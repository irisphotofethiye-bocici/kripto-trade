# Sistem denetimi — hata raporu

*2026-08-11 · tüm bulgular doğrulandı ve sayısallaştırıldı · **canlı bota hiçbir değişiklik yapılmadı***

> **Not:** bot kağıt üstünde çalışıyor, gerçek emir göndermiyor. Aşağıdakilerin hiçbiri
> gerçek para kaybı değil. Ama ölçümlerin doğruluğunu ve gerçek paraya geçilirse ne
> olacağını belirliyorlar.

---

## Özet tablo

| # | Sorun | Ciddiyet | Zarar verdi mi? |
|---|---|---|---|
| 1 | Güvenlik freni açık işlemleri görmüyor | 🔴 **Yüksek** | Henüz hayır — ama koruma çalışmıyor |
| 2 | Hesaplarda komisyon eksik girilmiş | 🟠 Orta | Evet, tüm geçmiş sayılar hafif iyimser |
| 3 | Radar, tamamlanmamış saati tam sayıyor | 🟠 Orta | Evet, coin'ler haksız yere eleniyor |
| 4 | Yarım kapatılan işlem batarsa zarar iki kat yazılır | 🟠 Orta | Hayır, henüz hiç olmadı |
| 5 | İki kapıdan biri diğerinin başarısını yazıyor | 🟡 Düşük | Karne yanlış, para etkisi yok |
| 6 | Deneme defteri gerçek kurallarla çalışmıyor | 🟡 Düşük | Şimdilik hayır |
| 7 | Geçmiş testlerde farklı bir dalgalanma ölçüsü | 🟡 Düşük | Kısmen |
| 8 | Toplam pozisyon büyüklüğüne tavan yok | 🟡 Düşük | 1 numarayla birlikte önemli |
| 9 | Kapanan turda son fonlama alınmıyor | 🟢 Önemsiz | Toplam 6 dolar |

**Temiz çıkanlar** (kontrol edildi, sorun yok): saat dilimi hizası · borsa veri alanları ·
funding/pozisyon oranlarının ölçeği · stop hesabının test-canlı uyumu · geleceğe bakma
(look-ahead) · R hesabı.

---

## 🔴 1. Güvenlik freni açık işlemleri görmüyor

**Ne oldu:** Bot "param ne kadar?" diye sorduğunda **sadece kapanmış işlemleri** topluyor.
Şu anda açık olan işlemler, ne kadar zararda olurlarsa olsunlar, bu hesaba girmiyor.
Açık zararı hesaplayan bir fonksiyon **var** — ama sadece ekrana yazdırmak için
kullanılıyor, karar verirken hiç bakılmıyor.

**Neye yol açtı:** Bot %25 zarara ulaşınca kendini durdurması gerekiyor. Ama bu freni
tetikleyen sayı, açık işlemleri hiç görmüyor. Yani zarar **kesinleşmeden** fren devreye
girmiyor.

Şu anki gerçek durum:

```
Frenin gördüğü      :  8.401 $   (düşüş %0,1 — "her şey yolunda")
Açık pozisyon toplamı: 21.889 $  = sermayenin 2,6 KATI
```

Açık pozisyonlar birlikte %10 aleyhe giderse gerçek sermaye **6.212 $**'a (−%26) düşer —
ama fren o an hâlâ 8.401 $ görür ve **tetiklenmez.**

Buna iki şey ekleniyor:
- Fren, açık işlemler yönetilmeden **önce** çalışıyor → bir tur geç ölçüyor
- Yeni işlem büyüklüğü de aynı "kapanmış" rakama göre belirleniyor → açık zarar büyürken
  bot pozisyonlarını küçültmüyor

**Bugünkü çalışmayla bağlantısı:** Bu sabah riski %3'ten %1,5'e indirdim ve gerekçesi
*"fren tetiklenmesin, bot hayatta kalsın"* idi. O hesap frenin **çalıştığını** varsayıyordu.
Fren çalışmıyorsa gerçek risk, hesapladığımdan **daha yüksek.**

---

## 🟠 2. Hesaplarda komisyon eksik girilmiş

**Ne oldu:** Geçmiş testlerin çoğunda işlem maliyeti **binde 0,9** yazılmış. Botun gerçekte
ödediği **binde 1,3** (alım-satım komisyonu iki kez + fiyat kayması iki kez).

**Neye yol açtı:** Bugüne kadarki bütün ölçüm sonuçları işlem başına **0,04 puan iyimser.**

