"""
فئة طباعة فاتورة العملاء بأبعاد 20×15 سم
"""

import traceback
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
from utils import format_clean_number
from print_utils import load_config, save_config

# --- ReportLab & Arabic Support Imports ---
try:
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor
    import arabic_reshaper
    from bidi.algorithm import get_display
    import win32api
    HAS_LIB = True
except ImportError:
    HAS_LIB = False


class ClientInvoicePrintWindow:
    """نافذة معاينة وطباعة فاتورة العميل - أبعاد 20×15 سم"""
    
    def __init__(self, parent, invoice_data):
        self.parent = parent
        self.data = invoice_data
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"معاينة فاتورة - {invoice_data['client_name']}")
        self.window.geometry("900x700")
        self.window.configure(bg='white')
        
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - 450
        y = (self.window.winfo_screenheight() // 2) - 350
        self.window.geometry(f"900x700+{x}+{y}")
        
        self.create_preview()
        
    def create_preview(self):
        """إنشاء واجهة المعاينة (Canvas Preview)"""
        # (This remains as is to preserve the UI the user likes)
        # إطار المعاينة
        preview_frame = tk.Frame(self.window, bg='white', relief=tk.SOLID, bd=2)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(preview_frame, bg='white')
        scrollbar = tk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=canvas.yview, width=25, bg='#BDC3C7')
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.window.bind("<MouseWheel>", _on_mousewheel)
        
        # === محتوى الفاتورة (تصميم المعاينة) ===
        header_frame = tk.Frame(scrollable_frame, bg='white', pady=10)
        header_frame.pack(fill=tk.X, padx=40)
        
        left_header = tk.Frame(header_frame, bg='white')
        left_header.pack(side=tk.LEFT)
        tk.Label(left_header, text="محمد / 01014501415\nسعيد / 01009330363\nأحمد / 01002367830", 
                 font=('Arial', 10, 'bold'), bg='white', justify='right').pack()

        center_header = tk.Frame(header_frame, bg='white')
        center_header.pack(side=tk.TOP, pady=5)
        tk.Label(center_header, text="🍎", font=('Arial', 24), bg='white').pack()
        tk.Label(center_header, text="MOHEY BAJAR", font=('Arial', 12, 'bold'), bg='white').pack()

        right_header = tk.Frame(header_frame, bg='white')
        right_header.pack(side=tk.RIGHT)
        tk.Label(right_header, text="خلفاء الحاج محي غريب بعجر\nلتجارة الخضروات والفواكه", 
                 font=('Simplified Arabic', 14, 'bold'), bg='white', justify='right').pack()
        tk.Label(right_header, text="كفر الشيخ - فوه ميدان السوق الكبير\nت / 0472976880", 
                 font=('Simplified Arabic', 10, 'bold'), bg='white', justify='right').pack()

        tk.Frame(scrollable_frame, height=2, bg='black').pack(fill=tk.X, padx=40)

        info_frame = tk.Frame(scrollable_frame, bg='white', pady=10)
        info_frame.pack(fill=tk.X, padx=40)
        
        tk.Label(info_frame, text=f"تحريراً في : {self.data['invoice_date']}", 
                font=('Simplified Arabic', 12, 'bold'), bg='white').pack(side=tk.LEFT)
        tk.Label(info_frame, text=f"الوارد من السيد / {self.data['client_name']}", 
                font=('Simplified Arabic', 14, 'bold'), bg='white').pack(side=tk.RIGHT)
        
        table_frame = tk.Frame(scrollable_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        
        headers = ['الصنف', 'السعر', 'الوزن', 'العدد', 'المبلغ']
        for i, header in enumerate(headers):
            lbl = tk.Label(table_frame, text=header, font=('Simplified Arabic', 12, 'bold'), 
                          bg='white', relief=tk.SOLID, bd=1, pady=5)
            lbl.grid(row=0, column=i, sticky='nsew')
            table_frame.grid_columnconfigure(i, weight=1 if header == 'الصنف' else 0, minsize=80)
        
        row_idx = 1
        for trans in self.data['transactions']:
            if trans[5] == "خصم": continue 
            
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
        
        summary_container = tk.Frame(scrollable_frame, bg='white', pady=20)
        summary_container.pack(fill=tk.X, padx=40)

        right_box = tk.Frame(summary_container, relief=tk.SOLID, bd=1, bg='white', padx=10, pady=5)
        right_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        def quick_row(parent, label, value, fsize=14, bg='white'):
            r = tk.Frame(parent, bg='white')
            r.pack(fill=tk.X, pady=2)
            tk.Label(r, text=value, font=('Arial', fsize, 'bold'), bg=bg, width=12, relief=tk.SUNKEN).pack(side=tk.LEFT)
            tk.Label(r, text=label, font=('Simplified Arabic', fsize, 'bold'), bg='white').pack(side=tk.RIGHT)

        quick_row(right_box, "الاجمالي", f"{self.data['total_goods']:.2f}")
        comm_val = "0.00"
        for t in self.data['transactions']:
            if t[0] == "عمولة": comm_val = f"{t[4]:.2f}"
        
        quick_row(right_box, "العمولة", comm_val)
        tk.Frame(right_box, height=1, bg='black').pack(fill=tk.X, pady=5)
        quick_row(right_box, "الصافي", f"{self.data['final_total']:.2f}", fsize=20, bg='#EAFAF1')

        left_box = tk.Frame(summary_container, relief=tk.SOLID, bd=1, bg='white', padx=10, pady=5)
        left_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
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
        
        buttons_frame = tk.Frame(self.window, bg='#ECF0F1', pady=15)
        buttons_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        btn_style = {'font': ('Playpen Sans Arabic', 12, 'bold'), 'fg': 'white', 'relief': tk.RAISED, 'bd': 3, 'cursor': 'hand2', 'width': 15, 'height': 2}
        
        tk.Button(buttons_frame, text="حفظ PDF", command=self.save_as_pdf, bg='#E74C3C', **btn_style).pack(side=tk.RIGHT, padx=20)
        tk.Button(buttons_frame, text="طباعة مباشرة", command=self.print_direct, bg='#3498DB', **btn_style).pack(side=tk.RIGHT, padx=10)
        
        tk.Button(buttons_frame, text="إغلاق", command=self.window.destroy, bg='#95A5A6', **btn_style).pack(side=tk.LEFT, padx=20)
    
    def save_as_pdf(self, target_path=None):
        """حفظ الفاتورة كملف PDF - أبعاد 20×15 سم - مع دعم العربية وتنسيق الجداول"""
        try:
            if not HAS_LIB:
                raise ImportError("مكتبات reportlab أو arabic-reshaper غير مثبتة.")

            # --- Helper to fix Arabic text ---
            def res(text):
                if not text: return ""
                try:
                    return get_display(arabic_reshaper.reshape(str(text)))
                except: return str(text)

            # --- Helper to Draw Table Cell ---
            def draw_cell(c, x, y, width, height, text, font, size, align='center', bg_color=None, border_color='#000000'):
                if bg_color:
                    c.setFillColor(HexColor(bg_color))
                    c.rect(x, y, width, height, fill=1, stroke=0)
                
                c.setStrokeColor(HexColor(border_color))
                c.rect(x, y, width, height, fill=0, stroke=1)
                
                c.setFillColor(HexColor('#000000'))
                c.setFont(font, size)
                
                reshaped_text = res(text)
                
                # Center vertically approx
                text_y = y + (height - size)/2 + 2 # +2 adjustment
                
                if align == 'center': c.drawCentredString(x + width/2, text_y, reshaped_text)
                elif align == 'right': c.drawRightString(x + width - 5, text_y, reshaped_text)
                else: c.drawString(x + 5, text_y, reshaped_text)

            # Determine Path
            if target_path:
                filepath = target_path
            else:
                config = load_config()
                save_dir = config.get('pdf_save_dir', '') or filedialog.askdirectory(title="اختر مجلد حفظ الفواتير")
                if not save_dir: return
                config['pdf_save_dir'] = save_dir
                save_config(config)
                safe_name = "".join([c for c in self.data['client_name'] if c.isalnum() or c in (' ', '_')]).strip()
                filepath = os.path.join(save_dir, f"فاتورة_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

            # Setup Page
            pw, ph = 21 * cm, 15.5 * cm 
            c = canvas.Canvas(filepath, pagesize=(pw, ph))
            
            # Fonts
            font_path = 'C:\\Windows\\Fonts\\arial.ttf'
            font_bold_path = 'C:\\Windows\\Fonts\\arialbd.ttf'
            
            font_normal = 'Helvetica'
            font_bold = 'Helvetica-Bold'
            
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arabic', font_path))
                font_normal = 'Arabic'
            
            if os.path.exists(font_bold_path):
                pdfmetrics.registerFont(TTFont('Arabic-Bold', font_bold_path))
                font_bold = 'Arabic-Bold'
            elif font_normal == 'Arabic':
                font_bold = 'Arabic'

            # Define Layout
            margin = 0.5 * cm
            
            # --- Header ---
            c.setFont(font_bold, 14)
            c.drawRightString(pw - margin, ph - 1.5*cm, res("خلفاء الحاج محي غريب بعجر"))
            c.setFont(font_bold, 11)
            c.drawRightString(pw - margin, ph - 2.1*cm, res("لتجارة الخضروات والفواكه"))
            c.setFont(font_bold, 9)
            c.drawRightString(pw - margin, ph - 2.6*cm, res("كفر الشيخ - فوه - ميدان السوق الكبير"))
            c.setFont(font_bold, 10)
            c.drawRightString(pw - margin, ph - 3.1*cm, res("ت / 0472976880"))

            c.setFont(font_bold, 10)
            c.drawString(margin, ph - 1.5*cm, res("محمد / 01014501415"))
            c.drawString(margin, ph - 2.0*cm, res("سعيد / 01009330363"))
            c.drawString(margin, ph - 2.5*cm, res("أحمد / 01007367830"))

            c.setFont(font_normal, 24)
            c.setFillColor(HexColor('#C0392B'))
            c.drawCentredString(pw/2, ph - 2.0*cm, "🍎")
            c.setFont(font_bold, 12)
            c.setFillColor(HexColor('#2C3E50'))
            c.drawCentredString(pw/2, ph - 2.8*cm, "MOHEY BAJAR")
            
            c.setStrokeColor(HexColor('#000000'))
            c.setLineWidth(1.5)
            c.line(margin, ph - 3.5*cm, pw - margin, ph - 3.5*cm)

            # --- Client Info ---
            c.setFillColor(HexColor('#000000'))
            c.setFont(font_bold, 11)
            c.drawRightString(pw - margin, ph - 4.2*cm, res(f"الوارد من السيد / {self.data['client_name']}"))
            c.drawCentredString(4*cm, ph - 4.2*cm, res(f"تحريراً في : {self.data['invoice_date']}"))

            # --- Table ---
            # Cols Widths: Amount(3), Count(2.5), Weight(2.5), Price(2.5), Item(Remaining)
            # RTL Visual Order: Item(Right) ... Amount(Left)
            # X coords (Left -> Right): 
            # Margin .. Amount .. Count .. Weight .. Price .. Item .. Margin
            
            x_amnt = margin
            w_amnt = 3.0 * cm
            
            x_cnt = x_amnt + w_amnt
            w_cnt = 2.5 * cm
            
            x_wgt = x_cnt + w_cnt
            w_wgt = 2.5 * cm
            
            x_prc = x_wgt + w_wgt
            w_prc = 2.5 * cm
            
            x_itm = x_prc + w_prc
            w_itm = (pw - margin) - x_itm
            
            y = ph - 5.5 * cm
            h_row = 0.8 * cm
            
            # Header Row
            c.setFillColor(HexColor('#34495E'))
            c.rect(margin, y, pw - 2*margin, h_row, fill=1, stroke=1)
            
            c.setFillColor(HexColor('#FFFFFF'))
            c.setFont(font_bold, 11)
            
            def draw_ctr(text, x, w):
                c.drawCentredString(x + w/2, y + 0.25*cm, res(text))
                
            draw_ctr("المبلغ", x_amnt, w_amnt)
            draw_ctr("العدد", x_cnt, w_cnt)
            draw_ctr("الوزن", x_wgt, w_wgt)
            draw_ctr("السعر", x_prc, w_prc)
            draw_ctr("الصنف", x_itm, w_itm)
            
            y -= h_row
            
            # Data Rows
            # Table logic: iterate expenses later or separate? 
            # usually invoices show expenses at footer.
            
            row_h = 0.7 * cm
            c.setFont(font_normal, 10)
            
            for i, trans in enumerate(self.data['transactions']):
                if trans[5] == "خصم": continue
                
                bg = '#F8F9F9' if i % 2 == 0 else '#FFFFFF'
                
                draw_cell(c, x_amnt, y, w_amnt, row_h, format_clean_number(trans[4]), font_normal, 10, bg_color=bg)
                draw_cell(c, x_cnt, y, w_cnt, row_h, format_clean_number(trans[2]), font_normal, 10, bg_color=bg)
                draw_cell(c, x_wgt, y, w_wgt, row_h, format_clean_number(trans[1]), font_normal, 10, bg_color=bg)
                draw_cell(c, x_prc, y, w_prc, row_h, format_clean_number(trans[3]), font_normal, 10, bg_color=bg)
                draw_cell(c, x_itm, y, w_itm, row_h, str(trans[0]), font_normal, 10, bg_color=bg)
                
                y -= row_h
                if y < 4 * cm: break # Footer safeguard
                
            # --- Footer ---
            y_foot = 3.5 * cm
            
            # Right Box: Totals
            rx = pw/2 + 1*cm
            rw = (pw - margin) - rx
            
            # Goods
            draw_cell(c, rx, y_foot, rw/2, 0.7*cm, "إجمالي البضاعة", font_bold, 10, align='right', bg_color='#ECF0F1')
            draw_cell(c, rx+rw/2, y_foot, rw/2, 0.7*cm, format_clean_number(self.data['total_goods']), font_bold, 11)
            y_foot -= 0.7*cm
            
            # Commission
            comm_val = 0
            for t in self.data['transactions']:
                if t[0] == "عمولة": comm_val = t[4]
                
            draw_cell(c, rx, y_foot, rw/2, 0.7*cm, "العمولة", font_bold, 10, align='right', bg_color='#ECF0F1')
            draw_cell(c, rx+rw/2, y_foot, rw/2, 0.7*cm, format_clean_number(comm_val), font_bold, 11)
            y_foot -= 0.9*cm
            
            # Final Net
            draw_cell(c, rx, y_foot, rw, 0.9*cm, f"الصافي: {self.data['final_total']:.2f}", font_bold, 14, align='center', bg_color='#D4EFDF')
            
            # Left Box: Expenses Details
            lx = margin
            lw = (pw/2) - 1*cm
            y_foot = 3.5 * cm
            
            draw_cell(c, lx, y_foot, lw, 0.6*cm, "تفاصيل الخصومات", font_bold, 10, align='center', bg_color='#E5E8E8')
            y_foot -= 0.6*cm
            
            exps = [t for t in self.data['transactions'] if t[5] == "خصم"]
            for exp in exps:
                draw_cell(c, lx, y_foot, lw/2, 0.6*cm, exp[0], font_normal, 9, align='right') # Name
                draw_cell(c, lx+lw/2, y_foot, lw/2, 0.6*cm, format_clean_number(exp[4]), font_bold, 9, align='center') # Val
                y_foot -= 0.6*cm
                
            # Total Deductions
            draw_cell(c, lx, y_foot, lw, 0.7*cm, f"إجمالي الخصم: {self.data['total_deductions']:.2f}", font_bold, 10, bg_color='#FADBD8')

            c.save()
            
            if not target_path:
                messagebox.showinfo("نجاح", f"تم حفظ PDF بنجاح:\n{filepath}")
                os.startfile(filepath)
            
            return filepath
            
        except Exception as e:
            msg = f"فشل حفظ PDF:\n{e}"
            if not target_path: messagebox.showerror("خطأ", msg)
            else: raise Exception(msg)

    def print_direct(self):
        """طباعة مباشرة عن طريق إنشاء PDF ثم طباعته"""
        try:
            # Create Temp PDF
            fd, path = tempfile.mkstemp(suffix=".pdf")
            os.close(fd)
            
            # Generate PDF content
            generated_path = self.save_as_pdf(target_path=path)
            
            if generated_path and os.path.exists(generated_path):
                # Print using ShellExecute
                win32api.ShellExecute(0, "print", generated_path, None, ".", 0)
                # Note: File clean up is tricky with ShellExecute as it is async.
                # Leaving temp file is safer for now.
                messagebox.showinfo("طباعة", "تم إرسال الفاتورة للطابعة")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"فشلت الطباعة:\n{e}")

