#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TabFM KUTUNUN DISINDA — D1..D5. On-kayit e1b6457. Olcutler SABIT."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, math, time, argparse
import numpy as np, pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--n-est", type=int, default=8)
ap.add_argument("--ctx-cap", type=int, default=2500)
ap.add_argument("--sure-probu", action="store_true")
A = ap.parse_args()
RNG = np.random.default_rng(20260827)

D = json.load(open(os.path.join(HERE, "kutu_disi_veri.json"), encoding="utf-8"))
SAY, KAT, TEST = D["sayisal"], D["kategorik"], D["test_gun"]
df = pd.DataFrame(D["satir"])
ALAN = SAY + KAT
print("KUTU DISI OLCUM — on-kayit e1b6457")
print("=" * 104)
print("gozlem %d · test gunu %d · n_est=%d · baglam cap=%d · bosluk kaydi %d"
      % (len(df), len(TEST), A.n_est, A.ctx_cap, D.get("bosluk", 0)))
print("girdi %d alan · score OZELLIK DEGIL (yalniz ust-veri)" % len(ALAN))


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
    if m.sum() < 30 or len(set(a[m])) < 5:
        return np.nan
    return stats.spearmanr(a[m], b[m]).statistic


def t_ist(v):
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    if len(v) < 5:
        return np.nan, np.nan, len(v)
    sd = v.std(ddof=1)
    return v.mean(), (v.mean() / (sd / math.sqrt(len(v))) if sd > 0 else np.nan), len(v)


def sepet(deger, y, saat, n=10, rastgele=False):
    """Her SAAT icin en iyi n secilir, getirilerinin ortalamasi alinir."""
    out = []
    for s in np.unique(saat):
        m = saat == s
        d, yy = deger[m], y[m]
        k = np.isfinite(d) & np.isfinite(yy)
        d, yy = d[k], yy[k]
        if len(d) < n + 5:
            continue
        idx = RNG.choice(len(d), n, replace=False) if rastgele else np.argsort(-d)[:n]
        out.append(yy[idx].mean())
    return float(np.mean(out)) if out else np.nan


from tabfm.src.pytorch import tabfm_v1_0_0
from tabfm import TabFMRegressor
model = tabfm_v1_0_0.load(model_type="regression",
                          checkpoint_path=os.path.join(HERE, "agirlik"), device="cpu")
print("model yuklendi", flush=True)

sat = []
for g in TEST:
    onceki = [x for x in D["gun"] if x < g]
    # AMBARGO: son baglam gunu atilir (onceki kosumlarla ayni)
    ctx = df[df["gun"].isin(onceki[:-1])] if len(onceki) > 1 else df[df["gun"] < g]
    tst = df[df["gun"] == g]
    if len(ctx) < 300 or len(tst) < 100:
        print("  %s ATLANDI (ctx=%d tst=%d)" % (g, len(ctx), len(tst)))
        continue
    if len(ctx) > A.ctx_cap:                    # BAGLAM ORNEKLEMI (on-kayitta)
        ctx = ctx.iloc[RNG.choice(len(ctx), A.ctx_cap, replace=False)]
    Xc, Xt = hazirla(ctx, tst)
    ta = time.time()
    reg = TabFMRegressor(model=model, n_estimators=A.n_est, random_state=20260827)
    reg.fit(Xc, ctx["y"].to_numpy(float))
    pred = np.asarray(reg.predict(Xt), float)
    sn = time.time() - ta
    if A.sure_probu:
        print("SURE PROBU %s ctx=%d tst=%d n_est=%d -> %.1f sn"
              % (g, len(ctx), len(tst), A.n_est, sn))
        raise SystemExit(0)
    y = tst["y"].to_numpy(float)
    saat = tst["saat"].to_numpy()
    sk = tst["skor_bot"].to_numpy(float)
    r = dict(gun=g, n=len(tst), nctx=len(ctx), sn=sn,
             rho=rho(pred, y),
             s_tab=sepet(pred, y, saat), s_rast=sepet(pred, y, saat, rastgele=True),
             s_bot=sepet(sk, y, saat), s_ters=sepet(-sk, y, saat),
             pred=pred.tolist(), y=y.tolist(),
             atr=tst["atr_pct"].to_numpy(float).tolist(),
             rejim=tst["rejim_yeni"].tolist())
    sat.append(r)
    print("  %s ctx=%-5d tst=%-5d %5.0fsn  rho %+.4f  sepet: TabFM %+.3f · rastgele %+.3f · bot %+.3f"
          % (g, len(ctx), len(tst), sn, r["rho"], r["s_tab"], r["s_rast"], r["s_bot"]),
          flush=True)

