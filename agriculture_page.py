import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import ColorManager
from datetime import datetime

class AgricultureTransferPage:
    def __init__(self, parent_window):
        self.db = Database()
        self.color_manager = ColorManager()
        self.theme = self.color_manager.get_random_theme()
        
        self.colors = {
            'bg': '#FFB347',
            'header_bg': '#6C3483',
            'card_bg': 'white',
            'text_primary': '#2C3E50',
            'text_secondary': '#7F8C8D',
            'accent': '#E67E22',
            'button_bg': '#800000',
            'button_fg': 'white',
            'border': '#BDC3C7'
        }
        
        self.col_colors = [
            '#F5CBA7', '#F9E79F', '#F5B7B1', '#AED6F1', '#A9DFBF', '#D7BDE2'
        ]
        
        self.window = tk.Toplevel(parent_window)
        self.window.title("نظام ترحيل الزراعة")
        self.window.geometry("1400x800")
        self.window.configure(bg=self.colors['bg'])
        self.window.resizable(True, True)
        
        self.fonts = {
            'header': ('Playpen Sans Arabic', 22, 'bold'),
            'label': ('Playpen Sans Arabic', 16, 'bold'),
            'entry': ('Arial', 18),
            'button': ('Playpen Sans Arabic', 16, 'bold'),
            'table': ('Playpen Sans Arabic', 18, 'bold')
        }
        
        self.shipment_var = tk.StringVar()
        self.item_var = tk.StringVar()
        self.price_var = tk.StringVar()
        
        self.table_rows = []
        self.current_row_index = 0
        self.setup_ui()
        
        # Add traces AFTER creating the first row
        self.shipment_var.trace('w', self.update_existing_rows)
        self.item_var.trace('w', self.update_existing_rows)
        self.price_var.trace('w', self.update_existing_rows)

    def update_existing_rows(self, *args):
        """Update all existing editable rows when top fields change"""
        client_name = self.shipment_var.get()
        item_name = self.item_var.get()
        price = self.price_var.get()
        
        for row in self.table_rows:
            # Only update if row is not saved (check if seller name field is editable)
            try:
                if row[0]['state'] != 'readonly':  # If seller name is editable, row is not saved
                    # Update client name (column 1)
                    row[1].config(state='normal')
                    row[1].delete(0, tk.END)
                    if client_name:
                        row[1].insert(0, client_name)
                    row[1].config(state='readonly')
                    
                    # Update item name (column 2)
                    row[2].config(state='normal')
                    row[2].delete(0, tk.END)
                    if item_name:
                        row[2].insert(0, item_name)
                    row[2].config(state='readonly')
                    
                    # Update price (column 3)
                    row[3].config(state='normal')
                    row[3].delete(0, tk.END)
                    if price:
                        row[3].insert(0, price)
                    row[3].config(state='readonly')
            except:
                pass

    def setup_ui(self):
        self.create_top_bar()
        main_frame = tk.Frame(self.window, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        self.create_table(main_frame)

    def create_top_bar(self):
        top_frame = tk.Frame(self.window, bg=self.colors['header_bg'], height=100, padx=30)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)
        
        def make_entry(parent, var, width=20):
            return tk.Entry(parent, textvariable=var, font=self.fonts['entry'], width=width, justify='center')
        
        # Single Row - All input fields
        controls_row = tk.Frame(top_frame, bg=self.colors['header_bg'])
        controls_row.pack(fill=tk.X, pady=25)
        
        # Date (Left)
        date_frame = tk.Frame(controls_row, bg=self.colors['header_bg'])
        date_frame.pack(side=tk.LEFT, padx=10)
        
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y/%m/%d"))
        date_entry = make_entry(date_frame, self.date_var, width=12)
        date_entry.pack(side=tk.LEFT, padx=5)
        date_entry.config(state='readonly', bg='#E8F8F5')
        
        tk.Label(date_frame, text="التاريخ:", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.LEFT, padx=5)
        
        # Price (Center-Left)
        price_frame = tk.Frame(controls_row, bg=self.colors['header_bg'])
        price_frame.pack(side=tk.LEFT, padx=10)
        
        self.price_entry = make_entry(price_frame, self.price_var, width=12)
        self.price_entry.pack(side=tk.LEFT, padx=5)
        self.price_entry.bind('<Return>', self.on_price_enter)
        
        tk.Label(price_frame, text="السعر:", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.LEFT, padx=5)
        
        # Client (Center) - swapped with Item
        client_frame = tk.Frame(controls_row, bg=self.colors['header_bg'])
        client_frame.pack(side=tk.RIGHT, padx=10)
        
        clients = self.db.get_all_clients_accounts()
        client_names = [c[1] for c in clients]
        
        self.client_combo = ttk.Combobox(client_frame, textvariable=self.shipment_var, values=client_names, 
                                        font=self.fonts['entry'], width=25, justify='center')
        self.client_combo.pack(side=tk.LEFT, padx=5)
        self.client_combo.bind('<Return>', self.on_client_enter)
        self.client_combo.focus()
        
        tk.Label(client_frame, text="اسم العميل:", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.LEFT, padx=5)
        
        # Item (Right) - swapped with Client
        item_frame = tk.Frame(controls_row, bg=self.colors['header_bg'])
        item_frame.pack(side=tk.RIGHT, padx=10)
        
        meals = self.db.get_all_meals()
        meal_names = [m[1] for m in meals]
        
        self.item_combo = ttk.Combobox(item_frame, textvariable=self.item_var, values=meal_names, 
                                       font=self.fonts['entry'], width=15, justify='center')
        self.item_combo.pack(side=tk.LEFT, padx=5)
        self.item_combo.bind('<Return>', self.on_item_enter)
        
        def on_item_change(e=None):
            item_name = self.item_var.get()
            if item_name:
                for meal in meals:
                    if meal[1] == item_name:
                        self.price_var.set(str(meal[2]))
                        return
        self.item_combo.bind('<<ComboboxSelected>>', on_item_change)
        
        tk.Label(item_frame, text="الصنف:", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.LEFT, padx=5)

    def on_client_enter(self, event=None):
        """When Enter is pressed in client field, move to item field"""
        self.item_combo.focus()
        
    def on_item_enter(self, event=None):
        """When Enter is pressed in item field, move to price field"""
        self.price_entry.focus()
        
    def on_price_enter(self, event=None):
        """When Enter is pressed in price field, move to first row"""
        if self.table_rows:
            self.table_rows[0][0].focus()

    def create_table(self, parent):
        table_frame = tk.Frame(parent, bg=self.colors['bg'])
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(table_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg'])
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_frame_id, width=e.width))
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        headers = ['اسم البائع', 'اسم العميل', 'الصنف', 'سعر الوحدة', 'الوزن', 'العدد']
        
        for i, text in enumerate(headers):
            lbl = tk.Label(self.scrollable_frame, text=text, font=self.fonts['table'],
                          bg=self.col_colors[i], relief=tk.RAISED, bd=3, height=2)
            lbl.grid(row=0, column=i, sticky='nsew', padx=2, pady=2)
            self.scrollable_frame.grid_columnconfigure(i, weight=1)
            
        # Create first row only
        self.add_new_row()

    def add_new_row(self):
        """Add a new editable row"""
        row_num = len(self.table_rows) + 1
        
        entry_style = {
            'font': self.fonts['table'],
            'relief': tk.SUNKEN,
            'bd': 2,
            'justify': 'center'
        }
        
        row_widgets = []
        for col_idx in range(6):
            e = tk.Entry(self.scrollable_frame, **entry_style, bg=self.col_colors[col_idx])
            
            # Pre-fill client name, item, and price
            if col_idx == 1:  # Client name
                shipment_val = self.shipment_var.get()
                if shipment_val:
                    e.insert(0, shipment_val)
                    e.config(state='readonly')
            elif col_idx == 2:  # Item name
                item_val = self.item_var.get()
                if item_val:
                    e.insert(0, item_val)
                    e.config(state='readonly')
            elif col_idx == 3:  # Price
                price_val = self.price_var.get()
                if price_val:
                    e.insert(0, price_val)
                    e.config(state='readonly')
            
            e.grid(row=row_num, column=col_idx, sticky='nsew', padx=2, pady=2, ipady=15)
            
            # Bind Enter key to move to next field or save
            if col_idx == 0:  # Seller name
                e.bind('<Return>', lambda ev, idx=row_num-1: self.move_to_weight(idx))
            elif col_idx == 4:  # Weight
                e.bind('<Return>', lambda ev, idx=row_num-1: self.move_to_count(idx))
            elif col_idx == 5:  # Count
                e.bind('<Return>', lambda ev, idx=row_num-1: self.save_current_row(idx))
            
            row_widgets.append(e)
        
        self.table_rows.append(row_widgets)
        
        # Focus on seller name field
        if row_widgets:
            row_widgets[0].focus()

    def move_to_weight(self, row_idx):
        """Move focus to weight field"""
        if row_idx < len(self.table_rows):
            self.table_rows[row_idx][4].focus()
    
    def move_to_count(self, row_idx):
        """Move focus to count field"""
        if row_idx < len(self.table_rows):
            self.table_rows[row_idx][5].focus()

    def save_current_row(self, row_idx):
        """Save the current row and create a new one"""
        if row_idx >= len(self.table_rows):
            return
        
        row = self.table_rows[row_idx]
        
        client_name = self.shipment_var.get().strip()
        item_name_input = self.item_var.get().strip()
        unit_price_str = self.price_var.get().strip()
        seller_name_input = row[0].get().strip()
        weight_str = row[4].get().strip()
        count_str = row[5].get().strip()
        
        # Validation
        if not client_name:
            messagebox.showwarning("تنبيه", "الرجاء إدخال اسم العميل أولاً")
            self.client_combo.focus()
            return
            
        if not item_name_input:
            messagebox.showwarning("تنبيه", "الرجاء إدخال الصنف أولاً")
            self.item_combo.focus()
            return
        
        if not seller_name_input:
            messagebox.showwarning("تنبيه", "الرجاء إدخال اسم البائع")
            row[0].focus()
            return
        
        try:
            weight = float(weight_str) if weight_str else 0.0
            count = float(count_str) if count_str else 0.0
            
            if weight == 0 and count == 0:
                messagebox.showwarning("تنبيه", "الرجاء إدخال الوزن أو العدد")
                row[4].focus()
                return
            
            unit_price = float(unit_price_str) if unit_price_str else 0.0
            
            # Resolve Item Name
            meals = self.db.get_all_meals()
            final_item_name = item_name_input
            item_exists = False
            
            for meal in meals:
                if meal[1].strip().lower() == item_name_input.lower():
                    final_item_name = meal[1]
                    item_exists = True
                    break
            
            # Add item if new
            if not item_exists:
                self.db.add_meal(final_item_name, unit_price, 0)
            
            # Calculate amount
            amount = 0.0
            if weight > 0:
                amount = weight * unit_price
            elif count > 0:
                amount = count * unit_price
            
            # 1. Client Action (Credit)
            self.db.add_client_debt(client_name, -amount)
            
            # Record 'in' transfer for Client
            self.db.add_agriculture_transfer(client_name, seller_name_input, final_item_name, 
                                            unit_price, weight, count, "", "in")
            
            # 2. Seller Action (Debit)
            seller_data = self.db.get_seller_by_name(seller_name_input)
            if not seller_data:
                self.db.add_seller_account(seller_name_input, 0, 0)
                seller_data = self.db.get_seller_by_name(seller_name_input)
            
            seller_id = seller_data[0]
            
            # Record 'out' transfer for Seller
            self.db.add_agriculture_transfer(client_name, seller_name_input, final_item_name, 
                                            unit_price, weight, count, "", "out")
            
            # Add Transaction to Seller Account
            note = f"نقلة من العميل {client_name}"
            today_date = datetime.now().strftime("%Y-%m-%d")
            
            self.db.add_seller_transaction(seller_id, amount, "متبقي", count, weight, unit_price,
                                          final_item_name, today_date, "", "", note)
            
            # Make current row readonly
            for widget in row:
                widget.config(state='readonly', bg='#D5F5E3')  # Light green to show saved
            
            # Add new row
            self.add_new_row()
            
        except ValueError as e:
            messagebox.showerror("خطأ", f"خطأ في البيانات المدخلة: {str(e)}")

    def clear_table(self):
        """Clear all rows and start fresh"""
        for row in self.table_rows:
            for widget in row:
                widget.destroy()
        self.table_rows = []
        self.add_new_row()