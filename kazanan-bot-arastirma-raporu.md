# Kazanan Trade Botu — Dürüst Araştırma Raporu
*(2026-07-23 · internet araştırması + bizim sisteme uygulama · sade dille)*

---

## 0. Önce kısa cevap (acele edenler için)

**"Her koşulda kazanan tek bot" diye bir şey YOK.** Dünyanın en büyük fonları (Citadel gibi, 400+ uzmanla) bile tek bir sihirli bot çalıştırmıyor. Onların "her havada kazanan" dediği şey, **birbirinden bağımsız birçok stratejinin bir arada** çalıştığı bir **portföy**.

Senin "boğada bütün parametreleri değiştirmek gerekiyor" gözlemin bir **kusur değil** — trade'in doğası. Buna profesyonel dilde **"rejim değiştirme"** deniyor ve zaten standart yöntem. Yani içgüdün doğru; sadece adı var ve bir eksik var.

**Bizim durum:** elimizde iyi çalışan **bir** strateji var (düşüşe/yatayda "fade"). Kazanan sisteme giden yol, ona **ikinci bir strateji** (boğa/trend) eklemek + hangisinin ne zaman çalışacağına karar veren rejim beynini güçlendirmek. Bunun zeminini (F10 rejim beyni, dürüst test disiplini, risk tavanı) **zaten kurduk** — ki retail botçuların %80'i bunları hiç yapmıyor.

---

## 1. Trade botu türleri — ne yapar, ne zaman kazanır

Neredeyse tüm sistemler şu 6 aileden birine girer. Hiçbiri her piyasada kazanmaz; her biri belli bir "piyasa havasına" göre iyidir.

