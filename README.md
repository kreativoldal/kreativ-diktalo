# Kreatív Diktáló 🎤

Intelligens Windows diktáló alkalmazás Groq/AssemblyAI/Whisper beszédfelismeréssel és LLM-alapú szövegtisztítással.

## ✨ Funkciók

- 🎯 **Online vagy Offline** - Groq (ajánlott), AssemblyAI (185h/hó ingyen) VAGY helyi Whisper
- 🧠 **Intelligens tisztítás** - LLM-alapú töltelékszó-eltávolítás és mondatjavítás
- ⚡ **Gyors átírás** - Kiváló pontosság magyarul is
- 🎨 **Modern GUI** - PyQt6-alapú felhasználói felület
- 📊 **Előzmények** - Korábbi diktálások újrahasználata
- 🔧 **Command Mode** - Szöveg átalakítása hangparancsokkal

## 🚀 Telepítés

### ⚠️ FONTOS: Admin jogok Windows-on

A **globális F8 hotkey** működéséhez **ADMIN JOGOK szükségesek** Windows-on!

**Egyszerű indítás adminként:**
```bash
# PowerShell (automatikusan kéri az admin jogokat):
powershell -ExecutionPolicy Bypass -File start_admin.ps1

# VAGY BAT fájl (jobb klikk -> "Futtatás rendszergazdaként"):
INDITAS_ADMIN.bat
```

Ha **NINCS admin jog** → Az F8 csak akkor működik, ha az app ablaka aktív ❌
Ha **VAN admin jog** → Az F8 BÁRHOL működik (Chrome, Notepad, stb.) ✅

---

### Előfeltételek

1. **Python 3.9+** telepítése
2. **Ollama** telepítése: [ollama.com](https://ollama.com)
3. **Llama modell** telepítése:
   ```bash
   ollama pull llama3.1:8b
   ```

### Alkalmazás telepítése

```bash
# Repository klónozása
git clone https://github.com/kreativoldal/kreativ-diktalo.git
cd kreativ-diktalo

# Virtuális környezet létrehozása
python -m venv venv
venv\Scripts\activate

# Függőségek telepítése
pip install -r requirements.txt
```

### Speech-to-Text választása

**Opció A: Groq (Ajánlott) 🏆**
- Ingyenes API (napi limit)
- Rendkívül gyors felhő-alapú feldolgozás
- Kiváló magyar pontosság (Whisper large-v3 modell)
- Setup: Regisztráció a [console.groq.com](https://console.groq.com) oldalon, API kulcs generálása

**Opció B: AssemblyAI**
- 185 óra/hónap ingyen
- Kiváló magyar pontosság
- Gyors felhő-alapú
- Setup: Lásd [ASSEMBLYAI_SETUP.md](ASSEMBLYAI_SETUP.md)

**Opció C: Helyi Whisper**
- Teljesen offline
- Ingyenes, korlátlan használat
- Lassabb, kevésbé pontos magyarul
- Nincs extra setup (automatikus letöltés)

## 🎮 Használat

### Indítás

```bash
python src/main.py
```

### Alapvető diktálás

1. **Nyomja le az F8** gombot
2. **Beszéljen** a mikrofonba
3. **Engedje fel az F8** gombot
4. Várjon pár másodpercet - a tisztított szöveg beíródik!

### Command Mode

1. **Jelöljön ki szöveget** az aktív alkalmazásban
2. **Nyomja le Ctrl+Shift+Space**
3. **Mondjon egy parancsot**:
   - "tedd barátságosabbá"
   - "fordítsd angolra"
   - "rövidítsd le"
   - "javítsd a helyesírást"
4. A szöveg automatikusan átalakul!

## ⚙️ Konfiguráció

Szerkessze a `config.yaml` fájlt:

```yaml
hotkeys:
  dictation: "F8"
  command_mode: "Ctrl+Shift+Space"

stt:
  provider: "groq"  # "groq", "assemblyai" vagy "whisper"

  groq:
    api_key: "YOUR_GROQ_API_KEY"  # console.groq.com
    language: "hu"

  assemblyai:
    api_key: "YOUR_ASSEMBLYAI_API_KEY"  # Lásd ASSEMBLYAI_SETUP.md
    language: "hu"

  whisper:
    model: "small"      # tiny, base, small, medium, large
    language: "hu"
    device: "cpu"       # vagy "cuda"

ollama:
  host: "http://localhost:11434"
  model: "llama3.1:8b"
```

## 🔧 Rendszerkövetelmények

- **OS**: Windows 10/11
- **RAM**: 8GB minimum (16GB ajánlott Whisper Large-hoz)
- **GPU**: Opcionális (CUDA support a gyorsabb feldolgozáshoz)
- **Tárhely**: ~5GB (modellek)

## 📝 Licensz

MIT License

## 🤝 Közreműködés

Pull requestek és issue-k szívesen fogadottak!

## 📧 Kapcsolat

Kérdések esetén nyisson issue-t a GitHub-on.
