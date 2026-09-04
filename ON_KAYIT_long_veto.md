# ÖN-KAYIT — `long_veto` haklı mı? Dört alt-tetiğin ayrı ayrı sınanması

**Yazılma tarihi:** 2026-09-04 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** `durum.md` → *BOĞA'DA SEÇİM* → Karar 2 · kullanıcı talimatı
(*"long veto testini yap"*).

---

## 1 · Neden bu ölçüm

Huni ölçümünde `long_veto`'nun **engellediği** dilim (+%0,128), **geçirdiğinden**
(−%0,855) daha iyi çıktı — fark +%0,983, t=+1,71. **Anlamlı değil ama yön net.**

Ve bu, sıradan bir kapı değişikliği önerisi değil: **ters çalışan bir vetoyu
düzeltmek kapıyı DARALTMAZ, AÇAR.** Kullanıcının reddettiği *"daha az işlem aç"*
yönünün tersi.

## 2 · 🔑 NEDEN ÇOKLU KARŞILAŞTIRMA DÜZELTMESİ GEREKMİYOR

Bir önceki ölçümde 43 hücre taradım ve permütasyonla düzelttim, çünkü
**hücreleri ben seçiyordum**.

**Burada durum farklı:** `long_veto` **üretimde çalışan, yazarları tarafından
seçilmiş bir kuraldır** ([testbot.py:430](testbot.py#L430)). Onun dört bileşenini
sınamak **arama değil, denetimdir**. Hücreler önceden ve benim dışımda belirlendi.

⚠️ Yine de **dört sınama önceden sayıldı** ve hüküm yalnız birincildedir.

## 3 · KURALIN AÇILIMI — koddan okundu

```python
long_veto = (
    pos < 0.25                                # 1  bandin dibi (dusen bicak)
    or chg24 <= -40                           # 2  asiri_dusmus (blowoff_chg24_pct=40)
    or (chg24 < 0 and oi24 >= 15)             # 3  fiyat dusuyor + OI hizli artiyor
    or para_cikis                             # 4  PIYASA GENELI risk-off bayragi
)
```

**Vetolanan satırların alt-tetik dağılımı (BOĞA dönemi, tasarım girdisi):**

| alt-tetik | satır | **sembol-gün** |
|---|---|---|
| **1 `pos < 0.25`** | **846** | **42** |
| 3 fiyat-düşük + OI-artış | 224 | 13 |
| 4 artık (≈ `para_cikis`) | 167 | 21 |
| 2 `asiri_dusmus` | 6 | 1 |

🔑 **Veto pratikte TEK koşuldan ibaret:** `pos < 0.25` satırların **%68'i**.

## 4 · TASARIM — vetolanan satırlar DEĞİL, KOŞULUN KENDİSİ sınanır

Vetolanan küme yalnız **65 sembol-gün** — hüküm için çok küçük.
Bunun yerine her alt-tetik **tüm BOĞA popülasyonunda** sınanır:

> *"Koşulu sağlayan satırlar, sağlamayanlardan gerçekten DAHA MI KÖTÜ?"*
> (Veto tam olarak bunu varsayıyor.)

Böylece N, vetolanan kümeyle sınırlı kalmaz.

**Ölçülen:** ham ileri getiri, mekaniksiz, yön LONG, **H = 4 saat** (birincil),
24 saat ikincil. **Birim = SEMBOL-GÜN** · **gün-kümeli t zorunlu**.

⚠️ **Alt-tetik 4 (`para_cikis`) piyasa geneli bir bayraktır** ve arşivde
kaydedilmiyor; artık olarak çıkarılıyor. Sembol bazlı değil **gün** bazlı etki
eder → **betimleyicidir, hüküm taşımaz.**

## 5 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

🔴 **BİRİNCİL:** alt-tetik **1** (`pos < 0.25`) — vetonun %68'i.

| # | ölçüt | eşik |
|---|---|---|
| **K1** | `pos<0.25` grubu, diğerinden **daha kötü** mü | fark **< 0**; veto **haklı** sayılır |
| **K2** | tersi: `pos<0.25` **daha İYİ** ve gün-kümeli t ≥ **+2,0** | veto **HAKSIZ** sayılır |
| **K3** | ikisi de değilse | veto **ETKİSİZ** (ne haklı ne haksız) |

**Üç yollu hüküm — her biri farklı eylem:**

| sonuç | eylem |
|---|---|
| **K1** (veto haklı) | dokunulmaz, konu kapanır |
| **K2** (veto haksız) | `pos<0.25` bileşeni **ayrı ön-kayıtla** kaldırılması tartışılır |
| **K3** (etkisiz) | veto işlem sayısını kısıyor ama kalite katmıyor → **maliyeti var, faydası yok** |

**Alt-tetik 2 ve 3 aynı üç yollu ölçütle, ama İKİNCİL** (N küçük).
Alt-tetik 4 **betimleyici**.

🔴 **GÜÇ DENETİMİ ZORUNLU.** MDE (t=2) hesaplanır. `|fark| < MDE` ise hüküm
*"etkisiz"* değil **"göremiyoruz"** yazılır.

**Zorunlu ek rapor:** her alt-tetiğin N'i (satır **ve** sembol-gün) ·
sembol yoğunlaşması · oynaklık eşitliği · vetolanan kümenin kendi karnesi
(küçük N ile, ayrıca) · karşı-olgu: her bileşen kaldırılsa LONG havuzunun
ham getirisi ne olurdu.

## 6 · BEKLENTİ — sonuç görülmeden yazıldı

**K2'nin (veto haksız) geçmesine ~%40 veriyorum.** Gerekçe: bir önceki
ölçümde `pos` çeyrek kesimi **yüksek pos daha kötü** dedi (−%1,503, t=−2,09),
yani vetonun kestiği **düşük** taraf daha iyiydi. Ama o değer **43 hücrelik
taramanın şans eşiğini geçememişti** (2,09 < 3,12), dolayısıyla burada da
anlamlılığa ulaşamayabilir.

**Yönlü tahminler (tutmazsa aynen raporlanır):**
1. Alt-tetik **3** (fiyat-düşük + OI-artış) **haklı** çıkacak — mekanizması
   en sağlam olan bu (güçlü düşüşün imzası).
2. Alt-tetik **1** vetonun tamamına hâkim olduğu için havuz sonucunu o
   belirleyecek.
3. `H=24` saatte fark `H=4`'ten **büyük** olacak.

🔴 **Ve şimdiden:** K2 geçse bile bileşen **kaldırılmaz.** Bu ham ölçümdür;
mekanik + portföy aşamaları ve **yeni bir pencere** gerekir. Ayrıca 13 günlük
**tek epizot** — ikinci bir BOĞA epizodunda görülmeden kapıya dokunulmaz.

## 7 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
Salt-okuma, ücretli çağrı yok. Betik: `scratchpad/long_veto_testi.py`
(bu commit'ten SONRA).
