#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOTUN GUNLUK GETIRISI, PIYASADAN NE KADAR BAGIMSIZ? (2026-09-06)

Kullanici: 'bir adim geri cekilip resmin tamamina bakalim... nerde hata
yapiyoruz'.

Bugunun en buyuk sayisi bir OZELLIK degil, bir DONEM farkiydi:
   kesif tabani  -0,1577 R   (BTC +8,5%)
   holdout tabani +0,0853 R  (BTC +22,5%)

Bu betik sunu sorar: gunluk ortalama R ile BTC gunluk getirisi arasindaki
iliski ne? Yani stratejinin kendi kenari mi var, yoksa BETA mi tasiyor?

🟡 BETIMLEYICI — on-kayit yok, hukum yok, kural cikmaz. SALT-OKUNUR.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, sys, math, collections, statistics as stx
import datetime as dt

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)
sys.path.insert(0, os.path.join(KOK, "scratchpad", "giris_arama"))
import evren  # noqa: E402
import importlib.util as il
sp = il.spec_from_file_location("ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)


def main():
    mum = ar.mumlar()
    rows = ar.veri_kur(mum)
    gun = collections.defaultdict(list)
    for x in rows:
        gun[x["gun"]].append(x["R"])
    gunluk = {g: stx.mean(v) for g, v in gun.items() if len(v) >= 5}

    d = evren.get("https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1d&limit=200")
    btc = {}
    for k in d:
        g = dt.datetime.fromtimestamp(int(k[0]) / 1000, dt.UTC).date().isoformat()
        o, c = float(k[1]), float(k[4])
        btc[g] = (c / o - 1) * 100.0

    ortak = sorted(set(gunluk) & set(btc))
    x = [btc[g] for g in ortak]
    y = [gunluk[g] for g in ortak]
    n = len(x)
    print("=" * 88)
    print("BOTUN GUNLUK R'si vs BTC GUNLUK GETIRISI  (N=%d gun)" % n)
    print("=" * 88)
    if n < 10:
        print("yetersiz")
        return
    mx, my = stx.mean(x), stx.mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    r = sxy / math.sqrt(sxx * syy) if sxx and syy else 0
    beta = sxy / sxx if sxx else 0
    alfa = my - beta * mx
    # alfanin t'si: artiklardan
    art = [b - (alfa + beta * a) for a, b in zip(x, y)]
    se_a = math.sqrt(sum(e * e for e in art) / (n - 2)) * math.sqrt(1.0 / n + mx * mx / sxx)
    t_a = alfa / se_a if se_a else 0

    print("   korelasyon r        : %+.3f" % r)
    print("   BETA (R / BTC %%)    : %+.4f   -> BTC %%1 yukselince ort R %+.4f artiyor"
          % (beta, beta))
    print("   ALFA (BTC=0'da R)   : %+.4f   t = %+.2f" % (alfa, t_a))
    print()
    print("   BTC gunlerine gore botun ortalama R'si:")
    kova = [("BTC < -2%%", lambda v: v < -2), ("-2..0%%", lambda v: -2 <= v < 0),
            ("0..+2%%", lambda v: 0 <= v < 2), ("BTC > +2%%", lambda v: v >= 2)]
    print("   %-12s %6s %11s" % ("kova", "gun", "ort R"))
    for ad, fn in kova:
        vv = [gunluk[g] for g in ortak if fn(btc[g])]
        if vv:
            print("   %-12s %6d %+11.4f" % (ad, len(vv), stx.mean(vv)))
    print()
    print("   TUM DONEM ortalama gunluk R : %+.4f" % my)
    print("   BTC ortalama gunluk         : %+.3f%%" % mx)
    print()
    print("🔑 ALFA = piyasa yatay oldugunda beklenen R. Sifirdan farkli mi?")
    print("🟡 Betimleyici. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
