import requests
import json
import time
import os
import re
from urllib.parse import quote
from typing import Dict, List, Optional, Tuple

# ================= 配置区域 (请修改这里) =================
# 1. 你的 ORCID API 凭证 (从开发者工具页面复制)
CLIENT_ID = os.getenv("ORCID_CLIENT_ID")
CLIENT_SECRET = os.getenv("ORCID_CLIENT_SECRET")

# 2. 你想抓取的多个目标学者 ORCID ID（列表形式，可添加多个）
TARGET_ORCID_IDS = [
    "0000-0003-4717-2814",
    "0000-0003-2075-366X"
]

# 3. 输出文件名（工作目录为项目根目录，路径正确）
OUTPUT_FILE = "./_bibliography/papers.bib"

# 4. 每个ORCID ID的抓取数量限制 (0表示无限制)
LIMIT_PER_ORCID = 0

# 5. 请求超时设置（秒）
TIMEOUT = 15

# 6. 请求间隔（秒），防止触发反爬限制
REQUEST_DELAY = 1
# =======================================================

# 日志颜色配置
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

# 全局DOI去重集合
processed_dois = set()
# 全局BibTeX条目列表
all_bib_entries = []

def load_existing_selected_dois() -> set:
    """加载现有BibTeX文件中包含selected = {true}的DOI集合"""
    selected_dois = set()
    if not os.path.exists(OUTPUT_FILE):
        print(f"{Colors.BLUE}📄 未找到现有BibTeX文件，无selected字段需要保留{Colors.RESET}")
        return selected_dois

    print(f"{Colors.BLUE}📄 正在读取现有BibTeX文件，保留selected = {{true}}的条目...{Colors.RESET}")
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            bib_content = f.read()

        # 正则匹配所有@article条目（兼容各种格式）
        article_pattern = re.compile(r'@article\{[^}]+\n(.*?)\n\}', re.DOTALL)
        entries = article_pattern.findall(bib_content)

        for entry_content in entries:
            # 提取DOI（兼容空格、大小写）
            doi_match = re.search(r'doi\s*=\s*\{([^}]+)\}', entry_content, re.IGNORECASE)
            # 提取selected字段（匹配true/TRUE/True）
            selected_match = re.search(r'selected\s*=\s*\{(true)\}', entry_content, re.IGNORECASE)

            if doi_match and selected_match:
                doi = doi_match.group(1).strip()
                # 清洗DOI格式（移除https://doi.org/前缀）
                clean_doi = doi.replace("https://doi.org/", "").strip()
                selected_dois.add(clean_doi)
                print(f"{Colors.GREEN}🔖 保留DOI {clean_doi} 的selected=true字段{Colors.RESET}")

    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  读取现有BibTeX文件失败: {str(e)}，将不会保留selected字段{Colors.RESET}")

    return selected_dois

def get_access_token() -> Optional[str]:
    """获取 Access Token (机器对机器模式)，带完善错误处理"""
    print(f"{Colors.BLUE}正在申请 Access Token...{Colors.RESET}")
    url = "https://orcid.org/oauth/token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "/read-public"
    }
    
    try:
        response = requests.post(
            url, 
            headers=headers, 
            data=data, 
            timeout=TIMEOUT,
            verify=True  # 验证SSL证书
        )
        response.raise_for_status()  # 抛出HTTP错误
        
        token_data = response.json()
        token = token_data.get("access_token")
        
        if not token:
            print(f"{Colors.RED}❌ 获取 Token 失败: 响应中无token字段{Colors.RESET}")
            return None
        
        print(f"{Colors.GREEN}✅ 成功获取 Token{Colors.RESET}")
        return token
        
    except requests.exceptions.Timeout:
        print(f"{Colors.RED}❌ 获取 Token 失败: 请求超时（{TIMEOUT}秒）{Colors.RESET}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"{Colors.RED}❌ 获取 Token 失败: HTTP错误 {e.response.status_code} - {e.response.text}{Colors.RESET}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}❌ 获取 Token 失败: 网络错误 {str(e)}{Colors.RESET}")
        return None
    except json.JSONDecodeError:
        print(f"{Colors.RED}❌ 获取 Token 失败: 响应不是有效JSON{Colors.RESET}")
        return None

