import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

class StartMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام الحسابات - خلفاء الحاج")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # تحميل الصورة كخلفية
        self.load_background_image()
        
        # إنشاء Canvas لعرض الصورة
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # عرض الصورة كخلفية
        self.bg_image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
        
        # قائمة لتتبع الأزرار الحالية حتى يمكن إعادة بنائها لاحقاً
        self.menu_buttons = []
        self.menu_button_wrappers = []
        self.bottom_buttons = []
        self.bottom_button_wrappers = []
        self.bottom_buttons_frame = None
        
        # إنشاء الزراير
        self.create_buttons()
        
        # ربط تغيير حجم النافذة بتحديث الصورة
        self.root.bind('<Configure>', self.on_window_resize)
    
    def load_background_image(self):
        """تحميل الصورة وتعديل حجمها"""
        image_path = "Screenshot 2025-11-24 202612.png"
        
        if not os.path.exists(image_path):
            print(f"تحذير: لم يتم العثور على الصورة في {image_path}")
            # إنشاء صورة افتراضية إذا لم توجد الصورة
            self.bg_image = None
            return
        
        try:
            # تحميل الصورة
            img = Image.open(image_path)
            # تعديل حجم الصورة لتناسب النافذة
            self.original_image = img
            self.bg_image = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"خطأ في تحميل الصورة: {e}")
            self.bg_image = None
    
    def on_window_resize(self, event):
        """تحديث حجم الصورة عند تغيير حجم النافذة"""
        if hasattr(self, 'original_image') and self.original_image:
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            if width > 1 and height > 1:
                # تعديل حجم الصورة مع الحفاظ على النسبة
                img = self.original_image.copy()
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(img)
                self.canvas.itemconfig(self.bg_image_id, image=self.bg_image)
    
    def create_buttons(self):
        """إنشاء أزرار القائمة الرئيسية في الجانب الأيسر"""
        # إزالة أي أزرار قديمة
        for btn in getattr(self, "menu_buttons", []):
            btn.destroy()
        for wrapper in getattr(self, "menu_button_wrappers", []):
            wrapper.destroy()
        for btn in getattr(self, "bottom_buttons", []):
            btn.destroy()
        for wrapper in getattr(self, "bottom_button_wrappers", []):
            wrapper.destroy()
        if getattr(self, "bottom_buttons_frame", None):
            self.bottom_buttons_frame.destroy()

        self.menu_buttons = []
        self.menu_button_wrappers = []
        self.bottom_buttons = []
        self.bottom_button_wrappers = []
        self.bottom_buttons_frame = None

        base_button_style = {
            'font': ('Playpen Sans Arabic', 18, 'bold'),
            'bg': 'white',
            'fg': '#d35400',
            'relief': tk.FLAT,
            'bd': 0,
            'cursor': 'hand2',
            'activebackground': '#f0f0f0',
            'activeforeground': '#d35400'
        }
        top_button_style = {**base_button_style, 'width': 22, 'height': 2}
        bottom_button_style = {**base_button_style, 'width': 16, 'height': 1}

        buttons_info = [
            ("برنامج البائعين", self.open_sellers_program, 0.28),
            ("برنامج العملاء", self.open_clients_program, 0.41),
            ("برنامج العدة", self.open_inventory_program, 0.54),
            ("برنامج التحصيل و المنصرف", self.open_collection_program, 0.67),
        ]

        for text, command, rely in buttons_info:
            wrapper = tk.Frame(self.root, bg='black')
            wrapper.place(relx=0.03, rely=rely, anchor=tk.W)

            btn = tk.Button(wrapper, text=text, command=command, **top_button_style)
            btn.pack(padx=2, pady=2)

            self.menu_buttons.append(btn)
            self.menu_button_wrappers.append(wrapper)

        # الأزرار السفلية المرصوصة أفقياً
        bottom_buttons_info = [
            ("اضافة منصرف", self.open_add_expense),
            ("اضافة تحصيل", self.open_add_collection),
            ("جديد", self.open_new_entry),
            ("ترحيل الزراعة", self.open_agriculture_transfer),
            ("حسابات", self.open_accounts_module),
        ]

        # زر ترحيل الزراعة هو المرجع في الحجم
        reference_width = bottom_button_style['width']
        reference_height = bottom_button_style['height']

        # إنشاء أزرار منفصلة مع الحفاظ على الخط الأفقي
        spacing = 0.17
        buttons_count = len(bottom_buttons_info)
        base_relx = 0.5 - ((buttons_count - 1) * spacing) / 2

        for index, (text, command) in enumerate(bottom_buttons_info):
            relx = base_relx + index * spacing
            wrapper = tk.Frame(self.root, bg='black')
            wrapper.place(relx=relx, rely=0.9, anchor=tk.CENTER)

            btn = tk.Button(
                wrapper,
                text=text,
                command=command,
                width=reference_width,
                height=reference_height,
                **base_button_style
            )
            btn.pack(padx=2, pady=2)

            self.bottom_buttons.append(btn)
            self.bottom_button_wrappers.append(wrapper)
        
        # زر الخروج في أعلى اليمين
        exit_button_style = {
            'font': ('Playpen Sans Arabic', 14, 'bold'),
            'bg': 'white',
            'fg': '#d35400',
            'relief': tk.FLAT,
            'bd': 0,
            'cursor': 'hand2',
            'activebackground': '#f0f0f0',
            'activeforeground': '#d35400',
            'width': 10,
            'height': 1
        }
        
        exit_wrapper = tk.Frame(self.root, bg='black')
        exit_wrapper.place(relx=0.95, rely=0.05, anchor=tk.NE)
        
        exit_btn = tk.Button(
            exit_wrapper,
            text="خروج",
            command=self.confirm_exit,
            **exit_button_style
        )
        exit_btn.pack(padx=2, pady=2)
        self.exit_button = exit_btn
        self.exit_wrapper = exit_wrapper
    
    def confirm_exit(self):
        """نافذة تأكيد الخروج من البرنامج"""
        result = messagebox.askyesno(
            "تأكيد الخروج",
            "هل تريد اغلاق البرنامج؟",
            icon='question'
        )
        if result:
            self.root.quit()
            self.root.destroy()
    
    def open_sellers_program(self):
        """فتح برنامج البائعين"""
        print("فتح برنامج البائعين")
        # سيتم تنفيذها لاحقاً

    def open_clients_program(self):
        """فتح برنامج العملاء"""
        print("فتح برنامج العملاء")
        # سيتم تنفيذها لاحقاً

    def open_inventory_program(self):
        """فتح برنامج العدة"""
        print("فتح برنامج العدة")
        # سيتم تنفيذها لاحقاً

    def open_collection_program(self):
        """فتح برنامج التحصيل والمنصرف"""
        print("فتح برنامج التحصيل والمنصرف")
        # سيتم تنفيذها لاحقاً

    def open_accounts_module(self):
        """فتح قسم الحسابات"""
        print("فتح قسم الحسابات")
        # سيتم تنفيذها لاحقاً

    def open_agriculture_transfer(self):
        """فتح ترحيل الزراعة"""
        print("فتح ترحيل الزراعة")
        # سيتم تنفيذها لاحقاً

    def open_new_entry(self):
        """فتح شاشة جديد"""
        print("فتح شاشة جديد")
        # سيتم تنفيذها لاحقاً

    def open_add_collection(self):
        """إضافة تحصيل جديد"""
        print("إضافة تحصيل جديد")
        # سيتم تنفيذها لاحقاً

    def open_add_expense(self):
        """إضافة منصرف جديد"""
        print("إضافة منصرف جديد")
        # سيتم تنفيذها لاحقاً


def main():
    # تهيئة قاعدة البيانات
    from database import Database
    db = Database()
    
    # إنشاء النافذة الرئيسية
    root = tk.Tk()
    app = StartMenu(root)
    root.mainloop()


if __name__ == "__main__":
    main()

