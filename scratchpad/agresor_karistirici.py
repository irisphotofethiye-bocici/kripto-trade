#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AGRESOR BULGUSU GERCEK MI? — karistirici kontrolu (2026-08-13)

agresor_ilk_saat.py uc kapiyi da gecti (+105 $ / +130 $). AMA ayni kosuda
"omur boyu hacim" de neredeyse ayni farki verdi (+112 $). Iki bagimsiz olcunun
ayni cevabi vermesi genelde ortak bir KARISTIRICI demektir.

En guclu suphe: ilk_taker_60 girisTEN SONRAKI 60 dakikada olculuyor. O saatte fiyat
lehimize gittiyse agresor de lehimize gorunur — yani olcu, ILK SAATIN FIYAT
HAREKETININ baska bir ifadesi olabilir. erken_mudahale.py zaten "erken durum sonucu
haber veriyor" demisti; eger agresor bunun otesinde bilgi TASIMIYORSA yeni bir sey
yok.

TEST: ilk saatin fiyat getirisi SABITLENDIGINDE agresor hala ayiriyor mu?
  - ayni yonde hareket eden pozisyonlar kendi icinde ikiye bolunur
  - ayrica dogrudan iliski (korelasyon) raporlanir
Ek kontroller: kapi (A+B / MA50) ve tutma suresi dagilimi.

Salt-okunur.
"""
import json, os, sys, statistics as stx

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURA)
sys.path.insert(0, KOK)
import testbot

OZET = os.path.join(KOK, "pozisyon_ozet.jsonl")
YOLLAR = os.path.join(BURA, "poz_yollari.json")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def lehte(pay, yon):
    return None if pay is None else (pay if yon == "LONG" else 1.0 - pay)


def pearson(x, y):
    n = len(x)
    if n < 5:
        return None
    mx, my = stx.mean(x), stx.mean(y)
    ust = sum((a - mx) * (b - my) for a, b in zip(x, y))
    alt = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** 0.5
    return ust / alt if alt else None


def main():
    kay = [json.loads(l) for l in open(OZET, encoding="utf-8") if l.strip()]
    try:
        yollar = json.load(open(YOLLAR, encoding="utf-8"))
    except Exception:
        yollar = {}

    v = []
    for k in kay:
        if k.get("sonuc_usdt") is None or k.get("ilk_taker_60") is None:
            continue
        yol = yollar.get(str(k.get("id"))) or []
        if len(yol) < 60:
            continue
        g = k["giris"]
        isaret = 1 if k["yon"] == "LONG" else -1
        # ilk 60 dakikanin KAPANIS getirisi (yon duzeltilmis)
        ilk_getiri = (yol[59][4] - g) / g * 100 * isaret
        v.append({**k, "ilk_lehte": lehte(k["ilk_taker_60"], k["yon"]),
                  "ilk_getiri": ilk_getiri})

    print("=" * 92)
    print("KARISTIRICI KONTROLU — agresor, ilk saatin FIYATININ otesinde bilgi tasiyor mu?")
    print("=" * 92)
    print(f"kullanilabilir pozisyon: {len(v)} (1 saatten kisa yasayanlar ve yolu olmayanlar disarida)\n")

    print("### 1) DOGRUDAN ILISKI")
    for ad, a, b in (("ilk_lehte  <-> ilk saat getirisi",
                      [k["ilk_lehte"] for k in v], [k["ilk_getiri"] for k in v]),
                     ("ilk_lehte  <-> sonuc $",
                      [k["ilk_lehte"] for k in v], [k["sonuc_usdt"] for k in v]),
                     ("ilk getiri <-> sonuc $",
                      [k["ilk_getiri"] for k in v], [k["sonuc_usdt"] for k in v])):
        r = pearson(a, b)
        print(f"  {ad:36} r = {r:+.3f}" if r is not None else f"  {ad:36} —")
    print("  Ilk satir yuksekse olcu, fiyatin kendisinin baska bir ifadesidir.\n")

    print("### 2) ILK SAAT GETIRISI SABIT TUTULUNCA")
    print("  Ayni yonde baslamis pozisyonlar kendi ICINDE agresore gore ikiye boluniyor.")
    print(f"  {'alt kume':28}{'N':>4}{'lehte ort $':>13}{'aleyhte ort $':>15}{'FARK':>11}")
    print("  " + "-" * 88)
    farklar = []
    for ad, sec in (("ilk saat ARTIDA basladi", [k for k in v if k["ilk_getiri"] > 0]),
                    ("ilk saat EKSIDE basladi", [k for k in v if k["ilk_getiri"] <= 0])):
        if len(sec) < 8:
            print(f"  {ad:28}{len(sec):4d}  — yetersiz")
            continue
        med = stx.median(k["ilk_lehte"] for k in sec)
        ust = [k["sonuc_usdt"] for k in sec if k["ilk_lehte"] > med]
        alt = [k["sonuc_usdt"] for k in sec if k["ilk_lehte"] <= med]
        if not ust or not alt:
            continue
        f = stx.mean(ust) - stx.mean(alt)
        farklar.append(f)
        print(f"  {ad:28}{len(sec):4d}{stx.mean(ust):13.2f}{stx.mean(alt):15.2f}{f:+11.2f}")
    print()

    print("### 3) KAPI DAGILIMI (agresor sadece kapiyi mi temsil ediyor?)")
    med = stx.median(k["ilk_lehte"] for k in v)
    print(f"  {'kapi':16}{'lehte yari':>12}{'aleyhte yari':>14}")
    kapilar = sorted({k.get("kapi") or "?" for k in v})
    for kp in kapilar:
        u = sum(1 for k in v if k["ilk_lehte"] > med and (k.get("kapi") or "?") == kp)
        a = sum(1 for k in v if k["ilk_lehte"] <= med and (k.get("kapi") or "?") == kp)
        print(f"  {kp:16}{u:12d}{a:14d}")
    print()

    print("### 4) TUTMA SURESI (uzun yasayan kazanir — agresor bunun proxy'si mi?)")
    for ad, sec in (("lehte yari", [k for k in v if k["ilk_lehte"] > med]),
                    ("aleyhte yari", [k for k in v if k["ilk_lehte"] <= med])):
        t = [k.get("tutma_saat") or 0 for k in sec]
        print(f"  {ad:16} N={len(sec):3d}  ort tutma {stx.mean(t):6.2f} sa  "
              f"medyan {stx.median(t):6.2f} sa")
    r = pearson([k["ilk_lehte"] for k in v], [k.get("tutma_saat") or 0 for k in v])
    print(f"  ilk_lehte <-> tutma_saat  r = {r:+.3f}" if r is not None else "")
    print()

    print("=" * 92)
    if farklar and all(f > 0 for f in farklar):
        print("SONUC: fiyat sabitlendiginde de ayni yonde -> agresor EK BILGI tasiyor olabilir.")
    elif farklar and all(f < 0 for f in farklar):
        print("SONUC: fiyat sabitlendiginde ISARET TERSINE DONDU -> bulgu fiyatin yansimasi.")
    else:
        print("SONUC: alt kumelerde ISARET TUTARSIZ -> bagimsiz bir etki KANITLANAMADI.")


if __name__ == "__main__":
    main()
