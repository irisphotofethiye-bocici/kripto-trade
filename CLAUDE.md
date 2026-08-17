# kripto trade — çalışma kuralları

Bu dosya her oturumda otomatik yüklenir. Amacı, 45 günde pahalıya öğrenilen kuralların
sıkıştırma (compaction) ile kaybolmasını engellemek.

---

## SERT KISITLAR — istisnasız

- **Bot KÂĞIT ÜSTÜNDE çalışır.** Gerçek emir gönderen kod YOKTUR ve eklenmez.
- **İzinsiz `git push` YOK.** Depo bugüne kadar hiç push edilmedi. İlk push'tan
  **önce** git geçmişi temizlenmeli (geçmişte ~920 MB veri var, `.git` ~242 MB).
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
- **BUG İSTİSNASI — ölçüm penceresi açıkken neyin değişebileceğinin ölçütü**
  (`test-degerlendirme-programi.md` D/8): tek soru şudur — *"bu değişiklik botun hangi
  işlemi açacağını değiştiriyor mu?"* Değiştirmiyorsa (tasarlanmış davranışı geri getiren
  onarım) serbest. Değiştiriyorsa pencere ya beklenir ya yeniden başlatılır.
- **DEĞİŞİKLİK PROTOKOLÜ** (D/9): eski ölçüt **silinmez**; yanına `[DEĞİŞTİ tarih]`
  eklenir. Kriter metni yorumlanmaz, sayı eşiği uygulanır. **Şüphede DAİMA statüko.**
- **Başarısızlık aynen raporlanır.** Çıkış tarafında **29 varyant** denendi, **1'i**
  geçti (`olcumler.md` → sayım). Bunu yumuşatmak da şişirmek de projenin değerini
  yok eder.
- **Tekrarlayan bulgu — keskin hâli:** geçen tek varyant çıkışı **gevşetiyordu**
  (sabit %10 hedef). Çıkışı **sıkılaştıran 28 varyantın 28'i de kaldı.**
  Yeni bir çıkış kuralı önerirken önce buna bak: sıkılaştırma öneriyorsan
  28/28'e karşı savunma yapman gerekiyor.
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
  belirgin fazladır — üç aday tabanın üçünde de fark **45–50 kayıt** civarında, çünkü
  `TP1_KISMI` satırları pozisyonu ikiye bölüyor. Kayıt sayan biri pencereyi **vaktinden
  önce dolmuş** ilan eder. Güncel sayım komutu `durum.md`'de.
- 🔴 **SÜZGEÇ SAYMAK İÇİNDİR, TOPLAMAK İÇİN DEĞİL.** Pozisyon *sayarken*
  `not x.get("kismi")` uygulanır. **P&L *toplarken* UYGULANMAZ** — kayıtlar `id` ile
  birleştirilir, yoksa TP1'de **realize edilmiş kâr kaybolur.** Ölçüldü:
  `golge` gerçek −1.350,72 iken süzgeçli hâli −5.815,70 → **4.465 $ hata**;
  `testbot`'ta 2.855 $. Süzgeç bu projede zaten bir kez yanlış toplam üretti.
- **MUTABAKAT DENKLEMİ — hangi yöntemi kullanırsan kullan, bunu tutturmuyorsa yanlıştır:**

  ```
  başlangıç bakiye + Σ P&L + funding − giriş ücreti (+ kasa sıfırlaması) ≈ equity
  ```

  Doğru yöntemde sapma **kuruş** mertebesinde çıkıyor (`golge` −0,07 · `testbot` −0,04).
  Süzgeçli yöntemde **binlerce dolar** sapıyor. Bir P&L toplamı yazmadan önce bu
  denklem koşturulur.
- **Ölçüm penceresinin başlangıcı ÇÖZÜLMEDİ — üç aday var, karar kullanıcının.**
  Pencere üç kez ön-kayıtlandı ve defter kendi içinde tutarsız. **Sayı üretmeden önce
  `durum.md`'nin pencere bölümünü oku** — tarih, üç tabanı birlikte veren sayım komutu
  ve çelişkinin kaynağı orada. Buraya tarih ya da rakam yazma.
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

## DÖRT DEFTER — her biri tek değişkeni yalıtır

| defter | soru | dosya |
|---|---|---|
| `testbot` | Bot ne yaptı? (ölçünün temeli) | `testbot.py` |
| `golge` | **İKİ İŞ birden** — aşağıya bak | `golge.py` |
| `benim` | Kararı kullanıcı verseydi? | `benim.py` |
| `ayna` | Bot girsin, çıkışa kullanıcı karar versin | `ayna.py` |

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
