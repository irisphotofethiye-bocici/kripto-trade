#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SKOR ILERI GETIRIYI TAHMIN EDIYOR MU? — KOSU A (tam tarama evreni).
On-kayit: ON_KAYIT_skor_tahmin.md (commit a4e0706). Olcutler S1-S5 SABIT.

radar_archive.jsonl CONTEXT'E YUKLENMEZ — burada toplanip ozet basilir.
top_ls/smart/glob_ls/taker/chg24 KULLANILMAZ (gizli secilim, %20-25 dolu).
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, datetime, collections, statistics, math, random

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KL = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
OFSET = -3           # radar ts YEREL (UTC+3) -> UTC.  Olculdu: %100 bar-ici
UFUK = {"H24": 24, "H6": 6}
BANT = [("<2", -1e9, 2), ("2-5", 2, 5), ("5-10", 5, 10), ("10-20", 10, 20),
        ("20-30", 20, 30), ("30-45", 30, 45), (">=45", 45, 1e9)]
random.seed(20260825)


def bant_of(s):
    for ad, lo, hi in BANT:
        if lo <= s < hi:
            return ad
    return BANT[-1][0]


# ---------------------------------------------------------------- 1) arsiv oku
print("SKOR ILERI GETIRIYI TAHMIN EDIYOR MU? — KOSU A")
print("on-kayit ON_KAYIT_skor_tahmin.md (a4e0706) · olcutler SABIT")
print("=" * 118)

gorulen = {}
n_satir = 0
for s in open(os.path.join(PROJE, "radar_archive.jsonl"), encoding="utf-8"):
    s = s.strip()
    if not s:
        continue
    n_satir += 1
    try:
        x = json.loads(s)
    except Exception:
        continue
    ts, sym, sc = x.get("ts"), x.get("sym"), x.get("score")
    if not ts or not sym or sc is None:
        continue
    try:
        t = datetime.datetime.strptime(ts[:16], "%Y-%m-%d %H:%M").replace(minute=0)
    except Exception:
        continue
    k = (sym, t)
    if k in gorulen:
        continue                      # saatteki ILK anlik goruntu
    gorulen[k] = dict(sym=sym, yerel=t, score=float(sc),
                      vol_x=x.get("vol_x"), rejim=x.get("rejim"),
                      stage=x.get("stage"), gun=t.strftime("%Y-%m-%d"))
print("\narsiv satir %d  ->  (sembol,saat) tekil %d  ·  sembol %d  ·  gun %d"
      % (n_satir, len(gorulen), len(set(v["sym"] for v in gorulen.values())),
         len(set(v["gun"] for v in gorulen.values()))))

# bosluk denetimi (CLAUDE.md: arsiv NOKTASAL)
bp = os.path.join(PROJE, "radar_bosluk.jsonl")
if os.path.exists(bp):
    nb = sum(1 for s in open(bp, encoding="utf-8") if s.strip())
    gunler = sorted(set(v["gun"] for v in gorulen.values()))
    saat = collections.Counter(v["gun"] for v in gorulen.values())
    print("radar_bosluk.jsonl kayit %d  ·  pencere %s..%s  ·  gun basi tekil satir medyan %d"
          % (nb, gunler[0], gunler[-1], statistics.median(saat.values())))

# ---------------------------------------------------------------- 2) klines
gerek = collections.defaultdict(list)
for v in gorulen.values():
    gerek[v["sym"]].append(v)

