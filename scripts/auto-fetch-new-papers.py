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
FILTER_DOI_PREFIX = ["10.21203", "10.31219", "10.3389"]
TIMEOUT = 15
REQUEST_DELAY = 0.5
# ====================================================

orcid_authors = {}
# 存储最终论文记录 key: f"{orcid}_{doi}" 保证同一DOI不同ORCID多条记录
paper_records: Dict[str, dict] = {}
# 存储每个DOI对应的所有中文/英文作者列表（用于拼接）
doi_author_map: Dict[str, Dict[str, Set[str]]] = {}

class Log:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

# 中文名字拼接：2人A和B，多人A、B和C
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

# 英文名字拼接：2人A and B，多人A, B and C
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

# 加载已存在CSV，保留fetch_time，收集作者信息
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

                # 保留旧记录，绝不修改fetch_time
                key = f"{orcid}_{doi}"
                paper_records[key] = row

                # 收集该DOI对应的作者
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
    doi = re.sub(r"^https?://doi\.org/", "", raw_doi.strip().lower())
    for prefix in FILTER_DOI_PREFIX:
        if doi.startswith(prefix):
            return None
    if len(doi) < 8:
        return None
    return doi

# 标题归一化
def normalize_title(title: str) -> str:
    if not title:
        return ""
    title = title.lower()
    title = re.sub(r"<[^>]+>", "", title)
    title = re.sub(r"[^a-z0-9\u4e00-\u9fa5]", "", title)
    return title.strip()

# 从ORCID抓取论文
def fetch_orcid_papers(orcid: str) -> List[Tuple[str, str, int, int, int]]:
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

            year, month, day = 0, 0, 0
            pub_date = w.get("publication-date", {})
            try:
                year = int(pub_date.get("year", {}).get("value", 0))
            except: pass
            try:
                month = int(pub_date.get("month", {}).get("value", 0))
            except: pass
            try:
                day = int(pub_date.get("day", {}).get("value", 0))
            except: pass

            doi_set.add(doi)
            results.append((clean_title, doi, year, month, day))

        print(f"{Log.BLUE}🔍 {orcid} 有效论文：{len(results)} 篇{Log.RESET}")
        return results
    except Exception as e:
        print(f"{Log.RED}❌ 抓取失败：{str(e)}{Log.RESET}")
        return []

# 获取期刊名
def get_journal(doi: str) -> str:
    try:
        url = f"https://api.crossref.org/works/{quote(doi)}"
        msg = requests.get(url, timeout=TIMEOUT).json()["message"]
        if msg.get("type") != "journal-article":
            return "未知期刊"
        return msg.get("container-title", ["未知期刊"])[0]
    except:
        return "未知期刊"

# 处理单篇论文，支持多作者拼接
def process_paper(orcid: str, title: str, doi: str, year: int, month: int, day: int):
    key = f"{orcid}_{doi}"
    # 同一ORCID+DOI已存在，跳过（不重复添加）
    if key in paper_records:
        return

    # 初始化DOI作者集合
    if doi not in doi_author_map:
        doi_author_map[doi] = {"cn": set(), "en": set()}
    # 添加当前作者
    author = orcid_authors[orcid]
    cn_name = author["name"].strip()
    en_name = author["en_name"].strip()
    if cn_name:
        doi_author_map[doi]["cn"].add(cn_name)
    if en_name:
        doi_author_map[doi]["en"].add(en_name)

    # 查询期刊
    journal = get_journal(doi)
    # 新记录生成fetch_time，旧记录已保留不修改
    fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 先存入原始信息，最后统一拼接名字
    paper_records[key] = {
        "fetch_time": fetch_time,
        "orcid_id": orcid,
        "doi": doi,
        "title": title,
        "journal": journal,
        "year": year,
        "month": month,
        "date": day,
        "name": "",
        "en_name": ""
    }

# 统一为所有记录拼接作者名字
def patch_all_author_names():
    for key, record in paper_records.items():
        doi = record.get("doi", "").strip()
        if not doi or doi not in doi_author_map:
            continue
        # 拼接名字
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
    print(f"{Log.GREEN}✅ 作者名字已自动拼接，旧数据fetch_time未修改{Log.RESET}")

# 主流程
def main():
    print(f"{Log.BLUE}===== ORCID 论文抓取（多作者拼接+保留fetch_time）====={Log.RESET}")
    if not load_authors():
        return

    # 加载旧数据，保留fetch_time
    load_existing_papers()

    # 抓取所有作者论文
    for orcid in orcid_authors:
        print(f"\n{Log.BLUE}──────── 处理：{orcid_authors[orcid]['name']}{Log.RESET}")
        papers = fetch_orcid_papers(orcid)
        for title, doi, year, month, day in papers:
            process_paper(orcid, title, doi, year, month, day)
            time.sleep(REQUEST_DELAY)

    # 统一拼接所有作者名字
    patch_all_author_names()
    # 保存结果
    save_csv()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Log.YELLOW}手动终止{Log.RESET}")