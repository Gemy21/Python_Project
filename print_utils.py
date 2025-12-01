"""
وحدة طباعة الفواتير
توفر وظائف حفظ PDF والطباعة المباشرة
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
from datetime import datetime

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")


class PrintPreviewWindow:
    """نافذة معاينة وطباعة الفاتورة"""
    
    def __init__(self, parent, invoice_data):
        """
        Parameters:
        - parent: النافذة الأب
        - invoice_data: dict يحتوي على:
            - seller_name: اسم البائع
            - invoice_date: تاريخ الفاتورة
            - old_balance: الرصيد السابق
            - transactions: قائمة المعاملات [(item, weight, count, price, amount, status), ...]
            - total_goods: إجمالي البضاعة
            - total_paid: إجمالي المدفوع
            - final_balance: المتبقي النهائي
        """
        self.parent = parent
        self.data = invoice_data
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"معاينة طباعة - {invoice_data['seller_name']}")
        self.window.geometry("768x756")
        self.window.configure(bg='white')
        
        # توسيط النافذة
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - 384
        y = (self.window.winfo_screenheight() // 2) - 378
        self.window.geometry(f"768x756+{x}+{y}")
        
        self.create_preview()
        
    def create_preview(self):
        """إنشاء واجهة المعاينة"""
        # إطار المعاينة (يحاكي ورقة A4)
        preview_frame = tk.Frame(self.window, bg='white', relief=tk.SOLID, bd=2)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas للتمرير
        canvas = tk.Canvas(preview_frame, bg='white')
        # استخدام tk.Scrollbar بدلاً من ttk.Scrollbar للتحكم في العرض
        scrollbar = tk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=canvas.yview, width=25, bg='#BDC3C7')
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # تفعيل السكرول بالماوس
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        self.window.bind("<MouseWheel>", _on_mousewheel)
        
        # === محتوى الفاتورة ===
        
        # الرأس (تصميم الكارت)
        header_frame = tk.Frame(scrollable_frame, bg='white', pady=10, relief=tk.SOLID, bd=2)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # تقسيم الرأس إلى 3 أقسام (يمين - وسط - يسار)
        
        # 1. اليمين: بيانات الشركة (اسم وعنوان)
        right_frame = tk.Frame(header_frame, bg='white')
        right_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(right_frame, text="خلفاء الحاج محي غريب بعجر", 
                font=('Simplified Arabic', 22, 'bold'), fg='#C0392B', bg='white').pack(anchor='e')
        
        tk.Label(right_frame, text="تجارة الخضروات والفواكه", 
                font=('Simplified Arabic', 18, 'bold'), fg='#C0392B', bg='white').pack(anchor='e')
                
        tk.Label(right_frame, text="كفر الشيخ - فوه - ميدان السوق الكبير", 
                font=('Simplified Arabic', 12, 'bold'), fg='#2C3E50', bg='white').pack(anchor='e')
                
        tk.Label(right_frame, text="ت / 0472976880", 
                font=('Arial', 12, 'bold'), fg='#2C3E50', bg='white').pack(anchor='e')

        # 2. اليسار: أرقام التليفون
        left_frame = tk.Frame(header_frame, bg='white')
        left_frame.pack(side=tk.LEFT, padx=20)
        
        phones = [
            ("محمد", "01014501415"),
            ("سعيد", "01009220363"),
            ("أحمد", "01007367830")
        ]
        
        for name, num in phones:
            p_frame = tk.Frame(left_frame, bg='white')
            p_frame.pack(anchor='w')
            tk.Label(p_frame, text=f"{name} / ", font=('Simplified Arabic', 12, 'bold'), bg='white').pack(side=tk.RIGHT)
            tk.Label(p_frame, text=num, font=('Arial', 12, 'bold'), bg='white').pack(side=tk.LEFT)

        # 3. الوسط: الشعار (نص مؤقت)
        center_frame = tk.Frame(header_frame, bg='white')
        center_frame.pack(side=tk.TOP, expand=True) # Using TOP/Expand to center it between left/right if possible, or just pack it.
        # Better approach for 3 columns in pack: Pack Left, Pack Right, then Pack remaining in Center.
        # Since we already packed Right and Left, the remaining space is in the middle.
        
        tk.Label(center_frame, text="🍎", font=('Arial', 40), bg='white', fg='#C0392B').pack()
        tk.Label(center_frame, text="MOHEY BAJAR", font=('Times New Roman', 14, 'bold'), bg='white', fg='#2C3E50').pack()
        
        # معلومات البائع والتاريخ
        info_frame = tk.Frame(scrollable_frame, bg='white')
        info_frame.pack(fill=tk.X, padx=40, pady=15)
        
        # البائع
        seller_frame = tk.Frame(info_frame, bg='#ECF0F1', relief=tk.SOLID, bd=1)
        seller_frame.pack(side=tk.RIGHT, padx=10, ipadx=15, ipady=8)
        tk.Label(seller_frame, text=f"البائع: {self.data['seller_name']}", 
                font=('Simplified Arabic', 16, 'bold'), bg='#ECF0F1').pack()
        
        # التاريخ
        date_frame = tk.Frame(info_frame, bg='#ECF0F1', relief=tk.SOLID, bd=1)
        date_frame.pack(side=tk.LEFT, padx=10, ipadx=15, ipady=8)
        tk.Label(date_frame, text=f"التاريخ: {self.data['invoice_date']}", 
                font=('Simplified Arabic', 14), bg='#ECF0F1').pack()
        
        # الرصيد السابق
        if self.data['old_balance'] != 0:
            balance_frame = tk.Frame(scrollable_frame, bg='#FFF9E6', relief=tk.SOLID, bd=2)
            balance_frame.pack(fill=tk.X, padx=40, pady=8)
            tk.Label(
                balance_frame,
                text=f"الرصيد السابق: {self.data['old_balance']:.2f} جنيه",
                font=('Simplified Arabic', 14, 'bold'),
                bg='#FFF9E6'
            ).pack(pady=8)
        
        # جدول المعاملات
        table_frame = tk.Frame(scrollable_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=15)
        
        # رأس الجدول
        headers = ['الصنف', 'السعر', 'الوزن', 'العدد', 'المبلغ']
        header_bg = '#34495E'
        
        for i, header in enumerate(headers):
            lbl = tk.Label(
                table_frame,
                text=header,
                font=('Simplified Arabic', 14, 'bold'),
                bg=header_bg,
                fg='white',
                relief=tk.RAISED,
                bd=1,
                pady=10
            )
            lbl.grid(row=0, column=i, sticky='nsew', padx=1, pady=1)
            table_frame.grid_columnconfigure(i, weight=1)
        
        # صفوف البيانات
        for idx, trans in enumerate(self.data['transactions'], start=1):
            # trans: (item_name, weight, count, price, amount, status)
            item_name = trans[0] if trans[0] else ""
            weight = f"{trans[1]:.2f}" if trans[1] else ""
            count = f"{trans[2]:.0f}" if trans[2] else ""
            price = f"{trans[3]:.2f}" if trans[3] else ""
            amount = f"{trans[4]:.2f}" if trans[4] else "0.00"
            status = trans[5] if trans[5] else ""
            
            # لون الصف حسب الحالة
            if status == "مدفوع":
                row_bg = '#FADBD8'
            elif status == "متبقي":
                row_bg = '#D6EAF8'
            else:
                row_bg = '#F8F9F9'
            
            # الترتيب الجديد: الصنف، السعر، الوزن، العدد، المبلغ
            values = [item_name, price, weight, count, amount]
            
            for col, val in enumerate(values):
                lbl = tk.Label(
                    table_frame,
                    text=val,
                    font=('Simplified Arabic', 13),
                    bg=row_bg,
                    relief=tk.SOLID,
                    bd=1,
                    pady=8
                )
                lbl.grid(row=idx, column=col, sticky='nsew', padx=1, pady=1)
        
        # الإجماليات
        totals_frame = tk.Frame(scrollable_frame, bg='#F4F6F7', relief=tk.SOLID, bd=2, pady=10)
        totals_frame.pack(fill=tk.X, padx=40, pady=20)
        
        def add_total_row(label, value, color='#FFFFFF'):
            row = tk.Frame(totals_frame, bg=totals_frame['bg'])
            row.pack(fill=tk.X, pady=5)
            
            tk.Label(row, text=value, font=('Simplified Arabic', 15, 'bold'), 
                    bg=color, relief=tk.SOLID, bd=1, width=18, pady=5).pack(side=tk.LEFT, padx=15)
            tk.Label(row, text=label, font=('Simplified Arabic', 14, 'bold'), 
                    bg=totals_frame['bg']).pack(side=tk.LEFT, padx=5)
        
        add_total_row("إجمالي الفاتورة:", f"{self.data['total_goods']:.2f} جنيه", '#FFF3CD')
        add_total_row("المدفوع:", f"{self.data['total_paid']:.2f} جنيه", '#F8D7DA')
        add_total_row("المتبقي (صافي):", f"{self.data['final_balance']:.2f} جنيه", '#D4EDDA')
        
        # الفوتر (الأزرار)
        buttons_frame = tk.Frame(self.window, bg='#ECF0F1', pady=15)
        buttons_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        btn_style = {
            'font': ('Playpen Sans Arabic', 13, 'bold'),
            'fg': 'white',
            'relief': tk.RAISED,
            'bd': 3,
            'cursor': 'hand2',
            'width': 15,
            'height': 2
        }
        
        tk.Button(
            buttons_frame,
            text="حفظ PDF",
            command=self.save_as_pdf,
            bg='#E74C3C',
            **btn_style
        ).pack(side=tk.RIGHT, padx=20)
        
        tk.Button(
            buttons_frame,
            text="طباعة مباشرة",
            command=self.print_direct,
            bg='#3498DB',
            **btn_style
        ).pack(side=tk.RIGHT, padx=10)
        
        # قائمة الطابعات
        self.printer_var = tk.StringVar()
        try:
            import win32print
            # جلب الطابعات المحلية والمتصلة بالشبكة
            flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            printers_info = win32print.EnumPrinters(flags)
            printers = [p[2] for p in printers_info] # الاسم موجود في الاندكس 2
            
            default_printer = win32print.GetDefaultPrinter()
        except Exception as e:
            print(f"Error listing printers: {e}")
            printers = []
            default_printer = ""
            
        if printers:
            self.printer_combo = ttk.Combobox(buttons_frame, textvariable=self.printer_var, values=printers, state='readonly', width=25, font=('Arial', 10))
            self.printer_combo.pack(side=tk.RIGHT, padx=5)
            if default_printer in printers:
                self.printer_combo.set(default_printer)
            elif printers:
                self.printer_combo.current(0)
        else:
            tk.Label(buttons_frame, text="لا توجد طابعات", bg='#ECF0F1', fg='red').pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="إغلاق",
            command=self.window.destroy,
            bg='#95A5A6',
            **btn_style
        ).pack(side=tk.LEFT, padx=20)
    
    def save_as_pdf(self):
        """حفظ الفاتورة كملف PDF"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.units import cm
            
            # تحديد مسار الحفظ
            config = load_config()
            save_dir = config.get('pdf_save_dir', '')
            
            # إذا لم يتم تحديد مجلد مسبقاً أو المجلد غير موجود، اطلب من المستخدم
            if not save_dir or not os.path.exists(save_dir):
                save_dir = filedialog.askdirectory(title="اختر مجلد حفظ الفواتير")
                if not save_dir:
                    return
                # حفظ المجلد المختار
                config['pdf_save_dir'] = save_dir
                save_config(config)
            
            # تكوين اسم الملف
            # التنسيق: فاتورة_اسم-البائع_التاريخ
            clean_date = datetime.now().strftime('%Y-%m-%d')
            safe_seller_name = "".join([c for c in self.data['seller_name'] if c.isalnum() or c in (' ', '_', '-')]).strip()
            base_name = f"فاتورة_{safe_seller_name}_{clean_date}"
            
            filename = f"{base_name}.pdf"
            full_path = os.path.join(save_dir, filename)
            
            # معالجة تكرار الاسم
            counter = 1
            while os.path.exists(full_path):
                filename = f"{base_name}_{counter}.pdf"
                full_path = os.path.join(save_dir, filename)
                counter += 1
            
            filepath = full_path
            
            # إنشاء PDF
            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            
            # محاولة تحميل خط عربي (اختياري)
            # يمكن تخطي هذا الجزء إذا لم يكن الخط متوفر
            
            # الرأس
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(width/2, height - 2*cm, "Sales Statement")
            
            c.setFont("Helvetica", 14)
            c.drawCentredString(width/2, height - 3*cm, "Kholafa El Hag")
            
            # معلومات البائع
            y = height - 4.5*cm
            c.setFont("Helvetica-Bold", 12)
            c.drawRightString(width - 2*cm, y, f"Seller: {self.data['seller_name']}")
            c.drawString(2*cm, y, f"Date: {self.data['invoice_date']}")
            
            # الرصيد السابق
            if self.data['old_balance'] != 0:
                y -= 1*cm
                c.drawString(2*cm, y, f"Previous Balance: {self.data['old_balance']:.2f} EGP")
            
            # جدول المعاملات
            y -= 2*cm
            # جدول المعاملات
            y -= 2*cm
            # الترتيب الجديد: الصنف، السعر، الوزن، العدد، المبلغ
            table_headers = ['Item', 'Price', 'Weight', 'Count', 'Amount']
            # تعديل المسافات (A4 width approx 21cm, margins 2cm -> 17cm usable)
            # Item(2), Price(8), Weight(11), Count(14), Amount(17)
            x_positions = [2*cm, 9*cm, 12*cm, 15*cm, 18*cm]
            
            c.setFont("Helvetica-Bold", 10)
            for i, header in enumerate(table_headers):
                c.drawString(x_positions[i], y, header)
            
            y -= 0.5*cm
            c.line(2*cm, y, width - 2*cm, y)
            
            # البيانات
            c.setFont("Helvetica", 9)
            for trans in self.data['transactions']:
                y -= 0.7*cm
                if y < 3*cm:  # صفحة جديدة
                    c.showPage()
                    y = height - 2*cm
                    c.setFont("Helvetica", 9)
                
                values = [
                    trans[0] or "",  # item
                    f"{trans[3]:.2f}" if trans[3] else "",  # price
                    f"{trans[1]:.2f}" if trans[1] else "",  # weight
                    f"{trans[2]:.0f}" if trans[2] else "",  # count
                    f"{trans[4]:.2f}" if trans[4] else "0.00",  # amount
                ]
                
                for i, val in enumerate(values):
                    c.drawString(x_positions[i], y, str(val))
            
            # الإجماليات
            y -= 1.5*cm
            c.setFont("Helvetica-Bold", 11)
            c.drawString(2*cm, y, f"Total Invoice: {self.data['total_goods']:.2f} EGP")
            y -= 0.7*cm
            c.drawString(2*cm, y, f"Paid: {self.data['total_paid']:.2f} EGP")
            y -= 0.7*cm
            c.drawString(2*cm, y, f"Remaining: {self.data['final_balance']:.2f} EGP")
            
            c.save()
            messagebox.showinfo("نجاح", f"تم حفظ PDF بنجاح:\n{filepath}")
            
        except ImportError:
            messagebox.showerror(
                "خطأ",
                "المكتبة 'reportlab' غير مثبتة.\nالرجاء تثبيتها باستخدام:\npip install reportlab"
            )
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل حفظ PDF:\n{e}")
    
    def print_direct(self):
        """طباعة مباشرة (Windows)"""
        try:
            import win32print
            import win32ui
            from PIL import Image, ImageDraw, ImageFont, ImageWin
            
            # إنشاء صورة للفاتورة
            img_width, img_height = 800, 1000
            img = Image.new('RGB', (img_width, img_height), 'white')
            draw = ImageDraw.Draw(img)
            
            # استخدام خط افتراضي
            try:
                font_title = ImageFont.truetype("arial.ttf", 32)
                font_header = ImageFont.truetype("arial.ttf", 20)
                font_normal = ImageFont.truetype("arial.ttf", 14)
            except:
                font_title = ImageFont.load_default()
                font_header = ImageFont.load_default()
                font_normal = ImageFont.load_default()
            
            y = 50
            
            # الرأس
            draw.text((img_width//2 - 100, y), "Sales Statement", fill='black', font=font_title)
            y += 50
            draw.text((img_width//2 - 80, y), "Kholafa El Hag", fill='black', font=font_header)
            y += 60
            
            # البائع والتاريخ
            draw.text((50, y), f"Seller: {self.data['seller_name']}", fill='black', font=font_normal)
            draw.text((500, y), f"Date: {self.data['invoice_date']}", fill='black', font=font_normal)
            y += 40
            
            # جدول مبسط
            # الترتيب الجديد: الصنف، السعر، الوزن، العدد، المبلغ
            header_text = f"{'Item':<20} | {'Price':<10} | {'Weight':<10} | {'Count':<10} | {'Amount':<10}"
            draw.text((50, y), header_text, fill='black', font=font_normal)
            y += 30
            draw.line((50, y, img_width - 50, y), fill='black', width=2)
            y += 20
            
            for trans in self.data['transactions'][:25]:  # أول 25 معاملة
                # trans: item, weight, count, price, amount, status
                item = str(trans[0])[:20]
                price = f"{trans[3]:.2f}" if trans[3] else "0"
                weight = f"{trans[1]:.2f}" if trans[1] else "0"
                count = f"{trans[2]:.0f}" if trans[2] else "0"
                amount = f"{trans[4]:.2f}" if trans[4] else "0"
                
                row_text = f"{item:<20} | {price:<10} | {weight:<10} | {count:<10} | {amount:<10}"
                draw.text((50, y), row_text, fill='black', font=font_normal)
                y += 25
            
            y += 30
            draw.text((50, y), f"Total: {self.data['total_goods']:.2f} EGP", fill='black', font=font_header)
            y += 30
            draw.text((50, y), f"Paid: {self.data['total_paid']:.2f} EGP", fill='black', font=font_header)
            y += 30
            draw.text((50, y), f"Remaining: {self.data['final_balance']:.2f} EGP", fill='black', font=font_header)
            
            # حفظ مؤقت
            temp_file = "temp_invoice.bmp"
            img.save(temp_file, "BMP")
            
            # الطباعة
            printer_name = self.printer_var.get()
            if not printer_name:
                # محاولة استخدام الافتراضية إذا لم يتم الاختيار
                printer_name = win32print.GetDefaultPrinter()
            
            if not printer_name:
                messagebox.showwarning("تنبيه", "الرجاء اختيار طابعة أو تعيين طابعة افتراضية")
                return

            hprinter = win32print.OpenPrinter(printer_name)
            
            try:
                hdc = win32ui.CreateDC()
                hdc.CreatePrinterDC(printer_name)
                hdc.StartDoc("Invoice")
                hdc.StartPage()
                
                # رسم الصورة
                bmp = Image.open(temp_file)
                dib = ImageWin.Dib(bmp)
                
                # تحجيم الصورة لتناسب الصفحة
                # الحصول على أبعاد الصفحة القابلة للطباعة
                horz_res = hdc.GetDeviceCaps(110) # HORZRES
                vert_res = hdc.GetDeviceCaps(111) # VERTRES
                
                # حساب الحجم المناسب (ملء العرض)
                # img_width, img_height هي أبعاد الصورة الأصلية
                # نريد عرض الصورة = عرض الصفحة
                
                scale = horz_res / img_width
                scaled_height = int(img_height * scale)
                
                # إذا كان الطول أكبر من الصفحة، قد نحتاج لتقليصه أو قصّه (هنا سنطبعه كما هو وقد يتم قصه)
                # الأفضل طباعته بحجم مناسب
                
                dib.draw(hdc.GetHandleOutput(), (0, 0, horz_res, scaled_height))
                
                hdc.EndPage()
                hdc.EndDoc()
            finally:
                win32print.ClosePrinter(hprinter)
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            messagebox.showinfo("نجاح", "تم إرسال الفاتورة للطابعة")
            
        except ImportError:
            messagebox.showerror(
                "خطأ",
                "المكتبات المطلوبة غير مثبتة.\nالرجاء تثبيت:\npip install pywin32 pillow"
            )
        except Exception as e:
            messagebox.showerror("خطأ", f"فشلت الطباعة:\n{e}")
