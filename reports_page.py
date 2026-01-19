import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from datetime import datetime
from utils import format_clean_number

class DailyReportsPage:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        
        self.window = tk.Toplevel(parent)
        self.window.title("التقارير والإحصائيات")
        self.window.geometry("1000x700")
        self.window.state('zoomed')
        self.window.configure(bg='#ECF0F1')
        
        # Main Title
        header = tk.Frame(self.window, bg='#2C3E50', pady=20)
        header.pack(fill=tk.X)
        tk.Label(header, text="التقارير المالية والتحليلية", font=('Simplified Arabic', 20, 'bold'), 
                 bg='#2C3E50', fg='white').pack()

        # Tabs
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=('Simplified Arabic', 12, 'bold'), padding=[20, 10])
        
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Tabs Frames
        self.tab_daily = tk.Frame(self.notebook, bg='#ECF0F1')
        self.tab_sellers = tk.Frame(self.notebook, bg='#ECF0F1')
        self.tab_commissions = tk.Frame(self.notebook, bg='#ECF0F1')
        
        self.notebook.add(self.tab_daily, text=" تقرير الخزنة والأرباح (التحصيل والمنصرف) ")
        self.notebook.add(self.tab_sellers, text=" تقارير حركة بضاعة البائعين ")
        self.notebook.add(self.tab_commissions, text=" تقارير عمولات فواتير العملاء ")
        
        # Setup Tabs
        self.setup_daily_profit_ui()
        self.setup_sellers_report_ui()
        self.setup_commissions_report_ui()

    # --- Tab 1: Daily Profit & Treasury (Original Functionality restored) ---
    def setup_daily_profit_ui(self):
        container = tk.Frame(self.tab_daily, bg='white', padx=30, pady=30, relief=tk.RIDGE, bd=1)
        container.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Header
        tk.Label(container, text="تقرير الخزنة والأرباح اليومية", font=('Simplified Arabic', 18, 'bold'), bg='white', fg='#2C3E50').pack(pady=(0, 20))
        
        # Date Selection
        sel_frame = tk.Frame(container, bg='white')
        sel_frame.pack(pady=10)
        tk.Label(sel_frame, text="اختر التاريخ:", bg='white', font=('Arial', 12, 'bold')).pack(side=tk.RIGHT, padx=10)
        
        self.daily_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        entry_date = tk.Entry(sel_frame, textvariable=self.daily_date_var, width=15, font=('Arial', 12), justify='center', relief=tk.SOLID, bd=1)
        entry_date.pack(side=tk.RIGHT, padx=10)
        
        btn_show = tk.Button(sel_frame, text="عرض التقرير", command=self.show_daily_profit, 
                            bg='#3498DB', fg='white', font=('Arial', 11, 'bold'))
        btn_show.pack(side=tk.RIGHT, padx=10)
        
        # Results Grid
        res_frame = tk.Frame(container, bg='white', pady=30)
        res_frame.pack(fill=tk.X)
        
        # Define cards
        self.lbl_collection = self._create_card(res_frame, "إجمالي التحصيل (الوارد)", "#27AE60", 0)
        self.lbl_expenses = self._create_card(res_frame, "إجمالي المنصرف (الصادر)", "#C0392B", 1)
        self.lbl_profit = self._create_card(res_frame, "صافي الخزنة / الربح", "#2C3E50", 2)
        
        # Load today's data initially
        self.show_daily_profit()

    def _create_card(self, parent, title, color, col_idx):
        frame = tk.Frame(parent, bg=color, padx=20, pady=20, width=250, height=150)
        frame.grid(row=0, column=col_idx, padx=20, sticky='nsew')
        parent.grid_columnconfigure(col_idx, weight=1)
        frame.pack_propagate(False)
        
        tk.Label(frame, text=title, font=('Simplified Arabic', 14, 'bold'), bg=color, fg='white').pack(pady=(10, 5))
        lbl_val = tk.Label(frame, text="0.00", font=('Arial', 20, 'bold'), bg=color, fg='white')
        lbl_val.pack(pady=10)
        return lbl_val

    def show_daily_profit(self):
        date_val = self.daily_date_var.get()
        # Use existing method in Database
        data = self.db.calculate_daily_totals(date_val)
        
        self.lbl_collection.config(text=format_clean_number(data['total_collection']))
        self.lbl_expenses.config(text=format_clean_number(data['total_expenses']))
        self.lbl_profit.config(text=format_clean_number(data['remaining_profit']))

    # --- Tab 2: Seller Goods Report ---
    def setup_sellers_report_ui(self):
        self._setup_generic_report_ui(
            parent_frame=self.tab_sellers,
            title="تقارير إجمالي قيمة البضاعة المرحلة للبائعين",
            desc="إجمالي قيمة البضاعة (سعر × وزن/عدد) التي تم ترحيلها للبائعين خلال الفترة المحددة",
            action_callback=self.calc_sellers_report,
            result_label_attr="lbl_sellers_result",
            color="#E67E22"
        )

    # --- Tab 3: Commissions Report ---
    def setup_commissions_report_ui(self):
        self._setup_generic_report_ui(
            parent_frame=self.tab_commissions,
            title="تقارير إيرادات العمولات",
            desc="إجمالي العمولات (القيمة المادية) المحصلة من فواتير العملاء خلال الفترة المحددة",
            action_callback=self.calc_commissions_report,
            result_label_attr="lbl_commissions_result",
            color="#8E44AD"
        )

    # --- Generic Report UI Builder ---
    def _setup_generic_report_ui(self, parent_frame, title, desc, action_callback, result_label_attr, color):
        container = tk.Frame(parent_frame, bg='white', padx=30, pady=30, relief=tk.RIDGE, bd=1)
        container.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        tk.Label(container, text=title, font=('Simplified Arabic', 16, 'bold'), bg='white', fg=color).pack(pady=(0, 10))
        tk.Label(container, text=desc, font=('Arial', 11), bg='white', fg='#7F8C8D').pack(pady=(0, 20))
        
        select_frame = tk.LabelFrame(container, text="خيارات الفترة", bg='white', font=('Arial', 12, 'bold'), padx=20, pady=20)
        select_frame.pack(pady=10)
        
        tk.Label(select_frame, text="نوع التقرير:", bg='white', font=('Arial', 12)).grid(row=0, column=2, padx=10, sticky='e')
        period_var = tk.StringVar(value="يومي")
        combo_period = ttk.Combobox(select_frame, textvariable=period_var, values=["يومي", "شهري", "سنوي"], state="readonly", width=15)
        combo_period.grid(row=0, column=1, padx=10)
        combo_period.current(0)
        
        inputs_frame = tk.Frame(select_frame, bg='white')
        inputs_frame.grid(row=1, column=0, columnspan=3, pady=20)
        
        year_var = tk.StringVar(value=datetime.now().strftime("%Y"))
        month_var = tk.StringVar(value=datetime.now().strftime("%m"))
        day_var = tk.StringVar(value=datetime.now().strftime("%d"))
        
        def update_inputs(*args):
            for widget in inputs_frame.winfo_children():
                widget.destroy()
            p_type = combo_period.get()
            
            # Year
            tk.Label(inputs_frame, text="السنة:", bg='white').pack(side=tk.RIGHT, padx=5)
            tk.Entry(inputs_frame, textvariable=year_var, width=6, justify='center', relief=tk.SOLID, bd=1).pack(side=tk.RIGHT, padx=5)
            
            if p_type in ["شهري", "يومي"]:
                tk.Label(inputs_frame, text="الشهر:", bg='white').pack(side=tk.RIGHT, padx=5)
                m_vals = [f"{i:02d}" for i in range(1, 13)]
                ttk.Combobox(inputs_frame, textvariable=month_var, values=m_vals, width=4, state="readonly").pack(side=tk.RIGHT, padx=5)
                
            if p_type == "يومي":
                tk.Label(inputs_frame, text="اليوم:", bg='white').pack(side=tk.RIGHT, padx=5)
                d_vals = [f"{i:02d}" for i in range(1, 32)]
                ttk.Combobox(inputs_frame, textvariable=day_var, values=d_vals, width=4, state="readonly").pack(side=tk.RIGHT, padx=5)

        combo_period.bind("<<ComboboxSelected>>", update_inputs)
        update_inputs()
        
        btn = tk.Button(container, text="عرض التقرير", 
                       command=lambda: action_callback(period_var.get(), year_var.get(), month_var.get(), day_var.get()),
                       bg=color, fg='white', font=('Arial', 12, 'bold'), width=20)
        btn.pack(pady=20)
        
        res_frame = tk.Frame(container, bg='#F4F6F7', padx=30, pady=30, relief=tk.SUNKEN, bd=1)
        res_frame.pack(fill=tk.X, pady=10)
        
        res_label = tk.Label(res_frame, text="---", font=('Arial', 28, 'bold'), bg='#F4F6F7', fg='#2C3E50')
        res_label.pack()
        setattr(self, result_label_attr, res_label)

    def calc_sellers_report(self, period_type, year, month, day):
        if not year.isdigit(): return
        db_period = {"يومي": "day", "شهري": "month", "سنوي": "year"}[period_type]
        date_str = f"{year}-{month}-{day}" if period_type=="يومي" else (f"{year}-{month}" if period_type=="شهري" else year)
            
        val = self.db.get_sellers_sales_total(db_period, date_str)
        getattr(self, "lbl_sellers_result").config(text=f"{format_clean_number(val)} ج.م")

    def calc_commissions_report(self, period_type, year, month, day):
        if not year.isdigit(): return
        db_period = {"يومي": "day", "شهري": "month", "سنوي": "year"}[period_type]
        date_str = f"{year}-{month}-{day}" if period_type=="يومي" else (f"{year}-{month}" if period_type=="شهري" else year)
            
        val = self.db.get_commissions_total_by_period(db_period, date_str)
        getattr(self, "lbl_commissions_result").config(text=f"{format_clean_number(val)} ج.م")
