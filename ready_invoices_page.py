import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import ColorManager
from datetime import datetime

class ReadyInvoicesPage:
    def __init__(self, parent_window, transfer_data=None, deductions=None):
        self.db = Database()
        self.color_manager = ColorManager()
        self.theme = self.color_manager.get_random_theme()
        
        self.colors = {
            'bg': '#FFB347',           # Orange background
            'header_bg': '#8B4513',    # Brown header
            'blue_bar': '#4169E1',     # Blue bar
            'button_bg': '#D2691E',    # Button color
            'white': 'white'
        }
        
        # Column colors (pastel colors)
        self.col_colors = [
            '#F5CBA7',  # Owner (Orange-ish)
            '#F9E79F',  # Count (Yellow-ish)
            '#F5B7B1',  # Weight (Pink-ish)
            '#AED6F1',  # Item (Blue-ish)
            '#A9DFBF',  # Price (Green-ish)
            '#D7BDE2',  # Net (Purple-ish)
            '#E5E7E9',  # Date (Grey-ish)
            '#F8C471'   # Equipment (Gold-ish)
        ]
        
        self.transfer_data = transfer_data  # Data from selected transfer
        self.deductions = deductions or {}  # Deductions data
        
        self.window = tk.Toplevel(parent_window)
        self.window.title("فاتورة عميل جاهزة")
        self.window.geometry("1400x700")
        self.window.configure(bg=self.colors['bg'])
        self.window.resizable(True, True)
        
        # Fonts
        self.fonts = {
            'header': ('Playpen Sans Arabic', 20, 'bold'),
            'button': ('Playpen Sans Arabic', 14, 'bold'),
            'label': ('Playpen Sans Arabic', 12, 'bold'),
            'entry': ('Arial', 12)
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- Header Frame ---
        header_frame = tk.Frame(self.window, bg=self.colors['header_bg'], height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="خلفاء الحاج محي غريب بعجر للخضروات و الفواكه",
            font=('Playpen Sans Arabic', 24, 'bold'),
            bg=self.colors['header_bg'],
            fg='white'
        )
        title_label.pack(pady=15)
        
        # Buttons Row
        buttons_frame = tk.Frame(header_frame, bg=self.colors['header_bg'])
        buttons_frame.pack(pady=10)
        
        # Buttons
        self.create_btn(buttons_frame, "معاينة فاتورة", self.preview_invoice, width=15).pack(side=tk.LEFT, padx=10)
        
        # --- Main Content Area (Single Row Display) ---
        content_frame = tk.Frame(self.window, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Table Headers
        headers = ['اسم صاحب الزراعة', 'العدد', 'الوزن', 'الصنف', 'سعر الوحدة', 'الصافي', 'التاريخ', 'العدة']
        
        headers_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        headers_frame.pack(fill=tk.X, pady=(0, 5))
        
        for i, text in enumerate(headers):
            lbl = tk.Label(
                headers_frame,
                text=text,
                font=('Playpen Sans Arabic', 14, 'bold'),
                bg=self.col_colors[i],
                fg='black',
                relief=tk.RAISED,
                bd=2,
                height=2,
                width=15
            )
            lbl.pack(side=tk.RIGHT, padx=1)
        
        # Single Data Row
        data_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        data_frame.pack(fill=tk.X)
        
        # Get data from transfer or empty
        if self.transfer_data:
            # transfer_data: (owner, count, weight, item, price, net, date, equipment)
            vals = list(self.transfer_data)
        else:
            vals = ["", "", "", "", "", "", "", ""]
        
        entry_style = {
            'font': ('Arial', 14, 'bold'),
            'relief': tk.FLAT,
            'justify': 'center',
            'bd': 1
        }
        
        self.entries = []
        for col in range(8):
            bg_color = self.col_colors[col]
            
            widget = tk.Entry(data_frame, **entry_style, bg=bg_color, fg='black', width=15)
            widget.insert(0, str(vals[col]) if vals[col] else "")
            widget.config(state='readonly')  # Read-only
            widget.pack(side=tk.RIGHT, padx=1, ipady=10)
            
            self.entries.append(widget)
        
        # Large empty space (orange area) - replaced with Summary Section
        summary_frame = tk.Frame(self.window, bg=self.colors['bg'])
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Calculate totals if data exists
        if self.transfer_data and self.deductions:
            try:
                net_amount = float(self.transfer_data[5])
                
                nolon = float(self.deductions.get('nolon', 0))
                mashal = float(self.deductions.get('mashal', 0))
                rent = float(self.deductions.get('rent', 0))
                cash = float(self.deductions.get('cash', 0))
                
                comm_str = str(self.deductions.get('commission', "0"))
                if '%' in comm_str:
                    comm_pct = float(comm_str.replace('%', '').strip())
                    commission = (net_amount * comm_pct) / 100
                    comm_display = f"{commission:.2f} ({comm_str})"
                else:
                    commission = float(comm_str)
                    comm_display = f"{commission:.2f}"
                
                total_deductions = nolon + commission + mashal + rent + cash
                final_total = net_amount - total_deductions
                
                # Display Summary
                # Frame for deductions
                deductions_frame = tk.LabelFrame(summary_frame, text="تفاصيل الخصومات", font=self.fonts['label'], bg=self.colors['bg'], fg='black', padx=10, pady=10)
                deductions_frame.pack(fill=tk.X, pady=10)
                
                deductions_data = [
                    ("نولون", nolon),
                    ("عمولة", comm_display),
                    ("مشال", mashal),
                    ("إيجار عدة", rent),
                    ("نقدية", cash),
                    ("إجمالي الخصم", total_deductions)
                ]
                
                for i, (label, value) in enumerate(deductions_data):
                    f = tk.Frame(deductions_frame, bg=self.colors['bg'])
                    f.pack(side=tk.RIGHT, expand=True, fill=tk.X)
                    
                    tk.Label(f, text=label, font=('Arial', 12, 'bold'), bg=self.colors['bg']).pack()
                    tk.Label(f, text=str(value), font=('Arial', 14), bg='white', relief=tk.SUNKEN, width=10).pack(pady=5)
                
                # Final Total
                total_frame = tk.Frame(summary_frame, bg=self.colors['bg'], pady=20)
                total_frame.pack(fill=tk.X)
                
                tk.Label(total_frame, text=f"الصافي النهائي: {final_total:.2f} جنيه", font=('Playpen Sans Arabic', 24, 'bold'), bg='#27AE60', fg='white', padx=20, pady=10, relief=tk.RAISED).pack()
                
            except ValueError:
                pass

        # --- Bottom Blue Bar ---
        bottom_bar = tk.Frame(self.window, bg=self.colors['blue_bar'], height=60)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)
        bottom_bar.pack_propagate(False)
        
        # Info in bottom bar
        info_frame = tk.Frame(bottom_bar, bg=self.colors['blue_bar'])
        info_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        if self.transfer_data:
            tk.Label(info_frame, text=f"الفاتورة جاهزة للمعاينة والطباعة", font=self.fonts['label'], bg=self.colors['blue_bar'], fg='white').pack(side=tk.LEFT, padx=10)
        else:
            tk.Label(info_frame, text="لا توجد فاتورة محددة", font=self.fonts['label'], bg=self.colors['blue_bar'], fg='white').pack(side=tk.LEFT, padx=10)
    
    def create_btn(self, parent, text, command, width=15):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=self.fonts['button'],
            bg=self.colors['button_bg'],
            fg='white',
            relief=tk.RAISED,
            bd=3,
            cursor='hand2',
            width=width,
            height=1
        )
    
    def add_invoice(self):
        """Open add invoice dialog - Redesigned"""
        dialog = tk.Toplevel(self.window)
        dialog.title("إضافة فاتورة")
        dialog.geometry("1100x450")
        
        # Colors
        bg_color = '#ECF0F1'
        header_bg = '#2C3E50'
        dialog.configure(bg=bg_color)
        
        # Center
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 550
        y = (dialog.winfo_screenheight() // 2) - 225
        dialog.geometry(f"1100x450+{x}+{y}")
        
        # === Header Section ===
        header_frame = tk.Frame(dialog, bg=header_bg, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="إضافة فاتورة جديدة",
            font=('Playpen Sans Arabic', 22, 'bold'),
            bg=header_bg,
            fg='white'
        ).pack(pady=20)
        
        # === Main Content ===
        content_frame = tk.Frame(dialog, bg=bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Input Card
        input_card = tk.Frame(content_frame, bg='white', relief=tk.RAISED, bd=2)
        input_card.pack(fill=tk.BOTH, expand=True)
        
        # Inner padding
        inner_frame = tk.Frame(input_card, bg='white')
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # --- Top Row: Owner and Date ---
        top_row = tk.Frame(inner_frame, bg='white')
        top_row.pack(fill=tk.X, pady=(0, 20))
        
        # Owner Name (Right)
        tk.Label(top_row, text="اسم صاحب الفاتورة:", font=('Arial', 12, 'bold'), bg='white').pack(side=tk.RIGHT, padx=5)
        owner_entry = tk.Entry(top_row, font=('Arial', 12), justify='center', width=30, bg='#F4F6F7')
        owner_entry.pack(side=tk.RIGHT, padx=5)
        if self.transfer_data:
            owner_entry.insert(0, self.transfer_data[0])
            
        # Date (Left)
        tk.Label(top_row, text="التاريخ:", font=('Arial', 12, 'bold'), bg='white').pack(side=tk.LEFT, padx=5)
        date_entry = tk.Entry(top_row, font=('Arial', 12), justify='center', width=15, bg='#F4F6F7')
        date_entry.pack(side=tk.LEFT, padx=5)
        date_entry.insert(0, datetime.now().strftime("%Y/%m/%d"))
        
        # --- Middle Row: Numeric Fields ---
        mid_frame = tk.Frame(inner_frame, bg='white')
        mid_frame.pack(fill=tk.X, pady=10)
        
        # Configure grid columns to have equal weight
        for i in range(5):
            mid_frame.grid_columnconfigure(i, weight=1, uniform='field')
        
        # Fields: Nolon, Commission, Mashal, Rent, Cash
        # Reversed order for display (Right to Left)
        fields_config = [
            ("نولون", "0"),
            ("العمولة", "0"),
            ("مشال", "0"),
            ("ايجار عد", "0"),
            ("نقديه", "0")
        ]
        
        invoice_entries = {}
        
        # Create fields using grid for perfect alignment
        for idx, (label_text, default_val) in enumerate(fields_config):
            # Calculate column position (right to left)
            col = 4 - idx
            
            # Container
            field_container = tk.Frame(mid_frame, bg='white', relief=tk.SOLID, bd=1)
            field_container.grid(row=0, column=col, padx=5, sticky='ew')
            
            # Label
            tk.Label(
                field_container,
                text=label_text,
                font=('Arial', 12, 'bold'),
                bg='#3498DB',
                fg='white',
                pady=5
            ).pack(fill=tk.X)
            
            # Entry
            entry = tk.Entry(
                field_container,
                font=('Arial', 14),
                justify='center',
                relief=tk.FLAT,
                bg='white'
            )
            entry.pack(fill=tk.BOTH, ipady=8, padx=2, pady=2)
            entry.insert(0, default_val)
            invoice_entries[label_text] = entry

        # Add owner and date to dictionary for easy access
        invoice_entries["اسم صاحب الفاتورة"] = owner_entry
        invoice_entries["التاريخ"] = date_entry

        # === Buttons Section ===
        buttons_frame = tk.Frame(dialog, bg=bg_color)
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        def save_invoice():
            try:
                owner_name = invoice_entries["اسم صاحب الفاتورة"].get().strip()
                nolon_str = invoice_entries["نولون"].get().strip() or "0"
                commission_str = invoice_entries["العمولة"].get().strip() or "0"
                mashal_str = invoice_entries["مشال"].get().strip() or "0"
                rent_str = invoice_entries["ايجار عد"].get().strip() or "0"
                cash_str = invoice_entries["نقديه"].get().strip() or "0"
                invoice_date = invoice_entries["التاريخ"].get().strip()
                
                if not owner_name:
                    messagebox.showwarning("تنبيه", "الرجاء إدخال اسم صاحب الفاتورة", parent=dialog)
                    return
                
                # Get net amount from transfer data
                if not self.transfer_data:
                    messagebox.showwarning("تنبيه", "لا توجد بيانات ترحيل لحساب الفاتورة", parent=dialog)
                    return
                
                # transfer_data: (owner, count, weight, item, price, net, date, equipment)
                net_amount = float(self.transfer_data[5])  # الصافي
                
                # Parse values
                nolon = float(nolon_str)
                mashal = float(mashal_str)
                rent = float(rent_str)
                cash = float(cash_str)
                
                # Calculate commission as percentage
                if '%' in commission_str:
                    commission_percent = float(commission_str.replace('%', '').strip())
                    commission = (net_amount * commission_percent) / 100
                else:
                    commission = float(commission_str)
                
                # Calculate final total
                total_deductions = nolon + commission + mashal + rent + cash
                final_total = net_amount - total_deductions
                
                # Save to database (create simple storage)
                self.db.save_client_invoice(owner_name, nolon, commission, mashal, rent, cash, invoice_date, net_amount, final_total)
                
                # Show success message
                messagebox.showinfo("نجاح", "تم حفظ الفاتورة بنجاح", parent=dialog)
                
                dialog.destroy()
                
            except ValueError as e:
                messagebox.showerror("خطأ", f"الرجاء إدخال قيم رقمية صحيحة\n{str(e)}", parent=dialog)

        btn_style = {
            'font': ('Playpen Sans Arabic', 14, 'bold'),
            'relief': tk.RAISED,
            'bd': 0,
            'cursor': 'hand2',
            'width': 15,
            'height': 1
        }
        
        tk.Button(
            buttons_frame,
            text="✓ حفظ الفاتورة",
            command=save_invoice,
            bg='#27AE60',
            fg='white',
            **btn_style
        ).pack(side=tk.RIGHT, padx=10)
        
        tk.Button(
            buttons_frame,
            text="✕ إلغاء",
            command=dialog.destroy,
            bg='#95A5A6',
            fg='white',
            **btn_style
        ).pack(side=tk.LEFT, padx=10)
        
        dialog.bind('<Return>', lambda e: save_invoice())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def print_client_invoice(self, owner_name, nolon, commission, mashal, rent, cash, invoice_date, net_amount, final_total):
        """Print client invoice using ClientInvoicePrintWindow"""
        from client_invoice_print import ClientInvoicePrintWindow
        
        # Prepare invoice data
        transactions = []
        
        # Add transfer data if available
        if self.transfer_data:
            # transfer_data: (owner, count, weight, item, price, net, date, equipment)
            item_name = str(self.transfer_data[3])  # الصنف
            weight = float(self.transfer_data[2]) if self.transfer_data[2] else 0     # الوزن
            count = float(self.transfer_data[1]) if self.transfer_data[1] else 0      # العدد
            price = float(self.transfer_data[4]) if self.transfer_data[4] else 0      # السعر
            amount = float(self.transfer_data[5]) if self.transfer_data[5] else 0     # الصافي
            
            transactions.append((item_name, weight, count, price, amount, "بضاعة"))
        
        # Add deductions as separate transactions
        if nolon > 0:
            transactions.append(("نولون", 0, 0, 0, nolon, "خصم"))
        if commission > 0:
            transactions.append(("عمولة", 0, 0, 0, commission, "خصم"))
        if mashal > 0:
            transactions.append(("مشال", 0, 0, 0, mashal, "خصم"))
        if rent > 0:
            transactions.append(("إيجار عد", 0, 0, 0, rent, "خصم"))
        if cash > 0:
            transactions.append(("نقدية", 0, 0, 0, cash, "خصم"))
        
        # Prepare invoice data for ClientInvoicePrintWindow
        invoice_data = {
            'client_name': owner_name,
            'invoice_date': invoice_date,
            'transactions': transactions,
            'total_goods': net_amount,
            'total_deductions': nolon + commission + mashal + rent + cash,
            'final_total': final_total
        }
        
        ClientInvoicePrintWindow(self.window, invoice_data)
    
    def preview_invoice(self):
        """Preview and print invoice - this is the main print button"""
        if not self.transfer_data:
            messagebox.showwarning("تنبيه", "لا توجد بيانات ترحيل لإنشاء الفاتورة")
            return
        
        # Open dialog to enter invoice details before printing
        dialog = tk.Toplevel(self.window)
        dialog.title("معاينة وطباعة الفاتورة")
        dialog.geometry("1100x450")
        
        # Colors
        bg_color = '#ECF0F1'
        header_bg = '#2C3E50'
        dialog.configure(bg=bg_color)
        
        # Center
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 550
        y = (dialog.winfo_screenheight() // 2) - 225
        dialog.geometry(f"1100x450+{x}+{y}")
        
        # === Header Section ===
        header_frame = tk.Frame(dialog, bg=header_bg, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="معاينة وطباعة الفاتورة",
            font=('Playpen Sans Arabic', 22, 'bold'),
            bg=header_bg,
            fg='white'
        ).pack(pady=20)
        
        # === Main Content ===
        content_frame = tk.Frame(dialog, bg=bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Input Card
        input_card = tk.Frame(content_frame, bg='white', relief=tk.RAISED, bd=2)
        input_card.pack(fill=tk.BOTH, expand=True)
        
        # Inner padding
        inner_frame = tk.Frame(input_card, bg='white')
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # --- Top Row: Owner and Date ---
        top_row = tk.Frame(inner_frame, bg='white')
        top_row.pack(fill=tk.X, pady=(0, 20))
        
        # Owner Name (Right)
        tk.Label(top_row, text="اسم صاحب الفاتورة:", font=('Arial', 12, 'bold'), bg='white').pack(side=tk.RIGHT, padx=5)
        owner_entry = tk.Entry(top_row, font=('Arial', 12), justify='center', width=30, bg='#F4F6F7')
        owner_entry.pack(side=tk.RIGHT, padx=5)
        owner_entry.insert(0, str(self.transfer_data[0]))
            
        # Date (Left)
        tk.Label(top_row, text="التاريخ:", font=('Arial', 12, 'bold'), bg='white').pack(side=tk.LEFT, padx=5)
        date_entry = tk.Entry(top_row, font=('Arial', 12), justify='center', width=15, bg='#F4F6F7')
        date_entry.pack(side=tk.LEFT, padx=5)
        date_entry.insert(0, datetime.now().strftime("%Y/%m/%d"))
        
        # --- Middle Row: Numeric Fields ---
        mid_frame = tk.Frame(inner_frame, bg='white')
        mid_frame.pack(fill=tk.X, pady=10)
        
        # Configure grid columns to have equal weight
        for i in range(5):
            mid_frame.grid_columnconfigure(i, weight=1, uniform='field')
        
        # Fields
        # Get defaults from self.deductions if available
        nolon_def = str(self.deductions.get('nolon', "0"))
        comm_def = str(self.deductions.get('commission', "0"))
        mashal_def = str(self.deductions.get('mashal', "0"))
        rent_def = str(self.deductions.get('rent', "0"))
        cash_def = str(self.deductions.get('cash', "0"))

        fields_config = [
            ("نولون", nolon_def),
            ("العمولة", comm_def),
            ("مشال", mashal_def),
            ("ايجار عد", rent_def),
            ("نقديه", cash_def)
        ]
        
        invoice_entries = {}
        
        # Create fields using grid for perfect alignment
        for idx, (label_text, default_val) in enumerate(fields_config):
            col = 4 - idx
            
            field_container = tk.Frame(mid_frame, bg='white', relief=tk.SOLID, bd=1)
            field_container.grid(row=0, column=col, padx=5, sticky='ew')
            
            tk.Label(
                field_container,
                text=label_text,
                font=('Arial', 12, 'bold'),
                bg='#3498DB',
                fg='white',
                pady=5
            ).pack(fill=tk.X)
            
            entry = tk.Entry(
                field_container,
                font=('Arial', 14),
                justify='center',
                relief=tk.FLAT,
                bg='white'
            )
            entry.pack(fill=tk.BOTH, ipady=8, padx=2, pady=2)
            entry.insert(0, default_val)
            invoice_entries[label_text] = entry

        invoice_entries["اسم صاحب الفاتورة"] = owner_entry
        invoice_entries["التاريخ"] = date_entry

        def print_now():
            try:
                owner_name = invoice_entries["اسم صاحب الفاتورة"].get().strip()
                nolon_str = invoice_entries["نولون"].get().strip() or "0"
                commission_str = invoice_entries["العمولة"].get().strip() or "0"
                mashal_str = invoice_entries["مشال"].get().strip() or "0"
                rent_str = invoice_entries["ايجار عد"].get().strip() or "0"
                cash_str = invoice_entries["نقديه"].get().strip() or "0"
                invoice_date = invoice_entries["التاريخ"].get().strip()
                
                if not owner_name:
                    messagebox.showwarning("تنبيه", "الرجاء إدخال اسم صاحب الفاتورة", parent=dialog)
                    return
                
                # Get net amount from transfer data
                net_amount = float(self.transfer_data[5])  # الصافي
                
                # Parse values
                nolon = float(nolon_str)
                mashal = float(mashal_str)
                rent = float(rent_str)
                cash = float(cash_str)
                
                # Calculate commission as percentage
                if '%' in commission_str:
                    commission_percent = float(commission_str.replace('%', '').strip())
                    commission = (net_amount * commission_percent) / 100
                else:
                    commission = float(commission_str)
                
                # Calculate final total
                total_deductions = nolon + commission + mashal + rent + cash
                final_total = net_amount - total_deductions
                
                dialog.destroy()
                
                # Print invoice
                self.print_client_invoice(owner_name, nolon, commission, mashal, rent, cash, invoice_date, net_amount, final_total)
                
            except ValueError as e:
                messagebox.showerror("خطأ", f"الرجاء إدخال قيم رقمية صحيحة\n{str(e)}", parent=dialog)

        # === Buttons Section ===
        buttons_frame = tk.Frame(dialog, bg=bg_color)
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        btn_style = {
            'font': ('Playpen Sans Arabic', 14, 'bold'),
            'relief': tk.RAISED,
            'bd': 0,
            'cursor': 'hand2',
            'width': 15,
            'height': 1
        }
        
        tk.Button(
            buttons_frame,
            text="📄 طباعة الفاتورة",
            command=print_now,
            bg='#3498DB',
            fg='white',
            **btn_style
        ).pack(side=tk.RIGHT, padx=10)
        
        tk.Button(
            buttons_frame,
            text="✕ إلغاء",
            command=dialog.destroy,
            bg='#95A5A6',
            fg='white',
            **btn_style
        ).pack(side=tk.LEFT, padx=10)
        
        dialog.bind('<Return>', lambda e: print_now())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def edit_invoice(self):
        """Open edit invoice dialog"""
        if not self.transfer_data:
            messagebox.showwarning("تنبيه", "لا توجد فاتورة للتعديل")
            return

        dialog = tk.Toplevel(self.window)
        dialog.title("تعديل فاتورة")
        dialog.geometry("1100x300")
        
        # Colors
        dark_blue = '#154360'
        light_blue = '#85C1E9'
        
        dialog.configure(bg=light_blue)
        
        # 1. Title Frame
        title_frame = tk.Frame(dialog, bg=dark_blue, pady=15)
        title_frame.pack(fill=tk.X)
        
        tk.Label(
            title_frame,
            text="خلفاء الحاج محي غريب بعجر للخضروات والفواكه",
            font=('Playpen Sans Arabic', 22, 'bold'),
            bg=dark_blue,
            fg='white'
        ).pack()
        
        # 2. Content Frame
        content_frame = tk.Frame(dialog, bg=light_blue)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # --- Middle Row: Numeric Fields (Right to Left) ---
        # Fields: Nolon, Commission, Mashal, Rent, Cash
        numeric_fields = [
            ("نولون", "100"),
            ("العمولة", "10%"),
            ("مشال", "10"),
            ("ايجار عد", "0"),
            ("نقديه", "0")
        ]
        
        mid_frame = tk.Frame(content_frame, bg=light_blue)
        mid_frame.pack(fill=tk.X, pady=10)
        
        self.edit_entries = {}
        
        # Clear Button (Arrow) on the far Left
        def clear_fields():
            for name, entry in self.edit_entries.items():
                if name == "العمولة":
                    entry.delete(0, tk.END)
                    entry.insert(0, "10%")
                elif name == "التاريخ":
                    entry.delete(0, tk.END)
                    entry.insert(0, datetime.now().strftime("%Y/%m/%d"))
                elif name == "اسم صاحب الفاتورة":
                    entry.delete(0, tk.END) # Or keep owner name? User said "clear data in invoice", usually means numbers.
                else:
                    entry.delete(0, tk.END)
                    entry.insert(0, "0")

        clear_btn = tk.Button(
            mid_frame,
            text="▶", # Arrow icon
            font=('Arial', 12, 'bold'),
            bg=dark_blue,
            fg='white',
            command=clear_fields,
            width=3
        )
        clear_btn.pack(side=tk.LEFT, padx=10)
        
        # Numeric Inputs (Right to Left)
        for label_text, default_val in numeric_fields:
            # Container
            col = tk.Frame(mid_frame, bg=light_blue)
            col.pack(side=tk.RIGHT, padx=5)
            
            # Label
            tk.Label(
                col,
                text=label_text,
                font=('Arial', 12, 'bold'),
                bg=dark_blue,
                fg='white',
                width=12,
                pady=5
            ).pack(fill=tk.X)
            
            # Entry
            entry = tk.Entry(
                col,
                font=('Arial', 12),
                justify='center',
                width=12
            )
            entry.pack(pady=5)
            entry.insert(0, default_val)
            self.edit_entries[label_text] = entry

        # --- Bottom Row: Date and Owner Name ---
        bottom_frame = tk.Frame(content_frame, bg=light_blue)
        bottom_frame.pack(fill=tk.X, pady=20)
        
        # Owner Name (Right)
        owner_frame = tk.Frame(bottom_frame, bg=light_blue)
        owner_frame.pack(side=tk.RIGHT)
        
        tk.Label(
            owner_frame,
            text="اسم صاحب الفاتورة",
            font=('Arial', 12, 'bold'),
            bg=dark_blue,
            fg='white',
            width=15,
            pady=5
        ).pack(side=tk.RIGHT)
        
        owner_entry = tk.Entry(
            owner_frame,
            font=('Arial', 12, 'bold'),
            justify='center',
            width=30
        )
        owner_entry.pack(side=tk.RIGHT, padx=5)
        if self.transfer_data:
            owner_entry.insert(0, self.transfer_data[0])
        self.edit_entries["اسم صاحب الفاتورة"] = owner_entry
        
        # Date (Left)
        date_frame = tk.Frame(bottom_frame, bg=light_blue)
        date_frame.pack(side=tk.LEFT)
        
        date_entry = tk.Entry(
            date_frame,
            font=('Arial', 12),
            justify='center',
            width=20
        )
        date_entry.pack(side=tk.LEFT, padx=5)
        date_entry.insert(0, datetime.now().strftime("%Y/%m/%d"))
        self.edit_entries["التاريخ"] = date_entry
        
        tk.Label(
            date_frame,
            text="التاريخ",
            font=('Arial', 12, 'bold'),
            bg=dark_blue,
            fg='white',
            width=10,
            pady=5
        ).pack(side=tk.LEFT)

        # === Buttons Section ===
        buttons_frame = tk.Frame(dialog, bg=light_blue)
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        def save_edited_invoice():
            try:
                owner_name = self.edit_entries["اسم صاحب الفاتورة"].get().strip()
                nolon_str = self.edit_entries["نولون"].get().strip() or "0"
                commission_str = self.edit_entries["العمولة"].get().strip() or "0"
                mashal_str = self.edit_entries["مشال"].get().strip() or "0"
                rent_str = self.edit_entries["ايجار عد"].get().strip() or "0"
                cash_str = self.edit_entries["نقديه"].get().strip() or "0"
                invoice_date = self.edit_entries["التاريخ"].get().strip()
                
                if not owner_name:
                    messagebox.showwarning("تنبيه", "الرجاء إدخال اسم صاحب الفاتورة", parent=dialog)
                    return
                
                # Get net amount from transfer data
                if not self.transfer_data:
                    messagebox.showwarning("تنبيه", "لا توجد بيانات ترحيل لحساب الفاتورة", parent=dialog)
                    return
                
                # transfer_data: (owner, count, weight, item, price, net, date, equipment)
                net_amount = float(self.transfer_data[5])  # الصافي
                
                # Parse values
                nolon = float(nolon_str)
                mashal = float(mashal_str)
                rent = float(rent_str)
                cash = float(cash_str)
                
                # Calculate commission as percentage relative to Net
                if '%' in commission_str:
                    commission_percent = float(commission_str.replace('%', '').strip())
                    commission = (net_amount * commission_percent) / 100
                else:
                    commission = float(commission_str)
                
                # Calculate final total
                # Sum (Noloon + Commission + Mashal + Rent + Cash) and subtract from Net
                total_deductions = nolon + commission + mashal + rent + cash
                final_total = net_amount - total_deductions
                
                # Save to database
                self.db.save_client_invoice(owner_name, nolon, commission, mashal, rent, cash, invoice_date, net_amount, final_total)
                
                # Show success message
                messagebox.showinfo("نجاح", "تم حفظ الفاتورة بنجاح", parent=dialog)
                
                dialog.destroy()
                
            except ValueError as e:
                messagebox.showerror("خطأ", f"الرجاء إدخال قيم رقمية صحيحة\n{str(e)}", parent=dialog)

        btn_style = {
            'font': ('Playpen Sans Arabic', 14, 'bold'),
            'relief': tk.RAISED,
            'bd': 0,
            'cursor': 'hand2',
            'width': 15,
            'height': 1
        }
        
        tk.Button(
            buttons_frame,
            text="✓ حفظ الفاتورة",
            command=save_edited_invoice,
            bg='#27AE60',
            fg='white',
            **btn_style
        ).pack(side=tk.RIGHT, padx=10)
        
        tk.Button(
            buttons_frame,
            text="✕ إلغاء",
            command=dialog.destroy,
            bg='#95A5A6',
            fg='white',
            **btn_style
        ).pack(side=tk.LEFT, padx=10)
