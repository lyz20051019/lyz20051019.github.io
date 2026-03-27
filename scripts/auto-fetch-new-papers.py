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
existing_news: Dict[str, Dict] = {}

class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

# -----------------------------------------------------------------------------
# 🔥 彻底修复：容错读取CSV，无视隐藏字符/空格/BOM
# -----------------------------------------------------------------------------
def load_orcid_authors():
    if not os.path.exists(ORCID_CSV):
        print(f"{Colors.RED}❌ 未找到 {ORCID_CSV}{Colors.RESET}")
        return False
    
    try:
        # 兼容所有编码、隐藏字符、空格
        with open(ORCID_CSV, "r", encoding="utf-8-sig") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        # 第一行表头：自动去除空格，兼容格式
        headers = [col.strip() for col in lines[0].split(",")]
        # 数据行
        for line in lines[1:]:
            values = [val.strip() for val in line.split(",")]
            row = dict(zip(headers, values))
            
            orcid = row.get("orcid", "")
            name = row.get("name", "")
            en_name = row.get("en_name", "")
            
            if orcid:
                orcid_info_map[orcid] = {"name": name, "en_name": en_name}
        
        print(f"{Colors.GREEN}✅ 加载 {len(orcid_info_map)} 个 ORCID 信息{Colors.RESET}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ CSV读取失败：{str(e)}{Colors.RESET}")
        return False

# -----------------------------------------------------------------------------
# 读取已存在的news.csv
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
    except Exception:
        pass

# -----------------------------------------------------------------------------
# ORCID API
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
    except Exception:
        print(f"{Colors.RED}❌ Token 获取失败{Colors.RESET}")
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
    except Exception:
        return []

def get_paper_info(doi):
    try:
        url = f"https://api.crossref.org/works/{quote(doi)}"
        data = requests.get(url, timeout=10).json()["message"]
        return data.get("title", ["未知标题"])[0], data.get("container-title", ["未知期刊"])[0]
    except Exception:
        return "未知标题", "未知期刊"

# -----------------------------------------------------------------------------
# 处理文章：合并作者 + 保留首次时间
# -----------------------------------------------------------------------------
def process_article(orcid, doi, name, en_name):
    if doi in existing_news:
        row = existing_news[doi]
        # 合并中文名（去重）
        if name and name not in row["name"]:
            row["name"] = f"{row['name']},{name}" if row["name"] else name
        # 合并英文名（去重）
        if en_name and en_name not in row["en_name"]:
            row["en_name"] = f"{row['en_name']},{en_name}" if row["en_name"] else en_name
        existing_news[doi] = row
        return

    # 新文章：记录时间
    fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title, journal = get_paper_info(doi)
    existing_news[doi] = {
        "fetch_time": fetch_time,
        "orcid_id": orcid,
        "doi": doi,
        "title": title,
        "journal": journal,
        "name": name,
        "en_name": en_name
    }

# -----------------------------------------------------------------------------
# 保存文件
# -----------------------------------------------------------------------------
def save_news():
    with open(NEWS_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "fetch_time", "orcid_id", "doi", "title", "journal", "name", "en_name"
        ])
        writer.writeheader()
        writer.writerows(existing_news.values())

# -----------------------------------------------------------------------------
# 主流程
# -----------------------------------------------------------------------------
def main():
    print(f"{Colors.BLUE}=== ORCID 文章自动更新 ==={Colors.RESET}")
    load_existing_news()
    
    if not load_orcid_authors():
        return

    token = get_access_token()
    if not token:
        return

    for orcid, info in orcid_info_map.items():
        name = info["name"]
        en_name = info["en_name"]
        print(f"\n{Colors.BLUE}处理：{orcid} | {name} ({en_name}){Colors.RESET}")
        
        dois = get_orcid_dois(orcid, token)
        for doi in dois:
            process_article(orcid, doi, name, en_name)
            time.sleep(REQUEST_DELAY)

    save_news()
    print(f"{Colors.GREEN}🎉 完成！共 {len(existing_news)} 条记录{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n中断")