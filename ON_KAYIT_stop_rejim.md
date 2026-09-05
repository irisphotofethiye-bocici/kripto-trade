# ÖN-KAYIT — STOP MESAFESİ, REJİME GÖRE: BOĞA'da cevap değişiyor mu?

**Yazılma tarihi:** 2026-09-05 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı talimatı (2026-09-05): *"22 ağustostan sonraki veriyi
kullanarak test et bi de, çünkü 2 yıllık veri rejim ayı rejim"* ve ardından
*"veri indirme, sadece eldeki veriyi kullan."*

---

## 1 · İtiraz haklı — ve sayısı burada

`ileri_rr.btc_rejim()` (BTC 720s değişimi ≥ %+15 → BOĞA, ≤ %−15 → AYI):

```
NOTR    554 gun   %77,5
AYI      84 gun   %11,7
BOGA     77 gun   %10,8      toplam 715 gun
```

⚠️ **Bir düzeltme:** örneklem *"ayı"* değil **NÖTR ağırlıklı**. Ama itirazın
çekirdeği ayakta: **BOĞA örneklemin onda biri**, ve önceki hüküm bu karışımın
ortalamasıydı.

## 2 · 🔴 KULLANICININ İSTEDİĞİ TARİH ÖLÇÜLEMEZ — sayıldı

`klines_1h_uzun` ve `funding_gecmis` **2026-08-25**'te bitiyor. Mekanik 72 saat
ileri getiri istiyor → kullanılabilir son tetik **~08-22**. Yani *"22 Ağustos
sonrası"* penceresinde **ölçülecek işlem yok.**

**Kullanıcı indirmeyi reddetti** (*"veri indirme"*), dolayısıyla bu pencere bu
ölçümde **açılmıyor.** Bunun yerine sorunun ölçülebilir hâli sınanır:
**rejim kırılımı.** Veride son BOĞA bloğu **2026-08-21..08-25** — yani
kullanıcının işaret ettiği epizodun **ilk 5 günü içeride.**

## 3 · BOĞA BLOKLARI — önceden sayıldı, sonuç değişkenine dokunulmadan

13 blok. Üç büyüğü (K2 bunlara dayanacak, **şimdi** sabitleniyor):

| # | blok | gün |
|---|---|---|
| **B1** | 2024-11-06 … 2024-12-10 | **35** |
| **B2** | 2025-05-06 … 2025-05-22 | **17** |
| **B3** | 2026-05-02 … 2026-05-06 | **5** |

Dördüncü blok 2026-08-21…08-25 (5 gün) — kullanıcının epizodu. **Ayrıca ve
BETİMLEYİCİ olarak** raporlanır; hüküm taşımaz (N çok küçük).

## 4 · 🔴 GÜÇ — hüküm yazılmadan ÖNCE hesaplandı

Tam örneklemde `A_funding` · `2.5x` · `R`: fark **+0,0518**, MDE **0,0522**,
653 gün. MDE `1/√gün` ile ölçekleniyor:

```
sqrt(653 / 77) = 2,91   ->   BOGA'da MDE ~ 0,152
```

🔑 **Yani BOĞA dilimi, ancak tam örneklemdekinin ~3 KATI bir etkiyi görebilir.**
Bu, ölçümden **önce** yazılıyor. Sonuç "göremiyoruz" çıkarsa bu bir sürpriz
değil, **beklenen** sonuçtur ve öyle raporlanacaktır.

## 5 · DEĞİŞMEYENLER — ölçü ve mekanik AYNEN korunur

🔴 **Birincil ölçü yine `R`**, ikincil yine `net%`. Bir önceki koşumda `net%`
geçmiş, `R` geçmemişti; **sonucu gördükten sonra ölçü değiştirmek** ön-kaydı
tiyatroya çevirir. Değişmiyor.

Kollar aynı (`A` · `1.5x` · `2.5x` · `4.0x`), mekanik aynı (`ileri_rr`'den
çağrılır), eşleştirme aynı (`asgari_stop` **A'ya göre**), evren aynı
(`A_funding` birincil · `B_ma50ucuz` ikincil).
Betik: `scratchpad/stop_mesafesi.py`'nin `tara()`'sı **yeniden yazılmadan** çağrılır.

## 6 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

Birincil hücre: **`A_funding` × BOĞA × `R`**, üç varyant.

| # | ölçüt | eşik |
|---|---|---|
| **K1** 🔴 | bir varyantın eşleşmiş `R` farkı | **> 0** · gün-kümeli t ≥ **+2,0** · işaret-çevirme permütasyonu **p ≤ 0,05** |
| **K2** | kazanan varyant **B1·B2·B3**'ün en az **ikisinde** aynı işaret | evet |
| **K3** | yalıtık hücre yasağı — merdivendeki **komşu** aynı işarette | evet |
| **K4** 🔴 | **rejim gerçekten fark yaratıyor mu:** `(BOĞA farkı) − (NÖTR farkı)` | **> 0** (işaret; t ayrıca raporlanır) |

**GEÇTİ** = K1+K2+K3+K4 · **ZAYIF** = K1+K2 var, K3/K4 düştü · aksi **DÜŞTÜ**.

🔴 **K4 bu ön-kaydın kalbi.** Kullanıcının iddiası *"rejim önemli"*. BOĞA farkı
NÖTR farkıyla **aynıysa**, rejim bu soruda bir şey açıklamıyor demektir —
BOĞA'da tek başına anlamlı çıksa bile.

## 7 · ÇOKLU KARŞILAŞTIRMA — önceden sayıldı

**Birincil: 3** (üç varyant, tek hücre). Permütasyon bu üçü üzerinden.
**İkincil ve hüküm taşımaz:** AYI dilimi · `B_ma50ucuz` × üç rejim ·
2R hedef kolu × rejim · 2026-08 bloğu tek başına.
🔴 **"Tabloya bakıp en iyi rejim-kol hücresini kural yapmak" YASAK** — bu
projede reddedilmiş davranış.

## 8 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%15 veriyorum.** Gerekçe bölüm 4: MDE, aranan etkinin
3 katı. Geçerse ya etki BOĞA'da gerçekten çok daha büyük, ya şans.

**Yönlü tahminler (tutmazsa aynen raporlanır):**

1. **BOĞA'da `A_funding` tetiği oransal olarak DAHA AZ olacak** —
   `funding ≤ −0,05` (derin negatif = kalabalık short) boğada nadirdir.
   Bu, BOĞA diliminin N'ini gün oranından (%10,8) **daha da** düşürür.
2. **Genişletmenin YÖNÜ iki rejimde de aynı (pozitif) çıkacak** → K4 düşecek,
   yani **rejim bu soruyu değiştirmiyor.**
3. **MDE gözlenen etkinin 2 katından büyük olacak** → hüküm *"göremiyoruz"*.
4. **2R hedef bulgusu BOĞA'da da duracak:** hedef stopla ölçeklendiğinde `A`
   en iyi kol kalacak. (Bu, önceki koşumun en bilgilendirici parçasıydı.)

## 9 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
**Veri indirme YOK** (kullanıcı talimatı) — hiçbir `.json` arşivine yazılmaz.
Salt-okuma. Betik: `scratchpad/stop_rejim.py` (**bu commit'ten SONRA**).
