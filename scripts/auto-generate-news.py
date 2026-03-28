import csv
import os
from typing import Dict, List

# ===================== 核心配置 =====================
# CSV文件路径
CSV_PATH = "scripts/news.csv"
# 模板文件路径
TEMPLATE_ZH = "scripts/news-zh-cn.md"
TEMPLATE_EN = "scripts/news-en-us.md"
# 输出根目录
OUTPUT_ROOT = "./_news"
OUTPUT_ZH_DIR = os.path.join(OUTPUT_ROOT, "zh-cn")
OUTPUT_EN_DIR = os.path.join(OUTPUT_ROOT, "en-us")
# ====================================================

def format_publish_time(year: str, month: str, date: str) -> str:
    """
    特殊处理 {time} 字段
    规则：非0数值保留，为0则舍去，自动拼接
    示例：
    2025,3,28 → 2025-03-28
    2025,0,0 → 2025
    2025,10,0 → 2025-10
    0,0,0 → 空字符串
    """
    # 转换为整数
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
    """将DOI转换为安全的文件名（替换/等非法字符）"""
    if not doi:
        return "unknown"
    return doi.replace("/", "_").replace("\\", "_")

def load_unique_papers() -> List[Dict]:
    """
    读取CSV并去重
    规则：以DOI为唯一标识，同一文章仅保留一条记录
    """
    unique_dois = set()
    unique_papers = []

    if not os.path.exists(CSV_PATH):
        print(f"❌ 未找到CSV文件：{CSV_PATH}")
        return unique_papers

    # 编码：utf-8-sig 兼容Windows导出的CSV带BOM的情况
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doi = row.get("doi", "").strip()
            # 跳过空DOI / 已存在的DOI
            if not doi or doi in unique_dois:
                continue
            unique_dois.add(doi)
            unique_papers.append(row)
    
    print(f"✅ 加载完成：共 {len(unique_papers)} 篇唯一论文")
    return unique_papers

def load_template(template_path: str) -> str:
    """加载Markdown模板文件"""
    if not os.path.exists(template_path):
        print(f"❌ 未找到模板：{template_path}")
        return ""
    # 强制UTF-8读取模板
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def render_and_save(paper: Dict, template: str, output_dir: str, lang: str):
    """
    渲染模板并保存文件
    规则：文件已存在则直接跳过
    """
    doi = paper.get("doi", "").strip()
    if not doi:
        return

    # 生成文件名
    filename = f"{get_safe_filename(doi)}.md"
    output_path = os.path.join(output_dir, filename)

    # 已存在则跳过（核心要求）
    if os.path.exists(output_path):
        print(f"ℹ️ [{lang}] 文件已存在，跳过：{filename}")
        return

    # 处理特殊字段 {time}
    publish_time = format_publish_time(
        paper.get("year", "0"),
        paper.get("month", "0"),
        paper.get("date", "0")
    )

    # 替换所有占位符
    content = template
    # 替换特殊字段
    content = content.replace("{time}", publish_time)
    # 替换CSV所有字段
    for key, value in paper.items():
        placeholder = f"{{{key}}}"
        content = content.replace(placeholder, str(value))

    # 写入文件：强制UTF-8编码，无BOM，保证跨平台兼容
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    
    print(f"✅ [{lang}] 生成成功：{filename}")

def main():
    print("===== 自动生成新闻Markdown文件 =====")
    
    # 1. 加载唯一论文数据
    papers = load_unique_papers()
    if not papers:
        return

    # 2. 加载双语模板
    template_zh = load_template(TEMPLATE_ZH)
    template_en = load_template(TEMPLATE_EN)

    # 3. 批量生成文件
    for paper in papers:
        # 生成中文文件
        if template_zh:
            render_and_save(paper, template_zh, OUTPUT_ZH_DIR, "中文")
        # 生成英文文件
        if template_en:
            render_and_save(paper, template_en, OUTPUT_EN_DIR, "英文")

    print("\n🎉 所有文件处理完成！")

if __name__ == "__main__":
    main()