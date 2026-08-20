# -*- coding: utf-8 -*-
"""IZ G — MEKANIK BIASI ESITSIZ MI? (kusurun kapsamini olcer)

Savunma sudur: "mekanik her hucrede AYNI, o yuzden siralamayi bozmaz."
Bu savunma yalnizca bias HER HUCREDE AYNI ise gecerli.
Bu betik onu olcer: bant bant stop-olma orani ve stop genisligi.
Farklilarsa savunma COKER ve tum bant-kiyaslarina supheyle bakilir.
"""
import json, os, sys, collections, random, statistics as stx
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ileri_rr as ir
import btcpay_rejim as bp

UFUK = 72
BANTLAR = [(-40, 0, "-40..0"), (0, 20, "0..20"), (20, 40, "20..40"), (40, 1e9, ">40")]
random.seed(41)
h = collections.defaultdict(lambda: {"n": 0, "stop": 0, "hedef": 0, "sure": 0, "sp": [], "atr": []})

for fn in sorted(os.listdir(ir.KLINE)):
    if not fn.endswith(".json"): continue
    try: b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
    except Exception: continue
    if len(b) < ir.ISINMA + UFUK + 50: continue
    atrs = ir.atr_serisi(b)
    faz = random.randint(0, 23)
    for i in range(ir.ISINMA + faz, len(b) - UFUK - 2, ir.SEYRELT):
        x = b[i]
        if (x.get("qv") or 0) < ir.MIN_VOL/24 or i < 24 or b[i-24]["c"] <= 0: continue
        c24 = (x["c"]/b[i-24]["c"]-1)*100
        ad = next((a for lo, hi, a in BANTLAR if lo <= c24 < hi), None)
        if ad is None: continue
        gi = i+1
        if not atrs[i] or gi >= len(b): continue
        ref = b[gi]["o"]
        if ref <= 0: continue
        son = min(gi+UFUK, len(b))
        if son-gi < 4: continue
        for yon in ("LONG", "SHORT"):
            if yon == "SHORT":
                stop = ir.stop_hesapla(b, i, ref, atrs[i]); sp = (stop-ref)/ref*100; hed = ref*0.90
            else:
                stop = bp.stop_long(b, i, ref, atrs[i]); sp = (ref-stop)/ref*100; hed = ref*1.10
            if sp <= 0 or sp < 2.0: continue
            d = h[(ad, yon)]
            d["n"] += 1; d["sp"].append(sp); d["atr"].append(atrs[i]/ref*100)
            tip = "sure"
            for j in range(gi, son):
                vs = (b[j]["h"] >= stop) if yon == "SHORT" else (b[j]["l"] <= stop)
                vh = (b[j]["l"] <= hed) if yon == "SHORT" else (b[j]["h"] >= hed)
                if vs: tip = "stop"; break
                if vh: tip = "hedef"; break
            d[tip] += 1

print("MEKANIK BIASI BANT BANT ESIT MI?")
print("=" * 96)
print("%-9s %-6s %8s %9s %9s %9s %11s %10s" %
      ("bant", "yon", "N", "stop%", "hedef%", "sure%", "stop genis", "ATR/fiyat"))
for lo, hi, ad in BANTLAR:
    for yon in ("LONG", "SHORT"):
        d = h.get((ad, yon))
        if not d or d["n"] < 100: continue
        n = d["n"]
        print("%-9s %-6s %8d %8.1f%% %8.1f%% %8.1f%% %10.2f%% %9.2f%%"
              % (ad, yon, n, 100*d["stop"]/n, 100*d["hedef"]/n, 100*d["sure"]/n,
                 stx.median(d["sp"]), stx.median(d["atr"])))
    print()
print("YORUM: stop-olma orani ve stop genisligi bantlar arasi FARKLIYSA,")
print("       'mekanik her hucrede ayni' savunmasi gecersizdir.")
