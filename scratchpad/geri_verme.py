#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GERI VERME — botun kusuru mu, piyasanin ozelligi mi?
On-kayit: ON_KAYIT_geri_verme.md (commit 17cfdec). Olcutler N1-N4 SABIT.

BOS HIPOTEZ: ayni sembolde, ayni donemde (+-3 gun), ayni yonde RASTGELE giris
anlari, BIREBIR AYNI mekanik. Degisen tek sey GIRIS ANI = botun sinyali.

Mekanik stop_mu_sure_mu.py / skor_mekanik.py'den birebir (olcucu.py + config).
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
F = "%Y-%m-%d %H:%M:%S"
OFSET = -3                      # defter ts YEREL (UTC+3) -> UTC
K_KONTROL = 20                  # on-kayit s.2
PENCERE_BAR = 72                # +-3 gun
random.seed(20260830)

CFG = json.load(open(os.path.join(PROJE, "kripto-config.json"), encoding="utf-8"))
ESIK, TB, MAL = CFG.get("esikler", {}), CFG.get("testbot", {}), CFG.get("maliyet", {})
NBAR = int(ESIK.get("olcucu_nbar_stop", 10))
ASGARI_STOP = float(TB.get("asgari_stop_pct", 2.0))
KISMI_R = float(ESIK.get("kismi_kar_r", 1.5))
KISMI_PAY = float(ESIK.get("kismi_pay", 0.4))
TR = (float(ESIK.get("trailing_atr_kat", 2.0)), float(ESIK.get("trailing_atr_kat_2r", 1.5)),
      float(ESIK.get("trailing_atr_kat_3r", 1.0)))
ZAMAN_STOP = int(TB.get("zaman_stop_saat", 48))
MALIYET = 2 * (float(MAL.get("taker_fee_pct", 0.045)) + float(MAL.get("slippage_pct", 0.02)))
YAPI_BAR = 100
ESIKLER = [1, 2, 3, 5]


# ------------------------------------------------------- fiyat kaynagi
_cache = {}


def seri(sym):
    if sym in _cache:
        return _cache[sym]
    out = None
    for p, tag in ((os.path.join(PROJE, "scratchpad", "perp_seri", sym + "_kline.json"), "perp"),
                   (os.path.join(PROJE, "scratchpad", "klines_1h_uzun", sym + ".json"), "uzun")):
        if not os.path.exists(p):
            continue
        try:
            b = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if len(b) < 200:
            continue
        idx, c, h, l = {}, [], [], []
        for k, z in enumerate(b):
            t = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(z["t"]))
            idx[t] = k
            c.append(float(z["c"]))
            h.append(float(z["h"]))
            l.append(float(z["l"]))
        cand = (idx, c, h, l, tag)
        if out is None or tag == "perp":
            out = cand
        if tag == "perp":
            break
    _cache[sym] = out
    return out


# ------------------------------------------------------- mekanik (birebir)
def atr_w(h, l, c, i, period=14):
    a0 = i - YAPI_BAR + 1
    trs = [max(h[k] - l[k], abs(h[k] - c[k - 1]), abs(l[k] - c[k - 1]))
           for k in range(max(1, a0 + 1), i + 1)]
    if not trs:
        return 0.0
    if len(trs) < period:
        return sum(trs) / len(trs)
    a = sum(trs[:period]) / period
    for tr in trs[period:]:
        a = (a * (period - 1) + tr) / period
    return a


