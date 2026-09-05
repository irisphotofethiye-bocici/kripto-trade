# PLAN — mevcut defterleri kapat, üç yeni defter aç (BOĞA · AYI · büyük-mcap)

**Yazılma tarihi:** 2026-09-05 · **Durum: PLAN — hiçbir şey uygulanmadı.**
**Kaynak:** kullanıcı (2026-09-05): *"3 tane daha eklemeyeceğiz, mevcut olanları
kapatacağız ve 3 yeni defter açacağız: boğa, ayı ve büyük mcap"* ·
*"şu anda işlem yapma sadece fikir"* · *"hepsini kapatacağız, şu görünüm bota
kaybettiriyor zaten"*

---

## 1 · Kullanıcının gerekçesi DOĞRULANDI — sayılar

Mutabakat denklemi (`CLAUDE.md`) uygulandı; sapma **kuruş** mertebesinde.

```
defter    baslangic  enjekte    equity      GERCEK        %      pozisyon
testbot    10000,00  1005,94   4472,54   -6533,40    -59,4%         388
ayna        9207,12     0,00   4518,62   -4688,50    -50,9%         360
golge      10000,00     0,00   5910,38   -4089,62    -40,9%         905
defter2    10000,00     0,00   6972,61   -3027,39    -30,3%         334
defter3    10000,00     0,00   7211,17   -2788,83    -27,9%         248
benim      10000,00     0,00  10089,99     +89,99     +0,9%           7  (ölü)
```

⚠️ `benim` hariç **beşinin beşi de** %28–59 zararda.
⚠️ `defter2`/`defter3` de zararda → *"bot yanlış evrende avlanıyor"* tezi
**kurtarmadı.**

## 2 · 🔑 KAYIP NEREDEN GELİYOR — maliyet DEĞİL

```
testbot:  islem P&L  -6.027,80 $
          funding      -111,01 $
          giris ucret  -464,41 $
          -> maliyet toplami 575 $ = kaybin YALNIZ %8,8'i
```

**Kayıp işlemlerin kendisinden.** Maliyeti kısmak sorunu çözmez.
Pozisyon başına ≈ **−15,5 $** (kabaca −0,1R), tutarlı biçimde.

## 3 · 🔴 EN ÖNEMLİ TEŞHİS — beş defter GİRİŞİ değiştirdi, MEKANİĞİ değiştirmedi

Beş defterin **ortak paydası**:

| bileşen | hepsinde AYNI |
|---|---|
| stop | `A-stop` (yapısal adaylardan girişe en yakın, tavan 1,5×ATR) |
| hedef | sabit %10 (kapılı dallar) ya da 2R |
| ufuk | 48–72 saat |
| boyut | `islem_risk_pct %1,5` · 8 slot |
| asgari stop | %2,0 |

**Farklı olan tek şey: hangi işlemi seçtikleri.**
Beş farklı giriş seçimi denendi (bot kapıları · reddedilenler · kullanıcı kararı ·
farklı evren · çift yön) ve **beşi de benzer oranda kaybetti.**

> 🔑 **Giriş seçimi beş kez değiştirildi ve sonuç değişmedi. Değişmeyen şey
> MEKANİK. Altıncı, yedinci, sekizinci defteri de aynı mekanikle kurarsak
> aynı deneyi tekrarlamış oluruz.**

Bugünkü ölçümler bunu destekliyor: hedef `2R`'ye çevrilince stop sıralaması
**tersine döndü**; stop genişliği rejime göre işaret değiştirdi. Yani mekanik
**sonucu belirliyor** ve hiç sistemli olarak taranmadı.

## 4 · KAPATMA — sıra önemli, ve bugün YAPILMIYOR

🔴 **Zamanlanmış görevi doğrudan kapatmak YANLIŞ:** görev durursa açık
pozisyonları yöneten kod da durur; stop/hedef işlemez, pozisyonlar **asılı kalır.**

**Doğru sıra:**

```
1. YENI GIRIS DURDURULUR      -> config: maks_pozisyon = 0
   (testbot.py:1376 giris aramasini keser; CIKIS yonetimi calismaya devam eder)
2. Acik pozisyonlar DOGAL kapanir (stop/hedef/zaman) — kullanici karari
3. Acik sayisi 0 olunca zamanlanmis gorev devre disi birakilir
4. Defter dosyalari ASLA SILINMEZ — kanit tabani
```

