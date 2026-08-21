# ÖN-KAYIT — 11-21 Ağustos gerçek holdout

**Yazıldığı an:** 2026-08-21, koşumdan **önce**, sonuç görülmeden.
**Kural:** `CLAUDE.md` — ön-kayıt koşumdan önce commit edilir, ölçüt sonradan
değiştirilmez.

---

## Neden bu bir holdout

`scratchpad/klines_1h_uzun/` **tam 2026-08-11 11:00'de bitiyordu**. 2 yıllık
veriden çıkarılmış her hüküm bu tarihten sonrasını **hiç görmedi**. Veri bugün
2026-08-21'e uzatıldı (+129.220 bar, +27.192 fonlama kaydı). Aradaki 10 gün
tamamen dışarıda kalmış bir örneklemdir.

## 🔴 İki sert sınır — sonuç görülmeden yazılıyor

**1. Boğa bacağı ASIL testin DIŞINDA kalıyor.**
Mekanik 72 saatlik ufuk kullanıyor. Tam ileri getirisi olan son giriş
**2026-08-18 civarı**. Boğa kırılması **08-19 18:15**'te oldu — yani **sonra**.
→ Asıl (kesin) test boğayı **görmüyor**.
→ Boğayı içeren kol ayrıca ve **AÇIKÇA "kırpık ufuk"** etiketiyle raporlanır;
   ana hükme dahil edilmez.

**2. Gün-kümesi sayısı 7-10. Bu ÇOK AZ.**
2 yıllık ölçümler 25 ay-kümesi kullanıyordu. Burada en fazla 10 gün var ve
gözlemler saatlik olduğu için **ağır örtüşüyor**.
→ Bu test **anlamlılık ölçemez.** Yalnızca **işaretin ters dönüp dönmediğini**
   görebilir. Geçme ölçütü buna göre kurulur.

## Sınanacak hükümler (2 yıllık değerleriyle)

| # | hüküm | 2 yıldaki değer |
|---|---|---|
| 1 | SHORT yığını: `fiyat>$0,07 · funding>−0,05 · chg24<%20 · btc_pay≠UST` | **+0,2340** (ay-t +1,33) |
| 2 | `funding ≤ −0,05` kapısı **ZARARLI** (kontrol kapıdan iyi) | ham fark **−0,5430** (t=−4,96) |
| 3 | `chg24 ≥ %20` pump engeli **DOĞRU** (geçenler kötü) | geçenler ham **−2,18** |
| 4 | `chg24 > %40` LONG + takip eden stop | **+2,379** (ay-t +3,24, 12/15 ay) |
| 5 | `btc_pay = UST` bandı SHORT için kötü | üç rejimde aynı işaret |

## Mekanik — 2 yıllık ölçümle BİREBİR aynı

`scratchpad/ileri_rr.py` yeniden kullanılır, **parametreler değiştirilmez**:

```
giris   = tetigin ertesi 1h barinin ACILISI
stop    = swing + NBAR(10) + 1,5xATR, Wilder ATR14, ASGARI %2
hedef   = giris -%10 (SHORT) / +%10 (LONG)
ufuk    = 72 saat
maliyet = olcum_ortak.MALIYET (gidis-donus taker + slipaj)
fonlama = gercek funding gecmisi, giris-cikis arasi toplam
bar ici : STOP (fitil) -> HEDEF (fitil)
MIN_VOL = 3.000.000 $ · ISINMA = 220 bar
```

⚠️ **`SEYRELT=24` KULLANILMAYACAK.** 10 günlük pencerede 24 barlık adım örneklemi
yok eder. Tüm saatlik barlar alınır. Bunun bedeli: gözlemler örtüşür →
**gün-kümeli** bakılır, gözlem sayısı anlamlılık iddiası için kullanılmaz.
(`CLAUDE.md` faz kilidi uyarısı: `SEYRELT=24` aynı UTC saatine düşürüyordu;
burada zaten kullanılmıyor, faz sorunu yok.)

## Geçme ölçütü — sonuç görülmeden sabitlendi

Her hüküm için **tek soru: işaret aynı mı?**

| sonuç | yazılacak |
|---|---|
| işaret aynı | **"henüz çürütülmedi"** — *doğrulandı DEĞİL* |
| işaret ters | 🔴 **"holdout'ta çöktü"** — hüküm `olcumler.md`'de işaretlenir |
| N < 200 gözlem veya < 5 gün | **"ölçülemedi"** |

**Anlamlılık iddiası YAPILMAYACAK.** t değeri hesaplanıp raporlanır ama geçme
ölçütü değildir — 7-10 küme buna yetmez.

## Ne yapılmayacak

- Eşikler ($0,07 · −0,05 · %20 · %40 · 72 saat) **oynatılmayacak**.
- Bir hüküm çökerse "şu alt kümede tutuyor" araması **yapılmayacak**.
- Sonuç ne olursa olsun **bota kural eklenmeyecek/çıkarılmayacak**.
- Kırpık-ufuk kolu **ana hükme karıştırılmayacak**.

## Beklenti (sonuç görülmeden)

- **1 (SHORT yığını):** işaret pozitif kalır sanıyorum ama düşük güvenle —
  ay-kümeli t zaten +1,33'tü, yani zayıf bir bulguydu.
- **2 (funding kapısı zararlı):** işaretin tutmasını bekliyorum, en sağlam ölçümdü.
- **3 (pump engeli):** tutar.
- **4 (>40 LONG + trailing):** **en riskli olan bu.** 10 günde `chg24>%40` olan
  sembol sayısı çok az olabilir → muhtemelen *"ölçülemedi"* çıkar.
- **5 (btc_pay):** ölçülebilirse tutar.

Genel beklentim: **hiçbiri çürütülmez ama hiçbiri de doğrulanmaz** — pencere
bunun için fazla kısa. Asıl değeri, bir hüküm **ters dönerse** onu yakalamak.
