# ÖN-KAYIT — emir defteri derinliği kendi işlemlerimizin sonucunu öngörüyor mu?

**Yazılma tarihi:** 2026-08-30 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"orderbook'a bakmak bir kazanç olabilir mi"*

---

## 1 · Bu ölçüm NE DEĞİL — sınırı önce yazıyorum

🔴 Emir defterinin **klasik kenarı dengesizliktir** (alış tarafı satış tarafından
kalın mı). **Bu ölçüm onu ölçemez** ve ölçmeye çalışmayacak:
[testbot.py:159](testbot.py#L159) yalnız pozisyonun **yiyeceği tarafı** saklıyor
(SHORT'ta bid, LONG'ta ask). İki taraf yok → dengesizlik hesaplanamaz.

🔴 Derinlik yalnız **dolan pozisyonda** kaydediliyor, reddedilen adaylarda değil.
Kodun kendi notu: *"Yalnız dolan pozisyonda ölçmek SEÇİLİM YANLI bir örneklemdir:
'bizim işlemlerimizde tuttu mu' sorusu için doğru, 'daha çok işlem yapsak da tutar
mıydı' için yanlış."*

**Bu ön-kayıt yalnızca birinci soruyu sorar:** *bizim açtığımız işlemlerde,
girişteki defter derinliği sonucu öngörüyor mu?* Yanlılık bu soru için sorun
değildir. İkinci soruya (**daha iyi aday seçebilir miydik**) genişletmek isteyen
bu bölümü okumadan genişletmesin.

## 2 · Zaten ölçülmüş olan (tekrar edilmiyor)

Maliyet tarafı ölçüldü: bütün eski ölçümler slipajı **%0,02 varsaymıştı**, ölçülen
medyan **%0,0499** (`olcumler.md` → satır 2205). O bulgu bugünkü ölçümlerde
"ölçülen slipaj" senaryosu olarak zaten kullanılıyor. **Burada tekrar edilmez.**

⚠️ Ve bir mekanik not: bot gerçek slipajı **fiile uygulamıyor** — giriş/çıkışta
config'teki sabit varsayımı kullanıyor ([testbot.py:741](testbot.py#L741)).
Yani ölçülen `slipaj_pct` sonucun içinde **aritmetik olarak yok**; ilişki çıkarsa
bilgi taşır, totoloji olmaz.

## 3 · Veri

Beş defterin işlem kaydında `derinlik_giriste` alanı · **2026-08-18 → bugün**

```
testbot   173 / 289   golge  447 / 634   ayna  167 / 261
defter2   183 / 183   defter3  83 /  83          TOPLAM ~1.053 pozisyon
```

Alanlar: `en_iyi` · `vwap` · `slipaj_pct` · `defter_usdt_20` (TEK taraf) ·
`notional` · `yetersiz` (defter 20 seviyede tükendi → slipaj **alt sınırdır**).

**Birim: POZİSYON** — kayıtlar `id` ile birleştirilir, kısmi kâr satırları
ayrı işlem sayılmaz (`CLAUDE.md`). **P&L toplarken süzgeç UYGULANMAZ.**

**Sonuç ölçüsü:** `(Σ sonuc_usdt + Σ funding_usdt) / notional × 100`
— pozisyonun notional'a oranla net getirisi, **fonlama dahil**.

## 4 · Yordayıcılar

**BİRİNCİL (önceden atanmış): `bası = notional / defter_usdt_20`**
— pozisyonumuzun defterin yenen tarafına oranı. Seçildi çünkü **doğrudan
kontrol edilebilir** (boyutlandırma ile) ve bugün bulunan *"kazananlar küçük
pozisyon alıyor"* olgusuyla akraba.

**İkincil, önceden ilan edilmiş (keşifsel):** `slipaj_pct` · `defter_usdt_20`
(mutlak derinlik) · `yetersiz` (bayrak).

Bantlar: `bası`ın **çeyrekleri** (veriden hesaplanır, ölçütten önce sabitlenir).

## 5 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

| # | ölçüt | eşik |
|---|---|---|
| **O1** | üst çeyrek − alt çeyrek | ≤ **−0,3 puan** **ve** gün-kümeli t ≤ **−2,5** |
| **O2** | monotonluk (4 çeyrek) | Spearman ρ ≤ **−0,75** |
| **O3** | 🔴 **BELİRLEYİCİ** karıştırıcı | `kaldirac` bantları **ve** defter kimliği içinde etki **≥%60 hücrede aynı işaretle** (N≥30) |
| **O4** | defterler arası tutarlılık | 5 defterin **≥3'ünde** aynı işaret (N≥30) |
| **O5** | şans | `bası` gün içinde karıştırılır × 2000 → **p ≤ 0,05** |

**O3 DÜŞERSE HÜKÜM DÜŞER.** `kaldirac` bu projede oynaklığın vekilidir (bot
kaldıracı stop genişliğinden türetiyor); etki oynaklığın kılığıysa yeni bilgi yoktur.

**GEÇTİ** = O1+O2+O3+O5 · **ZAYIF** = O1+O3, biri düştü · aksi **DÜŞTÜ**.

⚠️ **KÜME SAYISI AZ.** Pencere ~12 gün → gün-kümeli t **zayıftır**. Bu yüzden
**sembol-kümeli** t de raporlanır (ikisi de önceden ilan edildi, sonradan seçim yok).
Çelişirlerse ikisi de yazılır.

**Ek zorunlu rapor:** çeyreklerin `kaldirac` · `chg24_giriste` · stop-olma oranı
dağılımı (hücreler oynaklıkta ayrışıyor mu) · `yetersiz=True` payı · yön kırılımı ·
defter başına N.

## 6 · BEKLENTİ — sonuç görülmeden yazıldı

**O1'in geçmesine ~%40, O3'ü de geçmesine ~%25 veriyorum.**

- **Lehine:** ince defter → kötü dolum, daha kolay oynatılabilir fiyat; ayrıca
  bugün ölçülen *"kazananlar küçük pozisyon alıyor"* olgusu aynı yöne bakıyor.
- **Aleyhine:** `defter_usdt_20` büyük ölçüde bir **likidite ölçüsüdür** ve likidite
  hacim/mcap'in vekilidir — bu projede *"her yeni aday erken fiyat hareketinin
  başka bir ifadesi çıkıyor"* kuralı **beş kez** doğrulandı. En olası ölüm O3'te.

**Yön tahmini:** kalın defter → daha iyi sonuç bekliyorum. Ama karşı ihtimali de
yazıyorum: ince defterde hareket **daha büyük** olur, bu da kazananları
büyütebilir — işaret ters çıkarsa **aynen raporlanır**.

## 7 · Dokunulmayanlar

Bot · state · defterler · zamanlanmış görevler: **hiçbiri**. Salt-okuma.
Betik: `scratchpad/defter_derinligi.py` (bu commit'ten SONRA yazılır).
