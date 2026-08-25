# -*- coding: utf-8 -*-
"""YON mu OYNAKLIK mi tahmin edilebilir? — kullanicinin kendi verisiyle.
Her sembol icin AYRI hesaplanir, sonra sembol MEDYANI raporlanir
(tek bir coin sonucu tasiyamasin). SALT OKUMA."""
import json, glob, os, random, math, statistics as sx

KL = r"c:\Users\alper\Desktop\kripto trade\scratchpad\klines_1h_uzun"
fs = sorted(glob.glob(os.path.join(KL, "*.json")))
random.seed(3)
orn = random.sample(fs, 200)

def kor(a, b):
    n = len(a)
    if n < 50: return None
    ma, mb = sum(a)/n, sum(b)/n
    sa = math.sqrt(sum((x-ma)**2 for x in a)); sb = math.sqrt(sum((x-mb)**2 for x in b))
    if sa == 0 or sb == 0: return None
    return sum((a[i]-ma)*(b[i]-mb) for i in range(n))/(sa*sb)

sonuc = {k: [] for k in ("yon1","yon4","yon24","oyn1","oyn4","oyn24","blok_yon","blok_oyn")}

for f in orn:
    try: b = json.load(open(f, encoding="utf-8"))
    except Exception: continue
    if len(b) < 1500: continue
    c = [x["c"] for x in b]
    r = [(c[i]/c[i-1]-1)*100 if c[i-1] > 0 else 0.0 for i in range(1, len(c))]
    a = [abs(x) for x in r]
    for lag, k1, k2 in ((1,"yon1","oyn1"), (4,"yon4","oyn4"), (24,"yon24","oyn24")):
        v = kor(r[:-lag], r[lag:]);  sonuc[k1].append(v) if v is not None else None
        v = kor(a[:-lag], a[lag:]);  sonuc[k2].append(v) if v is not None else None
    # BLOK: 24 saatlik getiri vs sonraki 24 saatlik getiri / salinim
    gb, ob = [], []
    for i in range(0, len(c)-48, 24):
        if c[i] <= 0 or c[i+24] <= 0: continue
        gb.append((c[i+24]/c[i]-1)*100)
        ob.append(sx.pstdev(r[i:i+24]) if i+24 <= len(r) else 0.0)
    if len(gb) > 40:
        v = kor(gb[:-1], gb[1:]);  sonuc["blok_yon"].append(v) if v is not None else None
        v = kor(ob[:-1], ob[1:]);  sonuc["blok_oyn"].append(v) if v is not None else None

def yaz(ad, k):
    v = [x for x in sonuc[k] if x is not None]
    v.sort()
    med = v[len(v)//2]
    print("  %-34s N=%-4d  medyan korelasyon %+6.3f   -> aciklanan pay  %%%.2f"
          % (ad, len(v), med, 100*med*med))

print("=" * 84)
print("SORU: gecmis, gelecegin NEYINI soyler?   (200 sembol, her biri AYRI, medyan)")
print("=" * 84)
print("\nYON  —  gecmis getiri  ->  gelecek getiri")
yaz("1 saat sonra", "yon1"); yaz("4 saat sonra", "yon4"); yaz("24 saat sonra", "yon24")
yaz("24 saatlik blok -> sonraki blok", "blok_yon")
print("\nOYNAKLIK  —  gecmis salinim  ->  gelecek salinim")
yaz("1 saat sonra", "oyn1"); yaz("4 saat sonra", "oyn4"); yaz("24 saat sonra", "oyn24")
yaz("24 saatlik blok -> sonraki blok", "blok_oyn")

y = sorted(x for x in sonuc["blok_yon"] if x is not None)
o = sorted(x for x in sonuc["blok_oyn"] if x is not None)
print("\n" + "=" * 84)
print("BLOK duzeyinde sembol dagilimi (tek coin tasiyor mu?):")
print("  YON      : %%5 %+.3f | %%25 %+.3f | MEDYAN %+.3f | %%75 %+.3f | %%95 %+.3f"
      % (y[int(len(y)*.05)], y[len(y)//4], y[len(y)//2], y[3*len(y)//4], y[int(len(y)*.95)]))
print("  OYNAKLIK : %%5 %+.3f | %%25 %+.3f | MEDYAN %+.3f | %%75 %+.3f | %%95 %+.3f"
      % (o[int(len(o)*.05)], o[len(o)//4], o[len(o)//2], o[3*len(o)//4], o[int(len(o)*.95)]))
poz_y = 100*sum(1 for x in y if x > 0)/len(y)
poz_o = 100*sum(1 for x in o if x > 0)/len(o)
print("\n  korelasyonu POZITIF cikan sembol orani:   YON %%%.0f    OYNAKLIK %%%.0f" % (poz_y, poz_o))
