# ÖN-KAYIT — ETİKET DÖNMESEYDİ: NOTR'de kalsaydı ne olurdu?

**Yazılma tarihi:** 2026-09-05 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-05): *"bot etiket döndükten sonra açtığı pozları
ya da seçimlerini etiket dönmemiş gibi yapsaydı — yani NOTR çalışmaya devam
etseydi ne olurdu, ve short açmasaydı sadece long."*

---

## 1 · Soruyu doğuran olgu

Bugün ölçüldü (`olcumler.md` → *19-21 AĞUSTOS LONG'LARI*): botun kendi rejim
etiketi **08-21'de** BOĞA'ya döndü; LONG'lar **19-20'de** (etiket hâlâ NOTR
iken) kazandı, **21'inde** (etiket dönünce) kaybetmeye başladı.
Etiket bu dönüşte *"geç kalmadı, ters zamanlandı"*.

## 2 · ✅ YAPILABİLİRLİK ÖNCEDEN DOĞRULANDI

`testbot.karar_yon(rejim_ad, ...)` rejimi **parametre olarak alıyor** →
zorlanabilir. Girdilerin tamamı `testbot_aday_arsiv.jsonl`'de.

**Doğrulama koşturuldu** (`scratchpad/etiket_karsiolgu_dogrulama.py`):

```
karsilastirilan kayit  14.846
ESLESTI                14.679   (%98,9)
SAPTI                     167   (%1,1)  -> HEPSI ayni tip:
                                          "VETO:long_veto -> LONG/ONAY_BEKLE"
```

🔑 **Sapmanın kaynağı teşhis edildi:** arşivde olmayan `para_cikis` bayrağı.
O bayrak yalnız **LONG'u kapatır**. Dolayısıyla yeniden üretimim
**tek yönlü ve bilinen bir yanlılık** taşıyor: gerçekte veto edilmiş
**167 LONG'u açıyor**. Bu, hükümde **aynen** yazılacak.

⚠️ Eşleşme %95'in altında kalsaydı bu ölçüm **koşturulmayacaktı**; eşik
doğrulama betiğinde önceden yazılıydı.

## 3 · KOLLAR — üç tane, önceden sabit

| kol | tanım |
|---|---|
| **A · GERÇEK** | `rejim_ad` = arşivdeki değer (BOĞA) — botun fiilen yaptığı |
| **B · NOTR** | `rejim_ad` = **"NOTR"** zorlanır — *"etiket dönmeseydi"* |
| **C · NOTR-LONG** | B ile aynı, ama **SHORT kararları atılır** — *"short açmasaydı"* |

Üçü de **aynı aday akışını**, **aynı karar fonksiyonunu** (kaynaktan çağrılır),
**aynı mekaniği** ve **aynı slot kuralını** kullanır.

**Pencere:** 2026-08-21 → 09-02 (72s ileri getiri kesmesi).

## 4 · MEKANİK ve SLOT — önceden sabit

Karar → pozisyon dönüşümü botun kendi kısıtlarıyla:

```
maks 8 slot es zamanli · ayni sembolde tekrar YOK (acikken)
4 saat sembol cooldown · giris = kararin ertesi saat barinin acilisi
stop = A-stop · hedef %10 · ufuk 72s · maliyet %0,13 · fonlama DAHIL
asgari_stop %2
```

Fiyat: `klines_1h_uzun` + `taze_1h` (bellekte birleşik).
🔴 **`ONAY_BEKLE` kararları bir tur beklemeden alınır** — gerçek botta bir
sonraki turda teyit gerekiyordu; bu **basitleştirme** ve hükümde yazılır.

## 5 · ÖLÇÜ

| ölçü | rol |
|---|---|
| **toplam net $** | 🔴 **BİRİNCİL** — kullanıcının sorusu *"ne olurdu"*, cevabı dolar |
| işlem başına net% | ikincil |
| gün-kümeli t | her kol için, **ve kollar arası fark için** |

⚠️ Bugün iki kez görüldü: **gün-ortalaması ile işlem-ortalaması ayrışabiliyor.**
Her iki toplama da yazılır; işaretleri ters çıkarsa **kırılgan** işaretlenir.

## 6 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

Birincil karşılaştırma: **B − A** (NOTR'de kalmak daha mı iyiydi).

| # | ölçüt | eşik |
|---|---|---|
| **K1** 🔴 | `B` toplam net $ > `A` toplam net $ | evet |
| **K2** | fark gün-kümeli t ile | **\|t\| ≥ 2,0** |
| **K3** | işaret **iki kronolojik yarıda da** aynı | evet |
| **K4** | `C` (NOTR-LONG) `B`'yi geçiyor mu | **ayrı rapor**, ölçüt DEĞİL |

**GEÇTİ** = K1+K2+K3 · **ZAYIF** = K1+K3, K2 düştü · aksi **DÜŞTÜ**.

🔴 **K4 kasten ölçüt değil.** Bugün `boga_holdout`'ta, bilgisiz kalacağını
öngördüğüm bir alt kümeyi ölçüt yapıp üç ölçütü geçmiş bir hükmü batırdım.
Ders uygulanıyor.

## 7 · 🔴 SINIRLAR — hüküm yazılmadan önce

- **Yol bağımlılığı yeniden üretilemez.** Farklı kararlar farklı slot doluluğu
  → farklı sonraki girişler. Simülasyon bunu **yaklaşık** modeller.
- **`para_cikis` yanlılığı:** +167 LONG (bölüm 2). B ve C kollarını
  **lehte** şişirir; A kolunu da aynı yönde etkiler, ama eşit olmayabilir.
- **`ONAY_BEKLE` basitleştirmesi** (bölüm 4).
- **Kısmi kâr modellenmiyor** · likidasyon yok · portföy freni yok.
- **Tek epizot, 13 gün.**

## 8 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%55 veriyorum.** Gerçek kol (A) o pencerede **−4.748 $**
kaybetti ve LONG'un %47 isabetle sürekli kaybettiği ölçüldü; NOTR kolu daha
seçici (*"sadece stage aktif + smart hizalı"*) olduğu için **daha az işlem**
açar — ve kaybeden bir sistemde az işlem açmak tek başına iyileştirir.

**Yönlü tahminler (tutmazsa aynen raporlanır):**

1. **`B` (NOTR) `A`'dan AZ işlem açacak** — NOTR dalı daha temkinli.
2. **`B` yine de NEGATİF olacak** — kaybın kaynağı yön değil, mekanik
   (bugün beş defterde ölçüldü); rejim etiketini değiştirmek onu düzeltmez.
3. **`C` (NOTR-LONG) `B`'yi GEÇEMEYECEK** — o pencerede SHORT'lar da kaybetti
   ama LONG 228 işlemde −3.931 $ ile daha büyük kaybettirdi.
4. Fark **t ≥ 2,0'a ulaşmayacak** (13 gün, düşük güç) → K2 düşecek.

## 9 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
Salt-okuma, veri indirme yok. `testbot.karar_yon` **çağrılır**, değiştirilmez.
Betik: `scratchpad/etiket_karsiolgu.py` (**bu commit'ten SONRA**).
