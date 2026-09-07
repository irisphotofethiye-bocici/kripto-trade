# ÖN-KAYIT — LİKİDASYON DENGESİZLİĞİ, LONG GİRİŞLERİNDE

**Yazılma tarihi:** 2026-09-07 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"botun long ayağında likidasyon testi yapmadık,
liqmap ne kadar çalışır ölçelim"* → *"coin analyze"*
**Betik:** `scratchpad/liq/02_olcum.py`

---

## 1 · 🔴 ÖNCE: NE ÖLÇÜLMÜYOR

Kullanıcı **`liqmap`** dedi. İki ayrı şey var ve **karıştırılmayacak**:

| | ne | geçmiş | maliyet |
|---|---|---|---|
| **liqmap / ısı haritası** | CoinGlass'ın *"bekleyen likidasyon nerede yığılı"* **modeli** | **YOK** (anlık) | Apify, **ücretli** |
| **likidasyon geçmişi** | saat saat **gerçekleşen** long/short likidasyon (USD) | **VAR** | Coinalyze, **ücretsiz** |

🔴 **`liqmap` geriye test EDİLEMEZ** — anlık bir enstantane, tarihçesi
yayınlanmıyor. Ayrıca bir **model çıktısı**, ham veri değil.
🔴 **Apify çağrısı YAPILMAYACAK** (ücretli; `CLAUDE.md`: ücretli çağrı
onaya tabi). Bu ölçüm tamamen **ücretsiz** Coinalyze ucuyla koşuyor.

**Ölçülen şey:** gerçekleşen likidasyonların **YÖNÜ**, giriş öncesinde.

## 2 · 🔴 SIRADAKİ DUVAR: bu da "fiyatın kılığı" olabilir

`CLAUDE.md`: *"ÖLÇTÜĞÜMÜZ HER ŞEY TEK BANTTAN TÜRÜYOR."* Likidasyon bir
**işlemdir** — long likidasyon kaskadı **fiyatın düşmesinin ta kendisidir.**
Yani *"likidasyon ileri getiriyi öngörür"* bulgusu büyük olasılıkla
*"fiyat hareketi ileri getiriyi öngörür"*ün yeniden etiketlenmiş hâlidir —
ki o zaten ölçüldü (`pos`/`chg24`, 5 rejimde 5/5).

🔑 **Yeni bilgi taşıma ihtimali olan tek şey ASİMETRİ:** aynı fiyat düşüşünde
*"çok long likide oldu"* ile *"az long likide oldu"* **farklı kaldıraç
stresi** demektir. Bu, `CLAUDE.md`'nin bant-dışı listesindeki **pozisyon
kompozisyonuna** yakındır — listedeki **denenmemiş tek aday**.

⚠️ Ve emir defteri dersinin **birebir aynısı** geçerli: `defter_usdt_20`
**büyüklük** ölçüyordu ve **tam sıfır** taşıdı; yön taşıyan şey
**dengesizlikti**. Burada da **büyüklük değil, dengesizlik** birincil.

## 3 · DEĞİŞKEN

```
liq_dengesizlik = (short_liq - long_liq) / (short_liq + long_liq)
                  giristen ONCEKI 24 saatte toplanir      -> [-1, +1]

  +1 = yalniz SHORT'lar likide oldu (short squeeze)
  -1 = yalniz LONG'lar likide oldu  (long tasfiyesi)
```

**İkincil (büyüklük — düşmesi bekleniyor):**
`liq_toplam_usd = (short_liq + long_liq)` / 24 saatlik hacim

## 4 · HİPOTEZ — 🔴 İKİ YÖNLÜ, ve bunun bedeli ödeniyor

**Güçlü bir önselim YOK ve uydurmuyorum.** İki makul hikâye var:

```
(a) long tasfiyesi (-) -> kapitulasyon -> sicrama  -> LONG icin IYI
(b) short squeeze  (+) -> yukari baski  -> devam   -> LONG icin IYI
```

İkisi de savunulabilir → hipotez **iki yönlü** ilan ediliyor. Bedeli:
**`t` eşiği `2,0` değil `2,5`** ve keşif/holdout **işaret tutarlılığı şart**.

## 5 · VERİ

```
LIKIDASYON : Coinalyze /liquidation-history · 1hour · convert_to_usd
             KAPSAM OLCULDU: 67 gun (2026-07-02 .. 2026-09-07), ucretsiz tavan
             381 sembol · 10 sembol/istek · 40 cagri/dk
GIRISLER   : radar_archive · score>=30 · 4sa cooldown · LONG
             (giris_arama · r_hedef · kilit_aralik ile AYNI evren)
ORTUSME    : radar_archive 72 gun · Coinalyze 67 gun -> ~65 gun kesisim
KESIF      : ilk %60 gun    HOLDOUT : son %40 gun
```

