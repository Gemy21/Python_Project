
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import tempfile
import sys
import logging
from datetime import datetime

# --- Logging ---
logging.basicConfig(level=logging.INFO, filename="printing.log")

# --- ReportLab & Arabic Support ---
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor, black, white, gray
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    import win32print
    import win32api
    HAS_WIN32 = True
except:
    HAS_WIN32 = False

# --- Font Registration ---
class FontManager:
    _registered = False
    @classmethod
    def register(cls):
        if cls._registered or not HAS_REPORTLAB: return
        paths = ["C:\\Windows\\Fonts\\arial.ttf", "C:\\Windows\\Fonts\\tahoma.ttf", "C:\\Windows\\Fonts\\times.ttf"]
        path = next((p for p in paths if os.path.exists(p)), None)
        if path:
            try:
                pdfmetrics.registerFont(TTFont('ArabicFont', path))
                bold_path = path.replace(".ttf", "bd.ttf") if "arial" in path else path
                if not os.path.exists(bold_path): bold_path = path
                pdfmetrics.registerFont(TTFont('ArabicFontBold', bold_path))
                cls._registered = True
            except: pass

def cm_to_pdf(cm): return cm * 28.3465

def fix_text(text):
    if not text: return ""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except: return str(text)

# --- BACKENDS ---

class DrawBackend:
    def get_page_size_cm(self): pass
    def draw_text(self, x, y, text, size, align='left', bold=False, color='#000000'): pass
    def draw_line(self, x1, y1, x2, y2, color='#000000', width=1): pass
    def draw_rect(self, x, y, w, h, border='#000000', fill=None, width=1): pass

class TkCanvasBackend(DrawBackend):
    def __init__(self, canvas_obj, pw, ph):
        self.canvas, self.pw, self.ph = canvas_obj, pw, ph
        self.scale = 35
        self.ox, self.oy = 0, 0

    def _c2p(self, cm): return cm * self.scale
    def get_page_size_cm(self): return (self.pw, self.ph)
    
    def draw_text(self, x, y, text, size, align='left', bold=False, color='#000000'):
        lines = str(text).split('\n')
        curr_y = y
        line_height_cm = (size * 1.3) / 28.34
        for line in lines:
            f = ("Arial", int(size * 1.1), 'bold' if bold else 'normal')
            px, py = self._c2p(x) + self.ox, self._c2p(curr_y) + self.oy
            anchor = {'left': 'nw', 'center': 'n', 'right': 'ne'}[align]
            self.canvas.create_text(px, py, text=line, font=f, fill=color, anchor=anchor)
            curr_y += line_height_cm

    def draw_line(self, x1, y1, x2, y2, color='#000000', width=1):
        self.canvas.create_line(self._c2p(x1)+self.ox, self._c2p(y1)+self.oy, self._c2p(x2)+self.ox, self._c2p(y2)+self.oy, fill=color, width=width)

    def draw_rect(self, x, y, w, h, border='#000000', fill=None, width=1):
        # Fix: use outline instead of border for create_rectangle
        self.canvas.create_rectangle(self._c2p(x)+self.ox, self._c2p(y)+self.oy, self._c2p(x+w)+self.ox, self._c2p(y+h)+self.oy, outline=border or "", fill=fill or "", width=width)

class ReportLabBackend(DrawBackend):
    def __init__(self, canvas_obj, pw, ph):
        self.c, self.pw, self.ph = canvas_obj, pw, ph
        FontManager.register()

    def get_page_size_cm(self): return (self.pw, self.ph)
    def _y(self, y_cm): return cm_to_pdf(self.ph - y_cm)
    def _x(self, x_cm): return cm_to_pdf(x_cm)

    def draw_text(self, x, y, text, size, align='left', bold=False, color='#000000'):
        if not text: return
        self.c.setFont('ArabicFontBold' if bold else 'ArabicFont', size)
        self.c.setFillColor(HexColor(color))
        lines = str(text).split('\n')
        curr_y = y
        line_height_cm = (size * 1.3) / 28.34
        for line in lines:
            t = fix_text(line)
            py, px = self._y(curr_y) - (size * 0.8), self._x(x)
            if align == 'left': self.c.drawString(px, py, t)
            elif align == 'center': self.c.drawCentredString(px, py, t)
            elif align == 'right': self.c.drawRightString(px, py, t)
            curr_y += line_height_cm

    def draw_line(self, x1, y1, x2, y2, color='#000000', width=1):
        self.c.setStrokeColor(HexColor(color)); self.c.setLineWidth(width*0.5)
        self.c.line(self._x(x1), self._y(y1), self._x(x2), self._y(y2))

    def draw_rect(self, x, y, w, h, border='#000000', fill=None, width=1):
        if fill: self.c.setFillColor(HexColor(fill))
        if border: self.c.setStrokeColor(HexColor(border))
        self.c.setLineWidth(width*0.5)
        self.c.rect(self._x(x), self._y(y+h), cm_to_pdf(w), cm_to_pdf(h), fill=1 if fill else 0, stroke=1 if border else 0)

