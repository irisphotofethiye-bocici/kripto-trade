#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""POZISYON KOMPOZISYONU — OI / long-short / taker, SHORT girislerini ayiriyor mu?
On-kayit: ON_KAYIT.md (sonuc gorulmeden yazildi; GUC SINIRI orada ilan edildi).
Tasarim: GUN ICI ESLESTIRME — piyasa gunluk hareketi tanimi geregi sabitlenir.
SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, glob, math, bisect, datetime, collections, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
SERI = os.path.join(os.path.dirname(HERE), "perp_seri")
P24 = 288                      # 24 saat = 288 x 5dk
UF = {1: 12, 4: 48, 24: 288}   # saat -> bar
PUMP = 20.0

def yukle(sym, tip, alan, olcek=1.0):
    y = os.path.join(SERI, "%s_%s.json" % (sym, tip))
    if not os.path.exists(y): return [], []
    try: d = json.load(open(y, encoding="utf-8"))
    except Exception: return [], []
    t, v = [], []
    for x in d:
        ts = x.get("timestamp") or x.get("t")
        if ts is None or alan not in x: continue
        try: val = float(x[alan]) * olcek
        except Exception: continue
        t.append(int(ts)); v.append(val)
    z = sorted(zip(t, v))
    return [a for a, _ in z], [b for _, b in z]

def deger(t, v, ts, geri=0):
    """ts anindaki deger (ileriye bakma yok). geri>0 ise ts-geri'ye gore % degisim."""
    if not t: return None
    i = bisect.bisect_right(t, ts) - 1
    if i < 0: return None
    if not geri: return v[i]
    j = bisect.bisect_right(t, ts - geri) - 1
    if j < 0 or v[j] == 0: return None
    return (v[i] / v[j] - 1) * 100

DEG = ("d_oi_3s", "d_oi_24s", "top_ls", "d_top_ls", "glob_ls", "fark_ls", "taker")
olay = []
for f in sorted(glob.glob(os.path.join(SERI, "*_kline.json"))):
    sym = os.path.basename(f)[:-11]
    try: b = json.load(open(f, encoding="utf-8"))
    except Exception: continue
    if len(b) < P24 + max(UF.values()) + 10: continue
    t = [x["t"] for x in b]; c = [float(x["c"]) for x in b]
    oit, oiv = yukle(sym, "oi", "sumOpenInterestValue")
    tlt, tlv = yukle(sym, "top_ls", "longShortRatio")
    glt, glv = yukle(sym, "glob_ls", "longShortRatio")
    tkt, tkv = yukle(sym, "taker", "buySellRatio")
    son = -10**9
    for i in range(P24, len(c) - max(UF.values())):
        if c[i-P24] <= 0 or c[i] <= 0: continue
        if (c[i]/c[i-P24] - 1) * 100 < PUMP: continue
        if i - son < P24//2: continue
        son = i
        ts = t[i]
        d = {"sym": sym, "t": ts,
             "gun": datetime.datetime.utcfromtimestamp(ts/1000).strftime("%Y-%m-%d")}
        d["d_oi_3s"]  = deger(oit, oiv, ts, 3*3600*1000)
        d["d_oi_24s"] = deger(oit, oiv, ts, 24*3600*1000)
        d["top_ls"]   = deger(tlt, tlv, ts)
        d["d_top_ls"] = deger(tlt, tlv, ts, 3*3600*1000)
        d["glob_ls"]  = deger(glt, glv, ts)
        gl = deger(glt, glv, ts)
        d["fark_ls"]  = (d["top_ls"] - gl) if (d["top_ls"] is not None and gl is not None) else None
        d["taker"]    = deger(tkt, tkv, ts)
        for h, n in UF.items():
            d["ham%d" % h] = (c[i] - c[i+n]) / c[i] * 100        # SHORT ham getiri
        olay.append(d)

print("=" * 96)
print("POZISYON KOMPOZISYONU — SHORT pump girisleri")
print("N=%d olay · %d gun · %d sembol   (on-kayit: GUC SINIRI ilan edildi)"
      % (len(olay), len(set(x["gun"] for x in olay)), len(set(x["sym"] for x in olay))))
print("=" * 96)
cs = collections.Counter(x["sym"] for x in olay); cg = collections.Counter(x["gun"] for x in olay)
print("  yogunlasma: en buyuk sembol payi %%%.1f · en buyuk gun payi %%%.1f  (olcut 4: <%%15)"
      % (100*cs.most_common(1)[0][1]/len(olay), 100*cg.most_common(1)[0][1]/len(olay)))

def gun_ici(v, alan, hedef):
    """Her GUN icinde ust yari - alt yari farki. -> gunluk fark listesi"""
    g = collections.defaultdict(list)
    for x in v:
        if x.get(alan) is not None: g[x["gun"]].append((x[alan], x[hedef]))
    out = []
    for gun, z in g.items():
        if len(z) < 4: continue
        z.sort()
        k = len(z)//2
        alt = [y for _, y in z[:k]]; ust = [y for _, y in z[len(z)-k:]]
        out.append(sx.mean(ust) - sx.mean(alt))
    return out

def t_ist(v):
    if len(v) < 3: return None, None, len(v)
    m = sx.mean(v); s = sx.stdev(v)
    return m, (m/(s/math.sqrt(len(v))) if s > 0 else None), len(v)

print("\n--- OLCUT 1+2: GUN ICI ESLESMIS FARK (ust yari - alt yari, SHORT ham getiri) ---")
print("  %-11s | %-22s %-22s %-22s | tutarli?" % ("degisken", "1 saat", "4 saat", "24 saat"))
for a in DEG:
    sat = "  %-11s |" % a; isaretler = []
    for h in (1, 4, 24):
        m, t_, n = t_ist(gun_ici(olay, a, "ham%d" % h))
        if m is None: sat += " %-22s" % "(yetersiz)"; continue
        isaretler.append(1 if m > 0 else -1)
        yildiz = " *" if t_ and abs(t_) >= 2.0 else "  "
        sat += " %+7.3f t=%+5.2f n=%-2d%s" % (m, t_ or 0, n, yildiz)
    if isaretler:
        ayni = max(isaretler.count(1), isaretler.count(-1))
        sat += " | %d/3 %s" % (ayni, "GECTI" if ayni >= 2 else "KALDI")
    print(sat)
print("     (* = |t| >= 2,0 — olcut 1)")

print("\n--- OLCUT 3: HOLDOUT (32 gun ikiye) ---")
gunler = sorted(set(x["gun"] for x in olay)); yari = gunler[len(gunler)//2]
for a in DEG:
    sat = "  %-11s" % a
    for ad, v in (("ILK", [x for x in olay if x["gun"] < yari]),
                  ("SON", [x for x in olay if x["gun"] >= yari])):
        m, t_, n = t_ist(gun_ici(v, a, "ham4"))
        sat += "   %s %s" % (ad, ("%+.3f(n%d)" % (m, n)) if m is not None else "(yetersiz)")
    print(sat)

print("\n--- DEGISKEN DAGILIMLARI (betimleyici) ---")
for a in DEG:
    v = sorted(x[a] for x in olay if x.get(a) is not None)
    if len(v) < 20: print("  %-11s (N=%d yetersiz)" % (a, len(v))); continue
    print("  %-11s N=%-4d  %%25 %+8.3f  MED %+8.3f  %%75 %+8.3f" % (a, len(v), v[len(v)//4], v[len(v)//2], v[3*len(v)//4]))
