#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TOTAL1 / TOTAL2 / TOTAL3 — kendi cektigimiz veriyle.

TOTAL1 = tum kripto mcap (burada: top-98 toplami, gercegin ~%95'i)
TOTAL2 = TOTAL1 - BTC
TOTAL3 = TOTAL1 - BTC - ETH
TOTAL3X= TOTAL3 - STABLECOIN'LER   <- gercek "alt parasi" olcusu

Veri: scratchpad/gecko/ (98 coin x gunluk mcap x 365 gun)

UC SORU:
  1) Tespit kalitesi — TOTAL2/3 hareketi ileri yonu soyluyor mu?
  2) ONCULUK — TOTAL3 BTC'den ONCE mi doner, SONRA mi? (capraz korelasyon)
  3) Bugun ne diyor?

SALT OKUMA.
"""
import os, json, collections, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
GECKO = os.path.join(os.path.dirname(HERE), "gecko")
ILERI, ESIK = 7, 3.0
STABLE = {"tether", "usd-coin", "dai", "first-digital-usd", "ethena-usde", "usds",
          "paypal-usd", "true-usd", "binance-usd", "usdd", "frax"}


def seri():
    mc = {}
    for f in os.listdir(GECKO):
        if not f.endswith(".json") or f.startswith("_"):
            continue
        try:
            with open(os.path.join(GECKO, f), encoding="utf-8") as fh:
                mc[f[:-5]] = json.load(fh)
        except Exception:
            pass
    say = collections.Counter()
    for d in mc.values():
        say.update(d.keys())
    gunler = sorted(g for g, n in say.items() if n >= len(mc) * 0.8)
    out = {}
    for g in gunler:
        t1 = sum(d[g] for d in mc.values() if g in d)
        btc = mc.get("bitcoin", {}).get(g, 0)
        eth = mc.get("ethereum", {}).get(g, 0)
        stb = sum(mc[s][g] for s in STABLE if s in mc and g in mc[s])
        if t1 <= 0:
            continue
        out[g] = {"T1": t1, "T2": t1 - btc, "T3": t1 - btc - eth,
                  "T3X": t1 - btc - eth - stb, "BTC": btc, "STB": stb}
    return out, gunler, len(mc)


def turev(s, g):
    for i, d in enumerate(g):
        if d not in s:
            continue
        x = s[d]
        for n in (1, 3):
            if i >= n and g[i - n] in s:
                o = s[g[i - n]]
                for k in ("T1", "T2", "T3", "T3X", "BTC"):
                    x["%s_%dg" % (k, n)] = (x[k] - o[k]) / o[k] * 100 if o[k] else None
        # ALT PAYI: T3X / T1
        x["alt_pay"] = 100 * x["T3X"] / x["T1"]
        if i >= 3 and g[i - 3] in s:
            x["alt_pay_3g"] = x["alt_pay"] - (100 * s[g[i - 3]]["T3X"] / s[g[i - 3]]["T1"])
        if i + ILERI < len(g) and g[i + ILERI] in s:
            a, b = x["BTC"], s[g[i + ILERI]]["BTC"]
            x["ger"] = ((b - a) / a * 100) >= ESIK if a else None
        else:
            x["ger"] = None
    return s


def kalite(s, g, ad, f):
    tp = fp = fn = tn = 0
    for d in g:
        x = s.get(d)
        if not x or x.get("ger") is None or "T3_3g" not in x:
            continue
        p = f(x)
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
    print("  %-34s kesinlik %5.1f%%  kapsama %5.1f%%  acik %5.1f%%  (tp %3d fp %3d)"
          % (ad, 100 * tp / (tp + fp) if tp + fp else 0,
             100 * tp / (tp + fn) if tp + fn else 0, 100 * (tp + fp) / n, tp, fp))


def gecikme(s, g, ad, f):
    epi, i = [], 0
    while i < len(g) - ILERI:
        if s.get(g[i], {}).get("ger"):
            epi.append(i)
            i += ILERI
        else:
            i += 1
    gec, kacan = [], 0
    for j in epi:
        bul = None
        for k in range(j, min(j + 21, len(g))):
            x = s.get(g[k])
            if x and "T3_3g" in x and f(x):
                bul = k - j
                break
        if bul is None:
            kacan += 1
        else:
            gec.append(bul)
    print("  %-34s epizot %2d · gecikme medyan %-8s hemen %2d · kacirilan %2d"
          % (ad, len(epi), "%.1f gun" % sx.median(gec) if gec else "-",
             sum(1 for x in gec if x == 0), kacan))


def capraz(s, g):
    """TOTAL3 gunluk getirisi, BTC'nin +/- k gun kaydirilmis getirisiyle korelasyon."""
    print("\n  CAPRAZ KORELASYON — TOTAL3X gunluk vs BTC gunluk (kaydirmali)")
    print("  %-10s %10s   yorum" % ("kaydirma", "korelasyon"))
    t3 = [(d, s[d].get("T3X_1g")) for d in g if d in s and s[d].get("T3X_1g") is not None]
    bt = {d: s[d].get("BTC_1g") for d in g if d in s}
    for k in (-3, -2, -1, 0, 1, 2, 3):
        cift = []
        for i, (d, v) in enumerate(t3):
            j = i + k
            if 0 <= j < len(t3):
                b = bt.get(t3[j][0])
                if b is not None:
                    cift.append((v, b))
        if len(cift) < 50:
            continue
        mx, my = sx.mean(a for a, _ in cift), sx.mean(b for _, b in cift)
        pay = sum((a - mx) * (b - my) for a, b in cift)
        pd = (sum((a - mx) ** 2 for a, _ in cift) * sum((b - my) ** 2 for _, b in cift)) ** 0.5
        r = pay / pd if pd else 0
        yorum = ("TOTAL3 %d gun ONCE" % -k if k < 0 else
                 "esanli" if k == 0 else "TOTAL3 %d gun SONRA" % k)
        print("  %-10s %10.4f   %s" % ("k=%+d" % k, r, yorum))


