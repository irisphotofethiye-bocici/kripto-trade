# Ölçüm Kütüğü

`fikir-defteri.md` 251 kB / 3.908 satır / **287 başlık** — bağlama sığmıyor. Bu dosya
onun **içindekiler sayfası**: *"bunu daha önce ölçtük mü?"* sorusunun tek bakışta
cevabı.

**Kural:** Yeni ölçüm bitince buraya bir satır eklenir. Yalnızca defterde **yazılı**
olan girer; kaydı olmayan betik `kayıt yok` diye işaretlenir, uydurulmaz.

**Hüküm sözlüğü**

| hüküm | anlamı |
|---|---|
| `GEÇTİ` | ön-kayıtlı ölçütü sağladı, sisteme girdi |
| `KALDI` | ölçütü sağlayamadı, uygulanmadı |
| `ÇÜRÜDÜ` | iddia ölçümle yanlışlandı |
| `KARARSIZ` | işaret dönüyor / N yetersiz → kural çıkarılmadı |
| `KISMEN` | çekirdek amaç tuttu, kenarları tutmadı |
| `AÇILDI` | ölçüm sonucu sisteme kapı olarak girdi |
| `KAPATILDI` | ölçüm sonucu mevcut kapı devre dışı bırakıldı |

---

## Kapı kararları — sisteme giren/çıkanlar

| ölçüm | tarih | N | hüküm | betik | defter |
|---|---|---|---|---|---|
| R/R kapısı ayırt ediyor mu? | 08-10 | 7.119 olay | **KAPATILDI** — kazananın %62,8'ini, kaybedenin %61,8'ini kesiyor; geçirdiği grup kestiğinden kötü | `kacan_kazananlar.py` | s.916 |
| A+B kapısı (funding ≤ −0,05 **ve** oi24 ≥ %10 → SHORT) | 08-10 | 206 olay | **AÇILDI** — kesişim +0,375 vs kontrol −0,037 | `oruntu_analiz.py` | s.1025 |
| MA50+ucuz kapısı (fiyat ≤ $0,07 **ve** MA50 mesafesi ≥ %3,72) | 08-10 | 460 olay | **AÇILDI** — +0,84% vs kontrol −0,05% · ⚠️ iki gün sonra 2 yılda **ÇÜRÜTÜLDÜ**, aşağıdaki satıra bak | `yon_avi.py` | s.1478 |
| **MA50+ucuz, 2 yılda yeniden üretim** | 08-12 | 21.830 olay | **ÇÜRÜTÜLDÜ** — −0,079, t=−4,05, **üç rejimde de negatif**. Ama testin popülasyonu canlıdan uzak (medyan stop %1,3 vs canlı %3,4) → "kural geniş uygulanınca negatif" diyor, "canlı kapı negatif" **demiyor** | `ab_funding_2yil.py` | s.2790 |
| NÖTR fade dalı | 08-10 | 1.741 / 3.979 | **KAPATILDI** — açıldığı gün ölçüldü, ölçümün en kötü iki hücresine giriyordu | — | eşik notu |
| A+B'ye sabit %10 hedef | 08-10 | 206 | **GEÇTİ** — +2,01% vs mevcut +1,24% | — | s.1231 · s.1249 |
| **Sabit hedefin `MA50+ucuz`'a genişletilmesi** | 08-11 | 460 | ⚠️ **AÇIK SORU — dayanağı çürütüldü.** Genişletme koda *"ölçümü de %10 hedefle yapıldı (net +0,84%)"* diye gerekçelendirildi ([testbot.py:1179](testbot.py#L1179)); **o +0,84% ertesi gün 2 yılda −0,079 · t=−4,05 ile çürütüldü** (s.2790). 08-10 kararı *"A+B'ye özel"* demişti (s.1249). Pencere sonrası A+B kararıyla **birlikte** ele alınmalı → `durum.md` beşinci iş | — | s.1249 · s.2790 |

## Çıkış kuralları — 29 varyant, 1'i geçti

