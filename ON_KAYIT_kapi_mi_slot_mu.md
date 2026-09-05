# ÖN-KAYIT — KAPI MI SEÇİYOR, SLOT MU ŞANSLI?

**Yazılma tarihi:** 2026-09-05 · **koşumdan ÖNCE yazıldı ve commit edildi**
**Kaynak:** kullanıcı (2026-09-05): *"tamam yap"* — bugün kaydedilen iki
çelişkinin çözümü.

---

## 1 · Çözülecek çelişki

Bugün **iki kez**, aynı şekilde:

| sentetik ölçüm (tüm evren) | karşı-olgu (kapılı + slot-kısıtlı) |
|---|---|
| *"BOĞA'da SHORT kaybettirir"* (−0,19 … −0,77) | `B` kolunun SHORT bacağı **+731 $** |
| *"yüksek `s_brk` = kötü"* (t=−2,39) | `C` kolu medyan `s_brk` **13,88** → **+1.162 $** |

İkisi aynı anda doğru olamaz. **İki açıklama var ve ayrılabilirler:**

```
(a) KAPILAR SECIYOR   -> stage/smart/long_veto gercek bilgi tasiyor;
                          sentetik orneklem her bari aldigi icin goremiyor
(b) SLOT SANSI        -> 171 karardan yalniz 44'u pozisyona dondu ve seceni
                          VARIS SIRASI; alinanlar tesadufen iyi olabilir
```

## 2 · TASARIM — çelişkiyi ikiye bölen iki karşılaştırma

**Evren:** `C` kolunun ürettiği **171 LONG kararı** (NOTR mantığı, 08-19…09-02).

| # | karşılaştırma | neyi ayırır |
|---|---|---|
| **S1** | **alınan 44** vs **alınmayan 127** | **SLOT ŞANSI** — seçen şey varış sırasıysa iki grup aynı olmalı |
| **S2** | **kapılı 171** vs **eşleşmiş KAPISIZ kontrol** | **KAPI SEÇİMİ** — kapılar bilgi taşıyor mu |

**Kontrol tanımı (S2), önceden sabit:** her kapılı kararın **aynı arşiv
damgasında** (aynı radar turu) bulunan, NOTR mantığında **LONG kararı
ÜRETMEYEN** adaylar. Zaman eşleşmesi böylece **tam**; piyasa koşulu ortak.

**Mekanik üçünde de aynı** ve `etiket_karsiolgu.py`'den **çağrılır**:
A-stop (LONG aynası) · %10 hedef · 72s · maliyet %0,13 · fonlama · `asgari_stop %2`.
🔴 **S1 ve S2'de SLOT UYGULANMAZ** — her karar bir işlem sayılır. Slot etkisi
S1'in **ölçtüğü şey**; mekaniğe karıştırılmaz.

## 3 · ÖLÇÜ

**İşlem başına net%**, gün-kümeli t, **MDE zorunlu**.
Gün-ortalaması **ve** işlem-ortalaması ayrı yazılır (bugün üç kez ayrıştılar).

## 4 · GEÇME ÖLÇÜTLERİ — sonuç görüldükten sonra değiştirilmez

| # | ölçüt | eşik |
|---|---|---|
| **K1** 🔴 | **S2**: kapılı 171 − kontrol | **> 0** · gün-kümeli t ≥ **+2,0** |
| **K2** | **S1**: alınan 44 − alınmayan 127 | fark **MDE'nin altında** (slot şansı gösterilemiyor) |
| **K3** | kontrolün **mutlak** getirisi | raporlanır (sentetik ölçümlerle tutarlı mı) |

**YORUM TABLOSU — önceden sabit:**

| K1 | K2 | hüküm |
|---|---|---|
| geçti | geçti | 🟢 **KAPILAR SEÇİYOR** — karşı-olgu desteklenir, çelişki çözülür |
| geçti | düştü | ⚠️ ikisi de var: kapı seçiyor **ama** slot da şanslıydı → karşı-olgu **şişik** |
| düştü | geçti | 🔴 **kapılar seçmiyor** → `C`'nin sonucu gürültü; **NOTR modeli zayıflar** |
| düştü | düştü | 🔴 hiçbiri açıklamıyor → çelişki **çözülmedi**, başka sebep aranır |

🔴 **K2 bir "yokluk" testidir ve öyle raporlanacaktır:** fark MDE'nin
altındaysa *"slot şansı YOK"* değil **"slot şansı GÖSTERİLEMEDİ"** yazılır.

## 5 · ÇOKLU KARŞILAŞTIRMA

**Birincil: 1** (K1). K2 bir güvenlik denetimi, K3 betimleyici.
Eşik/parametre **taraması YASAK**; kapılar ve mekanik olduğu gibi kullanılır.

## 6 · BEKLENTİ — sonuç görülmeden yazıldı

**K1'in geçmesine ~%40 veriyorum.** Bugün skorun beş bileşeni de, fiyat
seviyesi de bilgi taşımadı; ama `stage` ve `smart` **hiç doğrudan
sınanmadı** — kapıların bilgi taşıdığı tek yer orası olabilir.

**Yönlü tahminler (tutmazsa aynen raporlanır):**

1. **S1'de görülür fark ÇIKMAYACAK** (K2 geçer) — varış sırasının getiriyle
   ilişkisi için bir mekanizma yok.
2. **Kontrolün mutlak getirisi NEGATİF** olacak — bugünkü sentetik ölçümlerle
   tutarlı (BOĞA'da geniş LONG evreni kaybediyordu).
3. **K1 geçse bile fark, `C`'nin +2,64%/işlemini AÇIKLAMAYA YETMEYECEK** —
   yani kapı etkisi gerçek olsa da bir kısmı açıklanmadan kalacak.
4. `C`'nin yüksek `s_brk`'ı ile `s_brk` ölçümünün çelişkisi **tam çözülmeyecek**;
   bu ölçüm kapı/slot ayrımını yapar, `s_brk`'ın yönünü **yeniden ölçmez**.

🔴 **Ve şimdiden:** K1 düşerse **NOTR modeli zayıflar** ve bunu aynen yazarım.
Bu ön-kayıt, savunduğum sonucu çürütebilecek biçimde kurulmuştur.

## 7 · Dokunulmayanlar

Bot · state · defterler · config · zamanlanmış görevler: **hiçbiri.**
Salt-okuma, veri indirme yok. Mekanik ve karar fonksiyonu **çağrılır**.
Betik: `scratchpad/kapi_mi_slot_mu.py` (**bu commit'ten SONRA**).
