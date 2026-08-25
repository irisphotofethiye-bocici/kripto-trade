#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PIYASA GENELI FONLAMA — SHORT girislerini uyariyor mu?
On-kayit: ON_KAYIT.md (sonuc gorulmeden yazildi).
HAM fiyat getirisi ile FONLAMA GELIRI AYRI olculur. SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, sys, json, glob, math, bisect, datetime, collections, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
sys.path.insert(0, SCRATCH)
import fonlama_oku as FO                                        # noqa: E402

KL = os.path.join(SCRATCH, "klines_1h_uzun")
seri = json.load(open(os.path.join(HERE, "seri.json"), encoding="utf-8"))
sts = sorted(int(k) for k in seri)
PUMP, BEKLEME = 20.0, 24
UF = (4, 24)

# BTC drawdown rejimi (16_rejim_kosullu ile ayni)
rt, rv = [], []
z = 0.0
for x in json.load(open(os.path.join(KL, "BTC.json"), encoding="utf-8")):
    z = max(z, x["h"]); dd = (x["c"] - z) / z * 100 if z else 0.0
    rt.append(x["t"]); rv.append("ATH_BOLGESI" if dd > -10 else "DUZELTME" if dd > -30 else "DERIN_AYI")

olay = []
for f in sorted(glob.glob(os.path.join(KL, "*.json"))):
    sym = os.path.basename(f)[:-5]
    try: b = json.load(open(f, encoding="utf-8"))
    except Exception: continue
    if len(b) < 200: continue
    ft, fr = FO.yukle(sym)
    c = [x["c"] for x in b]; t = [x["t"] for x in b]
    son = -10**9
    for i in range(25, len(b) - max(UF) - 1):
        if c[i] <= 0 or c[i-24] <= 0: continue
        if (c[i]/c[i-24] - 1) * 100 < PUMP: continue
        if i - son < BEKLEME: continue
        son = i
        j = bisect.bisect_right(sts, t[i]) - 1
        if j < 0 or t[i] - sts[j] > 12*3600*1000: continue
        s = seri[str(sts[j])]
        k = bisect.bisect_right(rt, t[i]) - 1
        d = {"sym": sym, "t": t[i], "rejim": rv[k] if k >= 0 else "?",
             "gun": datetime.datetime.utcfromtimestamp(t[i]/1000).strftime("%Y-%m-%d"),
             "ort": s["ort"], "poz_pay": s["poz_pay"], "btc24": 0.0}
        # btc24 asagida BTC mumundan doldurulur
        for h in UF:
            d["ham%d" % h] = (c[i] - c[i+h]) / c[i] * 100          # SHORT ham getiri
            d["fon%d" % h] = FO.dilim(ft, fr, t[i], t[i+h], "SHORT")
        olay.append(d)

# BTC 24sa getirisini seriden degil, BTC mumundan al (karistirici kontrolu)
btc = json.load(open(os.path.join(KL, "BTC.json"), encoding="utf-8"))
bt = [x["t"] for x in btc]; bc = [x["c"] for x in btc]
for d in olay:
    i = bisect.bisect_right(bt, d["t"]) - 1
    d["btc24"] = (bc[i]/bc[i-24] - 1) * 100 if i >= 24 and bc[i-24] > 0 else 0.0

json.dump(olay, open(os.path.join(HERE, "olaylar.json"), "w"))
print("=" * 100)
print("FONLAMA REJIMI — SHORT olaylari  N=%s · %d gun · %d sembol"
      % (format(len(olay), ","), len(set(x["gun"] for x in olay)), len(set(x["sym"] for x in olay))))
print("=" * 100)

KES_ORT = (-0.0095, -0.0032, 0.0020)       # on-kayitta yazili ceyrekler
kv = lambda o: 0 if o < KES_ORT[0] else 1 if o < KES_ORT[1] else 2 if o < KES_ORT[2] else 3
AD = ("ort<-0,0095", "-0,0095..-0,0032", "-0,0032..+0,0020", "ort>+0,0020")

def gk(v, a):
    g = collections.defaultdict(list)
    for x in v: g[x["gun"]].append(x[a])
    return [sx.mean(z) for z in g.values()]

def welch(a, b):
    if len(a) < 3 or len(b) < 3: return None, None
    se = math.sqrt(sx.variance(a)/len(a) + sx.variance(b)/len(b))
    f = sx.mean(a) - sx.mean(b)
    return f, (f/se if se > 0 else None)

