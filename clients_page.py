import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import ColorManager, format_clean_number
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
            '#E5E7E9', # Total (Grey-ish)
            '#FCF3CF', # Date (Light Yellow)
            '#D6EAF8'  # Equip (Light Blue)
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
        self.filter_date_var = tk.StringVar()
        self.filter_client_var = tk.StringVar()
        
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

        # --- Data for filters ---
        transfers = self.db.get_agriculture_transfers()
        unique_dates = set()
        unique_clients = set()
        for t in transfers:
            if t[8] == 'in': # Only client transfers
                if t[9]: unique_dates.add(t[9].split(' ')[0])
                if t[1]: unique_clients.add(t[1])
        
        sorted_dates = sorted(list(unique_dates), reverse=True)
        sorted_clients = sorted(list(unique_clients))
        
        # --- Filters (Right Side) ---
        def create_filter(parent, var, values, label_text, width=15):
            f_frame = tk.Frame(parent, bg=self.colors['header_bg'])
            f_frame.pack(side=tk.RIGHT, padx=10)
            tk.Label(f_frame, text=label_text, font=self.fonts['button'], bg=self.colors['header_bg'], fg='white').pack(side=tk.RIGHT, padx=5)
            
            full_values = ['الكل'] + values
            cb = ttk.Combobox(f_frame, textvariable=var, values=full_values, font=('Arial', 12), width=width, justify='center')
            cb.pack(side=tk.RIGHT)
            cb.current(0)
            
            def on_type(event):
                if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Return', 'Tab'): return
                
                typed = cb.get()
                if typed == '':
                    cb['values'] = full_values
                else:
                    cb['values'] = [x for x in full_values if typed.lower() in x.lower()]
                
                self.filter_table()

            cb.bind('<<ComboboxSelected>>', self.filter_table)
            cb.bind('<KeyRelease>', on_type)
            return cb

        # 1. Date Filter
        create_filter(controls, self.filter_date_var, sorted_dates, "التاريخ:")

        # 2. Client Filter (Naqla)
        create_filter(controls, self.filter_client_var, sorted_clients, "العميل (النقلة):", width=20)
        
        # 3. Item Filter
        meals = self.db.get_all_meals()
        meal_names = [m[1] for m in meals]
        create_filter(controls, self.filter_item_var, meal_names, "الصنف:")
        


        # New Buttons
        btns_frame = tk.Frame(controls, bg=self.colors['header_bg'])
        btns_frame.pack(side=tk.LEFT, padx=10)
        
        btn_font = ('Simplified Arabic', 12, 'bold')
        
        tk.Button(btns_frame, text="فواتير العملاء الجاهزة", command=self.show_ready_invoices, 
                 font=btn_font, bg='#27AE60', fg='white', relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=5)
                 
        tk.Button(btns_frame, text="فواتير العملاء المضافة", command=self.show_added_invoices, 
                 font=btn_font, bg='#E67E22', fg='white', relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=5)

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
        
        # Headers - Left to Right (so it appears Right to Left visually: Client at Right)
        headers = ['العدة', 'التاريخ', 'الإجمالي', 'سعر الوحدة', 'الوزن', 'الصنف', 'العدد', 'اسم البائع', 'اسم العميل']
        
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
        # Remaining buttons if any, or just pass if empty
        pass

    def load_data(self):
        # Clear current rows
        for row in self.table_rows:
            for widget in row:
                widget.destroy()
        self.table_rows = []
        
        transfers = self.db.get_agriculture_transfers()
        
        # Filter logic
        filter_date = self.filter_date_var.get()
        filter_client = self.filter_client_var.get()
        filter_item = self.filter_item_var.get()
        
        filtered_data = []
        for row in transfers:
            # row: id, shipment(client), seller, item, price, weight, count, equip, type
            if row[8] != 'in': # Only clients
                continue
                
            client = str(row[1])
            item_name = str(row[3])
            date_str = row[9].split(' ')[0] if row[9] else ""
            
            # Date Filter
            if filter_date and filter_date != 'الكل' and filter_date not in date_str:
                continue
            
            # Client Filter
            if filter_client and filter_client != 'الكل' and filter_client not in client:
                continue
                
            # Item Filter
            if filter_item and filter_item != 'الكل' and filter_item not in item_name:
                continue
            
            filtered_data.append(row)
            
        # Create Rows
        entry_style = {'font': ('Playpen Sans Arabic', 14), 'relief': tk.SUNKEN, 'bd': 1, 'justify': 'center'}
        
        min_rows = 15
        total_rows = max(len(filtered_data), min_rows)
        
        for i in range(total_rows):
            row_data = filtered_data[i] if i < len(filtered_data) else None
            
            vals = ["", "", "", "", "", "", "", "", ""]
            row_id = None
            
            if row_data:
                price = row_data[4] or 0
                weight = row_data[5] or 0
                count = row_data[6] or 0
                
                total = 0
                if weight > 0: total = weight * price
                elif count > 0: total = count * price
                
                # Equip, Date, Total, Price, Weight, Item, Count, Seller, Client
                date_str = row_data[9].split(' ')[0] if row_data[9] else ""
                
                vals = [
                    row_data[7] or "", # Equip
                    date_str,          # Date
                    format_clean_number(total), # Total
                    format_clean_number(row_data[4]), # Price
                    format_clean_number(row_data[5]), # Weight
                    row_data[3], # Item
                    format_clean_number(row_data[6]), # Count
                    row_data[2], # Seller
                    row_data[1]  # Client
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


    def show_ready_invoices(self):
        """إنشاء فاتورة مجمعة لكل نقلات العميل في التاريخ المحدد بناءً على الاختيار"""
        if not self.selected_transfer_id:
            messagebox.showwarning("تنبيه", "الرجاء اختيار نقلة من الجدول أولاً لتحديد العميل والتاريخ")
            return
            
        # جلب بيانات النقلة المختارة
        selected_transfer = self.db.get_transfer_by_id(self.selected_transfer_id)
        if not selected_transfer:
            messagebox.showerror("خطأ", "لم يتم العثور على النقلة")
            return
            
        # اسم النقلة المختار (الذي يحتوي على اسم العميل والتاريخ مدمجين)
        shipment_full_name = selected_transfer[1]
        
        # جلب كل نقلات العميل التي لها نفس اسم النقلة بالضبط
        all_transfers = self.db.get_agriculture_transfers()
        daily_transfers = [t for t in all_transfers if t[1] == shipment_full_name and t[8] == 'in']
        
        if not daily_transfers:
            messagebox.showinfo("تنبيه", f"لم يتم العثور على نقلات أخرى لـ {shipment_full_name}")
            return

        # فتح نافذة مراجعة النقلات المشتركة أولاً
        self.open_shared_transfers_review_window(shipment_full_name, daily_transfers)

    def open_shared_transfers_review_window(self, shipment_name, transfers):
        """نافذة مراجعة النقلات قبل إنشاء الفاتورة"""
        review_win = tk.Toplevel(self.window)
        review_win.title(f"مراجعة نقلات: {shipment_name}")
        review_win.geometry("1100x600")
        review_win.configure(bg=self.colors['bg'])

        tk.Label(review_win, text=f"نقلات: {shipment_name}", font=self.fonts['header'], bg=self.colors['bg']).pack(pady=10)

        # جدول مراجعة (يشبه الجدول الرئيسي)
        table_frame = tk.Frame(review_win, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Headers
        headers = ['البائع', 'الصنف', 'العدد', 'الوزن', 'سعر الوحدة', 'الإجمالي']
        for i, h in enumerate(headers):
            tk.Label(table_frame, text=h, font=self.fonts['label'], bg=self.colors['button_bg'], fg='white', relief=tk.RAISED, pady=5).grid(row=0, column=i, sticky='ew')
            table_frame.grid_columnconfigure(i, weight=1)

        # Data rows
        total_amount = 0
        for idx, t in enumerate(transfers):
            # transfer: id, shipment, seller, item, price, weight, count, equip, type, date
            row_bg = "white" if idx % 2 == 0 else "#FDF2E9"
            price = t[4] or 0
            weight = t[5] or 0
            count = t[6] or 0
            amount = (weight * price) if weight > 0 else (count * price)
            total_amount += amount

            vals = [t[2], t[3], format_clean_number(count), format_clean_number(weight), format_clean_number(price), format_clean_number(amount)]
            for col_i, val in enumerate(vals):
                tk.Label(table_frame, text=str(val), font=('Arial', 11), bg=row_bg, relief=tk.SOLID, bd=1, pady=5).grid(row=idx+1, column=col_i, sticky='ew')

        # Total Label
        tk.Label(review_win, text=f"إجمالي قيمة البضاعة: {format_clean_number(total_amount)} جنيه", font=self.fonts['label'], bg='#F1C40F').pack(pady=5)

        # Action Button
        def start_invoice_process():
            self.ask_for_invoice_deductions_from_review(shipment_name, transfers, review_win)

        tk.Button(review_win, text="إنشاء فاتورة مجمعة لهذه النقلات", command=start_invoice_process, 
                 font=self.fonts['button'], bg='#27AE60', fg='white', width=30, height=2).pack(pady=15)

    def ask_for_invoice_deductions_from_review(self, shipment_name, transfers, parent_win):
        """طلب الخصومات ثم فتح المعاينة"""
        dialog = tk.Toplevel(parent_win)
        dialog.title("إدخال خصومات الفاتورة")
        dialog.geometry("500x480")
        dialog.configure(bg=self.colors['bg'])
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 240
        dialog.geometry(f"500x480+{x}+{y}")

        tk.Label(dialog, text="إدخال بيانات الخصم لـ\n" + shipment_name, font=self.fonts['label'], bg=self.colors['bg']).pack(pady=15)
        
        form_frame = tk.Frame(dialog, bg=self.colors['bg'])
        form_frame.pack(pady=10, padx=20, fill=tk.X)
        
        entries = {}
        def create_row(label_text, key, default="0"):
            row = tk.Frame(form_frame, bg=self.colors['bg'])
            row.pack(fill=tk.X, pady=5)
            tk.Label(row, text=label_text, font=('Arial', 12, 'bold'), bg=self.colors['bg'], width=15, anchor='e').pack(side=tk.RIGHT)
            entry = tk.Entry(row, font=('Arial', 12), justify='center')
            entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
            entry.insert(0, default)
            entries[key] = entry

        create_row("نولون", "nolon")
        create_row("العمولة (%)", "commission", "10")
        create_row("مشال", "mashal")
        create_row("إيجار عدة", "rent")
        create_row("نقدية", "cash")
        
        def confirm():
            deductions = {
                'nolon': entries['nolon'].get().strip() or "0",
                'commission': entries['commission'].get().strip() + "%",
                'mashal': entries['mashal'].get().strip() or "0",
                'rent': entries['rent'].get().strip() or "0",
                'cash': entries['cash'].get().strip() or "0"
            }
            dialog.destroy()
            # فتح صفحة المعاينة النهائية والطباعة
            ReadyInvoicesPage(parent_win, transfer_data=transfers, deductions=deductions, is_multi=True)

        tk.Button(dialog, text="تأكيد ومعاينة الفاتورة", command=confirm, 
                 font=self.fonts['button'], bg='#27AE60', fg='white', width=20, height=2).pack(pady=20)

    def show_added_invoices(self):
        """عرض سجل الفواتير التي تم حفظها مسبقاً في جدول إكسيل مفتوح"""
        from manual_invoices_page import ManualInvoicesPage
        ManualInvoicesPage(self.window)

    def show_all_invoices_window(self, title):
        win = tk.Toplevel(self.window)
        win.title(title)
        win.geometry("1100x650")
        win.configure(bg=self.colors['bg'])
        
        tk.Label(win, text=title, font=self.fonts['header'], bg=self.colors['bg']).pack(pady=15)
        
        # List
        list_frame = tk.Frame(win, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        cols = ('inv_id', 'client', 'date', 'total', 'net', 'deductions')
        tree = ttk.Treeview(list_frame, columns=cols, show='headings', height=15)
        
        tree.heading('inv_id', text='رقم الفاتورة')
        tree.heading('client', text='العميل')
        tree.heading('date', text='التاريخ')
        tree.heading('total', text='الصافي النهائي')
        tree.heading('net', text='إجمالي البضاعة')
        tree.heading('deductions', text='الخصومات')
        
        tree.column('inv_id', width=80, anchor='center')
        tree.column('client', width=200, anchor='center')
        tree.column('date', width=120, anchor='center')
        tree.column('total', width=120, anchor='center')
        tree.column('net', width=120, anchor='center')
        tree.column('deductions', width=120, anchor='center')
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Load
        invoices = self.db.get_all_client_invoices()
        for inv in invoices:
            # id, owner_name, nolon, commission, mashal, rent, cash, invoice_date, net_amount, final_total
            inv_id = inv[0]
            client = inv[1]
            date = inv[7]
            net = inv[8] or 0
            final = inv[9] or 0
            
            # deductions calc
            nolon = inv[2] or 0
            comm_str = str(inv[3])
            commission = 0
            if '%' in comm_str:
                try:
                    pct = float(comm_str.replace('%', ''))
                    commission = (net * pct) / 100
                except: pass
            else:
                try: commission = float(comm_str)
                except: pass
            
            mashal = inv[4] or 0
            rent = inv[5] or 0
            cash = inv[6] or 0
            
            deductions = nolon + commission + mashal + rent + cash
            
            tree.insert('', tk.END, values=(inv_id, client, date, format_clean_number(final), format_clean_number(net), format_clean_number(deductions)), iid=inv_id)
            
        def open_details():
            selected = tree.selection()
            if not selected:
                 messagebox.showwarning("تنبيه", "اختر فاتورة")
                 return
            
            inv_id = int(selected[0])
            selected_inv = next((inv for inv in invoices if inv[0] == inv_id), None)
            if not selected_inv: return

            # Check if it's a manual invoice
            transfers = self.db.get_transfers_by_invoice_id(inv_id)
            is_manual = any(t[8] == 'manual' for t in transfers)
            
            if is_manual:
                from manual_invoices_page import ManualInvoicesPage
                ManualInvoicesPage(win, invoice_id=inv_id)
            else:
                deductions = {
                    'nolon': str(selected_inv[2]),
                    'commission': str(selected_inv[3]),
                    'mashal': str(selected_inv[4]),
                    'rent': str(selected_inv[5]),
                    'cash': str(selected_inv[6])
                }
                ReadyInvoicesPage(win, transfer_data=transfers, deductions=deductions, is_multi=True, invoice_id=inv_id)

        # Buttons
        btn_frame = tk.Frame(win, bg=self.colors['bg'])
        btn_frame.pack(pady=10)
        
        from manual_invoices_page import ManualInvoicesPage
        tk.Button(btn_frame, text="عرض/تعديل التفاصيل", command=open_details, 
                 font=self.fonts['button'], bg=self.colors['button_bg'], fg='white').pack(side=tk.RIGHT, padx=10)
                 
        tk.Button(btn_frame, text="فاتورة يدوية جديدة +", command=lambda: ManualInvoicesPage(win), 
                 font=self.fonts['button'], bg='#27AE60', fg='white').pack(side=tk.RIGHT, padx=10)