def seviyeler(h, l, c, i, yon):
    if i - YAPI_BAR + 1 < 1:
        return None
    a = atr_w(h, l, c, i)
    if a <= 0:
        return None
    ref = c[i]
    a0 = i - YAPI_BAR + 1
    hs, ls = [], []
    for k in range(a0 + 3, i - 2):
        if h[k] == max(h[k - 3:k + 4]):
            hs.append(h[k])
        if l[k] == min(l[k - 3:k + 4]):
            ls.append(l[k])
    ust = sorted([x for x in hs if x > ref])
    alt = sorted([x for x in ls if x < ref], reverse=True)
    res, sup = (ust[0] if ust else None), (alt[0] if alt else None)
    if yon == "LONG":
        ad = []
        if sup is not None and (ref - sup) <= 3 * a:
            ad.append(sup - 0.25 * a)
        nb = min(l[i - NBAR + 1:i + 1])
        if nb < ref:
            ad.append(nb - 0.25 * a)
        ad.append(ref - 1.5 * a)
        ge = [s for s in ad if s < ref]
        sl = max(ge) if ge else ref - 1.5 * a
        risk = ref - sl
        tp1 = res if (res is not None and res > ref) else ref + 2 * risk
        tp2 = tp1 + 1.5 * risk
    else:
        ad = []
        if res is not None and (res - ref) <= 3 * a:
            ad.append(res + 0.25 * a)
        nb = max(h[i - NBAR + 1:i + 1])
        if nb > ref:
            ad.append(nb + 0.25 * a)
        ad.append(ref + 1.5 * a)
        ge = [s for s in ad if s > ref]
        sl = min(ge) if ge else ref + 1.5 * a
        risk = sl - ref
        tp1 = sup if (sup is not None and sup < ref) else ref - 2 * risk
        tp2 = tp1 - 1.5 * risk
    if risk <= 0 or abs(ref - sl) / ref * 100.0 < ASGARI_STOP:
        return None
    return sl, tp1, tp2, risk, a


def oynat(h, l, c, i, yon, sl, tp1, tp2, risk, a):
    """Donus: (net_pct, tepe_pct, saat, stop_gen_pct)"""
    ref = c[i]
    isa = 1.0 if yon == "LONG" else -1.0
    stop, kalan, kar = sl, 1.0, 0.0
    kismi = False
    en_iyi_R = 0.0
    tepe = 0.0
    sg = abs(ref - sl) / ref * 100.0
    for j in range(i + 1, min(i + 1 + ZAMAN_STOP, len(c))):
        uc = h[j] if yon == "LONG" else l[j]
        tepe = max(tepe, isa * (uc - ref) / ref * 100.0)
        vurdu = (l[j] <= stop) if yon == "LONG" else (h[j] >= stop)
        if vurdu:
            kar += kalan * isa * (stop - ref) / ref * 100.0
            return kar - MALIYET, tepe, j - i, sg
        t2 = (h[j] >= tp2) if yon == "LONG" else (l[j] <= tp2)
        if t2:
            kar += kalan * isa * (tp2 - ref) / ref * 100.0
            return kar - MALIYET, tepe, j - i, sg
        if not kismi:
            hr = ref + isa * KISMI_R * risk
            if (h[j] >= hr) if yon == "LONG" else (l[j] <= hr):
                kar += KISMI_PAY * isa * (hr - ref) / ref * 100.0
                kalan -= KISMI_PAY
                kismi = True
        en_iyi_R = max(en_iyi_R, isa * (uc - ref) / risk)
        kat = TR[0] if en_iyi_R < 2 else (TR[1] if en_iyi_R < 3 else TR[2])
        yeni = uc - isa * kat * a
        stop = max(stop, yeni) if yon == "LONG" else min(stop, yeni)
    j = min(i + ZAMAN_STOP, len(c) - 1)
    kar += kalan * isa * (c[j] - ref) / ref * 100.0
    return kar - MALIYET, tepe, j - i, sg


# ------------------------------------------------------- kosum
V = json.load(open(os.path.join(PROJE, "scratchpad", "poz_yol", "kapi_veri.json"),
                   encoding="utf-8"))
print("GERI VERME — botun kusuru mu, piyasanin ozelligi mi?")
print("on-kayit ON_KAYIT_geri_verme.md (17cfdec) · olcutler SABIT")
print("=" * 116)

