# -*- coding: utf-8 -*-
"""KAPI KARNESI — HAM GETIRI DOGRULAMASI (bugunun dersi: tek mekanikle hukum yok).

Q_tum_kapilar mekanikli olcumdu (A-stop + %10 hedef). Bu betik AYNI kapilari
HAM ileri getiriyle (stop YOK, hedef YOK) yeniden olcer. Isaret ayni ise
bulgu mekanikten bagimsizdir; farkliysa mekanik eseridir.

Ayrica G_kapsam dersi: hucreler OYNAKLIKTA ayrisiyor mu — o da raporlanir.
"""
import json, os, sys, collections, random, statistics as stx, bisect, datetime, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ileri_rr as ir

UFUK, MAL = 72, 0.1726
random.seed(41)
OL = []
for fn in sorted(os.listdir(ir.KLINE)):
    if not fn.endswith(".json"): continue
    fp = os.path.join(ir.FUND, fn)
    if not os.path.exists(fp): continue
    try:
        fr = json.load(open(fp, encoding="utf-8"))
        b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
    except Exception: continue
    if not fr or len(b) < ir.ISINMA + UFUK + 50: continue
    ft = [x["t"] for x in fr]
    atrs = ir.atr_serisi(b); ma50 = ir.ma_serisi(b, 50)
    faz = random.randint(0, 23)
    for i in range(ir.ISINMA + faz, len(b) - UFUK - 2, ir.SEYRELT):
        x = b[i]
        if (x.get("qv") or 0) < ir.MIN_VOL/24 or i < 24: continue
        k = bisect.bisect_right(ft, x["t"]) - 1
        if k < 0: continue
        gi = i+1; j = gi + UFUK
        if j >= len(b) or not atrs[i]: continue
        ref = b[gi]["o"]
        if ref <= 0: continue
        ham = (ref - b[j]["c"])/ref*100                       # SHORT, stop YOK
        fon = ir.fonlama_pct(ft, fr, b[gi]["t"], b[j]["t"])
        pen = b[max(0, i-20):i+1]
        lo = min(z["l"] for z in pen); hi = max(z["h"] for z in pen)
        OL.append({"ham": ham, "fon": fon, "net": ham-MAL+fon, "ts": b[gi]["t"],
                   "funding": fr[k]["r"]*100,
                   "chg24": (x["c"]/b[i-24]["c"]-1)*100, "fiyat": x["c"],
                   "ma50m": ((x["c"]/ma50[i]-1)*100 if ma50[i] and ma50[i] > 0 else None),
                   "pos": ((x["c"]-lo)/(hi-lo) if hi > lo else 0.5),
                   "atr": atrs[i]/ref*100})
print("olay: %d" % len(OL))
assert all(math.isfinite(o["net"]) for o in OL)

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

KAPILAR = [
    ("funding <= -0,05", lambda o: o["funding"] <= -0.05),
    ("MA50+ucuz", lambda o: o["fiyat"] <= ir.UCUZ_FIYAT and o["ma50m"] is not None and o["ma50m"] >= ir.MA50_MESAFE),
    ("fiyat <= $0,07", lambda o: o["fiyat"] <= ir.UCUZ_FIYAT),
    ("chg24 >= %20 (pump)", lambda o: o["chg24"] >= ir.PUMP),
    ("chg24 >= %40 (blowoff)", lambda o: o["chg24"] >= 40.0),
    ("pos >= 0,75 (tepe)", lambda o: o["pos"] >= 0.75),
    ("pos < 0,25 (dip)", lambda o: o["pos"] < 0.25),
]
print("\nHAM GETIRI ILE AYNI KAPILAR (stop YOK, hedef YOK)")
print("=" * 110)
print("%-24s %8s %10s %10s %10s %8s %9s %11s"
      % ("kosul", "N gecen", "GECEN", "GECMEYEN", "FARK", "ay-t", "fark ay", "ATR gecen/gecmeyen"))
for ad, fn_ in KAPILAR:
    a = [o for o in OL if fn_(o)]
    b_ = [o for o in OL if not fn_(o)]
    assert len(a)+len(b_) == len(OL)
    if len(a) < 300 or len(b_) < 300:
        print("%-24s %8d  N yetersiz" % (ad, len(a))); continue
    na = stx.mean([o["net"] for o in a]); nb = stx.mean([o["net"] for o in b_])
    aa = collections.defaultdict(list); bb = collections.defaultdict(list)
    for o in a: aa[ay(o["ts"])].append(o["net"])
    for o in b_: bb[ay(o["ts"])].append(o["net"])
    ok = [m for m in set(aa) & set(bb) if len(aa[m]) >= 20 and len(bb[m]) >= 20]
    if len(ok) >= 3:
        fk = [stx.mean(aa[m])-stx.mean(bb[m]) for m in ok]
        se = stx.stdev(fk)/len(fk)**0.5
        t = stx.mean(fk)/se if se else 0
        ay_s = "%d/%d" % (sum(1 for z in fk if z > 0), len(ok))
    else:
        t, ay_s = 0.0, "-"
    print("%-24s %8d %+10.4f %+10.4f %+10.4f %+8.2f %9s   %.2f / %.2f"
          % (ad, len(a), na, nb, na-nb, t, ay_s,
             stx.median([o["atr"] for o in a]), stx.median([o["atr"] for o in b_])))
print("\nMEKANIKLI olcumle (Q_tum_kapilar) KIYAS:")
print("   funding<=-0,05  mekanikli FARK -0,0956 (t=-3,15)")
print("   pump  >=%20     mekanikli FARK -0,5134 (t=-2,14)")
print("   blowoff>=%40    mekanikli FARK -1,3889 (t=-2,41)")
print("   pos<0,25 (dip)  mekanikli FARK +0,1044 (t=+0,89)")
print("\nISARET AYNI ise bulgu mekanikten BAGIMSIZ; farkliysa mekanik eseri.")
