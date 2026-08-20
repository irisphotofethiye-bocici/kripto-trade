# -*- coding: utf-8 -*-
"""BOTUN CEKIRDEK KAPISI: funding <= -0,05 · KAPIYI GECMEYENLERLE kiyas.

N2 bulgusu (HAM getiri, stopsuz): kapi, tamamlayicisindan KOTU (-0,59 .. -0,75).
AMA CLAUDE.md ogretiyor: mekanik onemli. Bu betik AYNI MEKANIKLE kiyaslar:
A-stop · %10 hedef · 72s ufuk · maliyet + fonlama.

Bu, botun en temel kapisinin ilk DOGRUDAN kontrol-gruplu sinavidir.
Orijinal olcum: radar arsivinde N=201, +0,396R. Bu: 2 yil, N~180.000.
"""
import json, os, sys, collections, random, statistics as stx, bisect, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ileri_rr as ir

HEDEF, UFUK, MAL = 10.0, 72, 0.1726
random.seed(41)
K = collections.defaultdict(lambda: {"net": [], "ham": [], "fon": [], "ts": [], "oran": []})

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
    atrs = ir.atr_serisi(b)
    faz = random.randint(0, 23)
    for i in range(ir.ISINMA + faz, len(b) - UFUK - 2, ir.SEYRELT):
        x = b[i]
        if (x.get("qv") or 0) < ir.MIN_VOL/24 or i < 24: continue
        if (x["c"]/b[i-24]["c"]-1)*100 >= ir.PUMP: continue
        k = bisect.bisect_right(ft, x["t"]) - 1
        if k < 0: continue
        oran = fr[k]["r"]*100
        kume = "KAPI (fund<=-0,05)" if oran <= ir.FUND_ESIK else "KONTROL (fund>-0,05)"
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
        d["ham"].append(hm); d["fon"].append(f); d["net"].append(hm-MAL+f)
        d["ts"].append(b[gi]["t"]); d["oran"].append(oran)

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

def kumeli(v, ts):
    a = collections.defaultdict(list)
    for z, t in zip(v, ts): a[ay(t)].append(z)
    ok = [m for m in a if len(a[m]) >= 20]
    if len(ok) < 3: return None
    ms = [stx.mean(a[m]) for m in ok]
    se = stx.stdev(ms)/len(ms)**0.5
    return stx.mean(ms), (stx.mean(ms)/se if se else 0), len(ok), sum(1 for z in ms if z > 0)

print("BOTUN CEKIRDEK KAPISI — KONTROL GRUPLU SINAV (ayni mekanik)")
print("=" * 104)
print("%-22s %8s %10s %10s %10s %11s %9s"
      % ("kume", "N", "BRUT", "fonlama", "NET", "ay-kumeli t", "poz ay"))
sonuc = {}
for kume in ("KAPI (fund<=-0,05)", "KONTROL (fund>-0,05)"):
    d = K.get(kume)
    if not d or len(d["net"]) < 500: continue
    kn = kumeli(d["net"], d["ts"])
    sonuc[kume] = (stx.mean(d["net"]), d)
    print("%-22s %8d %+10.4f %+10.4f %+10.4f %+11.2f %6d/%-3d"
          % (kume, len(d["net"]), stx.mean(d["ham"]), stx.mean(d["fon"]),
             stx.mean(d["net"]), kn[1] if kn else 0, kn[3] if kn else 0, kn[2] if kn else 0))
if len(sonuc) == 2:
    a = sonuc["KAPI (fund<=-0,05)"][0]; b_ = sonuc["KONTROL (fund>-0,05)"][0]
    print("\nKAPININ KATKISI: %+.4f  ->  %s" % (a-b_, "KAPI DAHA IYI" if a > b_ else "🔴 KAPI DAHA KOTU"))
    # ay-kumeli fark
    da = sonuc["KAPI (fund<=-0,05)"][1]; db = sonuc["KONTROL (fund>-0,05)"][1]
    aa = collections.defaultdict(list); bb = collections.defaultdict(list)
    for z, t in zip(da["net"], da["ts"]): aa[ay(t)].append(z)
    for z, t in zip(db["net"], db["ts"]): bb[ay(t)].append(z)
    ok = [m for m in set(aa) & set(bb) if len(aa[m]) >= 20 and len(bb[m]) >= 20]
    fk = [stx.mean(aa[m])-stx.mean(bb[m]) for m in ok]
    se = stx.stdev(fk)/len(fk)**0.5
    print("AY-KUMELI fark: %d ay · ort %+.4f · t=%+.2f · KAPI ustun oldugu ay %d/%d"
          % (len(ok), stx.mean(fk), stx.mean(fk)/se if se else 0,
             sum(1 for z in fk if z > 0), len(ok)))

print("\nFONLAMA DILIMLERI (kapi esigi -0,05 nerede duruyor?)")
tum = []
for kume in K:
    d = K[kume]
    tum += list(zip(d["oran"], d["net"]))
tum.sort()
n = len(tum)//8
print("%-24s %8s %10s" % ("funding dilimi (%/8s)", "N", "NET"))
for i in range(8):
    g = tum[i*n:(i+1)*n] if i < 7 else tum[7*n:]
    print("%-24s %8d %+10.4f" % ("%.4f .. %.4f" % (g[0][0], g[-1][0]), len(g),
                                 stx.mean([z[1] for z in g])))