**SAYIM (2026-08-17'de yapıldı).** Beş ölçüm · içlerinde **29 ayrı varyant**:
5 (çıkış kıyası) + 8 (oynak hedef) + 7 (kısmi: 4 kural + 3 şekil) + 1 (başabaş) +
8 (erken müdahale) = **29.**

**Geçen: 1** — sabit %10 hedef. Ve o **çıkışı gevşetiyordu.** Çıkışı sıkılaştıran
**28 varyantın 28'i de kaldı.**

> ⚠️ *"13 çıkış kuralı denendi"* cümlesi bu projede aylarca tekrarlandı ve
> **dayanağı yoktu.** Gerçek sayım yukarıdadır. `kismi_pay = %40` bu 29'a dahil
> değil — o bir ölçüm değil, 2026-08-11'de kenarın küçüldüğü bilinerek kabul edilmiş
> bir takas.

| ölçüm | tarih | N | hüküm | betik | defter |
|---|---|---|---|---|---|
| **Beş çıkış kuralı kıyası** (5 varyant) | 08-10 | 206 A+B girişi | **GEÇTİ** — sabit %10 hedef +2,01% vs mevcut +1,24%, iki yarıda da. Bedeli: kazanma oranı %66 → %50 | — | s.1231 |
| 1,5R kısmi kâr lehimize mi? | 08-12 | 13.951 · **karar veren alt küme 4.195** (dar stop, canlı girişlerin %30'u) | **KALDI** — mevcut (yakın olanı seç) −0,011 · niyet edilen sabit %40 +0,005 · kısmi yok **+0,038**. Ölçüt 1 düştü, iki zaman yarısında da mevcut daha kötü | `kismi_15r.py` | s.2951 · s.3001 · s.3031 |
| Hedefi oynaklığa ölçekleme (8 varyant) | 08-12 | 21.830 olay / 312 sembol / 2 yıl | **KALDI** — 8'in 8'i de; hiçbiri sabit %10'u yenemedi (2×ATR −0,088 … 6×ATR −0,091) | `oynak_hedef.py` | s.2587 · s.2629 |
| TP1'de stopu başabaşa çekme | 08-12 | 11–12 Ağu pozisyonları | **KALDI** — kısmi sonrası başabaş +0,274 → +0,261 | `babas_stop_11_12.py` | eşik notu |
| Erken müdahale (N dk'da artıda değilse kapat) | 08-13 | 44 poz | **KARARSIZ** — durum haber verici ama kural kararsız (+1.170 / −227 / +161 / −222); kural çıkarılmadı | `erken_mudahale.py` | s.3755 · s.3784 |

> **Bu satırın nereden geldiği** (zincir kayıptı, eklendi): hipotez `pnl-tepe-raporu.md`
> §2'de doğdu — *"artıda geçen süre kazananı kaybedenden ayırıyor"* (kazananlar %93,
> kaybedenler %28, N=17). **Ertesi gün tam bu ileri-bakma tuzağı olarak teşhis edildi**
> (s.3757): *"kazanan işlem zaten kazandığı için çoğu zaman artıdadır — bu bir tahmin
> değil, sonucun yeniden ifadesi."* Sonra `erken_mudahale.py` ile **yalnız ilk N dakikaya
> bakarak** doğru biçimde ölçüldü → KARARSIZ. Üç adımlı zincirin kendisi bir yöntem
> dersi: gözlemi ölçüm sanmamak.

> **Kalıp:** *kötü girişte sıkı çıkış kaybı keser, iyi girişte kazancı keser.*
> Defterde sayaç ilerliyor: `oynak_hedef`'te "beşinci kez", `kismi_15r`'de "altıncı kez".

### ⚠️ Geçen tek kural sonradan sarsıldı (s.2671)

Dürüstlük notu: sabit %10 hedef **arşiv ölçümünde +0,41** idi, ama 08-12'deki 2 yıllık
yeniden üretimde referans çizgisi **−0,079 (t=−4,05)** çıktı. *"Örneklem-içi pozitif,
örneklem-dışı negatif"* — LONG hücrelerinde yaşananın aynısı.

**Ama "kapı öldü" denemez:** o popülasyon canlıdan uzak (medyan stop %1,3 vs canlı %3,4)
— MA50+ucuz tartışmasındaki **aynı sınır**, çünkü **aynı koşturmadan** geliyor.

→ Bu, üç ayarı tek hakeme bağlayan yapısal bağın parçası. Tamamı `durum.md`'de
*"Üç karar tek hakeme bağlı"* bölümünde: MA50+ucuz · sabit %10 hedef · (kısmen) 1,5R.
**Pencere dolduğunda üçü ayrı ayrı tartışılmamalı.**

### ⭐ Genel bulgu: kısmi kâr ERKENLİĞİNDE MONOTON (s.3031)

Tek bir kuralın hükmünden daha değerli olan sonuç. `kismi_15r.py`, N=13.951 · 2 yıl:

| kısmi eşiği | tüm olaylar | dar stop | geniş stop |
|---|---|---|---|
| 1,0R | +0,018 | −0,029 | +0,039 |
| 1,5R | +0,041 | −0,011 | +0,064 |
| 2,0R | +0,050 | +0,008 | +0,068 |
| 3,0R | +0,065 | +0,036 | +0,077 |
| **kısmi YOK** | **+0,065** | **+0,038** | **+0,076** |

**Kısmi kâr ne kadar erken alınırsa o kadar kaybettiriyor** — üç sütunda da monoton,
istisna yok. 3,0R "kısmi yok" ile aynı yere geliyor çünkü kısmiye ancak %13 değiyor.

Yeni bir kısmi-kâr/erken-çıkış fikri gelirse **önce bu tabloya bak**: eşiği
aşağı çekmeyi öneren her fikir bu monotonluğa karşı savunma yapmak zorunda.

## Sinyal / gösterge ölçümleri

| ölçüm | tarih | N | hüküm | betik | defter |
|---|---|---|---|---|---|
| Kanal + StochRSI (Acceleration Bands) | 08-11 | 570 sembol / ~60 gün / 1h · N=5.488 | **KALDI** — 20+6 hücre, hepsi negatif. Bota da gölgeye de alınmadı (*"gölge defter aday havuzu değil, ölçüm bütçesidir"*). **Ama ham sinyalin 4 barlık gerçek kenarı var** (+0,243 vs kontrol +0,035, t=+3,84) — A-stop onu +0,051'e indiriyor. Kenarın tamamı **tek bir 10 günlük pencereden** (Q1 +0,579 t=+7,91; BTC'nin %6 düştüğü hafta), Q2–Q4 ≈ 0 | `kanal_stoch.py` · `kanal_ham.py` · `kanal_stopsuz.py` | **`kanal-stochrsi-analizi.md`** (44 KB, 14 bölüm) · s.1892 · s.1966 |
| Scalp varyantı + rejim iddiası | 08-11 | — | **KALDI** — 6 rejim bölmesinin 6'sı da | `kanal_scalp.py` | s.2048 · s.2131 |
| "Sinyalde bilgi yok" iddiası | 08-11 | — | **ÇÜRÜDÜ** (kendi iddiam) — karar değişmedi ama gerekçe değişti | — | s.2140 |
| Hareket öncesi örüntü | 08-10 | — | **ÇÜRÜDÜ** — örüntü tanımlayıcı, tahmin edici değil | `oncesi_oruntu.py` · `oncesi_short.py` | s.1373 · s.1334 |
| Yükselenlerin ortak örüntüsü | 08-10 | — | **ÇÜRÜDÜ** — işaret olarak ters | `yukselen_oruntu.py` | s.1288 · s.823 |
| Ölü sinyallerin kaçı canlıydı? | 08-11 | 6.790 olay (ham: stop/hedef/maliyet yok) | **2 hücre bulundu, ikisi de LONG** — A-stopları %0,98, `asgari_stop_pct = %2,0` kapısı onları zaten tümden reddediyordu. Yani sinyal reddedildi çünkü **stop kuralımız sinyale uygun değildi.** Adaylar 2 yıllık veride çöktü (s.2284) | `olu_sinyal_tarama.py` | s.2210 · s.2259 |
| Fikir 1 adayları örneklem dışı | 08-11 | 2 yıl | **ÇÜRÜDÜ** — örneklem dışında çöktü | `long_2yil.py` | s.2284 |
| Agresör dengesi girişte ayırıyor mu? | 08-13 | 45 → 27 | **ÇÜRÜDÜ** — kapıları geçti, karıştırıcı kontrolü çürüttü (r=+0,578 ilk saat fiyatıyla) | `agresor_ilk_saat.py` · `agresor_karistirici.py` | s.3858 |
| "Hızlı tepe = kaybeden" | 08-12 | — | **ÇÜRÜTÜLDÜ** | `scalp_penceresi.py` | s.2825 · s.2875 |

## Fonlama (funding) — projenin en pahalı dersi

| ölçüm | tarih | N | hüküm | betik | defter |
|---|---|---|---|---|---|
| A+B'nin funding bacağı, 2 yıl | 08-12 | 14.599 sinyal / 523 sembol | **KALDI** — +0,111 (t=+4,68), kontrolü üç rejimde de yeniyor; ama küme-dayanıklı t=+1,51 → **kanıtlanamadı, çürütülmedi**. 4. ölçüt düştü (boğa −0,030). **oi24 bacağı ölçülemedi** (OI geçmişi ~30 gün) | `ab_funding_2yil.py` | s.2689 · s.2738 |
| **A+B, fonlama maliyeti dahil** | 08-13 | 8.666 işlem / 497 sembol | **KALDI** — kenar +0,154 → **+0,027**; kontrol (+0,061) sinyali (−0,034) **geçti**. Fonlama kenarın **%83'ünü** yedi | `ab_funding_maliyetli.py` | s.3520 · s.3561 |

> Bu iki satır projenin dönüm noktası: fonlama hariç tutulan her ölçüm yanıltıcıdır.

## LONG arayışı — hâlâ kanıtlanmış arketip yok

| ölçüm | tarih | N | hüküm | betik | defter |
|---|---|---|---|---|---|
| F1 tarayıcı→bot köprüsü (boğa pullback) | 08-10 | 410 | **KALDI** — +0,046R vs kontrol +0,062R | `boga_bacagi_test.py` | s.24 · s.589 |
| F3 derin-negatif funding öncül mü? | 07-15 | 14 pump + 15 kontrol | **ÇÜRÜDÜ** — 0/14; hep T0 sonrası = devam teyidi | — | s.26 |
| LONG karar ölçütü ön-kaydı | 08-11 | — | ön-kayıt: s.1837 | — | s.1837 |
| Gölge LONG pump tezi | 08-11 | 14/25 olay | **KARAR YOK** — pencere dolmadı (toplam −2,09R) | — | eşik notu |
| %10 hedef profili + LONG arayışı | 08-10 | 7.118 olay · A+B 206 · A+B∩pump 201 · A+B∩HAZIRLANIYOR 32 | **A+B %10 hedefle daha iyi doğrulandı** (+2,19% vs tüm olaylar −0,06; iki yarı +2,05/+2,36 — 2R ölçümündeki dalgalanmadan kararlı). **LONG: 30 hücrenin hiçbirinde pozitif yok**; hareket büyüdükçe kötüleşiyor. `HAZIRLANIYOR` kesişimi +4,63% ama **N=32 → izlenim, kural yapılmadı** | `hedef10.py` · `pump10.py` | s.1101 · s.1177 |
| Hedef boyutu — "long hedefini %2,5 yapsak" | 08-10 | — | kayıt: s.1186 | `long25_stop.py` | s.1186 |

## Rejim / altyapı

| ölçüm | tarih | N | hüküm | betik | defter |
|---|---|---|---|---|---|
| F10 sezon+hava rejim katmanı | 07-22 | 2022–2026 | **KISMEN** — çekirdek amaç (ayı-tepki-rallisini boğa sanmama) başarılı; 2023 tabanı fazla erken TAM_BOGA | `f10_sezon_test.py` | s.80 |
| Karar penceresi / S9 ön-kaydı | 08-11 | — | ön-kayıt: s.1807 | — | s.1762 |
| Düşüş freni riski | 08-11 | — | kenar kendini gösteremeden bot duruyor | `fren_riski.py` | s.1692 |
| Sistem denetimi | 08-11 | — | **9 doğrulanmış hata → 8 KAPANDI, 1 AÇIK.** Düzeltmeler 08-11 18:44'te girdi ve **ölçüm penceresi aynı anda yeniden başlatıldı** (s.2510). Durum dökümü aşağıda | `denetim_olcum.py` | s.2371 · s.2453 · s.2510 · `denetim-raporu.md` |
| Defter izolasyon testi | 08-13 | 14 kontrol | **GEÇTİ** — 4 defterin hepsi | `defter_izolasyon_testi.py` | s.3469 |
| Ölçüm ağırlık hatası (ilk parti) | 08-11 | — | **düzeltildi** — ölçümün ağırlığı yanlıştı | `boyut_agirlik.py` | s.1609 |

### ⭐ Bulgu: A+B'nin ham kenarının %65'ini KENDİ STOPUMUZ yiyor (s.2259)

Ölü sinyal taramasının asıl çıktısı, aradığı şeyden büyük:

| kapı | stopsuz ham | A-stop ile | kayıp |
|---|---|---|---|
| **A+B** | +6,10 | +2,14 | **%65** |
| SHORT: skor yüksek | +2,58 | +0,65 | %75 |
| SHORT: oi24 yüksek | +2,01 | +0,69 | %66 |
| **MA50+ucuz** | +0,78 | +0,84 | **%0 — korunmuş** |

Kontrol grubunda da aynı: stopsuz +0,90 (t=+5,12) → A-stopla **−0,05.** Hasarın
büyüklüğünü tek satırda gösteriyor.

**"Stopu kaldıralım" demek DEĞİL** — stopsuz kıyas kuyruk riskini yok sayar. Söylediği
şey: **stop mesafesi A+B için yeniden ölçülmeli.** İki kapı arasındaki asimetri de
dikkat çekici: MA50+ucuz'un stopu kapıya uyuyor, A+B'nin uymuyor.

**Defterde şöyle yazılı: "Pencere kuralı gereği ŞİMDİ UYGULANMAZ (138 işlem / 30 gün
dolana kadar parametre donuk). Pencere sonrası İLK İŞ bu."**

