# ÖN-KAYIT — Sert hareketten ÖNCE kımıldayan bir değişken var mı?

**Yazıldığı an:** 2026-08-21, koşumdan **önce**, sonuç görülmeden.
**Kural:** `CLAUDE.md` → *"Ön-kayıt koşturmadan ÖNCE yazılır ve commit edilir.
Sonucu gördükten sonra ölçüt değiştirilmez."*

---

## Soru

Kullanıcı (2026-08-20): *"Sert düşüş ya da çıkış yapmadan biraz önce
öngörebilir miyiz?"*

## Hipotez

Bir sembolün fiyatı sert hareket etmeden önce, **fiyattan başka bir bantta**
(açık pozisyon, pozisyon kompozisyonu, taker dengesi) sistematik bir kımıldama olur.

**Sıfır hipotezi:** olmaz — sert hareketten önceki pencere, rastgele bir
pencereden ayırt edilemez.

---

## 🔴 Tasarım kararı: pencere hareketi İÇERMEZ

İlk denememde `[t−30dk, t_stop]` penceresini ölçtüm ve hacim %145 artmış çıktı.
**O bir öngörü değil, hareketin tarifiydi** — pencere hareketin kendisini
içeriyordu. Bu ön-kayıt onu düzeltir:

```
t0 = sert hareketin BASLADIGI bar
olcum penceresi = [t0 - 60dk , t0]        <- hareket DISARIDA
```

## Olay tanımı (sonuçtan önce sabitlendi)

- Veri: `scratchpad/perp_seri/` · 5 dakikalık ızgara · 74 sembol · 29 gün
- `ATR5m` = 14 barlık ATR
- **Olay:** `t0`'dan sonraki **6 bar (30 dk)** içindeki kümülatif getiri
  mutlak değerce `≥ 2,0 × ATR5m`
- Aynı sembolde ardışık olaylar **çakışmaz**: bir olay bulunduğunda sonraki
  12 bar (60 dk) atlanır
- **Yukarı ve aşağı olaylar AYRI ölçülür** (simetri varsayılmaz)

## Ölçülecek değişkenler — hepsi ORAN/DEĞİŞİM, ham seviye değil

`[t0−60dk, t0]` penceresindeki değişim:

1. `d_oi` — açık pozisyon değişimi %
2. `oi_fiyat_orani` — `d_oi / d_fiyat` (fiyat |Δ| > %0,05 iken)
3. `d_top_ls` — top trader pozisyon oranı değişimi
4. `d_glob_ls` — global hesap oranı değişimi
5. `top_eksi_glob` — seviye farkı (akıllı − kalabalık)
6. `d_taker_orani` — taker alış/satış oranı değişimi
7. `taker_orani` — seviye
8. `d_hacim` — 5 dk hacim değişimi %

**8 değişken × 2 yön = 16 karşılaştırma.** Çoklu karşılaştırma **sayılıyor**
(`CLAUDE.md`: *"Çok sütun + az satır = sahte bulgu garantisi"*).

## Kontrol grubu

Aynı sembolden, **olay olmayan** rastgele barlar (olay penceresinden en az 60 dk
uzak), olay sayısıyla **eşleştirilmiş** sayıda. Aynı sembol → sembol ve rejim
karıştırıcıları sabitlenir.

## Geçme ölçütü — sonuç görülmeden sabitlendi

Bir değişken **öncü sayılır** ancak ve ancak:

1. **Karıştırma (permütasyon) testi:** olay/kontrol etiketleri sembol içinde
   1.000 kez karıştırılır; gerçek medyan farkı, sahte dağılımın **%99,9375**
   yüzdeliğini aşmalı → `p < 0,000625` (Bonferroni, 16 karşılaştırma için α=0,01)
2. **İşaret iki zaman yarısında da aynı** (ilk ~14,5 gün / son ~14,5 gün)
3. **Gün-kümeli**: farkın işareti günlerin **en az %60'ında** aynı yönde
4. **Etki büyüklüğü raporlanır**, sadece p değil

Bu dördünden **herhangi biri** tutmazsa: **öncü YOK** diye yazılır.

## Beklenti (sonuç görülmeden)

**Hiçbir değişkenin geçmeyeceğini bekliyorum.** Gerekçe: `CLAUDE.md` →
*"Ölçtüğümüz her şey tek banttan türüyor"*; OI ve long/short o bandın dışında
ama **aynı işlemlerden** üretiliyor, ve bu projede 7 yeni iz denendi, 1'i kaldı,
o da bilinen bir şeyin tekrarıydı.

En yüksek ihtimali `d_oi` ve `oi_fiyat_orani`'na veriyorum (tasfiye vs yeni
konumlanma ayrımı mekanik olarak anlamlı), en düşüğünü `top_eksi_glob`'a
(`top_ls` bu projede zaten bir kez çöktü).

## Ne yapılmayacak

- Eşik (2,0×ATR, 30 dk, 60 dk) sonucu gördükten sonra **oynatılmayacak**.
- Geçemeyen değişkenler için "şu alt kümede geçiyor" araması **yapılmayacak**.
- Sonuç ne olursa olsun **bota kural eklenmeyecek** — bu bir keşif ölçümüdür,
  geçen bir iz ayrıca ileri zamanda sınanır.

## Bilinen sınırlar (baştan yazılıyor)

- Pencere 29 gün (Binance `futures/data` 30 gün tutuyor) → **ay-kümeli
  istatistik kullanılamaz**, gün-kümeli kullanılır.
- 74 sembol botun dokunduklarıdır → evren **botun seçimiyle** sınırlı;
  bu bir genel piyasa iddiası değildir.
- 5 dakikalık ızgara → daha hızlı öncüler (saniye-dakika) görünmez.
