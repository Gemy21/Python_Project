"""
إنشاء أيقونة من الصورة المرفوعة
استخراج الدائرة وتحويلها إلى ملف .ico
"""

from PIL import Image, ImageDraw
import os

# مسار الصورة المرفوعة
input_image_path = r"C:/Users/gamal/.gemini/antigravity/brain/2599de39-7b98-4c9b-90cf-eedc01cc9f0c/uploaded_image_1764766807856.png"

# فتح الصورة
img = Image.open(input_image_path)

# تحويل إلى RGBA إذا لم تكن كذلك
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# الحصول على أبعاد الصورة
width, height = img.size

# حساب مركز الصورة ونصف قطر الدائرة
center_x = width // 2
center_y = height // 2
radius = min(center_x, center_y) - 10  # نقلل قليلاً لضمان عدم قص الحواف

# إنشاء قناع دائري
mask = Image.new('L', (width, height), 0)
draw = ImageDraw.Draw(mask)
draw.ellipse((center_x - radius, center_y - radius, 
              center_x + radius, center_y + radius), fill=255)

# تطبيق القناع على الصورة
output = Image.new('RGBA', (width, height), (0, 0, 0, 0))
output.paste(img, (0, 0))
output.putalpha(mask)

# قص الصورة لتحتوي على الدائرة فقط
bbox = (center_x - radius, center_y - radius, 
        center_x + radius, center_y + radius)
cropped = output.crop(bbox)

# إنشاء أيقونة بأحجام متعددة (256x256, 128x128, 64x64, 48x48, 32x32, 16x16)
icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]

# حفظ كملف .ico
output_path = "logo_icon.ico"
cropped.save(output_path, format='ICO', sizes=icon_sizes)

print(f"تم إنشاء الأيقونة بنجاح: {output_path}")

# حفظ أيضاً كـ PNG للمعاينة
png_output = "logo_icon.png"
cropped.save(png_output, format='PNG')
print(f"تم حفظ نسخة PNG: {png_output}")
