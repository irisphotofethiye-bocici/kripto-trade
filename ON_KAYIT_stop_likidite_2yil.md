# ÖN-KAYIT — STOP LİKİDİTE KÜMESİ, **2 YILLIK** VERİDE (ÜÇÜNCÜ BAKIŞ)

**Yazılma tarihi:** 2026-09-07 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"2 yıllık veriye mi baktın?"* → *"ölçelim, ne
kaybedebiliriz?"*
**Betik:** `scratchpad/stop_likidite/02_uzun.py`
**Önceki:** `ON_KAYIT_stop_likidite.md` (`224162f`) → **GÖREMİYORUZ**,
`N=2.019 · 71 gün`, katmanlı fark `+1,1 puan`, `MDE 13,1 puan`

---

## 1 · 🔴 BU ÜÇÜNCÜ BAKIŞ — ve bedeli ödeniyor

Bu sabah `CLAUDE.md`'ye yazdım: *"ikinci bakış ÇOKLULUKTUR; açık uçlu
'bir daha bak' yanlış pozitif üretir. Bir kol açık bırakılırken sonraki
bakışın N eşiği ilan edilir."*

Önceki ölçüm **N eşiği ilan etmemişti** — kusur bendeydi. Bedeli şimdi
ödeniyor:

```
t esigi 2,0 -> 2,5   (ucuncu bakisin bedeli)
```

🔴 **Ve DÖRDÜNCÜ BAKIŞ OLMAYACAK.** Bu ölçüm ne çıkarırsa çıkarsın, bu
hipotez kapanır. Yeniden açılması ancak **yeni bir mekanizma iddiası**
ile olur, "biraz daha veri" ile değil.

## 2 · NEDEN YENİDEN — güç, ve YALNIZ güç

Önceki ölçümde:
- `S1` (yön) · `S4` (işaret) · `S5` (karıştırıcı, **%159**) · `S6` GEÇTİ
- `S2`/`S3` **yalnız güç yüzünden** düştü: etki `1,1 puan`, `MDE 13,1 puan`

`S5`'in geçmesi kritikti: `stop_p` ile `stop_pct` çakışması **%16/%14**,
rastgele beklentinin (%20) **altında** → gerçekten ayrı bir değişken.

**Eksik olan tek şey N.** Ve `N` gerçekten artırılabilir.

## 3 · POPÜLASYON — 🔴 BOTUN EVRENİ DEĞİL, ve bu bir SINIRDIR

```
ONCEKI : radar_archive · score>=30 · 74 gun · N=2.019
SIMDI  : klines_1h_uzun · MEKANIK ornekleme · ~584 gun medyan · 567 sembol
         toplam 294.458 sembol-gun
```

**Giriş kuralı — skor YOK, mekanik:**
```
her sembolde GUNDE BIR ornek (24 barlik adim)
stop = olcucu uclu mantik (destek / 10-bar dibi / 1,5xATR'nin EN YAKINI)
kapi = asgari_stop  (mevcut bot kapisiyla AYNI)
cikis = %10 hedef · 48s zaman stopu · maliyet %0,09  (AYNI)
```

🔴 **Geçse bile *"botun girişlerinde geçerli"* DEMEZ.** Bu, *"genel olarak
geçerli mi"* sorusudur. Botun evrenine taşımak **ayrı bir iş** olur.

## 4 · ⚠️ FAZ KAYDIRMA ZORUNLU

`CLAUDE.md`: *"`SEYRELT=24` FAZ KİLİTLER — zamanla ilgili her ölçümde faz
kaydır."* Harita **24 saatlik** pencereden kuruluyor ve hacmin **günlük
döngüsü** var; sabit fazda örneklersek her giriş aynı UTC saatine düşer.

```
her sembol icin faz = hash(sembol) mod 24  -> ornekleme o saatten baslar
```

## 5 · GÜÇ — sınırda, ve bu KOŞUMDAN ÖNCE yazılıyor

