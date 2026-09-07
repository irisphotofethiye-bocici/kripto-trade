# ÖN-KAYIT — KÂR KİLİDİ, BOTUN ESKİ POZİSYONLARINDA

**Yazılma tarihi:** 2026-09-07 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"botun eski pozlarına uygulayabilir misin bunu"*
**Betik:** `scratchpad/kilit_gecmis/01_olcum.py`

---

## 1 · NE SORULUYOR

Kural (2026-09-07, kullanıcı kararı, `notrlong`'da **canlı**):

```
TETIK  kar = koyulan paranin %20'si  ->  fiyat = G x (1 + 0.20/k)
ALIM   pozisyonun %20'si kapanir
STOP   +%15 kara cekilir             ->  fiyat = G x (1 + 0.15/k)
```

Kapanmış pozisyona kural **uygulanamaz** — kapandılar. Ölçülebilen şey
**karşı-olgu**: bu kural yürürlükte olsaydı o pozisyonlar ne olurdu?

## 2 · 🔴 BU BİR HİPOTEZ TESTİ DEĞİL — SINIRLARI ÖNCE YAZIYORUM

- **Kural zaten uygulandı** (kullanıcı kararı). Bu ölçüm onu geri almaz;
  **bilgi** üretir.
- 🔴 **Karar veriyi ürettiği veriyle sınanıyor.** Bot bu 240 pozisyonu
  kendi kurallarıyla açtı; karşı-olgu **aynı** yollar üzerinde koşuyor.
  Bu **örneklem dışı bir kanıt değildir**.
- 🔴 Bu yüzden **hüküm "GEÇTİ/DÜŞTÜ" olmayacak.** Çıktı **betimleyici**:
  kaç pozisyon tetiklerdi, dolar farkı ne olurdu, dağılımı nasıl.
- **Kural buradan çıkarılmayacak, değiştirilmeyecek.** Hakem `PENCERE-3`.

## 3 · 🔴 SEÇİM YANLILIĞI — koşumdan ÖNCE ölçüldü ve ilan ediliyor

```
testbot_islemler.jsonl · 394 pozisyon
  TEK kayitli (kismi kar YOK) : 241   <- yeniden kurulabilir
  COK kayitli (kismi kar VAR) : 153   <- DISARIDA
```

🔴 **Dışarıda kalan 153, TP1'e ULAŞMIŞ olanlardır — yani KAZANANLAR.**
Kalan 240'ın **236'sı `STOP`** (%98). Yani karşı-olgu **kaybedene yanlı**
bir örneklemde koşuyor.

**Yönü de belli:** kilit yalnız fiyat `+%20 ROI`'ye varınca iş görür.
Kaybedenlerde çoğu zaman **hiç tetiklenmez** → ölçüm hem **faydayı** hem
**zararı** OLDUĞUNDAN KÜÇÜK gösterir. Sonuç bu yüzden *"etki küçük"*
çıkarsa bu **yanlılığın eseri olabilir** ve öyle yazılacaktır.

**Telafi:** 153'lük küme ayrıca **betimlenir** (TP1'e ulaştıklarına göre
kilit tetiği TP1'den önce mi geliyordu — kayıttan hesaplanabilir).

## 4 · ZORUNLU SINAMA — yeniden kurulan yol GERÇEĞİ üretmeli

Her pozisyon için 1m mumdan yol yeniden kurulur. **Kabul koşulları:**

```
(a) yeniden kurulan cikis SEBEBI defterdekiyle ayni
(b) yeniden kurulan cikis ANI defterdeki ts'ten +-10 dk icinde
(c) yeniden kurulan P&L defterdekinden +-%2 sapiyor
```

Üçünü birden geçmeyen pozisyon **DIŞLANIR** ve sayısı raporlanır.
🔴 Dışlanan oranı **%25'i aşarsa** ölçüm *"yeniden kurulamadı"* diye
raporlanır ve **karşı-olgu yayımlanmaz.**

**Stop nereden geliyor** (defterde `stop` alanı YOK):

```
sebep == STOP    ->  stop = cikis / (1 - slipaj)        (dogrudan)
diger            ->  stop = G x (1 - (net% / r) / 100)  (r'den turetilir)
```

⚠️ `giris_ts` de yok: `ts − tutma_saat` ile kestiriliyor ve `tutma_saat`
**0,1 saate yuvarlı** (±3 dk). Sınama (b) tam da bunu yakalamak için var.

## 5 · KARŞI-OLGU NASIL KOŞUYOR

Aynı 1m mumlar, aynı giriş, aynı orijinal stop. Bar bar:

```
1. bar dibi <= stop           -> STOP  (kilit alinmissa YENI stop)
2. bar tepesi >= tetik ve kilit alinmadi
                              -> %20 kapanir, stop +%15 kara CEKILIR
3. bar tepesi >= hedef        -> TP2
4. ufuk dolar                 -> ZAMAN
```

🔴 **Sıra `testbot`'un kendi bar döngüsüyle AYNI** (stop → tp1 → tp2);
ileri-bakış yok. Aynı barda ikisi de varsa **stop önce** (kötümser).
Maliyet `testbot` ile aynı: taker %0,045 · slipaj %0,02.

## 6 · RAPORLANACAKLAR — hepsi betimleyici

- Kaç pozisyon tetiklerdi (`N` ve `%`), kaldıraca göre kırılım
- Toplam dolar farkı · pozisyon başına ortalama · medyan
- **İyileşen / kötüleşen / değişmeyen** pozisyon sayısı
- 🔴 **Kilit yüzünden ERKEN ÇIKAN** pozisyonlar: kilit stopu tetiklendi ama
  orijinal stopla devam etseydi **hedefe varacaktı** — kuralın maliyeti budur
- Dışlanan pozisyon sayısı ve sebebi
- 153'lük kısmi kâr kümesinin betimlemesi (bölüm 3)

## 7 · NE YAPILMAZ

- Bota, state'e, defterlere **dokunulmaz** (salt-okuma)
- Eşik **aranmaz** — `%20 / %20 / %15` kullanıcı kararı, sabit
- Bu sonuçtan **kural çıkarılmaz, mevcut kural değiştirilmez**
- cp1254 koruma bloğu **zorunlu** · `pyflakes` `undefined name` = 0
- İndirilen mumlar **birleştirilir, ezilmez**; `.gitignore`'a **önce** yazılır

## 8 · BEKLENTİM — koşumdan önce

Kaybedene yanlı örneklemde **tetikleme oranı düşük** (~%15-25) ve **toplam
etki küçük** bekliyorum. İşaretine dair güçlü bir beklentim **yok**: kilit
kazananın bir kısmını erken alır (zarar) ama stopu kâra çeker (fayda);
hangisinin ağır bastığı bu örneklemde **görülemeyebilir**.

⚠️ Ve ne çıkarsa çıksın: 153 kazanan dışarıda olduğu için bu **kuralın
karnesi değildir.**
