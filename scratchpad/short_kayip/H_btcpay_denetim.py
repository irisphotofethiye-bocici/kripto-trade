# -*- coding: utf-8 -*-
"""IZ H — DUN GECEKI btc_pay HUKUMLERI de mekanik yuklu mu?

Dun gece verilen hukumler (olcumler.md):
  SHORT freni AYI/NOTR'da GERCEK · BOGA'da gurultu · LONG bacagi hicbir yerde yok
Hepsi A-stop + %10 hedef ile olculdu. Bugun ogrenilen kusur: hucreler
OYNAKLIKTA ayrisiyorsa mekanik siralamayi bozar.

BU BETIK: btc_pay hucrelerinde (UST vs diger) x (AYI/NOTR/BOGA)
  - stop genisligi
  - stop-olma orani
  - ATR/fiyat
esit mi? Ayrica AYNI hucreler HAM getiriyle yeniden olculur.
"""
import json, os, sys, collections, random, statistics as stx, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import olcum_ortak as oo
import ileri_rr as ir
import btcpay_rejim as bp

UST_ESIK = 2.8755
HEDEF, UFUK = 10.0, 72
random.seed(41)

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

vx, _ = bp.gostergeler()
rej = ir.btc_rejim()
h = collections.defaultdict(lambda: {"n": 0, "stop": 0, "sp": [], "atr": [],
                                     "ham": [], "mek": []})
for fn in sorted(os.listdir(ir.KLINE)):
    if not fn.endswith(".json"): continue
    sym = fn[:-5]
    try: b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
    except Exception: continue
    if len(b) < ir.ISINMA + UFUK + 50: continue
    fp = os.path.join(ir.FUND, fn); fr = []
    if os.path.exists(fp):
        try: fr = json.load(open(fp, encoding="utf-8"))
        except Exception: fr = []
    ft = [x["t"] for x in fr]
    atrs = ir.atr_serisi(b)
    faz = random.randint(0, 23)
    for i in range(ir.ISINMA + faz, len(b) - UFUK - 2, ir.SEYRELT):
        x = b[i]
        if (x.get("qv") or 0) < ir.MIN_VOL/24 or i < 24: continue
        sa = x["t"]//3600000
        if sa not in vx: continue
        gi = i+1
        if not atrs[i] or gi >= len(b): continue
        ref = b[gi]["o"]
        if ref <= 0: continue
        son = min(gi+UFUK, len(b))
        if son-gi < 4: continue
        stop = ir.stop_hesapla(b, i, ref, atrs[i])
        sp = (stop-ref)/ref*100
        if sp <= 0 or sp < 2.0: continue
        r = rej.get(sa, "NOTR")
        bant = "UST" if vx[sa] >= UST_ESIK else "diger"
        k = (r, bant)
        d = h[k]
        d["n"] += 1; d["sp"].append(sp); d["atr"].append(atrs[i]/ref*100)
        hedef = ref*(1-HEDEF/100)
        cj = hm = None
        for j in range(gi, son):
            if b[j]["h"] >= stop: cj, hm = j, -sp; d["stop"] += 1; break
            if b[j]["l"] <= hedef: cj, hm = j, HEDEF; break
        if cj is None:
            cj = son-1; hm = (ref-b[son-1]["c"])/ref*100
        f = ir.fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
        d["mek"].append((hm-oo.MALIYET+f, b[gi]["t"]))
        d["ham"].append(((ref-b[son-1]["c"])/ref*100, b[gi]["t"]))   # SHORT ham getiri

def kumeli(v):
    a = collections.defaultdict(list)
    for net, t in v: a[ay(t)].append(net)
    ok = [k for k in a if len(a[k]) >= 20]
    if len(ok) < 3: return None
    m = [stx.mean(a[k]) for k in ok]
    se = stx.stdev(m)/len(m)**0.5
    return stx.mean(m), (stx.mean(m)/se if se else 0), len(ok), sum(1 for x in m if x > 0)

print("IZ H — btc_pay HUCRELERI OYNAKLIKTA AYRISIYOR MU? (SHORT bacagi)")
print("=" * 96)
print("SORU 1 — mekanik esit mi?")
print("%-6s %-7s %8s %11s %10s %10s" % ("rejim", "bant", "N", "stop genis", "ATR/fiyat", "stop olma"))
for r in ("AYI", "NOTR", "BOGA"):
    for bant in ("UST", "diger"):
        d = h.get((r, bant))
        if not d or d["n"] < 100: continue
        print("%-6s %-7s %8d %10.2f%% %9.2f%% %9.1f%%"
              % (r, bant, d["n"], stx.median(d["sp"]), stx.median(d["atr"]), 100*d["stop"]/d["n"]))
    print()

print("SORU 2 — HAM getiriyle ayni hukum cikiyor mu?")
print("%-6s %-7s %8s %11s %9s %11s %9s" % ("rejim", "bant", "N", "HAM ay ort", "ham t", "MEK ay ort", "mek t"))
lift = {}
for r in ("AYI", "NOTR", "BOGA"):
    satir = {}
    for bant in ("UST", "diger"):
        d = h.get((r, bant))
        if not d or d["n"] < 100: continue
        kh, km = kumeli(d["ham"]), kumeli(d["mek"])
        if not kh or not km: continue
        satir[bant] = (kh[0], km[0])
        print("%-6s %-7s %8d %+10.3f %+9.2f %+10.3f %+9.2f"
              % (r, bant, d["n"], kh[0], kh[1], km[0], km[1]))
    if len(satir) == 2:
        lift[r] = (satir["UST"][0]-satir["diger"][0], satir["UST"][1]-satir["diger"][1])
    print()
print("LIFT (UST - diger) — frenin iddiasi NEGATIF olmasi:")
print("%-6s %14s %14s %s" % ("rejim", "HAM lift", "MEKANIK lift", "ayni yon mu"))
for r, (lh, lm) in lift.items():
    print("%-6s %+14.3f %+14.3f %s" % (r, lh, lm, "EVET" if (lh < 0) == (lm < 0) else "HAYIR — HUKUM SUPHELI"))
