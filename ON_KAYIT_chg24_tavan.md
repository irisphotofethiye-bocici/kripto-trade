# ÖN-KAYIT — `chg24` TAVANI: "belli bir yükseliş yapana girmesin"

**Yazılma tarihi:** 2026-09-07 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"bunu nasıl sınırlarız, belli bir yükseliş yapana girmesin"*
**Betik:** `scratchpad/chg24_tavan/01_olcum.py`

---

## 1 · NEDEN — beş girişin beşi de aynı bölgede

`notrlong` pencere-2'de açılan beş pozisyon:

```
id  sym      chg24  range_pos   sonuc
1   ARX     +10.03      0.76    -152.84  STOP
2   UAI     +26.86      0.57    acik
3   METIS   +18.96      0.85    acik
4   TAO     +15.45      1.00    -150.94  STOP
5   TIA     +13.64      1.09    acik
```

Hepsi **+%10…+%27** ve `range_pos` 0,57–1,09. Stop olan ikisinin MFE'si
**+1,05 R** ve **+0,51 R** — hedefe hiç yaklaşmadılar
(`scratchpad/tp1_iki_poz.py`, 2026-09-07).

Mevcut kapı `blowoff_chg24_pct = 40` ([testbot.py:411](testbot.py#L411)) —
beşinin hiçbirini yakalamıyor.

## 2 · 🔴 VERİ TUZAĞI — arşivin `chg24`'ü BOTUN `chg24`'ü DEĞİL

Ölçümden **önce** bulundu ve tasarımı değiştirdi:

```
radar_archive.jsonl, iki kayit sekli:
  N=179.298  ana radar kaydi    -> chg24 alani YOK  (last1 · last3 · pos var)
  N= 47.848  erken-kusak kaydi  -> chg24 VAR, ama |chg24| <= 15 (TANIM GEREGI)

erken_kusak_tara(): chg_max = evren.esik("erken_chg24_max", 15.0)   radar.py:194
  -> arsivde chg24 min -15,00 · max +15,00 · >20 olan SIFIR
```

Bot ise havuzunu **süzgeçsiz** kuruyor
(`binance_pool(..., cryptos=...)`, `chg_max` verilmiyor →
[testbot.py:1400](testbot.py#L1400) · [notrlong.py:265](notrlong.py#L265)).
`radar.py` arşivi **`--chg_max 15`** ile yazıyor ve kodda zaten
*"chg_max pump başlayınca eliyor — **kör nokta yapısal**"* diyor
([radar.py:186](radar.py#L186)).

🔑 **Bu yüzden `chg24` alanı KULLANILMAYACAK.** `chg24` her giriş için
**1s mumdan yeniden üretilecek**:

```
chg24 = (price / kapanis[i0-24] - 1) * 100
```

`CLAUDE.md`'nin kendi reçetesi: *"o tarihi aşan hiçbir rejim kırılımı bu
alanla yapılmaz — rejim BTC mumundan yeniden üretilir."* Aynı hata sınıfı.

## 3 · 🔴 BİRİNCİL METRİK **HAM GETİRİ** — bu bir seçim değil, KURAL

`CLAUDE.md` (2026-08-20 ihlali):

> **hücreler oynaklıkta ayrışıyorsa ham getiri ZORUNLU**

Ve `chg24` bantlarında ayrışma **ölçülmüş**:

| bant | stop genişliği | ATR/fiyat | stop olma |
|---|---|---|---|
| `-40..0` | %2,86 | %2,50 | %73,1 |
| `0..20` | %2,86 | %2,13 | %76,5 |
| `20..40` | %5,88 | %4,27 | %61,8 |
| `>40` | %9,31 | %6,50 | %50,1 |

Stop genişliği **3,3 kat** değişiyor. Bu yüzden:

```
BIRINCIL : ham +24 saat getiri  (mekaniksiz)
IKINCIL  : A0 mekanigiyle R     (rapor edilir, hukum kurmaz)
```

⚠️ Ve aynı kayıt uyarıyor: *"stop varyansı kırdığı için anlamlılık büyüyor —
**yön aynı, güven yalan.**"* Mekanikli `t` bu yüzden ölçüt olamaz.

## 4 · SORU ve HİPOTEZ — tek yönlü, koşumdan önce

```
H1 : dusuk chg24 (az kosmus coin) daha yuksek ham ileri getiri uretir
H0 : yon yok
```

## 5 · TASARIM — eşik ARANMAZ

🔴 **Hiçbir tavan seçilmez.** Karşılaştırma **önceden ilan edilmiş**:

```
BIRINCIL : EN DUSUK chg24 besli dilimi  -  EN YUKSEK chg24 besli dilimi
           (holdout'ta, gun-kumeli, HAM getiri)
```

Tek karşılaştırma → çoklu karşılaştırma düzeltmesi gerekmiyor, `t ≥ 2,0`.

⚠️ **Tavan merdiveni (`>%5 · >%10 · >%15 · >%20` elenirse) EK RAPORDUR,
ölçüt DEĞİL.** `genis_stop` ölçümünde eşik yordamım kusurlu çıkmıştı
(negatif tabanla her alt küme negatif görünür); tekrarlanmayacak.

## 6 · VERİ

```
POPULASYON : radar_archive ANA kayitlari · score>=30 · 4sa cooldown · LONG
DEGISKEN   : chg24 = (price / kapanis[i0-24] - 1) * 100   <- MUMDAN
N          : ~2.082 giris · 72 gun (giris_arama ile AYNI evren)
KESIF      : ilk %60 gun   HOLDOUT : son %40 gun
```

⚠️ **Bu evren `notrlong`'unkiyle AYNI DEĞİL** (notrlong: rejim NOTR zorla +
smart-LONG + temiz-aday). Daha geniş bir popülasyonda ölçülüyor; hüküm
notrlong'a **doğrudan taşınamaz**, bu ön-kayıtta yazılıdır.

## 7 · ÖLÇÜTLER — sonuç görüldükten sonra değişmez

| # | ölçüt | eşik |
|---|---|---|
| **C1** | HOLDOUT: en düşük dilim − en yüksek dilim, **ham getiri** | **> 0** |
| **C2** | HOLDOUT: **gün-kümeli t** | **≥ +2,0** |
| **C3** | farkın büyüklüğü **MDE'nin üstünde** | evet |
| **C4** | KEŞİF ve HOLDOUT'ta **aynı işaret** | evet |
| **C5** | **negatif kontrol** aynı boru hattında etki üretmemiş | evet |

```
YON VAR     = C1..C5 hepsi
YON YOK     = C1 veya C4 duser
GOREMIYORUZ = C1+C4 gecer ama C3 duser
```

## 8 · NEGATİF KONTROL

`chg24` **gün içinde permüte** edilir ve **birebir aynı** boru hattından
geçirilir (dilim + holdout farkı + gün-kümeli t).

🔴 `giris_arama`'da negatif kontrolü eksik kurmuştum (2 hücre vs 39);
burada **tam eşleştirilmiş** hat koşuyor.

## 9 · EK RAPOR — ölçüt DEĞİL

- Beşli dilim tablosu: N · ort `chg24` · **ham getiri** · `R` · isabet% ·
  **stop genişliği** · **stop olma %** (bölüm 3'ün ayrışma sınaması)
- 🔴 **`chg24` ile `pos` ne kadar aynı şey?** `pos` bir giriş kapısı olarak
  `giris_arama`'da **zaten arandı ve bulunamadı** (39 hücre, holdout `t +0,18`).
  İkisi neredeyse aynıysa bu ölçüm o aramanın **yeniden etiketlenmiş hâlidir**
  ve hüküm öyle yazılır. Spearman **kullanılmaz** — dilim çakışma oranı.
- Tavan merdiveni (yalnız bilgi)

## 10 · NE YAPILMAZ

- Bota, state'e, defterlere **dokunulmaz** (salt-okuma)
- Arşivin `chg24` **alanı okunmaz** (bölüm 2)
- Eşik **aranmaz** — dilimler veriden, karşılaştırma önceden ilan
- `R` ile `stop_pct` arasında **Spearman koşulmaz** (ortak payda)
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 11 · GEÇERSE

1. Ham aşama biter → **mekanik** → sonra **portföy simülasyonu**
2. ⚠️ Tavan **işlem sayısını azaltır**. `notrlong` penceresi
   `30 gün` **ve** `80 kapanmış pozisyon` istiyor ve şu an 5 pozisyonda.
   Kapı pencereyi *"ölçülemedi"*ye düşürebilir — bu **ayrı bir karardır**.
3. 🔴 Ve sıkılaştırma duvarı: çıkış tarafında **32 varyantta 1** geçti,
   geçen tek varyant **gevşetiyordu**.

## 12 · BEKLENTİM — koşumdan önce, olasılıkla

**%20.** Aleyhte üç şey: (a) `pos` — aynı ailenin **en güçlü** üyesi
(5 rejimde 5/5) — giriş kapısı olarak dün arandı ve **bulunamadı**;
(b) o aramanın asıl bulgusu *"kârlılığı belirleyen hangi coini seçtiğin
değil, hangi dönemde olduğun"* (taban iki yarı arasında **+0,24 R** kaydı);
(c) bugüne kadar on üç ön-kayıt yazıldı, on üçü de geçemedi.

Lehte: `chg24` (24 saat) o aramada **hiç yoktu** — taranan akrabalar
`last1` (1 saat) ve `last3` (3 saat), farklı ufuklar. Ve beş rejimli
kesit ölçümünde `chg24` **5/5** aynı işaret vermişti.
