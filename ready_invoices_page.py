import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import ColorManager
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
        
        # === Header Section ===
        header_frame = tk.Frame(self.scrollable_frame, bg='#2C3E50', pady=20)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="فاتورة عميل", 
                font=('Simplified Arabic', 24, 'bold'), fg='white', bg='#2C3E50').pack()
        
        tk.Label(header_frame, text="خلفاء الحاج محي غريب بعجر", 
                font=('Simplified Arabic', 18, 'bold'), fg='white', bg='#2C3E50').pack()
        
        # === Info Section (Client & Date) - Editable ===
        info_frame = tk.Frame(self.scrollable_frame, bg='white', pady=20)
        info_frame.pack(fill=tk.X, padx=50)
        
        # Date (Left)
        date_frame = tk.Frame(info_frame, bg='white')
        date_frame.pack(side=tk.LEFT)
        tk.Label(date_frame, text="التاريخ:", font=('Arial', 14, 'bold'), bg='white').pack(side=tk.LEFT)
        self.date_entry = tk.Entry(date_frame, font=('Arial', 14), justify='center', width=15, bg='#F4F6F7', relief=tk.SOLID, bd=1)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y/%m/%d"))
        
        # Client (Right)
        client_frame = tk.Frame(info_frame, bg='white')
        client_frame.pack(side=tk.RIGHT)
        tk.Label(client_frame, text="العميل:", font=('Arial', 14, 'bold'), bg='white').pack(side=tk.RIGHT)
        self.client_entry = tk.Entry(client_frame, font=('Arial', 14), justify='center', width=30, bg='#F4F6F7', relief=tk.SOLID, bd=1)
        self.client_entry.pack(side=tk.RIGHT, padx=5)
        
        # Set Client Name
        client_name_val = ""
        if self.is_multi and self.transfer_data:
            client_name_val = self.transfer_data[0][1]
        elif self.transfer_data:
            client_name_val = str(self.transfer_data[0])
        self.client_entry.insert(0, client_name_val)
        
        # === Transactions Table ===
        table_frame = tk.Frame(self.scrollable_frame, bg='white', pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=50)
        
        # Headers
        headers = ['الصنف', 'السعر', 'الوزن', 'العدد', 'المبلغ']
        header_bg = '#34495E'
        
        for i, header in enumerate(headers):
            lbl = tk.Label(
                table_frame,
                text=header,
                font=('Simplified Arabic', 14, 'bold'),
                bg=header_bg,
                fg='white',
                relief=tk.RAISED,
                bd=1,
                pady=10
            )
            lbl.grid(row=0, column=i, sticky='nsew', padx=1, pady=1)
            table_frame.grid_columnconfigure(i, weight=1)
            
        # Process Data
        self.total_net_amount = 0
        self.processed_transactions = []
        
        if self.transfer_data:
            data_list = self.transfer_data if self.is_multi else [self.transfer_data]
            
            for idx, item_data in enumerate(data_list):
                if self.is_multi:
                    # item_data: (id, shipment_name, seller_name, item_name, unit_price, weight, count, equipment, transfer_type)
                    t_id = item_data[0]
                    item = item_data[3]
                    price = item_data[4] or 0
                    weight = item_data[5] or 0
                    count = item_data[6] or 0
                    
                    net = 0
                    if weight > 0: net = weight * price
                    elif count > 0: net = count * price
                    
                    self.total_net_amount += net
                    
                    self.processed_transactions.append({
                        'id': t_id, 'item': item, 'weight': weight, 'count': count, 'price': price, 'amount': net, 'type': 'بضاعة'
                    })
                else:
                    # Legacy
                    vals = list(item_data)
                    try:
                        net = float(vals[5])
                        self.total_net_amount += net
                        self.processed_transactions.append({
                            'id': None, 'item': vals[3], 'weight': float(vals[2]) or 0, 'count': float(vals[1]) or 0, 'price': float(vals[4]) or 0, 'amount': net, 'type': 'بضاعة'
                        })
                    except: pass
        
        # Display Rows
        for idx, trans in enumerate(self.processed_transactions, start=1):
            row_bg = '#D6EAF8' if idx % 2 == 0 else '#EBF5FB'
            
            vals = [
                trans['item'],
                f"{trans['price']:.2f}",
                f"{trans['weight']:.2f}",
                f"{trans['count']:.0f}",
                f"{trans['amount']:.2f}"
            ]
            
            for col, val in enumerate(vals):
                lbl = tk.Label(
                    table_frame,
                    text=val,
                    font=('Arial', 12),
                    bg=row_bg,
                    relief=tk.SOLID,
                    bd=1,
                    pady=8
                )
                lbl.grid(row=idx, column=col, sticky='nsew', padx=1, pady=1)
                
        # === Deductions Section (Editable) ===
        deductions_frame = tk.LabelFrame(self.scrollable_frame, text="الخصومات والإضافات", font=('Simplified Arabic', 16, 'bold'), bg='white', padx=20, pady=20)
        deductions_frame.pack(fill=tk.X, padx=50, pady=20)
        
        # Grid for deductions
        # Fields: Nolon, Commission, Mashal, Rent, Cash
        fields_config = [
            ("نولون", "nolon"),
            ("العمولة", "commission"),
            ("مشال", "mashal"),
            ("إيجار عدة", "rent"),
            ("نقدية", "cash")
        ]
        
        self.deduction_entries = {}
        
        for i, (label_text, key) in enumerate(fields_config):
            # Frame for each field
            f = tk.Frame(deductions_frame, bg='white')
            f.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=10)
            
            tk.Label(f, text=label_text, font=('Arial', 12, 'bold'), bg='#3498DB', fg='white').pack(fill=tk.X)
            
            entry = tk.Entry(f, font=('Arial', 14), justify='center', relief=tk.SOLID, bd=1, bg='#FDEDEC')
            entry.pack(fill=tk.X, pady=5, ipady=5)
            
            # Set default value
            default_val = self.deductions.get(key, "0")
            if key == "commission" and default_val == "0": default_val = "10%" # Default commission
            
            entry.insert(0, str(default_val))
            
            # Bind to update totals
            entry.bind('<KeyRelease>', self.update_totals)
            
            self.deduction_entries[key] = entry

        # === Totals Section ===
        totals_frame = tk.Frame(self.scrollable_frame, bg='#F4F6F7', relief=tk.SOLID, bd=2, pady=15)
        totals_frame.pack(fill=tk.X, padx=50, pady=10)
        
        def add_total_row(label, var_name, color):
            row = tk.Frame(totals_frame, bg=totals_frame['bg'])
            row.pack(fill=tk.X, pady=5, padx=20)
            
            val_lbl = tk.Label(row, text="0.00", font=('Arial', 16, 'bold'), bg=color, width=15, relief=tk.SOLID, bd=1)
            val_lbl.pack(side=tk.LEFT)
            setattr(self, var_name, val_lbl)
            
            tk.Label(row, text=label, font=('Simplified Arabic', 14, 'bold'), bg=totals_frame['bg']).pack(side=tk.LEFT, padx=10)
            
        add_total_row("إجمالي البضاعة:", "lbl_total_goods", '#FFF3CD')
        add_total_row("إجمالي الخصومات:", "lbl_total_deductions", '#F8D7DA')
        add_total_row("الصافي النهائي:", "lbl_final_total", '#D4EDDA')
        
        # Initial Calculation
        self.update_totals()
        
        # === Action Buttons (Fixed at Bottom of Window) ===
        btn_frame = tk.Frame(self.window, bg='#BDC3C7', pady=10)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Button(btn_frame, text="حفظ وطباعة", command=self.save_and_print, font=self.fonts['button'], bg='#E74C3C', fg='white', width=20, height=2).pack(side=tk.RIGHT, padx=20)
        tk.Button(btn_frame, text="حفظ فقط", command=self.save_only, font=self.fonts['button'], bg='#27AE60', fg='white', width=20, height=2).pack(side=tk.RIGHT, padx=10)
        tk.Button(btn_frame, text="إغلاق", command=self.window.destroy, font=self.fonts['button'], bg='#7F8C8D', fg='white', width=15, height=2).pack(side=tk.LEFT, padx=20)

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
            self.lbl_total_goods.config(text=f"{total_goods:.2f} جنيه")
            self.lbl_total_deductions.config(text=f"{total_deductions:.2f} جنيه")
            self.lbl_final_total.config(text=f"{final_total:.2f} جنيه")
            
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
