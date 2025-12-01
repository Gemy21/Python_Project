import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import ColorManager
from datetime import datetime

class AgricultureTransferPage:
    def __init__(self, parent_window):
        self.db = Database()
        self.color_manager = ColorManager()
        self.theme = self.color_manager.get_random_theme()
        
        self.colors = {
            'bg': '#FFB347',           # Orange background like Accounts
            'header_bg': '#6C3483',    # Purple header
            'card_bg': 'white',
            'text_primary': '#2C3E50',
            'text_secondary': '#7F8C8D',
            'accent': '#E67E22',
            'button_bg': '#800000',
            'button_fg': 'white',
            'border': '#BDC3C7'
        }
        
        # Column Colors (Pastels)
        self.col_colors = [
            '#F5CBA7', # Seller (Orange-ish)
            '#F9E79F', # Shipment (Yellow-ish)
            '#F5B7B1', # Item (Pink-ish)
            '#AED6F1', # Price (Blue-ish)
            '#A9DFBF', # Weight (Green-ish)
            '#D7BDE2', # Count (Purple-ish)
            '#E5E7E9'  # Type (Grey-ish)
        ]
        
        self.window = tk.Toplevel(parent_window)
        self.window.title("نظام ترحيل الزراعة")
        self.window.geometry("1300x850")
        self.window.configure(bg=self.colors['bg'])
        self.window.resizable(True, True)
        
        # Fonts
        self.fonts = {
            'header': ('Playpen Sans Arabic', 20, 'bold'),
            'label': ('Playpen Sans Arabic', 14, 'bold'),
            'entry': ('Arial', 14),
            'button': ('Playpen Sans Arabic', 14, 'bold')
        }
        
        # Variables
        self.search_var = tk.StringVar()
        self.filter_item_var = tk.StringVar()
        self.global_price_var = tk.StringVar()
        
        # Input Row Variables
        self.in_seller_var = tk.StringVar()
        self.in_shipment_var = tk.StringVar()
        self.in_item_var = tk.StringVar()
        self.in_price_var = tk.StringVar()
        self.in_weight_var = tk.StringVar()
        self.in_count_var = tk.StringVar()
        
        # Load meal prices
        self.meal_prices = {}
        self.load_meal_prices()
        
        # Bind global price to input price
        self.global_price_var.trace('w', self.update_input_price)
        
        self.table_rows = []
        self.selected_transfer_id = None
        self.selected_row_widgets = []
        self.setup_ui()

    def load_meal_prices(self):
        meals = self.db.get_all_meals()
        # meal: id, name, price, equip
        self.meal_prices = {m[1]: m[2] for m in meals}

        
    def setup_ui(self):
        # --- Top Bar ---
        self.create_top_bar()
        
        # --- Main Content (Table + Input) ---
        main_frame = tk.Frame(self.window, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Input Row (The "Entry" part of the table)
        self.create_input_row(main_frame)
        
        # Table
        self.create_table(main_frame)
        
        # --- Bottom Bar ---
        self.create_bottom_bar()
        
    def create_top_bar(self):
        top_frame = tk.Frame(self.window, bg=self.colors['header_bg'], height=80, padx=20)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)
        
        # Container for controls
        controls = tk.Frame(top_frame, bg=self.colors['header_bg'])
        controls.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Helper for styled entry
        def make_entry(parent, var, width=20):
            e = tk.Entry(parent, textvariable=var, font=self.fonts['entry'], width=width, justify='center')
            return e

        # Right Side: Search 1 (Seller/Transfer)
        search_frame = tk.Frame(controls, bg=self.colors['header_bg'])
        search_frame.pack(side=tk.RIGHT, padx=10)
        tk.Label(search_frame, text="بحث (بائع/نقلة):", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.RIGHT, padx=5)
        search_entry = make_entry(search_frame, self.search_var, width=25)
        search_entry.pack(side=tk.RIGHT)
        search_entry.bind('<KeyRelease>', self.filter_table)
        
        # Middle: Search 2 (Item Filter)
        filter_frame = tk.Frame(controls, bg=self.colors['header_bg'])
        filter_frame.pack(side=tk.RIGHT, padx=20)
        tk.Label(filter_frame, text="تصفية بالصنف:", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.RIGHT, padx=5)
        
        meals = self.db.get_all_meals()
        meal_names = [m[1] for m in meals]
        
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_item_var, values=['الكل'] + meal_names, font=self.fonts['entry'], width=20, justify='center')
        filter_combo.pack(side=tk.RIGHT)
        filter_combo.bind('<<ComboboxSelected>>', self.filter_table)
        filter_combo.current(0)

        # Left: Global Unit Price
        price_frame = tk.Frame(controls, bg=self.colors['header_bg'])
        price_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(price_frame, text="سعر الوحدة (للمدخلات):", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.RIGHT, padx=5)
        price_entry = make_entry(price_frame, self.global_price_var, width=15)
        price_entry.pack(side=tk.RIGHT)
        
    def create_input_row(self, parent):
        # This frame simulates the "New Entry" row
        input_frame = tk.Frame(parent, bg='white', pady=10, padx=10, relief=tk.RAISED, bd=2)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(input_frame, text="إدخال بيانات جديدة:", font=self.fonts['header'], bg='white', fg=self.colors['accent']).pack(anchor='e', pady=(0, 10))
        
        # Grid layout for inputs to match columns roughly
        # Columns: Seller, Shipment, Item, Price, Weight, Count
        # We will use pack side=RIGHT to mimic RTL flow
        
        def add_input(label, var, width=15, is_combo=False, combo_values=None):
            f = tk.Frame(input_frame, bg='white')
            f.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)
            
            tk.Label(f, text=label, font=self.fonts['label'], bg='white').pack(anchor='n')
            
            if is_combo:
                w = ttk.Combobox(f, textvariable=var, values=combo_values, font=self.fonts['entry'], justify='center')
            else:
                w = tk.Entry(f, textvariable=var, font=self.fonts['entry'], justify='center', bg='#F8F9F9', relief=tk.SOLID, bd=1)
                
            w.pack(fill=tk.X, pady=5, ipady=5)
            return w

        # 1. Seller Name
        add_input("اسم البائع", self.in_seller_var, width=20)
        
        # 2. Shipment Name (Auto Date)
        ship_entry = add_input("اسم النقلة", self.in_shipment_var, width=20)
        ship_entry.bind('<FocusOut>', self.append_date_to_shipment)
        
        # 3. Item
        meals = self.db.get_all_meals()
        meal_names = [m[1] for m in meals]
        item_combo = add_input("الصنف", self.in_item_var, is_combo=True, combo_values=meal_names)
        item_combo.bind('<<ComboboxSelected>>', self.on_item_selected)
        
        # 4. Unit Price (Editable, defaults to item price or global)
        price_entry = add_input("سعر الوحدة", self.in_price_var, width=10)
        # price_entry.config(state='readonly') # Removed to allow editing
        
        # 5. Weight
        add_input("الوزن", self.in_weight_var, width=10)
        
        # 6. Count
        add_input("العدد", self.in_count_var, width=10)

    def create_table(self, parent):
        table_frame = tk.Frame(parent, bg=self.colors['bg'])
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(table_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg'])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_frame_id, width=e.width))
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Headers
        headers = ['اسم البائع', 'اسم النقلة', 'الصنف', 'سعر الوحدة', 'الوزن', 'العدد', 'نوع الترحيل']
        
        for i, text in enumerate(headers):
            lbl = tk.Label(
                self.scrollable_frame, 
                text=text, 
                font=('Playpen Sans Arabic', 16, 'bold'),
                bg=self.col_colors[i],
                relief=tk.RAISED,
                bd=2,
                height=2
            )
            lbl.grid(row=0, column=i, sticky='nsew', padx=1, pady=1)
            self.scrollable_frame.grid_columnconfigure(i, weight=1)
            
        self.load_data()

    def create_bottom_bar(self):
        btn_frame = tk.Frame(self.window, bg=self.colors['bg'], pady=20)
        btn_frame.pack(fill=tk.X)
        
        def create_btn(text, cmd, bg_color):
            return tk.Button(
                btn_frame,
                text=text,
                command=cmd,
                font=self.fonts['button'],
                bg=bg_color,
                fg='white',
                relief=tk.RAISED,
                bd=3,
                cursor='hand2',
                width=20,
                height=2
            )
            
        # Buttons
        # 1. Transfer In (Client)
        create_btn("ترحيل عميل", lambda: self.save_transfer('in'), self.colors['button_bg']).pack(side=tk.RIGHT, padx=20)
        
        # 2. Transfer Out (Seller)
        create_btn("ترحيل بائع", lambda: self.save_transfer('out'), '#E74C3C').pack(side=tk.RIGHT, padx=20)
        
        # 3. Items Statement
        create_btn("بيان الاصناف", self.show_summary, self.colors['text_secondary']).pack(side=tk.LEFT, padx=20)

        # 4. Delete Button
        create_btn("حذف الترحيل", self.delete_selected_transfer, self.colors['button_bg']).pack(side=tk.LEFT, padx=20)

    # --- Logic ---
    
    def update_input_price(self, *args):
        # If global price is typed, it overrides everything
        val = self.global_price_var.get()
        if val:
            self.in_price_var.set(val)
            
    def on_item_selected(self, event):
        # If global price is empty, use item price
        if not self.global_price_var.get():
            item_name = self.in_item_var.get()
            if item_name in self.meal_prices:
                self.in_price_var.set(self.meal_prices[item_name])
        
    def append_date_to_shipment(self, event=None):
        val = self.in_shipment_var.get().strip()
        if val:
            today_str = datetime.now().strftime("%Y-%m-%d")
            if today_str not in val:
                self.in_shipment_var.set(f"{val} - {today_str}")

    def save_transfer(self, t_type):
        # Validate
        seller = self.in_seller_var.get().strip()
        shipment = self.in_shipment_var.get().strip()
        item = self.in_item_var.get().strip()
        price = self.in_price_var.get().strip()
        weight = self.in_weight_var.get().strip()
        count = self.in_count_var.get().strip()
        
        if not (seller and shipment and item):
            messagebox.showwarning("تنبيه", "الرجاء إدخال البيانات الأساسية (البائع، النقلة، الصنف)")
            return
            
        try:
            price_val = float(price) if price else 0.0
            weight_val = float(weight) if weight else 0.0
            count_val = float(count) if count else 0.0
            
            # 1. Add to Agriculture Transfers
            self.db.add_agriculture_transfer(
                shipment, seller, item, price_val, weight_val, count_val, "", t_type
            )
            
            msg = ""
            if t_type == 'out': # Seller Transfer (ترحيل بائع)
                # Add to Seller's Account
                seller_data = self.db.get_seller_by_name(seller)
                if seller_data:
                    seller_id = seller_data[0]
                    
                    # Calculate Amount
                    amount = 0.0
                    if weight_val > 0:
                        amount = weight_val * price_val
                    elif count_val > 0:
                        amount = count_val * price_val
                        
                    t_type_str = "خارج"
                    note = f"ترحيل زراعة ({t_type_str}) - {shipment}"
                    today_date = datetime.now().strftime("%Y-%m-%d")
                    
                    # Add Transaction
                    self.db.add_seller_transaction(
                        seller_id, 
                        amount, 
                        "متبقي", 
                        count_val, 
                        weight_val, 
                        price_val, 
                        item, 
                        today_date, 
                        "", 
                        "", 
                        note
                    )
                    msg = "تم الترحيل وإضافة المعاملة لحساب البائع"
                else:
                    msg = "تم الترحيل ولكن لم يتم العثور على حساب للبائع"
                    
            elif t_type == 'in': # Client Transfer (ترحيل عميل)
                # Add to Client's Account (Debt)
                # Calculate Amount
                amount = 0.0
                if weight_val > 0:
                    amount = weight_val * price_val
                elif count_val > 0:
                    amount = count_val * price_val
                    
                self.db.add_client_debt(seller, amount)
                msg = "تم الترحيل وإضافة المبلغ لحساب العميل"
                
            messagebox.showinfo("نجاح", msg)
            
            # Clear inputs
            self.in_seller_var.set("")
            self.in_item_var.set("")
            self.in_weight_var.set("")
            self.in_count_var.set("")
            
            self.load_data()
            
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء إدخال قيم رقمية صحيحة")

    def load_data(self):
        # Clear current rows
        for row in self.table_rows:
            for widget in row:
                widget.destroy()
        self.table_rows = []
        
        data = self.db.get_agriculture_transfers()
        # Filter logic
        search_q = self.search_var.get().lower()
        filter_item = self.filter_item_var.get()
        
        filtered_data = []
        for row in data:
            # row: id, shipment, seller, item, price, weight, count, equip, type
            shipment = str(row[1]).lower()
            seller = str(row[2]).lower()
            item_name = str(row[3])
            
            if search_q and (search_q not in shipment and search_q not in seller):
                continue
                
            if filter_item and filter_item != 'الكل' and filter_item != item_name:
                continue
            
            filtered_data.append(row)
            
        # Create Rows
        # Create Rows
        entry_style = {'font': ('Playpen Sans Arabic', 14), 'relief': tk.SUNKEN, 'bd': 1, 'justify': 'center'}
        
        # Ensure at least 15 rows
        min_rows = 15
        total_rows = max(len(filtered_data), min_rows)
        
        for i in range(total_rows):
            # Check if we have data for this row
            row_data = filtered_data[i] if i < len(filtered_data) else None
            
            vals = ["", "", "", "", "", "", ""]
            row_id = None
            
            if row_data:
                # row: id, shipment, seller, item, price, weight, count, equip, type
                t_type = "عميل" if row_data[8] == 'in' else ("بائع" if row_data[8] == 'out' else row_data[8])
                vals = [
                    row_data[2], # Seller
                    row_data[1], # Shipment
                    row_data[3], # Item
                    row_data[4], # Price
                    row_data[5], # Weight
                    row_data[6], # Count
                    t_type       # Type
                ]
                row_id = row_data[0]
            
            row_widgets = []
            for col_idx, val in enumerate(vals):
                e = tk.Entry(self.scrollable_frame, **entry_style, bg=self.col_colors[col_idx])
                e.insert(0, str(val))
                e.config(state='readonly') # Make read-only
                e.grid(row=i+1, column=col_idx, sticky='nsew', padx=1, pady=1, ipady=8)
                
                # Bind click for selection ONLY if it's a real row
                if row_id:
                    e.bind('<Button-1>', lambda event, r_id=row_id, r_idx=i: self.on_row_click(event, r_id, r_idx))
                
                row_widgets.append(e)
                
            self.table_rows.append(row_widgets)

    def on_row_click(self, event, row_id, row_index):
        self.selected_transfer_id = row_id
        
        # Reset colors for all rows
        for r_idx, row in enumerate(self.table_rows):
            for c_idx, widget in enumerate(row):
                widget.config(bg=self.col_colors[c_idx])
                
        # Highlight selected row
        if 0 <= row_index < len(self.table_rows):
            self.selected_row_widgets = self.table_rows[row_index]
            for widget in self.selected_row_widgets:
                widget.config(bg='#D5F5E3') # Light Green highlight

    def delete_selected_transfer(self):
        if not self.selected_transfer_id:
            messagebox.showwarning("تنبيه", "الرجاء تحديد ترحيل للحذف")
            return
            
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذا الترحيل؟"):
            self.db.delete_agriculture_transfer(self.selected_transfer_id)
            messagebox.showinfo("نجاح", "تم الحذف بنجاح")
            self.selected_transfer_id = None
            self.load_data()
            
    def filter_table(self, event=None):
        self.load_data()
        
    def show_summary(self):
        """عرض نافذة ملخص المبيعات بتصميم عصري"""
        summary_window = tk.Toplevel(self.window)
        summary_window.title("بيان الأصناف")
        summary_window.geometry("700x600")
        summary_window.configure(bg=self.colors['bg'])
        
        # Center
        summary_window.update_idletasks()
        x = (summary_window.winfo_screenwidth() // 2) - (350)
        y = (summary_window.winfo_screenheight() // 2) - (300)
        summary_window.geometry(f"700x600+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(summary_window, bg=self.colors['header_bg'], height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame, 
            text="بيان الأصناف والمبيعات", 
            font=self.fonts['header'], 
            bg=self.colors['header_bg'], 
            fg='white'
        ).pack(pady=20)
        
        # Main Content
        content_frame = tk.Frame(summary_window, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Table Card
        table_card = tk.Frame(content_frame, bg=self.colors['card_bg'], padx=2, pady=2)
        table_card.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scroll_y = ttk.Scrollbar(table_card)
        scroll_y.pack(side=tk.LEFT, fill=tk.Y)
        
        # Treeview
        cols = ('item', 'count', 'weight', 'total_price')
        tree = ttk.Treeview(
            table_card, 
            columns=cols, 
            show='headings', 
            yscrollcommand=scroll_y.set,
            style="Summary.Treeview"
        )
        scroll_y.config(command=tree.yview)
        
        # Headers (Right to Left: الإجمالي، العدد، الوزن، الصنف)
        tree.heading('item', text='الصنف')
        tree.heading('count', text='العدد')
        tree.heading('weight', text='الوزن')
        tree.heading('total_price', text='الإجمالي')
        
        tree.column('item', anchor='center', width=200)
        tree.column('count', anchor='center', width=100)
        tree.column('weight', anchor='center', width=100)
        tree.column('total_price', anchor='center', width=120)
        
        tree.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Styling
        style = ttk.Style()
        style.configure(
            "Summary.Treeview.Heading", 
            font=self.fonts['header'], 
            background=self.colors['header_bg'], 
            foreground='white'
        )
        style.configure(
            "Summary.Treeview", 
            font=('Arial', 12, 'bold'),
            rowheight=35,
            background='white',
            fieldbackground='white'
        )
        
        # Alternating row colors with yellow highlight for item column
        tree.tag_configure('oddrow', background='#F8F9F9')
        tree.tag_configure('evenrow', background='white')
        
        # Data
        summary_data = self.db.get_sales_summary()
        
        for idx, row in enumerate(summary_data):
            # row: item_name, total_weight, total_price
            # نحتاج أيضاً إلى العدد، سنحصل عليه من قاعدة البيانات
            item_name = row[0]
            total_weight = row[1]
            total_price = row[2]
            
            # الحصول على إجمالي العدد لهذا الصنف
            total_count = self.db.get_item_total_count(item_name)
            
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            tree.insert('', tk.END, values=(
                item_name,
                f"{total_count:.0f}" if total_count else "0",
                f"{total_weight:.0f}",
                f"{total_price:.0f}"
            ), tags=(tag,))
        
        # Highlight item column with yellow background
        style.map("Summary.Treeview", 
                  background=[('selected', self.colors['accent'])],
                  foreground=[('selected', 'white')])
        
        # Close button
        btn_frame = tk.Frame(summary_window, bg=self.colors['bg'])
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            btn_frame,
            text="إغلاق",
            command=summary_window.destroy,
            bg=self.colors['header_bg'],
            fg='white',
            font=self.fonts['button'],
            width=15,
            relief=tk.FLAT,
            cursor='hand2',
            height=2
        ).pack(pady=10)