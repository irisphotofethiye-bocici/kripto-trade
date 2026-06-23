# FAZ 4 — 1 Haftalık Tam Test Günlüğü

**Başlangıç:** 2026-06-21 · **Bitiş (hedef):** 2026-06-28
**Kural:** Bu kapı geçilmeden gerçek para kararına ve Faz 5+'a geçilmez. Sahte hızlandırma yok.

## Geçme kriterleri (hafta sonu değerlendirilir)
| # | Kriter | Eşik / PASS koşulu |
|---|--------|--------------------|
| 1 | **Veri doğruluğu** | Binance vs CoinGecko fark <%0.5 — 7/7 gün |
| 2 | **Failover** | Binance düşerse CoinDesk MCP devreye girer; funding çapraz fark <%20 (oturum içi en az 1 kez doğrulanır) |
| 3 | **Sinyal kalitesi** | Hafta boyunca üretilen tahminler (defter→tahminler) kayıtlı; yön/senaryo isabeti makul, sistematik hata yok |
| 4 | **Ölçücü seviyeleri** | Önerilen SL/TP fiyat davranışıyla tutarlı (gözlem); saçma seviye üretmiyor |
| 5 | **Monitör (--mtf)** | Erken belirti (volatilite/sıkışma/funding/OI) gerçek hareketlerle örtüşüyor mu |
| 6 | **Maliyet** | Günlük çağrı (web_search/Gemma) makul; sürpriz ücret yok |
| 7 | **Küçük-cap/Bekçi (Faz 5)** | `kucukcap.py` mcap+GoPlus kapıları doğru; Bekçi riskleri (honeypot/tax/mint/sahiplik) mantıklı yakalıyor |

## Günlük çalıştırma
1. `python faz4_check.py` → veri doğruluğu + erişim (1 & 6 otomatik)
2. `/kripto` normal kullanım → üretilen tahminler deftere yazılır (3)
3. Gün notunu aşağıya ekle.

---

## Gün 1 — 2026-06-21
- **faz4_check:** Binance spot OK · fapi OK · CoinGecko OK. Max fark **%0.118** (BTC %0.103, ETH %0.091, LINK %0.013, SOL %0.081, PENGU %0.118). → **VERİ_DOĞRULUĞU: PASS**, **ERİŞİM: PASS**
- **Failover (oturum içi):** Binance vs CoinDesk funding %0.0062≈%0.0062, fiyat <%0.1 → **PASS** (Faz 1'de doğrulandı)
- **Ölçücü:** LINK long R/R 0.19→VETO, BTC short R/R 2.6→geçer, PENGU long R/R 1.46→VETO. Seviyeler yapısal, tutarlı. → gözlem OK
- **Monitör:** LINK/BTC --mtf "YUKARI_EGILIM", erken belirti temiz.
- **Küçük-cap/Bekçi (Faz 5):** PENDLE $248M→küçük-cap + Bekçi UYARI (mintable); ARB $533M→büyük-cap; PENGU $429M→büyük-cap (Bekçi temiz). Kapılar tutarlı çalışıyor. → gözlem OK
- **Not:** LINK aktif pozisyon stop'u kullanıcı tarafından kaldırıldı (korumasız).

## Gün 2 — 2026-06-22
- faz4_check: Max kaynak farkı %0.114 → VERİ PASS, ERİŞİM PASS.
- /kripto tahminleri (dünkü 3 kararın takibi): AIXBT BEKLE **isabetli** (−%4, long olsaydı zarar) · WLD "kovalama" uyarısı **doğru** (−%2.7, giriş bölgesi $0.60‑61'e yaklaşıyor, değmedi) · LINK TUT korumalı (~yatay, stop $7.10 uzak). Disiplin (R/R veto + BEKLE) zarar önledi.
- not: Radar canlı (15dk, KriptoRadar). Piyasa risk‑off/sakin, güçlü pre‑move sinyali yok.

## Gün 3 — 2026-06-23
- faz4_check:
- /kripto tahminleri:
- not:

## Gün 4 — 2026-06-24
- faz4_check:
- /kripto tahminleri:
- not:

## Gün 5 — 2026-06-25
- faz4_check:
- /kripto tahminleri:
- not:

## Gün 6 — 2026-06-26
- faz4_check:
- /kripto tahminleri:
- not:

## Gün 7 — 2026-06-27 / 28
- faz4_check:
- /kripto tahminleri:
- not:

---

## HAFTA SONU DEĞERLENDİRME (2026-06-28)
- Kriter 1 (veri): __/7 gün PASS
- Kriter 2 (failover): PASS/FAIL
- Kriter 3 (sinyal): __ tahmin, isabet:
- Kriter 4 (Ölçücü): PASS/FAIL
- Kriter 5 (monitör): PASS/FAIL
- Kriter 6 (maliyet): PASS/FAIL
- Kriter 7 (küçük-cap/Bekçi): PASS/FAIL
- **SONUÇ:** GEÇTİ / KALDI → (Geçtiyse gerçek karar + Faz 6 tarayıcıya; kaldıysa düzelt + tekrar)
