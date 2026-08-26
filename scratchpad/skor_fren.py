#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`skor >= 45` BIR FREN OLARAK DOGRU MU?
On-kayit: ON_KAYIT_skor_fren.md (commit 6bc6daf). Olcutler V1-V5 SABIT.

Yon YALNIZ LONG (fren alim tarafini kapatir).
Mekanik skor_mekanik.py ile AYNI (olcucu.py + testbot.py + config'ten birebir).
Fark: bu olcum TUM skor araligini yukler.
radar_archive.jsonl CONTEXT'E YUKLENMEZ. SALT OKUMA.
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

CFG = json.load(open(os.path.join(PROJE, "kripto-config.json"), encoding="utf-8"))
ESIK, TB, MAL = CFG.get("esikler", {}), CFG.get("testbot", {}), CFG.get("maliyet", {})
NBAR = int(ESIK.get("olcucu_nbar_stop", 10))
ASGARI_STOP = float(TB.get("asgari_stop_pct", 2.0))
KISMI_R = float(ESIK.get("kismi_kar_r", 1.5))
KISMI_PAY = float(ESIK.get("kismi_pay", 0.4))
TR_KAT = float(ESIK.get("trailing_atr_kat", 2.0))
TR_2R = float(ESIK.get("trailing_atr_kat_2r", 1.5))
TR_3R = float(ESIK.get("trailing_atr_kat_3r", 1.0))
ZAMAN_STOP = int(TB.get("zaman_stop_saat", 48))
TAKER = float(MAL.get("taker_fee_pct", 0.045))
SLIP_CFG = float(MAL.get("slippage_pct", 0.02))
SLIP_OLC = 0.0499
YAPI_BAR = 100


def atr_wilder(h, l, c, i, period=14):
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


def seviyeler(h, l, c, i):
    """LONG icin olcucu.measure mantigi."""
    if i - YAPI_BAR + 1 < 1:
        return None
    a = atr_wilder(h, l, c, i)
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
    res = ust[0] if ust else None
    sup = alt[0] if alt else None
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
    if risk <= 0:
        return None
    tp1 = res if (res is not None and res > ref) else ref + 2 * risk
    tp2 = tp1 + 1.5 * risk
    return sl, tp1, tp2, risk, a


def oynat(h, l, c, i, sl, tp1, tp2, risk, a):
    ref = c[i]
    stop, kalan, kar = sl, 1.0, 0.0
    kismi = False
    en_iyi_R = 0.0
    sg = (ref - sl) / ref * 100.0
    for j in range(i + 1, min(i + 1 + ZAMAN_STOP, len(c))):
        if l[j] <= stop:
            kar += kalan * (stop - ref) / ref * 100.0
            return kar, j - i, ("STOP" if not kismi else "STOP_TP1SONRASI"), sg
        if h[j] >= tp2:
            kar += kalan * (tp2 - ref) / ref * 100.0
            return kar, j - i, "TP2", sg
        if not kismi:
            hr = ref + KISMI_R * risk
            if h[j] >= hr:
                kar += KISMI_PAY * (hr - ref) / ref * 100.0
                kalan -= KISMI_PAY
                kismi = True
        en_iyi_R = max(en_iyi_R, (h[j] - ref) / risk)
        kat = TR_KAT if en_iyi_R < 2 else (TR_2R if en_iyi_R < 3 else TR_3R)
        stop = max(stop, h[j] - kat * a)
    j = min(i + ZAMAN_STOP, len(c) - 1)
    kar += kalan * (c[j] - ref) / ref * 100.0
    return kar, j - i, "ZAMAN_STOP", sg


# ---------------------------------------------------------------- arsiv (TUM skor)
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
                             funding=x.get("funding"), gun=t.date())

gerek = collections.defaultdict(list)
for v in gorulen.values():
    gerek[v["sym"]].append(v)

print("`skor >= 45` BIR FREN OLARAK DOGRU MU?  —  yalniz LONG")
print("on-kayit ON_KAYIT_skor_fren.md (6bc6daf) · olcutler SABIT")
print("=" * 118)
print("olay havuzu %d  ·  sembol %d" % (len(gorulen), len(gerek)))

