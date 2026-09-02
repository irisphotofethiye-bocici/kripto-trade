# ÖN-KAYIT — makro haberin kuyruğu: geç katılan hâlâ kazanır mı?

**Yazılma tarihi:** 2026-09-01 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** 19 Ağustos anekdotu (`olcumler.md` → *X GÖNDERİLERİ*). Orada makro bir
haberin kuyruğu **saatlerce** sürmüş görünüyordu — borsa duyurularının (5 dakikada
biten, `olcumler.md` → *OLAY KUYRUĞU*) tam tersi. **N=1 ve gün sonucu bilinerek
seçilmişti.** Bu ön-kayıt onu sınanabilir hâle getirir.

---

## 1 · Soru

```
makro haber cikti -> fiyat sicradi -> D dakika sonra KATILSAM ne kalir?
```

Bu tam olarak kullanıcının akışıdır: haber gelir, bildirim düşer, analiz edilir,
karar verilir — **hepsi dakikalar sürer.** Borsa duyurularında bu gecikme
öldürücüydü. Makro haberde de öyle mi?

## 2 · OLAY LİSTESİ — ve neyin dışarıda kaldığı

**FOMC kararları + FOMC tutanakları**, ikisi de **14:00 ET**.
Kaynak: `federalreserve.gov/monetarypolicy/fomccalendars.htm`.
Çapraz doğrulama: 2026 karar tarihleri projedeki `makro_takvim.json` ile **birebir**.
Yaz/kış saati elde hesaplanıp **iki bilinen noktada sınandı**; düşerse betik koşmaz.

| tip | N (pencere içi) |
|---|---|
| `fomc_karar` | 16 |
| `fomc_tutanak` | 17 |
| **toplam** | **33** |

🔴 **DIŞARIDA KALANLAR — ve bu ölçümün asıl sınırı:**
CPI/PPI/NFP alınamadı (`bls.gov` HTTP 403; 2024-2025 tarihleri **doğrulanamadı**,
tarih uydurulmaz). Hazine geri-alım duyuruları da doğrulanabilir geçmiş damgayla
alınamadı — **oysa 19 Ağustos'u açıklayan haber tam olarak oydu.**

⚠️ Yani bu ölçüm **19 Ağustos mekanizmasını doğrudan sınamıyor.** Titizlikle
tarihlenebilen **en yakın** makro olay sınıfını sınıyor. Fark önemli: FOMC
**takvimlidir**, piyasa önceden pozisyon alır; Hazine haberi o gün **sürprizdi**.
Bu ölçüm düşerse *"makro haber kovalanmaz"* denemez — *"takvimli makro olay
kovalanmaz"* denir.

⚠️ **2026-08-19 bu 33'ün içinde** (tutanak günü). Anekdotun günü, örneklemin
bir üyesi. Ayrıca o gün hem tutanak hem Hazine haberi vardı → **karıştırıcı**.

## 3 · YÖN — ileriye bakmadan nasıl atanır

Makro haberde yön **önceden bilinemez** (CPI sürprizi iki tarafa da gidebilir).
Bu yüzden yön, **ilk tepkiden** okunur:

```
yon = isaret( P(t0+5dk) - P(t0-5dk barinin kapanisi) )
```

Bu bilgi `t0+5dk`'da **elde vardır** → ileriye bakma yok. Giriş her hâlükârda
`t0+D`'de (D ≥ 5 dk) yapılır, yani yön atanırken kullanılan bilgi girişten önce
oluşmuştur.

## 4 · ÖLÇÜLEN BÜYÜKLÜK

```
giris  E(D) = P(t0+D)            D in {5, 15, 30, 60, 120} dk
cikis  X    = P(t0+D+H)          H in {60, 240, 1440} dk
getiri = yon * (X - E) / E * 100 - maliyet
```

Enstrüman **yalnız BTC** (makro olay BTC'yi hareket ettirir; alt paralar ekleseydim
aynı günü tekrar sayardım — sahte N).
Fiyat: Binance `fapi` 5 dakikalık mum, olay başına `[t0−7g, t0+3g]`,
`scratchpad/makro_pencere/` (YENİ dizin, mevcut arşivlere dokunmaz).
Maliyet: gidiş-dönüş `%0,13` (config türevi). **Kabul barı `%0,57`** —
önceki ön-kayıtla **aynı**, karşılaştırılabilirlik için.

