# ÖN-KAYIT — ATR stop çarpanı, olay seviyesinde

*Yazıldı 2026-08-24, **koşturmadan ÖNCE**. Sonuç görüldükten sonra ölçüt değişmez.*

## NEDEN BU ÖLÇÜM

TimesFM testi ATR'nin **iyi kalibre bir oynaklık ölçer** olduğunu gösterdi
(`olcumler.md` → TimesFM KUANTİL KAPSAMA). Yani stop probleminin kaynağı
oynaklık tahmini değil, ona uygulanan **çarpan.**

Ölçülen mevcut durum (`pozisyon_izleme.jsonl`, 161 pozisyon):

```
BOTUN SU ANKI CARPANI:  stop / atr_giriste  ->  MEDYAN 1,50   (%75 dilim 1,51)
DEFTER (anlik goruntu):  SHORT 136 (-1.656 $) · LONG 68 (-930 $)
STOP ile kapanan:        %80 · MAE medyan %3,20 · tepeye sure medyan 1,59 sa
```

**İDDİA: `k = 1,50` çok sıkı. Daha geniş bir çarpan, aynı girişlerde daha iyi
sonuç verir.**

## TASARIM — iki kol, ikisi de aynı soruyu sorar

**KOL A — botun GERÇEK girişleri (ilgi düzeyi yüksek, N düşük).**
`pozisyon_ozet` + `testbot_islemler`'den `sym · giris_ts · giris · yon ·
atr_giriste`. Aynı girişler, farklı stop → **eşleşmiş test**, `t` iyi tanımlı
(CLAUDE.md: alt-küme değil, aynı giriş iki kolda da var).

**KOL B — olay seviyesi vekil girişler (N yüksek, rejim ayrımı mümkün).**
2 yıl · 567 sembol · 1h mumlar. Botun karakteri SHORT-ağırlıklı ve pump
avcısı olduğu için vekil olay: **`chg24 ≥ +%20` → o barın kapanışında SHORT.**
LONG kolu ayrıca `chg24 ≤ −%20` ile ölçülür. Aynı sembolde 24 bar bekleme.

## MEKANİK — stop YALNIZ BAŞINA yalıtılır

Hedef yok, iz süren yok, kısmi kâr yok. Sadece:

```
   stop:  k x ATR(14) uzakta       (SHORT icin YUKARIDA, LONG icin ASAGIDA)
   cikis: stop degmezse H saat sonunda kapat
```

Böylece sıralama belirsizliği yok (stop bar içinde `high`/`low` ile aranır,
zaman çıkışı bar kapanışındadır). **Hedef eklenmemesi bilinçli:** amaç stopun
kendi etkisini ölçmek, çıkış mantığının tamamını değil.

**Fonlama DAHİL.** `scratchpad/funding_gecmis/` — birim doğrulandı: **yüzde/8sa**,
medyan `|r|` = %0,0050 (Binance varsayılanıyla tutarlı). SHORT pozitif oranı
**tahsil eder**, LONG öder. `*100` uygulanmaz.

## TARANACAK

```
k  =  0,50 · 0,75 · 1,00 · 1,25 · 1,50 · 2,00 · 2,50 · 3,00 · 4,00 · 6,00 · STOPSUZ
H  =  2 · 4 · 8 · 24 saat
```

**44 hücre = çoklu karşılaştırma.** Bu yüzden aşağıdaki holdout zorunlu.

## ÖLÇÜTLER (sonuca bakmadan yazıldı)

| # | ölçüt | eşik |
|---|---|---|
| 1 | **Holdout** — zaman ikiye bölünür; `k*` **ilk yarıda** seçilir, **ikinci yarıda** `k=1,50`'yi geçmeli | fark > 0, eşleşmiş |
| 2 | **Rejim** — `k*` üstünlüğü ATH · DÜZELTME · DERİN_AYI'dan **en az 2'sinde** korunmalı | 2/3 |
| 3 | **Eğri biçimi** — `k` eğrisi tek-tepeli ya da monoton olmalı, testere değil | gözle + komşu hücre tutarlılığı |
| 4 | **İki kol uyumu** — KOL A ve KOL B `k*` yönünde (daha geniş / daha dar) **aynı** işareti vermeli | işaret aynı |
| 5 | **Likidasyon denetimi** — geniş stop kolunda azami ters hareket raporlanır | bilgi amaçlı, kapı değil |

**HÜKÜM KURALI:** 1 ve 4 geçmezse **statüko** (`k=1,50` kalır) — CLAUDE.md
*"şüphede DAİMA statüko"*. 1 geçip 4 kalırsa **hüküm yazılmaz**, iki kolun neden
ayrıştığı araştırılır.

## KAPSAM DIŞI / BİLİNEN SINIRLAR

- **1 saatlik çözünürlük.** Bar içi yol bilinmiyor; stop `high`/`low` ile
  aranır. Botun medyan tutma süresi 2,5 saat olduğu için H=2 kolunda bu
  **kaba** bir yaklaşımdır ve öyle raporlanacaktır.
- **Kaldıraç yok** — getiriler kaldıraçsız yüzde. Kaldıraç `k`'yi doğrusal
  ölçekler, en iyi `k`'yi değiştirmez; **likidasyon** üzerinden değiştirir,
  o yüzden ölçüt 5 var.
- **Bu bir kâr iddiası değildir.** Geçse bile bota uygulanması ayrı karardır
  ve `CLAUDE.md` müdahale yasağına tabidir.
- Vekil girişler botun girişleri **değildir**; KOL A bu yüzden var.

Bota yazım: **YOK.** Salt-okuma.
