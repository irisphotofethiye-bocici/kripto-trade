#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KACAN HAREKETIN DAGILIMI — manset sayi ortalama; birkac uc degerden mi geliyor?
On-kayit ON_KAYIT_olay_kuyrugu.md s.5 "zorunlu ek rapor: kacan hareket".
Olcut DEGISTIRMEZ, yeni hipotez KURMAZ — var olan buyuklugun dagilimini acar.

Onbellekten okur (scratchpad/olay_pencere/), YENI ag cagrisi YAPMAZ.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, collections, statistics

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONBELLEK = os.path.join(PROJE, "scratchpad", "olay_pencere")
OLAYLAR = os.path.join(PROJE, "scratchpad", "olaylar.jsonl")
M = 60 * 1000
YON = {"spot_listeleme": +1, "launchpool": +1, "perp_listeleme": +1, "delisting": -1}
GRUP = {"spot_listeleme": "olumlu_duyuru", "launchpool": "olumlu_duyuru",
        "delisting": "delisting", "perp_listeleme": "perp_listeleme"}
GECIKME = [5, 15, 30, 60]


def kapanis(bar, indeks, ts):
    i = indeks.get(ts - (ts % (5 * M)))
    return bar[i][1] if i is not None else None


def main():
    print("KACAN HAREKETIN DAGILIMI — ortalama mi medyan mi anlatiyor?")
    print("on-kayit ON_KAYIT_olay_kuyrugu.md · yalniz betimleyici, olcut degismedi")
    print("=" * 100)

    ol = [json.loads(l) for l in open(OLAYLAR, encoding="utf-8")]
    veri = collections.defaultdict(lambda: collections.defaultdict(list))
    n = 0
    for o in ol:
        if not o.get("birincil") or not o.get("kume_ilk") or o["tip"] not in YON:
            continue
        for sym in o["semboller"]:
            yol = os.path.join(ONBELLEK, "%s_%d.json" % (sym, o["ts"]))
            if not os.path.exists(yol):
                continue
            try:
                bar = json.load(open(yol))
            except Exception:
                continue
            if not bar:
                continue
            indeks = {b[0]: j for j, b in enumerate(bar)}
            yon = YON[o["tip"]]
            p_on = kapanis(bar, indeks, o["ts"] - 5 * M)
            if not p_on or p_on <= 0:
                continue
            n += 1
            for d in GECIKME:
                e = kapanis(bar, indeks, o["ts"] + d * M)
                if e and e > 0:
                    v = yon * (e - p_on) / p_on * 100.0
                    veri[o["tip"]][d].append(v)
                    veri[GRUP[o["tip"]]][d].append(v)
    print("okunan olay penceresi: %d\n" % n)

    for grup in ["olumlu_duyuru", "spot_listeleme", "launchpool", "delisting"]:
        if not veri.get(grup):
            continue
        print("-" * 100)
        print("  %s" % grup)
        print("  %-8s %5s %9s %9s %9s %9s %9s %9s" %
              ("gecikme", "N", "ort", "MEDYAN", "%25", "%75", "en buyuk", ">%2 pay"))
        for d in GECIKME:
            v = sorted(veri[grup][d])
            if len(v) < 5:
                continue
            q = lambda p: v[min(len(v) - 1, int(p * len(v)))]
            pay = 100.0 * sum(1 for x in v if x > 2.0) / len(v)
            print("  %-8s %5d %+8.2f%% %+8.2f%% %+8.2f%% %+8.2f%% %+8.1f%% %8.0f%%"
                  % ("%d dk" % d, len(v), sum(v) / len(v), statistics.median(v),
                     q(0.25), q(0.75), v[-1], pay))
        # en buyuk 5 olay: ortalamayi tek basina tasiyorlar mi
        v = sorted(veri[grup][30], reverse=True)
        if len(v) >= 10:
            ust5 = sum(v[:5])
            tum = sum(v)
            print("  -> 30 dk: en buyuk 5 olay toplam kacanin %%%.0f'ini tasiyor"
                  % (100.0 * ust5 / tum) if tum else "  -> pay hesaplanamadi")
            kalan = v[5:]
            print("     en buyuk 5 CIKARILINCA ortalama: %+.2f%% (medyan %+.2f%%)"
                  % (sum(kalan) / len(kalan), statistics.median(kalan)))
    print("\n" + "=" * 100)
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
