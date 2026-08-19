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

