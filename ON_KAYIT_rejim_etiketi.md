# ÖN-KAYIT — Rejim etiketi yön bilgisi taşıyor mu?

**Yazılma tarihi:** 2026-09-04 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** `durum.md` → *İKİ REJİM, TEK PİYASA* ve *BOYUTLANDIRMA KOLU KAPANDI*
→ sıradaki iş.

---

## 1 · Soru — ve neden en büyük kaldıraç

Etiket botun **yönünü** belirliyor: `BOGA` → LONG (geniş), `NOTR`/`AYI` → SHORT
(kapılar üzerinden). Ölçüldü: 24 Ağustos'tan beri BOĞA'da SHORT adayı **sıfır**.

Ve ölçüldü: **alt para evreni iki rejimde de aşağı sürükleniyordu**
(`NOTR` LONG yönünde −0,592% · `BOGA` −0,816%, H=4sa). Yani etiket yönü
çevirdi, piyasa çevrilmedi.

🔴 **Ama o ölçüm 30 günlük TEK epizottu.** Bu ön-kayıt aynı soruyu **2 yıl ve
çok epizot** üzerinde soruyor: *etiket genel olarak yön bilgisi taşıyor mu,
yoksa bu epizot mu istisnaydı?*

## 2 · VERİ ve ÜRETİM

**Rejim serisi:** `scratchpad/rejim_gecis_sayim.py` ile BTC 1 saatlik mumundan
**nedensel** yeniden üretilir (ileriye bakma yok). **Doğrulandı:** bugünkü
yeniden üretim botun canlı etiketiyle birebir uyuşuyor
(`BOGA` · sezon `BOGA` · hava `BOGA` · f10 `TAM_BOGA`).

⚠️ `radar_archive.rejim` alanı **KULLANILMAZ** — tanımı 2026-07-22'de değişti
(`CLAUDE.md`). Seri BTC mumundan üretilir, bu kırılımdan etkilenmez.

**Pencere:** 2024-12-23…2026-08-25 · **611 gün**
`NOTR` 313 (%51,2) · `AYI` 204 (%33,4) · `BOGA` 94 (%15,4)
Geçişler: `NOTR→BOGA` **7** · `BOGA→NOTR` 6 · `NOTR→AYI` 15 · `AYI→NOTR` 15

🔴 **Geçiş sayısı 7 — hüküm GEÇİŞ düzeyinde VERİLMEZ**, gün düzeyinde verilir.
Geçiş analizi **betimleyicidir**.

