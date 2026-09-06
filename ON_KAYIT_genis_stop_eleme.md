# ÖN-KAYIT — ÇOK GENİŞ STOPLU GİRİŞLER ELENMELİ Mİ?

**Yazılma tarihi:** 2026-09-06 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"UAI eksiye düştü, bu düşüş öngörülebilir miydi"* → *"yap"*
**Betik:** `scratchpad/genis_stop/01_olcum.py`

---

## 1 · NEDEN — UAI'nin künyesi

```
R:R 0,97 · BASABAS %50,7 · populasyon isabeti ~%25
stop %10,28 = 1,5 x ATR(%6,84) · chg24 +26,86%
```

Fiyat hareketi `−%2,37` = **0,35 ATR** (sıradan gürültü), ama **kurulum**
girişte biliniyordu.

Ve bugünkü ön-kayıtlı dilim tablosunda (`ON_KAYIT_stop_genislik_yonu.md`)
geniş dilim, **iki yarıda da aynı işareti veren TEK hücreydi**:

```
hucre        KESIF                    HOLDOUT              ayni isaret
TUMU     -0,1577 (isabet %23,1)   +0,0868 (%27,6)            HAYIR
stop>%8  -0,0709 (%46,3)          -0,0778 (%45,2)            EVET
stop>%6  -0,0719 (%41,7)          -0,1625 (%36,6)            EVET
```

Mekanizma aritmetikten: isabet **%45-46**, `%10` stopla başabaş **%50** →
sık kazanıyor, **yetecek kadar sık değil**.

## 2 · 🔴 KARŞISINDAKİ KANIT — önce yazılıyor

**Aynı gün iki şey bu hipoteze karşı çıkıyor:**

**(a)** `asgari_stop` ölçümü ([testbot.py:1205](testbot.py#L1205), **577 olay**,
bugünkü veriden **bağımsız**) TAM TERSİNİ söylüyor:

```
stop banti     gozlenen isabet   basabas(%10)   fark
<%1,92              %10,3           %12,7       -2,4
%1,92-3,40          %20,1           %21,0       -0,9
%3,40-5,51          %33,3           %30,8       +2,5
>%5,51              %56,2           %42,0      +14,2   <- GENIS EN IYI
```

**(b)** Bugün `stop <= %3` tavanını ölçtüm ve **iki yarıda zıt işaret** verdi.

⚠️ **İki kaynak çelişiyor** ve bu ön-kayıt o çelişkiyi çözmek için var.

## 3 · 🔴 EŞİK NASIL BELİRLENECEK — koşumdan önce sabit

`X` **tablodan seçilmez**. Yordam:

```
1) YALNIZ KESIF yarisinda, ilan edilmis izgarada tara: X in {5, 6, 7, 8, 9, 10}
2) Kosul: stop_pct > X hucresinde  ort R < 0  VE  N >= 60
3) Kosulu saglayan EN KUCUK X secilir  (en genis eleme -> en muhafazakar)
4) O TEK X holdout'ta sinanir. Ikinci aday holdout'a SOKULMAZ.
```

Kosulu sağlayan `X` yoksa ölçüm **"aday yok"** ile biter.

## 4 · VERİ

```
POPULASYON : radar_archive · score>=30 · 4sa cooldown · A0 mekanigi
N          : 2.082 giris · 72 gun
KESIF      : ilk %60 gun (1.006)   HOLDOUT : son %40 gun (1.076)
```

## 5 · ÖLÇÜTLER — sonuç görüldükten sonra değişmez

| # | ölçüt | eşik |
|---|---|---|
| **W1** | HOLDOUT'ta `stop_pct > X` hücresinin ortalama `R`'si | **< 0** |
| **W2** | hücre vs geri kalan, **gün-kümeli t** | **≤ −2,0** |
| **W3** | farkın büyüklüğü **MDE'nin üstünde** | evet |
| **W4** | HOLDOUT'ta hücre `N` | **≥ 40** |
| **W5** | hücre çıkarılınca kalan popülasyonun ort `R`'si, tümünden **yüksek** | evet |

```
ELEME HAKLI   = W1..W5 hepsi
HAKLI DEGIL   = W1 veya W2 duser
GOREMIYORUZ   = W1+W2 gecer ama W3 duser
```

## 6 · NEGATİF KONTROL

`stop_pct` **gün içinde permüte** edilir ve **aynı boru hattından** geçirilir
(keşifte eşik seçimi + holdout sınaması). Sahte değişken de bir "eleme"
buluyorsa, yordam **kendi başına** eleme üretiyor demektir ve hüküm yazılmaz.

🔴 Bugün `giris_arama`'da negatif kontrolü **eksik** kurmuştum (2 hücre vs 39);
burada **birebir aynı boru hattı** koşuyor.

## 7 · 🔴 GEÇSE BİLE NE OLMADIĞI

Bu bir **kayıp önleme** kuralıdır, **kenar değil**. Bugün ölçüldü: geniş
stopluları çıkarmak **kalan kısmı tutarlı yapmıyor** — kalan hâlâ rejimle
işaret değiştiriyor (`stop <= %5`: keşif `−0,156` / holdout `+0,155`).

**Beklenen fayda:** tutarlı biçimde negatif olan bir dilimi kesmek.
**Beklenmeyen:** botun alfasını pozitife çevirmek (`alfa −0,108`, `t −2,01`).

## 8 · GEÇERSE NE OLUR

1. Bu ölçüm **ham mekanik** (portföy yok, slot yok, fonlama yok)
2. Geçerse **portföy simülasyonu** ayrı koşar — ⚠️ eleme, işlem sayısını
   **azaltır**; `notrlong` daha bu sabah "poz açmıyor" diye açılmıştı,
   pencere hızı yeniden kontrol edilmeli
3. Ancak o da geçerse `notrlong`'a **giriş kapısı** + pencere sıfırlama

## 9 · NE YAPILMAZ

- Bota, state'e, defterlere **dokunulmaz** (salt-okuma)
- Eşik holdout'ta **aranmaz**; keşifte seçilir, holdout'ta yalnız sınanır
- İkinci eşik holdout'a **sokulmaz**
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 10 · BEKLENTİM — koşumdan önce, olasılıkla

**%40.** Bugünün en yüksek beklentisi, çünkü hücre **iki yarıda da aynı
işareti veren tek hücre** ve mekanizma aritmetikten geliyor (isabet < başabaş).

Düşük tutmamın sebebi: (a) `asgari_stop` ölçümü **tam tersini** söylüyor ve
o ölçüm bu veriden bağımsız; (b) eşiği UAI kaybettikten **sonra** aramaya
başladım — keşif/holdout ayrımı bunu kısmen kapatır ama **tamamen değil**;
(c) bugün dokuz ön-kayıt yazıldı, dokuzu da düştü.
