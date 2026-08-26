#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TabFM BES DEFTERIN HAVUZUNDA. On-kayit e1b30d8. H1..H5 SABIT."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, math, argparse
import numpy as np, pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("--n-est", type=int, default=32)
A = ap.parse_args()

D = json.load(open(os.path.join(HERE, "havuz_veri.json"), encoding="utf-8"))
SAY, KAT, TEST = D["sayisal"], D["kategorik"], D["test_gun"]
df = pd.DataFrame(D["satir"])
ALAN = SAY + KAT
print("HAVUZ OLCUMU — on-kayit e1b30d8  ·  n_est=%d" % A.n_est)
print("=" * 104)
print("pozisyon %d · test gunu %d" % (len(df), len(TEST)))


def hazirla(ctx, tst):
    Xc, Xt = ctx[ALAN].copy(), tst[ALAN].copy()
    for a in SAY:
        m = pd.to_numeric(Xc[a], errors="coerce").median()
        if not np.isfinite(m): m = 0.0
        Xc[a] = pd.to_numeric(Xc[a], errors="coerce").fillna(m).astype(float)
        Xt[a] = pd.to_numeric(Xt[a], errors="coerce").fillna(m).astype(float)
    for a in KAT:
        Xc[a] = Xc[a].astype(object).where(Xc[a].notna(), "YOK").astype(str)
        Xt[a] = Xt[a].astype(object).where(Xt[a].notna(), "YOK").astype(str)
    return Xc, Xt


