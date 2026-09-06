# ÖN-KAYIT — NOTR-LONG BOTU (yeni test botu)

**Yazılma tarihi:** 2026-09-05 · **kurulmadan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-05): *"paneli temizle, NOTR-LONG botu kur, test
bot artık bu kuracağımız"* · *"skorda… şimdi kuracağımız botta test et"* ·
*"evet koy"*

---

## 1 · Bu bot NEYE dayanıyor — ve neye DAYANMIYOR

Bugün (2026-09-05) on iki ölçüm yapıldı. Bu botun tasarımı yalnız **ölçülmüş**
olanlardan kuruluyor.

### Konacaklar — hepsi ölçülmüş

| ne | ölçüm |
|---|---|
| **NOTR karar mantığı + YALNIZ LONG** | karşı-olgu: 08-19…09-02'de gerçek bot −4.630 $, `C` kolu **+1.162 $** (K1/K2/K3 geçti) |
| **Vetolar aynen** (`long_veto` · `onay_bekle` · `blowoff`) | gölge defter BOĞA penceresi: reddedilenler **−4.400 $** kaybettirmiş → veto **para kazandırıyor** |
| **Düşüş freni %25** | açık olsaydı bot −%25'te dururdu; kapalıyken −%31 oldu |
| **`islem_risk_pct` %1,5** | config portföy simülasyonu: %3→%1,5, 46-gün medyan çarpanı **1,24 → 2,49** |
| **`asgari_stop` %2** | olay başına +%0,58 → +%0,78, işlem %27 az |

### 🔴 KONMAYACAKLAR — hepsi ölçüldü ve BOŞ çıktı

