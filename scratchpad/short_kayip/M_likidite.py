# -*- coding: utf-8 -*-
"""KENAR, LIKIT SEMBOLLERDE DE VAR MI?  (surtunme = ne ticaret ettigin)

Bugunku ayristirma: BRUT +0,21 · surtunme 0,32.
Surtunmenin buyuk kismi slipaj ve o LIKIDITEYE bagli (olculdu: r=+0,44).
Bot UCUZ_FIYAT=0.07 ile 7 sentin altindaki coinleri seciyor.

SORU: funding kapisinin kenari LIKIT sembollerde de var mi?
Varsa surtunme dramatik duser ve isaret donebilir.
Yoksa kenar zaten likiditesizlik primi demektir — ve o odenemez.

Semboller HACME gore besе bolunur (medyan qv, son 500 bar).
"""
import json, os, sys, collections, random, statistics as stx, bisect, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ileri_rr as ir

HEDEF, UFUK = 10.0, 72
random.seed(41)

hac = []
for fn in sorted(os.listdir(ir.KLINE)):
    if not fn.endswith(".json"): continue
    try: b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
    except Exception: continue
    if len(b) < ir.ISINMA + UFUK + 50: continue
    hac.append((stx.median([x.get("qv") or 0 for x in b[-500:]]), fn))
hac.sort(reverse=True)
n5 = len(hac)//5
dilim = {}
for i, (q, fn) in enumerate(hac):
    dilim[fn] = min(i//n5, 4)
print("HACIM DILIMLERI (1 = en likit):")
for d in range(5):
    g = [q for q, fn in hac if dilim[fn] == d]
    print("   dilim %d: %3d sembol · medyan gunluk hacim ~ %,.0f $" .replace(",", "") % (d+1, len(g), stx.median(g)*24))

K = collections.defaultdict(lambda: {"ham": [], "fon": [], "ts": [], "fiyat": []})
for fn in sorted(os.listdir(ir.KLINE)):
    if fn not in dilim: continue
    fp = os.path.join(ir.FUND, fn)
    if not os.path.exists(fp): continue
    try:
        fr = json.load(open(fp, encoding="utf-8"))
        b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
    except Exception: continue
    if not fr: continue
    ft = [x["t"] for x in fr]
    atrs = ir.atr_serisi(b)
    faz = random.randint(0, 23)
    for i in range(ir.ISINMA + faz, len(b) - UFUK - 2, ir.SEYRELT):
        x = b[i]
        if (x.get("qv") or 0) < ir.MIN_VOL/24 or i < 24: continue
        if (x["c"]/b[i-24]["c"]-1)*100 >= ir.PUMP: continue
        k = bisect.bisect_right(ft, x["t"]) - 1
        if k < 0 or fr[k]["r"]*100 > ir.FUND_ESIK: continue
        gi = i+1
        if not atrs[i] or gi >= len(b): continue
        ref = b[gi]["o"]
        if ref <= 0: continue
        stop = ir.stop_hesapla(b, i, ref, atrs[i]); sp = (stop-ref)/ref*100
        if sp <= 0 or sp < ir.ASGARI_STOP: continue
        son = min(gi+UFUK, len(b))
        if son-gi < 4: continue
        hed = ref*(1-HEDEF/100)
        cj = hm = None
        for j in range(gi, son):
            if b[j]["h"] >= stop: cj, hm = j, -sp; break
            if b[j]["l"] <= hed: cj, hm = j, HEDEF; break
        if cj is None: cj = son-1; hm = (ref-b[son-1]["c"])/ref*100
        f = ir.fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
        d = K[dilim[fn]]
        d["ham"].append(hm); d["fon"].append(f); d["ts"].append(b[gi]["t"]); d["fiyat"].append(ref)

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

print()
print("FUNDING KAPISININ KENARI, HACIM DILIMINE GORE")
print("=" * 104)
print("%-8s %8s %10s %10s %12s %12s %11s %10s"
      % ("dilim", "N", "BRUT", "fonlama", "NET(ince)", "NET(likit)", "ay-kumeli t", "medyan $"))
for d in range(5):
    v = K.get(d)
    if not v or len(v["ham"]) < 200: continue
    n = len(v["ham"])
    # ince defter maliyeti (olculen): 0,1726 · likit maliyet: taker+dar slipaj
    net_i = [h - 0.1726 + f for h, f in zip(v["ham"], v["fon"])]
    net_l = [h - 0.1100 + f for h, f in zip(v["ham"], v["fon"])]   # 2x(0,045+0,010)
    a = collections.defaultdict(list)
    for z, t in zip(net_l, v["ts"]): a[ay(t)].append(z)
    ok = [m for m in a if len(a[m]) >= 20]
    ms = [stx.mean(a[m]) for m in ok]
    se = stx.stdev(ms)/len(ms)**0.5 if len(ms) > 2 else 0
    print("%-8d %8d %+10.4f %+10.4f %+12.4f %+12.4f %+11.2f %10.4f"
          % (d+1, n, stx.mean(v["ham"]), stx.mean(v["fon"]), stx.mean(net_i),
             stx.mean(net_l), (stx.mean(ms)/se if se else 0), stx.median(v["fiyat"])))
print()
print("NET(ince)  = olculen gercek maliyet 0,1726 (botun bugun ticaret ettigi defterler)")
print("NET(likit) = 2 x (taker %0,045 + slipaj %0,010) = 0,110  (derin defter varsayimi)")
