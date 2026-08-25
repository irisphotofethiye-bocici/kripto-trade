#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TABANLAR — TabFM'siz. On-kayit ON_KAYIT.md (43b0785).
TabFM'in asmak ZORUNDA oldugu cita. Ayni gun-bloklu semayi kullanir,
boylece olcum hatti (bolme, spearman, gun-kumeli t) modelden ONCE dogrulanir.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, math
import numpy as np, pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "veri.json"), encoding="utf-8"))
SAY, KAT, GUNLER = D["sayisal"], D["kategorik"], D["gunler"]
df = pd.DataFrame(D["satir"])
MIN_CTX = 7
TEST = GUNLER[MIN_CTX:]

print("TABANLAR — TabFM'siz  ·  on-kayit 43b0785")
print("=" * 100)
print("veri %d satir · %d gun · ufuk +%ds" % (len(df), len(GUNLER), D["ufuk"]))
print("test gunu %d  (%s .. %s)" % (len(TEST), TEST[0], TEST[-1]))
print("[SAPMA] on-kayit 14 test gunu diyordu -> 13. Sebep: +24s etiketi son gunu")
print("        dusuruyor ve 08-23 HALT_DUSUS (bot duruk) nedeniyle bos. ESIK DEGISMEDI.")


def rho(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 10 or len(set(a[m])) < 3:
        return np.nan
    return stats.spearmanr(a[m], b[m]).statistic


def t_ist(v):
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    if len(v) < 3:
        return np.nan, np.nan, len(v)
    return v.mean(), v.mean() / (v.std(ddof=1) / math.sqrt(len(v))), len(v)


sat = []
print("\n%-12s %5s %6s   %-22s %-22s" % ("gun", "ctx", "tst", "skor(isaretli)", "en iyi tek alan"))
print("-" * 100)
for g in TEST:
    ctx, tst = df[df["gun"] < g], df[df["gun"] == g]
    if len(tst) < 20 or len(ctx) < 200:
        continue
    yc, yt = ctx["y"].to_numpy(float), tst["y"].to_numpy(float)

    r_s = rho(ctx["score"], yc)
    isaret_s = 1.0 if (np.isfinite(r_s) and r_s >= 0) else -1.0
    rho_s = rho(isaret_s * tst["score"].to_numpy(float), yt)

    en_iyi, en_iyi_r = None, 0.0
    for a in SAY:
        rr = rho(pd.to_numeric(ctx[a], errors="coerce"), yc)
        if np.isfinite(rr) and abs(rr) > abs(en_iyi_r):
            en_iyi, en_iyi_r = a, rr
    isaret_b = 1.0 if en_iyi_r >= 0 else -1.0
    rho_b = rho(isaret_b * pd.to_numeric(tst[en_iyi], errors="coerce").to_numpy(float), yt)

    sat.append(dict(gun=g, n=len(tst), rho_skor=rho_s, rho_base=rho_b,
                    alan=en_iyi, ctx_r=en_iyi_r, isaret_s=isaret_s))
    print("%-12s %5d %6d   %+.3f (isaret %+d)      %-12s %+.3f (ctx %+.3f)"
          % (g, len(ctx), len(tst), rho_s, int(isaret_s), en_iyi, rho_b, en_iyi_r))

print("-" * 100)
rs = [s["rho_skor"] for s in sat]
rb = [s["rho_base"] for s in sat]
m1, t1, n1 = t_ist(rs)
m2, t2, n2 = t_ist(rb)
print("\nSKOR (baglamdan isaretli) : rho ort %+.4f  t=%+.2f  N=%d" % (m1, t1, n1))
print("EN IYI TEK ALAN           : rho ort %+.4f  t=%+.2f  N=%d" % (m2, t2, n2))
print("\nTabFM'in gecmesi gereken cita:")
print("   S1  rho > 0 ve t >= 2,0")
print("   S2  TabFM'in gun-rho'su SKOR'unkinden buyuk, eslesmis t >= 2,0")
print("   S3  TabFM'in gun-rho'su EN IYI ALAN'inkinden buyuk, eslesmis t >= 1,5")

from collections import Counter
print("\nen iyi tek alan secimi (baglam gunlerinden, test GORULMEDEN):")
for a, c in Counter(s["alan"] for s in sat).most_common():
    print("   %-14s %d/%d gun" % (a, c, len(sat)))
isc = Counter(int(s["isaret_s"]) for s in sat)
print("\nskor isareti (baglamdan secilen): %s" % dict(isc))
json.dump(sat, open(os.path.join(HERE, "taban_sonuc.json"), "w"))
