import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from utils import ColorManager

class StartMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام الحسابات - خلفاء الحاج")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # تهيئة مدير الألوان واختيار ثيم عشوائي
        self.color_manager = ColorManager()
        self.theme = self.color_manager.get_random_theme()
        
        self.colors = {
            'red': self.theme['dark'],      # للخلفيات الداكنة
            'orange': self.theme['base'],   # للأزرار
            'pink': self.theme['light'],    # للخلفيات الفاتحة
            'yellow': self.theme['lighter'], # للخلفيات الفاتحة جداً
            'white': self.theme['white']
        }
        
        # تحميل الصورة كخلفية
        self.load_background_image()
        
        # إنشاء Canvas لعرض الصورة
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # عرض الصورة كخلفية
        self.bg_image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
        
        # قائمة لتتبع الأزرار الحالية حتى يمكن إعادة بنائها لاحقاً
        self.menu_buttons = []
        self.menu_button_wrappers = []
        self.bottom_buttons = []
        self.bottom_button_wrappers = []
        self.bottom_buttons_frame = None
        
        # إنشاء الزراير
        self.create_buttons()
        
        # حفظ تقرير اليوم السابق تلقائياً عند فتح البرنامج
        self.auto_save_previous_day_report()
        
        # ربط تغيير حجم النافذة بتحديث الصورة
        self.root.bind('<Configure>', self.on_window_resize)
        
        # ربط حدث إغلاق النافذة بحفظ التقرير
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_background_image(self):
        """تحميل الصورة وتعديل حجمها"""
        # التعامل مع المسارات في حالة التشغيل كملف تنفيذي
        import sys
        if getattr(sys, 'frozen', False):
            # عند التشغيل كـ exe
            base_path = sys._MEIPASS
        else:
            # عند التشغيل كـ script
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        image_name = "Screenshot 2025-11-24 202612.png"
        image_path = os.path.join(base_path, image_name)
        
        # محاولة بديلة: البحث في المجلد الحالي إذا لم توجد في المسار الأساسي
        if not os.path.exists(image_path):
             image_path = os.path.join(os.getcwd(), image_name)
        
        if not os.path.exists(image_path):
            print(f"تحذير: لم يتم العثور على الصورة في {image_path}")
            # إنشاء صورة افتراضية إذا لم توجد الصورة
            self.bg_image = None
            return
        
        try:
            # تحميل الصورة
            img = Image.open(image_path)
            # تعديل حجم الصورة لتناسب النافذة
            self.original_image = img
            self.bg_image = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"خطأ في تحميل الصورة: {e}")
            self.bg_image = None
    
    def on_window_resize(self, event):
        """تحديث حجم الصورة عند تغيير حجم النافذة"""
        if hasattr(self, 'original_image') and self.original_image:
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            if width > 1 and height > 1:
                # تعديل حجم الصورة مع الحفاظ على النسبة
                img = self.original_image.copy()
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(img)
                self.canvas.itemconfig(self.bg_image_id, image=self.bg_image)
    
    def create_buttons(self):
        """إنشاء أزرار القائمة الرئيسية في الجانب الأيسر"""
        # إزالة أي أزرار قديمة
        for btn in getattr(self, "menu_buttons", []):
            btn.destroy()
        for wrapper in getattr(self, "menu_button_wrappers", []):
            wrapper.destroy()
        for btn in getattr(self, "bottom_buttons", []):
            btn.destroy()
        for wrapper in getattr(self, "bottom_button_wrappers", []):
            wrapper.destroy()
        if getattr(self, "bottom_buttons_frame", None):
            self.bottom_buttons_frame.destroy()

        self.menu_buttons = []
        self.menu_button_wrappers = []
        self.bottom_buttons = []
        self.bottom_button_wrappers = []
        self.bottom_buttons_frame = None

        base_button_style = {
            'font': ('Playpen Sans Arabic', 18, 'bold'),
            'bg': '#000000', # أسود
            'fg': 'white',
            'relief': tk.SOLID, # إطار صلب
            'bd': 2, # سمك الإطار
            'cursor': 'hand2',
            'activebackground': '#333333', # رمادي غامق عند الضغط
            'activeforeground': 'white'
        }
        top_button_style = {**base_button_style, 'width': 22, 'height': 2}
        bottom_button_style = {**base_button_style, 'width': 13, 'height': 1} # تصغير العرض

        buttons_info = [
            ("برنامج البائعين", self.open_sellers_program, 0.28),
            ("برنامج العملاء", self.open_clients_program, 0.41),
            ("برنامج العدة", self.open_inventory_program, 0.54),
            ("برنامج التحصيل و المنصرف", self.open_collection_program, 0.67),
        ]

        for text, command, rely in buttons_info:
            wrapper = tk.Frame(self.root, bg=self.colors['red'])
            wrapper.place(relx=0.03, rely=rely, anchor=tk.W)

            btn = tk.Button(wrapper, text=text, command=command, **top_button_style)
            btn.pack(padx=2, pady=2)

            self.menu_buttons.append(btn)
            self.menu_button_wrappers.append(wrapper)

        # الأزرار السفلية المرصوصة أفقياً
        bottom_buttons_info = [
            ("اضافة منصرف", self.open_add_expense),
            ("اضافة تحصيل", self.open_add_collection),
            ("جديد", self.open_new_entry),
            ("ترحيل الزراعة", self.open_agriculture_transfer),
            ("حسابات", self.open_accounts_module),
            ("مزامنة البيانات", self.open_data_sync),
        ]

        # زر ترحيل الزراعة هو المرجع في الحجم
        reference_width = bottom_button_style['width']
        reference_height = bottom_button_style['height']

        # إنشاء أزرار منفصلة مع الحفاظ على الخط الأفقي
        spacing = 0.15 # تقليل المسافة بين الأزرار
        buttons_count = len(bottom_buttons_info)
        base_relx = 0.5 - ((buttons_count - 1) * spacing) / 2

        for index, (text, command) in enumerate(bottom_buttons_info):
            relx = base_relx + index * spacing
            wrapper = tk.Frame(self.root, bg=self.colors['pink'])
            wrapper.place(relx=relx, rely=0.9, anchor=tk.CENTER)

            btn = tk.Button(
                wrapper,
                text=text,
                command=command,
                width=reference_width,
                height=reference_height,
                **base_button_style
            )
            btn.pack(padx=2, pady=2)

            self.bottom_buttons.append(btn)
            self.bottom_button_wrappers.append(wrapper)
        
        # زر الخروج في أعلى اليمين
        exit_button_style = {
            'font': ('Playpen Sans Arabic', 14, 'bold'),
            'bg': '#000000', # أسود
            'fg': 'white',
            'relief': tk.SOLID,
            'bd': 2,
            'cursor': 'hand2',
            'activebackground': '#333333',
            'activeforeground': 'white',
            'width': 10,
            'height': 1
        }
        
        exit_wrapper = tk.Frame(self.root, bg=self.colors['red'])
        exit_wrapper.place(relx=0.95, rely=0.05, anchor=tk.NE)
        
        exit_btn = tk.Button(
            exit_wrapper,
            text="خروج",
            command=self.confirm_exit,
            **exit_button_style
        )
        exit_btn.pack(padx=2, pady=2)
        self.exit_button = exit_btn
        self.exit_wrapper = exit_wrapper
    
    def confirm_exit(self):
        """نافذة تأكيد الخروج من البرنامج"""
        result = messagebox.askyesno(
            "تأكيد الخروج",
            "هل تريد اغلاق البرنامج؟",
            icon='question'
        )
        if result:
            self.on_closing()
    
    def auto_save_previous_day_report(self):
        """حفظ تقرير اليوم السابق تلقائياً عند فتح البرنامج"""
        from datetime import datetime, timedelta
        from database import Database
        
        try:
            db = Database()
            
            # الحصول على تاريخ اليوم السابق
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            # التحقق من وجود تقرير محفوظ لليوم السابق
            existing_report = db.get_daily_report(yesterday)
            
            if not existing_report:
                # حساب وحفظ تقرير اليوم السابق
                totals = db.calculate_daily_totals(yesterday)
                db.save_daily_report(
                    yesterday,
                    totals['total_collection'],
                    totals['remaining_profit'],
                    totals['total_expenses']
                )
                print(f"تم حفظ تقرير يوم {yesterday} تلقائياً")
        except Exception as e:
            print(f"خطأ في حفظ التقرير التلقائي: {e}")
    
    def save_today_report(self):
        """حفظ تقرير اليوم الحالي"""
        from datetime import datetime
        from database import Database
        
        try:
            db = Database()
            today = datetime.now().strftime("%Y-%m-%d")
            
            # حساب وحفظ تقرير اليوم
            totals = db.calculate_daily_totals(today)
            db.save_daily_report(
                today,
                totals['total_collection'],
                totals['remaining_profit'],
                totals['total_expenses']
            )
            print(f"تم حفظ تقرير يوم {today}")
        except Exception as e:
            print(f"خطأ في حفظ التقرير: {e}")
    
    def on_closing(self):
        """معالجة حدث إغلاق النافذة"""
        # حفظ تقرير اليوم قبل الإغلاق
        self.save_today_report()
        
        # إغلاق البرنامج
        self.root.quit()
        self.root.destroy()
    
    def open_sellers_program(self):
        """فتح برنامج البائعين"""
        from sellers_page import SellersPage
        SellersPage(self.root)

    def open_clients_program(self):
        """فتح برنامج العملاء"""
        from clients_page import ClientsPage
        ClientsPage(self.root)

    def open_inventory_program(self):
        """فتح برنامج العدة"""
        from inventory_page import InventoryPage
        InventoryPage(self.root)

    def open_collection_program(self):
        """فتح برنامج التحصيل والمنصرف"""
        from collection_page import CollectionPage
        CollectionPage(self.root)

    def open_accounts_module(self):
        """فتح قسم الحسابات"""
        from accounts_page import AccountsPage
        AccountsPage(self.root)

    def open_agriculture_transfer(self):
        """فتح ترحيل الزراعة"""
        from agriculture_page import AgricultureTransferPage
        AgricultureTransferPage(self.root)

    def open_add_meal(self):
        """فتح نافذة إدارة الوجبات والأصناف"""
        meal_window = tk.Toplevel(self.root)
        meal_window.title("إدارة الوجبات والأصناف")
        meal_window.geometry("700x650")
        meal_window.configure(bg=self.colors['pink'])
        
        # توسيط
        meal_window.update_idletasks()
        x = (meal_window.winfo_screenwidth() // 2) - (350)
        y = (meal_window.winfo_screenheight() // 2) - (325)
        meal_window.geometry(f"700x650+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(meal_window, bg=self.colors['red'], height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame, 
            text="إدارة الوجبات والأصناف", 
            font=('Playpen Sans Arabic', 20, 'bold'), 
            bg=self.colors['red'], 
            fg='white'
        ).pack(pady=20)
        
        # Main Content
        content_frame = tk.Frame(meal_window, bg=self.colors['pink'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Input Card
        input_card = tk.Frame(content_frame, bg=self.colors['white'], padx=20, pady=15)
        input_card.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            input_card, 
            text="بيانات الصنف", 
            font=('Playpen Sans Arabic', 14, 'bold'), 
            bg=self.colors['white'], 
            fg=self.colors['red']
        ).pack(anchor='e', pady=(0, 10))
        
        # Fields Frame
        fields_frame = tk.Frame(input_card, bg=self.colors['white'])
        fields_frame.pack(fill=tk.X)
        
        # Helper function to create field
        def create_field(label_text, default_val=""):
            field_container = tk.Frame(fields_frame, bg=self.colors['white'])
            field_container.pack(side=tk.RIGHT, padx=10, expand=True, fill=tk.X)
            
            tk.Label(
                field_container, 
                text=label_text, 
                font=('Playpen Sans Arabic', 11), 
                bg=self.colors['white'], 
                fg='#2C3E50'
            ).pack(anchor='e')
            
            entry = tk.Entry(
                field_container, 
                font=('Arial', 13), 
                justify='center', 
                bg='#F8F9F9', 
                relief=tk.FLAT, 
                bd=1
            )
            entry.config(highlightbackground=self.colors['yellow'], highlightthickness=1)
            entry.pack(fill=tk.X, ipady=8, pady=(5, 0))
            if default_val:
                entry.insert(0, default_val)
            return entry
        
        entry_equip = create_field("وزن العدة (كجم)", "0")
        entry_price = create_field("سعر الكيلو")
        entry_name = create_field("اسم الصنف")
        
        # متغير لتتبع حالة التعديل
        editing_id = [None]  # استخدام list للسماح بالتعديل داخل الدوال الداخلية
        
        # Buttons Frame
        btn_frame = tk.Frame(input_card, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        from database import Database
        db = Database()
        
        # Table Card
        table_card = tk.Frame(content_frame, bg=self.colors['white'], padx=2, pady=2)
        table_card.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        scroll_y = ttk.Scrollbar(table_card)
        scroll_y.pack(side=tk.LEFT, fill=tk.Y)
        
        cols = ('name', 'price', 'equip')
        tree = ttk.Treeview(
            table_card, 
            columns=cols, 
            show='headings', 
            yscrollcommand=scroll_y.set,
            style="Meals.Treeview"
        )
        scroll_y.config(command=tree.yview)
        
        tree.heading('name', text='الصنف')
        tree.heading('price', text='سعر الكيلو')
        tree.heading('equip', text='وزن العدة')
        tree.column('name', anchor='center', width=200)
        tree.column('price', anchor='center', width=120)
        tree.column('equip', anchor='center', width=120)
        tree.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Styling
        style = ttk.Style()
        style.configure(
            "Meals.Treeview.Heading", 
            font=('Playpen Sans Arabic', 12, 'bold'), 
            background=self.colors['red'], 
            foreground='white'
        )
        style.configure(
            "Meals.Treeview", 
            font=('Arial', 11),
            rowheight=30,
            background='white',
            fieldbackground='white'
        )
        style.map("Meals.Treeview", background=[('selected', self.colors['orange'])])
        
        def refresh_list():
            for item in tree.get_children():
                tree.delete(item)
            meals = db.get_all_meals()
            for meal in meals:
                tree.insert('', tk.END, values=(meal[1], meal[2], meal[3]), iid=meal[0])
        
        def clear_fields():
            entry_name.delete(0, tk.END)
            entry_price.delete(0, tk.END)
            entry_equip.delete(0, tk.END)
            entry_equip.insert(0, "0")
            editing_id[0] = None
            add_btn.config(text="إضافة")
            entry_name.focus()
        
        def add_or_update_meal():
            name = entry_name.get().strip()
            price = entry_price.get().strip()
            equip = entry_equip.get().strip()
            
            if not name or not price:
                messagebox.showwarning("تنبيه", "الرجاء إدخال الاسم والسعر", parent=meal_window)
                return
            
            try:
                price_val = float(price)
                equip_val = float(equip) if equip else 0.0
                
                if editing_id[0]:  # وضع التعديل
                    db.update_meal(editing_id[0], name, price_val, equip_val)
                    refresh_list()
                    clear_fields()
                else:  # وضع الإضافة
                    if db.add_meal(name, price_val, equip_val):
                        refresh_list()
                        clear_fields()
                        # لا نعرض رسالة نجاح لتسهيل الإضافة المتكررة
                    else:
                        messagebox.showerror("خطأ", "هذا الصنف موجود بالفعل", parent=meal_window)
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال أرقام صحيحة", parent=meal_window)
        
        def load_for_edit():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("تنبيه", "الرجاء تحديد صنف للتعديل", parent=meal_window)
                return
            
            item_id = selected[0]
            values = tree.item(item_id, 'values')
            
            entry_name.delete(0, tk.END)
            entry_name.insert(0, values[0])
            
            entry_price.delete(0, tk.END)
            entry_price.insert(0, values[1])
            
            entry_equip.delete(0, tk.END)
            entry_equip.insert(0, values[2])
            
            editing_id[0] = item_id
            add_btn.config(text="حفظ التعديل")
            entry_name.focus()
        
        def delete_meal():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("تنبيه", "الرجاء تحديد صنف للحذف", parent=meal_window)
                return
            if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف الصنف المحدد؟", parent=meal_window):
                for item_id in selected:
                    db.delete_meal(item_id)
                refresh_list()
                clear_fields()
        
        # Buttons
        add_btn = tk.Button(
            btn_frame, 
            text="إضافة", 
            command=add_or_update_meal, 
            bg=self.colors['orange'], 
            fg='white', 
            font=('Playpen Sans Arabic', 11, 'bold'), 
            width=12,
            relief=tk.FLAT,
            cursor='hand2',
            height=1
        )
        add_btn.pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            btn_frame, 
            text="تعديل المحدد", 
            command=load_for_edit, 
            bg=self.colors['yellow'], 
            fg='#2C3E50', 
            font=('Playpen Sans Arabic', 11, 'bold'), 
            width=12,
            relief=tk.FLAT,
            cursor='hand2',
            height=1
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            btn_frame, 
            text="حذف المحدد", 
            command=delete_meal, 
            bg=self.colors['red'], 
            fg='white', 
            font=('Playpen Sans Arabic', 11, 'bold'), 
            width=12,
            relief=tk.FLAT,
            cursor='hand2',
            height=1
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            btn_frame, 
            text="مسح الحقول", 
            command=clear_fields, 
            bg='#95A5A6', 
            fg='white', 
            font=('Playpen Sans Arabic', 11, 'bold'), 
            width=12,
            relief=tk.FLAT,
            cursor='hand2',
            height=1
        ).pack(side=tk.RIGHT, padx=5)
        
        # Double click to edit
        tree.bind('<Double-1>', lambda e: load_for_edit())
        
        # Enter key to add
        meal_window.bind('<Return>', lambda e: add_or_update_meal())
        
        refresh_list()
        entry_name.focus()

    def open_new_entry(self):
        """فتح نافذة إضافة جديد (بائع أو عميل)"""
        # إنشاء نافذة فرعية
        new_window = tk.Toplevel(self.root)
        new_window.title("إضافة جديد")
        new_window.geometry("600x350") # زيادة الارتفاع
        new_window.configure(bg=self.colors['pink'])
        
        # توسيط النافذة
        new_window.update_idletasks()
        width = new_window.winfo_width()
        height = new_window.winfo_height()
        x = (new_window.winfo_screenwidth() // 2) - (width // 2)
        y = (new_window.winfo_screenheight() // 2) - (height // 2)
        new_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # العنوان
        lbl_title = tk.Label(
            new_window,
            text="إضافة حساب جديد",
            font=('Playpen Sans Arabic', 16, 'bold'),
            bg=self.colors['pink'],
            fg=self.colors['red']
        )
        lbl_title.pack(pady=15)
        
        # نوع الحساب (Radio Buttons)
        type_frame = tk.Frame(new_window, bg=self.colors['pink'])
        type_frame.pack(pady=5)
        
        type_var = tk.StringVar(value="seller")
        
        rb_style = {
            'font': ('Playpen Sans Arabic', 12, 'bold'),
            'bg': self.colors['pink'],
            'activebackground': self.colors['pink'],
            'cursor': 'hand2'
        }
        
        tk.Radiobutton(type_frame, text="بائع", variable=type_var, value="seller", **rb_style).pack(side=tk.RIGHT, padx=20)
        tk.Radiobutton(type_frame, text="عميل", variable=type_var, value="client", **rb_style).pack(side=tk.RIGHT, padx=20)
        
        # إطار للحقول
        fields_frame = tk.Frame(new_window, bg=self.colors['pink'])
        fields_frame.pack(pady=10)
        
        # الاسم (وسط)
        tk.Label(fields_frame, text="الاسم:", font=('Arial', 12, 'bold'), bg=self.colors['pink']).grid(row=0, column=1, padx=5, sticky='e')
        entry_name = tk.Entry(fields_frame, font=('Arial', 14), justify='center', width=25)
        entry_name.grid(row=0, column=0, padx=10, pady=5)
        entry_name.focus()
        
        # دالة الحفظ
        def save_entry():
            name = entry_name.get().strip()
            entry_type = type_var.get()
            phone = ""
            
            if not name:
                messagebox.showwarning("تنبيه", "الرجاء إدخال الاسم", parent=new_window)
                return
            
            try:
                from database import Database
                db = Database()
                
                # التحقق من وجود الاسم في البائعين
                existing_seller = db.get_seller_by_name(name)
                # التحقق من وجود الاسم في العملاء
                existing_client = db.get_client_by_name(name)
                
                if existing_seller:
                    messagebox.showerror("خطأ", f"الاسم '{name}' موجود بالفعل كبائع!", parent=new_window)
                    return
                
                if existing_client:
                    messagebox.showerror("خطأ", f"الاسم '{name}' موجود بالفعل كعميل!", parent=new_window)
                    return
                
                # الحفظ بناءً على النوع
                if entry_type == "seller":
                    db.add_seller_account(name, 0.0, 0.0, phone)
                    msg_type = "بائع"
                else:
                    # إضافة عميل
                    if db.add_client_account(name, phone):
                        msg_type = "عميل"
                    else:
                        # هذا الاحتياط في حال فشل add_client_account لسبب آخر (مثل القيد UNIQUE)
                        messagebox.showerror("خطأ", "حدث خطأ أثناء إضافة العميل (قد يكون موجوداً)", parent=new_window)
                        return

                # رسالة نجاح
                messagebox.showinfo("نجاح", f"تم إضافة ال{msg_type} {name} بنجاح", parent=new_window)
                new_window.destroy()
                
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {e}", parent=new_window)

        # زر الحفظ
        save_btn_style = {
            'font': ('Playpen Sans Arabic', 14, 'bold'),
            'bg': '#800000', # نبيتي غامق
            'fg': 'white',
            'relief': tk.RAISED,
            'bd': 3,
            'cursor': 'hand2',
            'width': 15,
            'activebackground': '#500000',
            'activeforeground': 'white'
        }
        
        tk.Button(new_window, text="حفظ البيانات", command=save_entry, **save_btn_style).pack(pady=20)
        new_window.bind('<Return>', lambda e: save_entry())

    def open_add_collection(self):
        """إضافة تحصيل جديد (دفعة نقدية لبائع)"""
        # إنشاء نافذة فرعية
        coll_window = tk.Toplevel(self.root)
        coll_window.title("إضافة تحصيل نقدية")
        coll_window.geometry("400x300")
        coll_window.configure(bg=self.colors['pink'])
        
        # توسيط النافذة
        coll_window.update_idletasks()
        x = (coll_window.winfo_screenwidth() // 2) - 200
        y = (coll_window.winfo_screenheight() // 2) - 150
        coll_window.geometry(f"400x300+{x}+{y}")
        
        # العنوان
        tk.Label(coll_window, text="تسجيل دفعة نقدية", font=('Playpen Sans Arabic', 16, 'bold'), 
                 bg=self.colors['pink'], fg=self.colors['red']).pack(pady=15)
        
        # جلب قائمة البائعين
        from database import Database
        db = Database()
        sellers = db.get_all_sellers_accounts() # returns list of tuples
        seller_names = [s[1] for s in sellers]
        
        # إطار الحقول
        form_frame = tk.Frame(coll_window, bg=self.colors['pink'])
        form_frame.pack(pady=10)
        
        # اختيار البائع
        tk.Label(form_frame, text="اختر البائع:", font=('Arial', 12, 'bold'), bg=self.colors['pink']).grid(row=0, column=1, padx=5, pady=10, sticky='e')
        combo_seller = ttk.Combobox(form_frame, values=seller_names, font=('Arial', 12), justify='right', width=23)
        combo_seller.grid(row=0, column=0, padx=5, pady=10)
        
        # المبلغ
        tk.Label(form_frame, text="المبلغ:", font=('Arial', 12, 'bold'), bg=self.colors['pink']).grid(row=1, column=1, padx=5, pady=10, sticky='e')
        entry_amount = tk.Entry(form_frame, font=('Arial', 14), justify='center', width=25)
        entry_amount.grid(row=1, column=0, padx=5, pady=10)
        entry_amount.focus()
        
        def save_collection():
            seller_name = combo_seller.get()
            amount_str = entry_amount.get().strip()
            
            if not seller_name or seller_name not in seller_names:
                messagebox.showwarning("تنبيه", "الرجاء اختيار بائع صحيح من القائمة", parent=coll_window)
                return
            
            if not amount_str:
                messagebox.showwarning("تنبيه", "الرجاء إدخال المبلغ", parent=coll_window)
                return
                
            try:
                amount = float(amount_str)
                
                # الحصول على ID البائع
                seller_data = db.get_seller_by_name(seller_name)
                if not seller_data:
                    messagebox.showerror("خطأ", "لم يتم العثور على بيانات البائع", parent=coll_window)
                    return
                
                seller_id = seller_data[0]
                
                # تسجيل المعاملة
                from datetime import datetime
                today = datetime.now().strftime("%Y-%m-%d")
                
                # (seller_id, amount, status, count, weight, price, item_name, date, day_name, equipment, note)
                db.add_seller_transaction(
                    seller_id, 
                    amount, 
                    "مدفوع", 
                    0, 0, 0, 
                    "تحصيل نقدية", 
                    today, 
                    "", "", ""
                )
                
                messagebox.showinfo("نجاح", f"تم تسجيل مبلغ {amount} لحساب {seller_name}", parent=coll_window)
                coll_window.destroy()
                
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال مبلغ صحيح (أرقام فقط)", parent=coll_window)
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ: {e}", parent=coll_window)
        
        # زر الحفظ
        btn_style = {
            'font': ('Playpen Sans Arabic', 14, 'bold'),
            'bg': '#000000',
            'fg': 'white',
            'relief': tk.SOLID,
            'bd': 2,
            'cursor': 'hand2',
            'width': 15
        }
        
        tk.Button(coll_window, text="حفظ التحصيل", command=save_collection, **btn_style).pack(pady=20)
        coll_window.bind('<Return>', lambda e: save_collection())

    def open_add_expense(self):
        """إضافة منصرف جديد"""
        # إنشاء نافذة فرعية
        exp_window = tk.Toplevel(self.root)
        exp_window.title("إضافة منصرف")
        exp_window.geometry("400x400")
        exp_window.configure(bg=self.colors['pink'])
        
        # توسيط النافذة
        exp_window.update_idletasks()
        x = (exp_window.winfo_screenwidth() // 2) - 200
        y = (exp_window.winfo_screenheight() // 2) - 200
        exp_window.geometry(f"400x400+{x}+{y}")
        
        # العنوان
        tk.Label(exp_window, text="تسجيل مصروف جديد", font=('Playpen Sans Arabic', 16, 'bold'), 
                 bg=self.colors['pink'], fg=self.colors['red']).pack(pady=15)
        
        form = tk.Frame(exp_window, bg=self.colors['pink'])
        form.pack(pady=10)
        
        # Description
        tk.Label(form, text="بيان المصروف:", font=('Arial', 12, 'bold'), bg=self.colors['pink']).grid(row=0, column=1, padx=5, pady=10, sticky='e')
        entry_desc = tk.Entry(form, font=('Arial', 12), justify='right', width=25)
        entry_desc.grid(row=0, column=0, padx=5, pady=10)
        entry_desc.focus()
        
        # Amount
        tk.Label(form, text="المبلغ:", font=('Arial', 12, 'bold'), bg=self.colors['pink']).grid(row=1, column=1, padx=5, pady=10, sticky='e')
        entry_amount = tk.Entry(form, font=('Arial', 14), justify='center', width=25)
        entry_amount.grid(row=1, column=0, padx=5, pady=10)
        
        # Note
        tk.Label(form, text="ملاحظات:", font=('Arial', 12, 'bold'), bg=self.colors['pink']).grid(row=2, column=1, padx=5, pady=10, sticky='e')
        entry_note = tk.Entry(form, font=('Arial', 12), justify='right', width=25)
        entry_note.grid(row=2, column=0, padx=5, pady=10)
        
        def save_expense():
            desc = entry_desc.get().strip()
            amount_str = entry_amount.get().strip()
            note = entry_note.get().strip()
            
            if not desc:
                messagebox.showwarning("تنبيه", "الرجاء إدخال بيان المصروف", parent=exp_window)
                return
            if not amount_str:
                messagebox.showwarning("تنبيه", "الرجاء إدخال المبلغ", parent=exp_window)
                return
                
            try:
                amount = float(amount_str)
                from datetime import datetime
                today = datetime.now().strftime("%Y-%m-%d")
                
                from database import Database
                db = Database()
                db.add_expense(desc, amount, today, note)
                
                messagebox.showinfo("نجاح", "تم تسجيل المصروف بنجاح", parent=exp_window)
                exp_window.destroy()
                
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال مبلغ صحيح", parent=exp_window)
                
        # زر الحفظ
        btn_style = {
            'font': ('Playpen Sans Arabic', 14, 'bold'),
            'bg': '#000000',
            'fg': 'white',
            'relief': tk.SOLID,
            'bd': 2,
            'cursor': 'hand2',
            'width': 15
        }
        
        tk.Button(exp_window, text="حفظ المصروف", command=save_expense, **btn_style).pack(pady=20)
        exp_window.bind('<Return>', lambda e: save_expense())

    def open_reports(self):
        """فتح صفحة التقارير اليومية والشهرية"""
        from reports_page import DailyReportsPage
        DailyReportsPage(self.root)

    def open_data_sync(self):
        """فتح نافذة مزامنة البيانات"""
        from tkinter import filedialog
        import os
        
        sync_window = tk.Toplevel(self.root)
        sync_window.title("مزامنة البيانات")
        sync_window.geometry("700x600")
        sync_window.configure(bg=self.colors['pink'])
        
        # توسيط النافذة
        sync_window.update_idletasks()
        x = (sync_window.winfo_screenwidth() // 2) - 350
        y = (sync_window.winfo_screenheight() // 2) - 300
        sync_window.geometry(f"700x600+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(sync_window, bg=self.colors['red'], height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame, 
            text="مزامنة البيانات", 
            font=('Playpen Sans Arabic', 20, 'bold'), 
            bg=self.colors['red'], 
            fg='white'
        ).pack(pady=20)
        
        # Main Content
        content_frame = tk.Frame(sync_window, bg=self.colors['pink'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Info Card
        info_card = tk.Frame(content_frame, bg=self.colors['white'], padx=20, pady=15)
        info_card.pack(fill=tk.X, pady=(0, 15))
        
        info_text = """
نظام مزامنة البيانات يتيح لك:
• تصدير جميع البيانات إلى ملف احتياطي
• نقل البيانات إلى جهاز آخر
• استيراد البيانات من ملف احتياطي
• الاحتفاظ بنسخ احتياطية يومية
        """
        
        tk.Label(
            info_card, 
            text=info_text, 
            font=('Arial', 11), 
            bg=self.colors['white'], 
            fg='#2C3E50',
            justify='right'
        ).pack(anchor='e')
        
        # Export Section
        export_card = tk.Frame(content_frame, bg=self.colors['white'], padx=20, pady=15)
        export_card.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            export_card, 
            text="📤 تصدير البيانات", 
            font=('Playpen Sans Arabic', 14, 'bold'), 
            bg=self.colors['white'], 
            fg=self.colors['red']
        ).pack(anchor='e', pady=(0, 10))
        
        tk.Label(
            export_card, 
            text="إنشاء نسخة احتياطية من جميع البيانات", 
            font=('Arial', 10), 
            bg=self.colors['white'], 
            fg='#7F8C8D'
        ).pack(anchor='e', pady=(0, 10))
        
        def export_data():
            try:
                from data_sync import DataSync
                sync = DataSync()
                filepath = sync.create_daily_backup()
                
                messagebox.showinfo(
                    "نجاح", 
                    f"تم تصدير البيانات بنجاح!\n\nالملف: {os.path.basename(filepath)}\nالمسار: {filepath}",
                    parent=sync_window
                )
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء التصدير:\n{str(e)}", parent=sync_window)
        
        tk.Button(
            export_card, 
            text="تصدير البيانات الآن", 
            command=export_data, 
            bg=self.colors['orange'], 
            fg='white', 
            font=('Playpen Sans Arabic', 12, 'bold'), 
            width=20,
            relief=tk.FLAT,
            cursor='hand2',
            height=2
        ).pack(pady=5)
        
        # Import Section
        import_card = tk.Frame(content_frame, bg=self.colors['white'], padx=20, pady=15)
        import_card.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            import_card, 
            text="📥 استيراد البيانات", 
            font=('Playpen Sans Arabic', 14, 'bold'), 
            bg=self.colors['white'], 
            fg=self.colors['red']
        ).pack(anchor='e', pady=(0, 10))
        
        tk.Label(
            import_card, 
            text="استيراد البيانات من ملف احتياطي", 
            font=('Arial', 10), 
            bg=self.colors['white'], 
            fg='#7F8C8D'
        ).pack(anchor='e', pady=(0, 10))
        
        # Merge mode selection
        merge_frame = tk.Frame(import_card, bg=self.colors['white'])
        merge_frame.pack(anchor='e', pady=(0, 10))
        
        tk.Label(
            merge_frame, 
            text="طريقة الدمج:", 
            font=('Arial', 10, 'bold'), 
            bg=self.colors['white']
        ).pack(side=tk.RIGHT, padx=5)
        
        merge_var = tk.StringVar(value='update')
        
        merge_options = [
            ('تحديث (إضافة وتحديث)', 'update'),
            ('استبدال (حذف القديم)', 'replace'),
            ('تخطي (إضافة فقط)', 'skip')
        ]
        
        for text, value in merge_options:
            tk.Radiobutton(
                merge_frame,
                text=text,
                variable=merge_var,
                value=value,
                font=('Arial', 9),
                bg=self.colors['white'],
                activebackground=self.colors['white']
            ).pack(side=tk.RIGHT, padx=5)
        
        def import_data():
            # فتح نافذة اختيار الملف
            filepath = filedialog.askopenfilename(
                title="اختر ملف النسخة الاحتياطية",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialdir="data_exports",
                parent=sync_window
            )
            
            if not filepath:
                return
            
            # تأكيد الاستيراد
            confirm = messagebox.askyesno(
                "تأكيد الاستيراد",
                f"هل أنت متأكد من استيراد البيانات من:\n{os.path.basename(filepath)}\n\nطريقة الدمج: {merge_var.get()}",
                parent=sync_window
            )
            
            if not confirm:
                return
            
            try:
                from data_sync import DataSync
                sync = DataSync()
                stats = sync.import_data(filepath, merge_var.get())
                
                messagebox.showinfo(
                    "نجاح", 
                    f"تم استيراد البيانات بنجاح!\n\n"
                    f"الجداول المعالجة: {stats['tables_processed']}\n"
                    f"السجلات المُدرجة: {stats['rows_inserted']}\n"
                    f"السجلات المُحدثة: {stats['rows_updated']}\n"
                    f"السجلات المتخطاة: {stats['rows_skipped']}\n"
                    f"الأخطاء: {len(stats['errors'])}",
                    parent=sync_window
                )
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء الاستيراد:\n{str(e)}", parent=sync_window)
        
        tk.Button(
            import_card, 
            text="استيراد من ملف", 
            command=import_data, 
            bg=self.colors['yellow'], 
            fg='#2C3E50', 
            font=('Playpen Sans Arabic', 12, 'bold'), 
            width=20,
            relief=tk.FLAT,
            cursor='hand2',
            height=2
        ).pack(pady=5)
        
        # View Backups Section
        backups_card = tk.Frame(content_frame, bg=self.colors['white'], padx=20, pady=15)
        backups_card.pack(fill=tk.X)
        
        tk.Label(
            backups_card, 
            text="📦 إدارة النسخ الاحتياطية", 
            font=('Playpen Sans Arabic', 14, 'bold'), 
            bg=self.colors['white'], 
            fg=self.colors['red']
        ).pack(anchor='e', pady=(0, 10))
        
        def view_backups():
            try:
                from data_sync import DataSync
                sync = DataSync()
                backups = sync.list_backups()
                
                if not backups:
                    messagebox.showinfo("النسخ الاحتياطية", "لا توجد نسخ احتياطية", parent=sync_window)
                    return
                
                # إنشاء نافذة لعرض النسخ
                backups_list_window = tk.Toplevel(sync_window)
                backups_list_window.title("النسخ الاحتياطية المتاحة")
                backups_list_window.geometry("600x400")
                backups_list_window.configure(bg=self.colors['pink'])
                
                # توسيط
                backups_list_window.update_idletasks()
                x = (backups_list_window.winfo_screenwidth() // 2) - 300
                y = (backups_list_window.winfo_screenheight() // 2) - 200
                backups_list_window.geometry(f"600x400+{x}+{y}")
                
                # Listbox
                listbox_frame = tk.Frame(backups_list_window, bg=self.colors['white'])
                listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                
                scrollbar = tk.Scrollbar(listbox_frame)
                scrollbar.pack(side=tk.LEFT, fill=tk.Y)
                
                listbox = tk.Listbox(
                    listbox_frame,
                    font=('Arial', 10),
                    yscrollcommand=scrollbar.set,
                    bg='white',
                    selectmode=tk.SINGLE
                )
                listbox.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
                scrollbar.config(command=listbox.yview)
                
                for backup in backups:
                    display_text = f"{backup['filename']} - {backup['modified'].strftime('%Y-%m-%d %H:%M')} - {backup['size_kb']:.2f} KB"
                    listbox.insert(tk.END, display_text)
                
                def open_folder():
                    import subprocess
                    folder_path = os.path.abspath("data_exports")
                    if os.path.exists(folder_path):
                        subprocess.Popen(f'explorer "{folder_path}"')
                
                tk.Button(
                    backups_list_window,
                    text="فتح مجلد النسخ الاحتياطية",
                    command=open_folder,
                    bg=self.colors['orange'],
                    fg='white',
                    font=('Playpen Sans Arabic', 11, 'bold'),
                    relief=tk.FLAT,
                    cursor='hand2'
                ).pack(pady=10)
                
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ:\n{str(e)}", parent=sync_window)
        
        tk.Button(
            backups_card, 
            text="عرض النسخ الاحتياطية", 
            command=view_backups, 
            bg='#95A5A6', 
            fg='white', 
            font=('Playpen Sans Arabic', 11, 'bold'), 
            width=20,
            relief=tk.FLAT,
            cursor='hand2',
            height=1
        ).pack(pady=5)



def main():
    # تهيئة قاعدة البيانات
    from database import Database
    db = Database()
    
    # إنشاء النافذة الرئيسية
    root = tk.Tk()
    app = StartMenu(root)
    root.mainloop()


if __name__ == "__main__":
    main()

