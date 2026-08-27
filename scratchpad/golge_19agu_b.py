#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ek kesitler: sinir pozisyonlari, equity yolu, gunluk kirilim. SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections, datetime as dt

T0 = "2026-08-19 00:00:00"


def oku(a):
    return [json.loads(l) for l in open(a, encoding="utf-8") if l.strip()]


def gts(K):
    g = {}
    for r in K:
        t = dt.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S") \
            - dt.timedelta(hours=float(r.get("tutma_saat") or 0))
        if r["id"] not in g or t < g[r["id"]]:
            g[r["id"]] = t
    return g


print("=" * 96)
print("1) SINIR POZISYONLARI — pencere ONCESI acilmis, pencere ICINDE kapanmis")
print("   (equity farkina girer ama 'acilip kapanan' sayimina girmez)")
print("=" * 96)
for ad, f in (("testbot", "testbot_islemler.jsonl"), ("golge", "golge_islemler.jsonl")):
    K = oku(f)
    G = gts(K)
    sinir = {i for i, t in G.items()
             if t.strftime("%Y-%m-%d %H:%M:%S") < T0
             and max(r["ts"] for r in K if r["id"] == i) >= T0}
    p = sum(float(r.get("sonuc_usdt") or 0) for r in K if r["id"] in sinir)
    print("  %-8s %2d pozisyon  P&L %+9.2f" % (ad, len(sinir), p))

print("")
print("=" * 96)
print("2) EQUITY YOLU — pencere icinde gunluk kapanis (realize kasa)")
print("=" * 96)
yol = {}
for ad, f in (("testbot", "testbot_equity.jsonl"), ("golge", "golge_equity.jsonl")):
    g = {}
    for r in oku(f):
        if r["ts"] >= "2026-08-18":
            g[r["ts"][:10]] = r["equity"]
    yol[ad] = g
gunler = sorted(set(yol["testbot"]) | set(yol["golge"]))
print("  %-12s %12s %12s   %12s" % ("gun", "testbot", "golge", "fark"))
tb0 = gb0 = None
for g in gunler:
    tb, gb = yol["testbot"].get(g), yol["golge"].get(g)
    if tb is None or gb is None:
        continue
    if tb0 is None:
        tb0, gb0 = tb, gb
    print("  %-12s %12.2f %12.2f   %+7.2f / %+7.2f" % (g, tb, gb, tb - tb0, gb - gb0))

print("")
print("=" * 96)
print("3) GOLGE 'BILINMIYOR' rejimli 9 pozisyon nedir")
print("=" * 96)
K = oku("golge_islemler.jsonl")
G = gts(K)
pen = {i for i, t in G.items() if t.strftime("%Y-%m-%d %H:%M:%S") >= T0}
c = collections.Counter()
for r in K:
    if r["id"] in pen and not r.get("kismi") and str(r.get("rejim_giriste")) == "BILINMIYOR":
        c[(r.get("kaynak"), r.get("yon"))] += 1
print("  ", dict(c))

print("")
print("=" * 96)
print("4) ESLESMIS BAKIS — golge 'onay_bekle' botun ERTELEDIGI girisler")
print("   testbot ayni sembole ayni gun girdi mi?")
print("=" * 96)
TB = oku("testbot_islemler.jsonl")
tb_gun = collections.defaultdict(set)
TG = gts(TB)
for r in TB:
    tb_gun[r["sym"]].add(TG[r["id"]].strftime("%Y-%m-%d"))
esles = ayri = 0
for i in pen:
    m = [r for r in K if r["id"] == i and not r.get("kismi")]
    if not m or m[0].get("kaynak") != "golge:onay_bekle":
        continue
    if G[i].strftime("%Y-%m-%d") in tb_gun.get(m[0]["sym"], ()):
        esles += 1
    else:
        ayri += 1
print("  onay_bekle: botun AYNI GUN ayni sembole girdigi %d · girmedigi %d" % (esles, ayri))
