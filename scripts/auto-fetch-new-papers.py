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
ORCID_CSV = "./scripts/orcids.csv"       # 输入：ORCID+中英文姓名
NEWS_CSV = "./scripts/news.csv"          # 输出：文章列表（无重复DOI）
TIMEOUT = 15
REQUEST_DELAY = 1
# ============================================

# 全局数据存储
orcid_info_map: Dict[str, Dict[str, str]] = {}  # orcid -> {name, en_name}
doi_record_map: Dict[str, Dict] = {}            # doi -> 完整文章信息（去重+存首次时间）

class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

# -----------------------------------------------------------------------------
# 1. 从 orcids.csv 读取 ORCID + 中文/英文姓名
# -----------------------------------------------------------------------------
def load_orcid_info():
    if not os.path.exists(ORCID_CSV):
        print(f"{Colors.RED}❌ 未找到 {ORCID_CSV} 文件{Colors.RESET}")
        return False
    with open(ORCID_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            orcid = row.get("orcid", "").strip()
            name = row.get("name", "").strip()
            en_name = row.get("en_name", "").strip()
            if orcid:
                orcid_info_map[orcid] = {"name": name, "en_name": en_name}
    print(f"{Colors.GREEN}✅ 加载 {len(orcid_info_map)} 个 ORCID 信息{Colors.RESET}")
    return True

# -----------------------------------------------------------------------------
# 2. ORCID API 获取访问 Token
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
        print(f"{Colors.RED}❌ Token 获取失败：{str(e)}{Colors.RESET}")
        return None

# -----------------------------------------------------------------------------
# 3. 从 ORCID 获取文章 DOI 列表
# -----------------------------------------------------------------------------
def get_orcid_dois(orcid: str, token: str) -> List[str]:
    url = f"https://pub.orcid.org/v3.0/{orcid}/works"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    doi_list = []
    try:
        r = requests.get(url, headers=headers, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        for group in data.get("group", []):
            work_summaries = group.get("work-summary", [])
            if not work_summaries:
                continue
            work = work_summaries[0]
            # 提取 DOI
            for ext_id in work.get("external-ids", {}).get("external-id", []):
                if ext_id.get("external-id-type") == "doi":
                    doi = ext_id.get("external-id-value", "").strip()
                    if doi:
                        # 标准化 DOI（去掉前缀，统一小写）
                        doi = re.sub(r"^https?://doi\.org/", "", doi.lower())
                        doi_list.append(doi)
                    break
        # 去重单个 ORCID 内的重复 DOI
        return list(set(doi_list))
    except Exception as e:
        print(f"{Colors.RED}❌ ORCID {orcid} 抓取失败：{str(e)}{Colors.RESET}")
        return []

# -----------------------------------------------------------------------------
# 4. CrossRef 获取文章标题、期刊
# -----------------------------------------------------------------------------
def get_paper_info(doi: str) -> tuple[str, str]:
    try:
        url = f"https://api.crossref.org/works/{quote(doi)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        msg = r.json()["message"]
        title = msg.get("title", ["未知标题"])[0]
        journal = msg.get("container-title", ["未知期刊"])[0]
        return title, journal
    except Exception:
        return "未知标题", "未知期刊"

# -----------------------------------------------------------------------------
# 5. 合并作者姓名（中英文分别拼接，相同DOI不重复）
# -----------------------------------------------------------------------------
def merge_authors(doi: str, name: str, en_name: str):
    # 中文姓名合并
    if name and name not in doi_record_map[doi]["name"]:
        if doi_record_map[doi]["name"]:
            doi_record_map[doi]["name"] += f",{name}"
        else:
            doi_record_map[doi]["name"] = name
    # 英文姓名合并
    if en_name and en_name not in doi_record_map[doi]["en_name"]:
        if doi_record_map[doi]["en_name"]:
            doi_record_map[doi]["en_name"] += f",{en_name}"
        else:
            doi_record_map[doi]["en_name"] = en_name

# -----------------------------------------------------------------------------
# 6. 写入最终 news.csv（无重复DOI，保留首次时间）
# -----------------------------------------------------------------------------
def write_news_csv():
    with open(NEWS_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow(["fetch_time", "orcid_id", "doi", "title", "journal", "name", "en_name"])
        # 写入所有唯一数据
        for doi, info in doi_record_map.items():
            writer.writerow([
                info["fetch_time"],
                info["orcid_id"],
                doi,
                info["title"],
                info["journal"],
                info["name"],
                info["en_name"]
            ])
    print(f"\n{Colors.GREEN}🎉 完成！共保存 {len(doi_record_map)} 篇唯一文章{Colors.RESET}")

# -----------------------------------------------------------------------------
# 主流程
# -----------------------------------------------------------------------------
def main():
    print(f"{Colors.BLUE}=== ORCID 文章列表维护工具（DOI去重+中英文姓名）==={Colors.RESET}")
    
    # 1. 加载 ORCID 信息
    if not load_orcid_info():
        return

    # 2. 获取 API Token
    token = get_access_token()
    if not token:
        return

    # 3. 遍历所有 ORCID 抓取文章
    for orcid, info in orcid_info_map.items():
        name = info["name"]
        en_name = info["en_name"]
        print(f"\n{Colors.BLUE}== 处理：{orcid} | {name}({en_name}){Colors.RESET}")
        
        # 获取当前 ORCID 的所有 DOI
        dois = get_orcid_dois(orcid, token)
        for doi in dois:
            # ============= 核心：DOI 已存在 → 仅合并作者，不重复写入 =============
            if doi in doi_record_map:
                merge_authors(doi, name, en_name)
                print(f"{Colors.YELLOW}⚠️  DOI 已存在，合并作者：{doi}{Colors.RESET}")
                continue

            # ============= DOI 首次出现 → 新建记录，保存首次时间 =============
            fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            title, journal = get_paper_info(doi)
            # 存入记录
            doi_record_map[doi] = {
                "fetch_time": fetch_time,
                "orcid_id": orcid,
                "title": title,
                "journal": journal,
                "name": name,
                "en_name": en_name
            }
            print(f"{Colors.GREEN}✅ 新增：{doi[:50]} | {title[:40]}...{Colors.RESET}")
            time.sleep(REQUEST_DELAY)

    # 4. 写入结果文件
    write_news_csv()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ 程序手动中断{Colors.RESET}")