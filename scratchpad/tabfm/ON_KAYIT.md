# ÖN-KAYIT — TabFM İNDİKATÖR OLABİLİR Mİ?

**Yazıldı: 2026-08-25, KOŞUMDAN ÖNCE. Ölçütler bundan sonra DEĞİŞTİRİLMEZ.**

Kullanıcı sorusu: *"TabFM'i bir indikatör olarak kullanabilir miyiz?"*

---

## SORU

Bot 20+ alanı **elle konmuş eşiklerle** birleştiriyor (`funding ≤ −0,05`,
`fiyat ≤ $0,07`, `skor ≥ 45`). 2026-08-25 ölçümü botun **tek pozitif
seçicisinin TERS** çalıştığını gösterdi (`skor` → ileri getiri, rho = −0,643,
monotonik azalan; `≥45` bandı en düşük getirili hücre).

Bu, *"bilgi yok"* değil, *"eldeki bilgi yanlış birleştirilmiş olabilir"*
demektir. Tablo modellerinin insanı yenmesi beklenen yer tam burasıdır:
**etkileşim**.

**Hipotez:** TabFM, aday arşivinin girdi alanlarından ham +24s ileri getiriyi,
botun kendi seçicisinden VE en iyi tek alandan **daha iyi sıralar.**

---

## BU ÖLÇÜM NE DEĞİLDİR

🔴 **İndikatör KURMUYORUZ.** Bu bir **tavan ölçümüdür**. Sorusu şu: *darboğaz
bilginin kendisi mi, yoksa kullanımı mı?* Cevap "kullanımı" çıkarsa bile
sonraki adım TabFM'i bota gömmek DEĞİL, bulduğunu **elle yeniden kurmaktır** —
lisans (çıktılar da ticari karara giremez) ve `canliya-gecis-kontrol-listesi`
bunu zorunlu kılıyor.

