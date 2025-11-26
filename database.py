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
                remaining_amount REAL DEFAULT 0,
                total_credit REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("تم تهيئة قاعدة البيانات بنجاح")
    
    def get_all_sellers_accounts(self):
        """جلب جميع حسابات البائعين"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, seller_name, remaining_amount, total_credit FROM sellers_accounts ORDER BY seller_name')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def add_seller_account(self, seller_name, remaining_amount, total_credit):
        """إضافة حساب بائع جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sellers_accounts (seller_name, remaining_amount, total_credit)
            VALUES (?, ?, ?)
        ''', (seller_name, remaining_amount, total_credit))
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

