#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KÜÇÜK-CAP MODU + BEKÇİ — Faz 5 (kripto skill)
Verilen bir token icin iki DETERMINISTIK kapi:
  (1) market-cap kapisi: <$10M RED | $10M-$250M kucuk-cap GECER | >$250M buyuk-cap
  (2) BEKÇİ = GoPlus guvenlik kapisi: honeypot / tax / kaynak / mint / sahiplik / holder
Kucuk-cap'te Binance perp YOK -> D2 turev sinirli (bunu CEO bilir).
Anahtarsiz GoPlus + CoinGecko (key config'ten). Bagimlilik yok (stdlib).
Kullanim:  python kucukcap.py --id pendle
"""
import json, os, argparse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(HERE, "kripto-config.json")
CG_TO_GOPLUS = {"ethereum": "1", "binance-smart-chain": "56", "polygon-pos": "137",
                "arbitrum-one": "42161", "base": "8453", "avalanche": "43114",
                "optimistic-ethereum": "10", "fantom": "250", "cronos": "25"}
SEV = ["GECER", "UYARI", "RED"]

def get(u, h=None):
    req = urllib.request.Request(u, headers=h or {"User-Agent": "faz5/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def bump(cur, new):
    return new if SEV.index(new) > SEV.index(cur) else cur

def pct(x):
    try:
        return float(x) * 100
    except Exception:
        return None

def cg_coin(cid, key):
    return get(f"https://api.coingecko.com/api/v3/coins/{cid}"
               "?localization=false&tickers=false&market_data=true"
               "&community_data=false&developer_data=false",
               {"x-cg-demo-api-key": key, "User-Agent": "faz5/1.0"})

def bekci_evm(addr, chain):
    try:
        d = get(f"https://api.gopluslabs.io/api/v1/token_security/{chain}?contract_addresses={addr}")
        t = d.get("result", {}).get(addr.lower(), {})
    except Exception as e:
        return {"durum": "BILINMIYOR", "sebep": [f"GoPlus hata: {e}"]}
    if not t:
        return {"durum": "BILINMIYOR", "sebep": ["GoPlus veri yok"]}
    durum, sebep = "GECER", []
    bt, st = pct(t.get("buy_tax")), pct(t.get("sell_tax"))
    if t.get("is_honeypot") == "1":
        durum = bump(durum, "RED"); sebep.append("HONEYPOT")
    if t.get("cannot_sell_all") == "1":
        durum = bump(durum, "RED"); sebep.append("hepsini satamiyor")
    if t.get("selfdestruct") == "1":
        durum = bump(durum, "RED"); sebep.append("selfdestruct")
    if st is not None and st > 10:
        durum = bump(durum, "RED" if st > 20 else "UYARI"); sebep.append(f"sell_tax %{st:.0f}")
    if bt is not None and bt > 10:
        durum = bump(durum, "UYARI"); sebep.append(f"buy_tax %{bt:.0f}")
    if t.get("trading_cooldown") == "1":
        durum = bump(durum, "UYARI"); sebep.append("trading_cooldown")
    if t.get("is_open_source") == "0":
        durum = bump(durum, "UYARI"); sebep.append("kapali kaynak")
    if t.get("is_mintable") == "1":
        durum = bump(durum, "UYARI"); sebep.append("mintable")
    if t.get("can_take_back_ownership") == "1":
        durum = bump(durum, "UYARI"); sebep.append("sahiplik geri alinabilir")
    if t.get("hidden_owner") == "1":
        durum = bump(durum, "UYARI"); sebep.append("gizli sahip")
    if t.get("is_proxy") == "1":
        sebep.append("proxy kontrat")
    try:
        tp = pct((t.get("holders") or [{}])[0].get("percent"))
        if tp and tp > 30:
            durum = bump(durum, "UYARI"); sebep.append(f"en buyuk holder %{tp:.0f}")
    except Exception:
        pass
    return {"durum": durum, "buy_tax_pct": bt, "sell_tax_pct": st,
            "open_source": t.get("is_open_source"), "honeypot": t.get("is_honeypot"),
            "sebep": sebep or ["belirgin risk bayragi yok"]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True, help="CoinGecko coin id (orn. pendle, pudgy-penguins)")
    a = ap.parse_args()
    cfg = json.load(open(CFG, encoding="utf-8"))
    key = cfg.get("coingecko_demo_key", "")
    try:
        c = cg_coin(a.id, key)
    except Exception as e:
        print(json.dumps({"error": f"CoinGecko: {e}"}, ensure_ascii=False)); return
    md = c.get("market_data", {})
    mcap = (md.get("market_cap") or {}).get("usd")
    price = (md.get("current_price") or {}).get("usd")
    vol = (md.get("total_volume") or {}).get("usd")
    plats = {k: v for k, v in (c.get("platforms") or {}).items() if v}

    if mcap is None:
        mcap_kapi = "BILINMIYOR"
    elif mcap < 10_000_000:
        mcap_kapi = "RED (<$10M cok kucuk/riskli -> disla)"
    elif mcap <= 250_000_000:
        mcap_kapi = "GECER (kucuk-cap $10M-$250M)"
    else:
        mcap_kapi = "BUYUK-CAP (>$250M -> normal /kripto modu kullan)"

    bekci = {"durum": "YAPILAMADI", "sebep": ["EVM kontrat yok"]}
    for p, addr in plats.items():
        if p in CG_TO_GOPLUS:
            bekci = bekci_evm(addr, CG_TO_GOPLUS[p]); bekci["zincir"] = p; break
    else:
        if "solana" in plats:
            try:
                addr = plats["solana"]
                d = get(f"https://api.gopluslabs.io/api/v1/solana/token_security?contract_addresses={addr}")
                t = d.get("result", {}).get(addr, {})
                bekci = {"durum": "UYARI" if t else "BILINMIYOR", "zincir": "solana",
                         "sebep": ["Solana GoPlus temel kontrol (EVM kadar kapsamli degil)"]}
            except Exception as e:
                bekci = {"durum": "BILINMIYOR", "zincir": "solana", "sebep": [f"GoPlus solana hata: {e}"]}

    out = {"id": a.id, "price_usd": price, "market_cap_usd": mcap, "vol24_usd": vol,
           "mcap_kapisi": mcap_kapi, "bekci": bekci,
           "not": "Kucuk-cap: Binance perp YOK -> D2 turev sinirli. Bekci RED -> giris YOK; UYARI -> CEO ekstra dikkat + pozisyon kucult."}
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
