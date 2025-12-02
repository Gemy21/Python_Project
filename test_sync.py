"""
مثال بسيط لاختبار نظام المزامنة

هذا السكريبت يوضح كيفية استخدام نظام المزامنة بطريقة بسيطة
"""

from data_sync import DataSync
import os

def test_export():
    """اختبار التصدير"""
    print("\n" + "="*60)
    print("اختبار التصدير")
    print("="*60)
    
    sync = DataSync()
    filepath = sync.create_daily_backup()
    
    print(f"\n✓ تم التصدير بنجاح!")
    print(f"  الملف: {os.path.basename(filepath)}")
    print(f"  الحجم: {os.path.getsize(filepath) / 1024:.2f} KB")
    
    return filepath

def test_list_backups():
    """اختبار عرض النسخ الاحتياطية"""
    print("\n" + "="*60)
    print("النسخ الاحتياطية المتاحة")
    print("="*60)
    
    sync = DataSync()
    backups = sync.list_backups()
    
    if not backups:
        print("\n⚠ لا توجد نسخ احتياطية")
    else:
        print(f"\n✓ عدد النسخ: {len(backups)}")
        for i, backup in enumerate(backups[:5], 1):  # عرض أول 5 نسخ فقط
            print(f"\n{i}. {backup['filename']}")
            print(f"   التاريخ: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   الحجم: {backup['size_kb']:.2f} KB")

def test_import(filepath):
    """اختبار الاستيراد (تحذير: سيعدل قاعدة البيانات!)"""
    print("\n" + "="*60)
    print("اختبار الاستيراد")
    print("="*60)
    
    response = input("\n⚠ هذا سيعدل قاعدة البيانات. هل تريد المتابعة؟ (yes/no): ")
    if response.lower() != 'yes':
        print("تم الإلغاء.")
        return
    
    sync = DataSync()
    stats = sync.import_data(filepath, merge_mode='update')
    
    print(f"\n✓ تم الاستيراد بنجاح!")
    print(f"  الجداول المعالجة: {stats['tables_processed']}")
    print(f"  السجلات المُدرجة: {stats['rows_inserted']}")
    print(f"  السجلات المُحدثة: {stats['rows_updated']}")
    print(f"  السجلات المتخطاة: {stats['rows_skipped']}")
    if stats['errors']:
        print(f"  ⚠ الأخطاء: {len(stats['errors'])}")

def main():
    """القائمة الرئيسية"""
    print("\n" + "="*60)
    print("مثال اختبار نظام المزامنة")
    print("="*60)
    
    while True:
        print("\n" + "-"*60)
        print("اختر العملية:")
        print("1. تصدير البيانات")
        print("2. عرض النسخ الاحتياطية")
        print("3. اختبار الاستيراد (تحذير!)")
        print("4. خروج")
        print("-"*60)
        
        choice = input("\nاختيارك (1-4): ").strip()
        
        if choice == '1':
            filepath = test_export()
        elif choice == '2':
            test_list_backups()
        elif choice == '3':
            # عرض النسخ المتاحة أولاً
            sync = DataSync()
            backups = sync.list_backups()
            if not backups:
                print("\n⚠ لا توجد نسخ احتياطية للاستيراد")
                continue
            
            print("\nالنسخ المتاحة:")
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup['filename']}")
            
            try:
                num = int(input("\nاختر رقم النسخة (أو 0 للإلغاء): "))
                if num == 0:
                    continue
                if 1 <= num <= len(backups):
                    test_import(backups[num-1]['filepath'])
                else:
                    print("⚠ رقم غير صحيح")
            except ValueError:
                print("⚠ يرجى إدخال رقم صحيح")
        elif choice == '4':
            print("\n👋 إلى اللقاء!")
            break
        else:
            print("\n⚠ اختيار غير صحيح")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ تم الإيقاف بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}")
