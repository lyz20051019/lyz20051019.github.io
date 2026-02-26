import tkinter as tk
from tkinter import filedialog, messagebox, OptionMenu
import datetime


class BibTeXEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("BibTeX条目编辑器")
        self.root.geometry("1000x600")  # 加宽窗口适配删除按钮
        
        # 核心数据存储
        self.file_path = None
        self.string_entries = []
        self.bib_entries = []
        self.selected_index = -1
        self.temp_fields = {}  # 编辑时临时字段
        self.edit_widgets = []  # 编辑窗口组件：(field_name, label, text, delete_btn, hint_label)
        self.add_widgets = []   # 添加窗口组件：同上

        self._create_widgets()

    def _create_widgets(self):
        """主窗口布局（含删除按钮区域）"""
        # 1. 文件选择区
        file_frame = tk.Frame(self.root, padx=10, pady=5)
        file_frame.pack(fill=tk.X)
        
        self.file_btn = tk.Button(file_frame, text="选择BibTeX文件", command=self._select_file)
        self.file_btn.pack(side=tk.LEFT)
        
        self.file_label = tk.Label(file_frame, text="未选择文件", fg="gray")
        self.file_label.pack(side=tk.LEFT, padx=10)

        # 2. 条目列表区（带滚动）
        list_frame = tk.Frame(self.root, padx=10, pady=5)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(list_frame, text="条目列表（类型: 标题）").pack(anchor=tk.W)
        
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.entry_listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set, width=90, height=15
        )
        scrollbar.config(command=self.entry_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.entry_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.entry_listbox.bind("<<ListboxSelect>>", self._on_list_select)

        # 3. 功能按钮区
        btn_frame = tk.Frame(self.root, padx=10, pady=5)
        btn_frame.pack(fill=tk.X)
        
        self.view_edit_btn = tk.Button(
            btn_frame, text="查看/编辑选中条目", command=self._view_edit_entry, state=tk.DISABLED
        )
        self.view_edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = tk.Button(
            btn_frame, text="删除选中条目", command=self._delete_entry, state=tk.DISABLED, fg="red"
        )
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.add_btn = tk.Button(
            btn_frame, text="添加新条目", command=self._add_entry, state=tk.DISABLED
        )
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = tk.Button(
            btn_frame, text="保存到文件", command=self._save_file, state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

    def _select_file(self):
        """选择并解析BibTeX文件"""
        path = filedialog.askopenfilename(
            title="选择BibTeX文件",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialdir="."
        )
        if not path:
            return
        
        self.file_path = path
        self.file_label.config(text=f"已选择: {path.split('/')[-1]}", fg="black")
        
        try:
            self.bib_entries = self._parse_bibtex(path)
            self._update_listbox()
            # 启用功能按钮
            self.view_edit_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
            self.add_btn.config(state=tk.NORMAL)
            self.save_btn.config(state=tk.NORMAL)
            messagebox.showinfo("成功", f"解析完成！共发现 {len(self.bib_entries)} 个条目")
        except Exception as e:
            messagebox.showerror("解析错误", f"文件解析失败: {str(e)}")

    def _parse_bibtex(self, file_path):
        """解析BibTeX文件（保留原逻辑）"""
        self.string_entries.clear()
        entries = []
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        bib_parts = [p.strip() for p in content.split("@") if p.strip()]
        for part in bib_parts:
            # 处理@string
            if part.lower().startswith("string"):
                end_brace = part.rfind("}")
                if end_brace != -1:
                    self.string_entries.append(f"@{part[:end_brace+1]}")
                continue
            
            # 处理普通条目
            type_end = part.find("{")
            if type_end == -1:
                continue
            entry_type = part[:type_end].strip()
            
            key_start = type_end + 1
            key_end = part.find(",", key_start)
            if key_end == -1:
                continue
            entry_key = part[key_start:key_end].strip()
            
            fields_content = part[key_end+1:].strip()
            if fields_content.endswith("}"):
                fields_content = fields_content[:-1].strip()
            else:
                continue
            
            # 解析字段
            fields = {}
            current_field = ""
            brace_count = 0
            for char in fields_content:
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                elif char == "," and brace_count == 0:
                    self._parse_single_field(current_field.strip(), fields)
                    current_field = ""
                    continue
                current_field += char
            if current_field.strip():
                self._parse_single_field(current_field.strip(), fields)
            
            entries.append({
                "type": entry_type,
                "key": entry_key,
                "fields": fields
            })
        
        return entries

    def _parse_single_field(self, field_str, fields):
        """解析单个字段（保留原逻辑）"""
        eq_pos = field_str.find("=")
        if eq_pos == -1:
            return
        
        field_name = field_str[:eq_pos].strip()
        field_value = field_str[eq_pos+1:].strip()
        if field_value.startswith("{") and field_value.endswith("}"):
            field_value = field_value[1:-1].strip()
        
        fields[field_name] = field_value

    def _update_listbox(self):
        """更新条目列表"""
        self.entry_listbox.delete(0, tk.END)
        for entry in self.bib_entries:
            entry_type = entry["type"]
            title = entry["fields"].get("title", "无标题")
            self.entry_listbox.insert(tk.END, f"{entry_type}: {title}")

    def _on_list_select(self, event):
        """同步按钮状态"""
        selected = self.entry_listbox.curselection()
        if selected:
            self.selected_index = selected[0]
            self.view_edit_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
        else:
            self.selected_index = -1
            self.view_edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)

    def _delete_entry(self):
        """删除选中条目（保留原逻辑）"""
        if self.selected_index < 0 or self.selected_index >= len(self.bib_entries):
            messagebox.showwarning("警告", "请先在列表中选中一个条目")
            return
        
        selected_entry = self.bib_entries[self.selected_index]
        entry_type = selected_entry["type"]
        entry_title = selected_entry["fields"].get("title", "无标题")
        confirm = messagebox.askyesno(
            "确认删除", 
            f"是否要删除以下条目？\n类型：{entry_type}\n标题：{entry_title}\n（删除后需保存生效）"
        )
        
        if confirm:
            self.bib_entries.pop(self.selected_index)
            self.selected_index = -1
            self._update_listbox()
            self.view_edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)
            messagebox.showinfo("成功", "条目已删除（暂存）！")

    # ---------------------- 核心功能1：编辑窗口支持字段删除 ----------------------
    def _view_edit_entry(self):
        """查看/编辑条目（支持删除字段）"""
        if self.selected_index < 0:
            messagebox.showwarning("警告", "请先选中条目")
            return
        
        entry = self.bib_entries[self.selected_index]
        # 补全selected字段（默认false）
        self.temp_fields = entry["fields"].copy()
        if "selected" not in self.temp_fields:
            self.temp_fields["selected"] = "false"
        
        # 编辑窗口
        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"编辑条目: {entry['type']} - {entry['key']}")
        edit_win.geometry("1000x600")
        
        # 滚动区域
        scroll_frame = tk.Frame(edit_win)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(scroll_frame)
        scrollbar = tk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
        content_frame = tk.Frame(canvas)
        
        content_frame.bind("<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.config(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 基础信息（不可编辑）
        row = 0
        tk.Label(content_frame, text="条目类型（不可编辑）:", font=("bold")).grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=2
        )
        tk.Label(content_frame, text=entry["type"]).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2
        )
        row += 1

        tk.Label(content_frame, text="条目Key（不可编辑）:", font=("bold")).grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=2
        )
        tk.Label(content_frame, text=entry["key"]).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2
        )
        row += 1

        # 字段编辑提示
        tk.Label(content_frame, text="字段编辑（点击删除按钮移除字段）:", font=("bold")).grid(
            row=row, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5
        )
        row += 1

        # 生成字段组件（含删除按钮）
        self.edit_widgets.clear()
        # selected优先显示
        sorted_fields = sorted(self.temp_fields.items(), key=lambda x: 0 if x[0] == "selected" else 1)
        
        for field_name, field_value in sorted_fields:
            # 字段标签
            field_label = tk.Label(content_frame, text=f"{field_name}:")
            field_label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            
            # 字段输入框
            hint_label = None
            if field_name == "selected":
                text_widget = tk.Text(content_frame, height=1, width=80)
                # 提示：false不写入
                hint_label = tk.Label(content_frame, text="（true=保存写入并前置，false=不写入）", fg="blue")
                hint_label.grid(row=row, column=2, sticky=tk.W, padx=5, pady=2)
            else:
                text_widget = tk.Text(content_frame, height=2, width=80)
            text_widget.insert(tk.END, field_value)
            text_widget.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            
            # 删除按钮
            delete_btn = tk.Button(
                content_frame, text="删除字段", 
                command=lambda fn=field_name, r=row, pf=content_frame: self._delete_edit_field(fn, r, pf)
            )
            delete_btn.grid(row=row, column=3, sticky=tk.W, padx=5, pady=2)
            
            # 存储组件
            self.edit_widgets.append((field_name, field_label, text_widget, delete_btn, hint_label))
            row += 1

        # 添加自定义字段按钮
        tk.Button(
            content_frame, text="添加自定义字段", 
            command=lambda: self._add_custom_field("edit", content_frame, row)
        ).grid(row=row, column=0, columnspan=4, pady=5)
        row += 1

        # 保存修改
        tk.Button(
            content_frame, text="保存修改", 
            command=lambda: self._confirm_edit(edit_win, entry)
        ).grid(row=row, column=0, columnspan=4, pady=10)

    def _delete_edit_field(self, field_name, row, parent_frame):
        """删除编辑窗口中的字段"""
        # 从临时字段移除
        if field_name in self.temp_fields:
            del self.temp_fields[field_name]
        
        # 销毁组件
        to_remove = None
        for idx, (fn, label, text_wid, del_btn, hint_lab) in enumerate(self.edit_widgets):
            if fn == field_name:
                to_remove = idx
                label.destroy()
                text_wid.destroy()
                del_btn.destroy()
                if hint_lab:
                    hint_lab.destroy()
                break
        if to_remove is not None:
            self.edit_widgets.pop(to_remove)
        
        # 重新排版后续字段（行号-1）
        for (fn, label, text_wid, del_btn, hint_lab) in self.edit_widgets:
            current_row = label.grid_info()["row"]
            if current_row > row:
                new_row = current_row - 1
                label.grid(row=new_row, column=0)
                text_wid.grid(row=new_row, column=1)
                del_btn.grid(row=new_row, column=3)
                if hint_lab:
                    hint_lab.grid(row=new_row, column=2)

    # ---------------------- 核心功能2：添加窗口支持字段选择+删除 ----------------------
    def _add_entry(self):
        """添加新条目（默认加载最少字段，支持字段选择）"""
        add_win = tk.Toplevel(self.root)
        add_win.title("添加新BibTeX条目")
        add_win.geometry("1000x600")
        
        self.new_entry_data = {"type": "article", "key": "", "fields": {}}

        # 1. 类型选择
        type_frame = tk.Frame(add_win, padx=10, pady=5)
        type_frame.pack(fill=tk.X)
        
        tk.Label(type_frame, text="条目类型:").pack(side=tk.LEFT, padx=5)
        self.type_var = tk.StringVar(value="article")
        type_menu = OptionMenu(type_frame, self.type_var, "article", "book", "inproceedings")
        type_menu.pack(side=tk.LEFT, padx=5)
        self.type_var.trace("w", self._update_add_defaults)

        # 2. Key输入
        key_frame = tk.Frame(add_win, padx=10, pady=5)
        key_frame.pack(fill=tk.X)
        
        tk.Label(key_frame, text="条目Key（不可重复）:").pack(side=tk.LEFT, padx=5)
        self.key_entry = tk.Entry(key_frame, width=60)
        self.key_entry.pack(side=tk.LEFT, padx=5)
        self._update_default_key()

        # 3. 字段输入区（带滚动）
        scroll_frame = tk.Frame(add_win, padx=10, pady=5)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(scroll_frame)
        scrollbar = tk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.add_fields_frame = tk.Frame(canvas)
        
        self.add_fields_frame.bind("<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.add_fields_frame, anchor="nw")
        canvas.config(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 加载默认字段（最少字段的条目）
        self._load_add_default_fields()

        # 4. 功能按钮
        btn_frame = tk.Frame(add_win, padx=10, pady=5)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(
            btn_frame, text="添加自定义字段", 
            command=lambda: self._add_custom_field("add", self.add_fields_frame, len(self.add_widgets))
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame, text="确认添加", 
            command=lambda: self._confirm_add(add_win)
        ).pack(side=tk.LEFT, padx=5)

    def _get_all_existing_fields(self):
        """获取所有已有字段（去重，用于自定义选择）"""
        existing_fields = set()
        for entry in self.bib_entries:
            existing_fields.update(entry["fields"].keys())
        return sorted(existing_fields)  # 排序方便选择

    def _load_add_default_fields(self):
        """加载默认字段：优先文件中字段最少的条目的字段"""
        # 清空现有组件
        for widget_info in self.add_widgets:
            for widget in widget_info[1:]:
                if widget:
                    widget.destroy()
        self.add_widgets.clear()
        
        # 1. 找字段最少的条目
        default_field_names = []
        if self.bib_entries:
            # 字段数最少的条目
            min_field_entry = min(self.bib_entries, key=lambda x: len(x["fields"]))
            # 提取字段（加selected）
            default_field_names = ["selected"] + sorted(min_field_entry["fields"].keys())
        else:
            # 无条目时用基础字段
            base_fields = {"article": ["title", "author", "journal", "year"], 
                           "book": ["title", "author", "publisher", "year"],
                           "default": ["title", "author", "year"]}
            use_type = self.type_var.get().lower()
            default_field_names = ["selected"] + base_fields.get(use_type, base_fields["default"])
        
        # 生成字段组件
        row = 0
        for field_name in default_field_names:
            # 标签
            field_label = tk.Label(self.add_fields_frame, text=f"{field_name}:")
            field_label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            
            # 输入框
            hint_label = None
            if field_name == "selected":
                text_widget = tk.Text(self.add_fields_frame, height=1, width=80)
                text_widget.insert(tk.END, "false")  # 默认false
                hint_label = tk.Label(self.add_fields_frame, text="（true=保存写入，false=不写入）", fg="blue")
                hint_label.grid(row=row, column=2, sticky=tk.W, padx=5, pady=2)
            else:
                text_widget = tk.Text(self.add_fields_frame, height=2, width=80)
            
            text_widget.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            
            # 删除按钮
            delete_btn = tk.Button(
                self.add_fields_frame, text="删除字段", 
                command=lambda fn=field_name, r=row, pf=self.add_fields_frame: self._delete_add_field(fn, r, pf)
            )
            delete_btn.grid(row=row, column=3, sticky=tk.W, padx=5, pady=2)
            
            # 存储组件
            self.add_widgets.append((field_name, field_label, text_widget, delete_btn, hint_label))
            row += 1

    def _delete_add_field(self, field_name, row, parent_frame):
        """删除添加窗口中的字段"""
        # 销毁组件
        to_remove = None
        for idx, (fn, label, text_wid, del_btn, hint_lab) in enumerate(self.add_widgets):
            if fn == field_name:
                to_remove = idx
                label.destroy()
                text_wid.destroy()
                del_btn.destroy()
                if hint_lab:
                    hint_lab.destroy()
                break
        if to_remove is not None:
            self.add_widgets.pop(to_remove)
        
        # 重新排版
        for (fn, label, text_wid, del_btn, hint_lab) in self.add_widgets:
            current_row = label.grid_info()["row"]
            if current_row > row:
                new_row = current_row - 1
                label.grid(row=new_row, column=0)
                text_wid.grid(row=new_row, column=1)
                del_btn.grid(row=new_row, column=3)
                if hint_lab:
                    hint_lab.grid(row=new_row, column=2)

    def _add_custom_field(self, win_type, parent_frame, start_row):
        """添加自定义字段：从已有字段选择或手动输入"""
        # 弹窗
        custom_win = tk.Toplevel(self.root)
        custom_win.title("添加自定义字段")
        custom_win.geometry("550x220")
        
        # 变量
        field_choice_var = tk.StringVar()
        custom_name_var = tk.StringVar()
        
        # 1. 已有字段下拉菜单
        tk.Label(custom_win, text="选择已有字段或自定义：").pack(padx=10, pady=8, anchor=tk.W)
        existing_fields = self._get_all_existing_fields()
        choices = existing_fields + ["自定义字段（手动输入）"]
        field_choice_var.set(choices[0] if choices else "自定义字段（手动输入）")
        field_menu = OptionMenu(custom_win, field_choice_var, *choices)
        field_menu.pack(padx=10, pady=2, fill=tk.X)
        
        # 2. 自定义字段名输入框（默认隐藏）
        custom_frame = tk.Frame(custom_win)
        tk.Label(custom_frame, text="自定义字段名：").pack(side=tk.LEFT, padx=5)
        custom_entry = tk.Entry(custom_frame, textvariable=custom_name_var, width=40)
        custom_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 显示/隐藏输入框
        def toggle_custom_entry(*args):
            if field_choice_var.get() == "自定义字段（手动输入）":
                custom_frame.pack(padx=10, pady=8, fill=tk.X)
            else:
                custom_frame.pack_forget()
        
        field_choice_var.trace("w", toggle_custom_entry)

        # 3. 确认添加
        def confirm_field():
            choice = field_choice_var.get()
            # 确定字段名
            if choice == "自定义字段（手动输入）":
                field_name = custom_name_var.get().strip()
                if not field_name:
                    messagebox.showwarning("警告", "自定义字段名不能为空！")
                    return
            else:
                field_name = choice  # 选择已有字段
            
            # 检查重复
            if win_type == "edit":
                if field_name in self.temp_fields:
                    messagebox.showinfo("提示", f"字段「{field_name}」已存在！")
                    custom_win.destroy()
                    return
            else:
                for (fn, _, _, _, _) in self.add_widgets:
                    if fn == field_name:
                        messagebox.showinfo("提示", f"字段「{field_name}」已存在！")
                        custom_win.destroy()
                        return
            
            # 添加到对应窗口
            row = start_row if win_type == "add" else len(self.edit_widgets)
            # 标签
            field_label = tk.Label(parent_frame, text=f"{field_name}:")
            field_label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            # 输入框
            text_widget = tk.Text(parent_frame, height=2, width=80)
            text_widget.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            # 删除按钮
            delete_btn = tk.Button(
                parent_frame, text="删除字段",
                command=lambda fn=field_name, r=row, pf=parent_frame, wt=win_type: 
                    self._delete_edit_field(fn, r, pf) if wt == "edit" else self._delete_add_field(fn, r, pf)
            )
            delete_btn.grid(row=row, column=3, sticky=tk.W, padx=5, pady=2)
            
            # 存储组件
            if win_type == "edit":
                self.temp_fields[field_name] = ""  # 初始化空值
                self.edit_widgets.append((field_name, field_label, text_widget, delete_btn, None))
            else:
                self.add_widgets.append((field_name, field_label, text_widget, delete_btn, None))
            
            custom_win.destroy()
        
        tk.Button(custom_win, text="确认添加", command=confirm_field).pack(padx=10, pady=10)

    def _update_default_key(self):
        """生成默认Key"""
        current_type = self.type_var.get().lower()
        current_year = datetime.datetime.now().year
        default_key = f"user{current_year}{current_type}"
        self.key_entry.delete(0, tk.END)
        self.key_entry.insert(tk.END, default_key)

    def _update_add_defaults(self, *args):
        """类型变化时更新默认Key和字段"""
        self._update_default_key()
        self._load_add_default_fields()

    def _confirm_edit(self, edit_win, original_entry):
        """确认编辑修改"""
        # 收集字段值
        for (field_name, _, text_wid, _, _) in self.edit_widgets:
            value = text_wid.get("1.0", tk.END).strip()
            self.temp_fields[field_name] = value
        
        # 更新原条目
        original_entry["fields"] = self.temp_fields.copy()
        edit_win.destroy()
        self._update_listbox()
        messagebox.showinfo("成功", "条目修改已暂存！")

    def _confirm_add(self, add_win):
        """确认添加新条目"""
        # 基础校验
        entry_type = self.type_var.get().strip()
        entry_key = self.key_entry.get().strip()
        if not entry_type or not entry_key:
            messagebox.showwarning("警告", "类型和Key不能为空！")
            return
        
        # Key唯一性
        for entry in self.bib_entries:
            if entry["key"] == entry_key:
                messagebox.showwarning("警告", f"Key「{entry_key}」已存在！")
                return
        
        # 收集字段
        fields = {}
        for (field_name, _, text_wid, _, _) in self.add_widgets:
            value = text_wid.get("1.0", tk.END).strip()
            fields[field_name] = value
        
        # 添加条目
        self.bib_entries.append({
            "type": entry_type,
            "key": entry_key,
            "fields": fields
        })
        
        add_win.destroy()
        self._update_listbox()
        messagebox.showinfo("成功", "新条目已暂存！")

    # ---------------------- 核心功能3：selected=false不写入，true前置 ----------------------
    def _save_file(self):
        """保存文件：selected=false不写入，true前置"""
        if not self.file_path:
            messagebox.showwarning("警告", "未选择文件！")
            return
        
        # 1. 排序：selected=true在前（无selected视为false）
        selected_entries = []
        other_entries = []
        for entry in self.bib_entries:
            selected_val = entry["fields"].get("selected", "false").strip().lower()
            if selected_val == "true":
                selected_entries.append(entry)
            else:
                other_entries.append(entry)
        sorted_entries = selected_entries + other_entries

        # 2. 生成文件内容
        bib_content = []
        # 添加@string
        if self.string_entries:
            bib_content.extend(self.string_entries)
            bib_content.append("")
        
        # 添加条目（selected=false不写入）
        for entry in sorted_entries:
            entry_lines = [f"@{entry['type']}{{{entry['key']},"]
            # 字段排序：selected优先（仅true时写入）
            sorted_fields = sorted(entry["fields"].items(), key=lambda x: 0 if x[0] == "selected" else 1)
            for field_name, field_value in sorted_fields:
                # selected=false不写入
                if field_name == "selected":
                    if field_value.strip().lower() != "true":
                        continue
                # 其他字段写入
                entry_lines.append(f"  {field_name} = {{{field_value}}}")
            entry_lines.append("}")
            bib_content.append(",\n".join(entry_lines))
            bib_content.append("")
        
        # 3. 写入文件
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(bib_content).strip())
            messagebox.showinfo("成功", f"已保存到：\n{self.file_path}")
        except Exception as e:
            messagebox.showerror("保存错误", f"写入失败: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BibTeXEditor(root)
    root.mainloop()