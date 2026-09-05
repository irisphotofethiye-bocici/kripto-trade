# ÖN-KAYIT — EMİR DEFTERİ DENGESİZLİĞİ (OBI)

**Yazılma tarihi:** 2026-09-05 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-05): *"emir defterinde sinyal bulabilir miyiz?"* → *"a'ya başla."*

---

## 1 · Neden bu aday — ve neden ŞİMDİ mümkün

`CLAUDE.md`'nin bant-dışı listesindeki **son** aday. Diğer üçünün karnesi:

| aday | hüküm |
|---|---|
| pozisyon kompozisyonu | ❌ bulgu yok (temiz ayrıştırma hâlâ yapılmadı) |
| spot-perp basis | ❌ DÜŞTÜ 5/5 · rho −0,0152 |
| çapraz borsa | ❌ DÜŞTÜ · rho +0,0108 · **işaret hipotezin tersi** |

**İki olgu bugün düzeltildi** (`olcumler.md`, commit `4083d9b`):

1. *"Emir defteri geçmişi YOK → yalnız ileriye"* **yanlışmış.**
   `data.binance.vision/daily/bookDepth` **iki tarafı da** yayınlıyor
   (±%1…±%5, ~30 sn'de bir, 900+ gün geriye).
2. Bugüne kadar ölçülen `defter_usdt_20` **dengesizlik değil BÜYÜKLÜKTÜ** ve
   dolar cinsinden **tam sıfır** taşıyor (`r=−0,003 · t=−0,15`). Skorun düşme
   sebebiyle aynı: büyüklük ölçüyor, **yön** ölçmüyor.

🔑 **Yön taşıyan büyüklük dengesizliktir ve hiç ölçülmedi.** Bu ön-kayıt onu ölçer.

## 2 · PİLOT — ön-kayıttan ÖNCE koşuldu (`scratchpad/obi/00_pilot.py`)

🔴 **Pilot ileri getiriye HİÇ DOKUNMADI.** Aşağıdaki tasarım kararları
**etiketten habersiz** alınmıştır.

```
bookDepth kapsami      : ornek 12 sembolun 12'sinde VAR
dosya basi sure        : medyan 1,92 sn · 500 kB   <- BAGLAYICI KISIT
5m klines (etiket)     : arsivde VAR (13 kB/sembol/gun) -> ufuk merdiveni MUMKUN
OBI ±%1 std            : 0,040 .. 0,137 (sembole gore)
kesitsel yayilim ±%1   : medyan 0,313  -> semboller GERCEKTEN ayrisiyor
```

⚠️ **Pilotun gösterdiği bir yapısal olgu:** OBI sistematik olarak **pozitif**
(±%1'de +0,009…+0,154; ±%5'te +0,18…+0,37). Yani defterin alış tarafı yapısal
olarak daha kalın. **Kesitsel sıra korelasyonu bunu doğal olarak soğurur**
(gün içinde sıralama yapılır, seviye değil) — ama seviyeye bakan hiçbir hüküm
yazılmayacak, bu satır o yüzden burada.

## 3 · YORDAYICI — önceden sabit

```
OBI_L = (alis_notional_L - satis_notional_L) / (alis_notional_L + satis_notional_L)
```

- Anlık görüntü başına hesaplanır (~30 sn), sonra **SAAT içinde ortalaması** alınır.
  Ortalama saat sonunda bilinen bilgiden oluşur → **ileri bakış YOK**.
- 🔴 **BİRİNCİL seviye: ±%1** (dokunuşa en yakın; mikroyapı literatüründe en
  bilgilendirici olan). `±%2` ve `±%5` **ikincil**, önceden ilan, çoklu
  karşılaştırmaya sayılır. **Seviye SEÇİLMEYECEK** — birincil ±%1'dir, sonuç ne
  olursa olsun.

## 4 · 🔴 UFUK MERDİVENİ — bu ön-kaydın en önemli parçası

Mikroyapıda dengesizlik **saniye–dakika** ufkunda öngörür. Bot **7,5 dk** turla
çalışıp **saatlerce** tutuyor. Bu uyuşmazlık bu adayın **en olası ölüm sebebidir.**

```
+5 dk · +30 dk · +1 saat (BIRINCIL) · +4 saat · +24 saat
```

**Neden birincil +1 saat:** botun fiilen girip tutabileceği en kısa anlamlı ufuk.
+5 dk sinyal verse bile bot onu **kullanamaz** (tur süresi 314–440 sn).

🔑 **Merdivenin işi hüküm vermek değil, İKİ FARKLI BAŞARISIZLIĞI AYIRMAK:**

```
merdivenin hicbir basamaginda yok   ->  sinyal YOK
+5dk'da var, +1s'te yok             ->  sinyal VAR ama BIZIM ufkumuzda degil
```

İkincisi *"boş"* demekten tamamen farklı bir sonuçtur ve bu proje bu ayrımı
daha önce yapamadı.

## 5 · VERİ, EVREN, PENCERE — hepsi önceden sabit

| ne | kaynak |
|---|---|
| OBI | `data.binance.vision/.../daily/bookDepth/` — ham dosya **SAKLANMAZ**, akışta işlenir |
| etiket | `fapi/v1/klines interval=5m` (kalıcı uç) — **ham** ileri getiri |
| rejim | `evren.btc_rejim()` gün gün nedensel yeniden üretim (`02_veri.py` deseni) |

```
EVREN  : 120 sembol
         SECIM: pencerenin ILK gununde bookDepth'i olan VE klines_1h_uzun'da
                bulunan semboller arasindan RASTGELE ornek, TOHUM = 20260905
         Neden rastgele: alfabetik ilk 120 "1000XXX" meme coinlerine kayardi;
         bugunun hacmine gore secmek ise SAG KALIM yanliligi sokardi.
PENCERE: 2025-09-07 .. 2026-08-31, HER IKI GUNDE BIR  ->  ~180 gun
         Neden seyreltme: 1,92 sn/dosya baglayici. Iki gunluk adim 7 gunluk
         hafta dongusunu 14 gunde tamamen tarar -> gun-ici faz kilidi YOK
         (CLAUDE.md SEYRELT=24 uyarisi bu yuzden gecerli degil).
BIRIM  : sembol x saat
CIKARIM: gun ICINDE kesitsel Spearman rho, sonra GUN-KUMELI ortalama ve t
```

⚠️ **Sağ kalım sınırı:** evren *pencerenin başında* var olan sembollerden
seçiliyor; arada delist olan varsa gözlemi kısalır, dışlanmaz.

## 6 · 🔴 GEÇERLİLİK KAPISI — ölçümden ÖNCE, düşerse ölçüm YAPILMAZ

```
G-a) OBI cikarimi sinamasi: bilinen girdi -> beklenen OBI   -> duserse betik REDDEDER
G-b) sembol basina >= 500 saat gozlemi                      -> altindaki sembol duser
G-c) gun kumesi >= 120                                      -> altindaysa gun-kumeli t anlamsiz
G-d) gun basina >= 40 sembol (kesitsel rho icin)            -> altindaki gun duser
G-e) etiket kapsami >= %90 (5m klines eslesmesi)            -> altindaysa hizalama bozuk
```

Kapı düşerse **ölçüt gevşetilmez**; sebep yazılır ve ölçüm durur.

## 7 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra DEĞİŞTİRİLMEZ

Birincil hücre: **OBI ±%1 · ufuk +1 saat**.

| # | ölçüt | eşik |
|---|---|---|
| **P1** 🔴 | gün-kümeli rho | **\|rho\| ≥ 0,020 VE \|t\| ≥ 3,0** |
| **P2** | dört zaman çeyreği | ≥ **3/4** aynı işaret |
| **P3** | rejim (BOĞA/NÖTR/AYI) | ≥ **2/3** aynı işaret |
| **P4** | eleme: \|spearman(OBI, son 1s getiri)\| | **< 0,50** |
| **P5** | son 1s getiri üçte-birlikleri | ≥ **2/3** aynı işaret |

**GEÇTİ = beşi birden.** Aksi **DÜŞTÜ.**

🔴 **`\|rho\| ≥ 0,020` tabanı basis ve çapraz borsadan AYNEN alındı.** İkisi de
`t > 4` verip bu tabandan düştü. Aynı taban üç ölçümü kıyaslanabilir kılıyor.

🔴 **P4'ün gerekçesi:** emir defteri fiyat hareketinden **sonra** eğrilir
(hareket eden taraf yenir, diğer taraf kalır). O yüzden OBI, *son fiyat
hareketinin başka bir ifadesi* olabilir — `CLAUDE.md`'nin *"her aday erken fiyat
hareketinin başka bir ifadesi çıkıyor"* uyarısının tam olarak bu adaydaki hâli.
P4 ve P5 bunu ayırır.

### İkincil — önceden ilan, GEÇTİ'ye SAYILMAZ

```
ufuk merdiveni : +5dk · +30dk · +4s · +24s      (bolum 4'teki AYRIM icin)
seviye         : ±%2 · ±%5
```

### Çoklu karşılaştırma sayımı — şimdi ilan

```
5 birincil + 4 ek ufuk + 2 ek seviye + 4 ceyrek + 3 rejim + 3 getiri dilimi = 21 hucre
```

Bu sayı hüküm yazılırken **tekrarlanır**.

## 8 · YÖN HİPOTEZİ

**Beklenen: `rho > 0`** — alış tarafı kalınsa sonraki getiri yüksek
(mikroyapı literatürünün standart bulgusu).

⚠️ **Ama bugün çapraz borsada işaret hipotezin TERSİ çıktı.** İşaret dönerse
aynen raporlanır ve **P1 yine düşer değil** — P1 iki taraflı: `|rho| ≥ 0,020`
ve `|t| ≥ 3,0`. İşaret **ayrıca** raporlanır.
📌 Bu, çapraz borsa ön-kaydından **öğrenilen** bir düzeltmedir: orada işaret
ölçüte gömülüydü ve hükmü gereksiz yere ikiye böldü.

## 9 · ZORUNLU EK RAPOR (hüküm taşımaz)

- Sembol başına gözlem; düşen sembol/gün sayısı ve sebebi
- **Sabit-etki ayrıştırması**: OBI'nin kalıcı sembol bileşeni vs zamanla değişen
  bileşeni (`bası` ve çapraz borsa ölçümlerinde belirleyici olmuştu)
- **Ayna sağlaması**: `−OBI` ile rho tam aynalamalı; aksi hâlde betik hatalı
- OBI seviyesinin sembol dağılımı (pilotun yapısal pozitifliği sürüyor mu)

## 10 · BEKLENTİ — sonuç görülmeden yazıldı

| soru | olasılık |
|---|---|
| **P1** (+1 saat, birincil) geçer | **~%25** |
| **beşi birden** geçer | **~%12** |
| **merdivenin +5dk basamağında bir şey görünür** | **~%70** |

Gerekçe dürüst olmalı:

1. Emir defteri dengesizliği mikroyapıda **en sağlam belgelenmiş** etkilerden
   biri — o yüzden +5dk beklentisi yüksek.
2. Ama bu projede bugüne kadar **hiçbir** ölçüm kanıtlanmış bir giriş kenarı
   bulamadı; taban oran düşük.
3. Ve ufuk uyuşmazlığı gerçek: +5dk'da var olan bir şeyin +1 saatte kalması için
   çok daha yavaş bir mekanizma gerekir.

**Yönlü tahminler (tutmazsa aynen raporlanır):**

1. Merdiven **monotonik sönecek**: +5dk en güçlü, +24s ~sıfır.
2. `P4` **geçecek** (|r| < 0,50) ama sıfırdan uzak olacak — OBI kısmen son
   hareketin izidir.
3. **±%1 > ±%5** olacak (dokunuşa yakın seviye daha bilgilendirici).
4. Kalıcı sembol bileşeni **hiçbir şey taşımayacak**; varsa iş zamanla değişen
   bileşende olacak (çapraz borsada aynen böyle çıktı).

## 11 · Dokunulmayanlar

`testbot.py` · `golge.py` · `ayna.py` · `benim.py` · `defter2/3` · `radar.py` ·
`evren.py` · `kripto-config.json` · state · defterler · zamanlanmış görevler:
**hiçbiri.**

Salt-okuma + **yeni dizine** yazma (`scratchpad/obi/`). Ham `bookDepth` dosyaları
**diske hiç yazılmaz** (akışta işlenir). Ücretli çağrı **YOK**.

Betikler bu commit'ten **SONRA** yazılır:
`01_indir.py` · `02_veri.py` · `03_olcum.py`
