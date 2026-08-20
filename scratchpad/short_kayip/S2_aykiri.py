# -*- coding: utf-8 -*-
"""SON YIGININ AYKIRI KONTROLU — bugun uc bulguyu bu kontrol oldurdu."""
import json, os, sys, collections, random, statistics as stx, bisect, datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ileri_rr as ir
import btcpay_rejim as bp

vx, _ = bp.gostergeler()
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
    if not fr or len(b) < ir.ISINMA + 122: continue
    ft = [x["t"] for x in fr]; atrs = ir.atr_serisi(b); faz = random.randint(0, 23)
    for i in range(ir.ISINMA + faz, len(b) - 74, ir.SEYRELT):
        x = b[i]
        if (x.get("qv") or 0) < ir.MIN_VOL/24 or i < 24: continue
        sa = x["t"]//3600000
        if sa not in vx: continue
        k = bisect.bisect_right(ft, x["t"]) - 1
        if k < 0: continue
        c24 = (x["c"]/b[i-24]["c"]-1)*100; o = fr[k]["r"]*100
        if not (c24 < ir.PUMP and x["c"] > ir.UCUZ_FIYAT and o > -0.05 and vx[sa] < 2.8755): continue
        gi = i+1
        if not atrs[i] or gi >= len(b): continue
        ref = b[gi]["o"]
        if ref <= 0: continue
        stop0 = ir.stop_hesapla(b, i, ref, atrs[i]); sp = (stop0-ref)/ref*100
        if sp <= 0 or sp < ir.ASGARI_STOP: continue
        son = min(gi+72, len(b))
        if son-gi < 4: continue
        hed = ref*0.90; cj = hm = None
        for j in range(gi, son):
            st = ref + (stop0-ref)*(2.0 if (j-gi) < 6 else 1.0)
            if b[j]["h"] >= st: cj, hm = j, -(st-ref)/ref*100; break
            if b[j]["l"] <= hed: cj, hm = j, 10.0; break
        if cj is None: cj = son-1; hm = (ref-b[son-1]["c"])/ref*100
        f = ir.fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
        OL.append((hm-0.1726+f, b[gi]["t"], fn[:-5]))

v = sorted([z[0] for z in OL], reverse=True); n = len(v)
print("SON YIGIN (erken-stop) — AYKIRI KONTROLU")
print("  N=%d  ortalama %+.4f  MEDYAN %+.4f" % (n, stx.mean(v), stx.median(v)))
for pay in (1, 5, 10):
    k = max(1, n*pay//100)
    print("  en iyi %%%-3d cikarilinca: %+.4f" % (pay, stx.mean(v[k:])))
print("  en iyi 5: %s" % ["%+.1f" % z for z in v[:5]])
print("  kazanan islem: %%%.1f" % (100*sum(1 for z in v if z > 0)/n))
sem = collections.Counter(z[2] for z in OL)
print("  ayrik sembol: %d · en cok katkili sembolun payi %%%.1f"
      % (len(sem), 100*sem.most_common(1)[0][1]/n))

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")
a = collections.defaultdict(list)
for z, t, s in OL: a[ay(t)].append(z)
ok = sorted([m for m in a if len(a[m]) >= 20])
ms = [stx.mean(a[m]) for m in ok]
print("\n  AY AY:")
print("   " + "  ".join("%s %+.2f" % (m[2:], stx.mean(a[m])) for m in ok))
print("  pozitif ay %d/%d · ortalama %+.4f · EN IYI AY atilinca %+.4f"
      % (sum(1 for z in ms if z > 0), len(ms), stx.mean(ms), stx.mean(sorted(ms)[:-1])))