**İkinci, bağımsız kanıt aynı yönde:** `kanal-stochrsi-analizi.md` 13. bölümü de aynı
derse çıktı — ham sinyal +0,243 (t=+3,84) iken A-stop'la +0,051. O belge dersi kural
hâline getirdi (13.5) ve artık `CLAUDE.md` → YÖNTEM'de: **sinyal, kapı ölçümünden
önce mekanikten arınık ölçülür.** İki ölçümün bağımsız olarak aynı yere varması, bunun
tek bir kapının kusuru değil **yöntemsel bir boşluk** olduğunu gösteriyor.

### Denetim raporu — 9 bulgunun bugünkü durumu (2026-08-17'de doğrulandı)

`denetim-raporu.md` kendi durumunu **izlemiyor**; hükümler koddaki düzeltme
işaretlerinden ve canlı durumdan doğrulandı.

| # | bulgu | durum | kanıt |
|---|---|---|---|
| 1 | 🔴 Fren açık işlemleri görmüyor | **KAPANDI** | `testbot.py:1591-1626` — üç parçanın üçü de: fren `yonet_acik_pozisyonlar`'dan **sonra**, `efektif_equity` kullanıyor, aynı değer boyutlandırmada da (`:1120`) |
| 2 | 🟠 Komisyon eksik (binde 0,9) | **KAPANDI** | tüm ölçüm betikleri artık `0,13` |
| 3 | 🟠 Tamamlanmamış saat tam sayılıyor | **KAPANDI** | `olcucu.py:84` · `radar.py:91` |
| 4 | 🟠 Yarım kapamada marjin yarılanmıyor | **KAPANDI** | `testbot.py:773` |
| 5 | 🟡 Kapı atfı yanlış | **KAPANDI** | `testbot.py:417` |
| 6 | 🟡 Gölge zorla kipiyle çalışıyor | **KAPANDI** | `golge.py:102` |
| 7 | 🟡 ATR yöntemi ayrışık | **KAPANDI (ileriye dönük)** | `olcucu.py:98` Wilder; 11 Ağustos sonrası ölçümlerin hepsi Wilder |
| 8 | 🟡 **Toplam pozisyon tavanı yok** | **AÇIK** | config'de `notional`/`tavan`/`toplam` anahtarı yok; boyutlandırma pozisyon başına |
| 9 | 🟢 Kapanan turda son funding | **KAPANDI** | `testbot.py:968` |

**Bulgu 8 hâlâ açık ama tehlikesi büyük ölçüde söndü** — ve bunu söylemek dürüstlük
gereği: raporun asıl endişesi *"fren körken tavan da yoksa ikisi aynı riskin iki yüzü"*
idi ve **fren artık kör değil** (Bulgu 1 kapandı). Ayrıca `islem_risk_pct` %3 → %1,5
indirilmiş. Rapor günü toplam pozisyon sermayenin 2,6 katıydı.

**7 ve 2'nin ortak sınırı:** düzeltmeler **ileriye dönük.** Eski ~20 ölçüm betiği
geriye dönük düzeltilmedi (düzeltilemez de). O eski sonuçlara bakarken ATR yöntemi ve
%0,09 maliyet farkı hatırlanmalı; raporun verdiği düzeltilmiş rakamlar referanstır
(A+B +2,29 → +2,25 · MA50+ucuz +0,82 → +0,78).

## Dört defter — ne öğretti, ve neden hüküm YOK

Rakamlar hızlı değişiyor → canlı state'ten okunur (`durum.md`). Burada yalnız
**kompozisyon, N ve hükümsüzlük gerekçesi.**

| defter | yalıttığı soru | N | durum |
|---|---|---|---|
| `testbot` | Bot ne yaptı? | ~105 poz | Ölçünün temeli; hükmü **ölçüm penceresi** verecek |
| `golge` | ⚠️ **iki iş birden** — aşağıda | 177 poz | Reddedilenlerde işaret doğru yönde, **hüküm yok** |
| `benim` | Kararı kullanıcı verseydi? | **6 poz** | Dört gündür hareketsiz; N=6 → **hüküm imkânsız** |
| `ayna` | Bot girsin, çıkışa kullanıcı karar versin | 84 poz | Çalışıyor ama **kıyas henüz yapılamaz** |

### `golge` — tek soru yalıtmıyor

Rakamlar **`id` ile birleştirilmiş** (kısmi kayıtlar toplandı) ve **mutabakat denklemini
tutturuyor** — sapma −0,07 $:

| küme | N | kazanan | P&L | ort/poz |
|---|---|---|---|---|
| `pump_long_tezi` (hiç denenmemiş LONG tezi) | **122 · %69** | %57 | −1.066,43 | −8,74 |
| **reddedilen girişler** | **56 · %31** | | **−284,29** | **−5,08** |
| ↳ `stop_cok_dar` | 25 | %48 | −326,30 | −13,05 |
| ↳ `long_veto` | 13 | %62 | **+25,50** | +1,96 |
| ↳ `blowoff` | 10 | %60 | **+195,43** | +19,54 |
| ↳ `taker_soguma` | 5 | %80 | −109,19 | −21,84 |
| ↳ `onay_bekle` | 3 | %67 | −69,73 | −23,24 |

**Cevap yönü:** bot **fazla seçici değil** — reddettiği girişler ortalamada para
kaybettiriyor (−5,08 $/pozisyon). En büyük kategori `stop_cok_dar` (asgari %2,0 stop
kapısının elediği) −13,05 ile kuralı doğruluyor: **11 Ağustos'ta ön-kayıtla konan
kuralın canlıdaki ilk bağımsız teyidi.**

**Ama hüküm yazılamaz:** (a) kategori başına N=3–25, hiçbiri eşiğe yakın değil;
(b) `blowoff` (+19,54) ve `long_veto` (+1,96) **pozitif** — yani iki veto para
kaybettiriyor *olabilir*, ama N=10 ve N=13 ile bunu kural yapmak tam olarak
*"en iyi hücreyi seçme"* tuzağı; (c) `taker_soguma` kazanma oranı %80 iken P&L negatif
→ dağılım kuyruklu, ortalama tek başına yanıltıcı.

> ✅ **Bu rakamlar bir kez YANLIŞ hesaplandı, sebebi bulundu.** Önceki hesap
> `not x.get("kismi")` süzgecini **toplarken** kullanıyordu ve TP1'de realize edilen kârı
> düşürüyordu → `blowoff` için −332 (gerçek +195), gölge toplamında **4.465 $** hata.
> Yukarıdakiler id-birleşik ve equity ile mutabık. Kural `CLAUDE.md`'de:
> **süzgeç saymak için, toplamak için değil.**

### `ayna` — mutabakatta 177,84 $ açıklanmamış fark vardı, KAYNAĞI BULUNDU

Mutabakat denklemi ilk koşusunda bir kusur yakaladı: `golge` kuruşu tutarken (−0,07)
`ayna` **−177,84 $** sapıyordu. İzi sürüldü:

```
2026-08-12 17:34   equity 8.420,84   (defterden türemiş)
2026-08-12 17:42   equity 8.817,00   (gölge sızıntısı temizliğinde YENİDEN KURULDU)

eski başlangıç        8.201,18
o ana kadar defter P&L  +615,82
                     ─────────
toplam                8.817,00   ← yeniden kurulan değerle FARK = 0,00
```

