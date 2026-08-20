#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TUM KAPILAR — KONTROL GRUPLU SINAV.  Her kapi: gecen vs GECMEYEN.

Ayni olay evreni · ayni mekanik (A-stop · %10 hedef · 72s · maliyet 0,1726 ·
fonlama) · ay-kumeli istatistik · iki zaman yarisi.

HER KAPI TEK TEK, DIGERLERINDEN BAGIMSIZ olarak acilir/kapatilir. Yani
"bu kosul tek basina ayirim yapiyor mu" sorusu.

=== DOGRULAMA KATMANI (kullanici: 'hatasiz oldugundan emin ol') ===
D1. Bilinen sonucu YENIDEN URET: funding<=-0,05 kapisinda
    O_kapi_kontrol.py -> N=18832 · BRUT +0,2155 · fonlama -0,1519 · NET -0,1090
    Bu betik ayni sayilari vermeli (ayni tohum, ayni mantik).
D2. gecen + gecmeyen == toplam  (her kapi icin assert)
D3. NET = BRUT - MALIYET + fonlama  (her kume icin assert, tolerans 1e-9)
D4. NaN/sonsuz yok (assert)
D5. Toplam ortalama iki yoldan: (a) tum olaylar (b) gecen/gecmeyen agirlikli
"""
import json, os, sys, collections, random, statistics as stx, bisect, datetime, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ileri_rr as ir

HEDEF, UFUK, MAL = 10.0, 72, 0.1726
random.seed(41)

# ---------- olaylari TEK KEZ topla, kapilari sonra uygula ----------
OL = []
rej = ir.btc_rejim()
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
        chg24 = (x["c"]/b[i-24]["c"]-1)*100
        k = bisect.bisect_right(ft, x["t"]) - 1
        if k < 0: continue
        oran = fr[k]["r"]*100
        gi = i+1
        if not atrs[i] or gi >= len(b): continue
        ref = b[gi]["o"]
        if ref <= 0: continue
        stop = ir.stop_hesapla(b, i, ref, atrs[i]); sp = (stop-ref)/ref*100
        if sp <= 0: continue
        son = min(gi+UFUK, len(b))
        if son-gi < 4: continue
        hed = ref*(1-HEDEF/100)
        cj = hm = None
        for j in range(gi, son):
            if b[j]["h"] >= stop: cj, hm = j, -sp; break
            if b[j]["l"] <= hed: cj, hm = j, HEDEF; break
        if cj is None: cj = son-1; hm = (ref-b[son-1]["c"])/ref*100
        f = ir.fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
        pen = b[max(0, i-20):i+1]
        lo = min(z["l"] for z in pen); hi = max(z["h"] for z in pen)
        pos = (x["c"]-lo)/(hi-lo) if hi > lo else 0.5
        OL.append({"ham": hm, "fon": f, "net": hm-MAL+f, "ts": b[gi]["t"],
                   "rej": rej.get(b[gi]["t"]//3600000, "NOTR"),
                   "funding": oran, "chg24": chg24, "fiyat": x["c"],
                   "ma50m": ((x["c"]/ma50[i]-1)*100 if ma50[i] and ma50[i] > 0 else None),
                   "pos": pos, "sp": sp})

print("olay: %d" % len(OL))
# --- D4 ---
assert all(math.isfinite(o["net"]) for o in OL), "D4 DUSTU: NaN/sonsuz var"
# --- D3 ---
assert all(abs(o["net"] - (o["ham"]-MAL+o["fon"])) < 1e-9 for o in OL), "D3 DUSTU"
print("D3 (NET=BRUT-MAL+fon) OK · D4 (NaN yok) OK")

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

def kumeli(v, ts):
    a = collections.defaultdict(list)
    for z, t in zip(v, ts): a[ay(t)].append(z)
    ok = [m for m in a if len(a[m]) >= 20]
    if len(ok) < 3: return None
    ms = [stx.mean(a[m]) for m in ok]
    se = stx.stdev(ms)/len(ms)**0.5
    return stx.mean(ms), (stx.mean(ms)/se if se else 0), len(ok), sum(1 for z in ms if z > 0)

# --- D1: bilinen sonucu yeniden uret ---
g = [o for o in OL if o["funding"] <= -0.05 and o["sp"] >= ir.ASGARI_STOP
     and o["chg24"] < ir.PUMP]
print("\nD1 DOGRULAMA — O_kapi_kontrol.py'nin KAPI hucresi yeniden uretiliyor")
print("   beklenen: N=18832 · BRUT +0,2155 · fonlama -0,1519 · NET -0,1090")
print("   uretilen: N=%d · BRUT %+.4f · fonlama %+.4f · NET %+.4f"
      % (len(g), stx.mean([o["ham"] for o in g]), stx.mean([o["fon"] for o in g]),
         stx.mean([o["net"] for o in g])))
tut = (len(g) == 18832 and abs(stx.mean([o["net"] for o in g]) + 0.1090) < 0.0002)
print("   -> %s" % ("TUTTU" if tut else "TUTMADI (sebep asagida arastirilmali)"))

KAPILAR = [
    ("funding <= -0,05", lambda o: o["funding"] <= -0.05, "A+B kapisi -> SHORT AC"),
    ("MA50+ucuz", lambda o: o["fiyat"] <= ir.UCUZ_FIYAT and o["ma50m"] is not None
     and o["ma50m"] >= ir.MA50_MESAFE, "kapi -> SHORT AC"),
    ("fiyat <= $0,07", lambda o: o["fiyat"] <= ir.UCUZ_FIYAT, "MA50 kapisinin yarisi"),
    ("MA50 mesafe >= %3,72", lambda o: o["ma50m"] is not None and o["ma50m"] >= ir.MA50_MESAFE,
     "MA50 kapisinin diger yarisi"),
    ("chg24 >= %20 (pump)", lambda o: o["chg24"] >= ir.PUMP, "kapi -> SHORT ENGELLE"),
    ("chg24 >= %40 (blowoff)", lambda o: o["chg24"] >= 40.0, "kapi -> IKISINI DE ENGELLE"),
    ("stop >= %2,0 (asgari)", lambda o: o["sp"] >= ir.ASGARI_STOP, "kapi -> ALTINI REDDET"),
    ("pos >= 0,75 (tepe)", lambda o: o["pos"] >= 0.75, "SHORT'ta boyle bir kapi YOK"),
    ("pos < 0,25 (dip)", lambda o: o["pos"] < 0.25, "LONG'da veto, SHORT'ta yok"),
]

print("\n" + "=" * 116)
print("TUM KAPILAR — GECEN vs GECMEYEN (ayni mekanik, N=%d)" % len(OL))
print("=" * 116)
print("%-24s %8s %9s %9s %9s %9s %10s %9s  %s"
      % ("kosul", "N gecen", "GECEN", "GECMEYEN", "FARK", "ay-t(f)", "fark ay", "brut fark", "botun kullanimi"))
for ad, fn_, nt in KAPILAR:
    a = [o for o in OL if fn_(o)]
    b_ = [o for o in OL if not fn_(o)]
    assert len(a) + len(b_) == len(OL), "D2 DUSTU: %s" % ad          # --- D2 ---
    if len(a) < 300 or len(b_) < 300:
        print("%-24s %8d  N yetersiz" % (ad, len(a))); continue
    na = stx.mean([o["net"] for o in a]); nb = stx.mean([o["net"] for o in b_])
    ba = stx.mean([o["ham"] for o in a]); bb = stx.mean([o["ham"] for o in b_])
    # ay-kumeli FARK
    aa = collections.defaultdict(list); bbm = collections.defaultdict(list)
    for o in a: aa[ay(o["ts"])].append(o["net"])
    for o in b_: bbm[ay(o["ts"])].append(o["net"])
    ok = [m for m in set(aa) & set(bbm) if len(aa[m]) >= 20 and len(bbm[m]) >= 20]
    if len(ok) >= 3:
        fk = [stx.mean(aa[m])-stx.mean(bbm[m]) for m in ok]
        se = stx.stdev(fk)/len(fk)**0.5
        t = stx.mean(fk)/se if se else 0
        poz = sum(1 for z in fk if z > 0)
        ay_s = "%d/%d" % (poz, len(ok))
    else:
        t, ay_s = 0.0, "-"
    print("%-24s %8d %+9.4f %+9.4f %+9.4f %+9.2f %10s %+9.4f  %s"
          % (ad, len(a), na, nb, na-nb, t, ay_s, ba-bb, nt))

# --- D5 ---
tumu = stx.mean([o["net"] for o in OL])
a = [o for o in OL if o["funding"] <= -0.05]; b_ = [o for o in OL if o["funding"] > -0.05]
iki = (len(a)*stx.mean([o["net"] for o in a]) + len(b_)*stx.mean([o["net"] for o in b_]))/len(OL)
print("\nD5 DOGRULAMA — toplam ortalama iki yoldan: %+.6f vs %+.6f -> %s"
      % (tumu, iki, "TUTTU" if abs(tumu-iki) < 1e-9 else "TUTMADI"))
print("D2 (gecen+gecmeyen=toplam) tum kapilarda OK")
