# YAPILACAKLAR — canlı liste (2026-08-21)

*Plan: `C:\Users\alper\.claude\plans\replicated-tickling-frog.md`
Bot **çalışmaya devam ediyor**, hiçbir dosyasına dokunulmadı.*

---

## ✅ BİTTİ

| # | iş | sonuç |
|---|---|---|
| 1 | **Süre sınırlı veri çekimi** — 74 sembol + BTC/ETH, 5 dk OI/top_ls/glob_ls/taker, 29 gün | ✅ 370 dosya · OI kapsamı **103/104 pozisyon** · 30 günlük pencere kurtarıldı |
| 2 | **BTC/ETH 5 dk, 2 yıl** (210.241 bar) | ✅ 5 dk mumun kalıcı olduğu doğrulandı |
| 3 | Pozisyon film şeridi (`01_yol.py`, N=80) | ✅ STOP'lar tepe konumu 0,43 · TP2'ler 1,00 · kâr geri verme medyan **%157** |
| 4 | OI/long-short pozisyon analizi (`02_oi.py`, N=75) | ✅ |
| 5 | 19 Ağustos vaka incelemesi (`04_btc_vaka.py`) | ✅ olay iki ayaklı: 15:30 iz, 17:45 kırılma |
| 6 | **Majör iz testi** (`06_major_iz.py`, ön-kayıtlı) | ❌ **GEÇMEDİ** — `olcumler.md`'ye yazıldı |
| 7 | Hacim → yön testi (`07_hacim_yon.py`, N≈5.000/yön) | ❌ hacim **yönü söylemiyor** (BTC p=0,43 · ETH p=0,93) |
| 8 | Taker karıştırıcı testi (`08_taker_karistirici.py`) | ❌ **fiyatın gölgesi** — etki %69/%56 küçüldü, işaret döndü |
| 9 | Boğa bacağı × fonlama, 2 yıl (`09_boga_bacagi.py`, 69 olay) | ❌ fonlama ayırmıyor (fark −0,04) |
| 10 | Olay kesiti (`10_olay_kesit.py`) | ✅ üç olayda `pos` yüksek + `rel3` negatif tutuyor; **OI imzası tekrarlamıyor** |
| 11 | **Ayıdan çıkış epizotları** (`11_ayidan_cikis.py`) | ✅ doğru kıyas kümesi — 3 epizot, **2'si geri verdi** |
| 12 | Pozisyon bazlı fonlama | ✅ boğa penceresinde fonlama P&L'in **%0,1'i** |

## 🔴 BULGULARIN PLANI DEĞİŞTİRDİĞİ YERLER

1. **Fonlama, gerçek botun sürtünmesi DEĞİL.** `−0,1479` rakamı **72 saat** tutan
   bir simülasyondan geliyordu; bot gerçekte **2,8 saat** tutuyor ve 34 pozisyonun
   30'u hiç fonlama ödemiyor. Sürtünme neredeyse tamamen **ücret + slipaj**.
   → Plandaki "uzun tutma" işi artık **fonlamayla birlikte** ölçülmeli, ayrı değil.
2. **Kıyas kümesi yanlıştı.** 69 boğa bacağının çoğu ATH bölgesinde; bugünkü
   zirveden **−%42,5** aşağıda, 8 aylık ayıdan çıkış. Doğru analog **3 epizot**.
3. **Öncü gösterge yok** — üç bağımsız deneme, üçü de karıştırıcı kontrolünde çöktü.
   Yeni sinyal aramaya devam **edilmeyecek** (plan zaten bunu yasaklıyordu).
4. **REJİM BOĞA'YA DÖNDÜ** (2026-08-21 03:46) — 29 günde ilk kez.
   `ONT LONG chg24 %27,9 · rejim_giriste BOGA` = `karar_yon`'un BOĞA dalının
   **ilk gözlemi**. Bu artık canlı bir ölçüm penceresi.

---

## ⏭️ SIRADAKİ İŞLER

### A · BOĞA REJİMİ CANLI GÖZLEM  🔴 en yüksek öncelik, kaçırılırsa geri gelmez
- Bot 29 günde ilk kez BOĞA dalında. Her BOĞA pozisyonu ayrı kaydedilecek.
- Ölçülecek: BOĞA'daki LONG/SHORT karnesi · `chg24@giriş` dağılımı ·
  `blowoff` vetosunun kaç LONG'u kestiği · stop davranışı.
