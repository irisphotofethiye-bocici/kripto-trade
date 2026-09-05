# kripto trade — çalışma kuralları

Bu dosya her oturumda otomatik yüklenir. Amacı, 45 günde pahalıya öğrenilen kuralların
sıkıştırma (compaction) ile kaybolmasını engellemek.

---

## SERT KISITLAR — istisnasız

- 🔴 **BOTA HABER VERMEDEN KARIŞILMAZ** (kullanıcı talimatı, 2026-08-18). Çalışan bota
  ait hiçbir şey — `testbot_state.json` · açık pozisyonlar · defter dosyaları · `.py`
  kodu · zamanlanmış görevler — **önce söylenip onay alınmadan** değiştirilmez.
  Pozisyon elle kapatmak/açmak, stop oynatmak, state düzenlemek bu kapsamdadır.
  **Kapsam dışı:** salt-okuma, ölçüm betikleri, `.md` belgeler.
  **Neden bu kadar sert:** (1) ölçüm penceresi beş kararın hakemi — içine elle müdahale
  girerse hakem kalmaz; (2) `CLAUDE.md` zaten *"ölçüm bota dokunmaz"* diyordu ama o kural
  ölçüm süreçleri içindi, **elle karar** için ayrıca yazılması gerekti.
- **Bot KÂĞIT ÜSTÜNDE çalışır.** Gerçek emir gönderen kod YOKTUR ve eklenmez.
- **İzinsiz `git push` YOK.** ~~Depo bugüne kadar hiç push edilmedi. İlk push'tan
  **önce** git geçmişi temizlenmeli (geçmişte ~920 MB veri var, `.git` ~242 MB).~~
  **[DEĞİŞTİ 2026-08-25]** Bu iki olgunun **ikisi de yanlışmış**: depo **push
  edilmişti** (ilk push 2026-07-22) ve **geçmiş zaten temizdi** — `.git` on'lu MB
  mertebesinde, en büyük nesne bir MB'ın altında, `kripto-config.json` ve
  `kripto_portfoy.json` geçmişte **0 commit**. Yani *"ilk push'tan önce temizle"*
  koşulu **karşılanmış durumda** — engel kalmadı.
  **Kuralın kendisi aynen geçerli: onaysız push YOK.**
  ⚠️ **Buraya commit hash'i ya da tarih YAZMA** — bu satır bir kez bayatladı
  (`169c24a` yazıldı, aynı gün push'la geçersizleşti). Değer değil, **komut**:

  ```
  git fetch --all                                   # once uzagi tazele
  git log -1 --format='%h %cd' origin/main          # uzagin GERCEK ucu
  git rev-list --left-right --count origin/main...HEAD   # sag = push edilmemis
  du -sh .git
  git log --all --oneline -- kripto-config.json | wc -l  # 0 beklenir
  ```

  ⚠️ `origin/main` bir **yerel önbellektir** — `git fetch` yapılmadan okunan değer
  uzağın gerçek durumu değildir. Uzakla ilgili hüküm yazmadan önce **daima fetch**.
  ⚠️ **Push tarihini reflog'dan çıkarma.** Dal reflog'ları bir kez boş bulundu
  (`.git/logs/refs/heads/main` 0 satır); o durumda elde yalnız *commit* tarihi olur,
  push o an ya da **sonrasındadır**. İkisi aynı şey değildir.
- **`kripto-config.json` ve `kripto_portfoy.json` asla commit edilmez.** İçlerinde
  CoinGecko/Telegram/Apify/Coinalyze anahtarları var. `.gitignore`'da kalırlar.
- **`.gitignore`'a satır-içi yorum yazma.** Kalıbı bozuyor (`dosya.json  # not` çalışmaz).
- **Geri alınamaz / dışa açılan adımlar önce onaya sunulur.** Ücretli çağrı, push,
  paylaşım, silme.

## YÖNTEM — ölçmeden kural çıkarılmaz

- **Ön-kayıt koşturmadan ÖNCE yazılır ve commit edilir.** Hipotez + geçme ölçütü +
  beklenti. Sonucu gördükten sonra ölçüt değiştirilmez.
- **Kontrol grubu zorunlu.** "Kural kârlı" yetmez; kontrolü geçmeli.
- **Fonlama (funding) maliyeti dahil edilir.** A+B kapısında kenarın **%83'ünü**
  fonlama yedi; hariç tutulan her ölçüm yanıltıcıdır.
- **En iyi hücre seçilmez.** Tabloya bakıp en yüksek sayıyı kural yapmak bu projede
  reddedilmiş bir davranıştır (bkz. erken müdahale, `olcumler.md`).
- **Çoklu karşılaştırma sayılır.** Çok sütun + az satır = sahte bulgu garantisi.
- **SİNYAL, MEKANİKTEN ARINIK ÖLÇÜLÜR — ölçüm sırası şudur:**

  ```
  ham ileri getiri  →  ticaret mekaniği  →  portföy simülasyonu
  ```

  Aksi hâlde **bizim stopumuzun öldürdüğü bir kenarı "sinyal boş" diye kaydederiz.**
  Bu hata gerçekten yapıldı (`kanal-stochrsi-analizi.md` 12.5 → 13. bölümde
  düzeltildi). **İki bağımsız ölçüm aynı derse çıktı:** kanal/StochRSI'de ham sinyal
  +0,243 vs kontrol +0,035 (t=+3,84) iken A-stop'la +0,051'e iniyordu; ölü sinyal
  taramasında A-stop **A+B'nin ham kenarının %65'ini** yiyordu — MA50+ucuz'da %0.
  Bir kapı "çalışmıyor" derken **kapının mı, stopun mu** çalışmadığı ayrılmalı.
- 🔴 **AMA TERSİ DE TUZAK: "stopsuz kıyas" SÜREYİ de değiştirir — ÜÇ KEZ ısırdı.**
  Yukarıdaki kural *"mekanikten arınık ölç"* der ve bu **stopsuz kolu sabit ufukta
  tutmak** diye uygulandı. Yanlış: stoplu kol **erken çıkar**, stopsuz kol ufkun
  sonuna kadar durur. Fark *"stopun zararı"* değil, **stop + süre karışımıdır.**
  **Vakalar:** (1) *"A-stop A+B'nin ham kenarının %65'ini yedi"* — asimetrisi 2 yıllık
  veride yeniden üretilemedi; (2) *"farkı yiyen şey stop mekaniği"* betimlemesi —
  ufuk eşleştirilince **işaret döndü**, stop yardım ediyordu; (3) kanal/StochRSI'de
  aynı desen. İlk ikisi haftalarca *"stopumuz kenarı yiyor"* anlatısını besledi.
  **Doğrusu — ikisinden biri:** (a) **eşleşmiş süre** — stopsuz kolu, stoplu kolun
  *kendi gerçekleşen tutma süresi* kadar tut (`stop_mu_sure_mu.py` deseni); ya da
  (b) **eşleşmiş giriş, farklı genişlik** — her kolun kendi stopu olsun, hiçbiri
  stopsuz olmasın (`stop_mesafesi.py` deseni). **Sabit ufuk + stopsuz kol = teşhis
  aracı bile değil.** Ayrıntı ve sayılar `olcumler.md`.
- 🔴 **KURAL İHLAL EDİLDİ (2026-08-20) — "mekanikten arınık ölç" yetmiyor, ARANACAK
  BİR SINAMA gerek.** Yukarıdaki sıra kuralı yazılıydı ve yine atlandı: `chg24` bant
  ölçümleri doğrudan A-stop + %10 hedefle yapıldı, ham getiri hiç bakılmadı. Sonuç:
  `>40 LONG` hücresi **"gürültü, öldü" diye gömüldü** — ham getiride **+2,284**,
  takip eden stopla **+2,379 (t=+3,24, 15 ayın 12'si)**. Ölen sinyal değil, stopumuzdu.
  **Somut sınama — hüküm yazmadan önce koştur:** karşılaştırdığın hücrelerde
  *stop genişliği* ve *stop-olma oranı* eşit mi? Ölçüldü, DEĞİL:

  | bant | stop genişliği | ATR/fiyat | stop olma |
  |---|---|---|---|
  | `-40..0` | %2,86 | %2,50 | %73,1 |
  | `0..20` | %2,86 | %2,13 | %76,5 |
  | `20..40` | %5,88 | %4,27 | %61,8 |
  | `>40` | %9,31 | %6,50 | %50,1 |

  Stop genişliği **3,3 kat** değişiyor. *"Mekanik her hücrede aynı, sıralamayı
  bozmaz"* savunması bu tabloyla **çöker**. Kural: **hücreler oynaklıkta ayrışıyorsa
  ham getiri ZORUNLU**; ayrışmıyorsa mekanikli ölçüm tek başına yeter.
  ⚠️ Ayrıca **güven de şişiyor**: `0..20 LONG` ham t=−0,90 iken A-stop'la t=−4,11.
  Stop varyansı kırdığı için anlamlılık büyüyor — **yön aynı, güven yalan.**
  Bu proje doğru yöntemi zaten uygulamıştı (pump kapısı notu: *"ham fiyat"*,
  [testbot.py:418](testbot.py#L418)); eksik olan disiplin değil, **sınamaydı.**
- 🔴 **KARIŞTIRICI KONTROLÜ ZORUNLU — monotonluk tek başına YETMEZ.** Bir sinyal
  ön-kayıtlı kapıları geçse ve dilimleri **mükemmel sıralı** çıksa bile, *"aynı fiyat
  hareketi içinde de ayırıyor mu"* sorusu sorulmadan hüküm yazılmaz.
  **Bu proje bunu iki kez yaşadı:** agresör dengesi (2026-08-17, üç kapıyı geçti,
  ilk-saat getirisi sabitlenince işaret döndü) ve *son yeni uç* (2026-08-19, 11,8 puanlık
  monotonik yayılım kâr sabitlenince 2-4 puana indi ve işaret bantlar arasında döndü).
- 🔴 **ÖLÇTÜĞÜMÜZ HER ŞEY TEK BANTTAN TÜRÜYOR — "yeni sinyal" çoğu zaman aynı şeydir.**
  Fiyat · hacim · işlem sayısı · taker oranı · OI · oynaklık · sıkışma: hepsi
  **Binance perp'te gerçekleşmiş işlemden** çıkıyor. O yüzden her yeni aday
  *"erken fiyat hareketinin başka bir ifadesi"* çıkıyor. **Dizi** özelliği sanmak da
  kurtarmadı (2026-08-19). Gerçekten yeni bilgi **bandın dışındadır**: emir defterinde
  bekleyen likidite · spot-perp basis · çapraz borsa · pozisyon kompozisyonu.

  **[GÜNCEL 2026-09-05] Dördünün karnesi — üçü ölçüldü, üçü de DÜŞTÜ:**

  | aday | hüküm | not |
  |---|---|---|
  | pozisyon kompozisyonu (`top_ls − glob_ls`) | ❌ bulgu yok | ⚠️ **temiz ayrıştırma HİÇ yapılmadı** — `topLongShortAccountRatio` arşivlenmemişti, artık 2 yıl geriye var |
  | spot-perp basis | ❌ DÜŞTÜ 5/5 | rho −0,0152 · taban 0,020 · etki sönüyor |
  | çapraz borsa (Binance−Bybit fonlama) | ❌ DÜŞTÜ | rho **+0,0108** — ve **işaret hipotezin TERSİ** |
  | **bekleyen likidite (OBI)** | ❌ **DÜŞTÜ 2026-09-06** | rho **−0,0077 · t −0,88** — sıfırdan ayırt edilemiyor |

  🔑 **LİSTE KAPANDI: üç aday, üçü de düştü.** İlk ikisi en azından `t>4`
  veriyordu (*"yön aynı, güven yalan"*); OBI onu bile vermedi.

  🔴 **VE UFUK MERDİVENİ BİR AÇIKLAMAYI ÇÜRÜTTÜ.** OBI ölçümü `+5dk · +30dk ·
  +1s · +4s · +24s` basamaklarının **beşinde de** sıfır verdi. Yani
  *"mikroyapı sinyali var ama bot 7,5 dk turla çok yavaş"* savunması **artık
  kullanılamaz** — o ufukta da bir şey yok. Yeni bir hızlı-sinyal önerisi bu
  ölçüme karşı savunma yapmak zorundadır.

  ⚠️ Geriye denenmemiş **tek** şey kaldı: pozisyon kompozisyonunun **temiz**
  ayrıştırması (`topPosition/topAccount`) — `metrics` arşivi sayesinde artık
  2 yıl geriye mümkün.

  🔴 **BEKLEYEN LİKİDİTE — "ölçüldü" SANILMASIN, ölçülen şey BÜYÜKLÜKTÜ.**
  Kaydedilen `defter_usdt_20` yalnız **yediğimiz tarafın** toplamıdır ve dolar
  cinsinden **tam sıfır** taşıyor (`r=−0,003 · t=−0,15`; sembol içinde `+0,022`).
  Skorun düşme sebebiyle **aynı**: büyüklük ölçüyor, yön ölçmüyor. Emir defterinin
  yön taşıyan büyüklüğü **DENGESİZLİKTİR** (alış vs satış) ve o hiç kaydedilmedi.
  ⚠️ **[DEĞİŞTİ 2026-09-05]** *"emir defteri geçmişi YOK → yalnız ileriye"* kaydı
  **yanlışmış**: `data.binance.vision` → `daily/bookDepth` **iki tarafı da**
  (±%1…±%5, ~30 sn'de bir, **900+ gün geriye**) yayınlıyor. Geriye test **mümkün**.
  Boyut: ~0,5 MB/sembol/gün → kapsam ölçümden önce sınırlandırılmalı.
- ⚠️ **`SEYRELT=24` FAZ KİLİTLER — zamanla ilgili her ölçümde faz kaydır.**
  `klines_1h_uzun` dosyalarının hepsi aynı damgayla indirildi; 24 barlık adım her
  sembolde girişleri **aynı UTC saatine** düşürüyor. Fonlama-saati taramasında bir kova
  örneklemin **%62'sini** taşıdı. Saat boyutu olmayan sorularda zararsız.
- ⚠️ **ALT-KÜME testinde `t_küme` TANIMSIZ.** Eşleşmiş testte (aynı girişler, farklı
  çıkış) farkın t'si hesaplanır. Kural kolu kontrolün **alt kümesiyse** eşleşmiş fark
  yoktur; raporlanan t her kolun **mutlak** getirisinin t'sidir, *"fark anlamlı mı"*nın
  cevabı değildir. **Alt-küme ön-kayıtlarında iki-örneklemli istatistik belirtilir.**
- **BUG İSTİSNASI — ölçüm penceresi açıkken neyin değişebileceğinin ölçütü**
  (`test-degerlendirme-programi.md` D/8): tek soru şudur — *"bu değişiklik botun hangi
  işlemi açacağını değiştiriyor mu?"* Değiştirmiyorsa (tasarlanmış davranışı geri getiren
  onarım) serbest. Değiştiriyorsa pencere ya beklenir ya yeniden başlatılır.
- **DEĞİŞİKLİK PROTOKOLÜ** (D/9): eski ölçüt **silinmez**; yanına `[DEĞİŞTİ tarih]`
  eklenir. Kriter metni yorumlanmaz, sayı eşiği uygulanır. **Şüphede DAİMA statüko.**
- **Başarısızlık aynen raporlanır.** Çıkış tarafında **30 varyant** denendi, **1'i**
  geçti (`olcumler.md` → sayım). Bunu yumuşatmak da şişirmek de projenin değerini
  yok eder. ⚠️ **Bu sayı BÜYÜYOR — tekrarlamadan önce `olcumler.md`'den oku.**
- **Tekrarlayan bulgu — keskin hâli:** geçen tek varyant çıkışı **gevşetiyordu**
  (sabit %10 hedef). Çıkışı **sıkılaştıran 29 varyantın 29'u da kaldı.**
  Yeni bir çıkış kuralı önerirken önce buna bak: sıkılaştırma öneriyorsan
  **29/29**'a karşı savunma yapman gerekiyor.
  ⚠️ **[DEĞİŞTİ 2026-08-31]** Burada aylarca `28/28` yazıyordu ve **bayatlamıştı**;
  30. varyant (30. dakikada kesme) 2026-08-30'da düştü. Aynı gün ben de iki ayrı
  dosyaya `28/28` yazdım — **kaynağa bakmadan.** Bu, projenin kendi
  *"sayı tekrarlanmaz, sayılır"* kuralının ihlaliydi.
- **BİR SAPMAYI AÇIKLAYAN FORMÜL BULUNDUĞUNDA, İKİNCİ BİR ZAMANDA SINANMADAN HÜKÜM
  YAZILMAZ.** Tek noktaya uyan formül *"donmuş kayma"* ile *"büyüyen hata"*yı
  **ayırt edemez** — ikisi de o tek noktada aynı sayıyı verir. Gerçek vaka: `ayna`'nın
  177,84 $ farkı için 08-12 temizliğine dayanan bir açıklama bulundu, tuttuğu için
  *"kalıcı kayma, süregelen hata değil"* diye yazıldı. Commit commit ölçülünce fark
  08-13'te **−0,01** çıktı, yani açıklama yanlıştı: hata 08-14'te doğmuş ve
  **büyüyordu**. Doğru hamle formülü bulmak değil, **farkı birkaç zamanda ölçmekti.**
- 🔴 **ORTAK PAYDALI ORAN, SAHTE KORELASYON URETIR — bu proje iki turda iki kez ısırıldı.**
  `ret = net/notional` ve `R = net/risk` gibi büyüklüklerde payda **hem ölçtüğün
  değişken hem de normalleştiricidir**. `notional ~ ret` ya da `risk ~ R`
  korelasyonu bu yüzden **mekanik olarak** çıkar; piyasa hakkında hiçbir şey
  söylemez. **Somut vaka:** boyutlandırma ölçümünde `notional ~ ret = −0,30`
  bulundu ve "büyük pozisyonlar kaybediyor" diye yorumlandı; oysa kod
  `notional ≈ hedef_risk/stop_frac` diyor, yani `|ret| ∝ 1/notional`
  **tanım gereği**.
  **Kural:** boyutla ilgili bir iddia yazmadan önce sor — *"bu büyüklüğün
  paydasında, karşılaştırdığım değişken var mı?"* Varsa o korelasyon
  **dayanak olamaz**. Güvenli olan tek şey **boyuttan bağımsız büyüklüğün
  kendi toplamı/ortalamasıdır** (`ΣR`), korelasyonu değil.
- 🔴 **"NEDENSEL YOLUN UZERINDE" DEMEDEN ONCE YOLUN VAR OLDUGUNU GOSTER.**
  Bir ön-kayıta *"TP1'e koşullamak aşırı kontrol olur, çünkü TP1 nedensel yolun
  üzerinde"* yazıldı ve **yanlıştı**: kâğıt defterde pozisyon boyutu fiyatı
  etkilemez, dolayısıyla boyut→TP1 yolu **hiç yoktu**. TP1 ile boyutun
  **ortak nedeni** vardı (stop mesafesi). Aşırı kontrol savunması ancak
  yol **gösterilebiliyorsa** geçerlidir.
- **Sayı tekrarlanmaz, sayılır.** "13 çıkış kuralı denendi" cümlesi bu projede
  aylarca tekrarlandı ve **dayanağı yoktu**; kütük doldurulunca gerçek sayım
  ortaya çıktı. Bir rakamı ikinci kez söylemeden önce kaynağını göster.

## MİMARİ TUZAKLAR — üçü de gerçekten ısırdı

- **`yeni_giris_ac` dört defter tarafından çağrılır** (`testbot`, `golge`, `benim`,
  `ayna`). Bu fonksiyona yan etki (bildirim, aynalama, log) eklerken
  **`_DEFTER is not None` koruması şart.** Bu hata sınıfı **üç kez** yaşandı:
  ayna sızıntısı · Telegram'dan sahte giriş mesajı · gölge girişlerinin aynaya düşmesi.
- **Durum dosyaları ATOMİK yazılır** (`.tmp` + `os.replace`). Gölge defterin düz
  `json.dump`'ı 2026-08-11'de defteri **314 $** saptırdı.
  ⚠️ **`golge.py` bu kurala HÂLÂ uymuyor** → `durum.md` madde 4.
- **Ölçüm bota dokunmaz.** Ayrı süreç, ayrı dosya, salt-okunur. `testbot._DEFTER`
  ile oynanmaz.
- **Etkin kasa ≠ realize kasa.** Açık pozisyon varken yalnız `equity`'ye bakmak
  yanlış sonuç verir; bu hata **iki kez** yapıldı (fren hatası + ayna kıyası).
- **Kazanma oranı POZİSYON başına sayılır, kayıt başına değil.** Kısmi kâr kayıtları
  pozisyonu böler. **Somut tuzak:** ölçüm penceresinde kayıt sayısı pozisyon sayısından
  belirgin fazladır — fark **45–50 kayıt** mertebesinde, çünkü `TP1_KISMI` satırları
  pozisyonu ikiye bölüyor. Kayıt sayan biri pencereyi **vaktinden önce dolmuş** ilan
  eder. Güncel sayım komutu `durum.md`'de.
- 🔴 **`r` ALANI KISMİ KÂRI GÖRMEZ — R ile dolar ters işaret verebilir.** `r` yalnız
  kapanış kaydında var ve **kalan yarının** R'sini gösterir; TP1'de realize edilen kâr
  onun içinde YOK. Somut: `BAS` toplam **+13,36 $** ama `r = −0,51`. Yarı-yarı kıyas
  R üzerinden yapılırsa kısmi kâr alan pozisyonlar sistematik olarak **kötü** görünür.
  **Pozisyon-bazlı toplam ile kayıt-bazlı R aynı şeyi ölçmez** — hangisinin
  kullanılacağı hüküm yazılmadan ÖNCE kararlaştırılır (`durum.md` → pencere).
- 🔴 **SÜZGEÇ SAYMAK İÇİNDİR, TOPLAMAK İÇİN DEĞİL.** Pozisyon *sayarken*
  `not x.get("kismi")` uygulanır. **P&L *toplarken* UYGULANMAZ** — kayıtlar `id` ile
  birleştirilir, yoksa TP1'de **realize edilmiş kâr kaybolur.** Ölçüldü
  *(2026-08-17 anlık görüntüsü — rakamlar drift eder, hata BÜYÜKLÜĞÜ kanıt olarak
  duruyor)*: `golge` gerçek −1.350,72 iken süzgeçli hâli −5.815,70 → **~4.465 $ hata**;
  `testbot`'ta **~2.855 $**. Süzgeç bu projede zaten bir kez yanlış toplam üretti.
- **MUTABAKAT DENKLEMİ — hangi yöntemi kullanırsan kullan, bunu tutturmuyorsa yanlıştır:**

  ```
  başlangıç bakiye + Σ P&L + funding − giriş ücreti (+ kasa sıfırlaması) ≈ equity
  ```

  Doğru yöntemde sapma **kuruş** mertebesinde çıkıyor (`golge` −0,07 · `testbot` −0,04).
  Süzgeçli yöntemde **binlerce dolar** sapıyor. Bir P&L toplamı yazmadan önce bu
  denklem koşturulur.
- **İKİ AYRI TABAN VAR; karıştırmak üç kez yanlış sayı ürettirdi.** *Muhasebe tabanı*
  (kasa hangi bota ait) ile *hakem penceresi tabanı* (parametrelerin sabit kaldığı an)
  farklı sorulardır. Defter tutarsız değildi — iki doğru cevabı tek soru sanmıştı.
  **Sayı üretmeden önce `durum.md`'nin pencere bölümünü oku**; tarihler, sayım komutu
  ve hangi tabanın hangi soruya ait olduğu orada. Buraya tarih ya da rakam yazma.
  ⚠️ Sayarken **"kapanan" değil "açılıp kapanan"** ayrımına dikkat: bir taban
  seçilirken *"botun KENDİ işlemi"* denmişse bu **girişi de o pencerede olan**
  pozisyon demektir. Bu ayrımı atlamak kaydedilmiş bir çelişki üretti.
- **`radar_archive.jsonl` NOKTASAL veridir — kayıp kareler geri gelmez.** Bu arşivle
  ölçüm yaparken `radar_bosluk.jsonl` de okunur (2026-08-17'den beri işaretleniyor);
  yoksa eksik pencerede çalışıldığı fark edilmez. Oranlar `olcumler.md`'de.
  **Arşive yeni tip kayıt KARIŞTIRILMAZ** — 6 çözümleyici okuyor, karıştırılırsa
  onunla yapılmış tüm eski ölçümler geriye dönük geçersizleşir (`testbot.py:267`).
- 🔴 **İKİ SINIF VERİ VAR: KALICI ve 30 GÜNLÜK. Karıştırmak KALICI KAYIP üretti.**
  Binance iki farklı uç sınıfı sunuyor ve ikisi aynı `fapi` altında duruyor:

  | sınıf | uçlar | geçmiş |
  |---|---|---|
  | **kalıcı** | `/fapi/v1/klines` · `/fapi/v1/fundingRate` | istendiği an 2 yıl geriye |
  | **30 gün** | `/futures/data/openInterestHist` · `topLongShortPositionRatio` · `globalLongShortAccountRatio` · `takerlongshortRatio` | **yalnız 30 gün** (ölçüldü: 29g → N=500, 31g → HTTP 400) |

  ~~İkinci sınıf **çekilemez, ancak ARŞİVLENİR.** *"Hepsini indiririz"* bu sınıf için
  yanlıştır: o veri yalnızca **o an kaydediyorsan** vardır. `radar_archive` için
  yazılı olan *"noktasal veridir, kayıp kareler geri gelmez"* kuralı **aynen
  `perp_seri` için de geçerlidir.**~~

  🔴 **[DEĞİŞTİ 2026-09-05] BU YANLIŞMIŞ — "30 günlük" sınıf ARŞİVDE 2+ YIL GERİYE VAR.**
  `data.binance.vision` günlük **`metrics`** dosyaları bu dört ucun **ta kendisini**
  taşıyor. Belirleyici sınama koşuldu (`scratchpad/arsiv_30gun_kaniti.py`): arşiv
  dosyası canlı uçla **damga 5 dk kaydırılınca 5/5 alanda birebir** uyuşuyor
  (`sum_open_interest` bağıl hata **0e+00**). Kapsam **2023-09**'a kadar (1100 gün),
  sembol-gün başına ~11 kB.

  ```
  data/futures/um/daily/metrics/<SYM>/<SYM>-metrics-<YYYY-MM-DD>.zip
    create_time · sum_open_interest · sum_open_interest_value
    count_toptrader_long_short_ratio   <- topLongShortAccountRatio (hic arsivlenmemisti)
    sum_toptrader_long_short_ratio     <- topLongShortPositionRatio
    count_long_short_ratio             <- globalLongShortAccountRatio
    sum_taker_long_short_vol_ratio     <- takerlongshortRatio
  ⚠️ create_time = canli ucun damgasi − 5 dk. Join'den ONCE kaydir.
  ```

  **Sonuçları:** (1) 30–60 günle sınırlı kalmış her `perp_seri` ölçümü **2 yıla
  genişletilebilir**; (2) `topLongShortAccountRatio` ile *temiz* pozisyon-kompozisyonu
  ayrıştırması artık mümkün; (3) `KriptoPerpSeri` görevi **kritik değil** (zararsız,
  ama kaybı telafi edilebilir).
  ⚠️ **`radar_archive` için kural AYNEN GEÇERLİ** — o bizim ürettiğimiz skor/karar
  verisidir, Binance yayınlamaz.
  ⚠️ ~~**`perp_seri_indir.py` ZAMANLANMIŞ GÖREV DEĞİLDİR** — elle koşulan kurtarma
  betiğidir.~~ **[DEĞİŞTİ 2026-08-25]** Artık zamanlanmış görev **VAR**:
  `KriptoPerpSeri`, 2026-08-24'te kurulmuş, her gün **03:30**, son koşum başarılı
  (`LastTaskResult 0`). Yani pencere **büyüyor**, kuyruğundan düşmüyor.
  Eski uyarı, görev **silinir ya da başarısız olursa** yeniden geçerlidir —
  `Get-ScheduledTaskInfo -TaskName KriptoPerpSeri` ile denetlenir.
- 🔴 **YENİDEN İNDİRME ESKİYİ SİLEBİLİR — indiriciler BİRLEŞTİRMELİ, EZMEMELİ.**
  Gerçek kayıp (2026-08-24): `perp_seri_indir.py --bot` 07-26'dan başlayan bir
  pencere istedi; `sembol_indir` var olan dosyayı `os.replace` ile **ezdi**.
  **58 sembolde 07-23…07-26 arası OI/long-short/taker kalıcı olarak gitti**
  (30 günlük pencere oraya artık ulaşmıyor, `perp_seri` git'te takipli değil).
  ⚠️ **[DEĞİŞTİ 2026-09-05] "kalıcı" YANLIŞMIŞ — o dört gün arşivde DURUYOR**
  (yukarıdaki `metrics` maddesi; dördü de tek tek doğrulandı). **Kuralın kendisi
  aynen geçerli:** indirici birleştirmeli, ezmemeli — telafi edilebilir olması
  veri kaybını meşru yapmaz.
  Betikte `_kapsiyor_mu()` vardı ve *"dosya varsa atla"* hatasını çözüyordu — ama
  **ezme** yolunu hiç kapatmıyordu; iki ayrı hata sanılmıştı.
  **Kural:** arşiv dosyasına yazan her indirici (a) var olanı okur, (b) zaman
  damgasına göre birleştirir, (c) **sonuç eskisinden KISAysa hata fırlatır.**
  Onarım `perp_seri_indir.py:sembol_indir` içinde; deseni kopyala.
- 🔴 **ALAN ADI DEĞİŞMEDEN ANLAMI DEĞİŞEBİLİR — tarih sınırı olan alanlar var.**
  `radar_archive.jsonl` → `rejim` alanı **2026-07-22'de tanım değiştirdi** (F10
  SEZON×HAVA katmanlaması o gün eklendi, [evren.py:294](evren.py#L294)); öncesi eski
  tek-katmanlı detektör. O tarihi **aşan** hiçbir rejim kırılımı bu alanla yapılmaz —
  rejim BTC mumundan yeniden üretilir. Bu, `funding_gecmis` birim kırılmasıyla **aynı
  hata sınıfı**: iki farklı şey aynı adı taşıyor ve `pyflakes` de `py_compile` de
  göremez. Oranlar ve kırılım `olcumler.md`'de.
  **Grep'lenebilir refleks:** bir alanla uzun pencere bölmeden önce *"bu alanı yazan
  kod bu pencerede değişti mi"* diye `git log -S"<alan>"` koştur.

- **Fonlama pozisyona 2026-08-17'den İTİBAREN atfediliyor.** O tarihten önce açılmış
  pozisyonların fonlaması **geri üretilemez**. Bu olgunun sahibi burasıdır; başka
  dosya kopyalamaz, işaret eder.

  | | |
  |---|---|
  | alan adı | **`funding_usdt`** — işlem defterinde, **dolar** |
  | `null` | **bilinmiyor** (08-17 öncesi açılmış pozisyon) — sıfır DEĞİL |
  | `0.0` | meşru sıfır (fonlama görmemiş pozisyon) |
  | süzgeç | `r.get("funding_usdt") is not None` |
  | toplama | **dilim**dir, kümülatif değil → `id` ile toplanır, `sonuc_usdt` ile aynı muhasebe |

  ⚠️ **`funding` ADI BAŞKA ŞEYDİR — oran (%/8s).** `radar_archive.jsonl` ·
  `testbot_aday_arsiv.jsonl` · `veto_log.jsonl` hep oranı yazar ve A+B kapısı onu
  eşikle karşılaştırır ([testbot.py:426](testbot.py#L426)). İlk planlanan ölçüm
  (kapı × fonlama) bu iki dosyayı **birleştirecek**; oranla doları aynı adla yan yana
  koyan bir join **sessizce yanlış** çıkar. Ad ayrımı bu yüzden var.
- **`sonuc_usdt` FONLAMAYI İÇERMEZ.** `funding_uygula` doğrudan `st["equity"]`'yi
  düşürüyor ([testbot.py:818](testbot.py#L818)). Defter toplamına bakıp "pencere şu kadar
  kazandı" demek projenin en pahalı hatasını tekrarlamaktır. **Pencere sonucu her zaman
  equity üzerinden TÜRETİLİR:**

  ```
  equity farkı − kasa sıfırlaması  =  pencere realize
  pencere realize − defter P&L     =  pencere içi fonlama + ücret
  ```

  **`state`'teki `kumulatif_funding` ve `kumulatif_giris_ucret` PENCEREYE AİT DEĞİL** —
  2026-07-23'ten beri kümülatiftir; pencere maliyeti olarak kullanmak abartır.
  Güncel rakam okunmaz, **hesaplanır** (`durum.md` → pencere bölümü).
- **Tur ORTASINDA yapılan kod değişikliği o turu ETKİLEMEZ.** Python modülü tur
  başında yüklenir; sonraki tur başına kadar eski kod koşar. Yani değişiklikten
  sonra açılan bir pozisyon bile yeni alanı taşımayabilir ve bu **hata gibi görünür**.
  Gerçek vaka: `derinlik_giriste` 23:33:03'te yazıldı, ONG 23:33:49'da açıldı — 46 sn
  sonra, ama alan yok, çünkü o tur **23:28:42'de eski modülle başlamıştı**. Doğru
  davranış. Bir alanın eksikliğini hata saymadan önce **pozisyonun giriş anını değil,
  turun BAŞLANGIÇ anını** kod değişikliğiyle karşılaştır (`testbot_equity.jsonl`).

  ⚠️ **Tuzak İKİ YÖNLÜ çalışır.** Yukarıdaki vaka gerçek bir değişikliği *bozuk*
  gösteriyordu. Tersi de oldu: keep-alive 23:43:56'da yazıldı, 23:43:42'de **başlamış**
  tur 174,5 sn sürdü ve "hızlanma" sanıldı — eski modüldü. Üstelik olağandışı bile
  değildi (keep-alive öncesi 542 turun 186'sı ≤180 sn). **İlgisiz bir iyileşmeyi
  başarı gibi göstermek, gerçek bir iyileşmeyi bozuk göstermekten daha tehlikelidir:**
  ikincisi araştırılır, birincisi kutlanır. Bir ölçümün ilk turunu almadan önce
  `turun başlangıcı = ts − sure_sn` hesabını **her zaman** yap.
- 🔴 **KONTROL-ET-SONRA-YAP (check-then-act) BU PROJEDE BİR HATA SINIFIDIR.**
  Kontrol ile eylem arasında başka bir süreç/iş parçacığı araya girer. **Üç kez** oldu:

  | yer | desen | sonuç |
  |---|---|---|
  | `ayna.kapat` | "açık mı" → **ağ çağrısı** → yaz | aynı pozisyon iki kez kapandı |
  | ilk kilit denemem | `os.path.exists()` → `open(...,"w")` | iki çağıran da kilidi "aldı" |
  | `testbot._kilit_al` | aynısı | henüz ısırmadı (bkz. `olcumler.md` → Bekleyen) |

  **Grep'lenebilir kural — şu ikisi şüphelidir:**
  `os.path.exists(...)` ardından aynı yola yazma · *"hâlâ açık/var mı"* kontrolünden
  **sonra** ağ çağrısı gelmesi.
  **Doğrusu:** ya işletim sistemi düzeyinde tek adım (`os.O_CREAT | os.O_EXCL`), ya da
  kilit altında **yeniden oku + doğrula**. Ağ çağrısı kilidin **dışında** kalır.
  ⚠️ **ATOMİK YAZIM ≠ ATOMİK İŞLEM.** `ayna.kaydet` ilk günden atomikti ve yetmedi;
  bozulan tek yazım değil, oku-değiştir-yaz bütünlüğüydü.
- **Kilit dosyaları süresini ilan eder.** Uzun iş kilidi 4 dakikada bayat sayılırsa
  ikinci süreç kilidi çalar ve iki tur aynı durum üzerinde koşar.
- **`kismi_kar_r = 0` KAPATMA ANLAMINA GELMEZ — TERSİNİ yapar.** SHORT'ta
  `tp_r = giriş − 0×risk = giriş` olur; [testbot.py:888](testbot.py#L888)
  `max(yapısal, tp_r)` girişin kendisini seçer ve **TP1 anında tetiklenir.**
  Doğru kapatma kod tarafında: `tp1_efektif_hesapla` çağrısı
  ([testbot.py:933](testbot.py#L933) her turda, [:1145](testbot.py#L1145) girişte)
  `cikis_modu == "sabit_hedef"` pozisyonlarda atlanır. Ayrıntı `olcumler.md`.

## TEST YAZARKEN

**Sahte veriyle test ederken diske yazan HER yolu stub'la** — "güvenli fiyat seçmek"
yetmez. 2026-08-15'te sahte mum fiyatı `1.0` gerçek stop eşiğine (`0.01`) çarptı ve
`pozisyon_kapat` deftere **7 sahte likidasyon** yazdı. Aynı tuzağa ayna testinde de
düşülmüştü. Stub'lanacaklar: `_append_jsonl` · `_save_state` · `pozisyon_kapat` ·
`pozisyon_liq` · `pozisyon_kismi_tp1` · `telegram_gonder`. Testin sonunda
"diske yazım: YOK" diye **doğrula**.

🔴 **`print()` İÇİNDEKİ EMOJİ ÇIKTI YÖNLENDİRİLİNCE BETİĞİ ÖLDÜRÜR — beş kez ısırdı.**
Windows konsolu **cp1254**; emoji ve varyasyon seçicileri (`⚠️` = U+26A0 + U+FE0F)
bu kodlamada **yok**. Ekrana basarken sorun çıkmaz, `> dosya` ile yönlendirilince
`UnicodeEncodeError` fırlatır ve betik **çöker**. Bir kez uydurma p-değeri de
ürettirdi (çıktı yarıda kesilmişti).
⚠️ **Em-dash (`—`) ve Türkçe harfler cp1254'te VAR** — onlar tehlikeli değil.
Sorun yalnız emoji/varyasyon seçicisi. İlk taramam em-dash'i yanlışlıkla suçladı.
**Disiplinle kapanmadı, ARAÇLA kapatıldı** — her ölçüm betiğinin başına:

```python
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
```

Uygulandı: `poz_yol/40..43` · `fonlama_oku` · `fonlama_denetim` · `perp_seri_indir`
· `son2gun*` · `veri_denetim_2gun`. **Yeni ölçüm betiği bu bloksuz yazılmaz.**
⚠️ Bot dosyalarına (`testbot.py` vb.) EKLENMEDİ — onlar `pythonw` ile koşuyor,
çıktı yönlendirilmiyor, sorun çıkarmıyorlar; dokunmak bota müdahale olurdu.

**`python -m pyflakes *.py` — her kod değişikliğinden sonra, `py_compile`'a EK.**
`py_compile` yalnız sözdizimine bakar; **tanımsız isim** onun için hata değil, çalışma
anında patlar. Bu sınıf **üç kez** ısırdı: `radar.HERE` (modül düzeyinde yoktu — sessizce
hiç çalışmadı), `ayna.time` (import edilmemişti), ve ikisi de `py_compile`'dan geçti.
Doğrulandı: pyflakes ikisini de **isim isim** yakalıyor. Bu sınıf disiplinle değil
**araçla** kapanır. Beklenen çıktı: `undefined name` **sıfır** (bilinen zararsız
uyarılar: kullanılmayan import/değişken, placeholder'sız f-string).

🔴 **AMA PYFLAKES YETMEZ — DÜZENLİ İFADENİN *ANLAMI* İKİSİNE DE GÖRÜNMEZ.**
Betik **heredoc ile** yazıldığında kaçış dizileri sessizce bozulabilir: `\b`
(sınır imi) gerçek **BACKSPACE karakterine (0x08)** dönüştü, kural hiçbir zaman
eşleşmedi, yüzlerce kayıt yanlış sınıflandı — ve `py_compile` DE `pyflakes` DE
**temiz geçti.** `radar.HERE` / `ayna.time` ile aynı sınıf: araç görmüyor.
⚠️ Bu proje heredoc'la **iki kez** ısırıldı (biri `[^"\\]`'yi karakter kümesi
olarak bozdu, biri bu). **Düzenli ifade içeren dosya heredoc'la yazılmaz** —
yazma aracı kullanılır.
**Sınama, sınıflandırma yapan her betikte ZORUNLU:** bilinen girdi → beklenen
etiket listesi; düşerse betik **çalışmayı reddeder**. Ayrıca kalıplarda kontrol
karakteri aranır (`any(ord(c) < 32 for c in rx.pattern)`).
Örnek: `scratchpad/olay_listesi.py → kural_sinamasi()`. Vaka: `olcumler.md`
→ *OLAY KUYRUĞU*.

## ALTI DEFTER — her biri tek değişkeni yalıtır

| defter | soru | dosya |
|---|---|---|
| `testbot` | Bot ne yaptı? (ölçünün temeli) | `testbot.py` |
| `golge` | **İKİ İŞ birden** — aşağıya bak | `golge.py` |
| `benim` | Kararı kullanıcı verseydi? | `benim.py` |
| `ayna` | Bot girsin, çıkışa kullanıcı karar versin | `ayna.py` |
| `defter2` | **Bot yanlış evrende mi avlanıyor?** (2026-08-20) | `defter2.py` |
| `defter3` | **Aynı evren, İKİ YÖN** — kayıp evrenden mi yön kısıtından mı? (2026-08-25) | `defter3.py` |

⚠️ **`defter2` mevcut bota EKLENEMEZ, ayrı olmak ZORUNDA.** Ölçüldü: botun 117
gerçek pozisyonunun **%100'ü** bu yapılandırmadan geçemezdi — çünkü botun iki
giriş kapısı bu evreni **tam olarak dışlıyor** (`A+B` → `funding ≤ −0,05`;
`MA50+ucuz` → `fiyat ≤ $0,07`). Filtreleri bota eklemek onu **hiç işlem
açmaz** hâle getirir. Evren: `fiyat > $0,07` · `funding > −0,05` · `chg24 < %20`
· `btc_pay ≠ UST` · **YALNIZ SHORT**.
🔴 **LONG bilinçli olarak DIŞARIDA:** bu evrende LONG, ölçümün **beş adımının
hepsinde `t < −4`**. "Çift yönlü yapalım" önerisi bu ölçüme karşı savunma
yapmak zorundadır.
Çıkış kuralları **bilinçli olarak testbot ile aynı** — fark yalnız girişten
gelsin diye. Ölçülmüş stop onarımı BURAYA KONMADI; konsaydı fark iki kaynaktan
gelir ve ayrılamazdı.

⚠️ **`defter3` = `defter2` + YÖN.** Evren · çıkış · boyutlandırma **birebir aynı**;
tek fark: `chg24 ≥ 0 → SHORT` (defter2 ile aynı), `chg24 < 0 → LONG` (defter2
burada SHORT açıyor). Böylece `defter3 − defter2` = **yönün etkisi**, ve
`chg24 < 0` alt kümesinde **aynı isimler üzerinde doğrudan yön kıyası** olur.
**Neden:** defter2 yalnız SHORT olduğu için boğa haftasında yapısı gereği
kaybeder — kaybın *evrenden* mi *yön kısıtından* mı geldiği ayrılamıyordu.
🔴 LONG'un bu evrende `t < −4` ile reddedildiği bilinerek kuruldu; **LONG kolunun
kaybetmesi BEKLENİYOR**, "gerçekten kötü" de tam bir cevaptır.
İkisi de **kendi zamanlanmış göreviyle** koşar (`KriptoDefter2` · `KriptoDefter3`,
7dk30sn) — `golge`/`ayna`/`benim` gibi testbot içinden çağrılmazlar; testbot'a
hiçbir değişiklik yapılmadı.

⚠️ **`golge` tek soru yalıtmıyor, iki farklı iş yapıyor** — "reddettiği girişlere
girseydi?" tanımı defterin yalnızca **üçte birini** kapsıyor:

| küme | pay |
|---|---|
| `pump_long_tezi` — hiç denenmemiş bir LONG tezinin canlı testi | ~%68 |
| reddedilen girişler (`stop_cok_dar` · `long_veto` · `blowoff` · `taker_soguma` · `onay_bekle`) | ~%32 |

**Gölge kasasına bakıp "bot iyi eliyor" DENMEZ:** kaybın büyük kısmı `pump_long_tezi`'nden
geliyor, reddedilen girişlerden değil. Ayrıca gölge LONG ağırlıklı olduğu için fonlamayı
**tahsil ediyor**, bot ise ödüyor → **iki kasa doğrudan kıyaslanamaz.** Kırılım
`olcumler.md` → defterler bölümünde.

Uydu defterler `testbot._DEFTER`'i geçici olarak değiştirir ve `finally` ile eski
haline döndürür. Bu deseni bozma.

## BİLGİ NEREDE

| soru | dosya |
|---|---|
| Bunu daha önce ölçtük mü? | **`olcumler.md`** ← önce buraya bak |
| Şu an ne açık, ne bekliyor? | **`durum.md`** |
| O ölçümün gerekçesi neydi? | `fikir-defteri.md` (251 kB, 287 başlık, kronolojik — satır no `olcumler.md`'de) |
| Sistemde hangi hatalar bulundu? | `denetim-raporu.md` (9 bulgu; **durumları `olcumler.md`'de**) |
| Kanal/StochRSI stratejisi ne oldu? | `kanal-stochrsi-analizi.md` (44 KB, 14 bölüm — 1-10 ölçümden ÖNCE yazıldı, hüküm KALDI) |
| "Kazanan bot" nasıl bir şey? | `kazanan-bot-arastirma-raporu.md` — çerçeve dosyası, karar değil; §8.1 (boğa-bacağı ölçümü) **hiç yapılmadı** |
| Faz kapıları ne zaman geçildi? | `faz4-test-gunlugu.md` (tarihsel; o kapı **elle işlem** içindi, bot için değil) |
| Değerlendirme disiplini ne diyor? | `test-degerlendirme-programi.md` — D/8 ve D/9 **hâlâ bağlayıcı** (aşağıda YÖNTEM'de) |
| Kâr tepeden ne kadar geri verildi? | `pnl-tepe-raporu.md` (N=17, gözlem — kural çıkarılmadı) |
| Canlıya geçmeden ne kapanmalı? | `memory/canliya-gecis-kontrol-listesi.md` |
| Bileşenler ne işe yarar? | `README.md` |
| Ölçüm betikleri | `scratchpad/*.py` (59 dosya) |

`fikir-defteri.md` bir **laboratuvar defteridir**; kronolojisi kanıtın kendisidir
("o gün neye inanıyorduk"). Yeniden yapılandırma, konuya bölme, özetleyip kısaltma
**yapılmaz** — yalnızca sonuna eklenir.

## BAKIM KURALI — bu dosyanın işe yaraması buna bağlı

- **Ölçüm bitince** `olcumler.md`'ye bir satır ekle (hipotez · tarih · N · hüküm ·
  betik · defter satırı).
- **Karar alınınca** `durum.md`'yi güncelle — **kararı**, rakamı değil.
- **HIZLI DEĞİŞEN RAKAM DOSYAYA YAZILMAZ.** Kasa, açık pozisyon, PnL, fonlama
  7,5 dakikada bir değişir; yazıldığı an bayatlamaya başlar. `durum.md` bir kez bu
  hatayı yaptı: sabah yazılan rakamlar **aynı gün öğlen** yalan söylüyordu.
  Kural: **kaynağı ve okuma komutunu yaz, değeri yazma.** Bir anlık görüntü
  gerekiyorsa tarihini yanına koy ve "anlık görüntü" olduğunu söyle.
  Canlı rakam sorulunca **her zaman** `testbot_state.json` okunur — hiçbir `.md`
  dosyası canlı kaynak değildir.
- **Yeni bir hata sınıfı ısırınca** buraya "MİMARİ TUZAKLAR"a bir madde ekle.

- **HER OLGUNUN TEK SAHİBİ VAR; diğer dosyalar İŞARET EDER, kopyalamaz.**

  | olgu | tek sahibi |
  |---|---|
  | ölçüm penceresi, kasa, açık pozisyon, bekleyen kararlar | `durum.md` |
  | ölçüm hükümleri, N, betik ve defter satırı | `olcumler.md` |
  | kurallar ve tuzaklar | `CLAUDE.md` — **içinde rakam değil, işaretçi** |

  **Neden bu kural var:** indeks kurulduktan sonra bulunan **20 hatanın çoğu** bu
  sınıftandı — aynı olgu iki dosyada yazılıydı, biri düzeltilip diğeri unutuldu.
  Pencere tabanı, fonlama rakamı, gölge tanımı, pozisyon sayısı, atomik yazma kuralı:
  beşi de iki yerde duruyordu ve beşi de çelişkiye dönüştü.
  Bir olguyu ikinci bir dosyaya yazmak üzereyken **yaz değil, işaret et.**

Güncellenmeyen indeks **yalan söyler** ve hiç olmamasından kötüdür. İki yerde yazılan
indeks ise **kaçınılmaz olarak** yalan söyler.

## İLETİŞİM

Kullanıcı Türkçe yazıyor; yanıtlar Türkçe. Kod içi yorumlar da Türkçe (ASCII'ye
sadık — dosyalar Windows'ta düz kodlamayla açılıyor). Uydurma sayı yok: her rakam
ya dosyadan okunur ya ölçülür.
