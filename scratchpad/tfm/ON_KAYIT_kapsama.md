# ÖN-KAYIT — TimesFM kuantil kapsama testi

*Yazıldı: 2026-08-24, **koşturmadan ÖNCE**. Sonuç görüldükten sonra ölçüt değişmez.*

## İDDİA

TimesFM 2.5'in verdiği `P10–P90` bandı (a) **dürüst** — gerçekten %80 kapsıyor,
ve (b) **işe yarar** — Wilder-ATR bandından dar.

**İkisi birden geçmeli.** Sadece dürüst olması yetmez: ATR de kendi çapında
dürüst, bedava ve zaten kurulu. Yeni araç, yerine geçtiği şeyden iyi olmalı.

## VERİ — sızıntısız pencere

Yalnız **2025-09-01 sonrası** barlar. TimesFM 2.5 Eylül 2025'te yayımlandı;
bu pencere modelin eğitiminden SONRA oluştu, ezberlemiş olamaz.
Kaynak: `scratchpad/klines_1h_uzun/` (566 sembol).
Bağlam 512 bar, ufuklar **4sa** ve **24sa**.

## KONTROL

Wilder ATR(14) — botun bugün kullandığı yöntem, `olcucu.py:98`.
Band: `son_kapanış ± k · ATR · √ufuk`. `k`, örneklemin **ilk yarısında**
%80 kapsama verecek şekilde kalibre edilir, **ikinci yarıda** uygulanır.
Böylece ATR en iyi hâliyle yarışır.

## ÖLÇÜTLER (sonuca bakmadan yazıldı)

| # | ölçüt | geçme eşiği |
|---|---|---|
| 1 | **Dürüstlük** — P10–P90 empirik kapsama | **%75–%85**, her iki ufukta |
| 2 | **İşe yararlık** — medyan band genişliği | ATR bandından **dar** (eşit kapsamada) |
| 3 | **Rejim kararlılığı** — kapsama, rejim başına | **%70–%90**, üç rejimin üçünde |
| 4 | ~~**Uç davranışı** — P25–P75 empirik kapsama~~ | ~~%45–%55~~ |
| 4' | **[DEĞİŞTİ 2026-08-24, sonuç GÖRÜLMEDEN]** Uç davranışı — **P20–P80** kapsama | **%55–%65** |

**HÜKÜM:** 1 ve 2 geçmezse TimesFM bu projede kullanılmaz, konu kapanır.
3 kalırsa kullanım **rejim koşullu** olur. 4 kalırsa yalnız geniş band kullanılır,
stop yerleşimi için güvenilmez.

## İSTATİSTİK

Gün-kümeli: kapsama önce **gün** içinde ortalanır, güven aralığı **günler**
üzerinden kurulur. 251+ bağımsız gün beklentisiyle çözünürlük ≈ **±%4**.
Yoğunlaşma denetimi: en büyük sembol payı ve gün payı raporlanır.

## YÖN — ikincil, tavan ölçümü

Nokta tahmini (`P50`) aynı ileri geçişte bedava geliyor. Yön isabeti de
kaydedilir. **Beklenti: rastgeleden farksız** (`04_yon_vs_oynaklik` ölçtü:
çıplak fiyattan yön çıkmıyor, 198 sembolün %43'ü). Geçerse sürpriz, geçmezse
*"fiyat bandı tükendi"* hükmü güçlenir. **İki sonuç da işe yarar.**

## KAPSAM DIŞI

Bu test **kâr iddiası değildir.** Geçmesi *"çalışan bir oynaklık ölçerimiz var"*
demektir; onunla kurulacak stop kuralının kâr edip etmeyeceği **ayrı ve sonraki**
sorudur (ham → mekanik → portföy sırası).

Bota yazım: **YOK.** Ayrı venv (`scratchpad/tfm_venv/`), salt-okuma.

## [DEĞİŞTİ 2026-08-24] — ölçüt 4 neden değişti

Model kuantilleri **ondalık dilim** olarak veriyor: `[0.1, 0.2, ..., 0.9]`
(`timesfm_2p5_base.py:92`; index 0 = ortalama, index 5 = medyan).
**P25 ve P75 diye bir çıktı yok** — ölçüt 4 uygulanamaz hâlde yazılmıştı.
En yakın simetrik alternatif `P20–P80` (nominal %60) ile değiştirildi.
Eski ölçüt silinmedi, üstü çizildi. **Değişiklik sonuç görülmeden yapıldı;**
toplama betiği o sırada hâlâ koşuyordu ve hiçbir çıktısına bakılmadı.
