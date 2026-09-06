# ÖN-KAYIT — SIKIŞMA → KIRILIM: OYNAKLIĞI UCUZKEN AL

**Yazılma tarihi:** 2026-09-06 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-06): *"hacim bu kadar yükselmeden girsek, hacim
yükselir, oi yönü gösterir, beklemeye alır bot coini hangi yöne gidiyorsa ona
göre poz açar"* → *"tamam yap"*
**Betik:** `scratchpad/sikisma/01_olcum.py`

---

## 1 · FİKRİN HANGİ PARÇASI ÖLÇÜLÜYOR

Kullanıcının önerisi üç parçaya ayrıldı:

| parça | durum |
|---|---|
| *"hacim yükselmeden, OI birikirken yakala"* | **zaten botta var** — `stage=HAZIRLANIYOR` = `comp<0.65 ∧ \|last3\|<4 ∧ oi24>8` ([radar.py:153](radar.py#L153)), +8 sıralama bonusu |
| *"OI yönü gösterir"* | 🔴 **ölçüldü ve çürüdü** — `d_oi_3s` ayırdı (t=−3,27) ama *"fiyat hareketinin başka bir ifadesi"* çıktı (`olcumler.md:4816`, kuralın **5.** doğrulanışı). Ayrıca OI **büyüklük** ölçer, **taraf** ölçmez |
| **"beklemeye alır, hangi yöne giderse ona göre açar"** | ⭐ **ÖLÇÜLEN BU** — yön OI'dan değil **KIRILIMDAN** gelir, 2. satırdaki tuzağı atlar |

## 2 · ASIL İDDİA: SİNYAL DEĞİL, GEOMETRİ

Bugün ölçüldü (`olcumler.md`, stop/hedef ölçeği):

```
BOTUN BUGUNKU HALI   stop %3,58 · hedef %10 -> R 2,79 -> basabas %26,4 · GOZLENEN %25,4
```

Bot **başabaşın altında**. Sıkışmada girmek stopu daraltır:

```
SIKISMA KIRILIMI     stop ~%1,5-2 · hedef %10 -> R 5-6,7 -> basabas %13-16
```

**Başabaş yarıya iner.** İddia budur: daha iyi sinyal değil, **daha ucuz oynaklık**.

## 3 · 🔴 KARŞISINDAKİ KANIT — önce yazılıyor

**(a) Dar stop ZATEN ölçüldü ve düştü** ([testbot.py:1205](testbot.py#L1205), 577 canlı olay):

```
stop <%1,92 -> isabet %10,3   ·   o geometrinin basabasi %16,1   -> 5,8 PUAN EKSIK
```

**(b)** Bugünkü 39 hücrelik aramada `comp ≤ 0,7` → **−0,2648 R** (en kötü beşte).
**(c)** `stage == HAZIRLANIYOR` → **−0,3300 R** (N=84, keşif yarısı).

⚠️ Üçü de *"sıkışmışken **GİR**"*i ölçüyor. Bu ön-kayıt *"sıkışmışken **İZLE**,
kırılımda gir"*i ölçüyor. **Aynı şey değil** — ama üçü de aynı yöne bakıyor ve
bu, beklentiyi düşük tutmanın sebebidir.

## 4 · GEÇME BARI — kullanıcıya koşumdan ÖNCE söylendi

> *"Sıkışma-kırılımı girişleri, kendi geometrisinin başabaşının üstünde isabet
> yapmalı. Mevcut dar-stop girişleri %10,3 yapıyor, gereken ~%16."*

Bu cümle **koşumdan önce** yazıldı ve aşağıda `B1` olarak sabitlendi.

## 5 · TANIM — koşumdan önce sabit

```
t0        : radar_archive kaydi, SIKISMA kosulu saglaniyor
            BIRINCIL : stage == HAZIRLANIYOR   (botun KENDI tanimi)
            IKINCIL  : comp < 0.65 tek basina  (guc icin; botun tanimi DEGIL)
COOLDOWN  : sembol basina 4 saat (botun kurali) -> sahte tekrar yok
KOVA      : t0'dan ONCEKI 10 KAPANMIS bar -> tepe = max(h), dip = min(l)
BEKLEME   : t0'dan sonra en cok 12 SAAT
KIRILIM   : ilk kapanmis bar high >= tepe  -> LONG
            ilk kapanmis bar low  <= dip   -> SHORT
            ayni barda ikisi -> OLAY ATILIR (yon belirsiz)
            12 saatte kirilim yok -> OLAY ATILIR (kac tanesi RAPORLANIR)
GIRIS     : kirilim SEVIYESINDE (tepe ya da dip) + maliyet
STOP      : kovanin OBUR tarafi
HEDEF     : sabit %10 (BIRINCIL, botla ayni) · m x kova genisligi (IKINCIL)
ZAMAN     : girisin 48 saati
MALIYET   : %0,09 gidis-donus
```

**N (koşumdan önce ölçüldü):**

```
HAZIRLANIYOR (birincil) :   417 olay ·  70 gun · 174 sembol
comp<0.65    (ikincil)  : 2.583 olay ·  73 gun · 360 sembol
```

🔴 **GÜÇ SINIRI ÖNCEDEN İLAN EDİLİYOR:** birincil kolda N=417 ve kırılmayanlar
düşünce daha az kalacak. **Bu ölçümde NULL SONUÇ, YOKLUĞUN KANITI DEĞİLDİR.**
Yalnız büyük bir etki görülebilir. MDE her kolda **hesaplanıp raporlanacak** ve
etki tabanı ondan türetilecek — bugün iki ön-kayıt bu hatayı yaptı, üçüncüsü
yapmayacak.

## 6 · KONTROL GRUPLARI — ikisi birden

| | ne |
|---|---|
| **C1 taban** | aynı günlerdeki botun mevcut popülasyonu (A0 mekaniği) — **seviye** kıyası |
| **C2 şans** | 🔴 **eşleştirilmiş rastgele an**: aynı sembol, aynı gün, **rastgele saat**, aynı kova/stop/hedef kurgusu — `geri_verme.py` deseni |

`C2` belirleyicidir: kırılımın kendisi mi iş görüyor, yoksa o sembol-gün zaten
oynak mıydı?

## 7 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değişmez

| # | ölçüt | eşik |
|---|---|---|
| **B1** ⭐ | isabet, **kendi geometrisinin** başabaşının üstünde | evet |
| **B2** | ortalama net R | **> 0** |
| **B3** | `C2` (eşleştirilmiş rastgele) farkı, **gün-kümeli t** | **≥ +2,0** |
| **B4** | farkın büyüklüğü **MDE'nin üstünde** (koldan hesaplanır) | evet |
| **B5** | iki zaman yarısında **aynı işaret** | evet |
| **B6** | yoğunlaşma: en iyi 2 gün + 5 işlem çıkınca hâlâ `B2` | evet |

```
GECTI    = B1..B6 hepsi (BIRINCIL kolda)
DUSTU    = B1 veya B2 duser
GOREMIYORUZ = B1+B2 gecer ama B4 duser (guc yetmedi)
```

**Birincil sonuç TEKtir:** `HAZIRLANIYOR` · iki yön birlikte · sabit %10 hedef.
İkincil (hüküm kurmaz): `comp<0.65` kolu · yön ayrı ayrı · `m × kova` hedefi.

```
COKLU KARSILASTIRMA: 2 tanim x 3 yon-kumesi x 2 hedef = 12. BIRINCIL 1.
```

## 8 · NE YAPILMAZ

- Bota, state'e, defterlere, görevlere **dokunulmaz** (salt-okuma)
- Kova uzunluğu (10 bar), bekleme (12 sa) ve hedef (%10) **ARANMAZ** —
  üçü de mevcut koddan alındı (`olcucu_nbar_stop` · yarım gün · `SABIT_HEDEF_PCT`)
- En iyi hücre **seçilmez**; ölçüt sonuç görüldükten sonra **değişmez**
- `klines_1h_uzun` **EZİLMEZ**
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 9 · GEÇERSE NE OLUR

🔴 Doğrudan bota **konmaz**. Bu, **yeni bir giriş mantığıdır** — mevcut
`notrlong`'a eklenmez, `defter2`/`defter3` gibi **ayrı bir defterle** canlı
test edilir. Gerekçe `CLAUDE.md`: bir değişiklik hangi işlemin açılacağını
değiştiriyorsa pencere sıfırlanır; bu değişiklik **botun tamamını** değiştirir.

## 10 · BEKLENTİM — koşumdan önce, olasılıkla

**%20.** Bugünün diğer fikirlerine verdiğimden yüksek, çünkü bu **sinyal
aramıyor, geometri düzeltiyor** — ve bugün ölçülen kusur tam olarak geometriydi.

Düşük tutmamın sebepleri: (a) dar stop zaten ölçülüp düştü (%10,3 vs %16,1);
(b) sıkışma hücresi bugün en kötülerden çıktı; (c) sıkışmadan kırılım =
**momentum takibi**, bu projenin kimliği ise ortalamaya dönüş; (d) giriş
tarafında bugüne kadar aranan her şey boş çıktı.

⚠️ Ve şu şimdiden yazılıyor: **N=417 ile "geçti" demek bile zayıf bir hükümdür.**
Geçerse sonuç *"kapı bulundu"* değil, **"ayrı defterle canlı test edilmeye
değer bir aday"** olur.
