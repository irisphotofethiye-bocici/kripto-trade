#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EN IYIMSER SENARYO: her pozisyon BTC'nin YANINDA olsaydi? SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections, datetime as dt, os, statistics as stt

ONB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "btc_1h_onbellek.json")
BTC = {int(k): v for k, v in json.load(open(ONB)).items()}


def btc_at(ms):
    for d in (0, 3600000, -3600000, 7200000, -7200000):
        if ms + d in BTC:
            return BTC[ms + d]
    return None


for ad, f in (("testbot", "testbot_islemler.jsonl"), ("defter2", "defter2_islemler.jsonl")):
    K = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    pnl, meta = collections.defaultdict(float), {}
    for r in K:
        pnl[r["id"]] += float(r.get("sonuc_usdt") or 0)
        if not r.get("kismi"):
            meta[r["id"]] = r
    kova = collections.defaultdict(list)
    for i, m in meta.items():
        kap = dt.datetime.strptime(m["ts"], "%Y-%m-%d %H:%M:%S")
        gir = kap - dt.timedelta(hours=float(m.get("tutma_saat") or 0))
        b0 = btc_at(int(gir.timestamp() // 3600 * 3600 * 1000))
        b1 = btc_at(int(kap.timestamp() // 3600 * 3600 * 1000))
        if not b0 or not b1:
            continue
        btc = 100.0 * (b1 - b0) / b0
        if abs(btc) < 0.25:
            k = "YATAY"
        elif (btc > 0 and m["yon"] == "SHORT") or (btc < 0 and m["yon"] == "LONG"):
            k = "TERS"
        else:
            k = "AYNI"
        kova[k].append(pnl[i])
    n = sum(len(v) for v in kova.values())
    ger = sum(sum(v) for v in kova.values())
    ort_ayni = stt.mean(kova["AYNI"]) if kova["AYNI"] else 0
    print("=" * 88)
    print("%s   gercek toplam %+.2f   (N=%d poz)" % (ad.upper(), ger, n))
    print("=" * 88)
    print("  senaryo 1 — TERS olanlar HIC ACILMASAYDI      : %+9.2f"
          % (ger - sum(kova["TERS"])))
    print("  senaryo 2 — TERS olanlar YATAY gibi olsaydi   : %+9.2f"
          % (ger - sum(kova["TERS"]) + len(kova["TERS"]) * (stt.mean(kova["YATAY"]) if kova["YATAY"] else 0)))
    print("  senaryo 3 — HER pozisyon BTC'nin YANINDA (en iyimsel) : %+9.2f"
          % (n * ort_ayni))
    print("     (AYNI kovasinin gozlenen ortalamasi %+.2f $/poz)" % ort_ayni)
    print("  -> en iyimser senaryo bile acigi kapatiyor mu: %s"
          % ("EVET" if n * ort_ayni > 0 and ger < 0 and n * ort_ayni >= -0 else "—"))
    print("     gercek %+.2f  ->  en iyimser %+.2f   fark %+.2f"
          % (ger, n * ort_ayni, n * ort_ayni - ger))
    print("")
