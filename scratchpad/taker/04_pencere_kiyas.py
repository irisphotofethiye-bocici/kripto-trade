#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HAM GETIRI: 57 gunluk hucre vs KARSI-OLGUNUN 16 gunluk penceresi.

02_olcum.py'de hucrenin HER ufukta ham getirisi NEGATIF cikti (-0,2 .. -3,1).
Karsi-olgu C kolu ise ayni sinifta +2,932%/islem demisti. Ikisi CELISMEZ
(farkli mekanik) ama pencereler de FARKLI: C = 08-19..09-02 (16 gun),
benim hucrem = 07-03..09-06 (57 gun).

Bu betik yalniz sunu sorar: karsi-olgunun penceresi OZEL miydi?
🟡 BETIMLEYICI — hukum yok, olcut yok. SALT-OKUNUR.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, sys, statistics as stx

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util as _il
_sp = _il.spec_from_file_location(
    "o2", os.path.join(os.path.dirname(os.path.abspath(__file__)), "02_olcum.py"))
o2 = _il.module_from_spec(_sp)
_sp.loader.exec_module(o2)   # noqa

PENCERELER = [
    ("TUM (57 gun)",     "2026-01-01", "2027-01-01"),
    ("KARSI-OLGU 16g",   "2026-08-19", "2026-09-03"),
    ("ONCESI",           "2026-01-01", "2026-08-19"),
    ("SONRASI",          "2026-09-03", "2027-01-01"),
]


def main():
    hucre = o2.hucre_yukle()
    semboller = sorted(set(r["sym"] for r in hucre))
    mum = o2.mumlar_yukle(semboller)
    rows = o2.getiriler(hucre, mum, 3)      # kayma +3sa (02_olcum'de dogrulandi)

    print("=" * 92)
    print("HAM ILERI GETIRI — pencereye gore  (mekaniksiz, LONG, tum hucre)")
    print("=" * 92)
    print("%-18s %6s %6s %9s %9s %9s %9s %9s"
          % ("pencere", "N", "gun", "+1s", "+4s", "+12s", "+24s", "+48s"))
    for ad, a, b in PENCERELER:
        alt = [r for r in rows if a <= r["ts"] < b]
        if not alt:
            print("%-18s %6d  (bos)" % (ad, 0))
            continue
        gun = len(set(r["_gun"] for r in alt))
        sat = []
        for h in o2.UFUKLAR:
            v = [r["ret%d" % h] for r in alt if r.get("ret%d" % h) is not None]
            sat.append(("%+8.2f%%" % stx.mean(v)) if v else "       -")
        print("%-18s %6d %6d %s" % (ad, len(alt), gun, " ".join(sat)))

    print()
    print("### AYNI TABLO — yalniz taker>=1.0 kolu (botun BUGUNKU aldigi kume)")
    print("%-18s %6s %6s %9s %9s %9s %9s %9s"
          % ("pencere", "N", "gun", "+1s", "+4s", "+12s", "+24s", "+48s"))
    for ad, a, b in PENCERELER:
        alt = [r for r in rows if a <= r["ts"] < b and r["taker"] >= 1.0]
        if not alt:
            print("%-18s %6d  (bos)" % (ad, 0))
            continue
        gun = len(set(r["_gun"] for r in alt))
        sat = []
        for h in o2.UFUKLAR:
            v = [r["ret%d" % h] for r in alt if r.get("ret%d" % h) is not None]
            sat.append(("%+8.2f%%" % stx.mean(v)) if v else "       -")
        print("%-18s %6d %6d %s" % (ad, len(alt), gun, " ".join(sat)))

    print()
    print("### MEDYAN (+24s) — ortalama carpik olabilir")
    for ad, a, b in PENCERELER:
        alt = [r["ret24"] for r in rows
               if a <= r["ts"] < b and r.get("ret24") is not None]
        if alt:
            alt.sort()
            arti = 100.0 * sum(1 for x in alt if x > 0) / len(alt)
            print("   %-18s N=%4d  medyan %+7.2f%%  ortalama %+7.2f%%  artida %%%.0f"
                  % (ad, len(alt), alt[len(alt) // 2], stx.mean(alt), arti))

    print()
    print("🟡 BETIMLEYICI. Ham getiri MEKANIK ICERMEZ — sabit %10 hedef + A-stop")
    print("   dagilimin kuyrugunu kesip sonucu tersine cevirebilir; karsi-olgu")
    print("   tam olarak bunu olcmustu. Bu tablo o hukmu DEGISTIRMEZ, pencerenin")
    print("   ozel olup olmadigini gosterir.")
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