🔴 **Mekanik YOK.** Stop yok, hedef yok, ücret yok, fonlama yok.
`CLAUDE.md` sırası: **ham getiri → ticaret mekaniği → portföy.** Bu ADIM 1.
Etiket *"kazandı mı"* olsaydı model **bizim stopumuzun hatalarını** öğrenirdi —
`chg24 > 40 LONG` tam böyle gömülmüştü (ham getiride +2,284'tü).

---

## VERİ

```
kaynak   testbot_aday_arsiv.jsonl   22.728 satir · 250 sembol · 21 gun
pencere  2026-08-04 .. 2026-08-25
etiket   HAM +24s getiri, klines_1h_uzun'dan
giris    ts'i takip eden saatin kapanisi     (skor_tahmin.py ile AYNI)
ofset    OFSET = -3   (radar ts YEREL/UTC+3 -> UTC; %100 bar-ici olculdu)
```

`rejim` alanı kullanılabilir: arşiv **08-04**'te başlıyor, alanın tanım
değiştirdiği **2026-07-22**'den sonra. O tuzak bu veriye değmiyor.

### Girdi alanları (23)

`score` · `stage` · `price` · `comp` · `vol_x` · `oi24` · `oi3` · `funding` ·
`pos` · `last1` · `last3` · `chg24` · `dip_yakit` · `ayrisma` · `rel3` ·
`btc_chg3` · `rejim` · `top_ls` · `glob_ls` · `taker` · `smart` ·
`dusuk_float` · `ma50_mesafe`

### DIŞLANANLAR — gerekçesiyle

| alan | neden |
|---|---|
| `karar` | 🔴 **BOTUN KENDİ KARARI** (`VETO:*`, `SHORT/ANINDA`). Modele botun kapısını göstermek olur — "botu geçti" hükmü anlamsızlaşır |
| `sonuc` · `red_kapi` | sonuç alanları, giriş anında yok |
| `kaynak` | sabit (`testbot`), bilgi taşımıyor |
| `float_oran` | %9,3 dolu |
| `mcap` | %0 dolu |
| `ts` · `sym` | kimlik. **Saat türetilmeyecek:** `SEYRELT=24` faz kilidi uyarısı + 21 gün saat sorusuna yetmez |

---

## DOĞRULAMA ŞEMASI — gün-bloklu ileri doğrulama

```
baglam = 1..k gunleri        test = (k+1). gun        k >= 7
```

Test günleri: **8..21 = 14 gün.** Bağlam ile test günü **asla kesişmez.**

🔴 **Bu şart, bağlam-içi öğrenmenin sızıntı biçimidir.** Aynı günden örnek
verilirse ileri doğrulama değildir. Gün-kümeleme bu projenin zorunlu yöntemi.

Model: **TabFM regresyon** checkpoint'i (6,29 GB), ham getiri üzerinde.

---

## ÖLÇÜTLER — HEPSİ geçmeli

Her ölçüt **gün başına** hesaplanır, sonra **günler arası** t. (N=14 gün.)

| # | ölçüt | eşik |
|---|---|---|
| **S1** | TabFM tahmini ↔ gerçek +24s getiri, Spearman rho | **rho > 0 ve t ≥ 2,0** |
| **S2** | TabFM − `score` (işareti **bağlam günlerinden** seçilmiş), eşleşmiş gün farkı | **t ≥ 2,0** |
| **S3** | TabFM − **en iyi tek alan** (alan VE işaret bağlam günlerinden seçilir) | **t ≥ 1,5** |
| **S4** | karıştırıcı: gün × ATR-üçtebirlik hücrelerinde üst yarı − alt yarı | işaret **≥ %60** hücrede pozitif |
| **S5** | dayanıklılık: ilk 7 test günü / son 7 test günü | rho işareti **AYNI** |

### S2 neden böyle yazıldı

`skor`'un rho'su **−0,643**. Ham hâliyle taban almak **sahte kolaylık** olurdu:
TabFM'in −0,643'ü geçmesi bedava. Dürüst taban, bugün **bedavaya elde edilebilir
olan** şeydir: `skor`'un **ters çevrilmiş** hâli. İşaret **bağlam günlerinden**
seçilir, test gününden değil — yoksa sızıntı olur.

### S3 neden daha düşük eşikli

En iyi tek alan **güçlü** bir tabandır ve bu projede çoğu "yeni sinyal" tek
alanın kılık değiştirmiş hâli çıktı. TabFM'in onu geçmesi asıl sınavdır; eşik
1,5 çünkü eşleşmiş fark 14 günle ölçülüyor ve güç düşük.

---

## ÇOKLU KARŞILAŞTIRMA SAYIMI

Bu **1** karşılaştırmadır: tek model · tek etiket · **tek ufuk (+24s)**.

🔴 Ufuk **SABİT**. Koştuktan sonra +6s'e bakıp *"şurada çalıştı"* denmeyecek.
+6s raporlanırsa **İKİNCİL** diye işaretlenir ve **hükümde kullanılmaz.**

Bu, 2026-08-25'in **8.** ölçümüdür; önceki 7'sinin **7'si olumsuz**.

---

## BEKLENTİM — koşumdan önce yazılıyor

**S1'in geçmesini bekliyorum, S3'ün düşmesini bekliyorum.**

Gerekçe: `skor` ters çalıştığı için işareti düzelten herhangi bir şey rho > 0
üretir — S1 ucuz. Ama `CLAUDE.md`'nin *"ölçtüğümüz her şey tek banttan türüyor"*
kuralı doğruysa 23 alan büyük ölçüde **aynı fiyat hareketinin** farklı
ifadeleridir ve etkileşimden kazanılacak yer dardır.

**Yanılırsam bu, projenin 45 gündür cevaplayamadığı soruya ilk pozitif cevabı
olur.** O yüzden koşuluyor.

---

## GEÇMEZSE

TimesFM'e uygulanan kural aynen: **kurulum silinir** (venv + 6,3 GB ağırlık),
ölçüm kaydı ve betikler durur. İndikatör sorusu **kapanır.**

## GEÇERSE — sonraki adım NE DEĞİL

🔴 Bota gömmek **değil.** Sıra şu:
1. Modelin neyi kullandığı çıkarılır (alan önemi / ablasyon)
2. Bulgu **elle** yeniden kurulmaya çalışılır — TabFM'siz
3. Elle kurulan hâli **ayrı bir defterle** ileri zamanda sınanır (`defter3` gibi)

Model kalıcı bileşen değil, **keşif aracıdır.**

---

## SINIRLAR — şimdiden yazılıyor

- **SEÇİLİM ETKİSİ:** `testbot_aday_arsiv` botun zaten yüzeye çıkardığı
  adaylardır, tüm evren değil. Cevaplanan soru: *"botun gördüğü havuz içinde
  sıralama iyileştirilebilir mi?"* — *"piyasada kenar var mı?"* DEĞİL.
- **21 gün, 14 test günü.** Güç düşük. Olumsuz sonuç **zayıf kanıttır**;
  olumlu sonuç **ileri zamanda doğrulama ister.**
- **Rejim:** pencerenin %87'si `NOTR`, %13'ü `BOGA`. Rejim kırılımı
  yapılamayacak kadar dengesiz — denenmeyecek.
- **Donanım:** GPU yok, CPU çıkarımı. Bağlam satır sayısı RAM'e göre
  sınırlanabilir; sınırlanırsa **kaç satır kullanıldığı raporlanır.**
