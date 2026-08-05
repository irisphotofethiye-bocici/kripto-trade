# kripto-trade — Kripto CEO Ajanı + SANAL Test Botu

Claude Code üzerinde çalışan kripto analiz/karar sistemi. **İki katman:**
1. **CEO beyni** (`/kripto` skill) — çok‑mercekli (D1–D4 + D3 kapısı) insan‑yüzlü analiz; beyin = en güçlü mevcut model (Opus).
2. **SANAL test botu** (`testbot.py`) — **gerçek para DEĞİL**, paper‑trading. Amaç: edge'i gerçekçi maliyetlerle (fee+slippage+funding+likidasyon) KANITLAMAK — gerçek paradan önce.

Mekanik işler deterministik Python (0 LLM tokeni); LLM yalnız CEO final kararında.

> ⚠️ Yatırım kararları kullanıcıya aittir. Hiçbir bileşen otomatik emir/işlem yapmaz. **TestBot SANALDIR** (dosyada sayı tutar, hiçbir Binance emri yok).
> Faz 4 (1 haftalık ileri‑test kapısı) **2026‑07‑02'de GEÇTİ ile kapandı**; disiplin kuralları (NET R/R≥1:2, $5 risk‑önce, vetolar) aynen yürürlükte.

## Sistem kimliği (bot tezi)
Bot bir **momentum‑takipçisi DEĞİL** — **mean‑reversion fade + rejim‑okuyucu.** Ölçümle elenen momentum/erken‑yakalama fikirleri (beta‑rotasyon, breakout, erken‑kuşak‑LONG, likidasyon‑fade) `fikir-defteri.md`'de **gerekçeleriyle** emekliye ayrıldı (bilgi silinmedi, sadece kod/dosya enkazı temizlendi). Çalışan çekirdek: **radar aşırılık tespiti → seçili fade‑SHORT → rejim‑koşullu kapılar → risk‑önce.** LONG tarafı henüz kanıtlanmış arketip beklemede (tur‑2 sanal öğrenecek).

## Bileşenler
| Dosya | Görev | Durum |
|-------|-------|-------|
| `.claude/skills/kripto/SKILL.md` | CEO beyni: D1/D2/D4 sinyal + D3 kapı, veto, senaryo, karar (LONG+SHORT simetrik) | 🟢 LLM (final) |
| `evren.py` | Ortak evren/eleme (**kripto‑only**, tokenize‑hisse dışlanır) + rejim (`btc_rejim` 1d SMA20) + eşik okuyucu + rate‑limitli `get()` + **`para_rejim`** (TOTAL mcap trend × rotasyon) | 🟢 çekirdek |
| `testbot.py` | **SANAL $10k** 7g otonom iki‑yönlü vadeli bot: rejim‑koşullu giriş, para‑kapısı + makro‑kapı, gerçek maliyet/likidasyon | 🟢 zamanlı (5dk) |
| `radar.py` | Öncü imza taraması + **Pillar D** (top‑trader L/S, taker) + rejim + erken‑kuşak (kripto‑only) | 🟢 zamanlı (15dk) |
| `olcucu.py` | ATR+swing → giriş/SL/TP/R‑R (`--entry` plan fiyatı); `d1` bloğu (RSI/MA/cross/basis); `--mtf` | 🟢 |
| `piyasa_yapisi.py` | BTC.D/USDT.D + alt/BTC göreli güç + para_rejim girdisi (`piyasa_yapisi_log.jsonl`) | 🟢 zamanlı (11:00/23:00) |
| `nobetci.py` | Fırsat/pozisyon alarmı: radar+stop/TP+rejim flip → Telegram+toast+log | 🟢 zamanlı (5dk) |
| `panel_sunucu.py` + `panel.html` | TestBot canlı dashboard (localhost:8787): equity + pozisyon + mum + para_rejim | 🟢 elle başlat |
| `makro.py` | D3 çekirdek: DXY (Yahoo) + FOMC/CPI takvim + `veto_fomc_48s` (**bota bağlı: makro‑kapı**) | 🟢 |
| `katip.py` | Tahmin defteri karne (açık pozisyon + hit‑rate); okur, yazmaz | 🟢 on‑demand |
| `kucukcap.py` | Küçük‑cap modu + **Bekçi** (GoPlus güvenlik) + mcap + DEX likidite kapısı | 🟢 on‑demand |
| `tarayici.py` | Avcı/Kademe‑1: iki yönlü momentum+trend ön‑filtre (kripto‑only) | 🟢 on‑demand |
| `fng.py` | Fear & Greed (alternative.me) | 🟢 on‑demand (D4) |
| `faz4_check.py` | Sağlık: veri doğruluğu + erişim + zamanlayıcı bayatlık | 🟢 on‑demand |
| `arsiv_analiz.py` · `veto_analiz.py` · `kacirma_analiz.py` · `erken_analiz.py` | **Ölçüm motoru** (K‑kapıları): radar arşivi/veto/kaçırma forward‑return edge ölçümü | 🟡 ölçüm |
| `apify_liq.py` · `x_sentiment.py` | Liq‑heatmap / X sentiment (Apify, ~$0.01) | ⚪ atıl‑ücretli (CEO on‑demand; fade‑tezinde kullanılmıyor) |
| `arsiv/likidasyon.py` | Binance forceOrder canlı likidasyon (stdlib WS) | 🔴 **ÖLÜ** — bölge‑engeli, 0 olay; arşive taşındı |
| `arsiv/coinalyze.py` | Coinalyze REST likidasyon geçmişi | 🔴 **RAFTA** — test→edge yok (N=605); arşive taşındı |

