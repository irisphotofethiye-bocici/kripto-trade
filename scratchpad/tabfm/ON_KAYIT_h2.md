# ÖN-KAYIT — TabFM, DOĞRU UFUKTA (+2 saat)

**Yazıldı 2026-08-26, KOŞUMDAN ÖNCE.** Ölçütler bundan sonra değiştirilmez.

Kullanıcı itirazı: *"TabFM'i test ederken 24 saat üzerinden değerlendirdin ama
bizim için eldeki veri 2,5 saatte en büyük etkiyi veriyor."*

## KUSUR — ölçüldü, doğrulandı

Üç TabFM ölçümünde de etiket **`+24 saat`** alındı. Botun gerçek karar ufku
bunun onda biri:

```
HAVUZ (816 tekil pozisyon)     medyan tutma  1,90 sa
  <= 1 sa kapanan  %37           <= 3 sa   %61
  <= 2 sa kapanan  %52           <= 24 sa  %97
STOP ile kapanan  N=755 (%93)  medyan 1,70 sa
TEPEYE SURE (onceki olcum)     medyan 1,59 sa · %45'i ILK SAATTE
```

**24 saatte pozisyonların %97'si çoktan kapanmış.** Ölçülen fiyat hareketinin
neredeyse tamamı pozisyon kapandıktan *sonra* gerçekleşiyor.

`olcumler.md` bu tuzağı başka bir bağlamda zaten yazmıştı:
*"Botun kapıları çok daha kısa ufukta çalışıyor; **o ufuk ölçülmedi**, bu sonuç
oraya taşınamaz."* Aynı uyarı bu ölçümlere de uyuyordu, kullanılmadı.

⚠️ **KUSUR YALNIZ HAM SİNYAL SORUSUNU ETKİLİYOR.** Para etiketi (`net/marjin`)
pozisyonun gerçek sonucudur, ufuk seçiminden bağımsızdır → `H1`'in düşmesi
ayakta kalır ve **yeniden koşulmaz.** (Kullanıcı kararı: kapsam yalnız ham
sinyal.)

## SORU

2026-08-25'te aday havuzunda `S1` geçmişti (`rho +0,1676 · t=+4,92`).
**O sonuç doğru ufukta ayakta kalıyor mu?** Kalmıyorsa *"TabFM ham sinyali
görüyor"* ifadesi geri çekilir.

---

## TASARIM İLKESİ — TEK DEĞİŞEN ŞEY UFUK

`+24s` koşumuyla **birebir aynı** kalanlar:

| sabit | değer |
|---|---|
| veri kümesi | `testbot_aday_arsiv.jsonl` → saatlik tekilleştirme |
| girdi alanları | aynı 23 alan (`ON_KAYIT.md`, `43b0785`) |
| bölme | gün-bloklu ileri doğrulama, `min bağlam = 7 gün` |
| **ambargo** | son bağlam günü atılır — **AYNEN KORUNUR** |
| test günleri | aynı 13 gün |
| **satır kümesi** | `+24s` koşumundakiyle **AYNI 3.598 satır** |
| model | TabFM regresyon, `n_estimators = 16` |
| ölçütler | `S1..S5`, eşikler dâhil aynı |

**TEK DEĞİŞEN:** `UFUK = 24` → `UFUK = 2`.

### İki tasarım kararının gerekçesi

🔴 **AMBARGO NEDEN KORUNUYOR.** `+2s`'te etiket örtüşmesi bir güne değil ~1
saate iner; ambargo teknik olarak gevşetilebilirdi. **Gevşetilmeyecek** —
gevşetilseydi iki şey birden değişirdi (ufuk *ve* bölme) ve farkın hangisinden
geldiği **ayrılamazdı.**

🔴 **SATIR KÜMESİ NEDEN KİLİTLENİYOR.** `+2s` etiketi daha az satır düşürür;
fazladan satır almak örneklem farkı yaratırdı. Birincil koşum `+24s`
koşumunun **tam olarak aynı satırlarında** yapılır. Genişletilmiş küme
**ikincil dayanıklılık kontrolü** olarak raporlanır, **hükme girmez.**

---

## ÖLÇÜTLER — `+24s` koşumuyla aynı

