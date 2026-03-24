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
# 全局BibTeX条目列表（爬取下来的所有）
all_bib_entries = []
# 来自 papers_google.bib 的所有 DOI（用于最后去重）
google_dois = set()
# papers_google.bib 完整内容
google_bib_content = ""

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

        article_pattern = re.compile(r'@article\{[^}]+\n(.*?)\n\}', re.DOTALL)
        entries = article_pattern.findall(bib_content)

        for entry_content in entries:
            doi_match = re.search(r'doi\s*=\s*\{([^}]+)\}', entry_content, re.IGNORECASE)
            selected_match = re.search(r'selected\s*=\s*\{(true)\}', entry_content, re.IGNORECASE)

            if doi_match and selected_match:
                doi = doi_match.group(1).strip()
                clean_doi = doi.replace("https://doi.org/", "").strip()
                selected_dois.add(clean_doi)
                print(f"{Colors.GREEN}🔖 保留DOI {clean_doi} 的selected=true字段{Colors.RESET}")

    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  读取现有BibTeX文件失败: {str(e)}，将不会保留selected字段{Colors.RESET}")

    return selected_dois

def load_google_bib_info():
    """加载 papers_google.bib 的所有DOI 和 完整内容"""
    global google_dois, google_bib_content
    google_path = os.path.join(os.path.dirname(OUTPUT_FILE), "papers_google.bib")

    if not os.path.exists(google_path):
        print(f"{Colors.YELLOW}⚠️  未找到 papers_google.bib{Colors.RESET}")
        return

    try:
        with open(google_path, "r", encoding="utf-8") as f:
            google_bib_content = f.read()

        doi_pattern = re.compile(r'doi\s*=\s*\{([^}]+)\}', re.IGNORECASE)
        found_dois = doi_pattern.findall(google_bib_content)

        for doi in found_dois:
            clean_doi = doi.replace("https://doi.org/", "").strip()
            google_dois.add(clean_doi)

        print(f"{Colors.GREEN}✅ 读取 papers_google.bib 完成，共 {len(google_dois)} 条文献{Colors.RESET}")
    except:
        print(f"{Colors.RED}❌ 读取 papers_google.bib 失败{Colors.RESET}")

def extract_doi_from_entry(entry: str) -> Optional[str]:
    """从一条 BibTeX 条目中提取 DOI"""
    match = re.search(r'doi\s*=\s*\{([^}]+)\}', entry, re.IGNORECASE)
    if match:
        return match.group(1).replace("https://doi.org/", "").strip()
    return None

def get_access_token() -> Optional[str]:
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
        response = requests.post(url, headers=headers, data=data, timeout=TIMEOUT, verify=True)
        response.raise_for_status()
        token_data = response.json()
        token = token_data.get("access_token")
        if not token:
            print(f"{Colors.RED}❌ 获取 Token 失败{Colors.RESET}")
            return None
        print(f"{Colors.GREEN}✅ 成功获取 Token{Colors.RESET}")
        return token
    except:
        print(f"{Colors.RED}❌ 获取 Token 失败{Colors.RESET}")
        return None

def get_works_list(orcid_id: str, token: str) -> List[Tuple[str, str]]:
    print(f"\n{Colors.BLUE}===== 处理 ORCID: {orcid_id} ====={Colors.RESET}")
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT, verify=True)
        response.raise_for_status()
        data = response.json()
        dois = []
        groups = data.get('group', [])

        for group in groups:
            summaries = group.get('work-summary', [])
            if not summaries: continue
            summary = summaries[0]
            title = summary.get('title', {}).get('title', {}).get('value', 'No Title')

            found_doi = None
            external_ids = summary.get('external-ids', {}).get('external-id', [])
            for eid in external_ids:
                if eid.get('external-id-type') == 'doi':
                    found_doi = eid.get('external-id-value')
                    break

            if found_doi:
                clean_doi = found_doi.replace("https://doi.org/", "").strip()
                if clean_doi not in processed_dois:
                    processed_dois.add(clean_doi)
                    dois.append((title, clean_doi))

                if LIMIT_PER_ORCID > 0 and len(dois) >= LIMIT_PER_ORCID:
                    break

        print(f"{Colors.GREEN}✅ 提取到 {len(dois)} 篇文献{Colors.RESET}")
        return dois
    except:
        print(f"{Colors.RED}❌ 获取文献失败{Colors.RESET}")
        return []