ger, kon = [], []
kaynak = collections.Counter()
elendi = collections.Counter()
for n, r in enumerate(V):
    s = seri(r["sym"])
    if s is None:
        elendi["kline yok"] += 1
        continue
    idx, c, h, l, tag = s
    try:
        t = datetime.datetime.strptime(r["giris_ts"], F).replace(minute=0, second=0)
    except Exception:
        continue
    i = idx.get(t + datetime.timedelta(hours=OFSET))
    if i is None:
        elendi["bar eslesmedi"] += 1
        continue
    if i < YAPI_BAR + 2 or i + ZAMAN_STOP >= len(c):
        elendi["kenar"] += 1
        continue
    sv = seviyeler(h, l, c, i, r["yon"])
    if sv is None:
        elendi["asgari stop (gercek)"] += 1
        continue
    kaynak[tag] += 1
    net, tepe, saat, sg = oynat(h, l, c, i, r["yon"], *sv)
    ger.append(dict(gun=r["gun"], defter=r["defter"], yon=r["yon"], sym=r["sym"],
                    net=net, tepe=tepe, saat=saat, sg=sg))
    # --- KONTROL: ayni sembol, +-3 gun, ayni yon, rastgele an
    lo, hi = max(YAPI_BAR + 2, i - PENCERE_BAR), min(len(c) - ZAMAN_STOP - 1, i + PENCERE_BAR)
    if hi <= lo:
        continue
    denendi = 0
    alindi = 0
    while alindi < K_KONTROL and denendi < K_KONTROL * 4:
        denendi += 1
        j = random.randint(lo, hi)
        if j == i:
            continue
        sv2 = seviyeler(h, l, c, j, r["yon"])
        if sv2 is None:
            elendi["asgari stop (kontrol)"] += 1
            continue
        n2, t2, s2, g2 = oynat(h, l, c, j, r["yon"], *sv2)
        kon.append(dict(gun=r["gun"], defter=r["defter"], yon=r["yon"], sym=r["sym"],
                        net=n2, tepe=t2, saat=s2, sg=g2))
        alindi += 1
    if (n + 1) % 300 == 0:
        print("   ... %d/%d pozisyon (gercek %d · kontrol %d)" % (n + 1, len(V), len(ger), len(kon)),
              flush=True)

print("\nGERCEK N=%d  ·  KONTROL N=%d  (poz basina ~%.1f)"
      % (len(ger), len(kon), len(kon) / max(1, len(ger))))
print("fiyat kaynagi: %s" % dict(kaynak))
print("elenen: %s" % dict(elendi))


def gv(w, x):
    q = [r for r in w if r["tepe"] >= x]
    return (100.0 * sum(1 for r in q if r["net"] <= 0) / len(q), len(q)) if q else (None, 0)


print("\n1) GERI VERME ORANI — GV(X) = P(son<=0 | tepe>=X%)")
print("-" * 116)
print("  %-8s %10s %8s | %10s %8s | %10s" % ("esik", "GERCEK", "N", "KONTROL", "N", "fark"))
farklar = {}
for x in ESIKLER:
    a, na = gv(ger, x)
    b, nb = gv(kon, x)
    if a is None or b is None:
        continue
    farklar[x] = a - b
    print("  tepe>=%%%-2d %9.1f%% %8d | %9.1f%% %8d | %+9.1f puan" % (x, a, na, b, nb, a - b))


def gun_kumeli(x, nmin=5):
    gg = collections.defaultdict(list)
    gk = collections.defaultdict(list)
    for r in ger:
        if r["tepe"] >= x:
            gg[r["gun"]].append(1.0 if r["net"] <= 0 else 0.0)
    for r in kon:
        if r["tepe"] >= x:
            gk[r["gun"]].append(1.0 if r["net"] <= 0 else 0.0)
    d = [100.0 * (sum(gg[g]) / len(gg[g]) - sum(gk[g]) / len(gk[g]))
         for g in sorted(set(gg) & set(gk)) if len(gg[g]) >= nmin and len(gk[g]) >= nmin]
    if len(d) < 2:
        return None, None, 0, 0
    m, sd = sum(d) / len(d), statistics.stdev(d)
    return m, (m / (sd / math.sqrt(len(d))) if sd else None), sum(1 for z in d if z > 0), len(d)