def get_works_list(orcid_id: str, token: str) -> List[Tuple[str, str]]:
    """从单个ORCID ID获取文章DOI和标题列表，带错误处理"""
    print(f"\n{Colors.BLUE}===== 处理 ORCID ID: {orcid_id} ====={Colors.RESET}")
    print(f"{Colors.BLUE}正在获取用户 {orcid_id} 的文章列表...{Colors.RESET}")
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            url, 
            headers=headers, 
            timeout=TIMEOUT,
            verify=True
        )
        response.raise_for_status()
        
        data = response.json()
        dois = []
        groups = data.get('group', [])
        print(f"{Colors.BLUE}找到 {len(groups)} 个记录组，正在提取 DOI...{Colors.RESET}")

        for group in groups:
            # 取每个组里的第一个summary
            summaries = group.get('work-summary', [])
            if not summaries:
                continue
            
            summary = summaries[0]
            # 提取标题
            title = summary.get('title', {}).get('title', {}).get('value', 'Unknown Title')
            
            # 寻找 DOI
            external_ids = summary.get('external-ids', {}).get('external-id', [])
            found_doi = None
            for eid in external_ids:
                if eid.get('external-id-type') == 'doi':
                    found_doi = eid.get('external-id-value')
                    break
            
            if found_doi:
                # 清洗DOI格式
                clean_doi = found_doi.replace("https://doi.org/", "").strip()
                # 去重检查：仅添加未处理过的DOI
                if clean_doi not in processed_dois:
                    processed_dois.add(clean_doi)
                    dois.append((title, clean_doi))
                else:
                    print(f"{Colors.YELLOW}⚠️  跳过重复DOI: {clean_doi}{Colors.RESET}")
                
                # 达到数量限制则停止
                if LIMIT_PER_ORCID > 0 and len(dois) >= LIMIT_PER_ORCID:
                    break
        
        print(f"{Colors.GREEN}✅ ORCID {orcid_id} 提取到 {len(dois)} 个新DOI{Colors.RESET}")
        return dois
        
    except requests.exceptions.Timeout:
        print(f"{Colors.RED}❌ ORCID {orcid_id} 获取文章列表失败: 请求超时{Colors.RESET}")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"{Colors.RED}❌ ORCID {orcid_id} 获取文章列表失败: HTTP错误 {e.response.status_code}{Colors.RESET}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}❌ ORCID {orcid_id} 获取文章列表失败: 网络错误 {str(e)}{Colors.RESET}")
        return []
    except json.JSONDecodeError:
        print(f"{Colors.RED}❌ ORCID {orcid_id} 获取文章列表失败: 响应不是有效JSON{Colors.RESET}")
        return []
    except Exception as e:
        print(f"{Colors.RED}❌ ORCID {orcid_id} 获取文章列表失败: 未知错误 {str(e)}{Colors.RESET}")
        return []

