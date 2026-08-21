#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SADECE BIZIM VERI — radar_archive'in 29 alani x ILERI GETIRI.

KULLANICI (2026-08-21): "2 yillik veriyi bosver, sadece bizim veriye bak."

GEREKCE (olculdu): 2 yillik pencere en az uc rejimin KARISIMI; ayni kapinin
isareti rejimler arasi donuyor (16_rejim_kosullu.py). Ortalama hicbir gercek
kosula karsilik gelmiyor. Bizim veri ise TEK bir donem (derin ayi -> cikis)
ve 29 ALAN iceriyor — 2 yillik veride bunlarin 19'u YOK.

⚠️ IKI EVREN, ASLA KARISTIRILMAZ (olculdu: 3 numarali bulgu):
   A) TAM TARAMA   16 alan %100 dolu
   B) SKOR-SUZULMUS top_ls·smart·glob_ls·taker  %29,8 dolu
      -> B, radar'in "derin bakmaya deger" dedigi YUKSEK SKORLU adaylar
         (score medyani 19,2 vs 7,1). Kendi kontrol grubuyla olculur.

HER BULGUDA ZORUNLU: yogunlasma kontrolu (en iyi 3 sembol cikinca) —
bu oturumda dort hukmu ceviren tek test.

SALT OKUMA.
"""
import os, json, datetime, collections, bisect, statistics as sx, random

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
PROJE = os.path.dirname(SCRATCH)
KLINE = os.path.join(SCRATCH, "klines_1h_uzun")
ARSIV = os.path.join(PROJE, "radar_archive.jsonl")
ONBELLEK = os.path.join(HERE, "bizim_veri.json")
random.seed(97)

UFUKLAR = [6, 24, 72]        # saat
TAM = ["score", "chg24", "pos", "vol_x", "rel3", "funding", "oi3", "oi24",
       "comp", "last1", "last3", "dip_yakit", "ayrisma", "dusuk_float"]
SUZ = ["top_ls", "glob_ls", "taker"]


def kline_indeks():
    out = {}
    for fn in os.listdir(KLINE):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(KLINE, fn), encoding="utf-8") as f:
                b = json.load(f)
        except Exception:
            continue
        if len(b) < 50:
            continue
        out[fn[:-5]] = ([x["t"] for x in b], b)
    return out


def kur():
    if os.path.exists(ONBELLEK):
        with open(ONBELLEK, encoding="utf-8") as f:
            return json.load(f)
    print("kline indeksi...")
    ki = kline_indeks()
    print("  %d sembol" % len(ki))
    out, n, atlanan = [], 0, 0
    with open(ARSIV, encoding="utf-8") as f:
        for satir in f:
            n += 1
            if not satir.strip():
                continue
            try:
                x = json.loads(satir)
            except Exception:
                continue
            sym = x.get("sym")
            if sym not in ki:
                atlanan += 1
                continue
            ts, b = ki[sym]
            t = int(datetime.datetime.strptime(x["ts"], "%Y-%m-%d %H:%M").timestamp() * 1000)
            i = bisect.bisect_right(ts, t)          # SONRAKI bar = giris
            if i >= len(b) - max(UFUKLAR) - 1:
                continue
            ref = b[i]["o"]
            if ref <= 0:
                continue
            r = {"sym": sym, "gun": x["ts"][:10], "ts": x["ts"]}
            for k in TAM + SUZ:
                r[k] = x.get(k)
            for u in UFUKLAR:
                r["f%d" % u] = (b[i + u]["c"] - ref) / ref * 100
            out.append(r)
            if n % 40000 == 0:
                print("  ... %d satir, %d kayit" % (n, len(out)))
    print("  toplam %d kayit (kline'i olmayan %d atlandi)" % (len(out), atlanan))
    with open(ONBELLEK, "w", encoding="utf-8") as f:
        json.dump(out, f)
    return out


def yogunlasma(v, alan_f):
    """en iyi 3 sembol cikinca ne kalir"""
    s = collections.defaultdict(float)
    for x in v:
        s[x["sym"]] += alan_f(x)
    en = {k for k, _ in sorted(s.items(), key=lambda z: -z[1])[:3]}
    kalan = [x for x in v if x["sym"] not in en]
    return (sx.mean(alan_f(x) for x in kalan) if kalan else None), len(en)


def gun_t(v, alan_f):
    g = collections.defaultdict(list)
    for x in v:
        g[x["gun"]].append(alan_f(x))
    gun = [sx.mean(g[d]) for d in g if len(g[d]) >= 20]
    if len(gun) < 5:
        return None, 0, 0
    se = sx.stdev(gun) / len(gun) ** 0.5
    return (sx.mean(gun) / se if se else None), len(gun), sum(1 for x in gun if x > 0)


def alan_testi(kayit, alanlar, baslik, ufuk=24):
    print("\n" + "=" * 112)
    print("%s   N=%d · ufuk +%dsa" % (baslik, len(kayit), ufuk))
    print("=" * 112)
    f = lambda x: x["f%d" % ufuk]
    tum = sx.mean(f(x) for x in kayit)
    print("evren ortalamasi: %+.4f%%\n" % tum)
    print("%-14s %7s %10s %10s %10s %9s %8s %10s"
          % ("alan", "N", "ALT %25", "UST %25", "fark", "gun-t", "poz gun", "top3 cik."))
    print("-" * 96)
    for a in alanlar:
        v = [x for x in kayit if x.get(a) is not None and isinstance(x[a], (int, float))]
        if len(v) < 2000:
            print("%-14s %7d  N yetersiz" % (a, len(v)))
            continue
        d = sorted(x[a] for x in v)
        q1, q3 = d[len(d) // 4], d[3 * len(d) // 4]
        if q1 == q3:
            print("%-14s %7d  dagilim yok" % (a, len(v)))
            continue
        alt = [x for x in v if x[a] <= q1]
        ust = [x for x in v if x[a] >= q3]
        ma, mu = sx.mean(f(x) for x in alt), sx.mean(f(x) for x in ust)
        fark = mu - ma
        # gun-kumeli t: UST ile ALT farkinin gunluk ortalamasi
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
        # yogunlasma: UST kolundan en iyi 3 sembol cikinca
        yk, _ = yogunlasma(ust, f)
        isaret = "  <<<" if (t is not None and abs(t) >= 3.0) else ""
        print("%-14s %7d %+10.4f %+10.4f %+10.4f %9s %5d/%-3d %+10.4f%s"
              % (a, len(v), ma, mu, fark,
                 "%.2f" % t if t is not None else "-",
                 sum(1 for x in gd if x * (fark or 1) > 0), len(gd),
                 yk if yk is not None else float("nan"), isaret))


if __name__ == "__main__":
    k = kur()
    gunler = sorted({x["gun"] for x in k})
    print("\nBIZIM VERI: %d kayit · %d gun (%s -> %s)" % (len(k), len(gunler), gunler[0], gunler[-1]))
    suz = [x for x in k if x.get("top_ls") is not None]
    print("skor-suzulmus evren: %d kayit (%%%.1f)" % (len(suz), 100 * len(suz) / len(k)))
    sc = [x["score"] for x in k if x.get("score") is not None]
    sc2 = [x["score"] for x in suz if x.get("score") is not None]
    print("score medyani — tam tarama %.1f · suzulmus %.1f" % (sx.median(sc), sx.median(sc2)))
    for u in UFUKLAR:
        alan_testi(k, TAM, "KOSU A — TAM TARAMA EVRENI", u)
    alan_testi(suz, SUZ + ["score"], "KOSU B — SKOR-SUZULMUS EVREN (kendi kontrolüyle)", 24)
    print("\nOKUMA: |gun-t| >= 3,0 isaretli. top3-cik. sutunu UST kolunun en iyi 3")
    print("sembolu cikarilinca kalan ortalama — fark buhar oluyorsa yogunlasma.")
    print("bot dosyalarina yazim: YOK")
