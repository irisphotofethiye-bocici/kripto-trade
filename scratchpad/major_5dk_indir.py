#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MAJOR 5 DAKIKALIK MUM — 2 yillik, BTC/ETH.

NEDEN: "hacim patliyor ama fiyat kimildamiyor" izi 5 dakikalik olcekte gorunur;
1 saatlik mumda kaybolur (19 Agu 15:30 izi 15 dk'lik mumda gorulmustu).
5 dk mum KALICI (dogrulandi: 2024-09-01 cekilebiliyor) — 30 gun siniri yalniz
futures/data (OI, long/short) icin gecerli.

SALT OKUMA · scratchpad/major_5dk/ altina yazar.
"""
import os, sys, json, datetime, time, random

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import evren                                                    # noqa: E402

CIKTI = os.path.join(HERE, "major_5dk")
os.makedirs(CIKTI, exist_ok=True)


def indir(sym, gun=730):
    yol = os.path.join(CIKTI, "%s.json" % sym)
    bit = int(datetime.datetime.now().timestamp() * 1000)
    t0 = bit - gun * 86400000
    out, gorulen = [], set()
    if os.path.exists(yol):
        try:
            out = json.load(open(yol, encoding="utf-8"))
            gorulen = {x["t"] for x in out}
            if out:
                t0 = max(t0, out[-1]["t"] + 300000)
        except Exception:
            out, gorulen = [], set()
    n0 = len(out)
    while t0 < bit:
        u = ("https://fapi.binance.com/fapi/v1/klines?symbol=%sUSDT&interval=5m"
             "&startTime=%d&limit=1500" % (sym, t0))
        try:
            d = evren.get(u, timeout=25)
        except Exception:
            d = None
        if not d:
            break
        for k in d:
            t = int(k[0])
            if t in gorulen:
                continue
            gorulen.add(t)
            out.append({"t": t, "o": float(k[1]), "h": float(k[2]), "l": float(k[3]),
                        "c": float(k[4]), "v": float(k[5]), "qv": float(k[7]),
                        "n": int(k[8]), "tbv": float(k[9]), "tqv": float(k[10])})
        yeni = int(d[-1][0]) + 300000
        if yeni <= t0 or len(d) < 1500:
            break
        t0 = yeni
        time.sleep(random.uniform(0.05, 0.12))
    out.sort(key=lambda x: x["t"])
    tmp = yol + ".tmp"
    json.dump(out, open(tmp, "w", encoding="utf-8"))
    os.replace(tmp, yol)
    return len(out), len(out) - n0


if __name__ == "__main__":
    for s in (sys.argv[1:] or ["BTC", "ETH"]):
        n, yeni = indir(s)
        b = json.load(open(os.path.join(CIKTI, "%s.json" % s), encoding="utf-8"))
        print("%-5s %7d bar (+%d yeni)  %s -> %s" %
              (s, n, yeni,
               datetime.datetime.fromtimestamp(b[0]["t"] / 1000).date(),
               datetime.datetime.fromtimestamp(b[-1]["t"] / 1000).date()))
        sys.stdout.flush()
    print("bot dosyalarina yazim: YOK")
