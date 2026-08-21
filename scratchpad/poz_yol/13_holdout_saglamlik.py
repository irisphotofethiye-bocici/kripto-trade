#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HOLDOUT SAGLAMLIK — ters donen hukumler gercek mi, birkac sembol mu tasiyor?

12_holdout.py'de UC hukum isaret degistirdi. On-kayit "ters ise coktu" diyor
ve bu AYNEN raporlanacak. Ama hukmun YANINA saglamlik notu dusulmeli:
   - sembol yogunlasmasi (en iyi 3 sembol cikinca ne kalir)
   - gun yogunlasmasi (en iyi gun cikinca)
   - boga bacagi (08-19+) ayri
Bunlar olcutu GEVSETMEZ, hukmu GUCLENDIRIR/ZAYIFLATIR.

SALT OKUMA.
"""
import os, sys, collections, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import ileri_rr as ir                                           # noqa: E402
h = __import__("12_holdout")                                    # noqa: E402


def net_ozet(v):
    if not v:
        return 0, 0.0
    return len(v), sx.mean(x["net"] for x in v)


def analiz(ad, kayitlar, filtre, yon, trailing=False):
    out = []
    for x in kayitlar:
        if not filtre(x):
            continue
        r = h._oynat(x["b"], x["atrs"], x["si"], x["ft"], x["fr"], yon, trailing=trailing)
        if r:
            r["sym"] = x["sym"]
            out.append(r)
    if len(out) < 100:
        print("\n%s — N=%d yetersiz" % (ad, len(out)))
        return
    n, ort = net_ozet(out)
    print("\n%s   N=%d  ortalama %+.4f" % (ad, n, ort))
    # sembol yogunlasmasi
    g = collections.defaultdict(list)
    for r in out:
        g[r["sym"]].append(r["net"])
    katki = sorted(((sum(v), s, len(v)) for s, v in g.items()), reverse=True)
    top = sum(x[0] for x in katki[:3])
    print("   sembol: %d · en iyi 3 = %s" % (len(g), ", ".join("%s(%+.0f,N=%d)" % (s, k, n2) for k, s, n2 in katki[:3])))
    print("   toplam net %+.1f · en iyi 3'un payi %%%.0f" % (sum(x[0] for x in katki), 100 * top / sum(x[0] for x in katki) if sum(x[0] for x in katki) else 0))
    kalan = [r for r in out if r["sym"] not in {s for _, s, _ in katki[:3]}]
    print("   en iyi 3 sembol CIKINCA: N=%d ortalama %+.4f" % net_ozet(kalan))
    # gun yogunlasmasi
    gd = collections.defaultdict(list)
    for r in out:
        gd[r["gun"]].append(r["net"])
    gunler = sorted(((sx.mean(v), d, len(v)) for d, v in gd.items()), reverse=True)
    print("   gun: %s" % " · ".join("%s %+.2f(N=%d)" % (d, m, n2) for m, d, n2 in gunler))
    eniyi = gunler[0][1]
    kalan2 = [r for r in out if r["gun"] != eniyi]
    print("   en iyi gun (%s) CIKINCA: N=%d ortalama %+.4f" % ((eniyi,) + net_ozet(kalan2)))
    # boga oncesi / sonrasi
    once = [r for r in out if r["gun"] < "08-19"]
    sonra = [r for r in out if r["gun"] >= "08-19"]
    print("   boga ONCESI (08-11..18): N=%d %+.4f   ·   BOGA (08-19+): N=%d %+.4f"
          % (net_ozet(once) + net_ozet(sonra)))


if __name__ == "__main__":
    print("HOLDOUT SAGLAMLIK — ters donen hukumler")
    k = h.topla()
    print("aday: %d" % len(k))
    analiz("HUKUM 2 — funding <= -0,05 kapi kolu (2 yilda ZARARLI, holdout'ta ARTI)",
           k, lambda x: x["funding"] <= ir.FUND_ESIK, "SHORT")
    analiz("HUKUM 3 — chg24 >= %20 SHORT (2 yilda KOTU, holdout'ta ARTI)",
           k, lambda x: x["chg24"] >= ir.PUMP, "SHORT")
    analiz("HUKUM 4 — chg24 > %40 LONG takip eden (2 yilda +2,379, holdout'ta EKSI)",
           k, lambda x: x["chg24"] > 40.0, "LONG", True)
    analiz("HUKUM 1 — SHORT yigini (isaret TUTTU)",
           k, lambda x: (x["fiyat"] > ir.UCUZ_FIYAT and x["funding"] > ir.FUND_ESIK
                         and x["chg24"] < ir.PUMP), "SHORT")
    print("\nbot dosyalarina yazim: YOK")
