@echo off
echo Building Nova Pro X Controller...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

REM Build executable
pyinstaller --onefile --windowed --noconsole --name "NovaProXController" --icon="icon.ico" --collect-all customtkinter main.py

echo.
echo Build complete! Check the dist folder for the executable.
pause