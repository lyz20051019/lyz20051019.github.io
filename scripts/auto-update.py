import requests
import json
import time
import os
import re
from urllib.parse import quote
from typing import Dict, List, Optional, Tuple

# ================= 配置区域 =================
CLIENT_ID = os.getenv("ORCID_CLIENT_ID")
CLIENT_SECRET = os.getenv("ORCID_CLIENT_SECRET")
TARGET_ORCID_IDS = [
    "0000-0003-4717-2814",
    "0000-0003-2075-366X"
]
OUTPUT_FILE = "./_bibliography/papers.bib"
LIMIT_PER_ORCID = 0
TIMEOUT = 15
REQUEST_DELAY = 1
# ============================================

class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

all_bib_entries = []

# 存储 papers_google.bib 里的去重依据
google_dois = set()
google_clean_titles = set()
google_bib_content = ""

# -----------------------------------------------------------------------------
# 1. 读取原有 selected = {true} 的 DOI
# -----------------------------------------------------------------------------
def load_existing_selected_dois() -> set:
    selected_dois = set()
    if not os.path.exists(OUTPUT_FILE):
        return selected_dois
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            text = f.read()
        pattern = re.compile(r'@article\{.*?\}', re.DOTALL)
        for entry in pattern.findall(text):
            doi_match = re.search(r'doi\s*=\s*\{([^}]+)\}', entry, re.I)
            sel_match = re.search(r'selected\s*=\s*\{true\}', entry, re.I)
            if doi_match and sel_match:
                doi = doi_match.group(1).strip()
                doi = re.sub(r'https?://doi\.org/', '', doi, flags=re.I)
                selected_dois.add(doi)
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️ 读取 selected 失败：{e}{Colors.RESET}")
    return selected_dois

# -----------------------------------------------------------------------------
# 2. 加载 papers_google.bib，提取 完整 DOI + 标题
# -----------------------------------------------------------------------------
def load_google_bib():
    global google_bib_content, google_dois, google_clean_titles
    g_path = os.path.join(os.path.dirname(OUTPUT_FILE), "papers_google.bib")
    if not os.path.exists(g_path):
        print(f"{Colors.YELLOW}⚠️ 未找到 papers_google.bib{Colors.RESET}")
        return

    with open(g_path, "r", encoding="utf-8") as f:
        google_bib_content = f.read()

    entry_pattern = re.compile(r'@article\{.*?\}', re.DOTALL)
    entries = entry_pattern.findall(google_bib_content)

    doi_pattern = re.compile(r'doi\.org/([0-9]+\.[0-9]+/[^/]+)', re.I)

    for e in entries:
        # 从 html 提取 完整 DOI
        html_match = re.search(r'html\s*=\s*\{([^}]+)\}', e, re.I)
        doi = None
        if html_match:
            url = html_match.group(1).strip()
            dm = doi_pattern.search(url)
            if dm:
                doi = dm.group(1)

        # 从 doi 字段兜底
        if not doi:
            df_match = re.search(r'doi\s*=\s*\{([^}]+)\}', e, re.I)
            if df_match:
                doi_val = df_match.group(1).strip()
                dm = doi_pattern.search(f"https://doi.org/{doi_val}")
                if dm:
                    doi = dm.group(1)

        if doi:
            google_dois.add(doi)

        # 清洗标题
        title_match = re.search(r'title\s*=\s*\{(.*?)\}', e, re.I | re.DOTALL)
        if title_match:
            t = title_match.group(1).lower()
            t = re.sub(r'<[^>]+>', '', t)
            t = re.sub(r'[^a-z0-9]', '', t)
            google_clean_titles.add(t)

    print(f"{Colors.GREEN}✅ 加载 papers_google.bib：{len(google_dois)} 个完整 DOI，{len(google_clean_titles)} 个标题{Colors.RESET}")

# -----------------------------------------------------------------------------
# 3. 从一条 bib 条目里提取 完整 DOI + 清洗标题
# -----------------------------------------------------------------------------
def extract_doi_and_clean_title(entry):
    doi_pattern = re.compile(r'doi\.org/([0-9]+\.[0-9]+/[^/]+)', re.I)

    # 完整 DOI
    doi = None
    html = re.search(r'html\s*=\s*\{([^}]+)\}', entry, re.I)
    if html:
        m = doi_pattern.search(html.group(1))
        if m:
            doi = m.group(1)

    # 标题（去掉斜体标签再清洗）
    title = ""
    t_match = re.search(r'title\s*=\s*\{(.*?)\}', entry, re.I | re.DOTALL)
    if t_match:
        title = t_match.group(1).lower()
        title = re.sub(r'<[^>]+>', '', title)
        title = re.sub(r'[^a-z0-9]', '', title)

    return doi, title

