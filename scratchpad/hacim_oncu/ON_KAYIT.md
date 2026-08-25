# ÖN-KAYIT — "Hacim var, fiyat yok" öncü sinyal mi?

*Yazıldı 2026-08-24 **koşturmadan ÖNCE**. Sonuç görüldükten sonra ölçüt değişmez.*

## NEDEN

Kullanıcı gözlemi: *"BTC yükselmeden ~2 saat önce hacim çok arttı ama fiyat
%2 kadar arttı."* Veride bakıldı, **desen mevcut**:

```
08-19 13:00   hacim  8,0x   fiyat +0,20%     <- hacim var, fiyat yok
08-19 15:00   hacim 37,6x   fiyat +3,99%     <- patlama, 2 saat sonra
```

**Ama aynı desen bir gün önce boşa yandı:**

```
08-18 14:00   hacim  7,2x   fiyat +0,77%     -> sonrasinda HICBIR SEY
```

1 lehte, 1 aleyhte. Ölçüm bunun için var.

**İDDİA: Hacim patlarken fiyatın kıpırdamaması, yaklaşan BÜYÜK bir hareketin
öncü işaretidir.**

## EŞİKLER — dağılımdan, sonuca bakmadan

BTC saatlik, N=17.725. Hacim katı = `qv[t] / medyan(qv[t-24..t-1])`.

```
HACIM KATI     %50 0,99 · %75 1,70 · %90 2,93 · %95 4,05 · %99 7,38
|SAATLIK RET|  %25 0,091 · %50 0,205 · %75 0,399 · %90 0,708
```

**Olay: `hacim ≥ 4x` (≈%95 dilim) VE `|ret| ≤ %0,50` (≈medyan) → N=314.**
Sağlamlık için 3x/5x ve %0,30/%0,75 varyantları da raporlanır (kural
değiştirmek için değil, eğrinin biçimini görmek için).

## 🔴 KONTROL — asıl mesele bu

| kol | tanım | ne izole eder |
|---|---|---|
| **ÖLÇÜM** | hacim ≥4x **VE** \|ret\| ≤%0,50 | "hacim var, fiyat yok" |
| **KONTROL 1** | hacim ≥4x **VE** \|ret\| >%0,50 | "hacim da var, fiyat da var" |
| **KONTROL 2** | hacim <4x | normal saatler |

**KONTROL 1 kritiktir:** iddia *"hacim büyük hareketi haber verir"* değil,
*"fiyat kıpırdamadan gelen hacim haber verir"* — yani **ayrışmanın** kendisi.
KONTROL 1 olmadan yalnız "hacim = oynaklık" tekrarlanmış olur.

## ÖLÇÜLECEK

İleri ufuklar **1 · 2 · 4 · 8 saat**:
- **BÜYÜKLÜK**: `|ileri getiri|` ve ufuk içindeki azami mutlak hareket
- **YÖN**: işaretli ileri getiri *(beklenti: boş — `04_yon_vs_oynaklik` ve
  TimesFM testi çıplak fiyattan yön çıkmadığını iki kez gösterdi)*

## ÖLÇÜTLER (sonuca bakmadan yazıldı)

| # | ölçüt | eşik |
|---|---|---|
| 1 | **Büyüklük** — ÖLÇÜM kolu, KONTROL 1'den büyük ileri hareket | 2sa ve 4sa'te fark > 0 |
| 2 | 🔴 **KARIŞTIRICI** — son 24sa gerçekleşmiş oynaklık **sabitlendiğinde** fark korunuyor mu | oynaklık kovalarının ≥3/4'ünde aynı işaret |
| 3 | **Holdout** — zaman ikiye bölünür, işaret ikinci yarıda da aynı | işaret aynı |
| 4 | **Yön** — ikincil, tavan ölçümü | beklenti null; geçerse bonus |
| 5 | **Vaka denetimi** — 08-19 13:00 (doğru) ve 08-18 14:00 (yanlış) sinyalin ikisi de kümede mi | ikisi de görünmeli |

**HÜKÜM KURALI:** **1 veya 2 geçmezse hüküm YAZILMAZ.** Ölçüt 2 olmadan bu
bulgu, CLAUDE.md'nin *"her yeni aday erken fiyat hareketinin başka bir ifadesi"*
uyarısına takılır — genişlik ölçümü bu yüzden çürüdü (BTC ile %51 ortak varyans).

İstatistik **gün-kümeli**. Yoğunlaşma denetimi raporlanır.

## KAPSAM DIŞI

- Bu bir kâr iddiası değildir. Geçse bile *"bota kapı ekle"* kararı ayrıdır.
- BTC-düzeyi ölçümdür (piyasa geneli). Coin-düzeyi ayrıca raporlanır ama
  hüküm BTC üzerinden yazılır — kullanıcının sorusu piyasa geneliydi.
- Hipotez 08-19 vakasından doğdu; **o vaka tek başına kanıt sayılmaz** (holdout).

Bota yazım: **YOK.** Salt-okuma.
