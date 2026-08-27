# ÖN-KAYIT — TabFM, KUTUNUN DIŞINDA (tam tarama, skorsuz)

**Yazıldı 2026-08-27, KOŞUMDAN ÖNCE.** Ölçütler bundan sonra değiştirilmez.

Kullanıcı: *"Radardan çektiğimiz veriyi skorlama olmadan TabFM'e verseydik ne
seçerdi, ne olurdu?"* → *"Kutunun dışını da test et."*

## NEDEN — dört ölçümün DÖRDÜ de kutunun içindeydi

```
RADAR (tam tarama)       medyan skor  9,5   min 0,0
ADAY ARSIVI (TabFM'e)    medyan skor 40,6   min 30,0
huni: tur basi 9-10 aday / ~142 taranan  =  %6,3
```

TabFM piyasanın **%94'ünü hiç görmedi.** `golge`/`defter2`/`defter3` de aynı
huniden geçiyor (aday arşiviyle eşleşme %99,8-%100). Bu yüzden dört düşüşün
hükmü *"model işe yaramaz"* değil, *"botun kısa listesinde iyileştirecek bir
şey bulamadı"* idi. **Kutunun dışı hiç ölçülmedi.**

## VERİ

```
kaynak   radar_archive.jsonl  —  TAM TARAMA (kod dogrulandi: radar.py:357
         kosulu ARSIVE GIRISI degil ZENGINLESTIRMEYI kapiliyor; arsivin
         %89,7'si score<30 + stage "izle")
tekil    53.929 (sembol,saat)  ·  441 sembol  ·  62 gun (06-24..08-26)
etiket   HAM +2 saat perp getirisi  (bugun olculen DOGRU ufuk)
kullan.  51.478 gozlem (%95,5) · 61 gun · gun basi medyan 997
test     >=100 gozlemli 59 gun, min 7 baglam gunu -> 52 TEST GUNU
```

Önceki ölçüme göre: **14 kat gözlem, 4 kat test günü.**

### GİRDİ ALANLARI (18) — `score` YOK

`price` · `comp` · `vol_x` · `pos` · `last1` · `last3` · `rel3` · `btc_chg3` ·
`btc_chg24` · `funding` · `oi24` · `oi3` · `mcap` · `float_oran` · `dip_yakit` ·
`ayrisma` · `stage` · `dusuk_float` + **yeniden üretilmiş rejim**

### DIŞLANANLAR — gerekçesiyle

| alan | neden |
|---|---|
| **`score`** | 🔴 kullanıcı şartı: *"skorlama olmadan"*. Model kendi birleşimini kurmalı. Ayrıca skor **seçim değişkeni** — dahil etmek kutuyu geri getirirdi |
| `top_ls`·`glob_ls`·`taker`·`smart` | **%24,7 dolu — GİZLİ SEÇİLİM.** Yalnız botun beğendikleri zenginleştiriliyor; *"alan dolu mu"* sorusu botun tercihini geri sızdırırdı |
| `chg24`·`erken`·`vol_x_gun` | %20,5-24,3, aynı sebep |
| arşivin `rejim` alanı | 🔴 **2026-07-22'de TANIM DEĞİŞTİRDİ** ve pencere o tarihi aşıyor (`CLAUDE.md`). Yerine BTC mumundan **yeniden üretilen** rejim konur |
| `sym` · `ts` | kimlik — ezberleme |

⚠️ `radar_bosluk.jsonl` (111 kayıt) okunur ve raporlanır — arşiv **noktasal**
veridir, eksik pencerede çalışıldığı fark edilmeyebilir (`CLAUDE.md`).

## BÖLME

Gün-bloklu ileri doğrulama, `min bağlam = 7 gün`, **ambargo: son bağlam günü
atılır** (önceki koşumlarla aynı).

