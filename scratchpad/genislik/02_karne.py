# -*- coding: utf-8 -*-
"""GENISLIK KARNESI — on-kayit: ON_KAYIT.md (sonuc gorulmeden yazildi).
Olaylar: stop_carpani/kol_b.json (N=13.159). Getiriler k=1,50 (BOTUN stopu).
SALT OKUMA."""
import json, os, math, collections, statistics as sx, bisect

H = os.path.dirname(os.path.abspath(__file__))
gen = json.load(open(os.path.join(H, "genislik.json")))
gts = sorted(int(k) for k in gen)
d = json.load(open(os.path.join(os.path.dirname(H), "stop_carpani", "kol_b.json")))
ol = [x for x in d["olaylar"] if x["yon"] == "SHORT"]
ol.sort(key=lambda x: x["t"])

# genisligi olaya BAGLA (giris anindan onceki en yakin saat -> ileriye bakma YOK)
bagli = []
for x in ol:
    i = bisect.bisect_right(gts, x["t"]) - 1
    if i < 0: continue
    if x["t"] - gts[i] > 3*3600*1000: continue          # 3 saatten bayat ise atla
    g, nsym, btc24 = gen[str(gts[i])]
    y = dict(x); y["gen"] = g; y["btc24"] = btc24
    bagli.append(y)
print("=" * 100)
print("GENISLIK KARNESI — SHORT olaylari  N=%s  (genislik baglanabilen)  ·  %d gun"
      % (format(len(bagli), ","), len(set(x["gun"] for x in bagli))))
print("getiriler k=1,50 (BOTUN stopu) · gun-kumeli")
print("=" * 100)

KES = (16.8, 44.7, 77.8)     # on-kayitta yazili ceyrekler
def kova(g):
    return 0 if g < KES[0] else 1 if g < KES[1] else 2 if g < KES[2] else 3
AD = ("gen<16,8", "16,8-44,7", "44,7-77,8", "gen>77,8")
HL = (2, 4, 8, 24)

def go(v, h):
    g = collections.defaultdict(list)
    for x in v: g[x["gun"]].append(x["r"]["1.5|%d" % h])
    return sx.mean([sx.mean(z) for z in g.values()]), len(g)

print("\n--- OLCUT 1: MONOTONLUK (genislik arttikca SHORT getirisi DUSMELI) ---")
print("  %-12s %6s" % ("kova", "N") + "".join("%11s" % ("%dsa" % h) for h in HL))
kovalar = [[x for x in bagli if kova(x["gen"]) == k] for k in range(4)]
tablo = []
for k in range(4):
    v = kovalar[k]
    sat = "  %-12s %6d" % (AD[k], len(v))
    r = []
    for h in HL:
        m, _ = go(v, h); r.append(m); sat += "%+11.3f" % m
    tablo.append(r); print(sat)
for j, h in enumerate(HL):
    seri = [tablo[k][j] for k in range(4)]
    mono = all(seri[i] >= seri[i+1] for i in range(3))
    print("     %2dsa monoton azalan mi -> %s" % (h, "EVET" if mono else "HAYIR"))

def esl(v1, v2, h):
    """iki AYRIK grup, gun-kumeli Welch"""
    g1 = collections.defaultdict(list); g2 = collections.defaultdict(list)
    for x in v1: g1[x["gun"]].append(x["r"]["1.5|%d" % h])
    for x in v2: g2[x["gun"]].append(x["r"]["1.5|%d" % h])
    a = [sx.mean(z) for z in g1.values()]; b = [sx.mean(z) for z in g2.values()]
    if len(a) < 3 or len(b) < 3: return None, None
    se = math.sqrt(sx.variance(a)/len(a) + sx.variance(b)/len(b))
    fark = sx.mean(a) - sx.mean(b)
    return fark, (fark/se if se > 0 else None)

print("\n--- OLCUT 2: HOLDOUT (ust kova - alt kova, iki zaman yarisinda) ---")
yari = len(bagli)//2
for ad, v in (("ILK YARI", bagli[:yari]), ("IKINCI YARI", bagli[yari:])):
    sat = "  %-12s (%s..%s)" % (ad, v[0]["gun"], v[-1]["gun"])
    for h in HL:
        f, t = esl([x for x in v if kova(x["gen"]) == 3], [x for x in v if kova(x["gen"]) == 0], h)
        sat += "  %dsa %+.3f(t%s)" % (h, f or 0, ("%+.1f" % t) if t else "?")
    print(sat)

print("\n--- OLCUT 3: REJIM (ust-alt farki, en az 2/3) ---")
for h in (4, 24):
    sat = "  %2dsa" % h; tut = 0
    for rj in ("ATH_BOLGESI", "DUZELTME", "DERIN_AYI"):
        v = [x for x in bagli if x.get("rejim") == rj]
        f, t = esl([x for x in v if kova(x["gen"]) == 3], [x for x in v if kova(x["gen"]) == 0], h)
        if f is not None and f < 0: tut += 1
        sat += "  %s %+.2f(t%s)" % (rj[:4], f or 0, ("%+.1f" % t) if t else "?")
    sat += "  -> %d/3 %s" % (tut, "GECTI" if tut >= 2 else "KALDI")
    print(sat)

print("\n--- OLCUT 4 (KRITIK): BTC 24sa getirisi SABITLENDIGINDE ---")
btc = sorted(x["btc24"] for x in bagli)
BK = (btc[len(btc)//4], btc[len(btc)//2], btc[3*len(btc)//4])
print("  BTC 24sa ceyrekleri: %+.2f · %+.2f · %+.2f" % BK)
def bkova(b):
    return 0 if b < BK[0] else 1 if b < BK[1] else 2 if b < BK[2] else 3
for h in (4, 24):
    sat = "  %2dsa" % h; ayni = 0; gecerli = 0
    for bk in range(4):
        v = [x for x in bagli if bkova(x["btc24"]) == bk]
        f, t = esl([x for x in v if kova(x["gen"]) == 3], [x for x in v if kova(x["gen"]) == 0], h)
        if f is None: sat += "  BTC%d: -" % bk; continue
        gecerli += 1
        if f < 0: ayni += 1
        sat += "  BTC%d %+.2f(t%s)" % (bk, f, ("%+.1f" % t) if t else "?")
    sat += "  -> %d/%d %s" % (ayni, gecerli, "GECTI" if ayni >= 3 else "KALDI")
    print(sat)

print("\n--- YOGUNLASMA ---")
cs = collections.Counter(x["sym"] for x in bagli); cg = collections.Counter(x["gun"] for x in bagli)
print("  sembol %d · gun %d · en buyuk sembol payi %%%.1f · en buyuk gun payi %%%.1f"
      % (len(cs), len(cg), 100*cs.most_common(1)[0][1]/len(bagli), 100*cg.most_common(1)[0][1]/len(bagli)))
