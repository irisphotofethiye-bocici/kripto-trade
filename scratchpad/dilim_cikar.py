#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HAKEM PENCERESI DILIMLERI — kanittan cikarilir, belgeden DEGIL. SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections

T0 = "2026-08-12 01:17:00"
E = [json.loads(l) for l in open("testbot_equity.jsonl", encoding="utf-8") if l.strip()]
E = [r for r in E if r["ts"] >= T0]
print("pencere ici equity kaydi: %d  (%s .. %s)" % (len(E), E[0]["ts"], E[-1]["ts"]))

print("")
print("=" * 92)
print("1) DURUM GECISLERI — equity kutugunden (her tur yaziliyor)")
print("=" * 92)
onc = None
gecis = []
for r in E:
    d = r.get("durum")
    if d != onc:
        gecis.append((r["ts"], onc, d))
        onc = d
for ts, a, b in gecis:
    print("  %s   %s -> %s" % (ts, a or "(baslangic)", b))

print("")
print("  durum dagilimi (tur sayisi):")
for k, v in collections.Counter(r.get("durum") for r in E).most_common():
    print("     %-14s %5d tur (%%%.1f)" % (k, v, 100 * v / len(E)))

print("")
print("=" * 92)
print("2) config'teki FREN NOTU — git izi yok, kalici kayit orada")
print("=" * 92)
try:
    c = json.load(open("kripto-config.json", encoding="utf-8"))
    tb = c.get("testbot", c)
    for k in sorted(tb):
        if "dusus" in k.lower() or "fren" in k.lower() or "btc_pay" in k.lower():
            v = tb[k]
            print("  %-28s = %s" % (k, json.dumps(v, ensure_ascii=False)[:180]))
except Exception as e:
    print("  config okunamadi:", repr(e)[:120])

print("")
print("=" * 92)
print("3) HALT gunleri — fren gercekten isledi mi")
print("=" * 92)
g = collections.defaultdict(lambda: collections.Counter())
for r in E:
    g[r["ts"][:10]][r.get("durum")] += 1
print("  %-12s %6s %6s %8s" % ("gun", "AKTIF", "HALT", "HALT%"))
for k in sorted(g):
    v = g[k]
    h = sum(n for d, n in v.items() if d and "HALT" in str(d))
    a = sum(v.values()) - h
    if h:
        print("  %-12s %6d %6d %7.0f%%" % (k, a, h, 100 * h / (a + h)))
