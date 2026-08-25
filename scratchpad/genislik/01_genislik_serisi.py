# -*- coding: utf-8 -*-
"""SAATLIK PIYASA GENISLIGI — kac coinin 24 saatlik getirisi POZITIF.
Ayrica BTC'nin kendi 24sa getirisi (karistirici kontrolu icin). SALT OKUMA."""
import json, glob, os, collections

KL = r"c:\Users\alper\Desktop\kripto trade\scratchpad\klines_1h_uzun"
CIK = r"c:\Users\alper\Desktop\kripto trade\scratchpad\genislik\genislik.json"

yuk = collections.Counter(); top = collections.Counter()
btc = {}
n = 0
for f in sorted(glob.glob(os.path.join(KL, "*.json"))):
    sym = os.path.basename(f)[:-5]
    try: b = json.load(open(f, encoding="utf-8"))
    except Exception: continue
    if len(b) < 60: continue
    n += 1
    c = [x["c"] for x in b]; t = [x["t"] for x in b]
    for i in range(24, len(c)):
        if c[i-24] <= 0 or c[i] <= 0: continue
        top[t[i]] += 1
        if c[i] > c[i-24]: yuk[t[i]] += 1
    if sym == "BTC":
        for i in range(24, len(c)):
            if c[i-24] > 0: btc[t[i]] = (c[i]/c[i-24]-1)*100

seri = {}
for ts, tt in top.items():
    if tt >= 50:                                   # en az 50 sembol olsun
        seri[str(ts)] = [round(100.0*yuk[ts]/tt, 3), tt, round(btc.get(ts, 0.0), 4)]
json.dump(seri, open(CIK, "w"))
print("sembol %d   saat %s" % (n, format(len(seri), ",")))

g = sorted(v[0] for v in seri.values())
q = lambda p: g[int(len(g)*p)]
print("GENISLIK dagilimi: %%5 %.1f | %%25 %.1f | MEDYAN %.1f | %%75 %.1f | %%90 %.1f | %%95 %.1f"
      % (q(.05), q(.25), q(.50), q(.75), q(.90), q(.95)))

# 24 saatlik genislik DEGISIMI
ts_s = sorted(int(k) for k in seri)
idx = {t: i for i, t in enumerate(ts_s)}
d24 = []
for i, t in enumerate(ts_s):
    t0 = t - 24*3600*1000
    if str(t0) in seri:
        d24.append(seri[str(t)][0] - seri[str(t0)][0])
d24.sort()
q2 = lambda p: d24[int(len(d24)*p)]
print("GENISLIK 24sa DEGISIMI: %%5 %+.1f | %%25 %+.1f | MEDYAN %+.1f | %%75 %+.1f | %%90 %+.1f | %%95 %+.1f | %%99 %+.1f"
      % (q2(.05), q2(.25), q2(.50), q2(.75), q2(.90), q2(.95), q2(.99)))
print()
print("kullanicinin isaret ettigi olay:  08-18 %26,5  ->  08-19 %85,9   (gunluk endeks)")
print("saatlik seride bu ~+59 puanlik bir sicrama; yukaridaki %99 dilimle kiyasla.")
