# Kreatív Diktáló - csendes, admin indító (konzol ablak nélkül)

$projectDir = "D:\Antigravity\kreativ-diktalo"
$pythonw    = "$projectDir\venv\Scripts\pythonw.exe"
$script     = "$projectDir\src\gui_main.py"

# Admin jogok ellenőrzése
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    # Újraindítás admin joggal – ez a PowerShell ablak is rejtve fut
    Start-Process powershell.exe -ArgumentList `
        "-WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" `
        -Verb RunAs
    exit
}

# Admin jogok megvannak – indítás pythonw.exe-vel (nincs konzol ablak!)
$env:PYTHONIOENCODING = "utf-8"
$env:HF_HUB_DISABLE_SYMLINKS = "1"
Set-Location $projectDir

Start-Process -FilePath $pythonw -ArgumentList "`"$script`"" -WorkingDirectory $projectDir -WindowStyle Hidden
