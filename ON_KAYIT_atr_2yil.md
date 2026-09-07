# ÖN-KAYIT — `ATR/FİYAT`, 2 YILLIK MEKANİK BORU HATTINDA

**Yazılma tarihi:** 2026-09-07 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"2.'sini yap"* (ATR/fiyat'ı 738 günde ölç)
**Betik:** `scratchpad/atr_fiyat/02_uzun.py`
**Önceki:** `ON_KAYIT_atr_fiyat.md` (`8273a10`, 2026-09-06) → **GÖREMİYORUZ**

---

## 1 · NEDEN — tek eksik GÜN SAYISIYDI

`8273a10` sonucu (`N=2.082 · 72 gün`, `radar_archive`, skorlu girişler):

```
V1 holdout fark > 0            GECTI   +0,6605
V2 gun-kumeli t >= 2,0         DUSTU   t = +1,38  <- yalniz 25 gunde iki hucre dolu
V3 |fark| > MDE                GECTI   0,6605 > 0,4956   <- O GUN ILK KEZ
V4 kesif+holdout ayni isaret   GECTI
V5 negatif kontrol temiz       GECTI
```

Holdout tablosu **kusursuz monotondu**: `ATR %1,70 → R +0,5096` … `%7,08 → −0,1509`.
Kayıt: *"eksik olan tek şey gün sayısı."*

Bugün `stop_likidite` için kurulan **2 yıllık mekanik boru hattı**
(`02_uzun.py`, `N=82.085 · 738 gün · 554 sembol`) o eksiği kapatabilir.

## 2 · 🔴 BU İKİNCİ BAKIŞ — bedeli ödeniyor

```
t esigi 2,0 -> 2,5
```

⚠️ **Popülasyon değişiyor:** skorlu (`radar_archive`) değil, **mekanik**
(günde bir örnek, faz kaydırmalı). Yani soru *"botun girişlerinde"* değil
*"genel olarak"*. Geçse bile taşınabilirlik **ayrı adımdır**.

🔴 **ÜÇÜNCÜ BAKIŞ OLMAYACAK.** Ne çıkarsa çıksın bu hipotez kapanır;
yeniden açılması yalnız **taşınabilirlik** sorusuyla olur.

## 3 · 🔴 ORTAK PAYDA — ve neden yine de `R` birincil

`R = net% / stop%` ve `stop% ≈ 1,5 × ATR/fiyat` (girişlerin **%56,4**'ünde
ATR yedeği bağlıyor, `8273a10`'da ölçüldü). Yani `R`'nin **paydası**
ölçtüğümüz değişkenle ilişkili.

🔴 Bu, `CLAUDE.md`'nin *"ortak paydalı oran sahte korelasyon üretir"*
kuralının **sınırında**. Ama:

- **Yasak olan KORELASYONDUR**, dilim karşılaştırması değil. Spearman
  **koşulmayacak** (önceki ön-kayıtta da yasaktı).
- `R`, **sabit dolar riskiyle işlem yapanın gerçekten kazandığı birimdir**.
  Karar-ilgili metrik odur.

🔑 **Ama artefakt riski gerçek:** dar stoplu (düşük ATR) hücrede aynı fiyat
hareketi **daha büyük `R`** verir. Piyasa geneli yukarı sürüklenirse düşük
ATR sahte üstünlük gösterir.

**Bu yüzden ZORUNLU İKİZ SINAMA:**

```
BIRINCIL : ort R farki (en dusuk ATR dilimi - en yuksek)
ZORUNLU  : HAM net% farki AYNI ISARETTE olmali
           -> isaretler AYRISIRSA hukum "PAYDA ARTEFAKTI" yazilir,
              R gecse bile KURAL YAZILMAZ
```

## 4 · TASARIM — eşik ARANMAZ

```
POPULASYON : klines_1h_uzun · mekanik ornek (gunde 1, faz kaydirmali)
             asgari_stop kapisi · olcucu uclu stop · %10 hedef · 48s · %0,09
             (02_uzun.py ile BIREBIR)
DEGISKEN   : ATR14 / fiyat x 100   (giristen ONCEKI kapanmis barlardan)
BOLME      : besli dilim · EN DUSUK vs EN YUKSEK  (onceden ilan)
KESIF/HOLD : ilk %60 gun / son %40 gun  (zamana gore)
```

## 5 · ÖLÇÜTLER — sonuç görüldükten sonra değişmez

| # | ölçüt | eşik |
|---|---|---|
| **B1** | HOLDOUT: en düşük − en yüksek ATR dilimi, **ort R** | **> 0** |
| **B2** | HOLDOUT: gün-kümeli **t ≥ +2,5** | ikinci bakışın bedeli |
| **B3** | \|fark\| > **MDE** | evet |
| **B4** | KEŞİF ve HOLDOUT **aynı işaret** | evet |
| **B5** | 🔴 **HAM net% farkı AYNI İŞARETTE** (payda artefaktı sınaması) | evet |
| **B6** | **negatif kontrol** (gün içi permüte, aynı hat) temiz | evet |
| **B7** | **sembol-kümeli t ≥ 2,5** (etki tek tük sembolden gelmiyor) | evet |

```
YON VAR          = B1..B7 hepsi
PAYDA ARTEFAKTI  = B1..B4 gecer ama B5 duser      <- ayri ve onemli sonuc
SEMBOLE OZGU     = B1..B6 gecer ama B7 duser
YON YOK          = B1 veya B4 duser
GOREMIYORUZ      = B1+B4+B5 gecer, B2/B3 duser
```

🔴 **`B7` bugünün dersinden geliyor:** `stop_likidite` bulgusu çökerken
`A7` (sembol kümelemesi) geçmişti ve bu, etkinin *"her sembolde var"*
olduğunu gösterip beni yanıltmadı — ama **eksik olsaydı** yanıltırdı.

## 6 · ⚠️ BUGÜNÜN HATASINI TEKRARLAMAMAK İÇİN

Bugün `stop_likidite` bulgusu **`ATR/fiyat` karıştırıcısı** yüzünden çöktü.
Burada `ATR/fiyat` **değişkenin kendisi** — yani o hata bu ölçümde
**yapısal olarak** olamaz. Ama tersi olabilir:

🔴 **`ATR/fiyat` başka bir şeyin vekili olabilir mi?** Zorunlu ek rapor:
dilimler boyunca **fiyat düzeyi (`log fiyat`)**, **hacim**, ve **stop
mesafesi** nasıl değişiyor. Ayrışma varsa **yazılır** — hüküm kurmaz ama
sonraki adımın konusudur.

## 7 · NE YAPILMAZ

- Bota/state/deftere **dokunulmaz** · ücretli çağrı **YOK**
- Eşik **aranmaz** · faz **kaydırılır** · katsayılar öncekinden **aynen**
- **Spearman KOŞULMAZ** (`R` ile paydasındaki değişken)
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 8 · GEÇERSE

1. **Taşınabilirlik**: botun evreninde (`radar_archive`) aynı etki var mı
2. Sonra **portföy simülasyonu** — ⚠️ oynak coinleri elemek **işlem
   sayısını azaltır**, pencere hızı düşer
3. 🔴 **Kod otomatik değişmez.**

## 9 · BEKLENTİM — koşumdan önce

**`B1..B4`'ün geçmesine %55.** Önceki ölçümde `V1/V3/V4/V5` geçmişti ve
holdout **kusursuz monotondu**; eksik olan yalnız güçtü, ve güç `40 kat`
arttı.

**`B5`'in (payda artefaktı) geçmesine %45** — asıl risk burada.

**Hepsinin geçmesine %30.**

⚠️ Bugün **yirmi ön-kayıt yazıldı, yirmisi de kural üretmedi.** Biri
(`stop_likidite`) yedi ölçütü geçip **karıştırıcıda çöktü**.
