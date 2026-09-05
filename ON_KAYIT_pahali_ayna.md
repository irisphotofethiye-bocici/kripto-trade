# ÖN-KAYIT — UCUZ yerine PAHALI: fiyat seviyesinin işareti rejimle dönüyor mu?

**Yazılma tarihi:** 2026-09-05 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-05): *"ma50 ucuz yerine pahalı olsa ne olur"*

---

## 1 · Soru neden meşru — kodun kendi öngörüsü

`kripto-config.json → _ma50_kapisi_not` (2026-08-11):

> *"Fiyat seviyesi bir COIN-TIPI vekilidir (ucuz = yüksek arz/yeni/spekülatif).
> **Rejim değişince ilişki DÖNEBİLİR — boğada ucuz coinler öne geçebilir.**"*

Kullanıcının sorusu tam olarak bu öngörüyü sınıyor. Ayrıca bu oturumda ölçüldü:
BOĞA penceresinde ucuz coinleri short'lamak (`K_dar` **−0,790**) geniş evrenden
(`K_geniş` **−0,771**) **daha kötüydü** — yani ters yön için zayıf bir işaret var.

## 2 · 🔴 EŞİK UYDURULMADI — ve yolda bir olgu çıktı

Orijinal kapı `fiyat ≤ $0,07`, gerekçesi config'te *"dağılımın %20'lik dilimi"*.
**Koşumdan önce, sonuç değişkenine dokunmadan** yeniden hesaplandı
(`scratchpad/pahali_kapsam.py`, 566 sembol · N=208.580):

```
2 YIL       %10 $0,0111 · %20 $0,0318 · %50 $0,2236 · %80 $2,3610 · %90 $16,04
BOGA pen.   %10 $0,0078 · %20 $0,0189 · %50 $0,1289 · %80 $4,2460
```

🔴 **`$0,07` bu evrende %20 dilimi DEĞİL** — gerçek %20 dilimi **$0,0318**.
Yani kapı, kayıtlı gerekçesinden **daha gevşek** çalışıyor (~%28-30 dilimi).
Config'in *"ham fiyat eşiği zamanla kayar"* uyarısı **doğrulanmış** durumda.
Bu bir **olgu**, bu ön-kaydın hipotezi değil; ayrıca raporlanır.

**AYNA EŞİĞİ = `$2,3610`** — 2 yıllık dağılımın **%80 dilimi**, yani orijinalin
simetriği. **Tarama yok, tek değer, şimdi sabitlendi.**
`ma50_mesafe ≥ %3,72` **değişmez** (o da %80 dilimiydi).

**Kapsam (önceden sayıldı):** BOĞA penceresinde ayna kapısı **237 bağımsız olay ·
13 gün · 72 sembol** (ucuz kapısı: 580 / 13 / 253).

## 3 · 🔴 ÇOKLU BAKIŞ SORUNU — ve tasarımın buna cevabı

Bu, 08-21…09-02 penceresine **kaçıncı bakış** olduğu sayılmalı: stop genişliği,
rejim, MA50 kapısı, A+B holdout… Aynı 13 güne tekrar tekrar bakmak **sahte bulgu
üretir.**

**Bu yüzden birincil sınama o pencere DEĞİL:**

| aşama | veri | rol |
|---|---|---|
| **BİRİNCİL** | **2 yıllık rejim kırılımı** (BOĞA 77 gün · NÖTR 554 · AYI 84) | hipotezin sınandığı yer |
| **DOĞRULAMA** | taze BOĞA penceresi (13 gün) | yalnız **teyit**, keşif değil |

2 yıllık BOĞA dilimi 13 günlük pencereden **büyük ve büyük ölçüde bağımsızdır.**

## 4 · EVREN, KOLLAR, MEKANİK

| kol | tanım |
|---|---|
| **UCUZ** | `fiyat ≤ $0,07` **ve** `ma50_mesafe ≥ %3,72` → SHORT *(mevcut kapı)* |
| **PAHALI** | `fiyat ≥ $2,3610` **ve** `ma50_mesafe ≥ %3,72` → SHORT *(ayna)* |

