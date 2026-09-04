# ÖN-KAYIT — BOĞA'da LONG: yön mü yanlış, mekanik mi öldürüyor?

**Yazılma tarihi:** 2026-09-04 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** `hakem-penceresi-hukmu.md` §7 *"Birinci — LONG kilidi"* ve
2026-09-04 kapı karnesi (`olcumler.md` → *KAPI × FONLAMA*).

---

## 1 · Neden bu ölçüm

Ölçüldü ve kayıtlı: bot 24 Ağustos'tan beri BOĞA rejiminde **tek bir SHORT
açmadı** (12.594 aday satırında SHORT istisnasını sağlayan **sıfır** satır),
o sürede **217 LONG** pozisyon açtı ve toplam kaybın **~%70'ini** üretti.

🔴 **Ama iki bambaşka açıklama var ve karneden ayırt edilemiyor:**

| açıklama | eylem |
|---|---|
| **A — yön yanlış:** bu adaylarda LONG ham fiyatta da kaybediyor | LONG dalı daraltılır / kapatılır, SHORT istisnası genişletilir |
| **B — mekanik öldürüyor:** ham yön nötr/olumlu ama stop kesiyor | kapıya dokunulmaz, **stop** ölçülür |

Karne B'yi ima ediyor gibi: stop-olma oranı **%95**, medyan tutma **2,2 saat**.
Ama üç ayrı ölçüm A diyor. **Bu ön-kayıt ikisini ayırır.**

`CLAUDE.md`'nin ölçüm sırası bunu zaten emrediyor:
`ham ileri getiri → ticaret mekaniği → portföy simülasyonu`.
Bugüne kadar bu popülasyonda **ham getiri hiç ölçülmedi.**

## 2 · POPÜLASYON ve BİRİM

**Kaynak:** `testbot_aday_arsiv.jsonl` — 33.135 satır · 292 sembol ·
2026-08-04…2026-09-04 (30 gün). Tüm alanlar %100 dolu.
⚠️ Arşivin tamamı `rejim` tanım kırılmasından (2026-07-22) **sonra** →
alan anlamı sabit, kırılım güvenli.

🔴 **BİRİM = SEMBOL-GÜN, satır DEĞİL.** Aday satırları 7,5 dakikada bir
yazılıyor; aynı sembol aynı gün onlarca satır üretiyor. Satır saymak sahte N
üretir — bu proje bunu bir kez yaşadı (`olay seviyesi örnekleme` notu).
Her `(sembol, gün)` çifti, o gün nitelenen satırlarının **ortalaması** olarak
**tek gözlem** sayılır.

**Kollar:**

| kol | tanım |
|---|---|
| **KAPI** | `rejim=BOGA` **ve** `score ≥ 45` **ve** `smart ≠ SHORT` **ve** `pos ≤ 0,85` |
| **TABAN** | `rejim=BOGA` — tüm satırlar (piyasa sürüklenmesi tabanı) |

