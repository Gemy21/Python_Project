
    # --- طرق التعامل مع تفاصيل النقلات ---

    def save_shipment_details(self, shipment_name, total_weight, total_count):
        """حفظ أو تحديث تفاصيل النقلة (الوزن والعدد الكلي)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # التأكد من وجود الجدول (للحالات التي لم يتم فيها استدعاء init_database)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shipment_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shipment_name TEXT NOT NULL UNIQUE,
                total_weight REAL DEFAULT 0,
                total_count REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('SELECT id FROM shipment_details WHERE shipment_name = ?', (shipment_name,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('UPDATE shipment_details SET total_weight=?, total_count=? WHERE shipment_name=?', 
                          (total_weight, total_count, shipment_name))
        else:
            cursor.execute('INSERT INTO shipment_details (shipment_name, total_weight, total_count) VALUES (?, ?, ?)', 
                          (shipment_name, total_weight, total_count))
            
        conn.commit()
        conn.close()

    def get_shipment_details(self, shipment_name):
        """جلب تفاصيل نقلة محددة مع حساب المباع منها"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 1. Get totals
        cursor.execute('SELECT total_weight, total_count FROM shipment_details WHERE shipment_name = ?', (shipment_name,))
        details = cursor.fetchone()
        
        if not details:
            return None
            
        total_weight, total_count = details
        
        # 2. Calculate sold amounts from agriculture_transfers
        # We look for "out" transfers (to sellers) for this shipment
        cursor.execute('''
            SELECT SUM(weight), SUM(count) 
            FROM agriculture_transfers 
            WHERE shipment_name = ? AND transfer_type = 'out'
        ''', (shipment_name,))
        sold = cursor.fetchone()
        
        sold_weight = sold[0] if sold[0] else 0.0
        sold_count = sold[1] if sold[1] else 0.0
        
        conn.close()
        
        return {
            'total_weight': total_weight,
            'total_count': total_count,
            'sold_weight': sold_weight,
            'sold_count': sold_count,
            'remaining_weight': total_weight - sold_weight,
            'remaining_count': total_count - sold_count
        }
