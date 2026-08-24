#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TOTAL REJIMINE GORE POZ ACSAK KAZANC VAR MI? — YALNIZ BIZIM CEKTIGIMIZ VERI.

KULLANICI (2026-08-21): "totalleri hesaba katip ona gore rejim belirleyip poz
acarsa kazanc yok mu diyorsun. Sadece bizim veri ile test et, 2 yillik veriyi
kullanma."

KULLANILAN VERI (yalnizca kendi cektiklerimiz):
   scratchpad/gecko/  98 coin x gunluk market cap x 365 gun
   -> TOTAL1/2/3X ve rejim etiketi BURADAN
   -> coin getirileri de BURADAN (mcap degisimi)
Binance'in 2 yillik kline seti KULLANILMADI.

⚠️ MCAP VEKILI: gunluk mcap degisimi ~ fiyat degisimi. Arz degisimi (unlock,
   yakma) bunu kirletir. Coinlerin cogunda gunluk arz degisimi kucuktur ama
   SIFIR DEGILDIR -> bu bir YAKLASIKLIKTIR, raporda oyle gecer.

MALIYET: her islemde gidis-donus taker+slipaj (olcum_ortak.MALIYET).
   Gunluk yeniden dengeleme varsayilir -> her gun 1 maliyet.

HUKUM YAZILMAZ.
SALT OKUMA.
"""
import os, sys, json, collections, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
sys.path.insert(0, SCRATCH)
import olcum_ortak as oo                                        # noqa: E402

GECKO = os.path.join(SCRATCH, "gecko")
STABLE = {"tether", "usd-coin", "dai", "first-digital-usd", "ethena-usde", "usds",
          "paypal-usd", "true-usd", "binance-usd", "usdd", "frax"}


def yukle():
    mc = {}
    for f in os.listdir(GECKO):
        if f.endswith(".json") and not f.startswith("_"):
            try:
                with open(os.path.join(GECKO, f), encoding="utf-8") as fh:
                    mc[f[:-5]] = json.load(fh)
            except Exception:
                pass
    say = collections.Counter()
    for d in mc.values():
        say.update(d.keys())
    g = sorted(x for x, n in say.items() if n >= len(mc) * 0.8)
    return mc, g


if __name__ == "__main__":
    mc, g = yukle()
    alt = {k: v for k, v in mc.items() if k not in STABLE}
    print("BIZIM VERI: %d coin (%d stable haric) x %d gun (%s -> %s)"
          % (len(mc), len(mc) - len(alt), len(g), g[0], g[-1]))
    print("maliyet: %%%.4f (gidis-donus, gunluk yeniden dengeleme varsayimi)\n" % oo.MALIYET)

    # --- TOTAL3X ve rejim ---
    T = {}
    for d in g:
        t1 = sum(v[d] for v in mc.values() if d in v)
        btc = mc.get("bitcoin", {}).get(d, 0)
        eth = mc.get("ethereum", {}).get(d, 0)
        stb = sum(mc[s][d] for s in STABLE if s in mc and d in mc[s])
        T[d] = {"T1": t1, "T3X": t1 - btc - eth - stb}
    rej = {}
    for i, d in enumerate(g):
        if i < 3:
            continue
        o = T[g[i - 3]]["T3X"]
        v = (T[d]["T3X"] - o) / o * 100 if o else 0
        rej[d] = "BOGA" if v > 2 else ("AYI" if v < -2 else "NOTR")

    # --- gunluk alt getirisi (mcap vekili) ---
    gun_get = {}
    for i, d in enumerate(g):
        if i == 0:
            continue
        p = g[i - 1]
        v = []
        for k, s in alt.items():
            if d in s and p in s and s[p] > 0:
                v.append((s[d] - s[p]) / s[p] * 100)
        if len(v) >= 30:
            gun_get[d] = sx.median(v)

    print("=" * 96)
    print("1) REJIM ETIKETI ACIKKEN O GUN VE SONRAKI GUNLER NE OLDU")
    print("=" * 96)
    print("%-8s %6s %12s %12s %12s" % ("rejim", "gun", "AYNI gun", "SONRAKI gun", "sonraki 3 gun"))
    print("-" * 56)
    for r in ("BOGA", "NOTR", "AYI"):
        gl = [d for d in g if rej.get(d) == r and d in gun_get]
        if len(gl) < 10:
            continue
        ayni = [gun_get[d] for d in gl]
        son1, son3 = [], []
        for d in gl:
            i = g.index(d)
            if i + 1 < len(g) and g[i + 1] in gun_get:
                son1.append(gun_get[g[i + 1]])
            if i + 3 < len(g):
                v = [gun_get[g[j]] for j in range(i + 1, i + 4) if g[j] in gun_get]
                if len(v) == 3:
                    son3.append(sum(v))
        print("%-8s %6d %+12.4f %+12.4f %+12.4f"
              % (r, len(gl), sx.mean(ayni), sx.mean(son1) if son1 else 0,
                 sx.mean(son3) if son3 else 0))

    print("\n" + "=" * 96)
    print("2) STRATEJI SIMULASYONU — rejime gore poz ac, ERTESI gun getirisini al")
    print("   (etiket t gununde okunur, poz t+1'de acilir -> ileriye bakma YOK)")
    print("=" * 96)
    STR = [
        ("BOGA'da LONG, digerinde bos", lambda r: 1 if r == "BOGA" else 0),
        ("AYI'da SHORT, digerinde bos", lambda r: -1 if r == "AYI" else 0),
        ("BOGA LONG + AYI SHORT", lambda r: 1 if r == "BOGA" else (-1 if r == "AYI" else 0)),
        ("TERSI: BOGA SHORT + AYI LONG", lambda r: -1 if r == "BOGA" else (1 if r == "AYI" else 0)),
        ("HER ZAMAN LONG (kiyas)", lambda r: 1),
        ("HER ZAMAN SHORT (kiyas)", lambda r: -1),
    ]
    print("%-32s %8s %12s %12s %10s %9s" % ("strateji", "islem", "brut top%", "NET top%", "gun-ort", "poz gun%"))
    print("-" * 88)
    for ad, f in STR:
        brut, net, n = 0.0, 0.0, 0
        gunluk = []
        for i, d in enumerate(g[:-1]):
            r = rej.get(d)
            if r is None:
                continue
            y = f(r)
            if y == 0:
                continue
            nd = g[i + 1]
            if nd not in gun_get:
                continue
            b = y * gun_get[nd]
            brut += b
            net += b - oo.MALIYET
            gunluk.append(b - oo.MALIYET)
            n += 1
        if n < 20:
            continue
        print("%-32s %8d %+12.2f %+12.2f %+10.4f %8.0f%%"
              % (ad, n, brut, net, net / n, 100 * sum(1 for x in gunluk if x > 0) / n))

    print("\n" + "=" * 96)
    print("3) MALIYETSIZ (ust sinir) — maliyet SIFIR olsa bile kazanc var mi?")
    print("=" * 96)
    for ad, f in STR[:4]:
        brut, n = 0.0, 0
        for i, d in enumerate(g[:-1]):
            r = rej.get(d)
            if r is None:
                continue
            y = f(r)
            if y == 0:
                continue
            nd = g[i + 1]
            if nd in gun_get:
                brut += y * gun_get[nd]
                n += 1
        if n >= 20:
            print("  %-32s islem %4d   brut toplam %+8.2f%%   islem basi %+.4f%%"
                  % (ad, n, brut, brut / n))
    print("\nHUKUM YAZILMADI. mcap vekili yaklasikligi raporda gecerli.")
