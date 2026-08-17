# kripto trade — çalışma kuralları

Bu dosya her oturumda otomatik yüklenir. Amacı, 45 günde pahalıya öğrenilen kuralların
sıkıştırma (compaction) ile kaybolmasını engellemek.

---

## SERT KISITLAR — istisnasız

- **Bot KÂĞIT ÜSTÜNDE çalışır.** Gerçek emir gönderen kod YOKTUR ve eklenmez.
- **İzinsiz `git push` YOK.** Depo bugüne kadar hiç push edilmedi. İlk push'tan
  **önce** git geçmişi temizlenmeli (geçmişte ~920 MB veri var, `.git` ~242 MB).
- **`kripto-config.json` ve `kripto_portfoy.json` asla commit edilmez.** İçlerinde
  CoinGecko/Telegram/Apify/Coinalyze anahtarları var. `.gitignore`'da kalırlar.
- **`.gitignore`'a satır-içi yorum yazma.** Kalıbı bozuyor (`dosya.json  # not` çalışmaz).
- **Geri alınamaz / dışa açılan adımlar önce onaya sunulur.** Ücretli çağrı, push,
  paylaşım, silme.

## YÖNTEM — ölçmeden kural çıkarılmaz

- **Ön-kayıt koşturmadan ÖNCE yazılır ve commit edilir.** Hipotez + geçme ölçütü +
  beklenti. Sonucu gördükten sonra ölçüt değiştirilmez.
- **Kontrol grubu zorunlu.** "Kural kârlı" yetmez; kontrolü geçmeli.
- **Fonlama (funding) maliyeti dahil edilir.** A+B kapısında kenarın **%83'ünü**
  fonlama yedi; hariç tutulan her ölçüm yanıltıcıdır.
- **En iyi hücre seçilmez.** Tabloya bakıp en yüksek sayıyı kural yapmak bu projede
  reddedilmiş bir davranıştır (bkz. erken müdahale, `olcumler.md`).
- **Çoklu karşılaştırma sayılır.** Çok sütun + az satır = sahte bulgu garantisi.
- **Başarısızlık aynen raporlanır.** Bugüne kadar denenen çıkış kurallarının hepsi
  kârı düşürdü; bunu yumuşatmak projenin değerini yok eder.
- **Tekrarlayan bulgu:** *kötü girişte sıkı çıkış kaybı keser, iyi girişte kazancı
  keser.* Yeni bir çıkış kuralı önerirken önce buna bak.

## MİMARİ TUZAKLAR — üçü de gerçekten ısırdı

- **`yeni_giris_ac` dört defter tarafından çağrılır** (`testbot`, `golge`, `benim`,
  `ayna`). Bu fonksiyona yan etki (bildirim, aynalama, log) eklerken
  **`_DEFTER is not None` koruması şart.** Bu hata sınıfı **üç kez** yaşandı:
  ayna sızıntısı · Telegram'dan sahte giriş mesajı · gölge girişlerinin aynaya düşmesi.
- **Durum dosyaları ATOMİK yazılır** (`.tmp` + `os.replace`). Gölge defterin düz
  `json.dump`'ı 2026-08-11'de defteri **314 $** saptırdı.
- **Ölçüm bota dokunmaz.** Ayrı süreç, ayrı dosya, salt-okunur. `testbot._DEFTER`
  ile oynanmaz.
- **Etkin kasa ≠ realize kasa.** Açık pozisyon varken yalnız `equity`'ye bakmak
  yanlış sonuç verir; bu hata **iki kez** yapıldı (fren hatası + ayna kıyası).
- **Kazanma oranı POZİSYON başına sayılır, kayıt başına değil.** Kısmi kâr kayıtları
  pozisyonu böler.
- **Kilit dosyaları süresini ilan eder.** Uzun iş kilidi 4 dakikada bayat sayılırsa
  ikinci süreç kilidi çalar ve iki tur aynı durum üzerinde koşar.
