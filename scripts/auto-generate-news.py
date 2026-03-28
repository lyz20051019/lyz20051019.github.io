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

# 🔥 核心修复：清洗 Jekyll 不兼容的 HTML 标签 / 特殊符号
def clean_jekyll_text(text: str) -> str:
    if not text:
        return ""
    # 1. 移除所有 HTML 标签（<i> <sup> 等，Front Matter 禁止使用）
    text = re.sub(r'<[^>]+>', '', text)
    # 2. 替换特殊化学符号为纯文本兼容格式
    text = text.replace("sp(3)", "sp3")
    text = text.replace("η6", "eta6")
    # 3. 全角符号转半角
    text = text.replace("，", ",")
    text = text.replace("！", "!")
    # 4. 移除 YAML 不兼容的特殊字符
    text = text.replace(":", " -").replace("{", "").replace("}", "")
    return text.strip()

def format_publish_time(year: str, month: str, date: str) -> str:
    try:
        y = int(year.strip()) if year.strip() else 0
        m = int(month.strip()) if month.strip() else 0
        d = int(date.strip()) if date.strip() else 0
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

    # 🔥 关键修复：给 Front Matter 的 title 清洗 HTML 标签（不修改原标题）
    raw_title = paper.get("title", "")
    jekyll_title = clean_jekyll_text(raw_title)
    
    content = template
    content = content.replace("{time}", publish_time)
    # 渲染纯文本安全标题到 Front Matter
    content = content.replace("{title}", jekyll_title)
    # 渲染其他字段
    for key, value in paper.items():
        if key == "title":
            continue
        placeholder = f"{{{key}}}"
        content = content.replace(placeholder, str(value))

    os.makedirs(output_dir, exist_ok=True)
    # 强制 UTF-8 无 BOM 写入，Jekyll 标准编码
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    
    print(f"✅ [{lang}] 生成成功：{filename}")

def main():
    print("===== 自动生成新闻Markdown文件（Jekyll兼容版）=====")
    
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

    print("\n🎉 所有文件处理完成！Jekyll 解析兼容已修复")

if __name__ == "__main__":
    main()