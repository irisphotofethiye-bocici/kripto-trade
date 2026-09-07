# ÖN-KAYIT — STOP LİKİDİTE ETKİSİ, `ATR/FİYAT` SABİTLENİNCE KALIYOR MU?

**Yazılma tarihi:** 2026-09-07 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"onlarca ölçümde kusurlu da olsa bulduğumuz tek şey
bu, üstüne gitmelisin"* → *"a'yı ölç"*
**Betik:** `scratchpad/stop_likidite/03_atr_katman.py`

---

## 1 · NE SINANIYOR — hipotez DEĞİL, KARIŞTIRICI

`ON_KAYIT_stop_likidite_2yil.md` (`5a66803`) **yedi ölçütü de geçti**:
`N=82.085 · 738 gün`, katmanlı fark **+4,58 puan**, `t +5,48`, negatif
kontrol temiz.

🔴 **Ama ben bir açık bıraktım ve kendim yazdım:** `stop_p` dilimleri
boyunca `stop%` `4,48 → 3,14`'e düşerken `stop ATR` `1,25 → 1,37`'ye
çıkıyor → **yüksek `stop_p` grubu daha DÜŞÜK OYNAKLIKLI sembollerde.**
`U5` yalnız **ATR-mesafesini** sabitledi, **oynaklık düzeyini** değil.

Ve `ATR/fiyat` bu projede **MDE'yi aşan tek ölçümdü** (2026-09-06,
`olcumler.md`): düşük ATR dilimi `R +0,5096`, yüksek `−0,1509`.

```
SORU: stop-likidite etkisi, ATR/fiyat SABITLENINCE kaliyor mu?
```

Bu **dördüncü bakış değil** — hipotez aynı kalıyor, sınanan şey
**karıştırıcı**. Ön-kayıt `5a66803` bölüm 1 dördüncü *bakışı* yasakladı,
karıştırıcı kontrolünü **zorunlu** tuttu.

## 2 · YÖNTEM — 02_uzun.py ile BİREBİR, yalnız katmanlama değişiyor

Popülasyon · harita · `stop_p` · negatif kontrol · keşif/holdout ayrımı:
**aynen**. Değişen tek şey **neye göre katmanlandığı**.

```
BIRINCIL   : ATR/fiyat besli katmanlari ICINDE (kume ici - bos bolge)
             katman farklarinin AGIRLIKLI ortalamasi
IKINCIL-1  : CIFT katmanlama  ATR/fiyat x stop_atr  (5x5 = 25 hucre)
IKINCIL-2  : sembol-kumeli cikarim (etki birkac sembolden mi geliyor)
```

⚠️ `25` hücrede `N≈3.300` düşüyor; `<200` olan hücre **atlanır** ve
kaç hücrenin atlandığı **raporlanır**.

## 3 · ÖLÇÜTLER — sonuç görüldükten sonra değişmez

Karşılaştırma tabanı: `02_uzun.py`'nin **ATR-mesafesi katmanlı** sonucu
= **+4,58 puan**.

| # | ölçüt | eşik |
|---|---|---|
| **A1** | ATR/fiyat katmanlı fark > 0 | evet |
| **A2** | fark, `+4,58 puan`ın **en az %50'si** (≥ **2,29 puan**) | evet |
| **A3** | gün-kümeli **t ≥ +2,5** | evet |
| **A4** | KEŞİF ve HOLDOUT **aynı işaret** | evet |
| **A5** | **ekonomik taban ≥ 3,0 puan** (öncekiyle AYNI eşik) | evet |
| **A6** | **çift katmanlı** (ATR × stop_atr) fark, ATR-katmanlının ≥ %50'si | evet |
| **A7** | **sembol-kümeli** t ≥ +2,5 (etki tek tük sembolden gelmiyor) | evet |

```
KARISTIRICI KAPANDI = A1..A7 hepsi -> etki ATR'den BAGIMSIZ, sirada tasinabilirlik
KISMEN ATR          = A1+A3+A4 gecer ama A2 duser
ATR'NIN KILIGI      = A1 veya A4 duser  -> BULGU COKER
SEMBOLE OZGU        = A1..A6 gecer ama A7 duser
GORULUR AMA ZAYIF   = A1..A4 gecer, A5 duser
```

🔴 **`A2` ve `A5` sayısal ve koşumdan önce sabit.** *"Biraz azaldı ama
hâlâ var"* demeye yer bırakmıyorum.

## 4 · NE YAPILMAZ

- Bota/state/deftere **dokunulmaz** · ücretli çağrı **YOK**
- Katman sayısı, kova genişliği, katsayılar **ARANMAZ** (öncekinden aynen)
- Faz kaydırma **aynen** (`hash(sembol) mod 24`)
- Ölçüt gevşetilmez; `A2` düşerse *"kısmen ATR"* yazılır, kural yazılmaz
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 5 · GEÇERSE

Sıradaki **tek** adım: **taşınabilirlik** — botun evreninde
(`radar_archive`, skorlu girişler) aynı etki var mı. Ayrı ön-kayıt.
Ondan önce **kural yazılmaz**, kod değişmez.

## 6 · BEKLENTİM — koşumdan önce

**`A2`'nin geçmesine %45.** Lehte: `U5`'te ATR-mesafesi sabitlenince etki
**büyümüştü** (%119) — karıştırıcı yönünde davranmadı. Aleyhte: oynaklık
düzeyi ile ATR-mesafesi **farklı** şeyler ve `ATR/fiyat` bu projede
ölçülmüş en güçlü tekil değişken.

**`A7`'nin (sembol) geçmesine %60** — 554 sembol var, birkaçının
domine etmesi zor ama imkânsız değil.

**Hepsinin geçmesine %30.**

⚠️ Bugün on dokuz ön-kayıt yazıldı, **biri** geçti. Bu yirmincisi ve
o birinin **sınavı**.
