# ÖN-KAYIT — BOYUTLANDIRMA: seçim değil, ağırlık mı kaybettiriyor?

**Yazılma tarihi:** 2026-09-04 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** `durum.md` → *İKİ REJİM, TEK PİYASA* → Karar 2 (**sıranın birincisi**).

---

## 1 · Olgu — üç kesitte aynı

| kesit | ortalama getiri | net $ |
|---|---|---|
| SHORT (tümü) | **+%1,52** (t +2,43) | **−1.815** |
| LONG (tümü) | **+%0,77** (t +1,39) | **−3.861** |
| `MA50+ucuz` (NOTR-SHORT) | **+%1,10** | **−1.924** |

Botun **seçimi** ortalama pozitif getiriyor; **dolar** eksi. Aritmetik olarak bu,
büyük pozisyonların küçüklerden daha kötü sonuçlandığı anlamına gelir.

## 2 · 🔴 NEDEN BU KEZ DÖNGÜSEL DEĞİL — önceki denemenin dersi

Bu proje bir kez *"boyut kazananı kaybedenden ayırıyor"* diye bulgu yazdı,
sonra **TP1 kontrol katmanı eklenince çöktü** ve geri çekildi.

**Bu ölçüm o iddiayı tekrarlamıyor.** Fark:

| önceki (geri çekildi) | bu ölçüm |
|---|---|
| *"boyut, kazananı kaybedenden **yordar**"* — seçim iddiası | *"bu getiriler verildiğinde, bu **ağırlıklandırma** iyi miydi"* — muhasebe karşı-olgusu |
| TP1 kontrolü çökertti | TP1'e **hiç bakmaz, bakmamalı** |

🔑 **TP1'e koşullamak burada AŞIRI KONTROL olurdu.** TP1 sonucun bir parçasıdır
(nedensel yolun **üzerinde**), boyutun **öncesinde** değil. Nedensel yol üzerindeki
bir değişkene koşullamak, ölçmek istediğin kanalı **kapatır**.

🔑 **Ve boyut sonucu ETKİLEYEMEZ:** bot kâğıt üstünde çalışıyor, piyasa etkisi yok.
`notional` fiyat yolunu değiştirmez → `ret_i` boyuttan **bağımsızdır**. Bu yüzden
karşı-olgu aritmetik olarak iyi tanımlıdır:

```
gercek   P&L = Σ ( ret_i / 100 × notional_i )
esit     P&L = Σ ( ret_i / 100 × ortalama_notional )
```

⚠️ **Gerçek parada bu varsayım BOZULUR** (kayma, piyasa etkisi). Hüküm yalnız
kâğıt defter için geçerlidir ve öyle yazılır.

## 3 · POPÜLASYON

`testbot_islemler.jsonl` · birim **POZİSYON** (`id` ile birleştirme) ·
`net = Σ sonuc_usdt + Σ funding_usdt` · P&L toplarken `kismi` **SÜZÜLMEZ**.
376 pozisyon · 2026-07-23…2026-09-04.
Boyut dağılımı (tasarım girdisi, sonuç değil): medyan `notional` 1.830 ·
%95 5.290 · max 11.741 · en büyük 5'i toplam notional'ın **%5,9'u**.

## 4 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

