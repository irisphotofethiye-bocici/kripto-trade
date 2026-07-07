#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TARAYICI (Avcı / Kademe-1) - Faz 6 çekirdek. DETERMINISTIK, 0 LLM tokeni.
Momentum + trend on-filtresi -> kisa liste. CEO yalniz bu kisa listeyi derin analiz eder (Kademe-2).

2026-07-02 revizyonu (M1 duzeltmesi): IKI YONLU tarama (ders#4). Eski hali sadece LONG tier
uretiyordu; ayi rejiminde bu sistemin kendi dersleriyle (ders#3: ana trende karsi long yok)
celisiyordu. Simdi: rejim = evren.btc_rejim(); AYI iken SHORT-aday tier'lari da basilir.

Kaynak: Binance 24s + CoinGecko momentum + olcucu coklu-TF/turev. Esikler: kripto-config.json -> esikler.
Kullanim: python tarayici.py [--min_vol 25] [--n 10]
"""
import argparse
import evren
import olcucu


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min_vol", type=float, default=25.0, help="min 24s hacim (milyon $)")
    ap.add_argument("--n", type=int, default=10, help="her yon icin kac aday dogrulansin")
    a = ap.parse_args()

    rejim = evren.btc_rejim()
    kacin_fund = evren.esik("kacin_funding_abs_pct", 0.1)
    kacin_oi = evren.esik("kacin_oi24_pct", 80.0)

    # 1) Binance 24s likit havuz (stable/gold/kaldirac-token elenir; evren tek kaynak)
    bpool = evren.binance_pool("spot", a.min_vol)
    bchg = {s: chg for s, _, chg in bpool}

    # 2) CoinGecko momentum: 24s VE 7g ayni yonde = gercek trend (iki yonde de)
    cgmom_up, cgmom_dn = {}, {}
    try:
        m = evren.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc"
                      "&per_page=150&page=1&price_change_percentage=24h,7d",
                      {"x-cg-demo-api-key": evren.cg_key(), "User-Agent": "tarayici/1.0"})
    except Exception:
        m = []
    for c in m:
        d24 = c.get("price_change_percentage_24h_in_currency")
        d7 = c.get("price_change_percentage_7d_in_currency")
        if d24 is None or d7 is None:
            continue
        sym = c["symbol"].upper()
        if d24 > 0 and d7 > 0:
            cgmom_up[sym] = d7
        elif d24 < 0 and d7 < 0:
            cgmom_dn[sym] = d7

    def havuz(cg_taraf, b_taraf_syms, n):
        pool = [s for s, _ in sorted(cg_taraf.items(), key=lambda kv: -abs(kv[1])) if s in bchg]
        for s in b_taraf_syms:
            if s not in pool:
                pool.append(s)
        return pool[:n]

    long_pool = havuz(cgmom_up, sorted((s for s in bchg if bchg[s] > 0), key=lambda s: -bchg[s]), a.n)
    short_pool = []
    if rejim.get("rejim") == "AYI":  # SHORT tarama sadece uyumlu ruzgarda (hipotez#1: yon=rejim)
        short_pool = havuz(cgmom_dn, sorted((s for s in bchg if bchg[s] < 0), key=lambda s: bchg[s]), a.n)

    def dogrula(pool, cg_taraf):
        t1, t2, t3, avoid = [], [], [], []
        for sym in pool:
            try:
                _, uz = olcucu.mtf_scan(sym)
                ew = olcucu.early_warning(sym)
            except Exception:
                continue  # Binance perp yok -> deterministik tarama disi
            d7 = cg_taraf.get(sym)
            fund, oi = ew.get("funding_pct"), ew.get("oi_24s_degisim_pct")
            rec = (sym, uz, d7, fund, oi)
            if (fund is not None and abs(fund) > kacin_fund) or (oi is not None and oi > kacin_oi):
                avoid.append(rec + (ew["belirtiler"][0],))   # blow-off / asiri funding-OI
            elif uz in ("GUCLU_YUKARI", "GUCLU_ASAGI"):
                t1.append(rec)
            elif uz in ("YUKARI_EGILIM", "ASAGI_EGILIM"):
                t2.append(rec)
            else:
                t3.append(rec)
        return t1, t2, t3, avoid

    l1, l2, l3, lav = dogrula(long_pool, cgmom_up)
    s1 = s2 = s3 = sav = []
    if short_pool:
        s1, s2, s3, sav = dogrula(short_pool, cgmom_dn)

    def pr(title, rows):
        print(f"\n## {title}")
        for r in rows:
            sym, uz, d7, fund, oi = r[:5]
            d7s = ("%+.0f%%" % d7) if d7 is not None else "-"
            print(f"  {sym:8} {uz:13} 7g={d7s:6} funding={fund} OI24={oi}")

    print("=== TARAYICI (deterministik, 0 token, IKI YONLU) ===")
    print(f"REJIM: {rejim.get('rejim')} (BTC {rejim.get('btc')} vs SMA20 {rejim.get('sma20')})")
    pr("LONG Tier1 - guclu uptrend (agirlikli MTF)", l1)
    pr("LONG Tier2 - uptrend egilim", l2)
    pr("LONG Tier3 - karisik/zayif", l3)
    if rejim.get("rejim") == "AYI":
        print("\n(NOT: rejim AYI -> LONG adaylar ders#3 kapisina takilir; asagidaki SHORT taraf onceliklidir.)")
        pr("SHORT Tier1 - guclu downtrend (SHORT-aday)", s1)
        pr("SHORT Tier2 - downtrend egilim (SHORT-aday)", s2)
        print("\n  SHORT giris kurali (ders#4): guce karsi gir (bounce/lower-high), dipte DEGIL (konum<0.25 = gec).")
        print("  Neg funding = tasima maliyeti (scalp'te ucuz, hold'da pahali). Kalabalik short + smart LONG = squeeze riski.")
    print("\n## KACIN (blow-off / asiri funding-OI)")
    for r in list(lav) + list(sav):
        print(f"  {r[0]:8} funding={r[3]} OI24={r[4]} -> {r[5]}")
    print("\nNot: kisa liste -> CEO derin analizi (Kademe-2: olcucu --entry ile plan-fiyat R/R + Pillar D + Bekci). Bu script LLM kullanmaz.")


if __name__ == "__main__":
    main()
