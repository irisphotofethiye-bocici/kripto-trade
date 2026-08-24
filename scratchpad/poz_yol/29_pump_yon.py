#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIRLAMIS COINDE YON — LONG mu SHORT mu, rejime gore? YALNIZ BIZIM VERI.

KULLANICI (2026-08-21): golge defterinde iki zit tez ayni sembol ailesinde
kazanmis, ama farkli rejimlerde:
   blowoff (firlamisa SHORT)     : ayi/notr +195,43  ·  boga  -35,28
   pump_long_tezi (firlamisa LONG): ayi/notr -1.157  ·  boga +2.545
N kucuk (11 ve 254). Bu betik ayni soruyu BUYUK N ile sorar.

VERI: scratchpad/perp_seri/ — 5 dakikalik mumlar, kendi cektigimiz, ~82 sembol,
      2026-07-22 .. simdi. Binance 2 yillik kline seti KULLANILMADI.

KESIT: chg24 >= %20 olan her 5dk bari bir aday. Cakismayi azaltmak icin ayni
      sembolde 24 barlik (2 saat) ayirma.

OLCUM: hem HAM ileri getiri hem MEKANIK (stop/hedef, maliyet+fonlama dahil),
       LONG ve SHORT ayri, iki rejim kumesi ayri.

⚠️ BOGA kumesi ~2,3 gun -> gun-kumeli t hesaplanamaz. Havuzlanmis raporlanir
   ve bu ACIKCA yazilir. Yogunlasma kontrolu her iki kumede de uygulanir.

