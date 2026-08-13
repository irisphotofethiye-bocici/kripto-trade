# Fikir Defteri — Tur-2 Aday İyileştirmeleri (gerekçeli, ön-koşullu)

> **Amaç (2026-07-10):** Bu dosya, güçlü modelle yapılan strateji tartışmalarının GEREKÇELERİYLE dondurulmuş hali.
> Gelecek oturumlar (hangi model olursa olsun) buradan uygular; gerekçeyi yeniden türetmek zorunda kalmaz.
> **Kural: Her madde kendi ön-koşul kapısına bağlı — kapı sağlanmadan UYGULANMAZ. Test bitene kadar (21 Tem) hiçbiri koda girmez.**
> **İstisna ve değişiklik:** Bug-fix (tasarlanmış davranışı geri getiren onarım) her zaman serbest; kriter/fikir değişikliği SADECE kullanıcı kararıyla + tarihli izle yapılır — detay: `test-degerlendirme-programi.md` D bölümü madde 8-9.

## LONG tutarsızlığının teşhisi (kanıt özeti — kararların temeli)

Üç ayrı sebep var, karıştırma:
1. **Rejim (en büyük):** erken-kuşak N=86 ölçümü — hacim-uyanışı coinlerinin medyan +24h getirisi **-3.55%**. Evrenin kendisi long-düşmandı (F&G 17-25, ETF çıkışları, savaş). Botun seçim hatası değil. Aynı dönemde SHORT fade +$121 kazandı (simetrik kanıt: mean-reversion piyasası).
2. **Arketip eksikliği (yapısal):** Botun long girişleri anomali-tabanlı (radar OI/hacim tuhaflığı arar). Long'un klasik güvenilir arketipi bizde YOK: **kurulu trendde geri çekilme alımı** (ZEC kanıtı: Golden Cross + MA50 retrace — tarayıcı buldu, insan aldı, bot ASLA bulamazdı çünkü radar trend kalitesi puanlamıyor).
3. **Vetolar:** B-kalite long'ları eliyor (dip-bıçak/taker/blow-off = 0W/4L katilleri). "Boğayı kaçırtan" şey değil. TAC (N=1) tek başına hiçbir şey kanıtlamaz.

**Pump yakalama dürüst çerçevesi:** 5dk REST kadansıyla ateşlenme ÖNDEN yakalanamaz (akademik sistemler 30sn pencereyle ancak dakikalar önce bayrak kaldırıyor). Üç gerçekçi mod: (a) ateşlenmeyi önden almak → ÖLÇÜLDÜ, negatif (-3.55%); (b) tükenişi fade → kanıtlı edge (short karnesi + H2 %71 pozitif); (c) ikinci dalga (pump→konsolidasyon→devam) → SKL deneyi, N=1. **Hedef: ilk mum değil, ilk mumdan sonraki yapı.**

## Aday iyileştirmeler (öncelik sırasıyla)

### F1. Tarayıcı → Bot köprüsü (BOGA long arketipi) — EN YÜKSEK POTANSIYEL
- **Ne:** `tarayici.py` Tier1/2 çıktısındaki (CoinGecko top-150, uptrend'li likit coinler) sembolleri testbot'un aday evrenine ekle. Giriş kuralı YENİ İCAT EDİLMEZ: mevcut kapılardan (karar_yon, smart+taker, R/R, blow-off) aynen geçmek zorunda. Ek olarak trend-pullback tetiği tasarlanabilir: fiyat MA50(1h veya 4h)'ye retrace + taker≥1 teyidi.
- **Neden:** Long'un eksik arketipi bu. ZEC vakası kanıt. Bot şu an sadece hacim-top-40 + anomali görüyor; sağlıklı trend coinleri hiç göremiyor.
- **Ön-koşul:** 21 Tem sonrası + BOGA rejimi gelmeden gerçek testi yapılamaz (K6 simetriği: "gerçek BOĞA görülmeden long karnesi yargılanamaz").
- **Overfit koruması:** Yeni eşik yok; mevcut kapılar + tarayıcının mevcut Tier mantığı. Önce sanal.
- **SONUÇ (2026-08-10, KOŞULDU — ÖN-KAYITLI ÖLÇÜTÜ GEÇEMEDİ):** Geçmiş boğalarda test edildi (aşağıda "BOĞA BACAĞI ÖLÇÜMÜ" bölümü, N=410). Kural kontrol grubunu geçmedi (+0.046R vs kontrol +0.062R). Tek savunulabilir hücre TAM_BOGA (+0.130 vs kontrol +0.005) ama istatistiksel anlamlı değil. **F1 "kanıtlı arketip" statüsüne YÜKSELMEDİ; gerçek boğa gelmeden canlıya alınmaz.**

> **ÖLÇÜM GÜNCELLEMESİ (2026-07-15, patern araştırması N=14 pump + 15 kontrol, İZLENİM):** F2 kanıtı GÜÇLENDİ (kısa-ivme 9/14 pump vs 1/15 kontrol, öncülük 2-4h; 8/14 vaka arşiv kapsaması DIŞIYDI → F2 ancak TÜM-sembol olursa işler). F3 öncül iddiası ÇÜRÜDÜ (0/14; derin-neg funding hep T0 SONRASI = devam-teyidi, önden-görme değil). F4 0/4, F6 sadece KORU (FLOCK/RAVE yeni-listing DEĞİLDİ, hacim-eşiği-altı kapsama sorunuydu). OI-önbirikimi/smart-önyerleşimi ayrıştırmadı (3/14vs3/15, 5/6vs6/8) — kapı yapılmaz.

### F2. Snapshot-delta (15dk ivme) — BEDAVA ERKEN GÖRÜNÜRLÜK
- **Ne:** Radar zaten her 15dk TÜM piyasa ticker'ını çekiyor (`evren.raw_tickers`) ve fark verisini çöpe atıyor. Ardışık iki anlık görüntünün farkı = 15dk fiyat/hacim ivmesi, SIFIR ek API çağrısı. Çıktı: erken-kuşak benzeri ölçüm katmanı (`radar_active.json`'a alan + arşive etiket), KAPI DEĞİL.
- **Neden:** En hızlı sinyalimiz 1s mum + 24s hacim — pump'lar dakikalarda ateşleniyor; bu, tespiti saatler öne çeker. Literatür mikro-pencere anomalisini bir numaralı erken sinyal sayıyor.
- **Ön-koşul:** 21 Tem sonrası. Önce SADECE ölçüm (erken-kuşak gibi forward-return biriktir, 25-30 olay dolmadan alarm/karar entegrasyonu yok).
- **Uygulama notu:** radar --watch turunda önceki ticker snapshot'ını diske yaz (küçük json), sonraki turda diff al. Payload zaten elde.

### F3. Funding-fiyat ıraksama hızı
- **Ne:** Funding SEVİYESİNE değil İVMESİNE bak: "fiyat ↑ + funding ↓↓ (derinleşen negatif)" = short'lar hareketle kavga ediyor = devam yakıtı (SKL vakası: pump sırasında funding -2%/8s'e derinleşti, long carry +%3/12s ödedi).
- **Neden:** SKL girişini kapıdan geçiren şey buydu; sistematikleştirilmemiş. Radar `funding` alanını zaten topluyor — ardışık okumaların deltası arşivden bile geriye dönük ölçülebilir.
- **Ön-koşul:** Önce arşivden geriye dönük ölçüm (kod değişikliği gerektirmez, analiz scripti); edge görünürse Pillar-D'ye alan olarak eklenir (yine ölçüm-önce).

### F4. Spot-perp öncülüğü (basis kullanımı)
- **Ne:** `olcucu.py` basis_pct zaten hesaplıyor, hiçbir karar kullanmıyor. Spot-öncülü pump (pozitif basis, spot hacim baskın) = gerçek para = binilebilir; perp-öncülü = kaldıraç oyunu = fade malzemesi. "Binmeli mi fade mi" sorusunun ayracı.
- **Ön-koşul:** Önce mevcut arşiv + basis'in birlikte forward-return ölçümü; sonra karar entegrasyonu.
- **SONUÇ (2026-07-22, KOŞULDU — spot-öncülük PRATİK EDGE DEĞİL, RE anekdot):** RE canlı gözlemi (spot 391M>perp 189M, +30%) F4'ü öne aldırdı. Ölçüm (274 pump, 15ay, spot 24h-hacim vs perp 24h-hacim): **spot-öncülü (spot≥perp) pump 274'te SADECE 1** (N=1, o da AYI, long −10%). Yani spot-baskın pump istatistiksel olarak neredeyse yok — "spot≥perp" yapısal olarak nadir (perp hacmi ezici çoğunlukta baskın). **RE bir uç istisna (spot-payı %67), sistematik sınıf DEĞİL → bot-kuralı yapılamaz** (yeterli örnek yok; elle/CEO değerlendirilebilir ama bot için değil). YAN BULGU (perp-öncülü N=273, güçlü): rejim-fade doğrulandı — AYI long −1.35%/short +1.05% (fade et), BOGA long +0.33%/short −0.63% (fade etme), NOTR hafif-fade → F10 asimetrik kapı tasarımını (ayıda fade, boğada kapalı) BİR KEZ DAHA doğruluyor. İlk deneme (perp-hacim-3× pump tanımı) N=0 verdi = metodoloji hatası kabul edildi, fiyat-tabanlı yeniden koşuldu. Script: scratchpad/f4_basis_test.py. **F4 kapı-adayı DÜŞTÜ; spot-payı-çeyrek varyantı eşik-arama riski taşır, açılmaz.**

### F5. Sektör/anlatı kümelenmesi (gecikme arbitrajı)
- **Ne:** CoinGecko kategorileriyle evreni etiketle (cg_universe zaten çekiliyor, kategori alanı eklenebilir). Lider pump'layınca (LAB gibi) aynı sepetin henüz oynamayan üyelerini izleme/alarm listesine yükselt.
- **Neden:** 2026 piyasası anlatı-güdümlü rotasyon (genel ralli değil) — AI/privacy/RWA sektörlerine seçici akış; lider→takipçi gecikmesi saatler-günler.
- **Ön-koşul:** 21 Tem sonrası, önce alarm-katmanı olarak (KAPI DEĞİL). Kategori verisi CoinGecko'dan ek çağrı ister — rate-limit bütçesine dikkat.

### F6. Yeni-listing takvimi — K5 KAPISINA BAĞLI
- **Ne:** Binance duyuru/yeni-listing takibi; erken-kuşağın 8-gün-geçmiş şartının kör bıraktığı coinler (KAT vakası).
- **Ön-koşul:** SADECE kacirma_analiz haftalarca tekrarlayan MISSED≥3/10 + aynı sebep gösterirse (K5). Tek günün anekdotuyla eklenmez.

### F7. Emir defteri dengesizliği — RAFTA
- **Ne:** Bid duvarı/ask incelmesi (literatürün 1 numaralı erken sinyali). AMA sürekli derinlik takibi WebSocket altyapısı ister, 500+ sembolde bütçemizi aşar.
- **Ön-koşul:** Sadece kısa-liste adaylarına on-demand bakış olarak düşünülebilir; sürekli tarama YOK.

