#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A1 anlamli mi · F'te hepsi kaybetti mi · yon dagilimi. SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections, datetime as dt, statistics as stt, math


def poz(f):
    K = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    g = {}
    for r in K:
        t = dt.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S") \
            - dt.timedelta(hours=float(r.get("tutma_saat") or 0))
        if r["id"] not in g or t < g[r["id"]]:
            g[r["id"]] = t
    p, m = collections.defaultdict(float), {}
    for r in K:
        p[r["id"]] += float(r.get("sonuc_usdt") or 0)
        if not r.get("kismi"):
            m[r["id"]] = r
    return p, g, m


def gun_t(p, g, ids):
    d = collections.defaultdict(float)
    for i in ids:
        d[g[i].strftime("%Y-%m-%d")] += p[i]
    v = list(d.values())
    if len(v) < 3:
        return None, None, len(v), 0
    sd = stt.stdev(v)
    t = stt.mean(v) / (sd / math.sqrt(len(v))) if sd > 0 else None
    return stt.mean(v), t, len(v), sum(1 for x in v if x > 0)


P, G, M = poz("testbot_islemler.jsonl")
print("=" * 96)
print("1) DILIM A1 — ORIJINAL DONMUS YAPILANDIRMA, gun-kumeli")
print("=" * 96)
for ad, a, b in (("A1  (orijinal)", "2026-08-12 01:17:00", "2026-08-19 13:44:00"),
                 ("B+D+F (degisiklik sonrasi)", "2026-08-19 21:40:00", "2099-01-01")):
    ids = [i for i in M if a <= G[i].strftime("%Y-%m-%d %H:%M:%S") < b]
    m, t, n, ar = gun_t(P, G, ids)
    print("  %-28s %3d poz · %2d gun · gun ort %+8.2f · t=%s · arti gun %d/%d"
          % (ad, len(ids), n, m, ("%+.2f" % t) if t else "—", ar, n))

print("")
print("=" * 96)
print("2) YON DAGILIMI dilim dilim — bot davranisi DEGISTI mi")
print("=" * 96)
DIL = [("A1", "2026-08-12 01:17:00", "2026-08-19 13:44:00"),
       ("B", "2026-08-19 21:40:00", "2026-08-22 16:06:21"),
       ("D", "2026-08-24 01:24:35", "2026-08-26 17:58:52"),
       ("F", "2026-08-28 00:02:05", "2099-01-01")]
print("  %-6s %6s %8s %8s %11s %11s" % ("dilim", "poz", "SHORT", "LONG", "SHORT P&L", "LONG P&L"))
for ad, a, b in DIL:
    ids = [i for i in M if a <= G[i].strftime("%Y-%m-%d %H:%M:%S") < b]
    s = [i for i in ids if M[i]["yon"] == "SHORT"]
    l = [i for i in ids if M[i]["yon"] == "LONG"]
    print("  %-6s %6d %8d %8d %+11.0f %+11.0f"
          % (ad, len(ids), len(s), len(l),
             sum(P[i] for i in s), sum(P[i] for i in l)))

print("")
print("=" * 96)
print("3) DILIM F — dort defter, gun gun (hepsi ayni yonde mi kaybetti)")
print("=" * 96)
DEF = {"testbot": (P, G, M)}
for d in ("golge", "defter2", "defter3"):
    DEF[d] = poz(d + "_islemler.jsonl")
a = "2026-08-28 00:02:05"
gunler = collections.defaultdict(dict)
for dn, (p, g, m) in DEF.items():
    for i in m:
        k = g[i].strftime("%Y-%m-%d %H:%M:%S")
        if k >= a:
            gunler[g[i].strftime("%Y-%m-%d")][dn] = gunler[g[i].strftime("%Y-%m-%d")].get(dn, 0) + p[i]
print("  %-12s %10s %10s %10s %10s  %s" % ("gun", "testbot", "golge", "defter2", "defter3", "hepsi eksi?"))
hep = 0
for k in sorted(gunler):
    v = gunler[k]
    dolu = [v.get(x) for x in ("testbot", "golge", "defter2", "defter3")]
    he = all(x is not None and x < 0 for x in dolu)
    hep += 1 if he else 0
    print("  %-12s %10s %10s %10s %10s  %s"
          % (k, *[("%+.0f" % x) if x is not None else "—" for x in dolu],
             "EVET" if he else ""))
print("  -> %d gunun %d'inde DORDU DE eksi" % (len(gunler), hep))
