import requests
import csv
import os
import re
import time
from datetime import datetime
from urllib.parse import quote
from typing import Optional, Dict, List

# ===================== 核心配置 =====================
BASE_DIR = os.getcwd()
ORCID_CSV = os.path.join(BASE_DIR, "scripts", "orcids.csv")
NEWS_CSV = os.path.join(BASE_DIR, "scripts", "news.csv")
# 🔥 完整版预印本/无效DOI黑名单（彻底过滤）
FILTER_DOI_PREFIX = [
    "10.21203",    # ResearchSquare 预印本（你多的那篇就是这个）
    "10.26434",    # ChemRxiv
    "10.31219",    
    "10.3389",
    "10.12688"
]
TIMEOUT = 15
REQUEST_DELAY = 0.5
# ====================================================

orcid_authors = {}
unique_papers: Dict[str, dict] = {}

class Log:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

# 读取作者信息（无修改）
def load_authors():
    if not os.path.exists(ORCID_CSV):
        print(f"{Log.RED}❌ 未找到文件：{ORCID_CSV}{Log.RESET}")
        return False
    try:
        with open(ORCID_CSV, "r", encoding="utf-8-sig") as f:
            lines = [line.strip() for line in f if line.strip()]
        headers = [col.strip() for col in lines[0].split(",")]
        for line in lines[1:]:
            values = [v.strip() for v in line.split(",")]
            row = dict(zip(headers, values))
            orcid = row.get("orcid", "")
            if orcid:
                orcid_authors[orcid] = {
                    "name": row.get("name", ""),
                    "en_name": row.get("en_name", "")
                }
        print(f"{Log.GREEN}✅ 加载 {len(orcid_authors)} 位作者{Log.RESET}")
        return True
    except Exception as e:
        print(f"{Log.RED}❌ 读取作者失败：{str(e)}{Log.RESET}")
        return False

# 读取已有news.csv（无修改）
def load_existing():
    if not os.path.exists(NEWS_CSV):
        print(f"{Log.YELLOW}⚠️ 新建 news.csv{Log.RESET}")
        return
    try:
        with open(NEWS_CSV, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                doi = row["doi"].strip().lower()
                unique_papers[doi] = row
        print(f"{Log.GREEN}✅ 加载已有论文：{len(unique_papers)} 篇{Log.RESET}")
    except:
        pass

# 清洗+过滤DOI（无修改，更严格）
def clean_doi(raw_doi: str) -> Optional[str]:
    if not raw_doi:
        return None
    doi = re.sub(r"^https?://doi\.org/", "", raw_doi.strip().lower())
    for prefix in FILTER_DOI_PREFIX:
        if doi.startswith(prefix):
            return None
    if len(doi) < 8:
        return None
    return doi

# 从ORCID抓取DOI（无修改）
def fetch_orcid_dois(orcid: str) -> List[str]:
    url = f"https://pub.orcid.org/v3.0/{orcid}/works"
    headers = {"Accept": "application/json"}
    doi_set = set()

    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        data = resp.json()
        for group in data.get("group", []):
            for work in group.get("work-summary", []):
                for ext in work.get("external-ids", {}).get("external-id", []):
                    if ext.get("external-id-type") == "doi":
                        cleaned = clean_doi(ext.get("external-id-value", ""))
                        if cleaned:
                            doi_set.add(cleaned)
                work_url = work.get("url", {}).get("value", "")
                match = re.search(r"doi\.org/([0-9a-z\./-]+)", work_url, re.I)
                if match:
                    cleaned = clean_doi(match.group(1))
                    if cleaned:
                        doi_set.add(cleaned)
        res = sorted(list(doi_set))
        print(f"{Log.BLUE}🔍 {orcid} 有效论文：{len(res)} 篇{Log.RESET}")
        return res
    except Exception as e:
        print(f"{Log.RED}❌ 抓取失败：{str(e)}{Log.RESET}")
        return []

# ===================== 核心修复 =====================
# 🔥 新增：只保留【正式期刊文章】，过滤所有非期刊文献
def get_paper(doi: str):
    try:
        url = f"https://api.crossref.org/works/{quote(doi)}"
        msg = requests.get(url, timeout=TIMEOUT).json()["message"]
        
        # ✅ 强制只保留期刊文章（彻底解决多抓问题）
        if msg.get("type") != "journal-article":
            return None, None
            
        title = msg.get("title", ["未知标题"])[0]
        journal = msg.get("container-title", ["未知期刊"])[0]
        title = re.sub(r"<[^>]+>", "", title)
        journal = re.sub(r"<[^>]+>", "", journal)
        return title, journal
    except:
        return None, None

# 处理单篇论文（修复：过滤无效论文）
def process_paper(orcid: str, doi: str):
    author = orcid_authors[orcid]
    name, en_name = author["name"], author["en_name"]

    if doi in unique_papers:
        row = unique_papers[doi]
        if name and name not in row["name"]:
            row["name"] = f"{row['name']},{name}" if row["name"] else name
        if en_name and en_name not in row["en_name"]:
            row["en_name"] = f"{row['en_name']},{en_name}" if row["en_name"] else en_name
        unique_papers[doi] = row
        return

    # ✅ 无效论文直接跳过
    title, journal = get_paper(doi)
    if not title or not journal:
        return

    fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    unique_papers[doi] = {
        "fetch_time": fetch_time,
        "orcid_id": orcid,
        "doi": doi,
        "title": title,
        "journal": journal,
        "name": name,
        "en_name": en_name
    }

# 保存文件（无修改）
def save_csv():
    os.makedirs(os.path.dirname(NEWS_CSV), exist_ok=True)
    fields = ["fetch_time", "orcid_id", "doi", "title", "journal", "name", "en_name"]
    with open(NEWS_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(unique_papers.values())
    print(f"\n{Log.GREEN}🎉 最终有效论文：{len(unique_papers)} 篇{Log.RESET}")
    print(f"{Log.GREEN}✅ 文件已保存：scripts/news.csv{Log.RESET}")

# 主流程（无修改）
def main():
    print(f"{Log.BLUE}===== ORCID 论文自动更新（去重+过滤预印本）====={Log.RESET}")
    load_existing()
    if not load_authors():
        return

    for orcid in orcid_authors:
        print(f"\n{Log.BLUE}──────── 处理：{orcid_authors[orcid]['name']}{Log.RESET}")
        dois = fetch_orcid_dois(orcid)
        for doi in dois:
            process_paper(orcid, doi)
            time.sleep(REQUEST_DELAY)

    save_csv()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Log.YELLOW}手动终止{Log.RESET}")