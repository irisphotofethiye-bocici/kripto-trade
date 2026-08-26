#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KENARI STOP MU YIYOR, SURE MI?
On-kayit: ON_KAYIT_stop_mu_sure_mu.md (commit 1505a48). Olcutler D1-D4 SABIT.

AYIRMA:
  D_stop = net(mekanikli) - net(stopsuz, AYNI sure)   -> sure ETKISI SIFIR, saf stop
  S_H    = net(stopsuz, sabit H saat)                 -> stop ETKISI SIFIR, saf sure

Stopsuz kol GERCEK strateji DEGIL (likidasyon modellenmiyor) — teshis araci.
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
MALIYET = 2 * (TAKER + SLIP_CFG)
MALIYET_OLC = 2 * (TAKER + SLIP_OLC)
YAPI_BAR = 100
UFUKLAR = [1, 2, 4, 6, 12, 24, 48]


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


def seviyeler(h, l, c, i, yon):
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
    if risk <= 0:
        return None
    return sl, tp1, tp2, risk, a


def oynat(h, l, c, i, yon, sl, tp1, tp2, risk, a):
    ref = c[i]
    isaret = 1.0 if yon == "LONG" else -1.0
    stop, kalan, kar = sl, 1.0, 0.0
    kismi = False
    en_iyi_R = 0.0
    for j in range(i + 1, min(i + 1 + ZAMAN_STOP, len(c))):
        vurdu = (l[j] <= stop) if yon == "LONG" else (h[j] >= stop)
        if vurdu:
            kar += kalan * isaret * (stop - ref) / ref * 100.0
            return kar, j - i, ("STOP" if not kismi else "STOP_TP1SONRASI")
        t2 = (h[j] >= tp2) if yon == "LONG" else (l[j] <= tp2)
        if t2:
            kar += kalan * isaret * (tp2 - ref) / ref * 100.0
            return kar, j - i, "TP2"
        if not kismi:
            hr = ref + isaret * KISMI_R * risk
            ul = (h[j] >= hr) if yon == "LONG" else (l[j] <= hr)
            if ul:
                kar += KISMI_PAY * isaret * (hr - ref) / ref * 100.0
                kalan -= KISMI_PAY
                kismi = True
        uc = h[j] if yon == "LONG" else l[j]
        en_iyi_R = max(en_iyi_R, isaret * (uc - ref) / risk)
        kat = TR_KAT if en_iyi_R < 2 else (TR_2R if en_iyi_R < 3 else TR_3R)
        yeni = uc - isaret * kat * a
        stop = max(stop, yeni) if yon == "LONG" else min(stop, yeni)
    j = min(i + ZAMAN_STOP, len(c) - 1)
    kar += kalan * isaret * (c[j] - ref) / ref * 100.0
    return kar, j - i, "ZAMAN_STOP"


# ---------------------------------------------------------------- arsiv
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

print("KENARI STOP MU YIYOR, SURE MI?")
print("on-kayit ON_KAYIT_stop_mu_sure_mu.md (1505a48) · olcutler SABIT")
print("=" * 118)

kayit = {"LONG": [], "SHORT": []}
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
        fr = v["funding"]
        for yon in ("LONG", "SHORT"):
            sv = seviyeler(h, l, c, i, yon)
            if sv is None:
                continue
            sl, tp1, tp2, risk, a = sv
            if abs(c[i] - sl) / c[i] * 100.0 < ASGARI_STOP:
                continue
            isaret = 1.0 if yon == "LONG" else -1.0
            brut_m, hold, sebep = oynat(h, l, c, i, yon, sl, tp1, tp2, risk, a)

            def fon(saat):
                return ((1.0 if yon == "SHORT" else -1.0) * float(fr) * (saat / 8.0)
                        if fr is not None else 0.0)

            # STOPSUZ, AYNI sure (eslesmis)
            j = min(i + hold, len(c) - 1)
            brut_s = isaret * (c[j] - c[i]) / c[i] * 100.0
            net_m = brut_m - MALIYET + fon(hold)
            net_s = brut_s - MALIYET + fon(hold)
            # STOPSUZ, sabit ufuklar
            sh = {}
            for H in UFUKLAR:
                jj = i + H
                if jj < len(c):
                    sh[H] = (isaret * (c[jj] - c[i]) / c[i] * 100.0) - MALIYET + fon(H)
            kayit[yon].append(dict(sym=sym, gun=v["gun"], score=v["score"], hold=hold,
                                   sebep=sebep, net_m=net_m, net_s=net_s,
                                   d_stop=net_m - net_s,
                                   net_m_olc=brut_m - MALIYET_OLC + fon(hold),
                                   fon_h=fon(hold), sh=sh))
    if (n + 1) % 100 == 0:
        print("   ... %d/%d sembol (LONG %d)" % (n + 1, len(gerek), len(kayit["LONG"])),
              flush=True)


