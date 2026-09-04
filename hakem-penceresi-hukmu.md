# Hakem Penceresi — Dilimli Rapor ve Altı Kararın Açılışı

**Yazıldı 2026-09-04.** Pencere **2026-08-22 03:13:43**'te doldu (138. pozisyon);
13 gün fark edilmedi. Bu belge o boşluğu kapatır.

Taban **2026-08-12 01:17**. Betikler: `scratchpad/hakem_*.py` · `dilim_cikar.py`.
Tüm rakamlar **salt okumadan**; bota dokunulmadı.

---

## 1. Pencere sonucu — zorunlu yöntemle

`CLAUDE.md` pencere sonucunun **equity'den türetilmesini** şart koşuyor, defter
toplamından değil. Ve kasa sıfırlaması pencerenin **içinde** kaldığı için
düşülmesi gerekiyor.

```
equity pencere basi              8.053,62
equity simdi                     4.994,95
kasa sifirlamasi (DUSULUR)       1.005,94
-----------------------------------------
PENCERE REALIZE                 -4.064,61
```

Defter P&L ile fark **+355,90** — fonlama, giriş ücreti ve sınır pozisyonları.
Mutabakat tutuyor.

🔴 **PENCERE EKSİ KAPANDI.**

---

## 2. Dilimler — dörde değil **sekize** bölünüyor

`durum.md` dört dilim yazıyordu ve **eksikti**: yalnız `btc_pay` frenini
sayıyor, `düşüş freni`nin iki HALT dönemini ve 08-27 kapatmasını içermiyor.
Dilimler equity kütüğündeki durum geçişlerinden — yani **kanıttan** — yeniden
çıkarıldı.

| dilim | ne değişti | gün | poz | P&L | kazanma |
|---|---|---|---|---|---|
| **A1** | orijinal donmuş yapılandırma | 7,5 | 92 | **+357** | %48 |
| A2 | btc_pay freni kapatıldı | 0,2 | 6 | +54 | %50 |
| A3 | geri açıldı | 0,1 | 1 | +197 | %100 |
| **B** | btc_pay freni **kalıcı** kapandı | 2,8 | 65 | **−1.802** | %34 |
| C | *düşüş freni durdurdu* | 1,4 | 0 | — | — |
| **D** | elle devam, zirve sıfırlandı | 2,7 | 53 | **−1.702** | %47 |
| E | *düşüş freni yine durdurdu* | 1,3 | 0 | — | — |
| **F** | düşüş freni tamamen kapatıldı | 7,5 | 123 | **−1.526** | %50 |

**Parametreler pencere içinde beş kez değişti.** Pencerenin kuralı
*"parametre değişmez, kapı eklenmez, eşik oynatılmaz"* idi. `durum.md` bunu
zaten *"BU BİR ÖLÇÜM PENCERESİ İHLALİDİR"* diye kaydetmişti — bu rapor ihlalin
boyutunu gösteriyor.

---

## 3. İki dilim, iki ayrı hikâye

**A1 — orijinal yapılandırma, 7,5 gün, artıda.** Ama gün-kümeli bakıldığında
**anlamlı değil**: sekiz günün dördü artı, `t = +0,34`. Yani *"orijinal
yapılandırma çalışıyordu"* **denemez.** Artı sonuç gürültüden ayrılamıyor.

**Değişiklik sonrası (B+D+F) — 15 gün, 241 pozisyon, anlamlı biçimde eksi:**
`t = −3,49`, on beş günün yalnız **ikisi** artı.

Yani pencerenin verdiği tek sağlam ifade şudur: **değişikliklerden sonraki
dönem gerçekten kötü, öncesi ise belirsiz.**

---

## 4. 🔴 Asıl bulgu — bot 24 Ağustos'tan beri hiç SHORT açmadı

Dilimler yön kırılımıyla bakılınca ortaya bu çıktı:

| dilim | SHORT | LONG | SHORT P&L | LONG P&L |
|---|---|---|---|---|
| A1 | 85 | 7 | **+468** | −111 |
| B | 24 | 41 | −1.486 | −316 |
| D | **0** | 53 | — | −1.702 |
| F | **0** | 123 | — | −1.526 |

**176 ardışık LONG pozisyon, tek bir SHORT yok, toplam −3.228.**

Sebebi kodda ve veride:

- Radar arşivi **24 Ağustos'tan beri istisnasız `BOGA`** rejimi bildiriyor.
- Botun `BOGA` kuralında SHORT bir **istisnadır** — dar bir koşul kümesi
  gerektiriyor. Koşullar sağlanmayınca SHORT hiç açılmıyor.
- Veto kütüğü de bunu doğruluyor: 24 Ağustos'tan bu yana vetolanan girişlerin
  **hepsi LONG**; tek bir SHORT vetosu yok, çünkü aday bile üretilmiyor.

Ve A1'de bot %92 SHORT'tu ve **SHORT kolu artıdaydı** (+468). Rejim BOĞA'ya
dönünce bot yönünü tersine çevirdi ve o günden beri kaybediyor.

### Bu, bu oturumda ölçülen üç şeyle örtüşüyor

Üç bağımsız ölçüm aynı yeri gösteriyor:

1. **defter3'ün LONG kolu** — aynı evrende, canlı ileri zamanda, başabaşın on
   sekiz puan altında.
