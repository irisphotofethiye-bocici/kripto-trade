# ÖN-KAYIT — `pos` sinyalinin MEKANİK aşaması

**Yazıldı:** 2026-08-21, **koşumdan ÖNCE**, commit edildi.
**Betik (henüz yazılmadı):** `scratchpad/poz_yol/37_pos_mekanik.py`
**Ölçüt bu dosyada sabittir. Sonuç görüldükten sonra DEĞİŞTİRİLMEZ** (`CLAUDE.md` D/9).

---

## Gerekçe

`24_rejim_kararliligi.py` **ham** aşamada şunu buldu (`olcumler.md`, 2026-08-21):
son dönemde çok koşan, sonraki 24 saatte **görece geri kalıyor**. `pos` beş rejim
penceresinin **beşinde de** aynı işaret, gün-kümeli |t| 2,78–8,08, etki 0,56–2,24 puan.

`CLAUDE.md` sırası: **ham getiri → ticaret mekaniği → portföy.** Ham aşama bitti.
Bu ölçüm ikinci aşamadır. Portföy aşaması bu ön-kaydın **dışındadır.**

## Hipotez

**H1 (ilişki):** `pos`'un alt çeyreği ile üst çeyreği arasındaki fark, stop · hedef ·
maliyet · fonlama uygulandıktan sonra da **aynı işareti** korur.

**H2 (uygulanabilirlik):** Düşük-`pos` LONG kolu maliyet ve fonlama sonrası
**net pozitif** getirir — yani sadece "daha az kaybetmez", kazanır.

H1 ve H2 **ayrı sorulardır.** H1 geçip H2 düşebilir; o durumda sinyal gerçektir
ama tek başına yön kuralı değildir.

---

## Tasarım — ham aşamayla BİREBİR aynı örneklem

Aşağıdakiler `24_rejim_kararliligi.py`'den **değiştirilmeden** alınır:

| | |
|---|---|
| veri | `scratchpad/klines_1h_uzun/` (567 sembol, 1h) + `funding_gecmis/` |
| `pos` tanımı | `(c − lo20) / (hi20 − lo20)`, bar `i−20..i` |
| giriş referansı | `b[i+1]["o"]` |
| örnekleme adımı | `ADIM = 4` (4 saat) |
| hacim tabanı | `MIN_QV = 125000` |
| ufuk | 24 saat |
| çeyrekler | pencere **içinde** hesaplanır (havuzda değil) |
| gün-kümeli t | günde her kolda ≥5 gözlem şartı |

**Pencereler (5 tanesi; `BUGUN` HARİÇ — 2 gün, gün-kümesi hesaplanamaz):**
`ATH 24-09/12` · `ATH 25-06/10` · `TOPARLANMA 25-04/05` · `DERİN-AYI 26-01/03` ·
`AYI 26-06/08`

### Mekanik (ham aşamada YOK olan tek şey)

```
giris        b[i+1].o
stop         %5 BIRINCIL   ·  %3 ve %8 SAGLAMLIK
hedef        %10 sabit
ufuk         24 saat (ham asamayla ayni)
maliyet      %0,1726  <- OLCULMUS deger (olcumler.md, slipaj dogrulamasi)
             %0,13 ikincil olarak raporlanir (eski varsayim)
fonlama      tutma suresi boyunca kesilen dilimlerin toplami, yone gore isaretli
```

⚠️ **Neden %0,1726:** ölçülen slipaj varsayımın **2,5 katı** çıktı. `olcum_ortak.MALIYET`
hâlâ 0,13; bu ölçümde **kullanılmaz**, yalnız kıyas için raporlanır.

### Yön

**LONG ve SHORT ayrı ölçülür.** Aynı ilişkinin iki yüzü:

```
LONG   : dusuk pos  >  yuksek pos      (beklenen)
SHORT  : yuksek pos >  dusuk pos       (beklenen)
```

Bu **çoklu karşılaştırma değil, tutarlılık sınavıdır** — ikisi de aynı ilişkiden
çıkar. Biri tutup diğeri tutmazsa bu bulguyu **zayıflatır**, güçlendirmez.

### İstatistik

Gün-kümeli **eşleşmiş fark**: her gün için `ort(alt çeyrek) − ort(üst çeyrek)`,
sonra günler üzerinden t. İki kol **ayrık** çeyreklerdir (alt-küme DEĞİL), bu
yüzden `CLAUDE.md`'nin *"alt-kümede t tanımsız"* uyarısı burada geçerli değildir.

---

## GEÇME ÖLÇÜTLERİ — koşumdan önce sabit

