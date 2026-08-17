# Durum

**Son güncelleme: 2026-08-17.** Rakamlar `testbot_state.json` ve defter dosyalarından
okundu, hesaplanmadı.

> Eski `memory/kripto-proje-durumu.md` **güncel değil** (son yazım 2026-08-03; hâlâ
> "Faz 4" ve 1000 $'lık testbot anlatıyor). Tarihsel kayıt olarak duruyor, güncel
> durum için bu dosya esas.

---

## Bot

| | |
|---|---|
| Durum | **AKTIF** · kâğıt üstünde (gerçek emir kodu yok) |
| Kasa (realize) | 9.980,92 $ |
| Etkin kasa (realize + açık) | **10.159,03 $** |
| Zirve | 10.841,02 $ |
| Açık pozisyon | 7 — CAP · HUMA · BOME · COW · ONT · ZEREBRO · RVN |
| Kümülatif fonlama | **−488,35 $** |
| Kümülatif giriş ücreti | −168,55 $ |
| Defter | 148 kayıt · sonraki id 106 |

**Yayın çıpası: 2026-08-11 12:48:31.** Panel bu tarihten sonrasını gösterir; 23 Temmuz
dönemi kasa sıfırlamasıyla kapatıldı (delta +1.005,94 $).

**Süre sınırı yok** (`sure_gun = 0`). Koruma **düşüş freni**: zirveden %25 geri
çekilirse yeni giriş durur, açık pozisyonlar yönetilmeye devam eder.

## Dört defter

| defter | kasa | açık |
|---|---|---|
| `testbot` | 9.980,92 | 7 |
| `golge` | 8.242,47 | 1 |
| `benim` | 10.089,99 | 0 |
| `ayna` | 9.824,38 | 4 |

## Açık kapılar

| kapı | ayar | not |
|---|---|---|
| A+B (funding ≤ −0,05 · oi24 ≥ %10 → SHORT) | **açık** | **ASKIDA** — kanıtlanamadı, çürütülmedi |
| MA50+ucuz (fiyat ≤ $0,07 · MA50 ≥ %3,72) | **açık** | **REDDEDİLDİ** ama kullanıcı kararıyla açık (08-12) |
| A+B sabit %10 hedef | açık | kısmi kâr %40 payla, trailing kapalı |
| 1,5R kısmi ezmesi | **açık** | ⚠️ ölçüm "kaldır" dedi, **kullanıcı KALSIN dedi** (08-12) — aşağıda |
| NÖTR LONG | açık | **ölçüm bunu desteklemiyor** — kaynak `fikir-defteri.md` s.1177: *"Ölçüm bunu desteklemiyor — kayda geçer."* 30 LONG hücresinin hiçbiri pozitif değil (s.1101) |
| Gölge LONG pump | açık | gölgede test, pencere dolmadı |
| NÖTR fade | **kapalı** | açıldığı gün ölçülüp kapatıldı |
| R/R kapısı | **kapalı** | ayırt etmiyordu |

## Zamanlı görevler

| görev | sıklık |
|---|---|
| KriptoTestBot | 7,5 dk · `ExecutionTimeLimit` **PT20M** |
| KriptoRadar | 15 dk |
| KriptoNobetci | 5 dk |
| KriptoIzleyici | 5 dk |
| KriptoPiyasa | günlük |

Bildirim: yalnız **giriş** olayı Telegram'a gider (`bildirim.olaylar = ["giris"]`).

---

## Bekleyen kararlar

> **ÖNCE BUNU OKU — 2026-08-12'de verilmiş bir karar var** (`fikir-defteri.md` s.2812).
> Ölçüm `MA50+ucuz`'u kapatmayı öneriyordu (2 yıl, üç rejim, 21.830 olay, t=−4,05).
> **Kullanıcı iki kapıyı da açık bırakmayı seçti.** Bilinçli bir karardı ve defterde
> *"kayda geçiyor ki pencere dolduğunda 'gözden kaçmış' sanılmasın"* diye yazılı.
> Gerekçe: o test bir **yeniden üretim** — medyan stop %1,3, canlıda %3,4. Ölçüm
> "kural geniş uygulanınca negatif" diyor, "canlı kapı negatif" demiyor.
> **Hakem canlı pencere:** hedef 138 işlem · 12 Ağustos'tan beri **84 pozisyon kapandı**.

**1. A+B kapısı — nihai karar açık.** İki yıllık **fonlamalı** ölçüm "kapat" diyor
(kontrol sinyali geçti). Fonlamasız 2 yıllık ölçüm ise "kanıtlanamadı ama çürütülmedi"
diyordu (küme-dayanıklı t=+1,51). Canlı 16 işlemlik örnek "kapatmak %1,23 daha kötü
olurdu" diyor. Seçenekler: kapat (`ab_kapisi_acik: 0`) · fonlama-taban filtresi ekle
(ölçülebilir, veri elde) · pencere dolana kadar açık bırak.

**2. `MA50+ucuz` — çürütüldü ama açık, bilerek.** İki kapı **aynı statüde değil**:
A+B *askıda* (kanıtlanamadı, çürütülmedi), MA50+ucuz *reddedildi* (t=−4,05, üç rejimde
negatif). Aynı torbaya konmamalı. Fonlama yükü bu kapı için hiç hesaplanmadı — A+B'yi
bitiren hesap burada yapılmadı.

**3. 1,5R kısmi ezmesi — ölçüm "kaldır" dedi, kullanıcı "kalsın" dedi.** Karar
verilmiş, iş bitmiş; burada duruyor ki sonradan "gözden kaçmış" sanılmasın.

`kismi_pay = 0.40` ayarı fiilen çalışmıyor: [testbot.py:933](testbot.py#L933) her
turda yapısal TP1 ile 1,5×risk'ten **hangisi yakınsa** onu seçiyor (2026-07-04'ten
kalma). Ayrışma sınırı stop < %2,67; `asgari_stop_pct = %2,0` olduğu için bu dar bir
aralık değil — canlı girişlerin **%30'u** bu dilimde. Canlı kanıt: UMA'da stop %0,96
→ 1,5R = %1,43, %40 ayarını ezdi, yarısı **−%1,4'te** satıldı.

**Kullanıcı gerekçesi:** stop dar olduğunda kâr alma erken tetiklenir ve bu istenen
davranış. **Bedeli kayda geçti:** dar-stop diliminde işlem başına −0,016 sermaye,
`t_küme` −0,10 — yani gürültüden ayrışmıyor. Kanıt *"zararlı"* demiyor,
*"bedava değil"* diyor.

Geri dönmek gerekirse tek satır: `tp1_efektif_hesapla` çağrısını
`cikis_modu == "sabit_hedef"` pozisyonlarda atla. **`kismi_kar_r = 0` YAPMA** —
neden olmadığı `CLAUDE.md`'de yazılı (TP1 anında tetikleniyor).

### ⭐ Üç karar tek hakeme bağlı — ayrı ayrı tartışılmasın

Yukarıdaki maddelerin **1, 2, 3'ü ve sabit %10 hedef** birbirinden bağımsız görünüyor.
Değil. Üçünün savunması **aynı tek argümana** yaslanıyor:

> *"O ölçüm bir yeniden üretim; popülasyonu canlıdan uzak — medyan stop %1,3,
> canlıda %3,4. Yani 'kural geniş uygulanınca negatif' diyor, 'canlı kapı negatif'
> demiyor."*

| ayar | ölçüm ne dedi | savunma |
|---|---|---|
| MA50+ucuz | −0,079 · t=−4,05 · üç rejimde negatif | popülasyon itirazı |
| Sabit %10 hedef | referans çizgisi −0,079 (s.2671) | **aynı koşturmadan** geliyor, aynı itiraz |
| 1,5R kısmi ezmesi | mevcut −0,011 vs kısmi yok +0,038 | kısmen — ama `kismi_15r.py` evreni canlıya **daraltılmıştı** (stop medyanı %3,27), yani burada metodolojik itiraz **zayıf**, karar tercihe dayanıyor |

**Hakem de aynı: canlı pencere.** Hedef 138 işlem · **84 kapandı (%61)** · kalan **54**.

**Sonuç: tek bir çıktı üç kararı birden çözer.** Pencere eksi kapanırsa üç savunma
birden düşer ve üç ayar birlikte gözden geçirilir. Artı kapanırsa popülasyon itirazı
doğrulanmış olur. **Pencere dolduğunda bunları ayrı ayrı tartışma** — aynı sorunun
üç yüzü.

**Aynı pencereye bağlı DÖRDÜNCÜ iş — ve defterde "ilk iş" diye yazılı:**
**A+B'nin stop mesafesi yeniden ölçülecek.** Ölü sinyal taraması A+B'nin ham
kenarının **%65'ini kendi A-stopumuzun yediğini** buldu (+6,10 → +2,14); MA50+ucuz'da
aynı kayıp **%0**. Defterin sözü: *"Pencere kuralı gereği ŞİMDİ UYGULANMAZ
(138 işlem / 30 gün dolana kadar parametre donuk). Pencere sonrası ilk iş bu."*
Ayrıntı ve tablo `olcumler.md` → *"A+B'nin ham kenarının %65'i"*.

Uyarı: 1,5R'nin savunması diğer ikisinden **zayıf.** Onu popülasyon itirazına
yaslamak yanlış olur; o karar açıkça bir tercihti ve bedeli kayıtlı (−0,016/işlem).

**4. `golge.py`'nin `kaydet`'i hâlâ atomik değil** — 2026-08-11'de defteri 314 $
saptıran çift kaydın kök nedeni. `ayna.py` ve `izleyici.py` ilk günden atomik yazıyor;
aynı desen kopyalanacak. Onarım önerildi, uygulanmadı.

**5. Git geçmişi temizliği** — ilk push'tan önce zorunlu (geçmişte ~920 MB veri).
Depo bugüne kadar hiç push edilmedi.

## Zamana bağlı — ~27 Ağustos

**`d_taker` ölçümü.** İzleyici 2026-08-13 akşamından beri dakika çözünürlüklü
hacim/agresör topluyor (`taker_15`, `taker_60`, `d_taker`, `hacim_x`). Bu veri
**geriye dönük üretilemez**, canlı birikmeli. Birkaç yüz satır olunca ön-kayıtlı
ölçüm yapılacak.

Önem: bugüne kadar ölçülen her şey **seviye** idi ve "erken fiyat hareketinin başka
bir ifadesi" çıktı. `d_taker` **değişim** ölçen ilk sütun.

## Canlıya geçmeden

Tam liste: `memory/canliya-gecis-kontrol-listesi.md` — kullanıcı hatırlatılmasını
açıkça istedi. Beş madde: `d_taker` ölçümü · fonlamanın canlı doğrulaması · A+B
kararı · MA50 fonlama yükü · gölge atomik kayıt.

---

## Bilinen zayıflık

**İnternet/uyku kesintisi.** 13–16 Ağustos arasında toplam **~10 saat** veri akmadı
(en uzunu 124 dk). Makine uyandığında:

- **Dakika verisi geri geliyor** — izleyici son gördüğü bardan devam ediyor, sapma
  1–2 dk (yalnız oluşmakta olan dakika)
- **Bot stop/TP'yi doğru yakalıyor** — geçmiş mumları geri oynatıp stop fiyatından
  kapatıyor
- **Radar kareleri geri GELMİYOR** — noktasal veri (score, funding, oi, comp).
  Kabaca %7–14 kare kaybı

`kesilen_tur` sayacı **9** — bitmeden öldürülen tur sayısı. Tur süresi 08-14'ten beri
equity satırında ölçülüyor (`sure_sn`, `sure_yonet`, `sure_giris`, `verisiz_poz`).

**Ağ yavaşken tur süresi:** ortalama 191 sn, en uzun 521 sn. **Ağ normalken:** 15–25 sn.
Yani yavaşlık tamamen dış kaynaklı.
