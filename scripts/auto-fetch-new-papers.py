import requests
import csv
import os
import re
import time
from datetime import datetime
from urllib.parse import quote
from typing import Optional, Dict, List, Tuple, Set

# ===================== 核心配置 =====================
BASE_DIR = os.getcwd()
ORCID_CSV = os.path.join(BASE_DIR, "scripts", "orcids.csv")
NEWS_CSV = os.path.join(BASE_DIR, "scripts", "news.csv")
PAPERS_BIB = os.path.join(BASE_DIR, "_bibliography", "papers.bib")
FILTER_DOI_PREFIX = ["10.21203", "10.31219", "10.3389"]
TIMEOUT = 15
REQUEST_DELAY = 0.5
# ====================================================

orcid_authors = {}
paper_records: Dict[str, dict] = {}
doi_author_map: Dict[str, Dict[str, Set[str]]] = {}
papers_bib_dois: Set[str] = set()

class Log:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

# 中文名字拼接
def join_chinese_names(name_list: List[str]) -> str:
    names = [n.strip() for n in name_list if n.strip()]
    names = sorted(list(set(names)))
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    elif len(names) == 2:
        return "和".join(names)
    else:
        return "、".join(names[:-1]) + "和" + names[-1]

# 英文名字拼接
def join_english_names(name_list: List[str]) -> str:
    names = [n.strip() for n in name_list if n.strip()]
    names = sorted(list(set(names)))
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    elif len(names) == 2:
        return " and ".join(names)
    else:
        return ", ".join(names[:-1]) + " and " + names[-1]

# 读取作者
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

