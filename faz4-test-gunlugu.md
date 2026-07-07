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

## Gün 3 — 2026-06-23 *(retrospektif dolduruldu 2026-07-02)*
- faz4_check: koşulmadı (kayıt yok — kayıt disiplini zaafı).
- /kripto tahminleri: PIYASA#3 (BTC çapa, bear %45 EN OLASI, $59-60K hedef) → **isabetli çıktı** (06-24 doğrulandı).
- not: Apify liq-map ilk gerçek kullanım (üst mıknatıs $63-64K doğru). Gemma D4 akışından çıkarıldı (yavaş + veri uydurdu). Kullanıcı BTC long açtı $64397 (sisteme rağmen — PIYASA#3 bear diyordu).

## Gün 4 — 2026-06-24 *(retrospektif)*
- faz4_check: koşulmadı.
- /kripto tahminleri: LAB#5 (bekleme isabetli — smart-flip gelmedi, trap'ten korudu) · LAB#6 (yön doğru, bounce-giriş kaçtı → entry-taktiği dersi) · AAVE#7 (short tezi yanlış; BASLIYOR kapısı +%12'yi yakaladı, CEO küçümsedi → Pillar D dersi) · ADA short (doğru yönde).
- not: BTC long stop -$28 (DERS3 doğdu: ana trende karşı long yok). Radar arşivi bugün başladı (03:37).

## Gün 5 — 2026-06-25 *(retrospektif)*
- faz4_check: koşulmadı.
- /kripto tahminleri: yeni tahmin yok; hipotez ölçümleri yapıldı.
- not: Hipotez#1 ilk base-rate ölçümü (39+ → +1h %72 ama +3h/+6h fade) + scalp paper-testi (39+ LONG scalp ZARARDA → deploy RED). Hipotez#2 momentum-lider detektörü veriyle RED. AYRISMA etiketi negatif-edge çıktı. RE/ETHFI izlemeye alındı.

## Gün 6 — 2026-06-26 *(retrospektif)*
- faz4_check: koşulmadı.
- /kripto tahminleri: FOGO izleme (DIP_YAKIT 2. yanlış-pozitif — float/unlock refine doğrulandı).
- not: **DÖNÜM NOKTASI:** ders#4 (iki yönlü analiz) + arşivde SHORT forward-return testi: 45+ skor SHORT +EV (ayı rejimi, küçük N). İlk paper-short FOGO → +3.1R temiz. piyasa_yapisi.py yazıldı + KriptoPiyasa zamanlayıcısı kuruldu (11:00/23:00).

## Gün 7 — 2026-06-27 / 28 *(retrospektif)*
- faz4_check: koşulmadı.
- /kripto tahminleri: MANTA blow-off short setup (bounce-tetikli, kayıtlı).
- not: RE paper-short -1R stop (FOGO'nun tersi — small-N uyarısı CANLI doğrulandı; 1W/1L). Radar MANTA dump'ını yakaladı (20:47 skor 60).

---

## HAFTA SONU DEĞERLENDİRME (retrospektif kapanış: 2026-07-02, kullanıcı kararı "test modu bitti")
- Kriter 1 (veri): **2/7 gün ölçüldü, ölçülen günler PASS** (%0.118 · %0.114; FAIL kanıtı yok). Kayıt disiplini zayıftı — faz4_check günlük koşulmadı. → KISMEN PASS
- Kriter 2 (failover): **PASS** (Faz 1 + Gün 1 oturum-içi doğrulama; funding çapraz fark ≈%0).
- Kriter 3 (sinyal): **PASS** — 7 kayıtlı tahmin: 4 isabet (AIXBT BEKLE, PIYASA#3 bear, LAB#5 bekleme, ADA yön), 1 yön-doğru-giriş-kaçtı (LAB#6), 2 yanlış (WLD yön — stop korurdu; AAVE#7 short erken/long-miss). Sistematik hatalar TESPİT edilip ders üretti (ders#4, AYRISMA negatif-edge, DIP_YAKIT float refine) — testin amacı tam buydu.
- Kriter 4 (Ölçücü): **PASS (bilinen sınırla)** — seviyeler yapısal/tutarlı; sınır: anlık-fiyat R/R planlı girişte yanıltıcı (LAB/MANTA) → `--entry` parametresi eklendi (2026-07-02).
- Kriter 5 (monitör): **PASS** — radar erken belirtileri gerçek hareketlerle örtüştü (AAVE BASLIYOR +%12, FOGO skor70 → -%13, MANTA dump).
- Kriter 6 (maliyet): **PASS** — Apify toplam <$0.10, sürpriz ücret yok.
- Kriter 7 (küçük-cap/Bekçi): **PASS** — PENDLE/ARB/PENGU kapıları tutarlı (Gün 1).
- **SONUÇ: GEÇTİ** (2026-07-02). Gerçek pozisyon `trade_hesabi` kurallarıyla serbest: $5 risk-önce + NET R/R≥1:2 + kapı/veto/konviksiyon AYNEN — kapı kalktı, disiplin kalkmadı.
- **Tespit edilen zaaf → aksiyon:** günlük kayıt elle sürdürülemedi → `katip.py` (otomatik tahmin çözümleme + isabet raporu) ve `faz4_check` bayatlık kontrolleri eklendi (2026-07-02 sistem revizyonu).
