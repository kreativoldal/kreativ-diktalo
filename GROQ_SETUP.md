# Groq Whisper Setup Útmutató 🚀

**Ez az amit a WISPR FLOW is használ!**

## ⚡ Miért Groq?

- **Ultra gyors**: <1 másodperc transcription idő
- **Hatalmas free tier**: 14,400 perc/nap ingyen
- **Whisper Large-v3**: A legjobb Whisper modell
- **Kiváló magyar**: Ugyanaz a Whisper ami helyben is fut

## 1. Regisztráció (1 perc)

1. Menj ide: **https://console.groq.com/**
2. Kattints a **"Sign Up"** gombra
3. Regisztrálj email címmel vagy GitHub-bal

## 2. API Key megszerzése

1. Bejelentkezés után menj a **"API Keys"** menüpontra
2. Kattints a **"Create API Key"** gombra
3. Másold ki az API key-t (pl: `gsk_...`)

## 3. API Key beállítása a config.yaml-ban

Nyisd meg a `config.yaml` fájlt és add meg az API key-t:

```yaml
# Speech-to-Text Beállítások
stt:
  provider: "groq"  # <-- Groq használata (WISPR FLOW!)

  # Groq Whisper (WISPR FLOW használja ezt!)
  groq:
    api_key: "ITT_A_TE_API_KEY_ED"   # <-- Ide másold be!
    language: "hu"                   # Magyar nyelv
```

## 4. Kész! 🎉

Most már használhatod az appot Groq-kal (ugyanaz mint Wispr Flow):

```bash
python src/gui_main.py
```

## 📊 Groq vs AssemblyAI vs Whisper

| Provider | Sebesség | Free Tier | Pontosság | Használja |
|----------|----------|-----------|-----------|----------|
| **Groq** | ⚡⚡⚡ <1s | 14,400 min/nap | ⭐⭐⭐⭐⭐ | **Wispr Flow** |
| AssemblyAI | 🐌 38s | 185 óra/hó | ⭐⭐⭐⭐⭐ | - |
| Whisper (helyi) | 🐌 15-30s | ♾️ Végtelen | ⭐⭐⭐ | - |

## 🔥 Free Tier Részletek

**Groq Free Tier:**
- 14,400 perc/nap (240 óra!)
- Whisper Large-v3 modell
- <1 másodperc transcription
- Korlátlan számú request (rate limit van)

**Rate Limits:**
- 30 request/perc
- Tökéletes personal use-ra!

## Troubleshooting

### "Groq API key hiányzik!"

- Ellenőrizd, hogy kitöltötted-e az `api_key` mezőt a config.yaml-ban
- Ellenőrizd, hogy a key `gsk_` -vel kezdődik-e

### "Rate limit exceeded"

- Várs 1 percet és próbáld újra
- Free tier: 30 request/perc limit

## Hasznos linkek

- 🌐 Groq Console: https://console.groq.com/
- 📚 Groq Docs: https://console.groq.com/docs
- 🎤 Whisper Large-v3 info: https://github.com/openai/whisper
