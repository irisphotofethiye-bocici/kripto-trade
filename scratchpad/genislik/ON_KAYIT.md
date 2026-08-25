# ÖN-KAYIT — Piyasa genişliği SHORT girişlerini uyarıyor mu?

*Yazıldı 2026-08-24 **koşturmadan ÖNCE**. Sonuç görüldükten sonra ölçüt değişmez.*

## NEDEN

Ölçüldü (`olcumler.md` → "AÇIĞIN KAYNAĞI"): defterin açığının **%65'i**
2026-08-18..21 penceresinden geliyor; bot BTC %14,1 ralli yaparken SHORT açtı
(08-20 girişleri: SHORT −1.206 $ / LONG +284 $). Aynı günlerde piyasa genişliği
**%26,5 → %85,9** fırladı.

**İDDİA: Genişlik yüksekken açılan SHORT'lar sistematik olarak daha kötüdür,
ve bu giriş anında bilinebilir.**

## VERİ

Saatlik genişlik = 24 saatlik getirisi pozitif olan sembollerin yüzdesi
(`01_genislik_serisi.py`, 566 sembol, 17.726 saat, ≥50 sembol şartı).
Dağılım ölçüldü, **sonuca bakmadan** çeyrekler eşik seçildi:

```
GENISLIK seviyesi : %25 dilim 16,8 · MEDYAN 44,7 · %75 dilim 77,8
24sa DEGISIMI     : %75 +31,5 · %90 +64,3 · %95 +78,0
```

⚠️ **Günlük endekste dramatik görünen 08-19 sıçraması (+59 puan), saatlik
seride yalnızca ~%88'lik dilim.** Yani "nadir olay" sezgisi zaten zayıflamış
durumda; ölçüm bunu hesaba katarak kurulmuştur.

Olay kümesi: `scratchpad/stop_carpani/kol_b.json` (N=13.159, 717 gün, ön-kayıtlı
mekanikle üretildi). SHORT olayları `chg24 ≥ +%20` pump girişleridir — botun
gerçek karakteri. Getiriler **k=1,50** ile, yani **botun kendi stopuyla**.

## ÖLÇÜTLER (sonuca bakmadan yazıldı)

| # | ölçüt | eşik |
|---|---|---|
| 1 | **Monotonluk** — genişlik kovaları arttıkça SHORT getirisi düşmeli | 4 kovada sıra bozulmasın |
| 2 | **Holdout** — zaman ikiye bölünür; üst-alt kova farkı ikinci yarıda aynı işaret | işaret aynı |
| 3 | **Rejim** — fark ATH · DÜZELTME · DERİN_AYI'nın en az 2'sinde korunmalı | 2/3 |
| 4 | 🔴 **KARIŞTIRICI** — BTC'nin kendi 24sa getirisi **sabitlendiğinde** genişlik hâlâ ayırıyor mu | BTC kovaları içinde aynı işaret, ≥3/4 kovada |
| 5 | **Pratik** — "genişlik > eşik iken SHORT açma" kuralı, kontrolü geçiyor mu (eşleşmiş) | fark > 0 |

**HÜKÜM KURALI:** **Ölçüt 4 geçmezse hüküm YAZILMAZ** — CLAUDE.md:
*"monotonluk tek başına YETMEZ, karıştırıcı kontrolü zorunlu."* Genişlik,
BTC'nin hareketinin başka bir ifadesi olabilir; o hâlde yeni bilgi değildir.
Bu proje bu tuzağa **iki kez** düştü (agresör dengesi · son yeni uç).

İstatistik **gün-kümeli**. Yoğunlaşma denetimi raporlanır.

## KAPSAM DIŞI

- Bu bir kâr iddiası değildir; geçse bile bota uygulanması ayrı karardır.
- Genişlik **aynı banttan** (Binance perp fiyatları) türüyor — kısmi bağımsızlık
  yeni bilgi kaynağı demek değildir.
- 08-18..21 penceresi bu ölçümün **içindedir**; hipotez oradan doğdu, dolayısıyla
  o pencere tek başına kanıt sayılmaz. Holdout bu yüzden var.

Bota yazım: **YOK.** Salt-okuma.