satir = []
eksik_sym, eksik_bar = 0, 0
for n, (sym, kayitlar) in enumerate(sorted(gerek.items())):
    p = os.path.join(KL, sym + ".json")
    if not os.path.exists(p):
        eksik_sym += 1
        continue
    try:
        with open(p, encoding="utf-8") as f:
            b = json.load(f)
    except Exception:
        eksik_sym += 1
        continue
    idx, c, hi, lo = {}, [], [], []
    for i, z in enumerate(b):
        t = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(z["t"]))
        idx[t] = i
        c.append(float(z["c"]))
        hi.append(float(z["h"]))
        lo.append(float(z["l"]))
    for v in kayitlar:
        utc = v["yerel"] + datetime.timedelta(hours=OFSET)
        i = idx.get(utc)
        if i is None:
            eksik_bar += 1
            continue
        g = i + 1                                   # GIRIS = bir SONRAKI saatin kapanisi
        if g < 15 or g + max(UFUK.values()) >= len(c) or c[g] <= 0:
            eksik_bar += 1
            continue
        tr = [max(hi[k] - lo[k], abs(hi[k] - c[k - 1]), abs(lo[k] - c[k - 1]))
              for k in range(g - 13, g + 1)]
        r = dict(v)
        r["atr"] = 100.0 * (sum(tr) / len(tr)) / c[g]
        for ad, H in UFUK.items():
            r[ad] = 100.0 * (c[g + H] / c[g] - 1.0)
        r["bant"] = bant_of(r["score"])
        satir.append(r)
    if (n + 1) % 120 == 0:
        print("   ... %d/%d sembol islendi (satir %d)" % (n + 1, len(gerek), len(satir)),
              flush=True)

print("\nkullanilabilir gozlem %d  ·  kline'i olmayan sembol %d  ·  bar eslesmeyen %d"
      % (len(satir), eksik_sym, eksik_bar))
GUN = sorted(set(r["gun"] for r in satir))
print("gun sayisi %d  (%s .. %s)" % (len(GUN), GUN[0], GUN[-1]))


def ozet(ad, w, alan="H24"):
    if not w:
        print("   %-8s N=0" % ad)
        return None
    p = [r[alan] for r in w]
    print("   %-8s N=%6d   ort %+7.3f%%   medyan %+7.3f%%   pozitif %%%2.0f   ATR med %5.2f%%"
          % (ad, len(w), sum(p) / len(p), statistics.median(p),
             100.0 * sum(1 for x in p if x > 0) / len(p),
             statistics.median([r["atr"] for r in w])))
    return sum(p) / len(p)


def spearman(v):
    n = len(v)
    r1 = list(range(n))
    sr = sorted(range(n), key=lambda i: v[i])
    r2 = [0] * n
    for rank, i in enumerate(sr):
        r2[i] = rank
    d2 = sum((r1[i] - r2[i]) ** 2 for i in range(n))
    return 1 - 6 * d2 / (n * (n * n - 1))


def gun_t(w_hi, w_lo, alan="H24", nmin=5, nmin_lo=10):
    gh = collections.defaultdict(list)
    gl = collections.defaultdict(list)
    for r in w_hi:
        gh[r["gun"]].append(r[alan])
    for r in w_lo:
        gl[r["gun"]].append(r[alan])
    d = [sum(gh[g]) / len(gh[g]) - sum(gl[g]) / len(gl[g])
         for g in sorted(set(gh) & set(gl))
         if len(gh[g]) >= nmin and len(gl[g]) >= nmin_lo]
    if len(d) < 2:
        return None, None, 0, len(d)
    m, sd = sum(d) / len(d), statistics.stdev(d)
    return m, (m / (sd / math.sqrt(len(d))) if sd else None), sum(1 for x in d if x > 0), len(d)


