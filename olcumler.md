# Ölçüm Kütüğü

`fikir-defteri.md` 251 KB / 3.908 satır / 271 başlık — bağlama sığmıyor. Bu dosya
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
| A+B'ye sabit %10 hedef | 08-10 | 206 | **GEÇTİ** — +2,01% vs mevcut +1,24% | — | eşik notu |

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
| Erken müdahale (N dk'da artıda değilse kapat) | 08-13 | 44 poz | **KARARSIZ** — durum haber verici ama kural kararsız (+1.170 / −227 / +161 / −222); kural çıkarılmadı | `erken_mudahale.py` | s.3755 |

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
| Kanal + StochRSI | 08-11 | — | **KALDI** — 6 varyantın 6'sı da | `kanal_stoch.py` · `kanal_ham.py` · `kanal_stopsuz.py` | s.1892 · s.1966 |
| Scalp varyantı + rejim iddiası | 08-11 | — | **KALDI** — 6 rejim bölmesinin 6'sı da | `kanal_scalp.py` | s.2048 · s.2131 |
| "Sinyalde bilgi yok" iddiası | 08-11 | — | **ÇÜRÜDÜ** (kendi iddiam) — karar değişmedi ama gerekçe değişti | — | s.2140 |
| Hareket öncesi örüntü | 08-10 | — | **ÇÜRÜDÜ** — örüntü tanımlayıcı, tahmin edici değil | `oncesi_oruntu.py` · `oncesi_short.py` | s.1373 · s.1334 |
| Yükselenlerin ortak örüntüsü | 08-10 | — | **ÇÜRÜDÜ** — işaret olarak ters | `yukselen_oruntu.py` | s.1288 · s.823 |
| Ölü sinyallerin kaçı canlıydı? | 08-11 | arşiv | kayıt: s.2210 | `olu_sinyal_tarama.py` | s.2210 |
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
| %10 hedef ölçümü / long arayışı | 08-10 | — | kayıt: s.1101 | `hedef10.py` | s.1101 |
| Hedef boyutu — "long hedefini %2,5 yapsak" | 08-10 | — | kayıt: s.1186 | `long25_stop.py` | s.1186 |

## Rejim / altyapı

| ölçüm | tarih | N | hüküm | betik | defter |
|---|---|---|---|---|---|
| F10 sezon+hava rejim katmanı | 07-22 | 2022–2026 | **KISMEN** — çekirdek amaç (ayı-tepki-rallisini boğa sanmama) başarılı; 2023 tabanı fazla erken TAM_BOGA | `f10_sezon_test.py` | s.80 |
| Karar penceresi / S9 ön-kaydı | 08-11 | — | ön-kayıt: s.1807 | — | s.1762 |
| Düşüş freni riski | 08-11 | — | kenar kendini gösteremeden bot duruyor | `fren_riski.py` | s.1692 |
| Sistem denetimi | 08-11 | — | **9 doğrulanmış hata** → `denetim-raporu.md` | `denetim_olcum.py` | s.2371 |
| Defter izolasyon testi | 08-13 | 14 kontrol | **GEÇTİ** — 4 defterin hepsi | `defter_izolasyon_testi.py` | s.3469 |
| Ölçüm ağırlık hatası (ilk parti) | 08-11 | — | **düzeltildi** — ölçümün ağırlığı yanlıştı | `boyut_agirlik.py` | s.1609 |

## Bekleyen — ölçülmedi

| soru | neden bekliyor |
|---|---|
| `d_taker` — agresörün pozisyon ömrü boyunca **kayması** | Veri 2026-08-13'te toplanmaya başladı, geriye dönük üretilemez. ~27 Ağustos'ta yeterli olur |
| `MA50+ucuz` kapısının **fonlama** yükü | Kapı 2 yılda ölçüldü ve çürütüldü (s.2790) ama o test fonlama maliyetini içermiyordu. A+B'yi bitiren hesap bu kapı için yapılmadı. **Beklenti A+B'nin aynısı olmamalı:** A+B fonlamayı *tanım gereği* seçiyordu (funding ≤ −0,05 → kontrolün 11 katı ödüyor), MA50+ucuz ise fiyat ve MA50 mesafesine bakıyor, fonlama terimi yok. Yine de ucuz/şişmiş altcoinlerde fonlama çarpık olabilir → **ölçülmeden bilinmez** |
| `MA50+ucuz`: canlı artı kuralın mı, radarın ön elemesinin mi? | Ayırmanın tek yolu 2 yıllık OI verisi — yok. **Hakem canlı pencere** (138 işlem hedefi; 12 Ağustos'tan beri 84 pozisyon kapandı) |
| A+B kapısı kararı | 2 yıllık **fonlamalı** ölçüm "kapat" diyor, canlı 16 işlem "kapatma daha kötü olurdu" diyor. 12 Ağustos'ta kullanıcı "açık kalsın" dedi (s.2812); nihai karar hâlâ açık |
| Giriş aramasının süre maliyeti | Tur süresi ölçümü 08-14'te eklendi; ortalama 138 sn giriş aramasında |

---

## Kütüğe girmemiş betikler

`scratchpad/` altında 59 ölçüm betiği var; yukarıda **~30'u** adlandırıldı. Kalanlar
ya yardımcı (veri indirme: `funding_indir.py`, `scalp_1m_indir.py`, `ze_veri.py`) ya
da defterde ayrı bir sonuç bölümü olmayan ara çalışmalar. Bir betiği kullanmadan önce
defterde karşılığı olup olmadığına bak; yoksa **sonucu yeniden üretilmeden
güvenilmez.**
