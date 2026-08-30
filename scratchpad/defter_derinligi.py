#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EMIR DEFTERI DERINLIGI kendi islemlerimizin sonucunu ongoruyor mu?
On-kayit: ON_KAYIT_defter_derinligi.md (commit 837631d). Olcutler O1-O5 SABIT.

Birim POZISYON (id ile birlestirilir, P&L toplarken suzgec YOK).
Sonuc = (sum sonuc_usdt + sum funding_usdt) / notional * 100.
Birincil yordayici: basi = notional / defter_usdt_20.
SALT OKUMA — bot dosyalarina dokunmaz.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, datetime, collections, statistics, math, random

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = "%Y-%m-%d %H:%M:%S"
random.seed(20260830)
DEFTERLER = [("testbot", "testbot_islemler.jsonl"), ("golge", "golge_islemler.jsonl"),
             ("ayna", "ayna_islemler.jsonl"), ("defter2", "defter2_islemler.jsonl"),
             ("defter3", "defter3_islemler.jsonl")]


def poz_yukle():
    out = []
    for ad, f in DEFTERLER:
        p = os.path.join(PROJE, f)
        if not os.path.exists(p):
            continue
        g = collections.defaultdict(list)
        for s in open(p, encoding="utf-8"):
            if not s.strip():
                continue
            try:
                x = json.loads(s)
            except Exception:
                continue
            g[x.get("id")].append(x)
        for i, v in g.items():
            v.sort(key=lambda z: z["ts"])
            ilk, son = v[0], v[-1]
            d = ilk.get("derinlik_giriste")
            if not d or not d.get("defter_usdt_20"):
                continue
            no = ilk.get("notional") or 0
            if no <= 0:
                continue
            net = sum((t.get("sonuc_usdt") or 0) for t in v)          # SUZGEC YOK
            fon = [t.get("funding_usdt") for t in v if t.get("funding_usdt") is not None]
            kap = datetime.datetime.strptime(son["ts"], F)
            gir = kap - datetime.timedelta(hours=max((t.get("tutma_saat") or 0) for t in v))
            out.append(dict(
                defter=ad, sym=son["sym"], yon=son["yon"], gun=gir.date(),
                notional=no, kaldirac=ilk.get("kaldirac") or 0,
                chg24=ilk.get("chg24_giriste"), sebep=son.get("sebep"),
                basi=no / d["defter_usdt_20"],
                slipaj=d.get("slipaj_pct"), derinlik=d["defter_usdt_20"],
                yetersiz=bool(d.get("yetersiz")),
                ret=100.0 * (net + (sum(fon) if fon else 0.0)) / no))
    return out


P = poz_yukle()
print("EMIR DEFTERI DERINLIGI — kendi islemlerimizde ongoru var mi?")
print("on-kayit ON_KAYIT_defter_derinligi.md (837631d) · olcutler SABIT")
print("=" * 116)
print("pozisyon %d  ·  defter %d  ·  gun %d  ·  sembol %d"
      % (len(P), len(set(x["defter"] for x in P)), len(set(x["gun"] for x in P)),
         len(set(x["sym"] for x in P))))
for ad, _ in DEFTERLER:
    w = [x for x in P if x["defter"] == ad]
    if w:
        print("   %-8s N=%4d  ret ort %+7.3f%%  basi medyan %.4f"
              % (ad, len(w), sum(x["ret"] for x in w) / len(w),
                 statistics.median([x["basi"] for x in w])))

# --- ceyrekler (olcutten ONCE sabitlenir)
bs = sorted(x["basi"] for x in P)
Q = [bs[int(k / 4 * len(bs))] for k in range(1, 4)]


def ceyrek(x):
    return sum(1 for q in Q if x["basi"] >= q)


CAD = ["Q1 (en INCE poz)", "Q2", "Q3", "Q4 (en KALIN poz)"]
print("\n   basi = notional / defter_usdt_20   ceyrek sinirlari: %s"
      % " · ".join("%.4f" % q for q in Q))

print("\n1) CEYREKLER")
print("-" * 116)
print("   %-18s %6s %10s %10s %9s %9s %9s %9s" %
      ("ceyrek", "N", "ret ort", "ret med", "kazanan", "kaldirac", "chg24", "slipaj"))
ort = []
for k in range(4):
    w = [x for x in P if ceyrek(x) == k]
    if not w:
        ort.append(0.0)
        continue
    r = [x["ret"] for x in w]
    ort.append(sum(r) / len(r))
    sl = [x["slipaj"] for x in w if x["slipaj"] is not None]
    ch = [x["chg24"] for x in w if x["chg24"] is not None]
    print("   %-18s %6d %+9.3f%% %+9.3f%% %8.0f%% %9.1f %+8.1f %8.4f" %
          (CAD[k], len(w), sum(r) / len(r), statistics.median(r),
           100.0 * sum(1 for x in r if x > 0) / len(r),
           statistics.median([x["kaldirac"] for x in w]),
           statistics.median(ch) if ch else 0, statistics.median(sl) if sl else 0))


