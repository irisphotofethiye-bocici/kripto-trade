# -*- coding: utf-8 -*-
"""IS 1 / KONTROL — uzun ufuktaki artı GERCEK mi, yoksa (a) aykiri suruklemesi
(b) genel alt-coin cokusu mu?

N_ufuk bulgusu: 1 ayda havuz NET +1,8451 AMA ay-kumeli t = -0,35, poz ay 13/24.
Iki rakip aciklama:
  (a) AYKIRI: birkac coin %80 coktu, ortalamayi tasiyor -> medyan negatif olur
  (b) YAPISAL: alt coinler genel olarak dusuyor, kapinin katkisi YOK
      -> KONTROL (kapisiz rastgele giris) ayni sonucu verir

Ikisi de olculur.
"""
import json, os, sys, collections, random, statistics as stx, bisect, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ileri_rr as ir

UFUKLAR = [(72, "72s"), (336, "2 hafta"), (720, "1 ay")]
MAL = 0.1726
random.seed(41)
K = collections.defaultdict(lambda: {"ham": [], "fon": [], "ts": []})

for fn in sorted(os.listdir(ir.KLINE)):
    if not fn.endswith(".json"): continue
    fp = os.path.join(ir.FUND, fn)
    if not os.path.exists(fp): continue
    try:
        fr = json.load(open(fp, encoding="utf-8"))
        b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
    except Exception: continue
    if not fr or len(b) < ir.ISINMA + 760: continue
    ft = [x["t"] for x in fr]
    faz = random.randint(0, 23)
    for i in range(ir.ISINMA + faz, len(b) - 740, ir.SEYRELT):
        x = b[i]
        if (x.get("qv") or 0) < ir.MIN_VOL/24 or i < 24: continue
        if (x["c"]/b[i-24]["c"]-1)*100 >= ir.PUMP: continue
        k = bisect.bisect_right(ft, x["t"]) - 1
        gecti = (k >= 0 and fr[k]["r"]*100 <= ir.FUND_ESIK)
        gi = i+1
        ref = b[gi]["o"]
        if ref <= 0: continue
        for h, ad in UFUKLAR:
            j = gi + h
            if j >= len(b): continue
            ham = (ref - b[j]["c"])/ref*100
            fon = ir.fonlama_pct(ft, fr, b[gi]["t"], b[j]["t"])
            kume = "KAPI" if gecti else "KONTROL"
            d = K[(ad, kume)]
            d["ham"].append(ham); d["fon"].append(fon); d["ts"].append(b[gi]["t"])

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

print("KONTROL 1 — DAGILIM: ortalama mi medyan mi?")
print("=" * 100)
print("%-10s %-8s %8s %10s %10s %10s %10s %9s"
      % ("ufuk", "kume", "N", "ort HAM", "MEDYAN", "ort NET", "MED NET", "kazanan%"))
for h, ad in UFUKLAR:
    for kume in ("KAPI", "KONTROL"):
        d = K.get((ad, kume))
        if not d or len(d["ham"]) < 200: continue
        net = [a - MAL + f for a, f in zip(d["ham"], d["fon"])]
        kz = 100*sum(1 for z in net if z > 0)/len(net)
        print("%-10s %-8s %8d %+10.4f %+10.4f %+10.4f %+10.4f %8.1f%%"
              % (ad, kume, len(d["ham"]), stx.mean(d["ham"]), stx.median(d["ham"]),
                 stx.mean(net), stx.median(net), kz))
    print()

print("KONTROL 2 — KAPI eksi KONTROL (kapinin KATKISI)")
print("=" * 100)
print("%-10s %12s %12s %12s %12s" % ("ufuk", "KAPI net", "KONTROL net", "FARK", "medyan fark"))
for h, ad in UFUKLAR:
    a = K.get((ad, "KAPI")); b_ = K.get((ad, "KONTROL"))
    if not a or not b_ or len(a["ham"]) < 200 or len(b_["ham"]) < 200: continue
    na = [z - MAL + f for z, f in zip(a["ham"], a["fon"])]
    nb = [z - MAL + f for z, f in zip(b_["ham"], b_["fon"])]
    print("%-10s %+12.4f %+12.4f %+12.4f %+12.4f"
          % (ad, stx.mean(na), stx.mean(nb), stx.mean(na)-stx.mean(nb),
             stx.median(na)-stx.median(nb)))

print()
print("KONTROL 3 — AYKIRI SURUKLEMESI (1 ay, KAPI kumesi)")
d = K.get(("1 ay", "KAPI"))
if d:
    net = sorted([z - MAL + f for z, f in zip(d["ham"], d["fon"])], reverse=True)
    n = len(net)
    print("   N=%d  ortalama %+.4f  medyan %+.4f" % (n, stx.mean(net), stx.median(net)))
    for pay in (1, 5, 10):
        k = max(1, n*pay//100)
        print("   en iyi %%%-3d (%5d islem) cikarilinca ortalama: %+.4f"
              % (pay, k, stx.mean(net[k:])))
    print("   en iyi 5 islem: %s" % ["%+.0f" % z for z in net[:5]])
