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
import evren

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(HERE, "kripto-config.json")
CG_TO_GOPLUS = {"ethereum": "1", "binance-smart-chain": "56", "polygon-pos": "137",
                "arbitrum-one": "42161", "base": "8453", "avalanche": "43114",
                "optimistic-ethereum": "10", "fantom": "250", "cronos": "25"}
# CoinGecko platform adi -> GeckoTerminal ag slug'i (networks endpoint'inden dogrulandi 2026-07-08)
CG_TO_GECKOTERMINAL = {"ethereum": "eth", "binance-smart-chain": "bsc", "polygon-pos": "polygon_pos",
                       "arbitrum-one": "arbitrum", "base": "base", "avalanche": "avax",
                       "optimistic-ethereum": "optimism", "fantom": "ftm", "cronos": "cro",
                       "solana": "solana"}
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
    # esikler tek-dogruluk-kaynagindan (kripto-config.json -> esikler); kod-ici degerler ayni (drift onlenir)
    sell_tax_uyari = evren.esik("goplus_sell_tax_uyari_pct", 10.0)
    sell_tax_red = evren.esik("goplus_sell_tax_red_pct", 20.0)
    buy_tax_uyari = evren.esik("goplus_buy_tax_uyari_pct", 10.0)
    holder_uyari = evren.esik("goplus_holder_uyari_pct", 30.0)
    durum, sebep = "GECER", []
    bt, st = pct(t.get("buy_tax")), pct(t.get("sell_tax"))
    if t.get("is_honeypot") == "1":
        durum = bump(durum, "RED"); sebep.append("HONEYPOT")
    if t.get("cannot_sell_all") == "1":
        durum = bump(durum, "RED"); sebep.append("hepsini satamiyor")
    if t.get("selfdestruct") == "1":
        durum = bump(durum, "RED"); sebep.append("selfdestruct")
    if st is not None and st > sell_tax_uyari:
        durum = bump(durum, "RED" if st > sell_tax_red else "UYARI"); sebep.append(f"sell_tax %{st:.0f}")
    if bt is not None and bt > buy_tax_uyari:
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
        if tp and tp > holder_uyari:
            durum = bump(durum, "UYARI"); sebep.append(f"en buyuk holder %{tp:.0f}")
    except Exception:
        pass
    return {"durum": durum, "buy_tax_pct": bt, "sell_tax_pct": st,
            "open_source": t.get("is_open_source"), "honeypot": t.get("is_honeypot"),
            "sebep": sebep or ["belirgin risk bayragi yok"]}


def dex_likidite_gt(gt_network, addr):
    """GeckoTerminal (anahtarsiz) — token'in en derin DEX havuzundaki kilitli likidite (reserve_in_usd).
    En derin TEK havuz (toplam degil; cikis tipik tek havuzdan olur -> muhafazakar). Ag/parse hatasi
    veya bos -> None (cagiran taraf UYARI'ya cevirir, ASLA cokmez). Rate-limit ~30/dk, on-demand tek cagri."""
    try:
        d = get(f"https://api.geckoterminal.com/api/v2/networks/{gt_network}/tokens/{addr}/pools?page=1",
                {"User-Agent": "faz5/1.0"})
    except Exception:
        return None
    if not isinstance(d, dict) or d.get("errors"):
        return None
    havuzlar = d.get("data") or []
    if not havuzlar:
        return None
    en_derin, en_derin_ad = 0.0, None
    for p in havuzlar:
        a = p.get("attributes", {})
        try:
            r = float(a.get("reserve_in_usd") or 0.0)
        except Exception:
            continue
        if r > en_derin:
            en_derin, en_derin_ad = r, a.get("name")
    return {"en_derin_havuz_usd": round(en_derin, 0), "havuz_sayisi": len(havuzlar),
            "en_derin_havuz_ad": en_derin_ad, "zincir": gt_network}


