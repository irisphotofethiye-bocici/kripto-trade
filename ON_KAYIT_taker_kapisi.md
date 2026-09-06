# ÖN-KAYIT — `taker ≥ 1.0` KAPISI BİLGİ TAŞIYOR MU?

**Yazılma tarihi:** 2026-09-06 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-06): *"taker ne?"* → *"yap"*
**Betikler:** `scratchpad/taker/01_mum_indir.py` · `scratchpad/taker/02_olcum.py`

---

## 1 · SORU

NOTR-LONG karar zincirinin **son kapısı** `taker ≥ 1.0`
([testbot.py:645](testbot.py#L645)). Bu kapı bilgi mi taşıyor, yoksa aday mı
kısıyor?

`taker` = Binance `takerlongshortRatio` → `buySellRatio`, 1 saatlik:
son 1 saatte **taker alış hacmi / taker satış hacmi**. Yani "spread'i geçip
piyasadan vuran taraf hangisi".

## 2 · NEDEN ŞİMDİ

| gözlem | sayı |
|---|---|
| `notrlong`'da stage+skor+smart geçen aday | 6 |
| bunlardan `taker < 1.0` diye ölen | **6** (0,74 · 0,80 · 0,88 · 0,97 · 0,99 · 0,99) |
| arşiv tabanı: smart-LONG → `taker ≥ 1.0` geçen | 161 / 367 = **%43,9** |

Kapı, adayların **%56'sını** kesiyor ve canlı botta **terminal** darboğaz.

🔴 **Ve iki ölçülmüş kayıt kapıyı şüpheli yapıyor:**
1. Yön avı (2026-08-10, 6.790 olay): *"RASTGELE ÇIKANLAR: **gerçek taker oranı
   (−0,07)** · sıkışma (−0,17) · hacim katı (+0,03)"* — yön taşımadı.
2. Agresör dengesi (2026-08-17) bu projede **tam bu şekilde** çürüdü: üç kapıyı
   geçti, ilk-saat getirisi sabitlenince **işaret döndü**.

⚠️ İkisi de **SHORT yönü tahmini** için ölçüldü, **LONG kapısı** olarak değil.
Aynı şey olmayabilir — bu yüzden "boş" denmiyor, **ölçülüyor**.

## 3 · POPÜLASYON

`radar_archive.jsonl`, süzgeç = botun zincirinin **taker'dan ÖNCEKİ** hâli:

```
stage in (BASLIYOR, HAZIRLANIYOR)
score  >= 40 (HAZIRLANIYOR) / 45 (BASLIYOR)
smart  == LONG
```

**Rejim süzgeci YOK** — bot rejimi `NOTR`'a zorluyor. Dolayısıyla
`radar_archive.rejim` alanının 2026-07-22 tanım değişikliği (`CLAUDE.md`)
bu ölçümü **etkilemez**; alan hiç okunmuyor.

**Yoklandı** (`scratchpad/taker/00_yoklama.py`, sonuç değil, kapsam):

```
N = 956  ·  tekil gun 57  ·  tekil sembol 121
taker DOLU %100  ->  taker>=1.0: 378   taker<1.0: 578
```

⚠️ `smart` ve `taker` aynı `pillar_d` çağrısından gelir → arşivde ikisi
birlikte var ya da birlikte yok. Hücrede eksik yok.

⚠️ `radar_archive` **noktasal** veridir; `radar_bosluk.jsonl` birlikte okunur.

## 4 · BAĞIMSIZ DEĞİŞKEN

| | |
|---|---|
| **birincil** | ikili bölme `taker ≥ 1.0` vs `< 1.0` — **botun fiilî kapısı** |
| ikincil | sürekli `taker` ile Spearman rho |

## 5 · SONUÇ DEĞİŞKENİ — MEKANİKTEN ARINIK

Ham ileri getiri, **LONG** yönü:

```
ret(h) = (close[t+h] / price[t] - 1) * 100
```

**Ufuk merdiveni:** `+1s · +4s · +12s · +24s · +48s`

🔴 **Stop/hedef/maliyet YOK.** `CLAUDE.md` sırası: `ham → mekanik → portföy`.
Ham geçmezse mekaniğe **geçilmez**. Mekanikli ölçüm bu ön-kayıtta yapılmaz.

**Birincil ufuk: `+24s`.** Gerekçe: bot sabit %10 hedef + **48s zaman stopu**
ile tutuyor; yalnız `+1s`'te görünen bir kapı bu bota **yaramaz**. `+48s`
gürültülü, `+24s` ikisinin ortası. *Bu seçim koşumdan önce sabitlendi.*

## 6 · ZORUNLU SINAMA — OYNAKLIK AYRIŞMASI

`CLAUDE.md`: *"hücreler oynaklıkta ayrışıyorsa ham getiri ZORUNLU"*. Ham zaten
kullanılıyor, ama ayrışma **raporlanır**: her kolda `vol_x` ve `|last1|`
medyanı + getiri standart sapması. Ayrışma varsa hükme not düşülür.

## 7 · 🔴 KARIŞTIRICI KONTROLÜ — BU ÖLÇÜMÜN KALBİ

Agresör dengesi tam burada çürüdü. Bu yüzden **ham fark tek başına hüküm
kurmaz**; K2 yalnız **sabitlenmiş** karşılaştırmayla verilir.

```
SABITLENEN : last1  (son 1 saat getirisi, hucrede %100 dolu)
YONTEM     : last1'in BESLI dilimi icinde bolme -> dilim-ici farklarin
             N-agirlikli ortalamasi
IKINCIL    : last3 · pos · vol_x  (ayni yontem, ayri raporlanir)
```

⚠️ `chg24` hücrede yalnız **%43,8** dolu → birincil sabitleyici olarak
**kullanılmaz**; alt kümede ikincil olarak raporlanır.

## 8 · İSTATİSTİK

- Bu bir **bölme**dir, alt küme değil → iki-örneklemli test **geçerli**
  (`CLAUDE.md`'nin `t_küme` tanımsızlığı uyarısı buraya **uygulanmaz**).
- **Birincil: gün-kümeli t** (57 gün) — günlük kol farklarının t'si.
- Welch t ve dilim-içi fark ayrıca raporlanır.
- **Etki tabanı koşumdan önce:** `|fark| ≥ 0,30 puan`. Gerekçe: gidiş-dönüş
  maliyeti %0,19; bir kapının maliyeti **aşan** katkı yapması beklenir.
- **MDE raporlanır.** `|fark| < MDE` → **"göremiyoruz"**, *"etki yok"* değil.

## 9 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra DEĞİŞTİRİLMEZ

| # | ölçüt | eşik |
|---|---|---|
| **K1** | `taker≥1.0` kolu `taker<1.0` kolundan yüksek (`+24s`, ham) | fark **> 0** |
| **K2** 🔴 | `last1` beşli dilimi **içinde** sabitlenmiş fark | **≥ +0,30 puan** |
| **K3** | gün-kümeli t | **≥ +2,0** |
| **K4** | ufuk merdiveninin **en az 3** basamağında aynı işaret | evet |
| **K5** | yoğunlaşma: **en iyi 2 gün** çıkarılınca hâlâ K1 | evet |

```
KAPI BILGI TASIYOR (KALIR)     = K1..K5 hepsi gecer
KAPI BOS (kaldirilabilir)      = K2 duser
BELIRSIZ                        = K1+K2 gecer ama K3/K4/K5'ten biri duser
                                  -> kapi KALIR (supheda DAIMA statuko)
```

🔴 **Yön uyarısı:** kapı **ters** çıkarsa (`taker<1.0` daha iyi) bu
*"kapıyı çevir"* demek **DEĞİLDİR** — tek pencere, çoklu ufuk. Yalnız
raporlanır, kural çıkarılmaz.

## 10 · NEGATİF KONTROL

Aynı zincir, `taker` yerine **`glob_ls`** (global long/short **hesap** oranı)
aynı 1,0 eşiğiyle bölünür. Bu değişken için botta bir kapı **yok** ve yön
taşıması beklenmiyor. **K2'yi geçerse ölçüm düzeneği şüphelidir** ve hüküm
yazılmaz.

## 11 · ÇOKLU KARŞILAŞTIRMA

**Birincil sonuç TEKtir:** `+24s` ufkunda, `last1` sabitlenmiş fark.
Diğer dört ufuk, sürekli rho, ikincil sabitleyiciler (`last3`/`pos`/`vol_x`)
ve `chg24` alt kümesi → **ikincil**, tek başına hüküm kurmaz.

Sayım: **1 birincil + 4 ufuk + 3 ikincil sabitleyici + 1 rho + 1 negatif
kontrol = 10 karşılaştırma.** Hüküm yalnız birincilden çıkar.

## 12 · VERİ VE NE YAPILMAZ

```
ILERI FIYAT: 1h mum, Binance fapi/v1/klines (KALICI sinif, ucretsiz)
             -> scratchpad/taker/klines/   AYRI DIZIN
```

🔴 **`scratchpad/klines_1h_uzun/` EZİLMEZ.** O dizin 2024-08-11 → 2026-08-25
arasını taşıyor ve hücre penceresi **2026-09-06**'ya uzanıyor. `CLAUDE.md`'nin
*"yeniden indirme eskiyi silebilir"* kuralı gereği taze mumlar **ayrı dizine**
iner; birleştirme okuma anında yapılır.

**Yapılmayacaklar:**
- Bota, state'e, defterlere, zamanlanmış görevlere **dokunulmaz** (salt-okuma)
- Ücretli çağrı **yok**
- En iyi hücre **seçilmez**; ölçüt sonuç görüldükten sonra **değişmez**
- Arşiv context'e **yüklenmez** — Python okur, özet basar
- Betiklerde cp1254 koruma bloğu **zorunlu**

## 13 · BEKLENTİM — koşumdan önce, olasılıkla

Kapının **BOŞ** çıkmasına **%60** veriyorum.

**Lehte:** (a) yön avında `gerçek taker oranı −0,07` ile rastgele çıktı;
(b) agresör dengesi bu projede tam bu şekilde çürüdü; (c) skor kapısı aynı
sırayla ölçülüp boş çıktı.

**Aleyhte:** taker **LONG kapısı olarak hiç ölçülmedi**; 2026-07-06'da LONG
karnesi 0W/4L olduktan sonra eklendi — o dönemin kanıtı zayıf ama sıfır değil.
Ayrıca kapı `smart`'ın *duran* pozisyonuna karşı *akan* parayı ölçüyor; bunlar
gerçekten farklı büyüklükler olabilir.

## 14 · SONUÇ NE İŞE YARAYACAK

- **BOŞ çıkarsa:** kapı `notrlong`'dan kaldırılabilir → arşiv tabanına göre
  uygun aday **~2,3 kat** artar; `N=80` ölçütü ulaşılabilir hâle gelir.
- **BİLGİ TAŞIRSA:** kapı kalır ve `notrlong`'un ölçüt penceresi
  (`80 poz / 30 gün`) **başka bir yolla** düzeltilmek zorundadır — çünkü
  karşı-olgunun kendi hızı (2,06 poz/gün) o eşiğin **%77'si**.

Her iki durumda da karar **ayrı** verilir; bu ön-kayıt yalnız kapıyı ölçer.
