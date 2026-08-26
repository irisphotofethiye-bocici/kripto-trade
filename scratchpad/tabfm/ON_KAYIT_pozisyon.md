# ÖN-KAYIT — TabFM BOTUN KENDİ POZİSYONLARINI AYIRABİLİR Mİ?

**Yazıldı: 2026-08-26, KOŞUMDAN ÖNCE. Ölçütler bundan sonra DEĞİŞTİRİLMEZ.**

Kullanıcı sorusu: *"Botun 19'undan sonra poz aldığı coinleri verip tahmin
yapmasını sağlayabilir miyiz?"*

---

## 🔴 BU BİR HÜKÜM ÖLÇÜMÜ DEĞİL — TEŞHİSTİR

Sonuç ne çıkarsa çıksın **kural yazılmayacak**. Üretebileceği tek şey:
*"ileri zamanda sınamaya değer"* ya da *"değmez"*. Üç sebep:

1. **N=119 pozisyon, 7 gün.** Gün-kümeli hiçbir istatistik güçlü olamaz.
2. **PENCERE SEÇİLMİŞ.** 19 sonrasını *kaybettiğimizi bilerek* seçiyoruz.
   Burada "kurtarırdı" çıkması genellenebilir değildir.
3. **Tek rejim.** Test penceresinin %67'si BOĞA.

Ümit verirse sıradaki adım bota eklemek değil, **ayrı bir defterle ileri
zamanda sınamak** (`defter3` gibi).

---

## VERİ

```
evren    botun KENDI actigi pozisyonlar (kagit uzerinde)
toplam   237 pozisyon  ·  2026-07-23 .. 2026-08-26
test     2026-08-19,20,21,22,24,25,26  ->  119 pozisyon / 7 gun
baglam   her test gunu icin O GUNDEN ONCEKI TUM pozisyonlar
```

⚠️ Pozisyon sayımı **`id` bazlıdır**, kayıt bazlı değil — `TP1_KISMI` satırları
pozisyonu böler (`CLAUDE.md`). P&L toplanırken süzgeç **uygulanmaz**, `id` ile
birleştirilir.

### Neden bu bölme — naif "19 öncesi/sonrası" ölçüldü ve REDDEDİLDİ

```
              BAGLAM (19 oncesi)     TEST (19 sonrasi)
YON           SHORT %92              LONG %76
REJIM         NOTR  %96              BOGA %67
skor ort      45,5                   54,5
```

19 Ağustos rejimin döndüğü gün. Sabit bölmede model **iki ayrı dünyadan**
birini öğrenip diğerini tahmin etmeye çalışırdı; başarısızlığı TabFM hakkında
değil, pencere hakkında bilgi verirdi. Gün-bloklu kayan bağlamda 21 Ağustos
sorulurken bağlamda 19-20 Ağustos'un **aynı rejimdeki** pozisyonları bulunur.

### Girdiler

Aday arşivinin **23 alanı** (pozisyonların %97,5'i giriş saatine ±1 sa içinde
eşleşiyor) + defterin giriş anı alanları: `yon` · `kaldirac`.

### DIŞLANANLAR

| alan | neden |
|---|---|
| `cikis` · `roi_pct` · `r` · `sonuc_usdt` · `tutma_saat` · `sebep` | **sonuç** |
| `funding_usdt` | pozisyon boyunca birikir, giriş anında yok |
| `marjin` · `notional` | `risk_usdt`'nin ölçeklenmiş hâli, bilgi taşımıyor |
| **`derinlik_giriste`** | 🔴 test'te **%100**, bağlamda **%1,7** (18 Ağustos'ta eklendi). Bağlamda görülmeyen alan test'te işe yaramaz |

📌 `derinlik_giriste` (emir defteri derinliği + slipaj) `CLAUDE.md`'nin
*"gerçekten yeni bilgi"* listesindeki **ilk madde**. 08-18'den sonrası tam dolu
→ birkaç hafta sonra **ayrı bir ölçümün** konusu. Burada kullanılamaz.

---

## İKİ ETİKET — ikisi de koşulacak

| | etiket | soru |
|---|---|---|
| **L1** | ham +24s getiri, **yöne göre işaretli** (SHORT'ta ters) | sinyal var mı (mekanikten arınık) |
| **L2** | **gerçek pozisyon net P&L ($)**, `id` ile toplanmış | botu kayıptan kurtarır mıydı |

L1 `CLAUDE.md`'nin *ham → mekanik → portföy* sırasının 1. adımı; L2 doğrudan
kullanıcının sorusu. **Çelişirlerse bu da bulgudur** — *"ölen sinyal değil,
stopumuzdu"* dersi tam orada yaşandı.

---

## ÖLÇÜTLER — koşumdan önce sabit

| # | ölçüt | eşik |
|---|---|---|
| **T1** | **PARA:** model üst yarısı − alt yarısı, gerçek P&L farkı | fark > 0 **ve** 7 günün **≥5**'inde pozitif |
| **T2** | **SİNYAL:** L1 ile gün-kümeli Spearman rho | rho > 0 ve t ≥ 1,5 |
| **T3** | **TABAN:** aynı ikisi botun kendi `skor`'uyla (işaret bağlamdan) | TabFM **her ikisinde de** skoru geçmeli |
| **T4** | **KARIŞTIRICI:** yalnız LONG alt kümesinde (N≈90) T1 işareti | aynı işaret |

**"Sınamaya değer" = T1 + T3 + T4.** T2 destekleyici; düşerse *"mekanik
üzerinden çalışıyor, ham sinyal değil"* diye kaydedilir.

T4 neden: test penceresi %76 LONG. Yön sabitlenmeden ayırma görülürse model
sadece *"LONG kötüydü"* demeyi öğrenmiş olabilir — o bilgi zaten defterde var.

---

## ÇOKLU KARŞILAŞTIRMA

**2 etiket × 1 model = 2 karşılaştırma.** Ufuk (+24s), bölme, eşikler SABİT.
Başka kesme noktası (17, 11) **denenmeyecek**; denenirse hepsi raporlanır.

`n_estimators = 32` — bağlam küçük (118-230 satır), süre ~20 dk, bütçe sorunu
yok. TabFM'in referans varsayılanı.

---

## BEKLENTİM — koşumdan önce

**T1'in düşmesini bekliyorum.** Gerekçe: dünkü ölçümde model ham getiride
gerçekten sıralıyordu ama kazancının çoğu `skor`'un tersine çevrilmiş hâlinde
zaten vardı. Burada bağlam **çok daha küçük** (118-230 satır, dün 800-3400) ve
etiket **mekanikli** — yani daha gürültülü.

**T4'ün düşmesini bekliyorum** (yön sabitlenince ayırma kaybolur).

Yanılırsam, botun kendi pozisyonları üzerinde çalışan bir süzgeç adayımız olur
— ve o **elle kurulabilir** bir şey olabilir.

---

## GEÇMEZSE

TabFM silinmez (kullanıcı kararı: *"birkaç deneme daha yapacağız"*).
Bu ölçüm `olcumler.md`'ye **teşhis** olarak yazılır, hüküm olarak değil.
