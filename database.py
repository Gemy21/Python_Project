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

    def get_seller_by_name(self, name):
        """البحث عن بائع بالاسم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, seller_name, remaining_amount, total_credit FROM sellers_accounts WHERE seller_name = ?', (name,))
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
