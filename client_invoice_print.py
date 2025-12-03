"""
فئة طباعة فاتورة العملاء بأبعاد 20×15 سم
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime


class ClientInvoicePrintWindow:
    """نافذة معاينة وطباعة فاتورة العميل - أبعاد 20×15 سم"""
    
    def __init__(self, parent, invoice_data):
        """
        Parameters:
        - parent: النافذة الأب
        - invoice_data: dict يحتوي على:
            - client_name: اسم العميل
            - invoice_date: تاريخ الفاتورة
            - transactions: قائمة المعاملات [(item, weight, count, price, amount, status), ...]
            - total_goods: إجمالي البضاعة
            - total_deductions: إجمالي الخصومات
            - final_total: الصافي النهائي
        """
        self.parent = parent
        self.data = invoice_data
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"معاينة فاتورة - {invoice_data['client_name']}")
        self.window.geometry("900x700")
        self.window.configure(bg='white')
        
        # توسيط النافذة
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - 450
        y = (self.window.winfo_screenheight() // 2) - 350
        self.window.geometry(f"900x700+{x}+{y}")
        
        self.create_preview()
        
    def create_preview(self):
        """إنشاء واجهة المعاينة"""
        # إطار المعاينة
        preview_frame = tk.Frame(self.window, bg='white', relief=tk.SOLID, bd=2)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas للتمرير
        canvas = tk.Canvas(preview_frame, bg='white')
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
        
        # الرأس
        header_frame = tk.Frame(scrollable_frame, bg='#2C3E50', pady=15)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(header_frame, text="فاتورة عميل", 
                font=('Simplified Arabic', 24, 'bold'), fg='white', bg='#2C3E50').pack()
        
        tk.Label(header_frame, text="خلفاء الحاج محي غريب بعجر", 
                font=('Simplified Arabic', 16, 'bold'), fg='white', bg='#2C3E50').pack()
        
        # معلومات العميل والتاريخ
        info_frame = tk.Frame(scrollable_frame, bg='white')
        info_frame.pack(fill=tk.X, padx=40, pady=15)
        
        # العميل
        client_frame = tk.Frame(info_frame, bg='#ECF0F1', relief=tk.SOLID, bd=1)
        client_frame.pack(side=tk.RIGHT, padx=10, ipadx=15, ipady=8)
        tk.Label(client_frame, text=f"العميل: {self.data['client_name']}", 
                font=('Simplified Arabic', 14, 'bold'), bg='#ECF0F1').pack()
        
        # التاريخ
        date_frame = tk.Frame(info_frame, bg='#ECF0F1', relief=tk.SOLID, bd=1)
        date_frame.pack(side=tk.LEFT, padx=10, ipadx=15, ipady=8)
        tk.Label(date_frame, text=f"التاريخ: {self.data['invoice_date']}", 
                font=('Simplified Arabic', 12), bg='#ECF0F1').pack()
        
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
                font=('Simplified Arabic', 13, 'bold'),
                bg=header_bg,
                fg='white',
                relief=tk.RAISED,
                bd=1,
                pady=8
            )
            lbl.grid(row=0, column=i, sticky='nsew', padx=1, pady=1)
            table_frame.grid_columnconfigure(i, weight=1)
        
        # صفوف البيانات
        for idx, trans in enumerate(self.data['transactions'], start=1):
            item_name = trans[0] if trans[0] else ""
            weight = f"{trans[1]:.2f}" if trans[1] else ""
            count = f"{trans[2]:.0f}" if trans[2] else ""
            price = f"{trans[3]:.2f}" if trans[3] else ""
            amount = f"{trans[4]:.2f}" if trans[4] else "0.00"
            status = trans[5] if trans[5] else ""
            
            # لون الصف حسب الحالة
            if status == "خصم":
                row_bg = '#FADBD8'
            else:
                row_bg = '#D6EAF8'
            
            values = [item_name, price, weight, count, amount]
            
            for col, val in enumerate(values):
                lbl = tk.Label(
                    table_frame,
                    text=val,
                    font=('Simplified Arabic', 12),
                    bg=row_bg,
                    relief=tk.SOLID,
                    bd=1,
                    pady=6
                )
                lbl.grid(row=idx, column=col, sticky='nsew', padx=1, pady=1)
        
        # الإجماليات
        totals_frame = tk.Frame(scrollable_frame, bg='#F4F6F7', relief=tk.SOLID, bd=2, pady=10)
        totals_frame.pack(fill=tk.X, padx=40, pady=20)
        
        def add_total_row(label, value, color='#FFFFFF'):
            row = tk.Frame(totals_frame, bg=totals_frame['bg'])
            row.pack(fill=tk.X, pady=5)
            
            tk.Label(row, text=value, font=('Simplified Arabic', 14, 'bold'), 
                    bg=color, relief=tk.SOLID, bd=1, width=18, pady=5).pack(side=tk.LEFT, padx=15)
            tk.Label(row, text=label, font=('Simplified Arabic', 13, 'bold'), 
                    bg=totals_frame['bg']).pack(side=tk.LEFT, padx=5)
        
        add_total_row("إجمالي البضاعة:", f"{self.data['total_goods']:.2f} جنيه", '#FFF3CD')
        add_total_row("إجمالي الخصومات:", f"{self.data['total_deductions']:.2f} جنيه", '#F8D7DA')
        add_total_row("الصافي النهائي:", f"{self.data['final_total']:.2f} جنيه", '#D4EDDA')
        
        # الفوتر (الأزرار)
        buttons_frame = tk.Frame(self.window, bg='#ECF0F1', pady=15)
        buttons_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        btn_style = {
            'font': ('Playpen Sans Arabic', 12, 'bold'),
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
        """حفظ الفاتورة كملف PDF - أبعاد 20×15 سم"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.units import cm
            
            # تحديد مسار الحفظ
            from print_utils import load_config, save_config
            config = load_config()
            save_dir = config.get('pdf_save_dir', '')
            
            if not save_dir or not os.path.exists(save_dir):
                save_dir = filedialog.askdirectory(title="اختر مجلد حفظ الفواتير")
                if not save_dir:
                    return
                config['pdf_save_dir'] = save_dir
                save_config(config)
            
            # تكوين اسم الملف
            clean_date = datetime.now().strftime('%Y-%m-%d')
            safe_client_name = "".join([c for c in self.data['client_name'] if c.isalnum() or c in (' ', '_', '-')]).strip()
            base_name = f"فاتورة_عميل_{safe_client_name}_{clean_date}"
            
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
                pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
                font_name = 'Arial'
            except:
                try:
                    pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
                    font_name = 'Arial'
                except:
                    pass
            
            # إنشاء PDF
            # الفاتورة: عرض 20 سم × طول 15 سم
            page_width = 20 * cm
            page_height = 15 * cm
            
            c = canvas.Canvas(filepath, pagesize=(page_width, page_height))
            width, height = page_width, page_height
            
            # الرأس
            c.setFont(font_name, 14)
            c.drawCentredString(width/2, height - 1*cm, "فاتورة عميل")
            
            c.setFont(font_name, 10)
            c.drawCentredString(width/2, height - 1.7*cm, "خلفاء الحاج محي غريب بعجر")
            
            # معلومات العميل
            y = height - 2.5*cm
            c.setFont(font_name, 9)
            c.drawRightString(width - 0.5*cm, y, f"العميل: {self.data['client_name']}")
            c.drawString(0.5*cm, y, f"التاريخ: {self.data['invoice_date']}")
            
            # جدول المعاملات
            y -= 1*cm
            
            # رؤوس الأعمدة
            c.setFont(font_name, 8)
            col_positions = [
                (width - 0.5*cm, "المبلغ"),
                (width - 4*cm, "العدد"),
                (width - 7*cm, "الوزن"),
                (width - 10*cm, "السعر"),
                (width - 15*cm, "الصنف")
            ]
            
            for x_pos, header in col_positions:
                c.drawRightString(x_pos, y, header)
            
            y -= 0.3*cm
            c.line(0.3*cm, y, width - 0.3*cm, y)
            
            # البيانات
            c.setFont(font_name, 7)
            for trans in self.data['transactions']:
                y -= 0.5*cm
                if y < 2*cm:
                    c.showPage()
                    y = height - 1*cm
                    c.setFont(font_name, 7)
                
                item = trans[0] or ""
                price = f"{trans[3]:.2f}" if trans[3] else ""
                weight = f"{trans[1]:.2f}" if trans[1] else ""
                count = f"{trans[2]:.0f}" if trans[2] else ""
                amount = f"{trans[4]:.2f}" if trans[4] else "0.00"
                
                c.drawRightString(width - 0.5*cm, y, amount)
                c.drawRightString(width - 4*cm, y, count)
                c.drawRightString(width - 7*cm, y, weight)
                c.drawRightString(width - 10*cm, y, price)
                # تقصير اسم الصنف إذا كان طويلاً
                if len(item) > 20:
                    item = item[:20] + "..."
                c.drawRightString(width - 15*cm, y, item)
            
            # الإجماليات
            y -= 0.8*cm
            c.line(0.3*cm, y, width - 0.3*cm, y)
            y -= 0.5*cm
            c.setFont(font_name, 8)
            c.drawRightString(width - 0.5*cm, y, f"إجمالي البضاعة: {self.data['total_goods']:.2f}")
            y -= 0.4*cm
            c.drawRightString(width - 0.5*cm, y, f"إجمالي الخصومات: {self.data['total_deductions']:.2f}")
            y -= 0.4*cm
            c.setFont(font_name, 9)
            c.drawRightString(width - 0.5*cm, y, f"الصافي النهائي: {self.data['final_total']:.2f}")
            
            c.save()
            messagebox.showinfo("نجاح", f"تم حفظ PDF بنجاح:\n{filepath}")
            
        except ImportError:
            messagebox.showerror("خطأ", "مكتبة reportlab غير مثبتة")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل حفظ PDF:\n{e}")
    
    def print_direct(self):
        """طباعة مباشرة - أبعاد 20×15 سم"""
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
                
                hdc.StartDoc("فاتورة عميل")
                hdc.StartPage()
                
                # أبعاد مخصصة (20×15 سم)
                custom_width = int(20 * 37.8)  # 756 pixels
                custom_height = int(15 * 37.8)  # 567 pixels
                
                horz_res = custom_width
                vert_res = custom_height
                
                # هوامش أصغر
                margin_x = int(horz_res * 0.03)
                margin_y = int(vert_res * 0.03)
                width = horz_res - 2 * margin_x
                
                y = margin_y
                
                # الخطوط
                font_title = win32ui.CreateFont({
                    "name": "Arial",
                    "height": int(vert_res * 0.04),
                    "weight": 700,
                    "charset": 178
                })
                
                font_header = win32ui.CreateFont({
                    "name": "Arial",
                    "height": int(vert_res * 0.03),
                    "weight": 700,
                    "charset": 178
                })
                
                font_normal = win32ui.CreateFont({
                    "name": "Arial",
                    "height": int(vert_res * 0.025),
                    "weight": 400,
                    "charset": 178
                })
                
                # دوال مساعدة
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
                y += draw_text_centered("فاتورة عميل", y, font_title) + int(vert_res * 0.01)
                y += draw_text_centered("خلفاء الحاج محي غريب بعجر", y, font_header) + int(vert_res * 0.02)
                
                # معلومات
                hdc.SelectObject(font_normal)
                line_height = hdc.GetTextExtent("A")[1]
                
                draw_text_left(f"التاريخ: {self.data['invoice_date']}", margin_x, y, font_normal)
                draw_text_right(f"العميل: {self.data['client_name']}", horz_res - margin_x, y, font_normal)
                
                y += line_height * 2
                
                # جدول
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
                    y += int(line_height * 1.3)

                draw_total_row("إجمالي البضاعة", f"{self.data['total_goods']:.2f}")
                draw_total_row("إجمالي الخصومات", f"{self.data['total_deductions']:.2f}")
                draw_total_row("الصافي النهائي", f"{self.data['final_total']:.2f}")

                hdc.EndPage()
                hdc.EndDoc()
                
            finally:
                win32print.ClosePrinter(hprinter)
                
            messagebox.showinfo("نجاح", "تم إرسال الفاتورة للطابعة")

        except Exception as e:
            messagebox.showerror("خطأ", f"فشلت الطباعة:\n{e}")