| Strateji | Ne yapar | En iyi olduğu piyasa | Zayıf yanı |
|---|---|---|---|
| **Trend-takip** | Yükseliş/düşüş trendine biner, sürdükçe tutar | Güçlü boğa veya güçlü ayı | Yatay/kararsız piyasada sürekli küçük zarar (choppy'de %20-40 düşüş) |
| **Ortalamaya dönüş (fade)** — *bizim bot* | Aşırıya kaçmış fiyatı ters oynar (pump'ı satar) | Yatay / dalgalı / düşüş | Güçlü trendde ezilir (yükselişi satmaya çalışıp squeeze yer) |
| **Market-making** | Alış-satış farkından (spread) sürekli küçük kâr | Her yön — ama hız + altyapı ister | Ani sert hareket, envanter riski; retail için zor |
| **Grid (ızgara)** | Belli aralıklarla alım-satım emirleri dizer, salınımdan kâr | Belli bir bantta gidip gelen fiyat | Bant kırılıp trend başlayınca zarar birikir |
| **Arbitraj / istatistiksel** | İlişkili varlıklar arası fiyat farkını yakalar | Her koşul — ama çok hız/altyapı ister | Kâr küçük; maliyet/gecikme yer |
| **Momentum** | "Yükseleni al, düşeni sat" | Süren güçlü hareketler | Dönüş anlarında zikzak (whipsaw) — *bizde defalarca çöktü* |

**Önemli sayı (araştırmadan):** trend-takip uzun vadede orta bir performans verir (Sharpe ~0.5-0.8) ama dalgalı piyasada büyük düşüşler yaşar; ortalamaya-dönüş daha yüksek performans verebilir (Sharpe ~0.8-1.2) ama hızlı ve isabetli giriş ister. *(Sharpe = getiriyi riske bölen bir kalite notu; yüksek = iyi.)*

**Bizim bot buradaki 2. satır** — ve ölçümlerimiz bunu defalarca doğruladı: fade kazanıyor, momentum/trend-yakalama denemeleri (beta, breakout, erken-giriş) hep çöktü. Bu tesadüf değil, botun kimliği.

---

## 2. Neden tek bot her yerde kazanamaz — "rejim" gerçeği

Her strateji bir piyasa havasına göre ayarlıdır. **Boğada trend-takip kazanır, yatayda fade kazanır — ve biri kazanırken diğeri kaybeder.** Aynı botu her iki havada da çalıştırırsan, yarı zaman kazanıp yarı zaman geri verirsin.

Profesyonellerin çözümü: **rejim tespiti + strateji değiştirme.**
- Piyasanın hangi "halde" olduğunu ölçerler (boğa / ayı / yüksek-oynaklık / sakin).
- Kullandıkları araçlar: **Gizli Markov Modelleri (HMM)**, Markov rejim-değiştirme, veya bizimki gibi **kural-tabanlı** yöntemler.
- Sonra kuralı basit tutarlar: *"boğada trende gir; nötrde küçült/nakit; ayıda korun veya ters oyna."*

**Biz bunu zaten yapıyoruz** — F10 rejim beyni (BTC haftalık + günlük yapıdan SEZON×HAVA çıkarıp TAM_BOĞA / TEPKİ_RALLİSİ / AYI / BELİRSİZ etiketliyor). Yani senin "parametreleri değiştirmek gerekiyor" dediğin şey = **rejim değiştirme = doğru ve normal tasarım.** Eksik olan, "boğa" etiketi geldiğinde çalışacak bir **boğa stratejisinin** henüz kurulmamış olması.

---

## 3. "Her koşulda kazanan" = tek bot değil, PORTFÖY

Araştırmanın en net mesajı şu: profesyoneller **tek sistem değil, düşük-korelasyonlu strateji PORTFÖYÜ** çalıştırır.

- Buna yatırımın **"tek bedava öğle yemeği"** deniyor: birbirinden bağımsız (biri kaybederken öteki kazanan) stratejileri birleştirince, toplam risk parçaların toplamından **düşük** olur.
- Çarpıcı örnek: tek başına her biri **%40 düşüş** yaşayan 3 strateji, düşüşleri **aynı anda olmadığı** için birleştiğinde portföy **%5 düşüşü** bile geçmeyebilir. Düşük korelasyonun satın aldığı şey budur — dengeli, sarsıntısız getiri.
- Farklı stratejiler döngünün farklı anlarında parlar: yüksek-oynaklıkta istatistiksel arbitraj, trendde trend-takip, yatayda fade...

**Ama dürüst uyarı:** gerçek çok-stratejili fonlar devasa kaynak ister (Citadel 400+ kişi). Retail için gerçekçi versiyon: **2-3 basit ama farklı-rejim stratejisi** (örn. fade + trend) + hangisinin aktif olacağını seçen bir rejim anahtarı. Bu, "her koşulda kazanan"ın ulaşılabilir hali.

---

## 4. Kazanan bir sistemin gerçek bileşenleri

Strateji, bir sistemin sadece 1/4'ü. Araştırmaya göre asıl belirleyiciler:

**1) EDGE (pozitif beklenti) — matematiksel avantaj**
- Formül: **Beklenti = (kazanma% × ort. kazanç) − (kayıp% × ort. kayıp)**, ve bu **maliyetler düşüldükten sonra** artı olmalı.
- Artıysa edge'in var; değilse ne kadar iyi çalıştırırsan çalıştır kaybedersin. (Bizim K2-b fade ölçümü +%2.22 = pozitif beklenti kanıtı.)

**2) RİSK YÖNETİMİ — asıl hayatta kalma sanatı**
- En yaygın yöntem: her işlemde sermayenin **sabit %1-2'sini** riske at (bakiye büyüyünce büyür, küçülünce küçülür — kayıp serilerinde otomatik koruma).
- Kilit cümle: *"Risk yönetimi güvende hissetmek değil; edge'in çalışması için yeterince uzun **hayatta kalmak.**"*
- "Mükemmel sistem + kötü risk yönetimi" batar; "vasat sistem + mükemmel risk yönetimi" kazanabilir.
- (Bizde: işlem başına %5 tavan + stop hep likidasyondan önce — bu doğru omurga.)

**3) DİSİPLİN — botların en sık ölüm sebebi**
- Araştırma açık: botları en çok **insan müdahalesi** öldürüyor — düşüşte paniğe kapılıp kapatmak, dürtüyle parametre değiştirmek, kayıp serisinden sonra strateji atlamak. Bunlar sistematiğin tüm avantajını yok eder.
- (Bizim "onaysız değişiklik yok, eski kriteri silme, sonucu görünce eşik oynatma" disiplinimiz tam bunun panzehiri.)

**4) DÜRÜST TEST** — aşağıda ayrı bölüm.

---

## 5. Nasıl test edilir — kendini kandırmadan

