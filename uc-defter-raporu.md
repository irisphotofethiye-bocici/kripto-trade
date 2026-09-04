# Üç Defter Karşılaştırmalı Raporu

**Anlık görüntü 2026-09-03.** Betimleyici — ön-kayıt yok, eşik yok, **hüküm yok.**
Rakamlar canlı defterden okundu ve saat başı değişir; buradaki değerler o günün
fotoğrafıdır. Kaynak betikler `scratchpad/uc_defter_*.py`.

Pozisyonlar aday arşiviyle birleştirildi (eşleşme %99,9–100), böylece defterlerde
kaydedilmeyen **funding · hacim · OI · taker · bant konumu** gibi giriş koşulları
da karşılaştırmaya girdi.

---

## 1. Kısa cevap

Beş ayrı "kol" ölçüldü. İkisi kâr eşiğinin hafifçe üstünde, ikisi **çok** altında,
biri arada. Ve ilginç olan şu: iki kötü kol neredeyse **aynı miktarda** kötü.

| kol | başabaşa uzaklık |
|---|---|
| defter3 · SHORT | **+2,7 puan** |
| gölge · pump_long_tezi | **+2,1 puan** |
| defter2 (yalnız SHORT) | −4,2 puan |
| gölge · **reddedilen girişler** | **−17,9 puan** |
| defter3 · **LONG** | **−18,2 puan** |

*"Başabaşa uzaklık"* şu demek: bu kolun kazanç/kayıp büyüklüğü verildiğinde
başabaş için gereken kazanma oranı ile gerçekte tutturduğu oran arasındaki fark.
Sıfırın üstü kârlı, altı zararlı.

İki uçtaki kolların **on sekiz puanlık** açığı bu projede görülmüş en büyük
sistematik sapmadır. Ve iki farklı sebepten geliyorlar — aşağıda ayrılıyor.

---

## 2. Defterler aynı şeyi ölçmüyor — önce bu ayrılmalı

Rapor boyunca en sık yapılacak hata bu olurdu, o yüzden başa koyuyorum.

**defter2 ve defter3 ikizdir.** Aynı evren, aynı çıkış kuralları, aynı
boyutlandırma. Tek fark yön: defter2 her şeyi satar; defter3 yükselmişleri satar,
**düşmüşleri alır**. Kontrol hücresinde (ikisinin de sattığı yarıda) eşleşen
işlemlerin farkı kuruş mertebesinde — yani ikizlik gerçek.

**gölge bunlardan tamamen farklı bir yerde duruyor.** Onun evreni botun kendi
kısa listesi. Ve gölge **tek bir soru sormuyor, iki iş birden yapıyor**:

- işlemlerinin büyük çoğunluğu, botun hiç oynamadığı bir **LONG tezinin** canlı
  denemesi
- geri kalanı, botun **reddettiği girişlerin** ne yapacağının kaydı

Bu ikisini toplamak yanıltıcıdır. Gölgenin kasasına bakıp *"bot iyi/kötü eliyor"*
demek, bu raporun en açık uyarısıdır — çünkü ikisi **ters işaretli**.

---

## 3. Kol kol ne oluyor

### İyi olan iki kol

**gölge · pump_long_tezi** — ölçülen tek net pozitif tez. Yükselen, hacmi patlamış,
bandının tepesine yakın coinleri alıyor. Kazanma oranı yüksek, ama kârı birkaç büyük
kayıpla sürekli tırtıklanıyor: en kötü beş pozisyonu tek başına toplam kârının
yarısından fazlasını götürüyor. Yani bu kol **kırılgan bir kâr** üretiyor.

**defter3 · SHORT** — defter2'nin yaptığı işin, düşenler çıkarılmış hâli. Aynı
evrende defter2 zararda, bu kol artıda. Fark tamamen defter2'nin *düşenleri de
satmasından* geliyor. Bu, raporun en temiz tek bulgusu: **düşen coini satmak,
yükselen coini satmaktan kötü.**

