# ÖN-KAYIT — HEDEF `R`'YE BAĞLANIRSA (sabit `%10` yerine `m × stop`)

**Yazılma tarihi:** 2026-09-06 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"UAI 480 usd pozisyonda 149 dolar risk ediyor ama ARX
900 usdlik pozda 150 usd… biri 3,3 diğeri 0,97 rr"* → *"ilkini ölç"*
**Betik:** `scratchpad/r_hedef/01_olcum.py`

---

## 1 · SORUN — ölçülmüş, yapısal

Botun boyutlandırması **riski normalize ediyor, ödülü etmiyor:**

```
notional = hedef_risk / stop_frac          -> stop genisleyince notional KUCULUR
hedef    = notional x %10                  -> hedef DOLAR olarak da kuculur
risk     = SABIT $150

=> R:R = 10 / stop%     (kaldirac, marjin, skor GIRMIYOR)
```

Canlı örnek: `ARX stop %3,31 → R:R 3,02` · `UAI stop %10,28 → R:R 0,97`.
**Aynı dolar riski, üç kat farklı ödül.**

## 2 · ÖNERİ

```
A0    : hedef = giris x 1,10                (sabit %10 FIYAT)
R(m)  : hedef = giris x (1 + m x stop_frac) (R:R SABIT = m)
```

## 3 · 🔴 `m` TÜRETİLDİ, ARANMADI

```
m = 10 / medyan(stop_pct) = 10 / 3,58 = 2,793
```

Böylece **medyan işlemde hedef tam `%10`** olur → bu bir **yeniden dağıtımdır**,
seviye değişikliği değil. `m` için **arama YAPILMAZ.**

Dağılım (N=2.082):

```
stop p10 %2,21 -> hedef  %6,17     (A0: hep %10,00)
stop p25 %2,68 -> hedef  %7,49
stop MED %3,58 -> hedef %10,00
stop p75 %5,09 -> hedef %14,22
stop p90 %7,25 -> hedef %20,25

BASABAS:  A0'da %18,1 ... %42,0 (stopla degisir)
          R(m)'de SABIT %26,4
```

## 4 · 🔴 ÖNCE BİR MATEMATİK UYARISI

**Driftsiz rastgele yürüyüşte `m`'nin HİÇBİR etkisi yoktur:**
`P(hedef once) = 1/(1+m)` → `EV = 0`, her `m` için. Yani bulunacak bir fark,
**yalnız fiyat sürecinin gerçek yapısından** (ufka göre değişen sürüklenme /
momentum / ortalamaya dönüş) gelebilir.

**Lehte önsel:** ölçülmüş hedef taraması (`_ab_sabit_hedef_not`, 206 giriş)
hedef büyüdükçe getiriyi **artırıyor**: `%2,5 → +0,47 · %5 → +1,33 ·
%10 → +2,19`. Bu, uzun ufukta pozitif yapı olduğuna işaret eder ve **büyük `m`
lehine** bir argümandır.
**Aleyhte:** `%15`'te isabet başabaşın altına düşmüştü; ve `48s zaman stopu`
büyük hedefleri **kesiyor** (`stop p90` için hedef `%20,25` — 48 saatte zor).

## 5 · KAPSAM NOTU — 29/30 kuralı buraya UYGULANMAZ

*"Çıkışı sıkılaştıran 29 varyantın 29'u kaldı"* kuralı bu değişikliğe **doğrudan
uymaz**: `R(m)` dar stoplu işlemlerde hedefi **sıkılaştırır** (`%10 → %6,17`),
geniş stoplularda **gevşetir** (`%10 → %20,25`). Saf bir sıkılaştırma değil.

⚠️ Ama yine de bir **çıkış varyantıdır** ve sayaç `32 varyantta 1`. Bu **33.**

## 6 · VERİ

```
POPULASYON : radar_archive · score>=30 · 4sa cooldown · A0 mekanigi
N          : 2.082 giris · 72 gun      <- A2 kolunda N=31/75 idi; 27-67 KAT daha buyuk
KESIF      : ilk %60 gun (1.006)   HOLDOUT : son %40 gun (1.076)
MEKANIK    : fitil tetikli · ayni barda ikisi -> STOP · 48s zaman stopu ·
             maliyet %0,09 · stop DEGISMEZ (yalniz hedef degisir)
```

🔑 **Bu ölçüm `A2`'nin tekrarı değil, GÜÇLÜ hâlidir.** `A2` aynı fikri
`N=31/75` ile sınamış ve düşmüştü; orada *"düştü"* ile *"göremiyoruz"*
ayrılamıyordu.

## 7 · ÖLÇÜTLER — sonuç görüldükten sonra değişmez

Birincil: `R(2,793) − A0`, **eşleşmiş** fark (aynı girişler).

| # | ölçüt | eşik |
|---|---|---|
| **T1** | HOLDOUT'ta eşleşmiş fark | **> 0** |
| **T2** | HOLDOUT'ta **gün-kümeli t** | **≥ +2,0** |
| **T3** | farkın büyüklüğü **MDE'nin üstünde** | evet |
| **T4** | KEŞİF ve HOLDOUT'ta **aynı işaret** | evet |
| **T5** | yoğunlaşma: en iyi 2 gün + 5 işlem çıkınca hâlâ `T1` | evet |

```
GECTI       = T1..T5 hepsi
DUSTU       = T1 veya T4 duser
GOREMIYORUZ = T1+T4 gecer ama T3 duser
```

`t ≥ 2,0` çünkü **tek** birincil karşılaştırma var.

## 8 · EK RAPOR — ölçüt DEĞİL

- `m ∈ {2, 3, 4, 5}` ızgarası (koşumdan önce ilan) — **hüküm kurmaz**,
  yalnız `m`'ye duyarlılığı gösterir
- Her kolda: isabet% · **ampirik başabaş** · zaman stopunda kapanan oran ·
  medyan tutma
- 🔴 Stop dilimlerine göre kırılım: `R(m)` asıl olarak **geniş stoplu**
  işlemleri değiştirmeli; değiştirmiyorsa mekanizma çalışmıyor demektir

## 9 · NE YAPILMAZ

- Bota, state'e, defterlere **dokunulmaz** (salt-okuma)
- `m` **aranmaz** — formülle bir kez sabitlendi
- Izgara sonuçlarından **kural çıkarılmaz**
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 10 · GEÇERSE NE OLUR

1. Bu ölçüm **ham mekanik** (portföy yok, slot yok, fonlama yok)
2. Geçerse **portföy simülasyonu** — ⚠️ büyük hedefler **tutma süresini
   uzatır**, slot devri yavaşlar, pencere hızı düşer
3. Ancak o da geçerse `notrlong`'a uygulama + pencere sıfırlama

## 11 · BEKLENTİM — koşumdan önce, olasılıkla

**%30.**

Lehte: sorun **yapısal ve aritmetik** (R:R'yi tek değişken belirliyor);
ölçülmüş hedef taraması büyük hedef lehine; ve bu sefer **N 27-67 kat büyük**.

Aleyhte: (a) driftsiz yürüyüşte etki **sıfırdır** — fark ancak gerçek yapıdan
gelir; (b) `48s zaman stopu` `%20`'lik hedefleri kesiyor; (c) `A2` aynı fikri
zayıf güçle reddetmişti; (d) bugün **on ön-kayıt yazıldı, onu da düştü.**
