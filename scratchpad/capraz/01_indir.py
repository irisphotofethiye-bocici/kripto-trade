#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CAPRAZ BORSA — INDIRICI (2026-09-05)

ON-KAYIT: ON_KAYIT_capraz_borsa.md, commit a0e52c5 — KOSUMDAN ONCE yazildi.

NE INDIRIR: 460 ortak sembol icin 24 ay fonlama gecmisi, IKI borsadan.
   binance : fapi/v1/fundingRate                 (kalici uc)
   bybit   : v5/market/funding/history           (kalici uc, >=2023-11 dogrulandi)

🔴 EZMEZ — kullanicinin duran kurali ("eldeki veriyi ezme ama", 2026-09-05) ve
   CLAUDE.md'nin olculmus kaybi (2026-08-24, 58 sembolde OI/long-short gitti):
     (a) var olani OKUR
     (b) zaman damgasina gore BIRLESTIRIR
     (c) sonuc eskisinden KISAysa HATA firlatir, yazmaz
   Ayrica YENI dizine yazar; hicbir mevcut arsive dokunmaz.

KESINTIYE DAYANIKLI: her sembol kendi dosyasina yazilir, tamamlananlar atlanir.
   Yeniden calistirmak guvenlidir.

Salt-okuma disinda tek yazim: scratchpad/capraz/veri/*.json
Ucretli cagri YOK. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, time, random, urllib.request, urllib.error, argparse, datetime

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURASI))
VERI = os.path.join(BURASI, "veri")
KLINES = os.path.join(KOK, "scratchpad", "klines_1h_uzun")

# --- PENCERE: on-kayitta SABIT, burada degistirilmez -----------------------
BAS = int(datetime.datetime(2024, 9, 1).timestamp() * 1000)
SON = int(datetime.datetime(2026, 8, 31, 23, 59).timestamp() * 1000)

BEKLE = (0.06, 0.16)        # rate-limit guvenlik payi (evren.get deseni)


def _uyu():
    time.sleep(random.uniform(*BEKLE))


def g(url, timeout=25):
    """3 deneme, ustel bekleme. 418 (IP ban) -> hemen birak."""
    for deneme in range(3):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 418:
                raise RuntimeError("HTTP 418 — IP BAN. Indirme durduruldu.")
            if e.code == 429:
                time.sleep(5 * (deneme + 1))
            elif deneme == 2:
                raise
            else:
                time.sleep(2 * (deneme + 1))
        except Exception:
            if deneme == 2:
                raise
            time.sleep(2 * (deneme + 1))
    return None


# ---------------------------------------------------------------------------
def binance_seri(sym):
    """[(ts_ms, oran)] — ileri sayfalama, limit 1000."""
    out, bas = {}, BAS
    while bas < SON:
        d = g("https://fapi.binance.com/fapi/v1/fundingRate"
              "?symbol=%s&startTime=%d&endTime=%d&limit=1000" % (sym, bas, SON))
        if not d:
            break
        for x in d:
            out[int(x["fundingTime"])] = float(x["fundingRate"])
        yeni = max(int(x["fundingTime"]) for x in d)
        if yeni <= bas or len(d) < 1000:
            break
        bas = yeni + 1
        _uyu()
    return out


def bybit_seri(sym):
    """[(ts_ms, oran)] — GERIYE sayfalama (bybit yeniden eskiye doner), limit 200."""
    out, son = {}, SON
    for _ in range(60):                       # emniyet tavani
        d = g("https://api.bybit.com/v5/market/funding/history"
              "?category=linear&symbol=%s&startTime=%d&endTime=%d&limit=200"
              % (sym, BAS, son))
        L = (d or {}).get("result", {}).get("list", []) or []
        if not L:
            break
        for x in L:
            out[int(x["fundingRateTimestamp"])] = float(x["fundingRate"])
        eski = min(int(x["fundingRateTimestamp"]) for x in L)
        if eski <= BAS or len(L) < 200 or eski >= son:
            break
        son = eski - 1
        _uyu()
    return out


def guvenli_yaz(yol, yeni_binance, yeni_bybit):
    """🔴 EZMEZ. Var olani okur, damgaya gore birlestirir, KISALIRSA hata firlatir."""
    birlesik = {"binance": {}, "bybit": {}}
    eski_n = 0
    if os.path.exists(yol):
        # 🔴 BOZUK DOSYAYI BOS SAYMA — o yol, bozuk dosyanin UZERINE yalnizca yeni
        #    veriyi yazardi = sessiz kayip. (taze_veri_indir.py'de ayni onarim.)
        try:
            with open(yol, encoding="utf-8") as f:
                mevcut = json.load(f)
        except Exception as e:
            raise RuntimeError("OKUNAMADI, uzerine YAZILMADI: %s (%s)" % (yol, e))
        for k in ("binance", "bybit"):
            for t, v in (mevcut.get(k) or {}).items():
                birlesik[k][str(t)] = v
        eski_n = len(birlesik["binance"]) + len(birlesik["bybit"])
    for t, v in yeni_binance.items():
        birlesik["binance"][str(t)] = v
    for t, v in yeni_bybit.items():
        birlesik["bybit"][str(t)] = v
    yeni_n = len(birlesik["binance"]) + len(birlesik["bybit"])
    if yeni_n < eski_n:
        raise RuntimeError("KISALMA: %s  %d -> %d (YAZILMADI)" % (yol, eski_n, yeni_n))
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(birlesik, f)
    os.replace(tmp, yol)                       # atomik (CLAUDE.md kurali)
    return yeni_n, eski_n


# ---------------------------------------------------------------------------
def evren():
    bi = g("https://fapi.binance.com/fapi/v1/exchangeInfo")
    bset = set(x["symbol"] for x in bi["symbols"]
               if x.get("contractType") == "PERPETUAL"
               and x.get("quoteAsset") == "USDT" and x.get("status") == "TRADING")
    by = g("https://api.bybit.com/v5/market/tickers?category=linear")
    yset = set(x["symbol"] for x in by["result"]["list"] if x["symbol"].endswith("USDT"))
    kl = set()
    if os.path.isdir(KLINES):
        for f in os.listdir(KLINES):
            if f.endswith(".json"):
                kl.add(f[:-5].replace("_1h", ""))
    ortak = sorted(bset & yset)
    return [s for s in ortak if s in kl or s.replace("USDT", "") in kl]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="ilk N sembol (deneme icin)")
    a = ap.parse_args()

    os.makedirs(VERI, exist_ok=True)
    syms = evren()
    if a.limit:
        syms = syms[:a.limit]
    print("=" * 88)
    print("CAPRAZ BORSA INDIRICI — on-kayit a0e52c5")
    print("=" * 88)
    print("pencere : %s .. %s"
          % (datetime.datetime.fromtimestamp(BAS / 1000).strftime("%Y-%m-%d"),
             datetime.datetime.fromtimestamp(SON / 1000).strftime("%Y-%m-%d")))
    print("sembol  : %d" % len(syms))
    print("hedef   : %s   (🔴 mevcut hicbir arsive dokunulmaz)" % VERI)
    print()

    t0 = time.time()
    ok = atlandi = hata = 0
    for i, s in enumerate(syms, 1):
        yol = os.path.join(VERI, "%s.json" % s)
        if os.path.exists(yol):
            try:
                with open(yol, encoding="utf-8") as f:
                    m = json.load(f)
                if len(m.get("binance") or {}) > 100 and len(m.get("bybit") or {}) > 100:
                    atlandi += 1
                    continue
            except Exception:
                pass                            # bozuksa asagida yeniden indirilir
        try:
            fb = binance_seri(s)
            _uyu()
            fy = bybit_seri(s)
            guvenli_yaz(yol, fb, fy)
            ok += 1
            if i % 20 == 0 or i <= 3:
                gecen = time.time() - t0
                kalan = (gecen / max(1, ok + hata)) * (len(syms) - i) / 60
                print("[%4d/%d] %-16s binance=%-5d bybit=%-5d  (kalan ~%.0f dk)"
                      % (i, len(syms), s, len(fb), len(fy), kalan))
        except RuntimeError as e:
            if "418" in str(e):
                print("🔴 %s" % e)
                break
            print("[%4d/%d] %-16s HATA %s" % (i, len(syms), s, str(e)[:60]))
            hata += 1
        except Exception as e:
            print("[%4d/%d] %-16s HATA %s" % (i, len(syms), s, str(e)[:60]))
            hata += 1
        _uyu()

    print()
    print("BITTI: indirilen %d · atlandi %d · hata %d · sure %.1f dk"
          % (ok, atlandi, hata, (time.time() - t0) / 60))
    print("Mevcut arsivlere yazim: YOK · Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
