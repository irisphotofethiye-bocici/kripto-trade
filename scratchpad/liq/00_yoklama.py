#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COINALYZE LIKIDASYON — KAPSAM YOKLAMASI (olcum DEGIL)

Ne kadar geriye? Kac sembol? Toplu cagri calisiyor mu? Hiz siniri?
Bu bir ON-KAYIT DEGIL — tasarim parametresi topluyor, hipotez SINAMIYOR.

Ucretsiz uc (40 cagri/dk). Apify KULLANILMIYOR (o ucretli).
SALT-OKUNUR. Bot dosyalarina ve arsiv/coinalyze_liq_log.jsonl'e yazim YOK.
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


def _key():
    k = (json.load(io.open(os.path.join(KOK, "kripto-config.json"),
                           encoding="utf-8")).get("coinalyze_api_key") or "").strip()
    if not k:
        sys.exit("coinalyze_api_key BOS")
    return k


def get(path, params):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"api_key": _key(),
                                               "User-Agent": "kripto-yoklama/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        return None, "HTTP %d %s" % (e.code, e.read()[:120].decode("utf-8", "replace"))
    except Exception as e:
        return None, str(e)[:120]


def gun_once(n):
    return int((dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=n)).timestamp())


def main():
    print("=" * 92)
    print("COINALYZE LIKIDASYON — KAPSAM YOKLAMASI (hipotez sinanmaz)")
    print("=" * 92)

    print("\n### 1) PIYASA LISTESI — Binance perp sembolleri")
    mk, err = get("/future-markets", {})
    if err:
        print("   HATA: %s" % err)
        return
    binance = [m for m in mk if str(m.get("exchange", "")).upper() == "A"
               and m.get("is_perpetual")]
    print("   toplam market %d · Binance perp %d" % (len(mk), len(binance)))
    print("   ornek: %s" % json.dumps(binance[0], ensure_ascii=False)[:220])
    semboller = [m["symbol"] for m in binance]
    print("   ilk 6 sembol: %s" % ", ".join(semboller[:6]))

    print("\n### 2) GECMIS NE KADAR GERIYE? (BTCUSDT_PERP.A, 1hour)")
    hedef = "BTCUSDT_PERP.A"
    for gun in (7, 30, 90, 180, 365, 730):
        d, err = get("/liquidation-history",
                     {"symbols": hedef, "interval": "1hour", "convert_to_usd": "true",
                      "from": gun_once(gun), "to": int(time.time())})
        if err:
            print("   %4d gun -> HATA %s" % (gun, err))
            continue
        h = (d[0].get("history") if d else []) or []
        if not h:
            print("   %4d gun -> veri YOK" % gun)
            continue
        t0 = dt.datetime.fromtimestamp(h[0]["t"], dt.timezone.utc)
        t1 = dt.datetime.fromtimestamp(h[-1]["t"], dt.timezone.utc)
        print("   %4d gun -> N=%5d  %s .. %s  (gercek kapsam %.0f gun)"
              % (gun, len(h), t0.strftime("%Y-%m-%d"), t1.strftime("%Y-%m-%d"),
                 (t1 - t0).total_seconds() / 86400))
        time.sleep(1.6)

    print("\n### 3) TOPLU CAGRI — kac sembol tek istekte?")
    for n in (2, 5, 10, 20):
        grup = ",".join(semboller[:n])
        d, err = get("/liquidation-history",
                     {"symbols": grup, "interval": "1hour", "convert_to_usd": "true",
                      "from": gun_once(3), "to": int(time.time())})
        if err:
            print("   %2d sembol -> HATA %s" % (n, err))
        else:
            print("   %2d sembol -> %d seri donduU" % (n, len(d or [])))
        time.sleep(1.6)

    print("\n### 4) ALAN SEMASI")
    d, err = get("/liquidation-history",
                 {"symbols": hedef, "interval": "1hour", "convert_to_usd": "true",
                  "from": gun_once(2), "to": int(time.time())})
    if not err and d:
        h = d[0]["history"]
        print("   seri alanlari : %s" % ", ".join(sorted(d[0].keys())))
        print("   kayit alanlari: %s" % ", ".join(sorted(h[0].keys())))
        print("   son 3 kayit:")
        for x in h[-3:]:
            print("      %s  l=%.0f  s=%.0f"
                  % (dt.datetime.fromtimestamp(x["t"], dt.timezone.utc).strftime("%m-%d %H:%M"),
                     x.get("l", 0), x.get("s", 0)))

    print("\n" + "=" * 92)
    print("Salt-okuma. Bot dosyalarina ve arsiv kutugune yazim: YOK")


if __name__ == "__main__":
    main()
