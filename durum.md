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
| NÖTR LONG | açık | ölçümle gerekçelendirilmedi (eşik notunda yazılı) |
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

**3. `golge.py`'nin `kaydet`'i hâlâ atomik değil** — 2026-08-11'de defteri 314 $
saptıran çift kaydın kök nedeni. `ayna.py` ve `izleyici.py` ilk günden atomik yazıyor;
aynı desen kopyalanacak. Onarım önerildi, uygulanmadı.

**4. Git geçmişi temizliği** — ilk push'tan önce zorunlu (geçmişte ~920 MB veri).
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