def rho(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 8 or len(set(a[m])) < 3: return np.nan
    return stats.spearmanr(a[m], b[m]).statistic


def t_ist(v):
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    if len(v) < 3: return np.nan, np.nan, len(v)
    sd = v.std(ddof=1)
    return v.mean(), (v.mean()/(sd/math.sqrt(len(v))) if sd > 0 else np.nan), len(v)


def yari(p, y):
    p, y = np.asarray(p, float), np.asarray(y, float)
    m = np.isfinite(p) & np.isfinite(y); p, y = p[m], y[m]
    if len(p) < 6: return np.nan
    med = np.median(p); u, a = y[p > med], y[p <= med]
    if len(u) < 3 or len(a) < 3: return np.nan
    return u.mean() - a.mean()


from tabfm.src.pytorch import tabfm_v1_0_0
from tabfm import TabFMRegressor
model = tabfm_v1_0_0.load(model_type="regression",
                          checkpoint_path=os.path.join(HERE, "agirlik"), device="cpu")
print("model yuklendi", flush=True)

sat = []
for g in TEST:
    ctx, tst = df[df["gun"] < g], df[df["gun"] == g]
    Xc, Xt = hazirla(ctx, tst)
    r = dict(gun=g, n=len(tst), nctx=len(ctx))
    for et in ("L2", "L1"):
        cm = ctx[et].notna()
        if cm.sum() < 60:
            r["p_" + et] = None; continue
        reg = TabFMRegressor(model=model, n_estimators=A.n_est, random_state=20260826)
        reg.fit(Xc[cm.values], ctx.loc[cm, et].to_numpy(float))
        r["p_" + et] = np.asarray(reg.predict(Xt), float).tolist()
    rs = rho(ctx["score"], ctx["L2"])
    isaret = 1.0 if (np.isfinite(rs) and rs >= 0) else -1.0
    r["p_skor"] = (isaret * tst["score"].to_numpy(float)).tolist()
    r["isaret"] = isaret
    for a in ("L2", "L1", "yon", "chg24", "ret", "defter"):
        r[a] = tst[a].tolist()
    sat.append(r)
    print("  %s  ctx=%-4d tst=%-4d  ust-alt %+7.2f%%  (skor %+7.2f%%)  isaret %+d"
          % (g, len(ctx), len(tst), yari(r["p_L2"], r["L2"]),
             yari(r["p_skor"], r["L2"]), int(isaret)), flush=True)

json.dump(sat, open(os.path.join(HERE, "havuz_sonuc.json"), "w"))
print("\n" + "=" * 104)
print("OLCUTLER — on-kayitta SABIT (e1b30d8)")
print("=" * 104)

f1 = [yari(s["p_L2"], s["L2"]) for s in sat]
m1, t1_, n1 = t_ist(f1)
g1 = (m1 > 0 and t1_ >= 2.0)
print("H1  ust yari - alt yari (getiri %%): %+.3f%% · t=%+.2f · N=%d gun · pozitif %d/%d -> %s"
      % (m1, t1_, n1, sum(1 for x in f1 if np.isfinite(x) and x > 0), n1,
         "GECTI" if g1 else "DUSTU"))

r2 = [rho(s["p_L1"], s["L1"]) for s in sat if s.get("p_L1")]
m2, t2_, n2 = t_ist(r2)
g2 = (m2 > 0 and t2_ >= 2.0)
print("H2  rho(tahmin, ham L1)          : %+.4f · t=%+.2f · N=%d gun            -> %s"
      % (m2, t2_, n2, "GECTI" if g2 else "DUSTU"))

fs = [yari(s["p_skor"], s["L2"]) for s in sat]
ms, ts_, _ = t_ist(fs)
rsk = [rho(s["p_skor"], s["L1"]) for s in sat if s.get("L1")]
ms2, _, _ = t_ist(rsk)
g3 = (np.isfinite(ms) and m1 > ms) and (np.isfinite(ms2) and m2 > ms2)
print("H3  TABAN skor: getiri %+.3f%% (t=%+.2f) · rho %+.4f   -> TabFM gecti mi: %s"
      % (ms, ts_, ms2, "GECTI" if g3 else "DUSTU"))

# H4 — YON x OYNAKLIK, dort alt kume, HEPSI pozitif olmali
tumc = np.abs(np.concatenate([np.array(s["chg24"], float) for s in sat]))
esik = np.nanmedian(tumc)
kol = {}
for yn in ("LONG", "SHORT"):
    for ad, ust in (("dusuk", False), ("yuksek", True)):
        v = []
        for s in sat:
            p = np.array(s["p_L2"], float); y = np.array(s["L2"], float)
            yy = np.array(s["yon"]); cc = np.abs(np.array(s["chg24"], float))
            mm = (yy == yn) & ((cc > esik) if ust else (cc <= esik))
            if mm.sum() < 6: continue
            d = yari(p[mm], y[mm])
            if np.isfinite(d): v.append(d)
        mm_, tt_, nn_ = t_ist(v)
        kol["%s/%s" % (yn, ad)] = (mm_, nn_)
        print("H4  %-14s: %+7.3f%% · N=%d gun" % (yn + "/" + ad, mm_, nn_))
g4 = all(np.isfinite(v[0]) and v[0] > 0 for v in kol.values()) and len(kol) == 4
print("    DORT alt kumenin HEPSI pozitif mi (|chg24| esigi %.1f) -> %s"
      % (esik, "GECTI" if g4 else "DUSTU"))

# H5 — yalniz GERCEK RET (hukme girmez)
v5 = []
for s in sat:
    p = np.array(s["p_L2"], float); y = np.array(s["L2"], float)
    mm = np.array(s["ret"], bool)
    if mm.sum() < 6: continue
    d = yari(p[mm], y[mm])
    if np.isfinite(d): v5.append(d)
m5, t5, n5 = t_ist(v5)
print("H5  yalniz GERCEK RET (hukme girmez): %+.3f%% · t=%+.2f · N=%d gun" % (m5, t5, n5))

print("\n" + "=" * 104)
print("SONUC: %s" % ("SINAMAYA DEGER (H1+H3+H4)" if (g1 and g3 and g4) else "SINAMAYA DEGMEZ"))
print("=" * 104)