kayit = []
elendi = collections.Counter()
for n, (sym, kayitlar) in enumerate(sorted(gerek.items())):
    p = os.path.join(KL, sym + ".json")
    if not os.path.exists(p):
        continue
    try:
        with open(p, encoding="utf-8") as f:
            b = json.load(f)
    except Exception:
        continue
    idx, c, h, l = {}, [], [], []
    for k, z in enumerate(b):
        t = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(z["t"]))
        idx[t] = k
        c.append(float(z["c"]))
        h.append(float(z["h"]))
        l.append(float(z["l"]))
    for v in kayitlar:
        i0 = idx.get(v["yerel"] + datetime.timedelta(hours=OFSET))
        if i0 is None:
            continue
        i = i0 + 1
        if i < YAPI_BAR + 2 or i + ZAMAN_STOP >= len(c) or c[i] <= 0:
            continue
        sv = seviyeler(h, l, c, i)
        if sv is None:
            continue
        sl, tp1, tp2, risk, a = sv
        bant = ">=45" if v["score"] >= 45 else "<45"
        if (c[i] - sl) / c[i] * 100.0 < ASGARI_STOP:
            elendi[bant] += 1
            continue
        brut, saat, sebep, sg = oynat(h, l, c, i, sl, tp1, tp2, risk, a)
        fr = v["funding"]
        fon = -float(fr) * (saat / 8.0) if fr is not None else 0.0   # LONG: pozitif oran GIDER
        kayit.append(dict(sym=sym, gun=v["gun"], score=v["score"], bant=bant,
                          brut=brut, saat=saat, sebep=sebep, stop_gen=sg, fon=fon,
                          net=brut - 2 * (TAKER + SLIP_CFG) + fon,
                          net_olc=brut - 2 * (TAKER + SLIP_OLC) + fon))
    if (n + 1) % 100 == 0:
        print("   ... %d/%d sembol (islem %d)" % (n + 1, len(gerek), len(kayit)), flush=True)

V = [k for k in kayit if k["bant"] == ">=45"]
K = [k for k in kayit if k["bant"] == "<45"]
print("\nLONG islem %d   (V: skor>=45  N=%d  ·  K: skor<45  N=%d)  ·  gun %d"
      % (len(kayit), len(V), len(K), len(set(k["gun"] for k in kayit))))
print("asgari_stop elemesi:  >=45 %d  ·  <45 %d" % (elendi[">=45"], elendi["<45"]))
tv = elendi[">=45"] + len(V)
tk = elendi["<45"] + len(K)
print("   -> isleme donusen pay:  >=45 %%%.1f  ·  <45 %%%.1f   %s"
      % (100.0 * len(V) / tv if tv else 0, 100.0 * len(K) / tk if tk else 0,
         "(kollari ESIT etkilemiyor)" if tv and tk and
         abs(len(V) / tv - len(K) / tk) > 0.1 else "(yakin)"))


def ozet(ad, w):
    if not w:
        print("   %-16s N=0")
        return
    nt = [k["net"] for k in w]
    print("   %-16s N=%5d  BRUT %+7.3f%%  NET %+7.3f%%  NET(olculen slipaj) %+7.3f%%"
          % (ad, len(w), sum(k["brut"] for k in w) / len(w), sum(nt) / len(nt),
             sum(k["net_olc"] for k in w) / len(w)))
    print("   %-16s fonlama %+6.3f · stop-olma %%%2.0f · stop gen. med %5.2f%% · "
          "medyan tutma %4.1f sa · kazanan %%%2.0f"
          % ("", sum(k["fon"] for k in w) / len(w),
             100.0 * sum(1 for k in w if k["sebep"].startswith("STOP")) / len(w),
             statistics.median([k["stop_gen"] for k in w]),
             statistics.median([k["saat"] for k in w]),
             100.0 * sum(1 for x in nt if x > 0) / len(w)))


