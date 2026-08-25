#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TabFM INDIKATOR OLABILIR MI — olcum. On-kayit ON_KAYIT.md (43b0785).
Olcutler S1..S5 SABIT, sonuc gorulduikten sonra DEGISTIRILMEZ.

Gun-bloklu ileri dogrulama: baglam 1..k, test k+1, k>=7.
SALT OKUMA. Bota/deftere dokunmaz.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, time, math, argparse
import numpy as np, pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("HF_HOME", os.path.join(HERE, "hf_cache"))

ap = argparse.ArgumentParser()
ap.add_argument("--n-est", type=int, default=8)
ap.add_argument("--sure-probu", action="store_true", help="tek gun, SADECE sure basar")
ap.add_argument("--min-baglam-gun", type=int, default=7)
ap.add_argument("--ckpt", default=os.path.join(HERE, "agirlik"))
ap.add_argument("--gun", default=None, help="sure probu icin tek gun")
A = ap.parse_args()

D = json.load(open(os.path.join(HERE, "veri.json"), encoding="utf-8"))
SAY, KAT, GUNLER = D["sayisal"], D["kategorik"], D["gunler"]
df = pd.DataFrame(D["satir"])
print("veri: %d satir · %d gun · ufuk +%ds" % (len(df), len(GUNLER), D["ufuk"]))

TEST_GUN = GUNLER[A.min_baglam_gun:]
print("test gunu: %d  (%s .. %s)   baglam >= %d gun"
      % (len(TEST_GUN), TEST_GUN[0], TEST_GUN[-1], A.min_baglam_gun))
if len(TEST_GUN) != 14:
    print("  [SAPMA] on-kayit 14 test gunu yaziyordu; +24s etiketi son gunu dusurdu"
          " ve 08-23 HALT_DUSUS nedeniyle bos. Esikler DEGISMEDI.")

ALANLAR = SAY + KAT


def hazirla(ctx, tst):
    """Baglam medyaniyla doldur (SIZINTI YOK: test gunu kullanilmaz)."""
    Xc, Xt = ctx[ALANLAR].copy(), tst[ALANLAR].copy()
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
    if m.sum() < 10 or len(set(a[m])) < 3:
        return np.nan
    return stats.spearmanr(a[m], b[m]).statistic


def t_ist(v):
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    if len(v) < 3:
        return np.nan, np.nan, len(v)
    return v.mean(), v.mean() / (v.std(ddof=1) / math.sqrt(len(v))), len(v)


# ---------------------------------------------------------------- model
from tabfm.src.pytorch import tabfm_v1_0_0
from tabfm import TabFMRegressor

t0 = time.time()
model = tabfm_v1_0_0.load(model_type="regression", checkpoint_path=A.ckpt, device="cpu")
print("model yuklendi (%.0f sn)" % (time.time() - t0), flush=True)

sat = []
if A.gun:
    TEST_GUN = [A.gun]

for gi, g in enumerate(TEST_GUN):
    # AMBARGO: etiket ufku +24s oldugu icin son baglam gununun etiketi TEST
    # gunune bakiyor (baglamin %4-12si). Ozellik sizmiyor ama SONUC siziyor.
    # Bulundu 2026-08-25, kosumdan ONCE. Olcut esikleri DEGISMEDI.
    onceki = [x for x in GUNLER if x < g]
    ctx = df[df["gun"].isin(onceki[:-1])] if len(onceki) > 1 else df[df["gun"] < g]
    tst = df[df["gun"] == g]
    if len(tst) < 20 or len(ctx) < 200:
        print("  %s ATLANDI (ctx=%d tst=%d)" % (g, len(ctx), len(tst)))
        continue
    Xc, Xt = hazirla(ctx, tst)
    yc, yt = ctx["y"].to_numpy(float), tst["y"].to_numpy(float)

    ta = time.time()
    reg = TabFMRegressor(model=model, n_estimators=A.n_est, random_state=20260825)
    reg.fit(Xc, yc)
    pred = np.asarray(reg.predict(Xt), float)
    sn = time.time() - ta

    if A.sure_probu:
        print("SURE PROBU: %s  ctx=%d tst=%d  n_est=%d  ->  %.1f sn"
              % (g, len(ctx), len(tst), A.n_est, sn))
        raise SystemExit(0)

    # --- tabanlar: ISARET/ALAN yalniz BAGLAM gunlerinden secilir ---
    r_s = rho(ctx["score"], yc)
    isaret_s = 1.0 if (np.isfinite(r_s) and r_s >= 0) else -1.0
    base_s = isaret_s * tst["score"].to_numpy(float)

    en_iyi, en_iyi_r = None, 0.0
    for a in SAY:
        rr = rho(pd.to_numeric(ctx[a], errors="coerce"), yc)
        if np.isfinite(rr) and abs(rr) > abs(en_iyi_r):
            en_iyi, en_iyi_r = a, rr
    isaret_b = 1.0 if en_iyi_r >= 0 else -1.0
    base_b = isaret_b * pd.to_numeric(tst[en_iyi], errors="coerce").to_numpy(float)

    sat.append(dict(gun=g, n=len(tst), nctx=len(ctx), sn=sn,
                    rho_tab=rho(pred, yt), rho_skor=rho(base_s, yt),
                    rho_base=rho(base_b, yt), alan=en_iyi,
                    pred=pred.tolist(), y=yt.tolist(),
                    atr=tst["atr"].to_numpy(float).tolist()))
    print("  %s  ctx=%-5d tst=%-4d %5.0fsn   rho: TabFM %+.3f · skor %+.3f · %s %+.3f"
          % (g, len(ctx), len(tst), sn, sat[-1]["rho_tab"], sat[-1]["rho_skor"],
             en_iyi[:9], sat[-1]["rho_base"]), flush=True)

