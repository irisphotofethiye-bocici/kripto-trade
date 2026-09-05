#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KAPSAM SAYIMI — stop mesafesi olcumu ONCESI guc girdisi (2026-09-05)

NE YAPAR: yalnizca TETIK SAYAR. Getiri, stop, hedef, sonuc HESAPLAMAZ.
NEDEN ON-KAYITTAN ONCE: on-kayit kapsami (hangi evren birincil, oi24 bacagi
  olculebilir mi) bu sayilara bagli. Sonuc degiskenine dokunulmadigi icin
  "sonuca bakip olcut secme" riski YOKTUR.

SORU: A+B kapisinin (funding <= -0.05 VE oi24 >= %10) tam hali kac olay verir?
  A+B  bir ALT KUME'dir: A+B  subset  A_funding.
  Yani A_funding'in perp_seri ortusme penceresindeki sayisi bir UST SINIR'dir.

Salt-okunur. Bot dosyalarina yazim: YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, bisect, datetime as dt

BURA = os.path.dirname(os.path.abspath(__file__))
KLINE = os.path.join(BURA, "klines_1h_uzun")
FUND = os.path.join(BURA, "funding_gecmis")
PERP = os.path.join(BURA, "perp_seri")

# ileri_rr.py ile BIREBIR ayni evren parametreleri
ISINMA, SEYRELT, UFUK = 220, 24, 72
FUND_ESIK, PUMP, MIN_VOL = -0.05, 20.0, 3_000_000
UCUZ_FIYAT, MA50_MESAFE = 0.07, 3.72


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


def utc(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d")


def main():
    oi_sym = set()
    oi_bas, oi_son = {}, {}
    for f in os.listdir(PERP):
        if not f.endswith("_oi.json"):
            continue
        sym = f[:-8]
        try:
            j = json.load(open(os.path.join(PERP, f), encoding="utf-8"))
        except Exception:
            continue
        if not j:
            continue
        oi_sym.add(sym)
        oi_bas[sym] = j[0]["timestamp"]
        oi_son[sym] = j[-1]["timestamp"]

    print("=" * 74)
    print("KAPSAM SAYIMI — stop mesafesi olcumu icin guc girdisi")
    print("=" * 74)
    print("perp_seri OI olan sembol: %d" % len(oi_sym))
    print("klines_1h_uzun sembol   : %d" % len([f for f in os.listdir(KLINE) if f.endswith(".json")]))

    tum_a = tum_b = 0
    ort_a = 0                      # A_funding, perp_seri ortusme penceresinde
    ort_gun = set()
    a_gun, b_gun = set(), set()
    islenen = 0
    for fn in sorted(os.listdir(KLINE)):
        if not fn.endswith(".json"):
            continue
        sym = fn[:-5]
        try:
            b = json.load(open(os.path.join(KLINE, fn), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ISINMA + UFUK + 50:
            continue
        fpath = os.path.join(FUND, fn)
        fr = []
        if os.path.exists(fpath):
            try:
                fr = json.load(open(fpath, encoding="utf-8"))
            except Exception:
                fr = []
        ft = [x["t"] for x in fr]
        ma50 = ma_serisi(b, 50)
        islenen += 1
        ob = oi_bas.get(sym)
        os_ = oi_son.get(sym)
        for i in range(ISINMA, len(b) - UFUK - 2, SEYRELT):
            x = b[i]
            if (x.get("qv") or 0) < MIN_VOL / 24:
                continue
            if i < 24:
                continue
            if (x["c"] / b[i - 24]["c"] - 1) * 100 >= PUMP:
                continue
            a = False
            if ft:
                k = bisect.bisect_right(ft, x["t"]) - 1
                if k >= 0 and fr[k]["r"] <= FUND_ESIK:
                    a = True
            bb = False
            if ma50[i] and ma50[i] > 0 and x["c"] <= UCUZ_FIYAT:
                if (x["c"] / ma50[i] - 1) * 100 >= MA50_MESAFE:
                    bb = True
            if a:
                tum_a += 1
                a_gun.add(x["t"] // 86400000)
                # oi24 icin: bar zamani VE 24 saat oncesi OI penceresi icinde olmali
                if ob is not None and x["t"] - 86400000 >= ob and x["t"] <= os_:
                    ort_a += 1
                    ort_gun.add(x["t"] // 86400000)
            if bb:
                tum_b += 1
                b_gun.add(x["t"] // 86400000)

    print("islenen sembol: %d\n" % islenen)
    print("2 YILLIK EVREN (klines_1h_uzun, seyrelt=%d)" % SEYRELT)
    print("  A_funding   tetik = %6d   ayri gun = %4d" % (tum_a, len(a_gun)))
    print("  B_ma50ucuz  tetik = %6d   ayri gun = %4d" % (tum_b, len(b_gun)))
    print()
    print("oi24 BACAGI ICIN ORTUSME (perp_seri OI x klines):")
    print("  A_funding tetigi, OI penceresi icinde = %d   ayri gun = %d" % (ort_a, len(ort_gun)))
    print("  ^ bu bir UST SINIR: A+B  subset  A_funding, oi24 kapisi bunu KUCULTUR.")
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