def cg_id_coz(sembol_veya_id, key):
    """Sembolden CoinGecko id coz (2026-07-07 — SLLX/SLX karisikligi dersi: --id yanlissa
    sessizce bos market_data donuyordu). Once dogrudan id olarak dene (coins/{id} basarili donerse
    zaten id'dir); basarisizsa /search ile sembol eslesmesi ara, en yuksek mcap_rank'i (en olasi) sec."""
    try:
        c = cg_coin(sembol_veya_id, key)
        if c.get("market_data"):
            return sembol_veya_id, c, None
    except Exception:
        pass
    try:
        sonuc = get(f"https://api.coingecko.com/api/v3/search?query={sembol_veya_id}",
                    {"x-cg-demo-api-key": key, "User-Agent": "faz5/1.0"})
        adaylar = sonuc.get("coins", [])
    except Exception as e:
        return None, None, f"CoinGecko arama hatasi: {e}"
    if not adaylar:
        return None, None, f"'{sembol_veya_id}' hicbir yerde bulunamadi (CoinGecko arama bos) - uydurma, kullaniciya sor"
    tam_sembol_eslesen = [a for a in adaylar if a.get("symbol", "").lower() == sembol_veya_id.lower()]
    havuz = tam_sembol_eslesen or adaylar
    havuz.sort(key=lambda a: (a.get("market_cap_rank") is None, a.get("market_cap_rank") or 0))
    if len(havuz) > 1 and not tam_sembol_eslesen:
        return None, None, (f"'{sembol_veya_id}' TAM sembol eslesmesi yok, birden fazla benzer sonuc var "
                             f"({', '.join(a['id'] for a in havuz[:5])}) - hangisi oldugunu kullaniciya sor, uydurma")
    secilen = havuz[0]
    try:
        c = cg_coin(secilen["id"], key)
        return secilen["id"], c, None
    except Exception as e:
        return None, None, f"CoinGecko coins/{secilen['id']} hatasi: {e}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True, help="CoinGecko coin id VEYA sembol (orn. pendle, PENDLE) - sembolse otomatik cozulur")
    a = ap.parse_args()
    cfg = json.load(open(CFG, encoding="utf-8"))
    key = cfg.get("coingecko_demo_key", "")
    cid, c, hata = cg_id_coz(a.id, key)
    if hata:
        print(json.dumps({"error": hata}, ensure_ascii=False)); return
    md = c.get("market_data", {})
    mcap = (md.get("market_cap") or {}).get("usd")
    price = (md.get("current_price") or {}).get("usd")
    vol = (md.get("total_volume") or {}).get("usd")
    plats = {k: v for k, v in (c.get("platforms") or {}).items() if v}

    mcap_alt = evren.esik("kucukcap_mcap_alt_musd", 10.0) * 1e6
    mcap_ust = evren.esik("kucukcap_mcap_ust_musd", 250.0) * 1e6
    if mcap is None:
        mcap_kapi = "BILINMIYOR"
    elif mcap < mcap_alt:
        mcap_kapi = f"RED (<${mcap_alt/1e6:.0f}M cok kucuk/riskli -> disla)"
    elif mcap <= mcap_ust:
        mcap_kapi = f"GECER (kucuk-cap ${mcap_alt/1e6:.0f}M-${mcap_ust/1e6:.0f}M)"
    else:
        mcap_kapi = f"BUYUK-CAP (>${mcap_ust/1e6:.0f}M -> normal /kripto modu kullan)"

    # Rejim anahtari (2026-07-07 — daha once sadece SKILL talimatiydi, CEO'nun elle uygulamasina
    # birakiyordu; artik ciktida deterministik alan olarak var, atlanamaz).
    rejim = evren.btc_rejim()
    if rejim.get("rejim") == "AYI":
        rejim_uyarisi = "AYI rejimde kucuk-cap'ler en sert duser -> giristen UZAK DUR (SKILL kurali)"
    elif rejim.get("rejim") == "BOGA":
        rejim_uyarisi = "BOGA rejim -> kucuk-cap istahi normal, yine de Bekci+mcap kapisi gecerli"
    else:
        rejim_uyarisi = "NOTR rejim -> temkinli, tam boyut yerine yarim pozisyon dusun"

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

    # DEX likidite kapisi (2026-07-08 — exit-liquidity riski; GoPlus 'satabilir miyim'i olcer, 'ne kadar'i DEGIL).
    # Ayri ucuncu kapi (mcap/bekci gibi paralel). Iki kademeli: <red RED, <uyari UYARI, else GECER.
    red_esik = evren.esik("kucukcap_dex_liq_red_usd", 100000.0)
    uyari_esik = evren.esik("kucukcap_dex_liq_uyari_usd", 250000.0)
    gt_zincir = next((CG_TO_GECKOTERMINAL[p] for p in plats if p in CG_TO_GECKOTERMINAL), None)
    if gt_zincir is None:
        dex = {"durum": "UYARI", "sebep": ["kontrat adresi yok / GT-desteklenmeyen zincir - DEX likidite olculemedi"]}
    else:
        addr = next(v for p, v in plats.items() if CG_TO_GECKOTERMINAL.get(p) == gt_zincir)
        lik = dex_likidite_gt(gt_zincir, addr)
        if lik is None:
            dex = {"durum": "UYARI", "sebep": ["Likidite dogrulanamadi (GeckoTerminal yanit vermedi/bos)"], "zincir": gt_zincir}
        else:
            d_usd = lik["en_derin_havuz_usd"]
            if d_usd < red_esik:
                durum = "RED"; sebep = f"Yetersiz DEX likidite (en derin havuz ${d_usd/1e3:.0f}k < ${red_esik/1e3:.0f}k)"
            elif d_usd < uyari_esik:
                durum = "UYARI"; sebep = f"Sig havuz (${d_usd/1e3:.0f}k) - pozisyon kucult, slippage riski"
            else:
                durum = "GECER"; sebep = f"Yeterli DEX likidite (en derin havuz ${d_usd/1e3:.0f}k)"
            dex = {"durum": durum, "sebep": [sebep], **lik}

    out = {"id": cid, "girilen": a.id, "price_usd": price, "market_cap_usd": mcap, "vol24_usd": vol,
           "mcap_kapisi": mcap_kapi, "bekci": bekci, "dex_likidite": dex,
           "rejim": rejim.get("rejim"), "rejim_uyarisi": rejim_uyarisi,
           "not": "Kucuk-cap: Binance perp YOK -> D2 turev sinirli. Bekci RED -> giris YOK; UYARI -> CEO ekstra dikkat + pozisyon kucult. "
                  "dex_likidite RED -> giris YOK (Bekci RED ile ayni disiplin); UYARI -> pozisyon kucult."}
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
