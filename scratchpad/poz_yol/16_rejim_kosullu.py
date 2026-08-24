#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REJIM KOSULLU KAPI OLCUMU — "2 yil ortalamasi hangi kosula karsilik geliyor?"

KULLANICI (2026-08-21): "cunku 2 yilla test ediyoruz ve kosullar ayni degil
test ettigin."

IDDIA: 2 yillik pencere EN AZ UC farkli rejim iceriyor:
   2024-08..2025-01  ATH bolgesi (fonlama tavanda %46-63)
   2025-02..2025-04  duzeltme (-%25)
   2025-05..2025-10  ATH bolgesi
   2025-11..2026-06  DERIN AYI (-%54)
   2026-07..         ayidan cikis
Bir kuralin kenari rejime baglysa, 2 yil ORTALAMASI hicbir gercek koşula
karsilik gelmez — uc farkli evrenin karisimidir.

TEST: ayni kapilari BTC drawdown rejimi icinde AYRI AYRI olc.
   isaret rejimler arasi DONUYORSA  -> 2 yil ortalamasi anlamsiz, kullanici hakli
   isaret HER rejimde ayni ise      -> ortalama gecerli, sorun baska yerde

MEKANIK: ileri_rr ile BIREBIR ayni (parametreler degistirilmedi).
SALT OKUMA.
"""
import os, sys, json, datetime, collections, statistics as sx, bisect

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
sys.path.insert(0, SCRATCH)
sys.path.insert(0, HERE)
import ileri_rr as ir                                           # noqa: E402
h = __import__("12_holdout")                                    # noqa: E402

SEYRELT = 12          # 2 yil taranacak; her bar cok agir


def btc_rejim_serisi():
    """ms -> rejim etiketi (BTC drawdown'a gore), saatlik."""
    with open(os.path.join(ir.KLINE, "BTC.json"), encoding="utf-8") as f:
        b = json.load(f)
    z, out = 0.0, {}
    for x in b:
        z = max(z, x["h"])
        dd = (x["c"] - z) / z * 100
        out[x["t"]] = ("ATH_BOLGESI" if dd > -10 else
                       "DUZELTME" if dd > -30 else "DERIN_AYI")
    return out, sorted(out)


def ozet(v):
    if len(v) < 300:
        return None
    g = collections.defaultdict(list)
    for x in v:
        g[x["ay"]].append(x["net"])
    aylar = [sx.mean(g[a]) for a in g if len(g[a]) >= 20]
    if len(aylar) < 3:
        return None
    se = sx.stdev(aylar) / len(aylar) ** 0.5
    # sembol yogunlasmasi
    s = collections.defaultdict(float)
    for x in v:
        s[x["sym"]] += x["net"]
    top3 = sorted(s.values(), reverse=True)[:3]
    top = sum(x["net"] for x in v)
    kalan = [x["net"] for x in v if x["sym"] not in
             {k for k, val in sorted(s.items(), key=lambda z: -z[1])[:3]}]
    return {"n": len(v), "ay_ort": sx.mean(aylar), "ay": len(aylar),
            "t": sx.mean(aylar) / se if se else None,
            "poz_ay": sum(1 for a in aylar if a > 0),
            "top3_pay": 100 * sum(top3) / top if top else 0,
            "top3_cikinca": sx.mean(kalan) if kalan else None}


def yaz(ad, o):
    if not o:
        print("    %-30s N yetersiz" % ad)
        return
    print("    %-30s N=%-6d ay=%-3d ay-ort %+7.4f  t %6s  poz-ay %2d/%-2d  top3 %%%3.0f  cikinca %+7.4f"
          % (ad, o["n"], o["ay"], o["ay_ort"],
             "%.2f" % o["t"] if o["t"] is not None else "-",
             o["poz_ay"], o["ay"], o["top3_pay"],
             o["top3_cikinca"] if o["top3_cikinca"] is not None else float("nan")))


if __name__ == "__main__":
    rej, rts = btc_rejim_serisi()
    print("=" * 118)
    print("REJIM KOSULLU KAPI OLCUMU — 2 yil, BTC drawdown rejimine gore AYRI")
    print("=" * 118)
    say = collections.Counter(rej.values())
    print("saat dagilimi: %s" % dict(say))

    kova = collections.defaultdict(list)
    dosya = sorted(f for f in os.listdir(ir.KLINE) if f.endswith(".json"))
    for n, fn in enumerate(dosya, 1):
        sym = fn[:-5]
        fp = os.path.join(ir.FUND, fn)
        if not os.path.exists(fp):
            continue
        try:
            with open(os.path.join(ir.KLINE, fn), encoding="utf-8") as f:
                b = json.load(f)
            with open(fp, encoding="utf-8") as f:
                fr = json.load(f)
        except Exception:
            continue
        if len(b) < ir.ISINMA + ir.UFUK + 50 or not fr:
            continue
        ft = [x["t"] for x in fr]
        atrs = ir.atr_serisi(b)
        for si in range(ir.ISINMA, len(b) - ir.UFUK - 2, SEYRELT):
            x = b[si]
            if (x.get("qv") or 0) < ir.MIN_VOL / 24 or si < 24:
                continue
            i = bisect.bisect_right(rts, x["t"]) - 1
            if i < 0:
                continue
            r = rej[rts[i]]
            k = bisect.bisect_right(ft, x["t"]) - 1
            if k < 0:
                continue
            fund = fr[k]["r"]   # 2026-08-21: r ZATEN yuzde (funding_indir.py:67)
            if not b[si - 24]["c"]:
                continue
            chg24 = (x["c"] - b[si - 24]["c"]) / b[si - 24]["c"] * 100
            res = h._oynat(b, atrs, si, ft, fr, "SHORT")
            if not res:
                continue
            res["sym"] = sym
            res["ay"] = datetime.datetime.fromtimestamp(x["t"] / 1000).strftime("%Y-%m")
            res["funding"] = fund
            res["chg24"] = chg24
            res["fiyat"] = x["c"]
            kova[r].append(res)
        if n % 150 == 0:
            print("  ... %d/%d dosya" % (n, len(dosya)))
            sys.stdout.flush()

    print("\ntoplanan islem: %s" % {k: len(v) for k, v in kova.items()})

    KAPILAR = [
        ("funding <= -0,05 (BOT KAPISI)", lambda x: x["funding"] <= ir.FUND_ESIK),
        ("funding >  -0,05 (KONTROL)", lambda x: x["funding"] > ir.FUND_ESIK),
        ("chg24 >= %20 (pump, ENGELLENEN)", lambda x: x["chg24"] >= ir.PUMP),
        ("chg24 <  %20", lambda x: x["chg24"] < ir.PUMP),
        ("fiyat > $0,07", lambda x: x["fiyat"] > ir.UCUZ_FIYAT),
        ("SHORT yigini", lambda x: (x["fiyat"] > ir.UCUZ_FIYAT and
                                    x["funding"] > ir.FUND_ESIK and x["chg24"] < ir.PUMP)),
    ]
    for ad, f in KAPILAR:
        print("\n  %s" % ad)
        for r in ("ATH_BOLGESI", "DUZELTME", "DERIN_AYI"):
            yaz(r, ozet([x for x in kova.get(r, []) if f(x)]))
        yaz("TUM 2 YIL (karisim)", ozet([x for v in kova.values() for x in v if f(x)]))

    print("\n" + "=" * 118)
    print("OKUMA: isaret rejimler arasi DONUYORSA 2 yil ortalamasi hicbir gercek")
    print("kosula karsilik gelmiyor demektir.")
    print("bot dosyalarina yazim: YOK")
