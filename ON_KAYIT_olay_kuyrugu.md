# ÖN-KAYIT — duyurudan sonra kovalanabilir kenar kalıyor mu? ("olayın kuyruğu")

**Yazılma tarihi:** 2026-09-01 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcının Grok/X ajentik önerisi (2026-08-30) → onaylanan plan, AŞAMA 1.

---

## 1 · Soru nereden geldi

Kullanıcı üç şey önerdi: (1) Grok'tan sayısal parametre, (2) Grok'un **rejim etiketi**
olması, (3) *"AVAX'la ilgili haber gelince sana bildirir, sen analiz edip poz
almamı sağlarsın."*

Üçünden **yalnız biri bugün geriye test edilebilir.** Rejim kolunda hindsight
kirlenmesi var (Grok'a *"2025'te ne derdin"* sorulamaz), bildirim kolunun kontrol
grubu yok. Ama *"haber çıktıktan N dakika sonra hâlâ kenar var mıydı"* sorusu
**kamuya açık duyuru arşivi + elimizdeki fiyatla** bugün cevaplanır — Grok'suz,
ücretli çağrısız.

**Belirleyici olan haberin kendisi değil, KUYRUĞU.** Zincir şu:
`Grok fark eder → biçimler → bildirir → Claude analiz eder → kullanıcı karar verir`.
Bu **dakikalar** sürer. Kuyruk o gecikmeden önce tükeniyorsa, insan-döngü akışı
kurulamaz ve boru hattına emek harcanmamalıdır.

## 2 · VERİ — ne var, ne yok

**Olay kaynağı:** Binance resmî duyuru arşivi (public CMS ucu, anahtarsız).
Her duyurunun `releaseDate`'i **dakika kesinliğinde** → `t=0` makine kesinliğinde,
yorum payı yok. `scratchpad/olay_listesi.py` ile çekildi (962 duyuru,
2024-08-12 … 2026-09-01), sınıflandırma **öz-sınamalı**.

**Fiyat:** Binance `fapi` **5 dakikalık** mum, olay penceresi başına
`[t0−3 gün, t0+2 gün]`, `scratchpad/olay_pencere/` altında önbelleklenir.
Ölçüldü: 5dk mum **iki yıl geriye geliyor** → çözünürlük engel değil.
⚠️ Yeni dizin; `perp_seri` / `klines_1h_uzun` **okunmaz da yazılmaz da** —
2026-08-24 ezme kaybının tekrarı yapısal olarak imkânsız.

**Aday sayımı (koşumdan önce, sonuç görülmeden):**

| olay tipi | aday (birincil · küme-ilk · sembollü) | ölçüme girer mi |
|---|---|---|
| `perp_listeleme` | 188 | ❌ **yapısal olarak elenir** — perp kendi listelenmesinden önce yoktur |
| `launchpool` | 86 | ✅ LONG |
| `delisting` | 46 | ✅ SHORT |
| `spot_listeleme` | 36 | ✅ LONG |

⚠️ `ikincil_ekleme` (134 duyuru — *"Will Add … on Earn/Convert"*) **dışarıda**:
aynı bilgiyi tekrar eden takip duyurusudur, birincil olayın kuyruğuna karışır.
⚠️ **Kümeleme:** aynı sembolde 48 saat içinde önceki birincil duyuru varsa o kayıt
`kume_ilk=False` işaretlenir ve **ölçüme girmez** (ileri getirisi öncekinin
kuyruğuyla karışır).

## 3 · ÖLÇÜLEN BÜYÜKLÜK

`t=0` = duyuru damgası. `p_ön` = duyurudan **önceki** 5dk barın kapanışı.

```
kacan(D)     = yon * (E(D) - p_on) / p_on * 100          E(D)= t0+D barinin kapanisi
ileri(D,H)   = yon * (P(t0+D+H) - E(D)) / E(D) * 100 - maliyet
sizinti      = yon * (p_on - P(t0-60dk)) / P(t0-60dk) * 100
```

`D ∈ {5, 15, 30, 60, 120, 240}` dk · `H ∈ {1sa, 4sa, 24sa}`
`yon`: listeleme/launchpool **+1**, delisting **−1**.

**Maliyet:** gidiş-dönüş `2 × (taker %0,045 + slipaj %0,02) = %0,13` (config türevi).
**Kabul barı** yine de **%0,57** (= 3 × %0,19) — plandaki muhafazakâr sayı üzerinden.
Bar bilerek config'in kendi maliyetinden yüksek tutuldu; sonradan **gevşetilmeyecek.**

## 4 · BOŞ HİPOTEZ — eşleştirilmiş rastgele an

Her olay için **aynı sembolde, aynı pencerede, aynı yönde, aynı D/H mekaniğiyle**
`K = 20` rastgele an çekilir. `[t0−2sa, t0+26sa]` aralığı **hariç** (olay bulaşması).
Olay başına `gerçek − kendi çekilişlerinin ortalaması` = **eşli fark**.

Böylece sembol · dönem · yön · mekanik · maliyet sabit; **değişen tek şey duyurunun
varlığı**dır.

## 5 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

🔴 **BİRİNCİL HÜCRE ÖNCEDEN ATANDI:** grup = `olumlu_duyuru`
(`spot_listeleme` + `launchpool` havuzu) · **D = 30 dk** · **H = 4 saat**.
*(30 dk = zincirin gerçekçi gecikmesi; 4 sa = gerçekçi ihtiyari tutma süresi.
Havuz güç için: iki tip de olumlu duyuru ve aynı yön.)*

| # | ölçüt | eşik |
|---|---|---|
| **K1** | ham kenar (maliyet düşülmüş) | ≥ **+%0,57** |
| **K2** | şans tabanına eşli fark | **> 0** ve gün-kümeli t ≥ **+2,0** |
| **asgari N** | birincil hücrede olay | ≥ **10**, altındaysa **hüküm YOK** |

**GEÇTİ** = K1 **ve** K2. Aksi **DÜŞTÜ**.

**Zorunlu ek rapor:** eleme dökümü (tip tip, sebep sebep) · sızıntı (`t=0` öncesi
1 saat) · mekanik eşitliği (gerçek vs şans kolunun mutlak getiri ortalaması) ·
kaçan hareket · tip başına N ve gün sayısı.

⚠️ **Çoklu karşılaştırma:** ızgara 6 gecikme × 3 ufuk × 4 grup ≈ **72 hücre**.
Hüküm taşıyan **yalnız 1** hücre var ve **önceden atandı**. Kalan 71 hücre
**betimleyicidir**, kural üretmez. *"Tabloya bakıp en yüksek hücreyi seçmek"*
bu projede reddedilmiş davranıştır.

🔴 **GÜÇ DENETİMİ ZORUNLU — "DÜŞTÜ" iki farklı şey olabilir.** Betik, eşli farkın
gün düzeyindeki standart hatasından **asgari saptanabilir etkiyi** (MDE, t=2)
hesaplar ve barla karşılaştırır:

- `MDE ≤ %0,57` → örneklem barı görecek güçtedir, **DÜŞTÜ anlamlıdır**
- `MDE > %0,57` → bar kadar büyük gerçek bir etkiyi bile göremeyiz;
  **"DÜŞTÜ" ETKİ YOK demek DEĞİL, "GÖREMİYORUZ" demektir** ve öyle yazılır

Bu madde bilerek kondu: bu proje bir kez *"gürültü, öldü"* diye gömdüğü hücrenin
ham getiride canlı olduğunu gördü (`chg24 >40 LONG`, 2026-08-20).

## 6 · BEKLENTİ — sonuç görülmeden yazıldı

**Birincil hücrenin GEÇMESİNE ~%25 veriyorum.** Gerekçe: borsa duyurusunun fiyat
etkisi **saniyeler-dakikalar** ölçeğindedir ve 30 dakika büyük olasılıkla geç.
Ayrıca listelemeler sıklıkla **önceden sızar** — sızıntı ölçümünün pozitif çıkmasını
bekliyorum, ki bu `t=0`'ın zaten hareketin ortasında olduğu anlamına gelir.

**Yönlü tahminler (tutmazsa aynen raporlanır):**
1. `kacan(D)` D ile **artacak** — en büyük sıçrama ilk 15 dakikada.
2. `delisting` (SHORT) kolunda kuyruk **listelemeden uzun** olacak; delisting takvimli
   ve etkisi günlere yayılır. Ama N=46 aday küçük, çoğu elenebilir.
3. `H=24sa` hücrelerinde kenar `H=4sa`'ten **büyük ama daha gürültülü** olacak.

🔴 **Ve şimdiden yazıyorum:** birincil hücre GEÇSE bile bu bir **kural değildir**.
`benim` defteri (insan kararlı) tüm geçmişinde **6 pozisyon** açtı; bir duyuru
akışının hacmi oradan gelmez. Geçen bir bulgu, kendi ön-kayıtlı portföy ölçümünü
hak eden bir **adaydır** — Aşama 2'nin (Grok alt botları) kurulma gerekçesi olur,
bot değişikliği değil.

## 7 · Dokunulmayanlar

`testbot.py` · `golge.py` · `ayna.py` · `defter2/3` · `radar.py` · `evren.py` ·
`kripto-config.json` · state · defterler · zamanlanmış görevler: **hiçbiri.**
Salt-okuma; ücretli çağrı yok. Betikler: `scratchpad/olay_listesi.py` (koştu, yalnız
olay saydı) · `scratchpad/olay_kuyrugu.py` (bu commit'ten SONRA koşturulur).

## 8 · Kayda geçen tuzak — bu ön-kayıtla birlikte öğrenildi

`olay_listesi.py` bir kez **heredoc ile** yazıldı ve düzenli ifadedeki `\b` sınır imi
gerçek **BACKSPACE karakterine (0x08)** dönüştü. Kural hiçbir zaman eşleşmedi; 134
duyuru yanlış sınıfa düştü. **`py_compile` DE `pyflakes` DE temiz geçti** — ikisi de
düzenli ifadenin *anlamına* bakmaz. Aynı sınıf: `radar.HERE` · `ayna.time`.
**Çözüm disiplin değil araç oldu:** `kural_sinamasi()` her koşumda 9 bilinen başlığı
sınar ve beklenen etiketi vermeyen bir kural varsa betik **çalışmayı reddeder**;
ayrıca kalıplarda kontrol karakteri arar.
