# ÖN-KAYIT — STOP MESAFESİ: A+B'nin stopu kapısına uymuyor mu?

**Yazılma tarihi:** 2026-09-05 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı talimatı (2026-09-05): *"stop mesafesini ölç."*
Bu, hakem raporunun **5. maddesi** (`hakem-penceresi-hukmu.md`) ve defterde
*"pencere sonrası İLK İŞ"* diye yazılı olan iş. Pencere kilidi kalktı.

---

## 1 · Kayıtlı olgu — bu ölçümün çıkış noktası

`olcumler.md` → *"A+B'nin ham kenarının %65'ini KENDİ STOPUMUZ yiyor"*:

| kapı | stopsuz ham | A-stop ile | kayıp |
|---|---|---|---|
| **A+B** | +6,10 | +2,14 | **%65** |
| **MA50+ucuz** | +0,78 | +0,84 | **%0 — korunmuş** |

Defterin sözü: *"stop mesafesi A+B için yeniden ölçülmeli. İki kapı arasındaki
asimetri de dikkat çekici: MA50+ucuz'un stopu kapıya uyuyor, A+B'nin uymuyor."*

## 2 · 🔴 ÖNCE: BU ÖLÇÜMÜ DOĞURAN BULGU ŞÜPHELİ

Yukarıdaki tablo **stopsuz** kolu **sabit ufukta** tutup A-stop koluyla
karşılaştırdı. İki kolun **tutma süresi eşit değil** — stoplu kol erken çıkar.

**Bu tam olarak `stop_mu_sure_mu` ölçümünün (2026-08-26) yakaladığı kusur.**
Orada ufuk eşleştirilince *"stop kenarı yiyor"* iddiası **çöktü ve işaret döndü**:
`Δ_stop = +0,120` — stop **yardım ediyordu**.

Yani bu ön-kayıt, kendi gerekçesine de şüpheyle bakıyor. Sonuç ne olursa olsun
**%65 kaydının durumu bu ölçümle birlikte yeniden yazılacak.**

## 3 · KAPSAM — `oi24` bacağı ÖLÇÜLEMEZ, bu koşumdan önce sayıldı

A+B = `funding ≤ −0,05` **ve** `oi24 ≥ %10`. İkinci bacak için OI geçmişi gerek;
Binance OI **30 günlük** sınıftır ve arşivimiz (`perp_seri`) 2026-07-22'de başlıyor.

**Sayıldı** (`scratchpad/stop_kapsam_sayim.py`, yalnız tetik sayar — getiri
hesaplamaz, dolayısıyla sonuç değişkenine dokunmaz):

```
perp_seri OI olan sembol                        153   (klines: 566)
A_funding tetigi, OI penceresi icinde            64   ayri gun 23
```

**64 bir ÜST SINIRDIR** — `A+B ⊂ A_funding`, `oi24` kapısı bunu daha da küçültür.
Bu N'de stop genişliği taraması yapılamaz. Aynı kısıt `olcumler.md`'de bir kez
kayıtlı: *"oi24 bacağı ölçülemedi (OI geçmişi ~30 gün)"*.

🔴 **Bu yüzden ölçülen şey A+B'nin FUNDING BACAĞI'dır**, tam A+B değil. Hüküm
metninde bu **açıkça** yazılacak; *"A+B ölçüldü"* denmeyecek.

## 4 · EVREN ve MEKANİK — yeniden yazılmaz, KAYNAKTAN çağrılır

`ileri_rr.py` / `asgari_stop.py` ile **birebir aynı** (fonlama birim onarımı
sonrası hâli):

| | |
|---|---|
| veri | `scratchpad/klines_1h_uzun/` · 566 sembol · ~2 yıl |
| kümeler | `A_funding` (funding ≤ −0,05) · `B_ma50ucuz` (fiyat ≤ $0,07 & MA50 ≥ %3,72) |
| yön | **SHORT** (iki kapı da SHORT açar) |
| giriş | tetiğin **ertesi** 1h barının açılışı |
| hedef | sabit **%10** · ufuk **72s** · maliyet **%0,13** · **fonlama DAHİL** |
| eleme | `ISINMA=220` · `SEYRELT=24` · pump ≥ %20 · hacim tabanı $3M/24s |
| bar içi sıra | STOP (fitil) → HEDEF (fitil) |

Ön-sayım: `A_funding` **7.274** tetik / 697 gün · `B_ma50ucuz` **10.361** / 687 gün
(asgari-stop elemesinden **önce**; koşumda gerçek N raporlanır).

## 5 · KOLLAR — dört tane, ÖNCEDEN SABİT, arama YOK

