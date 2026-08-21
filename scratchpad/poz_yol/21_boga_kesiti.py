#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AYI vs BOGA — ayni alanlar, iki donemde AYRI.

KULLANICI (2026-08-21): "iyi de zaten ayi-notr o veri. son 3 gune bakarsan
o tutmaz. ayida her sey asagi yonlu, simdi her sey yukari dondu."

HAKLI: 20_bizim_veri.py'nin penceresi 2026-06-24 -> 08-18, yani boganin
kirildigi gunun (08-19 18:15) BIR GUN ONCESI. %100 ayi/notr.
"chg24 yuksekleri shortla" bulgusu, "ayida her sey duser"in baska ifadesi olabilir.

TEST: ayni alanlar, ayni yontem, iki donem AYRI:
   AYI/NOTR : 2026-06-24 .. 2026-08-18
   BOGA     : 2026-08-19 .. simdi
Isaret donuyorsa bulgu rejime bagli -> tek basina KURAL OLMAZ.

⚠️ KISA UFUK ZORUNLU: boga donemi 3 gunluk; 72 saatlik ileri getiri yok.
   Iki donem de AYNI ufukla olculur (1sa, 3sa, 6sa) yoksa kiyas bozulur.

SALT OKUMA.
"""
import os, json, datetime, collections, bisect, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
PROJE = os.path.dirname(SCRATCH)
KLINE = os.path.join(SCRATCH, "klines_1h_uzun")
ARSIV = os.path.join(PROJE, "radar_archive.jsonl")

UFUK = [1, 3, 6]
BOGA_BAS = "2026-08-19"
ALAN = ["score", "chg24", "pos", "vol_x", "rel3", "funding", "oi3", "oi24", "comp", "last3"]


def kur():
    ki = {}
    for fn in os.listdir(KLINE):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(KLINE, fn), encoding="utf-8") as f:
                b = json.load(f)
        except Exception:
            continue
        if len(b) > 50:
            ki[fn[:-5]] = ([x["t"] for x in b], b)
    out = []
    with open(ARSIV, encoding="utf-8") as f:
        for satir in f:
            if not satir.strip():
                continue
            try:
                x = json.loads(satir)
            except Exception:
                continue
            sym = x.get("sym")
            if sym not in ki:
                continue
            ts, b = ki[sym]
            t = int(datetime.datetime.strptime(x["ts"], "%Y-%m-%d %H:%M").timestamp() * 1000)
            i = bisect.bisect_right(ts, t)
            if i >= len(b) - max(UFUK) - 1:
                continue
            ref = b[i]["o"]
            if ref <= 0:
                continue
            r = {"sym": sym, "gun": x["ts"][:10]}
            for k in ALAN:
                r[k] = x.get(k)
            for u in UFUK:
                r["f%d" % u] = (b[i + u]["c"] - ref) / ref * 100
            out.append(r)
    return out


def tablo(kayit, ad, ufuk):
    f = lambda x: x["f%d" % ufuk]
    if len(kayit) < 500:
        print("  %s: N=%d yetersiz" % (ad, len(kayit)))
        return {}
    print("\n  %s   N=%d · gun=%d · evren ort %+.4f%%"
          % (ad, len(kayit), len({x["gun"] for x in kayit}), sx.mean(f(x) for x in kayit)))
    print("  %-12s %8s %10s %10s %10s %9s"
          % ("alan", "N", "ALT %25", "UST %25", "fark", "gun-t"))
    out = {}
    for a in ALAN:
        v = [x for x in kayit if isinstance(x.get(a), (int, float))]
        if len(v) < 400:
            continue
        d = sorted(x[a] for x in v)
        q1, q3 = d[len(d) // 4], d[3 * len(d) // 4]
        if q1 == q3:
            continue
        alt = [x for x in v if x[a] <= q1]
        ust = [x for x in v if x[a] >= q3]
        ma, mu = sx.mean(f(x) for x in alt), sx.mean(f(x) for x in ust)
        g = collections.defaultdict(lambda: [[], []])
        for x in alt:
            g[x["gun"]][0].append(f(x))
        for x in ust:
            g[x["gun"]][1].append(f(x))
        gd = [sx.mean(b2) - sx.mean(a2) for a2, b2 in g.values() if len(a2) >= 5 and len(b2) >= 5]
        t = None
        if len(gd) >= 3:
            se = sx.stdev(gd) / len(gd) ** 0.5 if len(gd) > 1 else 0
            t = sx.mean(gd) / se if se else None
        out[a] = mu - ma
        print("  %-12s %8d %+10.4f %+10.4f %+10.4f %9s"
              % (a, len(v), ma, mu, mu - ma, "%.2f" % t if t is not None else "-"))
    return out


if __name__ == "__main__":
    print("veri kuruluyor...")
    k = kur()
    ayi = [x for x in k if x["gun"] < BOGA_BAS]
    bog = [x for x in k if x["gun"] >= BOGA_BAS]
    print("AYI/NOTR: %d kayit (%d gun) · BOGA: %d kayit (%d gun)"
          % (len(ayi), len({x['gun'] for x in ayi}), len(bog), len({x['gun'] for x in bog})))
    for u in UFUK:
        print("\n" + "=" * 88)
        print("UFUK +%d SAAT" % u)
        print("=" * 88)
        a = tablo(ayi, "AYI / NOTR  (06-24 .. 08-18)", u)
        b = tablo(bog, "BOGA        (08-19 .. simdi)", u)
        if a and b:
            print("\n  ISARET KARSILASTIRMASI (+%dsa):" % u)
            don = []
            for al in ALAN:
                if al in a and al in b:
                    ayni = (a[al] * b[al]) > 0
                    if not ayni:
                        don.append(al)
                    print("    %-12s ayi %+8.4f  boga %+8.4f   %s"
                          % (al, a[al], b[al], "ayni" if ayni else "*** ISARET DONDU ***"))
            print("    -> isaret donen alan: %d/%d  (%s)"
                  % (len(don), len([x for x in ALAN if x in a and x in b]),
                     ", ".join(don) if don else "yok"))
    print("\nbot dosyalarina yazim: YOK")
