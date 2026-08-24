#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AYIDAN CIKIS — dogru kiyas kumesi.

KULLANICI (2026-08-21): "surekli guclu boga doneminden bahsediyorsun ama bu
guclu boga karsiligi degil, bu AYIDAN SICRAYIS. Bununla karsilastirilmali,
yoksa btc'nin 100 bin oldugu zamanla degil."

DOGRU: 09_boga_bacagi.py 69 olayi tek kefeye koydu. Onlarin cogu BOGA ICI
devam hareketi (2024-11, 2025-01, 2025-07 gibi ATH bolgesinde). Bugunku ise
ZIRVEDEN -%54 dusmus bir piyasada dipten toparlanma. Ayni sey degil.

BU BETIK: BTC'nin ZIRVEDEN GERI CEKILMESINE gore rejim ayirir ve
"derin dipten sicrayis" epizotlarini bulup KARSILASTIRIR.

SALT OKUMA.
"""
import os, json, datetime, statistics as sx, bisect, collections

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
BAR24 = 288


def yukle(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


b = yukle(os.path.join(SCRATCH, "major_5dk", "BTC.json"))
fd = yukle(os.path.join(SCRATCH, "funding_gecmis", "BTC.json"))
fts = [x["t"] for x in fd]
frs = [x["r"] for x in fd]


def fon(t0, t1):
    i, j = bisect.bisect_right(fts, t0), bisect.bisect_right(fts, t1)
    v = frs[i:j]
    return sx.mean(v) if v else None


# --- kosan zirve ve geri cekilme ---
zirve, dd = [], []
z = 0.0
for x in b:
    z = max(z, x["h"])
    zirve.append(z)
    dd.append((x["c"] - z) / z * 100)

print("=" * 92)
print("BTC — ZIRVEDEN GERI CEKILME (drawdown) ve REJIM")
print("=" * 92)
ay = collections.OrderedDict()
for i, x in enumerate(b):
    m = datetime.datetime.fromtimestamp(x["t"] / 1000).strftime("%Y-%m")
    ay.setdefault(m, []).append(dd[i])
print("%-9s %10s %10s   %s" % ("ay", "ort dd%", "ay sonu dd%", "rejim"))
print("-" * 56)
for m, v in ay.items():
    son = v[-1]
    rej = ("ATH bolgesi" if son > -5 else
           "hafif geri cekilme" if son > -15 else
           "duzeltme" if son > -30 else "DERIN AYI")
    print("%-9s %+10.1f %+10.1f   %s" % (m, sx.mean(v), son, rej))

# --- DERIN DIPTEN SICRAYIS epizotlari ---
print("\n" + "=" * 92)
print("DERIN DIPTEN SICRAYIS — dd <= -30%% iken baslayip +%15 toparlanan epizotlar")
print("=" * 92)
epi, i = [], BAR24
while i < len(b) - BAR24:
    if dd[i] <= -30:
        # bu andan sonraki 60 gunde dipten +%15 toparlanma var mi
        dip = min(x["l"] for x in b[max(0, i - BAR24):i + 1])
        ileri = b[i:i + BAR24 * 60]
        if ileri:
            tepe = max(x["h"] for x in ileri)
            if (tepe - dip) / dip * 100 >= 15:
                epi.append((i, b[i]["t"], dip, tepe))
                i += BAR24 * 45
                continue
    i += 12
# ayni dipi tekrar sayma
temiz = []
for e in epi:
    if not temiz or abs(e[2] - temiz[-1][2]) / temiz[-1][2] > 0.05:
        temiz.append(e)
print("%-14s %10s %10s %9s   %s" % ("baslangic", "dip", "sonraki tepe", "toparlan%", "sonuc"))
print("-" * 70)
for i, t, dip, tepe in temiz:
    d = datetime.datetime.fromtimestamp(t / 1000)
    # 60 gun sonra hala yukarida mi
    sonra = b[min(i + BAR24 * 60, len(b) - 1)]["c"]
    print("%-14s %10.0f %10.0f %+9.1f   60 gun sonra %6.0f (%s)"
          % (d.strftime("%Y-%m-%d"), dip, tepe, (tepe - dip) / dip * 100, sonra,
             "TUTTU" if sonra > dip * 1.15 else "GERI VERDI"))

# --- her epizotta fonlama ---
print("\n" + "=" * 92)
print("EPIZOTLARDA FONLAMA (%%/8 saat) — sicrayisin ONCESI ve SIRASI")
print("=" * 92)
print("%-14s %12s %12s %12s %10s" % ("epizot", "dip-7gun", "dip+-1gun", "dip+7gun", "tavan%"))
print("-" * 66)
for i, t, dip, tepe in temiz:
    d = datetime.datetime.fromtimestamp(t / 1000)
    a = fon(t - 7 * 86400000, t - 86400000)
    m = fon(t - 86400000, t + 86400000)
    s = fon(t + 86400000, t + 7 * 86400000)
    j0, j1 = bisect.bisect_right(fts, t - 7 * 86400000), bisect.bisect_right(fts, t + 7 * 86400000)
    tv = frs[j0:j1]
    klamp = 100 * sum(1 for x in tv if abs(abs(x) - 1.0) < 1e-9) / len(tv) if tv else 0
    print("%-14s %12s %12s %12s %9.0f%%"
          % (d.strftime("%Y-%m-%d"),
             "%+.4f" % a if a is not None else "-",
             "%+.4f" % m if m is not None else "-",
             "%+.4f" % s if s is not None else "-", klamp))
print("\nNOT: fonlama verisi 2026-08-11'de bitiyor -> bugunku epizot icin YOK.")
print("bot dosyalarina yazim: YOK")
