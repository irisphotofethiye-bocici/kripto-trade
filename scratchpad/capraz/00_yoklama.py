#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CAPRAZ BORSA — YOKLAMA (2026-09-05)

On-kayittan ONCE kosulan FIZIBILITE probu. Hukum YOK, olcum YOK.
(basis olcumunun 00_yoklama.py deseni birebir tekrarlaniyor.)

BES SORU:
  1) Kac ortak sembol, Bybit fonlama gecmisi ne kadar geriye gidiyor?
  2) 🔴 FONLAMA ARALIGI: Binance ve Bybit ayni sembolde AYNI araligi mi kullaniyor?
     (CLAUDE.md 'funding_gecmis birim kirilmasi' ile AYNI hata sinifi — iki farkli
      sey ayni adi tasirsa join sessizce yanlis cikar.)
  3) Fark gercekten oynuyor mu, yoksa arbitrajla sifirlanmis mi?
  4) ELEME TESTI onizlemesi: fark, Binance fonlamasinin gurultulu kopyasi mi?
  5) Indirme suresi tahmini.

Salt-okunur. Ucretli cagri YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, time, math, urllib.request, statistics as stx

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KLINES = os.path.join(KOK, "scratchpad", "klines_1h_uzun")
ORNEK = 20          # yoklama icin sembol sayisi


def g(url, timeout=25):
    for deneme in range(3):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception:
            if deneme == 2:
                raise
            time.sleep(1.5 * (deneme + 1))
    return None


def binance_semboller():
    d = g("https://fapi.binance.com/fapi/v1/exchangeInfo")
    return set(x["symbol"] for x in d["symbols"]
               if x.get("contractType") == "PERPETUAL"
               and x.get("quoteAsset") == "USDT" and x.get("status") == "TRADING")


def bybit_semboller():
    d = g("https://api.bybit.com/v5/market/tickers?category=linear")
    return set(x["symbol"] for x in d["result"]["list"] if x["symbol"].endswith("USDT"))


def binance_fonlama(sym, limit=1000):
    d = g("https://fapi.binance.com/fapi/v1/fundingRate?symbol=%s&limit=%d" % (sym, limit))
    return [(int(x["fundingTime"]), float(x["fundingRate"])) for x in d]


def bybit_fonlama(sym, limit=200):
    d = g("https://api.bybit.com/v5/market/funding/history"
          "?category=linear&symbol=%s&limit=%d" % (sym, limit))
    L = d.get("result", {}).get("list", []) or []
    return [(int(x["fundingRateTimestamp"]), float(x["fundingRate"])) for x in L]


def aralik_saat(seri):
    """Ardisik damgalardan fonlama araligini SAAT olarak cikar (medyan)."""
    if len(seri) < 5:
        return None
    ts = sorted(t for t, _ in seri)
    farklar = [(ts[i + 1] - ts[i]) / 3600000.0 for i in range(len(ts) - 1)]
    farklar = [f for f in farklar if 0.5 <= f <= 25]
    if not farklar:
        return None
    return round(stx.median(farklar), 2)


def spearman(xs, ys):
    n = len(xs)
    if n < 8:
        return None

    def sirala(v):
        idx = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(idx):
            j = i
            while j + 1 < len(idx) and v[idx[j + 1]] == v[idx[i]]:
                j += 1
            ort = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[idx[k]] = ort
            i = j + 1
        return r
    rx, ry = sirala(xs), sirala(ys)
    mx, my = stx.mean(rx), stx.mean(ry)
    pay = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    px = math.sqrt(sum((a - mx) ** 2 for a in rx))
    py = math.sqrt(sum((b - my) ** 2 for b in ry))
    return pay / (px * py) if px and py else None


