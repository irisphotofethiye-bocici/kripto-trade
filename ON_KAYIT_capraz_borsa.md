# ÖN-KAYIT — ÇAPRAZ BORSA: BINANCE − BYBIT FONLAMA FARKI

**Yazılma tarihi:** 2026-09-05 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-05): *"bekleyen likidite · spot-perp basis · çapraz
borsa · pozisyon kompozisyonu — bunları ölçelim"* · *"testleri önce yapıp işe
yarar bir şey bulursak onu da eklerdik bota."*

---

## 1 · Neden bu aday

`CLAUDE.md`'nin **bant-dışı** listesinden sırada olan. Listenin durumu bugün
çıkarıldı:

| aday | durum |
|---|---|
| spot-perp basis | ❌ ölçüldü 2026-08-26, **DÜŞTÜ 5/5** |
| pozisyon kompozisyonu (`top_ls − glob_ls`) | ❌ ölçüldü 2026-08-19, boş |
| bekleyen likidite | ❌ 2026-09-05: kaydedilen taraf **sıfır bilgi** taşıyor (r=−0,003); dengesizlik hiç kaydedilmedi |
| **çapraz borsa** | ⏳ **hiç denenmedi** ← bu ön-kayıt |

**Neden gerçekten bant-dışı:** projenin ölçtüğü her şey **Binance perp'te
gerçekleşmiş işlemden** türüyor. Bybit ayrı bir borsa, ayrı kullanıcı tabanı,
ayrı marj motoru. İki borsanın fonlaması ayrışıyorsa, ayrışma **Binance'in kendi
işlem akışından türetilemez.**

## 2 · YOKLAMA — ön-kayıttan ÖNCE koşuldu (`scratchpad/capraz/00_yoklama.py`)

🔴 **Yoklama ileri getiriye HİÇ DOKUNMADI.** Yalnız iki borsanın fonlama
oranlarına ve birbirleriyle ilişkisine baktı. Bu yüzden aşağıdaki tasarım
kararları **etiketten habersiz** alınmıştır — sonuca bakıp kural yazmak değildir.

```
ortak sembol                      : 462   (klines_1h_uzun'da fiyati olan: 460)
fonlama araligi UYUSMAZLIGI       : 20 sembolun 2'sinde FARKLI (binance 4s / bybit 8s)
fark |medyan|                     : %0,0025 / gun
fark |%90|                        : %0,1255 / gun        <- medyanin 50 KATI
spearman(binance fonlama, fark)   : +0,275
indirme tahmini                   : ~60-75 dk, ucretsiz, anahtarsiz
```

**İki tasarım kararı buradan çıktı:**

1. 🔴 **GÜNLÜK ORANA ÇEVİRME ZORUNLU.** Ham oranı karşılaştırmak
   `funding_gecmis` birim kırılmasıyla **aynı hata sınıfıdır** (iki farklı şey
   aynı adı taşıyor). Aralık, dosyanın kendi ardışık damgalarından çıkarılır
   (`medyan Δt`), sabit varsayılmaz.
   `gunluk = oran × 24 / aralik_saat`
2. **Kuyruk ölçütü ÖNCEDEN ilan ediliyor** (C6). Medyan ~0 ama %90'lık dilim 50
   kat büyük — yani dağılım kalın kuyruklu. Bunu koşumdan **sonra** fark edip
   *"asıl sinyal kuyrukta"* demek bu projede yasak; o yüzden **şimdi** yazılıyor
   ve **çoklu karşılaştırmaya sayılıyor**.

## 3 · HİPOTEZ ve YÖN — önceden sabit

```
fark = binance_fonlama_gunluk - bybit_fonlama_gunluk
```

Fonlama pozitifken **uzun taraf kısa tarafa öder**. Binance'in fonlaması
Bybit'inkinden yüksekse, **Binance'te uzun taraf daha kalabalıktır.**
Kalabalık taraf bu projede tekrar tekrar sonraki dönemde kaybetti.

🔑 **Beklenen işaret: `rho < 0`** (yüksek fark → sonraki getiri düşük).

⚠️ Bu, basis ön-kaydının hipoteziyle **aynı ekonomik mantık**. Basis'te işaret
doğru çıktı ama büyüklük yetersizdi. Aynı sonucun tekrarı **mümkün** ve
beklentiye yansıtıldı (bölüm 8).

## 4 · VERİ ve BİRİM

| ne | kaynak | sınıf |
|---|---|---|
| Binance fonlama | `fapi/v1/fundingRate` | **kalıcı**, 2 yıl |
| Bybit fonlama | `api.bybit.com/v5/market/funding/history` | **kalıcı**, ≥2023-11 doğrulandı |
| fiyat (etiket) | `scratchpad/klines_1h_uzun` (elde, 566 sembol) | kalıcı |

- **Evren:** 460 ortak sembol (fiyatı olanlar). Seçim YOK, tarama YOK.
- **Pencere:** 2024-09-01 … 2026-08-31 (**24 tam ay**). Uçlar önceden sabit.
- **Gözlem birimi:** sembol × fonlama damgası (saate hizalanmış, **UTC**).
- **Etiket:** `+24 saat HAM ileri getiri` — `CLAUDE.md` aşama sırası
  (*ham getiri → mekanik → portföy*). **Tek ufuk**, başka ufka BAKILMAZ.
- **Çıkarım:** kesitsel Spearman rho **gün içinde** hesaplanır, sonra
  **gün-kümeli** ortalama ve t. (basis deseni birebir.)