🔴 **BAĞLAM ÖRNEKLEMİ ZORUNLU.** Bağlam 52. günde ~50.000 satıra çıkar; tam
bağlamla koşum günler sürer. **Bağlam 2.500 satıra rastgele indirilir**
(sabit tohum 20260827), `n_estimators = 8`.
Hesap: `2.500 × 0,02415 sn × 8 × 52 ≈ 7 saat`.
Bu seçim **yalnız süre bütçesine** göre, sonuç görülmeden yapıldı.

## ÖLÇÜTLER

| # | ölçüt | eşik |
|---|---|---|
| **D1** | rho(tahmin, ham +2s), gün-kümeli | rho>0 · **t ≥ 2,0** · **\|rho\| ≥ 0,03** |
| **D2** | 🔴 **SEPET: TabFM en iyi 10 − RASTGELE 10**, saatlik sepet, gün-kümeli eşleşmiş | **t ≥ 2,0** |
| **D3** | KARIŞTIRICI oynaklık: `ATR/fiyat` üçte-birlikleri | **üçünde de** aynı işaret |
| **D4** | KARIŞTIRICI rejim: BOĞA · AYI · NÖTR (yeniden üretilmiş) | **üçünde de** aynı işaret |
| **D5** | BETİMLEYİCİ: TabFM 10 vs BOT 10 (skora göre) vs TERS-SKOR 10 | raporlanır, **hükme girmez** |

**GEÇME = D1 + D2 + D3 + D4.**

### 🔴 D2 BU ÖLÇÜMÜN KALBİDİR

Bot bu pencerede para kaybetti. TabFM **sessiz coinleri** seçerse *"botu
geçmiş"* görünür — **hiçbir şey bulmadan**, çünkü hareketsiz kalmak kaybetmekten
iyidir. `RASTGELE 10` kontrolü olmadan *"kenar buldu"* ile *"işlem yapmadı"*
**ayırt edilemez.**

`D3` aynı tuzağın ikinci kapısı: etki yalnız düşük oynaklıkta varsa, model
kenar değil **hareketsizlik** seçiyor demektir.

📌 `D5`'te `BOT 10` **hükme girmez**: botun skoru bu arşivde ölçülmüş şekilde
ters çalışıyor (`rho = −0,643`), onu geçmek bedava ve sahte bir zafer olurdu.
Dürüst çıta `RASTGELE`'dir.

## ÇOKLU KARŞILAŞTIRMA

**5. TabFM karşılaştırması.** Öncekiler: aday havuzu `+24s` · testbot BOĞA ·
testbot NÖTR · beş defter havuzu · aday havuzu `+2s` — **hepsi düştü.**
Ufuk **SABİT `+2s`**; başka ufka bakılmayacak.

## BEKLENTİM — koşumdan önce

**D1 geçer, D3 düşer.**

Gerekçe: 51 bin gözlem ve 52 günle küçük bir sıralama kabiliyeti bile `t ≥ 2,0`
üretebilir. Ama `score < 30` bölgesi **sessiz coinlerdir** — hacim patlaması yok,
OI hareketi yok. Modelin orada bulacağı ayrım büyük ihtimalle **oynaklık
ayrımıdır**, yön değil. `D3` bunu yakalamalı.

**Yanılırsam** — dört ölçüt de geçerse — bu, TabFM'in ilk kez gerçek bir şey
bulması olur **ve yine hüküm değildir**: ileri zamanda ayrı bir defterle
sınanması gerekir (`defter3` gibi).

## BU ÖLÇÜMÜN CEVAPLAMADIĞI

- **Para kazandırır mı** — mekanik yok, stop yok, ücret ve **fonlama yok.**
- **Girilebilir mi** — spread/derinlik cezası yok. Model gerçekte giremeyeceğin
  coinleri seçebilir. (`min_vol_musd` tabanı var ama düşük.)
- Cevapladığı tek şey: **tam evrende sıralanabilir sinyal var mı.**

## GEÇMEZSE

Kurulum silinmez (kullanıcı kararı). Kayıt `olcumler.md`'ye yazılır ve
*"kutunun dışı da ölçüldü"* satırı eklenir — o zaman eleme **tam** olur.
