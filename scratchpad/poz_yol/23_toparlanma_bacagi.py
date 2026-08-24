#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TOPARLANMA BACAGI — 2025-04-03..05-14 vs bugun. Alanlar orada ne yapiyor?

KULLANICI (2026-08-21): "365 gunde olcum dogru sonuc vermez, ama 3 nisan -
14 mayis 2025 arasini olc."

NEDEN DOGRU SECIM: o pencere ayidan ATH'ye giden TOPARLANMA BACAGI —
bugunun analogu, ama 42 GUNU var (bugunkunun 2 gunune karsi).
   2025-04-03..05-14 : 85.623 -> 103.500 (%+20,88) · zirveden -25,2% -> -5,9%
   2026-08-19..simdi :  64.547 ->  73.658 (%+14,11) · zirveden -45,3% -> -41,6%

⚠️ SINIR: gecko (TOTAL/dominans) 2025-08-22'de basliyor -> o pencerede YOK.
   radar_archive 2026-06-24'te basliyor -> o pencerede YOK.
   Olculebilen: kline'dan turetilen alanlar + fonlama gecmisi.
   Bu yuzden alanlar radar'dan degil KLINE'DAN yeniden uretiliyor
   (chg24 · pos · vol_x · rel3 · last3) — tanimlar radar'inkiyle ayni ruhta.

KIYAS PENCERELERI:
   A) TOPARLANMA  2025-04-03 .. 2025-05-14   (42 gun)
   B) AYI         2026-06-24 .. 2026-08-18   (56 gun, onceki olcum)
   C) BUGUN       2026-08-19 .. simdi        (2 gun)

