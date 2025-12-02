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
        self.window.geometry("1300x850")
        self.window.configure(bg=self.colors['bg'])
        self.window.resizable(True, True)
        
        self.fonts = {
            'header': ('Playpen Sans Arabic', 20, 'bold'),
            'label': ('Playpen Sans Arabic', 14, 'bold'),
            'entry': ('Arial', 14),
            'button': ('Playpen Sans Arabic', 14, 'bold')
        }
        
        self.shipment_var = tk.StringVar()
        self.item_var = tk.StringVar()
        self.price_var = tk.StringVar()
        
        self.shipment_var.trace('w', lambda *args: self.load_data())
        self.item_var.trace('w', lambda *args: self.load_data())
        self.price_var.trace('w', lambda *args: self.load_data())
        
        self.table_rows = []
        self.setup_ui()

    def setup_ui(self):
        self.create_top_bar()
        main_frame = tk.Frame(self.window, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.create_table(main_frame)
        self.create_bottom_bar()
        
    def create_top_bar(self):
        top_frame = tk.Frame(self.window, bg=self.colors['header_bg'], height=80, padx=20)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)
        
        controls = tk.Frame(top_frame, bg=self.colors['header_bg'])
        controls.pack(fill=tk.BOTH, expand=True, pady=20)
        
        def make_entry(parent, var, width=20):
            return tk.Entry(parent, textvariable=var, font=self.fonts['entry'], width=width, justify='center')

        shipment_frame = tk.Frame(controls, bg=self.colors['header_bg'])
        shipment_frame.pack(side=tk.RIGHT, padx=10)
        
        date_var = tk.StringVar(value=datetime.now().strftime("%Y/%m/%d"))
        date_entry = make_entry(shipment_frame, date_var, width=12)
        date_entry.pack(side=tk.RIGHT, padx=5)
        date_entry.config(state='readonly', bg='#E8F8F5')
        
        tk.Label(shipment_frame, text="التاريخ:", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.RIGHT, padx=5)
        
        shipment_entry = make_entry(shipment_frame, self.shipment_var, width=25)
        shipment_entry.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(shipment_frame, text="اسم النقلة:", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.RIGHT, padx=5)
        
        item_frame = tk.Frame(controls, bg=self.colors['header_bg'])
        item_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Button(item_frame, text="بيان الاصناف", command=self.show_items_list, font=('Playpen Sans Arabic', 10, 'bold'), bg='#2E86C1', fg='white').pack(side=tk.RIGHT, padx=5)
        
        tk.Label(item_frame, text="الصنف:", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.RIGHT, padx=5)
        
        meals = self.db.get_all_meals()
        meal_names = [m[1] for m in meals]
        
        item_combo = ttk.Combobox(item_frame, textvariable=self.item_var, values=meal_names, font=self.fonts['entry'], width=20, justify='center')
        item_combo.pack(side=tk.RIGHT)
        
        def on_item_change(e=None):
            item_name = self.item_var.get()
            if item_name:
                for meal in meals:
                    if meal[1] == item_name:
                        self.price_var.set(str(meal[2]))
                        return
        item_combo.bind('<<ComboboxSelected>>', on_item_change)

        price_frame = tk.Frame(controls, bg=self.colors['header_bg'])
        price_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(price_frame, text="سعر الوحدة:", font=self.fonts['label'], bg=self.colors['header_bg'], fg='white').pack(side=tk.RIGHT, padx=5)
        price_entry = make_entry(price_frame, self.price_var, width=15)
        price_entry.pack(side=tk.RIGHT)

    def show_items_list(self):
        """Show a window with all items"""
        list_window = tk.Toplevel(self.window)
        list_window.title("بيان الاصناف")
        list_window.geometry("400x500")
        list_window.configure(bg='white')
        
        tk.Label(list_window, text="قائمة الاصناف المسجلة", font=('Playpen Sans Arabic', 16, 'bold'), bg='white', fg=self.colors['header_bg']).pack(pady=10)
        
        list_frame = tk.Frame(list_window, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        lb = tk.Listbox(list_frame, font=('Arial', 14), yscrollcommand=scrollbar.set, justify='right')
        lb.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=lb.yview)
        
        meals = self.db.get_all_meals()
        for meal in meals:
            lb.insert(tk.END, f"{meal[1]} - {meal[2]} ج.م")

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
        
        headers = ['اسم البائع', 'اسم النقلة', 'الصنف', 'سعر الوحدة', 'الوزن', 'العدد']
        
        for i, text in enumerate(headers):
            lbl = tk.Label(self.scrollable_frame, text=text, font=('Playpen Sans Arabic', 16, 'bold'),
                          bg=self.col_colors[i], relief=tk.RAISED, bd=2, height=2)
            lbl.grid(row=0, column=i, sticky='nsew', padx=1, pady=1)
            self.scrollable_frame.grid_columnconfigure(i, weight=1)
            
        self.load_data()

    def create_bottom_bar(self):
        btn_frame = tk.Frame(self.window, bg=self.colors['bg'], pady=20)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(btn_frame, text="ترحيل", command=self.save_transfer, font=self.fonts['button'],
                 bg=self.colors['button_bg'], fg='white', relief=tk.RAISED, bd=3, cursor='hand2',
                 width=20, height=2).pack(side=tk.RIGHT, padx=20)

    def load_data(self):
        for row in self.table_rows:
            for widget in row:
                widget.destroy()
        self.table_rows = []
        
        saved_data = self.db.get_agriculture_transfers()
        saved_data.reverse()
        
        entry_style = {'font': ('Playpen Sans Arabic', 14), 'relief': tk.SUNKEN, 'bd': 1, 'justify': 'center'}
        
        row_num = 1
        
        row_widgets = []
        for col_idx in range(6):
            e = tk.Entry(self.scrollable_frame, **entry_style, bg=self.col_colors[col_idx])
            
            if col_idx == 1:
                shipment_val = self.shipment_var.get()
                if shipment_val:
                    e.insert(0, shipment_val)
                    e.config(state='readonly')
            elif col_idx == 2:
                item_val = self.item_var.get()
                if item_val:
                    e.insert(0, item_val)
                    e.config(state='readonly')
            elif col_idx == 3:
                price_val = self.price_var.get()
                if price_val:
                    e.insert(0, price_val)
                    e.config(state='readonly')
            
            e.grid(row=row_num, column=col_idx, sticky='nsew', padx=1, pady=1, ipady=8)
            row_widgets.append(e)
            
        self.table_rows.append(row_widgets)
        row_num += 1
        
        for data_row in saved_data:
            row_widgets = []
            vals = [data_row[2], data_row[1], data_row[3], data_row[4], data_row[5], data_row[6]]
            
            for col_idx, val in enumerate(vals):
                e = tk.Entry(self.scrollable_frame, **entry_style, bg=self.col_colors[col_idx])
                e.insert(0, str(val))
                e.config(state='readonly')
                e.grid(row=row_num, column=col_idx, sticky='nsew', padx=1, pady=1, ipady=8)
                row_widgets.append(e)
            
            self.table_rows.append(row_widgets)
            row_num += 1
            
        total_target_rows = 20
        current_rows = len(self.table_rows)
        for i in range(total_target_rows - current_rows):
            row_widgets = []
            for col_idx in range(6):
                e = tk.Entry(self.scrollable_frame, **entry_style, bg=self.col_colors[col_idx])
                e.config(state='readonly')
                e.grid(row=row_num, column=col_idx, sticky='nsew', padx=1, pady=1, ipady=8)
                row_widgets.append(e)
            row_num += 1

    def save_transfer(self):
        shipment_name = self.shipment_var.get().strip()
        item_name_input = self.item_var.get().strip()
        unit_price_str = self.price_var.get().strip()
        
        if not shipment_name:
            messagebox.showwarning("تنبيه", "الرجاء إدخال اسم النقلة")
            return
            
        if not item_name_input:
            messagebox.showwarning("تنبيه", "الرجاء إدخال الصنف")
            return
        
        meals = self.db.get_all_meals()
        final_item_name = item_name_input
        item_exists = False
        
        for meal in meals:
            if meal[1].strip().lower() == item_name_input.lower():
                final_item_name = meal[1]
                item_exists = True
                break
        
        if not item_exists:
            try:
                price_val = float(unit_price_str) if unit_price_str else 0.0
                self.db.add_meal(final_item_name, price_val, 0)
            except ValueError:
                messagebox.showerror("خطأ", "سعر الوحدة غير صحيح")
                return
        
        try:
            unit_price = float(unit_price_str) if unit_price_str else 0.0
        except ValueError:
            messagebox.showerror("خطأ", "سعر الوحدة غير صحيح")
            return
        
        if len(self.table_rows) > 0:
            first_row = self.table_rows[0]
            name_input = first_row[0].get().strip()
            weight_str = first_row[4].get().strip()
            count_str = first_row[5].get().strip()
            
            if not name_input:
                messagebox.showwarning("تنبيه", "الرجاء إدخال الاسم في الصف الأول")
                return
            
            try:
                weight = float(weight_str) if weight_str else 0.0
                count = float(count_str) if count_str else 0.0
                
                amount = 0.0
                if weight > 0:
                    amount = weight * unit_price
                elif count > 0:
                    amount = count * unit_price
                
                # Check if name exists in Sellers
                seller_data = self.db.get_seller_by_name(name_input)
                
                # Check if name exists in Clients
                clients = self.db.get_all_clients_accounts()
                client_exists = any(c[1] == name_input for c in clients)
                
                if seller_data:
                    # It's a Seller
                    self.db.add_agriculture_transfer(shipment_name, name_input, final_item_name, unit_price, weight, count, "", "out")
                    
                    seller_id = seller_data[0]
                    note = f"ترحيل زراعة - {shipment_name}"
                    today_date = datetime.now().strftime("%Y-%m-%d")
                    
                    self.db.add_seller_transaction(seller_id, amount, "متبقي", count, weight, unit_price,
                                                   final_item_name, today_date, "", "", note)
                    
                    messagebox.showinfo("نجاح", f"تم ترحيل النقلة لحساب البائع {name_input}")
                    
                elif client_exists:
                    # It's a Client
                    self.db.add_agriculture_transfer(name_input, shipment_name, final_item_name, unit_price, weight, count, "", "in")
                    
                    # Add debt to client
                    self.db.add_client_debt(name_input, amount)
                    
                    messagebox.showinfo("نجاح", f"تم ترحيل النقلة لحساب العميل {name_input}")
                    
                else:
                    # Treat as new Seller
                    self.db.add_seller_account(name_input, 0, 0)
                    seller_data = self.db.get_seller_by_name(name_input)
                    seller_id = seller_data[0]
                    
                    self.db.add_agriculture_transfer(shipment_name, name_input, final_item_name, unit_price, weight, count, "", "out")
                    
                    note = f"ترحيل زراعة - {shipment_name}"
                    today_date = datetime.now().strftime("%Y-%m-%d")
                    
                    self.db.add_seller_transaction(seller_id, amount, "متبقي", count, weight, unit_price,
                                                   final_item_name, today_date, "", "", note)
                                                   
                    messagebox.showinfo("نجاح", f"تم إضافة بائع جديد وترحيل النقلة لحساب {name_input}")
                
                self.item_var.set("")
                self.price_var.set("")
                
                self.load_data()
                
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال قيم رقمية صحيحة")
        else:
            messagebox.showwarning("تنبيه", "لا يوجد صف للإدخال")