# -----------------------------------------------------------------------------
# 4. ORCID 相关抓取
# -----------------------------------------------------------------------------
def get_access_token() -> Optional[str]:
    url = "https://orcid.org/oauth/token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "/read-public"
    }
    try:
        r = requests.post(url, headers=headers, data=data, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()["access_token"]
    except Exception as e:
        print(f"{Colors.RED}❌ Token 获取失败：{e}{Colors.RESET}")
        return None

def get_works(orcid, token):
    url = f"https://pub.orcid.org/v3.0/{orcid}/works"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, headers=headers, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        res = []
        for g in data.get("group", []):
            ws = g.get("work-summary", [])
            if not ws: continue
            w = ws[0]
            title = w.get("title", {}).get("title", {}).get("value", "")
            doi = None
            for eid in w.get("external-ids", {}).get("external-id", []):
                if eid.get("external-id-type") == "doi":
                    doi = eid.get("external-id-value")
                    break
            if doi:
                doi = re.sub(r'https?://doi\.org/', '', doi, flags=re.I)
                res.append((title, doi))
        return res
    except Exception as e:
        print(f"{Colors.RED}❌ ORCID 读取失败：{e}{Colors.RESET}")
        return []

def crossref_meta(doi):
    try:
        url = f"https://api.crossref.org/works/{quote(doi)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        m = r.json()["message"]
        authors = []
        for a in m.get("author", []):
            given = a.get("given", "")
            family = a.get("family", "")
            authors.append(f"{given} {family}".strip())
        year = "0"
        if m.get("published-print"):
            year = str(m["published-print"]["date-parts"][0][0])
        elif m.get("published-online"):
            year = str(m["published-online"]["date-parts"][0][0])
        return {
            "title": m.get("title", [""])[0],
            "year": year,
            "journal": m.get("container-title", [""])[0],
            "volume": m.get("volume", ""),
            "issue": m.get("issue", ""),
            "pages": m.get("page", ""),
            "publisher": m.get("publisher", ""),
            "authors": authors,
            "doi": doi,
            "html": f"https://doi.org/{doi}"
        }
    except Exception:
        return None

def make_bibkey(meta):
    try:
        last = meta["authors"][0].split()[-1] if meta.get("authors") else "Anon"
        year = meta.get("year", "0000")
        t = re.sub(r'[^A-Za-z]', '', meta.get("title", ""))[:20]
        return f"{last}{year}{t}"
    except:
        return f"Auto{int(time.time())}"

def format_entry(meta, selected_dois):
    if not meta: return None
    key = make_bibkey(meta)
    authors = " and ".join(meta.get("authors", ["Anonymous"]))
    lines = [
        f"  title = {{{meta['title']}}}",
        f"  journal = {{{meta['journal']}}}",
        f"  abbr = {{{meta['journal']}}}",
    ]
    if meta.get("volume"): lines.append(f"  volume = {{{meta['volume']}}}")
    if meta.get("issue"): lines.append(f"  issue = {{{meta['issue']}}}")
    if meta.get("pages"): lines.append(f"  pages = {{{meta['pages']}}}")
    lines.append(f"  year = {{{meta['year']}}}")
    lines.append(f"  author = {{{authors}}}")
    if meta.get("publisher"): lines.append(f"  publisher = {{{meta['publisher']}}}")
    lines.append(f"  html = {{{meta['html']}}}")
    if meta["doi"] in selected_dois:
        lines.append(f"  selected = {{true}}")
    return f"@article{{{key},\n" + ",\n".join(lines) + "\n}\n"

# -----------------------------------------------------------------------------
# 主流程
# -----------------------------------------------------------------------------
def main():
    print(f"{Colors.BLUE}=== ORCID 抓取 → 双重去重(完整DOI+标题) → 追加 google ==={Colors.RESET}")
    selected_dois = load_existing_selected_dois()
    load_google_bib()

    token = get_access_token()
    if not token: return

    # 1. 先全部爬完
    for oid in TARGET_ORCID_IDS:
        print(f"\n{Colors.BLUE}== 处理 ORCID: {oid}{Colors.RESET}")
        works = get_works(oid, token)
        for i, (title, doi) in enumerate(works, 1):
            print(f"[{i}/{len(works)}] {title[:50]}...")
            meta = crossref_meta(doi)
            if meta:
                entry = format_entry(meta, selected_dois)
                if entry:
                    all_bib_entries.append(entry)
            time.sleep(REQUEST_DELAY)

    # 2. 真正的双重去重：完整DOI 或 标题重复才删
    final = []
    for e in all_bib_entries:
        doi, clean_title = extract_doi_and_clean_title(e)
        dup = False

        if doi and doi in google_dois:
            dup = True
        elif clean_title and clean_title in google_clean_titles:
            dup = True

        if dup:
            show = doi if doi else clean_title[:40]
            print(f"{Colors.YELLOW}🚫 去重：{show}{Colors.RESET}")
        else:
            final.append(e)

    # 3. 写入
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    out = "\n\n".join(final)
    if google_bib_content.strip():
        out += "\n\n" + google_bib_content

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(out)

    print(f"\n{Colors.GREEN}🎉 完成！保留 {len(final)} 篇新文献 + 追加 papers_google.bib{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ 中断{Colors.RESET}")