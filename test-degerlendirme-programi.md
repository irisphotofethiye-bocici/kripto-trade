# TestBot 21 Temmuz Değerlendirme Programı

> **ÖN-KAYIT (2026-07-10):** Aşağıdaki kriterler test SONUÇLARI görülmeden sabitlendi ve kullanıcı onayıyla kilitlendi.
> Değerlendirme günü sonuca bakıp kriter değiştirmek YASAK — bu, overfitting'in rapor versiyonudur.
> Test penceresi: 2026-07-02 17:59 → 2026-07-21 17:59 (19 gün). Değerlendirme: 21 Tem akşamı veya 22 Tem.

## A. Veri Envanteri — hangi dosya hangi soruyu cevaplar

| Veri | Cevapladığı soru |
|---|---|
| `testbot_islemler.jsonl` (rejim_giriste etiketli) | Hangi rejimde hangi yön kazandı? Kazananların giriş-anı bağlamı (chg24/pos/skor/smart) kaybedenlerden farklı mı? |
| `testbot_state.json` (kumulatif_funding / kumulatif_giris_ucret) | Kâr GİRİŞ becerisinden mi FUNDING carry'den mi? (equity ayrıştırması; sayaçlar 2026-07-08'den beri akıyor) |
| `veto_log.jsonl` + `veto_analiz.py` | 4 veto kategorisi (long_veto/taker_soguma/blowoff/rr_veto) korudu mu, fırsat mı baltaladı? |
| `radar_archive.jsonl` erken:true + `erken_analiz.py` | Erken-kuşak LONG edge 2. ölçüm (boğa dönemi dahil; 1. ölçüm 07-10: N=82, medyan -3.55%) + pop-then-fade SHORT hipotezi |
| `kacirma_analiz.py --gun 11` | Test dönemi gainers kapsaması; tekrarlayan MISSED katmanı var mı? |
| `arsiv_analiz.py` | Skor-bucket × yön × rejim forward-return (testbot'tan bağımsız doğrulama) |
| `testbot_equity.jsonl` | Equity eğrisi + maksimum drawdown |
| `katip.py` + `kripto_portfoy.json` | Gerçek pozisyonlar (ZEC #9, CRCL #10) + tahmin karnesi hit-rate |
| `piyasa_yapisi_log.jsonl` | Test dönemi rejim çeşitliliği (K6 girdisi: tek rejim mi yaşandı?) |

## B. İnceleme Sırası (komutlarla)

1. **Mutabakat:** `python testbot.py --durum` → equity Δ = kapanan PnL + kısmi TP1 + funding + giriş ücretleri.
   Ayrıştırma yüzdesi hesapla: kârın % kaçı işlem edge'i, % kaçı funding carry?
2. **Rejim × yön karnesi:** `--durum` çıktısındaki tablo — hücre başına N / W / PnL. Etiketli (07-08+) ve BILINMIYOR ayrı okunur.
   Ek: kazanan vs kaybeden işlemlerin giriş-anı alanlarını karşılaştır (jsonl'den).
3. **Veto karnesi:** `python veto_analiz.py` — kategori başına KORUDU vs FIRSAT_KACTI + medyan forward + N.
4. **Erken-kuşak 2. ölçüm:** `python erken_analiz.py` — tespit-anı LONG (tümü / skor≥40 / skor<40) + pop-fade SHORT varyantı.
5. **Kaçırma kapsaması:** `python kacirma_analiz.py --top 10 --gun 11` — MISSED oranı + tekrarlayan sebep.
6. **Gerçek defter:** `python katip.py` — ZEC/CRCL sonuçları, tahmin hit-rate; izleme listesi hijyeni (çözülenleri geçmişe taşı).
7. **Karar matrisi (C) uygulanır** → sonuç raporu + verilen kararlar proje hafızasına dated kayıt.

## C. Karar Matrisi (ÖN-KAYITLI — 2026-07-10'da kilitlendi)

### K1. Bot gerçek mikro-paraya terfi eder mi?
**Kriter (üçü birden):**
1. Equity > $1000 (net kârlı bitiş), VE
2. Kapanan-işlem toplam R > 0 (funding carry HARİÇ gerçek giriş/çıkış edge'i var), VE
3. En az bir rejim×yön hücresi: N≥8 + pozitif PnL + winrate ≥%50.

**Sonuç:** Üçü sağlanırsa → SADECE kanıtlı hücre(ler)de, `trade_hesabi` kurallarıyla ($5 risk-önce, NET R/R≥2, kapı/veto aynen), her emir kullanıcı onaylı **gerçek-mikro pilot** (4-8 hafta). Sağlanmazsa → sanal tur 2.

### K2. Erken-kuşak testbot evrenine bağlanır mı? (07-10 ön-onaylı, ölçüm teyidi şart)
**Kriter:** 2. ölçümde tespit-anı LONG medyanı hâlâ negatifse LONG-yakalayıcı olarak BAĞLANMAZ.
Evren-genişletme (mevcut TÜM kapılardan geçme şartıyla) yalnız şu durumda etkinleşir:
(a) skor≥40 alt-grup +24h medyanı ≥ 0, VEYA (b) pop-fade SHORT medyanı ≥ +2% — ve ilgili N≥30.
**Sonuç:** Kriteri sağlayan varyant sanal turda etkinleşir; sağlanmazsa erken-kuşak alarm+ölçüm olarak kalır.

### K3. Herhangi bir veto gevşetilir mi?
**Kriter (üçü birden):** kategori N≥25, VE FIRSAT_KACTI medyan forward ≥ +5%, VE KORUDU oranı <%40.
**Sonuç:** Sağlanırsa o kategori için revizyon TASARISI yapılır (önce sanalda test edilir). Tek kriter bile eksikse DOKUNULMAZ.
Not: TAC vakası (N=1, +43%) tek başına HİÇBİR ŞEY kanıtlamaz — aynı veto RE/SLX/EPIC'te kurtarmıştı.

### K4. Ölçücü taze-pump stop düzeltmesi
**Kriter:** Koşulsuz (veri gerektirmeyen belgeli tasarım hatası — SKL vakası: swing dedektörü 3-bar teyit yüzünden
90 dakikalık retrace dibini göremeyip 1.5×ATR fallback'e düştü; trade_hesabi "ATR-artefaktı değil" ilkesiyle çelişki).
**Sonuç:** 21 Tem sonrası uygulanır: `olcucu.measure`'a "son N-bar dibi − 0.25×ATR" aday-invalidasyon; 1.5×ATR ile girişe yakın olanı seçilir.

### K5. Yeni sinyal boyutu (listing takvimi / 5dk ivme / emir defteri vb.) eklenir mi?
**Kriter:** kacirma raporunda MISSED ≥ 3/10 VE tekrarlayan sebep aynı (örn. hep yeni-listing).
**Sonuç:** Sağlanırsa SADECE o boşluğa dar çözüm tasarlanır; değilse hiçbir yeni sinyal eklenmez (07-10 kanıtı: mevcut tespit 8/10 görüyordu).

### K6. Test süresi / formatı
**Kriter:** K1 sağlanmadıysa VEYA test dönemi rejim çeşitliliği içermiyorsa (piyasa_yapisi_log + rejim etiketleri tek rejim gösteriyorsa).
**Sonuç:** Sanal tur 2 — K4 (+ varsa K2/K3 çıktıları) uygulanmış kodla yeni tam tur. Gerçek AYI dönemi görülmeden tam terfi verilmez ("ayıda çalışan sistem" tezi ancak ayıda kanıtlanır).

## D. Yürütücü Talimatı (değerlendirmeyi koşacak oturum/model için — 2026-07-10 eklendi)

Bu değerlendirmeyi güçlü model tasarladı; yürütmesi MEKANİKTİR, yargı gerektirmez:
1. B bölümündeki 7 komutu SIRAYLA koş, her çıktıyı kaydet.
2. C matrisindeki her kriteri çıktılardaki SAYILARLA karşılaştır — kriter metnini yorumlama, sayı eşiğini uygula.
3. Bir kriterin verisi eksik/belirsizse: o karar "VERİ YETERSİZ → varsayılan sonuç (değişiklik YOK)" olarak kaydedilir. Şüphede DAİMA statüko.
4. Kriterleri değiştirme, yeni kriter ekleme, "aslında şu da bakılmalı" deme — bunlar ön-kayıt ihlalidir.
5. Sonuç raporu + verilen kararları proje hafızasına dated olarak yaz; kullanıcıya K1-K6 tablosu halinde sun.
6. Uygulanacak değişiklikler (K4 kesin + kriter sağlayan K2/K3/K5): `fikir-defteri.md`'deki ilgili maddenin uygulama notlarını takip et — gerekçeler orada dondurulmuş, yeniden türetme.
7. Değişiklik uygulama disiplini: tek seferde TEK değişken, önce py_compile + mock test + canlı tek koşu, sonra commit; `fikir-defteri.md` "Uygulama disiplini" bölümü bağlayıcı.
8. **BUG İSTİSNASI (2026-07-10 eklendi):** Hata düzeltme ön-kayıt ihlali DEĞİLDİR — kod bariz yanlış davranıyorsa (çökme, yanlış hesap, veri bozulması) test sırasında bile düzeltilir; ama düzeltme DAVRANIŞI değiştirmemeli, TASARLANMIŞ davranışı geri getirmeli. Ayrım testi: "bu değişiklik botun hangi işlemi açacağını/kapatacağını değiştiriyor mu?" DEĞİŞTİRİYORSA strateji değişikliğidir → 21 Tem'i bekler; değiştirmiyorsa (log, mutabakat, çökme onarımı) bug-fix'tir → py_compile + mock test + tek canlı koşu doğrulamasıyla yapılır ve hafızaya not düşülür.
9. **DEĞİŞİKLİK PROTOKOLÜ (2026-07-10 eklendi):** Kriter/fikir değişikliği SADECE kullanıcının açık kararıyla olur ve şöyle kaydedilir: eski kriter SİLİNMEZ, yanına "[DEĞİŞTİ tarih: yeni değer — kullanıcı kararı, gerekçe]" eklenir. Böylece ön-kayıt izi korunur; "sonuca bakıp kriteri mi değiştirdik" sorusu her zaman denetlenebilir kalır. Model kriter değişikliği ÖNEREBİLİR ama kendi inisiyatifiyle UYGULAYAMAZ.

## E. Sonraki Aşama Haritası

- **K1 GEÇTİ →** "Gerçek-mikro pilot" fazı: bot sinyali + kanıtlı hücre + kullanıcı onaylı gerçek $5-risk emirleri (4-8 hafta). Veri katmanları (veto/erken/kaçırma/rejim-karne) aynen akmaya devam eder; pilot sonunda aynı ön-kayıt disipliniyle yeni değerlendirme.
- **K1 KALDI →** Sanal tur 2: iyileştirilmiş kod (K4 kesin; K2/K3 kriter sağlarsa), aynı ölçüm disiplini, tam tur.
- Her iki yolda da: bu doküman şablon olarak korunur; bir sonraki değerlendirmenin kriterleri de yine ÖNCEDEN yazılır.
