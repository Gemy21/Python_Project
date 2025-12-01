import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import ColorManager
from datetime import datetime

class ReadyInvoicesPage:
    def __init__(self, parent_window, transfer_data=None):
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
        self.create_btn(buttons_frame, "إضافة فاتورة", self.add_invoice, width=15).pack(side=tk.LEFT, padx=10)
        self.create_btn(buttons_frame, "معاينة فاتورة", self.preview_invoice, width=15).pack(side=tk.LEFT, padx=10)
        self.create_btn(buttons_frame, "تعديل فاتورة", self.edit_invoice, width=15).pack(side=tk.LEFT, padx=10)
        
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
        
        # Large empty space (orange area)
        empty_space = tk.Frame(self.window, bg=self.colors['bg'], height=300)
        empty_space.pack(fill=tk.BOTH, expand=True, padx=20)
        
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
        """Open add invoice dialog"""
        dialog = tk.Toplevel(self.window)
        dialog.title("اضافة فاتورة")
        dialog.geometry("1100x250")
        
        # Colors from image
        dark_blue = '#154360'  # Dark Blue for header
        light_blue = '#85C1E9' # Light Blue for background
        
        dialog.configure(bg=light_blue)
        
        # 1. Title Frame (Dark Blue)
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
        
        # Fields (Right to Left)
        fields = [
            ("اسم صاحب الفاتورة", 30),
            ("نولون", 12),
            ("العمولة", 12),
            ("مشال", 12),
            ("ايجار", 12),
            ("نقديه", 12),
            ("التاريخ", 15)
        ]
        
        self.add_invoice_entries = {}
        
        for field, width in fields:
            # Column Container
            col_frame = tk.Frame(content_frame, bg=light_blue)
            col_frame.pack(side=tk.RIGHT, padx=2, fill=tk.Y)
            
            # Header Label
            tk.Label(
                col_frame,
                text=field,
                font=('Arial', 12, 'bold'),
                bg=dark_blue,
                fg='white',
                width=width,
                pady=8
            ).pack(fill=tk.X)
            
            # Entry
            entry = tk.Entry(
                col_frame,
                font=('Arial', 12),
                justify='center',
                relief=tk.FLAT
            )
            entry.pack(fill=tk.X, pady=(5, 0), ipady=6)
            
            self.add_invoice_entries[field] = entry
            
            # Default Values
            if field == "التاريخ":
                entry.insert(0, datetime.now().strftime("%Y/%m/%d"))
            elif field == "العمولة":
                entry.insert(0, "10%")
            elif field == "اسم صاحب الفاتورة" and self.transfer_data:
                entry.insert(0, self.transfer_data[0])
            elif field != "اسم صاحب الفاتورة":
                entry.insert(0, "0")
    
    def preview_invoice(self):
        """Preview invoice for printing"""
        if not self.transfer_data:
            messagebox.showwarning("تنبيه", "لا توجد فاتورة لمعاينتها")
            return
        
        messagebox.showinfo("معاينة فاتورة", "سيتم فتح نافذة المعاينة للطباعة")
    
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
