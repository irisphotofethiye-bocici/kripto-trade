#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""defter2 omru boyunca testbot/golge ne yapti + defter2 gunluk yol. SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json

D2 = "2026-08-20 17:28:55"


def oku(a):
    return [json.loads(l) for l in open(a, encoding="utf-8") if l.strip()]


print("=" * 92)
print("AYNI TAKVIM — defter2'nin dogumundan (%s) bugune" % D2[:16])
print("=" * 92)
for ad, ef, sf in (("testbot", "testbot_equity.jsonl", "testbot_state.json"),
                   ("golge", "golge_equity.jsonl", "golge_state.json"),
                   ("defter2", "defter2_equity.jsonl", "defter2_state.json")):
    e = [r for r in oku(ef) if r["ts"] < D2]
    b = e[-1]["equity"] if e else json.load(open(sf, encoding="utf-8"))["baslangic_bakiye"]
    n = json.load(open(sf, encoding="utf-8"))["equity"]
    print("  %-8s %9.2f -> %9.2f   %+9.2f  (%%%+.2f)" % (ad, b, n, n - b, 100.0 * (n - b) / b))

print("")
print("=" * 92)
print("DEFTER2 GUNLUK YOL — kayip one mi yuklu?")
print("=" * 92)
g = {}
for r in oku("defter2_equity.jsonl"):
    g[r["ts"][:10]] = r["equity"]
onc = 10000.0
for k in sorted(g):
    print("  %-12s %9.2f   gunluk %+8.2f   toplam %+8.2f" % (k, g[k], g[k] - onc, g[k] - 10000.0))
    onc = g[k]

print("")
print("=" * 92)
print("DEFTER3 GUNLUK YOL")
print("=" * 92)
g = {}
for r in oku("defter3_equity.jsonl"):
    g[r["ts"][:10]] = r["equity"]
onc = 10000.0
for k in sorted(g):
    print("  %-12s %9.2f   gunluk %+8.2f   toplam %+8.2f" % (k, g[k], g[k] - onc, g[k] - 10000.0))
    onc = g[k]
