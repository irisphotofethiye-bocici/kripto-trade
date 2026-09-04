# ÖN-KAYIT (EK) — NOTR rejiminde SHORT: ham fiyatta da kazanıyor mu?

**Yazılma tarihi:** 2026-09-04 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı itirazı (2026-09-04): *"11-19 Ağustos NOTR-AYI rejimiydi,
yani iki rejim var; NOTR-SHORT'ta bot seçtiği pozlarda büyük oranda artıda
kalıyordu."* — `ON_KAYIT_boga_long_ham.md`'nin **simetrik tamamlayıcısı**.

---

## 1 · İtiraz doğrulandı, ölçüm eksikti

`scratchpad/rejim_yon_karne.py` ile canlı defterden sınandı:

- Ölçüm penceresi **gerçekten iki rejim** taşıyor: `NOTR` (08-01…08-21) ve
  `BOGA` (08-21…). Önceki ham ölçüm **yalnız BOGA'ya** bakmıştı.
- `NOTR-SHORT`: ortalama getiri **+%1,67**, poz-t **+2,61** → *"artıda kalıyordu"*
  **doğru**. Dolar toplamı eksi, ama bu **boyut ağırlığı** (kayıtlı bulgu).
- `MA50+ucuz` çıkarılınca `NOTR-SHORT` = **+798 $ / 35 pozisyon**.

**Eksik olan:** bu başarı **ham fiyatta** da var mı, yoksa mekaniğin (TP1/hedef)
ürünü mü? Defter getirisi mekaniklidir; ham getiri hiç ölçülmedi.

## 2 · Yöntem — öncekiyle BİREBİR aynı

`ON_KAYIT_boga_long_ham.md` §3'teki tanım **değiştirilmeden** uygulanır:
1 saatlik mum · `E` = satırın barının kapanışı · mekanik yok · maliyet yok ·
birim **sembol-gün** · zaman dilimi sınaması zorunlu · ufuk `{1,4,12,24}` saat ·
**birincil H = 4 saat**.

Tek fark: **rejim = NOTR** ve **yön = SHORT**.

```
ret_SHORT(H) = -1 * (P(t+H) - E) / E * 100
```

**Kollar:**

| kol | tanım |
|---|---|
| **A+B** | `rejim=NOTR` · `funding ≤ −0,05` · `oi24 ≥ 10` |
| **MA50** | `rejim=NOTR` · `price ≤ 0,07` · `ma50_mesafe ≥ 3,72` |
| **TABAN** | `rejim=NOTR` — tüm satırlar (SHORT yönünde) |

Eşikler config'ten **okunur**, varsayılmaz (`ab_funding_esik` −0,05 ·
`ab_oi24_esik` 10,0 · `ucuz_fiyat_esik` 0,07 · `ma50_mesafe_esik` 3,72).

## 3 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

🔴 **BİRİNCİL HÜCRE ÖNCEDEN ATANDI:** kol = **A+B** · yön SHORT · H = **4 saat**.
*Gerekçe:* canlı defterde artıda olan ve ölçülmüş dayanağı olan kapı budur;
`MA50+ucuz` beş kez olumsuz çıktı, birincil yapılamaz.

| # | ölçüt | eşik |
|---|---|---|
| **K1** | A+B kolunun ham SHORT getirisi | ortalama **> 0** **ve** sembol-gün t ≥ **+2,0** |
| **K2** | A+B − TABAN farkı | **> 0** **ve** iki-örneklemli t ≥ **+2,0** |

**GEÇTİ** = K1 ve K2 · **ZAYIF** = yalnız K1 · aksi **DÜŞTÜ**.

🔴 **GÜN-KÜMELİ t ZORUNLU** (önceki ölçümde sonradan eklenmişti, artık kural):
sembol-günler aynı gün bağımsız değil. Gün-t de raporlanır ve
*"en kötü N gün çıkarılınca"* dayanıklılık satırı eklenir.

⚠️ **Çoklu karşılaştırma:** 3 kol × 4 ufuk = 12 hücre. Hüküm taşıyan **1**,
önceden atandı. `MA50` kolu **betimleyicidir** — beşinci kez ölçülüyor ve
hüküm taşımaz; yalnız önceki dördüyle tutarlı mı diye bakılır.

**Zorunlu ek rapor:** satır ve sembol-gün sayısı · zaman dilimi sınaması ·
oynaklık eşitliği (A+B vs TABAN, 1,5× kuralı) · MDE · sembol yoğunlaşması.

## 4 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%55 veriyorum.** Gerekçe: A+B'nin üç bağımsız olumlu kaydı
var (arşiv +0,396R · 2 yıllık funding bacağı +0,111 · canlı +190 $). Ama
N küçük olacak (canlıda 25 pozisyon; arşiv satırı daha çok ama sembol-gün
sayısı sınırlı) ve **fonlama bu ölçümde YOK** — A+B tanımı gereği negatif
fonlama seçer, yani ham kenar gerçek kenardan **yüksek** çıkar.

🔴 **Bunu şimdiden yazıyorum:** K1 geçse bile bu *"A+B kârlıdır"* demek
DEĞİLDİR. Kayıtlı ölçüm duruyor: **fonlama A+B'nin kenarının %83'ünü yemişti**
ve kontrol sinyali geçmişti. Ham ölçüm o hesabı **içermiyor**.

**Yönlü tahminler (tutmazsa aynen raporlanır):**
1. `TABAN` SHORT yönünde **~0 veya hafif eksi** olacak — NOTR yatay bir rejim,
   yönsüz sürüklenme beklerim.
2. `MA50` kolu **eksi ya da sıfır** çıkacak (önceki dört ölçümle tutarlı).
3. A+B'nin ham kenarı, canlı defterdeki yüzde getirisinden **büyük** olacak
   (mekanik ve fonlama ham getiriyi aşağı çeker).

## 5 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
Salt-okuma. Betik: `scratchpad/notr_short_ham.py` (bu commit'ten SONRA).
