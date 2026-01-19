import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import ColorManager, format_clean_number
from datetime import datetime

class ReadyInvoicesPage:
    def __init__(self, parent_window, transfer_data=None, deductions=None, **kwargs):
        self.db = Database()
        self.color_manager = ColorManager()
        
        self.transfer_data = transfer_data  # Data from selected transfer (or list of transfers)
        self.deductions = deductions or {}  # Deductions data
        self.is_multi = kwargs.get('is_multi', False)
        self.invoice_id = kwargs.get('invoice_id', None)
        
        self.window = tk.Toplevel(parent_window)
        self.window.title(f"فاتورة عميل {'(تعديل)' if self.invoice_id else 'جاهزة'}")
        self.window.geometry("1300x850")
        
        # Fonts
        self.fonts = {
            'header': ('Simplified Arabic', 20, 'bold'),
            'button': ('Simplified Arabic', 14, 'bold'),
            'label': ('Simplified Arabic', 12, 'bold'),
            'entry': ('Arial', 12)
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configure main window to look like a workspace
        self.window.configure(bg='#BDC3C7') # Grey background for workspace
        
        # Main Paper Container (White Page)
        # A4 aspect ratio roughly
        paper_frame = tk.Frame(self.window, bg='white', relief=tk.RAISED, bd=2)
        paper_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Canvas for scrolling the paper if needed
        canvas = tk.Canvas(paper_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(paper_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        self.scrollable_frame = tk.Frame(canvas, bg='white')
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=1250) # Fixed width
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === Header Section (Matching Image) ===
        header_frame = tk.Frame(self.scrollable_frame, bg='white', pady=10)
        header_frame.pack(fill=tk.X, padx=50)
        
        # Left Side (Phones & Names)
        left_header = tk.Frame(header_frame, bg='white')
        left_header.pack(side=tk.LEFT)
        tk.Label(left_header, text="محمد / 01014501415\nسعيد / 01009330363\nأحمد / 01002367830", 
                 font=('Arial', 12, 'bold'), bg='white', justify='right').pack()

        # Right Side (Company Name & Info)
        right_header = tk.Frame(header_frame, bg='white')
        right_header.pack(side=tk.RIGHT)
        tk.Label(right_header, text="خلفاء الحاج محي غريب بعجر\nلتجارة الخضروات والفواكه", 
                 font=('Simplified Arabic', 18, 'bold'), bg='white', justify='right').pack()
        tk.Label(right_header, text="كفر الشيخ - فوه ميدان السوق الكبير\nت / 0472976880", 
                 font=('Simplified Arabic', 12, 'bold'), bg='white', justify='right').pack()

        # Center (Logo & Large Name)
        center_header = tk.Frame(header_frame, bg='white')
        center_header.pack(side=tk.TOP, pady=5)
        # Using a text emoji or placeholder for logo
        tk.Label(center_header, text="🍎", font=('Arial', 30), bg='white').pack()
        tk.Label(center_header, text="MOHEY BAJAR", font=('Arial', 16, 'bold'), bg='white').pack()

        tk.Frame(self.scrollable_frame, height=2, bg='black').pack(fill=tk.X, padx=50)

        # === Client & Date Bar ===
        client_bar = tk.Frame(self.scrollable_frame, bg='white', pady=10)
        client_bar.pack(fill=tk.X, padx=50)
        
        # Date (Left)
        date_frame = tk.Frame(client_bar, bg='white')
        date_frame.pack(side=tk.LEFT)
        tk.Label(date_frame, text="تحريراً في :", font=('Simplified Arabic', 14, 'bold'), bg='white').pack(side=tk.LEFT)
        self.date_entry = tk.Entry(date_frame, font=('Arial', 14), justify='center', width=15, bg='#F8F9F9', relief=tk.FLAT)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y/%m/%d"))
        
        # Client (Right)
        client_frame = tk.Frame(client_bar, bg='white')
        client_frame.pack(side=tk.RIGHT)
        self.client_entry = tk.Entry(client_frame, font=('Simplified Arabic', 16, 'bold'), justify='right', width=30, bg='#F8F9F9', relief=tk.FLAT)
        self.client_entry.pack(side=tk.RIGHT, padx=5)
        tk.Label(client_frame, text="الوارد من السيد /", font=('Simplified Arabic', 14, 'bold'), bg='white').pack(side=tk.RIGHT)
        
        # Set Client Name
        client_name_val = ""
        if self.is_multi and self.transfer_data:
            client_name_val = self.transfer_data[0][1]
        elif self.transfer_data:
            client_name_val = str(self.transfer_data[0])
        self.client_entry.insert(0, client_name_val)
        
        # === Transactions Table ===
        table_frame = tk.Frame(self.scrollable_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=10)
        
        # Table Headers (Left to Right to match image layout)
        display_headers = ['الصنف', 'السعر', 'الوزن', 'العدد', 'المبلغ']
        
        for i, h in enumerate(display_headers):
            lbl = tk.Label(table_frame, text=h, font=('Simplified Arabic', 14, 'bold'), 
                          bg='white', fg='black', relief=tk.SOLID, bd=1, pady=8)
            lbl.grid(row=0, column=i, sticky='nsew')
            table_frame.grid_columnconfigure(i, weight=1 if h == 'الصنف' else 0, minsize=100)

        # Process Data - Grouping by Item and Price
        self.total_net_amount = 0
        grouped_transactions = {}
        
        if self.transfer_data:
            data_list = self.transfer_data if self.is_multi else [self.transfer_data]
            for item_data in data_list:
                if self.is_multi:
                    item = item_data[3]; price = item_data[4] or 0; weight = item_data[5] or 0; count = item_data[6] or 0
                else:
                    vals = list(item_data)
                    try: item = vals[3]; price = float(vals[4]); weight = float(vals[2]); count = float(vals[1])
                    except: continue
                
                net = (weight * price) if weight > 0 else (count * price)
                self.total_net_amount += net
                key = (item, price)
                if key in grouped_transactions:
                    grouped_transactions[key]['weight'] += weight
                    grouped_transactions[key]['count'] += count
                    grouped_transactions[key]['amount'] += net
                else:
                    grouped_transactions[key] = {'item': item, 'price': price, 'weight': weight, 'count': count, 'amount': net}

        self.processed_transactions = list(grouped_transactions.values())
        
        for idx, trans in enumerate(self.processed_transactions, start=1):
            row_data = [
                trans['item'],
                format_clean_number(trans['price']),
                format_clean_number(trans['weight']),
                format_clean_number(trans['count']),
                format_clean_number(trans['amount'])
            ]
            for col, val in enumerate(row_data):
                lbl = tk.Label(table_frame, text=val, font=('Arial', 12, 'bold'), bg='white', relief=tk.SOLID, bd=1, pady=8)
                lbl.grid(row=idx, column=col, sticky='nsew')
                
        # === Footer Section (2 Boxes side-by-side as in image) ===
        footer_container = tk.Frame(self.scrollable_frame, bg='white', pady=20)
        footer_container.pack(fill=tk.X, padx=50)

        # Right Side Box (Summary)
        summary_box = tk.Frame(footer_container, relief=tk.SOLID, bd=2, bg='white', padx=10, pady=10)
        summary_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        def add_summary_row(parent, label, var_name, font_size=18, bg='#EBF5FB'):
            row = tk.Frame(parent, bg='white')
            row.pack(fill=tk.X, pady=5)
            val_lbl = tk.Label(row, text="0", font=('Arial', font_size, 'bold'), bg=bg, relief=tk.SUNKEN, width=15)
            val_lbl.pack(side=tk.LEFT)
            setattr(self, var_name, val_lbl)
            tk.Label(row, text=label, font=('Simplified Arabic', font_size, 'bold'), bg='white').pack(side=tk.RIGHT, padx=10)

        add_summary_row(summary_box, "الاجمالي", "lbl_total_goods")
        add_summary_row(summary_box, "العمولة", "lbl_total_comm_display", bg='#FDEDEC')
        tk.Frame(summary_box, height=2, bg='black').pack(fill=tk.X, pady=10)
        add_summary_row(summary_box, "الصافي", "lbl_final_total", font_size=28, bg='#EAFAF1')

        # Left Side Box (Detailed Reductions)
        deductions_box = tk.Frame(footer_container, relief=tk.SOLID, bd=2, bg='white', padx=10, pady=10)
        deductions_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.deduction_entries = {}
        fields = [("عمولة", "commission"), ("مشال", "mashal"), ("ايجار عده", "rent"), ("نولون", "nolon"), ("نقدية", "cash")]
        
        for label, key in fields:
            row = tk.Frame(deductions_box, bg='white')
            row.pack(fill=tk.X, pady=2)
            entry = tk.Entry(row, font=('Arial', 14, 'bold'), justify='center', width=12, bg='#FDEDEC')
            entry.pack(side=tk.LEFT)
            
            # استعادة القيمة المحفوظة من النافذة السابقة
            default_val = self.deductions.get(key, "0")
            entry.insert(0, str(default_val))
            
            entry.bind('<KeyRelease>', self.update_totals)
            self.deduction_entries[key] = entry
            tk.Label(row, text=label, font=('Simplified Arabic', 14, 'bold'), bg='white', width=10, anchor='e').pack(side=tk.RIGHT, padx=5)

        # Total Deductions for left box
        tk.Frame(deductions_box, bg='black', height=1).pack(fill=tk.X, pady=5)
        row_total = tk.Frame(deductions_box, bg='#FDEDEC')
        row_total.pack(fill=tk.X, pady=5)
        self.lbl_total_deductions = tk.Label(row_total, text="0", font=('Arial', 14, 'bold'), bg='#FDEDEC')
        self.lbl_total_deductions.pack(side=tk.LEFT)
        tk.Label(row_total, text="الأجمالي", font=('Simplified Arabic', 14, 'bold'), bg='#FDEDEC').pack(side=tk.RIGHT, padx=5)
        
        # Initial Calculation
        self.update_totals()
        
        # === Action Buttons (Fixed at Bottom of Window) ===
        btn_frame = tk.Frame(self.window, bg='#2C3E50', pady=15)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Main Print Button (Does Save + Print)
        print_btn = tk.Button(
            btn_frame, 
            text="🖨️ طباعة الفاتورة والمعاينة", 
            command=self.save_and_print, 
            font=('Simplified Arabic', 16, 'bold'), 
            bg='#27AE60', 
            fg='white', 
            width=25, 
            height=2,
            cursor='hand2',
            relief=tk.RAISED,
            bd=3
        )
        print_btn.pack(side=tk.RIGHT, padx=50)
        
        # Close Button
        close_btn = tk.Button(
            btn_frame, 
            text="إغلاق", 
            command=self.window.destroy, 
            font=('Simplified Arabic', 14, 'bold'), 
            bg='#E74C3C', 
            fg='white', 
            width=15, 
            height=2,
            cursor='hand2'
        )
        close_btn.pack(side=tk.LEFT, padx=50)

    def update_totals(self, event=None):
        try:
            # Get Goods Total
            total_goods = self.total_net_amount
            
            # Calculate Deductions
            total_deductions = 0
            
            # Nolon
            try: nolon = float(self.deduction_entries['nolon'].get().strip() or 0)
            except: nolon = 0
            
            # Mashal
            try: mashal = float(self.deduction_entries['mashal'].get().strip() or 0)
            except: mashal = 0
            
            # Rent
            try: rent = float(self.deduction_entries['rent'].get().strip() or 0)
            except: rent = 0
            
            # Cash
            try: cash = float(self.deduction_entries['cash'].get().strip() or 0)
            except: cash = 0
            
            # Commission
            comm_str = self.deduction_entries['commission'].get().strip()
            if '%' in comm_str:
                try:
                    pct = float(comm_str.replace('%', '').strip())
                    commission = (total_goods * pct) / 100
                except: commission = 0
            else:
                try: commission = float(comm_str or 0)
                except: commission = 0
            
            total_deductions = nolon + commission + mashal + rent + cash
            final_total = total_goods - total_deductions
            
            # Update Labels
            self.lbl_total_goods.config(text=format_clean_number(total_goods))
            self.lbl_total_comm_display.config(text=format_clean_number(commission)) # Use 'commission' for summary box
            self.lbl_total_deductions.config(text=format_clean_number(total_deductions)) # Sum of all in left box
            self.lbl_final_total.config(text=format_clean_number(final_total))
            
            # Store values for saving
            self.current_values = {
                'nolon': nolon,
                'commission': commission, # Value not string
                'commission_str': comm_str, # String for DB
                'mashal': mashal,
                'rent': rent,
                'cash': cash,
                'total_goods': total_goods,
                'total_deductions': total_deductions,
                'final_total': final_total
            }
            
        except Exception as e:
            print(f"Error updating totals: {e}")

    def save_only(self):
        self._save_invoice(print_after=False)
        
    def save_and_print(self):
        self._save_invoice(print_after=True)
        
    def _save_invoice(self, print_after=False):
        try:
            # Validate
            owner_name = self.client_entry.get().strip()
            invoice_date = self.date_entry.get().strip()
            
            if not owner_name:
                messagebox.showwarning("تنبيه", "الرجاء إدخال اسم العميل")
                return
                
            # Get values
            vals = self.current_values
            
            # Save to DB
            if self.invoice_id:
                self.db.update_client_invoice(
                    self.invoice_id, owner_name, vals['nolon'], vals['commission_str'], 
                    vals['mashal'], vals['rent'], vals['cash'], invoice_date, 
                    vals['total_goods'], vals['final_total']
                )
                invoice_id = self.invoice_id
            else:
                invoice_id = self.db.save_client_invoice(
                    owner_name, vals['nolon'], vals['commission_str'], 
                    vals['mashal'], vals['rent'], vals['cash'], invoice_date, 
                    vals['total_goods'], vals['final_total']
                )
            
            # Link transfers
            if self.is_multi and self.transfer_data:
                transfer_ids = [str(t[0]) for t in self.transfer_data]
                self.db.link_transfers_to_invoice(invoice_id, transfer_ids)
            
            if print_after:
                self.print_invoice(owner_name, invoice_date, vals)
            else:
                messagebox.showinfo("نجاح", "تم حفظ الفاتورة بنجاح")
                self.window.destroy()
                
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {e}")

    def print_invoice(self, owner_name, invoice_date, vals):
        """Open Print Window"""
        from client_invoice_print import ClientInvoicePrintWindow
        
        transactions = []
        # Add goods
        for t in self.processed_transactions:
            transactions.append((t['item'], t['weight'], t['count'], t['price'], t['amount'], t['type']))
            
        # Add deductions
        if vals['nolon'] > 0: transactions.append(("نولون", 0, 0, 0, vals['nolon'], "خصم"))
        if vals['commission'] > 0: transactions.append(("عمولة", 0, 0, 0, vals['commission'], "خصم"))
        if vals['mashal'] > 0: transactions.append(("مشال", 0, 0, 0, vals['mashal'], "خصم"))
        if vals['rent'] > 0: transactions.append(("إيجار عدة", 0, 0, 0, vals['rent'], "خصم"))
        if vals['cash'] > 0: transactions.append(("نقدية", 0, 0, 0, vals['cash'], "خصم"))
        
        invoice_data = {
            'client_name': owner_name,
            'invoice_date': invoice_date,
            'transactions': transactions,
            'total_goods': vals['total_goods'],
            'total_deductions': vals['total_deductions'],
            'final_total': vals['final_total']
        }
        
        ClientInvoicePrintWindow(self.window, invoice_data)
