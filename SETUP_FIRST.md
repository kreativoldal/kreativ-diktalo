# ⚙️ FONTOS: Első Indítás Előtt - API Kulcs Beállítása

## 🔐 API Kulcs Konfigurálása

**FONTOS:** Az alkalmazás használatához szükséged van egy **ingyenes Groq API kulcsra**!

---

## 🚀 Gyors Start (5 perc)

### 1. **Groq API Kulcs megszerzése** (INGYENES!)

1. Menj ide: **https://console.groq.com/**
2. Kattints: **"Sign Up"** (email vagy GitHub)
3. Menj az **"API Keys"** menüpontra
4. **"Create API Key"** → Másold ki (kezdődik: `gsk_...`)

**Free tier:**
- ✅ 14,400 perc/nap (240 óra!)
- ✅ Örökké ingyen
- ✅ Ultra gyors (<1 sec)

---

### 2. **API Kulcs beállítása az alkalmazásban**

**Módszer A: Grafikus felület (AJÁNLOTT)**

1. Indítsd el az alkalmazást: `KreativDiktalo.exe`
2. **Beállítások** (fogaskerék ikon vagy jobb klikk a tray-en)
3. **"Beszédfelismerés"** tab
4. Írd be az API kulcsot
5. **"Mentés"**
6. Indítsd újra az appot

**Módszer B: Kézi szerkesztés**

1. Nyisd meg: `config.template.yaml` (Notepad-dal)
2. Keresd meg:
   ```yaml
   stt:
     groq:
       api_key: YOUR_GROQ_API_KEY_HERE
   ```
3. Cseréld ki `YOUR_GROQ_API_KEY_HERE` →  a te API kulcsodra
4. **Mentsd el** mint `config.yaml`

---

### 3. **Kész! Indítás**

```
KreativDiktalo.exe
```

- **Admin jogok:** Az UAC ablakban kattints **"Igen"**
- **F8 hotkey:** Bárhol működik!

---

## 📖 További Dokumentáció

- **`GROQ_SETUP.md`** - Részletes Groq útmutató
- **`ASSEMBLYAI_SETUP.md`** - AssemblyAI alternatíva
- **`README.md`** - Teljes dokumentáció

---

## ❓ Gyakori Kérdések

### **Nem akarok regisztrálni, van offline verzió?**

Igen! Használhatsz **helyi Whisper** modellt (nincs API kell):
1. Beállítások → Beszédfelismerés
2. Provider: **"Whisper (helyi)"**
3. Lassabb (~15 sec), de teljesen offline

### **Mennyi ideig ingyen?**

**Örökké!** A Groq free tier nincs időkorlát, csak napi rate limit (14,400 perc/nap).

### **Biztonságos az API kulcsom?**

Igen! Az API kulcs csak a **te gépeden** van tárolva (`config.yaml`). Sehova nem küldjük el.

---

## 🐛 Problémák?

Ha bármi nem működik:
1. Ellenőrizd az API kulcsot (kezdődik `gsk_` -vel)
2. Nézd meg: `data/logs/app.log`
3. Indítsd újra az appot

---

**Jó diktálást!** 🎤✨
