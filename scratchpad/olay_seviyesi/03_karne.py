# -*- coding: utf-8 -*-
"""OLAY SEVIYESI ORNEKLEMIN KARNESI — BETIMLEYICI, hukum yazilmaz.
Iki AYRIK grup (alt-kume degil) -> iki-orneklemli istatistik gecerli.
Gun-kumeli: once GUN ortalamasi, sonra gunler uzerinden t.  SALT OKUMA."""
import json, os, math, collections, datetime, statistics as sx

d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "olaylar.json")))
olay, kontrol = d["olay"], d["kontrol"]
UF = (4, 24, 72)

def gun(x):
    return datetime.datetime.utcfromtimestamp(x["t"]/1000).strftime("%Y-%m-%d")

def gun_ort(v, alan):
    g = collections.defaultdict(list)
    for x in v:
        g[gun(x)].append(x[alan])
    return {k: sx.mean(z) for k, z in g.items()}

def welch(a, b):
    if len(a) < 3 or len(b) < 3:
        return None, None
    ma, mb = sx.mean(a), sx.mean(b)
    va, vb = sx.variance(a), sx.variance(b)
    se = math.sqrt(va/len(a) + vb/len(b))
    return (ma - mb), ((ma - mb)/se if se > 0 else None)

def tek_t(v):
    if len(v) < 3:
        return None
    m = sx.mean(v); s = sx.stdev(v)
    return m/(s/math.sqrt(len(v))) if s > 0 else None

print("=" * 88)
print("1) NAIF SAYIM  (her olay bagimsiz sayilirsa — YANLIS ama yaygin)")
print("=" * 88)
print("%-6s | %-28s | %-28s | %s" % ("ufuk", "OLAY (onu sakin)", "KONTROL (onu sakin degil)", "fark"))
for h in UF:
    a = [x["f%d" % h] for x in olay]
    b = [x["f%d" % h] for x in kontrol]
    fark, t = welch(a, b)
    print("%-6s | N=%-5d ort %+6.2f%%  t %+6.2f | N=%-6d ort %+6.2f%%      | %+6.2f%%  t=%+6.2f"
          % ("%dsa" % h, len(a), sx.mean(a), tek_t(a) or 0, len(b), sx.mean(b), fark, t or 0))

print()
print("=" * 88)
print("2) GUN-KUMELI SAYIM  (CLAUDE.md kurali — ayni gun = 1 kanit)")
print("=" * 88)
for h in UF:
    ga = gun_ort(olay, "f%d" % h)
    gb = gun_ort(kontrol, "f%d" % h)
    ortak = sorted(set(ga) & set(gb))
    # eslesmis: ayni gun icinde olay - kontrol farki
    esl = [ga[k] - gb[k] for k in ortak]
    fark, t = welch(list(ga.values()), list(gb.values()))
    te = tek_t(esl)
    print("%-5s | gun(olay)=%-4d gun(kontrol)=%-4d ortak=%-4d" % ("%dsa" % h, len(ga), len(gb), len(ortak)))
    print("        bagimsiz  : olay %+6.2f%%   kontrol %+6.2f%%   fark %+6.2f%%  t=%+5.2f"
          % (sx.mean(list(ga.values())), sx.mean(list(gb.values())), fark, t or 0))
    print("        ESLESMIS  : ayni gun icinde fark %+6.2f%%  t=%+5.2f   (gun N=%d)"
          % (sx.mean(esl) if esl else 0, te or 0, len(esl)))

print()
print("=" * 88)
print("3) REJIM KIRILIMI  (isaret rejimle donuyor mu?)")
print("=" * 88)
print("%-14s %6s | %-22s | %-22s | %s" % ("rejim", "N olay", "olay 24sa", "kontrol 24sa", "fark"))
for rj in ("ATH_BOLGESI", "DUZELTME", "DERIN_AYI"):
    a = [x["f24"] for x in olay if x["rejim"] == rj]
    b = [x["f24"] for x in kontrol if x["rejim"] == rj]
    if len(a) < 5:
        print("%-14s %6d | (yetersiz)" % (rj, len(a))); continue
    ga = gun_ort([x for x in olay if x["rejim"] == rj], "f24")
    fark, t = welch(a, b)
    print("%-14s %6d | ort %+6.2f%%  gun=%-4d | ort %+6.2f%% N=%-5d | %+6.2f%%  t=%+5.2f"
          % (rj, len(a), sx.mean(a), len(ga), sx.mean(b), len(b), fark, t or 0))

print()
print("=" * 88)
print("4) YOGUNLASMA DENETIMI  (tek sembol/tek gun tasiyor mu?)")
print("=" * 88)
s = collections.Counter(x["sym"] for x in olay)
g = collections.Counter(gun(x) for x in olay)
print("en cok olay veren 5 sembol :", ", ".join("%s(%d)" % kv for kv in s.most_common(5)))
print("en cok olay olan 5 gun     :", ", ".join("%s(%d)" % kv for kv in g.most_common(5)))
print("en buyuk sembol payi       : %%%.1f     en buyuk gun payi : %%%.1f"
      % (100*s.most_common(1)[0][1]/len(olay), 100*g.most_common(1)[0][1]/len(olay)))
