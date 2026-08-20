# ÖN-KAYIT — Majörlerde "hacim patlıyor, fiyat kımıldamıyor" izi

**Yazıldığı an:** 2026-08-21, koşumdan **önce**, sonuç görülmeden.
**Kural:** `CLAUDE.md` → ön-kayıt koşumdan önce yazılır ve commit edilir; ölçüt
sonradan değiştirilmez.

---

## Neden bu soru

Kullanıcı (2026-08-21): *"Majörlerde böyle bir patlamayı önceden okuyabilirsek
piyasanın o an ne yöne gideceğini tespit etme ihtimalimiz daha yüksek. Böyle bir
sıçrama olunca piyasa LONG'a döner ve biz SHORT'ta kalırız, squeeze'in içinde
kalırız."*

**Gözlem (19 Ağustos, ölçüldü — hipotezin kaynağı, kanıtı DEĞİL):**

```
15:30  BTC hacim  21,7 -> 538,1 M$  (25 KAT)   fiyat sadece %+0,71     <- IZ
       ETH hacim  14,6 -> 221,8 M$  (15 KAT)   fiyat        %+0,50
       ... 2,25 saat sikisma ...
18:15  BTC %+2,52 · ETH %+3,16                                          <- KIRILMA
```

Ve o kırılma sırasında altlarda **fiyat yukarı + OI aşağı** ölçüldü (−0,315),
taker alış payı kontrolün altında (0,488 vs 0,489) → yükselişi alıcılar değil
**kapanan shortlar** üretti. Bot tam o barın içinde SHORT açtı ve 12 dakikada
stop oldu.

⚠️ Bu **tek vaka**. Aşağıdaki ölçüm onu sınamak içindir, doğrulamak için değil.

## Hipotez

**H1 (oynaklık):** Majörde hacim patlayıp fiyat kımıldamadığında, sonraki
saatlerde **mutlak** hareket büyür.
**H2 (yön):** O izin **içindeki taker dengesi** (alış payı), hareketin **yönünü**
önceden söyler.

**Sıfır hipotezi:** ikisi de rastgele bir andan ayırt edilemez.

⚠️ **Beklentim:** H1 geçer (hacim–oynaklık ilişkisi neredeyse totolojik, bu bir
keşif değil). **H2'nin geçmeyeceğini bekliyorum** — yön bilgisi olsaydı bu
kadar basit bir izle uzun süre ayakta kalmazdı. Bu proje için değerli olan
H1'dir: *"bir hareket geliyor"* bilgisi, rejimle birleşince **hangi tarafta
durmamak gerektiğini** söyler.

## Veri

`scratchpad/major_5dk/BTC.json` · `ETH.json` — 5 dakikalık mum, **2 yıl**
(~210.000 bar). 5 dk mum kalıcıdır (doğrulandı: 2024-09-01 çekilebiliyor);
30 gün sınırı yalnız `futures/data` (OI, long/short) içindir.

Alanlar: `o h l c v qv n tbv tqv` — `tqv` = taker ALIŞ hacmi (USDT).

## İz tanımı — sonuçtan önce sabitlendi

```
pencere   : 3 bar (15 dk)
hacim_x   : pencere hacmi / onceki 24 barin (2 saat) ayni uzunluktaki ortalamasi
ATR       : 14 barlik, yuzde
IZ  ==  hacim_x >= 5,0   VE   |pencere getirisi| <= 0,5 x ATR
```

- Ardışık izler çakışmaz: bir iz bulununca sonraki **12 bar (60 dk)** atlanır.
- **Kontrol:** iz olmayan rastgele barlar, izlerden ≥60 dk uzak, iz sayısının
  2 katı.

## Ölçülecek

`t0` = izin son barı. İleri ufuklar: **+1 saat · +2 saat · +4 saat**.

| çıktı | test |
|---|---|
| `|ileri getiri|` (oynaklık) | H1 — iz vs kontrol |
| `ileri getiri` işaretli (yön) | H2 — iz içindeki `tqv/qv` yüksek olanlar vs düşük olanlar |

**Karşılaştırma sayısı:** 2 enstrüman × 3 ufuk × 2 hipotez = **12**.
Bonferroni: α=0,01 → `p < 0,000833`. Permütasyon **20.000** tur
(ulaşılabilir min p = 0,00005 → eşik ölçülebilir).

## Geçme ölçütü — sonuç görülmeden sabitlendi

Bir hipotez **geçer** ancak ve ancak:

1. Permütasyon `p < 0,000833`
2. **BTC ve ETH'de aynı işaret** (iki bağımsız enstrüman)
3. **Ay-kümeli:** 24 ayın **en az %60'ında** aynı yönde
4. **İki zaman yarısında da aynı işaret**
5. Etki büyüklüğü raporlanır, sadece p değil

Herhangi biri tutmazsa **"geçmedi"** yazılır.

## Karıştırıcı kontrolü — ZORUNLU

🔴 `CLAUDE.md`: monotonluk/anlamlılık tek başına yetmez. Bu proje aynı hatayı
iki kez yaptı (agresör dengesi 2026-08-17, son-yeni-uç 2026-08-19).

- **Saat dilimi:** iz belirli saatlerde mi yoğunlaşıyor (ABD açılışı, fonlama
  saati)? Saat sabitlendiğinde ayrım duruyor mu?
- **Oynaklık rejimi:** ATR dilimleri içinde de ayırıyor mu? (Yüksek ATR
  dönemlerinde hem iz hem hareket sık olur — sahte ilişki.)
- **Pencere-içi getiri:** iz tanımı `|getiri| ≤ 0,5×ATR` diyor ama bant içinde
  hâlâ değişiyor; dilimlenip kontrol edilir.
- 🔴 **H1 için özel:** `hacim_x` ile ileri oynaklık arasındaki ilişki, **iz
  koşulu olmadan da** ölçülür. İz, düz "yüksek hacim"den daha iyi değilse
  *"iz"* diye bir şey yoktur — sadece hacim vardır.

## Ne yapılmayacak

- Eşikler (5,0× · 0,5×ATR · 3 bar · 12 bar) sonuç görüldükten sonra
  **oynatılmayacak**.
- Geçmeyen bir hipotez için "şu alt kümede geçiyor" araması **yapılmayacak**.
- Sonuç ne olursa olsun **bota kural eklenmeyecek**; geçen bir iz ayrıca
  ileri zamanda sınanır.

## Bilinen sınırlar (baştan yazılıyor)

- 2 enstrüman = bağımsız gözlem az; ay-kümeli t bunu kısmen karşılar.
- 5 dk ızgara → daha hızlı izler görünmez.
- Bu ölçüm **girişe kural** üretmez; en fazla **maruziyet azaltma** (risk)
  kuralına dayanak olur — çünkü H2'nin geçmesini beklemiyorum.
