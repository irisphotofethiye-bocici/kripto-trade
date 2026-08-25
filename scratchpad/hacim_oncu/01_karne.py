# -*- coding: utf-8 -*-
"""HACIM ONCU SINYAL — karne. On-kayit: ON_KAYIT.md (sonuc gorulmeden yazildi).
SALT OKUMA."""
import json, os, math, datetime, collections, statistics as sx

KL = r"c:\Users\alper\Desktop\kripto trade\scratchpad\klines_1h_uzun"
KAT, RET = 4.0, 0.50
HL = (1, 2, 4, 8)
b = json.load(open(os.path.join(KL, "BTC.json"), encoding="utf-8"))

kayit = []
for i in range(25, len(b)-max(HL)-1):
    onc = [b[j]["qv"] for j in range(i-24, i)]
    med = sx.median(onc)
    if med <= 0 or b[i-1]["c"] <= 0 or b[i]["c"] <= 0: continue
    kat = b[i]["qv"]/med
    r0 = (b[i]["c"]/b[i-1]["c"]-1)*100
    # karistirici: son 24 saatin gerceklesmis oynakligi
    rr = [(b[j]["c"]/b[j-1]["c"]-1)*100 for j in range(i-24, i) if b[j-1]["c"] > 0]
    oyn = sx.pstdev(rr) if len(rr) > 5 else 0.0
    z = {"t": b[i]["t"], "kat": kat, "r0": r0, "oyn": oyn,
         "gun": datetime.datetime.utcfromtimestamp(b[i]["t"]/1000).strftime("%Y-%m-%d"),
         "saat": datetime.datetime.utcfromtimestamp(b[i]["t"]/1000).strftime("%Y-%m-%d %H:%M")}
    for h in HL:
        g = (b[i+h]["c"]/b[i]["c"]-1)*100
        z["g%d" % h] = g; z["a%d" % h] = abs(g)
        z["m%d" % h] = max(max((b[j]["h"]-b[i]["c"])/b[i]["c"]*100,
                               (b[i]["c"]-b[j]["l"])/b[i]["c"]*100) for j in range(i+1, i+h+1))
    kayit.append(z)

OLC  = [x for x in kayit if x["kat"] >= KAT and abs(x["r0"]) <= RET]
KON1 = [x for x in kayit if x["kat"] >= KAT and abs(x["r0"]) > RET]
KON2 = [x for x in kayit if x["kat"] < KAT]
print("=" * 96)
print("HACIM ONCU SINYAL — BTC saatlik, N=%s   (on-kayit: ON_KAYIT.md)" % format(len(kayit), ","))
print("OLAY: hacim>=%.0fx VE |ret|<=%%%.2f" % (KAT, RET))
print("=" * 96)
print("  OLCUM   (hacim var, fiyat YOK) N=%-5d  %d gun" % (len(OLC), len(set(x["gun"] for x in OLC))))
print("  KONTROL1(hacim var, fiyat DA var) N=%-5d" % len(KON1))
print("  KONTROL2(normal saatler)          N=%-5d" % len(KON2))

def gk(v, alan):
    g = collections.defaultdict(list)
    for x in v: g[x["gun"]].append(x[alan])
    return [sx.mean(z) for z in g.values()]

def welch(a, b_):
    if len(a) < 3 or len(b_) < 3: return None, None
    se = math.sqrt(sx.variance(a)/len(a) + sx.variance(b_)/len(b_))
    f = sx.mean(a)-sx.mean(b_)
    return f, (f/se if se > 0 else None)

print("\n--- OLCUT 1: BUYUKLUK  (|ileri getiri|, gun-kumeli) ---")
print("  %-6s %11s %11s %11s   %-16s %s" % ("ufuk", "OLCUM", "KONTROL1", "KONTROL2", "OLCUM-KON1", "hukum"))
for h in HL:
    a = gk(OLC, "a%d" % h); b1 = gk(KON1, "a%d" % h); b2 = gk(KON2, "a%d" % h)
    f, t = welch(a, b1)
    hk = "" if h not in (2, 4) else ("GECTI" if (f or 0) > 0 else "KALDI")
    print("  %-6s %11.3f %11.3f %11.3f   %+7.3f (t%s)  %s"
          % ("%dsa" % h, sx.mean(a), sx.mean(b1), sx.mean(b2), f or 0, ("%+.1f" % t) if t else "?", hk))

