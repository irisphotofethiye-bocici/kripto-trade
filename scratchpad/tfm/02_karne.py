# -*- coding: utf-8 -*-
"""TimesFM kapsama testi — KARNE. On-kayit: ON_KAYIT_kapsama.md
Kuantil indeksleri (timesfm_2p5_base.py:92 ile dogrulandi):
   index 0 = ortalama · 1..9 = P10..P90 · index 5 = medyan
SALT OKUMA."""
import json, os, math, collections, statistics as sx

HAM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ham_sonuc.json")
d = json.load(open(HAM))
d.sort(key=lambda x: x["t"])
UFUK = (4, 24)
P10, P90, P20, P80, P50 = 1, 9, 2, 8, 5

def kapsama(v, h, a, b):
    return [1.0 if v[i]["q%d" % h][a] <= v[i]["ger%d" % h] <= v[i]["q%d" % h][b] else 0.0
            for i in range(len(v))]

def gun_kumeli(v, bayrak):
    g = collections.defaultdict(list)
    for x, f in zip(v, bayrak):
        g[x["gun"]].append(f)
    gunler = [sx.mean(z) for z in g.values()]
    m = sx.mean(gunler)
    se = sx.stdev(gunler)/math.sqrt(len(gunler)) if len(gunler) > 2 else 0.0
    return m, se, len(gunler)

def atr_kapsama(v, h, k):
    n = 0
    for x in v:
        yari = k*x["atr"]*math.sqrt(h)
        if x["son"]-yari <= x["ger%d" % h] <= x["son"]+yari: n += 1
    return n/len(v)

def k_kalibre(v, h, hedef):
    lo, hi = 0.01, 30.0
    for _ in range(60):
        mid = (lo+hi)/2
        if atr_kapsama(v, h, mid) < hedef: lo = mid
        else: hi = mid
    return (lo+hi)/2

def tfm_kalibre(v, h, hedef):
    """TimesFM bandini merkezden olcekle -> hedef kapsama."""
    lo, hi = 0.05, 10.0
    def kap(s):
        n = 0
        for x in v:
            q = x["q%d" % h]; c = q[P50]
            if c+(q[P10]-c)*s <= x["ger%d" % h] <= c+(q[P90]-c)*s: n += 1
        return n/len(v)
    for _ in range(60):
        mid = (lo+hi)/2
        if kap(mid) < hedef: lo = mid
        else: hi = mid
    return (lo+hi)/2

print("=" * 100)
print("TimesFM KUANTIL KAPSAMA KARNESI   N=%s nokta   %s .. %s"
      % (format(len(d), ","), d[0]["gun"], d[-1]["gun"]))
print("on-kayit: scratchpad/tfm/ON_KAYIT_kapsama.md   (sonuc gorulmeden yazildi)")
print("=" * 100)

print("\n--- OLCUT 1: DURUSTLUK — P10-P90 gercekten %80 mi?  (gecme: %75-%85) ---")
for h in UFUK:
    f = kapsama(d, h, P10, P90)
    m, se, ng = gun_kumeli(d, f)
    huk = "GECTI" if 0.75 <= m <= 0.85 else "KALDI"
    print("  %2dsa  kapsama %%%.1f  +-%%%.1f  (gun N=%d)   ham %%%.1f   -> %s"
          % (h, 100*m, 100*1.96*se, ng, 100*sx.mean(f), huk))

print("\n--- OLCUT 4': UC DAVRANISI — P20-P80 nominal %60  (gecme: %55-%65) ---")
for h in UFUK:
    f = kapsama(d, h, P20, P80)
    m, se, ng = gun_kumeli(d, f)
    huk = "GECTI" if 0.55 <= m <= 0.65 else "KALDI"
    print("  %2dsa  kapsama %%%.1f  +-%%%.1f   -> %s" % (h, 100*m, 100*1.96*se, huk))

print("\n--- OLCUT 2: ISE YARARLIK — ATR ile yan yana (zaman bolmeli) ---")
yari = len(d)//2
kal, test = d[:yari], d[yari:]
print("  kalibrasyon: %s..%s (N=%d)   TEST: %s..%s (N=%d)"
      % (kal[0]["gun"], kal[-1]["gun"], len(kal), test[0]["gun"], test[-1]["gun"], len(test)))
for h in UFUK:
    hedef = sx.mean(kapsama(kal, h, P10, P90))     # TimesFM'in kendi kalibrasyon-yarisi kapsamasi
    k = k_kalibre(kal, h, hedef)
    s = tfm_kalibre(kal, h, hedef)
    t_kap = sx.mean(kapsama(test, h, P10, P90))
    a_kap = atr_kapsama(test, h, k)
    t_gen = sx.median([(x["q%d" % h][P90]-x["q%d" % h][P10])/x["son"]*100 for x in test])
    a_gen = sx.median([2*k*x["atr"]*math.sqrt(h)/x["son"]*100 for x in test])
    ts_gen = t_gen*s
    print("  %2dsa  hedef %%%.1f | k=%.3f  olcek=%.3f" % (h, 100*hedef, k, s))
    print("        TEST kapsama:  TimesFM %%%.1f   ATR %%%.1f" % (100*t_kap, 100*a_kap))
    print("        TEST genislik: TimesFM %%%.2f   ATR %%%.2f   -> %s"
          % (ts_gen, a_gen, "TimesFM DAR (%.0f%% daha)" % (100*(1-ts_gen/a_gen))
             if ts_gen < a_gen else "ATR DAR (%.0f%% daha)" % (100*(1-a_gen/ts_gen))))

print("\n--- OLCUT 3: REJIM KARARLILIGI  (gecme: %70-%90, ucunde de) ---")
for rj in ("ATH_BOLGESI", "DUZELTME", "DERIN_AYI"):
    v = [x for x in d if x["rejim"] == rj]
    if len(v) < 50:
        print("  %-14s N=%-5d (yetersiz)" % (rj, len(v))); continue
    sat = "  %-14s N=%-5d" % (rj, len(v))
    for h in UFUK:
        m, se, ng = gun_kumeli(v, kapsama(v, h, P10, P90))
        sat += "   %2dsa %%%.1f(+-%.1f)" % (h, 100*m, 100*1.96*se)
    print(sat)

print("\n--- YOGUNLASMA DENETIMI ---")
cs = collections.Counter(x["sym"] for x in d); cg = collections.Counter(x["gun"] for x in d)
print("  farkli sembol %d · farkli gun %d · en buyuk sembol payi %%%.1f · en buyuk gun payi %%%.1f"
      % (len(cs), len(cg), 100*cs.most_common(1)[0][1]/len(d), 100*cg.most_common(1)[0][1]/len(d)))

print("\n--- IKINCIL (tavan olcumu): YON ISABETI — beklenti: rastgele ---")
for h in UFUK:
    f = [1.0 if (x["p%d" % h] > x["son"]) == (x["ger%d" % h] > x["son"]) else 0.0 for x in d]
    m, se, ng = gun_kumeli(d, f)
    yuk = sum(1 for x in d if x["p%d" % h] > x["son"])/len(d)
    print("  %2dsa  isabet %%%.1f  +-%%%.1f   (model YUKARI dedigi oran %%%.1f)"
          % (h, 100*m, 100*1.96*se, 100*yuk))