def get_work_metadata(doi: str) -> Optional[Dict]:
    """通过DOI从Crossref获取完整的论文元数据，带错误处理"""
    try:
        # Crossref API (无API密钥也可使用)
        url = f"https://api.crossref.org/works/{quote(doi)}"
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(
            url, 
            headers=headers, 
            timeout=TIMEOUT,
            verify=True
        )
        response.raise_for_status()
        
        data = response.json().get('message', {})
        if not data:
            print(f"{Colors.YELLOW}⚠️  DOI {doi}: 无元数据返回{Colors.RESET}")
            return None
        
        # 提取核心元数据
        metadata = {
            # 基础信息
            "title": data.get('title', ['Unknown Title'])[0].strip(),
            "year": str(data.get('published-print', {}).get('date-parts', [[0]])[0][0]) or 
                    str(data.get('published-online', {}).get('date-parts', [[0]])[0][0]) or 
                    "Unknown Year",
            # 期刊信息
            "journal": data.get('container-title', ['Unknown Journal'])[0].strip(),
            "volume": data.get('volume', ''),
            "issue": data.get('issue', ''),
            "pages": data.get('page', ''),
            "publisher": data.get('publisher', ''),
            # 作者信息
            "authors": [],
            # DOI链接
            "doi": doi,
            "html_url": f"https://doi.org/{doi}"
        }
        
        # 处理作者（转换为 "Hua-Jie Jiang and Wei Fang and ..." 格式）
        authors = data.get('author', [])
        for author in authors:
            family = author.get('family', 'Unknown')
            given = author.get('given', '')
            if given:
                author_name = f"{given} {family}"
            else:
                author_name = family
            metadata["authors"].append(author_name)
        
        return metadata
        
    except requests.exceptions.Timeout:
        print(f"{Colors.YELLOW}⚠️  DOI {doi}: 请求超时，跳过{Colors.RESET}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"{Colors.YELLOW}⚠️  DOI {doi}: HTTP错误 {e.response.status_code}，跳过{Colors.RESET}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"{Colors.YELLOW}⚠️  DOI {doi}: 网络错误 {str(e)}，跳过{Colors.RESET}")
        return None
    except json.JSONDecodeError:
        print(f"{Colors.YELLOW}⚠️  DOI {doi}: 响应不是有效JSON，跳过{Colors.RESET}")
        return None
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  DOI {doi}: 处理失败 {str(e)}，跳过{Colors.RESET}")
        return None

def generate_bib_key(metadata: Dict) -> str:
    """生成BibTeX条目键：姓氏+年份+标题首字母（如Jiang2025UnlockingChiral）"""
    try:
        # 提取第一作者姓氏
        if metadata.get('authors'):
            first_author = metadata['authors'][0]
            # 提取姓氏（取最后一个单词）
            last_name = first_author.split()[-1].strip()
        else:
            last_name = "Unknown"
        
        # 提取年份
        year = metadata.get('year', '0000')
        if year == "Unknown Year":
            year = "0000"
        
        # 处理标题：移除特殊字符，转换为驼峰命名
        title = metadata.get('title', 'Unknown Title')
        # 移除特殊字符，只保留字母和数字
        clean_title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        # 转换为驼峰命名
        camel_title = ''.join(word.capitalize() for word in clean_title.split() if word)
        
        # 组合键
        bib_key = f"{last_name}{year}{camel_title[:30]}"  # 限制长度防止过长
        return bib_key.replace(' ', '')
        
    except Exception as e:
        # 生成备用键
        return f"Unknown{int(time.time())}"

def format_bib_entry(metadata: Dict, selected_dois: set) -> Optional[str]:
    """格式化BibTeX条目为指定格式，保留selected = {true}字段"""
    try:
        if not metadata:
            return None
        
        # 生成条目键
        bib_key = generate_bib_key(metadata)
        
        # 处理作者字符串
        author_str = " and ".join(metadata.get('authors', ['Unknown Author']))
        
        # 构建字段列表（只包含非空字段）
        fields = []
        
        # 标题（必选）
        fields.append(f"  title = {{{metadata['title']}}}")
        
        # 期刊（必选）
        journal = metadata.get('journal', 'Unknown Journal')
        fields.append(f"  journal = {{{journal}}}")
        
        # 期刊缩写（和journal一致）
        fields.append(f"  abbr = {{{journal}}}")
        
        # 卷（可选）
        if metadata.get('volume'):
            fields.append(f"  volume = {{{metadata['volume']}}}")
        
        # 期（可选）
        if metadata.get('issue'):
            fields.append(f"  issue = {{{metadata['issue']}}}")
        
        # 页码（可选）
        if metadata.get('pages'):
            fields.append(f"  pages = {{{metadata['pages']}}}")
        
        # 年份（必选）
        fields.append(f"  year = {{{metadata.get('year', '0000')}}}")
        
        # 作者（必选）
        fields.append(f"  author = {{{author_str}}}")
        
        # 出版商（可选）
        if metadata.get('publisher'):
            fields.append(f"  publisher = {{{metadata['publisher']}}}")
        
        # HTML链接（必选）
        fields.append(f"  html = {{{metadata.get('html_url', '')}}}")
        
        # 核心功能：保留selected = {true}字段
        doi = metadata.get('doi', '')
        if doi in selected_dois:
            fields.append(f"  selected = {{true}}")
            print(f"{Colors.BLUE}      📌 为DOI {doi} 保留selected = {{true}}字段{Colors.RESET}")
        
        # 拼接最终条目
        entry = f"@article{{{bib_key},\n"
        entry += ",\n".join(fields)
        entry += "\n}\n"
        
        return entry
        
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  格式化失败: {str(e)}{Colors.RESET}")
        return None

