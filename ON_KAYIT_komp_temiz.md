# ÖN-KAYIT — POZİSYON KOMPOZİSYONUNUN **TEMİZ** AYRIŞTIRMASI

**Yazılma tarihi:** 2026-09-06 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-06): *"önce ölç olumlu çıkarsa botu ona göre sıfırlarız"*
**Betikler:** `scratchpad/komp_temiz/01_indir.py` · `02_olcum.py`

---

## 1 · NEDEN — bu, `CLAUDE.md`'nin BİRAKTIĞI TEK BANT-DIŞI ADAY

Bant-dışı liste kapandı: basis ❌ · çapraz borsa ❌ · OBI ❌. Kalan tek madde:

> *"Geriye denenmemiş **tek** şey kaldı: pozisyon kompozisyonunun **temiz**
> ayrıştırması (`topPosition/topAccount`) — `metrics` arşivi sayesinde artık
> 2 yıl geriye mümkün."*

## 2 · 🔴 ÖNCEKİ ÖLÇÜM **ELMA İLE ARMUT**TU — bu ön-kaydın çekirdeği

Bugüne kadar `komp` şöyle hesaplandı:

```
komp = top_ls - glob_ls
     = topLongShortPositionRatio - globalLongShortAccountRatio
       ^^^^^^^^ POZISYON                       ^^^^^^^ HESAP
```

**İki farklı birim çıkarılıyordu.** `top_ls` pozisyon büyüklüğü oranı,
`glob_ls` hesap sayısı oranı. Farkları anlamlı bir büyüklük değil.

`metrics` arşivi eksik parçayı taşıyor — `count_toptrader_long_short_ratio`
(= `topLongShortAccountRatio`), **bizim hiç arşivlemediğimiz alan**:

```
data/futures/um/daily/metrics/<SYM>/<SYM>-metrics-<YYYY-MM-DD>.zip
  count_toptrader_long_short_ratio  = ust-trader HESAP orani   <- YENI
  sum_toptrader_long_short_ratio    = ust-trader POZISYON orani (eski top_ls)
  count_long_short_ratio            = tum hesaplar HESAP orani  (eski glob_ls)
  sum_taker_long_short_vol_ratio    = taker orani
  sum_open_interest(_value)
⚠️ create_time = canli ucun damgasi - 5 dk  (CLAUDE.md)
```

## 3 · ÖLÇÜLECEK DEĞİŞKENLER

| # | değişken | formül | ne sorar |
|---|---|---|---|
| **V1** | `komp_temiz` | `count_toptrader − count_global` | ⭐ üst-trader'lar kalabalıktan **daha mı** long? **AYNI BİRİM** |
| **V2** | `buyukluk_egimi` | `sum_toptrader / count_toptrader` | ⭐ **HİÇ HESAPLANAMAMIŞTI** — üst-trader'ların long pozisyonları hesap başına **daha mı büyük**? (konviksiyon) |
| V3 | `count_toptrader` | ham | üst-trader hesap duruşu |
| V4 | `count_global` | ham | kalabalık duruşu |
| V5 | `sum_toptrader` | ham | eski `top_ls` — **yineleme kontrolü** |
| V6 | `komp_kirli` | `sum_toptrader − count_global` | ⚠️ **eski ELMA-ARMUT** — `CLAUDE.md` "bulgu yok" demişti; temizi çalışıp kirlisi çalışmazsa bu **açıklayıcı** olur |

⭐ = birincil. **V1 ve V2 dışındakiler kontroldür**, hüküm kurmaz.

## 4 · 🔴 TASARIM — ÖNCEKİ İKİ ÖLÇÜMÜN HATASI DÜZELTİLDİ

Bugün arka arkaya iki ön-kayıt aynı aileden hata yaptı:
`taker` (etki tabanı MDE'siz kondu) ve `funding/L-S` (MDE bağımsızlık varsaydı,
sahte değişken `+0,0272` verdi, `olcumler.md`). **Üç düzeltme, koşumdan önce:**

**(a) SAHTE TEKRAR YOK — sembol-gün başına TEK gözlem.**
```
gunluk kesit: her gun, her sembol icin BIR olcum
saat: (gun_sirasi mod 24) -> DONEN saat   <- SEYRELT faz-kilidi tuzagi (CLAUDE.md)
ileri getiri: +24s, ORTUSMESIZ
```
Sabit `00:00 UTC` sürümü ayrıca **sağlamlık** olarak raporlanır.

**(b) İSTATİSTİK Fama-MacBeth — gün başına kesitsel rho, sonra günler üzerinde t.**
Bu, *"bugün hangi coini seçmeli"* sorusunun **doğru** istatistiğidir ve
kümelemeyi tanımı gereği halleder.

