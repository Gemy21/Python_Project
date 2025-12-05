import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from datetime import datetime, timedelta
import calendar

class DailyReportsPage:
    def __init__(self, parent_window):
        self.db = Database()
        
        self.colors = {
            'bg': '#FFB347',
            'header_bg': '#6C3483',
            'card_bg': 'white',
            'button_bg': '#800000',
            'button_fg': 'white'
        }
        
        self.window = tk.Toplevel(parent_window)
        self.window.title("التقارير اليومية والشهرية")
        self.window.geometry("1200x700")
        self.window.configure(bg=self.colors['bg'])
        
        self.setup_ui()
        self.load_today_report()
    
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.window, bg=self.colors['header_bg'], height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="التقارير اليومية والشهرية", 
                font=('Playpen Sans Arabic', 20, 'bold'),
                bg=self.colors['header_bg'], fg='white').pack(pady=15)
        
        # Main Container
        main_frame = tk.Frame(self.window, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left Panel - Daily Report
        left_panel = tk.Frame(main_frame, bg=self.colors['card_bg'], relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left_panel, text="التقرير اليومي", font=('Playpen Sans Arabic', 16, 'bold'),
                bg=self.colors['card_bg']).pack(pady=10)
        
        # Date Selection
        date_frame = tk.Frame(left_panel, bg=self.colors['card_bg'])
        date_frame.pack(pady=10)
        
        tk.Label(date_frame, text="التاريخ:", font=('Arial', 12, 'bold'),
                bg=self.colors['card_bg']).pack(side=tk.RIGHT, padx=5)
        
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(date_frame, textvariable=self.date_var, font=('Arial', 12),
                             justify='center', width=15)
        date_entry.pack(side=tk.RIGHT, padx=5)
        
        tk.Button(date_frame, text="تحديث", command=self.load_selected_date_report,
                 bg=self.colors['button_bg'], fg='white', font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, padx=5)
        
        # Daily Stats
        stats_frame = tk.Frame(left_panel, bg=self.colors['card_bg'])
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Collection
        self.create_stat_row(stats_frame, "إجمالي التحصيل:", "collection", 0, '#27AE60')
        
        # Expenses
        self.create_stat_row(stats_frame, "المصاريف:", "expenses", 1, '#E74C3C')
        
        # Remaining Profit
        self.create_stat_row(stats_frame, "صافي ربح اليوم:", "remaining", 2, '#3498DB')
        
        # Buttons
        btn_frame = tk.Frame(left_panel, bg=self.colors['card_bg'])
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="حفظ التقرير", command=self.save_current_report,
                 bg='#27AE60', fg='white', font=('Playpen Sans Arabic', 12, 'bold'),
                 width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="حساب تلقائي", command=self.auto_calculate,
                 bg='#2980B9', fg='white', font=('Playpen Sans Arabic', 12, 'bold'),
                 width=15).pack(side=tk.LEFT, padx=5)
        
        # Right Panel - Monthly Report
        right_panel = tk.Frame(main_frame, bg=self.colors['card_bg'], relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(right_panel, text="التقرير الشهري", font=('Playpen Sans Arabic', 16, 'bold'),
                bg=self.colors['card_bg']).pack(pady=10)
        
        # Month/Year Selection
        month_frame = tk.Frame(right_panel, bg=self.colors['card_bg'])
        month_frame.pack(pady=10)
        
        current_date = datetime.now()
        
        tk.Label(month_frame, text="الشهر:", font=('Arial', 12, 'bold'),
                bg=self.colors['card_bg']).pack(side=tk.RIGHT, padx=5)
        
        self.month_var = tk.StringVar(value=str(current_date.month))
        month_combo = ttk.Combobox(month_frame, textvariable=self.month_var,
                                   values=[str(i) for i in range(1, 13)],
                                   width=5, justify='center', state='readonly')
        month_combo.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(month_frame, text="السنة:", font=('Arial', 12, 'bold'),
                bg=self.colors['card_bg']).pack(side=tk.RIGHT, padx=5)
        
        self.year_var = tk.StringVar(value=str(current_date.year))
        year_entry = tk.Entry(month_frame, textvariable=self.year_var, font=('Arial', 12),
                             justify='center', width=8)
        year_entry.pack(side=tk.RIGHT, padx=5)
        
        tk.Button(month_frame, text="عرض", command=self.load_monthly_report,
                 bg=self.colors['button_bg'], fg='white', font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, padx=5)
        
        # Monthly Table
        table_frame = tk.Frame(right_panel, bg=self.colors['card_bg'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview
        columns = ('date', 'collection', 'expenses', 'remaining')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('date', text='التاريخ')
        self.tree.heading('collection', text='التحصيل')
        self.tree.heading('expenses', text='المصاريف')
        self.tree.heading('remaining', text='الباقي')
        
        self.tree.column('date', width=100, anchor='center')
        self.tree.column('collection', width=100, anchor='center')
        self.tree.column('expenses', width=100, anchor='center')
        self.tree.column('remaining', width=100, anchor='center')
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Monthly Totals
        totals_frame = tk.Frame(right_panel, bg='#34495E')
        totals_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(totals_frame, text="إجماليات الشهر:", font=('Playpen Sans Arabic', 14, 'bold'),
                bg='#34495E', fg='white').pack(pady=5)
        
        self.monthly_totals_label = tk.Label(totals_frame, text="", font=('Arial', 12, 'bold'),
                                             bg='#34495E', fg='white')
        self.monthly_totals_label.pack(pady=5)
    
    def create_stat_row(self, parent, label_text, var_name, row, color):
        frame = tk.Frame(parent, bg=self.colors['card_bg'])
        frame.pack(fill=tk.X, pady=10)
        
        tk.Label(frame, text=label_text, font=('Playpen Sans Arabic', 14, 'bold'),
                bg=self.colors['card_bg']).pack(side=tk.RIGHT, padx=10)
        
        value_label = tk.Label(frame, text="0.00 ج.م", font=('Arial', 16, 'bold'),
                              bg=color, fg='white', width=20, relief=tk.SUNKEN)
        value_label.pack(side=tk.LEFT, padx=10)
        
        setattr(self, f"{var_name}_label", value_label)
    
    def load_today_report(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_var.set(today)
        self.load_selected_date_report()
    
    def load_selected_date_report(self):
        target_date = self.date_var.get()
        
        # Try to load saved report
        report = self.db.get_daily_report(target_date)
        
        if report:
            collection = report[1]
            remaining = report[2]
            expenses = report[3]
        else:
            # Calculate from transactions
            totals = self.db.calculate_daily_totals(target_date)
            collection = totals['total_collection']
            remaining = totals['remaining_profit']
            expenses = totals['total_expenses']
        
        self.collection_label.config(text=f"{collection:,.2f} ج.م")
        self.expenses_label.config(text=f"{expenses:,.2f} ج.م")
        self.remaining_label.config(text=f"{remaining:,.2f} ج.م")
    
    def auto_calculate(self):
        target_date = self.date_var.get()
        totals = self.db.calculate_daily_totals(target_date)
        
        collection = totals['total_collection']
        remaining = totals['remaining_profit']
        expenses = totals['total_expenses']
        
        self.collection_label.config(text=f"{collection:,.2f} ج.م")
        self.expenses_label.config(text=f"{expenses:,.2f} ج.م")
        self.remaining_label.config(text=f"{remaining:,.2f} ج.م")
        
        messagebox.showinfo("نجاح", "تم حساب البيانات تلقائياً من المعاملات")
    
    def save_current_report(self):
        target_date = self.date_var.get()
        
        # Get current values
        totals = self.db.calculate_daily_totals(target_date)
        
        self.db.save_daily_report(
            target_date,
            totals['total_collection'],
            totals['remaining_profit'],
            totals['total_expenses']
        )
        
        messagebox.showinfo("نجاح", f"تم حفظ تقرير يوم {target_date}")
    
    def load_monthly_report(self):
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء إدخال سنة وشهر صحيحين")
            return
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get monthly reports
        reports = self.db.get_monthly_reports(year, month)
        
        total_collection = 0
        total_remaining = 0
        total_expenses = 0
        
        for report in reports:
            date = report[0]
            collection = report[1]
            remaining = report[2]
            expenses = report[3]
            
            self.tree.insert('', tk.END, values=(
                date,
                f"{collection:,.2f}",
                f"{expenses:,.2f}",
                f"{remaining:,.2f}"
            ))
            
            total_collection += collection
            total_remaining += remaining
            total_expenses += expenses
        
        # Update totals
        self.monthly_totals_label.config(
            text=f"التحصيل: {total_collection:,.2f} | المصاريف: {total_expenses:,.2f} | الباقي: {total_remaining:,.2f}"
        )
        
        if not reports:
            messagebox.showinfo("تنبيه", "لا توجد تقارير لهذا الشهر")