| ne | ölçüm |
|---|---|
| **skor kapısı** | gerçek defterde `Q4−Q1 = −1,507%`, t=−0,68 · kapının kattığı **+0,006 puan** |
| fiyat seviyesi (ucuz/pahalı) | altı hücrenin altısı da görülemiyor, en büyük `\|t\|`=1,36 |
| stop genişliği değişikliği | üç pencerede de geçmedi |
| ilk/tekrar giriş kuralı | gerçek defterde **ters** çıktı |
| `pos<0.25` mekaniği | LONG-only defterde **0 pozisyon** (zaten `long_veto`'da) |

## 2 · 🔴 KARŞI-OLGU İLE BOTUN ÇIKIŞI AYNI DEĞİL — bu ön-kayıtta kapatılıyor

Karşı-olgu (`C` kolu, **+2,643%/işlem**) **sabit %10 hedefle** ölçüldü.
Ama `testbot`'ta sabit hedef yalnız `A+B` ve `MA50+ucuz` (ikisi de SHORT)
kapılarında; bir NOTR-LONG **kısmi kâr + iz-süren** çıkışı alır.

🔑 **Yani `C`'nin sonucu, botun fiilen yapacağı şeyle ölçülmedi.** Bugünün
tekrarlayan dersi tam bu: *"ikisi aynı şeyi mi ölçüyor?"*

**Karar (önceden sabit):** bot **sabit %10 hedefle** çalışır — karşı-olgunun
ölçtüğü çıkışla **aynı**. Kısmi kâr **kapalı** (ölçüldü: kenarı **~%9**
küçültüyor; başabaşa çekme daha da kötü: +0,274 → +0,261).

## 3 · BOTUN TANIMI

```
KARAR   : testbot.karar_yon(rejim_ad="NOTR", ...)  — rejim ZORLANIR
YON     : yalniz LONG (SHORT kararlari atilir)
EVREN   : evren.binance_pool("fapi", min_vol=3)[:150]   (mevcutla ayni)
VETOLAR : long_veto · onay_bekle · blowoff · asgari_stop %2  (AYNEN)
GIRIS   : kararin ertesi turunda (ONAY_BEKLE korunur)
CIKIS   : sabit %10 hedef · A-stop (LONG aynasi) · 48s zaman stopu
          kismi kar KAPALI · iz-suren KAPALI
BOYUT   : islem_risk_pct %1,5 · maks 8 slot · kaldirac [3,10]
FREN    : maks_dusus_pct %25
```

🔴 **Ayrı defter, ayrı dosya, ayrı zamanlanmış görev** (`defter2`/`defter3`
deseni). `testbot`'a **hiçbir değişiklik yapılmaz**; mevcut defterler
ölçümün tabanı olarak **korunur**.

## 4 · İKİ KOL — kullanıcının skor sorusu böyle cevaplanır

| kol | fark |
|---|---|
| **N1** | skor kapısı **YOK** (yalnız NOTR mantığı + vetolar) |
| **N2** | skor kapısı **VAR** (`skor ≥ 45`), başka her şey N1 ile **birebir aynı** |

🔑 **Tek değişken: skor kapısı.** İkisi aynı anda, aynı evrende, aynı
mekanikle koşar → `N1 − N2` doğrudan *"skor kapısı ne katıyor"*un cevabıdır.

⚠️ Bu, bugünkü ölçümün **ileri yönlü** sınamasıdır; geriye dönük sonuç
(+0,006 puan) bir **beklenti**, hüküm değil.

## 5 · DEĞERLENDİRME PENCERESİ — şimdi sabitleniyor

**İKİSİ BİRDEN dolmadan hüküm YOK:**

```
SURE  : 30 gun
N     : her kolda en az 80 KAPANMIS pozisyon
```

⚠️ **Pozisyon sayılırken `not kismi` süzgeci uygulanır; P&L toplanırken
UYGULANMAZ** (`id` ile birleştirilir) — `CLAUDE.md`'nin ölçülmüş tuzağı.

**Pencere boyunca parametre DEĞİŞTİRİLMEZ.** Değiştirilirse pencere yeniden
başlar (D/8).

## 6 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

**Birincil soru: bu bot para kazanıyor mu?**

| # | ölçüt | eşik |
|---|---|---|
| **K1** 🔴 | `N1` toplam realize (equity farkı − enjeksiyon) | **> 0** |
| **K2** | işlem başına net%, gün-kümeli t | **≥ +2,0** |
| **K3** | 🔴 **yoğunlaşma**: en iyi 2 gün ve en iyi 5 işlem ÇIKARILDIĞINDA hâlâ artı | evet |
| **K4** | düşüş freni tetiklenmemiş | evet |

**İkincil soru (skor):** `N1 − N2` farkı ve gün-kümeli t'si **raporlanır**;
geçme ölçütü **yoktur** (tek pencere, düşük güç).

**GEÇTİ** = K1+K2+K3+K4 · aksi **DÜŞTÜ**.

🔴 **K3 bu ön-kaydın kalbi.** Bugün ölçülen **her** olumlu sonuç yoğunlaşma
testinde çöktü (`pump_long_tezi` %133 · 11-19 penceresi %665). Bu ölçüt
olmadan bu bot da aynı yanılgıyı üretir.

## 7 · BAŞARISIZLIK ÖLÇÜTÜ — ne olursa KAPATILIR

Pencere dolmadan da kapatılır:

```
- dusus freni tetiklenirse (-%25)            -> DURUR, aciklama yazilir
- 30 gun dolar ve K1 duserse                 -> KAPATILIR
- N 30 gunde 80'e ulasmazsa                  -> "olculemedi", uzatilmaz
```

⚠️ *"Biraz daha bekleyelim"* bu ön-kayıtla **yasaktır**.

## 8 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%25, K1+K3'ün birlikte geçmesine ~%15 veriyorum.**

Gerekçe dürüst olmalı: bugün **on iki ölçüm** yapıldı ve **hiçbiri** kanıtlanmış
bir giriş kenarı bulamadı. Bu bot, ölçülmüş bir kenara değil, **ölçülmüş
kenarsızlıktan arta kalan en makul yapıya** dayanıyor.

**Yönlü tahminler (tutmazsa aynen raporlanır):**

1. `N1` ve `N2` arasındaki fark **görülür olmayacak** (skor kapısı nötr).
2. `N2` **daha az işlem** açacak (kapı eliyor) — akış farkı raporlanır.
3. Kayıp/kazanç yine **birkaç güne yoğunlaşacak** → K3 belirleyici olacak.
4. Sabit %10 hedefle **kazanma oranı %50'nin altında** kalacak, kâr birkaç
   büyük kazanandan gelecek (mevcut defterde TP2 profili böyle).

## 9 · Dokunulmayanlar

`testbot.py` · `golge.py` · `ayna.py` · `benim.py` · `defter2/3` · `radar.py` ·
`evren.py` · mevcut state ve defter dosyaları · mevcut zamanlanmış görevler:
**hiçbiri.**

Yeni bot **ayrı dosya** (`notrlong.py`), **ayrı state**, **ayrı defter**,
**ayrı zamanlanmış görev**. `testbot`'un fonksiyonları **çağrılır**,
değiştirilmez (`_DEFTER` deseni, `finally` ile geri alınır).

## 10 · Panel

Kullanıcı *"paneli temizle"* dedi. Panel **yalnızca görüntüdür**, ölçüm
tabanı değil. Temizlik = kapanan defterlerin panelden çıkarılması ve yeni
iki kolun eklenmesi. **Ayrı ve geri alınabilir bir iş**; bu ön-kaydın
ölçütlerini etkilemez.

---

## 11 · 🔴 [DEĞİŞTİ 2026-09-06] SKOR KAPISI KALDIRILDI — İKİ KOL YERİNE TEK KOL

**Kullanıcı sorusu (2026-09-06):** *"n1 skor kapısı yok, skorun etkisi var mı?"*
**Kullanıcı kararı:** *"skor kapısını kaldır."*

### Neden — soru bir TASARIM KUSURU açığa çıkardı

Bölüm 4 *"N1: skor kapısı YOK"* diyordu. **Bu ifade yanlıştı.** Skor N1'de
zaten **üç yerde** iş görüyor:

```
(a) tara()     : radar.analyze sonucu  score >= 30 suzgeci
(b) tara()     : kisa liste SKORA GORE siralanip [:10] kirpiliyor
(c) karar_yon  : skor >= stage_esigi   (BASLIYOR 45 · HAZIRLANIYOR 40)
```

Ve daha ciddisi: `karar_yon` **zaten** BAŞLIYOR için `≥45` istiyor. N2'nin
`≥45` kapısı orada **hiçbir şey eklemiyordu**; yalnız HAZIRLANIYOR dalında
skoru `[40,45)` olanları kesiyordu.

**Arşivde ölçüldü** (`scratchpad/notrlong_skor_etkisi.py`, N=34.618 aday):

```
ilk uc kapiyi gecen (N1) : 1430
+ skor >= 45      (N2)   : 1308
FARK                     :  122   ->  %8,5
```

🔴 **İki kol adayların yalnız %8,5'inde ayrışıyordu.** `N1 − N2` farkı
gürültüden ayırt edilemezdi; ikincil soru **kurgu gereği cevapsız** kalacaktı.

### Ne değişti

```
ESKI: iki kol — N1 (skor kapisi yok) · N2 (skor >= 45)
YENI: TEK KOL — skor kapisi YOK. Dosyalar notrlong_state.json / _islemler.jsonl / ...
```

**Bölüm 4 (iki kol) ve bölüm 6'nın "İkincil soru (skor)" satırı GEÇERSİZ.**
Bölüm 5, 6 (K1–K4), 7 ve 8 **aynen geçerli**.

### Gerekçe — neden ayırmak yerine KALDIRMAK

1. **Skorun boş olduğu iki kez ölçüldü** (sentetik + gerçek defter:
   `r = −0,024`; `Q4−Q1` MDE'nin üçte biri). Üçüncü kez sormak için deneyin
   yarısını harcamak kötü tahsis.
2. **Akış kıl payı** — taban 2,75 poz/gün, hedef 2,67. Tek kol, asıl sorunun
   (`K1`: bu bot para kazanıyor mu) `N=80`'e ulaşma şansını **iki katına** çıkarır.
3. **Skor sorusu kaybolmuyor:** işlem defteri her girişin `skor_giriste`
   alanını zaten yazıyor. Kapı kurmadan, **sonradan** aynı defterde ölçülür
   (`skor_gercek.py` deseni). Bu, kapıyı test etmez ama korelasyonu test eder —
   ve bugüne kadarki iki ölçüm de zaten korelasyon ölçümüydü.

### Pencere

🔴 **Pencere SIFIRDAN başlar** (D/8). Maliyeti yok: değişiklik anında pencere
**1,5 saatlikti ve 0 pozisyon** açılmıştı. Eski `n1`/`n2` kasaları
`arsiv/notrlong_ilk_kurulum/` altına taşındı.

⚠️ **Bu değişiklik sonucu görülmeden yapıldı** — hiçbir pozisyon açılmamıştı,
dolayısıyla seçilim yok.
