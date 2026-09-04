# ÖN-KAYIT — `pos`'a göre KOŞULLU mekanik: kenar alınabilir mi?

**Yazılma tarihi:** 2026-09-04 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı talimatı (2026-09-04): *"bunun başka bir yolu olmalı,
mekaniği ayarlayalım pos'a göre."*

---

## 1 · Neden bu ölçüm — ve 30/30 duvarına cevap

Ölçüldü ve commit edildi (`olcumler.md` → *`pos<0.25` MEKANİK AŞAMASI*):

```
pos<0.25 ham 4 saat kenari  +%1,43  ->  MEKANIKLI  -%0,33   (korunan pay -%23)
cikis dagilimi: STOP %78 · TP1sonrasi %13 · TP2 %5 · medyan tutma 6,0 saat
                (pos>=0.25 icin: %65 · %18 · %15 · 3,0 saat)
```

**Kenar var, botun onu alacak mekaniği yok.** Kullanıcının önerisi: mekaniği
`pos`'a göre ayarla.

🔴 **DUVAR:** bu projede çıkış **sıkılaştıran 30 varyantın 30'u da kaldı**.
Yeni bir sıkılaştırma önerisi bu sayıya karşı savunma yapmak zorunda.

🔑 **SAVUNMA — ve bu gerçek bir fark:** o 30 varyant **koşulsuzdu**, herkese
uygulanıyordu. Bu ölçüm **koşullu** mekanik sınıyor: yalnız `pos<0.25`
diliminde, ve **ölçülmüş bir mekanizmaya** dayanarak (sekme 4 saat sürüyor,
TP2'ye ulaşma oranı üçte bir).
⚠️ Savunma **mazeret değildir**: koşulluluğun gerçekten fark yarattığı,
aşağıdaki **KOŞULSUZ KONTROL** ile sınanır. Fark yaratmıyorsa 31. varyant olur.

## 2 · AŞAMA 1 — TEŞHİS (betimleyici, hüküm taşımaz)

**Müdahalenin yönünü bu belirler**, ve iki ihtimal **zıt**:

| bulgu | anlamı | doğru müdahale |
|---|---|---|
| pozisyonlar sekmenin **İÇİNDE** stop oluyor | stop çok dar | **daha GENİŞ stop** |
| sekme **BİTTİKTEN sonra** stop oluyor | çıkış çok geç | **ERKEN çıkış** |

Ölçülecek (yalnız `pos<0.25`, mevcut mekanikle):
1. Stop tetiklenme **saatinin** dağılımı (1., 2., 3. … saat)
2. **MFE** — pozisyon ömrü boyunca ulaşılan azami lehte hareket, ve o hareketin
   **kaçıncı saatte** olduğu
3. Hiç artıya geçmeyenlerin oranı
4. TP1'e (1,5R) ulaşanların kaçı TP2'ye gidiyor

## 3 · AŞAMA 2 — VARYANTLAR (ön-kayıtta SABİT, dört tane)

Her varyant **yalnız `pos<0.25`** satırlarına uygulanır; diğerleri
**mevcut mekanikle** koşar. Hepsi ölçülmüş mekanizmadan türetildi:

| # | varyant | gerekçe (ölçülmüş) |
|---|---|---|
| **V1** | zaman stopu **48s → 6s** | sekme 4 saat sürüyor, medyan tutma 6 saat |
| **V2** | TP1'de **%100 çık** (%40 yerine) | TP2'ye ulaşma **%5** — kalan %60 bekletmek kaybettiriyor |
| **V3** | V1 + V2 | ikisinin bileşimi |
| **V4** | ilk stop **1,5×ATR → 2,5×ATR** (risk ve TP'ler yeniden ölçeklenir) | stop-olma **%91** — "sekme içinde kesiliyor" ihtimali |

⚠️ **V4 zıt yönde bir müdahaledir** (gevşetme). Bilerek kondu: Aşama 1 teşhisi
"stop çok dar" derse doğru cevap **budur**, ve bu projede geçen **tek** çıkış
varyantı da bir **gevşetmeydi**.

**Uygulama:** `seviyeler()` ve `oynat()` **kaynaktan çağrılır**, kopyalanmaz.
V1/V2 `oynat`'a parametre olarak geçer; V4 `seviyeler`'in döndürdüğü `sl`'yi
ölçekleyip `risk`/`tp1`/`tp2`'yi **aynı formül şekliyle** yeniden hesaplar.

## 4 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

🔴 **BİRİNCİL:** varyantın `pos<0.25` dilimindeki net getirisi, **mevcut
mekaniğin aynı dilimdeki** net getirisinden yüksek mi?
**Birim sembol-gün · gün-kümeli t · eşleşmiş** (aynı satırlar, farklı çıkış).

| # | ölçüt | eşik |
|---|---|---|
| **K1** | en iyi varyantın farkı | **> 0** ve eşleşmiş gün-kümeli t ≥ **+2,5** |
| **K2** | bölünmüş yarı | fark **A ve B yarısının ikisinde de > 0** |
| **K3** | 🔴 **KOŞULSUZ KONTROL** | aynı varyant **tüm satırlara** uygulandığında kazanç `pos<0.25` dilimindekinden **belirgin küçük** olmalı |
| **K4** | portföy-öncesi anlamlılık | fark ≥ **%0,5** (uygulanabilir büyüklük) |

**GEÇTİ** = K1+K2+K3+K4 · **ZAYIF** = K1+K2, K3 düştü · aksi **DÜŞTÜ**.

🔴 **K3 neden belirleyici:** varyant koşulsuz uygulandığında da aynı kazancı
veriyorsa, bulunan şey *"`pos`'a göre ayarlama"* değil, **sıradan bir çıkış
değişikliğidir** → 31. varyant olur ve 30/30 duvarına çarpar.

⚠️ **Çoklu karşılaştırma:** **4 varyant × 1 dilim = 4 sınama.** Eşik t bu
yüzden **+2,0 değil +2,5** seçildi (tek sınama olsaydı +2,0 olurdu).
Sayı önceden sabitlendi; beşinci varyant **eklenmeyecek**.

**Zorunlu ek rapor:** her varyant için çıkış sebebi dağılımı · medyan tutma ·
stop-olma · MDE · `pos≥0.25` dilimindeki etkisi (yan etki kontrolü).

## 5 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%30 veriyorum.** 30/30 duvarı ağır basıyor; ama koşulluluk
ve ölçülmüş mekanizma bunu kör bir sıkılaştırmadan ayırıyor.
**K3'ün (koşulsuz kontrol) geçmesine ~%40** — yani K1 geçse bile bulgunun
`pos`'a özgü olmama ihtimali ciddi.

**Yönlü tahminler (tutmazsa aynen raporlanır):**
1. Teşhis **"erken çıkış"** diyecek: MFE zirvesi ilk 4 saatte olacak ve
   stopların çoğu **4. saatten sonra** tetiklenecek.
2. **V2 (TP1'de tam çıkış)** en iyi varyant olacak — TP2 oranı %5 iken kalan
   %60'ı taşımak açık kayıp.
3. **V4 (geniş stop) düşecek** — stop-olma oranı düşer ama tutma süresi uzar
   ve dönüşü yer.

🔴 **Ve şimdiden:** K1+K3 geçse bile **kod değişmez.** Sırada **portföy
aşaması** (8 slot, marjin tavanı) ve **ikinci bir BOĞA epizodu** var.
Ayrıca koşullu mekanik, botun çıkış kodunu dallandırır — bakım maliyeti
ölçüme dahil değildir.

## 6 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
Salt-okuma, ücretli çağrı yok. Betik: `scratchpad/pos_kosullu_mekanik.py`
(bu commit'ten SONRA).
