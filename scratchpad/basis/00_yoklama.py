#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BASIS YOKLAMASI — olcum DEGIL, elemedir.

Tek soru: spot-perp basis, FONLAMANIN kilik degistirmis hali mi?
Bu proje her yeni adayin "ayni seyin baska ifadesi" ciktigini defalarca
gordu (CLAUDE.md). Buyuk indirmeye girmeden ONCE bunu sor.

Basis yuksek korelasyonluysa fikir BURADA olur, maliyet ~0.
SALT OKUMA + kucuk ag cagrisi (kalici uc, spot klines).
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, glob, time, urllib.request, statistics

HERE  = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(os.path.dirname(HERE))
KL    = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
FG    = os.path.join(PROJE, "scratchpad", "funding_gecmis")
N_SEM = 30
N_BAR = 700          # ~29 gun saatlik


def spot_kline(sym, limit=700):
    u = ("https://api.binance.com/api/v3/klines?symbol=%sUSDT&interval=1h&limit=%d"
         % (sym, limit))
    with urllib.request.urlopen(u, timeout=60) as r:
        return json.load(r)


semboller = [os.path.basename(p)[:-5] for p in sorted(glob.glob(os.path.join(KL, "*.json")))]
# perp'i EN UZUN olanlardan sec (likit, spotta da olma ihtimali yuksek)
boy = sorted(((os.path.getsize(os.path.join(KL, s + ".json")), s) for s in semboller),
             reverse=True)
aday = [s for _, s in boy[:120]]

print("BASIS YOKLAMASI — basis, fonlamanin kilik degistirmis hali mi?")
print("=" * 96)

satir, yok, hata = [], 0, 0
for s in aday:
    if len(satir) >= N_SEM:
        break
    try:
        sk = spot_kline(s, N_BAR)
    except Exception:
        yok += 1
        continue
    if not sk or len(sk) < 200:
        yok += 1
        continue
    try:
        pk = json.load(open(os.path.join(KL, s + ".json"), encoding="utf-8"))
        fg = json.load(open(os.path.join(FG, s + ".json"), encoding="utf-8"))
    except Exception:
        hata += 1
        continue
    perp = {int(x["t"]): float(x["c"]) for x in pk}
    spot = {int(x[0]): float(x[4]) for x in sk}
    fund = {int(x["t"]) // 3600000 * 3600000: float(x["r"]) for x in fg}

    b, f = [], []
    for t, sc in spot.items():
        pc = perp.get(t)
        if pc is None or sc <= 0:
            continue
        # fonlama 8 saatlik; o saate ait EN YAKIN gecmis fonlama
        fr = None
        for geri in range(0, 8):
            fr = fund.get(t - geri * 3600000)
            if fr is not None:
                break
        if fr is None:
            continue
        b.append(100.0 * (pc / sc - 1.0))     # basis %
        f.append(fr)                           # funding %/8s
    if len(b) < 150:
        yok += 1
        continue
    satir.append((s, b, f))
    print("  %-14s N=%-5d basis ort %+.4f%%  std %.4f   funding ort %+.4f"
          % (s, len(b), statistics.mean(b), statistics.pstdev(b), statistics.mean(f)),
          flush=True)
    time.sleep(0.15)

print("\nkullanilan sembol %d  ·  spotta yok/kisa %d  ·  dosya hatasi %d"
      % (len(satir), yok, hata))
json.dump([{"sym": s, "basis": b, "funding": f} for s, b, f in satir],
          open(os.path.join(HERE, "yoklama.json"), "w"))
print("YAZILDI -> scratchpad/basis/yoklama.json")
