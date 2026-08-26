# ÖN-KAYIT — SPOT-PERP BASIS, 2 YIL, ÜÇ REJİM

**Yazıldı 2026-08-26, KOŞUMDAN ÖNCE.** Ölçütler bundan sonra değiştirilmez.

## NEDEN BU ADAY

`CLAUDE.md`: *"Ölçtüğümüz her şey tek banttan türüyor — gerçekten yeni bilgi
bandın dışındadır: emir defteri, **spot-perp basis**, çapraz borsa, pozisyon
kompozisyonu."* Bunlardan `top_ls − glob_ls` denendi (bulgu yok).
**Basis hiç denenmedi.**

Eleme testi koşuldu ve **projenin kayıtlarındaki en temiz farkla geçti**
(`00_yoklama.py`, commit `5bb1824`):

```
basis vs FONLAMA           paylasilan varyans  %3,7    30/30 sembolde |r|<0,7
basis vs son 1/3/24 saat   %1,1 / %1,6 / %3,6
KIYAS, elenen adaylar      d_oi_3s vs fiyat %60  ·  genislik vs BTC %51
```

Fonlama sabit değil (havuz std 0,022 · 1.154 tekil değer) → düşük korelasyon
bedava çıkmıyor.

## VERİ

```
sembol   357   (567 perp'in spotta da islem goreni)
gecmis   ~25 ay saatlik   (perp: klines_1h_uzun · spot: 01_spot_indir.py)
basis    100 x (perp_kapanis - spot_kapanis) / spot_kapanis     ayni UTC saati
etiket   HAM +24s perp getirisi (mekanik YOK, maliyet YOK)
```

⚠️ **KALİBRASYON YAPILDI:** basis 30 sembolün 28'inde sistematik negatif
çıkınca damga kayması şüphelenildi. Ofset taraması `perp[t+0]`'ın std'sini
±1 saatin **onda biri** gösterdi (ETH 0,037 vs 0,55) → damgalar hizalı,
negatif basis **gerçek**.

⚠️ **FAZ KİLİDİ ÖNLENDİ:** `SEYRELT=24` bütün sembolleri aynı UTC saatine
düşürüyor (`CLAUDE.md`). Örnekleme **sembol başına SABİT RASTGELE faz** ile
yapılır (`seed=20260826`).

⚠️ **REJİM YENİDEN ÜRETİLİR.** `radar_archive.rejim` 2026-07-22'de tanım
değiştirdi ve o tarihi aşan kırılımda kullanılamaz. Rejim BTC mumundan
üretilir (`scratchpad/skor_tahmin_rejim.py` → `rejim_serisi()`).

## HİPOTEZ — yön ÖNCEDEN yazılıyor

Pozitif basis = perp spotun üstünde = kaldıraçlı LONG'lar prim ödüyor =
**kalabalık uzun taraf**. Beklenti: kalabalık taraf kaybeder →

```
rho(basis, ileri +24s getiri)  <  0
```

🔴 Tutarlı **pozitif** çıkarsa bu, hipotezin geçmesi DEĞİLDİR; *"ters işaretli
bulgu"* olarak ayrıca kaydedilir (`skor` vakasındaki gibi).

## ÖLÇÜTLER — HEPSİ geçmeli

| # | ölçüt | eşik |
|---|---|---|
| **B1** | gün-içi kesitsel rho(basis, +24s), gün-kümeli | **\|ort rho\| ≥ 0,02** VE **\|t\| ≥ 3,0** |
| **B2** | pencerenin **dört çeyreğinde** işaret aynı | dördü de |
| **B3** | **BOĞA · AYI · NÖTR** ayrı ayrı, işaret aynı | üçü de |
| **B4** | KARIŞTIRICI fonlama: fonlama üçte-birlikleri içinde | üçünde de aynı işaret |
| **B5** | KARIŞTIRICI fiyat: `chg24` üçte-birlikleri içinde | üçünde de aynı işaret |

🔴 **B1'de ETKİ BÜYÜKLÜĞÜ TABANI VAR** (`|rho| ≥ 0,02`). Gerekçe: ~750 gün
kümesiyle **hiçliğe yakın bir etki bile `t > 3` verir.** Yalnız `t`'ye bakmak
bu ölçekte yanıltıcıdır. Bu, projenin *"stop varyansı kırdığı için güven
şişiyor — yön aynı, güven yalan"* dersinin bu ölçüme uyarlanmış hâli.

🔴 **B3 BU ÖLÇÜMÜN ASIL SEBEBİDİR.** Bugüne kadarki her ölçüm **tek rejimde**
koştu ve `CLAUDE.md`'nin en sık tekrar eden uyarısı *"aynı tablo rejim
değişince tersine döndü"*. İki yıl bu uyarıyı **ilk kez sınanabilir** kılıyor.

**GEÇME = B1+B2+B3+B4+B5.**

## ÇOKLU KARŞILAŞTIRMA

**1 sinyal · 1 ufuk (+24s) · 1 etiket = 1 karşılaştırma.** Ufuk SABİT;
koşumdan sonra başka ufka bakılıp *"şurada çalıştı"* denmeyecek. Bakılırsa
İKİNCİL diye işaretlenir ve hükme girmez.

## MALİYET — bu ölçümün DIŞINDA

Etiket ham fiyat. **Fonlama dahil değil.** 2026-08-25 ölçümü fonlamanın 24
saatte ham kenarın büyük kısmını yediğini gösterdi. Yani buradan çıkacak bir
kenar, **ödemeler sonrası ayakta kalmayabilir** — o ayrı bir ölçümün konusudur
(`ham getiri → mekanik → portföy` zincirinin 2. adımı).

## BEKLENTİM

**B4 veya B5'in düşmesini bekliyorum.** Gerekçe: bu projede her aday
karıştırıcı kapısında öldü (agresör dengesi · son yeni uç · d_oi_3s · TabFM).
Ama basis elemeyi **temiz** geçti ve bandın dışında — yani gerçek bir şans var.
Geçerse, bu projede karıştırıcı kapısını geçen **ilk aday** olur ve o zaman
bile hüküm değil, **ileri zamanda sınama** gerekir.