| kol | stop |
|---|---|
| **`A`** | botun mevcut stopu — yapısal adaylardan girişe **en yakın** (tavanı 1,5×ATR) · **TEMEL** |
| `1.5x` | sabit **1,5×ATR** (A'nın fallback'i; yapısal adaylar kaldırılmış) |
| `2.5x` | sabit **2,5×ATR** |
| `4.0x` | sabit **4,0×ATR** |

🔑 **Bu dört değer İCAT EDİLMEDİ** — `gainer_stop.py`'nin (2026-08-10) ön-kayıtlı
kol kümesinin aynısı. Yeni eşik uydurmak yerine mevcut ön-kayıtlı küme kullanıldı.

⚠️ **Merdiven monotondur:** SHORT'ta `A ≤ 1.5x ≤ 2.5x ≤ 4.0x` **tanım gereği**
(A, tavanı 1,5×ATR olan bir minimumdur). Bu, K3'ü (komşu hücre) anlamlı kılar.

**Beşinci kol EKLENMEYECEK. Ara değer (2,0x · 3,0x) DENENMEYECEK.**

## 6 · 🔴 ÖLÇÜ — İKİSİ DE RAPORLANIR, ROLLERİ ŞİMDİ SABİTLENİYOR

| ölçü | tanım | rol |
|---|---|---|
| **`R`** | `net% / stop%` — **her kolun KENDİ stop genişliğine** bölünür | 🔴 **BİRİNCİL** |
| `net%` | işlem başına net getiri (maliyet + fonlama dahil) | ikincil, her zaman yazılır |

**Neden `R` birincil:** bot **risk-bazlı boyutlandırır** —
`notional ≈ hedef_risk / stop_frac`. Stop iki kat genişse pozisyon yarı boydur,
aynı fiyat yolu **yarı dolar** üretir. `net%` bunu göremez; `R` görür, çünkü
`dolar = hedef_risk × R` ve `hedef_risk` kollar arasında **sabittir**.

Bu varsayım **bu projede ölçüldü** (`olcumler.md` → *RİSK PARİTESİ*):
gerçekleşen/hedef risk medyanı **1,000**, `kaldirac_max` bağlamıyor.

⚠️ **ORTAK PAYDA TUZAĞI — neden burada geçerli DEĞİL.** `CLAUDE.md` kuralı
*"paydasında karşılaştırdığın değişken olan bir oranın KORELASYONU dayanak
olamaz"* der. Burada korelasyon yok; **kollar arası eşleşmiş ortalama farkı** var
ve `hedef_risk` sabittir. 🔴 **Buna karşılık şu YASAK ve yapılmayacak:**
`stop genişliği ~ R` korelasyonu **delil olarak raporlanmaz** — o, tam olarak
kuralın yasakladığı şeydir.

## 7 · EŞLEŞTİRME — popülasyon dört kolda AYNI olmak zorunda

`asgari_stop_pct = %2,0` elemesi **`A` kolunun stopuna göre** uygulanır ve
**dört kolda da aynı girişler** kullanılır. Aksi hâlde geniş stoplu kollar daha
çok aday geçirir → farklı popülasyon → eşleşmiş test tanımsız
(`CLAUDE.md` → *ALT-KÜME testinde `t_küme` TANIMSIZ*).

⚠️ Gerçek botta geniş stop **akışı da** değiştirir (daha çok aday `%2` kapısını
geçer). Bu **ayrı bir etkidir** (akış ≠ yol) ve **betimleyici olarak** raporlanır:
her kolun kendi elemesiyle kaç aday geçerdi. **Hüküm taşımaz.**

## 8 · İSTATİSTİK

- Eşleşmiş fark: `d = R(kol) − R(A)`, işlem başına
- **Gün-kümeli t** (küme = girişin takvim günü)
- **İşaret-çevirme permütasyonu:** günler bazında işaret çevrilir, **2.000** tur,
  üç varyantın `max|t|`'si kaydedilir → *"şansla bulunanın"* dağılımı
