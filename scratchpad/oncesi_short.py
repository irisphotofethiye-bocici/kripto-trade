#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HAREKET ÖNCESİ SİNYAL — İKİ YÖNLÜ (2026-08-10)

Kullanici: "bunu sadece short icin mi yaptin" -> HAYIR, TAM TERSI: onceki olcum yalniz
LONG'du (kendi notumda sinir olarak yazilmis ama kapatilmamisti). Bu script ayni
on-hareket sinyallerini SHORT tarafinda da olcer.

BEKLENTI (on-kayit): sinyal YON degil HAREKET onguruyordu; ve tetik sonrasi fiyat
duserken (tetik +24s medyan -2.62%) -> ayni sinyallerde SHORT, LONG'dan IYI olmali.
Eger SHORT da negatifse sinyal tamamen degersizdir; SHORT pozitifse "kovalama" degil
"fade" tarafinda kullanilabilir bir on-sinyal bulunmus olur.

MEKANIK: botun gercek A-stopu (yon simetrik) · hedef %2.5/24s ve %10/72s ·
fitil bazli · ayni barda ikisi de -> STOP · maliyet %0.09 gidis-donus.
KONTROL: ayni sembol/donemde rastgele barlar. Zaman ikiye bolunerek dogrulanir.
"""
import json, os, random, statistics as st

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h")
NBAR, MALIYET = 10, 0.09
random.seed(31)


def atr(b, i, n=14):
    if i < n:
        return None
    tr = []
    for j in range(i - n + 1, i + 1):
        p = b[j - 1]["c"]
        tr.append(max(b[j]["h"] - b[j]["l"], abs(b[j]["h"] - p), abs(p - b[j]["l"])))
    return st.mean(tr)


def swings2(b, i, left=3, right=3, geri=100):
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


def islem(b, gi, hedef_pct, ufuk, yon):
    i = gi - 1
    if i < 200 or gi >= len(b):
        return None
    a = atr(b, i)
    if not a or a <= 0:
        return None
    ref = b[gi]["o"]
    hi, lo = swings2(b, i)
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
        hedef = ref * (1 + hedef_pct / 100)
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
        hedef = ref * (1 - hedef_pct / 100)
    sp = abs(ref - stop) / ref * 100
    if sp <= 0:
        return None
    son = min(gi + ufuk, len(b))
    if son - gi < 4:
        return None
    for j in range(gi, son):
        x = b[j]
        if yon == "LONG":
            if x["l"] <= stop:
                return -sp - MALIYET, "STOP", sp
            if x["h"] >= hedef:
                return hedef_pct - MALIYET, "HEDEF", sp
        else:
            if x["h"] >= stop:
                return -sp - MALIYET, "STOP", sp
            if x["l"] <= hedef:
                return hedef_pct - MALIYET, "HEDEF", sp
    c = b[son - 1]["c"]
    g = (c - ref) / ref * 100 if yon == "LONG" else (ref - c) / ref * 100
    return g - MALIYET, "SURE", sp


def oz(k, hedef):
    k = [x for x in k if x]
    if not k:
        return None
    g = [x[0] for x in k]
    sp = st.median([x[2] for x in k])
    return {"n": len(g), "ort": st.mean(g), "sh": st.pstdev(g) / len(g) ** 0.5 if len(g) > 1 else 0,
            "isabet": sum(1 for x in k if x[1] == "HEDEF") / len(g) * 100,
            "basabas": sp / (hedef + sp) * 100, "stop": sp}


KOS = {
    "chg_6h >= %3": lambda o: o["chg_6h"] >= 3,
    "hacim>=3 & chg_6h>=3": lambda o: o["hacim"] >= 3 and o["chg_6h"] >= 3,
    "hacim>=6 & pos20>=0.85": lambda o: o["hacim"] >= 6 and o["pos20"] >= 0.85,
    "chg_24h %3-8 (usulca)": lambda o: 3 <= o["chg_24h"] < 8,
    "pos20 >= 0.85": lambda o: o["pos20"] >= 0.85,
    "hacim_kat_1h >= 6": lambda o: o["hacim"] >= 6,
    "KONTROL (rastgele)": None,
}


def main():
    dosyalar = sorted(f[:-5] for f in os.listdir(CACHE) if f.endswith(".json"))
    topla = {k: [] for k in KOS}
    for sym in dosyalar:
        try:
            b = json.load(open(os.path.join(CACHE, f"{sym}.json")))
        except Exception:
            continue
        if len(b) < 400 or "qv" not in b[-1]:
            continue
        c = [x["c"] for x in b]
        qv = [x.get("qv", 0.0) for x in b]
        son_kayit = {k: -999 for k in KOS}
        for i in range(200, len(b) - 80, 2):
            med24 = st.median(qv[i - 23:i + 1]) or 1e-9
            hi20 = max(x["h"] for x in b[i - 19:i + 1])
            lo20 = min(x["l"] for x in b[i - 19:i + 1])
            o = {"hacim": qv[i] / med24,
                 "chg_6h": (c[i] / c[i - 6] - 1) * 100 if c[i - 6] else 0,
                 "chg_24h": (c[i] / c[i - 24] - 1) * 100 if c[i - 24] else 0,
                 "pos20": (c[i] - lo20) / (hi20 - lo20) if hi20 > lo20 else 0.5}
            for ad, fn in KOS.items():
                if fn is None or not fn(o):
                    continue
                if i - son_kayit[ad] < 24:
                    continue
                son_kayit[ad] = i
                topla[ad].append((b, i, b[i]["t"]))
        for _ in range(max(3, len(b) // 200)):
            k = random.randint(200, len(b) - 80)
            topla["KONTROL (rastgele)"].append((b, k, b[k]["t"]))

    tsl = sorted(t for v in topla.values() for _, _, t in v)
    ORTA = tsl[len(tsl) // 2]
    print("=" * 116)
    print("HAREKET ÖNCESİ SİNYAL — LONG ve SHORT YAN YANA (botun A-stopu, maliyet %0.09)")
    print("=" * 116)
    for hedef, ufuk in ((2.5, 24), (10.0, 72)):
        print(f"\n### hedef %{hedef} · ufuk {ufuk} saat")
        print(f"{'sinyal':26}{'N':>7}{'LONG net':>10}{'isabet':>8}"
              f"{'SHORT net':>11}{'isabet':>8}{'stop%':>8}{'S: A yari':>11}{'S: B yari':>11}")
        print("-" * 116)
        for ad in KOS:
            v = topla[ad]
            if len(v) < 100:
                continue
            L = oz([islem(bb, ii + 1, hedef, ufuk, "LONG") for bb, ii, _ in v], hedef)
            S = oz([islem(bb, ii + 1, hedef, ufuk, "SHORT") for bb, ii, _ in v], hedef)
            SA = oz([islem(bb, ii + 1, hedef, ufuk, "SHORT") for bb, ii, t in v if t < ORTA], hedef)
            SB = oz([islem(bb, ii + 1, hedef, ufuk, "SHORT") for bb, ii, t in v if t >= ORTA], hedef)
            if not L or not S:
                continue
            im = " *" if S["ort"] > 0 else ""
            print(f"{ad:26}{L['n']:7d}{L['ort']:+10.2f}{L['isabet']:7.1f}%"
                  f"{S['ort']:+11.2f}{S['isabet']:7.1f}%{S['stop']:7.2f}%"
                  f"{(SA['ort'] if SA else 0):+11.2f}{(SB['ort'] if SB else 0):+11.2f}{im}")
    print("\n  '*' = SHORT net pozitif")


if __name__ == "__main__":
    main()