Retail'in **1 numaralı ölüm sebebi: overfitting** (botun geçmişe aşırı uydurulması). Sonuç: backtest harika görünür, canlıda berbat olur. Doğru test bunu engeller:

- **Walk-forward (ileriye-doğru) — altın standart:** stratejiyi bir dönemde ayarla, sonra **botun hiç görmediği** bir sonraki dönemde test et; pencereyi kaydır, tekrarla. Tek bir "şanslı" dönemin yanıltmasını engeller.
- **Out-of-sample:** verinin ~%30'unu teste ayır, ayarlarken hiç dokunma.
- **Çoklu rejim:** en az birkaç yıl (ideal ~10) veri; **hem boğa hem ayı** içermeli. (Bizim en büyük eksiğimiz: elimizde gerçek boğa verisi yok — o yüzden boğa-tarafı hâlâ kanıtsız.)
- **Hipotez önce gelir:** "bu neden çalışıyor" diye mantıklı bir sebep olmalı. Sadece backtest'e dayanıp mantığı yoksa = kırmızı bayrak. (Biz her ölçümü **ön-kayıtlı hipotezle** yapıyoruz — bu doğru yöntem.)
- **Parametre sağlamlığı:** eşiği ±%10 oynatınca edge hayatta kalmalı; bir tek sihirli sayıya bağlıysa sahtedir.
- **Monte Carlo:** işlem sırasını rastgele karıştırıp equity eğrisi ne kadar kırılgan, görür.
- **Sanal/kağıt test:** canlı paraya geçmeden önce. (Bizim testbot tam bu.)

**Not:** biz bu listenin çoğunu zaten uyguluyoruz — ön-kayıt, kontrol grubu, maliyet düşme, N-uyarıları, sanal test. Retail'in ezici çoğunluğu bunları atlıyor; bu bizim sessiz avantajımız.

---

## 6. Acı gerçekler (kimsenin satmadığı taraf)

- **Retail botların %80'inden fazlası para kaybeder.** Bir üniversite çalışması: incelenen platformlarda botlar kullanıcı başına insan trader'dan **77 kat fazla** kaybettirmiş.
- **"AI bot" pazarlamasının ~%95'i** aslında kural-tabanlı script + üstüne "AI" etiketi. Sihir yok.
- **Maliyet + slipaj**, kağıtta kârlı görüneni canlıda sıfırlar. (Bizim düşük-mcap slipaj tartışması tam buydu — $3M'lik coinde %0.02 varsayımı yalan söyler.)
- **Holy grail yok:** mütevazı-ama-gerçek bir edge + iyi risk yönetimi, "mükemmel görünen ama overfit" bir sistemden **her zaman** iyidir.

Bu bölümün amacı seni caydırmak değil — **beklentiyi gerçeğe oturtmak.** "Her ay %X garanti kazanan bot" arayan herkes dolandırıldı. Gerçekçi hedef: pozitif beklentili, hayatta kalan, disiplinli bir sistem.

---

## 7. Bizim bot bu tabloda nerede + akılcı yol haritası

**Neredeyiz (güçlü yanlar):**
- Kanıtlı bir **fade/ortalamaya-dönüş** stratejisi (ayı/yatayda çalışıyor).
- Bir **rejim beyni** (F10) — profesyonellerin yaptığı şeyin kural-tabanlı hali.
- **Dürüst test disiplini** (ön-kayıt, kontrol, sanal test) — retail'in %80'inin atladığı şey.
- **Risk omurgası** (işlem başına tavan, stop-önce-likidasyon).

**Eksik olan:** "boğa bacağı." Şu an tek stratejili, tek-yönlü bir sistemiz. Boğa gelince kazanacak ikinci bir strateji yok — sadece "zarar etme" moduna geçiyoruz.

**Kazanan sisteme iki rasyonel yol:**

**A) PORTFÖY yolu (önerilen, "her koşulda kazanan"ın gerçek hali):**
Mevcut fade botunun yanına **ayrı bir trend/boğa botu** kur. Rejim beyni (F10) hangisinin aktif olacağını seçer:
- TAM_BOĞA → trend botu açık, fade kapalı.
- AYI/yatay → fade botu açık, trend kapalı.
İki düşük-korelasyonlu strateji = daha dengeli, daha az sarsıntılı equity. Bu, retail'in ulaşabileceği "all-weather".

