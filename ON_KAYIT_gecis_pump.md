# ÖN-KAYIT — "nötr→boğa geçiş anında tetiklenen pump artıda kapanır"

**Yazılma tarihi:** 2026-08-25 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı hipotezi — *"bunların değişimini yakala, notrden boğaya geçiş
anında bu tetiklenirse artıda kapanır"*

---

## 1 · Neden bu ölçüm

Aynı gün yapılan portföy ölçümü şunu buldu (`scratchpad/pump_portfoy_rejim.py`):

| kol | NÖTR 08-10..08-18 | BOĞA 08-19..08-25 |
|---|---|---|
| pump skor<45 | −11,31% | +43,51% |
| bot TÜMÜ | +2,30% | −23,94% |

Kural boğada ödüyor, yatayda kanıyor. Kullanıcının önerisi: kuralı sürekli açık
tutmak yerine **rejim geçişine bağlamak**.

⚠️ **Bu ön-kaydın var olma sebebi:** elimizdeki canlı defterde **tek bir geçiş** var
(2026-08-21) ve bulguyu üreten pencere odur. Aynı geçiş üzerinde sınamak döngüseldir.
Bu yüzden ölçüm **2 yıllık mum verisine** taşınıyor.

## 2 · Veri

- `scratchpad/klines_1h_uzun/` — 567 sembol, 1 saatlik, 2024-08-11 → 2026-08-25
- Rejim serisi: `evren.btc_rejim()` gün gün **yeniden üretildi**, tamamen nedensel
  (yalnız o güne kadarki veri). Betik: `scratchpad/rejim_gecis_sayim.py`