⚠️ **Fonlama/ücret etikete DAHİL DEĞİL.** Gidiş-dönüş maliyet %0,19; rho
büyüklüğü küçükse maliyet sonrası zaten kalmaz — hüküm bölümünde yazılır.

## 5 · 🔴 GEÇERLİLİK KAPISI — ölçümden ÖNCE, düşerse ölçüm YAPILMAZ

```
K-a) gunluk orana cevirme uygulandi mi        -> betik kendini sinar, yoksa CALISMAYI REDDEDER
K-b) ortak damga kapsami >= %60               -> altindaysa hizalama bozuk demektir
K-c) sembol basina en az 100 ortak gozlem     -> altindaki sembol DUSER, sayisi raporlanir
K-d) gun kumesi >= 300                        -> altindaysa gun-kumeli t anlamsiz
```

Kapı düşerse **ölçüt gevşetilmez**; sebep yazılır ve ölçüm durur.

## 6 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra DEĞİŞTİRİLMEZ

| # | ölçüt | eşik |
|---|---|---|
| **C1** 🔴 | gün-kümeli rho | **\|rho\| ≥ 0,020 VE \|t\| ≥ 3,0** · işaret **negatif** |
| **C2** | dört zaman çeyreği | ≥ **3/4** aynı işaret |
| **C3** | rejim (BOĞA/NÖTR/AYI) | ≥ **2/3** aynı işaret |
| **C4** | eleme: \|spearman(fark, binance fonlama)\| | **< 0,50** |
| **C5** | Binance fonlaması üçte-birlikleri | ≥ **2/3** aynı işaret |

**GEÇTİ = beşi birden.** Aksi **DÜŞTÜ.**

🔴 **`\|rho\| ≥ 0,020` TABANININ SEBEBİ — basis'ten öğrenildi.** ~750 gün
kümesiyle hiçliğe yakın bir etki bile `t > 3` verir. Basis tam olarak buradan
düştü: `t = −4,85` ama `|rho| = 0,0152`. **Aynı taban aynen kullanılıyor** ki
iki ölçüm doğrudan kıyaslanabilsin.

### C6 — İKİNCİL, önceden ilan edildi, GEÇTİ'ye SAYILMAZ

```
BUYUK FARK alt kumesi: |fark| >= o gunun %90'lik dilimi
   -> ayni rho, ayni gun-kumeli t, AYRICA raporlanir
```

Yoklama dağılımın kalın kuyruklu olduğunu gösterdi (medyan %0,0025 vs %90
%0,1255). **Hüküm taşımaz** — tek pencere, düşük güç, ve çoklu karşılaştırmayı
artırır. Geçerse **kendi ön-kaydıyla** yeniden sınanır.

### Çoklu karşılaştırma sayımı — şimdi ilan

```
5 birincil olcut + 1 ikincil + 4 zaman ceyregi + 3 rejim + 3 fonlama dilimi = 16 hucre
```

Bu sayı hüküm yazılırken **tekrarlanır**.

## 7 · ZORUNLU EK RAPOR (hüküm taşımaz)

- Sembol başına gözlem sayısı; düşen sembol sayısı ve sebebi
- Aralık uyuşmazlığı olan sembol sayısı (yoklamada 20'de 2)
- Farkın **kalıcı sembol bileşeni** ile **zamanla değişen** bileşeninin ayrılması
  (sabit-etki ayrıştırması) — `bası` ölçümünde bu ayrım belirleyici olmuştu
- `fark` yerine **ters yön** (`bybit − binance`) sonucun aynadaki hâli olmalı;
  değilse betik hatalıdır — **sağlama olarak koşulur**

## 8 · BEKLENTİ — sonuç görülmeden yazıldı

**C1'in geçmesine ~%20, beşinin birden geçmesine ~%10 veriyorum.**

Gerekçe dürüst olmalı:

1. **Basis aynı mantıkla düştü** ve bu ölçüm ona ekonomik olarak yakın.
2. Yoklama farkın medyanının **~sıfır** olduğunu gösterdi — arbitraj çalışıyor.
3. Bu projede bugüne kadar **hiçbir** ölçüm kanıtlanmış bir giriş kenarı
   bulamadı; taban oran düşük.
4. Ama eleme testi **geçti** (+0,275) ve veri gerçekten bant-dışı — basis'in
   ötesinde tek yeni şey bu.

**Yönlü tahminler (tutmazsa aynen raporlanır):**

1. `C1` işareti **negatif** çıkacak (hipotez yönünde) ama `|rho| < 0,02`
   kalacak — yani basis'in tekrarı.
2. `C6` (büyük fark) **havuzdan güçlü** çıkacak; kuyrukta bilgi var.
3. `C3`'te **AYI rejiminde etki zayıflayacak** — basis'te tam bu oldu.
4. Farkın büyük kısmı **kalıcı sembol bileşeni** olacak (bir coin'de Binance
   sistematik olarak daha pahalı), zamanla değişen kısım küçük kalacak.

## 9 · Dokunulmayanlar

`testbot.py` · `golge.py` · `ayna.py` · `benim.py` · `defter2/3` · `radar.py` ·
`evren.py` · `kripto-config.json` · state · defterler · zamanlanmış görevler:
**hiçbiri.**

Salt-okuma + **yeni dizine** indirme (`scratchpad/capraz/`). Var olan hiçbir
arşiv dosyasına yazılmaz, ezilmez. Ücretli çağrı **YOK**.

Betikler bu commit'ten **SONRA** yazılır:
`01_indir.py` · `02_veri.py` · `03_olcum.py`
