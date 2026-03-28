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

# 🔥 核心：统一清洗所有HTML标签（<i> <sup> <b>等），保留所有文字/特殊符号
def clean_html_tags(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'<[^>]+>', '', text).strip()

# 🔥 格式化Front Matter标题：清洗HTML + 双引号包裹（YAML安全）
def format_front_title(title: str) -> str:
    return f'"{clean_html_tags(title)}"'

# 拼接发布时间（非0保留，为0舍去）
def format_publish_time(year: str, month: str, date: str) -> str:
    try:
        y = int(year.strip()) if year.strip() else 0
        m = int(month.strip()) if month.strip() else 0
        d = int(date.strip()) if date.strip() else 0
    except:
        return ""
    
    time_parts = []
    if y > 0: time_parts.append(f"{y:04d}")
    if m > 0: time_parts.append(f"{m:02d}")
    if d > 0: time_parts.append(f"{d:02d}")
    return "-".join(time_parts)

# DOI安全文件名
def get_safe_filename(doi: str) -> str:
    if not doi: return "unknown"
    return doi.replace("/", "_").replace("\\", "_")

# 读取CSV并按DOI去重
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
            if not doi or doi in unique_dois: continue
            unique_dois.add(doi)
            unique_papers.append(row)
    print(f"✅ 加载完成：共 {len(unique_papers)} 篇唯一论文")
    return unique_papers

# 加载模板
def load_template(template_path: str) -> str:
    if not os.path.exists(template_path):
        print(f"❌ 未找到模板：{template_path}")
        return ""
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

# 渲染并保存文件（核心逻辑）
def render_and_save(paper: Dict, template: str, output_dir: str, lang: str):
    doi = paper.get("doi", "").strip()
    raw_title = paper.get("title", "")
    if not doi or not template or not raw_title:
        return

    # 生成文件路径
    filename = f"{get_safe_filename(doi)}.md"
    output_path = os.path.join(output_dir, filename)
    if os.path.exists(output_path):
        print(f"ℹ️ [{lang}] 文件已存在，跳过：{filename}")
        return

    # 1. 处理所有变量
    publish_time = format_publish_time(paper.get("year","0"), paper.get("month","0"), paper.get("date","0"))
    cleaned_title = clean_html_tags(raw_title)  # 清洗后的纯文本标题（全局使用）
    front_title = format_front_title(raw_title) # 头部专用：双引号包裹

    # 2. 替换模板变量
    content = template
    content = content.replace("{time}", publish_time)
    # 🔥 关键修复：全局替换title，统一清洗HTML标签
    content = content.replace("{title}", cleaned_title)
    # 替换其余字段
    for key, value in paper.items():
        if key == "title": continue
        content = content.replace(f"{{{key}}}", str(value))
    # 🔥 修复头部title：替换为YAML安全格式
    content = re.sub(r'title: "?.*?"?', f'title: {front_title}', content, flags=re.DOTALL)

    # 保存文件（严格UTF-8）
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    
    print(f"✅ [{lang}] 生成成功：{filename}")

# 主函数
def main():
    print("===== 自动生成新闻Markdown（HTML全清洗·Jekyll完美版）=====")
    papers = load_unique_papers()
    if not papers: return

    template_zh = load_template(TEMPLATE_ZH)
    template_en = load_template(TEMPLATE_EN)

    for paper in papers:
        if template_zh: render_and_save(paper, template_zh, OUTPUT_ZH_DIR, "中文")
        if template_en: render_and_save(paper, template_en, OUTPUT_EN_DIR, "英文")

    print("\n🎉 所有文件生成完成！标题HTML已全清洗，Jekyll构建正常")

if __name__ == "__main__":
    main()