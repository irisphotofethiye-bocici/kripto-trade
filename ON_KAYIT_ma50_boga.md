# ÖN-KAYIT — MA50+UCUZ KAPISI, BOĞA PENCERESİNDE: hâlâ çalışıyor mu?

**Yazılma tarihi:** 2026-09-05 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-05): *"ma50'yi en son ölçtüğün veriyle ölç,
21'i sonrası bugüne kadar olan. Bu ölçümü yapmış mıydın?"*
**Cevap: HAYIR.** MA50 kapısı 2 yıllık veride ve rejim kırılımında ölçüldü;
**08-21 → bugün penceresinde hiç ölçülmedi.** Holdout betiği yalnız
`A_funding` içindi.

---

## 1 · 🔑 NEDEN BU KAPI ÖLÇÜLEBİLİR, ÖTEKİ DEĞİLDİ

Önceki ölçüm (`ON_KAYIT_boga_holdout.md`) **kendi geçerlilik kapısında durdu**:
`radar_archive.ts` bir **döngü damgası** (aynı dakikaya 50 sembol), dakika
düzeyinde hizalama yapısal olarak imkânsız.

**MA50+ucuz kapısının İKİ girdisi de yalnızca MUMDAN hesaplanır:**

```
fiyat <= $0,07            <- kline kapanisi
ma50_mesafe >= %3,72      <- kline kapanisi / 50 barlik MA
```

🔑 **Arşive hiç ihtiyaç yok** → o hizalama sorunu **bu kapıda geçersiz.**
Arşiv yalnız **fonlama maliyeti** için kullanılır ve orada dakika hassasiyeti
gerekmez (fonlama 8 saatte bir ödenen, yavaş değişen bir orandır) —
ama bu **iddia edilmez, SINANIR** (bölüm 6).

## 2 · Kodun VADESİ GEÇMİŞ talimatı — bu ölçüm onu ifa eder

`kripto-config.json` → `_ma50_kapisi_not` (2026-08-11, kullanıcı kararı) kendi
sınırını yazıyor:

> *"SINIR: fiyat seviyesi bir COIN-TIPI vekilidir (ucuz = yüksek arz/yeni/
> spekülatif); **rejim değişince ilişki DÖNEBİLİR, boğada ucuz coinler öne
> geçebilir.** Ham fiyat eşiği zamanla kayar, **yeniden ölçülmeden
> bırakılmamalı.**"*

Boğaya **2026-08-21'de girildi** ve kapı yeniden ölçülmedi.
Bu, `squeeze_bonus` ile aynı sınıf: **kodun kendi yazdığı, vadesi gelmiş bir iş.**

⚠️ Ayrıca kapının orijinal gerekçesi (**+%0,84**) `olcumler.md`'de zaten
*"dayanağı çürütüldü"* diye işaretli (2 yılda **−0,079 · t=−4,05**).

## 3 · KAPSAM — koşumdan ÖNCE sayıldı (`scratchpad/ma50_kapsam_sayim.py`)

```
perp_seri sembol (5dk -> 1sa)      151
  fiyati bir an <= $0,07 olan       88
pencere 2026-08-21 -> 2026-09-02   (72s ileri getiri icin kesme)

ucuz kapisini gecen bar            12.302
pump (>=%20) ile elenen             1.280
HAM tetik (iki kapi da)             3.125
soguma (24s) ile elenen            -2.797
>>> BAGIMSIZ OLAY                     328   (12 gun · 80 sembol)
```

Fonlama kapısının (55 olay) **altı katı.**

## 4 · 🔴 BİRİNCİL SORU: KAPININ KENDİSİ — stop genişliği DEĞİL

Bu oturumda stop genişliğine **üç kez** bakıldı. Dördüncü bir bakış
*"geçene kadar deneme"* olurdu. Bu yüzden birincil soru **başka**:

> **MA50+ucuz kapısı, bu boğada hâlâ kâr eden SHORT'lar seçiyor mu?**

Stop genişliği bu ön-kayıtta **ikincil ve BETİMLEYİCİ**dir; geçme ölçütü yoktur.

## 5 · EVREN, KOLLAR ve KONTROL

**Kural kolu:** `fiyat ≤ $0,07` **ve** `ma50_mesafe ≥ %3,72` → **SHORT**
**İki kontrol, ikisi de önceden ilan edildi:**

| kontrol | tanım | ne yalıtır |
|---|---|---|
| **K-dar** | `fiyat ≤ $0,07` ama `ma50_mesafe < %3,72` | **MA50 bacağını** — coin tipi sabit |
| **K-geniş** | hacim/pump süzgecini geçen **tüm** semboller | evrenin genel tabanı |

Üçü de aynı mekanik: **A-stop · sabit %10 hedef · 72s · maliyet %0,13 ·
fonlama dahil · giriş tetiğin ertesi barının açılışı · 24 saat soğuma.**
Mekanik `ileri_rr`'den **çağrılır**, yeniden yazılmaz.

## 6 · 🔴 ZORUNLU SINAMALAR — üçü de geçmeden koşmaz

