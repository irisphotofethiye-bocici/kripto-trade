# ÖN-KAYIT — GİRİŞ KAPISI ARAMASI (keşif + ayrık holdout)

**Yazılma tarihi:** 2026-09-06 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-06): *"ara ozaman"*
**Betik:** `scratchpad/giris_arama/01_arama.py`

---

## 1 · NEDEN — bugün ölçülen sayı

`ON_KAYIT_stop_hedef_olcek.md` sonucu (`olcumler.md`):

```
stop %3,52 · hedef %10 -> R 2,84 -> BASABAS isabet %26,0 · GOZLENEN %25,8
stop %3,71 · hedef %10 -> R 2,70 -> BASABAS isabet %27,1 · GOZLENEN %25,3
```

Bot **başabaşın hemen altında**. Çıkış tarafı 32 varyantta 1 geçti; üç yeni
çıkış fikri de bugün düştü. Kalan tek kaldıraç **giriş seçimi**.

**Soru:** botun aday havuzunda, isabeti başabaşın **üstüne** çıkaran bir alt
küme var mı?

## 2 · 🔴 BU BİR ARAMADIR — en tehlikeli ölçüm türü

`CLAUDE.md`: *"En iyi hücre seçilmez. Tabloya bakıp en yüksek sayıyı kural
yapmak bu projede **reddedilmiş** bir davranıştır."* ve *"Çok sütun + az satır =
sahte bulgu garantisi."*

Bu ön-kayıt o yasağı **kaldırmaz**; aramayı **ayrık bir holdout'la** güvenli
hâle getirir. Keşifte en iyi hücre seçilir — ama o hücre **hiç görülmemiş**
bir zaman diliminde tek seferlik sınanır ve hüküm **yalnız oradan** çıkar.

## 3 · EVREN — koşumdan önce sabit

```
KAYNAK   : radar_archive.jsonl
SUZGEC   : score >= 30  (botun kendi havuz kriteri) + fiyat var
COOLDOWN : sembol basina 4 saat (botun kendi kurali) -> sahte tekrar YOK
N        : 2.811 giris · 73 gun            <- KOSUMDAN ONCE OLCULDU
MEKANIK  : A0 aynen — olcucu uclu stop (ATR14) · sabit %10 hedef ·
           48s zaman stopu · fitil tetikli · ayni barda ikisi -> STOP ·
           maliyet %0,09 · asgari_stop %2 (gecmeyen giris ELENIR)
```

## 4 · 🔴 BÖLME — koşumdan önce ilan ediliyor

```
KESIF    : ilk %60 GUN   (2026-06-24'ten baslayarak 43-44 gun)
HOLDOUT  : son %40 GUN
```

**Holdout, aday seçilene kadar HİÇ AÇILMAZ.** Betik keşif tablosunu basar,
adayı seçer, **sonra** holdout'u okur. Tek geçiş.

## 5 · ARAMA UZAYI — koşumdan önce listelenmiş

**Sürekli değişkenler** (arşivde %100 dolu): `score` · `comp` · `vol_x` ·
`oi24` · `oi3` · `funding` · `pos` · `last1` · `last3` · `log10(price)` ·
`mcap` · `float_oran` · `btc_chg24` · `btc_chg3` · `rel3` → **15**

**Kategorik:** `stage` (3 değer) · `dusuk_float` · `erken` · `ayrisma` ·
`dip_yakit` → **5**

**Kısıt (kiraz toplamayı engeller):** sürekli değişkenlerde yalnız
**beşli dilimin EN ÜST ve EN ALT bandı** aday olabilir — orta hücreler
**aday değildir**. Kategoriklerde her düzey aday.

```
ARANAN HUCRE SAYISI: 15 x 2 + (3 + 2 + 2 + 2 + 2) = 30 + 11 = 41
```

⚠️ **41 hücre, α=0,05'te ~2 sahte pozitif** demektir. Holdout tam bunun için var.

## 6 · SEÇİM KURALI — koşumdan önce sabit

