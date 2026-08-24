#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTLAK SEVIYE — "fark" degil, KOLLARIN KENDISI artida mi?

25_mekanik_asamasi.py iki ceyrek arasindaki FARKI olctu. Fark buyuk olabilir
ama IKI KOL DA zararda olabilir. Kullanabilirlik icin mutlak seviye gerekir.

Ayrica: yogunlasma kontrolu (en iyi 3 sembol cikinca) — bu oturumda dort
hukmu ceviren tek test.

⚠️ HUKUM YAZILMAZ (on-kayit + kullanici talimati). Sayi uretilir.
SALT OKUMA.
"""
import os, sys, collections, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
m = __import__("25_mekanik_asamasi")


def kol_ozet(v, yon):
    net = [x["m_" + yon]["net"] for x in v if x.get("m_" + yon)]
    if len(net) < 200:
        return None
    g = collections.defaultdict(list)
    for x in v:
        if x.get("m_" + yon):
            g[x["gun"]].append(x["m_" + yon]["net"])
    gun = [sx.mean(g[d]) for d in g if len(g[d]) >= 5]
    t = None
    if len(gun) >= 5:
        se = sx.stdev(gun) / len(gun) ** 0.5
        t = sx.mean(gun) / se if se else None
    tip = collections.Counter(x["m_" + yon]["tip"] for x in v if x.get("m_" + yon))
    return {"n": len(net), "ort": sx.mean(net), "gun_ort": sx.mean(gun) if gun else None,
            "t": t, "gun": len(gun),
            "stop_pct": 100 * tip.get("STOP", 0) / len(net),
            "hedef_pct": 100 * tip.get("HEDEF", 0) / len(net)}


if __name__ == "__main__":
    print("veri kuruluyor...")
    k = m.topla()
    for alan in ("pos",):
        for yon in ("SHORT", "LONG"):
            print("\n" + "=" * 104)
            print("MUTLAK SEVIYE — %s ceyrekleri · MEKANIK %s (net %%, maliyet+fonlama dahil)"
                  % (alan.upper(), yon))
            print("=" * 104)
            print("%-21s %26s %26s %12s" % ("pencere", "ALT ceyrek (dusuk pos)",
                                            "UST ceyrek (yuksek pos)", "TUM EVREN"))
            print("-" * 92)
            for ad, _, _ in m.PENCERE:
                alt, ust = m.ceyrek(k[ad], alan)
                if alt is None:
                    continue
                oa, ou = kol_ozet(alt, yon), kol_ozet(ust, yon)
                ot = kol_ozet(k[ad], yon)
                def g(o):
                    if not o:
                        return "-"
                    return "%+7.3f (t%+5.2f) stop%%%2.0f" % (o["gun_ort"], o["t"] or 0, o["stop_pct"])
                print("%-21s %26s %26s %12s"
                      % (ad, g(oa), g(ou), "%+.3f" % ot["gun_ort"] if ot else "-"))
            # YOGUNLASMA
            print("\n  YOGUNLASMA — UST ceyrekten en iyi 3 sembol cikinca")
            print("  %-21s %14s %14s" % ("pencere", "UST ceyrek", "3 sembol cik."))
            for ad, _, _ in m.PENCERE:
                alt, ust = m.ceyrek(k[ad], alan)
                if ust is None:
                    continue
                s = collections.defaultdict(float)
                for x in ust:
                    if x.get("m_" + yon):
                        s[x.get("sym", "?")] += x["m_" + yon]["net"]
                o1 = kol_ozet(ust, yon)
                print("  %-21s %14s %14s"
                      % (ad, "%+.3f" % o1["gun_ort"] if o1 else "-", "(sym alani yok)"))
                break
    print("\nHUKUM YAZILMADI.")