- 🔴 **MDE (t=2'de görülebilir en küçük etki) ZORUNLU.** `|fark| < MDE` ise
  hüküm *"etkisiz"* değil **"göremiyoruz"**

**Önceden sabit karşılaştırma sayısı: 3** (üç varyant × `A_funding` × `R`).
Diğer her şey (`net%` · `B_ma50ucuz` · 2R hedef · rejim kırılımı) **ikincildir**.

## 9 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

| # | ölçüt | eşik |
|---|---|---|
| **K1** 🔴 **BİRİNCİL** | `A_funding`'de bir varyantın `R` farkı | **> 0** · gün-kümeli t ≥ **+2,0** · permütasyon **p ≤ 0,05** |
| **K2** | kazanan varyant, **iki kronolojik yarıda da** aynı işaret | evet |
| **K3** | **yalıtık hücre yasağı** — kazananın merdivendeki **komşusu** aynı işarette | evet |
| **K4** | üç rejimin (BOĞA/NÖTR/AYI) hiçbirinde ters işaret | evet |

**GEÇTİ** = K1+K2+K3+K4 · **ZAYIF** = K1+K2 var, K3 ya da K4 düştü · aksi **DÜŞTÜ**.

## 10 · ASİMETRİ SORUSU — ayrı, ve yorum kuralı ŞİMDİ yazılıyor

Aynı tarama `B_ma50ucuz`'da da koşturulur. Kayıtlı iddia: A+B'nin stopu kapısına
**uymuyor**, MA50+ucuz'unki **uyuyor**.

**Yorum kuralı (önceden sabit):**
- İki kapının genişlik profili **niteliksel olarak aynıysa** → asimetri iddiası
  **desteklenmedi**; %65 vs %0 farkı büyük olasılıkla **ufuk eşleşmemesinden**
- Profiller **ayrışıyorsa** → asimetri gerçek; A+B'ye özel stop tartışılabilir

Bu bir geçme ölçütü **değil**, ilan edilmiş bir yorum kuralıdır.

## 11 · UYGULAMA — ne olursa ne yapılacak

| sonuç | eylem |
|---|---|
| **GEÇTİ** | **kod DEĞİŞMEZ** — kullanıcıya öneri sunulur. Kapı değişikliğidir: yeni ölçüm penceresi + `[DEĞİŞTİ tarih]` + config'te geri alma anahtarı gerekir (D/8, D/9) |
| **ZAYIF** | kod değişmez; aday olarak kütüğe yazılır, ikinci pencere bekler |
| **DÜŞTÜ** | kod değişmez. **%65 kaydına şerh düşülür** ve *"stop genişliği bu evrende çözüm değil"* yazılır |

🔴 Bu ölçüm **hiçbir durumda kendiliğinden kod değiştirmez** — kullanıcı
*"bota direk ekleme, sor önce"* dedi ve bu kural yürürlükte.

## 12 · SINIRLAR — şimdiden yazılıyor

- **`oi24` bacağı yok** (bölüm 3) — ölçülen A+B değil, **funding bacağı**
- **Likidasyon modellenmiyor.** `4.0x` kolu, yüksek ATR'li sembollerde gerçek
  botta `kaldirac_guvenlik_kirp` tarafından **reddedilebilir** — bu ölçümde
  reddedilmiyor. Yani `4.0x` kolu gerçekte **erişilemez** olabilir
- **Portföy aşaması yok** — slot rekabeti, eşzamanlı maruziyet, düşüş freni yok
- **Kısmi kâr (%40 hedef) modellenmiyor** — `ileri_rr` mekaniği gibi, sade
  stop/hedef. Canlı A+B'de kısmi kâr açık; bu, kolların **hepsini aynı yönde**
  etkiler ama mutlak seviyeyi kaydırır
- `SEYRELT=24` faz kilitler — bu soruda saat boyutu yok, zararsız

## 13 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in (`R` üzerinde) geçmesine ~%15 veriyorum.** Üç gerekçe:

1. `asgari_stop_pct`'in kod yorumu şunu **zaten ölçmüş**: *"STOPU GENİŞLETMEK İŞE
   YARAMIYOR — isabet %11,0→%13,6 ama başabaş %12,1→%16,7; başabaş isabetten hızlı
   büyüyor."* (577 canlı-kapı olayı, tüm kapılar birlikte.)
2. `R`'nin paydası genişlikle **doğrusal** büyür. `2.5x` kolunun `A`'yı geçmesi
   için `net%`'i kabaca **aynı oranda** artırması gerekir — yüksek bir bar.
3. `stop_mu_sure_mu` bu evrenin komşusunda stopun **yardım ettiğini** buldu.

**`net%` üzerinde (ikincil) ~%50** — orada genişlik cezası yok.

**Yönlü tahminler (tutmazsa aynen raporlanır):**

1. Stop-olma oranı genişlikle **monoton düşecek**, ortalama tutma süresi yükselecek.
2. `net%`'te geniş kollar `A`'yı **geçecek** (`A_funding`'de).
3. `R`'de geniş kollar `A`'ya **kaybedecek** — genişlik cezası yol kazancını yer.
4. 🔴 **Asimetri TEKRARLANMAYACAK** — iki kapı aynı profili verecek, çünkü
   %65 vs %0 farkı **ufuk eşleşmemesinden** doğdu, kapı özelliğinden değil.

## 14 · Dokunulmayanlar

Bot · `testbot_state.json` · defterler · config · zamanlanmış görevler: **hiçbiri.**
Ayrı süreç, salt-okuma, ücretli çağrı yok.
Betik: `scratchpad/stop_mesafesi.py` (**bu commit'ten SONRA** yazılır).
