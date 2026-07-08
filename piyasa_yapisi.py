#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIYASA YAPISI - BTC.D / USDT.D dominans + alt/BTC goreli guc (altcoin rotasyon cercevesi).
Boga/yukselis doneminde alt SECIMI + altseason ZAMANLAMASI icin (kullanici teknigi, 2026-06-25,
deneyimle dogrulanmis). "Alt USD'de yesil ama BTC'ye karsi kirmizi" tuzagini cozer:
gercek alfa = alt'in BTC'yi GECMESI (alt/BTC ^), sadece BTC betasi degil.

- Dominans: CoinGecko /global (BTC.D, ETH.D, USDT.D, stable toplam, OTHERS)
- alt/BTC: Binance gunluk klines -> alt/BTC oran degisimi (24s/7g/30g); SURDURULEBILIR (7-30g) trend
  = gercek liderlik (3 SAATLIK AYRISMA'dan FARKLI; o gurultu/negatif-edge cikti).
- Append-only log (piyasa_yapisi_log.jsonl) -> dominans TRENDI: USDT.D kiriliyor mu, BTC.D donuyor mu.

Deterministik, 0 token, anahtarsiz (CoinGecko demo key config'ten okunur).
UYARI: REJIM/yapi gostergesi; tek basina al/sat SINYALI degil. En guclu boga/donus doneminde.
Kullanim: python piyasa_yapisi.py [--n 45] [--min_vol 15] [--tf 7g]
"""
import json, os, sys, argparse, datetime
import evren  # evren/eleme TEK kaynak (m7 drift duzeltmesi 2026-07-02); stable/gold listeleri orada

HERE = os.path.dirname(os.path.abspath(__file__))
SP = "https://api.binance.com"

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")


def get(u, headers=None):
    return evren.get(u, headers=headers or {"User-Agent": "piyasa/1.0"}, timeout=25)


def cg_key():
    try:
        return json.load(open(os.path.join(HERE, "kripto-config.json"), encoding="utf-8")).get("coingecko_demo_key", "")
    except Exception:
        return ""


def dominance(key):
    """CoinGecko global -> dominans yuzdeleri + toplam mcap. Transient rate-limit/timeout icin retry."""
    import time
    d = None
    for attempt in range(3):
        try:
            d = get("https://api.coingecko.com/api/v3/global",
                    {"x-cg-demo-api-key": key, "User-Agent": "piyasa/1.0"})["data"]
            break
        except Exception:
            if attempt < 2:
                time.sleep(5)
    if d is None:
        return None
    mc = d.get("market_cap_percentage", {})
    btc_d = mc.get("btc", 0.0); eth_d = mc.get("eth", 0.0)
    stable_d = sum(v for k, v in mc.items() if k.upper() in evren.STABLES)
    usdt_d = mc.get("usdt", 0.0)
    others = max(0.0, 100 - btc_d - eth_d - stable_d)
    return {"total": d.get("total_market_cap", {}).get("usd", 0),
            "chg24": d.get("market_cap_change_percentage_24h_usd", 0),
            "btc_d": btc_d, "eth_d": eth_d, "usdt_d": usdt_d,
            "stable_d": stable_d, "others": others}


def universe(key, min_vol, n):
    """Likit + kripto USDT spot havuzu - ortak modul evren.py (eleme kurallari tek yerde)."""
    cryptos = evren.cg_universe(key)
    return evren.binance_pool("spot", min_vol, None, cryptos)[:n], cryptos


def daily(sym, n=31):
    try:
        d = get(f"{SP}/api/v3/klines?symbol={sym}USDT&interval=1d&limit={n}")
        return [float(k[4]) for k in d]
    except Exception:
        return None


def rel(ac, bc, k):
    """alt/BTC oran degisimi son k bar (yuzde)."""
    if len(ac) <= k or len(bc) <= k or bc[-1-k] == 0 or ac[-1-k] == 0:
        return None
    rn = ac[-1] / bc[-1]; rp = ac[-1-k] / bc[-1-k]
    return (rn / rp - 1) * 100 if rp else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=45, help="havuz buyuklugu (hacme gore)")
    ap.add_argument("--min_vol", type=float, default=15.0, help="min 24s hacim (milyon $)")
    ap.add_argument("--tf", default="7g", choices=["24s", "7g", "30g"], help="siralama timeframe")
    a = ap.parse_args()
    key = cg_key()

    dom = dominance(key)
    pool, cryptos = universe(key, a.min_vol, a.n)
    bc = daily("BTC", 31)
    if not bc:
        print("BTC verisi alinamadi."); return

    KMAP = {"24s": 1, "7g": 7, "30g": 30}
    rows = []
    for base, qv, chg in pool:
        if base == "BTC":
            continue
        ac = daily(base, 31)
        if not ac or len(ac) < 2:
            continue
        r24 = rel(ac, bc, 1); r7 = rel(ac, bc, 7); r30 = rel(ac, bc, 30)
        usd7 = (ac[-1] / ac[-8] - 1) * 100 if len(ac) >= 8 else None
        mc = (cryptos.get(base) or {}).get("mcap")
        rows.append({"sym": base, "r24": r24, "r7": r7, "r30": r30, "usd7": usd7,
                     "mcap": mc, "vol": qv})
    ksel = a.tf
    rows = [r for r in rows if r["r%s" % ({"24s": "24", "7g": "7", "30g": "30"}[ksel])] is not None]
    rk = {"24s": "r24", "7g": "r7", "30g": "r30"}[ksel]
    rows.sort(key=lambda r: -(r[rk] if r[rk] is not None else -999))

    def fmt(v):
        return ("%+.1f%%" % v) if v is not None else "   -"

    def mcs(v):
        return ("$%.0fM" % (v / 1e6)) if v else "?"

    print("=== PIYASA YAPISI (BTC.D / USDT.D / alt-BTC) ===")
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print("(%s)\n" % ts)

    if dom:
        print("## DOMINANS")
        print("Toplam kripto mcap: $%.2fT (24s %+.1f%%)" % (dom["total"] / 1e12, dom["chg24"]))
        print("BTC.D  %5.1f%%   ETH.D %4.1f%%   USDT.D %4.2f%%   Stable %5.2f%%   OTHERS %4.1f%%"
              % (dom["btc_d"], dom["eth_d"], dom["usdt_d"], dom["stable_d"], dom["others"]))

    # --- TREND LOGU (append-only) + onceki ile delta ---
    breadth = (sum(1 for r in rows if (r[rk] or 0) > 0) / len(rows) * 100) if rows else 0
    logf = os.path.join(HERE, "piyasa_yapisi_log.jsonl")
    prev = None
    try:
        if os.path.exists(logf):
            lines = [l for l in open(logf, encoding="utf-8").read().splitlines() if l.strip()]
            if lines:
                prev = json.loads(lines[-1])
    except Exception:
        pass
    if dom:
        try:
            with open(logf, "a", encoding="utf-8") as f:
                f.write(json.dumps({"ts": ts, "btc_d": round(dom["btc_d"], 2), "eth_d": round(dom["eth_d"], 2),
                                    "usdt_d": round(dom["usdt_d"], 2), "stable_d": round(dom["stable_d"], 2),
                                    "others": round(dom["others"], 2), "breadth_%s" % ksel: round(breadth, 1),
                                    "total": dom["total"]}, ensure_ascii=False) + "\n")
        except Exception:
            pass

    print("\n## REJIM / ALTSEASON GOSTERGESI")
    if dom:
        sd = "YUKSEK (para kenarda=risk-off)" if dom["stable_d"] >= 9 else ("DUSUK (para girmis=risk-on)" if dom["stable_d"] < 6 else "orta")
        bd = "YUKSEK (alt zayif)" if dom["btc_d"] >= 54 else ("DUSUK (altseason)" if dom["btc_d"] < 45 else "orta")
        print("Stable dominans %.2f%% -> %s" % (dom["stable_d"], sd))
        print("BTC.D %.1f%% -> %s" % (dom["btc_d"], bd))
    print("Alt breadth (BTC'yi gecen, %s): %.0f%% (%d/%d coin)"
          % (ksel, breadth, sum(1 for r in rows if (r[rk] or 0) > 0), len(rows)))
    if prev and dom:
        d_btc = dom["btc_d"] - prev.get("btc_d", dom["btc_d"])
        d_usdt = dom["usdt_d"] - prev.get("usdt_d", dom["usdt_d"])
        print("TREND (onceki kayit %s): BTC.D %+.2f  USDT.D %+.2f" % (prev.get("ts", "?"), d_btc, d_usdt))
        print("  -> Boga-donus icin: USDT.D DUSER + BTC.D tepe yapip DONER + alt breadth ARTAR")
    else:
        print("(trend icin 2. calismadan sonra delta gosterilir; log: piyasa_yapisi_log.jsonl)")
        print("Boga-donus checklist: USDT.D kirilir + BTC.D tepe+doner + alt/BTC breakout = altseason yesil isik")

    head = "  %-8s %8s %8s %8s %9s %8s" % ("COIN", "a/BTC24s", "a/BTC7g", "a/BTC30g", "USD7g", "mcap")
    lead = [r for r in rows if (r[rk] or 0) > 0][:14]
    lag = [r for r in rows if (r[rk] or 0) <= 0]
    lag.sort(key=lambda r: (r[rk] if r[rk] is not None else 0))
    lag = lag[:12]

    def ptag(r):
        # parabolik/blow-off: saglikli liderden (AAVE +%22) ayir -> KACIN tipi
        if (r["r7"] or 0) > 50 or (r["r30"] or 0) > 120:
            return "  PARABOLIK/KACIN"
        return ""

    print("\n## ALT/BTC LIDERLER - BTC'yi geciyor (gercek guc, %s sirali)" % ksel)
    print(head)
    for r in lead:
        print("  %-8s %8s %8s %8s %9s %8s%s" % (r["sym"], fmt(r["r24"]), fmt(r["r7"]), fmt(r["r30"]), fmt(r["usd7"]), mcs(r["mcap"]), ptag(r)))

    print("\n## ALT/BTC GERIDE - BTC-betasi tuzagi / zayif (en zayif 12)")
    print(head)
    for r in lag:
        print("  %-8s %8s %8s %8s %9s %8s" % (r["sym"], fmt(r["r24"]), fmt(r["r7"]), fmt(r["r30"]), fmt(r["usd7"]), mcs(r["mcap"])))

    print("\nNot: REJIM gostergesi, sinyal DEGIL. 'BTC'yi gecen' = gercek alfa (USD-tuzagi degil).")
    print("Sustained (7-30g) alt/BTC = liderlik; 3h rel-guc (AYRISMA) gurultu/negatif-edge'di.")


if __name__ == "__main__":
    main()