**Evren:** `scratchpad/klines_1h_uzun/` (566 sembol, 2 yıl).
⚠️ 2026-08-25'te bitiyor → **güncel BOĞA epizodunun yalnız 5 günü** kapsanıyor.
Kalan kısmı zaten ayrı ölçüldü (`olcumler.md` → *BOĞA'da LONG*) ve **oradan
işaret edilir, yeniden hesaplanmaz.**

## 3 · BİRİM ve ÖLÇÜLEN BÜYÜKLÜK

🔴 **BİRİM = GÜN.** Aynı gün 566 sembol bağımsız değil (hepsi birlikte hareket
eder). Her gün için **semboller arası MEDYAN** ileri getiri tek gözlemdir.

```
gunluk_alt_getiri(d) = medyan_s [ (kapanis_s(d+1) - kapanis_s(d)) / kapanis_s(d) * 100 ]
```

Yön **LONG**. Medyan seçildi (ortalama değil): alt paralarda uç değerler
ortalamayı tek sembolle taşıyabilir.

## 4 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

🔴 **BİRİNCİL:** `BOGA` günlerinin alt getirisi, `NOTR`+`AYI` günlerinden
**yüksek mi?** (Botun yön kuralı tam olarak bunu varsayıyor.)

| # | ölçüt | eşik |
|---|---|---|
| **K1** | `ort(BOGA) − ort(NOTR∪AYI)` | **> 0** ve iki-örneklemli t ≥ **+2,0** |
| **K2** | `BOGA` günlerinin kendi ortalaması | **> 0** (LONG açmak savunulabilir mi) |
| **K3** | `NOTR∪AYI` günlerinin ortalaması | **< 0** (SHORT açmak savunulabilir mi) |

**GEÇTİ** = K1 · **KISMİ** = K1 düştü ama K2 ve K3 tuttu · aksi **DÜŞTÜ**.

🔴 **BELİRLEYİCİ KONTROL (K4) — etiket fiyatın kılığı mı?**
`btc_chg24` (BTC'nin önceki gün getirisi) ve **SMA20'ye uzaklık** sabitlenince
etiket **ek bilgi taşıyor mu?** Yöntem: günleri `btc_chg24` çeyreklerine böl,
her çeyrek **içinde** `BOGA` vs diğer farkını hesapla.
**Fark çeyrek içinde kayboluyorsa etiket fiyatın kılığıdır** ve K1 geçse bile
*"yeni bilgi"* sayılmaz.

⚠️ **Çoklu karşılaştırma:** 1 birincil (K1). K2/K3 aynı ölçümün iki yüzü.
K4 kontrol. Ufuk **tek**: 24 saat. Epizot kırılımı **betimleyicidir**.

## 5 · 🔴 EPİZOT KIRILIMI ZORUNLU — kullanıcı uyarısı

*"11-19'u başka rejim, unutma."* (kullanıcı, 2026-09-04)

**Havuz hükmü tek başına raporlanmaz.** Her `BOGA` epizodu ve her `NOTR`
epizodu **ayrı satır** olarak yazılır (başlangıç · bitiş · gün sayısı ·
ortalama alt getiri). Gerekçe: 30 günlük ölçümde `NOTR` ve `BOGA` **zıt
davranmıştı**; havuzda erimemeli.

**Ayrıca zorunlu:** güncel epizodun (2026-08-21→) havuzun **kaçıncı
yüzdeliğinde** olduğu — istisna mı, tipik mi?

## 6 · GECİKME ÖLÇÜMÜ — betimleyici, N=7

Her `NOTR→BOGA` geçişi için: etiket dönmeden **önceki 7 günde** BTC ne kadar
hareket etmişti? Bu, *"etiket geç kalıyor"* iddiasının **sayısıdır**.
N=7 → hüküm yok, **sayı olduğu gibi yazılır**.

## 7 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%60 veriyorum.** `BOGA` tanımı gereği BTC'nin SMA20
üstünde ve yükseliyor olması demek; altlar BTC'yi takip eder. Yani etiketin
**önemsiz anlamda** çalışması beklenir.

🔑 **Asıl soru K4.** **K4'ün düşmesine (yani etiketin `btc_chg24` sabitken
ek bilgi TAŞIMAMASINA) ~%65 veriyorum.** Bu projenin kayıtlı dersi:
*"ölçtüğümüz her şey tek banttan türüyor"*.

**Yönlü tahminler (tutmazsa aynen raporlanır):**
1. Güncel BOĞA epizodu (2026-08-21→) havuzun **alt çeyreğinde** kalacak —
   yani istisna olacak, tipik değil.
2. Gecikme ölçümü: geçişten önceki 7 günde BTC ortalama **%10'un üstünde**
   hareket etmiş olacak.
3. `AYI` günlerinin alt getirisi `NOTR`'dan **daha negatif** olacak.

🔴 **Ve şimdiden:** K1 geçse bile bu *"etiket iyi"* demek değildir. Etiket
**geç** olabilir (bölüm 6) ve **yapışkan** olabilir; ikisi de ortalama
doğruluğu bozmadan para kaybettirir. Kod değişikliği önerisi için
**portföy aşaması** gerekir.

## 8 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
Salt-okuma, ücretli çağrı yok. Betik: `scratchpad/rejim_yon_bilgisi.py`
(bu commit'ten SONRA).
