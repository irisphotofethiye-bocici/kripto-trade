#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AKIS TABANLI REJIM VEKILLERI — 2 yillik veriden kurulabilenler.

KULLANICI (2026-08-21): "btc ve eth'nin hareketinden rejim cikmiyor mu?
totallerde de olabilir. son 3 gunde kriptoya ne kadar para girdi, usdt dom,
btc dom bize rejimi verir."

FIKIR IYI. Sinir: piyasa_yapisi_log yalniz 2026-06-26'dan beri, 107 kayit,
gunde 2 kez -> 2 yillik sinama icin YETMEZ.

BIZIM VERIDEN NE KURULABILIR (567 sembol x 2 yil, saatlik fiyat+hacim):
  ✅ BTC.D vekili   : BTC getirisi / alt-endeks getirisi (goreli guc)
  ✅ ETH gucu       : ETH getirisi / alt-endeks
  ✅ PARA GIRISI    : evrenin toplam USDT hacmi (qv) — gercek akis vekili
  ✅ GENISLIK       : yukselen sembol orani
  ❌ USDT.D         : stablecoin ARZI gerekiyor, elimizde YOK — kurulamaz
  ❌ TOTAL ($)      : tarihsel mcap yok; alt-endeks yalniz FIYAT hareketini verir

Kurulan vekiller AYNI tespit-kalitesi testinden gecirilir (17_etiket_kalitesi.py
ile ayni ölcut): gecikme · kapsama · kesinlik · taban oran.