- **Hiçbir şey değiştirilmeyecek**, sadece kaydedilecek.

### B · VERİ TEMELİNİ TAMAMLA (holdout'un önkoşulu)
- [ ] `klines_1h_uzun` → 08-11'den bugüne güncelle (567 sembol)
- [ ] `funding_gecmis` → 08-11'den bugüne güncelle
- [ ] `radar_bosluk.jsonl` geriye dönük harita (86 boşluk, `kaynak:"geriye_donuk"`)
- [ ] Alan-doluluk haritasını `olcumler.md`'ye yaz (gizli seçilim bulgusu)

### C · 11-20 AĞUSTOS HOLDOUT  (B bitmeden başlayamaz)
2 yıllık veri **tam 08-11'de bitiyor** → o 10 gün gerçek holdout.
- [ ] Ön-kayıt yaz + commit
- [ ] Sınanacaklar: SHORT yığını (+0,2340) · funding kapısı zararlı (−0,5430) ·
      pump engeli · `>40 LONG` + trailing (+2,379) · btc_pay · erken-stop (+0,057)
- [ ] Sınır baştan yazılacak: 10 gün ≈ tek epizot → *çürütebilir, doğrulayamaz*

### D · AYIDAN ÇIKIŞ EPİZOTLARI — genişlet
3 epizot az. Eşik `dd ≤ −30%` → `−20%` gevşetilirse 5-6 epizot olur,
**ama bu tanımı sonuçtan sonra oynatmaktır** → ayrı ön-kayıt şart.
- [ ] Ön-kayıt: "tutan sıçrayış ile geri veren sıçrayışı ayıran ne?"
- [ ] Değişkenler: fonlama seviyesi/klamp oranı · hacim yapısı · dipten süre ·
      BTC.D · toparlanma hızı
- [ ] Bugünkü epizot tabloya eklenecek (fonlama güncellenince)

### E · ZENGİN ALAN DATASETİ
`radar_archive` (29 alan) × ileri getiri, 06-24 → şimdi.
- [ ] **İki ayrı koşu**, asla karıştırılmaz:
      A) tam tarama (16 alan, %100 dolu) · B) skor-süzülmüş (top_ls/smart/glob_ls/taker)
- [ ] Hakem: gün-kümeli t (~57 gün) · şans · zaman yarıları · sembol yoğunlaşması

### F · SÜRTÜNME — revize edildi
- [ ] **Maker giriş modellemesi** (~0,077/taraf) — ters seçim dürüst modellenecek
- [ ] **Uzun tutma × fonlama BİRLİKTE** (ayrı ayrı ölçmek yanıltıcı — bulgu 1)
- [ ] Defter derinliğine göre boyut (`defter_usdt_20` toplanıyor, kullanılmıyor)
- [ ] ~~Premium index~~ → **ertelendi**: yeni bant aramak, 3 çöken izden sonra
      öncelik değil

### G · YENİ TEST BOTU  (A-F bitmeden başlamaz)
Kapılar/rejim/yön yalnız ölçülmüş kıyaslarla değişir. Mevcut bot devrede kalır.

---

## 🚫 DOKUNULMAYACAK

`testbot.py` · `golge.py` · `benim.py` · `ayna.py` · `radar.py` · `izleyici.py` ·
`kripto-config.json` · state dosyaları · açık pozisyonlar · zamanlanmış görevler ·
`radar_archive.jsonl` · `pozisyon_izleme.jsonl` · `defter2`.
Rejim eşikleri (`f10_histerezis_gun`, `f10_olu_bant_pct`) — **rejim kendiliğinden
döndü, müdahale gerekmedi.**

## 📏 HER ÖLÇÜMDE

Ön-kayıt koşumdan **önce** commit · `ham getiri → mekanik → portföy` ·
gün/ay-kümeli t · şans ölçümü · **karıştırıcı kontrolü** · iki evren karıştırılmaz ·
`py_compile` + `pyflakes` · sahte veri testlerinde "diske yazım: YOK" ·
çöken izler aynen raporlanır · sonuç `olcumler.md`, karar `durum.md`.
