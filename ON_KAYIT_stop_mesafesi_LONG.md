# ÖN-KAYIT — STOP MESAFESİ, **LONG** POPÜLASYONUNDA

**Yazılma tarihi:** 2026-09-06 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"900 dolar 5x yerine 3x kaldıraç açsa 150 dolar stop
mesafesi uzar"* → *"koş"*
**Betik:** `scratchpad/stop_mesafesi_long/01_olcum.py`

---

## 1 · NEDEN — iki şeyi birden çözmek için

**(a)** Kullanıcının gözlemi doğru: sabit dolar riskiyle, daha düşük kaldıraç
(= daha küçük notional) **daha geniş stop** demektir. Bu bir tasarım
seçeneğidir ve LONG tarafında hiç sınanmadı.

**(b) 🔴 Bu akşam yaptığım bir çıkarım karıştırıcı olabilir.** `R(m)` ölçümünün
mekanizma tablosundan *"dar stop iyi, geniş stop kötü"* dedim:

```
stop 2,00-2,53 -> A0 ort R +0,4171   ·   stop 5,61-17,02 -> -0,1047
```

**O tablo GÖZLEMSEL:** `stop_pct` orada **coinin oynaklığının vekili**.
*"Dar stop"* = *"sakin coin"*. Bu ölçüm **aynı coinde** stopu değiştirir
(`CLAUDE.md`: *"eşleşmiş giriş, farklı genişlik"*, `stop_mesafesi.py` deseni)
ve o çıkarımın karıştırıcıdan gelip gelmediğini gösterir.

## 2 · ZATEN ÖLÇÜLDÜ — ama BAŞKA POPÜLASYONDA

`ON_KAYIT_stop_mesafesi.md` (2026-09-05, `olcumler.md:8199`),
**N=4.343 · 653 gün · 419 sembol**, `A_funding` girişleri:

```
kol      stop%     net%          R    stop-ol%   hedef%    saat
A         4,55   +0,074    -0,0092       63,4     28,7     19,8
1.5x      5,53   +0,016    +0,0011       58,4     32,1     22,6
2.5x      9,22   +0,219    +0,0235       42,2     39,9     32,0
4.0x     14,74   +0,304    +0,0242       26,8     44,0     40,2

2.5x  R +0,0518  t=+1,98 (MDE 0,052)  ·  net% +0,329  t=+2,43  GORULUR
4.0x  R +0,0577  t=+1,86              ·  net% +0,453  t=+2,55  GORULUR
permutasyon max|t| = 1,98 -> p = 0,090
```

**Hüküm: DÜŞTÜ** (birincil `R`, `t < 2,0`). Kayıt: *"Bu 'etki yok' değil,
**göremiyoruz**."*

🔴 **Ama `A_funding` bir SHORT kapısıdır (A+B).** Bizim bot **LONG**.
Bu ölçüm o boşluğu kapatır.

## 3 · KOLLAR — dünkü ölçümden AYNEN alındı, yeni eşik İCAT YOK

```
A      : olcucu uclu mantik (destek / 10-bar dibi / 1,5xATR'nin EN YAKINI)
1.5x   : stop = giris - 1,5 x ATR14
2.5x   : stop = giris - 2,5 x ATR14
4.0x   : stop = giris - 4,0 x ATR14
```

**Hiçbiri stopsuz değil** (`CLAUDE.md` deseni (b)). Hedef ve zaman stopu
**değişmez**: sabit `%10` fiyat · `48s` · maliyet `%0,09`.

🔑 **Dolar riski her kolda SABİT ($150).** Geniş stop → `notional = risk/stop_frac`
otomatik **küçülür** → tam da kullanıcının tarif ettiği "düşük kaldıraç" hâli.

## 4 · ZORUNLU SINAMA — merdiven monoton olmalı

`A ≤ 1.5x ≤ 2.5x ≤ 4.0x` (medyan stop genişliği). Değilse betik **çalışmayı
reddeder** — dünkü betiğin `sinama()` deseni.

## 5 · VERİ

```
POPULASYON : radar_archive · score>=30 · 4sa cooldown · LONG · A0 mekanigi
N          : 2.082 giris · 72 gun
KESIF      : ilk %60 gun (1.006)   HOLDOUT : son %40 gun (1.076)
ESLESME    : A kolunun asgari_stop kapisini gecen girisler TUM kollarda
```

## 6 · ÖLÇÜTLER — sonuç görüldükten sonra değişmez

🔴 **Birincil kol `2.5x`** — dün eşiğe en yakın olan. Bu seçim **dünkü, farklı
popülasyondaki** sonuçtan geliyor, yani bu veri için **örneklem dışı** bir
önseldir. Koşumdan önce ilan ediliyor.

| # | ölçüt | eşik |
|---|---|---|
| **U1** | HOLDOUT'ta eşleşmiş fark (`2.5x − A`), **R** | **> 0** |
| **U2** | HOLDOUT'ta **gün-kümeli t** | **≥ +2,0** |
| **U3** | farkın büyüklüğü **MDE'nin üstünde** | evet |
| **U4** | KEŞİF ve HOLDOUT'ta **aynı işaret** | evet |
| **U5** | **permütasyon** (gün bazında işaret çevirme, 2.000 tur), üç kolun `max\|t\|` | **p < 0,05** |

```
GECTI       = U1..U5 hepsi
DUSTU       = U1 veya U4 duser
GOREMIYORUZ = U1+U4 gecer ama U3/U5 duser
```

`U5` üç kolun çoklu karşılaştırmasını kapatır — dünkü ölçümün deseni.

## 7 · EK RAPOR — ölçüt DEĞİL

- `1.5x` ve `4.0x` kolları (aynı istatistikler)
- `net%` (ikincil metrik — dün **bu metrikte geçmişti**)
- Her kolda: stop olma% · hedef isabet% · **ampirik başabaş** · medyan tutma ·
  zaman stopu oranı
- 🔴 **Karıştırıcı testi:** stop dilimlerine göre `2.5x − A` farkı. Gözlemsel
  tablo *"dar stop iyi"* diyordu; eşleşmiş fark **her dilimde** aynı yöndeyse
  o çıkarım **karıştırıcıdan** gelmiş demektir

## 8 · NE YAPILMAZ

- Bota, state'e, defterlere **dokunulmaz** (salt-okuma)
- Çarpanlar **aranmaz** — dünkü ölçümden aynen alındı
- Hedef ve zaman stopu **değişmez**
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 9 · GEÇERSE

1. **Ham mekanik** ölçümdür → sonra **portföy simülasyonu**
   ⚠️ Geniş stop **tutma süresini uzatır** (dün `19,8 → 32,0` saat) → slot
   devri yavaşlar, pencere hızı düşer
2. Ancak o da geçerse `notrlong`'a uygulama + pencere sıfırlama

## 10 · BEKLENTİM — koşumdan önce, olasılıkla

**%35.** Bugünün en yükseklerinden, çünkü: (a) doğru tasarım (eşleşmiş giriş);
(b) dün **iki kat büyük** bir örneklemde kıl payı kaldı ve `net%`'te geçti;
(c) kullanıcının aritmetiği tutarlı.

Aleyhte: (a) dünkü ölçüm **SHORT** popülasyonundaydı, LONG'da işaret
dönebilir; (b) hedef sabit `%10` kalırken stop genişleyince `R:R` **düşer**
(`2.5x`'te medyan stop ~2 kat → `R:R` yarıya) — bugün `R(m)` ölçümü küçük
`R:R`'nin zararlı olduğunu gösterdi; (c) bugün **on bir ön-kayıt, on biri
düştü.**
