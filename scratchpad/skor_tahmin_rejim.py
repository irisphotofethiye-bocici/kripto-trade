#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S5 DUZELTMESI + SAGLAMLIK — skor_tahmin.py'nin rejim kirilimi yeniden.

NEDEN: radar_archive'in `rejim` alani 2026-07-22'de TANIM DEGISTIRDI.
   F10 SEZON x HAVA katmanlamasi o gun eklendi (evren.py:294 kendi notu).
   Oncesinde alan ESKI tek-katmanli (1d SMA20) detektorden geliyor.
   Olculdu — Temmuz gunleri:  benim uretimim sezon=AYI · hava=BOGA
   -> TEPKI_RALLISI -> 3'lu map = AYI ;  arsiv ise "BOGA" yaziyor.
   Yani arsivin alani o donemde `hava`ya denk dusuyor.
   Bu boundary'yi asan her rejim kirilimi IKI FARKLI TANIMI karistirir.

DUZELTME: rejim, BTC 1h mumundan gun gun YENIDEN URETILIR (tek tanim, nedensel).
Ayrica zaman-yarilari saglamlik kontrolu eklenir.
Olcutler DEGISTIRILMEDI — S5 zaten KESIFSEL rapordu.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, datetime, collections, statistics, math

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KL = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
OFSET = -3
BANT = [("<2", -1e9, 2), ("2-5", 2, 5), ("5-10", 5, 10), ("10-20", 10, 20),
        ("20-30", 20, 30), ("30-45", 30, 45), (">=45", 45, 1e9)]


def bant_of(s):
    for ad, lo, hi in BANT:
        if lo <= s < hi:
            return ad
    return ">=45"


# ---------------- rejim serisi (tek tanim, nedensel, F10 3'lu map)
def rejim_serisi():
    with open(os.path.join(KL, "BTC.json"), encoding="utf-8") as f:
        bars = json.load(f)
    g = {}
    for b in bars:
        d = (datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(b["t"]))).date()
        g[d] = float(b["c"])
    G = sorted(g.items())
    out = {}
    for i in range(len(G)):
        hafta = {}
        for d, c in G[:i + 1]:
            hafta[d.isocalendar()[:2]] = (d, c)
        wc = [c for k, (d, c) in sorted(hafta.items())]
        if len(wc) < 21:
            continue
        wo = statistics.mean(wc[-21:-1])
        sezon = ("BOGA" if (wc[-1] > wo and wc[-1] - wc[-21] > 0)
                 else ("AYI" if (wc[-1] < wo and wc[-1] - wc[-21] < 0) else "NOTR"))
        cl = [c for d, c in G[max(0, i - 59):i + 1]]
        ham = []
        for j in range(20, len(cl)):
            sma = statistics.mean(cl[j - 20:j])
            uz = (cl[j] - sma) / sma * 100
            ham.append("NOTR" if abs(uz) < 2.0 else ("BOGA" if uz > 0 else "AYI"))
        hava = ham[0] if ham else "NOTR"
        for j in range(len(ham)):
            if j < 3:
                hava = ham[j]
            else:
                pen = ham[j - 2:j + 1]
                if all(x == pen[0] for x in pen):
                    hava = pen[0]
        if sezon == "AYI" and hava == "BOGA":
            f10 = "TEPKI_RALLISI"
        elif sezon == "BOGA" and hava == "BOGA":
            f10 = "TAM_BOGA"
        elif sezon == "AYI" and hava == "AYI":
            f10 = "DERIN_AYI"
        elif sezon == "BOGA" and hava == "AYI":
            f10 = "BOGA_DUZELTME"
        else:
            f10 = "BELIRSIZ"
        out[G[i][0]] = (("BOGA" if f10 == "TAM_BOGA"
                         else ("AYI" if f10 in ("TEPKI_RALLISI", "DERIN_AYI") else "NOTR")),
                        f10, sezon, hava)
    return out


REJ = rejim_serisi()

# ---------------- arsiv + kline (skor_tahmin.py ile AYNI boru hatti)
gorulen = {}
for s in open(os.path.join(PROJE, "radar_archive.jsonl"), encoding="utf-8"):
    s = s.strip()
    if not s:
        continue
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
    if (sym, t) in gorulen:
        continue
    gorulen[(sym, t)] = dict(sym=sym, yerel=t, score=float(sc),
                             arsiv_rejim=x.get("rejim"), gun=t.date())

gerek = collections.defaultdict(list)
for v in gorulen.values():
    gerek[v["sym"]].append(v)

satir = []
for sym, kayitlar in sorted(gerek.items()):
    p = os.path.join(KL, sym + ".json")
    if not os.path.exists(p):
        continue
    try:
        with open(p, encoding="utf-8") as f:
            b = json.load(f)
    except Exception:
        continue
    idx, c = {}, []
    for i, z in enumerate(b):
        t = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(z["t"]))
        idx[t] = i
        c.append(float(z["c"]))
    for v in kayitlar:
        i = idx.get(v["yerel"] + datetime.timedelta(hours=OFSET))
        if i is None:
            continue
        g = i + 1
        if g < 15 or g + 24 >= len(c) or c[g] <= 0:
            continue
        r = dict(v)
        r["H24"] = 100.0 * (c[g + 24] / c[g] - 1.0)
        r["bant"] = bant_of(r["score"])
        rj = REJ.get(v["gun"])
        r["rejim"] = rj[0] if rj else None
        r["f10"] = rj[1] if rj else None
        satir.append(r)

