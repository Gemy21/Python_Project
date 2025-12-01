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
        
        # Load meal prices
        self.meal_prices = {}
        self.load_meal_prices()
        
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
        
        # --- Main Content (Table) ---
        main_frame = tk.Frame(self.window, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
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
        create_btn("ترحيل عميل", lambda: self.open_transfer_window('in'), self.colors['button_bg']).pack(side=tk.RIGHT, padx=20)
        
        # 2. Transfer Out (Seller)
        create_btn("ترحيل بائع", lambda: self.open_transfer_window('out'), '#E74C3C').pack(side=tk.RIGHT, padx=20)
        
        # 3. Items Statement
        create_btn("بيان الاصناف", self.show_summary, self.colors['text_secondary']).pack(side=tk.LEFT, padx=20)

        # 4. Delete Button
        create_btn("حذف الترحيل", self.delete_selected_transfer, self.colors['button_bg']).pack(side=tk.LEFT, padx=20)

    def open_transfer_window(self, t_type):
        title = "ترحيل عميل" if t_type == 'in' else "ترحيل بائع"
        bg_color = self.colors['button_bg'] if t_type == 'in' else '#E74C3C'
        
        win = tk.Toplevel(self.window)
        win.title(title)
        win.geometry("500x600")
        win.configure(bg=self.colors['bg'])
        
        # Header
        tk.Label(win, text=title, font=self.fonts['header'], bg=self.colors['bg'], fg=bg_color).pack(pady=20)
        
        # Form Frame
        form_frame = tk.Frame(win, bg=self.colors['bg'])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=40)
        
        # Local Variables
        v_seller = tk.StringVar()
        v_shipment = tk.StringVar()
        v_item = tk.StringVar()
        v_price = tk.StringVar()
        v_weight = tk.StringVar()
        v_count = tk.StringVar()
        
        # Helper to create fields
        def add_field(label, var, is_combo=False, values=None, editable=True):
            f = tk.Frame(form_frame, bg=self.colors['bg'])
            f.pack(fill=tk.X, pady=5)
            tk.Label(f, text=label, font=self.fonts['label'], bg=self.colors['bg']).pack(side=tk.RIGHT)
            if is_combo:
                w = ttk.Combobox(f, textvariable=var, values=values, font=self.fonts['entry'], justify='center')
                if not editable:
                    w.config(state='readonly')
            else:
                w = tk.Entry(f, textvariable=var, font=self.fonts['entry'], justify='center')
                if not editable:
                    w.config(state='readonly')
            w.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            return w

        # Get names based on transfer type
        if t_type == 'in':  # Client Transfer
            # Get client names
            clients = self.db.get_all_clients_accounts()
            client_names = [c[1] for c in clients]  # c[1] is client_name
            
            # Client name selector
            seller_combo = add_field("اسم العميل", v_seller, is_combo=True, values=client_names, editable=False)
            
            # Shipment name = Client name (auto-filled, read-only)
            ship_entry = add_field("اسم النقلة", v_shipment, editable=False)
            
            # When client is selected, auto-fill shipment name
            def on_client_select(e):
                client_name = v_seller.get()
                if client_name:
                    v_shipment.set(client_name)
            seller_combo.bind('<<ComboboxSelected>>', on_client_select)
            
        else:  # Seller Transfer
            # Get seller names
            sellers = self.db.get_all_sellers_accounts()
            seller_names = [s[1] for s in sellers]  # s[1] is seller_name
            
            # Seller name selector
            add_field("اسم البائع", v_seller, is_combo=True, values=seller_names, editable=False)
            
            # Get shipment names
            shipment_names = self.db.get_unique_shipment_names()
            
            # Shipment name selector (from existing shipments)
            add_field("اسم النقلة", v_shipment, is_combo=True, values=shipment_names, editable=True)
        
        meals = self.db.get_all_meals()
        meal_names = [m[1] for m in meals]
        item_combo = add_field("الصنف", v_item, is_combo=True, values=meal_names, editable=False)
        
        # Price logic
        def on_item_select(e):
            name = v_item.get()
            # Check global price first
            g_price = self.global_price_var.get()
            if g_price:
                v_price.set(g_price)
            elif name in self.meal_prices:
                v_price.set(self.meal_prices[name])
        item_combo.bind('<<ComboboxSelected>>', on_item_select)
        
        add_field("سعر الوحدة", v_price)
        add_field("الوزن", v_weight)
        add_field("العدد", v_count)
        
        # Save Button
        def save():
            seller = v_seller.get().strip()
            shipment = v_shipment.get().strip()
            item = v_item.get().strip()
            price = v_price.get().strip()
            weight = v_weight.get().strip()
            count = v_count.get().strip()
            
            if not (seller and shipment and item):
                messagebox.showwarning("تنبيه", "الرجاء إدخال البيانات الأساسية", parent=win)
                return
                
            try:
                price_val = float(price) if price else 0.0
                weight_val = float(weight) if weight else 0.0
                count_val = float(count) if count else 0.0
                
                # Add to Agriculture Transfers
                self.db.add_agriculture_transfer(
                    shipment, seller, item, price_val, weight_val, count_val, "", t_type
                )
                
                msg = ""
                if t_type == 'out': # Seller
                    seller_data = self.db.get_seller_by_name(seller)
                    if seller_data:
                        seller_id = seller_data[0]
                        amount = 0.0
                        if weight_val > 0: amount = weight_val * price_val
                        elif count_val > 0: amount = count_val * price_val
                            
                        note = f"ترحيل زراعة (خارج) - {shipment}"
                        today_date = datetime.now().strftime("%Y-%m-%d")
                        
                        self.db.add_seller_transaction(
                            seller_id, amount, "متبقي", count_val, weight_val, price_val, 
                            item, today_date, "", "", note
                        )
                        msg = "تم الترحيل وإضافة المعاملة لحساب البائع"
                    else:
                        msg = "تم الترحيل ولكن لم يتم العثور على حساب للبائع"
                        
                elif t_type == 'in': # Client
                    amount = 0.0
                    if weight_val > 0: amount = weight_val * price_val
                    elif count_val > 0: amount = count_val * price_val
                        
                    self.db.add_client_debt(seller, amount)
                    msg = "تم الترحيل وإضافة المبلغ لحساب العميل"
                    
                messagebox.showinfo("نجاح", msg, parent=win)
                win.destroy()
                self.load_data()
                
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال قيم رقمية صحيحة", parent=win)

        tk.Button(win, text="حفظ الترحيل", command=save, font=self.fonts['button'], bg=bg_color, fg='white', width=20).pack(pady=20)

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
            item_name = row[0]
            total_weight = row[1]
            total_price = row[2]
            
            total_count = 0 # Placeholder
            
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