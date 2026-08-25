# ÖN-KAYIT — `skor` ileri getiriyi tahmin ediyor mu?

**Yazılma tarihi:** 2026-08-25 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Neden:** `skor` botun **tek pozitif seçicisi**. LONG kapısı `skor ≥ 45`'e dayanıyor
ve bu eşik bugüne kadar **hiç doğrudan ölçülmedi.**

---

## 1 · Bugünkü kanıt bu ölçümü zorunlu kıldı

Boğa bacağı ölçümünde (2026-08-25), zorunlu mekanik-eşitlik sınamasını **geçen** tek
karşılaştırma şuydu:

```
                      stop genisligi  stop-olma  TP1    net/notional
golge pump skor<45        %4,89          %92     %61      +2,915%
testbot LONG (skor>=45)   %4,87          %92     %39      +0,182%
golge pump skor>=45       %6,33          %97     %37      +1,224%

golge skor>=45  vs  testbot LONG  ->  t = -0,14   (AYIRT EDILEMEZ)
```

Botun eşiği uygulanınca üstünlük **tamamen** kayboluyor. Ayrıca `43_portfoy`
(2026-08-25) *"skor tahmin etmiyor (t=+0,42)"* demişti. İkisi birlikte şunu ima
ediyor: **kapı boğada ters yarıyı seçiyor olabilir.**

## 2 · Veri — KOŞU A (tam tarama evreni), gizli seçilim YOK

`radar_archive.jsonl` · **184.373 satır** · 441 sembol · **2026-06-24 → 2026-08-25**
(61 gün). Alan doluluğu ölçüldü:

| kullanılacak (%100) | **kullanılmayacak** (gizli seçilim) |
|---|---|
| `score` `stage` `comp` `vol_x` `pos` `last1` `last3` `mcap` `dip_yakit` `ayrisma` `rel3` `funding` `oi3` `oi24` | `top_ls` `smart` `glob_ls` `taker` (**%24,7**) · `chg24` `erken` `vol_x_gun` (**%20,5**) |

🔴 **KOŞU B (skor-süzülmüş evren) bu ön-kayıtta YOKTUR.** İki evren karıştırılmaz
(`olcumler.md` → `top_ls` çöküşü: keşif t=+7,07 süzülmüş kümede, sınama t=+0,22 ham
taramada).

⚠️ `chg24` %20,5 dolu olduğu için **karıştırıcı ondan kurulamaz** → oynaklık
`klines_1h_uzun`'dan **ATR** olarak hesaplanır (%100 kullanılabilir).

**Boşluk denetimi:** `radar_bosluk.jsonl` okunur ve kapsam raporlanır
(`CLAUDE.md`: arşiv NOKTASAL veridir, kayıp kareler geri gelmez).

## 3 · Birim ve ölçülen büyüklük

**Birim:** `(sembol, saat)` — her saatteki **ilk** anlık görüntü. Aynı sembolün
15 dakikalık tekrarları tekilleştirilir.

**Giriş anı — ileriye bakma YOK:** anlık görüntü saat içinde herhangi bir dakikada
olduğu için, giriş o saatin kapanışı değil **BİR SONRAKİ** saatin kapanışıdır.

```
ham ileri getiri = c[h+1+H] / c[h+1] - 1        H = 24 saat (BIRINCIL)
                                                H =  6 saat (ONCEDEN ILAN EDILMIS ikincil)
```

İki ufuk da **önceden** ilan edilmiştir; ikisi de raporlanır, hiçbiri sonradan
seçilmez. (Geçen ölçümde ufuk-strateji uyumsuzluğu bir sınır olarak kaydedilmişti;
`H=6` onun için var, botun medyan tutması ~1,8 saat.)

Aşama: **HAM** — stop yok, hedef yok, fonlama yok.

## 4 · Bantlar (önceden sabit, botun eşiği sınırda)

```
<2  ·  2-5  ·  5-10  ·  10-20  ·  20-30  ·  30-45  ·  >=45
```

Dağılım ölçüldü: medyan 7,90 · `≥45` olan **%2,6** · `≥40` olan %4,1.

## 5 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

| # | ölçüt | eşik |
|---|---|---|
| **S1** | monotonluk + uç fark | bant ortalamaları üzerinde Spearman ρ ≥ **+0,75** **ve** (`≥45` − `<2`) ≥ **+0,5 puan** ile gün-kümeli t ≥ **+2,5** |
| **S2** | işaret tutarlılığı | `≥45` vs `<45` günlük eşleşmiş fark, **≥%60 günde** pozitif (her iki kolda o gün N≥10) |
| **S3** | 🔴 **BELİRLEYİCİ** karıştırıcı | ATR beşlik dilimleri **ve** `vol_x` bantları içinde gradyan **≥%60 hücrede aynı işaretle** ayakta |
| **S4** | şans | `score` gün içinde karıştırılır (permütasyon) × 2000 → **p ≤ 0,05** |
| **S5** | rejim (keşifsel rapor) | NOTR / BOGA / AYI ayrı; işaret dönüyorsa **aynen yazılır** |

**S3 DÜŞERSE HÜKÜM DÜŞTÜ** — skor oynaklığın vekiliyse yön tahmin etmiyor demektir.

**GEÇTİ** = S1+S2+S3+S4 · **ZAYIF** = S1+S3, biri düştü · aksi **DÜŞTÜ**.

**Ek zorunlu rapor:** her bandın ATR/fiyat medyanı ve N'i · gün sayısı · boşluk kapsamı.

## 6 · BEKLENTİ — sonuç görülmeden yazıldı

**Skorun yönü tahmin ETMEDİĞİNE ~%65 veriyorum.** Üç gerekçe:

1. `43_portfoy` zaten t=+0,42 bulmuştu (portföy aşamasında, farklı yöntem).
2. Bu projede *"her yeni aday erken fiyat hareketinin başka bir ifadesi çıkıyor"*
   kuralı **beş kez** doğrulandı; `skor` bir **bileşik ısı ölçüsü** ve en olası
   sonucu **oynaklığın vekili** olması — yani S3'te ölmesi.
3. Botun canlı karnesi: `skor ≥ 45` kapısından geçen LONG'lar boğa bacağında
   **−13,56%** yaptı.

**Ayrıca yönlü bir tahmin yazıyorum:** eğer bir gradyan çıkarsa **BOGA'da negatif**
olmasını bekliyorum (bugünkü golge bulgusu bunu ima ediyor), NOTR'de düz.
Bu tahmin tutmazsa **aynen raporlanır.**

## 7 · Dokunulmayanlar

Bot · state · defterler · zamanlanmış görevler: **hiçbiri**. Ayrı süreç, salt-okuma.
`radar_archive.jsonl` **context'e yüklenmez** — Python toplar, özet basar.
Betik: `scratchpad/skor_tahmin.py` (bu commit'ten SONRA yazılır).
