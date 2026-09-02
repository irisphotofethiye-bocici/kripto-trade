#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEFTER3 — gunluk kararlilik · eslesmis cift testi · stop mesafesi · veri kontrolu."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections, datetime as dt, statistics as stt, math


def binom_p(k, n, p0=0.5):
    """IKI YANLI tam binom p-degeri (esit ya da daha uc olasiliklarin toplami)."""
    pm = [math.comb(n, i) * p0 ** i * (1 - p0) ** (n - i) for i in range(n + 1)]
    return min(1.0, sum(x for x in pm if x <= pm[k] * 1.0000001))


def t_bir_ornek(v):
    """tek-orneklem t + normal yaklasimla iki yanli p."""
    n = len(v)
    sd = stt.stdev(v)
    if sd == 0:
        return float("nan"), float("nan")
    t = stt.mean(v) / (sd / math.sqrt(n))
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
    return t, p

T0 = "2026-08-25 16:12:12"


def poz(f):
    K = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    g = {}
    for r in K:
        t = dt.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S") \
            - dt.timedelta(hours=float(r.get("tutma_saat") or 0))
        if r["id"] not in g or t < g[r["id"]]:
            g[r["id"]] = t
    pnl, meta = collections.defaultdict(float), {}
    for r in K:
        if g[r["id"]].strftime("%Y-%m-%d %H:%M:%S") < T0:
            continue
        pnl[r["id"]] += float(r.get("sonuc_usdt") or 0)
        if not r.get("kismi"):
            meta[r["id"]] = dict(r, _gun=g[r["id"]].strftime("%Y-%m-%d"))
    return {i: (pnl[i], meta[i]) for i in meta}


D3, D2 = poz("defter3_islemler.jsonl"), poz("defter2_islemler.jsonl")
L = [(p, m) for p, m in D3.values() if m["yon"] == "LONG"]
S = [(p, m) for p, m in D3.values() if m["yon"] == "SHORT"]

print("=" * 96)
print("1) LONG KOLU GUN GUN — birkac gune mi yasliyor")
print("=" * 96)
g = collections.defaultdict(lambda: [0, 0.0, 0])
for p, m in L:
    g[m["_gun"]][0] += 1
    g[m["_gun"]][1] += p
    g[m["_gun"]][2] += 1 if p > 0 else 0
print("  %-12s %4s %11s %9s" % ("gun", "poz", "P&L", "kazanma"))
for k in sorted(g):
    v = g[k]
    print("  %-12s %4d %+11.2f %8.0f%%" % (k, v[0], v[1], 100 * v[2] / v[0]))
art = sum(1 for v in g.values() if v[1] > 0)
print("  -> %d gunun %d'i ARTI · %d'i EKSI" % (len(g), art, len(g) - art))

print("")
print("=" * 96)
print("2) KAZANMA ORANI — %50'den anlamli olarak dusuk mu (iki yanli binom)")
print("=" * 96)
for ad, X in (("LONG", L), ("SHORT", S)):
    k = sum(1 for p, _ in X if p > 0)
    n = len(X)
    p = binom_p(k, n, 0.5)
    print("  %-6s %2d/%3d = %%%.1f   binom p=%.4f  %s"
          % (ad, k, n, 100 * k / n, p, "ANLAMLI" if p < 0.05 else "anlamsiz"))

print("")
print("=" * 96)
print("3) ESLESMIS CIFT TESTI — ayni sembol+gun, D2 SHORT vs D3 LONG")
print("=" * 96)
s2 = {}
for p, m in D2.values():
    s2.setdefault((m["sym"], m["_gun"]), []).append((p, m))
fark = []
for p3, m3 in L:
    k = (m3["sym"], m3["_gun"])
    if k in s2 and s2[k][0][1]["yon"] == "SHORT":
        fark.append(p3 - s2[k][0][0])
if len(fark) >= 5:
    t, pv = t_bir_ornek(fark)
    arti = sum(1 for x in fark if x > 0)
    isaret_p = binom_p(arti, len(fark), 0.5)
    print("  N=%d cift · ort fark %+.2f · medyan %+.2f" % (len(fark), stt.mean(fark), stt.median(fark)))
    print("  t-testi  t=%+.2f  p=%.4f" % (t, pv))
    print("  ISARET testi       p=%.4f  (dagilimdan bagimsiz)" % isaret_p)
    print("  D3 LONG'un daha iyi oldugu cift: %d/%d" % (sum(1 for x in fark if x > 0), len(fark)))
    print("  ⚠️ BAGIMSIZ DEGIL: ayni sembol birden fazla kez geciyor (CYS, RIVER, JTO...)")
    tk = collections.Counter(m3["sym"] for p3, m3 in L
                             if (m3["sym"], m3["_gun"]) in s2)
    print("     tekil sembol %d · en cok tekrar: %s" % (len(tk), dict(tk.most_common(4))))

print("")
print("=" * 96)
print("4) STOP MESAFESI — LONG'un stopu daha mi genis (mekanik ayrisiyor mu)")
print("=" * 96)
for ad, X in (("LONG", L), ("SHORT", S)):
    r = [abs(float(m["giris"]) - 0) for p, m in X]
    atr = [float(m.get("atr_giriste") or 0) / float(m["giris"]) * 100
           for p, m in X if m.get("atr_giriste")]
    tut = [float(m.get("tutma_saat") or 0) for p, m in X]
    kal = [float(m.get("kaldirac") or 0) for p, m in X]
    mar = [float(m.get("marjin") or 0) for p, m in X]
    print("  %-6s ATR/fiyat medyan %%%.2f · tutma medyan %.1f sa · kaldirac medyan %.0f · marjin medyan %.0f"
          % (ad, stt.median(atr) if atr else 0, stt.median(tut), stt.median(kal), stt.median(mar)))

print("")
print("=" * 96)
print("5) VERI KONTROLU — tuhaf sembol adi")
print("=" * 96)
tuhaf = sorted({m["sym"] for p, m in list(D3.values()) + list(D2.values())
                if any(ord(c) > 127 for c in m["sym"])})
print("  ASCII disi karakter tasiyan sembol:", tuhaf if tuhaf else "YOK")
if tuhaf:
    for s in tuhaf:
        n3 = sum(1 for p, m in D3.values() if m["sym"] == s)
        n2 = sum(1 for p, m in D2.values() if m["sym"] == s)
        v = sum(p for p, m in D3.values() if m["sym"] == s)
        print("     %r  D3 %d poz (%+.2f) · D2 %d poz  <- BINANCE'te BOYLE BIR PERP VAR MI?"
              % (s, n3, v, n2))
