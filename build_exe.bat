@echo off
:: ====================================================================
:: Kreatív Diktáló - Windows EXE Builder
:: ====================================================================
::
:: Ez a script PyInstaller-rel .exe fájlt készít az alkalmazásból
::
:: ====================================================================

echo.
echo ========================================
echo   Kreativ Diktalo - EXE Builder
echo ========================================
echo.

:: Virtual environment aktiválása
if exist "venv\Scripts\activate.bat" (
    echo [1/4] Virtual environment aktiválása...
    call venv\Scripts\activate.bat
) else (
    echo [HIBA] Virtual environment nem található!
    pause
    exit /b 1
)

:: PyInstaller ellenőrzése
echo [2/4] PyInstaller ellenőrzése...
python -c "import PyInstaller" 2>nul
if %errorLevel% neq 0 (
    echo [*] PyInstaller telepítése...
    pip install pyinstaller
)

:: Régi build törlése
echo [3/4] Régi build törlése...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

:: EXE készítése
echo [4/4] EXE készítése (ez eltarthat 2-5 percig)...
echo.
pyinstaller --clean kreativ_diktalo.spec

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo   BUILD SIKERES!
    echo ========================================
    echo.
    echo [OK] EXE elkészült: dist\KreativDiktalo\KreativDiktalo.exe
    echo.
    echo Próbáld ki:
    echo   cd dist\KreativDiktalo
    echo   KreativDiktalo.exe
    echo.
) else (
    echo.
    echo [HIBA] Build sikertelen!
    echo.
)

pause
