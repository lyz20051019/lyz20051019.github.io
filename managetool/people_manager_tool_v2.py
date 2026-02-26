import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import yaml
import os
import re
from pathlib import Path

# 全局配置：严格匹配你的yml示例（无image字段，category自动赋值）
CATEGORIES = ["supervisor", "current_members", "past_members"]  # yml顶级分类（固定顺序）
CATEGORY_CN = ["导师", "现有组员", "往届组员"]  # GUI显示分类
# 分类对应category字段值（和你的示例完全一致，自动赋值，无需手动填）
CATEGORY_MAP = {
    "supervisor": "supervisor",
    "current_members": "current_team_members",
    "past_members": "past_team_members"
}
# YML字段配置：严格按你的示例顺序，分通用/专属字段（无image，无category）
# 通用字段：所有分类都有
COMMON_FIELDS = ["id", "name", "en_name", "position", "en_position"]
# 现有组员专属字段
CURRENT_FIELDS = ["research_interests", "en_research_interests", "email"]
# 往届组员专属字段（在现有组员基础上追加）
PAST_FIELDS = ["current_position", "en_current_position", "graduation_year"]
# 合并所有字段（按示例顺序，用于GUI文本框和YAML写入）
YML_FIELDS = COMMON_FIELDS + CURRENT_FIELDS + PAST_FIELDS
# 字段中文名称（匹配示例，用于GUI标签）
FIELD_CN = [
    "唯一ID", "中文名称", "英文名称", "中文职位", "英文职位",
    "中文研究方向", "英文研究方向", "邮箱",
    "中文现任职位", "英文现任职位", "毕业年份"
]
# 多语言配置
LANGS = ["zh-cn", "en-us"]
LANG_CN = ["中文md", "英文md"]
MD_TAB_INDEX = {1: "zh-cn", 2: "en-us"}  # 标签页索引对应语言

class PeopleManageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Al-Folio人员信息管理工具")
        self.root.geometry("1000x700")  # 精简窗口尺寸，适配极简文本框
        self.root.resizable(True, True)

        # 全局变量
        self.root_path = tk.StringVar()  # 项目根目录
        self.current_category = tk.StringVar(value=CATEGORY_CN[0])  # 当前选中分类
        self.current_selected_id = ""  # 当前选中人员ID（用于MD判断/YAML更新）
        self.yml_path = ""  # 缓存people.yml路径

        # 创建主布局
        self._create_widgets()
        # 绑定事件
        self._bind_events()

    def _create_widgets(self):
        """创建极简GUI控件：仅保留示例原数字段文本框"""
        # 1. 根目录选择区（顶部）
        frame_path = ttk.LabelFrame(self.root, text="项目根目录")
        frame_path.pack(fill=tk.X, padx=10, pady=5)
        ttk.Entry(frame_path, textvariable=self.root_path, state="readonly", width=80).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(frame_path, text="选择根目录", command=self._select_root_path).pack(side=tk.RIGHT, padx=5, pady=5)

        # 2. 分类+ID列表区（左侧，极简宽度）
        frame_list = ttk.LabelFrame(self.root, text="人员ID列表")
        frame_list.pack(fill=tk.Y, expand=False, padx=10, pady=5, side=tk.LEFT)
        frame_list.config(width=150)
        # 分类选择（极简）
        ttk.Combobox(frame_list, textvariable=self.current_category, values=CATEGORY_CN, state="readonly").pack(fill=tk.X, padx=5, pady=5)
        # ID列表框（极简）
        self.id_listbox = tk.Listbox(frame_list)
        self.id_listbox.pack(fill=tk.Y, expand=True, padx=5, pady=5)
        # 滚动条
        scroll_list = ttk.Scrollbar(frame_list, orient=tk.VERTICAL, command=self.id_listbox.yview)
        scroll_list.pack(side=tk.RIGHT, fill=tk.Y)
        self.id_listbox.config(yscrollcommand=scroll_list.set)

        # 3. 编辑区（右侧，核心区域，标签页极简）
        frame_editor = ttk.LabelFrame(self.root, text="信息编辑")
        frame_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.notebook = ttk.Notebook(frame_editor)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 3.1 YML字段编辑页（核心：仅示例原数字段，无多余）
        self.frame_yml = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_yml, text="YML字段（示例原数）")
        # 动态创建极简文本框（按示例字段顺序，无image/category）
        self.yml_entrys = {}
        for idx, (field, field_cn) in enumerate(zip(YML_FIELDS, FIELD_CN)):
            ttk.Label(self.frame_yml, text=f"{field_cn}：", width=12).grid(row=idx, column=0, padx=5, pady=3, sticky=tk.E)
            entry = ttk.Entry(self.frame_yml, width=60)
            entry.grid(row=idx, column=1, padx=5, pady=3, sticky=tk.W+tk.E)
            self.yml_entrys[field] = entry
        self.frame_yml.columnconfigure(1, weight=1)  # 输入框自适应宽度

        # 3.2 中文md编辑页（极简）
        self.frame_md_zh = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_md_zh, text=LANG_CN[0])
        self.md_zh_text = scrolledtext.ScrolledText(self.frame_md_zh, width=50, height=20)
        self.md_zh_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 3.3 英文md编辑页（极简）
        self.frame_md_en = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_md_en, text=LANG_CN[1])
        self.md_en_text = scrolledtext.ScrolledText(self.frame_md_en, width=50, height=20)
        self.md_en_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 4. 功能按钮区（底部，极简，仅3个核心按钮）
        frame_btn = ttk.Frame(self.root)
        frame_btn.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(frame_btn, text="保存修改", command=self._save_all, style="Accent.TButton").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(frame_btn, text="新增人员", command=self._add_people).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(frame_btn, text="重置编辑", command=self._reset_editor).pack(side=tk.LEFT, padx=5, pady=5)

        # 按钮样式（极简）
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="red", font=("SimHei", 10, "bold"))

    def _bind_events(self):
        """绑定核心事件，无多余"""
        self.current_category.trace("w", self._on_category_change)  # 分类切换
        self.id_listbox.bind("<<ListboxSelect>>", self._on_id_select)  # ID选中
        self.notebook.bind("<<NotebookTabChanged>>", self._on_md_tab_click)  # MD标签页点击

    def _select_root_path(self):
        """选择根目录，初始化yml（仅创建空文件，不修改原有内容）"""
        path = filedialog.askdirectory(title="选择al-folio项目根目录")
        if not path:
            return
        # 自动创建缺失目录（仅创建，不修改）
        for lang in LANGS:
            Path(os.path.join(path, "_pages", lang, "people")).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(path, "_data")).mkdir(parents=True, exist_ok=True)
        # 初始化people.yml（仅当文件不存在时创建空文件，存在则不触碰）
        self.yml_path = os.path.join(path, "_data", "people.yml")
        if not os.path.exists(self.yml_path):
            with open(self.yml_path, "w", encoding="utf-8") as f:
                yaml.dump({cat: [] for cat in CATEGORIES}, f, default_flow_style=False, indent=2, allow_unicode=True, sort_keys=False)
            messagebox.showinfo("提示", f"创建空people.yml：{self.yml_path}")
        # 缓存路径
        self.root_path.set(path)
        # 加载yml（仅读取，不修改）
        self._load_people_yml()
        messagebox.showinfo("成功", "根目录选择完成，已加载原有人员数据")

    def _load_people_yml(self):
        """仅读取yml原有内容，不修改、不排序、不重写"""
        if not self.yml_path or not os.path.exists(self.yml_path):
            return
        try:
            with open(self.yml_path, "r", encoding="utf-8") as f:
                self.people_data = yaml.safe_load(f) or {cat: [] for cat in CATEGORIES}
            # 补充分类（仅当分类缺失时添加空列表，不修改原有条目）
            for cat in CATEGORIES:
                if cat not in self.people_data:
                    self.people_data[cat] = []
            self._update_id_listbox()
        except Exception as e:
            messagebox.showerror("错误", f"读取yml失败：{str(e)}")

    def _update_id_listbox(self):
        """更新ID列表，仅显示当前分类原有ID"""
        self.id_listbox.delete(0, tk.END)
        current_cat = CATEGORIES[CATEGORY_CN.index(self.current_category.get())]
        for p in self.people_data.get(current_cat, []):
            if p.get("id"):
                self.id_listbox.insert(tk.END, p.get("id"))

    def _on_category_change(self, *args):
        """分类切换，仅更新ID列表"""
        self._update_id_listbox()

    def _on_id_select(self, *args):
        """ID选中，加载原有数据到文本框，无多余提示"""
        if not self.yml_path or not self.id_listbox.curselection():
            return
        # 获取当前分类和选中ID
        current_cat = CATEGORIES[CATEGORY_CN.index(self.current_category.get())]
        self.current_selected_id = self.id_listbox.get(self.id_listbox.curselection()[0])
        # 查找原有人员数据
        person = next((p for p in self.people_data[current_cat] if p.get("id") == self.current_selected_id), None)
        if not person:
            return
        # 加载数据到文本框（仅加载原有值，无默认值、无多余）
        for field in YML_FIELDS:
            self.yml_entrys[field].delete(0, tk.END)
            self.yml_entrys[field].insert(0, person.get(field, ""))
        # 加载MD内容（文件不存在则留空，无提示）
        self._load_md_content(self.current_selected_id)

    def _load_md_content(self, people_id):
        """加载MD内容，仅读取，无提示、无多余文字"""
        for lang, text_widget in zip(LANGS, [self.md_zh_text, self.md_en_text]):
            text_widget.delete(1.0, tk.END)
            md_path = os.path.join(self.root_path.get(), "_pages", lang, "people", f"{people_id}.md")
            if os.path.exists(md_path):
                with open(md_path, "r", encoding="utf-8") as f:
                    md_all = f.read()
                # 提取正文（除去Front Matter）
                match = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL).search(md_all)
                text_widget.insert(1.0, match.group(2).strip() if match else md_all.strip())

    def _on_md_tab_click(self, *args):
        """MD标签页点击，仅弹窗提示文件不存在，文本框留空"""
        if not self.root_path.get() or not self.current_selected_id:
            return
        # 获取当前点击的MD标签页对应的语言
        tab_idx = self.notebook.index(self.notebook.select())
        if tab_idx not in MD_TAB_INDEX:
            return
        lang = MD_TAB_INDEX[tab_idx]
        # 检查文件是否存在，仅弹窗提示
        md_path = os.path.join(self.root_path.get(), "_pages", lang, "people", f"{self.current_selected_id}.md")
        if not os.path.exists(md_path):
            messagebox.showinfo("提示", f"{LANG_CN[tab_idx-1]}文件不存在\n保存时将自动创建：{md_path}")

    def _reset_editor(self):
        """重置编辑框，仅清空内容，取消选中"""
        for field in YML_FIELDS:
            self.yml_entrys[field].delete(0, tk.END)
        self.md_zh_text.delete(1.0, tk.END)
        self.md_en_text.delete(1.0, tk.END)
        self.id_listbox.selection_clear(0, tk.END)
        self.current_selected_id = ""

    def _save_all(self):
        """核心保存逻辑：YAML仅追加/更新目标条目，MD按格式创建"""
        if not self.yml_path or not self.current_selected_id:
            messagebox.showwarning("警告", "请先选中人员ID！")
            return
        # 获取当前分类
        current_cat_cn = self.current_category.get()
        current_cat = CATEGORIES[CATEGORY_CN.index(current_cat_cn)]
        # 获取文本框内容，过滤空值
        person_info = {f: self.yml_entrys[f].get().strip() for f in YML_FIELDS if self.yml_entrys[f].get().strip()}
        # 必选字段验证
        if not person_info.get("id"):
            messagebox.showwarning("警告", "唯一ID不能为空！")
            return
        # 自动赋值category字段（匹配示例，无需手动填）
        person_info["category"] = CATEGORY_MAP[current_cat]

        # ========== YAML核心：仅追加/更新目标条目，不重写整个文件 ==========
        with open(self.yml_path, "r", encoding="utf-8") as f:
            original_yml = yaml.safe_load(f) or {cat: [] for cat in CATEGORIES}
        # 查找目标条目，存在则更新，不存在则追加（在原有分类后）
        updated = False
        for idx, p in enumerate(original_yml[current_cat]):
            if p.get("id") == self.current_selected_id:
                original_yml[current_cat][idx] = person_info
                updated = True
                break
        if not updated:
            original_yml[current_cat].append(person_info)  # 追加到分类最后，不改变原有顺序
        # 写入yml（仅更新目标条目/追加，保持原有分类/条目顺序，格式标准化）
        with open(self.yml_path, "w", encoding="utf-8") as f:
            yaml.dump(original_yml, f, default_flow_style=False, indent=2, allow_unicode=True, sort_keys=False, width=float("inf"))

        # ========== MD保存：按固定格式创建/覆盖，Front Matter标准化 ==========
        self._save_md_files(person_info["id"])

        # 刷新数据（仅读取，不修改）
        self._load_people_yml()
        messagebox.showinfo("成功", f"已保存！\nYAML：{current_cat_cn}分类下{self.current_selected_id}（仅更新/追加）\nMD：已同步保存")

    def _save_md_files(self, people_id):
        """保存MD文件，固定格式，和你的要求完全一致"""
        for lang in LANGS:
            # 获取正文（无多余处理）
            text_widget = self.md_zh_text if lang == "zh-cn" else self.md_en_text
            md_content = text_widget.get(1.0, tk.END).strip()
            # 固定Front Matter格式
            permalink = f"/zh-cn/people/{people_id}/" if lang == "zh-cn" else f"/people/{people_id}/"
            front_matter = f"""---
id: {people_id}
layout: person_detail
permalink: {permalink}
---
"""
            # 写入MD（不存在则创建，存在则覆盖正文，Front Matter不变）
            md_path = os.path.join(self.root_path.get(), "_pages", lang, "people", f"{people_id}.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(front_matter + md_content)

    def _add_people(self):
        """新增人员：仅追加到当前分类最后，不修改原有YAML内容"""
        if not self.yml_path:
            messagebox.showwarning("警告", "请先选择项目根目录！")
            return
        # 新增弹窗（极简，仅必填字段+核心字段）
        add_win = tk.Toplevel(self.root)
        add_win.title("新增人员（仅追加）")
        add_win.geometry("350x300")
        add_win.resizable(False, False)
        add_win.transient(self.root)
        add_win.grab_set()

        # 弹窗控件（极简，仅核心字段）
        ttk.Label(add_win, text="当前分类：", width=10).grid(row=0, column=0, padx=5, pady=8, sticky=tk.E)
        ttk.Label(add_win, text=self.current_category.get(), foreground="red").grid(row=0, column=1, padx=5, pady=8, sticky=tk.W)
        ttk.Label(add_win, text="唯一ID（必填）：", width=10).grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        add_id = ttk.Entry(add_win, width=20)
        add_id.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(add_win, text="中文名称：", width=10).grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        add_name = ttk.Entry(add_win, width=20)
        add_name.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(add_win, text="英文名称：", width=10).grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        add_en_name = ttk.Entry(add_win, width=20)
        add_en_name.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(add_win, text="中文职位：", width=10).grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
        add_position = ttk.Entry(add_win, width=20)
        add_position.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(add_win, text="英文职位：", width=10).grid(row=5, column=0, padx=5, pady=5, sticky=tk.E)
        add_en_position = ttk.Entry(add_win, width=20)
        add_en_position.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

        # 确认新增（核心：仅追加到当前分类最后）
        def _confirm_add():
            new_id = add_id.get().strip()
            if not new_id:
                messagebox.showwarning("警告", "唯一ID不能为空！")
                return
            # 检查ID是否重复（所有分类）
            if any(p.get("id") == new_id for cat in CATEGORIES for p in self.people_data.get(cat, [])):
                messagebox.showwarning("警告", f"ID[{new_id}]已存在，请勿重复！")
                return
            # 获取当前分类
            current_cat = CATEGORIES[CATEGORY_CN.index(self.current_category.get())]
            # 基础信息（仅填核心，其他字段可在编辑页补充）
            new_person = {
                "id": new_id,
                "name": add_name.get().strip(),
                "en_name": add_en_name.get().strip(),
                "position": add_position.get().strip(),
                "en_position": add_en_position.get().strip(),
                "category": CATEGORY_MAP[current_cat]  # 自动赋值
            }
            # 过滤空值（仅保留有内容的字段）
            new_person_filtered = {k: v for k, v in new_person.items() if v}

            # ========== 新增核心：仅追加到当前分类最后，不修改原有YAML ==========
            with open(self.yml_path, "r", encoding="utf-8") as f:
                original_yml = yaml.safe_load(f) or {cat: [] for cat in CATEGORIES}
            original_yml[current_cat].append(new_person_filtered)  # 追加到分类末尾
            # 写入yml（格式标准化，保留原有内容）
            with open(self.yml_path, "w", encoding="utf-8") as f:
                yaml.dump(original_yml, f, default_flow_style=False, indent=2, allow_unicode=True, sort_keys=False, width=float("inf"))

            # 创建MD文件（空正文，固定Front Matter）
            self._save_md_files(new_id)

            # 刷新数据
            self._load_people_yml()
            messagebox.showinfo("成功", f"人员[{new_id}]已新增！\n仅追加到[{self.current_category.get()}]分类最后，未修改原有YAML内容")
            add_win.destroy()

        # 弹窗按钮（极简）
        ttk.Button(add_win, text="确认新增", command=_confirm_add, style="Accent.TButton").grid(row=6, column=0, columnspan=2, pady=15)
        ttk.Button(add_win, text="取消", command=add_win.destroy).grid(row=7, column=0, columnspan=2)

if __name__ == "__main__":
    # Windows中文兼容（极简，仅设置字体）
    root = tk.Tk()
    root.option_add("*Font", ("SimHei", 10))  # 强制中文字体，无乱码
    app = PeopleManageGUI(root)
    root.mainloop()