print("\nN1 — BIRINCIL: fark(2%) >= +5,0 puan VE gun-kumeli t >= +2,5")
print("-" * 116)
m2, t2_, p2, n2_ = gun_kumeli(2)
print("   havuzlanmis fark(2%%) %+.1f puan" % farklar.get(2, 0))
print("   gun-kumeli  ort %+.2f puan  ·  t = %s  ·  %d/%d gun pozitif"
      % (m2 or 0, ("%+.2f" % t2_) if t2_ else "-", p2, n2_))
N1 = (farklar.get(2, -99) >= 5.0 and t2_ is not None and t2_ >= 2.5)
print("   N1: %s" % ("GECTI" if N1 else "DUSTU"))

print("\nN2 — GRADYAN: fark(1) >= fark(2) >= fark(3) VE |fark(5)| <= 5")
print("-" * 116)
f1, f2, f3, f5 = (farklar.get(k) for k in (1, 2, 3, 5))
print("   fark: %s" % "  ".join("%d%%: %+.1f" % (k, farklar[k]) for k in ESIKLER if k in farklar))
N2 = (None not in (f1, f2, f3, f5) and f1 >= f2 >= f3 and abs(f5) <= 5)
print("   N2: %s" % ("GECTI" if N2 else "DUSTU"))

print("\nN3 — YON TUTARLILIGI (LONG ve SHORT ayri)")
print("-" * 116)
isr = []
for yon in ("LONG", "SHORT"):
    g2 = [r for r in ger if r["yon"] == yon]
    k2 = [r for r in kon if r["yon"] == yon]
    a, na = gv(g2, 2)
    b, nb = gv(k2, 2)
    if a is None or b is None or na < 20:
        print("   %-6s N yetersiz" % yon)
        continue
    isr.append(1 if a - b > 0 else -1)
    print("   %-6s GERCEK %5.1f%% (N=%3d) | KONTROL %5.1f%% (N=%4d) | fark %+.1f puan"
          % (yon, a, na, b, nb, a - b))
N3 = len(isr) == 2 and isr[0] == isr[1]
print("   N3: %s" % ("GECTI" if N3 else "DUSTU"))

print("\nN4 — SURE ve MEKANIK ESITLIGI")
print("-" * 116)
sg_g = statistics.median([r["saat"] for r in ger])
sg_k = statistics.median([r["saat"] for r in kon])
st_g = statistics.median([r["sg"] for r in ger])
st_k = statistics.median([r["sg"] for r in kon])
print("   medyan tutma  GERCEK %5.1f sa · KONTROL %5.1f sa  ->  oran %.2f  %s"
      % (sg_g, sg_k, sg_g / sg_k if sg_k else 0,
         "(1,5 kat icinde)" if 0.67 <= (sg_g / sg_k if sg_k else 0) <= 1.5 else "🔴 AYRISIYOR"))
print("   medyan stop   GERCEK %5.2f%% · KONTROL %5.2f%%  ->  oran %.2f"
      % (st_g, st_k, st_g / st_k if st_k else 0))
print("   tepe medyani  GERCEK %+6.2f%% · KONTROL %+6.2f%%" %
      (statistics.median([r["tepe"] for r in ger]), statistics.median([r["tepe"] for r in kon])))
print("   net medyani   GERCEK %+6.2f%% · KONTROL %+6.2f%%" %
      (statistics.median([r["net"] for r in ger]), statistics.median([r["net"] for r in kon])))
N4 = 0.67 <= (sg_g / sg_k if sg_k else 0) <= 1.5

print("\n" + "=" * 116)
print("HUKUM")
print("=" * 116)
print("   N1 %s · N2 %s · N3 %s · N4 %s"
      % (*("GECTI" if z else "DUSTU" for z in (N1, N2, N3, N4)),))
if N1 and N2:
    print("   -> GECTI  (aday; kural DEGIL — kendi mekanik+portfoy olcumunu hak eder)")
elif N1:
    print("   -> ZAYIF (N2 dustu)")
else:
    print("   -> DUSTU: 'geri verme' botun kusuru DEGIL — esitlenmis rastgele girisle ayni")
print("\nbot dosyalarina yazim: YOK")