> **Likidasyon notu:** Bot likidasyon verisi KULLANMIYOR. Üç ayrı likidasyon denemesi (Binance WS ölü, Apify ücretli-atıl, Coinalyze edge'siz) yapıldı; hiçbiri bota bağlanmadı. Detay: `fikir-defteri.md`.
> **F10 (rejim SEZON×HAVA):** henüz KODDA DEĞİL — `fikir-defteri.md` F10'da dondurulmuş plan. Canlı rejim şu an tek‑katman `evren.btc_rejim()` (1d SMA20).

## Veri kaynakları
- **Binance direct REST/WS** (birincil, anahtarsız) → **CoinDesk MCP** (yedek, çapraz doğrulama)
- **CoinGecko** (evren/mcap/float, demo key) · **GoPlus** (Bekçi, anahtarsız)
- **alternative.me** (F&G) · **Yahoo Finance** (DXY) · **web_search** (haber/ETF/jeopolitik tamamlayıcı)

## Kurulum
1. `cp kripto-config.example.json kripto-config.json` → anahtarlar + `maliyet`/`esikler` değerleri.
2. `cp kripto_portfoy.example.json kripto_portfoy.json` → portföy (`.gitignore`'da, lokalde kalır).
3. Python 3 (ek bağımlılık yok — yalnız stdlib).
4. **Zamanlayıcılar (Windows Task Scheduler):** `KriptoRadar` (radar --watch, 15dk) + `KriptoPiyasa` (piyasa_yapisi, 11:00/23:00) + `KriptoNobetci` (nobetci.py, 5dk) + `KriptoTestBot` (testbot.py --cycle, 5dk). Hepsi StartWhenAvailable + pilde çalışma açık. Panel kalıcı görev DEĞİL — elle başlat.
5. Alarm (opsiyonel): Telegram @BotFather → token'ı `kripto-config.json → telegram_bot_token`, bota `/start`, chat_id'yi `getUpdates` ile bul.

## Kullanım
```bash
python tarayici.py --n 10                    # iki yönlü tarama → kısa liste
python radar.py                              # öncü imza + Pillar D + rejim
python olcucu.py --symbol WLD --side short --entry 0.62   # PLAN fiyatından giriş/SL/TP/R-R
python olcucu.py --symbol WLD --mtf          # çoklu-TF + erken belirti + basis
python piyasa_yapisi.py                      # dominans + alt/BTC + para_rejim
python arsiv_analiz.py                       # edge base-rate ölçümü (arşivden)
python veto_analiz.py                        # veto: korudu mu fırsat mı (forward-return)
python katip.py                              # açık tahminler + karne
python makro.py && python fng.py             # D3/D4 deterministik girdiler
python kucukcap.py --id aixbt                # küçük-cap + Bekçi güvenlik
python faz4_check.py                         # sağlık + zamanlayıcı bayatlık
python nobetci.py --test                     # fırsat/pozisyon alarmı, uçtan uca test
python testbot.py --durum                    # SANAL bot karne (win-rate, ort. R, rejim×yön)
python panel_sunucu.py                       # dashboard: http://127.0.0.1:8787
```
Derin analiz için Claude Code'da `/kripto <SEMBOL>`.

## Güvenlik
- Anahtarlar yalnız `kripto-config.json`'da (repo'da değil). Gerçek portföy + tüm log/arşivler lokalde (`.gitignore`).
- Hiçbir ajan işlem/para çekme yapmaz; emir her zaman kullanıcıda.
- **TestBot SANALDIR** — hiçbir Binance API anahtarı/emri yok. Gerçek para geçişi ayrı, açık onay gerektiren adımdır.
- Eşikler tek kaynaktan: `kripto-config.json → esikler`.

## Sadeleştirme (2026-07-23)
Ölü kod + geçmiş tur‑logları `arsiv/`'e taşındı (gitignore'da, geri‑alınabilir): `likidasyon.py`, `coinalyze.py`+log, `testbot_*.tur*`/`veto_log.tur*`. Boş/yedek dosyalar temizlendi. **Çekirdek mantık, eşikler, `fikir-defteri.md` ve ölçüm scriptleri değişmedi.**
