# ÖN-KAYIT — skorun TERS kenarı botun MEKANİĞİYLE hayatta kalıyor mu?

**Yazılma tarihi:** 2026-08-26 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Aşama:** üç aşamalı sıranın **İKİNCİSİ** (`ham → MEKANİK → portföy`).
Birinci aşama: `olcumler.md` → *"`skor` ileri getiriyi tahmin ediyor mu"* (commit `e8c9d59`).

---

## 1 · Neden

Ham aşama şunu buldu: `skor` ileri getiriyi **monotonik ve ters** tahmin ediyor;
`≥45` bandı (botun LONG kapısı) her rejimde en düşük getirili hücre. Karıştırıcı
kapısını geçti, yoğunlaşma yok, iki zaman yarısında aynı işaret.

**Ama ham kenar hüküm değildir.** Bu projenin kendi kaydı iki yönde de ısırdı:
- kanal/StochRSI'de ham `+0,243` A-stop'la `+0,051`'e indi (kenar stopla **öldü**),
- `0..20 LONG`'da ham t=−0,90 A-stop'la t=−4,11 oldu (mekanik **güveni şişirdi**).

Bu yüzden kural önerisi ancak bu aşamadan sonra tartışılır.

## 2 · Mekanik — botun KENDİ kodundan, uydurma yok

`olcucu.measure(sym, yon, "1h", 100)` ([testbot.py:1132](testbot.py#L1132)) ve
`kripto-config.json` birebir yeniden üretilir:

| parça | kaynak | değer |
|---|---|---|
| yapı | kapanmış 1s barlar, ATR(14) Wilder, `swings(3,3)` | [olcucu.py:98](olcucu.py#L98) |
| stop | üç aday — yapısal destek/direnç ±0,25·ATR · son `nbar` dip/tepe ±0,25·ATR · 1,5·ATR — **girişe EN YAKIN geçerli** | [olcucu.py:146](olcucu.py#L146) · `olcucu_nbar_stop=10` |
| asgari stop | stop mesafesi bunun altındaysa **giriş YOK** | `asgari_stop_pct = 2,0` |
| TP1 | yapısal (varsa) yoksa `2R` | [olcucu.py:163](olcucu.py#L163) |
| TP2 | `TP1 ± 1,5R` | aynı |
| kısmi kâr | `1,5R`'de pozisyonun `%40`'ı | `kismi_kar_r=1.5` · `kismi_pay=0.4` |
| iz-süren | `2,0·ATR`; `2R`'den sonra `1,5·ATR`; `3R`'den sonra `1,0·ATR` | `trailing_atr_kat*` |
| zaman stopu | 48 saat | `zaman_stop_saat=48` |
| maliyet | taker `%0,045` + slipaj `%0,02`, **iki taraf** | `maliyet.*` |
| maliyet (2. senaryo) | ölçülmüş slipaj `%0,0499` ile | `olcumler.md` |
| fonlama | `radar_archive.funding` = **oran, %/8s** · tutma süresine göre · SHORT'ta pozitif oran **gelir** | `CLAUDE.md` ad ayrımı |

⚠️ Bar-içi sıra belirsizliği: aynı barda hem stop hem hedef dokunulduysa **stop
öncelikli** sayılır (muhafazakâr).

## 3 · Veri ve kollar

Birinci aşamanın **aynı olay kümesi**: `radar_archive` → `(sembol, saat)` tekil ·
giriş = anlık görüntünün **bir sonraki** saatinin kapanışı (ileriye bakma yok) ·
saat ofseti **−3** (radar yerel UTC+3; ölçüldü).

| kol | yön | skor |
|---|---|---|
| **A — ÖNERİ** | SHORT | `≥45` |
| **B — kontrol** | SHORT | `<5` |
| **C — botun bugünkü davranışı** | LONG | `≥45` |
| **D — kontrol** | LONG | `<5` |

**Birincil karşılaştırma önceden atanmıştır: A vs B.** C ve D **rapor** içindir
(botun ne yaptığını göstermek); onların istatistiği keşifseldir.

**Sonuç ölçüsü:** pozisyon başına **net getiri** (notional'a oran, %),
maliyet **ve** fonlama dahil. R cinsinden de raporlanır ama hüküm **net %** üzerinden
(`CLAUDE.md`: `r` alanı kısmi kârı görmez, karar önceden yapılır).

## 4 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

| # | ölçüt | eşik |
|---|---|---|
| **M1** | A'nın net ortalaması | **> 0** (maliyet + fonlama sonrası) |
| **M2** | A − B farkı | ≥ **+0,3 puan** **ve** gün-kümeli t ≥ **+2,5** |
| **M3** | işaret tutarlılığı | A − B, **≥%60 günde** pozitif (her iki kolda N≥5) |
| **M4** | zaman yarıları | A − B **iki yarıda da aynı işaret** |
| **M5** | 🔴 **ZORUNLU SINAMA** | A ve B'de **stop genişliği** ve **stop-olma oranı** raporlanır; ayrışıyorsa güven ham aşamadan okunur, mekanikten **okunmaz** |

**GEÇTİ** = M1+M2+M3+M4 · **ZAYIF** = M1+M2, biri düştü · aksi **DÜŞTÜ**.

**Ek zorunlu rapor:** asgari-stop yüzünden elenen olay sayısı · kapanış sebebi dağılımı ·
fonlamanın net içindeki payı · iki maliyet senaryosu · C ve D kolları.

## 5 · BEKLENTİ — sonuç görülmeden yazıldı

**Hayatta kalmasına ~%40 veriyorum.** İki taraflı gerekçe:

- **Lehine:** ham kenar maliyete göre büyük; fonlama SHORT'ta muhtemelen **lehte**
  (yüksek skorlu coinler kalabalık LONG taşır).
- **Aleyhine:** `≥45` bandı en yüksek oynaklığa sahip hücre; ATR tabanlı stop orada
  sık dokunur. Bu projede çıkışı **sıkılaştıran 28 varyantın 28'i de kaldı** ve
  A-stop bir ölçümde ham kenarın **%65'ini** yemişti. En olası ölüm biçimi:
  **kenar var ama stop yiyor.**

Ayrıca **C kolunun (botun bugünkü LONG davranışı) negatif çıkmasını bekliyorum** —
ham aşama bunu ima ediyor; çıkmazsa aynen raporlanır.

## 6 · Dokunulmayanlar

Bot · state · defterler · zamanlanmış görevler: **hiçbiri**. Ayrı süreç, salt-okuma.
`radar_archive.jsonl` context'e yüklenmez. Betik: `scratchpad/skor_mekanik.py`
(bu commit'ten SONRA yazılır).
