#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPOT saatlik kapanislari indirir (2 yil, 357 sembol).

🔴 CLAUDE.md KURALI: arsive yazan indirici (a) var olani OKUR, (b) zaman
damgasina gore BIRLESTIRIR, (c) sonuc eskisinden KISAysa HATA firlatir.
2026-08-24'te bu kural olmadigi icin 58 sembolde veri KALICI kayboldu.

Yalnizca (t, c) saklanir -> dosya kucuk. Sürdürülebilir: tekrar cagrilabilir.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "spot_1h")
os.makedirs(OUT, exist_ok=True)
SEM  = json.load(open(os.path.join(HERE, "semboller.json"), encoding="utf-8"))
BASLA = 1719792000000          # ~2024-07-01, perp gecmisini kapsar
URL = ("https://api.binance.com/api/v3/klines?symbol=%sUSDT&interval=1h"
       "&startTime=%d&limit=1000")


def cek(sym, t0):
    for deneme in range(5):
        try:
            with urllib.request.urlopen(URL % (sym, t0), timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (418, 429):
                time.sleep(10 * (deneme + 1)); continue
            if e.code == 400:
                return []
            time.sleep(2)
        except Exception:
            time.sleep(3)
    raise RuntimeError("cekilemedi: %s" % sym)


def sembol(sym):
    p = os.path.join(OUT, sym + ".json")
    eski = []
    if os.path.exists(p):
        try:
            eski = json.load(open(p, encoding="utf-8"))
        except Exception:
            eski = []
    var = {int(x["t"]): float(x["c"]) for x in eski}
    t0 = (max(var) + 3600000) if var else BASLA
    ekle = 0
    while True:
        d = cek(sym, t0)
        if not d:
            break
        for x in d:
            t = int(x[0])
            if t not in var:
                var[t] = float(x[4]); ekle += 1
        yeni = int(d[-1][0]) + 3600000
        if yeni <= t0 or len(d) < 1000:
            break
        t0 = yeni
        time.sleep(0.08)
    yeni_liste = [{"t": t, "c": var[t]} for t in sorted(var)]
    # (c) SONUC ESKISINDEN KISA OLAMAZ
    if len(yeni_liste) < len(eski):
        raise RuntimeError("KISALMA %s: %d -> %d" % (sym, len(eski), len(yeni_liste)))
    if ekle or not os.path.exists(p):
        tmp = p + ".tmp"
        json.dump(yeni_liste, open(tmp, "w"))
        os.replace(tmp, p)                       # ATOMIK
    return len(yeni_liste), ekle


print("SPOT INDIRME — %d sembol" % len(SEM), flush=True)
ok = hata = 0
for i, s in enumerate(SEM):
    try:
        n, e = sembol(s)
        ok += 1
    except Exception as ex:
        hata += 1
        print("   HATA %s: %s" % (s, str(ex)[:70]), flush=True)
    if (i + 1) % 20 == 0:
        boy = sum(os.path.getsize(os.path.join(OUT, f))
                  for f in os.listdir(OUT) if f.endswith(".json"))
        print("   %3d/%d  ok=%d hata=%d  ·  %.0f MB"
              % (i + 1, len(SEM), ok, hata, boy / 1048576), flush=True)

print("\nBITTI  ok=%d hata=%d  dosya=%d" % (ok, hata, len(os.listdir(OUT))))
