import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name="company_accounts.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """إنشاء اتصال بقاعدة البيانات"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """تهيئة قاعدة البيانات وإنشاء الجداول الأساسية"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # جدول العملاء
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الموردين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المنتجات (الخضروات والفواكه)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                unit TEXT,
                price REAL DEFAULT 0,
                stock_quantity REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المبيعات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                sale_date DATE NOT NULL,
                total_amount REAL DEFAULT 0,
                paid_amount REAL DEFAULT 0,
                remaining_amount REAL DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')
        
        # جدول تفاصيل المبيعات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        # جدول المشتريات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                purchase_date DATE NOT NULL,
                total_amount REAL DEFAULT 0,
                paid_amount REAL DEFAULT 0,
                remaining_amount REAL DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        ''')
        
        # جدول تفاصيل المشتريات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (purchase_id) REFERENCES purchases(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        # جدول المدفوعات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL, -- 'sale' or 'purchase'
                reference_id INTEGER NOT NULL, -- sale_id or purchase_id
                amount REAL NOT NULL,
                payment_date DATE NOT NULL,
                payment_method TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول حسابات البائعين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sellers_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_name TEXT NOT NULL,
                phone TEXT, -- رقم الهاتف (جديد)
                remaining_amount REAL DEFAULT 0,
                total_credit REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # محاولة إضافة عمود phone إذا لم يكن موجوداً
        try:
            cursor.execute('ALTER TABLE sellers_accounts ADD COLUMN phone TEXT')
        except sqlite3.OperationalError:
            pass
        
        # جدول معاملات البائعين (الحساب الجاري)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seller_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER NOT NULL,
                amount REAL DEFAULT 0,
                status TEXT, -- مدفوع / متبقي
                count REAL DEFAULT 0,
                weight REAL DEFAULT 0,
                price REAL DEFAULT 0,
                item_name TEXT,
                date TEXT,
                day_name TEXT,
                equipment TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seller_id) REFERENCES sellers_accounts(id) ON DELETE CASCADE
            )
        ''')
        
        # جدول الوجبات / الأصناف
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price_per_kg REAL DEFAULT 0,
                equipment_weight REAL DEFAULT 0, -- وزن العدة المقابل (مثلاً 15 كيلو)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # جدول ترحيل الزراعة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agriculture_transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shipment_name TEXT,
                seller_name TEXT,
                item_name TEXT,
                unit_price REAL DEFAULT 0,
                weight REAL DEFAULT 0,
                count REAL DEFAULT 0,
                equipment TEXT,
                transfer_type TEXT, -- 'in' or 'out'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المنصرفات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                expense_date DATE NOT NULL,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # محاولة إضافة عمود transfer_type إذا لم يكن موجوداً
        try:
            cursor.execute('ALTER TABLE agriculture_transfers ADD COLUMN transfer_type TEXT')
        except sqlite3.OperationalError:
            pass
        
        # محاولة إضافة عمود count إذا لم يكن موجوداً (للنسخ القديمة من قاعدة البيانات)
        try:
            cursor.execute('ALTER TABLE agriculture_transfers ADD COLUMN count REAL DEFAULT 0')
        except sqlite3.OperationalError:
            pass # العمود موجود بالفعل

        # جدول العدة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                quantity INTEGER DEFAULT 0,
                price REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # إضافة عمود السعر إذا لم يكن موجوداً (للتوافق مع قواعد البيانات القديمة)
        try:
            cursor.execute('ALTER TABLE inventory_items ADD COLUMN price REAL DEFAULT 0')
        except sqlite3.OperationalError:
            pass # العمود موجود بالفعل

        # جدول فواتير العملاء
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_name TEXT,
                nolon REAL DEFAULT 0,
                commission TEXT DEFAULT '10%',
                mashal REAL DEFAULT 0,
                rent REAL DEFAULT 0,
                cash REAL DEFAULT 0,
                invoice_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # جدول التقارير اليومية
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date DATE NOT NULL UNIQUE,
                total_collection REAL DEFAULT 0,
                remaining_profit REAL DEFAULT 0,
                total_expenses REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        print("تم تهيئة قاعدة البيانات بنجاح")

    # --- طرق التعامل مع العدة ---
    def get_all_inventory(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, quantity, price FROM inventory_items ORDER BY name')
        results = cursor.fetchall()
        conn.close()
        return results

    def add_inventory_item(self, name, quantity, price=0):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO inventory_items (name, quantity, price) VALUES (?, ?, ?)', (name, quantity, price))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def update_inventory_item(self, item_id, name, price):
        """تحديث اسم وسعر العدة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE inventory_items SET name = ?, price = ? WHERE id = ?', (name, price, item_id))
        conn.commit()
        conn.close()

    def update_inventory_quantity(self, item_id, change_amount):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE inventory_items SET quantity = quantity + ? WHERE id = ?', (change_amount, item_id))
        conn.commit()
        conn.close()

    def delete_inventory_item(self, item_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM inventory_items WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()

    def get_all_sellers_accounts(self):
        """جلب جميع حسابات البائعين"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, seller_name, remaining_amount, total_credit, phone FROM sellers_accounts ORDER BY seller_name')
        results = cursor.fetchall()
        conn.close()
        return results

    def get_sellers_with_balances(self):
        """جلب حسابات البائعين مع الأرصدة المحسوبة من المعاملات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # استعلام لجلب البيانات وحساب المجاميع
        # نفترض أن remaining_amount في جدول sellers_accounts هو الرصيد الافتتاحي
        query = '''
            SELECT 
                s.id, 
                s.seller_name, 
                s.remaining_amount, -- الرصيد الافتتاحي
                s.phone,
                (SELECT SUM(amount) FROM seller_transactions WHERE seller_id = s.id AND status != 'مدفوع') as total_goods,
                (SELECT SUM(amount) FROM seller_transactions WHERE seller_id = s.id AND status = 'مدفوع') as total_paid,
                (SELECT SUM(amount) FROM seller_transactions WHERE seller_id = s.id AND item_name LIKE '%سماح%') as total_allowance
            FROM sellers_accounts s
            ORDER BY s.seller_name
        '''
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        processed_results = []
        for row in results:
            s_id = row[0]
            name = row[1]
            initial_balance = row[2] or 0.0
            phone = row[3]
            total_goods = row[4] or 0.0
            total_paid = row[5] or 0.0
            total_allowance = row[6] or 0.0
            
            # حساب المتبقي النهائي
            # المتبقي = الرصيد الافتتاحي + البضاعة - المدفوعات (شاملة السماح)
            final_remaining = initial_balance + total_goods - total_paid
            
            # التنسيق: id, name, calculated_remaining, calculated_allowance, phone
            processed_results.append((s_id, name, final_remaining, total_allowance, phone))
            
        return processed_results

    # --- حسابات العملاء ---
    def add_client_debt(self, client_name, amount):
        """إضافة دين على البرنامج لصالح العميل (ترحيل عميل)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # التأكد من وجود جدول العملاء
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL UNIQUE,
                balance REAL DEFAULT 0,
                phone TEXT
            )
        ''')
        
        # التحقق مما إذا كان العميل موجوداً
        cursor.execute('SELECT id, balance FROM clients_accounts WHERE client_name = ?', (client_name,))
        result = cursor.fetchone()
        
        if result:
            # تحديث الرصيد (إضافة المبلغ للرصيد الحالي)
            new_balance = result[1] + amount
            cursor.execute('UPDATE clients_accounts SET balance = ? WHERE id = ?', (new_balance, result[0]))
        else:
            # إنشاء عميل جديد
            cursor.execute('INSERT INTO clients_accounts (client_name, balance) VALUES (?, ?)', (client_name, amount))
            
        conn.commit()
        conn.close()

    def get_all_clients_accounts(self):
        """جلب جميع حسابات العملاء"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL UNIQUE,
                balance REAL DEFAULT 0,
                phone TEXT
            )
        ''')
        cursor.execute('SELECT id, client_name, balance, phone FROM clients_accounts ORDER BY client_name')
        results = cursor.fetchall()
        conn.close()
        return results

    def add_client_account(self, client_name, phone=""):
        """إضافة حساب عميل جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Ensure table exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL UNIQUE,
                balance REAL DEFAULT 0,
                phone TEXT
            )
        ''')
        
        try:
            cursor.execute('INSERT INTO clients_accounts (client_name, balance, phone) VALUES (?, 0, ?)', (client_name, phone))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def delete_client_account(self, client_id):
        """حذف حساب عميل"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM clients_accounts WHERE id = ?', (client_id,))
        conn.commit()
        conn.close()

    def get_unique_shipment_names(self):
        """جلب أسماء النقلات الفريدة من جدول ترحيل الزراعة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT shipment_name FROM agriculture_transfers WHERE shipment_name IS NOT NULL AND shipment_name != "" ORDER BY shipment_name')
        results = cursor.fetchall()
        conn.close()
        return [row[0] for row in results]

    def get_seller_by_name(self, name):
        """البحث عن بائع بالاسم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, seller_name, remaining_amount, total_credit FROM sellers_accounts WHERE seller_name = ?', (name,))
        result = cursor.fetchone()
        conn.close()
        return result

    def get_client_by_name(self, name):
        """البحث عن عميل بالاسم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # Ensure table exists just in case
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL UNIQUE,
                balance REAL DEFAULT 0,
                phone TEXT
            )
        ''')
        cursor.execute('SELECT id, client_name, balance, phone FROM clients_accounts WHERE client_name = ?', (name,))
        result = cursor.fetchone()
        conn.close()
        return result

    
    def add_seller_account(self, seller_name, remaining_amount, total_credit, phone=""):
        """إضافة حساب بائع جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sellers_accounts (seller_name, remaining_amount, total_credit, phone)
            VALUES (?, ?, ?, ?)
        ''', (seller_name, remaining_amount, total_credit, phone))
        conn.commit()
        conn.close()
    
    def update_seller_account(self, account_id, seller_name, remaining_amount, total_credit):
        """تحديث حساب بائع"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE sellers_accounts 
            SET seller_name = ?, remaining_amount = ?, total_credit = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (seller_name, remaining_amount, total_credit, account_id))
        conn.commit()
        conn.close()
    
    def delete_seller_account(self, account_id):
        """حذف حساب بائع"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sellers_accounts WHERE id = ?', (account_id,))
        conn.commit()
        conn.close()

    # --- طرق التعامل مع معاملات البائعين ---

    def get_seller_transactions(self, seller_id):
        """جلب جميع معاملات بائع معين"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, amount, status, count, weight, price, item_name, date, day_name, equipment, note 
            FROM seller_transactions 
            WHERE seller_id = ? 
            ORDER BY date DESC, id DESC
        ''', (seller_id,))
        results = cursor.fetchall()
        conn.close()
        return results

    def add_seller_transaction(self, seller_id, amount, status, count, weight, price, item_name, date, day_name, equipment, note):
        """إضافة معاملة جديدة لبائع"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO seller_transactions 
            (seller_id, amount, status, count, weight, price, item_name, date, day_name, equipment, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (seller_id, amount, status, count, weight, price, item_name, date, day_name, equipment, note))
        conn.commit()
        conn.close()

    def update_seller_transaction(self, trans_id, amount, status, count, weight, price, item_name, date, day_name, equipment, note):
        """تحديث معاملة لبائع"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE seller_transactions 
            SET amount=?, status=?, count=?, weight=?, price=?, item_name=?, date=?, day_name=?, equipment=?, note=?
            WHERE id=?
        ''', (amount, status, count, weight, price, item_name, date, day_name, equipment, note, trans_id))
        conn.commit()
        conn.close()

    def delete_seller_transaction(self, trans_id):
        """حذف معاملة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM seller_transactions WHERE id = ?', (trans_id,))
        conn.commit()
        conn.close()

    def get_last_payment_date(self, seller_id):
        """جلب تاريخ آخر عملية دفع لبائع"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date FROM seller_transactions 
            WHERE seller_id = ? AND status = 'مدفوع' 
            ORDER BY date DESC LIMIT 1
        ''', (seller_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def get_last_transaction_date(self, seller_id):
        """جلب تاريخ آخر معاملة لبائع (أي نوع)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date FROM seller_transactions 
            WHERE seller_id = ? 
            ORDER BY date DESC LIMIT 1
        ''', (seller_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    # --- طرق التعامل مع الوجبات / الأصناف ---

    def get_all_meals(self):
        """جلب جميع الوجبات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, price_per_kg, equipment_weight FROM meals ORDER BY name')
        results = cursor.fetchall()
        conn.close()
        return results

    def add_meal(self, name, price, equipment_weight=0):
        """إضافة وجبة جديدة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO meals (name, price_per_kg, equipment_weight) VALUES (?, ?, ?)', (name, price, equipment_weight))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # الاسم مكرر
        finally:
            conn.close()

    def update_meal(self, meal_id, name, price, equipment_weight=0):
        """تحديث بيانات وجبة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE meals 
            SET name = ?, price_per_kg = ?, equipment_weight = ?
            WHERE id = ?
        ''', (name, price, equipment_weight, meal_id))
        conn.commit()
        conn.close()

    def delete_meal(self, meal_id):
        """حذف وجبة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM meals WHERE id = ?', (meal_id,))
        conn.commit()
        conn.close()

    # --- طرق التعامل مع ترحيل الزراعة ---

    def get_agriculture_transfers(self):
        """جلب جميع بيانات ترحيل الزراعة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, shipment_name, seller_name, item_name, unit_price, weight, count, equipment, transfer_type FROM agriculture_transfers ORDER BY created_at DESC')
        results = cursor.fetchall()
        conn.close()
        return results

    def add_agriculture_transfer(self, shipment_name, seller_name, item_name, unit_price, weight, count, equipment, transfer_type):
        """إضافة سجل ترحيل زراعة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO agriculture_transfers (shipment_name, seller_name, item_name, unit_price, weight, count, equipment, transfer_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (shipment_name, seller_name, item_name, unit_price, weight, count, equipment, transfer_type))
        conn.commit()
        conn.close()

    def update_agriculture_transfer(self, trans_id, shipment_name, seller_name, item_name, unit_price, weight, count, equipment, transfer_type):
        """تحديث سجل ترحيل زراعة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE agriculture_transfers 
            SET shipment_name=?, seller_name=?, item_name=?, unit_price=?, weight=?, count=?, equipment=?, transfer_type=?
            WHERE id=?
        ''', (shipment_name, seller_name, item_name, unit_price, weight, count, equipment, transfer_type, trans_id))
        conn.commit()
        conn.close()

    def delete_agriculture_transfer(self, trans_id):
        """حذف سجل ترحيل زراعة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM agriculture_transfers WHERE id = ?', (trans_id,))
        conn.commit()
        conn.close()

    def get_sales_summary(self):
        """جلب ملخص المبيعات (الصنف، إجمالي الوزن، إجمالي السعر)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # نفترض أن إجمالي السعر هو (سعر الوحدة * الوزن)
        cursor.execute('''
            SELECT item_name, SUM(weight), SUM(unit_price * weight) 
            FROM agriculture_transfers 
            GROUP BY item_name
        ''')
        results = cursor.fetchall()
        conn.close()
        return results

    # --- طرق التعامل مع المنصرفات ---

    def get_all_expenses(self):
        """جلب جميع المنصرفات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, description, amount, expense_date, note FROM expenses ORDER BY expense_date DESC, id DESC')
        results = cursor.fetchall()
        conn.close()
        return results

    def add_expense(self, description, amount, expense_date, note=""):
        """إضافة منصرف جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (description, amount, expense_date, note)
            VALUES (?, ?, ?, ?)
        ''', (description, amount, expense_date, note))
        conn.commit()
        conn.close()

    def update_expense(self, expense_id, description, amount, expense_date, note=""):
        """تحديث منصرف"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE expenses 
            SET description = ?, amount = ?, expense_date = ?, note = ?
            WHERE id = ?
        ''', (description, amount, expense_date, note, expense_id))
        conn.commit()
        conn.close()

    def delete_expense(self, expense_id):
        """حذف منصرف"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
        conn.close()

    # --- طرق التعامل مع فواتير العملاء ---

    def save_client_invoice(self, owner_name, nolon, commission, mashal, rent, cash, invoice_date, net_amount=0, final_total=0):
        """حفظ فاتورة عميل جديدة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if table has net_amount and final_total columns, if not, add them
        cursor.execute("PRAGMA table_info(client_invoices)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'net_amount' not in columns:
            cursor.execute('ALTER TABLE client_invoices ADD COLUMN net_amount REAL DEFAULT 0')
        if 'final_total' not in columns:
            cursor.execute('ALTER TABLE client_invoices ADD COLUMN final_total REAL DEFAULT 0')
        
        cursor.execute('''
            INSERT INTO client_invoices (owner_name, nolon, commission, mashal, rent, cash, invoice_date, net_amount, final_total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (owner_name, nolon, commission, mashal, rent, cash, invoice_date, net_amount, final_total))
        invoice_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return invoice_id

    def update_client_invoice(self, invoice_id, owner_name, nolon, commission, mashal, rent, cash, invoice_date, net_amount=0, final_total=0):
        """تحديث فاتورة عميل"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE client_invoices 
            SET owner_name=?, nolon=?, commission=?, mashal=?, rent=?, cash=?, invoice_date=?, net_amount=?, final_total=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (owner_name, nolon, commission, mashal, rent, cash, invoice_date, net_amount, final_total, invoice_id))
        conn.commit()
        conn.close()

    def get_latest_client_invoice(self):
        """جلب آخر فاتورة عميل"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, owner_name, nolon, commission, mashal, rent, cash, invoice_date FROM client_invoices ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_latest_invoice_by_client(self, owner_name):
        """جلب آخر فاتورة لعميل/نقلة معينة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, owner_name, nolon, commission, mashal, rent, cash, invoice_date, net_amount, final_total 
            FROM client_invoices 
            WHERE owner_name = ? 
            ORDER BY id DESC LIMIT 1
        ''', (owner_name,))
        result = cursor.fetchone()
        conn.close()
        return result

    # --- طرق التعامل مع التقارير اليومية ---

    def save_daily_report(self, report_date, total_collection, remaining_profit, total_expenses):
        """حفظ أو تحديث تقرير يومي"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # التحقق من وجود تقرير لنفس اليوم
        cursor.execute('SELECT id FROM daily_reports WHERE report_date = ?', (report_date,))
        existing = cursor.fetchone()
        
        if existing:
            # تحديث التقرير الموجود
            cursor.execute('''
                UPDATE daily_reports 
                SET total_collection=?, remaining_profit=?, total_expenses=?, updated_at=CURRENT_TIMESTAMP
                WHERE report_date=?
            ''', (total_collection, remaining_profit, total_expenses, report_date))
        else:
            # إضافة تقرير جديد
            cursor.execute('''
                INSERT INTO daily_reports (report_date, total_collection, remaining_profit, total_expenses)
                VALUES (?, ?, ?, ?)\n            ''', (report_date, total_collection, remaining_profit, total_expenses))
        
        conn.commit()
        conn.close()

    def get_daily_report(self, report_date):
        """جلب تقرير يوم محدد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT report_date, total_collection, remaining_profit, total_expenses 
            FROM daily_reports 
            WHERE report_date = ?
        ''', (report_date,))
        result = cursor.fetchone()
        conn.close()
        return result


    def get_monthly_reports(self, year, month):
        """جلب تقارير شهر محدد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # تنسيق التاريخ للبحث (YYYY-MM-%)
        date_pattern = f"{year}-{month:02d}-%"
        
        cursor.execute('''
            SELECT report_date, total_collection, remaining_profit, total_expenses 
            FROM daily_reports 
            WHERE report_date LIKE ?
            ORDER BY report_date
        ''', (date_pattern,))
        results = cursor.fetchall()
        conn.close()
        return results

    def calculate_daily_totals(self, target_date):
        """حساب المجاميع اليومية من المعاملات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # حساب إجمالي التحصيل (المدفوع من البائعين - باستثناء السماح)
        # نستثني السماح لأنه ليس نقداً
        cursor.execute('''
            SELECT SUM(amount) FROM seller_transactions 
            WHERE status = 'مدفوع' AND date = ? AND item_name NOT LIKE '%سماح%'
        ''', (target_date,))
        total_collection = cursor.fetchone()[0] or 0.0
        
        # حساب إجمالي المصاريف
        cursor.execute('''
            SELECT SUM(amount) FROM expenses 
            WHERE expense_date = ?
        ''', (target_date,))
        total_expenses = cursor.fetchone()[0] or 0.0
        
        # حساب صافي ربح اليوم = إجمالي التحصيل - المصاريف
        remaining_profit = total_collection - total_expenses
        
        conn.close()
        
        return {
            'total_collection': total_collection,
            'remaining_profit': remaining_profit,
            'total_expenses': total_expenses
        }

    # --- طرق التعامل مع الفواتير المجمعة ---

    def get_uninvoiced_transfers(self, client_name):
        """جلب النقلات التي لم يتم عمل فاتورة لها لعميل معين"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Ensure invoice_id column exists
        try:
            cursor.execute('ALTER TABLE agriculture_transfers ADD COLUMN invoice_id INTEGER')
        except sqlite3.OperationalError:
            pass
            
        cursor.execute('''
            SELECT id, shipment_name, seller_name, item_name, unit_price, weight, count, equipment, transfer_type 
            FROM agriculture_transfers 
            WHERE shipment_name = ? AND transfer_type = 'in' AND (invoice_id IS NULL OR invoice_id = 0)
            ORDER BY created_at
        ''', (client_name,))
        results = cursor.fetchall()
        conn.close()
        return results

    def link_transfers_to_invoice(self, invoice_id, transfer_ids):
        """ربط النقلات بفاتورة معينة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Ensure invoice_id column exists
        try:
            cursor.execute('ALTER TABLE agriculture_transfers ADD COLUMN invoice_id INTEGER')
        except sqlite3.OperationalError:
            pass
            
        placeholders = ','.join(['?'] * len(transfer_ids))
        query = f'UPDATE agriculture_transfers SET invoice_id = ? WHERE id IN ({placeholders})'
        cursor.execute(query, [invoice_id] + transfer_ids)
        
        conn.commit()
        conn.close()

    def get_client_invoices(self, client_name):
        """جلب جميع فواتير عميل معين"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, owner_name, nolon, commission, mashal, rent, cash, invoice_date, net_amount, final_total 
            FROM client_invoices 
            WHERE owner_name = ? 
            ORDER BY invoice_date DESC, id DESC
        ''', (client_name,))
        results = cursor.fetchall()
        conn.close()
        return results

    def get_transfers_by_invoice_id(self, invoice_id):
        """جلب النقلات المرتبطة بفاتورة معينة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, shipment_name, seller_name, item_name, unit_price, weight, count, equipment, transfer_type 
            FROM agriculture_transfers 
            WHERE invoice_id = ?
            ORDER BY created_at
        ''', (invoice_id,))
        results = cursor.fetchall()
        conn.close()
        return results


    def update_transfer_price(self, client_name, seller_name, item_name, weight, count, new_price):
        """تحديث سعر النقلة في جدول ترحيل الزراعة (للبائع والعميل)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # تحديث السعر في السجلات التي تطابق المواصفات (سواء كانت in أو out)
            cursor.execute('''
                UPDATE agriculture_transfers 
                SET unit_price = ? 
                WHERE shipment_name = ? 
                AND seller_name = ? 
                AND item_name = ? 
                AND weight = ? 
                AND count = ?
            ''', (new_price, client_name, seller_name, item_name, weight, count))
            
            rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected
        except Exception as e:
            print(f"Error updating transfer price: {e}")
            return 0
        finally:
            conn.close()