| # | sınama | eşik |
|---|---|---|
| **S1** | merdiven monotonluğu (`A ≤ 1.5x ≤ 2.5x ≤ 4.0x`) | ihlal yok |
| **S2** | **fonlama oranının döngü-içi kararlılığı** — ardışık arşiv kayıtları (~7,5 dk) arasındaki `\|Δfunding\|` medyanı | **≤ %0,005** (kapı eşiğinin onda biri). Geçmezse damga bulanıklığı fonlamayı da bozuyordur ve fonlama **hariç** raporlanır |
| **S3** | 1 saate toplama doğruluğu — toplanan barın `h/l`'si, 5dk barların `h/l` uçlarına eşit | ihlal yok |

⚠️ **S2 düşerse ölçüm DURMAZ**, fonlamasız koşar ve bu **hükümde yazılır.**
Önceki ölçümdeki gibi tam durdurma burada gerekmiyor çünkü **kapı arşive
bağlı değil** — yalnız maliyet kalemi bağlı.

## 7 · ÖLÇÜ — ve neden bu sefer `net%` birincil

| ölçü | rol | gerekçe |
|---|---|---|
| **`net%`** | 🔴 **BİRİNCİL** | kapının kayıtlı gerekçesi `+%0,84` **net%** cinsinden; doğrudan kıyaslanabilir olmalı |
| `R` | ikincil, hep yazılır | portföy anlamı (risk-bazlı boyut) |

⚠️ **Bu bir ölçü değiştirme DEĞİLDİR.** Stop-genişliği ölçümlerinde `R` birincildi
çünkü **kolların boyutu farklıydı**. Burada kural ve kontrol **aynı mekaniği**
kullanıyor; manipüle edilen değişken stop değil **kapı**. İki durumda doğru ölçü
farklıdır ve gerekçe **koşumdan önce** yazılmıştır.

## 8 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

| # | ölçüt | eşik |
|---|---|---|
| **K1** 🔴 | kapı `net%` − **K-dar** `net%` | **> 0** · gün-kümeli t ≥ **+2,0** |
| **K2** | kapının **mutlak** `net%`'i | **> 0** (ayırıp para kaybeden kapı kullanılamaz) |
| **K3** | **K-geniş**'e karşı da aynı işaret | evet |
| **K4** | güç: `\|fark\| ≥ MDE` | evet, aksi **"göremiyoruz"** |

**GEÇTİ** = dördü · **AYIRIYOR AMA KAZANDIRMIYOR** = K1+K3 var, K2 düştü ·
**DÜŞTÜ** = K1 düştü.

🔴 **K2 kritik:** kayıtlı gerekçe *"bu kapı +%0,84 kazandırıyor"* idi. Kapı
kontrolü geçse bile **mutlak olarak zarardaysa** o gerekçe ayakta değildir.

## 9 · ÇOKLU KARŞILAŞTIRMA

**Birincil: 1** (kapı vs K-dar, `net%`). K-geniş bir **teyit**, ayrı hipotez değil.
İkincil ve hüküm taşımaz: `R` · stop genişliği dört kolu · fiyat dilimleri ·
`ma50_mesafe` dilimleri. **Eşik taraması YASAK** — `$0,07` ve `%3,72`
config'ten alınır, **oynatılmaz.**

## 10 · BEKLENTİ — sonuç görülmeden yazıldı

**K1+K2'nin birlikte geçmesine ~%20 veriyorum.**

**Yönlü tahminler (tutmazsa aynen raporlanır):**

1. **Kapının mutlak `net%`'i NEGATİF çıkacak** (K2 düşecek) — boğada ucuz
   coinleri short'lamak, config'in kendi uyarısının tam hedefi.
2. **K-dar kontrolü de negatif çıkacak** — yani zarar kapıdan değil, **boğada
   short olmaktan** gelecek. Bu ikisini ayırmak bu ölçümün asıl işi.
3. Kapı, K-dar'ı **t ≥ +2,0 ile geçemeyecek** (12 gün, düşük güç).
4. **Stop genişletme bu kapıda fonlama kapısındakinden ZAYIF** kalacak —
   2 yıllık BOĞA dilimi bu kapı için **negatif** demişti (−0,0447).

## 11 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
**Veri indirme YOK.** `radar_archive` context'e yüklenmez.
Betik: `scratchpad/ma50_boga.py` (**bu commit'ten SONRA**).

---

## 🔴 [DEĞİŞTİ 2026-09-05] — aynı ölçüt, DAHA GENİŞ kapsam

İlk koşum `perp_seri`'nin **151** sembolüyle yapıldı ve **K4 açıkça
"GÖREMİYORUZ"** dedi (`|fark| 0,5461 < MDE 0,9501`). Yani hüküm güçle sınırlıydı.

Kullanıcı onayıyla taze mum indirildi; aynı ölçüm **~566 sembolle** yeniden
koşuyor. **Bölüm 8'deki K1–K4 değiştirilmemiştir**; eşikler (`$0,07` · `%3,72`)
config'ten gelir ve oynatılmamıştır.

🔴 **İKİ KOŞUM DA RAPORLANIR.** Güç arttığı için hüküm değişebilir; hangisi
çıkarsa çıksın **ikisi yan yana** yazılacaktır — sadece iyi olanı seçmek
bu projede reddedilmiş davranıştır.
