#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BASIS VERI KUMESI. On-kayit: ON_KAYIT.md (2e3ff43). SALT OKUMA.

FAZ KILIDI ONLENDI: sembol basina SABIT RASTGELE faz (seed 20260826).
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, glob, random, datetime, collections, statistics

HERE  = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(os.path.dirname(HERE))
SPOT  = os.path.join(HERE, "spot_1h")
PERP  = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
FUND  = os.path.join(PROJE, "scratchpad", "funding_gecmis")
UFUK  = 24
random.seed(20260826)

print("BASIS VERI KUMESI — on-kayit 2e3ff43")
print("=" * 88)

sems = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(SPOT, "*.json")))
print("spot dosyasi: %d" % len(sems))

satir = []
atla = collections.Counter()
for n, sym in enumerate(sems):
    try:
        sp = json.load(open(os.path.join(SPOT, sym + ".json"), encoding="utf-8"))
        pk = json.load(open(os.path.join(PERP, sym + ".json"), encoding="utf-8"))
    except Exception:
        atla["dosya"] += 1
        continue
    if len(sp) < 500 or len(pk) < 500:
        atla["kisa"] += 1
        continue
    spot = {int(x["t"]): float(x["c"]) for x in sp}
    perp_t = [int(x["t"]) for x in pk]
    perp_c = [float(x["c"]) for x in pk]
    pidx = {t: i for i, t in enumerate(perp_t)}

    # fonlama: saate en yakin gecmis oran
    try:
        fg = json.load(open(os.path.join(FUND, sym + ".json"), encoding="utf-8"))
        fund = {int(x["t"]) // 3600000 * 3600000: float(x["r"]) for x in fg}
    except Exception:
        fund = {}

    faz = random.randrange(24)                 # SEMBOL BASINA SABIT RASTGELE FAZ
    for i in range(faz, len(perp_t) - UFUK - 1, 24):
        t = perp_t[i]
        sc = spot.get(t)
        if not sc or sc <= 0:
            continue
        pc = perp_c[i]
        if pc <= 0 or perp_c[i + UFUK] <= 0:
            continue
        j24 = pidx.get(t - 24 * 3600000)
        chg24 = (100.0 * (pc / perp_c[j24] - 1.0)) if (j24 is not None and perp_c[j24] > 0) else None
        fr = None
        for geri in range(0, 8):
            fr = fund.get(t - geri * 3600000)
            if fr is not None:
                break
        satir.append(dict(
            sym=sym, t=t,
            gun=datetime.datetime.utcfromtimestamp(t/1000).strftime("%Y-%m-%d"),
            basis=100.0 * (pc / sc - 1.0),
            y=100.0 * (perp_c[i + UFUK] / pc - 1.0),      # HAM +24s
            funding=fr, chg24=chg24))
    if (n + 1) % 60 == 0:
        print("   ... %d/%d sembol  (satir %d)" % (n + 1, len(sems), len(satir)), flush=True)

print("\ngozlem %d  ·  atlanan %s" % (len(satir), dict(atla)))
g = collections.Counter(r["gun"] for r in satir)
gunler = sorted(g)
print("gun %d  (%s .. %s)" % (len(gunler), gunler[0], gunler[-1]))
print("gun basi sembol: medyan %d · min %d · max %d"
      % (statistics.median(g.values()), min(g.values()), max(g.values())))
b = [r["basis"] for r in satir]
print("basis: ort %+.4f%% · medyan %+.4f%% · std %.4f · %%1 %+.3f · %%99 %+.3f"
      % (statistics.mean(b), statistics.median(b), statistics.pstdev(b),
         sorted(b)[len(b)//100], sorted(b)[99*len(b)//100]))
print("etiket +24s: ort %+.3f%% · medyan %+.3f%%"
      % (statistics.mean(r["y"] for r in satir), statistics.median(r["y"] for r in satir)))
print("funding dolu %%%.1f · chg24 dolu %%%.1f"
      % (100*sum(1 for r in satir if r["funding"] is not None)/len(satir),
         100*sum(1 for r in satir if r["chg24"] is not None)/len(satir)))
json.dump(satir, open(os.path.join(HERE, "veri.json"), "w"))
print("\nYAZILDI -> scratchpad/basis/veri.json (%.0f MB)"
      % (os.path.getsize(os.path.join(HERE, "veri.json"))/1048576))
