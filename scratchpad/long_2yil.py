#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIKIR 1 x FIKIR 3 — IKI LONG HUCRESI, 2 YILLIK VERIDE (2026-08-11)

ARSIVDE BULUNAN (60 gun, 6790 olay, HAM olcum):
  A) fiyat YUKSEK + chg24 dusuk  -> 24s  +1.30 (t=+4.01)  A +1.19 / B +1.45
  B) MA50 dusuk + fiyat YUKSEK   -> 12s  +1.02 (t=+2.90)  A +1.28 / B +0.60
  Ikisi de A-stopla oluyordu (stop %0.98 -> dar dilim). Yanlis negatif adayi.

SIMDI: 566 sembol · 6.88M bar · 2024-08 -> 2026-08 · GERCEK BOGA VE AYI ICERIYOR.

ESIKLER ARSIVDEN AYNEN ALINDI — yeniden hesaplanmadi (yeniden hesaplamak
orneklem-ici uydurma olurdu):
    chg24 <= -3.662%   ·   ma50_mesafe <= -2.945%   ·   fiyat "YUKSEK"

FIYAT ESIGI IKI SEKILDE:
  (a) MUTLAK  $58.884 (arsivin %80 dilimi) — en kati disari-orneklem testi
  (b) AYLIK DILIM: her ay evrenin %80 dilimi — "pahali" kavramina sadik
      (fiyat seviyeleri 2 yilda kayar; mutlak esik farkli bir populasyon secebilir)
  Ikisi de raporlanir. Ayrisirlarsa bu bilgidir, gizlenmez.

ORNEKLEM AYRIMI:
  ICI  : 2026-06-12 -> 2026-08-10  (hucrelerin BULUNDUGU pencere)
  DISI : 2024-08-11 -> 2026-06-11  (~22 ay, HIC GORULMEMIS)  <- ASIL KARAR BURADAN

