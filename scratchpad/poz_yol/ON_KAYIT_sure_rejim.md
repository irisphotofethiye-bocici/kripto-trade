# ÖN-KAYIT — STOPUN DEĞERİ rejime mi, yöne mi bağlı?

**Yazıldı:** 2026-08-25, **koşumdan ÖNCE**, commit edildi.
**Betik (henüz yazılmadı):** `scratchpad/poz_yol/41_stop_rejim_yon.py`
**Ölçüt bu dosyada sabittir. Sonuç görüldükten sonra DEĞİŞTİRİLMEZ** (`CLAUDE.md` D/9).

---

## Nereden çıktı

`35_stopsuz.py` (2026-08-25, taze veri) botun **kendi 202 pozisyonunda** şunu gösterdi:

```
STOP YOK eksi STOP %3      A) NOTR/AYI N=111     B) BOGA N=91
 4 saat                        +0,547               -0,611
24 saat                        +1,175               -4,040
72 saat                        +2,060               -3,119
```

Yani **stopun değeri işaret değiştiriyor**: A'da stop kenarı yiyor, B'de koruyor.

## 🔴 Ama iki açıklama var ve ölçüm bunları AYIRAMIYOR

```
A kumesi : bot cogunlukla SHORT idi   ·  rejim NOTR/AYI
B kumesi : bot cogunlukla LONG idi    ·  rejim BOGA
```

**Rejim ile yön tamamen iç içe.** Gözlenen fark şundan olabilir:
- **H1 (rejim):** stop, yükselen piyasada korur, düşende yer.
- **H2 (yön):** stop, LONG'da korur, SHORT'ta yer — rejimden bağımsız.

Bu ölçüm ikisini **ayırmak** için var. Ayrılmadan hüküm yazılmaz.

⚠️ **Bu bir zaman-ileri holdout DEĞİL.** Aynı dönemleri kullanır ama **başka bir
evrende** (botun 202 pozisyonu yerine 2 yıllık 567 sembol taraması). Bu fark
açıkça yazıldı: *"çürütebilir, doğrulayamaz."*

---

## Tasarım

`37_pos_mekanik.py` ile **aynı** iskelet: `klines_1h_uzun` · adım 4 saat ·
`MIN_QV = 125000` · giriş `b[i+1]["o"]` · maliyet **%0,1726** · fonlama
**`fonlama_oku.py`** ile (birim doğrulaması zorunlu).

### Kesit — rastgele giriş DEĞİL, botun kapısı DEĞİL

Bu ölçüm bir **kapı** ölçümü değil; stop mekaniğinin rejim/yön etkileşimini
ölçer. O yüzden kesit **tarafsız** tutulur: her 4 saatte bir, hacim tabanını
geçen her sembol bir gözlem. Kapı süzgeci **uygulanmaz** — uygulanırsa kapının
kendi yanlılığı sonuca karışır.

### İki boyut, tam çapraz

```
REJIM   yukselen : ATH 24-09/12 · ATH 25-06/10 · TOPARLANMA 25-04
        dusen    : DERIN-AYI 26-01 · AYI 26-06/08
YON     LONG · SHORT          (her pencerede AYRI, havuzlanmaz)
STOP    %3 · %5 · STOP YOK    (birincil kiyas: STOP YOK eksi STOP %3)
UFUK    4 · 24 · 72 saat      (birincil: 24 saat)
```

**Likidasyon simüle edilir** (kaldıraç 3 varsayılır, eşik ~%33) — yoksa stopsuz
kol sahte iyi görünür.

### Ölçülen büyüklük

```
D  =  net(STOP YOK)  -  net(STOP %3)          islem basi puan
```

`D > 0` → stop **zarar veriyor**. `D < 0` → stop **koruyor**.

### İstatistik

Gün-kümeli `D`, her pencere × yön hücresinde ayrı. Hücre başına t.

---

## GEÇME ÖLÇÜTLERİ — koşumdan önce sabit

### H1 — REJİM açıklaması

