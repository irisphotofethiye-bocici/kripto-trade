# ÖN-KAYIT — TabFM, BEŞ DEFTERİN HAVUZUNDA (kör test)

**Yazıldı 2026-08-26, KOŞUMDAN ÖNCE.** Ölçütler sabit.

Kullanıcı: *"diğer defterler ile kör test yapalım, evrende veya reddettiklerinde."*

## NEDEN — önceki iki ölçümün ortak zaafı N'DI

| ölçüm | N | test günü | sonuç |
|---|---|---|---|
| aday havuzu (dün) | 3.598 satır | 13 | düştü (bedavayı geçemedi) |
| testbot poz · BOĞA | 119 | 7 | düştü |
| testbot poz · NÖTR | 61 | 4 | düştü |

Son ikisinde **hiçbir şey kanıtlanamazdı** — N4 zaten toplam sayıların zıt
etkileri gizlediğini gösterdi (+728 / −655).

## HAVUZ

```
testbot   240 poz    golge  508    ayna 212    defter2 113    defter3 20
ortusme   ayna testbot'un %98'i (AYNI girisler, farkli cikis) -> TEKILLESTIRILIR
          golge testbot'tan %86 FARKLI -> gercek yeni evren
HAVUZ     801 tekil giris · 22 gun · >=15 girisli 15 gun (08-11..08-26)
```

Tekilleştirme anahtarı: `(sym, yon, giriş saati)`. Öncelik sırası
`testbot → golge → defter2 → defter3 → ayna`.

⚠️ **`golge` %74 `pump_long_tezi`, %26 gerçek ret.** Bu, "botun reddettikleri"
demek DEĞİL — `CLAUDE.md`'nin uyardığı ayrım. Ret alt kümesi **ayrıca**
raporlanır (aşağıda H5).

⚠️ **BOYUTLANDIRMA DEFTERLER ARASI FARKLI.** Dolar P&L kıyaslanamaz.
Etiket **pozisyon getirisi = net P&L / giriş marjini**. `r` alanı
KULLANILMAZ — kısmi kârı görmüyor (`CLAUDE.md`).
Çıkış kuralları `testbot·golge·defter2·defter3`'te **aynı**; `ayna` farklı ama
tekilleştirmede zaten düşüyor.

## BÖLME

Gün-bloklu ileri doğrulama. Test günü = **≥15 girişli 15 gün**, bağlam = o
günden önceki tüm havuz. Bağlam < 60 olan günler elenir (koşumdan önce).

## ÖLÇÜTLER

| # | ölçüt | eşik |
|---|---|---|
| **H1** | üst yarı − alt yarı, pozisyon getirisi | fark > 0 **ve** gün-kümeli t ≥ 2,0 |
| **H2** | ham +24s getiri ile gün-kümeli rho | rho > 0 ve t ≥ 2,0 |
| **H3** | TABAN: botun `skor`'u (işaret bağlamdan) — TabFM **her ikisinde** geçmeli | geçmeli |
| **H4** | KARIŞTIRICI: **yön** ve **oynaklık** ile ayrı ayrı ikiye böl — etki **DÖRT alt kümenin hepsinde** pozitif | dördü de |
| **H5** | alt küme: yalnız **gerçek ret** kayıtları (`golge`'nin %26'sı) — H1 işareti | raporlanır, hükme girmez |

🔴 **H4, N4'ün genişletilmiş hâli.** N4 bir koşumda +728/−655 bölünmesini
yakaladı; H4 aynı testi **iki eksende birden** yapar. *"İşaret uyuşsun"* değil,
**"etki her alt kümede AYAKTA KALSIN."**

**"Sınamaya değer" = H1 + H3 + H4.**

## ÇOKLU KARŞILAŞTIRMA — 3. PENCERE

Aynı model üzerinde **3. deneme** (aday havuzu · testbot-BOĞA+NÖTR · havuz).
İlk ikisi düştü. Burada geçse bile bu **tek başına bulgu değildir**; ileri
zamanda ayrı bir defterle sınanması gerekir.

## BEKLENTİM

**H1 geçebilir, H4 düşer.** Gerekçe: N4 zaten etkinin oynaklıkla işaret
değiştirdiğini gösterdi; N daha büyük olduğu için H1'in t'si yükselebilir ama
H4 bölünmeyi yine yakalar. Yanılırsam — dördü de pozitif çıkarsa — bu, bu
projede bir adayın karıştırıcı kapısını **ilk kez** geçmesi olur.