| Ölçüm | Yazılan | Doğrusu |
|---|---|---|
| A+B kapısı | +2,29 | **+2,25** |
| MA50+ucuz kapısı | +0,82 | **+0,78** |
| İkisinin birleşimi | +1,09 | **+1,05** |

İşaretler değişmiyor, kararlar aynı kalıyor — ama kenar sandığımızdan **%3,7 daha küçük.**

**Daha ciddi bir alt durum:** birkaç eski testte maliyet "risk biriminin %4'ü" diye
varsayılmış. Bu ancak stop mesafesi geniş olduğunda doğru. Dar stoplu işlemlerde
(%0,5 gibi) gerçek maliyet risk biriminin **%26'sı** — yani orada hata **6,5 kat.**

Ayrıca hiçbir geçmiş test **fonlama (funding) maliyetini** içermiyor.

---

## 🟠 3. Radar, tamamlanmamış saati tam sayıyor

**Ne oldu:** Bot her 5 dakikada bir çalışıyor. Borsadan saatlik mum verisi çekerken, içinde
bulunduğu **henüz bitmemiş saati** de tam bir saat gibi sayıyor. Saat 14:05'te, o saatin
sadece 5 dakikası geçmiş — ama hacmi tam saatlik hacimle karşılaştırılıyor.

**Neye yol açtı:** "Hacim patlaması" ölçüsü turun hangi dakikada çalıştığına göre değişiyor.
Ölçtüm:

| Turun çalıştığı dakika | Hacim eşiğini geçen coin oranı |
|---|---|
| 5. dakika | **%0,3** |
| 15. dakika | %1,8 |
| 30. dakika | %5,2 |
| 45. dakika | %9,3 |
| Saat kapanmışsa | **%15,0** |

**Aynı coin, saatin 5'inde eleniyor, 55'inde geçiyor — 50 kat fark.** Radar puanı, coin
seçimi ve gölge defterdeki LONG tezinin hacim şartı bundan doğrudan etkileniyor. Geçmiş
testler hep kapanmış saatle çalıştığı için test ile canlı arasında yapısal fark var.

---

## 🟠 4. Yarım kapatılan işlem batarsa zarar iki kat yazılır

**Ne oldu:** Bot kâr hedefinin yarısına gelince pozisyonun yarısını satıyor. Ama "bu işleme
ne kadar para koydum" kaydını yarıya indirmiyor. Sonra o işlem tamamen batarsa (likidasyon),
sistem **koyduğu paranın tamamını** siliyor — oysa yarısını çoktan geri almıştı.

**Neye yol açtı:** Şu ana kadar **hiç likidasyon olmadı** (0 vaka, 2 yarım kapama), yani
henüz kimseye zarar vermedi. Ama olursa o işlemin zararı gerçeğin ~2 katı yazılacak ve
karne bozulacak.

---

## 🟡 5. İki kapıdan biri diğerinin başarısını yazıyor

**Ne oldu:** Botun iki alım kuralı var. Bir coin ikisini birden karşılıyorsa, kod ilkinde
durup **hep birinci kuralın adını** yazıyor.

**Neye yol açtı:** İkinci kuralın (MA50+ucuz) karnesi eksik görünüyor:

```
Gerçek katkısı  : 445 olay
Karnede görünen : 384 olay   →  %14 eksik sayılıyor
```

Para etkisi yok — işlemler yine açılıyor. Ama hangi kuralın işe yaradığını ölçerken
yanlış yere bakıyoruz.

---

## 🟡 6. Deneme defteri gerçek kurallarla çalışmıyor

**Ne oldu:** Gölge defter (risksiz deneme alanı) "zorla" kipiyle çalışıyor ve canlıdaki bazı
kontrolleri atlıyor — bu sabah eklediğim **"stop %2'den yakınsa girme"** kuralı dahil.

**Neye yol açtı:** İlkesel bir çelişki: LONG için bu sabah yazdığım karar ölçütü, canlıya
alınacak olandan **farklı bir kuralı** ölçüyor.

**Ama pratikte henüz ısırmamış:** gölgedeki LONG işlemlerinin stop mesafesi hesaplanabilenlerin
**hiçbiri** %2'nin altında değil (en dar %2,19). Yani şu ana kadar gölge ile canlı aynı
işlemleri açardı. Kısa vadede sorun yok, ama kural ilerde ayrışabilir.

