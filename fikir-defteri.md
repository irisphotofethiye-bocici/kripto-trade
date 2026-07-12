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
- **Sınır:** Elimizde gerçek BOĞA sezonu verisi yok — SEZON katmanının boğa tarafı ancak boğa geldiğinde doğrulanır (K6 simetriği). O güne kadar F10'un kanıtlanabilir kısmı AYI/TEPKI_RALLISI ayrımıdır.

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