Aynı mekanik: **A-stop · sabit %10 hedef · 72s · maliyet %0,13 · fonlama dahil ·
giriş ertesi barın açılışı · `asgari_stop %2` · 24 saat soğuma.**
Mekanik `ileri_rr`'den **çağrılır**. Rejim `ileri_rr.btc_rejim()` (BTC mumundan).
Veri: `klines_1h_uzun`+`taze_1h`, `funding_gecmis`+`taze_funding`, **bellekte**.

**Ölçü: `net%` birincil** (MA50 ön-kaydıyla aynı gerekçe: kollar aynı mekaniği
kullanıyor, manipüle edilen değişken **kapı**). `R` her zaman yazılır.

## 5 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

Birincil hücre: **2 yıllık BOĞA dilimi** · `PAHALI − UCUZ` · `net%`.

| # | ölçüt | eşik |
|---|---|---|
| **K1** 🔴 | BOĞA'da `PAHALI − UCUZ` | **> 0** · gün-kümeli t ≥ **+2,0** |
| **K2** | taze BOĞA penceresinde **aynı işaret** | evet |
| **K3** | güç: `\|fark\| ≥ MDE` | evet, aksi **"göremiyoruz"** |

**GEÇTİ** = K1+K2+K3 · aksi **DÜŞTÜ**.

### 🔴 K4 YOK — ve bunun sebebi bugün öğrenildi

`ON_KAYIT_boga_holdout.md`'de K4'ü, **bilgisiz kalacağını kendi ön-kaydımda
öngördüğüm** bir alt küme üzerine kurmuştum; gürültü düzeyindeki işaret
tesadüfen negatif çıktı ve **üç ölçütü geçmiş bir hükmü batırdı.**
Ders uygulanıyor: **öngörülen gürültü geçme ölçütü yapılmaz.**

**Rejim tersliği (NÖTR/AYI'da işaretin dönmesi) bu yüzden ÖLÇÜT DEĞİL,
YORUM KURALIDIR:**

| gözlem | yorum (önceden sabit) |
|---|---|
| BOĞA'da pahalı önde **ve** NÖTR/AYI'da ucuz önde | **rejim tersliği gerçek** — config'in öngörüsü doğru |
| pahalı **her rejimde** önde | terslik yok; kapı baştan yanlış tarafa kurulmuş olabilir |
| BOĞA'da fark yok | fiyat seviyesi bu rejimde bilgi taşımıyor |

## 6 · ÇOKLU KARŞILAŞTIRMA

**Birincil: 1** (tek hücre, tek yön, tek ölçü). Rejim kırılımı **yorum** içindir.
İkincil ve hüküm taşımaz: `R` · stop genişliği · dilim kırılımları ·
mutlak kârlılık. **Eşik taraması YASAK** — `$2,3610` ve `%3,72` bu belgede
sabitlendi, oynatılmayacak.

## 7 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%35 veriyorum.** 2 yıllık BOĞA dilimi yalnız **77 gün** ve
bu oturumda o dilim tekrar tekrar güçsüz çıktı.

**Yönlü tahminler (tutmazsa aynen raporlanır):**

1. **NÖTR/AYI'da UCUZ önde olacak** — orijinal yön avının bulgusu (fiyat
   log10 +1,57) yeniden üretilmeli. Üretilemezse o bulgu da şüpheli demektir.
2. **BOĞA'da işaret dönecek (pahalı önde)** ama **fark küçük** ve muhtemelen
   MDE'nin altında.
3. **İki kol da BOĞA'da MUTLAK olarak negatif** kalacak — boğada short
   kaybettirir; hangi coini seçtiğin bunu değiştirmez.
4. **Pahalı kolun stop genişliği belirgin DAR** olacak (pahalı coinler daha az
   oynak) → `asgari_stop %2` elemesi pahalı kolu **daha çok** eleyecek.

## 8 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
Veri indirme yok (indirilen zaten var). Hiçbir arşive yazılmaz.
Betik: `scratchpad/pahali_ayna.py` (**bu commit'ten SONRA**).