### Arada olan

**defter2** — evren olarak botun kendisinden belirgin biçimde iyi durumda, ama
hâlâ zararda. Zararının tamamı, yönü tek başına SHORT'a kilitlemiş olmasından
kaynaklanıyor: yukarıdaki iki kola bölündüğünde iyi yarısı artıya geçiyor.

### Kötü olan iki kol — ve bunlar birbirine benzemiyor

**defter3 · LONG** — düşen coinleri alıyor ve tutarlı biçimde kaybediyor.
Sekiz günün yedisinde eksi. Kazanma oranı yazı-turadan anlamlı biçimde düşük.

Mekanizması net: kural, coin her düştüğünde **yeniden tetikleniyor**. Aynı isim
düşmeye devam ettikçe defter onu tekrar tekrar alıyor — bazı isimlerde yarım düzine
kez, fiyat yarıya inerken. Ama dikkat: tekrar girişler pozisyon başına daha kötü
**değil**. Kural tekdüze biçimde kaybediyor, sadece aynı düşen coinde defalarca
ateşlendiği için kayıp çarpılıyor.

Bu kolun ödeme geometrisi aslında **sağlam** — kazandığında kaybettiği kadar
kazanıyor. Sorunu tamamen isabet oranı. Yani burada bir mekanik arızası yok,
**yön yanlış.**

**gölge · reddedilen girişler** — botun kapıda çevirdiği işlemler. Bunlar
gerçekten kötü çıkmış: neredeyse her kapı, reddettiği şeyle zarar etmekten
kurtulmuş.

Bu kolun ödeme geometrisi ise **bozuk** — kazandığında az kazanıyor, kaybettiğinde
çok kaybediyor. Yani defter3'ün LONG kolundan farklı bir hastalık: orada yön
yanlıştı, burada hem yön hem geometri kötü.

---

## 4. Kapılar — hepsi işini yapıyor

Botun reddettiği girişler kapı kapı ayrıldığında tablo tek yönlü çıkıyor:
**onay bekletme · dar stop · LONG vetosu · BTC-payı freni · taker soğuması** —
beşi de reddettikleriyle zarar etmekten kurtulmuş. En büyük katkı onay bekletmeden
geliyor; tek başına gölgenin en büyük zarar kalemi.

Yalnız **blowoff** kapısı ters işaret veriyor, ama örneklemi hüküm yazmaya
elverişli değil.

Bu, raporun en rahatlatıcı bulgusu: **botun eleme mekanizması bozuk değil.**
Bot kötü işlemleri doğru tanıyor. Sorun elediklerinde değil, **aldıklarında.**

---

## 5. Üç evren neye benziyor

Giriş anındaki koşulların medyanlarına bakıldığında defterler açıkça farklı
yerlerde avlanıyor:

- **gölge** ucuz, hacmi patlamış, bandının tepesindeki coinleri alıyor. Skoru
  en yüksek olanlar burada.
- **defter2 / defter3 SHORT** daha pahalı, daha likit, hâlâ bandının üstünde ama
  daha ılımlı hareket etmiş coinleri satıyor.
- **defter3 LONG** tamamen ayrı bir yerde: **hacmi ölü**, bandının **dibinde**,
  satıcının baskın olduğu, son saatlerde düşmüş coinler. Emir defteri en derin
  olanlar da bunlar — yani büyük ama hareketsiz isimler.

Bu son profil, "düşen bıçağı yakalama"nın veri üzerindeki tam karşılığı.

Bir de şu var: **reddedilen girişler en yüksek skorlu grup.** Yani botun kendi
skoru, reddedilenlerde en yüksek değeri alıyor ve o grup en çok kaybeden grup.
Skorun bu evrende ters çalıştığı daha önce de ölçülmüştü; bu rapor onu bağımsız
olarak tekrar üretiyor.

---

## 6. Kazananı kaybedenden ne ayırıyor — cevap: neredeyse hiçbir şey

