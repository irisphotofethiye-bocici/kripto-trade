# ÖN-KAYIT — REJİM KAPISI: ALFA REJİME BAĞLI MI?

**Yazılma tarihi:** 2026-09-06 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-06): *"senin dediğin olsun"* → A şıkkı, rejim kapısı
**Betik:** `scratchpad/rejim_kapisi/01_olcum.py`

---

## 1 · 🔴 ÖNCE BAR HESAPLANDI — VE ÖNERİMİ KENDİ KENDİNE DARALTTI

Bugün ölçülen iki sayı (`scratchpad/giris_arama/02_beta.py`, N=69 gün):

```
gunluk R  =  ALFA + BETA x BTC%   =  -0,1078  +0,1220 x BTC%
                                     (t=-2,01)
```

Buradan **kapının geçmesi gereken bar türetilir**:

```
R > 0  icin  BTC% > 0,1078 / 0,1220 = %0,88 / GUN
```

Ve BTC'nin 2 yıllık gerçek dağılımı (744 gün):

```
ortalama +0,070%/gun · medyan +0,024%/gun · %0,88'i asan gun orani %31,5
-> kapinin BTC gunluk ORTALAMASINI 12,6 KAT'a cikarmasi gerekiyor
```

🔴 **Hiçbir nedensel filtre bunu yapamaz.** Yani *"alfa sabit kalırsa rejim
kapısı bu botu kurtaramaz"* — bu, koşumdan önce bilinen bir sonuçtur ve
buraya yazılıyor.

## 2 · O HÂLDE ÖLÇÜLEN SORU DARALDI

Kapının işe yaramasının **tek yolu** şudur:

> **ALFA'nın kendisi rejime bağlı olmalı.**

Yani bazı rejimlerde bot yalnız daha az beta almıyor, **daha az kötü seçim
yapıyor** olmalı. Ölçülen hipotez budur:

```
H0 : alfa her rejimde ayni (~ -0,11)   -> kapi ISE YARAMAZ
H1 : alfa rejime gore degisiyor        -> kapinin acik oldugu rejimde alfa >= 0
```

## 3 · KAPILAR — hepsi NEDENSEL, koşumdan önce listelenmiş

🔴 **Look-ahead yasak:** her kapı, o günün **başlamasından ÖNCE** bilinen
veriden hesaplanır. *"O gün BTC %2 çıktı mı"* bir kapı **DEĞİLDİR** —
ölçülemez, ticareti yapılamaz.

| # | kapı | tanım (t günü için, `t−1` kapanışıyla) |
|---|---|---|
| K1 | `btc_sma20` | BTC kapanış > 20 günlük SMA |
| K2 | `btc_sma50` | BTC kapanış > 50 günlük SMA |
| K3 | `btc_mom7` | BTC son 7 gün getirisi > 0 |
| K4 | `btc_sakin` | BTC 20 günlük gerçekleşen oynaklık, kendi medyanının **altında** |
| K5 | `btcd_dusuyor` | `btc_d` 3 günlük değişim < 0 (alt lehine rotasyon) |
| K6 | `usdtd_dusuyor` | `usdt_d` 3 günlük değişim < 0 (stabil para konuşlanıyor) |
| K7 | `bot_rejimi` | `evren.btc_rejim()` etiketi ∈ {`TAM_BOGA`, `TEPKI_RALLISI`} |

