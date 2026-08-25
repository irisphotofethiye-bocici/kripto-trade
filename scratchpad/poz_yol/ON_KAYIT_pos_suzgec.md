# ÖN-KAYIT — `pos` bir RET SÜZGECİ olarak işe yarıyor mu?

**Yazıldı:** 2026-08-25, **koşumdan ÖNCE**, commit edildi.
**Betik (henüz yazılmadı):** `scratchpad/poz_yol/40_pos_suzgec.py`
**Ölçüt bu dosyada sabittir. Sonuç görüldükten sonra DEĞİŞTİRİLMEZ** (`CLAUDE.md` D/9).

---

## Neden bu ölçüm

`ON_KAYIT_pos_mekanik.md` karar tablosu: **A ✓ · B ✗ → *"Sinyal gerçek, tek başına
yön kuralı değil. Yalnız süzgeç olarak sınanabilir — ayrı ön-kayıt gerekir."***

Bu, o ön-kayıt. Soru **yön** değil, **ret**: *bot bir adayı almaya karar verdiğinde,
`pos` yüksekse almamak daha mı iyi?*

Elimizdeki dayanak: `pos` beş rejim penceresinin **beşinde de** aynı işaret
(gün-kümeli |t| 2,78–8,08 ham; mekanik sonrası 2,43–6,58). Ve kapı karnesinde
`pos >= 0,75 (tepe)` hücresi mekanikli **−0,0984**, `pos < 0,25 (dip)` **+0,1044**.

⚠️ Ayrıca canlı gözlem: bot boğada `pos = 0,93`'te LONG açtı — sinyalin en kötü
çeyreğinde. Bu ölçüm o davranışın bedelini sayısallaştırır.

---

## Tasarım

### Evren — botun GERÇEK kapılarından geçen adaylar

`ileri_rr.py`'nin kapı tanımları **birebir** kullanılır (fonlama eşiği düzeltilmiş
hâliyle: `fr[k]["r"] <= -0.05`, çarpımsız):

```
A_funding   funding <= -0,05                      -> SHORT
B_ma50ucuz  fiyat <= $0,07  VE  ma50_mesafe >= 3,72 -> SHORT
BOGA_LONG   skor >= 45  VE  smart != SHORT  VE  0,25 <= pos <= 0,85   -> LONG
```

Üçü **ayrı** raporlanır; havuzlanmaz.

**Fonlama `scratchpad/fonlama_oku.py` ile okunur** (birim doğrulaması zorunlu).

### Kollar — İKİ AYRIK GRUP, alt-küme DEĞİL

```
TUTULAN   kapiyi gecen VE pos <  ESIK
REDDEDILEN kapiyi gecen VE pos >= ESIK
```

İkisi **ayrık**tır → iki-örneklemli istatistik geçerli. `CLAUDE.md`'nin
*"alt-kümede t tanımsız"* uyarısı burada **geçerli değildir**, ve bu açıkça yazıldı.

Ayrıca üçüncü bir referans kol raporlanır:
```
TUMU      kapiyi gecen HEPSI (suzgecsiz)   <- gercek karsilastirma bu
```

### ESİK — TEK değer, tarama YOK

**`ESIK = 0,75`** (üst çeyrek). Sabit, ön-kayıtta belirlendi.
`0,70` ve `0,85` **yalnız sağlamlık** olarak raporlanır; hüküm 0,75'ten okunur.

⚠️ LONG kapısında bot zaten `pos <= 0,85` uyguluyor; süzgeç onu **0,75'e sıkar**.
SHORT kapılarında `pos` kısıtı **yok**; orada süzgeç yeni bir kısıt getirir.
🔴 SHORT'ta beklenti **ters yönde**: `pos` yüksekken SHORT daha iyi olmalı
(ilişki "çok koşan geri kalır"). Bu yüzden SHORT kolunda süzgeç
**`pos < ESIK` olanları reddeder** — yön kapıya göre çevrilir ve bu şimdi yazıldı.

### Mekanik ve örneklem — `37_pos_mekanik.py` ile AYNI

| | |
|---|---|
| veri | `scratchpad/klines_1h_uzun/` + `funding_gecmis/` |
| pencereler | ATH 24-09/12 · ATH 25-06/10 · TOPARLANMA 25-04 · DERİN-AYI 26-01 · AYI 26-06/08 |
| `pos` | `(c − lo20)/(hi20 − lo20)` |
| giriş | `b[i+1]["o"]` · adım 4 saat · `MIN_QV = 125000` |
| ufuk | 24 saat |
| stop | **%5 birincil**, %3/%8 sağlamlık · hedef %10 sabit |
| maliyet | **%0,1726** (ölçülmüş) |
| fonlama | dahil, `fonlama_oku` ile |
| istatistik | gün-kümeli, iki-örneklemli (Welch), her pencere ayrı |

