import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import os
import re

class ProfileEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Profile 编辑器")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)
        
        # 存储文件夹路径
        self.base_folder = ""
        self.en_us_folder = ""  # 英文文件夹
        self.zh_cn_folder = ""  # 中文文件夹
        self.en_profiles_path = ""
        self.zh_profiles_path = ""
        self.en_scholar_folder = ""  # 英文Scholar ID文件夹
        self.zh_scholar_folder = ""  # 中文Scholar ID文件夹
        
        # 存储当前选中的profile索引和语言
        self.current_profile_index = -1
        self.current_language = "en"  # 默认英文
        
        # 创建UI
        self.create_widgets()
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部控制区
        control_frame = ttk.Frame(main_frame, padding="5")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 选择文件夹按钮
        self.select_folder_btn = ttk.Button(control_frame, text="选择根文件夹", command=self.select_folder)
        self.select_folder_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 状态标签
        self.status_label = ttk.Label(control_frame, text="未选择文件夹")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 同步按钮 - 用于手动同步en-us和zh-cn的核心内容
        self.sync_btn = ttk.Button(control_frame, text="同步当前条目", command=self.sync_current_profile, state=tk.DISABLED)
        self.sync_btn.pack(side=tk.RIGHT, padx=(10, 10))
        
        # 保存按钮
        self.save_btn = ttk.Button(control_frame, text="保存更改", command=self.save_changes, state=tk.DISABLED)
        self.save_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 取消按钮
        self.cancel_btn = ttk.Button(control_frame, text="取消更改", command=self.cancel_changes, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.RIGHT)
        
        # 创建标签页（分别对应en-us和zh-cn文件夹）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # 创建英文和中文标签页（对应两个文件夹）
        self.en_frame = ttk.Frame(self.notebook)
        self.zh_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.en_frame, text="英文 (en-us)")
        self.notebook.add(self.zh_frame, text="中文 (zh-cn)")
        
        # 为每个标签页创建内容
        self.create_tab_content(self.en_frame, is_english=True)
        self.create_tab_content(self.zh_frame, is_english=False)
        
        # 初始化数据存储
        self.en_profiles = []  # en-us文件夹中的条目
        self.zh_profiles = []  # zh-cn文件夹中的条目
        self.original_en_profiles = []
        self.original_zh_profiles = []
    
    def create_tab_content(self, parent, is_english):
        # 创建左右分栏
        left_frame = ttk.Frame(parent, width=300)
        right_frame = ttk.Frame(parent)
        
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, pady=(0, 10), padx=(0, 10))
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 左侧：profiles列表（对应当前文件夹的条目）
        lang = "en" if is_english else "zh"
        ttk.Label(left_frame, text="Profiles 列表:").pack(anchor=tk.W)
        
        # 列表视图
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        treeview = ttk.Treeview(list_frame, yscrollcommand=scrollbar.set, columns=["id"], show="headings", height=15)
        treeview.heading("id", text="条目")
        treeview.column("id", width=250)
        treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=treeview.yview)
        
        # 绑定列表选择事件
        treeview.bind("<<TreeviewSelect>>", lambda e, lang=lang: self.on_profile_selected(e, lang))
        
        # 列表操作按钮
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        add_btn = ttk.Button(btn_frame, text="添加新条目", 
                           command=lambda lang=lang: self.add_new_profile_dialog(lang))
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        delete_btn = ttk.Button(btn_frame, text="删除选中条目", 
                              command=lambda lang=lang: self.delete_profile(lang))
        delete_btn.pack(side=tk.LEFT)
        
        # 右侧：详情编辑区
        ttk.Label(right_frame, text="条目详情:").pack(anchor=tk.W)
        
        details_frame = ttk.Frame(right_frame)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 表单布局
        form_frame = ttk.Frame(details_frame)
        form_frame.pack(fill=tk.X, padx=5)
        
        # 对齐方式
        ttk.Label(form_frame, text="对齐方式:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        align_var = tk.StringVar(value="right")
        align_frame = ttk.Frame(form_frame)
        align_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(align_frame, text="左对齐", variable=align_var, value="left").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(align_frame, text="右对齐", variable=align_var, value="right").pack(side=tk.LEFT, padx=5)
        
        # 图片名称（需要在en-us和zh-cn间同步的字段）
        ttk.Label(form_frame, text="图片名称:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        photo_entry = ttk.Entry(form_frame, width=50)
        photo_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 是否圆形图片
        circular_var = tk.BooleanVar(value=False)
        circular_check = ttk.Checkbutton(form_frame, text="圆形图片", variable=circular_var)
        circular_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5, padx=5)
        
        # 条目ID（需要在en-us和zh-cn间同步的核心字段）
        ttk.Label(form_frame, text="条目ID:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        item_id_entry = ttk.Entry(form_frame, width=50)
        item_id_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Google Scholar ID（需要在en-us和zh-cn间同步的核心字段）
        ttk.Label(form_frame, text="Google Scholar ID:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        scholar_id_entry = ttk.Entry(form_frame, width=50)
        scholar_id_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # 显示Scholar ID文件路径（新增，帮助用户确认文件位置）
        ttk.Label(form_frame, text="Scholar ID 文件:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=5)
        scholar_path_label = ttk.Label(form_frame, text="未选择条目", foreground="gray")
        scholar_path_label.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # 地址（en-us和zh-cn各自独立的字段）
        ttk.Label(form_frame, text="地址:").grid(row=6, column=0, sticky=tk.NW, pady=5, padx=5)
        address_entry = ttk.Entry(form_frame, width=50)
        address_entry.grid(row=6, column=1, sticky=tk.W, pady=5)
        
        # 邮箱（en-us和zh-cn各自独立的字段）
        ttk.Label(form_frame, text="邮箱:").grid(row=7, column=0, sticky=tk.W, pady=5, padx=5)
        email_entry = ttk.Entry(form_frame, width=50)
        email_entry.grid(row=7, column=1, sticky=tk.W, pady=5)
        
        # 电话（en-us和zh-cn各自独立的字段）
        ttk.Label(form_frame, text="电话:").grid(row=8, column=0, sticky=tk.W, pady=5, padx=5)
        phone_entry = ttk.Entry(form_frame, width=50)
        phone_entry.grid(row=8, column=1, sticky=tk.W, pady=5)
        
        # About文件内容（en-us和zh-cn各自独立的内容）
        ttk.Label(right_frame, text="About 文件内容:").pack(anchor=tk.W, pady=(10, 0))
        about_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, height=8)
        about_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 保存详情按钮
        save_detail_btn = ttk.Button(right_frame, text="保存详情", 
                                    command=lambda lang=lang: self.save_profile_details(lang))
        save_detail_btn.pack(pady=10)
        
        # 存储引用（区分en-us和zh-cn的控件）
        if is_english:
            self.en_treeview = treeview
            self.en_align_var = align_var
            self.en_photo_entry = photo_entry
            self.en_circular_var = circular_var
            self.en_item_id_entry = item_id_entry  # 条目ID
            self.en_scholar_id_entry = scholar_id_entry
            self.en_scholar_path_label = scholar_path_label  # 显示Scholar ID文件路径
            self.en_address_entry = address_entry
            self.en_email_entry = email_entry
            self.en_phone_entry = phone_entry
            self.en_about_text = about_text
        else:
            self.zh_treeview = treeview
            self.zh_align_var = align_var
            self.zh_photo_entry = photo_entry
            self.zh_circular_var = circular_var
            self.zh_item_id_entry = item_id_entry  # 条目ID
            self.zh_scholar_id_entry = scholar_id_entry
            self.zh_scholar_path_label = scholar_path_label  # 显示Scholar ID文件路径
            self.zh_address_entry = address_entry
            self.zh_email_entry = email_entry
            self.zh_phone_entry = phone_entry
            self.zh_about_text = about_text
    
    def select_folder(self):
        """选择根文件夹并初始化en-us和zh-cn文件夹路径"""
        folder = filedialog.askdirectory()
        if not folder:
            return
        
        self.base_folder = folder
        self.status_label.config(text=f"已选择: {folder}")
        
        # 定位en-us和zh-cn文件夹
        pages_folder = os.path.join(folder, "_pages")
        if not os.path.exists(pages_folder):
            messagebox.showerror("错误", "未找到_pages文件夹")
            return
        
        self.en_us_folder = os.path.join(pages_folder, "en-us")  # 英文文件夹
        self.zh_cn_folder = os.path.join(pages_folder, "zh-cn")  # 中文文件夹
        
        # 创建或获取en-us和zh-cn各自的_scholarid文件夹
        self.en_scholar_folder = os.path.join(self.en_us_folder, "_scholarid")
        self.zh_scholar_folder = os.path.join(self.zh_cn_folder, "_scholarid")
        
        # 确保两个文件夹都存在
        for folder_path in [self.en_scholar_folder, self.zh_scholar_folder]:
            try:
                os.makedirs(folder_path, exist_ok=True)
                print(f"确保文件夹存在: {folder_path}")  # 调试信息
            except Exception as e:
                messagebox.showerror("错误", f"无法创建文件夹 {folder_path}: {str(e)}")
                return
        
        # 检查en-us和zh-cn文件夹是否存在
        missing = []
        if not os.path.exists(self.en_us_folder):
            missing.append("en-us")
        if not os.path.exists(self.zh_cn_folder):
            missing.append("zh-cn")
        
        if missing:
            messagebox.showerror("错误", f"未找到以下文件夹: {', '.join(missing)}")
            return
        
        # 检查两个文件夹中的profiles.md文件
        self.en_profiles_path = os.path.join(self.en_us_folder, "profiles.md")
        self.zh_profiles_path = os.path.join(self.zh_cn_folder, "profiles.md")
        
        missing_profiles = []
        if not os.path.exists(self.en_profiles_path):
            missing_profiles.append("en-us/profiles.md")
        if not os.path.exists(self.zh_profiles_path):
            missing_profiles.append("zh-cn/profiles.md")
        
        if missing_profiles:
            messagebox.showerror("错误", f"未找到以下profiles文件: {', '.join(missing_profiles)}")
            return
        
        # 读取并解析两个文件夹中的profiles内容
        self.read_and_parse_profiles()
        
        # 启用按钮
        self.save_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.NORMAL)
        self.sync_btn.config(state=tk.NORMAL)
    
    def read_and_parse_profiles(self):
        """读取并解析en-us和zh-cn文件夹中的profiles.md内容"""
        try:
            # 读取en-us文件夹中的profiles.md
            with open(self.en_profiles_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.en_profiles = self.parse_profiles(content, "en")
                self.original_en_profiles = [p.copy() for p in self.en_profiles]
                self.populate_profiles_list("en")
            
            # 读取zh-cn文件夹中的profiles.md
            with open(self.zh_profiles_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.zh_profiles = self.parse_profiles(content, "zh")
                self.original_zh_profiles = [p.copy() for p in self.zh_profiles]
                self.populate_profiles_list("zh")
                
        except Exception as e:
            messagebox.showerror("错误", f"读取profiles.md文件时出错: {str(e)}")
    
    def parse_profiles(self, content, lang):
        """解析profiles内容，重点修复Scholar ID文件读取"""
        profiles = []
        lines = content.split('\n')
        current_profile = None
        in_more_info = False
        more_info_count = 0  # 用于跟踪more_info中的三个字段: 地址、邮箱、电话
        
        for line in lines:
            stripped_line = line.strip()
            
            # 检测新的profile开始
            if stripped_line.startswith('-') and ('align:' in stripped_line or 'image:' in stripped_line):
                if current_profile:
                    profiles.append(current_profile)
                
                current_profile = {
                    'align': 'right',
                    'image': '',
                    'content': '',
                    'image_circular': False,
                    'item_id': '',  # 条目ID
                    'google_scholar_id': '',
                    'more_info': {
                        'address': '',
                        'email': '',
                        'phone': ''
                    }
                }
                in_more_info = False
                more_info_count = 0
                
                # 提取align属性
                if 'align:' in stripped_line:
                    align_match = re.search(r'align:\s*(\w+)', stripped_line)
                    if align_match:
                        current_profile['align'] = align_match.group(1)
                
                # 提取image属性
                if 'image:' in stripped_line:
                    image_match = re.search(r'image:\s*(.+)', stripped_line)
                    if image_match:
                        current_profile['image'] = image_match.group(1)
            
            # 在profile内部解析其他属性
            elif current_profile is not None:
                if stripped_line.startswith('image:'):
                    image_match = re.search(r'image:\s*(.+)', stripped_line)
                    if image_match:
                        current_profile['image'] = image_match.group(1)
                
                elif stripped_line.startswith('content:'):
                    content_match = re.search(r'content:\s*(.+)', stripped_line)
                    if content_match:
                        current_profile['content'] = content_match.group(1)
                        # 从content中提取条目ID (aboutXXX.md -> XXX)
                        if current_profile['content'].startswith('about') and current_profile['content'].endswith('.md'):
                            current_profile['item_id'] = current_profile['content'][5:-3]
                            
                            # 读取对应文件夹中的scholar id文件（重点修复）
                            scholar_folder = self.en_scholar_folder if lang == "en" else self.zh_scholar_folder
                            scholar_file = os.path.join(scholar_folder, f"{current_profile['item_id']}.md")
                            current_profile['scholar_file_path'] = scholar_file  # 保存文件路径
                            
                            # 尝试读取Scholar ID文件
                            if os.path.exists(scholar_file):
                                try:
                                    with open(scholar_file, 'r', encoding='utf-8') as f:
                                        current_profile['google_scholar_id'] = f.read().strip()
                                    print(f"成功读取Scholar ID文件: {scholar_file}")  # 调试信息
                                except Exception as e:
                                    error_msg = f"读取Google Scholar ID文件出错: {e}"
                                    print(error_msg)
                                    current_profile['google_scholar_id'] = f"[读取错误: {str(e)}]"
                            else:
                                print(f"Scholar ID文件不存在: {scholar_file}")  # 调试信息
                                current_profile['google_scholar_id'] = ""  # 文件不存在时设为空
                
                elif stripped_line.startswith('image_circular:'):
                    circular_match = re.search(r'image_circular:\s*(true|false)', stripped_line, re.IGNORECASE)
                    if circular_match:
                        current_profile['image_circular'] = circular_match.group(1).lower() == 'true'
                
                elif stripped_line.startswith('more_info:'):
                    in_more_info = True
                    more_info_count = 0  # 重置计数器
                
                # 解析more_info内容
                elif in_more_info and stripped_line.startswith('<p>') and stripped_line.endswith('</p>'):
                    # 提取<p>标签内的内容，移除可能的前缀
                    p_match = re.search(r'<p>(.*?)</p>', stripped_line)
                    if p_match:
                        text = p_match.group(1).strip()
                        
                        # 移除常见前缀
                        text = re.sub(r'^地址:\s*', '', text)
                        text = re.sub(r'^邮箱:\s*', '', text)
                        text = re.sub(r'^电话:\s*', '', text)
                        text = re.sub(r'^Address:\s*', '', text)
                        text = re.sub(r'^Email:\s*', '', text)
                        text = re.sub(r'^Phone:\s*', '', text)
                        
                        # 根据顺序分配到不同字段
                        if more_info_count == 0:
                            current_profile['more_info']['address'] = text
                        elif more_info_count == 1:
                            current_profile['more_info']['email'] = text
                        elif more_info_count == 2:
                            current_profile['more_info']['phone'] = text
                        
                        more_info_count += 1
        
        # 添加最后一个profile
        if current_profile:
            profiles.append(current_profile)
        
        return profiles
    
    def populate_profiles_list(self, lang):
        """填充对应文件夹的profiles列表"""
        treeview = self.en_treeview if lang == "en" else self.zh_treeview
        profiles = self.en_profiles if lang == "en" else self.zh_profiles
        
        # 清空现有项
        for item in treeview.get_children():
            treeview.delete(item)
        
        # 添加所有profile
        for i, profile in enumerate(profiles):
            item_id = f"profile_{i}"
            display_text = f"条目 {i+1}"
            if 'item_id' in profile and profile['item_id']:
                display_text += f" (ID: {profile['item_id']})"
            treeview.insert("", tk.END, iid=item_id, values=[display_text])
    
    def on_profile_selected(self, event, lang):
        """处理条目选择事件，显示Scholar ID文件路径"""
        treeview = self.en_treeview if lang == "en" else self.zh_treeview
        profiles = self.en_profiles if lang == "en" else self.zh_profiles
        selected_items = treeview.selection()
        
        if not selected_items:
            return
        
        # 获取选中的索引
        selected_index = int(selected_items[0].split('_')[1])
        self.current_profile_index = selected_index
        self.current_language = lang
        
        # 获取对应的表单控件
        if lang == "en":
            align_var = self.en_align_var
            photo_entry = self.en_photo_entry
            circular_var = self.en_circular_var
            item_id_entry = self.en_item_id_entry  # 条目ID
            scholar_id_entry = self.en_scholar_id_entry
            scholar_path_label = self.en_scholar_path_label  # Scholar ID文件路径标签
            address_entry = self.en_address_entry
            email_entry = self.en_email_entry
            phone_entry = self.en_phone_entry
            about_text = self.en_about_text
        else:
            align_var = self.zh_align_var
            photo_entry = self.zh_photo_entry
            circular_var = self.zh_circular_var
            item_id_entry = self.zh_item_id_entry  # 条目ID
            scholar_id_entry = self.zh_scholar_id_entry
            scholar_path_label = self.zh_scholar_path_label  # Scholar ID文件路径标签
            address_entry = self.zh_address_entry
            email_entry = self.zh_email_entry
            phone_entry = self.zh_phone_entry
            about_text = self.zh_about_text
        
        # 加载选中的profile数据到表单
        profile = profiles[selected_index]
        align_var.set(profile.get('align', 'right'))
        photo_entry.delete(0, tk.END)
        photo_entry.insert(0, profile.get('image', ''))
        circular_var.set(profile.get('image_circular', False))
        
        item_id_entry.delete(0, tk.END)
        item_id_entry.insert(0, profile.get('item_id', ''))
        
        # 加载Google Scholar ID并显示文件路径
        scholar_id_entry.delete(0, tk.END)
        scholar_id_entry.insert(0, profile.get('google_scholar_id', ''))
        
        # 显示Scholar ID文件路径
        scholar_file_path = profile.get('scholar_file_path', '未知路径')
        if os.path.exists(scholar_file_path):
            scholar_path_label.config(text=scholar_file_path, foreground="green")
        else:
            scholar_path_label.config(text=f"{scholar_file_path} (文件不存在)", foreground="red")
        
        # 加载more_info内容
        address_entry.delete(0, tk.END)
        address_entry.insert(0, profile['more_info'].get('address', ''))
        
        email_entry.delete(0, tk.END)
        email_entry.insert(0, profile['more_info'].get('email', ''))
        
        phone_entry.delete(0, tk.END)
        phone_entry.insert(0, profile['more_info'].get('phone', ''))
        
        # 加载对应文件夹中的about文件内容
        about_text.delete("1.0", tk.END)
        if profile.get('content'):
            about_path = os.path.join(self.en_us_folder if lang == "en" else self.zh_cn_folder, profile['content'])
            if os.path.exists(about_path):
                try:
                    with open(about_path, 'r', encoding='utf-8') as f:
                        about_text.insert(tk.END, f.read())
                except Exception as e:
                    print(f"无法读取about文件: {e}")
    
    def on_tab_changed(self, event):
        """切换标签页时，自动同步选择对应文件夹的相同ID条目"""
        current_tab = self.notebook.index(self.notebook.select())
        new_lang = "en" if current_tab == 0 else "zh"
        
        # 如果切换了语言，尝试选中对应ID的条目
        if self.current_language != new_lang and self.current_profile_index != -1:
            source_profiles = self.en_profiles if self.current_language == "en" else self.zh_profiles
            if 0 <= self.current_profile_index < len(source_profiles):
                source_id = source_profiles[self.current_profile_index].get('item_id')
                if source_id:
                    # 在新语言文件夹中查找相同ID的条目
                    target_profiles = self.en_profiles if new_lang == "en" else self.zh_profiles
                    for i, profile in enumerate(target_profiles):
                        if profile.get('item_id') == source_id:
                            # 选中找到的条目
                            treeview = self.en_treeview if new_lang == "en" else self.zh_treeview
                            treeview.selection_set(f"profile_{i}")
                            self.current_profile_index = i
                            self.current_language = new_lang
                            self.on_profile_selected(None, new_lang)
                            return
        
        # 如果没找到对应条目，重置选择
        self.current_language = new_lang
        self.current_profile_index = -1
    
    def find_matching_profile(self, target_lang, source_id):
        """在目标语言文件夹中查找具有相同ID的条目"""
        target_profiles = self.en_profiles if target_lang == "en" else self.zh_profiles
        for i, profile in enumerate(target_profiles):
            if profile.get('item_id') == source_id:
                return i
        return -1
    
    def sync_current_profile(self):
        """同步当前条目到另一个语言文件夹，重点确保Scholar ID文件同步"""
        if self.current_profile_index == -1:
            messagebox.showinfo("提示", "请先选择一个条目")
            return
        
        # 获取源文件夹数据
        source_lang = self.current_language
        target_lang = "zh" if source_lang == "en" else "en"
        source_profiles = self.en_profiles if source_lang == "en" else self.zh_profiles
        source_profile = source_profiles[self.current_profile_index]
        
        # 查找目标文件夹中的匹配条目
        target_index = self.find_matching_profile(target_lang, source_profile.get('item_id'))
        
        # 准备同步的核心字段
        sync_data = {
            'item_id': source_profile.get('item_id'),  # 条目ID
            'google_scholar_id': source_profile.get('google_scholar_id'),
            'image': source_profile.get('image')       # 图片内容
        }
        
        # 执行同步
        if target_index != -1:
            # 更新目标文件夹中的现有条目
            target_profiles = self.en_profiles if target_lang == "en" else self.zh_profiles
            target_profile = target_profiles[target_index]
            
            # 检查是否有变化
            changes = []
            if target_profile.get('item_id') != sync_data['item_id']:
                changes.append(f"条目ID: {target_profile.get('item_id')} → {sync_data['item_id']}")
            if target_profile.get('google_scholar_id') != sync_data['google_scholar_id']:
                changes.append(f"Scholar ID: {target_profile.get('google_scholar_id')} → {sync_data['google_scholar_id']}")
            if target_profile.get('image') != sync_data['image']:
                changes.append(f"图片: {target_profile.get('image')} → {sync_data['image']}")
            
            if not changes:
                messagebox.showinfo("提示", f"{target_lang == 'en' and 'en-us' or 'zh-cn'}文件夹中的条目已同步")
                return
            
            # 确认同步
            if messagebox.askyesno("确认同步", 
                                 f"将以下更改同步到{target_lang == 'en' and 'en-us' or 'zh-cn'}文件夹:\n" + 
                                 "\n".join(changes)):
                # 更新目标条目
                target_profile['item_id'] = sync_data['item_id']
                target_profile['content'] = f"about{sync_data['item_id']}.md" if sync_data['item_id'] else ""
                target_profile['google_scholar_id'] = sync_data['google_scholar_id']
                target_profile['image'] = sync_data['image']
                
                # 更新目标文件夹中的Scholar ID文件（重点修复）
                scholar_folder = self.en_scholar_folder if target_lang == "en" else self.zh_scholar_folder
                if sync_data['item_id']:
                    # 旧ID文件（如果ID改变了需要删除）
                    old_id = target_profile.get('item_id')
                    if old_id and old_id != sync_data['item_id']:
                        old_scholar_file = os.path.join(scholar_folder, f"{old_id}.md")
                        if os.path.exists(old_scholar_file):
                            try:
                                os.remove(old_scholar_file)
                                print(f"删除旧Scholar ID文件: {old_scholar_file}")
                            except Exception as e:
                                messagebox.showerror("错误", f"删除旧Scholar ID文件时出错: {str(e)}")
                
                # 创建/更新新的Scholar ID文件
                if sync_data['item_id']:
                    scholar_file = os.path.join(scholar_folder, f"{sync_data['item_id']}.md")
                    try:
                        # 确保文件夹存在
                        os.makedirs(os.path.dirname(scholar_file), exist_ok=True)
                        
                        with open(scholar_file, 'w', encoding='utf-8') as f:
                            f.write(sync_data['google_scholar_id'])
                        
                        # 验证保存结果
                        with open(scholar_file, 'r', encoding='utf-8') as f:
                            saved_id = f.read().strip()
                            if saved_id != sync_data['google_scholar_id']:
                                raise Exception("保存的ID与输入不匹配")
                        
                        # 更新文件路径信息
                        target_profile['scholar_file_path'] = scholar_file
                        print(f"成功同步Scholar ID文件: {scholar_file}")
                        
                    except Exception as e:
                        messagebox.showerror("错误", f"同步Scholar ID文件时出错: {str(e)}")
        
        else:
            # 在目标文件夹中创建新的对应条目
            if messagebox.askyesno("创建对应条目", 
                                 f"{target_lang == 'en' and 'en-us' or 'zh-cn'}文件夹中未找到对应条目，是否创建?\n" +
                                 f"条目ID: {sync_data['item_id']}\nScholar ID: {sync_data['google_scholar_id']}"):
                new_profile = {
                    'align': 'right',
                    'image': sync_data['image'],
                    'content': f"about{sync_data['item_id']}.md" if sync_data['item_id'] else "",
                    'image_circular': False,
                    'item_id': sync_data['item_id'],
                    'google_scholar_id': sync_data['google_scholar_id'],
                    'more_info': {
                        'address': '',
                        'email': '',
                        'phone': ''
                    }
                }
                
                # 添加到目标语言文件夹列表
                target_profiles = self.en_profiles if target_lang == "en" else self.zh_profiles
                target_profiles.append(new_profile)
                
                # 在目标文件夹中创建Scholar ID文件
                if sync_data['item_id']:
                    scholar_folder = self.en_scholar_folder if target_lang == "en" else self.zh_scholar_folder
                    scholar_file = os.path.join(scholar_folder, f"{sync_data['item_id']}.md")
                    new_profile['scholar_file_path'] = scholar_file  # 保存文件路径
                    
                    try:
                        os.makedirs(os.path.dirname(scholar_file), exist_ok=True)
                        with open(scholar_file, 'w', encoding='utf-8') as f:
                            f.write(sync_data['google_scholar_id'])
                        print(f"创建新Scholar ID文件: {scholar_file}")
                    except Exception as e:
                        messagebox.showerror("错误", f"创建Scholar ID文件时出错: {str(e)}")
        
        # 更新目标文件夹的列表
        self.populate_profiles_list(target_lang)
        messagebox.showinfo("成功", f"{target_lang == 'en' and 'en-us' or 'zh-cn'}文件夹已同步")
    
    def save_profile_details(self, lang):
        """保存条目详情，重点修复Scholar ID文件保存逻辑"""
        if self.current_profile_index == -1:
            messagebox.showinfo("提示", "请先选择一个条目")
            return
        
        profiles = self.en_profiles if lang == "en" else self.zh_profiles
        
        # 获取表单数据
        if lang == "en":
            align = self.en_align_var.get()
            image = self.en_photo_entry.get()
            circular = self.en_circular_var.get()
            item_id = self.en_item_id_entry.get()  # 条目ID
            scholar_id = self.en_scholar_id_entry.get()
            address = self.en_address_entry.get()
            email = self.en_email_entry.get()
            phone = self.en_phone_entry.get()
            about_content = self.en_about_text.get("1.0", tk.END).rstrip()
            target_folder = self.en_us_folder  # 当前操作的是en-us文件夹
            scholar_folder = self.en_scholar_folder
            scholar_path_label = self.en_scholar_path_label
        else:
            align = self.zh_align_var.get()
            image = self.zh_photo_entry.get()
            circular = self.zh_circular_var.get()
            item_id = self.zh_item_id_entry.get()  # 条目ID
            scholar_id = self.zh_scholar_id_entry.get()
            address = self.zh_address_entry.get()
            email = self.zh_email_entry.get()
            phone = self.zh_phone_entry.get()
            about_content = self.zh_about_text.get("1.0", tk.END).rstrip()
            target_folder = self.zh_cn_folder  # 当前操作的是zh-cn文件夹
            scholar_folder = self.zh_scholar_folder
            scholar_path_label = self.zh_scholar_path_label
        
        # 验证条目ID
        if not item_id:
            messagebox.showerror("错误", "条目ID不能为空")
            return
        
        # 获取原始条目信息
        original_profile = profiles[self.current_profile_index]
        original_item_id = original_profile.get('item_id')
        
        # 检查是否修改了需要同步的核心字段
        sync_fields_changed = (original_item_id != item_id or 
                              original_profile.get('google_scholar_id') != scholar_id or 
                              original_profile.get('image') != image)
        
        # 如果ID改变了，需要删除旧的Scholar ID文件
        if original_item_id and original_item_id != item_id:
            old_scholar_file = os.path.join(scholar_folder, f"{original_item_id}.md")
            if os.path.exists(old_scholar_file):
                try:
                    os.remove(old_scholar_file)
                    print(f"删除旧Scholar ID文件: {old_scholar_file}")
                except Exception as e:
                    messagebox.showerror("错误", f"删除旧Scholar ID文件时出错: {str(e)}")
                    return
        
        # 更新当前文件夹的profile数据
        profile = profiles[self.current_profile_index]
        profile['align'] = align
        profile['image'] = image
        profile['image_circular'] = circular
        profile['item_id'] = item_id  # 保存条目ID
        profile['content'] = f"about{item_id}.md"
        profile['google_scholar_id'] = scholar_id
        profile['more_info'] = {
            'address': address,
            'email': email,
            'phone': phone
        }
        
        # 保存当前文件夹中的about文件
        about_path = os.path.join(target_folder, profile['content'])
        try:
            with open(about_path, 'w', encoding='utf-8') as f:
                f.write(about_content)
        except Exception as e:
            messagebox.showerror("错误", f"保存about文件时出错: {str(e)}")
            return
        
        # 保存当前文件夹中的Google Scholar ID（重点修复）
        scholar_file = os.path.join(scholar_folder, f"{item_id}.md")
        profile['scholar_file_path'] = scholar_file  # 更新文件路径
        
        try:
            # 确保文件夹存在
            os.makedirs(os.path.dirname(scholar_file), exist_ok=True)
            
            # 写入Scholar ID
            with open(scholar_file, 'w', encoding='utf-8') as f:
                f.write(scholar_id)
            
            # 验证保存结果
            with open(scholar_file, 'r', encoding='utf-8') as f:
                saved_id = f.read().strip()
                if saved_id != scholar_id:
                    raise Exception("保存的Scholar ID与输入不匹配")
            
            print(f"成功保存Scholar ID到文件: {scholar_file}")
            # 更新路径显示
            scholar_path_label.config(text=scholar_file, foreground="green")
            
        except Exception as e:
            error_msg = f"保存Google Scholar ID文件时出错: {str(e)}"
            print(error_msg)
            scholar_path_label.config(text=f"{scholar_file} (保存失败)", foreground="red")
            messagebox.showerror("错误", error_msg)
            return
        
        # 更新当前文件夹的列表
        self.populate_profiles_list(lang)
        
        # 如果核心字段有变化，提示是否同步到另一个文件夹
        if sync_fields_changed:
            other_folder = "zh-cn" if lang == "en" else "en-us"
            if messagebox.askyesno("同步提示", f"已修改核心字段，是否同步到{other_folder}文件夹?"):
                self.sync_current_profile()
        
        messagebox.showinfo("成功", f"{lang == 'en' and 'en-us' or 'zh-cn'}文件夹中的条目已更新")
    
    def add_new_profile_dialog(self, lang):
        """添加新条目，确保正确创建Scholar ID文件"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加新Profile")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 同步选项
        other_folder = "zh-cn" if lang == "en" else "en-us"
        sync_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dialog, text=f"同时在{other_folder}文件夹中创建对应条目", 
                       variable=sync_var).pack(anchor=tk.W, padx=10, pady=5)
        
        # 创建表单
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 对齐方式
        ttk.Label(form_frame, text="对齐方式:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        align_var = tk.StringVar(value="right")
        align_frame = ttk.Frame(form_frame)
        align_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(align_frame, text="左对齐", variable=align_var, value="left").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(align_frame, text="右对齐", variable=align_var, value="right").pack(side=tk.LEFT, padx=5)
        
        # 图片名称
        ttk.Label(form_frame, text="图片名称:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        photo_entry = ttk.Entry(form_frame, width=30)
        photo_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        photo_entry.insert(0, "prof_pic.jpg")
        
        # 是否圆形图片
        circular_var = tk.BooleanVar(value=False)
        circular_check = ttk.Checkbutton(form_frame, text="圆形图片", variable=circular_var)
        circular_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5, padx=5)
        
        # 条目ID
        ttk.Label(form_frame, text="条目ID:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        item_id_entry = ttk.Entry(form_frame, width=30)
        item_id_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Google Scholar ID
        ttk.Label(form_frame, text="Google Scholar ID:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        scholar_id_entry = ttk.Entry(form_frame, width=30)
        scholar_id_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # 地址
        ttk.Label(form_frame, text="地址:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=5)
        address_entry = ttk.Entry(form_frame, width=30)
        address_entry.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # 邮箱
        ttk.Label(form_frame, text="邮箱:").grid(row=6, column=0, sticky=tk.W, pady=5, padx=5)
        email_entry = ttk.Entry(form_frame, width=30)
        email_entry.grid(row=6, column=1, sticky=tk.W, pady=5)
        
        # 电话
        ttk.Label(form_frame, text="电话:").grid(row=7, column=0, sticky=tk.W, pady=5, padx=5)
        phone_entry = ttk.Entry(form_frame, width=30)
        phone_entry.grid(row=7, column=1, sticky=tk.W, pady=5)
        
        # About文件内容
        ttk.Label(form_frame, text="About 文件内容:").grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=5, padx=5)
        about_text = scrolledtext.ScrolledText(form_frame, wrap=tk.WORD, height=5)
        about_text.grid(row=9, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5, padx=5)
        
        # 按钮
        btn_frame = ttk.Frame(dialog, padding=10)
        btn_frame.pack(fill=tk.X)
        
        def save_new_profile():
            """保存新条目，确保正确创建Scholar ID文件"""
            align = align_var.get()
            image = photo_entry.get()
            circular = circular_var.get()
            item_id = item_id_entry.get()  # 条目ID
            scholar_id = scholar_id_entry.get()
            address = address_entry.get()
            email = email_entry.get()
            phone = phone_entry.get()
            about_content = about_text.get("1.0", tk.END).rstrip()
            
            # 验证
            if not item_id:
                messagebox.showerror("错误", "条目ID不能为空")
                return
            
            # 检查目标文件夹中是否已有相同ID的条目
            target_lang = "zh" if lang == "en" else "en"
            target_index = self.find_matching_profile(target_lang, item_id)
            if target_index != -1 and sync_var.get():
                messagebox.showerror("错误", f"{other_folder}文件夹中已存在相同ID的条目，无法创建")
                return
            
            # 创建新profile（当前文件夹）
            new_profile = {
                'align': align,
                'image': image,
                'content': f"about{item_id}.md",
                'image_circular': circular,
                'item_id': item_id,  # 存储条目ID
                'google_scholar_id': scholar_id,
                'more_info': {
                    'address': address,
                    'email': email,
                    'phone': phone
                }
            }
            
            # 添加到当前文件夹列表
            profiles = self.en_profiles if lang == "en" else self.zh_profiles
            profiles.append(new_profile)
            
            # 保存当前文件夹中的about文件
            target_folder = self.en_us_folder if lang == "en" else self.zh_cn_folder
            about_path = os.path.join(target_folder, new_profile['content'])
            try:
                with open(about_path, 'w', encoding='utf-8') as f:
                    f.write(about_content)
            except Exception as e:
                messagebox.showerror("错误", f"保存about文件时出错: {str(e)}")
                return
            
            # 保存当前文件夹中的Google Scholar ID
            scholar_folder = self.en_scholar_folder if lang == "en" else self.zh_scholar_folder
            scholar_file = os.path.join(scholar_folder, f"{item_id}.md")
            new_profile['scholar_file_path'] = scholar_file  # 保存文件路径
            
            try:
                os.makedirs(os.path.dirname(scholar_file), exist_ok=True)
                with open(scholar_file, 'w', encoding='utf-8') as f:
                    f.write(scholar_id)
                print(f"创建新Scholar ID文件: {scholar_file}")
            except Exception as e:
                messagebox.showerror("错误", f"保存Google Scholar ID文件时出错: {str(e)}")
                return
            
            # 如果需要，在另一个文件夹中创建对应条目
            if sync_var.get():
                target_profiles = self.en_profiles if target_lang == "en" else self.zh_profiles
                # 创建同步的条目
                target_profile = {
                    'align': align,
                    'image': image,
                    'content': f"about{item_id}.md",
                    'image_circular': circular,
                    'item_id': item_id,  # 同步条目ID
                    'google_scholar_id': scholar_id,
                    'scholar_file_path': os.path.join(
                        self.en_scholar_folder if target_lang == "en" else self.zh_scholar_folder, 
                        f"{item_id}.md"
                    ),
                    'more_info': {
                        'address': '',
                        'email': '',
                        'phone': ''
                    }
                }
                target_profiles.append(target_profile)
                
                # 为目标文件夹创建Scholar ID文件
                target_scholar_folder = self.en_scholar_folder if target_lang == "en" else self.zh_scholar_folder
                target_scholar_file = os.path.join(target_scholar_folder, f"{item_id}.md")
                try:
                    os.makedirs(os.path.dirname(target_scholar_file), exist_ok=True)
                    with open(target_scholar_file, 'w', encoding='utf-8') as f:
                        f.write(scholar_id)
                    print(f"在{other_folder}创建Scholar ID文件: {target_scholar_file}")
                except Exception as e:
                    messagebox.showerror("错误", f"为{other_folder}创建Scholar ID文件时出错: {str(e)}")
                    return
                
                # 更新目标文件夹列表
                self.populate_profiles_list(target_lang)
            
            # 更新当前文件夹列表
            self.populate_profiles_list(lang)
            dialog.destroy()
            messagebox.showinfo("成功", f"新条目已添加到{lang == 'en' and 'en-us' or 'zh-cn'}文件夹{sync_var.get() and '，并同步到' + other_folder or ''}")
        
        ttk.Button(btn_frame, text="保存", command=save_new_profile).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def delete_profile(self, lang):
        """删除条目，确保同时删除对应的Scholar ID文件"""
        treeview = self.en_treeview if lang == "en" else self.zh_treeview
        profiles = self.en_profiles if lang == "en" else self.zh_profiles
        selected_items = treeview.selection()
        
        if not selected_items:
            messagebox.showinfo("提示", "请先选择一个条目")
            return
        
        # 获取选中的索引和ID
        selected_index = int(selected_items[0].split('_')[1])
        profile = profiles[selected_index]
        item_id = profile.get('item_id', '未知ID')
        
        # 检查另一个文件夹中是否有对应条目
        target_lang = "zh" if lang == "en" else "en"
        other_folder = "zh-cn" if lang == "en" else "en-us"
        target_index = self.find_matching_profile(target_lang, item_id)
        
        # 确认删除
        delete_message = f"确定要删除{lang == 'en' and 'en-us' or 'zh-cn'}文件夹中的条目(ID: {item_id})吗?\n相关文件也将被删除。"
        if target_index != -1:
            delete_message += f"\n\n同时在{other_folder}文件夹中也找到对应条目，是否一并删除?"
        
        if not messagebox.askyesno("确认删除", delete_message):
            return
        
        # 删除当前文件夹的条目和文件
        target_folder = self.en_us_folder if lang == "en" else self.zh_cn_folder
        scholar_folder = self.en_scholar_folder if lang == "en" else self.zh_scholar_folder
        
        # 删除about文件
        about_path = os.path.join(target_folder, profile['content'])
        if os.path.exists(about_path):
            try:
                os.remove(about_path)
                print(f"删除about文件: {about_path}")
            except Exception as e:
                messagebox.showerror("错误", f"删除about文件时出错: {str(e)}")
                return
        
        # 删除Google Scholar ID文件（重点操作）
        if item_id:
            scholar_file = os.path.join(scholar_folder, f"{item_id}.md")
            if os.path.exists(scholar_file):
                try:
                    os.remove(scholar_file)
                    print(f"删除Scholar ID文件: {scholar_file}")
                except Exception as e:
                    messagebox.showerror("错误", f"删除Google Scholar ID文件时出错: {str(e)}")
                    return
        
        # 从当前文件夹列表中删除
        del profiles[selected_index]
        
        # 如果需要，删除另一个文件夹的对应条目
        if target_index != -1:
            target_profiles = self.en_profiles if target_lang == "en" else self.zh_profiles
            target_profile = target_profiles[target_index]
            
            # 删除目标文件夹的about文件
            target_folder_other = self.en_us_folder if target_lang == "en" else self.zh_cn_folder
            about_path_other = os.path.join(target_folder_other, target_profile['content'])
            if os.path.exists(about_path_other):
                try:
                    os.remove(about_path_other)
                    print(f"删除{other_folder}的about文件: {about_path_other}")
                except Exception as e:
                    messagebox.showerror("错误", f"删除{other_folder}的about文件时出错: {str(e)}")
            
            # 删除目标文件夹的Scholar ID文件
            target_item_id = target_profile.get('item_id')
            if target_item_id:
                target_scholar_folder = self.en_scholar_folder if target_lang == "en" else self.zh_scholar_folder
                target_scholar_file = os.path.join(target_scholar_folder, f"{target_item_id}.md")
                if os.path.exists(target_scholar_file):
                    try:
                        os.remove(target_scholar_file)
                        print(f"删除{other_folder}的Scholar ID文件: {target_scholar_file}")
                    except Exception as e:
                        messagebox.showerror("错误", f"删除{other_folder}的Scholar ID文件时出错: {str(e)}")
            
            # 从目标文件夹列表中删除
            del target_profiles[target_index]
            # 更新目标文件夹列表
            self.populate_profiles_list(target_lang)
        
        # 更新当前文件夹列表
        self.populate_profiles_list(lang)
        
        # 清空详情区域
        if lang == "en":
            self.en_align_var.set("right")
            self.en_photo_entry.delete(0, tk.END)
            self.en_circular_var.set(False)
            self.en_item_id_entry.delete(0, tk.END)
            self.en_scholar_id_entry.delete(0, tk.END)
            self.en_scholar_path_label.config(text="未选择条目", foreground="gray")
            self.en_address_entry.delete(0, tk.END)
            self.en_email_entry.delete(0, tk.END)
            self.en_phone_entry.delete(0, tk.END)
            self.en_about_text.delete("1.0", tk.END)
        else:
            self.zh_align_var.set("right")
            self.zh_photo_entry.delete(0, tk.END)
            self.zh_circular_var.set(False)
            self.zh_item_id_entry.delete(0, tk.END)
            self.zh_scholar_id_entry.delete(0, tk.END)
            self.zh_scholar_path_label.config(text="未选择条目", foreground="gray")
            self.zh_address_entry.delete(0, tk.END)
            self.zh_email_entry.delete(0, tk.END)
            self.zh_phone_entry.delete(0, tk.END)
            self.zh_about_text.delete("1.0", tk.END)
        
        self.current_profile_index = -1
        messagebox.showinfo("成功", "条目已删除")
    
    def save_changes(self):
        """保存所有更改到对应文件夹的profiles.md"""
        if not messagebox.askyesno("确认", "确定要保存所有更改吗?"):
            return
        
        try:
            # 保存en-us文件夹的profiles.md
            en_content = self.generate_profiles_content(self.en_profiles)
            with open(self.en_profiles_path, 'w', encoding='utf-8') as f:
                f.write(en_content)
            
            # 保存zh-cn文件夹的profiles.md
            zh_content = self.generate_profiles_content(self.zh_profiles)
            with open(self.zh_profiles_path, 'w', encoding='utf-8') as f:
                f.write(zh_content)
            
            # 更新原始数据
            self.original_en_profiles = [p.copy() for p in self.en_profiles]
            self.original_zh_profiles = [p.copy() for p in self.zh_profiles]
            
            messagebox.showinfo("成功", "所有更改已保存到en-us和zh-cn文件夹的profiles.md")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存profiles.md文件时出错: {str(e)}")
    
    def cancel_changes(self):
        """取消所有更改，恢复到最后保存的状态"""
        if not messagebox.askyesno("确认", "确定要取消所有未保存的更改吗?"):
            return
        
        # 恢复原始数据
        self.en_profiles = [p.copy() for p in self.original_en_profiles]
        self.zh_profiles = [p.copy() for p in self.original_zh_profiles]
        
        # 更新两个文件夹的列表
        self.populate_profiles_list("en")
        self.populate_profiles_list("zh")
        
        # 清空详情区域
        self.en_align_var.set("right")
        self.en_photo_entry.delete(0, tk.END)
        self.en_circular_var.set(False)
        self.en_item_id_entry.delete(0, tk.END)
        self.en_scholar_id_entry.delete(0, tk.END)
        self.en_scholar_path_label.config(text="未选择条目", foreground="gray")
        self.en_address_entry.delete(0, tk.END)
        self.en_email_entry.delete(0, tk.END)
        self.en_phone_entry.delete(0, tk.END)
        self.en_about_text.delete("1.0", tk.END)
        
        self.zh_align_var.set("right")
        self.zh_photo_entry.delete(0, tk.END)
        self.zh_circular_var.set(False)
        self.zh_item_id_entry.delete(0, tk.END)
        self.zh_scholar_id_entry.delete(0, tk.END)
        self.zh_scholar_path_label.config(text="未选择条目", foreground="gray")
        self.zh_address_entry.delete(0, tk.END)
        self.zh_email_entry.delete(0, tk.END)
        self.zh_phone_entry.delete(0, tk.END)
        self.zh_about_text.delete("1.0", tk.END)
        
        self.current_profile_index = -1
        messagebox.showinfo("提示", "所有更改已取消")
    
    def generate_profiles_content(self, profiles):
        """根据profile数据生成profiles.md内容"""
        content = "# 多语言条目配置 - 同步条目ID、Scholar ID和图片\n"
        content += "# en-us和zh-cn文件夹的其他内容可独立编辑\n"
        
        for profile in profiles:
            content += "  - align: {}\n".format(profile['align'])
            content += "    image: {}\n".format(profile['image'])
            content += "    content: {}\n".format(profile['content'])
            content += "    image_circular: {}\n".format(str(profile['image_circular']).lower())
            content += "    more_info: >\n"
            content += "      <p>{}</p>\n".format(profile['more_info']['address'])
            content += "      <p>邮箱:{}</p>\n".format(profile['more_info']['email'])
            content += "      <p>电话:{}</p>\n".format(profile['more_info']['phone'])
        
        return content

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfileEditor(root)
    root.mainloop()
