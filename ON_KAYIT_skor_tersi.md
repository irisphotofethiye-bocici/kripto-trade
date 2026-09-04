# ÖN-KAYIT — Skorun TERSİ: düşük skorlu adaylar alınsaydı ne olurdu?

**Yazılma tarihi:** 2026-09-04 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı talimatı (2026-09-04): *"skor: tersi doğru mu onu
notlamıştık, 22 Ağustostan beri bütün pozlara bak, skorun tersine işlem
alsaydı ne olurdu, skorun poz almadaki etkisi ne?"*

---

## 1 · Kayıtlı olgu — bu ölçümün çıkış noktası

Huni ölçümünde (`olcumler.md` → *BOĞA'DA SEÇİM*):

```
taranan (hacim suzgeci sonrasi)  -%0,816
skor >= 45                       -%1,132   <- DAHA KOTU
```

**Skor eşiği popülasyonu kötüleştiriyor.** Kullanıcı bunu *"skor ters yönü
gösteriyor"* diye kaydetmişti. Bu ölçüm o gözlemi **sınanabilir** hâle getirir.

⚠️ Bu bir **arama değil, doğrulama**: hipotez önceki ölçümden geldi ve
**tek bir önceden belirlenmiş karşılaştırma** sınanır. Permütasyon düzeltmesi
gerekmez (43 hücrelik taramanın aksine).

## 2 · POPÜLASYON

**Kullanıcının tarihi esas alınır: 2026-08-22'den itibaren.**
(Önceki ölçümler 08-21'den başlıyordu; fark bir gün, ayrıca raporlanır.)

**İki kaynak, ikisi de raporlanır:**

| kaynak | ne verir |
|---|---|
| `testbot_aday_arsiv.jsonl` | **karşı-olgu**: skor<45 adayları hiç alınmadı, yalnız burada var |
| `testbot_islemler.jsonl` | **gerçek**: botun fiilen açtığı pozisyonlar ve giriş skorları |

Arşiv kolunda ölçüm: **ham** ileri getiri **ve** botun mekaniği
(`seviyeler`/`oynat` **kaynaktan çağrılır**), `CLAUDE.md` sırası gereği ikisi
yan yana. Birim **sembol-gün** · **gün-kümeli t**.

## 3 · ÜÇ AYRI SORU — karıştırılmaz

Kullanıcının sorusu üç parça içeriyor ve **farklı cevapları var**:

| # | soru | nasıl ölçülür |
|---|---|---|
| **S1** | *"skorun tersine işlem alsaydı?"* | `skor < 45` kolu vs `skor ≥ 45` kolu |
| **S2** | *"skorun poz ALMADAKİ etkisi?"* | eşik seçimi: kapının aldığı vs taranan evren |
| **S3** | *"skorun BOYUTLANDIRMADAKİ etkisi?"* | `marjin_pct_hesapla` %8–12'ye doyuyor; ölçülmüş `skor~notional ≈ −0,03` |

**S3 zaten ölçüldü ve cevabı biliniyor** (`olcumler.md` → *BOYUTLANDIRMA*):
skor boyutu **belirlemiyor**. Burada yalnız **teyit** edilir, yeni hüküm yok.

## 4 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

🔴 **BİRİNCİL (S1):** `skor < 45` kolunun **mekanikli** net getirisi,
`skor ≥ 45` kolundan yüksek mi?

| # | ölçüt | eşik |
|---|---|---|
| **K1** | mekanikli fark (`<45` − `≥45`) | **> 0** ve gün-kümeli t ≥ **+2,0** |
| **K2** | ham fark aynı işarette | evet (mekanik yön çevirmemeli) |
| **K3** | bölünmüş yarı | fark **iki yarıda da > 0** |
| **K4** | 🔴 mekanik eşitliği | iki kolun stop genişliği ve stop-olma oranı **1,5 kat** içinde |

**GEÇTİ** = K1+K2+K3+K4 · **ZAYIF** = K1+K3, K4 düştü · aksi **DÜŞTÜ**.

🔴 **GÜÇ DENETİMİ ZORUNLU.** MDE hesaplanır; `|fark| < MDE` ise hüküm
*"etkisiz"* değil **"göremiyoruz"**.

**Zorunlu ek rapor:** skor **bantlarına** göre kırılım (betimleyici — eşiğin
mi yoksa monotonluğun mu iş gördüğü) · gerçek defterdeki pozisyonların giriş
skoru × sonucu · `skor ~ notional` teyidi · her kolun N'i (satır **ve**
sembol-gün) · çıkış sebebi dağılımı.

⚠️ **Çoklu karşılaştırma:** 1 birincil (S1). Skor bantları ve defter kırılımı
**betimleyicidir**, hüküm taşımaz. *"Tabloya bakıp en iyi bandı kural yapmak"*
bu projede reddedilmiş davranıştır.

## 5 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%40 veriyorum.** Ham veride yön belli (skor≥45 daha kötü),
ama bu oturumda **ham kenarların mekanikte eridiğini iki kez** gördük
(`pos<0.25`: +%1,43 → −%0,33). Skorda da aynısı olabilir.

**Yönlü tahminler (tutmazsa aynen raporlanır):**
1. Ham farkta `skor<45` **önde** olacak (huni ölçümüyle tutarlı).
2. **Mekanikli fark ham farktan küçük** olacak — bu oturumun tekrarlayan deseni.
3. Skor **bantlarında monotonluk OLMAYACAK**; fark eşik civarında yoğunlaşacak
   (yani skor sürekli bir bilgi taşımıyor, sadece eşik kötü yerde).

🔴 **Ve şimdiden:** K1 geçse bile bu *"eşiği ters çevir"* demek **değildir.**
`skor < 45` kolu **hiç işlem görmemiş** bir popülasyondur; oraya geçmek
botun tüm aday akışını değiştirir ve **portföy aşaması** ile **ikinci bir
epizot** gerektirir. Ayrıca skor eşiği aynı zamanda **aday sayısını** belirler
(kullanıcı kısıtı: *"girişi engelleyen kısır kapı olmamalı"*).

## 6 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
Salt-okuma, ücretli çağrı yok. Betik: `scratchpad/skor_tersi.py`
(bu commit'ten SONRA).
