# ÖN-KAYIT — BOĞA HOLDOUT: geniş stop, TAZE veride de tutuyor mu?

**Yazılma tarihi:** 2026-09-05 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-05): *"21'inden bugüne kadar olan rejim boğa,
yani elimizde veri olması lazım."*

---

## 1 · 🔴 ÖNCE: İKİ KEZ YANLIŞ SÖYLEDİM, kullanıcı iki kez haklıydı

| iddiam | gerçek |
|---|---|
| *"22 Ağustos sonrası ölçülemez, veri 08-25'te bitiyor"* | ❌ **`perp_seri/*_kline.json` 09-05'e kadar var** (153 sembol, 5 dakikalık) |
| *"`oi24` bacağı ölçülemez"* | ❌ **`radar_archive.jsonl`'de `oi24` zaten var** (06-24'ten beri) |

Her ikisinde de **tek bir dizine bakıp genelleme yaptım.** Kullanıcı ısrar etmese
bu ölçüm hiç yapılmayacaktı. Bu, ön-kaydın parçası olarak yazılıyor.

## 2 · Bu neden GERÇEK bir holdout

Hipotez *"BOĞA'da geniş stop yardım eder"* **2 yıllık `klines_1h_uzun`** verisinde
doğdu ve o veri **2026-08-25'te bitiyor.** Bu koşum **`perp_seri` + `radar_archive`**
kullanıyor — farklı kaynak, ve **08-25 → 09-02 kısmı hiç görülmedi.**

⚠️ Örtüşme var ama **ihmal edilebilir**: eski koşumda 08-21…08-25 penceresi
**N=4** üretmişti (kütüğe öyle yazıldı). Yani bu pencerenin neredeyse tamamı yeni.

🔴 **Bu, üçüncü deneme.** Tam örneklem düştü, rejim kırılımı kılpayı düştü.
Üçüncü kez aynı soruyu sormak **ancak veri gerçekten tutulmuşsa** meşrudur —
burada öyle. Ölçü, kollar ve mekanik **değiştirilmiyor.**

## 3 · KAPSAM — koşumdan ÖNCE sayıldı (`scratchpad/boga_kapsam_sayim.py`)

```
BOGA penceresi 2026-08-21 -> 2026-09-02 (72s ileri getiri icin kesme)

A  (funding <= -0,05)          ham 2.869  ->  BAGIMSIZ OLAY  55   (13 gun · 27 sembol)
A+B (funding <= -0,05 & oi24 >= 10)      ->  BAGIMSIZ OLAY  25   (11 gun · 19 sembol)
```

Bağımsızlık: aynı sembolde **24 saat soğuma** (üst üste kareler elendi; 2.154 kayıt
bu yüzden düştü). `radar_bosluk.jsonl` 179 satır — kayıp kare kaydı **var**, raporlanacak.

## 4 · 🔴 GÜÇ — hüküm yazılmadan ÖNCE, ve KÖTÜ

2 yıllık BOĞA diliminde `2.5x` için MDE **0,2845** (51 gün). Ölçek `1/√gün`:

```
sqrt(51 / 13) = 1,98   ->   bu pencerede MDE ~ 0,56
beklenen etki (2 yillik BOGA)              ~ 0,29
```

🔑 **Ortalama farkın t-testi bu N'de İŞE YARAMAZ — iki kat yetersiz.**
Bu yüzden birincil ölçüt **ortalama değil, GÜN BAZINDA İŞARET TESTİ**: tutarlı
bir etki, küçük N'de bile günlerin çoğunu pozitif yapar ve binom testi buna
duyarlıdır.

## 5 · DEĞİŞMEYENLER

Ölçü **yine `R`** (`net%` ikincil) · kollar **yine** `A`/`1.5x`/`2.5x`/`4.0x` ·
hedef **%10** · ufuk **72s** · maliyet **%0,13** · eşleştirme `asgari_stop` **A'ya
göre** · stop hesabı `ileri_rr.stop_hesapla` **kaynaktan çağrılır**.
Aday kol **`2.5x`** — 2 yıllık BOĞA'da en iyi olan; **burada aranmıyor, sınanıyor.**

