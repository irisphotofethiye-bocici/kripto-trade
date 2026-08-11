# Pozisyonların gördüğü en yüksek kâğıt kâr

*2026-08-12 · 11-12 Ağustos'ta açılan 17 pozisyon · 1 dakikalık barlarla ölçüldü*

> **En yüksek tek rakam: ME `+356 $`** (11 Ağustos 22:11). Hâlâ açık, ömrünün %95'ini artıda geçirdi ve şu an **+351 $** — yani neredeyse tamamını korudu.
>
> Ama toplam tablo başka bir şey söylüyor: **17 pozisyon toplamda +2.112 $ kâğıt kâr gördü, şu anki toplam −720 $.** Aradaki **2.832 $** geri verildi.

---

## Tam tablo

Giriş anından çıkışa (açıksa şimdiye) kadar her dakika hesaplandı. Kısmi kâr alan pozisyonlarda pozisyon yarıya inip alınan kâr realize edildiği için, tepe rakamı buna göre modellendi — yoksa şişkin çıkardı.

| sembol | giriş | durum | **TEPE $** | tepe anı | gerçekleşen | bırakılan | artıda | süre |
|---|---|---|---|---|---|---|---|---|
| **ME** | 11 03:27 | AÇIK | **+356** | 11 22:11 | **+351** | +5 | %95 | 22,0s |
| PROM | 11 03:32 | STOP | +100 | 11 03:33 | −150 | +250 | %17 | 0,1s |
| WLFI | 11 03:57 | STOP | +24 | 11 03:59 | −30 | +55 | %33 | 0,1s |
| SQD | 11 04:29 | STOP | +37 | 11 04:38 | −275 | +311 | %17 | 0,4s |
| **AIOT** | 11 07:41 | TP2 | **+342** | 11 10:21 | **+333** | +9 | %96 | 2,7s |
| PROM | 11 08:34 | STOP | +113 | 11 08:46 | −265 | +378 | %11 | 0,9s |
| SQD | 11 08:55 | STOP | +24 | 11 08:58 | −265 | +289 | %17 | 0,3s |
| JST | 11 10:03 | STOP | +15 | 11 11:07 | −80 | +95 | %44 | 1,5s |
| **RVN** | 11 10:27 | AÇIK | **+246** | 11 18:41 | **−22** | **+268** | %78 | 15,0s |
| **UMA** | 11 12:21 | AÇIK | **+301** | 11 18:42 | +133 | +167 | %99 | 13,1s |
| **SQD** | 11 16:25 | STOP | **+269** | 11 16:43 | **−129** | **+398** | %49 | 1,3s |
| CAP | 11 18:15 | STOP | +21 | 11 18:46 | −134 | +155 | %9 | 3,8s |
| BANANAS31 | 11 18:16 | AÇIK | +45 | 12 01:04 | +44 | +2 | %75 | 7,2s |
| HOLO | 11 18:59 | STOP | +44 | 11 19:05 | −140 | +183 | %7 | 1,4s |
| AKE | 11 21:27 | STOP | +68 | 11 21:58 | −132 | +200 | %32 | 2,1s |
| SQD | 11 21:48 | AÇIK | +91 | 11 21:57 | +44 | +47 | %100 | 3,6s |
| HOLO | 12 00:38 | AÇIK | +16 | 12 01:21 | −3 | +19 | %23 | 0,8s |
| **TOPLAM** | | | **+2.112** | | **−720** | **+2.832** | | |

---

## 1. Büyük kâr gören 7 pozisyon — kimi tuttu, kimi bıraktı

100 $'ın üstünde kâğıt kâr gören 7 pozisyon var. Aralarındaki fark keskin:

| sembol | tepe | sonuç | **korunan** |
|---|---|---|---|
| ME | +356 | +351 | **%99** |
| AIOT | +342 | +333 | **%97** |
| UMA | +301 | +133 | %44 |
| SQD | +269 | −129 | **−%48** |
| RVN | +246 | −22 | −%9 |
| PROM | +113 | −265 | −%235 |
| PROM | +100 | −150 | −%150 |

**En acı iki vaka:**
- **SQD** 269 $'a çıktı, stop oldu, **−129 $** ile kapandı → 398 $ döndü
- **RVN** 246 $'a çıktı, hâlâ açık, şu an **−22 $** → 15 saattir taşınıyor

---

## 2. "Artıda geçen süre" kazananı kaybedenden ayırıyor

| grup | ortalama artıda geçen süre |
|---|---|
| **kazananlar (5)** | **%93** (en düşük %75) |
| kaybedenler (12) | %28 (en yüksek %78) |

Kazanan pozisyonlar ömürlerinin neredeyse tamamını artıda geçiriyor. Kaybedenler kısa bir an artıya çıkıp geri dönüyor — PROM %11, CAP %9, HOLO %7.

**Tek istisna RVN: %78 artıda geçmiş ama şu an eksi.** Kazananların bandında ama sonucu onlarla aynı değil. Hâlâ açık, henüz karar vermedi.

---

## 3. Dün eklenen kısmi kâr kuralı ne kurtardı

| sembol | kilitlenen |
|---|---|
| ME | +169,92 $ |
| UMA | +46,09 $ |
| BANANAS31 | +15,06 $ |
| **TOPLAM** | **+231,07 $** |

Bu 231 $ **realize edildi** — kural olmasaydı hepsi hâlâ risk altında olurdu.

En net örneği UMA: tepe 301 $, şu an 133 $. Kısmi alınmasaydı 133'ün de yarısı kalmayabilirdi. Kural tam da bu senaryo için eklenmişti.

**Ama dürüst olmak gerekirse ME'de kural gereksizdi** — o zaten tepesinin %99'unu koruyordu. Kısmi kâr, kazananın bir kısmını erken kilitleyerek kazancı buduyor; ölçümde kenarı ~%9 küçültmesinin sebebi bu. Bugünkü tablo hem faydasını (UMA) hem bedelini (ME) aynı anda gösteriyor.

---

## 4. Asıl soru: 2.832 $ geri verildi, bu kötü mü?

**Doğrudan kötü değil — bu sayının büyük kısmı hiç "kâr" değildi.**

Kaybeden 12 pozisyonun tepeleri çoğunlukla **+15 ile +68 $** arası, yani gürültü. Onlarda "bırakılan" rakamı aslında *küçük bir dalgalanma + stop zararı* toplamı. Örneğin PROM: tepe +100, sonuç −265 → "bırakılan 378" görünüyor ama gerçekte 100'ü hiç yakalanamayacak bir andı, 265'i ise normal stop.

**Gerçekten kâr bırakılan iki vaka var:** SQD (+269 → −129) ve RVN (+246 → −22). Toplam ~666 $.

Bu, sabit hedefli çıkış tasarımının bilinen bedeli: hedefe %10 kala dönen pozisyonda kâr korunmuyor. Ölçüm bu tasarımı seçmişti çünkü **erken çıkmak kazananları daha çok buduyordu** — ama tek tek işlemde canı yakan taraf tam olarak burası.

---

## Sınırlar

- Tepe rakamları **bar düşük/yüksek** değerlerinden; gerçekte o fiyattan çıkılabilir miydi ayrı soru (kayma yok sayıldı)
- Açık 6 pozisyonun "gerçekleşen" sütunu **şu anki** değer, nihai değil — RVN ve UMA hâlâ yön değiştirebilir
- 17 pozisyon, ~22 saat. **Karar penceresi 138 işlem;** bu tablo bir gözlem, kural değil

*Araç: `scratchpad/pnl_tepe_raporu.py` · veri: Binance 1 dakikalık barlar*
