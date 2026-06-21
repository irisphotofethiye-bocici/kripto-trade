#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TARAYICI (Avcı / Kademe-1) — Faz 6 çekirdek. DETERMINISTIK, 0 LLM tokeni.
Momentum + trend on-filtresi -> kisa liste. Opus CEO yalniz bu kisa listeyi derin analiz eder (Kademe-2).
Kaynak: Binance 24s + CoinGecko momentum + olcucu coklu-TF/turev. Anahtarsiz core + CoinGecko key (config).
Kullanim: python tarayici.py [--min_vol 25] [--n 10]
"""
import json, os, urllib.request, argparse
import olcucu

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(HERE, "kripto-config.json")
BAD = ("UPUSDT", "DOWNUSDT", "BULLUSDT", "BEARUSDT")
STABLE = {"USDT", "USDC", "FDUSD", "USD1", "TUSD", "DAI", "BUSD"}

def get(u, h=None):
    req = urllib.request.Request(u, headers=h or {"User-Agent": "tarayici/1.0"})
    return json.load(urllib.request.urlopen(req, timeout=30))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min_vol", type=float, default=25.0, help="min 24s hacim (milyon $)")
    ap.add_argument("--n", type=int, default=10, help="kac aday dogrulansin")
    a = ap.parse_args()
    key = json.load(open(CFG, encoding="utf-8")).get("coingecko_demo_key", "")

    # 1) Binance 24s gainers (likit)
    bgain = {}
    for x in get("https://api.binance.com/api/v3/ticker/24hr"):
        s = x["symbol"]
        if not s.endswith("USDT") or any(s.endswith(b) for b in BAD):
            continue
        sym = s[:-4]
        if sym in STABLE:
            continue
        try:
            chg, qv = float(x["priceChangePercent"]), float(x["quoteVolume"])
        except Exception:
            continue
        if qv < a.min_vol * 1e6:
            continue
        bgain[sym] = {"chg24": chg, "vol": qv}

    # 2) CoinGecko momentum (24s VE 7g pozitif = gercek uptrend)
    m = get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc"
            "&per_page=150&page=1&price_change_percentage=24h,7d",
            {"x-cg-demo-api-key": key, "User-Agent": "tarayici/1.0"})
    cgmom = {}
    for c in m:
        d24 = c.get("price_change_percentage_24h_in_currency")
        d7 = c.get("price_change_percentage_7d_in_currency")
        if d24 is not None and d7 is not None and d24 > 0 and d7 > 0:
            cgmom[c["symbol"].upper()] = {"d24": d24, "d7": d7, "rank": c.get("market_cap_rank")}

    # 3) aday havuzu: CG 7g momentum oncelik + binance gainers
    pool = [s for s, _ in sorted(cgmom.items(), key=lambda kv: -kv[1]["d7"])]
    for s in sorted(bgain, key=lambda s: -bgain[s]["chg24"]):
        if s not in pool:
            pool.append(s)
    pool = pool[:a.n]

    tier1, tier2, tier3, avoid = [], [], [], []
    for sym in pool:
        try:
            _, uz = olcucu.mtf_scan(sym)
            ew = olcucu.early_warning(sym)
        except Exception:
            continue  # Binance perp yok -> deterministik tarama disi
        d7 = cgmom.get(sym, {}).get("d7")
        fund, oi = ew.get("funding_pct"), ew.get("oi_24s_degisim_pct")
        rec = (sym, uz, d7, fund, oi)
        if (fund is not None and abs(fund) > 0.1) or (oi is not None and oi > 80):
            avoid.append(rec + (ew["belirtiler"][0],))   # blow-off / asiri funding-OI
        elif uz == "GUCLU_YUKARI":
            tier1.append(rec)
        elif uz == "YUKARI_EGILIM":
            tier2.append(rec)
        else:
            tier3.append(rec)

    def pr(title, rows):
        print(f"\n## {title}")
        for r in rows:
            sym, uz, d7, fund, oi = r[:5]
            d7s = ("+%.0f%%" % d7) if d7 is not None else "-"
            print(f"  {sym:8} {uz:13} 7g={d7s:6} funding={fund} OI24={oi}")

    print("=== TARAYICI (deterministik, 0 token) ===")
    pr("TIER 1 — guclu uptrend (4/4 TF)", tier1)
    pr("TIER 2 — uptrend egilim", tier2)
    pr("TIER 3 — karisik/zayif", tier3)
    print("\n## KACIN (blow-off / asiri funding-OI)")
    for r in avoid:
        print(f"  {r[0]:8} funding={r[3]} OI24={r[4]} -> {r[5]}")
    print("\nNot: kisa liste -> Opus CEO derin analizi (Kademe-2). Bu script LLM kullanmaz.")

if __name__ == "__main__":
    main()
