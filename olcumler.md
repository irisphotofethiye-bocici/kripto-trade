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
