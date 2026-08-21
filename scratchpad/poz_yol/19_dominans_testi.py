#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""USDT.D / TOTAL / BTC.D — kullanicinin onerdigi rejim gostergeleri, SINANIYOR.

Veri: scratchpad/gecko/ (CoinGecko, top 100 coin, gunluk mcap, 365 gun)
      TOTAL = top100 mcap TOPLAMI (kripto mcap'inin ~%95'i — YAKLASIKLIK)

Ayni tespit-kalitesi olcutu (17_etiket_kalitesi.py):
   gercek "yukselis gunu" = BTC'nin sonraki 7 gunluk getirisi >= +%3
   olculen: kesinlik · kapsama · gecikme · kacirilan   (SAYIM, getiri DEGIL)

⚠️ PENCERE 365 GUN — 2 yillik testlerden KISA. Ama tam bir cevrim iceriyor:
   2025-08..10 ATH bolgesi · 2025-11..2026-06 derin ayi · 2026-07.. toparlanma

SALT OKUMA.
"""
import os, json, collections, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
GECKO = os.path.join(os.path.dirname(HERE), "gecko")
ILERI_GUN, ILERI_ESIK = 7, 3.0


def seri():
    """gun -> {total, usdt_d, btc_d, eth_d, stable_d}"""
    dosya = [f for f in os.listdir(GECKO) if f.endswith(".json") and not f.startswith("_")]
    mc = {}
    for f in dosya:
        try:
            with open(os.path.join(GECKO, f), encoding="utf-8") as fh:
                mc[f[:-5]] = json.load(fh)
        except Exception:
            pass
    STABLE = {"tether", "usd-coin", "dai", "first-digital-usd", "ethena-usde",
              "usds", "paypal-usd", "true-usd", "binance-usd"}
    gunler = collections.Counter()
    for d in mc.values():
        gunler.update(d.keys())
    tam = [g for g, n in gunler.items() if n >= len(mc) * 0.8]
    out = {}
    for g in sorted(tam):
        tot = sum(d[g] for d in mc.values() if g in d)
        if tot <= 0:
            continue
        u = mc.get("tether", {}).get(g, 0)
        st = sum(mc[s][g] for s in STABLE if s in mc and g in mc[s])
        out[g] = {"total": tot, "usdt_d": 100 * u / tot,
                  "btc_d": 100 * mc.get("bitcoin", {}).get(g, 0) / tot,
                  "eth_d": 100 * mc.get("ethereum", {}).get(g, 0) / tot,
                  "stable_d": 100 * st / tot,
                  "btc_mc": mc.get("bitcoin", {}).get(g, 0)}
    return out, len(mc)


def turev(s):
    g = sorted(s)
    for i, d in enumerate(g):
        x = s[d]
        if i >= 3:
            o = s[g[i - 3]]
            x["total_3g"] = (x["total"] - o["total"]) / o["total"] * 100
            x["usdt_d_3g"] = x["usdt_d"] - o["usdt_d"]
            x["btc_d_3g"] = x["btc_d"] - o["btc_d"]
            x["stable_d_3g"] = x["stable_d"] - o["stable_d"]
        if i + ILERI_GUN < len(g):
            a, b = x["btc_mc"], s[g[i + ILERI_GUN]]["btc_mc"]
            x["ger"] = ((b - a) / a * 100) >= ILERI_ESIK if a else None
        else:
            x["ger"] = None
    return s, g


def kalite(s, g, ad, kural):
    tp = fp = fn = tn = 0
    for d in g:
        x = s[d]
        if x.get("ger") is None or "total_3g" not in x:
            continue
        p = kural(x)
        if p and x["ger"]:
            tp += 1
        elif p and not x["ger"]:
            fp += 1
        elif (not p) and x["ger"]:
            fn += 1
        else:
            tn += 1
    n = tp + fp + fn + tn
    if not n:
        return
    print("%-36s kesinlik %5.1f%%  kapsama %5.1f%%  acik %5.1f%%  (tp %3d fp %3d fn %3d)"
          % (ad, 100 * tp / (tp + fp) if tp + fp else 0,
             100 * tp / (tp + fn) if tp + fn else 0, 100 * (tp + fp) / n, tp, fp, fn))


def gecikme(s, g, ad, kural):
    epi, i = [], 0
    while i < len(g) - ILERI_GUN:
        if s[g[i]].get("ger"):
            epi.append(i)
            i += ILERI_GUN
        else:
            i += 1
    gec, kacan = [], 0
    for j in epi:
        bul = None
        for k in range(j, min(j + 21, len(g))):
            if "total_3g" in s[g[k]] and kural(s[g[k]]):
                bul = k - j
                break
        if bul is None:
            kacan += 1
        else:
            gec.append(bul)
    print("%-36s epizot %2d · gecikme medyan %-8s hemen %2d · kacirilan %2d"
          % (ad, len(epi), "%.1f gun" % sx.median(gec) if gec else "-",
             sum(1 for x in gec if x == 0), kacan))


if __name__ == "__main__":
    s, nc = seri()
    if len(s) < 100:
        print("gecko verisi yetersiz (%d gun, %d coin) — indirme bitmemis olabilir." % (len(s), nc))
        raise SystemExit(0)
    s, g = turev(s)
    var = [d for d in g if s[d].get("ger") is not None and "total_3g" in s[d]]
    tab = 100 * sum(1 for d in var if s[d]["ger"]) / len(var)
    print("=" * 100)
    print("USDT.D / TOTAL / BTC.D — TESPIT KALITESI")
    print("=" * 100)
    print("coin %d · gun %d (%s -> %s) · TABAN ORAN %%%.1f" % (nc, len(g), g[0], g[-1], tab))
    print("TOTAL = top%d mcap toplami (YAKLASIKLIK, gercek TOTAL'in ~%%95'i)\n" % nc)

    K = [
        ("USDT.D DUSUYOR (3g < -0,1 puan)", lambda x: x["usdt_d_3g"] < -0.1),
        ("USDT.D DUSUYOR (3g < -0,3 puan)", lambda x: x["usdt_d_3g"] < -0.3),
        ("STABLE.D DUSUYOR (3g < -0,2)", lambda x: x["stable_d_3g"] < -0.2),
        ("TOTAL ARTIYOR (3g > %+2)", lambda x: x["total_3g"] > 2),
        ("TOTAL ARTIYOR (3g > %+5)", lambda x: x["total_3g"] > 5),
        ("BTC.D ARTIYOR (3g > +0,2)", lambda x: x["btc_d_3g"] > 0.2),
        ("BTC.D DUSUYOR (3g < -0,2)", lambda x: x["btc_d_3g"] < -0.2),
        ("USDT.D dus VE TOTAL art", lambda x: x["usdt_d_3g"] < -0.1 and x["total_3g"] > 2),
        ("USDT.D dus VE BTC.D art", lambda x: x["usdt_d_3g"] < -0.1 and x["btc_d_3g"] > 0.2),
    ]
    print("--- TESPIT KALITESI ---")
    for ad, f in K:
        kalite(s, g, ad, f)
    print("\n--- GECIKME ---")
    for ad, f in K:
        gecikme(s, g, ad, f)
    print("\n--- SON 6 GUN ---")
    for d in g[-6:]:
        x = s[d]
        print("  %s  TOTAL %.3f T$ (%+5.2f%%)  USDT.D %5.2f (%+5.2f)  BTC.D %5.2f (%+5.2f)"
              % (d, x["total"] / 1e12, x.get("total_3g", 0), x["usdt_d"],
                 x.get("usdt_d_3g", 0), x["btc_d"], x.get("btc_d_3g", 0)))
    print("\nKIYAS: mevcut bot etiketi kesinlik %8,4 · gecikme 8,0 gun · kacirilan 36/49")
    print("bot dosyalarina yazim: YOK")
