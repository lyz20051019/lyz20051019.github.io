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

# 仅清洗HTML标签，保留所有文字
def clean_html_tags(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'<[^>]+>', '', text).strip()

# 拼接发布时间
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

# 读取CSV
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
            # 清洗标题HTML标签
            row['title'] = clean_html_tags(row['title'])
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

# 核心渲染：完全保留模板句式，仅替换变量+加双引号
def render_and_save(paper: Dict, template: str, output_dir: str, lang: str):
    doi = paper.get("doi", "").strip()
    if not doi or not template:
        return

    filename = f"{get_safe_filename(doi)}.md"
    output_path = os.path.join(output_dir, filename)
    if os.path.exists(output_path):
        print(f"ℹ️ [{lang}] 文件已存在，跳过：{filename}")
        return

    # 1. 替换所有变量（严格匹配模板）
    content = template
    content = content.replace("{time}", format_publish_time(paper.get("year","0"), paper.get("month","0"), paper.get("date","0")))
    # 替换全部占位符
    for key, value in paper.items():
        content = content.replace(f"{{{key}}}", str(value))

    # 2. 🔥 仅给Front Matter的title加双引号（保留完整句子，不破坏模板）
    def add_quotes(match):
        return f'title: "{match.group(1).strip()}"'
    # 精准匹配 title: 内容 并添加双引号
    content = re.sub(r'^title: (.*)$', add_quotes, content, flags=re.MULTILINE)

    # 保存文件
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    
    print(f"✅ [{lang}] 生成成功：{filename}")

def main():
    print("===== 自动生成新闻Markdown（模板完美匹配版）=====")
    papers = load_unique_papers()
    if not papers: return

    template_zh = load_template(TEMPLATE_ZH)
    template_en = load_template(TEMPLATE_EN)

    for paper in papers:
        if template_zh: render_and_save(paper, template_zh, OUTPUT_ZH_DIR, "中文")
        if template_en: render_and_save(paper, template_en, OUTPUT_EN_DIR, "英文")

    print("\n🎉 所有文件生成完成！模板句式100%保留")

if __name__ == "__main__":
    main()