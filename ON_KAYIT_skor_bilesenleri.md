# ÖN-KAYIT — Skorun BEŞ BİLEŞENİ: hangisi bilgi taşıyor, skor yeniden kurulabilir mi?

**Yazılma tarihi:** 2026-09-04 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı talimatı (2026-09-04): *"skor bir işe yaramıyorsa beş
bileşende aramalıyız sorunu… şimdi skoru düzelt. Her testi yapabilirsin,
sağlamalarını yap. Sana tam yetki, istediğin ayarlamayı yap."*

---

## 1 · Yetki ve sınırı

Kullanıcı **kod değişikliği için yetki verdi.** Projenin kendi kuralları
**yürürlükte kalır** (kullanıcının kendi yazdığı kurallar):
ön-kayıt önce · ölçüt sonradan değiştirilmez · D/9 protokolü
(eski ölçüt **silinmez**, `[DEĞİŞTİ tarih]` eklenir) · **config'te geri alma
anahtarı** · değişiklik uygulanırsa **yeni ölçüm penceresi** ilan edilir.

## 2 · 🔴 ÖNCE YAPISAL ŞÜPHE — bileşen ayarı bunu çözmez

Skor **tek sayı** ve **iki yönde birden** kullanılıyor:
`BOGA → LONG` seçiminde · `AYI/NOTR → SHORT` seçiminde.

Bu yüzden formül **yön-bağımsız** terimler taşıyor — en açığı `abs(funding)`:
`+0,05` ile `−0,05` **aynı 15 puanı** alıyor. Kodun kendi notu bunu kabul
ediyor: *"bilginin funding'in İŞARETİNDE olduğunu gösterdi… ayrı ölçüm ister."*

🔑 **Bu ön-kayıtın ilk sorusu bileşen ağırlıkları değil, ŞUDUR:**
*"Bir bileşen LONG ve SHORT için ZIT yön mü söylüyor?"*
Söylüyorsa tek skorla iki yön seçmek **yapısal olarak imkânsızdır** ve
ağırlık ayarı semptomu tedavi eder.

## 3 · VERİ ve BİRİM

`testbot_aday_arsiv.jsonl` · 2026-08-04…09-04 · **iki rejim birden**
(`NOTR` 08-04…08-21 · `BOGA` 08-21…09-04).
Fiyat: `scratchpad/aday_pencere_1h/`. Ham ileri getiri **ve** botun mekaniği
(`seviyeler`/`oynat` **kaynaktan çağrılır**).
**Birim = SEMBOL-GÜN · gün-kümeli t.** Ufuk **4 saat** (birincil), 24 saat ikincil.

## 4 · AŞAMA A — BİLEŞEN TARAMASI (önceden sayıldı)

Beş bileşen ve alt terimleri, **her rejimde ayrı**:

| # | terim | formül |
|---|---|---|
| 1 | `s_oi` | `clamp(oi24/20)*25 + clamp(oi3/8)*10` |
| 2 | `s_fund` | `clamp(|f|/0.05)*15 + squeeze_bonus` |
| 3 | `s_comp` | `clamp((0.8−comp)/0.5)*20` |
| 4 | `s_vol` | `clamp((vol_x−1.5)/3)*20` |
| 5 | `s_brk` | `clamp((pos−0.7)/0.3)*10 + clamp(last1/4)*5` |

**Ek olarak sınanacak iki özel soru (kodda yazılı, vadesi gelmiş):**

| # | soru | gerekçe |
|---|---|---|
| **Ö1** | `funding` **işaretli** mi daha iyi, `abs` mi? | kodun kendi notu: *"bilgi işarettedir"* |
| **Ö2** | `squeeze_bonus` BOĞA'da hâlâ geçerli mi? | kodda yazılı: *"boğaya girildiğinde YENİDEN ölçülmelidir"* — girildi, ölçülmedi |

**Sınama sayısı önceden sabit: 5 bileşen × 2 rejim + 2 özel soru × 2 rejim
= 14.** Altıncı bileşen icat edilmeyecek, üçüncü özel soru eklenmeyecek.

**Her terim için ölçülen:** üst çeyrek − alt çeyrek ham getiri farkı, gün-kümeli t.

## 5 · AŞAMA B — YENİ SKOR: ARANMAZ, TÜRETİLİR

