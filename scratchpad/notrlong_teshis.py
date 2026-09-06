#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NOTRLONG neden giris acmiyor — stage kapisi ne kadar daraltiyor. SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections

print("=" * 96)
print("1) RADAR ARSIVI — stage dagilimi zaman icinde (tum tarama)")
print("=" * 96)
g = collections.defaultdict(collections.Counter)
for l in open("radar_archive.jsonl", encoding="utf-8"):
    l = l.strip()
    if not l:
        continue
    d = json.loads(l)
    ts = d.get("ts", "")
    if ts >= "2026-08-20":
        g[ts[:10]][d.get("stage")] += 1
print("  %-12s %8s %8s %8s %8s   aktif%%" % ("gun", "izle", "HAZIRLA", "BASLIYOR", "toplam"))
for k in sorted(g):
    v = g[k]
    iz, ha, ba = v.get("izle", 0), v.get("HAZIRLANIYOR", 0), v.get("BASLIYOR", 0)
    t = sum(v.values())
    print("  %-12s %8d %8d %8d %8d   %6.2f%%" % (k, iz, ha, ba, t, 100 * (ha + ba) / t if t else 0))

print("")
print("=" * 96)
print("2) SKOR>=30 KISA LISTESINDE stage — notrlong'un gordugu havuz")
print("=" * 96)
g2 = collections.defaultdict(collections.Counter)
for l in open("radar_archive.jsonl", encoding="utf-8"):
    l = l.strip()
    if not l:
        continue
    d = json.loads(l)
    ts = d.get("ts", "")
    if ts >= "2026-08-20" and (d.get("score") or 0) >= 30:
        g2[ts[:10]][d.get("stage")] += 1
print("  %-12s %8s %8s %8s %8s   aktif%%" % ("gun", "izle", "HAZIRLA", "BASLIYOR", "toplam"))
for k in sorted(g2):
    v = g2[k]
    iz, ha, ba = v.get("izle", 0), v.get("HAZIRLANIYOR", 0), v.get("BASLIYOR", 0)
    t = sum(v.values())
    print("  %-12s %8d %8d %8d %8d   %6.2f%%" % (k, iz, ha, ba, t, 100 * (ha + ba) / t if t else 0))

print("")
print("=" * 96)
print("3) NOTR KAPISINI GECEBILECEK ADAY — stage aktif VE skor esigi VE smart LONG")
print("=" * 96)
gun = collections.defaultdict(int)
tur = collections.defaultdict(set)
for l in open("radar_archive.jsonl", encoding="utf-8"):
    l = l.strip()
    if not l:
        continue
    d = json.loads(l)
    ts = d.get("ts", "")
    if ts < "2026-08-20":
        continue
    tur[ts[:10]].add(ts)
    st, sk = d.get("stage"), (d.get("score") or 0)
    if st not in ("BASLIYOR", "HAZIRLANIYOR"):
        continue
    esik = 40.0 if st == "HAZIRLANIYOR" else 45.0
    if sk < esik:
        continue
    if d.get("smart") != "LONG":
        continue
    gun[ts[:10]] += 1
print("  %-12s %10s %10s %12s" % ("gun", "gecen aday", "tur", "tur basina"))
for k in sorted(tur):
    print("  %-12s %10d %10d %12.2f" % (k, gun.get(k, 0), len(tur[k]),
                                        gun.get(k, 0) / max(len(tur[k]), 1)))
print("")
print("  NOT: bu, notrlong'un [:10] kirpmasi UYGULANMADAN once. Gercek sayi daha DUSUK.")
