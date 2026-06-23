#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIFY LIKIDASYON HARITASI — D2 (ON-DEMAND, ucretli).
CoinGlass liq-heatmap actor -> en buyuk likidasyon MIKNATIS seviyeleri (yukari/asagi).
Maliyet: ~0.01 USD/kosu (Apify FREE plan $5 tavan). Token: kripto-config.json -> apify_token.
Kullanim: python apify_liq.py --symbol BTC [--interval 24h]
Sadece derin analiz/pozisyonda calistir (her quick scan'de DEGIL).
"""
import json, os, sys, argparse, urllib.request
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ACTOR = "api_merge~coinglass-liquidation-heatmap"

def cfg():
    return json.load(open(os.path.join(HERE, "kripto-config.json"), encoding="utf-8"))

def binance_price(sym):
    try:
        u = f"https://api.binance.com/api/v3/ticker/price?symbol={sym}USDT"
        return float(json.load(urllib.request.urlopen(
            urllib.request.Request(u, headers={"User-Agent": "x"}), timeout=10))["price"])
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--interval", default="24h", help="12h,24h,48h,3d,1w,2w,1mo,3mo")
    ap.add_argument("--model", default="model1")
    a = ap.parse_args()
    tok = cfg().get("apify_token", "")
    if not tok:
        print(json.dumps({"error": "apify_token bos (kripto-config.json)"}, ensure_ascii=False)); return
    sym = a.symbol.upper()
    body = json.dumps({"symbol": sym, "model": a.model, "interval": a.interval}).encode()
    req = urllib.request.Request(
        f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items",
        data=body, headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}, method="POST")
    try:
        res = json.load(urllib.request.urlopen(req, timeout=180))
    except Exception as e:
        print(json.dumps({"error": f"Apify kosu hatasi: {str(e)[:90]}"}, ensure_ascii=False)); return
    if not (isinstance(res, list) and res and res[0].get("success")):
        print(json.dumps({"error": "veri gelmedi", "ham": str(res)[:120]}, ensure_ascii=False)); return
    o = res[0]
    y, data = o.get("y_axis", []), o.get("liquidation_leverage_data", [])
    agg = [0.0] * len(y)
    for row in data:
        try:
            yi = int(row[1])
            if 0 <= yi < len(y):
                agg[yi] += float(row[2] or 0)
        except Exception:
            pass
    px = binance_price(sym) or (sum(y) / len(y) if y else 0)
    top = sorted(range(len(y)), key=lambda i: -agg[i])[:12]
    ust = sorted([(round(y[i], 6), round(agg[i])) for i in top if y[i] > px], key=lambda t: t[0])[:5]
    alt = sorted([(round(y[i], 6), round(agg[i])) for i in top if y[i] < px], key=lambda t: -t[0])[:5]
    out = {
        "symbol": sym, "interval": a.interval, "fiyat": round(px, 6) if px else None,
        "miknatis_yukari": [{"fiyat": p, "buyukluk": v} for p, v in ust],
        "miknatis_asagi": [{"fiyat": p, "buyukluk": v} for p, v in alt],
        "kaynak": "Apify CoinGlass liq-heatmap", "maliyet_usd": 0.01,
        "not": "Buyuk kume = likidite magnet / stop-hunt bolgesi. ON-DEMAND, her kosu ~1 cent.",
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
