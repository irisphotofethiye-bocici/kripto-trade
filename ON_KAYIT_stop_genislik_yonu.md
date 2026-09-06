# ÖN-KAYIT — STOP GENİŞLİĞİ ile GETİRİ ARASINDA YÖN VAR MI?

**Yazılma tarihi:** 2026-09-06 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"girilen miktarın %10 veya 20'sini alıp kapatsa… stopu da
yukarı çeksek"* → fikir çürütüldü, ama **doğru yeri gösterdi** → *"evet yap"*
**Betik:** `scratchpad/stop_genislik/01_olcum.py`

---

## 1 · 🔴 ÖNCE İKİ HATAM KAYDA GEÇİYOR

**(a)** Kullanıcıya *"stop genişliğine TAVAN koyalım, `R:R ≥ 3` olsun"* önerdim.
Sonra `testbot.py:1205`'teki ölçülmüş isabet tablosunu `%10` hedefe yansıttım:

```
stop banti      ort stop%    R:R   basabas%   GOZLENEN    EV (R)
<%1,92               1,46   6,85      12,7%      10,3%     -0,19
%1,92-3,40           2,66   3,76      21,0%      20,1%     -0,04
%3,40-5,51           4,46   2,24      30,8%      33,3%     +0,08
>%5,51               7,25   1,38      42,0%      56,2%     +0,34
```

**Tavan tam da en iyi görünen bandı keserdi.** Öneri yanlıştı.

**(b)** UAI pozisyonu için *"başabaş %50,7, ölçülen isabet %25 → yapısal
kaybeden"* dedim. **Koşullandırma hatası:** `%25` *tüm* adayların isabeti;
**geniş stoplu** olanların ölçülen isabeti `%56,2`. Doğru kıyas ikincisiydi.

🔑 **Ders:** stop daralınca `R:R` büyür (iyi) **ama isabet düşer** (kötü).
İki etki ters yönde çalışır ve **aritmetik hangisinin bastığını söyleyemez.**

## 2 · SORU

`notrlong`'un giriş havuzunda, **stop genişliği ile işlem başına net `R`
arasında yön var mı?** Varsa hangi yönde?

⚠️ Bu bir **giriş filtresi** sorusudur (adayı al/alma), **çıkış değişikliği
değil** → *"çıkışta 30 varyantta 1 geçti"* kuralı buraya **uygulanmaz**.

## 3 · HİPOTEZ — koşumdan önce, TEK YÖNLÜ ilan

Bölüm 1'deki yansıtmadan türeyen **yönlü** hipotez:

```
H1 : stop genisledikce ort R ARTAR   ->  rho(stop_pct, R) > 0
H0 : yon yok
```

🔴 **Tek karşılaştırma.** "En iyi bandı seç" **YAPILMAZ**; yön testi yapılır.
Ters yön (tavan) **ikincil** olarak raporlanır ki yalnız işime gelen yön
sınanmış olmasın.

## 4 · VERİ

```
POPULASYON : radar_archive · score>=30 · sembol basina 4sa cooldown
MEKANIK    : A0 aynen (olcucu uclu stop ATR14 · sabit %10 hedef · 48s ·
             fitil tetikli · maliyet %0,09 · asgari_stop %2 gecmeyen ELENIR)
N          : 2.082 giris · 72 gun          <- daha once olculdu
BOLME      : KESIF ilk %60 gun (N=1.006) · HOLDOUT son %40 gun (N=1.076)
```

⚠️ `asgari_stop %2` **zaten uygulanmış** → `<%1,92` bandı popülasyonda **YOK**.
Yani bölüm 1'deki en kötü bandı bu ölçüm göremez; sonuç **kalan üç bant**
hakkındadır.

## 5 · ÖLÇÜTLER — sonuç görüldükten sonra değişmez

| # | ölçüt | eşik |
|---|---|---|
| **P1** | HOLDOUT'ta `rho(stop_pct, R)` | **> 0** |
| **P2** | HOLDOUT'ta gün-kümeli `t` (üst yarı vs alt yarı, medyan bölme) | **≥ +2,0** |
| **P3** | farkın büyüklüğü **MDE'nin üstünde** (holdout'tan hesaplanır) | evet |
| **P4** | KEŞİF ve HOLDOUT'ta **aynı işaret** | evet |
| **P5** | HOLDOUT'ta en geniş dilimin ortalama `R`'si | **> 0** |

```
YON VAR   = P1..P5 hepsi
YON YOK   = P1 veya P2 duser
GOREMIYORUZ = P1+P2 gecer ama P3 duser
```

🔴 **Eşik `t ≥ 2,0`** (2,5 değil): **tek** birincil karşılaştırma var, çoklu
karşılaştırma düzeltmesine gerek yok. Bu, koşumdan önce yazıldı.

## 6 · EK RAPOR — ölçüt DEĞİL

- Beşli dilim tablosu: N · ort stop% · ort `R` · isabet% · **başabaş%** ·
  medyan tutma
- 🔴 **Başabaş AMPİRİK hesaplanır** — `1/(1+R:R)` formülü yalnız ikili sonuçta
  geçerli; zaman stopu üçüncü bir kapı açıyor (`sıkışma` ölçümünde bu hata
  yapıldı, `olcumler.md`)
- Zaman stopunda kapanan işlem oranı (formülün ne kadar bozulduğunun ölçüsü)
- İkincil: **tavan** kuralı (`stop_pct ≤ X`) ve **taban** kuralı ayrı ayrı

## 7 · NE YAPILMAZ

- Bota, state'e, defterlere, görevlere **dokunulmaz** (salt-okuma)
- Eşik/bant **aranmaz** — dilimler veriden, kural yönden gelir
- HOLDOUT **bir kez** okunur; ikinci bir hipotez sokulmaz
- Geçse bile **doğrudan bota konmaz** → bölüm 8
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 8 · GEÇERSE NE OLUR

🔴 Doğrudan bota konmaz:
1. Bu ölçüm **ham mekanik** (portföy yok, slot yok, fonlama yok)
2. Geçerse **portföy simülasyonu** ayrı koşar — ⚠️ geniş stop = **küçük
   pozisyon** demek (`notional = risk/stop_frac`), yani slot doluluğu ve
   sermaye kullanımı **değişir**; ham `R` bunu göstermez
3. Ancak o da geçerse kapı önerisi + pencere sıfırlama

## 9 · BEKLENTİM — koşumdan önce, olasılıkla

**`P1..P5`'in hepsinin geçmesine %30.**

Bölüm 1'deki yansıtma güçlü görünüyor (`EV −0,19 → +0,34`, monoton) ama:
(a) o tablo **başka bir ölçümden** (577 olay, farklı pencere) geliyor;
(b) bugün aynı arşivde **39 hücrelik arama holdout'ta çöktü** — bu popülasyonda
keşif→holdout büzülmesi ölçüldü ve büyüktü;
(c) stop genişliği **oynaklığın vekilidir** ve oynaklık bugün `vol_x` üzerinden
negatif kontrolü **geçemedi** (`funding/L-S` taraması) — yani bu değişken
"fiyat hareketinin başka bir ifadesi" olma riski taşıyor.

⚠️ Ve şu şimdiden yazılıyor: geçse bile bu **bir kapı önerisi değil**, bölüm
8'deki iki adımlı sıra bağlayıcıdır.
