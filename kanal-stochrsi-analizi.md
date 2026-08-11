# Price Headley Acceleration Bands + StochRSI — analiz ve ölçüm

*2026-08-11 · kripto perp · **ÖLÇÜLDÜ** · ana varyant + scalp + rejim: **hepsi KALDI***

> **Özet:** strateji ölçüldü — ana varyant, scalp varyantı ve rejim iddiası dahil.
> **Hiçbiri ön-kayıtlı ölçütü geçemedi.** Toplam 20+6 hücre, hepsi negatif.
>
> **Asıl teşhis:** maliyet düşülmeden **brüt getiri sıfır** (−0,01), rastgele girişin brütü
> ise daha iyi (+0,04). Yani sinyal yanlış yöne bakmıyor — **hiçbir yöne bakmıyor**;
> kaybı komisyon yapıyor. Parametre ayarıyla düzelmez.
>
> **"Nötr ve boğada çalışır" iddiası:** nötr **ölçüldü ve tutmadı**; strateji piyasa
> *yükselirken* en kötü sonucu veriyor. Gerçek boğa bu veride **yok**, o kısım açık kaldı.
>
> Ayrıntı: [ana ölçüm](#11-ölçüm-sonucu) · [scalp ve rejim](#12-scalp-varyanti-ve-notrbogada-calisir-iddiasi)

---

## Bu belge ne, ne değil

**Ne:** bir video tarifinden çıkarılmış stratejiyi kesin kurallara dönüştürür, ölçer, ve
avantaj/dezavantajını, risk yönetimini, hangi rejimde çalışıp çalışmadığını yazar.

**Ne değil:** stratejinin her koşulda kötü olduğunu kanıtlayan bir belge değildir. Ölçüm
tek zaman diliminde (1 saat), tek piyasada (kripto perp) ve **gerçek boğa içermeyen** bir
pencerede yapıldı (bölüm 12.1).

Bölüm 1-10 ölçümden **önce** yazıldı ve **değiştirilmedi** — böylece hangi öngörülerin
tuttuğu, hangilerinin tutmadığı görülebilsin (karne: bölüm 10).
Ölçümler bölüm 11 (ana) ve 12'dedir (scalp + rejim).

Belgedeki her sayı ya **genel mekanik aritmetiktir** ya **bu projenin başka
ölçümlerinden** aktarılmıştır ya da **kendi ölçümümüzden** gelir; her biri kaynağıyla
birlikte verilir.

**Bağlam:** orijinal örnek ASTOR ENERJİ (BIST) 15 dakikalıktı. Bu belge kripto perp
bağlamında yazıldı — projenin tüm altyapısı ve ölçülmüş bulguları oradan geliyor.
Maliyet, kaldıraç ve 7/24 işlem yapısı BIST'ten farklıdır; sonuçlar birebir taşınmaz.

---

## 1. Önce kanıt uyarısı

Kurallar, **geçmiş grafiğe sonradan işaretlenmiş** bir görüntüden çıkarıldı.

Bu, sinyalin gerçekliğine dair kanıt değildir. Seçilmiş bir grafikte işe yaramış örnekleri
işaretlemek, bu projenin **"tarama artığı"** dediği şeyin tam tanımıdır. Üç ayrı sorun aynı
anda var:

1. **Grafik seçilmiş.** Strateji çalışmadığı bir grafik gösterilmedi. Kaç grafiğe bakılıp bu
   seçildiği bilinmiyor.
2. **Oklar sonradan kondu.** Canlıda o barda o kararı verebilir miydiniz — grafikten
   anlaşılmaz. Özellikle "bar içinde mi, bar kapanışında mı" sorusu görselde görünmez.
3. **Kaybeden sinyaller işaretlenmedi.** Aynı kural, aynı grafikte kaç kez tetiklenip
   stop olmuş — sayılmamış.

Bu projede bunun canlı örneği var: taramada bulunan **en iyi görünen LONG hücresi**
(`funding >= +0.05`, +%0,69) zamanı ikiye bölünce dağıldı — **A yarısı +1,84 / B yarısı +0,14**.
Tek grafik, tanımı gereği tek yarıdır.

> **Bu, stratejinin kötü olduğu anlamına gelmez.** Sadece elimizde onun iyi olduğuna dair
> hiçbir kanıt olmadığı anlamına gelir. İkisi farklı şeylerdir ve bu ayrım belgenin geri
> kalanının temeli.

---

## 2. İndikatör: Price Headley Acceleration Bands

**Çözüldü.** Kaynak X gönderisi açılamadı (**HTTP 402** — X'in API duvarı), ama kullanıcı
indikatörü bildirdi: **Price Headley Acceleration Bands** (TradingView yerleşik) + StochRSI.

```
üst = SMA(yüksek × (1 + 4×(yüksek−düşük)/(yüksek+düşük)), 20)
alt = SMA(düşük  × (1 − 4×(yüksek−düşük)/(yüksek+düşük)), 20)
```

Oynaklığa uyum sağlayan bir bant — Bollinger/Keltner ailesinden, Donchian'dan değil.
Yani "alt banda değmek" **uç sapma** demek, "yeni dip" değil. Ortalamaya dönüş okuması
tutarlı.

### ⚠️ Ama yazarın kendi kullanımı bunun TERSİ

Headley bu bantları **kırılım** için tasarladı: fiyatın bandın **dışında** art arda
kapanmasını *hızlanma* sinyali sayar — yani bant, "buradan geri döner" değil,
**"buradan çıkarsa hızlanır"** demek için çizilmiştir.

Videodaki kullanım (alt bantta AL) indikatörün **tasarım amacının tersidir.** Bu tek
başına stratejiyi geçersiz kılmaz — bir araç yaratıcısının aklına gelmeyen bir işe
yarayabilir — ama kanıt yükünü artırır.

> **Bu belirti ölçümden önce yazıldı ve ölçümde doğrulandı:** alt banttan alım
> ölçütü geçemedi (bölüm 11).

### Ölçümden önceki belirsizlik (kayıt için)

İndikatör bildirilmeden önce tarif üç aileye birden uyuyordu. Bu yüzden ölçüm **üçünü de**
kapsadı — hangisinin doğru olduğu belli olmasaydı bile sonuç bilinsin diye:

| aday | tanım | alt banda değmek ne demek | strateji ne olur |
|---|---|---|---|
| **Bollinger** | `SMA(20) ± 2 × stdev(20)` | oynaklığa göre uç sapma | **ortalamaya dönüş** ✓ |
| **Keltner** | `EMA(20) ± k × ATR(20)` | ATR'ye göre uç sapma | ortalamaya dönüş, daha yavaş tepkili |
| **Donchian** | `son N barın en yüksek / en düşüğü` | **yeni N-bar dibi** | **momentum kırılımı** ✗ |

Fark kozmetik değil. **Donchian ise alt banda değmek "ucuzladı" demek değil, "yeni dip yaptı"
demektir** — o noktada almak, düşen bıçağı bilerek yakalamaktır. Bollinger'de aynı olay
istatistiksel bir uç sapmadır ve geri dönme beklentisi mantıklıdır.

**Ölçüm sonucu üçü de aynı yere çıktı** (bölüm 11): Acceleration −0,09, Bollinger −0,15,
Donchian −0,26. **Bant ailesi seçimi sonucu değiştirmedi** — bu, belirsizliğin
sanıldığı kadar kritik olmadığını gösterdi. Beklentimin tersi; kayda geçsin.

---

## 3. Kodlanabilir kurallar

Her eşik isimlendirilmiş parametre. Karşılaştırmalar (`<` mi `<=` mi) açıkça yazılmıştır.

### 3.1 Göstergeler

```
PARAMETRELER
  bant_periyot     = 20         # TradingView varsayılanı
  rsi_periyot      = 14
  stoch_periyot    = 14
  k_yumusatma      = 3
  d_yumusatma      = 3
  asiri_satim      = 20
  asiri_alim       = 80
  atr_periyot      = 14
  stop_nbar        = 10
  stop_atr_pay     = 0.25
  zaman_stopu_bar  = 12         # 1 saatlik için; config maliyet.tutma_saat_tf["1h"]
                                # 15 dakikalık kullanılacaksa: 4 saat = 16 bar

BANT — PRICE HEADLEY ACCELERATION BANDS
  faktor    = 4 * (yuksek - dusuk) / (yuksek + dusuk)     # bar başına
  ust_bant  = SMA(yuksek * (1 + faktor), bant_periyot)
  alt_bant  = SMA(dusuk  * (1 - faktor), bant_periyot)
  orta_bant = SMA(kapanis, bant_periyot)                  # yalnız görsel

  # TradingView kaynağı 2*((y-d)/((y+d)/2)) yazar; sadeleşince yukarıdakiyle aynıdır.
  # DİKKAT: bant, o barın KENDİ yüksek/düşüğünden türer — Bollinger gibi yalnız
  # kapanışa bakmaz. Bu yüzden geniş gövdeli bir bar bandı anında genişletir.

STOCHRSI
  r        = RSI(kapanis, rsi_periyot)              # Wilder RSI
  ham      = (r[şimdi] - min(r, stoch_periyot)) / (max(r, stoch_periyot) - min(r, stoch_periyot))
  %K       = SMA(ham * 100, k_yumusatma)
  %D       = SMA(%K, d_yumusatma)
```

**Not:** `max(r) == min(r)` olduğunda (RSI tam yatay) bölme sıfıra düşer — bu durumda
`ham = 0.5` alınır. Nadirdir ama canlıda çökme sebebidir.

**Uyarı:** RSI'ın Wilder mı basit ortalama mı olduğu StochRSI değerini belirgin değiştirir.
Bu projede `olcucu.rsi14` **Wilder**'dır (`olcucu.py:47`). Aynısı kullanılmalı ki diğer
ölçümlerle kıyaslanabilir kalsın.

### 3.2 Giriş

Üç koşul **aynı barda, bar kapanışında** sağlanmalı:

```
KOSUL 1 (bant temasi)
  bar.dusuk <= alt_bant                    # DEĞME yeterli; kapanışın altında olması ŞART DEĞİL

KOSUL 2 (osilatör dönüşü)
  %K[önceki] < asiri_satim                 # önceki barda aşırı satımdaydı
  AND %K[şimdi] > %D[şimdi]                # şimdi yukarı kesişim var
  AND %K[önceki] <= %D[önceki]             # kesişim GERÇEKTEN bu barda oldu

KOSUL 3 (onay)
  bar KAPANMIS olmali                      # bar içi tetikleme YOK
```

> **3. koşul en çok atlanan ve en pahalı olandır.** Geriye dönük grafikte bar içi sinyal
> bedava görünür — barın nasıl kapanacağını zaten bilirsiniz. Canlıda bilmezsiniz. Bar içi
> tetikleyen her backtest, gerçekte alınamayacak işlemleri sayar.

**Giriş fiyatı — iki seçenek, farkı yazılmalı:**

| seçenek | fiyat | artı | eksi |
|---|---|---|---|
| A | onay barının kapanışı | sinyale en yakın | kapanış anında emir yetişmeyebilir |
| B | **sonraki barın açılışı** | gerçekçi, uygulanabilir | 15dk'da açılış boşluğu riski |

**B önerilir** — bu projenin tüm backtest'leri `b[gi]["o"]` (sonraki barın açılışı) kullanır,
böylece kıyaslanabilir kalır.

### 3.3 Stop

```
aday_1 = son stop_nbar barın en düşüğü
aday_2 = alt_bant (giriş anındaki)
stop   = min(aday_1, aday_2) - stop_atr_pay * ATR(atr_periyot)
```

Bu, projenin `olcucu.measure` A-stop mantığının aynısıdır (`olcucu.py:120-150`) — kasıtlı,
çünkü diğer ölçümlerle karşılaştırılabilirlik ancak böyle korunur.

### 3.4 Çıkış

```
HEDEF     : ust_bant                       # DİNAMİK — her barda yeniden hesaplanır
STOP      : yukarıdaki sabit stop          # giriş anında sabitlenir, kaydırılmaz
ZAMAN     : zaman_stopu_saat sonra piyasa fiyatından çık
GECERSIZ  : %K > asiri_alim olup sonra %K < %D'ye dönerse çık (hedefe değmeden)

Aynı barda hem stop hem hedef görülürse → STOP sayılır (kötümser varsayım)
```

### 3.5 ⚠️ Ölçülebilirlik tuzağı

**Hedef dinamik.** Üst bant her barda hareket ediyor. Bu, backtest'te bir karar noktası
yaratır ve **önceden yazılmazsa sonuç istenen yöne çekilebilir:**

- **(a)** Hedef, girişteki üst bant değerinde **dondurulur** → sabit hedef, ölçmesi dürüst
- **(b)** Hedef, üst bantla birlikte **hareket eder** → fiyat yükselirken bant da yükselir,
  hedefe hiç ulaşılamayabilir; ya da fiyat düşerken bant düşüp hedefi "yakalayabilir"

**(b)'nin tehlikesi:** düşen bir piyasada üst bant aşağı inip fiyata *değerse*, backtest
bunu "hedefe ulaştı = kazanç" olarak sayar — oysa fiyat hiç yükselmemiştir. Bu, sessizce
kazanç uyduran bir hatadır.

**(a) önerilir.** Hangisi seçilirse seçilsin, **ölçümden önce yazılmalıdır.**

---

## 4. Avantajlar

**1. Sinyal tanımlı ve tekrarlanabilir.** "Trend çizgisi çektim" gibi yoruma açık bir
öğe yok. İki kişi aynı veriden aynı sinyal listesini üretir. Bu, ölçülebilirliğin ön koşulu
ve çoğu grafik stratejisinin sağlayamadığı şey.

**2. İki bağımsız aile birleşiyor.** Bant = *fiyatın konumu*, StochRSI = *momentumun yönü*.
Tek osilatör kullanan sistemlerin en büyük sorunu sürekli sinyal üretmeleridir; konum şartı
bunu belirgin azaltır.

**3. Stop ve hedefin ikisi de yapısal.** Sabit yüzde değil, piyasanın kendi oynaklığından
türüyor. Sakin piyasada dar, hareketli piyasada geniş — kendiliğinden uyum sağlar.

**4. Zayıflık satın alıyor, güç değil — ve bu ölçülmüş bir avantaj.**

Bu projenin en çok tekrarlanan bulgusu, **güç satın almanın kaybettirdiğidir.** Yükselen
coinlerin tetik sonrası **+24 saat medyanı −%2,62** *(fikir-defteri.md:1339; N=1.563)*.
Aynı sayı, farklı bir evrende farklı bir yöntemle yapılan bağımsız bir ölçümde de çıktı
(erken-kuşak, N=298, medyan −%2,62). İki bağımsız ölçümün aynı sayıda buluşması nadirdir.

Bu strateji **ters yönde duruyor** — yükseleni değil, düşeni alıyor. Bu ona gerçek bir puan
kazandırır ve onu bu projede reddedilmiş pump-kovalama ailesinden ayırır.

---

## 5. Dezavantajlar

### 5.1 ⚠️ En ağır itiraz: stop yapısı gereği dar

Stop, alt bandın hemen altında. Bu bir ayar tercihi değil, **stratejinin tanımının sonucu.**

Bu projede 2026-08-11'de ölçülen (577 olay, hedef %10 / 72 saat, gerçek A-stop mekaniği):

| stop dilimi | N | isabet | başabaş için gereken | sonuç |
|---|---|---|---|---|
| **< %1,92** | 145 | **%10,3** | ~%16 | **net sıfır** |
| %1,92–3,40 | 144 | %20,1 | ~%21 | başabaş |
| %3,40–5,51 | 144 | %33,3 | ~%30 | kazanıyor |
| > %5,51 | 144 | %56,2 | ~%44 | en çok |

İsabet **monoton** artıyor ve mekanik gerekçesi var:

> **Dar stop = yapı hemen dibinde = gürültü teğet geçiyor.** Fiyat bir tabanın hemen
> üstündeyse, o kadar yakın bir taban işlem gelişemeden sıradan dalgalanmayla delinir.

**15 dakikalıkta bu sorun daha sert**, çünkü bant genişliği 1 saatliğin belirgin altında;
stop mesafesi de aynı oranda daralır.

### 5.2 Stopu genişletmek kurtarmıyor — ölçüldü

Aynı gün test edildi: dar stopları tabana **itmek** (elemek yerine):

| | isabet | başabaş gereken |
|---|---|---|
| olduğu gibi | %11,0 | %12,1 |
| stop %2,0'a genişletilmiş | %13,6 | %16,7 |

**Başabaş, isabetten hızlı büyüyor.** Kazanç +2,6 puan, gereklilik +4,6 puan. Net etki
sıfırın altında.

### 5.3 Kovalama tuzağının kardeşi

Bu projenin genellenebilir kuralı *(fikir-defteri.md:1425-1432)*:

> **Yön değil sadece hareket öngören her sinyal değersizdir**, çünkü stop mesafesi hareketle
> birlikte büyür ve fazladan isabeti fazlasıyla yer.

Ölçülmüş rakamlar: sinyal isabeti **%27,8 → %39,8 (+%43)** çıkarıyor — kulağa harika geliyor.
Ama aynı sinyal stop mesafesini **%1,00 → %1,99 (+%99)** genişletiyor, ve başabaş oranı
**%28,6 → %44,3** çıkıyor. Net: **kötüleşme.**

**Bu stratejiye uygulaması:** StochRSI dönüşünün isabeti artırdığını göstermek yetmez.
İsabeti, **stop genişlemesinden daha hızlı** artırdığı gösterilmelidir. Tarif bunu iddia
etmiyor bile.

### 5.4 Maliyet 15 dakikalıkta öldürücü

`kripto-config.json → maliyet`:

```
taker_fee_pct  0.045  ×2 (giriş+çıkış)  = 0.090
slippage_pct   0.020  ×2 (giriş+çıkış)  = 0.040   (testbot.py:655-662)
                                   TOPLAM ≈ %0,13 / işlem
```

Bant genişliği %1,5 olan bir 15dk kurulumunda bu, **hedefin %9'u.** Günde 5 sinyal alan bir
sistem, ayda yaklaşık **sermayenin %20'sini** yalnızca maliyete verir — kazansa da kaybetse de.

> Bu, stratejinin en sessiz düşmanı. Zaman dilimi düştükçe hedef küçülür ama maliyet sabit
> kalır. 15 dakikalıkta oran, günlükte olduğunun onlarca katıdır.

### 5.5 LONG tarafı bu projede hiç doğrulanamadı

| tarama | kombinasyon | sonuç |
|---|---|---|
| tetik eşiği × giriş zamanlaması × ufuk | 30 | **hepsi negatif** |
| stop × ufuk (%2,5 hedef) | 33 | **hepsi negatif** |

*(fikir-defteri.md:1873-1874)*

**Dürüst uyarı:** ölçümün 46 gününün **tamamı ayı/nötr rejim.** Bu bulgu LONG'u çürütmez —
"ayı piyasasında LONG kaybettirdi" der, ki bu zaten beklenen şeydir. Ama elimizde LONG'un
işe yaradığına dair **hiçbir** ölçüm de yok.

### 5.6 Çıkış kuralı orijinal tarifte yoktu

Görselde yalnız **yeşil oklar** vardı. Çıkışı olmayan bir tarif, kârı görsel olarak
sınırsız gösterir — okun sağındaki her yükseliş "kazanç" gibi okunur.

Çıkış kuralı bu belgede eklendi (kullanıcı seçimi: üst bant). Ama şunu kayda geçirmek gerekir:
**stratejinin yarısı orijinal kaynakta yoktu.**

### 5.7 Sinyaller bağımsız değil

Piyasa geneli düştüğünde **bantlar aynı anda birçok sembolde delinir.** Yani 6 sinyal
6 bağımsız bahis değil, aynı bahsin 6 kopyasıdır.

Bu projede portföy simülasyonunun **gün-bloklu bootstrap** kullanmasının sebebi tam buydu:
tek tek işlemleri karıştırmak, aynı gün her şeyin birlikte kaybettiği gerçeğini siler ve
ruin riskini **sahte şekilde düşürür.**

---

## 6. Risk yönetimi

### 6.1 ⚠️ Boyutlandırma ile stratejinin çakışması

Risk-önce boyutlandırma der ki: `notional = hedef_risk / stop_mesafesi`.

Bu kural, **dar stoplu işleme en büyük pozisyonu verir.** Bu stratejinin stopu ise yapısı
gereği dar. İki şey burada çarpışıyor:

> Sistem, tam da 5.1'de "net sıfır üretiyor" diye ölçülen dilime **en büyük sermayeyi**
> tahsis eder.

Bu projede aynı sorun canlıda görüldü ve ölçüldü: kaldıraç tavanı yüzünden bot değersiz
dar-stop işlemini sermayenin **1,00 katıyla**, kârlı geniş-stop işlemini **0,40 katıyla**
alıyordu. Boyutlandırma edge'in tersine bakıyordu.

### 6.2 Asgari stop tabanı — ve bu stratejiyle uyum sorunu

Projede 2026-08-11'de canlıya alınan kural: **`asgari_stop_pct = 2.0`** — stop %2'den darsa
işleme girme.

**Bu stratejinin sinyallerinin büyük kısmı bu kapıdan geçemez.** 15 dakikalık bir Bollinger
alt bant temasında stop tipik olarak %0,3–%0,8 arasındadır.

Bu bir çelişki değil, **ölçülmüş bir uyumsuzluk.** Üç yoldan biri seçilmeli:

1. **Zaman dilimini yükselt** (15dk → 1s/4s) → stoplar doğal olarak genişler *(önerilen)*
2. **Bant genişliği tabanı koy** → yalnız bant yeterince genişken sinyal al
3. **Tabanı bu strateji için gevşet** → ancak ölçümle gerekçelendirilirse; şu an gerekçe yok

### 6.3 İşlem başına risk

Projede 2026-08-11'de ölçülen (portföy simülasyonu, 2000 yol, gün-bloklu bootstrap):

| işlem başına risk | 46 günlük medyan çarpan | 11 günde fren |
|---|---|---|
| %3 | 1,24 | %57 |
| **%1,5** | **2,49** | **%4,5** |

**Riski yarıya indirmek parayı iki katına çıkardı.** Sebep sihir değil: %3'te yolların %97'si
düşüş frenine çarpıp işlem yapmayı bırakıyor. **Ölü bot para kazanmaz.**

Bu bulgu stratejiden bağımsızdır — hangi sinyali kullanırsanız kullanın geçerlidir.

### 6.4 Her kurulum için önden hesaplanacak tek sayı

```
başabaş_isabet = (stop% + maliyet%) / (hedef% - maliyet% + stop% + maliyet%)
```

| stop % | hedef % | başabaş isabet (maliyet %0,13 dahil) |
|---|---|---|
| 0,30 | 2,00 | **%18,7** |
| 0,50 | 2,00 | %25,2 |
| 1,00 | 2,00 | %37,7 |
| 0,50 | 3,00 | %18,0 |
| 2,00 | 4,00 | %35,5 |

**Kullanımı:** sinyalinizin gerçek isabeti bu sayının üstünde değilse, R/R ne kadar
etkileyici görünürse görünsün sistem kaybeder.

### 6.5 Eş zamanlı maruziyet ve fren

Sinyaller kümelendiği için (5.7) şunlar gerekli:
- **eş zamanlı pozisyon sınırı** (projede 8)
- **sembol başına cooldown** (projede 4 saat)
- **düşüş freni** (projede %25) — ama frenin **normal dalgalanmanın medyanına** konmaması
  şartıyla; öyle olursa güvenlik değil yazı-tura olur

---

## 7. Örnek senaryolar

> **Bunlar aritmetiktir, backtest değildir.** Amaç mekaniğin nasıl işlediğini göstermek.
> Gerçek isabet oranları bilinmiyor — çünkü ölçülmedi.

### Senaryo 1 — Tez gerçekleşir (ve gizli tuzağı)

```
Kurulum (15dk):
  orta bant  1,0120     üst bant  1,0240     alt bant  1,0000
  bar düşüğü 0,9995  →  alt banda değdi ✓
  %K önceki 12 (<20), şimdi 22 > %D 16      →  kesişim ✓
  ATR(14)    0,0045    son 10 bar dibi  0,9990

Giriş (sonraki bar açılışı)  1,0010
Stop  = 0,9990 − 0,25×0,0045 = 0,9979   →  %0,31
Hedef = üst bant 1,0240                  →  %2,30

Ham R/R                  7,4 : 1
Maliyet dahil net hedef  %2,17
Maliyet dahil net stop   %0,44
BAŞABAŞ İSABET           %16,9
```

**Görünüşte muhteşem:** 7,4:1 R/R, sadece %17 isabet yeterli.

**Gizli tuzak iki tane:**

1. **%0,31'lik stop, ölçülen dağılımın en alt ucunun bile altında** — 577 olayın 10.
   yüzdeliği %1,19'du. Bu genişlikteki stopların bulunduğu dilim %10,3 isabet verdi;
   gereken %16,9. Canlıda görülen en dar stop **%0,42'ydi ve pozisyon 6 dakikada silindi**
   (WLFI, 2026-08-11). Yüksek R/R, isabetin düşük olacağını *haber veren* şeydir —
   telafi eden şey değil.
2. **Canlı botta bu işlem hiç açılmazdı** — `asgari_stop_pct = 2.0` kapısı %0,31'i reddeder.

> Bu senaryo stratejinin en iyi hâlini gösteriyor ve yine de mevcut ölçülmüş kurallarla
> çelişiyor. Belgedeki en önemli tek nokta budur.

### Senaryo 2 — Düşen bıçak (trend günü)

Piyasa gün boyu düşüyor. Fiyat alt bant boyunca **yürüyor**; bant her barda aşağı kayıyor,
StochRSI defalarca aşırı satımdan kesişiyor. **6 sinyal, 6 stop.**

Ortalama stop %0,31, maliyet %0,13.

**(a) Kaldıraç tavanı devredeyken** (notional ≤ 1,0× sermaye):

```
stop kaybı   6 × 0,31% × 1,00  =  −1,86%
maliyet      6 × 0,13% × 1,00  =  −0,78%
                        TOPLAM =  −2,64%
```

**(b) Risk-önce tam uygulansaydı** (%1,5 hedef risk, notional = 1,5/0,31 = **4,8× sermaye**):

```
stop kaybı   6 × 1,50%         =  −9,00%
maliyet      6 × 0,13% × 4,84  =  −3,77%
                        TOPLAM = −12,77%
```

> **Kaldıraç tavanı burada kazara koruma sağlıyor** — ama bu bir tasarım değil, şans.
> Dar stoplu bir stratejide risk-önce boyutlandırma, tavan olmadan tek günde çift haneli
> kayıp üretir.

Ve dikkat: bu 6 işlem **bağımsız değil** — hepsi aynı düşüşün parçası. Birden fazla sembolde
aynı anda tetiklendiğinde çarpan büyür.

### Senaryo 3 — Testere: maliyetin tek başına yediği hesap

Fiyat dalgalanıyor ama üst banda hiç ulaşmıyor. Her işlem **zaman stopuyla** (4 saat)
giriş fiyatına yakın kapanıyor. Kazanç da kayıp da yok — sadece maliyet.

```
Günde 8 sinyal, notional 1,0× sermaye
Günlük  8 × 0,13%          =  −1,04%
20 iş günü (bileşik)        ≈  −18,9%
```

**Tek bir kaybeden işlem olmadan sermayenin beşte biri gitti.**

> Bu, 15 dakikalık ortalamaya-dönüş stratejilerinin en yaygın ölüm biçimidir ve grafiğe
> bakarak **asla görülmez** — çünkü grafikte oklar var, komisyon yok.

---

## 8. Hangi rejimde çalışır, hangisinde çalışmaz

Projenin mevcut F10 rejim katmanına bağlanır *(evren.py:209-260)*:

| rejim | beklenti | gerekçe |
|---|---|---|
| **Yatay / BELİRSİZ** | **en uygun** | ortalamaya dönüş yalnız burada tanımlıdır — ortalama yerinde duruyor |
| BOGA_DUZELTME | uygun | düzeltme dipleri boğa yapısı içinde geri alınır |
| TEPKI_RALLISI | dikkat | bantlar hızla genişler, stop gürültünün içinde kalır |
| **DERIN_AYI** | **çalışmaz** | aşağıdaki bölüm |
| TAM_BOGA | zayıf | alt bant nadiren test edilir → sinyal kıtlığı |

### 8.1 ⚠️ Düşüş trendi: ayar hatası değil, tanım gereği kırılma

Kullanıcının kendi uyarısı doğru — ve sebebi teknik değil kavramsal:

> **Ortalamaya dönüş, ortalamanın yerinde durduğu varsayımına dayanır.**

Trendde ortalamanın kendisi kayar. Alt bant, "ucuz" değil **"yeni normal"** olur. Fiyat
banda değer, siz alırsınız, bant sizinle birlikte aşağı iner, stop olursunuz — sonra aynı
sinyal 3 bar sonra tekrar tetiklenir.

Bu bir parametre sorunu değildir. **Bant periyodunu, sapmayı veya StochRSI eşiğini değiştirmek
bunu çözmez** — hepsi aynı yanlış varsayımın üstüne kurulur. Tek çözüm **stratejiyi o rejimde
çalıştırmamaktır.**

Somut belirti: aynı sembolde **kısa aralıkla art arda tetiklenen sinyaller.** Sağlıklı bir
ortalamaya-dönüş ortamında sinyaller seyrektir; sıklaşması rejimin döndüğünün habercisidir.
Bu, kodlanabilir bir uyarıdır (bkz. 9.2).

---

## 9. Geliştirme önerileri

Sırayla, en yüksek etkiden başlayarak. Her biri **neyi düzeltmeye çalıştığıyla** birlikte.

### 9.1 Zaman dilimini yükselt: 15dk → 1s veya 4s ⭐
**Neyi düzeltir:** aynı anda **üç** sorunu — maliyet payı (5.4), dar stop (5.1),
`asgari_stop_pct` uyumsuzluğu (6.2).
**Bonus:** projenin elindeki **570 sembol × 60 gün 1h önbelleğiyle bugün ölçülebilir hâle
gelir.** 15 dakikalıkta önce veri indirilmesi gerekir.

### 9.2 Trend filtresi ⭐
**Neyi düzeltir:** düşen bıçağı (8.1) — stratejinin tek yapısal kırılma noktası.
Somut biçimler: `fiyat > MA200`, veya `orta bant eğimi ≈ 0`, veya `son N barda M'den fazla
sinyal tetiklendiyse dur` (8.1'deki sıklaşma belirtisi).

### 9.3 Bant genişliği tabanı
**Neyi düzeltir:** dar stop sorununu doğrudan — bant darken sinyal alma.
Projedeki `asgari_stop_pct` kuralıyla **aynı mantık**, sadece stop yerine bant üzerinden.

### 9.4 Sabit hedef, kısmi kâr yok
**Neyi düzeltir:** dinamik hedef belirsizliğini (3.5) ve ölçüm dürüstlüğünü.
Projede ölçüldü: **iyi girişte sıkı çıkış kazancı keser** — A+B kapısında sabit %10 hedef,
kısmi kâr + trailing'i +1,24 → +2,01 farkla yendi. Ama kural giriş-koşulludur:
*kötü girişte sıkı çıkış kaybı keser, iyi girişte kazancı keser.*

### 9.5 SHORT tarafını da ölç
**Neden:** bu projenin bütün ölçümleri **SHORT tarafını sistematik olarak daha güçlü** buldu.
Simetrik kural hazır: **üst bant teması + StochRSI aşırı alımdan aşağı kesişim.**
Aynı iş, iki katı bilgi.

### 9.6 Onay barının kapanmasını bekle
**Neyi düzeltir:** geriye dönük yanılsamayı (3.2). Ölçümde ve canlıda aynı kuralın
geçerli olmasını sağlar. Maliyeti: birkaç tik daha kötü giriş. Getirisi: ölçümün gerçek olması.

### 9.7 Ölçmeden önce yazılacaklar (ön-kayıt)
Bu projenin standardı. Ölçüme başlamadan önce **sonuç görülmeden** kâğıda geçmeli:
- hedef dondurulacak mı, hareket edecek mi (3.5)
- kontrol grubu ne (öneri: aynı sembol/dönemde **rastgele** barlar)
- geçme ölçütü ne, **ve** zaman ikiye bölündüğünde iki yarının da geçmesi şartı
- kaç olay birikince karar verilecek

---

## 10. Ölçümden önce yazılan tahminler

Bölüm 1-9 ölçümden **önce** yazıldı. Karneleri bölüm 11'de:

| # | tahmin | sonuç |
|---|---|---|
| 5.1 | dar stop yüzünden çalışmaz | ✅ **tuttu** — stop %51 oranında önce yeniyor |
| 8.1 | düşüş trendinde çalışmaz | ✅ **tuttu** — MA200 altı anlamlı negatif (t=−2,58) |
| 9.2 | trend filtresi düzeltir | ❌ **tutmadı** — filtre hücresi gürültü (t=+0,31) |
| 2 | bant ailesi kritik, seçim her şeyi değiştirir | ❌ **tutmadı** — üç aile de negatif |
| ön-kayıt | genel sonuç negatif olacak | ✅ **tuttu** |

---

## 11. ÖLÇÜM SONUCU

**Araç:** `scratchpad/kanal_stoch.py` · **ön-kayıt:** `fikir-defteri.md`, commit `2bde27b`
(**koşturmadan önce** commit'lendi, git geçmişi doğrular)

**Kısıt:** kullanıcı isteğiyle bota hiç dokunulmadı. Ölçüm tamamen `scratchpad/` içinde,
salt-okunur mum önbelleği üzerinde. `testbot.py` / `radar.py` / config / gölge defter
**değişmedi.**

**Kurulum:** 570 sembol · ~60 gün · 1 saatlik · giriş sonraki bar açılışı ·
maliyet %0,13 · ufuk 12 bar · hedef girişte dondurulmuş · sinyal seyreltme 24 bar

### 11.1 Ana tablo

| küme | N | net % | isabet | stop% | hedef% | A yarısı | B yarısı |
|---|---|---|---|---|---|---|---|
| **ACC LONG** *(asıl)* | 5488 | **−0,09** | %6,2 | 1,65 | 5,62 | +0,09 | −0,32 |
| **ACC SHORT** *(asıl)* | 5789 | **−0,12** | %4,9 | 2,03 | 6,01 | −0,09 | −0,15 |
| ayrıştırma: yalnız bant | 9583 | −0,03 | %5,7 | 1,02 | 5,34 | +0,09 | −0,15 |
| ayrıştırma: yalnız StochRSI | 17965 | −0,19 | %17,8 | 2,56 | 3,78 | −0,19 | −0,19 |
| Bollinger LONG *(duyarlılık)* | 9562 | −0,15 | %19,9 | 1,51 | 3,24 | −0,05 | −0,24 |
| Donchian LONG *(duyarlılık)* | 5205 | −0,26 | %10,9 | 1,26 | 4,36 | −0,30 | −0,22 |
| **KONTROL rastgele (long)** | 5387 | −0,19 | %26,7 | 2,94 | 3,14 | −0,30 | −0,09 |
| **KONTROL rastgele (short)** | 5380 | −0,06 | %29,5 | 3,32 | 2,74 | +0,06 | −0,18 |

**Ön-kayıtlı ölçüt:** net > 0 **ve** kontrolü yenmek **ve** her iki zaman yarısında pozitif.

> ### Altı varyantın altısı da KALDI.

Bant ailesini değiştirmek kurtarmıyor. Bileşenleri ayırmak da: yalnız bant −0,03,
yalnız StochRSI −0,19, ikisi birlikte −0,09. **Hiçbir bileşen kayıp bir kenar taşımıyor.**

### 11.2 Neden — açık 18,3 puan

```
medyan stop  %1,65      medyan hedef  %5,62      R/R 3,4 : 1

GEREKEN başabaş isabet  : %24,4
GERÇEKLEŞEN isabet      : % 6,2
AÇIK                    : −18,3 puan

çıkış dağılımı:   STOP %51   ·   SÜRE %43   ·   HEDEF %6
```

**R/R 3,4:1 kulağa iyi geliyor ve tamamen yanıltıcı** — bölüm 7'deki Senaryo 1'in
uyarısı tam olarak buydu. İşlemlerin yarısı stopa gidiyor, %43'ü zaman aşımına uğruyor;
hedefe yalnız **%6'sı** ulaşıyor.

### 11.3 ⭐ Hedefi yakınlaştırmak KURTARMIYOR — en önemli bulgu

Akla gelen ilk çare: "üst bant çok uzak, daha yakın bir hedef koyalım." Ölçüldü —
hedef, bant genişliğinin bir payı olarak süpürüldü:

| hedef | hedef % | isabet | başabaş gereken | **açık** | net % |
|---|---|---|---|---|---|
| bant × 0,25 | 1,40 | %48,0 | %58,2 | **−10,2** | −0,07 |
| bant × 0,50 | 2,81 | %23,1 | %39,9 | **−16,8** | −0,11 |
| bant × 0,75 | 4,21 | %11,5 | %30,3 | **−18,8** | −0,08 |
| bant × 1,00 | 5,62 | %6,2 | %24,4 | **−18,2** | −0,09 |

**Dört hedefte de açık kapanmıyor, dördünde de net negatif.**

Hedef yaklaştıkça isabet gerçekten yükseliyor (%6,2 → %48,0) — ama başabaş gereksinimi
**daha hızlı** yükseliyor (%24,4 → %58,2). Bu, projenin defalarca ölçtüğü aynı yapı:

> **Başabaş, isabetten hızlı büyür.** Bölüm 5.2 ve 5.3 bunu başka verilerde göstermişti;
> burada üçüncü kez, bu strateji üzerinde çıktı.

**Sonuç:** bu bir hedef-ayarı sorunu değil. **Stop, her hedeften önce yeniyor** — kurulumun
kendisinde yön bilgisi yok.

### 11.4 Tek hayatta kalan hücre gürültü çıktı

Ana taramada iki zaman yarısında da pozitif olan **tek** hücre `ACC LONG + fiyat > MA200`
idi (N=786, +%0,05). Test edildi:

| alt küme | N | net % | standart hata | t | karar |
|---|---|---|---|---|---|
| fiyat > MA200 | 786 | +0,052 | 0,166 | **+0,31** | **GÜRÜLTÜ** (\|t\|<2) |
| fiyat < MA200 | 4702 | −0,119 | 0,046 | −2,58 | anlamlı **negatif** |
| tümü | 5488 | −0,095 | 0,046 | −2,05 | anlamlı **negatif** |

Trend filtresi hücresi sıfırdan **ayırt edilemiyor.** Onlarca hücreye bakıldığında birinin
pozitif görünmesi zaten şansla beklenir — bu, aranan kanıt değil, aranırken bulunan gürültü.

**Ama bir öngörü doğrulandı:** MA200 **altında** anlamlı negatif (t=−2,58). Bölüm 8.1'in
*"düşüş trendinde çalışmaz"* öngörüsü veriyle örtüştü — üstelik o bölüm ölçümden önce
yazılmıştı.

### 11.5 ⚠️ Geçersiz ölçüm — dürüstlük kaydı

Betiğin çıktısında *"yazarın kendi kullanımı: KIRILIM long"* satırı **%98,2 isabet**
gösteriyor. **Bu sayı anlamsızdır, kullanılamaz.**

Sebep: fiyat üst bandın üstünde kapandığında hedef (üst bant) girişin **arkasında** kalıyor;
medyan hedef mesafesi %0,03. İşlem açılır açılmaz "hedefe ulaştı" sayılıyor. Kırılım
varyantı bu çıkış kuralıyla **ölçülemez** — kendi çıkış kuralıyla ayrıca ölçülmesi gerekir.

Satır tablodan silinmedi; hata görünür kalsın diye bırakıldı.

### 11.6 Ne kanıtlandı, ne kanıtlanmadı

**Kanıtlanan:** bu strateji, **1 saatlik kripto perp'te, ayı/nötr rejimde, TradingView
varsayılan parametreleriyle** kaybediyor. N büyük (5.488), sonuç istatistiksel olarak
sıfırdan ayrı (t=−2,05), ve bant ailesi ile hedef mesafesine karşı **dayanıklı** —
yani tek bir ayarın talihsizliği değil.

**Kanıtlanmayan:**
- **15 dakikalıkta** ne olur — orijinal tarif oydu, ölçüm 1 saatlik
- **BIST'te** ne olur — ASTOR bir hisse; maliyet, kaldıraç, seans yapısı tümüyle farklı
- **Boğa rejiminde** ne olur — ölçümün tamamı ayı/nötr
- **Başka parametrelerde** ne olur — taranmadı; taransaydı **tarama artığı** riski doğardı

**Not:** LONG tarafı rastgele kontrolü bir tık yeniyor (−0,09 vs −0,19), yani sinyalde
sıfır bilgi olmayabilir. Ama fark güvenilir değil ve **her hâlükârda maliyetten sonra
negatif** — "kontrolden az kaybetmek" bir strateji değildir.

---

## 12. SCALP VARYANTI ve "nötr/boğada çalışır" iddiası

**Soru:** kısa dönem LONG scalp olarak ayarlansa ne olur? Strateji için genellikle
*"nötr ve boğada çalışır"* deniyor.

**Araç:** `scratchpad/kanal_scalp.py` · 3.786 sinyal

### 12.1 ⚠️ Önce: bu veride gerçek boğa YOK

```
BTC 2026-06-12 → 2026-08-10 :  63.618 → 64.289  =  +%1,1
tepeden dip                  :  −%13,4
```

Pencere **nötr/yatay.** Dolayısıyla:

- **"Boğada çalışır"** → bu veriyle **test EDİLEMEZ.** Edilmedi, edilmiş gibi de yazılmadı.
- **"Nötr'de çalışır"** → **test edilebilir ve edildi.** Üstelik ortalamaya dönüşün ev sahası
  tam da bu rejimdir; strateji en avantajlı zeminde sınandı.

### 12.2 Hedef × ufuk ızgarası — 20 hücrenin 20'si negatif

net %, maliyet dahil, A-stop:

| hedef | 2 bar | 4 bar | 6 bar | 12 bar |
|---|---|---|---|---|
| %0,50 | −0,14 | −0,15 | −0,17 | −0,17 |
| %0,75 | −0,13 | −0,14 | −0,18 | −0,19 |
| %1,00 | −0,11 | **−0,14** | −0,19 | −0,20 |
| %1,50 | −0,09 | −0,13 | −0,21 | −0,24 |
| %2,00 | −0,09 | −0,14 | −0,24 | −0,27 |

**Tek pozitif hücre yok.** Scalp'e çekmek — kısa ufuk, yakın hedef — sonucu düzeltmiyor.

### 12.3 ⭐ Rejim iddiası tersine çıktı

Birincil scalp (hedef %1,0 · 4 bar), **rejim-eşleşmiş kontrolle**:

| rejim | N | net % | t | KONTROL | fark |
|---|---|---|---|---|---|
| TÜMÜ | 3786 | −0,14 | −6,46 | −0,09 | −0,05 |
| **BTC > MA500 (yükselen)** | 2843 | **−0,18** | −7,17 | −0,11 | −0,07 |
| BTC < MA500 (düşen) | 943 | −0,01 | −0,17 | −0,03 | +0,02 |
| **BTC 24s YATAY (nötr)** | 2030 | **−0,13** | −4,20 | −0,08 | −0,05 |
| **BTC 24s YUKARI** | 524 | **−0,24** | −3,91 | −0,12 | −0,12 |
| BTC 24s AŞAĞI | 1232 | −0,10 | −3,34 | −0,06 | −0,04 |

> **Strateji piyasa yükselirken EN KÖTÜ performansı veriyor** (−0,24, t=−3,91).
> En az kötü olduğu yer piyasanın **düştüğü** dönem — ve orada bile sıfırdan ayırt
> edilemiyor (t=−0,17; yarılar +0,62 / −0,09 ile dağılıyor).

**Nötr rejim:** net −0,13, t=−4,20, kontrolden 0,05 puan geride. **İddia ölçüldü, tutmadı.**

### 12.4 ⭐⭐ Rejim-eşleşmiş kontrol neden şart

Yükselen bir piyasada **herhangi bir long** para kazanır. "Boğa hücresinde pozitif çıktı"
demek, strateji çalışıyor demek **değildir** — piyasa çalışıyor demektir.

Doğru kıyas aynı rejimdeki **rastgele** long'lardır. Bu ölçümde strateji, altı bölmenin
**beşinde rastgeleye yeniliyor.**

Bu, herhangi bir "boğada çalışır" iddiasını test ederken atlanmaması gereken adımdır.

### 12.5 ⭐⭐⭐ Asıl teşhis: sinyalde bilgi yok, kaybı maliyet yapıyor

`brüt = net + maliyet (%0,13)`:

| küme | net % | **brüt %** |
|---|---|---|
| strateji, tümü | −0,14 | **−0,01** |
| strateji, nötr | −0,13 | **0,00** |
| **rastgele kontrol** | −0,09 | **+0,04** |

**Brüt olarak strateji tam bir yazı-turadır.** Kaybın neredeyse tamamı komisyon ve kaymadır.
Üstelik rastgele girişin brütü (+0,04), stratejininkinden (−0,01) daha iyi.

> **Bu, "yanlış yöne bakıyor" demek değil — "hiçbir yöne bakmıyor" demek.**
> Parametre ayarıyla düzelmez. Düzelmesi için sinyalin gerçek bir kenar taşıması gerekir,
> ve taşımıyor.

### 12.6 Sıkı scalp stopu daha da kötü

| stop | stop% | başabaş gereken | isabet | net % | t |
|---|---|---|---|---|---|
| A-stop (asıl) | 1,48 | %64,9 | %41,8 | −0,14 | −6,46 |
| 0,5 × ATR | 0,57 | %44,8 | %32,9 | −0,18 | −11,77 |
| sabit %0,5 | 0,50 | %42,0 | %25,5 | −0,15 | −14,59 |
| sabit %1,0 | 1,00 | %56,5 | %34,8 | −0,16 | −10,94 |

Stop daralınca başabaş gereksinimi düşüyor (%64,9 → %42,0) — ama isabet **daha hızlı**
düşüyor (%41,8 → %25,5). Açık her yerde 16-23 puan.

**Bu yapı bu belgede dördüncü kez çıktı** (5.2, 5.3, 11.3, 12.6). Artık bir tesadüf değil,
bu strateji ailesinin imzası:

> **Başabaş, isabetten hızlı büyür.**

---

## 13. Kapanış — bundan sonra ne yapılır

### Karar
Bu strateji **bu hâliyle bu piyasada kullanılmamalı.** Ölçüm ön-kayıtlıydı, örneklem büyüktü
(5.488 sinyal), sonuç istatistiksel olarak sıfırdan ayrıydı (t=−2,05), ve **bant ailesine
ve hedef mesafesine karşı dayanıklıydı** — yani tek bir ayarın talihsizliği değil.

Bota **eklenmedi**, gölge deftere **alınmadı.** Sebep: gölge defter bir *aday havuzu* değil,
ölçüm bütçesidir; ön-kayıtlı ölçütü kesin biçimde geçemeyen bir tez oraya girerse gerçek
adayların yerini işgal eder.

### Yine de ölçmeye değer iki şey

| # | ne | neden | maliyet |
|---|---|---|---|
| 1 | **Kırılım yönü** (Headley'nin kendi kullanımı) | Bölüm 11.5'te **geçersiz** ölçüldü — hedef girişin arkasında kaldı. Kendi çıkış kuralıyla hiç ölçülmedi. Yazarın tasarım amacı buydu. | Yeni çıkış tanımı + tekrar koşum |
| 2 | **Gerçek boğa rejimi** | Bölüm 12.1: bu veride boğa yok (BTC +%1,1). İddia ne doğrulandı ne çürütüldü. | Rejim döndüğünde veri birikmesi |

**Not:** "nötr'de çalışır" iddiası artık **ölçüldü ve tutmadı** (bölüm 12.3) — o yüzden
listeden çıktı. Geriye kalan tek gerçek boşluk kırılım yönü ve gerçek boğa.

**15 dakikalık** listeden çıkarıldı: bölüm 12.5 sinyalin brüt olarak yazı-tura olduğunu
gösterdi. Zaman dilimini düşürmek maliyet payını **artırır**, bilgi eklemez.

### Ne kanıtlanmadı — tekrar
- **15 dakikalıkta** ne olur (ölçüm 1 saatlik)
- **BIST'te** ne olur (ASTOR hisse; maliyet, kaldıraç, seans yapısı tümüyle farklı)
- **Boğa rejiminde** ne olur (ölçümün tamamı ayı/nötr)
- **Başka parametrelerde** ne olur (taranmadı — taransaydı tarama artığı riski doğardı)

### Yeniden üretmek için
```
python scratchpad/kanal_stoch.py        # ana ölçüm (ön-kayıtlı)
python scratchpad/kanal_stoch_tani.py   # tanı (keşifsel)
python scratchpad/kanal_scalp.py        # scalp + rejim (ön-kayıtlı birincil yapılandırma)
```
Ön-kayıt: `fikir-defteri.md`, commit `2bde27b` — **koşturmadan önce** commit'lendi.
Veri: `scratchpad/klines_1h/` (570 sembol, 2026-06-12 → 2026-08-10).

### Sisteme etki: yok
Kullanıcı kısıtı gereği `testbot.py`, `radar.py`, `kripto-config.json` ve gölge defter
**hiç ellenmedi.** Devam eden iki ölçüm penceresi (SHORT 138 işlem · LONG gölge 25 olay)
etkilenmedi.

---

*Kaynaklar: kendi ölçümü `scratchpad/kanal_stoch.py` · `fikir-defteri.md` (satır 1339,
1425-1432, 1873-1874 ve 2026-08-11 bölümleri) · `kripto-config.json → maliyet` ·
`olcucu.py` · `evren.py:209-260` · `testbot.py:655-662`.*
