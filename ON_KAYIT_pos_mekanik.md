# ÖN-KAYIT — `pos<0.25` kenarı botun KENDİ MEKANİĞİNDEN sağ çıkıyor mu?

**Yazılma tarihi:** 2026-09-04 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** `durum.md` → *`long_veto` ÖLÇÜLDÜ* → Karar 3 (Aşama 2).

---

## 1 · Soru

Ham ölçümde `pos < 0.25` (vetonun %68'i) **4 saatte +%1,26** kenar gösterdi
(gün-t +2,24). **Ama 24 saatte işaret döndü** (−%1,09).

`CLAUDE.md`'nin ölçüm sırası: `ham → mekanik → portföy`. Bu **mekanik aşamasıdır**
ve tek soru şudur:

> **Sekme 4 saat sürüyor. Botun stopu daha erken tetikleniyor olabilir.
> Kenar mekanikten sağ çıkıyor mu?**

🔴 Bu proje bunun **iki yönünü de** yaşadı: A-stop bir kez A+B'nin ham kenarının
**%65'ini** yedi; ama başka bir yerde de *"sinyal boş"* denen şeyin ölen tarafı
**stopumuz** çıktı. O yüzden ham ve mekanik **yan yana** raporlanır.

## 2 · MEKANİK — yeniden yazılmaz, ÇAĞRILIR

🔑 Bu oturumda pahalıya öğrenildi: rejim serisini kendim yeniden yazdım ve
doğrulanmışla uyuşmadı (üç hata). **Aynı hatayı tekrarlamamak için** mekanik
kod `scratchpad/stop_mu_sure_mu.py`'den **olduğu gibi çağrılır**:

- `seviyeler(h, l, c, i, yon)` — ölçücünün üç adaylı stopu (yapısal / son 10 bar
  / 1,5×ATR, girişe en yakın) + TP1 + TP2
- `oynat(h, l, c, i, yon, sl, tp1, tp2, risk, a)` — TP1 %40 @1,5R ·
  iz-süren 2,0→1,5→1,0 ATR · TP2 = TP1+1,5R · zaman stopu 48 saat

Modülde `__main__` koruması **yok**, o yüzden yalnız **fonksiyon tanımları**
(dosyanın `oynat` sonuna kadarki kısmı) çalıştırılır; analiz kısmı koşmaz.
⚠️ **Kopyalanmaz** — kaynaktan okunur, sürüklenme olmaz.

Maliyet: `2 × (taker %0,045 + slipaj %0,02) = %0,13`, **iki kolda da aynı**.
Asgari stop %2 sağlanmayan aday **elenir** (botun kendi kuralı), eleme oranı
**iki kol için ayrı** raporlanır.

## 3 · VERİ

Popülasyon: BOĞA dönemi aday satırları (2026-08-21…09-04), `rejim=BOGA`.
Fiyat: `scratchpad/aday_pencere_1h/` — saatlik, `[t, yüksek, düşük, kapanış]`.
Pencere 2026-08-03'te başlıyor → girişten önce **≥100 bar** geçmiş var
(`YAPI_BAR=100` şartı sağlanır).

⚠️ **KESİLME (truncation):** `oynat` 48 bar ileri gider; önbellek 09-05'te
bitiyor. 09-03 sonrası girişler tam 48 saati göremez. **Kesilen satır oranı
iki kol için ayrı raporlanır**; kollar arasında ayrışıyorsa hüküm **zayıflar**.

## 4 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

🔴 **BİRİNCİL:** mekanik uygulandıktan sonra `pos<0.25` ile `pos≥0.25`
arasındaki net getiri farkı. **Birim sembol-gün · gün-kümeli t.**

| # | ölçüt | eşik |
|---|---|---|
| **K1** | mekanikli fark | **> 0** ve gün-kümeli t ≥ **+2,0** |
| **K2** | ham kenarın korunan payı | mekanikli fark / ham fark ≥ **%50** |
| **K3** | 🔴 mekanik eşitliği | iki kolun **stop genişliği** ve **stop-olma oranı** 1,5 kat içinde |

**GEÇTİ** = K1+K2+K3 · **ZAYIF** = K1, K3 düştü (kıyas bozuk, aynen yazılır) ·
aksi **DÜŞTÜ**.

🔴 **K3 neden zorunlu:** `pos<0.25` bandın dibi demek → muhtemelen daha oynak
→ daha geniş stop. Kollar oynaklıkta ayrışıyorsa mekanikli kıyas
`CLAUDE.md` 2026-08-20 kuralı gereği **bozuktur** ve öyle yazılır.

**Zorunlu ek rapor:** her kol için ham vs mekanikli **yan yana** · stop-olma
oranı · medyan tutma süresi · çıkış sebebi dağılımı (STOP/TP1/TP2/ZAMAN) ·
asgari-stop elemesi · kesilme oranı · MDE.

## 5 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%30 veriyorum.** Gerekçe: ham kenar **4 saatlik bir
sekmeydi ve 24 saatte tersine döndü**. Mekanik simülasyon **48 saate kadar**
tutuyor; iz-süren stop ve TP1 sekmeyi yakalayıp erken çıkarmazsa dönüşü
yer. Yani mekaniğin kenarı **koruması için** TP1'in (1,5R) sekme içinde
tetiklenmesi gerekir.

**Yönlü tahminler (tutmazsa aynen raporlanır):**
1. `pos<0.25` kolunun **stopu daha geniş** olacak (bant dibi = oynak) →
   **K3 düşecek**.
2. `pos<0.25` kolunda **TP1 oranı daha yüksek** olacak (sekme 1,5R'yi
   tetikler) ama **TP2 oranı düşük** — yani sekip dönüyor.
3. Mekanikli fark ham farktan **küçük** olacak (kenarın bir kısmı yenir).

🔴 **Ve şimdiden:** K1 geçse bile bileşen **kaldırılmaz.** Sırada portföy
aşaması ve **ikinci bir BOĞA epizodu** var. 13 günlük tek epizot kapı
değiştirmez.

## 6 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
Salt-okuma, ücretli çağrı yok. Betik: `scratchpad/pos_mekanik.py`
(bu commit'ten SONRA).
