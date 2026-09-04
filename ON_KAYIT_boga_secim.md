# ÖN-KAYIT — BOĞA'da bot neyi seçti, ne seçseydi kazanırdı?

**Yazılma tarihi:** 2026-09-04 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı talimatı (2026-09-04): *"boğada işlem açmayacaksa bot ne
yapacak, bu kabul edilmez. 19'undan sonra çektiği verileri, açtığı longları,
seçtiği coinleri incele; ne olsaydı o coinleri seçmez artıya geçecek coinleri
seçerdi. Her aşamayı değerlendir, her ihtimali hesapla."*

---

## 1 · Kapsam ve kabul edilen kısıt

🔴 **"BOĞA'da işlem açma" seçeneği MASADAN KALKTI** (kullanıcı kararı).
Aranan şey **BOĞA içinde daha iyi seçim**, işlem sayısını sıfırlamak değil.

**Popülasyon:** aday arşivi, `rejim = BOGA`, **2026-08-21…2026-09-04**
→ **13.771 satır · 225 sembol · 13 gün**. Huni tamamen görünür:

| aşama | kayıt |
|---|---|
| taranan + skorlanan (hacim süzgeci **zaten** uygulanmış: ilk 150) | 13.771 |
| `karar-yok` (kapıyı geçemedi) | 11.550 |
| **`LONG/ONAY_BEKLE`** (kapıyı geçti) | **669** |
| `VETO:long_veto` | 1.240 |
| `VETO:blowoff` | 167 |
| `red_kapi = stop_cok_dar` | 62 |

**Yordayıcı alanlar (24):** `ayrisma · btc_chg3 · chg24 · comp · dip_yakit ·
dusuk_float · float_oran · funding · glob_ls · last1 · last3 · ma50_mesafe ·
mcap · oi24 · oi3 · pos · price · rel3 · score · smart · stage · taker ·
top_ls · vol_x`
*(`karar` · `red_kapi` · `sonuc` · `kaynak` **yordayıcı değildir** — botun
kendi kararı; yalnız AŞAMA işareti olarak kullanılır.)*

## 2 · ÖLÇÜLEN BÜYÜKLÜK

Ham ileri getiri, **mekaniksiz** (stop/hedef/maliyet yok), yön **LONG**:
`E` = satırın saatini içeren 1s barın kapanışı · **birincil ufuk 4 saat**
(botun BOĞA'daki medyan tutması 2,2 saat) · ikincil 24 saat.
**Birim = SEMBOL-GÜN** · **gün-kümeli t zorunlu** (önceki ölçümlerin kuralı).
Fiyat: `scratchpad/aday_pencere_1h/` (223/225 sembol mevcut).

## 3 · AŞAMA A — HUNİ (betimleyici, hüküm taşımaz)

Her aşamada **tutulan** ve **atılan** kümenin ham getirisi:

```
taranan  ->  kapiyi gecen  ->  vetodan sag cikan  ->  acilan
```

Ayrıca **vetoların karnesi**: `long_veto` ve `blowoff` **iyi mi kötü mü**
adayları engelledi? (Engellenenin getirisi kalanınkinden yüksekse veto ters çalışıyor.)

🔑 Bu bölüm *"her aşamayı değerlendir"* talebinin cevabıdır ve **hangi aşamanın
değer yok ettiğini** gösterir.

## 4 · AŞAMA B — AYIRICI TARAMASI (birincil, hüküm taşır)

*"Her ihtimali hesapla"* talebi. **24 alan × 2 kesim biçimi (çeyrek, ondalık)
= 48 sınama.** Her biri için: üst dilim getirisi − alt dilim getirisi.

🔴 **TARAMANIN KENDİSİ ŞANSA KARŞI SINANIR.** 48 hücre taranınca en iyi t
şans eseri büyük çıkar. Bu yüzden:

> **Permütasyon:** sonuç etiketleri **1.000 kez** karıştırılır, her seferinde
> **tüm 48 hücrelik tarama tekrarlanır** ve **en büyük |t|** kaydedilir.
> Böylece *"48 hücre arayınca şans eseri hangi t'yi bulurduk"* dağılımı çıkar.

| # | ölçüt | eşik |
|---|---|---|
| **K1** | gerçek taramanın en iyi \|t\|'si | permütasyon dağılımının **üst %5'inde** |
| **K2** | o aday, **kronolojik ilk yarıda** bulunup **ikinci yarıda** aynı işaretle ayakta mı | evet |
| **K3** | ayırdığı fark | ≥ **%1,0** (4 saatte, ham) — eyleme değecek büyüklük |

**GEÇTİ** = K1+K2+K3 · **ZAYIF** = K1+K2 · aksi **DÜŞTÜ**.

⚠️ **En iyi hücre TEK BAŞINA rapor edilmez** — permütasyon eşiğiyle birlikte
verilir. `CLAUDE.md`: *"tabloya bakıp en yüksek sayıyı kural yapmak reddedilmiş
davranıştır."* Permütasyon bu kuralın **araçla uygulanmış** hâlidir.

## 5 · AŞAMA C — TERS SORU (betimleyici)

*"Artıya geçecek coinleri seçerdi"* — o coinler **neydi**? BOĞA döneminde
4 saatte en çok yükselen sembol-günler alınır ve **alanlarının dağılımı**
kalanla karşılaştırılır. Bu **AŞAMA B'nin aynı sınamasıdır**, ters yönden
anlatılır; **ayrı hüküm taşımaz** (yoksa aynı veriden iki kez hüküm çıkar).

## 6 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%25 veriyorum.** Bu proje giriş tarafında **26 dilimin
26'sında** ayırıcı bulamadı ve *"ölçtüğümüz her şey tek banttan türüyor"*
dersi kayıtlı. Ama bu ölçümün **iki farkı var**: (a) popülasyon dar ve
homojen (tek rejim, 13 gün), (b) daha önce hiç **permütasyon düzeltmeli
tam tarama** yapılmadı.

**Yönlü tahminler (tutmazsa aynen raporlanır):**
1. Huni'de **kapı aşaması getiriyi İYİLEŞTİRMEYECEK** — taranan ile kapıyı
   geçenin ham getirisi birbirine yakın çıkacak (önceki ölçümde `KAPI−TABAN`
   +0,167% ve anlamsızdı).
2. `long_veto` **doğru** çalışacak (engellediği dilim daha kötü olacak).
3. En iyi ayırıcı `chg24` ya da `pos` ailesinden çıkacak — ikisi de fiyatın
   doğrudan ifadesi, yani *"tek bant"* dersini tekrarlayacak.

🔴 **Ve şimdiden:** K1 geçse bile **kural değildir.** Sonraki aşamalar
mekanik + portföy. Ayrıca 13 günlük tek epizot — ikinci bir BOĞA epizodunda
görülmeden kapı değişmez.

## 7 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
Salt-okuma, ücretli çağrı yok. Betik: `scratchpad/boga_secim.py`
(bu commit'ten SONRA).
