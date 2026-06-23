#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ÖLÇÜCÜ — Faz 2 (kripto skill)
ATR(14) + yapısal seviye (swing high/low) -> deterministik giriş / SL / TP.
CEO yön verir (long/short); bu script SAYILARI üretir. R/R < 1:2 -> VETO bayrağı.

Bağımlılık YOK (yalnız Python stdlib). Veri: Binance fapi klines (anahtarsız).

Kullanım:
  python olcucu.py --symbol LINK --side long
  python olcucu.py --symbol BTC  --side short --tf 4h --limit 300
Çıktı: JSON (skill bunu okur).
"""
import sys, os, json, argparse, urllib.request, statistics

FAPI = "https://fapi.binance.com"
HERE = os.path.dirname(os.path.abspath(__file__))

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "kripto-olcucu/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

def _load_costs():
    """Maliyet parametreleri: kripto-config.json -> 'maliyet'. Eksikse guvenli varsayilan."""
    try:
        c = json.load(open(os.path.join(HERE, "kripto-config.json"), encoding="utf-8")).get("maliyet", {})
    except Exception:
        c = {}
    return {
        "maker": float(c.get("maker_fee_pct", 0.018)),
        "taker": float(c.get("taker_fee_pct", 0.045)),
        "spot": float(c.get("spot_fee_pct", 0.075)),
        "periyot": float(c.get("funding_periyot", 6)),
        "slippage": float(c.get("slippage_pct", 0.02)),
    }

def _spread_pct(symbol, spot=False):
    """Canli bid/ask spread % (varsayim degil)."""
    base = "https://api.binance.com/api/v3/ticker/bookTicker" if spot else f"{FAPI}/fapi/v1/ticker/bookTicker"
    try:
        d = get_json(f"{base}?symbol={symbol}USDT")
        bid, ask = float(d["bidPrice"]), float(d["askPrice"])
        mid = (bid + ask) / 2
        return (ask - bid) / mid * 100 if mid else 0.0
    except Exception:
        return None

def fetch_klines(symbol, interval, limit):
    url = f"{FAPI}/fapi/v1/klines?symbol={symbol}USDT&interval={interval}&limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "kripto-olcucu/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.load(r)
    # kline: [openTime, open, high, low, close, volume, ...]
    return [{"o": float(k[1]), "h": float(k[2]), "l": float(k[3]), "c": float(k[4])} for k in data]

def atr(bars, period=14):
    """Wilder ATR."""
    trs = []
    for i in range(1, len(bars)):
        h, l, pc = bars[i]["h"], bars[i]["l"], bars[i-1]["c"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    if not trs:
        return 0.0
    if len(trs) < period:
        return statistics.mean(trs)
    a = statistics.mean(trs[:period])
    for tr in trs[period:]:
        a = (a * (period - 1) + tr) / period
    return a

def swings(bars, left=3, right=3):
    """Pivot swing high/low listesi."""
    highs, lows = [], []
    for i in range(left, len(bars) - right):
        win = bars[i-left:i+right+1]
        if bars[i]["h"] == max(b["h"] for b in win):
            highs.append(bars[i]["h"])
        if bars[i]["l"] == min(b["l"] for b in win):
            lows.append(bars[i]["l"])
    return highs, lows

def nearest(price, highs, lows):
    res = sorted([h for h in highs if h > price])      # üstteki en yakın direnç
    sup = sorted([l for l in lows if l < price], reverse=True)  # alttaki en yakın destek
    return (res[0] if res else None), (sup[0] if sup else None)

def measure(symbol, side, tf, limit, spot=False):
    bars = fetch_klines(symbol, tf, limit)
    if len(bars) < 20:
        raise ValueError("yetersiz mum verisi")
    price = bars[-1]["c"]
    a = atr(bars)
    highs, lows = swings(bars)
    res, sup = nearest(price, highs, lows)
    side = side.lower()

    if side == "long":
        # SL: yapısal destek 3*ATR içindeyse onun biraz altı; değilse ATR tabanlı
        if sup is not None and (price - sup) <= 3 * a:
            sl = sup - 0.25 * a
        else:
            sl = price - 1.5 * a
        risk = price - sl
        # TP1: en yakın yapısal direnç (varsa); yoksa 2R uzantı
        tp1 = res if (res is not None and res > price) else price + 2 * risk
        tp2 = tp1 + 1.5 * risk
        rr = (tp1 - price) / risk if risk > 0 else 0.0
    else:  # short
        if res is not None and (res - price) <= 3 * a:
            sl = res + 0.25 * a
        else:
            sl = price + 1.5 * a
        risk = sl - price
        tp1 = sup if (sup is not None and sup < price) else price - 2 * risk
        tp2 = tp1 - 1.5 * risk
        rr = (price - tp1) / risk if risk > 0 else 0.0

    # --- NET R/R (maliyet sonrasi) — SADECE R/R; swing/ATR/yon mantigi degismez ---
    cst = _load_costs()
    spr = _spread_pct(symbol, spot=spot)
    spr_v = spr if spr is not None else 0.0
    try:
        fr8 = fetch_funding(symbol)[0] * 100  # funding %/8h
    except Exception:
        fr8 = None
    reward_g_pct = (abs(tp1 - price) / price * 100) if price else 0.0
    risk_g_pct = (risk / price * 100) if price else 0.0
    if spot:
        f_in = f_tp = f_stop = cst["spot"]
        funding_cost = 0.0                       # spotta funding yok
    else:
        f_in = f_tp = cst["maker"]               # limit giris/TP = maker
        f_stop = cst["taker"]                    # stop market = taker
        ftot = (fr8 or 0.0) * cst["periyot"]
        funding_cost = ftot if side == "long" else -ftot   # ISARETLI: long+poz=gider, long+neg=gelir
    c_reward = f_in + f_tp + funding_cost
    c_risk = f_in + f_stop + spr_v + cst["slippage"] + funding_cost
    net_reward = reward_g_pct - c_reward
    net_risk = risk_g_pct + c_risk
    rr_net = round(net_reward / net_risk, 2) if net_risk > 0 else 0.0

    return {
        "symbol": symbol, "side": side, "tf": tf, "price": round(price, 6),
        "atr14": round(a, 6),
        "yapisal_destek": round(sup, 6) if sup is not None else None,
        "yapisal_direnc": round(res, 6) if res is not None else None,
        "giris": round(price, 6),
        "stop": round(sl, 6),
        "tp1": round(tp1, 6),
        "tp2": round(tp2, 6),
        "risk_birim": round(risk, 6),
        "rr_tp1": round(rr, 2),
        "VETO_rr": rr < 2.0,
        "rr_tp1_net": rr_net,
        "VETO_rr_net": rr_net < 2.0,
        "maliyet": {
            "giris_fee_pct": f_in, "stop_fee_pct": f_stop, "spread_pct": round(spr_v, 3),
            "slippage_pct": cst["slippage"], "funding_pct_8h": round(fr8, 4) if fr8 is not None else None,
            "funding_periyot": cst["periyot"], "funding_toplam_isaretli_pct": round(funding_cost, 4),
            "spot": spot, "C_reward_pct": round(c_reward, 4), "C_risk_pct": round(c_risk, 4),
        },
        "not": "Brut R/R=rr_tp1; maliyet sonrasi=rr_tp1_net. VETO NET uzerinden (VETO_rr_net). Funding ISARETLI (long+neg funding=gelir)."
    }

# ---- Faz 3: çoklu-TF + erken belirti (anahtarsız, ek bağımlılık yok) ----

def fetch_funding(symbol):
    url = f"{FAPI}/fapi/v1/premiumIndex?symbol={symbol}USDT"
    req = urllib.request.Request(url, headers={"User-Agent": "kripto-olcucu/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.load(r)
    return float(d.get("lastFundingRate", 0.0)), float(d.get("markPrice", 0.0))

def fetch_oi_change(symbol):
    url = f"{FAPI}/futures/data/openInterestHist?symbol={symbol}USDT&period=1h&limit=24"
    req = urllib.request.Request(url, headers={"User-Agent": "kripto-olcucu/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.load(r)
    if len(d) < 2:
        return None
    first, last = float(d[0]["sumOpenInterest"]), float(d[-1]["sumOpenInterest"])
    return (last - first) / first * 100 if first else None

def trend_of(bars, n=20):
    closes = [b["c"] for b in bars]
    if len(closes) < n + 1:
        n = max(2, len(closes) // 2)
    sma = statistics.mean(closes[-n:])
    price = closes[-1]
    slope = closes[-1] - closes[-n]
    if price > sma and slope > 0:
        t = "YUKARI"
    elif price < sma and slope < 0:
        t = "ASAGI"
    else:
        t = "NOTR"
    return t, round(price, 6), round(sma, 6)

def mtf_scan(symbol, tfs=("15m", "1h", "4h", "1d")):
    out = {}
    for tf in tfs:
        try:
            bars = fetch_klines(symbol, tf, 120)
            t, price, sma = trend_of(bars)
            a = atr(bars)
            out[tf] = {"trend": t, "price": price, "sma20": sma,
                       "atr_pct": round(a / price * 100, 2) if price else None}
        except Exception as e:
            out[tf] = {"error": str(e)}
    trends = [v["trend"] for v in out.values() if "trend" in v]
    uzlasi = "BELIRSIZ"
    if trends:
        if all(x == "YUKARI" for x in trends):
            uzlasi = "GUCLU_YUKARI"
        elif all(x == "ASAGI" for x in trends):
            uzlasi = "GUCLU_ASAGI"
        elif trends.count("YUKARI") > trends.count("ASAGI"):
            uzlasi = "YUKARI_EGILIM"
        elif trends.count("ASAGI") > trends.count("YUKARI"):
            uzlasi = "ASAGI_EGILIM"
        else:
            uzlasi = "KARISIK"
    return out, uzlasi

def early_warning(symbol):
    bars = fetch_klines(symbol, "1h", 60)
    a = atr(bars)
    price = bars[-1]["c"]
    last_tr = max(bars[-1]["h"] - bars[-1]["l"],
                  abs(bars[-1]["h"] - bars[-2]["c"]),
                  abs(bars[-1]["l"] - bars[-2]["c"]))
    recent = []
    for i in range(len(bars) - 6, len(bars)):
        recent.append(max(bars[i]["h"] - bars[i]["l"],
                          abs(bars[i]["h"] - bars[i-1]["c"]),
                          abs(bars[i]["l"] - bars[i-1]["c"])))
    flags = []
    if a and last_tr > 1.5 * a:
        flags.append("VOLATILITE_GENISLIYOR (son 1s bar TR > 1.5*ATR)")
    if a and statistics.mean(recent) < 0.7 * a:
        flags.append("SIKISMA (daralma -> kirilim yakin olabilir)")
    funding = oi24 = None
    try:
        funding, _ = fetch_funding(symbol)
        if abs(funding) > 0.0003:
            flags.append(f"FUNDING_ASIRI ({funding*100:.3f}%)")
    except Exception:
        pass
    try:
        oi24 = fetch_oi_change(symbol)
        if oi24 is not None and oi24 > 5:
            flags.append(f"OI_HIZLI_ARTIS (+{oi24:.1f}% / 24s)")
        if oi24 is not None and oi24 < -5:
            flags.append(f"OI_HIZLI_DUSUS ({oi24:.1f}% / 24s)")
    except Exception:
        pass
    return {
        "price": round(price, 6),
        "atr_pct_1h": round(a / price * 100, 2) if price else None,
        "son_bar_tr_x_atr": round(last_tr / a, 2) if a else None,
        "funding_pct": round(funding * 100, 4) if funding is not None else None,
        "oi_24s_degisim_pct": round(oi24, 1) if oi24 is not None else None,
        "belirtiler": flags or ["belirgin erken sinyal yok"],
    }

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Olcucu: ATR + yapisal seviye -> giris/SL/TP; --mtf izleme")
    ap.add_argument("--symbol", required=True, help="orn. LINK, BTC, PENGU (USDT eklenir)")
    ap.add_argument("--side", default=None, help="long | short (setup modunda zorunlu)")
    ap.add_argument("--tf", default="1d", help="1d, 4h, 1h, 15m ...")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--mtf", action="store_true", help="coklu-TF + erken belirti izleme raporu")
    ap.add_argument("--spot", action="store_true", help="spot islem (funding yok, spot fee)")
    args = ap.parse_args()
    sym = args.symbol.upper()
    try:
        if args.mtf:
            scan, uzlasi = mtf_scan(sym)
            out = {"symbol": sym, "coklu_tf": scan, "tf_uzlasisi": uzlasi,
                   "erken_belirti": early_warning(sym)}
        else:
            if not args.side:
                raise ValueError("setup modunda --side zorunlu (long|short); izleme icin --mtf kullan")
            out = measure(sym, args.side, args.tf, args.limit, spot=args.spot)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
