# -*- coding: utf-8 -*-
"""ADIM 2 — FONLAMA KOSULU KENARI MI TASIYOR, YOKSA MALIYETI MI GETIRIYOR?

A+B kapisi: funding <= -0,05 %/8s  ->  SHORT.
SHORT'ta NEGATIF fonlama = short ODER. Yani kapi, tanimi geregi fonlama
odeyen islemleri seciyor. Kutuk zaten biliyor: "A+B'de kenarin %83'unu
fonlama yedi."

SORU: A kapisi (funding) ile B kapisi (MA50+ucuz) ayri ayri ne yapiyor?
  brut kenar · fonlama yuku · net — uc kume: yalniz A · yalniz B · ikisi

ESIK TARAMASI YOK. Kumeler botun kendi kapilari.
"""
import json, os, sys, collections, random, statistics as stx, bisect, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import olcum_ortak as oo
import ileri_rr as ir

HEDEF, UFUK = 10.0, 72
random.seed(41)
K = collections.defaultdict(lambda: {"ham": [], "fon": [], "fr": [], "ts": []})

for fn in sorted(os.listdir(ir.KLINE)):
    if not fn.endswith(".json"): continue
    try: b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
    except Exception: continue
    if len(b) < ir.ISINMA + UFUK + 50: continue
    fp = os.path.join(ir.FUND, fn); fr = []
    if os.path.exists(fp):
        try: fr = json.load(open(fp, encoding="utf-8"))
        except Exception: fr = []
    ft = [x["t"] for x in fr]
    atrs = ir.atr_serisi(b); ma50 = ir.ma_serisi(b, 50)
    faz = random.randint(0, 23)
    for i in range(ir.ISINMA + faz, len(b) - UFUK - 2, ir.SEYRELT):
        x = b[i]
        if (x.get("qv") or 0) < ir.MIN_VOL/24 or i < 24: continue
        if (x["c"]/b[i-24]["c"]-1)*100 >= ir.PUMP: continue
        oran = None
        A = False
        if ft:
            k = bisect.bisect_right(ft, x["t"]) - 1
            if k >= 0:
                oran = fr[k]["r"]*100
                A = oran <= ir.FUND_ESIK
        B = bool(ma50[i] and ma50[i] > 0 and x["c"] <= ir.UCUZ_FIYAT
                 and (x["c"]/ma50[i]-1)*100 >= ir.MA50_MESAFE)
        if not (A or B): continue
        kume = "A+B" if (A and B) else ("A (funding)" if A else "B (MA50+ucuz)")
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
        d = K[kume]
        d["ham"].append(hm); d["fon"].append(f); d["fr"].append(oran); d["ts"].append(b[gi]["t"])

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

print("ADIM 2 — FONLAMA KOSULU: kenari mi tasiyor, maliyeti mi getiriyor?")
print("=" * 100)
print("%-16s %8s %10s %10s %10s %10s %11s" %
      ("kume", "N", "BRUT", "fonlama", "maliyet", "NET", "ay-kumeli t"))
for ad in ("A (funding)", "A+B", "B (MA50+ucuz)"):
    d = K.get(ad)
    if not d or len(d["ham"]) < 100: continue
    n = len(d["ham"])
    net = [h - oo.MALIYET + f for h, f in zip(d["ham"], d["fon"])]
    a = collections.defaultdict(list)
    for v, t in zip(net, d["ts"]): a[ay(t)].append(v)
    ok = [m for m in a if len(a[m]) >= 20]
    ms = [stx.mean(a[m]) for m in ok]
    se = stx.stdev(ms)/len(ms)**0.5 if len(ms) > 2 else 0
    print("%-16s %8d %+10.4f %+10.4f %+10.4f %+10.4f %+11.2f"
          % (ad, n, stx.mean(d["ham"]), stx.mean(d["fon"]), -oo.MALIYET,
             stx.mean(net), (stx.mean(ms)/se if se else 0)))
print()
print("GERCEK MALIYETLE (olculen slipaj %0,0499 -> toplam %0,1726):")
print("%-16s %8s %10s %11s" % ("kume", "N", "NET", "ay-kumeli t"))
for ad in ("A (funding)", "A+B", "B (MA50+ucuz)"):
    d = K.get(ad)
    if not d or len(d["ham"]) < 100: continue
    net = [h - 0.1726 + f for h, f in zip(d["ham"], d["fon"])]
    a = collections.defaultdict(list)
    for v, t in zip(net, d["ts"]): a[ay(t)].append(v)
    ok = [m for m in a if len(a[m]) >= 20]
    ms = [stx.mean(a[m]) for m in ok]
    se = stx.stdev(ms)/len(ms)**0.5 if len(ms) > 2 else 0
    print("%-16s %8d %+10.4f %+11.2f" % (ad, len(net), stx.mean(net), (stx.mean(ms)/se if se else 0)))
print()
print("FONLAMA ORANI ile kenar iliskisi (A kapisini gecen kume, dilimler):")
d = K.get("A (funding)")
if d:
    z = sorted([(o, h, f) for o, h, f in zip(d["fr"], d["ham"], d["fon"]) if o is not None])
    n = len(z)//4
    print("%-22s %7s %10s %10s %10s" % ("funding dilimi", "N", "BRUT", "fonlama", "NET"))
    for i in range(4):
        g = z[i*n:(i+1)*n] if i < 3 else z[3*n:]
        print("%-22s %7d %+10.4f %+10.4f %+10.4f"
              % ("%.4f .. %.4f" % (g[0][0], g[-1][0]), len(g),
                 stx.mean([x[1] for x in g]), stx.mean([x[2] for x in g]),
                 stx.mean([x[1]-0.1726+x[2] for x in g])))
