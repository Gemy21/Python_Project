
import tkinter as tk
from tkinter import messagebox
from print_utils import BaseDrawer, BasePrintWindow, cm_to_pdf, format_clean_number

class ClientInvoiceDrawer(BaseDrawer):
    def draw_content(self):
        m = self.margin
        cw = self.cw
        ph = self.ph
        
        # --- 1. Header Area (Black & White) ---
        y = 0.5
        # Far Right
        self.b.draw_text(m + cw, y, "خلفاء الحاج محي غريب بعجر", 15, 'right', bold=True)
        self.b.draw_text(m + cw, y + 0.6, "لتجارة الخضروات والفواكه", 11, 'right', bold=True)
        self.b.draw_text(m + cw, y + 1.1, "كفر الشيخ - فوه - ميدان السوق الكبير\nت / 0472976880", 9, 'right')
        
        # Center: Logo & Name
        self.b.draw_text(m + cw/2, 0.4, "🍎", 22, 'center')
        self.b.draw_text(m + cw/2, 1.2, "MOHEY BAJAR", 11, 'center', bold=True)
        
        # Far Left: Phones
        self.b.draw_text(m, y, "محمد / 01014501415\nسعيد / 01009330363\nأحمد / 01007367830", 9, 'left', bold=True)
        
        y = 2.4
        self.b.draw_line(m, y, m + cw, y, width=1.5)
        y += 0.2
        
        # --- 2. Client & Date Box (As in photo) ---
        self.b.draw_rect(m, y, cw, 0.8, border='#000000') # Box for info
        self.b.draw_text(m + cw - 0.2, y + 0.15, f"الوارد من السيد /  {self.data['client_name']}", 11, 'right', bold=True)
        self.b.draw_text(m + 4.5, y + 0.15, "تحريراً في :", 10, 'right')
        self.b.draw_text(m + 0.2, y + 0.15, self.data['invoice_date'], 11, 'left', bold=True)
        y += 1.0
        
        # --- 3. Table Calculations ---
        items = [t for t in self.data['transactions'] if t[5] != "خصم"]
        num_items = len(items)
        y_table = y
        y_footer_top = ph - 4.5
        available_h = y_footer_top - y_table
        
        row_h = 0.7
        if num_items > 0:
            total_needed = (num_items + 1) * row_h
            if total_needed > available_h:
                row_h = available_h / (num_items + 1)
                row_h = max(0.45, row_h)

        # --- 4. Table (Strict B&W) ---
        cols = [
            ("المبلغ", 3.0, 'center'),
            ("العدد", 2.0, 'center'),
            ("الوزن", 2.0, 'center'),
            ("السعر", 2.0, 'center'),
            ("الصنف", cw - 9.0, 'right')
        ]
        
        # Header
        curr_x = m
        self.b.draw_rect(m, y_table, cw, row_h, fill='#D0D3D4', border='#000000')
        for title, w, align in cols:
            tx = curr_x + w/2 if align == 'center' else curr_x + w - 0.2
            self.b.draw_text(tx, y_table + (row_h*0.15), title, 10, align, bold=True)
            curr_x += w
        
        # Rows
        y_row = y_table + row_h
        for i, trans in enumerate(items):
            curr_x = m
            vals = [
                format_clean_number(trans[4]),
                format_clean_number(trans[2]),
                format_clean_number(trans[1]),
                format_clean_number(trans[3]),
                str(trans[0])
            ]
            for idx, val in enumerate(vals):
                w, align = cols[idx][1], cols[idx][2]
                self.b.draw_rect(curr_x, y_row, w, row_h, border='#000000', width=0.5)
                tx = curr_x + w/2 if align == 'center' else curr_x + w - 0.2
                self.b.draw_text(tx, y_row + (row_h*0.15), val, 9 if row_h > 0.6 else 8, align)
                curr_x += w
            y_row += row_h

        # --- 5. Footer (Mirroring the photo) ---
        y_foot = ph - 4.2
        self.b.draw_rect(m, y_foot, cw, 3.7, border='#000000', width=1.5) # Outer frame
        
        # --- Left Section: Deductions list ---
        lx, lw = m + 0.2, (cw * 0.45)
        # Headers/List
        exps = [t for t in self.data['transactions'] if t[5] == "خصم"]
        exp_y = y_foot + 0.3
        for exp in exps:
            self.b.draw_text(lx + lw - 0.5, exp_y, f"{exp[0]}", 10, 'right')
            # Value box
            self.b.draw_rect(lx + 0.2, exp_y - 0.1, 2.5, 0.6, border='#000000')
            self.b.draw_text(lx + 1.45, exp_y, format_clean_number(exp[4]), 10, 'center', bold=True)
            exp_y += 0.6
            
        # Total Deductions Box (Left)
        self.b.draw_rect(lx, y_foot + 3.0, lw, 0.6, fill='#E5E8E8', border='#000000')
        self.b.draw_text(lx + lw - 0.5, y_foot + 3.05, "الأجمـــــالـي", 10, 'right', bold=True)
        self.b.draw_text(lx + 1.45, y_foot + 3.05, format_clean_number(self.data['total_deductions']), 11, 'center', bold=True)
        
        # --- Right Section: Summary ---
        rx, rw = m + cw - (cw * 0.45) - 0.2, (cw * 0.45)
        summary_y = y_foot + 0.8
        
        # Goods Total
        self.b.draw_text(rx + rw - 0.5, summary_y, "الأجمـــــالـي", 11, 'right', bold=True)
        self.b.draw_rect(rx, summary_y - 0.1, 3.2, 0.7, border='#000000')
        self.b.draw_text(rx + 1.6, summary_y, format_clean_number(self.data['total_goods']), 11, 'center', bold=True)
        summary_y += 0.8
        
        # Commission
        comm_val = sum(t[4] for t in self.data['transactions'] if t[5] == "خصم")
        self.b.draw_text(rx + rw - 0.5, summary_y, "العمولــــــــة", 11, 'right', bold=True)
        self.b.draw_rect(rx, summary_y - 0.1, 3.2, 0.7, border='#000000')
        self.b.draw_text(rx + 1.6, summary_y, format_clean_number(comm_val), 11, 'center', bold=True)
        summary_y += 1.0
        
        # Net
        self.b.draw_text(rx + rw - 0.5, summary_y, "الصافـــــــــي", 13, 'right', bold=True)
        self.b.draw_rect(rx, summary_y - 0.1, 3.2, 0.8, border='#000000', fill='#F2F3F4')
        self.b.draw_text(rx + 1.6, summary_y + 0.05, format_clean_number(self.data['final_total']), 14, 'center', bold=True)

class ClientInvoicePrintWindow(BasePrintWindow):
    def __init__(self, parent, invoice_data):
        # A5 Landscape approx (21x15.5 cm)
        super().__init__(parent, f"طباعة فاتورة - {invoice_data['client_name']}", invoice_data, ClientInvoiceDrawer, page_size=(21, 15.5))
