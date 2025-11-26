import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class AccountsPage:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.db = Database()
        
        # إنشاء نافذة جديدة
        self.window = tk.Toplevel(parent_window)
        self.window.title("صفحة الحسابات")
        self.window.geometry("900x600")
        self.window.resizable(True, True)
        
        # إطار العنوان
        title_frame = tk.Frame(self.window, bg='#34495e', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="حسابات البائعين",
            font=('Playpen Sans Arabic', 20, 'bold'),
            bg='#34495e',
            fg='white'
        )
        title_label.pack(pady=15)
        
        # إطار الأزرار
        buttons_frame = tk.Frame(self.window, bg='#ecf0f1', height=50)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        buttons_frame.pack_propagate(False)
        
        # أزرار الإضافة والتعديل والحذف
        btn_style = {
            'font': ('Playpen Sans Arabic', 12, 'bold'),
            'bg': '#3498db',
            'fg': 'white',
            'relief': tk.RAISED,
            'bd': 2,
            'cursor': 'hand2',
            'padx': 15,
            'pady': 5
        }
        
        btn_add = tk.Button(
            buttons_frame,
            text="إضافة",
            command=self.add_account,
            **btn_style
        )
        btn_add.pack(side=tk.LEFT, padx=5)
        
        btn_edit = tk.Button(
            buttons_frame,
            text="تعديل",
            command=self.edit_account,
            **btn_style
        )
        btn_edit.pack(side=tk.LEFT, padx=5)
        
        btn_delete = tk.Button(
            buttons_frame,
            text="حذف",
            command=self.delete_account,
            **btn_style
        )
        btn_delete.pack(side=tk.LEFT, padx=5)
        
        btn_refresh = tk.Button(
            buttons_frame,
            text="تحديث",
            command=self.refresh_table,
            **btn_style
        )
        btn_refresh.pack(side=tk.LEFT, padx=5)
        
        btn_close = tk.Button(
            buttons_frame,
            text="إغلاق",
            command=self.window.destroy,
            bg='#e74c3c',
            **{k: v for k, v in btn_style.items() if k != 'bg'}
        )
        btn_close.pack(side=tk.RIGHT, padx=5)
        
        # إطار الجدول
        table_frame = tk.Frame(self.window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # إطار للجدول مع شريط التمرير
        canvas_frame = tk.Frame(table_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas للتمرير
        canvas = tk.Canvas(canvas_frame, bg='white')
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # رأس الجدول - عكس الترتيب
        headers = ['اجمالي السماح', 'المتبقي', 'اسم البائع']
        header_style = {
            'font': ('Playpen Sans Arabic', 14, 'bold'),
            'bg': '#34495e',
            'fg': 'white',
            'relief': tk.RAISED,
            'bd': 2,
            'width': 15,
            'height': 2
        }
        
        for col, header in enumerate(headers):
            label = tk.Label(scrollable_frame, text=header, **header_style)
            label.grid(row=0, column=col, sticky='nsew', padx=1, pady=1)
        
        # إنشاء صفوف جاهزة (20 صف)
        self.table_rows = []
        self.num_rows = 20
        
        entry_style = {
            'font': ('Playpen Sans Arabic', 12),
            'relief': tk.SUNKEN,
            'bd': 1
        }
        
        for row in range(1, self.num_rows + 1):
            row_entries = []
            # اجمالي السماح (عمود 0)
            entry1 = tk.Entry(scrollable_frame, **entry_style)
            entry1.grid(row=row, column=0, sticky='nsew', padx=1, pady=1)
            row_entries.append(entry1)
            
            # المتبقي (عمود 1)
            entry2 = tk.Entry(scrollable_frame, **entry_style)
            entry2.grid(row=row, column=1, sticky='nsew', padx=1, pady=1)
            row_entries.append(entry2)
            
            # اسم البائع (عمود 2)
            entry3 = tk.Entry(scrollable_frame, **entry_style)
            entry3.grid(row=row, column=2, sticky='nsew', padx=1, pady=1)
            row_entries.append(entry3)
            
            self.table_rows.append(row_entries)
        
        # توزيع الأعمدة
        scrollable_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=1)
        scrollable_frame.grid_columnconfigure(2, weight=1)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # تحميل البيانات
        self.refresh_table()
    
    def refresh_table(self):
        """تحديث الجدول بالبيانات من قاعدة البيانات"""
        # مسح البيانات الحالية من جميع الصفوف
        for row_entries in self.table_rows:
            for entry in row_entries:
                entry.delete(0, tk.END)
                entry.config(bg='white')
        
        # جلب البيانات من قاعدة البيانات
        accounts = self.db.get_all_sellers_accounts()
        # ملء الصفوف بالبيانات (عكس الترتيب: اجمالي السماح، المتبقي، اسم البائع)
        for idx, account in enumerate(accounts):
            if idx < self.num_rows:
                account_id, seller_name, remaining, total_credit = account
                row_entries = self.table_rows[idx]
                # اجمالي السماح (العمود الأول)
                row_entries[0].insert(0, str(total_credit))
                # المتبقي (العمود الثاني)
                row_entries[1].insert(0, str(remaining))
                # اسم البائع (العمود الثالث)
                row_entries[2].insert(0, seller_name)
                # حفظ ID الحساب كخاصية للصف
                row_entries[0].account_id = account_id
    
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
                    self.db.add_seller_account(seller_name, remaining, total_credit)
                except ValueError:
                    pass  # تجاهل الأخطاء في الأرقام


class AccountDialog:
    def __init__(self, parent, title, seller_name="", remaining="", total_credit=""):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
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
            pady=10
        )
        title_label.pack()
        
        # إطار الحقول
        fields_frame = tk.Frame(self.dialog)
        fields_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # اسم البائع
        tk.Label(fields_frame, text="اسم البائع:", font=('Playpen Sans Arabic', 12)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_name = tk.Entry(fields_frame, font=('Playpen Sans Arabic', 12), width=25)
        self.entry_name.grid(row=0, column=1, pady=5, padx=10)
        self.entry_name.insert(0, seller_name)
        
        # المتبقي
        tk.Label(fields_frame, text="المتبقي:", font=('Playpen Sans Arabic', 12)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_remaining = tk.Entry(fields_frame, font=('Playpen Sans Arabic', 12), width=25)
        self.entry_remaining.grid(row=1, column=1, pady=5, padx=10)
        self.entry_remaining.insert(0, str(remaining))
        
        # اجمالي السماح
        tk.Label(fields_frame, text="اجمالي السماح:", font=('Playpen Sans Arabic', 12)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_credit = tk.Entry(fields_frame, font=('Playpen Sans Arabic', 12), width=25)
        self.entry_credit.grid(row=2, column=1, pady=5, padx=10)
        self.entry_credit.insert(0, str(total_credit))
        
        # الأزرار
        buttons_frame = tk.Frame(self.dialog)
        buttons_frame.pack(pady=10)
        
        btn_save = tk.Button(
            buttons_frame,
            text="حفظ",
            command=self.save,
            font=('Playpen Sans Arabic', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            width=10,
            padx=10
        )
        btn_save.pack(side=tk.LEFT, padx=5)
        
        btn_cancel = tk.Button(
            buttons_frame,
            text="إلغاء",
            command=self.cancel,
            font=('Playpen Sans Arabic', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=10,
            padx=10
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

