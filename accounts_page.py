import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import ColorManager
from datetime import datetime, timedelta

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
        
        # self.customer_income_btn = tk.Button(
        #     center_buttons_holder,
        #     text="وارد العملاء",
        #     command=self.open_customer_income,
        #     **bottom_buttons_style
        # )
        # self.customer_income_btn.pack(side=tk.LEFT, padx=15)
        
        self.arrears_btn = tk.Button(
            center_buttons_holder,
            text="متاخرات",
            command=self.open_arrears_window,
            **bottom_buttons_style
        )
        self.arrears_btn.pack(side=tk.LEFT, padx=15)
        
    def on_search_change(self, *args):
        """تصفية الجدول بناءً على البحث"""
        query = self.search_var.get().strip().lower()
        self.filter_data(query)

    def load_data(self):
        """تحميل البيانات من قاعدة البيانات"""
        # استخدام الدالة الجديدة لجلب الأرصدة المحسوبة
        self.all_accounts = self.db.get_sellers_with_balances()
        self.filter_data("")

    def filter_data(self, query):
        """عرض البيانات المصفاة"""
        # مسح الجدول
        for row_entries in self.table_rows:
            for i, entry in enumerate(row_entries):
                entry.config(state='normal') # تمكين التعديل للمسح
                entry.delete(0, tk.END)
                entry.config(bg=self.column_colors[i]) # إعادة اللون الأصلي
                if hasattr(row_entries[0], 'account_id'):
                    del row_entries[0].account_id
                    del row_entries[0].seller_name

        # تصفية البيانات
        filtered_accounts = []
        for acc in self.all_accounts:
            # acc: id, seller_name, calculated_remaining, calculated_allowance, phone
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
            # اجمالي السماح (calculated_allowance)
            row_entries[0].insert(0, str(account[3])) 
            row_entries[0].config(state='readonly')
            
            # المتبقي (calculated_remaining)
            row_entries[1].insert(0, str(account[2])) 
            row_entries[1].config(state='readonly')
            
            # الاسم
            row_entries[2].insert(0, account[1]) 
            row_entries[2].config(state='readonly')

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
        # تم تعطيل الحفظ لأن الجدول الآن يعرض قيم محسوبة ديناميكياً
        # ولا يجب حفظها كقيم ثابتة في قاعدة البيانات لتجنب الازدواجية
        messagebox.showwarning("تنبيه", "لا يمكن حفظ التعديلات من هذا الجدول مباشرة. الرجاء استخدام المعاملات المالية.")
        return
    
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
    
    def open_arrears_window(self):
        """فتح نافذة المتأخرات"""
        arrears_win = tk.Toplevel(self.window)
        arrears_win.title("المتأخرات")
        arrears_win.geometry("600x700")
        arrears_win.configure(bg=self.colors['window_bg'])
        
        # Header
        tk.Label(
            arrears_win, 
            text="قائمة المتأخرات (البائعين)", 
            font=('Playpen Sans Arabic', 18, 'bold'),
            bg=self.colors['header_bg'],
            fg='white'
        ).pack(fill=tk.X, pady=10)
        
        # Table Frame
        table_frame = tk.Frame(arrears_win, bg=self.colors['window_bg'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Headers
        headers = ['المبلغ المتبقي', 'اسم البائع']
        header_colors = [self.colors['col_remain'], self.colors['col_name']]
        
        for i, text in enumerate(headers):
            tk.Label(
                table_frame,
                text=text,
                font=('Playpen Sans Arabic', 14, 'bold'),
                bg=header_colors[i],
                relief=tk.RAISED,
                bd=2,
                width=20
            ).grid(row=0, column=i, sticky='nsew', padx=1, pady=1)
            table_frame.grid_columnconfigure(i, weight=1)
            
        # Data
        sellers = self.db.get_sellers_with_balances()
        row_idx = 1
        
        overdue_sellers = []
        today = datetime.now()
        
        for seller in sellers:
            # seller: id, name, remaining, allowance, phone
            s_id = seller[0]
            name = seller[1]
            remaining = seller[2]
            
            if remaining > 0: # فقط من عليهم مبالغ (مدينون)
                # التحقق من المتأخرات (مرور أسبوع دون دفع)
                last_payment_date_str = self.db.get_last_payment_date(s_id)
                is_overdue = False
                
                if last_payment_date_str:
                    try:
                        last_payment = datetime.strptime(last_payment_date_str, "%Y-%m-%d")
                        if (today - last_payment).days >= 7:
                            is_overdue = True
                    except ValueError:
                        pass
                else:
                    # لم يدفع أبداً، نتحقق من تاريخ آخر معاملة (بداية الدين)
                    last_trans_date_str = self.db.get_last_transaction_date(s_id)
                    if last_trans_date_str:
                        try:
                            last_trans = datetime.strptime(last_trans_date_str, "%Y-%m-%d")
                            if (today - last_trans).days >= 7:
                                is_overdue = True
                        except ValueError:
                            pass
                
                if is_overdue:
                    overdue_sellers.append(f"- {name}: {remaining:.2f}")

                # Remaining
                tk.Label(
                    table_frame,
                    text=f"{remaining:.2f}",
                    font=('Arial', 14, 'bold'),
                    bg=self.colors['col_remain'],
                    relief=tk.SUNKEN,
                    bd=1
                ).grid(row=row_idx, column=0, sticky='nsew', padx=1, pady=1, ipady=5)
                
                # Name
                tk.Label(
                    table_frame,
                    text=name,
                    font=('Playpen Sans Arabic', 14, 'bold'),
                    bg=self.colors['col_name'],
                    relief=tk.SUNKEN,
                    bd=1
                ).grid(row=row_idx, column=1, sticky='nsew', padx=1, pady=1, ipady=5)
                
                row_idx += 1
        
        # إشعار بالمتأخرات
        if overdue_sellers:
            message = "تنبيه: البائعين التاليين لم يقوموا بالدفع منذ أسبوع أو أكثر:\n\n"
            message += "\n".join(overdue_sellers)
            messagebox.showwarning("تنبيه متأخرات", message, parent=arrears_win)
        
        # Close Button
        tk.Button(
            arrears_win,
            text="إغلاق",
            command=arrears_win.destroy,
            font=('Playpen Sans Arabic', 12, 'bold'),
            bg=self.colors['btn_bg'],
            fg='white',
            width=15
        ).pack(pady=20)


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
        # من اليمين لليسار: المبلغ، الحالة، العدد، الوزن، السعر، الصنف، التاريخ، العدة
        # في الكود (0-based index):
        # 0: العدة, 1: التاريخ, 2: الصنف, 3: السعر, 4: الوزن, 5: العدد, 6: الحالة, 7: المبلغ
        self.headers = [
            "العدة", "التاريخ", "الصنف", 
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
            ("تعديل وجبة", self.edit_meal, '#27AE60'),
            ("تحصيل عدة", self.collect_equipment, '#8E44AD')
        ]
        
        self.selected_trans_id = None
        self.selected_row_widgets = []
        
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
    def collect_equipment(self):
        """فتح نافذة تحصيل عدة"""
        dialog = tk.Toplevel(self.window)
        dialog.title("تحصيل عدة")
        dialog.geometry("520x386")
        bg_color = self.colors.get('pink', '#F5CBA7')
        dialog.configure(bg=bg_color)
        
        # توسيط النافذة
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 260
        y = (dialog.winfo_screenheight() // 2) - 193
        dialog.geometry(f"520x386+{x}+{y}")
        
        # العنوان
        tk.Label(dialog, text="اختر نوع العدة والكمية", font=('Playpen Sans Arabic', 16, 'bold'), 
                bg=bg_color, fg='#2C3E50').pack(pady=10)
        
        # إطار القائمة
        list_frame = tk.Frame(dialog, bg='white', relief=tk.SUNKEN, bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # جلب أنواع العدة من قاعدة البيانات
        equipment_items = self.db.get_all_inventory()
        
        if not equipment_items:
            tk.Label(list_frame, text="لا توجد أنواع عدة مسجلة", font=('Arial', 14), 
                    bg='white', fg='red').pack(pady=50)
            tk.Button(dialog, text="إغلاق", command=dialog.destroy, 
                     bg='#C0392B', fg='white', font=('Arial', 12, 'bold'), 
                     width=15).pack(pady=10)
            return
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox لعرض أنواع العدة
        equipment_listbox = tk.Listbox(list_frame, font=('Arial', 14), 
                                       yscrollcommand=scrollbar.set, 
                                       justify='right', height=10)
        equipment_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=equipment_listbox.yview)
        
        # ملء القائمة
        equipment_dict = {}
        for item in equipment_items:
            # item: (id, name, quantity, price)
            display_text = f"{item[1]} - السعر: {item[3]} ج.م - المتاح: {item[2]}"
            equipment_listbox.insert(tk.END, display_text)
            equipment_dict[display_text] = item
        
        # إطار الإدخال
        input_frame = tk.Frame(dialog, bg=bg_color)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(input_frame, text="الكمية:", font=('Arial', 14, 'bold'), 
                bg=bg_color).pack(side=tk.RIGHT, padx=5)
        
        quantity_entry = tk.Entry(input_frame, font=('Arial', 14), 
                                 justify='center', width=15)
        quantity_entry.pack(side=tk.RIGHT, padx=5)
        quantity_entry.insert(0, "1")
        
        def confirm_equipment():
            selection = equipment_listbox.curselection()
            if not selection:
                messagebox.showwarning("تنبيه", "الرجاء اختيار نوع العدة")
                return
            
            selected_text = equipment_listbox.get(selection[0])
            selected_item = equipment_dict[selected_text]
            
            try:
                quantity = int(quantity_entry.get())
                if quantity <= 0:
                    messagebox.showerror("خطأ", "الرجاء إدخال كمية صحيحة")
                    return
                
                # حساب التكلفة
                item_id, item_name, available_qty, item_price = selected_item
                total_cost = item_price * quantity
                
                # إضافة معاملة للعدة
                from datetime import datetime
                today = datetime.now().strftime("%Y-%m-%d")
                
                note = f"تحصيل {quantity} {item_name}"
                
                # إضافة كمعاملة بضاعة (ليست مدفوع)
                self.db.add_seller_transaction(
                    self.seller_id, total_cost, "متبقي", quantity, 0, item_price,
                    item_name, today, "", item_name, note
                )
                
                # تحديث كمية العدة في المخزون (تقليل)
                self.db.update_inventory_quantity(item_id, -quantity)
                
                dialog.destroy()
                
                # إعادة تحميل البيانات
                for row_entries in self.rows:
                    for entry in row_entries:
                        entry.destroy()
                self.rows = []
                
                for widget in self.scrollable_frame.winfo_children():
                    if int(widget.grid_info()['row']) > 0:
                        widget.destroy()
                
                self.load_data()
                messagebox.showinfo("نجاح", f"تم تحصيل {quantity} {item_name} بمبلغ {total_cost} ج.م")
                
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال كمية صحيحة")
        
        # أزرار التأكيد والإلغاء
        buttons_frame = tk.Frame(dialog, bg=bg_color)
        buttons_frame.pack(pady=10)
        
        tk.Button(buttons_frame, text="تأكيد", command=confirm_equipment, 
                 bg='#27AE60', fg='white', font=('Arial', 12, 'bold'), 
                 width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(buttons_frame, text="إلغاء", command=dialog.destroy, 
                 bg='#C0392B', fg='white', font=('Arial', 12, 'bold'), 
                 width=15).pack(side=tk.LEFT, padx=5)
        
        dialog.bind('<Return>', lambda e: confirm_equipment())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def edit_meal(self):
        """تعديل سعر الوجبة/الصنف المحدد"""
        if not self.selected_trans_id:
            messagebox.showwarning("تنبيه", "الرجاء تحديد صنف من الجدول لتعديله")
            return
            
        # Get transaction details
        trans_data = None
        transactions = self.db.get_seller_transactions(self.seller_id)
        for t in transactions:
            if t[0] == self.selected_trans_id:
                trans_data = t
                break
        
        if not trans_data:
            return
            
        # trans: id, amount, status, count, weight, price, item_name, date, day_name, equipment, note
        current_price = trans_data[5]
        item_name = trans_data[6]
        
        # Dialog
        dialog = tk.Toplevel(self.window)
        dialog.title("تعديل سعر الصنف")
        dialog.geometry("400x200")
        bg_color = self.colors.get('window_bg', '#FFB347')
        dialog.configure(bg=bg_color)
        
        # Center
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 100
        dialog.geometry(f"400x200+{x}+{y}")
        
        tk.Label(dialog, text=f"تعديل سعر: {item_name}", font=('Playpen Sans Arabic', 14, 'bold'), bg=bg_color).pack(pady=20)
        
        frame = tk.Frame(dialog, bg=bg_color)
        frame.pack()
        
        tk.Label(frame, text="السعر الجديد:", font=('Arial', 12, 'bold'), bg=bg_color).pack(side=tk.RIGHT, padx=5)
        entry_price = tk.Entry(frame, font=('Arial', 14), justify='center', width=10)
        entry_price.pack(side=tk.RIGHT, padx=5)
        entry_price.insert(0, str(current_price))
        entry_price.focus()
        entry_price.select_range(0, tk.END)
        
        def save_price():
            try:
                new_price = float(entry_price.get())
                
                # Update seller transaction
                # We need to recalculate amount
                weight = trans_data[4]
                count = trans_data[3]
                new_amount = 0
                if weight > 0: new_amount = weight * new_price
                elif count > 0: new_amount = count * new_price
                
                # Update DB
                self.db.update_seller_transaction(
                    self.selected_trans_id, new_amount, trans_data[2], count, weight, new_price, 
                    item_name, trans_data[7], trans_data[8], trans_data[9], trans_data[10]
                )
                
                # Check if it's a transfer and update agriculture_transfers
                note = trans_data[10]
                if note and "نقلة من العميل" in note:
                    # Extract client name carefully
                    # Note format: "نقلة من العميل {client_name}"
                    client_name = note.replace("نقلة من العميل", "").strip()
                    
                    # Update transfers
                    updated_count = self.db.update_transfer_price(client_name, self.seller_name, item_name, weight, count, new_price)
                    if updated_count > 0:
                        print(f"Updated {updated_count} transfer records.")
                        
                    # Update Client Debt
                    # Calculate difference in amount
                    old_amount = trans_data[1]
                    diff = new_amount - old_amount
                    
                    # Apply difference to client account (negative because it's a credit to client)
                    self.db.add_client_debt(client_name, -diff)
                    
                messagebox.showinfo("نجاح", "تم تعديل السعر بنجاح")
                dialog.destroy()
                
                # Refresh
                # Clear table
                for row_entries in self.rows:
                    for entry in row_entries:
                        entry.destroy()
                self.rows = []
                for widget in self.scrollable_frame.winfo_children():
                    if int(widget.grid_info()['row']) > 0:
                        widget.destroy()
                self.load_data()
                
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال سعر صحيح")

        tk.Button(dialog, text="حفظ", command=save_price, bg='#27AE60', fg='white', font=('Playpen Sans Arabic', 12, 'bold'), width=10).pack(pady=20)
        
        dialog.bind('<Return>', lambda e: save_price())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def edit_payment(self):
        """فتح نافذة تعديل الدفع"""
        dialog = tk.Toplevel(self.window)
        dialog.title("تعديل الدفع")
        dialog.geometry("800x250")
        bg_color = self.colors.get('pink', '#F5CBA7')
        dialog.configure(bg=bg_color)
        
        # توسيط
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 400
        y = (dialog.winfo_screenheight() // 2) - 125
        dialog.geometry(f"800x250+{x}+{y}")

        # حساب المبلغ الإجمالي المدفوع حالياً (بدون السماح)
        transactions = self.db.get_seller_transactions(self.seller_id)
        current_total_paid = 0.0
        for trans in transactions:
            # trans: id, amount, status, count, weight, price, item_name, date, day_name, equipment, note
            if trans[2] == "مدفوع" and trans[6] != "سماح":  # status == مدفوع AND item_name != سماح
                current_total_paid += trans[1]  # amount

        # إطار رئيسي
        main_frame = tk.Frame(dialog, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # العناوين (شريط أصفر)
        headers_frame = tk.Frame(main_frame, bg='#F1C40F')
        headers_frame.pack(fill=tk.X, pady=(0, 5))
        
        lbl_style = {'font': ('Arial', 14, 'bold'), 'bg': '#F1C40F', 'fg': 'black', 'pady': 10}
        
        tk.Label(headers_frame, text="ملحوظة", **lbl_style).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Label(headers_frame, text="سماح", **lbl_style).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Label(headers_frame, text="المبلغ الكلي المدفوع", **lbl_style).pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # الحقول (شريط أبيض/رمادي)
        inputs_frame = tk.Frame(main_frame, bg='#ECF0F1')
        inputs_frame.pack(fill=tk.X, pady=5)
        
        entry_style = {'font': ('Arial', 14), 'justify': 'center', 'relief': tk.FLAT}
        
        # حاويات للحقول
        f1 = tk.Frame(inputs_frame, bg='#ECF0F1', bd=1, relief=tk.SOLID)
        f1.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        f2 = tk.Frame(inputs_frame, bg='#ECF0F1', bd=1, relief=tk.SOLID)
        f2.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        f3 = tk.Frame(inputs_frame, bg='#ECF0F1', bd=1, relief=tk.SOLID)
        f3.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        entry_note = tk.Entry(f1, **entry_style)
        entry_note.pack(fill=tk.BOTH, expand=True, ipady=5)
        
        entry_discount = tk.Entry(f2, **entry_style)
        entry_discount.pack(fill=tk.BOTH, expand=True, ipady=5)
        
        entry_total_payment = tk.Entry(f3, **entry_style)
        entry_total_payment.pack(fill=tk.BOTH, expand=True, ipady=5)
        
        # ملء المبلغ الحالي
        entry_total_payment.insert(0, f"{current_total_paid:.2f}")
        
        # التركيز على المبلغ الكلي
        entry_total_payment.focus()
        entry_total_payment.select_range(0, tk.END)

        def confirm_edit():
            new_total_payment_str = entry_total_payment.get().strip()
            discount_str = entry_discount.get().strip()
            note = entry_note.get().strip()
            
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            added = False
            
            # تعديل المبلغ الكلي المدفوع
            if new_total_payment_str:
                try:
                    new_total = float(new_total_payment_str)
                    difference = new_total - current_total_paid
                    
                    if abs(difference) > 0.01:  # إذا كان هناك فرق
                        if difference > 0:
                            # إضافة دفع إضافي
                            item_name = f"تعديل دفع - إضافة {('(' + note + ')') if note else ''}"
                        else:
                            # خصم من الدفع (إرجاع)
                            item_name = f"تعديل دفع - خصم {('(' + note + ')') if note else ''}"
                        
                        self.db.add_seller_transaction(
                            self.seller_id, abs(difference), "مدفوع" if difference > 0 else "متبقي", 
                            0, 0, 0, item_name, today, "", "", note
                        )
                        added = True
                except ValueError:
                    messagebox.showerror("خطأ", "الرجاء إدخال مبلغ دفع صحيح")
                    return

            # إضافة السماح (يُخصم من المتبقي)
            if discount_str:
                try:
                    amount = float(discount_str)
                    if amount > 0:
                        item_name = "سماح"
                        self.db.add_seller_transaction(
                            self.seller_id, amount, "سماح", 0, 0, 0, item_name, today, "", "", note
                        )
                        added = True
                except ValueError:
                    messagebox.showerror("خطأ", "الرجاء إدخال مبلغ سماح صحيح")
                    return

            if added:
                dialog.destroy()
                # إعادة تحميل البيانات
                for row_entries in self.rows:
                    for entry in row_entries:
                        entry.destroy()
                self.rows = []
                
                for widget in self.scrollable_frame.winfo_children():
                    if int(widget.grid_info()['row']) > 0:
                        widget.destroy()
                
                self.load_data()
                messagebox.showinfo("نجاح", "تم تعديل الدفع بنجاح")
            else:
                messagebox.showinfo("تنبيه", "لم يتم إجراء أي تعديل")
                dialog.destroy()

        tk.Button(dialog, text="تأكيد", command=confirm_edit, bg=self.colors.get('orange', '#F39C12'), 
                 fg='white', font=('Arial', 12, 'bold'), width=15).pack(pady=10)
        dialog.bind('<Return>', lambda e: confirm_edit())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    def open_add_payment_dialog(self):
        """فتح نافذة إضافة دفع - تصميم محدث"""
        dialog = tk.Toplevel(self.window)
        dialog.title(f"إضافة دفع - {self.seller_name}")
        dialog.geometry("900x500")
        bg_color = '#ECF0F1'
        dialog.configure(bg=bg_color)
        
        # توسيط
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 450
        y = (dialog.winfo_screenheight() // 2) - 250
        dialog.geometry(f"900x500+{x}+{y}")

        # === Header Section ===
        header_frame = tk.Frame(dialog, bg='#2C3E50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="إضافة دفعة أو خصم",
            font=('Playpen Sans Arabic', 22, 'bold'),
            bg='#2C3E50',
            fg='white'
        ).pack(pady=25)

        # === Main Content ===
        content_frame = tk.Frame(dialog, bg=bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # معلومات البائع
        info_card = tk.Frame(content_frame, bg='white', relief=tk.RAISED, bd=2)
        info_card.pack(fill=tk.X, pady=(0, 20))
        
        info_inner = tk.Frame(info_card, bg='white')
        info_inner.pack(padx=20, pady=15)
        
        tk.Label(
            info_inner,
            text=f"البائع: {self.seller_name}",
            font=('Playpen Sans Arabic', 16, 'bold'),
            bg='white',
            fg='#2C3E50'
        ).pack(side=tk.RIGHT, padx=20)
        
        # حساب المتبقي الحالي
        from datetime import datetime
        transactions = self.db.get_seller_transactions(self.seller_id)
        current_remaining = self.old_balance
        for trans in transactions:
            if trans[2] == "مدفوع" or trans[2] == "سماح":
                current_remaining -= trans[1]
            else:
                current_remaining += trans[1]
        
        tk.Label(
            info_inner,
            text=f"المتبقي الحالي: {current_remaining:,.2f} ج.م",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#E74C3C' if current_remaining > 0 else '#27AE60'
        ).pack(side=tk.LEFT, padx=20)

        # === Input Fields Card ===
        input_card = tk.Frame(content_frame, bg='white', relief=tk.RAISED, bd=2)
        input_card.pack(fill=tk.BOTH, expand=True)
        
        input_inner = tk.Frame(input_card, bg='white')
        input_inner.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)
        
        # Grid for inputs
        fields_container = tk.Frame(input_inner, bg='white')
        fields_container.pack(expand=True)
        
        def create_input_field(parent, label_text, row, default_value=""):
            # Label
            tk.Label(
                parent,
                text=label_text,
                font=('Playpen Sans Arabic', 14, 'bold'),
                bg='white',
                fg='#34495E'
            ).grid(row=row, column=1, sticky='e', padx=15, pady=15)
            
            # Entry Frame
            entry_frame = tk.Frame(parent, bg='#F8F9F9', relief=tk.SOLID, bd=1)
            entry_frame.grid(row=row, column=0, sticky='ew', padx=15, pady=15)
            
            entry = tk.Entry(
                entry_frame,
                font=('Arial', 16),
                justify='center',
                bg='#F8F9F9',
                relief=tk.FLAT,
                fg='#2C3E50'
            )
            entry.pack(fill=tk.BOTH, ipady=12, padx=5)
            
            if default_value:
                entry.insert(0, default_value)
            
            return entry
        
        # Configure grid columns
        fields_container.grid_columnconfigure(0, weight=1, minsize=400)
        
        # Create fields
        entry_payment = create_input_field(fields_container, "💰 المبلغ المدفوع:", 0, "0")
        entry_discount = create_input_field(fields_container, "🎁 الخصم (سماح):", 1, "0")
        entry_note = create_input_field(fields_container, "📝 ملاحظات:", 2, "")
        
        # Focus and select
        entry_payment.focus()
        entry_payment.select_range(0, tk.END)

        def confirm_payment():
            payment_str = entry_payment.get().strip()
            discount_str = entry_discount.get().strip()
            note = entry_note.get().strip()
            
            today = datetime.now().strftime("%Y-%m-%d")
            added = False
            
            # إضافة الدفع
            if payment_str and payment_str != "0":
                try:
                    amount = float(payment_str)
                    if amount > 0:
                        item_name = f"دفعة نقدية {('(' + note + ')') if note else ''}"
                        self.db.add_seller_transaction(
                            self.seller_id, amount, "مدفوع", 0, 0, 0, item_name, today, "", "", note
                        )
                        added = True
                except ValueError:
                    messagebox.showerror("خطأ", "الرجاء إدخال مبلغ دفع صحيح", parent=dialog)
                    return

            # إضافة السماح
            if discount_str and discount_str != "0":
                try:
                    amount = float(discount_str)
                    if amount > 0:
                        item_name = "سماح"
                        self.db.add_seller_transaction(
                            self.seller_id, amount, "سماح", 0, 0, 0, item_name, today, "", "", note
                        )
                        added = True
                except ValueError:
                    messagebox.showerror("خطأ", "الرجاء إدخال مبلغ سماح صحيح", parent=dialog)
                    return

            if added:
                dialog.destroy()
                # إعادة تحميل البيانات
                for row_entries in self.rows:
                    for entry in row_entries:
                        entry.destroy()
                self.rows = []
                
                for widget in self.scrollable_frame.winfo_children():
                    if int(widget.grid_info()['row']) > 0:
                        widget.destroy()
                
                self.load_data()
                messagebox.showinfo("نجاح", "تم إضافة الدفع بنجاح")
            else:
                messagebox.showwarning("تنبيه", "لم يتم إدخال أي قيمة", parent=dialog)

        # === Buttons Section ===
        buttons_frame = tk.Frame(dialog, bg=bg_color)
        buttons_frame.pack(fill=tk.X, padx=30, pady=(0, 20))
        
        btn_style = {
            'font': ('Playpen Sans Arabic', 13, 'bold'),
            'relief': tk.RAISED,
            'bd': 0,
            'cursor': 'hand2',
            'width': 18,
            'height': 2
        }
        
        tk.Button(
            buttons_frame,
            text="✓ تأكيد وحفظ",
            command=confirm_payment,
            bg='#27AE60',
            fg='white',
            **btn_style
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="✕ إلغاء",
            command=dialog.destroy,
            bg='#95A5A6',
            fg='white',
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        dialog.bind('<Return>', lambda e: confirm_payment())
        dialog.bind('<Escape>', lambda e: dialog.destroy())

    def print_invoice(self): 
        """طباعة كشف حساب لفترة محددة"""
        from print_utils import PrintPreviewWindow
        from datetime import datetime
        
        # نافذة اختيار الفترة
        date_window = tk.Toplevel(self.window)
        date_window.title("طباعة كشف حساب")
        date_window.geometry("400x250")
        bg_color = self.colors.get('pink', '#F5CBA7')
        date_window.configure(bg=bg_color)
        
        # توسيط
        date_window.update_idletasks()
        x = (date_window.winfo_screenwidth() // 2) - 200
        y = (date_window.winfo_screenheight() // 2) - 125
        date_window.geometry(f"400x250+{x}+{y}")
        
        tk.Label(date_window, text="اختر الفترة", font=('Playpen Sans Arabic', 16, 'bold'), 
                 bg=bg_color, fg='#2C3E50').pack(pady=15)
        
        frame = tk.Frame(date_window, bg=bg_color)
        frame.pack(pady=10)
        
        # تاريخ البداية
        tk.Label(frame, text="من تاريخ:", font=('Arial', 12, 'bold'), bg=bg_color).grid(row=0, column=1, padx=5, pady=5)
        start_entry = tk.Entry(frame, font=('Arial', 12), justify='center')
        start_entry.grid(row=0, column=0, padx=5, pady=5)
        # Default to first of current month
        start_entry.insert(0, datetime.now().strftime("%Y-%m-01"))
        
        # تاريخ النهاية
        tk.Label(frame, text="إلى تاريخ:", font=('Arial', 12, 'bold'), bg=bg_color).grid(row=1, column=1, padx=5, pady=5)
        end_entry = tk.Entry(frame, font=('Arial', 12), justify='center')
        end_entry.grid(row=1, column=0, padx=5, pady=5)
        end_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        def generate_report():
            start_date_str = start_entry.get()
            end_date_str = end_entry.get()
            
            try:
                # التحقق من صحة التنسيق
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                
                # جلب جميع المعاملات من قاعدة البيانات
                all_transactions = self.db.get_seller_transactions(self.seller_id)
                # transactions: id, amount, status, count, weight, price, item_name, date, day_name, equipment, note
                
                filtered_transactions = []
                
                # تصفية المعاملات
                for trans in all_transactions:
                    trans_date_str = trans[7]
                    try:
                        trans_date = datetime.strptime(trans_date_str, "%Y-%m-%d")
                        if start_date <= trans_date <= end_date:
                            # تحويل البيانات للشكل المطلوب للطباعة
                            # (item_name, weight, count, price, amount, status)
                            item_name = trans[6]
                            weight = trans[4]
                            count = trans[3]
                            price = trans[5]
                            amount = trans[1]
                            status = trans[2]
                            
                            filtered_transactions.append((item_name, weight, count, price, amount, status))
                            
                    except ValueError:
                        continue
                
                # حساب الإجماليات للفترة
                total_goods = sum(t[4] for t in filtered_transactions if t[5] != "مدفوع" and t[5] != "سماح")
                total_paid = sum(t[4] for t in filtered_transactions if t[5] == "مدفوع")
                total_discount = sum(t[4] for t in filtered_transactions if t[5] == "سماح")
                
                # حساب الرصيد السابق (قبل الفترة المحددة)
                balance_before_period = self.old_balance
                
                for trans in all_transactions:
                    trans_date_str = trans[7]
                    try:
                        trans_date = datetime.strptime(trans_date_str, "%Y-%m-%d")
                        if trans_date < start_date:
                            t_amount = trans[1]
                            t_status = trans[2]
                            if t_status == "مدفوع" or t_status == "سماح":
                                balance_before_period -= t_amount
                            else:
                                balance_before_period += t_amount
                    except ValueError:
                        pass
                
                # المتبقي النهائي = الرصيد السابق + بضاعة الفترة - مدفوعات الفترة - سماح الفترة
                final_balance = balance_before_period + total_goods - total_paid - total_discount
                
                # بيانات التقرير
                report_data = {
                    'seller_name': self.seller_name,
                    'invoice_date': f"من {start_date_str} إلى {end_date_str}",
                    'old_balance': balance_before_period,
                    'transactions': filtered_transactions,
                    'total_goods': total_goods,
                    'total_paid': total_paid,
                    'final_balance': final_balance
                }
                
                date_window.destroy()
                PrintPreviewWindow(self.window, report_data)
                
            except ValueError:
                messagebox.showerror("خطأ", "تنسيق التاريخ غير صحيح (YYYY-MM-DD)", parent=date_window)

        tk.Button(date_window, text="طباعة الكشف", command=generate_report, 
                  bg='#2C3E50', fg='white', font=('Arial', 12, 'bold'), width=15).pack(pady=20)


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
        total_discount_sum = 0  # إجمالي السماح
        
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
                elif status == "سماح":
                    # صف سماح (يُخصم من المتبقي)
                    self.add_row(current_row_idx, data=trans, row_type='discount')
                    total_discount_sum += amount
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
        
        # إضافة إجمالي السماح
        if total_discount_sum > 0:
            self.add_row(current_row_idx, data=total_discount_sum, row_type='total_discount')
            current_row_idx += 1
        
        # المتبقي = الرصيد السابق + البضاعة - المدفوع - السماح
        remaining = self.old_balance + grand_total - total_paid_sum - total_discount_sum
        self.add_row(current_row_idx, data=remaining, row_type='remaining')
        
        # تحديث خانة المتبقي في الفوتر
        if hasattr(self, 'lbl_footer_remaining'):
            self.lbl_footer_remaining.config(text=f"{remaining:,.2f}")

    def add_row(self, row_idx, data=None, row_type='normal'):
        entries = []
        # Columns: 0:Equipment, 1:Date, 2:Item, 3:Price, 4:Weight, 5:Count, 6:Status, 7:Amount
        vals = ["", "", "", "", "", "", "", ""]
        
        bg_color = '#ECF0F1'
        fg_color = 'black'
        font_style = ('Arial', 12)
        
        trans_id = None
        
        if row_type == 'normal' and data:
            # data: id, amount, status, count, weight, price, item_name, date, day_name, equipment, note
            trans_id = data[0]
            vals = [
                data[9], data[7], data[6], 
                data[5], data[4], data[3], data[2], data[1]
            ]
        elif row_type == 'paid' and data:
            trans_id = data[0]
            vals = ["", data[7], "دفعة نقدية", "", "", "", "مدفوع", data[1]]
            bg_color = '#E74C3C' # Red
            fg_color = 'white'
            
        elif row_type == 'discount' and data:
            trans_id = data[0]
            vals = ["", data[7], "سماح", "", "", "", "سماح", data[1]]
            bg_color = '#2ECC71' # Green
            fg_color = 'white'
            
        elif row_type == 'meal_total':
            vals = ["", "", "", "", "", "", "اجمالي وجبه", data]
            bg_color = '#F1C40F' # Yellow
            font_style = ('Arial', 12, 'bold')
            
        elif row_type == 'grand_total':
            vals = ["", "", "", "", "", "", "اجمالي الكلي", data]
            bg_color = '#BDC3C7' # Grey
            font_style = ('Arial', 12, 'bold')
            
        elif row_type == 'total_paid':
            vals = ["", "", "", "", "", "", "مدفوع", data]
            bg_color = '#E74C3C' # Red
            fg_color = 'white'
            font_style = ('Arial', 12, 'bold')
            
        elif row_type == 'total_discount':
            vals = ["", "", "", "", "", "", "اجمالي سماح", data]
            bg_color = '#2ECC71' # Green
            fg_color = 'white'
            font_style = ('Arial', 12, 'bold')
            
        elif row_type == 'remaining':
            vals = ["", "", "", "", "", "", "المتبقي", data]
            bg_color = '#2980B9' # Blue
            fg_color = 'white'
            font_style = ('Arial', 12, 'bold')

        for col in range(8):
            cell_bg = bg_color
            cell_fg = fg_color
            
            # Special styling for Status column (index 6) based on image
            if col == 6:
                if vals[6] == "مدفوع": cell_bg = '#E74C3C'; cell_fg = 'white'
                elif vals[6] == "المتبقي": cell_bg = '#2980B9'; cell_fg = 'white'
                elif vals[6] == "اجمالي وجبه": cell_bg = '#F1C40F'; cell_fg = 'black'
                elif vals[6] == "سماح" or vals[6] == "اجمالي سماح": cell_bg = '#2ECC71'; cell_fg = 'white'
            
            widget = tk.Entry(self.scrollable_frame, font=font_style, relief=tk.FLAT, justify='center', bg=cell_bg, fg=cell_fg)
            widget.insert(0, str(vals[col]) if vals[col] is not None else "")
            widget.grid(row=row_idx, column=col, padx=1, pady=1, sticky='nsew', ipady=8)
            
            # Store original background for selection highlighting
            widget.orig_bg = cell_bg
            
            # Bind click event for selection if it's a transaction row
            if trans_id:
                widget.bind('<Button-1>', lambda e, tid=trans_id: self.on_row_click(e, tid))
            
            entries.append(widget)
            
        if entries:
            entries[0].trans_id = trans_id
            
        self.rows.append(entries)

    def on_row_click(self, event, trans_id):
        """تحديد الصف عند النقر عليه"""
        self.selected_trans_id = trans_id
        
        # إعادة تعيين ألوان الصفوف السابقة
        if hasattr(self, 'selected_row_widgets') and self.selected_row_widgets:
            for w in self.selected_row_widgets:
                if hasattr(w, 'orig_bg'):
                    w.config(bg=w.orig_bg)
        
        # تحديد الصف الجديد (نبحث عنه في self.rows)
        # بما أننا لا نملك مرجعاً مباشراً للصف من الـ widget بسهولة (إلا عبر البحث)،
        # سنبحث عن الصف الذي يحتوي على الـ widget الذي تم النقر عليه
        clicked_widget = event.widget
        target_row = None
        for row in self.rows:
            if clicked_widget in row:
                target_row = row
                break
        
        if target_row:
            self.selected_row_widgets = target_row
            for w in target_row:
                w.config(bg='#D5F5E3') # لون التحديد (أخضر فاتح)

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
                if row[2] == widget: # العمود 2 هو الصنف (بعد حذف اليوم)
                    target_row = row
                    break
            
            if target_row:
                # تحديث السعر (العمود 3)
                target_row[3].delete(0, tk.END)
                target_row[3].insert(0, str(price))
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
            price = float(row_entries[3].get() or 0)  # السعر (العمود 3)
            weight = float(row_entries[4].get() or 0)  # الوزن (العمود 4)
            count = float(row_entries[5].get() or 0)  # العدد (العمود 5)
            
            amount = 0.0
            if weight > 0:
                amount = price * weight
            elif count > 0:
                amount = price * count
                
            # تحديث المبلغ (العمود 7)
            row_entries[7].delete(0, tk.END)
            row_entries[7].insert(0, str(amount))
            
        except ValueError:
            pass # تجاهل القيم غير الرقمية أثناء الكتابة

    def calculate_totals(self):
        """حساب المجاميع من الجدول مباشرة"""
        total_goods = 0.0
        total_paid = 0.0
        
        for row_entries in self.rows:
            try:
                # المبلغ (العمود 7)
                amount_str = row_entries[7].get().strip()
                amount = float(amount_str) if amount_str else 0.0
                
                # الحالة (العمود 6)
                status = row_entries[6].get().strip()
                
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
                
                # Columns: 0:Equipment, 1:Date, 2:Item, 3:Price, 4:Weight, 5:Count, 6:Status, 7:Amount
                equipment = row_entries[0].get().strip()
                date = row_entries[1].get().strip()
                item = row_entries[2].get().strip()
                price_str = row_entries[3].get()
                weight_str = row_entries[4].get()
                count_str = row_entries[5].get()
                status = row_entries[6].get().strip()
                amount_str = row_entries[7].get().strip()
                
                price = float(price_str or 0)
                weight = float(weight_str or 0)
                count = float(count_str or 0)
                amount = float(amount_str or 0)
                
                # Missing: note, day. We'll use empty strings or defaults.
                note = ""
                day = "" 
                
                # Recalculate amount if needed (smart logic)
                if status != "مدفوع" and status != "سماح":
                    if price > 0 and (weight > 0 or count > 0):
                         amount = price * (weight if weight > 0 else count)
                         row_entries[7].delete(0, tk.END)
                         row_entries[7].insert(0, str(amount))
                
                is_empty = not (equipment or date or item or price or weight or count or status or amount)
                
                if trans_id:
                    if is_empty:
                        self.db.delete_seller_transaction(trans_id)
                    else:
                        self.db.update_seller_transaction(trans_id, amount, status, count, weight, price, item, date, day, equipment, note)
                elif not is_empty:
                     # Add new transaction
                     self.db.add_seller_transaction(self.seller_id, amount, status, count, weight, price, item, date, day, equipment, note)
            
            # 2. تحديث الرصيد النهائي للبائع في الجدول الرئيسي
            final_remaining = self.calculate_totals() # يعيد حساب المتبقي النهائي
            
            # تحديث sellers_accounts
            total_credit = self.account_data[3] if self.account_data else 0.0
            self.db.update_seller_account(self.seller_id, self.seller_name, final_remaining, total_credit)
            
            messagebox.showinfo("نجاح", "تم حفظ الفاتورة وتحديث رصيد البائع")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {e}")


class MealsManagerWindow:
    def __init__(self, parent, db, colors):
        self.window = tk.Toplevel(parent)
        self.window.title("إدارة الوجبات والأصناف")
        self.window.geometry("700x550")
        self.colors = colors
        self.db = db
        
        bg_color = self.colors.get('window_bg', '#FFB347')
        self.window.configure(bg=bg_color)
        
        # Center
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - 350
        y = (self.window.winfo_screenheight() // 2) - 275
        self.window.geometry(f"700x550+{x}+{y}")

        # Title
        tk.Label(self.window, text="قائمة الوجبات والأصناف", font=('Playpen Sans Arabic', 18, 'bold'), 
                 bg=self.colors.get('header_bg', '#6C3483'), fg='white').pack(fill=tk.X, pady=(0, 10))

        # Content Frame
        content_frame = tk.Frame(self.window, bg=bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # List (Treeview)
        columns = ('id', 'name', 'price', 'weight')
        self.tree = ttk.Treeview(content_frame, columns=columns, show='headings', height=12)
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='اسم الصنف')
        self.tree.heading('price', text='السعر')
        self.tree.heading('weight', text='وزن العدة')
        
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('name', width=250, anchor='center')
        self.tree.column('price', width=100, anchor='center')
        self.tree.column('weight', width=100, anchor='center')
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # Form Frame
        form_frame = tk.Frame(self.window, bg=bg_color)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Grid layout for form
        tk.Label(form_frame, text="اسم الصنف:", font=('Arial', 12, 'bold'), bg=bg_color).grid(row=0, column=5, padx=5, pady=5)
        self.entry_name = tk.Entry(form_frame, font=('Arial', 12), justify='right', width=20)
        self.entry_name.grid(row=0, column=4, padx=5, pady=5)
        
        tk.Label(form_frame, text="السعر:", font=('Arial', 12, 'bold'), bg=bg_color).grid(row=0, column=3, padx=5, pady=5)
        self.entry_price = tk.Entry(form_frame, font=('Arial', 12), justify='center', width=10)
        self.entry_price.grid(row=0, column=2, padx=5, pady=5)
        
        tk.Label(form_frame, text="وزن العدة:", font=('Arial', 12, 'bold'), bg=bg_color).grid(row=0, column=1, padx=5, pady=5)
        self.entry_weight = tk.Entry(form_frame, font=('Arial', 12), justify='center', width=10)
        self.entry_weight.grid(row=0, column=0, padx=5, pady=5)

        # Buttons
        btn_frame = tk.Frame(self.window, bg=bg_color)
        btn_frame.pack(pady=15)
        
        btn_style = {'font': ('Arial', 12, 'bold'), 'width': 12, 'cursor': 'hand2'}
        
        tk.Button(btn_frame, text="إضافة جديد", command=self.add_meal, bg='#27AE60', fg='white', **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="حفظ التعديل", command=self.update_meal, bg='#2980B9', fg='white', **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="حذف", command=self.delete_meal, bg='#C0392B', fg='white', **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="تنظيف", command=self.clear_form, bg='#7F8C8D', fg='white', **btn_style).pack(side=tk.LEFT, padx=5)

        self.load_meals()

    def load_meals(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        meals = self.db.get_all_meals()
        for meal in meals:
            # meal: id, name, price, equip_weight
            self.tree.insert('', tk.END, values=meal)

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], 'values')
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, values[1])
            self.entry_price.delete(0, tk.END)
            self.entry_price.insert(0, values[2])
            self.entry_weight.delete(0, tk.END)
            self.entry_weight.insert(0, values[3])
            self.selected_id = values[0]
        else:
            self.selected_id = None

    def add_meal(self):
        name = self.entry_name.get().strip()
        price = self.entry_price.get().strip()
        weight = self.entry_weight.get().strip() or "0"
        
        if name and price:
            try:
                if self.db.add_meal(name, float(price), float(weight)):
                    messagebox.showinfo("نجاح", "تم إضافة الصنف")
                    self.load_meals()
                    self.clear_form()
                else:
                    messagebox.showerror("خطأ", "هذا الصنف موجود بالفعل")
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال أرقام صحيحة")
        else:
            messagebox.showwarning("تنبيه", "الرجاء إدخال الاسم والسعر")

    def update_meal(self):
        if hasattr(self, 'selected_id') and self.selected_id:
            name = self.entry_name.get().strip()
            price = self.entry_price.get().strip()
            weight = self.entry_weight.get().strip() or "0"
            
            if name and price:
                try:
                    self.db.update_meal(self.selected_id, name, float(price), float(weight))
                    messagebox.showinfo("نجاح", "تم تعديل الصنف")
                    self.load_meals()
                    self.clear_form()
                except ValueError:
                    messagebox.showerror("خطأ", "الرجاء إدخال أرقام صحيحة")
        else:
            messagebox.showwarning("تنبيه", "اختر صنفاً للتعديل")

    def delete_meal(self):
        if hasattr(self, 'selected_id') and self.selected_id:
            if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذا الصنف؟"):
                self.db.delete_meal(self.selected_id)
                self.load_meals()
                self.clear_form()
        else:
            messagebox.showwarning("تنبيه", "اختر صنفاً للحذف")

    def clear_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_weight.delete(0, tk.END)
        self.selected_id = None
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

