
import os

try:
    file_path = r"d:\Python_Project\database.py"
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Remove null bytes (common artifact of UTF-16 misinterpretation or PowerShell piping)
    cleaned_content = content.replace(b'\x00', b'')
    
    # Try to decode to ensure it's valid text now
    text_content = cleaned_content.decode('utf-8', errors='replace')
    
    # Write back clean content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text_content)
        
    print("Successfully cleaned database.py")
except Exception as e:
    print(f"Error: {e}")