Bu raporun en önemli negatif bulgusu.

Dört kolda, giriş anındaki hiçbir alan kazananı kaybedenden anlamlı biçimde
ayırmıyor. Hacim, OI, skor, fiyat, bant konumu, taker — hepsinde kazanan ve
kaybeden grupların medyanları neredeyse üst üste düşüyor.

Tek istisna **defter3'ün LONG kolu**: orada birkaç alan gerçekten ayırıyor —
kazananlar daha az düşmüş, banda daha yukarıdan girilmiş, hacmi daha canlı ve
funding'i daha yüksek isimler. Ama bu kolun kazananı yalnızca on üç pozisyon;
üzerine kural kurulacak bir taban değil.

⚠️ **Bir tuzağı burada açıkça atlıyorum.** "TP1'e ulaşma oranı" kazanan ve
kaybeden gruplar arasında dramatik biçimde farklı görünüyor. Bu **bilgi değil,
tanım**: TP1 zaten fiyat lehe gittiğinde tetikleniyor. Aynı tuzak bu projede
daha önce bir pozisyon-büyüklüğü bulgusunu çürütmüştü. Tutma süresi de aynı
sınıfta — kaybedenler hızlı kapanıyor çünkü stop hızlı çalışıyor. İkisi de
sonuçtur, sebep değil.

---

## 7. Ne kadar tutuluyorlar

Üç defterde de aynı desen: **kazananlar kaybedenlerin birkaç katı süre tutuluyor.**
Bu beklenen ve mekanik. Anlamlı olan kısım şu: defter2 ve defter3 pozisyonlarını
gölgeden belirgin biçimde **daha uzun** tutuyor, ve defter3'ün LONG kolu hepsinden
uzun. Uzun tutmak burada işe yaramamış.

⚠️ **"Toplam kârda kaldıkları süre" doğrudan ölçülemiyor.** Defterler yalnız
kapanış kaydı tutuyor; pozisyon içindeki fiyat yolu hiçbir yerde saklanmıyor.
Bu raporda o soru **cevaplanamadı**, sadece vekilleriyle yaklaşıldı. Düzeltme
yolu aşağıda.

---

## 8. Kayıp nasıl dağılıyor

İki farklı desen var ve ayrımı önemli:

**Kazanan kollarda kayıp yoğun.** Birkaç büyük pozisyon toplam kârın yarısından
fazlasını götürüyor. Yani bu kollar aslında daha iyi olabilirdi; onları aşağı
çeken şey nadir ama büyük kayıplar.

**Kaybeden kollarda kayıp yaygın.** Tek bir felaket yok; pozisyonların yarıdan
fazlası eksi kapanıyor ve zarar tabana yayılmış. Bu, "şanssız birkaç işlem"
açıklamasını kapatıyor — **kural sistematik olarak kaybediyor.**

---

## 9. Ölçülemeyenler — dürüstlük bölümü

Rapor yazılırken üç veri boşluğu çıktı:

1. **Stop mesafesi hiçbir deftere yazılmıyor.** Kapanış kayıtlarında ne stop
   seviyesi ne giriş anındaki ATR var. Bu yüzden *"LONG kolunun stopu daha mı
   geniş"* sorusu **cevaplanamadı** — sadece gerçekleşmiş kayıp görülebiliyor,
   ve o kayıp LONG'da SHORT'un iki katı.
2. **Piyasa değeri alanı tamamen boş.** Aday arşivindeki bu alan istisnasız
   boş geliyor, yani büyüklük boyutu hiç ölçülemedi.
3. **Pozisyon içi fiyat yolu yok**, yukarıda anlatıldığı gibi.

Bunların hiçbiri raporun bulgularını çürütmüyor, ama üçü de cevaplanamayan
soru bırakıyor.

---

## 10. Sorularım

