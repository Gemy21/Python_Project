import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import ColorManager

class AccountsPage:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.db = Database()
        
        # الألوان الجديدة المطلوبة
        self.colors = {
            'window_bg': '#FFB347',   # برتقالي متوسط للخلفية
            'header_bg': '#6C3483',   # بنفسجي غامق للعناوين
            'col_total': '#D7BDE2',   # بنفسجي فاتح (اجمالي السماح)
            'col_remain': '#AED6F1',  # أزرق فاتح (المتبقي)
            'col_phone': '#F9E79F',   # أصفر فاتح (رقم الهاتف)
            'col_name': '#F5CBA7',    # برتقالي فاتح (اسم البائع)
            'white': '#FFFFFF',
            'btn_bg': '#800000',      # نبيتي للأزرار
            'search_bg': '#FFF3E0'    # لون خلفية البحث
        }
        
        self.selected_account_id = None
        self.selected_seller_name = None
        self.selected_row_entries = None
        
        # إنشاء نافذة جديدة
        self.window = tk.Toplevel(parent_window)
        self.window.title("صفحة الحسابات")
        self.window.geometry("1000x700")
        self.window.configure(bg=self.colors['window_bg'])
        self.window.resizable(True, True)
        
        # إطار العنوان
        title_frame = tk.Frame(self.window, bg=self.colors['header_bg'], height=70)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="حسابات البائعين",
            font=('Playpen Sans Arabic', 22, 'bold'),
            bg=self.colors['header_bg'],
            fg=self.colors['white']
        )
        title_label.pack(pady=15)
        
        # --- شريط البحث ---
        search_frame = tk.Frame(self.window, bg=self.colors['window_bg'])
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(search_frame, text="بحث باسم البائع:", font=('Arial', 14, 'bold'), bg=self.colors['window_bg']).pack(side=tk.RIGHT, padx=10)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Arial', 14), justify='right', width=30)
        search_entry.pack(side=tk.RIGHT, padx=5)
        
        # إطار الأزرار العلوية
        buttons_frame = tk.Frame(self.window, bg=self.colors['window_bg'])
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # زر الإغلاق
        btn_close = tk.Button(
            buttons_frame,
            text="إغلاق",
            command=self.window.destroy,
            bg=self.colors['btn_bg'],
            fg='white',
            font=('Playpen Sans Arabic', 12, 'bold'),
            relief=tk.RAISED,
            bd=2,
            cursor='hand2',
            width=12
        )
        btn_close.pack(side=tk.RIGHT, padx=5)
        
        # أزرار إضافية
        top_button_style = {
            'font': ('Playpen Sans Arabic', 12, 'bold'),
            'bg': self.colors['btn_bg'],
            'fg': 'white',
            'relief': tk.RAISED,
            'bd': 2,
            'cursor': 'hand2',
            'width': 12
        }
        
        self.current_account_btn = tk.Button(buttons_frame, text="حساب جاري", command=self.open_current_account, **top_button_style)
        self.current_account_btn.pack(side=tk.RIGHT, padx=5)
        
        self.review_btn_top = tk.Button(buttons_frame, text="مراجعة و تعديل", command=self.open_review_modify, **top_button_style)
        self.review_btn_top.pack(side=tk.RIGHT, padx=5)
        
        # إطار الجدول
        table_frame = tk.Frame(self.window, bg=self.colors['window_bg'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # إطار داخلي للجدول
        table_canvas = tk.Canvas(table_frame, bg=self.colors['window_bg'], highlightthickness=0)
        table_canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        table_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table_canvas.yview)
        table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        table_canvas.configure(yscrollcommand=table_scrollbar.set)
        
        table_inner = tk.Frame(table_canvas, bg=self.colors['window_bg'])
        table_inner_id = table_canvas.create_window((0, 0), window=table_inner, anchor='nw')
        
        table_inner.bind("<Configure>", lambda e: table_canvas.configure(scrollregion=table_canvas.bbox("all")))
        table_canvas.bind("<Configure>", lambda e: table_canvas.itemconfigure(table_inner_id, width=e.width))
        
        # رأس الجدول
        headers = ['اجمالي السماح', 'المتبقي', 'اسم البائع']
        header_colors = [self.colors['col_total'], self.colors['col_remain'], self.colors['col_name']]
        
        header_style = {
            'font': ('Playpen Sans Arabic', 14, 'bold'),
            'fg': 'black',
            'relief': tk.RAISED,
            'bd': 2,
            'height': 2
        }
        
        for col, header in enumerate(headers):
            label = tk.Label(table_inner, text=header, bg=header_colors[col], **header_style)
            label.grid(row=0, column=col, sticky='nsew', padx=1, pady=1)
        
        # إنشاء الصفوف
        self.table_rows = []
        self.num_rows = 20
        self.column_colors = header_colors # استخدام نفس ألوان الرأس للأعمدة
        
        entry_style = {'font': ('Playpen Sans Arabic', 14), 'relief': tk.SUNKEN, 'bd': 1, 'justify': 'center'}
        
        for row in range(1, self.num_rows + 1):
            row_entries = []
            for col in range(3):
                entry = tk.Entry(table_inner, **entry_style, bg=self.column_colors[col])
                entry.grid(row=row, column=col, sticky='nsew', padx=1, pady=1, ipady=8)
                row_entries.append(entry)
            
            # تصحيح ربط الحدث للصف بالكامل
            for entry in row_entries:
                 entry.bind('<Button-1>', lambda e, r=row_entries: self.select_row_event(e, r))

            self.table_rows.append(row_entries)
        
        # توزيع الأعمدة
        for col in range(3):
            table_inner.grid_columnconfigure(col, weight=1)
            
        self.all_accounts = [] # لتخزين كل البيانات للبحث
        self.load_data()
        
        # أزرار أسفل الجدول (في المنتصف)
        bottom_buttons_style = {
            'font': ('Playpen Sans Arabic', 14, 'bold'),
            'bg': self.colors['btn_bg'],
            'fg': self.colors['white'],
            'relief': tk.RAISED,
            'bd': 2,
            'cursor': 'hand2',
            'width': 14,
            'height': 1,
            'padx': 10,
            'pady': 5,
            'activebackground': '#500000',
            'activeforeground': 'white'
        }
        
        self.bottom_buttons_frame = tk.Frame(self.window, height=80, bg=self.colors['window_bg'])
        self.bottom_buttons_frame.pack(fill=tk.X, pady=(10, 20))
        
        center_buttons_holder = tk.Frame(self.bottom_buttons_frame, bg=self.colors['window_bg'])
        center_buttons_holder.pack()
        
        self.customer_income_btn = tk.Button(
            center_buttons_holder,
            text="وارد العملاء",
            command=self.open_customer_income,
            **bottom_buttons_style
        )
        self.customer_income_btn.pack(side=tk.LEFT, padx=15)
        
        self.arrears_btn = tk.Button(
            center_buttons_holder,
            text="متأخرات",
            command=self.open_arrears,
            **bottom_buttons_style
        )
        self.arrears_btn.pack(side=tk.LEFT, padx=15)
        
    def on_search_change(self, *args):
        """تصفية الجدول بناءً على البحث"""
        query = self.search_var.get().strip().lower()
        self.filter_data(query)

    def load_data(self):
        """تحميل البيانات من قاعدة البيانات"""
        self.all_accounts = self.db.get_all_sellers_accounts()
        self.filter_data("")

    def filter_data(self, query):
        """عرض البيانات المصفاة"""
        # مسح الجدول
        for row_entries in self.table_rows:
            for i, entry in enumerate(row_entries):
                entry.delete(0, tk.END)
                entry.config(bg=self.column_colors[i]) # إعادة اللون الأصلي
                if hasattr(row_entries[0], 'account_id'):
                    del row_entries[0].account_id
                    del row_entries[0].seller_name

        # تصفية البيانات
        filtered_accounts = []
        for acc in self.all_accounts:
            # acc: id, seller_name, remaining, credit, phone
            name = acc[1]
            if query in name.lower():
                filtered_accounts.append(acc)
        
        # ملء الجدول
        for i, account in enumerate(filtered_accounts):
            if i >= self.num_rows: break
            
            row_entries = self.table_rows[i]
            
            # تخزين البيانات
            row_entries[0].account_id = account[0]
            row_entries[0].seller_name = account[1]
            
            # ملء الخانات
            # ملء الخانات
            row_entries[0].insert(0, str(account[3])) # اجمالي السماح
            row_entries[1].insert(0, str(account[2])) # المتبقي
            
            row_entries[2].insert(0, account[1]) # الاسم

    def select_row_event(self, event, row_entries):
        """معالجة حدث النقر على الصف"""
        # الحصول على معرف الحساب واسم البائع من الصف المحدد
        # قمنا بتخزينها في أول خانة في load_data
        if hasattr(row_entries[0], 'account_id'):
            self.select_row(row_entries[0].account_id, row_entries[0].seller_name, row_entries)
        else:
            # صف فارغ
            self.selected_account_id = None
            self.selected_seller_name = None
            # يمكن تنظيف التحديد السابق
            if self.selected_row_entries:
                for i, entry in enumerate(self.selected_row_entries):
                    entry.config(bg=self.column_colors[i])
            self.selected_row_entries = None

    def select_row(self, account_id, seller_name, row_entries):
        """تحديد الصف الحالي"""
        self.selected_account_id = account_id
        self.selected_seller_name = seller_name
        
        # إعادة تعيين ألوان الصفوف السابقة
        if self.selected_row_entries:
            for i, entry in enumerate(self.selected_row_entries):
                entry.config(bg=self.column_colors[i])
        
        # تمييز الصف الحالي
        self.selected_row_entries = row_entries
        for entry in row_entries:
            entry.config(bg='#D5F5E3')  # لون تمييز فاتح (أخضر فاتح)
    
    def add_account(self):
        """إضافة حساب جديد - حفظ البيانات من الصفوف"""
        self.save_all_data()
        messagebox.showinfo("نجح", "تم حفظ جميع البيانات")
    
    def edit_account(self):
        """تعديل حساب - حفظ البيانات من الصفوف"""
        self.save_all_data()
        messagebox.showinfo("نجح", "تم حفظ جميع البيانات")
    
    def delete_account(self):
        """حذف حساب - مسح صف محدد"""
        # البحث عن الصف المحدد (يمكن تحسينه لاحقاً)
        messagebox.showinfo("معلومة", "يمكنك مسح البيانات يدوياً من الصف ثم الضغط على حفظ")
    
    def save_all_data(self):
        """حفظ جميع البيانات من الصفوف إلى قاعدة البيانات"""
        # حذف جميع الحسابات الحالية
        accounts = self.db.get_all_sellers_accounts()
        for account in accounts:
            account_id = account[0]
            self.db.delete_seller_account(account_id)
        
        # إضافة البيانات الجديدة من الصفوف
        for row_entries in self.table_rows:
            # اجمالي السماح (العمود الأول)
            total_credit_str = row_entries[0].get().strip()
            # المتبقي (العمود الثاني)
            remaining_str = row_entries[1].get().strip()
            # اسم البائع (العمود الثالث)
            seller_name = row_entries[2].get().strip()
            
            # إذا كان هناك اسم بائع، احفظ البيانات
            if seller_name:
                try:
                    remaining = float(remaining_str) if remaining_str else 0.0
                    total_credit = float(total_credit_str) if total_credit_str else 0.0
                    self.db.add_seller_account(seller_name, remaining, total_credit, "")
                except ValueError:
                    pass  # تجاهل الأخطاء في الأرقام
    
    # وظائف الأزرار الإضافية
    def open_current_account(self):
        """فتح شاشة الحساب الجاري للبائع المحدد"""
        if not self.selected_account_id:
            messagebox.showwarning("تنبيه", "الرجاء تحديد بائع من الجدول أولاً")
            return
            
        CurrentAccountPage(self.window, self.selected_account_id, self.selected_seller_name, self.colors)
    
    def open_review_modify(self):
        """فتح صفحة برنامج البائعين (مراجعة وتعديل)"""
        from sellers_page import SellersPage
        SellersPage(self.window)
    
    def open_customer_income(self):
        messagebox.showinfo("وارد العملاء", "سيتم تطوير شاشة وارد العملاء لاحقاً.")
    
    def open_arrears(self):
        messagebox.showinfo("متأخرات", "سيتم تطوير شاشة المتأخرات لاحقاً.")


class AccountDialog:
    def __init__(self, parent, title, seller_name="", remaining="", total_credit="", colors=None):
        self.result = None
        self.colors = colors if colors else {
            'orange': '#F39C12',  # Medium Orange
            'white': '#FFFFFF',
            'yellow': '#AED6F1',  # Light Blue (replacing yellow)
            'pink': '#F5B7B1',    # Pink
            'red': '#EC7063'      # Light Red
        }
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=self.colors['pink'])
        
        # مركز النافذة
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (250 // 2)
        self.dialog.geometry(f"400x250+{x}+{y}")
        
        # العنوان
        title_label = tk.Label(
            self.dialog,
            text=title,
            font=('Playpen Sans Arabic', 16, 'bold'),
            pady=10,
            bg=self.colors['pink'],
            fg=self.colors['red']
        )
        title_label.pack()
        
        # إطار الحقول
        fields_frame = tk.Frame(self.dialog, bg=self.colors['white'])
        fields_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # اسم البائع
        tk.Label(fields_frame, text="اسم البائع:", font=('Playpen Sans Arabic', 12), bg=self.colors['white']).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_name = tk.Entry(fields_frame, font=('Playpen Sans Arabic', 12), width=25, bg=self.colors['yellow'])
        self.entry_name.grid(row=0, column=1, pady=5, padx=10)
        self.entry_name.insert(0, seller_name)
        
        # المتبقي
        tk.Label(fields_frame, text="المتبقي:", font=('Playpen Sans Arabic', 12), bg=self.colors['white']).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_remaining = tk.Entry(fields_frame, font=('Playpen Sans Arabic', 12), width=25, bg=self.colors['pink'])
        self.entry_remaining.grid(row=1, column=1, pady=5, padx=10)
        self.entry_remaining.insert(0, str(remaining))
        
        # اجمالي السماح
        tk.Label(fields_frame, text="اجمالي السماح:", font=('Playpen Sans Arabic', 12), bg=self.colors['white']).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_credit = tk.Entry(fields_frame, font=('Playpen Sans Arabic', 12), width=25, bg=self.colors['white'])
        self.entry_credit.grid(row=2, column=1, pady=5, padx=10)
        self.entry_credit.insert(0, str(total_credit))
        
        # الأزرار
        buttons_frame = tk.Frame(self.dialog, bg=self.colors['pink'])
        buttons_frame.pack(pady=10)
        
        dialog_button_style = {
            'font': ('Playpen Sans Arabic', 12, 'bold'),
            'bg': self.colors['orange'],
            'fg': 'white',
            'width': 10,
            'padx': 10,
            'cursor': 'hand2',
            'relief': tk.RAISED,
            'bd': 2,
            'activebackground': '#b84300',
            'activeforeground': 'white'
        }
        
        btn_save = tk.Button(
            buttons_frame,
            text="حفظ",
            command=self.save,
            **dialog_button_style
        )
        btn_save.pack(side=tk.LEFT, padx=5)
        
        btn_cancel = tk.Button(
            buttons_frame,
            text="إلغاء",
            command=self.cancel,
            **dialog_button_style
        )
        btn_cancel.pack(side=tk.LEFT, padx=5)
        
        # التركيز على حقل الاسم
        self.entry_name.focus()
        
        # ربط Enter بحفظ
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def save(self):
        """حفظ البيانات"""
        self.result = (
            self.entry_name.get(),
            self.entry_remaining.get(),
            self.entry_credit.get()
        )
        self.dialog.destroy()
    
    def cancel(self):
        """إلغاء"""
        self.dialog.destroy()


class CurrentAccountPage:
    def __init__(self, parent, seller_id, seller_name, colors):
        self.seller_id = seller_id
        self.seller_name = seller_name
        self.colors = colors
        self.db = Database()
        
        # جلب الرصيد السابق (من جدول الحسابات الرئيسي)
        self.account_data = self.get_account_data()
        self.old_balance = self.account_data[2] if self.account_data else 0.0 # remaining_amount
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"كشف بيع - {seller_name}")
        self.window.geometry("1300x750")
        # استخدام window_bg أو قيمة افتراضية
        bg_color = self.colors.get('window_bg', '#FFB347')
        self.window.configure(bg=bg_color)
        self.window.resizable(True, True)
        
        # العنوان
        header_bg = self.colors.get('header_bg', '#800000')
        title_frame = tk.Frame(self.window, bg=header_bg, height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text=f"كشف بيع: {seller_name}",
            font=('Playpen Sans Arabic', 18, 'bold'),
            bg=header_bg,
            fg='white'
        ).pack(pady=10)
        
        # إطار الجدول
        table_frame = tk.Frame(self.window, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas للجدول
        self.canvas = tk.Canvas(table_frame, bg='white')
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # تعريف الأعمدة
        # تعريف الأعمدة (تم التحديث حسب الصورة)
        # من اليمين لليسار: المبلغ، الحالة، العدد، الوزن، السعر، الصنف، التاريخ، اليوم، العدة
        # في الكود (0-based index):
        # 0: العدة, 1: اليوم, 2: التاريخ, 3: الصنف, 4: السعر, 5: الوزن, 6: العدد, 7: الحالة, 8: المبلغ
        self.headers = [
            "العدة", "اليوم", "التاريخ", "الصنف", 
            "السعر", "الوزن", "العدد", "الحالة", "المبلغ"
        ]
        
        # رسم العناوين
        header_style = {
            'font': ('Playpen Sans Arabic', 12, 'bold'),
            'bg': '#A93226', # Dark Red
            'fg': 'white',
            'relief': tk.RAISED,
            'bd': 1,
            'pady': 8
        }
        
        for i, header in enumerate(self.headers):
            tk.Label(
                self.scrollable_frame, 
                text=header, 
                **header_style
            ).grid(row=0, column=i, padx=1, pady=1, sticky='nsew')
            self.scrollable_frame.grid_columnconfigure(i, weight=1)
            
        self.rows = []
        # self.load_data() # Moved to end of init
        
        # --- الشريط السفلي (الفوتر) ---
        footer_frame = tk.Frame(self.window, bg='#E67E22', height=100)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        # قسم الحسابات (يمين الفوتر) - اجمالي المتبقي
        totals_frame = tk.Frame(footer_frame, bg='#E67E22')
        totals_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        tk.Label(totals_frame, text="اجمالي المتبقي", font=('Playpen Sans Arabic', 14, 'bold'), bg='#E67E22', fg='white').pack(anchor='e')
        self.lbl_footer_remaining = tk.Label(totals_frame, text="0.0", font=('Arial', 16, 'bold'), bg='white', fg='black', width=15, relief=tk.SUNKEN)
        self.lbl_footer_remaining.pack(pady=5)

        # الأزرار (يسار الفوتر)
        buttons_container = tk.Frame(footer_frame, bg='#E67E22')
        buttons_container.pack(side=tk.LEFT, padx=20, fill=tk.Y)

        # تنسيق الأزرار (ألوان محددة)
        btn_style_base = {'font': ('Arial', 11, 'bold'), 'fg': 'white', 'relief': tk.RAISED, 'bd': 2, 'width': 10, 'height': 2}
        
        # ترتيب الأزرار من اليسار لليمين (حسب الصورة: خروج، طباعة، اضافة دفع، تعديل دفع، تعديل وجبة، تحصيل عدة)
        # Colors: Exit(Red), Print(Blue/Black), Add Pay(Red), Edit Pay(Blue), Edit Meal(Green), Collect Equip(Purple)
        
        btns = [
            ("خروج", self.window.destroy, '#C0392B'),
            ("طباعة", self.print_invoice, '#2C3E50'),
            ("إضافة دفع", self.open_add_payment_dialog, '#C0392B'),
            ("تعديل الدفع", self.edit_payment, '#2980B9'),
            ("تحصيل عدة", self.collect_equipment, '#8E44AD')
        ]
        
        for text, cmd, color in btns:
            tk.Button(buttons_container, text=text, command=cmd, bg=color, **btn_style_base).pack(side=tk.LEFT, padx=3)

        # تحميل البيانات بعد إنشاء الواجهة
        self.load_data()

    def get_account_data(self):
        """جلب بيانات الحساب الرئيسي للبائع"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, seller_name, remaining_amount, total_credit FROM sellers_accounts WHERE id = ?', (self.seller_id,))
        res = cursor.fetchone()
        conn.close()
        return res

    def _on_canvas_configure(self, event):
        """تحديث عرض الإطار الداخلي ليطابق عرض الـ Canvas"""
        self.canvas.itemconfig(self.canvas_frame_id, width=event.width)

    # --- وظائف الأزرار ---
    def collect_equipment(self): messagebox.showinfo("تحصيل عدة", "سيتم التنفيذ قريباً")
    def edit_meal(self): messagebox.showinfo("تعديل", "يمكنك التعديل مباشرة في الجدول ثم الضغط على حفظ")
    def edit_payment(self): messagebox.showinfo("تعديل", "يمكنك تعديل مبلغ الدفع في الجدول مباشرة")
    def open_add_payment_dialog(self):
        """فتح نافذة إضافة دفع"""
        dialog = tk.Toplevel(self.window)
        dialog.title("إضافة دفع أو خصم")
        dialog.geometry("800x250") # Increased size
        bg_color = self.colors.get('pink', '#F5CBA7')  # Fallback to light orange
        dialog.configure(bg=bg_color)
        
        # توسيط
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400)
        y = (dialog.winfo_screenheight() // 2) - (125)
        dialog.geometry(f"800x250+{x}+{y}")

        # إطار رئيسي
        main_frame = tk.Frame(dialog, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # العناوين (شريط أصفر)
        headers_frame = tk.Frame(main_frame, bg='#F1C40F') # Yellow
        headers_frame.pack(fill=tk.X, pady=(0, 5))
        
        # استخدام pack للتوزيع المتساوي
        # العناوين: ملحوظة (يسار)، سماح (وسط)، دفع (يمين)
        
        lbl_style = {'font': ('Arial', 14, 'bold'), 'bg': '#F1C40F', 'fg': 'black', 'pady': 10}
        
        tk.Label(headers_frame, text="ملحوظة", **lbl_style).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Label(headers_frame, text="سماح", **lbl_style).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Label(headers_frame, text="دفع", **lbl_style).pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # الحقول (شريط أبيض/رمادي)
        inputs_frame = tk.Frame(main_frame, bg='#ECF0F1')
        inputs_frame.pack(fill=tk.X, pady=5)
        
        entry_style = {'font': ('Arial', 14), 'justify': 'center', 'relief': tk.FLAT}
        
        # حاويات للحقول لضمان التناسق مع العناوين
        f1 = tk.Frame(inputs_frame, bg='#ECF0F1', bd=1, relief=tk.SOLID); f1.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        f2 = tk.Frame(inputs_frame, bg='#ECF0F1', bd=1, relief=tk.SOLID); f2.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        f3 = tk.Frame(inputs_frame, bg='#ECF0F1', bd=1, relief=tk.SOLID); f3.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        entry_note = tk.Entry(f1, **entry_style)
        entry_note.pack(fill=tk.BOTH, expand=True, ipady=5)
        
        entry_discount = tk.Entry(f2, **entry_style)
        entry_discount.pack(fill=tk.BOTH, expand=True, ipady=5)
        
        entry_payment = tk.Entry(f3, **entry_style)
        entry_payment.pack(fill=tk.BOTH, expand=True, ipady=5)
        
        # التركيز على الدفع
        entry_payment.focus()

        def confirm_payment():
            payment_str = entry_payment.get().strip()
            discount_str = entry_discount.get().strip()
            note = entry_note.get().strip()
            
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            added = False
            
            # إضافة الدفع
            if payment_str:
                try:
                    amount = float(payment_str)
                    item_name = f"دفعة نقدية {('(' + note + ')') if note else ''}"
                    # (seller_id, amount, status, count, weight, price, item_name, date, day_name, equipment, note)
                    self.db.add_seller_transaction(
                        self.seller_id, amount, "مدفوع", 0, 0, 0, item_name, today, "", "", note
                    )
                    added = True
                except ValueError:
                    messagebox.showerror("خطأ", "الرجاء إدخال مبلغ دفع صحيح")
                    return

            # إضافة السماح
            if discount_str:
                try:
                    amount = float(discount_str)
                    item_name = f"سماح {('(' + note + ')') if note else ''}"
                    self.db.add_seller_transaction(
                        self.seller_id, amount, "مدفوع", 0, 0, 0, item_name, today, "", "", note
                    )
                    added = True
                except ValueError:
                    messagebox.showerror("خطأ", "الرجاء إدخال مبلغ سماح صحيح")
                    return

            if added:
                dialog.destroy()
                # إعادة تحميل البيانات لتحديث الجدول والإجماليات
                # أولاً مسح الجدول الحالي
                for row_entries in self.rows:
                    for entry in row_entries:
                        entry.destroy()
                self.rows = []
                # مسح محتوى الـ scrollable_frame للتأكد (العناوين ثابتة لكن الصفوف متغيرة)
                for widget in self.scrollable_frame.winfo_children():
                    if int(widget.grid_info()['row']) > 0: # إبقاء العناوين (row 0)
                        widget.destroy()
                
                self.load_data()
                messagebox.showinfo("نجاح", "تم إضافة الدفع بنجاح")
            else:
                dialog.destroy()

        tk.Button(dialog, text="تأكيد", command=confirm_payment, bg=self.colors.get('orange', '#F39C12'), fg='white', font=('Arial', 12, 'bold'), width=15).pack(pady=10)
        dialog.bind('<Return>', lambda e: confirm_payment())

    def print_invoice(self): 
        """طباعة الفاتورة"""
        from print_utils import PrintPreviewWindow
        from datetime import datetime
        
        # جمع بيانات الفاتورة
        transactions = []
        
        # تجاهل الصف الأخير لأنه عادة ما يكون صف إدخال جديد فارغ
        rows_to_process = self.rows[:-1] if len(self.rows) > 0 else []
        
        for row_entries in rows_to_process:
            try:
                # الفهارس بناءً على self.headers:
                # 0: العدة, 1: اليوم, 2: التاريخ, 3: الصنف, 4: السعر, 5: الوزن, 6: العدد, 7: الحالة, 8: المبلغ
                
                status = row_entries[7].get().strip()
                item_name = row_entries[3].get().strip()
                
                # تخطي الصفوف الفارغة تماماً
                if not item_name and not status:
                    continue
                    
                # تخطي الصفوف التي لا تحتوي على صنف وليست دفعة مالية
                if not item_name and status != "مدفوع":
                    continue
                    
                weight = float(row_entries[5].get() or 0)
                count = float(row_entries[6].get() or 0)
                price = float(row_entries[4].get() or 0)
                amount = float(row_entries[8].get() or 0)
                
                # إذا كان المبلغ صفر، تأكد من حسابه
                if amount == 0:
                    if weight > 0: amount = weight * price
                    elif count > 0: amount = count * price
                
                transactions.append((item_name, weight, count, price, amount, status))
            except (ValueError, AttributeError, IndexError):
                continue
        
        # حساب الإجماليات
        total_goods = 0.0
        total_paid = 0.0
        
        for trans in transactions:
            amount = trans[4]
            status = trans[5]
            if status == "مدفوع":
                total_paid += amount
            else:
                total_goods += amount
        
        final_balance = self.old_balance + total_goods - total_paid
        
        # بيانات الفاتورة
        invoice_data = {
            'seller_name': self.seller_name,
            'invoice_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'old_balance': self.old_balance,
            'transactions': transactions,
            'total_goods': total_goods,
            'total_paid': total_paid,
            'final_balance': final_balance
        }
        
        # فتح نافذة المعاينة
        PrintPreviewWindow(self.window, invoice_data)


    def load_data(self):
        # جلب البيانات
        transactions = self.db.get_seller_transactions(self.seller_id)
        
        # تجميع البيانات حسب التاريخ
        from itertools import groupby
        
        # Sort by date first (assuming date is at index 7)
        # data format: id, amount, status, count, weight, price, item_name, date, day_name, equipment, note
        transactions.sort(key=lambda x: x[7] if x[7] else "")
        
        current_row_idx = 1
        
        # إضافة الرصيد السابق كأول صف إذا وجد
        # self.add_row(current_row_idx, row_type='old_balance', data=self.old_balance)
        # current_row_idx += 1
        
        grand_total = 0
        total_paid_sum = 0
        
        for date, group in groupby(transactions, key=lambda x: x[7]):
            group_list = list(group)
            meal_total = 0
            
            for trans in group_list:
                # trans: id, amount, status, count, weight, price, item_name, date, day_name, equipment, note
                status = trans[2]
                amount = trans[1]
                
                if status == "مدفوع":
                    # صف مدفوع
                    self.add_row(current_row_idx, data=trans, row_type='paid')
                    total_paid_sum += amount
                else:
                    # صف بضاعة
                    self.add_row(current_row_idx, data=trans, row_type='normal')
                    meal_total += amount
                    grand_total += amount
                
                current_row_idx += 1
            
            # إضافة صف "اجمالي وجبه" بعد كل مجموعة تاريخ
            if meal_total > 0:
                self.add_row(current_row_idx, data=meal_total, row_type='meal_total')
                current_row_idx += 1
        
        # إضافة صفوف فارغة في النهاية
        for _ in range(5):
            self.add_row(current_row_idx, row_type='empty')
            current_row_idx += 1
            
        # إضافة الإجماليات النهائية
        self.add_row(current_row_idx, data=grand_total, row_type='grand_total')
        current_row_idx += 1
        
        self.add_row(current_row_idx, data=total_paid_sum, row_type='total_paid')
        current_row_idx += 1
        
        remaining = self.old_balance + grand_total - total_paid_sum
        self.add_row(current_row_idx, data=remaining, row_type='remaining')
        
        # تحديث خانة المتبقي في الفوتر
        if hasattr(self, 'lbl_footer_remaining'):
            self.lbl_footer_remaining.config(text=f"{remaining:,.2f}")

    def add_row(self, row_idx, data=None, row_type='normal'):
        entries = []
        # Columns: 0:Equipment, 1:Day, 2:Date, 3:Item, 4:Price, 5:Weight, 6:Count, 7:Status, 8:Amount
        vals = ["", "", "", "", "", "", "", "", ""]
        
        bg_color = '#ECF0F1'
        fg_color = 'black'
        font_style = ('Arial', 12)
        
        if row_type == 'normal' and data:
            # data: id, amount, status, count, weight, price, item_name, date, day_name, equipment, note
            vals = [
                data[9], data[8], data[7], data[6], 
                data[5], data[4], data[3], data[2], data[1]
            ]
        elif row_type == 'paid' and data:
            # data: id, amount, status, ...
            vals = ["", "", data[7], "دفعة نقدية", "", "", "", "مدفوع", data[1]]
            bg_color = '#E74C3C' # Red for paid row? Or just the label?
            # Image shows: "مدفوع" label is Red, Amount is normal.
            # Let's style the whole row slightly red or just the status column.
            
        elif row_type == 'meal_total':
            vals = ["", "", "", "", "", "", "", "اجمالي وجبه", data]
            bg_color = '#F1C40F' # Yellow
            font_style = ('Arial', 12, 'bold')
            
        elif row_type == 'grand_total':
            vals = ["", "", "", "", "", "", "", "اجمالي الكلي", data]
            bg_color = '#BDC3C7' # Grey
            font_style = ('Arial', 12, 'bold')
            
        elif row_type == 'total_paid':
            vals = ["", "", "", "", "", "", "", "مدفوع", data]
            bg_color = '#E74C3C' # Red
            fg_color = 'white'
            font_style = ('Arial', 12, 'bold')
            
        elif row_type == 'remaining':
            vals = ["", "", "", "", "", "", "", "المتبقي", data]
            bg_color = '#2980B9' # Blue
            fg_color = 'white'
            font_style = ('Arial', 12, 'bold')

        for col in range(9):
            cell_bg = bg_color
            cell_fg = fg_color
            
            # Special styling for Status column (index 7) based on image
            if col == 7:
                if vals[7] == "مدفوع": cell_bg = '#E74C3C'; cell_fg = 'white'
                elif vals[7] == "المتبقي": cell_bg = '#2980B9'; cell_fg = 'white'
                elif vals[7] == "اجمالي وجبه": cell_bg = '#F1C40F'; cell_fg = 'black'
            
            widget = tk.Entry(self.scrollable_frame, font=font_style, relief=tk.FLAT, justify='center', bg=cell_bg, fg=cell_fg)
            widget.insert(0, str(vals[col]) if vals[col] is not None else "")
            widget.grid(row=row_idx, column=col, padx=1, pady=1, sticky='nsew', ipady=8)
            entries.append(widget)
            
        self.rows.append(entries)

    def on_item_select(self, event, row_idx):
        """عند اختيار صنف، قم بتحديث السعر تلقائياً"""
        # العثور على الصف الصحيح (row_idx هو 1-based، والقائمة 0-based)
        # لكن row_idx هنا هو رقم السطر في الـ grid، وليس الـ index في self.rows بدقة إذا كان هناك حذف
        # الأفضل البحث عن الـ widget الذي أطلق الحدث
        widget = event.widget
        item_name = widget.get()
        
        if item_name in self.meal_prices:
            price = self.meal_prices[item_name]['price']
            # equip_weight = self.meal_prices[item_name]['equip'] # يمكن استخدامه لاحقاً
            
            # البحث عن الصف الذي يحتوي على هذا الـ widget
            target_row = None
            for row in self.rows:
                if row[4] == widget: # العمود 4 هو الصنف
                    target_row = row
                    break
            
            if target_row:
                # تحديث السعر (العمود 5)
                target_row[5].delete(0, tk.END)
                target_row[5].insert(0, str(price))
                # إعادة الحساب
                self.auto_calc_row_by_entries(target_row)

    def auto_calc_row(self, row_idx):
        """تحديد الصف وإعادة الحساب"""
        # هذه الدالة تستدعى من الـ bind، نحتاج لمعرفة الصف
        # بما أننا مررنا row_idx وقت الإنشاء، قد يكون غير دقيق إذا تغير الترتيب
        # الأفضل الاعتماد على الـ focus أو تمرير الـ entries مباشرة
        # سنجد الصف عن طريق الـ widget الذي عليه التركيز
        focused_widget = self.window.focus_get()
        
        target_row = None
        for row in self.rows:
            if focused_widget in row:
                target_row = row
                break
        
        if target_row:
            self.auto_calc_row_by_entries(target_row)

    def auto_calc_row_by_entries(self, row_entries):
        """حساب المبلغ للصف المحدد"""
        try:
            price = float(row_entries[5].get() or 0)
            weight = float(row_entries[6].get() or 0)
            count = float(row_entries[7].get() or 0)
            
            amount = 0.0
            if weight > 0:
                amount = price * weight
            elif count > 0:
                amount = price * count
                
            # تحديث المبلغ (العمود 9)
            row_entries[9].delete(0, tk.END)
            row_entries[9].insert(0, str(amount))
            
        except ValueError:
            pass # تجاهل القيم غير الرقمية أثناء الكتابة

    def calculate_totals(self):
        """حساب المجاميع من الجدول مباشرة"""
        total_goods = 0.0
        total_paid = 0.0
        
        for row_entries in self.rows:
            try:
                # المبلغ
                amount_str = row_entries[9].get().strip()
                amount = float(amount_str) if amount_str else 0.0
                
                # الحالة
                status = row_entries[8].get().strip()
                
                if status == "مدفوع":
                    total_paid += amount
                else:
                    # نعتبره بضاعة (متبقي أو فارغ)
                    total_goods += amount
            except ValueError:
                pass
        
        # تحديث واجهة المستخدم
        self.lbl_invoice_total.config(text=f"{total_goods:.2f}")
        self.lbl_paid_total.config(text=f"{total_paid:.2f}")
        
        # الحساب النهائي
        # المتبقي = (الرصيد السابق + بضاعة الفاتورة) - المدفوع
        final_remaining = (self.old_balance + total_goods) - total_paid
        self.lbl_final_total.config(text=f"{final_remaining:.2f}")
        
        return final_remaining

    def save_changes(self):
        """حفظ الفاتورة وتحديث الحسابات"""
        try:
            # 1. تحديث قاعدة بيانات المعاملات
            for row_entries in self.rows:
                trans_id = getattr(row_entries[0], 'trans_id', None)
                
                # قراءة القيم
                note = row_entries[0].get().strip()
                equipment = row_entries[1].get().strip()
                day = row_entries[2].get().strip()
                date = row_entries[3].get().strip()
                item = row_entries[4].get().strip()
                
                price_str = row_entries[5].get()
                weight_str = row_entries[6].get()
                count_str = row_entries[7].get()
                
                price = float(price_str or 0)
                weight = float(weight_str or 0)
                count = float(count_str or 0)
                
                status = row_entries[8].get().strip()
                
                # --- المنطق الذكي: حساب المبلغ تلقائياً ---
                # إذا كان هناك سعر و (وزن أو عدد)، نحسب المبلغ
                current_amount_str = row_entries[9].get().strip()
                amount = float(current_amount_str or 0)
                
                if status != "مدفوع": # للبضاعة فقط
                    if price > 0 and (weight > 0 or count > 0):
                        calc_amount = price * (weight if weight > 0 else count)
                        amount = calc_amount
                        # تحديث الخانة في الجدول للمستخدم
                        row_entries[9].delete(0, tk.END)
                        row_entries[9].insert(0, str(amount))
                
                is_empty = not (note or equipment or day or date or item or price or weight or count or status or amount)
                
                if trans_id:
                    if is_empty:
                        self.db.delete_seller_transaction(trans_id)
                    else:
                        self.db.update_seller_transaction(trans_id, amount, status, count, weight, price, item, date, day, equipment, note)
                elif not is_empty:
                    self.db.add_seller_transaction(self.seller_id, amount, status, count, weight, price, item, date, day, equipment, note)
            
            # 2. تحديث الرصيد النهائي للبائع في الجدول الرئيسي
            final_remaining = self.calculate_totals() # يعيد حساب المتبقي النهائي
            
            # تحديث sellers_accounts
            # نحتاج دالة في قاعدة البيانات لتحديث الرصيد فقط
            # للتبسيط سنستخدم update_seller_account مع الحفاظ على total_credit القديم
            total_credit = self.account_data[3] if self.account_data else 0.0
            self.db.update_seller_account(self.seller_id, self.seller_name, final_remaining, total_credit)
            
            messagebox.showinfo("نجاح", "تم حفظ الفاتورة وتحديث رصيد البائع")
            # self.window.destroy() # اختياري: هل نغلق النافذة أم نبقيها؟ سنبقيها للتعديل
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {e}")

