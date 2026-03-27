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
TIMEOUT = 20
REQUEST_DELAY = 0.5
# ====================================================

orcid_authors = {}
paper_records = {}

class Log:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

# 读取作者
def load_authors():
    if not os.path.exists(ORCID_CSV):
        print(f"{Log.RED}❌ 未找到：{ORCID_CSV}{Log.RESET}")
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
                orcid_authors[orcid] = {"name": row.get("name", ""), "en_name": row.get("en_name", "")}
        print(f"{Log.GREEN}✅ 加载 {len(orcid_authors)} 位作者{Log.RESET}")
        return True
    except:
        return False

# 读取已有数据
def load_existing_papers():
    if not os.path.exists(NEWS_CSV):
        print(f"{Log.YELLOW}⚠️ 新建 news.csv{Log.RESET}")
        return
    try:
        with open(NEWS_CSV, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                doi = row["doi"].strip().lower()
                paper_records[doi] = row
    except:
        pass

# 🔥 终极去重抓取DOI
def get_orcid_dois(orcid: str) -> List[str]:
    url = f"https://pub.orcid.org/v3.0/{orcid}/works"
    headers = {"Accept": "application/json"}
    doi_set = set()

    try:
        data = requests.get(url, headers=headers, timeout=TIMEOUT).json()
        for group in data.get("group", []):
            for work in group.get("work-summary", []):
                # 提取标准DOI
                for ext_id in work.get("external-ids", {}).get("external-id", []):
                    if ext_id.get("external-id-type") == "doi":
                        raw = ext_id.get("external-id-value", "").strip()
                        clean = re.sub(r"^https?://doi\.org/", "", raw, flags=re.I).lower()
                        if clean and len(clean) > 5:
                            doi_set.add(clean)
                # 链接提取DOI
                url_val = work.get("url", {}).get("value", "")
                match = re.search(r"doi\.org/([0-9a-z\./-]+)", url_val, re.I)
                if match:
                    doi_set.add(match.group(1).lower())

        doi_list = sorted(list(doi_set))
        print(f"{Log.BLUE}🔍 {orcid} 去重后 DOI：{len(doi_list)} 个{Log.RESET}")
        return doi_list
    except Exception as e:
        print(f"{Log.RED}❌ 抓取失败：{e}{Log.RESET}")
        return []

# 获取论文信息
def get_paper_detail(doi: str):
    try:
        data = requests.get(f"https://api.crossref.org/works/{quote(doi)}", timeout=10).json()["message"]
        return data.get("title", ["未知标题"])[0], data.get("container-title", ["未知期刊"])[0]
    except:
        return "未知标题", "未知期刊"

# 处理论文
def process_paper(orcid: str, doi: str):
    au = orcid_authors[orcid]
    if doi in paper_records:
        rec = paper_records[doi]
        if au["name"] and au["name"] not in rec["name"]:
            rec["name"] = f"{rec['name']},{au['name']}" if rec["name"] else au["name"]
        if au["en_name"] and au["en_name"] not in rec["en_name"]:
            rec["en_name"] = f"{rec['en_name']},{au['en_name']}" if rec["en_name"] else au["en_name"]
        return

    title, journal = get_paper_detail(doi)
    paper_records[doi] = {
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "orcid_id": orcid, "doi": doi,
        "title": title, "journal": journal,
        "name": au["name"], "en_name": au["en_name"]
    }

# 强制保存文件
def save_csv():
    os.makedirs(os.path.dirname(NEWS_CSV), exist_ok=True)
    fields = ["fetch_time", "orcid_id", "doi", "title", "journal", "name", "en_name"]
    with open(NEWS_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(paper_records.values())
    print(f"{Log.GREEN}🎉 已保存：{len(paper_records)} 篇论文{Log.RESET}")

# 主函数
def main():
    print(f"{Log.BLUE}===== ORCID 论文自动更新 ====={Log.RESET}")
    load_existing_papers()
    if not load_authors():
        return

    for orcid, au in orcid_authors.items():
        print(f"\n{Log.BLUE}处理：{au['name']} | {orcid}{Log.RESET}")
        dois = get_orcid_dois(orcid)
        for doi in dois:
            process_paper(orcid, doi)
            time.sleep(REQUEST_DELAY)

    save_csv()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Log.YELLOW}终止{Log.RESET}")