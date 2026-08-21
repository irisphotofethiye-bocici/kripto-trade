#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASAMA 2 — MEKANIK. ON_KAYIT_mekanik.md'ye BIREBIR uyar.

HAM asamada pos/chg24/last3/rel3 bes pencerede ayni isaret verdi.
Burada AYNI kesitler botun GERCEK mekanigiyle oynatilir.

⚠️ BU TURDA HUKUM YAZILMAZ (kullanici talimati). Yalniz sayi uretilir:
   1) ham -> mekanik gecisinde etkinin kacta kaci kaldigi
   2) isaretin kac pencerede korundugu
   3) stop genisligi / ATR / stop-olma orani AYRISMASI  <- zorunlu sinama

SALT OKUMA.
"""
import os, sys, json, datetime, collections, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
sys.path.insert(0, SCRATCH)
import ileri_rr as ir                                           # noqa: E402
import olcum_ortak as oo                                        # noqa: E402

ADIM = 4
MIN_QV = 125000
ALAN = ["pos", "chg24", "last3", "rel3"]


def ms(s):
    return int(datetime.datetime.strptime(s, "%Y-%m-%d").timestamp() * 1000)


PENCERE = [
    ("ATH-BOLGE 24-09/12", ms("2024-09-15"), ms("2024-12-15")),
    ("ATH-BOLGE 25-06/10", ms("2025-06-01"), ms("2025-10-15")),
    ("TOPARLANMA 25-04/05", ms("2025-04-03"), ms("2025-05-15")),
    ("DERIN-AYI 26-01/03", ms("2026-01-05"), ms("2026-03-20")),
    ("AYI 26-06/08", ms("2026-06-24"), ms("2026-08-19")),
]


def stop_long(b, si, ref, a):
    """SHORT stop_hesapla'nin simetrigi."""
    bas = max(3, si - 100)
    lo = [b[j]["l"] for j in range(bas, si - 2)
          if b[j - 3:j + 4] and b[j]["l"] == min(z["l"] for z in b[j - 3:j + 4])]
    sup = max([x for x in lo if x < ref], default=None)
    ad = []
    if sup is not None and (ref - sup) <= 3 * a:
        ad.append(sup - 0.25 * a)
    nb = min(z["l"] for z in b[max(0, si - ir.STOP_NBAR + 1):si + 1])
    if nb < ref:
        ad.append(nb - 0.25 * a)
    ad.append(ref - 1.5 * a)
    gec = [s for s in ad if s < ref]
    return max(gec) if gec else ref - 1.5 * a


def oynat(b, atrs, si, ft, fr, yon):
    gi = si + 1
    if not atrs[si] or gi >= len(b):
        return None
    ref = b[gi]["o"]
    if ref <= 0:
        return None
    a = atrs[si]
    if yon == "SHORT":
        stop = ir.stop_hesapla(b, si, ref, a)
        sp = (stop - ref) / ref * 100
        hedef = ref * (1 - ir.HEDEF_PCT / 100)
    else:
        stop = stop_long(b, si, ref, a)
        sp = (ref - stop) / ref * 100
        hedef = ref * (1 + ir.HEDEF_PCT / 100)
    if sp <= 0 or sp < ir.ASGARI_STOP:
        return None
    son = min(gi + ir.UFUK, len(b))
    if son - gi < 4:
        return None
    cj, tip, ham = son - 1, "SURE", None
    for j in range(gi, son):
        x = b[j]
        if (x["h"] >= stop) if yon == "SHORT" else (x["l"] <= stop):
            cj, tip, ham = j, "STOP", -sp
            break
        if (x["l"] <= hedef) if yon == "SHORT" else (x["h"] >= hedef):
            cj, tip, ham = j, "HEDEF", ir.HEDEF_PCT
            break
    if ham is None:
        c = b[cj]["c"]
        ham = ((ref - c) if yon == "SHORT" else (c - ref)) / ref * 100
    fon = ir.fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
    if yon == "LONG":
        fon = -fon
    return {"net": ham - oo.MALIYET + fon, "tip": tip, "sp": sp,
            "atr_pct": a / ref * 100, "saat": cj - gi}


