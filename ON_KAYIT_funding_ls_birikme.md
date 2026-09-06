# ÖN-KAYIT — FONLAMA ve LONG/SHORT BİRİKMESİ YÖN TAŞIYOR MU?

**Yazılma tarihi:** 2026-09-06 · **KOŞUMDAN ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-06): *"funding ve short long birikmesine de bakalım"*
**Betikler:** `scratchpad/fund_ls/01_mum_indir.py` · `02_olcum.py`

---

## 1 · SORU

`notrlong`'un LONG girişleri için **fonlama** ve **pozisyon birikmesi** ileri
getiriye bilgi taşıyor mu?

⚠️ **Fonlamanın SHORT tarafı ZATEN ölçüldü ve kullanılıyor:** A+B kapısı
`funding ≤ −0,05` + `oi24 ≥ %10` → SHORT, ölçüm `+0,259 R` (N=508,
`kripto-config.json → _ab_kapisi_not`). **LONG tarafı ölçülmedi.**
Bu ön-kayıt o boşluğu kapatır, A+B hükmüne dokunmaz.

## 2 · 🔴 GÜÇ ÖNCE — `taker` ön-kaydının hatası tekrarlanmıyor

`ON_KAYIT_taker_kapisi.md`'de etki tabanını **MDE'yi hesaplamadan** koydum ve
ölçüt daha yazıldığı anda geçilemezdi. Bu sefer güç **önce** hesaplandı:

| popülasyon | tanım | N | görülebilir `\|rho\|` |
|---|---|---|---|
| **P1 TAM** | tüm arşiv | 230.452 | **0,0058** |
| P2 GENİŞ | stage aktif + skor eşiği | 1.653 | 0,0689 |
| P3 DAR | botun tam hücresi (+ `smart==LONG`) | 956 | 0,0907 |

`top_ls`/`glob_ls` yalnız kısa listede var → P1'de N=57.354, `|rho| ≥ 0,0117`.

🔑 **Yalnız P1'de projenin standart etki tabanı (`|rho| ≥ 0,020`) uygulanabilir**
— ilk kez, çünkü MDE onun **altında**. P2/P3'te taban **MDE'nin kendisidir**
ve oralarda "boş" demek *"göremiyoruz"* demektir.

**Birincil popülasyon: P1.** P2/P3 karar-ilgisi için raporlanır, hüküm kurmaz.

## 3 · DEĞİŞKENLER

| değişken | ne | not |
|---|---|---|
| `funding` | fonlama oranı (%/8s) | ⚠️ **oran**, dolar değil (`CLAUDE.md` ad ayrımı) |
| `oi24` | 24s açık pozisyon değişimi % | **birikme** |
| `oi3` | 3s açık pozisyon değişimi % | **birikme, kısa** |
| `top_ls` | üst-trader pozisyon oranı | "akıllı para" duruşu |
| `glob_ls` | global hesap long/short oranı | kalabalığın duruşu |
| `top_ls − glob_ls` | **pozisyon kompozisyonu** | ⚠️ `CLAUDE.md`: bu **zaten ölçüldü, bulgu yok**; burada **kontrol** olarak var, yeni aday değil |

## 4 · SONUÇ DEĞİŞKENİ — MEKANİKTEN ARINIK

```
ret(h) = (close[t+h] / price[t] - 1) * 100      LONG isareti
ufuklar: +1s · +4s · +12s · +24s · +48s      BIRINCIL: +24s
```

