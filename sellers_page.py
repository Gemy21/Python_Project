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
        # Header with Close Button
        header_frame = tk.Frame(self.window, bg=self.colors['header_bg'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title in center
        tk.Label(header_frame, text="برنامج البائعين", font=self.fonts['header'], bg=self.colors['header_bg'], fg='white').pack(side=tk.LEFT, expand=True, pady=20)
        
        # Close button on the right
        tk.Button(
            header_frame, 
            text="إغلاق", 
            command=self.window.destroy, 
            bg=self.colors['button_bg'], 
            fg='white', 
            font=self.fonts['button'], 
            width=12, 
            height=1, 
            relief=tk.RAISED, 
            bd=2
        ).pack(side=tk.RIGHT, padx=20, pady=20)
        
        # Table Section
        table_container = tk.Frame(self.window, bg=self.colors['bg'], padx=20, pady=10)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        canvas = tk.Canvas(table_container, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_frame_id, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Table Headers (Right to Left) - Removed shipment and notes columns
        headers = ['#', 'اسم البائع', 'العدد', 'الصنف', 'الوزن', 'السعر', 'الإجمالي', 'التاريخ', 'حذف']
        header_colors = [
            self.colors['blue'],      # #
            self.colors['green'],     # اسم البائع
            self.colors['yellow'],    # العدد
            self.colors['green'],     # الصنف
            self.colors['yellow'],    # الوزن
            self.colors['yellow'],    # السعر
            self.colors['blue'],      # الإجمالي
            self.colors['yellow'],    # التاريخ
            self.colors['blue']       # حذف
        ]
        
        header_style = {
            'font': self.fonts['button'],
            'fg': 'black',
            'relief': tk.RAISED,
            'bd': 2,
            'height': 2
        }
        
        for i, (header, color) in enumerate(zip(headers, header_colors)):
            lbl = tk.Label(scrollable_frame, text=header, bg=color, **header_style)
            lbl.grid(row=0, column=i, sticky='nsew', padx=1, pady=1)
            scrollable_frame.grid_columnconfigure(i, weight=1)
        
        # Load data rows
        self.load_data(scrollable_frame, header_colors)
        
    def load_data(self, parent, colors):
        # Get data from agriculture transfers
        transfers = self.db.get_agriculture_transfers()
        
        entry_style = {
            'font': self.fonts['table'],
            'relief': tk.SUNKEN,
            'bd': 1,
            'justify': 'center'
        }
        
        # Ensure at least 15 rows
        min_rows = 15
        total_rows = max(len(transfers), min_rows)
        
        for i in range(total_rows):
            row_data = transfers[i] if i < len(transfers) else None
            row_entries = []
            
            # Row number
            num_lbl = tk.Label(parent, text=str(i+1), bg=colors[0], **entry_style)
            num_lbl.grid(row=i+1, column=0, sticky='nsew', padx=1, pady=1, ipady=5)
            
            row_id = None
            if row_data:
                # row_data: id, shipment_name, seller_name, item_name, unit_price, weight, count, equipment, type, created_at
                row_id = row_data[0]
                seller = row_data[2] or ""
                count = row_data[6] or 0
                item = row_data[3] or ""
                weight = row_data[5] or 0
                price = row_data[4] or 0
                total = weight * price if weight and price else 0
                
                # Get date from created_at (assuming it's at index 9 or we use current date)
                date = datetime.now().strftime("%Y/%m/%d")  # Default to today
                
                # Values: seller, count, item, weight, price, total, date
                values = [seller, count, item, weight, price, f"{total:.2f}", date]
            else:
                values = ["", "", "", "", "", "", ""]
            
            for col_idx, val in enumerate(values, start=1):
                e = tk.Entry(parent, **entry_style, bg=colors[col_idx])
                e.insert(0, str(val))
                e.grid(row=i+1, column=col_idx, sticky='nsew', padx=1, pady=1, ipady=5)
                row_entries.append(e)
            
            # Delete button - functional
            def make_delete_handler(transfer_id, row_idx):
                def delete_row():
                    if transfer_id:
                        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف هذا السجل؟"):
                            self.db.delete_agriculture_transfer(transfer_id)
                            # Refresh the page
                            for widget in self.window.winfo_children():
                                widget.destroy()
                            self.setup_ui()
                return delete_row
            
            del_btn = tk.Button(
                parent, 
                text="X", 
                bg='#E74C3C', 
                fg='white', 
                font=('Arial', 10, 'bold'), 
                width=3,
                command=make_delete_handler(row_id, i) if row_id else None,
                cursor='hand2' if row_id else 'arrow'
            )
            del_btn.grid(row=i+1, column=8, sticky='nsew', padx=1, pady=1)
            
            self.table_rows.append(row_entries)
