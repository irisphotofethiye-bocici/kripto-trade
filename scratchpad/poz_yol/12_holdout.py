#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HOLDOUT — 11-21 Agustos. ON_KAYIT_holdout.md'ye BIREBIR uyar.

2 yillik veri tam 2026-08-11 11:00'de bitiyordu; ondan cikan her hukum bu
gunleri HIC GORMEDI. Veri 08-21'e uzatildi.

GECME OLCUTU (on-kayitli): tek soru ISARET AYNI MI.
   ayni -> "henuz curutulmedi" (dogrulandi DEGIL)
   ters -> "holdout'ta coktu"
   N<200 gozlem veya <5 gun -> "olculemedi"
Anlamlilik IDDIA EDILMEZ; 7-10 gun-kumesi buna yetmez.

SALT OKUMA.
"""
import os, sys, json, datetime, collections, statistics as sx, bisect

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
sys.path.insert(0, SCRATCH)
import ileri_rr as ir                                           # noqa: E402
import olcum_ortak as oo                                        # noqa: E402

# --- ON-KAYITLI PENCERE ---
HOLDOUT_BAS = int(datetime.datetime(2026, 8, 11, 12, 0).timestamp() * 1000)
UFUK_MS = ir.UFUK * 3600000
UCUZ, FUND_ESIK, PUMP = ir.UCUZ_FIYAT, ir.FUND_ESIK, ir.PUMP
PUMP_UST = 40.0        # >40 LONG hucresi


def _oynat(b, atrs, si, ft, fr, yon, hedef_pct=10.0, trailing=False):
    """ileri_rr mekanigi, YON parametreli. -> dict | None"""
    gi = si + 1
    if si < ir.ISINMA or gi >= len(b) or not atrs[si]:
        return None
    ref = b[gi]["o"]
    if ref <= 0:
        return None
    a = atrs[si]
    if yon == "SHORT":
        stop = ir.stop_hesapla(b, si, ref, a)
        sp = (stop - ref) / ref * 100
        hedef = ref * (1 - hedef_pct / 100)
    else:
        # LONG: simetrik (swing DIP + NBAR dibi + 1,5xATR, girise en yakin)
        bas = max(3, si - 100)
        lo = [b[j]["l"] for j in range(bas, si - 2)
              if b[j - 3:j + 4] and b[j]["l"] == min(x["l"] for x in b[j - 3:j + 4])]
        sup = max([x for x in lo if x < ref], default=None)
        ad = []
        if sup is not None and (ref - sup) <= 3 * a:
            ad.append(sup - 0.25 * a)
        nb = min(x["l"] for x in b[max(0, si - ir.STOP_NBAR + 1):si + 1])
        if nb < ref:
            ad.append(nb - 0.25 * a)
        ad.append(ref - 1.5 * a)
        gec = [s for s in ad if s < ref]
        stop = max(gec) if gec else ref - 1.5 * a
        sp = (ref - stop) / ref * 100
        hedef = ref * (1 + hedef_pct / 100)
    if sp <= 0 or sp < ir.ASGARI_STOP:
        return None
    son = min(gi + ir.UFUK, len(b))
    if son - gi < 4:
        return None
    if b[son - 1]["t"] - b[gi]["t"] < UFUK_MS * 0.9:
        return None                                  # ufuk KIRPIK -> ana kola girmez

    izle = stop
    cj, tip, ham = son - 1, "SURE", None
    for j in range(gi, son):
        x = b[j]
        if yon == "SHORT":
            if x["h"] >= izle:
                cj, tip, ham = j, "STOP", -(izle - ref) / ref * 100
                break
            if x["l"] <= hedef:
                cj, tip, ham = j, "HEDEF", hedef_pct
                break
            if trailing and atrs[j]:
                izle = min(izle, x["l"] + 2.0 * atrs[j])       # SHORT: stop ASAGI cekilir
        else:
            if x["l"] <= izle:
                cj, tip, ham = j, "STOP", -(ref - izle) / ref * 100
                break
            if x["h"] >= hedef:
                cj, tip, ham = j, "HEDEF", hedef_pct
                break
            if trailing and atrs[j]:
                izle = max(izle, x["h"] - 2.0 * atrs[j])
    if ham is None:
        c = b[cj]["c"]
        ham = ((ref - c) if yon == "SHORT" else (c - ref)) / ref * 100
    fon = ir.fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
    if yon == "LONG":
        fon = -fon
    return {"net": ham - oo.MALIYET + fon, "tip": tip, "sp": sp,
            "ts": b[gi]["t"], "gun": datetime.datetime.fromtimestamp(b[gi]["t"] / 1000).strftime("%m-%d")}


def topla():
    """Holdout penceresindeki tum girisleri, ozellikleriyle."""
    kayit = []
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
        if len(b) < ir.ISINMA + ir.UFUK + 10 or not fr:
            continue
        ft = [x["t"] for x in fr]
        atrs = ir.atr_serisi(b)
        ma = ir.ma_serisi(b)
        for si in range(ir.ISINMA, len(b) - 2):
            if b[si]["t"] < HOLDOUT_BAS:
                continue
            x = b[si]
            if (x.get("qv") or 0) < ir.MIN_VOL / 24 or si < 24:
                continue
            k = bisect.bisect_right(ft, x["t"]) - 1
            if k < 0:
                continue
            fund = fr[k]["r"]   # 2026-08-21: r ZATEN yuzde (funding_indir.py:67)
            chg24 = (x["c"] - b[si - 24]["c"]) / b[si - 24]["c"] * 100 if b[si - 24]["c"] else None
            if chg24 is None:
                continue
            kayit.append({"sym": sym, "si": si, "b": b, "atrs": atrs, "ft": ft, "fr": fr,
                          "fiyat": x["c"], "funding": fund, "chg24": chg24,
                          "ma50": ma[si], "t": x["t"]})
        if n % 120 == 0:
            print("  ... %d/%d dosya · aday %d" % (n, len(dosya), len(kayit)))
            sys.stdout.flush()
    return kayit


def ozet(v):
    if not v:
        return None
    g = collections.defaultdict(list)
    for x in v:
        g[x["gun"]].append(x["net"])
    gunler = [sx.mean(g[d]) for d in g if len(g[d]) >= 5]
    if len(gunler) < 2:
        return {"n": len(v), "ort": sx.mean(x["net"] for x in v), "gun": len(g), "t": None}
    se = sx.stdev(gunler) / len(gunler) ** 0.5
    return {"n": len(v), "ort": sx.mean(x["net"] for x in v),
            "gun_ort": sx.mean(gunler), "gun": len(gunler),
            "t": sx.mean(gunler) / se if se else None,
            "poz_gun": sum(1 for x in gunler if x > 0)}


def yaz(ad, o, beklenen_isaret):
    if not o or o["n"] < 200 or o.get("gun", 0) < 5:
        print("  %-46s OLCULEMEDI (N=%s gun=%s)"
              % (ad, o["n"] if o else 0, o.get("gun", 0) if o else 0))
        return "olculemedi"
    isaret = 1 if o.get("gun_ort", o["ort"]) > 0 else -1
    hkm = "henuz CURUTULMEDI" if isaret == beklenen_isaret else "HOLDOUT'TA COKTU"
    print("  %-46s N=%-6d gun=%-3d ort %+7.4f  gun-ort %+7.4f  t %6s  poz-gun %d/%d  -> %s"
          % (ad, o["n"], o["gun"], o["ort"], o.get("gun_ort", 0),
             "%.2f" % o["t"] if o.get("t") is not None else "-",
             o.get("poz_gun", 0), o["gun"], hkm))
    return hkm


if __name__ == "__main__":
    print("=" * 112)
    print("HOLDOUT — girisler 2026-08-11 12:00 sonrasi · ufuk %d saat · mekanik ileri_rr ile BIREBIR" % ir.UFUK)
    print("=" * 112)
    k = topla()
    print("\ntoplam aday giris: %d" % len(k))
    if not k:
        sys.exit(0)
    gunler = sorted({datetime.datetime.fromtimestamp(x["t"] / 1000).strftime("%m-%d") for x in k})
    print("kapsanan gun: %s" % ", ".join(gunler))

    def oyna(f, yon, trailing=False):
        out = []
        for x in k:
            if not f(x):
                continue
            r = _oynat(x["b"], x["atrs"], x["si"], x["ft"], x["fr"], yon, trailing=trailing)
            if r:
                out.append(r)
        return out

    print("\n--- HUKUM 1: SHORT yigini (2 yilda +0,2340) ---")
    yig = lambda x: (x["fiyat"] > UCUZ and x["funding"] > FUND_ESIK and x["chg24"] < PUMP)
    yaz("SHORT yigini", ozet(oyna(yig, "SHORT")), +1)
    yaz("  kontrol: yiginsiz tum SHORT", ozet(oyna(lambda x: True, "SHORT")), +1)

    print("\n--- HUKUM 2: funding <= -0,05 kapisi ZARARLI (kontrol daha iyi) ---")
    kapi = ozet(oyna(lambda x: x["funding"] <= FUND_ESIK, "SHORT"))
    kont = ozet(oyna(lambda x: x["funding"] > FUND_ESIK, "SHORT"))
    yaz("kapi kolu (funding <= -0,05)", kapi, -1)
    yaz("kontrol kolu (funding > -0,05)", kont, +1)
    if kapi and kont and kapi["n"] >= 200 and kont["n"] >= 200:
        f = kont.get("gun_ort", 0) - kapi.get("gun_ort", 0)
        print("  FARK (kontrol - kapi): %+.4f  -> 2 yilda +0,5430 idi  -> %s"
              % (f, "ayni isaret" if f > 0 else "TERS"))

    print("\n--- HUKUM 3: pump engeli DOGRU (chg24>=%20 gecenler kotu) ---")
    yaz("chg24 >= %20 SHORT (engellenen dilim)", ozet(oyna(lambda x: x["chg24"] >= PUMP, "SHORT")), -1)
    yaz("chg24 <  %20 SHORT", ozet(oyna(lambda x: x["chg24"] < PUMP, "SHORT")), +1)

    print("\n--- HUKUM 4: chg24 > %40 LONG + takip eden stop (2 yilda +2,379) ---")
    yaz("chg24 > %40 LONG · takip eden", ozet(oyna(lambda x: x["chg24"] > PUMP_UST, "LONG", True)), +1)
    yaz("chg24 > %40 LONG · sabit stop", ozet(oyna(lambda x: x["chg24"] > PUMP_UST, "LONG")), +1)

    print("\n" + "=" * 112)
    print("ON-KAYIT: isaret ayni = 'henuz curutulmedi' (DOGRULANDI DEGIL) · ters = 'coktu'")
    print("Anlamlilik IDDIA EDILMIYOR — gun-kumesi az.")
    print("bot dosyalarina yazim: YOK")
