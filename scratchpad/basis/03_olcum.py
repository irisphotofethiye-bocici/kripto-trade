#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BASIS OLCUMU — B1..B5. On-kayit ON_KAYIT.md (2e3ff43). Olcutler SABIT."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, math, datetime, collections
import numpy as np
from scipy import stats

HERE  = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(os.path.dirname(HERE))
import statistics


def rejim_serisi():
    """skor_tahmin_rejim.py:42 ile BIREBIR AYNI mantik, KOPYALANDI.
    🔴 O modul IMPORT EDILMEZ: modul duzeyinde kendi olcumunu kosturuyor
    (REJ = rejim_serisi() ve ardindan tum boru hatti). Import yan etkisi
    baska bir olcumu calistirirdi."""
    with open(os.path.join(PROJE, "scratchpad", "klines_1h_uzun", "BTC.json"),
              encoding="utf-8") as f:
        bars = json.load(f)
    g = {}
    for b in bars:
        d = (datetime.datetime(1970,1,1)+datetime.timedelta(milliseconds=int(b["t"]))).date()
        g[d] = float(b["c"])
    G = sorted(g.items())
    out = {}
    for i in range(len(G)):
        hafta = {}
        for d, c in G[:i+1]:
            hafta[d.isocalendar()[:2]] = (d, c)
        wc = [c for k, (d, c) in sorted(hafta.items())]
        if len(wc) < 21:
            continue
        wo = statistics.mean(wc[-21:-1])
        sezon = ("BOGA" if (wc[-1] > wo and wc[-1]-wc[-21] > 0)
                 else ("AYI" if (wc[-1] < wo and wc[-1]-wc[-21] < 0) else "NOTR"))
        cl = [c for d, c in G[max(0, i-59):i+1]]
        ham = []
        for j in range(20, len(cl)):
            sma = statistics.mean(cl[j-20:j])
            uz = (cl[j]-sma)/sma*100
            ham.append("NOTR" if abs(uz) < 2.0 else ("BOGA" if uz > 0 else "AYI"))
        hava = ham[0] if ham else "NOTR"
        for j in range(len(ham)):
            if j < 3:
                hava = ham[j]
            else:
                pen = ham[j-2:j+1]
                if all(x == pen[0] for x in pen):
                    hava = pen[0]
        if sezon == "AYI" and hava == "BOGA":   f10 = "TEPKI_RALLISI"
        elif sezon == "BOGA" and hava == "BOGA": f10 = "TAM_BOGA"
        elif sezon == "AYI" and hava == "AYI":   f10 = "DERIN_AYI"
        elif sezon == "BOGA" and hava == "AYI":  f10 = "BOGA_DUZELTME"
        else:                                    f10 = "BELIRSIZ"
        # ANAHTAR: 'YYYY-MM-DD' string  ·  DEGER: 3'lu rejim
        out[G[i][0].isoformat()] = ("BOGA" if f10 == "TAM_BOGA"
                                    else ("AYI" if f10 in ("TEPKI_RALLISI","DERIN_AYI")
                                          else "NOTR"))
    return out

S = json.load(open(os.path.join(HERE, "veri.json"), encoding="utf-8"))
print("BASIS OLCUMU — on-kayit 2e3ff43")
print("=" * 96)
print("gozlem %d" % len(S))

gun = collections.defaultdict(list)
for r in S:
    gun[r["gun"]].append(r)
GUN = sorted(gun)
print("gun %d  (%s .. %s)" % (len(GUN), GUN[0], GUN[-1]))


def gun_rho(kayitlar, suzgec=None):
    """Her gun KESITSEL rho(basis, +24s). Gun listesi doner."""
    out = []
    for g in GUN:
        rs = kayitlar.get(g, [])
        if suzgec:
            rs = [r for r in rs if suzgec(r)]
        if len(rs) < 20:
            continue
        b = np.array([r["basis"] for r in rs], float)
        y = np.array([r["y"] for r in rs], float)
        m = np.isfinite(b) & np.isfinite(y)
        if m.sum() < 20 or len(set(b[m])) < 5:
            continue
        out.append((g, stats.spearmanr(b[m], y[m]).statistic))
    return out


def t_ist(v):
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    if len(v) < 5:
        return np.nan, np.nan, len(v)
    sd = v.std(ddof=1)
    return v.mean(), (v.mean()/(sd/math.sqrt(len(v))) if sd > 0 else np.nan), len(v)


# ---------------------------------------------------------------- B1
ana = gun_rho(gun)
rho = [x[1] for x in ana]
m1, t1, n1 = t_ist(rho)
b1 = (abs(m1) >= 0.02 and abs(t1) >= 3.0)
print("\n" + "=" * 96)
print("B1  gun-ici kesitsel rho(basis, +24s), gun-kumeli")
print("    ort rho %+.4f · t=%+.2f · N=%d gun · pozitif gun %d (%%%.0f)"
      % (m1, t1, n1, sum(1 for x in rho if x > 0), 100*sum(1 for x in rho if x > 0)/max(n1,1)))
