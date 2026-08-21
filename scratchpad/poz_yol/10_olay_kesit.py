#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOGA BACAGI ANINDA ALTLARIN KESITI — radar_archive'dan, bizim veride.

KULLANICI: "o sirada funding ne durumdaymis, ya olctugumuz digerleri..."

radar_archive 2026-06-24'ten beri her taramada 29 alan yaziyor. BTC'nin
24 saatte >= %4 yukseldigi olaylardan UCU bu pencerede:
   2026-07-02 14:05 · 2026-07-14 21:05 · 2026-08-19 19:05

ALAN DOLULUK (olculdu, 11 Agu sonrasi):
   %100 : funding · oi3 · oi24 · pos · vol_x · rel3 · score · ayrisma · mcap
   %29,8: top_ls · glob_ls · taker · smart      <- YUKSEK SKORLU adaylarda dolu
   %23,0: chg24
Bu yuzden iki grup AYRI raporlanir; karistirilmaz.

KONTROL: ayni gunun olaydan UZAK saatleri + olaysiz gunler.
SALT OKUMA.
"""
import os, json, datetime, statistics as sx

PROJE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARSIV = os.path.join(PROJE, "radar_archive.jsonl")

OLAY = ["2026-07-02 14", "2026-07-14 21", "2026-08-19 19"]
TAM = ["funding", "oi3", "oi24", "pos", "vol_x", "rel3", "score"]
SUZULMUS = ["top_ls", "glob_ls", "taker"]


def oku():
    out = []
    with open(ARSIV, encoding="utf-8") as f:
        for satir in f:
            if not satir.strip():
                continue
            try:
                x = json.loads(satir)
            except Exception:
                continue
            if x.get("ts", "") >= "2026-06-24":
                out.append(x)
    return out


def pencere(kayit, olay_ts, saat_once=(1, 0)):
    """olay saatinden [saat_once[0], saat_once[1]] saat ONCEKI kayitlar."""
    t = datetime.datetime.strptime(olay_ts + ":00", "%Y-%m-%d %H:%M")
    a = (t - datetime.timedelta(hours=saat_once[0])).strftime("%Y-%m-%d %H:%M")
    b = (t - datetime.timedelta(hours=saat_once[1])).strftime("%Y-%m-%d %H:%M")
    return [x for x in kayit if a <= x["ts"] < b]


def ozet(ad, kayitlar, alanlar):
    print("\n%-42s N=%d kayit" % (ad, len(kayitlar)))
    if not kayitlar:
        return
    print("   " + "  ".join("%-13s" % a for a in alanlar))
    sat = []
    for a in alanlar:
        v = [x[a] for x in kayitlar if x.get(a) is not None]
        sat.append("%-13s" % ("%.4f (%d)" % (sx.median(v), len(v)) if len(v) >= 5 else "-"))
    print("   " + "  ".join(sat))


if __name__ == "__main__":
    k = oku()
    print("radar_archive 06-24 sonrasi: %d kayit" % len(k))
    gunler = {x["ts"][:10] for x in k}
    print("kapsanan gun: %d" % len(gunler))

    print("\n" + "=" * 90)
    print("A) TAM DOLU ALANLAR (%100) — olaydan 1 saat ONCE")
    print("=" * 90)
    hepsi_olay = []
    for o in OLAY:
        w = pencere(k, o)
        hepsi_olay += w
        ozet("olay %s  (1 saat once)" % o, w, TAM)
    olay_gun = {o[:10] for o in OLAY}
    kont = [x for x in k if x["ts"][:10] not in olay_gun]
    ozet("KONTROL — olay gunleri DISINDAKI her sey", kont, TAM)
    ozet("UC OLAY BIRLESIK (1 saat once)", hepsi_olay, TAM)

    print("\n" + "=" * 90)
    print("B) SUZULMUS ALANLAR (%29,8 — yalniz yuksek skorlu adaylarda dolu)")
    print("   iki grup KARISTIRILMAZ: bunlar skor kapisiyla suzulmus bir evren")
    print("=" * 90)
    ozet("UC OLAY BIRLESIK (1 saat once)", hepsi_olay, SUZULMUS)
    ozet("KONTROL", kont, SUZULMUS)

    print("\n" + "=" * 90)
    print("C) 19 AGUSTOS — saat saat (olay 19:05)")
    print("=" * 90)
    t0 = datetime.datetime(2026, 8, 19, 14, 0)
    print("%-8s %6s  %s" % ("saat", "N", "  ".join("%-12s" % a for a in TAM)))
    for h in range(10):
        a = (t0 + datetime.timedelta(hours=h)).strftime("%Y-%m-%d %H:%M")
        b = (t0 + datetime.timedelta(hours=h + 1)).strftime("%Y-%m-%d %H:%M")
        w = [x for x in k if a <= x["ts"] < b]
        if len(w) < 5:
            continue
        sat = []
        for al in TAM:
            v = [x[al] for x in w if x.get(al) is not None]
            sat.append("%-12s" % ("%.4f" % sx.median(v) if len(v) >= 5 else "-"))
        print("%-8s %6d  %s" % (a[11:16], len(w), "  ".join(sat)))
    print("\nbot dosyalarina yazim: YOK")
