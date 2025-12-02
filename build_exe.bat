@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo Building Executable...
pyinstaller --noconfirm --onefile --windowed --name "VegetableFruitManager" --add-data "Screenshot 2025-11-24 202612.png;." main.py

echo Build Complete!
echo The executable will be in the 'dist' folder.