print("\n1) IKI KOL")
print("-" * 118)
ozet("V  skor>=45", V)
ozet("K  skor<45", K)


def gun_tek(w, alan="net", nmin=5):
    g = collections.defaultdict(list)
    for k in w:
        g[k["gun"]].append(k[alan])
    d = [sum(v) / len(v) for gg, v in sorted(g.items()) if len(v) >= nmin]
    if len(d) < 2:
        return None, None, 0, len(d)
    m, sd = sum(d) / len(d), statistics.stdev(d)
    return m, (m / (sd / math.sqrt(len(d))) if sd else None), sum(1 for x in d if x > 0), len(d)


def gun_fark(a, b, alan="net", nmin=5):
    ga, gb = collections.defaultdict(list), collections.defaultdict(list)
    for k in a:
        ga[k["gun"]].append(k[alan])
    for k in b:
        gb[k["gun"]].append(k[alan])
    d = [sum(ga[g]) / len(ga[g]) - sum(gb[g]) / len(gb[g])
         for g in sorted(set(ga) & set(gb)) if len(ga[g]) >= nmin and len(gb[g]) >= nmin]
    if len(d) < 2:
        return None, None, 0, len(d)
    m, sd = sum(d) / len(d), statistics.stdev(d)
    return m, (m / (sd / math.sqrt(len(d))) if sd else None), sum(1 for x in d if x < 0), len(d)


print("\nV1 — vetolanacak kume ZARARLI mi (frenin varlik sebebi)")
print("-" * 118)
m1, t1, p1, n1 = gun_tek(V)
vm = sum(k["net"] for k in V) / len(V) if V else 0
print("   V havuzlanmis net %+7.3f%%" % vm)
print("   gun-kumeli  ort %+7.3f   t = %s   (%d/%d gun POZITIF)"
      % (m1 or 0, "%+.2f" % t1 if t1 else "-", p1, n1))
V1 = (vm < 0 and t1 is not None and t1 <= -2.5)
print("   V1 (net<0 VE t<=-2,5): %s" % ("GECTI" if V1 else "DUSTU"))

print("\nV2 — 🔴 AYIRICI: V, K'dan belirgin kotu mu")
print("-" * 118)
km = sum(k["net"] for k in K) / len(K) if K else 0
m2, t2, p2, n2 = gun_fark(V, K)
print("   V %+7.3f%%   K %+7.3f%%   havuzlanmis fark %+7.3f puan" % (vm, km, vm - km))
print("   gun-kumeli  fark ort %+7.3f   t = %s   (%d/%d gun NEGATIF)"
      % (m2 or 0, "%+.2f" % t2 if t2 else "-", p2, n2))
V2 = (m2 is not None and m2 <= -0.3 and t2 is not None and t2 <= -2.5)
print("   V2: %s" % ("GECTI" if V2 else "DUSTU"))

print("\nV3 — isaret tutarliligi")
print("-" * 118)
V3 = (n2 > 0 and p2 / n2 >= 0.60)
print("   %d/%d gun negatif (%%%.0f)  ->  V3: %s"
      % (p2, n2, 100.0 * p2 / n2 if n2 else 0, "GECTI" if V3 else "DUSTU"))

