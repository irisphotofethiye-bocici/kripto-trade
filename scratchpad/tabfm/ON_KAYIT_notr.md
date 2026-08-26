# ÖN-KAYIT — TabFM, NÖTR PENCEREDE (11-18 Ağustos)

**Yazıldı 2026-08-26, KOŞUMDAN ÖNCE.** Ölçütler sabit.

## NEDEN BU PENCERE — karıştırıcı YAPISAL OLARAK yok

Önceki pozisyon ölçümünü (19-26 Ağustos) öldüren şey karıştırıcıydı: görünen
ayırmanın **%85'i yöndü** (+1.704 $ → +253 $). Bu pencerede o sorun **olamaz**:

```
11-18 Agustos   108 pozisyon   rejim %100 NOTR
yon             101 SHORT / 7 LONG      <-- yon neredeyse SABIT
net             +237,89 $  ·  kazanan %46
```

Yön varyansı yoksa bulunacak ayırma yönden gelemez.
⚠️ Pencere **kârda** → soru değişir: *"kaybı önler miydi"* değil,
***"daha çok kazandırır mıydı"***.

## BÖLME

```
test gunleri  08-13, 08-14, 08-15, 08-16, 08-17     -> 81 pozisyon
baglam        o gunden ONCEKI tum pozisyonlar (29 -> 97)
```

DIŞARIDA: **08-11** (bağlam yalnız 4 pozisyon) · **08-12** (bağlam 20) ·
**08-18** (2 pozisyon, yarıya bölünemez). Bu üç gün **koşumdan önce** ve
**sonuç görülmeden** elendi; gerekçe tamamen örneklem büyüklüğü.

Girdiler, dışlananlar, iki etiket (L1 ham +24s · L2 gerçek P&L): önceki
ön-kayıtla **birebir aynı** (`ON_KAYIT_pozisyon.md`, e1097b5).

## ÖLÇÜTLER

| # | ölçüt | eşik |
|---|---|---|
| **N1** PARA | üst yarı − alt yarı, gerçek P&L | fark > 0 **ve** 5 günün **≥4**'ünde pozitif |
| **N2** SİNYAL | L1 ile gün-kümeli rho | rho > 0 ve t ≥ 1,5 |
| **N3** TABAN | TabFM, botun `skor`'unu **her iki** etikette geçmeli | geçmeli |
| **N4** KARIŞTIRICI | **oynaklık** (giriş `chg24` medyanı) ile ikiye bölünüp, etki **HER İKİ** yarıda da pozitif | ikisi de |

🔴 **N4, T4'ün ONARILMIŞ hâli.** Önceki ön-kayıtta karıştırıcı ölçütü
*"işaret aynı olsun"* diye yazılmıştı — **etki her iki kolda da yoksa
kendiliğinden geçiyordu** ve tam olarak öyle oldu (ikisi de negatif, "GEÇTİ"
yazdı, hiçbir şey söylemedi). Doğrusu: **etki AYAKTA KALSIN.**
Burada karıştırıcı **yön değil oynaklıktır**, çünkü yön zaten sabit.

**"Sınamaya değer" = N1 + N3 + N4.**

## ÇOKLU KARŞILAŞTIRMA — SAYILIYOR

Bu, aynı model + aynı defter üzerindeki **2. pencere**. Birincisi (19-26 BOĞA)
düştü. **Burada geçerse bu bir bulgu DEĞİL, bir REJİM BAĞIMLILIĞI iddiasıdır**
ve ancak üçüncü, bağımsız bir pencerede sınanarak bulguya dönüşür.
Üçüncü pencere denenirse o da sayılır ve raporlanır.

## BEKLENTİM

**N1'in düşmesini bekliyorum.** Gerekçe: bağlam 29-97 satır — dünkü aday
havuzu ölçümünde 800-3400'dü ve orada bile TabFM bedavayı geçememişti.
Ama yön karıştırıcısı burada yok, yani **eğer** bir ayırma varsa bu pencere
onu görmenin en temiz yeri.
