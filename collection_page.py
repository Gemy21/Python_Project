import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import ColorManager, format_clean_number
from datetime import datetime

class CollectionPage:
    def __init__(self, parent_window):
        self.db = Database()
        self.color_manager = ColorManager()
        self.theme = self.color_manager.get_random_theme()
        
        self.colors = {
            'bg': '#2C3E50',           # Dark Blue/Grey background
            'banner_bg': '#34495E',    # Slightly lighter banner
            'card_bg': 'white',
            'text_primary': 'white',
            'text_secondary': '#BDC3C7',
            'accent_green': '#27AE60', # For Collection
            'accent_red': '#C0392B',   # For Expenses
            'accent_orange': '#E67E22', # For Discount
            'button_text': 'white'
        }
        
        self.window = tk.Toplevel(parent_window)
        self.window.title("برنامج التحصيل والمنصرف")
        self.window.geometry("1000x700")
        self.window.configure(bg=self.colors['bg'])
        self.window.resizable(True, True)
        
        # Fonts
        self.fonts = {
            'banner_title': ('Playpen Sans Arabic', 24, 'bold'),
            'banner_value': ('Arial', 28, 'bold'),
            'banner_label': ('Playpen Sans Arabic', 14),
            'button': ('Playpen Sans Arabic', 16, 'bold'),
            'header': ('Playpen Sans Arabic', 18, 'bold'),
            'table': ('Arial', 12)
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- Banner Section ---
        self.create_banner()
        
        # --- Main Buttons Section ---
        self.create_main_buttons()
        
    def create_banner(self):
        banner_frame = tk.Frame(self.window, bg=self.colors['banner_bg'], pady=20, padx=20)
        banner_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Date
        today_date = datetime.now().strftime("%Y-%m-%d")
        tk.Label(
            banner_frame, 
            text=f"تاريخ اليوم: {today_date}", 
            font=self.fonts['banner_label'], 
            bg=self.colors['banner_bg'], 
            fg=self.colors['text_secondary']
        ).pack(anchor='e')
        
        # Stats Container
        stats_frame = tk.Frame(banner_frame, bg=self.colors['banner_bg'])
        stats_frame.pack(fill=tk.X, pady=20)
        
        # Calculate Totals using database method
        totals = self.db.calculate_daily_totals(today_date)
        total_collection = totals['total_collection']
        total_expenses = totals['total_expenses']
        remaining_profit = totals['remaining_profit']
        
        # Collection Card (Right)
        self.create_stat_card(
            stats_frame, 
            "إجمالي التحصيل", 
            format_clean_number(total_collection), 
            self.colors['accent_green'], 
            tk.RIGHT
        )
        
        # Expenses Card (Center)
        self.create_stat_card(
            stats_frame, 
            "المصاريف", 
            format_clean_number(total_expenses), 
            self.colors['accent_red'], 
            tk.RIGHT
        )
        
        # Remaining Profit Card (Left)
        self.create_stat_card(
            stats_frame, 
            "باقي تحصيل اليوم", 
            format_clean_number(remaining_profit), 
            '#3498DB',
            tk.LEFT
        )
        
    def create_stat_card(self, parent, title, value, color, side):
        card = tk.Frame(parent, bg=self.colors['banner_bg'], padx=20)
        card.pack(side=side, expand=True)
        
        tk.Label(
            card, 
            text=title, 
            font=self.fonts['banner_label'], 
            bg=self.colors['banner_bg'], 
            fg='white'
        ).pack()
        
        tk.Label(
            card, 
            text=value, 
            font=self.fonts['banner_value'], 
            bg=self.colors['banner_bg'], 
            fg=color
        ).pack(pady=5)

    def create_main_buttons(self):
        btn_container = tk.Frame(self.window, bg=self.colors['bg'])
        btn_container.pack(expand=True)
        
        # Grid layout for 5 buttons
        
        # Row 1
        self.create_big_button(btn_container, "إضافة تحصيل", self.open_add_collection, self.colors['accent_green'], 0, 1)
        self.create_big_button(btn_container, "إضافة منصرف", self.open_add_expense, self.colors['accent_red'], 0, 0)
        
        # Row 2
        self.create_big_button(btn_container, "قائمة التحصيل", self.open_collection_list, '#2980B9', 1, 1) # Blue
        self.create_big_button(btn_container, "قائمة المنصرف", self.open_expense_list, '#8E44AD', 1, 0)   # Purple
        
        # Row 3 - Reports button centered
        self.create_big_button(btn_container, "التقارير اليومية والشهرية", self.open_reports, '#16A085', 2, 0, columnspan=2)
        
    def create_big_button(self, parent, text, command, color, row, col, columnspan=1):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=self.fonts['button'],
            bg=color,
            fg='white',
            relief=tk.RAISED,
            bd=0,
            cursor='hand2',
            width=20,
            height=3
        )
        btn.grid(row=row, column=col, columnspan=columnspan, padx=20, pady=20)
        


    # --- Actions ---
    def open_add_collection(self):
        """Open Add Collection Window (Same logic as main.py but local) with Discount support"""
        win = tk.Toplevel(self.window)
        win.title("إضافة تحصيل نقدية / سماح")
        win.geometry("450x450")
        win.configure(bg='white')
        
        # Center
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - 225
        y = (win.winfo_screenheight() // 2) - 225
        win.geometry(f"450x450+{x}+{y}")
        
        tk.Label(win, text="تسجيل دفعة نقدية / سماح", font=self.fonts['header'], bg='white', fg=self.colors['accent_green']).pack(pady=20)
        
        # Fields
        form = tk.Frame(win, bg='white')
        form.pack(pady=10)
        
        # Sellers
        sellers = self.db.get_all_sellers_accounts()
        seller_names = [s[1] for s in sellers]
        
        tk.Label(form, text="اختر البائع:", font=('Arial', 12), bg='white').grid(row=0, column=1, padx=5, pady=10, sticky='e')
        combo_seller = ttk.Combobox(form, values=seller_names, font=('Arial', 12), justify='right', width=20)
        combo_seller.grid(row=0, column=0, padx=5, pady=10)
        
        # Paid Amount
        tk.Label(form, text="المبلغ المدفوع:", font=('Arial', 12), bg='white').grid(row=1, column=1, padx=5, pady=10, sticky='e')
        entry_amount = tk.Entry(form, font=('Arial', 14), justify='center', width=22, bg='#F4F6F7')
        entry_amount.grid(row=1, column=0, padx=5, pady=10)
        entry_amount.insert(0, "0")
        entry_amount.select_range(0, tk.END)
        entry_amount.focus()
        
        # Discount Amount
        tk.Label(form, text="قيمة السماح (خصم):", font=('Arial', 12), bg='white').grid(row=2, column=1, padx=5, pady=10, sticky='e')
        entry_discount = tk.Entry(form, font=('Arial', 14), justify='center', width=22, bg='#FDF2E9')
        entry_discount.grid(row=2, column=0, padx=5, pady=10)
        entry_discount.insert(0, "0")
        
        # Note
        tk.Label(form, text="ملاحظات:", font=('Arial', 12), bg='white').grid(row=3, column=1, padx=5, pady=10, sticky='e')
        entry_note = tk.Entry(form, font=('Arial', 12), justify='right', width=22, bg='#F4F6F7')
        entry_note.grid(row=3, column=0, padx=5, pady=10)
        
        def save():
            seller_name = combo_seller.get()
            amount_str = entry_amount.get().strip()
            discount_str = entry_discount.get().strip()
            note = entry_note.get().strip()
            
            if not seller_name or seller_name not in seller_names:
                messagebox.showwarning("تنبيه", "الرجاء اختيار بائع صحيح", parent=win)
                return
            
            added = False
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Save Payment
            if amount_str and amount_str != "0":
                try:
                    amount = float(amount_str)
                    if amount > 0:
                        seller_data = self.db.get_seller_by_name(seller_name)
                        if seller_data:
                            seller_id = seller_data[0]
                            self.db.add_seller_transaction(
                                seller_id, amount, "مدفوع", 0, 0, 0, 
                                "تحصيل نقدية", today, "", "", note
                            )
                            added = True
                except ValueError:
                    messagebox.showerror("خطأ", "الرجاء إدخال مبلغ مدفوع صحيح", parent=win)
                    return
            
            # Save Discount
            if discount_str and discount_str != "0":
                try:
                    discount = float(discount_str)
                    if discount > 0:
                        seller_data = self.db.get_seller_by_name(seller_name)
                        if seller_data:
                            seller_id = seller_data[0]
                            self.db.add_seller_transaction(
                                seller_id, discount, "سماح", 0, 0, 0, 
                                "سماح", today, "", "", note
                            )
                            added = True
                except ValueError:
                    messagebox.showerror("خطأ", "الرجاء إدخال مبلغ سماح صحيح", parent=win)
                    return
                    
            if added:
                messagebox.showinfo("نجاح", "تم تسجيل العملية بنجاح", parent=win)
                win.destroy()
                self.refresh_banner()
            else:
                messagebox.showwarning("تنبيه", "الرجاء إدخال مبلغ مدفوع أو سماح", parent=win)
            
        tk.Button(win, text="حفظ", command=save, bg=self.colors['accent_green'], fg='white', font=self.fonts['button'], width=15).pack(pady=20)

    def open_add_expense(self):
        """Open Add Expense Window"""
        win = tk.Toplevel(self.window)
        win.title("إضافة منصرف")
        win.geometry("400x400")
        win.configure(bg='white')
        
        # Center
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - 200
        y = (win.winfo_screenheight() // 2) - 200
        win.geometry(f"400x400+{x}+{y}")
        
        tk.Label(win, text="تسجيل مصروف جديد", font=self.fonts['header'], bg='white', fg=self.colors['accent_red']).pack(pady=20)
        
        form = tk.Frame(win, bg='white')
        form.pack(pady=10)
        
        # Description
        tk.Label(form, text="بيان المصروف:", font=('Arial', 12), bg='white').grid(row=0, column=1, padx=5, pady=10, sticky='e')
        entry_desc = tk.Entry(form, font=('Arial', 12), justify='right', width=25, bg='#F4F6F7')
        entry_desc.grid(row=0, column=0, padx=5, pady=10)
        entry_desc.focus()
        
        # Amount
        tk.Label(form, text="المبلغ:", font=('Arial', 12), bg='white').grid(row=1, column=1, padx=5, pady=10, sticky='e')
        entry_amount = tk.Entry(form, font=('Arial', 14), justify='center', width=25, bg='#F4F6F7')
        entry_amount.grid(row=1, column=0, padx=5, pady=10)
        
        # Note
        tk.Label(form, text="ملاحظات:", font=('Arial', 12), bg='white').grid(row=2, column=1, padx=5, pady=10, sticky='e')
        entry_note = tk.Entry(form, font=('Arial', 12), justify='right', width=25, bg='#F4F6F7')
        entry_note.grid(row=2, column=0, padx=5, pady=10)
        
        def save():
            desc = entry_desc.get().strip()
            amount_str = entry_amount.get().strip()
            note = entry_note.get().strip()
            
            if not desc:
                messagebox.showwarning("تنبيه", "الرجاء إدخال بيان المصروف", parent=win)
                return
            if not amount_str:
                messagebox.showwarning("تنبيه", "الرجاء إدخال المبلغ", parent=win)
                return
                
            try:
                amount = float(amount_str)
                today = datetime.now().strftime("%Y-%m-%d")
                
                self.db.add_expense(desc, amount, today, note)
                
                messagebox.showinfo("نجاح", "تم تسجيل المصروف بنجاح", parent=win)
                win.destroy()
                self.refresh_banner()
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال مبلغ صحيح", parent=win)
                
        tk.Button(win, text="حفظ", command=save, bg=self.colors['accent_red'], fg='white', font=self.fonts['button'], width=15).pack(pady=20)

    def open_collection_list(self):
        """Show list of collections (Seller Transactions where status='مدفوع')"""
        self.show_list_window("قائمة التحصيلات (مدفوع وسماح)", "collection")

    def open_expense_list(self):
        """Show list of expenses"""
        self.show_list_window("قائمة المصروفات", "expense")

    def show_list_window(self, title, list_type):
        win = tk.Toplevel(self.window)
        win.title(title)
        win.geometry("950x600")
        win.configure(bg='white')
        
        # Center Window
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - 475
        y = (win.winfo_screenheight() // 2) - 300
        win.geometry(f"950x600+{x}+{y}")
        
        # Header
        header_lbl = tk.Label(win, text=title, font=self.fonts['header'], bg='white', fg='#2C3E50')
        header_lbl.pack(pady=15)
        
        # Buttons Frame (Top)
        btn_frame = tk.Frame(win, bg='white')
        btn_frame.pack(fill=tk.X, padx=20, pady=5)
        
        if list_type == "collection":
            tk.Button(btn_frame, text="تحديث", command=lambda: self.refresh_list(tree, list_type, total_lbl), 
                     bg='#3498DB', fg='white', font=('Arial', 12, 'bold'), width=10).pack(side=tk.RIGHT, padx=5)
            
            tk.Button(btn_frame, text="تعديل", command=lambda: self.edit_item(tree, "collection", win, lambda: self.refresh_list(tree, list_type, total_lbl)), 
                     bg='#F39C12', fg='white', font=('Arial', 12, 'bold'), width=10).pack(side=tk.RIGHT, padx=5)
            
            tk.Button(btn_frame, text="حذف", command=lambda: self.delete_item(tree, "collection", lambda: self.refresh_list(tree, list_type, total_lbl)), 
                     bg='#E74C3C', fg='white', font=('Arial', 12, 'bold'), width=10).pack(side=tk.RIGHT, padx=5)
        
        elif list_type == "expense":
             tk.Button(btn_frame, text="حذف", command=lambda: self.delete_item(tree, "expense", lambda: self.refresh_list(tree, list_type, total_lbl)), 
                     bg='#E74C3C', fg='white', font=('Arial', 12, 'bold'), width=10).pack(side=tk.RIGHT, padx=5)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=('Playpen Sans Arabic', 12, 'bold'), background="#2C3E50", foreground="white", padding=5)
        style.configure("Treeview", font=('Arial', 12), rowheight=30)
        style.map("Treeview", background=[('selected', '#3498DB')])
        
        # Treeview
        tree_frame = tk.Frame(win, bg='white', padx=10, pady=10)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll_y = ttk.Scrollbar(tree_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        if list_type == "collection":
            cols = ('id', 'date', 'seller', 'type', 'amount', 'note')
            headers = {'id': 'ID', 'date': 'التاريخ', 'seller': 'البائع', 'type': 'النوع', 'amount': 'المبلغ', 'note': 'ملاحظات'}
            display_cols = ('date', 'seller', 'type', 'amount', 'note')
        else:
            cols = ('id', 'date', 'desc', 'amount', 'note')
            headers = {'id': 'ID', 'date': 'التاريخ', 'desc': 'البيان', 'amount': 'المبلغ', 'note': 'ملاحظات'}
            display_cols = ('date', 'desc', 'amount', 'note')
            
        tree = ttk.Treeview(tree_frame, columns=cols, displaycolumns=display_cols, show='headings', yscrollcommand=scroll_y.set, selectmode='browse')
        scroll_y.config(command=tree.yview)
        
        for col in display_cols:
            tree.heading(col, text=headers[col])
            tree.column(col, anchor='center', width=130)
            
        if list_type == "collection":
            tree.column('type', width=100)
            tree.column('amount', width=100)
            tree.column('note', width=200)
            
            # Tags for coloring
            tree.tag_configure('paid', foreground='#27AE60') # Green text
            tree.tag_configure('discount', foreground='#E67E22') # Orange text
            
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Footer (Total)
        total_frame = tk.Frame(win, bg='#ECF0F1', pady=10)
        total_frame.pack(fill=tk.X)
        
        total_lbl = tk.Label(total_frame, text="الإجمالي: 0.00", font=('Arial', 16, 'bold'), bg='#ECF0F1', fg='#2C3E50')
        total_lbl.pack()
        
        # Load Data
        self.refresh_list(tree, list_type, total_lbl)

    def refresh_list(self, tree, list_type, total_lbl):
        # Clear
        for item in tree.get_children():
            tree.delete(item)
            
        total = 0.0
        
        if list_type == "collection":
            # Use updated DB method (including Discount)
            collections = self.db.get_all_collections()
            for item in collections:
                # item: id, seller_name, amount, date, note, status
                t_id = item[0]
                seller = item[1]
                amount = item[2]
                date = item[3]
                note = item[4]
                status = item[5]
                
                try:
                    amount_val = float(amount)
                    total += amount_val
                except: pass
                
                # Tag based on status
                tag = 'paid'
                if status == "سماح":
                    tag = 'discount'
                
                # Insert
                tree.insert('', tk.END, values=(t_id, date, seller, status, format_clean_number(amount), note), tags=(tag,))
                
        else: # expenses
            expenses = self.db.get_all_expenses()
            for exp in expenses:
                # exp: id, desc, amount, date, note
                # columns: id, date, desc, amount, note
                t_id = exp[0]
                desc = exp[1]
                amount = exp[2]
                date = exp[3]
                note = exp[4]
                
                try:
                    amount_val = float(amount)
                    total += amount_val
                except: pass
                
                tree.insert('', tk.END, values=(t_id, date, desc, format_clean_number(amount), note))

        total_lbl.config(text=f"الإجمالي: {format_clean_number(total)}")

    def delete_item(self, tree, list_type, callback):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء اختيار عنصر للحذف")
            return
            
        item = tree.item(selected[0])
        record_id = item['values'][0] # ID is hidden first column in logic but passed in values
        
        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف هذا السجل؟\nسيتم تحديث حساب البائع تلقائياً."):
            if list_type == "collection":
                self.db.delete_seller_transaction(record_id)
            else:
                self.db.delete_expense(record_id)
            
            callback()
            self.refresh_banner() # Refresh main page stats

    def edit_item(self, tree, list_type, parent, callback):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء اختيار عنصر للتعديل")
            return
            
        item = tree.item(selected[0])
        values = item['values']
        record_id = values[0]
        
        # values depending on list_type
        # collection: id, date, seller, type, amount, note
        
        if list_type == "collection":
            seller_name = values[2]
            current_date = values[1]
            status_type = values[3]
            current_amount = str(values[4]).replace(',', '') # format_clean_number adds commas
            current_note = values[5]
            
            dialog = tk.Toplevel(parent)
            dialog.title(f"تعديل {status_type}")
            dialog.geometry("400x450")
            dialog.configure(bg='white')
            
            # Center
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - 200
            y = (dialog.winfo_screenheight() // 2) - 225
            dialog.geometry(f"400x450+{x}+{y}")
            
            tk.Label(dialog, text=f"تعديل {status_type}: {seller_name}", font=('Arial', 12, 'bold'), bg='white').pack(pady=10)
            
            # Date
            tk.Label(dialog, text="التاريخ (YYYY-MM-DD):", font=('Arial', 12), bg='white').pack(pady=5)
            entry_date = tk.Entry(dialog, font=('Arial', 14), justify='center', bg='#F4F6F7')
            entry_date.pack(pady=5)
            entry_date.insert(0, str(current_date))
            
            # Amount
            tk.Label(dialog, text="المبلغ:", font=('Arial', 12), bg='white').pack(pady=5)
            entry_amt = tk.Entry(dialog, font=('Arial', 14), justify='center', bg='#F4F6F7')
            entry_amt.pack(pady=5)
            entry_amt.insert(0, str(current_amount))
            entry_amt.focus()
            entry_amt.select_range(0, tk.END)
            
            # Note
            tk.Label(dialog, text="ملاحظات:", font=('Arial', 12), bg='white').pack(pady=5)
            entry_note = tk.Entry(dialog, font=('Arial', 12), justify='right', bg='#F4F6F7', width=30)
            entry_note.pack(pady=5)
            entry_note.insert(0, current_note)
            
            def save_changes():
                new_date = entry_date.get().strip()
                new_amt = entry_amt.get().strip()
                new_note = entry_note.get().strip()
                
                # Check date format
                try:
                    datetime.strptime(new_date, '%Y-%m-%d')
                except ValueError:
                    messagebox.showerror("خطأ", "تنسيق التاريخ غير صحيح (YYYY-MM-DD)")
                    return
                
                try:
                    amount = float(new_amt)
                    
                    seller_data = self.db.get_seller_by_name(seller_name)
                    if not seller_data:
                        messagebox.showerror("خطأ", "بيانات البائع غير موجودة")
                        return
                        
                    seller_id = seller_data[0]
                    transactions = self.db.get_seller_transactions(seller_id)
                    target_trans = None
                    for t in transactions:
                        if int(t[0]) == int(record_id):
                            target_trans = t
                            break
                    
                    if target_trans:
                        # Update transaction (preserve status type)
                        self.db.update_seller_transaction(
                            record_id, amount, target_trans[2], target_trans[3], target_trans[4], 
                            target_trans[5], target_trans[6], new_date, target_trans[8], 
                            target_trans[9], new_note
                        )
                        
                        messagebox.showinfo("نجاح", "تم التعديل بنجاح")
                        dialog.destroy()
                        callback()
                        self.refresh_banner()
                    else:
                        messagebox.showerror("خطأ", "لم يتم العثور على السجل الأصلي")
                        
                except ValueError:
                    messagebox.showerror("خطأ", "الرجاء إدخال مبلغ صحيح")
            
            tk.Button(dialog, text="حفظ التعديلات", command=save_changes, bg='#27AE60', fg='white', font=('Arial', 12, 'bold'), width=15).pack(pady=20)


    def refresh_banner(self):
        # Destroy old banner content and recreate or just update labels
        # For simplicity, let's just close and reopen the page? No, that's bad UX.
        # Let's update the labels if we stored references, but I didn't.
        # I'll just re-call create_banner but I need to clear the frame first.
        # Actually, simpler: just close this window and let user reopen it? No.
        # Let's just update the window by destroying all children and rebuilding UI
        for widget in self.window.winfo_children():
            widget.destroy()
        self.setup_ui()

    def open_reports(self):
        """فتح صفحة التقارير"""
        from reports_page import DailyReportsPage
        DailyReportsPage(self.window)
