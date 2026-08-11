# Kanal + StochRSI stratejisi — analiz

*2026-08-11 · kripto perp bağlamı · ölçüm YAPILMADI*

---

## Bu belge ne, ne değil

**Ne:** görsel bir tariften çıkarılmış stratejiyi, iki kişinin aynı şekilde kodlayabileceği
kesin kurallara dönüştürür; avantaj/dezavantajını, risk yönetimini, hangi rejimde çalışıp
çalışmadığını ve geliştirme yollarını yazar.

**Ne değil:** bu stratejinin bir backtest'i **değildir.** Strateji hiç ölçülmedi.

Belgedeki her sayı ya **genel mekanik aritmetiktir** (başabaş oranı, maliyet payı gibi —
hesaplanabilir, tartışılamaz) ya da **bu projenin başka ölçümlerinden** aktarılmıştır ve
kaynağı belirtilmiştir. **"Bu strateji şu kadar kazandırır" türü tek bir iddia yoktur,**
çünkü öyle bir ölçüm yapılmadı.

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

## 2. ⚠️ İndikatörün kimliği belirsiz — ve bu her şeyi ters çeviriyor

Bana görsel verilmedi; tarif metinden geldi. **"Mavi üst çizgi + kırmızı alt çizgi + gri dolgu"**
en az üç farklı indikatöre uyuyor ve stratejinin anlamı üçünde **birbirine zıt:**

| aday | tanım | alt banda değmek ne demek | strateji ne olur |
|---|---|---|---|
| **Bollinger** | `SMA(20) ± 2 × stdev(20)` | oynaklığa göre uç sapma | **ortalamaya dönüş** ✓ |
| **Keltner** | `EMA(20) ± k × ATR(20)` | ATR'ye göre uç sapma | ortalamaya dönüş, daha yavaş tepkili |
| **Donchian** | `son N barın en yüksek / en düşüğü` | **yeni N-bar dibi** | **momentum kırılımı** ✗ |

Fark kozmetik değil. **Donchian ise alt banda değmek "ucuzladı" demek değil, "yeni dip yaptı"
demektir** — o noktada almak, düşen bıçağı bilerek yakalamaktır. Bollinger'de aynı olay
istatistiksel bir uç sapmadır ve geri dönme beklentisi mantıklıdır.

**Nasıl ayırt edilir (grafiğe bakarak, 10 saniye):**

- **Bantlar fiyat oynaklığıyla nefes alıyor mu** — sakin dönemde daralıp hareketli dönemde
  genişliyorsa → **Bollinger veya Keltner**
- **Bantlar basamaklı, yatay platolar çiziyor mu** — bir süre düz gidip sonra sıçrayarak
  yeni seviyeye geçiyorsa → **Donchian**
- **Fiyat banda değdiğinde bant o barda kırılıyor mu** — Donchian'da alt bant tanımı gereği
  fiyatı *takip eder*, fiyat onu geçemez; Bollinger'de fiyat bandın dışına taşabilir

> **Bu doğrulanmadan strateji kodlanamaz.** Yanlış aileyi seçmek, stratejiyi tersine
> çevirir — ortalamaya dönüş yerine kırılım alırsınız.

**Belgenin geri kalanı `Bollinger(20, 2.0)` varsayımıyla yazılmıştır** — tarifteki
"aşırı satımdan dönüş" mantığına uyan tek yorum budur. Varsayım yanlışsa 3. ve 8. bölümler
geçersizdir.

---

## 3. Kodlanabilir kurallar

Her eşik isimlendirilmiş parametre. Karşılaştırmalar (`<` mi `<=` mi) açıkça yazılmıştır.

### 3.1 Göstergeler

```
PARAMETRELER
  bant_periyot     = 20
  bant_sapma       = 2.0
  rsi_periyot      = 14
  stoch_periyot    = 14
  k_yumusatma      = 3
  d_yumusatma      = 3
  asiri_satim      = 20
  asiri_alim       = 80
  atr_periyot      = 14
  stop_nbar        = 10
  stop_atr_pay     = 0.25
  zaman_stopu_saat = 4          # config: maliyet.tutma_saat_tf["15m"]

BANT (Bollinger)
  orta_bant = SMA(kapanis, bant_periyot)
  sapma     = stdev(kapanis, bant_periyot)          # popülasyon std sapması
  ust_bant  = orta_bant + bant_sapma * sapma
  alt_bant  = orta_bant - bant_sapma * sapma

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

## 10. Ne ölçülmedi — kapanış

**Bu strateji hiç ölçülmedi.** Belgedeki hiçbir sayı onun performansına ait değildir.

- Genel aritmetik (başabaş, maliyet payı, R/R) → hesaplanabilir, tartışılamaz
- Aktarılan bulgular → bu projenin **başka** ölçümlerinden, kaynağı belirtilerek

### Ölçmek istenirse elimizde hazır olan

| ne | nerede |
|---|---|
| 570 sembol × 60 gün 1h mum | `scratchpad/klines_1h/` |
| A-stop mekaniği | `olcucu.py:120` |
| Wilder RSI | `olcucu.py:47` |
| ATR + swing/destek-direnç | `olcucu.py:89`, `olcucu.py:104` |
| Kontrol grubu + A/B zaman yarısı deseni | `scratchpad/oncesi_short.py` |
| Portföy / ruin simülatörü | `scratchpad/fren_riski.py` |

**Eksik olan tek şey:** Bollinger/StochRSI hesabı (~30 satır) ve **15 dakikalık önbellek.**
**1 saatlikte ölçüm bugün koşturulabilir** — ki 9.1'e göre zaten tercih edilmesi gereken
zaman dilimi odur.

### Ölçüm ne cevaplamalı

1. Sinyal, kontrol grubunu (rastgele barlar) **yeniyor mu?**
2. İsabeti, **stop genişlemesinden hızlı mı** artırıyor? (5.3'ün testi)
3. İki zaman yarısında da **ayakta kalıyor mu?**
4. Trend filtresi eklenince fark **ne kadar?** (9.2'nin değeri)
5. SHORT tarafı LONG'dan **güçlü mü?** (9.5)

---

*Kaynaklar: `fikir-defteri.md` (satır 1339, 1425-1432, 1873-1874 ve 2026-08-11 bölümleri),
`kripto-config.json → maliyet`, `olcucu.py`, `evren.py:209-260`, `testbot.py:655-662`.*