def topla():
    with open(os.path.join(ir.KLINE, "BTC.json"), encoding="utf-8") as f:
        btc = {x["t"]: x["c"] for x in json.load(f)}
    kova = {ad: [] for ad, _, _ in PENCERE}
    dosya = sorted(f for f in os.listdir(ir.KLINE) if f.endswith(".json"))
    for n, fn in enumerate(dosya, 1):
        sym = fn[:-5]
        if sym == "BTC":
            continue
        try:
            with open(os.path.join(ir.KLINE, fn), encoding="utf-8") as f:
                b = json.load(f)
        except Exception:
            continue
        if len(b) < ir.ISINMA + ir.UFUK + 20:
            continue
        ft, fr = [], []
        fp = os.path.join(ir.FUND, fn)
        if os.path.exists(fp):
            try:
                with open(fp, encoding="utf-8") as f:
                    fr = json.load(f)
                ft = [x["t"] for x in fr]
            except Exception:
                fr = []
        atrs = ir.atr_serisi(b)
        for i in range(ir.ISINMA, len(b) - ir.UFUK - 2, ADIM):
            x = b[i]
            if (x.get("qv") or 0) < MIN_QV:
                continue
            ad = None
            for a2, t0, t1 in PENCERE:
                if t0 <= x["t"] < t1:
                    ad = a2
                    break
            if ad is None:
                continue
            c24, c3 = b[i - 24]["c"], b[i - 3]["c"]
            if not c24 or not c3 or not x["c"]:
                continue
            pen = b[i - 20:i + 1]
            lo = min(z["l"] for z in pen)
            hi = max(z["h"] for z in pen)
            ref1 = b[i + 1]["o"]
            if ref1 <= 0:
                continue
            r = {"gun": datetime.datetime.fromtimestamp(x["t"] / 1000).strftime("%Y-%m-%d"),
                 "pos": (x["c"] - lo) / (hi - lo) if hi > lo else 0.5,
                 "chg24": (x["c"] - c24) / c24 * 100,
                 "last3": (x["c"] - c3) / c3 * 100,
                 "ham24": (b[i + 24]["c"] - ref1) / ref1 * 100}
            b0, b1 = btc.get(b[i - 3]["t"]), btc.get(x["t"])
            r["rel3"] = r["last3"] - (b1 - b0) / b0 * 100 if (b0 and b1) else None
            for yon in ("SHORT", "LONG"):
                o = oynat(b, atrs, i, ft, fr, yon)
                if o:
                    r["m_" + yon] = o
            kova[ad].append(r)
        if n % 150 == 0:
            print("  ... %d/%d" % (n, len(dosya)))
            sys.stdout.flush()
    return kova


def ceyrek(v, a):
    w = [x for x in v if isinstance(x.get(a), (int, float))]
    if len(w) < 400:
        return None, None
    d = sorted(x[a] for x in w)
    q1, q3 = d[len(d) // 4], d[3 * len(d) // 4]
    if q1 == q3:
        return None, None
    return [x for x in w if x[a] <= q1], [x for x in w if x[a] >= q3]


def gun_farki(alt, ust, f):
    g = collections.defaultdict(lambda: [[], []])
    for x in alt:
        y = f(x)
        if y is not None:
            g[x["gun"]][0].append(y)
    for x in ust:
        y = f(x)
        if y is not None:
            g[x["gun"]][1].append(y)
    gd = [sx.mean(b2) - sx.mean(a2) for a2, b2 in g.values() if len(a2) >= 5 and len(b2) >= 5]
    if len(gd) < 5:
        return None, None, 0
    se = sx.stdev(gd) / len(gd) ** 0.5
    return sx.mean(gd), (sx.mean(gd) / se if se else None), len(gd)


if __name__ == "__main__":
    print("veri kuruluyor (566 sembol x 5 pencere, iki yon)...")
    k = topla()
    print()
    for a in ALAN:
        print("=" * 118)
        print("ALAN: %s   (ust ceyrek eksi alt ceyrek)" % a.upper())
        print("=" * 118)
        print("%-21s %10s %20s %20s %20s"
              % ("pencere", "N", "HAM +24sa", "MEKANIK SHORT", "MEKANIK LONG"))
        print("-" * 96)
        for ad, _, _ in PENCERE:
            alt, ust = ceyrek(k[ad], a)
            if alt is None:
                print("%-21s  yetersiz" % ad)
                continue
            hm, ht, ng = gun_farki(alt, ust, lambda x: x.get("ham24"))
            sm, st, _ = gun_farki(alt, ust, lambda x: (x.get("m_SHORT") or {}).get("net"))
            lm, lt, _ = gun_farki(alt, ust, lambda x: (x.get("m_LONG") or {}).get("net"))
            def g(m, t):
                return "%+7.3f (t%+5.2f)" % (m, t) if (m is not None and t is not None) else "-"
            print("%-21s %10d %20s %20s %20s"
                  % (ad, len(alt) + len(ust), g(hm, ht), g(sm, st), g(lm, lt)))
        # ZORUNLU SINAMA
        print("\n  ZORUNLU SINAMA — mekanik yuku ceyrekler arasi esit mi?")
        print("  %-21s %14s %14s %14s %14s"
              % ("pencere", "stop% ALT", "stop% UST", "stopolma ALT", "stopolma UST"))
        for ad, _, _ in PENCERE:
            alt, ust = ceyrek(k[ad], a)
            if alt is None:
                continue
            def sp(v2):
                z = [x["m_SHORT"]["sp"] for x in v2 if x.get("m_SHORT")]
                return sx.median(z) if z else float("nan")
            def so(v2):
                z = [x["m_SHORT"]["tip"] for x in v2 if x.get("m_SHORT")]
                return 100 * sum(1 for t in z if t == "STOP") / len(z) if z else float("nan")
            print("  %-21s %13.2f%% %13.2f%% %13.1f%% %13.1f%%"
                  % (ad, sp(alt), sp(ust), so(alt), so(ust)))
        print()
    print("BU TURDA HUKUM YAZILMADI — on-kayit geregi yalniz olcum tablosu.")
    print("bot dosyalarina yazim: YOK")
