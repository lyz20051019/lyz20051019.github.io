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
# 过滤预印本平台DOI前缀
FILTER_DOI_PREFIX = ["10.21203", "10.31219", "10.3389"] # 预印本/无效DOI
TIMEOUT = 15
REQUEST_DELAY = 0.5
# ====================================================

orcid_authors = {}
# 全局唯一DOI存储（彻底去重）
unique_papers: Dict[str, dict] = {}

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

# 清洗+过滤DOI（彻底去重+过滤预印本）
def clean_doi(raw_doi: str) -> Optional[str]:
    if not raw_doi:
        return None
    # 统一格式
    doi = re.sub(r"^https?://doi\.org/", "", raw_doi.strip().lower())
    # 过滤无效/预印本DOI
    for prefix in FILTER_DOI_PREFIX:
        if doi.startswith(prefix):
            return None
    # 过滤太短的无效DOI
    if len(doi) < 8:
        return None
    return doi

# 从ORCID抓取DOI（严格去重）
def fetch_orcid_dois(orcid: str) -> List[str]:
    url = f"https://pub.orcid.org/v3.0/{orcid}/works"
    headers = {"Accept": "application/json"}
    doi_set = set()

    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        data = resp.json()
        for group in data.get("group", []):
            for work in group.get("work-summary", []):
                # 提取DOI
                for ext in work.get("external-ids", {}).get("external-id", []):
                    if ext.get("external-id-type") == "doi":
                        cleaned = clean_doi(ext.get("external-id-value", ""))
                        if cleaned:
                            doi_set.add(cleaned)
                # 从链接提取
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

# 获取论文信息
def get_paper(doi: str):
    try:
        url = f"https://api.crossref.org/works/{quote(doi)}"
        msg = requests.get(url, timeout=TIMEOUT).json()["message"]
        title = msg.get("title", ["未知标题"])[0]
        journal = msg.get("container-title", ["未知期刊"])[0]
        # 去除html标签
        title = re.sub(r"<[^>]+>", "", title)
        journal = re.sub(r"<[^>]+>", "", journal)
        return title, journal
    except:
        return "未知标题", "未知期刊"

# 处理单篇论文（合并作者+唯一存储）
def process_paper(orcid: str, doi: str):
    author = orcid_authors[orcid]
    name, en_name = author["name"], author["en_name"]

    # 已存在：仅合并作者
    if doi in unique_papers:
        row = unique_papers[doi]
        if name and name not in row["name"]:
            row["name"] = f"{row['name']},{name}" if row["name"] else name
        if en_name and en_name not in row["en_name"]:
            row["en_name"] = f"{row['en_name']},{en_name}" if row["en_name"] else en_name
        unique_papers[doi] = row
        return

    # 新论文：新增
    fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title, journal = get_paper(doi)
    unique_papers[doi] = {
        "fetch_time": fetch_time,
        "orcid_id": orcid,
        "doi": doi,
        "title": title,
        "journal": journal,
        "name": name,
        "en_name": en_name
    }

# 保存文件
def save_csv():
    os.makedirs(os.path.dirname(NEWS_CSV), exist_ok=True)
    fields = ["fetch_time", "orcid_id", "doi", "title", "journal", "name", "en_name"]
    with open(NEWS_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(unique_papers.values())
    print(f"\n{Log.GREEN}🎉 最终有效论文：{len(unique_papers)} 篇{Log.RESET}")
    print(f"{Log.GREEN}✅ 文件已保存：scripts/news.csv{Log.RESET}")

# 主流程
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