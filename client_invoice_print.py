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
        
        # === محتوى الفاتورة (تصميم المعاينة) ===
        
        # الرأس (Matching Image)
        header_frame = tk.Frame(scrollable_frame, bg='white', pady=10)
        header_frame.pack(fill=tk.X, padx=40)
        
        # Left: Phones
        left_header = tk.Frame(header_frame, bg='white')
        left_header.pack(side=tk.LEFT)
        tk.Label(left_header, text="محمد / 01014501415\nسعيد / 01009330363\nأحمد / 01002367830", 
                 font=('Arial', 10, 'bold'), bg='white', justify='right').pack()

        # Center: Logo
        center_header = tk.Frame(header_frame, bg='white')
        center_header.pack(side=tk.TOP, pady=5)
        tk.Label(center_header, text="🍎", font=('Arial', 24), bg='white').pack()
        tk.Label(center_header, text="MOHEY BAJAR", font=('Arial', 12, 'bold'), bg='white').pack()

        # Right: Company
        right_header = tk.Frame(header_frame, bg='white')
        right_header.pack(side=tk.RIGHT)
        tk.Label(right_header, text="خلفاء الحاج محي غريب بعجر\nلتجارة الخضروات والفواكه", 
                 font=('Simplified Arabic', 14, 'bold'), bg='white', justify='right').pack()
        tk.Label(right_header, text="كفر الشيخ - فوه ميدان السوق الكبير\nت / 0472976880", 
                 font=('Simplified Arabic', 10, 'bold'), bg='white', justify='right').pack()

        tk.Frame(scrollable_frame, height=2, bg='black').pack(fill=tk.X, padx=40)

        # معلومات العميل والتاريخ
        info_frame = tk.Frame(scrollable_frame, bg='white', pady=10)
        info_frame.pack(fill=tk.X, padx=40)
        
        # التاريخ (Left)
        tk.Label(info_frame, text=f"تحريراً في : {self.data['invoice_date']}", 
                font=('Simplified Arabic', 12, 'bold'), bg='white').pack(side=tk.LEFT)
        
        # العميل (Right)
        tk.Label(info_frame, text=f"الوارد من السيد / {self.data['client_name']}", 
                font=('Simplified Arabic', 14, 'bold'), bg='white').pack(side=tk.RIGHT)
        
        # جدول المعاملات
        table_frame = tk.Frame(scrollable_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        
        # رأس الجدول (الصنف، السعر، الوزن، العدد، المبلغ)
        headers = ['الصنف', 'السعر', 'الوزن', 'العدد', 'المبلغ']
        for i, header in enumerate(headers):
            lbl = tk.Label(table_frame, text=header, font=('Simplified Arabic', 12, 'bold'), 
                          bg='white', relief=tk.SOLID, bd=1, pady=5)
            lbl.grid(row=0, column=i, sticky='nsew')
            table_frame.grid_columnconfigure(i, weight=1 if header == 'الصنف' else 0, minsize=80)
        
        # صفوف البيانات (بضاعة فقط)
        row_idx = 1
        for trans in self.data['transactions']:
            if trans[5] == "خصم": continue # تخطي الخصومات في الجدول العلوي
            
            vals = [
                str(trans[0]),
                f"{trans[3]:.2f}" if trans[3] else "",
                f"{trans[1]:.2f}" if trans[1] else "",
                f"{trans[2]:.0f}" if trans[2] else "",
                f"{trans[4]:.2f}"
            ]
            for col, val in enumerate(vals):
                lbl = tk.Label(table_frame, text=val, font=('Arial', 11), bg='white', relief=tk.SOLID, bd=1, pady=5)
                lbl.grid(row=row_idx, column=col, sticky='nsew')
            row_idx += 1
        
        # الإجماليات والخصومات (2-Box Layout)
        summary_container = tk.Frame(scrollable_frame, bg='white', pady=20)
        summary_container.pack(fill=tk.X, padx=40)

        # Right: Main Summary
        right_box = tk.Frame(summary_container, relief=tk.SOLID, bd=1, bg='white', padx=10, pady=5)
        right_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        def quick_row(parent, label, value, fsize=14, bg='white'):
            r = tk.Frame(parent, bg='white')
            r.pack(fill=tk.X, pady=2)
            tk.Label(r, text=value, font=('Arial', fsize, 'bold'), bg=bg, width=12, relief=tk.SUNKEN).pack(side=tk.LEFT)
            tk.Label(r, text=label, font=('Simplified Arabic', fsize, 'bold'), bg='white').pack(side=tk.RIGHT)

        quick_row(right_box, "الاجمالي", f"{self.data['total_goods']:.2f}")
        # استخراج العمولة كخصم منفصل للعرض
        comm_val = "0.00"
        for t in self.data['transactions']:
            if t[0] == "عمولة": comm_val = f"{t[4]:.2f}"
        
        quick_row(right_box, "العمولة", comm_val)
        tk.Frame(right_box, height=1, bg='black').pack(fill=tk.X, pady=5)
        quick_row(right_box, "الصافي", f"{self.data['final_total']:.2f}", fsize=20, bg='#EAFAF1')

        # Left: Reductions List
        left_box = tk.Frame(summary_container, relief=tk.SOLID, bd=1, bg='white', padx=10, pady=5)
        left_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        reds = [t for t in self.data['transactions'] if trans[5] == "خصم"]
        # Note: self.data['transactions'] usually contains strings like "نولون", "عمولة" etc as first element
        for t in self.data['transactions']:
            if t[5] == "خصم":
                row = tk.Frame(left_box, bg='white')
                row.pack(fill=tk.X)
                tk.Label(row, text=f"{t[4]:.2f}", font=('Arial', 11, 'bold'), bg='white').pack(side=tk.LEFT)
                tk.Label(row, text=t[0], font=('Simplified Arabic', 11), bg='white').pack(side=tk.RIGHT)
        
        tk.Frame(left_box, height=1, bg='black').pack(fill=tk.X, pady=2)
        row_tot = tk.Frame(left_box, bg='#FDEDEC')
        row_tot.pack(fill=tk.X)
        tk.Label(row_tot, text=f"{self.data['total_deductions']:.2f}", font=('Arial', 12, 'bold'), bg='#FDEDEC').pack(side=tk.LEFT)
        tk.Label(row_tot, text="الأجمالي", font=('Simplified Arabic', 12, 'bold'), bg='#FDEDEC').pack(side=tk.RIGHT)
        
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
        """حفظ الفاتورة كملف PDF - أبعاد 20×15 سم - مطابقة للتصميم"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.units import cm
            
            from print_utils import load_config, save_config
            config = load_config()
            save_dir = config.get('pdf_save_dir', '') or filedialog.askdirectory(title="اختر مجلد حفظ الفواتير")
            if not save_dir: return
            config['pdf_save_dir'] = save_dir
            save_config(config)
            
            safe_name = "".join([c for c in self.data['client_name'] if c.isalnum() or c in (' ', '_')]).strip()
            filepath = os.path.join(save_dir, f"فاتورة_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            
            # Fonts
            font_path = 'C:\\Windows\\Fonts\\arial.ttf'
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arabic', font_path))
                f_name = 'Arabic'
            else: f_name = 'Helvetica'
            
            pw, ph = 21 * cm, 15 * cm
            c = canvas.Canvas(filepath, pagesize=(pw, ph))
            
            # Header
            c.setFont(f_name, 10)
            c.drawString(1 * cm, ph - 1.5 * cm, "محمد / 01014501415\nسعيد / 01009330363\nأحمد / 01002367830")
            
            c.setFont(f_name, 14)
            c.drawRightString(pw - 1 * cm, ph - 1.5 * cm, "خلفاء الحاج محي غريب بعجر")
            c.setFont(f_name, 11)
            c.drawRightString(pw - 1 * cm, ph - 2.1 * cm, "لتجارة الخضروات والفواكه")
            c.setFont(f_name, 9)
            c.drawRightString(pw - 1 * cm, ph - 2.6 * cm, "كفر الشيخ - فوه ميدان السوق الكبير")
            
            c.setFont(f_name, 12)
            c.drawCentredString(pw/2, ph - 2 * cm, "MOHEY BAJAR")
            
            c.line(0.5 * cm, ph - 3 * cm, pw - 0.5 * cm, ph - 3 * cm)
            
            # Client & Date
            c.setFont(f_name, 10)
            c.drawString(1 * cm, ph - 3.6 * cm, f"تحريراً في : {self.data['invoice_date']}")
            c.drawRightString(pw - 1 * cm, ph - 3.6 * cm, f"الوارد من السيد / {self.data['client_name']}")
            
            # Table
            y = ph - 4.5 * cm
            headers = [("الصنف", 1 * cm), ("السعر", 7 * cm), ("الوزن", 10 * cm), ("العدد", 13 * cm), ("المبلغ", 16 * cm)]
            c.setFont(f_name, 10)
            for text, x in headers: c.drawString(x, y, text)
            y -= 0.3 * cm; c.line(0.8 * cm, y, pw - 0.8 * cm, y); y -= 0.5 * cm
            
            c.setFont(f_name, 9)
            for trans in self.data['transactions']:
                if trans[5] == "خصم": continue
                c.drawString(1 * cm, y, str(trans[0]))
                c.drawString(7 * cm, y, format_clean_number(trans[3]))
                c.drawString(10 * cm, y, format_clean_number(trans[1]))
                c.drawString(13 * cm, y, format_clean_number(trans[2]))
                c.drawString(16 * cm, y, format_clean_number(trans[4]))
                y -= 0.6 * cm
            
            c.line(0.8 * cm, y, pw - 0.8 * cm, y); y -= 1 * cm
            
            # Footer (2-Box)
            # Right Box
            c.setFont(f_name, 11)
            c.drawRightString(pw - 1 * cm, y, f"الاجمالي: {self.data['total_goods']:.2f}")
            y -= 0.6 * cm
            comm_val = 0
            for t in self.data['transactions']:
                if t[0] == "عمولة": comm_val = t[4]
            c.drawRightString(pw - 1 * cm, y, f"العمولة: {comm_val:.2f}")
            y -= 0.3 * cm; c.line(pw - 6 * cm, y, pw - 1 * cm, y); y -= 0.7 * cm
            c.setFont(f_name, 14)
            c.drawRightString(pw - 1 * cm, y, f"الصافي: {self.data['final_total']:.2f}")
            
            # Left Box
            y_l = y + 1.6 * cm
            c.setFont(f_name, 9)
            for t in self.data['transactions']:
                if t[5] == "خصم":
                    c.drawString(1 * cm, y_l, f"{t[0]}: {t[4]:.2f}")
                    y_l -= 0.5 * cm
            c.line(0.8 * cm, y_l, 5 * cm, y_l); y_l -= 0.6 * cm
            c.setFont(f_name, 10)
            c.drawString(1 * cm, y_l, f"الأجمالي: {self.data['total_deductions']:.2f}")

            c.save()
            messagebox.showinfo("نجاح", f"تم حفظ PDF بنجاح:\n{filepath}")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل حفظ PDF:\n{e}")
            
        except ImportError:
            messagebox.showerror("خطأ", "مكتبة reportlab غير مثبتة")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل حفظ PDF:\n{e}")
    
    def print_direct(self):
        """طباعة مباشرة - أبعاد 20×15 سم - مطابقة للتصميم المعتمد"""
        try:
            import win32print; import win32ui; import win32con
            
            printer_name = self.printer_var.get() or win32print.GetDefaultPrinter()
            if not printer_name:
                messagebox.showwarning("تنبيه", "الرجاء اختيار طابعة")
                return

            hprinter = win32print.OpenPrinter(printer_name)
            try:
                hdc = win32ui.CreateDC()
                hdc.CreatePrinterDC(printer_name)
                hdc.StartDoc("فاتورة عميل")
                hdc.StartPage()
                
                # أبعاد مخصصة (21×15 سم)
                # 21 cm width, 15 cm height
                pixel_width = int(21 * (horz_res / 21)) # Standard proportion
                pixel_height = int(15 * (vert_res / 15))
                
                margin_x = int(horz_res * 0.05); margin_y = int(vert_res * 0.05)
                width = horz_res - 2 * margin_x; y = margin_y
                
                # Fonts
                def create_f(size, weight=400):
                    return win32ui.CreateFont({"name": "Arial", "height": int(vert_res * size), "weight": weight, "charset": 178})
                
                f_title = create_f(0.045, 700); f_header = create_f(0.03, 700); f_normal = create_f(0.025)
                f_small = create_f(0.02)
                
                # Drawing functions
                def draw_r(text, x_right, y_pos, font):
                    hdc.SelectObject(font)
                    size = hdc.GetTextExtent(text)
                    hdc.TextOut(x_right - size[0], y_pos, text)
                    return size[1]
                
                def draw_l(text, x_left, y_pos, font):
                    hdc.SelectObject(font); hdc.TextOut(x_left, y_pos, text)
                    return hdc.GetTextExtent(text)[1]

                def draw_c(text, y_pos, font):
                    hdc.SelectObject(font); size = hdc.GetTextExtent(text)
                    hdc.TextOut((horz_res - size[0]) // 2, y_pos, text); return size[1]

                # --- Header (As in image) ---
                # Left: Phones
                phones = ["محمد / 01014501415", "سعيد / 01009330363", "أحمد / 01002367830"]
                y_phone = y
                for p in phones: y_phone += draw_l(p, margin_x, y_phone, f_small) + 5
                
                # Right: Company Info
                y_comp = y
                y_comp += draw_r("خلفاء الحاج محي غريب بعجر", horz_res - margin_x, y_comp, f_header) + 5
                y_comp += draw_r("لتجارة الخضروات والفواكه", horz_res - margin_x, y_comp, f_normal) + 5
                y_comp += draw_r("كفر الشيخ - فوه - ميدان السوق الكبير", horz_res - margin_x, y_comp, f_small) + 5
                y_comp += draw_r("ت / 0472976880", horz_res - margin_x, y_comp, f_small) + 5
                
                # Center: Logo Label
                draw_c("MOHEY BAJAR", y + int(vert_res * 0.05), f_header)
                
                y = max(y_phone, y_comp) + 20
                hdc.MoveTo(margin_x, y); hdc.LineTo(horz_res - margin_x, y); y += 20
                
                # --- Client Info ---
                draw_l(f"تحريراً في : {self.data['invoice_date']}", margin_x, y, f_normal)
                draw_r(f"الوارد من السيد / {self.data['client_name']}", horz_res - margin_x, y, f_header)
                y += int(vert_res * 0.04)
                
                # --- Transactions Table ---
                cols = [("الصنف", 0.35), ("السعر", 0.15), ("الوزن", 0.15), ("العدد", 0.15), ("المبلغ", 0.20)]
                hdc.SelectObject(f_header)
                hdc.MoveTo(margin_x, y); hdc.LineTo(horz_res - margin_x, y); y += 5
                
                current_x = margin_x
                x_pos_list = []
                for title, ratio in cols:
                    cw = int(width * ratio)
                    size = hdc.GetTextExtent(title)
                    hdc.TextOut(current_x + (cw - size[0]) // 2, y, title)
                    x_pos_list.append((current_x, cw))
                    current_x += cw
                y += int(vert_res * 0.035)
                hdc.MoveTo(margin_x, y); hdc.LineTo(horz_res - margin_x, y); y += 5
                
                # Data Rows (Goods)
                hdc.SelectObject(f_normal)
                for trans in self.data['transactions']:
                    if trans[5] == "خصم": continue
                    item = str(trans[0]); price = f"{trans[3]:.2f}"; weight = f"{trans[1]:.2f}"
                    count = f"{trans[2]:.0f}"; amount = f"{trans[4]:.2f}"
                    vals = [item, price, weight, count, amount]
                    for i, val in enumerate(vals):
                        sx, cw = x_pos_list[i]
                        size = hdc.GetTextExtent(str(val))
                        hdc.TextOut(sx + (cw - size[0]) // 2, y, str(val))
                    y += int(vert_res * 0.03)
                
                y += 10; hdc.MoveTo(margin_x, y); hdc.LineTo(horz_res - margin_x, y); y += 20
                
                # --- Footer (2-Box Logic) ---
                footer_y_start = y
                box_w = width // 2 - 20
                
                # Right Box: Summary
                box_r_x = horz_res - margin_x
                y_r = footer_y_start
                y_r += draw_r(f"الاجمالي: {self.data['total_goods']:.2f}", box_r_x, y_r, f_header) + 10
                
                comm_val = 0
                for t in self.data['transactions']:
                    if t[0] == "عمولة": comm_val = t[4]
                y_r += draw_r(f"العمولة: {comm_val:.2f}", box_r_x, y_r, f_header) + 15
                hdc.MoveTo(horz_res - margin_x - box_w, y_r); hdc.LineTo(horz_res - margin_x, y_r); y_r += 10
                draw_r(f"الصافي: {self.data['final_total']:.2f}", box_r_x, y_r, f_title)
                
                # Left Box: Expenses Details (Matching labels in image)
                y_l = footer_y_start
                for t in self.data['transactions']:
                    if t[5] == "خصم":
                        draw_l(t[0], margin_x + 100, y_l, f_normal)
                        draw_l(f"{t[4]:.2f}", margin_x, y_l, f_normal)
                        y_l += int(vert_res * 0.025)
                y_l += 5; hdc.MoveTo(margin_x, y_l); hdc.LineTo(margin_x + box_w, y_l); y_l += 5
                draw_l("الأجمالي", margin_x + 100, y_l, f_header)
                draw_l(f"{self.data['total_deductions']:.2f}", margin_x, y_l, f_header)

                hdc.EndPage(); hdc.EndDoc()
            finally:
                win32print.ClosePrinter(hprinter)
            messagebox.showinfo("نجاح", "تم إرسال الفاتورة للطابعة")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشلت الطباعة:\n{e}")