for alan, H in (("H24", 24), ("H6", 6)):
    ana = (alan == "H24")
    print("\n" + "=" * 118)
    print("%s — H = %d saat  %s" % ("BIRINCIL" if ana else "IKINCIL (onceden ilan edilmis)",
                                    H, ""))
    print("=" * 118)
    print("\n1) BANT ORTALAMALARI")
    print("-" * 118)
    ortalar = []
    for ad, lo, hi_ in BANT:
        w = [r for r in satir if r["bant"] == ad]
        o = ozet(ad, w, alan)
        ortalar.append(o if o is not None else 0.0)

    print("\nS1 — monotonluk + uc fark")
    print("-" * 118)
    rho = spearman(ortalar)
    hi_w = [r for r in satir if r["score"] >= 45]
    lo_w = [r for r in satir if r["score"] < 2]
    m1, t1, p1, n1 = gun_t(hi_w, lo_w, alan)
    print("   Spearman rho (7 bant) = %+.3f   (esik >= +0,75)" % rho)
    print("   (>=45) - (<2)  havuzlanmis %+7.3f puan"
          % ((sum(r[alan] for r in hi_w) / len(hi_w)) - (sum(r[alan] for r in lo_w) / len(lo_w))))
    print("   gun-kumeli     fark ort %+7.3f   t = %s   (%d/%d gun pozitif)"
          % (m1 or 0, "%+.2f" % t1 if t1 else "-", p1, n1))
    S1 = (rho >= 0.75 and m1 is not None and m1 >= 0.5 and t1 is not None and t1 >= 2.5)
    print("   S1: %s" % ("GECTI" if S1 else "DUSTU"))

    print("\nS2 — isaret tutarliligi  (>=45 vs <45, gunluk)")
    print("-" * 118)
    alt = [r for r in satir if r["score"] < 45]
    m2, t2, p2, n2 = gun_t(hi_w, alt, alan, nmin=10, nmin_lo=10)
    print("   gunluk eslesmis fark ort %+7.3f  t = %s  ->  %d/%d gun pozitif (%%%.0f)"
          % (m2 or 0, "%+.2f" % t2 if t2 else "-", p2, n2, 100.0 * p2 / n2 if n2 else 0))
    S2 = (n2 > 0 and p2 / n2 >= 0.60)
    print("   S2: %s" % ("GECTI" if S2 else "DUSTU"))

    if not ana:
        continue

    print("\nS3 — BELIRLEYICI: ATR dilimleri ve vol_x bantlari icinde gradyan ayakta mi")
    print("-" * 118)
    atrs = sorted(r["atr"] for r in satir)
    q = [atrs[int(k / 5 * len(atrs))] for k in range(1, 5)]
    vxs = sorted(r["vol_x"] for r in satir if r["vol_x"] is not None)
    vq = [vxs[int(k / 4 * len(vxs))] for k in range(1, 4)]

    def atr_d(r):
        return sum(1 for x in q if r["atr"] >= x)

    def vx_d(r):
        return None if r["vol_x"] is None else sum(1 for x in vq if r["vol_x"] >= x)

    havuz_isaret = 1 if (sum(r[alan] for r in hi_w) / len(hi_w)
                         - sum(r[alan] for r in lo_w) / len(lo_w)) > 0 else -1
    print("   havuzlanmis gradyan isareti: %s" % ("POZITIF" if havuz_isaret > 0 else "NEGATIF"))
    print("   %-14s %-8s %7s %10s | %7s %10s | %9s %8s" %
          ("katman", "dilim", "yuk N", "yuk ort", "dus N", "dus ort", "fark", "rho"))
    ayakta, hucre = 0, 0
    for katman, fn, etiketler in (("ATR beslik", atr_d, ["1", "2", "3", "4", "5"]),
                                  ("vol_x dortlu", vx_d, ["1", "2", "3", "4"])):
        for d in range(len(etiketler)):
            w = [r for r in satir if fn(r) == d]
            yuk = [r[alan] for r in w if r["score"] >= 20]
            dus = [r[alan] for r in w if r["score"] < 5]
            if len(yuk) >= 30 and len(dus) >= 30:
                hucre += 1
                f = sum(yuk) / len(yuk) - sum(dus) / len(dus)
                if (1 if f > 0 else -1) == havuz_isaret:
                    ayakta += 1
                bo = []
                for ad, blo, bhi in BANT:
                    v = [r[alan] for r in w if r["bant"] == ad]
                    bo.append(sum(v) / len(v) if len(v) >= 20 else None)
                gec = [x for x in bo if x is not None]
                rr = spearman(gec) if len(gec) >= 4 else float("nan")
                print("   %-14s %-8s %7d %+9.3f%% | %7d %+9.3f%% | %+8.3f %+7.2f" %
                      (katman, etiketler[d], len(yuk), sum(yuk) / len(yuk),
                       len(dus), sum(dus) / len(dus), f, rr))
    oran3 = ayakta / hucre if hucre else 0
    S3 = oran3 >= 0.60
    print("   -> %d/%d hucrede havuz isaretiyle AYNI (%%%.0f)" % (ayakta, hucre, 100 * oran3))
    print("   S3: %s" % ("GECTI" if S3 else "DUSTU  ->  HUKUM DUSER"))

    print("\nS4 — SANS: score GUN ICINDE karistirilir x 2000")
    print("-" * 118)
    gun_gr = collections.defaultdict(list)
    for r in satir:
        gun_gr[r["gun"]].append(r)
    gercek = (sum(r[alan] for r in hi_w) / len(hi_w)
              - sum(r[alan] for r in alt) / len(alt))
    sahte = []
    for _ in range(2000):
        hs, ls_ = [], []
        for g, w in gun_gr.items():
            sk = [r["score"] for r in w]
            random.shuffle(sk)
            for r, s_ in zip(w, sk):
                (hs if s_ >= 45 else ls_).append(r[alan])
        if hs and ls_:
            sahte.append(sum(hs) / len(hs) - sum(ls_) / len(ls_))
    sahte.sort()
    ust = sum(1 for x in sahte if x >= gercek)
    p4 = ust / len(sahte)
    print("   sahte dagilim: medyan %+7.3f  %%5 %+7.3f  %%95 %+7.3f"
          % (statistics.median(sahte), sahte[int(0.05 * len(sahte))], sahte[int(0.95 * len(sahte))]))
    print("   gercek (>=45)-(<45) %+7.3f  ->  p = %.4f" % (gercek, p4))
    S4 = p4 <= 0.05
    print("   S4: %s" % ("GECTI" if S4 else "DUSTU"))

    print("\nS5 — REJIM KIRILIMI (kesifsel; isaret donuyorsa aynen yazilir)")
    print("-" * 118)
    for rj in ("NOTR", "BOGA", "AYI"):
        w = [r for r in satir if r["rejim"] == rj]
        if len(w) < 200:
            continue
        h = [r[alan] for r in w if r["score"] >= 45]
        l = [r[alan] for r in w if r["score"] < 45]
        if len(h) >= 30 and len(l) >= 30:
            print("   %-6s N=%6d   >=45: N=%5d %+7.3f%%   <45: N=%6d %+7.3f%%   fark %+7.3f"
                  % (rj, len(w), len(h), sum(h) / len(h), len(l), sum(l) / len(l),
                     sum(h) / len(h) - sum(l) / len(l)))
    print("\n   BANT x REJIM (ort %s):" % alan)
    print("   %-8s %12s %12s %12s" % ("bant", "NOTR", "BOGA", "AYI"))
    for ad, blo, bhi in BANT:
        hu = []
        for rj in ("NOTR", "BOGA", "AYI"):
            v = [r[alan] for r in satir if r["bant"] == ad and r["rejim"] == rj]
            hu.append("%+8.3f(%d)" % (sum(v) / len(v), len(v)) if len(v) >= 20 else "-")
        print("   %-8s %12s %12s %12s" % (ad, hu[0], hu[1], hu[2]))

    print("\n" + "=" * 118)
    print("HUKUM")
    print("=" * 118)
    print("   S1 %s · S2 %s · S3 %s · S4 %s"
          % (*("GECTI" if z else "DUSTU" for z in (S1, S2, S3, S4)),))
    if not S3:
        print("   -> DUSTU  (S3 belirleyici)")
    elif S1 and S2 and S3 and S4:
        print("   -> GECTI")
    elif S1 and S3:
        print("   -> ZAYIF")
    else:
        print("   -> DUSTU")

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
