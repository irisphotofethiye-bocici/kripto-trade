# ÖN-KAYIT — Piyasa geneli FONLAMA, SHORT girişlerini uyarıyor mu?

*Yazıldı 2026-08-25 **koşturmadan ÖNCE**. Sonuç görüldükten sonra ölçüt değişmez.*

## NEDEN BU ÖLÇÜM

Defterin açığının **%65'i** 2026-08-18..21 penceresinden geliyor; bot BTC %14,1
ralli yaparken SHORT açtı (`olcumler.md` → "AÇIĞIN KAYNAĞI").
Fiyat bandındaki üç aday elendi: **genişlik** (BTC'nin kopyası, %51 ortak
varyans) · **hacim-öncü** (oynaklık kontrolünü geçemedi) · **TimesFM** (üç
ölçümde de kaldı). Geriye CLAUDE.md'nin işaret ettiği yer kaldı:
*"gerçekten yeni bilgi bandın dışındadır — pozisyon kompozisyonu."*

**Fonlama, bant dışı alanlar arasında 2 yıllık geçmişi olan TEK alandır**
(kalıcı uç). Diğerleri (OI · long/short · taker) 30 günlük kayan pencerede.

⚠️ Bu veri 2026-08-25'te onarıldı (birim kırılması). Seri `fonlama_oku` üzerinden
okunur; birim doğrulaması araca devredildi.

## 🔴 İKİ ZIT ETKİ — ölçüm bunları AYIRMAK zorunda

SHORT açan biri için yüksek pozitif fonlama:

| etki | yön |
|---|---|
| **doğrudan** — pozitif fonlamada SHORT **tahsil eder** | SHORT lehine |
| **dolaylı** — yüksek fonlama = kalabalık LONG = momentum | SHORT aleyhine |

Bu yüzden **ham fiyat getirisi ile fonlama geliri AYRI ölçülür.** Toplamına
bakmak iki etkiyi birbirine karıştırır ve hiçbir şey öğretmez.

## VERİ

- Piyasa geneli seri: `01_seri.py` → 8 saatlik kovalar, 2.230 kova,
  2024-08-12..2026-08-25, kova başına ~990 sembol. Alanlar: `ort` (kesitsel
  ortalama), `med`, `poz_pay` (fonlaması pozitif sembol yüzdesi), `ust10`, `btc`.
- Olaylar: `chg24 ≥ +%20` → SHORT (botun karakteri), 1h mumlar, 566 sembol,
  aynı sembolde 24 bar bekleme. Mekanik: **stop yok, hedef yok** — ham ileri
  fiyat getirisi (CLAUDE.md sırası: ham → mekanik → portföy).
- Ufuklar: **4 · 24 saat.**

Eşikler dağılımdan, **sonuca bakmadan** (yukarıdaki seri çıktısı):
`ort` çeyrekleri **−0,0095 / −0,0032 / +0,0020** · `poz_pay` çeyrekleri
**67,96 / 77,86 / 87,21**.

## ÖLÇÜTLER (sonuca bakmadan yazıldı)

| # | ölçüt | eşik |
|---|---|---|
| 1 | **Monotonluk** — fonlama kovaları arttıkça SHORT'un **ham fiyat** getirisi düşmeli | 4 kovada sıra bozulmasın |
| 2 | 🔴 **KARIŞTIRICI** — BTC'nin 24sa getirisi **sabitlendiğinde** fark korunmalı | BTC kovalarının ≥3/4'ünde aynı işaret |
| 3 | **Holdout** — zaman ikiye bölünür, üst-alt farkı ikinci yarıda aynı işaret | işaret aynı |
| 4 | **Rejim** — ATH · DÜZELTME · DERİN_AYI'nın en az 2'sinde | 2/3 |
| 5 | **Ayrışma** — fonlama geliri ayrı raporlanır; ham etki gelirle **ters** yönde mi | bilgi amaçlı |

**HÜKÜM KURALI:** **1 veya 2 geçmezse hüküm YAZILMAZ.** Genişlik ölçümü tam
ölçüt 2'de çöktü (BTC'nin kopyası çıktı); fonlama da fiyattan türeyebilir.
İstatistik **gün-kümeli**, yoğunlaşma denetimi raporlanır.

## KAPSAM DIŞI

- Kâr iddiası değildir; geçse bile bota kapı eklemek ayrı karardır.
- 08-18..21 penceresi ölçümün **içindedir**; hipotez oradan doğdu, o pencere
  tek başına kanıt sayılmaz — holdout bu yüzden var.
- Bot zaten coin-bazlı bir fonlama kapısı kullanıyor (`testbot.py:426`,
  A+B). Bu ölçüm **piyasa geneli** göstergedir, o kapı değildir.

Bota yazım: **YOK.** Salt-okuma.
