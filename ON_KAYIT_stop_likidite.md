# ÖN-KAYIT — STOP LİKİDİTE KÜMESİNİN İÇİNDEYSE DAHA ÇOK YENİR Mİ?

**Yazılma tarihi:** 2026-09-07 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"işleme girmeden önce buna bakmak faydalı olur diye
düşünüyorum, likidite temizliği ihtimali yüksek"* → *"ölç bakalım"*
**Betik:** `scratchpad/stop_likidite/01_olcum.py`

---

## 1 · HİPOTEZ — yön değil, YERLEŞİM

```
H1 : giriste stop bir likidite KUMESININ icindeyse, stop olma orani ARTAR
     (ve ham ileri getiri DUSER)
H0 : fark yok
```

🔑 **Bu bir yön sorusu değil.** Bugün düşen on yedi ölçümün neredeyse hepsi
*"fiyat nereye gider"* sorusuydu. Bu soru **farklı bir aile**: *"stopum
gürültünün içinde mi"*. Hiç sorulmadı.

## 2 · LİQMAP NASIL KURULUYOR — formül repodan, veri diskten

`py-liquidation-map` (aoki-h-jp) `mapping.py:193-211` incelendi; formül:

```
ALICI agresor hacim  ->  seviyeler  fiyat x 0,99 / 0,98 / 0,96 / 0,90
SATICI agresor hacim ->             fiyat x 1,01 / 1,02 / 1,04 / 1,10
agirlik = islem hacmi (kote cinsinden)
```

**Yaklaşıklık ve açıkça yazılıyor:** repo tek tek işlemleri kullanır; burada
**saatlik mum** kullanılıyor (`klines_1h_uzun`, 567 sembol, 2 yıl, diskte).
Her mum için:

```
alici agresor kote hacim = tbv x fiyat
satici agresor kote hacim = (v - tbv) x fiyat
temsili fiyat = (h + l + c) / 3
```

`tbv` (taker alış hacmi) verinin **içinde**; doğrulandı. Yaklaşıklık
**daha kaba** ama yapı aynı — ve bu ölçümün sorusu **konum**, mutlak
büyüklük değil.

## 3 · DEĞİŞKEN — stopun oturduğu yoğunluk

Girişten önceki **24 saatin** mumlarından harita kurulur, kovalar giriş
fiyatının **%0,25**'i genişliğinde. Sonra:

```
stop_yogunluk = stopun dustugu kovadaki toplam agirlik
stop_p = bu yogunlugun, AYNI HARITADAKI tum kovalara gore YUZDELIK sirasi
         -> [0, 1] · sembolden sembole ve oynakliktan BAGIMSIZ
```

**Birincil bölme (eşik ARANMAZ, önceden ilan):**
`stop_p` **en yüksek beşte bir** (küme içinde) vs **en düşük beşte bir**
(boş bölgede).

## 4 · 🔴 BELİRLEYİCİ KARIŞTIRICI — ve bunsuz sonuç ANLAMSIZ

Kümeler doğal olarak **fiyata yakın** oluşur; dar stoplu pozisyonların
stopu da fiyata yakındır. Yani *"kümedeki stop daha çok yenir"* bulgusu
büyük olasılıkla *"dar stop daha çok yenir"*in kılığıdır — ki o **zaten
biliniyor**.

```
ZORUNLU: stop mesafesi ATR CINSINDEN besli katmanlara ayrilir;
         karsilastirma HER KATMANIN ICINDE yapilir;
         katman farklarinin agirlikli ortalamasi BIRINCIL sonuctur
```

🔴 Ham (katmansız) fark da raporlanır. **Katmanlı etki hamın en az
%50'sini korumazsa, bulgu "stop mesafesinin kılığı"dır** ve öyle yazılır.
Bu proje bu tuzağa **üç kez** düştü (agresör dengesi · son yeni uç ·
`chg24` bantları).