**1 — defter3'ün LONG kolu devam etmeli mi?**
Kurulurken *"LONG kolunun kaybetmesi bekleniyor, 'gerçekten kötü' de tam bir
cevaptır"* yazılmıştı. Şu an tam olarak o cevabı vermiş durumda ve mekanizması da
anlaşıldı. Devam etmesi bilgi ekler mi, yoksa soru cevaplandı mı? Kapatmak
disiplin açısından erken olabilir — karar senin.

**2 — Bu iki defter için ölçüt ve pencere ne zaman yazılacak?**
`durum.md`'de ikisi için de *"henüz belirlenmedi"* yazıyor. Bu, ön-kayıt
disiplininin açık ihlali: sonuçları görmeye devam ederken ölçüt yazmak, ölçütü
sonuca uydurmak olur. **Ölçüt şimdi yazılmalı** — ve bence bu en acil madde.

**3 — Tek pozitif tez ne olacak?**
gölgedeki LONG tezi ölçülen tek kârlı kol. Ama kırılgan: kârı birkaç büyük kayba
bağlı. Bu bir aday mı, yoksa gürültü mü? Bunu anlamak için ayrı bir ön-kayıt
gerekir.

**4 — Stop verisi kaydedilsin mi?**
Defterlere stop ve ATR yazmak küçük bir kod değişikliği, ama **çalışan koda
dokunmak** demek. Onayın olmadan yapmam. Yapılmazsa stop genişliği sorusu
kalıcı olarak cevapsız kalır.

---

## 11. Düzeltme yolları

Etkisi ölçülmüş olandan spekülatif olana doğru sıralı.

### Yüksek güven — zaten ölçülmüş

**Düşen coini almayı bırakmak.** defter3'ün LONG kolu bunu doğrudan ölçtü ve
tutarlı biçimde kaybettiriyor. Aynı evrende yükselenleri satan kol artıda.
Bu, bu raporun en net tek sonucu.

**Aynı isme tekrar tekrar girmeyi sınırlamak.** Kural düşen coinde defalarca
ateşleniyor. Pozisyon başına daha kötü olmasa da, kayıp bu tekrarla çarpılıyor.
Sembol başına ardışık giriş sayısını sınırlamak kaybı doğrudan böler.
⚠️ Bu bir **sıkılaştırmadır**; ama bir *çıkış* değil **giriş** sınırıdır, yani
çıkış sıkılaştırmalarının 29/29 siciline tabi değildir.

### Orta güven — ölçüm gerekiyor

**Ödeme oranını ölçüt yapmak.** Beş kolun beşinde de kazanma oranı yanıltıcı
çıktı; kollar ancak kazanç/kayıp büyüklüğü hesaba katılınca doğru sıralanıyor.
Bu bir kural değil, **başarı ölçüsünün değişmesi.**

**Kazanan kolların kuyruk riskini kesmek.** İki pozitif kolun kârını birkaç
büyük kayıp yiyor. Ama bu bir çıkış sıkılaştırmasıdır ve bu projede otuz
varyantın yirmi dokuzu bu şekilde düşmüştür — ön-kayıt yazmadan denenmemeli.

### Düşük güven — sadece fikir

**Hacmi ölü coinlerden uzak durmak.** Kaybeden kolun en ayırt edici özelliği
hacim kuruluğu. Ama bu, düşen coin olmanın yan ürünü olabilir; ayrı bir bilgi
taşıyıp taşımadığı ölçülmedi.

### Skorun tersi — ayrı başlık, çünkü zaten ölçüldü

**[EKLENDİ 2026-09-03 — kullanıcı hatırlattı, ilk yazımda eksikti.]**

Raporun ilk hâlinde yalnızca *"skor ters çalışıyor"* yazmıştım. Eksik: **tersi
de ölçüldü**, hem ham fiyatta hem mekanikle.

**Ham fiyatta ters kenar gerçek ve iki ayrı veri kümesinde doğrulandı.** Yüksek
skorlu coinler düşüyor, düşük skorlular düşmüyor. İlişki güçlü ve tesadüf
değil.