# --- BASE DRAWER ---

class BaseDrawer:
    def __init__(self, backend, data):
        self.b, self.data = backend, data
        self.pw, self.ph = backend.get_page_size_cm()
        self.margin = 0.5
        self.cw = self.pw - 2 * self.margin
    def draw(self):
        try: self.draw_content()
        except Exception as e: logging.error(f"Draw error: {e}"); print(f"Draw error: {e}")
    def draw_content(self): raise NotImplementedError()

# --- UTILS ---

def silent_print_pdf(pdf_path, printer_name=None):
    if not os.path.exists(pdf_path): return False
    try:
        if HAS_WIN32:
            try:
                if printer_name: win32print.SetDefaultPrinter(printer_name)
                win32api.ShellExecute(0, "print", pdf_path, None, ".", 0)
                return True
            except: os.startfile(pdf_path); return False
        else: os.startfile(pdf_path); return False
    except: return False

def format_clean_number(v):
    try:
        n = float(v)
        if n == int(n): return f"{int(n):,}"
        return f"{n:,.2f}".rstrip('0').rstrip('.')
    except: return str(v)

# --- WINDOW ---

class BasePrintWindow:
    def __init__(self, parent, title, data, drawer_class, page_size=(11, 29.7)):
        self.data, self.drawer_class, self.pw, self.ph = data, drawer_class, page_size[0], page_size[1]
        self.window = tk.Toplevel(parent)
        self.window.title(title); self.window.geometry("850x950")
        
        toolbar = tk.Frame(self.window, bg='white', height=50, bd=1, relief=tk.RAISED)
        toolbar.pack(fill=tk.X)
        tk.Button(toolbar, text="🖨️ طباعة", command=self.print_action, bg='#333', fg='white', width=12, font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, padx=10, pady=5)
        tk.Button(toolbar, text="💾 حفظ PDF", command=self.save_pdf_action, bg='#666', fg='white', width=12, font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, padx=5, pady=5)
        
        if HAS_WIN32:
            self.p_combo = ttk.Combobox(toolbar, state='readonly', width=30)
            self.p_combo.pack(side=tk.LEFT, padx=10)
            try:
                self.p_combo['values'] = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
                self.p_combo.set(win32print.GetDefaultPrinter())
            except: pass

        frame = tk.Frame(self.window, bg='#F0F0F0')
        frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(frame, bg='white')
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y); hsb.pack(side=tk.BOTTOM, fill=tk.X); self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.window.after(100, self.render)

    def render(self):
        self.canvas.delete("all")
        backend = TkCanvasBackend(self.canvas, self.pw, self.ph)
        px_w, px_h = backend._c2p(self.pw), backend._c2p(self.ph)
        self.canvas.create_rectangle(40, 40, 40+px_w, 40+px_h, fill='white', outline='#000000')
        backend.ox, backend.oy = 40, 40
        self.drawer_class(backend, self.data).draw()
        self.canvas.config(scrollregion=(0, 0, px_w + 100, px_h + 100))

    def print_action(self):
        path = os.path.join(tempfile.gettempdir(), f"print_{datetime.now().strftime('%H%M%S')}.pdf")
        c = canvas.Canvas(path, pagesize=(cm_to_pdf(self.pw), cm_to_pdf(self.ph)))
        self.drawer_class(ReportLabBackend(c, self.pw, self.ph), self.data).draw()
        c.save()
        if not silent_print_pdf(path, self.p_combo.get() if HAS_WIN32 else None):
            messagebox.showwarning("تنبيه", "تم فتح الفاتورة للطباعة اليدوية")
        else: self.window.destroy()

    def save_pdf_action(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"فاتورة_{datetime.now().strftime('%H%M%S')}.pdf")
        if path:
            c = canvas.Canvas(path, pagesize=(cm_to_pdf(self.pw), cm_to_pdf(self.ph)))
            self.drawer_class(ReportLabBackend(c, self.pw, self.ph), self.data).draw()
            c.save(); os.startfile(path)
