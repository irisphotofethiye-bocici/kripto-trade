# ÖN-KAYIT — MUM FORMASYONLARI (BOĞA penceresi)

**Yazılma tarihi:** 2026-09-06 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-06): *"mum formasyonları denemeye değer bir eşik mi?"*
→ *"bunu 2 yıllık veriyle değil bizim 22 ağustos sonrası verimizle test et. ve bu
formasyonlardan hangisini deneyeceksin niye?"*

---

## 1 · Bu ölçüm neden yapılıyor — ve önyargım ne

Mum formasyonları bu projede **hiç ölçülmedi** (`olcumler.md`'de sıfır kayıt).
Ama **üç yakın akrabası** ölçüldü ve üçü de düştü:

| akraba | N | hüküm |
|---|---|---|
| `stage` (`BASLIYOR`/`HAZIRLANIYOR`/`izle`) — projenin kendi fiyat-aksiyonu sınıflandırıcısı | 1.460 poz | kazanan/kaybeden dağılımı **AYNI** (d≈0) |
| pump tetiği | 18.420 | **DÜŞTÜ**, p=0,12; tek epizod çıkınca işaret döndü |
| hareket bitişi | 18.402 | **DÜŞTÜ**; *"detektör bir seçici değil, sadece bir gecikme"* — olayların %99,96'sı koşulu sağlıyordu |

**Teorik durum en kötüsü:** mum formasyonu saf OHLC = **en bant-kilitli veri**.
`CLAUDE.md`'nin merkezi dersi (*"her yeni aday erken fiyat hareketinin başka bir
ifadesi çıkıyor"*) formasyon için **tanım gereği** geçerli.

**Yine de ölçülüyor, üç sebeple:** (a) hiç denenmedi — bu projenin kuralı iki
yönlü çalışır, ölçmeden ret de çıkarılmaz; (b) maliyet ~sıfır, veri diskte;
(c) formasyon bir **yön** iddiasıdır — bugün skorun (%89 büyüklük) ve
`defter_usdt_20`'nin (büyüklük) düşme sebebine sahip **değil**.

## 2 · GÜÇ HESABI — ön-kayıttan ÖNCE koşuldu (`scratchpad/formasyon/00_guc.py`)

🔴 **Etkiye BAKMADI** — yalnız olay sayısı, etiketin varyansı ve oynaklık ayrışması.

```
gun kumesi           : 14      (2026-08-22 .. 2026-09-04)
sembol               : 566  ·  olculebilir bar: 182.561
gunluk ort getiri std: 1,277 puan
MDE (iki kol farki)  : 0,965 puan

olay sayilari: pin BOGA 9.849 · pin AYI 9.853 · yutan BOGA 16.360
               yutan AYI 15.511 · doji 20.886
```

**Güç yeterli.** Kıyas: A+B kapısının kabul edilmiş kenarı ~2,2 puan;
`chg24>40 LONG` ~2,3 puan. Gerçek bir kenar bu pencerede **görünür**.

🔴 **AMA KÖR BANT VAR ve şimdiden ilan ediliyor:** **0,2–0,97 puan** arası etkiler
maliyeti (%0,19 gidiş-dönüş) aşar ama MDE'nin altında kalır. O bantta sonuç
**"göremiyoruz"** olur ve **"etki yok" DEĞİLDİR.**

### 🔑 Zorunlu sınama ZATEN GEÇTİ

`CLAUDE.md`: *"hücreler oynaklıkta ayrışıyorsa ham getiri ZORUNLU"* — `chg24`
bandı bu sınamada çökmüştü (stop genişliği **3,3 kat** değişiyordu).

```
formasyon    oynaklik med   taban kati
TUM BARLAR       1,43%         1,00
pin              1,40%         0,98x
yutan            1,42%         1,00x
doji             1,41%         0,99x
```

Formasyonlar **oynaklıkta nötr**. Karşılaştırılan hücreler mekanik olarak eşit.
Yoğunlaşma da temiz: en yoğun gün toplam olayların yalnız **%8-9**'unu taşıyor.

## 3 · 🔴 PENCERE TEK REJİM — ve bunun iki sonucu var

```
2026-08-22 .. 2026-09-04  ->  14 gunun 14'u de BOGA
```

Kullanıcının rejim gerekçesi **doğrulandı**. Ama:

1. **Rejim kırılımı YAPILAMAZ.** Diğer ön-kayıtlarda birincil sağlamlık ölçütü
   olan *"rejimlerin ≥2/3'ünde aynı işaret"* buraya **konulamaz**; yerine ufuk
   tutarlılığı (F3) ve yoğunlaşma (F5) konuyor.
2. **Bulgu çıkarsa YALNIZ BOĞA için geçerlidir.** Genelleme yapılamaz. Bu proje
   rejim dönünce tablonun tersine döndüğünü **defalarca** gördü (basis BOĞA'da
   güçlü/AYI'da sıfır; çapraz borsa tam tersi).

## 4 · HANGİ FORMASYONLAR — ve NEDEN

**Seçim ilkesi tek soru:** *"bu formasyon, zaten ölçtüğümüz değişkenlerin
kodlamadığı bir şey kodluyor mu?"*

### DIŞARIDA — zaten ölçüldü, başka adla

| formasyon | mevcut karşılığı | kod | durum |
|---|---|---|---|
| Marubozu / büyük mum | `last1` · `chg24` (büyüklük) | `radar.py:117` | 30 hücre; LONG'da hiçbiri pozitif değil |
| Üç asker / üç karga | `last3` (3 bar momentum) | `radar.py:118` | skorun `s_brk` parçası — boş |
| İç bar / dar aralık (NR) | `comp` (TR/ATR sıkışması) | `radar.py:110` | `s_comp` skorun %20'si — boş |
| Boşluk (gap) | — | — | perp 7/24 açık, yapısal olarak yok |

### İÇERİDE — üçü, ve her birinin AYRI işi var

**1 · PIN BAR — 🔴 BİRİNCİL**

```
boga pin : alt_fitil >= 2 x govde  VE  ust_fitil <= govde
ayi  pin : ust_fitil >= 2 x govde  VE  alt_fitil <= govde
```

**Gerekçe (kod okumasından):** mevcut değişkenlerimiz `h`/`l`'yi yalnız iki
şekilde kullanıyor — `comp` (true range = **büyüklük**) ve `pos` (**20 barlık**
aralıkta konum). **Tek bir barın İÇİNDEKİ fitil asimetrisi hiçbir yerde
hesaplanmıyor.** OHLC'nin hiç kullanmadığımız tek parçası bu, ve bir **yön**
iddiası.

⚠️ **Dürüst akrabalık kaydı:** `pos` bir kuzendir ve **DÜŞTÜ**
(*"`pos` RET SÜZGECİ — DÜŞTÜ, `pos` YOLU KAPANDI"*, 2026-08-25). 20-barlık trend
konumu ile 1-barlık reddediliş farklı mekanizmalardır, ama bu akrabalık bulgunun
lehine değil aleyhine bir önsel.

**2 · YUTAN (engulfing) — ikincil**

```
boga : simdi YUKSELEN + onceki DUSEN + simdi.acilis <= onceki.kapanis
       + simdi.kapanis >= onceki.acilis        (ayi: aynasi)
```

İki barlı gövde ilişkisi; kapsanmıyor. **Ama kısmen `last1` ile örtüşüyor**
(o da kapanıştan kapanışa hareket) — birincil olmamasının sebebi bu.

**3 · DOJI — 🔑 NEGATİF KONTROL, aday DEĞİL**

```
doji : govde <= 0,10 x aralik
```

Doji **tanım gereği yönsüzdür.** Üçüncü yuva dördüncü bir adaya değil bir
**sağlamaya** harcanıyor: doji "öngörürse" bulgu şüphelidir — yön değil, başka
bir şey (oynaklık, likidite, saat etkisi) yakalıyoruz demektir.

🔴 **PARAMETRE TARAMASI YOK.** Eşikler standart tanımdan alındı (2× ve 0,10);
**optimize edilmeyecek**, alternatif eşik denenmeyecek.

## 5 · VERİ · BİRİM · ÖLÇÜ

| ne | değer |
|---|---|
| bar | **saatlik**, `klines_1h_uzun` + `taze_1h` birleşik |
| evren | **566 sembol** (seçim YOK, tarama YOK) |
| pencere | **2026-08-22 … 2026-09-04** (uçlar sabit) |
| etiket | **HAM** ileri getiri — mekanik YOK, stop YOK (`CLAUDE.md` aşama sırası) |
| ufuk | **+1s · +4s (BİRİNCİL) · +24s** |
| çıkarım | **gün-kümeli** t (14 küme) |

**Neden birincil ufuk +4 saat:** `golge`'nin medyan tutma süresi **1,8 saat**;
pump tetiği ölçümü +24s kullanmış ve *"ufuk stratejiyle uyuşmuyor"* diye kendi
sınırını yazmıştı. +4s botun gerçekçi tutuşuna en yakın basamak.

**Kontrol grubu:** aynı **sembol-gün** içinden eşleşmiş rastgele barlar
(tohum **20260906**). Formasyon barları ile aynı gün ve aynı sembolde olduğu için
gün/sembol etkisi düşer.

## 6 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra DEĞİŞTİRİLMEZ

Birincil hücre: **pin bar · +4 saat**.

| # | ölçüt | eşik |
|---|---|---|
| **F1** 🔴 | `pin_BOĞA − pin_AYI` (yön testi) | **≥ +0,50 puan VE gün-kümeli t ≥ +2,5** |
| **F2** | her yön KENDİ kontrolünü geçer | `pin_BOĞA > kontrol` **VE** `pin_AYI < kontrol` |
| **F3** | ufuk tutarlılığı (+1s · +4s · +24s) | ≥ **2/3** aynı işaret |
| **F4** | 🔑 **NEGATİF KONTROL** | `\|doji − kontrol\|` **< MDE** (doji öngörmemeli) |
| **F5** | 🔴 **yoğunlaşma** | en iyi **2 gün** çıkarıldığında hâlâ ≥ +0,50 |

**GEÇTİ = beşi birden.** Aksi **DÜŞTÜ.**

🔴 **F1 neden `BOĞA − AYI` farkı:** iki kol da pin bar olduğu için *"pin bar"*a
özgü her yan etki (oynaklık, likidite, saat) **birbirini götürür**. Geriye yalnız
**yön** kalır — ölçmek istediğimiz tam olarak o.

🔴 **F5 bu ön-kaydın kalbi.** 2026-09-05'te ölçülen **her** olumlu sonuç yoğunlaşma
testinde çöktü. 14 günlük bir pencerede iki gün toplamın büyük kısmını taşıyabilir.

⚠️ **`ZAYIF` kategorisi YOK.** F1 geçip diğerleri düşerse hüküm **DÜŞTÜ**'dür.

### İkincil — önceden ilan, GEÇTİ'ye SAYILMAZ

```
yutan (iki yon) · +1s ve +24s ufuklari · yon kirilimi olmadan havuz ortalamalari
```

### Çoklu karşılaştırma sayımı — şimdi ilan

```
3 formasyon x 3 ufuk x 2 yon = 18 hucre  (+ kontrol kollari)
```

Bu sayı hüküm yazılırken **tekrarlanır**.

## 7 · ZORUNLU EK RAPOR (hüküm taşımaz)

- Formasyon başına N ve gün başına dağılım (yoğunlaşma zaten %8-9 ölçüldü)
- **Sınıflandırma sınaması**: elle kurulmuş bilinen barlar → beklenen etiket.
  Düşerse betik **çalışmayı reddeder** (`CLAUDE.md`: sınıflandırma yapan her
  betikte zorunlu; `\b` heredoc vakası).
- **Ayna sağlaması**: yönler takas edilince fark tam işaret değiştirmeli
- Formasyonun `chg24` · `vol_x` · `comp` ile korelasyonu — *"başka adla aynı şey"*
  sorusunun doğrudan cevabı

## 8 · BEKLENTİ — sonuç görülmeden yazıldı

| soru | olasılık |
|---|---|
| **F1** (pin, +4s, yön testi) geçer | **~%20** |
| **beşi birden** geçer | **~%10** |

Gerekçe: `stage` zaten bir formasyon dedektörüydü ve hiçbir şey ayırmadı; iki
büyük OHLC çalışması (her biri N≈18.400) düştü; ve `pos` — pin bar'ın en yakın
akrabası — kapandı.

**Yönlü tahminler (tutmazsa aynen raporlanır):**

1. Etki varsa **kısa ufukta** (+1s) en güçlü olacak, +24s'te sönecek.
2. **Doji hiçbir şey göstermeyecek** (F4 geçecek). Gösterirse birincil bulgu da
   şüpheli sayılacak.
3. **Yutan, pin'den zayıf** çıkacak — `last1` ile örtüştüğü için.
4. En olası tek sonuç: **F1'in "göremiyoruz" bandına düşmesi** (|etki| < 0,97).

## 9 · Dokunulmayanlar

`testbot.py` · `golge.py` · `ayna.py` · `benim.py` · `defter2/3` · `radar.py` ·
`evren.py` · `kripto-config.json` · state · defterler · zamanlanmış görevler:
**hiçbiri.** Salt-okuma. İndirme **YOK** (veri diskte). Ücretli çağrı **YOK**.

Betik bu commit'ten **SONRA**: `scratchpad/formasyon/01_olcum.py`
