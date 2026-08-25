# ÖN-KAYIT — "hareketin bittiği nokta 2. yönü gösterir"

**Yazılma tarihi:** 2026-08-25 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı hipotezi — *"hareket var, hareket başlangıcı, hareketin bittiği
nokta olarak 2. yönü gösterir"* → pump bitince **ters yöne (SHORT)** gir.

---

## 1 · Neden bu ölçüm — mekanizma somut

Bugün üretilen tetik tablosu (18.420 pump, 2 yıl, `chg24 ≥ +%10` ve `vol_x ≥ 2,0`):

```
ham +24s   medyan -2,43%   ort -0,448%   pozitif %37
SHORT      ort +0,448%     kazanan %62
  ama  %5,2'si  >+20% DEVAM ediyor   ortalama +42,5%   <- SHORT'un felaketi
       %2,8'i   <-20% cokuyor        ortalama -29,7%
```

SHORT'un brüt kenarı **+0,448%**; maliyet `%0,1726 × 2 = %0,345` → net **~+0,10%**.
Kenarı yiyen tek şey **%5,2'lik devam kuyruğu**. Hipotez tam olarak o kuyruğu
kesmeyi hedefliyor: *"hareket bitmeden girme."*

## 2 · Yakınındaki İKİ ÖLÜ ölçüm (bu ön-kayıt onları tekrar etmiyor)

| ölçüm | ne yaptı | sonuç |
|---|---|---|
| **Boşluk 1 — "son yeni uçtan geçen süre"** (2026-08-19, `olcumler.md:1226`) | AÇIK pozisyonda *"hedefe varacak mı"* | ❌ 11,8 puan → kâr sabitlenince **2-4 puan**, işaret döndü. *"Dizi sandığım şey seviyenin kılığıymış."* |
| **Kapı karnesi — pump'ı shortlamak** | `chg24 ≥ %20` / `≥ %40` **seviyesine** bakarak SHORT | ❌ ham **−2,1799** / **−4,4757** |

**Boşluk:** ikisi de *"pump BİTTİ mi"* diye sormadı. (1) açık pozisyon sorusuydu,
(2) seviye sorusuydu. Bu ön-kayıt **taze SHORT girişi × hareketin bitişi** bileşimini
sınar — hiç ölçülmedi.

## 3 · Veri

`scratchpad/klines_1h_uzun/` · 546 sembol · 1 saatlik · **2024-12-23 → 2026-08-25**
(rejim etiketi de taşınsın diye aynı pencere; ~20 takvim ayı = **20 küme**).
Aşama: **HAM** — stop yok, hedef yok, **fonlama yok**.

⚠️ Fonlama bilerek dışarıda: pumplanmış coinde fonlama tipik olarak **pozitif**,
yani SHORT **tahsil eder** → ham ölçüm SHORT için **muhafazakâr**. Fonlama mekanik
aşamada `scratchpad/fonlama_oku.py` ile (birim doğrulamalı) eklenir.

## 4 · Tanımlar (hepsi nedensel — ileriye bakmaz)

**Olay (hareket başlangıcı):** pump tetiği bar `i` — `chg24 ≥ +%10` ve `vol_x ≥ 2,0`,
sembol başına 24 saatte tek.

**Hareketin bitişi (detektör):** `hh(j) = max(high[i..j])`. İlk `j > i+M` barı ki

```
hh(j) == hh(j-M)          yani son M barda YENI TEPE YOK
```

**M = 6 saat BİRİNCİL.** `M = 3` ve `M = 12` **keşifsel** (Bonferroni |t| ≥ 3,0).
48 saat içinde bitiş yoksa olay **atılır** (*"hâlâ sürüyor"* diye ayrıca sayılır).
Olay başına **tek** giriş (ilk bitiş barı).

**Kollar:**

| kol | giriş barı |
|---|---|
| **A — ÖNERİ** | hareket-bitiş barı `j` |
| **B — kontrol (seviye)** | `i+1..i+48` arasındaki **bitiş olmayan** barlar, kovaya göre eşleştirilir |
| **C — temel** | tetik barı `i`'nin kendisi (*"pump'ı hemen shortla"*) |

**Sonuç:** SHORT ham getirisi `= −(c[k+24]/c[k] − 1)`, **H = 24 saat**.

**Kovalar (önceden sabit):**
- `geçen` (tetikten bu yana saat): `1-6` · `7-12` · `13-24` · `25-48`
- `kazanç` (girişteki kümülatif, tetik kapanışına göre): `<-5%` · `-5..0` · `0..5` · `5..15` · `>15%`

## 5 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

| # | ölçüt | eşik |
|---|---|---|
| **H1** | `A − C` ortalama | ≥ **+0,5 puan** **ve** ay-kümeli t ≥ **+2,5** (küme = takvim ayı, her iki kolda N≥30) |
| **H2** | kuyruk kesildi mi — SHORT getirisi `< −20%` olan pay | `A` payı ≤ **0,60 × C** payı (≥%40 kesme) |
| **H3** | 🔴 **BELİRLEYİCİ — karıştırıcı** | `geçen × kazanç` kovalarında (her iki kolda N≥50), `A > B` **≥%60 kovada aynı işaretle**; ayrıca N-ağırlıklı `A−B` > 0 ve ay-kümeli t ≥ **+2,0** |
| **H4** | şans | olay başına rastgele giriş barı × 2000 çekiliş → **p ≤ 0,05** |
| **H5** | maliyet sonrası (rapor) | `A` ortalaması − 0,345 > 0 |

**🔴 H3 DÜŞERSE HÜKÜM OTOMATİK DÜŞTÜ** — diğerleri geçse bile. Çünkü o durumda
sinyal *"pump ne kadar yaşlandı / ne kadar kazandı"*ın vekilidir ve bu, 2026-08-19'da
aynı fikri öldüren tam kusurdur. **Dördüncü kez aynı duvar** diye yazılır.

**GEÇTİ** = H1+H2+H3+H4 · **ZAYIF** = H1+H3+H4, H2 düştü · aksi **DÜŞTÜ**.

**Ek zorunlu rapor:** her kolun ATR/fiyat medyanı (bantlar oynaklıkta ayrışıyorsa
mekanik aşamada ham getiri zorunlu kalır) · `hâlâ sürüyor` oranı · rejim kırılımı
(keşifsel).

## 6 · BEKLENTİ — sonuç görülmeden yazıldı

**Geçme olasılığı ~%20.** Gerekçeler:

1. En yakın iki ölçüm de düştü ve **birincisi tam bu kusurdan** (dizi sanılan şey
   seviyenin vekiliydi). H3'ün düşmesini en olası tek sonuç olarak görüyorum.
2. Brüt kenar zaten ince (+0,448%) ve maliyet (%0,345) neredeyse tamamını yiyor;
   H1'in +0,5 puanı geçmesi kuyruğun **ciddi** kesilmesini gerektirir.
3. **Ama karşı argüman gerçek:** kuyruk spesifik ve mekanizma doğrudan ona nişanlı.
   Bu, *"bir sayı yüksek çıktı"* türünden bir aday değil; önce nedeni söylendi,
   sonra ölçülüyor. Bu projede o sıra nadiren tutturuldu.

Beklentinin yanlış çıkmasını isterim; ölçütler yukarıda **sabittir**.

## 7 · Dokunulmayanlar

Bot · state · defterler · zamanlanmış görevler: **hiçbiri**. Ayrı süreç, salt-okuma.
Betik: `scratchpad/hareket_bitisi_short.py` (bu commit'ten SONRA yazılır).
