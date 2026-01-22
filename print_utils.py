
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import json
import tempfile
import sys
from datetime import datetime

# --- ReportLab Imports ---
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.colors import black, white, HexColor
except ImportError:
    pass # Will handle check in code

# --- Arabic Support ---
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC_SUPPORT = True
except ImportError:
    HAS_ARABIC_SUPPORT = False

# --- CONFIG ---
CONFIG_FILE = "config.json"
PAGE_WIDTH_CM = 11.0 # As requested
# PAGE_HEIGHT_CM = 30.0 # As requested
# Adjusting to A4 height or dynamic? User said "11 x 30 cm".
PAGE_HEIGHT_CM = 30.0 

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
    except:
        pass

# --- METRICS HELPERS ---
def cm_to_px(cm, dpi=96):
    # 1 inch = 2.54 cm
    return int(cm * dpi / 2.54)

def cm_to_pdf(cm):
    # 1 cm = 28.3465 points
    return cm * 28.3465

# --- ABSTRACT BACKEND ---
class DrawBackend:
    def draw_text(self, x_cm, y_cm, text, font_size, align='left', bold=False, color='#000000'):
        raise NotImplementedError

    def draw_rect(self, x_cm, y_cm, width_cm, height_cm, border_color='#000000', fill_color=None, border_width=1):
        raise NotImplementedError
    
    def draw_line(self, x1_cm, y1_cm, x2_cm, y2_cm, color='#000000', width=1):
        raise NotImplementedError
    
    def get_page_size_cm(self):
        return PAGE_WIDTH_CM, PAGE_HEIGHT_CM

# --- TKINTER BACKEND ---
class TkCanvasBackend(DrawBackend):
    def __init__(self, canvas: tk.Canvas, scale=1.0):
        self.canvas = canvas
        self.scale = scale # Zoom factor if needed (default 1 to match 96DPI approx)
        self.dpi = 110 # Slightly higher than 96 to look good on screen
        
    def _c2p(self, cm):
        return cm_to_px(cm, self.dpi) * self.scale

    def draw_text(self, x_cm, y_cm, text, font_size, align='left', bold=False, color='#000000'):
        if not text: return
        x = self._c2p(x_cm)
        y = self._c2p(y_cm)
        
        # Font mapping
        # Tk font size is usually negative for pixels or positive for points. 
        # Using negative to match px somewhat or just heuristics.
        # Heuristic: font_size (pt) -> px. 12pt ~= 16px.
        f_size = int(font_size * 1.3 * self.scale) 
        weight = 'bold' if bold else 'normal'
        font_spec = ('Simplified Arabic', f_size, weight) # Good for Arabic
        
        anchor_map = {'left': 'nw', 'center': 'n', 'right': 'ne'}
        anchor = anchor_map.get(align, 'nw')
        
        self.canvas.create_text(x, y, text=text, font=font_spec, fill=color, anchor=anchor)

    def draw_rect(self, x_cm, y_cm, width_cm, height_cm, border_color='#000000', fill_color=None, border_width=1):
        x1 = self._c2p(x_cm)
        y1 = self._c2p(y_cm)
        x2 = self._c2p(x_cm + width_cm)
        y2 = self._c2p(y_cm + height_cm)
        
        outline = border_color if border_color else ''
        fill = fill_color if fill_color else ''
        
        # Tkinter requires empty string for transparent, not None
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=outline, fill=fill, width=border_width)

    def draw_line(self, x1_cm, y1_cm, x2_cm, y2_cm, color='#000000', width=1):
        self.canvas.create_line(
            self._c2p(x1_cm), self._c2p(y1_cm),
            self._c2p(x2_cm), self._c2p(y2_cm),
            fill=color, width=width
        )