**B) Tek bot, güçlü rejim-anahtarı:**
Tek sistem ama rejime göre **komple mod değiştiren** (fade-modu / trend-modu). Senin "boğada parametreleri değiştir" içgüdün birebir bu. A'dan daha basit ama daha az esnek.

**Her iki yol da aynı eksik adımı gerektiriyor:** bir **boğa/trend stratejisi kurmak + dürüstçe test etmek.** Ve bunu ancak şöyle yapabiliriz:
- Ya **gerçek boğa gelene kadar bekle** (o zaman canlı öğreniriz), 
- Ya da **geçmiş boğa dönemlerinde test et** — BTC'nin 2020-21 ve 2023-24 boğaları elimizde; bir trend-takip stratejisini o dönemlerde walk-forward test edip "boğa bacağı gerçekten kazanıyor mu?" sorusunu **şimdi** cevaplayabiliriz.

---

## 8. Somut sonraki adımlar (sen karar ver)

1. **Boğa-bacağı ölçümü:** basit bir trend-takip kuralını (örn. haftalık trend + geri-çekilmede al) BTC/likit-alt'ların **2023-24 ve 2020-21 boğalarında** walk-forward test et → boğada gerçekten kazanıyor mu, ne kadar?
2. Kazanıyorsa: **fade + trend'i F10 rejim anahtarıyla birleştir** = iki-rejimli portföy (A yolu). Tek-değişken disiplini, sanal.
3. **Risk yönetimini netleştir:** işlem başına sabit %, ve bir **portföy-düşüş limiti** (örn. "toplam %15 düşersen dur ve gözden geçir").
4. Her şey **sanal** akmaya devam eder; sadece çoklu-rejim boyunca pozitif kanıt birikirse mikro-gerçek düşünülür.

**Tek cümlelik özet:** "Her koşulda kazanan tek sihirli bot" bir efsane — ama **rejime göre strateji değiştiren / birden çok strateji taşıyan, gerçek edge'li, sıkı risk yönetimli, dürüst test edilmiş** bir sistem gerçek ve ulaşılabilir. Biz bu iskeletin yarısını (fade + rejim + disiplin) kurduk; kalan yarısı **boğa bacağını kurup test etmek.**

---

## Kaynaklar
- [Algorithmic Trading Strategies — QuantVPS](https://www.quantvps.com/blog/algorithmic-trading-strategies)
- [Key Algorithmic Trading Strategies — Bookmap](https://bookmap.com/blog/key-algorithmic-trading-strategies-from-trend-following-to-mean-reversion-and-beyond)
- [Regime Detection: Measuring Market Regime Shifts — PickMyTrade](https://blog.pickmytrade.trade/regime-detection-measuring-market-regime-shifts-2026/)
- [Hidden Markov Model Market Regimes — QuantifiedStrategies](https://www.quantifiedstrategies.com/hidden-markov-model-market-regimes-how-hmm-detects-market-regimes-in-trading-strategies/)
- [Bull and Bear Regime Trading — Kevin Davey](https://kjtradingsystems.com/bull-bear-regime-trading.html)
- [Walk-Forward Optimization — QuantInsti](https://blog.quantinsti.com/walk-forward-optimization-introduction/)
- [6 Best Practices for Backtesting — GoatFundedTrader](https://www.goatfundedtrader.com/blog/best-practices-for-backtesting-trading-strategies)
- [Why Most Trading Bots Lose Money — ForTraders](https://www.fortraders.com/blog/trading-bots-lose-money)
- [Are AI Crypto Trading Bots Profitable in 2026 — Altrady](https://www.altrady.com/blog/crypto-bots/are-ai-crypto-trading-bots-profitable-2026)
- [Building a Multi-Strategy Portfolio — Man Group](https://www.man.com/insights/building-a-multi-strategy-portfolio)
- [Why Professional Traders Run Portfolios of Strategies — See It Market](https://www.seeitmarket.com/why-professional-traders-run-portfolios-of-strategies-not-one-system/)
- [Trading Expectancy — JournalPlus](https://journalplus.co/blog/trading-expectancy-formula/)
- [Trading Risk Management & Position Sizing — QuantVPS](https://www.quantvps.com/blog/trading-risk-management)