🔴 Stop/hedef/maliyet **YOK**. `ham → mekanik → portföy` sırası. Ham geçmezse
mekaniğe geçilmez. Fiyat: `klines_1h_uzun` (2026-08-25'e kadar) **+** taze
indirme (`scratchpad/fund_ls/klines/`) — **eski dizin EZİLMEZ**.

⚠️ Zaman damgası hizası `02_olcum.py`'de doğrulandı: `radar_archive.ts`
**yereldir (UTC+3)**. Bu ölçüm de aynı `+3 sa` kaymasını uygular ve
**yeniden doğrular**; doğrulama düşerse betik çalışmayı reddeder.

## 5 · İSTATİSTİK

- **Birincil istatistik: Spearman rho** (ortalama farkından çok daha güçlü;
  `taker` ölçümünde ortalama farkın MDE'si 2,57 puandı — kullanılamaz).
- **Karıştırıcı kontrolü:** `last1` beşli dilimi **içinde** rho, dilimlerin
  N-ağırlıklı ortalaması. Ham rho ayrıca raporlanır.
- **Kararlılık:** zaman **iki yarıya** bölünür; **aynı işaret şart**.
  (Bu ölçüt `taker` kapısını da yakaladı: karşı-olgu penceresinde `+1,01`,
  öncesinde `−4,41`.)
- **Gün-kümeli:** medyan bölmeli ikili karşılaştırmanın gün-kümeli t'si.
- **MDE her hücrede raporlanır.**

## 6 · GEÇME ÖLÇÜTLERİ — koşumdan önce sabit

Bir değişken **"bilgi taşıyor"** sayılır ancak **hepsi** sağlanırsa:

| # | ölçüt | eşik |
|---|---|---|
| **G1** | P1'de `last1` sabitlenmiş `\|rho\|` (+24s) | **≥ 0,020** |
| **G2** | iki zaman yarısında **aynı işaret** | evet |
| **G3** | ufuk merdiveninde ≥3 basamak aynı işaret | evet |
| **G4** | gün-kümeli `\|t\|` (medyan bölme) | **≥ 2,0** |
| **G5** | negatif kontrolleri **geçmemiş** olması | evet |

```
BILGI TASIYOR   = G1..G5 hepsi -> AYRI bir on-kayitla MEKANIKLI olculur
BOS             = G1 duser
GOREMIYORUZ     = P2/P3'te esik altinda kalan her sey (MDE > taban)
```

🔴 **Bu bir TARAMADIR, kapı kararı DEĞİLDİR.** G1..G5'i geçen bir değişken
bile bota **eklenmez**; kendi ön-kaydıyla, mekanikle ve kontrol grubuyla
yeniden ölçülür. Bu ön-kayıt yalnız *"bakmaya değer mi"* sorusunu cevaplar.

## 7 · ÇOKLU KARŞILAŞTIRMA — sayıldı

```
6 degisken x 5 ufuk x 3 populasyon = 90 karsilastirma
```

**Birincil olan 6'dır:** P1 · +24s · `last1` sabitlenmiş, her değişken için bir.
Diğer 84 **ikincil**, tek başına hüküm kurmaz.

⚠️ 6 birincil karşılaştırmada, `α=0,05`'te **0,3 sahte pozitif** beklenir.
G2+G3+G4'ün birlikte istenmesi bunun asıl savunmasıdır — şans eseri geçen bir
değişkenin iki yarıda **da** aynı işareti ve merdivende 3 basamağı tutturması
zordur.

## 8 · NEGATİF KONTROLLER — ikisi birden

1. **`vol_x`** — yön avında (2026-08-10, 6.790 olay) `+0,03` ile **rastgele**
   ölçüldü. G1'i geçerse düzenek şüphelidir.
2. **Gün içi karıştırma** — `funding` değerleri **gün içinde rastgele
   permüte** edilir (yapı korunur, eşleşme bozulur). Bu sahte değişken G1'i
   geçerse ölçüm **çöpe atılır**.

🔴 **`taker` ön-kaydında negatif kontrolü TEK YÖNLÜ yazmıştım** (`≥ +0,30`) ve
`glob_ls` `−2,53` verdiği hâlde "geçti" sayıldı. **Bu sefer ölçüt ÇİFT
YÖNLÜDÜR:** `|rho| ≥ 0,020` → düşer.

## 9 · NE YAPILMAZ

- Bota, state'e, defterlere, görevlere **dokunulmaz** (salt-okuma)
- Ücretli çağrı **yok**
- `scratchpad/klines_1h_uzun/` **EZİLMEZ** — taze mumlar ayrı dizine
- En iyi hücre **seçilmez**; ölçüt sonuç görüldükten sonra **değişmez**
- Arşiv context'e **yüklenmez**
- cp1254 koruma bloğu **zorunlu**
- `rejim` alanı **okunmaz** (2026-07-22 tanım değişikliği tuzağı)

## 10 · BEKLENTİM — koşumdan önce, olasılıkla

| değişken | G1'i geçme olasılığım | gerekçe |
|---|---|---|
| `funding` | **%45** | SHORT tarafında ölçülmüş kenar var (`+0,259 R`); simetri ölçümü *"aynı koşullar LONG'da `−0,28..−0,34`"* demişti, **yani yön taşıyor** — ama o A+B kesişimiydi, tek başına fonlama değil |
| `oi24` | **%40** | A+B'nin ikinci bacağı; tek başına `+0,189 R` ölçüldü |
| `oi3` | %20 | kısa pencere, gürültülü |
| `top_ls` | %20 | `smart` etiketi 3/3 kaybetmişti |
| `glob_ls` | %15 | kalabalık ölçüsü, `taker` ölçümünde `−2,53` verdi ama dengesiz kollarla |
| `top_ls − glob_ls` | **%10** | `CLAUDE.md`: zaten ölçüldü, **bulgu yok** |

**En az birinin G1..G5'i geçmesine %55 veriyorum.** Ama geçse bile bu bir
**kapı değil**, ikinci bir ön-kaydın konusudur.

⚠️ Ve şu ihtimal açıkça yazılıyor: `funding`/`oi24` geçerse bu **yeni bilgi
olmayabilir** — ikisi de A+B kapısının bacakları, yani zaten bilinen bir
kenarın LONG aynası çıkabilir. O durumda hüküm *"yeni sinyal bulundu"* değil,
*"bilinen kenar iki yönlü"* olur.
