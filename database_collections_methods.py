
    def get_all_collections(self):
        """جلب كل التحصيلات (المعاملات المدفوعة من البائعين)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT st.id, sa.seller_name, st.amount, st.date, st.note
            FROM seller_transactions st
            JOIN sellers_accounts sa ON st.seller_id = sa.id
            WHERE st.status = 'مدفوع'
            ORDER BY st.date DESC, st.id DESC
        ''')
        
        collections = cursor.fetchall()
        conn.close()
        return collections
    
    def get_all_expenses(self):
        """جلب كل المصروفات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, description, amount, expense_date, note
            FROM expenses
            ORDER BY expense_date DESC, id DESC
        ''')
        
        expenses = cursor.fetchall()
        conn.close()
        return expenses