json.dump(sat, open(os.path.join(HERE, "ham_sonuc.json"), "w"))
print("\n" + "=" * 96)
print("OLCUTLER — on-kayitta SABIT")
print("=" * 96)

rt = [s["rho_tab"] for s in sat]
rs = [s["rho_skor"] for s in sat]
rb = [s["rho_base"] for s in sat]

m, t, n = t_ist(rt)
print("S1  rho > 0 ve t >= 2,0        : rho ort %+.4f  t=%+.2f  N=%d gun   -> %s"
      % (m, t, n, "GECTI" if (m > 0 and t >= 2.0) else "DUSTU"))

d2 = [a - b for a, b in zip(rt, rs)]
m2, t2, n2 = t_ist(d2)
print("S2  TabFM - skor(isaretli)     : fark %+.4f  t=%+.2f  N=%d      -> %s"
      % (m2, t2, n2, "GECTI" if t2 >= 2.0 else "DUSTU"))

d3 = [a - b for a, b in zip(rt, rb)]
m3, t3, n3 = t_ist(d3)
print("S3  TabFM - en iyi tek alan    : fark %+.4f  t=%+.2f  N=%d      -> %s"
      % (m3, t3, n3, "GECTI" if t3 >= 1.5 else "DUSTU"))

# S4 karistirici: gun x ATR-uctebirlik hucrelerinde ust yari - alt yari
poz = tot = 0
for s in sat:
    p, y, a = np.array(s["pred"]), np.array(s["y"]), np.array(s["atr"])
    if len(p) < 30:
        continue
    q = np.quantile(a, [1/3, 2/3])
    for lo, hi in ((-np.inf, q[0]), (q[0], q[1]), (q[1], np.inf)):
        m_ = (a > lo) & (a <= hi)
        if m_.sum() < 10:
            continue
        pp, yy = p[m_], y[m_]
        med = np.median(pp)
        ust, alt = yy[pp > med], yy[pp <= med]
        if len(ust) < 3 or len(alt) < 3:
            continue
        tot += 1
        poz += 1 if (ust.mean() - alt.mean()) > 0 else 0
oran = 100.0 * poz / tot if tot else float("nan")
print("S4  gun x ATR hucresi pozitif  : %d/%d = %%%.1f (esik %%60)         -> %s"
      % (poz, tot, oran, "GECTI" if oran >= 60 else "DUSTU"))

y1, y2 = rt[:7], rt[7:]
m1_, _, _ = t_ist(y1)
m2_, _, _ = t_ist(y2)
ayni = np.isfinite(m1_) and np.isfinite(m2_) and (m1_ > 0) == (m2_ > 0)
print("S5  ilk 7 / son %d test gunu    : %+.4f  vs  %+.4f              -> %s"
      % (len(y2), m1_, m2_, "GECTI" if ayni else "DUSTU"))

gecti = ((m > 0 and t >= 2.0) and t2 >= 2.0 and t3 >= 1.5 and oran >= 60 and ayni)
print("\n" + "=" * 96)
print("HUKUM: %s" % ("GECTI - tum olcutler" if gecti else "DUSTU"))
print("=" * 96)
# ---------------------------------------------------------------- IKINCIL
# HUKME GIRMEZ. S1..S5 on-kayitli ve YUKARIDA karara baglandi.
# "Olay seviyesi" gorunumu: getirinin %91'i GUN ICI, coinler arasi yasiyor.
# "Ayiriyor mu" 3.598 sembol-saatte olculur; "zamanda tutuyor mu" 13 gunde.
print("\n" + "-" * 96)
print("IKINCIL - olay seviyesi (HUKME GIRMEZ)")
print("-" * 96)
_tp, _ty = [], []
for _s in sat:
    _p = np.array(_s["pred"], float); _y = np.array(_s["y"], float)
    _tp.append(_p - _p.mean()); _ty.append(_y - _y.mean())   # gun ort. ARINDIRILDI
_tp = np.concatenate(_tp); _ty = np.concatenate(_ty)
print("  gun-ici arindirilmis havuz rho : %+.4f   N=%d sembol-saat" % (rho(_tp, _ty), len(_tp)))
print("  gun-rho dagilimi               : min %+.3f . medyan %+.3f . max %+.3f"
      % (np.nanmin(rt), np.nanmedian(rt), np.nanmax(rt)))
print("  pozitif gun                    : %d/%d" % (sum(1 for x in rt if x > 0), len(rt)))
print("  NOT: havuz rho'nun t'si gun-kumelemesini YOK SAYAR -> guveni SISIRIR.")
print("       Karar yukaridaki gun-kumeli olcutlerle verildi.")

print("\nsecilen en iyi tek alan (gun gun):")
for s in sat:
    print("   %s  %s" % (s["gun"], s["alan"]))
