#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TabFM botun KENDI pozisyonlarini ayirabilir mi. On-kayit e1097b5.
Olcutler T1..T4 SABIT. TESHIS -- hukum yazilmaz.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, math, argparse
import numpy as np, pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--n-est", type=int, default=32)
A = ap.parse_args()

D = json.load(open(os.path.join(HERE, "poz_veri.json"), encoding="utf-8"))
SAY, KAT, TEST = D["sayisal"], D["kategorik"], D["test_gun"]
df = pd.DataFrame(D["satir"])
ALAN = SAY + KAT
print("POZISYON OLCUMU — on-kayit e1097b5  ·  TESHIS, hukum yazilmaz")
print("=" * 100)
print("pozisyon %d · test gunu %d · n_est=%d" % (len(df), len(TEST), A.n_est))


def hazirla(ctx, tst):
    Xc, Xt = ctx[ALAN].copy(), tst[ALAN].copy()
    for a in SAY:
        m = pd.to_numeric(Xc[a], errors="coerce").median()
        if not np.isfinite(m):
            m = 0.0
        Xc[a] = pd.to_numeric(Xc[a], errors="coerce").fillna(m).astype(float)
        Xt[a] = pd.to_numeric(Xt[a], errors="coerce").fillna(m).astype(float)
    for a in KAT:
        Xc[a] = Xc[a].astype(object).where(Xc[a].notna(), "YOK").astype(str)
        Xt[a] = Xt[a].astype(object).where(Xt[a].notna(), "YOK").astype(str)
    return Xc, Xt


