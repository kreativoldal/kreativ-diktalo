# Kreatív Diktáló - Windows Telepítő Készítése 📦

Ez az útmutató bemutatja, hogyan készíthetsz telepíthető Windows verziót.

---

## 🎯 Két lehetőség:

### **Opció A: Egyszerű .exe (Portable)**
- Egyetlen mappa, ami bárhova másolható
- Gyors, egyszerű
- **Használat:** Csak futtasd a `build_exe.bat` fájlt

### **Opció B: Professzionális Telepítő**
- Teljes Windows installer (.exe)
- Start Menu shortcut
- Automatikus eltávolítás
- **Használat:** Inno Setup-pal fordítsd le az `installer.iss` fájlt

---

## 🚀 Opció A: Portable .exe készítés

### 1. **Build futtatása**

**Egyszerű módszer:**
```bash
# Dupla kattintás:
build_exe.bat
```

**Vagy CMD-ből:**
```bash
cd D:\Antigravity\kreativ-diktalo
build_exe.bat
```

### 2. **Eredmény**

Build után megjelenik:
```
dist/
└── KreativDiktalo/
    ├── KreativDiktalo.exe  ← Ezt futtasd!
    ├── config.yaml
    ├── assets/
    │   └── icon.ico
    └── ... (más dll-ek, library-k)
```

### 3. **Terjesztés**

**A teljes `dist/KreativDiktalo` mappát csomagold be ZIP-be:**
```bash
cd dist
# Jobb klikk a KreativDiktalo mappán → "Tömörítés" → ZIP
```

**Küldd el ezt a ZIP-et** → A másik ember:
1. Kicsomagolja
2. Dupla klikk a `KreativDiktalo.exe`-n
3. UAC ablak → "Igen" (admin jogok)
4. Kész! 🎉

---

## 🎁 Opció B: Professzionális Telepítő

### 1. **Inno Setup telepítése**

1. Töltsd le: https://jrsoftware.org/isdl.php
2. Telepítsd (Next, Next, Finish)

### 2. **EXE build (előfeltétel)**

Először készítsd el a .exe-t:
```bash
build_exe.bat
```

### 3. **Installer fordítása**

1. Nyisd meg az **Inno Setup Compiler**-t
2. **File → Open** → válaszd ki: `installer.iss`
3. **Build → Compile** (vagy F9)
4. Várj 1-2 percet...

### 4. **Eredmény**

```
dist/
└── installer/
    └── KreativDiktalo_Setup_1.0.0.exe  ← EZ A TELEPÍTŐ!
```

### 5. **Terjesztés**

**Küldd el ezt az egyetlen fájlt** → A másik ember:
1. Dupla klikk → Next, Next, Install
2. Start Menu-ből elindítja
3. Automatikusan admin jogokkal fut! ✅

---

## 📊 Fájl méretek (becsült)

- **Portable ZIP:** ~300-500 MB
- **Installer .exe:** ~250-400 MB (tömörített)

Miért nagy? Mert tartalmazza:
- Python runtime
- PyQt6 (GUI library)
- NumPy, SciPy (audio processing)
- Torch (ha használod)
- Összes dependency

---

## ⚙️ Build beállítások módosítása

### **Kisebb fájlméret** (ha túl nagy):

Nyisd meg `kreativ_diktalo.spec` és módosítsd:

```python
# Kizárható súlyos modulok ha nem használod őket:
excludes=[
    'matplotlib',
    'IPython',
    'jupyter',
    'torch',  # Ha nem használsz helyi Whisper-t
    'torchaudio',
],
```

### **Konzol ablak megjelenítése** (debug-hoz):

```python
exe = EXE(
    ...
    console=True,  # Változtasd True-ra
    ...
)
```

---

## 🐛 Troubleshooting

### **"Modul nem található" hiba**

Adj hozzá a `hiddenimports` listához:
```python
hidden_imports = [
    'hiányzó_modul_neve',
]
```

### **"Admin jogok kellenek" hiba**

Ellenőrizd, hogy a .spec fájlban van-e:
```python
uac_admin=True,
```

### **Túl nagy a fájlméret**

1. Zárj ki felesleges modulokat (lásd fent)
2. Használj UPX tömörítést: `upx=True`
3. Töröld a debug információkat: `strip=True`

---

## 📝 Követelmények a futtatáshoz

**A telepített .exe-hez NEM kell:**
- ❌ Python telepítés
- ❌ pip install
- ❌ Virtual environment
- ❌ Semmilyen setup

**Csak Windows 10/11 (64-bit)** ✅

---

## 🎯 Következő lépések

1. **Build készítése:** `build_exe.bat`
2. **Tesztelés:** `dist\KreativDiktalo\KreativDiktalo.exe`
3. **Terjesztés:** ZIP vagy Inno Setup installer

**Kész! Most már bárkinek odaadhatod!** 🎉
