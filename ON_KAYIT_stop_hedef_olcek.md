# ÖN-KAYIT — STOP ve HEDEF, OYNAKLIK ÖLÇEĞİNE UYUYOR MU?

**Yazılma tarihi:** 2026-09-06 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-06): *"bot %13 yükselmiş coine long açıyor, bu normal
mi? … günlük veri alıp anlık poz açıyoruz"* → *"bu fikirleri test et, sonra bota
dokunuruz"*
**Betik:** `scratchpad/stop_olcek/01_olcum.py`

---

## 1 · GÖZLEM — bu ön-kaydı doğuran teşhis

ORCA (botun ilk işlemi, `−153,60 $`, `r −1,02`, **36 dakika**):

```
onceki 24 saat oynaklik : %0,39/saat
son 6 saat (pump ici)   : %2,28/saat        <- 5,8 KAT
konan stop              : %2,66
  -> sakin oynaklikla stopun karakteristik omru  45,4 saat
  -> pump oynakligiyla                            1,4 saat
  -> GERCEK                                       0,6 saat
```

**Hipotez:** giriş sinyali oynaklık **patladığı için** ateşleniyor
(`vol_x` · `last1` · `stage=BASLIYOR`), stop ise **patlamadan önceki**
oynaklığa göre boyutlanıyor (`ATR14`). İkisi aynı olayın ters yüzü.

