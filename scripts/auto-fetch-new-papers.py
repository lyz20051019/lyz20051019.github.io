import requests
import csv
import os
import re
import time
from datetime import datetime
from urllib.parse import quote
from typing import Optional, Dict, List

# ================= 配置区域 =================
CLIENT_ID = os.getenv("ORCID_CLIENT_ID")
CLIENT_SECRET = os.getenv("ORCID_CLIENT_SECRET")
ORCID_CSV = "./scripts/orcids.csv"
NEWS_CSV = "./scripts/news.csv"
TIMEOUT = 15
REQUEST_DELAY = 1
# ============================================

# 全局存储
orcid_info_map: Dict[str, Dict[str, str]] = {}
# 加载已存在的news.csv数据（保留首次时间+DOI去重）
existing_news: Dict[str, Dict] = {}
new_entries: List[Dict] = []

class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

# -----------------------------------------------------------------------------
# 【修复1】读取已存在的news.csv（保留首次时间）
# -----------------------------------------------------------------------------
def load_existing_news():
    if not os.path.exists(NEWS_CSV):
        return
    try:
        with open(NEWS_CSV, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                doi = row["doi"].strip().lower()
                existing_news[doi] = row
        print(f"{Colors.GREEN}✅ 加载已存在新闻：{len(existing_news)} 条{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️ 无历史新闻文件：{e}{Colors.RESET}")

# -----------------------------------------------------------------------------
# 【修复2】强制正确读取 ORCID/姓名（兼容所有CSV格式）
# -----------------------------------------------------------------------------
def load_orcid_authors():
    if not os.path.exists(ORCID_CSV):
        print(f"{Colors.RED}❌ 未找到 {ORCID_CSV}{Colors.RESET}")
        return False
    
    # 强制使用正确列名读取
    required_cols = ["orcid", "name", "en_name"]
    with open(ORCID_CSV, "r", encoding="utf-8") as f:
        content = f.read().replace('\0', '')  # 清理空字符
        reader = csv.DictReader(content.splitlines())
        
        # 校验列名
        if not all(col in reader.fieldnames for col in required_cols):
            print(f"{Colors.RED}❌ CSV必须包含列：orcid, name, en_name{Colors.RESET}")
            return False

        for row in reader:
            orcid = row["orcid"].strip()
            name = row["name"].strip()
            en_name = row["en_name"].strip()
            if orcid:
                orcid_info_map[orcid] = {"name": name, "en_name": en_name}
    
    print(f"{Colors.GREEN}✅ 加载作者信息：{len(orcid_info_map)} 个{Colors.RESET}")
    return True

# -----------------------------------------------------------------------------
# ORCID API + CrossRef（不变）
# -----------------------------------------------------------------------------
def get_access_token() -> Optional[str]:
    url = "https://orcid.org/oauth/token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials", "scope": "/read-public"
    }
    try:
        r = requests.post(url, headers=headers, data=data, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()["access_token"]
    except:
        return None

def get_orcid_dois(orcid: str, token: str) -> List[str]:
    url = f"https://pub.orcid.org/v3.0/{orcid}/works"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    dois = []
    try:
        data = requests.get(url, headers=headers, timeout=TIMEOUT).json()
        for g in data.get("group", []):
            ws = g.get("work-summary", [])
            if not ws: continue
            for ext in ws[0].get("external-ids", {}).get("external-id", []):
                if ext["external-id-type"] == "doi":
                    doi = re.sub(r"^https?://doi\.org/", "", ext["external-id-value"]).lower()
                    dois.append(doi)
                    break
        return list(set(dois))
    except:
        return []

def get_paper_info(doi):
    try:
        url = f"https://api.crossref.org/works/{quote(doi)}"
        data = requests.get(url, timeout=10).json()["message"]
        return data.get("title", ["未知标题"])[0], data.get("container-title", ["未知期刊"])[0]
    except:
        return "未知标题", "未知期刊"

# -----------------------------------------------------------------------------
# 【修复3】合并作者 + 保留首次时间
# -----------------------------------------------------------------------------
def process_article(orcid, doi, name, en_name):
    # DOI已存在：仅合并作者，不修改时间
    if doi in existing_news:
        row = existing_news[doi]
        # 中文姓名去重合并
        if name and name not in row["name"]:
            row["name"] = f"{row['name']},{name}" if row["name"] else name
        # 英文姓名去重合并
        if en_name and en_name not in row["en_name"]:
            row["en_name"] = f"{row['en_name']},{en_name}" if row["en_name"] else en_name
        existing_news[doi] = row
        print(f"{Colors.YELLOW}⚠️ 合并作者：{doi}{Colors.RESET}")
        return

    # DOI新文章：新建记录，保存当前时间
    fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title, journal = get_paper_info(doi)
    existing_news[doi] = {
        "fetch_time": fetch_time, "orcid_id": orcid, "doi": doi,
        "title": title, "journal": journal, "name": name, "en_name": en_name
    }
    print(f"{Colors.GREEN}✅ 新增：{title[:40]}{Colors.RESET}")

# -----------------------------------------------------------------------------
# 【修复4】仅在数据变化时写入文件（触发git提交）
# -----------------------------------------------------------------------------
def save_news():
    # 写入文件
    with open(NEWS_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["fetch_time","orcid_id","doi","title","journal","name","en_name"])
        writer.writeheader()
        writer.writerows(existing_news.values())
    print(f"{Colors.GREEN}🎉 保存成功：{len(existing_news)} 条新闻{Colors.RESET}")

# -----------------------------------------------------------------------------
# 主流程
# -----------------------------------------------------------------------------
def main():
    print(f"{Colors.BLUE}=== ORCID 新闻自动更新工具 ==={Colors.RESET}")
    load_existing_news()
    if not load_orcid_authors(): return

    token = get_access_token()
    if not token: return

    for orcid, info in orcid_info_map.items():
        name, en_name = info["name"], info["en_name"]
        print(f"\n{Colors.BLUE}处理：{orcid} | {name} / {en_name}{Colors.RESET}")
        dois = get_orcid_dois(orcid, token)
        for doi in dois:
            process_article(orcid, doi, name, en_name)
            time.sleep(REQUEST_DELAY)

    save_news()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n中断")