SALT OKUMA.
"""
import os, json, datetime, collections, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
KLINE = os.path.join(SCRATCH, "klines_1h_uzun")
ONBELLEK = os.path.join(HERE, "endeks_gunluk.json")

ILERI_GUN, ILERI_ESIK = 7, 3.0


def endeks_kur():
    """Gunluk: alt-endeks (esit agirlikli getiri), toplam hacim, genislik, BTC, ETH."""
    if os.path.exists(ONBELLEK):
        with open(ONBELLEK, encoding="utf-8") as f:
            return json.load(f)
    gun_get = collections.defaultdict(list)      # gun -> [sembol gunluk getirisi]
    gun_hac = collections.defaultdict(float)
    gun_fiy = {}
    dosya = sorted(f for f in os.listdir(KLINE) if f.endswith(".json"))
    for n, fn in enumerate(dosya, 1):
        sym = fn[:-5]
        try:
            with open(os.path.join(KLINE, fn), encoding="utf-8") as f:
                b = json.load(f)
        except Exception:
            continue
        if len(b) < 48:
            continue
        g = collections.OrderedDict()
        for x in b:
            d = datetime.datetime.fromtimestamp(x["t"] / 1000).strftime("%Y-%m-%d")
            if d not in g:
                g[d] = {"ilk": x["o"], "son": x["c"], "qv": 0.0}
            g[d]["son"] = x["c"]
            g[d]["qv"] += x.get("qv") or 0.0
        for d, v in g.items():
            if v["ilk"] > 0:
                gun_get[d].append((v["son"] - v["ilk"]) / v["ilk"] * 100)
            gun_hac[d] += v["qv"]
        if sym in ("BTC", "ETH"):
            gun_fiy[sym] = {d: v["son"] for d, v in g.items()}
        if n % 150 == 0:
            print("  ... %d/%d" % (n, len(dosya)))
    out = []
    for d in sorted(gun_get):
        v = gun_get[d]
        if len(v) < 30:
            continue
        out.append({"gun": d, "alt_get": sx.median(v), "n_sembol": len(v),
                    "hacim": gun_hac[d], "genislik": 100 * sum(1 for x in v if x > 0) / len(v),
                    "btc": gun_fiy.get("BTC", {}).get(d),
                    "eth": gun_fiy.get("ETH", {}).get(d)})
    with open(ONBELLEK, "w", encoding="utf-8") as f:
        json.dump(out, f)
    return out


def vekiller(e):
    """Her gune: btc_pay vekili · hacim ivmesi · genislik · ETH gucu."""
    for i, x in enumerate(e):
        if i < 8 or not x["btc"] or not e[i - 1]["btc"]:
            continue
        x["btc_get"] = (x["btc"] - e[i - 1]["btc"]) / e[i - 1]["btc"] * 100
        if x["eth"] and e[i - 1]["eth"]:
            x["eth_get"] = (x["eth"] - e[i - 1]["eth"]) / e[i - 1]["eth"] * 100
        # BTC.D vekili: BTC getirisi - alt medyan getirisi (3 gun toplami)
        x["btc_pay_3g"] = sum(e[j].get("btc_get", 0) - e[j]["alt_get"] for j in range(i - 2, i + 1))
        # PARA GIRISI vekili: son 3 gun hacim / onceki 7 gun ortalamasi
        onc = [e[j]["hacim"] for j in range(i - 9, i - 2)]
        son3 = [e[j]["hacim"] for j in range(i - 2, i + 1)]
        if onc and sum(onc) > 0:
            x["hacim_ivme"] = (sum(son3) / 3) / (sum(onc) / len(onc))
        x["genislik_3g"] = sx.mean(e[j]["genislik"] for j in range(i - 2, i + 1))
    return e


def gercek(e):
    for i, x in enumerate(e):
        x["ger"] = None
        if i + ILERI_GUN < len(e) and x["btc"] and e[i + ILERI_GUN]["btc"]:
            x["ger"] = ((e[i + ILERI_GUN]["btc"] - x["btc"]) / x["btc"] * 100) >= ILERI_ESIK
    return e


def kalite(e, ad, kural):
    tp = fp = fn = tn = 0
    for x in e:
        if x.get("ger") is None or "hacim_ivme" not in x:
            continue
        p = kural(x)
        if p and x["ger"]:
            tp += 1
        elif p and not x["ger"]:
            fp += 1
        elif (not p) and x["ger"]:
            fn += 1
        else:
            tn += 1
    top = tp + fp + fn + tn
    if not top:
        return
    print("%-34s kesinlik %5.1f%%  kapsama %5.1f%%  acik %5.1f%%  (tp %3d fp %3d fn %3d)"
          % (ad, 100 * tp / (tp + fp) if tp + fp else 0,
             100 * tp / (tp + fn) if tp + fn else 0, 100 * (tp + fp) / top, tp, fp, fn))


def gecikme(e, ad, kural):
    epi, i = [], 0
    while i < len(e) - ILERI_GUN:
        if e[i].get("ger"):
            epi.append(i)
            i += ILERI_GUN
        else:
            i += 1
    gec, kacan = [], 0
    for j in epi:
        bul = None
        for k in range(j, min(j + 21, len(e))):
            if "hacim_ivme" in e[k] and kural(e[k]):
                bul = k - j
                break
        if bul is None:
            kacan += 1
        else:
            gec.append(bul)
    print("%-34s epizot %d · gecikme medyan %s · hemen %d · kacirilan %d"
          % (ad, len(epi), "%.1f gun" % sx.median(gec) if gec else "-",
             sum(1 for x in gec if x == 0), kacan))


if __name__ == "__main__":
    print("endeks kuruluyor (567 sembol x 2 yil)...")
    e = gercek(vekiller(endeks_kur()))
    var = [x for x in e if x.get("ger") is not None and "hacim_ivme" in x]
    tab = 100 * sum(1 for x in var if x["ger"]) / len(var)
    print("gun: %d · vekil hesaplanabilen: %d · TABAN ORAN %%%.1f\n" % (len(e), len(var), tab))

    KURALLAR = [
        ("PARA GIRISI: hacim_ivme > 1,2", lambda x: x["hacim_ivme"] > 1.2),
        ("PARA GIRISI: hacim_ivme > 1,5", lambda x: x["hacim_ivme"] > 1.5),
        ("GENISLIK 3g > %55", lambda x: x["genislik_3g"] > 55),
        ("GENISLIK 3g > %65", lambda x: x["genislik_3g"] > 65),
        ("BTC ONDE (btc_pay_3g > 0)", lambda x: x.get("btc_pay_3g", 0) > 0),
        ("ALTLAR ONDE (btc_pay_3g < 0)", lambda x: x.get("btc_pay_3g", 0) < 0),
        ("hacim>1,2 VE genislik>%55", lambda x: x["hacim_ivme"] > 1.2 and x["genislik_3g"] > 55),
        ("hacim>1,2 VE altlar onde", lambda x: x["hacim_ivme"] > 1.2 and x.get("btc_pay_3g", 0) < 0),
    ]
    print("--- TESPIT KALITESI (taban %%%.1f) ---" % tab)
    for ad, k in KURALLAR:
        kalite(e, ad, k)
    print("\n--- GECIKME ---")
    for ad, k in KURALLAR:
        gecikme(e, ad, k)
    print("\nbot dosyalarina yazim: YOK")