Keşif yarısında, **N ≥ 100** olan hücreler arasından **ortalama R'si en yüksek
TEK hücre** seçilir. Beraberlik → N'i büyük olan.

🔴 **Tam bir hücre seçilir. "İki hücreyi birleştir", "eşiği biraz kaydır"
YAPILMAZ.** Seçim otomatiktir; betik seçer, ben seçmem.

## 7 · HOLDOUT ÖLÇÜTLERİ — sonuç görüldükten sonra değişmez

| # | ölçüt | eşik |
|---|---|---|
| **H1** | holdout'ta hücrenin ortalama R'si | **> 0** |
| **H2** | hücre vs **hücre dışı**, gün-kümeli t | **≥ +2,0** |
| **H3** | farkın büyüklüğü **MDE'nin üstünde** (holdout'tan hesaplanır) | evet |
| **H4** | hücrenin isabet oranı, **kendi geometrisinin** başabaşının üstünde | evet |
| **H5** | holdout'ta N ≥ 60 | evet |

```
KAPI BULUNDU = H1..H5 hepsi
BULUNAMADI   = biri duser
```

🔴 **H4 ayrı yazıldı** çünkü bir hücre isabeti stopu **genişleterek** de
yükseltebilir — o zaman başabaş da yükselir ve kazanç sahtedir. `R` bunu
zaten yakalar; `H4` görünür kılar.

## 8 · NEGATİF KONTROL — aramanın kendi gücünü sınar

Tüm boru hattı, **gün içinde rastgele permüte edilmiş sahte bir değişkenle**
de koşturulur (aynı 41 hücre değil; sahte değişken tek başına 2 hücre).
Sahte değişkenin keşifteki "en iyi" hücresi, gerçek adayınkine **yakınsa**,
arama sahte pozitif üretiyor demektir ve bu **rapora yazılır**.

Ayrıca **keşif → holdout büzülmesi** raporlanır: seçilen hücrenin keşifteki
etkisi ile holdouttaki etkisi. Büyük büzülme = aramanın gürültü topladığının
doğrudan ölçüsü.

## 9 · NE YAPILMAZ

- Bota, state'e, defterlere, görevlere **dokunulmaz** (salt-okuma)
- Holdout **bir kez** okunur; sonuç görülünce ölçüt/aday **değişmez**
- İkinci bir aday holdout'a **sokulmaz** (o an bu ön-kayıt biter)
- Eşik **kaydırılmaz**, hücre **birleştirilmez**
- Bulunsa bile **doğrudan bota konmaz** — bölüm 11
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 10 · BEKLENTİM — koşumdan önce, olasılıkla

**Bir kapı bulunmasına %20 veriyorum.**

Gerekçe: bu proje giriş tarafında defalarca aradı ve bulduklarının çoğu
(skor · fiyat seviyesi · agresör dengesi · son yeni uç · basis · çapraz borsa ·
OBI · taker · funding/L-S) ya boş çıktı ya karıştırıcıya yenildi. Taban oranım
düşük olmak zorunda.

⚠️ Ve şu şimdiden yazılıyor: **holdout'ta bulunan bir kapı bile, `N≈1.100`
mertebesinde tek bir pencereden gelir.** Hüküm *"kapı bulundu"* değil,
**"holdout'u geçen bir aday var"** olur.

## 11 · BULUNURSA NE OLUR

🔴 Doğrudan bota **konmaz**:
1. Bu ön-kayıt = **ham mekanik** (portföy yok, slot yok, fonlama yok)
2. Geçerse **portföy simülasyonu** (8 slot · düşüş freni · fonlama) ayrı koşar
3. Ancak o da geçerse kapı önerisi + `notrlong`'a uygulama + pencere sıfırlama

**Bulunamazsa:** giriş tarafında bu arşivin verebileceği tükenmiş demektir.
O noktada dürüst seçenek, `notrlong`'u mevcut hâliyle (taker kaldırılmış)
koşturup **ölçüm penceresinin kendisini** hakem yapmaktır.
