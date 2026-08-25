#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOZUK FONLAMA PENCERESINI UCTAN YENIDEN CEK — kesin cozum.

NEDEN: veri_guncelle.py:97 `*100`'u atlamisti; 2026-08-12 civarindan itibaren
   KESIR kayit yazildi. `fonlama_onar.py` (sezgisel sinir arama) dosyalarin
   cogunu duzeltti ama sinirini guvenle belirleyemedigi dosyalari YEDEGE
   dondurdu -> bir kismi hala bozuk.

   Sezgisel sinir aramayi BIRAKIYORUZ. Fonlama KALICI sinif veridir
   (CLAUDE.md): /fapi/v1/fundingRate istendigi an 2 yil geriye doner.
   Bozuk pencereyi silip UCTAN yeniden almak kesin ve esiksizdir.

YONTEM: bozuk dosyalar tespit edilir (orta blok, iki komsusuna gore 20+ kat
   kucuk) -> [08-08, 08-23] araligi ATILIR -> uctan yeniden indirilir
   (*100 UYGULANIR) -> zaman damgasina gore BIRLESTIRILIR.
   ⚠️ CLAUDE.md: "sonuc eskisinden KISAysa hata firlat" — uygulandi.

--kuru : indirme yok, yalniz tespit.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, sys, time, datetime, urllib.request, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
FON = os.path.join(HERE, "funding_gecmis")
FAPI = "https://fapi.binance.com"
BEKLE = 0.9
A = int(datetime.datetime(2026, 8, 8, 0, 0).timestamp() * 1000)
B = int(datetime.datetime(2026, 8, 23, 0, 0).timestamp() * 1000)
KURU = "--kuru" in sys.argv


def get(url, deneme=4):
    for k in range(deneme):
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                return json.loads(r.read().decode())
        except Exception:
            time.sleep(1.5 * (k + 1))
    return None


def med(v):
    z = [abs(x) for x in v if x]
    return sx.median(z) if len(z) >= 5 else None


bozuk = []
for ad in sorted(os.listdir(FON)):
    if not ad.endswith(".json"): continue
    with open(os.path.join(FON, ad), encoding="utf-8") as f: d = json.load(f)
    mo = med([x["r"] for x in d if x["t"] < A])
    mm = med([x["r"] for x in d if A <= x["t"] < B])
    ms = med([x["r"] for x in d if x["t"] >= B])
    if mo is None or mm is None: continue
    if (mo / mm >= 20) and (ms is None or ms / mm >= 20):
        bozuk.append(ad[:-5])

print("BOZUK PENCERESI OLAN DOSYA: %d" % len(bozuk))
if KURU or not bozuk:
    print("  " + ", ".join(bozuk[:20]) + (" ..." if len(bozuk) > 20 else ""))
    raise SystemExit(0)

ok = hata = 0
t0 = time.time()
for n, sym in enumerate(bozuk, 1):
    yol = os.path.join(FON, sym + ".json")
    with open(yol, encoding="utf-8") as f: d = json.load(f)
    n0 = len(d)
    yeni, t = [], A
    basarili = True
    while t < B:
        r = get("%s/fapi/v1/fundingRate?symbol=%sUSDT&startTime=%d&endTime=%d&limit=1000"
                % (FAPI, sym, t, B))
        if r is None:
            basarili = False; break
        if not r: break
        yeni += [{"t": int(x["fundingTime"]), "r": float(x["fundingRate"]) * 100} for x in r]
        ileri = int(r[-1]["fundingTime"]) + 1
        if ileri <= t: break
        t = ileri
        time.sleep(BEKLE)
        if len(r) < 1000: break
    if not basarili or not yeni:
        hata += 1; continue
    kalan = [x for x in d if not (A <= x["t"] < B)]
    birlesik = {x["t"]: x for x in kalan}
    for x in yeni: birlesik[x["t"]] = x
    son = sorted(birlesik.values(), key=lambda z: z["t"])
    if len(son) < n0 - 2:                       # CLAUDE.md: kisalirsa HATA
        print("  !! %s: sonuc kisaldi (%d -> %d) — YAZILMADI" % (sym, n0, len(son)))
        hata += 1; continue
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(son, f)
    os.replace(tmp, yol)
    ok += 1
    if n % 15 == 0:
        print("  [%d/%d] %-12s %d kayit · gecen %.0f dk" % (n, len(bozuk), sym, len(son), (time.time()-t0)/60), flush=True)

print("\nBITTI — yenilenen %d · hata %d · sure %.0f dk" % (ok, hata, (time.time()-t0)/60))