def spearman(v):
    n = len(v)
    sr = sorted(range(n), key=lambda i: v[i])
    r2 = [0] * n
    for rank, i in enumerate(sr):
        r2[i] = rank
    d2 = sum((i - r2[i]) ** 2 for i in range(n))
    return 1 - 6 * d2 / (n * (n * n - 1))


def kume_t(a, b, anahtar, nmin=3):
    ga, gb = collections.defaultdict(list), collections.defaultdict(list)
    for x in a:
        ga[x[anahtar]].append(x["ret"])
    for x in b:
        gb[x[anahtar]].append(x["ret"])
    d = [sum(ga[g]) / len(ga[g]) - sum(gb[g]) / len(gb[g])
         for g in sorted(set(ga) & set(gb)) if len(ga[g]) >= nmin and len(gb[g]) >= nmin]
    if len(d) < 2:
        return None, None, 0, len(d)
    m, sd = sum(d) / len(d), statistics.stdev(d)
    return m, (m / (sd / math.sqrt(len(d))) if sd else None), sum(1 for x in d if x < 0), len(d)


ust = [x for x in P if ceyrek(x) == 3]
alt = [x for x in P if ceyrek(x) == 0]
fark = (sum(x["ret"] for x in ust) / len(ust)) - (sum(x["ret"] for x in alt) / len(alt))

print("\nO1 — ust ceyrek (en kalin poz) - alt ceyrek")
print("-" * 116)
mg, tg, pg, ng = kume_t(ust, alt, "gun")
ms, ts_, ps, ns = kume_t(ust, alt, "sym", nmin=2)
print("   havuzlanmis fark %+7.3f puan" % fark)
print("   GUN-kumeli    ort %+7.3f  t = %s  (%d/%d gun negatif)"
      % (mg or 0, "%+.2f" % tg if tg else "-", pg, ng))
print("   SEMBOL-kumeli ort %+7.3f  t = %s  (%d/%d sembol negatif)"
      % (ms or 0, "%+.2f" % ts_ if ts_ else "-", ps, ns))
O1 = (fark <= -0.3 and tg is not None and tg <= -2.5)
print("   O1 (<=-0,3 VE gun-kumeli t<=-2,5): %s" % ("GECTI" if O1 else "DUSTU"))

print("\nO2 — monotonluk")
print("-" * 116)
rho = spearman(ort)
O2 = rho <= -0.75
print("   Spearman rho (4 ceyrek) = %+.3f   (esik <= -0,75)  ->  %s"
      % (rho, "GECTI" if O2 else "DUSTU"))

print("\nO3 — BELIRLEYICI: kaldirac ve defter icinde ayakta mi")
print("-" * 116)
isaret = 1 if fark > 0 else -1
print("   havuzlanmis isaret: %s" % ("POZITIF" if isaret > 0 else "NEGATIF"))
print("   %-16s %-10s %6s %10s | %6s %10s | %9s" %
      ("katman", "dilim", "ust N", "ust ort", "alt N", "alt ort", "fark"))
ayakta, hucre = 0, 0
kl = sorted(x["kaldirac"] for x in P)
KQ = [kl[int(k / 3 * len(kl))] for k in range(1, 3)]
for katman, fn, etiket in (("kaldirac", lambda x: sum(1 for q in KQ if x["kaldirac"] >= q),
                            ["dusuk", "orta", "yuksek"]),
                           ("defter", lambda x: x["defter"], None)):
    dilimler = sorted(set(fn(x) for x in P), key=str)
    for d in dilimler:
        w = [x for x in P if fn(x) == d]
        u = [x["ret"] for x in w if ceyrek(x) == 3]
        a = [x["ret"] for x in w if ceyrek(x) == 0]
        if len(u) >= 30 and len(a) >= 30:
            hucre += 1
            f = sum(u) / len(u) - sum(a) / len(a)
            if (1 if f > 0 else -1) == isaret:
                ayakta += 1
            ad = etiket[d] if etiket else str(d)
            print("   %-16s %-10s %6d %+9.3f%% | %6d %+9.3f%% | %+8.3f" %
                  (katman, ad, len(u), sum(u) / len(u), len(a), sum(a) / len(a), f))
oran = ayakta / hucre if hucre else 0
O3 = oran >= 0.60 and hucre >= 2
print("   -> %d/%d hucrede havuz isaretiyle AYNI (%%%.0f)  ->  %s"
      % (ayakta, hucre, 100 * oran, "GECTI" if O3 else "DUSTU  ->  HUKUM DUSER"))

