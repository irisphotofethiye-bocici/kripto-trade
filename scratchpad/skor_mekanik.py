#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SKORUN TERS KENARI BOTUN MEKANIGIYLE HAYATTA KALIYOR MU? — ASAMA 2.
On-kayit: ON_KAYIT_skor_mekanik.md (commit d7b607d). Olcutler M1-M5 SABIT.

Mekanik olcucu.py + testbot.py + kripto-config.json'dan BIREBIR yeniden uretildi.
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
ESIK = CFG.get("esikler", {})
TB = CFG.get("testbot", {})
MAL = CFG.get("maliyet", {})
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
SLIP_OLC = 0.0499                      # olcumler.md: gercek medyan slipaj
YAPI_BAR = 100                         # testbot.py:1132 -> olcucu.measure(...,"1h",100)


def atr_wilder(h, l, c, i, period=14):
    """Kapanmis barlar [i-YAPI_BAR+1 .. i] uzerinde Wilder ATR."""
    a0 = i - YAPI_BAR + 1
    trs = []
    for k in range(max(1, a0 + 1), i + 1):
        trs.append(max(h[k] - l[k], abs(h[k] - c[k - 1]), abs(l[k] - c[k - 1])))
    if not trs:
        return 0.0
    if len(trs) < period:
        return sum(trs) / len(trs)
    a = sum(trs[:period]) / period
    for tr in trs[period:]:
        a = (a * (period - 1) + tr) / period
    return a


def swings(h, l, i, left=3, right=3):
    a0 = i - YAPI_BAR + 1
    hs, ls = [], []
    for k in range(a0 + left, i - right + 1):
        if h[k] == max(h[k - left:k + right + 1]):
            hs.append(h[k])
        if l[k] == min(l[k - left:k + right + 1]):
            ls.append(l[k])
    return hs, ls


def seviyeler(h, l, c, i, yon):
    """olcucu.measure'in stop/TP mantigi. Donus: (sl, tp1, tp2, risk, atr) veya None."""
    if i - YAPI_BAR + 1 < 1:
        return None
    a = atr_wilder(h, l, c, i)
    if a <= 0:
        return None
    ref = c[i]
    hs, ls = swings(h, l, i)
    ust = sorted([x for x in hs if x > ref])
    alt = sorted([x for x in ls if x < ref], reverse=True)
    res = ust[0] if ust else None
    sup = alt[0] if alt else None
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
    """Botun pozisyon yonetimi. Donus: (brut_pct, saat, sebep, stop_gen_pct)"""
    ref = c[i]
    isaret = 1.0 if yon == "LONG" else -1.0
    stop = sl
    kalan = 1.0
    kar = 0.0                        # realize edilmis brut (notional orani, %)
    kismi_alindi = False
    en_iyi_R = 0.0
    stop_gen = abs(ref - sl) / ref * 100.0
    for j in range(i + 1, min(i + 1 + ZAMAN_STOP, len(c))):
        # --- once STOP (bar-ici sira belirsiz -> muhafazakar)
        vurdu = (l[j] <= stop) if yon == "LONG" else (h[j] >= stop)
        if vurdu:
            kar += kalan * isaret * (stop - ref) / ref * 100.0
            return kar, j - i, ("STOP" if not kismi_alindi else "STOP_TP1SONRASI"), stop_gen
        # --- TP2 (tam cikis)
        t2 = (h[j] >= tp2) if yon == "LONG" else (l[j] <= tp2)
        if t2:
            kar += kalan * isaret * (tp2 - ref) / ref * 100.0
            return kar, j - i, "TP2", stop_gen
        # --- kismi kar (1,5R)
        if not kismi_alindi:
            hedef_r = ref + isaret * KISMI_R * risk
            ul = (h[j] >= hedef_r) if yon == "LONG" else (l[j] <= hedef_r)
            if ul:
                kar += KISMI_PAY * isaret * (hedef_r - ref) / ref * 100.0
                kalan -= KISMI_PAY
                kismi_alindi = True
        # --- iz-suren stop (R'ye gore siki)
        uc = h[j] if yon == "LONG" else l[j]
        R = isaret * (uc - ref) / risk
        en_iyi_R = max(en_iyi_R, R)
        kat = TR_KAT if en_iyi_R < 2 else (TR_2R if en_iyi_R < 3 else TR_3R)
        yeni = uc - isaret * kat * a
        if yon == "LONG":
            stop = max(stop, yeni)
        else:
            stop = min(stop, yeni)
    j = min(i + ZAMAN_STOP, len(c) - 1)
    kar += kalan * isaret * (c[j] - ref) / ref * 100.0
    return kar, j - i, "ZAMAN_STOP", stop_gen


# ------------------------------------------------------------------ arsiv
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
    if v["score"] >= 45 or v["score"] < 5:
        gerek[v["sym"]].append(v)

