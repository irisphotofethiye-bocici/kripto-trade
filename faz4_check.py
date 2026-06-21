#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAZ 4 günlük sağlık kontrolü.
Ölçer: (1) veri doğruluğu = Binance vs CoinGecko fiyat farkı (<%0.5 -> PASS),
       (2) erişilebilirlik = Binance spot+fapi ulaşılabilir mi.
Anahtarsız core; CoinGecko için key kripto-config.json'dan okunur (chat'e girmez).
Kullanım: python faz4_check.py
"""
import json, os, urllib.request, datetime

SPOT = "https://api.binance.com"
FAPI = "https://fapi.binance.com"
HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(HERE, "kripto-config.json")
SYMS = {"BTC": "bitcoin", "ETH": "ethereum", "LINK": "chainlink",
        "SOL": "solana", "PENGU": "pudgy-penguins"}

def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "faz4/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

def main():
    cfg = json.load(open(CFG, encoding="utf-8"))
    key = cfg.get("coingecko_demo_key", "")
    binance_ok, fapi_ok, cg_ok = True, True, bool(key)
    try:
        get(f"{SPOT}/api/v3/ping")
    except Exception:
        binance_ok = False
    try:
        get(f"{FAPI}/fapi/v1/premiumIndex?symbol=BTCUSDT")
    except Exception:
        fapi_ok = False
    cg = {}
    if key:
        try:
            ids = ",".join(SYMS.values())
            cg = get(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd",
                     {"x-cg-demo-api-key": key, "User-Agent": "faz4/1.0"})
        except Exception:
            cg_ok = False
    rows, max_div = [], 0.0
    for sym, cid in SYMS.items():
        try:
            b = float(get(f"{SPOT}/api/v3/ticker/price?symbol={sym}USDT")["price"])
        except Exception:
            rows.append((sym, None, None, None)); continue
        c = cg.get(cid, {}).get("usd") if cg else None
        div = abs(b - c) / b * 100 if c else None
        if div is not None:
            max_div = max(max_div, div)
        rows.append((sym, b, c, div))
    veri_pass = (max_div < 0.5) and cg_ok
    erisim_pass = binance_ok and fapi_ok
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"=== FAZ4 kontrol {now} ===")
    print(f"Binance spot: {'OK' if binance_ok else 'ERISILEMEDI'} | "
          f"Binance fapi: {'OK' if fapi_ok else 'ERISILEMEDI'} | "
          f"CoinGecko: {'OK' if cg_ok else 'YOK/HATA'}")
    for sym, b, c, div in rows:
        ds = ("%.3f%%" % div) if div is not None else "-"
        print(f"  {sym:6} Binance={b} CoinGecko={c} fark={ds}")
    print(f"Max fark: {max_div:.3f}%  ->  VERI_DOGRULUGU: {'PASS' if veri_pass else 'FAIL'} (esik <0.5% + CoinGecko OK)")
    print(f"ERISIM: {'PASS' if erisim_pass else 'FAIL'}")

if __name__ == "__main__":
    main()