🔴 **Ağırlıklar aranmayacak.** Arama = aşırı uydurma. Yeni skor **mekanik bir
kuralla** kurulur ve kural **şimdi** sabitlenir:

```
1. Bir terim ANCAK su iki sart birden saglanirsa yeni skora girer:
     (a) gun-kumeli |t| >= 2,0     ve
     (b) KRONOLOJIK IKI YARIDA DA ayni isaret
2. Giren terimin agirligi, olculen farkiyla ORANTILI (normalize edilir,
   toplam 100 puan). Elle ayar YOK.
3. Yon celiskisi olan terim (NOTR'da bir isaret, BOGA'da ters) ATILIR —
   tek skorla iki yon secilemez.
4. Hicbir terim gecmezse: YENI SKOR KURULMAZ ve bu aynen raporlanir.
```

## 6 · AŞAMA C — DOĞRULAMA (hüküm buradadır)

Yeni skor ile mevcut skor, **aynı kapı eşiği mantığıyla** karşılaştırılır:
her ikisinin **üst %36'sı** alınır (mevcut eşiğin fiilen aldığı pay).

| # | ölçüt | eşik |
|---|---|---|
| **K1** | yeni skorun seçtiği dilim − mevcut skorunki | **> 0**, gün-kümeli t ≥ **+2,0** |
| **K2** | **AYRI YARIDA doğrulama** | terimler **A yarısında** seçilir, hüküm **B yarısında** ölçülür |
| **K3** | mekanik aşaması | fark mekanikli ölçümde de **> 0** |
| **K4** | aday sayısı | yeni eşik, mevcut kadar aday geçirmeli (**kısır kapı yasağı**) |

**GEÇTİ** = K1+K2+K3+K4. **K2 belirleyicidir**: terimler bir yarıda seçilip
aynı yarıda ölçülürse sonuç **kaçınılmaz olarak** iyi çıkar.

🔴 **GÜÇ DENETİMİ ZORUNLU** — `|fark| < MDE` ise *"göremiyoruz"*.

## 7 · UYGULAMA — ne olursa ne yapılacak (şimdi karara bağlanıyor)

| sonuç | eylem |
|---|---|
| **GEÇTİ** | `radar.py` skor formülü değiştirilir · `esikler.skor_surum: 2` anahtarı eklenir (0 = eski formül, **geri alma**) · `durum.md`'ye `[DEĞİŞTİ 2026-09-04]` · **yeni ölçüm penceresi** ilan edilir |
| **Ö1/Ö2 tek başına geçerse** | yalnız o terim değiştirilir (işaretli funding / `squeeze_bonus` kapatma), aynı protokol |
| **DÜŞTÜ** | **kod değişmez.** Skorun *"ayırmıyor"* hükmü kalır ve *"bileşen ayarı da çözmüyor"* eklenir |

⚠️ Uygulanırsa değişiklik **botun hangi işlemi açacağını değiştirir** → mevcut
ölçüm penceresi biter, yenisi başlar (D/8).

## 8 · BEKLENTİ — sonuç görülmeden yazıldı

**K1+K2'nin geçmesine ~%25 veriyorum.** Gerekçe: bu oturumda 43 hücrelik
permütasyon düzeltmeli tarama **hiçbir ayırıcı bulamadı** ve skor eşiğinin
kattığı değer **+0,006 puan** çıktı. Bileşenler o taramanın içindeydi.

**Ö1 (işaretli funding) ~%45** — projenin kendi ölçümü bu yönü destekliyor.
**Ö2 (`squeeze_bonus` BOĞA'da zararlı) ~%50** — kural ayı piyasasında
ölçülmüştü, boğada tersine dönmesi kodun kendi uyarısı.

**Yönlü tahminler (tutmazsa aynen raporlanır):**
1. `s_comp` hiçbir rejimde geçmeyecek (BOĞA'daki katkısı zaten %3).
2. En az bir terim **iki rejimde ZIT işaret** verecek → kural 3 ile atılacak.
3. `s_oi` skorun %41'i olduğu hâlde tek başına anlamlı **çıkmayacak**.

## 9 · Dokunulmayanlar (ölçüm boyunca)

Ölçüm salt-okuma; hiçbir bot dosyası **ölçüm sırasında** değişmez.
Değişiklik ancak Aşama C **geçerse** ve bölüm 7'deki protokolle yapılır.
Betik: `scratchpad/skor_bilesen.py` (bu commit'ten SONRA).