# --- REPORTLAB BACKEND ---
class ReportLabBackend(DrawBackend):
    def __init__(self, canvas_obj, height_cm):
        self.c = canvas_obj
        self.height_cm = height_cm
        self.font_name = 'Arial' # Will register
        self.font_name_bold = 'Arial-Bold'
        
        # Register Font
        self._register_font()

    def _register_font(self):
        try:
            # Try to find standard fonts
            # Windows font paths
            font_paths = [
                "C:\\Windows\\Fonts\\arial.ttf",
                "C:\\Windows\\Fonts\\tahoma.ttf",
                "C:\\Windows\\Fonts\\segoeui.ttf"
            ]
            font_path = None
            for p in font_paths:
                if os.path.exists(p):
                    font_path = p
                    break
            
            if font_path:
                pdfmetrics.registerFont(TTFont('Arial', font_path))
                self.font_name = 'Arial'
                
                # Check for bold
                base, ext = os.path.splitext(font_path)
                bold_path = base + "bd" + ext # arialbd.ttf
                if os.path.exists(bold_path):
                     pdfmetrics.registerFont(TTFont('Arial-Bold', bold_path))
                else:
                     self.font_name_bold = 'Arial' # Fallback
            else:
                self.font_name = 'Helvetica'
                self.font_name_bold = 'Helvetica-Bold'
                
        except Exception as e:
            print(f"Font registration warning: {e}")
            self.font_name = 'Helvetica' # Fallback

    def _reshape(self, text):
        if HAS_ARABIC_SUPPORT and text:
            try:
                reshaped = arabic_reshaper.reshape(str(text))
                return get_display(reshaped)
            except:
                return str(text)
        return str(text)

    def _y(self, y_cm):
        # Convert Top-Down Y (cm) to Bottom-Up PDF Y (points)
        return cm_to_pdf(self.height_cm - y_cm)

    def _x(self, x_cm):
        return cm_to_pdf(x_cm)

    def draw_text(self, x_cm, y_cm, text, font_size, align='left', bold=False, color='#000000'):
        if not text: return
        text = self._reshape(text)
        
        font = self.font_name_bold if bold else self.font_name
        self.c.setFont(font, font_size)
        self.c.setFillColor(HexColor(color))
        
        x = self._x(x_cm)
        y = self._y(y_cm) # Base line. But Tk draws from Top-Left. 
        # API expects y_cm to be the TOP of the text or baseline?
        # Tkinter anchor usually 'nw' (top-left).
        # ReportLab text is drawn from baseline. 
        # Need to adjust Y down by font size approx.
        y -= font_size # Approximation
        
        if align == 'left':
            self.c.drawString(x, y, text)
        elif align == 'center':
            self.c.drawCentredString(x, y, text)
        elif align == 'right':
            self.c.drawRightString(x, y, text)

    def draw_rect(self, x_cm, y_cm, width_cm, height_cm, border_color='#000000', fill_color=None, border_width=1):
        x = self._x(x_cm)
        y = self._y(y_cm + height_cm) # Bottom-Left Y
        w = cm_to_pdf(width_cm)
        h = cm_to_pdf(height_cm)
        
        stroke = 1 if border_color else 0
        fill = 1 if fill_color else 0
        
        if border_color: self.c.setStrokeColor(HexColor(border_color))
        if fill_color: self.c.setFillColor(HexColor(fill_color))
        
        self.c.setLineWidth(border_width * 0.5) # Scale width bits
        self.c.rect(x, y, w, h, fill=fill, stroke=stroke)

    def draw_line(self, x1_cm, y1_cm, x2_cm, y2_cm, color='#000000', width=1):
        self.c.setStrokeColor(HexColor(color))
        self.c.setLineWidth(width * 0.5)
        self.c.line(self._x(x1_cm), self._y(y1_cm), self._x(x2_cm), self._y(y2_cm))

