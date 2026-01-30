
import tkinter as tk
from tkinter import messagebox
from print_utils import BaseDrawer, BasePrintWindow, cm_to_pdf

class SellerStatementDrawer(BaseDrawer):
    def draw(self):
        y = self.margin
        cx = self.margin + self.content_w / 2
        
        # 1. Header
        self.b.draw_text(cx, y, "كشف حساب بائع", 16, 'center', bold=True, color='#2C3E50')
        y += 1.0
        self.b.draw_text(cx, y, self.data['seller_name'], 14, 'center', bold=True)
        y += 0.8
        self.b.draw_text(cx, y, self.data['invoice_date'], 10, 'center')
        y += 1.2
        
        self.b.draw_line(self.margin, y, self.margin + self.content_w, y, width=2)
        y += 0.5
        
        # 2. Info (Seller & Balance)
        self.b.draw_rect(self.margin, y, self.content_w, 1.0, border='#7F8C8D', fill='#F4F6F7')
        self.b.draw_text(self.margin + self.content_w - 0.2, y + 0.3, "رصيد سابق:", 12, 'right', bold=True)
        self.b.draw_text(self.margin + 0.5, y + 0.3, f"{self.data['old_balance']:.2f}", 12, 'left', bold=True)
        y += 1.5
        
        # 3. Table Headers
        cols = [
            ("الإجمالي", 2.5, 'center'),
            ("السعر", 2.0, 'center'),
            ("العدد/وزن", 2.0, 'center'),
            ("الصنف", self.content_w - 6.5, 'right')
        ]
        
        curr_x = self.margin
        for title, w, align in cols:
            self.b.draw_rect(curr_x, y, w, 0.8, fill='#BDC3C7', border='#FFFFFF')
            tx = curr_x + w/2 if align == 'center' else curr_x + w - 0.2
            self.b.draw_text(tx, y + 0.15, title, 10, align, bold=True)
            curr_x += w
        y += 0.8
        
        # 4. Table Rows
        row_h = 0.7
        for i, trans in enumerate(self.data.get('transactions', [])):
            item = str(trans[0])
            weight = trans[1] or 0
            count = trans[2] or 0
            price = trans[3] or 0
            amount = trans[4] or 0
            status = trans[5]
            
            is_payment = status in ['مدفوع', 'سماح']
            bg = '#EAFAF1' if is_payment else ('#FDF2E9' if i % 2 == 0 else '#FFFFFF')
            
            if is_payment:
                self.b.draw_rect(self.margin, y, self.content_w, row_h, fill=bg, border='#BDC3C7')
                lbl = "دفعة" if status == 'مدفوع' else "خصم"
                txt = f"{lbl}: {amount:.2f}"
                self.b.draw_text(self.margin + self.content_w/2, y + 0.1, txt, 10, 'center', bold=True)
            else:
                qty_s = f"{weight}" if weight > 0 else f"{count:.0f}"
                vals = [f"{amount:.2f}", f"{price:.2f}", qty_s, item]
                
                curr_x = self.margin
                for idx, val in enumerate(vals):
                    w, align = cols[idx][1], cols[idx][2]
                    self.b.draw_rect(curr_x, y, w, row_h, fill=bg, border='#BDC3C7')
                    tx = curr_x + w/2 if align == 'center' else curr_x + w - 0.2
                    self.b.draw_text(tx, y + 0.1, val, 9, align)
                    curr_x += w
            y += row_h
            if y > self.h - 5: break
            
        # 5. Footer (Totals)
        y += 0.5
        self.draw_summary_row(y, "إجمالي البضاعة", f"{self.data['total_goods']:.2f}")
        y += 0.7
        self.draw_summary_row(y, "إجمالي المدفوع", f"{self.data['total_paid']:.2f}", color='#2980B9')
        y += 0.7
        if self.data.get('total_discount', 0) > 0:
            self.draw_summary_row(y, "إجمالي الخصم", f"{self.data['total_discount']:.2f}", color='#E74C3C')
            y += 0.7
            
        self.b.draw_line(self.margin, y, self.margin + self.content_w, y, width=2)
        y += 0.2
        self.b.draw_rect(self.margin, y, self.content_w, 1.2, fill='#F9E79F', border='#000000')
        self.b.draw_text(self.margin + self.content_w/2, y + 0.3, f"الصافي النهائي: {self.data['final_balance']:.2f}", 14, 'center', bold=True)

    def draw_summary_row(self, y, label, value, color='#000000'):
        self.b.draw_text(self.margin + self.content_w - 0.5, y, label, 10, 'right')
        self.b.draw_text(self.margin + 2.0, y, value, 10, 'center', bold=True, color=color)

class SellerStatementPrintWindow(BasePrintWindow):
    def __init__(self, parent, report_data):
        super().__init__(parent, f"كشف حساب - {report_data['seller_name']}", report_data, SellerStatementDrawer)
