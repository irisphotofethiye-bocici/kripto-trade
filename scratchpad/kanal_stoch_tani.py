#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KANAL + StochRSI — TANI (2026-08-11).  kanal_stoch.py SONRASI, KESIFSEL.

⚠️ BU BOLUM ON-KAYITLI DEGILDIR. Ana test (kanal_stoch.py) on-kayitli olcutle
KALDI. Buradaki her sey "neden kaldi" sorusunu cevaplamak icindir; buradan
cikan hicbir sayi "strateji su kadar kazandirir" diye kullanilamaz.
Cok sayida hucreye bakiliyor -> icinden pozitif cikmasi SANSLA beklenir.

UC SORU:
  1) Isabet neden %6.2? Basabas ne kadardi? (mekanizma)
  2) Hedef daha YAKIN olsaydi kurtulur muydu? (bant genisliginin %25/50/75/100'u)
  3) Ana testte iki yarida da pozitif cikan TEK hucre (ACC LONG + fiyat>MA200,
     N=786, +%0.05) gercek mi, gurultu mu? -> standart hata
"""
import json, os, statistics as stx, collections, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kanal_stoch as ks


def islem_hedefli(b, si, alt, ust, atr, ufuk, pay):
    """ks.islem ile ayni; hedef = giristen bant genisliginin `pay` kadari."""
    gi = si + 1
    if gi >= len(b) or None in (atr, alt, ust):
        return None
    ref = b[gi]["o"]
    if ref <= 0:
        return None
    dip = min(x["l"] for x in b[si - ks.STOP_NBAR + 1:si + 1])
    stop = min(dip, alt) - ks.STOP_ATR_PAY * atr
    hedef = ref + (ust - ref) * pay
    if not (stop < ref < hedef):
        return None
    sp = (ref - stop) / ref * 100
    hp = (hedef - ref) / ref * 100
    if sp <= 0 or hp <= 0:
        return None
    son = min(gi + ufuk, len(b))
    if son - gi < 2:
        return None
    for j in range(gi, son):
        if b[j]["l"] <= stop:
            return -sp - ks.MALIYET, "STOP", sp, hp
        if b[j]["h"] >= hedef:
            return hp - ks.MALIYET, "HEDEF", sp, hp
    c = b[son - 1]["c"]
    return (c - ref) / ref * 100 - ks.MALIYET, "SURE", sp, hp


def main():
    dosyalar = sorted(f[:-5] for f in os.listdir(ks.CACHE) if f.endswith(".json"))
    olay = []
    for sym in dosyalar:
        try:
            b = json.load(open(os.path.join(ks.CACHE, sym + ".json"), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ks.ISINMA + 60:
            continue
        c = [x["c"] for x in b]
        au, aa = ks.acc_bands(b)
        A = ks.atr_serisi(b)
        K, D = ks.stochrsi(ks.wilder_rsi(c))
        m200 = ks.ma(c, 200)
        son = -10 ** 9
        for i in range(ks.ISINMA, len(b) - ks.UFUK_IKINCIL - 2):
            if None in (K[i], D[i], K[i - 1], D[i - 1], A[i], aa[i]):
                continue
            if not (K[i - 1] < ks.ASIRI_SATIM and K[i - 1] <= D[i - 1] and K[i] > D[i]):
                continue
            if b[i]["l"] > aa[i]:
                continue
            if i - son < ks.SEYRELT:
                continue
            son = i
            olay.append({"b": b, "i": i, "t": b[i]["t"], "aa": aa[i], "au": au[i],
                         "atr": A[i], "trend": (m200[i] is not None and c[i] > m200[i])})
    tl = sorted(o["t"] for o in olay)
    ORTA = tl[len(tl) // 2]
    print("=" * 104)
    print("TANI — ACC LONG (bant+stoch) · KESIFSEL, ON-KAYITLI DEGIL")
    print("=" * 104)
    print(f"Olay: {len(olay)}\n")

    print("1) NEDEN KALDI — isabet vs basabas (ufuk 12 bar, hedef = ust bant)")
    print("-" * 104)
    k = [ks.islem(o["b"], o["i"], "LONG", o["aa"], o["au"], o["atr"], 12) for o in olay]
    k = [x for x in k if x]
    sp, hp = stx.median([x[2] for x in k]), stx.median([x[3] for x in k])
    isa = sum(1 for x in k if x[1] == "HEDEF") / len(k) * 100
    bb = (sp + ks.MALIYET) / ((hp - ks.MALIYET) + (sp + ks.MALIYET)) * 100
    print(f"  medyan stop %{sp:.2f} · medyan hedef %{hp:.2f} · R/R {hp/sp:.1f}:1")
    print(f"  GEREKEN basabas isabet : %{bb:.1f}")
    print(f"  GERCEKLESEN isabet     : %{isa:.1f}")
    print(f"  ACIK  : {isa - bb:+.1f} puan  ->  {'kapali' if isa >= bb else 'KAPANMIYOR'}")
    dag = collections.Counter(x[1] for x in k)
    print(f"  cikis dagilimi: " + " · ".join(f"{a} %{n/len(k)*100:.0f}" for a, n in dag.most_common()))

    print("\n2) HEDEF DAHA YAKIN OLSAYDI? — hedef = bant genisliginin payi (ufuk 12 bar)")
    print("-" * 104)
    print(f"{'hedef payi':16}{'N':>7}{'hedef%':>9}{'isabet':>9}{'basabas':>10}"
          f"{'net %':>9}{'A yari':>9}{'B yari':>9}")
    for pay in (0.25, 0.50, 0.75, 1.00):
        v = [(o, islem_hedefli(o["b"], o["i"], o["aa"], o["au"], o["atr"], 12, pay)) for o in olay]
        v = [(o, r) for o, r in v if r]
        if len(v) < 60:
            continue
        g = [r[0] for _, r in v]
        s_, h_ = stx.median([r[2] for _, r in v]), stx.median([r[3] for _, r in v])
        i_ = sum(1 for _, r in v if r[1] == "HEDEF") / len(v) * 100
        bb2 = (s_ + ks.MALIYET) / ((h_ - ks.MALIYET) + (s_ + ks.MALIYET)) * 100
        Av = [r[0] for o, r in v if o["t"] < ORTA]
        Bv = [r[0] for o, r in v if o["t"] >= ORTA]
        im = " *" if stx.mean(g) > 0 else ""
        print(f"bant x {pay:<9.2f}{len(v):7d}{h_:8.2f}%{i_:8.1f}%{bb2:9.1f}%"
              f"{stx.mean(g):+9.2f}{stx.mean(Av):+9.2f}{stx.mean(Bv):+9.2f}{im}")

    print("\n3) TEK HAYATTA KALAN HUCRE gercek mi? — ACC LONG + fiyat > MA200")
    print("-" * 104)
    for ad, sec in (("fiyat > MA200", [o for o in olay if o["trend"]]),
                    ("fiyat < MA200", [o for o in olay if not o["trend"]]),
                    ("TUMU", olay)):
        v = [ks.islem(o["b"], o["i"], "LONG", o["aa"], o["au"], o["atr"], 12) for o in sec]
        v = [x for x in v if x]
        if len(v) < 60:
            continue
        g = [x[0] for x in v]
        sh = stx.pstdev(g) / len(g) ** 0.5
        ort = stx.mean(g)
        print(f"  {ad:16} N={len(v):5d}  net {ort:+.3f}%  standart hata {sh:.3f}  "
              f"t = {ort/sh:+.2f}  ->  {'anlamli' if abs(ort/sh) >= 2 else 'GURULTU (|t| < 2)'}")
    print("\n  t = net / standart hata. |t| < 2 ise sifirdan ayirt edilemez.")


if __name__ == "__main__":
    main()
