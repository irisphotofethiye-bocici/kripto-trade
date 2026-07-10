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

## Uygulama disiplini (her madde için geçerli)
1. Önce ÖLÇÜM, sonra karar entegrasyonu (erken-kuşak modeli: KAPI DEĞİL → forward-return → 25-30 olay → kapı).
2. Yeni eşik icat etme; mevcut config eşiklerini yeniden kullan veya ölçümün gösterdiği değeri al.
3. Tek seferde TEK değişken değiştir (hangi değişikliğin işe yaradığını ayırt edebilmek için).
4. Her değişiklik önce sanalda tam tur test.
5. N<25-30 = izlenim. Tek-rejim verisiyle eşik oynatma.
