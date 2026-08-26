# ÖN-KAYIT — `skor ≥ 45` bir FREN olarak doğru mu?

**Yazılma tarihi:** 2026-08-26 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı yönlendirmesi — puanı kâr kaynağına çeviremedik; **fren**
olarak sınanmadı.

---

## 1 · Neden bu, öncekinden FARKLI bir soru

Önceki iki ölçüm skoru **açan kapı** yapmaya çalıştı (giriş kuralı). Çıtası yüksek:
kârlı olacak, masrafı çıkaracak, her dönemde tutarlı olacak. **Düştü** (`57e0c57`).

Fren bunların hiçbirini yapmak zorunda değil. Tek işi **kaybettiren işlemleri
engellemek**. Ve bu projenin kayıtlı örüntüsü tam olarak bu yönde:

> *"Botun negatif filtreleri çalışıyor, pozitif seçicileri çalışmıyor.
> AÇAN kapıların ikisi de ZARARLI · ENGELLEYEN kapıların ikisi de DOĞRU."*
> — `olcumler.md`, kapı karnesi

## 2 · 🔴 AYIRMAM GEREKEN İKİ AÇIKLAMA

Ölçüm iki farklı dünyayı karıştırabilir ve **bunu önceden ayırıyorum**:

| açıklama | gözlenecek desen | doğru hüküm |
|---|---|---|
| **(a) skor kapısı suçlu** | `≥45` LONG'ları zararlı **VE** geri kalan LONG'lardan belirgin kötü | fren doğru |
| **(b) LONG tarafının kendisi bozuk** | `≥45` LONG'ları zararlı **AMA** geri kalanı da benzer şekilde zararlı | fren **yanlış teşhis** — sorun kapıda değil, LONG'un tamamında |

**(b) çıkarsa hüküm "fren çalışır" DEĞİLDİR.** O durumda doğru cümle:
*"botun bütün LONG tarafı kaybediyor, skor kapısı özel suçlu değil"* — ve bu,
frenden **daha önemli** bir bulgudur.

## 3 · Veri, kollar, mekanik

`radar_archive` tam tarama evreni (KOŞU A) · `(sembol, saat)` tekil · giriş anlık
görüntünün **bir sonraki** saatinin kapanışı · saat ofseti **−3** · **tüm skor
aralığı** (önceki ölçüm yalnız uçları yüklemişti; bu ölçüm `<45`'i **eksiksiz** ister).

Mekanik `olcucu.py`+`testbot.py`+config'ten birebir — üç adaylı stop · asgari %2 ·
TP1 yapısal/2R · TP2 = TP1+1,5R · %40 kısmi @1,5R · iz-süren 2,0/1,5/1,0 ATR ·
zaman stopu 48s · maliyet iki senaryo · fonlama (oran, %/8s).

| kol | tanım |
|---|---|
| **V — vetolanacak** | LONG, `skor ≥ 45` |
| **K — kalan** | LONG, `skor < 45` |

Yön **yalnız LONG** — fren botun alım tarafını kapatır, SHORT'a dokunmaz.

## 4 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

| # | ölçüt | eşik |
|---|---|---|
| **V1** | V zararlı mı (frenin varlık sebebi) | V net ortalama **< 0** **ve** gün-kümeli t ≤ **−2,5** |
| **V2** | 🔴 **AYIRICI** — V, K'dan belirgin kötü mü | `V − K` ≤ **−0,3 puan** **ve** gün-kümeli t ≤ **−2,5** |
| **V3** | işaret tutarlılığı | `V − K`, **≥%60 günde** negatif (her iki kolda N≥5) |
| **V4** | zaman yarıları | `V − K` **iki yarıda da aynı işaret** |
| **V5** | zorunlu sınama | V ve K'da stop genişliği + stop-olma oranı raporlanır |

**GEÇTİ (fren doğru)** = V1+V2+V3+V4
**AÇIKLAMA (b)** = V1 geçer, **V2 düşer** → hüküm *"LONG tarafının tamamı bozuk"*
**DÜŞTÜ** = V1 düşer (vetolanacak küme zaten zararlı değil)

**Ek zorunlu rapor:** eşik taraması (`≥40 / ≥45 / ≥50 / ≥60`) — **keşifsel**, en iyi
hücre seçilmez, yalnız eşiğin bir uçurumda mı yoksa platoda mı olduğunu göstermek için ·
`asgari_stop` elemesinin kolları eşit etkileyip etkilemediği · V'nin toplam LONG
zararı içindeki payı · fonlamanın payı.

## 5 · BEKLENTİ — sonuç görülmeden yazıldı

**V1'in geçmesine ~%55, V2'nin geçmesine ~%35 veriyorum.**
Yani **en olası tek sonuç açıklama (b)**: `≥45` LONG'ları zararlı çıkacak ama
geri kalan LONG'lar da zararlı çıkacak ve ayırıcı ölçüt düşecek.

Gerekçe: 2. aşamada `LONG skor<5` kolu da net negatifti ve `LONG≥45 − LONG<5`
farkı anlamlı değildi (t=−1,12). Aynı desenin `<45`'in tamamına karşı da
tekrarlanmasını bekliyorum.

⚠️ Ve (b) çıkarsa bu **kötü haber değil**, teşhisin yerini değiştirir: sorun
skor eşiğinde değil, botun LONG açma mantığının tamamındadır.

## 6 · Dokunulmayanlar

Bot · state · defterler · zamanlanmış görevler: **hiçbiri**. Ayrı süreç, salt-okuma.
Çıkan sonuç bir **öneri**dir; uygulama kararı kullanıcınındır.
Betik: `scratchpad/skor_fren.py` (bu commit'ten SONRA yazılır).
