#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_uzun.py OLCUMUNDE HATA VAR MI? — TESHIS

Kullanici: "sanki olcumunde hata varmis gibi geliyor bana"

Uc supheli:
  1) UST DILIM 422,44% ATR'ye kadar gidiyor -> bozuk mum / asiri deger
  2) asgari_stop kapisi 208.377 aday eledi -> ATR'ye gore SECICI mi?
  3) stop/ATR orani dilimler arasi farkli mi (yapisal asimetri)

Hukum DEGIL, TESHIS. SALT-OKUNUR.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, sys, math, collections, statistics as stx
import importlib.util as il

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURA))
sys.path.insert(0, KOK)
sp = il.spec_from_file_location(
    "ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)
import olcucu  # noqa: E402

KDIR = os.path.join(KOK, "scratchpad", "klines_1h_uzun")
SEYRELT = 24


def faz(sym):
    h = 0
    for c in sym:
        h = (h * 131 + ord(c)) & 0xFFFFFFFF
    return h % SEYRELT


def main():
    print("=" * 100)
    print("TESHIS — 02_uzun.py'de hata var mi?")
    print("=" * 100)
    gecen, elenen = [], []
    dosyalar = sorted(x for x in os.listdir(KDIR) if x.endswith(".json"))
    for di, fn in enumerate(dosyalar, 1):
        sym = fn[:-5]
        try:
            d = json.load(open(os.path.join(KDIR, fn), encoding="utf-8"))
        except Exception:
            continue
        d.sort(key=lambda x: x["t"])
        n = len(d)
        if n < ar.YAPI_BAR + ar.ZAMAN_STOP + 40:
            continue
        for i0 in range(ar.YAPI_BAR + faz(sym), n - ar.ZAMAN_STOP - 1, SEYRELT):
            p = d[i0]["c"]
            if not p or p <= 0:
                continue
            bars = d[i0 - ar.YAPI_BAR:i0]
            atr = olcucu.atr(bars, period=14)
            if atr <= 0:
                continue
            stop = ar.stop_hesapla(bars, p)
            if stop is None:
                continue
            sf = (p - stop) / p * 100.0
            kayit = (atr / p * 100.0, sf, sf / (atr / p * 100.0), sym)
            if sf < ar.ASGARI_STOP:
                elenen.append(kayit)
            else:
                gecen.append(kayit)
        if di % 150 == 0:
            print("   ... %d/%d" % (di, len(dosyalar)))

    print()
    print("### 1) ASIRI ATR DEGERLERI — bozuk veri mi?")
    a = sorted(x[0] for x in gecen)
    n = len(a)
    for et, v in (("p50", a[n // 2]), ("p90", a[9 * n // 10]), ("p99", a[99 * n // 100]),
                  ("p99,9", a[999 * n // 1000]), ("MAX", a[-1])):
        print("   %-6s %10.2f%%" % (et, v))
    for esik in (20, 50, 100):
        k = sum(1 for x in a if x > esik)
        print("   ATR%% > %3d olan: %5d  (%%%.3f)" % (esik, k, 100.0 * k / n))
    ust = sorted(gecen, key=lambda z: -z[0])[:8]
    print("   en asiri 8: %s" % ", ".join("%s %.0f%%" % (x[3], x[0]) for x in ust))
    print()

    print("### 2) 🔴 asgari_stop KAPISI ATR'ye GORE SECICI Mi?")
    print("   (asgari_stop = %.2f%%)" % ar.ASGARI_STOP)
    hepsi = gecen + elenen
    hepsi.sort(key=lambda z: z[0])
    m = len(hepsi)
    print("   %-16s %10s %10s %10s %10s"
          % ("ATR% dilimi", "aday", "gecen", "elenen", "eleme%"))
    for i in range(5):
        q = hepsi[i * m // 5:(i + 1) * m // 5]
        el = sum(1 for x in q if x[1] < ar.ASGARI_STOP)
        print("   %-16s %10s %10s %10s %9.1f%%"
              % ("%.2f-%.2f" % (q[0][0], q[-1][0]), "{:,}".format(len(q)),
                 "{:,}".format(len(q) - el), "{:,}".format(el), 100.0 * el / len(q)))
    print()

    print("### 3) stop/ATR ORANI — dilimler arasi yapisal asimetri")
    gecen.sort(key=lambda z: z[0])
    g = len(gecen)
    print("   %-16s %10s %11s %11s %11s"
          % ("ATR% dilimi", "N", "ort ATR%", "ort stop%", "stop/ATR"))
    for i in range(5):
        q = gecen[i * g // 5:(i + 1) * g // 5]
        print("   %-16s %10s %10.2f%% %10.2f%% %11.2f"
              % ("%.2f-%.2f" % (q[0][0], q[-1][0]), "{:,}".format(len(q)),
                 stx.mean([x[0] for x in q]), stx.mean([x[1] for x in q]),
                 stx.mean([x[2] for x in q])))
    print()
    print("   -> stop/ATR dilimler arasinda BUYUK olcude degisiyorsa,")
    print("      R'nin paydasi ATR'yle DEGIL asgari_stop TABANIYLA belirleniyor")
    print("      demektir ve R karsilastirmasi YANLIS olur.")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
