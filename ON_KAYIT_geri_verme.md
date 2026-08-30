# ÖN-KAYIT — "artıya geçip geri verme" botun kusuru mu, piyasanın özelliği mi?

**Yazılma tarihi:** 2026-08-30 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** 2026-08-30 tersine mühendislik incelemesinin bıraktığı **aday**.

---

## 1 · Aday nereden geldi

Kazananların incelenmesinde şu görüldü (`olcumler.md` → TERSİNE MÜHENDİSLİK):

```
tepe >= %1 : %39 kaybetti   ·  tepe >= %2 : %32  ·  >= %3 : %18  ·  >= %5 : %7
```

Gauss rastgele yürüyüş boş hipotezine karşı (pozisyonun **kendi** ATR'si, süresi,
stopu ve 2×ATR iz-süren stopuyla) fark **+20,3 / +20,0 / +10,3 / −0,3 puan** çıktı.

🔴 **Ama o boş hipotez YANLIŞ olabilir.** Kripto kısa ufukta ortalamaya döner ve
pompalanmış altlarda bu belgelenmiş bir olgudur. *"Gauss yürüyüşten kötü"*
**piyasanın özelliği** olabilir — botun kusuru değil. O yüzden hüküm yazılmadı.

**Bu ön-kayıt doğru boş hipotezi kuruyor.**

## 2 · DOĞRU BOŞ HİPOTEZ — eşleştirilmiş rastgele giriş

Her gerçek pozisyon için, **aynı sembolde · aynı takvim penceresinde · aynı yönde**
rastgele giriş anları üretilir ve **birebir aynı mekanik** uygulanır.

```
sabit tutulanlar : sembol · donem · yon · mekanik (stop/TP1/iz-suren/TP2/zaman stopu) · maliyet
degisen tek sey  : GIRIS ANI  = botun sinyali
```

Böylece fark kalırsa, kalan tek açıklama **botun giriş zamanlaması**dır.

**Kontrol üretimi:** her gerçek pozisyon için **K = 20** rastgele giriş anı,
gerçek girişin **±3 gün**i içinde, aynı sembol ve aynı yön. Mekanik ayakta değilse
(asgari stop %2 sağlanmıyor, yapı hesaplanamıyor) o çekiliş atılır.

## 3 · Veri ve mekanik

**Fiyat:** `scratchpad/perp_seri/*_kline.json` (taze, 08-30'a kadar) **öncelikli**,
yoksa `scratchpad/klines_1h_uzun/` (08-25'e kadar). Ölçüldü: birleşik kapsam
**214 sembol · 1.463 pozisyon (%100)**. Kaynak başına kapsam raporlanır.

**Mekanik — mevcut betiklerden BİREBİR yeniden kullanılır** (`scratchpad/stop_mu_sure_mu.py`
ve `skor_mekanik.py` içindeki `seviyeler()` / `oynat()` deseni):
ölçücünün üç adaylı stopu (yapısal / son 10 bar / 1,5×ATR, girişe en yakın) ·
asgari stop %2 · TP1 %40 @1,5R · iz-süren 2,0→1,5→1,0 ATR · TP2 = TP1±1,5R ·
zaman stopu 48 saat · maliyet 2×(taker %0,045 + slipaj %0,02), **iki kolda da aynı**.

⚠️ Fonlama **dışarıda** — ölçülen şey P&L değil, *"tepeye ulaşıp negatif bitme"*
oranı. Fonlama iki kolu da aynı yönde etkiler ve oranı değiştirmez.
⚠️ Bar-içi sıra belirsizliğinde **stop öncelikli** (muhafazakâr), iki kolda da aynı.

## 4 · ÖLÇÜLEN BÜYÜKLÜK

```
GV(X) = P( son <= 0 | tepe >= X% )        X ∈ {1, 2, 3, 5}
fark(X) = GV_gercek(X) - GV_kontrol(X)     [puan]
```

`tepe` = pozisyon ömrü boyunca ulaşılan azami lehte hareket (%), iki kolda da
aynı biçimde hesaplanır.

## 5 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

| # | ölçüt | eşik |
|---|---|---|
| **N1** 🔴 **BİRİNCİL** | `fark(2%)` | ≥ **+5,0 puan** **ve** gün-kümeli t ≥ **+2,5** |
| **N2** | gradyan | `fark` eşikle **azalmalı**: `fark(1) ≥ fark(2) ≥ fark(3)` **ve** `\|fark(5)\| ≤ 5` puan |
| **N3** | yön tutarlılığı | LONG ve SHORT **ayrı ayrı** aynı işaret |
| **N4** | süre kontrolü | gerçek ve kontrol kollarının medyan tutma süreleri **1,5 kat** içinde; değilse güven zayıflar ve **aynen yazılır** |

**GEÇTİ** = N1+N2 · **ZAYIF** = N1, N2 düştü · aksi **DÜŞTÜ**.

**Ek zorunlu rapor:** kol başına N · kaynak kapsamı · `tepe` dağılımı ·
kontrol kolunda elenen çekiliş oranı (asgari stop) · defter kırılımı ·
gerçek/kontrol stop genişliği ve stop-olma oranı (mekanik eşitliği).

⚠️ **Çoklu karşılaştırma:** 4 eşik × 1 birincil. Birincil **önceden atanmıştır**
(`X=2%`); diğer üçü N2'nin parçası, ayrı hüküm taşımaz.

## 6 · BEKLENTİ — sonuç görülmeden yazıldı

**N1'in geçmesine ~%45 veriyorum.** Gauss boş hipotezine karşı fark +20 puandı;
gerçek fiyat serisiyle eşleştirilmiş boş hipotez bunu **belirgin biçimde
küçültecektir** çünkü kripto zaten ortalamaya dönüyor. Tahminim: fark **+3 ile
+10 puan** arasına iner ve eşiği geçip geçmemesi kıl payı olur.

**Yönlü tahmin:** `fark(5%)` sıfıra yakın kalacak (Gauss testinde −0,3'tü) —
yani etki varsa **yalnız küçük kârlarda**. Tutmazsa aynen raporlanır.

🔴 **Ve şunu şimdiden yazıyorum:** N1 geçse bile bunun doğal önerisi *"daha erken
kâr al"* olur ve bu bir **çıkış sıkılaştırmasıdır** — bu projede sıkılaştıran
**29 varyantın 29'u da kalmıştır**. Geçen bir bulgu **kural değil**, kendi
ön-kayıtlı mekanik+portföy ölçümünü hak eden bir **adaydır**.

## 7 · Dokunulmayanlar

Bot · state · defterler · zamanlanmış görevler · config: **hiçbiri.** Salt-okuma.
Betik: `scratchpad/geri_verme.py` (bu commit'ten SONRA yazılır).