# --- INVOICE RENDERER ---
class InvoiceDrawer:
    def __init__(self, backend: DrawBackend, data):
        self.b = backend
        self.data = data
        self.width_page, self.height_page = backend.get_page_size_cm()
        self.margin = 0.5
        self.width = self.width_page - 2 * self.margin
        
    def draw(self):
        y = self.margin
        
        # 1. Header
        y = self.draw_header(y)
        
        # 2. Client Info
        y = self.draw_client_info(y)
        
        # 3. Table
        y = self.draw_table(y)
        
        # 4. Footer
        self.draw_footer(y) # Draw at next Y or fixed bottom? Let's flow.
        
    def draw_header(self, y):
        cx = self.margin + self.width / 2
        right_x = self.margin + self.width
        
        # Logo placeholder
        self.b.draw_text(cx, y, "🍎", 24, 'center', color='#C0392B')
        y += 1.2
        self.b.draw_text(cx, y, "MOHEY BAJAR", 10, 'center', bold=True, color='#2C3E50')
        y += 0.8
        
        # Company Info (Right)
        # We'll center for this narrow receipt look or use right align?
        # User requested 11x30cm, which is narrow. Centered header is best.
        self.b.draw_text(cx, y, "خلفاء الحاج محي غريب بعجر", 12, 'center', bold=True)
        y += 0.6
        self.b.draw_text(cx, y, "تجارة الخضروات والفواكه", 10, 'center')
        y += 0.6
        self.b.draw_text(cx, y, "كفر الشيخ - فوه", 10, 'center')
        y += 0.6
        self.b.draw_text(cx, y, "ت / 0472976880", 10, 'center')
        y += 1.0
        
        self.b.draw_line(self.margin, y, self.margin + self.width, y, width=2)
        y += 0.2
        return y
        
    def draw_client_info(self, y):
        # Two columns: Date (Left), Name (Right)
        self.b.draw_rect(self.margin, y, self.width, 1.5, border_color='#000000', fill_color='#F4F6F7')
        
        # Right: Name
        tx_y = y + 0.3
        self.b.draw_text(self.margin + self.width - 0.2, tx_y, f"المطلوب من: {self.data['client_name']}", 10, 'right', bold=True)
        
        # Left: Date
        self.b.draw_text(self.margin + 0.2, tx_y + 0.6, f"التاريخ: {self.data['invoice_date']}", 9, 'left')
        
        return y + 1.8
        
    def draw_table(self, y):
        # Cols: Item, Price, Weight, Count, Amount
        # Widths ratios for 11cm width
        # Total Width = 10cm.
        # Amount: 2, Count: 1.5, Weight: 1.5, Price: 1.5, Item: 3.5
        
        cols = [
            # Header, Width, Align
            ("المبلغ", 2.0, 'center'),
            ("العدد", 1.5, 'center'),
            ("الوزن", 1.5, 'center'),
            ("السعر", 1.5, 'center'),
            ("الصنف", 3.5, 'right')
        ]
        
        # Header
        h_height = 0.8
        current_x = self.margin
        
        # Draw Headers (Left to Right logic, but Arabic is RTL visually)
        # We draw rectangles from Left to Right.
        # But columns order should be visually: Amount (Left) ... Item (Right)?
        # Or Item (Right) ... Amount (Left)?
        # Standard Arabic Table: Item (Right), ..., Amount (Left).
        # Let's reverse the list to draw from Right to Left?
        # No, let's keep array as [Amount, Count, Weight, Price, Item] if we want Left->Right drawing to map to visual Left->Right.
        # Visual: | Amount | Count | Weight | Price | Item |
        # X:      0       2       3.5      5       6.5    10
        
        x_positions = []
        cx = self.margin
        for title, w, align in cols:
            self.b.draw_rect(cx, y, w, h_height, fill_color='#34495E', border_color='white')
            # Text
            tx = cx + w/2 if align == 'center' else (cx + w - 0.2 if align == 'right' else cx + 0.2)
            self.b.draw_text(tx, y + 0.1, title, 10, align, bold=True, color='#FFFFFF')
            x_positions.append((cx, w, align))
            cx += w
            
        y += h_height
        
        # Rows
        row_height = 0.7
        # transactions structure: (item, weight, count, price, amount, type)
        # Cols map: Amount (4), Count (2), Weight (1), Price (3), Item (0)
        
        for i, trans in enumerate(self.data['transactions']):
            item = str(trans[0])
            weight = f"{trans[1]:.2f}" if trans[1] else "-"
            count = f"{trans[2]:.0f}" if trans[2] else "-"
            price = f"{trans[3]:.2f}" if trans[3] else "-"
            amount = f"{trans[4]:.2f}" if trans[4] else "0.00"
            
            vals = [amount, count, weight, price, item]
            
            bg = '#F2F3F4' if i % 2 == 0 else '#FFFFFF'
            
            cx = self.margin
            for idx, val in enumerate(vals):
                w = cols[idx][1]
                align = cols[idx][2]
                
                self.b.draw_rect(cx, y, w, row_height, fill_color=bg, border_color='#BDC3C7', border_width=0.5)
                
                tx = cx + w/2 if align == 'center' else (cx + w - 0.2 if align == 'right' else cx + 0.2)
                self.b.draw_text(tx, y + 0.1, str(val), 9, align)
                
                cx += w
            
            y += row_height
            
            # Check Page Break (simplified - just stop or new page not implemented in single page preview)
            if y > self.height_page - 5: # Leave space for footer
                 break 
                 
        return y + 0.5

    def draw_footer(self, y):
        # Totals
        # Goods Total
        self.draw_summary_row(y, "إجمالي البضاعة", f"{self.data['total_goods']:.2f}")
        y += 0.8
        
        # Deductions
        if self.data.get('total_deductions', 0) > 0:
             self.draw_summary_row(y, "الخصومات", f"{self.data['total_deductions']:.2f}", color='#E6B0AA')
             y += 0.8
             
        # Final
        self.draw_summary_row(y, "الصافي المستحق", f"{self.data['final_total']:.2f}", bold=True, bg='#D4EFDF')
        
    def draw_summary_row(self, y, label, value, bold=False, color='#FFFFFF', bg=None):
        h = 0.8
        self.b.draw_rect(self.margin, y, self.width, h, fill_color=bg)
        
        # Label Right
        self.b.draw_text(self.margin + self.width - 0.2, y+0.1, label, 10, 'right', bold=bold)
        
        # Value Left
        self.b.draw_text(self.margin + 2.0, y+0.1, value, 10, 'center', bold=True)