# 加载 papers.bib 中的 DOI
def load_papers_bib_dois():
    global papers_bib_dois
    if not os.path.exists(PAPERS_BIB):
        print(f"{Log.YELLOW}ℹ️ 未找到 papers.bib 文件{Log.RESET}")
        return

    try:
        with open(PAPERS_BIB, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 提取 html 字段中的 DOI
        html_pattern = re.compile(r'html\s*=\s*\{([^}]+)\}', re.I)
        doi_pattern = re.compile(r'https?://doi\.org/([0-9]+\.[0-9]+/[^/]+)', re.I)
        
        for html_match in html_pattern.findall(content):
            doi_match = doi_pattern.search(html_match)
            if doi_match:
                doi = doi_match.group(1)
                papers_bib_dois.add(doi)
        
        print(f"{Log.GREEN}✅ 加载 papers.bib 中的 DOI：{len(papers_bib_dois)} 个{Log.RESET}")
    except Exception as e:
        print(f"{Log.RED}❌ 读取 papers.bib 失败：{str(e)}{Log.RESET}")

# 加载旧数据
def load_existing_papers():
    if not os.path.exists(NEWS_CSV):
        print(f"{Log.YELLOW}ℹ️ 未找到旧数据文件，将全新创建{Log.RESET}")
        return

    try:
        with open(NEWS_CSV, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                orcid = row.get("orcid_id", "").strip()
                doi = row.get("doi", "").strip()
                if not orcid or not doi:
                    continue

                key = f"{orcid}_{doi}"
                paper_records[key] = row

                if doi not in doi_author_map:
                    doi_author_map[doi] = {"cn": set(), "en": set()}
                cn_name = row.get("name", "").strip()
                en_name = row.get("en_name", "").strip()
                if cn_name:
                    doi_author_map[doi]["cn"].add(cn_name)
                if en_name:
                    doi_author_map[doi]["en"].add(en_name)

        print(f"{Log.GREEN}✅ 加载旧数据：{len(paper_records)} 条（fetch_time 已保留）{Log.RESET}")
    except Exception as e:
        print(f"{Log.RED}❌ 读取旧数据失败：{str(e)}{Log.RESET}")

# DOI清洗
def clean_doi(raw_doi: str) -> Optional[str]:
    if not raw_doi:
        return None
    doi = re.sub(r"^https?://doi\.org/", "", raw_doi.strip().lower(), flags=re.I)
    for prefix in FILTER_DOI_PREFIX:
        if doi.startswith(prefix):
            return None
    if len(doi) < 8:
        return None
    return doi

# ORCID 只抓标题+DOI
def fetch_orcid_dois(orcid: str) -> List[Tuple[str, str]]:
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

            raw_title = w.get("title", {}).get("title", {}).get("value", "")
            clean_title = re.sub(r'[\n\r\t\f\v]', ' ', raw_title)
            clean_title = re.sub(r'\s+', ' ', clean_title).strip()

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

            doi_set.add(doi)
            results.append((clean_title, doi))

        print(f"{Log.BLUE}🔍 {orcid} 有效论文：{len(results)} 篇{Log.RESET}")
        return results
    except Exception as e:
        print(f"{Log.RED}❌ 抓取失败：{str(e)}{Log.RESET}")
        return []

# CrossRef 元数据（年/月/日/期刊）
def crossref_meta(doi: str) -> dict:
    try:
        url = f"https://api.crossref.org/works/{quote(doi)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        m = r.json()["message"]

        year, month, day = 0, 0, 0
        date_parts = None
        if m.get("published-print"):
            date_parts = m["published-print"]["date-parts"][0]
        elif m.get("published-online"):
            date_parts = m["published-online"]["date-parts"][0]

        if date_parts:
            year = int(date_parts[0]) if len(date_parts)>=1 else 0
            month = int(date_parts[1]) if len(date_parts)>=2 else 0
            day = int(date_parts[2]) if len(date_parts)>=3 else 0

        journal = m.get("container-title", ["未知期刊"])[0] or "未知期刊"
        return {"year": year, "month": month, "date": day, "journal": journal}
    except Exception:
        return {"year": 0, "month": 0, "date": 0, "journal": "未知期刊"}

# 处理论文：旧记录缺数据就补齐，fetch_time不动
def process_paper(orcid: str, title: str, doi: str):
    # 检查 DOI 是否存在于 papers.bib 中
    if doi not in papers_bib_dois:
        print(f"{Log.YELLOW}🚫 过滤：DOI 不在 papers.bib 中{Log.RESET}")
        return
    
    key = f"{orcid}_{doi}"
    meta = crossref_meta(doi)

    # 把新抓到的作者加入集合
    if doi not in doi_author_map:
        doi_author_map[doi] = {"cn": set(), "en": set()}
    author = orcid_authors[orcid]
    cn_name = author["name"].strip()
    en_name = author["en_name"].strip()
    if cn_name:
        doi_author_map[doi]["cn"].add(cn_name)
    if en_name:
        doi_author_map[doi]["en"].add(en_name)

    # 已有记录：只补空缺，不改 fetch_time
    if key in paper_records:
        rec = paper_records[key]
        
        # 年份为空/0 就补齐
        if not rec.get("year") or rec["year"] in ("", "0", 0):
            rec["year"] = meta["year"]
        # 月份为空/0 就补齐
        if not rec.get("month") or rec["month"] in ("", "0", 0):
            rec["month"] = meta["month"]
        # 日期为空/0 就补齐
        if not rec.get("date") or rec["date"] in ("", "0", 0):
            rec["date"] = meta["date"]
        # 期刊未知就补齐
        if rec.get("journal", "") in ("", "未知期刊"):
            rec["journal"] = meta["journal"]
        return

    # 全新记录：正常新建
    paper_records[key] = {
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "orcid_id": orcid,
        "doi": doi,
        "title": title,
        "journal": meta["journal"],
        "year": meta["year"],
        "month": meta["month"],
        "date": meta["date"],
        "name": "",
        "en_name": ""
    }

# 统一拼接作者名
def patch_all_author_names():
    for key, record in paper_records.items():
        doi = record.get("doi", "").strip()
        if not doi or doi not in doi_author_map:
            continue
        cn_list = list(doi_author_map[doi]["cn"])
        en_list = list(doi_author_map[doi]["en"])
        record["name"] = join_chinese_names(cn_list)
        record["en_name"] = join_english_names(en_list)

# 保存CSV
def save_csv():
    os.makedirs(os.path.dirname(NEWS_CSV), exist_ok=True)
    fields = ["fetch_time","orcid_id","doi","title","journal","year","month","date","name","en_name"]
    
    with open(NEWS_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(paper_records.values())
    
    print(f"\n{Log.GREEN}🎉 总记录数：{len(paper_records)} 条{Log.RESET}")
    print(f"{Log.GREEN}✅ 旧数据空缺日期/期刊已补齐，fetch_time 未改动{Log.RESET}")

# 主流程
def main():
    print(f"{Log.BLUE}===== ORCID 论文抓取（补齐空缺日期版）====={Log.RESET}")
    if not load_authors():
        return

    load_existing_papers()
    load_papers_bib_dois()

    for orcid in orcid_authors:
        print(f"\n{Log.BLUE}──────── 处理：{orcid_authors[orcid]['name']}{Log.RESET}")
        paper_list = fetch_orcid_dois(orcid)
        for title, doi in paper_list:
            process_paper(orcid, title, doi)
            time.sleep(REQUEST_DELAY)

    patch_all_author_names()
    save_csv()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Log.YELLOW}手动终止{Log.RESET}")