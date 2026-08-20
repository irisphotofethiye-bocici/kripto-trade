# SHORT'lar neden kaybetti? — 11 Ağustos sonrası, her veri, her kombinasyon

**Tarih:** 2026-08-20 · **Betikler:** `scratchpad/short_kayip/` ·
**Bota dokunulmadı, kural önerilmiyor** (kullanıcı talimatı).

**Veri:** 11 Ağu 12:48'den bu yana kapanmış **103 SHORT** + **14 LONG**, 55 sembol.
Her pozisyon giriş anındaki **25 ölçüm alanıyla** eşleştirildi (%100 eşleşme,
medyan zaman farkı 1,2 dk). İki taban ayrı koşturuldu (muhasebe 11 Ağu / hakem
12 Ağu) — sonuçlar niteliksel olarak aynı çıktı.

**Mutabakat:** `equity farkı − kasa sıfırlaması = ΣP&L + funding − ücret`
→ artık −656,97 = funding −496,92 + ücret −160,05 (ücret oranı %0,057; config
taker %0,045 + slipaj %0,02 bandında). ⚠️ Pencere fonlaması kümülatife eşit
varsayıldı; kuruşu kuruşuna kanıt değil, **tutarlılık** kanıtı.

---

## 1 · Zarar nerede oluştu

```
                        N     toplam     medyan   kazanan
SHORT tumu            103    -488,94     -65,52     %43
  sicrama ONCESI       91    +183,41     -14,94     %46
  sicrama SONRASI      12    -672,35     -72,73     %17
LONG tumu              14    +249,43      +5,36     %64
```

**Kayıp tamamen SHORT'ta ve büyük kısmı son 2 günde.** Ama "öncesi kârlıydı"
demek yanıltıcı: **medyan −14,94**, yani tipik işlem kaybediyor. Toplamı artıda
tutan üç işlem var; onlar çıkınca **−671,65**.

Aynı kırılganlık tümünde: en iyi 3 kazanç çıkınca **−1.344**.

---

## 2 · "Hangi kombinasyonda zarar etmezdi?" — cevap ve tuzağı

