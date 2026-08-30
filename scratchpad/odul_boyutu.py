#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ODULUN UST SINIRI — 'mukemmel rejim donus dedektoru' ne kadar kurtarirdi?
Pozisyon TUTMA suresi boyunca BTC ne yapti, bot hangi yondeydi. SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections, datetime as dt, urllib.request, os

HERE = os.path.dirname(os.path.abspath(__file__))
ONB = os.path.join(HERE, "btc_1h_onbellek.json")


def btc_serisi():
    if os.path.exists(ONB):
        return {int(k): v for k, v in json.load(open(ONB)).items()}
    out, son = {}, int(dt.datetime(2026, 7, 20).timestamp() * 1000)
    while True:
        u = ("https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT"
             "&interval=1h&limit=1000&startTime=%d" % son)
        with urllib.request.urlopen(u, timeout=25) as r:
            d = json.loads(r.read())
        if not d:
            break
        for m in d:
            out[m[0]] = float(m[4])
        son = d[-1][0] + 3600000
        if len(d) < 1000:
            break
    json.dump({str(k): v for k, v in out.items()}, open(ONB, "w"))
    return out


BTC = btc_serisi()
print("BTC 1sa mum: %d  (%s .. %s)" % (
    len(BTC), dt.datetime.utcfromtimestamp(min(BTC) / 1000),
    dt.datetime.utcfromtimestamp(max(BTC) / 1000)))


def saat(ts):
    return int(dt.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").timestamp() // 3600 * 3600 * 1000)


def btc_at(ms):
    for d in (0, 3600000, -3600000, 7200000, -7200000):
        if ms + d in BTC:
            return BTC[ms + d]
    return None


for ad, f in (("testbot", "testbot_islemler.jsonl"), ("defter2", "defter2_islemler.jsonl"),
              ("defter3", "defter3_islemler.jsonl")):
    K = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    pnl = collections.defaultdict(float)
    meta = {}
    for r in K:
        pnl[r["id"]] += float(r.get("sonuc_usdt") or 0)
        if not r.get("kismi"):
            meta[r["id"]] = r
    g = collections.defaultdict(lambda: [0, 0.0])
    atlanan = 0
    for i, m in meta.items():
        kap = dt.datetime.strptime(m["ts"], "%Y-%m-%d %H:%M:%S")
        gir = kap - dt.timedelta(hours=float(m.get("tutma_saat") or 0))
        b0 = btc_at(int(gir.timestamp() // 3600 * 3600 * 1000))
        b1 = btc_at(int(kap.timestamp() // 3600 * 3600 * 1000))
        if not b0 or not b1:
            atlanan += 1
            continue
        btc = 100.0 * (b1 - b0) / b0
        if abs(btc) < 0.25:                       # BTC yatay — ayrima girmez
            k = "BTC YATAY (<%0,25)"
        elif (btc > 0 and m["yon"] == "SHORT") or (btc < 0 and m["yon"] == "LONG"):
            k = "TERS YONDE  (BTC'ye karsi)"
        else:
            k = "AYNI YONDE  (BTC ile)"
        g[k][0] += 1
        g[k][1] += pnl[i]
    tot = sum(v[1] for v in g.values())
    print("")
    print("=" * 82)
    print("%s   toplam %+.2f   (BTC verisi yok: %d poz)" % (ad.upper(), tot, atlanan))
    print("=" * 82)
    for k in sorted(g, key=lambda x: g[x][1]):
        v = g[k]
        print("  %-26s %4d poz (%%%4.1f)   %+9.2f   ort %+7.2f"
              % (k, v[0], 100.0 * v[0] / sum(x[0] for x in g.values()), v[1], v[1] / v[0]))
    ters = g.get("TERS YONDE  (BTC'ye karsi)", [0, 0.0])
    print("  -> TERS yondeki tum pozisyonlar HIC ACILMASAYDI: %+.2f  (fark %+.2f)"
          % (tot - ters[1], -ters[1]))
