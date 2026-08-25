# -*- coding: utf-8 -*-
"""HACIM NE KADAR DEGERLI? — kullanici tezi: "hacim elimizdeki en degerli veri".
04_yon_vs_oynaklik ile AYNI yontem: her sembol AYRI, sonra sembol medyani.
SALT OKUMA."""
import json, glob, os, random, math, statistics as sx

KL = r"c:\Users\alper\Desktop\kripto trade\scratchpad\klines_1h_uzun"
fs = sorted(glob.glob(os.path.join(KL, "*.json")))
random.seed(3)                                   # 04 ile AYNI tohum, ayni semboller
orn = random.sample(fs, 200)

def kor(a, b):
    n = len(a)
    if n < 50: return None
    ma, mb = sum(a)/n, sum(b)/n
    sa = math.sqrt(sum((x-ma)**2 for x in a)); sb = math.sqrt(sum((x-mb)**2 for x in b))
    if sa == 0 or sb == 0: return None
    return sum((a[i]-ma)*(b[i]-mb) for i in range(n))/(sa*sb)

K = ("hac_hac", "hac_oyn", "oyn_oyn", "hac_yon", "hac_mutyon", "islem_oyn", "taker_yon")
s = {k: [] for k in K}

for f in orn:
    try: b = json.load(open(f, encoding="utf-8"))
    except Exception: continue
    if len(b) < 1500: continue
    c  = [x["c"] for x in b]
    qv = [x.get("qv") or 0.0 for x in b]          # dolar hacmi
    nn = [x.get("n") or 0 for x in b]             # islem sayisi
    tb = [x.get("tbv") or 0.0 for x in b]         # taker ALIS hacmi
    v  = [x.get("v") or 0.0 for x in b]
    r  = [(c[i]/c[i-1]-1)*100 if c[i-1] > 0 else 0.0 for i in range(1, len(c))]

    # 24 saatlik bloklar
    H, G, N, T, O = [], [], [], [], []
    for i in range(0, len(c)-48, 24):
        if c[i] <= 0 or c[i+24] <= 0: continue
        blok = qv[i:i+24]
        if sum(blok) <= 0: continue
        H.append(math.log(sum(blok)))                       # log dolar hacim
        G.append((c[i+24]/c[i]-1)*100)                      # yon
        N.append(math.log(max(sum(nn[i:i+24]), 1)))         # islem sayisi
        tv = sum(v[i:i+24])
        T.append(sum(tb[i:i+24])/tv if tv > 0 else 0.5)     # taker alis orani
        O.append(sx.pstdev(r[i:i+24]) if i+24 <= len(r) else 0.0)
    if len(H) < 40: continue

    def ek(k, a, b_):
        val = kor(a, b_)
        if val is not None: s[k].append(val)

    ek("hac_hac",   H[:-1], H[1:])          # hacim -> gelecek hacim
    ek("hac_oyn",   H[:-1], O[1:])          # hacim -> gelecek OYNAKLIK
    ek("oyn_oyn",   O[:-1], O[1:])          # oynaklik -> gelecek oynaklik (kiyas)
    ek("hac_yon",   H[:-1], G[1:])          # hacim -> gelecek YON
    ek("hac_mutyon",H[:-1], [abs(x) for x in G[1:]])   # hacim -> gelecek hareket BUYUKLUGU
    ek("islem_oyn", N[:-1], O[1:])          # islem sayisi -> gelecek oynaklik
    ek("taker_yon", T[:-1], G[1:])          # taker alis orani -> gelecek YON

def yaz(ad, k):
    v = sorted(x for x in s[k] if x is not None)
    if not v: print("  %-42s (veri yok)" % ad); return
    med = v[len(v)//2]
    poz = 100*sum(1 for x in v if x > 0)/len(v)
    print("  %-42s medyan %+6.3f  pay %%%5.2f  POZITIF cikan sembol %%%3.0f"
          % (ad, med, 100*med*med, poz))

print("=" * 96)
print("HACIM TEZI — 24 saatlik bloklar, 200 sembol, her biri AYRI, sembol medyani")
print("=" * 96)
print("\nHACIM NEYI SOYLUYOR?")
yaz("hacim -> gelecek HACIM",              "hac_hac")
yaz("hacim -> gelecek OYNAKLIK",           "hac_oyn")
yaz("islem sayisi -> gelecek OYNAKLIK",    "islem_oyn")
yaz("hacim -> gelecek hareket BUYUKLUGU",  "hac_mutyon")
print("\nHACIM YON SOYLUYOR MU?")
yaz("hacim -> gelecek YON",                "hac_yon")
yaz("taker ALIS orani -> gelecek YON",     "taker_yon")
print("\nKIYAS TABANI")
yaz("oynaklik -> gelecek OYNAKLIK",        "oyn_oyn")
