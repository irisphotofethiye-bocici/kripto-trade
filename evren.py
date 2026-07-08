#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVREN — ortak kripto evren + rejim modulu (2026-07-02 revizyonu, m7 duzeltmesi).
radar / tarayici / piyasa_yapisi ayni evren kodunu 3 kopya tasiyordu (drift basladi:
radar stable/gold elemiyordu). Tek kaynak artik burasi.

Icerik:
  - cg_universe(): CoinGecko top-750 -> {SYM: {mcap, circ, total, float_oran}}
  - binance_pool(): likit USDT havuzu (stable/gold/tokenize-hisse/kaldirac-token elenir)
  - btc_rejim(): BTC gunluk SMA20 + piyasa_yapisi_log son satiri -> AYI/BOGA/NOTR
  - esik(): kripto-config.json -> esikler (tek dogruluk kaynagi; yoksa varsayilan)
Deterministik, 0 token. Bagimlilik yok (stdlib).
"""
import json, os, time, urllib.request, urllib.error, datetime, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(HERE, "kripto-config.json")
SPOT = "https://api.binance.com"
FAPI = "https://fapi.binance.com"
STABLES = {"USDT", "USDC", "DAI", "BUSD", "TUSD", "FDUSD", "USDE", "USDD", "PYUSD",
           "RLUSD", "USD1", "USDP", "GUSD", "USDB", "USDX"}
GOLD = {"PAXG", "XAUT", "XAU"}
BAD = ("UPUSDT", "DOWNUSDT", "BULLUSDT", "BEARUSDT")

_cfg_cache = None


def cfg():
    global _cfg_cache
    if _cfg_cache is None:
        try:
            _cfg_cache = json.load(open(CFG, encoding="utf-8"))
        except Exception:
            _cfg_cache = {}
    return _cfg_cache


def cg_key():
    return cfg().get("coingecko_demo_key", "")


def esik(ad, varsayilan):
    """kripto-config.json -> esikler[ad]; yoksa varsayilan (kod ve config ayni degeri tasir)."""
    try:
        return float(cfg().get("esikler", {}).get(ad, varsayilan))
    except Exception:
        return varsayilan


_ban_until = 0.0  # Binance 418 sogutma penceresi (2026-07-08, rate-limit direnc katmani)


def get(u, headers=None, timeout=25):
    """Paylasimli HTTP getirici — TEK dogruluk kaynagi (radar/testbot/olcucu/piyasa_yapisi/panel buradan cagirir).
    429 (rate-limit uyarisi): Retry-After bekle, BIR KEZ tekrar dene. 418 (IP ban): retry YOK, sogutma
    penceresi baslat — pencere icinde YENI network cagrisi yapilmadan hemen hata donulur (banı uzatmamak
    icin; cagiran taraflardaki mevcut 'except Exception' sarmalayicilari degismeden calismaya devam eder)."""
    global _ban_until
    if _ban_until and time.time() < _ban_until:
        raise RuntimeError(f"Binance IP-ban sogutma penceresinde (kalan {_ban_until - time.time():.0f}sn) -> istek atlandi: {u}")
    req = urllib.request.Request(u, headers=headers or {"User-Agent": "evren/1.0"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=timeout))
    except urllib.error.HTTPError as e:
        if e.code == 418:
            _ban_until = time.time() + 120.0
            print(f"BINANCE 418 (IP BAN) -> 120sn sogutma baslatildi: {u}")
            raise
        if e.code == 429:
            try:
                bekle = float(e.headers.get("Retry-After", 3))
            except Exception:
                bekle = 3.0
            time.sleep(bekle)
            try:
                return json.load(urllib.request.urlopen(req, timeout=timeout))
            except urllib.error.HTTPError as e2:
                if e2.code == 418:
                    _ban_until = time.time() + 120.0
                print(f"BINANCE {e2.code} (429 sonrasi tekrar basarisiz) -> {u}")
                raise
        raise


def cg_universe(key=None, pages=(1, 2, 3)):
    """CoinGecko markets -> {SYM: {mcap, circ, total, float_oran}}.
    float_oran = circulating/total (dusuk-float/unlock filtresi icin; RE/FOGO dersi)."""
    key = key if key is not None else cg_key()
    out = {}
    for pg in pages:
        try:
            url = (f"https://api.coingecko.com/api/v3/coins/markets"
                   f"?vs_currency=usd&order=market_cap_desc&per_page=250&page={pg}")
            for c in get(url, {"x-cg-demo-api-key": key, "User-Agent": "evren/1.0"}):
                sym = c["symbol"].upper()
                if sym in out:
                    continue
                circ, tot = c.get("circulating_supply"), c.get("total_supply")
                fo = (circ / tot) if (circ and tot and tot > 0) else None
                out[sym] = {"mcap": c.get("market_cap"), "circ": circ, "total": tot,
                            "float_oran": round(fo, 3) if fo is not None else None}
        except Exception:
            pass
    return out


def raw_tickers(kaynak="fapi", timeout=60, retries=2):
    """Tum-sembol 24hr ticker, HAM liste (buyuk payload -> genis timeout + birkac deneme).
    binance_pool() ve radar.erken_kusak_tara() AYNI cagriyi bagimsiz tekrarliyordu (2026-07-08
    duzeltmesi) -> tek yerden cekilir, ikisine de tickers= parametresiyle gecirilir."""
    base = FAPI + "/fapi/v1/ticker/24hr" if kaynak == "fapi" else SPOT + "/api/v3/ticker/24hr"
    for _ in range(retries):
        try:
            return get(base, timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code == 418:
                raise
        except Exception:
            pass
    return []


def binance_pool(kaynak="fapi", min_vol_musd=8.0, chg_max=None, cryptos=None, tickers=None):
    """Likit USDT havuzu: [(sym, quoteVol, chg24), ...] hacme gore sirali.
    Eleme: BAD kaldirac-tokenlari, stable, altin-pegli, (cryptos verildiyse) kripto-olmayan.
    tickers: onceden raw_tickers() ile cekilmis liste verilirse tekrar network cagrisi yapilmaz."""
    t = tickers if tickers is not None else raw_tickers(kaynak)
    pool = []
    for x in t:
        s = x.get("symbol", "")
        if not s.endswith("USDT") or any(s.endswith(b) for b in BAD):
            continue
        sym = s[:-4]
        if sym in STABLES or sym in GOLD or "USD" in sym:
            continue
        if cryptos is not None and cryptos and sym not in cryptos:
            continue
        try:
            chg = float(x["priceChangePercent"]); qv = float(x["quoteVolume"])
        except Exception:
            continue
        if qv < min_vol_musd * 1e6:
            continue
        if chg_max is not None and abs(chg) > chg_max:
            continue
        pool.append((sym, qv, chg))
    pool.sort(key=lambda r: -r[1])
    return pool


def btc_rejim():
    """Rejim tespiti (hipotez#1: 'yon = rejim'; ayi -> yuksek radar skoru = SHORT adayi).
    Birincil: BTC gunluk kapanis vs SMA20 + egim. Ek baglam: piyasa_yapisi_log son satiri (taze ise)."""
    rejim, detay = "BILINMIYOR", {}
    try:
        d = get(f"{SPOT}/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=30")
        cl = [float(k[4]) for k in d]
        sma20 = statistics.mean(cl[-20:])
        slope = cl[-1] - cl[-20]
        if cl[-1] > sma20 and slope > 0:
            rejim = "BOGA"
        elif cl[-1] < sma20 and slope < 0:
            rejim = "AYI"
        else:
            rejim = "NOTR"
        detay = {"btc": round(cl[-1], 0), "sma20": round(sma20, 0)}
    except Exception:
        pass
    # piyasa_yapisi trend logu (varsa ve <24h taze ise) baglama eklenir
    try:
        logf = os.path.join(HERE, "piyasa_yapisi_log.jsonl")
        lines = [l for l in open(logf, encoding="utf-8").read().splitlines() if l.strip()]
        last = json.loads(lines[-1])
        yas_saat = (datetime.datetime.now()
                    - datetime.datetime.strptime(last["ts"], "%Y-%m-%d %H:%M")).total_seconds() / 3600
        if yas_saat < 24:
            detay.update({"btc_d": last.get("btc_d"), "usdt_d": last.get("usdt_d"),
                          "stable_d": last.get("stable_d")})
    except Exception:
        pass
    return {"rejim": rejim, **detay}


if __name__ == "__main__":
    print(json.dumps({"rejim": btc_rejim(),
                      "esik_ornek": {"funding_long_veto_pct": esik("funding_long_veto_pct", 0.03)}},
                     ensure_ascii=False, indent=2))
