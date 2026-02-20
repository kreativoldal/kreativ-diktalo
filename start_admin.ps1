# ====================================================================
# Kreatív Diktáló - Auto-Admin Launcher
# ====================================================================
# Ez a script AUTOMATIKUSAN kéri az admin jogokat és elindítja az app-ot
# ====================================================================

# Admin jogok ellenőrzése
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "  Admin jogok kérése..." -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""

    # Újraindítás admin jogokkal
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Kreatív Diktáló - ADMIN MÓD" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "[OK] Admin jogok: MEGVANNAK" -ForegroundColor Green
Write-Host ""

# Projekt könyvtár
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

# Virtual environment aktiválása
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[*] Virtual environment aktiválása..." -ForegroundColor Cyan
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "[HIBA] Virtual environment nem található!" -ForegroundColor Red
    Write-Host "Futtasd először: python -m venv venv" -ForegroundColor Yellow
    Read-Host "Nyomj ENTER-t a kilépéshez"
    exit 1
}

# Keyboard library telepítése (ha nincs)
Write-Host "[*] Keyboard library ellenőrzése..." -ForegroundColor Cyan
python -c "import keyboard" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[*] Keyboard library telepítése..." -ForegroundColor Cyan
    pip install keyboard>=0.13.5
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  GUI INDÍTÁSA (Admin mód)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "[*] Most már az F8 BÁRHOL működik!" -ForegroundColor Green
Write-Host "[*] Próbáld ki más appban is (Notepad, Chrome...)" -ForegroundColor Cyan
Write-Host ""

# GUI indítása
python src/gui_main.py

Write-Host ""
Read-Host "Nyomj ENTER-t a kilépéshez"
