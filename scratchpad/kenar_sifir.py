#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KENAR SIFIRSA (2026-08-11) — fren riski simulasyonu kenarin GERCEK oldugunu
varsayiyor (+%0.58/olay). Ama kenar daha dogrulanmadi (138 islem gerekiyor).
YANILIYORSAM MALIYETI NE?

YONTEM: her olayin getirisinden sabit bir miktar cikarilir; oyle ki portfoy
beklentisi TAM SIFIR olsun. Stop dagilimi, sureler, gun-ici kumelenme,
korelasyon — hepsi AYNEN korunur. Yani "ayni oynaklik, kenar yok" dunyasi.
Karsilastirma: kenar varken vs kenar yokken, HALT olasiligi ve bitis.
"""
import sys, random, statistics as stx, collections
sys.path.insert(0, ".")
import fren_riski as fr

def main():
    ol = fr.olaylari_hazirla()
    gm = collections.OrderedDict()
    for o in ol:
        gm.setdefault(o["gun"], []).append(o)
    bloklar = list(gm.values())

    def sifirla(bloklar, taban, risk):
        """beklentiyi tam sifira ceken sabit kaydirma"""
        pay = [(min(risk / (o["sp"]/100.0), fr.MARJIN_PCT*fr.KALD_MAX), o["g"])
               for g in bloklar for o in g if o["sp"] >= taban]
        top_w = sum(w for w, _ in pay)
        top_g = sum(w * x for w, x in pay)
        c = top_g / top_w                      # agirlikli ortalama getiri
        return [[dict(o, g=o["g"] - c) for o in g] for g in bloklar], c

    SEN = [("S0  bugunku hal (risk %3)", 0.0, None, 0.03),
           ("S9  risk %1.5 + taban %2", 2.0, None, 0.015)]
    NSIM = 2000
    print("=" * 100)
    print("KENAR SIFIRSA — ayni oynaklik, sifir beklenti (yanilma maliyeti)")
    print("=" * 100)
    print(f"{'senaryo':30}{'dunya':14}{'11g HALT':>10}{'46g HALT':>10}"
          f"{'medyan 46g':>12}{'alt %5':>9}{'kayip yol':>11}")
    print("-" * 100)
    for ad, tb, tv, rk in SEN:
        for dunya in ("kenar VAR", "kenar YOK"):
            bl, c = (bloklar, 0.0) if dunya == "kenar VAR" else sifirla(bloklar, tb, rk)
            random.seed(7)
            s11 = s46 = 0; carp = []
            for _ in range(NSIM):
                g11 = [random.choice(bl) for _ in range(11)]
                if fr.simule(g11, tb, tv, rk)[1] is not None:
                    s11 += 1
                g46 = g11 + [random.choice(bl) for _ in range(35)]
                e, h, d = fr.simule(g46, tb, tv, rk)
                if h is not None:
                    s46 += 1
                carp.append(e)
            carp.sort()
            print(f"{ad:30}{dunya:14}{s11/NSIM*100:9.1f}%{s46/NSIM*100:9.1f}%"
                  f"{stx.median(carp):12.2f}{carp[int(NSIM*0.05)]:9.2f}"
                  f"{sum(1 for x in carp if x < 1)/NSIM*100:10.1f}%")
    print("-" * 100)
    print("  'kenar YOK' = ayni olaylar, ayni stoplar, ayni kumelenme; sadece beklenti sifira cekildi")

main()
