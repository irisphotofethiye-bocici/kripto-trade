# ÖN-KAYIT — KÂR KİLİDİNİN ARALIĞI: sabit ROI puanı mı, ATR mi?

**Yazılma tarihi:** 2026-09-07 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"ölç"* (canlı ölçüm kuralın kaybettirdiğini gösterdi)
**Betik:** `scratchpad/kilit_aralik/01_olcum.py`

---

## 1 · NEDEN — teşhis var, çözüm ölçülmedi

Canlı ölçüm (`olcumler.md`, 2026-09-07): kilit tetiklediği **üç vakada da
kaybettirdi**, temiz dörtlüde `+7,61 $` vs `+546,38 $` → **−538,77 $**.

Teşhis sayısal: tetik ile kilit stopu arasındaki aralık tanım gereği
**`5/kaldıraç`** ve ölçüldüğünde **medyan 0,35 ATR** çıkıyor — yani
**gürültünün içinde**.

🔑 Hipotez: sorun *"kilit fikri"* değil, **aralığın ATR'ye göre çok dar
olması.** Aralık ATR cinsinden tanımlansaydı davranış değişir miydi?

## 2 · POPÜLASYON — botun defteri DEĞİL, temiz simülasyon

🔴 `01_olcum.py` botun defterini kullanmıştı ve **kaybedene yanlıydı**
(kazananlar kısmi kâr aldığı için yeniden kurulamıyordu). Bu ölçüm o hatayı
tekrarlamayacak:

```
POPULASYON : radar_archive · score>=30 · 4sa cooldown · LONG
             (giris_arama · r_hedef · stop_mesafesi_LONG ile AYNI evren)
MEKANIK    : olcucu uclu stop · %10 hedef · 48s zaman stopu · maliyet %0,09
N          : ~2.000 giris · ~72 gun
KESIF      : ilk %60 gun    HOLDOUT : son %40 gun
```

**Eşleşmiş tasarım:** aynı girişler, **yalnız çıkış değişir**
(`stop_mesafesi.py` deseni). Seçim yanlılığı **yok** — her giriş her kolda.

## 3 · KOLLAR — ARANMAZ, koşumdan önce ilan

Kullanıcının kuralının iki parçası **SABİT** tutuluyor:
`tetik` yeri ve `%20 kısmi alım`. **Yalnız ARALIK değişiyor.**

```
tetik  : giris + 1,2 x ATR14      (SABIT, tum kilit kollarinda ayni)
alim   : pozisyonun %20'si        (SABIT — kullanici karari)
aralik : DEGISKEN
```

| kol | aralık | ne demek |
|---|---|---|
| **A0** | — | **kilit YOK** (mevcut taban) |
| **G0.35** | 0,35 ATR | **bugünkü kuralın ATR karşılığı** |
| **G1.00** | 1,00 ATR | 🔴 **BİRİNCİL** |
| **G1.50** | 1,50 ATR | |
| **GBE** | tetik kadar (stop = giriş) | klasik başabaş referansı |

🔴 **`G1.00` neden birincil:** ATR'nin **kendisi** doğal birim; `1,0`
**aranmış bir sayı değil**, ölçeğin tanımı. `0,75` veya `1,25` gibi ara
değerler **hiç denenmeyecek** — denenirse eşik araması olur.

🔴 **`1,2 ATR` tetik nereden geliyor:** canlı 13 pozisyonda `tetik% / ATR%`
oranı ölçüldü — `1,15 · 1,20 · 1,27 · 1,30 · 1,38 · 1,44 · 1,70 · 1,81 ·
1,82 · 1,92` (medyan ~1,4, alt uç 1,15). **`1,2` alt uca yakın seçildi ve
koşumdan önce ilan ediliyor.** Yayılım geniş; bu bir **yaklaşıklıktır** ve
hüküm bu kabulle sınırlıdır.

## 4 · ÖLÇÜT — birincil metrik ve karşılaştırma

```
BIRINCIL : HOLDOUT'ta ESLESMIS fark  (G1.00 - A0),  net %
```

