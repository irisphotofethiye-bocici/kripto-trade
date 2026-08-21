# ÖN-KAYIT — HAM → MEKANİK → PORTFÖY, üç aşamalı tarama

**Yazıldığı an:** 2026-08-21, mekanik aşaması **koşturulmadan önce**.
**Kullanıcı talimatı:** *"Yaz, ama ham/mekanik/portföyü de ek taramalara tabi
tutacağız, bütün değişkenleri kendi verimizle deneyeceğiz. Sen başla ama
sonuç çıkarma."*
→ Bu belge ölçütleri sabitler. **Bu turda hüküm YAZILMAYACAK**, yalnız sayı üretilecek.

---

## Nereden geliyoruz

**HAM aşama bitti** (`24_rejim_kararliligi.py`). Beş rejim penceresinde
gün-kümeli, üst çeyrek eksi alt çeyrek, ileri +24 saat:

```
alan     ATH24    ATH25    TOPARL   D.AYI    AYI     ayni  |t|>=2
chg24    -7,29    -5,14    -3,23    -1,84    -2,73   5/5     4
pos      -8,08    -6,04    -3,06    -2,78    -2,95   5/5     5
last3    -7,20    -6,53    -4,19    -4,08    -1,95   5/5     4
rel3     -4,33    -5,12    -2,81    -1,46    -1,64   5/5     3
vol_x    +1,31    +0,21    +1,27    +1,74    +0,50   5/5     0
funding  -0,29    -0,72    +0,11    +1,40    +1,57   2/5     0
```

Etki: aralık tepesindekiler dibindekilerden 24 saatte **0,56–2,24 puan** geride.

⚠️ **Bu HAM getiridir.** `CLAUDE.md`: *"Sinyal, mekanikten arınık ölçülür"* —
ama sıra **ham → mekanik → portföy**'dür ve mekanik aşaması atlanamaz.
Bu projede mekanik bir kez bulguyu tamamen yedi (`kanal-stochrsi` 12.5→13),
bir kez de sahte "ölü sinyal" üretti (`>40 LONG`).

---

## AŞAMA 2 — MEKANİK (bu turda koşulacak)

### Soru
Ham kesitsel sıralama, **botun gerçek mekaniği** uygulandığında ayakta kalıyor mu?

### Mekanik — `ileri_rr.py` ile birebir, parametre değiştirilmez
```
giris   = tetigin ertesi 1h barinin ACILISI
stop    = swing + NBAR(10) + 1,5xATR (Wilder ATR14), ASGARI %2
hedef   = giris -+%10
ufuk    = 72 saat
maliyet = olcum_ortak.MALIYET (gidis-donus taker + slipaj)
fonlama = gercek funding gecmisi
bar ici : STOP (fitil) -> HEDEF (fitil)
```
**İki yön de ölçülür** (LONG ve SHORT ayrı) — `pos` sıralaması yön kuralı değil.

### 🔴 ZORUNLU SINAMA — mekanik yükü eşit mi
`CLAUDE.md` 2026-08-20 ihlali: hücreler oynaklıkta ayrışıyorsa ham getiri zorunlu.
Buradaki tersi de geçerli — **mekanikli sonuç yazmadan önce şu tablo üretilir:**

| çeyrek | stop genişliği (medyan %) | ATR/fiyat | stop-olma oranı |

`pos` üst ve alt çeyreğinde bu üç sayı **belirgin ayrışıyorsa**, mekanikli
karşılaştırma tek başına yorumlanmaz; ham ile birlikte raporlanır.

### Ölçüm birimi
Her pencere için ayrı: `pos` çeyreklerine göre net getiri, gün-kümeli t,
stop-olma oranı, ortalama tutma süresi.

### Geçme ölçütü — sonuç görülmeden sabitleniyor
Bu turda **geçme/kalma hükmü YAZILMAYACAK** (kullanıcı talimatı). Yalnız şu
üç sayı raporlanır ve kaydedilir:
1. Ham → mekanik geçişinde etkinin **kaçta kaçı kaldığı** (her pencere)
2. İşaretin **kaç pencerede korunduğu**
3. Stop genişliği / stop-olma oranı ayrışması

Hüküm, **portföy aşaması da bittikten sonra** ve ayrı bir ön-kayıtla yazılır.

---

## AŞAMA 3 — PORTFÖY (sonraki tur)

- Aynı anda azami 8 pozisyon · risk-önce boyutlandırma · kapasite kuyruğu
- Sıra `pos` düşükten yükseğe mi, skora göre mi? (ikisi de ölçülür)
- Fonlama ve giriş ücreti dahil, `equity` üzerinden türetilir
  (`CLAUDE.md` mutabakat denklemi)

---

## EK TARAMA — bütün değişkenler, kendi verimizle

**İki ayrı iz, karıştırılmaz:**

**İz A — çok rejimli (kline'dan türetilen alanlar).** 5 pencere.
`chg24 · pos · vol_x · rel3 · last3 · funding` + eklenecekler:
`ATR/fiyat · hacim payı · fiyat seviyesi · 20-bar aralık genişliği ·
BTC ile korelasyon · gün-içi saat`

**İz B — zengin alanlar (yalnız `radar_archive`, 2026-06-24+).** Tek dönem.
`score · comp · oi3 · oi24 · dip_yakit · ayrisma · mcap · float_oran ·
dusuk_float` (%100 dolu) **ve ayrıca** `top_ls · glob_ls · taker · smart`
(%29,8 dolu → **skor-süzülmüş evren, kendi kontrol grubuyla**).

🔴 İki iz **asla birleştirilmez** — B'nin evreni skor kapısıyla süzülmüş
(score medyanı 19,7 vs 7,5).

### Çoklu karşılaştırma
Taranan her alan sayılır ve raporlanır. `CLAUDE.md`: *"Çok sütun + az satır =
sahte bulgu garantisi."* Alan sayısı × pencere sayısı × ufuk sayısı açıkça
yazılır ve Bonferroni eşiği hesaplanır.

### Her bulguda zorunlu
gün/ay-kümeli t · şans (karıştırma) · **yoğunlaşma kontrolü (en iyi 3 sembol
çıkınca)** · rejim içi ayrı ölçüm · iki evren karıştırılmaz.

---

## Bu turda YAPILMAYACAK

- Hüküm yazılmayacak, `olcumler.md`'ye "geçti/kaldı" kaydı düşülmeyecek —
  yalnız **ölçüm tablosu** kaydedilecek.
- Bota hiçbir değişiklik önerilmeyecek.
- Eşikler (çeyrek bölmesi, +24sa/+72sa ufuk, mekanik parametreleri) sonuç
  görüldükten sonra oynatılmayacak.
