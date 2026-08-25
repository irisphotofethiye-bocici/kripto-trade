# -*- coding: utf-8 -*-
"""HACIM YENI BILGI MI? — KISMI korelasyon.
CLAUDE.md: "olctugumuz her sey tek banttan turuyor, yeni sinyal cogu zaman ayni sey".
Bu betik tam olarak onu sinar: hacim, OYNAKLIK sabitlendiginde hala bilgi tasiyor mu?
SALT OKUMA."""
import json, glob, os, random, math, statistics as sx

KL = r"c:\Users\alper\Desktop\kripto trade\scratchpad\klines_1h_uzun"
random.seed(3)
orn = random.sample(sorted(glob.glob(os.path.join(KL, "*.json"))), 200)

def kor(a, b):
    n = len(a)
    if n < 50: return None
    ma, mb = sum(a)/n, sum(b)/n
    sa = math.sqrt(sum((x-ma)**2 for x in a)); sb = math.sqrt(sum((x-mb)**2 for x in b))
    if sa == 0 or sb == 0: return None
    return sum((a[i]-ma)*(b[i]-mb) for i in range(n))/(sa*sb)

def kismi(xy, xz, zy):
    """x ile y arasindaki korelasyon, z SABITLENDIGINDE."""
    d = math.sqrt(max(1-xz*xz, 1e-12)) * math.sqrt(max(1-zy*zy, 1e-12))
    return (xy - xz*zy)/d if d > 0 else None

hk, ok, ham_h, ham_o = [], [], [], []
for f in orn:
    try: b = json.load(open(f, encoding="utf-8"))
    except Exception: continue
    if len(b) < 1500: continue
    c = [x["c"] for x in b]; qv = [x.get("qv") or 0.0 for x in b]
    r = [(c[i]/c[i-1]-1)*100 if c[i-1] > 0 else 0.0 for i in range(1, len(c))]
    H, O = [], []
    for i in range(0, len(c)-48, 24):
        blok = qv[i:i+24]
        if c[i] <= 0 or sum(blok) <= 0 or i+24 > len(r): continue
        H.append(math.log(sum(blok))); O.append(sx.pstdev(r[i:i+24]))
    if len(H) < 60: continue
    Hn, On, Oy = H[:-1], O[:-1], O[1:]          # simdiki hacim, simdiki oynaklik, GELECEK oynaklik
    r_HY = kor(Hn, Oy); r_OY = kor(On, Oy); r_HO = kor(Hn, On)
    if None in (r_HY, r_OY, r_HO): continue
    ham_h.append(r_HY); ham_o.append(r_OY)
    a = kismi(r_HY, r_HO, r_OY);  b2 = kismi(r_OY, r_HO, r_HY)
    if a is not None: hk.append(a)
    if b2 is not None: ok.append(b2)

def yaz(ad, v):
    v = sorted(v); med = v[len(v)//2]
    poz = 100*sum(1 for x in v if x > 0)/len(v)
    print("  %-52s medyan %+6.3f   POZITIF %%%3.0f   (N=%d)" % (ad, med, poz, len(v)))

print("=" * 100)
print("HACIM, OYNAKLIKTAN BAGIMSIZ BILGI TASIYOR MU?   (200 sembol, her biri ayri)")
print("=" * 100)
print("\nHAM (kontrolsuz):")
yaz("hacim        -> gelecek oynaklik", ham_h)
yaz("oynaklik     -> gelecek oynaklik", ham_o)
print("\nKISMI (digeri SABITLENDIGINDE — asil soru bu):")
yaz("hacim -> gelecek oynaklik | OYNAKLIK sabit", hk)
yaz("oynaklik -> gelecek oynaklik | HACIM sabit", ok)
print("\n  simdiki hacim <-> simdiki oynaklik ortalama ortusme:")
