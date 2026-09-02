#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MOCK KAYIT DENETIMI — aktor sonuc bulamayinca `type=mock_tweet, id=-1` yer
tutucu dondurup yine ucret aliyor. Bu kayitlar GERCEK GONDERI DEGILDIR ve
sayima girerse sonucu kirletir. Her cekilen dosya taranir.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, glob, os

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def mock_mu(t):
    return t.get("type") == "mock_tweet" or t.get("id") == -1


def main():
    yollar = sorted(glob.glob(os.path.join(PROJE, "scratchpad", "x_pencere", "*", "saat_*.json")))
    yollar += sorted(glob.glob(os.path.join(PROJE, "scratchpad", "x_1908", "saat_*.json")))
    print("MOCK KAYIT DENETIMI")
    print("=" * 62)
    print("%-34s %7s %6s %7s" % ("dosya", "toplam", "mock", "gercek"))
    print("-" * 62)
    top_m = 0
    kirli = []
    for p in yollar:
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        m = sum(1 for t in d if mock_mu(t))
        top_m += m
        ad = os.path.relpath(p, os.path.join(PROJE, "scratchpad")).replace(os.sep, "/")
        im = "   <== KIRLI" if m else ""
        print("%-34s %7d %6d %7d%s" % (ad, len(d), m, len(d) - m, im))
        if m:
            kirli.append(ad)
    print("-" * 62)
    print("TOPLAM mock kayit: %d" % top_m)
    if kirli:
        print("KIRLI dosyalar (silinip yeniden cekilmeli): %s" % ", ".join(kirli))
    else:
        print("temiz — hicbir dosyada mock kayit yok")


if __name__ == "__main__":
    main()
