#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KESINLIK TESTI — "hacim patlayinca TEPE midir?"

30_cikis_tersine.py "tepede hacim patliyor" gosterdi (KAPSAMA).
Karar icin gereken TERSI: hacim patlayinca kacinda tepe? (KESINLIK)

Bu oturumda ayni karisiklik DORT kez yasandi. Bu yuzden ayri betik.

TETIK ADAYLARI (t aninda elde olan, ileriye bakma YOK):
   hacim_15 son 3 barda >= +X%   ·  islem_15 >= +X%  ·  taker_15 dususu
TEPE tanimi: pozisyonun MFE bari (+-1 bar tolerans).

Ayrica pratik olcut: tetik anindan sonra pozisyon ne yapmis?
   (tepe olmasa bile tetikte cikmak IYI mi?)

HUKUM YAZILMAZ. SALT OKUMA.
"""
import os, sys, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ortak                                                    # noqa: E402


def hazirla():
    out = []
    for p in ortak.pozisyonlar(en_az_goruntu=12, zengin=True):
        s = p["seri"]
        pnl = [g.get("pnl_pct") for g in s]
        if any(x is None for x in pnl):
            continue
        out.append({"sym": p["sym"], "seri": s, "pnl": pnl,
                    "i_tepe": pnl.index(max(pnl)), "sonuc": p["sonuc"]})
    return out


def deg(s, i, alan, geri=3):
    if i - geri < 0:
        return None
    a, b = s[i - geri].get(alan), s[i].get(alan)
    if a is None or b is None or a == 0:
        return None
    return (b - a) / abs(a) * 100


TETIK = [
    ("hacim15 3bar >= +20%", lambda s, i: (deg(s, i, "hacim_15_usdt") or -999) >= 20),
    ("hacim15 3bar >= +50%", lambda s, i: (deg(s, i, "hacim_15_usdt") or -999) >= 50),
    ("hacim15 3bar >= +100%", lambda s, i: (deg(s, i, "hacim_15_usdt") or -999) >= 100),
    ("islem15 3bar >= +25%", lambda s, i: (deg(s, i, "islem_15") or -999) >= 25),
    ("taker15 3bar <= -10%", lambda s, i: (deg(s, i, "taker_15") or 999) <= -10),
    ("hacim>=+50 VE taker<=-10", lambda s, i: (deg(s, i, "hacim_15_usdt") or -999) >= 50
     and (deg(s, i, "taker_15") or 999) <= -10),
]

if __name__ == "__main__":
    P = hazirla()
    print("KESINLIK TESTI — %d pozisyon" % len(P))
    print("TEPE = MFE bari (+-1 bar tolerans)\n")
    print("%-26s %8s %8s %9s %9s %11s"
          % ("tetik", "tetik", "tepede", "KESINLIK", "KAPSAMA", "tetik sonr."))
    print("-" * 78)
    for ad, f in TETIK:
        tet = tepede = 0
        tepe_top = 0
        sonra = []
        for p in P:
            s, pnl, it = p["seri"], p["pnl"], p["i_tepe"]
            tepe_top += 1
            bul = False
            for i in range(4, len(s) - 1):
                if not f(s, i):
                    continue
                tet += 1
                if abs(i - it) <= 1:
                    tepede += 1
                    bul = True
                # tetikte ciksaydik vs pozisyonun gercek sonu
                sonra.append(pnl[i] - pnl[-1])
            _ = bul
        # kapsama: kac pozisyonun TEPESI tetiklendi
        kaps = 0
        for p in P:
            s, it = p["seri"], p["i_tepe"]
            if any(f(s, i) for i in range(max(4, it - 1), min(len(s) - 1, it + 2))):
                kaps += 1
        print("%-26s %8d %8d %8.1f%% %8.1f%% %+11.3f"
              % (ad, tet, tepede, 100 * tepede / tet if tet else 0,
                 100 * kaps / tepe_top, sx.median(sonra) if sonra else 0))
    # TABAN ORAN
    tb = sum(1 for p in P for i in range(4, len(p["seri"]) - 1))
    tt = sum(1 for p in P if p["i_tepe"] >= 4)
    print("\nTABAN ORAN: %d bar icinde %d tepe -> rastgele bir bar tepe olma olasiligi %%%.2f"
          % (tb, tt, 100 * tt * 3 / tb if tb else 0))
    print("(tepe +-1 bar tolerans -> 3 bar sayilir)")
    print("\n'tetik sonr.' sutunu: tetikte CIKSAYDIK kazanilacak puan (medyan).")
    print("   POZITIF = cikmak iyiydi · NEGATIF = erken cikmis olurduk")
    print("\nHUKUM YAZILMADI.")
