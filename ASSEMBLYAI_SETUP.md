# AssemblyAI Setup Útmutató 🎤

Az AssemblyAI **185 óra/hónap ingyenes** speech-to-text szolgáltatást biztosít, amely **sokkal pontosabb magyar felismerést** ad, mint a helyi Whisper modell.

## 1. Regisztráció (2 perc)

1. Menj ide: **https://www.assemblyai.com/**
2. Kattints a **"Sign Up Free"** gombra
3. Regisztrálj email címmel vagy GitHub-bal

## 2. API Key megszerzése

1. Bejelentkezés után menj a **Dashboard**-ra
2. Baloldalon kattints az **"API Keys"** menüpontra
3. Másold ki az API key-t (pl: `a1b2c3d4e5f6...`)

## 3. API Key beállítása a config.yaml-ban

Nyisd meg a `config.yaml` fájlt és add meg az API key-t:

```yaml
# Speech-to-Text Beállítások
stt:
  provider: "assemblyai"             # <-- AssemblyAI használata

  # AssemblyAI (Online API - 185 óra/hónap ingyen!)
  assemblyai:
    api_key: "ITT_A_TE_API_KEY_ED"   # <-- Ide másold be!
    language: "hu"                   # Magyar nyelv
```

## 4. Kész! 🎉

Most már használhatod az appot az AssemblyAI-val:

```bash
python src/gui_main.py
```

## Free Tier Info

- **185 óra/hónap** ingyen (minden hónapban megújul)
- Magyarul kiváló pontosság
- Gyors felhő-alapú feldolgozás
- Auto-punctuation (automatikus írásjelek)

## Összehasonlítás

| STT Provider | Pontosság (magyar) | Sebesség | Free Tier |
|--------------|-------------------|----------|-----------|
| **AssemblyAI** | ⭐⭐⭐⭐⭐ | 🚀 Gyors | 185 h/hó |
| Whisper (helyi) | ⭐⭐⭐ | 🐌 Lassú | ♾️ Végtelen |

## Troubleshooting

### "AssemblyAI API key hiányzik!"

- Ellenőrizd, hogy kitöltötted-e az `api_key` mezőt a config.yaml-ban
- Ellenőrizd, hogy nincs-e extra szóköz vagy idézőjel az API key körül

### "API Error: Invalid API key"

- Ellenőrizd, hogy helyes API key-t másoltál-e be
- Próbáld meg újragenerálni az API key-t a Dashboard-on

### Vissza akarsz váltani Whisper-re?

Egyszerűen módosítsd a config.yaml-t:

```yaml
stt:
  provider: "whisper"  # <-- Whisper használata
```

## Hasznos linkek

- 📚 AssemblyAI Docs: https://www.assemblyai.com/docs
- 💰 Pricing: https://www.assemblyai.com/pricing
- 📊 Dashboard: https://www.assemblyai.com/app