**(c) ETKİ TABANI ÖLÇÜLÜR, UYDURULMAZ.**
```
NULL: her gun, degisken semboller arasinda RASTGELE PERMUTE edilir
      -> 200 tekrar -> null dagilimin %95 kuantili = ESIK
```
🔴 **Eşik koşumdan önce SAYI olarak yazılmaz — çünkü veriden türetilir.**
Yazılan şey **yöntemdir** ve o değişmez. Null hesaplanır, **sonra** gerçek
değerle karşılaştırılır; null bir kez hesaplandıktan sonra yeniden ayarlanmaz.

## 5 · POPÜLASYON — koşumdan önce SABİT

```
EVREN : scratchpad/pozisyon_komp/evren150.txt  (150 sembol)
        = radar_archive'da EN SIK gorulen, klines_1h_uzun'da mumu olan ilk 150
        en seyrek secilenin kayit sayisi 267 -> hepsi botun gercek evreninde
PENCERE: 2025-09-06 .. 2026-08-25  (klines_1h_uzun'un bittigi gun)
        ~354 gun x 150 sembol = ~53.100 sembol-gun
FIYAT  : klines_1h_uzun (mevcut, EZILMEZ)
```

⚠️ Evren `radar_archive` sıklığına göre seçildi — bu bir **hayatta kalma
yanlılığıdır** (bugün listede olan semboller). Yön ölçümünde etkisi sınırlı
ama **kayda geçiyor**.

## 6 · GEÇME ÖLÇÜTLERİ — koşumdan önce sabit

| # | ölçüt | eşik |
|---|---|---|
| **G1** | Fama-MacBeth `\|t\|` (günlük kesitsel rho, +24s) | **≥ 2,5** |
| **G2** | ortalama kesitsel `\|rho\|` > permütasyon null'ının **%95 kuantili** | evet |
| **G3** | pencere **iki yarıya** bölünür, işaret aynı | evet |
| **G4** | ufuk merdiveninde (`+4s · +24s · +72s`) ≥2 basamak aynı işaret | evet |
| **G5** | `last1` (son 1s getiri) kesit içinde sabitlenince işaret korunur | evet |

```
BILGI TASIYOR = G1..G5 hepsi
BOS           = G1 veya G2 duser
BELIRSIZ      = G1+G2 gecer, biri duser -> "aday", hukum DEGIL
```

🔴 **G1 eşiği 2,5** (2,0 değil): iki birincil değişken × 3 ufuk = **6
karşılaştırma**; `2,5` kabaca Bonferroni'li `2,0`ye denk.

## 7 · SONUÇ NE İŞE YARAR — kullanıcının şartı

Kullanıcı: *"olumlu çıkarsa botu ona göre sıfırlarız"*.

- **BİLGİ TAŞIRSA:** 🔴 doğrudan bota **eklenmez**. Sıra: (1) botun kendi
  mekaniğiyle (sabit %10 hedef · A-stop · 48s) **ikinci** bir ölçüm;
  (2) ancak o da geçerse kapı önerisi + pencere sıfırlama.
  Ham getiride görünen bir kenarın mekanikte kaybolduğu bu projede **ölçüldü**.
- **BOŞ ÇIKARSA:** bant-dışı liste **tamamen** kapanır (dört adayın dördü).
  O zaman `notrlong` mevcut hâliyle, `taker` kaldırılarak koşar.

## 8 · NE YAPILMAZ

- Bota, state'e, defterlere, görevlere **dokunulmaz** (salt-okuma)
- Ücretli çağrı **yok** (`data.binance.vision` ücretsiz)
- `klines_1h_uzun` **EZİLMEZ**; metrics ayrı dizine, `.gitignore`'a
- En iyi hücre **seçilmez**; null bir kez hesaplanır, ayarlanmaz
- `rejim` alanı **okunmaz** (2026-07-22 tanım değişikliği)
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 9 · BEKLENTİM — koşumdan önce, olasılıkla

| değişken | G1..G5 geçme | gerekçe |
|---|---|---|
| **V1** `komp_temiz` | **%25** | kirli hâli boş çıktı; temizlemek işareti kurtarabilir ama aynı bilgiyi taşıyor olması daha olası |
| **V2** `buyukluk_egimi` | **%30** | tek gerçek **yeni** büyüklük; hiç ölçülmedi, o yüzden en yüksek şansı buna veriyorum |
| V3-V6 | %10 | hepsi zaten ölçülmüş ailelerin üyesi |

**En az birinin geçmesine %40.** Üç bant-dışı adayın üçü de düştüğü için
taban oranım düşük — ve `taker`/`funding` ölçümleri gösterdi ki bu arşiv
üzerinde küçük etkiler **görülemiyor**.

⚠️ Ve şu şimdiden yazılıyor: **V2 geçerse bile bu bir kapı değildir.**
Bölüm 7'deki iki adımlı sıra bağlayıcıdır.
