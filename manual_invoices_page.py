import tkinter as tk
from tkinter import messagebox
from database import Database
from utils import format_clean_number
from datetime import datetime

class ManualInvoicesPage:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        
        self.window = tk.Toplevel(parent)
        self.window.title("سجل فواتير العملاء المضافة")
        self.window.state('zoomed')
        self.window.configure(bg='#ECF0F1')
        
        self.rows_entries = [] # To store row widgets
        self.setup_ui()
        
        # Add initial empty rows
        for _ in range(25):
            self.add_row()
            
        # Update Scrollbox
        self.window.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def setup_ui(self):
        # --- Header Title ---
        header_frame = tk.Frame(self.window, bg='#E67E22', pady=10)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="إدخال الفواتير اليدوية (نظام الجدول)", 
                 font=('Simplified Arabic', 18, 'bold'), bg='#E67E22', fg='white').pack()

        # --- Toolbar ---
        toolbar = tk.Frame(self.window, bg='#34495E', pady=5)
        toolbar.pack(fill=tk.X)
        tk.Button(toolbar, text="حفظ الكل", command=self.save_all, bg='#27AE60', fg='white', width=15, font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, padx=10)
        tk.Button(toolbar, text="طباعة المحدد", command=self.print_selected, bg='#F39C12', fg='white', width=15, font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, padx=10)
        tk.Button(toolbar, text="+ إضافة سطر", command=self.add_one_row, bg='#3498DB', fg='white', width=15, font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, padx=10)

        # --- Footer (Totals) ---
        self.footer_frame = tk.Frame(self.window, bg='#2C3E50', pady=10)
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.setup_footer()

        # --- Main Table Area (Canvas + Scrollbar) ---
        table_container = tk.Frame(self.window)
        table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        v_scroll = tk.Scrollbar(table_container, orient=tk.VERTICAL)
        h_scroll = tk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        
        self.canvas = tk.Canvas(table_container, bg='white', 
                                yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        v_scroll.config(command=self.canvas.yview)
        h_scroll.config(command=self.canvas.xview)
        
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame inside Canvas
        self.table_frame = tk.Frame(self.canvas, bg='white')
        self.canvas.create_window((0, 0), window=self.table_frame, anchor='nw')
        self.table_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # --- Column Headers ---
        self.columns_config = [
            ("تحديد", 5), 
            ("اسم العميل", 25), 
            ("العدد", 8), 
            ("الوزن", 8),
            ("الصنف", 15), 
            ("سعر الوحدة", 10), 
            ("الصافي", 12), 
            ("التاريخ", 12),
            ("نولون", 8), 
            ("عمولة", 8), 
            ("مشال", 8), 
            ("إيجار", 8),
            ("نقدية", 8), 
            ("الصافي النهائي", 12)
        ]
        
        # Grid Headers in Reverse Order (Right to Left)
        # Select (Index 0) -> Column 13
        # ...
        # Final (Index 13) -> Column 0
        total_cols = len(self.columns_config) # 14
        
        for i, (text, width) in enumerate(self.columns_config):
            grid_col = total_cols - 1 - i
            lbl = tk.Label(self.table_frame, text=text, width=width, font=('Arial', 10, 'bold'),
                          bg='#95A5A6', fg='white', relief=tk.RAISED, bd=1, height=2)
            lbl.grid(row=0, column=grid_col, sticky='nsew', padx=1, pady=1)

    def setup_footer(self):
        # Footer Labels for Totals
        self.lbl_totals = {}
        # Changed label to 'إجمالي المصاريف' to indicate addition
        items = [('goods', 'إجمالي البضاعة'), ('expenses', 'إجمالي المصاريف'), ('final', 'الصافي النهائي')]
        
        for key, text in items:
            frame = tk.Frame(self.footer_frame, bg='#2C3E50', padx=20)
            frame.pack(side=tk.RIGHT)
            tk.Label(frame, text=text, fg='#BDC3C7', bg='#2C3E50', font=('Arial', 10)).pack()
            l = tk.Label(frame, text="0", fg='white', bg='#2C3E50', font=('Arial', 14, 'bold'))
            l.pack()
            self.lbl_totals[key] = l

    def add_row(self):
        r = len(self.rows_entries) + 1 # Row index (0 is header)
        total_cols = 14
        
        # Variables and Widgets
        checkbox_var = tk.BooleanVar()
        
        # Styles
        entry_opts = {'font': ('Arial', 10), 'relief': tk.SOLID, 'bd': 1, 'justify': 'center'}
        
        widgets = []
        
        # 0: Select (Far Right -> Col 13)
        cb = tk.Checkbutton(self.table_frame, variable=checkbox_var, bg='white', command=self.update_totals)
        cb.grid(row=r, column=13, sticky='nsew', padx=1, pady=1)
        widgets.append(cb)
        
        # 1: Owner (Col 12)
        entry_owner = tk.Entry(self.table_frame, width=25, font=('Arial', 10), relief=tk.SOLID, bd=1, justify='right', bg='#E8F8F5')
        entry_owner.grid(row=r, column=12, sticky='nsew', padx=1, pady=1)
        widgets.append(entry_owner)
        
        # 2: Count (Col 11)
        entry_count = tk.Entry(self.table_frame, width=8, **entry_opts)
        entry_count.grid(row=r, column=11, sticky='nsew', padx=1, pady=1)
        widgets.append(entry_count)
        
        # 3: Weight (Col 10)
        entry_weight = tk.Entry(self.table_frame, width=8, **entry_opts)
        entry_weight.grid(row=r, column=10, sticky='nsew', padx=1, pady=1)
        widgets.append(entry_weight)
        
        # 4: Item (Col 9)
        entry_item = tk.Entry(self.table_frame, width=15, font=('Arial', 10), relief=tk.SOLID, bd=1, justify='right')
        entry_item.grid(row=r, column=9, sticky='nsew', padx=1, pady=1)
        widgets.append(entry_item)
        
        # 5: Price (Col 8)
        entry_price = tk.Entry(self.table_frame, width=10, **entry_opts)
        entry_price.grid(row=r, column=8, sticky='nsew', padx=1, pady=1)
        widgets.append(entry_price)
        
        # 6: Net (Col 7)
        lbl_net = tk.Label(self.table_frame, text="0", font=('Arial', 10, 'bold'), bg='#D6EAF8', relief=tk.SOLID, bd=1)
        lbl_net.grid(row=r, column=7, sticky='nsew', padx=1, pady=1)
        widgets.append(lbl_net)
        
        # 7: Date (Col 6)
        entry_date = tk.Entry(self.table_frame, width=12, **entry_opts)
        entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        entry_date.grid(row=r, column=6, sticky='nsew', padx=1, pady=1)
        widgets.append(entry_date)
        
        # 8: Nolon (Col 5)
        entry_nolon = tk.Entry(self.table_frame, width=8, **entry_opts)
        entry_nolon.insert(0, "0")
        entry_nolon.grid(row=r, column=5, sticky='nsew', padx=1, pady=1)
        widgets.append(entry_nolon)
        
        # 9: Comm (Col 4)
        entry_comm = tk.Entry(self.table_frame, width=8, **entry_opts)
        entry_comm.insert(0, "0")
        entry_comm.grid(row=r, column=4, sticky='nsew', padx=1, pady=1)
        widgets.append(entry_comm)
        
        # 10: Mashal (Col 3)
        entry_mashal = tk.Entry(self.table_frame, width=8, **entry_opts)
        entry_mashal.insert(0, "0")
        entry_mashal.grid(row=r, column=3, sticky='nsew', padx=1, pady=1)
        widgets.append(entry_mashal)
        
        # 11: Rent (Col 2)
        entry_rent = tk.Entry(self.table_frame, width=8, **entry_opts)
        entry_rent.insert(0, "0")
        entry_rent.grid(row=r, column=2, sticky='nsew', padx=1, pady=1)
        widgets.append(entry_rent)
        
        # 12: Cash (Col 1)
        entry_cash = tk.Entry(self.table_frame, width=8, **entry_opts)
        entry_cash.insert(0, "0")
        entry_cash.grid(row=r, column=1, sticky='nsew', padx=1, pady=1)
        widgets.append(entry_cash)
        
        # 13: Final Total (Col 0)
        lbl_final = tk.Label(self.table_frame, text="0", font=('Arial', 10, 'bold'), bg='#ABEBC6', relief=tk.SOLID, bd=1)
        lbl_final.grid(row=r, column=0, sticky='nsew', padx=1, pady=1)
        widgets.append(lbl_final)
        
        # --- Store Row Data ---
        row_data = {
            'check': checkbox_var,
            'widgets': widgets
        }
        self.rows_entries.append(row_data)
        
        # --- Bindings for Calculation ---
        calc_indices = [2, 3, 5, 8, 9, 10, 11, 12] # Indices in widgets list (Logical order 0..13)
        for i in calc_indices:
            widgets[i].bind('<KeyRelease>', lambda e, rd=row_data: self.calculate_row(rd))

        # --- Keyboard Navigation ---
        all_entries = [w for w in widgets if isinstance(w, tk.Entry)]
        for i, entry in enumerate(all_entries):
             # Move Down
             entry.bind('<Down>', lambda e, idx=i, row_idx=r: self.focus_entry(row_idx + 1, idx))
             # Move Up
             entry.bind('<Up>', lambda e, idx=i, row_idx=r: self.focus_entry(row_idx - 1, idx))
        
        
    def add_one_row(self):
        self.add_row()
        self.window.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def focus_entry(self, target_row_idx, entry_idx):
        # target_row_idx is 1-based (Grid ROW). List index = target_row_idx - 1
        list_idx = target_row_idx - 1
        
        if 0 <= list_idx < len(self.rows_entries):
            row_data = self.rows_entries[list_idx]
            entries = [w for w in row_data['widgets'] if isinstance(w, tk.Entry)]
            if 0 <= entry_idx < len(entries):
                entries[entry_idx].focus_set()

    def calculate_row(self, row_data):
        w = row_data['widgets']
        
        try:
            # Inputs
            count = float(w[2].get() or 0)
            weight = float(w[3].get() or 0)
            price = float(w[5].get() or 0)
            
            # Net
            net = (price * weight) if weight > 0 else (price * count)
            w[6].config(text=format_clean_number(net))
            
            # Expenses (Added)
            nolon = float(w[8].get() or 0)
            mashal = float(w[10].get() or 0)
            rent = float(w[11].get() or 0)
            cash = float(w[12].get() or 0)
            
            comm_val = w[9].get()
            comm = 0
            if '%' in comm_val:
                comm = (net * float(comm_val.replace('%', ''))) / 100
            else:
                comm = float(comm_val or 0)
                
            total_expenses = nolon + comm + mashal + rent + cash
            
            # Final = Net + Expenses (Aded as requested)
            final = net + total_expenses
            
            w[13].config(text=format_clean_number(final))
            
        except ValueError:
            pass # Ignore invalid inputs while typing
            
        self.update_totals()

    def update_totals(self, *args):
        total_goods = 0
        total_expenses = 0
        
        selected_rows = [r for r in self.rows_entries if r['check'].get()]
        target_rows = selected_rows if selected_rows else self.rows_entries
        
        for r in target_rows:
            if not r['widgets'][1].get().strip():
                continue
            try:
                net = float(r['widgets'][6].cget('text').replace(',', ''))
                final = float(r['widgets'][13].cget('text').replace(',', ''))
                
                # Logic: Final = Net + Expenses -> Expenses = Final - Net
                expenses = final - net
                
                total_goods += net
                total_expenses += expenses
            except:
                pass
                
        self.lbl_totals['goods'].config(text=format_clean_number(total_goods))
        self.lbl_totals['expenses'].config(text=format_clean_number(total_expenses))
        # Display Final = Goods + Expenses
        self.lbl_totals['final'].config(text=format_clean_number(total_goods + total_expenses))

    def save_all(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        count = 0
        try:
            for r in self.rows_entries:
                w = r['widgets']
                owner = w[1].get().strip()
                if not owner: continue
                
                date = w[7].get().strip()
                if not date: date = datetime.now().strftime("%Y-%m-%d")
                
                try:
                    net = float(w[6].cget('text').replace(',', '').strip() or 0)
                except ValueError: net = 0.0
                
                try:
                    final = float(w[13].cget('text').replace(',', '').strip() or 0)
                except ValueError: final = 0.0
                
                def get_clean(idx):
                    val = w[idx].get().strip()
                    return val if val else "0"

                nolon = get_clean(8)
                comm = get_clean(9)
                mashal = get_clean(10)
                rent = get_clean(11)
                cash = get_clean(12)
                
                cursor.execute('''INSERT INTO client_invoices (owner_name, nolon, commission, mashal, rent, cash, invoice_date, net_amount, final_total)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (owner, nolon, comm, mashal, rent, cash, date, net, final))
                count += 1
            
            conn.commit()
            if count > 0:
                messagebox.showinfo("نجاح", f"تم حفظ {count} فاتورة")
            else:
                 messagebox.showwarning("تنبيه", "لا توجد بيانات لحفظها. تأكد من إدخال اسم العميل.")
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ:\n{e}\n{err}")
        finally:
            conn.close()

    def print_selected(self):
        selected = [r for r in self.rows_entries if r['check'].get()]
        if not selected:
            messagebox.showwarning("تنبيه", "يجب تحديد سطر واحد على الأقل للطباعة")
            return
            
        from client_invoice_print import ClientInvoicePrintWindow
        
        w0 = selected[0]['widgets']
        client_name = w0[1].get()
        inv_date = w0[7].get()
        
        transactions = []
        total_goods = 0
        
        agg_exp = {'nolon':0.0, 'comm':0.0, 'mashal':0.0, 'rent':0.0, 'cash':0.0}
        
        for r in selected:
            w = r['widgets']
            item = w[4].get() or "بضاعة"
            count = float(w[2].get() or 0)
            weight = float(w[3].get() or 0)
            price = float(w[5].get() or 0)
            net = float(w[6].cget('text').replace(',', '') or 0)
            
            total_goods += net
            transactions.append((item, weight, count, price, net, "بضاعة"))
            
            agg_exp['nolon'] += float(w[8].get() or 0)
            agg_exp['mashal'] += float(w[10].get() or 0)
            agg_exp['rent'] += float(w[11].get() or 0)
            agg_exp['cash'] += float(w[12].get() or 0)
            
            c_val = w[9].get()
            if '%' in c_val:
                c_amount = (net * float(c_val.replace('%', ''))) / 100
            else:
                c_amount = float(c_val or 0)
            agg_exp['comm'] += c_amount

        # Pass Expenses as Additions to transaction list
        if agg_exp['nolon'] > 0: transactions.append(("نولون", 0, 0, 0, agg_exp['nolon'], "اضافة"))
        if agg_exp['comm'] > 0: transactions.append(("عمولة", 0, 0, 0, agg_exp['comm'], "اضافة"))
        if agg_exp['mashal'] > 0: transactions.append(("مشال", 0, 0, 0, agg_exp['mashal'], "اضافة"))
        if agg_exp['rent'] > 0: transactions.append(("ايجار عدة", 0, 0, 0, agg_exp['rent'], "اضافة"))
        if agg_exp['cash'] > 0: transactions.append(("نقدية", 0, 0, 0, agg_exp['cash'], "اضافة"))
            
        total_exp_val = sum(agg_exp.values())
        
        # NOTE: Current print logic (ClientInvoicePrintWindow) likely assumes deductions are subtracted.
        # We need to ensure it processes "اضافة" correctly OR we trick it.
        # If we just pass total_deductions as a NEGATIVE number, maybe it will subtract a negative => ADD?
        # Let's try passing -total_exp_val as 'total_deductions' 
        # So Final = Net - (-Exp) = Net + Exp.
        
        print_data = {
            'client_name': client_name,
            'invoice_date': inv_date,
            'total_goods': total_goods,
            'total_deductions': -total_exp_val, # Pass as negative so subtraction becomes addition?
            'final_total': total_goods + total_exp_val,
            'transactions': transactions
        }
        
        
        print_win = ClientInvoicePrintWindow(self.window, print_data)
        # Auto-print immediately on default printer
        print_win.print_direct()
