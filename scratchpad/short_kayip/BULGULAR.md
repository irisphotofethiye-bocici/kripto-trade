# Fark yaratacak veri arayışı — ne bulundu, ne çöktü

**2026-08-20 · salt-okuma · kural önerilmedi, bota dokunulmadı**

## Kısa cevap

**Bir şey bulundu: `top_ls` (top trader'ların long/short oranı).** Bot onu zaten
topluyor ve `smart` etiketi olarak kullanıyor — ama **yön seçmek için**, ve
**hiç ölçülmemiş.** Ölçünce bilgi taşıdığı çıktı.

Diğer altı iz ya çöktü ya bilinen bir şeyin tekrarı çıktı. Hepsi aşağıda.

---

## ❌ BULGU 1 İPTAL — `top_ls` GENİŞ SINAVDA ÇÖKTÜ (2026-08-20, ön-kayıt `E_topls_arsiv.py`)

> **Aşağıdaki bölüm keşif hâliyle duruyor (D/9: silinmez).** 49 günlük arşiv
> sınavında **ön-kayıtlı dört ölçütten geçemedi.** Sonuç en altta, *SINAV SONUCU*
> başlığında.

### (keşif hâli — geçersiz)

`smart` etiketinin kaynağı ([radar.py:72](radar.py#L72)):
```python
smart = "LONG" if top_ls >= 1.2 else ("SHORT" if top_ls <= 0.83 else "NOTR")
```

`top_ls` = **topLongShortPositionRatio** — büyük hesapların long/short oranı.

**72 saatlik ham ileri getiri, aday başına (N=1.312, 11–17 Ağustos):**

```
top_ls dilimi      N     r72 ort     botun etiketi
0,55 - 0,92      131      -9,73      SHORT / NOTR
0,92 - 1,04      131     -15,66      NOTR
1,04 - 1,11      131      -9,40      NOTR
1,11 - 1,22      131     -13,31      NOTR
1,22 - 1,33      131     -18,11      LONG   <-- bot LONG diyor, -%18
1,33 - 1,43      131      -7,84      LONG
1,43 - 1,57      131      +3,95      LONG   <-- isaret burada donuyor
1,57 - 1,80      131      +6,87      LONG
1,80 - 2,41      131      +4,81      LONG
2,43 - 7,38      133      +0,67      LONG
```

**Kontroller — üçü de geçti:**

| kontrol | sonuç |
|---|---|
| gün içi sıra korelasyonu | **7/7 gün pozitif**, ortalama +0,273, **t=+7,07** |
| gün içi etiket karıştırma (NOTR vs diğer) | gerçek −12,81 · sahte −0,26 (sd 1,49) · **p=0,0000** |
| `chg24` sabitlenince | dört kovada da duruyor (−13,6 / −7,3 / −10,6 / −2,2) |
| gün gün kırılım | 7/7 gün negatif, gün-kümeli **t=−6,52** |

**Daha önce ölçülmüş mü:** `olcumler.md` → **yalnız `top_ls − glob_ls` FARKI**
denenmiş, bulgu çıkmamış. **`top_ls`'in kendisi hiç ölçülmemiş.**

### ⚠️ Sınırlar — hüküm yazılamaz

- **Yalnız 7 gün** (11–17 Ağustos), tek piyasa dönemi
- **Aynı bandın içinde** — `CLAUDE.md`: ölçtüğümüz her şey Binance perp'ten türüyor
- Yalnız **radar adayları**, genel evren değil
- Ufuk **72 saat**; botun pozisyonları medyan **~2 saat** yaşıyor
- 🔴 **Eşik taraması YAPILMADI.** "1,43'te dönüyor" bir gözlemdir, **öneri değildir**
- **2 yıllık sınav İMKÂNSIZ** — Binance `futures/data` uçları 30 gün geriye gidiyor.
  Yapılabilecek en geniş sınav: `radar_archive.jsonl` (**8 hafta, ~37.000 olay**)

---

## ✅ BULGU 2 — `chg24` 0–20 bandında LONG tutarlı kaybettiriyor

2 yıllık sınav (565 sembol, 40.000+ gözlem):

```
bant       LONG ay ort    ay-t     pozitif ay
-40..0        -0,112     -0,76       10/25
 0..20        -0,406     -4,11        4/25   <-- en kotu
20..30        -0,030     -0,11        9/23
30..40        +0,104     +0,27        9/14
  >40         +0,372     +0,23       10/21
```

- Üç rejimde de negatif (AYI −0,249 · NOTR −0,491 · **BOĞA −0,824**)
- En büyük ay atılınca **kötüleşiyor** (−0,470)
- **Canlı defterde tekrarlandı:** botun `chg24<20` LONG'ları **6 poz −159,19**,
  `chg24>=20` olanları **8 poz +408,62**

**Botun davranışı:** LONG kararlarının **31'i** bu bantta (22'si 20–40'ta, 4'ü
−40..0'da). Yani LONG akışının yaklaşık **%43'ü** ölçülen en kötü bantta.

---

## ✅ BULGU 3 — Takip eden stop İLK KEZ ölçüldü (30. çıkış varyantı) → KALDI

`olcumler.md`'deki 29 varyantın listesi: 5 çıkış kıyası + 8 oynak hedef +
7 kısmi + 1 başabaş + 8 erken müdahale. **Takip eden stop bunlarda YOK** —
ama bot onu LONG tarafında **zaten kullanıyor** (`SABIT_HEDEF_KAPILARI`
dışındaki her giriş trailing ile çıkıyor).

Ön-kayıtlı sınav (2 yıl, eşleşmiş, aynı girişler/aynı başlangıç stopu):

```
                 islem ort     ay ort     ay-t
sabit hedef %10    -0,076     -0,154     -1,33   (kontrol)
trail 1,0x         -0,118     -0,150     -3,81   (on-kayitli kural)
eslesmis fark      -0,041                +0,04
iki yari           A -0,058 · B -0,024           <-- ikisi de negatif
rejim              AYI +0,18 · NOTR -0,11 · BOGA +0,20  <-- isaret doniyor
```

**Dört ölçütün dördü de düştü.** Çıkış sayacı: **30 varyant, 1'i geçti.**

⚠️ 10 günlük canlı pencerede trailing **+1.620 $ daha iyi** görünüyordu.
2 yıllık veri bunu **tekrarlamadı**. `trail 0,5x` daha iyi göründü ama o bir
**tarama sonucu**, hüküm sayılmaz.

---

## ❌ ÇÖKEN İZLER (bulgular kadar önemli)

| iz | ilk görünüm | çöküş sebebi |
|---|---|---|
| `<-40` LONG (kapitülasyon alımı) | +2,188 · p=0,001 | Yalnız **3 ayda** toplanmış. ≥5 gözlemli 10 ayda **−1,680** |
| `>40` LONG (pump alımı) | +0,372 · p=0,009 | 21 ayda **+0,123 · t=+0,23**; en büyük ay atılınca değişmiyor |
| Aynı sembole tekrar giriş | ONG 7 kez −748 | Ortalama **tersini** söylüyor: tekrar −8,62 vs ilk −24,33. Yoğunlaşma |
| Sabit hedef vs trailing (10 gün) | trailing +1.620 | 2 yıllık sınavda tekrarlanmadı (yukarıda) |
| "Zarar etmeyen kombinasyon" | 27 kural | Karıştırılmış sahte veride de **~26** çıkıyor |

---

## Kullanıcının sorularına doğrudan cevaplar

**"Neden %20 artmış coine long diyor?"**
Çünkü iki eşik farklı yerde: pump kapısı SHORT'u **%20**'de kesiyor, blowoff
LONG'u **%40**'ta kesiyor. Arada **yalnız-LONG** bandı kalıyor.
```
bant       aday   LONG  SHORT
0..20      4491     31    283
20..40     1394     22      0    <-- SHORT yasak, LONG serbest
>40        1179      0      0
```

**"Short kapısı kapanınca neden long arıyor?"**
Aramıyor — dallar ayrı ve yönü `smart` belirliyor. Ama yukarıdaki eşik farkı
yüzünden o bantta **hayatta kalan tek yön LONG**. Sonuç aynı, mekanizma farklı.

**"BTC arttığında short seçimini neye göre yapıyor?"**
Seçim değişmiyor — kapılar (A+B funding / MA50+ucuz) rejimden bağımsız. Değişen
**havuz**: 20 Ağustos'ta adayların %84'ü yükseliyordu, medyan +%13,80.
Aynı kural, farklı girdi.

**"Stop olmadan poz kapatmış mı hiç?"**
```
SHORT: STOP 71 · TP2 29 · ZAMAN_STOP 2 · TP1_KISMI 1
LONG : STOP 14 · TP2 0                    <-- hicbiri hedefe ulasmadi
```
LONG'lar sabit hedef almıyor (trailing), o yüzden TP2 imkânsız. 14'ün 9'u
yine de **kârda** kapandı — trailing kâr kilitliyor.

---

## Sıradaki tek adım (öneri değil, ölçüm)

`top_ls`'i **`radar_archive.jsonl` üzerinde** sına: 8 hafta, ~37.000 olay,
7 gün yerine. Bu, bulgunun tek gerçek sınavı — çünkü 2 yıllık sınav
**imkânsız** (Binance `futures/data` 30 gün geriye gidiyor).

---

## 🔴 SINAV SONUCU — `top_ls` KALDI

**Ön-kayıt** `E_topls_arsiv.py` içinde, koşturulmadan önce yazıldı. Sınav:
`radar_archive.jsonl` · **2026-07-02 … 2026-08-20** · 38.841 kayıt · 394 sembol.
Keşif penceresi (11–17 Ağu) **çıkarılarak** 42 günde birincil hüküm verildi.

```
KESIF DISI 42 gun (N=8.554)
  Olcut 1  gun ici sira korelasyonu  +0,047 · t=+1,39 · 21/39 gun   -> DUSTU (t>2,0 gerekiyordu)
  Olcut 2  A yarisi t=+1,01 · B yarisi t=+0,66                      -> zayif
  Olcut 3  ondalik dilimlerde GRADYAN YOK
           -3,18 -1,62 +0,63 -1,45 -1,62 -2,87 -3,03 -1,63 -1,08 +0,79
           ust tercil -0,98 · alt tercil -1,41 · fark yalniz +0,43   -> DUSTU
```

**Keşifte fark +5,51 idi, sınavda +0,43.**

### 🔴 Daha kötüsü: keşif günlerinin KENDİSİ tekrarlanmadı

```
ayni 7 gun, testbot_aday_arsiv ile  ->  t=+7,07 · 7/7 gun pozitif
ayni 7 gun, radar_archive ile      ->  t=+0,22 · 3/7 gun pozitif
```

**Sebep: farklı popülasyon.** Keşif `testbot_aday_arsiv.jsonl` üzerindeydi —
botun **süzülmüş kısa listesi**. Sınav `radar_archive.jsonl` — radarın **ham
taraması**. Sinyal süzülmüş kümede görünüyor, ham kümede yok.

### Post-hoc kurtarma denemesi de tutmadı

```
kume (42 gun)                    N     gun-t
tumu                          8554     +1,39
score>=40                     1449     +2,04   <-- siniri gecti
score>=45                      870     +0,95   <-- KOMSUSU dustu
stage aktif                    640     +0,05
```

4 dilim denendi, **1'i** sınırı geçti, **komşusu geçemedi.** Bu tam olarak şansın
ürettiği desendir (`CLAUDE.md` → *"en iyi hücre seçilmez"*).

### ⚠️ Arşiv boşluk denetimi (CLAUDE.md şartı)

`radar_bosluk.jsonl` **yok** — mekanizma 08-17'de başladı, o tarihten beri boşluk
kaydedilmemiş. Boşluk arşivin kendi damgalarından türetildi:

```
3.501 ayrik tur damgasi · 88 adet 30 dk'dan uzun bosluk
toplam kayip: 19.266 dk / 70.591 dk  ->  %27,3
en uzunu: 07-20 20:33 -> 07-22 11:54  (39 saat)
```

**%27,3 kayıp kare** — sınav bu sınırla okunmalı.

---

## Nihai sayım

| iz | sonuç |
|---|---|
| `chg24` 0–20 bandında LONG | ✅ **AYAKTA** — 2 yıl, 25 ay, 4/25 pozitif, t=−4,11, canlı defterde tekrarlandı |
| Takip eden stop (30. çıkış varyantı) | ✅ **BOŞLUK KAPANDI** — ilk kez ölçüldü, KALDI |
| `top_ls` / `smart` | ❌ **ÇÖKTÜ** — 42 günlük holdout'ta dört ölçüt de düştü |
| `<-40` LONG (kapitülasyon) | ❌ çöktü — 3 aya yığılmış |
| `>40` LONG (pump alımı) | ❌ çöktü — 21 ayda t=+0,23 |
| Aynı sembole tekrar giriş | ❌ çöktü — ortalama tersini söylüyor |
| "Zarar etmeyen kombinasyon" | ❌ çöktü — sahtede de ~26 tane çıkıyor |

**7 iz · 1 ayakta · 1 boşluk kapandı · 5 çöktü.**
