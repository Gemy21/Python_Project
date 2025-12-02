import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import ColorManager
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
        
        # Calculate Totals
        total_collection = self.calculate_total_collection()
        total_expenses = self.calculate_total_expenses()
        daily_profit = self.calculate_daily_profit()
        
        # Collection Card (Right)
        self.create_stat_card(
            stats_frame, 
            "إجمالي التحصيل", 
            f"{total_collection:,.2f}", 
            self.colors['accent_green'], 
            tk.RIGHT
        )
        
        # Daily Profit Card (Center)
        self.create_stat_card(
            stats_frame, 
            "صافي ربح اليوم", 
            f"{daily_profit:,.2f}", 
            '#F39C12',
            tk.RIGHT
        )
        
        # Expenses Card (Left)
        self.create_stat_card(
            stats_frame, 
            "إجمالي المصاريف", 
            f"{total_expenses:,.2f}", 
            self.colors['accent_red'], 
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
        
        # Grid layout for 4 buttons (2x2)
        
        # Row 1
        self.create_big_button(btn_container, "إضافة تحصيل", self.open_add_collection, self.colors['accent_green'], 0, 1)
        self.create_big_button(btn_container, "إضافة منصرف", self.open_add_expense, self.colors['accent_red'], 0, 0)
        
        # Row 2
        self.create_big_button(btn_container, "قائمة التحصيل", self.open_collection_list, '#2980B9', 1, 1) # Blue
        self.create_big_button(btn_container, "قائمة المنصرف", self.open_expense_list, '#8E44AD', 1, 0)   # Purple
        
    def create_big_button(self, parent, text, command, color, row, col):
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
        btn.grid(row=row, column=col, padx=20, pady=20)
        
    # --- Calculations ---
    def calculate_total_collection(self):
        """
        Calculate total collection: Sum of seller transfers (agriculture transfers to sellers)
        This is the value of goods transferred to sellers (status='متبقي')
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM seller_transactions WHERE status='متبقي'")
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 0.0

    def calculate_total_expenses(self):
        """
        Calculate total expenses: 
        Sum of 'expenses' table + Sum of ready client invoices (agriculture_transfers type='in')
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # 1. Sum of direct expenses
        cursor.execute("SELECT SUM(amount) FROM expenses")
        res_expenses = cursor.fetchone()[0]
        total_expenses = res_expenses if res_expenses else 0.0
        
        # 2. Sum of client invoices (transfers type='in')
        # Value = weight * unit_price OR count * unit_price
        cursor.execute("SELECT weight, count, unit_price FROM agriculture_transfers WHERE transfer_type='in'")
        transfers = cursor.fetchall()
        
        total_invoices = 0.0
        for weight, count, price in transfers:
            w = weight if weight else 0.0
            c = count if count else 0.0
            p = price if price else 0.0
            
            if w > 0:
                total_invoices += w * p
            elif c > 0:
                total_invoices += c * p
                
        conn.close()
        
        return total_expenses + total_invoices

    def calculate_daily_profit(self):
        """
        Calculate daily profit: Sum of payments received today (status='مدفوع')
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT SUM(amount) FROM seller_transactions WHERE status='مدفوع' AND date=?", (today,))
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 0.0

    # --- Actions ---
    def open_add_collection(self):
        """Open Add Collection Window (Same logic as main.py but local)"""
        win = tk.Toplevel(self.window)
        win.title("إضافة تحصيل نقدية")
        win.geometry("400x350")
        win.configure(bg='white')
        
        # Center
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - 200
        y = (win.winfo_screenheight() // 2) - 175
        win.geometry(f"400x350+{x}+{y}")
        
        tk.Label(win, text="تسجيل دفعة نقدية (تحصيل)", font=self.fonts['header'], bg='white', fg=self.colors['accent_green']).pack(pady=20)
        
        # Fields
        form = tk.Frame(win, bg='white')
        form.pack(pady=10)
        
        # Sellers
        sellers = self.db.get_all_sellers_accounts()
        seller_names = [s[1] for s in sellers]
        
        tk.Label(form, text="اختر البائع:", font=('Arial', 12), bg='white').grid(row=0, column=1, padx=5, pady=10, sticky='e')
        combo_seller = ttk.Combobox(form, values=seller_names, font=('Arial', 12), justify='right', width=20)
        combo_seller.grid(row=0, column=0, padx=5, pady=10)
        
        tk.Label(form, text="المبلغ:", font=('Arial', 12), bg='white').grid(row=1, column=1, padx=5, pady=10, sticky='e')
        entry_amount = tk.Entry(form, font=('Arial', 14), justify='center', width=22, bg='#F4F6F7')
        entry_amount.grid(row=1, column=0, padx=5, pady=10)
        entry_amount.focus()
        
        def save():
            seller_name = combo_seller.get()
            amount_str = entry_amount.get().strip()
            
            if not seller_name or seller_name not in seller_names:
                messagebox.showwarning("تنبيه", "الرجاء اختيار بائع صحيح", parent=win)
                return
            if not amount_str:
                messagebox.showwarning("تنبيه", "الرجاء إدخال المبلغ", parent=win)
                return
                
            try:
                amount = float(amount_str)
                seller_data = self.db.get_seller_by_name(seller_name)
                if seller_data:
                    seller_id = seller_data[0]
                    today = datetime.now().strftime("%Y-%m-%d")
                    
                    self.db.add_seller_transaction(
                        seller_id, amount, "مدفوع", 0, 0, 0, 
                        "تحصيل نقدية", today, "", "", ""
                    )
                    messagebox.showinfo("نجاح", "تم تسجيل التحصيل بنجاح", parent=win)
                    win.destroy()
                    self.refresh_banner()
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال مبلغ صحيح", parent=win)
                
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
        self.show_list_window("قائمة التحصيلات", "collection")

    def open_expense_list(self):
        """Show list of expenses"""
        self.show_list_window("قائمة المصروفات", "expense")

    def show_list_window(self, title, list_type):
        win = tk.Toplevel(self.window)
        win.title(title)
        win.geometry("800x600")
        win.configure(bg='white')
        
        tk.Label(win, text=title, font=self.fonts['header'], bg='white', fg='#2C3E50').pack(pady=15)
        
        # Treeview
        tree_frame = tk.Frame(win, bg='white', padx=10, pady=10)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll_y = ttk.Scrollbar(tree_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        if list_type == "collection":
            cols = ('date', 'seller', 'amount', 'note')
            headers = {'date': 'التاريخ', 'seller': 'البائع', 'amount': 'المبلغ', 'note': 'ملاحظات'}
        else:
            cols = ('date', 'desc', 'amount', 'note')
            headers = {'date': 'التاريخ', 'desc': 'البيان', 'amount': 'المبلغ', 'note': 'ملاحظات'}
            
        tree = ttk.Treeview(tree_frame, columns=cols, show='headings', yscrollcommand=scroll_y.set)
        scroll_y.config(command=tree.yview)
        
        for col, text in headers.items():
            tree.heading(col, text=text)
            tree.column(col, anchor='center')
            
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Load Data
        if list_type == "collection":
            # Need to join with seller name manually or fetch all transactions and filter
            # Since get_seller_transactions is per seller, we might need a new DB function or iterate all sellers
            # For efficiency, let's fetch all sellers and their transactions
            sellers = self.db.get_all_sellers_accounts()
            all_trans = []
            for seller in sellers:
                # seller: id, name, ...
                s_id = seller[0]
                s_name = seller[1]
                trans = self.db.get_seller_transactions(s_id)
                for t in trans:
                    # t: id, amount, status, ... date ... note
                    if t[2] == "مدفوع":
                        all_trans.append({
                            'date': t[7],
                            'seller': s_name,
                            'amount': t[1],
                            'note': t[10]
                        })
            # Sort by date
            all_trans.sort(key=lambda x: x['date'], reverse=True)
            
            for item in all_trans:
                tree.insert('', tk.END, values=(item['date'], item['seller'], f"{item['amount']:.2f}", item['note']))
                
        else: # expenses
            expenses = self.db.get_all_expenses()
            for exp in expenses:
                # exp: id, desc, amount, date, note
                tree.insert('', tk.END, values=(exp[3], exp[1], f"{exp[2]:.2f}", exp[4]))

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