2. **Skor freni ölçümü** — on yedi binden fazla LONG işlem: skor bandı ne
   olursa olsun LONG'un tamamı negatif, eşikte plato var.
3. **Bu rapor** — bot BOĞA'da LONG'a kilitlenince 176 pozisyonda −3.228.

Üçü farklı evren, farklı yöntem, farklı zaman. **Ortak mesaj: bu piyasada
LONG açmak kaybettiriyor, ve bot tam da onu yapmak zorunda kalıyor.**

---

## 5. Karıştırıcı kontrolü — dürüstlük bölümü

**Piyasa da değişti.** B diliminde BTC 2,8 günde **%13 yükseldi**. Botun o
dilimdeki kaybı, kural değişikliğinden mi ralliden mi geldiği **ayrılamıyor** —
ikisi aynı anda oldu.

**Son dilimde diğer defterler de kaybetti**, ama günlük bakıldığında birlikte
hareket etmiyorlar: sekiz günün yalnız **birinde** dört defter aynı anda eksi.
Yani *"hepsi kaybetti, demek ki piyasa"* açıklaması **kurulamıyor** — toplamlar
benzer, günlük yollar farklı.

**A1 anlamlı değil.** Orijinal yapılandırmanın iyi olduğunu söyleyemeyiz.

---

## 6. Altı karar — hakem ne diyor

Grafın kuralı şuydu:

> *"Pencere **eksi** kapanırsa: üç savunma **birden** düşer; 1·2·3 birlikte
> gözden geçirilir; 4 zaten tercihe dayanıyordu."*

Pencere eksi kapandı, ve eşik fazlasıyla aşıldı. Ölçüt metni **yorumlanmaz,
sayı eşiği uygulanır** (D/9).

| # | karar | hakemin sonucu |
|---|---|---|
| **1** | `MA50+ucuz` kapısı | **savunma DÜŞTÜ.** Dayanağı *"o ölçüm canlıya benzemiyor"* idi; canlı pencere de eksi kapandı |
| **2** | Sabit %10 hedef | **aynı savunma, aynı kader** — ikisi aynı koşturmadan geliyordu |
| **3** | Hedefin `MA50`'ye genişletilmesi | **aynı** |
| **4** | 1,5R kısmi ezmesi | savunması zaten ölçüme değil **tercihe** dayanıyordu; hakem burada yeni bilgi vermiyor |
| **5** | `A+B` stop mesafesi | pencereye kilitli iş — **artık serbest**, ölçülebilir |
| **6** | LONG tarafı | 🔴 **acil hâle geldi** — bölüm 4'e bak |

### ⚠️ Ama üç çekince, ve ciddiler

**Pencere kirlendi.** Parametreler beş kez değişti. Hakemin ön koşulu buydu ve
tutulmadı. Sonucun ne kadarı kuralların, ne kadarı değişikliklerin —
**ayrılmadı.**

**Kirlenmenin yönü not edilmeli.** Değişiklikler koruma **kaldırıyordu** (iki
fren de kapatıldı). Yani pencere, orijinal yapılandırmayı haksız yere kötü
göstermiş değil — aksine, en iyi dilim orijinal olandı. Bu, *"eksi sonuç
kirlenmeden geliyor"* itirazını **zayıflatır**, ama ortadan kaldırmaz.

**Yine de hüküm bir kapı kapatmıyor.** `CLAUDE.md`: *"Şüphede DAİMA statüko."*
Bu belge savunmaların düştüğünü söyler; **kapıları kapatmaz.** Kapı kapatmak
kullanıcı kararıdır ve ayrı bir işlemdir.

---

## 7. Sırada ne var

**Birinci — LONG kilidi.** Bot BOĞA'da yapısı gereği LONG açıyor ve üç ayrı
ölçüm LONG'un bu evrende kaybettirdiğini söylüyor. Bu, altı kararın hepsinden
acil. En küçük müdahale: BOĞA rejiminde LONG için **ek bir koşul**, ya da
SHORT istisnasının genişletilmesi. İkisi de kapı değişikliğidir ve **yeni bir
pencere** ister.

**İkinci — 5 numaralı iş serbest kaldı.** `A+B` stop mesafesi ölçümü pencereye
kilitliydi, artık değil. Defterde *"pencere sonrası İLK İŞ"* diye yazılıydı.

**Üçüncü — yeni pencere tanımlanmalı.** Eskisi kirlendi. Yenisi kurulacaksa
ölçütü ve dokunulmazlık kuralı **koşturmadan önce** yazılmalı; ve bu kez
tetiği kontrol eden bir satır konmalı — bu pencerenin dolduğu 13 gün fark
edilmedi.

---

## 8. Bu rapor neyi söylemiyor

- **Hangi kapının kaybettirdiğini** söylemiyor. Pencere toplu sonuç verir,
  kapı kırılımı ayrı ölçümdür.
- **Orijinal yapılandırmanın iyi olduğunu** söylemiyor — A1 anlamlı değil.
- **Kaybın piyasadan mı kuraldan mı geldiğini** kesin söylemiyor; B diliminde
  ikisi aynı anda oldu.
- **Bir kapıyı kapatmıyor.** Savunmaların düştüğünü kaydeder, kararı kullanıcıya
  bırakır.
