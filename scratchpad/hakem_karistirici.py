#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DILIM x PIYASA — kayip kural degisikliginden mi, piyasadan mi? SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, os, datetime as dt, collections, statistics as stt

HERE = os.path.dirname(os.path.abspath(__file__))
BTC = {int(k): v for k, v in json.load(open(os.path.join(HERE, "btc_1h_onbellek.json"))).items()}
DILIM = [
    ("A1  btc_pay freni ACIK",        "2026-08-12 01:17:00", "2026-08-19 13:44:00"),
    ("A2+A3  fren gidip geldi",       "2026-08-19 13:44:00", "2026-08-19 21:40:00"),
    ("B   frensiz SHORT",             "2026-08-19 21:40:00", "2026-08-22 16:06:21"),
    ("C   DURDU",                     "2026-08-22 16:06:21", "2026-08-24 01:24:35"),
    ("D   elle DEVAM",                "2026-08-24 01:24:35", "2026-08-26 17:58:52"),
    ("E   DURDU",                     "2026-08-26 17:58:52", "2026-08-28 00:02:05"),
    ("F   dusus freni KAPALI",        "2026-08-28 00:02:05", "2099-01-01 00:00:00"),
]


def ms(s):
    return int(dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").timestamp() * 1000)


def btc_at(t):
    k = sorted(BTC)
    for d in range(0, 6):
        for s in (+1, -1):
            x = (t // 3600000 + s * d) * 3600000
            if x in BTC:
                return BTC[x]
    return None


K = [json.loads(l) for l in open("testbot_islemler.jsonl", encoding="utf-8") if l.strip()]
g = {}
for r in K:
    t = dt.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S") \
        - dt.timedelta(hours=float(r.get("tutma_saat") or 0))
    if r["id"] not in g or t < g[r["id"]]:
        g[r["id"]] = t
pnl, meta = collections.defaultdict(float), {}
for r in K:
    pnl[r["id"]] += float(r.get("sonuc_usdt") or 0)
    if not r.get("kismi"):
        meta[r["id"]] = r

print("=" * 104)
print("DILIM x PIYASA — kayip KURAL degisikliginden mi PIYASADAN mi?")
print("=" * 104)
print("  %-26s %7s %7s %8s %9s %8s %8s"
      % ("dilim", "gun", "BTC %", "poz", "P&L", "SHORT%", "kazanma"))
son = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
for ad, a, b in DILIM:
    bb = min(b, son)
    b0, b1 = btc_at(ms(a)), btc_at(ms(bb))
    d = (dt.datetime.strptime(bb, "%Y-%m-%d %H:%M:%S")
         - dt.datetime.strptime(a, "%Y-%m-%d %H:%M:%S")).total_seconds() / 86400
    ids = [i for i in meta if a <= g[i].strftime("%Y-%m-%d %H:%M:%S") < b]
    v = [pnl[i] for i in ids]
    sh = sum(1 for i in ids if meta[i]["yon"] == "SHORT")
    btc = (100 * (b1 - b0) / b0) if (b0 and b1) else float("nan")
    print("  %-26s %6.1fg %+6.1f%% %8d %+9.0f %7s %8s"
          % (ad, d, btc, len(v), sum(v),
             ("%.0f%%" % (100 * sh / len(ids))) if ids else "—",
             ("%.0f%%" % (100 * sum(1 for x in v if x > 0) / len(v))) if v else "—"))

print("")
print("=" * 104)
print("AYNI DILIMLERDE DIGER DEFTERLER — bot mu kotu, piyasa mi?")
print("=" * 104)


def defter(f, t0):
    KK = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    gg = {}
    for r in KK:
        t = dt.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S") \
            - dt.timedelta(hours=float(r.get("tutma_saat") or 0))
        if r["id"] not in gg or t < gg[r["id"]]:
            gg[r["id"]] = t
    pp, mm = collections.defaultdict(float), {}
    for r in KK:
        pp[r["id"]] += float(r.get("sonuc_usdt") or 0)
        if not r.get("kismi"):
            mm[r["id"]] = r
    return pp, gg, mm


DEF = {"golge": defter("golge_islemler.jsonl", None),
       "defter2": defter("defter2_islemler.jsonl", None),
       "defter3": defter("defter3_islemler.jsonl", None)}
print("  %-26s %10s %10s %10s %10s" % ("dilim", "testbot", "golge", "defter2", "defter3"))
for ad, a, b in DILIM:
    sat = "  %-26s" % ad
    ids = [i for i in meta if a <= g[i].strftime("%Y-%m-%d %H:%M:%S") < b]
    sat += "%10s" % (("%+.0f" % sum(pnl[i] for i in ids)) if ids else "—")
    for dn in ("golge", "defter2", "defter3"):
        pp, gg, mm = DEF[dn]
        ii = [i for i in mm if a <= gg[i].strftime("%Y-%m-%d %H:%M:%S") < b]
        sat += "%10s" % (("%+.0f" % sum(pp[i] for i in ii)) if ii else "—")
    print(sat)
