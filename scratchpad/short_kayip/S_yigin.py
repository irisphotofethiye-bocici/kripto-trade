#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KAR EDEN YAPILANDIRMA VAR MI? — bugun OLCULEN bilesenleri ust uste koy.

⚠️ DURUSTLUK UYARISI — BU ORNEKLEM ICI BIR INSA.
Bilesenler sonuclara BAKILARAK secildi. O yuzden tek gecerli hakem ZAMAN
BOLUNMESI: A yarisinda kurulan yigin B yarisinda da tutuyor mu?

BILESENLER (hepsi bugun kontrol gruplu olculdu, her biri AYRI kanit):
  + chg24 < %20        pump engeli   (gecenler ham -2,18 · ENGELLEMEK dogru)
  + fiyat > $0,07      ucuz disla    (ucuz ham -0,28 · t=-2,14)
  - funding <= -0,05   KALDIR        (kapi ham -0,54 · t=-4,96)
  + btc_pay bant != UST              (ham lift -4,12/-3,21/-1,48, uc rejimde ayni)
  + stop: ilk 6 saat x2              (eslesmis +0,057 · ay-kumeli t=+2,32)

KADEMELI raporlanir: her bilesen tek tek eklenir, katkisi gorulur.
Iki yon de olculur — SHORT varsayimi da sorgulanir.
"""
import json, os, sys, collections, random, statistics as stx, bisect, datetime, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ileri_rr as ir
import btcpay_rejim as bp

HEDEF, UFUK, MAL = 10.0, 72, 0.1726
UST_ESIK = 2.8755
ERKEN_SA, ERKEN_KAT = 6, 2.0
random.seed(41)

print("btc_pay vekili kuruluyor...")
vx, _ = bp.gostergeler()
print("   %d saatlik deger\n" % len(vx))

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
    atrs = ir.atr_serisi(b)
    faz = random.randint(0, 23)
    for i in range(ir.ISINMA + faz, len(b) - UFUK - 2, ir.SEYRELT):
        x = b[i]
        if (x.get("qv") or 0) < ir.MIN_VOL/24 or i < 24: continue
        sa = x["t"]//3600000
        if sa not in vx: continue
        k = bisect.bisect_right(ft, x["t"]) - 1
        if k < 0: continue
        gi = i+1
        if not atrs[i] or gi >= len(b): continue
        ref = b[gi]["o"]
        if ref <= 0: continue
        son = min(gi+UFUK, len(b))
        if son-gi < 4: continue
        rec = {"ts": b[gi]["t"], "funding": fr[k]["r"]*100,
               "chg24": (x["c"]/b[i-24]["c"]-1)*100, "fiyat": x["c"],
               "ust": vx[sa] >= UST_ESIK}
        for yon in ("SHORT", "LONG"):
            if yon == "SHORT":
                stop0 = ir.stop_hesapla(b, i, ref, atrs[i]); sp = (stop0-ref)/ref*100
                hed = ref*(1-HEDEF/100)
            else:
                stop0 = bp.stop_long(b, i, ref, atrs[i]); sp = (ref-stop0)/ref*100
                hed = ref*(1+HEDEF/100)
            if sp <= 0 or sp < ir.ASGARI_STOP:
                rec[yon] = None; rec[yon+"_e"] = None; continue
            for mod in ("n", "e"):     # n = normal stop · e = ilk 6s x2
                cj = hm = None
                for j in range(gi, son):
                    t = j-gi
                    kat = ERKEN_KAT if (mod == "e" and t < ERKEN_SA) else 1.0
                    st = ref + (stop0-ref)*kat
                    vs = (b[j]["h"] >= st) if yon == "SHORT" else (b[j]["l"] <= st)
                    vh = (b[j]["l"] <= hed) if yon == "SHORT" else (b[j]["h"] >= hed)
                    if vs: cj, hm = j, (-(st-ref)/ref*100 if yon == "SHORT" else -(ref-st)/ref*100); break
                    if vh: cj, hm = j, HEDEF; break
                if cj is None:
                    cj = son-1
                    hm = ((ref-b[son-1]["c"]) if yon == "SHORT" else (b[son-1]["c"]-ref))/ref*100
                f = ir.fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
                fon = f if yon == "SHORT" else -f
                rec[yon if mod == "n" else yon+"_e"] = hm - MAL + fon
        OL.append(rec)

print("olay: %d" % len(OL))
assert all(math.isfinite(o[k]) for o in OL for k in ("SHORT", "LONG") if o.get(k) is not None)

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

def ozet(v, ts):
    if len(v) < 300: return None
    a = collections.defaultdict(list)
    for z, t in zip(v, ts): a[ay(t)].append(z)
    ok = [m for m in a if len(a[m]) >= 20]
    if len(ok) < 3: return None
    ms = [stx.mean(a[m]) for m in ok]
    se = stx.stdev(ms)/len(ms)**0.5
    return stx.mean(v), stx.mean(ms), (stx.mean(ms)/se if se else 0), len(ok), sum(1 for z in ms if z > 0)

ADIMLAR = [
    ("0. HAM EVREN (kapisiz)", lambda o: True),
    ("1. + pump engeli (<%20)", lambda o: o["chg24"] < ir.PUMP),
    ("2. + ucuz disla (>$0,07)", lambda o: o["chg24"] < ir.PUMP and o["fiyat"] > ir.UCUZ_FIYAT),
    ("3. + funding kapisi KALK", lambda o: o["chg24"] < ir.PUMP and o["fiyat"] > ir.UCUZ_FIYAT
     and o["funding"] > -0.05),
    ("4. + btc_pay UST disla", lambda o: o["chg24"] < ir.PUMP and o["fiyat"] > ir.UCUZ_FIYAT
     and o["funding"] > -0.05 and not o["ust"]),
]
for yon in ("SHORT", "LONG"):
    print("\n" + "=" * 108)
    print("### %s — KADEMELI YIGIN" % yon)
    print("=" * 108)
    print("%-26s %8s %10s %10s %9s %8s %11s"
          % ("adim", "N", "net(ort)", "net(ay)", "ay-t", "poz ay", "erken-stop"))
    for ad, fn_ in ADIMLAR:
        g = [o for o in OL if fn_(o) and o.get(yon) is not None]
        if len(g) < 300:
            print("%-26s %8d  N yetersiz" % (ad, len(g))); continue
        v = [o[yon] for o in g]; ts = [o["ts"] for o in g]
        z = ozet(v, ts)
        ve = [o[yon+"_e"] for o in g if o.get(yon+"_e") is not None]
        ze = ozet(ve, [o["ts"] for o in g if o.get(yon+"_e") is not None])
        print("%-26s %8d %+10.4f %+10.4f %+9.2f %5d/%-3d %+11.4f"
              % (ad, len(g), z[0], z[1], z[2], z[4], z[3], ze[1] if ze else 0))

print("\n" + "=" * 108)
print("HAKEM — ZAMAN BOLUNMESI (ornekle-ici insa oldugu icin TEK gecerli sinav)")
print("=" * 108)
son = ADIMLAR[-1][1]
for yon in ("SHORT", "LONG"):
    for anahtar, et in ((yon, "normal stop"), (yon+"_e", "erken-stop")):
        g = sorted([o for o in OL if son(o) and o.get(anahtar) is not None], key=lambda o: o["ts"])
        if len(g) < 600: continue
        y = len(g)//2
        A = ozet([o[anahtar] for o in g[:y]], [o["ts"] for o in g[:y]])
        B = ozet([o[anahtar] for o in g[y:]], [o["ts"] for o in g[y:]])
        if A and B:
            print("%-6s %-12s  A yarisi %+8.4f (t=%+5.2f)  ·  B yarisi %+8.4f (t=%+5.2f)  %s"
                  % (yon, et, A[1], A[2], B[1], B[2],
                     "<-- IKISI DE ARTI" if A[1] > 0 and B[1] > 0 else ""))