Kod bunu destekliyor: [olcucu.py:150](olcucu.py#L150) stopu üç adayın **en yakını**
olarak seçer — yapısal destek · 10-bar dibi · **`1,5 × ATR14` yedeği**. ORCA'da
`%2,66 ≈ 1,5 × %1,77` → **ATR yedeği bağlamış**.

## 2 · 🔴 KARŞISINDAKİ KANIT — önce bu yazılıyor

```
CIKIS tarafinda 30 VARYANT denendi, 1'i gecti.
Gecen tek varyant cikisi GEVSETIYORDU (sabit %10 hedef).
Sikilastiran 29 varyantin 29'u da KALDI.
```

Ayrıca [testbot.py:1207](testbot.py#L1207) **stopu genişletmeyi zaten ölçmüş**:
*"isabet %11,0 → %13,6 ama başabaş %12,1 → %16,7; başabaş isabetten hızlı
büyüyor → kovalama tuzağının stop tarafı. O yüzden ELE."*

⚠️ **Yani "stopu genişlet" fikri bu projede bir kez ölçüldü ve düştü.**
Bu ön-kayıt onu **aynen tekrarlamıyor**: oradaki genişletme *sabit bir çarpanla,
her işlemde* yapılmıştı. Buradaki öneri **koşullu** — stop yalnız oynaklığın
**taze** ölçüsüne göre yeniden boyutlanıyor; sakin coinlerde **daralır**,
pump içindekilerde genişler. Fark budur ve hüküm bu farkı sınayacaktır.

## 3 · KOLLAR — hepsi AYNI GİRİŞLERDE, hiçbiri STOPSUZ

🔴 `CLAUDE.md`: *"sabit ufuk + stopsuz kol = teşhis aracı bile değil"*.
Tasarım **(b) eşleşmiş giriş, farklı genişlik** desenidir (`stop_mesafesi.py`).

| kol | stop | hedef | yön |
|---|---|---|---|
| **A0** MEVCUT | `olcucu` üçlü mantık, **ATR14** | sabit **%10** | — |
| **A1** TAZE ATR | aynı mantık, **ATR3** | sabit %10 | pump'ta **genişler**, sakinde **daralır** |
| **A2** ÖLÇEKLİ HEDEF | ATR14 (A0 ile aynı) | **`m × ATR`** | sabit değil, oynaklıkla ölçekli |

`m` **koşumdan önce** şöyle sabitlenir: `m = 0,10 / medyan(ATR14/fiyat)`
— yani **medyan işlemde hedef tam %10 olur**. Bu bir seviye değişikliği değil,
**yeniden dağıtımdır**; "en iyi m'yi ara" YAPILMAZ.

⚠️ Üçüncü fikir (**`chg24`'e koşullu hedef**) bu ön-kayıta **ALINMADI**.
Gerekçe: eşiği icat etmek gerekiyordu ve *"tabloya bakıp seçmek"* bu projede
reddedilmiş davranıştır. Ayrı ve daha iyi gerekçelendirilmiş bir ön-kayıt ister.

## 4 · MEKANİK — botun kendi kodu kullanılır

```
GIRISLER : radar_archive -> NOTR-LONG zinciri (testbot.karar_yon, rejim ZORLA NOTR)
           IKI SURUM raporlanir: taker kapisi ACIK ve KAPALI
STOP     : olcucu'nun KENDI fonksiyonlari (yeniden yazilmaz) — yalniz ATR periyodu degisir
GIRIS AN : karar barinin KAPANISI (ONAY_BEKLE bir bar sonra)
TETIK    : FITIL (bar low <= stop -> stop; bar high >= hedef -> hedef)
CAKISMA  : ayni barda ikisi de -> STOP sayilir (muhafazakar, botun varsayimi)
ZAMAN    : 48 saat -> kapanista cik
MALIYET  : %0,09 gidis-donus
BOYUT    : hedef risk SABIT -> notional = risk / stop_frac  (dolar riski her kolda AYNI)
```

🔑 **Sabit dolar riski kritiktir:** A1 stopu genişletince pozisyon **küçülür**.
Yoksa "geniş stop = büyük zarar" diye sahte bir sonuç çıkardı.

## 5 · ÖLÇÜT — birincil metrik ve eşikler

**Birincil metrik: işlem başına net R** (`sonuç / risk`), A0'a göre **eşleşmiş fark**.

Aynı girişler kullanıldığı için test **eşleşmiştir** → fark istatistiği geçerli
(`CLAUDE.md`'nin *"alt kümede t tanımsız"* uyarısı buraya **uygulanmaz**).

| # | ölçüt | eşik |
|---|---|---|
| **S1** | eşleşmiş fark (A1−A0 veya A2−A0), **gün-kümeli t** | **≥ +2,5** |
| **S2** | farkın büyüklüğü **MDE'nin üstünde** (eşleşmiş farklardan hesaplanır) | evet |
| **S3** | pencere iki yarıya bölünür, **işaret aynı** | evet |
| **S4** | yoğunlaşma: **en iyi 2 gün ve en iyi 5 işlem** çıkarılınca hâlâ artı | evet |
| **S5** | `taker` açık ve kapalı **iki giriş setinde de** aynı işaret | evet |

```
GECTI    = S1..S5 hepsi
DUSTU    = S1 veya S2 duser
BELIRSIZ = S1+S2 gecer, biri duser -> A0 KALIR (supheda DAIMA statuko)
```

🔴 **S1 eşiği 2,5** (2,0 değil): iki kol × iki giriş seti = 4 karşılaştırma.
🔴 **MDE, farkların kendi dağılımından ÖLÇÜLÜR, önceden sayı yazılmaz.**
Bugün iki ön-kayıt bu hatayı yaptı (`taker`, `funding/L-S`) — üçüncüsü yapmayacak.

## 6 · RAPORLANACAK TEŞHİSLER (ölçüt değil, açıklayıcı)

- Her kolda: stop mesafesi medyanı · **stop olma oranı** · hedef isabeti ·
  medyan tutma süresi
- `CLAUDE.md`'nin zorunlu sınaması: kollar **stop genişliğinde ve stop olma
  oranında ayrışıyor mu** — evet, çünkü tasarım gereği ayrışıyorlar; bu yüzden
  metrik **R** (riske normalize) seçildi, ham % değil
- ⚠️ **Ortak payda tuzağı** (`CLAUDE.md`): `R = net/risk`. `risk ~ R`
  korelasyonu **mekaniktir**, dayanak yapılmaz. Yalnız **ΣR ve ortalama R**
  raporlanır, `risk` ile korelasyonu **DEĞİL**.

## 7 · NE YAPILMAZ

- Bota, state'e, defterlere, görevlere **dokunulmaz** (salt-okuma)
- `m` için **arama yapılmaz** — formülle bir kez sabitlenir
- En iyi hücre **seçilmez**; ölçüt sonuç görüldükten sonra **değişmez**
- ATR periyodu için **tarama yapılmaz** — yalnız `3` denenir (`14`'e karşı)
- `klines_1h_uzun` **EZİLMEZ** (salt okunur)
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 8 · GEÇERSE NE OLUR

🔴 Geçen kol **doğrudan bota konmaz**. Sıra:
1. Bu ön-kayıt = **ham mekanik** ölçümü (portföy yok, slot yok, fonlama yok)
2. Geçerse **portföy simülasyonu** (8 slot · düşüş freni · fonlama) ayrı koşar
3. Ancak o da geçerse kapı önerisi + `notrlong`'a uygulama + **pencere sıfırlama**

## 9 · BEKLENTİM — koşumdan önce, olasılıkla

| kol | geçme olasılığım | gerekçe |
|---|---|---|
| **A1** taze ATR | **%30** | teşhis güçlü ve "genişletme" ölçümünden farklı (koşullu); ama 29/30 duvarı ve stop-genişletme ölçümünün kendisi aleyhte |
| **A2** ölçekli hedef | **%20** | sabit %10 ölçülmüş tepe noktasıydı; yeniden dağıtım onu bozabilir |

**En az birinin geçmesine %40.** Taban oranım düşük: bu projede çıkış tarafında
30 denemede 1 geçti, yani **%3,3**. %40 demem, teşhisin (5,8 kat oynaklık
sıçraması) spesifik ve ölçülmüş olmasından; ama bu bir *mekanizma* argümanı ve
bu proje mekanizma argümanlarının defalarca çürüdüğünü kaydetti.