print("    esik |rho|>=0,02 VE |t|>=3,0   ->  %s" % ("GECTI" if b1 else "DUSTU"))
ISARET = 1 if m1 > 0 else -1
print("    ISARET: %s  (hipotez NEGATIF idi -> %s)"
      % ("POZITIF" if ISARET > 0 else "NEGATIF",
         "hipotez yonunde" if ISARET < 0 else "TERS -> 'ters isaretli bulgu'"))

# ---------------------------------------------------------------- B2 ceyrekler
print("\nB2  pencerenin DORT CEYREGI")
q = len(ana) // 4
ceyrek = [ana[i*q:(i+1)*q] if i < 3 else ana[3*q:] for i in range(4)]
b2ok = []
for i, c in enumerate(ceyrek):
    mm, tt, nn = t_ist([x[1] for x in c])
    b2ok.append(np.isfinite(mm) and (mm > 0) == (m1 > 0))
    print("    C%d %s..%s  rho %+.4f · t=%+.2f · N=%d  %s"
          % (i+1, c[0][0], c[-1][0], mm, tt, nn, "ayni" if b2ok[-1] else "TERS"))
b2 = all(b2ok)
print("    dordu de ayni isaret mi -> %s" % ("GECTI" if b2 else "DUSTU"))

# ---------------------------------------------------------------- B3 rejim
print("\nB3  REJIM (BTC mumundan YENIDEN URETILDI)")
try:
    RJ = rejim_serisi()
    _d = collections.Counter(RJ.values())
    print("    uretilen rejim gunu: %d  %s" % (len(RJ), dict(_d)))
except Exception as e:
    print("    rejim uretilemedi: %s" % str(e)[:70])
    RJ = {}
if isinstance(RJ, dict) and RJ:
    ok3 = []
    for rj in ("BOGA", "AYI", "NOTR"):
        gg = {g: v for g, v in gun.items() if RJ.get(g) == rj}
        rr = [x[1] for x in gun_rho(gg)]
        mm, tt, nn = t_ist(rr)
        ayni = np.isfinite(mm) and (mm > 0) == (m1 > 0)
        ok3.append(ayni if nn >= 20 else False)
        print("    %-5s rho %+.4f · t=%+.2f · N=%d gun   %s"
              % (rj, mm, tt, nn, "ayni" if ayni else "TERS/YETERSIZ"))
    b3 = all(ok3)
else:
    b3 = False
    print("    REJIM SERISI ALINAMADI -> B3 DUSTU (veri eksigi, hukumde belirtilecek)")
print("    ucu de ayni isaret mi -> %s" % ("GECTI" if b3 else "DUSTU"))

# ---------------------------------------------------------------- B4/B5
def uctebirlik(ad, alan):
    v = np.array([r[alan] for r in S if r.get(alan) is not None], float)
    q1, q2 = np.nanpercentile(v, [33.33, 66.67])
    print("\n%s  KARISTIRICI: %s uctebirlikleri (esik %.4f / %.4f)" % (ad, alan, q1, q2))
    ok = []
    for lab, lo, hi in (("alt", -np.inf, q1), ("orta", q1, q2), ("ust", q2, np.inf)):
        f = lambda r: (r.get(alan) is not None and lo < r[alan] <= hi)
        rr = [x[1] for x in gun_rho(gun, f)]
        mm, tt, nn = t_ist(rr)
        ayni = np.isfinite(mm) and (mm > 0) == (m1 > 0)
        ok.append(ayni if nn >= 20 else False)
        print("    %-5s rho %+.4f · t=%+.2f · N=%d gun   %s"
              % (lab, mm, tt, nn, "ayni" if ayni else "TERS/YETERSIZ"))
    r = all(ok)
    print("    ucunde de ayni isaret mi -> %s" % ("GECTI" if r else "DUSTU"))
    return r

b4 = uctebirlik("B4", "funding")
b5 = uctebirlik("B5", "chg24")

print("\n" + "=" * 96)
gecti = b1 and b2 and b3 and b4 and b5
print("HUKUM: %s" % ("GECTI — B1+B2+B3+B4+B5" if gecti else "DUSTU"))
print("=" * 96)
print("B1 %s · B2 %s · B3 %s · B4 %s · B5 %s"
      % (*(("GECTI" if x else "DUSTU") for x in (b1, b2, b3, b4, b5)),))
json.dump({"ana": ana}, open(os.path.join(HERE, "sonuc.json"), "w"))
