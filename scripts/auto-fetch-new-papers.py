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
FILTER_DOI_PREFIX = ["10.21203", "10.31219", "10.3389"]
TIMEOUT = 15
REQUEST_DELAY = 0.5
# ====================================================

orcid_authors = {}
unique_papers: Dict[str, dict] = {}
exist_titles: set = set()

class Log:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

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

def load_existing():
    global exist_titles
    if not os.path.exists(NEWS_CSV):
        print(f"{Log.YELLOW}⚠️ 新建 news.csv{Log.RESET}")
        return
    try:
        with open(NEWS_CSV, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                doi = row["doi"].strip().lower()
                unique_papers[doi] = row
                title = normalize_title(row["title"])
                exist_titles.add(title)
        print(f"{Log.GREEN}✅ 加载已有论文：{len(unique_papers)} 篇{Log.RESET}")
    except:
        pass

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

def normalize_title(title: str) -> str:
    if not title:
        return ""
    title = title.lower()
    title = re.sub(r"<[^>]+>", "", title)
    title = re.sub(r"[^a-z0-9\u4e00-\u9fa5]", "", title)
    return title.strip()

# 🔥 修复1：清洗标题换行/异常格式 + 修复2：获取发表年月日
def get_paper(doi: str):
    try:
        url = f"https://api.crossref.org/works/{quote(doi)}"
        msg = requests.get(url, timeout=TIMEOUT).json()["message"]
        if msg.get("type") != "journal-article":
            return None, None, 0, 0, 0

        # 清洗标题：删除换行、回车、制表符、多余空格
        title = msg.get("title", ["未知标题"])[0]
        title = re.sub(r'[\n\r\t]+', ' ', title)    # 去掉换行/制表符
        title = re.sub(r'\s+', ' ', title).strip()  # 合并多余空格
        title = re.sub(r"<[^>]+>", "", title)       # 去掉HTML标签

        journal = msg.get("container-title", ["未知期刊"])[0]
        journal = re.sub(r"<[^>]+>", "", journal)

        # 解析发表日期：年/月/日，无则填0
        year, month, day = 0, 0, 0
        date_parts = None
        if "published-print" in msg:
            date_parts = msg["published-print"]["date-parts"][0]
        elif "published-online" in msg:
            date_parts = msg["published-online"]["date-parts"][0]
        
        if date_parts and len(date_parts) >= 1:
            year = date_parts[0]
        if date_parts and len(date_parts) >= 2:
            month = date_parts[1]
        if date_parts and len(date_parts) >= 3:
            day = date_parts[2]

        return title, journal, year, month, day
    except:
        return None, None, 0, 0, 0

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

# 双重去重 + 新增日期字段
def process_paper(orcid: str, doi: str):
    if doi in unique_papers:
        return

    title, journal, year, month, day = get_paper(doi)
    if not title or not journal:
        return

    norm_title = normalize_title(title)
    if norm_title in exist_titles:
        return

    author = orcid_authors[orcid]
    name, en_name = author["name"], author["en_name"]
    fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    unique_papers[doi] = {
        "fetch_time": fetch_time,
        "orcid_id": orcid,
        "doi": doi,
        "title": title,
        "journal": journal,
        "year": year,
        "month": month,
        "date": day,
        "name": name,
        "en_name": en_name
    }
    exist_titles.add(norm_title)

# 🔥 新增日期列到CSV
def save_csv():
    os.makedirs(os.path.dirname(NEWS_CSV), exist_ok=True)
    fields = [
        "fetch_time", "orcid_id", "doi", 
        "title", "journal", "year", "month", "date",
        "name", "en_name"
    ]
    with open(NEWS_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(unique_papers.values())
    print(f"\n{Log.GREEN}🎉 最终有效论文：{len(unique_papers)} 篇{Log.RESET}")
    print(f"{Log.GREEN}✅ 文件已保存：scripts/news.csv{Log.RESET}")

def main():
    print(f"{Log.BLUE}===== ORCID 论文自动更新（去重+纯净标题+日期）====={Log.RESET}")
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