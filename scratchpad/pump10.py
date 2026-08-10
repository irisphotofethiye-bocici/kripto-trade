#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PUMP + %10 HEDEF (2026-08-10) — "pumplara bakalim, long da ara"

Onceki olcum radar arsiviyle sinirliydi (radarin gordugu evren). Bu script TUM EVRENDE
(570 sembol, radar filtresi YOK) pump olaylarini %10 hedefle olcer — hem LONG hem SHORT.

TETIK: 24h getiri ilk kez esigi asan bar (72 bar dedup). Uc esik ayri ayri: %10 / %15 / %25.
GIRIS ZAMANLAMASI: tetikten 0 / 3 / 6 / 12 / 24 saat sonra.
HEDEF: giris ±%10 · STOP: botun A-varyanti · UFUK: 72 ve 168 saat (uzun tutus da denenir)
MALIYET: %0.09 gidis-donus.

AYRICA: pump'in ICINDE hangi ozellikler es zamanli olusuyorsa onlarin kirilimi
(hacim kati, uzanim, ATR patlamasi) — "kazananlarin ozellikleri hangi asamada ortusuyor".
"""
import json, os, statistics as st, collections

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h")
NBAR, MALIYET = 10, 0.09
HEDEF = 10.0


def atr14(b, i):
    if i < 14:
        return None
    tr = []
    for j in range(i - 13, i + 1):
        p = b[j - 1]["c"]
        tr.append(max(b[j]["h"] - b[j]["l"], abs(b[j]["h"] - p), abs(p - b[j]["l"])))
    return st.mean(tr)


def swings(b, i, left=3, right=3, geri=100):
    bas = max(left, i - geri)
    hi, lo = [], []
    for j in range(bas, i - right + 1):
        w = b[j - left:j + right + 1]
        if not w:
            continue
        if b[j]["h"] == max(x["h"] for x in w):
            hi.append(b[j]["h"])
        if b[j]["l"] == min(x["l"] for x in w):
            lo.append(b[j]["l"])
    return hi, lo


def oyna(b, gi, yon, ufuk):
    i = gi - 1
    if i < 30 or gi >= len(b):
        return None
    a = atr14(b, i)
    if not a or a <= 0:
        return None
    ref = b[gi]["o"]
    hi, lo = swings(b, i)
    if yon == "LONG":
        sup = max([x for x in lo if x < ref], default=None)
        ad = []
        if sup is not None and (ref - sup) <= 3 * a:
            ad.append(sup - 0.25 * a)
        nb = min(x["l"] for x in b[max(0, i - NBAR + 1):i + 1])
        if nb < ref:
            ad.append(nb - 0.25 * a)
        ad.append(ref - 1.5 * a)
        gec = [s for s in ad if s < ref]
        stop = max(gec) if gec else ref - 1.5 * a
        hedef = ref * (1 + HEDEF / 100)
    else:
        res = min([x for x in hi if x > ref], default=None)
        ad = []
        if res is not None and (res - ref) <= 3 * a:
            ad.append(res + 0.25 * a)
        nb = max(x["h"] for x in b[max(0, i - NBAR + 1):i + 1])
        if nb > ref:
            ad.append(nb + 0.25 * a)
        ad.append(ref + 1.5 * a)
        gec = [s for s in ad if s > ref]
        stop = min(gec) if gec else ref + 1.5 * a
        hedef = ref * (1 - HEDEF / 100)
    sp = abs(ref - stop) / ref * 100
    if sp <= 0:
        return None
    son = min(gi + ufuk, len(b))
    if son - gi < 6:
        return None
    for j in range(gi, son):
        x = b[j]
        if yon == "LONG":
            if x["l"] <= stop:
                return -sp - MALIYET, "STOP", sp
            if x["h"] >= hedef:
                return HEDEF - MALIYET, "HEDEF", sp
        else:
            if x["h"] >= stop:
                return -sp - MALIYET, "STOP", sp
            if x["l"] <= hedef:
                return HEDEF - MALIYET, "HEDEF", sp
    c = b[son - 1]["c"]
    g = (c - ref) / ref * 100 if yon == "LONG" else (ref - c) / ref * 100
    return g - MALIYET, "SURE", sp


def oz(k):
    if not k:
        return None
    g = [x[0] for x in k]
    return {"n": len(g), "ort": st.mean(g), "sh": st.pstdev(g) / len(g) ** 0.5 if len(g) > 1 else 0,
            "hedef": sum(1 for x in k if x[1] == "HEDEF") / len(g) * 100,
            "stop_med": st.median([x[2] for x in k])}


def main():
    dosyalar = [f[:-5] for f in os.listdir(CACHE) if f.endswith(".json")]
    print(f"TUM EVREN: {len(dosyalar)} sembol · radar filtresi YOK · hedef %{HEDEF} · maliyet %{MALIYET}\n")

    for TETIK in (10.0, 15.0, 25.0):
        olay = []
        for sym in dosyalar:
            try:
                b = json.load(open(os.path.join(CACHE, f"{sym}.json")))
            except Exception:
                continue
            if len(b) < 150:
                continue
            son = -999
            for i in range(24, len(b) - 40):
                if i - son < 72:
                    continue
                onc = b[i - 24]["c"]
                if not onc:
                    continue
                if (b[i]["c"] / onc - 1) * 100 < TETIK:
                    continue
                son = i
                a = atr14(b, i)
                tepe20 = max(x["h"] for x in b[max(0, i - 19):i + 1])
                olay.append({"sym": sym, "i": i, "b": b,
                             "uzanim": (tepe20 - b[i]["c"]) / a if a else None,
                             "r24": (b[i]["c"] / onc - 1) * 100})
        print("=" * 104)
        print(f"TETIK: 24h getiri ilk kez > %{TETIK:.0f}   ->   {len(olay)} olay (46 gun)")
        print("=" * 104)
        print(f"{'giris':14}{'ufuk':>7}{'LONG net %':>13}{'hedefe':>9}{'SHORT net %':>14}{'hedefe':>9}{'stop med':>10}")
        print("-" * 104)
        for ufuk, uad in ((72, "72s"), (168, "168s")):
            for gec, gad in ((0, "hemen"), (3, "+3 saat"), (6, "+6 saat"),
                             (12, "+12 saat"), (24, "+24 saat")):
                L = [oyna(o["b"], o["i"] + 1 + gec, "LONG", ufuk) for o in olay]
                S = [oyna(o["b"], o["i"] + 1 + gec, "SHORT", ufuk) for o in olay]
                L = [x for x in L if x]; S = [x for x in S if x]
                a, s = oz(L), oz(S)
                if not a:
                    continue
                print(f"{gad:14}{uad:>7}{a['ort']:+13.2f}{a['hedef']:8.1f}%"
                      f"{s['ort']:+14.2f}{s['hedef']:8.1f}%{a['stop_med']:9.2f}%")
        if TETIK == 15.0:
            print("\n  --- hareket buyuklugune gore (giris hemen, 72s) ---")
            for lo_, hi_ in ((15, 25), (25, 40), (40, 70), (70, 9999)):
                alt = [o for o in olay if lo_ <= o["r24"] < hi_]
                if len(alt) < 15:
                    continue
                L = [x for x in (oyna(o["b"], o["i"] + 1, "LONG", 72) for o in alt) if x]
                S = [x for x in (oyna(o["b"], o["i"] + 1, "SHORT", 72) for o in alt) if x]
                a, s = oz(L), oz(S)
                print(f"    24h %{lo_}-{hi_ if hi_ < 9999 else '+':<5} N={a['n']:4d}  "
                      f"LONG {a['ort']:+6.2f}% (hedefe %{a['hedef']:.0f})  "
                      f"SHORT {s['ort']:+6.2f}% (hedefe %{s['hedef']:.0f})")
            print("\n  --- UZANIM (20-bar tepesinden ATR uzakligi, giris hemen) ---")
            for lo_, hi_ in ((0, 0.5), (0.5, 1.5), (1.5, 3.0), (3.0, 99)):
                alt = [o for o in olay if o["uzanim"] is not None and lo_ <= o["uzanim"] < hi_]
                if len(alt) < 15:
                    continue
                L = [x for x in (oyna(o["b"], o["i"] + 1, "LONG", 72) for o in alt) if x]
                S = [x for x in (oyna(o["b"], o["i"] + 1, "SHORT", 72) for o in alt) if x]
                a, s = oz(L), oz(S)
                print(f"    tepeden {lo_}-{hi_} ATR  N={a['n']:4d}  "
                      f"LONG {a['ort']:+6.2f}% (hedefe %{a['hedef']:.0f})  "
                      f"SHORT {s['ort']:+6.2f}% (hedefe %{s['hedef']:.0f})")
        print()


if __name__ == "__main__":
    main()
