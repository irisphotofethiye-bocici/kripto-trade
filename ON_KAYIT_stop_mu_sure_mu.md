# ÖN-KAYIT — kenarı STOP mu yiyor, SÜRE mi?

**Yazılma tarihi:** 2026-08-26 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"süre yiyor çıkar muhtemel, koş bakalım"*

---

## 1 · Cevaplanmamış soru

Bir önceki ölçüm (`1649f8a`) şunu buldu: ham fiyat ölçümünde düşük skor bantları
**pozitifti**; aynı olaylara botun mekaniği uygulanınca **hepsi negatife** döndü.
Maliyet bu farkı açıklamıyor (yalnız 0,13 puan).

Ama o ölçüm iki şeyi **ayıramadı**: ham aşama sabit 24 saat tutuyordu, mekanik
aşamanın medyan tutması 4-6 saat. Yani fark ya **stoptan** geliyor ya **süreden**.

## 2 · AYIRMA YÖNTEMİ — eşleşmiş süre

🔴 **Kilit fikir:** her işlem için botun mekaniği kendi çıkış anını üretir
(`hold_M` saat). Aynı girişten **aynı saat sayısı** boyunca **stopsuz** tutulsa ne
olurdu — bu hesaplanabilir. O zaman:

```
Δ_stop = net(mekanikli)  −  net(stopsuz, AYNI sure)
```

Aynı giriş · aynı çıkış anı · aynı maliyet · aynı fonlama → **tek fark stop/TP/iz-süren.**
Bu, süre etkisini **tanım gereği** sıfırlar.

Süre etkisi ise ayrı ölçülür: stopsuz, **sabit ufuk** eğrisi

```
S_H  =  net getiri, stopsuz, tam H saat tutuldu       H ∈ {1, 2, 4, 6, 12, 24, 48}
```

Bu eğri stoptan tamamen bağımsızdır. İkisi birlikte ayrışmayı tamamlar.

⚠️ **Maliyet sabittir (işlem başına), fonlama süreyle BÜYÜR.** Kısa tutmak maliyeti
küçültmez, sadece onu karşılayacak fiyat hareketini küçültür. Fonlama ayrı raporlanır.

## 3 · Veri, evren, mekanik

Bir önceki ölçümün **aynı LONG evreni**: `radar_archive` tam tarama (KOŞU A) ·
`(sembol, saat)` tekil · giriş anlık görüntünün **bir sonraki** saatinin kapanışı ·
ofset −3 · tüm skor aralığı · `asgari_stop=2` elemesi **aynen** uygulanır
(kollar arasında ortak, çünkü stopsuz kol da aynı olay kümesinden gelir).

Mekanik `olcucu.py`+`testbot.py`+config'ten birebir (önceki iki ölçümle **aynı kod
deseni**). Maliyet iki senaryo. Fonlama oran (%/8s) × tutma saati.

**Yön: LONG birincil.** SHORT **önceden ilan edilmiş ikincil** rapordur
(bot iki tarafı da açıyor; sonuç ne çıkarsa yazılır, ölçüt uygulanmaz).

## 4 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

| # | ölçüt | eşik |
|---|---|---|
| **D1** 🔴 **BİRİNCİL** | `Δ_stop` ortalaması | **< 0** **ve** gün-kümeli t ≤ **−2,5** → *stop, eşleşmiş sürede kenarı yiyor* |
| **D2** | `Δ_stop` zaman yarıları | **iki yarıda da aynı işaret** |
| **D3** | süre eğrisi `S_H` | eğride **net > 0** olan bir bölge var mı — varsa hangi H'lerde (rapor) |
| **D4** | hangi faktör baskın | `\|Δ_stop\|` ile `\|S_48 − S_4\|` karşılaştırılır; büyük olan **baskın faktör** ilan edilir |

**Yorum kuralı (önceden sabit):**
- D1 geçer, D3'te pozitif bölge **yok** → *"stop yiyor, ama süre uzatmak da kurtarmıyor"*
- D1 geçer, D3'te pozitif bölge **var** → *"stop yiyor; stopsuz + doğru ufukta kenar var"*
- D1 düşer → *"stop suçlu değil"*, teşhis süreye ya da girişin kendisine kayar

🔴 **EN İYİ H SEÇİLMEZ.** `S_H` eğrisinde pozitif bir hücre çıkarsa bu **kural olmaz**;
kendi ön-kaydıyla ayrıca sınanır. Bu projede *"tabloya bakıp en yüksek sayıyı kural
yapmak"* reddedilmiş davranıştır.

⚠️ **Stopsuz kol GERÇEK bir strateji değildir** — likidasyon riski taşır ve bu ölçümde
likidasyon modellenmez. Kol **teşhis aracıdır**, öneri değil. Hükümde bu yazılır.

**Ek zorunlu rapor:** her H'de fonlamanın payı · mekaniğin gerçekleşen tutma süresi
dağılımı · `Δ_stop`'un kapanış sebebine göre kırılımı (stopla ölenlerde mi yoğunlaşıyor)
· skor bandına göre `Δ_stop` · SHORT ikincil tablosu.

## 5 · BEKLENTİ — sonuç görülmeden yazıldı

**D1'in geçmesine ~%70 veriyorum** (stop, eşleşmiş sürede negatif çıkar).
Gerekçe: bu projede A-stop bir ölçümde ham kenarın **%65'ini** yemişti ve çıkışı
sıkılaştıran **28 varyantın 28'i de** kalmıştı.

**Kullanıcının hipotezine (*"süre yiyor"*) ~%30 veriyorum** ve şu yönde bir
**karşı-tahmin** yazıyorum: maliyet işlem başına **sabit**, fiyat hareketi ise süreyle
büyür — bu yüzden **kısa** tutmanın maliyeti karşılaması daha zordur. Yani süre
etkisi çıkarsa **kısa sürenin aleyhine** çıkmasını bekliyorum, uzun sürenin değil.
Eğer eğri tersini gösterirse **tahminim yanlıştı diye aynen yazılır.**

Ayrıca ikisinin **aynı mekanizma** olabileceğini not düşüyorum: stop erken tetiklenir →
tutma kısalır → sabit maliyet küçük harekete bölünür. Bu durumda D1 ve D3 birbirini
dışlamaz.

## 6 · Dokunulmayanlar

Bot · state · defterler · zamanlanmış görevler: **hiçbiri**. Ayrı süreç, salt-okuma.
Betik: `scratchpad/stop_mu_sure_mu.py` (bu commit'ten SONRA yazılır).
