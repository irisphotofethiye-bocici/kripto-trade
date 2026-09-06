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

## Çıkış kuralları — 30 varyant, 1'i geçti

> 🔻 **GÜNCEL SAYIM (2026-08-31): 30 denendi · 1 geçti · sıkılaştıran 29'un 29'u kaldı.**
> Aşağıdaki 29'luk döküm **2026-08-17 tabanıdır**; 30. varyant (30. dakikada kesme)
> 2026-08-30'da düştü. **Bu sayıyı tekrarlamadan önce buraya bak** — bir kez
> bayatladı ve iki dosyaya yanlış kopyalandı.

**TABAN SAYIM (2026-08-17'de yapıldı).** Beş ölçüm · içlerinde **29 ayrı varyant**:
5 (çıkış kıyası) + 8 (oynak hedef) + 7 (kısmi: 4 kural + 3 şekil) + 1 (başabaş) +
8 (erken müdahale) = **29.**

**Geçen: 1** — sabit %10 hedef. Ve o **çıkışı gevşetiyordu.** Çıkışı sıkılaştıran
~~**28 varyantın 28'i de kaldı.**~~ **[DEĞİŞTİ 2026-08-30] → 29 varyantın 29'u.**

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
| **BTC risk-payı (`btc_d_xs`) → SHORT freni** | 08-04 | 12 ay · 103 sembol · **37.271** | ⭐ **GEÇTİ — projenin TEK gerçek out-of-sample sinyali.** Aşağıda | betik KAYIP (bkz. not) | commit `4f5046a` · config `_btc_pay_not` |

### ⭐⭐ BTC risk-payı freni — GERÇEK HOLDOUT'TAN GEÇEN TEK SİNYAL (2026-08-04)

**Kütüğe 2026-08-19'da eklendi** — ölçüm indeks kurulmadan (08-17) önce yapıldığı için
arada kalmıştı. *"Bunu daha önce ölçtük mü?"* sorusuna yanlış cevap verdiriyordu.

**Sinyal:** `btc_d_xs` = BTC mcap ÷ (TOTAL − stablecoin mcap) — BTC'nin **risk varlıkları
içindeki payı**. Stablecoin çıkarılır çünkü *"para kriptodan çıktı mı"* ile *"para kripto
içinde BTC'ye mi kaydı"* farklı sorulardır; ölçülen ikincisi. **Seviye değil, 3 günlük
PUAN değişimi.**

```
12 ay · 103 sembol · 37.271 gozlem
GERCEK HOLDOUT:  kesif 2025-08..2026-03  |  SAKLI 2026-04..2026-08

  ALT ceyrek        SHORT R  +0,27 / +0,16     (temel +0,06 / +0,04)
  UST ceyrek        SHORT R  -0,02 / -0,03     <-- FRENLENEN BANT
  UST + para-durgun LONG  R  +0,24 / +0,16     (rastgele -0,07 / -0,04)

  kesif/sakli ayrimi  +0,45  vs  +0,46      <-- HIC BOZULMADI
  saklida dilimler    MONOTON sirali (+1,00)
```

**Neden bu ölçüm diğerlerinden farklı:** bu projedeki çoğu ölçüm veriyi ikiye bölüp
*"iki yarıda da tuttu mu"* diye bakar. Burada **saklı dönem gerçekten saklıydı** — keşif
8 ayda yapıldı, sonraki 4 ay hiç görülmeden sınandı ve ayrım bozulmadı.

**Eşikler İCAT EDİLMEDİ:** 365 günlük serinin çeyrekleri — ÜST %75 = **+0,287**,
ALT %25 = **−0,318**.

**Kural asimetrik, çünkü ölçüm asimetrik.** Fren **yalnız SHORT'u kapatır, hiçbir LONG
AÇMAZ** (kodda yazılı: `[FREN LONG-NOTR]`). Mekanizma tezi: BTC pay kazanırken alt'lar
zaten satılmış olur, short'a aşağıda alan kalmaz → kenar sıfıra iner (+0,06 → −0,02),
işlem maliyetini bile çıkarmaz.

**AYRI LOG NEDENİ — kayda değer:** mevcut `piyasa_yapisi_log` BTC.D topluyordu ama bu
sinyali **üretemiyor**: aynı dönemde korelasyon **−0,12**, işaret uyuşması **%47**
(yazı-tura). Sebep: o log günde ~2 kez **düzensiz saatlerde** yazıyor. Ondan beslenseydik
**ölçülen sinyali değil gürültüyü** bağlamış olurduk → `btc_pay_log.jsonl` ayrı ve günlük.

> ⚠️ **SINIR (commit mesajında yazılı):** ölçülen 12 ayın **tamamı düşen piyasa**
> (TOTAL −%40). **Yükselen piyasada ilişki tersine dönebilir — ölçülmedi.**

> ⚠️ **BETİK KAYIP.** Ölçüm, betiklerin geçici oturum klasöründe tutulduğu dönemde
> yapıldı (s.617'deki uyarı: *"o ölçümler bugün yeniden koşulamıyor, yalnız sonuçları
> kayıtlı"*). **Yeniden üretilemez** — rakamlar commit `4f5046a` mesajından ve config
> `_btc_pay_not` alanından geliyor. Geri alma: `esikler.btc_pay_short_freni = 0`.

**Canlı doğrulama (2026-08-19):** fren pencerede tetiklendi ve frenlediği 13 aday ileri
oynatıldı → ortalama **−1,198%**, 9'u stop. Ölçümün öngörüsü tuttu. Ayrıntı aşağıda
("BTC-pay SHORT freni pencerede tetiklendi").

> 🔴 **SHORT BACAĞI 2026-08-19 13:44'TE DEVRE DIŞI BIRAKILDI (kullanıcı kararı).**
> `esikler.btc_pay_short_freni: 1 → 0`. **Ölçüm çürütülmedi** — aksine aynı gün canlı
> doğrulandı (13 aday, −1,198%, 9 stop). Kapatma gerekçesi kâr değil **ölçüm akışı**:
> pencere 2 gün boyunca SHORT üretmiyordu. Bu bir **pencere ihlalidir** ve kullanıcı
> pencereyi devam ettirmeyi seçti → hüküm iki dönem ayrı raporlanmalı. Karar, gerekçe,
> geri alma ve `[DEĞİŞTİ]` notu **`durum.md`**'de (tek sahip).
> **LONG bacağı (AYI kolu, `btc_pay_ayi_long`) DOKUNULMADI.**

#### ⚠️ ÖLÇÜMÜN LONG BACAĞI VAR AMA NOTR'DA ERİŞİLEMİYOR (2026-08-19'da fark edildi)

Aynı ölçüm **iki** sonuç üretti; ikisi de aynı 37.271 gözlemden ve aynı holdout'tan:

```
UST ceyrek                ->  SHORT R  -0,02 / -0,03   -> FREN konuldu    ✅
UST ceyrek + para DURGUN  ->  LONG  R  +0,24 / +0,16   -> kapi konuldu    ✅
                              (rastgele kontrol -0,07 / -0,04)
```

**Yani ölçüm dengeli** — aynı sinyal "short'u kes" derken "long'u aç" da diyor.

**Ama LONG kapısı AYI dalının içine gömülü** ([testbot.py:559](testbot.py#L559):
`btc_pay_ust and para_durgun`, `rejim_ad == "AYI"` kolunda). 2026-08-19 durumu:
`bant = UST` ✅ · `para_rejim = PARA DURGUN` ✅ · **`rejim = NOTR`** ❌ → o kod yoluna
hiç girilmiyor.

**Sonuç:** ölçümün **+0,24/+0,16** veren kapısı kapalı; boşluğu **ölçümle
gerekçelenmemiş** `notr_long_acik` dolduruyor (kendi notu: *"ön-kayıtlı kural BU
ETİKETTE DE GEÇİLEMEDİ: A +0,79 / B −0,17, işaret yarıyı döndürüyor"*).
**Bot, elinde güçlü kanıt varken zayıf kanıtla işlem açıyor.** 2026-08-18/19'daki
3 LONG (−450,00 $) tam oradan geldi.

**ASİMETRİNİN YERİ — "denge" tartışması buradan başlamalı:**

| taraf | kanıt katmanı |
|---|---|
| **SHORT** | kapı ölçüldü (A+B +0,396R) · ikinci kapı ölçüldü (MA50+ucuz) · rejim freni **gerçek holdout** |
| **LONG** | tek kapı, **ölçümle gerekçelenmedi**, işaret yarı döndürüyor |

Dengesizlik frenin fazlalığından **değil**, LONG tarafının **kanıt standardının**
düşüklüğünden. "Simetrik LONG freni" eklemek, ölçülmemiş makineye bir ölçülmemiş parça
daha eklemek olur → *karmaşıklık bütçesi* ihlali. **Akılcı yön ters: LONG tarafını daha
izinli değil, SHORT ile aynı kanıt standardına çekmek.**

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

> 🔴 **[ŞERH 2026-09-05] BU KUTUNUN ASİMETRİ YORUMU 2 YILLIK VERİDE DESTEKLENMEDİ.**
> Yukarıdaki kıyas **stopsuz kolu SABİT ufukta** tutuyor — iki kolun tutma süresi
> eşit değil. Aynı kusur `stop_mu_sure_mu`'da (2026-08-26) işareti **döndürmüştü**.
> Stop genişliği taraması iki kapıda da koşturuldu: **6 karşılaştırmanın 6'sı da
> aynı yön** → *"A+B'nin stopu kapısına uymuyor"* **yeniden üretilemedi**.
> Sayılar ve hüküm: bu dosyada → *STOP MESAFESİ (2026-09-05)*. **İş kapandı.**

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
Betik: `scratchpad/ileri_rr.py` (commit `bf2b95f`). Ham çıktı:
`scratchpad/ileri_rr_sonuc.txt`. **Ölçüt metni sonuç görüldükten sonra
DEĞİŞTİRİLMEDİ.**

### 🔴 SONUÇ — **KALDI** (2026-08-19, 565 sembol / 2 yıl)

```
A_funding   N=20.521          B_ma50ucuz  N=4.340
  kontrol  +0,006% (t +0,16)    kontrol  -0,235% (t -2,62)
  kural    -0,062% (t -2,34)    kural    -0,231% (t -3,79)
  FARK     -0,069% (t -2,35)    FARK     +0,003% (t +0,05)
           t_kume -0,37                  t_kume +0,01
```

| ölçüt | A_funding | B_ma50ucuz |
|---|---|---|
| **1.** net getiri kontrolden yüksek | ❌ **−0,069%** (daha kötü) | ❌ +0,003% — `t=+0,05`, sıfırdan ayrışmıyor |
| **2.** iki yarıda da yüksek | ❌ A **+0,020** / B **−0,158** | ❌ A **−0,089** / B **+0,095** — işaret ters |
| **3.** `t_küme > +2,0` | ❌ **−0,37** | ❌ **+0,01** |
| **4.** rejimde ters işaret yok | ❌ AYI +0,068 · BOĞA **−0,192** · NOTR −0,099 | ❌ AYI +0,089 · BOĞA +0,046 · NOTR **−0,020** |

**Dört ölçütün dördü de, iki giriş kümesinin ikisinde de başarısız.** Kural reddedildi.

**ÖN-KAYITLI BEKLENTİ TUTTU** — "KALACAK" yazılmıştı, kaldı.

### Mekanizma — sayım tek başına açıklıyor

```
              KONTROL                        KURAL
A_funding     STOP  14.282 (%69,6)           STOP  11.461 (%55,9)
              HEDEF  4.643 (%22,6)           HEDEF     208 (%1,0)
              SURE   1.596                   RR      8.754 (%42,7)

B_ma50ucuz    STOP   3.095 (%71,3)           STOP   2.423 (%55,8)
              HEDEF    963 (%22,2)           HEDEF      57 (%1,3)
              SURE     282                   RR      1.853 (%42,7)
```

Kural iki şey birden yapıyor:
- **KURTARIYOR:** stop olacak 2.821 işlem (A) artık orta noktada kârla çıkıyor
- **ÖLDÜRÜYOR:** hedefe varacak 4.643 işlemin **4.435'i** artık %10 yerine ~%4'te kesiliyor

İkincisi birinciden büyük → net negatif. Bu, projenin tekrarlayan bulgusunun
sayısal hâli: **kötü girişte sıkı çıkış kaybı keser, iyi girişte kazancı keser** —
ve burada ikinci etki baskın.

**Kural nadir bir uç durum değil:** işlemlerin **%42,7'sini** değiştiriyor (iki kümede
de birebir aynı oran).

### Sayım güncellendi
Çıkış tarafında **30 varyant** denendi, **1'i** geçti. Sıkılaştıran **29 varyantın
29'u da kaldı.** Geçen tek varyant hâlâ çıkışı *gevşeten* (sabit %10 hedef).

### Yan bulgu — ön-kayıtlı soru DEĞİL, not olarak
`B_ma50ucuz` **kontrolü** (yani botun bugün koştuğu hâli) **−0,235%, t=−2,62** çıktı;
fonlama dahil, 2 yıl, N=4.340. Bu, `MA50+ucuz` kapısının negatifliğinin **bağımsız bir
teyidi** (önceki ölçüm: −0,079 · t=−4,05, s.2790). ⚠️ Ön-kayıtlı soru bu değildi ve
bu satırdan **kural çıkarılmaz** — pencereye bağlı altı işin tartışmasına **girdi**
olarak taşınır.

## BTC-pay SHORT freni pencerede tetiklendi (2026-08-19, gözlem + post-hoc ölçüm)

**Ne oldu:** Fren **2026-08-18 00:01**'de açıldı. O andan itibaren SHORT girişi **sıfır**;
`VETO:btc_pay_freni` 0 → **585 satır**. Bot boş oturmadı — `NOTR-belirsiz long` kapısı
boşluğu doldurdu.

```
pencere kirilimi (taban 12 Agu 01:17)
  fren ONCESI   N=89   P&L +807,48   85 SHORT / 4 LONG
  fren SONRASI  N= 3   P&L -450,00    0 SHORT / 3 LONG
```

**Tetikleyen:** `btc_d_xs` (BTC'nin risk varlıkları içindeki payı, stablecoin hariç)
**17→18 Ağustos'ta tek günde +0,3022 puan** sıçradı. Fren *seviyeye* değil **3 günlük
değişime** bakar; sıçrama 3 günlük pencerenin içinde kaldığı sürece açık kalır.
Sıçrama 21 Ağustos'ta pencereden çıkar → **fren kendiliğinden kalkar** (`btc_d_xs`
65,60 civarında kalırsa). Hesap `durum.md`'de.

### ⭐ FREN DOĞRU ÇALIŞTI — frenlenen SHORT'lar ölçüldü

Fren sonrası reddedilen adaylar botun gerçek mekaniğiyle ileri oynatıldı
(giriş = veto sonrası bar açılışı · A-stop · %10 hedef · 72s · maliyet dahil):

```
N=13 bagimsiz olay    9 STOP · 2 HEDEF · 2 hala ACIK
ortalama -1,198%   medyan -3,004%   kazanan 3/13
yalniz karara baglanmis: N=11, ortalama -1,927%
```

En kötüler: `GPS` −%10,09 · `RED` −%6,28 · `ACE` −%5,94.

**Yani fren para KAZANDIRDI.** SHORT kapısını gevşetmek, bu 13 işlemi *almak* demek.
Kullanıcının *"piyasada short engelleyen bir durum yok"* öncülü test edildi ve
**çürüdü** — piyasa short'u mekanik olarak engellemiyor, **kârlı olmaktan çıkarmış**;
frenin 12 aylık holdout ölçümünün (bu bantta SHORT R −0,02/−0,03) söylediği tam bu.

⚠️ **N=13 · post-hoc · ön-kayıtsız · ufuk truncated (2 olay hâlâ açık).** İzlenim,
kanıt değil. Yön nettir ama eşik değiştirmeye YETMEZ.

> 🔴 **SONRAKİ GELİŞME (2026-08-19 13:44):** fren **kullanıcı kararıyla kapatıldı.**
> Aşağıdaki ölçüm (frenin haklı olduğu) **geçerliliğini koruyor**; kapatma kararı bu
> ölçüme rağmen ve ölçüm akışı gerekçesiyle alındı. Ayrıntı `durum.md`.

### 🔴 ASIL BULGU — fren doğru, boşluğu dolduran yanlış

```
frenlenen SHORT'lar  ~ -0,4R / islem   (acilmadi)
acilan LONG'lar       -1,01R / islem   (HOME · PRL · DOS = -450,00 $)
```

Fren **kanıtlı** tarafı kapattı, **kanıtsız** taraf doldurdu. `NOTR-belirsiz long`
kapısının kendi metni: *"[2026-08-04 kullanıcı kararı; **ölçümle gerekçelenmedi**]"*.
→ Pencereye bağlı **ALTINCI** iş (`durum.md`).

### ⚠️ R İLE DOLAR ÇELİŞİYOR — hüküm yazılmadan çözülmeli

```
ilk yari     N=46  defter P&L +396,62  ort R -0,190
ikinci yari  N=46  defter P&L  -39,14  ort R -0,184
```

İki yarıda da ortalama R **negatif** ama ilk yarı dolar bazında **artı**. Sebep
`TP1_KISMI`: kısmi kâr alınıp kalan yarı −0,5R'de stop olunca kayıt `r=−0,5` gösterir,
pozisyon dolar bazında artıda kapanır (`BAS`: toplam **+13,36** ama `r=−0,51`).

**Ön-kayıt "yarılar R ya da yüzdeyle kıyaslanmalı" diyor — ama R kayıt başına ve kısmi
kârı görmüyor.** Hüküm yazılmadan önce hangi ölçünün kullanılacağı netleşmeli:
pozisyon-bazlı toplam mı, kayıt-bazlı R mi. **Bu bir ölçüt yumuşatma değil, ölçüt
belirsizliği** — sonuç görülmeden çözülmesi gerekiyor.

## ⭐ KAPI KARNESİ — canlı, pozisyon bazlı (2026-08-19, betimleyici)

`pozisyon_ozet.jsonl` N=117. **Betimleyici sayım, kontrollü kıyas DEĞİL** — kapılar farklı
piyasa anlarında tetikleniyor.

```
kapi              N   TP2%  ort P&L    toplam   MFE med  tutma  <8s pay
A+B              28    43%   +36,12  +1.011,41  +7,87%   10,7s    39%
NOTR              3     0%   +56,17    +168,52  +1,78%    6,0s    67%
MA50+ucuz        72    26%    -7,11    -511,83  +3,12%    2,7s    71%
NOTR-belirsiz    10     0%   -53,31    -533,13  +2,86%    2,3s    80%
AYI               4     0%  -174,99    -699,94  +2,81%    1,0s   100%
```

### Son sütun sıralamayı açıklıyor

`<8s pay` (ilk 8 saatte ölen oran) ile kârlılık **neredeyse monoton**:
`A+B` %39 → **+1.011** · `MA50+ucuz` %71 → **−512** · `NOTR-belirsiz` %80 → **−533** ·
`AYI` %100 → **−700**.

Bu, iki bulguyu bağlıyor: **kayıp 0-8 saat kovasında** (yukarıdaki Bekleyen satırı) ve
**kapılar o kovayı ne kadar doldurduklarıyla** ayrışıyor. `MFE` de aynı yönde: `A+B`
medyan **+%7,87**, diğerleri **+%2,8–3,1** — yani `A+B`'nin seçtiği kurulumlar gerçekten
hareket ediyor, diğerleri kıpırdayıp ölüyor.

### 🔴 ÜÇÜNCÜ BAĞIMSIZ TEYİT — `MA50+ucuz` negatif

```
2 yillik ham         -0,079   t=-4,05   (s.2790)
2 yillik fonlamali   -0,235%  t=-2,62   (ileri_rr kontrol kolu, 2026-08-19)
canli 72 pozisyon    -511,83  TP2 %26   (bu tablo)
```

`A+B` için de iki teyit: **+0,396R** (N=201, arşiv) ve canlı **+1.011,41** (N=28).

**Önemi:** `MA50+ucuz`'un savunması *"o ölçüm bir yeniden üretim, popülasyonu canlıdan
uzak"* idi. **Artık canlı popülasyon da aynı şeyi söylüyor** → pencereye bağlı işlerin
1. maddesinin savunması zayıfladı. Hüküm değil, **girdi**.

⚠️ **UYARILAR:** N dengesiz (28 / 72 / 10 / 4 / 3). **`AYI` ve `NOTR` satırları
anlamsız** — tek işlem tabloyu çevirir. `<8s pay` bir **teşhis göstergesi** olarak
saklanmaya değer: hızlı ölüm üreten kapı kötü seçiyor demektir.

## ⭐ ÖN-KAYIT — ASGARİ STOP EŞİĞİ (2026-08-19, KOŞTURMADAN ÖNCE yazıldı)

### Nereden çıktı — hipotez üretimi (aynı gün, ayrı iş)
20 "artıya geçip stop olan" (A) ve 20 "hedefe varan" (B) pozisyon **MFE bakımından
eşleştirilip** ilk +%2'ye ulaştıkları anda karşılaştırıldı (o anda sonuç belli değil →
totoloji yok). **11 alan** test edildi; medyan farkları yanıltıcı çıktı, sıra testi
(AUC) dokuzunu eledi:

```
alan                 medyan farki   AUC     hukum
islem_15                 +249%     83,2%   AYAKTA
stopa_uzaklik_pct         +41%     81,3%   AYAKTA
score / taker_60      +40 / +8%   64,1%   zayif
oi24                     +132%     57,9%   ELENDI (aykiri deger)
yas_saat                 +141%     47,9%   ELENDI (hic ayirmiyor)
rel3 · d_taker · comp        —    43-51%   ELENDI
```

Ve `stopa_uzaklik` **giriş anına kadar** izlendi: A medyan **3,38%** · B medyan **5,60%**
· AUC **77,4%**. Yani kazananlar **daha geniş stop'la** giriliyor.

### Hipotez
`asgari_stop_pct` eşiğini **2,0 → 3,0** yükseltmek (yani yapısal stop'u %3'ten dar olan
adayı reddetmek) **net getiriyi artırır.**

⚠️ **Bu bir stop GENİŞLETME değil, bir FİLTRE.** Stop'lar olduğu gibi kalır; yalnız dar
stoplu adaylar açılmaz. Risk-bazlı boyutlandırma zaten stop genişliğiyle ölçekleniyor,
yani işlem başına risk sabit — değişen **işlem sayısı ve kalitesi**.

### Eşik: **3,0** — ve neden gözlenen ayrım noktası DEĞİL
Gözlem A=3,38 / B=5,60 diyor. **Eşiği oraya koymak veriye uydurmak olurdu.** 3,0
seçildi çünkü: (a) mevcut eşiğin (2,0) yarım katı — anlamlı ama uç olmayan adım,
(b) **her iki grubun medyanının da ALTINDA**, yani gözlenen ayrımı taklit etmiyor,
yönü muhafazakâr sınıyor. Canlı dağılımda işlemlerin **%32'sini** eler.
**Eşik taraması (2,5 · 3,5 · 4,0 · 5,0 denemek) YASAK.**

### Ölçüm yöntemi
`ileri_rr.py` iskeleti — aynı giriş kümesi, tek fark filtre.
- Veri: `scratchpad/klines_1h_uzun/` (2 yıl · 566 sembol)
- Kümeler: `A_funding` (funding ≤ −0,05) ve `B_ma50ucuz` (fiyat ≤ $0,07 & MA50 ≥ %3,72)
- Kontrol: `ASGARI_STOP = 2,0` · Kural: `ASGARI_STOP = 3,0`
- Maliyet **fonlama + ücret + kayma DAHİL**
- İstatistik **`t_küme`**
- **İKİ ÖLÇÜ birden raporlanır:** işlem başına net % **ve** toplam (işlem sayısı düştüğü
  için ikisi ters yönde çıkabilir — o durum da bir sonuçtur)

### GEÇME ÖLÇÜTÜ — dördü de gerekli
1. **İşlem başına net getiri** kontrolden yüksek
2. **İKİ YARIDA DA** yüksek (A ve B ayrı ayrı)
3. **`t_küme` > +2,0**
4. Üç rejimin hiçbirinde ters işaret yok

⚠️ **EK ŞART:** işlem sayısı **%50'den fazla düşerse**, işlem başına kazanç artsa bile
KALDI sayılır — ölçüm hızı bu projede bağlayıcı kısıt ve akışı yarıya indiren bir
kazanç net değildir.

### BEKLENTİ — sonuç görülmeden yazıldı
**KARARSIZ bekliyorum, KALDI'ya yakın.** Gerekçe: (a) bu bir **giriş filtresi**, ve
projenin kazananları giriş tarafından çıktı — çıkış sıkılaştırmalarının 29/29 sicili
buraya uygulanmaz; (b) ama hipotez **N=25/21 anlık görüntüden** doğdu ve **11 alan
tarandı**, yani ikisinden biri gürültü olabilir; (c) %32 akış kaybı ek şartı zorlar.

⚠️ **ÇOKLU KARŞILAŞTIRMA UYARISI:** bu hipotez 11 alan taranarak bulundu. AUC %81
tek başına kanıt değil — 2 yıllık bağımsız veri hakemdir.

### Betik ve kayıt
Betik: `scratchpad/asgari_stop.py`. Ham çıktı: `scratchpad/asgari_stop_sonuc.txt`.
**Ölçüt metni sonuç görüldükten sonra DEĞİŞTİRİLMEDİ.**

### 🔴 SONUÇ — **KALDI** (2026-08-19, 565 sembol / 2 yıl)

```
A_funding    kontrol N=20.521  +0,006%    kural N=9.457  +0,142%   fark +0,135%
B_ma50ucuz   kontrol N= 4.340  -0,235%    kural N=2.487  -0,159%   fark +0,075%
```

| ölçüt | A_funding | B_ma50ucuz |
|---|---|---|
| **1.** işlem başına yüksek | ✅ +0,135% | ✅ +0,075% |
| **2.** iki yarıda da | ❌ A **−0,109%** / B +0,329% | ✅ +0,062 / +0,090 |
| **3.** `t_küme > +2,0` | ❌ **+0,47** | ❌ **−0,40** |
| **4.** rejimde ters işaret yok | ❌ AYI +0,615 · **BOĞA −0,301** | ❌ AYI +0,241 · **BOĞA −0,294** |
| **ek.** işlem düşüşü ≤%50 | ❌ **%53,9** | ✅ %42,7 |

**ÖN-KAYITLI BEKLENTİ TUTTU** — *"KARARSIZ, KALDI'ya yakın"* yazılmıştı.

### ⭐ AMA HİPOTEZİN ÇEKİRDEĞİ DOĞRULANDI — elenen dilim ölçüldü

```
stop 2,0-3,0 arasi islemler (kuralin ATTIKLARI):
  A_funding    N=11.064   -0,109%   t=-2,43
  B_ma50ucuz   N= 1.853   -0,335%   t=-3,14
```

**Dar stoplu işlemler gerçekten kötü** — ikisi de anlamlı negatif. AUC bulgusu (%81,3)
yön olarak **doğruydu.**

**Kural neden yine de kaldı:** onları atmak akışın yarısını da götürüyor ve geriye kalan
iyileşme **yarılarda ve rejimlerde tutmuyor**. `A_funding`'in ilk yarısında kural işi
**daha kötü** yapıyor (−0,398 vs −0,289). 2. ölçüt tam bunu yakalamak için vardı.

**Ders:** *"atılan dilim kötü"* ile *"atmak iyi"* aynı şey değil. Bir alt kümenin negatif
olması, onu çıkarmanın kalanı iyileştirdiği anlamına gelmiyor — kalanın da tutarlı olması
gerekiyor.

### 🔴 DÖRDÜNCÜ TEYİT — `MA50+ucuz` filtreyle de kurtulmuyor
Dar stopluları atınca **−0,235% → −0,159%**: iyileşiyor ama **hâlâ negatif**.
Bu kapı için dördüncü bağımsız negatif ölçüm (ham · fonlamalı · canlı 72 poz · bu).

## ⭐ ÖN-KAYIT — KATILIM FİLTRESİ (`islem_x`) (2026-08-19, KOŞTURMADAN ÖNCE yazıldı)

### Nereden çıktı
Aynı gün yapılan hipotez taramasında **en güçlü ayırıcı** buydu: ilk +%2 anında
`islem_15` (15 dk işlem sayısı) **AUC %83,2** — kazananlarda 11.706, kaybedenlerde 3.353.

⭐ **Kritik ayrıntı:** `ort_islem_usdt` (ortalama işlem BÜYÜKLÜĞÜ) **hiç ayırmıyor**
(AUC %51,1). Yani işlemler daha *büyük* değil, daha *çok*. Bu, "geniş katılım" ile
"birkaç büyük emir" arasındaki farkı ölçen **bağımsız bir eksen** — fiyat geometrisinde
görünmeyen bilgi.

### Hipotez
Giriş anında **katılımı kendi normalinin altında olan** adayı reddetmek net getiriyi
artırır.

`islem_x = n(giriş barı) ÷ medyan(n, önceki 48 bar)`

⚠️ **Neden GÖRELİ:** mutlak işlem sayısı **büyüklük vekilidir** (büyük coin = çok işlem).
Mutlak eşik katılımı değil coin boyutunu seçer. Sembolün kendi tabanına oranlanmalı.

### Eşik: **1,0** — sıfır serbestlik derecesi
```
gozlenen dagilim (N=12.984 giris olayi):
  %10  0,74   %25  0,97   %50  1,33   %75  1,97   %90  3,22
eleme:  1,0 -> %27   ·   1,2 -> %42   ·   1,5 -> %59   ·   2,0 -> %76
```
**1,0 ayarlanmış bir eşik değil, TANIMSAL sınır**: *"hareket, o sembolün kendi
normalinin altında katılımla oluşmamış olsun."* Başka gerekçe gerektirmiyor.
1,5 ve üstü zaten **kendi ek şartımla** (>%50 eleme → KALDI) dışlanmış durumda;
1,2 keyfî olurdu. **Eşik taraması YASAK.**

### Ölçüm yöntemi
`asgari_stop.py` iskeleti — alt-küme testi, aynı giriş kümeleri
(`A_funding` · `B_ma50ucuz`), aynı mekanik (A-stop · %10 hedef · 72s ·
maliyet + **fonlama dahil**), `t_küme`.

⚠️ **ÇÖZÜNÜRLÜK SINIRI — kayda geçiyor:** gözlem **15 dakikalık**, 2 yıllık veri
**saatlik**. Yani ölçülen şey uygulanacak şeyin **vekili**. Geçse bile canlıda
15 dk çözünürlükle yeniden doğrulanmalı.

### GEÇME ÖLÇÜTÜ — dördü de gerekli + ek şart
1. İşlem başına net getiri kontrolden **yüksek**
2. **İKİ YARIDA DA** yüksek
3. **`t_küme` > +2,0**
4. Üç rejimin hiçbirinde ters işaret yok
5. **EK:** işlem sayısı düşüşü **≤%50** (ölçüm hızı bağlayıcı kısıt)

### BEKLENTİ — sonuç görülmeden yazıldı
**KARARSIZ, KALDI'ya biraz yakın.**
- **Lehte:** bu bir **giriş** filtresi ve projenin dört kazananı da giriş/rejim tarafından
  çıktı (çıkışın 30/1 sicili buraya uygulanmaz). Ayrıca sinyal, `ort_islem_usdt`'nin
  ayırmaması sayesinde **boyuttan arınık** — gerçek bir katılım ölçüsü.
- **Aleyhte:** hipotez **N=25/21**'den ve **11 alan taranarak** doğdu; kardeş aday
  (`stopa_uzaklik`, AUC %81,3) **aynı gün KALDI**. İkisinden birinin gürültü olma
  ihtimali baştan yazılıydı. Ayrıca çözünürlük vekil.

### Betik ve kayıt
Betik: `scratchpad/katilim_filtresi.py`. Ham çıktı: `scratchpad/katilim_filtresi_sonuc.txt`.
**Ölçüt metni sonuç görüldükten sonra DEĞİŞTİRİLMEDİ.**

### 🟡 SONUÇ — **KALDI**, ama ilk kez İKİYE AYRILDI (2026-08-19)

```
A_funding    kontrol +0,006%   kural -0,007%   fark -0,013%   <-- TERSINE
B_ma50ucuz   kontrol -0,235%   kural -0,166%   fark +0,069%
```

**`A_funding` — hipotez tersine döndü.** Elenen dilim (`islem_x < 1,0`, N=6.372)
**+0,035%** yani hafif POZİTİF; filtre iyi işlemleri eliyor. Dört ölçüt de başarısız.
**Mekanizma anlaşılır:** `A+B` zaten *"short'lar kalabalık"* seçiyor — kalabalık zaten
yüksek katılım demek. Filtre orada **fazlalık**.

**`B_ma50ucuz` — beş ölçütün DÖRDÜNÜ geçti:**

| ölçüt | sonuç |
|---|---|
| 1. işlem başına yüksek | ✅ +0,069% |
| 2. iki yarıda da | ✅ A +0,113 / B +0,028 |
| 3. `t_küme > +2,0` | ❌ −0,49 |
| 4. rejimde ters işaret yok | ✅ AYI +0,049 · BOĞA +0,036 · NOTR +0,078 — **üçü de artı** |
| 5. işlem düşüşü ≤%50 | ✅ %16,3 |

Attığı dilim gerçekten kötü: **N=709 · −0,587% · t=−2,54**. `MA50+ucuz`'da
fonlama/kalabalık terimi **yok** → filtre oraya gerçek bilgi katıyor.

### ⚠️ ÖLÇÜT KUSURU — kabul ediliyor, DÜZELTİLMİYOR (D/9)

**3. ölçüt (`t_küme > +2,0`) ALT-KÜME testi için iyi tanımlanmamış.**
`ileri_rr`'de kollar **eşleşmişti** → farkın t'si hesaplanabiliyordu. Burada kural kolu
kontrolün **alt kümesi** → eşleşmiş fark yok; raporlanan `t_küme` her kolun **mutlak
getirisinin** t'si, *"fark anlamlı mı"* sorusunun cevabı **değil**.

**Ölçüt metni değiştirilmedi**; yazıldığı gibi okununca `B_ma50ucuz` **KALIYOR**.
⚠️ Aynı kusur **`asgari_stop` testinde de vardı** — ikisi de bu ölçütle okunmalı.
**Sonraki alt-küme ön-kayıtlarında iki-örneklemli istatistik belirtilmeli.**

### Bunun anlamı — "veride bilgi yok" cevabı artık verilemez
Bugün ilk kez bir **katılım** sinyali dört ölçütü geçti, ve geçtiği yer **tesadüfi değil**:
zayıf kapıya bilgi katıyor, güçlü kapıda fazlalık. ⚠️ Yine de **iki küme test edildi,
biri tuttu** — bu bir alt-grup bulgusudur, çoklu karşılaştırma sayılır. Kural DEĞİL.

## 🔍 DÖRT BOŞLUK — "dönüş işaretini neden bulamıyoruz" (2026-08-19, çerçeve)

**Ortak kusur:** 2026-08-19'da test edilen üç şeyin **üçü de TEK ANIN fotoğrafı**:
`ileri R/R` (hedefe/stopa mesafe) · `asgari stop` (giriş anı) · `islem_x` (giriş barı).
**Ama dönüş bir an değil, bir DİZİDİR** — hareket yavaşlar, agresör döner, hacim karşı
tarafta geri gelir. Tek kareye bakıp "bu kare dönüş mü" diye sorduk.

| # | boşluk | neden önemli | geriye-test edilebilir mi |
|---|---|---|---|
| **1** | **Devamın BAŞARISIZLIĞI ölçülmedi** — "en son ne zaman YENİ UÇ yapıldı" (ATR'ye normalize). Çalışan SHORT yeni dipler yapar; dönüş, **yeni dip yapmayı bıraktığında** başlar. Ölçtüğümüz hep *seviye*, bu bir *dizi* özelliği | En güçlü aday; "duraklama mı dönüş mü" sorusunu doğrudan hedefliyor | ✅ saatlik veriyle |
| **2** | **Fonlama saatleri** — fonlama 8 saatte bir SABİT saatlerde kesiliyor (00/08/16 UTC); kalabalık pozisyonlar tam o anlarda tasfiye olur. Dönüşler oralarda kümeleniyor mu? **Bugünkü bulguyla örtüşüyor: kayıp 0-8 saat kovasında = tam bir fonlama periyodu** | Hiç sorulmadı; **zamana bağlı kural** hiç denenmemiş sınıf | ✅ `funding_gecmis` damgaları var |
| **3** | **Sektör/breadth bağlamı** — `rel3` (coin vs BTC) bakıldı, ayırmadı. Sorulmayan: **bütün ucuz altcoin'ler aynı anda mı sıçradı?** Piyasa geneli sıçrama geçici, coine özel alım kalıcı | `piyasa_yapisi.py` breadth topluyor ama pozisyonlarla **hiç birleştirilmedi** | ⚠️ kısmen (log 06-26'dan) |
| **4** | **Bekleyen likidite** — elimizdeki her değişken *olmuş bitmiş işlemlerden* türüyor (hacim · işlem sayısı · taker · OI). Hiçbiri **emir defterinde bekleyen** boyutu ölçmüyor. Dönüş tam orada olur: agresif akış duran boyutla karşılaşır | `defter_derinlik` 17 Ağu'da **yalnız girişe** eklendi, sürekli değil | ❌ **emir defteri geçmişi YOK** → yalnız ileriye |

### ⚠️ VE DÜRÜST İHTİMAL: temiz bir dönüş işareti OLMAYABİLİR

Bugünkü sonuçlar bunu **dışlamıyor**. `A_funding`'de katılım filtresi **tersine** döndü
(aradığımız bilgi orada yok, hatta ters). Ve `t_küme` değerleri sürekli düşük çıkıyor —
bulduğumuz sinyaller **az sayıda sembolde kümeleniyor**, yani genel değil. Bu projede
30 çıkış varyantı ve 8 oynaklık varyantı zaten aynı duvara çarptı.

**Eğer dönüş işareti yoksa doğru cevap onu aramak değil, dönüşe DAYANIKLI olmaktır:**
daha geniş stop · daha az pozisyon · daha iyi kapı. Bugünkü kapı karnesi de bunu
fısıldıyor (`A+B` %39 hızlı ölüm · `MA50+ucuz` %71).

**Sıra önerisi:** önce **2** (en ucuz, en spesifik, 0-8 saat bulgusuyla örtüşüyor),
sonra **1** (dizi özelliği). 3 ve 4 pahalı; ilk ikisinin sonucuna göre.

### ❌ BOŞLUK 2 (fonlama saatleri) — TARANDI, BULGU YOK (2026-08-19)

Betimleyici tarama (**ön-kayıt değil**, hipotez üretimi): girişin fonlama döngüsündeki
konumu (0 = kesim saati 00/08/16 UTC) × net getiri, 565 sembol, faz kaydırmalı örneklem.

```
konum   TUM N   ort%     A_funding        B_ma50ucuz
  0      2649  +0,075    +0,162 EN IYI    -0,404 EN KOTU
  3      3085  -0,176    -0,177           +0,050
  6      3312  +0,002    -0,034           +0,260 EN IYI
```

**Kural YAZILMADI. Üç sebep:**
1. **İki kapı ZIT yönde** — `konum 0` A'da en iyi, B'de en kötü. Gerçek mikroyapısal
   etki olsaydı ikisi de aynı yönde olurdu. **Zıt işaret = gürültü imzası.**
2. **Yayılım gürültü seviyesinde:** SE 0,105–0,239; gözlenen yayılım **2,4–3,0 × SE**.
   **8 kova × 2 kapı = 16 karşılaştırma** → şansla beklenen en büyük sapma ~2,5 × SE.
3. `+0,162`'ye bakıp kural yazmak **"en iyi hücreyi seçmek"** olurdu.

### ⚠️ ÖRNEKLEME KUSURU BULUNDU — `SEYRELT=24` faz kilitliyor

İlk koşumda `konum 1` tek başına **23.886 olayın 14.717'sini** taşıyordu. Sebep:
`SEYRELT = 24` **tam 24 saat**, ve `klines_1h_uzun` dosyalarının **hepsi aynı zaman
damgasıyla indirilmiş** → her sembolde girişler **aynı UTC saatine** düşüyor.
Sembol başına rastgele faz kaydırmayla düzeltildi (kovalar 2.300–3.300'e dengelendi).

🔴 **Bu kusur `SEYRELT=24` kullanan HER ölçümü ilgilendirir** — `ileri_rr` ·
`asgari_stop` · `katilim_filtresi` dahil. **Saat/zaman boyutu olmayan sorularda
zararsız**, ama **zamanla ilgili her ölçümde faz kaydırma ŞARTTIR.**

### ❌ BOŞLUK 1 (devamın başarısızlığı) — KARIŞTIRICIYA YENİLDİ (2026-08-19)

*"Son yeni uçtan bu yana geçen süre"* — SHORT'ta yeni dip yapmayı bırakmak dönüşün
başlangıcı mı? İlk ölçüm noktası **dejenereydi** (+%2'ye ilk ulaşma anında SHORT zaten
yeni dip yapıyor: 11.340 olayın 10.200'ü "0 bar"). **Sabit zamana** (12. saat) taşındı:

```
son yeni dip     N      HEDEFE varma    o anki kar%
0-1 bar      2850        %48,0          +4,19
2-4 bar      1754        %42,2          +3,45
5-8 bar      1424        %40,2          +3,02
9+ bar        426        %36,2          +2,46
```

**Mükemmel monotonik, 11,8 puanlık yayılım.** Ama sağ sütun da monotonik →
karıştırıcı kontrolü yapıldı (kâr sabit, süre değişken):

```
kar bandi   |  0-1 bar      2-4 bar      5+ bar    |  yayilim
  1-3       |  948 %28,8   834 %31,1  1150 %31,1  |  -2,3 puan
  3-5       |  969 %47,9   566 %45,8   465 %44,1  |  +3,8 puan
  5+        |  933 %67,5   354 %63,0   235 %69,4  |  -1,8 puan
```

**11,8 puan → 2-4 puana iniyor ve işaret bantlar arasında DÖNÜYOR.** Sinyal
*"ne kadar kârdayım"*ın vekiliymiş; o zaten biliniyor.

🔴 **DÖRDÜNCÜ KEZ AYNI DUVAR.** Kütüğün kendi notu: *"ölçülen her şey **seviye** idi ve
'erken fiyat hareketinin başka bir ifadesi' çıktı."* **Dizi** sandığım şey de seviyenin
kılığıymış. Aynı ölüm agresör dengesi ölçümünde de yaşandı (2026-08-17).

### ❌ POZİSYON KOMPOZİSYONU (`top_ls − glob_ls`) — BULGU YOK (2026-08-19)

**Neden denendi:** ölçtüğümüz her şey *tek bir banttan* (Binance perp'te gerçekleşmiş
işlem) türüyor — bu yüzden hepsi fiyatın başka ifadesi çıkıyor. `glob_ls` **toplanıyor,
arşivlenıyor, ve hiçbir karar fonksiyonunda okunmuyor** (`grep` → testbot 0 · radar 0).
`smart` yalnızca `top_ls`'in eşiklenmiş hâli (`>=1,2 LONG · <=0,83 SHORT`). Fark ise
**kimin hangi tarafta olduğunu** söylüyor — farklı bilgi sınıfı, ve **bedava**.

Ham +24s getiri (arşiv, 8 hafta, 37.192 olayın 10.183'ü eşleşti):

```
ayrisma        N      +24s ort%   medyan%
<-0.4        2541      -0,726    -1,007
-0.4..-0.1   1873      +0,359    -0,223   <-- ort/medyan CELISIYOR
-0.1..+0.1   1284      -0,937    +0,151
+0.1..+0.4   1619      -0,491    +0,225
>+0.4        2866      -0,590    -0,888
```

Monotonluk yok; **iki uç da negatif** (yön yorumu ölür); ortalama/medyan çelişiyor
(aykırı değer sürüklemesi). Karıştırıcı kontrolü (chg24 sabit) da tutarsız:
`<-0,4` düşen bantta en iyi, yükselende en iyi, **yatayda en kötü**.

⚠️ **Sınırlar:** %27 eşleşme oranı (arşiv örneklemesi düzensiz) · 8 hafta · tek rejim.
**Ön-kayıt YAZILMADI** — betimleyici tarama geçilemedi.

### 🟡 MUM ŞEKLİ (reddetme) — KARIŞTIRICIDAN SAĞ ÇIKTI ama GEÇMEDİ (2026-08-19)

Trader'ın *"mum reddetti"* dediği şey: son 3 barın ortalama kapanış konumu
`(c−l)/(h−l)`. SHORT için **yüksek = tepeye yakın kapatıyor = alıcılar reddediyor.**
Ölçüm 12. saatte, artıdaki pozisyonlarda.

```
kapanis konumu     N      HEDEFE varma
dusuk (<0,35)    1676        %48,9
orta             4214        %42,9
yuksek (>0,65)    563        %36,8      ham fark 12,1 puan = 5,1 SE
```

**Karıştırıcı kontrolü (kâr sabit):**

```
kar bandi | dusuk       orta        yuksek     | fark    SE   kac SE
  1-3     | 611 %31,6  1980 %30,1   340 %30,0  |  +1,6   3,1    0,5
  3-5     | 500 %45,4  1340 %47,3   160 %41,9  |  +3,5   4,5    0,8
  5+      | 565 %70,6   894 %64,8    63 %60,3  | +10,3   6,5    1,6
TABAKALI (kar bandlariyla agirlikli):           |  +3,3   2,4    1,4
```

### ⭐ NEDEN BU "ÖLDÜ" DEĞİL — ayrım kütüğe giriyor

| | *son yeni uç* (aynı gün) | *mum şekli* |
|---|---|---|
| ham | monotonik 11,8 puan | monotonik 12,1 puan |
| kâr sabitlenince | **İŞARET DÖNDÜ** (−2,3 / +3,8 / −1,8) | **İŞARET KORUNDU** (+1,6 / +3,5 / +10,3) |
| birleşik | gürültü | **+3,3 puan · 1,4 SE** |

İşaretin bantlar arasında dönmesi **gürültünün imzasıdır**; burada üç bandın üçünde de
aynı yön (şansla 1/8) ve **etki kârla birlikte büyüyor** (mekanizma önerisi: pozisyon
hedefe yaklaştıkça reddetme sinyali ağırlık kazanıyor — ⚠️ bu post-hoc hikâye, ölçüm değil).

### ⭐⭐ LONG SİMETRİ TESTİ — tahmin KOŞTURMADAN ÖNCE yazıldı, TUTTU

**Neden yapıldı:** iki amaç birden — (a) N artırma denemesi, (b) sinyalin artefakt olup
olmadığının **keskin testi**. Mekanizma gerçekse LONG'da **ters** yönde çalışmalı
(yüksek kapanış = alıcılar kazanıyor = LONG için **iyi**). Aynı yön çıksaydı **artefakt**
olurdu.

Kurulum: aynı evren, **kapısız** LONG girişleri, aynalanmış mekanik (stop aşağıda,
hedef +%10), 12. saatte artıdaki pozisyonlar. N=13.818 (SHORT'un iki katı).

```
                 yuksek kapanis konumu       ham fark
SHORT              %36,8  <  %48,9           -12,1 puan   (yuksek = KOTU)
LONG               %47,1  >  %36,0           +11,1 puan   (yuksek = IYI)
```

🟢 **YÖN TAM TERSİNE DÖNDÜ ve büyüklükler neredeyse simetrik.** Tahmin tuttu →
**bu bir hesaplama artefaktı DEĞİL, gerçek bir piyasa mekanizması.**

### 🔴 AMA KARIŞTIRICI KONTROLÜ İKİSİNİ DE ELİYOR

```
                tabakali (kar sabit)   kac SE
  SHORT              +3,3 puan          1,4
  LONG               +0,84 puan         0,55     (bandlar: +1,1 / -2,3 / +7,2)
```

LONG'da işaret bantlar arasında **tutarsız** da (orta bant ters). İkisi de eşiğin altında.

### HÜKÜM: **ÖN-KAYIT YAZILMADI** — mekanizma GERÇEK, sinyal ZAYIF

Mumun şekli gerçekten *"kim kazandı"* bilgisini taşıyor — yön simetrisi bunu kanıtlıyor.
Ama taşıdığı bilginin **neredeyse tamamı zaten kârda kodlanmış**; bağımsız kalan kısım
1,4 ve 0,55 SE.

### ⚠️ N ARTIRMAK KURTARMIYOR — bu test aynı zamanda o sorunun cevabı

LONG testi **N=13.818** ile SHORT'un (N=6.453) iki katıydı ve sinyal **daha zayıf** çıktı
(0,55 vs 1,4 SE). Yani daha çok veri sinyali güçlendirmiyor, **daha kesin biçimde zayıf**
gösteriyor. *"N biriktiğinde tekrar bak"* beklentisi bu ölçümle **büyük ölçüde düştü**.

### ⭐ KÜTÜĞE GİREN ASIL ŞEY — yeni ve ucuz bir geçerlilik testi

**"Yön simetrisi mekanizmayı doğrular ama büyüklüğü kurtarmaz."**

Bu ayrım bugün ilk kez uygulandı ve iki farklı ölüm biçimini ayırıyor:

```
1-6. hipotez  ->  isaret bandlar arasi DONUYOR      ->  GURULTU
mum sekli     ->  yon TAM SIMETRIK, buyukluk zayif  ->  GERCEK ama KULLANILAMAZ
```

Yeni bir aday çıktığında **ilk sorulacak test bu olmalı**: *"ters yönde ters çalışıyor mu?"*
Ucuz, keskin, ve artefaktı gerçek mekanizmadan ayırıyor. ⚠️ Ama **geçmesi yetmez** —
mum şekli geçti ve yine de kullanılamaz çıktı.

## BTC KIRILIMI — gözlem penceresi açıldı (2026-08-19) ⏳ ÖN-KAYIT, hüküm YOK

**Olay ölçüldü** (Binance perp, 1h): 44 günlük sıkışma kırıldı. Son 20 günün
kapanışları **62.792–64.928** aralığında, yalnız **%3,4 genişlik** — akümülasyon
iddiası veriyle doğrulandı. 08-19 **15:00 UTC** saatinde açılış 65.895 → tepe
**70.450** → kapanış 68.523; hacim **103.352 BTC**, önceki saatlerin **~30 katı**.
Gün içi tepe 44 günün tepesini **%5,3** aştı.

**Mekanizma — squeeze DEĞİL, yeni kaldıraçlı long:**

| gösterge | kırılım saati | okuma |
|---|---|---|
| OI | 105.230 → **110.212 BTC** (%+3,29) | **artıyor** — squeeze'de düşerdi |
| taker alış/satış | **1,42** (60.579 / 42.773) | agresif alıcı baskın |
| fonlama | +0,0016% → **+0,0100%** | long'lar ödemeye başladı |
| genişlik | perp'lerin **%72'si** artıda | piyasa geneli, tek coin değil |

**Dış katalizör** (web, tek kaynak değil — ölçüm değil *bağlam*): ABD Hazinesi'nin
uzun vadeli tahvil alım açıklaması → getiriler düştü → risk varlıkları yukarı.
Yanında spot BTC ETF'lerine ~**298 M$** net giriş (IBIT 160 M$, FBTC 112 M$) ve
~60 günlük dağıtımdan sonra balina tarafında birikime dönüş. ⚠️ **Bu satır haber
özetidir, ölçüm değildir; kural dayanağı yapılamaz.** Yerel olarak ölçülen tek şey
yukarıdaki tablodur.

**Neden bizi ilgilendiriyor:** bot **yapısal SHORT**. Kapanmış 121 pozisyonun
**111'i SHORT (%92)**; tezi `MA50+ucuz` = MA50'nin çok üstündeki ucuz coinleri
satmak, yani **ortalamaya dönüş**. Geniş bir melt-up bu tezin en kötü ortamıdır.
Kırılım saatinde `BIO` SHORT stop oldu (**−74,93**), ve bot kırılımdan *sonra*
`RSR` (19:01) ile `ZAMA` (19:09) SHORT'larını açtı — yani **olayı görmedi**.

**ÖN-KAYIT — sonucu görmeden yazıldı** (betik: `scratchpad/kirilim_gozlem.py`,
çıktı `scratchpad/kirilim_gozlem.jsonl`, 5 dk aralık):

- **H1** — Geniş melt-up'ta `MA50+ucuz` SHORT'ları daha sık stoplanır.
  **Ölçüt:** kırılım penceresindeki SHORT stop oranı, **tabanı ≥15 puan** aşarsa
  H1 desteklenir. **TABAN ŞİMDİ SABİTLENDİ: %68,2 (N=110)** → eşik **%83,2**.
- **H2** — Bot kırılımı görmez, short açmaya devam eder (yön seçiminde rejim
  koruması yok). **Ölçüt:** kırılımdan sonraki 24 saatte açılan **LONG payı <%20**
  ise H2 doğrudur.
- **BEKLENTİ:** H2'nin doğru çıkması kuvvetle muhtemel (`rejim_giriste` kaydediliyor
  ama yön seçimine **girmiyor**). H1 belirsiz — alt'lar BTC'den az yükselirse
  SHORT'lar kurtulabilir; nitekim ilk anlık görüntüde üç short net **+15,50** idi.

### SONUÇ — 12 saat, 145 anlık görüntü (2026-08-20 07:20'de kapandı)

🔴 **ÖNCE KENDİ ÖLÇÜTÜMÜN KUSURU: `STOP` ETİKETİ "KAYIP" DEMEK DEĞİL.**
H1'i *"SHORT stop oranı"* üzerine kurdum. Yanlış vekil: bu bot TP1'den sonra stopu
**takip ettiriyor**, yani `STOP` kaydı **kârda** da kapanabiliyor. Tabanda ölçtüm —
SHORT stop'larının **%20'si (74'ün 15'i)** kârla kapanmış, LONG stop'larının **%50'si**.
Yani "stop oranı" *öldürülme* ile *kâr kilitleme*yi tek kovaya atıyor.

**Düzeltilmiş ölçü — zararla kapanan SHORT oranı:**

| | N | zararla kapanan | oran |
|---|---|---|---|
| taban (kırılım öncesi) | 109 | 60 | **%55,0** |
| pencere | **5** | 5 | **%100** |

Ön-kayıtlı eşik (taban +15 puan) **her iki ölçüde de aşıldı**. ⚠️ **Ama N=5.**
Taban p=0,55 iken 5/5'in olasılığı **%5,0**; orijinal p=0,682 ile **%14,7**.
**Bu bir kanıt değil, bir gözlemdir.** H1 "geçti" diye yazmak, bu projenin
reddettiği davranış olur.

**H2 YANLIŞ ÇIKTI — beklentim tutmadı.** *"Bot kırılımı görmez, short açmaya devam
eder"* dedim ve *"kuvvetle muhtemel"* diye yazdım. Gerçek: kırılımdan sonra açılan
**13 pozisyonun 5'i LONG (%38,5)**, ölçüt <%20 idi. Bot yön değiştirdi.
*(24 saatlik pencere 08-20 18:00'de doluyor; eşiğin altına inmesi için kalan sürede
13 ardışık SHORT gerekir — pratikte çürütülmüş sayılır.)*

**ASIL BULGU — yön her şeydi, ve LONG'lar pencereyi kurtardı:**

| yön | N | sonuç | ayrıntı |
|---|---|---|---|
| SHORT | 5 | **−368,74** | 5/5 zararda stop, hepsi ≈ **−1,02R** |
| LONG | 4 | **+423,53** | 4/4 "stop" ama **dördü de kârda** (TP1 + takip eden stop) |

Realize **+87,95**; açıklarla birlikte **+149,56**. Etkin kasa **9.587,47 → 9.779,54**
(**+192,07**). Yani bot melt-up'ta **kazandı** — short olmasına *rağmen* değil,
**açtığı LONG'lar sayesinde.**

**Piyasa bağlamı (145 anlık görüntüden):** BTC 68.631 → 69.343. Perp'lerin yükselen
payı %73 → **%81**, ama BTC'yi geçen pay yalnız %8 → **%17**. Yani alt'lar yükseldi
*ama BTC'den az* — BTC pay kazanmaya devam etti. `btc_pay` freninin aradığı hâl tam
buydu ve frenlenmiş olması gereken 5 SHORT'un 5'i de zarar etti (−368,74).
⚠️ **Frenin haklılığı bununla KANITLANMADI** — N=5, ve aynı pencerede LONG'lar
daha çok kazandırdı. Fren yalnız SHORT bacağını kapatıyor, LONG'lara dokunmuyordu.

**ÇIKARILMAYAN KURAL:** tek kırılım **N=1 olaydır**. Ne "melt-up'ta short açma" ne
"fren geri açılsın" hükmü bu veriden çıkarılamaz. İkinci bir kırılımda sınanmadan
yazılmaz. Kaydedilen: **ölçüt tasarımı dersi** (aşağıda) ve rakamlar.

**DERS — vekil değişken seçilirken etiketin ANLAMI doğrulanır.** `STOP` alanını
"kayıp" sandım; kodu değil adı okumuşum. Bu, `r` alanının kısmi kârı görmemesiyle
(`CLAUDE.md`) **aynı hata sınıfı**: defterdeki bir alanın adı, muhasebesini anlatmıyor.
Ön-kayıt yazarken **vekil değişkenin tabandaki dağılımına önce bakılmalıydı** — 30
saniyelik bir kontrol, ölçütü kurtarırdı.

⚠️ **HÜKÜM YOK.** Bu bir veri toplamadır. *"En iyi hücre seçilmez"* ve *"karıştırıcı
kontrolü zorunlu"* kuralları burada da geçerli: tek bir kırılım **N=1 olaydır**,
istatistik değil. İkinci bir kırılımda sınanmadan kural çıkarılmaz
(`CLAUDE.md` → *"bir sapmayı açıklayan formül ikinci bir zamanda sınanmadan..."*).

**BULGU DEĞİL — kayda geçirilen negatif:** giriş anındaki `chg24` dilimlerine göre
SHORT sonucu **monotonik değil** (`<5%` +6,63 · `5-8%` −4,48 · `8-12%` +9,42 ·
`>12%` −11,97 ort $). Dört hücre, sıra yok → **gürültü olarak okunmalı**, en iyi
hücre seçilmemeli. Yalnız `>12%` kovasının N=44 ile en büyük ve en kötü olması
(−526,69 $ toplam) ayrıca izlenmeye değer, **ama tek başına kural değildir.**

---

## ⭐ ÖN-KAYIT — `btc_pay` LONG PENCERESİ REJİMDEN BAĞIMSIZ MI? (2026-08-19, KOŞTURMADAN ÖNCE)

### Soru
`btc_pay` ölçümünün LONG bacağı (`UST + para durgun → LONG R +0,24 / +0,16`, 12 ay ·
37.271 gözlem · **gerçek holdout**) koda **`rejim_ad == "AYI"` kolunun içine** konmuş
([testbot.py:559](testbot.py#L559)). Kodun gerekçesi: *"AYI'da başka hiçbir long yolu
YOKTU."* — bu bir **ekleme** sebebi, **hapsetme** sebebi değil. Ölçümün kendi tanımı
piyasa seviyesinde: *"T-B **piyasa-seviyesi** bir İZİN penceresidir."*

**Sonuç:** bugün `bant=UST` ✅ `para=DURGUN` ✅ ama `rejim=NOTR` olduğu için **ölçülmüş
kapı kapalı**; bot ölçütü geçemeyen `notr_long_acik`'ı kullanıyor.

### ⚠️ Bu bir VEKİL ölçümdür — orijinali yeniden üretmez
Dayanak dosyalar (`PARA_SONUC.md` · `CIKIS_SONUC.md`) **kayıp**. Onun yerine iki gösterge
2 yıllık mumlardan **yeniden kuruldu** ve gerçek loglarla doğrulandı:

```
                          vekil tanimi                        r      isaret
btc_d_xs 3g degisim   BTC_3g - sepet MEDYAN 3g              +0,680    %72
para_rejim 7g         0,56*BTC_7g + 0,44*sepet MEDYAN 7g    +0,882    %86
```
Sepet: ≥8000 barlık, hacimce en büyük **60** sembol. ⚠️ **MEDYAN zorunlu** — ortalama
denendi, sıfıra yakın fiyatlı tokenlerde patladı (r düştü **+0,025**'e, aykırı −38.275).

**Geçse bile orijinal ölçümü doğrulamış olmaz** — yalnız *"rejim koşulluluğu"* sorusunu
cevaplar.

### DONDURULAN PARAMETRELER — getiriye BAKILMADAN kalibre edildi
```
UST_ESIK = 2,8755     gercek UST anlarinin %50'sini yakalar (N=92); tum saatlerin %26'si
DUR_ALT  = -2,8046    gercek PARA DURGUN anlarinin %80'ini kapsar (N=50)
DUR_UST  =  2,3766    tum saatlerin %32'si
```
**Bu üç sayı sonuç görüldükten sonra DEĞİŞTİRİLMEZ.**

### Ölçüm
**4 hücre:** `{AYI, NOTR} × {UST+durgun, diğer}`. LONG girişleri, **kapısız** (rejim ve
pencere dışında filtre yok), aynalanmış mekanik (stop aşağıda · hedef **+%10** · 72s),
**fonlama + ücret dahil**, `SEYRELT=24` + **sembol başına faz kaydırma**.

### GEÇME ÖLÇÜTÜ — dördü de gerekli
1. `NOTR × UST+durgun` net getirisi `NOTR × diğer`'den **yüksek** (lift NOTR'da da var)
2. Bu lift **iki zaman yarısında da** pozitif
3. **İKİ-ÖRNEKLEMLİ t > +2,0** — ⚠️ `t_küme` **kullanılmayacak**: alt-küme testinde
   tanımsız olduğu bugün (`asgari_stop` · `katilim_filtresi`) tespit edildi. Kullanılacak
   istatistik: `(ort₁−ort₂) / sqrt(sh₁² + sh₂²)`, sembol kümelenmesi ayrıca **raporlanır**
4. `AYI` lifti ile `NOTR` lifti **aynı işarette** — zıt işaret çıkarsa **rejim
   koşulluluğu DOĞRULANIR ve kilit haklıdır**

### BEKLENTİ — sonuç görülmeden yazıldı
**KARARSIZ.**
- **Lehte:** ölçümün kendi tanımı piyasa-seviyesi; kilidin gerekçesi ölçümden değil
  boşluğun yerinden geliyor.
- **Aleyhte:** bugün 7 hipotezin 6'sı öldü, 1'i yetmedi. Ve bu bir **vekil** (r=0,68 —
  iyi ama mükemmel değil); vekil gürültüsü gerçek bir farkı silebilir.

### Betik ve kayıt
`scratchpad/btcpay_rejim.py` · ham çıktı `scratchpad/btcpay_rejim_sonuc.txt`.
**Ölçüt metni sonuç görüldükten sonra DEĞİŞTİRİLMEDİ.**
**KARAR KAPSAMI (kullanıcı, 2026-08-19): YALNIZ ÖLÇÜM — kod değişikliği YOK.**
Kilidin açılıp açılmayacağı 21-22 tartışmasında (altıncı bağlı iş).

### 🟢 SONUÇ — **GEÇTİ** (2026-08-19, 565 sembol / 2 yıl / vekil)

```
          UST+durgun          diger              LIFT      2-ornekli t
AYI     N=  157  +0,122%   N= 9206  -0,222%     +0,344%       +0,73
NOTR    N= 3458  -0,079%   N=43439  -0,385%     +0,306%       +3,13
BOGA    N=  604  -1,857%   N= 8378  +0,185%     -2,043%       -9,95
```

| ölçüt | sonuç |
|---|---|
| **1.** `NOTR` lifti pozitif | ✅ **+0,306%** |
| **2.** iki yarıda da pozitif | ✅ A **+0,314** (t +2,42) · B **+0,298** (t +2,04) |
| **3.** iki-örneklemli t > +2,0 | ✅ **+3,13** — yarılar da eşiğin üstünde |
| **4.** `AYI` ve `NOTR` aynı işarette | ✅ +0,344 / +0,306 |

**DÖRDÜ DE GEÇTİ.** Ön-kayıtlı beklenti (*"kararsız"*) tutmadı — sonuç beklediğimden
temiz çıktı.

**Yorum:** `UST + para durgun` penceresinin LONG kenarı **NOTR'da da var** ve
`AYI`'dakiyle **aynı büyüklükte** (+0,306 vs +0,344). Kilidin `AYI`'ya hapsedilmesi
ölçümle desteklenmiyor — kodun gerekçesi (*"AYI'da başka long yolu yoktu"*) bir ekleme
sebebiydi, hapsetme sebebi değil. **Ölçüm bunu doğruladı.**

### 🔴 ÖLÇÜTTE OLMAYAN AMA EN ÖNEMLİ BULGU — BOĞA'da pencere ZARARLI

```
BOGA   UST+durgun -1,857%   ·   diger +0,185%   ->   LIFT -2,043%   t=-9,95
```

Boğa rejiminde pencere **kenarı tersine çeviriyor** ve etki **devasa** (t=−9,95,
iki yarıda da: −2,372 ve −1,713).

⭐ **Bu, orijinal ölçümün kendi uyarısının DOĞRULANMASI.** `_btc_pay_not` şöyle diyordu:

> *"SINIR: ölçülen 12 ayın TAMAMI düşen piyasa. **Yükselen piyasada ilişki tersine
> dönebilir — ölçülmedi.**"*

**Şimdi ölçüldü ve gerçekten dönüyor.** Yani kilit yanlış yerde ama **bir kilit gerekiyor**:
`AYI` değil, **`BOGA` HARİÇ**.

### ⚠️ KÜMELENME — ön-kayıtta "ayrıca raporlanır" denmişti

```
       N      ayri sembol   olay/sembol    t      t_kume (kaba ust-sinir)
AYI    157       137           1,1       +0,73    +0,68
NOTR  3458       495           7,0       +3,13    +1,18
BOGA   604       304           2,0       -9,95    -7,06
```

`NOTR`'da `t_küme = +1,18` — **eşiğin altında.** Ön-kayıt iki-örneklemli t seçtiği için
**ölçüt t üzerinden okunur ve geçmiştir**; ama gerçek değer **t ile t_küme arasındadır**
(`olcum_ortak`: *"KABA üst-sınır düzeltmesi"*). Bu, sonucu **zayıflatan** ama
çürütmeyen bir kayıt.

### ⚠️ Bu bir VEKİL ölçümdür
Orijinali yeniden üretmedi. `btc_d_xs` vekili r=+0,680 — vekil gürültüsü liftleri
**küçültme** yönünde çalışır, yani gerçek etki muhtemelen ölçülenden **büyük**. Ama
eşik kalibrasyonu da vekil üzerinden yapıldığı için hücre tanımları gerçek kapıyla
birebir aynı değil.

### ⚠️ KARŞI-OLGU KONTROLÜ — "kanıtlı kapı olsaydı son 3 gün farklı olur muydu?"

**HAYIR, hatta biraz daha kötü.** Kullanıcı sorusu üzerine ölçüldü (2026-08-19):

```
sym    bant   stage         skor   btc_pay penceresi        gercek sonuc
XPIN   ORTA   HAZIRLANIYOR  42,1   GECMEZ (bant, skor<45)   +79,17  <-- KAZANAN
HOME   UST    BASLIYOR      51,2   GECER                   -154,13
PRL    UST    BASLIYOR      68,5   GECER                   -147,56
DOS    UST    BASLIYOR      89,1   GECER                   -148,31
```

```
gercek (notr_long_acik)   +79,17 -154,13 -147,56 -148,31  =  -370,83
kanitli kapi olsaydi             -154,13 -147,56 -148,31  =  -450,00
                                                    FARK      -79,17
```

**Üç zararın üçünü de `btc_pay` penceresi de açardı** (bant UST · skor ≥45 · stage aktif ·
taker ≥1,0 · blowoff yok — hepsi sağlanıyor). **Ve tek kazananı kaçırırdı.**

**Neden şaşırtıcı değil:** iki kapı aynı kalite filtrelerini (blowoff · long_veto ·
taker ≥1,0) ve aynı `stage` şartını kullanıyor. Farkları küçük:
`notr_long_acik` → `smart == LONG`, eşik 40/45 · `btc_pay` → `smart != SHORT`, eşik hep 45
**artı** bant UST + para durgun.

### ⭐ DERS — bu kayıt ileride "keşke açsaydık" anlatısını önlemek için var

Ölçümün söylediği şey *"bu pencerede LONG işlem başına **+0,3 puan** daha iyi"*.
Bu **binlerce işlemde** anlamlı bir kenardır, **3 işlemde görünmez.** N=3'tür.

**Kilit açma kararı hâlâ doğru — ama doğru sebeple:** 2 yıllık ölçüm `t=+3,13` diyor,
son 3 gün değil. Aynı disiplin bugün yedi hipotezi eledi; burada da geçerli.

### Ne yapılmadı
**Kod değiştirilmedi** (kullanıcı kararı). Bu sonuç 21-22 tartışmasına **altıncı bağlı
işin girdisi** olarak gidiyor. Orada karara bağlanacak iki şey:
1. `btc_pay` LONG penceresi `AYI` kilidinden çıkarılıp **`BOGA` hariç** yapılsın mı?
2. Ölçütü geçemeyen `notr_long_acik` açık kalmaya devam etsin mi?

## 🔍 KAYIP DOSYA DENETİMİ (2026-08-19) — 45 atıf, **canlı kural taşıyan SIFIR**

**Neden yapıldı:** `btc_pay` ölçümünün dayanağı (`PARA_SONUC.md` · `CIKIS_SONUC.md`)
kayıp olduğu için bugün bir soru **cevaplanamadı** ve vekil kurmak gerekti. Aynı sınıftan
başka kaç açık var, sistematik tarandı.

**Yöntem:** `CLAUDE.md` · `durum.md` · `olcumler.md` · `fikir-defteri.md` içindeki tüm
`*.py` / `*.md` atıfları çıkarıldı, dosya sisteminde arandı (kök · `scratchpad/` · `arsiv/`).

### Sonuç — üç katmanlı triyaj

| katman | adet | durum |
|---|---|---|
| **Yanlış alarm** | 3 | `SKILL.md` → `.claude/skills/kripto/` altında **VAR**; `durumu.md` / `listesi.md` → tireli dosya adlarının parçaları |
| **Yalnız `fikir-defteri.md`'de** | 41 | Kronolojik laboratuvar defteri. **Sonuçlar kayıtlı, betikler yok.** Hiçbiri kütükte hüküm taşımıyor |
| **`olcumler.md`'de atıflı** | 2 | Aşağıda |

### İndeksi ilgilendiren iki dosya — ikisi de ÇÖZÜLDÜ

**1 · `PARA_SONUC.md` + `CIKIS_SONUC.md`** — `btc_pay` freni ve LONG penceresinin dayanağı.
🟢 **BUGÜN ÇÖZÜLDÜ.** İki gösterge 2 yıllık mumlardan yeniden kuruldu ve gerçek loglarla
doğrulandı (r=+0,680 / +0,882) → rejim koşulluluğu sorusu cevaplandı.

**2 · `f10_sezon_test.py`** — F10 sezon+hava rejim katmanı ölçümü.
🟢 **YÜK TAŞIMIYOR.** `f10` yalnız `evren.py`'de hesaplanıyor ve panelde gösteriliyor;
**`testbot.py` ve `radar.py` onu hiç okumuyor** (grep 0). Yani **hiçbir giriş/çıkış kararı
F10'a bağlı değil** — gözlem katmanı.

### 🟢 HÜKÜM: bugün itibarıyla **canlı bir bot kuralının dayandığı kayıp dosya YOK**

41 kayıp betiğin tamamı **rafta duran ya da sonucu kayıtlı** ölçümlere ait
(`ze_*` zemin etüdü · `bt_*` backtest altyapısı · `sk_*`/`st_*`/`sg_*` otopsiler ·
`f10_replay` · `fade_boga_test` · `beta_backtest` · `f4_basis_test` …).

**Kalan risk:** rafta duran bir fikir canlanırsa betiği yeniden yazılmalı. **Maliyet,
engel değil.**

### Tekrarı zaten engellendi
`fikir-defteri.md` s.617 (2026-08-10): *"Bu oturumdan itibaren ölçüm scriptleri projedeki
`scratchpad/` klasörüne yazılır ve commit edilir."* O tarihten beri uygulanıyor —
bugünkü 5 betiğin 5'i de commit'li.

### ⭐ ÇÖZÜM DESENİ — bugün kanıtlandı, tekrar gerekirse buradan uygulanır

> **Kayıp ölçüm, hayatta kalan veriden VEKİL kurularak ve hayatta kalan LOGLARLA
> doğrulanarak yeniden sorulabilir.**

Adımlar: (1) göstergeyi hayatta kalan ham veriden yeniden türet · (2) örtüşen dönemde
gerçek logla **korelasyon + işaret uyuşması** eşiği koy · (3) eşikleri **getiriye
bakmadan** kalibre et · (4) ön-kayıt yaz · (5) ölç.
⚠️ **Vekil orijinali yeniden üretmez** — yalnız belirli bir soruyu cevaplar; bu her
seferinde açıkça yazılır.

## Bekleyen — ölçülmedi

| soru | neden bekliyor |
|---|---|
| 🥇 **GECİKMELİ GİRİŞ — `ANINDA` yerine sıçrama bekle** (2026-08-19, önerilen) | ⚠️ **Yeni hipotez DEĞİL — çekmecede duran bulguyu uygulamak.** `SKILL.md:249`, arşiv analizinin doğrulanmış sonucu: *"anında-giriş short stop'a takılır → **giriş bounce'a**"*. Bot bugün `A+B` ve `MA50+ucuz`'da hâlâ `"ANINDA"` giriyor. **Doğrudan 0-8 saat kovasını hedefliyor** (aşağıya bak: kaybın TAMAMI orada, ve o pozisyonların %80'i önce artıya geçiyor). En büyük tek kaldıraç. Uygulanırsa **kapı değişikliğidir** → pencereyi etkiler |
| **0-8 SAAT KOVASI — hangi gözlenebilir değişken hızlı ölümü öngörüyor?** (2026-08-19) | `tutma<8s` N=76 **−3.734,18 $** · `8s+` N=41 **+3.169,22 $** — kayıp tek kovada. **Totoloji değil:** hızlı ölenlerin **%80'i önce artıya geçti** (MFE medyan +%1,77), yani kötü giriş değil kötü zamanlama. Giriş anında gözlenebilir ilk aday: **`ilk_hacim_usdt` 1.740.676 vs 807.227 (2,2 kat)** — ölenler iki katı hacimle giriliyor. ⚠️ **Büyüklük vekili olabilir** (büyük coin = çok hacim), ayrıştırmadan kural çıkmaz |
| **KAPASİTE — dolu turda ne kaçırıyoruz?** (2026-08-19) | Pencerede turların **%26,1'inde bot DOLU** (8/8) ve doluyken **giriş araması hiç koşmuyor** → neyi kaçırdığımızın **kaydı bile yok**. Önce ÖLÇ (dolu turda adayları yine tara ve arşive yaz, işlem açma), sonra "sıralama/değiştirme gerekir mi" sorusu anlamlı olur. Sayaç işi, davranış değişikliği değil |
| ⭐ **KAPI × FONLAMA — "her kapı kazandığı R başına ne kadar fonlama ödüyor?"** (2026-08-19, önerilen İLK iş) | **Hiç sorulmadı.** Fonlama brüt kârın **%33'ünü** alıyor ve isabet oranı başabaşın yalnız **+1,3 puan** üstünde — yani fonlamanın üçte birini kurtarmak, isabet oranını 3 puan artırmaya bedel. `A+B` **tanımı gereği** negatif funding seçiyor (ödemeyi *seçiyor*); `MA50+ucuz`'da fonlama terimi yok. Eğer R başına fonlama yükleri ayrışıyorsa **kapı sıralaması değişir**. Alan `funding_usdt` 2026-08-17'den beri kayıtlı → birkaç düzine yeni pozisyon yeter. ⚠️ **İnce ayar DEĞİL, muhasebe** — tek soru, tek cevap, çoklu karşılaştırma riski yok |
| **`btc_pay` LONG penceresi rejimden BAĞIMSIZ mı?** (2026-08-19) | Ölçüm `UST + para durgun → LONG R +0,24/+0,16` diyor ama kapı **AYI dalına** gömülü; NOTR'da erişilemiyor. Kodun kendi notu pencereyi *"T-B **piyasa-seviyesi** bir İZİN penceresidir"* diye tanımlıyor — coin seçmiyor, **rejim de seçmiyor olabilir**; AYI'ya hapsedilmesi keyfî bir daraltma olabilir. ⚠️ **Doğrulanamıyor:** dayanak dosyalar `PARA_SONUC.md` / `CIKIS_SONUC.md` **kayıp** (geçici oturum klasöründe yok oldu), ölçüm rejime koşullu muydu bilinmiyor. **Yeniden ölçülmeden genişletilmez** — 2 yıllık veri elde, betik yeniden yazılmalı |
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
| ⚡ **HTTP keep-alive / bağlantı havuzu** — ölçüldü, uygulanmadı | [evren.py:54](evren.py#L54) her çağrıda yeni bağlantı açıyor; keep-alive medyan çağrıyı **0,614 → 0,285 sn** (2,1 kat) indiriyor, medyan turu **298 → ~145 sn**. **Pencereye bağlı DEĞİL** — D/8: aynı uç noktalar, aynı sıra, aynı veri, aynı kararlar; yalnız socket yeniden kullanılıyor. Pencereye bağlı altı işin arkasında beklemesi gerekmiyor, ama derinliğin de önüne alınmadı. Ölçüm: yukarıdaki "ağ çağrısı bütçesi" bölümü |
| **Slipaj varsayımı tutuyor mu?** (emir defteri derinliği) — ⚙️ **veri 2026-08-17'den beri toplanıyor** | Alan `derinlik_giriste` işlem kaydında: `slipaj_pct` (notional defterin karşı tarafını yerken oluşan VWAP sapması) · `defter_usdt_20` · `yetersiz` (defter 20 seviyede tükendiyse slipaj **alt sınırdır**). `null` = ölçülemedi. Pozisyon başına **1 çağrı**, aday döngüsüne girmiyor. Ölçüm birkaç düzine pozisyon birikince ön-kayıtla yapılır. Bütün ölçümler slipajı **%0,02 varsaydı**; hiç doğrulanmadı ve A+B'nin sınırlar bölümü *"slipaj yok sayıldı; olaylar düşük hacimli coinlerde yoğunlaşıyor"* diyor. Gerçek paraya geçişte kenarı belirleyecek kalem bu. Giriş anında derinlik kaydı planlandı — **yalnız dolan pozisyonda**, reddedilen adaylarda değil (o, çağrıyı giriş arama döngüsünün içine sokar; tur süresi zaten 314–440 sn). ⚠️ **SINIR — şimdiden yazıldı:** yalnız dolan pozisyonda ölçmek **seçilim yanlı bir örneklemdir.** *"Bizim işlemlerimizde tuttu mu"* için doğru örneklem, yanlılık yok. *"Daha çok işlem yapsak da tutar mıydı"* için **yanlış** örneklem. İkincisine genişletmek isteyen bu cümleyi okumadan genişletmesin |
| **`ayna`'nın 177,84 $ equity–defter kayması** | Kaynağı bulundu (08-12 17:42 temizliğinde equity `başlangıç + defter P&L` ile, **funding'siz** yeniden kuruldu). **Kıyastan ÖNCE** düzeltilmeli ya da kıyasa dahil edilmeli, yoksa ayna-bot karşılaştırması yanlı başlar. Ayrıntı defterler bölümünde |

---

## Kütüğe girmemiş betikler

`scratchpad/` altında 59 ölçüm betiği var; yukarıda **~30'u** adlandırıldı. Kalanlar
ya yardımcı (veri indirme: `funding_indir.py`, `scalp_1m_indir.py`, `ze_veri.py`) ya
da defterde ayrı bir sonuç bölümü olmayan ara çalışmalar. Bir betiği kullanmadan önce
defterde karşılığı olup olmadığına bak; yoksa **sonucu yeniden üretilmeden
güvenilmez.**

### FREN GECIKMESI — btc_pay UST bandinin devreye girme/birakma mekanigi (2026-08-19)

**Tur:** tanimsal cozumleme (getiri olcumu DEGIL, on-kayit gerektirmez — hicbir esik
taranmadi, hicbir kural onerilmedi). **Betik:** `scratchpad/fren_gecikme.py`.
**Veri:** `btc_pay_log.jsonl`, 380 gun (2025-08-05 .. 2026-08-19), 377 karsilastirilabilir.

**Soru:** kullanici *"fren gecikmeli calisiyor, karar geldiginde cok gec"* dedi. Dogru mu?

```
UST gunu: 94 / 377  (%24.9)          <-- tasarim ust ceyrek %25, KALIBRASYON DOGRU

(1) DEVREYE GIRERKEN — 3g degisimini en cok hangi yastaki gunluk adim tasiyor
    bugunun kendi hareketi : 42  (%44.7)
    1 gun onceki           : 24  (%25.5)
    2 gun onceki           : 28  (%29.8)

(2) BIRAKIRKEN — fren kalktigi gun BTC payi ne yapmisti
    GERCEKTEN dustu        : 46 / 55  (%83.6)
    artti ama fren kalkti  :  9 / 55  (%16.4)   <-- referans yurumesi

UST serisi: 56 adet · medyan 1 gun · ortalama 1,7 · en uzun 4
Gunluk |adim|: medyan 0,1982 · %90 dilim 0,6709 · 08-18 sicramasi 0,3022 (%67 dilim)
```

**HUKUM: "fren GENEL OLARAK gecikmeli" onermesi DESTEKLENMEDI.** Vakalarin %44,7'sinde
bugunun kendi hareketiyle tetikleniyor, %83,6'sinda gercek dususle birakiyor, normal
omru **1 gun**. Gecikme SU ANKI seriye ozgu: 08-19'un 3g degisimi +0,4048'in +0,3022'si
08-18 adimindan tasiniyor, gunun kendi adimi +0,0658.

**Yan bulgu — 08-18 sicramasi olaganustu DEGIL.** 0,3022 gunluk adimlarin yalnizca
%67. dilimi; medyan gunluk adim 0,1982. Yani 3 GUNLUK degisim icin konan +0,287 esigi,
TEK tipik gunun hareketinin ~1,5 kati. Kapi dogasi geregi gurultulu — ama bu tasarim
geregi (ust ceyrek), kusur degil.

**Veri denetimi (ayni kosumda):** 380 gunde **eksik gun yok**; `kapsam` canli donemde
sabit 130 (geri-doldurulan tarihsel bolumde 105 -> 130 surukleniyor, seviye farki
belgelenmis −0,062 puan — 3 GUNLUK FARK aldigi icin sabit ofset sadelesir);
tek zamanlama sapmasi 2026-08-14 anlik goruntusu (03:32, digerleri 00:0x).

**Gizli kusur bulundu (aktif DEGIL):** `evren.btc_pay_akisi` donusunde
`"gun_farki": gun` — yani her zaman **3** yaziyor, +-1 gun toleransi 2 ya da 4 gunluk
bir kayitla eslesse bile. Kutukte eksik gun olmadigi icin tolerans **hic devreye
girmemis**; `onceki_gun` alani gercek tarihi tasidigi icin izlenebilir. Duzeltilmedi
(bota dokunmama).

**Karara etkisi:** kullanici bu bulguya RAGMEN freni ucuncu kez kapatti (21:40);
gerekcesi gecikme degil, *olcum penceresinin kapiya bagli kalmamasi*. Kayit `durum.md`.

### ON-KAYIT — FRENIN KENDISI (btc_pay SHORT bacagi) REJIMDEN BAGIMSIZ MI? (2026-08-19)

**KOSTURULMADAN ONCE YAZILDI VE COMMIT EDILDI.** Olcut metni sonradan
degistirilmez (D/9). Esik taranmaz, hucre secilmez.

**NEDEN:** `btc_pay` SHORT freni su an CANLI ve bugun uc kez elle degistirildi.
Freni kuran olcumun KENDI yazili uyarisi: *"SINIR: olcumun 12 ayinin tamami
DUSEN piyasa. Yukselen piyasada iliski tersine donebilir."* BTC 18-19 Agustos'ta
64,5k -> 69,5k kirilim yapti. Ayni gun olculen LONG bacaginda BOGA rejiminde
lift **−2,043% (t=−9,95)** cikti, yani isaret DONDU. **SHORT bacagi — yani
frenin kendisi — rejime gore HIC sinanmadi.** Bu on-kayit o boslugu kapatir.

**FRENIN IDDIASI (sinanan sey):** `bant == UST` iken SHORT kenari DUSUKTUR,
o yuzden SHORT girisi engellenmelidir. Orijinal olcum: UST ceyrek SHORT R
kesif −0,02 / sakli −0,03; ALT ceyrek +0,27/+0,16 (temel +0,06/+0,04).

**HIPOTEZ:** frenin iddiasi UC REJIMDE DE gecerlidir; ozellikle BOGA'da da
`UST` SHORT'lari `diger`den kotudur.

**VEKIL UYARISI:** dayanak dosya `PARA_SONUC.md` KAYIP. `btc_d_xs` 3g,
2 yillik mumlardan yeniden kuruldu (BTC 3g − sepet **MEDYAN** 3g), gercek
`btc_pay_log` ile dogrulandi: r=+0,680, isaret uyusmasi %72. **MEDYAN ZORUNLU**
(ortalama r=+0,025'e cokuyor). Bu olcum orijinali YENIDEN URETMEZ; yalniz
*"rejim kosulluluğu"* sorusuna cevap verir.

**DONDURULMUS PARAMETRE:** `UST_ESIK = 2.8755` — `btcpay_rejim.py`'de LONG
sinavi icin getiriye BAKILMADAN kalibre edilmisti; **aynen** kullanilir,
yeniden kalibre EDILMEZ. `para_durgun` kosulu YOK (fren onu kullanmiyor).

**OLCUM:** 6 hucre = {AYI, NOTR, BOGA} x {UST, diger}. **SHORT** girisleri,
botun A-varyanti stop, hedef −%10, ufuk 72s, **maliyet + FONLAMA dahil**,
`SEYRELT=24` + **sembol basina faz kaydirma**. Hucre basina asgari N=40.

**GECME OLCUTU — "fren BOGA'da da hakli" hukmu icin ucu de gerekli:**
1. `BOGA x UST` net getirisi `BOGA x diger`'den **DUSUK** (lift < 0)
2. Bu lift **iki zaman yarisinda da** negatif
3. **IKI-ORNEKLEMLI** t (alt-kume degil, ayrik kumeler) **< −2,0**

**TERS HUKUM — fren BOGA'da ZARARLIDIR:** lift > 0 **ve** iki-ornekli t > +2,0
**ve** iki yari da pozitif. Bu cikarsa fren `rejim != BOGA` ile sinirlandirilmali
onerisi 21-22 tartismasina tasinir (karar orada, burada DEGIL).

**BELIRSIZ:** ikisi de cikmazsa hukum "yetersiz" yazilir ve fren OLDUGU GIBI kalir.

**BEKLENTI (sonuc gorulmeden yaziliyor):** LONG bacaginin BOGA'da isaret
cevirdigi olculdu; SHORT bacaginda da cevirmesi MEKANIK OLARAK BEKLENIR
(ayni gostergenin iki yuzu). Ama bu beklenti bir kez daha yaniltabilir —
bugun 7 hipotezin 6'si oldu. Ayrica BOGA hucresinde N kucuk cikabilir.

**KARAR YETKISI:** bu olcum HICBIR kod degisikligi TETIKLEMEZ. Sonuc ne olursa
olsun karar 21-22 tartismasinda kullanicidadir.

**Betik:** `scratchpad/btcpay_fren_rejim.py` (bu on-kayittan SONRA yazilacak).

### SONUC — FRENIN KENDISI REJIMDEN BAGIMSIZ MI? (2026-08-19, on-kayit 43d2cf5)

**Betikler:** `scratchpad/btcpay_fren_rejim.py` (on-kayitli olcum) ·
`scratchpad/fren_bogakontrol.py` + `scratchpad/ay_kumeli_denetim.py` +
`scratchpad/tohum_kararliligi.py` (POST-HOC karistirici kontrolu).
**Islenen sembol:** 565.

#### On-kayitli olcut ne dedi

```
--- AYI    UST -1.498%  diger +0.250%   LIFT -1.748%   t=-15.33   fren HAKLI
--- NOTR   UST -0.336%  diger +0.323%   LIFT -0.659%   t=-12.62   fren HAKLI
--- BOGA   UST +0.196%  diger -0.621%   LIFT +0.817%   t= +6.07   fren TERS
           A yarisi +0.571 (t=+3.08) · B yarisi +1.064 (t=+5.50)
```

On-kayitli **TERS HUKUM**'un uc ölcutu de gecti -> *"fren BOGA'da ZARARLI"*.

#### KARISTIRICI KONTROLU BU HUKMU CURUTTU

**CLAUDE.md zorunlu kilar:** monotonluk/isaret tek basina yetmez. Soruldu:
*bu 2928 gozlem BAGIMSIZ mi?* **Degil.** Rejim epizotlari takvimde kumelenir;
BOGA hucresi 2 yilda yalnizca **6 ayrik ay** iceriyor.

```
BOGA ay lifti: 2024-10 -3.89 · 2024-11 -0.08 · 2024-12 +3.00
               2025-05 -0.26 · 2025-07 +1.20 · 2026-05 -0.29
pozitif 2/6 · ay ortalamasi -0.054 · medyan -0.171
BASKIN ay 2024-12 (katki +2784) ATILINCA -> lift -0.246%, t=-1.74  ISARET DONDU
AY-KUMELI t = -0.06                                                <-- GURULTU
```

**Ham +0,817%'in TAMAMI 2024-12'den geliyor.** On-kayitli *"iki yari"* olcutu
bunu YAKALAYAMADI cunku 2024-12 zaman ortasini **atliyor** — iki yariya da
ayni ay bulasti.

**AYNI KONTROL TUM HUCRELERE UYGULANDI** (yalniz hosa gitmeyeni elemek
suclamasini imkansiz kilmak icin) **ve UC TOHUMDA tekrarlandi:**

| olcum | rejim | ham lift | AY-KUMELI t (tohum 41 / 7 / 99) | hukum |
|---|---|---|---|---|
| SHORT (fren) | AYI | −1,75 | −2,95 / −4,01 / −3,29 | **AYAKTA** |
| SHORT (fren) | NOTR | −0,66 | −2,73 / −3,38 / −2,68 | **AYAKTA** |
| SHORT (fren) | BOGA | +0,82 | −0,06 / +0,06 / +0,26 | **GURULTU** (isaret bile sabit degil) |
| LONG | AYI | +0,34 | −1,09 / −2,27 / −1,50 | **GURULTU** |
| LONG | NOTR | +0,31→+0,10→+0,08 | +0,36 / −0,10 / +0,02 | **GURULTU** (saf sifir) |
| LONG | BOGA | −2,04 | −2,39 / −2,21 / −3,01 | **AYAKTA** |

#### HUKUM

1. **On-kayitli soru (fren BOGA'da zararli mi):** ham olcut gecti, karistirici
   kontrolu curuttu -> **BELIRSIZ.** On-kaydin kendi *belirsiz* dali uygulanir:
   **fren OLDUGU GIBI kalir, rejim sinirlamasi ONERILMEZ.**
2. **BEKLENMEYEN ve daha onemli bulgu — fren AYI ve NOTR'da GERCEK.** En sert
   testte (ay-kumeli, uc tohum, baskin ay atilarak) ayakta kaliyor.
   **Su anki rejim NOTR** (BTC 30g getirisi +4,83%, olcumun tanimi ±15).
3. 🔴 **BUGUN SABAHKI LONG KARARININ DAYANAGI COKTU.** *"21 Agustos'ta btc_pay
   LONG kilidi ACILACAK (BOGA HARIC)"* karari, LONG/NOTR lifti +0,306 (t=+3,13)
   bulgusuna dayaniyordu. Ay-kumeli bakista **t = +0,36 / −0,10 / +0,02** —
   saf gurultu. Ham lift bile tohuma gore **+0,306 → +0,098 → +0,080** oynuyor.
   **Karar 21-22'de yeniden acilmalidir.**
4. **LONG'un BOGA'da ZARARLI oldugu AYAKTA** (t −2,39/−2,21/−3,01, 0-1/4 ay
   pozitif). Yani kararin *"BOGA HARIC"* niteleyicisi dogruydu; *"AC"* kismi degil.

**NET: `btc_pay`'in SHORT bacagi gercek, LONG bacagi degil.** Ayni vekil, ayni
mekanik, ayni tohumlar — biri gorunuyor, digeri gorunmuyor.

#### KUSUR ITIRAFI — bu olcumun kendi hatalari

- 🔴 **On-kayitta IKI-ORNEKLI t belirttim, KUMELENMIS t degil.** "Alt-kume
  testinde t_kume tanimsiz" tuzagini bugun ogrenip on-kayda yazmistim; ama
  **ayrik kumelerde de kumelenme var** (takvim) ve onu atladim. Gozlem-t
  2928 korelasyonlu gozlemi bagimsiz sayiyor. Ust hukum bu yuzden gecti.
- 🔴 **Faz kaydirma TEKRARLANABILIR DEGIL.** `random.seed` modul duzeyinde;
  iki olcum ayni surecte kosunca akislar kayiyor. Ayni kod ayni gun
  LONG/NOTR icin +0,306 (t=+3,13) ve +0,124 (t=+1,31) uretti. Ay-kumeli
  hukumler uc tohumda sinandi ve **kararli**; ham gozlem-t **degil**.
  Duzeltme: faz sembol adindan TURETILMELI (`hash(sym) %% 24`), rastgele degil.
- **VEKIL siniri:** btc_d_xs vekili r=+0,680. LONG bacaginin gorunmemesi
  (a) vekilin cok gurultulu olmasindan ya da (b) orijinal LONG bulgusunun
  kucuk-orneklem eseri olmasindan olabilir; **bu olcum ikisini AYIRT EDEMEZ.**
  Ancak ayni vekil SHORT bacagini net goruyor — yani vekil bu buyuklukte
  bir etkiyi yakalayabiliyor. Kanit degil, isaret.

### KAPSAM DARALTMASI — NOTR hukmu BUGUNKU bolgeyi KAPSAMIYOR (2026-08-19 gece)

**Betik:** `scratchpad/notr_keskin.py`. **Tetikleyen:** kullanici itirazi —
*"BTC bir anda 70'e firladi, bu pek notr degil."* Rejim etiketi BTC'nin
**30 GUNLUK** getirisine bakiyor; bugun 30g **+5,11%** (NOTR) ama 3g **+8,95%**,
24s +6,41%. Sinuflandirici yavas — itiraz mesru.

**YONTEM (esik SECILMEZ):** NOTR gozlemleri, o andaki BTC 3 gunluk getirisine
gore **UCE** bolundu. Uc dilim de raporlanir; en iyi hucre secilmez. Istatistik
**AY-KUMELI** (ayni gece ogrenilen ders).

```
                                AY-KUMELI lift        t (tohum 41 / 7)
DUSUK  (BTC 3g < -2,3%)          -1,90 / -2,05     -2,99 / -3,40
ORTA                             -0,58 / -0,51     -1,16 / -1,24   gurultu
YUKSEK (BTC 3g > +0,9%)          -1,04 / -1,20     -2,47 / -3,26
```

Uc dilimde de isaret NEGATIF (fren yonunde). **AMA dilim bizi kapsamiyor:**

```
NOTR gozlemlerinin %99,3'u bugunkunden DUSUK bir BTC 3g getirisinde
dagilim: %10 -5,62 · %50 -0,75 · %90 +3,98 · %95 +5,51 · en yuksek +16,70
bugun:   +8,95                                          <-- %99,3 dilim
```

"YUKSEK" dilimi +0,9%'dan basliyor ve icindekilerin cogu %1-4 arasi.
**Bugunku durum o dilimin ortalamasi degil, UCU.**

**Gercekten bulundugumuz bolge (en yuksek %10, BTC 3g >= +3,98%):**

```
N=853/4348   ham lift +0,551%   <-- ISARET DONUYOR
             AY-KUMELI lift -0,592%   t=-0,79   9 ay, 4/9 pozitif   GURULTU
```

**HUKUM: bu bolgede kanit YOK.** Ham isaret donuyor, kumeli t sifira yakin,
aylar yari yariya. ⚠️ Bu *"fren zararli"* DEMEK DEGIL — 9 ay / N=853 ile ayirt
edecek guc yok. **Kanit yoklugu, yokluk kaniti degildir.**

**AYNI GECE YAZILAN HUKMUN KAPSAMI DARALIR (D/9 — eski metin SILINMEDI):**
*"Fren AYI ve NOTR'da GERCEK"* hukmu **AYAKTA**, ama ona eklenen isletme cumlesi
—*"su anki rejim NOTR, yani olcum frenin simdi calismasi gerektigini soyluyor"*—
**FAZLA ILERI GITTI.** Dogrusu: **olcum NOTR ORTALAMASINDA freni destekler;
bugunku gibi keskin-hareket kuyrugunda SUSAR.**

**Karara etkisi:** frenin 21:40'ta kapatilmasina yonelttigim itiraz ZAYIFLAR.
Olcum bugunku durumda ne "ac" ne "kapat" diyor. Karar (kullanici, olcum akisi
gerekcesiyle) OLCUMLE CELISMIYOR.

**Yontem dersi — kaydedilmeye deger:** bir hukum "X rejiminde gecerli" derken
**X'in HANGI bolgesinde bulundugumuz** ayrica sorulmalidir. Rejim etiketi genis
bir kumeyi tek adla anar; ortalamanin hukmu, o kumenin %99 diliminde otomatik
olarak gecerli DEGILDIR.

### 🔴 DÜZELTME — `chg24` BANT HÜKÜMLERİ MEKANİK YÜKLÜYDÜ, HAM GETİRİYLE YENİDEN (2026-08-20)

**Neden düzeltme:** kullanıcı sordu — *"bu ölçümlerin doğruluğuna güvenmemi
gerektirecek sebep ne?"* Doğrulandı: aynı 117 işlem benim replay mekaniğimle
**−2.400 $**, botun gerçek sonucu **−489 $**. Yani ölçüm başka bir sistemi tarif
ediyordu. `CLAUDE.md`'nin *ham → mekanik → portföy* sırası atlanmıştı.

**Betik:** `scratchpad/short_kayip/F_ham.py` — aynı bantlar **üç** mekanikle.

```
### LONG
bant      olcum          N       ay ort     ay-t   poz ay
-40..0    HAM        96523      -0.005    -0.01    12/25
-40..0    A-stop     24588      -0.112    -0.76    10/25
-40..0    trailing   24588      -0.011    -0.12    10/25

0..20     HAM        89429      -0.390    -0.90    10/25
0..20     A-stop     37525      -0.406    -4.11     4/25
0..20     trailing   37525      -0.210    -5.01     2/25

20..40    HAM         2353      +0.196    +0.19     9/24
20..40    A-stop      2301      +0.028    +0.14    11/23
20..40    trailing    2301      +0.091    +0.61    14/23

>40       HAM          678      +2.284    +0.77     8/15
>40       A-stop       677      +0.776    +1.43     9/15
>40       trailing     677      +2.379    +3.24    12/15

### SHORT
0..20     A-stop     21575      +0.014    +0.14    16/25
0..20     trailing   21575      -0.095    -2.26     6/25
>40       HAM          678      -2.284    -0.77     7/15
>40       A-stop       637      -1.661    -2.55     2/14
>40       trailing     637      -1.144    -2.29     3/14
```

#### DÜZELTİLEN HÜKÜMLER

| hüküm | eski | **düzeltilmiş** |
|---|---|---|
| `0..20 LONG` kötü | *"t=−4,11, sağlam"* | **yön AYAKTA** (üç mekanikte de negatif, −0,21…−0,41) ama **güven ŞİŞİKTİ** — ham t=**−0,90**, anlamlı değil |
| `>40 LONG` | *"öldü, t=+0,23 gürültü"* | 🔴 **YANLIŞ ÖLDÜRÜLDÜ.** Ham **+2,284**, trailing **+2,379 (t=+3,24, 12/15 ay)**. Ölen sinyal değil, A-stop'tu |
| `0..20 SHORT` | *"tek iyi SHORT bandı"* | **HÜKÜM YOK** — mekaniğe göre işaret dönüyor (+0,014 → −0,095, t=−2,26) |
| `>40 SHORT` kötü | t=−2,55 | **AYAKTA** — üç ölçümde de negatif (−2,284 / −1,661 / −1,144) |
| `-40..0` | — | **HÜKÜM YOK** — üçünde de sıfıra yakın |

#### KAPSAM DENETİMİ — hangi ölçümler etkilendi

**Betik:** `scratchpad/short_kayip/G_kapsam.py`. Savunma (*"mekanik her hücrede
aynı, sıralamayı bozmaz"*) **çürütüldü**:

```
bant      stop genisligi  ATR/fiyat  stop olma
-40..0        2,86%         2,50%      73,1%
0..20         2,86%         2,13%      76,5%
20..40        5,88%         4,27%      61,8%
>40           9,31%         6,50%      50,1%
```

Stop genişliği **3,3 kat** ayrışıyor. **Kural: hücreler oynaklıkta ayrışıyorsa
ham getiri ZORUNLU.**

| durum | ölçümler |
|---|---|
| ❌ **etkilendi** | bugünkü `chg24` bant hükümleri · trailing testi (tek mekanik tabanı) |
| ✅ **temiz** | `top_ls` ölümü (ham 72s getiri) · 117 canlı pozisyon analizi (gerçek defter) · mutabakat · kapı karnesi · yön karışımı · 30 hücrelik ızgara (zaten mekanik taraması) · kombinasyon araması (gerçek P&L) |
| ⚠️ **bakılacak** | `btc_pay` rejim testleri · `asgari_stop` · `katilim_filtresi` · `ileri_rr` — hepsi A-stop+%10 kullandı, hücrelerin oynaklık ayrışması ÖLÇÜLMEDİ |

### ✅ DENETİM — `btc_pay` hükümleri AYAKTA (2026-08-20, `H_btcpay_denetim.py`)

Bant hükümlerini çürüten kusur `btc_pay` testlerini de vurdu mu? **Hayır.**

**SORU 1 — hücreler oynaklıkta ayrışıyor mu?**

```
rejim  bant   stop genis  ATR/fiyat  stop olma
AYI    UST      3,44%      2,71%      79,6%
AYI    diger    3,11%      2,45%      67,7%
NOTR   UST      2,99%      2,23%      71,8%
NOTR   diger    2,83%      2,20%      67,9%
BOGA   UST      3,09%      2,36%      69,4%
BOGA   diger    2,97%      2,51%      76,7%
```

Stop genişliği **2,83–3,44%** — yalnız **1,2 kat** yayılım.
(Karşılaştır: `chg24` bantlarında **3,3 kat**.) **Mekanik burada neredeyse eşit.**

**SORU 2 — ham getiriyle aynı hüküm mü?**

```
LIFT (UST - diger)        HAM       MEKANIK    ayni yon
AYI                     -4,124      -1,270      EVET
NOTR                    -3,214      -0,922      EVET
BOGA                    -1,476      -0,015      EVET
```

**Üç rejimde de aynı işaret.** Üstelik **ham etki mekaniklinin ~3 KATI** — yani
stop sinyali *yaratmıyor*, **söndürüyor**.

#### Hükümlere etkisi

| dün geceki hüküm | denetim sonucu |
|---|---|
| Fren AYI'da gerçek | ✅ **güçlendi** — ham lift −4,12 (mekanik −1,27) |
| Fren NOTR'da gerçek | ✅ **güçlendi** — ham lift −3,21 (mekanik −0,92) |
| Fren BOĞA'da gürültü | ⚠️ **yeniden okunmalı** — ham lift −1,476, diğerleriyle **aynı yönde**; mekanikte sıfıra yakın çıkması stop sönümlemesi olabilir. *"İşaret dönüyor"* demek artık desteklenmiyor; doğrusu **"aynı yönde ama zayıf/az güçlü"** |

**Genel ders:** stop, `btc_pay` sinyalinin **üçte ikisini yiyor** (ham −4,12 →
mekanik −1,27). Kenar var ama mekanik onu büyük ölçüde tüketiyor.

### 🔴 STOPUN GERÇEK MALİYETİ ÖLÇÜLDÜ (2026-08-20, `I_stop_maliyeti.py`)

**Soru:** stopu neden bu kadar pahalıya ödüyoruz? (ham etki mekaniklinin 3 katı
çıkınca soruldu.) SHORT · botun kendi kapıları · 2 yıl · **N=22.072**.

#### 1 · Stop, gürültünün İÇİNDE duruyor

```
stop mesafesi     : medyan %2,97  (ATR cinsinden 1,50 x ATR)
72 saatlik ufkun beklenen menzili : sqrt(72) = 8,5 x ATR
-> stop, ufkun dogal menzilinin YALNIZ %17,7'sinde
```

**Mekanizma tek cümle:** 1,5 ATR uzağa stop koyup **72 saat** bekliyoruz.
Saf rastgele yürüyüş bile o stopa çarpar.

#### 2 · Sonuç dağılımı

```
STOP    15.364  (%69,6)
HEDEF    4.936  (%22,4)
SURE     1.772  (% 8,0)
```

#### 3 · Stopların beşte biri YANLIŞ

Stop olan işlemler, stop **olmasaydı** aynı 72 saat içinde hedefe varır mıydı:

```
stop olan                : 15.364
hedefe varirdi           :  3.333  (%21,7)   <-- YANLIS STOP
gercekten kotu giris     : 12.031  (%78,3)

yanlis stoplarin TUM olaylara orani: %15,1
olay basina kaba maliyet: ~1,96 puan
```

#### 4 · Yanlış stoplar ERKEN geliyor

```
tum stoplar    : medyan  6. saat
YANLIS stoplar : medyan  4. saat
yanlis stoplarin %64'u ILK 6 SAATTE
```

#### HÜKÜM

**Kenar var, mekanik tüketiyor.** İki bağımsız ölçüm aynı yere çıktı:
`btc_pay` ham lift −4,12 → mekanikle −1,27 (üçte biri kalıyor); ve burada
işlemlerin **%15,1'i** kazanacakken stopla öldürülüyor.

⚠️ **Bu "stopu kaldır" DEMEK DEĞİL.** Ölçülen şey maliyet tarafı; fayda tarafı
(kalan %78,3'te kaybın sınırlanması) **ölçülmedi**. Stopsuz kayıp sınırsızdır.

**Ölçülmemiş ama işaret edilen:** yanlış stopların %64'ü ilk 6 saatte geliyor,
yani sorun stop *seviyesi* değil **erken gürültü** olabilir. Zamanla değişen
(başta gevşek, sonra sıkı) bir stop bunu sınardı — **denenmedi, önerilmiyor.**

### 🔴 ERKEN GÜRÜLTÜ SINAVI + KENAR/SÜRTÜNME AYRIŞTIRMASI (2026-08-20)

**Ön-kayıt** `J_erken_gurultu.py` içinde, koşturulmadan önce. SHORT · botun
kapıları · 2 yıl · **N=22.072** · eşleşmiş (aynı girişler, farklı mekanik).

#### Ayırıcı sınav — hangi açıklama doğru?

```
kol                        islem ort  eslesmis f.  ay-kumeli t   A yari    B yari
K0 KONTROL (bugunku)         -0,076        -            -           -         -
K1 ERKEN-GEN (ilk 6s x2)     -0,019     +0,0572      +2,32     +0,0086   +0,1057
K2 SQRT-GEN (sqrt(1+t/6))    -0,054     +0,0223      -0,63     -0,1061   +0,1508
K3 UFUK 6 saat               -0,121     -0,0441      -0,22     +0,0724   -0,1607
K4 UFUK 12 saat              -0,118     -0,0415      -0,49     +0,0198   -0,1028
```

**TEŞHİS DOĞRULANDI: sorun ERKEN GÜRÜLTÜ.** Ön-kayıtlı ayırıcı okumaya göre
`K1 >> K0` ve `K1 > K2` → ölçek uyumsuzluğu değil, **ilk saatlerin dalgalanması**.
Ufku kısaltmak (K3/K4) işi **kötüleştiriyor** — yani 72 saat sorun değil.

⚠️ **Kendi beklentim TUTMADI**: K3/K4'ün kazanmasını yazmıştım, kaybettiler.

#### Ama KURAL geçemedi

| ölçüt | K1 |
|---|---|
| 1. işlem başına yüksek | ✅ −0,019 vs −0,076 |
| 2. iki yarıda da | ✅ +0,009 / +0,106 |
| 3. ay-kümeli t > +2,0 | ✅ **+2,32** |
| 4. üç rejimde ters işaret yok | ❌ **BOĞA −0,1134** |

**HÜKÜM: KALDI** (ölçüt 4). Not: düşüren hücre **güçsüz** — BOĞA t=−0,48,
8 ayın 2'si, N=1.111. NOTR ise güçlü: **t=+3,47, 25 ayın 19'u**, N=16.704.
Ölçüt metni sonuçtan sonra **değiştirilmedi** (D/9).

#### 🔴 ASIL BULGU — kenar var, sürtünme yiyor

```
BRUT  (stop/hedef sonrasi, maliyet ONCESI)  : +0,1795 puan
fonlama                                     : -0,1259   (brut kenarin %70'i)
maliyet (2 x [taker %0,045 + slipaj %0,02]) : -0,1300   (brut kenarin %72'si)
--------------------------------------------------------
NET                                         : -0,0764
```

**Giriş kenarı VAR (+0,18). Sürtünme onun %142'sini yiyor.**

Stop onarımı (+0,057) uygulansa bile net **−0,019** — hâlâ negatif.
Yani stop gerçek bir sızıntı ama **tek başına yetmiyor**.

⚠️ `kripto-config.json → maliyet._teyit`: *"BU SAYILARI BINANCE FEE-RATE
SAYFANDAN TEYIT ET ... hesabindan OKUNMADI"*. Maliyetin %72'lik payı
**doğrulanmamış bir varsayıma** dayanıyor.

### 🔴 MALİYET DOĞRULAMASI + FONLAMA AYRIŞTIRMASI (2026-08-20)

#### ADIM 1 — ücretler doğru, SLİPAJ 2,5 kat eksik

Kullanıcı BNB tutuyor. İki kaynak doğrulandı: Binance USDⓈ-M futures VIP0 taban
**maker %0,02 / taker %0,05**, BNB ile futures'ta **%10 indirim** →
**0,018 / 0,045**. `kripto-config.json` bu değerleri **doğru** taşıyor.

**Ama slipaj tahmindi ve ölçüldü** (`derinlik_giriste`, N=25 tekil):

```
olculen slipaj : medyan %0,0499 · ortalama %0,0612 · max %0,196
VARSAYIM       : %0,0200            -> gercek 2,5 KAT
```

**Slipaj pozisyon/defter oranıyla büyüyor** (`defter_usdt_20` zaten toplanıyor):

```
poz/defter   slipaj
  0,032      0,0335%
  0,102      0,0565%
  0,296      0,0761%      korelasyon r = +0,439
```

**Gerçekçi maliyet** (giriş taker+slipaj; çıkış %69,6 STOP taker+slipaj ·
%22,4 TP maker · %8 süre): **0,1726** — varsayılan 0,130'dan **+0,0426 pahalı**.
→ **NET −0,076 değil, −0,119.**

#### ADIM 2 — fonlama HEM kenar HEM maliyet

Botun iki kapısı ayrı ölçüldü (2 yıl, SHORT):

```
kume                N       BRUT    fonlama   maliyet       NET    ay-t
A (funding)     17836    +0,2096   -0,1479   -0,1300   -0,0683   -1,36
A+B               996    +0,3215   -0,2250   -0,1300   -0,0334   -0,49
B (MA50+ucuz)    3240    -0,0301   +0,0256   -0,1300   -0,1345   -0,58
```

🔴 **`MA50+ucuz` kapısının BRÜT kenarı NEGATİF (−0,0301).** Maliyet öncesi bile
kaybettiriyor. Kenarın tamamı **funding kapısından** geliyor.

**Fonlama dilimlerinde kenar ve maliyet BİRLİKTE büyüyor:**

```
funding dilimi (%/8s)      N       BRUT    fonlama       NET
-200,00 .. -4,29        4459    +0,6044   -0,4479   -0,0161
  -4,29 .. -1,59        4459    +0,0078   -0,0910   -0,2557
  -1,59 .. -0,61        4459    +0,1232   -0,0382   -0,0876
  -0,61 .. -0,05        4459    +0,1029   -0,0144   -0,0841
```

**HÜKÜM: kenar ve maliyet AYNI OLGU.** Kalabalık short (derin negatif fonlama)
geri döner — kenar budur — ama o pozisyonu taşımak için fonlama ödenir. En derin
dilimde brüt **+0,6044**, fonlama **−0,4479** onu yer. İkisi birlikte ölçekleniyor,
net düz kalıyor.

**Buradan çıkan ölçülebilir soru (denenmedi):** fonlama **8 saatte bir** kesiliyor;
brüt kenar ise sürekli. En derin dilimde tek fonlama kesintisi **%4,29**.
*Fonlama saatinden kaçınan bir tutma penceresi kenarı ödemeden yakalar mı?*
⚠️ Bu daha önce denenmiş ama ölçüm `SEYRELT=24` faz kilidine takılmıştı
(bir kova örneklemin %62'sini taşımıştı). Faz kaydırmayla yeniden kurulabilir.

### ❌ FONLAMA ZAMANLAMASI — BULGU YOK (2026-08-20)

**Hipotez:** fonlama 8/4 saatte bir kesiliyor, brüt kenar sürekli. Kesintiden
kaçınan bir giriş zamanlaması kenarı ödemeden yakalar mı?

#### İlk deneme HATALIYDI — karıştırıcı bulundu ve giderildi

*"Fonlamaya kalan saat"* değişkeni zamanlamayı değil **sembolün periyodunu**
ölçüyordu. Ölçüldü: **418 sembol 4 saatlik**, **147 sembol 8 saatlik**, 2 sembol
1 saatlik fonlama kullanıyor. 4 saatlikler yalnız `kalan 0-3`'e düşüyor →
kovalar karışıktı (bir kova %22,2, diğeri %3,7).

#### Düzeltilmiş ölçüm — periyot ayrık, zamanlama oransal

```
4 SAATLIK semboller (N=14.026)
ceyrek     N       BRUT     fonlama       NET     ay-t   kesinti
1       1996    +0,4667    -0,3213   -0,0272    +0,35     9,25
2       3669    +0,2009    -0,2305   -0,2022    -2,55     7,43
3       3143    +0,2054    -0,1440   -0,1112    -0,66     5,88
4       5218    +0,0798    -0,1307   -0,2235    -2,22     5,36

8 SAATLIK semboller (N=4.501)
1        766    -0,0701    -0,0426   -0,2853    -1,21     4,11
2       1160    -0,4185    -0,0446   -0,6357    -3,48     3,98
3       1101    -0,4629    -0,0357   -0,6712    -2,98     3,54
4       1474    +0,0618    -0,0266   -0,1374    -1,25     3,21
```

**HÜKÜM: BULGU YOK.**
1. **Hiçbir hücre pozitif değil** — en iyisi 4s/1. çeyrek −0,0272
2. Desen iki periyot grubunda **tutarsız** (4s'de azalan, 8s'de U)
3. **Artık karıştırıcı duruyor:** `kesinti` sayısı çeyrekler arası 9,25 → 5,36
   değişiyor, yani çeyrek hâlâ tutma süresiyle ilişkili (hayatta kalan uzun tutar)

**Fonlama zamanlaması sistemi kurtarmıyor.** Denendi, kapandı.

### 🔴🔴 BOTUN ÇEKİRDEK KAPISI KONTROL GRUBUNDAN KÖTÜ (2026-08-20)

**Betikler:** `N_ufuk.py` · `N2_ufuk_kontrol.py` · `O_kapi_kontrol.py` ·
`P_ters_kapi.py` (ön-kayıtlı). SHORT · aynı mekanik (A-stop · %10 hedef · 72s ·
maliyet 0,1726 · fonlama) · 2 yıl.

#### Uzun tutma ölçümü (Eksen 1 / İş 1) — havuz artı, ay-kümeli sıfır

```
ufuk        N       HAM     fonlama       NET   ham ay-t   net ay-t   poz ay
24s     44701   +0,0984   -0,1851   -0,2592     -0,18     -3,45      7/24
72s     44701   +0,2540   -0,4746   -0,3932     -0,64     -2,04     11/24
1 hafta 44701   +1,0827   -0,9631   -0,0530     +0,02     -0,81     10/24
2 hafta 44701   +2,2265   -1,6562   +0,3977     +0,18     -0,59     11/24
1 ay    44701   +4,8722   -2,8545   +1,8451     +0,24     -0,35     13/24
```

**Havuz-net 2 haftada artıya geçiyor — ama sahte.** Üç kontrol:
- **Aykırı sürüklemesi:** en iyi %5 çıkarılınca **−0,5704**; %10 çıkarılınca −2,5641.
  En iyi 5 işlem: +110, +109, +109, +108, +102 (sıfıra çöken coinler)
- **Ay-kümeli t her ufukta NEGATİF**, pozitif ay ~yarısı
- **Kontrol grubu daha iyi:** 1 ayda kapı +1,8451 · kapısız **+2,2061**

#### 🔴 Ve asıl bulgu: kapı, KONTROL GRUBUNDAN kötü

```
kume                     N       BRUT    fonlama       NET   ay-kumeli t   poz ay
KAPI (fund<=-0,05)   18832    +0,2155   -0,1519   -0,1090     -1,74       9/25
KONTROL (fund>-0,05) 49258    +0,1231   +0,0199   -0,0295     -0,35      11/25
                                          KAPININ KATKISI: -0,0795
                          ay-kumeli fark t=-1,72 · kapi ustun 10/25 ay
```

**Kapı doğru yeri buluyor ama ödeyerek buluyor.** Brüt kenarı gerçekten yükseltiyor
(+0,2155 vs +0,1231) — sinyal var. Ama o kenarı bulmak için **fonlama ödüyor**
(−0,1519) iken kontrol grubu fonlama **tahsil ediyor** (+0,0199). Net etki: kapı
**0,08 puan zarar ettiriyor**.

⚠️ Orijinal kapı ölçümü `radar_archive`'da **N=201**, farklı mekanik (2R hedef),
kontrol grubu **yoktu**. Bu ölçüm **N=68.090**, 2 yıl, **kontrol gruplu**. İkisi
aynı şeyi ölçmüyor, ama örneklem 300 kat ve kontrol var.

#### ÖN-KAYITLI TERS KAPI SINAVI — KALDI

Fonlaması **pozitif** olanı shortlamak (kalabalık LONG'u fade'lemek + fonlama
tahsil etmek). Eşik botun kendi eşiğinin aynası (±0,05), seçilmedi.

```
kume                     N       BRUT    fonlama       NET   ay-kumeli t   poz ay
MEVCUT (f<=-0,05)    18832    +0,2155   -0,1519   -0,1090     -1,74       9/25
KONTROL (arasi)       1274    +0,0943   -0,0126   -0,0910     -0,99      10/22
TERS   (f>=+0,05)    47984    +0,1239   +0,0208   -0,0279     -0,30      11/25
```

| ölçüt | sonuç |
|---|---|
| 1. TERS > MEVCUT | ✅ +0,0811 |
| 2. TERS > KONTROL | ✅ +0,0630 |
| 3. ay-kümeli t > +2,0 | ❌ **−0,30** |
| 4a. iki yarıda da pozitif | ❌ A +0,0131 / B −0,0689 |
| 4b. rejimde ters işaret yok | ❌ AYI −0,178 · NOTR +0,068 · BOĞA −0,383 |

**HÜKÜM: KALDI.** Ön-kayıtlı beklenti (*"kararsız, geçmeye yakın"*) tuttu.
⚠️ Bu bir **dilim taramasından** çıkmıştı ve ön-kayıtla sınandı; geçemedi.

#### NE ÖĞRENİLDİ

**Ters kapı kâr etmiyor (−0,0279) ama mevcut kapıdan +0,0811 daha iyi.**
Yani mevcut kapı **kenarı buluyor ama net olarak zarar ettiriyor** — kontrolünden
de, aynasından da kötü. Bu, projenin en merkezî varsayımına ait ilk
**kontrol gruplu** ölçümdür.

### 🔴🔴🔴 KAPI KARNESİ — KONTROL GRUPLU, ÇİFT MEKANİKLİ (2026-08-20)

**Betikler:** `Q_tum_kapilar.py` (mekanikli) · `R_ham_dogrulama.py` (ham getiri).
Her kapı **tek tek**, diğerlerinden bağımsız: *geçen* vs *geçmeyen*.
Aynı olay evreni **N=189.134** · 2 yıl · ay-kümeli · maliyet+fonlama dahil.

#### Doğrulama katmanı (kullanıcı talebi: *"hatasız olduğundan emin ol"*)

| # | kontrol | sonuç |
|---|---|---|
| D1 | bilinen sonucu yeniden üret (`O_kapi_kontrol` KAPI hücresi) | ✅ N=18832 · BRUT +0,2155 · fonlama −0,1519 · NET −0,1090 **birebir** |
| D2 | geçen + geçmeyen = toplam (her kapı) | ✅ |
| D3 | NET = BRUT − maliyet + fonlama (tolerans 1e-9) | ✅ |
| D4 | NaN/sonsuz yok | ✅ |
| D5 | toplam ortalama iki yoldan | ✅ −0,047304 = −0,047304 |

#### Karne

```
kosul                  MEKANIKLI fark  ay-t     HAM fark   ay-t    ATR gec/gecmeyen  ISARET
funding <= -0,05          -0,0956     -3,15     -0,5430   -4,96      1,73 / 1,69      AYNI
MA50+ucuz                 -0,1084     -0,75     -0,1574   -0,11      2,36 / 1,67      AYNI
fiyat <= $0,07            -0,0880     -2,44     -0,2827   -2,14      1,87 / 1,63      AYNI
chg24 >= %20 (pump)       -0,5134     -2,14     -2,1799   -1,90      4,69 / 1,68      AYNI
chg24 >= %40 (blowoff)    -1,3889     -2,41     -4,4757   -1,88      6,50 / 1,69      AYNI
pos >= 0,75 (tepe)        -0,0984     -1,12     +0,0763   +0,44      1,56 / 1,74      🔴 DONDU
pos < 0,25 (dip)          +0,1044     +0,89     +0,0558   -0,24      1,77 / 1,67      zayif
```

#### 🔴 HÜKÜM — bot NE ALMAYACAĞINI biliyor, NE ALACAĞINI bilmiyor

**AÇAN kapıların ikisi de ZARARLI:**
- `funding <= -0,05 → SHORT AÇ` : **ham fark −0,5430 (t=−4,96, 5/25 ay)**,
  mekanikli −0,0956 (t=−3,15). **İki ölçümde de anlamlı negatif.**
  ⚠️ Ve **oynaklık karıştırıcısı YOK** — ATR 1,73 vs 1,69 (bugün öğrenilen sınama).
  Ham ölçüm mekanikliden **beş kat güçlü**: mekanik, kapının ne kadar kötü
  olduğunu **maskeliyor**.
- `MA50+ucuz → SHORT AÇ` : her iki ölçümde negatif. Fiyat bacağı (`≤$0,07`)
  tek başına **t=−2,44 / −2,14** ile anlamlı zararlı.

**ENGELLEYEN kapıların ikisi de DOĞRU:**
- `chg24 >= %20` pump kapısı : geçenler −0,5525 (ham −2,14). Engellemek **doğru**.
- `chg24 >= %40` blowoff : geçenler −1,4313 (ham −4,46). Engellemek **doğru**.
  ⚠️ Bu ikisinde ATR **3-4 kat** ayrışıyor; hüküm ham ölçümle de aynı yönde
  olduğu için ayakta, ama güveni mekanikliden okumak yanlış olur.

**`pos >= 0,75` işaret DÖNDÜ** (mekanikli −0,0984 / ham +0,0763) → **hüküm yok.**

#### Bunun anlamı

Botun **negatif filtreleri çalışıyor**, **pozitif seçicileri çalışmıyor**.
Aylardır ölçülen her şey bu iki açan kapının üstüne inşa edildi; **kapıların
kendisi bugüne kadar kontrol grubuyla hiç sınanmamıştı**. Orijinal `A+B` ölçümü
`radar_archive`'da **N=201**, kontrol grubu **yoktu**.

⚠️ **Kural önerilmiyor** (kullanıcı talimatı). Bu bir teşhis kaydıdır.

### 🟡 KÂR EDEN YAPILANDIRMA VAR MI? — kademeli yığın (2026-08-20)

**Betikler:** `S_yigin.py` · `S2_aykiri.py`.
⚠️ **ÖRNEKLEM İÇİ İNŞA** — bileşenler sonuçlara bakılarak seçildi. Tek geçerli
hakem **zaman bölünmesi**.

#### SHORT — her bileşen katkı yapıyor (2 yıl, ay ortalaması)

```
adim                          N       net(ay)   ay-t   poz ay   erken-stop
0. HAM EVREN (kapisiz)    70694       -0,1097  -0,86   11/25      -0,0340
1. + pump engeli (<%20)   68090       -0,0949  -0,73   11/25      -0,0153
2. + ucuz disla (>$0,07)  45175       -0,0453  -0,36   12/25      +0,0301
3. + funding kapisi KALK  32427       +0,0106  +0,08   14/25      +0,0904
4. + btc_pay UST disla    19766       +0,2340  +1,33   15/25      +0,3416
```

**Monoton iyileşme.** Her adım katkı yapıyor; işlem sayısı 70.694 → 19.766 (**−%72**).

#### LONG — her adımda daha kötü

```
0. HAM EVREN  -0,3229 (t=-4,14)  ...  4. tam yigin  -0,5292 (t=-4,53)
```

**Bu evrende LONG anlamlı biçimde zararlı.** Beş adımın hepsinde t < −4.

#### HAKEM — zaman bölünmesi

```
SHORT normal stop   A yarisi +0,2376 (t=+0,75)  ·  B yarisi +0,2814 (t=+1,53)
SHORT erken-stop    A yarisi +0,3433 (t=+0,96)  ·  B yarisi +0,4018 (t=+1,87)
```

**İki yarıda da artı**, ve ikinci yarı daha iyi.

#### Aykırı ve yoğunlaşma kontrolü

```
N=19.766 · ortalama +0,2745 · MEDYAN -2,5365 · kazanan %32,4
en iyi %1 cikarilinca +0,1756 · %5 cikarilinca -0,2343
en iyi 5 islem: +11,3 +10,8 +10,8 +10,7 +10,6   <-- bunlar HEDEF vuruslari
ayrik sembol 454 · en cok katkili sembolun payi %1,0
pozitif ay 15/25 · EN IYI AY atilinca +0,2362
```

⚠️ **"En iyi %5 çıkınca negatif" burada kırmızı bayrak DEĞİL.** Sistem tasarımı
gereği %32 kazanma oranı + 3:1 ödeme; kazançların tamamı hedef vuruşlarından
gelir. En iyi %5 = ~988 işlem, birkaç aykırı değil. **Sembol yoğunlaşması yok**
(454 sembol, en büyüğü %1,0), en iyi ay atılınca **hâlâ pozitif**.

#### HÜKÜM — 🟡 UMUT VERİCİ AMA ANLAMLI DEĞİL

| ölçüt | sonuç |
|---|---|
| iki zaman yarısında da pozitif | ✅ +0,343 / +0,402 |
| ay-kümeli t > +2,0 | ❌ **+1,33** |
| pozitif ay | 🟡 15/25 |
| aykırı/sembol yoğunlaşması | ✅ yok |
| en iyi ay atılınca | ✅ +0,236 |

**Kural ÇIKARILMIYOR.** Bu bir *örneklem içi inşadır* ve ön-kayıtlı değildir.
2 yıllık verinin tamamı kullanıldığı için **geriye kalan tek geçerli hakem
İLERİ ZAMANDIR.**

**Ne söylüyor:** botun bugünkü net'i **−0,119**; bu yapılandırma **+0,34**.
Fark ~0,46 puan/işlem. Ve farkın kaynağı **yeni bir sinyal değil** — üç zararlı
şeyin kaldırılması (funding kapısı, ucuz coinler, UST bandı) artı ölçülmüş bir
stop onarımı.


---

### ❌ MAJÖRLERDE "HACİM PATLIYOR, FİYAT KIMILDAMIYOR" İZİ — GEÇMEDİ (2026-08-21)

**Ön-kayıt:** `scratchpad/poz_yol/ON_KAYIT_major_iz.md` (koşumdan önce commit `9edaad7`)
**Betik:** `scratchpad/poz_yol/06_major_iz.py`
**Veri:** `scratchpad/major_5dk/{BTC,ETH}.json` — 5 dk, **210.241 bar**, 2024-08-21 → 2026-08-21, 25 ay

**Soru (kullanıcı):** *"Majörlerdeki patlamayı önceden okuyabilirsek piyasanın o an ne
yöne gideceğini tespit etme ihtimalimiz yüksek. Böyle bir sıçrama olunca piyasa LONG'a
döner ve biz SHORT'ta squeeze'de kalırız."*

**İz tanımı (ön-kayıt):** 3 barlık (15 dk) pencerede `hacim_x ≥ 5,0` **VE**
`|getiri| ≤ 0,5 × ATR`. N: BTC **151** · ETH **165**.

#### H1 — oynaklık: iz sonrası mutlak hareket büyür mü?

```
        BTC                              ETH
ufuk    iz/kontrol   oran      p         iz/kontrol   oran      p
+1sa    0,205/0,207  0,99x  0,96495      0,368/0,234  1,57x  0,00185
+2sa    0,441/0,309  1,43x  0,00510      0,443/0,368  1,20x  0,09185
+4sa    0,554/0,409  1,36x  0,02260      0,704/0,552  1,28x  0,05085
```

**Eşik `p < 0,000833` (Bonferroni, 12 karşılaştırma) — hiçbir ufuk geçemedi.**
En iyisi ETH +1sa (0,00185), eşiğin **2 katı** üstünde. Üstelik BTC'nin en iyi
ufku (+2sa) ile ETH'ninki (+1sa) **farklı**.

#### H2 — yön: izin içindeki taker alış payı yönü söyler mi?

BTC en iyi p=0,04510 · ETH hepsi p>0,45 · ay tutarlılığı 2/3 ve 2/4 (kullanılamaz).
**Açıkça geçmedi** — ön-kayıtta zaten beklenmiyordu.

#### 🔴 Asıl çürüten: karıştırıcı kontrolleri İKİ ENSTRÜMANDA TERS

```
"iz", duz yuksek hacimden daha mi iyi? (+2sa |getiri|)
  BTC  iz 0,4413  vs  hacimli-HAREKETLI 0,3846   -> iz DAHA IYI
  ETH  iz 0,4426  vs  hacimli-HAREKETLI 0,5586   -> iz DAHA KOTU

ATR dilimi icinde oran (iz/kontrol)
  BTC  dusuk 0,89x  ·  orta 1,69x  ·  yuksek 1,14x
  ETH  dusuk 1,53x  ·  orta 1,04x  ·  yuksek 0,87x
```

BTC'de ortada tepe yapıp uçlarda düşüyor, ETH'de **tam tersi** — düşükten yükseğe
monoton azalıyor ve yüksek ATR'de **1'in altına** iniyor. İki bağımsız enstrüman
aynı olguya zıt cevap veriyorsa olgu yoktur.

#### ⚠️ Hipotezi doğuran vaka, tanıma UYMUYOR — koşumdan önce tespit edildi

19 Ağustos'un hiçbir penceresi "iz" değil; fiyat her pencerede ATR'nin
**3-4,4 katı** oynamış (15:45'te hacim 11,3× ama getiri 4,4×ATR). Yani
motive eden olay `hacim yüksek + fiyat KIMILDADI` grubunda — ki o grup da
yukarıdaki kontrolde iki enstrümanda ters çıktı.

**HÜKÜM: öncü gösterge YOK.** Bota kural eklenmedi, eklenmeyecek.

**Yan bulgu (ölçülmedi, gözlem):** 19 Ağustos kırılmasında altlarda
`fiyat +1,777% · OI −0,315% · taker alış payı 0,488 (kontrol 0,489)` —
yükselişi alıcılar değil kapanan pozisyonlar üretmiş görünüyor. Tek vaka,
hüküm değil. Bot tam o barın içinde SHORT açtı (BIO ~18:09) ve 12 dakikada
stop oldu.

---

### 🔴🔴 HOLDOUT (11-18 AĞUSTOS) — DÖRT HÜKMÜN DÖRDÜ DE AYAKTA KALMADI (2026-08-21)

**Ön-kayıt:** `scratchpad/poz_yol/ON_KAYIT_holdout.md` (koşumdan önce, commit `b146cc3`)
**Betikler:** `12_holdout.py` · `13_holdout_saglamlik.py`
**Veri:** `klines_1h_uzun` 08-11 → 08-21'e uzatıldı (+129.220 bar, +27.192 fonlama)

**Neden holdout:** 2 yıllık veri **tam 2026-08-11 11:00'de** bitiyordu; ondan çıkan
her hüküm bu günleri hiç görmedi. N=53.354 aday giriş, 8 gün.

#### İşaret testi (ön-kayıtlı ölçüt)

| hüküm | 2 yıl | holdout (gün-ort) | işaret |
|---|---|---|---|
| 1 · SHORT yığını | +0,2340 | **+0,1798** | tuttu |
| 2 · `funding ≤ −0,05` kapısı ZARARLI | fark +0,5430 | fark **−1,1369** | 🔴 **TERS** |
| 3 · pump ≥%20 engeli DOĞRU | geçenler −2,18 | geçenler **+0,9106** | 🔴 **TERS** |
| 4 · `>40 LONG` + trailing | +2,379 | **−1,6660** | 🔴 **TERS** |

#### 🔴 Sağlamlık: dördü de birkaç sembolden geliyor

```
hukum  N      ortalama   en iyi 3 sembolun payi   3 sembol CIKINCA
1     4279    +0,1038          %342                 -0,2777   <- ISARET DONDU
2     1568    +1,1353           %97                 +0,0439   <- sifirlandi
3      798    +0,5202          %104                 -0,0252   <- sifirlandi
4      274    -0,5578         -%262                 -2,9154   <- daha kotu
```

**Hüküm 1 dahil hiçbiri ayakta kalmıyor.** SHORT yığınının artısı 138 sembolün
**3'ünden** geliyor (BEAT +762 · SKYAI +427 · LAB +330); onlar çıkınca **−0,2777**.
En iyi gün çıkınca **−0,0034**.

#### ⚠️ Boğa bacağı test edilmedi — `BOGA (08-19+): N=0`

72 saatlik ufuk şartı, 08-19 sonrası tüm girişleri eledi. Bu ön-kayıtta
**baştan yazılmıştı**; yine de sonuç şu: holdout yalnızca **boğa öncesi 8 günü**
ölçtü. Boğa penceresi hâlâ ölçülmemiş durumda.

#### HÜKÜM

**Holdout hiçbir şeyi doğrulamadı ve SHORT yığınını aktif olarak zayıflattı.**
Tüm |t| < 1,6 — ön-kayıt gereği anlamlılık iddia edilmiyor, ama işaret testinin
kendisi de yoğunlaşma kontrolünden geçmedi.

**Somut sonuç:** `funding ≤ −0,05` kapısının **zararlı olduğu iddiası** artık iki
yönlü belirsiz — 2 yıl "zararlı", holdout "faydalı" dedi ve holdout'un cevabı
3 sembolden geliyor. **Hiçbir yönde kanıt yok.** 2026-08-20 tarihli
*"botun çekirdek kapısı kontrol grubundan kötü"* hükmünün yanına bu not düşülür
(D/9: eski ölçüt silinmez).

⚠️ `defter2` bu SHORT yığını üzerine kurulmuştu; dayanağı bu ölçümle zayıfladı.
Defterin kendisi ileri zamanda sınanmaya devam ediyor — kapatılmadı.

---

### ❌ ALTLAR BTC'Yİ HABER VERİYOR MU — HAYIR (2026-08-21, `05_btc_olay.py`)

**Veri:** `perp_seri/` 63 alt sembol + BTC, 5 dk, 07-23 → 08-21.
**Olay:** BTC'de 30 dk içinde ≥ 2,0×ATR. Yukarı **235** · aşağı **199** · kontrol **859**.

#### BTC hareketinden ÖNCEKİ 60 dk — altların toplu görünümü

```
                 alt_d_fiyat  alt_hacim_x  alt_taker_pay  alt_d_oi
BTC YUKARI (235)    -0,047       1,036        0,4915       -0,010
BTC ASAGI  (199)    +0,000       1,041        0,4918       -0,019
KONTROL    (859)    -0,055       1,029        0,4912       -0,025
```

**Üç grup ayırt edilemiyor.** `taker_pay` farkı 4. ondalıkta. Karıştırıcı kontrolü
(BTC'nin kendi pencere-içi hareketi sabitlenince) üç bantta da aynı: yukarı ve
aşağı olayları birbirinden **ayrılmıyor**.

**HÜKÜM: öncü gösterge yok.** Bu, bu oturumdaki **dördüncü** bağımsız deneme ve
dördü de negatif (majör iz · hacim→yön · taker dengesi · altlar→BTC).

#### 🟡 Yan bulgu — altların aşağı betası yukarı betasından büyük

```
BTC yukari sonrasi 60 dk : altlar  +0,096   (kontrol -0,045)
BTC asagi  sonrasi 60 dk : altlar  -0,134   (kontrol -0,045)
```

Altlar BTC düşerken **1,4 kat daha sert** düşüyor. Gözlem, hüküm değil —
ama SHORT'un neden düşüşte daha kolay para kazandığını, boğada neden
zorlandığını açıklayan yapısal bir asimetri.

---

### 🔴🔴🔴 2 YILLIK ORTALAMA HİÇBİR GERÇEK KOŞULA KARŞILIK GELMİYOR (2026-08-21)

**Betik:** `scratchpad/poz_yol/16_rejim_kosullu.py` · N=145.678 işlem, 25 ay
**Kullanıcının teşhisi:** *"Çünkü 2 yılla test ediyoruz ve koşullar aynı değil."*
**Ölçüldü: doğru.**

Aynı kapılar, BTC drawdown rejimine göre **ayrı ayrı**:

```
                          ATH_BOLGESI   DUZELTME   DERIN_AYI   KARISIM(2 yil)
funding <= -0,05 (kapi)      +0,2944     -0,7298     -0,0459      -0,1692
funding >  -0,05 (kontrol)   +0,7991     -0,7231     -0,2033      +0,0607
chg24 >= %20 (engellenen)    +0,8306     -0,3002     -0,4077      +0,1417
chg24 <  %20                 +0,6454     -0,7367     -0,1493      -0,0054
fiyat > $0,07                +0,6601     -0,6659     -0,1667      +0,0080
SHORT yigini                 +0,7996     -0,6272     -0,1631      +0,0953
```

**Altı kapının altısında da işaret rejimler arasında dönüyor.** 2 yıllık
"ortalama" (+0,0953 gibi), `+0,80` ile `−0,63`'ün karışımıdır — **hiçbir gerçek
piyasa koşuluna karşılık gelmez.**

#### 🔴 Yoğunlaşma sorununun gerçek sebebi bu

```
SHORT yigini · ATH_BOLGESI : top3 payi  %6  ·  3 sembol cikinca +0,3450  (SAGLAM)
SHORT yigini · KARISIM     : top3 payi %12  ·  3 sembol cikinca +0,1060  (zayif)
funding>-0,05 · ATH        : top3 payi  %5  ·  cikinca +0,3099          (SAGLAM)
```

**Tek rejim içinde sonuçlar yoğunlaşmaya DAYANIKLI.** Karışımda çöküyorlar,
çünkü karışım zıt işaretli rejimleri ortalıyor ve kalan şey birkaç gözlemin
tuttuğu gürültü. Holdout'ta dört hükmün birden çökmesinin sebebi buydu.

#### Ortaya çıkan yapısal olgu

**SHORT, piyasa ZİRVEDEYKEN çalışıyor; düşerken çalışmıyor.**
Altı ölçümün altısında sıralama aynı: `ATH pozitif · DÜZELTME en kötü · DERİN AYI hafif negatif`.
Sezgiye ters ama tutarlı: zirvede uzamış altları fade etmek işe yarıyor,
düzeltmede sıçramalar shortu sıkıştırıyor.

⚠️ Bot **07-23'ten beri DERİN AYI ve ondan çıkışta** koşuyor — yani SHORT'un
en zayıf olduğu bölgede. Canlı karnesi bunu doğruluyor: `NOTR SHORT −770,42`.

#### Sınırlar

Rejim-içi t değerleri hâlâ zayıf (en yüksek +1,70), ay sayısı 11-15.
**Anlamlılık iddia edilmiyor.** Bulgu, *işaretin rejimle dönmesi* ve
*rejim-içi yoğunlaşma dayanıklılığı*dır — ikisi birlikte, karışım ölçümünün
neden işe yaramadığını açıklıyor.

**SONUÇ: rejim bir KAPI değil, ÖLÇÜMÜN TABANIDIR.** Rejime koşullamayan her
ölçüm, zıt davranışları ortalayıp sıfır bulur. Bu proje 2 yıldır bunu yapıyordu.

---

### 🔴 REJİM ETİKETİ 8 GÜN GEÇ VE 49 YÜKSELİŞİN 36'SINI KAÇIRIYOR (2026-08-21)

**Betik:** `scratchpad/poz_yol/17_etiket_kalitesi.py` · BTC günlük, 741 gün, 2 yıl

**Yöntem değişikliği — kullanıcının itirazı üzerine.** *"Koşullar aynı olmayacak,
negatif çıkacak."* Haklıydı: iki etiketi **getiri** üzerinden kıyaslamak yine
karışım üretirdi (bkz. rejim-koşullu ölçüm). Bu yüzden soru değişti:

```
ESKI (tuzakli): "hangi etiket daha cok kazandirir?"
YENI (temiz)  : "etiket, BOGA oldugunu ne kadar DOGRU ve ZAMANINDA soyluyor?"
```

Ölçülen şey **sayım istatistiği** (gecikme · kapsama · yanlış alarm), ortalama
getiri değil → yoğunlaşma ve karışım sorunu bulaşmıyor.
**Gerçek "yükseliş günü" tanımı etiketten bağımsız:** BTC'nin sonraki 7 günlük
getirisi ≥ +%3. Taban oran: **220/734 gün = %30**.

#### Tespit kalitesi

```
kural                    kesinlik  kapsama  acik gun%  yanlis+  kacan
MEVCUT (sezon VE hava)      8,4%     4,5%     14,1%      76      147
ONERI  (yalniz sezon)      22,5%    29,9%     34,8%     158      108
sezon VE ham hava (hist.yok) 15,9%   8,4%     14,0%      69      141
```

#### Gecikme — 49 gerçek yükseliş epizodu

```
kural                    gecikme-medyan  ortalama  hemen yakalanan  kacirilan
MEVCUT (sezon VE hava)        8,0 gun     7,2 gun        2/49          36/49
ONERI  (yalniz sezon)         0,0 gun     3,8 gun       11/49          30/49
sezon VE ham hava             7,0 gun     6,8 gun        5/49          32/49
```

**Mevcut etiket 49 yükselişin 36'sını hiç görmüyor; gördüğü 13'ünde medyan
8 gün geç.** Epizot 7 günlük bir hareketle tanımlandığı için **8 gün gecikme,
hareket bittikten sonra açılmak demektir.**

#### Canlı doğrulama — bu hafta

```
08-18  sezon AYI   hava NOTR  ham NOTR  | MEVCUT DIGER  ONERI DIGER
08-19  sezon BOGA  hava NOTR  ham BOGA  | MEVCUT DIGER  ONERI BOGA   <- boga kirildi
08-20  sezon BOGA  hava NOTR  ham BOGA  | MEVCUT DIGER  ONERI BOGA
08-21  sezon BOGA  hava BOGA  ham BOGA  | MEVCUT BOGA   ONERI BOGA   <- 2 gun sonra
```

Bot o iki günde SHORT'taydı; BTC **+%7,6** yaptı.

#### ⚠️ AMA HİÇBİRİ TABAN ORANI GEÇMİYOR

Taban oran %30; kesinlikler **%8,4 · %22,5 · %15,9** — üçü de altında.
**Mevcut etiket BOĞA dediğinde, o günün yükseliş günü olma ihtimali rastgele bir
günden DÜŞÜK** (%8,4 vs %30). Yani etiket bir yükseliş *habercisi* değil;
en iyi hâlde geriye dönük bir *durum tarifi*.

**HÜKÜM:** `izin = sezon` önerisi üç ölçütte de mevcut kuraldan iyi (gecikme
8→0 gün · kapsama %4,5→%29,9 · kesinlik %8,4→%22,5). Ama **hiçbiri yükseliş
tahmin etmiyor.** Etiket yön SEÇMEK için kullanılmamalı; olsa olsa
maruziyet/şiddet ayarı için kullanılabilir.

---

### 🟡 AKIŞ TABANLI REJİM VEKİLLERİ — mevcut etiketten ÇOK İYİ, tabandan değil (2026-08-21)

**Betik:** `scratchpad/poz_yol/18_akis_vekilleri.py` · 567 sembol × 2 yıl → günlük endeks
**Kullanıcı fikri:** *"BTC/ETH hareketi, TOTAL'e giren para, USDT.D, BTC.D bize rejimi verir."*

#### Neyi test edebildik, neyi edemedik

| vekil | 2 yıllık veriden kurulabildi mi |
|---|---|
| **BTC.D** (BTC getirisi − alt medyan, 3 gün) | ✅ |
| **Para girişi** (evren toplam USDT hacmi, 3g/7g ivme) | ✅ |
| **Genişlik** (yükselen sembol oranı) | ✅ |
| **USDT.D** | ❌ stablecoin **arzı** gerekiyor, elimizde yok |
| **TOTAL ($)** | ❌ tarihsel mcap yok |

⚠️ Kullanıcının **özellikle saydığı iki gösterge** (USDT.D, TOTAL) tam da
kuramadığımız ikisi. `piyasa_yapisi_log` onları tutuyor ama **2026-06-26'dan beri,
107 kayıt, günde 2 kez** — sınama için yetersiz.

#### Tespit kalitesi (taban oran %29,6 · 726 gün)

```
kural                          kesinlik  kapsama  acik gun%  gecikme-medyan  kacirilan
BTC ONDE (btc_pay_3g > 0)        29,1%    65,6%     66,8%       0,0 gun          0/49
ALTLAR ONDE (btc_pay_3g < 0)     30,7%    34,4%     33,2%       2,0 gun          0/49
PARA GIRISI (hacim_ivme>1,2)     30,8%    22,8%     21,9%       2,0 gun          2/49
GENISLIK 3g > %55                26,7%    32,6%     36,1%       3,0 gun          0/49
hacim>1,2 VE altlar onde         30,9%     7,9%      7,6%       7,0 gun         17/49
---------------------------------------------------------------------------------
MEVCUT ETIKET (sezon VE hava)     8,4%     4,5%     14,1%       8,0 gun         36/49
```

#### Üç ayrı sonuç, karıştırılmamalı

**1 · Vekiller mevcut etiketten KAT KAT iyi.** Kesinlik %8,4 → %29-31,
gecikme 8 gün → 0-2 gün, kaçırılan 36/49 → 0/49. Mevcut etiketin **anti-haberci**
olması (tabanın 3,5 katı altında) buradaki asıl bulgudur.

**2 · Ama hiçbiri tabanı anlamlı geçmiyor.** En iyisi %30,9 vs taban %29,6 —
**1,3 puan**. `BTC ONDE` günlerin %66,8'inde açık ve kesinliği tam tabanda
(%29,1): bilgi değil, geniş bir süzgeç.

**3 · Kullanıcının asıl önerdiği iki gösterge SINANMADI.** USDT.D ve TOTAL
2 yıllık veride yok. 2 aylık kayıtta ikisi de **doğru günde** döndü
(08-19 23:00: `usdt_d 8,01→7,59` · `total 2,284→2,411 T$`) — botun etiketi
2 gün sonra döndü. Ama 107 kayıtla hüküm yazılmaz.

**HÜKÜM:** Akış vekilleri **yön tahmin etmiyor**, ama mevcut etiketin zararını
kaldırıyor. Bu bir *kazanç* değil, bir *hasar onarımı*.
**Eyleme dönük tek çıkarım:** USDT.D ve TOTAL şu an günde 2 kez kaydediliyor;
sıklaştırılırsa 6 ay sonra sınanabilir hâle gelir. Şimdi sınanamaz.

---

### 🟡 USDT.D / TOTAL / BTC.D SINANDI — mevcut etiketten hızlı, şanstan değil (2026-08-21)

**Kullanıcı onayı ile CoinGecko'dan çekildi** (demo anahtar, ücretsiz katman).
**Betikler:** `scratchpad/gecko_dominans_indir.py` · `poz_yol/19_dominans_testi.py`
**Veri:** 98 coin × günlük mcap × **365 gün** (2025-08-22 → 2026-08-21)

#### Uç sınırları (ölçüldü)
```
/global/market_cap_chart      -> HTTP 401  UCRETLI katman
/coins/{id}/market_chart      -> demo anahtarla OK, AZAMI 365 GUN (366 -> 401)
```
TOTAL bu yüzden **top-98 mcap toplamı** olarak kuruldu (gerçeğin ~%95'i, yaklaşıklık).

#### Tespit kalitesi — taban oran **%24,2** · 20 epizot

```
kural                            kesinlik  kapsama  gecikme-med  kacirilan
BTC.D DUSUYOR (3g < -0,2)          24,8%    31,4%     1,5 gun       0/20
STABLE.D DUSUYOR (3g < -0,2)       23,6%    24,4%     4,0 gun       0/20
USDT.D DUSUYOR (3g < -0,1)         20,8%    25,6%     4,0 gun       0/20
TOTAL ARTIYOR (3g > %+2)           20,8%    23,3%     4,0 gun       0/20
BTC.D ARTIYOR (3g > +0,2)          20,6%    24,4%     3,0 gun       0/20
USDT.D dus VE TOTAL art            21,7%    23,3%     4,0 gun       0/20
------------------------------------------------------------------------
MEVCUT BOT ETIKETI                  8,4%     4,5%     8,0 gun      36/49
```

#### Üç sonuç

**1 · Hiçbiri şansı geçmiyor.** Dokuz kuralın hepsi taban oranın (%24,2)
**altında veya eşitinde** (en iyi %27,8, ve o N=5 ile). Kullanıcının önerdiği
göstergeler **yükseliş tahmin etmiyor.**

**2 · Ama mevcut etiketten kat kat iyi.** Kesinlik %8,4 → %21-25 · gecikme
8 gün → 1,5-4 gün · kaçırılan **36/49 → 0/20**. Yani hiçbir epizodu kaçırmıyorlar.

**3 · Bugünkü okuma tarihsel olarak uç.**
```
08-18  TOTAL 2,236 T$ (+1,72%)   USDT.D 8,18 (-0,14)   BTC.D 57,86
08-19  TOTAL 2,240    (+2,95%)   USDT.D 8,17 (-0,24)   BTC.D 57,93
08-20  TOTAL 2,406    (+9,74%)   USDT.D 7,61 (-0,74)   BTC.D 57,91
08-21  TOTAL 2,630   (+17,64%)   USDT.D 6,96 (-1,23)   BTC.D 59,37 (+1,52)
```
**3 günde TOTAL +%17,6, USDT.D −1,23 puan.** Göstergeler hareketi **tarif
ediyor**, önceden söylemiyor — 4 günlük gecikme bunu zaten gösteriyordu.

**HÜKÜM:** USDT.D/TOTAL/BTC.D **yön tahmin etmiyor** (şansın altında), ama
mevcut etiketin **anti-haberci** zararını kaldırıyor ve hiçbir epizodu
kaçırmıyor. Aynı sonuç, üçüncü bağımsız veri kaynağından: **rejim göstergeleri
durum tarif eder, gelecek söylemez.**

⚠️ Sınır: 365 gün, 20 epizot, taban %24,2 (pencere ağırlıklı ayı). Kısa.

---

### 🔴🔴 HİÇBİR ALANIN İŞARETİ REJİMDE SABİT DEĞİL — bizim veride kanıtlandı (2026-08-21)

**Betik:** `scratchpad/poz_yol/21_boga_kesiti.py`
**Kullanıcının önceden söylediği:** *"İyi de zaten ayı-nötr o veri. Son 3 güne
bakarsan o tutmaz. Ayıda her şey aşağı yönlü, şimdi her şey yukarı döndü."*
**Ölçüldü: aynen öyle.**

`20_bizim_veri.py`'nin penceresi **2026-06-24 → 08-18** — boğanın kırıldığı günün
(08-19 18:15) **bir gün öncesi.** Yani %100 ayı/nötr.

#### Evren ortalaması komple döndü (+6 saat ufuk)

```
AYI/NOTR (54 gun, N=155.258)  ->  -0,1548%
BOGA     ( 2 gun, N=  8.344)  ->  +1,5283%
```

#### İşaret karşılaştırması

```
alan       AYI/NOTR      BOGA        durum
chg24       -0,4961    +1,8814    *** DONDU ***
score       -0,3214    +0,1394    *** DONDU ***
oi24        +0,1136    -0,9197    *** DONDU ***
last3       -0,1131    +0,3098    *** DONDU ***
pos         +0,1459    +1,2359    ayni
vol_x       +0,0764    +1,4883    ayni
comp        +0,1598    +0,9053    ayni
funding     +0,1044    +0,1292    ayni
rel3        -0,0388    -0,5284    ayni
oi3         +0,0684    +0,3889    ayni

+6 saat ufukta isaret donen: 4/10   ·   +3 saat ufukta: 6/10
```

#### 🔴 Bir saat önce yazdığım bulgu, ayı yapaylığıymış

`20_bizim_veri.py`'de *"fırlamış coinleri shortla — chg24 en güçlü ayırıcı
(fark −3,7571, yoğunlaşmaya dayanıklı)"* yazmıştım.

Boğada **tam tersi**: yüksek `chg24` +%2,28 / düşük `chg24` +%0,40 →
fark **+1,8814**. Üstelik ayıdaki farktan (−0,4961) **büyük**.

Yani o bulgu *"fırlamışı shortla"* değil, ***"ayıda her şey düşer"***in başka
bir ifadesiydi. Kullanıcı bunu **ölçümden önce** söyledi.

#### Sabit kalanlar — ve neden yetmiyorlar

`pos` · `vol_x` · `comp` · `funding` · `rel3` · `oi3` işaretini korudu. Ama:
- büyüklükleri 8-19 kat değişiyor (`vol_x` +0,076 → +1,488)
- en sabit olan `funding` (+0,104 → +0,129) ve **çok küçük**
- `rel3` iki rejimde de negatif: BTC'nin gerisinde kalanlar daha iyi gidiyor
  (zayıf ama tutarlı — tek not edilmeye değer olan)

⚠️ **BOGA N=2 gün, 8.344 kayıt.** Gün-kümeli t hesaplanamıyor. Bu bir ÖLÇÜM
değil, **yön kanıtı** — ama farkın büyüklüğü (chg24 −0,50 → +1,88) tartışmayı
kapatıyor.

**HÜKÜM:** Bizim verideki alanlardan **hiçbiri** rejimden bağımsız bir seçim
kuralı üretmiyor. Ayıda ölçüp boğaya taşınan her kural ters işaret riski taşıyor.
Bu, 2 yıllık veri için ölçülen şeyin (`16_rejim_kosullu.py`) **kendi verimizde
tekrarı** — üçüncü kez, farklı pencerede.

---

### 🟡 TOTAL1/2/3 — EŞ ANLI, ÖNCÜ DEĞİL (2026-08-21, `22_total123.py`)

**Veri:** `scratchpad/gecko/` 98 coin × günlük mcap × 365 gün.
`TOTAL1` = top-98 toplamı · `TOTAL2` = −BTC · `TOTAL3` = −BTC−ETH ·
`TOTAL3X` = stablecoin'ler de hariç.

#### Tespit kalitesi — taban oran %24,2

```
kural                              kesinlik  kapsama  gecikme-med  kacirilan
ALT PAYI artiyor (3g > +0,2)         23,0%    26,7%     2,0 gun       0/20
TOTAL3X 3g > %+5                     22,5%    10,5%     4,0 gun       0/20
TOTAL2 3g > %+2 (BTC haric)          22,4%    22,1%     3,5 gun       0/20
TOTAL3X 3g > %+2                     21,5%    26,7%     3,0 gun       0/20
TOTAL1 3g > %+2                      20,8%    23,3%     4,0 gun       0/20
TOTAL3 3g > %+2                      20,5%    19,8%     3,0 gun       0/20
```

**Sekiz kuralın sekizi de taban oranın ALTINDA.** Yön tahmin etmiyorlar.

#### 🔴 Belirleyici olan: çapraz korelasyon

```
kaydirma   korelasyon   yorum
k=-3        -0,0622     TOTAL3X 3 gun ONCE
k=-2        -0,0339     TOTAL3X 2 gun ONCE
k=-1        +0,0129     TOTAL3X 1 gun ONCE
k= 0        +0,7419     ES ANLI        <<<
k=+1        +0,0612     TOTAL3X 1 gun SONRA
k=+2        -0,0621
k=+3        -0,0661
```

**Korelasyon yalnız k=0'da var (0,742); diğer bütün kaydırmalarda sıfır.**
TOTAL3X, BTC'yi **öncelemiyor** — aynı anda hareket ediyor. Öncü olsaydı
k=−1 veya k=−2'de anlamlı bir değer görülürdü; **0,013 ve −0,034.**

Yani TOTAL3X ayrı bir bilgi değil, **aynı hareketin başka bir ölçüsü**.

#### Son 8 gün — ve BTC-önderliğinde ralli

```
gun        T3X 3g%   alt payi%
08-18       +1,13      19,42
08-19       +6,61      19,36    <- boga kirildi (18:15), AYNI GUN
08-20       +8,29      19,23
08-21      +15,47      19,06
```

TOTAL3X kırılmayla **aynı gün** döndü — önceden değil.
⚠️ Ve **alt payı DÜŞÜYOR** (19,42 → 19,06) TOTAL3X %15 artarken: altlar
yükseliyor ama **BTC daha hızlı**. BTC-önderliğinde ralli, altlar geride.

#### HÜKÜM

TOTAL1/2/3 **yön tahmin etmiyor** (dokuz göstergenin dokuzu şansın altında) ve
**öncü değil** (korelasyon yalnız eş anlı). Ama:
- **hiçbir epizodu kaçırmıyor** (0/20 · bot etiketi 36/49 kaçırıyor)
- gecikme 2-4 gün (bot etiketi 8 gün)

**Doğru kullanım: gerçek zamanlı termometre.** "Şu an neredeyiz" sorusunu
doğru ve hızlı cevaplıyor; "ne olacak" sorusunu cevaplamıyor. Bu, rejim
göstergeleri için **dördüncü** bağımsız kaynaktan aynı sonuç.

---

### 🔴 TOTAL ETİKETİYLE YÖN SEÇMEK — ÖLÇÜM ÖNERİYİ ÇÜRÜTTÜ (2026-08-21)

**Öneri (kullanıcı):** *"Rejim ayağında TOTAL kullanılacak en büyük aday. Rejim
etiketi koymadan bot yönü seçemiyor, bunu 2 gündür short açıp kaybetmesinden
anlıyoruz."*

**Öneriyi doğuran vaka gerçek ve büyük:**
```
19-21 Agustos:  SHORT N=28  -1.555,24 $  kazanan 4 (%14)
                LONG  N=12    +258,20 $  kazanan 7 (%58)
gune gore SHORT:  08-19 -261,24 · 08-20 -999,93 · 08-21 -294,07

ETIKETLER:  08-19  T3X 3g +6,61  -> TOTAL: BOGA   BOT: NOTR
            08-20  T3X 3g +8,29  -> TOTAL: BOGA   BOT: NOTR
            08-21  T3X 3g +15,47 -> TOTAL: BOGA   BOT: BOGA
```
TOTAL etiketi **2 gün önce** dönerdi; o iki günde SHORT **−1.261,17 $** kaybetti.

#### Ama 365 günde ölçünce ters çıkıyor

Etiket açıkken BTC'nin **ileri** getirisi:

```
etiket                     gun   ileri 1g   ileri 3g   ileri 7g   poz 7g
TOTAL BOGA (T3X 3g>+2)     107     -0,291     -1,034     -1,378     44%
TOTAL BOGA (T3X 3g>+5)      40     -0,278     -0,877     -0,783     38%
TOTAL NOTR (-2..+2)        117     -0,011     -0,308     -0,358     46%
TOTAL AYI  (T3X 3g<-2)     131     -0,126     +0,019     -0,805     49%
TUM GUNLER                 355     -0,138     -0,406     -0,830     46%
```

🔴 **BOĞA etiketi açıkken ileri getiri −1,378% — tüm günler ortalamasından
(−0,830%) DAHA KÖTÜ.** Yani etiket LONG dediğinde piyasa ortalamanın altında
gidiyor; **SHORT için ise en iyi anı işaret ediyor** (+1,378 kazanç).

Etiketle yön seçmek, **yönü ters seçmek** olurdu.

Mekanizma: `T3X 3g > +2` "altlar son 3 günde koştu" demek. Koşan geri veriyor —
ortalamaya dönüş. Termometre doğru ama **okunuşu ters.**

#### ⚠️ Bu ölçüm de rejim kirli — ve bu bilinerek yazılıyor

365 günlük pencere ağırlıklı **ayı** (taban oran %24,2, tüm günler ileri
getirisi −0,830%). Ayıda her ralli geri verir; bulgu kısmen bunun ifadesi
olabilir. Kullanıcının iki kez haklı çıktığı aynı kirlilik.

**Dolayısıyla:** öneri **desteklenmedi**, ama **temiz biçimde çürütülmedi** de.
Ayırt etmek için boğa rejiminde biriktirilecek veri gerekiyor — bugün başladı.

#### HÜKÜM

- 2 günlük vaka **gerçek**: etiket gecikmesi ölçülebilir para kaybettirdi (−1.261 $).
- 365 günlük taban **tersini** söylüyor: etiket açıkken LONG ortalamanın altında.
- `CLAUDE.md`: tek vaka ile taban oran çelişirse **taban oran kazanır.**
- **TOTAL etiketi yön seçmek için BOTA KONMAYACAK.**
- Değeri duruyor ama başka yerde: gerçek zamanlı durum tarifi (0/20 epizot
  kaçırmıyor, bot etiketi 36/49 kaçırıyor).

---

### 🟢🔴 TOPARLANMA BACAĞI (2025-04/05) — GÜN-KÜMELİ BAKINCA İŞARETLER **TUTUYOR** (2026-08-21)

**Kullanıcının seçtiği pencere:** 2025-04-03 → 05-14. Doğru seçim: ayıdan ATH'ye
giden toparlanma bacağı, bugünün analoğu, ama **42 günü var** (bugünkü bacağın 2
gününe karşı).

```
2025-04-03..05-14   85.623 -> 103.500  %+20,88   zirveden -25,2% -> -5,9%
2026-08-19..simdi   64.547 ->  73.658  %+14,11   zirveden -45,3% -> -41,6%
```

#### 🔴 ÖNCE BİR DÜZELTME — `21_boga_kesiti.py`'nin hükmü YANLIŞTI

O ölçümde *"4-6 alanın işareti rejimle dönüyor"* yazmıştım. **Havuzlanmış
(pooled) farka bakmıştım ve gün-kümesi hesaplamamıştım** (BOGA penceresi 2 gündü,
zaten hesaplanamıyordu).

Havuzlanmış fark, **seviye kaymasını ilişkiyle karıştırıyor**: boğada bütün ileri
getiriler pozitif; yüksek-`pos` coinler o günlerde daha sık olursa havuz
"yüksek pos → yüksek getiri" der. Gün-kümesi bunu kaldırır.

#### Gün-kümeli ölçüm — 42 gün vs 56 gün, +24 saat

```
alan       TOPARLANMA (42g)      AYI (56g)      isaret
           fark      gun-t      fark    gun-t
chg24    -0,2074    -3,23    -0,3964   -2,73    AYNI
pos      +0,4425    -3,06    -0,2503   -2,95    AYNI (gun-t'ye gore)
rel3     +0,3124    -2,81    -0,1144   -1,64    AYNI
last3    +0,1955    -4,19    -0,1294   -1,95    AYNI
vol_x    +0,5055    +1,27    +0,0027   +0,50    AYNI
funding  +0,2135    +0,11    +0,2312   +1,57    AYNI
```

**Gün-kümeli bakınca ALTI ALANIN ALTISI DA aynı işarette.**
Havuzlanmış farka bakınca üçü "dönmüş" görünüyor — o bir yapaylık.

```
evren ortalamasi:  TOPARLANMA +1,0961%  ·  AYI -0,2216%  ·  BUGUN +4,6110%
```
Değişen şey **seviye**, ilişki değil.

#### İlk rejim-KARARLI ilişki

```
yuksek chg24 / pos / last3 / rel3  ->  DUSUK ileri getiri
gun-kumeli |t|: 2,81 · 3,06 · 3,23 · 4,19   (ikisi 3,0 esigini asiyor)
Iki rejimde de ayni yon.
```

Yani **kesitsel ortalamaya dönüş**: son dönemde çok koşan, sonraki 24 saatte
görece geri kalıyor — hem ayıda hem toparlanmada.

⚠️ **Bu bir YÖN kuralı değil, GÖRECELI sıralama kuralı.** Toparlanmada herkes
kazanıyor (+1,10 ortalama); "düşük chg24" kolu daha çok kazanıyor. Ayıda herkes
kaybediyor; "düşük chg24" kolu daha az kaybediyor.

**HÜKÜM:** Bu, bu oturumda bulunan **ilk rejim-kararlı ilişki**. `21_boga_kesiti`
hükmü düzeltildi (havuz yapaylığı). Kural yazılmadan önce üçüncü bir rejimde
(ATH bölgesi) sınanmalı — henüz yapılmadı.

---

### 🟢 İLK REJİM-KARARLI İLİŞKİ — 5 pencerenin 5'inde aynı işaret (2026-08-21)

**Betik:** `scratchpad/poz_yol/24_rejim_kararliligi.py`
**Kullanıcının uyarısı:** *"Seçtiğin dönem yine yanlış, durum aynı değil ama ölç."*
Uyarı yerinde — ATH bölgesinde fonlama tavanda (%55-63), bugün tabanda (0,0050).
Yine de ölçüldü ve **aynı çıktı.**

#### Beş farklı rejim, aynı kesitsel ilişki

Gün-kümeli `t` **|** etki (üst çeyrek eksi alt çeyrek, ileri +24 saat):

```
alan     ATH 24-09/12   ATH 25-06/10   TOPARL 25-04   D.AYI 26-01   AYI 26-06   ayni
         (90-91 gun)     (136 gun)      (42 gun)      (74 gun)     (56 gun)
chg24   -7,29 | -2,310  -5,14 | -1,307 -3,23 | -1,884 -1,84 |-0,510 -2,73 |-0,649  5/5
pos     -8,08 | -2,241  -6,04 | -1,466 -3,06 | -2,048 -2,78 |-0,728 -2,95 |-0,561  5/5 <<<
last3   -7,20 | -1,397  -6,53 | -1,077 -4,19 | -1,539 -4,08 |-0,848 -1,95 |-0,314  5/5
rel3    -4,33 | -0,919  -5,12 | -0,794 -2,81 | -0,939 -1,46 |-0,248 -1,64 |-0,248  5/5
vol_x   +1,31 | +0,258  +0,21 | +0,030 +1,27 | +0,451 +1,74 |+0,410 +0,50 |+0,086  5/5
funding -0,29 | -0,036  -0,72 | -0,089 +0,11 | +0,022 +1,40 |+0,197 +1,57 |+0,244  2/5
```

Pencerelerin evren ortalamaları taban tabana zıt:
`ATH +? · TOPARLANMA +1,0961 · DERİN AYI −0,4490 · AYI −0,2216`
**Seviye değişiyor, ilişki değişmiyor.**

#### Ne söylüyor

**Son dönemde çok koşan, sonraki 24 saatte GÖRECE geri kalıyor.** Beş rejimde de.
En güçlüsü **`pos`** (20 barlık aralıktaki konum): beş pencerenin **beşinde de
|t| ≥ 2**, ATH'de −8,08.

Etki büyüklüğü: aralığın tepesindekiler dibindekilerden **24 saatte 0,56–2,24
puan geride**. Rejime göre 4 kat değişiyor ama işaret hiç dönmüyor.

⚠️ **YÖN kuralı değil, SIRALAMA kuralı.** Boğada herkes kazanır, düşük-`pos`
daha çok; ayıda herkes kaybeder, düşük-`pos` daha az.

#### 🔴 Bot tam tersini yapıyor

Bugün 11:00 ölçümü: radar medyanı `pos = 0,93` ve bot o anda **LONG** açtı
(`GAS · CRV · SPK · POL · SSV`, `chg24@giriş` +8…+25,5). Yani **aralığın
tepesinde, en kötü çeyrekte** alıyor.

#### Sınırlar

- `funding` **kararlı DEĞİL** (2/5) — ATH'de negatif, ayıda pozitif.
- `vol_x` işareti kararlı ama **hiçbir pencerede |t| ≥ 2** — zayıf.
- BUGÜN penceresi 2 gün, gün-kümesi hesaplanamadı.
- Bu bir **kesit** ilişkisi; mekanik (stop/hedef/maliyet) dahil edilmedi.
  `CLAUDE.md` sırası: **ham → mekanik → portföy.** Ham aşama bitti, mekanik yok.

**Bu, oturumdaki ilk rejim-kararlı bulgu.** Kural yazılmadan önce mekanikli
ölçüm ve ön-kayıtlı ileri sınav gerekir.

---

### 🟢🔴 TAVAN ÖLÇÜMÜ — ödül BÜYÜK, ama yakından görünmüyor (2026-08-21)

**Betik:** `scratchpad/poz_yol/36_tavan.py`
**Kullanıcının sorusu:** *"Bu kadar veri çektik, hiçbir veri sinyal vermiyor mu?"*

Şimdiye kadar hep *"şu kural işe yarıyor mu"* soruldu (9 çıkış fikri düştü).
Bu ölçüm **hiç sorulmayan** soruyu sorar: **aranacak şey ne kadar var?**

**Tasarım — sızıntı önlendi.** `32_rastgele_kontrol.py`'nin rastgele çıkışı
pozisyonun **ömrünü biliyordu**. Burada her pozisyon aynı `N` barlık pencereye
kırpılır, sabit-bar kolu her pozisyonda **aynı `j`**'de çıkar. Ömür bilgisi
hiçbir kola sızmaz. Pencereden önce kapanan pozisyon **elenmez**, kapanış
değerinde sabitlenir (yoksa 86 → 26 pozisyona düşüyordu = hayatta-kalma yanlılığı).

`pnl_pct` = **kaldıraçsız, yön düzeltilmiş fiyat yüzdesi** ([izleyici.py:127](izleyici.py#L127))
→ aşağıdaki puanlar brüt kenar ölçüsüyle aynı birimde. Her kolda tam 1 giriş +
1 çıkış var, **maliyet mesafeyi değiştirmez.**

**N = 86 pozisyon** (58 notr/ayı · 28 boğa), `pozisyon_izleme.jsonl`, ≥13 görüntü.

#### 1 · Aranabilir mesafe, mevcut kenarın 10-20 katı

```
pencere    ZAMANLAMA mesafesi (tepe-tut)     SECIM mesafesi (kaybedeni acma)
           A notr/ayi      B boga            A notr/ayi      B boga
 1 sa        +1,184        +1,082              +0,630        +0,649
 2 sa        +1,790        +2,753              +1,084        +1,631
 6 sa        +2,393        +3,802              +1,074        +1,956
12 sa        +3,307        +4,701              +1,540        +2,399
```

Kıyas: `funding` kapısının brüt kenarı **+0,2096**, net **−0,0683**
(bu dosya → maliyet doğrulaması). **Ödül yokluğu problem değil.**

#### 2 · Öngörü merdiveni — tavanın ne kadarı ne kadar ileri görmekle alınıyor

`k` = kaç bar ileri gören kâhin. Tavanın yüzdesi:

```
                        A) NOTR/AYI                B) BOGA
                   1sa   2sa   6sa  12sa      1sa   2sa   6sa  12sa
en iyi SABIT bar   %18   %15    %0   %4        %0   %40   %43   %46
kahin k=1  ( 5dk)  %31   %23  -%10 -%10       -%2   %35   %39   %43
kahin k=3  (15dk)  %81   %58   %16   %9       %39   %51   %51   %53
kahin k=6  (30dk)  %92   %86   %44  %29       %64   %68   %63   %62
kahin k=12 (60dk)  %96   %97   %63  %43       %79   %90   %80   %76
```

🔴 **`k=1` (5 dakika ileri) neredeyse hiçbir şey satın almıyor** — A'da uzun
ufuklarda **negatif** (−%10: yerel tepede çıkmak, asıl hareketi kaçırtıyor).
Tavanı almak için **30-60 dakika** ileri görmek gerekiyor.

**Anlamı:** aranan bilgi *"şu anda ne oluyor"* değil, *"önümüzdeki yarım saatte
ne olacak"*. 78 alanın hepsi birincisini ölçüyor.

#### 3 · Ve iki kümede çıkışın yönü TERS

```
A (notr/ayi)  tut = +1,379 (6sa)   en iyi sabit bar j=71 = pencerenin SONU  -> TUT
B (boga)      tut = -1,243 (6sa)   en iyi sabit bar j=12 = 60 dk           -> CIK
```

B'de **hiçbir sinyal olmadan**, sadece *"60 dakika sonra çık"* diyen sabit kural
tavanın **%43-46'sını** alıyor. A'da aynı kural **sıfır** alıyor.
Bu, `35_stopsuz.py`'nin bulgusuyla **bağımsız olarak aynı yere çıkıyor**:
değişken stop değil **süre**, ve doğru süre rejime göre ters.

#### 4 · Seçim ekseni vs zamanlama ekseni

Zamanlama mesafesi daha büyük **ama kümeye ve ufka göre 4 kat oynuyor ve işareti
dönüyor**. Seçim mesafesi daha küçük ama **iki kümede de aynı işaret ve benzer
büyüklük** (+0,63 … +2,40).

🟢 Ve elimizdeki **tek rejim-kararlı sinyal** (`pos`/`chg24`/`last3`/`rel3`,
5/5 pencere, bu dosya) tam olarak **seçim ekseninde** duruyor.

#### Sınırlar

- N=86 (58/28) · 8 gün · gün-kümeli t hesaplanmadı, bunlar **ortalama**dır.
- Kâhin kolları **tanımı gereği** ulaşılamaz; ölçülen şey ödülün büyüklüğü,
  bir kuralın performansı değil.
- Pencere kırpması pozisyonun gerçek çıkışını değil, sabit ufku ölçer.
- B kümesi 28 pozisyon — mesafe rakamları geniş güven aralığı taşır.

**HÜKÜM YAZILMADI.** Bot dosyalarına yazım: YOK.

---

### 🔴 HATA — FONLAMA 100 KAT BÜYÜK HESAPLANDI (2026-08-21, bulan: ölçümün kendisi)

**Kök neden:** [funding_indir.py:67](scratchpad/funding_indir.py#L67) indirirken
**zaten yüzdeye çeviriyor**:

```python
out += [{"t": int(x["fundingTime"]), "r": float(x["fundingRate"]) * 100} for x in d]
```

14 ölçüm betiği okurken **bir kez daha** `× 100` uyguladı.
Doğru kullanım `ab_funding_maliyetli.py:86`'da duruyordu: `fr[k]["r"]`, çarpımsız.

**Nasıl yakalandı:** `37_pos_mekanik.py` derin ayıda LONG alt kol için
**+7,145 net/işlem** verdi. Stop %5 · hedef %10 ile bir işlemin net'i fonlama
hariç **en fazla ≈ +4,04** olabilir (üst sınır hesabı `38_ayristir.py` başında).
Sınırın aşılması veriye değil **alete** işaret etti. Doğrulama: `funding_gecmis`
içinde tam `−2,00000` değerleri var — bu Binance'in **%−2 fonlama tavanı**,
yani `r` zaten yüzde.

#### Etkilenen betikler — iki sınıf

**A) Fonlamayı MALİYET olarak kullananlar → sonuç BOZUK, yeniden koşulmalı**

```
asgari_stop.py · ileri_rr.py · katilim_filtresi.py (kontrol edilmeli)
poz_yol/ 09_boga_bacagi · 11_ayidan_cikis · 12_holdout · 28_cikis_taramasi
         29_pump_yon · 35_stopsuz · 37 · 38  (37/38 DUZELTILDI ve yeniden kosuldu)
```

Tipik bozulma: 24 saatte 3 dilim × ~0,005 medyan × 100 = **±1,5 puan** sahte
maliyet/kredi. LONG'da sahte maliyet, SHORT'ta sahte kredi.

⚠️ **Bu, `28_cikis_taramasi`'nın *"46 varyantın hiçbiri iki kümede artı değil"*
hükmünü ve `35_stopsuz`'un tablosunu ŞÜPHELİ yapar.** İkisi de yeniden koşulmadan
alıntılanmaz.

**B) Fonlamayı ALAN (dilim değişkeni) olarak kullananlar → ETKİLENMEDİ**

```
poz_yol/16_rejim_kosullu · 24_rejim_kararliligi · 23_toparlanma_bacagi (alan kısmı)
```

Çeyrek bölmesi ve t **sıra tabanlıdır**; `×100` monotondur, sıralamayı değiştirmez.
🟢 **`pos` için 5/5 rejim bulgusu AYAKTA.**

**Ders (`CLAUDE.md` → mimari tuzaklar adayı):** bir birim dönüşümü **indirici ile
okuyucu arasında iki kez** uygulanabilir. `py_compile` ve `pyflakes` bunu görmez.
Yakalayan şey **büyüklük mantığı** oldu: *"bu sayı mekanik olarak mümkün mü?"*
Her ölçümde bir **üst sınır hesabı** yapılırsa bu sınıf kapanır.

---

### 🟡 `pos` MEKANİK AŞAMASI — A GEÇTİ, B DÜŞTÜ (2026-08-21)

**Ön-kayıt:** `scratchpad/poz_yol/ON_KAYIT_pos_mekanik.md`, commit **cdbc4b5**,
koşumdan **önce** yazıldı. Ölçütler değiştirilmedi.
**Betikler:** `37_pos_mekanik.py` · `38_ayristir.py` (tanı) · `39_b2.py` (B2)
**N:** 636.475 aday · 5 pencere · 567 sembol · fonlama düzeltmesi dahil

#### Sonuç — LONG, stop %5, maliyet %0,1726, fonlama dahil

```
pencere            HAM fark   MEKANIK fark  gun-t   ALT kol net  UST kol net
ATH 24-09/12        +2,241       +1,726     +6,58     +1,069       -0,656
ATH 25-06/10        +1,466       +1,081     +5,97     +0,459       -0,623
TOPARLANMA 25-04    +2,048       +1,100     +2,89     +0,728       -0,372
DERIN-AYI 26-01     +0,728       +0,488     +2,43     -0,240       -0,728
AYI 26-06/08        +0,561       +0,420     +3,96     -0,144       -0,564
```

#### Kapılar

| kapı | ölçüt | sonuç |
|---|---|---|
| A1 | fark > 0, ≥4/5 | **5/5 ✅** |
| A2 | gün-kümeli t ≥ +2,0, ≥3/5 | **5/5 ✅** |
| A3 | üç stopta da ≥4/5 | **✅** |
| A4 | en iyi 3 sembol çıkınca ≥4/5 | **5/5 ✅** (fark neredeyse hiç düşmüyor) |
| **KAPI A** | | **GEÇTİ** |
| B1 | alt kol net > 0, ≥3/5 | 3/5 ✅ |
| B2 | alt kolun kendi t'si ≥ +2,0, ≥2/5 | **1/5 ❌** (en iyi ikinci: +1,97) |
| **KAPI B** | B1 ∧ B2 | **DÜŞTÜ** |
| C1 | SHORT'ta ters işaret, ≥4/5 | **5/5 ✅** |

#### Zorunlu tanı (ön-kayıtta şart koşulmuştu)

Stop-olma oranı alt/üst: `31,7/29,8` · `33,7/28,1` · `38,4/29,8` · `39,7/35,8` ·
`28,9/29,7` → **en fazla 1,29 kat.** Eşik 1,5'ti → **mekanik iki kolu eşit ölçüyor.**

Ve stop, kenarın **kaynağı değil**: alt kolda stop ortalamada **zarar ettiriyor**
(ATH 24: −0,172 · TOPARLANMA: −0,750 puan). Sinyal stopa rağmen kazanıyor.

Fonlama farkı (düzeltilmiş): **+0,007 … +0,038 puan** — ihmal edilebilir.
`pos` fonlamanın vekili **değil**.

#### HÜKÜM — ön-kayıt karar tablosundan aynen

**A ✓ · B ✗ · C ✓ → "Sinyal gerçek, tek başına YÖN KURALI DEĞİL."**

İlişki mekanikten sağ çıktı (5/5, t 2,43–6,58) ama düşük-`pos` kolu **kendi başına
güvenilir biçimde kâr etmiyor**: boğa/toparlanmada artı, iki ayı penceresinde eksi.

**Bu bir sıralama/süzgeç sinyalidir, yön sinyali değil.**
Süzgeç olarak sınanması **ayrı ön-kayıt** gerektirir. **Bot değişmez.**

⚠️ Not: bu ölçüm **portföy aşamasını kapsamaz** (8 pozisyon sınırı, boyutlandırma,
kuyruk sırası). `CLAUDE.md` sırasının üçüncü aşaması yapılmadı.

---

### 🔴 FONLAMA HATASININ GERÇEK KAPSAMI — daha DAR çıktı (2026-08-24)

2026-08-21'de *"14 betik etkilendi"* yazmıştım ve `short_kayip/` ailesini de
şüpheli ilan etmiştim. **Yanlıştı.** Denetlendi:

```
scratchpad/funding_gecmis/        r = YUZDE    (funding_indir.py:67 zaten *100 yapiyor)
scratchpad/short_kayip/fonlama/   r = ONDALIK  (short_kayip/ortak.py:82 ham birakiyor)
```

**İki ayrı önbellek, aynı alan adı `r`, FARKLI BİRİM.**

- `funding_gecmis` okuyan betikler `*100` uygularsa **100 kat şişer** → hata buradaydı.
- `short_kayip/ortak.py:100` `*100` uygular ama kendi ondalık önbelleğini okur → **DOĞRU**.

Doğrulama: `KAPI KARNESİ`nin D1 kontrolü fonlamayı **−0,1519** raporlamıştı; 100 kat
şişik olsaydı ≈ −15 çıkardı.

#### Ayakta kalan hükümler (yanlışlıkla şüpheli ilan edilmişti)

```
KAPI KARNESI [:2369] · CEKIRDEK KAPI [:2297] · STOP MALIYETI [:2085]
ERKEN GURULTU [:2143] · MALIYET DOGRULAMASI [:2197]   -> HEPSI AYAKTA
```

#### Gerçekten etkilenenler

`funding_gecmis` okuyup `*100` uygulayanlar: `asgari_stop` · `ileri_rr` ·
`katilim_filtresi` · `poz_yol/09` · `11` · `12` · `16` · `23` · `24` · `28` · `29` ·
`35` · `37` · `38`. **Hepsi düzeltildi.**

**Ders — `CLAUDE.md` tuzak adayı:** *aynı ada sahip iki önbellek farklı birimde
olabilir.* Alan adı (`r`) birimi taşımıyordu. Yakalayan şey **üst sınır hesabı** oldu.
Kural önerisi: fonlama okuyan her betik, ilk kaydın büyüklüğünü **iddia etsin**
(`assert abs(median) < 0.5` gibi) — birim karışması sessiz kalmasın.

---

### 🔴 DÜZELTİLMİŞ FONLAMAYLA YENİDEN KOŞUM — iki hüküm DEĞİŞTİ (2026-08-24)

#### 1 · `35_stopsuz` — ESKİ HÜKÜM YANLIŞTI

```
A) NOTR/AYI N=111   stop%3   stop%5   stop%8   STOP YOK   (liq%)
1sa                 -0,034   -0,116   -0,119    +0,005     2
4sa                 +0,081   +0,036   +0,169    +0,628     3
8sa                 -0,159   +0,084   +0,292    +0,769     6
24sa                -0,088   +0,152   +0,137    +1,087    12
72sa                -0,582   -0,325   -0,269    +1,472    21
```

Eski (hatalı) tabloyla *"her iki kümede de uzun tutma monoton olarak kötü"* denmişti.
**Düzeltilmiş veride TERSİ:** stopsuz kol her ufukta artı ve süreyle **monoton artıyor**.
72 saatte stoplu-stopsuz farkı **2,05 puan**.

⚠️ Bedeli: likidasyon %2 → **%21**. Ve **B (BOĞA) kümesi ölçülemedi** — `perp_seri`
2026-08-21'de bitiyor (55 saat bayat). Tek kümelik bulgu.

#### 2 · `12_holdout` — HÜKÜM 2 ÖLÇÜLMEMİŞ, HÜKÜM 1 DÖNDÜ

```
HUKUM 1  SHORT yigini    N=4833  gun=8  +0,1660  t 0,56  5/8  -> henuz CURUTULMEDI
HUKUM 2  funding kapisi  OLCULEMEDI (N=107, gun=2)
HUKUM 3  pump engeli     -> COKTU
HUKUM 4  chg24>%40 LONG  -> COKTU
```

🔴 **Kayıtlı *"dört hükmün dördü de ayakta kalmadı"* yanlıştı.** Doğru sayım:
**iki çöktü, biri henüz çürütülmedi, biri hiç ölçülemedi.**

Hüküm 2'nin eski sonucu **100 kat gevşek bir kapıyla** üretilmişti — botun gerçek
kapısı 8 günlük holdout'ta yalnız **107 kez** tetikleniyor, ölçüm için yetersiz.

#### 3 · `16_rejim_kosullu` — kapı kontrolden İYİ çıktı (ama anlamsız)

```
funding <= -0,05 (KAPI)     TUM 2 YIL  N= 9714  ay-ort +0,0585  t +0,62
funding >  -0,05 (KONTROL)  TUM 2 YIL  N=135964 ay-ort -0,0100  t -0,08
```

Rejim kırılımı işareti **döndürüyor** (ATH +0,5150 · DÜZELTME +0,0485 ·
DERİN-AYI −0,0519) → *"2 yıllık ortalama hiçbir gerçek koşula karşılık gelmiyor"*
hükmü [:2653] **güçlendi**.

#### 4 · `ileri_rr` — R/R çıkış kuralı hükmü DEĞİŞMEDİ

```
A_funding  N=4327  kontrol +0,082  kural +0,009  fark -0,073  t_kume -0,30
B_ma50ucuz N=4443  kontrol -0,227  kural -0,222  fark +0,004  t_kume +0,02
```
Kural hâlâ kontrolü geçemiyor. N 17.836 → 4.327'ye düştü (kapı artık gerçek eşikte).

**HÜKÜM YAZILMADI** (35 ve 12 için yeni ön-kayıt gerekir). Bot dosyalarına yazım: YOK.

---

### 🔬 OLAY SEVİYESİ ÖRNEKLEME + YÖN/OYNAKLIK AYRIMI (2026-08-24)

> **HÜKÜM YAZILMADI.** Aşağıdakilerin hiçbiri ön-kayıtlı değildir; tasarım tek
> geçişte seçildi. Bunlar **yöntem gösterimi ve betimleyici ölçüm**dür. Kural
> adayı olmaları için ön-kayıt + holdout + mekanik aşaması gerekir.
> Betikler: `scratchpad/olay_seviyesi/01..04`. Bot dosyalarına yazım: **YOK**.

#### A · Olay seviyesi örnekleme — "N küçük" çoğu zaman bir TANIM hatası

Kullanıcı tespiti: *"son bir hafta nötrken ralli yapması 2 yılda sadece 2 kere
olmuş, biz bunu yanlış rejimin örneğiyle kıyaslıyoruz."* **Tespit doğru çıktı** —
ama kıtlık verinin değil, **gözlem biriminin** içindeydi.

Aynı durum (`7 gün yatay → 1 saatte +%5 sıçrama`) iki ayrı birimde sayıldı.
Eşikler `01_kalibre.py` dağılımlarından, **sonuca bakmadan** seçildi
(alt ~%30 dilim: `|7g getiri| ≤ %5` · `168sa saatlik std ≤ %0,80`).

```
PIYASA-TAKVIM SEVIYESI  (endeks_gunluk.json, 741 gun)
    7 satir -> ardisik gunler birlestirilince  4 BAGIMSIZ OLAY
    son 13 ayda: 1 olay                        -> hicbir istatistik kurulamaz

SEMBOL-OLAY SEVIYESI    (klines_1h_uzun, 566 sembol, 7.010.384 bar)
    ham sicrama (>= +%5, tek saat)      37.242
    OLAY    (sicrama + onu SAKIN)          476     251 bagimsiz gun · 274 sembol
    KONTROL (sicrama + onu sakin DEGIL) 19.621
    (ayni sembolde 24 bar bekleme -> ortusen pencereler elendi)
```

**4 → 476.** Yeni veri toplanmadı, yeni araç kullanılmadı; yalnız soru
*"piyasa haftada ne yaptı"* yerine *"coin saatinde ne oldu"* diye soruldu.

Yoğunlaşma denetimi: en büyük **sembol payı %1,3** · en büyük **gün payı %2,7**
→ tek sembol/gün taşımıyor.

Karne (gün-kümeli, aynı gün içinde eşleşmiş — iki AYRIK grup, alt küme değil,
dolayısıyla iki-örneklemli istatistik geçerli):

| ufuk | olay | kontrol | fark | t |
|---|---|---|---|---|
| 4 sa | −0,48% | −0,15% | −0,47% | −1,12 |
| 24 sa | −2,27% | −0,56% | **−2,03%** | **−3,45** |
| 72 sa | −3,37% | −0,21% | **−3,28%** | **−3,55** |

Rejim kırılımı (24 sa): `ATH_BOLGESI` +0,34% (t=+0,31, N=101) ·
`DUZELTME` −2,92% (t=−3,97, N=89) · `DERIN_AYI` −1,66% (t=−2,28, N=286).
→ İşaret **dönmüyor** ama ATH'de yok oluyor; rejim ayrımı zorunlu.

⚠️ Ham fiyat getirisi — **fonlama ve mekanik dahil DEĞİL** (CLAUDE.md sırası
gereği bu birinci aşama). 4 saatte etki yok; botun medyan tutma süresi 2,5 saat
olduğu için mevcut hâliyle bota uygulanamaz.

**Devri alınacak ders:** *"N yetersiz, ölçülemedi"* diye kapanmış her kutu bu
yöntemle yeniden açılabilir — örn. `12_holdout` HÜKÜM 2 (`N=107, gün=2`).

#### B · Yön mü oynaklık mı tahmin edilebilir? — `04_yon_vs_oynaklik.py`

200 sembol, **her biri ayrı** hesaplandı, sembol medyanı raporlandı.

```
YON      gecmis getiri -> gelecek getiri        aciklanan pay
   1 sa   -0,017                                     %0,03
   4 sa   +0,007                                     %0,00
  24 sa   -0,019                                     %0,04
  24sa blok -> sonraki blok   -0,018                 %0,03

OYNAKLIK gecmis salinim -> gelecek salinim
   1 sa   +0,294                                     %8,64
   4 sa   +0,182                                     %3,32
  24 sa   +0,142                                     %2,02
  24sa blok -> sonraki blok   +0,459                 %21,08
```

Sembol dağılımı (blok düzeyi) — **kararlılık farkı burada**:

```
             %5      %25    MEDYAN    %75     %95    korelasyonu POZITIF cikan
  YON      -0,160  -0,079  -0,018  +0,028  +0,134           %43   <- yazi-tura
  OYNAKLIK +0,238  +0,387  +0,459  +0,538  +0,677          %100   <- 198/198
```

**Çıplak fiyat serisinden yön çıkmıyor (198 sembolün %43'ü, yani gürültü);
oynaklık 198'de 198'de aynı işaret.** Bu, *"yön tahmin edilemez"* demek DEĞİL —
defterin kendi kenarı (aşağıda: pozisyonların %96'sı artıya geçiyor) fiyat
şeklinden değil, radarın alanlarından geliyor. Sonuç şu kapsamdadır:
**fiyat serisine yön sorulmaz.**

Karar sonucu: TimesFM'e ana iş olarak **dağılım/oynaklık** verilecek; yön aynı
ileri geçişte bedava geldiği için **tavan ölçümü olarak** yine de kaydedilecek.

#### C · Defter röntgeni — ANLIK GÖRÜNTÜ (2026-08-24, `pozisyon_ozet.jsonl` N=198)

⚠️ **Anlık görüntüdür, drift eder.** Kanıt değeri rakamların büyüklüğündedir.

```
Hic olmazsa bir an artiya gecen   191  (%96)     ARTIDA KAPANAN   83  (%42)
Bir an %2'yi goren                120  (%61)     TOPLAM SONUC   -2.753 $
Bir an %5'i goren                  67  (%34)
Bir an %10'u goren                 23  (%12)

MFE >= %2  -> 120 pozisyonun 41'i  (%34) EKSIDE kapandi
MFE >= %5  ->  67 pozisyonun  7'si (%10) EKSIDE kapandi
MFE >= %10 ->  23 pozisyonun  0'i  ( %0) EKSIDE kapandi

CIKIS SEBEBI   STOP 159 (%80) -9.296 $ | TP2 34 (%17) +5.888 $ | ZAMAN_STOP 5 +656 $
TEPEYE SURE    medyan 1,59 sa  (%45'i ilk 1 saatte)     TUTMA medyan 2,50 sa
MAE            medyan %3,20    %90 dilim %7,66
```

**İki bağımsız kanıt aynı eşiği gösteriyor:** çıkış taramasında geçen tek varyant
`sabit %10 hedef` idi; burada **%10'u gören 23 pozisyonun 23'ü de artıda kapandı.**

Aritmetik kerteriz: stop (−58 $ ort.) → TP2 (+173 $ ort.) salınımı 231 $.
`2.753 ÷ 231 ≈ 12` → **defter başabaşa 12 pozisyon uzakta.** Eşdeğeri: stop
başına ortalama zarar %30 azalsa aynı yere gelinir. Teşhis **giriş değil,
mekanik** tarafını işaret ediyor.

#### D · Hacim tezi — kullanıcı hipotezi sınandı (2026-08-24)

Kullanıcı: *"hacim elimizdeki en değerli veri."* `04` ile **aynı yöntem ve aynı
tohum** (200 sembol, her biri ayrı, sembol medyanı), 24 saatlik bloklar.
Betikler: `scratchpad/olay_seviyesi/05_hacim.py` · `06_hacim_kismi.py`.

```
HACIM NEYI SOYLUYOR?                       aciklanan pay   ayni isaretli sembol
  hacim -> gelecek HACIM         +0,860         %74,0             %100
  hacim -> gelecek OYNAKLIK      +0,454         %20,6             %100
  islem sayisi -> OYNAKLIK       +0,461         %21,3             %100
  hacim -> hareket BUYUKLUGU     +0,264          %7,0              %99

HACIM YON SOYLUYOR MU?
  hacim -> gelecek YON           -0,033          %0,11             %24
  taker ALIS orani -> YON        +0,008          %0,01             %57
```

**Hacim, veri setindeki EN TAHMİN EDİLEBİLİR seri** (%74 — fiyat oynaklığının
üç katı). Ama **yön söylemiyor**: 198 sembolün yalnız %24'ünde aynı işaret.

##### Kısmi korelasyon — "tek bant" tuzağından KAÇAN bir ölçüm

CLAUDE.md uyarısı: *"yeni sinyal çoğu zaman aynı şeydir."* Hacim ile oynaklık
aynı şey mi diye sınandı — biri sabitlenip diğeri ölçüldü:

```
HAM                                            KISMI (digeri SABIT)
  hacim    -> gel. oynaklik  +0,454  %100        +0,218   %98
  oynaklik -> gel. oynaklik  +0,459  %100        +0,230   %98
```

**İkisi de hayatta kalıyor.** Hacim, oynaklığın kılık değiştirmiş hâli DEĞİL;
198 sembolün 194'ünde bağımsız katkı veriyor. İkisi birlikte, her biri tek
başına olduğundan iyi.

⚠️ **Kapsam:** ikisi de hâlâ **aynı banttan** (Binance perp işlem akışı) geliyor.
Kısmi bağımsızlık, *yeni bilgi kaynağı* demek değildir — bant içinde
tamamlayıcılık demektir.

⚠️ **`taker → yön` sonucu 24 SAATLİK blokta ölçüldü.** Botun `taker_15`/`taker_60`
kapıları çok daha kısa ufukta çalışıyor; **o ufuk ölçülmedi**, bu sonuç oraya
taşınamaz.

**Tasarım sonucu:** TimesFM'e yalnız fiyat değil, **hacim de kovaryat olarak**
verilecek (TimesFM 2.5 XReg destekliyor). Kullanıcı hipotezi planı değiştirdi.

---

### 🔴 TimesFM KUANTİL KAPSAMA TESTİ — **KALDI** (2026-08-24)

Ön-kayıt: `scratchpad/tfm/ON_KAYIT_kapsama.md` (**koşturmadan önce** yazıldı).
Betikler: `scratchpad/tfm/01_topla.py` · `02_karne.py`. Ayrı venv, salt-okuma.
**N=7.999 nokta · 564 sembol · 354 bağımsız gün · 2025-09-01..2026-08-20**
(sızıntısız pencere: TimesFM 2.5 Eylül 2025'te yayımlandı, bu veri sonrasında oluştu).
Yoğunlaşma: en büyük sembol payı **%0,3** · en büyük gün payı **%0,5**.

| ölçüt | eşik | 4sa | 24sa | hüküm |
|---|---|---|---|---|
| 1 · Dürüstlük (P10–P90) | %75–85 | **%77,9** ±1,2 | **%76,1** ±1,8 | ✅ GEÇTİ |
| 4' · Uç (P20–P80) | %55–65 | **%57,6** | **%56,3** | ✅ GEÇTİ |
| 3 · Rejim (üçünde de) | %70–90 | ATH %75,4 · DÜZ %79,6 · AYI %76,5 | ATH %72,6 · DÜZ %78,4 · AYI %76,2 | ✅ GEÇTİ |
| **2 · ATR'den dar** | dar olmalı | **%4,03 vs ATR %3,66** | %8,95 vs ATR %9,07 | 🔴 **KALDI** |

Ölçüt 2 ayrıntısı (zaman bölmeli; ATR `k` kalibrasyon yarısında TimesFM'in kendi
kapsamasına ayarlandı, test yarısında uygulandı):

```
      TEST kapsama                TEST band genisligi
 4sa  TimesFM %78,5  ATR %79,3    TimesFM %4,03   ATR %3,66   -> ATR %9 DAR
24sa  TimesFM %76,0  ATR %78,0    TimesFM %8,95   ATR %9,07   -> berabere/ATR
```

**ATR her iki ufukta da DAHA YÜKSEK kapsamayı DAHA DAR bandla sağlıyor** (4sa'te
açık farkla; 24sa'te %2 puan fazla kapsamayı %1,3 fazla genişlikle). Ön-kayıt
*"1 ve 2 geçmezse TimesFM bu projede kullanılmaz, konu kapanır"* diyordu.

> **HÜKÜM: TimesFM fiyat-serisi kuantilleri için KULLANILMAYACAK.**
> Dürüst ve rejim-kararlı çıktı — ama **botta zaten kurulu olan Wilder-ATR'yi
> geçemedi.** Yeni araç, yerine geçtiği şeyden iyi olmak zorundaydı; değil.

#### İkincil (tavan ölçümü): YÖN

```
 4sa isabet %51,2 ±1,2   (guven araliginin alt ucu %50,0)
24sa isabet %51,0 ±1,4   (guven araligi %50'yi ICERIYOR)
```

**Rastgeleden ayırt edilemiyor** — `04_yon_vs_oynaklik`'ın öngördüğü gibi
(çıplak fiyattan yön çıkmıyor, 198 sembolün %43'ü). *"Fiyat bandı tükendi"*
hükmü **güçlendi**: 200M parametreli, 100 milyar zaman noktasıyla eğitilmiş bir
model de bu seriden yön çıkaramıyor.

#### 🔑 ASIL KAZANÇ — teşhis yer değiştirdi

ATR, **iyi kalibre bir oynaklık ölçer** çıktı (kalibre edildiğinde %79,3 kapsama,
TimesFM'den dar). Yani stop probleminin kaynağı **oynaklık tahmini DEĞİL** —
o zaten doğru ölçülüyor. Sorun ATR'ye uygulanan **çarpan/yerleşim kararında**.

Bu, `pozisyon_ozet` röntgeniyle (MAE medyan %3,20 · stop %2,86–9,31 · stop-olma
%50–76) birleştiğinde şunu söylüyor: **doğru çarpan, elde zaten olan ATR ile,
olay seviyesi yöntemiyle bedava ölçülebilir.** Temel modele gerek yok.

#### Yöntem notu — ön-kayıt bu sefer işe yaradı

Ölçüt 2 yazılı olmasaydı, *"kapsama %77,9, model dürüst!"* görülüp **geçti ilan
edilecekti.** Testi öldüren şey genişlik kıyasıydı ve o kıyas yalnızca
**önceden yazıldığı için** koşuldu.

⚠️ **Kapsam:** bu test **yalnız fiyat serisi** ile yapıldı. Hacim kovaryatlı
(XReg) varyant **ölçülmedi**. Denenecekse **yeni bir ön-kayıt** gerekir ve
**ikinci karşılaştırma olarak sayılır** (çoklu karşılaştırma kuralı).

#### E · KÜME AYIRMA — kullanıcı önerisi sınandı (2026-08-24)

Kullanıcı önerisi: *"düşen / stabil / yükselen diye üç küme yap, geçmişteki
sonucu zaten biliyoruz, model 1 saatlik tahmin yapsın."* **Yeni koşum
gerekmedi** — `01_topla.py`'nin ham çıktısında hem tahmin hem gerçekleşen var.
Betik: `scratchpad/tfm/03_kume_ayirma.py`. Gruplama **sonuca göre** yapıldı;
bu meşrudur çünkü **değerlendirme ekseni**dir, bağlam/eğitim seçimi değil.

```
4 SAAT (esik +-%1)          gercek ort    MODEL NE DEDI    ongordugu band
  DUSEN     N=2048            -2,69%         -0,173%           %6,55
  STABIL    N=4041            -0,03%         +0,014%           %4,61
  YUKSELEN  N=1910            +2,86%         -0,072%           %6,22
```

**Model, %2,86 yükselecek coine ile %2,69 düşecek coine neredeyse AYNI şeyi
söylüyor** (−0,07% vs −0,17%). Ama stabil gruba **belirgin dar band** veriyor.

| ayrım | skor | 4 sa | 24 sa |
|---|---|---|---|
| yükselen vs düşen | model **yön** tahmini | **%52,1** | **%52,0** |
| hareketli vs stabil | model **band genişliği** | **%68,0** | **%65,2** |
| yükselen vs düşen | band genişliği | %48,5 | %49,0 |

Gün-kümeli yön AUC: **%50,9 ±5,5** (4sa) · **%52,9 ±5,8** (24sa) —
**iki güven aralığı da %50'yi içeriyor.**

##### 🔴 Ve ayırt etme yeteneği TimesFM'e ait DEĞİL

Aynı test, skor olarak ATR/fiyat konularak tekrarlandı:

```
                                     4 sa      24 sa
  TimesFM band genisligi   -> AUC   %68,0     %65,2
  ATR / fiyat  (bedava)    -> AUC   %67,4     %64,8
  fark                              +0,6      +0,4   -> FARK YOK
```

> **HÜKÜM: Üç kümeli tasarım işe yarıyor ama TimesFM'e gerek yok.**
> "Hareketli mi stabil mi" ayrımını **ATR zaten yapıyor** (AUC %67,4).
> "Yükselecek mi düşecek mi" ayrımını **hiçbiri yapamıyor** (%52, GA %50'yi içeriyor).
> TimesFM'in katkısı **0,4–0,6 puan** — 925 MB ve ayrı ortam karşılığında.

**TimesFM üzerine ÜÇÜNCÜ ve son olumsuz ölçüm.** Kapsama (ölçüt 2 kaldı) ·
yön isabeti (%51,2, rastgele) · küme ayırma (ATR'ye eşit). **Konu kapandı.**

⚠️ **Kapsam:** hepsi **çıplak fiyat serisi** üzerinedir. Defterin kendi yön kenarı
(pozisyonların %96'sı artıya geçiyor) radarın 28 alanından geliyor; o girdi
**TimesFM'e verilemez** — mimarisi tek seri alır, etiketli örnek almaz.
Kullanıcının *"örnekleri göster, farkı öğrensin"* fikri mimari olarak
**TabFM-biçimlidir**, TimesFM-biçimli değil.

---

### ⚖️ ATR STOP ÇARPANI — olay seviyesinde (2026-08-24) · **HÜKÜM YAZILMADI**

Ön-kayıt: `scratchpad/stop_carpani/ON_KAYIT.md` (**koşturmadan önce**, 5 ölçüt).
Betikler: `01_kol_b.py` · `02_kol_a.py` · `03_karne.py`. Salt-okuma.
Fonlama **dahil** — birim iddiası betikte `assert` ile korunuyor (medyan |r|
%0,0050, yüzde/8sa). Mekanik yalıtıldı: **hedef yok, iz süren yok**, sadece
`k×ATR` stop + `H` saat zaman çıkışı.

**Ölçülen mevcut durum:** bot `k = 1,50` kullanıyor (`stop/atr_giriste` medyan
1,50, %75 dilim 1,51) · medyan kaldıraç **3x** · medyan notional 2.052 $.

#### KOL B — vekil girişler · N=13.159 · **717 gün** · 532 sembol

Vekil olay: `chg24 ≥ +%20` → SHORT · `chg24 ≤ −%20` → LONG. 24 bar bekleme.

```
SHORT N=8.562         2sa      4sa      8sa     24sa   stop-olma
  k=1,50 (BOT)      +0,238   +0,224   +0,274   +0,404     %61
  k=3,00            +0,349   +0,334   +0,376   +0,498     %40
  STOPSUZ           +0,424   +0,433   +0,339   +0,076      %0

LONG  N=4.597
  k=1,50 (BOT)      +0,394   +0,624   +0,493   +0,531     %49
  k=3,00            +0,489   +0,813   +0,673   +0,807     %18
  STOPSUZ           +0,521   +0,900   +0,707   +1,174      %0
```

**Eğri `k` ile MONOTON artıyor** (ölçüt 3 ✅). SHORT'ta 24sa'te stopsuz çöküyor
(+0,076) — **SHORT'un sınırsız yukarı riski var, LONG'un yok.** Asimetri gerçek.

| ölçüt | sonuç |
|---|---|
| 1 · Holdout (k* ilk yarıda seçildi, ikinci yarıda kıyaslandı) | ✅ **GEÇTİ** — SHORT 4/4 ufuk (t +2,02 · +1,87 · +0,45 · +0,41) · LONG 4/4 (t +2,13 · +1,89 · +0,40 · +2,01) |
| 2 · Rejim | ✅ **3/3** her ufukta |
| 3 · Eğri biçimi | ✅ monoton, testere değil |
| 5 · Likidasyon (3x) | k=1,50 %0,22 · k=3,00 **%1,17** · k=6,00 %4,46 · STOPSUZ **%10,37** |

Likidasyon tavanı: 3x'te eşik ~%30 ters hareket → **`k_eşdeğer ≈ 7,4`**.
Yani `k ≤ 4` bölgesi likidasyondan güvenli mesafede; **stopsuz değil.**

#### KOL A — botun GERÇEK girişleri · N=83 · **yalnız 7 gün** → CEVAP VEREMİYOR

`atr_giriste` yalnız `pozisyon_izleme.jsonl`'de var ve o dosya **2026-08-13'te
başlıyor**; mumlar **2026-08-21'de bitiyor**. 161 girişin 83'ü oynatılabildi.

```
k=3,0 vs k=1,5   (tum ornek, 7 gun)
   2sa  fark -0,040   %95 GA [-0,34 , +0,26]   -> AYIRT EDEMIYOR
   4sa  fark -0,055   %95 GA [-0,47 , +0,36]   -> AYIRT EDEMIYOR
   8sa  fark -0,084   %95 GA [-0,52 , +0,35]   -> AYIRT EDEMIYOR
  24sa  fark -0,173   %95 GA [-1,04 , +0,69]   -> AYIRT EDEMIYOR
```

**Dört ufkun dördünde de güven aralığı sıfırı içeriyor** ve genişliği ±0,3–1,0.
KOL B'nin bulduğu etki (+0,05…+0,25) bu aralığın **içinde kaybolur**.
→ İki kol **çelişmiyor; biri kör.** Ayrışmanın sebebi budur (ön-kayıt ölçüt 4
"ayrışırsa araştırılır" diyordu — araştırıldı).

#### 🔴 HÜKÜM YAZILMADI — kendi kuralımız gereği

Ön-kayıt: *"1 geçip 4 kalırsa hüküm yazılmaz."* Ölçüt 1 geçti, **ölçüt 4
doğrulanamadı** → CLAUDE.md *"şüphede DAİMA statüko"*. **`k = 1,50` kalır.**

**Kanıtın yönü yine de tek taraflı:** 717 gün, iki yön, üç rejim, holdout —
hepsi *"1,50 fazla sıkı"* diyor. Ama botun kendi girişlerinde doğrulanmadı.

⚠️ **Büyüklük ölçeği (KABA, vekil olaylardan taşındı, KOL A doğrulamadı):**
+0,16…+0,25 puan × 2.052 $ × 204 pozisyon ≈ **+670…+1.046 $**.
Defterin açığı **−2.753 $**. Yani bu düzeltme **açığın ancak %25–40'ını** kapatır
— tek başına yetmez.

#### Ne bu soruyu bitirir

KOL A'nın büyümesi. `atr_giriste`'ye bağımlılık kaldırılıp ATR **mumlardan
yeniden hesaplanırsa** KOL A 83 → ~204 olaya çıkar (defter 2026-07-23'te
başlıyor). Yine de az; asıl çözüm botun koşmaya devam etmesi.

---

### 🔴 AÇIĞIN KAYNAĞI — kullanıcı tespiti DOĞRULANDI, önceki teşhisim YANLIŞTI (2026-08-24)

Kullanıcı: *"18-21 arası short rejimde olduğu için short kovaladı, açığın bir
kısmı ondan; yoksa başabaştı."* **Ölçüldü — doğru, hatta daha güçlü.**

#### Mutabakat denklemi önce koşuldu (CLAUDE.md zorunlu)

```
10.000,00  baslangic_bakiye
-2.847,00  defter P&L (id ile birlestirilmis, kismi kayitlar DAHIL)
  -401,43  kumulatif_funding
  -295,03  kumulatif_giris_ucret
+1.005,94  _kasa_sifirlama (2026-08-12 kullanici karari)
---------
 7.462,51  hesaplanan     vs   7.462,61 equity   ->  SAPMA 0,10 $
```

#### Equity yörüngesi — açık ANLIK GÖRÜNTÜ, drift eder

```
2026-08-12  9.558 $   (kasa sifirlamasi sonrasi taban)
2026-08-17 10.156 $   <- BASLANGIC BAKIYENIN USTUNDE. Defter ARTIDAYDI.
2026-08-21  8.312 $   <- 4 gunde -1.844 $
2026-08-24  7.463 $   <- 3 gun daha -849 $
```

#### Piyasa o günlerde ne yaptı

```
gun        alt_get    BTC      genislik
08-18       -1,37%  64.548      %26,5
08-19       +5,12%  69.016      %85,9   <- patlama
08-20       +3,05%  72.638      %77,7
08-21       +0,66%  73.658      %76,5
```

**BTC 3 günde 64.548 → 73.658 = +%14,1.** Genişlik %26,5 → %85,9.

#### GİRİŞ gününe göre kırılım (kapanış değil — CLAUDE.md "açılıp kapanan" ayrımı)

```
08-19   SHORT   -358   LONG  +241
08-20   SHORT -1.206   LONG  +284   <- rallinin en sert gununde SHORT acti
08-21   SHORT    -60   LONG  -285
08-22   SHORT     +0   LONG  -315   <- ralli bitti, bot LONG'a dondu
08-24   SHORT     +0   LONG  -583   <- ve LONG'da kaybetti
```

**Açığın yapısı iki parçalı:** (1) ralliye karşı SHORT **−1.844 $**,
(2) ralliden sonra LONG'a dönüp **−849 $**. Klasik whipsaw.

#### 🔴 ÖNCEKİ TEŞHİS YANLIŞTI — ve tam da yasak olan hatayla

Bu oturumda *"para çıkışta kayboluyor, stop çok sıkı"* teşhisi yazılmıştı.
O teşhis **198 pozisyonun havuzlanmış** rakamlarından çıkarıldı. Ama o havuz
**kârlı bir dönemi (08-17'ye kadar) ile 3 günlük bir felaketi** aynı ortalamaya
sokuyor. Bu, `16_rejim_kosullu`'nun zaten belgelediği hata:
***"2 yıl ortalaması hiçbir gerçek koşula karşılık gelmez."***
Aynı hata bu sefer 1 aylık pencerede yapıldı. **Kullanıcı yakaladı.**

#### Geniş stop bu günleri kurtarır mıydı? — ÖLÇÜLDÜ, HAYIR

KOL A, 08-19 sonrası girişler (N=12, SHORT 8 — **çok küçük, yön göstergesi**):

```
SHORT  2sa   k=1,5 -0,64   k=3,0 -0,63   STOPSUZ  -0,39
SHORT  4sa   k=1,5 -0,78   k=3,0 -0,31   STOPSUZ  -0,07
SHORT 24sa   k=1,5 -2,01   k=3,0 -3,59   STOPSUZ -10,22   <- GENIS STOP FELAKET
```

Kısa ufukta yardım ediyor, **24 saatte yıkıcı.** Sert bir ters trendde geniş stop
kaybı büyütür. ATR çarpanı bulgusu (717 gün ortalaması) **bu rejimde geçersiz.**

#### Sonuç — çalışılacak yer değişti

Botun sorunu *"stop genişliği"* değil: **rejim döndüğünde hâlâ eski yönde işlem
açması.** 08-20'de BTC %14 ralli yaparken SHORT açtı. Soru artık şu:
**ralli başlangıcı, o an bilinebilir bir şeyle tespit edilebilir miydi?**
(genişlik %26,5 → %85,9 sıçraması bir aday — ölçülmedi.)

---

### ❌ PİYASA GENİŞLİĞİ SHORT'LARI UYARIYOR MU? — **ÇÜRÜDÜ** (2026-08-24)

Ön-kayıt: `scratchpad/genislik/ON_KAYIT.md` (**koşturmadan önce**, 5 ölçüt).
Betikler: `01_genislik_serisi.py` · `02_karne.py`.
Saatlik genişlik = 24sa getirisi pozitif sembol yüzdesi (566 sembol, 17.726 saat).
Olaylar: `kol_b.json` SHORT (pump girişleri), **N=8.562 · 703 gün · 527 sembol**,
getiriler **k=1,50** (botun kendi stopu). Yoğunlaşma: sembol %0,9 · gün %2,4.

İDDİA: *"genişlik yüksekken açılan SHORT'lar sistematik olarak daha kötüdür."*

#### Ölçüt 1 — monotonluk: **KALDI, üstelik TERS**

```
kova              N       2sa      4sa      8sa     24sa
gen<16,8        789    -0,016   -0,356   -0,453   -0,300
16,8-44,7     1.761    +0,186   +0,270   +0,329   +0,487
44,7-77,8     2.244    +0,227   +0,193   +0,255   +0,207
gen>77,8      3.768    +0,240   +0,242   +0,274   +0,748
```

**Genişlik yüksekken SHORT'lar daha İYİ.** Dört ufkun dördünde de monotonluk yok
ve işaret hipotezin tersi. Holdout iki yarıda da **aynı (ters) işareti** veriyor
(+0,20…+1,56), ama `t` hiçbirinde 1,5'i geçmiyor.

Ölçüt 3 (rejim): **0/3** (4sa) · **1/3** (24sa) → KALDI.

#### 🔴 Ölçüt 4 — karıştırıcı: teknik olarak "geçti" ama **DEJENERE**

BTC 24sa sabitlendiğinde işaret dönüyor (4sa: −0,07 · −1,34 · −1,77;
24sa: −1,58 · −1,01 · −6,20) — yani koşullu olarak hipotez yönünde. **Ama:**

```
genislik <-> BTC 24sa getirisi   korelasyon +0,714  ->  ORTAK VARYANS %51
gen>77,8 iken BTC24 medyan +2,51%   ·   gen<16,8 iken BTC24 medyan -2,05%
BTC'nin EN UST ceyreginde alt genislik kovasi BOS  -> kiyas yapilamiyor
tum t degerleri |t| < 1,7
```

**Genişlik, BTC'nin hareketinin başka bir ifadesi.** Koşullandırınca geriye
bağımsız değişim kalmıyor. CLAUDE.md'nin *"her yeni aday erken fiyat
hareketinin başka bir ifadesi çıkıyor"* kuralının **bir kez daha** doğrulanması.

> **HÜKÜM: ÇÜRÜDÜ.** Genişlik SHORT girişlerini uyarmıyor; yeni bilgi de değil.

#### Ama o pencere gerçekten farklıydı — ve genişlik onu göstermedi

```
2026-08-18..21 penceresindeki KOL B SHORT olaylari (N=25):
    2sa  PENCERE +0,240   digerleri +0,212
    4sa  PENCERE +1,075   digerleri +0,227
    8sa  PENCERE -0,944   digerleri +0,291   fark -1,235
   24sa  PENCERE -0,952   digerleri +0,205   fark -1,157

Pencerede genislik MEDYANI 45,6  —  tum orneklem medyani 72,0  (yani DUSUK!)

Gunluk genislik yolu:  08-17 med 40 · 08-18 med 27 · 08-19 med 55 (32->87)
                       08-20 med 85 · 08-21 med 81
```

Pencere SHORT'lar için **8–24 saatte gerçekten kötüydü** (−1,2 puan), ama
genişlik medyanı örneklemin altındaydı. **Genişlik bu pencereyi işaretlemedi.**

⚠️ N=25 — vekil olaylar botun o penceredeki etkinliğini (17 SHORT tek günde)
temsil etmiyor. Pencerenin neden kötü olduğu **hâlâ açıklanmamış durumda.**

---

### ❌ "HACİM VAR, FİYAT YOK" ÖNCÜ SİNYAL Mİ? — **HÜKÜM YAZILMADI** (2026-08-24)

Ön-kayıt: `scratchpad/hacim_oncu/ON_KAYIT.md` (**koşturmadan önce**, 5 ölçüt).
Betik: `01_karne.py`. BTC saatlik, N=17.716 saat, 2 yıl.
Olay: `hacim ≥ 4x` (medyan-24sa'e göre, ≈%95 dilim) **VE** `|saatlik ret| ≤ %0,50`.

```
OLCUM    (hacim var, fiyat YOK)      N=  314   ·  217 gun
KONTROL1 (hacim var, fiyat DA var)   N=  596
KONTROL2 (normal saatler)            N=16.806
```

KONTROL1 kritik: iddia *"hacim hareketi haber verir"* değil, **ayrışmanın**
kendisi. O olmadan yalnız "hacim = oynaklık" tekrarlanmış olur.

#### Ölçüt 1 — büyüklük: ölçüte göre "geçti", **ama gürültü içinde**

```
ufuk      OLCUM   KONTROL1   KONTROL2    OLCUM-KON1
1sa       0,399     0,454      0,310     -0,055 (t-1,6)
2sa       0,618     0,594      0,440     +0,023 (t+0,5)
4sa       0,802     0,791      0,631     +0,011 (t+0,2)
8sa       1,013     1,046      0,920     -0,033 (t-0,4)

AZAMI hareket (ufuk icinde):
1sa       0,697     0,850                -0,153 (t-3,6)   <- TERS, ve ANLAMLI
2sa       1,000     1,080                -0,081 (t-1,3)
```

⚠️ **Ön-kaydımdaki ölçüt 1 fazla gevşek yazılmıştı** (*"fark > 0"*, anlamlılık
şartı yok). Yazıldığı hâliyle geçiyor (+0,023 · +0,011) ama `t` = 0,5 ve 0,2 —
sıfırdan ayırt edilemez. Üstelik **azami hareket ölçüsü ters yönde ve 1sa'te
anlamlı** (t=−3,6): hacim varken fiyatın kıpırdamadığı saatleri, sonrasında
**daha KÜÇÜK** hareket izliyor.

#### 🔴 Ölçüt 2 (karıştırıcı) — **KALDI**

Son 24sa gerçekleşmiş oynaklık sabitlendiğinde:

```
2sa   Q0 +0,049  Q1 -0,057  Q2 +0,017  Q3 +0,163   -> 3/4  GECTI
4sa   Q0 +0,138  Q1 -0,089  Q2 +0,196  Q3 -0,088   -> 2/4  KALDI
```

Tüm `|t| < 1,5`. Ön-kayıt: *"1 veya 2 geçmezse hüküm YAZILMAZ."*

> **HÜKÜM YAZILMADI.** Sinyal, oynaklık kontrolünden geçmiyor.

Ölçüt 3 (holdout): iki yarıda da `|t| < 0,7`. Ölçüt 4 (yön): dört ufkun
dördünde de %95 GA sıfırı içeriyor — **yön yok** (üçüncü kez doğrulandı).

#### 🔑 Ölçüt 5 — VAKA DENETİMİ: anekdot kusursuz, toplam boş

```
2026-08-19 13:00   8,0x  ret +0,20%  -> OLCUM   ileri 2sa +5,45%  4sa +4,90%
2026-08-18 14:00   7,2x  ret +0,77%  -> KON1    ileri 2sa +0,19%  4sa +0,09%
2026-08-19 12:00   5,4x  ret +0,59%  -> KON1    ileri 2sa +1,60%  4sa +5,51%
2026-08-19 15:00  37,6x  ret +3,99%  -> KON1    ileri 2sa -0,52%  4sa -0,17%
```

**Hipotezin doğduğu vaka kusursuz uyuyor:** 13:00'te hacim 8 kat, fiyat sabit →
2 saatte **+%5,45**. Yanlış alarm (08-18) fiyat süzgecine takılıp ÖLÇÜM
kümesine bile girmiyor. Ve 37,6x'lik saat hareketin **başı değil sonu**.

**Ama 314 olayın toplamı hiçbir şey söylemiyor.** Tek vaka ne kadar ikna edici
olursa olsun, genellemiyor. Bu kayıt, *"anlatı ikna eder, sayım karar verir"*
ilkesinin en temiz örneğidir.

⚠️ Sağlamlık taramasında `hacim ≥ 5x` kolu üç fiyat eşiğinde de küçük pozitif
veriyor (+0,032 · +0,027 · +0,059; N=85–228). **Kovalanmadı** — eşik gezdirip
geçen hücre aramak bu projede reddedilmiş davranıştır (`CLAUDE.md`).

---

### 🔴🔴 VERİ HATASI — `funding_gecmis` İÇİNDE BİRİM KIRILMASI (bulundu 2026-08-25)

Fonlama rejim ölçümü kurulurken bulundu. **Ölçüm değil, BULGU.**
Betikler: `scratchpad/fonlama_rejim/01_seri.py` (bulguyu ortaya çıkaran).

#### Bulgu

`scratchpad/funding_gecmis/*.json` içindeki `r` alanı **iki farklı birimde**:

```
gun bazinda |r| < 1e-3 olan kayitlarin payi (150 sembol ornegi):

  2026-08-06    3,4%
  2026-08-11    2,7%
  2026-08-12   95,3%   <<<< KIRILMA
  2026-08-13   97,7%
  ...
  2026-08-20   98,5%
```

**2026-08-12'den ÖNCE: yüzde (%/8sa). 2026-08-12'den İTİBAREN: kesir (ham Binance).**
Aradaki fark **100 kat**. 24 aylık geçmişte küçük-ölçek payı %0,3–4,6 arasında
sabit; tek bir günde %95'e fırlıyor.

#### Üç bağımsız doğrulama

1. **Çapraz depo:** `radar_archive.funding` medyanı **0,00500**; aynı sembolün
   `funding_gecmis.r`'si aynı dönemde **5e-05** → tam **100 kat**.
   (CLAUDE.md zaten *"`funding` adı başka şeydir — oran"* diye uyarıyordu.)
2. **Kaynak kod:** `testbot.funding_uygula` → `maliyet = notional * e["rate"] * isaret`
   — **bölme yok**, yani canlı uçtan gelen `rate` bir **kesir**. İndirici bunu
   ham yazmaya 08-12'de başlamış.
3. **Yer gerçeği:** defterdeki `funding_usdt` ile kıyas — kesir varsayımı 4
   kıyaslanabilir pozisyonun 2'sinde **tam** tutuyor, yüzde varsayımı 0'ında.
   (Kıyaslanabilir N düşük çünkü `funding_usdt` yalnız 08-17'den beri var.)

#### ⛔ [DÜZELTİLDİ 2026-08-25] — aşağıdaki bölüm YANLIŞTI

**Sebep bulundu ve benim çıkarımım yanlıştı.** Kırılma bir "indirici değişikliği"
değil, **aynı önbelleğe yazan İKİNCİ BİR BETİK**:

```
scratchpad/funding_indir.py:67    "r": float(x["fundingRate"]) * 100    -> YUZDE  (dogru)
scratchpad/veri_guncelle.py:97    "r": float(x["fundingRate"])          -> HAM KESIR (eksik *100)
```

`veri_guncelle.py`'nin kendi açıklaması: *"klines_1h_uzun ve funding_gecmis
**08-11'de DURMUS**"* — veri durunca yazılmış bir yakalama betiği, ve `*100`'ü
atlamış. 08-12'den itibaren eklenen kayıtlar bu yüzden kesir.

**Doğrulama — `r` YÜZDEDİR, kayıtlı düzeltme DOĞRUYDU:**
`|r| = 2,00000` (Binance'in %−2 fonlama tavanı) 21 ayrı ayda, **2026-08 dahil**
189 kez görülüyor; kesir tavanı `0,02` iki yılda yalnız 2 kez (rastlantı).

**Bu yüzden aşağıdaki iki iddiam GEÇERSİZDİR:**
- ~~"`*100` kaldırmak 24 ayda fonlamayı sıfırlar"~~ → **yanlış.** Kaldırma doğruydu.
- ~~"`35_stopsuz`'un hükmü şüphelidir"~~ → **geri alındı.** O hüküm için bu
  gerekçeyle bir şüphe yok. *(Bu proje aynı hatayı bir kez daha yaşadı:
  `short_kayip` ailesi haksız yere şüpheli ilan edilmişti — bkz. kayıtlı
  "DÜZELTİLMİŞ FONLAMAYLA YENİDEN KOŞUM". **Ben aynı kalıbı tekrarladım:
  bir birim şüphesini doğrulamadan geriye genelledim.**)*

**AYAKTA KALAN kısım:** 08-12 sonrası kayıtlar gerçekten kesir. Etkisi
**2 yıllık ölçümlerde ihmal edilebilir** (730 günün 10'u), ama **son pencereye
odaklı** her ölçümde büyüktür — fonlama rejim serisi tam bu yüzden ölü göründü.

**Onarım:** `veri_guncelle.py:97`'ye `* 100` eklenmeli; 08-12..08-21 kayıtları
100 ile çarpılmalı ya da kalıcı uçtan yeniden indirilmeli. **Yapılmadı — onay bekliyor.**

---

#### 🔴 Sonuç: kayıtlı "düzeltme" bu bulguyla ÇELİŞİYOR

`olcumler.md` → *"DÜZELTİLMİŞ FONLAMAYLA YENİDEN KOŞUM"* kaydı, `funding_gecmis`
okuyup `*100` uygulayan **14 betiğin** düzeltildiğini (yani `*100`'ün
kaldırıldığını) söylüyor ve bu koşumda **iki hüküm değişmişti**
(`35_stopsuz` ve `12_holdout`).

**`*100` kaldırmak yalnız 08-12 SONRASI kayıtlar için doğrudur.** Ölçümlerin
neredeyse tamamı **08-12 ÖNCESİ 24 ayda** yaşıyor ve orada `*100` kaldırmak
fonlamayı **100 kat küçültür — yani fiilen sıfırlar.**

⚠️ **`35_stopsuz`'un "stopsuz her ufukta daha iyi" hükmü özellikle şüphelidir:**
stopsuz kol daha uzun tutar, daha çok fonlama öder; fonlama sıfırlanırsa o kol
yapay olarak kazanır. **Yeniden koşulmalı.**

#### Bu oturumdaki ölçümlere etkisi

| ölçüm | etkilendi mi |
|---|---|
| `stop_carpani/01_kol_b.py` (ATR çarpanı) | ❌ **Hayır** — `r` zaten yüzde, doğrudan eklemek DOĞRU; yalnız 08-12 sonrası birkaç olayda fonlama 100 kat küçük kaldı, ihmal edilebilir |
| `fonlama_rejim/01_seri.py` | ✅ **Evet** — kritik pencere (08-17..21) tamamen kesir bölgesinde, seri orada ölü göründü |
| TimesFM / genişlik / hacim ölçümleri | ❌ Hayır — fonlama kullanmıyorlar |

#### Kural önerisi (CLAUDE.md → MİMARİ TUZAKLAR)

> **Bir önbelleğin birimi ZAMAN İÇİNDE değişebilir.** Dosya başındaki tek bir
> `assert` yetmez — indirici değiştiğinde eski ve yeni kayıtlar aynı dosyada
> yan yana durur. Fonlama okuyan her betik **kaydın tarihine göre** birim
> seçmeli, ya da yükleyici tek birime normalize etmeli.
> Kırılma tarihi: **2026-08-12**.

---

### 🔴 TAZE VERİYLE YENİDEN — BOĞA YARISI ÖLÇÜLDÜ, TABLO TERSİNE DÖNDÜ (2026-08-25)

**Betikler:** `28_cikis_taramasi.py` · `35_stopsuz.py` — fonlama düzeltilmiş **ve**
`perp_seri` 08-25'e tazelenmiş hâliyle. Önceki koşumda B kümesi **ölçülemiyordu**
(veri 08-21'de bitiyordu); şimdi N=91 pozisyon.

#### `35_stopsuz` — iki küme ZIT

```
STOP YOK kolu      A) NOTR/AYI N=111      B) BOGA N=91
 1 saat               +0,005                 -0,020
 2 saat               +0,101                 -0,708
 4 saat               +0,628                 -1,382
 8 saat               +0,769                 -2,576
24 saat               +1,087                 -6,147   (liq %9)
72 saat               +1,478                 -4,698   (liq %17)
```

🔴 **2026-08-24 tarihli kaydım eksikti.** *"Stopsuz kol her ufukta artı ve süreyle
monoton artıyor"* demiştim — o **yalnız A kümesi** içindi, B ölçülemiyordu.
B ölçülünce **tam tersi** çıktı: stopsuz **en kötü kol**, ve süreyle çöküyor.

Boğada stop **koruyor**: 24 saatte `stop %3 = −2,107` vs `stopsuz = −6,147`.
Ayıda stop **yiyor**: 72 saatte `stop %3 = −0,582` vs `stopsuz = +1,478`.

**Tek düzenlilik: stopun değeri rejime göre İŞARET DEĞİŞTİRİYOR.**

#### `28_cikis_taramasi` — hüküm AYAKTA, artık iki kümede de ölçülü

```
varyant                    A (notr/ayi)     B (boga)   ikisi de arti?
yol 24 bar (120 dk)             +377          -3011    hayir
yol  3 bar ( 15 dk)             +312          -1226    hayir
stop%8 / hedef %5               +211          -2187    hayir
yol  6 bar ( 30 dk)             +154           -935    hayir
```

**46 varyantın hiçbiri iki kümede birden artı değil.** Bu hüküm önceden B'de veri
olmadığı için zayıftı; artık **gerçek ölçümle** duruyor.

⚠️ Botun B kümesindeki GERÇEK sonucu **−2.395,89 $** (89 kapanan). Izgaranın en iyi
B hücresi −935; yani **birçok varyant botu geçiyor ama hiçbiri kâra geçmiyor.**

**HÜKÜM YAZILMADI** — bunlar bozuk aletin düzeltme koşumudur, gözlemdir.
Hüküm için ileri sınav gerekir: `ON_KAYIT_sure_rejim.md`.
Bot dosyalarına yazım: YOK.

---

### 🔴 SIZINTILI KIYAS ÖLÇÜTÜ ONARILDI — hüküm ayakta, KANITI değişti (2026-08-25)

**Betik:** `scratchpad/poz_yol/42_cikis_yeniden.py`

#### Onarılan hata

`32/33/34`'ün "rastgele çıkış" kolu:

```python
aday = range(2, len(pnl) - 1)          # len(pnl) = POZISYONUN OMRU
rast = pnl[random.choice(aday)] - pnl[-1]
```

Kol, pozisyonun **kaç bar yaşayacağını bilerek** çıkış seçiyordu — kısa ömürlüde
erken, uzun ömürlüde geç. Gerçek zamanda o bilgi yok. Kıyas ölçütü şişikti.

#### Sızıntısız tasarım

```
SABIT UFUK H=48 bar (4 saat) · kapanan pozisyon ELENMEZ, kapanis degerinde SABITLENIR
BELLEKSIZ CIKIS  : her barda p olasilikla cik (geometrik) — omur bilgisi YOK
ESLESMIS TUTMA   : p, kuralin ORTALAMA cikis barina esitlendi
SABIT BAR        : ayrica herkes ayni j'de cikan ongorusuz taban
```

N=141 pozisyon (72'si ufuktan kısa, dolduruldu · 69 tam), Monte Carlo 200 tekrar.

#### Sonuç

```
kural                        N    bar   kural  belleksiz    FARK      z
blowoff                     18    8,6  -0,413    +0,424    -0,837  -2,00
herhangi bir veto           23   10,9  -0,653    +0,161    -0,814  -2,49
artik bu yonde almazdi     117   12,4  +0,000    +0,040    -0,040  -0,43
smart POZUN TERSINE         63    2,2  +0,097    +0,115    -0,018  -0,38
taker_soguma / long_veto / ters aday / smart-ayristi : N YETERSIZ
```

🟢 **Hüküm AYAKTA:** hiçbir çıkış kuralı sızıntısız ölçütü de geçemiyor. İkisi
**anlamlı biçimde kötü** (z −2,00 ve −2,49), ikisi ayırt edilemez.

🔴 **Ama eski kanıt yanlıştı:** sızıntılı ölçüt **+1,789** puan veriyordu;
sızıntısız ölçüt **+0,04 … +0,42**. Yani eski kıyas tabanı yaklaşık **40 kat**
şişikti. *"Rastgele çıkmak +1,789 kazandırıyor"* cümlesi **geri çekilir** —
o rakam bir sızıntı yapaylığıydı, bulgu değil.

⚠️ Dört kuralın N'i yetersiz (1-9 gözlem); onlar hakkında hüküm **yok**, "denendi
ve düştü" diye **sayılamaz**. Gerçek sayım: **4 kural sınandı, 4'ü de geçemedi.**

**HÜKÜM YAZILMADI.** Bot dosyalarına yazım: YOK.

---

### 🔴 PORTFÖY AŞAMASI — üç aşamalı sıranın ÜÇÜNCÜSÜ, ilk kez yapıldı (2026-08-25)

**Betik:** `scratchpad/poz_yol/43_portfoy.py` · N=210 kapanmış pozisyon
(83'ü kısmi kayıt içeriyor) · toplam net **−3.168,75 $** · **tanımlayıcı, hüküm yok**

#### 1 · Pozisyon sınırı — bağlıyor ama nadiren

```
maks_pozisyon = 8   (config: testbot.maks_pozisyon)
6.869 turun 544'u (%7,9) sinirda
acik sayisi: {0:4239, 1:484, 2:174, 3:283, 4:306, 5:321, 6:213, 7:305, 8:544}
```

Turların **%62'sinde hiç açık pozisyon yok.** Sınır ana kısıt değil; asıl kısıt
aday bulmak (adayların %97,4'ü skorda eleniyor — bu dosya, boğa kapısı ölçümü).

#### 2 · 🔴 KUYRUK SIRASI KEYFİ — skor sonucu öngörmüyor

Bot adayları **skora göre** sıralıyor ([testbot.py:1444](testbot.py#L1444)):

```
skor dilimi      N   ort net $   kazanma
30,0-36,2       52     -16,76      %38
36,4-47,0       52      -6,00      %40
47,2-57,7       52     -21,77      %42
58,2-89,3       54     -15,80      %44
UST - ALT ceyrek: +2,20 $   gun-kumeli t +0,42  (11 gun)
```

**Monotonluk yok, fark yok (t=+0,42).** Sınır bağladığında bot hangi adayı seçtiğini
**bilmiyor** — sıralama pratikte rastgele. Kazanma oranı hafif artıyor (%38→%44)
ama dolar sonucu değişmiyor.

#### 3 · Girişteki `pos` — işaret doğru, güç yok

```
pos dilimi       N   ort net $   kazanma
0,00-0,57       52      -0,88      %48
0,57-0,77       52     -31,21      %37
0,77-0,91       52     -20,75      %37
0,92-3,27       54      -7,79      %44
UST - ALT ceyrek: -5,13 $   gun-kumeli t -0,57  (10 gun)
```

İşaret **beklenen yönde** (yüksek `pos` kötü) ve en alt çeyrek neredeyse başabaş
(−0,88, %48 kazanma) — ama t=−0,57, **anlamlı değil.** N=210, 10 gün.
⚠️ `range_pos_giriste` **1'i aşıyor** (maks 3,27) — 20 barlık aralığın dışında
hesaplanıyor olabilir; ayrı teşhis gerekir.

#### 4 · Boyutlandırma

```
marjin $: medyan 401  ceyrekler 218 / 723  aralik 50-1174   (23 kat yayilim)
kaldirac : 3x=164 · 4x=47 · 5x=34 · 6x=19 · 7x=6 · 8x=9 · 9x=6 · 10x=8
```

Risk sabit (~121 $) → **stop genişliği pozisyon büyüklüğünü belirliyor.**

#### 5 · 🔴 KAPI KARNESİ — kaybın %61'i TEK kapıdan

```
kapi              N     toplam     ort   kazanma
MA50+ucuz        98   -1921,58  -19,61     %36   <<< kaybin %61'i
BOGA             53   -1504,74  -28,39     %42
A+B              25    +198,56   +7,94     %44
NOTR-belirsiz    19    +140,61   +7,40     %63
A+B+MA50          6    +598,58  +99,76     %67
AYI               5    -690,08 -138,02     %40
```

🟢 **2 yıllık ölçümle BİREBİR uyumlu.** `olcumler.md` → maliyet doğrulaması:
*"`MA50+ucuz` kapısının BRÜT kenarı NEGATİF (−0,0301) — maliyet öncesi bile
kaybettiriyor."* Canlı veri aynı şeyi söylüyor: **N=98, −1.921,58, %36 kazanma.**

İki bağımsız ölçüm (2 yıl replay + 210 canlı işlem) aynı kapıyı işaret ediyor.

**HÜKÜM YAZILMADI** — bu tanımlayıcı bir ölçüm. Kapı kapatma kararı ayrı ön-kayıt
ister. Bot dosyalarına yazım: YOK.

---

### 🔴 STOP: REJİM Mİ, YÖN MÜ? — İKİSİ DE DÜŞTÜ (2026-08-25)

**Ön-kayıt:** `ON_KAYIT_sure_rejim.md`, commit **c471b59**, koşumdan **önce**.
**Betik:** `41_stop_rejim_yon.py` · 5 pencere × 2 yön = 10 hücre · tarafsız kesit
(kapı süzgeci yok) · `D = net(STOP YOK) − net(STOP %3)` · ufuk 24 sa

#### Sonuç

```
pencere              yon        D    gun-t   gun   D(top3cik)  liq%   tur
ATH 24-09/12         LONG   +0,500   +2,29    91     +0,484    0,1  yukselen
ATH 24-09/12         SHORT  -0,473   -2,44    91     -0,459    0,7  yukselen
ATH 25-06/10         LONG   -0,094   -0,40   136     -0,129    0,9  yukselen
ATH 25-06/10         SHORT  -0,192   -1,41   136     -0,168    1,2  yukselen
TOPARLANMA 25-04     LONG   +0,577   +2,55    42     +0,552    0,1  yukselen
TOPARLANMA 25-04     SHORT  -0,655   -2,13    42     -0,627    1,4  yukselen
DERIN-AYI 26-01      LONG   -0,003   -0,03    74     -0,029    0,3    dusen
DERIN-AYI 26-01      SHORT  +0,078   +0,73    74     +0,113    1,2    dusen
AYI 26-06/08         LONG   +0,069   +0,87    56     +0,021    0,7    dusen
AYI 26-06/08         SHORT  +0,156   +2,31    56     +0,180    2,0    dusen
```

```
H1 (REJIM)  H1a 4/6 · H1b 3/4 · H1c 5/10   -> DUSTU
H2 (YON)    H2a 2/5 · H2b 2/5 · H2c 5/10   -> DUSTU
K1 yogunlasma: isaret DONEN hucre 0        -> GECTI
K3 likidasyon: hicbir hucre %25'i asmadi
```

#### HÜKÜM — ön-kayıt karar tablosundan aynen

**İkisi de ✗ → *"`35`'in A/B farkı botun kendi örneklemine özgü, evrene
genellenmiyor. `35` bir hüküm üretmez."***

`35_stopsuz`'un *"ayıda stop yiyor, boğada koruyor"* okuması **hüküm olarak
yazılamaz.** Botun 202 pozisyonunda görülen fark, 2 yıllık tarafsız kesitte yok.

#### 🔴 KENDİ ÖN-KAYDIMDA ÇELİŞKİ — kayda geçiyor

Beklenti notunda şöyle yazmıştım: *"trendin **tersine** açılan pozisyonda stop
kaçınılmaz olarak korur."* Yükselen piyasada trendin tersi **SHORT**'tur.
Ama ölçütü **`H2a: LONG'da D < 0`** diye kodladım — yani stopun **LONG'u**
koruyacağını yazdım. **Gerekçemle ölçütüm birbirini tutmuyordu.**

Veri, yazdığım gerekçeyi iki güçlü pencerede destekliyor
(ATH 24-09 ve TOPARLANMA: LONG `D>0` = stop yiyor · SHORT `D<0` = stop koruyor),
ama **kodladığım ölçütün tam tersi**. D/9 gereği ölçüt değiştirilmez:
**H2 DÜŞTÜ olarak kalır.**

Gözlenen desen (*"stop, trendin tersindeki pozisyonu korur"*) **yeni bir hipotezdir**
ve kendi ön-kaydını gerektirir. Bu ölçümden hüküm olarak çıkarılamaz.
Not: 5 pencerenin yalnız 3'üne uyuyor ve etki tamamen **yükselen** pencerelerde
yoğunlaşıyor (|D| 0,47-0,65 vs düşende 0,003-0,156).

**HÜKÜM: `35` hüküm üretmez.** Bot dosyalarına yazım: YOK.

---

### 🔴 `pos` RET SÜZGECİ — DÜŞTÜ, `pos` YOLU KAPANDI (2026-08-25)

**Ön-kayıt:** `ON_KAYIT_pos_suzgec.md`, commit **1957302**, koşumdan **önce**.
**Betik:** `40_pos_suzgec.py` · ESIK 0,75 · stop %5 · ufuk 24 sa · maliyet %0,1726

⚠️ **Ön-kayıttan sapma (koşumdan önce tespit edildi):** `BOGA_LONG` kapısı `skor`
ve `smart` istiyor, ikisi de radar çıktısı ve `klines_1h_uzun`'dan üretilemiyor →
**ölçülemedi**. Dolayısıyla ölçüt **Y1 de ölçülemedi** (iki kapı da SHORT).

#### Sonuç

```
A_funding (SHORT · suzgec: pos < 0,75 REDDEDILIR)
pencere              N    tut%  TUTULAN  REDDEDIL     TUMU    FARK  gun-t
ATH 24-09/12      1058   19,4%  +0,259    -0,414   -0,283  +0,926   1,82
ATH 25-06/10      7228   18,9%  -0,460    -0,249   -0,289  +0,495   2,12
TOPARLANMA 25-04  2967   19,4%  -0,423    -0,579   -0,549  +0,696   1,78
DERIN-AYI 26-01  10078   14,5%  -0,372    +0,036   -0,023  -0,205  -0,95
AYI 26-06/08      3615   11,1%  -0,021    +0,174   +0,152  -0,037  -0,09

B_ma50ucuz
ATH 24-09/12      4936   58,5%  -0,741    -0,469   -0,628  +0,467   1,87
ATH 25-06/10     12882   58,1%  +0,070    +0,261   +0,150  +0,184   1,02
TOPARLANMA 25-04  4763   56,1%  -1,163    -0,897   -1,046  +0,564   1,46
DERIN-AYI 26-01   8161   50,6%  +0,004    +0,122   +0,062  -0,178  -1,03
AYI 26-06/08      6060   52,0%  +0,083    +0,207   +0,143  -0,030  -0,21
```

```
              A_funding   B_ma50ucuz
S1 fark>0        3/5         3/5      (gereken >=4)   DUSTU
S2 gun-t>=2,0    1/5         0/5      (gereken >=3)   DUSTU
S3 uc stopta     DUSTU       DUSTU
U1 TUT>TUMU      2/5         0/5      DUSTU
U2 kazanc>=0,05  2/5         0/5      DUSTU
U3 kapsam>=%60   0/5         0/5      DUSTU
Y1               OLCULEMEDI
```

#### HÜKÜM — ön-kayıt karar tablosundan aynen

**S ✗ → *"Süzgeç de düştü. `pos`, mekanik sonrası uygulanabilir bir kural
üretmiyor."*** `pos` yolu **KAPANDI**.

⚠️ **Benim beklentim de düştü:** ön-kayda *"S'nin geçmesini bekliyorum"* yazmıştım
(mekanik aşamada fark 5/5 pozitifti). Geçmedi. Sebebi görülüyor: mekanik aşamadaki
5/5, **uç çeyrekler arası** farktı; süzgeç olarak uygulanınca kalan kolun kazancı
kayboluyor ve işaret rejime göre dönüyor.

Ayrıca **U3 tek başına yolu kapatırdı**: `A_funding`'de süzgeç adayların yalnız
**%11-19'unu** bırakıyor. Kural doğru olsa bile portföy kuyruğu boşalırdı.

#### 🔴 OTURUMUN TEKRARLAYAN DESENİ

Bu oturumda üç bağımsız ölçümde **aynı yapı** çıktı:

```
35_stopsuz   stopun degeri     yukselen pencerede X, dusende TERS
41_stop_rejim  D isareti       yukselen +/-, dusende ~0
40_pos_suzgec  suzgec farki    yukselen +0,18..+0,93, dusende -0,03..-0,21
```

**Ölçülen her etki yükselen ve düşen pencereler arasında işaret değiştiriyor.**
Bu bir bulgu değil, bir **uyarı**: tek dönemden çıkan hiçbir kural taşınmıyor.
`olcumler.md` → *"2 yıllık ortalama hiçbir gerçek koşula karşılık gelmiyor"*
hükmüyle aynı yere bakıyor.

Bot dosyalarına yazım: YOK.

#### ✅ [2026-08-25] Kırılma, DİĞER OTURUMUN KENDİ ARACIYLA doğrulandı — ve sebebi kesinleşti

Diğer oturum `scratchpad/fonlama_oku.py` (birim doğrulayıcı) ve
`scratchpad/fonlama_denetim.py` (depo tarayıcı) yazmış. **Okuyucu-tarafı teşhisi
doğru; `funding_gecmis.r` yüzdedir** (`funding_indir.py:67` `*100` uyguluyor,
`|r|=2,00000` tavanı 21 ayda 189 kez). Yukarıdaki yanlış çıkarımım düzeltildi.

**Ama ikinci ve bağımsız bir hata var — YAZICI tarafında:**

```
scratchpad/funding_indir.py:67    "r": float(x["fundingRate"]) * 100    -> YUZDE   (dogru)
scratchpad/veri_guncelle.py:97    "r": float(x["fundingRate"])          -> KESIR   (EKSIK *100)
```

`veri_guncelle.py` açıklaması: *"klines_1h_uzun ve funding_gecmis **08-11'de
DURMUS**"* — yakalama betiği, `*100`'ü atlamış. Aynı dosyaya yazan iki betik,
iki farklı birim.

**Onların KENDİ doğrulayıcısı, KENDİ eşikleriyle (59 sembol):**

```
TUM DOSYA        gecti: 59/59     <- butun dosya medyani hala yuzde (bozuk dilim %1,4)
08-12 ONCESI     gecti: 59/59     <- dogru
08-12 SONRASI    gecti:  4/59     <- 55 sembol BirimHatasi firlatiyor

  ornek           medyan ONCE   medyan SONRA
  SUI                0,007853       0,000078
  PIXEL              0,005000       0,000050     (tam 100 kat)
  ENJ                0,010000       0,000050
```

##### İki alet boşluğu — araç iyi, kapsamı dar

| boşluk | kanıt |
|---|---|
| `fonlama_oku.dogrula()` **tüm dosyaya** bakıyor; kırılma **tarihe yerel** | tüm dosya 59/59 geçiyor, pencere 4/59 |
| `fonlama_denetim.py` **okuyucuları** tarıyor (`["r"]*100`), **yazıcıları** taramıyor | `python fonlama_denetim.py` → *"IHLAL YOK"*, `veri_guncelle.py` hiç anılmıyor |

##### 🔴 AKTİF TEHLİKE

Veri **2026-08-21'de duruyor** (bugün 08-25). Yakalamak için `veri_guncelle.py`
yeniden koşulursa **4 gün daha kesir kayıt eklenir.** Betik düzeltilmeden
koşturulmamalı.

##### Onarım (yapılmadı, onay bekliyor)

1. `veri_guncelle.py:97` → `float(x["fundingRate"]) * 100`
2. `t ≥ 2026-08-12` kayıtları `×100` ile onar **ya da** kalıcı uçtan yeniden indir
3. `fonlama_oku.dogrula()`'ya **son N kayıt** için ayrı iddia eklensin
4. `fonlama_denetim.py`'ye **yazıcı** kalıbı eklensin: `fundingRate` okuyup
   `funding_gecmis`'e `*100`'süz yazan dosya = ihlal

**Etki:** 2 yıllık ölçümlerde ihmal edilebilir (730 günün 10'u) · son pencereye
odaklı ölçümlerde büyük.

#### 🔧 [2026-08-25] ONARIM UYGULANDI — beş adım, her biri doğrulandı

**1 · Yazıcı düzeltildi.** `scratchpad/veri_guncelle.py:97` →
`float(x["fundingRate"]) * 100`, gerekçe yorumu satır içinde.
`py_compile` + `pyflakes` temiz.

**2 · Veri onarıldı.** `scratchpad/fonlama_onar.py` (yeni betik).
Yedek alındı (55 MB, 567 dosya, oturum klasörü).

> ⚠️ **Sınır DOSYA BAZINDADIR, sabit tarih DEĞİL.** `veri_guncelle` her dosyanın
> kendi son kaydından devam etmişti; ölçüldü: 393 dosya 08-12 00:00'da, 44'ü
> 08-12 04:00'ta, 12'si **08-11'de** başlıyor. Sabit kesim, geç başlayanların
> **yüzde** kayıtlarını 100'le çarpar → yeni bozulma. Bu yüzden dosyanın
> sonundan geriye kesintisiz kesir bloğu taranıyor; sınır 2026-08-11'den
> önceyse dosya **atlanıyor**.

```
onarilan dosya : 552      onarilan kayit : 24.274
dokunulmayan   :  13      ATLANAN        : 2  (CBRS · SPY — tokenize hisse, belirsiz)
```

Atomik yazım (`.tmp` + `os.replace`). **İki bağımsız doğrulama:**

```
(a) DIGER OTURUMUN dogrulayicisi, pencere pencere (59 sembol):
       08-12 SONRASI gecti:   4/59  ->  59/59

(b) Botun kendi funding_usdt dolarina karsi:
       YUZDE tuttu  0/4 -> 2/4      KESIR tuttu  2/4 -> 0/4
       (SPACE 0,287=0,287 · EDGE -0,571=-0,571 tam eslesme)
```

**3 · Doğrulayıcı genişletildi.** `fonlama_oku.dogrula()` artık **son pencereyi
ayrı** doğruluyor (kuyruk medyanı dosya medyanından farklı birimdeyse
`BirimHatasi`). Sınandı: onarılmış veride **0/40 yanlış alarm**; son 250 kaydı
sentetik olarak kesire çevrilmiş dosyada **yakalandı**.

**4 · Denetim genişletildi.** `fonlama_denetim.py` artık **yazıcı** kalıbını da
arıyor (`fundingRate` okuyup `*100`'süz yazan satır). Sınandı: sentetik hatalı
**yazıcı ve okuyucu — ikisi de yakalandı**; güncel depo **ihlalsiz** (çıkış 0).
`fonlama_onar.py` muafiyete eklendi (orada `*100` meşru).

**5 · Eksik veri indirildi.** Düzeltilmiş `veri_guncelle.py` ile.
Tek-sembol sınaması (LINK) önce koşuldu: +101 mum, +12 fonlama, yeni kayıtlar
`r = 0,010000` (Binance taban oranı, **yüzde**), pencere doğrulaması geçti.

##### Neden bu sıra önemliydi

Yazıcı (1) düzeltilmeden veri (2) onarılsaydı, indirme (5) bozukluğu **yeniden
üretirdi.** Doğrulayıcı (3) ve denetim (4) ise bu hata sınıfının **bir daha
sessiz kalmamasını** sağlar — CLAUDE.md'nin *"hata sınıfı disiplinle değil
ARAÇLA kapanır"* ilkesi.

##### ⚠️ ONARIM ÜÇ KEZ YANLIŞ YAPILDI — kütüğe aynen yazılıyor

İlk kayıtta *"552 dosya onarıldı, doğrulandı"* yazıyordu. **Eksikti.** Sonraki
denetimlerde üç ayrı hata çıktı; üçü de **sezgisel sınır aramasından** doğdu:

| # | yaklaşım | hata | belirti |
|---|---|---|---|
| 1 | sabit eşik `|r| < 0,0009` | yüksek-fonlamalı sembollerde kesir değerleri eşiği aşıyor | 20 dosya kaçtı, çoğu **kısmen** onarıldı |
| 2 | sabit tarih `t ≥ 08-11` | dosyaların sınırları **farklı**; geç başlayanların DOĞRU kayıtları da ×100 | 33 dosyada `max|r|` %2,7–11,7 (tavan %2) |
| 3 | değişim-noktası (oran argmax) | medyan sağlam → erken bölmeler de yüksek oran; argmax pencere başına yapıştı | 300 dosyada sınır 08-08'e kaydı |

🔴 **İkinci hata özellikle utandırıcı:** *"sabit kesim yeni bozulma üretir"*
uyarısını betiğin kendi başlığına ben yazmıştım ve sonra aynısını yaptım.

**Yakalayan şey her seferinde BÜYÜKLÜK MANTIĞI oldu** — *"bu sayı mekanik olarak
mümkün mü?"* Binance fonlama tavanı **%2**; `max|r| = 11,7` görülünce şüphe
veriye değil **alete** yöneldi. Diğer oturumun `37_pos_mekanik` vakasında
bulduğu ders, burada birebir tekrarlandı.

##### Çözüm: sezgisel arama BIRAKILDI

Fonlama **KALICI sınıf** veridir (CLAUDE.md) — `/fapi/v1/fundingRate` istendiği
an geçmişi döndürür. **Bozuk pencereyi uçtan yeniden çekmek eşiksiz ve kesindir.**
`scratchpad/fonlama_yeniden_cek.py`: bozuk dosyayı tespit et → pencereyi uçtan
al (`*100` uygula) → zaman damgasına göre birleştir → **kısalırsa hata fırlat**.
Tespit-çek-tespit döngüsü **bozuk dosya kalmayana kadar** tekrarlandı.

`fonlama_onar.py` ise güvenli hâle getirildi: sınırı **güvenle belirleyemediği
dosyayı yedeğe geri döndürüyor** (*"şüphede DAİMA statüko"*).

##### NİHAİ DURUM — üç bağımsız denetim

```
1) birim dogrulayici (567 sembol)     : 0 hata
2) bozuk pencere taramasi             : 0 dosya
3) onarimin urettigi tavan asimi      : 0 dosya
4) depo denetimi (okuyucu + yazici)   : IHLAL YOK
5) kapsam: fonlama 2026-08-25 04:00 · mum 2026-08-25 06:00  (guncel)
```

Yer gerçeği (botun `funding_usdt`'si): **6/11** (onarım öncesi 0/4). Sapan 5
pozisyonda fark **birim değil pencere** kaynaklı — bot fonlamayı
`son_funding_kontrol_ts`'e göre kesiyor, kıyas betiği giriş→çıkış aralığı
kullanıyor. Bu ayrı bir konu, birim sorunu değil.

**Yedek:** `scratchpad/funding_yedek_20260825/` (55 MB, 567 dosya, gitignore'da).

---

### ❌ PİYASA GENELİ FONLAMA SHORT'LARI UYARIYOR MU? — **ÇÜRÜDÜ** (2026-08-25)

Ön-kayıt: `scratchpad/fonlama_rejim/ON_KAYIT.md` (**koşturmadan önce**, 5 ölçüt).
Betikler: `01_seri.py` · `02_olcum.py`. Veri **2026-08-25 onarımı sonrası**;
seri `fonlama_oku` üzerinden okunuyor (birim doğrulaması araçta).
**N=8.853 SHORT pump girişi · 708 gün · 527 sembol.** Yoğunlaşma: sembol %0,9 ·
gün %2,3. Mekanik yok — **ham ileri fiyat getirisi**, fonlama AYRI.

#### Ölçüt 1 — monotonluk: **KALDI** (U biçimli)

```
fonlama kovasi          N       HAM 4sa    HAM 24sa      FON 4sa    FON 24sa
ort<-0,0095          2334        +0,901      +1,341      -0,2777     -1,1544
-0,0095..-0,0032     2082        +0,643      +0,611      -0,2038     -0,9426
-0,0032..+0,0020     2206        +0,556      +0,093      -0,0903     -0,4544
ort>+0,0020          2231        +0,589      +1,429      -0,0381     -0,2116
```

#### Ölçüt 2 (kritik) — BTC sabitlendiğinde: **KALDI**

```
 4sa  BTC0 -2,03  BTC1 +0,35  BTC2 -1,13  BTC3 +0,89   -> 2/4
24sa  BTC0 -2,67  BTC1 -1,85  BTC2 +1,31  BTC3 +3,87   -> 2/4
```

İşaret BTC kovaları arasında **dönüyor**. Ölçüt 3 (holdout) de yarılar arasında
işaret döndürüyor (4sa −0,579 → +0,029; 24sa +1,352 → −0,108). Ölçüt 4 (rejim)
nominal 2/3 ama ufuklar arasında işaret tutarsız (ATH: 4sa −1,92 · 24sa +2,03).

> **HÜKÜM: ÇÜRÜDÜ.** Piyasa geneli fonlama SHORT girişlerini uyarmıyor.
> Bant dışı ilk aday da elendi.

⚠️ `ort>+0,0020` kovasının NET'i **+1,217** ile en yüksek. **Bu bir bulgu
DEĞİLDİR** — ön-kayıtlı ölçütlerin ikisi de kaldı; tabloya bakıp en iyi hücreyi
seçmek bu projede reddedilmiş davranıştır.

#### 🔑 İKİNCİL ÖLÇÜM — asıl değer burada

```
ufuk        HAM fiyat        FONLAMA           NET     fonlamanin payi
 4sa    +0,648 (t +4,7)   -0,1575 (t -16,1)   +0,491        %24
24sa    +0,821 (t +2,2)   -0,7016 (t -15,7)   +0,120        %85

fonlamasi NEGATIF olan (SHORT ODUYOR):  4sa %28,9  ·  24sa %36,1
```

**SHORT pump girişlerinde fonlama, 24 saatte ham kenarın %85'ini yiyor.**
CLAUDE.md'de kayıtlı *"A+B kapısında kenarın %83'ünü fonlama yedi"* olgusu,
bağımsız bir popülasyonda (8.853 olay · 708 gün) **doğrulandı.**

🔴 **Asimetriye dikkat:** kenarın `t`'si **+2,2**, fonlama maliyetinin `t`'si
**−15,7**. **Maliyet kesin, kenar marjinal.** Kenar tartışmalıyken maliyet
tartışmasızdır.

**Bota dair gözlem (kural değil):** 4 saatte fonlama payı %24, net +0,491;
24 saatte pay %85, net +0,120. Kısa tutma fonlama yapısına **çok daha uygun** —
botun medyan tutma süresi 2,5 saat, yani bu tarafta doğru konumlanmış.

---

### 🟡 OI DEĞİŞİMİ — **ADAY** (hüküm DEĞİL) · pozisyon kompozisyonu (2026-08-25)

Ön-kayıt: `scratchpad/pozisyon_komp/ON_KAYIT.md` (**koşturmadan önce**;
**güç sınırı orada ilan edildi**). Betik: `01_olcum.py`.
**N=358 SHORT pump girişi · 31 gün · 84 sembol** (`perp_seri`, 102 sembol × 30 gün).
Tasarım: **gün içi eşleştirme** — piyasa günlük hareketi tanımı gereği sabit.
Mekanik yok, ham ileri fiyat getirisi.

7 değişken sınandı (`d_oi_3s` · `d_oi_24s` · `top_ls` · `d_top_ls` · `glob_ls` ·
`fark_ls` · `taker`). **Yalnız biri ayırdı:**

```
degisken     1 saat              4 saat              24 saat            tutarli
d_oi_3s     -2,151 t=-3,27 *    -1,989 t=-1,50      -6,380 t=-2,12 *    3/3
taker       -0,727 t=-1,08      -2,124 t=-1,92      -4,085 t=-1,67      3/3
d_oi_24s    -0,345 t=-0,58      -0,840 t=-0,79      -1,476 t=-0,51      3/3
top_ls      +0,507 t=+0,59      -1,389 t=-1,20      -1,675 t=-0,59      2/3
fark_ls     +0,316 t=+0,40      -0,453 t=-0,34      -1,063 t=-0,41      2/3
```

`fark_ls` (`top_ls − glob_ls`) yine boş — CLAUDE.md'nin *"denendi, bulgu
çıkmadı"* kaydı **yinelendi**.

#### Ön-kayıtlı ölçütlerin tamamı geçti (`d_oi_3s`)

| ölçüt | sonuç |
|---|---|
| 1 · gün içi \|t\| ≥ 2,0 | ✅ 1sa **t=−3,27** · 24sa **t=−2,12** |
| 2 · ufuklar arası tutarlılık | ✅ **3/3** aynı işaret |
| 3 · holdout (31 gün ikiye) | ✅ ILK −2,267 · SON −1,781 — **aynı işaret** |
| 4 · yoğunlaşma | ✅ sembol %8,1 · gün %13,7 (eşik %15) |

#### Karıştırıcı denetimi — pump BÜYÜKLÜĞÜ

```
ust yari (d_oi yuksek) ortalama chg24  +27,69%
alt yari (d_oi dusuk)  ortalama chg24  +27,52%      fark +0,17  t=+0,10
```

Yarılar pump büyüklüğünde **ayrışmıyor**. chg24 açıkça sabitlenip tekrar
ölçüldüğünde: **1sa −1,763 (t=−2,39, n=44) AYAKTA** · 24sa −4,336 (t=−1,38)
**zayıflıyor**.

#### 🔴 HÜKÜM DEĞİL — ADAY. Sebepleri:

1. **31 gün.** Ön-kayıt bunu önceden ilan etti: bu pencerede geçen bir sonuç
   *"aday"* olarak kaydedilir. Kıyas: genişlik 251 gün, fonlama 708 gün.
2. **7 değişken × 3 ufuk = 21 sınama.** Bu, 7'nin biri.
3. 🔴 **İŞARET, ÖN-KAYITTAKİ GEREKÇEMİN TERSİ.** Ön-kayıtta *"OI artarak gelen
   pump = yeni kaldıraçlı LONG = kırılgan"* yazmıştım — kırılgan olsa SHORT
   **kazanırdı**. Ölçüm tersini söylüyor: **OI hızla artarken short açmak
   DAHA KÖTÜ.** Okuma: hızlı pozisyon girişi = momentum sürüyor.
   *Gerekçe yanlıştı, etki var — ikisi ayrı şeyler.*
4. 24 saatte karıştırıcı kontrolünden sonra zayıflıyor.
5. Ham fiyat getirisidir; **fonlama dahil değil** (bu oturumda ölçüldü:
   24sa'te ham kenarın %85'i).

#### Doğrulama için ne gerekir

`perp_seri` **30 günlük kayan pencere** — koşulmadığı her gün kuyruğundan bir
gün düşüyor (CLAUDE.md). Bu adayın hüküm olabilmesi için pencerenin
**büyümesi** gerek: `perp_seri_indir.py` düzenli koşarsa 60-90 günde yeniden
sınanabilir. **Koşulmazsa bu aday doğrulanamadan ölür.**

#### ⛔ [DÜZELTME 2026-08-25, aynı gün] — `d_oi_3s` ADAYLIĞI **DÜŞÜRÜLDÜ**

*"Bota nasıl uygularız"* sorusu sorulunca botun kendi tanımına bakıldı ve
ölçtüğüm değişkende **fiyat bulaşması** olduğu görüldü:

```
BOTUN oi3     : sumOpenInterest       = KONTRAT sayisi       (fiyattan arinik)
BENIM d_oi_3s : sumOpenInterestValue  = DOLAR = kontrat x FIYAT
```

Dolar cinsinden OI, fiyat yükseldiği için **kendiliğinden** artar. Ölçüldü:

```
dolar-OI   <-> son 3sa FIYAT : korelasyon +0,774   ORTAK VARYANS %60
kontrat-OI <-> son 3sa FIYAT : korelasyon +0,396   ortak varyans %16
```

**Değişkenimin %60'ı fiyat hareketiymiş.** `chg24`'ü sabitlemiştim ama
**son 3 saatin** fiyat hareketini sabitlememiştim.

##### Temiz (kontrat) sürümle yeniden ölçüm — ÖLÇÜT 1'İ GEÇMİYOR

```
gun ici eslesmis fark, 1 saat SHORT ham getiri:

  DOLAR-OI   (ilk olcum)             -2,151  t=-3,27  *   <- gecmisti
  DOLAR-OI   | 3sa FIYAT sabit       -1,818  t=-2,56  *
  KONTRAT-OI (fiyattan arinik)       -0,781  t=-1,25      <- GECMIYOR
  KONTRAT-OI | 3sa FIYAT sabit       -1,118  t=-1,72      <- GECMIYOR
  SADECE 3sa FIYAT (kiyas)           -1,149  t=-1,48
```

Ön-kayıtlı ölçüt **|t| ≥ 2,0** idi. **Pozisyon kompozisyonunun temiz ölçüsü
(kontrat OI) bu eşiği geçmiyor.**

> **YENİ HÜKÜM: `d_oi_3s` bulgusu, büyük ölçüde FİYAT HAREKETİNİN başka bir
> ifadesidir.** CLAUDE.md'nin *"her yeni aday erken fiyat hareketinin başka bir
> ifadesi çıkıyor"* kuralı **beşinci kez** doğrulandı (agresör dengesi · son yeni
> uç · genişlik · hacim-öncü · ve şimdi dolar-OI).

##### Ders — ön-kayıt bu hatayı yakalayamadı

Ön-kayıtta karıştırıcı olarak **pump büyüklüğünü** (`chg24`) yazmıştım ve o
kontrol geçti. Ama asıl bulaşma **değişkenin tanımının içindeydi**: `Value`
alanı fiyatı çarpan olarak taşıyor. **Karıştırıcı listesi dışsal değişkenlerle
sınırlı kalmamalı — ölçülen büyüklüğün KENDİ TANIMI da denetlenmeli.**
Yakalayan şey, *"bot bunu nasıl hesaplıyor"* sorusu oldu.

⚠️ Kodda kayıtlı bağımsız ölçüm ([testbot.py:1432](testbot.py#L1432), 2026-08-03,
41 gün): `BASLIYOR (vol_x>2.5 & last1>2 & oi3>3)` N=69 ort R **−0,09** ·
`izle` N=796 ort R **+0,07**. Aynı yön, ama N=69 ve etki küçük — o da hüküm değil.

### ❌ NÖTR→BOĞA GEÇİŞİNDE PUMP TETİĞİ — **DÜŞTÜ** (2026-08-25)

**Ön-kayıt:** `ON_KAYIT_gecis_pump.md`, commit `2e0c96f` — **koşumdan önce** yazıldı.
**Hipotez (kullanıcı):** *"nötrden boğaya geçiş anında bu tetiklenirse artıda kapanır."*
**Betik:** `scratchpad/gecis_pump_ham.py` · rejim serisi `scratchpad/rejim_gecis_sayim.py`

**Veri:** `klines_1h_uzun` 546 sembol · 2024-12-23 → 2026-08-25 · **18.420 tetik**
(`chg24 ≥ +%10` ve `vol_x ≥ 2,0`, sembol başına 24 saatte tek). Rejim serisi
`evren.btc_rejim()`'den gün gün nedensel üretildi ve **botun canlı etiketiyle
doğrulandı**. NÖTR→BOĞA geçiş: **7**. Aşama: **HAM** (stop/hedef/fonlama yok), H=24s.

| ölçüt | sonuç |
|---|---|
| G1 · `T0−KONTROL` ort ≥ +1,0 **ve** t ≥ +2,5 | ❌ ort **+0,920** · **t = +0,49** |
| G2 · ≥5/7 geçişte pozitif | ❌ **4/7** |
| G3 · çürütme (`ÖNCE` ≥ `T0`) | ⚠️ tetikledi, **ama sağlam değil** (aşağı) |
| G4 · `chg24 × vol_x` hücrelerinde ayakta | ✅ 7/9 hücre pozitif |
| G5 · şans (2000 sahte geçiş) | ❌ **p = 0,1205** |

**HÜKÜM: DÜŞTÜ.**

**Sonuç tek epizoda yaslanıyor.** 2025-05-06 çıkarılınca işaret dönüyor:
`T0−KONTROL` **+0,920 → −0,763** (t=−0,75 · 3/6). Kalan altı geçiş: −5,24 · +1,81 ·
+0,62 · +0,46 · −0,63 · −1,60.

🔴 **Hipotezi doğuran geçiş, hipoteze KARŞI çıktı.** 2026-08-21 (canlı pencere):
`T0` −1,597 · `ÖNCE` **+5,692**. Para etiket dönmeden **önce** kazanılmış.

⚠️ **G3'e yaslanılmaz — ön-kayıt bir ayrıntıyı bağlamamıştı.** 2025-10-03 ve 10-12
epizodları bitişik; bantlar çakışıyor. İlk-eşleşme atamasıyla `ÖNCE` +1,643 (t=+1,27),
her geçişe kendi penceresi verilince **+0,214** (t=+0,10) — ve G3 artık tetiklemiyor.
İkisi de eşiği geçmiyor, **hüküm değişmiyor**, ama G3 bir bulgu olarak kullanılamaz.

**Betimsel gradyan (çıkarım DEĞİL):** `ÖNCE` +2,856 → `T0` +1,443 → `T1` −0,406 →
`T2` −2,286 (ham ort +24s). Etiketten uzaklaştıkça kötüleşiyor.

⚠️ **TASARIM SINIRI — ufuk stratejiyle uyuşmuyor.** Ölçüm 24 saat tutuyor; golge'nin
medyan tutma süresi **1,8 saat**. Kısa ufuklu bir kenarı 24 saatlik ham getiri
göremeyebilir. Bu **ayrı bir ön-kayıtla** sınanır; sonuç görüldükten sonra ufuk
değiştirmek bu projede reddedilmiş davranıştır — **kısa ufka BİLEREK bakılmadı.**

**Beklenti tutmuştu:** ön-kayıt G1'in düşmesine ~%25 vermiş ve gerekçe olarak
*"etiket hareketi geç yakalıyor"* yazmıştı; 08-21'de `ÖNCE ≫ T0` çıktı.

⚠️ **Koşum sırasında ileriye-bakma hatası bulundu ve onarıldı:** haftalık seri bir kez
baştan kuruluyordu, yani açık haftanın kapanışı o haftanın **son** günüydü. Etiketi
kaydırıyordu (7 geçiş → 5, `2025-05-06 → 05-11`). Onarımdan sonra geçiş sayısı
ön-kayıtla uyuştu. Ölçüt **değiştirilmedi**.

### ❌ HAREKET BİTİNCE TERS YÖN (SHORT) — **DÜŞTÜ** (2026-08-25)

**Ön-kayıt:** `ON_KAYIT_hareket_bitisi_short.md`, commit `d9cbdd7` — koşumdan **önce**.
**Hipotez (kullanıcı):** *"hareketin bittiği nokta 2. yönü gösterir."*
**Betik:** `scratchpad/hareket_bitisi_short.py` · N=18.402 pump olayı · 546 sembol ·
2024-12-23 → 2026-08-25 · 21 ay kümesi · aşama **HAM** (stop/hedef/fonlama yok).

Kollar: **A** = hareket-bitiş barı (son M=6 saatte yeni tepe yok) · **B** = aynı olayda
hâlâ yeni tepe yapan barlar (kova-eşleşmeli) · **C** = tetik barında hemen SHORT.

| ölçüt | eşik | sonuç |
|---|---|---|
| H1 · `A−C` | ≥ +0,5 **ve** t ≥ +2,5 | ❌ **−0,065** · t = **−0,35** · 9/21 ay |
| H2 · devam kuyruğu kesildi mi | `A/C ≤ 0,60` | ❌ **0,723** (%5,17 → %3,73) |
| H3 · 🔴 **BELİRLEYİCİ** karıştırıcı | ≥%60 kova + t ≥ +2,0 | ❌ **7/13 kova (%54)** · N-ağırlıklı **−0,154** · t = **−1,28** |
| H4 · şans (rastgele bar) | p ≤ 0,05 | ✅ p = **0,0020** |
| H5 · maliyet sonrası | net > 0 | ✅ A +0,042% · **C +0,099%** |

**HÜKÜM: DÜŞTÜ** (H3 belirleyiciydi).

🔴 **Asıl bulgu: detektör bir SEÇİCİ değil, sadece bir GECİKME.** Olayların
**%99,96'sı** (18.394/18.402) 48 saat içinde *"6 saattir yeni tepe yok"* koşulunu
sağlıyor; *"hâlâ sürüyor"* oranı **%0,0**. Bunların **%79'u 7-12. saatte** tetikliyor
(M=6 ile en erken mümkün an 7. saat). Yani kural *"hareket bitmiş olanları seç"*
değil, *"her pump'ta ~7-12 saat bekle"* demek — ve beklemek **kaybettiriyor**.

**Mekanizma açık:** *"son 6 saatte yeni tepe yok"* tanımı gereği fiyatın tepeden
gelmiş olması demek → SHORT'a **daha kötü (daha düşük) fiyattan** giriliyor. Kuyruk
korumasının bedeli, girişin kendisi. M uzadıkça kötüleşiyor: `M=3 −0,107` ·
`M=6 −0,065` · `M=12 −0,194` — **üçü de C'nin altında.**

**H2 kısmen çalıştı ama iki taraflı:** devam felaketi %5,17 → %3,73 kesildi (−%28),
**ama jackpot da** %2,76 → %2,40 kesildi. Kuyruk simetrik budanıyor.

**H4 geçti ve yanlış okunmamalı:** `A` (+0,388) rastgele bardan (medyan +0,187,
p=0,002) **iyi**. Yani *bekleyeceksen* bitiş anı iyi bir zamanlama — ama
**hiç beklememek (C +0,444) hepsinden iyi.**

⚠️ **EN İYİ HÜCRE SEÇİLMEDİ.** H3 tablosunda gerçek yapı var: `7-12 sa × kazanç>%15`
→ A +4,976 vs B +0,340 (**+4,636**); `13-24 × >%15` → +1,401. Ama kütlenin çoğu
`kazanç<0` kovalarında ve orada A **kaybediyor** (`7-12 × -5..0`: N=6.807, −0,515).
Bu hücreyi kural yapmak bu projede reddedilmiş davranıştır; **aday olarak bile
yazılmıyor** — ayrı ön-kayıt ister.

**Beklenti tutmuştu:** ön-kayıt ~%20 vermiş ve *"H3'ün düşmesini en olası tek sonuç"*
demişti. **Dördüncü kez aynı duvar** değil ama akrabası: sinyal seviyenin vekili
çıkmadı, **hiç sinyal olmadığı** çıktı — koşul neredeyse her olayda sağlanıyor.

**Yan olgu (hüküm değil):** `C` = pump'ı tetikte shortlamak, ham +0,444%,
maliyet sonrası **+0,099%** — fonlama HARİÇ ve fonlama SHORT lehine olurdu.
Ama kapı karnesinin *"ters kapı sınavı"* (fonlaması pozitif olanı shortla) zaten
**KALDI** (NET −0,0279). Bu satır bir kural önerisi DEĞİLDİR.

### 🔴 `skor` İLERİ GETİRİYİ TAHMİN EDİYOR MU? — **DÜŞTÜ**, ama TERS YÖNDE (2026-08-25)

**Ön-kayıt:** `ON_KAYIT_skor_tahmin.md`, commit `a4e0706` — koşumdan **önce**.
**Betik:** `scratchpad/skor_tahmin.py` · rejim düzeltmesi `scratchpad/skor_tahmin_rejim.py`
**Neden:** `skor` botun **tek pozitif seçicisi**; LONG kapısı `skor ≥ 45`'e dayanıyor
ve **hiç doğrudan ölçülmemişti**.

**Veri — KOŞU A (tam tarama evreni):** `radar_archive.jsonl` 184.373 satır →
`(sembol, saat)` tekilleştirmesiyle 52.028 → kline eşleşen **50.738 gözlem** ·
441 sembol · **60 gün**. `top_ls/smart/glob_ls/taker` (%24,7) ve `chg24` (%20,5)
**kullanılmadı** — gizli seçilim. KOŞU B yok, iki evren karıştırılmadı.

⚠️ **KALİBRASYON — bu yapılmasaydı ölçüm sessizce yanlış çıkardı.** `radar_archive`
`ts` alanı **YEREL saat (UTC+3)**; kline UTC. Ofset −3'te fiyatlar **%100** bar
aralığında, ofset 0'da **%37**. Giriş anı, ileriye bakmayı engellemek için anlık
görüntünün **bir sonraki saatinin** kapanışı alındı.

#### Bant tablosu (ham +24s)

```
bant      N       ort       medyan    pozitif   ATR med
<2      5870    +0,126%    -0,146%     %47       1,14%
2-5    10523    +0,218%    -0,132%     %48       1,11%
5-10   11876    +0,249%    -0,067%     %49       1,32%
10-20  12204    +0,250%    -0,119%     %48       1,85%
20-30   5513    -0,001%    -0,419%     %45       2,47%
30-45   3381    -0,623%    -1,034%     %42       2,90%
>=45    1371    -2,015%    -3,062%     %35       3,38%   <- BOTUN LONG KAPISI
```

| ölçüt | eşik | sonuç |
|---|---|---|
| S1 · monotonluk | ρ ≥ **+0,75** | ❌ **ρ = −0,643** (H6: **−0,893**) · uç fark −2,141 · gün-kümeli t=−2,00 |
| S2 · işaret tutarlılığı | ≥%60 gün | ❌ **13/43 gün (%30)** · t=−2,14 |
| S3 · 🔴 karıştırıcı | ≥%60 hücre | ✅ **6/9** — ama **NEGATİF işaretle** |
| S4 · şans (gün-içi permütasyon) | p ≤ 0,05 | ❌ **p = 1,0000** — gerçek değer 2000 permütasyonun **hepsinin altında** |

**HÜKÜM: DÜŞTÜ.** Ön-kayıtlı hipotez *"skor pozitif tahmin eder"* **çürüdü.**

#### 🔴 Ama düşme biçimi önemli: skor GÜRÜLTÜ DEĞİL, TERS

Monotonik **azalan**. S4'ün `p=1,0000`'ı şu demek: gözlenen fark 2000 gün-içi
permütasyonun tamamından **daha negatif**. S3 (belirleyici karıştırıcı kapısı)
negatif işaretle **ayakta kaldı** → skor yalnızca oynaklığın vekili değil.

**Sağlamlık — bu projede nadir görülen tutarlılık:**

```
zaman yarilari    ILK -3,343   SON -1,067          AYNI ISARET
rejim (tek tanim) NOTR -1,017  AYI -3,584  BOGA -2,870   UCUNDE DE AYNI ISARET
yogunlasma        274 sembol · 58 gun · top3 sembol %8,2 · top3 gun %14,4
ufuk              H24 rho -0,643   ·   H6 rho -0,893  (t=-3,21)
```

`BANT × REJİM` (tek tanımlı): BOĞA'da `<2` … `20-30` bantlarının **hepsi güçlü
pozitif** (+2,087 … +2,577) ve **yalnız `≥45` negatif** (−0,675). Yani boğada her şey
çıkarken en yüksek skorlular çıkmıyor.

⚠️ **Sınırlar aynen:** gün-kümeli t'ler ılımlı (−2,00 / −2,14; H6'da −3,21). Rejim içi
t'ler **anlamsız**: NOTR −1,14 · AYI −0,99 · **BOGA t=−9,40 ama yalnız 3 gün ve N=123
→ okunmaz.** 60 gün tek pencere. Bantlar oynaklıkta **3 kat** ayrışıyor (ATR 1,14 →
3,38) — S3 bunu ele aldı ama mekanik aşama için not düşülür.

#### Çıkarım (hüküm DEĞİL — 2. ve 3. aşama yapılmadı)

`skor ≥ 45` **iyi bir SHORT seçicisi gibi davranıyor ve LONG kapısı olarak kullanılıyor.**
AYI'da `≥45` ham −4,043% → shortlamak +4,043% (maliyet %0,345). Ama bu **ham** aşamadır;
`CLAUDE.md`'nin kendi kaydı bir ham kenarın stopla ölebileceğini de, mekaniğin güveni
şişirebileceğini de gösteriyor. Kural önerisi için mekanik + portföy aşaması şart.

**Ön-kayıtlı yönlü tahmin kısmen tuttu:** *"gradyan çıkarsa BOĞA'da negatif, NOTR'de
düz"* yazılmıştı. BOĞA negatif ✅; NOTR düz değil, **o da negatif**.

---

### 🔴 VERİ TUZAĞI — `radar_archive.rejim` 2026-07-22'de TANIM DEĞİŞTİRDİ (2026-08-25)

Yukarıdaki ölçümün rejim kırılımı yapılırken bulundu. F10 SEZON×HAVA katmanlaması
[evren.py:294](evren.py#L294) **2026-07-22'de** eklendi; arşivin `rejim` alanı o
tarihten önce **eski tek-katmanlı** detektörden geliyor. Ad değişmedi, anlam değişti.

```
arsiv rejim  vs  F10 3'lu map   07-22 ONCESI  %21,1 uyum   ·   SONRASI  %96,8
arsiv rejim  vs  hava (eski)    07-22 ONCESI  %80,7 uyum
```

Somut: Temmuz'da 8.880 satır arşivde **BOGA**, tek tanımda **AYI** (`TEPKI_RALLISI`).
Genel uyum yalnız **%73,7**.

**Kural:** `radar_archive`'in `rejim` alanıyla 2026-07-22'yi **aşan** hiçbir kırılım
yapılmaz; rejim BTC mumundan **yeniden üretilir** (`scratchpad/skor_tahmin_rejim.py`
içinde hazır, botun canlı etiketiyle doğrulanmış). Bu, `funding_gecmis` birim
kırılmasıyla **aynı hata sınıfıdır**: alan adı değişmeden anlamı değişmiş.

---

### ❌ TabFM İNDİKATÖR OLABİLİR Mİ? — **DÜŞTÜ** (5 ölçütün 2'si) (2026-08-26)

**Ön-kayıt:** `scratchpad/tabfm/ON_KAYIT.md`, commit `43b0785` — koşumdan önce.
**Betikler:** `scratchpad/tabfm/01_veri.py` · `02_olcum.py` · `03_taban.py`
**N:** 3.598 sembol-saat · 236 sembol · 20 gün (2026-08-04..24) · 13 test günü

Soru: *"Botun elle konmuş eşikleri yerine bir tablo modeli koysak daha iyi sıralar mı?"*
Etiket **ham +24s getiri** (stop/hedef/ücret/fonlama YOK). Gün-bloklu ileri
doğrulama + **etiket ufku kadar ambargo**. Model TabFM 1.0.0 regresyon (6,14 GB, CPU).

| ölçüt | sonuç | eşik | |
|---|---|---|---|
| **S1** sıralıyor mu | rho **+0,1676** · t=+4,92 | t≥2,0 | ✅ |
| **S2** ters skoru geçiyor mu | fark **+0,0552** · t=+1,48 | t≥2,0 | ❌ |
| **S3** en iyi tek alanı geçiyor mu | fark **+0,1805** · t=+3,94 | t≥1,5 | ✅ |
| **S4** karıştırıcı (gün × ATR) | **22/39 = %56,4** | %60 | ❌ |
| **S5** dayanıklılık | +0,151 vs +0,187 (aynı işaret) | aynı | ✅ |

**HÜKÜM: DÜŞTÜ.**

#### Asıl bulgu — model bir şey buluyor, ama BEDAVA olanı geçemiyor

Model **gerçekten sıralıyor**: 13 günün 12'sinde pozitif, en iyi tek alanı
belirgin farkla geçiyor (t=+3,94). Bu, *"tek banttan türüyor, etkileşimden
kazanç yok"* beklentisini **çürütüyor** — etkileşimden kazanç VAR.

Ama rakibi tek alan değil, **`skor`'un ters çevrilmiş hâli** — bugün bedavaya
elde edilebilen şey. Fark yalnız **+0,055 rho** ve **t=+1,48**.

```
ters skor (BEDAVA)   rho +0,1124
TabFM (6,14 GB)      rho +0,1676
fark                     +0,0552   t=+1,48  (esik 2,0)
```

⚠️ **Bu "daha kötü" demek DEĞİL, "daha iyi olduğu kanıtlanamadı" demek.**
İşaret pozitif, ama 13 günde güç yetmiyor. Ön-kayıt bunu zaten yazmıştı:
*"olumsuz sonuç zayıf kanıttır."*

#### S4 neden önemli — düşmesi tesadüf değil

Aynı gün **ve** aynı oynaklık diliminde ayırma yalnız hücrelerin %56,4'ünde
tuttu. Yani kazancın bir kısmı **oynaklıkla** ilişkili, temiz kesitsel ayırma
değil. Bu, projenin zorunlu karıştırıcı kontrolü — agresör dengesi ve *son yeni
uç* tam burada ölmüştü.

#### BEKLENTİM YANLIŞ ÇIKTI — kayda geçiyor

Ön-kayıtta *"S1 geçer, S3 düşer"* yazmıştım. **S3 geçti**, hem de t=+3,94 ile.
Modeli hafife almışım. Düşüren S2 oldu — yani darboğaz *"model bir şey bulamıyor"*
değil, ***"bulduğu şeyin çoğu zaten bedavaya elde edilebiliyor."***

#### İKİNCİL — hükme girmedi

Gün ortalaması arındırılmış havuz rho **+0,2311** (N=2.668 sembol-saat),
gün-rho dağılımı −0,022 … +0,425, **12/13 gün pozitif**.
t'si **bilerek basılmadı**: gün kümelemesini yok sayar, güveni şişirir.

#### SINIRLAR

- **Tek pencere, tek rejim.** 20 gün, %87 NÖTR / %13 BOĞA. **Ayı verisi YOK.**
- **Seçilmiş havuz** — botun yüzeye çıkardığı adaylar, tüm evren değil.
- **Maliyet yok.** Ham fiyat. Fonlama 24 saatte ham kenarın büyük kısmını yiyor
  (2026-08-25 ölçümü) → ham kenar ödemeler sonrası kalmayabilir.
- **`n_estimators=16`**, süre bütçesine göre seçildi (4 saat); 32 ile sonuç
  değişebilir. Seçim **yalnız süreye** bakılarak, sonuç görülmeden yapıldı
  (kural commit `705670b`).
- Koşum süresi 2 sa 51 dk (CPU, GPU yok).

#### YOL BOYUNCA İKİ ONARIM

1. **Etiket örtüşmesi** (`81272c2`): bağlamın son gününün +24s etiketi test
   gününe bakıyordu (bağlamın %4-12'si). Ambargo kondu, koşumdan **önce**.
   Kullanıcının *"N küçüklüğü olay seviyesi örneklemeyle giderilir demiştin"*
   sorusu ortaya çıkardı.
2. **`safetensors` eksikti** — `tabfm[pytorch]` çekmiyor; prob çöktü, kuruldu.

#### VERİ NOTU — 2026-08-23 arşivde YOK

Bug değil: bot o gün `HALT_DUSUS`'te (192/192 tur, tur süresi 2,6 sn vs
komşularda 148-212 sn). Düşüş freni 08-22'de tetiklendi, 08-24'te elle devam
edildi. Radar normal koştu (4.660 satır) ama testbot taramadı.
Bu yüzden test günü 14 değil **13**.

### ❌ SKORUN TERS KENARI MEKANİKLE — **DÜŞTÜ** (2026-08-26)

**Ön-kayıt:** `ON_KAYIT_skor_mekanik.md`, commit `d7b607d` — koşumdan **önce**.
**Aşama:** üç aşamalı sıranın **İKİNCİSİ**. Birinci aşama: `e8c9d59`.
**Betik:** `scratchpad/skor_mekanik.py` · mekanik `olcucu.py`+`testbot.py`+config'ten
**birebir** (üç adaylı stop · asgari %2 · TP1 yapısal/2R · TP2 = TP1+1,5R ·
%40 kısmi @1,5R · iz-süren 2,0/1,5/1,0 ATR · zaman stopu 48s).
**N:** 9.507 işlem · 59 gün · giriş = anlık görüntünün bir sonraki saati · ofset −3.

```
kol                     N     BRUT    NET(cfg)  NET(olculen)  fonlama  stop-olma  kazanan
A SHORT skor>=45      930   +1,263%   +0,689%     +0,629%     -0,444     %73       %44
B SHORT skor<5       4145   -0,095%   -0,219%     -0,279%     +0,005     %79       %34
C LONG  skor>=45      911   -1,027%   -1,001%     -1,060%     +0,156     %88       %26   <- BOTUN KAPISI
D LONG  skor<5       3521   -0,251%   -0,385%     -0,445%     -0,005     %79       %33
```

| ölçüt | eşik | sonuç |
|---|---|---|
| M1 · A net > 0 | maliyet+fonlama sonrası | ✅ **+0,689%** (ölçülen slipajla +0,629%) |
| M2 · A−B (BİRİNCİL) | ≥+0,3 **ve** t ≥ +2,5 | ❌ ort +0,632 · **t = +1,56** |
| M3 · işaret tutarlılığı | ≥%60 gün | ❌ **29/49 (%59)** |
| M4 · zaman yarıları | aynı işaret | ❌ **İŞARET DÖNÜYOR** |
| M5 · zorunlu sınama | — | ✅ stop genişliği A/B **1,21 kat** (yakın), stop-olma %73/%79 |

**HÜKÜM: DÜŞTÜ.**

🔴 **Ölüm M4'te ve öğretici:** ham aşamada iki zaman yarısı **aynı işaretteydi**
(−3,343 / −1,067). Mekanik girince ilk yarı **döndü**:

```
ILK yari   A -0,211%   B +0,001%   fark -0,212
SON yari   A +1,411%   B -0,389%   fark +1,800
```

Kenarın tamamı ikinci yarıda. **Bu tam olarak `CLAUDE.md`'nin kayıtlı uyarısıdır:**
ham kenar mekanikle ölebilir — burada dönemsel olarak öldü. M5 geçtiği için bunu
"stop genişliği ayrışması" ile açıklayamayız; ayrışma yok (1,21 kat).

✅ **M1 geçti ve gömülmemeli:** A kolu maliyet **ve** fonlama sonrası pozitif.
Ama tek başına M1 hüküm değil — ön-kayıt dört ölçüt istiyordu.

#### Ön-kayıtlı beklentiler — biri tuttu, biri TUTMADI

- *"En olası ölüm biçimi: kenar var ama stop yiyor"* → **kısmen**. Kenar tamamen
  yenmedi (A hâlâ net pozitif), ama ham aşamadaki tutarlılık yok oldu.
- *"Fonlama SHORT'ta muhtemelen lehte"* → 🔴 **YANLIŞ.** Fonlama A'da **−0,444**,
  yani yüksek skorlu coinlerde fonlama **negatif**; SHORT ödüyor, tahsil etmiyor.
  Brütün üçte birinden fazlasını yiyor. Varsayım ölçülmeden yazılmıştı, ölçüm çürüttü.
- *"C kolu (botun bugünkü LONG'u) negatif çıkacak"* → **tuttu**, aşağıda.

#### C KOLU — botun bugünkü davranışı (ön-kayıtta KEŞİFSEL, hüküm değil)

`LONG skor≥45`: işlem başına net **−1,001%**, **%88 stop-olma**, kazanan **%26**,
medyan tutma 4 saat. Aynı olayda ters yön farkı **+1,690 puan**.
`LONG≥45 − LONG<5` = −0,431 (t=−1,12, 23/51 gün) → **anlamlı değil**, yalnız betimsel.

⚠️ **C, botun kendisi DEĞİLDİR:** bot ayrıca `smart` · taker · onay bekletme ·
maks pozisyon kapılarını uyguluyor. C bu kapıların hepsini atlar, yani **abartır**.

#### 🔴 KONTROL KOLUNDA SEÇİLİM — rapor edilmeli

`asgari_stop_pct = 2` düşük oynaklıklı adayları eliyor ve bu **kolları eşit
etkilemiyor**: `≥45` olaylarının ~%68'i işleme dönüştü, `<5` olaylarının ~%25'i.
B kolu *"düşük skorlu coinler"* değil, *"düşük skorlu ama stopu yeterince geniş
coinler"*. Farkın yönü bilinmiyor; kıyas bu yüzden ideal değil.

#### Bunun anlamı

Üç aşamalı sıra **tam olarak bunun için var**. Ham aşama güçlü ve tutarlı görünüyordu;
mekanik aşama tutarlılığı yok etti. **Botta hiçbir şey değişmez.**

### 🔴 `skor ≥ 45` FREN OLARAK — **AÇIKLAMA (b)**: LONG TARAFININ TAMAMI KAYBEDİYOR (2026-08-26)

**Ön-kayıt:** `ON_KAYIT_skor_fren.md`, commit `6bc6daf` — koşumdan **önce**.
**Betik:** `scratchpad/skor_fren.py` · mekanik `skor_mekanik.py` ile **aynı**
(olcucu+testbot+config'ten birebir) · yalnız **LONG**.
**N:** 17.715 LONG işlem · 441 sembol · 59 gün · tüm skor aralığı.

| ölçüt | eşik | sonuç |
|---|---|---|
| V1 · vetolanacak küme zararlı mı | net<0 **ve** t ≤ −2,5 | ✅ **−1,001%** · **t = −2,65** |
| V2 · 🔴 **AYIRICI** V−K | ≤−0,3 **ve** t ≤ −2,5 | ❌ ort −0,533 · **t = −1,69** |
| V3 · işaret tutarlılığı | ≥%60 gün | ❌ **28/51 (%55)** |
| V4 · zaman yarıları | aynı işaret | ✅ ilk −0,433 · son −0,981 |
| V5 · zorunlu sınama | — | ✅ stop genişliği **1,13 kat**, stop-olma %88/%80 → kıyas adil |

**HÜKÜM: AÇIKLAMA (b).** Ön-kayıt bu sonucu *"en olası tek sonuç"* diye
**önceden** yazmıştı (V1 ~%55, V2 ~%35).

#### 🔴 Asıl bulgu — skor bandı **fark etmiyor, hepsi negatif**

```
bant       N      net       stop-olma  kazanan
<2       1241   -0,519%       %81       %31
2-5      2280   -0,313%       %78       %35
5-10     3439   -0,206%       %78       %36
10-20    5062   -0,170%       %79       %36
20-30    2763   -0,165%       %82       %36
30-45    2019   -0,205%       %83       %33
>=45      911   -1,001%       %88       %26
```

`≥45` en kötü hücre ama **çıkarmak kurtarmıyor**: işlem başına −0,266% → −0,226%.
Hâlâ negatif. **Fren doğru teşhis değil.**

Eşik taraması bunu doğruluyor — 45'te uçurum yok, **plato** var
(`≥40 −0,625` · `≥45 −0,775` · `≥50 −0,869` · `≥60 −0,804`). Yani 45 sayısında
özel bir şey yok; yüksek skor genel olarak kötü, eşik keyfî.

#### 🔴 DAHA BÜYÜK OLGU — mekanik, ham beklentiyi işaretiyle birlikte yiyor

Birinci aşamada (`e8c9d59`) düşük bantlar **pozitifti** (`<2` +0,126% · `10-20`
+0,250%). Aynı olaylara botun mekaniği uygulanınca **hepsi negatife düşüyor**
(`<2` −0,519% · `10-20` −0,170%).

Maliyet yalnız 0,13 puan. Aradaki fark bundan **büyük** → farkı yiyen şey
**stop mekaniği**. Bu, projenin kayıtlı örüntüsüyle örtüşüyor: *"çıkışı sıkılaştıran
28 varyantın 28'i de kaldı"*, ve A-stop bir ölçümde ham kenarın **%65'ini** yemişti.

⚠️ **Hüküm değil, betimleme:** ham aşama sabit 24 saat tutuyordu, mekanik aşamanın
medyan tutması 4-6 saat. İki ölçüm **aynı ufuğa sahip değil**; işaret kaymasının ne
kadarı stop, ne kadarı ufuk — **ayrılmadı.** Ayrı ön-kayıt ister.

#### Sınırlar — aynen

- **Sentetik evren:** her radar anlık görüntüsü bir LONG girişi sayıldı. Bot ayrıca
  `smart` · taker · onay bekletme · maks pozisyon kapılarını uyguluyor.
  **Bu botun karnesi DEĞİLDİR**, botun *kapı öncesi havuzunun* karnesidir.
- **Eşitsiz eleme:** `asgari_stop=2` kolları eşit etkilemiyor — `≥45` olaylarının
  **%68,4'ü**, `<45` olaylarının **%34,9'u** işleme dönüştü. K kolu seçilmiş bir alt küme.
- 59 gün, tek pencere.

#### Ne değişti, ne değişmedi

**Değişen:** teşhis. Sorun *"skor eşiği yanlış yerde"* değil.
**Değişmeyen:** bot. Hiçbir dosyaya dokunulmadı.

**Yeni ve daha keskin soru:** botun LONG tarafı, giriş kapısı ne olursa olsun
kaybediyorsa, sıradaki inceleme **giriş seçiminde değil, ÇIKIŞ mekaniğinde** olmalı.

### 🔴 KENARI STOP MU YİYOR, SÜRE Mİ? — **STOP DEĞİL** (2026-08-26)

**Ön-kayıt:** `ON_KAYIT_stop_mu_sure_mu.md`, commit `1505a48` — koşumdan **önce**.
**Betik:** `scratchpad/stop_mu_sure_mu.py` · **N:** LONG 17.715 · SHORT 18.175 · 59 gün.

**Ayırma yöntemi:** her işlem için mekaniğin **kendi gerçekleşen tutma süresi** alınıp
aynı süre boyunca **stopsuz** ne olacağı hesaplandı → `Δ_stop` süre etkisini **tanım
gereği** sıfırlar. Süre etkisi ayrıca stopsuz sabit-ufuk eğrisiyle ölçüldü.

#### LONG (birincil)

```
mekanikli (botun kendisi)       net -0,266%    medyan tutma 6 sa
STOPSUZ, AYNI sure (eslesmis)   net -0,385%
D_stop                              +0,120 puan     <- STOP YARDIM EDIYOR
```

| ölçüt | eşik | sonuç |
|---|---|---|
| D1 · `Δ_stop` < 0 (stop yiyor mu) | t ≤ −2,5 | ❌ **+0,077** · **t = +0,94** — işaret **TERS** |
| D2 · zaman yarıları | aynı işaret | ✅ ilk +0,163 · son +0,094 (ikisi de **pozitif**) |
| D3 · süre eğrisinde pozitif bölge | — | ❌ **YOK** |
| D4 · baskın faktör | — | **SÜRE** (yayılım 0,470 vs stop 0,120) |

**Saf süre eğrisi (stopsuz, sabit ufuk) — LONG:**

```
1s -0,178  ·  2s -0,194  ·  4s -0,225  ·  6s -0,226  ·  12s -0,227  ·  24s -0,364  ·  48s -0,648
```

**HÜKÜM: D1 DÜŞTÜ — stop suçlu değil.** Ve süre ayarı da kurtarmıyor: **hiçbir ufukta
pozitif yok.** Geriye tek açıklama kalıyor: **bu evrende LONG yanlış taraf.**

#### 🔴 ÖNCEKİ ANLATIYI DÜZELTİYOR

Bir önceki ölçüm *"farkı yiyen şey stop mekaniği"* diye **betimlemişti** (hüküm
yazılmamıştı, ufuk uyumsuzluğu not düşülmüştü — iyi ki). **Yanlıştı.** Ufuk
eşleştirilince stop **yardım ediyor**. Kırılım:

```
STOP            N=11566 (%65)   D_stop +0,055
TP2             N= 3316 (%19)   D_stop -0,748   <- TP2 kazanci KESIYOR
STOP_TP1SONRASI N= 2662 (%15)   D_stop +1,479   <- kismi+iz-suren EN COK BURADA kazandiriyor
```

Skor bandına göre `Δ_stop`: `<5` −0,027 · `5-20` +0,080 · `20-45` +0,159 ·
**`≥45` +0,842** — stop en çok, en oynak yerde yardım ediyor.

⚠️ Bu, projenin *"A-stop ham kenarın %65'ini yedi"* kaydını **geçersiz kılmaz**;
o başka bir kapı ve başka bir stopla ölçülmüştü. Ama *"bizim stopumuz genel olarak
kenarı yer"* şeklindeki genellemeyi **bu evrende çürütür.**

#### SHORT (önceden ilan edilmiş ikincil — ölçüt uygulanmadı)

```
mekanikli net -0,021%   ·   D_stop -0,012 (t=+0,13, notr)
sure egrisi: 1s -0,099 · 4s -0,050 · 12s -0,003 · 24s +0,273 · 48s +0,614
```

LONG'un **tam aynası**: süre uzadıkça SHORT iyileşiyor, LONG kötüleşiyor.
🔴 **Bu bir strateji bulgusu DEĞİL, bu pencerenin YÖN bulgusudur** — radar evreni
bu iki ayda aşağı sürüklendi. `24s/48s SHORT` hücresi **kural yapılmaz** (en iyi
hücre seçilmez); ayrı ön-kayıt ve başka pencere ister. Ayrıca fonlama SHORT'un
**aleyhine** (48s'te −0,193) ve stopsuz kol **likidasyon içermiyor.**

#### İKİ TAHMİN DE YANLIŞ ÇIKTI — aynen yazılıyor

- **Benimki:** *"D1 geçer ~%70, stop yiyor"* → **DÜŞTÜ**, stop yardım ediyor.
- **Benim karşı-tahminim:** *"süre etkisi çıkarsa KISA sürenin aleyhine çıkar
  (maliyet sabit)"* → **YANLIŞ.** LONG'da kısa süre **daha az** kötü, uzun süre daha
  kötü. Maliyet mantığım doğruydu ama yön sürüklenmesi onu ezdi.
- **Kullanıcınınki:** *"süre yiyor"* → **baskın faktör gerçekten SÜRE** (0,470 vs 0,120).
  Yön beklentisi farklıydı ama teşhis doğruydu.

#### Nereye kaydı

Teşhis sırayla şuraya taşındı: skor eşiği → LONG tarafının tamamı → **stop değil,
süre değil, YÖNÜN KENDİSİ.** Botun LONG açması bu evrende hiçbir çıkış ayarıyla
kurtarılamıyor.

**Sınırlar:** sentetik evren (botun kapı öncesi havuzu, botun karnesi DEĞİL) ·
59 gün tek pencere · stopsuz kol likidasyonsuz, teşhis aracı · `asgari_stop` elemesi
kollara ortak uygulandı ama evreni daraltıyor.

---

### ❌ TabFM BOTUN KENDİ POZİSYONLARINI AYIRABİLİR Mİ? — **SINAMAYA DEĞMEZ** (2026-08-26)

**Ön-kayıt:** `scratchpad/tabfm/ON_KAYIT_pozisyon.md`, commit `e1097b5` — koşumdan önce.
**Betikler:** `scratchpad/tabfm/05_poz_veri.py` · `06_taze_mum.py` · `07_poz_olcum.py`
**N:** 119 pozisyon · 7 test günü (2026-08-19..26) · bağlam 112→227 pozisyon

Kullanıcı sorusu: *"Botun 19'undan sonra poz aldığı coinleri verip tahmin
yapmasını sağlayabilir miyiz?"* — yani **bizi −3.208 $'lık serinin dışında
tutabilir miydi?**

🔴 **TEŞHİS, hüküm değil.** Pencere *kaybettiğimizi bilerek* seçildi; tek rejim.

| ölçüt | sonuç | |
|---|---|---|
| **T1** PARA: üst yarı − alt yarı | **−24,97 $/poz** · t=−1,56 · pozitif gün **2/7** | ❌ |
| **T2** SİNYAL: ham +24s ile rho | +0,0578 · t=+0,38 · N=6 gün | ❌ |
| **T3** TABAN: skoru geçti mi | **hayır**, ikisinde de geride | ❌ |
| **T4** yalnız LONG | aynı işaret (**ikisi de negatif**) | ⚠️ bkz. aşağıda |

**SONUÇ: SINAMAYA DEĞMEZ.** TabFM yalnız ayıramadı, **tutarlı biçimde ters**
sıraladı — "iyi" dediği yarı 7 günün 5'inde daha çok kaybetti.

#### 🔴 TABAN ŞAŞIRTTI, SONRA KARIŞTIRICI KONTROLÜNDE ÇÖKTÜ

Botun **kendi skoru** (işaret bağlamdan seçilerek) çok güçlü göründü:

```
gun          isaret    ust $      alt $      fark
08-19          +1     +182,36   -298,59   +480,95
08-20          +1     -214,34   -707,54   +493,20
08-21          +1      +18,11   -363,10   +381,21
08-22          -1     -144,55   -170,89    +26,34
08-24          -1     -305,24   -392,35    +87,11
08-25          -1     -300,72   -428,16   +127,44
08-26          -1      +12,42    -95,73   +108,15
TOPLAM                -751,96  -2456,36  +1704,40      pozitif gun 7/7
```

7/7 gün pozitif, tek güne bağlı değil (en büyük gün çıkarılınca **6/6**, +1.211 $).

**Ama ön-kayıtta olmayan bir kontrol koştum** — kendi şaşkınlığımı sınamak için,
ve sonucu **zayıflatan** yönde:

```
KARISTIRICI 1 — skor ayrimi YON ayrimi mi?
   08-19  ust yaridaki LONG %60  ·  alt yarida %0    <-- AYRISIYOR
   08-20  ust yaridaki LONG %46  ·  alt yarida %8    <-- AYRISIYOR
   (kalan gunlerde her iki yari da %100 LONG)

KARISTIRICI 2 — YALNIZ LONG alt kumesinde
   TOPLAM fark  +252,77 $   (pozitif gun 5/6)
```

**+1.704 $ → +253 $. Etkinin %85'i YÖNDÜ.** En büyük iki gün (19-20 Ağustos)
skorla değil, **SHORT/LONG ayrımıyla** kazanmış.

Bu, `CLAUDE.md`'de kayıtlı **aynı hata sınıfının üçüncü vakası**: agresör
dengesi (ilk-saat getirisi sabitlenince işaret döndü) · *son yeni uç*
(11,8 puan → 2-4 puan). Karıştırıcı sabitlenince kalan artık küçük ve
kanıtlanmamış.

#### ⚠️ KENDİ ÖLÇÜTÜM KUSURLUYDU — T4

T4'ü *"yalnız LONG'da işaret aynı olsun"* diye yazmıştım. **Etki her iki kolda
da yoksa bu ölçüt kendiliğinden geçer.** Tam olarak bu oldu: ikisi de negatif,
T4 "GEÇTİ" yazdı ve hiçbir şey söylemedi.
**Doğrusu:** karıştırıcı ölçütü *"etki AYAKTA KALSIN"* der, *"işaret uyuşsun"*
demez. Bir sonraki ön-kayıtta bu düzeltilecek.

#### BEKLENTİM — yarısı tuttu

*"T1 ve T4 düşer"* yazmıştım. T1 düştü. T4 kâğıt üzerinde geçti ama yukarıdaki
kusur yüzünden anlamsız — yani **fiilen** o da bir şey göstermedi.

#### SINIRLAR

- 119 pozisyon / 7 gün · pencere **seçilmiş** · %67 BOĞA, tek rejim
- 22 Ağustos'tan sonra pozisyonların **%100'ü LONG** → yön boyutu o günlerde yok
- Bağlam 112-227 satır; dünkü ölçümde 800-3400'dü
- **`derinlik_giriste` (emir defteri) kullanılamadı:** test'te %100, bağlamda
  %1,7 (18 Ağustos'ta eklendi). 📌 08-18 sonrası tam dolu → birkaç hafta sonra
  **ayrı bir ölçümün** konusu; `CLAUDE.md`'nin *"gerçekten yeni bilgi"*
  listesindeki ilk madde.

#### VERİ NOTU

`klines_1h_uzun` 2026-08-25 06:00'da bitiyor; `+24s` etiketi örneklemi 119→79'a
düşürüyordu. Taze mumlar **ayrı bir önbelleğe** çekildi (`scratchpad/tabfm/taze_mum/`,
08-26 08:00'a kadar) — paylaşılan veri kümesine **dokunulmadı** (`CLAUDE.md`:
indiriciler birleştirmeli, ezmemeli). L1 opsiyonel yapıldı; L2 tüm 119'da var.

---

### ❌ TabFM NÖTR PENCEREDE (11-18 Ağu) — **SINAMAYA DEĞMEZ**, ama düşme BİÇİMİ öğretici (2026-08-26)

**Ön-kayıt:** `scratchpad/tabfm/ON_KAYIT_notr.md`, commit `abf488b` — koşumdan önce.
**N:** 61 pozisyon · **4** test günü · bağlam 49→97

Pencere seçildi çünkü **karıştırıcı yapısal olarak yoktu**: 11-18 arası 108
pozisyonun 101'i SHORT, rejim %100 NÖTR. Önceki ölçümü öldüren *"aslında yön
ayrımıydı"* açıklaması burada **mümkün değil**. Ayrıca pencere kârda (+238 $).

| ölçüt | sonuç | |
|---|---|---|
| **N1** PARA | +9,49 $/poz · t=+0,33 · **3/4** gün · toplam fark +169,71 $ | ❌ (4/4 gerekti) |
| **N2** SİNYAL | rho **+0,2448** · t=+1,21 · N=4 gün | ❌ (t≥1,5 gerekti) |
| **N3** TABAN | skor: para **+26,98** $/poz · rho **−0,0245** | ❌ |
| **N4** KARIŞTIRICI | **düşük oynaklık +728,20 $ · yüksek oynaklık −654,67 $** | ❌ |

#### 🔴 ASIL BULGU N4'TE — onarılmış ölçüt İLK KOŞUMDA işini yaptı

```
dusuk oynaklik  (|chg24| <= 10,5)   fark  +728,20 $   pozitif gun 3/4
yuksek oynaklik (|chg24| >  10,5)   fark  -654,67 $   pozitif gun 1/4
                                    ----------------
toplamda gorunen                          +169,71 $
```

Toplam sayı **iki zıt etkinin farkıdır.** Model düşük oynaklıkta sıralıyor,
yüksek oynaklıkta **tersine dönüyor**, net neredeyse sıfır kalıyor.

⚠️ **Eski T4 bunu göremezdi.** *"İşaret aynı olsun"* ölçütü toplamla düşük-kolu
karşılaştırıp geçerdi. Onarım (`4c3af9e`'de kaydedilmişti) **ilk kullanıldığı
koşumda** gizli bir bölünmeyi yakaladı.

#### BOĞA PENCERESİYLE KIYAS — aynı model, iki dünya

| | 19-26 (BOĞA) | 11-18 (NÖTR) |
|---|---|---|
| PARA yönü | **−24,97** $/poz | **+9,49** $/poz |
| pozitif gün | 2/7 | 3/4 |
| ham sinyal rho | +0,058 | **+0,245** |
| skorun rho'su | +0,115 | **−0,025** |

Nötr pencerede TabFM **ham sinyalde skoru geçiyor** (+0,245 vs −0,025) —
boğada tersiydi. Ama t=+1,21, N=4 gün: **güç yok.** Bu bir bulgu değil,
*"rejime göre değişiyor olabilir"* şüphesi.

#### ÇOKLU KARŞILAŞTIRMA — 2/2

Aynı model + aynı defter üzerinde **iki pencere denendi, ikisi de düştü.**
Ön-kayıt bunu şart koşmuştu: geçseydi bile *"rejim bağımlılığı iddiası"*
olacaktı, bulgu değil.

#### ÖN-KAYITTAN SAPMA — muhafazakâr yönde

5 test günü yazılmıştı; betikteki sabit `bağlam ≥ 40` alt sınırı **08-13**'ü
(bağlam 29) eledi → **4 gün**. N1 eşiği gün sayısıyla ölçeklendiği için
`4/5` yerine **`4/4`** istendi — yani **daha sıkı**. Gevşek eşik (3/4 ≥ 4/5
karşılığı) uygulansaydı N1 yine geçmezdi; N3 ve N4 bağımsız düştü.

#### BEKLENTİM — kısmen yanlış

*"N1 düşer"* demiştim; düştü **ama pozitif yönde** (+9,49, 3/4). Boğa
penceresindeki tutarlı terslik nötrde yok. Modeli yine hafife almışım.

---

### 🟡 TabFM BEŞ DEFTERİN HAVUZUNDA — **SINAMAYA DEĞMEZ**, ama HAM SİNYAL İLK KEZ EŞİĞİ GEÇTİ (2026-08-26)

**Ön-kayıt:** `scratchpad/tabfm/ON_KAYIT_havuz.md`, commit `e1b30d8` — koşumdan önce.
**Betikler:** `08_havuz_veri.py` · `09_havuz_olcum.py`
**N:** 705 test pozisyonu · 13 test günü · bağlam 89→774 · `n_est=32` · koşum ~2 sa

Havuz: `testbot` 205 · `golge` 377 · `defter2` 110 · `defter3` 10 · `ayna` 3.
Örtüşme tekilleştirildi (`ayna` testbot'un %98'i; `golge` %86 farklı).
Etiket **pozisyon getirisi = net/marjin** — defterlerin boyutlandırması farklı.

| ölçüt | sonuç | |
|---|---|---|
| **H1** üst yarı − alt yarı (getiri) | +2,026% · **t=+0,55** · pozitif 9/13 | HAYIR |
| **H2** ham +24s ile rho | **+0,1662 · t=+2,63** · N=12 gün | **EVET** |
| **H3** botun `skor`'unu geçti mi | evet (skor: +1,156% · rho −0,0824) | SAYILMAZ |
| **H4** yön × oynaklık, dördü de pozitif | **LONG/düşük −1,612%** · LONG/yüksek +0,722% · SHORT/düşük +2,508% · SHORT/yüksek +7,256% | HAYIR |
| **H5** yalnız gerçek ret (hükme girmez) | +1,558% · t=+0,34 · N=6 gün | — |

**SONUÇ: SINAMAYA DEĞMEZ** (H1+H3+H4 gerekiyordu).

#### 🟡 İLK KEZ: H2 EŞİĞİ GEÇTİ

Üç TabFM ölçümünde ilk kez ön-kayıtlı bir eşik gerçekten aşıldı.
Model **ham ileri fiyat hareketini** sıralıyor: rho +0,166, **t=+2,63**, 12 gün.

Ama **H1 düştü** (t=+0,55):

```
ham sinyal      VAR   (H2 gecti)
paraya donusum  YOK   (H1 t=+0,55)
```

Bu tam olarak `CLAUDE.md`'nin *ham getiri → ticaret mekaniği → portföy*
zincirinin **ikinci halkada kopması**. Zincirin ilk halkası bu kez tuttu.
Günlük değerler +36,36% ile −22,29% arasında saçılıyor; ortalama pozitif ama
gün-kümeli t'yi taşımıyor.

#### ⚠️ H3'ÜN GEÇMESİ SAYILMAZ — TABAN GÜRÜLTÜYDÜ

Taban işareti `rho(skor, pozisyon getirisi)`'nden seçiliyor. **Aynı gün ayrıca
ölçüldü: bu korelasyon −0,0308, p=0,39** — sıfırdan ayırt edilemez. İşaret
bağlamda kararsız: 10 gün `+1`, 3 gün `−1`. Yani taban rakip değil **para
atışı**; H3'ün geçmesi TabFM'in üstünlüğü değil **tabanın zayıflığıdır.**
Bu ölçütü bu koşumda geçerli saymıyorum. Kusur ölçüt tasarımındadır ve sonucu
görmeden fark edilmeliydi.

#### H4 — üçünde ayakta, birinde değil

```
LONG  / dusuk oynaklik   -1,612%   <-- TEK NEGATIF
LONG  / yuksek oynaklik  +0,722%
SHORT / dusuk oynaklik   +2,508%
SHORT / yuksek oynaklik  +7,256%
```

Önceki iki ölçümde karıştırıcı kapısı **daha sert** çökmüştü (N4: +728 / −655,
zıt işaret). Burada 4'te 3 pozitif ve tek negatif küçük. **Yine de geçmedi** —
ölçüt *"hepsinde ayakta kalsın"* diyor; bu bilinçli, çünkü bu proje 4'te 3'e
bakıp kural yazmanın bedelini ödedi.

#### SAYIM — 3. deneme, 3. düşüş

| ölçüm | N | geçen ölçüt |
|---|---|---|
| aday havuzu (08-25) | 3.598 satır / 13 gün | S1·S3·S5 (S2·S4 düştü) |
| testbot poz BOĞA | 119 / 7 gün | yok |
| testbot poz NÖTR | 61 / 4 gün | yok |
| **beş defter havuzu** | **705 / 13 gün** | **H2** (H3 sayılmaz) |

Ön-kayıt şunu şart koşmuştu: *geçse bile tek başına bulgu değildir.* Geçmedi.

#### SINIRLAR

- Çıkış kuralları havuzda **aynı** (`testbot`·`golge`·`defter2`·`defter3`) →
  H1'in etiketi bizim stopumuzun damgasını taşıyor. H2 bundan **bağımsız**.
- `golge` %74 `pump_long_tezi` → havuz "botun reddettikleri" değil.
- 13 gün, 08-13..08-26, tek pencere. **Ayı verisi yok.**
- Fonlama etiketlere dahil değil.

---

### 🔴 BOT, DÜŞECEĞİNİ KENDİ SKORUNUN SÖYLEDİĞİ COİNLERDE LONG AÇIYOR (2026-08-26)

Yukarıdaki havuz verisinden, **model kullanılmadan**. N=689 pozisyon (L1 dolu).

```
1) skor -> HAM +24s fiyat hareketi        rho = -0,1456   p = 0,00012
2) skor >= 45   N=320   SHORT %23 (=> %77 LONG)   ham hareket ort  -2,98%
   skor <  45   N=369   SHORT %52                 ham hareket ort  +0,91%
3) skor -> YONE GORE ISARETLI getiri      rho = -0,0895   p = 0,019
4) skor -> POZISYON GETIRISI (stop dahil) rho = -0,0308   p = 0,39
5) yon sabit:  LONG   rho(skor, ham) = -0,1395   p = 0,004
               SHORT  rho(skor, ham) = -0,0110   p = 0,86
```

`skor ≥ 45` botun **BOĞA rejimindeki LONG kapısıdır**. O bantta coinler ortalama
**%2,98 düşüyor** ve giriş **%77 LONG**. Etki LONG içinde ayakta (p=0,004);
SHORT'ta yok — yani skor SHORT'a yardım etmiyor, **LONG'da zarar veriyor.**

Madde (4) ayrıca yukarıdaki H3'ün neden sayılmadığını gösteriyor: skorun
pozisyon getirisiyle ilişkisi **sıfırdan ayırt edilemez.**

#### KOD BUNU ZATEN UYARMIŞTI — uyarı işletilmedi

[radar.py:138](radar.py#L138), `squeeze_bonus` notu:

> *"SINIR: tek 41 günlük pencere, YALNIZ ayı piyasası. **Boğada 'sert düşer'
> tersine dönebilir. Boğaya girildiğinde bu kural YENİDEN ÖLÇÜLMELİDİR.**"*

Boğaya girildi, kural yeniden ölçülmedi. Şimdi ölçüldü ve uyarı **haklı**
çıktı — ama beklenenden farklı biçimde: **kural tersine dönmedi, KULLANIMI
döndü.** Skor hâlâ düşecekleri işaretliyor; değişen şey, boğada `≥45`
kapısının LONG açtırması. Ayı rejiminde aynı skor SHORT açtırıyordu ve
*"long için en kötü kova = short için en iyi kova"* mantığı tutuyordu.

#### SAYIM

Bu, *skor ters çalışıyor* bulgusunun **ikinci veri kümesindeki teyididir**
(birincisi: aday havuzu, 2026-08-25, ters skor `t=+3,44`). Aynı olgu →
**bağımsız kanıt değil**, farklı kümede doğrulama. Yeni olan: **yön
uyuşmazlığı ilk kez sayısallaştı.**

🔴 **HÜKÜM YAZILMADI, BOTA DOKUNULMADI.** Bu bir ölçümdür. Kapı değişikliği
kullanıcı kararıdır ve ileri zamanda ayrı defterle sınanmalıdır.

---

### ❌ SPOT-PERP BASIS — **DÜŞTÜ** (5/5), ama işaret HİPOTEZ YÖNÜNDE ve ETKİ ÇOK KÜÇÜK (2026-08-26)

**Ön-kayıt:** `scratchpad/basis/ON_KAYIT.md`, commit `2e3ff43` — koşumdan önce.
**Betikler:** `00_yoklama.py` · `01_spot_indir.py` · `02_veri.py` · `03_olcum.py`
**N:** 216.358 gözlem · 357 sembol · **744 gün** (2024-08-11 .. 2026-08-24)
Model **kullanılmadı** — doğrudan kesitsel sıra korelasyonu.

`CLAUDE.md`'nin *"gerçekten yeni bilgi bandın dışındadır"* listesinden ilk kez
denenen aday. Eleme testini projenin en temiz farkıyla geçmişti (basis vs
fonlama %3,7 · vs fiyat %1,1-3,6; elenenler %60 ve %51).

| ölçüt | sonuç | |
|---|---|---|
| **B1** gün-kümeli rho | **−0,0152 · t=−4,85** · N=744 gün | ❌ **etki tabanı** |
| **B2** dört çeyrek | −0,0250 · −0,0206 · −0,0156 · **+0,0004** | ❌ |
| **B3** rejim | BOĞA −0,0396 · NÖTR −0,0123 · **AYI +0,0002** | ❌ |
| **B4** fonlama üçte-birlikleri | **alt +0,0254** · orta −0,0268 · üst −0,0369 | ❌ |
| **B5** `chg24` üçte-birlikleri | alt +0,0006 · orta −0,0155 · üst +0,0074 | ❌ |

**HÜKÜM: DÜŞTÜ.**

#### 🔑 B1 İSTATİSTİKTEN DEĞİL, ETKİ BÜYÜKLÜĞÜNDEN DÜŞTÜ

```
t = -4,85          <- son derece "anlamli"
|rho| = 0,0152     <- esik 0,02   ->  DUSTU
```

Ön-kayıt eşiği `|rho| ≥ 0,02` **VE** `|t| ≥ 3,0` diyordu. Gerekçesi de
yazılıydı: *"~750 gün kümesiyle hiçliğe yakın bir etki bile t>3 verir."*

**Bu taban olmasaydı B1 GEÇERDİ** ve `t=−4,85` ile güçlü bir bulgu ilan
edilirdi. Ölçüt koşumdan önce yazıldığı için bu olmadı.
📌 Bu, projenin *"yön aynı, güven yalan"* dersinin ikinci kez işe yaraması.

#### İŞARET DOĞRU ÇIKTI — hipotez yönünde

Ön-kayıt *"pozitif basis = kalabalık uzun taraf → `rho < 0`"* diyordu.
Ölçülen işaret **negatif**. Yani ekonomik sezgi doğru, **büyüklük yetersiz.**

#### ⏳ ETKİ ZAMAN İÇİNDE SÖNÜYOR

```
C1 2024-08..2025-02   -0,0250   t=-3,40
C2 2025-02..2025-08   -0,0206   t=-3,45
C3 2025-08..2026-02   -0,0156   t=-2,50
C4 2026-02..2026-08   +0,0004   t=+0,08     <- SIFIR
```

**Monotonik sönüm.** Etki iki yıl önce (zaten küçükken) daha büyüktü, bugün
yok. Bu, "kenar keşfedilince kapanır" örüntüsüyle uyumlu — ama tek pencere,
kanıt değil.

#### 🎯 B3 — İKİ YILLIK VERİNİN ASIL KAZANCI

```
BOGA  -0,0396  t=-3,88  N= 93 gun     etki EN GUCLU
NOTR  -0,0123  t=-2,79  N=313 gun     zayif ama ayni yon
AYI   +0,0002  t=+0,05  N=204 gun     YOK
```

**Ayı piyasasında etki yok.** Bu proje bugüne kadar hiçbir ölçümü ayı verisinde
sınayamamıştı; `CLAUDE.md`'nin en sık tekrar eden uyarısı (*"aynı tablo rejim
değişince tersine döndü"*) **ilk kez doğrudan test edildi** ve haklı çıktı —
tersine dönmedi ama **kayboldu.**

#### KARIŞTIRICI KIRILIMLARI

`B4`: fonlama **düşükken işaret TERSİNE dönüyor** (+0,0254, t=+5,19).
Yani basis'in bilgisi fonlamadan bağımsız değil — eleme testi korelasyonun
düşük olduğunu göstermişti (%3,7), ama **etkileşim var.**
📌 Ders: *"az korelasyonlu"* ile *"bağımsız"* aynı şey değil.

`B5`: etki yalnız **orta** `chg24` diliminde (−0,0155); uçlarda yok.

#### SINIRLAR

- Etiket **ham fiyat**; fonlama/ücret dahil değil. rho −0,015'lik bir kenar
  maliyet sonrası zaten kalmazdı.
- Tek ufuk (+24s), ön-kayıtta sabit. Başka ufka **bakılmadı**.
- 357 sembol = perp evreninin %63'ü (spotta işlem görenler). Spotta olmayan
  %37 en yeni/küçük listelemeler — sistematik bir dışlama.

#### NE ÖĞRENİLDİ

**Basis gerçekten yeni bilgi taşıyor** (eleme testi bunu gösterdi) **ama
kullanışlı değil.** Bu ikisi ayrı şeylerdir ve bu proje ilk kez ikisini
ayırabildi: aday, *"aynı şeyin başka ifadesi"* diye değil, **kendi başına
yetersiz** olduğu için elendi.

---

### 🔴 TabFM DOĞRU UFUKTA (+2 saat) — **DÜŞTÜ**, ve `+24s` BULGUSU GERİ ÇEKİLDİ (2026-08-26)

**Ön-kayıt:** `scratchpad/tabfm/ON_KAYIT_h2.md`, commit `454281d` — koşumdan önce.
**N:** 3.598 satır · 13 test günü — **`+24s` koşumuyla BİREBİR AYNI SATIRLAR.**

Kullanıcı itirazı: *"24 saat üzerinden değerlendirdin ama eldeki veri 2,5 saatte
en büyük etkiyi veriyor."* Ölçüldü, **haklı**:

```
HAVUZ 816 tekil pozisyon   medyan tutma 1,90 sa   ·   STOP ile kapanan %93, medyan 1,70 sa
<=2 sa kapanan %52          <=24 sa kapanan %97
```

**24 saatte pozisyonların %97'si çoktan kapanmış** — ölçülen fiyat hareketinin
neredeyse tamamı pozisyon kapandıktan *sonra* gerçekleşiyordu.

#### İKİ UFUK YAN YANA — tek değişen ufuk

| ölçüt | `+24s` | `+2s` | |
|---|---|---|---|
| **S1** rho ort · t | **+0,1676 · t=+4,92** ✅ | **+0,0379 · t=+1,45** | ❌ |
| **S2** TabFM − skor | +0,0552 · t=+1,48 ❌ | −0,0393 · t=−1,11 | ⚪ **GEÇERSİZ** |
| **S3** TabFM − en iyi tek alan | +0,1805 · t=+3,94 ✅ | **+0,0004 · t=+0,02** | ❌ |
| **S4** gün × ATR hücresi | %56,4 ❌ | %51,3 | ❌ |
| **S5** ilk/son yarı | aynı işaret ✅ | −0,013 vs +0,097 **TERS** | ❌ |
| ikincil havuz rho | +0,2311 | **+0,0380** | |

**HÜKÜM: DÜŞTÜ (5/5).**

#### 🔴 `+24s` BULGUSU GERİ ÇEKİLİYOR

2026-08-25'te *"TabFM ham sinyali görüyor"* diye kaydedilmişti (`S1` geçmişti).
**Doğru ufukta ayakta kalmıyor:** etki **4,4 kat** küçülüyor (havuz rho'da
**6,1 kat**) ve `t` eşiğin altına iniyor.

Daha keskin bir gösterge `S3`: `+24s`'te TabFM en iyi tek alanı **+0,1805**
farkla geçiyordu; `+2s`'te fark **+0,0004** — yani **tam olarak sıfır.**
Modelin 23 alanı birleştirmekten gelen üstünlüğünün tamamı **ufka özgüymüş.**

#### İKİ UFUK FARKLI ŞEY ÖLÇÜYOR

Günlük rho'ların birbirine korelasyonu **pearson +0,372 (p=0,21)** ·
spearman +0,324 (p=0,28) — **anlamsız.** 13 günün 5'inde işaret bile ters.
İyi bir `+24s` günü, iyi bir `+2s` günü demek değil.

#### 🔑 YENİ TABAN KAPISI İLK KULLANIMDA ATEŞLENDİ

```
skor tabani        : baglamda p<0,05 olan gun  0/13   -> S2 GECERSIZ (VOID)
en iyi alan tabani :                         13/13   -> S3 gecerli
```

`+2s`'te skorun bağlam korelasyonu **hiçbir günde** sıfırdan ayırt edilemedi.
Kapı olmasaydı `S2` *"TabFM tabandan kötü"* diye okunacaktı — oysa **taban
yoktu.** Kapı, havuz ölçümündeki `H3` sahte geçişinden sonra eklenmişti
(`454281d`); **ilk kullanıldığı koşumda** işini gördü.

📌 Yan bulgu: `skor`'un *"düşecekleri işaretlemesi"* **yavaş bir sinyal** —
24 saatte var, 2 saatte yok.

#### ÖN-KAYITTAN SAPMA — BETİMLEYİCİ EĞRİ KOŞULMADI

Ön-kayıt `1·2·3·4·6·12·24` saatlik betimleyici eğri vaat ediyordu.
**Koşulmadı** — her ufuk ayrı bir tam model koşumu demek (~3 sa × 7 = 21 saat).
Vaat edilip yapılmadığı için burada açıkça yazılıyor. Eğri istenirse
**modelsiz** (tek alan tabanlarıyla) ucuza üretilebilir.

#### METODOLOJİK KAZANÇ

Tasarım *"tek değişen şey ufuk"* ilkesine kilitlendi ve doğrulandı:
satır 3.598=3.598 · gün 20=20 · test günü 13=13 · gün başı satır **birebir** ·
skor vektörü **aynı** · etiket std 17,782→5,615 (oran 3,17; rastgele yürüyüş
beklentisi 3,46).

⚠️ **Satır kilidinde hata bulunup koşumdan önce onarıldı:** ilk parmak izi
`(sym, gün, skor)` **saati içermiyordu**; aynı sembol gün içinde birden çok
saatte aynı skorla görünüyor → 122 anahtar çakıştı, kilit 3.601 satır geçirdi.
Parmak izine `price/last1/last3/vol_x` eklendi ve kilit **çoklu-küme** yapıldı.

#### SAYIM — 4. TabFM karşılaştırması, 4. düşüş

| # | ölçüm | sonuç |
|---|---|---|
| 1 | aday havuzu `+24s` | düştü (S2·S4) — **S1 geçişi bu kayıtla geri çekildi** |
| 2 | testbot poz. BOĞA | düştü |
| 3 | testbot poz. NÖTR | düştü |
| 3b | beş defter havuzu | düştü (H1·H4) |
| **4** | **aday havuzu `+2s`** | **düştü (5/5)** |

#### 🔴 SINIR — HEPSİ KUTUNUN İÇİNDE

Ölçüldü: `aday_arsiv`, botun taradığı sembollerin **%6,3'ü** (tur başına 9-10 /
~142) ve skor tabanı **≥30** (evren medyanı 9,5). TabFM piyasanın **%94'ünü
hiç görmedi.**

```
RADAR (tam tarama)      N=58.359   medyan skor  9,5   min 0,0
ADAY ARSIVI (TabFM'e)   N=14.248   medyan skor 40,6   min 30,0
```

Dört ölçümün **dördü de** bu huninin içinde: `golge`/`defter2`/`defter3`
girişlerinin aday arşiviyle eşleşmesi %99,8-%100.

**Bu yüzden hüküm şudur:** *"TabFM botun kısa listesinin içinde iyileştirecek
bir şey bulamadı."* — *"model işe yaramaz"* DEĞİL. Kutunun dışı hiç ölçülmedi.
`radar_archive` 62 gün · 53.341 tekil (sembol,saat) · 18 alan %93-100 dolu ile
bunu mümkün kılıyor; **açık iş.**

#### GEÇMEZSE — kurulum

Kullanıcı kararı: **silinmiyor**, karar sonra verilecek.


---

### 🔴 TabFM KUTUNUN DIŞINDA — tam tarama, skorsuz — **DÜŞTÜ 4/4** (2026-08-27)

**Ön-kayıt `e1b6457`** (koşumdan önce yazıldı ve commit edildi). Ölçütler koşum
sırasında değişmedi. Kullanıcı sorusu: *"Radardan çektiğimiz veriyi skorlama
olmadan TabFM'e verseydik ne seçerdi, ne olurdu?"* → *"Kutunun dışını da test et."*

Bir önceki kayıtta **açık iş** olarak bırakılan madde budur; **kapandı.**

```
kaynak  radar_archive.jsonl — TAM TARAMA (bosluk kaydi 111 okundu)
veri    51.478 gozlem · 441 sembol · 62 gun (06-24..08-26)
etiket  HAM +2 saat perp getirisi  (dogru ufuk)
test    52 gun · 48.604 test gozlemi
girdi   19 alan · score OZELLIK DEGIL (yalniz ust-veri)
model   TabFM regresyon · n_est=8 · baglam 2.500'e orneklendi (sure butcesi)
sure    8,3 saat CPU
```

Önceki TabFM ölçümüne göre **14 kat gözlem, 4 kat test günü.**

#### SONUÇ

| # | ölçüt | eşik | sonuç | |
|---|---|---|---|---|
| **D1** | rho(tahmin, ham +2s), gün-kümeli | rho>0 · t≥2,0 · \|rho\|≥0,03 | **+0,0106 · t=+0,89 · 31/52 gün** | ❌ |
| **D2** | 🔴 SEPET: TabFM en iyi 10 − RASTGELE 10 | t≥2,0 | **−0,0106% · t=−0,31 · 28/52** | ❌ |
| **D3** | karıştırıcı: ATR/fiyat üçte-birlikleri | üçünde aynı işaret | yüksek oynaklık **TERS** (−0,0113) | ❌ |
| **D4** | karıştırıcı: rejim (BTC mumundan yeniden) | üçünde aynı işaret | **BOĞA TERS** (−0,0495, N=5 gün) | ❌ |
| **D5** | betimleyici sepetler | hükme girmez | aşağıda | — |

**HÜKÜM: DÜŞTÜ.** Dört ölçütün dördü de.

#### 🔴 D2 — ölçümün kalbi, ve en sert cevap

```
TabFM en iyi 10        ort -0,0488% · t=-1,08 · N=52 gun
RASTGELE 10            ort -0,0382% · t=-0,91 · N=52 gun
BOT en iyi 10 (skor)   ort -0,0592% · t=-1,01 · N=52 gun
TERS-SKOR 10           ort +0,0033% · t=+0,07 · N=52 gun
```

**TabFM'in seçtiği 10 coin, rastgele seçilen 10 coinden KÖTÜ.** Ön-kayıt bu
kontrolü *"kenar buldu"* ile *"işlem yapmadı"*yı ayırmak için koymuştu; ayırdı
ve TabFM'in tarafında bir şey çıkmadı. `TERS-SKOR` tek artı sepet ama
`t=+0,07` — gürültü.

#### ⚠️ BEKLENTİM YANLIŞ ÇIKTI — ve yanlış yönde

Ön-kayıtta *"D1 geçer, D3 düşer"* yazmıştım; gerekçe **51 bin gözlem ve 52
günle küçük bir sıralama kabiliyeti bile t≥2,0 üretir** idi. Üretmedi:
`t=+0,89`. Model beklediğimden **daha zayıf** çıktı. Etki boyutu tabanı da
(`|rho|≥0,03`) zaten karşılanmıyordu — iki ayrı sebepten düştü.

#### ⚠️ TEK HÜCRE BULGU DEĞİLDİR

`D4`'te `AYI` hücresi `rho +0,0487 · t=+2,10 · N=16 gün` verdi. **Bu bir bulgu
olarak kaydedilmiyor:** üç hücrenin biri, ön-kayıt yalnız **kesişimi** hükme
sokuyor, ve `BOĞA` hücresi ters işaretli. Çoklu karşılaştırma sayılıyor.

#### SAYIM — 5. TabFM karşılaştırması, 5. düşüş

| # | ölçüm | evren | sonuç |
|---|---|---|---|
| 1 | aday havuzu `+24s` | kutu içi | düştü (S2·S4) — S1 geçişi geri çekildi |
| 2 | testbot poz. BOĞA | kutu içi | düştü |
| 3 | testbot poz. NÖTR | kutu içi | düştü |
| 3b | beş defter havuzu | kutu içi | düştü (H1·H4) |
| 4 | aday havuzu `+2s` | kutu içi | düştü (5/5) |
| **5** | **radar tam tarama, skorsuz** | **KUTU DIŞI** | **düştü (4/4)** |

#### 🔑 ELEME ARTIK TAM

Önceki dört düşüşün hükmü *"TabFM botun kısa listesinin içinde iyileştirecek
bir şey bulamadı"* idi — çünkü model piyasanın **%94'ünü** hiç görmemişti.
Bu ölçüm o %94'ü de gösterdi: **51.478 gözlem, skor yok, botun kapıları yok.**
Sonuç değişmedi.

Yani *"kutu daraltıyor"* savunması **artık kullanılamaz.** Yeni bir TabFM
denemesi için gereken şey daha geniş evren değil, **bandın dışında yeni bir
girdi** (`CLAUDE.md` → emir defteri likiditesi · spot-perp basis · çapraz borsa
· pozisyon kompozisyonu). Basis denendi ve **düştü**; diğer üçü açık.

**Betikler:** `scratchpad/tabfm/10_kutu_disi_veri.py` · `11_kutu_disi_olcum.py`
**Ham çıktı:** `scratchpad/tabfm/kutu_disi.log` · özet `kutu_disi_ozet.json`
**Kurulum:** silinmedi (kullanıcı kararı) — 7,2 GB (`tabfm_venv` + `agirlik`).


---

## 2026-08-30 — ÜÇ BETİMLEYİCİ KAYIT (ön-kayıt YOK, eşik YOK)

⚠️ **Bunlar HÜKÜM DEĞİL.** Hipotez yazılmadan, geçme ölçütü konmadan, kullanıcı
sorularına cevaben koşuldu. Kural çıkarılmaz — yalnız *"o gün defterler ne
gösteriyordu"* kaydıdır. Tüm rakamlar **2026-08-30 13:04:29 anlık görüntüsüdür.**

⚠️ **YÖNTEM DERSİ — defter SOHBETİN İÇİNDE büyüdü.** Aynı oturumda testbot
kapanmış pozisyonu `243 → 288` oldu, kasası `6.414 → 5.458` düştü. İlk verdiğim
rakamlar üç gün sonra yalan söylüyordu. **Canlı deftere dayanan her sayı damgalanır**
(`CLAUDE.md` → hızlı değişen rakam). Mutabakat üç defterde de koşuldu:
testbot sapma **+0,08** · defter2 **−0,03** · defter3 **−0,01**.

---

### 1. GÖLGE — 19 Ağustos sonrası (BOĞA), botun kaybettiği pencerede

Kullanıcı sorusu: *"Bot boğada 19 Ağustos sonrası başarısız, gölge defter ne durumda?"*

```
pencere 2026-08-19 00:00 -> 2026-08-30 13:04
testbot  equity  9749,71 -> 5457,73   PENCERE REALIZE  -4291,98
golge    equity  7280,32 -> 8152,39   PENCERE REALIZE   +872,07
```

Kasada gölge önde. **Ama iki iş ayrılınca işaret dönüyor** (`CLAUDE.md`: gölge
tek soru yalıtmıyor):

| iş | poz | P&L | kazanma |
|---|---|---|---|
| `pump_long_tezi` — botun hiç oynamadığı LONG tezi | 305 | **+3.747,60** | %61,3 |
| **botun REDDETTİĞİ girişler** | 100 | **−2.699,24** | %43,0 |

Reddedilenlerin kırılımı — **altının beşi eksi**:

```
onay_bekle    50 poz  -1502,39      btc_pay_freni  6 poz  -189,57
stop_cok_dar  13 poz   -560,50      taker_soguma   2 poz  -117,22
long_veto     26 poz   -345,36      blowoff        3 poz   +15,80  <- TEK ARTI
```

🔑 **Gölgenin kasasına bakıp *"bot yanlış eliyor"* DENMEZ.** Gölgeyi taşıyan şey
botun elediği girişler değil, botun **hiç oynamadığı ayrı bir tez.** Botun
reddettikleri bu pencerede **2.699 $ kaybettirirdi** — kapılar işini yaptı.

⚠️ Fonlama asimetrisi bu pencerede **ısırmıyor**: ikisi de tahsil etti
(testbot +165,17 · golge +130,32). Olağan *"gölge LONG olduğu için fonlama
topluyor"* uyarısı burada geçerli değil.

**Betikler:** `scratchpad/golge_19agu.py` · `_b.py` · `_c.py`

---

### 2. DEFTER2 vs DEFTER3 — yönün etkisi, örtüşen pencerede

Örtüşen pencere `2026-08-25 16:12 → 08-30 13:04` (**4,9 gün**), yalnız o
pencerede **AÇILAN** pozisyonlar (defter2 pencere başında 8 açık pozisyon
devraldı — kaba equity farkı bu yüzden yanıltıcı):

```
defter2   82 poz   P&L   +97,66   kazanma %55   medyan marjin 491
defter3   79 poz   P&L  -765,76   kazanma %49   medyan marjin 665
FARK (D3 - D2):  -863,42 $
```

Ayrışma **tek noktada** — `chg24` işareti:

| dilim | defter2 | defter3 |
|---|---|---|
| `chg24 ≥ 0` — **ikisi de SHORT** (kontrol) | −3,05 · 67 poz · %52 | +674,48 · 61 poz · %57 |
| `chg24 < 0` — **D2 SHORT / D3 LONG** | **−6,42** · 15 poz · %60 | **−1.523,20** · 18 poz · **%17** |

```
defter3 LONG kolu olmasaydi:  +674,48   (gercek: -765,76)
```

Pencerede açılan **161 pozisyonun 161'i de `BOĞA` rejiminde** girildi. Yani
boğada bile bu evrende LONG kaybediyor — `defter3` ön-kayıtının *"LONG bu
evrende `t < −4`, LONG kolunun kaybetmesi BEKLENİYOR"* beklentisiyle aynı yönde.

⚠️ **Hüküm yazılamaz:** 4,9 gün, 18 LONG pozisyon, tek pencere, ayı verisi yok.
`durum.md`'de yazılı olduğu gibi bu iki defter için **ölçüt ve pencere hâlâ
belirlenmedi** — bu kayıt o açık maddeyi kapatmaz.

📌 08-27'de aynı ölçüm koşulduğunda defter3 `+43,79` idi ve *"sıralama VELVET'in
sonucundan bağımsız olarak defter2 lehine kilitli"* diye hesaplanmıştı
(`scratchpad/acik_poz_menzil.py`). Üç gün sonra sıralama aynı, **fark 20 kat
büyüdü.**

**Betikler:** `scratchpad/defter23_durum.py` · `_esit.py` · `_d.py` · `acik_poz_menzil.py`

---

### 3. 🔴 ÖDEME GEOMETRİSİ — dört defter aynı duvara çarpıyor

Kullanıcı itirazı: *"Yanlış yere bakıyor olabilir misin?"* — evet.

`kazanma oranı > %50` olan defterler bile para kaybediyor. Sebep seçim değil,
**kazanç/kayıp büyüklüğü**:

| defter | poz | kazanma | ort KAZANÇ | ort KAYIP | **oran** | beklenti/poz |
|---|---|---|---|---|---|---|
| testbot | 288 | %43,8 | +93,46 | −102,89 | **0,91** | −16,99 |
| golge | 631 | %55,9 | +86,35 | −114,23 | **0,76** | −2,02 |
| defter2 | 180 | %50,6 | +63,62 | −75,70 | **0,84** | −5,27 |
| defter3 | 80 | %48,8 | +87,00 | −102,11 | **0,85** | −9,92 |

Başabaş için gereken kazanma oranı `kayıp/(kazanç+kayıp)`:

```
testbot   gereken %52,4   gercek %43,8   ACIK -8,7 puan
golge     gereken %56,9   gercek %55,9   ACIK -1,0 puan
defter2   gereken %54,3   gercek %50,6   ACIK -3,8 puan
defter3   gereken %54,0   gercek %48,8   ACIK -5,2 puan
```

#### 🔑 ASIL GÖZLEM — DOĞAL DENEY

Bu dört defterin **seçim kuralları tamamen farklı**: farklı evren, farklı yön
kısıtı, farklı kapılar. Kazanma oranları **12 puanlık** bir aralığa yayılıyor
(%43,8 → %55,9).

**Ödeme oranı ise 0,76–0,91 dar bandında sıkışmış.**

Seçim değişiyor, geometri değişmiyor — çünkü dördü de **aynı çıkış kodunu**
paylaşıyor (`CLAUDE.md`: *"Çıkış kuralları bilinçli olarak testbot ile aynı —
fark yalnız girişten gelsin diye"*). Bu, tasarımın istenen yan ürünü: girişi
yalıtmak için çıkış sabitlendi, ve sabitlenen şey **bağlayıcı kısıt** çıktı.

#### ÖDEME ŞEKLİ NEREDEYSE İKİLİ

```
testbot   TP1'e ULASTI    116 poz  ort  +95,50  kazanma %92
          TP1'e ULASMADI  172 poz  ort  -92,85  kazanma %11
golge     TP1 var 271 ort +108,07 (%93)  ·  TP1 yok 360 ort -84,89 (%28)
defter2   TP1 var  70 ort  +78,17 (%96)  ·  TP1 yok 110 ort -58,36 (%22)
defter3   TP1 var  29 ort +116,09 (%100) ·  TP1 yok  51 ort -81,57 (%20)
```

🔴 **BU NEDENSEL DEĞİL — sonuca göre seçim (selection on outcome).** TP1'e
ulaşanlar zaten lehe hareket edenlerdir; kârlı olmaları tanım gereğidir.
*"TP1 kâr getiriyor"* diye okunamaz. Gösterdiği tek şey **şekildir**: kazananın
yarısı erken alınıyor, kaybedenin tamamı taşınıyor — `ort kazanç < ort kayıp`
üretmenin matematiksel yolu tam olarak budur.

🔴 **[EKLENDİ 2026-08-31] AYNI GÜN BAŞKA BİR OTURUM BUNU DAHA SERT KOYDU
(`65043f6`, GERİ ÇEKME).** Orada `TP1` üzerinden yapılan bir **pozisyon
büyüklüğü** bulgusu artefakt çıktı: TP1 bir **sonuçtur** (fiyat lehe 1,5R
gidince tetiklenir), ve TP1 kontrol katmanı eklenince işaret çöktü
(`t=+12,52 → +1,58`). Konan kural:

> *"Döngüsel diye etiketlenen her değişken, aynı veri üzerindeki sonraki
> **her** ayrıştırmada kontrol katmanı olur."*

**Bu kaydın ANA bulgusu (`ort kazanç / ort kayıp` oranı) o kanaldan geçmiyor**
— TP1 koşullaması içermez, doğrudan pozisyon P&L'inden hesaplanır. Ama
**yukarıdaki TP1 tablosu karar için kullanılamaz**; yalnız şekli gösterir.
İlgili: `b386738` (*zarar seçimden değil boyut ağırlığından — ama boyut da TP1
kanalından geçiyor, eyleme dönüştürülemez*) · `f6eebc3` (*"artıya geçip geri
verme" düştü; çıkış/kâr-alma tarafında eyleme dönüşebilir bulgu YOK*).

#### BU KAYIT NEYİ ÖNERİYOR — kural değil, ÖLÇÜT

Çıkış tarafında **30 varyant** denendi, geçen **1** tanesi çıkışı *gevşetiyordu*
(sabit %10 hedef); sıkılaştıran **29'un 29'u da kaldı**. Bu kayıt o **29/29** ile
**aynı yöne** bakıyor — ödeme oranı düşükse çare üst tarafı açmaktır.

⚠️ **[DÜZELTİLDİ 2026-08-31]** Bu paragraf ilk yazıldığında `28/28` diyordu —
sayımı kaynaktan okumadan tekrarladım. 30. varyant aynı gün (`b386738`)
düşmüştü. Projenin *"sayı tekrarlanmaz, sayılır"* kuralının ihlali.

Önerilen tek şey **ölçütün değişmesi**: bir çıkış varyantı denendiğinde
başarı ölçüsü **kazanma oranı değil, `ort kazanç / ort kayıp` oranı** olmalı.
Dört defterin dördünde de kazanma oranı yanıltıcı çıktı — `golge` %55,9 kazanıp
kaybediyor.

⚠️ **Bu bir ön-kayıt değildir.** Çıkış varyantı denenecekse ayrı ön-kayıt
gerekir ve **31.'si olarak sayılır** (güncel sayım `olcumler.md` başlığında).

**Betik:** `scratchpad/geometri.py` · ham çıktı `scratchpad/_kayit_ham.txt`

### 🟡 EMİR DEFTERİ DERİNLİĞİ — **DÜŞTÜ**, ama GÜÇ yetmediği için (2026-08-30)

**Ön-kayıt:** `ON_KAYIT_defter_derinligi.md`, commit `837631d` — koşumdan **önce**.
**Betik:** `scratchpad/defter_derinligi.py` · **N=1.056 pozisyon** · 5 defter ·
175 sembol · **yalnız 12 gün** (08-18 → 08-30).
**Yordayıcı (önceden atanmış):** `bası = notional / defter_usdt_20` — pozisyonumuzun
defterin yenen tarafına oranı.

```
ceyrek                N     ret ort    ret med   kazanan  kaldirac   chg24   slipaj
Q1 (poz/defter EN KUCUK) 264  +2,668%    +0,446%     %62      3,0     +12,7   0,0253
Q2                    264    +0,946%    +0,041%     %50      4,0     +12,0   0,0485
Q3                    264    +0,175%    -2,032%     %42      4,0     +12,9   0,0608
Q4 (poz/defter EN BUYUK) 264 +0,027%    -1,034%     %44      4,0     +14,0   0,0700
```

| ölçüt | eşik | sonuç |
|---|---|---|
| O1 · üst−alt çeyrek | ≤−0,3 **ve** t ≤ −2,5 | ❌ fark **−2,640** ama **t = −1,99** |
| O2 · monotonluk | ρ ≤ −0,75 | ✅ **ρ = −1,000** (kusursuz) |
| O3 · 🔴 **BELİRLEYİCİ** karıştırıcı | ≥%60 hücre | ✅ **6/6 (%100)** |
| O4 · defterler arası | ≥3/5 | ✅ **4/4** |
| O5 · şans (2000 permütasyon) | p ≤ 0,05 | ✅ **p = 0,0000** |

**HÜKÜM: DÜŞTÜ** — ön-kayıt dört ölçütün hepsini istiyordu, O1 tutmadı.

🔴 **Ama düşme sebebi İŞARET DEĞİL, GÜÇ.** Pencere **12 gün**, kullanılabilir gün
kümesi **11**. Etki büyük (−2,640 puan), kusursuz monotonik, 9/11 günde aynı yönde,
4/4 defterde aynı yönde, permütasyonda p sıfır. Eksik olan tek şey **küme sayısı**.

**Karıştırıcı elemeleri geçti:** `chg24` çeyrekler arası düz (+12,7 … +14,0) → pump
büyüklüğünün vekili değil. `kaldirac` düz (3-4) → oynaklığın vekili değil. Yön
kırılımında da aynı işaret: LONG −3,087 · SHORT −2,003.

#### 🔴 AÇIK KALAN AYRIM — bu hüküm yazılmadan çözülmeli

`bası` büyük ölçüde bir **sembol özelliğidir**: iki çeyrekte birden görülen sembol
sayısı yalnız **6**. Yani bulgu iki farklı şey olabilir ve ölçüm bunları **ayırmıyor**:

- **(a) boyutlandırma:** pozisyon/defter oranı önemli → kural: pozisyonu defterin
  derinliğine göre kırp
- **(b) coin seçimi:** derin defterli coinlerde daha iyiyiz → kural: sığ coine girme

Eşleşen 6 sembolde etki **−6,171 · t=−2,99 · 6/6 negatif** — (a) yönünü destekliyor
ama **N=6 sembol hiçbir şey kanıtlamaz.**

#### İkincil yordayıcılar (önceden ilan edilmiş, keşifsel)

```
slipaj_pct        ceyrek ort +1,490 · +1,408 · +0,463 · +0,456   rho -1,00
defter_usdt_20    ceyrek ort +1,839 · -0,041 · +1,317 · +0,701   rho -0,40
yetersiz=True     N=66 +0,953%  ·  False N=990 +0,954%  ->  fark SIFIR
```

`yetersiz` bayrağı hiçbir şey söylemiyor. Mutlak derinlik zayıf. **Oran güçlü.**

#### Beklentiler — biri yanlış, biri doğru

- *"O3'ü geçmesi ~%25"* → **yanlıştı**, 6/6 ile geçti.
- *"Kalın defter → daha iyi sonuç"* → **doğru**; pozisyon defterin yanında küçükken
  sonuç daha iyi.

#### 🔑 İKİNCİ BAĞIMSIZ ÖLÇÜM AYNI YERİ GÖSTERİYOR

2026-08-25'te portföy ölçümünde bulunmuştu: *"kazananların medyan exposure'ı 0,160,
kaybedenlerin 0,400"* — risk-önce boyutlandırma kazananları küçültüyor.
Bu ölçüm **farklı veriyle, farklı yöntemle** aynı yeri gösteriyor: **pozisyon
büyüklüğü**. İki bağımsız işaret bu projede nadirdir.

#### Sınırlar

- 12 gün · 11 gün kümesi — **tek eksik olan bu**
- Derinlik yalnız **dolan** pozisyonda kaydediliyor (seçilim yanlı; bu soru için meşru,
  *"daha iyi aday seçebilir miydik"* için değil)
- Defterin **tek tarafı** saklanıyor → **dengesizlik ölçülemez**, emir defterinin
  klasik kenarı hâlâ ölçülmemiş durumda
- Sembol yoğunlaşması sorun değil (top3 payı %19, 74/69 tekil sembol)

**Sıradaki adım açık:** aynı ölçüm ~4 hafta sonra tekrarlanır (küme sayısı 11 → ~40).
Ölçüt **değiştirilmez**; bugün düşen ölçütle yeniden koşulur.

### 🔴🔴 KAZANAN vs KAYBEDEN — TEK AYIRICI POZİSYON BÜYÜKLÜĞÜ (2026-08-30)

**Tür:** 🟡 **KEŞİFSEL — HÜKÜM DEĞİL.** Ön-kayıt yok; kullanıcı isteğiyle yapılan
patern taraması. Kural önerisi için **kendi ön-kaydıyla** sınanmalı.
**Betik:** `scratchpad/kazanan_kaybeden.py` · **N=1.460 pozisyon** · 6 defter.

#### Giriş anında HİÇBİR ŞEY ayırmıyor — bir şey hariç

Kazanan (736) vs kaybeden (724), giriş anı özellikleri, etki büyüklüğü `d`:

```
skor              d=-0,06      range_pos     d=+0,09      beklenen slipaj  d=+0,04
chg24 giriste     d=+0,10      kaldirac      d=-0,04      poz/defter orani d=-0,14
NOTIONAL ($)      d=-0,69   <-- TEK AYIRICI
```

`yon` · `smart` · `stage` · `rejim` dağılımları kazanan/kaybeden arasında **aynı**.
Botun bütün seçici alanları ayırt etmiyor. **Ayıran tek şey pozisyonun büyüklüğü.**

#### Çeyrekler (aynı gün + aynı defter içinde hesaplandı)

```
ceyrek  N     notional med   kazanma   ort ret     TOPLAM $      poz basi $
Q1     363          982       %85      +6,890%   +20.680,12       +56,97
Q2     363        1.676       %58      +1,333%    +7.383,07       +20,34
Q3     365        2.478       %31      -1,409%   -12.867,31       -35,25
Q4     364        4.085       %29      -1,496%   -25.581,04       -70,28
                                                 ------------
                                        TOPLAM   -10.385,16
```

**Q3+Q4 olmasaydı defterler −10.385 yerine +28.063 olurdu.**

#### Geçtiği kontroller

| kontrol | sonuç |
|---|---|
| aynı gün **ve** aynı defter | **59/63 hücrede (%94)** küçük önde · ort fark **+5,913** · **t = +13,35** |
| stop genişliği sabitlenince (testbot) | **3/3 dilimde** küçük önde (+5,64 · +8,54 · +9,90) |
| defterler arası | **5/5** |
| haftalar arası | **3/3** |
| likidasyon artefaktı | **yok** (4 çeyrekte de sıfır likidasyon) |
| dolar mutabakatı | yüzde artefaktı **değil** — dolar bazında da aynı |

#### 🔑 Aynı olgu DÖRDÜNCÜ kez, dört farklı yoldan

1. 2026-08-25 portföy simülasyonu: kazananların exposure medyanı 0,160 · kaybedenlerin 0,400
2. 2026-08-25: eşit-ağırlıklı +29,88 puan → gerçekleşen −10,96
3. 2026-08-30 emir defteri: `notional/defter_usdt_20` kusursuz monotonik
4. **bu ölçüm:** giriş anındaki tek ayırıcı `notional`, dolar bazında doğrulandı

**Kaldıraç kırılımı aynı şeyi söylüyor:** dokuz kaldıraç bandının sekizinde
ortalama yüzde getiri **POZİTİF**, ama dolar toplamı **NEGATİF**.
🔴 **Bot ortalamada haklı, büyük bahis koyduğu yerde haksız.**

#### ⚠️ MEKANİZMA AÇIKLANMADI — hüküm bu yüzden yazılmıyor

`t=+13` bu kadar çalışılmış bir sistemde **kendi başına şüphe sebebidir**. Aday
mekanizmalar (piyasa etkisi · risk-önce boyutlandırmanın stop genişliğiyle bağı ·
kaldıraç klempi) **elenmedi**; stop genişliği kontrolü etkiyi ortadan kaldırmadı,
yani en bariz mekanik açıklama tutmadı. **Sebep bilinmeden kural yazılmaz.**

#### İlk 30 dakika — ikinci bulgu (yalnız testbot, N=239)

Karar verilebilir pencerede güçlü ayrım (döngüsel olmayan biçimde):

```
30dk sonunda pnl>0    N=117  kazanma %62  ort ret +3,128%  |  degilse N=122 %27 -1,318%
30dk MAE > -%1        N=111          %59         +2,140%   |          N=128 %32 -0,253%
30dk artida %50+      N=127          %59         +2,469%   |          N=112 %28 -0,968%
```

⚠️ Bu bir **çıkış sıkılaştırması** önerisidir ve bu projede sıkılaştıran
**28 varyantın 28'i de kalmıştı**. Prior kötü; ayrı ön-kayıt şart.

#### Atlanmış alanlar (izlemede toplanıyor, hiç ölçülmedi)

`arti_oran` · `atr_canli`/`atr_giriste` (**oynaklık GENİŞLEMESİ — seviye değil değişim**) ·
`ma50_mesafe` · `radar_izi` · `stop_mesafe_pct` · `tp1_alindi`

⚠️ **5 dakikalık izleme yalnız `testbot`'u kapsıyor** (`kaynak='canli'`, 241 pozisyon).
Diğer dört defterin yol verisi **YOK** — bu bir veri boşluğudur.

#### EK — MEKANİZMA ARANDI, BULUNAMADI (2026-08-30, aynı gün)

Kural yazmadan önce *"büyük pozisyonlar neden kaybediyor"* sorusu kovalandı.
**Cevap bulunamadı.** Elenenler ve kalan:

**Kod okundu** ([testbot.py:1218-1242](testbot.py#L1218)): boyutlandırma sanıldığı gibi
saf risk-önce **değil**. `marjin = baz_equity × marjin_pct(skor)` ve kaldıraç iki yerden
klempleniyor (`kaldirac_min/max` + `kaldirac_guvenlik_kirp`); risk hedefi yalnız
**yukarı yönlü kırpıyor**, aşağı yönlü doldurmuyor.

**ELENEN AÇIKLAMALAR:**

| aday | ölçüm | sonuç |
|---|---|---|
| skor (boyut skordan türüyor) | `log(notional)` ↔ `skor` korelasyon **−0,064**; `marjin` ↔ `skor` **+0,068** | ❌ `marjin_pct` pratikte hiç değişmiyor (skorların çoğu 45 civarı, fonksiyon orada düz) |
| stop genişliği | kazanan/kaybeden **d = +0,00**; stop × skor hücrelerinde **4/4** etki ayakta | ❌ |
| zaman / equity | equity d = **−0,05** | ❌ |
| döngüsellik (ilk kare geç çekilmiş olabilir) | 4 çeyrekte de ilk kare **0,05 sa**, ilk kare pnl ≈ **0**, TP1 alınmış %0-3 | ❌ temiz alt küme (228/235) **aynı sonucu** veriyor |

**KALAN OLGU — açıklanamadı:**

```
carpan ayristirmasi (notional = risk$ / stop%)
  notional      d = -0,87
  RISK ($)      d = -1,13   <- EN GUCLU AYIRICI
  stop%         d = +0,00
  equity        d = -0,05

risk ceyrekleri:  38,80$ -> %98 kazanma  ·  68,84$ -> %39  ·  88,68$ -> %19  ·  127,58$ -> %19
ayni gun icinde:  risk kucuk olan 14/15 gunde onde, t = +6,80
```

🔴 **%98 kazanma oranı olağandışıdır ve açıklaması yoktur.** Boyutlandırma formülü
bu dağılımı üretmemeli: hedef risk equity'nin %1,5'i (~129 $) iken Q1 pozisyonları
**%0,65**'te (~39 $) duruyor — yani risk hedefin çok altında kalmış ve bunun neden
olduğu bulunamadı. Aday yollar (smart karşı yönde → `hedef_risk/2` · kaldıraç klempi)
tek başına bu dağılımı açıklamıyor.

**BU YÜZDEN KURAL YAZILMIYOR.** Etki gerçek ve dört yoldan doğrulandı, ama sebebi
bilinmeden *"pozisyonu küçült"* demek, neyi küçülttüğünü bilmeden müdahale etmektir.

#### 🔧 SOMUT SONRAKİ ADIM — ölçümü değil, KAYDI düzelt

`risk_usdt` kodda **hesaplanıyor** ([testbot.py:1239](testbot.py#L1239)) ve pozisyon
sözlüğüne yazılıyor, ama **işlem defterine yazılmıyor**. Şu an ancak
`pozisyon_izleme`'nin `stop_mesafe_pct` alanından **türetiliyor** — ve o yalnız
`testbot`'u kapsıyor (N=235), diğer dört defterde **hiç yok**.

**Öneri:** işlem defterine iki alan eklensin — `risk_usdt` ve girişteki `stop`.
⚠️ `CLAUDE.md` → BUG İSTİSNASI sınaması: *"bu değişiklik botun hangi işlemi açacağını
değiştiriyor mu?"* → **HAYIR.** Yalnız kaydı genişletir, davranışa dokunmaz →
ölçüm penceresi kırılmaz. Bu yapılmadan mekanizma beş defterde birden aranamaz.

### 🔴🔴 GERİ ÇEKME — POZİSYON BÜYÜKLÜĞÜ BULGUSU ÇÜRÜDÜ (2026-08-30, aynı gün)

**Kullanıcı ısrarı sayesinde yakalandı:** *"mekanizmayı bulman lazım... %98 aradığımızın
da üstü."* Mekanizma arandı ve **artefakt çıktı. Bulgu GERİ ÇEKİLİYOR.**

#### Artefaktın kalbi

```
notional Q1   TP1 alan %83   kazanma %85
notional Q2   TP1 alan %53   kazanma %58
notional Q3   TP1 alan %17   kazanma %31
notional Q4   TP1 alan %10   kazanma %29
```

**Kısmi kâr alma oranı, kazanma oranını neredeyse birebir izliyor.** Ve `TP1 alındı`
bir SONUÇtur — fiyat lehe 1,5R gittiğinde tetiklenir. Yani "küçük pozisyon kazanıyor"
cümlesi, "fiyatı lehine gitmiş pozisyonlar kazanıyor" cümlesinin kılığıymış.

#### Kontrol katman katman — nerede çöktüğü

```
gun                                  19/19  hucre (%100)  t=+11,40
gun + defter                         61/65        (%94)   t=+12,81
gun + defter + YON                   68/72        (%94)   t=+12,52
gun + defter + yon + TP1 DURUMU      43/106       (%41)   t= +1,58   <- COKTU
```

TP1 sabitlenince:

```
TP1 ALDI  N=593   Q1 %97 / Q2 %96 / Q3 %93 / Q4 %87     (hepsi kazaniyor)
TP1 YOK   N=862   Q1 %21 / Q2 %17 / Q3 %23 / Q4 %23     (hepsi kaybediyor)
```

Her iki grubun **içinde** notional ayırmıyor. `TP1 YOK` grubunda işaret **ters** bile
dönüyor (en büyük çeyrek en iyi: −1,91 vs −5,11).

#### 🔴 AYNI ARTEFAKT EMİR DEFTERİ ÖLÇÜMÜNÜ DE ÇÜRÜTÜYOR

`ON_KAYIT_defter_derinligi.md` / commit `9751a6a` — *"düştü ama güç yetmedi, en umut
verici bulgu"* diye yazılmıştı. **O da aynı artefakt:**

```
KONTROLSUZ   Q1 +2,697% ... Q4 +0,029%   (TP1 alan %53 -> %29)
TP1 ALDI     Q4-Q1 = -1,57
TP1 YOK      Q4-Q1 = +0,47      <- ISARET DONUYOR
```

`bası` çeyrekleri boyunca TP1 alma oranı %53 → %29 düşüyor; gradyanı üreten buydu.

#### 🔴 "DÖRT BAĞIMSIZ ONAY" — DÖRDÜ DE AYNI ARTEFAKTMIŞ

Aynı gün *"dört ayrı yoldan aynı yere çıkıyoruz"* diye yazılmıştı. **Yanlış.**
Dördü de `notional`/`exposure` tabanlıydı ve dördü de aynı TP1 kanalından geçiyordu:
2026-08-25 exposure kıyası · 2026-08-25 eşit-ağırlık kıyası · 2026-08-30 emir defteri ·
2026-08-30 kazanan/kaybeden. **Bağımsız değillerdi.**

#### Ders — kayda geçiyor

⚠️ **`kismi` (TP1 alındı) bir SONUÇ değişkenidir ve bu betiğin kendi B bölümünde
"DÖNGÜSEL, karar için kullanılamaz" diye ETİKETLENMİŞTİ** (`False: KAZ%25/KAY%95`).
Sonra notional analizinde **kontrol edilmedi.** Kusur bilgi eksikliği değil,
**uygulama**: döngüsel diye işaretlenen değişken, ikinci analizde kontrol listesine
alınmadı.

🔑 **Grep'lenebilir refleks:** bir ölçümde *"döngüsel"* diye etiketlenen her değişken,
**aynı veri üzerindeki sonraki her ayrıştırmada kontrol katmanı olarak** kullanılır.

⚠️ Ayrıca bir **veri tutarsızlığı** bulundu (bulguyu etkilemiyor, kayda geçiyor):
`TP1_KISMI` kaydında `marjin` yarıya yazılıyor ama `notional` tam kalıyor →
`(notional/marjin)/kaldirac` TP1'li pozisyonlarda **2,00**, diğerlerinde 1,00.
`notional` iki kayıtta da aynı (son/ilk = 1,00), yani o alan güvenli.

#### Geriye ne kaldı

**Pozisyon büyüklüğü hakkında hiçbir şey.** Giriş anında kazananı kaybedenden ayıran
**hiçbir alan bulunamadı** — skor, chg24, range_pos, kaldıraç, yön, smart, stage,
rejim, slipaj, defter derinliği, **ve notional.** Hepsi ayırmıyor.

Bu, projenin *"bot ne alınmayacağını biliyor, ne alınacağını bilmiyor"* hükmünü
zayıflatmıyor — **güçlendiriyor.**


---

### 🔻 REJİM DÖNÜŞ DEDEKTÖRÜNÜN ÜST SINIRI — **ÖDÜL KÜÇÜK** (2026-08-30)

**Betimleyici, ön-kayıt YOK.** Anlık görüntü **2026-08-30 14:18**.

🔴 **Bu ölçüm, onu öneren kişinin (benim) 10 dakika önceki tavsiyesini çürüttü —
iş yapılmadan önce.** Kayıt bu yüzden değerli.

#### NEDEN KOŞULDU

Kullanıcı bir X gönderisi getirdi: opsiyon *25-delta put skew*'inin fiyatı 6-18
dakika öncülediği iddiası. Değerlendirirken `olcumler.md`'nin 08-24 kaydına
dayanarak *"Deribit skew'i TabFM'in her varyantının önünde"* dedim. Gerekçem o
kayıttaki şu cümleydi:

> *"Botun sorunu stop genişliği değil: **rejim döndüğünde hâlâ eski yönde işlem
> açması.** 08-20'de BTC %14 ralli yaparken SHORT açtı."*

Tavsiye vermeden **önce ödülü ölçmem gerekiyordu.** Ölçmedim; kullanıcı
*"faydası tam olarak ne"* diye sorunca ölçtüm.

#### YÖNTEM

Her kapanmış pozisyon için **tutma süresi boyunca** BTC'nin hareketi
(`fapi/v1/klines`, 1sa, kalıcı uç). Üç kova: yön BTC'ye **ters** · BTC ile
**aynı** · BTC **yatay** (|hareket| < %0,25). Soru: *"ters yöndeki pozisyonların
hiçbiri açılmasaydı"* — yani **mükemmel** bir dedektörün üst sınırı.

#### SONUÇ

```
TESTBOT   toplam -4903,34
  BTC YATAY iken    161 poz (%55,3)   -4666,18   <- KAYBIN %95'I BURADA
  BTC'ye TERS        75 poz (%25,8)    -570,80
  BTC ile AYNI       55 poz (%18,9)    +333,64
  mukemmel dedektor:  -4903 -> -4333   kurtardigi +570,80  =  kaybin %11,6'si
```

| defter | şimdi | mükemmel dedektörle | kurtardığı |
|---|---|---|---|
| testbot | −4.903,34 | −4.332,54 | **+570,80 (%11,6)** |
| defter2 | −947,36 | −441,42 | +505,94 |
| defter3 | −862,43 | **+164,69** | +1.027,12 |

#### 🔑 HÜKÜM

**Botun kaybı BTC'ye ters düşmekten gelmiyor.** Kaybın **%95'i BTC yatayken**
oluşuyor — altcoin'in kendi hareketinde, BTC'nin yönünde değil. Mükemmel bir
rejim dönüş dedektörü bile ana defterin kaybının **%11,6'sını** kurtarıyor.

`defter3` istisna (ters yöndeki 11 pozisyon −1.027, dedektörle defter artıya
geçiyor) — ama 4,9 günlük ve 84 pozisyonluk.

⚠️ **KARIŞTIRICI, açıkça yazılıyor:** *"BTC yatay"* = tutma süresi boyunca
hareket < %0,25. Medyan tutma 1,7-1,9 saat olduğu için **kısa tutmalar yapısal
olarak "yatay" kovasına düşüyor** — kova kısmen tutma süresinin vekilidir.
Yön yine de belirgin: TERS kova pozisyonların yalnız %25,8'i ve kaybın %11,6'sı.

#### GÖNDERİNİN DOĞRULAMASI — kayda geçiyor ki tekrar tartışılmasın

| iddia | doğrulanan |
|---|---|
| *"CBOE veriyi gerçek zamanlı ve ücretsiz yayınlıyor"* | **Cboe SKEW Index günde BİR KEZ, kapanışta** hesaplanıyor; Cboe 2025'te intraday'e geçmeyi **teklif etti** (konsültasyon Haziran 2025'te kapandı, tarih açıklanmadı) |
| *"canlı 25-delta skew"* | Cboe skew'i **"End-Of-Day Volatility Skew Data"** adıyla DataShop'ta **satıyor** |
| ücretsiz kaynaklar | MarketChameleon · Barchart: **15 dk gecikmeli** → 6-18 dk öncülüğü yer |
| *"2019 arxiv, parçacık sürüklenme"* | **bulunamadı.** En yakın gerçek çalışma Cont & Mueller, `arXiv:1904.03058` — emir defteri SPDE'si; skew, Citadel, tahmin **yok** |
| *"%71 kazanma oranı"* | ödeme oranı ve maliyet yok → anlamsız (`golge` %55,9 kazanıp kaybediyor) |
| *"14 ayın 14'ü pozitif"* | uyarı işareti, güven işareti değil |

**Gönderi uydurma.** Altındaki tek gerçek veri kaynağı Deribit (BTC/ETH IV skew
+ DVOL, genel API kimlik doğrulaması istemiyor).

#### ERİŞİM — ölçüldü, KAPALI

```
Binance fapi     OK    0,8 sn
genel internet   OK    0,4 sn
Deribit          HATA 12,0 sn (timeout)   <- bu makineden erisilemiyor
```

Geçmiş verinin var olup olmadığı **ölçülemedi** (bağlanılamadı). Yoksa
`perp_seri` gibi **ileriye doğru biriktirme** gerekir.
Ayrıca botun 119 sembolünün **hiçbirinin** likit opsiyonu yok (290 işlemin 0'ı)
— skew ancak piyasa geneli **rejim girdisi** olabilirdi, coin başına sinyal değil.

#### SIRALAMAYA ETKİSİ

```
1. odeme geometrisi   kaybin %100'une dokunuyor · veri ELDE · maliyet SIFIR
2. Deribit skew       kaybin ~%12'si · borsa KAPALI · gunler + VPN
3. TabFM varyantlari  5 olcumde de bir sey bulunmadi
```

**Yöntem dersi:** *"şu veri kaynağını ekleyelim"* önerisi, **ödülün üst sınırı
ölçülmeden** yapılmamalı. Üst sınır elde olan veriyle ve dakikalar içinde
hesaplanabiliyordu.

**Betik:** `scratchpad/odul_boyutu.py` (BTC önbelleği `.gitignore`'da)

### ❌ KAPI SİSTEMİNİN DENGELİ DENETİMİ — **A ve C DÜŞTÜ**, B kısmi (2026-08-30)

**Ön-kayıt:** `ON_KAYIT_kapi_dengesi.md`, commit `bd327a6` — koşumdan **önce**.
**Betikler:** `scratchpad/kapi_veri.py` · `kapi_karne.py` · `kapi_erken_cikis.py`
**Veri:** `testbot_aday_arsiv.jsonl` (31 alan, gizli seçilim YOK) × 5 defter →
**1.467 pozisyon, %84 eşleşme**, medyan gecikme 2,6 dk.

⚠️ **Ön-kayıtta tasarım kusuru — koşumdan önce fark edildi, DÜZELTİLMEDİ:**
keşif penceresi `N=253 · 9 gün · dolar −168` iken doğrulama `N=984 · 12 gün ·
−8.228`. Keşif hem küçük hem **neredeyse hiç zarar taşımıyor.** Tarihleri sonradan
değiştirmek disiplin ihlali olurdu; ön-kayıtlı hâliyle koşuldu.

#### A KOLU (eklenecek kapı) — **DÜŞTÜ, 0/26**

26 aday koşulun **hiçbiri** hak kazanmadı. Ve bu bir güç sorunu **değil**:

| tarama | N | gün | dolar | hak kazanan |
|---|---|---|---|---|
| keşif (ön-kayıtlı) | 253 | 9 | −168 | **0/26** |
| tüm pencere (keşifsel kontrol) | 1.237 | 21 | −8.397 | **0/26** |

🔴 **Engellenebilecek her dilimin işlem başı getirisi POZİTİF.** Sınananlar:
`vol_x` · `oi3` · `oi24` · `rel3` · `last1` · `last3` · `btc_chg3` · `taker` ·
`comp` · `ma50_mesafe` · `dip_yakit` · `ayrisma` · `dusuk_float` · `stage`.

**Yapısal gözlem:** dilimlerin çoğunda işlem başı getiri **+**, dolar toplamı **−**
(ör. `taker ≤ 0,93`: +0,306% ama −5.508 $). Yani **zarar seçimden değil, boyut
ağırlığından** geliyor. Ama boyutun TP1 kanalından geçtiği aynı gün ölçüldü
(bkz. GERİ ÇEKME) → bu da eyleme dönüştürülemez.

#### B KOLU (kaldırılacak kapı) — `golge` doğal deneyi

Gölge botun **reddettiklerini** açıyor; reddedilenler kârlıysa kapı yanlıştır.

```
kaynak            N     ort ret    TOPLAM $   kazanan   gun-t   yorum
pump_long_tezi  461    +2,297%    +2.813,4      %59    +5,40   kapi yanlis OLABILIR
blowoff          13    +5,562%      +210,0      %62    +1,91   N=13, HUKUM YOK
long_veto        40    +0,340%      -337,3      %52    +0,70   belirsiz (ret/dolar celisiyor)
onay_bekle       57    -0,404%    -1.757,0      %46    -0,00   kapi dogru gorunuyor
stop_cok_dar     39    -0,408%      -948,1      %38    -0,66   kapi dogru gorunuyor
btc_pay_freni    20    -0,989%      -756,4      %30    -2,58   kapi dogru gorunuyor
```

⚠️ `pump_long_tezi` bir **kapı değil, gölgenin kendi tezi** — "kapı kaldırma" olarak
okunamaz. ⚠️ N'ler küçük; keşif/doğrulama **bölünemedi** (ön-kayıtta sınır olarak
yazılıydı). Hiçbiri K1+K2+K3'ü geçmedi.

**`skor ≥ 45` LONG kapısı — ön-kayıtlı YÖNLÜ TAHMİN TUTTU:**

```
kapinin ALDIKLARI      N=525  ort +0,686%  TOPLAM -7.512,1 $  kazanan %50  gun-t +1,69
kapinin REDDETTIKLERI  N=219  ort +2,364%  TOPLAM +1.383,6 $  kazanan %59  gun-t +2,95
```

⚠️ Bu **yeni bilgi değil** — aynı gün `skor`un ters çalıştığı ölçülmüştü; burada
farklı bir dilimde ve farklı veriyle **tekrar** görülüyor. Hüküm o kayıttadır.

#### C KOLU (erken çıkış) — **DÜŞTÜ**

Karşı-olgu: koşulu sağlayanlar 30. dakikada kesilseydi ne olurdu?
(birim doğrulandı: izleme `pnl_pct` ile defter `ret` aynı tabanda, eğim 1,195)

```
                        KESIF (N=57)          DOGRULAMA (N=184)
kosul                   kazanc   gun-t        kazanc   gun-t
30dk pnl < 0            -1,473   -0,52        -0,104   -0,54
30dk pnl < -0,5%        -3,106   -0,86        +0,256   +0,03
30dk MAE < -1%          -2,911   -1,31        -0,279   -0,98
30dk artida sure < %50  -3,130   -0,70        +0,134   -0,29
```

Keşifte kesmek **zarar ettiriyor**, doğrulamada **sıfıra yakın**. Hiçbirinde
gün-kümeli t anlamlı değil. **28/28 sicili bozulmadı — 29/29 oldu.**

🔑 **Z1 kontrol katmanı uyarı verdi:** erken çıkış koşulları TP1 alma oranıyla
**güçlü ilişkili** (`30dk pnl<0`: TP1 alanlarda %26, almayanlarda %54 — **27,6 puan**).
Yani bulunacak şey *"kesmek iyi"* değil *"zaten kaybedenleri kesmek iyi"* olurdu —
bugün geri çekilen artefaktın aynı kanalı. Ölçüt zaten geçmedi, ama **geçseydi bile
bu kontrol düşürecekti.**

#### HÜKÜM

**Ön-kayıtlı ölçüm hiçbir kapı değişikliği üretmedi.** A ve C düştü; B'de K1+K2+K3'ü
geçen küme yok. **Bota hiçbir şey önerilmiyor.**

⚠️ Tasarım kusuru (dengesiz keşif penceresi) A kolunun sonucunu **değiştirmedi** —
tüm pencerede de 0/26. Ama C kolunun keşif yarısı (N=57, 4 gün) gerçekten zayıftı;
o kolun "düştü"sü doğrulama yarısına dayanıyor.

#### Ne öğrenildi

Bu ölçüm, giriş seçiciliği aramanın **kapı tarafında da** tükendiğini gösteriyor:
radar/ölçücünün ürettiği hiçbir alan, engellenmesi kârlı olacak bir dilim
işaretlemiyor. Projenin *"bot ne alınmayacağını biliyor, ne alınacağını bilmiyor"*
hükmü artık daha da dar: **ne alınmayacağını da bu alanlardan öğrenemiyor.**

### 🟡 TERSİNE MÜHENDİSLİK — KAZANANLARIN İNCELENMESİ (2026-08-30) · **KEŞİFSEL**

**Tür:** ön-kayıt YOK, kullanıcı isteğiyle betimleyici inceleme. **HÜKÜM DEĞİL.**
**N:** 1.467 pozisyon (6 defter) · kâr geri verme kısmı `testbot` 241 pozisyon.

#### 1 · Kâr YOĞUNLAŞMIYOR — vaka incelemesi değil, istatistik doğru araç

```
en iyi   5 poz: karin  %4'u     en iyi  50 poz: karin %24'u
en iyi  10 poz: karin  %7'u     en iyi 100 poz: karin %41'u
```

Piyango yapısı **yok**. `golge`'nin pump tezindeki *"10 pozisyon her şeyi taşıyor"*
deseni defterlerin geneli için **geçerli değil**.

#### 2 · 🔴 YÜZDE POZİTİF, DOLAR NEGATİF

```
YUZDE bazinda   ort kazanc +6,561%   ort kayip -4,013%   oran 1,63   kazanma %50
DOLAR bazinda   ort kazanc  +84,5$   ort kayip -100,3$   oran 0,84
```

Beş defterin **beşi de** başabaş için gereken kazanç/kayıp oranının **altında**.
İşlem başı yüzde beklentisi açıkça pozitif (+1,27 puan/işlem) ama defterler
kaybediyor. Fark **boyut ağırlığından** geliyor.

⚠️ Bu, aynı gün geri çekilen *"küçük pozisyon kazanır"* bulgusu **değildir**.
O bir **tahmin** iddiasıydı ve TP1 kanalından geçtiği için çürüdü. Bu ise
gerçekleşmiş defterin **aritmetik** bir olgusu: eşit-ağırlıklı ve dolar-ağırlıklı
sonuçlar zıt işaretli. Boyut sonucu **öngörmüyor** ama sonuçla **ilişkili**;
ikisi farklı ifadelerdir ve bu satır kural önerisi taşımaz.

#### 3 · Kazananların %83'ü hedefe VARMADAN kapanıyor

```
KAZANANLAR   STOP  612 (%83)  ort +5,458%   TP2  87 (%12)  ort +14,099%
KAYBEDENLER  STOP  717 (%98)  ort -4,060%
```

İz-süren stopla kapanan kazananlar tepenin **%58'ini** tutuyor; hedefe varanlar
**+%14,10** alıyor. Kazananları kesen şey hedef değil, **iz-süren stop.**

#### 4 · 🔴 ARTIYA GEÇİP GERİ VERME — ŞANSTAN FAZLA

`pnl-tepe-raporu.md` N=17'ydi; artık **N=241**.

```
tepe >= %1 : 167 poz -> %39 KAYBETTI      tepe >= %3 : 108 poz -> %18
tepe >= %2 : 134 poz -> %32               tepe >= %5 :  68 poz -> % 7
```

**Şans tabanı ölçüldü** — driftsiz rastgele yürüyüş, pozisyonun **kendi ATR'si,
kendi süresi, kendi stopu ve 2×ATR iz-süren stopu** ile (mekanik birebir aynı,
tek fark fiyatın rastgele olması):

```
esik        GERCEK   RASTGELE+STOP    fark
tepe>=%1      %39         %19       +20,3 puan
tepe>=%2      %32         %12       +20,0
tepe>=%3      %18          %7       +10,3
tepe>=%5       %7          %8        -0,3   <- SANSLA AYNI
```

🔑 **Küçük kâra geçen pozisyonlar şansın 2-3 katı oranında geri dönüyor.
%5'i aşanlar ise tam olarak şans gibi davranıyor.** Etki mekanik kontrolünü geçti:
simülasyona gerçek stop ve iz-süren stop eklendiğinde fark **kapanmadı**.

⚠️ **MODEL RİSKİ — hükmü bu yüzden yazmıyorum:** boş hipotez Gauss rastgele
yürüyüş. Kripto kısa ufukta **ortalamaya dönüyor** ve pompalanmış altlarda bu
belgelenmiş bir olgu. *"Rastgele yürüyüşten kötü"*, **piyasanın özelliği** olabilir,
botun kusuru değil. Doğru boş hipotez (aynı evrende eşleştirilmiş rastgele giriş
zamanları) kurulmadan bu bir bulgu değil, bir **adaydır**.

#### Nereye işaret ediyor

Dört bulgunun dördü de **giriş seçiciliğine değil, ÇIKIŞ/KÂR ALMA seviyesine**
bakıyor: yüzde kenarı var ama dolara dönüşmüyor · kazananlar hedefe varmadan
kesiliyor · küçük kârlar şanstan fazla geri veriliyor · büyük kârlar normal.

⚠️ Bunun doğal önerisi *"daha erken kâr al"* olur ve bu bir **çıkış
sıkılaştırmasıdır** — bu projede sıkılaştıran **29 varyantın 29'u da kalmıştır**
(bugün 28→29 oldu). Öneriye dönüşmeden önce kendi ön-kaydı ve **doğru boş
hipotezi** gerekir.

**Kural önerilmiyor. Bota dokunulmadı.**

### ❌ "ARTIYA GEÇİP GERİ VERME" — **DÜŞTÜ**: botun kusuru değil (2026-08-30)

**Ön-kayıt:** `ON_KAYIT_geri_verme.md`, commit `17cfdec` — koşumdan **önce**.
**Betik:** `scratchpad/geri_verme.py`
**Boş hipotez:** aynı sembol · aynı dönem (±3 gün) · aynı yön · **rastgele giriş anı** ·
**birebir aynı mekanik**. Değişen tek şey giriş anı = botun sinyali.
**N:** gerçek **458** · kontrol **7.980** (pozisyon başına ~17,4)

```
esik        GERCEK    KONTROL     fark
tepe>=%1     55,9%     52,0%     +3,9 puan
tepe>=%2     46,4%     41,2%     +5,1
tepe>=%3     35,0%     28,4%     +6,6
tepe>=%5     22,8%     14,9%     +7,9
```

| ölçüt | eşik | sonuç |
|---|---|---|
| N1 · fark(2%) | ≥+5,0 **ve** t ≥ +2,5 | ❌ fark **+5,1** ✓ ama **t = +1,37** ✗ |
| N2 · gradyan | azalmalı, \|fark(5)\|≤5 | ❌ **ARTIYOR** (+3,9 → +7,9) |
| N3 · yön tutarlılığı | ikisi aynı işaret | ✅ LONG +4,5 · SHORT +7,7 |
| N4 · süre eşitliği | 1,5 kat içinde | ❌ gerçek 4,0 sa · kontrol 6,0 sa (oran 0,67) |

**HÜKÜM: DÜŞTÜ.**

#### 🔴 GAUSS BOŞ HİPOTEZİ ETKİYİ DÖRT KAT ABARTMIŞ

```
Gauss rastgele yuruyus (onceki)    +20,3 / +20,0 / +10,3 / -0,3 puan
Eslestirilmis GERCEK fiyat (bu)     +3,9 /  +5,1 /  +6,6 / +7,9 puan
```

Aynı gün *"model riski"* diye yazılan çekince **haklı çıktı**: geri vermenin
büyük kısmı **piyasanın kendi ortalamaya dönüşü**, botun kusuru değil.

#### 🔴 ÖN-KAYITLI YÖNLÜ TAHMİN YANLIŞ ÇIKTI — aynen yazılıyor

*"fark(5%) sıfıra yakın kalacak, etki varsa yalnız küçük kârlarda"* demiştim.
**Tersi çıktı:** fark eşikle **büyüyor**, en büyüğü %5'te (+7,9). Yani kalan cılız
etki küçük kârlarda değil, **büyük tepelerde**. Bu, *"küçük kârı erken al"*
yorumunun dayanağını **ortadan kaldırır** — bulgu olsaydı bile öneri o olmazdı.

#### Sınırlar — hükmü zayıflatanlar da aynen

- 🔴 **Gerçek pozisyonların yalnız %31'i yeniden üretilebildi** (458/1.467).
  762'si asgari %2 stop kuralında elendi: canlı ölçücü **canlı fiyatla**,
  yeniden üretim **kapanmış barla** çalışıyor → stoplar birebir tutmuyor.
- 🔴 **Kontrol kolu seçilmiş:** 16.040 rastgele çekiliş asgari-stop kuralında
  elendi. Yani kontrol *"herhangi bir an"* değil, *"stopu yeterince geniş çıkan an"*.
- ⚠️ N4 düştü: gerçek 4,0 sa tutuyor, kontrol 6,0 sa. Gerçek **daha kısa tuttuğu
  hâlde daha çok geri veriyor** — bu farkı zayıflatmaz, ama kollar eşit değil.
- 21 gün, tek pencere.

#### Ne kaldı

**Hiçbir şey.** *"Bot artıya geçip geri veriyor"* gözlemi, doğru boş hipoteze karşı
**anlamlı değil**. Çıkış/kâr-alma tarafında da eyleme dönüşebilir bir bulgu yok.

Bu, aynı gün üretilen adayın **kendi ön-kaydıyla sınanıp ölmesidir** — kural
yazılmadan önce. Sistem tam da bunun için kuruldu.

#### EK — ÜST SINIRIN KENDİ SINIRI (aynı gün, kullanıcı itirazı üzerine)

Kullanıcı: *"Yani işimize yaramaz mı demek istiyorsun?"* — modellediğim dedektör
yalnız **engelliyordu**; gerçek bir sinyal **yön çevirebilir** de. Üç senaryo
koşuldu.

⚠️ Defter bu arada yine büyüdü: testbot 290 → **296 poz**, −4.903 → **−5.049**.

```
TESTBOT   gercek -5048,98  (296 poz)
  1) TERS olanlar HIC ACILMASAYDI      -4478,18    kurtardigi  +570,80
  2) TERS olanlar YATAY gibi olsaydi   -6652,20    DAHA KOTU
  3) HER poz BTC'nin YANINDA olsaydi   +1795,59    fark     +6844,57

DEFTER2   gercek  -987,39  (189 poz)
  1)  -481,45   ·   2) -1677,75   ·   3) +7665,38
```

#### 🔴 SENARYO 3 KULLANILMIYOR — KÂHİNLİKTİR

`+6.844`'lük sıçrama gerçek görünüyor ve **geçersizdir.** *"BTC'nin yanında
olmak"* ancak pozisyon **kapandıktan sonra** bilinir; `AYNI` kovası **sonuca
göre tanımlıdır.** Onun gözlenen ortalamasını (`+6,07 $/poz`) 296 pozisyona
uygulamak, geleceği bilmeyi varsaymaktır — sinyal değil, kâhinlik.

Bu, `CLAUDE.md`'nin *"KARIŞTIRICI KONTROLÜ ZORUNLU"* ve *"en iyi hücre
seçilmez"* kurallarının doğrudan kapsamındadır. **Sayı üretildi ve
kullanılmadı.** Uygulanabilir şekildeki tek sınır **senaryo 1: +570,80 = %11,6.**

#### 🔑 SENARYO 2 — TERS EN KÖTÜ KOVA DEĞİL

```
TERS  ortalama   -7,61 $/poz
YATAY ortalama  -28,98 $/poz   <- EN KOTU KOVA BU
AYNI  ortalama   +6,07 $/poz
```

TERS pozisyonlar YATAY gibi davransaydı defter **daha kötü** olurdu (−6.652).
Yani *"BTC'ye ters düşmek"* kaybın kaynağı değil; kayıp **BTC hiçbir şey
yapmazken**, altcoin'in kendi hareketinde oluşuyor. Bu, ana bulguyu
zayıflatmıyor — **güçlendiriyor.**

#### ⚠️ ÖNERİLMEYEN İKİNCİ KULLANIM — bilerek önerilmedi

Skew aslında **yön** değil **oynaklık/kuyruk riski** ölçer. Projenin kendi
bulgusu *"yön çıkmıyor, oynaklık 198/198 çıkıyor"*, ve bağlayıcı kısıt olan
ödeme oranı da stop/hedef mesafesi meselesi. Yani skew'in **başka** bir
kullanımı teorik olarak tutarlıdır.

🔴 **Buna rağmen önerilmiyor.** Bir fikrin ödülü ölçülüp küçük bulunduktan
hemen sonra aynı veri için ikinci gerekçe üretmek, **gerekçeyi sonuca
uydurmaktır.** O yol denenecekse ayrı soru, ayrı ön-kayıt, ve **ödül önce
ölçülür.** Bu paragraf, ileride birinin *"ama skew oynaklık için denenmemişti"*
demesi için değil, **denenirse hangi disiplinle deneneceği** için duruyor.

**Betik:** `scratchpad/odul_ustsinir2.py`

---

## OLAY KUYRUĞU — "haber gelince poz al" akışı kurulabilir mi? (2026-09-01)

**Ön-kayıt:** `ON_KAYIT_olay_kuyrugu.md` (commit `dd5b94d`, **koşumdan önce**)
**Betikler:** `scratchpad/olay_listesi.py` · `scratchpad/olay_kuyrugu.py` ·
`scratchpad/olay_kacan_dagilim.py`
**Hüküm:** 🔴 **BİRİNCİL HÜCRE DÜŞTÜ** — ama gerekçesi ön-kayıtta beklenen gerekçe değil.

### Soru

Kullanıcının Grok/X ajentik önerisinin üç kolundan **geriye test edilebilen tek kolu.**
*"AVAX'la ilgili haber gelince sana bildirir, sen analiz edip poz almamı sağlarsın"*
akışı için zorunlu koşul: `Grok → bildirim → analiz → karar` gecikmesinden **sonra**
hâlâ maliyeti aşan kenar kalmalı.

### Veri

Binance resmî duyuru arşivi (public CMS ucu, anahtarsız) — **962 duyuru**,
2024-08-12…2026-09-01, `releaseDate` **dakika kesinliğinde** → `t=0` yorum payı yok.
Fiyat: `fapi` 5dk mum, olay penceresi başına, `scratchpad/olay_pencere/` (YENİ dizin;
mevcut arşivler okunmadı da yazılmadı da).

| tip | aday | ölçülen | düşme sebebi |
|---|---|---|---|
| `perp_listeleme` | 260 | **0** | 232'si *olay öncesi bar yok* — **yapısal** |
| `delisting` | 135 | 84 | 51 mum yok |
| `launchpool` | 87 | 36 | 24 mum yok · 27 olay öncesi bar yok |
| `spot_listeleme` | 52 | 31 | 6 mum yok · 15 olay öncesi bar yok |

🔑 **`perp_listeleme` yapısı gereği ölçülemez:** bir perp kendi listelenmesinden
**önce var olmaz**, dolayısıyla olay öncesi fiyatı da yoktur. 260 adayın 0'ı ölçüldü.
Bu bir eksiklik değil, **sonuçtur** — bu olay tipi tanım gereği kovalanamaz.

### 🔴 ASIL BULGU — kenar testi değil, KAÇAN HAREKET

Birincil hücre (olumlu duyuru havuzu · 30 dk gecikme · 4 sa ufuk) düştü:
ham kenar **−0,404 %**, şans tabanına eşli fark **−0,324 %** (gün-t −0,20, 57 gün).
**Ama bu testin gücü yok** (aşağı bak). Hükmü taşıyan sayı bu değil, `kaçan`:

```
olumlu duyuru — duyuru anindan girise kadar KACAN hareket
gecikme     ortalama   MEDYAN     %25      %75    >%2 pay
 5 dk       +15,54%   + 6,49%   +0,91%  +22,22%     72%
15 dk       +18,72%   + 7,85%   +1,06%  +24,41%     72%
30 dk       +18,52%   + 9,12%   +0,17%  +27,52%     67%
60 dk       +20,35%   +10,70%   +0,16%  +28,42%     67%
```

**Hareket ilk 5 dakikada bitmiş durumda.** 5→60 dakika arası artış (+15,5 → +20,4)
ilk sıçramanın yanında küçük. Uç değer değil: **medyan** olay bile 5 dakikada
**+%6,5** kaçırmış, olayların **%72'si** +%2'yi aşmış. En büyük 5 olay çıkarılınca
30 dk ortalaması **+%10,33**, medyan **+%8,51** — sonuç ayakta.

`spot_listeleme` daha da keskin (5 dk medyan **+%7,78**, olayların **%81'i** >%2).
`launchpool` en uç-değer bağımlısı (en büyük 5 çıkarılınca 30 dk medyanı
+%4,02 → **+%1,18**'e iner).

⚠️ `delisting` dağılım tablosunda N=168, ölçüm tablosunda 84 — dağılım betiği yalnız
olay öncesi bar arar, ölçüm ayrıca ≥5 geçerli şans çekilişi ister. Aynı sayı değil.

### 🔴 GÜÇ DENETİMİ — "DÜŞTÜ" burada "ETKİ YOK" DEMİYOR

Ön-kayıt bunu **zorunlu** kılmıştı (`chg24 >40 LONG` dersi):

```
asgari saptanabilir etki (t=2) : %3,287
kabul bari                      : %0,57
```

Örneklem, **barın altı katı** büyüklükte gerçek bir etkiyi bile göremez.
Yani ileri-getiri testinin hükmü **"kovalanabilir kenar yok" değil, "göremiyoruz".**
Bu ayrım yazılmasaydı bulgu abartılırdı.

**Ama akış hakkındaki hüküm bu testten gelmiyor** — `kaçan`'dan geliyor ve o
büyüklük hem ortalamada hem medyanda hem uç değersiz hâlde ayakta.

### ⚠️ MEKANİK EŞİTLİĞİ DÜŞTÜ — kıyas zayıf

`CLAUDE.md` 2026-08-20 kuralı gereği raporlanır:

| grup | gerçek \|ort\| | şans \|ort\| |
|---|---|---|
| `olumlu_duyuru` | %8,33 | %4,02 |
| `delisting` | %13,08 | %2,91 |

Olay kolu şans kolundan **2-4,5 kat** oynak. Eşli fark testinin güveni bu yüzden
zayıf; MDE'nin büyüklüğünün de kaynağı bu. Kayda geçiyor.

### Sızıntı

`launchpool` +0,551 % (olay-t +0,75) · `spot_listeleme` +0,061 % · `delisting`
−0,115 %. Yani `t=0` **görece temiz** — hareket duyurudan **önce** değil, duyuruyla
başlıyor. Bu, kaçan-hareket bulgusunu güçlendirir: kaçırdığımız şey sızıntı değil,
**kendi gecikmemiz.**

### Ön-kayıtlı yönlü tahminlerin karnesi

| # | tahmin | sonuç |
|---|---|---|
| 1 | `kaçan` D ile artacak, sıçrama ilk 15 dk'da | ✅ **TUTTU** |
| 2 | `delisting` kuyruğu listelemeden uzun | ⚠️ **KISMİ** — ham kenar öyle (+2,07 vs −0,40) ama şans tabanına karşı ikisi de sıfır (t −0,3 / −0,2) |
| 3 | `H=24sa` kenarı `H=4sa`'ten büyük olacak | ❌ **YANLIŞ** — 24 saat tutarlı biçimde **negatif** (havuzda her gecikmede, t≈−2,2) |

Tahmin 3 sadece yanlış değil, **ters** çıktı: duyuru sonrası geç girip 24 saat tutmak
şans tabanının **altında**. (Betimleyici ızgarada, hüküm taşımaz — ama yön tutarlı.)

### Ne öğrendik

1. **Duyuru kovalama akışı insan hızında kurulamaz.** Hareket 5 dakikada bitiyor;
   `Grok → bildirim → analiz → karar` zinciri bunun altına inemez.
2. **`perp_listeleme` tanım gereği kovalanamaz** — 260 aday, ölçülebilir 0.
3. Bir kenar **var mı yok mu bilinmiyor** — örneklem onu görecek güçte değil.
   Bu soru kapanmadı, **cevaplanamadı.**
4. Plandaki üç sonuçtan **🟡**: kuyruk var ama insan-döngüsü için çok kısa.
   Aşama 2 (Grok alt botları) bu hâliyle **kurulmaz**; kurulacaksa gerekçesi
   "haber kovalama" olamaz.

### Tuzak — kayda geçti

`olay_listesi.py` bir kez **heredoc** ile yazıldı; düzenli ifadedeki `\b` sınır imi
gerçek **BACKSPACE (0x08)** karakterine döndü, kural hiç eşleşmedi, **134 duyuru**
yanlış sınıflandı. **`py_compile` DE `pyflakes` DE temiz geçti** — ikisi de düzenli
ifadenin *anlamına* bakmaz. Aynı sınıf: `radar.HERE` · `ayna.time`.
Çözüm araç oldu: `kural_sinamasi()` her koşumda 9 bilinen başlığı sınar, kalıplarda
kontrol karakteri arar, ve düşerse betik **çalışmayı reddeder**.

---

## X DUYGUSU — KONTROL GÜNLERİYLE ÖLÇÜLDÜ: yön bilgisi YOK (2026-09-01)

**Betikler:** `scratchpad/x_gun_cek.py` · `x_kontrol_coz.py` · `x_mock_denetim.py`
**Hüküm:** 🔴 **KESİN OLUMSUZ** — duygu sayımı yön taşımıyor.

19 Ağustos tek başına yorumlanamıyordu (`olcumler.md` → *X GÖNDERİLERİ*): boğa payı
%84 çıkmıştı ama kripto X yapısal olarak boğa olduğu için bunun **normal mi sinyal mi**
olduğu bilinmiyordu. Kontrol günleri **çekimden önce** kurala göre seçildi.

| gün | BTC 13→23 | boğa payı |
|---|---|---|
| **2026-08-19 (hedef)** | **+%7,1** | **%84** |
| 2026-07-08 (yatay) | −%0,1 | %83 |
| 2026-07-29 (düşüş) | −%1,5 | %81 |
| 2026-02-05 (sert düşüş) | **−%10,0** | **%77** |

```
hedef   boga 145 · ayi 27   -> %84
kontrol boga 361 · ayi 87   -> %81      iki oran farki z = +1,07
hedef (+%7,1) vs sert dusus (-%10,0)    z = +1,59
```

**BTC'de 17 puanlık bir salınım, boğa payında 7 puan oynatıyor ve bu istatistiksel
olarak ayırt edilemiyor.** Kripto X, fiyat ne yaparsa yapsın ~%80 boğa konuşuyor.
`%90 boğa` bir sinyal değil, o ortamın **normali**.

⚠️ **Sınır:** sert düşüş günü hedeften 195 gün uzak (±6 haftada −%4'ten sert gün
YOKTU) — rejim farklı. Yakın kontroller yalnız −%0,1 ve −%1,5'ti.

### 🔑 TUZAK — ÜCRETLİ AKTÖR SAHTE KAYIT DÖNDÜRÜYOR

Apify aktörü sonuç bulamayınca `type="mock_tweet"`, `id=-1` **yer tutucu** döndürüyor
(ve yine ücret alıyor). Metni gerçek gönderi sanılırsa sayıma girer ve sonucu kirletir.
Bir pencerede 15 tanesi çıktı. `x_mock_denetim.py` bütün dosyaları tarar.
**19 Ağustos verisi temiz çıktı — önceki rakamlar ayakta.**
Yakalayan şey damga denetimiydi; onsuz sessizce geçerdi.

---

## MAKRO KUYRUK — takvimli makro olayda kovalanabilir kenar YOK (2026-09-01)

**Ön-kayıt:** `ON_KAYIT_makro_kuyruk.md` (commit `df8eb1e`, **koşumdan önce**)
**Betikler:** `scratchpad/makro_olaylar.py` · `makro_kuyruk.py`
**Hüküm:** 🔴 **DÜŞTÜ — ve bu kez örneklem YETERLİ.**

19 Ağustos anekdotunu sınanabilir hâle getirme denemesi. 33 olay (16 FOMC kararı +
17 FOMC tutanağı), hepsi 14:00 ET, kaynak `federalreserve.gov`; 2026 tarihleri
projedeki `makro_takvim.json` ile **birebir** uyuştu. Yaz/kış saati elde hesaplandı
ve iki bilinen noktada **sınandı** (düşerse betik koşmaz).

### Olaylar gerçekten oynatıyor — özne var

| grup | N | olay \|ilk 5dk\| | şans \|ilk 5dk\| | oran |
|---|---|---|---|---|
| havuz | 33 | %0,338 | %0,116 | **2,91×** |
| `fomc_karar` | 16 | %0,488 | %0,124 | **3,95×** |
| `fomc_tutanak` | 17 | %0,196 | %0,109 | 1,81× |

### Ama devamı yok — hiçbir gecikmede

Birincil hücre (havuz · D=30 dk · H=4 sa): ham kenar **−0,062 %**, şans tabanına
eşli fark **+0,059 %** (olay-t **+0,31**). K1 ve K2 **ikisi de düştü**.

🔑 **Ve önemli olan şu: kenar `D=5` dakikada da yok.** Izgaranın tamamı sıfır
civarında geziniyor. Yani bu bir **gecikme sorunu değil** — devam hareketi hiç yok.
Borsa duyurusunda hareket 5 dakikada *bitiyordu*; burada hareket oluyor ama
**yönlü devamı hiç başlamıyor.** İki farklı başarısızlık biçimi.

### 🔑 GÜÇ DENETİMİ — bu kez "GÖREMİYORUZ" DEĞİL

```
asgari saptanabilir etki (t=2): %0,377   ·   kabul bari: %0,57
-> MDE bar'in ALTINDA. Orneklem bari saptayacak guctedir. DUSTU ANLAMLIDIR.
```

Listeleme ölçümünün aksine (MDE %3,29, bar %0,57 → "göremiyoruz"), burada hüküm
gerçek bir olumsuzluk. Aynı ön-kayıt maddesi bir ölçümü kurtardı, diğerini mahkûm etti.

### Anekdotun günü örneklemin İÇİNDE

`2026-08-19` bu 33'ten biri (tutanak günü). Kendi çerçevesinde: ilk 5 dk **−0,168 %**
→ yön SHORT, birincil hücre **−1,251 %**. Yani anekdot kendi yöntemiyle ölçüldüğünde
**kaybediyor**.

🔴 **Ama bu, anekdotu çürütmez — çünkü aynı şeyi ölçmüyor.** O günün asıl hareketi
**14:00-15:00 UTC** arasında Hazine geri-alım haberiyle oldu; FOMC tutanağı
**18:00 UTC**. Bu ölçüm o gün için **tutanağı** ölçüyor, Hazine haberini değil.
İkisinin aynı güne düşmesi anekdotun **karıştırıcısıydı** — N=1'in neden
yetmediğinin somut örneği.

### Ölçümün asıl sınırı — ön-kayıtta yazılıydı

CPI/PPI/NFP alınamadı (`bls.gov` HTTP 403; tarih **uydurulmaz**). Hazine geri-alım
duyurularının geçmiş damgaları da doğrulanabilir biçimde alınamadı.
🔴 **Yani düşen şey *"makro haber kovalanmaz"* değil, *"TAKVİMLİ makro olay
kovalanmaz"*.** FOMC takvimlidir ve piyasa önceden pozisyon alır; 19 Ağustos'un
Hazine haberi **sürprizdi.** Sürpriz makro haber **hâlâ ölçülmedi.**

### Ön-kayıtlı yönlü tahminlerin karnesi

| # | tahmin | sonuç |
|---|---|---|
| 1 | ilk 5 dk hareketi rastgeleden belirgin büyük | ✅ **TUTTU** (2,91×) |
| 2 | `fomc_karar` ilk tepkisi `fomc_tutanak`tan büyük | ✅ **TUTTU** (2,5 kat) |
| 3 | kuyruk `D` ile hızla tükenecek, `D=120`'de sıfır | ⚠️ **KISMİ** — sıfır, ama `D=5`'te de sıfır; tükenmedi, hiç var olmadı |

### Mekanik eşitliği

Gerçek kol şans kolundan **1,40×** oynak (listeleme ölçümünde 2-4,5× idi). Daha iyi
ama tam eşit değil; kayda geçiyor.

---

## BOĞA'da LONG — HAM getiri: yön mü yanlış, mekanik mi? (2026-09-04)

**Ön-kayıt:** `ON_KAYIT_boga_long_ham.md` (commit `59b7a67`, **koşumdan önce**)
**Betikler:** `scratchpad/boga_long_ham.py` · `boga_long_ham_gun.py`
**Hüküm:** 🔴 **K1 GEÇTİ — yön yanlış.** Ama asıl bulgu ön-kayıtta beklenen değil.

### Soru

Bot BOĞA'da LONG'a kilitli (ölçüldü: 12.594 satırda SHORT adayı **sıfır**) ve
kaybın ~%70'ini orada üretiyor. Karne iki açıklamayı ayıramıyordu: **yön mü
yanlış**, yoksa **stop mu öldürüyor** (%95 stop, 2,2 saat medyan ömür)?
Bu popülasyonda ham getiri **hiç ölçülmemişti**.

### Kurulum

Aday arşivi 08-04…09-04 · BOĞA satırı **13.399** · 224 sembol · 223'ünde mum bulundu.
Birim **sembol-gün** (satır 7,5 dakikada bir yazılıyor → satır saymak sahte N).
Mekanik **yok**: stop yok, hedef yok, maliyet yok.

✅ **Zaman dilimi sınaması geçti:** `price` alanı eşlenen barın aralığında —
**%99,7** (13.176 / 38). Kaydırma (UTC+3 → UTC) doğru.
✅ **Oynaklık eşitliği:** KAPI/TABAN = **1,14×** → eşit sayılır, K2 zayıflamaz.

### Birincil hücre (KAPI · H=4 saat)

```
KAPI   ort -0,649%   sembol-gun 246   sg-t -2,06   MDE 0,630
TABAN  ort -0,816%   sembol-gun 627   sg-t -4,67
KAPI - TABAN  +0,167%   iki-orneklemli t +0,46
```

| ölçüt | sonuç |
|---|---|
| **K1** ort < 0 ve t ≤ −2,0 | ✅ **GEÇTİ** (−0,649 / −2,06) — kıl payı |
| **K2** kapı anti-seçici mi | ❌ **DÜŞTÜ** (+0,167 / +0,46) |

### 🔑 ASIL BULGU — kapı suçlu değil, EVRENİN TAMAMI DÜŞÜYOR

`TABAN` = BOĞA'da taranan **her şey**, kapı süzgeci olmadan: **−0,816%**,
gün-t **−4,94**. Kapı kolundan **daha güçlü** negatif.

**Yani bot kötü seçmiyor — bu pencerede alt paraların tamamı düşüyordu.**
Kapıyı daraltmak bunu çözmez; kapı zaten tabandan (anlamsız da olsa) **iyi**.

### Gün-kümeli denetim — ön-kayıtta yoktu, eklendi

Sembol-günler aynı gün içinde bağımsız değil (düşüş gününde bütün altlar
birlikte düşer). Gün düzeyinde toplandı:

| kol | H | sembol-gün t | **gün-t** |
|---|---|---|---|
| KAPI | 4 sa | −2,06 | **−2,22** |
| TABAN | 4 sa | −4,67 | **−4,94** |

Daha sıkı kümelemede hüküm **zayıflamadı, güçlendi**. 13 günün **10'u eksi (%77)**.

⚠️ **Ama kırılganlık gerçek:** en kötü günler çıkarılınca KAPI kolu erir —
1 gün: t=−1,86 · 2 gün: −1,43 · 3 gün: −0,96. `TABAN` kolu bu erimeyi yaşamıyor.
**Sağlam olan taban bulgusu, kapı bulgusu değil.**

### Ufuk eğrisi — kayıp süreyle büyüyor

```
KAPI    1sa -0,084   4sa -0,649   12sa -1,399   24sa -1,881
TABAN   1sa -0,252   4sa -0,816   12sa -1,249   24sa -1,558
```

Tek yönlü ve monoton → gürültü değil, **süregelen aşağı sürüklenme**.

### Ön-kayıtlı yönlü tahminlerin karnesi — 3'te 1

| # | tahmin | sonuç |
|---|---|---|
| 1 | TABAN hafif **ARTI** (BTC pencerede ~%12 yükseldi) | ❌ **YANLIŞ** — −0,816%, gün-t −4,94 |
| 2 | KAPI − TABAN **negatif** (momentum tepeden alır) | ❌ **YANLIŞ** — +0,167, t +0,46 |
| 3 | 24 saatte kayıp 4 saatten büyük | ✅ **TUTTU** |

🔑 **1. tahminin yanlış çıkışı bulgunun kendisi:** BTC yükselirken altlar
düşüyordu. Bot BTC-hâkimiyeti artan bir fazda alt para **satın alıyordu**.

### İkincil (betimleyici, hüküm taşımaz)

`taker ≤ 1,0` → −0,632% · `taker > 1,0` → −0,898%. **İkisi de negatif.**
SHORT istisnasını kesen şart, kazananı kaybedenden **ayırmıyor**; sadece
biraz daha az kötü olan tarafı geçiriyor.

`BASLIYOR + smart=SHORT` alt kümesi: 35 satır ama **2 sembol-gün, tek sembol
(AKE)**. Ham LONG +0,126% → SHORT tarafı −0,126%. **N=2, hiçbir şey söylemez.**

### 🔴 SINIRLAR — bulgudan büyük

1. **13 gün, TEK rejim epizodu** (08-21…09-04) — ve tam olarak botun kaybettiği
   pencere. *"Kaybı kayıp dönemiyle açıklama"* riski gerçek. Sonraki BOĞA
   epizodunda ne olacağını **söylemez**.
2. **Bu Aşama 1.** Ham kenar +0,85% (taban, ters yön) kulağa iyi geliyor ama
   `CLAUDE.md` kaydı duruyor: A-stop, A+B'nin ham kenarının **%65'ini** yemişti.
   Mekanik aşaması yapılmadan hiçbir kural çıkmaz.
3. **K1 kıl payı geçti** ve en kötü 3 gün çıkınca kayboluyor.

---

## NOTR'da SHORT — HAM getiri + İKİ REJİMİN BİRLEŞTİRİLMESİ (2026-09-04)

**Ön-kayıt:** `ON_KAYIT_notr_short_ham.md` (commit `107b2e4`, **koşumdan önce**)
**Betikler:** `scratchpad/notr_short_ham.py` · `rejim_yon_karne.py`
**Hüküm:** 🔴 **Birincil DÜŞTÜ ama GÜÇSÜZ** — ve asıl bulgu birincilde değil.

### Kullanıcı itirazı — doğrulandı, eksiklik bendeydi

*"11-19 Ağustos NOTR-AYI rejimiydi, iki rejim var; NOTR-SHORT'ta bot artıda
kalıyordu."* Canlı defterden sınandı:

- Pencere gerçekten **iki rejim**: `NOTR` (08-01…08-21) · `BOGA` (08-21…).
  Önceki ham ölçüm **yalnız BOGA'ya** bakmıştı.
- `NOTR-SHORT`: ortalama getiri **+%1,67**, poz-t **+2,61** → iddia **DOĞRU**.
- Dolar eksi (−1.125) ama kırılım suçluyu gösteriyor:
  `A+B+MA50` +599 · `A+B` +190 · `NOTR` +10 · **`MA50+ucuz` −1.924**.
  **`MA50+ucuz` çıkarılınca NOTR-SHORT = +798 $ / 35 pozisyon.**

### Birincil hücre (A+B · SHORT · H=4 saat)

```
A+B    ort +0,199%  sembol-gun 77  sg-t +0,21  gun-t -0,13  MDE 1,883
TABAN  ort +0,592%  sembol-gun 789 sg-t +3,22  gun-t +1,51
A+B - TABAN  -0,394%   t -0,41
```

K1 ❌ · K2 ❌ → **DÜŞTÜ.** Ama `|ort| < MDE` → **"göremiyoruz"**, "etki yok" değil.

### 🔑 BİRİNCİL HORİZON YANLIŞ SEÇİLMİŞTİ — A+B 12-24 saatte çalışıyor

Ufuk eğrisi (A+B, SHORT):

```
 1 sa +0,030 (t+0,09)   ·   4 sa +0,199 (t+0,21)
12 sa +2,254 (sg-t+1,98 · gun-t+1,95)   ·   24 sa +3,315 (sg-t+2,63 · gun-t+2,49)
```

Ve bu **canlı veriyle birebir tutuyor**: A+B'nin canlı medyan tutma süresi
**10,9 saat** (bütün kapıların en uzunu) ve canlı ortalama getirisi **+%2,514** —
ham 12 saatlik değer **+2,254** ile neredeyse aynı.

⚠️ **Bu POST-HOC bir gözlemdir.** Ön-kayıtlı hücre 4 saatti ve düştü; hükmü
değiştirmiyorum. Ama *"A+B'nin ufku 12-24 saat"* hipotezi **kendi ön-kaydını
hak ediyor** — 45 hücrelik ızgaradan seçilmiş bir hücre değil, canlı tutma
süresinden bağımsız olarak **öngörülebilirdi**.

### ⚠️ MA50 KOLU POZİTİF ÇIKTI — dört önceki ölçümle ÇELİŞİYOR

```
MA50 (NOTR, SHORT):  1sa +0,714 (t+2,59) · 4sa +1,675 (sg-t+3,53 · gun-t+3,19)
                    12sa +2,047 (t+2,64) · 24sa +0,012
```

Önceki dört ölçüm bu kapıyı **negatif** bulmuştu (en güçlüsü: 2 yıl, 21.830 olay,
−0,079, t=−4,05). **Çelişki kaydediliyor, çözülmüyor.** Ağırlık kıyası:

| | bu ölçüm | 2 yıllık ölçüm |
|---|---|---|
| pencere | **11 gün** | **2 yıl** |
| rejim | yalnız NOTR | üç rejim |
| mekanik | yok (ham) | var |

**2 yıllık ölçüm baskın kabul edilir.** Bu sonuç onu çürütmez; *"kapının ham
sinyali bu dar pencerede pozitifti"* der.

### 🔴🔴 ASIL BULGU — İKİ REJİM, TEK PİYASA

İki ölçüm yan yana konunca (her ikisi de `TABAN` = süzgeçsiz taranan evren):

| rejim | taban, LONG yönünde, H=4sa | gün-t |
|---|---|---|
| `NOTR` | **−0,592%** (SHORT +0,592 ölçüldü) | +1,51 (SHORT lehine) |
| `BOGA` | **−0,816%** | −4,94 |

**Alt para evreni İKİ REJİMDE DE aşağı sürükleniyordu.** Rejim etiketi botun
**yönünü** değiştirdi, piyasa değişmedi. Bot NOTR'da SHORT'tu (doğru yön),
BOĞA'ya dönünce LONG'a geçti (yanlış yön) — ve kaybın %70'i orada oluştu.

🔑 Bu, kapı tartışmasından **daha temel**: mesele hangi kapının seçtiği değil,
**rejim etiketinin yönü çevirmesi**. Ve `durum.md`'de kayıtlı: etiket geç ve
yapışkan (BOĞA'dan çıkmak için BTC'nin −%6,2 düşmesi **ve 3 gün** sürmesi gerek).

### 🔴 İKİNCİ ASIL BULGU — HER KAPI YÜZDE ARTI, DOLAR EKSİ

| kesit | ort getiri % | net $ |
|---|---|---|
| SHORT (tümü) | **+1,517%** (t +2,43) | −1.815 |
| LONG (tümü) | **+0,774%** (t +1,39) | −3.861 |
| `MA50+ucuz` (NOTR-SHORT) | **+1,098%** | −1.924 |

**Botun seçimi ortalama pozitif getiriyor; parayı kaybettiren BOYUTLANDIRMA.**
Kazananlar küçük, kaybedenler büyük açılıyor.

⚠️ **Yeni değil ve hâlâ eyleme dönüşmedi:** kayıtlı bulgu (`b386738`) bunu
bulmuş ama **boyutun TP1 kanalından geçtiğini** (döngüsel) tespit edip
eyleme dönüştürememişti. Bu ölçüm o bulguyu **üçüncü kez** ve iki ayrı
rejimde doğruluyor.

### Ön-kayıtlı yönlü tahminlerin karnesi — 3'te 0

| # | tahmin | sonuç |
|---|---|---|
| 1 | TABAN SHORT yönünde ~0 veya hafif eksi | ❌ **YANLIŞ** — +0,592%, sg-t +3,22 |
| 2 | MA50 kolu eksi ya da sıfır | ❌ **YANLIŞ** — +1,675%, gün-t +3,19 |
| 3 | A+B ham kenarı canlı yüzdesinden büyük | ❌ **YANLIŞ** (birincil ufukta): ham 4sa +0,199 < canlı +2,514. 12 saatte eşitleniyor |

**Üçünde üçü de yanlış.** Aynen yazılıyor.

### Sınırlar

- 30 günlük tek pencere; `MA50` kolu yalnız **11 gün**, `A+B` **18 gün**.
- Ham ölçüm **fonlamayı içermiyor**; A+B tanımı gereği negatif fonlama seçer →
  ham kenarı gerçeğinden **yüksek** gösterir. Kayıtlı ölçüm: fonlama A+B'nin
  kenarının **%83'ünü** yemişti.
- `A+B` kolunda en büyük sembolün payı %7,8 (PROM) — yoğunlaşma sınırda.

---

## BOYUTLANDIRMA — ön-kayıt GEÇTİ, ama YORUMU KISMEN GERİ ÇEKİYORUM (2026-09-04)

**Ön-kayıt:** `ON_KAYIT_boyutlandirma.md` (commit `161271f`, **koşumdan önce**)
**Betikler:** `scratchpad/boyut_karsi_olgu.py` · `boyut_mekanizma.py`
**Hüküm:** ölçütler **GEÇTİ** · mekanizma zinciri **KOPTU** · yorum **DÜZELTİLDİ**

### Ön-kayıtlı ölçütler — üçü de geçti

```
gercek P&L  -5.676,83 $        ESIT AGIRLIK  +8.620,07 $     fark +14.296,91 $
K1 bolunmus yari : A +8.144,48 · B +6.509,32          -> GECTI
K2 permutasyon   : gercek deger 10.000 karistirmanin  -> GECTI (yuzdelik %0,00)
                   HEPSININ altinda
K3 uc deger      : en buyuk 5 ve 20 atilinca ayakta   -> GECTI
```

### Mekanizma zinciri KOPTU — ön-kayıtta bu ihtimal yazılıydı

| | korelasyon | t |
|---|---|---|
| M1 `notional ~ ret` | **−0,303** | −6,15 |
| M2 `skor ~ ret` | +0,009 | +0,18 |
| M3 `skor ~ notional` | −0,028 | −0,53 |
| EK `marjin ~ ret` | **−0,573** | −13,54 |

**Skor boyutu belirlemiyor.** Sebep kodda: `marjin_pct_hesapla` skoru
**%8–12 bandına sıkıştırıyor** ([testbot.py:255](testbot.py#L255)) — bant doyuyor.
Ön-kayıtlı *"skor → boyut → kayıp"* zinciri **kurulmadı**.

### Elenen açıklamalar

| aday | sonuç |
|---|---|
| **zaman** (equity düşerken boyut küçülüyor) | ❌ `zaman~ret` −0,032 · kısmi kontrolde ilişki **güçlendi** (−0,602) |
| **stop mesafesi** | ❌ dilim **içi** karşı-olgu global kazancın **%88'ini** taşıyor; log uzayında kısmi kontrol de zayıflatmadı |
| **kaldıraç** | ❌ `kaldirac~ret` −0,066 |

### 🔴 SONRA BULDUĞUM ARTEFAKT — ve ön-kayıtımdaki HATA

Koda tekrar bakınca ([testbot.py:1237-1241](testbot.py#L1237)):

```
risk_usdt = stop_frac * notional
if risk_usdt > hedef_risk:  hepsi kucultulur
   =>  notional  ~  hedef_risk / stop_frac
```

**`notional` yapısı gereği stop mesafesiyle ters orantılı.** Ve `ret` yaklaşık
stop mesafesi kadar oynar. Yani **`|ret| ∝ 1/notional` MEKANİK bir bağıntıdır** —
piyasa hakkında bir bulgu değil, boyutlandırma formülünün kendi aritmetiği.

Eşit-ağırlık karşı-olgusu bu yüzden kısmen **formülün aritmetiğini** ölçüyor.

🔴 **VE ÖN-KAYITTA YAZDIĞIM GEREKÇE YANLIŞTI.** Şöyle yazmıştım:

> *"TP1'e koşullamak burada AŞIRI KONTROL olurdu — TP1 nedensel yolun üzerinde."*

**Bu muhakeme hatalı.** TP1'in boyutun *ardılı* olabilmesi için boyutun fiyatı
etkilemesi gerekir; kâğıt defterde etkilemiyor. TP1 ile boyutun **ORTAK NEDENİ**
var: **stop mesafesi**. Dar stop → hem büyük `notional`, hem TP1'e varmadan
stop. Yani TP1 aracı değil, **ortak neden çocuğu**. Koşullamak aşırı kontrol değildi.

**Ve koşullanınca gradyan çöküyor:**

```
TUM POZISYONLAR (notional dilimi):   kazanan %82 / %53 / %26 / %17
                                     TP1 alan %83 / %48 / %19 / %4
TP1 ALMAYANLAR icinde:               kazanan %21 / %11 / %14 / %12   <- GRADYAN YOK
```

Bu, projenin **daha önce bir kez geri çektiği** bulgunun aynı çöküşü.

### 🔑 GERİYE NE KALIYOR — ve bu kısım sağlam

Yüzdeye hiç bakmayan ölçü: **R katı** (dolar / pozisyonun kendi riski).

```
toplam R      +62,06        ortalama R +0,193 (t +2,05)
toplam DOLAR  -4.749,10     ort risk $  77,45
saf risk-paritesi olsaydi: 77,45 x 62,06 = +4.805,97 $
```

**Defter R cinsinden ARTIDA, dolar cinsinden EKSİDE.** Aradaki ~9.555 $
tamamen **riskin sabit olmamasından** geliyor:

| risk $ dilimi | ort risk $ | toplam R | net $ | kazanan |
|---|---|---|---|---|
| Q1 düşük | 39,92 | **+157,66** | +6.201 | %96 |
| Q2 | 67,66 | +11,05 | +362 | %40 |
| Q3 | 80,43 | −41,98 | −3.505 | %25 |
| Q4 yüksek | 121,22 | **−64,67** | −7.807 | %16 |

Risk $ **32–156 arası, 4,8 kat** yayılıyor — risk paritesi **tutmuyor**.
Sebep kodda: `kaldirac_min=3` / `kaldirac_max=10` kırpmaları ve
`kaldirac_guvenlik_kirp` hedeflenen sabit riski bozuyor.

⚠️ `risk$ ~ R` korelasyonu (−0,564) **aynı artefakt sınıfından** olabilir
(`R = net/risk`). Artefakttan bağımsız olan tek ifade: **toplam R > 0, t=+2,05.**

### Ön-kayıtlı yönlü tahminlerin karnesi — 3'te 1

| # | tahmin | sonuç |
|---|---|---|
| 1 | fark pozitif ve kaybın yarısı mertebesinde | ✅ **TUTTU** (fark kaybın 2,5 katı — büyüklük bile aşıldı) |
| 2 | M2 sıfıra yakın, zincir "skor bilgisiz ama boyutu belirliyor" | ⚠️ **YARIM** — M2 sıfır (doğru) ama skor boyutu **belirlemiyor** (zincir koptu) |
| 3 | eşit ağırlık defteri artıya çevirmez, sadece kaybı küçültür | ❌ **YANLIŞ** — artıya çeviriyor (+8.620) |

### HÜKÜM

- ✅ Ön-kayıtlı ölçütler geçti — **kayda geçiyor, silinmiyor**.
- 🔴 **Ama eşit-ağırlık rakamı KURAL ÜRETMEZ:** kısmen boyutlandırma formülünün
  kendi aritmetiğini ölçüyor, ve TP1 katmanı gradyanı çökertiyor.
- 🔑 **Eyleme dönüşebilir tek kısım:** *"risk paritesi tutmuyor, risk $ 4,8 kat
  yayılıyor, defter R'de artıda"*. Bu **kaldıraç kırpmalarının** sorunu ve
  kendi ön-kaydını hak ediyor.

### Yöntem — pahalı ders

**Ön-kayıta yazılmış bir gerekçe yanlış olabilir.** *"TP1'e koşullamak aşırı
kontrol olur"* diye yazdım; ortak-neden yapısını atlamıştım. Bir değişkeni
"nedensel yolun üzerinde" ilan etmeden önce **o yolun gerçekten var olup
olmadığı** sorulmalı — burada boyut fiyatı etkilemediği için yol hiç yoktu.

---

## RİSK PARİTESİ — çalışıyormuş. Önceki turun "bulgusu" ÇÜRÜDÜ (2026-09-04)

**Ön-kayıt:** `ON_KAYIT_risk_paritesi.md` (commit `cd97004`, **koşumdan önce**)
**Betik:** `scratchpad/risk_paritesi.py`
**Hüküm:** **ZAYIF** (K1+K2 geçti, K3 düştü) · ve **mekanik bölüm önceki
turun eyleme dönüşebilir dediği bulguyu ÇÜRÜTTÜ**

### Ön-kayıtlı ölçütler

```
        N     SigmaR    ort R      t
A     160     +46,90   +0,293   +2,03
B     161     +15,16   +0,094   +0,78     <- neredeyse sifir
HAVUZ 321     +62,06   +0,193   +2,05
```

| ölçüt | sonuç |
|---|---|
| **K1** ΣR iki yarıda da > 0 | ✅ GEÇTİ (+46,90 / +15,16) |
| **K2** ort R > 0, t ≥ +2,0 | ✅ GEÇTİ (kıl payı) |
| **K3** uç 5'er atılınca ayakta | ❌ **DÜŞTÜ** |

→ **ZAYIF.** Ve R kenarı **ikinci yarıda pratikte yok** (t=+0,78) — yani
BOĞA/LONG döneminde R avantajı da kayboluyor.

### 🔴 MEKANİK BÖLÜM — önceki turun iddiası ÇÜRÜDÜ

Geçen tur *"risk paritesi tutmuyor, risk $ 4,8 kat yayılıyor"* demiştim ve
bunu **eyleme dönüşebilir tek bulgu** olarak işaretlemiştim. Ölçüldü:

```
gerceklesen_risk / hedef_risk  :  MEDYAN 1,000   (%10 0,500 · %90 2,000)
hedefin +-%20 bandinda         :  %47
gerceklesen risk yayilimi      :  32,4 -> 156,0   (4,8 kat)
HEDEF risk yayilimi            :  33,3 -> 159,6   (4,8 kat)   <-- AYNI
```

🔑 **Gerçekleşen riskin yayılımı, hedefin kendi yayılımıyla BİREBİR aynı.**
Hedef zaten `equity × %1,5` ve equity pencerede **2,26 kat** düştü; üstüne
smart-karşıysa **yarılama** var → 2,26 × 2 ≈ 4,5 kat. Gözlenen 4,8 kat.

**Yani 4,8 katlık yayılım bir kusur değil, TASARIMIN KENDİSİ.**
Kalan ±2 kat sapma da benim `smart_hiz` bayrağını pozisyon bazında yeniden
üretememem — bot kusuru değil, yeniden üretim sınırı.

**Hangi kısıt bağlıyor:** `kaldirac_min=3` → **%54** · kırpma yok → %46 ·
`kaldirac_max=10` → **hiç bağlamıyor (%0)**.

### Ön-kayıtlı yönlü tahminlerin karnesi — 3'te 1

| # | tahmin | sonuç |
|---|---|---|
| 1 | gerçekleşen risk hedefin **ALTINDA** kalır (küçültme asimetrik) | ❌ **YANLIŞ** — medyan oran tam **1,000**; altında %17, üstünde %36 |
| 2 | bağlayan kısıt çoğunlukla **`kaldirac_max`** | ❌ **YANLIŞ** — kmax **hiç** bağlamıyor, **kmin** %54 |
| 3 | yayılımın büyük kısmı equity düşüşüyle açıklanır | ✅ **TUTTU** — ve bu, 1 ve 2'yi geçersiz kılan bulgu |

### Karşı-olgu — artık dayanağı zayıf

```
gercek P&L                          -4.749,10 $
esit risk @ gerceklesen medyan      +4.643,08 $
esit risk @ hedef ortalamasi        +4.271,13 $
```

⚠️ **Bu rakamlar `ΣR`'ye dayanıyor ve `ΣR` ZAYIF çıktı** (K3 düştü, ikinci
yarı t=+0,78). Parite de zaten çalıştığına göre, karşı-olgunun ima ettiği
değişiklik *"riski zamanla azaltmayı bırak"* olur — yani **düşüş korumasını
kaldırmak**. Bu, ölçümün desteklediği bir öneri değildir.

### Betimleyici — hükme dayanak DEĞİL

`risk $` dilimlerine göre ΣR: +157,66 / +11,05 / −41,98 / −64,67.
⚠️ Bu tablo `R = net/risk` ortak paydasından **etkilenir**; hüküm yalnız
ΣR'ye dayanır ve o da zayıf.

**Smart-yarılaması sınandı** (artefaktsız: R boyuttan bağımsız, smart giriş
anında belli): karşı-yönde ort R **+0,293** (N=70, t=+1,17) vs aynı/nötr
**+0,166** (N=251, t=+1,69). Yarılanan grup **biraz daha iyi** ama
**hiçbiri anlamlı değil** → *"bot en iyi işlemlerinde riski kısıyor"*
hipotezi **desteklenmedi**.

### 🔑 SONUÇ — boyutlandırma kolu KAPANIYOR

İki tur ölçüm sonunda elde eyleme dönüşebilir bir şey **yok**:

1. Eşit-ağırlık karşı-olgusu → kısmen formülün kendi aritmetiği (geri çekildi).
2. *"Risk paritesi bozuk"* → **çürüdü**, parite çalışıyor.
3. ΣR > 0 → **zayıf**, uç değere bağımlı, ikinci yarıda yok.

**Boyutlandırmada kusur bulunamadı.** Bu bir başarısızlık değil, bir sonuçtur —
ve iki tur ön-kayıt olmasaydı bu koldan yanlış bir kod değişikliği çıkardı.

---

## REJİM ETİKETİ — bilgi taşıyor, ama bot onu TERS kullanıyor (2026-09-04)

**Ön-kayıt:** `ON_KAYIT_rejim_etiketi.md` (commit `32b908f`, **koşumdan önce**)
**Betik:** `scratchpad/rejim_yon_bilgisi.py`
**Hüküm:** 🔴 **DÜŞTÜ** — ve düşme **yönü** bulgunun kendisi.

### Kurulum

Rejim serisi **doğrulanmış** `rejim_gecis_sayim.py`'den **çağrılır** (yeniden
yazılmaz — aşağıya bak). 611 gün · `NOTR` 313 · `AYI` 204 · `BOGA` 94.
Alt evren: 566 sembol, günlük **medyan** getiri, **birim = GÜN**.

### Ana tablo

| rejim | gün | ort % | medyan % | tek-örneklemli t | artı gün |
|---|---|---|---|---|---|
| **BOGA** | 93 | **−1,305%** | −0,364% | **−2,47** | %46 |
| `NOTR` | 313 | −0,309% | −0,110% | −1,50 | %47 |
| `AYI` | 204 | −0,627% | −0,517% | **−2,84** | %43 |

| ölçüt | sonuç |
|---|---|
| **K1** `BOGA − (NOTR∪AYI) > 0`, t ≥ +2 | ❌ **DÜŞTÜ** — fark **−0,871%**, t=−1,58 (ters yön, anlamlı değil) |
| **K2** `BOGA` ort > 0 → LONG savunulur mu | ❌ **DÜŞTÜ** — −1,305%, t=−2,47 |
| **K3** `NOTR∪AYI` ort < 0 → SHORT savunulur mu | ✅ **GEÇTİ** |

🔑 **Bot BOĞA'da LONG açıyor. BOĞA, alt evrenin ölçülen EN KÖTÜ rejimi.**

### K4 — etiket fiyatın kılığı DEĞİL

`btc_chg24` çeyrekleri **içinde** fark duruyor: havuz farkının **%123'ü**
çeyrek içinde kalıyor. Yani etiket, BTC'nin günlük hareketinden **bağımsız
bilgi taşıyor**.

🔑 **Bu iyi haber değil, kötü haber:** etiket gürültü olsaydı zararsız olurdu.
Bilgi taşıyor ve **bot onu ters yönde kullanıyor**.

### 🔴 EPİZOT KIRILIMI — kullanıcı uyarısı sayesinde

*"11-19'u başka rejim, unutma"* (kullanıcı). Havuza gömülseydi kaçacaktı:

**7 BOĞA epizodunun 6'sı negatif:**

```
1/7  2025-10-03  -4,324%  (8 gun)      5/7  2026-08-21  -0,674%  (4 gun) <- GUNCEL
2/7  2025-01-17  -3,023%  (20 gun)     6/7  2025-07-10  -0,246%  (20 gun)
3/7  2025-09-12  -1,485%  (11 gun)     7/7  2025-05-06  +0,054%  (27 gun)
4/7  2025-10-12  -1,288%  (3 gun)
```

**Güncel epizot 7'nin 5'incisi — istisna DEĞİL, tipik.** Yani *"bu sefer
şanssızlık oldu"* açıklaması **kurulamıyor**; kural 2 yıldır aynı yönde yanlış.

**Kullanıcının işaret ettiği NOTR dilimi** (2026-07-25…08-20, 27 gün):
**+0,231%** — az sayıdaki **pozitif** epizottan biri. Yani bot o dönemde
hafif yükselen bir zemine karşı SHORT açıyordu **ve yine de kazandı**
(`A+B` +190 · `A+B+MA50` +599). Bu, **kapıların lehine** bir gözlem.

⚠️ **Gerilim kaydediliyor:** 30 günlük ölçümde NOTR, LONG yönünde
**−0,592%** (H=4sa, aday arşivi) çıkmıştı; burada **+0,231%** (H=24sa, tüm
arşiv). Farklı ufuk, farklı evren — çelişki değil ama **aynı şey de değil**.

### Gecikme — betimleyici, N=7

Etiket BOĞA'ya dönmeden önceki 7 günde BTC:
`+9,89 · +2,76 · +5,87 · +4,85 · +11,49 · −6,91 · **+24,27**`
ortalama **+7,46%** · medyan **+5,87%**

**Güncel geçiş (+%24,27) açık ara en geç kalanı** — ortalamanın üç katı.

### ⚠️ Sağlamlık — BOĞA'nın negatifliği KUYRUK günlerinden

BOĞA günlerinin dağılımı: %10 −7,20 · medyan **−0,36** · %75 +1,76 · %90 +3,30.
En kötü 5 gün: −28,6 · −12,9 · −11,5 · −10,0 · −9,5.
**O 5 gün çıkarılınca ort −0,557%, t=−1,39 → anlamlılık kayboluyor.**

🔑 Doğru okuma: *"BOĞA'da her gün düşüyor"* **değil**;
**"BOĞA, alt evrenin en şişman negatif kuyruğunu taşıyor"** — ve bot tam
orada kaldıraçlı LONG açıyor. Bu bir **sürüklenme** değil **risk** ifadesidir.

### Ön-kayıtlı yönlü tahminlerin karnesi — 3'te 1

| # | tahmin | sonuç |
|---|---|---|
| 1 | güncel epizot havuzun alt çeyreğinde (istisna) | ❌ **YANLIŞ** — 7'de 5, **tipik** |
| 2 | geçiş öncesi BTC ort **%10 üstü** hareket etmiş | ❌ **YANLIŞ** — ort +7,46%, medyan +5,87% (güncel +24,27 istisna) |
| 3 | `AYI` günleri `NOTR`'dan daha negatif | ✅ **TUTTU** (−0,627 vs −0,309) |

Ayrıca ön-kayıtta *"K1'in geçmesine %60"* demiştim — **düştü**, üstelik
**ters yönde**. *"K4'ün düşmesine %65"* demiştim — **geçti**.
**İki beklentim de yanlış çıktı.**

### 🔴 YÖNTEM — koşumdan önce yakalanan hata

İlk denemede rejim serisini **kendim yeniden yazdım** ve doğrulanmış betikle
**uyuşmadı** (745 gün / AYI 133 vs 611 gün / AYI 204). Üç gerçek hata:

1. SEZON ısınma penceresi (≥21 hafta, `wc[-21:-1]`) atlanmıştı
2. HAVA'nın SMA'sı **günün kendisini içeriyordu** (doğrusu hariç)
3. 🔴 `TEPKI_RALLISI` (sezon AYI + hava BOGA) **NOTR'a** haritalanmıştı —
   **doğrusu AYI**. En büyük fark bundandı.

**Hüküm yazılmadan yakalandı.** Çözüm: doğrulanmış fonksiyon **çağrılıyor**,
ve betiğe `seri_sinamasi()` kondu — seri beklenen sayıları vermezse betik
**çalışmayı reddediyor**.

---

## BOĞA'DA SEÇİM — huni ölçüldü, ayırıcı ARANDI ve BULUNAMADI (2026-09-04)

**Ön-kayıt:** `ON_KAYIT_boga_secim.md` (commit `2866b50`, **koşumdan önce**)
**Betik:** `scratchpad/boga_secim.py`
**Hüküm:** ayırıcı taraması **DÜŞTÜ** · ama **huni iki somut kusur gösterdi**

Kullanıcı talimatı: *"boğada işlem açmayacaksa bot ne yapacak, bu kabul edilmez.
19'undan sonra seçtiği coinleri incele; ne olsaydı artıya geçecekleri seçerdi.
Her aşamayı değerlendir, her ihtimali hesapla."*
🔴 *"BOĞA'da işlem açma"* seçeneği **masadan kaldırıldı.**

Popülasyon: 13.003 satır · 221 sembol · 13 gün · birim **sembol-gün** · H=4 saat, ham.

### 🔴 AŞAMA A — HUNİ: eleme getiriyi İYİLEŞTİRMİYOR, biri KÖTÜLEŞTİRİYOR

| aşama | satır | sembol-gün | ort % |
|---|---|---|---|
| 1. taranan (hacim süzgeci sonrası) | 13.003 | 627 | **−0,816%** |
| 2. `skor ≥ 45` | 4.642 | 319 | **−1,132%** ⬅ **DAHA KÖTÜ** |
| 3. kapıyı geçen (LONG kararı) | 642 | 207 | −0,745% |

**Kapı katkısı: +0,071%, t=+0,18** → kapı **hiçbir şey eklemiyor**.
Ve **skor eşiği popülasyonu kötüleştiriyor**: skoru yüksek olanlar, taranan
evrenin tamamından daha çok düşüyor.

### 🔴 VETO KARNESİ — `long_veto` TERS ÇALIŞIYOR

| veto | engellenenin getirisi | kalanın getirisi | fark | t | okuma |
|---|---|---|---|---|---|
| **`long_veto`** | **+0,128%** | −0,855% | **+0,983%** | **+1,71** | 🔴 **İYİYİ engelliyor** |
| `blowoff` | −3,641% | −0,855% | −2,786% | −0,92 | ✅ kötüyü engelliyor (anlamsız) |

`long_veto` **1.170 satırda** devreye girdi ve engellediği dilim, geçirdiğinden
**daha iyiydi**. t=+1,71 → **anlamlı değil**, ama yön net ve bu bir
**ön-kayıtlı aşama değerlendirmesi**, taranmış hücre değil.

### AŞAMA B — AYIRICI TARAMASI: 43 hücre, hiçbiri şansı geçemedi

En güçlü 10 hücre (ham):

```
ma50_mesafe (ceyrek)  -2,974%  t -2,94      last1 (ceyrek)       -0,837%  t -2,19
chg24 (ceyrek)        -2,787%  t -2,61      float_oran (ondalik) +1,202%  t +2,11
comp (ceyrek)         -1,578%  t -2,60      pos (ondalik)        -1,076%  t -2,10
rel3 (ceyrek)         -1,350%  t -2,30      pos (ceyrek)         -1,503%  t -2,09
last3 (ceyrek)        -1,276%  t -2,21      comp (ondalik)       -2,326%  t -2,04
```

🔴 **PERMÜTASYON — asıl sınama.** Sonuç etiketleri 1.000 kez karıştırıldı ve
**her seferinde 43 hücrelik taramanın tamamı tekrarlandı**, en büyük |t|
kaydedildi:

```
sans dagiliminin en buyuk |t|'si : MEDYAN 2,30 · %95 3,12 · max 4,15
GERCEK taramanin en iyi |t|'si   : 2,94   ->  yuzdelik %89,7
```

| ölçüt | sonuç |
|---|---|
| **K1** en iyi \|t\|, şans dağılımının üst %5'inde | ❌ **DÜŞTÜ** (2,94 < 3,12) |
| **K2** iki yarıda aynı işaret | ✅ A −2,079% (t−1,90) · B −3,602% (t−2,40) |
| **K3** \|fark\| ≥ %1,0 | ✅ GEÇTİ |

→ **DÜŞTÜ.**

🔑 **Permütasyon olmasaydı bu bir "bulgu" olurdu.** *"MA50'den uzak coinler
daha çok düşüyor, t=−2,94, iki yarıda da ayakta"* diye yazardım — ve
**43 hücre ararken şans eseri bulunan t'nin medyanı zaten 2,30.**
Bu, projenin dördüncü geri çekmesi olurdu.

### AŞAMA C — ters soru: kazananlar kaybedenlere BENZİYOR

4 saatte en çok yükselen %10 (**+6,89%**) vs en çok düşen %10 (**−8,94%**) —
**tüm alanlar neredeyse aynı**:

```
chg24       +17,5  vs  +19,2      score       41,4  vs  42,0
ma50_mesafe +15,4  vs  +17,2      pos         0,84  vs  0,88
vol_x       +10,6  vs  +16,1      oi24        14,3  vs  10,0
```

En büyük göreli fark `vol_x` (kazananlarda **düşük**) ve `oi24` (kazananlarda
**yüksek**) — *"daha az hype, daha çok gerçek pozisyonlanma"* yönünde. Ama bu
ikisi ön-kayıtlı taramada **şans eşiğini geçemedi**.

⚠️ Sonuca göre seçilmiş kümeler — **hüküm taşımaz**, Aşama B zaten önceden ölçtü.

### Ön-kayıtlı yönlü tahminlerin karnesi — 3'te 1,5

| # | tahmin | sonuç |
|---|---|---|
| 1 | kapı aşaması getiriyi iyileştirmeyecek | ✅ **TUTTU** (+0,071%, t=+0,18) |
| 2 | `long_veto` doğru çalışacak | ❌ **YANLIŞ** — **ters** çalışıyor |
| 3 | en iyi ayırıcı `chg24`/`pos` ailesinden | ⚠️ **YARIM** — `ma50_mesafe` çıktı, ama ilk onun hepsi fiyat türevi → *"tek bant"* dersi **tekrarlandı** |

### SONUÇ — kullanıcının sorusuna doğrudan cevap

**"Ne seçseydi kazanırdı?"** → **Botun topladığı verilerde o ayrım YOK.**
Kazananlar ve kaybedenler 20 alanda birbirine benziyor; en iyi ayırıcı 43
hücre aramasının şans eşiğini geçemiyor.

**Ama huni iki somut kusur gösterdi ve ikisi de eleme aşamasında:**
1. **`skor ≥ 45` popülasyonu kötüleştiriyor** (−0,816% → −1,132%)
2. **`long_veto` iyi adayları engelliyor** (+0,128% vs −0,855%, t=+1,71)

İkisi de ön-kayıtlı aşama değerlendirmesi, taranmış hücre değil — ama
**ikisi de istatistiksel olarak zayıf** ve kendi ön-kayıtlarını hak ediyor.

---

## `long_veto` — BİRİNCİL GEÇTİ: veto kestiği dilimde HAKSIZ (2026-09-04)

**Ön-kayıt:** `ON_KAYIT_long_veto.md` (commit `76d1f08`, **koşumdan önce**)
**Betik:** `scratchpad/long_veto_testi.py`
**Hüküm:** 🔴 **K2 GEÇTİ — veto haksız** · ⚠️ ama üç ciddi çekinceyle

Kullanıcı talimatı: *"long veto testini yap"*. (Skor kolu kullanıcı kararıyla
bırakıldı: *"skorun yanılttığını biliyoruz, hatta ters yönü gösteriyor."*)

### Kural ve gerçek ağırlığı

```
long_veto = pos<0.25  or  chg24<=-40  or  (chg24<0 & oi24>=15)  or  para_cikis
```

Vetolanan 1.243 satırın **%68'i** tek koşuldan: **`pos < 0.25`** (bandın dibi,
"düşen bıçak"). Diğerleri marjinal.

### BİRİNCİL — `pos < 0.25`, H = 4 saat (botun medyan tutması 2,2 saat)

| küme | sembol-gün | ham getiri |
|---|---|---|
| **`pos < 0.25`** (vetonun kestiği) | 139 | **+0,131%** |
| `pos ≥ 0.25` (geçirdiği) | 594 | **−1,127%** |
| **fark** | | **+1,259%** · gün-t **+2,24** · MDE 1,125 |

`|fark| > MDE` → örneklem bu büyüklüğü **görebiliyor**.

| ölçüt | sonuç |
|---|---|
| **K1** fark < 0 → veto haklı | ❌ hayır |
| **K2** fark > 0 ve t ≥ +2,0 → veto **HAKSIZ** | ✅ **EVET** |

🔑 **Bandın dibindeki coinler, botun aldıklarından daha iyi gitti. Veto tam
olarak onları kesiyor.**

### 🔴 ÇEKİNCE 1 — 24 SAATTE İŞARET DÖNÜYOR

| ufuk | `pos<0.25` | `pos≥0.25` | fark | t |
|---|---|---|---|---|
| **4 saat** | +0,131% | −1,127% | **+1,259%** | **+2,24** |
| **24 saat** | −3,018% | −1,931% | **−1,087%** | −0,89 |

**Dört saatte iyi, yirmi dört saatte kötü.** Mekanizması tutarlı:
*"düşen bıçak"* önce **sekiyor**, sonra düşmeye devam ediyor.

🔑 Yani veto **4 saatlik tutucu için yanlış, 24 saatlik tutucu için doğru**.
Bot 2,2 saat tutuyor → ön-kayıtlı birincil ufuk (4 saat) **doğru seçilmişti**,
ama bulgu **ufka bağlı** ve bu aynen yazılır.

### 🔴 ÇEKİNCE 2 — vetonun GERÇEKLEŞEN etkisi anlamlı DEĞİL

Birincil test **koşulu** tüm popülasyonda sınadı (güç için). Vetonun
**fiilen kestiği** satırlar çok daha az:

| küme | sembol-gün | ort % | gün-t |
|---|---|---|---|
| VETOLANAN | 63 | −0,127% | −0,31 |
| GEÇEN (LONG kararı) | 207 | −0,804% | −2,14 |
| **fark** | | **+0,676%** | **+1,20** ⬅ anlamlı **değil** |

Alt-tetik kırılımı (vetolanan içinde): `pos<0.25` **+0,039%** (40 sembol-gün) ·
`chg24<0 & oi24≥15` **−0,971%** (26) · artık≈`para_cikis` +0,356% (20, 2 gün).

**Yani: koşul genel popülasyonda anlamlı, vetonun kendi etkisi değil.**

### 🔴 ÇEKİNCE 3 — düzeltmek BOĞA-LONG'u KÂRLI YAPMIYOR

Karşı-olgu (ham, mekaniksiz):

```
bugunku LONG havuzu           -0,804%
+ pos<0.25 kaldirilsa         -0,527%   (+0,277 puan)
+ oi-artis kaldirilsa         -0,669%   (+0,135 puan)
+ TUM veto kaldirilsa         -0,442%   (+0,362 puan)
```

**Tüm veto kalksa bile havuz −0,442% ile EKSİDE.** Veto kaybın kaynağı değil,
kaybı bir miktar **büyüten** bir etken.

### Ön-kayıtlı yönlü tahminlerin karnesi — 3'te 1

| # | tahmin | sonuç |
|---|---|---|
| 1 | alt-tetik 3 (fiyat-düşük+OI) **haklı** çıkacak | ❌ **YANLIŞ** (4 saatte +0,216%, t=+0,49 — etkisiz). 24 saatte haklı yönde (−3,177%) ama t=−1,63 |
| 2 | alt-tetik 1 havuz sonucunu belirleyecek | ✅ **TUTTU** (%68) |
| 3 | H=24'te fark H=4'ten **büyük** olacak | ❌ **YANLIŞ** — işaret **döndü** |

### HÜKÜM ve sınır

✅ Ön-kayıtlı birincil ölçüt **geçti** — bu, uzun süredir birincil ölçütü geçen
**ilk** bulgu.

🔴 **Ama bileşen KALDIRILMAZ.** Üç sebep, üçü de ön-kayıtta yazılıydı:
1. Ham ölçüm — mekanik (stop/hedef) ve portföy (8 slot) aşamaları yapılmadı.
2. **13 günlük tek epizot** — ikinci bir BOĞA epizodunda görülmeden kapıya
   dokunulmaz.
3. İşaret **24 saatte dönüyor** → bulgu ufka bağlı, ve botun tutma süresi
   değişirse hüküm de değişir.

**Sonraki adım kod değil, mekanik aşaması:** *"`pos<0.25` adayları botun kendi
stopuyla oynatılsaydı ne olurdu?"* — çünkü sekme 4 saat sürüyor ve botun stopu
2 saatte tetikleniyor olabilir.

---

## `pos<0.25` MEKANİK AŞAMASI — kenar mekanikten SAĞ ÇIKMIYOR (2026-09-04)

**Ön-kayıt:** `ON_KAYIT_pos_mekanik.md` (commit `5338860`, **koşumdan önce**)
**Betik:** `scratchpad/pos_mekanik.py`
**Hüküm:** 🔴 **DÜŞTÜ** — ve mekanizma tam olarak öngörülen yerde.

Mekanik kod `stop_mu_sure_mu.py`'den **kaynaktan çağrıldı** (kopyalanmadı) —
bu oturumda rejim serisini yeniden yazıp üç hata yapmanın dersi.

### Zincirin tamamı

| aşama | `pos<0.25` | `pos≥0.25` | fark | t |
|---|---|---|---|---|
| **ham, 4 saat** | +0,023% | −1,410% | **+1,433%** | +1,59 |
| **MEKANİKLİ** | **−1,470%** | −1,141% | **−0,328%** | −0,60 |

**Korunan pay: −%23.** Kenar yenmedi, **tersine döndü**.

| ölçüt | sonuç |
|---|---|
| **K1** mekanikli fark > 0, t ≥ +2,0 | ❌ **DÜŞTÜ** (−0,328%, t=−0,60) |
| **K2** korunan pay ≥ %50 | ❌ **DÜŞTÜ** (−%23) |
| **K3** mekanik eşitliği | ✅ **GEÇTİ** — kıyas sağlam |

`|fark| 0,328 < MDE 1,088` → farkın kendisi için **"göremiyoruz"**; ama
**işaret dönüşü** (+1,433 → −0,328) tek başına belirleyici.

### 🔑 MEKANİZMA — çıkış sebebi dağılımı gösteriyor

```
pos<0.25   STOP %78 · STOP_TP1SONRASI %13 · TP2 %5  · ZAMAN %4   medyan 6,0 saat
pos>=0.25  STOP %65 · STOP_TP1SONRASI %18 · TP2 %15 · ZAMAN %2   medyan 3,0 saat
```

**Sekme 4 saat sürüyor; bot medyanda 6 saat tutuyor.** Yani tam olarak
sekmenin bittiği ve dönüşün başladığı yere kadar tutuyor. Ve:

- **stop-olma %91 vs %83** — daha çok stop oluyor
- **TP2 %5 vs %15** — üçte bir oranında hedefe ulaşıyor

Kenar var, **bot onu alacak mekaniğe sahip değil.**

### K3 geçti — kıyas sağlam

stop genişliği 5,85% vs 4,94% (**1,18×**) · stop-olma 1,09× → ikisi de 1,5 kat
içinde. Yani *"kollar oynaklıkta ayrışıyor, kıyas bozuk"* itirazı **kurulamıyor**.

### ⚠️ Popülasyon değişti — dürüstlük notu

Mekanik, asgari %2 stop şartını sağlamayan **3.150 satırı eliyor** (+698 geçmiş
yetersiz, +233 seri yok) → 13.003'ten **9.770**'e. Bu alt-popülasyonda ham fark
**+1,433% ama t=+1,59** (tam popülasyonda +1,259% / t=+2,24 idi).
**Yani kaybın bir kısmı mekanikten değil, popülasyon daralmasından geliyor.**

### Ön-kayıtlı yönlü tahminlerin karnesi — 3'te 1,5

| # | tahmin | sonuç |
|---|---|---|
| 1 | `pos<0.25` stopu daha geniş → **K3 düşecek** | ⚠️ **YARIM** — stop gerçekten daha geniş (1,18×) ama K3 **geçti** |
| 2 | TP1 oranı **yüksek**, TP2 oranı düşük | ⚠️ **YARIM** — TP2 düşük ✅ (%5 vs %15) ama TP1 de **düşük** ❌ (%18,6 vs %32,7) |
| 3 | mekanikli fark ham farktan küçük | ✅ **TUTTU** (dramatik: +1,433 → −0,328) |

### 🔴 SONUÇ — `long_veto`'nun `pos<0.25` bileşeni KALDIRILMAZ

Ham kenar gerçekti ve ön-kayıtlı birincil ölçütü geçmişti. **Mekanik aşaması
onu tükettiği için öneri düşüyor.** Vetoyu kaldırmak, botun stop'una yem olan
işlemler eklerdi.

🔑 **Ve bu, mekanik aşamasının neden zorunlu olduğunun somut kanıtı:**
bu aşama yapılmasaydı *"`pos<0.25` vetosunu kaldır, +%1,26 kenar var"*
önerisi yazılacaktı.

### Kenarı almanın tek yolu KAPALI — iki bağımsız gerekçeyle

Sekme ~4 saatte bitiyor; almak için **~4 saatte çıkmak** gerekir. Bu bir
**çıkış sıkılaştırmasıdır** ve bu projede sıkılaştıran **30 varyantın 30'u da
kalmıştır** (`olcumler.md` → sayım). Ayrıca 13 günlük tek epizot.

**Bu kol kapanıyor.**

---

## `pos`'a GÖRE KOŞULLU MEKANİK — düştü ama KAPANMIYOR (2026-09-04)

**Ön-kayıt:** `ON_KAYIT_pos_kosullu_mekanik.md` (commit `bd92dab`, **koşumdan önce**)
**Betik:** `scratchpad/pos_kosullu_mekanik.py`
**Hüküm:** **DÜŞTÜ** (K1) · ama K2+K3+K4 geçti ve **güç yetersiz** → *"göremiyoruz"*

Kullanıcı talimatı: *"bunun başka bir yolu olmalı, mekaniği ayarlayalım pos'a göre."*

**Sarmalayıcı sınaması:** parametresiz hâli kaynaktaki `oynat()` ile 400 satırda
**birebir aynı** (fark 0) → varyantlar dışında davranış değişmedi.

### 🔑 TEŞHİS — çarpıcı olgu

```
pos<0.25, mevcut mekanik:
  MFE medyan  +4,98%   ·  %25 +2,74%  ·  %75 +9,83%
  hic artiya gecmeyen:  17 / 1400  (%1)
  ama STOP ile biten:   %91
```

**Bu pozisyonların %99'u artıya geçiyor, medyanda +%5 kâr görüyor, ve %91'i
stopla kapanıyor.** Yani kâr *var*, alınamıyor.

Stop tetiklenme zamanı: **%59'u 4. saatten SONRA** → teşhis **"çıkış çok geç"**.
MFE zirvesi medyan **6. saat**. TP1'e ulaşan 260 pozisyonun yalnız **%29'u**
TP2'ye gidiyor.

### Varyantlar (eşleşmiş: aynı satırlar, farklı çıkış)

| varyant | `pos<0.25` net | fark | eşli t | med. süre | stop% |
|---|---|---|---|---|---|
| TABAN (mevcut) | −1,459% | — | — | 6,0 | %91 |
| **V1** zaman stopu 6 saat | −0,961% | **+0,721%** | +1,69 | 6,0 | %46 |
| V2 TP1'de %100 çıkış | −1,529% | −0,076% | −0,48 | 5,0 | %78 |
| **V3** V1+V2 | **−0,833%** | **+0,797%** | **+1,94** | 5,0 | %42 |
| V4 stop 2,5×ATR | −2,315% | −1,499% | −2,23 | 15,0 | %70 |

🔑 **Kaldıraç zaman stopunda, TP1 politikasında değil:** V1 tek başına
kazancın neredeyse tamamını veriyor (+0,721 / +0,797). V2 hiçbir şey katmıyor.

### Ölçütler

| # | ölçüt | sonuç |
|---|---|---|
| **K1** | fark > 0 ve eşli t ≥ **+2,5** | ❌ **DÜŞTÜ** (+0,797 / **t=+1,94**) |
| **K2** | iki yarıda da > 0 | ✅ GEÇTİ (A +1,077 · B +0,557) |
| **K3** | 🔴 koşulsuz kontrol | ✅ **GEÇTİ** |
| **K4** | fark ≥ %0,5 | ✅ GEÇTİ |

**K3 ayrıntısı — kazanç gerçekten `pos`'a özgü:**

```
pos<0.25  : +0,797%  (t +1,94)
pos>=0.25 : +0,172%  (t +1,68)
TUM satir : +0,214%  (t +2,73)
```

Yani V3 herkese uygulansa kazanç **dörtte bire** iniyor. **30/30 duvarına
çarpan sıradan bir çıkış sıkılaştırması DEĞİL** — koşulluluk gerçek fark yaratıyor.

### 🔴 NEDEN "KAPANDI" DEMİYORUM

```
MDE 0,821  ·  |fark| 0,797  ->  GOREMIYORUZ
```

Fark, örneklemin görebileceğinin **hemen altında**. `t=+1,94`, eşik +2,5
(dört varyant için düzeltilmiş; tek varyant olsaydı +2,0 idi ve **o da
geçilemezdi**).

**Bağlayıcı kısıt N:** `pos<0.25` diliminde yalnız **87 sembol-gün**, 13 gün.
Bu, bulgunun yanlış olduğunu **göstermiyor** — göremediğimizi gösteriyor.

### Ön-kayıtlı yönlü tahminlerin karnesi — 3'te 1,5

| # | tahmin | sonuç |
|---|---|---|
| 1 | teşhis "erken çıkış" diyecek; MFE zirvesi ilk 4 saatte | ⚠️ **YARIM** — teşhis doğru (%59 sonra), ama MFE zirvesi medyan **6. saat**, ilk 4 saatte olan yalnız %44 |
| 2 | **V2** en iyi varyant olacak | ❌ **YANLIŞ** — V2 hiçbir şey katmadı (−0,076%); kaldıraç **zaman stopunda** |
| 3 | V4 (geniş stop) düşecek | ✅ **TUTTU** (−1,499%) |

### Durum — bu kol AÇIK kalıyor

Bu oturumda kapanan dört kolun aksine, burada bulgu **yanlışlanmadı**:
yön tutarlı · iki yarıda da aynı işaret · mekanizma ölçülmüş · koşulsuz
kontrolü geçti. **Eksik olan tek şey N.**

**İkinci bir BOĞA epizodu N'i kabaca ikiye katlar** ve aynı fark
(+%0,8) o zaman `t ≈ 2,7` verir → eşiği geçer. Yani bu, **veri bekleyen**
bir aday; çürütülmüş bir fikir değil.

⚠️ **Yine de kod değişmez:** portföy aşaması (8 slot, marjin tavanı) yapılmadı
ve koşullu mekanik çıkış kodunu dallandırır — bakım maliyeti ölçüme dahil değil.

---

## SKORUN TERSİ — DÜŞTÜ, ve önceki notu DÜZELTİYOR (2026-09-04)

**Ön-kayıt:** `ON_KAYIT_skor_tersi.md` (commit `c83e4a8`, **koşumdan önce**)
**Betik:** `scratchpad/skor_tersi.py`
**Hüküm:** 🔴 **DÜŞTÜ** — *"skor ters yönü gösteriyor"* **kanıtlanamadı**

Kullanıcı talimatı: *"skor: tersi doğru mu onu notlamıştık, 22 Ağustostan beri
bütün pozlara bak, skorun tersine işlem alsaydı ne olurdu, skorun poz
almadaki etkisi ne?"*

Pencere kullanıcının tarihi: **2026-08-22'den itibaren** · 12.435 satır · 12 gün.

### S1 — skor<45 (ters) vs skor≥45 (botun kuralı)

| kol | sembol-gün | ham 4sa | sembol-gün | **mekanikli** |
|---|---|---|---|---|
| `skor<45` | 523 | −0,469% | 401 | **−0,781%** |
| `skor≥45` | 289 | −0,918% | 252 | **−1,173%** |
| **fark** | | **+0,449%** (t +1,39) | | **+0,392%** (t **+1,22**) |

| ölçüt | sonuç |
|---|---|
| **K1** mekanikli fark > 0, t ≥ +2,0 | ❌ **DÜŞTÜ** (+0,392 / t=+1,22) |
| **K2** ham ve mekanik aynı işaret | ✅ GEÇTİ |
| **K3** iki yarıda da > 0 | ❌ **DÜŞTÜ** — A yarı **−0,095%**, B yarı +0,879% |
| **K4** mekanik eşitliği | ✅ GEÇTİ (0,75× / 0,96×) |

`MDE 0,643 > |fark| 0,392` → **"göremiyoruz"**.

🔴 **K3 belirleyici:** ilk yarıda fark **negatif**. Yani ters-işlem tezi
pencerenin yalnız ikinci yarısında görünüyor — **tekrarlamıyor.**

### 🔑 S2 — SKOR EŞİĞİNİN KATTIĞI DEĞER: **+0,006 PUAN**

```
taranan evrenin ham getirisi : -0,924%
skor >= 45'in getirisi       : -0,918%
esigin kattigi deger         : +0,006 puan
```

**Eşik adayların %64'ünü kesiyor ve ölçülebilir hiçbir şey katmıyor.**
Ne iyileştiriyor ne kötüleştiriyor — **etkisiz**.

### Skor bantları — monotonluk YOK (betimleyici)

```
0-35   ham +0,014  mek -0,537      45-50   ham -1,291  mek -0,889
35-40  ham -0,311  mek -0,697      50-60   ham +0,381  mek -0,498
40-45  ham -0,889  mek -0,601      60-200  ham -1,093  mek -1,396
```

Ham getiride **en iyi bant 50-60**, **en kötü bant 45-50** — yan yana.
Sıralı bir yapı yok → skor sürekli bir bilgi **taşımıyor**, gürültü.

### 🔴 S3 — GERÇEK DEFTER, ARŞİVİN TERSİNİ SÖYLÜYOR

08-22'den beri **207 gerçek pozisyon**:

```
skor ~ notional : -0,105   (marjin_pct %8-12'ye DOYUYOR -> teyit edildi)
skor ~ getiri   : +0,062

skor uctebiri   N   ort skor   ort ret%     net $
dusuk          69      48,3    +0,444%   -1.761,92
orta           69      55,8    +0,547%     -987,81
yuksek         69      69,5    +1,257%   -1.111,20
```

**Gerçek defterde YÜKSEK skorlu pozisyonlar daha İYİ yüzde getiri verdi**
(+1,257% vs +0,444%) — arşiv kolunun **tersi**.

### 🔴 ÖNCEKİ NOTUN DÜZELTİLMESİ — bir günlük hassasiyet

Huni ölçümü (08-**21**'den) *"skor ≥ 45 popülasyonu kötüleştiriyor"* demişti
(taranan −0,816% → skor≥45 −1,132%). Bu ölçüm (08-**22**'den) aynı şeyi
**−0,924% → −0,918%** buluyor, yani **fark yok**.

**Tek günlük kayma bulguyu ortadan kaldırıyor.** Önceki not **kırılgandı** ve
bu kayda geçiyor.

### Ön-kayıtlı yönlü tahminlerin karnesi — 3'te 3 ✅

| # | tahmin | sonuç |
|---|---|---|
| 1 | ham farkta `skor<45` önde | ✅ TUTTU (+0,449%) |
| 2 | mekanikli fark ham farktan küçük | ✅ TUTTU (+0,392 < +0,449) |
| 3 | skor bantlarında monotonluk olmayacak | ✅ TUTTU |

**İlk kez üç tahminin üçü de tuttu.**

### SONUÇ — kullanıcının sorusuna doğrudan cevap

| soru | cevap |
|---|---|
| *"skorun tersine işlem alsaydı ne olurdu?"* | Ölçülebilir bir iyileşme **yok**. Yön zayıfça o tarafta ama **anlamlı değil**, **ilk yarıda tersine dönüyor**, ve **gerçek defterde tam tersi**. |
| *"skorun poz almadaki etkisi ne?"* | **+0,006 puan.** Adayların %64'ünü kesiyor, karşılığında hiçbir şey vermiyor. |
| *"skorun boyutlandırmadaki etkisi?"* | **Yok** — `marjin_pct` %8-12'ye doyuyor, `skor~notional = −0,105`. Teyit edildi. |

🔑 **Skor ters değil, BOŞ.** *"Ters yönü gösteriyor"* notu bu ölçümle
**desteklenmedi**; doğru ifade **"ayırmıyor"**.

---

## SKORUN BEŞ BİLEŞENİ — dördü boş, beşincisi TERS. Skor onarılamadı (2026-09-04)

**Ön-kayıt:** `ON_KAYIT_skor_bilesenleri.md` (commit `81c95fb`, **koşumdan önce**)
**Betik:** `scratchpad/skor_bilesen.py`
**Hüküm:** 🔴 **DÜŞTÜ → KOD DEĞİŞMEDİ** (ön-kayıt s.7 gereği)

Kullanıcı **tam yetki** verdi (*"istediğin ayarlamayı yap"*). Ön-kayıt
koşumdan önce yazıldı ve **ölçüt tutmadığı için değişiklik yapılmadı.**

### AŞAMA A — 14 ön-kayıtlı sınama (üst çeyrek − alt çeyrek, ham 4 saat, LONG)

| terim | skordaki payı | BOĞA fark / t | NOTR fark / t |
|---|---|---|---|
| `s_oi` | **%41** | −0,504% / **−1,12** | +0,738% / +0,54 |
| `s_fund (abs)` | %22 | +0,018% / **+0,03** | +0,082% / +0,06 |
| `s_comp` | %3 | 🔴 **dağılım YOK** | 🔴 **dağılım YOK** |
| `s_vol` | %23 | −0,472% / −1,01 | +0,445% / +0,57 |
| **`s_brk`** | %11 | **−1,265% / −2,39** | −1,998% / −1,49 |
| Ö1 işaretli funding | — | +0,112% / +0,25 | −1,668% / −1,37 |

### 🔑 ÜÇ YAPISAL BULGU

**1. `s_comp` ÖLÜ TERİM.** Çeyrekleri çöküyor — değişken pratikte sabit.
Tavanı 20 puan, gerçek katkısı 1,3, taşıdığı bilgi **ölçülemiyor bile**.

**2. `s_fund (abs)` sıfır bilgi.** Skorun **%22'si**, t=+0,03. Kelimenin tam
anlamıyla hiçbir şey. İşaretli hâli (Ö1) de eşiği geçemedi.

**3. 🔴 `s_oi` ve `s_vol` REJİMLER ARASI İŞARET DEĞİŞTİRİYOR.**

```
s_oi   BOGA -0,504%  ·  NOTR +0,738%
s_vol  BOGA -0,472%  ·  NOTR +0,445%
```

Skorun **%64'ü** (s_oi + s_vol) bir rejimde bir şey, diğerinde tersini
söylüyor. **Tek skorla iki yön seçilemez** — ön-kayıtın açılışındaki yapısal
şüphe **doğrulandı**.

**4. Tek sinyalli terim `s_brk` ve YANLIŞ YÖNDE.** BOĞA'da t=−2,39: bant
tepesine yakınlık + son 1 saat kazancı → **daha kötü** ileri getiri.
**Skor bu terime PUAN EKLİYOR.**

### Ö2 — `squeeze_bonus`: kodun vadesi geçmiş talimatı kapandı

Kod aynen şöyle diyordu: *"Boğada 'sert düşer' tersine dönebilir. **Boğaya
girildiğinde bu kural YENİDEN ölçülmelidir.**"* 21 Ağustos'ta girildi, ölçülmedi.

⚠️ **Yöntem düzeltmesi:** terim ikili (0/8), çeyrek kesimi onda çöküyor.
Ön-kayıtlı **soru** değişmeden, doğru yöntemle (ikili kesim) koşturuldu.

```
NOTR  bonus +0,120%  ·  digeri -0,060%  ·  fark +0,180%  (t +0,16)
BOGA  bonus -0,359%  ·  digeri -0,852%  ·  fark +0,493%  (t +0,97)
```

**Zararlı tersine dönüş YOK** — kodun korktuğu şey olmamış. Ama **fayda da yok**
(ikisi de anlamsız). Terim **etkisiz**. Talimat yerine getirildi.

### AŞAMA B — yeni skor türetildi (aranmadı)

Ön-kayıttaki mekanik kural uygulandı. **Tek terim geçti:** `s_brk`.
Diğer dördü `|t| < 2,0` ile elendi.

```
YENI SKOR = 100 x s_brk   (olculen isarete gore TERS cevrilmis)
```

### AŞAMA C — AYRI YARIDA doğrulama (terimler A'da seçildi, hüküm B'de)

| ölçüm | yeni | eski | fark | t | MDE |
|---|---|---|---|---|---|
| **ham** | +0,038% | −0,933% | **+0,971%** | **+1,58** | 1,226 |
| mekanik | −0,846% | −1,112% | +0,266% | +0,54 | 0,993 |

| ölçüt | sonuç |
|---|---|
| **K1** ham fark > 0, t ≥ +2,0 | ❌ **DÜŞTÜ** (+0,971 / t=+1,58) |
| **K2** ayrı yarıda doğrulama | ✅ yapıldı |
| **K3** mekanikli de > 0 | ✅ GEÇTİ |
| **K4** kısır kapı yok (2.767 vs 2.737 aday) | ✅ GEÇTİ |

`MDE 1,226 > |fark| 0,971` → **"göremiyoruz"**.

### Ön-kayıtlı yönlü tahminlerin karnesi — 3'te 3 ✅

| # | tahmin | sonuç |
|---|---|---|
| 1 | `s_comp` hiçbir rejimde geçmeyecek | ✅ TUTTU (dağılımı bile yok) |
| 2 | en az bir terim rejimler arası ZIT işaret verecek | ✅ TUTTU (`s_oi` **ve** `s_vol`) |
| 3 | `s_oi` skorun %41'i olduğu hâlde anlamlı çıkmayacak | ✅ TUTTU (t=−1,12) |

**Üst üste ikinci kez üçte üç.**

### 🔴 HÜKÜM — yetki vardı, değişiklik YAPILMADI

Kullanıcı kod değişikliği için **tam yetki** verdi. Ön-kayıtlı ölçüt
(koşumdan önce commit edilmiş) **geçmedi**, dolayısıyla `radar.py`
**değiştirilmedi.**

**Skor "yanlış ayarlanmış" değil — ölçülebilir bilgi taşımıyor:**
dört bileşenin dördü boş, beşincisi ters, ve %64'ü rejimler arası işaret
değiştiriyor. **Ağırlık ayarı bunu çözmüyor** çünkü çözülecek bir sinyal yok.

⚠️ Tek somut aday `s_brk`'ın **ters çevrilmesi** — ayrı yarıda +0,97 puan
kazandırdı ama saptama eşiğinin altında kaldı. **Veri bekleyen** bir aday;
`pos<0.25` (V3) ile aynı sınıfta.

---

## 🔴 STOP MESAFESİ — hakem raporunun 5. maddesi (2026-09-05) — **DÜŞTÜ**

**Ön-kayıt:** `ON_KAYIT_stop_mesafesi.md`, commit `409e514` — koşumdan **önce**.
**Betik:** `scratchpad/stop_mesafesi.py` · ham çıktı `scratchpad/stop_mesafesi_sonuc.txt`
**Kapsam sayımı:** `scratchpad/stop_kapsam_sayim.py` (ön-kayıttan önce, yalnız tetik sayar).

### Kapsam — `oi24` bacağı ÖLÇÜLEMEZ, bu koşumdan ÖNCE sayıldı

```
perp_seri OI olan sembol                  153   (klines 566)
A_funding tetigi, OI penceresi icinde      64   ayri gun 23   <- UST SINIR
```

`A+B ⊂ A_funding`, yani gerçek A+B bundan da küçük. **Ölçülen şey A+B'nin
FUNDING BACAĞI'dır, tam A+B değil.** Aynı kısıt bir kez daha kayıtlı
(*"oi24 bacağı ölçülemedi"*, satır 123).

### Kollar (ön-kayıtlı dördü, `gainer_stop.py`'nin kümesi — yeni eşik icat YOK)

`A` (mevcut) · `1.5x` · `2.5x` · `4.0x` ATR. Merdiven **monoton** —
betiğin `sinama()`'sı bunu koşumdan önce doğrular, düşerse çalışmayı reddeder.

### `A_funding` — N=4.343 işlem · 653 gün · 419 sembol (en sık 5 sembol payı %5)

```
kol      stop%     net%          R    stop-ol%   hedef%    saat
A         4,55   +0,074    -0,0092       63,4     28,7     19,8
1.5x      5,53   +0,016    +0,0011       58,4     32,1     22,6
2.5x      9,22   +0,219    +0,0235       42,2     39,9     32,0
4.0x     14,74   +0,304    +0,0242       26,8     44,0     40,2
```

| eşleşmiş fark (kol − A) | **R** (birincil) | `net%` (ikincil) |
|---|---|---|
| `1.5x` | +0,0068 · t=+0,49 · MDE 0,028 → göremiyoruz | −0,034 · t=−0,57 → göremiyoruz |
| `2.5x` | +0,0518 · **t=+1,98** · MDE 0,052 → göremiyoruz | **+0,329 · t=+2,43 → GÖRÜLÜR** |
| `4.0x` | +0,0577 · t=+1,86 · MDE 0,062 → göremiyoruz | **+0,453 · t=+2,55 → GÖRÜLÜR** |

**Permütasyon** (işaret-çevirme, gün bazında, 2.000 tur): `max|t| = 1,98` → **p = 0,090**.

### 🔴 HÜKÜM: **K1 DÜŞTÜ** — kod DEĞİŞMEDİ

Hiçbir varyant `R` üzerinde `t ≥ +2,0`'a ulaşmadı ve permütasyon `p = 0,090 > 0,05`.
Ölçüt metni sonuç görüldükten sonra **değiştirilmedi**; K2/K3/K4 uygulanmadı.

⚠️ `2.5x` **t=+1,98** ile eşiğin **kılpayı altında** kaldı ve MDE'yle başa baş
(+0,0518 vs 0,0522). Bu *"etki yok"* değil, **"göremiyoruz"**.

### ⭐ ASIMETRİ İDDİASI ÇÜRÜTÜLDÜ — ön-kayıtlı yorum kuralıyla

Kayıtlı iddia: A-stop, A+B'nin ham kenarının **%65'ini** yiyor; MA50+ucuz'da **%0**
→ *"A+B'nin stopu kapısına uymuyor."* Aynı tarama iki kapıda da koşturuldu:

```
                  A_funding    B_ma50ucuz
R    1.5x           +0,0068       +0,0373      AYNI yon
R    2.5x           +0,0518       +0,0530      AYNI yon
R    4.0x           +0,0577       +0,0549      AYNI yon
net% 1.5x           -0,0341       -0,0035      AYNI yon
net% 2.5x           +0,3288       +0,0890      AYNI yon
net% 4.0x           +0,4528       +0,0670      AYNI yon
```

**Altı karşılaştırmanın altısı da aynı yön.** Ön-kayıtlı yorum kuralı gereği:
**asimetri DESTEKLENMEDİ.** Dahası ters yönde — `R` ölçütünü geçen kol
*"stopu kapısına uyan"* denen `B_ma50ucuz`'da çıktı (`1.5x` t=+2,26 · `2.5x`
t=+2,04 · permütasyon **p=0,048**). Birincil evren o değildi, hüküm oraya
**taşınmadı** (en iyi hücre seçilmez).

### 🔑 MEKANİZMA — stop mutlak olarak dar DEĞİL, **%10 HEDEFE GÖRE** dar

Ön-kayıtlı ikincil kol (hedef = 2×risk, yani R ölçeği korunur) tabloyu **tersine
çeviriyor**:

```
A_funding, hedef 2R:   A +0,0203   1.5x +0,0170   2.5x +0,0179   4.0x +0,0127
A_funding, hedef %10:  A -0,0092   1.5x +0,0011   2.5x +0,0235   4.0x +0,0242
```

**Hedef stopla birlikte ölçeklendiğinde `A` EN İYİ kol.** Genişletmenin kazancı
yalnız **sabit %10 hedefle** var. Yani sorun stopun kendisi değil,
**dar stop ile uzak sabit hedefin uyuşmazlığı**: `A` kolunda işlemlerin
**%63,4'ü** hedefe hiç yaklaşamadan stop oluyor.

⚠️ Bu **betimleyici** bir gözlemdir (ikincil kol, ön-kayıtta *"hüküm taşımaz"*
diye ilan edildi). Kural adayı olması için **kendi ön-kaydı** gerekir.
Not: sabit %10 hedefin `MA50+ucuz`'a genişletilmesinin dayanağı zaten
çürütülmüştü (`durum.md` → beşinci iş) — bu gözlem o açık soruyla **aynı yere** bakıyor.

### Akış (her kol KENDİ %2 elemesiyle — BETİMLEYİCİ, hüküm taşımaz)

```
A_funding    A=4.343   1.5x=6.611   2.5x=7.206   4.0x=7.242
B_ma50ucuz   A=4.515   1.5x=9.311   2.5x=10.347  4.0x=10.361
```

Geniş stop akışı **%52–%106 artırır** — `asgari_stop %2` kapısını daha çok aday geçer.
Bu **yol etkisi değil akış etkisi**; eşleşmiş testte kasıtlı olarak dışarıda tutuldu.

### Ön-kayıtlı yönlü tahminlerin karnesi — 4'te 3

| # | tahmin | sonuç |
|---|---|---|
| 1 | stop-olma oranı genişlikle monoton düşer, süre uzar | ✅ TUTTU (63,4→26,8 · 19,8→40,2 sa) |
| 2 | `net%`'te geniş kollar `A`'yı geçer | ✅ TUTTU (+0,33 / +0,45, t=2,43 / 2,55) |
| 3 | `R`'de geniş kollar `A`'ya **kaybeder** | ❌ **YANLIŞ** — `R` genişlikle **iyileşti** |
| 4 | asimetri tekrarlanmayacak | ✅ TUTTU (6/6 aynı yön) |

**3. tahmin neden yanlıştı:** genişlik cezasının yol kazancını yiyeceğini
söylemiştim. Aritmetik tersini gösterdi — `A`'da stop-olma **%63,4** olduğu için
kaybedilen `−1R`'ler, dar stopun kazandırdığı yüksek `R`'li galibiyetleri
(%28,7 × 2,20R) tam olarak dengeliyor. İki kol da **sıfıra yakın**; ceza vardı
ama kazanç da vardı.

### 🔴 %65 KAYDINA ŞERH

`olcumler.md` → *"A+B'nin ham kenarının %65'ini KENDİ STOPUMUZ yiyor"* (satır 245)
kaydı, **stopsuz kolu SABİT ufukta** tutup A-stop koluyla karşılaştırmıştı;
iki kolun **tutma süresi eşit değildi**. `stop_mu_sure_mu` (2026-08-26) tam bu
kusuru yakalayıp işareti **döndürmüştü**. Bu ölçüm üçüncü kanıt:

- İki kapı arasındaki **asimetri yeniden üretilemedi** (6/6 aynı yön)
- `A` ile neredeyse-stopsuz `4.0x` arasındaki `net%` farkı **0,23 puan** —
  kayıttaki 6,10 → 2,14 uçurumuna benzemiyor

**Kayıt silinmiyor** (proje kuralı), ama *"A+B'nin stopu kapısına uymuyor"*
yorumu **2 yıllık veride desteklenmiyor.**

### Sınırlar — ön-kayıtta ilan edildiği gibi

`oi24` bacağı yok · likidasyon modellenmiyor (`4.0x` gerçekte
`kaldirac_guvenlik_kirp` ile reddedilebilir) · portföy aşaması yok ·
kısmi kâr (%40 hedef) modellenmiyor · `SEYRELT=24` faz kilitler (bu soruda
saat boyutu yok, zararsız).

**Bot dosyalarına yazım: YOK.**

---

## 🔴 STOP MESAFESİ, REJİME GÖRE (2026-09-05) — **K1 DÜŞTÜ**, ama tablo değişti

**Ön-kayıt:** `ON_KAYIT_stop_rejim.md`, commit `272f62e` — koşumdan **önce**.
**Betik:** `scratchpad/stop_rejim.py` (mekanik `stop_mesafesi.py`'den **çağrılır**)
**Ham çıktı:** `scratchpad/stop_rejim_sonuc.txt`

**Kullanıcı itirazı:** *"2 yıllık veri rejim ayı rejim."*
⚠️ **Kısmen doğru:** örneklem ayı değil **NÖTR ağırlıklı** (NÖTR %77,5 · AYI %11,7
· BOĞA %10,8). Ama itirazın çekirdeği **tamamen haklı çıktı.**

⚠️ *"22 Ağustos sonrası"* **ölçülemedi** — veri 08-25'te bitiyor, mekanik 72s ileri
getiri istiyor, kullanıcı indirmeyi reddetti. Verideki BOĞA bloğu 08-21..08-25 →
o pencerede **N=4**, sayı bile verilmedi.

### `A_funding` · birincil ölçü `R` · eşleşmiş fark (kol − A)

```
rejim   N      gun   1.5x                2.5x                4.0x
BOGA    149     51   +0,0668 t+0,69      +0,2934 t+2,06 GOR   +0,2931 t+1,94
NOTR   3314    530   +0,0038 t+0,24      +0,0228 t+0,78       +0,0252 t+0,72
AYI     880     92   +0,0480 t+1,67      +0,1305 t+2,45 GOR   +0,1679 t+2,92 GOR
```

🔑 **BOĞA etkisi NÖTR'ün 12,9 KATI. AYI 5,7 katı. NÖTR düz.**
Ve NÖTR işlemlerin **%76,3'ü** — yani önceki hüküm **NÖTR'ün hükmüydü.**

### 🔴 HÜKÜM: **K1 DÜŞTÜ** — permütasyonda, tek bacakta

```
K1  aday 2.5x (+0,2934, t=+2,06)  ·  permutasyon p=0,0950  ->  DUSTU
```

Ölçüt `t ≥ +2,0` **VE** `p ≤ 0,05` idi; t geçti, permütasyon geçmedi.
**Ölçüt gevşetilmedi.** K2/K3/K4 resmen uygulanmadı.

⚠️ **Ama üçü de geçecekti** — dürüstlük gereği yazılıyor:

| # | ölçüt | değer | olurdu |
|---|---|---|---|
| K2 | B1/B2/B3'ün ≥2'sinde aynı işaret | +0,348 · +0,164 · +0,144 — **3/3** | ✅ |
| K3 | komşu hücre aynı işaret | `1.5x` +0,067 · `4.0x` +0,293 | ✅ |
| K4 | (BOĞA − NÖTR) > 0 | **+0,2706** | ✅ |

**Tek bacakta, kılpayı düştü.** `pos<0.25` ve `s_brk` ile **aynı sınıfta üçüncü aday.**

### ⭐ TETİK SEYREKLİĞİ — operasyonel olarak en önemli satır

```
BOGA:  gun payi %10,8   vs   islem payi %3,4   -> tetik UC KAT SEYREK
```

`funding ≤ −0,05` (derin negatif = kalabalık short) **boğada nadirdir.**
Botun ana SHORT kapısı, tam boğada **susuyor**. Bu, botun BOĞA'da %100 LONG'a
kayması olgusuyla aynı madalyonun yüzü.

### 🔴 KAPI ASİMETRİSİ — ama KAYITTAKİ ASİMETRİ DEĞİL

`B_ma50ucuz` (ikincil, hüküm taşımaz) **ters** desen veriyor:

```
             BOGA                NOTR                    AYI
A_funding    +0,2934 (t+2,06)    +0,0228 (t+0,78)        +0,1305 (t+2,45)
B_ma50ucuz   -0,0447 (t-0,58)    +0,0660 (t+2,18) GOR    +0,1089 (t+1,58)
```

**İki kapı ayrışıyor:** `A_funding` trendli rejimlerde (BOĞA/AYI), `B_ma50ucuz`
NÖTR'de genişlemeden fayda görüyor — BOĞA'da işareti **dönüyor**.

⚠️ **DÜZELTME — kendi önceki cümlemi kısıtlıyorum.** Aynı gün *"altı
karşılaştırmanın altısı da aynı yön → asimetri desteklenmedi"* yazmıştım.
O cümle **havuzlanmış örneklem için doğru**, ama soruyu kapatır gibi sunuldu.
Rejim kırılımında iki kapı **gerçekten ayrışıyor**. Kayıttaki iddia
(*"A+B'nin stopu kapısına uymuyor"*, koşulsuz) hâlâ yeniden üretilemiyor;
ama *"iki kapı aynı davranır"* demek de yanlışmış.

### 🔴 2R HEDEF BULGUSU **YALNIZ NÖTR'DE** GEÇERLİYMİŞ

Önceki koşumun en ilgi çekici parçası şuydu: *"hedef stopla ölçeklendiğinde `A`
en iyi kol → stop dar değil, hedef uzak."* Rejime bölününce:

```
hedef 2R, A_funding      A         1.5x      2.5x      4.0x
NOTR                  +0,0579   +0,0529   +0,0441   +0,0372   <- A EN IYI
BOGA                  -0,2983   -0,2680   -0,2015   -0,1569   <- GENIS daha iyi
AYI                   -0,0673   -0,0699   -0,0438   -0,0507   <- GENIS daha iyi
```

**O bulgu bir NÖTR olgusuydu.** Trendli rejimlerde stop, hedef orantılı olsa
bile **gerçekten dar**. Önceki notun *"sorun stop değil hedef"* çerçevesi
**NÖTR'e daraltılmalı.**

### Ön-kayıtlı yönlü tahminlerin karnesi — 4'te **1** 🔴

| # | tahmin | sonuç |
|---|---|---|
| 1 | BOĞA'da `A_funding` tetiği oransal olarak daha az | ✅ **TUTTU** (%10,8 gün vs %3,4 işlem) |
| 2 | yön iki rejimde de aynı → K4 düşecek, rejim bu soruyu değiştirmiyor | ❌ **YANLIŞ** — yön aynı ama **büyüklük 13 kat**; K4 geçecekti |
| 3 | MDE etkinin 2 katından büyük olacak → "göremiyoruz" | ❌ **YANLIŞ** — birincil hücrede MDE 0,2845 < etki 0,2934 |
| 4 | 2R bulgusu BOĞA'da da duracak (`A` en iyi kalacak) | ❌ **YANLIŞ** — yalnız NÖTR'de duruyor |

**Bu tur kötü geçti ve aynen yazılıyor.** Ortak kök: üçünde de *"etki her yerde
aynı büyüklükte"* varsaydım. Rejim büyüklüğü değiştiriyor, ve tam da kullanıcının
söylediği yönde. **Üst üste iki 3/3'ten sonra 1/4.**

### 🔴 ÇOKLU KARŞILAŞTIRMA — bu tablodan hücre seçilmez

3 rejim × 3 kol × 2 ölçü × 2 kapı = **36 hücre.** Permütasyon **yalnız
`A_funding` × BOĞA × `R`** için koşturuldu (3 karşılaştırma). AYI'nın `t=+2,92`'si
ve `B_ma50ucuz`/NÖTR'ün `t=+2,46`'sı **düzeltilmemiştir** ve bulgu sayılmaz.
*"Tabloya bakıp en iyi rejim-kol hücresini kural yapmak"* bu projede reddedilmiş
davranıştır.

### Sınırlar

BOĞA hücresi **N=149 · 51 gün · 88 sembol** — küçük. B1 bloğu yalnız N=15.
Likidasyon yok · portföy aşaması yok · kısmi kâr yok · `oi24` bacağı yok ·
kullanıcının epizodu (08-21…) **ölçülemedi**.

**Veri indirme: YOK. Bot dosyalarına yazım: YOK.**

---

## ⛔ BOĞA HOLDOUT — **KOŞMADI**, kendi geçerlilik kapımda durdu (2026-09-05)

**Ön-kayıt:** `ON_KAYIT_boga_holdout.md`, commit `5144a45` (+ şerh `6843bd8`).
**Betik:** `scratchpad/boga_holdout.py` · **hüküm YOK — ölçüm hiç çalışmadı.**

### Neden bu ölçüm denendi

Kullanıcı *"21'inden bugüne rejim boğa, elimizde veri olması lazım"* dedi ve
**haklıydı**. İki kez yanlış söylemişim:

| iddiam | gerçek |
|---|---|
| *"22 Ağustos sonrası ölçülemez"* | `perp_seri/*_kline.json` **09-05'e kadar var** |
| *"`oi24` bacağı ölçülemez"* | `radar_archive`'da **`oi24` zaten var** |

Kapsam sayıldı: **55 bağımsız olay · 13 gün · 27 sembol** (tam A+B: 25 olay).

### Zorunlu sınama üç kez koştu, üçünde de kapı kapalı kaldı

Ön-kayıt: *"zaman ofseti kanıtlanmadan koşulmaz — `last1` korelasyonu ≥ 0,80."*

```
sinama surumu                              -4       -3       -2
1) saatlik bar kapanis getirisi         +0,215   +0,511   +0,013
2) 5dk izgarada kayan 60dk getiri       -0,063   +0,738   -0,055
3) radar.py:117 TAM tanimi              -0,017   +0,745   -0,031
```

🔑 **Ofset sorusu KESİN olarak cevaplandı: −3 doğru.** Komşu ofsetler sıfır
civarında; yanlış hizalama olsaydı bu tablo çıkmazdı.
🔴 **Ama eşik 0,80'e hiçbir sürümde ulaşılmadı.**

### Tavanın sebebi bulundu — ve GİDERİLEMEZ

```
radar_archive 'ts' bir DONGU damgasidir:
  ayni dakika damgasini paylasan sembol -> medyan 42 · maks 50
```

Radar ~400 sembolü bir döngüde tarıyor; her sembolün **canlı fiyatı farklı bir
anda** çekiliyor ama hepsi **aynı `ts`**'yi alıyor. Sembol başına çekim anı
**hiç kaydedilmemiş.** Dolayısıyla dakika düzeyinde hizalama yapısal olarak
imkânsız ve 0,745 bu verinin **tavanı.**

### 🔴 NEDEN EŞİĞİ ÜÇÜNCÜ KEZ DEĞİŞTİRMEDİM

Sınamayı **iki kez** düzelttim (ikisi de meşruydu: ilkinde yanlış büyüklüğü
ölçüyordum, ikincisinde `last1`'in tanımını kaynaktan okumamıştım). Üçüncü bir
ayar — eşiği düşürmek ya da testi *"ofset ayrımı"*na çevirmek — mantıken
savunulabilir olsa bile, **geçene kadar ayarlamaktan ayırt edilemez.**

Bu projenin tüm disiplini bunu yapmamaya dayanıyor. **Ölçüm koşmadı ve
koşturulmadı.** Karar kullanıcınındır.

### Elde ne var, ne yok

| | |
|---|---|
| ✅ | veri gerçekten var (55 olay / 13 gün), betik hazır ve doğrulanmış |
| ✅ | zaman hizalaması **−3 olarak kanıtlandı** |
| ⛔ | ön-kayıtlı geçerlilik kapısı açılmadı → **hiçbir sayı üretilmedi** |
| ⚠️ | güç zaten kötüydü: MDE ~0,56 vs beklenen etki ~0,29 |

**Veri indirme: YOK. Bot dosyalarına yazım: YOK.**

---

## 🔴 MA50+UCUZ KAPISI, BOĞA PENCERESİNDE — **DÜŞTÜ** (2026-09-05)

**Ön-kayıt:** `ON_KAYIT_ma50_boga.md`, commit `42e6452` — koşumdan **önce**.
**Betik:** `scratchpad/ma50_boga.py` · ham çıktı `scratchpad/ma50_boga_sonuc.txt`
**Kapsam sayımı:** `scratchpad/ma50_kapsam_sayim.py` (ön-kayıttan önce).

**Kullanıcı sorusu:** *"MA50'yi en son ölçtüğün veriyle ölç, 21'i sonrası.
Bu ölçümü yapmış mıydın?"* → **Hayır, yapılmamıştı.**

### Bu kapı neden ölçülebildi, fonlama kapısı ölçülemedi

MA50+ucuz'un **iki girdisi de yalnızca mumdan** hesaplanır
(`fiyat ≤ $0,07` · `ma50_mesafe ≥ %3,72`) → `radar_archive`'a ihtiyaç yok →
önceki ölçümü durduran **döngü-damgası hizalama sorunu bu kapıda geçersiz.**
Arşiv yalnız fonlama maliyeti için kullanıldı ve **S2 sınaması bunu doğruladı**
(döngü-içi `|Δfunding|` medyanı **0,000000** — damga bulanıklığı fonlamayı bozmuyor).

### Sonuç — üç kolun ÜÇÜ DE negatif

```
kol        N     gun  sembol   net%      R       stop-ol%  hedef%
KAPI      235    12     79    -0,586   -0,1895     75        19
K_dar     540    13     83    -0,663   -0,2639     74        13
K_genis  1223    13    150    -0,757   -0,2563     76        14
```

`K_dar` = ucuz ama MA50'ye yakın · `K_geniş` = tüm evren. Fonlama **dahil**
(işlem başı −0,0087 puan — ihmal edilebilir).

| # | ölçüt | değer | sonuç |
|---|---|---|---|
| **K1** | kapı − `K_dar` (net%) | +0,5461 · t=+1,15 · MDE 0,9501 | ❌ **DÜŞTÜ** (+ göremiyoruz) |
| **K2** | kapının **mutlak** net%'i | −0,2929 (gün ort) · t=−0,86 | ❌ **DÜŞTÜ** |
| **K3** | `K_geniş`'e karşı aynı işaret | +0,0384 · t=+0,07 | ✅ (ama sıfıra eşit) |
| **K4** | güç | 0,5461 < MDE 0,9501 | ❌ **GÖREMİYORUZ** |

**SONUÇ: DÜŞTÜ.**

### 🔑 ASIL BULGU — zarar KAPIDAN değil, BOĞADA SHORT OLMAKTAN geliyor

Kapı **en az kötü** kolu seçiyor (−0,586 vs −0,663 vs −0,757) ama **hepsi
zararda.** Sıralama doğru, seviye yanlış. Bir kapı yalnızca *"daha az kaybettiren"*
işlemler seçiyorsa kapı sorunu çözmüyor — **yön** sorunu var.

⚠️ Ve config'in kendi özel uyarısı (*"boğada ucuz coinler öne geçebilir"*)
**doğrulanmadı**: ucuz coinler (`K_dar` −0,663) geniş evrenden (`K_geniş` −0,757)
**daha kötü değil, biraz daha iyi.** Yani mekanizma *"ucuzlar öne geçti"* değil,
*"boğada short kaybettirir"*.

### 🔴 KODUN VADESİ GEÇMİŞ TALİMATI KAPANDI

`kripto-config.json → _ma50_kapisi_not`: *"rejim değişince ilişki DÖNEBİLİR…
yeniden ölçülmeden bırakılmamalı."* Boğaya 08-21'de girildi, şimdi ölçüldü.
**Talimat ifa edildi.** İlişki dönmedi — zaten kapı BOĞA'da **kapalı**.

### ⭐ VE BOTUN MEVCUT KİLİDİ DOĞRULANDI

[testbot.py:484](testbot.py#L484): her iki SHORT kapısı da
`rejim_ad in ("AYI","NOTR")` koşuluna bağlı → **BOĞA'da ikisi de KAPALI.**
Bu ölçüm bir **karşı-olgudur**: *"kapı açık olsaydı ne olurdu."*
Cevap: işlem başına **−%0,586**. **Mevcut kilit doğru çalışıyor** ve bu ölçüm
onu değiştirme değil, **doğrulama** üretti.

### 🔴 STOP GENİŞLETME BU KAPIDA ZARARLI — ve kapı-özgü olduğu kanıtlandı

(Ön-kayıtta **betimleyici** ilan edildi, geçme ölçütü yoktu — hüküm taşımaz.)

```
kol      stop%    net%       R      stop-ol%    eslesmis fark (R, kol-A)
A         3,67   -0,586   -0,1895     75
1,5x      4,76   -0,750   -0,2226     70        -0,0764  t -1,77
2,5x      7,93   -1,568   -0,2727     63        -0,1703  t -2,86  <- GORULUR
4,0x     12,69   -2,099   -0,2021     49        -0,1093  t -1,29
```

🔑 **Fonlama kapısının BOĞA'daki bulgusunun TAM TERSİ:**

```
BOGA'da 2,5x'e genislet   ->   A_funding  +0,2934      MA50+ucuz  -0,1703
```

Ve bu, 2 yıllık rejim kırılımının bu kapı için verdiği işaretle (**−0,0447**)
**aynı yönde, tutulmuş veride.** Yani *"boğada stopu genişlet"* **genel bir kural
değildir** — kapıya bağlıdır ve bot geneline uygulanırsa MA50 kapısını **bozar.**

### Ön-kayıtlı yönlü tahminlerin karnesi — **4'te 4** ✅

| # | tahmin | sonuç |
|---|---|---|
| 1 | kapının mutlak net%'i **negatif** çıkacak | ✅ TUTTU (−0,586) |
| 2 | `K_dar` de negatif çıkacak → zarar **yönden** gelecek | ✅ TUTTU (üç kol da negatif) |
| 3 | kapı `K_dar`'ı t≥+2 ile geçemeyecek | ✅ TUTTU (t=+1,15) |
| 4 | stop genişletme burada fonlama kapısından **zayıf** kalacak | ✅ TUTTU — zayıf değil, **zararlı** |

(Bir önceki tur 4'te 1'di; bu tur 4'te 4.)

### Sınırlar

12 gün · 151 sembol (perp_seri kapsamı) · likidasyon yok · portföy aşaması yok ·
kısmi kâr yok · fonlama arşivden **yaklaşıkla** alındı (S2 ile doğrulandı) ·
tek BOĞA epizodu.

**Veri indirme: YOK. Bot dosyalarına yazım: YOK.**

---

## 🔴 BOĞA PENCERESİ, TAZE VERİYLE — iki kapı birden (2026-09-05)

**Ön-kayıtlar:** `ON_KAYIT_boga_holdout.md` (`5144a45`) · `ON_KAYIT_ma50_boga.md`
(`42e6452`) — **ikisi de koşumdan önce**, ölçütleri değiştirilmedi.
**Betik:** `scratchpad/boga_taze.py` · ham çıktı `scratchpad/boga_taze_sonuc.txt`
**İndirici:** `scratchpad/taze_veri_indir.py` (567 sembol · 0 hata · 27,5 dk)

**Veri:** `klines_1h_uzun`+`taze_1h` · `funding_gecmis`+`taze_funding`,
**bellekte** birleştirildi. Hiçbir arşive yazılmadı; eski dosyalar sağlam
(BTC hâlâ 08-25'te bitiyor). Pencere **08-21 → 09-02** (72s ileri getiri kesmesi).

🔑 **`radar_archive` HİÇ kullanılmadı** → önceki ölçümü durduran döngü-damgası
hizalama kapısı **aşılmadı, konusuz kaldı.** Kapı artık 2 yıllık ölçümün
**birebir aynı yöntemiyle** tetikleniyor.
Sınamalar: S1 merdiven ✅ · S2 birleştirme sürekliliği **0/120 boşluk** ✅ ·
S3 fonlama birimi medyan `|r|`=0,0050 ✅

### HÜKÜM 1 — `A_funding` · N=177 · 13 gün · 63 sembol

```
kol      stop%    net%       R      stop-ol%  hedef%
A         5,03   -0,692   -0,2452     68,4     22,6
1.5x      6,09   -0,744   -0,1857     60,5     25,4
2.5x     10,14   -0,239   -0,1059     44,6     33,9
4.0x     16,23   -0,523   -0,0890     30,5     37,3

eslesmis fark (kol - A), R:
1.5x   +0,0814  t+1,41  MDE 0,1153   6/13 gun   binom p 0,7095
2.5x   +0,1771  t+2,14  MDE 0,1654  10/13 gun   binom p 0,0461
4.0x   +0,1892  t+2,15  MDE 0,1761  10/13 gun   binom p 0,0461
```

| # | ölçüt | sonuç |
|---|---|---|
| **K1** 🔴 birincil · gün işaret testi | 10/13 · p=**0,0461** | ✅ **GEÇTİ** |
| **K2** ortalama fark > 0 | +0,1771 | ✅ GEÇTİ |
| **K3** komşu `4.0x` > 0 | +0,1892 | ✅ GEÇTİ |
| **K4** tam A+B (N=34) işareti ters değil | **−0,1737** (t=−0,88) | ❌ **DÜŞTÜ** |

**SONUÇ 1: DÜŞTÜ.** Ön-kayıt bölüm 7 harfiyen: *GEÇTİ = K1+K2+K3+K4* ·
*ZAYIF = K2+K3 var, **K1 düştü*** · *aksi DÜŞTÜ*. K1 geçip K4 düşen bileşim
ZAYIF tanımına girmiyor → **DÜŞTÜ**. Metin yorumlanmadı, uygulandı (D/9).

#### 🔴 BETİĞİM YANLIŞ ETİKET BASTI — ve hata LEHE yöndeydi

İlk sürüm bu durumda **"ZAYIF (K1 düştü)"** yazdı: (a) K1 düşmemişti, (b) ZAYIF
kategorisi bu bileşimi kapsamıyordu. Düzeltildi, yeniden koşuldu, sonuç **DÜŞTÜ**.
*Bir betiğin hüküm satırı, ön-kaydın metnine karşı denetlenmelidir.*

#### 🔴 VE K4'ÜN KENDİSİ BENİM TASARIM HATAM

Ön-kayıt bölüm 9, tahmin 4: *"A+B alt kümesi (N=25) **hiçbir şey
söyleyemeyecek** — MDE her makul etkiden büyük."* Tahmin **tuttu** (t=−0,88).
Ama K4'ü **tam o büyüklük üzerine** kurmuştum: gürültü düzeyindeki bir işaret
tesadüfen negatif çıktı ve hükmü batırdı.
**Ders: bilgisiz kalacağını ÖNGÖRDÜĞÜN bir büyüklük geçme ölçütü yapılmaz.**
Bu ölçümün hükmü yine de değişmez — kural kuraldır.

#### ⭐ Ama kanıt BİRİKTİ: iki bağımsız pencere aynı şeyi söylüyor

```
2 yillik BOGA dilimi (klines_1h_uzun)   +0,2934   t+2,06   perm p 0,095   K1 DUSTU
TAZE holdout       (08-21..09-02)       +0,1771   t+2,14   10/13 gun      K1 GECTI
```

Farklı pencere, farklı veri kaynağı, **aynı yön ve benzer büyüklük**; ve
holdout'un **birincil işaret testi geçti.** Resmî hüküm DÜŞTÜ, ama bu aday
oturumun en çok desteklenen adayı hâline geldi.

### HÜKÜM 2 — `MA50+ucuz` · N=580 · 13 gün · 253 sembol → **GEÇTİ**

```
kol        N      net%       R      stop-ol%
MA50      580   -0,193   -0,1123     71,7
K_dar    1476   -0,790   -0,3257     75,7    (ucuz ama MA50'ye yakin)
K_genis  3387   -0,771   -0,3080     76,8
```

| # | ölçüt | değer | sonuç |
|---|---|---|---|
| **K1** | kapı − `K_dar` (net%) | **+1,0455 · t=+2,14** | ✅ GEÇTİ |
| **K2** | mutlak net% | **gün-ort +0,1481 (t=+0,44)** · **işlem-ort −0,1929** | ⚠️ GEÇTİ ama **KIRILGAN** |
| **K3** | `K_geniş`'e karşı | +0,9059 · t=+1,95 | ✅ GEÇTİ |
| **K4** | güç | 1,0455 ≥ MDE 0,9786 | ✅ **GÖRÜLÜR** |

**SONUÇ 2: GEÇTİ** — ama K2 üzerinde **ciddi çekince**:

🔴 **Gün-ortalaması ile işlem-ortalamasının İŞARETLERİ TERS** (+0,148 vs −0,193).
Gün-ortalaması günleri eşit tartar; çok işlemli kötü günler işlem-ortalamasını
aşağı çekiyor. Üstelik gün-ortalamasının t'si **+0,44** — sıfırdan
ayrılmıyor. **Yani "kapı kâr ediyor" KANITLANMADI.** Kanıtlanan tek şey K1:
kapı, ucuz-coin kontrolünden **~1 puan ayrışıyor** ve bu görülür.

#### 🔴 BU KOŞUM ÖNCEKİNİ TERSİNE ÇEVİRDİ — ikisi de yazılıyor

| | 151 sembol (`perp_seri`) | **566 sembol (taze)** |
|---|---|---|
| N | 235 | **580** |
| kapı net% (işlem-ort) | −0,586 | −0,193 |
| K1 | +0,5461 · t=1,15 ❌ | **+1,0455 · t=2,14 ✅** |
| K2 (gün-ort) | −0,2929 ❌ | **+0,1481 ✅** |
| K4 güç | göremiyoruz | **GÖRÜLÜR** |
| **SONUÇ** | **DÜŞTÜ** | **GEÇTİ** |

Sebep: `perp_seri`'nin 151 sembolü **seçilmiş** bir alt kümedir (radarın izlediği
semboller); 566'lık küme **tam evren**. Geniş olan daha iyi kestirimdir —
ama ön-kayıt şerhi *"ikisi de raporlanır"* diyordu ve raporlanıyor.

#### ⚠️ ve ÖNCEKİ CÜMLEMİ ZAYIFLATIYORUM

*"MA50'de stop genişletmek ZARARLI, görülür (t=−2,86)"* demiştim. Geniş örneklemde:

```
1.5x -0,0415 t-1,08 | 2.5x -0,0881 t-1,51 (MDE 0,1168) | 4.0x -0,0737 t-1,11
```

**Hiçbiri görülür değil.** İşaret hâlâ negatif ve hâlâ `A_funding`'in tersi
(+0,1771 **görülür** vs −0,0881 **görülmez**), ama *"zararlı"* iddiası
**kanıtlanmış değil.** Kapıya-bağlılık gözlemi ayakta, kanıt gücü düştü.

### Ön-kayıtlı yönlü tahminlerin karnesi — **4'te 4** ✅ (holdout)

| # | tahmin | sonuç |
|---|---|---|
| 1 | ortalama farkın işareti pozitif | ✅ +0,1771 |
| 2 | büyüklük +0,29'dan **küçük** olacak | ✅ +0,1771 < +0,2934 |
| 3 | stop-olma genişlikle monoton düşecek | ✅ 68,4→60,5→44,6→30,5 |
| 4 | A+B alt kümesi hiçbir şey söyleyemeyecek | ✅ t=−0,88 (ve K4 tasarım hatamı açığa çıkardı) |

### Sınırlar

13 gün · tek BOĞA epizodu · likidasyon yok · portföy aşaması yok · kısmi kâr yok ·
A+B alt kümesi yalnız `perp_seri` OI'si olan 153 sembolden.
**Bot dosyalarına yazım: YOK · mevcut arşivlere yazım: YOK.**

---

## 🔴 UCUZ yerine PAHALI — **DÜŞTÜ**, ve orijinal bulguyu şüpheye düşürdü (2026-09-05)

**Ön-kayıt:** `ON_KAYIT_pahali_ayna.md`, commit `5f213c2` — koşumdan **önce**.
**Betikler:** `scratchpad/pahali_kapsam.py` (eşik/kapsam, ön-kayıttan önce) ·
`pahali_ayna.py` (hüküm) · `pahali_mutlak.py` (post-hoc, **bulgu değil**).
**Kullanıcı sorusu:** *"ma50 ucuz yerine pahalı olsa ne olur"*

### Eşik uydurulmadı — ve yolda bir olgu çıktı

```
2 yil fiyat dilimleri:  %20 $0,0318 · %50 $0,2236 · %80 $2,3610
```

🔴 **Config'in "$0,07 = %20 dilim" gerekçesi bu evrende TUTMUYOR** — gerçek %20
dilimi **$0,0318**. Kapı kayıtlı gerekçesinden **daha gevşek** (~%28-30 dilimi).
Config'in *"ham fiyat eşiği zamanla kayar"* uyarısı **doğrulandı.**
Ayna eşiği **$2,3610** (=%80 dilim) buradan geldi, tarama yapılmadı.

### Sonuç

```
                UCUZ                  PAHALI              PAHALI-UCUZ
tum pencere  N=16130  -0,152%    N=5914  -0,028%
NOTR         N=11789  -0,020%    N=3924  +0,208%       +0,0777  t +0,45
AYI          N= 2501  -0,183%    N= 562  +0,217%       +0,5210  t +1,24
BOGA         N= 1840  -0,953%    N=1428  -0,770%       -0,0259  t -0,05
taze pencere N=  553  -0,153%    N= 135  -0,767%       -0,3279  t -0,65
```

| # | ölçüt | değer | sonuç |
|---|---|---|---|
| **K1** | BOĞA'da `PAHALI−UCUZ` > 0 · t ≥ +2,0 | −0,0259 · t=−0,05 | ❌ **DÜŞTÜ** |
| **K2** | taze pencerede aynı işaret | −0,3279 | ✅ GEÇTİ |
| **K3** | güç, fark ≥ MDE | 0,026 vs **1,019** | ❌ **GÖREMİYORUZ** |

**SONUÇ: DÜŞTÜ.** BOĞA'da iki kol arasındaki fark **yok denecek kadar küçük**
(−0,026) ve MDE'nin **kırkta biri**.

### 🔴 ÖN-KAYITTA SÖZ VERİLEN SONUÇ DOĞDU

Tahmin 1'e şunu yazmıştım: *"NÖTR/AYI'da UCUZ önde olacak — orijinal yön avının
bulgusu (fiyat log10 +1,57) yeniden üretilmeli. **Üretilemezse o bulgu da
şüpheli demektir.**"*

**Üretilemedi — üstelik TERSİ çıktı:** NÖTR'de `PAHALI−UCUZ` **+0,078**,
AYI'da **+0,521**. Yani iki rejimde de **pahalı** önde.

🔴 Kendi ön-kayıtlı kuralım gereği: **MA50+ucuz kapısının fiyat bacağını doğuran
bulgu** (*"ucuz coinler BTC'nin altında kalır"*, 2026-08-10 yön avı)
**2 yıllık veride yeniden üretilemedi ve ŞÜPHELİDİR.**

### ⭐ POST-HOC — asıl cevap burada (BULGU DEĞİL, ön-kayıtsız)

Mutlak kârlılık, gün-kümeli (`pahali_mutlak.py`):

```
kol     rejim      N     gun     net%     t_gun     MDE      gorulur mu
UCUZ    NOTR   11789    599   +0,1050   +0,97   0,2166    goremiyoruz
UCUZ    AYI     2501     96   -0,1949   -0,94   0,4138    goremiyoruz
UCUZ    BOGA    1840     95   -0,2028   -0,56   0,7201    goremiyoruz
PAHALI  NOTR    3924    573   +0,1827   +1,36   0,2695    goremiyoruz
PAHALI  AYI      562     89   +0,3261   +0,89   0,7322    goremiyoruz
PAHALI  BOGA    1428     85   -0,2287   -0,63   0,7204    goremiyoruz
```

🔑 **ALTI HÜCRENİN ALTISI DA GÖRÜLEMİYOR.** En büyük mutlak t **1,36**.
**Fiyat seviyesi hiçbir rejimde ölçülebilir bilgi taşımıyor** — ne ucuz ne pahalı.

⚠️ Bu, kapının **fiyat bacağının boş** olduğunu düşündürüyor; geriye yalnız
**MA50 bacağı** kalır. Ama bu **ayrı bir ön-kayıt** ister — bugün bu pencerede
onlarca hücreye bakıldı, buradan kural çıkmaz.

⚠️ **Gün-ortalaması ile işlem-ortalaması bu tabloda da ayrışıyor**
(`UCUZ/NOTR`: işlem −0,020 vs gün +0,105). Bu veri setinde iki toplama yöntemi
sistematik olarak farklı sonuç veriyor — tek başına bir uyarıdır.

### Ön-kayıtlı yönlü tahminlerin karnesi — **4'te 1 (+1 kısmi)**

| # | tahmin | sonuç |
|---|---|---|
| 1 | NÖTR/AYI'da UCUZ önde (orijinal bulgu yeniden üretilir) | ❌ **YANLIŞ** — tersi çıktı |
| 2 | BOĞA'da işaret döner (pahalı önde), fark küçük | ❌ işaret dönmedi (−0,026); "küçük" kısmı doğru |
| 3 | iki kol da BOĞA'da mutlak negatif | ✅ TUTTU (−0,953 · −0,770) |
| 4 | pahalı kolun stopu belirgin dar, elemesi ağır | ⚠️ **kısmi** — eleme ağır (%90 vs %82) ama stop yalnız %8 dar (2,96 vs 3,22) |

### Sınırlar

Fiyat eşikleri **sabit dolar** (2 yılda kayar — bu ölçümün kendi bulgusu) ·
BOĞA 95 gün · likidasyon yok · portföy aşaması yok · kısmi kâr yok.

**Arşive yazım: YOK. Bot dosyalarına yazım: YOK.**

---

## 🔬 BOT NEDEN BÜYÜK COİNLERE İŞLEM ALMIYOR? — BETİMLEYİCİ teşhis (2026-09-05)

> 🔴 **HÜKÜM YOK.** Ön-kayıt yok, geçme ölçütü yok, kural çıkmaz. Bu tablo yalnız
> **mekanizmayı** gösterir. Kullanıcı sorusu: *"bot neden büyük coinlere işlem almıyor"*.
> Betikler: `scratchpad/neden_kucuk.py` · ham çıktı `neden_kucuk_sonuc.txt`.

### Önce yanlış cevabı eleyelim: büyükler evrenin İÇİNDE

`testbot.py:1400` → `evren.binance_pool("fapi", min_vol=3)[:150]`, ve
`binance_pool` **hacme göre azalan** sıralıyor. Yani havuz = **en yüksek hacimli
150 perp**; BTC/ETH/SOL **taranıyor**.

```
fiyat kovasi     havuzda    pay%
< $0,01           11.659    9,4%
$0,01-0,07        22.437   18,1%
$0,07-1           40.567   32,7%
$1-10             15.672   12,6%
$10-100           11.698    9,4%
>= $100           22.015   17,7%      <- havuzun altida biri
```

**Havuzun %40'ı $1 üstü.** Sorun tarama değil, **kapılar.**

### DÖRT AYRI KAPI, DÖRDÜ DE AYNI YÖNE ELİYOR

```
fiyat kovasi    A_funding   MA50 kapisi   ATR/fiyat   asgari_stop %2'yi gecen
< $0,01            9,11%       21,80%       2,42%            19,9%
$0,01-0,07        13,20%       31,92%       3,31%            23,4%
$0,07-1            4,06%        0,00%       1,98%            24,2%
$1-10              2,75%        0,00%       1,43%            16,6%
$10-100            2,11%        0,00%       1,07%            13,2%
>= $100            0,40%        0,00%       0,58%             2,9%
```

| # | kapı | büyüklerde etkisi |
|---|---|---|
| **1** | `MA50+ucuz`: `fiyat ≤ $0,07` | **%0,00** — mekanik, havuzun **%72'sini** tanım gereği dışlıyor |
| **2** | `asgari_stop_pct = %2` | ≥$100 coinlerin yalnız **%2,9'u** geçiyor (ucuzlarda %23) — **8 kat** |
| **3** | `A_funding`: `funding ≤ −0,05` | ≥$100'de **%0,40**, ucuzda **%13,20** — **33 kat** |
| **4** | `skor ≥ 45` | büyük-cap **%0,3**, küçük-cap **%6,1** — **20 kat** |

### Skorun neden büyükleri elediği — `radar_archive`

```
mcap               N    skor ort   skor>=45%   vol_x med   oi24 med
< $100M        57.046      17,6        6,1%       0,60       +0,60
$100M-1Mr      45.203      13,0        2,9%       0,70       +0,06
$1-10Mr        76.170       8,2        0,3%       0,80       -0,21
>= $10Mr       39.554       7,6        0,3%       0,80       -0,12
```

`vol_x` neredeyse **aynı** (0,60 vs 0,80) ama `oi24` medyanı **+0,60 → −0,12**.
Skorun **%41'i `s_oi`** ([radar.py:123](radar.py#L123)) → büyük coinlerin açık
pozisyonu sıçramadığı için skor doğal olarak küçük kalıyor.

### 🔑 KÖK NEDEN: OYNAKLIK

```
ATR / fiyat (medyan):   ucuz %3,31   ·   >= $100  %0,58     -> 5,7 KAT
A-stop genisligi (med): ucuz %1,18   ·   >= $100  %0,42
```

Botun stopu en fazla `1,5 × ATR` kadar geniş olabiliyor. ≥$100 bir coinde bu
**%0,87** eder — `asgari_stop %2` eşiğinin **altında**. Yani büyük bir coin
diğer üç kapıyı geçse bile **stop kapısında ölür.**

### ⚖️ VE BU BİR HATA DEĞİL — maliyet tarafı bunu destekliyor

Gidiş-dönüş maliyet **%0,13**. Bir ATR'ye oranla:

```
ucuz coin :  0,13 / 3,31  =  hareketin %3,9'u
>= $100   :  0,13 / 0,58  =  hareketin %22,4'u      -> 5,7 KAT agir
```

Aynı mekanikle büyük coin işlemek **maliyet-baskın** olurdu. Yani dört kapının
ürettiği sonuç, en azından bu ölçekte, **savunulabilir.**

### Defterdeki gerçek dağılım (389 pozisyon · 152 sembol)

```
giris fiyati:  %25 $0,015  ·  medyan $0,053  ·  %75 $0,231  ·  %90 $1,61
>= $1  : 47 islem (%12,1)   ·   >= $10 : 7 (%1,8)   ·   >= $100 : 1 (%0,3)
```

Bot büyükleri **tamamen** dışlamıyor — ama medyanı **$0,053**.

### 🔴 Ne söylüyor, ne söylemiyor

**Söylüyor:** bot yapısı gereği bir **küçük-cap botudur**, ve bu tek bir tasarım
kararından değil **dört ayrı eşiğin kesişiminden** doğuyor. Hiçbiri "büyükleri
eleyelim" diye konmamıştı.

**Söylemiyor:** büyük coinlerde kenar olup olmadığını. Bu ölçüm **hiç getiri
hesaplamadı.** *"Büyüklerde işlem açsak kazanır mıydık"* sorusu ayrı bir
ön-kayıt ister ve farklı bir mekanik (daha uzun ufuk / daha dar hedef) gerektirir —
çünkü mevcut mekanik onlarda **maliyet-baskın**.

**Bot dosyalarına yazım: YOK.**

---

## 🔬 GÖLGE DEFTER, BOĞA PENCERESİ — sentetik ölçümlerin CANLI kontrolü (2026-09-05)

> Kullanıcı isteği: *"22'den sonrası (boğa) için gölge deftere bak ve ölçtüğümüz
> o aralıktakileri kontrol et."*
> Betik: `scratchpad/golge_boga.py` · ham çıktı `golge_boga_sonuc.txt`.
> 🔴 **Ön-kayıt yok, hüküm yok.** Betimleyici çapraz kontrol.

**Pencere:** 2026-08-21 → 09-05 · **581 pozisyon** (1.285 kayıt, `id` ile
birleştirildi) · 16 gün.

### Kaynağa göre kırılım — `CLAUDE.md`: tek kasa rakamı yanıltır

```
kaynak                 N     toplam $     ort $   kazanan   fonlama
pump_long_tezi       424    +2.529,66     +5,97    %57,8    +97,60
onay_bekle            89    -3.125,65    -35,12    %41,6   +151,80
long_veto             60    -1.275,16    -21,25    %48,3   +198,30
stop_cok_dar           4      -174,30    -43,58    %25,0     +7,35
blowoff                4       +72,56    +18,14   %100,0     -1,23
TUMU                 581    -1.972,89     -3,40    %54,4   +453,83
```

### ⭐ BOTUN VETOLARI BOĞA'DA DOĞRU ÇALIŞMIŞ

`onay_bekle` (−3.126 $) ve `long_veto` (−1.275 $) — botun **reddettiği**
girişler. İkisi de zararda: bot bu pencerede **~4.400 $ kayıptan kaçınmış.**
Bu, `long_veto` ölçümünün (bu oturumda *"kaldırmak stop yemi işlem ekler"*)
canlı teyididir.

### 🔴 `pump_long_tezi` — ÖNCE ARTI SANDIM, YOĞUNLAŞMA ÖLÇÜLÜNCE ÇÖKTÜ

Bu tez `CANLI_ADAYI` listesinde ([golge.py:110](golge.py#L110)) → `zorla=False`,
yani **canlının bütün kapılarına uyuyor**; sonucu doğrudan canlıya taşınabilir.
Tetik: `chg24 ≥ %10` **ve** `vol_x ≥ 2,0` → LONG.

```
dilim             N   gun    toplam $    gun ort    t_gun     MDE
TUMU            652    26   +2.653,47     -7,45    -0,91    16,33
BOGA oncesi     228    11     +123,81    -13,29    -0,90    29,59
BOGA (08-21->)  424    15   +2.529,66     -3,18    -0,34    18,84
```

🔴 **Toplam artı, ama GÜN ORTALAMASI EKSİ** ve t sıfırdan ayrılmıyor.
Yoğunlaşma ölçüldü:

```
en iyi 1 gun  +1.840,14 $  -> toplamin %73'u
en iyi 2 gun  +3.364,94 $  -> toplamin %133'u
en iyi 2 gun HARIC       :  -835,28 $
en iyi 5 ISLEM           :  toplamin %62'si
artida gun               :  9 / 15
```

**İki gün ve beş işlem tüm kârı taşıyor.** Bu bir kenar değil, birkaç büyük
kazanç. `+2.530 $` rakamı tek başına okunursa **yanıltır.**

⚠️ **Bu oturumda kendi ilk okumamı düzelttim:** kaynak tablosunu görünce
*"pump tezi BOĞA'da kârlı"* diye okudum; gün-kümeli kırılım bunu **çürüttü**.

### 🔴 SHORT ÇAPRAZ KONTROLÜ YAPILAMADI — N=3

Bugünkü sentetik ölçümlerin ana iddiası *"BOĞA'da SHORT kaybettirir"* idi.
Gölge defterde bu pencerede **yalnız 3 SHORT** var (−114,83 $).
**N=3 ile doğrulama da çürütme de yapılamaz.** Betiğin bastığı *"işaret aynı"*
satırı **kanıt değildir**; burada açıkça öyle işaretleniyor.

Sebebi yapısal: bot BOĞA'da SHORT kapılarını kapatıyor
([testbot.py:484](testbot.py#L484)), gölge de reddedilen girişleri izlediği için
short akışı kuruyor.

### ⭐ KISMİ KÂR SÜZGECİ TUZAĞI — ölçülmüş en büyük örnek

```
DOGRU  (id ile birlestirilmis)   :  -1.972,89 $
YANLIS (kismi olanlar atilirsa)  : -26.742,79 $
fark                             : +24.769,90 $   (255 pozisyonda kismi var)
```

`CLAUDE.md`'de kayıtlı örnek **~4.465 $** idi; bu pencerede hata **24.770 $**.
Kural (*"süzgeç saymak içindir, toplamak için değil"*) burada **beş kat daha
büyük** bir sapma üretiyor.

### Ne söylüyor, ne söylemiyor

**Söylüyor:** (a) botun BOĞA'daki vetoları para kazandırmış; (b) `pump_long_tezi`
tek rakamla okunamaz, kârı iki güne bağlı; (c) kısmi-kâr süzgeci hatası bu
defterde devasa.

**Söylemiyor:** BOĞA'da SHORT'un kaybettirdiğini — o iddia gölgeyle
**doğrulanamadı** (N=3). Sentetik ölçüm tek dayanak olarak kalıyor.

**Bot dosyalarına yazım: YOK.**

---

## 🔬 11-19 AĞUSTOS PENCERESİ — *"elimizdeki en iyi bot oydu"* ölçüldü (2026-09-05)

> Kullanıcı: *"başarılıdan kastım seçtiği coinler bir şekilde büyük oranda artıda
> kalıyordu, elimizdeki en iyi bot oydu."*
> Betikler: `scratchpad/pencere_11_19.py` · ham çıktı `pencere_11_19_sonuc.txt`.
> 🔴 **Betimleyici. Ön-kayıt yok, hüküm yok.**

### ✅ Tespit DOĞRU — tek artı pencere o

```
pencere                       N   toplam $    ort $  kazanan   gun ort  t_gun  gun
07-23..08-10 (S9 oncesi)     10    -803,31   -80,33    %40,0   -169,19  -1,68    5
08-11..08-19  <- KULLANICI  115    +184,98    +1,61    %45,2     -5,59  -0,31    9
08-20                        24    -715,99   -29,83    %29,2         -      -    1
08-21..09-05 (BOGA)         243   -4748,27   -19,54    %46,1    -26,96  -3,75   16
```

**Dört pencerenin yalnız biri artıda** — ve o, kullanıcının işaret ettiği pencere.

### ⚠️ AMA ÜÇ ÇEKİNCE

**1 · Kazanç küçük.** +184,98 $ / 115 işlem = işlem başına **+1,61 $**.
*"Büyük oranda artıda"* bir büyüklük değil.

**2 · Kazanma oranı aslında DÜŞÜK.** %45,2 — BOĞA penceresinin (%46,1)
**altında.** Yani *"seçtiği coinler artıda kalıyordu"* gözlemi **isabet
oranından gelmiyor**; farkı yaratan **kazananların büyüklüğü** (31 TP2).

**3 · 🔴 Yoğunlaşma uç seviyede.**

```
en iyi 1 gun    +696,01 $  -> toplamin %376'si
en iyi 2 gun   +1229,97 $  -> toplamin %665'i
en iyi 5 islem +1640,01 $  -> toplamin %887'si
en iyi 2 gun HARIC        :  -1044,99 $
artida gun                :  5 / 9
gun-kumeli ortalama       :  -5,59 $   (t = -0,31)
```

**İki günü ve beş işlemi çıkarınca pencere −1.045 $.**
Gün-kümeli ortalama **negatif** ve sıfırdan ayrılmıyor.

🔑 **Doğru okuma: "en iyi bot" = kaybetmeyen tek yapılandırma. Ölçülmüş bir
kenarı olan bot DEĞİL.**

### 🔑 PENCEREYİ AYIRAN ASIL ŞEY — yön

```
yon      : SHORT 105 · LONG 10        <- neredeyse saf SHORT defteri
cikis    : STOP 80 · TP2 31 · ZAMAN_STOP 4
en iyi 5 : RVN +395 · AIOT +333 · BICO +324 · IOTX +308 · ME +279  (hepsi SHORT)
```

Kıyas: BOĞA penceresinde **LONG 232 / SHORT 9**. Yani 11-19 botu, düşen bir
piyasada **SHORT defteri** işletiyordu — kazancı oradan geldi.

⚠️ Bugünkü kuyruk ölçümüyle birlikte okunmalı: küçük coin short'lamanın yukarı
kuyruğu 18 kat şişman. O pencere **piyasa düştüğü için** çalıştı.

### ⭐ YAPILANDIRMA KURTARILDI — ve iki ayara indi

`kripto-config.json` git'te izlenmiyor (**0 commit**), ama yedekler duruyor:

```
yedek-2026-08-11-s9      Aug 11 12:43   S9 (risk %3->%1,5 · asgari_stop %2)
yedek-2026-08-11-kismi   Aug 11 22:25   kismi kar
yedek-20260819-134420    Aug 19 13:44   PENCERENIN SONU
```

**Pencere içinde parametre DEĞİŞMEDİ** (yalnız bildirim ayarları + `kismi_pay`
resmileşmesi) → *"11-19 botu"* **iyi tanımlı** bir yapılandırma.

**19 Ağustos → bugün arasında değişen SADECE ÜÇ ŞEY:**

| ayar | 19 Ağustos | bugün | ne yapar |
|---|---|---|---|
| `esikler.btc_pay_short_freni` | **1** | 0 | SHORT freni — **kapatıldı** |
| `testbot.maks_dusus_pct` | **25** | 0 | düşüş freni — **kapatıldı** |
| `testbot.maks_pozisyon` | 8 | 0 | *(bugün ben durdurdum)* |

🔴 **İkisi de KORUMAYDI ve ikisi de kaldırılmış.** Hakem raporunun
*"kirlenmenin yönü: değişiklikler koruma KALDIRIYORDU"* notu birebir doğrulandı.

**Yani 11-19 botunu geri getirmek iki satır:**
`btc_pay_short_freni: 1` · `maks_dusus_pct: 25`

⚠️ Düşüş freni açık olsaydı **tetiklenirdi**: zirve 6.320,77 → bugün 4.427,99 =
**−%29,9**, eşik −%25. Bot kendi kendine duracaktı.

### Ne söylüyor, ne söylemiyor

**Söylüyor:** o pencere tek artı olan; yapılandırması tanımlı ve iki ayarla
geri getirilebilir; farkı yaratan **SHORT ağırlığı** ve **TP2'ye kadar tutmak**.

**Söylemiyor:** o yapılandırmanın bir **kenarı** olduğunu. Gün-kümeli t=−0,31,
iki gün çıkınca eksi. **Aynı config farklı bir piyasada aynı sonucu vermez.**

**Bot dosyalarına yazım: YOK.**

---

## 🔬 19-21 AĞUSTOS LONG'LARI — kullanıcı tespitinin ölçümü (2026-09-05)

> Kullanıcı: *"yanılmıyorsam o bot LONG'da açıyordu, ve 19-21 arası açtığı
> LONG'lar isabetliydi, doğru mudur?"*
> 🔴 **Betimleyici. Ön-kayıt yok, hüküm yok.**

### ✅ 1 · "LONG açıyordu" — DOĞRU, ama azdı ve payı ARTIYORDU

```
gun           LONG  SHORT     LONG P&L    SHORT P&L
2026-08-17       0     14        +0,00      +352,99
2026-08-18       3      3      -222,52      -140,56
2026-08-19       3      4      +241,49      -294,40
2026-08-20       7     17      +283,94      -999,93
2026-08-21       6      7      -419,29      -338,52
2026-08-22      23      1      +108,23        +8,83
```

11-19 penceresinde LONG **10 / SHORT 105** — yani %9. Ama 18'inden itibaren
payı hızla büyüyor.

### ⚠️ 2 · "19-21 isabetliydi" — DOĞRU AMA TARİH BİR GÜN DAR

```
19-21 LONG   N=16   +106,14 $   ort  +6,63   kazanan %56,2   R_med +0,01
19-21 SHORT  N=28  -1632,85 $   ort -58,32   kazanan %10,7   R_med -1,02
```

**Göreli olarak kesinlikle haklısın:** o pencerede LONG artıda, SHORT
felaket (%10,7 isabet). Yön çağrısı doğruydu.

**Ama günlere ayırınca:**

```
19-20  LONG 10 -> +525,43 $      SHORT 21 -> -1294,33 $
21     LONG  6 -> -419,29 $      SHORT  7 ->  -338,52 $
```

🔑 **LONG başarısı 19-20'ye ait. 21'inde LONG'lar da kaybetti.**

### 🔴 3 · VE İRONİ BURADA — botun etiketi tam ters anda döndü

Botun **kendi** rejim etiketi (defterden, giriş anında):

```
08-19  NOTR 7
08-20  NOTR 24
08-21  NOTR 7 · BOGA 6     <- etiket BURADA donuyor
08-22  NOTR 1 · BOGA 23
```

**Bot LONG'ları etiketi NOTR derken kazandı (19-20), etiket BOĞA dediği anda
kaybetmeye başladı (21).**

Yani rejim etiketi bu dönüşte **geç kalmadı, tam ters zamanlandı**: LONG'un
işe yaradığı iki günü kaçırdı, işe yaramaz olduğu gün açıldı.

⚠️ N küçük (16 LONG); tek vaka. Ama `durum.md`'de kayıtlı *"etiket 08-21'de
döndü, hareket 08-19'da başlamıştı"* gözlemine **fiyat etiketi değil, PARA
etiketi** ekliyor.

### 🔴 4 · VE DEVAM ETMEDİ

```
11-18 LONG (oncesi)      N=  7    -102,25 $   ort -14,61
19-21 LONG               N= 16    +106,14 $   ort  +6,63
22-09-05 LONG (sonrasi)  N=228   -3930,60 $   ort -17,24
```

İki günlük LONG başarısını **228 işlemlik −3.931 $** izledi.

### 5 · Kazancın niteliği

19-21 LONG'larının **16'sının 16'sı da `STOP` ile kapandı** — yani hiçbiri
hedefe varmadı; kazananlar **iz-süren stopla** kırpıldı (en iyisi `EDGE`
+222,54, r=0,89). Kaybedenler tam **−1R**.

```
9 kazanan (kirpilmis)  vs  6 kaybeden (tam -1R)  ->  net +106,14 $
```

**R medyanı +0,01** — sıfır. Yani *"isabetliydi"* isabet oranından geliyor
(%56,2), büyüklükten değil.

### Özet

| iddia | sonuç |
|---|---|
| bot LONG açıyordu | ✅ **doğru** (11-19'da %9, sonra hızla arttı) |
| 19-21 LONG'lar isabetliydi | ⚠️ **19-20 için doğru**; 21'inde LONG da kaybetti |
| SHORT'tan iyiydi | ✅ **kesinlikle** (+106 vs −1.633) |
| sürdürülebilir bir kenar mıydı | 🔴 **hayır** — sonraki 228 LONG −3.931 $ |

**Bot dosyalarına yazım: YOK.**

---

## 🟢 ETİKET DÖNMESEYDİ — **GEÇTİ** (2026-09-05) · oturumun tek geçen ölçümü

**Ön-kayıt:** `ON_KAYIT_etiket_karsiolgu.md`, commit `8757c99` — koşumdan **önce**.
**Betikler:** `scratchpad/etiket_karsiolgu_dogrulama.py` (yapılabilirlik) ·
`etiket_karsiolgu.py` (hüküm) · ham çıktı `etiket_karsiolgu_sonuc.txt`
**Kullanıcı:** *"NOTR çalışmaya devam etseydi ne olurdu, ve short açmasaydı sadece long."*

### ✅ Yapılabilirlik ÖNCE doğrulandı — %98,9

`testbot.karar_yon(rejim_ad, ...)` rejimi parametre alıyor → zorlanabilir.
14.846 kayıtta kayıtlı kararların **%98,9'u yeniden üretildi**. Sapan 167'nin
**hepsi tek tip**: `VETO:long_veto → LONG` — kaynağı arşivde olmayan
`para_cikis` bayrağı, ki yalnız **LONG'u kapatır**.
🔴 **Yani karşı-olgu bilinen ve tek yönlü biçimde LONG-YANLI.**
(Eşleşme %95'in altında kalsaydı ölçüm koşturulmayacaktı; eşik önceden yazılıydı.)

### Sonuç — pencere 08-21 → 09-02, notional $1.000 sabit, 8 slot

```
kol            karar   pozisyon  yon dagilimi        toplam $  islem-ort  gun-ort  kazanan
A GERCEK         884       191   LONG 191           -1719,78   -0,900%   -1,267%   %27,7
B NOTR          3445       136   SHORT 113·LONG 23   +971,20   +0,714%   +0,521%   %37,5
C NOTR-LONG      136        33   LONG 33             +967,45   +2,932%   +2,555%   %51,5
```

| # | ölçüt | değer | sonuç |
|---|---|---|---|
| **K1** | `B` toplam > `A` toplam | **+971,20 vs −1.719,78** | ✅ GEÇTİ |
| **K2** | gün-kümeli \|t\| ≥ 2,0 | fark +1,788% · **t=2,46** | ✅ GEÇTİ |
| **K3** | iki yarıda aynı işaret | +1.294,65 / +1.396,32 | ✅ GEÇTİ |

**SONUÇ: GEÇTİ.** Fark **2.691 $** — ve iki yarıda da neredeyse eşit dağılmış.

### 🟢 VE YOĞUNLAŞMA TESTİNDEN SAĞ ÇIKIYOR — bugün bir ilk

```
B NOTR   en iyi 2 gun HARIC  +377,81 $   ·  en iyi 5 islem HARIC  +474,18 $  · artida gun 8/16
C LONG   en iyi 2 gun HARIC  +457,85 $   ·  en iyi 5 islem HARIC  +472,28 $  · artida gun 9/13
```

Bugün **her** bulgu bu adımda çöktü (`pump_long_tezi` %133 · 11-19 penceresi
%665). **Bu ikisi en iyi 2 gün ve en iyi 5 işlem çıkarıldıktan sonra hâlâ artıda.**

### 🔴 AMA ÜÇ CİDDİ ÇEKİNCE

**1 · Bugünkü sentetik ölçümlerle ÇELİŞİYOR.**
Gün boyu *"BOĞA'da SHORT kaybettirir"* ölçüldü
(`A_funding −0,692% · MA50 −0,193% · K_geniş −0,771%`).
Burada `B`'nin SHORT bacağı **+731,21 $** (113 işlem, %37,2 isabet).
Olası açıklama: NOTR dalı **seçici** (*"stage aktif + smart hizalı"*), sentetik
ölçüm ise **her uygun barı** örnekledi. **Çözülmedi — açık çelişki olarak kayda geçiyor.**

**2 · Slot kısıtı seçimi neredeyse keyfî yapıyor.**
3.445 karardan yalnız **136'sı** pozisyona döndü; seçen şey **varış sırası**.
Yani `B`'nin kârı *"NOTR dalı iyi seçiyor"*dan değil, **kısmen tesadüften**
gelebilir. N=113 SHORT için bağımsız bir kenar testi yapılmadı.

**3 · `para_cikis` yanlılığı `C`'yi en çok şişiriyor.**
Yanlılık **yalnız LONG ekliyor**; `C` tamamen LONG. Yani `C`'nin
**+2,932%/işlem** başlığı üç kolun **en az güvenilir**i.

### K4 (ayrı rapor, ölçüt DEĞİL) — "sadece LONG" sorusu

```
C +967,45 $  vs  B +971,20 $   ->  toplamda BASA BAS
ama islem basina: C +2,932%  vs  B +0,714%   (t=1,51)
```

`C` aynı parayı **dörtte bir işlemle** kazanıyor (33 vs 136). Bu ilgi çekici
ama **ölçüt değil**, N=33, ve yukarıdaki 3. çekince tam buraya vuruyor.

### 🔴 Ön-kayıtlı tahminlerin karnesi — **4'te 2**, ve büyük olan YANLIŞ

| # | tahmin | sonuç |
|---|---|---|
| 1 | `B` daha AZ işlem açacak | ✅ TUTTU (136 vs 191) |
| 2 | **`B` yine de NEGATİF olacak** — *"kayıp yönden değil mekanikten"* | ❌ **YANLIŞ** (+971 $) |
| 3 | `C`, `B`'yi geçemeyecek | ✅ teknik olarak tuttu (+967 vs +971), ama işlem başına **4 kat** önde |
| 4 | fark t≥2,0'a ulaşmayacak | ❌ **YANLIŞ** (t=2,46) |

🔑 **2. tahmin bu oturumun en büyük hatası.** Beş defterin aynı mekanikle
kaybetmesine bakıp *"sorun mekanikte, yön değil"* dedim. **Yön belirleyici çıktı.**

### Sınırlar (ön-kayıtta ilan edildiği gibi)

Yol bağımlılığı yaklaşık · `para_cikis` yanlılığı · `ONAY_BEKLE` bir tur
beklemeden alındı · kısmi kâr, likidasyon, düşüş freni **yok** · 13 gün,
tek epizot · sabit $1.000 notional (risk-bazlı boyutlandırma **değil**).

**Bot dosyalarına yazım: YOK.**

### 🟢 EK — kullanıcının tam sorusu: **19'dan itibaren, NOTR + yalnız LONG**

> *"Yani bot 19'dan beri etiket değiştirmeyip NOTR'da kalsaydı ve SHORT
> açmasaydı artıda mı olacaktı?"*

Pencere **08-19 → 09-02**'ye çekilerek yeniden koşturuldu (ön-kayıtlı kollar,
ölçüt ve mekanik **değişmedi**; yalnız başlangıç tarihi kullanıcının sorduğu
güne alındı).

```
GERCEK BOT (defterden, gercek boyutlandirma)   235 poz   -4630,48 $   LONG 206·SHORT 29

Karsi-olgu (SABIT $1.000 notional, 8 slot):
A GERCEK (yeniden uretim)   224 poz   -2372,31 $   islem-ort -1,059%   kazanan %25,4
B NOTR (short dahil)        171 poz    +516,02 $   islem-ort +0,302%   kazanan %33,3
C NOTR + YALNIZ LONG         44 poz   +1162,78 $   islem-ort +2,643%   kazanan %50,0
```

**Cevap: EVET.** Ve sorulan kombinasyon (`C`) **üç kolun en güçlüsü.**

#### 🟢 Ve yoğunlaşmada B ile C AYRIŞIYOR — belirleyici fark

```
B NOTR   artida gun  9/19 · en iyi 2 gun HARIC   -77,37 $   <- COKUYOR
C LONG   artida gun 10/15 · en iyi 2 gun HARIC  +571,76 $   <- AYAKTA
                            en iyi 5 islem HARIC +667,60 $   <- AYAKTA
```

**SHORT'lar dahil edilince kâr iki güne bağlanıyor; yalnız LONG kolu
sağlam kalıyor.** Yani kullanıcının *"short açmasaydı"* kısıtı **süsleme değil,
sonucun taşıyıcısı.**

#### ✅ `para_cikis` yanlılığı endişesi ÇÖZÜLDÜ

`C`'nin 171 kararı ile yanlılığın 167'si sayıca yakındı; örtüşme sanıldı.
Ölçüldü — örtüşme **yok**:

```
C kolunun 171 kararinin arsivdeki GERCEK karsiligi:
   karar-yok         129  (%75,4)   <- gercek bot bu adaylarda KARAR VERMEDI
   LONG/ONAY_BEKLE    38  (%22,2)
   VETO:long_veto      4   (%2,3)   <- yanliligin etkisi
```

`C`'nin işlemleri *"veto edilmişken sızan"* işlemler **değil**; NOTR dalının
**gerçekten farklı** kararları.

#### ⚠️ Ölçek uyarısı — dolar rakamı doğrudan okunamaz

Kollar **sabit $1.000 notional** kullanıyor; gerçek bot **risk-bazlı**
boyutlandırıyor ve daha büyük açıyor. Kalibrasyon: `A` yeniden üretimi
**−2.372 $** derken gerçek bot **−4.630 $** kaybetti (≈**1,95 kat**).
Aynı çarpanla `C` kabaca **+2.200 $** mertebesine denk gelir — ama bu bir
**kestirimdir**, ölçüm değil.

#### Kalan sınırlar

N=44 · slot seçimi varış sırasına bağlı (kısmen keyfî) · `ONAY_BEKLE` bir tur
beklemeden alındı · kısmi kâr/likidasyon/düşüş freni yok · 15 gün, tek epizot ·
ve `olcumler.md`'de kayıtlı **açık çelişki**: bugünkü sentetik ölçümler
*"BOĞA'da SHORT kaybettirir"* demişti, `B`'nin SHORT bacağı ise artıda.

### 🔴 EK — "pos ve diğer adayları ekleyelim" — İKİSİ DE EKLENEMİYOR

> Kullanıcı: *"buna pos ve daha önce uygulayalım dediğimiz şeyleri eklesek nasıl olur?"*
> **Sayım** (getiri hesaplanmadı), `C` kolunun 171 kararı üzerinde:

```
pos dagilimi                          s_brk dagilimi (skorun %11'i)
  < 0,25 (dip-bicak)   0   (%0,0)       s_brk = 0 olan :   0  (%0,0)
  0,25-0,50            0   (%0,0)       medyan s_brk   : 13,88  (tavan 15)
  0,50-0,70            1   (%0,6)       skor medyani   : 58,0
  >= 0,70            170  (%99,4)
  medyan pos: 1,13
```

#### 1 · `pos<0.25` koşullu mekanik → **EKLENEMEZ: 0 pozisyon**

`long_veto` zaten `pos < 0.25`'i **her dalda** engelliyor
([testbot.py:431](testbot.py#L431)). Bir LONG-only defterde dip-bıçak girişi
**tanım gereği yok.** Medyan `pos` **1,13** — yani 20-bar aralığının **üstünde**.

⚠️ V3 adayı **sentetik** evrende (her radar karesi bir LONG girişi sayıldı)
ölçülmüştü; botun gerçek LONG defterinde o popülasyon **hiç yok.**

#### 2 · `s_brk` ters çevirme → **EKLENİRSE `C`'Yİ ÖLDÜRÜR**

`C`'nin medyan `s_brk`'ı **13,88 / 15** — yani işlemlerinin neredeyse tamamı
**maksimum breakout** girişleri (`pos ≥ 0,7` **ve** yüksek `last1`).

🔴 Bugün ölçüldü: `s_brk` skorun **tek sinyal taşıyan** terimi ve **ters** yönde
(BOĞA'da t=−2,39; yüksek `s_brk` → **daha kötü** getiri).

**Yani `C`'nin işlemleri, tam olarak `s_brk`'ın "kötü" dediği işlemler.**
`s_brk`'ı düzeltmek `C`'yi **elemek** demek.

#### 🔴 3 · VE BU İKİNCİ ÇELİŞKİ — desen artık belli

| ölçüm | ne diyor | veri |
|---|---|---|
| `s_brk` bileşen ölçümü | yüksek `s_brk` = **kötü** (t=−2,39) | sentetik, tüm evren |
| `C` kolu karşı-olgusu | medyan `s_brk` 13,88, sonuç **+1.162 $** | kapılı, slot-kısıtlı alt küme |

Bugün **aynı şekilde** bir çelişki daha kaydedildi: sentetik ölçüm
*"BOĞA'da SHORT kaybettirir"* derken `B` kolunun SHORT bacağı artıda çıktı.

🔑 **İki çelişki, tek desen:** *tüm evreni tarayan sentetik ölçümler* ile
*kapılı + slot-kısıtlı karşı-olgu* **sistematik olarak ters** sonuç veriyor.
İkisinden biri yanlış ve **hangisi olduğu bilinmiyor.**

**İki olası açıklama, ikisi de sınanabilir:**
1. Kapılar (`stage` · `smart` · `long_veto`) gerçekten seçiyor; sentetik
   örnekleme bunu göremiyor.
2. Karşı-olgu slot sırası yüzünden şanslı; N=44 bunu ayırt edemiyor.

#### Sonuç — kullanıcının sorusuna cevap

| eklenmek istenen | durum |
|---|---|
| `pos<0.25` mekaniği | ❌ **eklenemez** — 0 pozisyon |
| `s_brk` ters çevirme | ❌ **eklenirse `C`'yi eler** — ters yönde çalışıyor |
| geniş stop (2,5×ATR) | ⚠️ teknik olarak eklenebilir; **ama aynı pencerede denenirse aşırı uydurma** |

🔴 **Bu adaylar bağımsız yapı taşları değil — aynı işlemler hakkında
BİRBİRİYLE YARIŞAN iddialar.** Üst üste koymak toplama değil, çelişki üretiyor.

**Doğru sıradaki iş, kural eklemek değil: yukarıdaki çelişkiyi çözmek.**

---

## 🔴 KAPI MI SEÇİYOR, SLOT MU ŞANSLI — **ÇELİŞKİ ÇÖZÜLMEDİ**, ve NOTR modeli ZAYIFLADI (2026-09-05)

**Ön-kayıt:** `ON_KAYIT_kapi_mi_slot_mu.md`, commit `fc88daa` — koşumdan **önce**.
**Betik:** `scratchpad/kapi_mi_slot_mu.py` · ham çıktı `kapi_mi_slot_mu_sonuc.txt`

### Sonuç

```
### S1 — SLOT SANSI  (slot UYGULANMADAN, ayni mekanik)
  alinan (slot gecti)   N=44  gun=15   islem-ort +2,643%   kazanan %50,0
  alinmayan             N=22  gun=12   islem-ort -0,929%   kazanan %27,3
  fark +5,229%   t_gun +2,62   MDE 3,995   -> GORULUR

### S2 — KAPI SECIMI
  kapili (tumu)         N= 66 gun=16   islem-ort +1,452%   kazanan %42,4
  eslesmis KONTROL      N=412 gun=16   islem-ort +0,139%   kazanan %34,2
  fark +1,336%   t_gun +1,05   MDE 2,545   -> goremiyoruz
```

| # | ölçüt | sonuç |
|---|---|---|
| **K1** | kapı seçimi > 0 · t ≥ +2,0 | ❌ **DÜŞTÜ** (t=1,05) |
| **K2** | slot farkı MDE altında | ❌ **DÜŞTÜ** — slot farkı **GÖRÜLÜR** |

**Ön-kayıtlı yorum tablosuna göre resmî hüküm: ÇELİŞKİ ÇÖZÜLMEDİ.**

### 🔴 AMA BİLEŞENLER AÇIK BİR ŞEY SÖYLÜYOR

```
SLOT SANSI    -> GORULUR      (+5,23%, t=2,62)
KAPI SECIMI   -> GOREMIYORUZ  (+1,34%, t=1,05)
```

**Slot'a giren 44 işlem +2,64%, giremeyen 22 işlem −0,93%.** Aralarındaki tek
fark **varış sırası** — kapıları ikisi de geçmişti.

🔑 **Yani `C` kolunun +1.162 $'ı, önemli ölçüde HANGİ 44'ün slota girdiğine
bağlı; kapıların seçiciliğine değil.**

### 🔴 NOTR MODELİ ZAYIFLADI — ve bunu bir mesaj önce ilan etmiştim

Kullanıcı *"NOTR modelde hemfikiriz değil mi"* diye sordu; cevabım
*"hemfikirim ama kanıtlanmış olarak değil — ve şimdi koşturacağım ölçüm onu
çürütebilir"* olmuştu. **Çürüttü.**

`C` kolunun `+2,643%/işlem` başlığı artık **büyük ölçüde slot sırası
artefaktı** olarak okunmalı. Ön-kayıtlı hükmü (`GEÇTİ`) **geri almıyorum** —
o ölçüt kendi kurallarıyla geçti — ama **yorumu değişti**: geçen şey
*"NOTR mantığı kazandırır"* değil, *"o pencerede o 44 işlem kazandırdı"*.

### ⚠️ Sınırlar — bu ölçümün kendisi de zayıf

`S1` **44 vs 22** ile koşuyor; `t=2,62` ve `MDE 3,995`'in **hemen üstünde**.
Yani *"slot şansı var"* da güçlü kanıt değil — yalnızca *"yok"* diyemiyoruz.
`S2`'de de `MDE 2,545` gözlenen farkın (**1,336**) neredeyse **iki katı** →
kapı seçimi için de **güç yetersiz**.

🔑 **Dürüst özet: bu pencerede 66 işlemle bu soru cevaplanamıyor.**

### Ön-kayıtlı tahminlerin karnesi — 4'te 1

| # | tahmin | sonuç |
|---|---|---|
| 1 | S1'de görülür fark **çıkmayacak** | ❌ **YANLIŞ** — çıktı (+5,23%, t=2,62) |
| 2 | kontrolün mutlak getirisi negatif | ⚠️ **kısmi** — işlem-ort **+0,139%**, gün-ort −0,425% |
| 3 | K1 geçse bile `C`'nin +2,64'ünü açıklamaya yetmez | ✅ tutarlı (kapı etkisi +1,34) |
| 4 | `s_brk` çelişkisi tam çözülmeyecek | ✅ TUTTU |

### Ne yapılmalı

Çelişki **açık kaldı** ve bu pencerede kapanmıyor. Kapanması için:
**daha çok slot** (kapasite kısıtı kalksın → alınan/alınmayan ayrımı kaybolur)
ya da **ikinci bir epizot**. İkisi de ileri yönlü çalışma gerektiriyor —
geriye dönük bu veriden çıkarılamaz.

**Bot dosyalarına yazım: YOK.**

### 🔴 DÜZELTME — "slot şansı" YORUMU YANLIŞTI (2026-09-05, aynı gün)

Kullanıcı *"peki slotu büyütsek"* diye sordu; slot taraması koşturuldu ve
**4'ten sınırsıza kadar her değerde aynı 44 işlem** çıktı.

```
171 karardan ne oldu:
   ALINAN                   44
   ayni sembol zaten ACIK   95   <- ASIL eleyici
   4 saat COOLDOWN          17
   asgari_stop/mekanik      10
   fiyat yok                 5

   SLOT hic bagladi mi:  HAYIR, HIC
```

🔴 **`SLOT` kısıtı hiçbir zaman dolmadı.** Dolayısıyla `kapi_mi_slot_mu`
ölçümünün `S1` karşılaştırmasını *"slot şansı"* diye adlandırmam **yanlıştı**;
o karşılaştırma başka bir şeyi ölçüyormuş.

**Sayılar doğru, ETİKET yanlıştı.** Ön-kayıtlı hüküm (`K1 düştü · K2 düştü`)
**geri alınmıyor** — ölçüt kendi metniyle uygulandı; düzeltilen **yorum**.

#### Gerçekte ne ölçülmüş — ve bulgu daha iyi

```
66 islem, sembolde kacinci giris:
   ILK giris      N=33   islem-ort  +3,549%   kazanan %54,5
   TEKRAR giris   N=33   islem-ort  -0,645%   kazanan %30,3

   "alinmayan 22"nin 22'si (%100) TEKRAR girisi
```

🔑 **Ayıran şey varış sırası ya da şans değil: bir sembole İLK giriş
kazandırıyor, AYNI sembole tekrar giriş kaybettiriyor.**

Ve simülasyonun *"aynı sembol açıkken tekrar açma"* kuralı **tam olarak
kaybeden tekrarları eliyor.** Bu bir **mekanizma**, tesadüf değil —
ve bot bu kurala **zaten sahip**.

#### 🔴 NOTR modeli hakkındaki hükmüm DEĞİŞİYOR

| ne demiştim | doğrusu |
|---|---|
| *"kâr slot şansından geliyor"* | ❌ slot hiç bağlamadı |
| *"tek fark varış sırası"* | ❌ fark **ilk giriş / tekrar giriş** |
| *"NOTR modeli zayıfladı"* | ⚠️ **kısmen geri alınıyor** — zayıflatan sebep geçersizdi |

`C` kolunun kârı bir **artefakt değil**; mevcut ve makul bir kuralın
(sembol başına tek açık pozisyon) çalışmasından geliyor.

⚠️ **Ama NOTR modeli yine de kanıtlanmadı** — bunlar hâlâ geçerli:
kapı seçimi gösterilemedi (`t=1,05`) · holdout yok · ilk-giriş N=**33** ·
hipotez ile test aynı pencereden.

#### 🔑 VE YENİ, DAHA BASİT BİR SORU DOĞDU

*"İlk giriş iyi, tekrar giriş kötü"* iddiası **rejimden bağımsız** olabilir ve
NOTR modelinden **çok daha basit** bir hipotezdir. Bu haliyle:

- ön-kayıtsız ve tek pencerede bulundu → **kural değil**
- ama botun **gerçek defterinde** doğrudan sınanabilir (sembol başına
  kaçıncı giriş × sonuç)
- ve doğruysa **mevcut kuralı sıkılaştırmak** (cooldown süresi) somut bir aday olur

**Bot dosyalarına yazım: YOK.**

---

## 🔴 İLK GİRİŞ / TEKRAR GİRİŞ — **DÜŞTÜ**, ve işaret TERS (2026-09-05)

**Ön-kayıt:** `ON_KAYIT_ilk_tekrar_giris.md`, commit `00f5d5a` — koşumdan **önce**.
**Betik:** `scratchpad/ilk_tekrar_giris.py` · ham çıktı `ilk_tekrar_giris_sonuc.txt`
**Kullanıcı:** *"tekrar girişler çok fazla… bunu sına."*

### Sonuç — gerçek defter, 392 pozisyon / 152 sembol

```
ILK giris     N=152   net% +0,420%   dolar -14,74 $   kazanan %42,1
TEKRAR giris  N=240   net% +1,347%   dolar -16,01 $   kazanan %46,2
                      (%61,2 tekrar)
```

🔴 **Tekrar girişler net%'te DAHA İYİ, kazanma oranı da DAHA YÜKSEK.**

| # | ölçüt | değer | sonuç |
|---|---|---|---|
| **K1** | gün-eşleşmiş fark > 0 · t ≥ +2,0 | **−0,463%** · t=−0,48 | ❌ DÜŞTÜ |
| **K2** | sembol-kümeli aynı işaret | +0,083% (ters) | ❌ DÜŞTÜ |
| **K3** | \|fark\| ≥ MDE | 0,463 vs **1,943** | ❌ GÖREMİYORUZ |
| **K4** | dolarda aynı işaret | −2,34 $ | ✅ |

**SONUÇ: DÜŞTÜ.** Giriş sırasında **azalma da yok** — tersine:

```
sira 1: +0,420%  ·  sira 2: +0,580%  ·  sira 3: +2,108%  ·  sira 4+: +1,698%
```

### 🔑 SENTETİK ÖLÇÜMLE ÇELİŞKİ — ve bu sefer AÇIKLAMASI BULUNDU

```
sentetik karsi-olgu :  ilk +3,549%  vs  tekrar -0,645%   (N=33/33)
gercek defter       :  ilk +0,420%  vs  tekrar +1,347%   (N=152/240)
```

**İki ölçüm AYNI ŞEYİ ölçmüyor:**

```
tekrarlarin oncekinden gecen sure (GERCEK defter):
   medyan 25,1 saat · %25: 10,1 · %75: 96,4 · 4 SAATTEN KISA: 0 (%0)
```

- **Sentetik "tekrar"** = pozisyon **hâlâ AÇIKKEN** gelen ikinci sinyal
  (simülasyonda *"aynı sembol açık"* diye elenenler) → **ekleme/piramit**
- **Gerçek "tekrar"** = önceki pozisyon **KAPANDIKTAN sonra**, medyan **25 saat**
  sonra yeni giriş → **yeniden giriş**

🔑 **Bunlar farklı şeyler ve ikisi de doğru olabilir:**
*açık pozisyona eklemek* kötü (zaten yasak), *kapandıktan sonra tekrar girmek*
kötü **değil**.

### 🔴 ÖNCEKİ DÜZELTMEMİ DE DÜZELTİYORUM

Bir mesaj önce *"ayıran şey ilk giriş / tekrar giriş"* demiştim ve bunu genel
bir mekanizma gibi sundum. **Gerçek defterde tekrarlanmıyor.** Doğrusu dar:
*sentetik simülasyonda, pozisyon açıkken gelen ikinci sinyal kötüydü.*

### Kullanıcının işaret ettiği coin — bulundu ama beklenen o değil

```
ASCII disi sembol adlari:
   牛来   giris=2   toplam  -3,83 $
   龙虾   giris=2   toplam -67,53 $
```

İkisi de **yalnız 2 kez** girilmiş ve zararları küçük. Kullanıcının hatırladığı
desen büyük olasılıkla **`ONG`**:

```
ONG   13 giris   -838,22 $   (ort -64,48)
ONT    9 giris   -690,40 $   (ort -76,71)
CAP    6 giris   -399,33 $   (ort -66,55)
```

⚠️ **Gözlem doğru, genelleme yanlış:** `ONG` gerçekten 13 kez girilip 838 $
kaybettirmiş. Ama bu **tekrar girmenin** değil, **o sembolün** özelliği —
tekrarların geneli kaybettirmiyor. En çok girilen 10 sembol tüm tekrarların
yalnız **%31'ini** taşıyor.

### Ön-kayıtlı tahminlerin karnesi — 4'te 1

| # | tahmin | sonuç |
|---|---|---|
| 1 | havuzlanmış fark, gün-eşleşmişten büyük | ✅ (0,927 > 0,463) |
| 2 | giriş sırasında monotonluk, sonra düzleşme | ❌ **YANLIŞ** — azalma yok, artış var |
| 3 | en çok girilen 10 sembol tekrarların yarısından fazlasını taşır | ❌ **YANLIŞ** (%31) |
| 4 | dolar farkı yüzde farkından büyük görünür | ❌ işaretler ayrıştı |

### 🔴 GÜNÜN META-BULGUSU: ÜÇÜNCÜ SENTETİK-GERÇEK ÇELİŞKİSİ

```
1. sentetik "BOGA'da SHORT kaybettirir"  vs  karsi-olguda SHORT bacagi ARTIDA
2. sentetik "yuksek s_brk kotu"          vs  C kolu yuksek s_brk ile ARTIDA
3. sentetik "tekrar giris kotu"          vs  gercek defterde tekrar DAHA IYI
```

Üçünde de **sentetik yeniden-kurgu** ile **gerçek/kapılı veri** ters düşüyor.
Üçüncüsünün sebebi bulundu (tanım farkı). **İlk ikisininki hâlâ açık.**

🔑 **Kural adayı:** sentetik bir ölçüm gerçek defterle çelişiyorsa, önce
*"ikisi aynı şeyi mi ölçüyor"* sorulur — bugün üç kez sorulmalıydı, bir kez soruldu.

**Bot dosyalarına yazım: YOK.**

---

## 🔑 ÇIKIŞ VERİMİ — bugünün en büyük tek rakamı (2026-09-05)

> 🔴 **Betimleyici. Ön-kayıt yok, hüküm yok, kural çıkmaz.**
> Kullanıcı: *"fark yaratacak ne var elinde"* → bütün gün **girişe** bakıldı;
> bu, **çıkış** tarafına ilk bakış. Betik: `scratchpad/cikis_verimi.py`
> Veri: `pozisyon_izleme.jsonl` (`mfe_pct`) × `testbot_islemler.jsonl` (id ile).

### Sonuç — 341 pozisyon

```
MFE (lehimize EN COK)   medyan  +2,85%
GERCEKLESEN             medyan  -2,14%
MAE (aleyhimize EN COK) medyan  -3,18%
YAKALAMA ORANI (gerceklesen/MFE)   medyan %0,0   ·   ort %39,2
```

🔑 **Medyan pozisyon %2,85 artıya geçiyor ve %2,14 zararla kapanıyor.
Yakalama oranının medyanı SIFIR.**

### Çıkış sebebine göre — asıl tablo burada

```
sebep          N     MFE med   gercek med    toplam $
STOP         301      +2,50%      -2,52%   -10.601,69
TP2           34      +9,99%     +13,88%    +5.270,72
ZAMAN_STOP     6      +7,19%      +1,82%       +191,82
```

**301 pozisyon stopla kapandı ve −10.602 $ kaybettirdi — ve o pozisyonların
medyanı +%2,50 kâra geçmişti.** Bütün kayıp tek bir satırda.

### Geri verme, MFE eşiğine göre

```
MFE >= %1   : 256 pozisyon, 107'si ZARARLA kapandi   (%42)
MFE >= %3   : 168 pozisyon,  37'si ZARARLA kapandi   (%22)
MFE >= %5   : 106 pozisyon,   6'si ZARARLA kapandi   (%6)
MFE >= %10  :  45 pozisyon,   0'i  ZARARLA kapandi   (%0)
```

🔑 **Geri verme sorunu KÜÇÜK MFE'de yoğunlaşıyor.** %5'e ulaşan pozisyon
neredeyse hiç zararla kapanmıyor; %1-3'te kalanların **%42'si** kapanıyor.

Yani bu *"kârı erken al"* değil, **"küçük kazanan neden kaybedene dönüşüyor"**
sorusu — hedef değil **stop yerleşimi** meselesi.

### 🔴 AMA — bu refleks ZATEN TEST EDİLDİ ve DÜŞTÜ

Buradan çıkacak ilk fikir *"başabaşa çek / erken kâr al"* olur. Kayıt:

- **Çıkışı sıkılaştıran 30 varyantın 29'u düştü**; geçen tek varyant çıkışı
  **gevşetiyordu** (sabit %10 hedef).
- **Kısmi kâr ölçüldü ve kenarı KÜÇÜLTÜYOR**: `_kismi_pay_not` →
  kısmi yok +0,301 · %40'ta +0,274 → kenarın **~%9'u** gidiyor.
  Hedefe ulaşma oranı **değişmiyor** (%29,1 iki kuralda da); değişen, kazananda
  kazancın kesilmesi.
- **Kısmi sonrası başabaşa çekme de ölçüldü**: +0,274 → **+0,261** (daha kötü).

⚠️ **Yani "geri veriyoruz" gözlemi doğru, ama bilinen çözümleri denenmiş ve
kaybettirmiş.** Buradan yeni bir kural çıkarmak, 29/30 sicile karşı savunma
yapmayı gerektirir.

### En büyük kaçırılanlar (MFE yüksek, zararla kapandı)

```
MELANIA LONG  MFE +9,65  ->  -2,25%   ZAMAN_STOP
HOME    SHORT MFE +9,23  ->  -0,93%   STOP
BICO    SHORT MFE +8,79  ->  -2,82%   STOP
ZORA    LONG  MFE +6,41  ->  -7,31%   STOP   (-125,27 $)
TRUMP   LONG  MFE +4,85  -> -11,92%   STOP   (-128,60 $)
```

### Ne söylüyor, ne söylemiyor

**Söylüyor:** kaybın **tamamı** stop kapanışlarında (−10.602 $), ve o
pozisyonlar ortalama olarak **artıya geçmişti**. Yakalama oranı medyanı sıfır.

**Söylemiyor:** ne yapılması gerektiğini. Akla gelen iki çözüm (kısmi kâr,
başabaş stop) **ölçülmüş ve ikisi de kenarı küçültmüş.** Üçüncü bir fikir
gerekiyor ve o fikrin **kendi ön-kaydı** olmalı.

**Bot dosyalarına yazım: YOK.**

---

## 🔑 SKOR, GERÇEK DEFTERDE — ve "5 bileşen nasıl etkisiz olur"un CEVABI (2026-09-05)

> Kullanıcı: *"skor hiçbir işe yaramıyorsa neden kullanıyoruz · 5 bileşen nasıl
> etkisiz olur anlamıyorum."*
> 🔴 İtiraz haklıydı: bugünkü skor ölçümü **sentetikti** ve bugün **üç kez**
> sentetik ölçüm gerçek veriyle ters düştü. Bu ölçüm **gerçek defteri** kullanır.
> Betik: `scratchpad/skor_gercek.py` · **Betimleyici, hüküm yok.**

### A · Gerçek defterde skor sonucu öngörüyor mu — HAYIR

```
dilim          N   skor ort    net% ort   dolar ort   kazanan   stop% ort
Q1 (dusuk)    85      37,1      +1,885      -5,92      %44,7      4,26
Q2            85      48,7      +0,247     -21,51      %43,5      4,90
Q3            85      56,1      +0,603     -14,57      %49,4      4,49
Q4 (yuksek)   86      69,7      +1,025     -18,24      %43,0      5,23

Q4 - Q1 : -1,507%   t_gun -0,68   MDE 4,447   -> goremiyoruz
```

Monotonluk yok; **en düşük skor dilimi en iyi net%'e ve en az dolar zararına
sahip.** Bu, sentetik ölçümle **aynı yönde** — yani bu bulguda sentetik/gerçek
çelişkisi **YOK**.

### 🔑 C · MEKANİZMA — asıl cevap burada

```
skor ~ STOP MESAFESI  : r = +0,151   <- OYNAKLIK ile iliskili
skor ~ |MFE|          : r = -0,138   <- hareket buyuklugu
skor ~ net%           : r = -0,024   <- SONUC ile iliskisi SIFIR

stop mesafesi:  Q1 %4,26  ->  Q4 %5,23
```

**Skor yükseldikçe stop genişliyor, sonuç değişmiyor.**

### 🔑 VE SEBEBİ FORMÜLÜN KENDİSİNDE — [radar.py:123](radar.py#L123)

```python
s_oi   = clamp(oi24/20)*25 + clamp(oi3/8)*10        # OI DEGISIMI  -> buyukluk
s_fund = clamp(abs(f)/0.05)*15 + squeeze_bonus      # abs() -> ISARET YOK
s_comp = clamp((0.8-comp)/0.5)*20                   # SIKISMA      -> oynaklik
s_vol  = clamp((vol_x-1.5)/3)*20                    # HACIM KATI   -> buyukluk
s_brk  = clamp((pos-0.7)/0.3)*10 + clamp(last1/4)*5 # konum+momentum -> YON
```

**Beş bileşenin dördü "ne kadar hareket var" ölçüyor, "hangi yöne" değil.**
Yalnız `s_brk` (skorun **%11'i**) yön taşıyor.

`s_fund` için kodun kendi notu bunu **kabul ediyor**:
> *"abs() BİLİNÇLİ olarak DOKUNULMADI. Zemin etüdü bilginin funding'in
> İŞARETİNDE olduğunu gösterdi…"*

### 🔴 CEVAP: bileşenler "etkisiz" değil — YANLIŞ ŞEYİ ölçüyor

Skor bir **hareket detektörü**. Ve bu projede zaten kayıtlı bir ders var
(`CLAUDE.md` → `kanal-stochrsi-analizi.md` 13.5):

> *"Yön değil sadece hareket öngören her sinyal DEĞERSİZDİR, çünkü stop
> mesafesi hareketle büyür."*

Mekanizma tam olarak şu:

```
yuksek skor -> "buyuk hareket geliyor" (DOGRU tespit)
            -> ATR buyuk -> STOP GENIS (olculdu: %4,26 -> %5,23)
            -> ayni R icin daha buyuk fiyat hareketi gerekiyor
            -> R-normalize sonuc DEGISMIYOR   (olculdu: r = -0,024)
```

🔑 **Skor doğru çalışıyor; sadece ölçtüğü şey kâr getirmiyor.**
Beş bileşenin ayrı ayrı "etkisiz" olması tesadüf değil — **beşi de aynı
büyüklüğü ölçüyor** ve o büyüklük stopa da giriyor, birbirini götürüyor.

Bu, `CLAUDE.md`'nin *"ÖLÇTÜĞÜMÜZ HER ŞEY TEK BANTTAN TÜRÜYOR"* kuralının
skor içindeki hâli.

### B · Aralık sıkışması — ikincil ama gerçek

```
gercek pozisyonlarin skoru: min 21,2 · %25 45,8 · medyan 51,3 · maks 83,1
skor < 45 olan pozisyon: 73 (%21,4)
```

Bot skorun yalnız üst bandını görüyor (kapı ≥45), ve pozisyonların **%21,4'ü**
skor kapısından geçmemiş — çünkü `A+B` ve `MA50+ucuz` kapıları skor
**istemiyor**. Yani skor zaten defterin dörtte birinde devre dışı.

### Yeni bot için ne demek

- Skoru **kapı** olarak kullanmak için gerekçe yok (ölçüldü: kapının kattığı
  değer **+0,006 puan**)
- Skoru **boyutlandırmada** kullanmak için de yok (`skor ~ notional ≈ −0,03`)
- ⚠️ Ama çıkarmak da bedava değil: aday akışını değiştirir → **kendi ön-kaydı** ister

🔑 **Ve asıl ders: yeni botun sinyali YÖN taşımalı.** Hareket büyüklüğü ölçen
her şey, stop harekete göre ölçeklendiği sürece nötr kalır.

**Bot dosyalarına yazım: YOK.**

---

### 🔴 EMİR DEFTERİ DERİNLİĞİ — TEKRAR KOŞUM: ön-kayıt **GEÇTİ (5/5)**, ama yordayıcı **DEFTERİ DEĞİL BOYUTU** taşıyor (2026-09-05)

**Ön-kayıt:** `ON_KAYIT_defter_derinligi.md`, commit `837631d` — **değiştirilmedi.**
İlk koşum 2026-08-30'da O1'de düşmüştü (`t=−1,99`, eşik −2,5) ve kütüğe
*"sıradaki adım: ~4 hafta sonra tekrarla, küme 11 → ~40"* yazılmıştı.

**Betikler:** `scratchpad/defter_derinligi.py` (aynen) · yeni ek sınamalar:
`basi_karistirici.py` · `basi_ic_dis.py` · `basi_ic_stop.py` · `basi_ortak_payda.py`

#### 1 · Ön-kayıt ölçütleri — hepsi geçti

| | ilk koşum (08-30) | bugün (09-05) |
|---|---|---|
| N | 1.056 | **1.858** |
| gün kümesi | 11 | **19** (O1'de eşleşen 17) |
| O1 gün-kümeli t | −1,99 ❌ | **−3,85** ✅ (15/17 gün) |
| O2 monotonluk ρ | −1,000 ✅ | **−1,000** ✅ |
| O3 karıştırıcı | 6/6 ✅ | **7/7** ✅ |
| O4 defterler | 4/4 ✅ | **5/5** ✅ |
| O5 permütasyon | p=0,0000 ✅ | **p=0,0000** ✅ |

**Ön-kayıta göre HÜKÜM: GEÇTİ.** Ölçütler değiştirilmedi (D/9).

⚠️ **Ama planlanan güce ULAŞILMADI ve ulaşılamayacak.** Hedef ~40 kümeydi; 19'da
kaldı çünkü **girişler 2026-09-05'te durduruldu → örneklem DONDU.** Bu bir ara
bakıştır ve ikinci bakıştır (ilk: 11 küme). Ön-kayıt tekrarı öngördüğü için
p-hacking değil, ama **planlanan gücün %43'ü**.

#### 2 · 🔴 ASIL BULGU — yordayıcı bir KOSTÜM

Ön-kayıtta olmayan dört ek sınama koşuldu. Üçü bulguyu **destekledi**, dördüncüsü
**anlamını değiştirdi.**

**Destekleyenler:**

```
stop genisligi ceyreklere gore : 4,27 / 4,16 / 3,84 / 4,03   (Q1/Q4 = 1,06 kat)
   -> CLAUDE.md'nin ZORUNLU sinamasi: hucreler oynaklikta AYRISMIYOR ✅
stop sabitlenince (3 dilim)    : -1,969 / -2,016 / -3,580     3/3 ayni isaret ✅
slipaj mekanizma mi?           : slipaj farki, getiri farkinin %1,3'u -> HAYIR
```

**Anlamı değiştiren — `bası`'yı bileşenlerine ayırmak:**

```
basi = notional / defter_usdt_20

SEMBOL ICINDE, ikisi AYRI AYRI getiriyle:
   r(notional sapmasi, getiri sapmasi) = -0,428   t = -19,54   <- GUCLU
   r(DEFTER   sapmasi, getiri sapmasi) = +0,022   t =  +0,92   <- SIFIR

DEFTER DERINLIGI TEK BASINA, dolar cinsinden (N=1.858):
   r(log defter, DOLAR) = -0,003   t = -0,15                   <- TAM SIFIR
   Q1 (en sig 4.442$) -4,17 $  ·  Q4 (en derin 103.033$) -7,37 $   -> desen YOK
```

🔑 **Emir defteri hiçbir şey taşımıyor. Etkinin tamamı `notional`'dan geliyor.**
`bası`, `notional`'ın gürültülü bir versiyonu — payda yalnızca seyreltiyor:

```
r(log notional, DOLAR) = -0,431  t=-20,57      <- basi'dan GUCLU
```

#### 3 · Ortak payda sınaması — eser DEĞİL, ama YENİ de değil

`bası`'nın **payında** notional var, `ret`'in **paydasında** notional var →
`CLAUDE.md`'nin iki kez ısıran tuzağı. Dolar cinsinden sınandı:

```
Q4-Q1  ret%  : -3,317 puan
Q4-Q1  DOLAR : -47,69 $      gun-eslesmis t = -4,02   17/19 gun negatif
-> isaret AYNI -> saf normalizasyon eseri DEGIL
```

Ve stop sabitlenince notional hâlâ doları öngörüyor (3/3, r = −0,39…−0,49),
`r(log notional, log stop) = −0,324` — yani "büyük pozisyon" ile "dar stop" aynı
şey değil.

**Ama bu bulgu YENİ DEĞİL.** 2026-08-30 kütüğü zaten yazmıştı: *"KAZANAN vs
KAYBEDEN — TEK AYIRICI POZİSYON BÜYÜKLÜĞÜ"* (`d=−0,69`). Bugünkü ölçüm o bulguyu
**üçüncü kez** ve daha güçlü biçimde doğruluyor, emir defteri kılığında.

#### 4 · (a) BOYUTLANDIRMA mı (b) COİN SEÇİMİ mi — ilk koşumun açık bıraktığı soru

İlk koşum *"bu hüküm yazılmadan çözülmeli"* demişti (o gün eşleşen sembol = 6).
Bugün 146 sembolle sabit-etki ayrıştırması yapıldı:

```
ICERIDE  (sembol sabit) r = -0,358  t = -15,82   <- GUCLU
DISARIDA (sembol ort.)  r = -0,119  t =  -1,44   <- GORULMUYOR
```

**Cevap: (a) BOYUTLANDIRMA.** Coin seçimi değil.
⚠️ Ama (2) ışığında bu *"pozisyonu defter derinliğine göre kırp"* demek **değil** —
defterin katkısı sıfır. Sadece *"büyük notional kötü"* diyor.

#### 5 · 🔴 NEDEN — MEKANİZMA BİLİNMİYOR

Kâğıt defterde pozisyon büyüklüğü fiyatı **etkileyemez**, ve slipaj farkın
%1,3'ünü açıklıyor. Yani **nedensel bir kanal gösterilemiyor.** `CLAUDE.md`'nin
kuralı burada bağlayıcı: *"nedensel yolun üzerinde demeden önce yolun var
olduğunu göster."* Gösterilemedi → bu bir **korelasyon**, kural değil.

#### 6 · SONUÇ — `CLAUDE.md`'nin 4. bant-dışı adayı HÂLÂ ÖLÇÜLMEDİ

**Bekleyen likidite ölçülmüş sayılmaz.** Sebebi kayıtlıydı ve şimdi kanıtlandı:

> *"Defterin **tek tarafı** saklanıyor → dengesizlik ölçülemez, emir defterinin
> klasik kenarı hâlâ ölçülmemiş durumda."*

Kaydedilen `defter_usdt_20` = **yediğimiz taraf**. Emir defterinin gerçek sinyali
**dengesizliktir** (bid vs ask) ve o hiç kaydedilmedi. Bugünkü ölçüm, kaydedilen
tarafın **sıfır bilgi** taşıdığını gösterdi (r = −0,003).

**Bot dosyalarına yazım: YOK.**

---

### ❌ ÇAPRAZ BORSA (BINANCE − BYBIT FONLAMA FARKI) — **DÜŞTÜ**, ve işaret **HİPOTEZİN TERSİ** çıktı (2026-09-05)

**Ön-kayıt:** `ON_KAYIT_capraz_borsa.md`, commit `a0e52c5` — koşumdan **önce**.
**Betikler:** `scratchpad/capraz/00_yoklama.py` · `01_indir.py` · `02_veri.py` · `03_olcum.py`
**N:** 1.233.872 gözlem · **460 sembol** · **730 gün** (2024-09-01 … 2026-08-31)
İndirme: 460 sembol, **0 hata, 0 ban**, 104,6 dk, 2,78 M fonlama kaydı.

`CLAUDE.md`'nin bant-dışı listesinden **ikinci** denenen aday (ilki basis).

| ölçüt | sonuç | |
|---|---|---|
| **C1** 🔴 | **rho = +0,0108 · t = +4,11** · N=730 gün | ❌ **iki koldan birden** |
| **C2** dört çeyrek | −0,0039 · +0,0020 · **+0,0246** · **+0,0203** | ✅ 3/4 |
| **C3** rejim | BOĞA +0,0002 · NÖTR +0,0049 · **AYI +0,0283** | ✅ 3/3 |
| **C4** eleme | spearman(f_bin, fark) = **+0,430** (tavan 0,50) | ✅ |
| **C5** fonlama üçte-birlik | **alt +0,0212** · orta +0,0018 · üst +0,0025 | ✅ 3/3 |

**HÜKÜM: DÜŞTÜ.**

#### 🔴 C1 İKİ AYRI SEBEPTEN DÜŞTÜ — ve ikincisi daha önemli

```
1) |rho| = 0,0108  <  taban 0,020        -> etki cok kucuk (basis'in tekrari)
2) isaret POZITIF  <- on-kayit NEGATIF diyordu
```

Ön-kayıt açıkça yazmıştı: *"fark yüksek = Binance'te uzun taraf kalabalık →
`rho < 0`"*. Ölçülen işaret **pozitif**, ve **tesadüf değil**: t=+4,11, çeyreklerin
3/4'ü, rejimlerin 3/3'ü, fonlama dilimlerinin 3/3'ü pozitif.

🔑 **Yani ekonomik sezgim tersineydi.** Yüksek Binance fonlaması *ortalamaya dönüş*
değil, **momentum** öncülüyor. Basis'te işaret doğru çıkmıştı; burada çıkmadı.

#### 🔴 DÖRT YÖNLÜ TAHMİNİN ÜÇ BUÇUĞU YANLIŞ

| # | tahmin | sonuç |
|---|---|---|
| 1 | *"işaret negatif, \|rho\| < 0,02"* | **yarısı** — büyüklük doğru, **işaret yanlış** |
| 2 | *"C6 (kuyruk) havuzdan güçlü çıkacak"* | ❌ **rho = −0,0002, t = −0,03 — TAM SIFIR** |
| 3 | *"AYI'da etki zayıflayacak"* | ❌ **AYI en güçlü yer** (+0,0283 vs BOĞA +0,0002) |
| 4 | *"fark çoğunlukla kalıcı sembol bileşeni"* | ❌ kalıcı **+0,0006 (sıfır)**, zamanla değişen +0,0100 (t=+3,79) |

Özellikle **2** kayda değer: kuyruk ölçütü ön-kayıta *tam da* yoklamada kalın
kuyruk görüldüğü için konmuştu. Kuyrukta **hiçbir şey yok.**

#### 🔴 C2 ile C3 BAĞIMSIZ KANIT DEĞİL — aynı olgu

Ölçümden sonra kontrol edildi:

```
ceyrek                       BOGA   NOTR    AYI
C1 2024-09-01..2025-03-01      20    162      0
C2 2025-03-02..2025-08-30      47    120     15
C3 2025-08-31..2026-02-28      22     71     89
C4 2026-03-01..2026-08-31      11     73    100

AYI payi: ilk yari %4  ·  son yari %52
```

*"Etki son iki çeyrekte"* ile *"etki AYI'da"* **aynı cümle**. İki ölçüt sanılan
şey tek gözlemdir. Ön-kayıt bunu ayırmamıştı — **eksiklik ön-kayıtta.**

#### BASIS İLE AYNA GÖRÜNTÜSÜ

| | basis (08-26) | çapraz borsa (09-05) |
|---|---|---|
| işaret | hipotez yönünde (−) | **hipotezin TERSİ (+)** |
| en güçlü rejim | **BOĞA** −0,0396 | **AYI** +0,0283 |
| AYI | +0,0002 (yok) | +0,0283 (en güçlü) |
| zaman | **sönüyor** (→ +0,0004) | **büyüyor** (→ +0,0203) |
| t | −4,85 | +4,11 |
| \|rho\| vs 0,020 | 0,0152 ❌ | 0,0108 ❌ |

🔑 **İki bant-dışı aday, ikisi de t>4, ikisi de etki tabanının ALTINDA.**
Bu artık bir örüntü: bant dışında bilgi **var**, ama tek başına kullanılabilir
büyüklükte **değil**.

#### ⚠️ ÖN-KAYITTA OLMAYAN EK HESAP — hüküm DEĞİL, kural DEĞİL

Hükmü somutlaştırmak için rho paraya çevrildi (**post-hoc**, ölçütlere sayılmaz):

```
ust ondalik - alt ondalik, gunluk:
  TUM PENCERE  +0,3927%  t=+5,29      BOGA +0,3288%  t=+1,33
  NOTR         +0,2607%  t=+2,83      AYI  +0,6998%  t=+5,14
```

🔴 **Bu sayı kural yapılamaz, dört sebeple:**
1. **Ön-kayıtta yoktu.** Birincil ölçüt rho'ydu ve düştü. *"Tabloya bakıp en
   yüksek sayıyı kural yapmak bu projede reddedilmiş bir davranıştır."*
2. **Maliyet karşılanmıyor:** uzun+kısa **iki bacak** ≈ %0,38; ölçülen +0,39%.
   Başabaş. Slipaj (ölçülen medyan %0,0499/bacak) eklenince **altına düşer**.
3. **Bu botun yapabileceği bir şey değil:** ondalık sepeti her tarafta ~46
   eşzamanlı pozisyon ister; bot **8 slot**.
4. AYI hücresi (+0,6998) **seçilmiş hücredir** ve AYI = son bir yıl (yukarı bak).

#### SINIRLAR

- Etiket **ham getiri**; fonlama/ücret dahil değil.
- Tek ufuk (+24s), ön-kayıtta sabit. Başka ufka **bakılmadı**.
- `C4 = +0,430` tavana (0,50) yakın — fark, Binance fonlamasından **bağımsız değil**.
  Yoklamadaki +0,275 yalnız 20 sembolle ölçülmüştü; tam evrende **daha yüksek**.
- 460 sembol = Binance perp evreninin %87'si; Bybit'te olmayan 64 sembol dışarıda.
- Çoklu karşılaştırma **16 hücre** (ön-kayıtta ilan edilmişti).

#### 🔑 BİRİM KIRILMASI GERÇEKTİ — ön-kayıtın en değerli kararı

Günlük orana çevirme zorunlu kılınmasaydı ölçümün büyük kısmı **farklı
birimleri** kıyaslayacaktı:

```
binance  1s:  63.577 · 2s:    587 · 4s: 994.703 · 8s: 253.851
bybit    1s: 283.440 · 2s: 65.999 · 4s: 802.289 · 8s: 317.585
```

1 saatlik kovada **4,5 kat**, 2 saatlikte **112 kat** fark. Ayrıca aralık
**sembol içinde zamanla değişiyor** → global medyan yetmezdi, yerel
normalizasyon gerekti. Sınama (düzenli 8s · düzenli 4s · 48s delik · aralık
değişimi) **4/4** geçti.

**Bot dosyalarına yazım: YOK.**

---

### 🔑 ARŞİV BULGUSU — "30 GÜNLÜK SINIF" ve "EMİR DEFTERİ GEÇMİŞİ YOK" **İKİSİ DE YANLIŞMIŞ** (2026-09-05)

**Tür:** 🟢 **OLGU DÜZELTMESİ** — hipotez sınaması değil, iki kayıtlı olgunun
doğrudan yoklanması. Ön-kayıt gerekmez (hüküm değil, veri varlığı sorusu).
**Betikler:** `scratchpad/defter_gecmis_yoklama.py` · `scratchpad/arsiv_30gun_kaniti.py`
**Tetikleyen:** kullanıcı — *"emir defterinde sinyal bulabilir miyiz?"*

`data.binance.vision` günlük dosyaları yoklandı. İki kayıtlı olgu çürüdü.

#### 1 · "30 günlük sınıf" — ARŞİVDE 2+ YIL VAR

`daily/metrics/<SYM>/` dosyaları dört *"çekilemez"* ucun **ta kendisi**.
Belirleyici sınama: arşiv vs canlı uç, damga kayması −10…+10 dk tarandı.

```
alan                               kayma(dk):bagil_hata
sum_open_interest                  -10:2e-02  -5:2e-02  +0:2e-02  +5:0e+00  +10:2e-02
count_toptrader_long_short_ratio   -10:3e-02  -5:3e-02  +0:2e-02  +5:3e-04  +10:2e-02
sum_toptrader_long_short_ratio     -10:3e-02  -5:3e-02  +0:2e-02  +5:2e-05  +10:2e-02
count_long_short_ratio             -10:2e-02  -5:2e-02  +0:2e-02  +5:3e-04  +10:2e-02
sum_taker_long_short_vol_ratio     -10:3e+00  -5:3e+00  +0:1e-03  +5:3e+00  +10:3e+00

-> 5/5 alanda bir kaymada bagil hata < 1e-3  =>  AYNI VERI
```

⚠️ **`create_time` = canlı ucun damgası − 5 dk** (taker hariç, o kaymasız).
Join'den önce kaydırılmazsa **sessizce %2 hata** girer.

**Kapsam:** 2023-09'a kadar (1100 gün), ~11 kB/sembol/gün.

**Kaydedilmiş kayıp geri alınabilir:** *"58 sembolde 07-23…07-26 arası kalıcı
olarak gitti"* — dört günün **dördü de arşivde**, tek tek doğrulandı.

🔑 **`topLongShortAccountRatio` hiç arşivlenmemişti** (`radar.py:63` üçünü çekiyor).
Yani `top_ls − glob_ls`'in *"bulgu yok"* hükmü **karışık bir büyüklük** üzerineydi:
hem nüfus (üst %20 vs herkes) hem normalizasyon (pozisyon vs hesap) aynı anda
değişiyordu. **Temiz ayrıştırma ilk kez mümkün:**

```
topPosition / topAccount  = ayni nufus, boyut asimetrisi   <- HIC olculmedi
topAccount  / globAccount = ayni normalizasyon, nufus farki <- HIC olculmedi
```

#### 2 · EMİR DEFTERİ GEÇMİŞİ — VAR, ve İKİ TARAF BİRDEN

`olcumler.md:1190` *"emir defteri geçmişi YOK → yalnız ileriye"* diyordu.
`daily/bookDepth/<SYM>/` **900+ gün** geriye var:

```
timestamp,percentage,depth,notional
2026-08-26 00:00:04,-5.00,891825.24,84013805.96     <- ALIS tarafi
...
2026-08-26 23:59:31, 5.00,865711.88,90466597.73     <- SATIS tarafi
```

- ±%1 · ±%2 · ±%3 · ±%4 · ±%5 seviyeleri, **her iki taraf**
- **~30 saniyede bir** anlık görüntü (2.880/gün)
- ~0,5 MB/sembol/gün · küçük altcoinlerde de var (test: SOL·BONK·AEVO·ACH·ZRX)

**Dengesizlik hesaplanabiliyor ve oynuyor** (SOLUSDT, 1 gün):

```
±1%  medyan -0,0087  %10 -0,0850  %90 +0,1159  std 0,0758
±2%  medyan +0,0549  %10 -0,0528  %90 +0,2096  std 0,1010
±5%  medyan +0,0828  %10 +0,0416  %90 +0,1134  std 0,0279
```

#### 3 · NEDEN BU ÖNEMLİ — bugünkü derse bağlanıyor

Aynı gün ölçüldü: kaydedilen `defter_usdt_20` **tam sıfır** taşıyor
(`r=−0,003 · t=−0,15`). Sebebi artık açık — o bir **büyüklük** ölçüsü, tıpkı
skorun %89'u gibi. Emir defterinin **yön** taşıyan büyüklüğü dengesizliktir ve
**hiç ölçülmedi**.

⚠️ **Ölçülmeden önce bilinen risk:** mikroyapı literatüründe dengesizlik
**saniye–dakika** ufkunda öngörür. Bot 7,5 dk turla çalışıp **saatlerce** tutuyor.
Ufuk uyuşmazlığı bu adayın en olası ölüm sebebidir ve ön-kayıtta **ufuk merdiveni**
(+5dk · +30dk · +1s · +4s · +24s) ilan edilmelidir.

⚠️ **Boyut:** 0,5 MB/sembol/gün. 150 sembol × 365 gün ≈ **27 GB** — kapsam
ön-kayıtta sınırlandırılmadan indirme başlatılmaz.

**Bot dosyalarına yazım: YOK.**

---

### ❌ EMİR DEFTERİ DENGESİZLİĞİ (OBI) — **DÜŞTÜ**, ve merdiven "hiç yok" dedi (2026-09-06)

**Ön-kayıt:** `ON_KAYIT_obi.md`, commit `0db685f` — koşumdan **önce**.
**Betikler:** `scratchpad/obi/00_pilot.py` · `01_indir.py` · `02_veri.py` · `03_olcum.py`
**N:** 513.476 gözlem · **119 sembol** · **180 gün** (2025-09-07 … 2026-08-31)
İndirme 145 dk; **10 GB ham `bookDepth` akışta işlendi, diske hiç yazılmadı.**

`CLAUDE.md`'nin bant-dışı listesindeki **son** aday.

| ölçüt | sonuç | |
|---|---|---|
| **P1** 🔴 ±%1 · +1 saat | **rho = −0,0077 · t = −0,88** | ❌ |
| **P2** dört çeyrek | +0,002 · −0,015 · −0,042 · +0,025 | ❌ 2/4 |
| **P3** rejim | BOĞA +0,007 · NÖTR +0,002 · AYI −0,017 | ❌ 1/3 |
| **P4** eleme | spearman(önceki 1s getiri, OBI) = **−0,037** | ✅ |
| **P5** getiri üçte-birlik | −0,012 · +0,001 · −0,012 | ✅ 2/3 |

**HÜKÜM: DÜŞTÜ.**

#### 🔑 UFUK MERDİVENİ — ön-kaydın en değerli parçası, ve cevabı NET

```
+5 dk   rho -0,0074  t -0,97
+30 dk  rho -0,0044  t -0,54
+1 saat rho -0,0077  t -0,88     <- BIRINCIL
+4 saat rho -0,0031  t -0,38
+24 saat rho +0,0031 t +0,40
```

Merdiven iki başarısızlığı ayırmak için konmuştu:

```
hicbir basamakta yok  ->  sinyal YOK
+5dk var, +1s yok     ->  sinyal VAR ama BIZIM ufkumuzda degil
```

🔑 **Cevap birincisi. Beş basamağın beşi de sıfır — `+5 dakika` dahil.**
Yani *"mikroyapı sinyali var ama bot çok yavaş"* açıklaması **çürüdü.** Bu proje
bu ayrımı ilk kez yapabildi ve sonuç en temiz olanı.

#### 🔴 BEKLENTİLERİMİN İKİSİ BİRDEN YANLIŞ

| tahmin | sonuç |
|---|---|
| *"+5dk basamağında bir şey görünmesi ~%70"* | ❌ **görünmedi** (t=−0,97) |
| *"merdiven monotonik sönecek, +5dk en güçlü"* | ❌ **düz sıfır**, sönüm deseni yok |
| *"P4 geçecek ama sıfırdan uzak"* | ❌ geçti ama **−0,037 = neredeyse tam sıfır** |
| *"kalıcı sembol bileşeni bir şey taşımayacak"* | ✅ **+0,0004** |

`P4 = −0,037` ayrıca bir olgu: OBI, son saatlik fiyat hareketinin izi **değil**.
Yani gerçekten bağımsız bilgi — **ama boş bir bilgi.**

#### ⚠️ ±%5 SEVİYESİ EŞİĞİ GEÇTİ — ve KURAL YAPILMIYOR

```
±%1 (BIRINCIL)  rho -0,0077  t -0,88
±%2             rho -0,0169  t -2,32
±%5             rho -0,0455  t -5,79     <- taban 0,020'nin USTUNDE
```

Seviyede **monotonik** bir desen var. Ama:

1. **Ön-kayıt `±%1`'i birincil ilan etmişti** ve açıkça *"seviye SEÇİLMEYECEK —
   birincil ±%1'dir, sonuç ne olursa olsun"* yazıyordu. `±%5`'i şimdi seçmek
   **tam olarak** *"en iyi hücre seçilmez"* ihlalidir.
2. **İşaret hipotezin TERSİ** (kalın alış → **düşük** getiri).
3. 🔴 **`P4` elemesi yalnız `±%1` üzerinde koşuldu.** `±%5`'in karıştırıcı durumu
   **ÖLÇÜLMEDİ** — ve geniş bantta *"fiyat nereden geldi"* izi çok daha güçlü
   olabilir. Yani `±%5` bulgusunun elemesi **hiç yapılmadı**.

**Not:** ayrı bir ön-kayıtla sınanabilir. Bu satır bir kural önerisi **değildir**.

#### YAPISAL OLGU

```
OBI ±%1: ort +0,0970 · medyan +0,0955 · std 0,1546 · POZITIF oran %82,1
```

Defterin alış tarafı **yapısal olarak** daha kalın (pilotta da görülmüştü).
Kesitsel sıralama bunu soğuruyor; seviyeye bakan hiçbir hüküm yazılmadı.

#### 🔑 BANT-DIŞI LİSTE KAPANDI — ÜÇ ADAY, ÜÇÜ DE DÜŞTÜ

| aday | rho | t | taban 0,020 |
|---|---|---|---|
| spot-perp basis | −0,0152 | −4,85 | ❌ |
| çapraz borsa | +0,0108 | +4,11 | ❌ |
| **emir defteri (OBI)** | **−0,0077** | **−0,88** | ❌ |

İlk ikisi en azından `t>4` veriyordu — *"yön aynı, güven yalan"*. OBI **onu bile
vermiyor**: `|t| < 1`, yani sıfırdan ayırt edilemiyor.

⚠️ Geriye kalan tek denenmemiş şey: **pozisyon kompozisyonunun TEMİZ ayrıştırması**
(`topPosition/topAccount`), ki o da bugün mümkün oldu (`metrics` arşivi).

#### SINIRLAR

- Etiket **ham getiri**; maliyet/slipaj dahil değil (etki sıfır olduğu için önemsiz).
- `bookDepth` **~30 sn**'de bir; daha ince mikroyapı (emir defteri güncellemeleri,
  `bookTicker`) **bakılmadı** — o veri USD-M futures'ta yayınlanmıyor.
- 120 sembol, tohumla rastgele; 119'u geçerli.
- Çoklu karşılaştırma **21 hücre** (ön-kayıtta ilan edilmişti).

**Bot dosyalarına yazım: YOK.**

---

### ❌ MUM FORMASYONLARI — **DÜŞTÜ** (BOĞA penceresi, 2026-09-06)

**Ön-kayıt:** `ON_KAYIT_formasyon.md`, commit `dd66728` — koşumdan **önce**.
**Betikler:** `scratchpad/formasyon/00_guc.py` (güç) · `01_olcum.py`
**N:** 182.561 bar · **567 sembol** · **14 gün** (2026-08-22 … 2026-09-04)
**Pencere kullanıcı kararı:** *"2 yıllık veriyle değil bizim 22 ağustos sonrası
verimizle test et"* — gerekçe: 2 yıllık veri AYI ağırlıklı, bu pencere BOĞA.
**Doğrulandı: 14 günün 14'ü de BOĞA.**

| ölçüt | sonuç | |
|---|---|---|
| **F1** 🔴 `pin_BOĞA − pin_AYI` (+4s) | **−0,0547 puan · t = −0,56** · 7/14 gün | ❌ |
| **F2** her yön kendi kontrolünü geçer | BOĞA **−0,055** (pozitif olmalıydı) · AYI −0,000 | ❌ |
| **F3** ufuk tutarlılığı | −0,034 · −0,055 · −0,040 | ✅ 3/3 (ama **ters** yönde) |
| **F4** 🔑 negatif kontrol (doji) | −0,0279 · t=−1,47 · `\|etki\|` **< MDE** | ✅ |
| **F5** 🔴 yoğunlaşma | en iyi 2 gün çıkınca **−0,1227** | ❌ |

**HÜKÜM: DÜŞTÜ.**

#### F1 "GÖREMİYORUZ" BANDINA DÜŞTÜ — ve bu önceden ilan edilmişti

```
|etki| = 0,055   ·   MDE = 0,965   ->  sifirdan ayirt EDILEMIYOR
```

Ön-kayıt bölüm 2 tam bunu öngörmüştü: *"0,2–0,97 puan arası etkiler maliyeti
aşar ama MDE'nin altında kalır; o bantta sonuç GÖREMİYORUZ olur ve ETKİ YOK
DEĞİLDİR."* **Ama ölçülen etki o bandın da çok altında (0,055)** — yani
*"kenar var ama göremedik"* savunması burada da zayıf.

#### 🔑 SEÇİM GEREKÇESİ TUTTU — formasyon gerçekten yeni bilgiymiş, ama BOŞ

Pin bar, *"OHLC'nin hiç kullanmadığımız tek parçası"* diye seçilmişti
(`comp` fitili yalnız **büyüklük**, `pos` yalnız **20 barlık** konum olarak
kullanıyor). Doğrulandı:

```
r(pin yonu, barin kendi getirisi) = -0,148   <- last1'in kiligi DEGIL
r(pin yonu, hacim carpani)        = -0,004   <- vol_x'in kiligi DEGIL
```

**Yani aday gerçekten bağımsız bilgiydi ve yine boş çıktı.** Bu, basis'in
dersinin tekrarı: *"yeni bilgi taşımak"* ile *"kullanışlı olmak"* ayrı şeyler.

#### 🔴 DÖRT TAHMİNİN İKİSİ TUTTU

| tahmin | sonuç |
|---|---|
| *"en olası sonuç F1'in göremiyoruz bandına düşmesi"* | ✅ **tuttu** |
| *"doji hiçbir şey göstermeyecek"* | ✅ **tuttu** (F4 geçti) |
| *"yutan pin'den zayıf çıkacak"* | ❌ **yanlış** — yutan `t=−1,93`, pin `t=−0,56` |
| *"etki varsa kısa ufukta en güçlü"* | ❌ etki yok; üç ufuk da düz (0,034/0,055/0,040) |

#### ⚠️ İKİ GÖZLEM — kural DEĞİL, aday DA değil

1. **Her iki formasyon da TERS yönde.** `yutan_BOĞA − yutan_AYI = −0,1285`
   (t=−1,93), `pin` −0,0547. Yani *boğa formasyonları ayı formasyonlarından
   KÖTÜ*. Yutan conventional anlamlılığa yakın — **ama ikincil hücre, MDE altı,
   tek rejim, 14 gün ve post-hoc yön dönüşü.** Kural yapılmaz.
2. 🔴 **F3 "geçti" ama okunuşu yanıltıcı:** üç ufkun üçü de aynı işaretli, fakat
   o işaret **hipotezin tersi**. Ölçüt tutarlılık istiyordu, yön değil — bu bir
   ön-kayıt eksiğidir ve not düşülüyor.

#### ZORUNLU SINAMALAR

- **Sınıflandırma sınaması 6/6 geçti** — çekiç · kayan yıldız · doji ·
  **HİÇBİRİ (aşırı etiketleme yok)** · boğa yutan · ayı yutan.
  Negatif durum bilerek konmuştu: *"hareket bitişi"* ölçümü olayların **%99,96'sını**
  etiketleyip ölmüştü. Burada oranlar sağlıklı: pin %5,4 · yutan %8,5 · doji %11,4.
- **Oynaklık ayrışması YOK** (0,98–1,00× taban) → `chg24` bandının düştüğü tuzak
  burada yok, mekanikli ölçüm de yanıltmazdı.
- **Ayna sağlaması geçti** (yönler takas edilince işaret tam döndü).

#### SINIRLAR

- **Tek rejim (14/14 BOĞA)** → genellenemez. Rejim kırılımı yapılamadı.
- Etiket **ham getiri**; maliyet %0,19 dahil değil (etki zaten sıfıra yakın).
- Yalnız **üç** formasyon; standart tanımlar, **parametre taraması yok**.
  Başka formasyonlar denenmedi — ve denenirse çoklu karşılaştırma büyür.
- Çoklu karşılaştırma **18 hücre** (ön-kayıtta ilan edilmişti).

**Bot dosyalarına yazım: YOK.**

---

### 🟡 BOĞA BACAĞI — 14 GÜNLÜK PENCEREMİZ DOSYAYLA KIYASLANAMIYOR (2026-09-06)

**Tür:** 🟡 **BETİMLEYİCİ** — ön-kayıt yok, hüküm yok, kural çıkmaz.
**Betik:** `scratchpad/boga_bacagi_bugun.py`
**Tetikleyen:** kullanıcı — *"elimizdeki 14 günlük boğa verisi burdakiyle tutuyor mu?"*

#### 1 · Örtüşme YOK

```
boga_bacagi_islemler.json : 2019-07-23 .. 2026-07-13   (N=410)
bizim pencere             : 2026-08-22 .. 2026-09-04
ortak kayit               : 0
```

Aynı işlemleri kıyaslamak **mümkün değil**. Yapılabilen tek şey aynı kuralı
boşluk döneminde koşturmaktı.

#### 2 · Kural taze veride koşuldu — ama N çok küçük

Önbellek `2026-08-09`'da bitiyordu; **ezmeden** birleştirildi (+5.546 bar,
artık `2026-09-06`'ya kadar).

```
bosluk (2026-07-14 -> bugun)  COZULEN  N=1   net +1,976
                              KIRPIK   N=3   net +0,358   (30 gunu dolduramadi)
BIZIM 14 GUN                           N=1   net +0,973   (NEAR, 08-22, 16 gun)
```

🔴 **Pencerede 25 büyük sembolde toplam BİR tetik oluştu.** F1'in örnekleme
hızı bunu açıklıyor: 2020-21'de 19 ayda 132 işlem ≈ ayda 7. 14 günde beklenen
~3; biz 1 gördük. **N=1 hiçbir şey söylemez** — *"tutuyor mu"* sorusu bu kural
için **cevapsız**.

#### 3 · 🔑 KIYAS YERİNE ASIL BULGU — dosyanın kendi son dönemi

```
[dosya] 2020-21 BOGA   N=132  net +0,299  kazanan %45
[dosya] 2023-24 BOGA   N=170  net +0,071  kazanan %39
[dosya] 2022 AYI       N= 31  net +0,072  kazanan %39
[dosya] 2025-26 SON    N= 62  net -0,531  kazanan %16   <- KESKIN AYRISMA
```

**2025-26 dönemi geçmiş boğalardan keskin biçimde ayrışıyor** ve bu N=62'ye
dayanıyor, N=1'e değil. Kazanma oranı %39-45'ten **%16**'ya düşmüş.

⚠️ Bu bir hüküm değil — dönem ayrımı takvimseldi ve `2025-26 SON` etiketi
orijinal ölçümde kurulmuştu. Ama *"bugünkü boğa 2021 boğasına benziyor mu"*
sorusuna eldeki en iyi veri bu ve cevabı **hayır** yönünde.

#### 4 · SINIRLAR

- **N=1** — pencere ölçüm için değil, kuralın örnekleme hızı için kısa.
- Kural **spot günlük** barla ölçülüyor; bot **perp saatlik** ile çalışıyor.
- `KIRPIK` kayıtlar 30 günü dolduramadı, ayrı tutuldu — karıştırmak yanlı olurdu.
- Orijinal hüküm **KALDI** (`olcumler.md:132`): +0,046R vs kontrol +0,062R.
  Bu betik o hükmü **değiştirmez**.

**Bot dosyalarına yazım: YOK** (yalnız `klines_cache` birleştirilerek güncellendi).

---

## TAKER ≥ 1.0 KAPISI — 2026-09-06 · **DÜŞTÜ (5/5)** ama ÖN-KAYIT KUSURLU

**Ön-kayıt:** `ON_KAYIT_taker_kapisi.md` · commit `08c8876` — koşumdan **önce**
**Betikler:** `scratchpad/taker/00_yoklama.py` · `01_mum_indir.py` · `02_olcum.py`
**Soru:** NOTR-LONG zincirinin son kapısı `taker ≥ 1.0` bilgi taşıyor mu?

**N = 956 aday · 57 gün · 121 sembol · 378 (`≥1.0`) / 578 (`<1.0`)**
Popülasyon: `stage` aktif + skor eşiği + `smart == LONG` (kapının **önündeki** zincir).

#### Hüküm

| # | ölçüt | eşik | sonuç |
|---|---|---|---|
| K1 | ham fark > 0 (+24s) | >0 | **DÜŞTÜ** `−0,353` |
| K2 | `last1` sabitlenmiş fark | ≥ +0,30 | **DÜŞTÜ** `−0,293` |
| K3 | gün-kümeli t | ≥ +2,0 | **DÜŞTÜ** `−0,79` (39 gün) |
| K4 | merdivende ≥3 basamak aynı işaret | evet | **DÜŞTÜ** `1/5` |
| K5 | en iyi 2 gün çıkınca hâlâ K1 | evet | **DÜŞTÜ** `−0,807` |

Ufuk merdiveni (ham fark): `+1s −0,124` · `+4s −0,148` · `+12s **+0,897**` ·
`+24s −0,353` · `+48s −0,531`. Sabitleyicilerin **dördü de** negatif
(`last1 −0,293` · `last3 −0,209` · `pos −0,420` · `vol_x −0,485` · `chg24 −0,614`).

#### 🔴 ÖN-KAYITIN KUSURU — etki tabanını MDE'den ÖNCE koydum

```
+24s SE = 0,916 puan   ->   MDE (2,8*SE) = 2,57 puan
on-kayitta koydugum etki tabani = 0,30 puan
0,30'u gormek icin gereken N ~ 69.000  (mevcudun 73 KATI)
```

**K2 daha yazıldığı anda geçilemezdi** — etki tabanı örneklemin görebileceğinin
**sekizde biri**. Bu, ölçümün değil **ön-kaydın** hatası ve aynen kayda geçiyor.

**Bu yüzden doğru okuma şudur:** `|−0,353| ≪ MDE` → *"göremiyoruz"*,
**"etki yok" DEĞİL**. Söylenebilen tek şey: **+2,57 puandan büyük bir yarar
YOK** — o büyüklükte olsa görülürdü.

#### Ne KULLANILMADI

- `+12s` tek başına pozitif (`+0,897`, t=1,99). **Seçilmedi** — "en iyi hücre
  seçilmez"; merdivenin 4/5 basamağı ters işaretli.
- Ters işaret **kural yapılmadı** (ön-kayıt bölüm 9 uyarısı): tek pencere.

#### Zaman damgası hizası — zorunlu doğrulama

`radar_archive.ts` **yerel (UTC+3)** çıktı: kayma `+3 sa` medyan bağıl hata
`0,00502`, `0 sa` ile `0,01747`. Bu sınama yapılmasa **tüm ileri getiri 3 saat
kayardı**. `create_time` dersinin (metrics arşivi, −5 dk) aynı sınıfı.

#### Negatif kontrol — ön-kayıt gereği geçti, ama tasarımı zayıftı

`glob_ls` aynı eşikle: ham `−1,802`, sabitlenmiş `−2,530`. K2 (`≥ +0,30`)
geçilmedi → düzenek "sağlam" sayıldı. ⚠️ **Ama ölçüt tek yönlüydü**;
`|−2,53|` büyük bir nokta tahmini ve "hiçbir şey" demek değil. Kollar
784/160 ile çok dengesiz. Negatif kontrol ölçütü **çift yönlü** yazılmalıydı.

#### Sonuç ve etkisi

Kapı **ölçülebilir bir yarar göstermiyor** ve adayların **%56'sını** kesiyor
(arşiv tabanı: `smart-LONG 367 → taker≥1.0 161`). `notrlong` bu kapıda
terminal darboğaz yaşıyor (stage+skor geçen 6 adayın 6'sı burada öldü).

**Karar verilmedi** — kaldırma `notrlong`'un hangi işlemi açacağını değiştirir
(D/8 → pencere sıfırlanır) ve kullanıcı onayı gerektirir.