SALT OKUMA.
"""
import os, json, datetime, collections, bisect, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
KLINE = os.path.join(SCRATCH, "klines_1h_uzun")
FUND = os.path.join(SCRATCH, "funding_gecmis")
UFUK = [6, 24]
ADIM = 4          # 4 saatte bir ornek (ortusmeyi azalt)
MIN_QV = 125000   # saatlik ~3M$/24


def ms(s):
    return int(datetime.datetime.strptime(s, "%Y-%m-%d").timestamp() * 1000)


PENCERE = [("TOPARLANMA 2025-04/05", ms("2025-04-03"), ms("2025-05-15")),
           ("AYI 2026-06/08", ms("2026-06-24"), ms("2026-08-19")),
           ("BUGUN 2026-08-19+", ms("2026-08-19"), ms("2026-08-22"))]
ALAN = ["chg24", "pos", "vol_x", "rel3", "last3", "funding"]


def btc_serisi():
    with open(os.path.join(KLINE, "BTC.json"), encoding="utf-8") as f:
        b = json.load(f)
    return {x["t"]: x["c"] for x in b}


def topla():
    btc = btc_serisi()
    kova = {ad: [] for ad, _, _ in PENCERE}
    dosya = sorted(f for f in os.listdir(KLINE) if f.endswith(".json"))
    for n, fn in enumerate(dosya, 1):
        sym = fn[:-5]
        if sym == "BTC":
            continue
        try:
            with open(os.path.join(KLINE, fn), encoding="utf-8") as f:
                b = json.load(f)
        except Exception:
            continue
        if len(b) < 100:
            continue
        fp = os.path.join(FUND, fn)
        ft, fr = [], []
        if os.path.exists(fp):
            try:
                with open(fp, encoding="utf-8") as f:
                    d = json.load(f)
                ft = [x["t"] for x in d]
                fr = [x["r"] for x in d]
            except Exception:
                pass
        for i in range(48, len(b) - max(UFUK) - 1, ADIM):
            x = b[i]
            if (x.get("qv") or 0) < MIN_QV:
                continue
            ad = None
            for a, t0, t1 in PENCERE:
                if t0 <= x["t"] < t1:
                    ad = a
                    break
            if ad is None:
                continue
            c0 = b[i - 24]["c"]
            if not c0 or not x["c"]:
                continue
            pen = b[i - 20:i + 1]
            lo = min(z["l"] for z in pen)
            hi = max(z["h"] for z in pen)
            hac = sx.mean(z.get("qv") or 0 for z in b[i - 24:i])
            r = {"sym": sym,
                 "gun": datetime.datetime.fromtimestamp(x["t"] / 1000).strftime("%Y-%m-%d"),
                 "chg24": (x["c"] - c0) / c0 * 100,
                 "pos": (x["c"] - lo) / (hi - lo) if hi > lo else 0.5,
                 "vol_x": ((x.get("qv") or 0) / hac) if hac > 0 else None,
                 "last3": (x["c"] - b[i - 3]["c"]) / b[i - 3]["c"] * 100 if b[i - 3]["c"] else None}
            bt0, bt1 = btc.get(b[i - 3]["t"]), btc.get(x["t"])
            r["rel3"] = (r["last3"] - (bt1 - bt0) / bt0 * 100) if (bt0 and bt1 and r["last3"] is not None) else None
            if ft:
                k = bisect.bisect_right(ft, x["t"]) - 1
                r["funding"] = fr[k] if k >= 0 else None
            else:
                r["funding"] = None
            ref = b[i + 1]["o"]
            if ref <= 0:
                continue
            for u in UFUK:
                r["f%d" % u] = (b[i + u]["c"] - ref) / ref * 100
            kova[ad].append(r)
        if n % 150 == 0:
            print("  ... %d/%d" % (n, len(dosya)))
    return kova


def tablo(v, ad, ufuk):
    f = lambda x: x["f%d" % ufuk]
    if len(v) < 500:
        print("\n  %s: N=%d yetersiz" % (ad, len(v)))
        return {}
    print("\n  %s   N=%d · gun=%d · evren ort %+.4f%%"
          % (ad, len(v), len({x["gun"] for x in v}), sx.mean(f(x) for x in v)))
    print("  %-10s %8s %10s %10s %10s %8s" % ("alan", "N", "ALT %25", "UST %25", "fark", "gun-t"))
    out = {}
    for a in ALAN:
        w = [x for x in v if isinstance(x.get(a), (int, float))]
        if len(w) < 300:
            continue
        d = sorted(x[a] for x in w)
        q1, q3 = d[len(d) // 4], d[3 * len(d) // 4]
        if q1 == q3:
            continue
        alt = [x for x in w if x[a] <= q1]
        ust = [x for x in w if x[a] >= q3]
        ma, mu = sx.mean(f(x) for x in alt), sx.mean(f(x) for x in ust)
        g = collections.defaultdict(lambda: [[], []])
        for x in alt:
            g[x["gun"]][0].append(f(x))
        for x in ust:
            g[x["gun"]][1].append(f(x))
        gd = [sx.mean(b2) - sx.mean(a2) for a2, b2 in g.values() if len(a2) >= 5 and len(b2) >= 5]
        t = None
        if len(gd) >= 5:
            se = sx.stdev(gd) / len(gd) ** 0.5
            t = sx.mean(gd) / se if se else None
        out[a] = mu - ma
        print("  %-10s %8d %+10.4f %+10.4f %+10.4f %8s"
              % (a, len(w), ma, mu, mu - ma, "%.2f" % t if t is not None else "-"))
    return out


if __name__ == "__main__":
    print("veri kuruluyor (566 sembol)...")
    k = topla()
    for a, _, _ in PENCERE:
        print("  %-26s %d kayit" % (a, len(k[a])))
    for u in UFUK:
        print("\n" + "=" * 92)
        print("UFUK +%d SAAT" % u)
        print("=" * 92)
        s = {}
        for a, _, _ in PENCERE:
            s[a] = tablo(k[a], a, u)
        t, ayi = s.get(PENCERE[0][0], {}), s.get(PENCERE[1][0], {})
        if t and ayi:
            print("\n  TOPARLANMA vs AYI (+%dsa):" % u)
            for a in ALAN:
                if a in t and a in ayi:
                    print("    %-10s toparlanma %+8.4f   ayi %+8.4f   %s"
                          % (a, t[a], ayi[a], "ayni" if t[a] * ayi[a] > 0 else "*** DONDU ***"))
    print("\nbot dosyalarina yazim: YOK")
