#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AGRESOR DENGESI — kazananlarla kaybedenler GIRISTE farkli miydi? (2026-08-13)

ON-KAYIT (kosmadan once yazildi):
  HIPOTEZ  Pozisyonun ILK SAATINDE agresorun LEHIMIZE olmasi sonucla iliskilidir.
  OLCU     ilk_taker_60 = ilk 60 dakikada taker ALIS hacminin toplam hacme payi.
           YON DUZELTMESI SART: SHORT'ta lehte olan DUSUK pay. Duzeltilmis olcu
           lehte_taker = pay (LONG) · 1-pay (SHORT). 0.50 = denge.
  GECERLI  Yalnizca ilk_taker_60 KARAR ONCESI bilgidir (giris + 60 dk).
           son_taker_60 KIRLI: cikis saatindeki denge zaten sonucun kendisidir
           (stop yiyen pozisyonda agresor tabii ki aleyhte olur). Raporlanir ama
           KURAL CIKARILMAZ.
  BEKLENTI Zayif ya da sifir. Bu projede 13 cikis kurali olculdu, 13'u de getiriyi
           dusurdu. N=45 ile ayrica COK KUCUK — bulunan sey buyuk ihtimalle gurultu.
  KAPI     Karar icin sart: (a) N>=30, (b) etki tek yonlu, (c) ust/alt yari
           arasindaki fark ortalama islem sonucunun yariSINDAN buyuk, (d) hem
           tum ornekte hem 11 Agustos sonrasi ayni yonde. Dordu de saglanmazsa
           KURAL CIKARILMAZ — gozlem olarak yazilir.

Salt-okunur. Hicbir deftere yazmaz.
"""
import json, os, sys, statistics as stx

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURA)
sys.path.insert(0, KOK)
OZET = os.path.join(KOK, "pozisyon_ozet.jsonl")
ANKRAJ = "2026-08-11 12:48:31"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def lehte(pay, yon):
    """Yon duzeltmesi: SHORT'ta lehimize olan taker alisin DUSUK olmasi."""
    if pay is None:
        return None
    return pay if yon == "LONG" else 1.0 - pay


def yari_kiyas(v, alan, etiket):
    """Ustyari/altyari — esik SECILMEZ, medyandan bolunur (veri gozetleme riski dusuk)."""
    d = [k for k in v if k.get(alan) is not None and k.get("sonuc_usdt") is not None]
    if len(d) < 10:
        print(f"  {etiket:26} N={len(d)} — yetersiz, atlandi")
        return None
    med = stx.median(k[alan] for k in d)
    ust = [k for k in d if k[alan] > med]
    alt = [k for k in d if k[alan] <= med]
    out = []
    for ad, sec in (("lehte (medyan ustu)", ust), ("aleyhte (medyan alti)", alt)):
        kaz = sum(1 for k in sec if k["sonuc_usdt"] > 0)
        out.append((ad, len(sec), kaz / len(sec) * 100 if sec else 0,
                    stx.mean(k["sonuc_usdt"] for k in sec),
                    stx.median(k["sonuc_usdt"] for k in sec)))
    print(f"  {etiket}  (medyan esik {med:.4f}, N={len(d)})")
    print(f"    {'grup':24}{'N':>4}{'kazanan':>9}{'ort $':>11}{'medyan $':>11}")
    for ad, n, kz, ort, mdn in out:
        print(f"    {ad:24}{n:4d}{kz:8.0f}%{ort:11.2f}{mdn:11.2f}")
    fark = out[0][3] - out[1][3]
    print(f"    FARK (lehte - aleyhte): {fark:+.2f} $")
    return fark


def main():
    kay = [json.loads(l) for l in open(OZET, encoding="utf-8") if l.strip()]
    for k in kay:
        k["ilk_lehte"] = lehte(k.get("ilk_taker_60"), k.get("yon"))
        k["son_lehte"] = lehte(k.get("son_taker_60"), k.get("yon"))

    print("=" * 92)
    print("AGRESOR DENGESI — kazananlarla kaybedenler GIRISTE farkli miydi?")
    print("=" * 92)
    kapali = [k for k in kay if k.get("sonuc_usdt") is not None]
    yeni = [k for k in kapali if (k.get("giris_ts") or "") >= ANKRAJ]
    print(f"kapanmis pozisyon: {len(kapali)} · 11 Agustos sonrasi: {len(yeni)}")
    kaz = [k for k in kapali if k["sonuc_usdt"] > 0]
    print(f"kazanan {len(kaz)} · kaybeden {len(kapali)-len(kaz)} · "
          f"toplam {sum(k['sonuc_usdt'] for k in kapali):+.2f} $\n")

    print("### 1) SONUCA GORE ORTALAMA AGRESOR (yon duzeltilmis, 0.50 = denge)")
    print(f"  {'grup':16}{'N':>4}{'ilk saat':>12}{'cikis saati':>14}")
    for ad, sec in (("KAZANAN", kaz), ("KAYBEDEN", [k for k in kapali if k["sonuc_usdt"] <= 0])):
        a = [k["ilk_lehte"] for k in sec if k["ilk_lehte"] is not None]
        b = [k["son_lehte"] for k in sec if k["son_lehte"] is not None]
        print(f"  {ad:16}{len(sec):4d}{(stx.mean(a) if a else float('nan')):12.4f}"
              f"{(stx.mean(b) if b else float('nan')):14.4f}")
    print("  (cikis saati KIRLI: sonucun kendisini yansitir — kural cikarilmaz)\n")

    print("### 2) ILK SAAT AGRESORU -> SONUC   [karar oncesi bilgi]")
    f_tum = yari_kiyas(kapali, "ilk_lehte", "TUM ORNEK")
    print()
    f_yeni = yari_kiyas(yeni, "ilk_lehte", "11 AGUSTOS SONRASI")

    print("\n### 3) YAN OLCULER (kesif — karar icin degil)")
    for alan, ad in (("ilk_ort_islem_usdt", "ilk saat ort. islem boyu"),
                     ("hacim_usdt", "omur boyu hacim"),
                     ("ort_islem_usdt_omur", "omur boyu ort. islem boyu")):
        yari_kiyas(kapali, alan, ad)
        print()

    print("=" * 92)
    print("### KAPI DEGERLENDIRMESI")
    ort_islem = stx.mean(abs(k["sonuc_usdt"]) for k in kapali)
    n_ok = len([k for k in kapali if k["ilk_lehte"] is not None]) >= 30
    yon_ok = (f_tum is not None and f_yeni is not None and
              ((f_tum > 0) == (f_yeni > 0)))
    buyuk_ok = f_tum is not None and abs(f_tum) > ort_islem / 2
    print(f"  (a) N>=30                        : {'GECTI' if n_ok else 'KALDI'}")
    print(f"  (b,d) iki ornekte ayni yon       : {'GECTI' if yon_ok else 'KALDI'}"
          f"   (tum {f_tum:+.2f} · yeni {f_yeni:+.2f})" if f_tum is not None and f_yeni is not None
          else "  (b,d) yetersiz veri")
    print(f"  (c) fark > ort islem/2 ({ort_islem/2:.2f}$)  : "
          f"{'GECTI' if buyuk_ok else 'KALDI'}")
    print()
    print("  KARAR: " + ("KURAL ADAYI — ama once ON-KAYITLI ileriye donuk dogrulama"
                         if (n_ok and yon_ok and buyuk_ok) else
                         "KURAL CIKARILMADI — gozlem olarak kaydedilir"))


if __name__ == "__main__":
    main()