print("\n--- OLCUT 1: MONOTONLUK  (HAM fiyat getirisi, gun-kumeli) ---")
print("  %-20s %6s | %11s %11s | %11s %11s"
      % ("fonlama kovasi", "N", "HAM 4sa", "HAM 24sa", "FON 4sa", "FON 24sa"))
kov = [[x for x in olay if kv(x["ort"]) == q] for q in range(4)]
tab = []
for q in range(4):
    v = kov[q]
    if not v: print("  %-20s %6d | (bos)" % (AD[q], 0)); tab.append([0,0]); continue
    h4, h24 = sx.mean(gk(v, "ham4")), sx.mean(gk(v, "ham24"))
    f4, f24 = sx.mean(gk(v, "fon4")), sx.mean(gk(v, "fon24"))
    tab.append([h4, h24])
    print("  %-20s %6d | %+11.3f %+11.3f | %+11.4f %+11.4f" % (AD[q], len(v), h4, h24, f4, f24))
for j, h in enumerate(UF):
    s = [tab[q][j] for q in range(4)]
    print("     %2dsa monoton azalan mi -> %s" % (h, "EVET" if all(s[i] >= s[i+1] for i in range(3)) else "HAYIR"))

print("\n--- OLCUT 2 (KRITIK): BTC 24sa getirisi SABITLENDIGINDE ---")
bq = sorted(x["btc24"] for x in olay)
BK = (bq[len(bq)//4], bq[len(bq)//2], bq[3*len(bq)//4])
bkv = lambda b: 0 if b < BK[0] else 1 if b < BK[1] else 2 if b < BK[2] else 3
print("  BTC 24sa ceyrekleri: %+.2f · %+.2f · %+.2f" % BK)
for h in UF:
    sat = "  %2dsa" % h; ayni = ge = 0
    for q in range(4):
        v = [x for x in olay if bkv(x["btc24"]) == q]
        f, t_ = welch(gk([x for x in v if kv(x["ort"]) == 3], "ham%d" % h),
                      gk([x for x in v if kv(x["ort"]) == 0], "ham%d" % h))
        if f is None: sat += "  BTC%d: -" % q; continue
        ge += 1
        if f < 0: ayni += 1
        sat += "  BTC%d %+.2f(t%s)" % (q, f, ("%+.1f" % t_) if t_ else "?")
    sat += "  -> %d/%d %s" % (ayni, ge, "GECTI" if ayni >= 3 else "KALDI")
    print(sat)

print("\n--- OLCUT 3: HOLDOUT ---")
olay.sort(key=lambda x: x["t"]); y = len(olay)//2
for ad, v in (("ILK YARI", olay[:y]), ("IKINCI YARI", olay[y:])):
    sat = "  %-12s (%s..%s)" % (ad, v[0]["gun"], v[-1]["gun"])
    for h in UF:
        f, t_ = welch(gk([x for x in v if kv(x["ort"]) == 3], "ham%d" % h),
                      gk([x for x in v if kv(x["ort"]) == 0], "ham%d" % h))
        sat += "   %dsa %+.3f(t%s)" % (h, f or 0, ("%+.1f" % t_) if t_ else "?")
    print(sat)

print("\n--- OLCUT 4: REJIM ---")
for h in UF:
    sat = "  %2dsa" % h; tut = 0
    for rj in ("ATH_BOLGESI", "DUZELTME", "DERIN_AYI"):
        v = [x for x in olay if x["rejim"] == rj]
        f, t_ = welch(gk([x for x in v if kv(x["ort"]) == 3], "ham%d" % h),
                      gk([x for x in v if kv(x["ort"]) == 0], "ham%d" % h))
        if f is not None and f < 0: tut += 1
        sat += "  %s %+.2f(t%s)" % (rj[:4], f or 0, ("%+.1f" % t_) if t_ else "?")
    sat += "  -> %d/3 %s" % (tut, "GECTI" if tut >= 2 else "KALDI")
    print(sat)

print("\n--- YOGUNLASMA ---")
cs = collections.Counter(x["sym"] for x in olay); cg = collections.Counter(x["gun"] for x in olay)
print("  sembol %d · gun %d · en buyuk sembol payi %%%.1f · en buyuk gun payi %%%.1f"
      % (len(cs), len(cg), 100*cs.most_common(1)[0][1]/len(olay), 100*cg.most_common(1)[0][1]/len(olay)))
