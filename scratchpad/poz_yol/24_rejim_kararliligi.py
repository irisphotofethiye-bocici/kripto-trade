#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REJIM KARARLILIGI — ayni iliski ALTI farkli pencerede tutuyor mu?

KULLANICI (2026-08-21): "sectigin donem yine yanlis, olcum yanlis cikar,
durum ayni degil ama olc."

HAKLI OLDUGU NOKTA: ATH bolgesi bugunun durumu DEGIL — orada fonlama tavana
yapisik (%55-63, olculdu), burada tabanda (0,0050). Oradan cikan sonuc buraya
DOGRUDAN TASINMAZ. Yine de olculuyor: farkli cikmasi da bilgidir.

OLCULEN: kesitsel iliski — "son donemde cok kosan, sonraki 24 saatte gorece
geri kaliyor mu?" Alanlar KLINE'DAN uretiliyor (radar_archive 2026-06'da
basliyor, eski pencerelerde yok).

⚠️ GUN-KUMELI t KULLANILIR, havuzlanmis fark DEGIL. Havuzlanmis fark seviye
kaymasini iliskiyle karistiriyor (21_boga_kesiti.py'de bu hata yapildi ve
23_toparlanma_bacagi.py'de yakalandi).

SALT OKUMA.
"""
import os, json, datetime, collections, bisect, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
KLINE = os.path.join(SCRATCH, "klines_1h_uzun")
FUND = os.path.join(SCRATCH, "funding_gecmis")
UFUK = 24
ADIM = 4
MIN_QV = 125000
ALAN = ["chg24", "pos", "vol_x", "rel3", "last3", "funding"]


def ms(s):
    return int(datetime.datetime.strptime(s, "%Y-%m-%d").timestamp() * 1000)


PENCERE = [
    ("ATH-BOLGE 24-09/12", ms("2024-09-15"), ms("2024-12-15")),
    ("ATH-BOLGE 25-06/10", ms("2025-06-01"), ms("2025-10-15")),
    ("TOPARLANMA 25-04/05", ms("2025-04-03"), ms("2025-05-15")),
    ("DERIN-AYI 26-01/03", ms("2026-01-05"), ms("2026-03-20")),
    ("AYI 26-06/08", ms("2026-06-24"), ms("2026-08-19")),
    ("BUGUN 26-08-19+", ms("2026-08-19"), ms("2026-08-22")),
]


def topla():
    with open(os.path.join(KLINE, "BTC.json"), encoding="utf-8") as f:
        btc = {x["t"]: x["c"] for x in json.load(f)}
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
                fr = [x["r"] for x in d]
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
            c24 = b[i - 24]["c"]
            c3 = b[i - 3]["c"]
            if not c24 or not c3 or not x["c"]:
                continue
            pen = b[i - 20:i + 1]
            lo = min(z["l"] for z in pen)
            hi = max(z["h"] for z in pen)
            hac = sx.mean(z.get("qv") or 0 for z in b[i - 24:i])
            ref = b[i + 1]["o"]
            if ref <= 0:
                continue
            r = {"gun": datetime.datetime.fromtimestamp(x["t"] / 1000).strftime("%Y-%m-%d"),
                 "chg24": (x["c"] - c24) / c24 * 100,
                 "pos": (x["c"] - lo) / (hi - lo) if hi > lo else 0.5,
                 "vol_x": ((x.get("qv") or 0) / hac) if hac > 0 else None,
                 "last3": (x["c"] - c3) / c3 * 100,
                 "f": (b[i + UFUK]["c"] - ref) / ref * 100}
            b0, b1 = btc.get(b[i - 3]["t"]), btc.get(x["t"])
            r["rel3"] = r["last3"] - (b1 - b0) / b0 * 100 if (b0 and b1) else None
            if ft:
                k = bisect.bisect_right(ft, x["t"]) - 1
                r["funding"] = fr[k] if k >= 0 else None
            else:
                r["funding"] = None
            kova[ad].append(r)
        if n % 150 == 0:
            print("  ... %d/%d" % (n, len(dosya)))
    return kova


def gun_t(v, a):
    """UST %25 ile ALT %25 arasindaki farkin GUN-KUMELI t'si."""
    w = [x for x in v if isinstance(x.get(a), (int, float))]
    if len(w) < 300:
        return None, 0, 0
    d = sorted(x[a] for x in w)
    q1, q3 = d[len(d) // 4], d[3 * len(d) // 4]
    if q1 == q3:
        return None, 0, 0
    g = collections.defaultdict(lambda: [[], []])
    for x in w:
        if x[a] <= q1:
            g[x["gun"]][0].append(x["f"])
        elif x[a] >= q3:
            g[x["gun"]][1].append(x["f"])
    gd = [sx.mean(b2) - sx.mean(a2) for a2, b2 in g.values() if len(a2) >= 5 and len(b2) >= 5]
    if len(gd) < 5:
        return None, len(gd), 0
    se = sx.stdev(gd) / len(gd) ** 0.5
    return (sx.mean(gd) / se if se else None), len(gd), sx.mean(gd)


if __name__ == "__main__":
    print("veri kuruluyor (566 sembol, 6 pencere)...")
    k = topla()
    print()
    print("=" * 112)
    print("REJIM KARARLILIGI - gun-kumeli t (UST ceyrek eksi ALT ceyrek, ileri +%d saat)" % UFUK)
    print("=" * 112)
    print("%-22s %9s %6s %11s" % ("pencere", "N", "gun", "evren ort%"))
    for ad, _, _ in PENCERE:
        v = k[ad]
        if v:
            print("%-22s %9d %6d %+11.4f"
                  % (ad, len(v), len({x["gun"] for x in v}), sx.mean(x["f"] for x in v)))
    print()
    bas = "%-9s" % "alan"
    for ad, _, _ in PENCERE:
        bas += "%20s" % (ad[:12] + " t|etki")
    print(bas)
    print("-" * 112)
    for a in ALAN:
        sat, isr = "%-9s" % a, []
        for ad, _, _ in PENCERE:
            t, ng, ef = gun_t(k[ad], a)
            sat += "%20s" % ("%+.2f | %+.3f" % (t, ef) if t is not None else "-")
            if t is not None:
                isr.append(t)
        ayni = sum(1 for x in isr if x * isr[0] > 0) if isr else 0
        guclu = sum(1 for x in isr if abs(x) >= 2.0)
        print(sat + "   %d/%d ayni · |t|>=2: %d" % (ayni, len(isr), guclu))
    print()
    print("OKUMA: bir alan TUM pencerelerde ayni isaretteyse REJIM-KARARLI.")
    print("UYARI: ATH bolgesi bugunun durumu DEGIL (fonlama orada tavanda) - ayni")
    print("   cikmasi bile dogrudan transfer anlamina gelmez.")
    print("bot dosyalarina yazim: YOK")