**Etkilenen görevler:** `KriptoTestBot` · `KriptoDefter2` · `KriptoDefter3`.
`golge` · `ayna` · `benim` testbot içinden çağrılıyor → testbot giriş açmayı
bırakınca onlar da durur (`golge`'nin kendi tezi `golge_long_pump: 0` ile kapanır).

⚠️ **Kapatmadan önce alınacak son görüntü** (her defter için, tek dosya):
equity · açık pozisyon · mutabakat denklemi · pozisyon sayısı. Yoksa bu
rakamlar bir daha üretilemez.

⚠️ **`KriptoRadar` · `KriptoPerpSeri` · `KriptoPiyasa` · `KriptoNobetci`
KAPANMAZ** — onlar veri toplar, defter değildir. Kapanırsa **kalıcı veri
kaybı** olur (30 günlük sınıf, `CLAUDE.md`).

## 5 · ÜÇ YENİ DEFTER — dürüst temel değerlendirmesi

| defter | elimizdeki ölçülmüş temel |
|---|---|
| **AYI** | 🟢 **En sağlam.** Mevcut kapılar zaten ayıda ölçüldü; bugün `A_funding`'de geniş stop AYI'da t=+2,45/+2,92 çıktı (düzeltilmemiş) |
| **BOĞA** | 🔴 **Hiçbiri.** Skor bilgi taşımıyor · fiyat seviyesi taşımıyor · SHORT kaybettiriyor · `pump_long_tezi` iki güne bağlı |
| **büyük-mcap** | 🔴 **Hiçbiri** — üstelik mevcut mekanik orada **maliyet-baskın** (maliyet bir ATR'nin %22'si vs ucuzda %3,9) |

**Sonuç: ikisi "kâr defteri" olamaz, ancak KEŞİF defteri olabilir.**
Bu meşrudur (`defter2`/`defter3` deseni) ama **adı doğru konmalıdır.**

## 6 · TASARIM İLKESİ — her defter MEKANİĞİ değiştirsin, girişi değil

Bölüm 3'ün doğrudan sonucu:

| defter | yalıttığı **tek** değişken | somut öneri |
|---|---|---|
| **AYI** | *stop genişliği* | mevcut kapılar + `2,5×ATR` sabit stop (bugün iki pencerede tutarlı çıkan tek aday) |
| **BOĞA** | *yön ve çıkış* | boğada LONG mekaniği — giriş seçimi **kasten basit** tutulur (seçimde bilgi bulunamadı) |
| **büyük-mcap** | *ufuk ve hedef* | `mcap ≥ eşik` evreni + **uzun ufuk / dar hedef** (mevcut %10/72s orada ölü) |

🔴 **Üçü de aynı anda birden çok şeyi değiştirirse hiçbiri yorumlanamaz.**
Her defterin **bir** farkı olmalı; geri kalanı mevcut botla **birebir aynı**.

## 7 · HER DEFTER İÇİN ÖN-KAYIT ZORUNLU — kurulmadan ÖNCE

Her biri için, koşumdan önce yazılıp commit edilecek:

1. **Yalıtılan tek değişken** ve neden o
2. **Değerlendirme penceresi**: süre **ve** asgari N (ikisi de; hangisi önce
   dolarsa değil, **ikisi de** dolmalı)
3. **Geçme ölçütü** — gün-kümeli t · MDE · yarı kontrolü
4. **Geri alma anahtarı** config'te
5. **Ne olursa kapatılır** — başarısızlık ölçütü de önceden yazılır

⚠️ **Çoklu karşılaştırma:** üç defter aynı anda koşacak. Birinin şansla iyi
görünme olasılığı tek deftere göre yüksektir. Ön-kayıtlarda bu **sayılmalı**.

## 8 · SIRA ÖNERİSİ

```
1. Son goruntu alinir (mutabakat dahil)          [salt-okuma]
2. maks_pozisyon = 0  -> yeni giris durur         [config, geri alinabilir]
3. Acik pozisyonlar dogal kapanir                 [birkac gun]
4. AYI defteri once kurulur  <- tek saglam temel  [on-kayit + kod]
5. Buyuk-mcap: ONCE OLCUM (farkli mekanik kenar var mi), sonra defter
6. BOGA: ONCE OLCUM (bogada ne calisir), sonra defter
```

🔑 **4-5-6'nın sırası önemli:** AYI'nın temeli var, kurulabilir. Diğer ikisi
için **önce ölçüm** — yoksa kenarı olmayan iki defter daha koşturmuş oluruz
ve bölüm 3'teki hatayı tekrarlarız.

## 9 · Bu planın kendi riski

Beş defter aynı mekanikle kaybetti. Üç yeni defter **mekaniği değiştirmezse**
aynı sonucu verir ve altı ay sonra aynı tabloya bakarız.
**Bu planın tek gerekçesi mekaniği taramaktır** — rejim ya da evren değil.

## 10 · Dokunulmayanlar (bu belge yazılırken)

Hiçbir kod · config · state · zamanlanmış görev **değiştirilmedi.**
Kullanıcı talimatı: *"şu anda işlem yapma sadece fikir."*