---

## GEÇME ÖLÇÜTLERİ — koşumdan önce sabit

### KAPI S — süzgeç ayırıyor mu

| # | ölçüt |
|---|---|
| **S1** | TUTULAN − REDDEDİLEN farkı **> 0**, ≥4/5 pencerede (her kapı için ayrı) |
| **S2** | gün-kümeli iki-örneklemli **t ≥ +2,0**, en az **3 pencerede** |
| **S3** | üç stop genişliğinde de (%3/%5/%8) fark ≥4/5 pencerede pozitif |
| **S4** | **yoğunlaşma:** en iyi 3 sembol çıkınca fark ≥4/5 pencerede hâlâ pozitif |

### KAPI U — süzgeç UYGULAMAYA değer mi

| # | ölçüt |
|---|---|
| **U1** | TUTULAN kolu **TÜMÜ** kolundan iyi, ≥4/5 pencerede |
| **U2** | kazanç ≥ **+0,05 puan/işlem**, ≥3/5 pencerede *(maliyetin ~%30'u; altı gürültü)* |
| **U3** | **kapsam:** süzgeç aday sayısını **%60'ın altına düşürmemeli** — düşürürse portföy kuyruğu boşalır ve kazanç kâğıt üstünde kalır |

### KAPI Y — yön tutarlılığı

| # | ölçüt |
|---|---|
| **Y1** | LONG kapısında yüksek-`pos` **kötü**, SHORT kapılarında yüksek-`pos` **iyi** — ikisi de ≥4/5 |

---

## KARAR TABLOSU — sonuç görülmeden yazıldı

| sonuç | karar |
|---|---|
| **S ✓ U ✓ Y ✓** | Altıncı defter önerilir: aynı kapılar + `pos` süzgeci, tek değişken. Kullanıcı onayına sunulur. |
| **S ✓ U ✗** | Ayrım gerçek ama **uygulamaya değmez** (kazanç maliyetin altında ya da kapsam çöküyor). Kaydedilir, bot değişmez, `pos` yolu **kapanır**. |
| **S ✓ Y ✗** | Yön tutarsız → ilişki sanıldığı gibi çalışmıyor. Hüküm YOK, ayrı teşhis gerekir. |
| **S ✗** | **Süzgeç de düştü.** `pos`, mekanik sonrası uygulanabilir bir kural üretmiyor. Aynen kaydedilir. |

---

## BEKLENTİ — dürüstlük notu

- **S'nin geçmesini bekliyorum** — mekanik aşamada fark zaten 5/5 pozitifti (t 2,43–6,58).
- **U'nun DÜŞMESİNİ bekliyorum.** Mekanik aşamada etki 0,42–1,73 puandı ama bu
  **uç çeyrekler arası** farktı. Süzgeç yalnız üst çeyreği kesiyor; kalan kolun
  kazancı çok daha küçük olacak. U2 eşiği (+0,05) bunu sınar.
- **U3 ayrı bir risk:** LONG kapısı zaten `pos <= 0,85` uyguluyor; 0,75'e sıkmak
  aday sayısını belirgin düşürebilir.
- En olası çıktı: **S ✓ U ✗** → `pos` yolu kapanır ve bu aynen kaydedilir.

## Bilinen sınırlar

- Mekanik replay botun **gerçek** mekaniği değil (bot 1,5R kısmi + trailing ile
  çıkıyor; burada sabit stop/hedef). Bu, `37` ile tutarlı olsun diye seçildi.
- 1 saatlik barla stop kontrolü: bar içi sıra bilinmez → **stop öncelikli** (kötümser).
- **Portföy aşaması KAPSAM DIŞI** (8 pozisyon sınırı, boyutlandırma, kuyruk sırası).
  U3 yalnız kapsamı ölçer, portföy simülasyonu yapmaz.
- `BOGA_LONG` kapısı için 2 yıllık veride BOĞA rejimi az → N düşük olabilir;
  düşükse **ölçülemedi** yazılır, zorlanmaz.

**SALT OKUMA. Bot dosyalarına yazım YOK.**