## 5 · BOŞ HİPOTEZ — aynı yön kuralıyla eşleştirilmiş rastgele an

Her olay için `[t0−7g, t0+3g]` içinde, `[t0−2sa, t0+26sa]` **hariç**, `K = 20`
rastgele an. Her çekilişte **yön aynı kuralla** (o anın ilk 5 dakikasının işareti)
atanır ve **aynı D/H mekaniği** uygulanır.

🔴 Bu şart: yön kuralı momentum taşıyorsa, kontrol kolu da onu taşımalı. Yoksa
ölçtüğüm şey haberin etkisi değil, **kısa vadeli momentumun kendisi** olur.
Olay başına `gerçek − kendi çekilişlerinin ortalaması` = **eşli fark**.

## 6 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

🔴 **BİRİNCİL HÜCRE ÖNCEDEN ATANDI:** tüm olaylar havuzu · **D = 30 dk** ·
**H = 4 saat**. (Önceki ön-kayıtla aynı hücre — iki olay sınıfı doğrudan
kıyaslanabilsin diye.)

| # | ölçüt | eşik |
|---|---|---|
| **K1** | ham kenar (maliyet düşülmüş) | ≥ **+%0,57** |
| **K2** | şans tabanına eşli fark | **> 0** ve olay-t ≥ **+2,0** |
| **asgari N** | birincil hücrede olay | ≥ **10** |

**GEÇTİ** = K1 **ve** K2. Aksi **DÜŞTÜ**.

⚠️ **Çoklu karşılaştırma:** 5 gecikme × 3 ufuk × 3 grup (havuz/karar/tutanak) =
45 hücre. Hüküm taşıyan **1** ve önceden atandı. Kalan 44 **betimleyici**.

⚠️ **t neyin üzerinde:** olaylar farklı günlerde (33 olay, 33 ayrı gün), o yüzden
gün-kümeleme ile olay-kümeleme burada **aynı şey**; t olay üzerinden hesaplanır.

🔴 **GÜÇ DENETİMİ ZORUNLU.** N=33 küçüktür ve bunu **şimdiden** yazıyorum:
MDE (t=2'de asgari saptanabilir etki) hesaplanıp barla karşılaştırılacak.
`MDE > %0,57` ise hüküm *"etki yok"* değil **"göremiyoruz"** diye yazılır.

**Ek zorunlu rapor:** olay tipi başına N · ilk 5 dakikanın büyüklüğü (haber
gerçekten oynatmış mı) · yön dağılımı (kaç LONG / kaç SHORT) · mekanik eşitliği
(gerçek vs şans kolunun mutlak getirisi) · eleme dökümü.

## 7 · BEKLENTİ — sonuç görülmeden yazıldı

**Birincil hücrenin GEÇMESİNE ~%20 veriyorum.** Gerekçe: FOMC **takvimlidir**;
piyasa günler öncesinden pozisyon alır ve sürpriz saniyeler içinde fiyatlanır.
19 Ağustos'un tersine, burada kovalanacak kuyruk beklemiyorum.

**Yönlü tahminler (tutmazsa aynen raporlanır):**
1. İlk 5 dakikanın mutlak hareketi, rastgele bir 5 dakikadan **belirgin büyük**
   olacak — yani olaylar gerçekten oynatıyor (bu geçmezse ölçümün öznesi yok).
2. `fomc_karar`ın ilk tepkisi `fomc_tutanak`tan **büyük** olacak.
3. Kuyruk `D` ile **hızla** tükenecek; `D=120`'de kenar sıfır civarı.

🔴 **Ve şimdiden:** geçse bile bu bir **kural değildir.** N=33, tek enstrüman,
tek olay ailesi. Geçen bir bulgu ancak *"Hazine/regülasyon gibi SÜRPRİZ makro
haber ayrıca ölçülsün"* demeye yeter.

## 8 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.** Salt-okuma,
ücretli çağrı yok. Betikler: `scratchpad/makro_olaylar.py` (koştu, yalnız olay
tarihledi) · `scratchpad/makro_kuyruk.py` (bu commit'ten SONRA koşturulur).
