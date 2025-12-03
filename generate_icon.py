from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import os

def create_icon():
    # Image size
    size = (256, 256)
    # Background color (Dark Green for agriculture/fresh feel)
    bg_color = (34, 139, 34) 
    # Text color
    text_color = (255, 255, 255)

    image = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(image)

    # Text to display
    text = "خلفاء الحاج\nمحي غريب بعجر"
    
    # Reshape and reorder for Arabic
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)

    # Load font - trying Arial Bold for better visibility
    try:
        # Windows font path
        font_path = "C:\\Windows\\Fonts\\arialbd.ttf" # Arial Bold
        font = ImageFont.truetype(font_path, 32)
    except IOError:
        try:
            font_path = "C:\\Windows\\Fonts\\arial.ttf"
            font = ImageFont.truetype(font_path, 32)
        except IOError:
            font = ImageFont.load_default()
            print("Warning: Arial font not found, using default.")

    # Calculate text position to center it
    lines = bidi_text.split('\n')
    
    # Calculate total height
    total_height = 0
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        line_heights.append(h)
        total_height += h + 10 # 10px padding between lines

    current_y = (size[1] - total_height) / 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (size[0] - w) / 2
        draw.text((x, current_y), line, font=font, fill=text_color)
        current_y += line_heights[i] + 10

    # Save as PNG
    png_filename = "app_icon.png"
    image.save(png_filename)
    print(f"Saved {png_filename}")

    # Save as ICO
    ico_filename = "app_icon.ico"
    image.save(ico_filename, format='ICO', sizes=[(256, 256)])
    print(f"Saved {ico_filename}")

if __name__ == "__main__":
    create_icon()
