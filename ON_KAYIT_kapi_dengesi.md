# ÖN-KAYIT — kapı sisteminin dengeli denetimi

**Yazılma tarihi:** 2026-08-30 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı — *"sadece kaybedenlere bakalım, neyi engelleseydik girmezdi veya
erken çıkardı... girişi engelleyen kısır kapı olmamalı, denge önemli."*

---

## 1 · Neden ve önceki başarısızlık

2026-08-30'da *"kazananı kaybedenden ne ayırıyor"* kapsamlı denendi, **çöktü**. Giriş
anında bilinen hiçbir alan ayırmadı. Tek ayırıcı görünen `notional` **geri çekildi** —
TP1 (kısmi kâr) durumu sabitlenince etki yok oldu; TP1 bir **sonuç** olduğu için ayrım
döngüseldi (`olcumler.md` → GERİ ÇEKME, `65043f6`).

Bu ön-kayıt **farklı bir soru** soruyor ve çıtası farklı: bir veto **kârlı olmak zorunda
değil**, negatif beklentili bir dilimi kaldırması yeterli. Projenin kendi hükmü bu yönü
destekliyor: *"negatif filtreler çalışıyor, pozitif seçiciler çalışmıyor."*

## 2 · 🔴 DENGE — bu ön-kaydın ekseni

Kapılar **tek tek değil, KÜME olarak** değerlendirilir. Gerekçe kayıtlı: `defter2`'nin
filtreleri bota eklenseydi botun 117 pozisyonunun **%100'ü** elenirdi (`CLAUDE.md`).
Tek tek geçen kapıları toplamak **kısır bir bot** üretir.

Denetim ayrıca **SİMETRİK**: yalnız *"hangi kapı eklensin"* değil, *"hangi mevcut kapı
kaldırılsın/gevşetilsin"* de sorulur.

## 3 · Veri

| kaynak | rol | kapsam |
|---|---|---|
| `testbot_aday_arsiv.jsonl` | birincil (31 alan) | 26.898 satır · 267 sembol · 08-04→08-30 |
| 5 defter (`testbot` `golge` `ayna` `defter2` `defter3`) | sonuç | eşleşen **1.234 pozisyon** (%85) |
| `golge` kaynak alanı | **kapı KALDIRMA doğal deneyi** | `blowoff` `long_veto` `taker_soguma` `btc_pay_freni` `stop_cok_dar` `onay_bekle` |
| `pozisyon_izleme.jsonl` | C kolu | yalnız `testbot`, 239 pozisyon |

Eşleştirme: pozisyon girişinden **önceki 30 dakika** içindeki en yakın aday kaydı
(ölçüldü: medyan gecikme 2,6 dk · %90 → 6,8 dk).

**Birim: POZİSYON** — kayıtlar `id` ile birleştirilir. **P&L toplarken süzgeç YOK.**
**Sonuç:** `(Σ sonuc_usdt + Σ funding_usdt) / notional × 100`.

⚠️ **Kullanılmayacak alanlar:** `float_oran` (%9 dolu) · `sonuc` (%2,2) ·
`ma50_mesafe` (%73 — kullanılırsa eksik oran raporlanır).
⚠️ `radar_archive.jsonl` **kullanılmaz** — `top_ls`/`smart`/`taker`/`chg24` orada
%20-25 dolu (gizli seçilim). Aday arşivinde aynı alanlar %98,5.
⚠️ `golge` kolunda N küçük (kaynak başına 11-45) — hüküm gücü sınırlı, aynen yazılır.

## 4 · Keşif / doğrulama ayrımı

```
KESIF      2026-08-04 .. 08-16   -> aday kapilar aranir, KUME BURADA SECILIR
DOGRULAMA  2026-08-17 .. 08-30   -> secilen kume DEGISTIRILMEDEN kosulur
```

🔴 **Doğrulama yarısında küme yeniden optimize EDİLMEZ.** Tek bir küme seçilir ve
olduğu gibi taşınır. Bugün çöken bulgunun eksik olan tek koruması budur.

## 5 · Aday koşullar — SABİT, sonradan eklenmez

**Tekrar edilmeyecekler (ölçülmüş):** `funding ≤ −0,05` · `MA50+ucuz` · `fiyat ≤ $0,07` ·
`chg24 ≥ %20` · `chg24 ≥ %40` · `pos ≥ 0,75` · `pos < 0,25` · `skor` · `top_ls − glob_ls`

**A kolu — EKLENECEK (13):** `vol_x` · `oi3` · `oi24` · `rel3` · `last1` · `last3` ·
`btc_chg3` · `taker` · `comp` · `dip_yakit` · `ayrisma` · `dusuk_float` · `stage`

**B kolu — KALDIRILACAK/gevşetilecek (7):** `blowoff` · `long_veto` · `btc_pay_freni` ·
`taker_soguma` · `stop_cok_dar` · `onay_bekle` · `skor ≥ 45` LONG kapısı