| # | ölçüt |
|---|---|
| **H1a** | Yükselen 3 pencerenin **hepsinde** `D < 0` (stop koruyor), **her iki yönde de** |
| **H1b** | Düşen 2 pencerenin **ikisinde de** `D > 0` (stop yiyor), **her iki yönde de** |
| **H1c** | |t| ≥ 2,0, 10 hücrenin (5 pencere × 2 yön) en az **6**'sında |

**H1 = H1a ∧ H1b ∧ H1c.** Yön fark yaratmamalı; fark yaratıyorsa H1 düşer.

### H2 — YÖN açıklaması

| # | ölçüt |
|---|---|
| **H2a** | LONG'da `D < 0`, **5 pencerenin en az 4'ünde** (rejimden bağımsız) |
| **H2b** | SHORT'ta `D > 0`, **5 pencerenin en az 4'ünde** |
| **H2c** | |t| ≥ 2,0, en az **6** hücrede |

**H2 = H2a ∧ H2b ∧ H2c.**

### Ortak zorunlu kontroller

| # | ölçüt |
|---|---|
| **K1** | **yoğunlaşma:** en iyi 3 sembol çıkınca `D`'nin işareti hiçbir hücrede dönmemeli |
| **K2** | stop %5 ile de aynı işaret (≥8/10 hücre) |
| **K3** | **likidasyon oranı** her hücrede raporlanır; stopsuz kolda %25'i aşarsa o hücre *"likidasyon baskın"* diye işaretlenir ve hükme sayılmaz |

---

## KARAR TABLOSU — sonuç görülmeden yazıldı

| sonuç | karar |
|---|---|
| **H1 ✓ H2 ✗** | Stopun değeri **rejime** bağlı. Rejim-koşullu stop ayrı bir ön-kayıtla sınanabilir. |
| **H2 ✓ H1 ✗** | Stopun değeri **yöne** bağlı. `35`'in A/B farkı bir rejim bulgusu **değildi** — yön yapaylığıydı. Bu, `35`'in kaydına düzeltme olarak yazılır. |
| **İkisi de ✓** | Ayrılamadı (pencereler yön dağılımında da ayrışıyor demektir). Hüküm YOK, teşhis gerekir. |
| **İkisi de ✗** | `35`'in A/B farkı **botun kendi örneklemine özgü**, evrene genellenmiyor. `35` bir hüküm üretmez. |

---

## BEKLENTİ — dürüstlük notu

**H2'nin geçmesini bekliyorum.** Sebep: ölçülen dönemlerin çoğunda piyasa yönlü
hareket etti; yönlü bir piyasada trendin **tersine** açılan pozisyonda stop
kaçınılmaz olarak korur, **lehine** açılanda erken keser. Bu, bir "rejim bilgisi"
değil, trend ile pozisyon yönünün etkileşiminin mekanik sonucu.

Öyleyse `35`'in *"boğada stop koruyor, ayıda yiyor"* okuması **yanlış** olur;
doğrusu *"trendin tersinde stop korur"* olur — ve bot zaten trendin tersine
girdiği için (boğada shortta kalmıştı, sonra tepede longa girdi) bu bir
**giriş** sorunudur, stop sorunu değil.

⚠️ Bu beklentiyi yazıyorum ki sonuç tersine çıkarsa **kendi tahminimin
düştüğü** kayda geçsin.

## Bilinen sınırlar

- Aynı dönemler, farklı evren → **çürütür, doğrulamaz.**
- Kaldıraç 3 sabit varsayılıyor; botun gerçek kaldıracı 3-6 arasında değişiyor.
- 1 saatlik barla stop kontrolü: bar içi sıra bilinmez → **stop öncelikli** (kötümser).
- Hedef yok (saf stop-vs-stopsuz kıyası); hedefli hâli `28`'de zaten tarandı.
- **Portföy aşaması KAPSAM DIŞI.**

**SALT OKUMA. Bot dosyalarına yazım YOK.**