⚠️ Örtüşme nedeniyle `N`, kardeş ölçümlerden **küçük** olacak. Gerçek `N`
raporlanacak; `< 800` çıkarsa **güç yetersiz** diye yazılacak.

## 6 · BİRİNCİL METRİK — HAM ileri getiri

Likidasyon yoğun hücreler **oynak** olacak → `CLAUDE.md`: *"hücreler
oynaklıkta ayrışıyorsa ham getiri ZORUNLU."*

```
BIRINCIL : ham +24 saat getiri (mekaniksiz)
IKINCIL  : A0 mekanigiyle R  (rapor, hukum kurmaz)
```

## 7 · 🔴 BELİRLEYİCİ SINAMA — KARIŞTIRICI KONTROLÜ

Bu ölçümün **asıl** sorusu budur:

```
HAM       : dengesizlik besli dilim, en dusuk vs en yuksek, HOLDOUT
KATMANLI  : once chg24 (MUMDAN uretilir) besli dilime ayrilir;
            HER katmanin ICINDE ayni karsilastirma yapilir;
            katman farklarinin ORTALAMASI alinir
```

**Katmanlı etki, ham etkinin en az %50'sini korumalı.** Korumazsa bulgu
**fiyatın kılığıdır** ve öyle yazılır.

🔴 Bu proje bunu **iki kez** yaşadı: agresör dengesi (üç kapıyı geçti, ilk-saat
getirisi sabitlenince **işaret döndü**) ve *son yeni uç* (11,8 puanlık
monotonik yayılım kâr sabitlenince 2-4 puana indi). Üçüncüsü olmasın.

⚠️ `chg24` **arşiv alanından OKUNMAZ** — bugün ölçüldü: o alan yalnız
erken-kuşak kaydında var ve `|chg24| ≤ 15` ile **kırpılmış**. **Mumdan
üretilecek.**

## 8 · ÖLÇÜTLER — sonuç görüldükten sonra değişmez

| # | ölçüt | eşik |
|---|---|---|
| **L1** | KEŞİF ve HOLDOUT **aynı işaret** | evet |
| **L2** | HOLDOUT **gün-kümeli \|t\|** | **≥ 2,5** (iki yönlü) |
| **L3** | \|fark\| > **MDE** | evet |
| **L4** | 🔴 **KATMANLI etki, ham etkinin ≥ %50'si** | evet |
| **L5** | **negatif kontrol** (gün içi permüte, aynı hat) temiz | evet |

```
YON VAR      = L1..L5 hepsi
FIYATIN KILIGI = L1+L2+L3 gecer ama L4 duser        <- ayri ve onemli sonuc
YON YOK      = L1 duser
GOREMIYORUZ  = L1+L4 gecer, L2/L3 duser
```

## 9 · EK RAPOR — ölçüt DEĞİL

- Beşli dilim tablosu: N · ort dengesizlik · **ham getiri** · `R` · isabet% ·
  ATR/fiyat · stop genişliği (ayrışma sınaması)
- **Büyüklük** (`liq_toplam`) aynı hattan — emir defteri dersi tekrarlanıyor mu
- Likidasyon verisi bulunan / bulunamayan sembol sayısı
- Dengesizlik ile `chg24` çakışma oranı (dilim bazında; **Spearman YOK**)

## 10 · NE YAPILMAZ

- Bota, state'e, defterlere **dokunulmaz** (salt-okuma)
- **Apify/ücretli çağrı YOK**
- Eşik **aranmaz** — dilimler veriden, karşılaştırma önceden ilan
- `chg24` **arşiv alanından okunmaz** (bölüm 7)
- `R` ile paydasındaki değişken arasında **Spearman koşulmaz**
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 11 · GEÇERSE

1. Ham aşama → **mekanik** → **portföy**
2. Ancak o zaman kapı önerisi + pencere sıfırlama
3. 🔴 Geçse bile **kod otomatik değişmez.**

## 12 · BEKLENTİM — koşumdan önce

**`L4`'ün (karıştırıcı kontrolü) geçmesine %20.** Likidasyon fiyatın
kendisidir; asimetrinin ayrı bilgi taşıması için kaldıraç dağılımının
fiyattan bağımsız değişmesi gerekir — mümkün ama zor.

**Genel geçme (`L1..L5`) olasılığı %12.** Bant-dışı aday listesi bugüne
kadar **4/4 düştü**; bu beşincisi ve bandın **içinden** geliyor.

⚠️ Bugün **on altı ön-kayıt yazıldı, on altısı da geçemedi.**
