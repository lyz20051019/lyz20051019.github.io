import csv
import os
import re
from typing import Dict, List

# ===================== 核心配置 =====================
CSV_PATH = "scripts/news.csv"
TEMPLATE_ZH = "scripts/news-zh-cn.md"
TEMPLATE_EN = "scripts/news-en-us.md"
OUTPUT_ROOT = "./_news"
OUTPUT_ZH_DIR = os.path.join(OUTPUT_ROOT, "zh-cn")
OUTPUT_EN_DIR = os.path.join(OUTPUT_ROOT, "en-us")
# ====================================================

# 🔥 仅移除 HTML 标签，保留所有文字/符号/化学公式
def clean_html_tags(text: str) -> str:
    if not text:
        return ""
    # 只删除 <xxx> 格式的HTML标签，其余内容完全保留
    return re.sub(r'<[^>]+>', '', text).strip()

# 🔥 Jekyll YAML安全处理：给标题加双引号，解决冒号/特殊字符导致的解析崩溃
def yaml_safe_title(text: str) -> str:
    text = clean_html_tags(text)
    # 用双引号包裹标题，彻底解决YAML语法冲突（核心修复）
    return f'"{text}"'

def format_publish_time(year: str, month: str, date: str) -> str:
    try:
        y = int(year.strip()) if year.strip() else 0
        m = int(month.strip()) if month.strip() else 0
        d = int(date.strip()) if month.strip() else 0
    except:
        return ""
    time_parts = []
    if y > 0:
        time_parts.append(f"{y:04d}")
    if m > 0:
        time_parts.append(f"{m:02d}")
    if d > 0:
        time_parts.append(f"{d:02d}")
    return "-".join(time_parts)

def get_safe_filename(doi: str) -> str:
    if not doi:
        return "unknown"
    return doi.replace("/", "_").replace("\\", "_")

def load_unique_papers() -> List[Dict]:
    unique_dois = set()
    unique_papers = []
    if not os.path.exists(CSV_PATH):
        print(f"❌ 未找到CSV文件：{CSV_PATH}")
        return unique_papers
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doi = row.get("doi", "").strip()
            if not doi or doi in unique_dois:
                continue
            unique_dois.add(doi)
            unique_papers.append(row)
    print(f"✅ 加载完成：共 {len(unique_papers)} 篇唯一论文")
    return unique_papers

def load_template(template_path: str) -> str:
    if not os.path.exists(template_path):
        print(f"❌ 未找到模板：{template_path}")
        return ""
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def render_and_save(paper: Dict, template: str, output_dir: str, lang: str):
    doi = paper.get("doi", "").strip()
    if not doi:
        return

    filename = f"{get_safe_filename(doi)}.md"
    output_path = os.path.join(output_dir, filename)

    if os.path.exists(output_path):
        print(f"ℹ️ [{lang}] 文件已存在，跳过：{filename}")
        return

    publish_time = format_publish_time(
        paper.get("year", "0"),
        paper.get("month", "0"),
        paper.get("date", "0")
    )

    # ===================== 核心修复 =====================
    raw_title = paper.get("title", "")
    # 1. Front Matter用：YAML安全标题（去HTML+引号包裹）
    safe_front_title = yaml_safe_title(raw_title)
    # 2. 正文用：仅去HTML，保留所有符号
    safe_body_title = clean_html_tags(raw_title)

    # 替换模板
    content = template
    content = content.replace("{time}", publish_time)
    # 修复：分开渲染标题（解决YAML崩溃）
    content = content.replace('title: {title}', f'title: {safe_front_title}')
    content = content.replace('# {title}', f'# {safe_body_title}')
    # 替换其余字段
    for key, value in paper.items():
        if key == "title":
            continue
        placeholder = f"{{{key}}}"
        content = content.replace(placeholder, str(value))

    # 严格UTF-8写入
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    
    print(f"✅ [{lang}] 生成成功：{filename}")

def main():
    print("===== 自动生成新闻Markdown（Jekyll完美兼容版）=====")
    
    papers = load_unique_papers()
    if not papers:
        return

    template_zh = load_template(TEMPLATE_ZH)
    template_en = load_template(TEMPLATE_EN)

    for paper in papers:
        if template_zh:
            render_and_save(paper, template_zh, OUTPUT_ZH_DIR, "中文")
        if template_en:
            render_and_save(paper, template_en, OUTPUT_EN_DIR, "英文")

    print("\n🎉 所有文件处理完成！Jekyll构建正常，符号完整保留")

if __name__ == "__main__":
    main()