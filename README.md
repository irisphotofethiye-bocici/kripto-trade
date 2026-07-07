# kripto-trade — Kripto CEO Ajanı

Claude Code üzerinde çalışan, çok‑mercekli (D1–D4 + D3 kapısı) bir kripto analiz/karar sistemi.
**Beyin (CEO) = en güçlü mevcut model** (Fable/Opus); mekanik işler deterministik Python (0 token).

> ⚠️ Yatırım kararları kullanıcıya aittir. Hiçbir bileşen otomatik emir/işlem yapmaz.
> Faz 4 (1 haftalık ileri-test kapısı) **2026‑07‑02'de GEÇTİ ile kapandı**; disiplin kuralları (NET R/R≥1:2, $5 risk-önce, vetolar) aynen yürürlükte.

## Bileşenler
| Dosya | Görev | Model/maliyet |
|-------|-------|---------------|
| `.claude/skills/kripto/SKILL.md` | CEO beyni: 3 sinyal (D1/D2/D4) + D3 kapısı, veto, senaryo, karar (LONG+SHORT simetrik) | LLM (sadece final) |
| `evren.py` | Ortak evren/eleme + rejim (BTC SMA20) + eşik okuyucu | Python, 0 token |
| `olcucu.py` | ATR+swing → giriş/SL/TP/R‑R (**`--entry` plan fiyatı**); `d1` bloğu (RSI/MA50/MA200/cross/basis); `--mtf` ağırlıklı çoklu‑TF | Python, 0 token |
| `radar.py` | Öncü imza taraması + **Pillar D** (top-trader L/S, taker) + rejim + float filtresi; 15dk zamanlayıcı | Python, 0 token |
| `piyasa_yapisi.py` | BTC.D/USDT.D + alt/BTC göreli güç + altseason checklist; 11:00/23:00 zamanlayıcı | Python, 0 token |
| `tarayici.py` | Avcı/Kademe‑1: **iki yönlü** momentum+trend ön‑filtre (AYI'da SHORT tier) | Python, 0 token |
| `arsiv_analiz.py` | Radar arşivi forward-return: skor×yön×rejim, short-sim, etiket doğrulama (edge ölçümü) | Python, 0 token |
| `katip.py` | Tahmin defteri çözümleme: açık pozisyon durumu + hit-rate karnesi (okur, yazmaz) | Python, 0 token |
| `kucukcap.py` | Küçük‑cap modu + **Bekçi** (GoPlus güvenlik) + mcap kapısı | Python, 0 token |
| `makro.py` | D3 çekirdek: DXY (Yahoo) + FOMC/CPI takvimi (`makro_takvim.json`) + veto bayrakları | Python, 0 token |
| `fng.py` | Fear & Greed (alternative.me) | Python, 0 token |
| `likidasyon.py` | Binance forceOrder canlı likidasyon akışı (stdlib websocket) | Python, 0 token |
| `faz4_check.py` | Günlük sağlık: veri doğruluğu + erişim + **zamanlayıcı bayatlık** | Python, 0 token |
| `nobetci.py` | Fırsat/pozisyon alarmı: radar+stop/TP+ekstra seviye+rejim flip → Telegram+toast+log; 5dk zamanlayıcı | Python, 0 token |
| `testbot.py` | **SANAL** ($1000 paper) 7 günlük otonom iki-yönlü vadeli bot: rejim-koşullu giriş, gerçek maliyetler, likidasyon; 5dk zamanlayıcı | Python, 0 token |
| `panel_sunucu.py` + `panel.html` | TestBot canlı dashboard (localhost:8787): equity eğrisi + pozisyon tablosu + mum grafiği | Python (stdlib) |
| `apify_liq.py` / `x_sentiment.py` | Liq-heatmap haritası / X sentiment (on-demand, ücretli ~$0.01) | Apify |

## Veri kaynakları
- **Binance direct REST/WS** (birincil, anahtarsız) → **CoinDesk MCP** (yedek, çapraz doğrulama)
- **CoinGecko** (evren/mcap/float, demo key) · **GoPlus** (Bekçi, anahtarsız)
- **alternative.me** (F&G) · **Yahoo Finance** (DXY) · **web_search** (haber/ETF/jeopolitik tamamlayıcı)

## Kurulum
1. `cp kripto-config.example.json kripto-config.json` → kendi anahtarlarını ve `maliyet`/`esikler` değerlerini gir.
2. `cp kripto_portfoy.example.json kripto_portfoy.json` → portföyünü gir (`.gitignore`'da, lokalde kalır).
3. Python 3 (ek bağımlılık yok — yalnız stdlib).
4. Zamanlayıcılar (Windows Task Scheduler): `KriptoRadar` (radar --watch, 15dk) + `KriptoPiyasa` (piyasa_yapisi, 11:00/23:00) + `KriptoNobetci` (nobetci.py, 5dk) + `KriptoTestBot` (testbot.py --cycle, 5dk). Hepsi StartWhenAvailable + pilde çalışma açık. Panel (`panel_sunucu.py`) kalıcı görev DEĞİL — elle başlat (bkz Kullanım).
5. Alarm bildirimi (opsiyonel ama önerilir): Telegram'da @BotFather → `/newbot` → token'ı `kripto-config.json → telegram_bot_token` alanına yapıştır, bota bir kez `/start` yaz → chat_id'yi `getUpdates` ile bul.

## Kullanım
```bash
python tarayici.py --n 10                    # iki yönlü tarama → kısa liste
python radar.py                              # öncü imza + Pillar D + rejim
python olcucu.py --symbol WLD --side short --entry 0.62   # PLAN fiyatından giriş/SL/TP/R-R
python olcucu.py --symbol WLD --mtf          # çoklu-TF + erken belirti + basis
python piyasa_yapisi.py                      # dominans + alt/BTC liderlik
python arsiv_analiz.py                       # edge base-rate ölçümü (arşivden)
python katip.py                              # açık tahminler + karne
python makro.py && python fng.py             # D3/D4 deterministik girdiler
python likidasyon.py --dk 10                 # canlı likidasyon akışı
python kucukcap.py --id aixbt                # küçük-cap + Bekçi güvenlik
python faz4_check.py                         # sağlık + zamanlayıcı bayatlık
python nobetci.py --test                     # fırsat/pozisyon alarmı, uçtan uca test
python testbot.py --durum                     # SANAL 7 günlük bot: karne (win-rate, ort. R)
python panel_sunucu.py                        # dashboard: http://127.0.0.1:8787
```
Derin analiz için Claude Code'da `/kripto <SEMBOL>`.

## Güvenlik
- Anahtarlar yalnız `kripto-config.json`'da (repo'da değil). Gerçek portföy ve tüm log/arşivler lokalde (`.gitignore`).
- Hiçbir ajan işlem/para çekme yapmaz; emir her zaman kullanıcıda.
- **TestBot SANALDIR** — hiçbir Binance API anahtarı/emri yok, sadece dosyada sayı tutar. Gerçek para geçişi ayrı, açık onay gerektiren bir adımdır.
- Eşikler tek kaynaktan: `kripto-config.json → esikler` (funding/OI/float/skor).
