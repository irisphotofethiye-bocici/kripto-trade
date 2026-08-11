#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S9 ISLEM SAYISINI AZALTIR MI? (2026-08-11)
Iki zit etki var, olculmeden bilinmez:
  (-) asgari_stop_pct=2.0 olaylarin bir kismini eler
  (+) risk %3->%1.5 HALT olasiligini dusurur -> bot daha uzun sure ACIK kalir
      (S0'da yollarin %97'si duruyor; duran bot islem yapmaz)
Simulasyonu islem SAYACIYLA tekrar kosar.
"""
import sys, random, statistics as stx, collections
sys.path.insert(0, ".")
import fren_riski as fr

SAYAC = {}

def simule_sayarak(gunler, taban, tavan, risk):
    eq, zirve, acik, cool = 1.0, 1.0, [], {}
    saat0, halt_gun, n = 0.0, None, 0
    for gi, gun in enumerate(gunler):
        for o in gun:
            simdi = saat0 + o["sa"]
            kalan = []
            for p in acik:
                if p["kapanis"] <= simdi:
                    eq += p["notional"] * p["g"] / 100.0
                    zirve = max(zirve, eq)
                    if halt_gun is None and eq / zirve - 1 <= -fr.HALT:
                        halt_gun = gi
                else:
                    kalan.append(p)
            acik = kalan
            if halt_gun is not None or o["sp"] < taban or len(acik) >= fr.SLOT:
                continue
            if cool.get(o["sym"], -99) > simdi - fr.COOLDOWN_S:
                continue
            notional = min(risk / (o["sp"]/100.0), fr.MARJIN_PCT*fr.KALD_MAX) * eq
            cool[o["sym"]] = simdi
            n += 1
            acik.append({"notional": notional, "g": o["g"], "kapanis": simdi + o["sure"]})
        saat0 += 24.0
    return n, halt_gun

def main():
    ol = fr.olaylari_hazirla()
    gm = collections.OrderedDict()
    for o in ol:
        gm.setdefault(o["gun"], []).append(o)
    bloklar = list(gm.values())
    print("=" * 92)
    print("ISLEM SAYISI — S9 azaltir mi? (2000 bootstrap yolu)")
    print("=" * 92)
    print(f"{'senaryo':28}{'11 gunde':>12}{'46 gunda':>12}{'gun/islem':>12}{'46g HALT':>11}")
    print("-" * 92)
    for ad, tb, tv, rk in (("S0  bugunku (risk %3)", 0.0, None, 0.03),
                           ("S9  risk %1.5 + taban %2", 2.0, None, 0.015)):
        random.seed(7)
        n11, n46 = [], []
        for _ in range(2000):
            g11 = [random.choice(bloklar) for _ in range(11)]
            a, _h = simule_sayarak(g11, tb, tv, rk); n11.append(a)
            g46 = g11 + [random.choice(bloklar) for _ in range(35)]
            b, h = simule_sayarak(g46, tb, tv, rk); n46.append(b)
        print(f"{ad:28}{stx.median(n11):12.0f}{stx.median(n46):12.0f}"
              f"{stx.median(n46)/46:12.1f}{'':>11}")
    print("-" * 92)
    print("  ILK 11 GUN kritik: 138 islemlik karar penceresi bu surede dolmali mi?")

main()
