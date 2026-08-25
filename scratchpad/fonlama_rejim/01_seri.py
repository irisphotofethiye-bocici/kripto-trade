# -*- coding: utf-8 -*-
"""PIYASA GENELI FONLAMA SERISI — 8 saatlik kovalarda kesitsel ozet.
Fonlama = pozisyon kompozisyonu; fiyatin kendisi DEGIL.
Birim: YUZDE/8sa (CLAUDE.md kurali geregi assert ile korunur). SALT OKUMA."""
import json, glob, os, sys, collections, statistics as sx, datetime

PROJE = r"c:\Users\alper\Desktop\kripto trade"
FUND = os.path.join(PROJE, "scratchpad", "funding_gecmis")
KL = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
CIK = os.path.join(PROJE, "scratchpad", "fonlama_rejim", "seri.json")
SLOT = 8*3600*1000

# [2026-08-25] fonlama_oku ile okunur — birim dogrulamasi ARACA devredildi.
#   Ham json.load kullanilmaz: 2026-08-12 birim kirilmasi tam bu betikte
#   yakalandi (kritik pencere OLU gorundu). Ayrinti: olcumler.md.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fonlama_oku as FO

kova = collections.defaultdict(list)
n = 0
for f in sorted(glob.glob(os.path.join(FUND, "*.json"))):
    sym = os.path.basename(f)[:-5]
    ft, fr = FO.yukle(sym)          # BirimHatasi firlatirsa betik COKER (istenen)
    if not ft: continue
    n += 1
    for t, r in zip(ft, fr):
        kova[(t//SLOT)*SLOT].append(r)

hep = [r for v in kova.values() for r in v]
med = sx.median([abs(r) for r in hep])
print("sembol %d   kova %s   kayit %s   medyan |r| %.4f%%/8sa"
      % (n, format(len(kova), ","), format(len(hep), ","), med))

# BTC fiyati (karistirici kontrolu icin)
b = json.load(open(os.path.join(KL, "BTC.json"), encoding="utf-8"))
bt = [x["t"] for x in b]; bc = [x["c"] for x in b]
import bisect
def btc_fiyat(t):
    i = bisect.bisect_right(bt, t)-1
    return bc[i] if i >= 0 else None

seri = {}
for t in sorted(kova):
    v = kova[t]
    if len(v) < 40: continue                       # en az 40 sembol
    v2 = sorted(v)
    p = btc_fiyat(t)
    if not p: continue
    seri[str(t)] = {
        "n": len(v),
        "ort": round(sx.mean(v), 5),
        "med": round(v2[len(v2)//2], 5),
        "poz_pay": round(100.0*sum(1 for r in v if r > 0)/len(v), 2),   # kac sembolde LONG oduyor
        "ust10": round(v2[int(len(v2)*0.90)], 5),
        "btc": p,
    }
json.dump(seri, open(CIK, "w"))
ts = sorted(int(k) for k in seri)
g = lambda t: datetime.datetime.utcfromtimestamp(t/1000).strftime("%Y-%m-%d %H:%M")
print("seri: %s kova   %s .. %s" % (format(len(seri), ","), g(ts[0]), g(ts[-1])))

for ad in ("ort", "med", "poz_pay", "ust10"):
    v = sorted(seri[str(t)][ad] for t in ts)
    q = lambda p: v[int(len(v)*p)]
    print("  %-8s %%5 %+8.4f | %%25 %+8.4f | MED %+8.4f | %%75 %+8.4f | %%95 %+8.4f | %%99 %+8.4f"
          % (ad, q(.05), q(.25), q(.50), q(.75), q(.95), q(.99)))

# 8sa DEGISIM dagilimi
d1 = []
for i in range(1, len(ts)):
    if ts[i]-ts[i-1] == SLOT:
        d1.append(seri[str(ts[i])]["ort"] - seri[str(ts[i-1])]["ort"])
d1.sort()
q = lambda p: d1[int(len(d1)*p)]
print("  %-8s %%5 %+8.4f | %%25 %+8.4f | MED %+8.4f | %%75 %+8.4f | %%95 %+8.4f | %%99 %+8.4f"
      % ("D(ort)", q(.05), q(.25), q(.50), q(.75), q(.95), q(.99)))

print("\n=== KRITIK PENCERE (2026-08-17..08-22) ===")
print("%-18s %6s %9s %9s %9s %9s" % ("kova(UTC)", "n", "ort", "medyan", "poz_pay%", "BTC"))
for t in ts:
    s = g(t)
    if "2026-08-17" <= s[:10] <= "2026-08-22":
        z = seri[str(t)]
        print("%-18s %6d %+9.4f %+9.4f %9.2f %9.0f" % (s, z["n"], z["ort"], z["med"], z["poz_pay"], z["btc"]))