print("SKORUN TERS KENARI MEKANIKLE HAYATTA KALIYOR MU? — ASAMA 2")
print("on-kayit ON_KAYIT_skor_mekanik.md (d7b607d) · olcutler SABIT")
print("=" * 118)
print("mekanik: nbar=%d · asgari_stop=%.1f%% · kismi %.0f%%@%.1fR · iz-suren %.1f/%.1f/%.1f ATR"
      " · zaman_stop=%ds · taker %.3f%%" % (NBAR, ASGARI_STOP, KISMI_PAY * 100, KISMI_R,
                                            TR_KAT, TR_2R, TR_3R, ZAMAN_STOP, TAKER))

kayit = []
elendi_stop, elendi_veri = 0, 0
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
        i = i0 + 1                                  # GIRIS = bir sonraki saatin kapanisi
        if i < YAPI_BAR + 2 or i + ZAMAN_STOP >= len(c) or c[i] <= 0:
            elendi_veri += 1
            continue
        for yon in ("SHORT", "LONG"):
            sv = seviyeler(h, l, c, i, yon)
            if sv is None:
                elendi_veri += 1
                continue
            sl, tp1, tp2, risk, a = sv
            if abs(c[i] - sl) / c[i] * 100.0 < ASGARI_STOP:
                if yon == "SHORT":
                    elendi_stop += 1
                continue
            brut, saat, sebep, sg = oynat(h, l, c, i, yon, sl, tp1, tp2, risk, a)
            fr = v["funding"]
            fon = 0.0
            if fr is not None:
                # oran %/8s · SHORT'ta pozitif oran GELIR · LONG'ta gider
                fon = (1.0 if yon == "SHORT" else -1.0) * float(fr) * (saat / 8.0)
            kayit.append(dict(sym=sym, gun=v["gun"], score=v["score"], yon=yon,
                              brut=brut, saat=saat, sebep=sebep, stop_gen=sg,
                              fon=fon,
                              net_cfg=brut - 2 * (TAKER + SLIP_CFG) + fon,
                              net_olc=brut - 2 * (TAKER + SLIP_OLC) + fon,
                              bant=">=45" if v["score"] >= 45 else "<5"))
    if (n + 1) % 100 == 0:
        print("   ... %d/%d sembol (islem %d)" % (n + 1, len(gerek), len(kayit)), flush=True)

print("\nislem %d  ·  asgari-stop elemesi (SHORT) %d  ·  veri elemesi %d  ·  gun %d"
      % (len(kayit), elendi_stop, elendi_veri, len(set(k["gun"] for k in kayit))))


def kol(yon, bant):
    return [k for k in kayit if k["yon"] == yon and k["bant"] == bant]


def ozet(ad, w):
    if not w:
        print("   %-22s N=0" % ad)
        return
    br = [k["brut"] for k in w]
    nc = [k["net_cfg"] for k in w]
    no = [k["net_olc"] for k in w]
    fo = [k["fon"] for k in w]
    st = sum(1 for k in w if k["sebep"].startswith("STOP"))
    print("   %-22s N=%5d  BRUT %+7.3f%%  NET(cfg) %+7.3f%%  NET(olculen slipaj) %+7.3f%%"
          % (ad, len(w), sum(br) / len(br), sum(nc) / len(nc), sum(no) / len(no)))
    print("   %-22s fonlama %+6.3f  ·  stop-olma %%%2.0f  ·  stop genisligi med %5.2f%%"
          "  ·  medyan tutma %4.1f sa  ·  kazanan %%%2.0f"
          % ("", sum(fo) / len(fo), 100.0 * st / len(w),
             statistics.median([k["stop_gen"] for k in w]),
             statistics.median([k["saat"] for k in w]),
             100.0 * sum(1 for x in nc if x > 0) / len(w)))


print("\n1) DORT KOL")
print("-" * 118)
A, B = kol("SHORT", ">=45"), kol("SHORT", "<5")
C, D = kol("LONG", ">=45"), kol("LONG", "<5")
ozet("A  SHORT skor>=45", A)
ozet("B  SHORT skor<5", B)
ozet("C  LONG  skor>=45  (BOT)", C)
ozet("D  LONG  skor<5", D)


def gun_t(a, b, alan="net_cfg", nmin=5):
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
    return m, (m / (sd / math.sqrt(len(d))) if sd else None), sum(1 for x in d if x > 0), len(d)


print("\nM1 — A'nin net ortalamasi > 0 mi (maliyet + fonlama sonrasi)")
print("-" * 118)
a_cfg = sum(k["net_cfg"] for k in A) / len(A) if A else 0
a_olc = sum(k["net_olc"] for k in A) / len(A) if A else 0
print("   A net (cfg slipaj)      %+7.3f%%" % a_cfg)
print("   A net (olculen slipaj)  %+7.3f%%" % a_olc)
M1 = a_cfg > 0 and a_olc > 0
print("   M1: %s" % ("GECTI" if M1 else "DUSTU"))