json.dump([{k: v for k, v in s.items() if k not in ("pred", "y", "atr", "rejim")}
           for s in sat], open(os.path.join(HERE, "kutu_disi_ozet.json"), "w"))

print("")
print("=" * 104)
print("OLCUTLER — on-kayitta SABIT (e1b6457)")
print("=" * 104)

r1 = [s["rho"] for s in sat]
m1, t1, n1 = t_ist(r1)
d1 = (m1 > 0 and t1 >= 2.0 and abs(m1) >= 0.03)
print("D1  rho(tahmin, ham +2s)      : %+.4f · t=%+.2f · N=%d gun · pozitif %d/%d"
      % (m1, t1, n1, sum(1 for x in r1 if x > 0), n1))
print("    esik rho>0 · t>=2,0 · |rho|>=0,03  -> %s" % ("GECTI" if d1 else "DUSTU"))

d2v = [s["s_tab"] - s["s_rast"] for s in sat]
m2, t2, n2 = t_ist(d2v)
d2 = (m2 > 0 and t2 >= 2.0)
print("D2  SEPET TabFM - RASTGELE    : %+.4f%% · t=%+.2f · N=%d gun · pozitif %d/%d  -> %s"
      % (m2, t2, n2, sum(1 for x in d2v if x > 0), n2, "GECTI" if d2 else "DUSTU"))


def dilim(baslik, alan):
    v = np.concatenate([np.array(s[alan], float) for s in sat])
    q = np.nanpercentile(v, [33.33, 66.67])
    ok = []
    print("")
    print("%s (esik %.3f / %.3f)" % (baslik, q[0], q[1]))
    for lab, lo, hi in (("dusuk", -np.inf, q[0]), ("orta", q[0], q[1]),
                        ("yuksek", q[1], np.inf)):
        vv = []
        for s in sat:
            p = np.array(s["pred"], float)
            y = np.array(s["y"], float)
            c = np.array(s[alan], float)
            m = (c > lo) & (c <= hi)
            if m.sum() < 30:
                continue
            rr = rho(p[m], y[m])
            if np.isfinite(rr):
                vv.append(rr)
        mm, tt, nn = t_ist(vv)
        ayni = np.isfinite(mm) and (mm > 0) == (m1 > 0)
        ok.append(ayni if nn >= 15 else False)
        print("    %-7s rho %+.4f · t=%+.2f · N=%d gun   %s"
              % (lab, mm, tt, nn, "ayni" if ayni else "TERS/YETERSIZ"))
    return all(ok)


d3 = dilim("D3  KARISTIRICI: oynaklik (ATR/fiyat)", "atr")
print("    ucunde de ayni isaret mi -> %s" % ("GECTI" if d3 else "DUSTU"))

print("")
print("D4  KARISTIRICI: REJIM (BTC mumundan YENIDEN URETILDI)")
ok4 = []
for rj in ("BOGA", "AYI", "NOTR"):
    vv = []
    for s in sat:
        p = np.array(s["pred"], float)
        y = np.array(s["y"], float)
        m = np.array([x == rj for x in s["rejim"]], bool)
        if m.sum() < 30:
            continue
        rr = rho(p[m], y[m])
        if np.isfinite(rr):
            vv.append(rr)
    mm, tt, nn = t_ist(vv)
    ayni = np.isfinite(mm) and (mm > 0) == (m1 > 0)
    ok4.append(ayni if nn >= 10 else False)
    print("    %-5s rho %+.4f · t=%+.2f · N=%d gun   %s"
          % (rj, mm, tt, nn, "ayni" if ayni else "TERS/YETERSIZ"))
d4 = all(ok4)
print("    ucunde de ayni isaret mi -> %s" % ("GECTI" if d4 else "DUSTU"))

print("")
print("D5  BETIMLEYICI — sepetler (HUKME GIRMEZ)")
for ad, k in (("TabFM en iyi 10", "s_tab"), ("RASTGELE 10", "s_rast"),
              ("BOT en iyi 10 (skor)", "s_bot"), ("TERS-SKOR 10", "s_ters")):
    mm, tt, nn = t_ist([s[k] for s in sat])
    print("    %-22s ort %+.4f%% · t=%+.2f · N=%d gun" % (ad, mm, tt, nn))

print("")
print("=" * 104)
print("HUKUM: %s" % ("GECTI — D1+D2+D3+D4" if (d1 and d2 and d3 and d4) else "DUSTU"))
print("=" * 104)
print("D1 %s · D2 %s · D3 %s · D4 %s"
      % (*(("GECTI" if x else "DUSTU") for x in (d1, d2, d3, d4)),))
