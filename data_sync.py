import sqlite3
import json
import os
from datetime import datetime
import shutil

class DataSync:
    def __init__(self, db_name="company_accounts.db"):
        self.db_name = db_name
        self.exports_folder = "data_exports"
        
        # إنشاء مجلد التصدير إذا لم يكن موجوداً
        if not os.path.exists(self.exports_folder):
            os.makedirs(self.exports_folder)
    
    def get_connection(self):
        """إنشاء اتصال بقاعدة البيانات"""
        return sqlite3.connect(self.db_name)
    
    def export_all_data(self, filename=None):
        """
        تصدير جميع البيانات من قاعدة البيانات إلى ملف JSON
        
        Args:
            filename: اسم الملف (اختياري). إذا لم يتم تحديده، سيتم استخدام التاريخ الحالي
        
        Returns:
            str: مسار الملف المُصدَّر
        """
        if filename is None:
            # استخدام التاريخ والوقت الحالي كاسم للملف
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"backup_{timestamp}.json"
        
        filepath = os.path.join(self.exports_folder, filename)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # قائمة بجميع الجداول التي نريد تصديرها
        tables = [
            'sellers_accounts',
            'seller_transactions',
            'clients_accounts',
            'inventory_items',
            'meals',
            'agriculture_transfers',
            'expenses',
            'client_invoices'
        ]
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'database_name': self.db_name,
            'tables': {}
        }
        
        for table in tables:
            try:
                # جلب أسماء الأعمدة
                cursor.execute(f"PRAGMA table_info({table})")
                columns_info = cursor.fetchall()
                columns = [col[1] for col in columns_info]
                
                # جلب جميع البيانات
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                # تحويل البيانات إلى قائمة من القواميس
                table_data = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        row_dict[col] = row[i]
                    table_data.append(row_dict)
                
                export_data['tables'][table] = {
                    'columns': columns,
                    'data': table_data,
                    'row_count': len(table_data)
                }
                
                print(f"✓ تم تصدير {len(table_data)} سجل من جدول {table}")
                
            except sqlite3.OperationalError as e:
                print(f"⚠ تحذير: لم يتم العثور على جدول {table} - {e}")
                continue
        
        conn.close()
        
        # حفظ البيانات في ملف JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ تم تصدير البيانات بنجاح إلى: {filepath}")
        print(f"حجم الملف: {os.path.getsize(filepath) / 1024:.2f} KB")
        
        return filepath
    
    def import_data(self, filepath, merge_mode='update'):
        """
        استيراد البيانات من ملف JSON إلى قاعدة البيانات
        
        Args:
            filepath: مسار ملف JSON
            merge_mode: طريقة الدمج
                - 'replace': حذف البيانات القديمة واستبدالها بالجديدة
                - 'update': تحديث السجلات الموجودة وإضافة الجديدة
                - 'skip': تخطي السجلات الموجودة وإضافة الجديدة فقط
        
        Returns:
            dict: إحصائيات الاستيراد
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"الملف غير موجود: {filepath}")
        
        # قراءة البيانات من الملف
        with open(filepath, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        print(f"📥 بدء استيراد البيانات من: {filepath}")
        print(f"تاريخ التصدير: {import_data.get('export_date', 'غير محدد')}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {
            'tables_processed': 0,
            'rows_inserted': 0,
            'rows_updated': 0,
            'rows_skipped': 0,
            'errors': []
        }
        
        for table_name, table_info in import_data['tables'].items():
            print(f"\n⚙ معالجة جدول: {table_name}")
            
            columns = table_info['columns']
            data = table_info['data']
            
            # إزالة عمود id من الأعمدة للإدراج (سيتم إنشاؤه تلقائياً)
            insert_columns = [col for col in columns if col not in ['id', 'created_at', 'updated_at']]
            
            for row_dict in data:
                try:
                    if merge_mode == 'replace':
                        # حذف السجل القديم إذا كان موجوداً
                        if 'id' in row_dict and row_dict['id']:
                            cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_dict['id'],))
                        
                        # إدراج السجل الجديد
                        placeholders = ', '.join(['?' for _ in insert_columns])
                        columns_str = ', '.join(insert_columns)
                        values = [row_dict.get(col) for col in insert_columns]
                        
                        cursor.execute(
                            f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})",
                            values
                        )
                        stats['rows_inserted'] += 1
                    
                    elif merge_mode == 'update':
                        # محاولة تحديث السجل أولاً
                        if 'id' in row_dict and row_dict['id']:
                            # التحقق من وجود السجل
                            cursor.execute(f"SELECT id FROM {table_name} WHERE id = ?", (row_dict['id'],))
                            exists = cursor.fetchone()
                            
                            if exists:
                                # تحديث السجل الموجود
                                set_clause = ', '.join([f"{col} = ?" for col in insert_columns])
                                values = [row_dict.get(col) for col in insert_columns]
                                values.append(row_dict['id'])
                                
                                cursor.execute(
                                    f"UPDATE {table_name} SET {set_clause} WHERE id = ?",
                                    values
                                )
                                stats['rows_updated'] += 1
                            else:
                                # إدراج سجل جديد
                                placeholders = ', '.join(['?' for _ in insert_columns])
                                columns_str = ', '.join(insert_columns)
                                values = [row_dict.get(col) for col in insert_columns]
                                
                                cursor.execute(
                                    f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})",
                                    values
                                )
                                stats['rows_inserted'] += 1
                        else:
                            # إدراج سجل جديد (بدون id)
                            placeholders = ', '.join(['?' for _ in insert_columns])
                            columns_str = ', '.join(insert_columns)
                            values = [row_dict.get(col) for col in insert_columns]
                            
                            cursor.execute(
                                f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})",
                                values
                            )
                            stats['rows_inserted'] += 1
                    
                    elif merge_mode == 'skip':
                        # إدراج فقط إذا لم يكن السجل موجوداً
                        if 'id' in row_dict and row_dict['id']:
                            cursor.execute(f"SELECT id FROM {table_name} WHERE id = ?", (row_dict['id'],))
                            exists = cursor.fetchone()
                            
                            if exists:
                                stats['rows_skipped'] += 1
                                continue
                        
                        # إدراج سجل جديد
                        placeholders = ', '.join(['?' for _ in insert_columns])
                        columns_str = ', '.join(insert_columns)
                        values = [row_dict.get(col) for col in insert_columns]
                        
                        cursor.execute(
                            f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})",
                            values
                        )
                        stats['rows_inserted'] += 1
                
                except Exception as e:
                    error_msg = f"خطأ في جدول {table_name}: {str(e)}"
                    stats['errors'].append(error_msg)
                    print(f"⚠ {error_msg}")
            
            stats['tables_processed'] += 1
            print(f"✓ تمت معالجة جدول {table_name}")
        
        conn.commit()
        conn.close()
        
        # طباعة الإحصائيات
        print("\n" + "="*50)
        print("📊 إحصائيات الاستيراد:")
        print(f"  • الجداول المعالجة: {stats['tables_processed']}")
        print(f"  • السجلات المُدرجة: {stats['rows_inserted']}")
        print(f"  • السجلات المُحدثة: {stats['rows_updated']}")
        print(f"  • السجلات المتخطاة: {stats['rows_skipped']}")
        print(f"  • الأخطاء: {len(stats['errors'])}")
        print("="*50)
        
        return stats
    
    def create_daily_backup(self):
        """إنشاء نسخة احتياطية يومية"""
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"daily_backup_{today}.json"
        
        # التحقق من وجود نسخة احتياطية لهذا اليوم
        filepath = os.path.join(self.exports_folder, filename)
        if os.path.exists(filepath):
            print(f"⚠ توجد نسخة احتياطية لهذا اليوم بالفعل: {filepath}")
            # إنشاء نسخة بالوقت الحالي
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"backup_{timestamp}.json"
        
        return self.export_all_data(filename)
    
    def list_backups(self):
        """عرض قائمة بجميع النسخ الاحتياطية المتاحة"""
        if not os.path.exists(self.exports_folder):
            print("لا توجد نسخ احتياطية")
            return []
        
        backups = []
        for filename in os.listdir(self.exports_folder):
            if filename.endswith('.json'):
                filepath = os.path.join(self.exports_folder, filename)
                size = os.path.getsize(filepath) / 1024  # KB
                modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                backups.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size_kb': size,
                    'modified': modified
                })
        
        # ترتيب حسب التاريخ (الأحدث أولاً)
        backups.sort(key=lambda x: x['modified'], reverse=True)
        
        if backups:
            print("\n📦 النسخ الاحتياطية المتاحة:")
            print("-" * 80)
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup['filename']}")
                print(f"   التاريخ: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   الحجم: {backup['size_kb']:.2f} KB")
                print("-" * 80)
        else:
            print("لا توجد نسخ احتياطية")
        
        return backups
    
    def cleanup_old_backups(self, keep_days=30):
        """
        حذف النسخ الاحتياطية القديمة
        
        Args:
            keep_days: عدد الأيام للاحتفاظ بالنسخ الاحتياطية
        """
        if not os.path.exists(self.exports_folder):
            return
        
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        deleted_count = 0
        
        for filename in os.listdir(self.exports_folder):
            if filename.endswith('.json'):
                filepath = os.path.join(self.exports_folder, filename)
                if os.path.getmtime(filepath) < cutoff_date:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"🗑 تم حذف النسخة القديمة: {filename}")
        
        if deleted_count > 0:
            print(f"\n✓ تم حذف {deleted_count} نسخة احتياطية قديمة")
        else:
            print("✓ لا توجد نسخ احتياطية قديمة للحذف")


# دالة مساعدة للاستخدام السريع
def quick_export():
    """تصدير سريع للبيانات"""
    sync = DataSync()
    return sync.create_daily_backup()

def quick_import(filepath, merge_mode='update'):
    """استيراد سريع للبيانات"""
    sync = DataSync()
    return sync.import_data(filepath, merge_mode)


if __name__ == "__main__":
    # مثال على الاستخدام
    print("=" * 60)
    print("نظام مزامنة البيانات")
    print("=" * 60)
    
    sync = DataSync()
    
    # عرض القائمة
    while True:
        print("\n" + "=" * 60)
        print("اختر العملية:")
        print("1. تصدير البيانات (نسخة احتياطية)")
        print("2. استيراد البيانات")
        print("3. عرض النسخ الاحتياطية")
        print("4. حذف النسخ القديمة")
        print("5. خروج")
        print("=" * 60)
        
        choice = input("\nاختيارك: ").strip()
        
        if choice == '1':
            print("\n📤 تصدير البيانات...")
            filepath = sync.create_daily_backup()
            print(f"\n✓ تم التصدير بنجاح!")
            
        elif choice == '2':
            backups = sync.list_backups()
            if not backups:
                print("\n⚠ لا توجد نسخ احتياطية للاستيراد")
                continue
            
            print("\nاختر رقم النسخة الاحتياطية للاستيراد (أو 0 للإلغاء):")
            try:
                backup_num = int(input("الرقم: ").strip())
                if backup_num == 0:
                    continue
                if 1 <= backup_num <= len(backups):
                    filepath = backups[backup_num - 1]['filepath']
                    
                    print("\nاختر طريقة الدمج:")
                    print("1. تحديث (update) - تحديث السجلات الموجودة وإضافة الجديدة")
                    print("2. استبدال (replace) - حذف القديم واستبداله بالجديد")
                    print("3. تخطي (skip) - إضافة الجديد فقط وتخطي الموجود")
                    
                    merge_choice = input("\nاختيارك (1/2/3): ").strip()
                    merge_modes = {'1': 'update', '2': 'replace', '3': 'skip'}
                    merge_mode = merge_modes.get(merge_choice, 'update')
                    
                    print(f"\n📥 استيراد البيانات بطريقة {merge_mode}...")
                    stats = sync.import_data(filepath, merge_mode)
                    print("\n✓ تم الاستيراد بنجاح!")
                else:
                    print("⚠ رقم غير صحيح")
            except ValueError:
                print("⚠ يرجى إدخال رقم صحيح")
            
        elif choice == '3':
            sync.list_backups()
            
        elif choice == '4':
            try:
                days = int(input("\nعدد الأيام للاحتفاظ بالنسخ (افتراضي: 30): ").strip() or "30")
                sync.cleanup_old_backups(days)
            except ValueError:
                print("⚠ يرجى إدخال رقم صحيح")
            
        elif choice == '5':
            print("\n👋 إلى اللقاء!")
            break
        
        else:
            print("\n⚠ اختيار غير صحيح")