def process_single_orcid(orcid_id: str, token: str, selected_dois: set):
    """处理单个ORCID ID的完整流程"""
    # 获取该ORCID的DOI列表（自动去重）
    works = get_works_list(orcid_id, token)
    if not works:
        print(f"{Colors.YELLOW}⚠️  ORCID {orcid_id} 未获取到任何新DOI{Colors.RESET}")
        return
    
    # 处理每个DOI
    for i, (title, doi) in enumerate(works, 1):
        print(f"\n{Colors.BLUE}[{i}/{len(works)}] 处理 DOI: {doi}{Colors.RESET}")
        print(f"      标题: {title[:60]}...")
        
        # 获取元数据
        metadata = get_work_metadata(doi)
        if not metadata:
            print(f"{Colors.YELLOW}      ❌ 元数据获取失败，跳过{Colors.RESET}")
            continue
        
        # 格式化BibTeX条目（传入selected_dois保留字段）
        bib_entry = format_bib_entry(metadata, selected_dois)
        if not bib_entry:
            print(f"{Colors.YELLOW}      ❌ 条目格式化失败，跳过{Colors.RESET}")
            continue
        
        # 添加到全局列表
        all_bib_entries.append(bib_entry)
        print(f"{Colors.GREEN}      ✅ 成功生成BibTeX条目{Colors.RESET}")
        
        # 礼貌性延时
        time.sleep(REQUEST_DELAY)

def main():
    """主函数：批量处理多个ORCID ID，去重后生成最终文件"""
    print(f"{Colors.BLUE}===== 多ORCID ID 论文爬取工具（自动去重+保留selected字段版） ====={Colors.RESET}")
    print(f"{Colors.BLUE}待处理ORCID ID数量: {len(TARGET_ORCID_IDS)}{Colors.RESET}")
    
    # 第一步：加载现有文件中标记为selected=true的DOI
    selected_dois = load_existing_selected_dois()
    
    # 第二步：获取Token
    token = get_access_token()
    if not token:
        print(f"{Colors.RED}❌ 无法获取Token，程序退出{Colors.RESET}")
        return
    
    # 第三步：批量处理每个ORCID ID（传入selected_dois）
    for orcid_id in TARGET_ORCID_IDS:
        process_single_orcid(orcid_id, token, selected_dois)
    
    # 第四步：写入最终文件（所有ID的去重结果）
    if all_bib_entries:
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(OUTPUT_FILE)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("\n\n".join(all_bib_entries))
            
            print(f"\n{Colors.GREEN}🎉 批量处理完成！{Colors.RESET}")
            print(f"{Colors.GREEN}✅ 共生成 {len(all_bib_entries)} 个去重后的BibTeX条目{Colors.RESET}")
            print(f"{Colors.GREEN}✅ 已写入文件: {os.path.abspath(OUTPUT_FILE)}{Colors.RESET}")
            
        except Exception as e:
            print(f"{Colors.RED}❌ 写入文件失败: {str(e)}{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  未生成任何BibTeX条目{Colors.RESET}")
    
    print(f"\n{Colors.BLUE}===== 爬取完成 ====={Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  用户中断程序{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ 程序异常退出: {str(e)}{Colors.RESET}")