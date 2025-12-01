import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import ColorManager
from datetime import datetime

class ClientsPage:
    def __init__(self, parent_window):
        self.db = Database()
        self.color_manager = ColorManager()
        self.theme = self.color_manager.get_random_theme()
        
        self.colors = {
            'bg': self.theme['light'],           # Pinkish
            'header_bg': self.theme['dark'],     # Reddish
            'card_bg': self.theme['white'],      # White
            'button_bg': self.theme['base'],     # Orange
            'text_primary': '#2C3E50',
            'text_secondary': '#7F8C8D',
            'border': self.theme['lighter']
        }
        
        self.window = tk.Toplevel(parent_window)
        self.window.title("برنامج العملاء")
        self.window.geometry("1300x800")
        self.window.configure(bg=self.colors['bg'])
        self.window.resizable(True, True)
        
        # Fonts
        self.fonts = {
            'header': ('Playpen Sans Arabic', 18, 'bold'),
            'button': ('Playpen Sans Arabic', 12, 'bold'),
            'label': ('Playpen Sans Arabic', 11, 'bold'),
            'entry': ('Arial', 12),
            'table': ('Arial', 11, 'bold')
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- Top Control Panel ---
        top_frame = tk.Frame(self.window, bg=self.colors['header_bg'], pady=10)
        top_frame.pack(fill=tk.X)
        
        # Right Side Buttons (Bills)
        right_btn_frame = tk.Frame(top_frame, bg=self.colors['header_bg'])
        right_btn_frame.pack(side=tk.RIGHT, padx=20)
        
        self.create_header_btn(right_btn_frame, "فواتير العملاء المضافة").pack(pady=5, fill=tk.X)
        self.create_header_btn(right_btn_frame, "فواتير العملاء الجاهزة").pack(pady=5, fill=tk.X)
        
        # Left Side Buttons (Accounts & Reports)
        left_btn_frame = tk.Frame(top_frame, bg=self.colors['header_bg'])
        left_btn_frame.pack(side=tk.LEFT, padx=20)
        
        row1 = tk.Frame(left_btn_frame, bg=self.colors['header_bg'])
        row1.pack(pady=2)
        self.create_header_btn(row1, "بيان العملاء", width=15).pack(side=tk.LEFT, padx=2)
        self.create_header_btn(row1, "حسابات العملاء", width=15).pack(side=tk.LEFT, padx=2)
        
        row2 = tk.Frame(left_btn_frame, bg=self.colors['header_bg'])
        row2.pack(pady=2)
        self.create_header_btn(row2, "وارد العملاء", width=15).pack(side=tk.LEFT, padx=2)
        self.create_header_btn(row2, "تقارير العملاء", width=15).pack(side=tk.LEFT, padx=2)
        
        # Center Title & Search
        center_frame = tk.Frame(top_frame, bg=self.colors['header_bg'])
        center_frame.pack(side=tk.TOP, pady=10)
        
        tk.Label(center_frame, text="إدارة حسابات وفواتير العملاء", font=('Playpen Sans Arabic', 22, 'bold'), bg=self.colors['header_bg'], fg='white').pack()
        
        # Search/Input Bar
        search_frame = tk.Frame(top_frame, bg=self.colors['header_bg'])
        search_frame.pack(side=tk.TOP, pady=10)
        
        # Shipment Input
        tk.Label(search_frame, text="النقلة:", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.RIGHT, padx=5)
        self.entry_shipment = tk.Entry(search_frame, font=self.fonts['entry'], width=20, justify='center')
        self.entry_shipment.pack(side=tk.RIGHT, padx=5)
        
        # Item Input
        tk.Label(search_frame, text="الصنف:", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.RIGHT, padx=5)
        self.entry_item = tk.Entry(search_frame, font=self.fonts['entry'], width=15, justify='center')
        self.entry_item.pack(side=tk.RIGHT, padx=5)
        
        # Edit Button
        tk.Button(search_frame, text="تعديل", bg='#C0392B', fg='white', font=self.fonts['button'], width=10).pack(side=tk.RIGHT, padx=20)

        # --- Table Section ---
        table_frame = tk.Frame(self.window, bg=self.colors['bg'], padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Columns based on image
        cols = ('shipment', 'seller', 'count', 'item', 'weight', 'price', 'total', 'date', 'notes')
        
        self.tree = ttk.Treeview(
            table_frame, 
            columns=cols, 
            show='headings', 
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            style="Clients.Treeview"
        )
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # Headings
        headers = {
            'shipment': 'اسم النقلة',
            'seller': 'البائع',
            'count': 'العدد',
            'item': 'الصنف',
            'weight': 'الوزن',
            'price': 'سعر الوحدة',
            'total': 'إجمالي',
            'date': 'التاريخ',
            'notes': 'ملاحظات'
        }
        
        for col, text in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, anchor='center', width=120)
            
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Styling
        style = ttk.Style()
        style.configure(
            "Clients.Treeview.Heading", 
            font=self.fonts['label'], 
            background=self.colors['button_bg'], 
            foreground='white',
            rowheight=40
        )
        style.configure(
            "Clients.Treeview", 
            font=self.fonts['table'],
            rowheight=35,
            fieldbackground='white'
        )
        
        # Row Colors (Tags)
        self.tree.tag_configure('yellow_row', background='#F1C40F') # Yellow
        self.tree.tag_configure('blue_row', background='#AED6F1')   # Light Blue
        self.tree.tag_configure('white_row', background='white')
        self.tree.tag_configure('orange_row', background='#F5CBA7') # Light Orange
        
        # Load Dummy Data for Visualization (matching image style)
        self.load_dummy_data()

    def create_header_btn(self, parent, text, width=25):
        return tk.Button(
            parent,
            text=text,
            font=self.fonts['button'],
            bg=self.colors['button_bg'],
            fg='white',
            relief=tk.RAISED,
            bd=2,
            width=width,
            cursor='hand2'
        )

    def load_data(self):
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Fetch from DB (Using agriculture transfers as the source of 'Wared')
        transfers = self.db.get_agriculture_transfers()
        
        for row in transfers:
            # row: id, shipment_name, seller_name, item_name, unit_price, weight, count, equipment
            # We need to format date from created_at if available, but get_agriculture_transfers currently doesn't return date
            # Let's assume we want to show these.
            
            # Calculate total
            price = row[4] or 0
            weight = row[5] or 0
            count = row[6] or 0
            
            # Total logic: usually weight * price, but if weight is 0, maybe count * price
            total = 0
            if weight > 0:
                total = weight * price
            elif count > 0:
                total = count * price
                
            # Date: currently not returned by get_agriculture_transfers, we might need to update the query in database.py
            # For now, we'll leave it empty or update database.py next.
            date_str = "" 
            
            values = (
                row[1], # shipment
                row[2], # seller
                row[6], # count
                row[3], # item
                row[5], # weight
                row[4], # price
                f"{total:.2f}", # total
                date_str, # date
                ""      # notes
            )
            
            # Determine row color based on some logic or random for now to match the colorful theme
            # In the image, colors seem to group shipments or just alternate
            tag = 'white_row' 
            
            self.tree.insert('', tk.END, values=values, tags=(tag,))