if __name__ == "__main__":
    s, g, nc = seri()
    s = turev(s, g)
    var = [d for d in g if d in s and s[d].get("ger") is not None and "T3_3g" in s[d]]
    tab = 100 * sum(1 for d in var if s[d]["ger"]) / len(var)
    print("=" * 100)
    print("TOTAL1 / TOTAL2 / TOTAL3 — BIZIM CEKTIGIMIZ VERIYLE")
    print("=" * 100)
    print("coin %d · gun %d (%s -> %s) · TABAN ORAN %%%.1f\n" % (nc, len(g), g[0], g[-1], tab))
    K = [
        ("TOTAL1 3g > %+2", lambda x: x["T1_3g"] > 2),
        ("TOTAL2 3g > %+2 (BTC haric)", lambda x: x["T2_3g"] > 2),
        ("TOTAL3 3g > %+2 (BTC+ETH haric)", lambda x: x["T3_3g"] > 2),
        ("TOTAL3X 3g > %+2 (stable de haric)", lambda x: x["T3X_3g"] > 2),
        ("TOTAL3X 3g > %+5", lambda x: x["T3X_3g"] > 5),
        ("ALT PAYI artiyor (3g > +0,2)", lambda x: x.get("alt_pay_3g", 0) > 0.2),
        ("TOTAL3X art VE alt payi art", lambda x: x["T3X_3g"] > 2 and x.get("alt_pay_3g", 0) > 0.2),
        ("TOTAL2 art VE TOTAL1 art", lambda x: x["T2_3g"] > 2 and x["T1_3g"] > 2),
    ]
    print("--- 1) TESPIT KALITESI ---")
    for ad, f in K:
        kalite(s, g, ad, f)
    print("\n--- 2) GECIKME ---")
    for ad, f in K:
        gecikme(s, g, ad, f)
    capraz(s, g)
    print("\n--- 3) SON 8 GUN ---")
    print("  %-11s %9s %9s %9s %9s   %8s %8s" % ("gun", "T1 T$", "T2 T$", "T3 T$", "T3X T$", "T3X 3g%", "altpay%"))
    for d in g[-8:]:
        x = s[d]
        print("  %-11s %9.3f %9.3f %9.3f %9.3f   %+8.2f %8.2f"
              % (d, x["T1"] / 1e12, x["T2"] / 1e12, x["T3"] / 1e12, x["T3X"] / 1e12,
                 x.get("T3X_3g", 0), x["alt_pay"]))
    print("\nbot dosyalarina yazim: YOK")