**Neden `net %`, `R` değil:** kollar **aynı girişi ve aynı orijinal stopu**
paylaşıyor → `R`'nin paydası her kolda aynı, ortak-payda tuzağı yok. Yine de
`R` **ikincil** olarak raporlanır. Kaldıraç yok; kaldıraç `net %`'i doğrusal
ölçekler, **sıralamayı değiştirmez.**

| # | ölçüt | eşik |
|---|---|---|
| **P1** | HOLDOUT eşleşmiş fark `G1.00 − A0` | **> 0** |
| **P2** | HOLDOUT **gün-kümeli t** | **≥ +2,0** |
| **P3** | \|fark\| > **MDE** | evet |
| **P4** | KEŞİF ve HOLDOUT **aynı işaret** | evet |
| **P5** | **permütasyon** (gün bazında işaret çevirme, 2.000 tur), dört kilit kolunun `max\|t\|` | **p < 0,05** |

```
GECTI       = P1..P5 hepsi
DUSTU       = P1 veya P4 duser
GOREMIYORUZ = P1+P4 gecer, P3/P5 duser
```

`P5` dört kolun çoklu karşılaştırmasını kapatır (`stop_mesafesi` deseni).

## 5 · AYRICA CEVAPLANACAK — ölçüt DEĞİL, ama soru bu

🔴 **`G0.35 − A0` işareti**: bugünkü kural bu popülasyonda da kaybettiriyor
mu? Canlı `N=3`'tü; burada `N~2.000`. **Bu bir ölçüt değil** — çünkü kural
zaten uygulanmış durumda ve bu ölçüm onu doğrulamak için kurulmadı. Ama
işaret raporlanacak ve `durum.md`'ye geçecek.

## 6 · ZORUNLU SINAMA

1. **Merdiven monotonluğu:** `G0.35` stopu ≤ `G1.00` ≤ `G1.50` ≤ `GBE`
   (medyan mesafe). Değilse betik **çalışmayı reddeder**.
2. **Parametresiz hâl = kaynak:** kilit kapalı koşulduğunda `A0` ile
   **birebir** aynı sonucu vermeli (fark 0). Değilse **reddeder**.
3. **Sıra:** her barda `stop → tetik → hedef` — `testbot`'un bar döngüsüyle
   **aynı**. Aynı barda stop ve tetik varsa **stop önce** (kötümser).

## 7 · EK RAPOR — ölçüt DEĞİL

- Her kol: ort `net %` · ort `R` · isabet% · **tetikleme oranı** ·
  kilit stopuyla kapanma oranı · medyan tutma
- 🔴 **Kuralın maliyeti:** kilit stopuyla kapanıp `A0`'da **hedefe varan**
  pozisyon sayısı (canlıda `INJ`/`CFG` buydu)
- 🔴 **Kuralın faydası:** kilit stopuyla kapanıp `A0`'da **stop olan** sayısı
- Tetik `1,8 ATR` ile duyarlılık **tekrarı** — ailenin dışında, ayrı raporlanır

## 8 · NE YAPILMAZ

- Bota, state'e, defterlere **dokunulmaz** (salt-okuma)
- **Aralık aranmaz** — dört kol yukarıda sabit
- Tetik ve `%20` alım **değiştirilmez** (kullanıcı kararı)
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 9 · GEÇERSE

1. Ham mekanik ölçümdür → sonra **portföy simülasyonu**
2. Ancak o da geçerse `notrlong`'a uygulama + **pencere sıfırlama**
3. 🔴 **`P1` geçse bile kod otomatik değişmez** — kural kullanıcının, karar
   kullanıcının.

## 10 · BEKLENTİM — koşumdan önce, olasılıkla

**`G1.00 > A0` olmasına %25.** Kilit her hâlükârda **kazananın %20'sini
erken alıyor**; geniş aralık zararı azaltır ama artıya çevirmesi ayrı iş.
Ve bu proje **çıkışı sıkılaştıran 32 varyantın 31'ini** reddetti; kilit
sıkılaştırmadır.

**`G0.35 < A0` (bugünkü kural kaybettiriyor) olmasına %75** — canlı üç vaka
ve `0,35 ATR` teşhisi aynı yeri gösteriyor.

⚠️ Ve bugün **on beş ön-kayıt yazıldı, on beşi de geçemedi.**
