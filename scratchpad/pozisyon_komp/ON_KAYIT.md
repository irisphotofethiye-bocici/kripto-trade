# ÖN-KAYIT — OI ve long/short kompozisyonu SHORT girişlerini ayırıyor mu?

*Yazıldı 2026-08-25 **koşturmadan ÖNCE**. Sonuç görüldükten sonra ölçüt değişmez.*

## NEDEN

CLAUDE.md: *"Gerçekten yeni bilgi bandın dışındadır: emir defteri likiditesi ·
spot-perp basis · çapraz borsa · **pozisyon kompozisyonu**."*
Bu oturumda fiyat bandındaki dört aday elendi (genişlik · hacim-öncü · TimesFM ·
piyasa geneli fonlama). **Pozisyon kompozisyonu son bant-dışı aday.**

**Ana hipotez:** Bir pump'ın *nasıl* oluştuğu, *ne kadar* olduğundan ayrı bilgidir.
**OI ARTARAK** gelen pump = yeni kaldıraçlı LONG yığılması (kırılgan).
**OI DÜŞEREK** gelen pump = short kapanması (squeeze bitişi). Fiyat ikisinde aynı.

## 🔴 GÜÇ SINIRI — ÖNCEDEN İLAN EDİLİYOR

```
perp_seri:  102 sembol · 30 gun (2026-07-26 .. 2026-08-25) · 5dk
pump olayi (chg24>=+%20):  367 olay · 85 sembol · YALNIZ 32 BAGIMSIZ GUN
```

Kıyas: genişlik ölçümü **251 gün**, fonlama ölçümü **708 gün**.
32 günle standart hata ~4,7 kat büyük.

> ⚠️ **Bu ölçümde NULL SONUÇ, YOKLUĞUN KANITI DEĞİLDİR.** Güç yetersiz.
> Yalnız **büyük** bir etki görülebilir. Bu, sonuç görülmeden yazıldı.

Bu yüzden tasarım **GÜN İÇİ EŞLEŞTİRME**: her günün olayları kendi aralarında
üst/alt yarıya bölünür. Piyasa günlük hareketi (genişlik ve fonlama ölçümlerini
öldüren karıştırıcı) böylece **tanımı gereği** sabitlenir.

## ÖLÇÜLECEK DEĞİŞKENLER

Giriş anında (ileriye bakma yok), her biri **ayrı** sınanır:

| değişken | kaynak | ne sorar |
|---|---|---|
| `d_oi_3s` · `d_oi_24s` | `sumOpenInterestValue` değişimi | pump OI artarak mı geldi |
| `top_ls` seviye · değişim | `topLongShortPositionRatio` | büyük hesaplar hangi tarafta |
| `glob_ls` seviye · değişim | `globalLongShortAccountRatio` | perakende hangi tarafta |
| `top_ls − glob_ls` | ikisi | ⚠️ CLAUDE.md: **denendi, bulgu çıkmadı** — yineleme kontrolü |
| `taker` | `buySellRatio` | alıcı agresyonu |

**7 değişken = çoklu karşılaştırma.** Ön-kayıt gereği hepsi raporlanır;
**en iyisi seçilmez.**

## MEKANİK

Stop yok, hedef yok. **Ham ileri fiyat getirisi** (SHORT yönünde) 1 · 4 · 24 saat.
Fonlama **ayrı** raporlanır (bu oturumda ölçüldü: 24sa'te ham kenarın %85'i).

## ÖLÇÜTLER (sonuca bakmadan yazıldı)

| # | ölçüt | eşik |
|---|---|---|
| 1 | **Gün içi eşleşmiş fark** — üst yarı vs alt yarı, aynı gün | \|t\| ≥ 2,0 gün üzerinden |
| 2 | **Tutarlılık** — 1sa · 4sa · 24sa ufuklarının en az 2'sinde aynı işaret | 2/3 |
| 3 | **Holdout** — 32 gün ikiye bölünür, işaret aynı kalmalı | işaret aynı |
| 4 | **Yoğunlaşma** — en büyük sembol/gün payı | < %15 |

**HÜKÜM KURALI:** 1 ve 2 geçmezse hüküm YAZILMAZ. Geçse bile **N=32 gün**
nedeniyle *"aday"* olarak kaydedilir, hüküm değil — doğrulama için pencere
büyümeli (`perp_seri` her gün kuyruğundan bir gün kaybediyor; kayıt için
`perp_seri_indir.py` düzenli koşmalı).

Bota yazım: **YOK.** Salt-okuma.