print("\n  azami hareket (ufuk icinde, gun-kumeli):")
for h in HL:
    a = gk(OLC, "m%d" % h); b1 = gk(KON1, "m%d" % h)
    f, t = welch(a, b1)
    print("  %-6s OLCUM %7.3f  KON1 %7.3f  fark %+7.3f (t%s)"
          % ("%dsa" % h, sx.mean(a), sx.mean(b1), f or 0, ("%+.1f" % t) if t else "?"))

print("\n--- OLCUT 2 (KRITIK): son 24sa OYNAKLIK sabitlendiginde ---")
oy = sorted(x["oyn"] for x in kayit)
OK = (oy[len(oy)//4], oy[len(oy)//2], oy[3*len(oy)//4])
print("  oynaklik ceyrekleri: %.3f · %.3f · %.3f" % OK)
ok = lambda o: 0 if o < OK[0] else 1 if o < OK[1] else 2 if o < OK[2] else 3
for h in (2, 4):
    sat = "  %dsa" % h; ayni = 0; ge = 0
    for q in range(4):
        a = gk([x for x in OLC if ok(x["oyn"]) == q], "a%d" % h)
        b1 = gk([x for x in KON1 if ok(x["oyn"]) == q], "a%d" % h)
        f, t = welch(a, b1)
        if f is None: sat += "  Q%d: -" % q; continue
        ge += 1
        if f > 0: ayni += 1
        sat += "  Q%d %+.3f(t%s,n%d)" % (q, f, ("%+.1f" % t) if t else "?", len(a))
    sat += "  -> %d/%d %s" % (ayni, ge, "GECTI" if ayni >= 3 else "KALDI")
    print(sat)

print("\n--- OLCUT 3: HOLDOUT ---")
kayit.sort(key=lambda x: x["t"]); yari = len(kayit)//2
for ad, v in (("ILK YARI", kayit[:yari]), ("IKINCI YARI", kayit[yari:])):
    o = [x for x in v if x["kat"] >= KAT and abs(x["r0"]) <= RET]
    k1 = [x for x in v if x["kat"] >= KAT and abs(x["r0"]) > RET]
    sat = "  %-12s (%s..%s) N=%d" % (ad, v[0]["gun"], v[-1]["gun"], len(o))
    for h in (2, 4):
        f, t = welch(gk(o, "a%d" % h), gk(k1, "a%d" % h))
        sat += "   %dsa %+.3f(t%s)" % (h, f or 0, ("%+.1f" % t) if t else "?")
    print(sat)

print("\n--- OLCUT 4: YON (ikincil, beklenti null) ---")
for h in HL:
    a = gk(OLC, "g%d" % h)
    m = sx.mean(a); s = sx.stdev(a)/math.sqrt(len(a))
    yuk = 100*sum(1 for x in OLC if x["g%d" % h] > 0)/len(OLC)
    print("  %-6s ortalama %+6.3f  %%95 GA [%+.3f,%+.3f]   yukari cikan %%%.1f"
          % ("%dsa" % h, m, m-1.96*s, m+1.96*s, yuk))

print("\n--- OLCUT 5: VAKA DENETIMI ---")
for hedef in ("2026-08-19 13:00", "2026-08-18 14:00", "2026-08-19 12:00", "2026-08-19 15:00"):
    v = [x for x in kayit if x["saat"] == hedef]
    for x in v:
        grup = "OLCUM" if (x["kat"] >= KAT and abs(x["r0"]) <= RET) else ("KON1" if x["kat"] >= KAT else "KON2")
        print("  %s  kat %.1fx  ret %+.2f%%  -> %-5s   ileri 2sa %+.2f%%  4sa %+.2f%%"
              % (hedef, x["kat"], x["r0"], grup, x["g2"], x["g4"]))

print("\n--- SAGLAMLIK (esik varyantlari, 4sa |ileri getiri| farki OLCUM-KON1) ---")
for kk in (3.0, 4.0, 5.0):
    sat = "  hacim>=%.0fx" % kk
    for rr in (0.30, 0.50, 0.75):
        o = [x for x in kayit if x["kat"] >= kk and abs(x["r0"]) <= rr]
        k1 = [x for x in kayit if x["kat"] >= kk and abs(x["r0"]) > rr]
        f, t = welch(gk(o, "a4"), gk(k1, "a4"))
        sat += "   |ret|<=%.2f: %+.3f(n%d)" % (rr, f or 0, len(o))
    print(sat)
