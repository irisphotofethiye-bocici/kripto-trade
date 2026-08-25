# -*- coding: utf-8 -*-
"""STOP CARPANI KARNESI — on-kayit: ON_KAYIT.md (sonuc gorulmeden yazildi).
Gun-kumeli, holdout'lu, rejim kirilimli. SALT OKUMA."""
import json, os, math, collections, statistics as sx, sys

H = os.path.dirname(os.path.abspath(__file__))
kol = sys.argv[1] if len(sys.argv) > 1 else "b"
d = json.load(open(os.path.join(H, "kol_%s.json" % kol)))
ol, KLAR, HLAR = d["olaylar"], d["KLAR"], d["HLAR"]
ol.sort(key=lambda x: x["t"])
ETIKET = {999.0: "STOPSUZ"}
ad = lambda k: ETIKET.get(k, "%.2f" % k)

def gun_ort(v, anahtar):
    g = collections.defaultdict(list)
    for x in v: g[x["gun"]].append(x["r"][anahtar])
    return {k: sx.mean(z) for k, z in g.items()}

def esl_t(v, a1, a2):
    """ayni girisler, farkli stop -> gun-kumeli ESLESMIS t"""
    g = collections.defaultdict(list)
    for x in v: g[x["gun"]].append(x["r"][a1] - x["r"][a2])
    f = [sx.mean(z) for z in g.values()]
    if len(f) < 3: return None, None, len(f)
    m = sx.mean(f); s = sx.stdev(f)
    return m, (m/(s/math.sqrt(len(f))) if s > 0 else None), len(f)

print("=" * 104)
print("KOL %s — N=%s olay · %d gun · %d sembol   (on-kayit: ON_KAYIT.md)"
      % (kol.upper(), format(len(ol), ","), len(set(x["gun"] for x in ol)), len(set(x["sym"] for x in ol))))
print("=" * 104)

for yon in ("SHORT", "LONG", "HEPSI"):
    v = ol if yon == "HEPSI" else [x for x in ol if x["yon"] == yon]
    if len(v) < 60: continue
    print("\n### %s   N=%s" % (yon, format(len(v), ",")))
    print("  %-8s" % "k" + "".join("%11s" % ("%dsa" % h) for h in HLAR) + "   stop-olma")
    for k in KLAR:
        sat = "  %-8s" % ad(k)
        for h in HLAR:
            gm = gun_ort(v, "%g|%d" % (k, h))
            sat += "%+11.3f" % sx.mean(list(gm.values()))
        so = [x.get("stopta", {}).get("%g" % k) for x in v if x.get("stopta")]
        so = [z for z in so if z is not None]
        sat += "      %s" % ("%%%.0f" % (100*sx.mean(so)) if so else "-")
        print(sat)

print("\n" + "=" * 104)
print("OLCUT 1 — HOLDOUT   (k* ILK yarida secilir, IKINCI yarida k=1,50 ile eslesmis kiyas)")
print("=" * 104)
yari = len(ol)//2
k1, k2 = ol[:yari], ol[yari:]
print("  kalibrasyon %s..%s (N=%d)   TEST %s..%s (N=%d)"
      % (k1[0]["gun"], k1[-1]["gun"], len(k1), k2[0]["gun"], k2[-1]["gun"], len(k2)))
for h in HLAR:
    en, enk = None, None
    for k in KLAR:
        m = sx.mean(list(gun_ort(k1, "%g|%d" % (k, h)).values()))
        if en is None or m > en: en, enk = m, k
    a1 = "%g|%d" % (enk, h); a2 = "%g|%d" % (1.50, h)
    fark, t, ng = esl_t(k2, a1, a2)
    tt = sx.mean(list(gun_ort(k2, a1).values())); tb = sx.mean(list(gun_ort(k2, a2).values()))
    huk = "GECTI" if (fark or 0) > 0 else "KALDI"
    print("  %2dsa  k*=%-8s (kalib %+.3f) | TEST: k* %+.3f  vs  1,50 %+.3f  ->  fark %+.3f  t=%s  gun=%d  %s"
          % (h, ad(enk), en, tt, tb, fark or 0, ("%+.2f" % t) if t else "?", ng, huk))

print("\n" + "=" * 104)
print("OLCUT 2 — REJIM   (k* ustunlugu en az 2/3 rejimde korunmali)")
print("=" * 104)
for h in HLAR:
    en, enk = None, None
    for k in KLAR:
        m = sx.mean(list(gun_ort(k1, "%g|%d" % (k, h)).values()))
        if en is None or m > en: en, enk = m, k
    sat = "  %2dsa  k*=%-8s" % (h, ad(enk))
    tut = 0
    for rj in ("ATH_BOLGESI", "DUZELTME", "DERIN_AYI"):
        v = [x for x in ol if x.get("rejim") == rj]
        if len(v) < 100: sat += "  %s: yetersiz" % rj[:4]; continue
        fark, t, ng = esl_t(v, "%g|%d" % (enk, h), "%g|%d" % (1.50, h))
        if (fark or 0) > 0: tut += 1
        sat += "  %s %+.2f(t%s)" % (rj[:4], fark or 0, ("%+.1f" % t) if t else "?")
    sat += "   -> %d/3 %s" % (tut, "GECTI" if tut >= 2 else "KALDI")
    print(sat)

print("\n" + "=" * 104)
print("OLCUT 5 — LIKIDASYON DENETIMI  (azami ters hareket, 24sa icinde)")
print("=" * 104)
ters = sorted(x["ters"] for x in ol)
print("  medyan %%%.2f   %%75 %%%.2f   %%90 %%%.2f   %%95 %%%.2f   %%99 %%%.2f"
      % (ters[len(ters)//2], ters[int(len(ters)*.75)], ters[int(len(ters)*.90)],
         ters[int(len(ters)*.95)], ters[int(len(ters)*.99)]))
for kald in (3, 5, 10):
    esik = 100.0/kald*0.9
    n = sum(1 for x in ters if x >= esik)
    print("  kaldirac %2dx (liq ~%%%.0f)  ->  olaylarin %%%.2f'si likide olurdu" % (kald, esik, 100*n/len(ters)))
