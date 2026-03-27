import requests
import csv
import os
import re
import time
from datetime import datetime
from urllib.parse import quote
from typing import Optional, Dict, List

# ===================== 核心配置 =====================
# 环境变量读取 ORCID 凭据
CLIENT_ID = os.getenv("ORCID_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("ORCID_SECRET", "")
# 文件路径（固定路径，确保生成在 scripts 目录下）
BASE_DIR = os.getcwd()
ORCID_CSV = os.path.join(BASE_DIR, "scripts", "orcids.csv")
NEWS_CSV = os.path.join(BASE_DIR, "scripts", "news.csv")
# 请求配置
TIMEOUT = 20
REQUEST_DELAY = 1
# ====================================================

# 全局数据存储
orcid_authors = {}  # ORCID -> 作者信息
paper_records = {}  # DOI -> 论文记录

class Log:
    """日志美化"""
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

# --------------------- 1. 读取作者CSV ---------------------
def load_authors():
    """容错读取 orcids.csv，支持中文、特殊字符"""
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
        print(f"{Log.GREEN}✅ 成功加载 {len(orcid_authors)} 位作者{Log.RESET}")
        return True
    except Exception as e:
        print(f"{Log.RED}❌ 读取作者失败：{str(e)}{Log.RESET}")
        return False

# --------------------- 2. 读取已有论文数据 ---------------------
def load_existing_papers():
    """加载已存在的 news.csv，无文件则跳过"""
    if not os.path.exists(NEWS_CSV):
        print(f"{Log.YELLOW}⚠️ news.csv 不存在，将新建文件{Log.RESET}")
        return
    
    try:
        with open(NEWS_CSV, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                doi = row["doi"].strip().lower()
                paper_records[doi] = row
        print(f"{Log.GREEN}✅ 加载已有论文：{len(paper_records)} 篇{Log.RESET}")
    except Exception as e:
        print(f"{Log.YELLOW}⚠️ 读取旧文件失败：{str(e)}{Log.RESET}")

# --------------------- 3. ORCID 抓取 DOI（终极修复版） ---------------------
def get_orcid_dois(orcid: str) -> List[str]:
    """
    从 ORCID 抓取所有 DOI
    支持：标准DOI字段 + URL中的DOI + 全量work遍历
    公开接口，无需TOKEN也能访问
    """
    url = f"https://pub.orcid.org/v3.0/{orcid}/works"
    headers = {"Accept": "application/json"}
    dois = set()

    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        # 遍历所有论文组
        for group in data.get("group", []):
            # 遍历所有工作记录（不只是第一条）
            for work in group.get("work-summary", []):
                # 方式1：提取标准 DOI 字段
                for ext_id in work.get("external-ids", {}).get("external-id", []):
                    if ext_id.get("external-id-type") == "doi":
                        raw_doi = ext_id.get("external-id-value", "").strip()
                        clean_doi = re.sub(r"^https?://doi\.org/", "", raw_doi, flags=re.I).lower()
                        if clean_doi:
                            dois.add(clean_doi)

                # 方式2：从论文链接中提取 DOI（作者未填写DOI但填了链接）
                work_url = work.get("url", {}).get("value", "")
                if work_url:
                    match = re.search(r"doi\.org/([0-9a-zA-Z\./-]+)", work_url, re.I)
                    if match:
                        dois.add(match.group(1).lower())

        result = list(dois)
        print(f"{Log.BLUE}🔍 ORCID {orcid} 抓取到 {len(result)} 个 DOI{Log.RESET}")
        return result

    except Exception as e:
        print(f"{Log.RED}❌ 抓取 ORCID 失败：{str(e)}{Log.RESET}")
        return []

# --------------------- 4. 获取论文标题/期刊 ---------------------
def get_paper_detail(doi: str):
    """通过 CrossRef API 获取论文信息，失败返回默认值"""
    try:
        url = f"https://api.crossref.org/works/{quote(doi)}"
        data = requests.get(url, timeout=TIMEOUT).json()["message"]
        title = data.get("title", ["未知标题"])[0]
        journal = data.get("container-title", ["未知期刊"])[0]
        return title, journal
    except:
        return "未知标题", "未知期刊"

# --------------------- 5. 合并/新增论文 ---------------------
def process_paper(orcid: str, doi: str):
    """处理单篇论文：新增/合并作者"""
    author = orcid_authors[orcid]
    name = author["name"]
    en_name = author["en_name"]

    # 论文已存在 → 合并作者
    if doi in paper_records:
        record = paper_records[doi]
        if name and name not in record["name"]:
            record["name"] = f"{record['name']},{name}" if record["name"] else name
        if en_name and en_name not in record["en_name"]:
            record["en_name"] = f"{record['en_name']},{en_name}" if record["en_name"] else en_name
        paper_records[doi] = record
        return

    # 论文不存在 → 新增记录
    title, journal = get_paper_detail(doi)
    paper_records[doi] = {
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "orcid_id": orcid,
        "doi": doi,
        "title": title,
        "journal": journal,
        "name": name,
        "en_name": en_name
    }

# --------------------- 6. 保存文件（强制生成） ---------------------
def save_csv():
    """强制生成 news.csv，哪怕没有数据也创建表头"""
    os.makedirs(os.path.dirname(NEWS_CSV), exist_ok=True)

    fields = ["fetch_time", "orcid_id", "doi", "title", "journal", "name", "en_name"]
    with open(NEWS_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(paper_records.values())

    print(f"{Log.GREEN}🎉 文件保存成功：{NEWS_CSV}{Log.RESET}")
    print(f"{Log.GREEN}📊 总计论文：{len(paper_records)} 篇{Log.RESET}")

# --------------------- 主函数 ---------------------
def main():
    print(f"{Log.BLUE}===== ORCID 论文自动更新工具 ====={Log.RESET}")
    
    # 初始化
    load_existing_papers()
    if not load_authors():
        return

    # 遍历所有作者抓取论文
    for orcid in orcid_authors:
        author = orcid_authors[orcid]
        print(f"\n{Log.BLUE}──────── 处理：{author['name']} ({author['en_name']}) {orcid}{Log.RESET}")
        
        dois = get_orcid_dois(orcid)
        for doi in dois:
            process_paper(orcid, doi)
            time.sleep(REQUEST_DELAY)

    # 保存结果
    save_csv()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Log.YELLOW}⚠️ 程序手动终止{Log.RESET}")