print("S5 DUZELTMESI — rejim TEK TANIMLA yeniden uretildi")
print("=" * 112)
print("gozlem %d  ·  gun %d" % (len(satir), len(set(r["gun"] for r in satir))))

print("\n0) TANIM KIRILMASI — arsivin alani vs tek-tanimli yeniden uretim")
print("-" * 112)
uyum = collections.Counter()
for r in satir:
    if r["arsiv_rejim"] and r["rejim"]:
        uyum[(r["arsiv_rejim"], r["rejim"])] += 1
print("   %-16s %-16s %8s" % ("arsiv alani", "yeniden uretim", "N"))
for (a, b_), n in uyum.most_common(9):
    print("   %-16s %-16s %8d %s" % (a, b_, n, "" if a == b_ else "  <-- CELISKI"))
uy = sum(n for (a, b_), n in uyum.items() if a == b_)
print("   uyum orani %%%.1f" % (100.0 * uy / sum(uyum.values())))


def satirla(ad, w):
    if len(w) < 30:
        return
    h = [r["H24"] for r in w if r["score"] >= 45]
    l = [r["H24"] for r in w if r["score"] < 45]
    if len(h) < 20 or len(l) < 20:
        print("   %-22s N=%6d   (>=45 N=%d — yetersiz)" % (ad, len(w), len(h)))
        return
    print("   %-22s N=%6d   >=45: N=%5d %+7.3f%%   <45: N=%6d %+7.3f%%   fark %+7.3f"
          % (ad, len(w), len(h), sum(h) / len(h), len(l), sum(l) / len(l),
             sum(h) / len(h) - sum(l) / len(l)))


print("\n1) REJIM (tek tanim, F10 3'lu map)")
print("-" * 112)
for rj in ("NOTR", "AYI", "BOGA"):
    satirla(rj, [r for r in satir if r["rejim"] == rj])

print("\n2) F10 (bes durum — daha ince)")
print("-" * 112)
for f in ("BELIRSIZ", "DERIN_AYI", "TEPKI_RALLISI", "BOGA_DUZELTME", "TAM_BOGA"):
    satirla(f, [r for r in satir if r["f10"] == f])

print("\n3) BANT x REJIM (tek tanim; ort H24, N)")
print("-" * 112)
print("   %-8s %16s %16s %16s" % ("bant", "NOTR", "AYI", "BOGA"))
for ad, lo, hi in BANT:
    hu = []
    for rj in ("NOTR", "AYI", "BOGA"):
        v = [r["H24"] for r in satir if r["bant"] == ad and r["rejim"] == rj]
        hu.append("%+8.3f (%5d)" % (sum(v) / len(v), len(v)) if len(v) >= 20 else "-")
    print("   %-8s %16s %16s %16s" % (ad, *hu))

print("\n4) ZAMAN YARILARI — saglamlik")
print("-" * 112)
gunler = sorted(set(r["gun"] for r in satir))
orta = gunler[len(gunler) // 2]
for ad, sec in (("ILK yari  (%s..%s)" % (gunler[0], orta), lambda r: r["gun"] <= orta),
                ("SON yari  (%s..%s)" % (orta, gunler[-1]), lambda r: r["gun"] > orta)):
    satirla(ad, [r for r in satir if sec(r)])

print("\n5) TANIM KIRILMASI ONCESI / SONRASI (2026-07-22)")
print("-" * 112)
kir = datetime.date(2026, 7, 22)
for ad, sec in (("07-22 ONCESI", lambda r: r["gun"] < kir),
                ("07-22 SONRASI", lambda r: r["gun"] >= kir)):
    satirla(ad, [r for r in satir if sec(r)])

print("\n6) GUN-KUMELI t — rejim ici (tek tanim)")
print("-" * 112)
for rj in ("NOTR", "AYI", "BOGA"):
    gh, gl = collections.defaultdict(list), collections.defaultdict(list)
    for r in satir:
        if r["rejim"] != rj:
            continue
        (gh if r["score"] >= 45 else gl)[r["gun"]].append(r["H24"])
    d = [sum(gh[g]) / len(gh[g]) - sum(gl[g]) / len(gl[g])
         for g in sorted(set(gh) & set(gl)) if len(gh[g]) >= 5 and len(gl[g]) >= 10]
    if len(d) >= 2:
        m, sd = sum(d) / len(d), statistics.stdev(d)
        t = m / (sd / math.sqrt(len(d))) if sd else None
        print("   %-6s  fark ort %+7.3f   t = %s   (%d/%d gun pozitif)"
              % (rj, m, "%+.2f" % t if t else "-", sum(1 for x in d if x > 0), len(d)))
    else:
        print("   %-6s  yeterli gun yok (%d)" % (rj, len(d)))

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