Eşikler koddan ve config'ten **okundu, varsayılmadı**:
`radar_short_skor = 45.0` · `pos ≤ 0.85` sabit ([testbot.py:617](testbot.py#L617)).

## 3 · ÖLÇÜLEN BÜYÜKLÜK — HAM, mekaniksiz

```
E = satirin ts'ini ICEREN 1 saatlik barin KAPANISI
ret(H) = (P(t+H) - E) / E * 100          yon LONG
```

Mekanik **YOK**: stop yok, hedef yok, kısmi kâr yok, maliyet yok.
Ufuklar: **H ∈ {1, 4, 12, 24} saat**. **Birincil H = 4 saat.**

⚠️ `E` satırın anından **sonra** oluşan bir fiyattır (bar kapanışı) → gecikme,
ileriye bakma değil. Muhafazakâr yönde.

**Fiyat:** Binance `fapi` 1 saatlik mum, 2026-08-03…2026-09-05,
`scratchpad/aday_pencere_1h/` (YENİ dizin; `perp_seri` ve `klines_1h_uzun`
**okunmaz da yazılmaz da**).
⚠️ `perp_seri` kasten kullanılmıyor: 292 sembolün yalnız **141'ini** kapsıyor.

🔴 **ZAMAN DİLİMİ SINAMASI ZORUNLU.** Arşiv `ts`'i YEREL (UTC+3), mumlar UTC.
Betik her satırda `price` alanının, eşlenen barın `[low, high]` aralığına
düşüp düşmediğini sınar. **İçeride kalma oranı %90'ın altındaysa betik
çalışmayı reddeder** — yanlış kaydırma sessizce her şeyi bozar.

## 4 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

🔴 **BİRİNCİL HÜCRE ÖNCEDEN ATANDI:** kol = **KAPI** · H = **4 saat** ·
birim = **sembol-gün**.

| # | ölçüt | eşik |
|---|---|---|
| **K1** | KAPI kolunun ham getirisi | ortalama **< 0** **ve** sembol-gün t ≤ **−2,0** |
| **K2** | KAPI − TABAN farkı | **< 0** **ve** t ≤ **−2,0** (kapı anti-seçici mi) |

**ÜÇ YOLLU HÜKÜM — her biri FARKLI bir eylem doğurur:**

| sonuç | okuma | eylem |
|---|---|---|
| **K1 GEÇTİ** | yön yanlış: ham fiyatta da kaybediyor | LONG dalı ele alınır · SHORT istisnası gündeme gelir |
| **K1 düştü, ortalama ≈ 0** | yön nötr | **kapıya dokunulmaz**, sıra **stop** ölçümüne geçer |
| **K1 düştü, ortalama > 0** | yön doğru, mekanik yiyor | kapı **kesinlikle** değişmez; sorun stop/hedef |

⚠️ **Çoklu karşılaştırma:** 2 kol × 4 ufuk = 8 hücre. Hüküm taşıyan **1**,
önceden atandı. Kalan 7 **betimleyicidir**.

**İKİNCİL — betimleyici, hüküm taşımaz, önceden sayıldı (3 adet):**
1. Ufuk eğrisi (1/4/12/24 sa) — kayıp süreyle büyüyor mu?
2. `taker ≤ 1,0` vs `> 1,0` ayrımı, BOĞA satırlarında. *Gerekçe:* SHORT
   istisnasını kesen şart tam olarak bu (ölçüldü: 35 satırın 35'i buradan
   düştü). Ayırıyor mu?
3. `BASLIYOR + smart=SHORT` alt kümesi. **N'in çok küçük olacağı biliniyor**
   (11 günde tek sembol) — sayı olduğu gibi yazılır, hüküm çıkarılmaz.

**Zorunlu ek rapor:** satır sayısı **ve** sembol-gün sayısı · sembol
yoğunlaşması (en büyük sembolün payı) · zaman dilimi sınaması sonucu ·
kaynak kapsamı (kaç sembolde mum bulunamadı) · **MDE**.

🔴 **OYNAKLIK EŞİTLİĞİ (CLAUDE.md 2026-08-20).** KAPI ve TABAN kolları
oynaklıkta ayrışıyorsa kıyas bozulur. Her kol için `|getiri|` ortalaması
raporlanır; **1,5 kattan fazla ayrışma varsa K2 hükmü ZAYIF sayılır** ve
öyle yazılır.

🔴 **GÜÇ DENETİMİ.** MDE (t=2) hesaplanır. Bir sonuç *"düştü"* diye
yazılacaksa ve MDE ilgili eşikten büyükse, hüküm **"göremiyoruz"** olur.

## 5 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%45 veriyorum.** İki taraf da ciddi: üç bağımsız ölçüm
LONG'un kaybettiğini söylüyor (A'yı destekler), ama %95 stop oranı ve 2,2
saatlik medyan ömür mekaniğin tek başına yeteceğini düşündürüyor (B).
**Bu ölçümün değeri tam da bu belirsizlikte.**

**Yönlü tahminler (tutmazsa aynen raporlanır):**
1. **TABAN kolu hafif ARTI** çıkacak — pencerede BTC yaklaşık **%12** yükseldi,
   yani ham sürüklenme yukarı.
2. **KAPI − TABAN farkı NEGATİF** çıkacak: skor momentum seçiyor, momentum
   seçimi tepeden alır.
3. Ufuk eğrisi: kayıp **24 saatte 4 saatten büyük** olacak.

🔴 **Ve şimdiden:** K1 geçse bile bu **kural değildir.** Ham getiri ölçümün
**birinci** aşamasıdır; kapı değişikliği ancak mekanik + portföy aşamalarından
sonra ve **yeni bir pencere** tanımlanarak tartışılır. Hakem raporunun kendi
sözü: *"Şüphede DAİMA statüko. Kapı kapatmak kullanıcı kararıdır."*

## 6 · Dokunulmayanlar

`testbot.py` · `golge.py` · `ayna.py` · `defter2/3` · `radar.py` · `evren.py` ·
`kripto-config.json` · state · defterler · zamanlanmış görevler: **hiçbiri.**
Salt-okuma, ücretli çağrı yok. Betik: `scratchpad/boga_long_ham.py`
(bu commit'ten SONRA yazılıp koşturulur).