def main():
    print("=" * 92)
    print("CAPRAZ BORSA — YOKLAMA (on-kayittan ONCE, hukum YOK)")
    print("=" * 92)
    print()

    print("### 1) EVREN")
    bi, by = binance_semboller(), bybit_semboller()
    ortak = sorted(bi & by)
    print("   binance perp USDT : %d" % len(bi))
    print("   bybit  linear USDT: %d" % len(by))
    print("   ORTAK             : %d   (yalniz-binance %d)" % (len(ortak), len(bi - by)))

    kl = set()
    if os.path.isdir(KLINES):
        for f in os.listdir(KLINES):
            if f.endswith(".json"):
                kl.add(f[:-5].replace("_1h", ""))
    kapsam = [s for s in ortak if s in kl or s.replace("USDT", "") in kl]
    print("   klines_1h_uzun'da fiyati olan ortak sembol: %d  (%s)"
          % (len(kapsam), "yeterli" if len(kapsam) > 200 else "🔴 DUSUK"))
    print()

    ornek = ortak[:ORNEK]
    print("### 2) 🔴 FONLAMA ARALIGI — iki borsa ayni birimi mi kullaniyor?")
    print("   %-14s %12s %12s %10s" % ("sembol", "binance sa", "bybit sa", "AYNI MI"))
    ayni, farkli, veri = 0, 0, []
    t0 = time.time()
    for s in ornek:
        try:
            fb = binance_fonlama(s, 200)
            fy = bybit_fonlama(s, 200)
        except Exception as hata:
            print("   %-14s HATA %s" % (s, str(hata)[:40]))
            continue
        ab, ay_ = aralik_saat(fb), aralik_saat(fy)
        es = "EVET" if (ab and ay_ and abs(ab - ay_) < 0.6) else "🔴 HAYIR"
        if es == "EVET":
            ayni += 1
        else:
            farkli += 1
        print("   %-14s %12s %12s %10s"
              % (s, ab if ab else "?", ay_ if ay_ else "?", es))
        veri.append((s, fb, fy, ab, ay_))
    sure = time.time() - t0
    print()
    print("   -> ayni aralik: %d / farkli: %d" % (ayni, farkli))
    if farkli:
        print("   🔴 ARALIK FARKLI OLAN VAR -> ham oran KIYASLANAMAZ.")
        print("      Zorunlu: her iki tarafi GUNLUK orana cevir (oran * 24/aralik).")
    print()

    print("### 3) FARK GERCEKTEN OYNUYOR MU? (gunluk orana cevrilmis, %)")
    print("   %-14s %11s %11s %11s %11s" %
          ("sembol", "binance ort", "bybit ort", "fark ort", "fark std"))
    tum_fark, tum_bin = [], []
    for s, fb, fy, ab, ay_ in veri:
        if not ab or not ay_:
            continue
        hb = dict((t // 3600000, r * 24.0 / ab) for t, r in fb)
        hy = dict((t // 3600000, r * 24.0 / ay_) for t, r in fy)
        ortak_t = sorted(set(hb) & set(hy))
        if len(ortak_t) < 20:
            continue
        d = [(hb[t] - hy[t]) * 100 for t in ortak_t]
        b = [hb[t] * 100 for t in ortak_t]
        tum_fark += d
        tum_bin += b
        print("   %-14s %+10.4f %+10.4f %+10.4f %10.4f"
              % (s, stx.mean(b), stx.mean([hy[t] * 100 for t in ortak_t]),
                 stx.mean(d), stx.stdev(d) if len(d) > 1 else 0))
    print()
    if tum_fark:
        af = sorted(abs(x) for x in tum_fark)
        print("   HAVUZ: N=%d  fark ort %+.4f%%  std %.4f%%" %
              (len(tum_fark), stx.mean(tum_fark), stx.stdev(tum_fark)))
        print("          |fark| medyan %.4f%%  ·  %%90 %.4f%%" %
              (af[len(af) // 2], af[int(len(af) * 0.9)]))
        print("   -> %s" % ("✅ fark OYNUYOR, arbitrajla sifirlanmamis"
                            if af[len(af) // 2] > 0.005 else
                            "🔴 fark ~SIFIR — arbitrajlanmis, sinyal beklenmez"))
    print()

    print("### 4) ELEME TESTI ONIZLEMESI — fark, Binance fonlamasinin kopyasi mi?")
    if tum_fark and tum_bin:
        r = spearman(tum_bin, tum_fark)
        print("   spearman(binance fonlama, FARK) = %s" %
              (("%+.3f" % r) if r is not None else "yok"))
        print("   (basis olcumunde eleme esigi: elenenler %%60 ve %%51 korelasyondaydi;")
        print("    basis %%3,7 ile gecmisti. |r| buyukse fark YENI BILGI DEGIL.)")
        if r is not None:
            print("   -> %s" % ("✅ dusuk korelasyon, bagimsiz bilgi adayi" if abs(r) < 0.5
                                else "🔴 YUKSEK korelasyon — fark buyuk olcude Binance fonlamasi"))
    print()

    print("### 5) INDIRME MALIYETI")
    if ornek:
        sn = sure / len(ornek)
        print("   yoklamada sembol basi %.1f sn (2 cagri)" % sn)
        print("   TAM indirme: 2 yil icin binance ~3 cagri + bybit ~11 cagri = ~14 cagri")
        print("   tahmin: %d sembol x ~%.1f sn = ~%.0f dakika"
              % (len(kapsam), sn * 7, len(kapsam) * sn * 7 / 60))
    print()
    print("Ucretli cagri: YOK · Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
