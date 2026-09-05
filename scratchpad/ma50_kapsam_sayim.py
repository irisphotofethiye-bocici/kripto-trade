#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MA50 KAPISI — BOGA penceresi KAPSAM SAYIMI (2026-09-05)

NE YAPAR: yalnizca TETIK sayar. Getiri/stop/hedef HESAPLAMAZ.

NEDEN ONEMLI: MA50+ucuz kapisinin IKI girdisi de (fiyat <= $0.07 ·
  ma50_mesafe >= %3.72) YALNIZCA MUMDAN hesaplanir. radar_archive'a
  ihtiyac YOKTUR -> onceki olcumu durduran dongu-damgasi hizalama sorunu
  BU KAPIDA GECERLI DEGIL.

Salt-okunur. Veri indirme YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, collections, datetime as dt

BURA = os.path.dirname(os.path.abspath(__file__))
PERP = os.path.join(BURA, "perp_seri")

UCUZ_FIYAT, MA50_MESAFE = 0.07, 3.72
PUMP, MIN_VOL = 20.0, 3_000_000
ISINMA, UFUK = 220, 72
SOGUMA_SAAT = 24
BOGA_BAS = "2026-08-21"


def saatlik(b5):
    g = collections.OrderedDict()
    for x in b5:
        s = (x["t"] // 3600000) * 3600000
        d = g.get(s)
        if d is None:
            g[s] = {"t": s, "o": x["o"], "h": x["h"], "l": x["l"], "c": x["c"],
                    "qv": x.get("qv") or 0.0}
        else:
            d["h"] = max(d["h"], x["h"])
            d["l"] = min(d["l"], x["l"])
            d["c"] = x["c"]
            d["qv"] += x.get("qv") or 0.0
    return [v for _, v in sorted(g.items())]


def ma_serisi(b, n=50):
    out = [None] * len(b)
    s = 0.0
    for i, x in enumerate(b):
        s += x["c"]
        if i >= n:
            s -= b[i - n]["c"]
        if i >= n - 1:
            out[i] = s / n
    return out


def ms(s):
    return int(dt.datetime.strptime(s, "%Y-%m-%d")
               .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def gunad(t):
    return dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%Y-%m-%d")


def main():
    bas = ms(BOGA_BAS)
    print("=" * 74)
    print("MA50+UCUZ KAPISI — BOGA PENCERESI KAPSAM SAYIMI")
    print("=" * 74)
    print("kapi: fiyat <= $%.2f  VE  ma50_mesafe >= %%%.2f   (ikisi de MUMDAN)" %
          (UCUZ_FIYAT, MA50_MESAFE))
    print("arsive ihtiyac YOK -> dongu-damgasi hizalama sorunu GECERSIZ\n")

    ucuz_sem, tum_sem = set(), set()
    say = collections.Counter()
    olay_gun, olay_sem = set(), set()
    son_olay = {}
    en_son = 0
    tumler = []

    for f in sorted(os.listdir(PERP)):
        if not f.endswith("_kline.json"):
            continue
        sym = f[:-11]
        try:
            j = json.load(open(os.path.join(PERP, f), encoding="utf-8"))
        except Exception:
            continue
        if not j:
            continue
        b = saatlik(j)
        if len(b) < ISINMA + 10:
            continue
        tum_sem.add(sym)
        en_son = max(en_son, b[-1]["t"])
        if min(x["c"] for x in b) <= UCUZ_FIYAT:
            ucuz_sem.add(sym)
        tumler.append((sym, b))

    kesme = en_son - UFUK * 3600000
    print("perp_seri sembol (1sa)          : %d" % len(tum_sem))
    print("  fiyati bir an <= $%.2f olan   : %d" % (UCUZ_FIYAT, len(ucuz_sem)))
    print("  kline sonu %s · 72s ileri icin kesme %s\n" % (gunad(en_son), gunad(kesme)))

    for sym, b in tumler:
        ma50 = ma_serisi(b, 50)
        for i in range(ISINMA, len(b)):
            x = b[i]
            if x["t"] < bas:
                continue
            if x["t"] > kesme:
                say["ileri_getiri_YOK"] += 1
                continue
            if (x.get("qv") or 0) < MIN_VOL / 24:
                continue
            if i < 24 or b[i - 24]["c"] <= 0:
                continue
            if (x["c"] / b[i - 24]["c"] - 1) * 100 >= PUMP:
                say["pump_elendi"] += 1
                continue
            if x["c"] > UCUZ_FIYAT:
                continue
            say["ucuz_gecti"] += 1
            if not ma50[i] or ma50[i] <= 0:
                continue
            if (x["c"] / ma50[i] - 1) * 100 < MA50_MESAFE:
                continue
            say["ham_tetik"] += 1
            s0 = son_olay.get(sym)
            if s0 is not None and x["t"] - s0 < SOGUMA_SAAT * 3600000:
                say["soguma_elendi"] += 1
                continue
            son_olay[sym] = x["t"]
            say["OLAY"] += 1
            olay_gun.add(gunad(x["t"]))
            olay_sem.add(sym)

    print("BOGA penceresi %s -> %s" % (BOGA_BAS, gunad(kesme)))
    print("  ucuz kapisini gecen bar-sayisi : %d" % say["ucuz_gecti"])
    print("  pump (>=%%%.0f) ile elenen      : %d" % (PUMP, say["pump_elendi"]))
    print("  HAM tetik (iki kapi da)        : %d" % say["ham_tetik"])
    print("  soguma (%ds) ile elenen        : -%d" % (SOGUMA_SAAT, say["soguma_elendi"]))
    print("  >>> BAGIMSIZ OLAY              : %d   (%d gun · %d sembol)"
          % (say["OLAY"], len(olay_gun), len(olay_sem)))
    if olay_gun:
        g = sorted(olay_gun)
        print("      gun araligi: %s .. %s" % (g[0], g[-1]))
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