*(LONG penceresi şu an 18/25 — devam ediyor.)*

---

## 🟡 7. Geçmiş testlerde farklı bir dalgalanma ölçüsü

**Ne oldu:** Canlı bot dalgalanmayı (ATR) bir yöntemle, geçmiş testlerin ~20 tanesi başka bir
yöntemle hesaplıyor.

**Neye yol açtı:** Ortalamada fark küçük (%1,5), **ama vakaların %39'unda %10'dan fazla
sapıyor.** Toplu sonuçlar ayakta kalıyor; tek tek işlemlerin stop mesafeleri test ile
canlıda farklı. "Ortalama stop %0,31" gibi işlem-bazlı sayılar bundan etkileniyor.

---

## 🟡 8. Toplam pozisyon büyüklüğüne tavan yok

**Ne oldu:** Bot aynı anda 8 işlem açabiliyor ve her birinin büyüklüğü ayrı hesaplanıyor.
Toplamı sınırlayan bir kural yok.

**Neye yol açtı:** Şu an toplam pozisyon sermayenin **2,6 katı**; teorik tavan yaklaşık
**9,6 katı.** Bu bilinçli bir karardı — ama o karar **1 numaralı bulgu bilinmeden** verildi.
Fren körken tavan da yoksa, ikisi aynı riskin iki yüzü olur.

---

## 🟢 9. Kapanan turda son fonlama alınmıyor

**Ne oldu:** Bir işlem kapandığı turda, o son döneme ait fonlama ücreti hiç yazılmıyor.

**Neye yol açtı:** Neredeyse hiçbir şey — toplam fonlama bugüne kadar **6 dolar**. Tek yönlü
(hep lehte) bir sapma olduğu için kayda geçti, o kadar.

---

## Ne yapılmalı

### Şimdi güvenle yapılabilir — canlı botu etkilemez
Bunlar sadece ölçüm betikleri; çalışan bota dokunmaz, açık ölçüm penceresini bozmaz.

1. Maliyet sabitini **binde 1,3**'e çek, `0.04R` varsayımını kaldır *(bulgu 2)*
2. Ölçüm çıktılarına **"kaç ayrı sembol"** sütunu ekle *(bugün öğrenilen ders)*
3. Dalgalanma hesabını tek yöntemde birleştir *(bulgu 7)*

### Karar gerektirir — canlı botu değiştirir, **ölçüm penceresini bozar**
Açık pencere: 138 işlem / 30 gün, ön-kayıtta *"pencere boyunca hiçbir parametreye
dokunulmaz"* yazıyor. Aşağıdakiler kod düzeltmesi, parametre değil — ama yine de botun
davranışını değiştirir ve pencereyi geçersiz kılar.

| Düzeltme | Aciliyet |
|---|---|
| Freni açık zararı da görecek şekilde düzelt *(bulgu 1)* | **Yüksek** — koruma şu an çalışmıyor |
| Yarım kapama sonrası teminat kaydını güncelle *(bulgu 4)* | Orta — henüz tetiklenmedi |
| İki kapının atıfını ayır *(bulgu 5)* | Düşük — sadece karne |
| Tamamlanmamış saati kırp *(bulgu 3)* | Orta — ama geçmiş ölçümlerle uyumu bozar |

**Seçim üç şekilde yapılabilir:**
- **(a)** Hiçbirine dokunma, pencere dolsun (~20 gün), sonra hepsini birlikte düzelt
- **(b)** Yalnız freni düzelt, pencereyi yeniden başlat
- **(c)** Hepsini düzelt, pencereyi yeniden başlat

Bot kağıt üstünde olduğu için **(a)** savunulabilir — gerçek para riski yok ve ölçüm
bütünlüğü korunur. Gerçek paraya geçmeden önce 1 numara **mutlaka** düzeltilmeli.

---

## Denetimin kendi sınırı

Bu tarama **statik okuma + hedefli doğrulama** ile yapıldı; her satır çalıştırılarak test
edilmedi. Bulunmayan hata olmadığı anlamına gelmez. Özellikle denetlenmeyen alanlar:
panel arayüzü (`panel_sunucu.py`), nöbetçi/alarm katmanı, Telegram bildirimleri ve
harici veri sağlayıcıları (CoinGecko, Apify, Coinalyze).

**Doğrulama betikleri:** `scratchpad/denetim_olcum.py` · rapordaki her sayı çalıştırılarak
üretildi, hiçbiri tahmin değil.