HUKUM YAZILMAZ.
SALT OKUMA.
"""
import os, sys, json, datetime, collections, bisect, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
SERI = os.path.join(SCRATCH, "perp_seri")
sys.path.insert(0, SCRATCH)
import olcum_ortak as oo                                        # noqa: E402

BOLEN = int(datetime.datetime(2026, 8, 19, 18, 15).timestamp() * 1000)
BAR24 = 288          # 24 saat / 5 dk
AYIRMA = 24          # 2 saat
ESIK = 20.0
UFUK = [12, 72, 288]          # 1sa · 6sa · 24sa (5dk bar cinsinden)
STOP_PCT = [3.0, 5.0, 8.0]
HEDEF_PCT = 10.0


def fonlama(sym):
    y = os.path.join(SCRATCH, "funding_gecmis", "%s.json" % sym)
    if not os.path.exists(y):
        return [], []
    try:
        with open(y, encoding="utf-8") as f:
            d = json.load(f)
        return [x["t"] for x in d], [x["r"] for x in d]
    except Exception:
        return [], []


def fon(ft, fr, t0, t1, yon):
    if not ft:
        return 0.0
    i, j = bisect.bisect_right(ft, t0), bisect.bisect_right(ft, t1)
    s = sum(fr[k] for k in range(i, j))
    return s if yon == "SHORT" else -s


def mekanik(b, i, yon, stop_pct, ft, fr):
    ref = b[i + 1]["o"] if i + 1 < len(b) else None
    if not ref or ref <= 0:
        return None
    sp = ref * (1 + stop_pct / 100) if yon == "SHORT" else ref * (1 - stop_pct / 100)
    hp = ref * (1 - HEDEF_PCT / 100) if yon == "SHORT" else ref * (1 + HEDEF_PCT / 100)
    son = min(i + 1 + max(UFUK), len(b))
    cj, ham = son - 1, None
    for j in range(i + 1, son):
        x = b[j]
        if (x["h"] >= sp) if yon == "SHORT" else (x["l"] <= sp):
            cj, ham = j, -stop_pct
            break
        if (x["l"] <= hp) if yon == "SHORT" else (x["h"] >= hp):
            cj, ham = j, HEDEF_PCT
            break
    if ham is None:
        c = b[cj]["c"]
        ham = ((ref - c) if yon == "SHORT" else (c - ref)) / ref * 100
    return ham - oo.MALIYET + fon(ft, fr, b[i + 1]["t"], b[cj]["t"], yon)


def topla():
    syms = sorted({f.rsplit("_", 1)[0] for f in os.listdir(SERI) if f.endswith("_kline.json")}
                  - {"BTC", "ETH"})
    ayi, bog = [], []
    for n, s in enumerate(syms, 1):
        try:
            with open(os.path.join(SERI, "%s_kline.json" % s), encoding="utf-8") as f:
                b = sorted(json.load(f), key=lambda x: x["t"])
        except Exception:
            continue
        if len(b) < BAR24 + max(UFUK) + 10:
            continue
        ft, fr = fonlama(s)
        i = BAR24
        while i < len(b) - max(UFUK) - 2:
            c0 = b[i - BAR24]["c"]
            if not c0 or not b[i]["c"]:
                i += 1
                continue
            chg = (b[i]["c"] - c0) / c0 * 100
            if chg < ESIK:
                i += 1
                continue
            ref = b[i + 1]["o"]
            if ref <= 0:
                i += AYIRMA
                continue
            r = {"sym": s, "t": b[i]["t"], "chg24": chg,
                 "gun": datetime.datetime.fromtimestamp(b[i]["t"] / 1000).strftime("%Y-%m-%d")}
            for u in UFUK:
                r["ham%d" % u] = (b[i + u]["c"] - ref) / ref * 100
            for yon in ("LONG", "SHORT"):
                for sp in STOP_PCT:
                    v = mekanik(b, i, yon, sp, ft, fr)
                    if v is not None:
                        r["m_%s_%d" % (yon, int(sp))] = v
            (bog if b[i]["t"] >= BOLEN else ayi).append(r)
            i += AYIRMA
        if n % 25 == 0:
            print("  ... %d/%d sembol" % (n, len(syms)))
            sys.stdout.flush()
    return ayi, bog


def yogun(v, f):
    s = collections.defaultdict(float)
    for x in v:
        y = f(x)
        if y is not None:
            s[x["sym"]] += y
    en = {k for k, _ in sorted(s.items(), key=lambda z: -z[1])[:3]}
    kal = [f(x) for x in v if x["sym"] not in en and f(x) is not None]
    return sx.mean(kal) if kal else None, len(s)


def rapor(v, ad):
    print("\n" + "=" * 100)
    print("%s   N=%d aday · %d sembol · %d gun" % (ad, len(v), len({x["sym"] for x in v}),
                                                   len({x["gun"] for x in v})))
    print("=" * 100)
    if len(v) < 30:
        print("  N yetersiz")
        return
    print("  chg24 medyani %+.1f%%" % sx.median(x["chg24"] for x in v))
    print("\n  HAM ILERI GETIRI (yonsuz, fiyat degisimi)")
    for u in UFUK:
        w = [x["ham%d" % u] for x in v if x.get("ham%d" % u) is not None]
        if w:
            k3, ns = yogun(v, lambda z: z.get("ham%d" % u))
            print("    +%-5s ort %+7.3f%%  medyan %+7.3f%%  poz %%%2.0f  |  en iyi 3 sembol cik. %+7.3f"
                  % ("%dsa" % (u // 12), sx.mean(w), sx.median(w),
                     100 * sum(1 for x in w if x > 0) / len(w), k3 if k3 is not None else float("nan")))
    print("\n  MEKANIK (hedef %%%.0f, maliyet+fonlama dahil)" % HEDEF_PCT)
    print("    %-8s %14s %14s %14s" % ("stop", "LONG ort", "SHORT ort", "fark(L-S)"))
    for sp in STOP_PCT:
        lv = [x["m_LONG_%d" % int(sp)] for x in v if x.get("m_LONG_%d" % int(sp)) is not None]
        sv = [x["m_SHORT_%d" % int(sp)] for x in v if x.get("m_SHORT_%d" % int(sp)) is not None]
        if lv and sv:
            print("    %%%-7.0f %+14.3f %+14.3f %+14.3f"
                  % (sp, sx.mean(lv), sx.mean(sv), sx.mean(lv) - sx.mean(sv)))
    print("\n  YOGUNLASMA (mekanik, stop %3) — en iyi 3 sembol cikinca")
    for yon in ("LONG", "SHORT"):
        tam = [x["m_%s_3" % yon] for x in v if x.get("m_%s_3" % yon) is not None]
        k3, ns = yogun(v, lambda z: z.get("m_%s_3" % yon))
        if tam:
            print("    %-6s tam %+8.3f  ->  cikinca %+8.3f   (%d sembol)"
                  % (yon, sx.mean(tam), k3 if k3 is not None else float("nan"), ns))


if __name__ == "__main__":
    print("FIRLAMIS COIN (chg24 >= %%%.0f) — YON x REJIM, yalniz bizim veri" % ESIK)
    ayi, bog = topla()
    rapor(ayi, "A) NOTR/AYI   07-22 .. 08-19 18:15")
    rapor(bog, "B) BOGA       08-19 18:15 .. simdi")
    print("\n" + "=" * 100)
    print("⚠️ B kumesi ~2,3 gun -> gun-kumeli t YOK, havuzlanmis rakamlar.")
    print("HUKUM YAZILMADI. bot dosyalarina yazim: YOK")