REJIM: BTC 30 gunluk kayan getiri >= +%15 BOGA · <= -%15 AYI · arasi NOTR
KONTROL: ayni sembol/donemde rastgele barlar, ayni mekanik.
HAM olcum: stop yok · hedef yok · maliyet %0.09 dusulmus.
SISTEME DOKUNULMAZ.
"""
import json, os, sys, random, statistics as stx, datetime, collections

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h_uzun")
MALIYET = 0.09
CHG_ESIK, MA50_ESIK, FIYAT_MUTLAK = -3.662, -2.945, 58.884
SEYRELT, ISINMA = 24, 220
ICI_BAS = int(datetime.datetime(2026, 6, 12).timestamp() * 1000)
random.seed(37)


def ma(v, n):
    out, s = [None] * len(v), 0.0
    for i, x in enumerate(v):
        s += x
        if i >= n:
            s -= v[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def btc_rejim():
    b = json.load(open(os.path.join(CACHE, "BTC.json"), encoding="utf-8"))
    c = [x["c"] for x in b]
    pen = 720
    out = {}
    for i in range(pen, len(b)):
        g = (c[i] / c[i - pen] - 1) * 100
        out[b[i]["t"] // 3600000] = "BOGA" if g >= 15 else ("AYI" if g <= -15 else "NOTR")
    return out


def aylik_fiyat_esigi(dosyalar):
    """her ay icin evrenin %80 fiyat dilimi (24 barda bir orneklenerek)"""
    ay = collections.defaultdict(list)
    for f in dosyalar:
        try:
            b = json.load(open(os.path.join(CACHE, f), encoding="utf-8"))
        except Exception:
            continue
        for x in b[::24]:
            d = datetime.datetime.fromtimestamp(x["t"] / 1000)
            ay[(d.year, d.month)].append(x["c"])
    return {k: sorted(v)[int(len(v) * 0.8)] for k, v in ay.items() if len(v) >= 50}


def oz(v, asgari=40):
    v = [x for x in v if x is not None]
    if len(v) < asgari:
        return None
    sh = stx.pstdev(v) / len(v) ** 0.5 if len(v) > 1 else 0
    return {"n": len(v), "ort": stx.mean(v), "sh": sh, "t": stx.mean(v) / sh if sh else 0}


def main():
    dosyalar = sorted(f for f in os.listdir(CACHE) if f.endswith(".json"))
    print("Aylik fiyat esikleri hesaplaniyor...", flush=True)
    esik_ay = aylik_fiyat_esigi(dosyalar)
    rej = btc_rejim()
    print(f"  {len(esik_ay)} ay · ornek: "
          + " ".join(f"{y}-{m:02d}=${v:.0f}" for (y, m), v in sorted(esik_ay.items())[::8]),
          flush=True)

    olay = {"A_mutlak": [], "A_aylik": [], "B_mutlak": [], "B_aylik": [], "KONTROL": []}
    for n, f in enumerate(dosyalar, 1):
        if f == "BTC.json":
            continue
        try:
            b = json.load(open(os.path.join(CACHE, f), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ISINMA + 60:
            continue
        c = [x["c"] for x in b]
        m50 = ma(c, 50)
        son = collections.defaultdict(lambda: -10 ** 9)

        def ekle(ad, i):
            if i - son[ad] < SEYRELT or i + 24 >= len(b):
                return
            son[ad] = i
            gi = i + 1
            ref = b[gi]["o"]
            if ref <= 0:
                return
            r12 = (b[gi + 12]["c"] / ref - 1) * 100 - MALIYET
            r24 = (b[gi + 24]["c"] / ref - 1) * 100 - MALIYET
            olay[ad].append({"t": b[i]["t"], "r12": r12, "r24": r24,
                             "rej": rej.get(b[i]["t"] // 3600000),
                             "ici": b[i]["t"] >= ICI_BAS})

        for i in range(ISINMA, len(b) - 26):
            if m50[i] is None or c[i - 24] <= 0:
                continue
            px = c[i]
            d = datetime.datetime.fromtimestamp(b[i]["t"] / 1000)
            ea = esik_ay.get((d.year, d.month))
            chg24 = (px / c[i - 24] - 1) * 100
            ma50m = (px / m50[i] - 1) * 100
            pahali_m = px >= FIYAT_MUTLAK
            pahali_a = ea is not None and px >= ea
            if chg24 <= CHG_ESIK:
                if pahali_m:
                    ekle("A_mutlak", i)
                if pahali_a:
                    ekle("A_aylik", i)
            if ma50m <= MA50_ESIK:
                if pahali_m:
                    ekle("B_mutlak", i)
                if pahali_a:
                    ekle("B_aylik", i)
        for _ in range(max(2, (len(b) - ISINMA) // 200)):
            i = random.randint(ISINMA, len(b) - 27)
            ekle("KONTROL", i)
        if n % 150 == 0:
            print(f"  {n}/{len(dosyalar)} ...", flush=True)

    AD = {"A_mutlak": "A) fiyat>=$58.9 + chg24 dusuk", "A_aylik": "A) fiyat AYLIK%80 + chg24 dusuk",
          "B_mutlak": "B) MA50 dusuk + fiyat>=$58.9", "B_aylik": "B) MA50 dusuk + fiyat AYLIK%80",
          "KONTROL": "KONTROL rastgele"}
    print("\n" + "=" * 112)
    print("IKI LONG HUCRESI — 2 YILLIK VERIDE (ham, stopsuz, maliyet dusulmus)")
    print("=" * 112)
    for etiket, fn in (("ORNEKLEM DISI (2024-08 -> 2026-06, ~22 ay) — ASIL KARAR",
                        lambda o: not o["ici"]),
                       ("ORNEKLEM ICI (2026-06-12 ->, hucrelerin bulundugu pencere)",
                        lambda o: o["ici"])):
        print(f"\n### {etiket}")
        print(f"{'hucre':36}{'N':>7}{'12s net':>10}{'t':>7}{'24s net':>10}{'t':>7}")
        print("-" * 112)
        for k in ("A_mutlak", "A_aylik", "B_mutlak", "B_aylik", "KONTROL"):
            s = [o for o in olay[k] if fn(o)]
            a12, a24 = oz([o["r12"] for o in s]), oz([o["r24"] for o in s])
            if not a12:
                continue
            im = " *" if a24 and a24["ort"] > 0 else ""
            print(f"{AD[k]:36}{a12['n']:7d}{a12['ort']:+10.2f}{a12['t']:+7.2f}"
                  f"{(a24['ort'] if a24 else 0):+10.2f}{(a24['t'] if a24 else 0):+7.2f}{im}")

    print("\n" + "=" * 112)
    print("REJIME GORE (yalniz ORNEKLEM DISI) — 'bogada calisir mi?' ARTIK TEST EDILEBILIR")
    print("=" * 112)
    print(f"{'hucre':36}{'rejim':8}{'N':>7}{'24s net':>10}{'t':>7}{'KONTROL':>10}{'FARK':>9}")
    print("-" * 112)
    for k in ("A_mutlak", "A_aylik", "B_mutlak", "B_aylik"):
        for r in ("BOGA", "NOTR", "AYI"):
            s = [o["r24"] for o in olay[k] if not o["ici"] and o["rej"] == r]
            kk = [o["r24"] for o in olay["KONTROL"] if not o["ici"] and o["rej"] == r]
            a, ko = oz(s), oz(kk)
            if not a or not ko:
                continue
            print(f"{AD[k]:36}{r:8}{a['n']:7d}{a['ort']:+10.2f}{a['t']:+7.2f}"
                  f"{ko['ort']:+10.2f}{a['ort']-ko['ort']:+9.2f}")
        print()

    print("=" * 112)
    print("CEYREKLERE GORE (ornek: A_aylik, 24s) — kenar dayanikli mi yoksa tek donemlik mi?")
    print("=" * 112)
    for k in ("A_aylik", "B_aylik"):
        print(f"\n{AD[k]}")
        ceyrek = collections.defaultdict(list)
        for o in olay[k]:
            d = datetime.datetime.fromtimestamp(o["t"] / 1000)
            ceyrek[(d.year, (d.month - 1) // 3 + 1)].append(o["r24"])
        kc = collections.defaultdict(list)
        for o in olay["KONTROL"]:
            d = datetime.datetime.fromtimestamp(o["t"] / 1000)
            kc[(d.year, (d.month - 1) // 3 + 1)].append(o["r24"])
        for key in sorted(ceyrek):
            a, ko = oz(ceyrek[key]), oz(kc[key])
            if not a:
                continue
            im = " *" if a["ort"] > 0 else ""
            print(f"  {key[0]}-Q{key[1]}  N={a['n']:5d}  net {a['ort']:+7.2f}  t={a['t']:+5.2f}"
                  f"  kontrol {(ko['ort'] if ko else 0):+7.2f}{im}")


if __name__ == "__main__":
    main()
