# -*- coding: utf-8 -*-
"""ESIK KALIBRASYONU — uydurma esik kullanmamak icin dagilimlara bak.
SALT OKUMA."""
import json, glob, os, random, statistics as sx

KL = r"c:\Users\alper\Desktop\kripto trade\scratchpad\klines_1h_uzun"
fs = sorted(glob.glob(os.path.join(KL, "*.json")))
random.seed(11)
orn = random.sample(fs, 80)

get168 = []   # 7 gunluk getiri (%)
std168 = []   # onceki 168 saatin saatlik getiri std'si (%)
saatlik = []  # tek saatlik getiri (%)

for f in orn:
    try:
        b = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    if len(b) < 400:
        continue
    c = [x["c"] for x in b]
    r = [0.0] + [(c[i] / c[i-1] - 1) * 100 if c[i-1] else 0.0 for i in range(1, len(c))]
    saatlik.extend(r[1::7])                      # seyreltilmis ornek
    for i in range(169, len(c), 13):             # seyreltilmis tarama
        if c[i-169] <= 0:
            continue
        get168.append((c[i-1] / c[i-169] - 1) * 100)
        pen = r[i-168:i]
        try:
            std168.append(sx.pstdev(pen))
        except Exception:
            pass

def dil(ad, v, birim="%"):
    v = sorted(v)
    n = len(v)
    q = lambda p: v[int(n * p)]
    print("%-22s N=%-8d  %%5 %7.2f | %%25 %7.2f | MEDYAN %7.2f | %%75 %7.2f | %%95 %7.2f"
          % (ad, n, q(.05), q(.25), q(.50), q(.75), q(.95)))

print("=== DAGILIMLAR (80 sembol ornegi) ===")
dil("7 gunluk getiri", get168)
dil("|7 gunluk getiri|", [abs(x) for x in get168])
dil("168sa saatlik std", std168)
dil("tek saatlik getiri", saatlik)
dil("|tek saatlik getiri|", [abs(x) for x in saatlik])

for e in (3, 4, 5, 7, 10):
    n = sum(1 for x in saatlik if x >= e)
    print("  tek saatte >= +%%%-2d : %%%.3f of saatler" % (e, 100.0 * n / len(saatlik)))
