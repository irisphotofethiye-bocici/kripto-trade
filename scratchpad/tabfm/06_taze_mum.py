#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pozisyon sembolleri icin TAZE saatlik mum — AYRI onbellek.

klines_1h_uzun 2026-08-25 06:00'da bitiyor; +24s etiketi son gunleri dusuruyor.
🔴 PAYLASILAN VERI KUMESINE DOKUNULMAZ (CLAUDE.md: indiriciler birlestirmeli,
   ezmemeli). Bu betik AYRI bir onbellege yazar, klines_1h_uzun'a hic dokunmaz.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, time, urllib.request, collections, datetime

HERE  = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(os.path.dirname(HERE))
OUT   = os.path.join(HERE, "taze_mum")
os.makedirs(OUT, exist_ok=True)

R = [json.loads(l) for l in open(os.path.join(PROJE, "testbot_islemler.jsonl"),
                                 encoding="utf-8") if l.strip()]
semboller = sorted({r["sym"] for r in R if r.get("sym")})
print("pozisyon sembolu: %d" % len(semboller))

ok = hata = atla = 0
for i, s in enumerate(semboller):
    p = os.path.join(OUT, s + ".json")
    if os.path.exists(p) and os.path.getsize(p) > 100:
        atla += 1
        continue
    u = ("https://fapi.binance.com/fapi/v1/klines?symbol=%sUSDT&interval=1h&limit=400" % s)
    try:
        with urllib.request.urlopen(u, timeout=60) as r:
            d = json.load(r)
        bar = [{"t": int(x[0]), "c": float(x[4]), "h": float(x[2]), "l": float(x[3])}
               for x in d]
        if len(bar) < 50:
            hata += 1
            continue
        tmp = p + ".tmp"
        json.dump(bar, open(tmp, "w"))
        os.replace(tmp, p)                       # ATOMIK
        ok += 1
    except Exception:
        hata += 1
    if (i + 1) % 25 == 0:
        print("   ... %d/%d  (yeni %d · atlanan %d · hata %d)"
              % (i + 1, len(semboller), ok, atla, hata), flush=True)
    time.sleep(0.12)

print("\nindi %d · zaten vardi %d · hata %d" % (ok, atla, hata))
son = []
for f in os.listdir(OUT):
    if f.endswith(".json"):
        try:
            b = json.load(open(os.path.join(OUT, f)))
            son.append(int(b[-1]["t"]))
        except Exception:
            pass
if son:
    t = datetime.datetime(1970,1,1)+datetime.timedelta(milliseconds=max(son))
    t0 = datetime.datetime(1970,1,1)+datetime.timedelta(milliseconds=min(son))
    print("son bar: %s .. %s UTC  (dosya %d)" % (t0.strftime("%m-%d %H:%M"),
                                                  t.strftime("%m-%d %H:%M"), len(son)))
