# -*- coding: utf-8 -*-
"""ADIM 3 (DUZELTILMIS) — FONLAMA ZAMANLAMASI, PERIYOT KARISTIRICISI GIDERILMIS.

ILK DENEME HATALIYDI: "fonlamaya kalan saat" degiskeni buyuk olcude SEMBOLUN
PERIYODUNU olcuyordu. Olculdu: 418 sembol 4 SAATLIK, 147 sembol 8 SAATLIK
fonlama kullaniyor. 4 saatlikler yalniz kalan 0-3'e dusuyor -> kovalar karisik.

DUZELTME: semboller periyoda gore AYRILIR, ve zamanlama ORANSAL olculur
(dongude kalan pay: 0..1). Boylece 4s ve 8s semboller ayni olcekte.
"""
import json, os, sys, collections, random, statistics as stx, bisect, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ileri_rr as ir

HEDEF, UFUK = 10.0, 72
MAL = 0.1726
random.seed(41)
K = collections.defaultdict(lambda: {"ham": [], "fon": [], "ts": [], "kes": []})

for fn in sorted(os.listdir(ir.KLINE)):
    if not fn.endswith(".json"): continue
    fp = os.path.join(ir.FUND, fn)
    if not os.path.exists(fp): continue
    try:
        fr = json.load(open(fp, encoding="utf-8"))
        b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
    except Exception: continue
    if len(fr) < 20 or len(b) < ir.ISINMA + UFUK + 50: continue
    ts = [x["t"] for x in fr]
    dd = [(y-x)/3600000 for x, y in zip(ts[-40:], ts[-39:])]
    per = round(stx.median(dd))
    if per not in (4, 8): continue
    atrs = ir.atr_serisi(b)
    i = ir.ISINMA
    while i < len(b) - UFUK - 2:
        i += 24
        j0 = i + random.randint(-11, 12)
        if j0 < ir.ISINMA or j0 >= len(b) - UFUK - 2: continue
        x = b[j0]
        if (x.get("qv") or 0) < ir.MIN_VOL/24 or j0 < 24: continue
        if (x["c"]/b[j0-24]["c"]-1)*100 >= ir.PUMP: continue
        k = bisect.bisect_right(ts, x["t"]) - 1
        if k < 0 or fr[k]["r"]*100 > ir.FUND_ESIK: continue
        gi = j0+1
        if not atrs[j0] or gi >= len(b): continue
        ref = b[gi]["o"]
        if ref <= 0: continue
        stop = ir.stop_hesapla(b, j0, ref, atrs[j0]); sp = (stop-ref)/ref*100
        if sp <= 0 or sp < ir.ASGARI_STOP: continue
        son = min(gi+UFUK, len(b))
        if son-gi < 4: continue
        nx = bisect.bisect_right(ts, b[gi]["t"])
        if nx >= len(ts): continue
        kalan_sa = (ts[nx]-b[gi]["t"])/3600000.0
        pay = min(max(kalan_sa/per, 0.0), 1.0)          # dongude KALAN PAY 0..1
        hed = ref*(1-HEDEF/100)
        cj = hm = None
        for j in range(gi, son):
            if b[j]["h"] >= stop: cj, hm = j, -sp; break
            if b[j]["l"] <= hed: cj, hm = j, HEDEF; break
        if cj is None: cj = son-1; hm = (ref-b[son-1]["c"])/ref*100
        f = ir.fonlama_pct(ts, fr, b[gi]["t"], b[cj]["t"])
        kes = bisect.bisect_right(ts, b[cj]["t"]) - nx + 1
        çey = min(int(pay*4), 3)
        d = K[(per, çey)]
        d["ham"].append(hm); d["fon"].append(f); d["ts"].append(b[gi]["t"]); d["kes"].append(kes)

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

print("ADIM 3 DUZELTILMIS — periyot ayrilmis, zamanlama ORANSAL")
print("=" * 100)
for per in (4, 8):
    top = sum(len(K[(per, c)]["ham"]) for c in range(4))
    if top < 500: continue
    print("\n### %d SAATLIK fonlama sembolleri  (N=%d)" % (per, top))
    print("%-16s %8s %7s %10s %10s %10s %11s %9s"
          % ("dongude kalan", "N", "pay%", "BRUT", "fonlama", "NET", "ay-kumeli t", "kesinti"))
    for c in range(4):
        d = K[(per, c)]
        n = len(d["ham"])
        if n < 200:
            print("%-16s %8d  N yetersiz" % ("%d. ceyrek" % (c+1), n)); continue
        net = [h - MAL + f for h, f in zip(d["ham"], d["fon"])]
        a = collections.defaultdict(list)
        for v, t in zip(net, d["ts"]): a[ay(t)].append(v)
        ok = [m for m in a if len(a[m]) >= 20]
        ms = [stx.mean(a[m]) for m in ok]
        se = stx.stdev(ms)/len(ms)**0.5 if len(ms) > 2 else 0
        print("%-16s %8d %6.1f%% %+10.4f %+10.4f %+10.4f %+11.2f %9.2f"
              % ("%d. ceyrek" % (c+1), n, 100*n/top, stx.mean(d["ham"]), stx.mean(d["fon"]),
                 stx.mean(net), (stx.mean(ms)/se if se else 0), stx.mean(d["kes"])))
    print("   (1. ceyrek = kesintiye EN YAKIN · 4. ceyrek = EN UZAK)")
