import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import ColorManager
from datetime import datetime

class SellersPage:
    def __init__(self, parent_window):
        self.db = Database()
        self.color_manager = ColorManager()
        self.theme = self.color_manager.get_random_theme()
        
        self.colors = {
            'bg': '#FFB347',           # Medium Orange
            'header_bg': '#6C3483',    # Dark Purple
            'card_bg': '#FFFFFF',      # White
            'button_bg': '#800000',    # Maroon
            'yellow': '#F1C40F',       # Yellow
            'green': '#27AE60',        # Green
            'blue': '#AED6F1',         # Light Blue
            'text_primary': '#2C3E50'
        }
        
        self.window = tk.Toplevel(parent_window)
        self.window.title("برنامج البائعين")
        self.window.geometry("1400x800")
        self.window.configure(bg=self.colors['bg'])
        self.window.resizable(True, True)
        
        self.fonts = {
            'header': ('Playpen Sans Arabic', 22, 'bold'),
            'button': ('Playpen Sans Arabic', 14, 'bold'),
            'label': ('Playpen Sans Arabic', 12, 'bold'),
            'entry': ('Arial', 13, 'bold'),
            'table': ('Arial', 12, 'bold')
        }
        
        self.selected_row_id = None
        self.table_rows = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.window, bg=self.colors['header_bg'], height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="كشف حركة البائعين (مجمع بالتاريخ)", font=self.fonts['header'], bg=self.colors['header_bg'], fg='white').pack(side=tk.LEFT, padx=20)
        
        tk.Button(header_frame, text="إغلاق", command=self.window.destroy, bg='#C0392B', fg='white', width=10, font=self.fonts['button']).pack(side=tk.RIGHT, padx=20)

        # Scrollable Container
        container = tk.Frame(self.window, bg=self.colors['bg'])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(container, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        
        self.scrollable_content = tk.Frame(canvas, bg=self.colors['bg'])
        self.scrollable_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_grouped_data()

    def load_grouped_data(self):
        # Clear existing
        for widget in self.scrollable_content.winfo_children():
            widget.destroy()
            
        # Get Data
        # Returns: (id, shipment_name, seller_name, item_name, unit_price, weight, count, equipment, transfer_type, created_at)
        transfers = self.db.get_agriculture_transfers()
        
        # Group by Date
        from collections import defaultdict
        grouped_data = defaultdict(list)
        
        for t in transfers:
            # Assuming created_at is index 9
            created_at_str = t[9]
            if created_at_str:
                # Extract date part only (YYYY-MM-DD)
                date_part = created_at_str.split(' ')[0]
            else:
                date_part = "بدون تاريخ"
            grouped_data[date_part].append(t)
            
        # Sort dates descending
        sorted_dates = sorted(grouped_data.keys(), reverse=True)
        
        for date_str in sorted_dates:
            day_frame = tk.LabelFrame(self.scrollable_content, text=f" {date_str} ", font=self.fonts['header'], 
                                     bg=self.colors['bg'], fg='#2C3E50', labelanchor='ne', padx=10, pady=10)
            day_frame.pack(fill=tk.X, pady=15, padx=5)
            
            # Headers for this day
            headers = ["البائع", "الصنف", "العدد", "الوزن", "السعر", "الإجمالي", "اسم النقلة", "تعديل", "حذف"]
            col_weights = [3, 2, 1, 1, 1, 1, 2, 1, 1]
            
            for i, h in enumerate(headers):
                bg_col = self.colors['button_bg'] if h in ["تعديل", "حذف"] else self.colors['header_bg']
                lbl = tk.Label(day_frame, text=h, font=('Arial', 12, 'bold'), bg=bg_col, fg='white', relief=tk.FLAT, pady=8)
                lbl.grid(row=0, column=i, sticky='ew', padx=1)
                day_frame.grid_columnconfigure(i, weight=col_weights[i])
                
            # Rows
            daily_transfers = grouped_data[date_str]
            for idx, row in enumerate(daily_transfers):
                # row: id(0), shipment(1), seller(2), item(3), price(4), weight(5), count(6), equip(7), type(8), date(9)
                t_id = row[0]
                seller = row[2]
                item = row[3]
                price = row[4]
                weight = row[5]
                count = row[6]
                shipment = row[1]
                total = (weight * price) if weight else (count * price)
                
                # Display Values
                display_vals = [seller, item, count, weight, price, f"{total:,.2f}", shipment]
                
                for col_i, val in enumerate(display_vals):
                    bg_color = "white" if idx % 2 == 0 else "#FDF2E9" # Alternating colors
                    lbl = tk.Label(day_frame, text=str(val), font=('Arial', 11), bg=bg_color, relief=tk.SOLID, bd=1, pady=5)
                    lbl.grid(row=idx+1, column=col_i, sticky='ew', padx=1, pady=1)
                    
                # Edit Button
                edit_btn = tk.Button(day_frame, text="تعديل", 
                                    command=lambda r=row: self.open_edit_popup(r),
                                    bg='#F39C12', fg='white', font=('Arial', 10, 'bold'), cursor='hand2')
                edit_btn.grid(row=idx+1, column=7, sticky='ew', padx=1, pady=1)
                
                # Delete Button
                del_btn = tk.Button(day_frame, text="X", 
                                   command=lambda tid=t_id: self.delete_record(tid),
                                   bg='#C0392B', fg='white', font=('Arial', 10, 'bold'), cursor='hand2')
                del_btn.grid(row=idx+1, column=8, sticky='ew', padx=1, pady=1)

    def delete_record(self, t_id):
        if messagebox.askyesno("تأكيد", "هل تريد حذف هذا السجل نهائياً؟"):
            self.db.delete_agriculture_transfer(t_id)
            self.load_grouped_data()

    def open_edit_popup(self, row_data):
        """Open popup to edit meal details"""
        # row_data: id(0), shipment(1), seller(2), item(3), price(4), weight(5), count(6), equip(7), type(8), date(9)
        t_id = row_data[0]
        
        popup = tk.Toplevel(self.window)
        popup.title("تعديل تفاصيل الوجبة")
        popup.geometry("400x450")
        popup.configure(bg=self.colors['bg'])
        
        # Center
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 200
        y = (popup.winfo_screenheight() // 2) - 225
        popup.geometry(f"400x450+{x}+{y}")
        
        font_lbl = ('Arial', 12, 'bold')
        font_ent = ('Arial', 14)
        
        # Form
        entry_vars = {}
        
        fields = [
            ("اسم الصنف", row_data[3]),
            ("السعر", row_data[4]),
            ("الوزن", row_data[5]),
            ("العدد", row_data[6]),
            ("اسم البائع", row_data[2]),
            ("اسم النقلة", row_data[1])
        ]
        
        for i, (label, val) in enumerate(fields):
            tk.Label(popup, text=label, font=font_lbl, bg=self.colors['bg']).pack(pady=(10, 0))
            var = tk.StringVar(value=str(val))
            tk.Entry(popup, textvariable=var, font=font_ent, justify='center').pack()
            entry_vars[label] = var
            
        def save():
            try:
                # Collect new values
                new_item = entry_vars["اسم الصنف"].get()
                new_price = float(entry_vars["السعر"].get())
                new_weight = float(entry_vars["الوزن"].get())
                new_count = float(entry_vars["العدد"].get())
                new_seller = entry_vars["اسم البائع"].get()
                new_shipment = entry_vars["اسم النقلة"].get()
                
                # Update DB
                # update function signature: id, shipment_name, seller_name, item_name, unit_price, weight, count, equipment, transfer_type
                # We reuse existing 'equipment' and 'transfer_type' from row_data
                existing_equip = row_data[7]
                existing_type = row_data[8]
                
                self.db.update_agriculture_transfer(t_id, new_shipment, new_seller, new_item, 
                                                  new_price, new_weight, new_count, 
                                                  existing_equip, existing_type)
                
                messagebox.showinfo("نجاح", "تم التعديل بنجاح", parent=popup)
                popup.destroy()
                self.load_grouped_data()
                
            except ValueError:
                messagebox.showerror("خطأ", "تأكد من إدخال أرقام صحيحة في السعر والوزن والعدد", parent=popup)
        
        tk.Button(popup, text="حفظ التعديلات", command=save, 
                 bg=self.colors['button_bg'], fg='white', font=self.fonts['button'], width=20).pack(pady=20)