def get_work_metadata(doi: str) -> Optional[Dict]:
    try:
        url = f"https://api.crossref.org/works/{quote(doi)}"
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json().get('message', {})

        metadata = {
            "title": data.get('title', ['No Title'])[0].strip(),
            "year": str(data.get('published-print', {}).get('date-parts', [[0]])[0][0]) or
                    str(data.get('published-online', {}).get('date-parts', [[0]])[0][0]) or "Unknown",
            "journal": data.get('container-title', ['Unknown Journal'])[0].strip(),
            "volume": data.get('volume', ''),
            "issue": data.get('issue', ''),
            "pages": data.get('page', ''),
            "publisher": data.get('publisher', ''),
            "authors": [],
            "doi": doi,
            "html_url": f"https://doi.org/{doi}"
        }

        for author in data.get('author', []):
            family = author.get('family', '')
            given = author.get('given', '')
            metadata["authors"].append(f"{given} {family}".strip())

        return metadata
    except:
        return None

def generate_bib_key(metadata):
    try:
        last_name = metadata['authors'][0].split()[-1] if metadata.get('authors') else "Unknown"
        year = metadata.get('year', '0000')
        title = re.sub(r'[^a-zA-Z0-9\s]', '', metadata.get('title', ''))
        camel = ''.join([w.capitalize() for w in title.split()])
        return f"{last_name}{year}{camel[:30]}"
    except:
        return f"Unknown{int(time.time())}"

def format_bib_entry(metadata, selected_dois):
    if not metadata: return None
    key = generate_bib_key(metadata)
    authors = " and ".join(metadata.get('authors', ['Unknown']))
    fields = [
        f"  title = {{{metadata['title']}}}",
        f"  journal = {{{metadata['journal']}}}",
        f"  abbr = {{{metadata['journal']}}}",
    ]
    if metadata.get('volume'): fields.append(f"  volume = {{{metadata['volume']}}}")
    if metadata.get('issue'): fields.append(f"  issue = {{{metadata['issue']}}}")
    if metadata.get('pages'): fields.append(f"  pages = {{{metadata['pages']}}}")
    fields.append(f"  year = {{{metadata['year']}}}")
    fields.append(f"  author = {{{authors}}}")
    if metadata.get('publisher'): fields.append(f"  publisher = {{{metadata['publisher']}}}")
    fields.append(f"  html = {{{metadata['html_url']}}}")
    if metadata['doi'] in selected_dois:
        fields.append(f"  selected = {{true}}")
        print(f"{Colors.BLUE}      📌 保留 selected = true{Colors.RESET}")
    return f"@article{{{key},\n" + ",\n".join(fields) + "\n}\n"

def process_single_orcid(orcid_id, token, selected_dois):
    works = get_works_list(orcid_id, token)
    for idx, (title, doi) in enumerate(works, 1):
        print(f"\n[{idx}/{len(works)}] {doi}")
        meta = get_work_metadata(doi)
        if not meta:
            print(f"{Colors.YELLOW}⚠️  跳过{Colors.RESET}")
            continue
        entry = format_bib_entry(meta, selected_dois)
        if entry:
            all_bib_entries.append(entry)
        time.sleep(REQUEST_DELAY)

def main():
    print(f"{Colors.BLUE}===== ORCID 文献抓取（先爬取→后去重→再追加） ====={Colors.RESET}")
    selected_dois = load_existing_selected_dois()
    load_google_bib_info()

    token = get_access_token()
    if not token: return

    # ========== 第一步：先完整爬取所有 ORCID 文献 ==========
    for orcid in TARGET_ORCID_IDS:
        process_single_orcid(orcid, token, selected_dois)

    # ========== 第二步：比对 google，删除重复 ==========
    print(f"\n{Colors.BLUE}🔍 开始去重：删除与 papers_google.bib 重复的文献{Colors.RESET}")
    final_entries = []
    for entry in all_bib_entries:
        doi = extract_doi_from_entry(entry)
        if doi and doi in google_dois:
            print(f"{Colors.YELLOW}🚫 重复已删除: {doi}{Colors.RESET}")
        else:
            final_entries.append(entry)

    # ========== 第三步：写入最终文件：新文献 + google 文献 ==========
    output_dir = os.path.dirname(OUTPUT_FILE)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    final_text = "\n\n".join(final_entries)
    if google_bib_content.strip():
        final_text += "\n\n" + google_bib_content

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"\n{Colors.GREEN}🎉 全部完成！{Colors.RESET}")
    print(f"{Colors.GREEN}✅ ORCID 新文献：{len(final_entries)} 条{Colors.RESET}")
    print(f"{Colors.GREEN}✅ 已追加 papers_google.bib{Colors.RESET}")
    print(f"{Colors.GREEN}✅ 保存到：{OUTPUT_FILE}{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  手动中断{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ 错误：{e}{Colors.RESET}")