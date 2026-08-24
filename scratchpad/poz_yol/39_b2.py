#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 OLCUTU — 37_pos_mekanik.py bunu hesaplamayi ATLAMISTI.

ON_KAYIT_pos_mekanik.md: "B = B1 ve B2".
   B1 dusuk-pos LONG kolunun NET ortalamasi > 0, >=3/5 pencerede   -> 37 hesapladi
   B2 AYNI KOLUN gun-kumeli t >= +2,0, >=2 pencerede               -> 37 ATLADI

B2, farkin degil KOLUN KENDI ortalamasinin t'sidir (sifirdan farkli mi).
Olcut ON-KAYITTAN aynen alinir, DEGISTIRILMEZ.

Fonlama duzeltmesi dahil (funding_indir.py:67 zaten yuzde -> ekstra *100 YOK).
SALT OKUMA.
"""
import os, sys, json, datetime, collections, bisect, statistics as sx, math

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
KLINE = os.path.join(SCRATCH, "klines_1h_uzun")
FUND = os.path.join(SCRATCH, "funding_gecmis")

UFUK, ADIM, MIN_QV = 24, 4, 125000
STOP, HEDEF, MALIYET = 5.0, 10.0, 0.1726


def ms(s):
    return int(datetime.datetime.strptime(s, "%Y-%m-%d").timestamp() * 1000)


PENCERE = [
    ("ATH 24-09/12", ms("2024-09-15"), ms("2024-12-15")),
    ("ATH 25-06/10", ms("2025-06-01"), ms("2025-10-15")),
    ("TOPARLANMA 25-04", ms("2025-04-03"), ms("2025-05-15")),
    ("DERIN-AYI 26-01", ms("2026-01-05"), ms("2026-03-20")),
    ("AYI 26-06/08", ms("2026-06-24"), ms("2026-08-19")),
]


def topla():
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
        ft, fr = [], []
        fp = os.path.join(FUND, fn)
        if os.path.exists(fp):
            try:
                with open(fp, encoding="utf-8") as f:
                    d = json.load(f)
                ft = [x["t"] for x in d]
                fr = [x["r"] for x in d]          # ZATEN yuzde
            except Exception:
                pass
        for i in range(48, len(b) - UFUK - 2, ADIM):
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
            pen = b[i - 20:i + 1]
            lo = min(z["l"] for z in pen)
            hi = max(z["h"] for z in pen)
            ref = b[i + 1]["o"]
            if ref <= 0 or hi <= lo:
                continue
            sonbar = min(i + UFUK, len(b) - 1)
            sl, tp = ref * (1 - STOP / 100), ref * (1 + HEDEF / 100)
            mek, cj = None, sonbar
            for j in range(i + 1, sonbar + 1):
                z = b[j]
                if z["l"] <= sl:
                    mek, cj = -STOP, j
                    break
                if z["h"] >= tp:
                    mek, cj = HEDEF, j
                    break
            if mek is None:
                mek = (b[sonbar]["c"] - ref) / ref * 100
            f = 0.0
            if ft:
                a0 = bisect.bisect_right(ft, b[i + 1]["t"])
                f = -sum(fr[k] for k in range(a0, bisect.bisect_right(ft, b[cj]["t"])))
            kova[ad].append({
                "gun": datetime.datetime.fromtimestamp(x["t"] / 1000).strftime("%Y-%m-%d"),
                "pos": (x["c"] - lo) / (hi - lo),
                "net": mek - MALIYET + f})
        if n % 200 == 0:
            print("  ... %d/%d" % (n, len(dosya)))
            sys.stdout.flush()
    return kova


def kol_t(v, alt=True):
    """KOLUN KENDI ortalamasinin gun-kumeli t'si (sifirdan farkli mi)."""
    d = sorted(x["pos"] for x in v)
    q1, q3 = d[len(d) // 4], d[3 * len(d) // 4]
    g = collections.defaultdict(list)
    for x in v:
        if (x["pos"] <= q1) if alt else (x["pos"] >= q3):
            g[x["gun"]].append(x["net"])
    gunluk = [sx.mean(w) for w in g.values() if len(w) >= 5]
    if len(gunluk) < 8:
        return None, None, len(gunluk)
    m, sd = sx.mean(gunluk), sx.pstdev(gunluk)
    return m, (m / (sd / math.sqrt(len(gunluk))) if sd > 0 else None), len(gunluk)


if __name__ == "__main__":
    print("B2 OLCUTU — dusuk-pos LONG kolunun KENDI gun-kumeli t'si")
    print("olcut (ON_KAYIT): t >= +2,0 en az 2 pencerede\n")
    kova = topla()
    gecen = 0
    print("  %-20s %10s %8s %6s   %s" % ("pencere", "ALT ort", "gun-t", "gun", "durum"))
    print("  " + "-" * 62)
    for ad, _, _ in PENCERE:
        v = kova[ad]
        if len(v) < 300:
            continue
        m, t, ng = kol_t(v, alt=True)
        ok = t is not None and t >= 2.0
        gecen += 1 if ok else 0
        print("  %-20s %+10.3f %+8.2f %6d   %s"
              % (ad, m, t if t is not None else float("nan"), ng,
                 "t>=2 EVET" if ok else "hayir"))
    print("\n  B2: %d/5 pencerede t >= +2,0  ->  %s"
          % (gecen, "GECTI" if gecen >= 2 else "DUSTU"))
    print("\nBot dosyalarina yazim: YOK")