def gun_tek(w, alan, nmin=5):
    g = collections.defaultdict(list)
    for k in w:
        g[k["gun"]].append(k[alan] if not callable(alan) else alan(k))
    d = [sum(v) / len(v) for gg, v in sorted(g.items()) if len(v) >= nmin]
    if len(d) < 2:
        return None, None, 0, len(d)
    m, sd = sum(d) / len(d), statistics.stdev(d)
    return m, (m / (sd / math.sqrt(len(d))) if sd else None), sum(1 for x in d if x < 0), len(d)


for yon in ("LONG", "SHORT"):
    W = kayit[yon]
    ana = (yon == "LONG")
    print("\n" + "=" * 118)
    print("%s  —  N=%d islem · %d gun" % ("BIRINCIL: LONG" if ana else
                                          "IKINCIL (onceden ilan edilmis): SHORT",
                                          len(W), len(set(k["gun"] for k in W))))
    print("=" * 118)
    if not W:
        continue
    nm = sum(k["net_m"] for k in W) / len(W)
    ns = sum(k["net_s"] for k in W) / len(W)
    ds = sum(k["d_stop"] for k in W) / len(W)
    print("\n0) UC RAKAM")
    print("-" * 118)
    print("   mekanikli (botun kendisi)          net %+7.3f%%   medyan tutma %4.1f sa"
          % (nm, statistics.median([k["hold"] for k in W])))
    print("   STOPSUZ, AYNI sure (eslesmis)      net %+7.3f%%" % ns)
    print("   ------------------------------------------------------")
    print("   D_stop = mekanikli - stopsuz       %+7.3f puan" % ds)

    print("\nD1 — stop, ESLESMIS surede kenari yiyor mu   %s"
          % ("[BIRINCIL]" if ana else "[ikincil, olcut UYGULANMAZ]"))
    print("-" * 118)
    m1, t1, p1, n1 = gun_tek(W, "d_stop")
    print("   gun-kumeli  D_stop ort %+7.3f   t = %s   (%d/%d gun NEGATIF)"
          % (m1 or 0, "%+.2f" % t1 if t1 else "-", p1, n1))
    D1 = (ds < 0 and t1 is not None and t1 <= -2.5)
    if ana:
        print("   D1: %s" % ("GECTI" if D1 else "DUSTU"))

    print("\nD2 — zaman yarilari")
    print("-" * 118)
    gunler = sorted(set(k["gun"] for k in W))
    orta = gunler[len(gunler) // 2]
    isr = []
    for ad, sec in (("ILK yari", lambda k: k["gun"] <= orta),
                    ("SON yari", lambda k: k["gun"] > orta)):
        v = [k for k in W if sec(k)]
        if v:
            d_ = sum(k["d_stop"] for k in v) / len(v)
            isr.append(1 if d_ > 0 else -1)
            print("   %-10s N=%6d   mekanikli %+7.3f%%   stopsuz(esl.) %+7.3f%%   D_stop %+7.3f"
                  % (ad, len(v), sum(k["net_m"] for k in v) / len(v),
                     sum(k["net_s"] for k in v) / len(v), d_))
    D2 = len(isr) == 2 and isr[0] == isr[1]
    if ana:
        print("   D2: %s" % ("GECTI" if D2 else "DUSTU"))

    print("\nD3 — SAF SURE EGRISI  (stopsuz, sabit ufuk; stop etkisi SIFIR)")
    print("-" * 118)
    print("   %-6s %8s %11s %11s %11s   %s" % ("H saat", "N", "net", "brut", "fonlama", "isaret"))
    egri = {}
    for H in UFUKLAR:
        v = [k["sh"][H] for k in W if H in k["sh"]]
        f = [(-1.0 if yon == "LONG" else 1.0) * 0 for k in W]  # placeholder
        if not v:
            continue
        fo = [k["fon_h"] * (H / k["hold"]) if k["hold"] else 0 for k in W if H in k["sh"]]
        egri[H] = sum(v) / len(v)
        print("   %-6d %8d %+10.3f%% %+10.3f%% %+10.3f    %s"
              % (H, len(v), egri[H], egri[H] + MALIYET - (sum(fo) / len(fo)),
                 sum(fo) / len(fo), "POZITIF" if egri[H] > 0 else "negatif"))
    poz = [H for H, x in egri.items() if x > 0]
    print("   -> net POZITIF ufuk: %s" % (", ".join("%ds" % x for x in poz) if poz else "YOK"))

    print("\nD4 — hangi faktor baskin")
    print("-" * 118)
    if egri:
        yay = max(egri.values()) - min(egri.values())
        print("   |D_stop|                 %7.3f puan" % abs(ds))
        print("   sure egrisinin yayilimi  %7.3f puan   (%ds -> %ds)"
              % (yay, min(egri, key=lambda z: egri[z]), max(egri, key=lambda z: egri[z])))
        print("   -> BASKIN: %s" % ("STOP" if abs(ds) > yay else "SURE"))

    if not ana:
        continue

    print("\n5) D_stop KAPANIS SEBEBINE GORE  (stop nerede yiyor)")
    print("-" * 118)
    for s_, n_ in collections.Counter(k["sebep"] for k in W).most_common():
        v = [k for k in W if k["sebep"] == s_]
        print("   %-18s N=%5d (%%%2.0f)  mekanikli %+7.3f%%  stopsuz(esl.) %+7.3f%%  D_stop %+7.3f"
              % (s_, n_, 100.0 * n_ / len(W), sum(k["net_m"] for k in v) / len(v),
                 sum(k["net_s"] for k in v) / len(v),
                 sum(k["d_stop"] for k in v) / len(v)))

    print("\n6) D_stop SKOR BANDINA GORE")
    print("-" * 118)
    for ad, lo, hi in (("<5", -1e9, 5), ("5-20", 5, 20), ("20-45", 20, 45), (">=45", 45, 1e9)):
        v = [k for k in W if lo <= k["score"] < hi]
        if len(v) >= 30:
            print("   %-8s N=%5d  mekanikli %+7.3f%%  stopsuz(esl.) %+7.3f%%  D_stop %+7.3f"
                  % (ad, len(v), sum(k["net_m"] for k in v) / len(v),
                     sum(k["net_s"] for k in v) / len(v), sum(k["d_stop"] for k in v) / len(v)))

    print("\n7) TUTMA SURESI DAGILIMI (mekanik)")
    print("-" * 118)
    hs = sorted(k["hold"] for k in W)
    for q in (10, 25, 50, 75, 90):
        print("   %%%-3d  %3d saat" % (q, hs[int(q / 100 * len(hs))]))

    print("\n" + "=" * 118)
    print("HUKUM (LONG)")
    print("=" * 118)
    print("   D1 %s · D2 %s" % ("GECTI" if D1 else "DUSTU", "GECTI" if D2 else "DUSTU"))
    if D1 and not poz:
        print("   -> STOP YIYOR, ama sure uzatmak da KURTARMIYOR")
    elif D1 and poz:
        print("   -> STOP YIYOR; stopsuz + belirli ufuklarda kenar VAR (%s)"
              % ", ".join("%ds" % x for x in poz))
    else:
        print("   -> D1 DUSTU: stop suclu degil; teshis sureye ya da GIRISIN KENDISINE kayar")
    print("   NOT: stopsuz kol GERCEK strateji DEGIL (likidasyon modellenmiyor) — teshis araci.")

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
