#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RADAR — Faz 3/6: hareketten ONCE veya tam baslarken yakalama (öncü imza taramasi).
"Sonradan en cok artan"i DEGIL, yukselisi tetikleyen oncu kosullari arar:
  - OI fiyat yatayken hizli sisiyor (pozisyon kuruluyor)
  - funding negatife/asiriya kayiyor (squeeze yakiti) ama fiyat daha oynamadi
  - volatilite sikismasi (coiling) -> ilk genisleme
  - hacim tabandan uyaniyor
2 asama: (1) Binance 24h ticker'dan likit + henuz-patlamamis havuz; (2) her aday icin 1h klines + OI + funding.
Anahtarsiz Binance. Kullanim: python radar.py [--n 35] [--min_vol 8] [--chg_max 15]
UYARI: bu ONCU olasilik tahminidir, garanti DEGIL; yon yukari da asagi da olabilir.
"""
import json, os, sys, urllib.request, statistics, argparse, datetime
import olcucu

# pythonw.exe (zamanlayici) altinda sys.stdout/err = None -> print() patlar.
# Devnull'a yonlendir; gercek uyarilar zaten radar_alerts.log'a yaziliyor.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

FAPI = "https://fapi.binance.com"
BAD = ("UPUSDT", "DOWNUSDT", "BULLUSDT", "BEARUSDT")

def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "radar/1.0"})
    return json.load(urllib.request.urlopen(req, timeout=20))

def klines(sym, n=50):
    d = get(f"{FAPI}/fapi/v1/klines?symbol={sym}USDT&interval=1h&limit={n}")
    return [{"h": float(k[2]), "l": float(k[3]), "c": float(k[4]),
             "v": float(k[5]), "qv": float(k[7])} for k in d]

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def funding(sym):
    try:
        return float(get(f"{FAPI}/fapi/v1/premiumIndex?symbol={sym}USDT")["lastFundingRate"]) * 100
    except Exception:
        return None

def oi_changes(sym):
    try:
        d = get(f"{FAPI}/futures/data/openInterestHist?symbol={sym}USDT&period=1h&limit=24")
        if len(d) < 5:
            return None, None
        oi = [float(x["sumOpenInterest"]) for x in d]
        ch24 = (oi[-1] - oi[0]) / oi[0] * 100 if oi[0] else None
        ch3 = (oi[-1] - oi[-4]) / oi[-4] * 100 if oi[-4] else None
        return ch24, ch3
    except Exception:
        return None, None

def analyze(sym):
    b = klines(sym, 50)
    if len(b) < 25:
        return None
    price = b[-1]["c"]
    a = olcucu.atr(b)
    if not a or not price:
        return None
    # sikisma: son 6 barin TR ort / ATR14
    trs = [max(b[i]["h"]-b[i]["l"], abs(b[i]["h"]-b[i-1]["c"]), abs(b[i]["l"]-b[i-1]["c"])) for i in range(len(b)-6, len(b))]
    comp = statistics.mean(trs) / a
    # hacim patlamasi: son bar qv / son 24 medyan
    med = statistics.median([x["qv"] for x in b[-24:]])
    vol_x = (b[-1]["qv"] / med) if med else 0
    # 20-bar aralikta konum
    hi = max(x["h"] for x in b[-20:]); lo = min(x["l"] for x in b[-20:])
    pos = (price - lo) / (hi - lo) if hi > lo else 0.5
    last1 = (b[-1]["c"] - b[-2]["c"]) / b[-2]["c"] * 100
    last3 = (b[-1]["c"] - b[-4]["c"]) / b[-4]["c"] * 100
    f = funding(sym)
    oi24, oi3 = oi_changes(sym)

    # --- skor (0-100) ---
    s_oi = clamp((oi24 or 0)/20)*25 + clamp((oi3 or 0)/8)*10
    # negatif funding = squeeze yakiti AMA yalniz fiyat dusmuyorsa (yoksa bu sadece dususte short baskisi)
    squeeze_bonus = 8 if (f is not None and f < -0.01 and last3 >= -1 and (oi3 or 0) >= 0) else 0
    s_fund = clamp(abs(f or 0)/0.05)*15 + squeeze_bonus
    s_comp = clamp((0.8 - comp)/0.5)*20
    s_vol = clamp((vol_x - 1.5)/3)*20
    s_brk = clamp((pos - 0.7)/0.3)*10 + clamp(last1/4)*5
    score = round(s_oi + s_fund + s_comp + s_vol + s_brk, 1)

    # asama etiketi
    if vol_x > 2.5 and last1 > 2 and (oi3 or 0) > 3:
        stage = "BASLIYOR"        # hareket tam basliyor
    elif comp < 0.65 and abs(last3) < 4 and (oi24 or 0) > 8:
        stage = "HAZIRLANIYOR"    # coiled + pozisyon, fiyat hala yatay
    else:
        stage = "izle"
    return {"sym": sym, "score": score, "stage": stage, "comp": round(comp, 2),
            "vol_x": round(vol_x, 1), "oi24": oi24, "oi3": oi3, "funding": f,
            "pos": round(pos, 2), "last1": round(last1, 1), "last3": round(last3, 1)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=35, help="aday sayisi (asama-2)")
    ap.add_argument("--min_vol", type=float, default=8.0, help="min 24s hacim (milyon $)")
    ap.add_argument("--chg_max", type=float, default=15.0, help="zaten patlamis (>%) olanlari ele")
    ap.add_argument("--watch", action="store_true", help="yeni sinyalleri radar_alerts.log'a yaz (zamanlayici icin)")
    a = ap.parse_args()

    # Kripto evreni (CoinGecko) — tokenize hisseleri (SOXL/INTC/MSTR...) elemek + mcap icin
    HERE = os.path.dirname(os.path.abspath(__file__))
    key = json.load(open(os.path.join(HERE, "kripto-config.json"), encoding="utf-8")).get("coingecko_demo_key", "")
    cryptos = {}
    for pg in (1, 2, 3):
        try:
            req = urllib.request.Request(
                f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={pg}",
                headers={"x-cg-demo-api-key": key, "User-Agent": "radar/1.0"})
            for c in json.load(urllib.request.urlopen(req, timeout=20)):
                cryptos.setdefault(c["symbol"].upper(), c.get("market_cap"))
        except Exception:
            pass

    # Asama 1: likit + henuz patlamamis + KRIPTO havuz
    t = get(f"{FAPI}/fapi/v1/ticker/24hr")
    pool = []
    for x in t:
        s = x.get("symbol", "")
        if not s.endswith("USDT") or any(s.endswith(b) for b in BAD):
            continue
        base = s[:-4]
        if cryptos and base not in cryptos:   # tokenize hisse / kripto olmayan -> ele
            continue
        try:
            chg = float(x["priceChangePercent"]); qv = float(x["quoteVolume"])
        except Exception:
            continue
        if qv < a.min_vol*1e6 or abs(chg) > a.chg_max:
            continue
        pool.append((base, qv))
    pool.sort(key=lambda r: -r[1])
    pool = [s for s, _ in pool[:a.n]]

    rows = []
    for sym in pool:
        try:
            r = analyze(sym)
            if r:
                mc = cryptos.get(sym)
                r["mcap"] = (f"${mc/1e6:.0f}M" if mc else "?")
                rows.append(r)
        except Exception:
            continue
    rows.sort(key=lambda r: -r["score"])

    # --- WATCH modu: onceki tarama ile kiyasla, YENI sinyalleri logla (zamanlayici icin) ---
    if a.watch:
        statef = os.path.join(HERE, "radar_state.json")
        logf = os.path.join(HERE, "radar_alerts.log")
        try:
            prev = json.load(open(statef, encoding="utf-8"))
        except Exception:
            prev = {}
        alerts = []
        for r in rows:
            p = prev.get(r["sym"])
            pscore = p["score"] if p else 0
            pstage = p["stage"] if p else None
            if r["stage"] in ("BASLIYOR", "HAZIRLANIYOR"):
                if pstage not in ("BASLIYOR", "HAZIRLANIYOR") or (r["score"] - pscore >= 10):
                    alerts.append(r)
            elif r["score"] >= 40 and pscore < 40:
                alerts.append(r)
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        if alerts:
            with open(logf, "a", encoding="utf-8") as fh:
                for r in alerts:
                    fh.write(f"{ts} | {r['stage']:12} | {r['sym']:8} skor={r['score']} mcap={r['mcap']} "
                             f"OI24={r['oi24']} OI3={r['oi3']} fund={r['funding']} volx={r['vol_x']} "
                             f"sikis={r['comp']} konum={r['pos']} son1s={r['last1']}\n")
            print(f"[{ts}] {len(alerts)} YENI uyari -> radar_alerts.log")
            for r in alerts:
                print(f"  ALERT {r['stage']:12} {r['sym']:8} skor={r['score']}")
        else:
            print(f"[{ts}] yeni uyari yok ({len(rows)} coin tarandi)")
        # CANLI snapshot — her calismada YENIDEN yazilir (birikme YOK; eski/yeni karismaz).
        # "Su an ne sicak" icin BUNU oku; radar_alerts.log = sadece gecmis gunluk.
        active = [r for r in rows if r["stage"] in ("BASLIYOR", "HAZIRLANIYOR")]
        json.dump({"guncelleme": ts, "tarandi": len(rows),
                   "aktif_sinyaller": [{"sym": r["sym"], "stage": r["stage"], "score": r["score"],
                                        "oi24": r["oi24"], "oi3": r["oi3"], "funding": r["funding"],
                                        "comp": r["comp"], "vol_x": r["vol_x"], "pos": r["pos"],
                                        "last1": r["last1"], "mcap": r["mcap"]} for r in active]},
                  open(os.path.join(HERE, "radar_active.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        # alert log'u sinirla: son 300 satir (sinirsiz buyumeyi onle)
        try:
            if os.path.exists(logf):
                ln = open(logf, encoding="utf-8").read().splitlines()
                if len(ln) > 300:
                    open(logf, "w", encoding="utf-8").write("\n".join(ln[-300:]) + "\n")
        except Exception:
            pass
        json.dump({r["sym"]: {"stage": r["stage"], "score": r["score"]} for r in rows},
                  open(statef, "w", encoding="utf-8"))
        return

    def show(title, items):
        print(f"\n## {title}")
        print(f"  {'COIN':8} {'skor':>5} {'mcap':>8} {'sikis':>5} {'volx':>5} {'OI24':>6} {'OI3s':>6} {'fund%':>7} {'konum':>5} {'son1s':>6}")
        for r in items:
            print(f"  {r['sym']:8} {r['score']:>5} {r['mcap']:>8} {r['comp']:>5} {r['vol_x']:>5} "
                  f"{('%+.0f'%r['oi24']) if r['oi24'] is not None else '-':>6} "
                  f"{('%+.0f'%r['oi3']) if r['oi3'] is not None else '-':>6} "
                  f"{('%.3f'%r['funding']) if r['funding'] is not None else '-':>7} "
                  f"{r['pos']:>5} {('%+.1f'%r['last1']):>6}")

    print("=== RADAR (oncu imza; garanti DEGIL) ===")
    show("BASLIYOR — hareket tam baslıyor (vol+OI+ilk bar)", [r for r in rows if r["stage"] == "BASLIYOR"][:8])
    show("HAZIRLANIYOR — coiled + pozisyon, fiyat hala yatay", [r for r in rows if r["stage"] == "HAZIRLANIYOR"][:8])
    show("EN YUKSEK SKOR (genel, ilk 10)", rows[:10])
    print("\nNot: oncu olasilik; yon yukari da asagi da olabilir. Kisa liste -> Opus CEO derin analiz + Bekci.")

if __name__ == "__main__":
    main()
