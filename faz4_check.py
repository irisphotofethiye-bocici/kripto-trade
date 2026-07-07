#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Günlük sağlık kontrolü (Faz 4'te doğdu; kapı 2026-07-02'de GEÇTİ ile kapandı, kontrol kalıcı).
Ölçer: (1) veri doğruluğu = Binance vs CoinGecko fiyat farkı (<%0.5 -> PASS),
       (2) erişilebilirlik = Binance spot+fapi ulaşılabilir mi,
       (3) ZAMANLAYICI BAYATLIK (m11/M8 duzeltmesi 2026-07-02): radar_active >25dk VEYA
           piyasa_yapisi_log son satiri >14sa eski ise UYARI (gorev durmus/PC kapali kalmis).
CoinGecko key yoksa veri karşılaştırması ATLANDI sayılır (ERİŞİM'den ayrı — m11).
Kullanım: python faz4_check.py
"""
import json, os, urllib.request, datetime

def _yas_dakika(ts_str):
    try:
        t = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M")
        return (datetime.datetime.now() - t).total_seconds() / 60
    except Exception:
        return None

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
    erisim_pass = binance_ok and fapi_ok
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"=== SAGLIK kontrol {now} ===")
    print(f"Binance spot: {'OK' if binance_ok else 'ERISILEMEDI'} | "
          f"Binance fapi: {'OK' if fapi_ok else 'ERISILEMEDI'} | "
          f"CoinGecko: {'OK' if cg_ok else ('KEY YOK' if not key else 'HATA')}")
    for sym, b, c, div in rows:
        ds = ("%.3f%%" % div) if div is not None else "-"
        print(f"  {sym:6} Binance={b} CoinGecko={c} fark={ds}")
    if key and cg_ok:
        print(f"Max fark: {max_div:.3f}%  ->  VERI_DOGRULUGU: {'PASS' if max_div < 0.5 else 'FAIL'} (esik <0.5%)")
    else:
        print("VERI_DOGRULUGU: ATLANDI (CoinGecko yok — erisimden ayri degerlendirilir, m11)")
    print(f"ERISIM: {'PASS' if erisim_pass else 'FAIL'}")

    # --- Zamanlayici bayatlik (M8/m11): gorev calisiyor mu? ---
    print("\n-- Zamanlayici bayatlik --")
    try:
        ra = json.load(open(os.path.join(HERE, "radar_active.json"), encoding="utf-8"))
        yas = _yas_dakika(ra.get("guncelleme", ""))
        if yas is None:
            print("radar_active: guncelleme damgasi okunamadi -> UYARI")
        else:
            durum = "OK" if yas <= 25 else "BAYAT -> KriptoRadar gorevi durmus/PC uyumus olabilir"
            print(f"radar_active: {yas:.0f} dk once ({durum}; beklenen ~15dk ritim)")
    except Exception:
        print("radar_active.json okunamadi -> UYARI")
    try:
        lines = [l for l in open(os.path.join(HERE, "piyasa_yapisi_log.jsonl"), encoding="utf-8").read().splitlines() if l.strip()]
        yas = _yas_dakika(json.loads(lines[-1]).get("ts", "")) if lines else None
        if yas is None:
            print("piyasa_yapisi_log: bos/okunamadi -> UYARI")
        else:
            durum = "OK" if yas <= 14 * 60 else "BAYAT -> KriptoPiyasa gorevi kacirmis (11:00/23:00 ritim)"
            print(f"piyasa_yapisi_log: {yas/60:.1f} saat once ({durum})")
    except Exception:
        print("piyasa_yapisi_log.jsonl okunamadi -> UYARI")

if __name__ == "__main__":
    main()
