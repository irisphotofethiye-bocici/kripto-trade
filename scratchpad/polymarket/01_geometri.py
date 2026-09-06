#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""%92,6 BIR KENAR MI, YOKSA SADECE GEOMETRI MI? (2026-09-06)

00_pilot.py 'hareket $70-100 ise %92,6 ayni tarafta kapaniyor' dedi.
BU BIR KENAR DEGIL OLABILIR: rastgele yuruyuste de, 3 dakikada d kadar
uzaklasmis fiyatin 2 dakikada geri donmesi zordur. Piyasa bunu ZATEN bilir
ve fiyati ona gore koyar.

SINAMA: gozlenen olasilik, RASTGELE YURUYUS formuluyle ortusuyor mu?
   P(ayni tarafta) = Phi( d / (sigma * sqrt(kalan_dakika)) )
Ortusuyorsa BILGI YOK, yalniz geometri var.

🟡 BETIMLEYICI. SALT-OKUNUR.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import io, zipfile, urllib.request, collections, datetime as dt, math
import statistics as stx

KOK_URL = "https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/1m"
AYLAR = ["2026-06", "2026-07", "2026-08"]
PENCERE, GECEN = 5, 3
BANTLAR = [(20, 40), (40, 70), (70, 100), (100, 150), (150, 250), (250, 1e9)]


def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def ay_indir(ay):
    ham = urllib.request.urlopen("%s/BTCUSDT-1m-%s.zip" % (KOK_URL, ay), timeout=120).read()
    z = zipfile.ZipFile(io.BytesIO(ham))
    out = []
    for l in z.read(z.namelist()[0]).decode("utf-8", "replace").splitlines():
        p = l.split(",")
        if len(p) < 5 or not p[0].isdigit():
            continue
        out.append((int(p[0]), float(p[1]), float(p[4])))
    return out


def main():
    bar = []
    for ay in AYLAR:
        bar += ay_indir(ay)
    bar.sort()
    ix = {t: i for i, (t, o, c) in enumerate(bar)}

    # 1 dakikalik dolar oynakligi
    dk = [abs(bar[i][2] - bar[i - 1][2]) for i in range(1, len(bar))]
    sigma = stx.median(dk) * 1.2533
    print("1 dakikalik BTC dolar oynakligi (sigma) : $%.1f" % sigma)
    print("kalan sure: %d dakika -> sqrt(%d)*sigma = $%.1f"
          % (PENCERE - GECEN, PENCERE - GECEN, sigma * math.sqrt(PENCERE - GECEN)))
    print()

    kova = collections.defaultdict(lambda: [0, 0, []])
    for i, (t, o, c) in enumerate(bar):
        d = dt.datetime.fromtimestamp(t / 1000, dt.UTC)
        if d.minute % PENCERE != 0:
            continue
        i3 = ix.get(t + (GECEN - 1) * 60_000)
        i5 = ix.get(t + (PENCERE - 1) * 60_000)
        if i3 is None or i5 is None:
            continue
        h = bar[i3][2] - o
        a = abs(h)
        for lo, hi in BANTLAR:
            if lo <= a < hi:
                k = kova[(lo, hi)]
                k[0] += 1
                yon = 1 if h > 0 else -1
                son = 1 if (bar[i5][2] - o) > 0 else (-1 if (bar[i5][2] - o) < 0 else 0)
                if son == yon:
                    k[1] += 1
                k[2].append(a)
                break

    print("%-14s %7s %10s %12s %10s %9s" %
          ("hareket ($)", "N", "gozlenen", "RASTGELE", "fark", "s.h."))
    for lo, hi in BANTLAR:
        n, w, ds = kova[(lo, hi)]
        if n < 30:
            continue
        p = w / n
        dmed = stx.median(ds)
        beklenen = phi(dmed / (sigma * math.sqrt(PENCERE - GECEN)))
        se = math.sqrt(p * (1 - p) / n)
        et = "%d-%d" % (lo, hi) if hi < 1e9 else "%d+" % lo
        print("%-14s %7d %9.2f%% %11.2f%% %+9.2f %8.2f"
              % (et, n, 100 * p, 100 * beklenen, 100 * (p - beklenen), 100 * se))
    print()
    print("🔑 'gozlenen' ile 'RASTGELE' ortusuyorsa: BILGI YOK, sadece geometri.")
    print("   Piyasa bunu zaten bilir ve fiyati ~gozlenen olasiliga koyar.")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