**7 kapı = 7 karşılaştırma.** Bu yüzden eşik `t ≥ 2,5` (kabaca Bonferroni'li 2,0).

⚠️ K7 botun **kendi** dedektörüdür ve `radar_archive.rejim` alanı
2026-07-22'de tanım değiştirdi (`CLAUDE.md`) → alan **okunmaz**, etiket BTC
mumundan **yeniden üretilir**.

## 4 · VERİ ve 🔴 GÜÇ SINIRI — koşumdan önce ilan

```
GUNLUK R : radar_archive -> A0 mekanigi (01_arama.py:veri_kur) -> gun ortalamasi
N        : 69 GUN   <- HARD SINIR, radar_archive 2026-06-24'te basliyor
BTC      : klines_1h_uzun (744 gun) -> kapi hesaplari
BTC.D    : piyasa_yapisi_log.jsonl (137 kayit, 2026-06-26'dan)
```

🔴 **N=69 GÜN ÇOK AZDIR.** İkiye bölününce ~35/34 kalır. **Bu ölçümde NULL
SONUÇ, YOKLUĞUN KANITI DEĞİLDİR.** MDE her kapıda **hesaplanıp raporlanacak**
ve etki tabanı ondan türetilecek — bugün üç ön-kayıt bu hatayı yaptı
(`taker` · `funding/L-S` · kısmen `sıkışma`), dördüncüsü yapmayacak.

## 5 · ÖLÇÜTLER — sonuç görüldükten sonra değişmez

Her kapı için:

| # | ölçüt | eşik |
|---|---|---|
| **R1** | kapı AÇIK günlerde ortalama günlük R | **> 0** |
| **R2** | açık-kapalı farkının **gün düzeyinde** t'si | **≥ +2,5** |
| **R3** | farkın büyüklüğü **MDE'nin üstünde** | evet |
| **R4** | 🔴 **ALFA testi**: açık günlerde `R = α + β·BTC%` regresyonunda **α ≥ 0** | evet |
| **R5** | açık günlerin sayısı ≥ 20 **ve** kapalı günlerin sayısı ≥ 20 | evet |

```
KAPI ISE YARAR = R1..R5 hepsi
BOS            = R1 veya R4 duser
GOREMIYORUZ    = R1+R4 gecer ama R3 duser (N=69, guc yetmedi)
```

🔴 **R4 belirleyicidir.** `R1` tek başına yalnız *"o günler BTC iyiydi"*
demek olabilir (beta). `R4`, betadan **arta kalanı** sorar — bölüm 2'deki
tek gerçek çıkış yolu odur.

## 6 · EK RAPOR — ölçüt değil, teşhis

- Her kapı için: açık/kapalı gün sayısı, ortalama BTC getirisi, β ve α ayrı ayrı
- **Bölüm 1'in barı**: kapının açık olduğu günlerde ortalama BTC getirisi
  `%0,88`'i geçiyor mu (geçmeyecek — ama **ne kadar** eksik kaldığı bilgidir)
- Kapıların birbiriyle örtüşmesi (aynı günleri mi seçiyorlar)

## 7 · NE YAPILMAZ

- Bota, state'e, defterlere, görevlere **dokunulmaz** (salt-okuma)
- **Look-ahead yok**: her kapı `t−1` kapanışıyla hesaplanır
- Eşik/pencere **aranmaz** (20 · 50 · 7 · 3 gün: hepsi standart ve önceden yazıldı)
- En iyi kapı **seçilip** kural yapılmaz — hepsi aynı ölçütten geçer
- `radar_archive.rejim` alanı **okunmaz** (2026-07-22 tanım değişikliği)
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 8 · GEÇERSE NE OLUR

🔴 Doğrudan bota **konmaz**:
1. Bu ölçüm **ham mekanik** günlük R üzerinde (portföy yok, slot yok, fonlama yok)
2. Geçerse **portföy simülasyonu** ayrı koşar
3. Ancak o da geçerse kapı önerisi + `notrlong`'a uygulama + pencere sıfırlama

**Geçmezse:** *"rejim kapısı"* yolu kapanır ve bölüm 1'in aritmetiği bağlayıcı
hâle gelir — o noktada dürüst seçenekler **yönü çevirmek** (B) ya da
**yönü tamamen bırakmak** (C: funding/basis) olur, ve bu **kullanıcının
kararıdır**.

## 9 · BEKLENTİM — koşumdan önce, olasılıkla

**Bir kapının R1..R5'i geçmesine %15.**

Bölüm 1'in aritmetiği yüzünden düşük: kapı ancak **alfayı** değiştirirse
işe yarar, ve alfanın rejime bağlı olması için bir mekanizma göremiyorum —
bot her rejimde aynı kapılarla aynı tür coini seçiyor.

⚠️ En olası şey: birkaç kapı `R1`'i geçer (çünkü beta iyi günleri yakalar),
ama `R4` (alfa ≥ 0) **düşer**. O sonuç bile değerlidir: *"kâr betadan
geliyor, seçimden değil"* hükmünü **doğrudan** kanıtlar.