**Mekanik uygulandığında ön-kayıtlı testi geçemedi** — ama nasıl düştüğü önemli:

- Yüksek skorluları **satmak**, maliyet **ve fonlama** düşüldükten sonra bile
  **pozitif** kaldı. Bu, bu projede maliyet sonrası ayakta kalan nadir
  bulgulardan biri.
- Ama **zamanla kararlı değil**: pencerenin iki yarısında işaret dönüyor,
  kenarın tamamı ikinci yarıda toplanıyor. Ön-kayıt bunu şart koşmuştu, ve
  düştüğü yer burası oldu.
- İşaret tutarlılığı ölçütünü de **bir gün farkla** kaçırdı.
- Stop genişliği ayrışması **yok** — yani "mekanik hilesi" savunması kapalı.
  Düşüş gerçek.

Yani skorun tersi *"işe yaramaz"* değil, **"henüz güvenilmez"**. Farkı önemli:
biri konuyu kapatır, diğeri ikinci bir pencere ister.

### 🔑 İki bağımsız ölçüm aynı yeri gösteriyor

Bu raporun defter3 bulgusuyla, daha önce yapılmış bir skor ölçümü **aynı sonuca
varıyor** — ve ikisi farklı evrende, farklı yöntemle, farklı zamanda yapıldı:

- Skor ölçümü, botun kapı öncesi havuzunda on yedi binden fazla LONG işlemi
  taradı: **skor bandı ne olursa olsun LONG'un tamamı negatif.** Yüksek skorlu
  bandı çıkarmak bile kurtarmıyor — eşikte uçurum değil **plato** var.
- Bu rapor, canlı ileri zamanda kırk pozisyonla aynı şeyi buldu: defter3'ün
  LONG kolu başabaşın on sekiz puan altında.

**İkisinin ortak mesajı: sorun skorun eşiği değil, bu evrende LONG açmak.**

Bu, tek bir ölçümün söyleyebileceğinden daha güçlü bir ifadedir — ama yine de
hüküm değil: ikisi de tek pencere, ikisinde de ayı verisi yok.

### Yapılmaması gereken

**Skoru bugünkü yönüyle kullanmak.** Botun boğa rejimindeki LONG kapısı, kendi
skorunun *"düşecek"* dediği coinlerde LONG açıyor. Bu ölçüldü ve o kapının
işlem başına getirisi belirgin biçimde negatif, stop olma oranı neredeyse
tümüyle. Reddedilen girişlerin en yüksek skorlu grup olması da aynı olgunun
başka bir yüzü.

**Skor eşiğini oynatarak kurtarmaya çalışmak.** Ölçüldü: eşikte uçurum yok,
plato var. Eşiği kaydırmak sayıyı biraz iyileştiriyor ama işareti
değiştirmiyor.

**Yeni bir giriş sinyali aramak.** Bu rapor, dört kolda giriş anındaki hiçbir
alanın kazananı kaybedenden ayırmadığını gösteriyor. Daha fazla alan eklemek
aynı duvara çarpar.

### Ve bir uyarı — mekanik ham kenarı yiyor

Skor ölçümünde kayda değer bir ayrıntı var: ham aşamada **pozitif** olan skor
bantları, botun mekaniği uygulanınca **hepsi negatife** düşüyor. Aradaki fark
işlem maliyetinden çok daha büyük — yani farkı yiyen şey **stop mekaniği**.

Bu, raporun 8. bölümündeki "kazanan kollarda kayıp yoğun" gözlemiyle ve bu
projede daha önce kaydedilmiş *"A-stop ham kenarın üçte ikisini yedi"*
bulgusuyla aynı yöne bakıyor.

⚠️ Ama o ölçümün kendi uyarısı da aynen geçerli: ham aşama ile mekanik aşama
**aynı ufka sahip değildi**, o yüzden kaymanın ne kadarı stop, ne kadarı ufuk —
**ayrılmadı.** Ayrı bir ön-kayıt ister.
