# ÖN-KAYIT — `ATR/FİYAT`, SEÇİM YANLILIĞI GİDERİLMİŞ (DÜZELTME KOŞUMU)

**Yazılma tarihi:** 2026-09-07 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"sanki ölçümünde hata varmış gibi geliyor bana"*
→ teşhis kusuru **doğruladı** → *"yap"*
**Betik:** `scratchpad/atr_fiyat/04_temiz.py`

---

## 1 · 🔴 BU YENİ BİR BAKIŞ DEĞİL, BOZUK ÖLÇÜMÜN ONARIMI

`ON_KAYIT_atr_2yil.md` (`4474a75`) *"üçüncü bakış olmayacak"* demişti.
Bu koşum onu **ihlal etmiyor**, çünkü önceki ölçüm **kusurlu bulundu** —
daha iyi sonuç aramak için değil, **hatayı düzeltmek** için koşuluyor.

**Teşhis** (`scratchpad/atr_fiyat/03_teshis.py`, aynı gün):

```
asgari_stop (%2) kapisi ATR'ye gore ASIRI SECICI:
  ATR 0,00-1,04  ->  58.092 aday,      0 gecti  (%100 elendi)
  ATR 1,04-1,34  ->  58.092 aday,    306 gecti  (%99,5 elendi)
  ATR 2,26-422   ->  58.093 aday, 39.368 gecti  (%32 elendi)

stop/ATR orani dilimler arasi: 1,48 -> 1,12  (SABIT DEGIL)
```

🔴 **Sonuç: gerçek düşük-ATR evreni ölçümde HİÇ YOKTU.** *"En düşük ATR
dilimi"* dediğim şey, `%2` tabanını geçebilen **hayatta kalanlardı**.
Ve `R`'nin paydası orada `ATR` ile değil **tabanla** belirleniyordu —
`B5`'in yakaladığı artefaktın sebebi buydu.

⚠️ **Aynı kusur `8273a10`'daki (2026-09-06, skorlu evren) ölçümde de
VAR** — orada da `asgari_stop` kapısı vardı. Yani o ölçümün *"düşük ATR
iyi"* bulgusu da **aynı seçim yanlılığını** taşıyor. Bu kayda geçiyor.

## 2 · DÜZELTME — geometri SABİTLENİYOR

```
ESKI : stop = olcucu uclu mantik + asgari_stop %2 kapisi
       hedef = SABIT %10 fiyat
       -> stop/ATR degisken (1,48..1,12) VE R:R degisken (4,4..1,1)

YENI : stop  = 1,5 x ATR      (kapi YOK)
       hedef = 4,5 x ATR      (R:R = 3,0 HER HUCREDE AYNI)
       zaman stopu 48s · maliyet %0,09  (degismedi)
```

🔑 **İki kusur birden kapanıyor:** (a) seçim yanlılığı yok, gerçek
düşük-ATR evreni içeride; (b) `stop/ATR` **ve** `R:R` her hücrede
**birebir aynı** → payda artefaktı **yapısal olarak imkânsız**.

🔴 **ZORUNLU SINAMA:** `stop/ATR` ve `R:R`'nin dilimler arası değişimi
`%1`'i aşarsa betik **çalışmayı reddeder**.

## 3 · 🔴 METRİK — ve `B5`'i NEDEN KULLANMIYORUM

Önceki ön-kayıtta *"ham net% aynı işarette olmalı"* (`B5`) koşulu vardı.
**Burada geçerli değil ve sebebini koşumdan önce yazıyorum:**

Geometri sabitken düşük-ATR coinler **tanım gereği** daha az yüzde
hareket eder. Ham `net%`'in küçük olması **artefakt değil, olgudur**.
İki metrik **meşru olarak** ayrışabilir:

```
BIRINCIL : ort R = net% / (1,5 x ATR%)   -> sabit dolar riskiyle KAZANILAN
IKINCIL  : ham net%                      -> BETIMLEYICI, olcut DEGIL
```

`B5`'i ölçüt olarak taşımak, **kendi kurduğum tuzağa** düşmek olurdu:
orada payda **taban** yüzünden bozuluyordu, burada payda **tasarım gereği**
tekdüze. Fark bu.

## 4 · VERİ

```
klines_1h_uzun · 567 sembol · medyan 584 gun · en erken 2024-08-11
mekanik ornek: gunde 1, FAZ KAYDIRMALI (hash(sembol) mod 24)
BOLME: ATR/fiyat besli dilim, EN DUSUK vs EN YUKSEK (onceden ilan)
KESIF ilk %60 gun · HOLDOUT son %40 gun
```

⚠️ **Aşırı değer budama — koşumdan önce ilan:** `ATR/fiyat > %20` olan
kayıtlar **dışlanır** (teşhiste ölçüldü: 80 kayıt, **on binde bir**;
`BABY %422`, `BULLA %194` gibi bozuk mumlar). Bu bir eşik **araması
değil**, veri temizliği; oran ve etkilenen sayı raporlanır.

## 5 · ÖLÇÜTLER — sonuç görüldükten sonra değişmez

| # | ölçüt | eşik |
|---|---|---|
| **C0** | 🔴 **YAPISAL**: `stop/ATR` ve `R:R` dilimler arası sapma < %1 | yoksa **betik durur** |
| **C1** | HOLDOUT: en düşük − en yüksek ATR dilimi, **ort R** | **> 0** |
| **C2** | HOLDOUT: gün-kümeli **t ≥ +2,5** | evet |
| **C3** | \|fark\| > **MDE** | evet |
| **C4** | KEŞİF ve HOLDOUT **aynı işaret** | evet |
| **C5** | **negatif kontrol** temiz | evet |
| **C6** | **sembol-kümeli t ≥ 2,5** | evet |

```
YON VAR      = C1..C6 hepsi
TERS YON     = C1 duser AMA |t| >= 2,5 ve C4 gecer   <- ayri ve ONEMLI sonuc
YON YOK      = C1 ve C4 duser
GOREMIYORUZ  = C1+C4 gecer, C2/C3 duser
```

🔴 **`TERS YON` ayrı bir hüküm olarak yazıldı:** mekanik evrende işaret
zaten ters çıkmıştı; temiz ölçümde de ters çıkarsa bu **bulgudur**,
"düştü" değil.

## 6 · NE YAPILMAZ

- Bota/state/deftere **dokunulmaz** · ücretli çağrı **YOK**
- Çarpanlar (`1,5` / `4,5`) **ARANMAZ** — `1,5xATR` projenin kendi
  stop tanımından, `4,5` onun `3,0` R:R karşılığı
- **Spearman KOŞULMAZ**
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 7 · GEÇERSE / GEÇMEZSE

**Geçerse:** taşınabilirlik (botun evreninde, `asgari_stop` **ile**) ayrı
adım. Kod otomatik değişmez.
**Geçmezse:** `ATR/fiyat` mekanik evrende kapanır. Skorlu evrendeki soru
`radar_archive` ~110 güne ulaşınca ayrıca sorulur.

🔴 **Her iki durumda da bu, mekanik evrendeki SON `ATR/fiyat` ölçümüdür.**

## 8 · BEKLENTİM — koşumdan önce

**`C1..C6`'nın geçmesine %30.** Seçim yanlılığı gerçek düşük-ATR evrenini
tamamen dışarıda bırakıyordu; içeri girince ne olacağını **bilmiyorum** —
bu ölçümün değeri de burada.

**`TERS YON` çıkmasına %25.** Mekanik evrende işaret zaten negatifti.

⚠️ Bugün **yirmi bir ön-kayıt yazıldı, yirmi biri de kural üretmedi.**
