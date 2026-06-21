# kripto-trade — Kripto CEO Ajanı

Claude Code üzerinde çalışan, çok‑mercekli (D1–D4) bir kripto analiz/karar sistemi.
**Beyin (CEO) = Opus**; mekanik işler deterministik Python + yerel Gemma (token tasarrufu).

> ⚠️ Yatırım kararları kullanıcıya aittir. Hiçbir bileşen otomatik emir/işlem yapmaz.

## Bileşenler
| Dosya | Görev | Model/maliyet |
|-------|-------|---------------|
| `.claude/skills/kripto/SKILL.md` | CEO beyni: D1–D4 sentez, veto, senaryo, karar | Opus (sadece final) |
| `olcucu.py` | ATR(14) + yapısal seviye → giriş/SL/TP/R‑R; `--mtf` çoklu‑TF + erken belirti | Python, 0 token |
| `kucukcap.py` | Küçük‑cap modu + **Bekçi** (GoPlus güvenlik) + mcap kapısı | Python, 0 token |
| `tarayici.py` | Avcı/Kademe‑1: momentum+trend ön‑filtre → kısa liste | Python, 0 token |
| `faz4_check.py` | Günlük sağlık: 3‑kaynak veri doğruluğu + erişim | Python, 0 token |

## Veri kaynakları
- **Binance direct REST** (birincil, anahtarsız) → **CoinDesk MCP** (yedek, çapraz doğrulama)
- **CoinGecko** (D1 fiyat + D4 trending, demo key) · **GoPlus** (Bekçi, anahtarsız)
- **Gemma/Ollama** (D4 haber özeti, yerel) · **web_search** (D3 makro)

## Kurulum
1. `cp kripto-config.example.json kripto-config.json` → kendi `coingecko_demo_key` ve `ollama_model` değerlerini gir.
2. `cp kripto_portfoy.example.json kripto_portfoy.json` → portföyünü gir (bu dosya `.gitignore`'da, lokalde kalır).
3. Ollama kurlu + bir model çekili olsun (örn. `gemma4:12b`).
4. Python 3 (ek bağımlılık yok — yalnız stdlib).

## Kullanım
```bash
python tarayici.py --n 10                 # piyasa taraması → kısa liste
python olcucu.py --symbol WLD --side long # giriş/SL/TP/R-R
python olcucu.py --symbol WLD --mtf       # çoklu-TF + erken belirti
python kucukcap.py --id aixbt             # küçük-cap + Bekçi güvenlik
python faz4_check.py                       # günlük sağlık kontrolü
```
Derin analiz için Claude Code'da `/kripto <SEMBOL>`.

## Güvenlik
- Anahtarlar yalnız `kripto-config.json`'da (repo'da değil). Gerçek portföy de lokalde.
- Faz 4 (1 haftalık test) geçmeden gerçek para kararı verilmez.