### F8. Erken-kuşak → SHORT-fade setup beslemesi — K2-b KAPISINA BAĞLI
- **Ne:** H2 ölçümü güçlüyse (pop-fade SHORT: tespit+4h'te short) erken-kuşak, testbot'un SHORT tarafına aday üretir. İlk ölçüm: medyan +3.13%, %71 pozitif (N=86); skor≥40: +5.04%, %86 (N=22).
- **Ön-koşul:** 21 Tem'de K2-b teyidi (N≥30 + medyan≥+2% — şimdiden sağlıyor görünüyor ama boğa dönemi verisi eklenecek).

### F9. Ölçücü taze-pump stop düzeltmesi — K4, KOŞULSUZ
- **Ne:** `swings(left=3,right=3)` taze retrace dibini göremiyor (SKL: -%5.2'lik mantıksal seviye yerine -%10.6 ATR fallback). Düzeltme: "son N-bar en düşüğü − 0.25×ATR" aday-invalidasyon, 1.5×ATR ile girişe yakın olanı seç.
- **Ön-koşul:** 21 Tem sonrası ilk iş (veri gerektirmez, belgeli tasarım hatası).

### F10. Rejim katmanlama: SEZON × HAVA + ölü bant + asimetrik kapı — YAPISAL KONSOLİDASYON (2026-07-12, kullanıcı kararı)
- **Ne:** `evren.btc_rejim()` tek katman (BTC 1d kapanış vs SMA20 + eğim) ve KESKİN — kıl payı fark (+119$ eğim) tam BOĞA etiketi üretiyor. İki katmana çıkar:
  - **SEZON (yavaş, aylar):** BTC haftalık yapı (örn. haftalık kapanış vs uzun ortalama) + hipotez#3 boğa-dönüş kontrol listesi (breadth ≥%50, BTC.D <54 trendi, USDT.D kırılımı, liderlik genişlemesi). Kaynak: piyasa_yapisi_log — **YENİ VERİ YOK, hepsi zaten toplanıyor.**
  - **HAVA (hızlı, haftalar):** mevcut SMA20 ölçümü + **ölü bant** (SMA'ya uzaklık marjinal ise NOTR — aday eşikler ölçümden ÖNCE yazılır) + **histerezis** (etiket değişimi 2-3 gün üst üste teyit ister; günlük flip-flop yasak).
  - **Çapraz matris:** SEZON=AYI + HAVA=BOGA → **"TEPKI_RALLISI"**: anomali-long dalı KAPALI, fade-short AÇIK, long yalnız F1 arketipiyle. Tam long-agresiflik ancak SEZON=BOGA + HAVA=BOGA.
- **Neden (kanıt):** SXT vakası 2026-07-11/12 — kıl payı BOĞA etiketi anomali-long kapısını açtı, bot aynı düşen coine 3 kez long girdi (-$95 kapanmış + 1 açık). Karne: BOGA_LONG 0/4 -$154 vs AYI_SHORT 3/3 +$42. Asimetri kanıtı: erken-kuşak LONG medyan -3.55% vs fade SHORT +3.13% → **long'u geç açmanın maliyeti küçük (gerçek boğa aylarca sürer), ayı rallisinde ters kalmanın maliyeti anında ve tekrarlı.** Gösterge güvenilirliği notu: F&G yalnız uçlarda anlamlı; RSI rejim bilinmeden okunamaz (döngüsel — trend piyasasında 70 üstünde haftalarca kalır); hiçbir gösterge sezonu "bilmez" — hızlı tanım çok yanlış sinyal verir, yavaş tanım geç kalır; kanıt bizi "long tarafında yavaş/katı, short-fade tarafında esnek" seçimine itiyor.
- **KONSOLİDASYON ŞARTI (sadelik — bu maddenin varlık sebebi):** F10 nokta-yamaların YERİNE geçer, üstüne binmez. F10 uygulanıyorsa şunlar EKLENMEZ: sembol ceza-hafızası, cooldown uzatma, yeni anomali-long vetoları (SXT'yi bunlar değil sezon katmanı çözer). TEPKI_RALLISI dalı mevcut long-veto zincirinde gereksizleşen koşul bırakırsa emekliliği değerlendirilir — **ekleme = çıkarma adayı dengesi.**
- **Ön-koşul:** 21 Tem sonrası. ÖNCE geriye dönük ölçüm: aday tanımlar (ölü bant eşikleri, sezon kriterleri) sonuca bakmadan yazılır, TÜM arşivde (radar_archive + piyasa_yapisi_log + islemler) test edilir: "bu tanım dönemi nasıl etiketlerdi, karne hücreleri nasıl değişirdi?" **SXT'yi kurtaracak şekilde eşik ayarlamak YASAK** (tek-vaka optimizasyonu = overfit); genel ilke yazılır, bütün dönemde ölçülür.
- **Sınır:** Elimizde gerçek BOĞA sezonu verisi yok — SEZON katmanının boğa tarafı ancak boğa geldiğinde doğrulanır (K6 simetriği). O güne kadar F10'un kanıtlanabilir kısmı AYI/TEPKI_RALLISI ayrımıdır (derin backtest bu sınırı KISMEN aşar, aşağıda).
- **DOLAR-DEĞERİ KANITI (2026-07-22, F10 replay — 35 test-işlemi doğru etiketle yeniden oynatıldı):** Mevcut tek-katman rejim 35 işlemin **TAMAMINA "BOGA" dedi ama F10'a göre HİÇBİRİ TAM_BOGA değildi** (hepsi DERIN_AYI/AYI-NOTR/TEPKI_RALLISI/NOTR-BOGA). F10+asimetrik kapı uygulansaydı: 25 işlem bloklanır (çoğu anomali-long), 10 açılır (hepsi fade-SHORT). **Sonuç: −$329.63 → +$110.49 (net +$440).** Önlenen long kaybı −$440.12; kesilen kazanan-short $0 (hiçbir short TAM_BOGA'da değildi → fade hepsi korundu). SINIR: bu turda hiç TAM_BOGA olmadı → F10'un kanıtladığı SAVUNMA (yanlış-long'u kes); HÜCUM (gerçek boğada F1-long) hâlâ test edilmedi. Script: scratchpad/f10_replay.py. Bu, F10'u tur-2'nin 1. önceliği yapan somut gerekçe.
- **TOTAL2/TOTAL3 notu (2026-07-15, kullanıcı sorusu):** Sistem TOTAL (toplam mcap) + BTC.D + ETH.D'yi zaten logluyor (piyasa_yapisi_log, günde 2×, 06-26'dan beri) → TOTAL2 = total×(1−btc_d), TOTAL3 = total×(1−btc_d−eth_d) ARİTMETİKLE türetilir, yeni veri yok. "TOTAL3 yükselirken BTC yatay" = alt-rotasyon teyidi → SEZON katmanı girdisi adayı. SINIR: derin geçmişi yok (kendi loğumuz 06-26+; ücretsiz kaynaklarda TOTAL2/3 tarihsel serisi güvenilir değil) — F10 backtest'inin BTC-verili kısmına giremez, canlı+log-sonrası ölçülür.

### DERİN BACKTEST PLANI (2026-07-12 eklendi, kullanıcı kararı) — SADECE İKİ SORU, EŞİK TARAMASI YASAK
- **Neden dar:** Tam-sistem derin backtest DÜRÜST YAPILAMAZ — karar katmanının yarısı (OI değişimi, taker oranı, top-trader L/S) Binance'te yalnız ~30 gün geriye mevcut; daha derini simüle etmek BAŞKA bir sistemi test etmektir, sonucu bizim sisteme kanıt sayılamaz. Ayrıca serbest backtest motoru = eşik-tarama cazibesi = overfit fabrikası (Karmaşıklık Bütçesi ihlali).
- **İzinli soru 1 — F10 sezon katmanı:** SEZON×HAVA tanımı yalnız BTC mumları + dominans ister (5+ yıl tam mevcut). 2021 boğası / 2022 ayısı / 2023-24 dönüşüne uygula: "bu tanım o dönemleri doğru etiketler miydi, TEPKI_RALLISI'ları yakalar mıydı?" Bu, F10 ön-koşulundaki geriye-dönük ölçümün derin hali — F10'un 1. adımıdır.
  - **SONUÇ (2026-07-22, KOŞULDU — KISMEN GEÇTİ, ÇEKİRDEK AMAÇ BAŞARILI):** SEZON=haftalık 20-ort+eğim, HAVA=1d SMA20+ölü bant %2+3g histerezis. Uç rejimler DOĞRU: 2022 %97 AYI (dominant DERIN_AYI+TEPKI_RALLISI), 2024 %71 BOGA (TAM_BOGA), **2026-şu-an %81 AYI → DERIN_AYI+TEPKI_RALLISI** (= mevcut tek-katman rejimin "BOGA" dediği yeri F10 doğru etiketliyor — SXT/BOGA_LONG −$298 felaketinin TAM çözümü). Kusur: 2023 tabanı fazla erken "TAM_BOGA" (haftalık eğim dipten dönünce; long-agresiflik için risk, fade için sorun değil). TEPKI_RALLISI ayı içinde %30 sıklık (mantıklı). Sınır: Binance perp geçmişi 2022-06'dan → 2021 tepe→ayı geçişi test edilemedi; dominans dahil değil (BTC-only). **HÜKÜM: F10 çekirdek amacını (ayı-tepki-rallisini boğa sanmayı önleme) başarıyor → tur-2'ye alınabilir (konsolidasyon şartıyla); 2023-tipi taban iyimserliği long-kapısında dikkat ister.** Script: scratchpad/f10_sezon_test.py.
- **İzinli soru 2 — fade çekirdeğinin boğa testi:** "24s'de hacim anomalisiyle +%X pump'layan coin, +4h'te SHORT'lansa +24h'te ne olur?" — chg24 + hacim anomalisi klines'tan tam kurulabilir. 2023-2025 boyunca REJİM kırılımıyla koş: fade edge'i gerçek boğada da işliyor mu, yoksa ayı hediyesi mi? (K6 boşluğunu kısmen kapatır; tam kapatamaz — taker/smart filtresi geçmişte yok, bu sınır raporda yazılır.)
  - **SONUÇ (2026-07-22, KOŞULDU — KRİTİK BULGU: HAM FADE BOĞADA ÇALIŞMAZ):** Pump=24h+%20&3×hacim, giriş+4h SHORT, çıkış+24h, son 2yıl (N=312: BOGA149/AYI125/NOTR38). **BOGA hücresi NEGATİF: medyan −0.79%, ort −3.08%, poz %46** (ort<<medyan = sağ-kuyruk: boğada pump devam edip short'u eziyor, asimetrik ölümcül risk). AYI ~0 (medyan −0.02%), NOTR hafif+ (+1.23%). Kontrolü hiçbir rejimde belirgin geçmiyor. **arsiv_analiz'in seçici (radar 45+) fade bulgusuyla (+2-3%, %60-77) ÇELİŞMİYOR, TAMAMLIYOR: fade edge'i HAM pump'ta değil SEÇİMDE (radar skoru+Pillar D+erken-kuşak). Ham +%20 pump'ı ayrımsız fade = edge değil, boğada tehlikeli.** Sınır: Pillar D geçmişte yok → seçili fade boğada nasıl bilinmiyor (K2-b bizim dönem verisi, gerçek-boğa teyidi GELMEDI). **HÜKÜM: F8 fade tur-2'de REJİM-KAPILI olmalı (TAM_BOGA'da kapalı, AYI/TEPKI_RALLISI/NOTR'da açık) VE seçili (erken-kuşak+skor, ham pump değil).** Script: scratchpad/fade_boga_test.py.
- **İzinli soru 3 — beta-rotasyon (EKLENDİ 2026-07-15, kullanıcı kararı; ETHFI/ETH gözlemi + patern araştırması "ada-değerlendirme" boşluğu):** Majör ateşleme günlerinde (BTC/ETH/SOL 1h kapanışta rolling-24h ilk kez ≥+5%, 48h dedup) yüksek-beta GECİKEN coinler sonraki 24-48h'te piyasa medyanını yener mi? **Mekanik:** beta = tetik-ÖNCESİ 60 günlük 1h getiri kovaryansı (look-ahead yok); "geciken" = tetik anında kendi chg24'ü majörünkinin yarısından az; gruplar beta-kuintili ile ÖN-SABİT; kontrol = aynı ölçüm rastgele tetiksiz günlerde (baseline); maliyet+rejim kırılımı raporlanır. Sadece klines → aynı alet. Sonuç güçlüyse tur-2'de F5, "beta-rotasyon haritası" ölçüm katmanına evrilir (KAPI DEĞİL).
  - **SONUÇ (2026-07-22, KOŞULDU — TEZ DESTEKLENMEDİ):** İki çözünürlük (günlük 3yıl BTC46/ETH92/SOL154 tetik; saatlik 9ay BTC15/ETH36/SOL45 tetik, fwd +4h/+12h/+24h). **Geciken/yüksek-beta hücresi hiçbir liderde piyasayı anlamlı yenmedi** — günlükte NEGATİF (ETH +2g excess-net −2.51%!), saatlikte gürültü-seviyesi (~0, kontrolle AYRIŞMIYOR, +24h poz %41-50 = yazı-tura). **Katlayan/yüksek-beta net NEGATİF** her yerde (−1 ila −2% excess, kovalama = tepeden alma teyidi). Yorum: "gecikme = yakında yakalar" DEĞİL "gecikme = zaten zayıf, zayıflık taşınıyor" — erken-kuşak (hacim-uyanan-long negatif) ve "anomali-long kötü" temasıyla tutarlı. ETHFI gözlemi yanlış değil (beta gerçek) ama beta≠edge. **F5 beta-rotasyon KAPI/harita adayı DÜŞTÜ.** Script: scratchpad/beta_backtest.py + _saatlik.py. Değer: mantıklı-görünen tez gerçek paraya dokunmadan elendi.
- **Kurallar:** (1) Tanım/eşik ÖNCE yazılır, tek varyant koşulur, sonuç neyse o — parametre taraması YASAK. (2) Maliyetler dahil: komisyon + funding (funding geçmişi tam mevcut). (3) N ve rejim kırılımı raporlanır; N<25-30 hücre = izlenim. (4) Dördüncü soru açılamaz — yeni soru ancak kayıtlı bir boşluğu gösterip kullanıcı kararıyla eklenir. [DEĞİŞTİ 2026-07-15: "üçüncü" → "dördüncü"; soru-3 kullanıcı kararıyla eklendi, gerekçe yukarıda]
- **SIRA (kullanıcı sorusu 2026-07-12: "değerlendirmeden sonra mı?" — EVET):**
  1. 21 Tem değerlendirme (K1-K6, mekanik) — araya HİÇBİR ŞEY girmez, backtest sonuçları karar gününden önce masaya konmaz.
  2. K4 stop düzeltmesi (koşulsuz, bağımsız).
  3. DERİN BACKTEST (soru 1 + soru 2) — **tur-2 kodu yazılmadan ÖNCE**, çünkü F10 tanımı bu ölçümle seçilir; tur-2 başladıktan sonra rejim tanımı değiştirmek "tek seferde tek değişken" ihlalidir.
  4. Ölçüm destekliyorsa F10 uygulanır (konsolidasyon şartıyla).
  5. Tur-2 sanal başlar (K1 geçtiyse gerçek-mikro pilot + veri katmanları birlikte akar).

## KARMAŞIKLIK BÜTÇESİ — major edge tezi ve sadelik ilkesi (2026-07-12, kullanıcı talebi: "bot bu kadar verinin altında boğulmasın")

**Ayrım:** VERİ/ÖLÇÜM ucuz (karar vermez, botu boğmaz — kötü kuralları öldürmek için var; yükü insana/modele düşer, o da bütçelidir). KURAL pahalı (kurallar etkileşir; SXT = 4 tek tek makul kuralın birleşiminden doğan saçmalık: kıl-payı-BOGA + geri-çekilmede-kalkan-tepe-bloğu + düşen-fiyatta-iyileşen-R/R + 4h-cooldown). Kural sayısı arttıkça beklenmedik birleşimler karesel artar.

**MAJOR EDGE TEZİ (tek paragraf — her şey buna hizmet eder ya da rafta kalır):** Aşırılığı tespit et (radar) → ayıda/tepki-rallisinde tükenişi FADE'le (KANITLI: arşiv 45+ short testi, karne AYI_SHORT 3/3, erken H2 %71 — 3 bağımsız ölçüm aynı yön) → gerçek boğada kurulu trendi pullback'te LONG'la (F1 — kanıt bekliyor, tek örnek ZEC) → risk-önce boyutlandırmayla hayatta kal. Çekirdek 4 parçadır; F10 parçalar arası ANAHTARLAMA'yı düzeltir, yeni parça eklemez. Major edge dosyaya 47. sütunu eklemekten ÇIKMAZ — muhtemelen çoktan bulundu (fade); verinin görevi onun şans olmadığını ve sınırlarını netleştirmek.

**Kurallar:**
1. Yeni karar-kuralı ancak (a) ölçülmüş bir boşluğu kapatıyorsa (K5 tipi kapı) veya (b) mevcut kuralları konsolide ediyorsa (F10 tipi) eklenir. "İyi olur" diye kural eklenmez. Her ekleme yanında bir emeklilik adayı ister.
2. Ölçüm araçları da bütçelidir: soru cevaplanınca araç emekli edilebilir (veto/erken/kacirma/arsiv_analiz zaten 4 script; yenisi ancak yeni SORU ile açılır).
3. Emeklilik adayları (21 Tem verisiyle, kullanıcı kararıyla): AYRISMA etiketi (ölçüldü, negatif-edge); hiç korumamış veto kategorileri (veto_analiz gösterirse — K3 gevşetmeye bakar, emeklilik de sadeleştirmedir); K2 iki varyantı da kalırsa erken-kuşak alarmının kendisi bile sorgulanır.
4. Alarm maliyeti dürüstlüğü: alarm "zararsız veri" değildir — insana aksiyon eğilimi bulaştırır (kanıt: ilk [ERKEN] alarmı, sistemin kendi R/R kapısının reddettiği düşük-konviksiyonlu gerçek CRCL girişine yol açtı; boyut disiplinliydi ama mekanizma kayda geçti). Alarm sayısı ve eşiği de bütçelidir.
5. F2-F7 hiçbiri major-edge tezi değildir (hepsi rafine katman); kapıları sağlanmadan implemente edilmez, tartışması yeniden açılmaz.

## Uygulama disiplini (her madde için geçerli)
1. Önce ÖLÇÜM, sonra karar entegrasyonu (erken-kuşak modeli: KAPI DEĞİL → forward-return → 25-30 olay → kapı).
2. Yeni eşik icat etme; mevcut config eşiklerini yeniden kullan veya ölçümün gösterdiği değeri al.
3. Tek seferde TEK değişken değiştir (hangi değişikliğin işe yaradığını ayırt edebilmek için).
4. Her değişiklik önce sanalda tam tur test.
5. N<25-30 = izlenim. Tek-rejim verisiyle eşik oynatma.

## ELENEN GİRİŞ FİKİRLERİ — "hareket kovalama" tuzağı (2026-07-22, ölçümle)

Kullanıcı gainers-yakalama motivasyonuyla 4 "hareket yakalama" fikri getirdi; DÖRDÜ DE ölçümde çöktü (hepsi klines forward-return, rejim kırılımı, gerçek paraya dokunmadan):
- **Beta-rotasyon** (ETH-ETHFI, lideri takip): geciken/yüksek-beta piyasayı yenmedi (negatif/gürültü). scratchpad/beta_backtest*.py
- **F4 spot-öncülük** (RE örneği): spot-baskın pump 274'te 1 (istatistiksel yok); RE uç istisna, sınıf değil. scratchpad/f4_basis_test.py
- **Trend-kırılım/breakout** (48bar direnç+hacim): +24h yukarı-long −0.38% (kontrolden kötü), **FAKEOUT %80-81** (hacimli kırılım bile 5'te 4 sahte — likidite avı). Aşağı-short ayıda +0.27% ama fakeout %81 kullanılamaz. scratchpad/trend_kirilim_test.py
- (+ erken-tespit LONG N=298 medyan −2.62%, fade-boğa ham pump BOGA negatif — daha önce)

**ORTAK DERS (sistemin kimliği):** Dört fikrin ortak yanı "hareketi KOVALA" (momentum/breakout/beta). Hepsi kripto'da fakeout/mean-reversion yüzünden kaybettiriyor. KAZANAN iki şey: (a) **fade** (aşırılığı tersine oyna — kanıtlı edge), (b) **para akışı + rejim** (durum oku — TOTAL2/3, F10). → **Sistem momentum-takipçisi DEĞİL, mean-reversion + rejim-okuyucu.** Yeni giriş fikri önerilirken bu kimlik hatırlanır: "yükseleni al" arketipleri (breakout/beta/anomali-long) ölçümde tekrar tekrar çöktü; enerji fade + rejim + (boğada) F1-pullback'e yönlendirilir. AYRIM: trend-BREAKOUT (kırılımı al, tepeden = çöktü) ≠ trend-PULLBACK (F1, geri-çekilmede al, destekten = HENÜZ AÇIK, gerçek boğa bekliyor). "Trend önemli" sezgisi ölmedi; "kırılımı kovala" versiyonu öldü.

## F11. PARA-KAPISI — TOTAL mcap trendi long-kısıtlayıcı (2026-07-23, kullanıcı kararı, Madde 9)

Kullanıcı: "kriptoya para girişi + o para nereye (alt mı majör mi) okunmalı; total 2.8T→3T ise boğa durumu var. Bunu giriş-kapısına bağla." **Onaylı tasarım değişikliği** (Madde 9 — eski kriter SİLİNMEDİ, üzerine bir long-kısıtı eklendi).
- **Tanım (`evren.para_rejim`, panel göstergesiyle ORTAK kaynak):** piyasa_yapisi_log'dan TOTAL 7g değişimi (Katman-1: kriptoya taze para?) × rotasyon (Katman-2: BTC.D↑ majöre / BTC.D↓+TOTAL3↑ alta). Ölü-bant %2 (f10 mantığı). Etiketler: PARA GİRİYOR→ALTLARA / →MAJÖRLERE / DURGUN / ÇIKIYOR.
- **Kapı (yalnız bir yön):** `PARA CIKIYOR` (TOTAL 7g ≤ −%2) iken **long-veto** (`karar_yon(..., para_cikis=True)` → mevcut long_veto zincirine eklenir). Etki gerçek olarak **BOGA-long + AYI-AAVE-istisna-long**'ta (NOTR-long zaten Faz-2'de kapalı). SHORT/fade tarafına **DOKUNULMAZ**.
- **Neden opener DEĞİL (kritik):** Tüm F10 dersi "long-gevşetme = kayıp"tı (SXT/−$298). Para-akışının long AÇMASI o hatayı tekrarlardı. Bu yüzden para-kapısı **sadece kısıtlar** (risk-off'ta long kapatır), asla açmaz. Log yok/az → None → kapı kapalı (fail-open, mevcut davranış korunur).
- **Ölçüm:** veto `long_veto` kategorisinde `detay="para-cikis..."` ile ayrışır; tur-2 sonunda "para-kapısı hangi long'ları önledi, fırsat-medyanı ne?" K3-tipi değerlendirilir. Canlı doğrulama: mock 3/3 (BOGA-long para_cikis'te None, SHORT dokunulmadı). **Not:** gerçek "PARA GİRİYOR→ALTLARA" long-teşviki HENÜZ YOK — o, opener olur, ayrı Madde-9 kararı + ölçüm ister.

## F12. TARAMA EVRENİ: kripto-only fix + genişletme (2026-07-23, kullanıcı kararı)

**Tetik:** "1 gündür poz açmıyor" → veto-forward analizi (veto_analiz.py, N=127 tur1+tur2): reddedilenlerin +24h medyanı TÜM kategoride negatif (long_veto −3.1% N=68, rr_veto −3.5% N=37, blowoff −7.8%) → **vetolar fırsat kaçırmıyor, koruyor; seçicilik sağlam.** Sonuç: aktivite artışı için doğru kaldıraç GEVŞETMEK değil, **evreni GENİŞLETMEK** (aynı bar, daha çok coin).
- **BUG bulundu (Madde 8): testbot tarama kripto-only DEĞİLDİ.** `yeni_giris_ara` `binance_pool(..., None)` çağırıyordu → `cryptos=None`, tokenize-hisse filtresi kapalı. Tam havuz 141 enstrüman, sadece 71 kripto; 41-70 bandı çoğunlukla HİSSE (SKHY/SPCX/INTC/MSTR/IBM/NVDA...). **Tur-2'nin işlemleri hisseye açılmıştı** (SKHY=SK Hynix +$3.41; ve fix anında CL=ham petrol SHORT açıktı). radar/tarayıcı `cg_universe` ile eliyordu ama testbot'ta unutulmuştu.
- **Uygulanan (kullanıcı "evet yap"):** `binance_pool("fapi", min_vol, cryptos=cg_universe)` → kripto-only (hisse elenir). Havuz config'e: `min_vol_musd` 15→**3** ($3M taban, düşük-mcap kripto anomalileri), `tarama_havuz_n` **70** (yeni anahtar; eski hardcoded [:40]). cg_universe başarısızsa o cycle kripto-only atlanır (degrade, nadir). Doğrulama: compile OK, yeni havuz kripto-only (hisse sızıntısı YOK), --durum OK.
- **KISIT bulundu (ölçüldü): analyze() ~2.0s/coin (418 ban YOK, sıralı hacim).** 40→80s, 70→140s (güvenli), 100→200s, **150→~300s = 5-dk cycle'ı taşar → çakışır/atlanır.** Kullanıcı $3M (~150 coin) istedi ama sıralı mimari 150'yi süremiyor. **Kapak GÜVENLİ 70'e çekildi** (min_vol=3 kalır: havuz $3M-derin ama [:70] volume-rank ile bağlar → efektif ~$16M taban şimdilik). Bu, crypto-only 40→70 genişletmeyi ŞİMDİ verir.
- **AÇIK (kullanıcı onayı bekliyor): düşük-mcap $3M derinliğine ulaşmak için UCUZ ÖN-FİLTRE gerekli** — 150 coini analyze() etmeden, bedava 24h ticker (chg24/hacim) ile hareket edenleri seç, sadece onları analyze() et (örn. top-volume çekirdek + top-|chg24| hareketliler). Böylece düşük-mcap pumpçıları görülür, ölü coinler atlanır, süre bütçesi korunur. Bu ayrı Madde-9 tasarım kararı (seçim mantığı değişir).

## "AKIŞ YOK" OTURUMU — 10 ölçüm, hepsi negatif (2026-08-02, kullanıcı kararıyla deftere alındı)

**Tetik:** Bot 1 haftadır işleme girmiyor. Sebep bulundu ve BUG DEĞİL: rejim 2026-07-26'da AYI→NOTR döndü. AYI dalı `smart != "LONG"` (izin verici, ~%20 geçer), NOTR dalı `smart == "SHORT"` (~%6, 30 günde SIFIR oluş) şartı koşuyor. Yani sessizlik tasarımın sonucu.

> ### ⚠ ÖLÇÜM DAMGASI — bu bloğun TÜMÜ için geçerli
> - **PENCERE-A (gölge ölçümler, 1-8):** 2026-07-03 → 08-02, 30 gün. **REJİM: yalnız TEPKI_RALLISI + DERIN_AYI.** Örneklemde **TAM_BOGA YOK.**
> - **PENCERE-B (tam-döngü backtest, 9):** 2023-01 → 2026-08, ~1.100 gün. **575 gün boğa-ailesi / 101 gün ayı** (kullanıcının "son ayı piyasası" çerçevesi ÖLÇÜMLE DÜZELTİLDİ — pencere ağırlıklı BOĞA'dır).
> - **GEÇERLİLİK:** PENCERE-B rejim kırılımı verdiği için TAM_BOGA hücresi VARDIR (N=26) ama küçüktür. **N<25-30 hücreler izlenimdir (Madde 110).**
> - **YAPISAL SINIR — en önemlisi:** `top_ls` (smart) ve `taker` Binance'te **yalnız 30 gün** geriye var. PENCERE-B'de bu iki kapı **UYGULANAMADI**. Yani tam-döngü backtest **botun kendisini değil, kalabalık-filtresi ÖNCESİ huniyi** test eder. → **"Kapılar değer yaratıyor mu?" sorusu bu blokta CEVAPLANMADI.**
> - `oi3` yok (günlük OI) → akışın ~%61'i. Spread/float_oran güncel (geçmişi yok). Hayatta-kalma yanlılığı var.

**KALİBRASYON (yayın-öncesi zorunlu kapı, Madde 106 disiplini):** Motor önce gerçeğe karşı doğrulandı. Kısmi-bar dersi TEKRAR yakaladı: canlı `olcucu.measure` **oluşmakta olan barı görür**; backtest ne tam kapanmış barı alabilir (look-ahead) ne de barı atabilir (v2 hatası) → 1m veriden yeniden kurulmalı. Bu düzeltmeyle replay motoru gerçek stopları **%0.000** sapmayla üretti (PROM/DEXE), `radar_archive` yeniden-üretimi **%83** (ilk deneme %68 = `vol_x` bir-bar kayması, `kismi_bar()` ile düzeldi). Pillar alanları **alan-başına farklı ofset** ister (`top_ls` açık kovayı günceller, `taker` yalnız kapalıyı yayınlar) — ikisi de %98. **Kalibre edilmemiş replay sonucu yayımlanmaz.**

**ÖLÇÜMLER (hepsi salt-okur, gerçek paraya/koda dokunmadan):**

| # | Soru | Sonuç |
|---|---|---|
| 1 | Vetolananlara girilseydi? (gerçek SL/TP ile) | **−$1.356,59** (N=42; TP 18'inde çalıştı, kayıplar %5 risk tavanı) |
| 2 | Radara takılıp değerlendirilmeyenler? | Negatif; risk-normalize edilince "kaçan büyük kazançlar" tezi **+$1,29**a indi |
| 3 | NOTR kapısı gevşetilse? | N=20 +$415 **ama en-iyi-2-hariç −$427** → önceden yazılı kural: **DEĞİŞİKLİK YOK** |
| 4 | `smart` kapısı gevşetilse? (127 bloklu aday) | Evren-filtreli akış N=5, +$91,93; **en-iyi-2-hariç −$361,76** → N<25, **YETERSİZ, değişiklik YOK** |
| 5 | `taker_soguma` kaldırılsa? | Negatif |
| 6 | Planlı giriş (veto fiyatından bekle)? | 34 ulaştı, **−$3.294,87**, 5/34 kazanan, piyasadan **−$1.318,80 daha kötü** |
| 7 | Başka TF daha mı iyi? | **1h optimal** (41/107 @ RRbrüt 2,00; 15m 1,82; 4h 27/107) → `olcucu.mtf_scan` kullanılmıyor, HAKLI |
| 8 | Hangi özellik kazananı önden haber verir? | `pos→RR` örneklem-dışı TUTTU (r +0,56→+0,53); **`skor` ÇÖKTÜ** (+0,59→+0,16). Ama `pos≥0.70` **boğada çöküyor** (TAM_BOGA kazanan kovası 0,45-0,70) |
| 9 | **TAM DÖNGÜ, 1.100 gün, 437 aday** | **HER REJİMDE NEGATİF:** TAM_BOGA −$2.369 (9/26), TEPKI_RALLISI −$2.777 (11/42), DERIN_AYI −$4.085 (36/115). Toplam **−$9.905,54, %30 kazanan**, en-iyi-2-hariç −$12.181 |
| 10 | Kalabalık filtresi eksik olan mı? (Coinalyze global L/S vekili) | **AYIRT ETMİYOR.** Kazanma oranı tüm varyantlarda düz: %30/%29/%30/%31/%29. Kazanan-kaybeden L/S medyan farkı **+0,128** ve **ters yönde** (kalabalık-long adaylar %31 vs kalabalık-short %25). Toplamların iyileşmesi filtreden değil **N küçülmesinden**. |

**HÜKÜM — ne söylenebilir, ne söylenemez:**
- **Söylenebilir:** Bu oturumda denenen **altı ayrı "gevşet/genişlet" varyantının ALTISI DA negatif.** Fade çekirdeği, elimizdeki hiçbir ölçümde — ne ayıda ne boğada — pozitif doğrulanmadı. **Edge'in VARLIĞINA dair pozitif kanıt yok; yokluğuna dair birikmiş işaret var.**
- **Söylenemez:** "Sistem çöp" veya "`smart` kapısı işe yaramaz." Ölçülen huni **botun kendisi değil** (kapılar geçmişte uygulanamıyor). Madde-10'un vekili botun `top_ls`'i değil (r=0,665, günlük çözünürlük).
- **Ders (Madde 120'yi güçlendirir):** Ölçüm ne zaman kapıyı gevşetmeye baksa negatif çıktı. Bu, "akış az" şikâyetinin çözümünün **gevşetme değil** olduğunu üçüncü kez söylüyor (F12 aynı sonuca evren-genişletmeyle varmıştı).

**AÇIK KALAN TEK SORU — ve neden backtest'le kapanmaz:** Değeri yaratan `taker_soguma` olabilir (canlı hunide %13 eliyordu, hiç izole test edilmedi). Ama `taker` geçmişi 30 gün → **bu soru backtest'le CEVAPLANAMAZ, yalnız ileriye dönük biriktirmeyle.** Agentic katman tasarlanırsa görevi "daha çok işlem bulmak" değil, **bu belirsizliği kapatacak veriyi disiplinli biriktirmek** olmalıdır.

**VERİ DUVARLARI (tekrar keşfedilmesin):** Binance klines →2021 · Binance `openInterestHist`/`topLongShortPositionRatio`/`takerlongshortRatio` = **30 gün** (400 hatası ~40 günde) · Coinalyze `1hour` ≈1 ay, `4hour` ≈11 ay, `daily` →2023-06 · Coinalyze `/long-short-ratio-history` = `globalLongShortAccountRatio` (botun metriğiyle r=0,665, birebir DEĞİL).

**Araçlar (scratchpad, repoya taşınmadı — kullanıcı kararı):** `veto_replay3.py` (kalibre motor) · `rejim_gecmis.py` · `pillar_gecmis.py` · `rejim_golge.py` · `planli_giris.py` · `tf_karsilastir.py` · `hipotez_test.py` · `bt_veri.py` (veri katmanı) · **`bt_kalibre.py` (zorunlu kapı)** · `bt_kos.py` · `bt_rapor.py` · `bt_ls_filtre.py`. **Hiçbiri aksiyon almaz; kapı değişikliği ayrı kullanıcı kararıdır (Madde 9).**

## ZEMİN ETÜDÜ — projenin ilk TARAFSIZ arayışı (2026-08-02, kullanıcı kararı: "tamam başla")

**Neden farklı:** Bugüne kadarki ~15 ölçümün hepsi "mevcut tasarımın şu parçası haklı mı?" diye
sordu — hepsi **denetimdi**. Bu ilk kez sistemden bağımsız soruyor: *"Bu piyasada, günler-haftalar
ölçeğinde, herhangi bir şey herhangi bir şeyi öngörüyor mu?"* Ön-kayıt sonuca bakılmadan yazıldı
(`scratchpad/ZEMIN_ETUDU_ONKAYIT.md`): 14 tahminci, 3 ufuk (7/14/30g), 5 kova, keşif|saklı zaman
bölmesi, dört ölçütlü hüküm — **hepsi koşmadan önce donduruldu, sonradan değiştirilmedi.**

> **ÖLÇÜM DAMGASI:** 507 Binance perp sembolü · günlük bar · 1.301 ölçüm günü (2023-01-01→2026-07-24)
> · gün başına ort. 218 likit coin ($3M/30g medyan hacim kapısı, geçmişe dayalı) · **keşif 2023-01→2024-12
> (ağırlıklı boğa) / saklı 2025-01→2026-08 (ağırlıklı ayı-kararsız)** · maliyet düşülmüş · piyasa-üstü.

**KALİBRASYON (zorunlu kapı, geçti):** Sızdırılmış değişken (gelecek elimize verildi) → her iki
yarıda **tekdüzelik +1,00**, yayılım +%53 / +%69. Sahte değişken (rastgele sayı) → **elendi**
(tekdüze değil, işaret döndü, maliyetten sonra negatif). **"Aletimiz negatife mi meyilli?" sorusu
doğrudan cevaplandı: HAYIR.** [Kayıt: ilk koşuda sahte kontrole ön-kayıtta OLMAYAN ayrı bir eşik
uygulanmıştı; belgedeki tanıma (gerçek tahmincilerle BİREBİR aynı kapı) dönüldü — hedef kaydırma değil.]

### BULGU 1 (en önemlisi): 10 tahmincinin 9'u İŞARET DEĞİŞTİRDİ
h=30 piyasa-üstü yayılım, keşif → saklı: 30g güç −1,46→+0,22 · 90g güç −1,82→+0,22 ·
**12ay tersine dönüş −1,81→+3,45** · oynaklık −2,22→+3,73 · 200g uzaklık −1,10→+0,61 ·
30g açık-poz +0,06→−4,41 · hacim trendi +1,46→−2,75 · listelenme yaşı +3,95→−6,46 ·
fonlama hasadı +0,36→−1,52.

**12ay tersine dönüş kritik vaka:** keşifte **kusursuz tekdüze (−1,00)**, saklıda **kusursuz tekdüze
TERS yönde (+1,00)**. Tek yarıya bakan "mükemmel edge buldum" der.

> **DERS — projenin bütün geçmişini açıklar:** Piyasanın 2023-24 kesitsel yapısı, 2025-26'nın
> aynasıdır. Beta-rotasyon, trend-kırılım, spot-öncülük, ham-fade... hepsi TEK pencerede ölçüldü.
> "Ölçtük çalışıyordu, sonra çalışmadı" = kötü şans değil, **tek pencerede ölçüp genellemek.**
> **Bundan sonra hiçbir kesitsel bulgu, zaman-bölmeli saklı-yarı teyidi olmadan bulgu sayılmaz.**

### BULGU 2: tek hayatta kalan — 30g ortalama fonlama (ama şüpheli köşede)
Dört ölçütü geçti (h=14: +0,71→+2,12 net +1,86 · h=30: +1,90→+4,91 net +4,65; tekdüze +0,90).
Yön: **yüksek fonlama → yüksek ileri getiri** (fade tezinin TERSİ). Momentum kılığı DEĞİL
(sıra korelasyonu mom30 −0,07, momentum üçte-birlerinin her birinde ayrı ayrı ayakta).
**AMA sağlama (post-hoc, sadece düşürebilir) etkiyi tek köşede buldu:** yaş üçte-birleri
keşif [+3,71 / −0,67 / −0,91], saklı [+5,33 / +0,43 / +0,02] → **etkinin tamamı EN GENÇ coinlerde**,
olgunlarda sıfır; ayrıca yüksek oynaklıkta yoğun. Bu, hayatta-kalma yanlılığının en çok şişirdiği
ve maliyet/kaymanın en yüksek olduğu köşe. → **Bulgu gerçek ama üzerine kural kurulmaz.**

### BULGU 3 (yan ürün, aranmıyordu): BOT FONLAMANIN İŞARETİNİ ATIYOR — kurulum hatası
`radar.py:110` `s_fund = clamp(abs(f)/0.05)*15 + squeeze_bonus` → **mutlak değer**: funding −0,05 ile
+0,05 aynı puanı alıyor. Üstüne `squeeze_bonus` (satır 109) **yalnız negatif** funding'e +8 veriyor.
Toplam 23 puan (skor kapısı 45) → **bot sistematik olarak derin-negatif funding'e yöneliyor.**
`dip_yakit` (satır 127) de derin-negatif funding'i "short-squeeze yakıtı" = LONG kurulumu sayıyor.
**Ölçüm tersini söylüyor:** en negatif funding kovası **her iki yarıda da en kötü** (−1,00 ve −2,35).
**Köken (git ile doğrulandı):** `d54ee05` 2026-07-07 "Faz 1-6 genişleme", asistan (Sonnet 5) tasarımı —
kullanıcı kararı değil, kurulum anında short-squeeze arama önceliğinden gelen **tasarım hatası**.
**Neden ileriye dönük teste GEREK YOK (kullanıcı tespiti, doğru):** Hayatta-kalma yanlılığı pozitif
bulguları şişirir, negatifleri şişirmez. "Yüksek funding iyi" = pozitif yarı = şüpheli.
"Derin-negatif funding kötü" = **negatif yarı = sağlam.** Yani `squeeze_bonus`/`dip_yakit`'in
kaldırılması ŞİMDİ gerekçelidir; yüksek-funding'e YENİ kural kurmak gerekçeli DEĞİLDİR. (Madde 9 —
uygulama ayrı kullanıcı kararı; eski kriter silinmez, tarihli not düşülür.)

### BULGU 4: rejim/tahsis boyutu ÖLÇÜLEMEDİ (çürütülmedi de)
B grubu (BTC 200g yapısı, piyasa geneli funding) saklı yarıda **boş kova** verdi — kova sınırları
keşiften; saklı dönem o aralığı kapsamıyor. `genişlik` N=11. → **Hüküm verilemez.** Keşif yarısı
ilginç (BTC 200g'nin çok üstündeyken ileri getiri DAHA DÜŞÜK, tekdüze −0,90; 2023 −22,7 / 2024 −6,7)
ama teyitsiz. **Not: "bir ölçek yukarı çık, rejime göre tahsis" tezi (2026-08-02 asistan önerisi)
BU ÇALIŞMAYLA DESTEKLENMEDİ — sezgiye dayanıyordu, kanıta değil. Açıkça kayda geçirilir.**

### ÖN-KAYITLI HÜKÜM
Ayakta kalan farklı tahminci: **1**. Kural: *"Etrafına TEK tahsis kuralı kurulur, başka hiçbir şey
eklenmez, sanal çalışır."* Sağlama ışığında pratik karşılığı: **kural kurulmaz, bulgu ileriye dönük
biriktirilir** (bulgunun tek zayıflığı hayatta-kalma yanlılığı ve o yanlılık ileri ölçümde yapısal
olarak imkânsız). Bu, belgedeki "sanal çalışır" maddesinin uygulanmasıdır, gevşetilmesi değil.

**Sınırlar:** hayatta-kalma yanlılığı (→ bu çalışmanın 9 negatifi SAĞLAM, 1 pozitifi ŞÜPHELİ) ·
funding/OI 294/507 sembolde · dominans-TOTAL geçmişi yok (para-akışı boyutu ölçülmedi) ·
günlük yeniden-dengeleme → ileri pencereler üst üste biniyor → t-değerleri şişkin (ölçüt olarak
kullanılmadı; koruma saklı-yarı şartıdır) · tek borsa/tek para birimi · ilişki ölçümü, nedensellik değil.

**Araçlar:** `scratchpad/ze_veri.py` · `ze_kos.py` · `ze_rapor.py` · `ze_saglama.py` ·
`ze_sonuc.json` · `ZEMIN_ETUDU_ONKAYIT.md` · `ZEMIN_ETUDU_SONUC.md`. Repoya dokunulmadı.

## TAŞIMA İŞLEMİ (delta-nötr fonlama hasadı) — "yapısal" sandığım şey yine MEVSİM çıktı (2026-08-03)

**Tez (asistan, iddialı kuruldu):** "Vadeli piyasa kalıcı olarak long tarafta kalabalık (top_ls
medyanı 1,58). Spot'tan al + aynı büyüklükte perp short → fiyat nötr, her 8 saatte kira topla.
Bu mevsim değil balık; karşı tarafta kimin durduğunu ve neden ödemeyi kesemeyeceğini
söyleyebildiğim TEK şey." **Ölçüm bu tezi ÇÜRÜTTÜ.**

> **DAMGA:** 351 sembol · Binance'in **gerçek 8 saatlik fonlama ödeme kayıtları**
> (`fapi/v1/fundingRate`; Coinalyze günlük yaklaşımı DEĞİL) + spot & perp günlük fiyat ·
> 43 ay (2023-01→2026-07) · keşif 2023-01→2024-12 / saklı 2025-01→2026-08 ·
> maliyet DEVİR bazlı %0,16 tek yön · ön-kayıt `scratchpad/TASIMA_ONKAYIT.md`.

**HEDGE DOĞRULANDI (yayın şartıydı):** baz terimi yıllık **−0,07 / −0,16 / −0,02%** — ön-kayıt
sınırı %3'tü. İki bacak gerçekten birbirini götürüyor → "fiyattan bağımsız" iddiası geçerli.

| Varyant | Keşif | Saklı | Hüküm |
|---|---|---|---|
| V1 BTC+ETH (sürekli) | +9,84%/yıl | **+3,53%** | AYAKTA (kıl payı — aşağıya bak) |
| V2 fonlaması en yüksek 10 (aylık) | +9,52% | **−8,41%** | DÜŞTÜ (+ devir maliyeti %2,82/yıl) |
| V3 tüm uygunlar (sürekli) | +7,42% | **−13,61%** | DÜŞTÜ |

### ASIL BULGU: fonlama taşıması REJİME BAĞIMLI
Saklı dönemde geniş piyasada **ayların %89'unda fonlama NEGATİF** (V3). Yani ayı piyasasında
kalabalık long değil SHORT tarafta → ödeme yönü tersine dönüyor, kira toplayan kira ÖDÜYOR.
**"Perp piyasası yapısal net-long" iddiası altcoinler için YANLIŞ; boğa dönemi olgusu.**
(Not: 1,58'lik top_ls ölçümü 30 günlük tek pencereydi — aynı hata, üçüncü kez.)

### YAN BULGU (ileride işe yarayabilir): BTC/ETH ALTLARDAN AYRIŞIYOR
Majörlerde fonlama saklı dönemde bile ayların **%84'ünde pozitif** kaldı (altlarda %11).
Yorum: BTC/ETH'de altlarda olmayan kurumsal long talebi (baz işlemi, ETF hedge) var.
**Ama getiri eriyor: %9,84 → %3,53 (sermaye payı düzeltilince %2,83)** — koyduğum %6 eşiği
tam da borsa/karşı-taraf riskini karşılasın diyeydi; bugün ödediği o eşiğin yarısı.

### ÖN-KAYIT TUTARSIZLIĞI (sonucu gördükten sonra fark edildi, saklanmıyor)
Bu çalışmanın kuralı "toplam ≥%6 **ve** iki yarıda da pozitif" → V1 GEÇER.
Zemin etüdünün kuralı "saklı yarı keşfin **en az yarısı** kadar" → V1 **DÜŞER** (3,53 < 4,92).
**Cevap hangi standardı uyguladığına duyarlı → bu kadar kıl payı olan şey edge değildir.**
Bundan sonra tek standart: **saklı ≥ keşfin yarısı** (daha sert olan).

### DERS (üçüncü tekrar)
Bu oturumda "yapısal/kalıcı" diye kurulan üçüncü iddia da mevsim çıktı (1: fade edge'i,
2: kesitsel kalıplar, 3: fonlama taşıması). **Kural: "yapısal" kelimesi, iki farklı rejimde
ölçülmeden kullanılmaz.** Tek pencerede ölçülen hiçbir şey "piyasanın doğası" diye anlatılmaz.

**Araçlar:** `scratchpad/ze_tasima_veri.py` · `ze_tasima.py` · `ze_tasima_sonuc.json` ·
`TASIMA_ONKAYIT.md`. Repoya dokunulmadı, commit yok.

## YAPISAL ELEME ÖLÇÜMÜ — "hangi coin" sorusunun büyüklüğü ölçüldü (2026-08-03)

**Bağlam:** Kullanıcı birinci-ilke sorularını sordu (coin neden yükselir, kurumsal/bireysel,
para nerede kazanılır, işlevin fiyata etkisi). Buradan `SISTEM_TASARIM_v2.md` çıktı; kalbi
**Katman-2 ELEME** olacaktı ("eleyen kural sağlam, seçen kural kırılgan" — pozitif bulgularımızın
hepsi çöktü, negatiflerin hepsi ayakta kaldı). İki eleme kuralı ölçüldü.
Ön-kayıt: `scratchpad/YAPI_ONKAYIT.md`. **Soru ortalama değil SOL KUYRUK'tu:** felaket kaybı olasılığı.

> **DAMGA:** 507 perp sembolü · coin başına dönem başına TEK gözlem (ilk uygun günden **sabit
> 365 gün** ileri, üst üste binme yok) · keşif 2023-01→2024-12 (N=172) / saklı 2025-01→2026-08
> (N=376) · E1 = toplam/dolaşan arz (CoinGecko, BUGÜN) · E2 = yıllık ücret ≥ $1M
> (DefiLlama; zincirler `/v2/chains` ile eklendi — bu düzeltme olmadan ETH/SOL/BTC "gelir yok"
> damgası yiyordu) · felaket eşiği −%80, ön-kayıtta sabit.

### ⭐ ASIL BULGU — FELAKETİN TEMEL ORANI (oturumun en büyük sayısı)

| Dönem | 365g'de −%80 | −%50 | fiili ölüm (likiditeden düşme) |
|---|---|---|---|
| **2023-01→2024-12 (boğa)** | **%1** | %5 | %4 |
| **2025-01→2026-08 (ayı)** | **%46** | %85 | %41 |

**Boğada hiçbir şey ölmüyor; ayıda her iki coinden biri bir yılda %80 eriyor.**

### E1 SEYRELTME — ÖLDÜ
Fark **−4,2 puan** (yanlış yönde, sıfır). Sebep açıklayıcı: **memecoinlerin seyreltmesi 1,00**
(hepsi zaten dolaşımda, kilit açılımı yok) ve %52'si öldü. **"Gelecek arz baskısı yok" hiçbir
koruma sağlamıyor.** → Eleme kuralı olarak **sisteme GİRMEZ.**

### E2 DEĞER YAKALAMA — VAR AMA EŞİĞİN ALTINDA, TEK PENCERE
Geliri yok: P(−%80)=**%50**, medyan −%79,9 · Geliri var: **%32**, medyan −%72,5 → **17,8 puan.**
Karıştırıcı testlerini büyük ölçüde geçti (yaş 21/18/11 · büyüklük 18/8/10 · oynaklık 20/16/15
— her dilimde var, "sadece küçük/genç coin" değil). **Yine de GİRMEZ:** (1) ön-kayıt eşiği 20 puandı,
(2) tek pencere — keşif yarısında ölçülemedi, (3) **geliri olanların da %32'si %80 kaybetti,
medyanı −%72 → gelir koruma değil, sadece daha az felaket.**

### KONTROL BENİM ÖN-KAYIT HATAMI BULDU (kayda geçer)
Sızdırılmış kontrol keşif yarısında ayrıştıramadı — çünkü orada **ayrışacak sol kuyruk yok**
(temel oran %1). Saklı yarıda %100 vs %0 ile kusursuz ayrıştırdı → **boru hattı sağlam.**
Hata bendeydi: bir yarıda hiç gerçekleşmeyen bir olay için "her iki yarıda da ayrışsın" şartı
koymuştum. Çalışma ön-kayıtlı haliyle **koşulamaz**; sonrası KEŞİFSEL etiketiyle raporlandı.

### ⭐ TASARIM SONUCU — Katman-2 çöktü, Katman-1 büyüdü

| Karar | Ölçülen değeri |
|---|---|
| **Ne zaman piyasada olduğun** (rejim) | %1 → %46 = **45 puan** |
| **En iyi coin filtresi** (gelir) | %50 → %32 = **18 puan**, üstelik teyitsiz |

> **Hangi coini tuttuğun, ne zaman tuttuğunun yanında önemsiz kalıyor.**
> Mükemmel bir coin filtresi bile rejim kararının **üçte birini** ediyor.

**SISTEM_TASARIM_v2'nin kalbi olarak önerilen ELEME katmanı, kendi ilk testinde büyük ölçüde
çürüdü.** Ayakta kalan, zaten kanıtlı olan Katman-1'dir. Asistan tahmini ("E2 geçer, E1 sınırda")
**iki maddede de iyimser yönde yanlış** çıktı — kayda geçer.

**Araçlar:** `scratchpad/ze_yapi_veri.py` · `ze_yapi.py` · `ze_yapi_sonuc.json` ·
`YAPI_ONKAYIT.md` · `SISTEM_TASARIM_v2.md`. Repoya dokunulmadı, commit yok.

## SKOR OTOPSİSİ — "60+ skoru hangi parça üretti, o parça haklı mıydı?" (2026-08-03)

**Kullanıcı sorusu:** *"Botun 60 ve üzeri skor gösterdiği coinleri tek tek incelesek, aslında
gerçek skorun kaç olduğunu bulsak — neden o skoru verdi, nerede ölçüm mantığı yanlıştı."*
Bu, 18 ölçümden **farklı bir soru**: "skor işe yarıyor mu" değil, **"skorun hangi parçası bozuk".**
Teşhis, edge avı değil.

> **DAMGA:** `radar_archive.jsonl` 101.926 kayıt · **41 gün (2026-06-24 → 08-03), YALNIZ AYI** ·
> skor≥60 → 648 kayıt → **125 EPİZOT** (aynı sembolde 4 saat içi tek olay sayıldı; CFX tek başına
> 30 kez görünüyordu) · ileri getiri 1h klines · **KALİBRASYON: skor arşiv alanlarından yeniden
> üretildi, sapma medyan 0,000** → parçalama güvenilir.

### BULGU 1 — Skor beş faktörlü bileşke DEĞİL, bir AÇIK-POZİSYON DEDEKTÖRÜ

| Parça | Ort. katkı | Tasarım kapasitesi | Payı | Baskın olduğu epizot |
|---|---|---|---|---|
| **OI** | **30,8** | 35 | **%46** | **115/125 (%92)** |
| HACIM | 16,3 | 20 | %24 | 3 (%2) |
| FUND | 15,3 | 23 | %23 | 7 (%6) |
| **SIKIŞMA** | **0,7** | 20 | **%1** | **0** |
| KIRILIM | 3,7 | 15 | %5,5 | **0** |

**Tasarımın üçte biri (sıkışma 20p + kırılım 15p) fiilen çalışmıyor** — 35 puanlık kapasiteden
4,4 puan üretiyor. İkisi de **emeklilik adayı** (Madde 99: her ekleme bir çıkarma ister).
**Ayrıca OI DOYUYOR:** epizotların %69'u oi24≥%20 kırpma eşiğinin üstünde → skor %20 ile %200'ü
AYNI sayıyor. Halbuki oi24>60 grubu en iyi sonucu verdi (R=+0,86) → **kırpma bilgi çöpe atıyor.**

### BULGU 2 — İşaret ters: skor "yükseliş öncüsü" diyor, ölçüm "düşüş" diyor

| | +4h | +24h | +72h | +72h pozitif |
|---|---|---|---|---|
| **skor 60+** (N=125) | −0,85% | −3,57% | **−6,78%** | **%23** |
| **KONTROL skor<45, aynı günler** (N=499) | −0,15% | −0,64% | −1,02% | %42 |

Kontrol grubu şart: ayı piyasasındayız, "düştü" tek başına anlamsız. **Fark gerçek: 5,8 puan.**
Skorda bilgi VAR, etiketi yanlış.

### BULGU 3 ⭐ — BOT EN ZAYIF BANTTA ÇALIŞIYOR (en aksiyon alınabilir bulgu)

> **⚠ DÜZELTME (2026-08-03, aynı gün, stop otopsisi sırasında yakalandı):** İlk yol testi
> **yalnız KAPANIŞ** fiyatına bakıyordu. Stop mumun **FİTİLİYLE** tetiklenir — kapanışla ölçmek
> stop oranını sistematik olarak **düşük** gösterir (%41,9 yerine gerçek %58,1). İlk raporlanan
> R değerleri (+0,16 / +0,32 / +0,58) **FAZLA İYİMSERDİ, GEÇERSİZDİR.** Aşağıdaki tablo
> fitil bazlı ve `olcucu`'nun GERÇEK stop yerleşimiyle yeniden koşuldu. **Ders: yol testi
> her zaman high/low ile yapılır; kapanış-bazlı dokunma testi yayımlanmaz.**

Yol testi (SHORT, `olcucu`'nun gerçek stopu, hedef=2×risk, 72 saat, **fitil bazlı**):

| Bant | Hedefe | Stopa | Ort. R |
|---|---|---|---|
| kontrol <45 (N=1277) | %31,9 | %66,0 | **−0,02** |
| **45-60 ← BOTUN KAPISI** (N=302) | %32,5 | %58,3 | **+0,10** |
| **60+** (N=124) | %38,7 | %58,1 | **+0,20** |

Sıralama tekdüze — skorda bilgi var, ama büyüklük ilk sandığımın **üçte biri**.
Maliyet (~0,04R) düşülünce botun bandı **+0,06R** kalıyor: pozitif ama çok ince.
**Not:** Botun canlı karnesi (6 işlem, ort R −0,67) bu ölçümü ÇÜRÜTMEZ — N=6 ile
+0,10'dan ayırt edilemez. İkisi çelişmiyor, canlı örneklem yok denecek kadar küçük.

**60+'ta hedef stopu geçiyor; botun fiilen işlem yaptığı 45-60'ta stop hedefi geçiyor.**
Skor çalışıyor ama kapı, bilginin en zayıf olduğu yere konmuş.
**EŞİK YÜKSELTİLMEDİ** — 41 gün, tek rejim, bantlar tekdüze değil (45-50:+0,31, 50-55:+0,23,
55-60:+0,47). Tek pencereye göre eşik oynatmak 18 kez yanıltan desendir. **Boğa verisi bekler.**

### BULGU 4 — `squeeze_bonus`: KALDIRILDI, sonra GERİ ALINDI (asistan muhakeme hatası)
Aynı gün içinde üç adım, hepsi kayıtlı:
1. **Kaldırıldı** — gerekçe: premis ("negatif funding = yukarı squeeze yakıtı") iki ölçümle çürük.
2. **Otopsi ölçtü** — 60+ bandında: bonus ALAN hedef %58,7 / stop %31,7 → **R=+0,89**;
   ALMAYAN hedef %36,1 / stop %52,5 → R=+0,25. Botun bandında (45-60) fark NÖTR (+0,30 vs +0,32).
3. **Geri alındı** (kullanıcı "evet al").

> **DERS (asistan hatası, tekrarlanmasın):** *"Premis yanlış"* ile *"kural zararlı"* aynı şey DEĞİL.
> Premis gerçekten yanlıştı (yukarı squeeze değil), ama kural **düşecek coinleri** işaretliyordu ve
> **bot bu skoru SHORT için kullanıyor (6/6 işlem SHORT)** → "long için en kötü kova" =
> "short için en iyi kova". **Bir kuralı kaldırmadan önce onun FİİLİ etkisi ölçülür, gerekçesi değil.**

**Kalan düzeltme (doğru ve yerinde):** `dip_yakit` ve dokümantasyon artık "squeeze yakıtı = alım"
demiyor, **UYARI** diyor. Etiketin hesabı korundu (arşiv sürekliliği).
**SINIR:** hepsi 41 gün, yalnız AYI. Boğaya girildiğinde `squeeze_bonus` YENİDEN ölçülmeli — koda not düşüldü.

### OTOPSİ-2: STOP YERLEŞİMİ (`olcucu.measure` SHORT dalı) — hipotezim ÇÜRÜDÜ
Ön-kayıt: üç SABİT varyant, eşik araması yok. A=min(adaylar) **botun bugünü** (F9 2026-07-22
"girişe en yakın") · B=medyan · C=max (~1,5×ATR, F9 öncesine yakın). Hedef=2×risk, R cinsinden.

| Varyant | Stop mesafesi | skor 60+ | botun bandı 45-60 |
|---|---|---|---|
| **A = min (BOT)** | %2,80 | **+0,20** | **+0,10** |
| B = medyan | %5,00 | +0,10 | +0,11 |
| C = max (~1,5×ATR) | %7,71 | +0,08 | +0,07 |

**"F9 stopu fazla daralttı" hipotezi REDDEDİLDİ** — genişletmek daha kötü. Mekanizma: geniş stopla
daha az stop yeniyorsun (%39,5 vs %58,1) ama hedefe de hiç varamıyorsun (%15,3 vs %38,7).
**Ek kontrol (post-hoc): akıllı yerleşim, aynı mesafedeki SABİT yüzdeyi 60+'ta yeniyor**
(+0,20 vs +0,09), botun bandında berabere. → `olcucu`'nun yerleşim mantığı hakkını veriyor.
A'da seçilen aday kaynağı: yapısal %39 · nbar %21 · ATR-fallback %40.

### OTOPSİ-3: `stage` ETİKETİ — amiral gemisi etiket EN KÖTÜ hücre
`radar_active`'in asıl kapısı hiç denetlenmemişti. Aynı fitil-bazlı yöntem:

| stage | N | HEDEF | STOP | ort R |
|---|---|---|---|---|
| **BASLIYOR** (vol_x>2,5 & last1>2 & oi3>3) | 69 | %30,4 | %69,6 | **−0,09** |
| **HAZIRLANIYOR** (comp<0,65 & \|last3\|<4 & oi24>8) | 162 | %37,0 | %56,8 | **+0,19** |
| izle | 796 | %33,9 | %62,4 | +0,07 |

**"Hareket başlıyor" etiketi, short için NEGATİF.** Mantıklı: taze pump'ın içine short atıyorsun,
momentum stopu alıyor (TLM/MANTA dersinin simetriği). **"Hazırlanıyor" (sıkışmış + fiyat yatay +
pozisyon birikiyor) en iyi hücre** ve skordan BAĞIMSIZ ayırt ediyor: skor<45 içinde bile
HAZIRLANIYOR +0,22 vs izle +0,01 (N=116). Alt-bant kırılımları gürültülü (skor 60+ izle N=25
R=+0,68 = küçük örneklem aykırısı, güvenilmez). **Aksiyon alınmadı** — 41 gün, tek rejim.

### OTOPSİ-4 ⭐ — BOYUTLANDIRMA "RİSK-ÖNCE" DEĞİL, "MARJİN-ÖNCE" (en somut bulgu)
Sistem kendini "risk-önce boyutlandırma" diye tanımlıyor. Kod öyle yapmıyor:
```
marjin   = equity × marjin_pct(skor)        # %8-12, stoptan BAĞIMSIZ
notional = marjin × kaldirac(skor)          # 3-10x, stoptan BAĞIMSIZ
risk_usdt = stop_frac × notional            # <- risk BURADA ORTAYA ÇIKIYOR
if risk_usdt > equity×%5: kucult            # yalnız TAVAN kırpılıyor
```
**Risk hedeflenmiyor, sonuçta oluşuyor.** Gerçek risk-öncede `notional = hedef_risk / stop_frac`
olurdu: geniş stop → KÜÇÜK pozisyon, dolar riski SABİT. Burada tersi: **geniş stop → BÜYÜK risk.**

7 gerçek işlemden türetilen kanıt (risk = sonuc_usdt / r):

| İşlem | Skor | Kald. | Türetilen stop | **Dolar riski** | Sonuç |
|---|---|---|---|---|---|
| PROM | 54,3 | 5 | %1,5 | **$70** | −$72 |
| AKE | 48,2 | 6 | %2,3 | **$115** | −$118 |
| DEXE | 46,5 | 3 | %7,2 | **$178** | −$179 |
| **BLESS** | 72,3 | 9 | **%7,5** | **$483** | **−$488** |

Hepsi R≈−1,0 — yani R muhasebesi tutarlı görünüyor **ama dolar etkisi 7 KAT değişiyor** ($70→$483).
Ve farkı yaratan şey konviksiyon değil, **stop mesafesi** — ki o bir konviksiyon sinyali değil,
mekanik bir çıktı. En büyük kayıp (BLESS −$488) en geniş stoplu işlemden geldi.
**Bu bir tasarım-davranış çelişkisidir (Madde 8 adayı: belgelenmiş davranışı geri getiren onarım).**
~~Düzeltme YAPILMADI — ayrı kullanıcı kararı~~ ama R/R≥2 kapısı ve %5 tavanı bu haliyle
"her işlem eşit risk" garantisi VERMİYOR, bunu bilerek karar verilmeli.

> **DURUM GÜNCELLEMESİ (2026-08-10): ONARIM YAPILDI ve DOĞRULANDI.** Yukarıdaki "düzeltme
> yapılmadı" satırı ESKİDİ: onarım aynı gün (2026-08-05, commit `efa8785`) koda girdi —
> `notional = hedef_risk / stop_frac`, kaldıraç artık girdi değil ARAÇ. `benim.py` de aynı
> fonksiyonu çağırdığı için ikinci kasa da otomatik kapsandı.
>
> **DOĞRULAMA (replay, 10 kapanan gerçek işlem, `scratchpad/o4_dogrulama.py`):** iki formül
> aynı girdilerle yeniden hesaplandı. Replay ESKİ formülü birebir yeniden üretti (PROM $70,
> AKE $115, DEXE $178, BLESS $483 → **6,9×** yayılma; defterdeki "7 KAT" ifadesiyle tutarlı,
> yani replay güvenilir). YENİ formülle yayılma **3,5×**'e indi.
>
> **KALAN YAYILMA TAMAMEN GÜVENLİ YÖNDE ve sebebi ÖLÇÜLDÜ:** maksimum notional =
> equity × marjin_pct(≤%12) × kaldıraç_max(10) = **1,2 × equity**. Yani %5 hedef riske
> ulaşmak için stop ≥ **%4,17** olmalı (replay o dönemin `islem_risk_pct`=5 ayarıyla
> koşuldu; config bugün **3** → eşik **%2,5**'e iner, mekanizma aynı kalır);
> daha DAR stoplu işlemler hedefin altında kalıyor
> (PROM %1,48 → $139 = %1,4 risk; GRVT %1,37 → $151). Eski hatanın yönü (geniş stop → BÜYÜK
> risk) TERSİNE döndü: artık geniş stop tam hedefte tavanlanıyor, dar stop hedefin altında.
> **AÇIK KARAR (kullanıcıya):** dar stoplarda hedefe ulaşmak için `marjin_pct` yükseltilsin mi?
> Öneri: HAYIR — %5/işlem zaten agresif, eksik-risk güvenli yön, ve bu yeni bir kural eklemek
> olur (Karmaşıklık Bütçesi). Kayda geçsin diye yazıldı, kendiliğinden uygulanmayacak.

**Araçlar:** `scratchpad/sk_anatomi.py` · `sk_sonuc.py` · `sk_kontrol.py` · `sk_yol.py` · `sk_bant.py`
· `st_otopsi.py` · `st_kontrol.py` · `sg_otopsi.py`.
**Yöntem dersi:** Bu otopsi 41 günlük mevcut arşivden, yeni veri çekmeden, 18 backtest'ten daha
fazla aksiyon alınabilir bulgu üretti. **Sebep: "yeni edge var mı" değil "elimizdeki alet ne yapıyor"
diye sordu.** Bundan sonra yeni arayışa çıkmadan önce mevcut bileşenlerin otopsisi yapılır.

## ⭐ BOĞA BACAĞI ÖLÇÜMÜ — F1 trend-pullback, gerçek boğalarda test edildi (2026-08-10)

**Neden:** `kazanan-bot-arastirma-raporu.md` §8 adım 1. Sistemin tek elenmemiş long arketipi F1'di
("kurulu trendde geri çekilme alımı"); breakout/beta/anomali-long zaten ölçümde çökmüştü. Elimizde
gerçek boğa verisi olmadığı için (K6 boşluğu) tek doldurma yolu geçmiş boğalarda test.

**ÖN-KAYIT (sonuca bakmadan yazıldı, tek varyant, eşik taraması yok):**
Trend = kapanış>MA200 **ve** MA50>MA200 · Tetik = günün düşüğü ≤ MA50 **ve** kapanış > MA50 ·
Giriş = ERTESİ günün açılışı · Stop = son 5 günün dibi − 0.25×ATR14 (F9 mantığı) · Hedef = 2×risk
(botun R/R≥2 kapısı) · Süre ≤30 gün · aynı gün stop+hedef → **STOP** sayılır (muhafazakâr) ·
Maliyet: %0.09 gidiş-dönüş + %0.03/gün funding vekili. Evren: 25 büyük alt + BTC, 2019→bugün.
**Hipotez:** boğada net ort R > +0.20 **ve** kontrolü belirgin geçer; ayı/nötrde edge kaybolur.
**Kontrol grubu:** her sinyal için aynı sembolde ±60 gün içinde rastgele bir gün, aynı mekanik.

| Dönem | N | kazanma | F1 ort R_net | **KONTROL ort R_net** |
|---|---|---|---|---|
| 2020-21 BOĞA | 132 | %45 | +0.299 ±0.122 | **+0.260** |
| 2022 AYI | 31 | %39 | +0.072 ±0.244 | **+0.127** |
| 2023-24 BOĞA | 170 | %39 | +0.071 ±0.102 | **+0.120** |
| 2025-26 (şimdi) | 62 | %16 | **−0.531** ±0.135 | −0.468 |
| **TOPLAM** | **410** | %37 | **+0.046 ±0.067** | **+0.062** |

### ⭐ HÜKÜM: HİPOTEZ REDDEDİLDİ — F1 kontrolü GEÇEMEDİ
Dört dönemin **üçünde kontrol F1'e eşit ya da ÜSTÜN**. Toplamda rastgele giriş (+0.062) kuralı
(+0.046) yeniyor. **Boğa dönemlerindeki artı R, kuralın seçiciliğinden değil DÖNEMİN kendisinden
geliyor** — yani ölçtüğümüz şey edge değil **beta**. 2020-21'de +0.299 gibi "iyi" bir sayı çıkması
tam da kontrolün neden zorunlu olduğunu gösteriyor: kontrol olmasaydı bu tablo "F1 boğada çalışıyor"
diye okunur ve gerçek paraya girerdi.

**Rejim kırılımı (F10 etiketi, giriş günü — kontrol de aynı etiketle bölündü):**

| F10 hücresi | F1 (N) | F1 ort R_net | kontrol (N) | kontrol ort R_net |
|---|---|---|---|---|
| **TAM_BOGA** | 186 | **+0.130** ±0.099 | 169 | **+0.005** ±0.103 |
| BOGA_DUZELTME | 78 | +0.032 | 73 | **+0.280** |
| TEPKI_RALLISI | 11 | +0.744 | 14 | +1.411 |
| DERIN_AYI | 23 | −0.221 | 23 | −0.441 |
| BELIRSIZ | 112 | −0.098 | 131 | −0.043 |

**Tek savunulabilir hücre TAM_BOGA** — F1 kontrolü +0.125R geçiyor. AMA birleşik standart hata
≈0.14 → t≈0.9, **istatistiksel olarak anlamlı DEĞİL**. Dürüst ifade: *işaret doğru yönde, kanıt yok.*
BOGA_DUZELTME'de F1 kontrolden BELİRGİN kötü (+0.032 vs +0.280) — "düzeltmede pullback al" fikri
bu veriyle desteklenmiyor. F10'un long'u yalnız TAM_BOGA'da açma tasarımı bu tabloyla TUTARLI
(DERIN_AYI ve BELIRSIZ negatif), ama F10'u long tarafında haklı çıkaran şey F1 değil, F1'in
DIŞINDAKİ hücrelerin kötülüğü.

**YAN BULGU (kayda değer):** TAM_BOGA'da rastgele girişin ortalaması +0.005R, yani ~sıfır — buna
karşılık 2020-21 boğasının TAMAMINDA rastgele giriş +0.260R. Demek ki "boğada her giriş kazanır"
da doğru değil; kazandıran şey 2R hedef + dar stop mekaniğinin o dönemki trend yapısına denk
gelmesi. **Boğa bacağının cazip görünen "sadece beta al" versiyonu bile ölçülmeden alınamaz.**

**Şu anki dönem (2025-26) her iki grupta da sert negatif (−0.53 / −0.47)** → mevcut piyasada
long tarafı sistematik olarak cezalandırıyor; sistemin fade kimliğiyle tutarlı.

**SINIRLAR (dürüstlük, hükümle birlikte okunur):**
1. **Hayatta kalma yanlılığı:** evren bugün yaşayan büyük altlardan seçildi → long lehine YUKARI yanlı.
   Yanlılık F1'in *lehine* olduğu halde F1 yine de kontrolü geçemedi — bu, hükmü ZAYIFLATMAZ, güçlendirir.
2. Spot mumlar; funding gerçek geçmiş değil, muhafazakâr vekil (%0.01/8s).
3. Botun kapıları (radar skoru, Pillar D, taker) geçmişte YOK → bu test **saf arketipi** ölçer,
   botun seçiciliğini değil. "Seçili F1 boğada ne yapar" hâlâ bilinmiyor (skor otopsisinin
   "edge HAM sinyalde değil SEÇİMDE" dersinin long simetriği — açık boşluk).
4. Parametre araması yapılmadı (MA50/MA200/ATR14/2R hepsi konvansiyonel, önceden sabit) →
   optimize edilecek şey olmadığı için klasik walk-forward anlamsız; onun yerine tüm dönemler
   ayrı raporlandı, yani her dönem zaten örnek-dışı. Overfit kanalı kapalı.

**Script:** `scratchpad/boga_bacagi_test.py` (ön-kayıt dosyanın başında, mum önbelleği diske).

**NE DEĞİŞTİ / NE DEĞİŞMEDİ:** Koda HİÇBİR ŞEY girmedi. F1 rafta kalmaya devam ediyor,
"kanıtlı" statüsüne yükselmedi. Araştırma raporunun A/B yol haritası (fade+trend portföyü)
**bu ölçümle askıya alındı**: trend bacağı için elimizde hâlâ kanıtlanmış bir kural YOK.
Rapor §8 adım 2 ("kazanıyorsa birleştir") koşulu SAĞLANMADI.

**DERS (beşinci tekrar, artık desen):** Mantıklı görünen giriş arketipi + iyi görünen boğa
sayısı + kontrol grubu = fikir ölür. Kontrolsüz aynı tablo canlıya girerdi. Kontrol grubu bu
projede en ucuz ve en çok para kurtaran alet.

## ALT/BTC PARİTESİ ÖLÇÜM KATMANI — sisteme girdi (2026-08-10, kullanıcı tekniği)

**Ne:** `evren.alt_btc(sym)` — coinin BTC'ye karşı 24s/7g/30g getirisi + yorum etiketi
("GERÇEK GÜÇ" / "liderlik soğuyor" / "BTC-BETASI TUZAĞI" / "zayıf"). Panelde coin sayfasında
ayrı bir şerit olarak görünür; `piyasa_yapisi.py` artık **breadth_30g** ve **lider_30g** listesini
de loglar (sürdürülebilir liderliğin ileriye dönük getirisi ancak seri birikirse ölçülebilir).

**Neden burada:** Kullanıcının deneyimle doğrulanmış çerçevesi (2026-06-25): "USD'de yeşil ama
BTC'ye karşı kırmızı" tuzağı — USD kazancı sadece BTC betası olabilir; gerçek alfa altın BTC'yi
GEÇMESİDİR. Dominans tarafı (BTC.D/USDT.D/breadth/altseason kontrol listesi) zaten sistemdeydi
(`piyasa_yapisi.py` + panel para-akışı + F11 para kapısı); eksik olan tek-coin parite ölçümüydü.

**KAPI DEĞİL — bilinçli:** hiçbir karar fonksiyonu okumaz. Kısa pencere (3 saatlik göreli güç =
eski AYRIŞMA etiketi) ölçüldü ve **negatif-edge** çıktı; bu yüzden kasıtlı olarak yalnız 7-30 gün
var. Kapı tartışması ancak 25-30 olayda forward-return biriktikten sonra açılır (erken-kuşak modeli).

**Sadeleştirme yan etkisi:** `daily`/`rel` formülleri `piyasa_yapisi.py` içinde kopyaydı; panel de
aynı ölçümü göstereceği için `evren.py`'ye taşındı (bu projenin tekrarlayan hatası: kopyalanan
formül drift eder — evren.py'nin varlık sebebi zaten buydu).

> **ÖLÇÜM SCRIPTLERİ ARTIK REPODA (2026-08-10):** Defterdeki eski `scratchpad/*.py` atıfları
> (f10_replay, fade_boga_test, beta_backtest, sk_*/st_*/sg_* otopsileri) **geçici oturum
> klasöründe kalıp KAYBOLDU** — yani o ölçümler bugün yeniden koşulamıyor, yalnız sonuçları
> kayıtlı. Bu oturumdan itibaren ölçüm scriptleri projedeki `scratchpad/` klasörüne yazılır ve
> commit edilir (mum önbelleği gitignore'da). Ön-kayıt scriptin başında durur; sonuç defterde.

## ⭐ GÖLGE DEFTER — "bot girmediği sürece ölçemeyiz" sorununun çözümü (2026-08-10, kullanıcı kararı)

**TEŞHİS (kullanıcı sorusu "bot neden işleme girmiyor"):** Bot çalışıyordu — 7 günde 1141 tur,
234 yön kararı/veto — ama **3 gündür hiç işlem açmamıştı** (son giriş KGEN LONG, 07 Ağu 19:30).

Huni (2026-08-03 → 08-10, 6754 aday kaydı): blowoff 65 · taker_soguma 46 · btc_pay_freni 43 ·
long_veto 26 · **LONG/ONAY_BEKLE 33 (hiçbiri onaylanmadı)** · **SHORT/ANINDA 21 (hiçbiri açılmadı)**.

**İKİ AYRI KÖR NOKTA BULUNDU:**

1. **`yeni_giris_ac`'ın retleri SESSİZDİ** (rr_veto hariç). 08-08'de KMNO **19 kez** SHORT kararı
   aldı, 19'u da giriş kapısında öldü; panelde "SHORT/ANINDA" yazıyordu, sanki girmiş gibi.
   Gerçek sebep: NET R/R 0.19 < 1:2. Üstelik veto logunun 12 saatlik tekrar-yazma engeli yüzünden
   19 redden yalnız **1'i** loga düştü → hem sebep hem sıklık görünmezdi.
   **Onarım:** `yeni_giris_ac(..., red_out=[])` — ret sebebi `{kapı, detay, yön, ölçüm}` olarak
   döner (`olcum_hatasi` / `rr_veto` / `stop_gecersiz` / `kaldirac_guvenlik`), cycle logu da yazar.
   Liste verilmezse davranış **birebir aynı** (mevcut çağıranlar değişmedi).

2. **Kapıların haklı olup olmadığı ölçülemiyordu.** Bir kapının değeri "neyi engellediği"yle
   ölçülür; engellenen işlem hiç açılmadığı için sonucu hiç bilinmiyordu. `veto_analiz.py` vardı
   ama (a) dedup'lu logdan besleniyor, (b) sabit %8 stop-vekili kullanıyor — botun gerçek
   ATR-stop'u/TP1'i değil. Yani yaklaşık, ve az sayıda olayla.

### ÇÖZÜM: `golge.py` — reddedilen her girişin sanal karnesi
Bot bir girişi reddettiğinde **aynı giriş gölgede açılır**: ölçücünün AYNI giriş/stop/tp1/tp2
seviyeleri, botun AYNI çıkış kuralları (`testbot.yonet_acik_pozisyonlar` doğrudan çağrılır,
mantık kopyalanmaz — `benim.py` deseni), AYNI risk-önce boyutlandırma. Ayrı kasa/dosyalar.
Pozisyon `kapi` etiketiyle işaretlenir → kapı bazında karne:

> ort R **negatif** → kapı HAKLI (zarardan korudu, dokunma)
> ort R **pozitif** → kapı para yakıyor OLABİLİR → N≥25-30 + çoklu rejim şartıyla tartışılır

**Kapsanan kapılar:** karar_yon vetoları (blowoff / taker_soguma / long_veto / btc_pay_freni) ·
giriş kapıları (rr_veto / kaldirac_guvenlik / stop_gecersiz) · **onay_bekle** (beklemenin kendisi
de bir kapı: 33 aday burada öldü — "beklemek kazandırıyor mu, fırsat mı kaçırıyor" ancak
beklemeden girilen hali ölçülürse cevaplanır).

**NEDEN KAPI GEVŞETMEK DEĞİL DE BU (kararın gerekçesi):** Kapıyı gevşetip sonuca bakmak,
hipotezi sermayeyle test etmektir; gölge defterde hipotez **bedava** test edilir. Ayrıca
[[giris-mekanizmasi-mukemmel]] dersi: onay gevşetilmez, risk başka pilarlarla yönetilir.
**Karar kapılarında HİÇBİR değişiklik yapılmadı.** Ölçüm N'i haftada ~2'den ~30'a çıkar.

**Fail-safe:** tüm `_golge` çağrıları try/except içinde; gölge çöker/yavaşlarsa bot etkilenmez
(ölçüm katmanı hiçbir zaman karar katmanını durduramaz). Gölge girişleri Telegram/toast
GÖNDERMEZ (alarm maliyeti dürüstlüğü, Karmaşıklık Bütçesi md.4).

**Tekrar-sayım koruması:** sembol başına 4 saatte bir gölge (KMNO'nun 19 kaydı = 1 olayın 19 kez
sayılması = sahte N). Botun kendi cooldown'uyla aynı büyüklük.

**Panel:** "Bot neden işlem açmıyor?" sayfasına gölge karnesi tablosu eklendi + tıkla-aç açıklama.

### YAN BULGU — testin süresi doluyor (sessiz üçüncü sebep)
`sure_gun=19`, başlangıç 07-23 19:07 → **11 Ağustos 19:07'de SURE_DOLDU**. O andan itibaren bot
açık pozisyonları yönetmeye devam eder ama **yeni giriş HİÇ aramaz**. "Bot girmiyor"un yakında
gelecek en büyük sebebi bu olacaktı ve hiçbir yerde görünmüyordu → panele süre uyarısı eklendi
(kalan ≤2 gün veya durum≠AKTİF ise kırmızı şerit). **Uzatma kararı kullanıcıya ait, otomatik
uzatılmadı.**

**SINIR (dürüstlük):** kancalar canlı turda henüz TETİKLENMEDİ — değişiklikten bu yana hiçbir
aday reddedilmedi (piyasa sakin, hepsi "karar-yok"). Kablo testi elle doğrulandı (`testbot._golge`
→ gölge pozisyon açıldı, `kapi`/`kaynak` etiketleri doğru), test artıkları silinip defter temiz
bırakıldı. İlk gerçek kayıt ilk redde oluşacak.

## ⭐⭐ TUR-3 — TEZAT RAPORU + AGRESİFLEŞTİRME (2026-08-10, kullanıcı kararı)

**Talep:** "ölçüm bant genişliğini düzelt · pump'lamış coinleri pump'lamadan keşfetsin ·
giriş hem long hem short olsun · süre sınırı olmadan çalışsın · **tezatları tespit et** ·
daha agresif bir bot."

Aşağıdaki 8 tezat kodda ve isteklerde tespit edildi. 1-3 ve 7 **onarıldı** (Madde 8: belgelenmiş
davranışı geri getiren onarım), 4-6 ve 8 **ölçüldü ve kayda geçti**.

### TEZAT-1 ⭐ — Kapı, botun kullanmadığı hedefi test ediyordu (giriş kuraklığının ASIL sebebi)
`olcucu`: yapısal TP1'e net R/R < **2.0** ise VETO. Ama `testbot.tp1_efektif_hesapla` TP1'i
**min(yapısal, giriş + 1.5×risk)**'e ÇEKİYOR (`kismi_kar_r`=1.5; 2026-07-04'te "TP1 pratikte hiç
tetiklenmiyordu, 2.6-5.2R uzaktaydı" diye eklendi). **Bot, almayı hiç planlamadığı 2R hedefe göre
işlem reddediyordu.** Kanıt: 08-08 KMNO 19 kez SHORT kararı → 19'u da bu kapıda öldü (rr 0.19);
03-10 Ağustos 21 SHORT kararı → 0 giriş; bot 3 gün hiç işlem açmadı.
**Onarım:** kapı artık `rr_kapisi_r` = `kismi_kar_r` (1.5) — **yeni eşik icat edilmedi**, mevcut
config değeri kullanıldı. `olcucu` ayrıca `rr_tp2` / `rr_tp2_net` döndürüyor.
Geri alma: `rr_kapisi_r: 2.0`.

### TEZAT-2 ⭐ — Fade girişi için momentum ön-şartı aranıyordu
NOTR dalı `stage ∈ (BASLIYOR, HAZIRLANIYOR)` şartı koyuyordu. Ama fade = ortalamaya dönüş; ihtiyacı
"hareket başlıyor" değil **uç nokta**. Üstelik OTOPSİ-3 tam da BASLIYOR'un short için **en kötü**
hücre olduğunu ölçmüştü (−0.09R; izle +0.07R; HAZIRLANIYOR +0.19R). **Bot, en iyi stratejisi için
en kötü ölçülmüş ön-şartı dayatıyordu.** Havuzun **%89'u** "izle" ve o hücre POZİTİF ölçtü.
**Onarım:** yeni NOTR-fade dalı stage şartı aramıyor (skor ≥ `radar_alert_skor`).

### TEZAT-3 — Aynı kanıt tek dalda uygulanmış
Pump kapısı (chg24 ≥ %20 → SHORT açma; 362 sembol / 16.169 gözlem, iki yarıda da negatif)
2026-08-04'te **yalnız AYI-SHORT** dalına konmuş; kodun kendi notu "NOTR-SHORT ve BOGA-SHORT
dokunulmadı, ayrı karar ister" diyordu. Dahası **AYI blow-off redirect** pump'ta LONG'u SHORT'a
ÇEVİRİYORDU — yani aynı kanıtın tam tersini yapıyordu (BLESS −$488'in sınıfı).
**Onarım:** eşik tüm SHORT dallarında; redirect kaldırıldı (pump'a short da long da açılmaz).

### TEZAT-4 ⭐ — Kullanıcının iki isteği birbiriyle çelişiyor (ÖLÇÜLDÜ)
"Pump'lamadan keşfet" ile "daha çok işlem" ilk bakışta aynı anda olamaz, çünkü **botun mevcut giriş
akışının kendisi pump'lamış coin fade'iydi.** Ölçüm (`scratchpad/etki_tahmini.py`, 7 gün / 1152 tur /
6799 aday kaydı, hepsi NOTR rejim):

| Varyant | Toplam karar | Kırılım |
|---|---|---|
| **A — eski kural** | 97 | SHORT 64 (hepsi pump'lamış sınıf) · LONG 33 |
| **B — pump kapısı + stage şartlı fade** | **72** ↓ | pump kapısı 44 SHORT'u kesiyor, fade 18 ekliyor |
| **C — pump kapısı + stage şartsız fade** | **111** ↑ | SHORT 53 · LONG 58 — *gerçekten iki yönlü* |

**C seçildi.** Çelişki gerçekti ama çözülebilirdi: pump'lamış coinleri elerken bandı korumanın yolu,
fade'i uç-nokta tabanlı hale getirip "izle" hücresine açmaktı. **B'yi ölçmeden uygulasaydık
kullanıcının "daha agresif" isteğinin TERSİ olurdu (97 → 72).**

### TEZAT-5 — "Agresif" ile "ölçüm" aynı eksen değil
Agresiflik iki şey olabilir: **işlem başına boyut** ya da **işlem sayısı**. Mevcut karne negatif
(−$815 / 19 gün); negatif beklentide boyutu büyütmek kaybı hızlandırır, sayıyı büyütmek ölçüm üretir.
**Agresiflik FREKANSA verildi:** `maks_pozisyon` 4→8, `tarama_havuz_n` 70→150, fade dalı açık.
`islem_risk_pct` **3'te bırakıldı** — portföy riski zaten 4×3=%12'den 8×3=**%24**'e çıktı.
Boyut agresifliği isteniyorsa tek satır: `islem_risk_pct`. (Öneri; kullanıcı kararı bekliyor.)

### TEZAT-6 — Süre sınırı iki iş yapıyordu, biri sessizce kayboluyordu
`sure_gun` yalnız bir zaman kapısı değil, **zorunlu değerlendirme durağıydı** (K1-K6 kapıları orada
açılırdı). Sınırsız bot bu durağa hiç uğramaz. Ayrıca `min_equity_dur`=50 ($10.000'de %99,5 kayıp)
pratikte **hiç tetiklenmez** — yani gerçek bir koruma yoktu.
**Yerine:** `maks_dusus_pct` = %25 → equity zirveden %25 düşerse `HALT_DUSUS` (yeni giriş durur,
açık pozisyonlar yönetilmeye devam eder, `--devam` ile açılır ve zirve referansı sıfırlanır).
kazanan-bot-arastirma-raporu §8/3'ün uygulaması — rapor önermişti, hiç uygulanmamıştı.

### TEZAT-7 — Skor bir "açık-pozisyon dedektörü" ama sıralama saf skora göreydi
SKOR OTOPSİSİ BULGU 1: skor beş faktörlü bileşke değil, bir açık-pozisyon dedektörü. Kısa liste
(top-10) saf skora göre diziliyordu → **en yüksek skorlular sistematik olarak zaten HAREKET ETMİŞ
coinler** → "pump'lamadan keşfet" isteğiyle doğrudan çelişiyordu.
**Onarım:** HAZIRLANIYOR'a sıralama bonusu (+8, `hazirlaniyor_sira_bonus`) ve NOTR skor eşiği 45→40.
Gerekçe OTOPSİ-3: HAZIRLANIYOR skordan **bağımsız** ayırt ediyor (skor<45'te bile +0.22 vs +0.01,
N=116) ve 7 günlük havuzda medyan skoru **40,2** — eski 45 eşiği bu hücrenin yarısını kesiyordu.
Bonus **yalnız sıralamaya** etki eder; skor, kapılar ve karar mantığı değişmedi.

### TEZAT-8 — "Tek seferde tek değişken" ihlali (kabul edilen, telafi edilen)
Bu turda **7 değişken birden** değişti. Normalde yasak; ama 19 günde 12 işlem üreten bir kurulumda
tek-değişken disiplini bir lükstür — koruduğumuz karne zaten kanıt üretemiyordu. **Telafi:**
(a) `2026-08-10` sınırı defterde, karne öncesi/sonrası ayrılabilir; (b) atribüsyon aracı **gölge
defter** — reddedilenler orada açılıyor, kapı bazında karne çıkacak; (c) her değişiklik ayrı config
anahtarına bağlı, tek satırla geri alınabilir.

### Uygulanan değişikliklerin özeti

| Ne | Eski | Yeni | Anahtar |
|---|---|---|---|
| Süre sınırı | 19 gün | **sınırsız** | `sure_gun: 0` |
| Düşüş freni | yok (etkisiz $50) | **%25** | `maks_dusus_pct` |
| R/R kapısı | 2.0 (kullanılmayan hedef) | **1.5** (fiili hedef) | `rr_kapisi_r` |
| Eşzamanlı pozisyon | 4 | **8** | `maks_pozisyon` |
| Tarama havuzu | 70 | **150** | `tarama_havuz_n` |
| Pump kapısı kapsamı | yalnız AYI-SHORT | **tüm SHORT dalları** | `ayi_short_chg24_max` |
| Pump'ta LONG→SHORT çevirme | var | **kaldırıldı** | — |
| Pump-öncesi öncelik | yok | **HAZIRLANIYOR +8 sıra, eşik 40** | `hazirlaniyor_sira_bonus` |
| smart=NOTR adayları | hiçbir yol yoktu | **iki yönlü fade** (pos≥0.75 SHORT / ≤0.40 LONG) | `notr_fade_acik` |
| İşlem başına risk | %3 | **%3 (değişmedi)** | `islem_risk_pct` |

**DÜRÜSTLÜK NOTU:** NOTR-fade dalı **ölçümle gerekçelendirilmedi** — `notr_long_acik` (2026-08-04) ile
aynı sınıfta, kullanıcı kararı. Kalite filtrelerinin hiçbiri gevşetilmedi (pump kapısı, long_veto,
dip-bıçak koruması, taker≥1.0 aynen duruyor). Tahmini bant: 7 günde 97 → **111 karar**; gerçek artış
bundan BÜYÜK olacak, çünkü HAZIRLANIYOR sıra bonusunun kısa listeye sokacağı adaylar bu simülasyonda
görünmüyor (arşiv yalnız top-10'a girmişleri taşıyor).
Config yedeği: `kripto-config.json.yedek-2026-08-10` (anahtar içerir, gitignore'da).

## ⭐⭐⭐ ÖRÜNTÜ ANALİZİ — 46 günlük radar arşivi + 10 gerçek işlem (2026-08-10, kullanıcı kararı)

**Talep:** "botun işlem açtığı ve kâr ettiği bütün varsayımları nasıl sağladı, her eşik ve ölçme
birimini detaylı araştırıp bir örüntü üret · elinde 2 aya yakın radar verisi ve bota takılanlar var."

**Veri:** `radar_archive.jsonl` 121.620 kayıt / 384 sembol / 46 gün (06-24 → 08-10) → sembol başına
6 saat dedup ile **7.119 bağımsız olay**. Her olay botun GERÇEK mekaniğiyle ileri oynatıldı:
giriş = kaydın ertesi 1h barının açılışı · stop = ölçücünün A-varyantı (yapısal ±0.25ATR / son 10
barın ucu ±0.25ATR / 1.5ATR yedeği arasından **girişe en yakın**) · hedef 2R · ufuk 72s · **fitil
bazlı** · aynı barda ikisi de → STOP · maliyet 0.04R.
Araçlar: `scratchpad/oruntu_analiz.py` · `oruntu_rapor.py` · `oruntu_bilesik.py` · `cikis_karsilastirma.py`.
Grafikli rapor: artifact (bkz. oturum notu).

### BULGU 1 ⭐ — Ödül/risk asimetrisi: kayıplar TAM, kazançlar KIRPIK
10 pozisyonun **10'u da STOP ile kapandı. TP2'ye bir kez bile ulaşılmadı.**
Gerçekleşen R: kaybedenler ort **−1.03** (aralık −1.01…−1.05), kazananlar ort **+0.62**
(+0.01 / +0.05 / +0.76 / +1.65). Bu ödül profiliyle başabaş kazanma oranı **%62**; fiili **%40**.

**Kâr tek işlemden:** GRVT +$446 = toplam kârın **%89'u**. Diğer üç kazanan pratikte sıfır.
→ "Kazanan profili" dört gözlemlik, pratikte **bir** işlemlik. Popülasyon sınaması bu yüzden zorunluydu.

### BULGU 2 — Çıkış mekaniği SUÇLU DEĞİL (hipotezim çürüdü)
Aynı 10 giriş, üç çıkış kuralıyla yeniden oynatıldı (`cikis_karsilastirma.py`):

| Çıkış kuralı | ort R | kazanma |
|---|---|---|
| SAF 2R (trailing yok, kısmi yok) | −0.400 | %20 |
| SAF 1.5R | −0.500 | %20 |
| **GERÇEK (trailing + kısmi TP1)** | **−0.368** | **%40** |

Trailing + kısmi kâr, iki işlemi −1.00R'den +0.76R ve +0.01R'ye çevirdi. **Çıkış katmanı üçünün
en iyisi.** Sorun GİRİŞ SEÇİMİNDE: 10 girişin 8'i herhangi bir hedefe varmadan stopu gördü.

### BULGU 3 ⭐⭐ — Kazananların ortak özelliği ÇÜRÜDÜ (işaret olarak TERS)
Dört kazananın tek ortak yanı: hepsi 20-bar aralığın tepesinde (**pos ≥ 0.86**, popülasyonun
%91-98'inin üstünde). Ön-kayıtlı profil (SHORT · pos≥0.85 · 0<chg24<40) 7.119 olayda sınandı:

| | N | ort R |
|---|---|---|
| PROFİL | 638 | **−0.090** |
| KONTROL (profil dışı) | 6481 | −0.018 |

**Profil kontrolden DAHA KÖTÜ**, ve iki zaman yarısında da öyle (A −0.118 / B −0.060).
SHORT için pos bandı tablosu tam ters yönde: 0-0.25 → **+0.017** · 0.25-0.5 → −0.013 ·
0.5-0.7 → −0.031 · 0.7-0.85 → **−0.090** · 0.85+ → **−0.071**.
**Range tepesinden SHORT en kötü bant; range dibinden SHORT tek pozitif bant.**

> **DERS (altıncı tekrar):** Dört gözlemden örüntü çıkarmak, o dört gözlemin ortak yanını
> "sebep" sanmaktır. Dördü de tepedeydi ama tepede olmak kazandırmadı — piyasa o dönem
> tepeleri fazlasıyla cezalandırdı, kazananlar oraya rağmen çıktı. Kontrol grubu olmasaydı
> bu profil koda girerdi.

### BULGU 4 ⭐⭐⭐ — GERÇEK ÖRÜNTÜ (dört koşul, hepsi iki zaman yarısında da pozitif)
Eşikler **icat edilmedi**, hepsi sistemin zaten taşıdığı config değerleri:

| | Koşul | N | ort R | A yarısı | B yarısı |
|---|---|---|---|---|---|
| **A** | `funding ≤ −0.05` (%/8s) | 508 | **+0.259** ±0.063 | +0.250 | +0.269 |
| **B** | `oi24 ≥ %10` | 803 | **+0.189** ±0.050 | +0.151 | +0.228 |
| **C** | `skor ≥ 40` | 405 | **+0.200** ±0.070 | +0.097 | +0.312 |
| **D** | `stage = HAZIRLANIYOR` | 114 | **+0.247** ±0.133 | +0.113 | +0.352 |
| X | `pos ≥ 0.85` (kazananların profili) | 715 | **−0.071** ±0.052 | −0.091 | −0.049 |

**Kesişimler:**

| Kombinasyon | N | ort R | A | B |
|---|---|---|---|---|
| **A + B** | **206** | **+0.375** ±0.098 | +0.253 | +0.510 |
| A + C | 211 | +0.366 ±0.097 | +0.194 | +0.553 |
| A + B + C | 192 | +0.369 ±0.101 | +0.199 | +0.566 |
| B + C | 354 | +0.212 ±0.074 | +0.118 | +0.317 |
| A + D | 33 | +0.740 ±0.232 | +0.334 | +1.039 |

Kontrol grubu her satırda ≈ **−0.03**. **A+B en savunulabilir hücre**: N=206, ~3,8 SE,
iki yarıda da pozitif. A+D daha yüksek ama N=33 → izlenim.

> **ÖRÜNTÜ (tek cümle):** *Shortlar kalabalık (funding ≤ −0.05) ve pozisyon birikiyor
> (oi24 ≥ %10) iken SHORT; aşama HAZIRLANIYOR ve skor ≥ 40 ise daha güçlü; range konumu
> DÜŞÜK olmalı, yüksek değil.*

**Mekanizma:** kalabalık short + biriken açık pozisyon = "squeeze yakıtı" DEĞİL **dağıtım**
işareti. Fiyat henüz yatayken (HAZIRLANIYOR: sıkışmış + |last3|<%4) pozisyon birikiyorsa hareket
aşağı çözülüyor. **Bot bunun tersini yapıyordu:** hareket başladıktan SONRA (BASLIYOR, R −0.04)
ve tepeden (pos≥0.85, R −0.07) giriyordu.

**SİMETRİ KONTROLÜ (örüntünün gürültü olmadığının en güçlü kanıtı):** aynı koşullar LONG
tarafında simetrik NEGATİF — A −0.337 · B −0.278 · C −0.286 · D −0.134. Koşullar sadece
"oynaklık" işaretlemiyor, **yön taşıyorlar**.

**ÜÇÜNCÜ BAĞIMSIZ DOĞRULAMA:** derin negatif funding bulgusu, projenin daha önce iki ayrı
ölçümle (zemin etüdü + skor otopsisi `squeeze_bonus`) vardığı sonuca üçüncü kez ulaşıyor:
derin negatif funding "yukarı squeeze yakıtı" değil, **düşüşe devam işareti**.

### BULGU 5 — Skor monoton, ama YALNIZ short tarafında
skor 0-30 → −0.046 · 30-40 → +0.093 · 40-45 → +0.167 · **45-60 → +0.205 (botun kapısı)** ·
60-80 → +0.234 · 80+ → +0.460 (N=4, izlenim). Tekdüze artıyor → **skorda gerçek bilgi var.**
Aynı skor LONG tarafında **−0.286**. Sebebi skorun yapısında: 113 puanın **35'i** açık pozisyon
değişiminden, 20'si hacimden geliyor → yüksek skor "pozisyon birikmiş" demek, "yükselecek" değil.
Bu, SKOR OTOPSİSİ BULGU 1-2'nin (dedektör + ters işaret) bağımsız doğrulaması.

### BULGU 6 ⚠️ — BUGÜN AÇTIĞIM İKİ KURAL ÖLÇÜMLE ÇELİŞİYOR
Tur-3'te (aynı gün, ölçümden ÖNCE) açılan NOTR-fade dalı, ölçümün **en kötü iki hücresine** giriyor:

| Ayar | Değer | Ölçülen R | N | Hüküm |
|---|---|---|---|---|
| `notr_fade_pos_ust` | 0.75 → SHORT | −0.090 / −0.071 | 1741 | ✕ **ters yönde** |
| `notr_fade_pos_alt` | 0.40 → LONG | −0.155 / −0.165 | 3979 | ✕ **ters yönde** |
| `radar_short_skor` | 45 | +0.205 | 201 | ✓ doğru |
| `hazirlaniyor_sira_bonus` | 8.0 | +0.247 | 114 | ✓ doğrulandı |
| `ayi_short_chg24_max` | 20 | −0.119 (chg24 20-40) | 45 | ✓ doğru |
| `funding_derin_neg_pct` | −0.05 (kapıda kullanılmıyor) | **+0.259** | 508 | ◆ kapı adayı |
| `oi_hizli_degisim_pct` | 5 (yalnız veto) | **+0.189** (≥10) | 803 | ◆ kapı adayı |

**AKSİYON ALINMADI — kullanıcı kararı bekliyor.** Önerim: `notr_fade_acik: 0` ile kapat
(dal ölçümsüz açılmıştı, artık ölçüm var ve karşı çıkıyor), yerine **A+B'yi ÖLÇÜM KATMANI**
olarak ekle (kapı değil): koşul sağlanınca aday "A+B" etiketiyle işaretlensin, 25-30 canlı
olay biriktikten sonra kapı tartışması açılsın — erken-kuşak modelinin aynısı.

### SINIRLAR (hükümle birlikte okunur)
1. **46 günün tamamı AYI/NOTR — boğa hücresi YOK.** Örüntü tek rejimde doğrulandı.
2. Pillar D (smart / taker) radar arşivinde yok → o iki kapı bu ölçümde sınanamadı.
3. Ölçüm 2R hedefli; botun fiili çıkışı 1.5R kısmi + trailing → **gerçekte elde edilecek R
   bu tablodan KÜÇÜK olur** (BULGU 1: sistem 2R'ye hiç ulaşmadı).
4. Slipaj yok sayıldı; düşük hacimli sembollerde iyimser.
5. A+D (+0.740) cazip ama N=33 — karar için yetersiz, eşik oynatmaya davetiye.

## ⭐⭐⭐⭐ KAÇAN KAZANANLAR — R/R kapısı TERS ÇALIŞIYOR (2026-08-10)

**Talep:** "kazananlara neden giremedi, girmesi gereken yerde girseydi ne olurdu —
kazananlardaki ortak GİRİLECEK NOKTA'yı ara; aynı sinyale sahip radarda olup
değerlendirilemeyenlerle karşılaştır."

**Yöntem:** 7.119 olayın hepsine giriş-noktası ölçüleri eklendi (mumdan hesaplandı, arşivde yok):
`stop_frac` (girişten stopa %), `rr_tp1` (en yakın yapısal hedefe uzaklık ÷ risk),
`uzanim` (20-bar tepesinden ATR cinsinden uzaklık), `mfe/mae`. Sonra **kazanan (2R hedefe
ulaşan, N=2289)** ile **kaybeden (stopa giden, N=4606)** karşılaştırıldı ve botun her kapısı
bu iki grup üzerinde yeniden koşuldu. Araç: `scratchpad/kacan_kazananlar.py`.

**DOĞRULAMA:** offline hesaplanan R/R kapısı, canlıdaki ret oranını birebir yeniden üretti
(hesap %71.1 / canlı ~%70) → kapı simülasyonu sadık.

### BULGU A — "Ortak girilecek nokta" DİYE BİR ŞEY YOK
Kazanan vs kaybeden medyanları:

| Ölçü | KAZANAN | KAYBEDEN | ayırt ediyor mu |
|---|---|---|---|
| stop mesafesi % | 1.443 | 1.398 | hayır |
| **rr_tp1** | **1.012** | **1.001** | **hayır** |
| tepeden ATR uzaklık | 2.403 | 2.308 | hayır |
| skor | 8.50 | 8.10 | hayır |
| pos | 0.43 | 0.45 | hayır |
| comp / vol_x | 0.94 / 0.60 | 0.92 / 0.60 | hayır |
| **oi24** | **+0.271** | **−0.054** | **EVET** |
| **chg24** | **+0.023** | **+0.050** | evet (zayıf) |

**Giriş NOKTASI (fiyatın yapıya göre yeri) kazananı kaybedenden ayırmıyor.** Ayıran tek şey
giriş KOŞULU: açık pozisyon birikimi. Bu, "daha iyi bir yerden girseydik kazanırdık"
hipotezini çürütüyor — 2.289 kazananla 4.606 kaybeden aynı yerlerden giriliyor.

### BULGU B ⭐⭐ — R/R KAPISI KAZANANLA KAYBEDENİ AYIRT ETMİYOR
| Kapı | kazananın %'sini keser | kaybedenin %'sini keser | kestiğinin R | **geçirdiğinin R** |
|---|---|---|---|---|
| skor < 45 | 95.5% | 96.8% | −0.035 | **+0.216** |
| stage = izle | 97.8% | 98.3% | −0.029 | **+0.197** |
| **rr_tp1 < 1.5 (yeni)** | **62.8%** | **61.8%** | **−0.008** | **−0.053** |
| **rr_tp1 < 2.0 (eski)** | **71.9%** | **69.8%** | **−0.000** | **−0.085** |
| chg24 ≥ 20 (pump) | 0.6% | 0.7% | −0.139 | −0.024 |

Skor kapısı **düşük kapsam / yüksek isabet**: kazananların %95'ini atıyor ama geçirdiği
grup +0.216 — bir seçici için doğru davranış. **R/R kapısı ise kazananla kaybedeni AYNI
oranda kesiyor (62.8% vs 61.8%) ve geçirdiği grup kestiğinden DAHA KÖTÜ.** Yani filtre değil,
%30'luk rastgele bir örnekleyici — üstelik hafif ters seçici.

### BULGU C ⭐⭐⭐ — R/R KAPISI EDGE'İ YOK EDİYOR (izole ölçüm)
| Küme | N | ort R | hedefe ulaşan | A yarısı | B yarısı |
|---|---|---|---|---|---|
| **A+B (kapısız)** | 206 | **+0.375** | %40 | +0.253 | +0.510 |
| A+B + rr ≥ 1.5 (yeni kapı) | 63 | **−0.004** | %32 | −0.319 | +0.365 |
| A+B + rr ≥ 2.0 (eski kapı) | 42 | **−0.034** | %31 | −0.427 | +0.398 |
| **A+B + rr < 1.5 (KAPININ ÇÖPE ATTIĞI)** | **143** | **+0.542** | %43 | +0.516 | +0.571 |
| skor≥45 (kapısız) | 276 | +0.216 | %37 | +0.144 | +0.294 |
| skor≥45 + rr ≥ 1.5 | 122 | +0.045 | %33 | −0.033 | +0.145 |
| **skor≥45 + rr < 1.5 (kapının attığı)** | **154** | **+0.351** | %40 | +0.305 | +0.395 |

**Kapının reddettiği grup, kabul ettiğinden her seferinde belirgin daha iyi.**

Botun tüm kapıları birlikte (46 gün):
| | N | ort R |
|---|---|---|
| tüm kapılar + R/R 2.0 | 77 | **+0.011** |
| tüm kapılar + R/R 1.5 | 107 | +0.008 |
| **tüm kapılar, R/R YOK** | **212** | **+0.151** |

**R/R kapısını kaldırmak hem işlem sayısını ~2×'e çıkarıyor hem beklentiyi +0.011'den
+0.151'e taşıyor.** 2.289 kazanandan sadece 26'sı (%1) mevcut kapılardan geçebiliyordu.

### BULGU D — MEKANİZMA: kapı yapısı gereği ters
`rr_tp1` bandına göre (tüm olaylar, monotonluk YOK ve yön TERS):

| rr_tp1 bandı | N | ort R |
|---|---|---|
| 0.00 – 0.75 | 3015 | −0.011 |
| 0.75 – 1.00 | 570 | −0.075 |
| **1.00 – 1.50** | 872 | **+0.048** |
| **1.50 – 2.00** | 602 | **+0.056** |
| 2.00 – 3.00 | 1020 | −0.061 |
| **3.00 +** | 1040 | **−0.109** ← kapının en çok sevdiği bant |

**Yüksek R/R = daha kötü.** Sebep tanımın kendisinde: `rr_tp1` = *en yakın yapısal desteğe*
uzaklık ÷ risk. Yüksek rr_tp1 "aşağıda yakın destek YOK" demektir — yani coin zaten her şeyi
kırıp boşluğa düşmüş, uzamış durumda; ortalamaya dönüş onu geri zıplatıyor. Düşük rr_tp1 ise
"hemen altında destek var" = kırılmayı bekleyen gerçek short kurulumu.
**Bot "koşacak yer var" sanıp aslında "zaten koşmuş"u seçiyor.**

Ek bulgu: rr_tp1 < 1.5 olan olayların %43'ü yine de 2R'ye ulaşıyor → **yapısal TP1, fiyatın
duracağı yerin kötü bir tahmini.** R/R çerçevesinin dayandığı varsayım da bu ölçümle zayıflıyor.

### HÜKÜM
1. **"Kazananlara neden giremedi?"** → R/R kapısı yüzünden. Kapı kazananların %72'sini
   kesiyor, kaybedenlerin %70'ini — yani ayırt etmiyor; ve kestiği grup daha iyi.
2. **"Girmesi gereken yerde girseydi ne olurdu?"** → Giriş noktasında ortak örüntü YOK.
   Kazananları ayıran şey *nereden* girildiği değil, *hangi koşulda* girildiği (oi24 + funding).
3. **"Radarda olup değerlendirilemeyenler"** → R/R kapısı olmadan aynı kapılardan geçen
   212 olay +0.151R; kapıyla 77 olay +0.011R.

**ÖNERİ (kullanıcı kararı bekliyor, aksiyon ALINMADI):**
- `rr_kapisi_r: 0` → R/R kapısını etkisizleştir (kaldırma değil, config ile kapat — geri alınabilir).
- Yerine **A+B'yi kapı yap** (funding ≤ −0.05 **ve** oi24 ≥ %10): N=206, +0.375R, iki yarıda da pozitif.
- Kaldıraç güvenlik kırpması (stop likidasyondan önce) **AYNEN KALIR** — o ayrı bir koruma.

**SINIRLAR:** 46 günün tamamı AYI/NOTR. Ölçüm sabit 2R hedefli; botun fiili çıkışı
1.5R kısmi + trailing olduğu için gerçekte elde edilecek R bu tablodan küçük olur.
rr_tp1 burada BRÜT (maliyet düşülmemiş); botunki net — sıralamayı değiştirmez, seviyeyi düşürür.
Pillar D (smart/taker) arşivde yok, o kapılar sınanamadı.

## ⭐⭐⭐⭐⭐ A+B KAPISI AÇILDI · R/R KAPISI KAPANDI (2026-08-10, kullanıcı kararı)

**Kullanıcı:** *"Elimizdeki geçmiş veriyle bunları bulabilirsin, niye bekleyelim — elimdeki
edge kapıdan geçsin."* Doğru: önerilen kapı seti **canlıya alınmadan önce** 46 günlük arşivde
baştan sona koşuldu (`scratchpad/kapi_seti_replay.py`), sonra uygulandı.

### KAPI SETİ REPLAY (7.119 olay · SHORT · botun gerçek mekaniği)

| Set | N | gün/olay | ort R | hedefe | A yarısı | B yarısı | kontrol |
|---|---|---|---|---|---|---|---|
| **S0 bugünkü** (skor≥45 + rr≥1.5) | 107 | 2.3 | **+0.008** | %33 | −0.058 | +0.093 | −0.025 |
| S1 R/R kalksın | 212 | 4.6 | +0.151 | %35 | +0.141 | +0.163 | −0.030 |
| S2 S1 + A+B | 95 | 2.1 | +0.273 | %39 | +0.347 | +0.165 | −0.029 |
| S3 sadece A+B | 206 | 4.5 | +0.375 | %40 | +0.253 | +0.510 | −0.037 |
| S4 A+B + skor≥45 | 134 | 2.9 | +0.338 | %40 | +0.274 | +0.407 | −0.032 |
| **S5 A+B + pump kapısı** | **201** | **4.4** | **+0.396** | **%40** | **+0.277** | **+0.528** | −0.037 |
| S6 A+B + HAZIRLANIYOR | 32 | 0.7 | +0.702 | %47 | +0.334 | +0.988 | −0.028 |

**Gerçekçilik kesintisi** (bot 2R'ye hiç ulaşmadı; kazançlar 1.5R'de kırpılarak):

| Set | kırpılmış ort R | A yarısı | B yarısı |
|---|---|---|---|
| **S0 bugünkü** | **−0.143** | −0.196 | −0.074 |
| S1 R/R kalksın | −0.005 | −0.002 | −0.007 |
| **S5 A+B + pump** | **+0.218** | **+0.127** | **+0.319** |
| S6 A+B + HAZIRLANIYOR | +0.499 | +0.231 | +0.707 |

Kümülatif: S0 = **+0.8R / 46 gün**. S5 = **+79.5R / 46 gün** (201 işlem).

**KRİTİK AYRINTI — skor bu kapıya ŞART DEĞİL:** S4 (+0.338) < S3 (+0.375). Skor eklemek
performansı *düşürüyor* ve adayı kısıyor. Sebep: skorun 113 puanının 35'i zaten oi24'ten
geliyor — `oi24 ≥ %10` şartıyla aynı bilgiyi ikinci kez saymak oluyor. Aday kısa listesi
zaten skora göre sıralanıyor; skoru bir de kapı yapmaya gerek yok. **S6 en yüksek ama N=32
(izlenim) → seçilmedi; S5 uygulandı.**

### UYGULANAN DEĞİŞİKLİKLER

| Ayar | Eski | Yeni | Gerekçe |
|---|---|---|---|
| `ab_kapisi_acik` | — | **1** | Yeni SHORT kapısı: `funding ≤ −0.05` **ve** `oi24 ≥ %10` |
| `ab_funding_esik` | — | −0.05 | mevcut `funding_derin_neg_pct` ile aynı değer |
| `ab_oi24_esik` | — | 10.0 | ölçümün gösterdiği eşik (0-10 bandı −0.02, 10-25 bandı +0.217) |
| `rr_kapisi_r` | 1.5 | **0** (devre dışı) | kapı kazananla kaybedeni ayırt etmiyor, geçirdiği grup daha kötü |
| `notr_fade_acik` | 1 | **0** | aynı gün açılmıştı; ölçüm iki yönüne de karşı çıktı |

**A+B kapısının yeri:** `_karar_yon_ham` başında, rejim dallarından ÖNCE; yalnız
`rejim ∈ (AYI, NOTR)`. **TAM_BOGA'da kapalı** — ölçümün 46 gününde boğa hücresi yok.
Korunan filtreler: pump kapısı (chg24 ≥ %20 → açma) · dip-bıçak (`short_riskli_dip`) ·
`asiri_dusmus` · BTC-PAY short freni (sarmalayıcıda, holdout'lu ölçüm) · kaldıraç güvenlik
kırpması. **Hiçbiri gevşetilmedi.**

**R/R kapısı `rr_kapisi_r ≤ 0` ile TAMAMEN devre dışı** (negatif `rr_net` bile geçer —
ölçüm böyle yapıldığı için tutarlı). Doğrulandı: daha önce hepsi `rr_veto` yiyen
XAN/GRVT/SQD artık açılıyor.

**Birim testi (sentetik aday):** NOTR → SHORT/ANINDA · AYI → SHORT/ANINDA · BOGA → karar-yok ·
chg24=25 → VETO:blowoff · funding=−0.02 → karar-yok · oi24=5 → karar-yok. Hepsi beklendiği gibi.

### NE BEKLENİYOR
Botun kendi aday evreninde A+B **günde ~6,4 bağımsız olay** üretiyordu (6,2 günlük ölçüm,
40 olay / 15 sembol). Maks 8 pozisyon + 4 saat cooldown ile pratikte günde 3-5 giriş.
Öncesi: **6,2 günde 4 giriş.**

### SINIRLAR (hükümle birlikte okunur)
1. **Tek rejim** — 46 günün tamamı AYI/NOTR. Boğa gelince A+B yeniden ölçülmeli.
2. Ölçüm **sabit 2R hedefli**; bot 1.5R kısmi + trailing ile çıkıyor → gerçek R daha küçük.
   Kırpılmış tablo (+0.218) daha gerçekçi ama o da tavan.
3. **Slipaj yok sayıldı**; A+B olayları düşük hacimli coinlerde yoğunlaşıyor.
4. **Bağımsızlık zayıf**: 206 olay 15 sembolde kümeleniyor ve düşen piyasada hepsi aynı yönde
   → gerçek portföy riski göründüğünden yüksek. Karnede "ayrı sembol" sayısı izlenmeli.
5. Pillar D (smart/taker) arşivde yok → o kapılar bu ölçümde sınanamadı, kodda duruyorlar.

### GERİ ALMA (tek satır)
`ab_kapisi_acik: 0` · `rr_kapisi_r: 1.5` (ya da 2.0 = 08-10 öncesi) · `notr_fade_acik: 1`.
Config yedeği: `kripto-config.json.yedek-2026-08-10b`.

## ⭐⭐ %10 HEDEF ÖLÇÜMÜ · LONG ARAYIŞI · AŞAMA ÖRTÜŞMESİ (2026-08-10, kullanıcı kararı)

**Talep:** *"long işlemde açsın sadece short değil · long işlem ara, gainers'da önemli olan bu ·
kazananların gösterdiği özellikler hangi AŞAMADA örtüşüyor bunu bul · yüzde 10 kazanç hedefle,
ona göre ölç · aynı anda aynı sinyalleri üretmesi önemli · pumplara bakalım"*

**Ne değişti:** tüm önceki ölçümler **2R hedefliydi**. Bu ölçüm sabit **%10 hedefli** — ödeme
profili tamamen farklı. Stop medyanı %1,4-5 → %10 hedef 2-7R uzakta; isabet oranı düşer ama
tek kazanç büyür. Başabaş = `stop% ÷ (10 + stop%)`. Maliyet %0,09 (gidiş-dönüş taker) düşüldü.
Araçlar: `scratchpad/hedef10.py` · `pump10.py`.

### BULGU 1 ⭐⭐ — CANLIDAKİ A+B KAPISI %10 HEDEFİYLE DAHA DA İYİ DOĞRULANDI

| Küme | N | SHORT net % | isabet | başabaş | A yarısı | B yarısı |
|---|---|---|---|---|---|---|
| tüm olaylar | 7118 | −0.06% | %12.0 | %12.8 | −0.15 | +0.03 |
| **A+B (canlıdaki kapı)** | 206 | **+2.19%** | %37.9 | %29.4 | **+2.05** | **+2.36** |
| **A+B + pump kapısı** | 201 | **+2.30%** | %37.8 | %28.9 | **+2.27** | **+2.33** |
| **A+B ∩ HAZIRLANIYOR** | 32 | **+4.63%** | **%56.2** | %32.9 | +3.67 | +5.38 |
| A+B ∩ izle | 170 | +1.75% | %34.1 | %28.5 | +1.75 | +1.75 |
| HAZIRLANIYOR (tek) | 113 | +1.91% | %29.2 | %19.0 | +1.75 | +2.05 |
| skor ≥ 45 | 275 | +1.53% | %32.7 | %25.6 | +1.52 | +1.53 |

A+B'nin iki zaman yarısı **+2.27 / +2.33** — neredeyse aynı. Bu, 2R ölçümündeki
(+0.277 / +0.528) dalgalanmadan daha kararlı: **%10 hedefi bu edge'e daha uygun.**

### BULGU 2 ⭐⭐ — "HANGİ AŞAMADA ÖRTÜŞÜYOR": **HAZIRLANIYOR**

| Aşama | N | LONG net % | SHORT net % | SHORT isabet |
|---|---|---|---|---|
| **HAZIRLANIYOR** | 113 | −0.08% | **+1.91%** | %29.2 |
| BASLIYOR | 24 | −0.11% | +0.64% | %29.2 |
| izle | 6981 | −0.37% | −0.10% | %11.7 |

Ve kesişim: **A+B ∩ HAZIRLANIYOR → +4.63%, isabet %56,2** — A+B'nin tek başına iki katı.
HAZIRLANIYOR = `comp<0.65` (sıkışmış) + `|last3|<%4` (fiyat yatay) + `oi24>%8` (pozisyon
birikiyor) = **pump ÖNCESİ hal**. Yani kazananların özellikleri tam da harekete geçmeden
önceki sıkışma anında örtüşüyor. N=32 → **izlenim, kural yapılmadı** (iki yarıda da pozitif
olması umut verici: +3.67 / +5.38).

### BULGU 3 — LONG: her yere bakıldı, pozitif hücre YOK
**Pump'lar, tüm evren (570 sembol, radar filtresi YOK), %10 hedef:**

| Tetik | giriş | LONG net % | SHORT net % |
|---|---|---|---|
| 24h > %10 (N=2690) | hemen | −0.36% | −0.15% |
| | +6 saat | −0.56% | −0.00% |
| | +24 saat | −0.25% | +0.06% |
| 24h > %15 (N=1411) | hemen | −0.46% | −0.04% |
| | +6 saat | −0.88% | **+0.18%** |
| 24h > %25 (N=614) | hemen | −1.03% | +0.05% |
| | +6 saat | −0.56% | **+0.55%** |
| | +12 saat | −0.14% | +0.08% |

**3 tetik eşiği × 5 giriş zamanlaması × 2 ufuk (72/168 saat) = 30 hücre. LONG hiçbirinde
pozitif değil.** Hareket büyüdükçe LONG kötüleşiyor (%25-40 → −1.29%, %40-70 → −2.27%).

**Uzanım kırılımı (20-bar tepesinden ATR uzaklığı) — en keskin ayrım:**

| Uzanım | N | LONG net % | SHORT net % | SHORT isabet |
|---|---|---|---|---|
| 0–0.5 ATR | 703 | −0.31% | −0.01% | %13 |
| 0.5–1.5 ATR | 513 | −0.56% | −0.23% | %21 |
| 1.5–3.0 ATR | 139 | −0.04% | −0.40% | %29 |
| **3.0+ ATR (çok uzamış)** | 34 | **−3.56%** | **+3.73%** | **%56** |

Radar arşivinde LONG'un en iyi hücresi: `funding ≥ +0.05` (longlar kalabalık) → **+0.69%**,
isabet %38,0 / başabaş %36,8 — **kıl payı** ve yarılar dağılıyor (A +1.84 / B +0.14). Edge değil.

### KARAR: LONG gerçek deftere AÇILMADI, GÖLGEDE canlı test ediliyor
Kullanıcı LONG istedi; ölçüm hiçbir yerde destek vermedi. Tezi çöpe atmak yerine **risksiz
canlı teste** aldık: `golge_long_pump = 1` → `chg24 ≥ %10` **ve** `vol_x ≥ 2.0` olan her adayda
**gölge defterde LONG açılır**, botun AYNI çıkış kurallarıyla (stop / 1.5R kısmi / trailing)
izlenir. Gerçek defter, equity, kararlar **etkilenmez**. İlk kayıt aynı gün oluştu
(SIREN LONG, `kapi=pump_long_tezi`). 25-30 olay biriktiğinde gerçek karar verilir.

**Gerçek deftere LONG açmak isteniyorsa** tek satır: `notr_long_acik` zaten 1 (NOTR'de
smart-LONG + üç kalite filtresi). Ölçüm bunu desteklemiyor — kayda geçer.

### SINIRLAR
1. 46 günün tamamı AYI/NOTR. **Boğa hücresi yok** — LONG'un asıl sınavı orada, elimizde değil.
2. A+B ∩ HAZIRLANIYOR N=32 → izlenim. Kural yapılmadı.
3. Uzanım 3.0+ ATR hücresi N=34 → izlenim, ama işaret A+B ile aynı yönde (aşırı uzamışı fade).
4. Slipaj yok sayıldı; %10 hedefli işlemler daha uzun tutulur, funding maliyeti de eklenmedi.

## ⭐⭐⭐ HEDEF BOYUTU ÖLÇÜMÜ — "long hedefini %2.5 yapsak" (2026-08-10, kullanıcı önerisi)

**Öneri:** ayı/nötr sezonda LONG hedefi %10 yerine **%2.5** — küçük hedef, yüksek isabet.

### BULGU 1 — Hedefi küçültmek işe yaramıyor, ve sebebi öğretici
LONG, 7.118 olay, botun A-stopu, 72 saat, maliyet %0,09:

| Hedef | isabet | başabaş | net % |
|---|---|---|---|
| %1.5 | %46.1 | %47.4 | −0.18 |
| %2.0 | %40.1 | %40.3 | −0.19 |
| **%2.5** | **%35.3** | **%35.1** | **−0.20** |
| %3.0 | %31.7 | %31.1 | −0.20 |
| %5.0 | %21.6 | %21.3 | −0.29 |
| %10 | %11.3 | %11.9 | −0.37 |

**Her hedefte isabet oranı başabaşa neredeyse EŞİT.** Hedefi küçültmek isabeti tam da
başabaşın gerektirdiği kadar artırıyor — net kazanç doğmuyor. Bu, fiyatın o yönde
**sürüklenmesi olmadığının** imzası: hedef boyutu tek başına edge üretmez, ancak bir giriş
koşulu isabeti başabaşın ÜSTÜNE çıkarırsa edge olur.

Stop varyantları da değiştirmedi (%2.5 hedefle): A-stop −0.20 · 0.75×ATR −0.21 · 1.5×ATR −0.24.
Ufuk 24s/72s farkı yok.

**Tek pozitif LONG hücresi** (%2.5 hedef): `funding ≥ +0.05` → **+0.20%**, N=71,
A +0.34 / B +0.14. Longlar kalabalıkken LONG — küçük ve tek yarıda zayıf, kural yapılmadı.

### BULGU 2 ⭐⭐ — Aynı test A+B'ye uygulanınca: edge HEDEF BÜYÜDÜKÇE ARTIYOR
A+B (funding ≤ −0.05 & oi24 ≥ %10), SHORT, N=206:

| Hedef | isabet | başabaş | net % | A yarısı | B yarısı |
|---|---|---|---|---|---|
| %1.5 | %72.3 | %73.5 | +0.14 | +0.31 | −0.05 |
| %2.0 | %68.4 | %67.5 | +0.22 | +0.31 | +0.12 |
| %2.5 | %67.0 | %62.5 | +0.47 | +0.57 | +0.36 |
| %3.0 | %65.0 | %58.1 | +0.72 | +0.78 | +0.65 |
| %5.0 | %56.3 | %45.4 | +1.33 | +1.17 | +1.51 |
| %7.5 | %45.6 | %35.7 | +1.63 | +1.66 | +1.59 |
| **%10** | %37.9 | %29.4 | **+2.19** | +2.05 | +2.36 |
| %15 | %15.0 | %21.7 | +2.36 | +2.06 | +2.69 (isabet başabaşın ALTINA düştü) |

**A+B'de isabet, başabaşı hedef büyüdükçe daha çok geçiyor** — LONG'un tam tersi. Yani A+B
gerçek bir aşağı sürüklenme yakalıyor; LONG'da öyle bir sürüklenme yok.

### BULGU 3 ⭐⭐ — Botun ÇIKIŞI A+B edge'inin bir kısmını masada bırakıyor
Aynı 206 A+B girişi, beş çıkış kuralıyla (1h mum, 48s ufuk, maliyet dahil):

| Çıkış kuralı | net % | kazanan | A yarısı | B yarısı |
|---|---|---|---|---|
| **MEVCUT** (kısmi %50 @1.5R + ATR trailing) | **+1.24** | %66.0 | +1.22 | +1.25 |
| kısmi yok, sadece trailing | +1.28 | %66.0 | +1.22 | +1.34 |
| **sabit %10 hedef, trailing yok** | **+2.01** | %50.0 | +1.95 | +2.08 |
| kısmi %5 + hedef %10 | +1.67 | %52.9 | +1.61 | +1.73 |
| kısmi 1.5R + geniş trail (3×ATR) | +1.13 | %66.0 | +1.40 | +0.87 |

**Mevcut çıkış +1.24%, sabit %10 hedef +2.01% — %62 daha fazla, iki yarıda da.**
Bedeli: kazanma oranı %66 → %50 (daha az sıklıkta ama daha büyük kazanç).

**ÖNEMLİ NÜANS:** daha önce (kötü girişlerle) ölçmüştük ki trailing+kısmi üç seçeneğin
EN İYİSİ. Şimdi (iyi girişlerle) en kötülerinden. Çelişki değil, kural: **kötü girişte sıkı
çıkış kaybı keser; iyi girişte sıkı çıkış kazancı keser.** Çıkış kuralı girişin kalitesine bağlı.

### AKSİYON ALINMADI — kullanıcı kararı bekliyor
Öneri: **A+B pozisyonlarına özel sabit %10 hedef** (giriş-koşullu çıkış; diğer dallar
mevcut kısmi+trailing ile kalır). Global değiştirmek diğer dalları bozabilir — onlar için
sıkı çıkış hâlâ doğru.

**SINIR:** ölçüm 1 SAATLİK mumla; bot 1 DAKİKALIK mumla yönetiyor → trailing burada kaba,
gerçek MEVCUT değeri biraz daha iyi olabilir. Sıralamanın değişmesi beklenmez.
46 günün tamamı AYI/NOTR. Funding maliyeti (uzun tutuşta artar) eklenmedi — %10 hedefli
işlemler daha uzun tutulur, bu MEVCUT lehine küçük bir düzeltme demektir.

### EK ÖLÇÜM — "LONG'da stopu ayarlarsak %2.5 yaşar mı?" (2026-08-10, kullanıcı sorusu)

**Tarama:** 11 stop varyantı (0.25–2.00 × ATR ve sabit %0.5–%1.5) × 3 ufuk (6/24/72 saat)
= **33 kombinasyon**, hedef sabit %2.5, N=7.118. Araç: `scratchpad/long25_stop.py`.

**HİÇBİRİ POZİTİF DEĞİL.** En iyisi `stop %0.50 / ufuk 6s` → **−0.14%**, ve zaman bölmesinde
**A −0.14 / B −0.14** — şanslı hücre bile değil, tutarlı negatif. En iyi varyantın koşul
kırılımında da her hücre negatif (`funding ≥ +0.05` dahil: −0.08).

**NEDEN — ikili başabaş formülü yanıltıyor:** dar ATR stoplarında isabet, başabaşı GEÇİYOR
(0.25×ATR/72s → isabet %15.2 vs başabaş %13.4, fark +1.8) ama net yine −0.17%. Sebep formülün
ihmal ettiği iki kalem:
1. **Zaman aşımı çıkışları** (ne stop ne hedef) — ortalamada negatif kapanıyorlar.
2. **Maliyet** — %0,09 gidiş-dönüş, %2.5 hedefin **%3,6'sı**. Küçük hedefte maliyet oransal
   olarak büyük; ikili formül bunu görmez.

**SİMETRİ:** aynı tarama SHORT tarafında da negatif (en iyi 1.5×ATR/72s → **+0.01%**, sıfır).
Yani **%2.5 hedef her iki yön için de kötü bir hedef** — bu, A+B'yi %10'a çekme kararını
bağımsız olarak destekliyor.

> **HÜKÜM:** LONG'un sorunu stop ayarı değil. Hedef boyutu, stop genişliği ve ufuk üç eksende
> tarandı (6 hedef × 11 stop × 3 ufuk) — pozitif hücre yok. Ayı/nötr rejimde **yukarı yönde
> sürüklenme yok**; hiçbir çıkış ayarı olmayan bir edge'i var edemez. LONG'un gerçek sınavı
> boğa rejiminde ve o veri elimizde değil. Gölge defterdeki `pump_long_tezi` canlı ölçümü
> devam ediyor — karar oradan gelecek.

**YÖNTEM NOTU (dürüstlük):** bu bir **eşik taramasıdır** ve projede normalde yasaktır. Burada
meşru çünkü amaç "en iyi eşiği bulup koda koymak" değil, "böyle bir eşik VAR MI" sorusunu
kapatmak. Nitekim bulunan en iyi hücre bile negatif çıktı — koda hiçbir şey girmedi.

## ⭐⭐⭐ YÜKSELENLERİN ORTAK ÖRÜNTÜSÜ — bizim göstergelerimizden BAĞIMSIZ (2026-08-10)

**Talep (kullanıcı):** *"bizden bağımsız, bu coinler ortak olarak hangi sinyalleri verdi —
aynı rejim, yükselmiş, yükseldiği andaki tüm coinlerin arasındaki örüntüyü bul."*

**Parametreler (kullanıcı seçti):** yükseliş = 24 saatte **+%10** (ilk kez eşiği aştığı bar) ·
an = **tetik barının kendisi** · evren = **tüm 570 USDT perp, yalnız fiyat/hacim** ·
rejim = 46 günün tamamı (AYI/NOTR, tek rejim).

**Yöntem:** radar skoru/stage'i **hiç kullanılmadı**; ham OHLCV'den 24 ölçü türetildi.
**Eşleşmiş kontrol:** her yükseliş için aynı sembolden, aynı dönemde rastgele bir bar
(sembol ve dönem etkisi sabitlenir). Rastgele olsaydı her ölçüde %25 çıkardı.
**1.673 yükseliş olayı · 1.673 kontrol · 565 sembol.** Araç: `scratchpad/yukselen_oruntu.py`.

### ⚠️ ÖNCE TOTOLOJİ AYRIMI (bu olmadan tablo yanıltıcı)
Tetik "24h getiri > +%10" olduğu için şu ölçüler **tanım gereği** ayrışır, bulgu değildir:
`chg_24h` (%100) · `ma50_mesafe` (%95.8) · `pos20` (%91.4) · `chg_6h` (%90.0) · `chg_1h` (%87.7) ·
`ma200_mesafe` (%73.3) · `dip7g_yukselis` (%71.4) · `chg_72h` (%69.3) · `ardisik_yesil` (%69.2) ·
`pos168` (%67.5) · `govde_orani` · `zirve30g_uzaklik` · `sikisma` · `atr_patlama`.
Bir coin %10 yükseldiyse zaten aralığın tepesinde, MA'nın üstünde ve ATR'si patlamış olur.

### ⭐ GERÇEK BULGU — tek bağımsız ve kararlı ortak sinyal: **HACİM**

| Ölçü (totolojik olmayan) | yükselen med | kontrol med | ayrım | A yarısı | B yarısı |
|---|---|---|---|---|---|
| **hacim_kat_1h** (tetik barı / 24-bar medyan) | **4.34×** | 0.99× | **%81.0** | %78.4 | %83.5 |
| hacim_kat_24h | 1.61 | 0.94 | %58.2 | %56.8 | %59.7 |
| atr_pct | %2.34 | %1.64 | %44.4 | %45.6 | %43.2 |
| hacim_kat_7g | 1.12 | 0.91 | %38.7 | %36.9 | %40.6 |
| islem_sayisi | 2412 | 1911 | %28.9 | %26.5 | %31.4 |
| hacim_musd (likidite) | $0.14M | $0.10M | %28.4 | %27.8 | %29.0 |
| **taker_alis_pay** | 3.33 | 3.28 | **%24.8** | %20.8 | %28.8 |
| **utc_saat** | 11 | 12 | **%20.3** | %18.9 | %21.6 |

**Yükselen coinlerin ortak yanı bir tanedir: tetik barında hacim patlaması (medyan 4.3×).**
%81 oranıyla kontrolün üst çeyreğinin dışında ve iki zaman yarısında da aynı (%78 / %84).

**Ayırt ETMEYEN, kayda değer üç ölçü:**
- **taker alış payı %24.8 = tam rastgele.** "Agresif alıcı" fikri tetik anında hiçbir şey söylemiyor.
- **likidite %28.4** — yani sadece küçük/ince coinler değil; büyükler de aynı oranda yükseliyor.
- **UTC saati %20.3 = rastgele.** Saat/seans etkisi yok.

**TARAMA ARTIĞI YAKALANDI:** `listelenme_bar` toplamda %34.2 ayırıcı görünüyordu ama zaman
bölmesi **A %67.8 / B %0.8** verdi — pencere yapaylığı (yeni listelenenlerin bar sayısı dönemle
korelasyonlu). Zaman bölmesi tam da bunun için var; ölçü elendi.

### ⭐⭐ ASIL SONUÇ — örüntü TANIMLAYICI, TAHMİN EDİCİ DEĞİL
Aynı 1.563 olayda tetik barından sonra ne olduğu:

| | medyan | ortalama | pozitif |
|---|---|---|---|
| **+24 saat** | **−2.62%** | −0.74% | **%34** |
| **+72 saat** | **−3.98%** | −1.28% | %34 |
| +24s en yüksek nokta | +5.50% | | |

Ve ortak sinyalin **şiddeti hiç yardım etmiyor** — hatta ters:

| hacim katı | N | +24s medyan | pozitif | A yarısı | B yarısı |
|---|---|---|---|---|---|
| 0–2× | 399 | −1.87% | %35 | −0.13 | −1.49 |
| 2–4× | 341 | −1.86% | %36 | −0.96 | +0.55 |
| 4–8× | 318 | −2.78% | %35 | −1.96 | −0.89 |
| 8–20× | 275 | −2.91% | %33 | −0.57 | −1.30 |
| **20×+** | 230 | **−4.90%** | **%26** | −3.39 | +2.60 |

**En güçlü ortak sinyal, en kötü devamı veriyor.** Yükselenler birbirine benziyor (hacim), ama
bu benzerlik hangisinin devam edeceğini ayırmıyor — tam tersine, hacim ne kadar patlarsa
sonraki 24 saat o kadar kötü.

### 🔁 BAĞIMSIZ DOĞRULAMA (dikkat çekici)
`+24 saat medyan −2.62%` — defterdeki **erken-kuşak** ölçümünün (N=298, medyan **−2.62%**)
**birebir aynı sayısı.** Farklı evren (570 sembol vs radar'ın 384'ü), farklı yöntem, farklı
tarih aralığı, aynı sonuç. Bu, "hareketi kovalama tuzağı" bulgusunun en güçlü teyidi.

### HÜKÜM
1. **Sorunun cevabı:** yükselen coinlerin ortak sinyali **hacim patlaması**, başka hiçbir şey değil.
   Taker alış payı, likidite, saat, listelenme yaşı — hiçbiri ayırt etmiyor.
2. **Ama bu sinyal bir GİRİŞ KURALI olamaz**, çünkü sonrasını tahmin etmiyor (medyan −2.62%)
   ve şiddeti arttıkça kötüleşiyor.
3. **Açık kalan tek yol:** hareket ÖNCESİ pencere (tetikten 1-6 saat önce). Kullanıcı bu turda
   "tetik anının kendisi"ni seçti; öncesi ölçülmedi. Örüntü orada varsa kullanılabilir olurdu.

**SINIR:** tek rejim (46 gün AYI/NOTR) · funding/OI yok (tam evren için mevcut değil) ·
tetik anı seçildiği için "önceden görülebilirlik" bu ölçümün konusu değil.

## ⭐⭐⭐⭐ HAREKET ÖNCESİ ÖRÜNTÜ — sinyal VAR, ama neden işe yaramadığı ÇÖZÜLDÜ (2026-08-10)

**Kalan tek soru:** tetik anında örüntü tanımlayıcıydı; ya hareketin **öncesi**?
225.056 bar tarandı, 570 sembol, 46 gün. Araçlar: `scratchpad/oncesi_oruntu.py` · `oncesi_getiri.py`.

### A) GERİYE BAKIŞ — yükselenlerin öncesi ayrışıyor mu? (rastgele = %25)

| Ölçü | −1s | −3s | −6s | −12s | −24s |
|---|---|---|---|---|---|
| chg_24h | 90.0 | 72.4 | 54.4 | 33.7 | 42.5 |
| pos20 | 78.7 | 66.4 | 62.0 | 44.8 | 44.3 |
| chg_6h | 76.0 | 59.1 | 52.9 | 48.3 | 45.1 |
| **hacim_kat_1h** | **63.6** | 49.5 | 39.7 | 31.3 | 33.6 |
| atr_patlama | 56.4 | 46.8 | 36.7 | 29.5 | 26.2 |
| sikisma | 51.2 | 42.5 | 39.3 | 27.0 | 27.4 |
| **taker_alis_pay** | **25.6** | **25.2** | **25.6** | **25.7** | **26.0** |

Ayrışma **−1 saatte güçlü, −6 saatte yarılanmış, −24 saatte gürültü.** Yani "önceden görme
penceresi" pratikte 1-3 saat. Taker alış payı **beş mesafede de tam rastgele** — kayda değer.

### B) İLERİYE BAKIŞ — bu özelliğe sahip barların kaçı tetiğe yol açtı?
**Taban oran %5.68** (rastgele bir bardan sonraki 24 saatte +%10 tetiği olma olasılığı):

| Koşul | N | tetik % | **KAT** | A yarısı | B yarısı |
|---|---|---|---|---|---|
| **chg_6h ≥ %3** | 16.420 | **19.29%** | **3.40** | 19.47 | 19.09 |
| hacim≥3 & chg_6h≥3 | 5.490 | 18.93% | 3.33 | 18.97 | 18.87 |
| hacim≥6 & pos20≥0.85 | 1.419 | 16.35% | 2.88 | 16.57 | 16.15 |
| chg_24h %3-8 (usulca) | 26.604 | 12.50% | 2.20 | 12.30 | 12.73 |
| pos20 ≥ 0.85 | 20.536 | 11.61% | 2.05 | 12.72 | 10.57 |
| hacim_kat_1h ≥ 6 | 6.015 | 11.27% | 1.99 | 11.56 | 10.96 |
| **sikisma < 0.65** | 11.575 | **5.33%** | **0.94** | 5.68 | 4.93 |
| pos20 ≤ 0.15 | 33.967 | 3.49% | 0.61 | 3.66 | 3.33 |

**Tahmin edici yapı GERÇEKTEN VAR:** `chg_6h ≥ %3` tetik olasılığını **3,4 katına** çıkarıyor,
iki zaman yarısında da neredeyse aynı (19.47 / 19.09). Bu bir tarama artığı değil.
**Sıkışma (HAZIRLANIYOR'un çekirdeği) hiçbir şey söylemiyor: KAT 0.94.**

### C) ⭐ AMA PARA KAZANDIRMIYOR — ve nedeni tam olarak ölçüldü
Aynı sinyallerde LONG açılsaydı (botun A-stopu, maliyet %0,09):

| Sinyal | hedef %2.5 net | isabet | başabaş | ham +24s medyan | pozitif |
|---|---|---|---|---|---|
| chg_6h ≥ %3 | **−0.27%** | %39.8 | %44.3 | −1.03% | %40 |
| hacim≥3 & chg_6h≥3 | −0.22% | %43.0 | %46.1 | −1.50% | %36 |
| hacim≥6 & pos20≥0.85 | −0.28% | %40.1 | %45.7 | −1.67% | %36 |
| pos20 ≥ 0.85 | −0.14% | %31.6 | %34.4 | −0.45% | %43 |
| **KONTROL (rastgele)** | **−0.13%** | %27.8 | %28.6 | **−0.24%** | **%46** |

**Her sinyal kontrolden DAHA KÖTÜ.** Ve %10 hedefte de aynı (hepsi −0.15…−0.31, kontrol −0.26).

### ⭐⭐ MEKANİZMA — "hareket kovalama tuzağı"nın matematiksel açıklaması
Sinyal isabeti **gerçekten artırıyor**: kontrol %27.8 → chg_6h≥3 ile %39.8 (**+%43**).
Ama aynı sinyal **stop mesafesini daha çok genişletiyor**: kontrol %1.00 → sinyalde %1.99 (**+%99**).
Başabaş oranı stop mesafesiyle birlikte yükseldiği için (%28.6 → %44.3), artan isabet
yetmiyor — net kötüleşiyor.

> **GENELLENEBİLİR KURAL:** *Yön değil sadece HAREKET öngören her sinyal değersizdir,
> çünkü stop mesafesi hareketle birlikte büyür ve fazladan isabeti fazlasıyla yer.*
> Bir sinyalin işe yaraması için isabeti, stop genişlemesinden **daha hızlı** artırması gerekir.
> A+B tam da bunu yapıyor (isabet %37.9 / başabaş %29.4, hedef %10) — çünkü yönü de söylüyor.

Bu, projedeki tüm "kovalama" ölçümlerinin (erken-kuşak, beta-rotasyon, breakout, F1,
gainer'a binme) ortak sebebini tek cümlede topluyor. 225.056 barla ölçüldü.

### HÜKÜM
1. Hareket öncesi tahmin edici yapı **var** (3,4 kat) ve **kararlı** — ama yalnızca hareketin
   *olacağını* söylüyor, *yönünü* değil.
2. Bu yapıyla LONG açmak kontrolden kötü. **Kod değişikliği YOK.**
3. Sıkışma tabanlı "pump öncesi" sezgisi (HAZIRLANIYOR'un çekirdeği) tetik tahmininde
   **hiçbir şey** katmıyor (KAT 0.94) — ama A+B ∩ HAZIRLANIYOR hücresi SHORT tarafında güçlü
   (+4.63%), yani değeri "pump öncesi" olmasından değil **fade kurulumu** olmasından geliyor.

**SINIR:** tek rejim (46 gün AYI/NOTR) · funding/OI tam evrende yok · yalnız LONG denendi
(sinyal yön söylemediği için SHORT'u da ayrıca ölçmek gerekirdi; A+B zaten o işi yapıyor).

### EK — hareket öncesi sinyal SHORT tarafında da ölçüldü (2026-08-10, kullanıcı yakaladı)

**Kullanıcı: "bunu sadece short için mi yaptın"** → Hayır, **tam tersi**: önceki ölçüm yalnız
LONG'du. Sınırı kendi notumda yazmıştım ama kapatmamıştım. Kapatıldı (`scratchpad/oncesi_short.py`).

**Ön-kayıt:** sinyal yön değil hareket öngörüyordu ve tetik sonrası fiyat düşüyordu
(+24s medyan −2.62%) → aynı sinyallerde SHORT, LONG'dan **iyi** olmalı. Eğer SHORT da negatifse
sinyal tamamen değersizdir.

| Sinyal (hedef %2.5 / 24s) | N | LONG net | SHORT net | SHORT isabet | S: A yarısı | S: B yarısı |
|---|---|---|---|---|---|---|
| chg_6h ≥ %3 | 7.984 | −0.27% | **−0.04%** | %34.2 | −0.01 | −0.07 |
| hacim≥3 & chg_6h≥3 | 3.809 | −0.22% | −0.18% | %32.4 | −0.12 | −0.25 |
| hacim≥6 & pos20≥0.85 | 1.391 | −0.28% | −0.27% | %26.0 | −0.28 | −0.26 |
| chg_24h %3-8 | 8.312 | −0.18% | −0.07% | %30.4 | −0.06 | −0.09 |
| hacim_kat_1h ≥ 6 | 4.963 | −0.21% | −0.13% | %32.3 | −0.19 | −0.07 |
| **KONTROL (rastgele)** | 3.930 | −0.13% | **−0.10%** | %29.4 | −0.06 | −0.14 |

%10 hedef / 72s'de de aynı: hepsi negatif (SHORT −0.09…−0.13, kontrol −0.21).

**SONUÇ — sinyal İKİ YÖNDE DE değersiz.** Ortalamaya-dönüş eğilimi görünüyor (her satırda
SHORT, LONG'dan daha az negatif — ön-kayıtlı beklenti tuttu) ama hiçbiri kontrolü anlamlı
geçmiyor, hiçbiri pozitif değil. En iyisi `chg_6h ≥ %3` SHORT −0.04% (kontrol −0.10%) — fark
0,06 puan, maliyet gürültüsü seviyesinde.

> **Hareket öncesi örüntü dosyası KAPANDI.** Yapı var (tetik olasılığını 3,4 katına çıkarıyor,
> iki yarıda kararlı) ama ne LONG ne SHORT tarafında paraya çevrilebiliyor. Sebep yukarıda
> ölçülmüş mekanizma: yön söylemeyen bir sinyal, stop mesafesini isabetten daha hızlı büyütür.

## ⭐⭐⭐⭐ YÖN AVI — ikinci SHORT kapısı bulundu, LONG hâlâ yok (2026-08-10)

**Talep:** *"yönü bulmaya çalışalım eldeki veriyle, yönü diğer verilerle karşılaştırmalı test et
ve yön sinyali ara."*

**Neden yeni bir ölçüm tasarımı:** bu oturumun bulgusu — yön söylemeyen sinyal değersiz, çünkü
stop mesafesi hareketle büyür. Ama stop/hedef mekaniği **yönü de gizliyor**. O yüzden burada
**stop yok, hedef yok**; sadece ham ileri getiri. Ve asıl ölçü:
**`rel24` = coin 24s getirisi − BTC 24s getirisi.** Ayı piyasasında her şey düşer; "daha az düşen"
yön sinyali değildir. **Yön = piyasadan ayrışma.**
6.790 olay · taban rel24 medyan **−0.46%**. Araçlar: `scratchpad/yon_avi.py` · `yon_dogrula.py`.

### ⚠️ ÖNCE YAKALANAN HATA (kayda geçer)
İlk turda "taker alış payı" güçlü bir yön sinyali göründü (−1.57). **Birim hatasıydı:**
`tbv` (taker buy **BASE** volume, kline[9]) `qv` (**QUOTE** volume, kline[7]) ile bölünmüştü →
sonuç ≈ `taker_oranı ÷ fiyat`, yani pratikte **1/fiyat**. Yani ölçtüğüm şey taker davranışı değil,
**fiyat seviyesiydi**. Düzeltildi (`tbv/v`, ikisi de base):
**gerçek taker oranı yön gücü −0.07 (A +0.10 / B −0.25) = RASTGELE.**
Fiyat seviyesi ise ayrı bir ölçü olarak bırakıldı ve gerçek bir sinyal çıktı.

### 1) KARARLI YÖN ÖLÇÜLERİ (rel24, üst dilim − alt dilim, iki yarıda da aynı işaret)

| Ölçü | alt dilim | üst dilim | YÖN GÜCÜ | A yarısı | B yarısı |
|---|---|---|---|---|---|
| MA50 mesafesi % | −0.35 | −2.10 | **−1.76** | −1.70 | −1.87 |
| **fiyat seviyesi (log10)** | −1.57 | +0.00 | **+1.57** | +2.18 | +1.03 |
| radar skoru | −0.13 | −1.68 | −1.55 | −1.94 | −1.27 |
| son 24 saat % | −0.72 | −2.16 | −1.44 | −1.31 | −1.65 |
| MA200 mesafesi % | −0.40 | −1.83 | −1.43 | −1.64 | −1.14 |
| açık pozisyon 24s % | −0.77 | −1.68 | −0.91 | −1.13 | −0.73 |
| piyasa değeri | −0.14 | −0.65 | −0.51 | −0.57 | −0.32 |

**Hepsi aynı yöne bakıyor: MA'ların üstünde, yükselmiş, pozisyon birikmiş, ucuz coin →
BTC'nin ALTINDA performans.** Yani yön sinyalinin tamamı SHORT tarafında.

**RASTGELE ÇIKANLAR:** gerçek taker oranı (−0.07) · sıkışma (−0.17) · hacim katı (+0.03) ·
son 3 saat (−0.01) · BTC 3s (−0.04) · range konumu (+0.16). Funding tek başına kararsız
(A +1.35 / B +0.14) — **A+B'nin gücü funding'den değil, funding × oi24 kesişiminden geliyor.**

### 2) ⭐ TİCARET MEKANİĞİNDE (hedef %10 / 72 saat, A-stop, maliyet %0.09)

| Hücre | N | net % | isabet | başabaş | A yarısı | B yarısı |
|---|---|---|---|---|---|---|
| **SHORT: A+B (canlıdaki kapı)** | 197 | **+2.14** | %37.6 | %28.7 | +2.38 | +1.90 |
| **SHORT: MA50 yüksek + fiyat düşük** | **460** | **+0.84** | %29.8 | %25.9 | **+0.99** | **+0.72** |
| SHORT: A+B + fiyat düşük | 113 | +1.61 | %33.6 | %29.3 | +2.31 | +0.67 |
| SHORT: fiyat düşük (tek) | 1359 | +0.20 | %21.0 | %22.1 | +0.58 | −0.08 |
| LONG: MA50 düşük + fiyat yüksek | 120 | +0.27 | %9.2 | %8.9 | **−0.09** | +0.86 |
| LONG: fiyat yüksek + chg24 düşük | 113 | +0.22 | %8.0 | %8.8 | **−0.47** | +1.16 |
| KONTROL SHORT | 6790 | −0.05 | %12.0 | %12.7 | −0.11 | +0.01 |
| KONTROL LONG | 6790 | −0.35 | %11.2 | %11.8 | −0.43 | −0.27 |

### 3) BULUNAN: ikinci SHORT kapısı — **MA50 yüksek + fiyat düşük**
- N=**460** (A+B'nin 2,3 katı olay) · net **+0.84%** · **iki yarıda da pozitif** (+0.99 / +0.72)
- Türkçesi: *ucuz bir coin MA50'nin belirgin üstüne çıkmışsa* → aşağı.
- **Yalnız 1 saatlik mumdan hesaplanır** — funding/OI/Pillar D gerekmiyor, ek API çağrısı yok.

**Örtüşme ve birleşik katkı** (hedef %10/72s, toplam = N × net%):

| Küme | N | net % | toplam |
|---|---|---|---|
| A+B | 197 | +2.14 | +422 |
| MA50+fiyat | 460 | +0.84 | +390 |
| kesişim | 65 | **+2.53** | +165 |
| yalnız A+B | 132 | +1.95 | +257 |
| **yalnız MA50+fiyat** | **407** | **+0.55** | +226 |
| **BİRLEŞİM** | **604** | +1.07 | **+648** |

İkinci kapıyı eklemek toplam katkıyı **+422 → +648 (%54 artış)** yapıyor; bedeli işlem başı
beklentinin +2.14'ten +1.07'ye düşmesi. **Kesişim en güçlü hücre (+2.53, isabet %44.6).**

### 4) LONG — hâlâ kararlı hücre YOK
İki LONG hücresi toplamda pozitif ama **ilk yarıda negatif** (−0.09 ve −0.47), gücün tamamı
ikinci yarıdan geliyor. Tek dönemlik = kural yapılamaz. Yön avında da LONG tarafı yalnızca
"fiyat seviyesi yüksek" (major coinler) üzerinden ve o da rel24 +0.00 (başabaş).

> **HÜKÜM:** Yön sinyali **var** ve tamamı SHORT tarafında. Yeni kapı adayı bulundu
> (MA50 yüksek + fiyat düşük, N=460, iki yarıda da pozitif, ek veri gerektirmiyor).
> LONG için 46 günlük ayı/nötr veride kararlı hiçbir hücre yok — LONG'un sınavı hâlâ boğada.

**AKSİYON ALINMADI** — ikinci kapı kullanıcı kararı bekliyor.
**SINIR:** tek rejim · fiyat seviyesi bir *coin-tipi* göstergesi (ucuz coin = genelde yeni/spekülatif),
rejim değişince ilişki dönebilir · kesişim hücresi N=65 (izlenim).

### UYGULANDI — ikinci SHORT kapısı canlıda (2026-08-11, kullanıcı: "ekle")

**Kural:** `fiyat ≤ $0.07` **ve** `MA50 mesafesi ≥ %3.72` → **SHORT**.
*Ucuz bir coin 50 saatlik ortalamasının belirgin üstüne çıkmışsa → aşağı.*

**Eşikler icat edilmedi:** ikisi de ölçümün kendi dağılımının çeyreğinden —
fiyat %20'lik dilim ($0.07), ma50_mesafe %80'lik dilim (%3.72).

**Kod değişiklikleri:**
- `radar.analyze`: pencere 50 → **60 bar** (50 barla MA50, fiyatın kendisini de içeren dejenere
  bir ortalamaydı). Diğer tüm hesaplar kuyruk dilimi kullanıyor (son 6/20/24 bar) → **skor ve
  stage birebir aynı kaldı**. Yeni alan: `ma50_mesafe`.
- `testbot.karar_yon`: A+B'nin hemen ardına yeni kapı; yalnız `rejim ∈ (AYI, NOTR)`,
  **TAM_BOGA'da kapalı**.
- **Çıkış A+B ile aynı:** sabit %10 hedef, kısmi kâr ve trailing kapalı (ölçüm o hedefle yapıldı).
- `_aday_arsivle`: `ma50_mesafe` arşive yazılıyor → kapının karnesi geriye dönük çözümlenebilir.
- Config: `ma50_kapisi_acik=1` · `ucuz_fiyat_esik=0.07` · `ma50_mesafe_esik=3.72`.

**Birim testleri (hepsi geçti):** ucuz+MA50 üstü → SHORT/ANINDA · pahalı → karar-yok ·
eşik altı → karar-yok · pumplamış → VETO:blowoff · aşırı düşmüş → karar-yok ·
AYI → SHORT/ANINDA · BOĞA → karar-yok. Sabit %10 hedef doğrulandı (hedef mesafesi %10.00,
`cikis_modu=sabit_hedef`); diğer dalların girişinde `cikis_modu=None` (değişmedi).

**CANLI TUR:** kapı ilk turda tetiklendi — SQD ve GWEI koşulu sağladı, **pump kapısı doğru
şekilde bloke etti** (ikisi de 24s'te +%20 üstü).

**CANLI HALİN GERÇEK BEKLENTİSİ** (pump kapısı dahil, hedef %10/72s):

| Küme | N | net % | isabet | A yarısı | B yarısı | toplam |
|---|---|---|---|---|---|---|
| MA50+ucuz (ham ölçüm) | 460 | +0.84 | %29.8 | +0.99 | +0.72 | +386 |
| **MA50+ucuz + pump kapısı (canlıdaki)** | **445** | **+0.82** | %28.8 | +1.09 | +0.62 | +366 |
| A+B + pump kapısı (canlıdaki) | 193 | +2.29 | %37.8 | +2.63 | +1.95 | +442 |
| **BİRLEŞİM (canlı toplam)** | **577** | **+1.09** | %30.0 | +1.30 | +0.94 | **+630** |

Pump kapısı yalnız 15 olay kesiyor — kapıyı bozmuyor.
**Beklenen hız: 577 olay / 46 gün ≈ 12,5 olay/gün.** Bot artık kapasite-sınırlı çalışacak
(8 eşzamanlı pozisyon + 4 saat cooldown), ki bu 18 günde 4 giriş yapan hâline göre kökten fark.

**SINIR (tekrar):** fiyat seviyesi bir **coin-tipi vekili** (ucuz = genelde yüksek arz/yeni/
spekülatif). Rejim değişince ilişki **dönebilir** — boğada ucuz coinler öne geçebilir.
Ham fiyat eşiği zamanla kayar; yeniden ölçülmeden yıllarca bırakılmamalı.
Ölçümün 46 gününün tamamı AYI/NOTR.
**GERİ ALMA:** `ma50_kapisi_acik: 0`. Config yedeği: `kripto-config.json.yedek-2026-08-11`.

---

## 2026-08-11 — BOT İŞLEM AÇIYOR: ilk parti + ÖLÇÜMÜN AĞIRLIK HATASI

**Durum:** iki SHORT kapısı canlıda; 9 saatte **7 kapanış + 2 açık**. Beklenen hız
(12,5 olay/gün) tutuyor — 18 günde 4 giriş yapan bot bitti.

| ts | sym | kapı | stop% | R | sonuç $ | tutuş |
|---|---|---|---|---|---|---|
| 03:38 | PROM | A+B | 1.36 | −1.05 | −149.83 | 0.1s |
| 04:03 | WLFI | MA50+ucuz | 0.42 | −1.18 | −30.28 | 0.1s |
| 04:53 | SQD | MA50+ucuz | 3.96 | −1.02 | −274.51 | 0.4s |
| 09:13 | SQD | MA50+ucuz | 5.44 | −1.01 | −264.71 | 0.3s |
| 09:28 | PROM | A+B | 4.60 | −1.02 | −265.37 | 0.9s |
| **10:23** | **AIOT** | **MA50+ucuz** | **3.96** | **+2.55** | **+333.02** | **2.7s** |
| 11:33 | JST | A+B | 1.23 | −1.06 | −80.28 | 1.5s |

**Toplam −731,96 $.** Equity 8415 (zirve 10000 → düşüş **−%15,9**; HALT eşiği −%25).
Eski dönemin 12 işlemi ayrıca −803 $ (kapılar öncesi).

### 1) İlk parti ölçümle çelişiyor mu? — HAYIR
Ölçümün isabet oranı %30,0. 7 denemede **tam 1 kazanç olasılığı %24,7**; 1 veya daha az
**%33,0**. Beklenen 2,1/7. Yani bu sonuç dağılımın tam ortasında; ne doğrular ne yalanlar.
**Ayırt etmek için gereken:** 2 standart hata güveni ≈ **138 işlem ≈ 11 gün**;
3 SH ≈ 310 işlem ≈ 25 gün. Erken karar vermek yasak.

### 2) ⚠️ ÖLÇÜMÜN AĞIRLIK HATASI — düzeltme
Ölçüm her olayı **eşit notional** ile topluyordu ("olay başına net %"). Bot ise
**risk-önce** boyutlandırıyor: `notional = risk/stop_frac` → **dar stop = büyük pozisyon**.
Bunlar aynı portföy değil. Kaldıraç tavanı (`marjin×kaldirac_max` = sermayenin 1,0 katı)
yüzünden canlı, ikisinin **melezi**.

| Küme | N | A eşit-notional | B saf risk-önce | **C CANLI** | C: A yarı | C: B yarı |
|---|---|---|---|---|---|---|
| A+B | 193 | +2.29 | +1.69 | **+1.37** | +1.43 | +1.31 |
| MA50+ucuz | 445 | +0.82 | +0.48 | **+0.41** | +0.60 | +0.25 |
| **BİRLEŞİM** | **577** | **+1.09** | +0.66 | **+0.58** | +0.70 | +0.49 |
| KONTROL (tüm olaylar SHORT) | 6790 | −0.05 | −0.84 | **−0.14** | −0.21 | −0.08 |

**Dün "+%1,09 / olay" dedim; botun gerçek boyutlandırmasıyla doğrusu +%0,58.**
Kenar hâlâ var (kontrol −0,14; iki yarı da pozitif) ama **yarı yarıya küçük**.

### 3) Kârı yalnız GENİŞ stoplu işlemler taşıyor — ve bot onları KÜÇÜK alıyor

| stop dilimi | N | isabet | başabaş gereken | eşit-not % | CANLI % | ort boyut |
|---|---|---|---|---|---|---|
| < %1.92 | 145 | %10.3 | ~%16 | −0.06 | **−0.06** | **1.00** |
| %1.92–3.40 | 144 | %20.1 | ~%21 | +0.27 | +0.27 | 0.98 |
| %3.40–5.51 | 144 | %33.3 | ~%30 | +1.27 | +0.92 | 0.70 |
| > %5.51 | 144 | %56.2 | ~%44 | +2.89 | **+1.19** | **0.40** |

İsabet monoton artıyor ve mekanik gerekçesi var: **dar A-stop = direnç hemen tepede,
gürültü teğet geçiyor**; geniş stop = yapı gerçekten uzakta. Dar dilim başabaşın altında
kalıyor → matematiksel olarak kaybediyor.
**Ters ağırlık:** kaldıraç tavanı yüzünden bot değersiz dar-stop işlemini sermayenin
**1,00 katıyla**, kârlı geniş-stop işlemini **0,40 katıyla** alıyor. Boyutlandırma
edge'in tam tersine bakıyor. Canlıdaki WLFI'nin **%0,42 stopu** ölçüm dağılımının
**0. yüzdeliği** — 46 günde eşi görülmemiş bir darlık.

### 4) ELE mi GENİŞLET mi? — ELE

| taban | ELE: N | olay/gün | net % | A yarı | B yarı | toplam | GENİŞLET: net % | toplam |
|---|---|---|---|---|---|---|---|---|
| %0.0 (bugünkü) | 577 | 12.5 | +0.58 | +0.70 | +0.49 | +334 | +0.58 | +334 |
| %1.5 | 482 | 10.5 | +0.68 | +0.70 | +0.67 | +329 | +0.52 | +300 |
| **%2.0** | **423** | **9.2** | **+0.78** | **+0.64** | **+0.89** | **+330** | +0.59 | +341 |
| %2.5 | 372 | 8.1 | +0.87 | +0.81 | +0.91 | +322 | +0.60 | +346 |
| %3.0 | 321 | 7.0 | +0.92 | +0.94 | +0.90 | +294 | +0.59 | +342 |

**GENİŞLET işe yaramıyor** — ve sebebi bu oturumun ana dersinin aynısı: stopu %2,0'a itmek
isabeti %11,0 → %13,6 çıkarıyor ama başabaşı %12,1 → %16,7 çıkarıyor. **Başabaş isabetten
hızlı büyüyor.** ("Kovalama tuzağı"nın stop tarafındaki hâli.)

**ELE doğru:** %2,0 tabanında olay başına getiri **+0,58 → +0,78**, toplam kâr neredeyse
aynı (+334 → +330), işlem sayısı **%27 azalıyor**. Yani atılan işlemler net sıfır üretiyor
ama ücret, kayma ve **pozisyon slotu** yiyor.
**Seçim gerekçesi (ön-kayıt uyarınca tablonun maksimumu DEĞİL):** %2,0, isabetin
başabaşın *altında* kaldığı bölgenin sınırı — mekanik olarak savunulabilir tek çizgi.
%2,5 daha yüksek getiri veriyor ama gerekçesi tabloya bakmak olurdu.

**SINIR:** aynı 46 gün, aynı rejim (AYI/NOTR), aynı olay havuzu — bu bir *yeniden ağırlıklandırma*,
bağımsız doğrulama değil. Kapının kendi kenarı hâlâ 138 işlem bekliyor.

---

## 2026-08-11 — FREN RİSKİ ÖLÇÜLDÜ: kenar kendini gösteremeden bot duruyor

**Soru:** kapılar bu hızda çalışırken −%25 HALT freni, kenarın belli olması için gereken
~11 günden ÖNCE tetiklenir mi?

**Yöntem — portföy simülasyonu** (tek işlem ortalaması DEĞİL): 8 slot · 4s cooldown ·
gerçek boyutlandırma · eş zamanlı maruziyet. **Gün-bloklu bootstrap**: 41 gün yerine
konarak yeniden örneklendi. Gün bloğu şart — tek tek olay karıştırmak, aynı gün bütün
shortların birlikte kazanıp birlikte kaybettiği gerçeğini silerdi ve ruin riskini
**sahte şekilde düşürürdü**. Her olayın (stop%, sonuç%, süre) üçgeni bozulmadan taşındı.
2000 yol.

### Bugünkü hâl tehlikeli

| senaryo | 11g HALT | 46g HALT | medyan 46g | %5 alt | medyan dip | kaybeden yol |
|---|---|---|---|---|---|---|
| **S0 bugünkü (risk %3)** | **%57,0** | %97,4 | 1.24 | 0.76 | −%27,7 | %31,4 |
| S1 stop tabanı %2 | %44,4 | %92,5 | 1.48 | 0.80 | −%27,4 | %23,6 |
| S2 maruziyet tavanı 3x | %24,3 | %75,9 | 1.57 | 0.77 | −%26,4 | %25,4 |
| S4 taban %2 + tavan 2x | %12,6 | %56,9 | 1.56 | 0.79 | −%25,3 | %23,2 |
| S5 yalnız risk %3→%2 | %35,0 | %87,7 | 1.32 | 0.78 | −%26,8 | %30,6 |
| S7 risk %2 + taban %2 | %14,9 | %58,1 | 2.33 | 0.84 | −%25,4 | %14,1 |
| S8 risk %2 + taban %2 + tavan 3x | %9,6 | %43,5 | 2.48 | 0.84 | −%23,8 | %12,4 |
| **S9 risk %1,5 + taban %2** | **%4,5** | %24,8 | **2.49** | **0.89** | −%20,4 | **%8,1** |

**Bugünkü ayarın 11 günde freni tetikleme olasılığı %57, 46 günde %97,4.** Yani kenarın
gerçek olup olmadığını öğrenmeden bot neredeyse kesin duruyor. Sistem para kaybettiği
için değil — **medyan 46 gün çarpanı 1.24, yani kazanıyor** — sadece o kadar sert
savruluyor ki fren yolda tetikleniyor.

**Frenin yeri yanlış:** −%25, sistemin **medyan en dip düşüşünün** (−%27,7) neredeyse
tam üstünde. Normal dalgalanmanın medyanına konmuş fren, güvenlik değil yazı-tura.

### ⚠️ TEZAT: agresif ayar DAHA AZ para kazandırıyor
Kullanıcının isteği "daha agresif bot"tu. Ölçüm şunu söylüyor:
**risk %3 → %1,5 indirilince medyan 46 günlük çarpan 1.24'ten 2.49'a ÇIKIYOR** — iki katı.
Sebep karmaşık değil: %3'te yollar erken HALT'a çarpıp işlem yapmayı bırakıyor (%97,4),
%1,5'te hayatta kalıp bileşiklenmeye devam ediyor (%24,8).
**Agresiflik GİRİŞ SIKLIĞINDA doğru çıktı (12 → 4 giriş/18 gün yerine ~12/gün);
POZİSYON BOYUTUNDA yanlış çıktı.** İkisi ayrı kaldıraçlar, ayrı ölçüldüler.

### KENAR SIFIRSA — yanılma maliyeti
Kenar henüz doğrulanmadı (138 işlem gerekiyor). Aynı olaylar, aynı stoplar, aynı gün-içi
kümelenme; sadece beklenti tam sıfıra çekilerek tekrarlandı:

| senaryo | dünya | 11g HALT | 46g HALT | medyan 46g | kaybeden yol |
|---|---|---|---|---|---|
| S0 bugünkü | kenar VAR | %57,0 | %97,4 | 1.24 | %31,4 |
| S0 bugünkü | **kenar YOK** | %89,1 | %100,0 | 0.91 | %69,5 |
| S9 | kenar VAR | %4,5 | %24,8 | 2.49 | %8,1 |
| S9 | **kenar YOK** | %38,6 | %95,5 | 0.86 | %78,1 |

**En önemli satır bu:** S0'da fren tetiklenmesi hiçbir şey söylemiyor (%57 vs %89 —
oran 1,6:1). S9'da tetiklenmesi **kenarın sahte olduğunun güçlü kanıtı** (%4,5 vs %38,6 —
oran **8,6:1**). Yani bugünkü ayar sadece riskli değil, **deneyin bilgi değerini de yok
ediyor**. S9 hem hayatta kalıyor hem ölçüyor.

### ÖNERİ: S9
`islem_risk_pct: 3 → 1.5` · yeni `asgari_stop_pct: 2.0`. Maruziyet tavanı **gerekmiyor**
(S9, tavanlı S8'le aynı medyanı yarı HALT riskiyle veriyor) — daha az parça, daha az kural.

**SINIRLAR (ciddi):**
- Aynı 46 gün, tek rejim (AYI/NOTR). Bootstrap yeni bir rejim üretemez; boğaya dönüşte
  bütün shortlar birlikte kaybeder ve örneklemdeki hiçbir günden kötü olur.
- Gün-bloklu bootstrap **1 günden uzun trendleri kırar** → gerçek ruin riskini
  muhtemelen **OLDUĞUNDAN AZ** gösteriyor. Hata yönü güvenli tarafta değil.
- Simülasyon kenarın +%0,58 olduğunu varsayıyor; "kenar YOK" tablosu bunun alt sınırı.

---

## 2026-08-11 — S9 UYGULANDI + KARAR PENCERESİ ÖN-KAYDI

### Uygulanan (3 parça, tek hamle)

| ne | eski | yeni | nerede |
|---|---|---|---|
| işlem başına risk | %3 | **%1,5** | `testbot.islem_risk_pct` |
| asgari stop mesafesi | (yok) | **%2,0** | `testbot.asgari_stop_pct` (yeni) |
| fren referansı (zirve) | 10000 | **8412,06** | `testbot_state.zirve_equity` |

**Kod:** `yeni_giris_ac` içinde `stop_frac` hesabından hemen sonra `stop_cok_dar` reddi.
Kapı **efektif** stop mesafesine bakıyor — boyutlandırmanın kullandığı değerin aynısı.
Sınır taraması: nominal %1,96 → efektif %1,98 **red** · nominal %1,99 → efektif %2,01 **geçer**.
Kesme efektif %2,00'de tam. Birim testleri: %0,42 red · %2,10 geçer · %4 geçer · %8 geçer;
sabit %10 hedef ve `cikis_modu=sabit_hedef` korundu.

**Risk doğrulaması** (equity 8412 → hedef risk 126,18 $):
stop %2,10 → notional 5594 (0,66× sermaye), risk 118,62 $ (%1,41 — kaldıraç tavanı kırptı) ·
stop %4,00 → notional 3138 (0,37×), risk 126,18 $ (%1,50) ·
stop %8,00 → notional 1573 (0,19×), risk 126,18 $ (%1,50). Hedefin **üstüne** hiç çıkmıyor.

### Zirve sıfırlaması — gerekçe ve kural
Eski 10000 zirvesindeki −803 $, **artık var olmayan bir bota** ait (R/R kapısı açık,
A+B yok, MA50 yok, 18 gün süre sınırı). Fren "şu anki yapılandırma bozulursa dur"
demek için var; eski botun kaybından tetiklenseydi S9'un tek amacı olan "hayatta kal
ve ölç" çalışamazdı (frene %25 değil %11 mesafe kalıyordu).
**Equity'ye ve işlem geçmişine dokunulmadı** (19 kayıt duruyor); yalnız frenin referansı
bugüne çekildi. Gerekçe `testbot_state._zirve_sifirlama` alanına da yazıldı.
**KURAL:** zirve sıfırlaması *yalnızca* yapılandırma esaslı değiştiğinde yapılır ve
defterde gerekçesiyle kaydedilir. Aksi hâlde bu hareket kaybı gizlemenin yolu olur.

### ⚠️ DÜZELTME: "138 işlem ≈ 11 gün" YANLIŞTI
O tahmin 12,5 olay/gün üzerindendi; **slot sınırı ve cooldown'u saymıyordu.**
Simülasyon işlem sayacıyla tekrar koşturuldu (2000 yol):

| senaryo | 11 günde | 46 günde | işlem/gün |
|---|---|---|---|
| S0 bugünkü (risk %3) | 75 | **81** | 1,8 |
| **S9** | **80** | **319** | **6,9** |

**S9 işlem sayısını AZALTMIYOR, 46 günde DÖRT KATINA çıkarıyor.** Sebep: S0 yollarının
%97'si erken HALT'a çarpıp işlem yapmayı bırakıyor — duran bot işlem yapmaz. Stop tabanının
elediği %27, hayatta kalmanın kazandırdığının yanında küçük kalıyor.
**Gerçek hız ~6,9 işlem/gün → 138 işlem ≈ 20 gün, 11 gün değil.**

### KARAR PENCERESİ — ÖN-KAYIT (sonuç görülmeden yazıldı)

| | |
|---|---|
| **Başlangıç** | 2026-08-11 12:45 (S9 yürürlükte) |
| **Pencere** | 138 kapanmış işlem **veya** 30 gün — hangisi önce |
| **GEÇTİ** | toplam net > 0 **ve** pencerenin ikinci yarısı da > 0 |
| **KALDI** | toplam net < 0 **ya da** fren tetiklendi (S9'da fren = kenarın sahte olduğunun 8,6:1 kanıtı) |
| **BELİRSİZ** | toplam > 0 ama ikinci yarı < 0 → pencereyi uzat, karar verme |

**Pencere boyunca hiçbir parametreye dokunulmaz.** Yeni kapı eklenmez, eşik oynatılmaz,
fren taşınmaz. LONG gerçek deftere açılmaz (gölgede 17/25-30 olay birikti, kendi başına dolsun).
Bu kural olmadan pencere ölçüm değil, gözlem olur.

**İŞLETİM NOTU — state yazma yarışı (2026-08-11):** `zirve_equity` düzeltmesi ilk seferde
**ezildi**. Sebep: cycle state'i **başta yükleyip sonda yazıyor**; 12:43'te başlayan tur
12:46:57'de yazınca 12:45'teki elle düzeltmem kayboldu. Sessizce oldu — fark edilmesinin
tek sebebi yazma sonrası doğrulama yapmam. **Kural: `testbot_state.json`'a elle her yazma,
bir cycle bitişinin hemen ardından yapılır ve SONRAKİ cycle'dan sonra doğrulanır.**
İkinci yazma 12:48'de (cycle'dan 94 sn sonra) yapıldı, 12:52:05 turundan sonra `zirve=8412.06`
olarak **doğrulandı**.

**Ayrıca:** bot 5 dakikalık turlarla, her tur **ayrı kısa ömürlü süreç** olarak çalışıyor
(zamanlanmış görev yok, `python testbot.py --cycle`). `tasklist` turlar arası boşluğa
denk gelirse "hiç Python süreci yok" gösterir — bu bot durdu anlamına GELMEZ.
Doğru kontrol: `testbot_state.son_cycle_ts` ve `testbot_equity.jsonl` aralıkları.
(11:17 → 12:06 arasında 49 dakikalık bir boşluk var; sebebi bilinmiyor, izlenecek.)

---

## 2026-08-11 — LONG KARAR ÖLÇÜTÜ: ÖN-KAYIT

**Neden şimdi:** gölge LONG tezi için "25-30 olayda karar verilir" yazılmıştı ama
**geçme ölçütü yazılmamıştı.** Ölçüt sonuçlara bakıldıktan sonra yazılırsa karar değil
gerekçelendirme olur. Bu yüzden pencere dolmadan, rakamlar elde varken sabitleniyor.

**Tez:** `chg24 >= %10 & vol_x >= 2.0` olan adayda **gölgede** LONG açılır, botun
**aynı çıkış kurallarıyla** izlenir. Gerçek para yok, gerçek kurallar var.
Başlangıç: 2026-08-10 17:42.

### Ölçüt (sonuç görülmeden yazıldı)

| | |
|---|---|
| **Pencere** | 25 kapanmış gölge LONG (kronolojik ilk 25) |
| **Yarılar** | ilk 12 / son 13, kronolojik |
| **GEÇTİ** | toplam R > 0 **ve** ikinci yarı > 0 **ve** ortalama ≥ **+0,15R** |
| **KALDI** | toplam R ≤ 0 |
| **BELİRSİZ** | toplam > 0 ama ikinci yarı < 0 → pencereyi 40 olaya uzat, karar verme |

**+0,15R marjı neden var:** gölge defter kaymayı (slippage) ve emir defteri derinliğini
modellemiyor. Sıfırın hemen üstünde bir sonuç, gerçek deftere taşındığında sıfırın altına
düşer. Marj icat edilmedi: A+B kapısının canlıya alınırken kullanılan aynı mantık.

**GEÇERSE bile doğrudan canlıya alınmaz:** önce `islem_risk_pct`'in yarısıyla, yalnız
NOTR rejimde, ayrı bir pencerede ölçülür. Sebep: LONG'un tüm negatif kanıtı duruyor;
gölgenin pozitif çıkması onu çürütmez, sadece "yeniden bakmaya değer" der.

### Ölçütün şu anki karşılığı (14 olay, pencere dolmadı — KARAR YOK)
toplam **−2,09R** · ortalama **−0,16R** · kazanan **%46**.
R'ler: −1,01 · +0,02 · −1,01 · −0,01 · +0,01 · +1,14 · +0,01 · +1,73 · +0,09 · −0,00 ·
−1,02 · −1,03 · −1,01 (+ 14'üncü açık/yeni).
İki iyi kazanç (+1,73, +1,14) beş tam stop tarafından yeniyor. **Arşiv ölçümüyle aynı
yerde: hafif negatif.** Bu satır bilgi olarak duruyor, ölçüt bundan türetilmedi.

### LONG'un neden gölgede olduğunun özeti (tek yerde)
- Tetik eşiği × giriş zamanlaması × ufuk taraması: **30 kombinasyon, hepsi negatif**
- Stop × ufuk taraması (%2,5 hedef, nötr-ayı): **33 kombinasyon, hepsi negatif**
- Yön avı: kararlı altı ölçünün (MA50, fiyat seviyesi, skor, chg24, MA200, oi24)
  **hepsi SHORT tarafını** gösteriyor
- En iyi LONG hücresi `funding >= +0.05` → +%0,69 ama başabaş %36,8 / isabet %38,0
  (kıl payı) ve yarılar dağılıyor (A +1,84 / B +0,14) = **tarama artığı imzası**
- Mekanizma: yükselen coinlerin +24s medyanı **−%2,62** (iki ayrı evrende, iki ayrı
  yöntemle aynı sayı). Hareket öngören ama yön öngörmeyen sinyal değersizdir —
  isabeti +%43 artırırken stop mesafesini +%99 genişletir.

### ⚠️ YAPISAL RİSK — kayıtta kalsın
**Her iki canlı kapı da SHORT.** Rejim katmanı TAM_BOĞA'da ikisini de kapatıyor, yani
boğada bot **kaybetmez ama hiç işlem de yapmaz.** LONG'un olmamasının gerçek bedeli
kayıp değil **körlük**. Çözümü boğa verisi olmadan LONG kapısı uydurmak değil; gölgeyi
çalışır tutup rejim döndüğünde elde ölçüm olması. Bütün ölçümlerin 46 gününün tamamı
AYI/NOTR olduğu için LONG'un kaybetmesi rejimin kendisinden de kaynaklanıyor olabilir.

---

## 2026-08-11 — KANAL + StochRSI ÖLÇÜMÜ: ÖN-KAYIT (sonuç görülmeden, koşturmadan ÖNCE commit edildi)

**Kaynak:** kullanıcı bir X videosundan aldı (`x.com/ralli_kralicesi/status/2084712571748106659`).
**Gönderi açılamadı — HTTP 402 (X API duvarı).** Videoyu göremedim; indikatörün kimliği
belirsizliğini koruyor. Bu yüzden **iki aile birden** ölçülecek (Bollinger + Donchian).

**Kısıt (kullanıcı):** bota dokunulmayacak, sisteme hiçbir ekleme yapılmayacak.
Ölçüm tamamen `scratchpad/` içinde, salt-okunur önbellek üzerinde.

### Veri ve mekanik
- `scratchpad/klines_1h/` — 570 sembol, ~1433 bar (2026-06-12 → 2026-08-10, ~60 gün)
- **1 saatlik** (15dk önbelleği yok; analiz belgesi zaten 1s'i öneriyordu)
- Giriş: **sonraki barın açılışı** (`b[gi]["o"]`) — projenin tüm backtest'leriyle aynı
- Stop: `min(son 10 bar dibi, alt bant) − 0.25×ATR(14)`
- Hedef: **giriş anındaki üst bant, DONDURULMUŞ** — belgede (a) seçeneği; hareketli hedef
  düşen piyasada sahte kazanç üretir
- Aynı barda hem stop hem hedef → **STOP** (kötümser)
- Maliyet **%0,13** (taker 0,045×2 + slipaj 0,02×2). *Not: projenin önceki betikleri %0,09
  kullanıyordu; buradaki sayılar işlem başına ~0,04 puan daha muhafazakâr.*
- Sinyal seyreltme: aynı sembolde en az **24 bar** ara
- Isınma: `i >= 200` (önceki ölçümlerle aynı)

### Ufuk — ÖNCEDEN sabitlendi
- **BİRİNCİL: 12 bar** — `kripto-config.json → maliyet.tutma_saat_tf["1h"] = 12`.
  Benim seçimim değil, config'den geliyor.
- İkincil: 48 bar (yalnız bilgi için; karar birincilden verilir)

### Ölçülecek kümeler
1. **Bollinger LONG** — `düşük ≤ alt bant` + StochRSI aşırı satımdan yukarı kesişim
2. **Bollinger SHORT** — simetrik (üst bant + aşırı alımdan aşağı kesişim)
3. **Donchian LONG / SHORT** — aynı kural, bant = son 20 barın en düşüğü/en yükseği
4. **AYRIŞTIRMA:** yalnız bant teması (StochRSI yok) · yalnız StochRSI kesişimi (bant yok)
   → etkiyi hangi bileşenin taşıdığını görmek için
5. **KONTROL:** aynı sembol/dönemde **rastgele** barlar, aynı mekanik
6. **FİLTRELER:** trend filtresi (`fiyat > MA200`) ve bant genişliği tabanı

### GEÇME ÖLÇÜTÜ (önceden sabit)
1. Net > 0 (maliyet sonrası), **ve**
2. Kontrol grubunu yeniyor, **ve**
3. **Her iki zaman yarısında da** pozitif

Üçü birden sağlanmazsa **KALDI**. Tek yarıda güçlü olması geçmez — tarama artığı imzası budur.

### BEKLENTİM (önceden yazıyorum, yanılırsam kayda geçsin)
**NEGATİF bekliyorum.** Üç gerekçe:
1. Stop yapısı gereği dar; ölçülmüş dilim (`stop < %1,92`) isabet %10,3 / başabaş %16
2. Bu projede LONG tarafı 63 kombinasyonda doğrulanamadı (ayı/nötr rejim)
3. Bant genişliğine oranla maliyet yüksek

**Pozitif çıkarsa bu bilgi değeri YÜKSEK bir sonuçtur** — çünkü tersini önceden yazdım.

### Sınırlar (şimdiden)
- 15 dakikalık değil 1 saatlik → orijinal tarifin birebir testi **değil**
- Tek rejim (46-60 gün, ayı/nötr) · kripto perp · BIST'e taşınmaz
- İndikatör kimliği doğrulanmadı; Bollinger ve Donchian ayrı ayrı ölçülüyor

**ÖN-KAYIT DEĞİŞİKLİĞİ (aynı gün, sonuç görülmeden):** kullanıcı indikatörü bildirdi —
**"price hadley ve stokastik rsi"** → **Price Headley Acceleration Bands** (TradingView
yerleşik) + StochRSI. Belirsizlik kalktı, asıl ölçüm bu bantla yapılacak.

```
üst = SMA(yüksek × (1 + 4×(yüksek−düşük)/(yüksek+düşük)), 20)
alt = SMA(düşük  × (1 − 4×(yüksek−düşük)/(yüksek+düşük)), 20)
```

**Bu değişiklik betik hiç koşturulmadan yapıldı** — girdi düzeltmesi, bulguya göre ayar
değil. Bollinger ve Donchian tablodan çıkarılmadı, **duyarlılık kontrolü** olarak kaldı:
sonucun bant ailesine ne kadar bağımlı olduğu görünsün.

**⚠️ Ve önemli bir belirti:** Headley bu bantları **kırılım** için tasarladı — fiyatın bandın
**dışında** art arda kapanmasını "hızlanma" sinyali sayar. Videodaki kullanım (alt bantta AL)
indikatörün **tasarım amacının tersi**. Bu yüzden yazarın kendi kullanımı (bant dışı ardışık
kapanış = kırılım) ayrı bir satır olarak da ölçülüyor. Beklenti değişmedi: **NEGATİF.**

### SONUÇ — 6 varyantın **hepsi KALDI**

`scratchpad/kanal_stoch.py` · 570 sembol · ~60 gün 1h · giriş sonraki bar açılışı ·
maliyet %0,13 · ufuk 12 bar · hedef girişte dondurulmuş

| küme | N | net % | isabet | stop% | hedef% | A yarısı | B yarısı |
|---|---|---|---|---|---|---|---|
| **ACC LONG (asıl)** | 5488 | **−0.09** | %6,2 | 1,65 | 5,62 | +0.09 | −0.32 |
| **ACC SHORT (asıl)** | 5789 | **−0.12** | %4,9 | 2,03 | 6,01 | −0.09 | −0.15 |
| ayrıştırma: yalnız BANT | 9583 | −0.03 | %5,7 | 1,02 | 5,34 | +0.09 | −0.15 |
| ayrıştırma: yalnız STOCH | 17965 | −0.19 | %17,8 | 2,56 | 3,78 | −0.19 | −0.19 |
| BOLL LONG (duyarlılık) | 9562 | −0.15 | %19,9 | | | −0.05 | −0.24 |
| DONCH LONG (duyarlılık) | 5205 | −0.26 | %10,9 | | | −0.30 | −0.22 |
| KONTROL rastgele (long) | 5387 | −0.19 | %26,7 | 2,94 | 3,14 | −0.30 | −0.09 |
| KONTROL rastgele (short) | 5380 | −0.06 | %29,5 | 3,32 | 2,74 | +0.06 | −0.18 |

**Ön-kayıtlı ölçüt (net>0 **ve** kontrolü yenmek **ve** iki yarıda da pozitif):
altı varyantın altısı da KALDI.** Bant ailesini değiştirmek kurtarmıyor —
Acceleration / Bollinger / Donchian, hepsi negatif.

**Beklentim tutmuştu** (ön-kayıtta "NEGATİF" yazmıştım). Bu bir başarı değil,
sadece ölçümün sürprizsiz olduğunun kaydı.

### NEDEN kaldı — açık 18,3 puan
```
medyan stop  %1,65   ·   medyan hedef  %5,62   ·   R/R 3,4:1
GEREKEN başabaş isabet : %24,4
GERÇEKLEŞEN isabet     : %6,2
AÇIK                   : −18,3 puan
çıkış dağılımı: STOP %51 · SÜRE %43 · HEDEF %6
```
**R/R 3,4:1 kulağa iyi geliyor ve tamamen yanıltıcı.** İşlemlerin yarısı stopa,
%43'ü zaman aşımına gidiyor; hedefe yalnız %6'sı ulaşıyor.

### ⭐ Hedefi yakınlaştırmak KURTARMIYOR — kritik bulgu
Hedef, bant genişliğinin bir payı olarak süpürüldü (keşifsel, ön-kayıtlı değil):

| hedef | hedef % | isabet | başabaş gereken | **açık** | net % | A | B |
|---|---|---|---|---|---|---|---|
| bant × 0,25 | 1,40 | %48,0 | %58,2 | **−10,2** | −0.07 | +0.13 | −0.27 |
| bant × 0,50 | 2,81 | %23,1 | %39,9 | **−16,8** | −0.11 | +0.18 | −0.39 |
| bant × 0,75 | 4,21 | %11,5 | %30,3 | **−18,8** | −0.08 | +0.21 | −0.36 |
| bant × 1,00 | 5,62 | %6,2 | %24,4 | **−18,2** | −0.09 | +0.20 | −0.39 |

**Dört hedefte de açık kapanmıyor ve net negatif kalıyor.** Yani bu bir hedef-ayarı
sorunu değil; **stop, her hedeften önce yeniyor.** Kurulumun kendisinde yön bilgisi yok.

### Tek hayatta kalan hücre GÜRÜLTÜ çıktı
Ana tabloda iki yarısı da pozitif olan tek hücre `ACC LONG + fiyat > MA200` idi:

| alt küme | N | net % | standart hata | t | karar |
|---|---|---|---|---|---|
| fiyat > MA200 | 786 | +0.052 | 0.166 | **+0.31** | **GÜRÜLTÜ** (\|t\|<2) |
| fiyat < MA200 | 4702 | −0.119 | 0.046 | −2.58 | anlamlı NEGATİF |
| tümü | 5488 | −0.095 | 0.046 | −2.05 | anlamlı NEGATİF |

Trend filtresi hücresi sıfırdan **ayırt edilemiyor.** Çok sayıda hücreye bakıldığında
içinden bir tanesinin pozitif görünmesi zaten şansla beklenir — bu, aranan kanıt değil.

**Ama yönü doğruladı:** MA200 **altında** anlamlı negatif (t=−2,58). Belgenin
"düşüş trendinde çalışmaz" öngörüsü veriyle örtüştü.

### ⚠️ Geçersiz ölçüm — dürüstlük kaydı
"Yazarın kendi kullanımı: KIRILIM long" satırı tabloda **%98,2 isabet** gösteriyor.
**Bu sayı anlamsızdır ve kullanılamaz.** Sebep: fiyat üst bandın üstünde kapandığında
hedef (üst bant) girişin *arkasında* kalıyor, medyan hedef mesafesi %0,03 → işlem
anında "hedefe ulaştı" sayılıyor. Kırılım varyantı bu çıkış kuralıyla **ölçülemez**;
kendi çıkış kuralıyla ayrıca ölçülmesi gerekir. Tabloda bırakıldı ki hata görünsün.

### Sınırlar
- 15 dakikalık değil **1 saatlik** → orijinal tarifin birebir testi değil
- Tek rejim (~60 gün, ayı/nötr) · kripto perp · **BIST'e taşınmaz**
- Bant parametreleri (20, StochRSI 14/14/3/3, eşik 20/80) TradingView varsayılanı;
  taranmadı — taransaydı **tarama artığı** riski doğardı

### Sisteme etki: YOK
Kullanıcı kısıtı gereği `testbot.py`, `radar.py`, `kripto-config.json` ve gölge defter
**hiç ellenmedi.** Ölçüm tamamen `scratchpad/` içinde, salt-okunur önbellek üzerinde.
Devam eden iki pencere (SHORT 138 işlem · LONG gölge 25 olay) etkilenmedi.

---

## 2026-08-11 — SCALP VARYANTI + REJİM İDDİASI: ölçüldü

**Kullanıcı sorusu:** "long için kısa dönem scalp olarak ayarlasak? Genelde nötr ve boğada
çalıştığı söyleniyor."

### ⚠️ ÖNCE: bu pencerede GERÇEK BOĞA YOK
```
BTC 2026-06-12 → 2026-08-10 :  63.618 → 64.289   =  +%1,1
tepeden dip                  :  −%13,4
BTC MA500 (saatlik ~21g) üstünde geçen süre: %75
```
**Pencere NÖTR/YATAY.** "Boğada çalışır" iddiası **bu veriyle test EDİLEMEZ** — test
edilmedi, edilmiş gibi de yazılmadı.
**Ama "nötr'de çalışır" iddiası test EDİLEBİLİR ve edildi** — üstelik ortalamaya dönüşün
kendi ev sahası tam da bu rejim.

**Ayrıca bu bir düzeltme:** defterde "46 günün tamamı ayı/nötr" yazıyordu. Daha doğrusu
**nötr/yatay**, ikinci yarısı hafif yukarı. Yani LONG'un başarısızlığı "ayıda long tutuldu"
ile açıklanamaz — **çalışması gerektiği söylenen rejimde** başarısız oldu.

### Hedef × ufuk ızgarası — 20 hücrenin 20'si de negatif
`scratchpad/kanal_scalp.py` · 3.786 sinyal · A-stop · net %, maliyet %0,13 dahil

| hedef | 2 bar | 4 bar | 6 bar | 12 bar |
|---|---|---|---|---|
| %0,50 | −0,14 | −0,15 | −0,17 | −0,17 |
| %0,75 | −0,13 | −0,14 | −0,18 | −0,19 |
| %1,00 | −0,11 | **−0,14** | −0,19 | −0,20 |
| %1,50 | −0,09 | −0,13 | −0,21 | −0,24 |
| %2,00 | −0,09 | −0,14 | −0,24 | −0,27 |

**Tek pozitif hücre yok.** Scalp'e çekmek (kısa ufuk, yakın hedef) sonucu düzeltmiyor.

### ⭐ REJİM İDDİASI TERSİNE ÇIKTI
Birincil scalp (hedef %1,0 · ufuk 4 bar), **rejim-eşleşmiş kontrolle**:

| rejim | N | net % | t | KONTROL | fark | A yarısı | B yarısı |
|---|---|---|---|---|---|---|---|
| TÜMÜ | 3786 | −0,14 | −6,46 | −0,09 | **−0,05** | −0,10 | −0,17 |
| **BTC > MA500 (yükselen)** | 2843 | **−0,18** | **−7,17** | −0,11 | −0,07 | −0,15 | −0,23 |
| BTC < MA500 (düşen) | 943 | −0,01 | −0,17 | −0,03 | +0,02 | +0,62 | −0,09 |
| **BTC 24s YATAY (nötr)** | 2030 | **−0,13** | **−4,20** | −0,08 | −0,05 | −0,18 | −0,08 |
| **BTC 24s YUKARI** | 524 | **−0,24** | **−3,91** | −0,12 | −0,12 | −0,05 | −0,50 |
| BTC 24s AŞAĞI | 1232 | −0,10 | −3,34 | −0,06 | −0,04 | −0,01 | −0,20 |

**Piyasa yükselirken EN KÖTÜ** (BTC 24s yukarı: −0,24, t=−3,91). En az kötü olduğu yer
piyasanın **düştüğü** dönem (−0,01) — ve orada bile sıfırdan ayırt edilemiyor (t=−0,17,
yarılar +0,62 / −0,09 ile dağılıyor).

**Nötr rejimde net −0,13, t=−4,20, kontrolden 0,05 puan geride → iddia ÖLÇÜLDÜ ve TUTMADI.**

### ⭐⭐ REJİM-EŞLEŞMİŞ KONTROLÜN ÖNEMİ
Yükselen piyasada **herhangi bir long** para kazanır. "Boğa hücresinde pozitif" demek
strateji çalışıyor demek değildir. Doğru kıyas aynı rejimdeki rastgele long'lardır —
ve **strateji altı bölmenin beşinde rastgeleye yeniliyor.**

### ⭐⭐⭐ ASIL TEŞHİS: sinyalde bilgi yok, kaybı maliyet yapıyor
`brüt = net + maliyet(%0,13)`:

| küme | net % | **brüt %** |
|---|---|---|
| strateji TÜMÜ | −0,14 | **−0,01** |
| strateji nötr | −0,13 | **0,00** |
| KONTROL rastgele | −0,09 | **+0,04** |

**Brüt olarak strateji tam bir yazı-tura.** Kaybın neredeyse tamamı komisyon+kayma.
Rastgele girişin brütü (+0,04) stratejininkinden (−0,01) **daha iyi**.

> **Bu, "yanlış yöne bakıyor" demek değil — "hiçbir yöne bakmıyor" demek.**
> Parametre ayarıyla düzelmez; düzelmesi için sinyalin gerçek bir kenar taşıması gerekir.

### Stop varyantları — sıkı scalp stopu daha da kötü
| stop | stop% | başabaş gereken | isabet | net % | t |
|---|---|---|---|---|---|
| A-stop (asıl) | 1,48 | %64,9 | %41,8 | −0,14 | −6,46 |
| 0,5 × ATR | 0,57 | %44,8 | %32,9 | −0,18 | −11,77 |
| sabit %0,5 | 0,50 | %42,0 | %25,5 | −0,15 | −14,59 |
| sabit %1,0 | 1,00 | %56,5 | %34,8 | −0,16 | −10,94 |

Stop daralınca başabaş düşüyor (%64,9 → %42,0) ama isabet **daha hızlı** düşüyor
(%41,8 → %25,5). Açık her yerde 16-23 puan. **Aynı yapı, dördüncü kez.**

### Karar
**Altı rejim bölmesinin altısı da KALDI.** Scalp varyantı da, rejim iddiası da ölçüldü.
Sisteme hiçbir şey eklenmedi.

### Sınır
"Boğada çalışır" iddiası **hâlâ açık** — bu veride boğa yok. Rejim döndüğünde ölçülebilir;
o zamana kadar ne doğrulanmış ne çürütülmüş sayılır.

---

## 2026-08-11 — ⚠️ DÜZELTME: "sinyalde bilgi yok" DEDİM, YANLIŞTI

**Kullanıcının sorusu bu düzeltmeyi tetikledi:** *"sonuç olumsuz? ama bizim sisteme göre"* —
haklı çıktı. Önceki bütün ölçümlerde **bizim** A-stopumuz vardı. Sinyalin kendisi hiç
mekanikten arınık ölçülmemişti.

### Mekanikten arınık ölçüm (`scratchpad/kanal_ham.py`)
Stop yok · hedef yok · maliyet yok. Sadece: sinyalden sonra fiyat ne yaptı?

| ufuk | sinyal ham | KONTROL | fark | fark t | sinyal REL | fark REL t |
|---|---|---|---|---|---|---|
| 1 bar | +0,099 | +0,009 | +0,090 | **+3,19** | +0,044 | +1,76 |
| **4 bar** | **+0,243** | +0,035 | **+0,208** | **+3,84** | +0,124 | **+2,31** |
| 12 bar | +0,146 | +0,061 | +0,085 | +0,90 | +0,003 | −0,12 |
| 24 bar | −0,119 | −0,045 | −0,074 | −0,55 | −0,085 | +0,12 |

**Sinyal GERÇEK bilgi taşıyor** — ilk ~4 barda, hem ham hem BTC'ye göre, anlamlı.
12 barda tamamen sönüyor. MFE/MAE de destekliyor: 4 barda sinyal 1,25 oranı, kontrol 1,03.

**Yani "sinyal hiçbir yöne bakmıyor" ifadem YANLIŞTI.** Doğrusu: sinyal bakıyor, ama
çok kısa mesafeye — ve bizim stopumuz o mesafeyi görmeden kesiyor.

### Stopsuz 4-bar çıkış (`scratchpad/kanal_stopsuz.py`)
| stop | net % | t | stopa giden | KONTROL | fark | fark t | A yarısı | B yarısı |
|---|---|---|---|---|---|---|---|---|
| **stop YOK** | **+0,112** | +3,13 | %0 | −0,066 | +0,179 | +3,32 | +0,247 | −0,023 |
| 3 × ATR | +0,110 | +3,12 | %3,8 | −0,069 | +0,179 | +3,36 | +0,249 | −0,029 |
| 2 × ATR | +0,086 | +2,54 | %10,5 | −0,095 | +0,181 | +3,52 | +0,249 | −0,077 |
| **A-stop (bizim)** | +0,051 | +1,57 | **%26,5** | −0,111 | +0,162 | +3,28 | +0,237 | −0,135 |

**Bizim A-stopumuz işlemlerin %26,5'ini kesiyor ve kenarı +0,112 → +0,051'e düşürüyor
(anlamlılık kayboluyor).** Kullanıcının sezgisi doğruydu: sonucun bir kısmı bizim sistemimizdi.

Ufuk: 2 bar +0,103 · 4 bar +0,112 · **6 bar −0,036 · 8 bar −0,067** → kenar 4 barda bitiyor.

### ⭐⭐⭐ AMA — kenarın TAMAMI tek bir 10 günlük pencereden geliyor
| çeyrek | tarih | net % | t | N |
|---|---|---|---|---|
| **Q1** | 06-20 → 06-30 | **+0,579** | **+7,91** | 1372 |
| Q2 | 06-30 → 07-13 | −0,082 | −1,13 | 1380 |
| Q3 | 07-13 → 07-26 | −0,119 | −1,71 | 1379 |
| Q4 | 07-26 → 08-09 | +0,074 | +1,07 | 1379 |

İki yarı **anlamlı farklı**: A +0,247 / B −0,023, fark +0,270, **t = +3,76**.
Yani rastgele dalgalanma değil — kenar gerçekten **sönmüş**.

**Ve Q1 ne dönemi?** BTC'nin **2026-06-19 → 06-25 arasında %6 düştüğü** hafta —
pencerenin tek keskin satışı.

> **MEKANİZMA:** ortalamaya dönüş **keskin bir çöküş-toparlanma sırasında** çalışıyor.
> Normal piyasada hiçbir şey. Kenar "vardı ve söndü" değil, **"yalnız V dibinde vardı."**

### Sonuç — üç katmanlı, hepsi doğru
1. **Sinyal gerçek bilgi taşıyor** (4 bar, kontrolden +0,18 puan, t=+3,3)
2. **Bizim A-stopumuz o bilgiyi büyük ölçüde yok ediyor** (%26,5 stop, anlamlılık kaybı)
3. **Ama kenar tek bir çöküş episoduna ait** — Q2/Q3/Q4'te yok. Ön-kayıtlı ölçütün
   "her iki yarıda pozitif" şartı bu yüzden düşüyor.

**Karar değişmedi (KALDI) ama GEREKÇE değişti.** Eski gerekçe "sinyal boş" idi — yanlıştı.
Doğru gerekçe: **sinyalin kenarı gerçek ama rejime bağlı ve dayanıksız; normal piyasada yok.**

### Bunun bize öğrettiği (stratejiden bağımsız)
**Her sinyal, kapı ölçümünden ÖNCE mekanikten arınık ölçülmeli.** Aksi hâlde bizim
stopumuzun öldürdüğü bir kenarı "sinyal boş" diye kaydederiz. Bu oturumda tam bunu yaptım.
Bu ders A+B ve MA50+ucuz kapıları için de geriye dönük uygulanabilir — onlar ham ölçümle
(yön avı) bulunmuştu, yani şanslıyız; ama gelecekteki adaylar için sıra bu olmalı:
**ham ileri getiri → mekanik → portföy.**

---

## 2026-08-11 — FİKİR 1: "kaç ölü sinyalimiz aslında canlıydı?" (arşiv taraması)

**Gerekçe:** bugün A-stopun gerçek bir kenarı öldürebildiğini gördük. Bu projede "negatif"
diye kapatılmış **her şey** stoplu ölçülmüştü → bir kısmı **yanlış negatif** olabilir.
Araç: `scratchpad/olu_sinyal_tarama.py` · 6.790 arşiv olayı · HAM = stop/hedef/maliyet YOK.

### ⭐ BULUNDU — iki LONG hücresi yanlış negatifmiş

**HAM ölçüm (stopsuz, sabit süreli çıkış, maliyet düşülmüş):**

| hücre | en iyi ufuk | ham net | t | A yarısı | B yarısı |
|---|---|---|---|---|---|
| **LONG: fiyat YÜKSEK + chg24 düşük** | 24s | **+1,30** | **+4,01** | +1,19 | +1,45 |
| **LONG: MA50 düşük + fiyat YÜKSEK** | 12s | **+1,02** | **+2,90** | +1,28 | +0,60 |
| KONTROL: tüm olaylar LONG | 1s | −0,11 | −3,42 | −0,10 | −0,12 |

**Her iki yarıda da pozitif, t anlamlı, kontrol açıkça negatif.**

**Aynı hücreler MEKANİKLE (A-stop) — `yon_dogrula.py`, 2026-08-10:**

| hücre | hedef %2,5/24s | hedef %10/72s | **stop%** | A yarısı | B yarısı |
|---|---|---|---|---|---|
| fiyat YÜKSEK + chg24 düşük | **−0,17** | +0,22 | **0,97** | **−0,47** | +1,16 |
| MA50 düşük + fiyat YÜKSEK | **−0,08** | +0,27 | **0,98** | **−0,09** | +0,86 |

**Ham temiz ve tutarlı; mekanik kırık.** A yarısı negatife dönüyor.

### Sebep tek bakışta görünüyor: stop %0,98
Bu hücrelerin A-stopu **%0,98** çıkıyor — bugün ölçtüğümüz "net sıfır üreten" dar dilimin
tam içinde (`stop < %1,92` → isabet %10,3 / başabaş %16). Ve **canlıdaki
`asgari_stop_pct = 2.0` kapımız bu işlemleri zaten tümden reddederdi.**

> Yani sinyali reddettik çünkü **stop kuralımız o sinyale uygun değildi** — sinyalde
> bilgi olmadığı için değil. Fikir 1'in aradığı şey tam olarak buydu.

### Ne anlama geliyor — canlı kapının AYNASI
`fiyat YÜKSEK + chg24 düşük` = **pahalı + sakin coin → LONG**, 24 saat tut.
Canlıdaki SHORT kapımız ise `ucuz + MA50 üstü → SHORT`. İkisi aynı eksenin iki ucu.
Bu, projenin en büyük açığına (LONG kapısı yok, boğada bot kör) doğrudan aday.

### ⭐⭐ İKİNCİ BULGU — A-stop CANLI kapımızın da 2/3'ünü yiyor

| küme | HAM (stopsuz, en iyi ufuk) | MEKANİK (A-stop) | kaybedilen |
|---|---|---|---|
| **A+B (canlı kapı)** | +6,10 (72s, t=+6,82) | +2,14 | **%65** |
| SHORT: skor yüksek | +2,58 (48s) | +0,65 | %75 |
| SHORT: oi24 yüksek | +2,01 (48s) | +0,69 | %66 |
| SHORT: chg24 yüksek (pump) | +1,67 (48s) | +0,50 | %70 |
| MA50+ucuz (canlı kapı) | +0,78 (12s) | +0,84 | %0 (korunmuş) |

**A+B'nin ham kenarının %65'ini kendi stopumuz yiyor.** Not: stopsuz karşılaştırma
kuyruk riskini yok sayar, yani "stopu kaldıralım" demek değil — ama stop mesafesinin
**bu kapı için yeniden ölçülmesi gerektiğini** söylüyor.
**Pencere kuralı gereği ŞİMDİ UYGULANMAZ** (138 işlem / 30 gün dolana kadar parametre
donuk). Pencere sonrası ilk iş bu.

### Genel tarama sonucu
Bayrak koşulunu (`ham>0 & |t|>=2 & iki yarı + & mekanik<=0`) yalnız **kontrol grubu**
karşıladı: tüm olayları stopsuz SHORT'lamak +0,90 (t=+5,12), A-stopla **−0,05**.
Bu bir kenar değil **piyasa betası** (ayı/nötr pencerede her şey düştü) — ama A-stopun
+0,90'ı −0,05'e çevirmesi, hasarın büyüklüğünü tek satırda gösteriyor.

### Sınırlar
- N küçük (113 / 120), hücreler **tarama ile** bulundu → çoklu karşılaştırma riski
- Aynı 60 günlük tek rejim
- **Asıl sınav Fikir 3'ün 2 yıllık verisi olacak** — bu bulgular oraya devredildi

### Kendi hatam
Betiğin ilk sürümünde yarı örneklem 60'ın altına düşünce tablo `0.00` yazıyordu; bu
"yarılar çöktü" diye **yanlış okunuyordu**. Eşik 30'a indirildi ve yetersizse `az` yazılıyor.
Bu düzeltilmeden önce iki LONG hücresi de yanlışlıkla elenmiş görünüyordu.

---

## 2026-08-11 — FİKİR 3 TAMAM + FİKİR 1'İN ADAYLARI **ÖRNEKLEM DIŞINDA ÇÖKTÜ**

### Veri (Fikir 3)
`scratchpad/klines_1h_uzun/` — **566 sembol · 6,88 milyon bar · 2024-08-11 → 2026-08-11**
217 sembol tam 2 yıl · 395 sembol ≥1 yıl · medyan 13.692 bar. Eski `klines_1h/`
dokunulmadı (tüm önceki ölçümler yeniden üretilebilir).

BTC rejim kapsamı: **BOĞA** 2024-09→2025-01 (+%72) · **AYI** 2025-11→2026-06 (−%49) ·
tepeden dip −%58 · **10 keskin çöküş episodu** (eski veride 1 taneydi).

**İndirici hatası:** 567/570'te `UnicodeEncodeError` ile çöktü — Windows cp1254 konsolu
Çince sembol adlarını basamıyordu. **İndirme bitmişti, çöken `print`'ti.** Eksik 3 sembol
eski önbellekte de **0 barlıktı** (boş kayıt). `sys.stdout.reconfigure(utf-8, replace)`
eklendi.

### Sınav: iki LONG hücresi, eşikler arşivden AYNEN alınarak (`scratchpad/long_2yil.py`)

**ÖRNEKLEM DIŞI (2024-08 → 2026-06, ~22 ay, hiç görülmemiş):**

| hücre | N | 12s | t | 24s | t |
|---|---|---|---|---|---|
| A) fiyat ≥ $58,9 + chg24 düşük | 2762 | +0,04 | +0,44 | +0,16 | **+1,17** |
| A) fiyat AYLIK%80 + chg24 düşük | 19021 | −0,13 | −3,06 | −0,12 | **−2,12** |
| B) MA50 düşük + fiyat ≥ $58,9 | 2583 | +0,02 | +0,23 | +0,10 | **+0,75** |
| B) MA50 düşük + fiyat AYLIK%80 | 17674 | −0,25 | −5,75 | −0,25 | **−4,49** |
| KONTROL rastgele | 1117 | −0,37 | −2,60 | −0,49 | −2,51 |

Arşivde **+1,30 (t=+4,01)** olan hücre, 22 ayda **+0,16 (t=+1,17)** — sıfırdan ayırt
edilemiyor. Göreli (aylık dilim) sürümler ise **anlamlı NEGATİF**.

### ⭐ Boğada ne oluyor — artık cevaplanabiliyor

| hücre | rejim | net 24s | KONTROL | fark |
|---|---|---|---|---|
| A ($58,9) | **BOĞA** | +0,39 | **+0,75** | **−0,36** |
| A (aylık) | **BOĞA** | +0,58 | +0,75 | −0,17 |
| B ($58,9) | **BOĞA** | +0,85 | +0,75 | +0,10 |
| B (aylık) | **BOĞA** | +0,59 | +0,75 | −0,16 |
| A ($58,9) | NÖTR | +0,19 | −0,54 | +0,72 |
| A ($58,9) | AYI | −0,10 | −0,78 | +0,68 |

**Boğada hücreler rastgele long'a YENİLİYOR.** Pozitifler, ama boğada her şey pozitif —
bu kenar değil **beta**. NÖTR/AYI'da kontrolü ~+0,7 yeniyorlar ama mutlak olarak ≈ sıfır:
yani "daha az kaybettiren", "kazandıran" değil. *(Bu projede daha önce de aynı ayrım
çıkmıştı: "şu andaki bot kazandıran değil, az kaybettiren.")*

Çeyrekler tutarsız: A(aylık) 9 çeyrekte + + − − + − − + −.

### ⭐⭐ ASIL SEBEP BULUNDU — "fiyat YÜKSEK" aslında fiyat değil

Arşivin fiyat dağılımına bakınca eşik anlaşıldı:

```
arşiv olayları:  %50 dilim $0,56  ·  %75 $8,30  ·  %80 $58,88  ·  %90 $367
>= $58,88 olan 1358 olay  ->  yalnız 46 sembol
en sık: BTC(136) ETH(136) SOL(136) BNB(136) ZEC(136) TAO(135) AAVE(135) BCH(119)
```

> **"fiyat YÜKSEK + chg24 düşük → LONG" demek, aslında
> "BTC/ETH/SOL/BNB gibi BÜYÜK coinler düştüğünde al" demekti.**
> Fiyat seviyesi bir **büyük-coin vekiliydi**, fiyat etkisi değil.

Ve buradan ikinci, daha ciddi sorun çıkıyor: **N=113 diye görünen hücre, aslında ~8 coinin
tekrar tekrar gözlenmesiydi.** Bu gözlemler bağımsız değil; **t=+4,01 kümelenme yüzünden
şişmiş.** Örneklem dışı test bunu zaten çürüttü, ama çürütmeseydi bile o t'ye güvenilmezdi.

### Sonuç
**Fikir 1'in iki adayı da düştü.** Arşiv bulgusu örneklem-içi bir yapaydı; iki bağımsız
sebeple: (1) 22 ayda tekrar etmiyor, (2) sinyalin kendisi 8 coine kümelenmiş.

**Ama bu bir başarısızlık değil, sistemin çalışması.** 60 günlük veri "umut verici" diyordu;
2 yıllık veri "hayır" dedi — **ve bu, gerçek deftere hiç girmeden oldu.**

### Metodolojik sınır (bu ölçümün kendisine ait)
2 yıllık testte sinyaller **her uygun bardan** üretildi; arşivdeki olaylar ise radar
taramasının kısa listesinden geliyordu (hacim tabanı, skor sıralaması vb.). Yani bu
tam bir replikasyon değil — **kuralın kendisi** test edildi, arşivin olay seçimi değil.
Kural, yazıldığı hâliyle 22 ayda çalışmıyor.

### Kalıcı ders — kümelenme kontrolü artık zorunlu
Bir hücrenin N'i büyük görünse bile **kaç ayrı sembolden geldiği** sayılmalı.
`N=113 ama 8 sembol` ile `N=113 ve 90 sembol` aynı kanıt değildir.
Bu, A+B kapısı için de not edilmişti ("olaylar 15 sembolde kümeleniyor") — artık
**her ölçümde standart sütun** olmalı.

---

## 2026-08-11 — SİSTEM DENETİMİ: 9 doğrulanmış hata (rapor: `denetim-raporu.md`)

**Gerekçe:** bu oturumda arka arkaya üç ölçüm hatası tesadüfen yakalandı (birim hatası
`tbv/qv`, yarı-örneklem `0.00` gösterimi, kümelenmeyle şişen `t=+4.01`). Sistematik tarama
yapılmamıştı. Keşif üç paralel Explore ajanına dağıtıldı (bağlam şişmesin diye), her bulgu
sonra **elle doğrulandı ve sayısallaştırıldı**. Doğrulama betiği: `scratchpad/denetim_olcum.py`.

### Doğrulanan bulgular

| # | bulgu | yer | ciddiyet | zarar verdi mi |
|---|---|---|---|---|
| 1 | **Düşüş freni açık pozisyonları görmüyor** | `testbot.py:1396-1402` | 🔴 YÜKSEK | koruma çalışmıyor |
| 2 | Maliyet %0,09 (betikler) vs %0,13 (canlı) | 11 betik | 🟠 ORTA | tüm geçmiş sayılar iyimser |
| 3 | Kapanmamış mum göstergelere dahil | `radar.py:91,97-107` | 🟠 ORTA | evet, canlı seçim bozuk |
| 4 | TP1 sonrası likidasyonda marjin çift sayımı | `testbot.py:703` | 🟠 ORTA | hayır (0 likidasyon) |
| 5 | A+B kapısı MA50+ucuz'u gölgeliyor | `testbot.py:392-443` | 🟡 DÜŞÜK | karne yanlış |
| 6 | Gölge `zorla=True` canlı kuralları atlıyor | `golge.py:116` | 🟡 DÜŞÜK | henüz hayır |
| 7 | ATR: Wilder (canlı) vs basit ortalama (~20 betik) | `olcucu.py:89` | 🟡 DÜŞÜK | kısmen |
| 8 | Toplam maruziyet tavanı yok | — | 🟡 DÜŞÜK | 1 ile birlikte önemli |
| 9 | Kapanan turda funding atlanıyor | `testbot.py:896-899` | 🟢 ÖNEMSİZ | 6 $ |

### ⚠️ 1 NUMARA — bugünkü S9 kararını doğrudan etkiliyor
Fren yalnız `st["equity"]`'ye bakıyor. `acik_pnl_toplam` (`:1319`) **var** ama sadece log
(`:1423`) ve `--durum` (`:1459`) çıktısında; hiçbir karar dalında değil. Ayrıca fren
`yonet_acik_pozisyonlar`'dan **önce** çalışıyor (bir tur geç), ve `hedef_risk`/`marjin` de
aynı gerçekleşmiş equity'ye dayanıyor (açık zarar büyürken boyut küçülmüyor).

Canlı ölçüm:
```
frenin gördüğü equity  :  8.401 $  (düşüş %0,1)
toplam açık notional   : 21.889 $  = sermayenin 2,61 KATI
%10 aleyhe senaryo     : gerçek 6.212 $ (−%26) ama fren hâlâ 8.401 görür -> TETİKLENMEZ
```
**Bugün riski %3→%1,5 indirdim, gerekçe "fren tetiklenmesin, bot hayatta kalsın" idi.
O hesap frenin ÇALIŞTIĞINI varsayıyordu.** `fren_riski.py` simülasyonu de gerçekleşmiş
equity üzerinden modelledi — yani simülasyon canlıya *sadık*, ama **ikisi de gerçek ruin
riskini olduğundan az gösteriyor**: hesap, fren görmeden açık pozisyonlarla yok olabilir.

### Sayısallaştırmalar
- **Bulgu 2:** A+B +2,29 → **+2,25** · MA50+ucuz +0,82 → **+0,78** · birleşim +1,09 → **+1,05**
  (işaret değişmiyor, kenar %3,7 küçülüyor). `gainer_*` betiklerindeki `0.04R` varsayımı
  stop %0,5'te gerçek 0,26R → **6,5 kat** hata.
- **Bulgu 3:** `vol_x >= 2` eşiğini geçen olay oranı — dakika 5'te **%0,3**, dakika 59'da
  %14,6, kapanmış barda **%15,0**. Aynı coin saatin 5'inde elenip 55'inde geçiyor (**50 kat**).
- **Bulgu 5:** MA50 kapısının gerçek katkısı 445 olay, karnede 384 → **%14 eksik** sayılıyor
  (61 olay ikisini birden sağlıyor, hepsi A+B etiketli).
- **Bulgu 6:** gölge LONG'ların stopu hesaplanabilenlerin **hiçbiri** %2 altında değil
  (min %2,19) → çelişki ilkesel, pratikte henüz ısırmamış. blowoff SHORT'ta 3'te 1.
- **Bulgu 7:** Wilder/basit oranı medyan 1,015 ama **vakaların %39'unda fark >%10**.

### ⭐ Kümelenme — beklediğimden İYİ çıktı
Bugün LONG hücresinde (N=113 ama 8 sembol) yakalanan sorun **canlı kapılarda yok**:

| kapı | N | ayrı sembol | olay/sembol | en sık 5'in payı |
|---|---|---|---|---|
| A+B | 193 | **78** | 2,5 | %17 |
| MA50+ucuz | 445 | **119** | 3,7 | %21 |
| birleşim | 577 | **158** | 3,7 | %16 |

Canlı kapılar makul dağılmış. Yine de **"kaç ayrı sembol" sütunu artık standart** olmalı —
41 betikten yalnız 2'si sayıyordu.

### TEMİZ çıkanlar (kontrol edildi, sorun yok)
Zaman dilimi hizası (ampirik doğrulandı, kayma 0) · kline alan indeksleri · funding/OI
ölçekleri · stop aday listesinin test-canlı uyumu (3×ATR koşulu dahil) · look-ahead yok ·
R hesabı gerçekleşen riski kullanıyor.
*(Kırılganlık notu: arşiv damgaları tz taşımıyor — makine saat dilimi değişirse sessizce bozulur.)*

### KARAR BEKLİYOR
Açık pencere (138 işlem / 30 gün) ön-kaydı *"hiçbir parametreye dokunulmaz"* diyor.
Bulgu 1, 3, 4, 5 kod düzeltmesi ama yine de davranışı değiştirir → pencereyi geçersiz kılar.
Seçenekler: **(a)** pencere dolsun sonra düzelt · **(b)** yalnız freni düzelt, pencere yeniden ·
**(c)** hepsi + pencere yeniden.
Bot kağıt üstünde olduğu için (a) savunulabilir. **Gerçek paraya geçilmeden 1 numara
mutlaka düzeltilmeli.**

### Denetimin sınırı
Statik okuma + hedefli doğrulama; her satır çalıştırılmadı. Denetlenmeyen alanlar:
`panel_sunucu.py`, nöbetçi/alarm katmanı, Telegram, harici sağlayıcılar (CoinGecko/Apify/Coinalyze).

---

## 2026-08-11 — DENETİM DÜZELTMELERİ UYGULANDI (kullanıcı: "hepsini düzelt, bot düzelmiş olarak devam etsin")

Denetimde bulunan **9 hata + uygulama sırasında çıkan 1 hata daha** düzeltildi.
Birim testleri **15/15** geçti, canlı tur doğrulandı, ölçüm penceresi yeniden başlatıldı.

### Canlı bota uygulananlar

| # | ne | dosya | doğrulama |
|---|---|---|---|
| 1 | Fren **efektif equity**'ye bakıyor (gerçekleşmiş + açık P&L) + pozisyon yönetiminden **sonra** çalışıyor + boyutlandırma da efektife göre | `testbot.py` `efektif_equity()` | canlı: equity 8270 · efektif 9017 · fark **+747 $** |
| 2 | TP1 sonrası `marjin` **yarılanıyor** | `pozisyon_kismi_tp1` | test: likidasyon 500 $ siliyor (eskiden 1000 $ = 2 kat) |
| 3 | A+B / MA50+ucuz / **A+B+MA50** ayrı etiketleniyor | `karar_yon` birleşik blok | canlıda CAP ve BANANAS31 doğru "MA50+ucuz" yazıldı |
| 4 | Funding **kapanan turda da** alınıyor | `yonet_acik_pozisyonlar` | `funding_uygula` artık `continue`'dan önce |
| 5 | Radar ve ölçücü **kapanmış bar** kullanıyor (fiyat canlı kalır) | `radar.py`, `olcucu.py` `kapali=` | test: 51 istenip 50 dönüyor |
| 6 | Gölge: **canlı adayı** tezler canlı kurallara uyuyor | `golge.CANLI_ADAYI` | `pump_long_tezi` artık `zorla=False` |
| 7 | **`_save_state` ATOMİK** (tmp + `os.replace` + fsync) | `testbot.py:88` | ⬇ aşağıda |

### ⚠️ UYGULAMA SIRASINDA ÇIKAN 10. HATA — botun 3 saat durmasının sebebi
Kullanıcı sordu: *"neden 84 dakika tur atmamış"*. Araştırınca çok daha ciddi bir şey çıktı.

```
Görev : KriptoTestBot (Windows Zamanlayıcı, pythonw --cycle, 5 dk)
Sonuç : 267014 = SCHED_S_TASK_TERMINATED
Ayar  : ExecutionTimeLimit = PT4M   <-- Windows turu 4 DAKIKADA OLDURUYOR
```

Tetikleyici 5 dakikada bir, ama süre limiti **4 dakika**. Tur 4 dakikayı aşarsa Windows
süreci **öldürüyor** → `son_cycle` güncellenmiyor, kilit dosyası ortada kalıyor.

Bugünkü boşluklar: 11:17→12:06 (49dk) · **13:22→16:22 (180dk)** · 16:37→18:16 (99dk).

**180 dakikalık boşluk benim yüzümden:** 2 yıllık veri indirmesi **14:28→16:19** arası
saniyede ~3,5 istek atıyordu; botun API çağrıları yavaşladı, turlar 4 dakikayı aştı ve
öldürüldü. Turlar indirme bittikten **3 dakika sonra** (16:22) kendiliğinden döndü.
*(Diğer iki boşluğun sebebi kesinleşmedi — 11:17'deki benim işimden önce.)*

**Ve asıl tehlike:** `_save_state` dosyayı `open(..,"w")` ile TRUNCATE edip yazıyordu.
Öldürme tam o ana denk gelseydi `testbot_state.json` **yarım kalır, açık pozisyonlar ve
equity tamamen kaybolurdu.** Görev bugün 3 kez terminated döndüğü için senaryo teorik değildi.

**Düzeltildi:** `ExecutionTimeLimit` **PT4M → PT10M** (`MultipleInstances=IgnoreNew`
olduğu için uzun tur çakışma yaratmaz, sonraki tetik atlanır) **ve** `_save_state` atomik
yazmaya geçti. Doğrulama: zamanlayıcı turu **18:33:37**'de sorunsuz tamamlandı.

### Ölçüm tarafı — eski betikler BİLEREK değiştirilmedi
Defterdeki sayıların yeniden üretilebilir kalması için. Bundan sonrası için
**`scratchpad/olcum_ortak.py`**: Wilder ATR (canlıyla aynı) · `MALIYET=%0.13` ·
`maliyet_r(stop)` (sabit 0.04R yerine stop-bağımlı) · `ozet()` **ayrı sembol sayısı,
olay/sembol, ilk-5 payı ve `t_kume`** döndürüyor.

Kümelenme sütununun ne yakaladığı (aynı veri, farklı dağılım):
```
KUMELENMIS (8 sembol)   N=120  ort +0.246  t +2.86  ->  t_kume +0.74
YAYILMIS  (90 sembol)   N=120  ort +0.246  t +2.86  ->  t_kume +2.47
```
Bu sütun olmasaydı ikisi de "+2.86" diye raporlanırdı — bugün LONG hücresinde tam bu oldu.

### ÖLÇÜM PENCERESİ YENİDEN BAŞLADI
Önceki pencerenin ön-kaydı *"parametreye dokunulmaz"* diyordu; **botun davranışı değişti**,
o pencere **GEÇERSİZ**. Yeni ön-kayıt:

| | |
|---|---|
| **Başlangıç** | 2026-08-11 18:42 (denetim düzeltmeleri yürürlükte) |
| **Pencere** | 138 kapanmış işlem **veya** 30 gün — hangisi önce |
| **GEÇTİ** | toplam net > 0 **ve** ikinci yarı > 0 |
| **KALDI** | toplam net < 0 **ya da** fren tetiklendi |
| **BELİRSİZ** | toplam > 0 ama ikinci yarı < 0 → uzat |

`zirve_equity` **9016,60**'a çekildi (efektif equity). Equity ve 20 işlemlik geçmiş
**dokunulmadı**. Beklenti maliyet düzeltmesiyle **+%1,09 → +%1,05** / olay.

**Pencere boyunca kural yine aynı:** parametre değişmez, kapı eklenmez, eşik oynatılmaz.

---

## 2026-08-12 — TARAMA CADENCE'İ: 10 dk (kazara) → 7,5 dk (kararlı)

**Nasıl fark edildi:** kullanıcı "sistem tarama çalışıyor mu" diye sordu. Görevlerin
hepsi sağlıklıydı (`Sonuç: 0`, dünkü `267014` ölümleri gitmiş), ama tur aralıkları
**5 değil 10 dakika** çıktı.

**Sebep — 11 saniyelik fark:**
```
tur suresi   : 311 saniye (5 dk 11 sn)
tetikleyici  : 5 dakika
MultipleInstances = IgnoreNew  ->  tur hala kosarken gelen tetik ATLANIR
sonuc: efektif cadence 10 dakika, üstelik KARARSIZ (bazen 5, bazen 10)
```

### Denenen ama İŞE YARAMAYAN optimizasyon (dürüstlük kaydı)
`acik_pnl_toplam` her pozisyon için ayrı ticker çağırıyordu ve cycle içinde iki yerde
çalışıyordu → 6 pozisyonda 12 gereksiz istek. Tek `/fapi/v1/ticker/price` çağrısına
indirdim (731 sembol, 0,57 sn) + equity logu önbelleklenmiş değeri kullanıyor.
**Ölçülen API kazancı ~5,5 sn — ama tur süresi 308 → 311 sn, yani DEĞİŞMEDİ.**
Darboğaz fiyat çağrıları değil, **150 sembollük tarama turu.**
Optimizasyon yine de tutuldu: daha az istek = daha az hız-limiti riski (11 Ağustos'ta
toplu indirme turları öldürtmüştü).

### Uygulanan: tetik 5 dk → **7,5 dk**
Kullanıcı sordu: *"7,5 dakikaya ayarla, çakışmayı önler ama bizi kör eder mi?"*

**Kör etmiyor — ve bunun sebebi kodda:** `testbot.py:903`
```python
bars = klines_since(pos["sym"], "1m", to_ms(son_ts))
for b in bars:  ...stop / likidasyon / TP1 / TP2 her 1 dakikalık bar için
```
Çıkışlar, son kontrolden bu yana geçen **tüm 1 dakikalık barlar geri oynatılarak**
tespit ediliyor. Stop 3. dakikada tetiklendiyse tur 7,5 dk sonra koşsa bile **o barın
fiyatından** kapanıyor. Geciken şey fiyat değil, kaydın deftere düşme anı.
`limit=500` → 500 dakikalık boşluğa kadar tolerans.

| | önce | sonra |
|---|---|---|
| gerçek cadence | 10 dk (kararsız) | **7,5 dk (kararlı)** |
| çıkış fiyatları | doğru | doğru |
| yeni giriş tespiti | ≤10 dk gecikme | **≤7,5 dk** |
| tur payı | 5:11 / 10:00 | 5:11 / 7:30 (2:19 boşluk) |

**Yani körlüğü azalttı.** 10 dakika bir tercih değil, kazara oluşmuş bir durumdu.
Doğrulama: 00:48:43 → 00:56:23 = **7,7 dk**. Görev bilgisi: son 00:43:42, sonraki
00:51:11 = 7,48 dk. `ExecutionTimeLimit` PT10M kaldı (uzun tur öldürülmesin,
sadece sonraki tetik atlansın).

### Kalan sınır
Tur 5:11 sürüyor ve bunun tamamı **150 sembollük tarama**. Havuzu küçültmek cadence'i
5 dakikaya indirirdi ama **botun ne gördüğünü değiştirir** — ölçüm penceresi açıkken
yapılmadı. Pencere sonrası bakılacak.

**PENCERE SIFIRLANDI** (cadence botun gördüğü fırsat sayısını değiştirir):
zirve 8698,11 → **8381,06** (efektif equity). Equity ve işlem geçmişi dokunulmadı.

---

## 2026-08-12 — ÖN-KAYIT: hedefi oynaklığa ölçekleme (koşturmadan ÖNCE commit)

**Fikir (kullanıcı):** *"TP çok aşağıdadır, hacme göre gücü yetmez."* Sabit %10 yerine
hedef = `N × ATR`, ve **her turda coin'in güncel oynaklığıyla yeniden hesaplansın**;
oynaklık sönmüşse pozisyon kapansın.

**Neden makul — elimizdeki dolaylı delil:** stop mesafesi dilimlerine göre hedefe
ulaşma %10,3 → %20,1 → %33,3 → **%56,2**. Stop mesafesi büyük ölçüde ATR'den geliyor,
yani "oynak coinler %10'a ulaşıyor, sakin coinler ulaşamıyor". Bugüne kadarki bütün
hedef taramaları **sabit yüzdeydi**; oynaklığa ölçeklenmiş hedef hiç denenmedi.

### Ön-kayıtlı tasarım
- **Veri:** `scratchpad/klines_1h_uzun/` — 566 sembol, 2 yıl, **gerçek boğa + gerçek ayı**
- **Olaylar:** canlı iki kapının (A+B, MA50+ucuz) tetiklendiği barlar, pump kapısı dahil
- **Mekanik:** botun A-stopu · **Wilder ATR** (`olcum_ortak.atr`, canlıyla aynı) ·
  maliyet **%0,13** · giriş sonraki barın açılışı · aynı barda stop+hedef → STOP
- **Hedef DİNAMİK:** her barda ATR yeniden hesaplanır, `hedef = N × ATR`.
  Fiyat güncel hedefi geçmişse o barda kapanır. *(Önceden hesaplanamaz — bar-bar
  simülasyon şart, yoksa ölçüm gerçeği yansıtmaz.)*
- **Taranacak:** `N` = 2 · 3 · 4 · 5 · 6 · taban/tavan çiftleri
- **Kıyas:** bugünkü sabit %10, aynı olaylar/stop/maliyet

### GEÇME ÖLÇÜTÜ (sonuç görülmeden)
1. Sermaye getirisi (işlem başına) **sabit %10'u yenmeli**
2. **Her iki zaman yarısında da** pozitif
3. **BOĞA ve AYI rejimlerinin ikisinde de** çökmemeli *(ilk kez mümkün)*
4. Ayrı sembol sayısı ve `t_kume` raporlanacak

Dördü birden sağlanmazsa **KALDI** → uygulanmaz, gerekçesi buraya yazılır.

### BEKLENTİM (önceden, yanılırsam kayda geçsin)
**Kısmen pozitif bekliyorum** — ama sabit %10'u yenmesini beklemiyorum.
Gerekçem: dinamik hedef, kazanan işlemi coin sakinleştiğinde erken kesecek; bu
projede "erken çıkış kazananı budar" beş kez çıktı. Buna karşılık sakin coinlerdeki
ulaşılamaz hedefi düzeltmesi lehte. İki etki birbirini götürebilir.
**Sabit %10'u net yenerse bu, beklentimin tersi ve bilgi değeri yüksek bir sonuçtur.**

### Sınır (şimdiden)
ATR hem stopu hem hedefi belirlediği için `N × ATR` hedefi, stop mesafesiyle
**mekanik olarak korele**. Yani "geniş stoplu işlem daha çok kazanır" bulgusunu
kısmen yeniden üretiyor olabiliriz — sonuç pozitif çıkarsa bu ayrıştırılmalı.

### SONUÇ — oynaklığa ölçekli hedef: **8 varyantın 8'i de KALDI**

`scratchpad/oynak_hedef.py` · 21.830 olay · 312 ayrı sembol · 2 yıl · hacim tabanı $3M/24s

| kural | sermaye% | t | isabet | hedef~ | A yarısı | B yarısı |
|---|---|---|---|---|---|---|
| **SABİT %10 (bugünkü)** | **−0,079** | −4,05 | %12,9 | %10,0 | −0,073 | −0,085 |
| oynak 2×ATR | −0,088 | −6,62 | %27,2 | %4,0 | −0,104 | −0,072 |
| oynak 3×ATR | −0,094 | −5,98 | %21,0 | %6,0 | −0,105 | −0,084 |
| oynak 4×ATR | −0,096 | −5,43 | %17,3 | %8,0 | −0,095 | −0,097 |
| oynak 5×ATR | −0,088 | −4,55 | %14,7 | %9,9 | −0,097 | −0,079 |
| oynak 6×ATR | −0,091 | −4,43 | %12,3 | %11,9 | −0,103 | −0,079 |
| + taban%3 tavan%20 | −0,086…−0,095 | | | | | |

**Hiçbiri sabit %10'u yenemedi.** Ve yine aynı yapı: hedef yaklaştıkça isabet
%12,9 → **%27,2** çıkıyor ama net getiri düşüyor. **Beşinci kez: başabaş isabetten
hızlı büyüyor.**

**Beklentim tutmuştu** — ön-kayıtta *"sabit %10'u yenmesini beklemiyorum"* yazmıştım.

**"Oynaklık söndü → kapat" mekanizması pratikte hiç çalışmadı:** işlemlerin
yalnız **%0,1–0,4'ü** bu yolla kapandı. ATR 72 saatte hedefi geçersiz kılacak kadar
hızlı düşmüyor. Fikrin en çekici kısmı ölçümde **boş çıktı**.

### Rejim ayrımı (ilk kez mümkün)
| kural | BOĞA | NÖTR | AYI |
|---|---|---|---|
| sabit %10 | −0,157 | −0,087 | −0,123 |
| oynak 3×ATR | −0,163 | −0,088 | −0,060 |
| oynak 4×ATR | −0,195 | −0,081 | −0,092 |

Üç rejimde de negatif. Boğada en kötü — SHORT kapısı için beklenen yön.

### ⚠️ ÖLÇÜMÜN KENDİ HATALARI (ikisi de düzeltildi, kayda geçsin)
1. **Fikrin aleyhine çarpıtma:** hedef daralıp fiyat onu zaten geçmişse ilk sürüm
   *hedef fiyatından* dolduruyordu; canlıda bot **piyasadan** kapatır. SHORT'ta hedef
   daha yüksek = daha kötü fiyat → kazanç eksik yazılıyordu. Düzeltildi.
2. **Yanlış evren:** hacim filtresi yoktu, medyan stop **%1,1** çıkıyordu (canlıda %3,4)
   → başka bir popülasyon ölçülüyordu. Canlının `min_vol_musd=3` eşiği eklendi;
   olay 27.576 → 21.830, stop %1,3'e çıktı.

### 🔴 ASIL BULGU — hedeften daha önemli
**Referans çizgisi (bugünkü sabit %10) 2 yıllık veride NEGATİF: −0,079 (t=−4,05).**
Arşiv ölçümü aynı kapı için **+0,41** demişti. Bu, LONG hücrelerinde yaşadığımızın
aynısı: örneklem-içi pozitif, örneklem-dışı negatif.

**AMA doğrudan "kapı öldü" DENEMEZ.** Popülasyon hâlâ farklı: medyan stop %1,3
(canlıda %3,4), 21.830 olay (arşivde 445). Arşiv olayları radar'ın **skorla sıralanmış
ilk 150** kısa listesinden geliyor; benim yeniden üretimim yalnız hacim tabanı
uyguluyor. Yani **kapının canlı performansı radar'ın seçimine bağlı olabilir** ve o
seçimi 2 yıllık veriyle yeniden üretemiyorum (skor için funding/OI gerekiyor, uzun
veride yok).

**Açık soru, kayda geçti:** MA50+ucuz kapısının artısı kuralın kendisinden mi geliyor,
yoksa radar'ın ön elemesinden mi? Bunu ayırmak için 2 yıllık funding/OI verisi gerekir.

**KARAR: oynaklığa ölçekli hedef UYGULANMADI.** Canlı bota dokunulmadı; sabit %10 kalıyor.

---

## 2026-08-12 — ÖN-KAYIT: A+B'nin funding bacağı 2 yılda sınanıyor (koşturmadan ÖNCE)

**Neden bu:** bugün MA50+ucuz kapısı 2 yıllık veride çöktü (−0,079, t=−4,05). Ama iki
kapı eşit durumda değil:

| kapı | ham ileri getiri (arşiv, 72s) | 2 yılda sınandı mı |
|---|---|---|
| **A+B** | **+6,10 (t=+6,82)** — projenin en güçlü delili | ❌ henüz değil |
| MA50+ucuz | +0,78 (t=+1,66) | ✅ **çöktü** |

**Neden A+B'nin şansı olabilir — MA50'den farklı bir sebeple:** MA50+ucuz'un iki bacağı
da fiyattan türüyordu ve "fiyat seviyesi" sonradan bir **coin-tipi vekili** çıktı.
Funding ise fiyattan türemiyor — pozisyon taşıma maliyeti, yani piyasanın **kendi
konumlanması**. Yapısal olarak bağımsız bir sinyal. Bu, otomatik olarak işe yarar
demek değil ama bulduğumuz tuzağa aynı yoldan düşmez.

### Kısıt — dürüstçe
Binance **funding geçmişi 2 yıl açık**, ama **açık pozisyon (OI) geçmişi yalnız ~30 gün.**
Yani A+B'nin `oi24 >= %10` bacağı 2 yılda **kurulamaz**. Sınanacak olan **funding bacağı
tek başına**. Arşivde tekli ölçüm: funding +0,259R (N=508). Kesişim +0,375R idi, yani
funding tek başına daha zayıf — bu testin **kapının tamamını değil, taşıyıcı bacağını**
sınadığı kayda geçsin.

### Tasarım (sonuç görülmeden)
- Veri: `scratchpad/funding_gecmis/` (yeni indirilecek) + `klines_1h_uzun/`
- Sinyal: en güncel funding **≤ −0,05 %/8s** · pump kapısı (chg24 < %20) · hacim ≥ $3M/24s
- Mekanik: botun A-stopu · Wilder ATR · sabit %10 hedef · 72s ufuk · maliyet %0,13 ·
  giriş sonraki barın açılışı · seyreltme 24 bar
- Kontrol: aynı sembol/dönemde **rejim-eşleşmiş rastgele** barlar
- Bölme: BOĞA / NÖTR / AYI · iki zaman yarısı · ayrı sembol sayısı + `t_kume`

### GEÇME ÖLÇÜTÜ
1. Sermaye getirisi (işlem başına) **> 0**
2. **Rejim-eşleşmiş kontrolü** yenmeli
3. **Her iki zaman yarısında da** pozitif
4. **BOĞA ve AYI'nın ikisinde de** çökmemeli

Dördü birden yoksa **KALDI** → A+B de doğrulanmamış sayılır ve bu deftere yazılır.

### BEKLENTİM
**Kararsızım, hafif pozitife meyilliyim.** Lehte: funding fiyattan bağımsız, arşiv
ham getirisi çok güçlü (t=+6,82), ve kapı gerçekten seçici (BTC'de %0, OGN'de %3
tetikleniyor). Aleyhte: MA50+ucuz da arşivde iyiydi ve çöktü; ayrıca oi24 bacağı
olmadan kapı zayıflar. **Yanılırsam kayda geçsin.**

### İşletim notu
Dün 2 yıllık mum indirmesi (~215 istek/dk) botun turlarını **3 saat öldürmüştü.**
Bu indirme ~1.700 istek ve **~66 istek/dk** hızla yapılacak (üçte bir). Bot izlenecek.

### SONUÇ — A+B'nin funding bacağı: **KALDI, ama MA50'den kökten farklı biçimde**

`scratchpad/ab_funding_2yil.py` · **14.599 sinyal · 523 ayrı sembol** · 2 yıl · funding
geçmişi 567/567 sembol indirildi (52 dk, ~66 istek/dk — bot boyunca sağlıklı kaldı)

| küme | N | sermaye% | t | isabet | stop~ | A yarısı | B yarısı |
|---|---|---|---|---|---|---|---|
| **funding ≤ −0,05** | 14599 | **+0,111** | **+4,68** | %20,9 | 2,40 | +0,081 | +0,140 |
| KONTROL rastgele | 12095 | +0,003 | +0,10 | %13,4 | 1,52 | +0,022 | −0,034 |
| **FARK** | | **+0,108** | | | | | |

**Rejime göre — kontrolü ÜÇ REJİMDE DE yeniyor, hem de tutarlı biçimde:**

| rejim | N | sinyal | KONTROL | **fark** |
|---|---|---|---|---|
| BOĞA | 558 | −0,030 | −0,123 | **+0,093** |
| NÖTR | 11228 | +0,139 | +0,025 | **+0,114** |
| AYI | 2729 | +0,021 | −0,083 | **+0,104** |

Farkın üç rejimde de +0,09…+0,11 bandında olması dikkate değer — tek bir dönemin
artığı değil.

### ⚠️ KÜME-DAYANIKLI TEST — ham t şişmiş
`t = +4,68` sembol içi korelasyonu yok sayıyor. Her **sembolü tek gözlem** sayarak
tekrar ölçtüm (455 sembol ortalaması üzerinden):

| küme | sembol | ort % | t |
|---|---|---|---|
| funding ≤ −0,05 | 455 | +0,058 | **+1,58** |
| KONTROL | 533 | −0,018 | −0,51 |
| **FARK** | | **+0,076** | **+1,51** |

Sembol düzeyinde: BOĞA +0,012 (t=0,09) · NÖTR +0,080 (t=1,76) · AYI −0,037 (t=−0,54).

**Yani doğru yöne bakıyor ama |t| < 2 — kanıtlanamıyor.**

### ÖN-KAYITLI ÖLÇÜT: KALDI
1. net > 0 → **EVET** (+0,111)
2. kontrolü yener → **EVET** (+0,108)
3. iki zaman yarısı + → **EVET** (A +0,081 / B +0,140)
4. BOĞA ve AYI'da çökme yok → **HAYIR** (boğa −0,030)

**Dördüncü şart düştü.** Ölçütü şimdi gevşetmek kale direğini oynatmak olur — düşürdü.
*Kayda geçsin: "çökme yok" diye yazmıştım, kodda `> 0` diye uyguladım. Boğa hücresi
N=558, t=−0,26 — bu bir çöküş değil, sıfır etrafında gürültü, üstelik kontrolü +0,093
yeniyor. Ölçüt kaba tanımlanmıştı. Ama tanımı sonradan değiştirmiyorum.*

**Beklentim** ("kararsızım, hafif pozitife meyilliyim") **tuttu** — pozitif çıktı ama
kanıtlanamadı.

### ⭐ İKİ KAPI ARTIK EŞİT DEĞİL — asıl çıktı bu

| | MA50+ucuz | A+B (funding bacağı) |
|---|---|---|
| 2 yıl sonucu | **−0,079 (t=−4,05)** | **+0,111 (t=+4,68)** |
| küme-dayanıklı | negatif | +0,076 (t=+1,51) |
| rejimler | **üçü de negatif** | **üçünde de kontrolü yeniyor** |
| popülasyon uyumu | stop %1,3 (canlı %3,4) — **uzak** | stop %2,4 (canlı ~%3) — **yakın** |
| verdikt | **ÇÜRÜTÜLDÜ** | **kanıtlanamadı, çürütülmedi** |

**MA50+ucuz reddedildi. A+B askıda.** İkisi aynı torbaya konamaz.

### Sınırlar
- **oi24 bacağı yok** (OI geçmişi ~30 gün). Arşivde kesişim funding-tekliden **1,4 kat**
  güçlüydü (+0,375 vs +0,259R) → canlı kapı ölçtüğümden **iyi olabilir**
- Yeniden üretim canlı evrenin birebir aynısı değil (radar skor sıralaması yok)

### KARAR (kullanıcı, 2026-08-12): **her iki kapı da AÇIK KALIYOR**

Ölçüm MA50+ucuz'u kapatmayı öneriyordu (2 yıl, üç rejim, 21.830 olay, t=−4,05).
**Kullanıcı ikisini de açık bırakmayı seçti.** Bilinçli bir karar; kayda geçiyor ki
pencere dolduğunda "gözden kaçmış" sanılmasın.

**Kararı savunulabilir kılan şey:** MA50 testi bir *yeniden üretim* — canlı evrenin
birebir aynısı değil. Medyan stop %1,3 çıktı, canlıda %3,4. Arşiv olayları radar'ın
skorla sıralanmış ilk-150 kısa listesinden geliyor; ben yalnız hacim tabanı
uygulayabildim (skor için funding+OI gerekiyor, uzun veride OI yok). Yani ölçüm
"kural geniş uygulanınca negatif" diyor, "canlı kapı negatif" demiyor.

**Açık soru aynen duruyor:** MA50+ucuz'un canlıdaki artısı kuralın kendisinden mi
geliyor, yoksa radar'ın ön elemesinden mi? Bunu ayırmanın tek yolu 2 yıllık OI verisi
ve o yok. **Hakem canlı pencere olacak** (138 işlem).

**Pencere sıfırlanmadı** — hiçbir şey değişmedi, bot aynen devam ediyor.

---

## 2026-08-12 — SCALP PENCERESİ: "botun girdiği poza elle binebilir miyim?"

**Kullanıcının gerçek kullanım amacı ortaya çıktı:** botu otonom kazanan makine olarak
değil, **sinyal üreteci** olarak kullanmak — pozisyon artıdayken elle kısa vadeli işlem
almak. Bu, bugüne kadar ölçtüğümüz hiçbir şeyin cevaplamadığı bir soru: tüm ölçümler
botun **kendi** çıkışlarıyla (A-stop, %10 hedef, 72s) yapılmıştı.

`scratchpad/scalp_penceresi.py` · 2 yıl · A+B 14.634 (524 sembol) · MA50+ucuz 21.977
(312 sembol) · kontrol 12.048 (557 sembol)

### 1) Kapılar rastgeleden GERÇEKTEN daha çok lehte hareket üretiyor

İlk 1 saatte MFE (lehte en uç nokta):

| küme | MFE medyan | ≥ +%1 | ≥ +%2 |
|---|---|---|---|
| MA50+ucuz | **1,09%** | %54 | %25 |
| A+B | 0,88% | %45 | %20 |
| KONTROL | 0,64% | %33 | %12 |

**Kapılar çalışıyor** — girişten sonra fiyat rastgeleden belirgin daha çok lehe gidiyor.

### 2) ⚠️ Ama aleyhte de aynı kadar gidiyor — MFE/MAE ≈ 1,1

| ufuk | A+B MFE/MAE | MA50 MFE/MAE | kontrol |
|---|---|---|---|
| 1s | 1,06 | 1,07 | 1,05 |
| 4s | 1,13 | 1,06 | 1,11 |
| 24s | 1,17 | 1,10 | 1,11 |

Hareket **neredeyse simetrik**. Kapılar oynaklık üretiyor, **yön asimetrisi** değil —
en azından ilk saatlerde.

### 3) ASIL TABLO — her hedef/stop çifti NEGATİF

İlk 4 saat, maliyet %0,13 dahil, en iyi hücreler:

| küme | en iyi hedef/stop | hedef% | stop% | **beklenti** |
|---|---|---|---|---|
| A+B | 2,0 / 1,5 | %32 | %47 | **−0,168** |
| MA50+ucuz | 2,0 / 0,5 | %16 | %80 | **−0,199** |
| **KONTROL** | 1,5 / 1,5 | %37 | %37 | **−0,094** |

**36 hücrenin 36'sı da negatif.** Ve kontrol her ikisinden **daha az kötü** — çünkü
kapılar daha oynak, oynaklık hem hedefi hem stopu daha çok vurduruyor.

**Aritmetiği:** MFE/MAE ≈ 1,1 iken simetrik hedef/stop ≈ %52/%48 verir.
Beklenti = 0,52×(H−0,13) − 0,48×(H+0,13) = **0,04H − 0,13**.
Başabaş için **H > %3,25** gerekir — o da artık scalp değil.

### 4) ⭐ "HIZLI TEPE = KAYBEDEN" HİPOTEZİ ÇÜRÜTÜLDÜ
17 canlı pozisyonda "hızlı tepe yapanlar kaybediyor" gibi görünüyordu. 2 yılda tersi:

| | ilk 4 saatte ≥ +%1 görenler | görmeyenler |
|---|---|---|
| A+B | N=10.234 · 72s medyan **+3,43%** | N=4.365 · **+0,08%** |
| MA50+ucuz | N=16.326 · **+3,07%** | N=5.509 · **+0,04%** |

**Erken güç, sonraki gücü haber veriyor** — uyarı değil. 17 pozisyonluk gözlem
küçük örneklem artığıydı. *(İyi ki "bu bir gözlem, kural değil" diye yazmıştım.)*

### SONUÇ
**Scalp bu ölçümde çalışmıyor.** Ama iki şey kayda değer:
- Kapılar gerçekten bilgi taşıyor (MFE kontrolden belirgin yüksek)
- Erken hareket **pozitif** bir sinyal — scalp'lemek yerine **beklemek/eklemek** için

### ⚠️ ÖLÇÜMÜN SINIRI — cevabı değiştirebilir
1 saatlik bar kullanıldı; bar **içinde** hedefin mi stopun mu önce geldiği bilinemez →
**kötümser** varsayımla hep STOP sayıldı. Yani bu tablo **ALT SINIR**. Canlıda ekranı
izleyen biri sırayı görür ve daha iyisini yapabilir. Gerçek cevap için **15 dakikalık
veri** gerekir; 1 saatlik çözünürlükte kapanmayan soru bu.

### KESİN CEVAP — 1 dakikalık ölçüm (alt sınır değil, gerçek)

Kullanıcı haklıydı: *"6 ay eşit sınama olmaz, ayı sadece."* Toplu 15dk yerine **her
sinyalin etrafından tek istek** çekildi — 4.498 kayıt, **rejime tam eşit** (kapı × rejim
başına ~500), her birinde 260 dakikalık bar. İndirme 107 dk, bot boyunca sağlıklı.
`scratchpad/scalp_1m_indir.py` + `scalp_1m_olc.py`

**1 saatlik ölçüm gerçekten kötümsermiş** — ama yönü değiştirmedi:

| kapı | 1 saatlik (alt sınır) | **1 dakikalık (gerçek)** | fark |
|---|---|---|---|
| A+B | −0,168 | **−0,008** | +0,160 |
| MA50+ucuz | −0,199 | **−0,085** | +0,114 |
| **KONTROL** | −0,094 | **+0,032** | +0,126 |

**Rastgele giriş her iki kapıyı da yeniyor.** Ve o +0,032 bile 20 hücrelik ızgaranın
maksimumu — yani tarama artığı adayı.

### Rejim ayrımı ikisini de çürütüyor
| kapı | en iyi hücre | BOĞA | NÖTR | AYI |
|---|---|---|---|---|
| A+B | 2,0/2,0 | **+0,093** | −0,030 | −0,087 |
| MA50+ucuz | 2,0/0,5 | −0,039 | −0,116 | −0,100 |
| KONTROL | 1,5/2,0 | −0,051 | **+0,089** | **+0,060** |

**İkisi de rejime göre işaret değiştiriyor.** A+B yalnız boğada, kontrol yalnız boğa
dışında pozitif. Bu bir kenar değil, ızgara taramasının gürültüsü.

### ⭐ YAPISAL SEBEP — MFE/MAE her yerde ~1,0
| kapı | 15dk MFE | 15dk MAE | oran |
|---|---|---|---|
| MA50+ucuz | 0,60 | 0,57 | **1,05** |
| A+B | 0,45 | 0,45 | **1,00** |
| KONTROL | 0,37 | 0,34 | **1,09** |

240 dakikaya kadar oran hep **1,00–1,15**. Kapılar **daha çok hareket** üretiyor
(MA50 kontrolden %62 fazla) ama **yön asimetrisi ÜRETMİYOR.**

Aritmetiği: oran ~1,05 iken simetrik hedef/stop ≈ %51/%49 verir →
`beklenti = 0,02×H − 0,13` → başabaş için **H > %6,5**. O da scalp değil.

> **Bot, girişleriyle sana daha OYNAK bir coin veriyor — daha YÖNLÜ bir coin değil.**
> Scalper maliyeti (%0,13) simetrik harekette her zaman kazanır.

### Ama işe yarar bir kullanım kaldı
MA50+ucuz 15 dakikada medyan **%0,60** hareket üretiyor, kontrol %0,37 — **%62 fazla.**
Yönü kendi belirleyebilen biri için (grafik, emir akışı, haber) bot bir **oynaklık
tarayıcısı** olarak değerli: "şu an hangi coinler hareketli" sorusuna cevap veriyor.
Yön sinyali olarak değil.

**KARAR: scalp fikri ölçüldü ve çalışmıyor. Bota hiçbir şey eklenmedi.**

---

## ⭐ ÖN-KAYIT — "eski 1,5R kısmi kuralı lehimize mi?" (2026-08-12, kullanıcı sorusu)

**Nasıl bulundu:** kullanıcı açık pozisyonların TP1'lerini panelden sordu. İnceleme
`kismi_pay=0.40` ayarı ile kodun fiilen yaptığı şeyin **çeliştiğini** gösterdi.

**Çelişki:** `testbot.py:902` her turda TP1'i yeniden hesaplıyor ve **yapısal TP1 ile
1,5×risk'ten hangisi daha yakınsa** onu seçiyor (`tp1_efektif_hesapla`, 2026-07-04'ten
kalma). Stop dar olduğunda 1,5R seviyesi %4'ten yakın kalıyor ve kullanıcının %40
ayarını **sessizce eziyor.**

Ayrışma sınırı: `1,5 × stop% < 10 × 0,40`  →  **stop < %2,67**.
`asgari_stop_pct = %2,0` olduğu için bu aralık dar değil.

Canlı kanıt (12 Ağustos, 4 açık pozisyon):

| | stop | 1,5R | %40 kuralı | fiilen kullanılan |
|---|---|---|---|---|
| UMA | %0,96 | **%1,43** | %4,00 | %1,43 — **1,5R ezdi**, yarısı −%1,4'te satıldı (+46$) |
| IOTX | %2,80 | %4,20 | %4,00 | %4,00 |
| RVN | %4,49 | %6,73 | %4,00 | %4,00 |
| ME | %3,20 | %4,79 | %4,00 | (kural öncesi giriş, TP1=TP2) |

### Sınanan
Aynı girişlerde 4 kural: **A)** kısmi yok · **B)** sabit %40 (niyet edilen) ·
**C)** mevcut fiili = yakın olan{%4, 1,5R} · **D)** saf 1,5R. Şekil için 1,0R/2,0R/3,0R.

**Asıl test dar-stop alt kümesinde** (stop < %2,67) — iki kural yalnızca orada
ayrışıyor. Genel ortalama farkı sulandırır, karar oradan okunmayacak.

Betik: `scratchpad/kismi_15r.py` · veri: `klines_1h_uzun` (566 sembol, 2 yıl, **gerçek
boğa + gerçek ayı**) · mekanik canlının aynısı (A-stop, Wilder ATR, %10 hedef, 72s,
maliyet %0,13, kısmi sonrası stop başabaşa ÇEKİLMEZ).

### GEÇME ÖLÇÜTÜ (koşturmadan önce yazıldı)
1,5R kuralı **kalır** ancak dar-stop alt kümesinde şunların **hepsi** sağlanırsa:
1. `C (mevcut)` sermaye getirisi `B (sabit %40)`'ı **yenmeli**
2. Bu üstünlük **iki zaman yarısında da** aynı yönde olmalı
3. Boğa ve ayı rejimlerinin **ikisinde de** çökmemeli
4. Kaç ayrı sembolden geldiği raporlanacak (`t_kume`)

Geçmezse `kismi_kar_r` kapatılır ve %40 ayarı sözünü tutar. Sonuç ne olursa olsun
deftere yazılır.

**BEKLENTİM (yanılabilirim, kayda geçsin):** 1,5R'nin **kaybettireceğini** bekliyorum.
Daha önce beş kez çıkan kural aynı yöne işaret ediyor: *"iyi girişte sıkı çıkış
kazancı keser."* Dar stoplu işlemde 1,5R çok erken bir seviye — pozisyonun yarısı
%10 hedefe gitme şansını hiç kullanamadan kapanıyor. Ama dar stop aynı zamanda
**büyük pozisyon** demek (risk-öncelikli boyutlandırma), yani erken kâr almanın
dalgalanma faydası bu hücrede en yüksek. Bu yüzden emin değilim.

### SONUÇ — 1,5R kuralı KALDI (geçme ölçütünü sağlayamadı)

Koşturuldu: `scratchpad/kismi_15r.py`, 2 yıl, 566 sembol.

**ÖNEMLİ DÜZELTME (koşturma sırasında):** ilk turda `asgari_stop_pct` kapısı
uygulanmamıştı; ölçülen 34.084 olayın **%71'i canlıda zaten reddedilecek** (stop < %2)
işlemlerdi. Canlı popülasyona daraltıldı: **N=13.951, 510 sembol, stop medyanı %3,27**
(canlı açık pozisyonlarla uyumlu). Aşağıdaki her sayı bu daraltılmış evrenden.

Ayrışma bandı gerçek boyutu: `%2,0 ≤ stop < %2,67` → **canlı girişlerin %30'u.**

#### Asıl test — dar stop alt kümesi (N=4.195)

| kural | sermaye/işlem | kısmi değdi | A yarısı | B yarısı |
|---|---|---|---|---|
| A) kısmi YOK | **+0,038** | 0% | +0,057 | +0,021 |
| B) sabit %40 (niyet edilen) | +0,005 | 38% | −0,002 | +0,011 |
| C) MEVCUT (yakın olan) | **−0,011** | 41% | −0,016 | −0,006 |
| D) saf 1,5R | −0,011 | 41% | −0,016 | −0,006 |

**Ölçüt 1 (C, B'yi yenmeli): HAYIR** — C, B'nin 0,016 altında. Pencere burada kapandı.
Ölçüt 2: iki zaman yarısında da C daha kötü (tutarlı, ama B lehine).
Ölçüt 3: NÖTR ve AYI'da C daha kötü; BOĞA'da 0,005 daha iyi ama N=295 (hüküm yok).
Ölçüt 4: `t_kume` C −0,10 / B +0,05 — ikisi de sıfırdan ayrılmıyor.

#### Beklenti tuttu, ama asıl bulgu daha büyük

Beklentim "1,5R kaybettirir" idi — **doğru çıktı.** Ama asıl örüntü, kısmi kârın
**erkenliğinde monoton**:

| | tüm olaylar | dar stop | geniş stop |
|---|---|---|---|
| 1,0R | +0,018 | −0,029 | +0,039 |
| 1,5R | +0,041 | −0,011 | +0,064 |
| 2,0R | +0,050 | +0,008 | +0,068 |
| 3,0R | +0,065 | +0,036 | +0,077 |
| **kısmi YOK** | **+0,065** | **+0,038** | **+0,076** |

Kısmi kâr ne kadar erken alınırsa o kadar kaybettiriyor; 3,0R zaten kısmiye ancak
%13 değdiği için "kısmi yok" ile aynı yere geliyor. **Altıncı kez aynı kural:
"iyi girişte sıkı çıkış kazancı keser."**

#### KARAR
1,5R ezmesi **kaldırılmalı** — ama `kismi_kar_r = 0` GÜVENLİ DEĞİL: SHORT'ta
`tp_r = giriş − 0×risk = giriş` olur, `max(yapısal, giriş)` girişin kendisini seçer
ve TP1 anında tetiklenir. Doğru onarım kod tarafında: `tp1_efektif_hesapla` çağrısı
`cikis_modu == "sabit_hedef"` pozisyonlarda **atlanmalı** (klasik çıkış modları
1,5R'yi korur — orada yapısal TP1 2,6–5,2R uzakta ve hiç tetiklenmiyordu, 2026-07-04).

Kısmi kârın kendisi (%40) kapatılmıyor: kullanıcı 2026-08-11'de bunun kenarı
küçülttüğünü **bilerek** kabul etmişti (tek işlem bazında kâr koruması). Bu ölçüm o
kararı değiştirmiyor, yalnızca **ayarın sözünü tutmasını** sağlıyor.

### KULLANICI KARARI: 1,5R KALSIN (2026-08-12)

Ölçüm sonucu sunuldu, onarım **uygulanmadı**. Kullanıcının gerekçesi: stop dar
olduğunda kâr alma erken tetikleniyor ve bunu **istiyor**.

Mekanik netleştirmesi (kullanıcı "stop erken tetikleniyor" dedi, düzeltildi):
stop HAREKET ETMİYOR; short'ta girişin üstünde duruyor. Erkene gelen **TP1**:
`TP1 = yakın olan{%4 · 1,5×stop%}`. Dar stop → 1,5R küçülür → kâr alma girişe yaklaşır.

Kararın bedeli açıkça kayda geçti: dar-stop diliminde (canlı girişlerin %30'u)
işlem başına **−0,016 sermaye**, `t_kume −0,10` — yani **gürültüden ayrışmıyor**.
Kanıt "zararlı" demiyor, "bedava değil" diyor. Kullanıcı 2026-08-11'de `kismi_pay`
için de aynı takası bilerek yapmıştı (kenardan feragat ↔ tek işlem kâr koruması).

Karşı-argüman da kayda geçsin: dar stop = büyük pozisyon (risk-öncelikli
boyutlandırma), erken alınan yarı daha çok dolar kilitler. Ölçüm bunun getirdiğinden
çok götürdüğünü söylüyor ama fark istatistiksel değil.

**Değişen hiçbir şey yok — pencere (6/138) sıfırlanmadı, bot kesintisiz.**
Geri dönmek istenirse tek satır: `testbot.py:902` çağrısını `cikis_modu ==
"sabit_hedef"` pozisyonlarda atla. `kismi_kar_r = 0` YAPILMAMALI (SHORT'ta TP1=giriş
olur, anında tetikler).

---

## ⭐ AYNA DEFTERİ — "botun girişlerinde benim çıkışım" (2026-08-12, kullanıcı kararı)

**Soru:** *"Botun pozisyonlarını kâr ettiğini gördüğüm ve yeterli bulduğum yerde
kapatsam işe yarar mı? Reelde de böyle yapmayı düşünüyorum."*

**Neden geçmiş veriyle ölçülemez:** kullanıcı sabit bir eşik uygulamıyor — grafiğe,
hacme, coinin davranışına bakıyor. Bu bilgi geçmiş mumların içinde **yok**. Backtest
"+%X'te kapat" kuralını ölçebilir (13 kez ölçüldü, 13'ü de kaybettirdi) ama
**yargıyı** ölçemez. Yargı yalnızca ileriye doğru kaydedilebilir.

**Kullanıcının fikri:** mevcut `benim.py` defterini kullanmak — "tamamen farklı
düzlem, karışmaz". Ayrılık iddiası **doğru** (ayrı state/defter/equity, aynı
boyutlandırma), ama `benim.py`'nin kuruluş şartıyla çelişiyor: *"çıkışlar AYNI kalsın,
fark yalnızca GİRİŞ kararından gelsin."* Bu deney tam tersi (giriş aynı, fark çıkıştan).
İkisi tek defterde toplanırsa equity eğrisi iki deneyin toplamı olur ve **ayrılamaz** —
`benim.py`'yi doğuran problemin bir kat yukarısı. Ayrıca `giris_ac` o anki piyasadan
açıyor, botun giriş fiyatından değil → eşleşme bozulurdu.

### Kurulan: dördüncü kasa `ayna.py`

Bot bir pozisyon açtığında **birebir kopyası** aynaya düşer (fiyat/boyut/stop/TP
kopyalanır, yeniden hesaplanmaz) ve **botun kendi kurallarıyla** yönetilir.
Kullanıcı dokunmazsa ayna botun **aynısını** yapar → **kontrol grubu bedava gelir.**
Tek yetki: panelden "kapatırdım".

| defter | fark nereden gelir |
|---|---|
| `testbot` | — (referans) |
| `golge` | botun **reddettiği** girişler |
| `benim` | **giriş** kararı |
| `ayna` | **çıkış** kararı |

Dördü de aynı çıkış motorunu kullanır; her biri **tek değişkende** ayrışır.

**Başlangıç:** botun o anki durumunun tam kopyası (equity 8.201,18 $ + 5 açık pozisyon
+ id'ler). İki defter aynı noktadan başladı, fark 0,00 $. Eşleştirme id üzerinden.

**Sağlamlık:** `ayna.kaydet` ilk günden **atomik** (gölge defterin 11 Ağustos'ta 314 $
saptıran hatasının kökü atomik olmayan kayıttı). Bot kancaları try/except — ayna
çökerse bot etkilenmez. Bildirim göndermez.

### Yanında düzeltilen gerçek hata
`panel_sunucu.py` → `pozisyon_kapat` eylemi pozisyonu **listeden çıkarmıyordu**.
Panelden elle kapatılan her pozisyon sonraki turda **bir kez daha** kapanır, çift
defter kaydı + çift PnL üretirdi. Gölge defterde bu hata 11 Ağustos'ta fiilen
gerçekleşmişti (BANANAS31). Artık `benim.py:165`'teki doğru sürümle aynı.

### Okuma eşiği
Eşli karşılaştırma (aynı pozisyonun iki çıkışı) olduğu için coin/rejim/giriş kalitesi
birbirini götürüyor — **~30 karar** kabaca okuma verir, 138 işlemlik pencereye gerek yok.

**Tuzaklar (baştan kayda geçsin):** ① seçici bakma — yalnız kapattıklarını değil,
**tuttuklarını da** kaydet; ② sonradan karar — kayıt fiyatı gördüğün an düşmeli;
③ maliyet — erken çıkış fazladan bir alış-satış, %0,13 karşılaştırmaya dahil (kod
zaten uyguluyor).

### 🔴 HATA VE ONARIMI — ayna defterine gölge sızıntısı (2026-08-12, aynı gün)

**Kullanıcı bildirdi:** *"BLESS aynada var ama botun pozu yok"* · *"ayna LONG açıyor"*.

**Sebep — benim hatam.** `_aynala` kancasını `yeni_giris_ac` içine **korumasız**
koydum. Ama o fonksiyon **bota özel değil**: `golge.py` ve `benim.py` de aynı
fonksiyonu çağırıyor (defter yolunu `_DEFTER` ile geçici değiştirerek). Sonuç: gölge
defterin **reddedilmiş LONG girişleri** (pump_long_tezi) aynaya düştü. Ayna, botun
hiç açmadığı BLESS/BTW/BEAT/APR/QTUM/BOT/BR/HOLO pozisyonlarını açmış göründü.

Bu, `_defterde` deseninin tam olarak önlemek için var olduğu tuzağın kendisi — ve
kancayı koyarken onu düşünmedim.

**Onarım:** `_DEFTER is not None` ise aynalama yapılmaz — o durumda çağrı başka bir
defter (gölge/benim/aynanın kendisi) için koşuyor demektir. Dört durumla sınandı
(bot ✓ aynalanır · gölge ✗ · benim ✗ · aynanın kendi turu ✗).

**Temizlik:** 5 sızıntı kaydı + 4 sızıntı pozisyonu silindi, equity kararlardan
yeniden kuruldu (8.420,84 → **8.817,00**). Kullanıcının **5 kararı korundu** — deneyin
asıl verisi onlar. Yedek alındı.

**Ders:** paylaşılan bir fonksiyona kanca koyarken "beni kim çağırıyor" sorusu
sorulmalı. Bu projede o sorunun cevabı zaten `_DEFTER`'de duruyordu.

### İlk sonuçlar (N=2, hüküm yok)

| coin | senin çıkışın | botun çıkışı | fark |
|---|---|---|---|
| RVN | +228,69 | TP2 +282,88 | **−54,19** |
| CAP | +40,77 | STOP −67,08 | **+107,85** |
| | | **net** | **+53,66** |

Örüntü tanıdık: **erken çıkış kaybedeni kesiyor, kazananı da kesiyor.** CAP'te kâr
korundu, RVN'de hedefin bir kısmı bırakıldı. İki işlemden kural çıkmaz — okuma eşiği
~30 karar.

### Panel eksiği — verilen kararın 3'ü görünmüyordu (2026-08-12)

**Kullanıcı bildirdi:** *"aynada kapatılmış 2 poz görünüyor sadece"* — beş karar
verilmişti.

**Sebep:** `karne()` yalnızca **iki defterde de kapanmış** işlemleri döndürüyordu.
ME/UMA/IOTX botta hâlâ açık olduğu için karşılaştırılamıyor, dolayısıyla listeye
hiç girmiyorlardı. Karar kaybolmuş gibi duruyordu.

**Onarım:** `karne()` artık iki küme döndürüyor —
- **kesin**: ikisinde de kapandı, fark **gerçekleşti**
- **bekliyor**: aynada kapandı, botta açık; botun **gerçekleşmemiş** K/Z'si canlı
  fiyattan gösterilir, parantez içinde ve `elle_fark` toplamına **dahil edilmez**

Bu ayrım önemli: bekleyen farkı toplama katmak, henüz olmamış bir sonucu karneye
yazmak olurdu. Panelde "bekliyor" rozetiyle ve soluk renkle ayrışıyor.

**Durum:** 5 karar · 2 kesinleşti (net **+53,66 $**) · 3 bekliyor.

### 🔴 YANILTICI KIYAS — "ama ayna realize etmiş oluyor o kârı" (2026-08-12, kullanıcı yakaladı)

**Kullanıcı haklıydı ve bu, işaretin ters dönmesine yol açacak kadar ciddiydi.**

Panel iki defterin **gerçekleşmiş** equity'sini kıyaslıyordu. Ayna bir pozisyonu
kapattığında kârı **bankaya yazıyor**; botun aynı pozisyonu hâlâ açık olduğu için o kâr
botun equity'sine **hiç yansımıyor**. Yani ölçülen şey karar değil, **"kim daha önce
kapattı"** oluyordu.

| | gerçekleşmiş | açık K/Z | efektif |
|---|---|---|---|
| ayna | 8.817,00 | 0 (0 açık) | **8.817,00** |
| bot | 8.597,00 | +429,78 (3 açık) | **9.026,78** |

Panelde **+220 $ (ayna önde)** yazıyordu; doğrusu **−210 $ (ayna geride)**. İşaret ters.

**Onarım:** kıyas **efektif equity** (gerçekleşmiş + açık K/Z) üzerinden yapılıyor;
panelin manşeti artık **KESİNLEŞEN fark** (+53,66 $) — tek dürüst skor tablosu o.
Efektif karşılaştırma bilgi olarak duruyor ama "karar değil kıyas" diye etiketli.
CLI'da (`ayna.py --durum`) aynı düzeltme yapıldı.

**Ders:** bu, 11 Ağustos'ta frende düzelttiğimiz hatanın aynısı — *gerçekleşmiş equity,
açık pozisyon varken tek başına bir şey anlatmaz.* Aynı hatayı iki farklı yerde
yaptım; artık bu projede "equity" gördüğüm her yerde "açık pozisyonlar dahil mi?"
sorusu refleks olmalı.

### Sızıntının ikinci zararı: KAYIP GÖZLEM

Sızıntı yalnızca çöp eklemedi, **gerçek bir veriyi de engelledi.**

Bot 16:58'de kendi **BLESS SHORT**'unu (id 32, MA50+ucuz) açıp kapattı — TP1 +44,74,
TP2 +140,07, **toplam +184,81 $**. Bu pozisyon aynaya **hiç düşmedi**, çünkü o anda
aynanın açık listesinde gölgeden sızmış bir **BLESS LONG** vardı ve `aynala()`'nın
aynı-sembol koruması gerçek girişi reddetti.

Kullanıcı o pozisyon için karar vermedi; veri **geri üretilemez** (sonucu bilerek
"şurada kapatırdım" demek ölçümü sahteleştirir). Deneyde **eksik gözlem** olarak
kayda geçti (`ayna_state.json → kayip_veri_notu`). `sonraki_id` de botla hizalandı
(58 → 33; gölge id'leri şişirmişti).

## ⭐ YAYIN KARNESİ — "11'inde aldığımız tarihten itibaren göster" (2026-08-12, kullanıcı)

Defter 23 Temmuz'a kadar gidiyor ve **artık var olmayan bir botun** sonuçlarını içeriyor
(risk %3, asgari stop yok, R/R kapısı açık, A+B ve MA50 kapıları yok). Tek karnede
toplamak, eski botun karnesini bugünkünün üzerine yazmaktır.

**Ankraj: 2026-08-11 12:48:31** — S9'un uygulandığı an (`islem_risk_pct %3→%1,5`,
`asgari_stop_pct %2,0`). State'teki `_zirve_sifirlama` aynı anı, aynı gerekçeyle zaten
kaydetmişti. Config: `testbot.yayin_ts` (yalnızca **görünüm**; equity ve işlem geçmişi
değiştirilmez).

**Filtre GİRİŞ zamanına göre** (`çıkış ts − tutma_saat`) — "bu bot hangi işlemleri
**açmaya** karar verdi". Çıkışa göre süzmek, 10 Ağustos girişli RVN'i (+282,88) bugünkü
bota yazardı.

### "ME ve UMA'yı bu bot açtı" — kullanıcı sordu, ölçüldü

Kullanıcı haklıydı ama **yarısında**. Giriş anındaki risk yüzdeleri:

| giriş | coin | risk % | not |
|---|---|---|---|
| 11 Ağu 03:27 | ME | %1,50 | ayar değil — **akıllı para LONG**'du, boyut yarıya indi (%3→%1,5) |
| 11 Ağu 08:34 | PROM | %2,99 | eski %3 |
| 11 Ağu 10:30 | RVN | %3,00 | eski %3 |
| 11 Ağu 12:21 | UMA | %0,76 | kaldıraç tavanı bağladı |
| *— S9 —* | | | |
| 11 Ağu 16:25+ | hepsi | %1,5–1,6 | bugünkü ayar |

**Kapılar aynıydı** (A+B 10 Ağu, MA50+ucuz 11 Ağu 00:12) — o yüzden "bu bot açtı"
sezgisi doğru. Değişen **boyut ve stop tabanı**.

Keskin kanıt: **UMA'nın stopu %0,96** — bugünkü bot `asgari_stop_pct = %2,0` ile onu
**reddederdi**. Yani UMA, bugünkü botun asla açmayacağı bir işlem.

**Kullanıcı kararı: ankraj 12:48'de kalsın.** ME ve UMA "devir" sayılıyor; panelde
sebebi yazılı.

### Üç sayı ayrı gösteriliyor (toplamak yanıltır)

| | |
|---|---|
| bu botun açtıkları | 12 işlem · %25 kazanç · ort −0,43 R · kapanan −390,34 + açık +216,95 = **saf karne −173,39** |
| devir | kapanan +611,32 · hâlâ açık +288,10 (ME, UMA) |
| ücret + fonlama | −109,20 |
| **kasa** | 8.412,06 → 8.523,84 (**+111,78**) |

Açık pozisyonlar da ayrıldı: ME/UMA yayından önce açıldığı için "efektif K/Z"ye tek
parça bakmak eski botun taşıdığı kârı bugünkünün hanesine yazardı.

### 🔴 PANEL SÜREKLİ DÜŞÜYORDU — sebep benim eklediklerimdi (2026-08-12)

**Kullanıcı bildirdi:** *"panel sürekli düşüyor ve yeniden yükleniyor"*.

**Ölçüm:** `/api/durum` **43,3 · 85,1 · 19,9 saniye** sürüyordu. Panel ise **30 saniyede
bir** yeniliyor → istekler üst üste yığılıyor, kalıcı kuyruk oluşuyordu.

**İki sebep üst üste bindi, ikisi de bugün benim eklediklerimden:**

1. **İstek başına ~16 ardışık ticker çağrısı.** Ayna defteri ve yayın karnesi eklenince
   `/api/durum` her açık pozisyon, her ayna pozisyonu, her bekleyen karar ve bir kez daha
   botun pozisyonları için **ayrı ayrı** `fiyat_fapi` çağırıyordu.
2. **Sunucu tek iş parçacıklıydı** (`HTTPServer`). Yavaş bir API isteği, sayfanın kendisini
   (`panel.html`, ~108 KB) de bloke ediyordu — tarayıcı için "panel düştü" demek bu.

**Onarım:**
- `_fiyatlar()` önbelleği: `testbot._tum_fiyatlar()` **tek çağrıyla** bütün perp
  fiyatlarını getiriyor, 8 sn TTL. **16 istek → 1 istek.** Emir/kapatma yollarında
  önbellek KULLANILMIYOR (orada taze fiyat şart).
- `ThreadingHTTPServer`: yavaş bir istek diğerlerini kilitlemiyor.

| | önce | sonra |
|---|---|---|
| `/api/durum` | 43–85 sn | **0,03–0,79 sn** |
| `panel.html` | bloke oluyordu | 0,02 sn |
| 8 paralel istek | — | 0,18 sn, hatasız |

**Ders:** panel bir ölçüm katmanı; ona her yeni bölüm eklendiğinde **istek sayısı**
sorulmalı. Aynı ders 11 Ağustos'ta da çıkmıştı — o gün toplu indirme API'yi doyurup
botun turlarını 3 saat öldürmüştü. `_tum_fiyatlar()` zaten o gün bu yüzden yazılmıştı;
panelde kullanmayı atlamışım.

### SANAL 10.000$ — "12 giriş üzerinde göster, 30 değil" (2026-08-12, kullanıcı)

**İstek:** panelde bakiye, botun **kendi açtığı 12 işlem** üzerinden 10.000$'dan
başlatılarak gösterilsin; **UMA, ME ve bütün devir işlemleri hariç** (RVN'in +282,88$'ı
dahil).

**Kritik incelik — dolar toplanmıyor, yüzde bileşikleniyor.** İşlemler 8.000–8.600$'lık
bir kasada açıldı; dolarları 10.000'e eklemek, küçük hesabın dolarlarını büyük hesaba
yazmak olurdu. Boyutlandırma **risk-yüzdesi esaslı**, yani pozisyon büyüklüğü equity ile
**doğru orantılı** — 10.000$'lık hesap aynı işlemleri `10000/8400` kat büyük yapardı ve
**yüzde getirisi aynı çıkardı.** Bu yüzden her işlemin getirisi giriş anındaki equity'ye
oranlanıp bileşikleniyor. Dönüşüm tam, yaklaşık değil.

**Sonuç (12 işlem, 18 kayıt — kısmiler dahil):**

| | |
|---|---|
| kapananlardan sonra | **9.558,08** (−%4,42) |
| açık pozisyonların etkisi | **+%2,49** (IOTX +2,52 · RVN −0,47 · DOS +0,44) |
| **güncel** | **9.795,85 (−%2,04)** |

Ücret ve fonlama dahil değil (işlem defterine yazılmıyor) — bu sayı **işlem
kararlarının saf karnesi**. Gerçek kasa ayrıca ücret/fonlama taşıyor.

Panelde eğrisiyle birlikte, yayın bölümünün manşeti olarak duruyor.

## ⭐ KASA SIFIRLAMASI — "23 Temmuz botu ile işimiz bitti" (2026-08-12, kullanıcı kararı)

**İstek:** serbest para yeni kasaya göre hesaplansın; eski botun kaybı bugünkü botu
kısıtlamasın.

**Gerekçe:** 23 Temmuz – 11 Ağustos 12:48 arasında kaybedilen **−1.587,94 $**, artık
var olmayan bir yapılandırmaya aitti (risk %3, asgari stop yok, kapıların bir kısmı
yok). Ama boyutlandırma ve fren gerçek kasaya baktığı için o kayıp bugünkü botun
oynayabileceği büyüklüğü hâlâ kısıtlıyordu. Aynı gerekçe 11 Ağustos'ta `zirve_equity`
için de kabul edilmişti — bu, onun kasa tarafındaki karşılığı.

### Neden 9.792 değil 9.558 yazıldı

Panelde görünen **9.792,18** bir **efektif** değerdi — açık pozisyonların
**gerçekleşmemiş** kârını içeriyordu. Onu gerçekleşmiş equity alanına yazmak,
pozisyonlar kapandığında aynı kârı **ikinci kez** saymak olurdu.

Yazılan: **9.558,08** = sanal karnenin **kapanmış işlem** bakiyesi. Açık pozisyonların
kârı kapandıkça normal yoldan gelir. Hedeflenen sonuç aynı, çift sayım yok.
(Kullanıcıya seçenek sunarken 9.792 yazmıştım; hata bendeydi, uygulamadan önce
düzeltildi ve söylendi.)

| | önce | sonra |
|---|---|---|
| equity | 8.552,14 | **9.558,08** |
| zirve_equity | 9.069,16 | 9.558,08 → *(tur sonrası 10.039,54, efektif zirveyi izliyor)* |
| serbest para | 6.573,52 | **7.579,46** |
| fren eşiği (−%25) | 6.801,87 | 7.529,66 |

### Dokunulmayanlar
- **İşlem defteri ve geçmiş** — hiç değiştirilmedi
- **Açık 5 pozisyon** — teminatları eski tabana göre hesaplanmıştı, aynen devam
  ediyorlar; yalnızca **yeni** girişler büyüyecek (hedef risk 128 $ → 143 $)
- **Ölçüm penceresi (12/138) SIFIRLANMADI** — getiri R ve yüzde ile ölçülüyor, hesap
  büyüklüğünden bağımsız. Strateji değişmedi, yalnızca ölçek değişti.

### Panel tarafı
`_yayin_karnesi` artık `_kasa_sifirlama.delta`'yı tabana ekliyor. Yoksa equity
eğrisindeki sıçrama **sahte +1.005,94 $ kâr** gibi görünürdü. Doğrulandı: yayın
karnesi sıfırlamadan önce ve sonra aynı — **+140,08 $**.

Yedek: `testbot_state.json.yedek-20260812-225602`. Geri alma: equity ve zirve_equity'yi
yedekten yaz, `_kasa_sifirlama` alanını sil.

### Ayna defteri de kaydırıldı — yoksa kıyas bozulurdu (2026-08-12)

**Kullanıcı:** *"ayna defterini de botunki gibi yap, 8550 olmasın yani"* — ve bu sadece
görüntü meselesi değildi.

Botun kasası +1.005,94 $ kaydırılmıştı. Ayna kaydırılmasaydı iki defter **farklı
ölçekte** kalırdı ve `ayna − bot` farkı **1.005,94 $ kadar sahte** kayardı. Deneyin
ölçtüğü tek şey o fark olduğu için bu, ölçümü doğrudan bozardı.

- efektif fark sıfırlama öncesi görünen: **−1.230,66 $** (sahte)
- kaydırma sonrası: **−206,90 $** (gerçek)

**Kaydırma, çarpma değil.** Botta yapılan işlem toplamaydı (`equity += delta`), o yüzden
aynaya da aynı toplama uygulandı. Hem `equity` hem `baslangic_bakiye` kaydırıldı →
aynanın **kendi $ kazancı (+599,57) değişmedi**.

| | önce | sonra |
|---|---|---|
| ayna equity | 8.800,75 | **9.806,69** |
| ayna başlangıç | 8.201,18 | 9.207,12 |
| kendi $ kazancı | +599,57 | +599,57 *(aynı)* |

İşlem defteri, açık pozisyonlar ve **kullanıcının 6 kararı** değiştirilmedi.
Yedek: `ayna_state.json.yedek-20260812-233326`.

### Ayna sağlık kontrolü (aynı anda yapıldı)
Sızıntı onarımından sonra aynalama **kusursuz çalışıyor**: COTI (id 34) aynalandı ve
botla aynı şekilde STOP oldu; DOS (id 35) aynalandı, kullanıcı elle kapattı (+58,64).
Botta olup aynada hiç görülmeyen pozisyon **yok**.

**Karne durumu:** 6 karar · 2 kesinleşti (**net +53,66 $**) · 4 bekliyor.

### "ben" hesabı KAYDIRILMADI — gerekmiyordu (2026-08-12)

**Kullanıcı:** *"ben ve botu da düzelt"*.

**Kontrol edildi:** `benim` hesabı **6 Ağustos'ta 10.000 $ ile bağımsız** başladı ve
yalnızca kullanıcının kendi 6 giriş kararını içeriyor. **23 Temmuz botunun kaybını hiç
taşımadı** — silinecek bir şey yok. Kaydırmak, hiç var olmamış bir kaybı geri ekleyip
hesabı **şişirmek** olurdu (10.167,88 → 11.173,82 sahte).

Bugünkü DOS/COTI işlemleri de kontrol edildi: hepsi `kaynak='elle'`, yani panelden
kullanıcı açmış. **Ayna türü bir sızıntı yok.**

### Ama gerçek bir sorun vardı: eğrilerdeki sahte sıçrama

Kasa sıfırlaması equity **eğrisinde** dikey bir atlama bıraktı — grafikte o an
+1.005,94 $ kazanılmış gibi görünüyordu, ve `maks_dusus` hesabı da bundan etkileniyordu.

`_egri_duzelt()`: sıfırlamadan **önceki** noktalar aynı miktar yukarı kaydırılıyor →
eğri sürekli oluyor ve her nokta bugünkü kasa ölçeğinde okunuyor. **Yalnızca görünüm**,
dosyadaki veri değişmiyor. Bot ve ayna eğrilerine uygulandı; `ben` eğrisine
uygulanmıyor (sıfırlama görmedi). Doğrulandı: iki eğride de 600 $ üstü sıçrama **yok**.

### Kalan bir dürüstlük sorunu — panelde işaretlendi
"BOT vs BEN" sayfası **aynı dönemi kapsamıyor**: bot 23 Temmuz'dan (eski %3 riskli
yapılandırma dahil), ben 6 Ağustos'tan beri. Bu yüzden "en kötü düşüş" gibi ölçüler
doğrudan kıyaslanamaz (bot %−17,77 vs ben %−3,30 — botunki eski dönemin kaybını da
içeriyor). Sayfaya uyarı notu eklendi; botun bugünkü hâlinin saf karnesi Özet
sekmesindeki "Yayından beri" bölümünde.

Dönemi hizalamak ayrı bir karar — kullanıcıya soruldu, henüz istenmedi.

### 🔴 "BTW'ye girildi" mesajı geldi ama pozisyon botta yoktu (2026-08-13)

**Kullanıcı bildirdi.** Doğru — pozisyon **senin kendi hesabındaydı** (`benim`), bot
onu hiç açmadı.

```
BTW SHORT · giriş 12 Ağu 23:24 · çıkış 13 Ağu 00:06 STOP −77,89 $ · kaynak='elle'
BENIM defterinde  : VAR      TESTBOT defterinde : YOK (hiç kayıt yok)
```

**Sebep — bugün üçüncü kez aynı kök:** `testbot.yeni_giris_ac` **bota özel değil**;
`golge.py`, `benim.py` ve `ayna.py` de onu çağırıyor. İçindeki Telegram çağrısı
"bot girdi" diye haber veriyor. `golge.py` ve `ayna.py` bunu ilk günden susturuyordu,
**`benim.py`'de eksikti.** Bildirimler 3 Ağustos'tan beri kapalı olduğu için bugüne
kadar görünmedi — 12 Ağustos'ta giriş bildirimini açınca ortaya çıktı.

**Onarım:** `benim._defterde` artık `telegram_gonder` ve `toast_gonder`'ı da
susturuyor (diğer iki defterle aynı). Bu hesabın girişini zaten kullanıcı açıyor ve
panel anında onaylıyor; bota ait olmayan hareketi bot bildirimi gibi göndermek yanıltır.

### Bu kökten çıkan hatalar (bugün üçü de)
1. `_aynala` korumasızdı → gölgenin LONG'ları aynaya düştü
2. Panel `pozisyon_kapat` pozisyonu listeden çıkarmıyordu → çift kayıt riski
3. `benim.py` bildirimleri susturmuyordu → sahte "[TESTBOT] GİRİŞ" mesajı

**Kalıcı önlem:** `scratchpad/defter_izolasyon_testi.py` — dört defterin izolasyonunu
birden doğrular: bot çağrısında bildirim **gider** ve ayna **kopyalar**; gölge/benim/ayna
çağrılarında **hiçbiri** olmaz, her biri **kendi defterine** yazar, ve çağrı sonrası
bot **normale döner**. 14 kontrol, hepsi geçti. Paylaşılan bir fonksiyona her yeni yan
etki eklendiğinde bu test koşturulmalı.

### Ücret/fonlama da yayın dönemine ayrıldı (2026-08-13, kullanıcı)

**Kullanıcı:** *"defter bize 11 Ağustos sonrası veriyi göstersin, 23 Temmuz değil —
onun ayrımını yap"*.

`kumulatif_giris_ucret` ve `kumulatif_funding` state'te **23 Temmuz'dan beri toplam**
tutuluyordu; panelde iki dönem ayrılmıyordu. Ayrıldı.

**Yöntem.** Giriş komisyonu = pozisyonun **tam notional**'i × taker. Kısmi kâr alınmış
pozisyonlarda kayıtlar pozisyonu böldüğü için (yarı + kalan yarı) id başına notional
**toplanıyor**, hâlâ açık olanların kalan miktarı da ekleniyor. Fonlama mutabakattan
türüyor (`artık = −giriş ücreti + fonlama`).

**Doğrulama:** bu yolla hesaplanan toplam giriş ücreti **88,15 $**, state'teki
`kumulatif_giris_ucret` **88,16 $** — kuruş farkı yuvarlama. Fonlama toplamı da
**−186,05** ile birebir tutuyor. Yani ayrım uydurma değil, mutabık.

| | yayından ÖNCE (23 Tem–11 Ağu) | yayından BERİ |
|---|---|---|
| giriş komisyonu | 55,62 $ | **32,53 $** |
| çıkış komisyonu | — | **25,63 $** *(işlem sonuçlarına zaten dahil)* |
| **komisyon toplam** | — | **58,16 $** |
| **fonlama** | **+3,00 $** | **−189,05 $** |

### 🔴 Bulgu: asıl maliyet komisyon değil, FONLAMA

Kullanıcı "221 $ komisyon 16 işlemin mi?" diye sordu. Hayır — **221,58 $**'ın yalnızca
**32,53**'ü giriş komisyonu, **189,05**'i **fonlama**.

Fonlama yayından önce **artı** (+3,00) iken yayından sonra **−189,05**'e döndü. Sebep
yapısal: `A+B` kapısının tanımı *"funding ≤ −0,05 olan coini SHORT'la"* — negatif
funding **short'un ödemesi** demek. Kapı botu bilerek fonlama ödeyen tarafa koyuyor.

Anlık ölçüm (13 Ağustos, 8 açık pozisyon, notional 18.713 $): **günlük −100,13 $**,
yani ~9.500 $'lık hesabın **%1'i her gün**. En ağırları KAITO −0,506 %/8s (−45,94 $/gün),
COTI −0,370 (−17,92), RVN −0,180 (−19,60).

**Neden önemli:** A+B'nin 2 yıllık ölçümünde deftere *"funding maliyeti eklenmedi"*
diye yazmıştım. Ölçülen kenar işlem başına **+0,111 sermaye**; pozisyonlar 72 saate
kadar tutuluyor ve %1/gün × 3 gün = **%3**. Maliyet kenardan büyük olabilir.

**Bu, kapıyı kapatmak için yeterli değil** — ölçülmemiş bir kalem bulundu, o kadar.
2 yıllık funding verisi elimizde (`scratchpad/funding_gecmis/`, 567 sembol); A+B ölçümü
fonlama maliyeti dahil tekrar koşturulabilir. Kullanıcıya soruldu.

## ⭐ ÖN-KAYIT — A+B'nin funding MALİYETİ dahil sınavı (2026-08-13, koşturulmadan önce)

**Neden:** canlıda fonlama yayından beri **−189,05 $** çıktı ve şu an **günde −100 $**
akıyor (hesabın ~%1'i/gün). A+B'nin 2 yıllık ölçümünde deftere *"funding maliyeti
eklenmedi"* yazmıştım — o boşluk şimdi kapanıyor.

**Sınanan:** A+B'nin funding bacağı (`funding ≤ −0,05 %/8s → SHORT`), **fonlama
maliyeti dahil**. Aynı olaylar, aynı mekanik, tek fark maliyet kalemi.

**Fonlama muhasebesi.** Pozisyon tutulurken her 8 saatlik fonlama anında gerçek
tarihsel oran uygulanır. SHORT için P&L katkısı = Σ(oran) — oran negatifken **ödersin**.
Bu, canlı botun `funding_uygula` mantığıyla aynı işaret kuralı.

**Popülasyon:** canlı `asgari_stop_pct = %2,0` uygulanır (11 Ağustos'ta öğrenildi:
uygulanmazsa örneklemin %71'i botun hiç açmayacağı işlemlerden oluşuyor).

**Mekanik canlının aynısı:** A-stop · Wilder ATR · sabit %10 hedef · 72 saat · işlem
maliyeti %0,13 · giriş sonraki barın açılışı · pump kapısı · hacim tabanı $3M/24s ·
seyreltme 24 bar. Kontrol: rejim-eşleşmiş rastgele barlar.

Betik: `scratchpad/ab_funding_maliyetli.py` · veri: `klines_1h_uzun` (566 sembol, 2 yıl)
+ `funding_gecmis` (567 sembol).

### GEÇME ÖLÇÜTÜ (koşturmadan önce yazıldı)
A+B **kalır** ancak fonlama maliyeti dahil edildikten sonra şunların **hepsi**:
1. Net sermaye getirisi **> 0**
2. Kontrolü **yenmeli**
3. **İki zaman yarısında da** pozitif
4. Boğa ve ayı rejimlerinin **ikisinde de** çökmemeli
5. Kaç ayrı sembolden geldiği raporlanacak (`t_kume`)

Geçmezse kapı kapatılır ve gerekçe deftere yazılır.

**BEKLENTİM (yanılabilirim, kayda geçsin):** kenarın **yenileceğini** bekliyorum.
Maliyetsiz ölçümde net +0,111 sermaye/işlem idi. Fonlama −0,05 %/8s eşiğinde bile
72 saatte 9 fonlama anı × %0,05 = **%0,45**; ama kapı eşiği aşan coinleri de alıyor ve
canlıda gördüğüm oranlar **−0,18 ile −0,51** arasında. Ortalama −0,15 varsayarsam
72 saatte **%1,35** — kenarın kendisinden büyük. Yine de tutuş süresi çoğu işlemde
72 saatten kısa (stop erken vuruyor), o yüzden emin değilim: **gerçek fonlama yükü
tutma süresine bağlı ve onu ancak ölçüm söyler.**

### 🔴 SONUÇ — A+B, fonlama maliyeti dahil edilince KALDI (2026-08-13)

Koşturuldu: `scratchpad/ab_funding_maliyetli.py` · 8.666 işlem · **497 ayrı sembol** ·
2 yıl · canlı `asgari_stop_pct %2,0` uygulanmış.

| küme | sermaye/işlem | t | t_kume | isabet | fonlama% |
|---|---|---|---|---|---|
| SİNYAL — fonlamasız | **+0,154** | +5,68 | +1,36 | %28,6 | −0,341 |
| **SİNYAL — FONLAMALI** | **+0,027** | +1,01 | **+0,24** | %28,6 | −0,341 |
| KONTROL — fonlamasız | +0,071 | +1,76 | +0,60 | %23,4 | −0,030 |
| **KONTROL — FONLAMALI** | **+0,061** | +1,50 | +0,51 | %23,4 | −0,030 |

**Fonlamanın bedeli: −0,127 — kenarın %83'ü.**

#### Geçme ölçütü (ön-kayıtlı)
1. net > 0 — **EVET** (+0,027)
2. kontrolü yener — **HAYIR** (fark **−0,034**; kontrol +0,061 ile sinyali geçiyor)
3. iki zaman yarısı da + — **HAYIR** (A −0,076 / B +0,131)
4. boğa ve ayıda çökme yok — **HAYIR** (BOĞA −0,119 · AYI −0,021 · NÖTR +0,048)
5. 497 sembol · `t_kume +0,24`

→ **KALDI.** Beklentim doğrulandı: kenar fonlamayı kaldıramadı.

#### Mekanizma net görünüyor
Kontrolün fonlama yükü **−0,030**, sinyalinki **−0,341** — kapı, fonlama ödeyen coinleri
**bilerek seçtiği için 11 kat fazla** ödüyor. Kapının tanımı bu.

Tutuş süresine göre kırılım, fonlamanın **tam kenarın yaşadığı yerde** yediğini gösteriyor:

| tutuş | N | fonlamasız | FONLAMALI | fonlama% | isabet |
|---|---|---|---|---|---|
| 0–8 saat | 3.735 | −0,827 | −0,857 | −0,097 | %16,7 |
| 8–24 saat | 2.463 | +0,306 | +0,175 | −0,397 | %37,2 |
| 24–48 saat | 1.236 | +1,345 | +1,105 | −0,625 | %52,3 |
| 48–72 saat | 1.232 | +1,626 | +1,326 | −0,685 | %23,5 |

Kısa tutuşta fonlama az ama işlem zaten kaybediyor; kâr uzun tutuştan geliyor ve
fonlama orada en ağır. **Kenar ve maliyet aynı yerde büyüyor.**

#### Sınır (dürüstlük payı)
Fonlama **giriş notional'i** üzerinden hesaplandı; gerçekte SHORT kazanırken notional
küçülür, yani gerçek maliyet kazananlarda biraz daha az. Bu ölçüm fonlama yükünü
**hafif abartıyor** — ama kapıyı kurtaracak yönde değil: kontrolü **−0,034** ile
kaybediyor ve iki rejimde birden eksi.

**Not:** bu ölçüm yalnızca **A+B'nin funding bacağını** kapsıyor. `MA50+ucuz` kapısı
funding'e göre seçim yapmıyor; onun fonlama yükü ayrı ölçülmeli.

### Panel tamamen 11 Ağustos'a taşındı (2026-08-13, kullanıcı)

**Kullanıcı:** *"paneldeki bütün veriler 11 Ağustos'u baz alsın, 23 Temmuz verisi
olmasın, o zamana ait 20 işlem olmasın — sayıyı kontrol et"*.

**Sayı doğrulandı: tam 20.** Giriş zamanına göre ankraj öncesi 20 tam işlem var
(23 Tem 22:33 ON'dan 11 Ağu 12:22 UMA'ya). Hepsi eski yapılandırmaya ait.

**Merkezi filtre eklendi** (`_yayin_suz`, `_egri_kirp`, `_ankraj`) ve panelin bütün
veri kaynaklarına uygulandı:

| yer | önce | sonra |
|---|---|---|
| `son_islemler` (işlem geçmişi) | 54 kayıt, 20'si eski | **34 kayıt, 0 eski** |
| `karne` (kart sayaçları) | 41 işlem | **21 işlem** |
| `equity_serisi` (eğri) | 23 Tem'den, 4.500+ nokta | **11 Ağu 12:52'den, 326 nokta** |
| "BOT vs BEN" bot tarafı | 41 işlem, 23 Tem eğrisi | **21 işlem, 11 Ağu eğrisi** |

**Filtre GİRİŞ zamanına göre** — "bu bot hangi işlemleri **açmaya** karar verdi".
Çıkışa göre süzmek RVN/ME/UMA'yı (eski botun açtığı, yeni dönemde kapanan) yanlışlıkla
bugüne yazardı.

**Süzülmeyenler ve sebebi:**
- **"Yayından beri" bölümü** defteri kendi okuyor — devir işlemleri orada *ayrıca*
  gösterilmesi gerekiyor (mutabakat oradan kuruluyor).
- **`ben` hesabı** — 6 Ağustos'ta bağımsız başladı, hiç eski yapılandırma taşımadı.
- **Gerçek kasa rakamı** — hesabın fiili tutarı; fren ve boyutlandırma ona bakıyor,
  gizlemek yanlış olurdu. Etiketi "kasadaki fiili tutar" olarak netleştirildi.

Kart etiketlerindeki "tüm zamanlar ..." ikincil satırları kaldırıldı (sunucu zaten
süzdüğü için aynı sayıyı gösteriyorlardı).
