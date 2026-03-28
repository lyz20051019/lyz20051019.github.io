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

# 🔥 仅移除HTML标签，保留所有文字/符号（不修改模板）
def clean_html_tags(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'<[^>]+>', '', text).strip()

# 🔥 拆分Markdown的 Front Matter 和 正文，仅修复头部YAML（核心！）
def fix_jekyll_frontmatter(content: str) -> str:
    # 匹配 --- 包裹的 Front Matter 区域
    pattern = r'^---\n(.*?)\n---'
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    if not match:
        return content
    
    frontmatter = match.group(1)
    # 处理 title 字段：添加双引号，清洗HTML标签，解决YAML语法冲突
    def replace_title_line(line: str) -> str:
        if line.strip().startswith('title:'):
            # 提取标题内容
            title_content = line.split(':', 1)[1].strip()
            # 清洗HTML + 双引号包裹（Jekyll必须）
            safe_title = clean_html_tags(title_content)
            return f'title: "{safe_title}"'
        return line
    
    # 逐行修复 Front Matter
    fixed_lines = [replace_title_line(line) for line in frontmatter.split('\n')]
    fixed_frontmatter = '\n'.join(fixed_lines)
    # 替换回原内容
    return content.replace(frontmatter, fixed_frontmatter)

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
    if not doi or not template:
        return

    filename = f"{get_safe_filename(doi)}.md"
    output_path = os.path.join(output_dir, filename)

    # 已存在则跳过
    if os.path.exists(output_path):
        print(f"ℹ️ [{lang}] 文件已存在，跳过：{filename}")
        return

    # 1. 拼接时间字段
    publish_time = format_publish_time(
        paper.get("year", "0"),
        paper.get("month", "0"),
        paper.get("date", "0")
    )

    # 2. 🔥 完整替换所有占位符（完全遵循模板，不修改模板）
    content = template
    content = content.replace("{time}", publish_time)
    for key, value in paper.items():
        placeholder = f"{{{key}}}"
        content = content.replace(placeholder, str(value))

    # 3. 🔥 自动修复 Front Matter（代码自动加引号、洗HTML）
    final_content = fix_jekyll_frontmatter(content)

    # 4. 严格UTF-8写入文件
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_content.strip())
    
    print(f"✅ [{lang}] 生成成功：{filename}")

def main():
    print("===== 自动生成新闻Markdown（模板零改动·Jekyll兼容版）=====")
    
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

    print("\n🎉 所有文件生成完成！模板无改动，Jekyll构建正常")

if __name__ == "__main__":
    main()