```
onceki: N=2.019   -> MDE 0,1307 (13,1 puan)
etkiyi gorebilmek icin (0,0113):  N > 2.019 x (13,1/1,13)^2 = ~270.000
elde: 294.458 sembol-gun (suzgeclerden sonra DAHA AZ olacak)
```

**Güç ancak yetişir.** `N` süzgeçlerden sonra `270.000`'in altında kalırsa
sonuç *"hâlâ güç yetersiz"* diye yazılır ve **bu kol yine de kapanır**
(bölüm 1).

## 6 · 🔴 EKONOMİK TABAN — koşumdan ÖNCE ilan

Önceki ölçüm etkiyi `~1,1 puan` gösterdi. Anlamlılık kazanmak onu
**kullanışlı yapmaz**: `1 puan` = 100 işlemde bir stop farkı.

```
KURAL YAZILABILMESI ICIN: katmanli fark >= 3,0 PUAN (0,030)
```

🔑 **Bu eşik sonucu görmeden konuyor.** `t` geçse bile fark `3 puanın`
altındaysa hüküm *"istatistiksel olarak görülür, ekonomik olarak
kullanılamaz"* olur ve **kural yazılmaz**.

## 7 · ÖLÇÜTLER — sonuç görüldükten sonra değişmez

| # | ölçüt | eşik |
|---|---|---|
| **U1** | HOLDOUT: **katmanlı** stop-olma farkı > 0 (küme içi daha çok yenir) | evet |
| **U2** | HOLDOUT: gün-kümeli **t ≥ +2,5** | üçüncü bakışın bedeli |
| **U3** | \|fark\| > **MDE** | evet |
| **U4** | KEŞİF ve HOLDOUT **aynı işaret** | evet |
| **U5** | **katmanlı ≥ ham etkinin %50'si** (ATR karıştırıcısı) | evet |
| **U6** | **negatif kontrol** temiz | evet |
| **U7** | 🔴 **katmanlı fark ≥ 3,0 puan** (ekonomik taban) | evet |

```
KURAL YAZILIR   = U1..U7 hepsi
GORULUR AMA ISE YARAMAZ = U1..U6 gecer, U7 duser
GUC YETERSIZ    = U1+U4+U5 gecer, U2/U3 duser
YON YOK         = U1 veya U4 duser
FIYATIN/STOPUN KILIGI = U2+U3 gecer, U5 duser
```

Keşif/holdout **zamana göre** bölünür (ilk %60 gün / son %40) — sembole
göre değil, çünkü rejim etkisi zamanla gelir.

## 8 · YÖNTEM — öncekiyle BİREBİR aynı, yalnız popülasyon değişti

Harita, `stop_p`, katmanlama, negatif kontrol: `01_olcum.py`'den **aynen**.
Kova genişliği `%0,25`, pencere `24 saat`, katsayılar
`0,99/0,98/0,96/0,90` — hepsi **aranmadı**, repodan/önceki ölçümden geldi.

⚠️ **Sözde-tekrar:** günlük örnekleme + `48s` ufuk → ardışık örneklerin
ufukları örtüşüyor. Çıkarım **gün-kümeli** yapılır; yine de `t` bir miktar
şişer ve bu **kayda geçiyor**.

## 9 · NE YAPILMAZ

- Bota, state'e, defterlere **dokunulmaz** · ücretli çağrı **YOK**
- Eşik **aranmaz** · faz **kaydırılır** (bölüm 4)
- `R` ile paydasındaki değişken arasında **Spearman koşulmaz**
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 10 · BEKLENTİM — koşumdan önce

**`U7`'nin (ekonomik taban) geçmesine %10.** Önceki ölçüm etkiyi
`1,1 puan` gösterdi; `3 puana` çıkması için önceki tahminin **üç kat**
yanlış olması gerekir.
**`U1..U6`'nın geçmesine %35** — yön tutarlıydı, karıştırıcıyı geçti,
tek eksik güçtü ve güç artıyor.

**Yani en olası sonuç: *"görülür ama işe yaramaz."*** Bunu baştan
yazıyorum ki çıktığında sürpriz olmasın.

⚠️ Bugün **on sekiz ön-kayıt yazıldı, on sekizi de geçemedi.**
