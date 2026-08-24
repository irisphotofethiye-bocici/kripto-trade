#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RASTGELE CIKIS KONTROLU — tetikler rastgeleden iyi mi?

31_kesinlik.py: her tetikte cikmak +1,5..+1,9 puan kazandiriyor gorundu.
AMA kontrolu yok. Pozisyonlar ortalamada KOTU bittigi icin, HERHANGI bir
ara barda cikmak da pozitif gorunur.

Bu betik o kontrolu koyar:
   tetikte cikis  vs  RASTGELE barda cikis  vs  SABIT barda cikis
Ayni pozisyon kumesinde, ayni sayida cikis.

HUKUM YAZILMAZ. SALT OKUMA.
"""
import os, sys, statistics as sx, random

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ortak                                                    # noqa: E402
random.seed(7)


def hazirla():
    out = []
    for p in ortak.pozisyonlar(en_az_goruntu=12, zengin=True):
        s = p["seri"]
        pnl = [g.get("pnl_pct") for g in s]
        if any(x is None for x in pnl):
            continue
        out.append({"sym": p["sym"], "seri": s, "pnl": pnl, "sonuc": p["sonuc"]})
    return out


def deg(s, i, alan, geri=3):
    if i - geri < 0:
        return None
    a, b = s[i - geri].get(alan), s[i].get(alan)
    if a is None or b is None or a == 0:
        return None
    return (b - a) / abs(a) * 100


TETIK = [
    ("hacim15 >= +50%", lambda s, i: (deg(s, i, "hacim_15_usdt") or -999) >= 50),
    ("taker15 <= -10%", lambda s, i: (deg(s, i, "taker_15") or 999) <= -10),
    ("hacim>=+50 VE taker<=-10", lambda s, i: (deg(s, i, "hacim_15_usdt") or -999) >= 50
     and (deg(s, i, "taker_15") or 999) <= -10),
]

if __name__ == "__main__":
    P = hazirla()
    print("RASTGELE CIKIS KONTROLU — %d pozisyon" % len(P))
    print("olculen: TETIKTE cikis ile pozisyonun GERCEK sonu arasindaki fark (puan)")
    print("pozitif = tetikte cikmak daha iyiydi\n")
    print("%-28s %10s %12s %12s %12s"
          % ("cikis kurali", "cikis", "medyan fark", "RASTGELE", "kural-rast."))
    print("-" * 78)
    for ad, f in TETIK:
        tet, rast = [], []
        for p in P:
            s, pnl = p["seri"], p["pnl"]
            idx = [i for i in range(4, len(s) - 1) if f(s, i)]
            if not idx:
                continue
            for i in idx:
                tet.append(pnl[i] - pnl[-1])
            # AYNI SAYIDA rastgele bar, ayni pozisyondan
            aday = list(range(4, len(s) - 1))
            for i in random.sample(aday, min(len(idx), len(aday))):
                rast.append(pnl[i] - pnl[-1])
        if len(tet) < 50:
            continue
        mt, mr = sx.median(tet), sx.median(rast)
        print("%-28s %10d %+12.3f %+12.3f %+12.3f" % (ad, len(tet), mt, mr, mt - mr))
    print("\n%-28s %10s %12s" % ("SABIT BAR cikisi", "poz", "medyan fark"))
    print("-" * 52)
    for n in (6, 12, 24, 48):
        v = [p["pnl"][n] - p["pnl"][-1] for p in P if len(p["pnl"]) > n + 1]
        if len(v) >= 20:
            print("%-28s %10d %+12.3f" % ("%d. barda (%d dk) cik" % (n, n * 5), len(v), sx.median(v)))
    print("\n%-28s %10s %12s" % ("EN IYI MUMKUN (tepe)", "poz", "medyan fark"))
    v = [max(p["pnl"]) - p["pnl"][-1] for p in P]
    print("%-28s %10d %+12.3f" % ("tepede cikis (imkansiz)", len(v), sx.median(v)))
    print("\nHUKUM YAZILMADI.")
