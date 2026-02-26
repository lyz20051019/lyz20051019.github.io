import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path

class PeopleManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Al-Folio 团队成员管理工具（最终版）")
        self.root.geometry("1100x680")
        
        # 项目根目录和标准路径（符合al-folio规范）
        self.project_root = None
        self.assets_img_dir = "assets/img"  # al-folio标准图片目录
        
        # 设置中文字体支持
        self.style = ttk.Style()
        self.style.configure(".", font=("SimHei", 10))
        
        # 成员数据
        self.people_files = {"en-us": None, "zh-cn": None}  # 多语言people.md文件
        self.people_data = []
        self.current_person = None
        self.people_dir = "_people"
        self.lang_dirs = ["en-us", "zh-cn"]
        self.unsaved_changes = False  # 跟踪未保存的更改
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 项目根目录选择区
        root_frame = ttk.Frame(main_frame, padding="5")
        root_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(root_frame, text="项目根目录:").pack(side=tk.LEFT, padx=5)
        self.root_path_var = tk.StringVar(value="未选择")
        ttk.Label(root_frame, textvariable=self.root_path_var, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(root_frame, text="选择根目录", command=self.select_project_root).pack(side=tk.LEFT, padx=5)
        ttk.Label(root_frame, text="(请选择al-folio项目根目录)", font=("SimHei", 9)).pack(side=tk.LEFT, padx=5)
        
        # 顶部控制区
        control_frame = ttk.Frame(main_frame, padding="5")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 多语言文件选择
        lang_frame = ttk.LabelFrame(control_frame, text="选择people.md文件", padding="5")
        lang_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(lang_frame, text="选择英文版本", command=lambda: self.select_people_file("en-us")).pack(side=tk.LEFT, padx=5)
        ttk.Button(lang_frame, text="选择中文版本", command=lambda: self.select_people_file("zh-cn")).pack(side=tk.LEFT, padx=5)
        
        # 状态显示
        self.file_status_var = tk.StringVar(value="未选择文件")
        ttk.Label(control_frame, textvariable=self.file_status_var).pack(side=tk.LEFT, padx=20)
        
        # 其他控制按钮
        ttk.Button(control_frame, text="刷新成员列表", command=self.refresh_people_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="添加新成员", command=self.add_new_person).pack(side=tk.LEFT, padx=5)
        
        # 未保存提示
        self.unsaved_var = tk.StringVar(value="")
        ttk.Label(control_frame, textvariable=self.unsaved_var, foreground="red").pack(side=tk.RIGHT, padx=20)
        
        # 中间分割面板
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 左侧成员列表
        left_frame = ttk.Frame(paned_window, width=300)
        paned_window.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="团队成员列表", font=("SimHei", 12, "bold")).pack(pady=5)
        
        self.people_listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE, font=("SimHei", 10))
        self.people_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.people_listbox.bind('<<ListboxSelect>>', self.on_person_select)
        
        # 右侧详情编辑区
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=3)
        
        # 详情编辑区标题
        self.detail_title = ttk.Label(right_frame, text="请选择一个成员查看详情", font=("SimHei", 12, "bold"))
        self.detail_title.pack(pady=10)
        
        # 详情编辑面板
        self.detail_frame = ttk.Frame(right_frame, padding="10")
        self.detail_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建详情编辑控件
        self.create_detail_widgets()
        
        # 底部按钮区 - 突出显示保存按钮
        btn_frame = ttk.Frame(right_frame, padding="10")
        btn_frame.pack(fill=tk.X)
        
        # 保存按钮使用不同样式突出显示
        save_btn = ttk.Button(btn_frame, text="💾 保存修改", command=self.save_person_details)
        save_btn.pack(side=tk.RIGHT, padx=10)
        ttk.Button(btn_frame, text="删除成员", command=self.delete_person).pack(side=tk.RIGHT, padx=5)
        
        # 绑定文本修改事件，跟踪未保存的更改
        self.bind_change_events()
    
    def bind_change_events(self):
        """绑定所有输入控件的修改事件，跟踪未保存的更改"""
        def mark_unsaved(event=None):
            self.unsaved_changes = True
            self.unsaved_var.set("有未保存的更改")
        
        # 绑定所有输入控件
        self.name_en_var.trace_add("write", lambda *args: mark_unsaved())
        self.name_zh_var.trace_add("write", lambda *args: mark_unsaved())
        self.permalink_var.trace_add("write", lambda *args: mark_unsaved())
        self.avatar_var.trace_add("write", lambda *args: mark_unsaved())
        self.email_var.trace_add("write", lambda *args: mark_unsaved())
        self.avatar_shape_var.trace_add("write", lambda *args: mark_unsaved())
        self.position_en_var.trace_add("write", lambda *args: mark_unsaved())
        self.position_zh_var.trace_add("write", lambda *args: mark_unsaved())
        self.research_en_var.trace_add("write", lambda *args: mark_unsaved())
        self.research_zh_var.trace_add("write", lambda *args: mark_unsaved())
        self.bio_en_text.bind("<KeyRelease>", mark_unsaved)
        self.bio_zh_text.bind("<KeyRelease>", mark_unsaved)
    
    def create_detail_widgets(self):
        # 表单框架
        form_frame = ttk.Frame(self.detail_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 姓名（双语）
        name_frame = ttk.LabelFrame(form_frame, text="姓名（双语）", padding="10")
        name_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(name_frame, text="英文:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_en_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_en_var, width=50).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(name_frame, text="中文:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=10)
        self.name_zh_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_zh_var, width=50).grid(row=0, column=3, sticky=tk.W, pady=5)
        
        # 基本信息（双语同步）
        basic_frame = ttk.LabelFrame(form_frame, text="基本信息（双语同步）", padding="10")
        basic_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 永久链接
        ttk.Label(basic_frame, text="Permalink:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.permalink_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.permalink_var, width=50).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 头像 - 符合al-folio规范
        ttk.Label(basic_frame, text="头像路径:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.avatar_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.avatar_var, width=50).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 浏览按钮使用grid而非pack，解决布局冲突
        ttk.Button(basic_frame, text="浏览...", command=self.browse_avatar).grid(row=1, column=2, padx=5, pady=5)
        
        # 显示当前路径类型（相对/绝对）
        self.avatar_path_type = tk.StringVar(value="")
        ttk.Label(basic_frame, textvariable=self.avatar_path_type, font=("SimHei", 9)).grid(row=1, column=3, sticky=tk.W, pady=5)
        ttk.Label(basic_frame, text=f"（建议放在{self.assets_img_dir}目录下）", font=("SimHei", 9)).grid(row=1, column=4, sticky=tk.W, pady=5)
        
        # 邮箱
        ttk.Label(basic_frame, text="邮箱:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.email_var, width=50).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 头像形状选择
        ttk.Label(basic_frame, text="头像形状:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.avatar_shape_var = tk.StringVar(value="circle")  # 默认圆形
        
        shape_frame = ttk.Frame(basic_frame)
        shape_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(shape_frame, text="圆形", variable=self.avatar_shape_var, value="circle").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(shape_frame, text="方形", variable=self.avatar_shape_var, value="square").pack(side=tk.LEFT, padx=10)
        
        # 职位（双语）
        position_frame = ttk.LabelFrame(form_frame, text="职位", padding="10")
        position_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(position_frame, text="英文:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.position_en_var = tk.StringVar()
        ttk.Entry(position_frame, textvariable=self.position_en_var, width=50).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(position_frame, text="中文:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=10)
        self.position_zh_var = tk.StringVar()
        ttk.Entry(position_frame, textvariable=self.position_zh_var, width=50).grid(row=0, column=3, sticky=tk.W, pady=5)
        
        # 研究兴趣（双语）
        research_frame = ttk.LabelFrame(form_frame, text="研究兴趣", padding="10")
        research_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(research_frame, text="英文:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.research_en_var = tk.StringVar()
        ttk.Entry(research_frame, textvariable=self.research_en_var, width=50).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(research_frame, text="中文:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=10)
        self.research_zh_var = tk.StringVar()
        ttk.Entry(research_frame, textvariable=self.research_zh_var, width=50).grid(row=0, column=3, sticky=tk.W, pady=5)
        
        # 个人简介（双语）
        bio_frame = ttk.LabelFrame(form_frame, text="个人简介", padding="10")
        bio_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(bio_frame, text="英文:").grid(row=0, column=0, sticky=tk.NW, pady=5)
        self.bio_en_text = scrolledtext.ScrolledText(bio_frame, width=50, height=10, wrap=tk.WORD)
        self.bio_en_text.grid(row=0, column=1, sticky=tk.NSEW, pady=5)
        
        ttk.Label(bio_frame, text="中文:").grid(row=0, column=2, sticky=tk.NW, pady=5, padx=10)
        self.bio_zh_text = scrolledtext.ScrolledText(bio_frame, width=50, height=10, wrap=tk.WORD)
        self.bio_zh_text.grid(row=0, column=3, sticky=tk.NSEW, pady=5)
        
        # 配置权重，使文本框可以伸缩
        bio_frame.grid_rowconfigure(0, weight=1)
        bio_frame.grid_columnconfigure(1, weight=1)
        bio_frame.grid_columnconfigure(3, weight=1)
    
    def select_project_root(self):
        """选择项目根目录，用于计算相对路径"""
        root_dir = filedialog.askdirectory(title="选择al-folio项目根目录")
        if root_dir:
            self.project_root = root_dir
            self.root_path_var.set(os.path.basename(root_dir) + " (" + root_dir + ")")
            
            # 检查标准图片目录是否存在，不存在则创建
            assets_img_path = os.path.join(self.project_root, self.assets_img_dir)
            if not os.path.exists(assets_img_path):
                os.makedirs(assets_img_path)
                messagebox.showinfo("提示", f"已创建标准图片目录: {self.assets_img_dir}")
            
            # 检查people目录是否存在
            people_path = os.path.join(self.project_root, self.people_dir)
            if not os.path.exists(people_path):
                os.makedirs(people_path)
                for lang in self.lang_dirs:
                    os.makedirs(os.path.join(people_path, lang), exist_ok=True)
                messagebox.showinfo("提示", f"已创建成员目录结构: {self.people_dir}")
    
    def select_people_file(self, lang):
        """选择特定语言的people.md文件"""
        # 如果已设置项目根目录，从那里开始浏览
        initial_dir = self.project_root if self.project_root else None
        
        file_path = filedialog.askopenfilename(
            title=f"选择{lang}版本的people.md文件",
            filetypes=[("Markdown文件", "*.md"), ("所有文件", "*.*")],
            initialdir=initial_dir
        )
        
        if file_path:
            self.people_files[lang] = file_path
            
            # 如果未设置项目根目录，尝试从people.md文件路径推断
            if not self.project_root:
                self.project_root = os.path.dirname(file_path)
                self.root_path_var.set(os.path.basename(self.project_root) + " (" + self.project_root + ")")
                
            self.update_file_status()
            messagebox.showinfo("成功", f"已选择{lang}文件: {os.path.basename(file_path)}")
    
    def update_file_status(self):
        """更新文件选择状态显示"""
        status_parts = []
        for lang, path in self.people_files.items():
            if path:
                # 显示相对路径（如果可能）
                if self.project_root:
                    rel_path = os.path.relpath(path, self.project_root)
                    status_parts.append(f"{lang}: {rel_path}")
                else:
                    status_parts.append(f"{lang}: {os.path.basename(path)}")
        
        if status_parts:
            self.file_status_var.set("; ".join(status_parts))
        else:
            self.file_status_var.set("未选择文件")
    
    def get_relative_path(self, absolute_path):
        """将绝对路径转换为相对于项目根目录的相对路径，符合al-folio规范"""
        if not self.project_root:
            messagebox.showwarning("警告", "未设置项目根目录，将使用绝对路径")
            return absolute_path
            
        try:
            rel_path = os.path.relpath(absolute_path, self.project_root)
            # 确保路径使用正斜杠，符合web规范
            return rel_path.replace(os.sep, '/')
        except ValueError:
            # 路径不在项目目录下，提示用户移动文件
            messagebox.showwarning("警告", f"文件不在项目目录下，建议移动到{self.assets_img_dir}目录")
            return absolute_path.replace(os.sep, '/')
    
    def is_relative_path(self, path):
        """检查路径是否为相对路径"""
        return not os.path.isabs(path)
    
    def refresh_people_list(self):
        """刷新成员列表"""
        # 检查是否至少选择了一个语言版本的文件
        if not any(self.people_files.values()):
            messagebox.showerror("错误", "请先选择至少一个语言版本的people.md文件")
            return
        
        # 清空列表
        self.people_listbox.delete(0, tk.END)
        self.people_data = []
        
        # 选择一个已存在的文件进行解析（优先英文）
        parse_lang = "en-us" if self.people_files["en-us"] else "zh-cn"
        file_path = self.people_files[parse_lang]
        
        # 解析people.md文件，提取成员信息
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 查找所有成员链接，格式如：[姓名](/people/xxx/)
                # 考虑可能包含图片的情况
                pattern = r'!\[.*?\]\((.*?)\)\s*\[([^]]+)\]\((/people/[^)]+)\)'
                matches = re.findall(pattern, content)
                
                # 如果没找到带图片的链接，尝试找普通链接
                if not matches:
                    pattern = r'\[(.*?)\]\((/people/.*?/)\)'
                    link_matches = re.findall(pattern, content)
                    # 转换格式以保持一致性
                    matches = [("", name, permalink) for name, permalink in link_matches]
                
                for img_path, name, permalink in matches:
                    # 尝试加载成员详细信息
                    person_data = self.load_person_data(permalink)
                    self.people_data.append({
                        'name': {parse_lang: name},
                        'permalink': permalink,
                        'avatar': img_path,
                        'data': person_data
                    })
                    self.people_listbox.insert(tk.END, name)
        
        except Exception as e:
            messagebox.showerror("错误", f"解析文件时出错: {str(e)}")
            print(f"解析错误详情: {e}")
    
    def load_person_data(self, permalink):
        """加载成员的详细信息"""
        # 从permalink提取文件名，如从/people/zhangsan/提取zhangsan
        person_id = permalink.strip('/').split('/')[-1]
        data = {'en-us': {}, 'zh-cn': {}}
        
        for lang in self.lang_dirs:
            # 构建文件路径（使用相对路径）
            if self.project_root:
                file_path = os.path.join(self.project_root, self.people_dir, lang, f"{person_id}.md")
            else:
                file_path = os.path.join(self.people_dir, lang, f"{person_id}.md")
                
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # 解析front matter
                        front_matter = {}
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 2:
                                for line in parts[1].split('\n'):
                                    line = line.strip()
                                    if ':' in line:
                                        key, value = line.split(':', 1)
                                        front_matter[key.strip()] = value.strip().strip('"').strip("'")
                        
                        # 处理头像路径（如果是相对路径，显示时补充说明）
                        if 'avatar' in front_matter and self.project_root:
                            avatar_path = front_matter['avatar']
                            if not os.path.isabs(avatar_path):
                                front_matter['avatar_abs'] = os.path.join(self.project_root, avatar_path)
                        
                        # 提取正文内容
                        bio = parts[2].strip() if len(parts) >= 3 else ''
                        
                        data[lang] = {
                            'front_matter': front_matter,
                            'bio': bio,
                            'avatar_shape': front_matter.get('avatar_shape', 'circle')  # 默认为圆形
                        }
                except Exception as e:
                    print(f"加载{lang}文件出错: {str(e)}")
        
        return data
    
    def on_person_select(self, event):
        """当选择成员时，显示其详情"""
        # 检查是否有未保存的更改
        if self.unsaved_changes:
            confirm = messagebox.askyesnocancel("未保存的更改", "有未保存的更改，是否保存？")
            if confirm is None:  # 取消操作
                return
            if confirm:  # 保存更改
                self.save_person_details()
        
        selection = self.people_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        self.current_person = self.people_data[index]
        
        # 更新标题
        display_name = self.current_person['name'].get('en-us', '') or self.current_person['name'].get('zh-cn', '')
        self.detail_title.config(text=f"编辑成员: {display_name}")
        
        # 填充表单
        person_id = self.current_person['permalink'].strip('/').split('/')[-1]
        self.permalink_var.set(self.current_person['permalink'])
        
        # 加载双语数据
        en_data = self.current_person['data']['en-us'].get('front_matter', {})
        zh_data = self.current_person['data']['zh-cn'].get('front_matter', {})
        
        # 姓名（双语）
        self.name_en_var.set(en_data.get('name', ''))
        self.name_zh_var.set(zh_data.get('name', ''))
        
        # 同步字段 - 优先使用front matter中的头像路径
        avatar_path = en_data.get('avatar', zh_data.get('avatar', self.current_person.get('avatar', '')))
        self.avatar_var.set(avatar_path)
        
        # 显示头像路径类型
        if self.is_relative_path(avatar_path):
            self.avatar_path_type.set("(相对路径)")
        else:
            self.avatar_path_type.set("(绝对路径)")
        
        self.email_var.set(en_data.get('email', zh_data.get('email', '')))
        self.avatar_shape_var.set(en_data.get('avatar_shape', zh_data.get('avatar_shape', 'circle')))
        
        # 英文信息
        self.position_en_var.set(en_data.get('position', ''))
        self.research_en_var.set(en_data.get('research_interests', ''))
        self.bio_en_text.delete(1.0, tk.END)
        self.bio_en_text.insert(tk.END, self.current_person['data']['en-us'].get('bio', ''))
        
        # 中文信息
        self.position_zh_var.set(zh_data.get('position', ''))
        self.research_zh_var.set(zh_data.get('research_interests', ''))
        self.bio_zh_text.delete(1.0, tk.END)
        self.bio_zh_text.insert(tk.END, self.current_person['data']['zh-cn'].get('bio', ''))
        
        # 重置未保存状态
        self.unsaved_changes = False
        self.unsaved_var.set("")
    
    def browse_avatar(self):
        """浏览选择头像文件，并自动转换为符合al-folio规范的相对路径"""
        # 从标准图片目录开始浏览
        if self.project_root:
            initial_dir = os.path.join(self.project_root, self.assets_img_dir)
            if not os.path.exists(initial_dir):
                os.makedirs(initial_dir)
        else:
            initial_dir = None
        
        file_path = filedialog.askopenfilename(
            title="选择头像图片",
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.gif"), ("所有文件", "*.*")],
            initialdir=initial_dir
        )
        
        if file_path:
            # 转换为相对路径
            rel_path = self.get_relative_path(file_path)
            self.avatar_var.set(rel_path)
            
            # 显示路径类型
            if self.is_relative_path(rel_path):
                self.avatar_path_type.set("(相对路径)")
            else:
                self.avatar_path_type.set("(绝对路径)")
    
    def save_person_details(self):
        """保存成员详情修改，符合al-folio规范"""
        if not self.current_person:
            messagebox.showwarning("警告", "请先选择一个成员")
            return
        
        try:
            # 获取表单数据
            name_en = self.name_en_var.get()
            name_zh = self.name_zh_var.get()
            permalink = self.permalink_var.get()
            avatar = self.avatar_var.get()
            email = self.email_var.get()
            avatar_shape = self.avatar_shape_var.get()
            
            # 确保头像路径是相对路径（如果可能）
            if os.path.isabs(avatar) and self.project_root:
                avatar = self.get_relative_path(avatar)
                self.avatar_var.set(avatar)
            
            # 从permalink提取原ID和新ID
            old_person_id = self.current_person['permalink'].strip('/').split('/')[-1]
            new_person_id = permalink.strip('/').split('/')[-1]
            
            # 保存双语文件
            for lang in self.lang_dirs:
                # 构建文件路径（使用项目根目录）
                if self.project_root:
                    lang_dir = os.path.join(self.project_root, self.people_dir, lang)
                else:
                    lang_dir = os.path.join(self.people_dir, lang)
                    
                os.makedirs(lang_dir, exist_ok=True)
                
                # 构建文件路径
                old_file_path = os.path.join(lang_dir, f"{old_person_id}.md")
                new_file_path = os.path.join(lang_dir, f"{new_person_id}.md")
                
                # 如果ID变了，删除旧文件
                if old_person_id != new_person_id and os.path.exists(old_file_path):
                    os.remove(old_file_path)
                
                # 准备front matter数据（符合al-folio规范）
                front_matter = {
                    'name': name_en if lang == 'en-us' else name_zh,
                    'permalink': permalink,
                    'avatar': avatar,
                    'email': email,
                    'avatar_shape': avatar_shape
                }
                
                # 设置职位和研究兴趣（根据语言）
                if lang == 'en-us':
                    front_matter['position'] = self.position_en_var.get()
                    front_matter['research_interests'] = self.research_en_var.get()
                    bio = self.bio_en_text.get(1.0, tk.END).strip()
                else:  # zh-cn
                    front_matter['position'] = self.position_zh_var.get()
                    front_matter['research_interests'] = self.research_zh_var.get()
                    bio = self.bio_zh_text.get(1.0, tk.END).strip()
                
                # 写入文件
                with open(new_file_path, 'w', encoding='utf-8') as f:
                    # 写入front matter
                    f.write('---\n')
                    for key, value in front_matter.items():
                        if value:  # 只写入有值的字段
                            # 处理特殊字符
                            value = value.replace(':', '\\:').replace('#', '\\#')
                            f.write(f"{key}: {value}\n")
                    f.write('---\n\n')
                    
                    # 写入正文
                    f.write(bio)
            
            # 更新多语言people.md文件中的链接和头像（符合al-folio规范）
            for lang in self.lang_dirs:
                if self.people_files[lang] and os.path.exists(self.people_files[lang]):
                    with open(self.people_files[lang], 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 获取当前语言对应的姓名
                    current_name = name_en if lang == 'en-us' else name_zh
                    old_name = self.current_person['name'].get(lang, '')
                    old_permalink = self.current_person['permalink']
                    
                    # 安全处理特殊字符，避免正则表达式错误
                    try:
                        # 转义所有特殊字符
                        escaped_old_name = re.escape(old_name)
                        escaped_old_permalink = re.escape(old_permalink)
                        
                        # 构建正则表达式模式（避免使用rf字符串）
                        # 带图片的模式
                        pattern_with_img = r'!\[.*?\]\(.*?\)\s*\[' + escaped_old_name + r'\]\(' + escaped_old_permalink + r'\)'
                        # 不带图片的模式
                        pattern_without_img = r'\[' + escaped_old_name + r'\]\(' + escaped_old_permalink + r'\)'
                        
                        # 新的带图片的链接格式（符合al-folio规范）
                        # 头像alt文本使用"Profile picture of 姓名"格式
                        alt_text = f"Profile picture of {current_name}"
                        new_link = f'![{alt_text}]({avatar}) [{current_name}]({permalink})'
                        
                        # 先替换带图片的模式
                        new_content = re.sub(pattern_with_img, new_link, content)
                        # 再替换不带图片的模式
                        new_content = re.sub(pattern_without_img, new_link, new_content)
                        
                        with open(self.people_files[lang], 'w', encoding='utf-8') as f:
                            f.write(new_content)
                            
                    except re.error as e:
                        # 捕获正则表达式错误并提供详细信息
                        messagebox.showerror("正则表达式错误", f"处理{current_name}时出现错误: {str(e)}\n请检查是否有特殊字符")
                        print(f"正则错误详情: {e}，名称: {old_name}，链接: {old_permalink}")
                        continue
            
            # 更新当前数据并刷新列表
            self.current_person['name']['en-us'] = name_en
            self.current_person['name']['zh-cn'] = name_zh
            self.current_person['permalink'] = permalink
            self.current_person['avatar'] = avatar
            self.refresh_people_list()
            
            # 更新未保存状态
            self.unsaved_changes = False
            self.unsaved_var.set("")
            
            messagebox.showinfo("成功", "成员信息已保存，符合al-folio规范")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存时出错: {str(e)}")
            print(f"保存错误详情: {e}")
    
    def add_new_person(self):
        """添加新成员"""
        # 检查是否有未保存的更改
        if self.unsaved_changes:
            confirm = messagebox.askyesnocancel("未保存的更改", "有未保存的更改，是否保存？")
            if confirm is None:  # 取消操作
                return
            if confirm:  # 保存更改
                self.save_person_details()
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加新成员")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 姓名（双语）
        name_frame = ttk.LabelFrame(dialog, text="姓名", padding="5")
        name_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(name_frame, text="英文:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        name_en_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=name_en_var, width=30).grid(row=0, column=1, pady=5)
        
        ttk.Label(name_frame, text="中文:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        name_zh_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=name_zh_var, width=30).grid(row=1, column=1, pady=5)
        
        # permalink
        permalink_frame = ttk.LabelFrame(dialog, text="基本信息", padding="5")
        permalink_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(permalink_frame, text="Permalink:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        permalink_var = tk.StringVar(value="/people/new-person/")
        ttk.Entry(permalink_frame, textvariable=permalink_var, width=30).grid(row=0, column=1, pady=5)
        
        # 头像形状
        ttk.Label(permalink_frame, text="头像形状:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        avatar_shape_var = tk.StringVar(value="circle")
        
        shape_frame = ttk.Frame(permalink_frame)
        shape_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(shape_frame, text="圆形", variable=avatar_shape_var, value="circle").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(shape_frame, text="方形", variable=avatar_shape_var, value="square").pack(side=tk.LEFT, padx=10)
        
        # 按钮
        def save_new():
            name_en = name_en_var.get().strip()
            name_zh = name_zh_var.get().strip()
            permalink = permalink_var.get().strip()
            avatar_shape = avatar_shape_var.get()
            
            if not (name_en or name_zh) or not permalink:
                messagebox.showwarning("警告", "姓名和Permalink不能为空")
                return
            
            # 创建空的成员文件
            person_id = permalink.strip('/').split('/')[-1]
            
            for lang in self.lang_dirs:
                # 构建文件路径（使用项目根目录）
                if self.project_root:
                    lang_dir = os.path.join(self.project_root, self.people_dir, lang)
                else:
                    lang_dir = os.path.join(self.people_dir, lang)
                    
                os.makedirs(lang_dir, exist_ok=True)
                
                file_path = os.path.join(lang_dir, f"{person_id}.md")
                
                # 写入基本内容（符合al-folio规范）
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('---\n')
                    f.write(f"name: {name_en if lang == 'en-us' else name_zh}\n")
                    f.write(f"permalink: {permalink}\n")
                    f.write("position: \n")
                    f.write("research_interests: \n")
                    f.write(f"avatar: /{self.assets_img_dir}/\n")  # 预设标准图片目录
                    f.write("email: \n")
                    f.write(f"avatar_shape: {avatar_shape}\n")
                    f.write('---\n\n')
            
            # 添加到多语言people.md文件
            for lang in self.lang_dirs:
                if self.people_files[lang] and os.path.exists(self.people_files[lang]):
                    with open(self.people_files[lang], 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 获取当前语言对应的姓名
                    current_name = name_en if lang == 'en-us' else name_zh
                    
                    # 查找成员列表的位置
                    member_header = "# 团队成员"
                    header_pos = content.find(member_header)
                    
                    # 带头像的成员链接（符合al-folio规范）
                    alt_text = f"Profile picture of {current_name}"
                    new_member_entry = f"\n- ![{alt_text}](/{self.assets_img_dir}/) [{current_name}]({permalink})"
                    
                    if header_pos != -1:
                        # 在标题后添加新成员链接
                        insert_pos = header_pos + len(member_header)
                        new_content = (
                            content[:insert_pos] + 
                            new_member_entry +
                            content[insert_pos:]
                        )
                    else:
                        # 如果找不到标题，添加到文件末尾
                        new_content = content + f"\n\n# 团队成员{new_member_entry}"
                    
                    with open(self.people_files[lang], 'w', encoding='utf-8') as f:
                        f.write(new_content)
            
            dialog.destroy()
            self.refresh_people_list()
            messagebox.showinfo("成功", f"新成员已添加，请将头像图片放入{self.assets_img_dir}目录并编辑详细信息")
        
        # 按钮布局
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=20, padx=10)
        ttk.Button(btn_frame, text="创建", command=save_new).pack(side=tk.RIGHT, padx=10)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=10)
        
        # 居中显示
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_width() // 2) - (width // 2) + self.root.winfo_x()
        y = (self.root.winfo_height() // 2) - (height // 2) + self.root.winfo_y()
        dialog.geometry(f"+{x}+{y}")
    
    def delete_person(self):
        """删除成员"""
        if not self.current_person:
            messagebox.showwarning("警告", "请先选择一个成员")
            return
        
        display_name = self.current_person['name'].get('en-us', '') or self.current_person['name'].get('zh-cn', '')
        confirm = messagebox.askyesno("确认", f"确定要删除成员 {display_name} 吗？")
        if not confirm:
            return
        
        try:
            # 删除双语文件
            person_id = self.current_person['permalink'].strip('/').split('/')[-1]
            for lang in self.lang_dirs:
                if self.project_root:
                    file_path = os.path.join(self.project_root, self.people_dir, lang, f"{person_id}.md")
                else:
                    file_path = os.path.join(self.people_dir, lang, f"{person_id}.md")
                    
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # 从多语言people.md文件中移除链接
            for lang in self.lang_dirs:
                if self.people_files[lang] and os.path.exists(self.people_files[lang]):
                    with open(self.people_files[lang], 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 获取当前语言对应的姓名和链接
                    current_name = self.current_person['name'].get(lang, '')
                    permalink = self.current_person['permalink']
                    
                    # 安全处理特殊字符
                    try:
                        escaped_name = re.escape(current_name)
                        escaped_permalink = re.escape(permalink)
                        
                        # 移除链接（考虑带图片的情况）
                        pattern = r'!\[.*?\]\(.*?\)\s*\[' + escaped_name + r'\]\(' + escaped_permalink + r'\)\s*'
                        new_content = re.sub(pattern, '', content)
                        
                        # 也尝试移除不带图片的链接
                        pattern = r'[-*]\s*\[' + escaped_name + r'\]\(' + escaped_permalink + r'\)\s*'
                        new_content = re.sub(pattern, '', new_content)
                        
                        with open(self.people_files[lang], 'w', encoding='utf-8') as f:
                            f.write(new_content)
                            
                    except re.error as e:
                        messagebox.showerror("正则表达式错误", f"删除{current_name}时出现错误: {str(e)}")
                        print(f"删除正则错误: {e}")
                        continue
            
            # 刷新列表
            self.current_person = None
            self.refresh_people_list()
            
            # 清空表单
            self.detail_title.config(text="请选择一个成员查看详情")
            self.name_en_var.set("")
            self.name_zh_var.set("")
            self.permalink_var.set("")
            self.avatar_var.set("")
            self.email_var.set("")
            self.position_en_var.set("")
            self.position_zh_var.set("")
            self.research_en_var.set("")
            self.research_zh_var.set("")
            self.bio_en_text.delete(1.0, tk.END)
            self.bio_zh_text.delete(1.0, tk.END)
            
            # 更新未保存状态
            self.unsaved_changes = False
            self.unsaved_var.set("")
            
            messagebox.showinfo("成功", "成员已删除")
            
        except Exception as e:
            messagebox.showerror("错误", f"删除时出错: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PeopleManager(root)
    root.mainloop()