🔴 **BİRİNCİL: BÖLÜNMÜŞ YARI TEKRARI.** Havuzda pozitif çıkması neredeyse
garanti (bölüm 1'deki aritmetik), o yüzden **tek başına hüküm taşımaz.**
Gerçek sınama tekrarlanabilirlik:

Pozisyonlar **giriş zamanına göre** kronolojik ikiye bölünür (A = ilk yarı,
B = ikinci yarı).

| # | ölçüt | eşik |
|---|---|---|
| **K1** | `esit − gercek` farkı | **A ve B yarısının İKİSİNDE DE > 0** |
| **K2** | permütasyon boş hipotezi | gerçek P&L, karıştırılmış ağırlık dağılımının **alt %5'inde** |
| **K3** | uç değer dayanıklılığı | en büyük **5** ve **20** notional atıldığında K1 **ayakta** |

**GEÇTİ** = K1+K2+K3 · **ZAYIF** = K1+K2, K3 düştü · aksi **DÜŞTÜ**.

**Permütasyon:** `notional` vektörü pozisyonlar arasında **10.000 kez** karıştırılır,
her seferinde `Σ(ret_i × notional_π(i))` hesaplanır. Gerçek değerin yüzdeliği
raporlanır. Bu, *"herhangi bir ağırlıklandırma bu kadar kötü olur muydu"*
sorusunun cevabıdır.

⚠️ **Çoklu karşılaştırma:** 1 birincil (bölünmüş yarı) + 3 ölçüt. Rejim ve kapı
kırılımları **betimleyicidir**, hüküm taşımaz.

## 5 · MEKANİZMA — "neden" sorusu, ayrıca ön-kayıtlı

Kullanıcının kayıtlı talebi: *"mekanizmayı bulman lazım, bot bu tercihi niye
yapıyor ve neye dayanarak?"* Boyut **skordan** türüyor
(`marjin = baz_equity × marjin_pct_hesapla(skor)`, [testbot.py:1218](testbot.py#L1218)).

**Sınanacak zincir:** `skor → boyut → kayıp`

| # | ölçüm | beklenen işaret |
|---|---|---|
| **M1** | `notional` ~ `ret` korelasyonu | **negatif** |
| **M2** | `skor_giriste` ~ `ret` korelasyonu | **negatif ya da sıfır** |
| **M3** | `skor` ~ `notional` korelasyonu | **pozitif** (tasarım gereği) |

**Zincir kurulmuş sayılır** ancak M1 negatif · M3 pozitif · M2 **pozitif değilse**.
M2 pozitif çıkarsa zincir **kopar** ve boyut-kayıp ilişkisinin başka bir
açıklaması aranır (kaldıraç, rejim, tutma süresi).

⚠️ `kaldirac` da ayrıca raporlanır — `notional = marjin × kaldirac`, iki kanal var.

## 6 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in (iki yarıda da) geçmesine ~%75 veriyorum.** Desen şimdiye kadar
baktığım **her** kesitte aynı yönde çıktı (SHORT, LONG, iki rejim, üç kapı) —
bu, bağımsıza yakın birkaç tekrar demektir. Yine de bölünmüş yarı gerçek bir
sınamadır ve düşebilir.

**K3'e (uç değer dayanıklılığı) ~%60** — en büyük 20 pozisyon toplam notional'ın
%16,9'unu taşıyor; atılınca etki zayıflayabilir.

**Yönlü tahminler (tutmazsa aynen raporlanır):**
1. `esit − gercek` farkı **pozitif ve büyük** olacak — kabaca kaybın yarısı
   mertebesinde.
2. **M2 sıfıra yakın çıkacak** (skor yordamıyor), M1 negatif. Yani zincir
   *"skor kötüyü seçiyor"* değil, **"skor bilgisiz ama boyutu belirliyor"**
   olacak — gürültüyü büyüteçle çarpmak.
3. Eşit ağırlık defteri **artıya çevirmeyecek**, yalnız kaybı küçültecek.

🔴 **Ve şimdiden:** K1 geçse bile bu **kural değildir.**
- Karşı-olgu **portföy kısıtlarını yok sayıyor**: 8 eşzamanlı slot, %25 düşüş
  freni, marjin tavanı. Eşit ağırlık bunları farklı tetikler.
- Kâğıt defter varsayımı (boyut fiyatı etkilemez) **gerçek parada geçersizdir.**
- Bir sonraki aşama **portföy simülasyonu**dur, kod değişikliği değil.

## 7 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
Salt-okuma, ücretli çağrı yok. Betik: `scratchpad/boyut_karsi_olgu.py`
(bu commit'ten SONRA).