# --- WINDOW & API ---

class PrintPreviewWindow:
    def __init__(self, parent, invoice_data):
        self.data = invoice_data
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"معاينة وطباعة - {invoice_data['client_name']}")
        self.window.geometry("600x800")
        
        # Toolbar
        toolbar = tk.Frame(self.window, bg='#ECF0F1', pady=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        tk.Button(toolbar, text="🖨️ طباعة", command=self.print_pdf, bg='#27AE60', fg='white', font=('Arial', 11, 'bold')).pack(side=tk.RIGHT, padx=10)
        tk.Button(toolbar, text="💾 حفظ PDF", command=self.save_pdf_dialog, bg='#3498DB', fg='white', font=('Arial', 11, 'bold')).pack(side=tk.RIGHT, padx=10)
        
        # Canvas Scroll
        frame = tk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        hbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        
        self.canvas = tk.Canvas(frame, bg='#5D6D7E', 
                                yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        
        vbar.config(command=self.canvas.yview)
        hbar.config(command=self.canvas.xview)
        
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.draw_preview()
        
    def draw_preview(self):
        # Create a "Paper" on the canvas
        # 11cm x 30cm scaled
        backend = TkCanvasBackend(self.canvas)
        
        # Paper visual
        pw_px = backend._c2p(PAGE_WIDTH_CM)
        ph_px = backend._c2p(PAGE_HEIGHT_CM)
        
        # Background space
        margin_view = 20
        self.canvas.config(scrollregion=(0, 0, pw_px + 2*margin_view, ph_px + 2*margin_view))
        
        # The paper rectangle
        self.canvas.create_rectangle(margin_view, margin_view, margin_view+pw_px, margin_view+ph_px, fill='white', outline='black', width=1)
        
        # Make a sub-canvas offset logic or just shift drawing?
        # TkCanvasBackend needs offset support? 
        # Easier: Move all items after drawing or backend offset.
        # Let's add offsets to Backend.
        
        # Hack adjust backend to draw relative to paper
        origin_redraw = backend._c2p
        def offset_c2p(cm):
            return origin_redraw(cm) + margin_view
        backend._c2p = offset_c2p
        
        # Draw
        drawer = InvoiceDrawer(backend, self.data)
        drawer.draw()

    def generate_pdf(self, filepath):
        c = canvas.Canvas(filepath, pagesize=(cm_to_pdf(PAGE_WIDTH_CM), cm_to_pdf(PAGE_HEIGHT_CM)))
        backend = ReportLabBackend(c, PAGE_HEIGHT_CM)
        drawer = InvoiceDrawer(backend, self.data)
        drawer.draw()
        c.save()

    def save_pdf_dialog(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=f"فاتورة_{self.data['client_name']}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        )
        if filepath:
            try:
                self.generate_pdf(filepath)
                messagebox.showinfo("نجاح", "تم الحفظ بنجاح")
                os.startfile(filepath)
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل الحفظ: {e}")

    def print_pdf(self):
        try:
            # Create temp file
            fd, path = tempfile.mkstemp(suffix=".pdf")
            os.close(fd)
            
            self.generate_pdf(path)
            
            # Print using ShellExecute
            # "print" verb works if a PDF reader is associated
            try:
                win32api.ShellExecute(0, "print", path, None, ".", 0)
                # Note: This is async. We can't delete file immediately.
                # Maybe schedule deletion or leave in temp.
            except Exception as e:
                # Fallback to os.startfile
                os.startfile(path, "print")
                
        except Exception as e:
            messagebox.showerror("خطأ", f"فشلت الطباعة: {e}")