print("\nM2 — A - B  (BIRINCIL)")
print("-" * 118)
m2, t2, p2, n2 = gun_t(A, B)
print("   havuzlanmis fark %+7.3f puan" % (a_cfg - (sum(k["net_cfg"] for k in B) / len(B) if B else 0)))
print("   gun-kumeli  fark ort %+7.3f   t = %s   (%d/%d gun pozitif)"
      % (m2 or 0, "%+.2f" % t2 if t2 else "-", p2, n2))
M2 = (m2 is not None and m2 >= 0.3 and t2 is not None and t2 >= 2.5)
print("   M2: %s" % ("GECTI" if M2 else "DUSTU"))

print("\nM3 — isaret tutarliligi")
print("-" * 118)
M3 = (n2 > 0 and p2 / n2 >= 0.60)
print("   %d/%d gun (%%%.0f)  ->  M3: %s" % (p2, n2, 100.0 * p2 / n2 if n2 else 0,
                                             "GECTI" if M3 else "DUSTU"))

print("\nM4 — zaman yarilari")
print("-" * 118)
gunler = sorted(set(k["gun"] for k in kayit))
orta = gunler[len(gunler) // 2]
isaretler = []
for ad, sec in (("ILK yari", lambda k: k["gun"] <= orta), ("SON yari", lambda k: k["gun"] > orta)):
    aa = [k for k in A if sec(k)]
    bb = [k for k in B if sec(k)]
    if aa and bb:
        f = sum(k["net_cfg"] for k in aa) / len(aa) - sum(k["net_cfg"] for k in bb) / len(bb)
        isaretler.append(1 if f > 0 else -1)
        print("   %-10s A N=%4d %+7.3f%%   B N=%5d %+7.3f%%   fark %+7.3f"
              % (ad, len(aa), sum(k["net_cfg"] for k in aa) / len(aa),
                 len(bb), sum(k["net_cfg"] for k in bb) / len(bb), f))
M4 = len(isaretler) == 2 and isaretler[0] == isaretler[1]
print("   M4: %s" % ("GECTI" if M4 else "DUSTU"))

print("\nM5 — ZORUNLU SINAMA: stop genisligi ve stop-olma orani esit mi")
print("-" * 118)
for ad, w in (("A SHORT>=45", A), ("B SHORT<5", B), ("C LONG>=45", C), ("D LONG<5", D)):
    if w:
        print("   %-14s stop genisligi med %5.2f%%   stop-olma %%%2.0f   ATR-tabanli"
              % (ad, statistics.median([k["stop_gen"] for k in w]),
                 100.0 * sum(1 for k in w if k["sebep"].startswith("STOP")) / len(w)))
if A and B:
    o = statistics.median([k["stop_gen"] for k in A]) / statistics.median([k["stop_gen"] for k in B])
    print("   -> A/B stop genisligi orani %.2f kat  %s"
          % (o, "AYRISIYOR -> guven HAM asamadan okunur" if (o > 1.25 or o < 0.8) else "yakin"))

print("\n2) KAPANIS SEBEBI DAGILIMI")
print("-" * 118)
for ad, w in (("A SHORT>=45", A), ("B SHORT<5", B), ("C LONG>=45", C)):
    if not w:
        continue
    print("   %s" % ad)
    for s_, n_ in collections.Counter(k["sebep"] for k in w).most_common():
        v = [k["net_cfg"] for k in w if k["sebep"] == s_]
        print("      %-18s %5d (%%%2.0f)   net ort %+7.3f%%"
              % (s_, n_, 100.0 * n_ / len(w), sum(v) / len(v)))

print("\n3) FONLAMANIN PAYI")
print("-" * 118)
for ad, w in (("A SHORT>=45", A), ("C LONG>=45", C)):
    if w:
        br = sum(k["brut"] for k in w) / len(w)
        fo = sum(k["fon"] for k in w) / len(w)
        print("   %-14s brut %+7.3f%%  fonlama %+6.3f  maliyet %-6.3f  ->  net %+7.3f%%"
              % (ad, br, fo, -2 * (TAKER + SLIP_CFG), br + fo - 2 * (TAKER + SLIP_CFG)))

print("\n4) C KOLU — botun BUGUNKU davranisi (rapor)")
print("-" * 118)
if C and D:
    mc, tc, pc, nc_ = gun_t(C, D)
    print("   LONG>=45 - LONG<5   ort %+7.3f   t = %s   (%d/%d gun)"
          % (mc or 0, "%+.2f" % tc if tc else "-", pc, nc_))
    print("   LONG>=45 net %+7.3f%%   SHORT>=45 net %+7.3f%%   ->  ayni olayda ters yon farki %+7.3f"
          % (sum(k["net_cfg"] for k in C) / len(C), a_cfg,
             a_cfg - sum(k["net_cfg"] for k in C) / len(C)))

print("\n" + "=" * 118)
print("HUKUM")
print("=" * 118)
print("   M1 %s · M2 %s · M3 %s · M4 %s"
      % (*("GECTI" if z else "DUSTU" for z in (M1, M2, M3, M4)),))
if M1 and M2 and M3 and M4:
    print("   -> GECTI")
elif M1 and M2:
    print("   -> ZAYIF")
else:
    print("   -> DUSTU")

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