**C kolu — ERKEN ÇIKIŞ (4):** ilk 30 dk `pnl_pct` · ilk 30 dk `mae_pct` ·
ilk 30 dk artıda geçen süre oranı · `atr_canli/atr_giriste` (**oynaklık GENİŞLEMESİ —
seviye değil değişim, hiç ölçülmedi**)

Sayısal alanlar çeyrek bantlarına bölünür; boolean'lar doğrudan.
**Toplam karşılaştırma: 13 + 7 + 4 = 24 aile.** Keşif eşiği gevşek (tarama),
doğrulama eşiği bunu telafi eder (aşağıda).

⚠️ C kolu bir **çıkış sıkılaştırmasıdır** ve bu projede sıkılaştıran
**28 varyantın 28'i de kalmıştır.** Prior kötü.

## 6 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

### Marjinal karne (tarama, keşif yarısı)
Bir kapı adayı **yol eğrisine girmeye hak kazanır** ise: engellenen dilimin işlem
başı neti **< 0** ve gün-kümeli **t ≤ −1,5**. (Gevşek — bu bir eleme değil, sıralama.)

### Yol eğrisi ve küme seçimi (keşif yarısı)
Hak kazanan kapılar etkiye göre sıralanır, birer birer uygulanır. Her adımda
`(kalan işlem %, işlem başı net, TOPLAM dolar)` izlenir.
🔴 **DURMA: kalan işlem oranı %50'nin altına inerse durulur** (kullanıcı kararı).

### Kabul — ÜÇÜ BİRDEN, doğrulama yarısında
| # | ölçüt | eşik |
|---|---|---|
| **K1** | kısırlık tabanı | kalan pozisyon **≥ %50** |
| **K2** | çift iyileşme | işlem başı net **VE** toplam dolar, **ikisi de** iyileşmeli |
| **K3** | işaret tutarlılığı | doğrulama yarısında **aynı işaret** ve gün-kümeli t ≤ **−2,0** |

🔴 *"Engellenen dilim zararlı"* **tek başına yeterli değildir.** Kaldırdığı kazananlar
hesaba katılmadan hüküm yazılmaz. **Denge tam olarak budur.**

### Zorunlu kontroller (her ayakta kalan koşul için)
| # | kontrol |
|---|---|
| **Z1** | 🔑 **TP1 KONTROL KATMANI** — `TP1 alındı` sabitlenir; etki orada kaybolursa **bugünkü artefaktın aynısı → DÜŞER** |
| **Z2** | **şans** — küme işlemlerin %X'ini eliyorsa rastgele %X elemekle kıyaslanır (2000 permütasyon), p ≤ 0,05 |
| **Z3** | **oynaklık eşitliği** — elenen/kalan hücrelerde ATR/fiyat ve stop genişliği raporlanır; ayrışıyorsa güven mekanikten okunmaz |
| **Z4** | **defter kontrol katmanı** — etki ≥3/5 defterde aynı işaret |

### 🔴 YASAKLI ALANLAR (sonuç türetilmiş)
`kismi`/TP1 · `sebep` · `tutma_saat` · `r` · `roi_pct` · `sonuc_usdt` · ömrün
TAMAMINA ait `mfe_pct`/`mae_pct`/`tepe_pnl_pct`/`arti_dakika`.
(İlk 30 dakikaya ait olanlar **serbest** — karar penceresi içinde.)

## 7 · BEKLENTİ — sonuç görülmeden yazıldı

- **A kolu (yeni kapı) K1+K2+K3'ü geçme olasılığı ~%30.** Gerekçe: bu projede
  *"her yeni aday erken fiyat hareketinin başka bir ifadesi"* kuralı **beş kez**
  doğrulandı ve aday alanların çoğu fiyat/hacim türevi. En olası ölüm **Z1**'de.
- **B kolu (kapı kaldırma) bir şey bulma olasılığı ~%45** — daha yüksek, çünkü
  `skor ≥ 45` bugün zaten **ters** ölçüldü ve bu kol onu doğrudan sınıyor.
  ⚠️ Ama `golge` N'i küçük; "bulundu" desek bile güç zayıf olacak.
- **C kolu ~%20.** 28/28 sicili var.
- **Yönlü tahmin:** `skor ≥ 45` LONG kapısının **kaldırılması** en güçlü aday
  çıkacak. Tutmazsa aynen raporlanır.

## 8 · Dokunulmayanlar

Bot · state · defterler · zamanlanmış görevler · `kripto-config.json`: **hiçbiri.**
Ölçüm tamamen salt-okuma. Sonuç bir **öneridir**; uygulama kullanıcı kararıdır
(2026-08-30: *"bota direkt ekleme, sor önce"*).

⏸️ Botun kaderi ertelendi (*"şimdilik karar verme"*) — testbot koşmaya devam eder.

**Betikler:** `scratchpad/kapi_veri.py` · `kapi_karne.py` · `kapi_kume.py` ·
`kapi_erken_cikis.py` (bu commit'ten SONRA yazılır).
