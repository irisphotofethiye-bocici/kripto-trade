#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""POLYMARKET API YOKLAMASI — 5dk BTC piyasalarinin FIYAT GECMISI cekilebilir mi?

Tek soru: P(kazanir | hareket VE fiyat<=0,70) olculebilir mi?
Bunun icin gerekli: (a) 5dk BTC piyasalarinin listesi, (b) her birinin
kapanistan ONCEKI fiyat gecmisi.

SALT-OKUNUR · UCRETSIZ (halka acik uclar) · bota dokunmaz.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, urllib.request, urllib.error

BASLIK = {"User-Agent": "Mozilla/5.0 (research; read-only)"}


def al(u, n=1200):
    try:
        r = urllib.request.Request(u, headers=BASLIK)
        d = urllib.request.urlopen(r, timeout=40).read()
        return d.decode("utf-8", "replace")[:n], None
    except urllib.error.HTTPError as e:
        return None, "HTTP %s" % e.code
    except Exception as e:
        return None, str(e)[:120]


def bolum(b):
    print()
    print("=" * 92)
    print(b)
    print("=" * 92)


bolum("1) GAMMA API — 5 dakikalik BTC piyasalari var mi?")
denemeler = [
    ("gamma /markets  slug ara",
     "https://gamma-api.polymarket.com/markets?limit=5&closed=true&order=endDate&ascending=false"),
    ("gamma /events   BTC ara",
     "https://gamma-api.polymarket.com/events?limit=3&closed=true&order=endDate&ascending=false"),
]
for ad, u in denemeler:
    t, e = al(u, 600)
    print("   %-28s -> %s" % (ad, ("OK, %d bayt" % len(t)) if t else e))
    if t:
        print("      ilk 400: %s" % t[:400].replace("\n", " "))
    print()

bolum("2) CLOB API — fiyat gecmisi ucu")
for ad, u in [
    ("clob /markets", "https://clob.polymarket.com/markets?next_cursor="),
    ("clob /sampling-markets", "https://clob.polymarket.com/sampling-markets?next_cursor="),
]:
    t, e = al(u, 500)
    print("   %-28s -> %s" % (ad, ("OK, %d bayt" % len(t)) if t else e))
    if t:
        print("      ilk 300: %s" % t[:300].replace("\n", " "))
    print()

print("Salt-okuma. Bot dosyalarina yazim: YOK")