- **`kismi_kar_r = 0` KAPATMA ANLAMINA GELMEZ — TERSİNİ yapar.** SHORT'ta
  `tp_r = giriş − 0×risk = giriş` olur; [testbot.py:888](testbot.py#L888)
  `max(yapısal, tp_r)` girişin kendisini seçer ve **TP1 anında tetiklenir.**
  Doğru kapatma kod tarafında: `tp1_efektif_hesapla` çağrısı
  ([testbot.py:933](testbot.py#L933) her turda, [:1145](testbot.py#L1145) girişte)
  `cikis_modu == "sabit_hedef"` pozisyonlarda atlanır. Ayrıntı `olcumler.md`.

## TEST YAZARKEN

**Sahte veriyle test ederken diske yazan HER yolu stub'la** — "güvenli fiyat seçmek"
yetmez. 2026-08-15'te sahte mum fiyatı `1.0` gerçek stop eşiğine (`0.01`) çarptı ve
`pozisyon_kapat` deftere **7 sahte likidasyon** yazdı. Aynı tuzağa ayna testinde de
düşülmüştü. Stub'lanacaklar: `_append_jsonl` · `_save_state` · `pozisyon_kapat` ·
`pozisyon_liq` · `pozisyon_kismi_tp1` · `telegram_gonder`. Testin sonunda
"diske yazım: YOK" diye **doğrula**.

## DÖRT DEFTER — her biri tek değişkeni yalıtır

| defter | soru | dosya |
|---|---|---|
| `testbot` | Bot ne yaptı? (ölçünün temeli) | `testbot.py` |
| `golge` | Reddettiği girişlere girseydi? | `golge.py` |
| `benim` | Kararı kullanıcı verseydi? | `benim.py` |
| `ayna` | Bot girsin, çıkışa kullanıcı karar versin | `ayna.py` |

Uydu defterler `testbot._DEFTER`'i geçici olarak değiştirir ve `finally` ile eski
haline döndürür. Bu deseni bozma.

## BİLGİ NEREDE

| soru | dosya |
|---|---|
| Bunu daha önce ölçtük mü? | **`olcumler.md`** ← önce buraya bak |
| Şu an ne açık, ne bekliyor? | **`durum.md`** |
| O ölçümün gerekçesi neydi? | `fikir-defteri.md` (251 KB, kronolojik — satır no `olcumler.md`'de) |
| Sistemde hangi hatalar bulundu? | `denetim-raporu.md` |
| Canlıya geçmeden ne kapanmalı? | `memory/canliya-gecis-kontrol-listesi.md` |
| Bileşenler ne işe yarar? | `README.md` |
| Ölçüm betikleri | `scratchpad/*.py` (59 dosya) |

`fikir-defteri.md` bir **laboratuvar defteridir**; kronolojisi kanıtın kendisidir
("o gün neye inanıyorduk"). Yeniden yapılandırma, konuya bölme, özetleyip kısaltma
**yapılmaz** — yalnızca sonuna eklenir.

## BAKIM KURALI — bu dosyanın işe yaraması buna bağlı

- **Ölçüm bitince** `olcumler.md`'ye bir satır ekle (hipotez · tarih · N · hüküm ·
  betik · defter satırı).
- **Karar alınınca / pozisyon durumu değişince** `durum.md`'yi güncelle.
- **Yeni bir hata sınıfı ısırınca** buraya "MİMARİ TUZAKLAR"a bir madde ekle.

Güncellenmeyen indeks **yalan söyler** ve hiç olmamasından kötüdür.

## İLETİŞİM

Kullanıcı Türkçe yazıyor; yanıtlar Türkçe. Kod içi yorumlar da Türkçe (ASCII'ye
sadık — dosyalar Windows'ta düz kodlamayla açılıyor). Uydurma sayı yok: her rakam
ya dosyadan okunur ya ölçülür.
