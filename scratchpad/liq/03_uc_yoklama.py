#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COINALYZE — HANGI UCLAR VAR? (olcum DEGIL, envanter)

Soru: Coinalyze'de liqmap / isi haritasi var mi? Yoksa ne var?
Ucretsiz. Apify KULLANILMIYOR. SALT-OKUNUR.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, sys, time, datetime as dt
import urllib.request, urllib.parse, urllib.error

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = "https://api.coinalyze.net/v1"
SYM = "BTCUSDT_PERP.A"


def _key():
    return (json.load(io.open(os.path.join(KOK, "kripto-config.json"),
                              encoding="utf-8")).get("coinalyze_api_key") or "").strip()


def dene(path, params, ad):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"api_key": _key(),
                                               "User-Agent": "kripto-envanter/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(r.read().decode("utf-8"))
        if isinstance(d, list):
            ozet = "liste, %d oge" % len(d)
            ic = json.dumps(d[0], ensure_ascii=False)[:150] if d else "(bos)"
        else:
            ozet = "obje"
            ic = json.dumps(d, ensure_ascii=False)[:150]
        print("   VAR   %-30s %-16s %s" % (ad, ozet, ic))
        return d
    except urllib.error.HTTPError as e:
        print("   YOK   %-30s HTTP %d" % (ad, e.code))
    except Exception as e:
        print("   YOK   %-30s %s" % (ad, str(e)[:60]))
    return None


def main():
    print("=" * 100)
    print("COINALYZE UC ENVANTERI — liqmap var mi?")
    print("=" * 100)
    simdi = int(time.time())
    frm = simdi - 3 * 86400

    print("\n### ANLIK UCLAR")
    for p, ad in (("/open-interest", "open-interest"),
                  ("/funding-rate", "funding-rate"),
                  ("/predicted-funding-rate", "predicted-funding")):
        dene(p, {"symbols": SYM}, ad)
        time.sleep(4)

    print("\n### GECMIS UCLAR")
    for p, ad in (("/open-interest-history", "open-interest-history"),
                  ("/funding-rate-history", "funding-rate-history"),
                  ("/liquidation-history", "liquidation-history"),
                  ("/long-short-ratio-history", "long-short-ratio-history"),
                  ("/ohlcv-history", "ohlcv-history")):
        dene(p, {"symbols": SYM, "interval": "1hour", "from": frm, "to": simdi}, ad)
        time.sleep(4)

    print("\n### LIQMAP / ISI HARITASI ARANIYOR (beklenen: YOK)")
    for p in ("/liquidation-heatmap", "/liquidation-map", "/liq-heatmap",
              "/heatmap", "/liquidation-levels"):
        dene(p, {"symbols": SYM}, p)
        time.sleep(4)

    print("\n" + "=" * 100)
    print("Salt-okuma · Apify cagrisi: YOK")


if __name__ == "__main__":
    main()