**Fiyat:** `perp_seri` 5 dakikalık → **1 saate toplanır** (o=ilk açılış · h=maks ·
l=min · c=son kapanış). Isınma 220 bar = ~9 gün; `perp_seri` 07-26'da başlıyor → yeterli.

**Fonlama:** `funding_gecmis` 08-25'te bittiği için, tutma süresi boyunca
`radar_archive`'ın gözlediği oran her **8 saatlik ödeme anına** (00/08/16 UTC) en
yakın kayıttan alınır. ⚠️ Bu bir **yaklaşımdır** ve eski koşumlardaki gerçek
ödeme serisinden farklıdır; hükümde belirtilir.

## 6 · 🔴 ZORUNLU SINAMA — zaman ofseti kanıtlanmadan koşulmaz

`radar_archive.ts` **yerel (UTC+3)**, klineler **UTC** → ofset **−3 saat**.
Bu varsayım yanlışsa tüm ölçüm çöp olur ve **sessizce** çöp olur.

**Sınama:** arşivin `last1` alanı (son 1 saatlik getiri) ile, eşlenen UTC barından
hesaplanan gerçek 1 saatlik getiri **korelasyonu ≥ 0,80** olmalı.
Ayrıca ofset **−4, −3, −2** denenir ve **−3 en yüksek** çıkmalı.
Düşerse betik **çalışmayı REDDEDER.**

## 7 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

Birincil: `A_funding` · BOĞA holdout · ölçü `R` · kol **`2.5x`**.

| # | ölçüt | eşik |
|---|---|---|
| **K1** 🔴 | **gün bazında işaret testi**: `2.5x − A` farkının pozitif olduğu gün sayısı | tek yönlü binom **p ≤ 0,05** |
| **K2** | ortalama eşleşmiş fark | **> 0** (işaret önceki bulguyla aynı) |
| **K3** | komşu kol `4.0x` de **> 0** | evet |
| **K4** | **tam A+B kapısı** (N=25) alt kümesinde işaret **ters değil** | evet |

**GEÇTİ** = K1+K2+K3+K4 · **ZAYIF** = K2+K3 var, K1 düştü · aksi **DÜŞTÜ**.

🔴 **K1 tek yönlüdür ve bu bilinçlidir:** yön **önceki ölçümde sabitlendi**
(pozitif). Çift yönlü test burada yanlış olurdu — keşif değil, **doğrulama**.

⚠️ **Ortalama farkın t'si ve MDE'si her hâlükârda raporlanır**, ama K1 değildir
(bölüm 4). *"t çıktı ama sign testi düştü"* durumunda hüküm **DÜŞTÜ**'dür.

## 8 · ÇOKLU KARŞILAŞTIRMA

**Birincil: 1** (tek kol, tek yön, tek ölçü, tek evren). Ek düzeltme gerekmez —
bu bir **tarama değil, tek bir önceden belirlenmiş doğrulamadır.**
`1.5x` · `4.0x` · `net%` · A+B alt kümesi · rejim dışı hücreler: **ikincil.**

## 9 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%30 veriyorum.** 13 günde binom p ≤ 0,05 için **10/13** pozitif
gün gerekiyor; gerçek ama gürültülü bir etkide bile bu zor bir bar.

**Yönlü tahminler (tutmazsa aynen raporlanır):**

1. **Ortalama farkın işareti POZİTİF çıkacak** (K2 geçecek) — 2 yıllık BOĞA ile aynı yön.
2. **Etkinin büyüklüğü +0,29'dan KÜÇÜK olacak** — kılpayı kaçırmış bir hücreyi
   yeniden ölçmek ortalamaya dönüş üretir.
3. Stop-olma oranı genişlikle yine **monoton düşecek** (bu üçüncü kez sınanıyor,
   üçünde de tuttu).
4. **A+B alt kümesi (N=25) hiçbir şey söyleyemeyecek** — MDE her makul etkiden büyük.

## 10 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
**Veri indirme YOK** (kullanıcı talimatı) — yalnız var olan arşivler okunur.
`radar_archive.jsonl` **context'e yüklenmez**, Python özetler.
Betik: `scratchpad/boga_holdout.py` (**bu commit'ten SONRA**).
