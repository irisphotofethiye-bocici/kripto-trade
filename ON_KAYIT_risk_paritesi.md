# ÖN-KAYIT — Risk paritesi tutuyor mu, tutmuyorsa nerede kırılıyor?

**Yazılma tarihi:** 2026-09-04 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** `durum.md` → *BOYUTLANDIRMA ÖLÇÜLDÜ* → Karar 2 (sıradaki iş).

---

## 1 · Neden bu ölçüm — ve önceki ölçümün dersi

Boyutlandırma ölçümünde ön-kayıtlı ölçütler geçti **ama yorumu geri çektim**:
`notional` yapısı gereği stop mesafesiyle ters orantılı olduğu için
`|ret| ∝ 1/notional` **mekanik** bir bağıntı. Eşit-ağırlık karşı-olgusu kısmen
formülün kendi aritmetiğini ölçüyordu.

🔴 **Bu ön-kayıt o tuzağa DÜŞMEMEK için kuruldu.** Her iddia için önce
*"bu büyüklük artefaktan bağımsız mı"* sorusu soruldu.

## 2 · Artefakttan bağımsız olan tek büyüklük: **R**

```
R_i = (fiyat hareketi) / (stop mesafesi)
```

Hem pay hem payda **giriş anında belirlenir ve boyuttan bağımsızdır**;
`notional` iki katına çıksa `R` değişmez. Bu yüzden:

🔑 **`ΣR > 0` ise, "her işlemde AYNI dolar riski alınsaydı defter artıda
olurdu" ifadesi ARİTMETİK OLARAK doğrudur** — çünkü o durumda
`P&L = sabit_risk × ΣR`.

⚠️ Buna karşılık `risk$ ~ R` korelasyonu **artefakt taşır** (`R = net/risk`,
payda ortak). **Bu ön-kayıt o korelasyonu HÜKME DAYANAK YAPMAZ**; yalnız
betimleyici olarak raporlar.

## 3 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

🔴 **BİRİNCİL:** `ΣR` (toplam R katı), **kronolojik iki yarıda da** pozitif.

| # | ölçüt | eşik |
|---|---|---|
| **K1** | `ΣR` | A ve B yarısının **İKİSİNDE DE > 0** |
| **K2** | havuz `ortalama R` | **> 0** ve t ≥ **+2,0** |
| **K3** | uç değer | en büyük ve en küçük **5'er R** atılınca K1 ayakta |

**GEÇTİ** = K1+K2+K3 · **ZAYIF** = K1+K2 · aksi **DÜŞTÜ**.

Havuz değeri **zaten biliniyor** (`ΣR = +62,06`, ort +0,193, t=+2,05 —
önceki koşumdan). O yüzden **hüküm K1'dedir**: bölünmüş yarı tekrarı.
Pooled t kıl payı (+2,05) olduğu için K1'in düşmesi **gerçekten mümkün**.

## 4 · MEKANİK BÖLÜM — sonuç HİÇ kullanılmaz, saf muhasebe

Bot şunu hedefliyor ([testbot.py:1224](testbot.py#L1224)):

```
hedef_risk = baz_equity * islem_risk_pct/100          (config: %1,5)
   smart karsi yonde ise  hedef_risk /= 2
gerceklesen_risk = stop_frac * notional
```

**Ölçülecek (hiçbir sonuç değişkeni girmez):**

1. `gerceklesen_risk / hedef_risk` oranının dağılımı.
2. Hedefin **±%20 bandında** tutturulan pozisyon oranı.
3. Hangi kısıt bağlıyor: `kaldirac_min=3` · `kaldirac_max=10` ·
   `kaldirac_guvenlik_kirp` · küçültme dalı.
4. Sapmanın **equity düşüşüyle** ne kadar açıklandığı (hedef zaten
   equity'ye orantılı — bu **tasarım**, kusur değil).

🔑 **Bu bölüm hüküm taşımaz ama en değerli kısmı olabilir:** tamamen
mekanik, döngüsellik ihtimali **sıfır**.

## 5 · KARŞI-OLGU — yalnız K1 geçerse anlamlı

```
esit_risk P&L = sabit_risk x ΣR
```
İki seviye raporlanır: (a) gerçekleşen riskin **medyanı**, (b) **hedef_risk**
ortalaması. Fark, *"parite tutsaydı"* ile *"parite hedeflendiği seviyede
tutsaydı"* ayrımını verir.

⚠️ **Çoklu karşılaştırma:** 1 birincil (K1). Mekanik bölümün 4 maddesi
**betimleyicidir**, hüküm taşımaz.

## 6 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%50 veriyorum.** Havuz t'si +2,05 ile eşiğin hemen
üstünde; ikiye bölününce her yarının N'i ve t'si düşer. Gerçek bir yazı-tura.

**Yönlü tahminler (tutmazsa aynen raporlanır):**
1. Gerçekleşen risk, hedefin **ALTINDA** kalacak (küçültme dalı yalnız
   yukarı sapmayı düzeltir; aşağı sapma için **düzeltme YOK** — asimetrik).
2. Bağlayan kısıt çoğunlukla **`kaldirac_max=10`** olacak (dar stopta
   gereken kaldıraç 10'u aşar, oraya kırpılır, hedef riske ulaşılamaz).
3. Risk yayılımının **büyük kısmı equity düşüşüyle** açıklanacak — yani
   "parite bozuk" demek haksız olabilir; hedef zaten kayan bir hedef.

🔴 **Ve şimdiden:** K1 geçse bile bu **kod değişikliği önerisi değildir.**
Sıradaki aşama **portföy simülasyonu** — 8 slot, marjin tavanı, düşüş freni
ve eşzamanlılık kısıtları karşı-olguda yok sayılıyor. Riski büyütmek
düşüş profilini de büyütür ve bu ölçüm onu **hiç görmüyor**.

## 7 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
Salt-okuma, ücretli çağrı yok. Betik: `scratchpad/risk_paritesi.py`
(bu commit'ten SONRA).
