# ÖN-KAYIT — İLK GİRİŞ İYİ, TEKRAR GİRİŞ KÖTÜ MÜ?

**Yazılma tarihi:** 2026-09-05 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-05): *"tekrar girişler çok fazla, mesela Çince
yazılı coin kaç kere girdi ve zarar fazla — bunu sına."*

---

## 1 · Hipotez nereden geldi

İki bağımsız kaynaktan:

1. **Kullanıcı gözlemi** — aynı sembole tekrar tekrar girildiği ve zararın
   orada yoğunlaştığı (defter okunarak fark edildi).
2. **Bugünkü karşı-olgu ölçümü** (sentetik, NOTR kolu): sembolde
   **ilk giriş +3,549%** · **tekrar giriş −0,645%** (N=33/33).

🔴 **Bu ölçüm ONU TEKRARLAMAK DEĞİL:** kaynak popülasyon farklı.
Önceki bulgu **sentetik karşı-olguydu**; bu ölçüm **botun GERÇEK defterinde**
(389 pozisyon, iki yön, tüm rejimler, gerçek boyutlandırma) sınıyor.

## 2 · VERİ ve BİRİM

`testbot_islemler.jsonl` · kayıtlar **`id` ile birleştirilir**
(`CLAUDE.md`: P&L toplarken süzgeç UYGULANMAZ; kısmi kâr kaybolmasın).
Birim = **pozisyon**. Sıra = açılış `ts`.

**Etiket:** her pozisyon, o sembolde **kaçıncı giriş** olduğuyla işaretlenir
(1, 2, 3, …), kronolojik.

## 3 · 🔴 ASIL KARIŞTIRICI — ve birincil ölçüt ONU KONTROL EDER

*"Tekrar girişler kötü"* iddiasının en güçlü rakip açıklaması:
**tekrarlar kötü GÜNLERDE yoğunlaşıyor olabilir.** Bir sembol üst üste sinyal
üretiyorsa piyasa o gün hareketlidir; ilk giriş erken, tekrarlar geç kalır.

Bu ayrılmazsa ölçtüğümüz şey *"tekrar girmek kötü"* değil
*"o gün kötüydü"* olur.

🔑 **Bu yüzden BİRİNCİL ölçüt GÜN-EŞLEŞMİŞ karşılaştırmadır:**
ilk ve tekrar girişler **aynı gün içinde** karşılaştırılır; gün ortalaması
alınıp gün-kümeli t hesaplanır. Havuzlanmış karşılaştırma **ikincildir**.

## 4 · ÖLÇÜ

| ölçü | rol |
|---|---|
| **`sonuc_usdt / notional × 100`** (net %) | 🔴 **BİRİNCİL** — boyuttan arınık |
| `sonuc_usdt` (dolar) | ikincil — *"zarar fazla"* iddiasının doğrudan karşılığı |
| `r` | ikincil, ⚠️ kısmi kârı görmez (`CLAUDE.md`) — dolarla ters çıkabilir |

⚠️ **Ortak payda uyarısı:** `net% = sonuc/notional`. Bu ölçüyü **notional ile
korelasyona sokmayacağım**; yalnız **grup ortalaması** karşılaştırılır
(`CLAUDE.md`'nin izin verdiği kullanım).

## 5 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

| # | ölçüt | eşik |
|---|---|---|
| **K1** 🔴 | **gün-eşleşmiş** `ilk − tekrar` (net %) | **> 0** · gün-kümeli t ≥ **+2,0** |
| **K2** | **sembol-kümeli** t ile de aynı işaret | evet (tekrarlar sembolde yoğunlaşır) |
| **K3** | güç: `\|fark\| ≥ MDE` | evet, aksi **"göremiyoruz"** |
| **K4** | dolar cinsinden de aynı işaret | evet |

**GEÇTİ** = dördü · **ZAYIF** = K1+K3 var, K2 ya da K4 düştü · aksi **DÜŞTÜ**.

## 6 · ZORUNLU EK RAPOR (hüküm taşımaz)

- **Giriş sırasına göre kırılım** (1 · 2 · 3 · 4+) — monotonluk var mı
- **Yoğunlaşma**: en çok tekrar edilen 10 sembol, kaç giriş, toplam $
- **Kullanıcının işaret ettiği coin** — ASCII dışı sembol adları ayrıca listelenir
- Yön kırılımı (LONG/SHORT) · rejim kırılımı
- Tekrarların **ilk girişten kaç saat sonra** açıldığı

## 7 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%55 veriyorum.** İki bağımsız kaynak aynı yönü gösteriyor
(kullanıcı gözlemi + sentetik karşı-olgu) ama gün-eşleştirme etkinin bir
kısmını yiyecek.

**Yönlü tahminler (tutmazsa aynen raporlanır):**

1. **Havuzlanmış fark, gün-eşleşmiş farktan BÜYÜK olacak** — yani etkinin bir
   kısmı *"kötü gün"* karıştırıcısıdır.
2. **Giriş sırasında monotonluk olacak** ama 3. girişten sonra düzleşecek
   (N azalır, gürültü artar).
3. **Tekrarlar birkaç sembolde yoğunlaşacak** — en çok tekrar edilen 10 sembol
   tüm tekrarların yarısından fazlasını taşıyacak.
4. **Dolar farkı, yüzde farkından BÜYÜK görünecek** — çünkü tekrar girişler
   oynak/pahalı kurulumlarda oluyor ve notional farklı.

## 8 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
Salt-okuma. Betik: `scratchpad/ilk_tekrar_giris.py` (**bu commit'ten SONRA**).