print("\nO4 — defterler arasi tutarlilik")
print("-" * 116)
ayni = 0
sayilan = 0
for ad, _ in DEFTERLER:
    w = [x for x in P if x["defter"] == ad]
    u = [x["ret"] for x in w if ceyrek(x) == 3]
    a = [x["ret"] for x in w if ceyrek(x) == 0]
    if len(u) >= 30 and len(a) >= 30:
        sayilan += 1
        f = sum(u) / len(u) - sum(a) / len(a)
        if (1 if f > 0 else -1) == isaret:
            ayni += 1
        print("   %-8s ust %3d %+8.3f%%  ·  alt %3d %+8.3f%%  ->  fark %+7.3f"
              % (ad, len(u), sum(u) / len(u), len(a), sum(a) / len(a), f))
    else:
        print("   %-8s N yetersiz (ust %d / alt %d)" % (ad, len(u), len(a)))
O4 = ayni >= 3
print("   -> %d/%d defterde ayni isaret  ->  %s" % (ayni, sayilan, "GECTI" if O4 else "DUSTU"))

print("\nO5 — SANS: basi GUN ICINDE karistirilir x 2000")
print("-" * 116)
gg = collections.defaultdict(list)
for x in P:
    gg[x["gun"]].append(x)
sahte = []
for _ in range(2000):
    u, a = [], []
    for g, w in gg.items():
        b = [x["basi"] for x in w]
        random.shuffle(b)
        tmp = sorted(zip(b, [x["ret"] for x in w]))
        n = len(tmp)
        if n < 4:
            continue
        k = max(1, n // 4)
        a += [r for _b, r in tmp[:k]]
        u += [r for _b, r in tmp[-k:]]
    if u and a:
        sahte.append(sum(u) / len(u) - sum(a) / len(a))
sahte.sort()
alt_p = sum(1 for x in sahte if x <= fark) / len(sahte)
print("   sahte dagilim: medyan %+7.3f  %%5 %+7.3f  %%95 %+7.3f"
      % (statistics.median(sahte), sahte[int(0.05 * len(sahte))], sahte[int(0.95 * len(sahte))]))
print("   gercek fark %+7.3f  ->  p(sol kuyruk) = %.4f" % (fark, alt_p))
O5 = alt_p <= 0.05
print("   O5: %s" % ("GECTI" if O5 else "DUSTU"))

print("\n2) IKINCIL YORDAYICILAR (onceden ilan edilmis, KESIFSEL)")
print("-" * 116)
for ad, anahtar, ters in (("slipaj_pct", "slipaj", False),
                          ("defter_usdt_20 (mutlak)", "derinlik", False)):
    w = [x for x in P if x[anahtar] is not None]
    if len(w) < 100:
        continue
    v = sorted(x[anahtar] for x in w)
    q = [v[int(k / 4 * len(v))] for k in range(1, 4)]
    o = []
    for k in range(4):
        c = [x["ret"] for x in w if sum(1 for z in q if x[anahtar] >= z) == k]
        o.append(sum(c) / len(c) if c else 0)
    print("   %-24s ceyrek ort: %s   rho %+.2f"
          % (ad, " · ".join("%+.3f" % z for z in o), spearman(o)))
ye = [x["ret"] for x in P if x["yetersiz"]]
hy = [x["ret"] for x in P if not x["yetersiz"]]
if ye and hy:
    print("   %-24s yetersiz=True N=%d %+7.3f%%  ·  False N=%d %+7.3f%%  fark %+7.3f"
          % ("yetersiz (defter bitti)", len(ye), sum(ye) / len(ye), len(hy), sum(hy) / len(hy),
             sum(ye) / len(ye) - sum(hy) / len(hy)))

print("\n3) YON KIRILIMI (rapor)")
print("-" * 116)
for yon in ("LONG", "SHORT"):
    w = [x for x in P if x["yon"] == yon]
    if len(w) < 30:
        continue
    u = [x["ret"] for x in w if ceyrek(x) == 3]
    a = [x["ret"] for x in w if ceyrek(x) == 0]
    print("   %-6s N=%4d   ust %3d %+8.3f%%  alt %3d %+8.3f%%  fark %s"
          % (yon, len(w), len(u), sum(u) / len(u) if u else 0,
             len(a), sum(a) / len(a) if a else 0,
             "%+7.3f" % (sum(u) / len(u) - sum(a) / len(a)) if u and a else "-"))

print("\n" + "=" * 116)
print("HUKUM")
print("=" * 116)
print("   O1 %s · O2 %s · O3 %s · O4 %s · O5 %s"
      % (*("GECTI" if z else "DUSTU" for z in (O1, O2, O3, O4, O5)),))
if not O3:
    print("   -> DUSTU (O3 belirleyici)")
elif O1 and O2 and O3 and O5:
    print("   -> GECTI")
elif O1 and O3:
    print("   -> ZAYIF")
else:
    print("   -> DUSTU")
print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
