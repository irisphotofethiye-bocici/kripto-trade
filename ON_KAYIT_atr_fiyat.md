# ÖN-KAYIT — `ATR/FİYAT` DOĞRUDAN GİRİŞ FİLTRESİ OLARAK

**Yazılma tarihi:** 2026-09-06 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"atr fiyat ölçümünü de yap"*
**Betik:** `scratchpad/atr_fiyat/01_olcum.py`

---

## 1 · NEDEN — bugün üç ölçüm buraya işaret etti

```
1) R(m) mekanizma tablosu   : dar stop hucresi +0,4171 · genis -0,1047
2) genis stop eleme         : elenen hucre iki yarida da negatif (t -1,44, KIL PAYI)
3) stop mesafesi LONG       : stop 2,5xATR'ye GENISLETILSE DE dar hucre en iyi
                              (+0,3418) -> 'dar stop iyi' DEGIL, 'SAKIN COIN iyi'
```

Üçü de **stop üzerinden dolaylı** bakıyordu. `ATR/fiyat` doğrudan
**coinin oynaklığıdır** ve hiç böyle ölçülmedi.

## 2 · 🔴 YASAK: SPEARMAN KULLANILMAYACAK

`R = net%/stop%` ve `stop% ≈ 1,5 × ATR/fiyat` (ATR yedeği bağladığında).
Yani `ATR/fiyat`, `R`'nin **paydasıyla** doğrudan ilişkilidir.

`CLAUDE.md`: *"`R` ile paydasındaki değişken arasında Spearman KOŞULMAZ."*
Bu kuralı **bugün bir kez ihlal ettim** (`rho(stop_pct, R) = +0,40` çıkmıştı
ve medyan bölme tam tersini söylüyordu, `olcumler.md`).

🔑 **Geçerli istatistik: sabit dolar riskine normalize edilmiş ORTALAMA `R`**
ve dilimler arası **gün-kümeli fark**. Korelasyon **hiç hesaplanmayacak**.

## 3 · SORU ve HİPOTEZ — tek yönlü, koşumdan önce

```
H1 : dusuk ATR/fiyat (sakin coin) daha yuksek ort R uretir
H0 : yon yok
```

## 4 · TASARIM — eşik ARANMAZ

🔴 **Hiçbir eşik seçilmez.** Karşılaştırma **önceden ilan edilmiş**:

```
BIRINCIL : EN DUSUK ATR besli dilimi   -   EN YUKSEK ATR besli dilimi
           (holdout'ta, gun-kumeli)
```

Tek karşılaştırma → çoklu karşılaştırma düzeltmesi gerekmiyor, `t ≥ 2,0`.

## 5 · VERİ

```
POPULASYON : radar_archive · score>=30 · 4sa cooldown · LONG · A0 mekanigi
DEGISKEN   : ATR14(kapanmis barlar) / giris fiyati x 100
N          : ~2.078 giris · 72 gun
KESIF      : ilk %60 gun   HOLDOUT : son %40 gun
```

## 6 · ÖLÇÜTLER — sonuç görüldükten sonra değişmez

| # | ölçüt | eşik |
|---|---|---|
| **V1** | HOLDOUT: en düşük dilim `R` − en yüksek dilim `R` | **> 0** |
| **V2** | HOLDOUT: gün-kümeli t | **≥ +2,0** |
| **V3** | farkın büyüklüğü **MDE'nin üstünde** | evet |
| **V4** | KEŞİF ve HOLDOUT'ta **aynı işaret** | evet |
| **V5** | **negatif kontrol** aynı boru hattında etki üretmemiş | evet |

```
YON VAR     = V1..V5 hepsi
YON YOK     = V1 veya V4 duser
GOREMIYORUZ = V1+V4 gecer ama V3 duser
```

## 7 · NEGATİF KONTROL

`ATR/fiyat` **gün içinde permüte** edilir ve **birebir aynı** boru hattından
geçirilir (dilim + holdout farkı + gün-kümeli t).

🔴 Bugün `giris_arama`'da negatif kontrolü eksik kurmuştum (2 hücre vs 39) ve
`genis_stop`'ta sahte değişken **gerçekle aynı eşiği** seçmişti — o yüzden
burada **tam eşleştirilmiş** hat koşuyor.

## 8 · EK RAPOR — ölçüt DEĞİL

- Beşli dilim tablosu: N · ort `ATR%` · ort `R` · `net%` · isabet% ·
  **ampirik başabaş** · stop olma% · medyan tutma
- 🔴 **`ATR/fiyat` ile `stop_pct` ne kadar aynı şey?** İkisinin arasındaki
  ilişki raporlanır. Neredeyse birebirse, bu ölçüm *"yeni bir değişken"*
  değil, **aynı şeyin doğrudan ölçümüdür** ve hüküm öyle yazılır.
- `chg24` ile ilişki (pump'lamış coin = oynak coin mi?)

## 9 · NE YAPILMAZ

- Bota, state'e, defterlere **dokunulmaz** (salt-okuma)
- **Spearman/korelasyon hesaplanmaz** (bölüm 2)
- Eşik **aranmaz** — dilimler veriden, karşılaştırma önceden ilan
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0

## 10 · GEÇERSE

1. **Ham mekanik** ölçüm → sonra **portföy simülasyonu**
   ⚠️ Oynak coinleri elemek **işlem sayısını azaltır**; `notrlong` bu sabah
   *"poz açmıyor"* diye açılmıştı — pencere hızı yeniden kontrol edilmeli
2. Ancak o da geçerse `notrlong`'a **giriş kapısı** + pencere sıfırlama

## 11 · BEKLENTİM — koşumdan önce, olasılıkla

**%35.** Bugünkü en yükseklerden, çünkü **üç bağımsız ölçüm** aynı yere
işaret etti ve sonuncusu (stop genişletme) karıştırıcıyı **eledi**.

Aleyhte: (a) `ATR/fiyat` ile `stop_pct` büyük olasılıkla **çok yakın** —
o zaman bu, `genis_stop` ölçümünün (`t = −1,44`, düştü) yeniden
etiketlenmiş hâli olur ve aynı güç sorununa çarpar; (b) oynaklık bu projede
`vol_x` üzerinden bir kez negatif kontrolü **geçemedi**; (c) bugün **on iki
ön-kayıt yazıldı, on ikisi de düştü.**
