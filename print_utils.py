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
        center_frame.pack(side=tk.TOP, expand=True)
        
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
            printers = [p[2] for p in printers_info]
            
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
            
            # إعداد الخط العربي
            font_name = "Helvetica"
            try:
                # محاولة تسجيل خط Arial
                pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
                font_name = 'Arial'
            except:
                try:
                    # محاولة مسار ويندوز القياسي
                    pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
                    font_name = 'Arial'
                except:
                    pass
            
            # إنشاء PDF
            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            
            # الرأس
            c.setFont(font_name, 24)
            c.drawCentredString(width/2, height - 2*cm, "كشف حساب")
            
            c.setFont(font_name, 14)
            c.drawCentredString(width/2, height - 3*cm, "خلفاء الحاج محي غريب بعجر")
            
            # معلومات البائع
            y = height - 4.5*cm
            c.setFont(font_name, 12)
            c.drawRightString(width - 2*cm, y, f"البائع: {self.data['seller_name']}")
            c.drawString(2*cm, y, f"التاريخ: {self.data['invoice_date']}")
            
            # الرصيد السابق
            if self.data['old_balance'] != 0:
                y -= 1*cm
                c.drawRightString(width - 2*cm, y, f"الرصيد السابق: {self.data['old_balance']:.2f}")
            
            # جدول المعاملات
            y -= 2*cm
            
            # رؤوس الأعمدة (من اليمين لليسار)
            c.setFont(font_name, 10)
            c.drawRightString(width - 2*cm, y, "المبلغ")
            c.drawRightString(width - 5*cm, y, "العدد")
            c.drawRightString(width - 8*cm, y, "الوزن")
            c.drawRightString(width - 11*cm, y, "السعر")
            c.drawRightString(width - 14*cm, y, "الصنف")
            
            y -= 0.5*cm
            c.line(2*cm, y, width - 2*cm, y)
            
            # البيانات
            c.setFont(font_name, 10)
            for trans in self.data['transactions']:
                y -= 0.7*cm
                if y < 3*cm:
                    c.showPage()
                    y = height - 2*cm
                    c.setFont(font_name, 10)
                
                item = trans[0] or ""
                price = f"{trans[3]:.2f}" if trans[3] else ""
                weight = f"{trans[1]:.2f}" if trans[1] else ""
                count = f"{trans[2]:.0f}" if trans[2] else ""
                amount = f"{trans[4]:.2f}" if trans[4] else "0.00"
                
                c.drawRightString(width - 2*cm, y, amount)
                c.drawRightString(width - 5*cm, y, count)
                c.drawRightString(width - 8*cm, y, weight)
                c.drawRightString(width - 11*cm, y, price)
                c.drawRightString(width - 14*cm, y, item)
            
            # الإجماليات
            y -= 1.5*cm
            c.setFont(font_name, 12)
            c.drawRightString(width - 2*cm, y, f"إجمالي البضاعة: {self.data['total_goods']:.2f}")
            y -= 0.7*cm
            c.drawRightString(width - 2*cm, y, f"المدفوع: {self.data['total_paid']:.2f}")
            y -= 0.7*cm
            c.drawRightString(width - 2*cm, y, f"المتبقي: {self.data['final_balance']:.2f}")
            
            c.save()
            messagebox.showinfo("نجاح", f"تم حفظ PDF بنجاح:\n{filepath}")
            
        except ImportError:
            messagebox.showerror("خطأ", "مكتبة reportlab غير مثبتة")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل حفظ PDF:\n{e}")
    
    def print_direct(self):
        """طباعة مباشرة (Windows) باستخدام GDI لدعم العربية"""
        try:
            import win32print
            import win32ui
            import win32con
            
            printer_name = self.printer_var.get()
            if not printer_name:
                printer_name = win32print.GetDefaultPrinter()
            
            if not printer_name:
                messagebox.showwarning("تنبيه", "الرجاء اختيار طابعة")
                return

            hprinter = win32print.OpenPrinter(printer_name)
            
            try:
                hdc = win32ui.CreateDC()
                hdc.CreatePrinterDC(printer_name)
                
                hdc.StartDoc("فاتورة مبيعات")
                hdc.StartPage()
                
                # مقاييس الصفحة
                horz_res = hdc.GetDeviceCaps(8)  # HORZRES
                vert_res = hdc.GetDeviceCaps(10)  # VERTRES
                
                # هوامش
                margin_x = int(horz_res * 0.05)
                margin_y = int(vert_res * 0.05)
                width = horz_res - 2 * margin_x
                
                y = margin_y
                
                # الخطوط (Charset 178 = Arabic)
                font_title = win32ui.CreateFont({
                    "name": "Arial",
                    "height": int(vert_res * 0.03),
                    "weight": 700,
                    "charset": 178
                })
                
                font_header = win32ui.CreateFont({
                    "name": "Arial",
                    "height": int(vert_res * 0.02),
                    "weight": 700,
                    "charset": 178
                })
                
                font_normal = win32ui.CreateFont({
                    "name": "Arial",
                    "height": int(vert_res * 0.015),
                    "weight": 400,
                    "charset": 178
                })
                
                # دوال مساعدة للكتابة
                def draw_text_centered(text, y_pos, font):
                    hdc.SelectObject(font)
                    size = hdc.GetTextExtent(text)
                    x_pos = (horz_res - size[0]) // 2
                    hdc.TextOut(x_pos, y_pos, text)
                    return size[1]

                def draw_text_right(text, x_right, y_pos, font):
                    hdc.SelectObject(font)
                    size = hdc.GetTextExtent(text)
                    x_pos = x_right - size[0]
                    hdc.TextOut(x_pos, y_pos, text)
                    return size[1]
                
                def draw_text_left(text, x_left, y_pos, font):
                    hdc.SelectObject(font)
                    hdc.TextOut(x_left, y_pos, text)
                    return hdc.GetTextExtent(text)[1]

                # الرأس
                y += draw_text_centered("كشف حساب بائع", y, font_title) + int(vert_res * 0.005)
                y += draw_text_centered("خلفاء الحاج محي غريب بعجر", y, font_header) + int(vert_res * 0.01)
                
                # معلومات
                hdc.SelectObject(font_normal)
                line_height = hdc.GetTextExtent("A")[1]
                
                # التاريخ (يسار) والبائع (يمين)
                draw_text_left(f"التاريخ: {self.data['invoice_date']}", margin_x, y, font_normal)
                draw_text_right(f"البائع: {self.data['seller_name']}", horz_res - margin_x, y, font_normal)
                
                y += line_height * 2
                
                # جدول - الأعمدة من اليمين لليسار
                cols = [
                    ("الصنف", 0.35),
                    ("السعر", 0.15),
                    ("الوزن", 0.15),
                    ("العدد", 0.15),
                    ("المبلغ", 0.20)
                ]
                
                # رسم رأس الجدول
                current_x = horz_res - margin_x
                hdc.SelectObject(font_header)
                
                # خط علوي
                hdc.MoveTo(margin_x, y)
                hdc.LineTo(horz_res - margin_x, y)
                
                row_height = int(line_height * 1.5)
                text_y = y + (row_height - line_height) // 2
                
                x_positions = []
                
                for title, ratio in cols:
                    col_width = int(width * ratio)
                    col_center = current_x - (col_width // 2)
                    size = hdc.GetTextExtent(title)
                    hdc.TextOut(col_center - (size[0]//2), text_y, title)
                    
                    x_positions.append((current_x, col_width))
                    current_x -= col_width
                
                y += row_height
                hdc.MoveTo(margin_x, y)
                hdc.LineTo(horz_res - margin_x, y)
                
                # البيانات
                hdc.SelectObject(font_normal)
                
                for trans in self.data['transactions']:
                    # التحقق من نهاية الصفحة
                    if y > vert_res - margin_y - (line_height * 5):
                        hdc.EndPage()
                        hdc.StartPage()
                        y = margin_y
                    
                    item = str(trans[0])
                    price = f"{trans[3]:.2f}" if trans[3] else ""
                    weight = f"{trans[1]:.2f}" if trans[1] else ""
                    count = f"{trans[2]:.0f}" if trans[2] else ""
                    amount = f"{trans[4]:.2f}" if trans[4] else ""
                    
                    row_vals = [item, price, weight, count, amount]
                    
                    text_y = y + (row_height - line_height) // 2
                    
                    for i, val in enumerate(row_vals):
                        start_x, col_w = x_positions[i]
                        size = hdc.GetTextExtent(str(val))
                        center_x = start_x - (col_w // 2) - (size[0] // 2)
                        hdc.TextOut(center_x, text_y, str(val))
                    
                    y += row_height

                y += int(line_height * 0.5)
                hdc.MoveTo(margin_x, y)
                hdc.LineTo(horz_res - margin_x, y)
                y += int(line_height * 0.5)
                
                # الإجماليات
                hdc.SelectObject(font_header)
                
                def draw_total_row(label, value):
                    nonlocal y
                    draw_text_right(f"{label}: {value}", horz_res - margin_x, y, font_header)
                    y += int(line_height * 1.5)

                draw_total_row("إجمالي البضاعة", f"{self.data['total_goods']:.2f}")
                draw_total_row("المدفوع", f"{self.data['total_paid']:.2f}")
                draw_total_row("المتبقي", f"{self.data['final_balance']:.2f}")

                hdc.EndPage()
                hdc.EndDoc()
                
            finally:
                win32print.ClosePrinter(hprinter)
                
            messagebox.showinfo("نجاح", "تم إرسال الفاتورة للطابعة")

        except Exception as e:
            messagebox.showerror("خطأ", f"فشلت الطباعة:\n{e}")
