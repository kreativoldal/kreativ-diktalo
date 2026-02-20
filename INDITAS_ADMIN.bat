@echo off
chcp 65001 >nul
cd /d "D:/Antigravity/kreativ-diktalo"
net session >nul 2>&1
if %errorLevel% == 0 goto :admin_ok
echo [HIBA] ADMIN JOGOK HIANYOZNAK!
pause
exit /b 1
:admin_ok
echo [OK] Admin jogok megvannak
echo Indul a program...
set PYTHONIOENCODING=utf-8
"D:/Antigravity/kreativ-diktalo/venv/Scripts/python.exe" "D:/Antigravity/kreativ-diktalo/src/gui_main.py"
pause