print("\nV4 — zaman yarilari")
print("-" * 118)
gunler = sorted(set(k["gun"] for k in kayit))
orta = gunler[len(gunler) // 2]
isr = []
for ad, sec in (("ILK yari", lambda k: k["gun"] <= orta), ("SON yari", lambda k: k["gun"] > orta)):
    vv = [k for k in V if sec(k)]
    kk = [k for k in K if sec(k)]
    if vv and kk:
        a_ = sum(k["net"] for k in vv) / len(vv)
        b_ = sum(k["net"] for k in kk) / len(kk)
        isr.append(1 if (a_ - b_) > 0 else -1)
        print("   %-10s V N=%4d %+7.3f%%   K N=%5d %+7.3f%%   fark %+7.3f"
              % (ad, len(vv), a_, len(kk), b_, a_ - b_))
V4 = len(isr) == 2 and isr[0] == isr[1]
print("   V4: %s" % ("GECTI" if V4 else "DUSTU"))

print("\nV5 — ZORUNLU SINAMA")
print("-" * 118)
if V and K:
    sv = statistics.median([k["stop_gen"] for k in V])
    sk = statistics.median([k["stop_gen"] for k in K])
    print("   V stop gen. med %5.2f%%  stop-olma %%%2.0f"
          % (sv, 100.0 * sum(1 for k in V if k["sebep"].startswith("STOP")) / len(V)))
    print("   K stop gen. med %5.2f%%  stop-olma %%%2.0f"
          % (sk, 100.0 * sum(1 for k in K if k["sebep"].startswith("STOP")) / len(K)))
    print("   -> oran %.2f kat  %s" % (sv / sk,
         "AYRISIYOR" if (sv / sk > 1.25 or sv / sk < 0.8) else "yakin"))

print("\n2) ESIK TARAMASI — KESIFSEL (en iyi hucre SECILMEZ; plato mu ucurum mu)")
print("-" * 118)
print("   %-8s %7s %10s | %7s %10s | %9s" % ("esik", "V N", "V net", "K N", "K net", "fark"))
for e in (40, 45, 50, 60):
    vv = [k for k in kayit if k["score"] >= e]
    kk = [k for k in kayit if k["score"] < e]
    if len(vv) >= 50:
        print("   >=%-6d %7d %+9.3f%% | %7d %+9.3f%% | %+8.3f"
              % (e, len(vv), sum(k["net"] for k in vv) / len(vv),
                 len(kk), sum(k["net"] for k in kk) / len(kk),
                 sum(k["net"] for k in vv) / len(vv) - sum(k["net"] for k in kk) / len(kk)))

print("\n3) V'NIN TOPLAM LONG ZARARI ICINDEKI PAYI")
print("-" * 118)
tv_ = sum(k["net"] for k in V)
tk_ = sum(k["net"] for k in K)
print("   V toplam %+10.2f puan (islem payi %%%.1f)" % (tv_, 100.0 * len(V) / len(kayit)))
print("   K toplam %+10.2f puan (islem payi %%%.1f)" % (tk_, 100.0 * len(K) / len(kayit)))
print("   TUM LONG toplam %+10.2f puan   ·  V cikarilirsa %+10.2f" % (tv_ + tk_, tk_))
print("   -> islem BASINA: tum %+7.3f%%  ·  V'siz %+7.3f%%"
      % ((tv_ + tk_) / len(kayit), tk_ / len(K) if K else 0))

print("\n4) SKOR BANDI x NET (betimsel)")
print("-" * 118)
for ad, lo, hi in (("<2", -1e9, 2), ("2-5", 2, 5), ("5-10", 5, 10), ("10-20", 10, 20),
                   ("20-30", 20, 30), ("30-45", 30, 45), (">=45", 45, 1e9)):
    w = [k for k in kayit if lo <= k["score"] < hi]
    if len(w) >= 30:
        print("   %-8s N=%5d  net %+7.3f%%  stop-olma %%%2.0f  kazanan %%%2.0f"
              % (ad, len(w), sum(k["net"] for k in w) / len(w),
                 100.0 * sum(1 for k in w if k["sebep"].startswith("STOP")) / len(w),
                 100.0 * sum(1 for k in w if k["net"] > 0) / len(w)))

print("\n" + "=" * 118)
print("HUKUM")
print("=" * 118)
print("   V1 %s · V2 %s · V3 %s · V4 %s"
      % (*("GECTI" if z else "DUSTU" for z in (V1, V2, V3, V4)),))
if V1 and V2 and V3 and V4:
    print("   -> GECTI (fren dogru)")
elif V1 and not V2:
    print("   -> ACIKLAMA (b): botun BUTUN LONG tarafi kaybediyor; skor kapisi OZEL SUCLU DEGIL")
elif not V1:
    print("   -> DUSTU (vetolanacak kume zaten zararli degil)")
else:
    print("   -> ZAYIF")

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
