import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import ColorManager
from datetime import datetime
from ready_invoices_page import ReadyInvoicesPage

class ClientsPage:
    def __init__(self, parent_window):
        self.db = Database()
        self.color_manager = ColorManager()
        
        # Design copied from AgricultureTransferPage
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
            '#F5CBA7', # Client (Orange-ish)
            '#F9E79F', # Seller (Yellow-ish)
            '#F5B7B1', # Item (Pink-ish)
            '#AED6F1', # Price (Blue-ish)
            '#A9DFBF', # Weight (Green-ish)
            '#D7BDE2', # Count (Purple-ish)
            '#E5E7E9'  # Total (Grey-ish)
        ]
        
        self.window = tk.Toplevel(parent_window)
        self.window.title("برنامج العملاء")
        self.window.geometry("1300x850")
        self.window.configure(bg=self.colors['bg'])
        self.window.resizable(True, True)
        
        # Fonts
        self.fonts = {
            'header': ('Playpen Sans Arabic', 20, 'bold'),
            'label': ('Playpen Sans Arabic', 14, 'bold'),
            'entry': ('Arial', 14),
            'button': ('Playpen Sans Arabic', 12, 'bold')
        }
        
        # Variables
        self.search_var = tk.StringVar()
        self.filter_item_var = tk.StringVar()
        
        self.table_rows = []
        self.selected_transfer_id = None
        self.selected_row_widgets = []
        
        self.setup_ui()
        
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

        # Right Side: Search
        search_frame = tk.Frame(controls, bg=self.colors['header_bg'])
        search_frame.pack(side=tk.RIGHT, padx=10)
        tk.Label(search_frame, text="بحث (عميل/بائع):", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.RIGHT, padx=5)
        search_entry = make_entry(search_frame, self.search_var, width=25)
        search_entry.pack(side=tk.RIGHT)
        search_entry.bind('<KeyRelease>', self.filter_table)
        
        # Middle: Filter by Item
        filter_frame = tk.Frame(controls, bg=self.colors['header_bg'])
        filter_frame.pack(side=tk.RIGHT, padx=20)
        tk.Label(filter_frame, text="تصفية بالصنف:", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.RIGHT, padx=5)
        
        meals = self.db.get_all_meals()
        meal_names = [m[1] for m in meals]
        
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_item_var, values=['الكل'] + meal_names, font=self.fonts['entry'], width=20, justify='center')
        filter_combo.pack(side=tk.RIGHT)
        filter_combo.bind('<<ComboboxSelected>>', self.filter_table)
        filter_combo.current(0)
        
        # Left: Title
        tk.Label(controls, text="إدارة حسابات وفواتير العملاء", font=self.fonts['header'], bg=self.colors['header_bg'], fg='white').pack(side=tk.LEFT, padx=20)

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
        headers = ['اسم العميل', 'اسم البائع', 'الصنف', 'سعر الوحدة', 'الوزن', 'العدد', 'الإجمالي']
        
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
        btn_frame = tk.Frame(self.window, bg=self.colors['bg'], pady=10)
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
                width=18,
                height=2
            )
            
        # Buttons
        # Right side
        # Removed "فواتير العملاء الجاهزة" button as requested
        
        # Left side
        create_btn("حسابات العملاء", self.open_client_accounts, '#E74C3C').pack(side=tk.LEFT, padx=5)
        create_btn("بيان العملاء", lambda: None, self.colors['text_secondary']).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        # Clear current rows
        for row in self.table_rows:
            for widget in row:
                widget.destroy()
        self.table_rows = []
        
        transfers = self.db.get_agriculture_transfers()
        
        # Filter logic
        search_q = self.search_var.get().lower()
        filter_item = self.filter_item_var.get()
        
        filtered_data = []
        for row in transfers:
            # row: id, shipment(client), seller, item, price, weight, count, equip, type
            if row[8] != 'in': # Only clients
                continue
                
            client = str(row[1]).lower()
            seller = str(row[2]).lower()
            item_name = str(row[3])
            
            if search_q and (search_q not in client and search_q not in seller):
                continue
                
            if filter_item and filter_item != 'الكل' and filter_item != item_name:
                continue
            
            filtered_data.append(row)
            
        # Create Rows
        entry_style = {'font': ('Playpen Sans Arabic', 14), 'relief': tk.SUNKEN, 'bd': 1, 'justify': 'center'}
        
        min_rows = 15
        total_rows = max(len(filtered_data), min_rows)
        
        for i in range(total_rows):
            row_data = filtered_data[i] if i < len(filtered_data) else None
            
            vals = ["", "", "", "", "", "", ""]
            row_id = None
            
            if row_data:
                price = row_data[4] or 0
                weight = row_data[5] or 0
                count = row_data[6] or 0
                
                total = 0
                if weight > 0: total = weight * price
                elif count > 0: total = count * price
                
                vals = [
                    row_data[1], # Client (Shipment)
                    row_data[2], # Seller
                    row_data[3], # Item
                    row_data[4], # Price
                    row_data[5], # Weight
                    row_data[6], # Count
                    f"{total:.2f}" # Total
                ]
                row_id = row_data[0]
            
            row_widgets = []
            for col_idx, val in enumerate(vals):
                e = tk.Entry(self.scrollable_frame, **entry_style, bg=self.col_colors[col_idx])
                e.insert(0, str(val))
                e.config(state='readonly')
                e.grid(row=i+1, column=col_idx, sticky='nsew', padx=1, pady=1, ipady=8)
                
                if row_id:
                    e.bind('<Button-1>', lambda event, r_id=row_id, r_idx=i: self.on_row_click(event, r_id, r_idx))
                
                row_widgets.append(e)
                
            self.table_rows.append(row_widgets)

    def on_row_click(self, event, row_id, row_index):
        self.selected_transfer_id = row_id
        
        for r_idx, row in enumerate(self.table_rows):
            for c_idx, widget in enumerate(row):
                widget.config(bg=self.col_colors[c_idx])
                
        if 0 <= row_index < len(self.table_rows):
            self.selected_row_widgets = self.table_rows[row_index]
            for widget in self.selected_row_widgets:
                widget.config(bg='#D5F5E3')

    def filter_table(self, event=None):
        self.load_data()

    def open_ready_invoices(self):
        """Open ready invoices page with selected transfer"""
        if not self.selected_transfer_id:
            # Open empty invoice page
            ReadyInvoicesPage(self.window, transfer_data=None)
            return
        
        # Get selected transfer data
        transfer_id = int(self.selected_transfer_id)
        transfers = self.db.get_agriculture_transfers()
        
        selected_transfer = None
        for t in transfers:
            if t[0] == transfer_id and t[8] == 'in':  # Only client transfers
                selected_transfer = t
                break
        
        if not selected_transfer:
            messagebox.showwarning("تنبيه", "لم يتم العثور على النقلة المحددة")
            return
        
        # Prepare data: (owner, count, weight, item, price, net, date, equipment)
        owner = selected_transfer[1]  # shipment_name (client name)
        count = selected_transfer[6]
        weight = selected_transfer[5]
        item = selected_transfer[3]
        price = selected_transfer[4]
        
        # Calculate net
        net = 0
        if weight > 0:
            net = weight * price
        elif count > 0:
            net = count * price
        
        date = ""  # Will be added later
        equipment = selected_transfer[7] if len(selected_transfer) > 7 else ""
        
        transfer_data = (owner, count, weight, item, price, f"{net:.2f}", date, equipment)
        
        # Open invoice page with data
        ReadyInvoicesPage(self.window, transfer_data=transfer_data)

    def create_invoice(self, invoice_type):
        """Create invoice from selected transfer"""
        if not self.selected_transfer_id:
            messagebox.showwarning("تنبيه", "الرجاء تحديد نقلة أولاً")
            return
        
        # Get transfer details
        transfer_id = int(self.selected_transfer_id)
        transfers = self.db.get_agriculture_transfers()
        
        selected_transfer = None
        for t in transfers:
            if t[0] == transfer_id:
                selected_transfer = t
                break
        
        if not selected_transfer:
            messagebox.showerror("خطأ", "لم يتم العثور على النقلة")
            return
        
        # Show invoice window
        invoice_title = "فاتورة عميل - " + ("مضافة" if invoice_type == 'added' else "جاهزة")
        
        win = tk.Toplevel(self.window)
        win.title(invoice_title)
        win.geometry("600x500")
        win.configure(bg=self.colors['bg'])
        
        # Header
        tk.Label(win, text=invoice_title, font=self.fonts['header'], bg=self.colors['bg']).pack(pady=20)
        
        # Invoice details
        details_frame = tk.Frame(win, bg='white', padx=20, pady=20)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Transfer details: id, shipment_name, seller_name, item_name, unit_price, weight, count, equipment, transfer_type
        client_name = selected_transfer[1]  # shipment_name (which is client name for type='in')
        seller_name = selected_transfer[2]
        item_name = selected_transfer[3]
        unit_price = selected_transfer[4]
        weight = selected_transfer[5]
        count = selected_transfer[6]
        
        # Calculate total
        total = 0
        if weight > 0:
            total = weight * unit_price
        elif count > 0:
            total = count * unit_price
        
        # Display details
        info = [
            ("اسم العميل:", client_name),
            ("البائع:", seller_name),
            ("الصنف:", item_name),
            ("سعر الوحدة:", f"{unit_price:.2f}"),
            ("الوزن:", f"{weight:.2f}"),
            ("العدد:", f"{count:.0f}"),
            ("الإجمالي:", f"{total:.2f}")
        ]
        
        for label, value in info:
            row = tk.Frame(details_frame, bg='white')
            row.pack(fill=tk.X, pady=5)
            tk.Label(row, text=label, font=self.fonts['label'], bg='white', anchor='e', width=15).pack(side=tk.RIGHT, padx=10)
            tk.Label(row, text=str(value), font=self.fonts['entry'], bg='#F8F9F9', relief=tk.SOLID, bd=1, anchor='center').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, ipady=5)
        
        # Buttons
        btn_frame = tk.Frame(win, bg=self.colors['bg'])
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="طباعة", font=self.fonts['button'], bg='#27AE60', fg='white', width=15).pack(side=tk.RIGHT, padx=10)
        tk.Button(btn_frame, text="إغلاق", command=win.destroy, font=self.fonts['button'], bg='#C0392B', fg='white', width=15).pack(side=tk.LEFT, padx=10)

    def open_client_accounts(self):
        window = tk.Toplevel(self.window)
        window.title("حسابات العملاء")
        window.geometry("600x500")
        window.configure(bg=self.colors['bg'])
        
        # Title
        tk.Label(window, text="إدارة حسابات العملاء", font=self.fonts['header'], bg=self.colors['bg']).pack(pady=10)
        
        # Input Frame
        input_frame = tk.Frame(window, bg=self.colors['bg'])
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="اسم العميل:", font=self.fonts['label'], bg=self.colors['bg']).pack(side=tk.RIGHT, padx=5)
        entry_name = tk.Entry(input_frame, font=self.fonts['entry'], width=30, justify='right')
        entry_name.pack(side=tk.RIGHT, padx=5)
        
        # List Frame
        list_frame = tk.Frame(window, bg=self.colors['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview for clients
        cols = ('name', 'balance')
        tree = ttk.Treeview(list_frame, columns=cols, show='headings', height=10)
        tree.heading('name', text='اسم العميل')
        tree.heading('balance', text='الرصيد')
        tree.column('name', anchor='center', width=200)
        tree.column('balance', anchor='center', width=100)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        def load_clients():
            for item in tree.get_children():
                tree.delete(item)
            clients = self.db.get_all_clients_accounts()
            for client in clients:
                # client: id, name, balance, phone
                tree.insert('', tk.END, values=(client[1], client[2]), iid=client[0])
                
        def add_client():
            name = entry_name.get().strip()
            if name:
                if self.db.add_client_account(name):
                    entry_name.delete(0, tk.END)
                    load_clients()
                else:
                    messagebox.showerror("خطأ", "هذا العميل موجود بالفعل")
            else:
                messagebox.showwarning("تنبيه", "الرجاء إدخال اسم العميل")
                
        def delete_client():
            selected = tree.selection()
            if selected:
                if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذا العميل؟"):
                    client_id = selected[0]
                    self.db.delete_client_account(client_id)
                    load_clients()
            else:
                messagebox.showwarning("تنبيه", "الرجاء اختيار عميل للحذف")
        
        def open_client_transfers():
            """فتح صفحة نقلات العميل المحدد"""
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("تنبيه", "الرجاء اختيار عميل أولاً")
                return
            
            # Get selected client name
            client_name = tree.item(selected[0])['values'][0]
            
            # Open client transfers page
            self.open_client_transfers_page(client_name)

        # Buttons Frame
        btn_frame = tk.Frame(window, bg=self.colors['bg'])
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="حساب العميل", command=open_client_transfers, font=self.fonts['button'], bg='#3498DB', fg='white', width=15).pack(side=tk.TOP, pady=5)
        tk.Button(btn_frame, text="إضافة عميل", command=add_client, font=self.fonts['button'], bg='#27AE60', fg='white', width=15).pack(side=tk.RIGHT, padx=10)
        tk.Button(btn_frame, text="حذف عميل", command=delete_client, font=self.fonts['button'], bg='#C0392B', fg='white', width=15).pack(side=tk.LEFT, padx=10)
        
        load_clients()
    
    def open_client_transfers_page(self, client_name):
        """صفحة عرض نقلات العميل مع إمكانية إنشاء فاتورة"""
        transfers_window = tk.Toplevel(self.window)
        transfers_window.title(f"نقلات العميل: {client_name}")
        transfers_window.geometry("1200x700")
        transfers_window.configure(bg=self.colors['bg'])
        
        # Title
        title_frame = tk.Frame(transfers_window, bg=self.colors['header_bg'], height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text=f"نقلات العميل: {client_name}", font=self.fonts['header'], bg=self.colors['header_bg'], fg='white').pack(pady=15)
        
        # Table Frame
        table_frame = tk.Frame(transfers_window, bg=self.colors['bg'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas for scrolling
        canvas = tk.Canvas(table_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_frame_id, width=e.width))
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Headers
        headers = ['البائع', 'الصنف', 'سعر الوحدة', 'الوزن', 'العدد', 'العدة', 'الإجمالي']
        header_colors = ['#F5CBA7', '#F9E79F', '#F5B7B1', '#AED6F1', '#A9DFBF', '#D7BDE2', '#E5E7E9']
        
        for i, text in enumerate(headers):
            lbl = tk.Label(
                scrollable_frame, 
                text=text, 
                font=('Playpen Sans Arabic', 16, 'bold'),
                bg=header_colors[i],
                relief=tk.RAISED,
                bd=2,
                height=2
            )
            lbl.grid(row=0, column=i, sticky='nsew', padx=1, pady=1)
            scrollable_frame.grid_columnconfigure(i, weight=1)
        
        # Get client transfers
        all_transfers = self.db.get_agriculture_transfers()
        client_transfers = [t for t in all_transfers if t[1] == client_name and t[8] == 'in']
        
        # Store selected transfer
        selected_transfer = {'id': None, 'widgets': []}
        
        def on_transfer_click(transfer_id, row_widgets):
            """تحديد النقلة عند النقر عليها"""
            # Reset previous selection
            for widget in selected_transfer['widgets']:
                col_idx = widget.grid_info()['column']
                widget.config(bg=header_colors[col_idx])
            
            # Highlight selected row
            selected_transfer['id'] = transfer_id
            selected_transfer['widgets'] = row_widgets
            for widget in row_widgets:
                widget.config(bg='#D5F5E3')
        
        # Create rows
        entry_style = {'font': ('Playpen Sans Arabic', 14), 'relief': tk.SUNKEN, 'bd': 1, 'justify': 'center'}
        
        for idx, transfer in enumerate(client_transfers):
            # transfer: id, shipment, seller, item, price, weight, count, equipment, type
            price = transfer[4] or 0
            weight = transfer[5] or 0
            count = transfer[6] or 0
            equipment = transfer[7] or ""
            
            # Calculate total
            total = 0
            if weight > 0:
                total = weight * price
            elif count > 0:
                total = count * price
            
            vals = [
                transfer[2],  # Seller
                transfer[3],  # Item
                f"{price:.2f}",
                f"{weight:.2f}",
                f"{count:.0f}",
                equipment,
                f"{total:.2f}"
            ]
            
            row_widgets = []
            for col_idx, val in enumerate(vals):
                e = tk.Entry(scrollable_frame, **entry_style, bg=header_colors[col_idx])
                e.insert(0, str(val))
                e.config(state='readonly')
                e.grid(row=idx+1, column=col_idx, sticky='nsew', padx=1, pady=1, ipady=8)
                
                transfer_id = transfer[0]
                e.bind('<Button-1>', lambda event, tid=transfer_id, rw=None: on_transfer_click(tid, rw if rw else event.widget.master.grid_slaves(row=event.widget.grid_info()['row'])))
                
                row_widgets.append(e)
        
        # Bottom buttons
        btn_frame = tk.Frame(transfers_window, bg=self.colors['bg'], pady=10)
        btn_frame.pack(fill=tk.X)
        
        def create_invoice_from_transfer():
            """إنشاء فاتورة من النقلة المحددة مع إدخال الخصومات"""
            if not selected_transfer['id']:
                messagebox.showwarning("تنبيه", "الرجاء تحديد نقلة أولاً")
                return
            
            # Get transfer data
            transfer_data = None
            for t in client_transfers:
                if t[0] == selected_transfer['id']:
                    transfer_data = t
                    break
            
            if not transfer_data:
                messagebox.showerror("خطأ", "لم يتم العثور على النقلة")
                return
            
            # Open Dialog to enter deductions
            dialog = tk.Toplevel(transfers_window)
            dialog.title("بيانات الفاتورة")
            dialog.geometry("500x450")
            dialog.configure(bg=self.colors['bg'])
            
            # Center
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - 250
            y = (dialog.winfo_screenheight() // 2) - 225
            dialog.geometry(f"500x450+{x}+{y}")
            
            tk.Label(dialog, text="إدخال بيانات الفاتورة", font=('Playpen Sans Arabic', 16, 'bold'), bg=self.colors['bg']).pack(pady=15)
            
            form_frame = tk.Frame(dialog, bg=self.colors['bg'])
            form_frame.pack(pady=10, padx=20, fill=tk.X)
            
            entries = {}
            
            def create_row(label_text, key, default="0", is_percent=False):
                row = tk.Frame(form_frame, bg=self.colors['bg'])
                row.pack(fill=tk.X, pady=5)
                
                tk.Label(row, text=label_text, font=('Arial', 12, 'bold'), bg=self.colors['bg'], width=15, anchor='e').pack(side=tk.RIGHT)
                
                if is_percent:
                    # Frame for entry and % sign
                    p_frame = tk.Frame(row, bg=self.colors['bg'])
                    p_frame.pack(side=tk.RIGHT, expand=True, fill=tk.X)
                    
                    tk.Label(p_frame, text="%", font=('Arial', 12, 'bold'), bg=self.colors['bg']).pack(side=tk.LEFT, padx=5)
                    entry = tk.Entry(p_frame, font=('Arial', 12), justify='center')
                    entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
                else:
                    entry = tk.Entry(row, font=('Arial', 12), justify='center')
                    entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
                
                entry.insert(0, default)
                entries[key] = entry
            
            create_row("نولون", "nolon")
            create_row("العمولة", "commission", "10", is_percent=True)
            create_row("مشال", "mashal")
            create_row("إيجار عدة", "rent")
            create_row("نقدية", "cash")
            
            def confirm():
                # Collect data
                deductions = {}
                try:
                    deductions['nolon'] = entries['nolon'].get().strip() or "0"
                    
                    comm_val = entries['commission'].get().strip() or "0"
                    # Add % if not present, since user sees the % label
                    if '%' not in comm_val:
                        deductions['commission'] = comm_val + "%"
                    else:
                        deductions['commission'] = comm_val
                        
                    deductions['mashal'] = entries['mashal'].get().strip() or "0"
                    deductions['rent'] = entries['rent'].get().strip() or "0"
                    deductions['cash'] = entries['cash'].get().strip() or "0"
                    
                    dialog.destroy()
                    
                    # Prepare data for invoice page
                    owner = transfer_data[1]  # client name
                    count = transfer_data[6]
                    weight = transfer_data[5]
                    item = transfer_data[3]
                    price = transfer_data[4]
                    equipment = transfer_data[7] if len(transfer_data) > 7 else ""
                    
                    # Calculate net
                    net = 0
                    if weight > 0:
                        net = weight * price
                    elif count > 0:
                        net = count * price
                    
                    date = datetime.now().strftime("%Y-%m-%d")
                    
                    invoice_data = (owner, count, weight, item, price, f"{net:.2f}", date, equipment)
                    
                    # Open invoice page with deductions
                    ReadyInvoicesPage(transfers_window, transfer_data=invoice_data, deductions=deductions)
                    
                except Exception as e:
                    messagebox.showerror("خطأ", f"حدث خطأ: {e}")

            btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
            btn_frame.pack(pady=20)
            
            tk.Button(btn_frame, text="موافق", command=confirm, font=self.fonts['button'], bg='#27AE60', fg='white', width=15).pack(side=tk.RIGHT, padx=10)
            tk.Button(btn_frame, text="إلغاء", command=dialog.destroy, font=self.fonts['button'], bg='#C0392B', fg='white', width=15).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="إنشاء فاتورة", command=create_invoice_from_transfer, font=self.fonts['button'], bg='#27AE60', fg='white', width=18, height=2).pack(side=tk.RIGHT, padx=10)
        tk.Button(btn_frame, text="إغلاق", command=transfers_window.destroy, font=self.fonts['button'], bg='#C0392B', fg='white', width=18, height=2).pack(side=tk.LEFT, padx=10)
