#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Eksik hacim (quote volume) alanini tamamlar — ilk indirmede yalniz OHLC saklanmisti."""
import json, os, time, urllib.request

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h")
FAPI = "https://fapi.binance.com"
BAS = 1781222400000


def indir(sym):
    out, bas = [], BAS
    while True:
        u = f"{FAPI}/fapi/v1/klines?symbol={sym}USDT&interval=1h&startTime={bas}&limit=1500"
        try:
            with urllib.request.urlopen(urllib.request.Request(
                    u, headers={"User-Agent": "hacim/1.0"}), timeout=30) as r:
                d = json.loads(r.read())
        except Exception:
            return None
        if not d:
            break
        out += d
        if len(d) < 1500:
            break
        bas = d[-1][0] + 3600000
        time.sleep(0.1)
    return [{"t": int(k[0]), "o": float(k[1]), "h": float(k[2]), "l": float(k[3]),
             "c": float(k[4]), "v": float(k[5]), "qv": float(k[7]),
             "n": int(k[8]), "tbv": float(k[9])} for k in out]


eksik = []
for f in os.listdir(CACHE):
    if not f.endswith(".json"):
        continue
    p = os.path.join(CACHE, f)
    try:
        b = json.load(open(p))
    except Exception:
        continue
    if not b or "qv" not in b[-1]:
        eksik.append(f[:-5])

print(f"eksik: {len(eksik)} sembol")
for n, s in enumerate(eksik, 1):
    b = indir(s)
    if b and len(b) > 100:
        json.dump(b, open(os.path.join(CACHE, f"{s}.json"), "w"))
    if n % 40 == 0:
        print(f"  {n}/{len(eksik)}")
    time.sleep(0.05)
print("tamam")