> 🔴 **BU TEŞHİS ÇÜRÜTÜLDÜ (2026-08-18).** Aşağıdaki 08-12 anlatısı kaymanın kaynağı
> **değil.** Commit commit mutabakat kuruldu: 2026-08-13 23:06'ya kadar fark
> **−0,01 $** (kuruşu kuruşuna, yani temizlikten SONRA da tamdı). Fark
> **08-14'te doğdu** ve büyüdü: `−0,01 → −102,54 (08-14 21:10) → −177,84 (08-18)`.
> Yani **kalıcı bir kayma değil, SÜREGELEN bir hata** — tam tersi yazılmıştı.
>
> **Mekanizma bulundu — geri alınan kapanış, defterden silinmedi:**
> ```
> ayna_equity.jsonl
>   14:51:41   9.559,64 -> 9.664,47   (+104,83)   acik 6
>   14:51:54   9.664,47 -> 9.559,64   (-104,83)   acik 7   <- GERI ALINDI, poz DONDU
> ayna_islemler.jsonl
>   14:51:41  BAS  ELLE_KAPAT  +104,83   <- kayit SILINMEDI
>   14:52:26  BAS  ELLE_KAPAT  +103,45   <- ayni pozisyon IKINCI kez kapandi
> ```
> Equity doğru geri alındı, **defter kaydı kalmaya devam etti** → defterde equity'ye
> hiç yansımamış +104,83. Kalan ~73 $ için aynı sınıftan başka olaylar aranmalı
> (aynı gün `2Z` iki kez STOP, `EDEN` iki kez ELLE_KAPAT).
>
> **Sınıf tanıdık:** çok-dosyalı durumun atomik olmayan güncellenmesi — gölge
> sızıntısı ve 314 $ olayıyla aynı aile. `ayna.py` atomik **yazıyor**, ama
> "equity'yi geri al + defter kaydını sil" **tek işlem değil.**
>
> **Sonuç:** eşleşmiş `ayna`–bot kıyasının ön koşulu sanıldığından ağır. Önce
> düzeltilmeli; düzeltme **defter mutasyonu** demek, onay ister.

*(Aşağıdaki 08-12 analizi tarihsel kayıt olarak duruyor — o gün doğru sanılmıştı.)*

**Yeniden kurulum `başlangıç + defter P&L` formülünü kullandı — funding terimi YOK.**
`temizlik_notu` *"equity kararlardan yeniden kuruldu"* diyor ama **hangi formülle**
kurulduğunu ve **fonlamanın dışarıda kaldığını** yazmıyor. Bugünkü 177,84 $ kalıntısı
buradan geliyor; kalıcı bir kayma, süregelen bir hata değil.

**Sonuç:** `ayna`'nın equity'si ile defteri **tutarlı değil** ve fark belgeli değildi.
Eşleşmiş kıyas yapılmadan önce bu kayma açıkça düzeltilmeli ya da kıyasa dahil edilmeli
— yoksa ayna-bot karşılaştırması 177,84 $ yanlı başlar. **Bekleyen'e eklendi.**

> **Genel ders:** mutabakat denklemi **yazılmamış bir düzeltmeyi ilk koşusunda yakaladı.**
> Denklemin değeri buydu — hangi yöntemi kullanırsan kullan, equity'yi tutturmuyorsa
> ya hesap yanlıştır ya belgelenmemiş bir müdahale var.

### `ayna` — kıyas bugün YAPILAMAZ
Gereken üç şey elde yok: (a) **eşleşmiş** pozisyon listesi, (b) iki tarafta **etkin**
kasa (ikisinin de açık pozisyonu var), (c) ayna'nın farklı tabanı ve `kayip_veri_notu` /
`temizlik_notu` alanlarının etkisi.

Bugün kıyasa kalkışmak `CLAUDE.md`'nin *"bu hata iki kez yapıldı (fren hatası + ayna
kıyası)"* dediği hatanın **üçüncü tekrarı** olur. → Bekleyen: ön-kayıtlı ayrı ölçüm.

## Radar kare kaybı — ölçüldü (2026-08-17)

`radar_archive.jsonl` **noktasal** veri; makine uyur/internet giderse kareler geri
gelmez. Boşluk artık `radar_bosluk.jsonl`'e işaretleniyor (`radar.py` `_son_arsiv_ts`
+ `_bosluk_yaz`, eşik 2× tur = 30 dk). Geçmiş, arşivden geriye dönük ölçüldü:

| dönem | tur | tahmini kayıp | oran | en uzun |
|---|---|---|---|---|
| Faz 4 (06-24…07-02) | 189 | 677 | **%78,2** | 3.585 dk |
| Temmuz (07-03…07-23) | 1.203 | 714 | %37,2 | 2.361 dk |
| Bot başı (07-23…08-11) | 1.487 | 334 | %18,3 | 1.034 dk |
| **Ölçüm penceresi (08-11…)** | 621 | 46 | **%6,9** | 298 dk |
| ↳ 08-13…08-16 kesinti dönemi | 357 | 25 | %6,5 | 179 dk |

**Ömür boyu oran %33,6 ama bu sayı kullanılmamalı** — kurulum dönemi (zamanlayıcı
sürekli çalışmıyordu) hakim. Karar veren dönem **ölçüm penceresi: %6,9.**
`durum.md`'nin "%7–14" tahmini son dönem için doğruymuş, hafif yüksek.

**Sınır:** 30 dk altındaki boşluklar sayılmıyor → bu oranlar **alt sınır**.
Betik: `scratchpad/radar_bosluk_testi.py` (13 kontrol + geçmiş ölçümü).

> ⚠️ `radar_archive.jsonl` ile yapılan **her** ölçümde `radar_bosluk.jsonl` de
> okunmalı — yoksa eksik pencereyle çalışıldığı fark edilmez. Bugüne kadarki tüm
> arşiv ölçümleri (`oruntu_analiz` · `yon_avi` · `arsiv_analiz` · `erken_analiz`)
> bu bilgi **olmadan** yapıldı.

## Tur başına ağ çağrısı bütçesi — ölçüldü (2026-08-17)

**Soru:** girişe emir defteri derinliği çağrısı eklemek pahalı mı, ve nereye düşer?

### Bütçe (statik sayım + 538 turluk süre kaydı)

| aşama | çağrı/birim | birim/tur | toplam |
|---|---|---|---|
| `cg_universe` · `binance_pool` · `btc_ref` | — | sabit | 3 |
| **aday döngüsü** `radar.analyze` | **3** (klines · premiumIndex · openInterestHist) | 96–150 sembol | **288–450** |
| kısa liste `radar.pillar_d` | **3** | medyan 7, maks 10 | 21–30 |
| giriş `olcucu.measure` | 1 | 0–4 pozisyon | 0–4 |
| **toplam** | | | **313–475, orta ~385** |

**Aday döngüsü tüm çağrıların ~%90'ı.** Günde 187 tur → ~72.000 çağrı/gün.

### Derinlik çağrısı — çarpan farkı 1.400 kat

Çağrı her iki tasarımda da `yeni_giris_ac` → `yeni_giris_ara` içinde, yani **`sure_giris`'e**
yazılır. Fark süre alanında değil, çarpanda:

| | çarpan | çağrı/tur | artış | medyan tur | >450 sn |
|---|---|---|---|---|---|
| **A) yalnız dolan pozisyon** ✅ | 14,4/gün ÷ 187 tur | **0,077** | **%0,02** | +0,06 sn | 9/538 (değişmez) |
| B) her aday | ~120/tur | **+120** | **%31** | 298 → **396 sn** | **85/538 — 9 kat** |

B seçeneği `kesilen_tur` sayacını doğrudan büyütür (kümülatif, şu an 9).

### ⭐ ASIL BULGU — yavaşlık dış kaynaklı DEĞİL, taşıma katmanı

0,70 sn/çağrı "ağ yavaş" diye kaydedilmek üzereydi. Ölçüldü, öyle değil:

| | medyan |
|---|---|
| A) her çağrıda yeni bağlantı (`evren.get`'in yaptığı) | **0,614 sn** |
| B) keep-alive, aynı bağlantı | **0,285 sn** |
| | **2,1 kat** |