def rho(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 6 or len(set(a[m])) < 3:
        return np.nan
    return stats.spearmanr(a[m], b[m]).statistic


def yari(pred, y):
    """ust yari - alt yari (ortalama). Tek sayida ise medyan ustu/alti."""
    p, y = np.asarray(pred, float), np.asarray(y, float)
    m = np.isfinite(p) & np.isfinite(y)
    p, y = p[m], y[m]
    if len(p) < 4:
        return np.nan, np.nan, np.nan
    med = np.median(p)
    u, a = y[p > med], y[p <= med]
    if len(u) < 2 or len(a) < 2:
        return np.nan, np.nan, np.nan
    return u.mean() - a.mean(), u.sum(), a.sum()


from tabfm.src.pytorch import tabfm_v1_0_0
from tabfm import TabFMRegressor
model = tabfm_v1_0_0.load(model_type="regression",
                          checkpoint_path=os.path.join(HERE, "agirlik"), device="cpu")
print("model yuklendi", flush=True)

sat = []
for g in TEST:
    ctx, tst = df[df["gun"] < g], df[df["gun"] == g]
    if len(tst) < 4 or len(ctx) < 40:
        print("  %s ATLANDI (ctx=%d tst=%d)" % (g, len(ctx), len(tst)))
        continue
    Xc, Xt = hazirla(ctx, tst)
    r = dict(gun=g, n=len(tst), nctx=len(ctx))

    for et in ("L2", "L1"):
        cm = ctx[et].notna()
        if cm.sum() < 40:
            r["p_" + et] = None
            continue
        reg = TabFMRegressor(model=model, n_estimators=A.n_est, random_state=20260826)
        reg.fit(Xc[cm.values], ctx.loc[cm, et].to_numpy(float))
        r["p_" + et] = np.asarray(reg.predict(Xt), float).tolist()

    # taban: botun kendi skoru, isaret BAGLAMDAN
    rs = rho(ctx["score"], ctx["L2"])
    isaret = 1.0 if (np.isfinite(rs) and rs >= 0) else -1.0
    r["p_skor"] = (isaret * tst["score"].to_numpy(float)).tolist()
    r["isaret_skor"] = isaret
    r["L2"] = tst["L2"].to_numpy(float).tolist()
    r["L1"] = tst["L1"].to_numpy(float).tolist() if "L1" in tst else []
    r["yon"] = tst["yon"].tolist()
    sat.append(r)
    d, us, al = yari(r["p_L2"], r["L2"])
    print("  %s  ctx=%-4d tst=%-3d  ust-alt %+8.2f $  (ust %+8.2f / alt %+8.2f)  skor isaret %+d"
          % (g, len(ctx), len(tst), d, us, al, int(isaret)), flush=True)

json.dump(sat, open(os.path.join(HERE, "poz_sonuc.json"), "w"))

print("\n" + "=" * 100)
print("OLCUTLER — on-kayitta SABIT (e1097b5)")
print("=" * 100)


def t_ist(v):
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    if len(v) < 3:
        return np.nan, np.nan, len(v)
    sd = v.std(ddof=1)
    return v.mean(), (v.mean()/(sd/math.sqrt(len(v))) if sd > 0 else np.nan), len(v)


def t1(anahtar, suzgec=None):
    fark, ust, alt, poz, n = [], 0.0, 0.0, 0, 0
    for s in sat:
        p, y, yn = s.get(anahtar), np.array(s["L2"]), np.array(s["yon"])
        if p is None:
            continue
        p = np.array(p, float)
        if suzgec is not None:
            m = yn == suzgec
            p, y = p[m], y[m]
        d, u, a = yari(p, y)
        if not np.isfinite(d):
            continue
        fark.append(d); ust += u; alt += a; n += 1
        poz += 1 if d > 0 else 0
    return fark, ust, alt, poz, n


f, ust, alt, poz, n = t1("p_L2")
m, t, _ = t_ist(f)
gec1 = (m > 0 and poz >= 5)
print("T1  PARA  ust yari - alt yari : ort %+.2f $/poz · t=%+.2f · pozitif gun %d/%d"
      % (m, t, poz, n))
print("          toplam: ust %+.2f $  ·  alt %+.2f $  ·  FARK %+.2f $   -> %s"
      % (ust, alt, ust-alt, "GECTI" if gec1 else "DUSTU"))

r2 = [rho(s["p_L1"], s["L1"]) for s in sat if s.get("p_L1") and s.get("L1")]
m2, t2, n2 = t_ist(r2)
gec2 = (m2 > 0 and t2 >= 1.5)
print("T2  SINYAL rho(tahmin, ham L1): %+.4f · t=%+.2f · N=%d gun            -> %s"
      % (m2, t2, n2, "GECTI" if gec2 else "DUSTU"))

fs, us_, as_, pz, ns = t1("p_skor")
ms, ts_, _ = t_ist(fs)
rs2 = [rho(s["p_skor"], s["L1"]) for s in sat if s.get("L1")]
ms2, _, _ = t_ist(rs2)
gec3 = (np.isfinite(ms) and m > ms) and (np.isfinite(ms2) and m2 > ms2)
print("T3  TABAN skor: para %+.2f $/poz (pozitif %d/%d) · rho %+.4f"
      % (ms, pz, ns, ms2))
print("          TabFM her ikisinde de gecti mi -> %s" % ("GECTI" if gec3 else "DUSTU"))

fl, ul, al_, pl, nl = t1("p_L2", suzgec="LONG")
ml, tl, _ = t_ist(fl)
gec4 = np.isfinite(ml) and np.isfinite(m) and (ml > 0) == (m > 0)
print("T4  KARISTIRICI yalniz LONG   : ort %+.2f $/poz · pozitif gun %d/%d   -> %s"
      % (ml, pl, nl, "GECTI" if gec4 else "DUSTU"))

print("\n" + "=" * 100)
print("SONUC: %s" % ("SINAMAYA DEGER (T1+T3+T4)" if (gec1 and gec3 and gec4)
                     else "SINAMAYA DEGMEZ"))
print("=" * 100)
print("🔴 Bu bir TESHISTIR. N=%d pozisyon / %d gun, pencere SECILMIS, tek rejim."
      % (sum(s["n"] for s in sat), len(sat)))
