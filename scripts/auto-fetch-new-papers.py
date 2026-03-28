import requests
import csv
import os
import re
import time
from datetime import datetime
from urllib.parse import quote
from typing import Optional, Dict, List, Tuple

# ===================== 核心配置 =====================
BASE_DIR = os.getcwd()
ORCID_CSV = os.path.join(BASE_DIR, "scripts", "orcids.csv")
NEWS_CSV = os.path.join(BASE_DIR, "scripts", "news.csv")
FILTER_DOI_PREFIX = ["10.21203", "10.31219", "10.3389"]  # 预印本过滤
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

# 读取作者信息
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

# 读取已有news.csv
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

# DOI清洗（过滤预印本+标准化）
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

# 标题归一化（去重专用）
def normalize_title(title: str) -> str:
    if not title:
        return ""
    title = title.lower()
    title = re.sub(r"<[^>]+>", "", title)
    title = re.sub(r"[^a-z0-9\u4e00-\u9fa5]", "", title)
    return title.strip()

# 🔥 修复核心：适配ORCID官方日期结构（字典取值）+ 彻底清洗标题换行
def fetch_orcid_dois(orcid: str) -> List[Tuple[str, str, int, int, int]]:
    url = f"https://pub.orcid.org/v3.0/{orcid}/works"
    headers = {"Accept": "application/json"}
    results = []
    doi_set = set()

    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        data = resp.json()
        
        for group in data.get("group", []):
            ws = group.get("work-summary", [])
            if not ws:
                continue
            w = ws[0]

            # 1. 清洗标题：删除所有换行、缩进、多余空格
            raw_title = w.get("title", {}).get("title", {}).get("value", "")
            clean_title = re.sub(r'[\n\r\t\f\v]', ' ', raw_title)
            clean_title = re.sub(r'\s+', ' ', clean_title).strip()

            # 2. 提取并清洗DOI
            doi = None
            for eid in w.get("external-ids", {}).get("external-id", []):
                if eid.get("external-id-type") == "doi":
                    doi = eid.get("external-id-value")
                    break
            if not doi:
                continue
            doi = clean_doi(doi)
            if not doi or doi in doi_set:
                continue

            # 3. 🔥 修复ORCID日期解析（适配字典结构，无报错）
            year, month, day = 0, 0, 0
            pub_date = w.get("publication-date", {})
            # ORCID API 格式：year = {"value": "2026"}
            if pub_date.get("year"):
                year = int(pub_date["year"].get("value", 0))
            if pub_date.get("month"):
                month = int(pub_date["month"].get("value", 0))
            if pub_date.get("day"):
                day = int(pub_date["day"].get("value", 0))

            doi_set.add(doi)
            results.append((clean_title, doi, year, month, day))

        print(f"{Log.BLUE}🔍 {orcid} 有效论文：{len(results)} 篇{Log.RESET}")
        return results
    except Exception as e:
        print(f"{Log.RED}❌ 抓取失败：{str(e)}{Log.RESET}")
        return []

# 获取期刊信息
def get_paper_journal(doi: str) -> str:
    try:
        url = f"https://api.crossref.org/works/{quote(doi)}"
        msg = requests.get(url, timeout=TIMEOUT).json()["message"]
        if msg.get("type") != "journal-article":
            return "未知期刊"
        journal = msg.get("container-title", ["未知期刊"])[0]
        return re.sub(r"<[^>]+>", "", journal)
    except:
        return "未知期刊"

# 双重去重（DOI+标题）+ 数据写入
def process_paper(orcid: str, clean_title: str, doi: str, year: int, month: int, day: int):
    # DOI去重
    if doi in unique_papers:
        return
    # 标题去重
    norm_title = normalize_title(clean_title)
    if norm_title in exist_titles:
        return

    journal = get_paper_journal(doi)
    author = orcid_authors[orcid]
    name, en_name = author["name"], author["en_name"]
    fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 写入所有字段（日期强制有值，无空白）
    unique_papers[doi] = {
        "fetch_time": fetch_time,
        "orcid_id": orcid,
        "doi": doi,
        "title": clean_title,
        "journal": journal,
        "year": year,
        "month": month,
        "date": day,
        "name": name,
        "en_name": en_name
    }
    exist_titles.add(norm_title)

# 保存CSV（完整字段，日期列必输出）
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

# 主流程
def main():
    print(f"{Log.BLUE}===== ORCID 论文自动更新（最终修复版）====={Log.RESET}")
    load_existing()
    if not load_authors():
        return

    for orcid in orcid_authors:
        print(f"\n{Log.BLUE}──────── 处理：{orcid_authors[orcid]['name']}{Log.RESET}")
        paper_list = fetch_orcid_dois(orcid)
        for title, doi, year, month, day in paper_list:
            process_paper(orcid, title, doi, year, month, day)
            time.sleep(REQUEST_DELAY)

    save_csv()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Log.YELLOW}手动终止{Log.RESET}")