[evren.py:54](evren.py#L54) düz `urllib.request.urlopen` — havuz yok, keep-alive yok.
Günde **~72.000 kez TCP+TLS el sıkışması** kuruluyor. `requests.Session` ya da yeniden
kullanılan `http.client.HTTPSConnection` medyan turu **298 → ~145 sn**'ye indirir.

### Rate-limit bir kısıt DEĞİL

~500 ağırlık/tur · 187 tur → **93.600 ağırlık/gün** = Binance günlük tavanının **%2,7'si**,
dakika bazında **%4,2**. Yani `radar.analyze` döngüsündeki `time.sleep(0,05–0,15)` payları
**var olmayan bir tehdide karşı** tur başına 12 sn, günde **37 dakika** ödüyor.

> "Hız için `tarama_havuz_n`'i kıs" diyen önce bu satırı okusun: sıra **keep-alive →
> uyku payı → havuz**. İlk ikisi hangi sembollerin tarandığını **değiştirmez**;
> havuzu kısmak değiştirir ve D/8 gereği pencereyi bekler.

**Düzeltme kaydı:** ilk sayımda >450 sn turlar `sure_giris` ile sayılmıştı (6/538);
kadansla kıyaslanacak alan **`sure_sn`** (toplam tur) → **9/538**. Günlük tur da
sabit değil: 08-15 **161** · 08-16 **181** · 08-17 **187**. 08-17'de beklenen (23,4 saat
÷ 7,5 dk) = 187, gerçekleşen 187 → **bugün hiç tur yenmedi**; "turlar birbirini yiyor"
08-16 için doğru, bugün için değil.

## ⭐ ÖN-KAYIT — HTTP keep-alive (2026-08-17, uygulamadan ÖNCE yazıldı)

