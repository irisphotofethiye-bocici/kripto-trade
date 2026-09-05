#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOT NEDEN BUYUK COINLERE ISLEM ALMIYOR? — BETIMLEYICI teshis (2026-09-05)

🔴 BU BIR HIPOTEZ TESTI DEGILDIR. On-kayit yok, gecme olcutu yok, hukum yok.
   Yalnizca "kapilar hangi buyuklukteki coinlerde tetikleniyor" diye SAYAR.
   Kural adayi uretmez.

EVREN: testbot.py:1400 ile AYNI — evren.binance_pool("fapi", min_vol=3)[:150]
  yani HACME gore ilk 150. BTC/ETH/SOL bu havuzun ICINDE.

Salt-okunur. Veri BELLEKTE birlestirilir. radar_archive context'e yuklenmez.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import sys, json, os, re, statistics as stx, collections, datetime as dt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ileri_rr as ir

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURA)
ESKI_K, YENI_K = os.path.join(BURA, "klines_1h_uzun"), os.path.join(BURA, "taze_1h")
ESKI_F, YENI_F = os.path.join(BURA, "funding_gecmis"), os.path.join(BURA, "taze_funding")
ARSIV = os.path.join(KOK, "radar_archive.jsonl")

HAVUZ_N, MIN_VOL = 150, 3_000_000
FUND_ESIK, UCUZ_ESIK, MA50_MESAFE = -0.05, 0.07, 3.72
BAS = "2026-08-01"                 # son ~5 hafta (taze veri kapsami)

MCAP_RX = re.compile(r"^\$([0-9.]+)M$")


def birlestir(a, b):
    d = {}
    for y in (a, b):
        if os.path.exists(y):
            try:
                for x in json.load(open(y, encoding="utf-8")):
                    d[int(x["t"])] = x
            except Exception:
                pass
    return [d[k] for k in sorted(d)] if d else None


def kova_fiyat(p):
    for esik, ad in ((0.01, "< $0,01"), (0.07, "$0,01-0,07"), (1.0, "$0,07-1"),
                     (10.0, "$1-10"), (100.0, "$10-100")):
        if p < esik:
            return ad
    return ">= $100"


KOVA_SIRA = ["< $0,01", "$0,01-0,07", "$0,07-1", "$1-10", "$10-100", ">= $100"]


def main():
    bas = int(dt.datetime.strptime(BAS, "%Y-%m-%d")
              .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    print("=" * 78)
    print("BOT NEDEN BUYUK COINLERE ISLEM ALMIYOR? — BETIMLEYICI teshis")
    print("=" * 78)
    print("🔴 Hipotez testi DEGIL. On-kayit yok, hukum yok, kural cikmaz.")
    print("Evren: testbot.py:1400 ile ayni -> hacme gore ilk %d (taban $%dM)\n"
          % (HAVUZ_N, MIN_VOL / 1e6))

    # --- klineler ---
    kl, fn = {}, {}
    for f in sorted(os.listdir(ESKI_K)):
        if not f.endswith(".json"):
            continue
        sym = f[:-5]
        b = birlestir(os.path.join(ESKI_K, f), os.path.join(YENI_K, f))
        if not b:
            continue
        b = [x for x in b if x["t"] >= bas]
        if len(b) < 100:
            continue
        kl[sym] = b
        fn[sym] = birlestir(os.path.join(ESKI_F, f), os.path.join(YENI_F, f)) or []

    # --- her SAAT icin havuz: o saatin son 24s hacmine gore ilk 150 ---
    saatler = collections.defaultdict(list)
    for sym, b in kl.items():
        for i in range(24, len(b)):
            hac = sum(x.get("qv") or 0 for x in b[i - 23:i + 1])
            if hac < MIN_VOL:
                continue
            saatler[b[i]["t"]].append((hac, sym, i))

    say = collections.defaultdict(collections.Counter)
    oynak = collections.defaultdict(list)
    ma50s = {s: ir.ma_serisi(b, 50) for s, b in kl.items()}
    atrs = {s: ir.atr_serisi(b) for s, b in kl.items()}
    ftl = {s: [x["t"] for x in (fn.get(s) or [])] for s in kl}

    for t, kayit in saatler.items():
        kayit.sort(reverse=True)
        for hac, sym, i in kayit[:HAVUZ_N]:
            b = kl[sym]
            p = b[i]["c"]
            k = kova_fiyat(p)
            say[k]["havuzda"] += 1
            a = atrs[sym][i]
            if a and p > 0:
                oynak[k].append(a / p * 100)
            fr = fn.get(sym) or []
            ft = ftl[sym]
            if ft:
                j = ir.bisect.bisect_right(ft, b[i]["t"]) - 1
                if j >= 0 and fr[j]["r"] <= FUND_ESIK:
                    say[k]["A_funding"] += 1
            if p <= UCUZ_ESIK:
                say[k]["ucuz_gecti"] += 1
                m = ma50s[sym][i]
                if m and m > 0 and (p / m - 1) * 100 >= MA50_MESAFE:
                    say[k]["MA50_kapisi"] += 1

    print("### HAVUZDAKI SAAT-SEMBOL SAYISI ve KAPI TETIKLEME ORANI")
    print("%-13s %10s %8s %10s %10s %10s" %
          ("fiyat kovasi", "havuzda", "pay%", "A_funding", "MA50 kapisi", "ATR/fiyat%"))
    top = sum(say[k]["havuzda"] for k in say)
    for k in KOVA_SIRA:
        h = say[k]["havuzda"]
        if not h:
            continue
        av = stx.median(oynak[k]) if oynak[k] else 0
        print("%-13s %10d %7.1f%% %9.2f%% %10.2f%% %9.2f" %
              (k, h, h / top * 100, say[k]["A_funding"] / h * 100,
               say[k]["MA50_kapisi"] / h * 100, av))

    # --- radar_archive: skor, mcap kovasina gore ---
    print("\n### RADAR SKORU, PIYASA DEGERINE GORE (radar_archive)")
    sk = collections.defaultdict(list)
    voll = collections.defaultdict(list)
    oi = collections.defaultdict(list)
    with open(ARSIV, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            m = MCAP_RX.match(str(r.get("mcap") or ""))
            if not m or r.get("score") is None:
                continue
            mc = float(m.group(1))
            kv = ("< $100M" if mc < 100 else "$100M-1Mr" if mc < 1000
                  else "$1-10Mr" if mc < 10000 else ">= $10Mr")
            sk[kv].append(r["score"])
            if r.get("vol_x") is not None:
                voll[kv].append(r["vol_x"])
            if r.get("oi24") is not None:
                oi[kv].append(r["oi24"])
    print("%-12s %9s %9s %9s %9s %9s" %
          ("mcap", "N", "skor ort", "skor>=45%", "vol_x med", "oi24 med"))
    for kv in ("< $100M", "$100M-1Mr", "$1-10Mr", ">= $10Mr"):
        v = sk.get(kv)
        if not v:
            continue
        print("%-12s %9d %9.1f %8.1f%% %9.2f %9.2f" %
              (kv, len(v), stx.mean(v), sum(1 for x in v if x >= 45) / len(v) * 100,
               stx.median(voll[kv]) if voll[kv] else 0,
               stx.median(oi[kv]) if oi[kv] else 0))

    print("\n🔴 Hukum YOK — bu tablo yalnizca MEKANIZMAYI gosterir.")
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