## 5 · VERİ

```
POPULASYON : radar_archive · score>=30 · 4sa cooldown · LONG
             (giris_arama · r_hedef · kilit_aralik ile AYNI evren)
MEKANIK    : olcucu uclu stop · %10 hedef · 48s zaman stopu · maliyet %0,09
HARITA     : klines_1h_uzun (hacim + tbv) · giristen onceki 24 saat
N          : ~2.000 giris · ~72 gun
KESIF      : ilk %60 gun    HOLDOUT : son %40 gun
```

## 6 · METRİKLER

```
BIRINCIL  : STOP OLMA ORANI farki (kume ici - bos bolge), katmanli
IKINCIL   : ham +24 saat getiri farki  (ayni bolme)
```

**Neden stop-olma oranı birincil:** hipotez doğrudan *"stop yenir mi"*
diyor. Getiri ikincil, çünkü stop yenmesi ile getiri arasında mekanik
bağ var ve iki metrik aynı şeyi iki kez saymamalı.

## 7 · ÖLÇÜTLER — sonuç görüldükten sonra değişmez

| # | ölçüt | eşik |
|---|---|---|
| **S1** | HOLDOUT: katmanlı stop-olma farkı **> 0** (küme içi daha çok yenir) | evet |
| **S2** | HOLDOUT: gün-kümeli **t ≥ +2,0** | evet |
| **S3** | \|fark\| > **MDE** | evet |
| **S4** | KEŞİF ve HOLDOUT **aynı işaret** | evet |
| **S5** | 🔴 **katmanlı etki ≥ ham etkinin %50'si** | evet |
| **S6** | **negatif kontrol** (`stop_p` gün içi permüte, aynı hat) temiz | evet |

```
YON VAR                 = S1..S6 hepsi
STOP MESAFESININ KILIGI = S1+S2+S3 gecer ama S5 duser
YON YOK                 = S1 veya S4 duser
GOREMIYORUZ             = S1+S4+S5 gecer, S2/S3 duser
```

## 8 · EK RAPOR — ölçüt DEĞİL

- Beşli `stop_p` dilimi: N · stop-olma% · hedef% · ham getiri · ATR% · stop%
- Haritanın **yukarı/aşağı** ağırlık dengesi ile sonuç ilişkisi
- `stop_p` ile `stop_pct` çakışma oranı (**Spearman YOK** — dilim çakışması)
- Kaç girişte harita kurulamadı (mum eksiği)

## 9 · NE YAPILMAZ

- Bota, state'e, defterlere **dokunulmaz** (salt-okuma)
- **Apify/ücretli çağrı YOK** — harita diskteki mumdan kurulur
- Kova genişliği ve kaldıraç katsayıları **ARANMAZ** (repodan aynen)
- `R` ile paydasındaki değişken arasında **Spearman koşulmaz**
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 10 · GEÇERSE

🔴 Bu bir **giriş kapısı değil, STOP YERLEŞTİRME** kuralı olur — *"coini
alma"* demez, *"stopunu kümenin dışına koy"* der. Çok daha ucuz bir
değişiklik ve botun ölçülmüş zayıf noktasına denk düşüyor (kâr kilidinin
aralığı `0,35 ATR` çıkmıştı, yani gürültünün içinde).

Yine de: ham → **mekanik** → **portföy** sırası geçerli, ve **kod otomatik
değişmez.**

## 11 · BEKLENTİM — koşumdan önce

**`S5`'in (karıştırıcı) geçmesine %25.** Liqmap fiyat+hacimden, stop
fiyat+ATR'den türüyor; ortak bileşen fazla.
**Genel geçme (`S1..S6`) olasılığı %18.**

Lehte: bu bir **yerleşim** sorusu, bugün düşenlerin hepsi **yön** sorusuydu.
Aleyhte: bugün **on yedi ön-kayıt yazıldı, on yedisi de geçemedi.**