### KAPI A — ilişki mekanikten sağ çıkıyor mu

| # | ölçüt |
|---|---|
| **A1** | stop %5 · LONG · fark **5 pencerenin ≥4'ünde pozitif** |
| **A2** | gün-kümeli **t ≥ +2,0**, en az **3 pencerede** |
| **A3** | üç stop genişliğinde de (%3/%5/%8) fark ≥4/5 pencerede pozitif |
| **A4** | **yoğunlaşma:** en iyi 3 sembol çıkınca fark ≥4/5 pencerede hâlâ pozitif |

**A = A1 ∧ A2 ∧ A3 ∧ A4.** Dördü de gerekli.

### KAPI B — tek başına yön kuralı olur mu

| # | ölçüt |
|---|---|
| **B1** | düşük-`pos` LONG kolunun **net ortalaması > 0**, ≥3/5 pencerede |
| **B2** | aynı kolun gün-kümeli **t ≥ +2,0**, ≥2 pencerede |

**B = B1 ∧ B2.**

### KAPI C — tutarlılık

| # | ölçüt |
|---|---|
| **C1** | SHORT tarafında fark **ters yönde** (yüksek `pos` üstün), ≥4/5 pencerede |

---

## KARAR TABLOSU — sonuç görülmeden yazıldı

| sonuç | karar |
|---|---|
| **A ✓ B ✓ C ✓** | Adım 2 önerilir: **altıncı defter**, tek fark sıralama (`-score` → `+pos`). Kullanıcı onayına sunulur. |
| **A ✓ B ✗** | Sinyal gerçek, **yön kuralı değil.** Yalnız *süzgeç* olarak sınanabilir — **ayrı ön-kayıt** gerekir. Bot değişmez. |
| **A ✓ C ✗** | Tutarsız. Hüküm YOK; SHORT'un neden ayrıştığı ayrıca ölçülür. |
| **A ✗** | **Mekanik aşamada düşen 30. varyant.** Aynen kaydedilir. `pos` yolu kapanır. |

---

## ZORUNLU TANI — hüküm yazılmadan önce raporlanır

`CLAUDE.md` sert kuralı: *"hücreler oynaklıkta ayrışıyorsa ham getiri zorunlu"*.
Ham zaten elimizde, bu yüzden bu **engel değil tanı**dır — ama **raporlanmadan
hüküm yazılmaz**:

```
kol basina:  stop-olma orani  ·  hedef-tutma orani  ·  ortalama tutma suresi
```

**Eğer iki kolun stop-olma oranı 1,5 kattan fazla ayrışıyorsa**, sonuç
*"ilişki mekanikten sağ çıktı"* diye değil, *"mekanik iki kolu farklı ölçüyor"*
diye yazılır — `chg24` bandındaki hatanın (3,3 kat ayrışma) tekrarı olmasın.

---

## BEKLENTİ — dürüstlük notu

Bu projede **mekanik aşamada denenen 20 hücrenin hiçbiri hem artı hem anlamlı
değildi.** Çıkış tarafında 29 varyanttan 1'i geçti.

- **A'nın geçmesini ORTA olasılıkla bekliyorum** — ham etki (0,56–2,24 puan)
  maliyetin (0,1726) belirgin üstünde ve beş pencerede de aynı işaret.
- **B'nin düşmesini bekliyorum.** İlişki *göreceli sıralama*dır: ayıda "düşük-`pos`
  daha az kaybeder" demek, "kazanır" demek değil. Ayı pencerelerinde B1'in
  düşmesi **beklenen** sonuçtur.
- En olası çıktı: **A ✓ B ✗** → süzgeç yolu, bot değişmez.

## Bilinen sınırlar (koşmadan önce yazıldı)

- `ADIM = 4` olduğu için `SEYRELT = 24` **faz kilidi bu ölçümde geçerli değil** —
  girişler tek bir UTC saatine düşmüyor. Yine de saat dağılımı raporlanır.
- 1 saatlik barla stop kontrolü: bar içi sıra bilinmez. Stop ve hedef aynı barda
  tetiklenirse **stop öncelikli** sayılır (kötümser, tek yönlü).
- `klines_1h_uzun` 2026-08-21'e kadar güncel; `AYI 26-06/08` penceresi tam.
- Fonlama 8 saatte bir kesilir; 24 saatlik ufukta en fazla 3 dilim.
- Bu ölçüm **portföy** aşamasını (8 pozisyon sınırı, boyutlandırma, kuyruk sırası)
  KAPSAMAZ.

**SALT OKUMA. Bot dosyalarına yazım YOK.**