27 alandan **77 koşul**, bunlardan **76.153 kural** üretildi (1'li, 2'li, 3'lü).
En az 15 işlem bırakan kurallar değerlendirildi.

### 🔴 Önce tuzak: "zarar etmeyen kombinasyon" bulmak hiçbir şey ifade etmiyor

```
                              GERCEK      KARISTIRILMIS veride
toplam >= 0 olan 1'li kural      27              ~26
toplam >= 0 olan 2'li kural     352             ~339
toplam >= 0 olan 3'lu kural   1.042             ~999
```

Sonuçlar **rastgele karıştırıldığında da** aynı sayıda "zarar etmeyen kural"
çıkıyor. Yani *"şu kombinasyonda zarar etmezdi"* cümlesi tek başına **bilgi
taşımıyor** — o kadar çok kombinasyon var ki bir kısmı her zaman iyi görünür.

### Ama bir tanesi şansla açıklanamıyor

```
GERCEK en iyi 1'li kural : +2262,24   ->  notional < 1437 $   (pozisyon buyuklugu)
SAHTE en iyi (1000 tur)  : ortalama +1135,81 · en yuksek +2452,98
p = 0,001
```

İki tabanda da **aynı kural birinci** (hakem tabanında +2420,40, p<0,001).

---

## 3 · O kural aslında ne söylüyor: **stop genişliği**

Bot risk-önce boyutlandırma kullanıyor → **küçük pozisyon = geniş stop**.

```
                stop% medyan   risk ($)   %10 hedefe ulasma
kucuk notional      4,51         74,5           %53
buyuk notional      2,77         76,0            %4
```

**Riske edilen dolar aynı** (74,5 vs 76,0) — boyutlandırma tasarım gibi çalışıyor.
Fark tamamen geometride: sabit %10 hedefle, %2,77'lik stop **3,6:1** oranında
elverişli bir yol gerektiriyor. Bu neredeyse hiç olmuyor.

### Karıştırıcı kontrolü — geçti

```
AYNI GUN icinde kucuk vs buyuk notional farki:
  08-12 +206,19 · 08-13 +139,87 · 08-14 +108,23 · 08-15 +99,84
  08-16  +34,68 · 08-17 +222,97 · 08-19  +48,37
  7 gun · 7/7 pozitif · ortalama +122,88 · gun-kumeli t = +4,50
```

### ⚠️ AMA BU YENİ BİR BULGU DEĞİL — 2 yıllık veri bunu zaten söylemişti

`olcumler.md` → *ASGARİ STOP EŞİĞİ* ölçümü (2026-08-19, 565 sembol / 2 yıl):

- Dar stoplu işlemler **gerçekten kötü**: A_funding −0,109% (t=−2,43),
  B_ma50ucuz −0,335% (t=−3,14)
- **Ama eşiği 2,0→3,0 yükseltmek KALDI** — akışın yarısını götürüyor ve
  iyileşme yarılarda/rejimlerde tutmuyor
- Kayıtlı ders: ***"atılan dilim kötü" ile "atmak iyi" aynı şey değil.***

Yani bu penceredeki bulgu, 2 yıllık ölçümün **bağımsız tekrarı**. Yeni bilgi:
canlı defterde de aynı yönde ve gün-içi kontrolü geçiyor.

---

## 4 · Gerçek holdout — kural sıçrama sonrasında ne yaptı?

Kural 91 işlemde arandı, 12 işlemde sınandı.

```
egitim +2334,15 (N=30)  ->  TEST +33,16 (N=1)   [test tumu -672,35]
```

Kural testte **12 işlemden 1'ini** alıyor. Zararı "önlüyor" ama **işlem yapmayarak**.
Bu bir filtredir ve N=1 hiçbir şey doğrulamaz.

---

## 5 · Kapıları kapatmadan: 30 mekanik kombinasyonu

Aynı 103 giriş, **hiçbiri elenmeden**, farklı stop/hedef ile yeniden oynatıldı
(5 dk mum, maliyet + fonlama dahil, **risk her hücrede sabit 75 $**).

```
stop\hedef      %3        %5        %7       %10       %15
%2           -1222     -2131     -2690     -2708     -3453
%3           -1112     -1706     -2105     -2401     -2973
%4            -980     -1241     -1859     -1671     -2168
%5            -935      -875     -1120     -1076     -1984
%6            -856     -1109     -1350     -1314     -2282
%8            -411      -336      -837     -1023     -1317
```

**30 hücrenin 30'u zararda.** En iyisi stop %8 / hedef %5 → −336.

**Botun gerçek sonucu −488,94 ve bu, 30 hücrenin 28'inden İYİ.** Botun kendi
mekaniği (yapısal stop + takip eden stop + TP1'de kısmi kâr) sabit stop/hedefe
göre **~1.900 $ değer katıyor** (3%/10% hücresi −2.401 iken gerçek −489).

### Filtre olmayan diğer değişiklikler (SHORT, tüm dönem)

```
1 saatte kosulsuz kapat      -68,18    <-- en iyisi, yine zararda
2 saatte                    -343,25
4 saatte                    -435,35
8 saatte                  -1.639,98
+15/30/60 dk gecikmeli giris  hepsi DAHA KOTU
YON CEVIRME (ters islem)    +182,11
```

---

## 6 · Dönem ayrımı — tek gerçek fark **yön**

```
                        sicrama ONCESI (N=91)   sicrama SONRASI (N=12)
en iyi izgara hucresi        +198,90 (8/5)          -487,88 (3/3)
YON CEVIRME                -1.292,30              +1.474,41   (9/12 kazanir)
```

Sıçrama sonrasında SHORT'ları **LONG'a çevirmek** −672 yerine **+1.474** yapardı.
Ama aynı çevirme sıçrama **öncesinde −1.292** eder. Yani bu bir kural değil,
**rejimin kendisi.**

Ek kanıt (5 dk mumdan): sıçrama öncesi SHORT'lar en iyi anında **+4,22%** artıya
geçiyordu; sıçrama sonrası yalnızca **+0,98%**. Sonradakiler hiç çalışmadı.

---

## 7 · LONG tarafı: kapı boğayı algıladı mı?

**Ham sayı evet der:** fren hiç çalışmayan günlerde LONG payı **%7,4 → %24,0**
(karıştırma testi p=0,002).

⚠️ **08-18'deki %100 sahtedir** — fren o gün 399 SHORT adayını kesmişti.

### Ama koşullu test kapıyı akladı

```
ONCESI kapi davranisi + SONRASI havuzu  ->  beklenen long payi %22,8
GERCEK sonrasi long payi                ->                     %24,0
aciklanamayan artik                     ->                     +1,2 puan
```

**Mekanizma tek cümle:** kapı, 24 saatte %20'den fazla yükselmiş coine
**her zaman LONG diyor.**

```
11-17 Agu : chg24 > %20 olan aday karari  8  ->  8'i LONG  (%100)
20 Agu    : chg24 > %20 olan aday karari 10  -> 10'u LONG  (%100)
```

Kural değişmedi; **o kurala uyan coin sayısı değişti.** 08-20'de aday havuzunun
medyanı **+13,80%**, adayların **%84'ü** yükseliyordu (önceki günler: medyan
+0,13…+5,97, yükselen %50-68).

O günün LONG'ları: `RE +37,1%` · `MAGMA +36,8%` · `RED +34,2%` · `MET +25,6%` ·
`EDGE +23,9%` — hepsi zaten fırlamış coinler.

**Yani bot boğayı "anlamadı", momentum kuralı daha sık tetiklendi.**

---

## 8 · LONG kombinasyon araması — N=14, uyarı amaçlı

SHORT'la aynı eşikte (en az 15 işlem) **hiçbir kural oluşamıyor** — N zaten 14.
Eşik 5'e indirilince arama çalışıyor ve tam da beklenen şeyi gösteriyor:

```
1'li kural (43 kural)
  GERCEK en iyi :  +718,34   ->  a_last3 >= 10,6
  SAHTE en iyi  : ortalama +647,39 · en yuksek +946,36
  p = 0,302  ->  SANSTAN AYIRT EDILEMIYOR

2'li kural (27 kural)
  GERCEK en iyi :  +537,95   ->  a_glob_ls>=1,2 & a_pos>=1,21
  SAHTE en iyi  : ortalama +564,61   <-- SAHTE, GERCEKTEN IYI
  p = 0,535
```

**2'li kuralda sahte veri gerçeği geçiyor.** N=14'te arama yapmanın ne kadar
kolay yanılttığının en temiz kanıtı bu.

---

## 9 · Ölçülemeyenler (dürüstlük notu)

| ne | neden |
|---|---|
| Fonlamanın pozisyon bazlı yükü | alan 2026-08-17'de eklendi, 23/117 pozisyonda var |
| Emir defteri derinliği | 12/117 pozisyonda var |
| Botun ORİJİNAL stop fiyatı | defter saklamıyor; geri kurma r=+0,61, yetersiz → mutlak ızgara kullanıldı |
| Sıçrama sonrası her şey | N=12 |