- **Doğrulandı:** yeniden üretim 2026-08-25'te `BOGA · TAM_BOGA · sezon BOGA ·
  hava BOGA` veriyor — botun canlı etiketiyle birebir aynı.
- Isınma (21 hafta SEZON) sonrası kullanılabilir pencere: **2024-12-23 → 2026-08-25,
  611 gün.**

**Örneklem büyüklüğü (koşumdan önce sayıldı, sonuç DEĞİL):**

```
NOTR->BOGA gecis : 7      (2025-01-17 · 05-06 · 07-10 · 09-12 · 10-03 · 10-12 · 2026-08-21)
BOGA epizodu     : 7      medyan uzunluk 11 gun
rejim dagilimi   : NOTR %51,2 · AYI %33,4 · BOGA %15,4
```

## 3 · Tetik tanımı (nedensel, ileriye bakmaz)

`testbot.py:1500`'ün mum verisinden yeniden üretilebilir hâli. Sembol `s`, saat `h`:

```
chg24 = c[h] / c[h-24] - 1      >= +0,10
vol_x = v[h] / ortalama(v[h-24:h]) >= 2,0
```

İkisi de `h` barının kapanışında bilinir. **Tekilleştirme:** aynı sembolde 24 saat
içinde birden çok tetik varsa **yalnız ilki** sayılır (tek pump 10 olay gibi
sayılmasın).

⚠️ `skor < 45` süzgeci bu aşamada **YOK** — `skor` radar bileşiğidir, mumdan
üretilemez. Bu ölçüm **tetik × geçiş** etkileşimini sınar, skor kapısını değil.
Skor kapısı ayrı bir ölçümün konusudur.

## 4 · Bantlar

Geçiş günü `D` = BOĞA etiketinin ilk günü.

| bant | tanım |
|---|---|
| `ONCE` | `[D−3g, D)` — hareket başladı, etiket **henüz dönmedi** |
| `T0` | `[D, D+3g)` — **kullanıcının hipotez penceresi** |
| `T1` | `[D+3g, D+7g)` |
| `T2` | `[D+7g, epizod sonu)` |
| `KONTROL` | geçiş `i` için: `D_i`'den önceki 30 günde, rejimi BOĞA **olmayan** ve `[D_i−3g, D_i)` dışında kalan tetikler |

`KONTROL` bilerek **aynı piyasa dönemine** demirlendi; böylece "2025 mi 2026 mı"
farkı değil, geçişe yakınlık ölçülür.

## 5 · Ölçülen büyüklük — HAM, mekaniksiz

`CLAUDE.md` sırası gereği bu **birinci aşamadır**: stop yok, hedef yok, fonlama yok.

```
ham ileri getiri = c[h+H] / c[h] - 1        H = 24 saat (BIRINCIL) · 48 saat (ikincil)
```

Mekanik aşama **yalnız ham aşama geçerse** koşulur.

## 6 · İstatistik

**Küme = geçiş epizodu (7 adet).** Her geçiş için eşleşmiş fark:

```
d_i = ortalama(T0 tetikleri, geçiş i) - ortalama(KONTROL tetikleri, geçiş i)
```

→ 7 değer üzerinde eşleşmiş t (df=6). Olay-düzeyi N raporlanır ama **çıkarım
küme düzeyinde** yapılır.

**Birincil karşılaştırma önceden atanmıştır:** `T0` vs `KONTROL`, `H=24`.
Diğer bantlar ve `H=48` **keşifseldir**; onlar için Bonferroni eşiği |t| ≥ 4,0
(df=6, 8 karşılaştırma) uygulanır ve ayrıca işaretlenir.

## 7 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

| # | ölçüt | eşik |
|---|---|---|
| **G1** | birincil fark `T0 − KONTROL`, H=24 | ortalama ≥ **+1,0 puan** **ve** t ≥ **+2,5** |
| **G2** | işaret tutarlılığı | 7 geçişin **≥5**'inde fark pozitif |
| **G3** | çürütme kapısı | `ONCE` ≥ `T0` ise **geçiş tespiti hiçbir şey katmıyor** demektir → hüküm "kural pump'ın kendisinde, geçişte değil" |
| **G4** | karıştırıcı | `chg24` bandı (10-20/20-40/40+) × `vol_x` bandı (2-3/3-5/5-10/10+) içinde eşleştirildiğinde etki **≥3 hücrede aynı işaretle** ayakta kalmalı |
| **G5** | şans | 7 sahte geçiş tarihi (aynı rejim-günü dağılımından) × 2000 çekiliş → gerçek etki **p ≤ 0,05** |

**GEÇTİ** = G1+G2+G4+G5 hepsi · **ZAYIF** = G1+G2, G4 veya G5 düştü · aksi **DÜŞTÜ**.

**Ek zorunlu rapor (hüküm değil, sonraki aşama için):** her bandın oynaklığı
(ATR/fiyat medyanı). Bantlar oynaklıkta ayrışıyorsa mekanik aşamada ham getiri
zorunlu kalır (`CLAUDE.md` 2026-08-20 ihlali).

## 8 · BEKLENTİ — sonuç görülmeden yazıldı

**G1'in düşmesini bekliyorum. Geçme olasılığına ~%25 veriyorum.** Gerekçeler:

1. **Etiket hareketi geç yakalıyor.** Tek gözlemleyebildiğim geçişte hareket
   08-19'da başladı, etiket **08-21'de** döndü — BTC o arada zaten **+%21** yapmıştı.
   Bu doğruysa `ONCE` ≥ `T0` çıkar ve **G3 tetikler**.
2. **BOĞA etiketinin kendisi BTC için kenar taşımıyor.** 7 epizodun BTC getirisi:
   −7,2% · +9,1% · +1,7% · −2,9% · −7,7% · −1,7% · +3,1% → **7'nin 4'ü negatif**,
   medyan ≈ −1,7%. Etiket "yükselecek" demiyor.
3. 7 küme çok az; gerçek bir etki bile bu güçle t=2,5'i zor geçer.

**Bu beklentinin yanlış çıkmasını isterim** — ama ölçüt yukarıda sabittir ve
sonuç ne çıkarsa aynen yazılacaktır.

## 9 · Dokunulmayanlar

Bot, state, defterler, zamanlanmış görevler: **hiçbiri**. Ölçüm ayrı süreç,
ayrı dosya, salt-okuma. Betik: `scratchpad/gecis_pump_ham.py` (bu commit'ten sonra yazılır).
