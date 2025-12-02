import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import Database
from utils import ColorManager

class InventoryPage:
    def __init__(self, parent_window):
        self.db = Database()
        self.color_manager = ColorManager()
        
        # Match AccountsPage colors
        self.colors = {
            'bg': '#FFB347',           # Medium Orange (window_bg)
            'header_bg': '#6C3483',    # Dark Purple
            'card_bg': '#FFFFFF',      # White
            'button_bg': '#800000',    # Maroon
            'text_primary': '#2C3E50',
            'accent': '#F39C12'
        }
        
        self.window = tk.Toplevel(parent_window)
        self.window.title("برنامج العدة")
        self.window.geometry("1100x700")
        self.window.configure(bg=self.colors['bg'])
        self.window.resizable(True, True)
        
        self.fonts = {
            'header': ('Playpen Sans Arabic', 22, 'bold'),
            'label': ('Playpen Sans Arabic', 14, 'bold'),
            'entry': ('Arial', 14),
            'button': ('Playpen Sans Arabic', 14, 'bold'),
            'table': ('Arial', 13, 'bold')
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.window, bg=self.colors['header_bg'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="إدارة المخزون والعدة", font=self.fonts['header'], bg=self.colors['header_bg'], fg='white').pack(pady=20)
        
        # Main Content
        main_content = tk.Frame(self.window, bg=self.colors['bg'])
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Right Side: Actions & Add New
        right_frame = tk.Frame(main_content, bg=self.colors['bg'], width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Add New Item Card
        add_card = tk.Frame(right_frame, bg=self.colors['card_bg'], padx=15, pady=15, relief=tk.RAISED, bd=2)
        add_card.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(add_card, text="إضافة عدة جديدة", font=self.fonts['button'], bg=self.colors['card_bg'], fg=self.colors['button_bg']).pack(pady=(0, 10))
        
        tk.Label(add_card, text="اسم العدة", font=self.fonts['label'], bg=self.colors['card_bg']).pack(anchor='e')
        self.entry_name = tk.Entry(add_card, font=self.fonts['entry'], justify='center', bg='#F8F9F9')
        self.entry_name.pack(fill=tk.X, pady=(0, 10), ipady=5)
        
        tk.Label(add_card, text="سعر القطعة", font=self.fonts['label'], bg=self.colors['card_bg']).pack(anchor='e')
        self.entry_price = tk.Entry(add_card, font=self.fonts['entry'], justify='center', bg='#F8F9F9')
        self.entry_price.pack(fill=tk.X, pady=(0, 10), ipady=5)
        self.entry_price.insert(0, "0")
        
        tk.Label(add_card, text="العدد الابتدائي", font=self.fonts['label'], bg=self.colors['card_bg']).pack(anchor='e')
        self.entry_qty = tk.Entry(add_card, font=self.fonts['entry'], justify='center', bg='#F8F9F9')
        self.entry_qty.pack(fill=tk.X, pady=(0, 10), ipady=5)
        self.entry_qty.insert(0, "0")
        
        tk.Button(add_card, text="حفظ", command=self.add_item, bg=self.colors['button_bg'], fg='white', font=self.fonts['button'], relief=tk.RAISED, bd=2, height=1).pack(fill=tk.X, pady=5)
        
        # Action Buttons
        action_card = tk.Frame(right_frame, bg=self.colors['card_bg'], padx=15, pady=15, relief=tk.RAISED, bd=2)
        action_card.pack(fill=tk.X)
        
        tk.Label(action_card, text="عمليات على المحدد", font=self.fonts['button'], bg=self.colors['card_bg'], fg=self.colors['button_bg']).pack(pady=(0, 10))
        
        # Edit Item
        tk.Button(action_card, text="تعديل العدة", command=self.edit_item, bg='#8E44AD', fg='white', font=self.fonts['button'], relief=tk.RAISED, bd=2, height=1).pack(fill=tk.X, pady=5)
        
        # Buy (Increase)
        tk.Button(action_card, text="شراء عدة (+)", command=lambda: self.update_stock('buy'), bg='#27AE60', fg='white', font=self.fonts['button'], relief=tk.RAISED, bd=2, height=1).pack(fill=tk.X, pady=5)
        

        
        # Return (Increase)
        tk.Button(action_card, text="استرجاع عدة (+)", command=lambda: self.update_stock('return'), bg='#2980B9', fg='white', font=self.fonts['button'], relief=tk.RAISED, bd=2, height=1).pack(fill=tk.X, pady=5)
        
        # Delete
        tk.Button(action_card, text="حذف الصنف", command=self.delete_item, bg='#7F8C8D', fg='white', font=self.fonts['button'], relief=tk.RAISED, bd=2, height=1).pack(fill=tk.X, pady=(20, 5))

        # Left Side: Table
        table_frame = tk.Frame(main_content, bg=self.colors['card_bg'], padx=2, pady=2, relief=tk.SUNKEN, bd=2)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        cols = ('name', 'price', 'qty')
        self.tree = ttk.Treeview(table_frame, columns=cols, show='headings', style="Inventory.Treeview")
        
        self.tree.heading('name', text='اسم العدة')
        self.tree.heading('price', text='سعر القطعة')
        self.tree.heading('qty', text='العدد المتبقي')
        
        self.tree.column('name', anchor='center', width=200)
        self.tree.column('price', anchor='center', width=120)
        self.tree.column('qty', anchor='center', width=120)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Styling
        style = ttk.Style()
        style.theme_use('clam') # Use clam theme for better color control
        
        # Configure Heading Style
        style.configure(
            "Inventory.Treeview.Heading", 
            font=self.fonts['button'], 
            background=self.colors['header_bg'], 
            foreground='white',
            relief='raised'
        )
        
        # Configure Row Style
        style.configure(
            "Inventory.Treeview", 
            font=self.fonts['table'], 
            rowheight=40,
            background='white',
            fieldbackground='white'
        )
        style.map("Inventory.Treeview", background=[('selected', self.colors['accent'])])
        
        self.load_data()
        
    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        items = self.db.get_all_inventory()
        for item in items:
            # item: id, name, qty, price
            self.tree.insert('', tk.END, values=(item[1], item[3], item[2]), iid=item[0])
            
    def add_item(self):
        name = self.entry_name.get().strip()
        price = self.entry_price.get().strip()
        qty = self.entry_qty.get().strip()
        
        if not name:
            messagebox.showwarning("تنبيه", "الرجاء إدخال اسم العدة")
            return
            
        try:
            price_val = float(price) if price else 0.0
            qty_val = int(qty) if qty else 0
            if self.db.add_inventory_item(name, qty_val, price_val):
                self.load_data()
                self.entry_name.delete(0, tk.END)
                self.entry_price.delete(0, tk.END)
                self.entry_price.insert(0, "0")
                self.entry_qty.delete(0, tk.END)
                self.entry_qty.insert(0, "0")
                # Removed messagebox.showinfo("نجاح", "تمت الإضافة بنجاح")
                self.entry_name.focus()
            else:
                messagebox.showerror("خطأ", "هذا الاسم موجود بالفعل")
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء إدخال أرقام صحيحة")
    
    def edit_item(self):
        """تعديل العدة المحددة"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء تحديد عدة للتعديل")
            return
        
        item_id = selected[0]
        item_values = self.tree.item(item_id)['values']
        
        # Create edit dialog
        edit_window = tk.Toplevel(self.window)
        edit_window.title("تعديل العدة")
        edit_window.geometry("400x300")
        edit_window.configure(bg=self.colors['card_bg'])
        
        # Center window
        edit_window.update_idletasks()
        x = (edit_window.winfo_screenwidth() // 2) - 200
        y = (edit_window.winfo_screenheight() // 2) - 150
        edit_window.geometry(f"400x300+{x}+{y}")
        
        tk.Label(edit_window, text="تعديل بيانات العدة", font=self.fonts['button'], bg=self.colors['card_bg'], fg=self.colors['button_bg']).pack(pady=20)
        
        # Fields
        fields_frame = tk.Frame(edit_window, bg=self.colors['card_bg'])
        fields_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(fields_frame, text="اسم العدة", font=self.fonts['label'], bg=self.colors['card_bg']).pack(anchor='e')
        entry_name = tk.Entry(fields_frame, font=self.fonts['entry'], justify='center', bg='#F8F9F9')
        entry_name.pack(fill=tk.X, pady=(0, 15), ipady=5)
        entry_name.insert(0, item_values[0])
        
        tk.Label(fields_frame, text="سعر القطعة", font=self.fonts['label'], bg=self.colors['card_bg']).pack(anchor='e')
        entry_price = tk.Entry(fields_frame, font=self.fonts['entry'], justify='center', bg='#F8F9F9')
        entry_price.pack(fill=tk.X, pady=(0, 15), ipady=5)
        entry_price.insert(0, item_values[1])
        
        def save_changes():
            new_name = entry_name.get().strip()
            new_price = entry_price.get().strip()
            
            if not new_name:
                messagebox.showwarning("تنبيه", "الرجاء إدخال اسم العدة", parent=edit_window)
                return
            
            try:
                price_val = float(new_price) if new_price else 0.0
                self.db.update_inventory_item(item_id, new_name, price_val)
                self.load_data()
                edit_window.destroy()
                messagebox.showinfo("نجاح", "تم التعديل بنجاح")
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال سعر صحيح", parent=edit_window)
        
        tk.Button(edit_window, text="حفظ التعديلات", command=save_changes, bg=self.colors['button_bg'], fg='white', font=self.fonts['button'], relief=tk.RAISED, bd=2, height=1).pack(pady=10)
        
        entry_name.focus()
        edit_window.bind('<Return>', lambda e: save_changes())
            
    def update_stock(self, action):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء تحديد صنف أولاً")
            return
            
        item_id = selected[0]
        item_name = self.tree.item(item_id)['values'][0]
        
        action_map = {
            'buy': ('شراء', 1),
            'return': ('استرجاع', 1)
        }
        
        verb, multiplier = action_map[action]
        
        amount_str = simpledialog.askstring(f"{verb} عدة", f"أدخل عدد {item_name} المراد {verb}ه:", parent=self.window)
        
        if amount_str:
            try:
                amount = int(amount_str)
                if amount <= 0:
                    raise ValueError
                
                change = amount * multiplier
                self.db.update_inventory_quantity(item_id, change)
                self.load_data()
                messagebox.showinfo("نجاح", f"تمت عملية {verb} بنجاح")
                
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال رقم صحيح موجب")

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء تحديد صنف للحذف")
            return
        
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذا الصنف؟"):
            self.db.delete_inventory_item(selected[0])
            self.load_data()
