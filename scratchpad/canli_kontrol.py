#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CANLI ILK PARTI KONTROLU (2026-08-11) — 7 islem, 1 kazanc: olcumle celisiyor mu?

SORU: Iki SHORT kapisi canliya alindi (A+B ve MA50+ucuz, sabit %10 hedef).
Ilk 9 saatte 7 kapanis: 6 STOP + 1 HEDEF, -732 USDT.
Olcum "+%1.09 net / olay" demisti. ILK PARTI OLCUMLE CELISIYOR MU, YOKSA
BEKLENEN DAGILIMIN ICINDE MI?

YONTEM: olcumun kendi mekanigini (A-stop, %10 hedef, 72s ufuk, maliyet %0.09)
ayni kapilarla kosar; ISABET ORANI ve STOP MESAFESI dagilimini cikarir.
Sonra binom: p=isabet iken 7 denemede <=1 kazanc olasiligi nedir?

AYRICA: canli stoplarin mesafesi (0.42% - 5.44%) olcumun stop dagiliminin
neresine dusuyor? Cok dar stoplar olcumde de var miydi, yoksa canli baska
bir seyi mi seciyor?
"""
import json, os, sys, statistics as stx
from math import comb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yon_dogrula as yd
import yon_avi

PUMP = 20.0  # canlidaki pump kapisi: chg24 >= %20 ise SHORT acilmaz


def gecer_ab(o):
    return (o.get("funding") or 0) <= -0.05 and (o.get("oi24") or 0) >= 10


def gecer_ma50(o):
    px = 10 ** o["fiyat_log"] if o.get("fiyat_log") is not None else None
    return px is not None and px <= 0.07 and (o.get("ma50_mesafe") or -99) >= 3.72


def pump_ok(o):
    return (o.get("chg24") or 0) < PUMP


def main():
    ge = yon_avi.yukle()
    bc, idxc = {}, {}
    import datetime
    for o in ge:
        s = o["sym"]
        if s not in bc:
            p = os.path.join(yd.CACHE, f"{s}.json")
            bc[s] = json.load(open(p)) if os.path.exists(p) else None
            if bc[s]:
                idxc[s] = {x["t"] // 3600000: i for i, x in enumerate(bc[s])}
        if not bc[s]:
            continue
        ms = int(datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M").astimezone().timestamp() * 1000)
        o["_b"], o["_gi"] = bc[s], idxc[s].get(ms // 3600000)

    KUME = [
        ("A+B (+pump kapisi)", lambda o: gecer_ab(o) and pump_ok(o)),
        ("MA50+ucuz (+pump kapisi)", lambda o: gecer_ma50(o) and pump_ok(o)),
        ("BIRLESIM = canlidaki bot", lambda o: (gecer_ab(o) or gecer_ma50(o)) and pump_ok(o)),
    ]
    print("=" * 104)
    print("CANLI KAPILARIN OLCUMDEKI DAGILIMI — hedef %10 · ufuk 72s · A-stop · maliyet %0.09")
    print("=" * 104)
    print(f"{'kume':30}{'N':>6}{'net %':>9}{'isabet':>9}{'stop med':>10}"
          f"{'stop<%1.5':>11}{'basabas':>10}")
    print("-" * 104)
    kayit = {}
    for ad, fn in KUME:
        sec = [o for o in ge if o.get("_gi") is not None and fn(o)]
        k = [yd.islem(o["_b"], o["_gi"] + 1, 10.0, 72, "SHORT") for o in sec]
        k = [x for x in k if x]
        if not k:
            continue
        g = [x[0] for x in k]
        sp = [x[2] for x in k]
        isa = sum(1 for x in k if x[1] == "HEDEF") / len(k)
        dar = sum(1 for s in sp if s < 1.5) / len(sp) * 100
        med = stx.median(sp)
        print(f"{ad:30}{len(k):6d}{stx.mean(g):+9.2f}{isa*100:8.1f}%{med:9.2f}%"
              f"{dar:10.1f}%{med/(10+med)*100:9.1f}%")
        kayit[ad] = (isa, sp, k)

    isa, sp, k = kayit["BIRLESIM = canlidaki bot"]
    print("\n" + "=" * 104)
    print("1) ILK 7 ISLEMDE 1 KAZANC — beklenen dagilimin icinde mi?")
    print("=" * 104)
    n, w = 7, 1
    p_le = sum(comb(n, i) * isa ** i * (1 - isa) ** (n - i) for i in range(w + 1))
    p_tam = comb(n, w) * isa ** w * (1 - isa) ** (n - w)
    print(f"  Olcumun isabet orani p = {isa*100:.1f}%   (kazanan = %10 hedefe ulasan)")
    print(f"  7 denemede tam 1 kazanc olasiligi        : {p_tam*100:.1f}%")
    print(f"  7 denemede 1 VEYA DAHA AZ kazanc olasiligi: {p_le*100:.1f}%")
    bek = isa * n
    print(f"  Beklenen kazanc sayisi                   : {bek:.1f} / 7")
    print(f"  -> {'BEKLENEN DAGILIMIN ICINDE (celiski YOK)' if p_le > 0.05 else 'DAGILIMIN DISINDA — celiski VAR'}")

    print("\n" + "=" * 104)
    print("2) CANLI STOP MESAFELERI olcumun neresinde?")
    print("=" * 104)
    canli = [("PROM", 1.36), ("WLFI", 0.42), ("SQD", 3.96), ("SQD", 5.44),
             ("PROM", 4.60), ("AIOT", 3.96), ("JST", 1.23)]
    sps = sorted(sp)
    print(f"  Olcum stop dagilimi: p10={sps[len(sps)//10]:.2f}%  medyan={stx.median(sps):.2f}%  "
          f"p90={sps[len(sps)*9//10]:.2f}%")
    print(f"\n  {'canli islem':14}{'stop %':>9}{'olcumdeki yuzdelik':>22}")
    for ad, s in canli:
        yuz = sum(1 for x in sps if x <= s) / len(sps) * 100
        print(f"  {ad:14}{s:9.2f}{yuz:21.0f}%")

    print("\n" + "=" * 104)
    print("3) KAC ISLEM GEREKIR — bu kapinin gercekten pozitif oldugunu ayirt etmek icin")
    print("=" * 104)
    g = [x[0] for x in k]
    ort, sd = stx.mean(g), stx.pstdev(g)
    print(f"  Olay basi net: ortalama {ort:+.2f}%  ·  standart sapma {sd:.2f}%")
    for hedef_t in (2.0, 3.0):
        gerek = (hedef_t * sd / ort) ** 2 if ort > 0 else float("inf")
        print(f"  {hedef_t:.0f} standart hata guveni icin gereken islem sayisi: {gerek:.0f}")
    print(f"  Gunluk ~12.5 olay hizinda bu {((2.0*sd/ort)**2)/12.5:.1f} gun (2 SH) / "
          f"{((3.0*sd/ort)**2)/12.5:.1f} gun (3 SH) demek.")


if __name__ == "__main__":
    main()
