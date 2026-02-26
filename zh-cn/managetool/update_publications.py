import os
import re
import time
import random
import requests
from scholarly import scholarly, MaxTriesExceededException
from pathlib import Path
from fake_useragent import UserAgent

# 配置请求头，模拟真实浏览器
ua = UserAgent()
HEADERS = {
    'User-Agent': ua.random,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# 配置代理（如果需要）
PROXIES = {
    # 'http': 'http://your_proxy:port',
    # 'https': 'https://your_proxy:port'
}

# ---------------------- 新增：网络环境检测功能 ----------------------
def check_baidu_access():
    """检查能否访问百度（国内常用网站）"""
    try:
        response = requests.get('https://www.baidu.com', timeout=5, headers=HEADERS)
        return response.status_code == 200
    except Exception:
        return False

def check_google_access():
    """检查能否访问谷歌（国外常用网站）"""
    try:
        response = requests.get('https://www.google.com', timeout=5, headers=HEADERS)
        return response.status_code == 200
    except Exception:
        return False

def check_ip_geolocation():
    """通过IP查询服务判断地理位置"""
    ip_services = [
        'https://ipapi.co/json/',
        'https://ip.cn/ipjson',
        'https://api.ipify.org?format=json'  # 这个只返回IP，需要额外处理
    ]
    
    for service in ip_services:
        try:
            response = requests.get(service, timeout=5, headers=HEADERS)
            data = response.json()
            
            if 'country' in data:
                return data['country'].lower() == 'china'
            elif 'country_name' in data:
                return data['country_name'].lower() == 'china'
            elif 'country_code' in data:
                return data['country_code'].lower() == 'cn'
            elif 'country_id' in data:  # ip.cn的返回格式
                return data['country_id'] == 'CN'
        except:
            continue
            
    return None  # 无法确定

def detect_network_environment():
    """综合判断网络环境是国内还是国外"""
    print("\n正在检测网络环境...")
    
    # 初始化评分
    domestic_score = 0
    foreign_score = 0
    
    # 百度访问测试
    baidu_access = check_baidu_access()
    print(f"百度访问测试: {'成功' if baidu_access else '失败'}")
    if baidu_access:
        domestic_score += 2
    
    # 谷歌访问测试
    google_access = check_google_access()
    print(f"谷歌访问测试: {'成功' if google_access else '失败'}")
    if google_access:
        foreign_score += 2
    else:
        domestic_score += 1  # 国内通常无法直接访问谷歌
    
    # IP地理位置测试
    ip_location = check_ip_geolocation()
    print(f"IP地理位置测试: {'中国' if ip_location is True else '国外' if ip_location is False else '无法确定'}")
    if ip_location is True:
        domestic_score += 3
    elif ip_location is False:
        foreign_score += 3
    
    # 综合判断
    print("\n网络环境检测结果:")
    if domestic_score > foreign_score:
        result = "国内"
        print("当前网络环境很可能在国内")
        print("提示：国内网络通常无法直接访问Google Scholar，建议使用代理服务")
    elif foreign_score > domestic_score:
        result = "国外"
        print("当前网络环境很可能在国外")
    else:
        result = "未知"
        print("无法准确判断网络环境")
    
    return result
# ---------------------- 网络环境检测功能结束 ----------------------

def set_scholarly_headers():
    """为scholarly设置自定义请求头"""
    scholarly._SESSION.headers.update(HEADERS)
    if PROXIES and any(PROXIES.values()):
        scholarly._SESSION.proxies.update(PROXIES)

def read_scholar_ids(file_path):
    """读取scholarid.txt文件中的所有Google Scholar ID，清理特殊字符"""
    if not os.path.exists(file_path):
        print(f"错误：文件 {file_path} 不存在")
        return []
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        ids = []
        for line in f:
            clean_id = line.strip().replace('\ufeff', '').replace('\u200b', '')
            if clean_id:
                ids.append(clean_id)
    
    return ids

def verify_scholar_id(scholar_id):
    """验证学者ID是否有效（通过直接访问URL）"""
    try:
        url = f"https://scholar.google.com/citations?user={scholar_id}&hl=en"
        response = requests.get(
            url, 
            headers=HEADERS, 
            proxies=PROXIES if any(PROXIES.values()) else None,
            timeout=10
        )
        
        # 检查页面是否包含学者信息特征
        if response.status_code == 200:
            return "Citations" in response.text and "Publications" in response.text
        return False
    except Exception as e:
        print(f"验证学者ID时出错: {str(e)}")
        return False

def get_all_scholar_papers(scholar_id, max_retries=5):
    """获取学者的所有文章，包含详细错误处理"""
    set_scholarly_headers()
    
    # 先验证学者ID是否有效
    if not verify_scholar_id(scholar_id):
        print(f"  学者ID {scholar_id} 无效或无法访问")
        return []
    
    for attempt in range(max_retries):
        try:
            delay = random.uniform(3, 8) + attempt * 2
            print(f"  等待 {delay:.2f} 秒后请求...")
            time.sleep(delay)
            
            print(f"  尝试获取学者 {scholar_id} 的信息 (尝试 {attempt+1}/{max_retries})...")
            
            # 搜索学者ID
            author = scholarly.search_author_id(scholar_id)
            if author is None:
                print(f"  未找到学者 {scholar_id} 的信息")
                return []
            
            print(f"  找到学者: {author.get('name', '未知')}")
            
            # 获取出版物信息
            author = scholarly.fill(author, sections=['basics', 'publications'])
            if author is None:
                print(f"  无法填充学者 {scholar_id} 的详细信息")
                return []
            
            publications = author.get('publications', [])
            print(f"  获取到 {len(publications)} 篇文章，开始填充详细信息...")
            
            filled_publications = []
            for i, pub in enumerate(publications):
                try:
                    if (i + 1) % 5 == 0 or i == len(publications) - 1:
                        print(f"    正在处理第 {i+1}/{len(publications)} 篇文章...")
                    
                    time.sleep(random.uniform(2, 5))
                    filled_pub = scholarly.fill(pub)
                    filled_publications.append(filled_pub)
                    
                except MaxTriesExceededException:
                    print(f"  填充文章 {i+1} 时达到最大尝试次数")
                    filled_publications.append(pub)
                except Exception as e:
                    print(f"  填充文章 {i+1} 时出错: {str(e)}，使用基础信息")
                    filled_publications.append(pub)
            
            print(f"  成功填充 {len(filled_publications)} 篇文章的详细信息")
            return filled_publications
        
        except MaxTriesExceededException:
            print(f"  获取学者 {scholar_id} 达到最大尝试次数，可能被Google限制")
            if attempt < max_retries - 1:
                wait_time = 60 * (attempt + 1)
                print(f"  等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        except AttributeError as e:
            # 专门处理NoneType错误
            print(f"  属性错误: {str(e)} - 可能是Google页面结构变化导致")
            if attempt < max_retries - 1:
                wait_time = 10 * (2 **attempt)
                print(f"  等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        except Exception as e:
            print(f"  获取学者 {scholar_id} 出错（尝试 {attempt + 1}/{max_retries}）：{str(e)}")
            if attempt < max_retries - 1:
                wait_time = 10 * (2** attempt)
                print(f"  等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
    return []

def extract_year_from_bib(bib):
    """从bib信息中提取年份"""
    if not bib:  # 增加空值检查
        return ""
        
    year = bib.get('year', '')
    if year:
        year_match = re.search(r'\b(19|20)\d{2}\b', str(year))
        if year_match:
            return year_match.group()
    
    pub_year = bib.get('pub_year', '')
    if pub_year:
        year_match = re.search(r'\b(19|20)\d{2}\b', str(pub_year))
        if year_match:
            return year_match.group()
    
    return ''

def clean_bibtex_value(value):
    """清理BibTeX值，确保格式正确"""
    if not value:
        return ""
    
    value = str(value)
    value = value.replace('\\', '\\\\')
    value = value.replace('{', '\\{').replace('}', '\\}')
    value = value.replace('"', '\\"')
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    value = value.replace('\n', ' ').replace('\r', ' ')
    value = re.sub(r'\s+', ' ', value).strip()
    
    return value

def generate_valid_bibtex_id(author, year, title):
    """生成有效的BibTeX ID"""
    if not author:
        author = "unknown"
    if not title:
        title = "untitled"
        
    first_author = author.split(' and ')[0] if ' and ' in author else author.split(',')[0]
    surname = first_author.split(',')[0] if ',' in first_author else first_author.split()[-1]
    surname_clean = re.sub(r'[^a-zA-Z]', '', surname)
    
    title_words = title.split()[:2]
    title_clean = ''.join([re.sub(r'[^a-zA-Z]', '', word) for word in title_words])
    
    bib_id = f"{surname_clean}{year}{title_clean}"
    bib_id = re.sub(r'[^a-zA-Z0-9_]', '', bib_id)
    
    if not bib_id:
        bib_id = f"entry{hash(title) % 10000}"
    
    return bib_id

def validate_year(year_str):
    """验证年份是否为纯数字"""
    if not year_str:
        return '0000'
    
    year_str = str(year_str)
    if year_str.isdigit():
        current_year = time.localtime().tm_year
        if 1900 <= int(year_str) <= current_year + 5:
            return year_str
        else:
            print(f"警告: 年份 {year_str} 不在合理范围内，使用0000代替")
            return '0000'
    else:
        print(f"警告: 年份 {year_str} 不是纯数字，使用0000代替")
        return '0000'

def format_bib_entry(pub):
    """将文章信息格式化为BibTeX格式"""
    if not pub:  # 增加空值检查
        return "", "", "", ""
        
    bib = pub.get('bib', {})
    entry = []
    
    title = clean_bibtex_value(bib.get('title', 'untitled'))
    author = clean_bibtex_value(bib.get('author', 'unknown'))
    raw_year = clean_bibtex_value(extract_year_from_bib(bib))
    year = validate_year(raw_year)
    
    bib_id = generate_valid_bibtex_id(author, year, title)
    entry.append(f"@article{{{bib_id},")
    
    field_mappings = [
        ('title', title),
        ('journal', clean_bibtex_value(
            bib.get('journal') or bib.get('publisher') or 
            bib.get('conference') or bib.get('venue')
        )),
        ('abbr', clean_bibtex_value(bib.get('abbr'))),
        ('volume', clean_bibtex_value(bib.get('volume'))),
        ('issue', clean_bibtex_value(bib.get('number') or bib.get('issue'))),
        ('pages', clean_bibtex_value(bib.get('pages'))),
        ('year', year),
        ('month', clean_bibtex_value(bib.get('month'))),
        ('author', author),
        ('publisher', clean_bibtex_value(bib.get('publisher'))),
        ('doi', clean_bibtex_value(bib.get('doi'))),
        ('html', clean_bibtex_value(pub.get('pub_url') or bib.get('url'))),
    ]
    
    for field_name, value in field_mappings:
        if value and value.strip():
            entry.append(f"  {field_name} = {{{value}}},")
    
    entry.append("}")
    return '\n'.join(entry), bib_id, title, year

def normalize_title(title):
    """标准化标题用于去重"""
    if not title:
        return ""
    title = title.lower()
    title = re.sub(r'[^\w\s]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def is_duplicate(existing_entries, new_entry_id, new_title):
    """检查文章是否重复"""
    if new_entry_id in existing_entries:
        return True
    
    normalized_new = normalize_title(new_title)
    if not normalized_new:
        return False
    
    for entry in existing_entries.values():
        existing_title = entry.get('title', '')
        normalized_existing = normalize_title(existing_title)
        if normalized_existing == normalized_new:
            return True
    
    return False

def test_google_scholar_access():
    """测试Google Scholar访问"""
    print("测试Google Scholar访问...")
    try:
        url = "https://scholar.google.com/"
        response = requests.get(
            url, 
            headers=HEADERS, 
            proxies=PROXIES if any(PROXIES.values()) else None,
            timeout=15
        )
        
        if response.status_code == 200:
            if "Google Scholar" in response.text and "Authors" in response.text:
                print("Google Scholar访问正常")
                return True
            else:
                print("Google Scholar页面内容异常，可能被限制")
                return False
        elif response.status_code == 429:
            print("访问被拒绝：请求过于频繁（429错误）")
            return False
        elif response.status_code in [403, 503]:
            print(f"访问被拒绝：{response.status_code}错误，可能IP被限制")
            return False
        else:
            print(f"Google Scholar访问失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"Google Scholar访问测试失败: {str(e)}")
        return False

def main():
    # 首先检测网络环境
    network_env = detect_network_environment()
    
    # 如果检测到国内网络环境，给出提示并确认是否继续
    if network_env == "国内":
        try:
            confirm = input("\n在国内网络环境下可能无法访问Google Scholar，是否继续? (y/n): ")
            if confirm.lower() not in ['y', 'yes']:
                print("用户选择退出程序")
                return
        except:
            print("\n输入确认失败，程序退出")
            return
    
    # 测试Google Scholar访问
    connection_ok = test_google_scholar_access()
    if not connection_ok:
        print("无法正常访问Google Scholar")
        if any(PROXIES.values()):
            print("尝试使用代理访问...")
            connection_ok = test_google_scholar_access()
        if not connection_ok:
            print("严重错误：无法访问Google Scholar，程序无法继续")
            return
    
    # 定义文件路径
    current_dir = os.getcwd()
    scholar_ids_path = os.path.join(current_dir, 'scholar', 'scholarid.txt')
    output_dir = os.path.join(os.path.dirname(current_dir), '_bibliography')
    output_file = os.path.join(output_dir, 'papers.bib')
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 读取学者ID
    scholar_ids = read_scholar_ids(scholar_ids_path)
    if not scholar_ids:
        print("没有找到有效的Google Scholar ID，程序退出")
        return
    print(f"已读取 {len(scholar_ids)} 个学者ID：{scholar_ids}")
    
    # 获取所有文章
    all_papers = []
    for scholar_id in scholar_ids:
        print(f"正在获取学者 {scholar_id} 的所有文章...")
        try:
            # 先手动检查学者页面是否可访问
            if not verify_scholar_id(scholar_id):
                print(f"学者 {scholar_id} 的页面无法访问，跳过")
                continue
                
            papers = get_all_scholar_papers(scholar_id)
            all_papers.extend(papers)
            print(f"已获取 {len(papers)} 篇文章")
        except Exception as e:
            print(f"获取学者 {scholar_id} 的文章时发生错误: {str(e)}，继续处理下一个学者")
        
        # 学者之间的延迟
        wait_time = random.uniform(60, 180)
        print(f"等待 {wait_time:.1f} 秒后处理下一个学者...")
        time.sleep(wait_time)
    
    # 处理文章，去重并格式化
    formatted_entries = {}
    success_count = 0
    for paper in all_papers:
        try:
            bib_entry, entry_id, title, year = format_bib_entry(paper)
            if not is_duplicate(formatted_entries, entry_id, title):
                formatted_entries[entry_id] = {
                    'bib_entry': bib_entry,
                    'title': title,
                    'year': year
                }
                success_count += 1
                print(f"成功处理文章: {title[:50]}... ({year})")
            else:
                print(f"跳过重复文章: {title[:50]}...")
        except Exception as e:
            print(f"处理文章时出错：{str(e)}，继续处理下一篇")
    
    print(f"成功处理 {success_count} 篇不重复的文章")
    
    # 按年份排序
    def sort_key(entry):
        try:
            return int(entry['year']) if entry['year'] and entry['year'].isdigit() else 0
        except (ValueError, TypeError):
            return 0
    
    sorted_entries = sorted(
        formatted_entries.values(),
        key=sort_key,
        reverse=True
    )
    
    # 写入文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, entry in enumerate(sorted_entries):
                f.write(entry['bib_entry'])
                if i != len(sorted_entries) - 1:
                    f.write('\n\n')
        
        print(f"已成功将 {len(sorted_entries)} 篇文章写入 {output_file}")
    except Exception as e:
        print(f"写入文件时出错: {str(e)}")

if __name__ == "__main__":
    main()
