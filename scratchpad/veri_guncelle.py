#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VERI TEMELI GUNCELLE — klines_1h_uzun ve funding_gecmis 08-11'de DURMUS.

NEDEN: 2 yillik veri seti tam 2026-08-11'de bitiyor. 11-20 Agustos HOLDOUT'u
o veriyle olculemez cunku ILERI GETIRI orada yok. Bu betik ikisini de bugune
kadar uzatir. KALICI veri (30 gun siniri yalniz futures/data icin).

Var olan dosyaya EKLER, bastan indirmez. Atomik yazim (.tmp + os.replace).
SALT scratchpad/ altina yazar.
"""
import os, sys, json, time, random, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import evren                                                    # noqa: E402

KLINE = os.path.join(HERE, "klines_1h_uzun")
FON = os.path.join(HERE, "funding_gecmis")
FAPI = "https://fapi.binance.com"


def _kaydet(yol, veri):
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(veri, f)
    os.replace(tmp, yol)


def kline_guncelle(sym):
    yol = os.path.join(KLINE, "%s.json" % sym)
    try:
        with open(yol, encoding="utf-8") as f:
            b = json.load(f)
    except Exception:
        return 0, 0
    if not b:
        return 0, 0
    n0 = len(b)
    gorulen = {x["t"] for x in b}
    t0 = b[-1]["t"] + 3600000
    son = int(datetime.datetime.now().timestamp() * 1000)
    while t0 < son:
        try:
            d = evren.get("%s/fapi/v1/klines?symbol=%sUSDT&interval=1h&startTime=%d&limit=1500"
                          % (FAPI, sym, t0), timeout=25)
        except Exception:
            d = None
        if not d:
            break
        for k in d:
            t = int(k[0])
            if t in gorulen:
                continue
            gorulen.add(t)
            b.append({"t": t, "o": float(k[1]), "h": float(k[2]), "l": float(k[3]),
                      "c": float(k[4]), "v": float(k[5]), "qv": float(k[7]),
                      "n": int(k[8]), "tbv": float(k[9])})
        yeni = int(d[-1][0]) + 3600000
        if yeni <= t0 or len(d) < 1500:
            break
        t0 = yeni
        time.sleep(random.uniform(0.03, 0.09))
    b.sort(key=lambda x: x["t"])
    if len(b) > n0:
        _kaydet(yol, b)
    return len(b), len(b) - n0


def fonlama_guncelle(sym):
    yol = os.path.join(FON, "%s.json" % sym)
    try:
        with open(yol, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        return 0, 0
    if not d:
        return 0, 0
    n0 = len(d)
    gorulen = {x["t"] for x in d}
    t0 = d[-1]["t"] + 1
    son = int(datetime.datetime.now().timestamp() * 1000)
    while t0 < son:
        try:
            r = evren.get("%s/fapi/v1/fundingRate?symbol=%sUSDT&startTime=%d&limit=1000"
                          % (FAPI, sym, t0), timeout=25)
        except Exception:
            r = None
        if not r:
            break
        ekle = 0
        for x in r:
            t = int(x["fundingTime"])
            if t in gorulen:
                continue
            gorulen.add(t)
            d.append({"t": t, "r": float(x["fundingRate"])})
            ekle += 1
        yeni = int(r[-1]["fundingTime"]) + 1
        if yeni <= t0 or ekle == 0:
            break
        t0 = yeni
        time.sleep(random.uniform(0.03, 0.09))
    d.sort(key=lambda x: x["t"])
    if len(d) > n0:
        _kaydet(yol, d)
    return len(d), len(d) - n0


if __name__ == "__main__":
    hedef = sys.argv[1:] or None
    syms = hedef or sorted(f[:-5] for f in os.listdir(KLINE) if f.endswith(".json"))
    print("VERI GUNCELLEME — %d sembol" % len(syms))
    tk = tf = 0
    for i, s in enumerate(syms, 1):
        nk, yk = kline_guncelle(s)
        nf, yf = fonlama_guncelle(s)
        tk += yk
        tf += yf
        if yk or yf or i % 50 == 0:
            print("  [%3d/%3d] %-12s kline %5d (+%3d)  fonlama %5d (+%2d)"
                  % (i, len(syms), s, nk, yk, nf, yf))
            sys.stdout.flush()
    print("\nTOPLAM yeni: %d kline bari · %d fonlama kaydi" % (tk, tf))
    print("bot dosyalarina yazim: YOK (yalniz scratchpad/)")