**Değişen:** [evren.py:54](evren.py#L54) `get()` — düz `urllib.request.urlopen`
(her çağrıda yeni TCP+TLS) → `urllib3.PoolManager` (bağlantı havuzu).

**ÖLÇÜM ÖNCESİ TABAN** (2026-08-17 23:11–23:34, son dört tur):

| tur | `sure_sn` | `sure_giris` | `sure_yonet` | kesildi |
|---|---|---|---|---|
| 23:11:42 | 329,9 | 323,6 | 5,6 | False |
| 23:18:05 | 262,9 | 257,2 | 5,1 | False |
| 23:26:41 | 328,6 | 319,3 | 8,5 | False |
| 23:33:50 | 308,2 | 300,1 | 7,4 | False |

`kesilen_tur` = **9** (kümülatif, sabit) · 538 turluk medyan `sure_sn` **298,1** ·
>450 sn **9/538**.

**BEKLENTİ (yanılabilirim, kayda geçsin):** medyan `sure_sn` **298 → ~145–180 sn**.
Ölçülen 2,1 kat hızlanma çağrı başına; ama turun tamamı çağrı değil (uyku payı 12 sn,
yerel hesap birkaç sn), o yüzden 2,1 katın tamamını beklemiyorum.

**GEÇME ÖLÇÜTÜ (koşturmadan önce yazıldı).** Keep-alive **kalır** ancak hepsi:
1. Medyan `sure_sn` **anlamlı düşmeli** (≥%25) — 20 tur üzerinden
   → **`223,6 sn` mutlak çizgi** (298,1 tabanının %25 altı)

   **[DEĞİŞTİ 2026-08-17 — ölçüt SIKILAŞTIRILDI, gevşetilmedi]**
   Örneklem süzgeci eklendi: **yalnız `acik_sayisi < 8` turlar sayılır.** Sebep:
   `sure_sn` **iki modlu** — 8 pozisyon doluyken giriş araması hiç koşmuyor
   (N=202, medyan **19,2 sn**), boş slot varken koşuyor (N=340, medyan **322,9**).
   Süzgeçsiz ölçüt hızı değil **pozisyon sayısını** ölçer: pencere içinde 8'e
   dolarsa medyan 19 sn'ye çöker ve ölçüt **yanlış sebeple** geçer.

   ⚠️ **Mutlak çizgi 223,6 sn'de TUTULDU.** Süzgeçli taban 298,1 → **322,9**'a
   çıkıyor; %25 kuralı mekanik uygulansaydı çizgi 242,3'e **gevşerdi**. Sonucu
   gördükten sonra çizgiyi gevşetmek bu projede yasak, o yüzden eski çizgi aynen
   duruyor — yeni tabana göre bu **−%30,7**, yani ölçüt zorlaştı.
   *(Beklenti zaten 145–180 sn; rahat geçmeli. Geçmezse gevşetilmez, geri alınır.)*

   **Örneklem kuralları:** ilk keep-alive turu **23:51:12**'de başlıyor
   (`turun başlangıcı = ts − sure_sn`). 23:46:37'deki 174,5 sn'lik tur **HARİÇ** —
   23:43:42'de başladı, `evren.py` 23:43:56'da yazıldı, yani **eski modül**.
   (Ve 174,5 olağandışı değil: keep-alive öncesi 542 turun 186'sı ≤180 sn.)
2. `verisiz_poz` artmamalı · `kesilen_tur` artmamalı
3. 418/429 davranışı **birebir korunmalı** (testle kanıt)
4. Dört üretim çağıranı (`radar` · `testbot` · `olcucu` · `panel`) sahte sunucuyla geçmeli
5. Eşzamanlı iş parçacığından çağrı bozulmamalı (panel `ThreadingHTTPServer`)

Geçmezse geri alınır ve gerekçe buraya yazılır.

**TASARIM KISITLARI** (biri ihlal edilirse yeni bir hata sınıfı doğar):
- **Modül-global `requests.Session` KULLANILMAZ** — thread-safe olduğu garanti
  edilmiyor. `requests 2.34.2` kurulu olması onu güvenli yapmaz.
- `urllib3.PoolManager` tasarımı gereği thread-safe ve havuzlamayı kendi yapar.
- **Bayat socket** yeniden kullanımda hata atar → **tek seferlik yeniden deneme şart**,
  yoksa şu an hiç görülmeyen bir hata sınıfı doğar.
- **418 soğutma penceresi ve 429 `Retry-After`** aynen korunur — tek doğruluk kaynağı burası.
- Çağıranların hiçbiri `HTTPError`/`.code`'a bakmıyor (tarandı) → istisna tipi serbest.

**D/8:** aynı uç noktalar, aynı sıra, aynı veri, aynı kararlar; yalnız socket yeniden
kullanılıyor → pencereyi beklemez. (Havuzu kısmak *hangi sembollerin* taranacağını
değiştirir, o bekler.)

### 🟢 SONUÇ — GEÇTİ (2026-08-18, 20/20 tur)

| ölçüt | sonuç |
|---|---|
| 1. medyan `sure_sn` ≤ **223,6** | **184,4** — taban 322,9'a göre **−%42,9** ✅ |
| 2. `verisiz_poz` / `kesilen_tur` artmamalı | 0 · **9 = 9** (değişmedi) ✅ |
| 3. 418/429 birebir korundu | test 21/21 ✅ |
| 4. dört üretim çağıranı | test ✅ (panel **üretimde** koşmuyor — süreç eski, `durum.md`) |
| 5. eşzamanlı iş parçacığı | 80 çağrı, hata yok ✅ |

Dağılım: ort 188,9 · min 151,7 · maks 252,0 · `sure_giris` medyan 179,6 ·
`taranan_sembol` 145–146 (17/20 turda alan var) · `sure_giris/sembol` **1,249 sn**.

#### Kanıt: 12 saatlik payda-normalize seri

`sure_giris / taranan_sembol` — havuz boyutundan arınmış tek metrik:

| | değer |
|---|---|
| gözlenen (100 tur, 12 saat) | **medyan 1,117** sn/sembol · %90'ı 1,03–1,29 |
| **tahmin — keep-alive** (3 × 0,333 + 0,10) | **1,10** ✅ |
| tahmin — eski kod (3 × 0,620 + 0,10) | 1,96 |

Seri 12 saat boyunca keep-alive tahmininde **düz**. Ağ gerçekten hızlansaydı
keep-alive turlarının da hızlanması gerekirdi — kalmadı.

#### ⚠️ Ön-kayıtlı tablonun BOŞLUĞU + 02:17 sondası GEÇERSİZ

Üç sonuçlu tablo *"geçer + A kolu **düştü**"* halini saymamıştı ve 02:17 sondası
tam onu gösterdi (A 0,781 → 0,360, oran 1,08×). **Ama o sonda geçersiz, ağ
iyileşmesi değil:**

| sonda | A | B | oran |
|---|---|---|---|
| 00:13 | 0,781 | 0,333 | 2,35× |
| **02:17** | **0,360** | 0,333 | **1,08×** ← geçersiz |
| 12:26 (12 saat sonra) | **0,615** | 0,316 | **1,95×** |

**Neden geçersiz — yapısal ilişki bozuldu.** `A ≈ 2×B` beklenir (A = el sıkışma
2 RTT + istek 1 RTT). Ağ yavaşlasa/hızlansa **ikisi de orantılı** değişir ve oran
korunur. 02:17'de **B hiç değişmedi** (0,3331 → 0,3330), yalnız A yarılandı — bu,
o örneklemde el sıkışmanın bedavaya geldiği anlamına gelir, ağın hızlandığı değil.
12:26 ölçümü A'yı başlangıç seviyesinde buldu (0,615) ve oranı geri getirdi.

→ **Hüküm yalnız erken yarıya dayanmıyor; 12 saatlik serinin tamamı destekliyor.**

#### İKİ DERS — kontrol grubu tasarımı

1. **Kontrol grubu tek sayı değil, ZAMAN SERİSİ olmalı.** Tek sonda, alındığı saate
   göre sahte pozitif ya da sahte belirsizlik üretir.
2. **KONTROLÜN KENDİSİNİN DE GEÇERLİLİK TESTİ OLMALI.** Sonda protokolüne kondu:
   **A/B oranı ~2'den belirgin saparsa o örneklem ATILIR.** Gerekçe: ağ değişimi
   oranı **korur**, ölçüm artefaktı **korumaz**. Bu kural olmasaydı 02:17 sondası
   sağlam bir bulguyu belirsize çevirecekti.

**Not:** `acik_sayisi < 8` süzgeci bu pencerede **hiçbir turu elemedi** (0 atlanan).
Yine de doğruydu — gerçekleşmeyen bir senaryoya karşı korumaydı, sonucu değiştirmedi.

### ⚠️ `sure_sn` KİRLİ BİR VEKİL — kontrol grubu şart

Turun süresi **taranan sembol sayısıyla doğru orantılı** (her sembol = 3 ağ çağrısı)
ve o sayı havuz kapağı · $3M hacim tabanı · cooldown'a göre turdan tura oynuyor —
**hiçbir yerde loglanmıyordu.** Bu tam da bu ölçümde ısırdı: eski kodla koşan bir tur
169,5 sn'ye indi, "hızlandı" sanıldı; A/B sondası ağın iyileşmediğini gösterdi
(2,0× sabit) → farkı yaratan sembol sayısıydı ama **kanıtlanamadı, çünkü kayıt yoktu.**

Süre verisi tek başına *"keep-alive mi, o saatte havuz mu küçüktü"* sorusunu
**cevaplayamaz.** Bu proje aynı soruyu daha önce yaşadı ve hâlâ Bekleyen'de:
*`MA50+ucuz`: kuralın mı, radarın ön elemesinin mi?* — ayıracak veri yoktu.

**İki ek yapıldı (ikisi de ölçümü durdurmadı):**

**1. A/B sondası = KONTROL GRUBU** — `scratchpad/ab_sonda.py`, kayıt
`scratchpad/ab_sonda_kayit.jsonl`. Mekanizmayı havuz boyutundan **bağımsız** ölçer:
A kolu her çağrıda yeni bağlantı, B kolu keep-alive, aynı uç nokta, sırayla.

| ayrım kuralı | hüküm |
|---|---|
| turlar hızlandı **+** sonda 2,0× | **keep-alive** |
| turlar hızlandı **+** sondanın **A kolu da düştü** | ağ iyileşmiş |
| turlar hızlanmadı **+** sonda 2,0× | mekanizma çalışıyor, darboğaz başka yerde |

| sonda | A (yeni bağlantı) | B (keep-alive) | oran |
|---|---|---|---|
| ilk ölçüm (uygulama öncesi) | 0,614 | 0,285 | 2,1× |
| tekrar | 0,634 | 0,323 | 2,0× |
| 08-18 00:13 (pencere içi 1/4) | **0,781** | 0,333 | **2,35×** |

**A kolu düşmüyor, yükseliyor** — ağ iyileşmiyor. Taban sağlam.

### ⭐ BİRİNCİL KANIT — aritmetik kapandı (medyan düşüşü İKİNCİL)

İlk `taranan_sembol` = **145**. Bununla iki rejim de önden hesaplanabiliyor:

```
cagri/tur = 145x3 (analyze) + 8x3 (pillar_d) + 3 (sabit) = 462
uyku payi = 145 x 0,10 = 14,5 sn

eski kod    462 x 0,634 (A kolu) + 14,5 = 307,4 sn   ->  gozlenen 294-300  ✓
keep-alive  462 x 0,323 (B kolu) + 14,5 = 163,7 sn   ->  gozlenen 170-185  ✓
```

**Neden bu birincil:** medyan *"hızlandı"* der; aritmetik *"ŞU mekanizmayla hızlandı"*
der. Sondadan ölçülen çağrı gecikmesi, sayılan çağrı adediyle çarpılınca gözlenen tur
süresini **iki rejimde de** veriyor. Serbest parametre yok.

**Havuz boyutu sorusu da kapandı:** 145, kapak olan 150'ye dayanmış — yani tur
**küçük havuzla** hızlanmadı. Bu, `sure_sn`'in kirli vekil olmasından doğan tek
ciddi karıştırıcıydı.

### GEÇME ÖLÇÜTÜ — ÜÇ SONUÇLU (sonuç belli olmadan yazıldı)

A kolu **yükseliyor** (0,614 → 0,634 → 0,781) ve bu simetrik bir risk yaratıyor:
geçen sefer ağ *iyileşmesi* yanlış pozitif üretebilirdi, şimdi ağ *kötüleşmesi*
yanlış negatif üretebilir. Üç sonuç:

| sonuç | hüküm |
|---|---|
| **geçer** + A kolu sabit ya da **yükselmiş** | **keep-alive çalışıyor** — yükselen A geçişi daha da inandırıcı yapar |
| **geçmez** + A kolu sabit | **geri al**, gerekçe buraya yazılır |
| **geçmez** + A kolu belirgin yükselmiş | **KARARSIZ** — pencere uzatılır, geri alma yok |

> Bu **bar gevşetmek değil, üçüncü bir sonuç eklemek.** Meşruiyeti şuradan:
> yazıldığı anda **4/20 tur** gelmişti ve medyan **179,9** — yani çizginin (223,6)
> çok altında, geçmeye gidiyor. Üçüncü dal yalnız **başarısızlık** hâlinde işe
> yarıyor, dolayısıyla şu an eklemek kendi lehine oynamak olamaz. Sonra yazılsaydı
> olurdu; o yüzden **şimdi** yazıldı.

**2. `taranan_sembol` equity satırına eklendi** ([testbot.py](testbot.py)) — `sure_giris`'in
**paydası**. Gerçek metrik `sure_giris / taranan_sembol`. `None` = giriş aranmadı
(8 poz dolu / fren / makro-kapı) → hız ölçüsüne girmez. **D/8:** sayaç, karar dalına
dokunmuyor → pencereyi beklemez. Pencerenin ilk turları alansız kalır, sorun değil:
**birincil ölçüt 223,6 sn mutlak çizgisi olarak KALIR**, bu ikincil olarak eklenir.

## Pencere tabanı — ÇÖZÜLDÜ (2026-08-18, sayımla)

**Kaydedilmiş çelişki YANLIŞTI ve düzeltildi.** `durum.md` *"'12/138' yalnız 18:42
tabanıyla çıkıyor"* diyordu; o sayım **yalnız kapanan** işlemleri sayıyordu. Kararın
kendi ifadesi *"botun **KENDİ** 12 işlemi"* — yani yeni botun **kendi açtığı**.

| taban | pencerede kapanan | **açılıp kapanan** |
|---|---|---|
| 2026-08-11 12:45 / 12:48 | 13 | **12** ✅ |
| 2026-08-11 18:42 | 12 | 9 |
| 2026-08-12 01:17 | 9 | 5 |

**Sonuç: iki ayrı taban vardı, karıştırılmışlardı** — defter tutarsız değildi.

| soru | taban | dayanak |
|---|---|---|
| bot ne zaman başladı (muhasebe) | **2026-08-11 12:48** | kullanıcı kararı (`_kasa_sifirlama`) · git `34524ad` 12:46:24 · "kendi 12 işlemi" sayımı |
| hakem penceresi (parametre kararlılığı) | **2026-08-12 01:17** | pencere kuralı *"parametre değişmez"*; 12:48 sonrası iki davranış değişikliği var — `b5123b6` kısmi kâr (08-11 22:38), `0b3f3e3` cadence (08-12 01:17) |

**Aday 2 (18:42) düşer:** ne muhasebe ne parametre tabanı. Denetim düzeltmeleri
bug onarımıydı (D/8), yeni pencere gerektirmiyordu.

**Ders:** *"kapanan"* ile *"açılıp kapanan"* aynı şey değil. Bu ayrımı atlamak
kaydedilmiş bir çelişki üretti ve üç kez üç farklı sayı verdirdi.
Tanım ve sayım komutu → `durum.md`.

## CEO çerçevesi ile botun çıkış disiplini ÇELİŞTİ (2026-08-18, gözlem — kural çıkarılmadı)

Kullanıcı isteğiyle `kripto` CEO skill'i açık pozisyonlara uygulandı. **İki sistem farklı
cevap verdi ve bu kayda değer**, çünkü ikisinin kanıt durumu farklı:

| | CEO çerçevesi | botun çıkış kuralları |
|---|---|---|
| `BAS` SHORT +1,92R | **KÂR AL** (ileri R/R 0,58:1) | tut (sabit %10 hedef) |
| `PRL` LONG | **YARIYA İN** (funding +0,0304% > eşik · 1g RSI 75 · OI +%38,6) | tut |
| kanıt durumu | vetoları **ön-kayıtla sınanmadı** | **29 varyant sınandı**, sıkılaştıran 28'i kaldı |

**Karar: botun kuralları geçerli.** CEO'nun tavsiyesi tanımı gereği *çıkışı sıkılaştırmak*
ve 28/28'e karşı savunması yok.

**CEO'nun kattığı değer karar değil, iki ÖLÇÜLEBİLİR soru** (→ Bekleyen): ileri R/R eşiği
ve pozisyon boyutu ayrışması.

⚠️ **N=1 ANEKDOT TUZAĞI — bilerek kayda geçiriliyor.** Aynı oturumda `HOLO` SHORT, CEO
okumasının aleyhte işaret ettiği yönde (kalabalık short L/S 0,58 + Fiyat↑+OI↑) **bir saat
sonra stop oldu**; `BAS` ise CEO "kâr al" dedikten sonra **25 dakika %0,4'lük bantta yatay
kaldı** (dönmedi). Biri isabet biri değil, **ikisi de N=1**. Birini başarı diye kaydedip
diğerini yazmamak bu projede reddedilmiş davranıştır.

## ⭐ ÖN-KAYIT — İLERİ R/R ÇIKIŞ EŞİĞİ (2026-08-19, KOŞTURMADAN ÖNCE yazıldı)

### Hipotez
Açık pozisyonun **ileri R/R**'si — *(hedefe kalan mesafe) ÷ (stopa kalan mesafe)* —
eşiğin altına düştüğünde kapatmak, mevcut sabit %10 hedefe göre **net getiriyi artırır.**

### Neden bu soru soruldu
Sabit %10 hedef, pozisyon ilerledikçe ödül-risk geometrisinin **tersine dönmesini**
hesaba katmıyor. Kâr biriktikçe stop sabit kalır, hedef yaklaşır; bir noktadan sonra
pozisyon **kazanabileceğinden fazlasını riske atar.**

**Tetikleyen canlı vaka (2026-08-18):** `BAS` SHORT +1,92R'de iken stopa **%8,51**,
hedefe **%4,97** → ileri R/R **0,58:1**. Dört saat sonra stop oldu, +1,92R'nin tamamı
geri verildi (defter: TP1 +47,52 · STOP −34,16 · toplam +13,36).

### Eşik: **1,0** — ve neden tarama YAPILMAYACAK
Tek eşik ön-kayıtlanır: **ileri R/R < 1,0 → kapat.** Gerekçe **önsel**: 1,0 geometrik
başabaştır — altında pozisyon kazanabileceğinden fazlasını riske atar. Giriş eşiği olan
2:1 kullanılmadı, çünkü **girmek ile tutmak farklı kararlar**; 2:1 tutma şartı
pozisyonların çoğunu erken kapatırdı.

⚠️ **Dürüstlük notu:** 1,0 eşiği `BAS` vakasını (0,58) da kapsıyor. Eşik o vakadan
türetilmedi — geometrik başabaş olduğu için seçildi — ama **örtüşme kayda geçiyor**,
okuyan kendi kararını versin. **Eşik taraması (0,5 · 0,8 · 1,2 · 1,5 denemek) YASAK.**

### Ölçüm yöntemi
`CLAUDE.md` sırası: **ham ileri getiri → ticaret mekaniği → portföy.** Bu kural bir
*mekanik* olduğu için mekanik katmanında, **aynı giriş kümesi üzerinde** ölçülür.

- Veri: `scratchpad/klines_1h_uzun/` (2 yıl, 566 sembol — boğa ve ayı bacağı dahil)
- Kontrol: **mevcut sabit %10 hedef**, birebir aynı girişlerde
- Maliyet: **fonlama + ücret + kayma DAHİL** (hariç tutulan ölçüm bu projede yanıltıcıdır)
- İstatistik: **`t_küme`** (sembol-kümeli), ham t değil

### GEÇME ÖLÇÜTÜ — dördü de gerekli
1. Net getiri (maliyet sonrası) kontrolden **yüksek**
2. **İKİ YARIDA DA** yüksek (A ve B ayrı ayrı) — tek yarıda geçen KALDI sayılır
3. **`t_küme` > +2,0**
4. Üç rejimin (AYI/NOTR/BOĞA) **hiçbirinde ters işaret yok**

### BEKLENTİ — sonuç görülmeden yazıldı
**KALACAĞINI bekliyorum.** Gerekçe: bu bir **sıkılaştırmadır** ve bu projede çıkış
tarafında denenen **29 varyantın 28'i sıkılaştırıyordu, 28'i de kaldı**; geçen tek
varyant çıkışı *gevşetiyordu*. Ön bilgi açıkça aleyhte.

⚠️ **N=3 UYARISI — ölçütü yumuşatma gerekçesi DEĞİL.** 18-19 Ağustos'ta CEO çerçevesinin
tavsiyesi üç pozisyonun üçünde de daha iyi sonuç verirdi (toplam **+173,64 $**; BTC aynı
dönemde %+0,09 ile düz, yani tek makro olay değil). Bu **gözlem**, kanıt değil —
`CLAUDE.md`: *N<25-30 = izlenim*. Sonucu gördükten sonra bu üç vakaya dayanıp ölçütü
gevşetmek, projenin en açık yasağıdır.

### Betik ve kayıt
Betik yazılacak: `scratchpad/ileri_rr.py`. Sonuç bu bölümün altına yazılır; **ölçüt
metni sonuç görüldükten sonra DEĞİŞTİRİLMEZ** (D/9: değişirse eski metin silinmez,
yanına `[DEĞİŞTİ tarih]`).

## Bekleyen — ölçülmedi

| soru | neden bekliyor |
|---|---|
| **İLERİ R/R eşiği — sabit hedefe eklenmeli mi?** (2026-08-18, CEO okumasından doğdu) | Sabit %10 hedef, pozisyon ilerledikçe **ödül-risk geometrisinin tersine dönmesini** hesaba katmıyor. Canlı örnek: `BAS` SHORT +1,92R'de iken stopa %8,51, hedefe %4,97 → **ileri R/R 0,58:1**, yani 1:2 eşiğinin çok altında. ⚠️ **Bu bir sıkılaştırmadır ve 28/28'e karşı savunma gerektirir** — ön-kayıt yazılmadan ölçülmez. Ölçüm 2 yıllık veride, ham→mekanik sırasıyla; "en iyi eşik" taraması YASAK, tek eşik ön-kayıtlanır |
| **Pozisyon boyutu neden 2 kat ayrışıyor?** (2026-08-18) | Aynı risk ayarında `PRL` risk %1,46 eq / marjin %11,6 eq iken iki SHORT %0,67-0,75 / %3,5-4,0. Ayrışmanın kaynağı bilinmiyor (kaldıraç tavanı · stop genişliği · efektif equity ölçeklemesi). **Pencere hükmünü doğrudan etkiler:** ön-kayıtlı ölçüt *"ikinci yarı > 0"* diyor ve kasa sıfırlaması zaten boyutları ortada büyütmüştü; üstüne pozisyonlar arası 2 kat fark varsa dolarla kıyas iyice geçersiz → **R/yüzde kıyası zorunlu**. 21-22 Ağustos taramasına madde |
| `d_taker` — agresörün pozisyon ömrü boyunca **kayması** | Veri 2026-08-13'te toplanmaya başladı, geriye dönük üretilemez. ~27 Ağustos'ta yeterli olur |
| **Pozisyon başına fonlama** — kapı × fonlama, tutuş × fonlama, fonlamalı gerçek R | Alan `funding_usdt` 2026-08-17'de eklendi (`testbot.py` `funding_uygula` + `_funding_dilim`); **geriye dönük üretilemez.** O tarihten **önce açılmış** pozisyonlar için cevap kalıcı olarak yok — bot başlangıcından o güne kadarki kümülatif fonlama pozisyonlara **hiç atfedilemeyecek**. Ölçüm birkaç düzine yeni pozisyon birikince ön-kayıtla yapılır. **Alanın anlamı, `null`/`0.0` ayrımı ve süzgeç → `CLAUDE.md`** |
| `MA50+ucuz` kapısının **fonlama** yükü | Kapı 2 yılda ölçüldü ve çürütüldü (s.2790) ama o test fonlama maliyetini içermiyordu. A+B'yi bitiren hesap bu kapı için yapılmadı. **Beklenti A+B'nin aynısı olmamalı:** A+B fonlamayı *tanım gereği* seçiyordu (funding ≤ −0,05 → kontrolün 11 katı ödüyor), MA50+ucuz ise fiyat ve MA50 mesafesine bakıyor, fonlama terimi yok. Yine de ucuz/şişmiş altcoinlerde fonlama çarpık olabilir → **ölçülmeden bilinmez**. ⭐ **2026-08-17'den itibaren CANLI yol açıldı:** işlem kaydına pozisyon başına `funding` alanı eklendi, artık kapı × fonlama kırılımı geriye dönük backtest'e muhtaç değil. Açık pozisyonların çoğu bu kapıdan geliyor → veri hızlı birikir |
| `MA50+ucuz`: canlı artı kuralın mı, radarın ön elemesinin mi? | Ayırmanın tek yolu 2 yıllık OI verisi — yok. **Hakem canlı ölçüm penceresi** (başlangıç **2026-08-12 01:17** — çözüldü 2026-08-18; bitiş 138 pozisyon veya 30 gün) → tanım, sayım komutu ve diyagram **`durum.md`**'de |
| A+B kapısı kararı | 2 yıllık **fonlamalı** ölçüm "kapat" diyor, canlı 16 işlem "kapatma daha kötü olurdu" diyor. 12 Ağustos'ta kullanıcı "açık kalsın" dedi (s.2812); nihai karar hâlâ açık |
| Giriş aramasının süre maliyeti | Tur süresi ölçümü 08-14'te eklendi; ortalama 138 sn giriş aramasında |
| **Boğa-bacağı walk-forward ölçümü** — HİÇ YAPILMADI | `kazanan-bot-arastirma-raporu.md` §8.1'in 1. maddesi. **Projenin en büyük bilinen açığı** (LONG'un kanıtlanmış arketipi yok) ve **veri elde**: `scratchpad/klines_1h_uzun/` 566 sembol / 2 yıl, gerçek boğa içeriyor. Aynı raporun 3. maddesi (portföy düşüş limiti) 08-10'da uygulandı — 1. madde beklemede |
| **K1–K6 değerlendirmesi koşturuldu mu?** | `test-degerlendirme-programi.md` ön-kaydı 2026-07-10'da yazıldı, **sonucu hiçbir yerde yok.** Ön-kayıt yazıp sonucunu yazmamak projenin kendi disiplinine aykırı. K1 eşiği ("equity > 1000 $") bugünkü 10.000 $ tabanlı bot için geçersiz; ama **koşturulup mu geçildi, atlandı mı** — bu bilinmeli. D/8 ve D/9 kuralları `CLAUDE.md`'ye taşındı |
| **`testbot._kilit_al` aynı check-then-act kusurunu taşıyor** — ⚠️ **ŞİMDİ DOKUNMA** | `os.path.exists()` → `open(...,"w")`; `ayna`'da bu desen gerçekten ısırdı ve `O_CREAT\|O_EXCL` ile düzeltildi. **Ama `testbot`'ta İKİ BAĞIMSIZ SAVUNMA var ve 45 günde ısırmadı:** (1) zamanlayıcıda `MultipleInstances=IgnoreNew`, (2) `ExecutionTimeLimit` **1200 sn**, kilidin bayatlama eşiği **1250 sn** — yani Windows süreci **önce** öldürüyor, kilit **ondan sonra** bayatlıyor. Bu sıralama bilinçli tasarlandı ve kodda yazılı ([testbot.py:1624](testbot.py#L1624)). **Ölçüm penceresi açıkken `testbot` kilidine dokunmak kusurun kendisinden büyük risk:** kilitte yeni bir hata **çift tur** demektir, o da doğrudan pencereyi bozar. Pencere kapandıktan sonra ele alınır |
| **`ayna` eşleşmiş kıyası** | Ön-kayıtlı ayrı ölçüm işi — gerekçe yukarıdaki defterler bölümünde |
| **Derinlik çağrısına kısa timeout (3–5 sn)** | `_get` varsayılanı **25 sn**; derinlik çağrısı onu taşıyor → ağ takılırsa açılan pozisyon başına +25 sn, turda en fazla 4 pozisyon = teorik +100 sn. ⚠️ **Keep-alive bunu ÇÖZMEZ** — keep-alive el sıkışma gecikmesini siler, timeout kuyruğunu silmez: sunucu takılırsa 25 sn yine 25 sn. İkisi **ayrı iş**. Derinlik ölçüm verisi, karar değil → kısa timeout'ta kaybetmek ucuz |
| ⚡ **HTTP keep-alive / bağlantı havuzu** — ölçüldü, uygulanmadı | [evren.py:54](evren.py#L54) her çağrıda yeni bağlantı açıyor; keep-alive medyan çağrıyı **0,614 → 0,285 sn** (2,1 kat) indiriyor, medyan turu **298 → ~145 sn**. **Pencereye bağlı DEĞİL** — D/8: aynı uç noktalar, aynı sıra, aynı veri, aynı kararlar; yalnız socket yeniden kullanılıyor. Pencereye bağlı beş işin arkasında beklemesi gerekmiyor, ama derinliğin de önüne alınmadı. Ölçüm: yukarıdaki "ağ çağrısı bütçesi" bölümü |
| **Slipaj varsayımı tutuyor mu?** (emir defteri derinliği) — ⚙️ **veri 2026-08-17'den beri toplanıyor** | Alan `derinlik_giriste` işlem kaydında: `slipaj_pct` (notional defterin karşı tarafını yerken oluşan VWAP sapması) · `defter_usdt_20` · `yetersiz` (defter 20 seviyede tükendiyse slipaj **alt sınırdır**). `null` = ölçülemedi. Pozisyon başına **1 çağrı**, aday döngüsüne girmiyor. Ölçüm birkaç düzine pozisyon birikince ön-kayıtla yapılır. Bütün ölçümler slipajı **%0,02 varsaydı**; hiç doğrulanmadı ve A+B'nin sınırlar bölümü *"slipaj yok sayıldı; olaylar düşük hacimli coinlerde yoğunlaşıyor"* diyor. Gerçek paraya geçişte kenarı belirleyecek kalem bu. Giriş anında derinlik kaydı planlandı — **yalnız dolan pozisyonda**, reddedilen adaylarda değil (o, çağrıyı giriş arama döngüsünün içine sokar; tur süresi zaten 314–440 sn). ⚠️ **SINIR — şimdiden yazıldı:** yalnız dolan pozisyonda ölçmek **seçilim yanlı bir örneklemdir.** *"Bizim işlemlerimizde tuttu mu"* için doğru örneklem, yanlılık yok. *"Daha çok işlem yapsak da tutar mıydı"* için **yanlış** örneklem. İkincisine genişletmek isteyen bu cümleyi okumadan genişletmesin |
| **`ayna`'nın 177,84 $ equity–defter kayması** | Kaynağı bulundu (08-12 17:42 temizliğinde equity `başlangıç + defter P&L` ile, **funding'siz** yeniden kuruldu). **Kıyastan ÖNCE** düzeltilmeli ya da kıyasa dahil edilmeli, yoksa ayna-bot karşılaştırması yanlı başlar. Ayrıntı defterler bölümünde |

---

## Kütüğe girmemiş betikler

`scratchpad/` altında 59 ölçüm betiği var; yukarıda **~30'u** adlandırıldı. Kalanlar
ya yardımcı (veri indirme: `funding_indir.py`, `scalp_1m_indir.py`, `ze_veri.py`) ya
da defterde ayrı bir sonuç bölümü olmayan ara çalışmalar. Bir betiği kullanmadan önce
defterde karşılığı olup olmadığına bak; yoksa **sonucu yeniden üretilmeden
güvenilmez.**