| # | ölçüt | eşik | `+24s` sonucu |
|---|---|---|---|
| **S1** | rho(tahmin, ham getiri), gün-kümeli | rho>0 ve **t ≥ 2,0** | GEÇTİ +0,1676 · t=+4,92 |
| **S2** | TabFM − `skor` (işaret bağlamdan), eşleşmiş | **t ≥ 2,0** | DÜŞTÜ +0,0552 · t=+1,48 |
| **S3** | TabFM − en iyi tek alan (alan+işaret bağlamdan) | **t ≥ 1,5** | GEÇTİ +0,1805 · t=+3,94 |
| **S4** | gün × ATR-üçtebirlik hücrelerinde pozitif oran | **≥ %60** | DÜŞTÜ %56,4 |
| **S5** | ilk / son test yarısında işaret aynı | aynı | GEÇTİ |

**GEÇME = S1..S5'in HEPSİ.**

### 🔴 YENİ KORUMA — TABAN GEÇERLİLİK KAPISI

Havuz ölçümünde `H3` *"geçti"* göründü ama tabanın kendi korelasyonu sıfırdan
ayırt edilemiyordu (`rho −0,0308 · p=0,39`) — taban rakip değil **para
atışıydı** ve "geçmek" anlamsızdı.

Bu koşumda `S2` ve `S3` tabanları **kullanılmadan önce sınanır**:

```
tabanin BAGLAM gunlerindeki kendi rho'su sifirdan ayirt edilemiyorsa
   -> ilgili olcut  GECTI degil, GECERSIZ (VOID)
   -> ve GECME kosulu SAGLANMAMIS sayilir
```

Bu kural ölçütü **yalnız sıkılaştırır**: bir *"geçti"*yi *"geçersiz"*e
çevirebilir, tersini **asla** yapamaz. Sonuç görülmeden yazılıyor.

---

## ÇOKLU KARŞILAŞTIRMA — SAYILIYOR

Bu **4. TabFM karşılaştırmasıdır**:

| # | ölçüm | sonuç |
|---|---|---|
| 1 | aday havuzu, `+24s` | düştü (S2 · S4) |
| 2 | testbot pozisyonları, BOĞA | düştü |
| 3 | testbot pozisyonları, NÖTR | düştü |
| 3b | beş defter havuzu | düştü (H1 · H4) |
| **4** | **aday havuzu, `+2s`** | **bu ölçüm** |

🔴 **UFUK BU KOŞUMDA DA SABİT.** `+2s` dışında hiçbir ufuk hükme giremez.
`1·2·3·4·6·12·24` saatlik eğri ayrıca basılır — ufkun etkisinin **şeklini**
görmek için — ama **BETİMLEYİCİ** etiketiyle yazılır ve hükümde kullanılmaz.

---

## BEKLENTİM — koşumdan önce

**`S1`'in zayıflamasını, `S2`'nin yine düşmesini bekliyorum.**

Gerekçe: `+24s`'te `S1` geçmiş ama `S2` (ters çevrilmiş skoru geçme) düşmüştü.
Ters skorun kenarı, skorun *"düşecekleri işaretlemesi"*nden geliyor ve bu
yavaş işleyen bir sinyal — `+2s`'te hem TabFM hem taban **birlikte** zayıflar.
Ayrıca girdi alanları **saatlik toplamlar**; 2 saatlik hareketi çözecek
çözünürlükte olmayabilirler.

**Yanılırsam** — `S1` `+2s`'te de güçlü çıkarsa — sinyal botun **gerçek karar
ufkunda** var demektir ve bu, ilk kez operasyonel olarak anlamlı bir TabFM
sonucu olur.

## SINIRLAR

- 13 test günü, tek pencere (08-11..08-24), **ayı verisi yok**.
- Etiket ham fiyat: **fonlama ve ücret dahil değil.**
- Aday havuzu **seçilmiş** evren (botun yüzeye çıkardıkları), tüm piyasa değil.
- `n_estimators=16` süre bütçesinden seçilmişti; 32 ile sonuç değişebilir.

## GEÇMEZSE

Kullanıcı kararı: **kurulum SİLİNMEZ**, karar sonra verilir (8,6 GB; yeniden
indirmesi ~7 saat sürmüştü, silme geri alınamaz).
Sonuç ne olursa olsun `olcumler.md`'ye yazılır ve `+24s` sonucuyla **yan yana**
konur — asıl bilgi ikisinin **farkındadır.**
