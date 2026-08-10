#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ÖNCESİ SİNYALİ — PARA KAZANDIRIYOR MU? (2026-08-10)

BULUNAN: hareket oncesi TAHMIN EDICI yapi VAR (ileriye bakis, taban oran %5.68):
    chg_6h >= %3            -> %19.29 tetik  (KAT 3.40)  A %19.47 / B %19.09
    hacim>=3 VE chg_6h>=3   -> %18.93        (KAT 3.33)
    hacim>=6 VE pos20>=0.85 -> %16.35        (KAT 2.88)
    chg_24h %3-8 (usulca)   -> %12.50        (KAT 2.20)
    sikisma < 0.65          -> % 5.33        (KAT 0.94)  <- SIKISMA HICBIR SEY DEMIYOR

AMA "tetik gelme olasiligi" ile "para kazanmak" AYNI SEY DEGIL: tetik anindan sonrasi
zaten olculdu ve negatifti (+24s medyan -2.62%). Bu script kalan soruyu kapatir:
tetik GELMEDEN, sinyal aninda girilse ne olurdu?

MEKANIK: botun gercek A-stopu · hedef %2.5 ve %10 ayri ayri · ufuk 24 ve 72 saat ·
fitil bazli · ayni barda ikisi de -> STOP · maliyet %0.09 gidis-donus.
Ayrica ham forward getiri (+6s/+24s) da raporlanir.
KONTROL: ayni sembol/donemde rastgele barlar (taban).
Zaman ikiye bolunerek dogrulanir.
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


def swings(b, i, left=3, right=3, geri=100):
    bas = max(left, i - geri)
    lo = []
    for j in range(bas, i - right + 1):
        w = b[j - left:j + right + 1]
        if w and b[j]["l"] == min(x["l"] for x in w):
            lo.append(b[j]["l"])
    return lo


def islem(b, gi, hedef_pct, ufuk):
    """LONG, botun A-stopu. -> (net %, sonuc, stop%) | None"""
    i = gi - 1
    if i < 200 or gi >= len(b):
        return None
    a = atr(b, i)
    if not a or a <= 0:
        return None
    ref = b[gi]["o"]
    lo = swings(b, i)
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
    sp = (ref - stop) / ref * 100
    if sp <= 0:
        return None
    hedef = ref * (1 + hedef_pct / 100)
    son = min(gi + ufuk, len(b))
    if son - gi < 4:
        return None
    for j in range(gi, son):
        x = b[j]
        if x["l"] <= stop:
            return -sp - MALIYET, "STOP", sp
        if x["h"] >= hedef:
            return hedef_pct - MALIYET, "HEDEF", sp
    return (b[son - 1]["c"] - ref) / ref * 100 - MALIYET, "SURE", sp


def oz(k, hedef):
    k = [x for x in k if x]
    if not k:
        return None
    g = [x[0] for x in k]
    sp = st.median([x[2] for x in k])
    return {"n": len(g), "ort": st.mean(g), "sh": st.pstdev(g) / len(g) ** 0.5 if len(g) > 1 else 0,
            "isabet": sum(1 for x in k if x[1] == "HEDEF") / len(g) * 100,
            "basabas": sp / (hedef + sp) * 100, "stop": sp}


def main():
    dosyalar = sorted(f[:-5] for f in os.listdir(CACHE) if f.endswith(".json"))
    KOS = {
        "chg_6h >= %3": lambda o: o["chg_6h"] >= 3,
        "hacim>=3 & chg_6h>=3": lambda o: o["hacim"] >= 3 and o["chg_6h"] >= 3,
        "hacim>=6 & pos20>=0.85": lambda o: o["hacim"] >= 6 and o["pos20"] >= 0.85,
        "chg_24h %3-8 (usulca)": lambda o: 3 <= o["chg_24h"] < 8,
        "pos20 >= 0.85": lambda o: o["pos20"] >= 0.85,
        "hacim_kat_1h >= 6": lambda o: o["hacim"] >= 6,
        "KONTROL (rastgele)": None,
    }
    topla = {k: [] for k in KOS}
    fwd = {k: [] for k in KOS}
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
            hi20 = max(x["h"] for x in b[i - 19:i + 1]); lo20 = min(x["l"] for x in b[i - 19:i + 1])
            o = {"hacim": qv[i] / med24,
                 "chg_6h": (c[i] / c[i - 6] - 1) * 100 if c[i - 6] else 0,
                 "chg_24h": (c[i] / c[i - 24] - 1) * 100 if c[i - 24] else 0,
                 "pos20": (c[i] - lo20) / (hi20 - lo20) if hi20 > lo20 else 0.5}
            for ad, fn in KOS.items():
                if fn is None:
                    continue
                if not fn(o):
                    continue
                if i - son_kayit[ad] < 24:      # ayni kurulumu tekrar sayma
                    continue
                son_kayit[ad] = i
                topla[ad].append((b, i, b[i]["t"]))
                if i + 24 < len(b):
                    fwd[ad].append(((c[i + 24] / c[i] - 1) * 100, b[i]["t"]))
        # kontrol
        for _ in range(max(3, len(b) // 200)):
            k = random.randint(200, len(b) - 80)
            topla["KONTROL (rastgele)"].append((b, k, b[k]["t"]))
            fwd["KONTROL (rastgele)"].append(((c[k + 24] / c[k] - 1) * 100, b[k]["t"]))

    tsl = sorted(t for v in topla.values() for _, _, t in v)
    ORTA = tsl[len(tsl) // 2]
    print("=" * 112)
    print("ÖNCESİ SİNYALİ PARA KAZANDIRIYOR MU? — LONG, botun A-stopu, maliyet %0.09")
    print("=" * 112)
    for hedef, ufuk in ((2.5, 24), (2.5, 72), (10.0, 72)):
        print(f"\n### hedef %{hedef} · ufuk {ufuk} saat")
        print(f"{'sinyal':26}{'N':>8}{'net %':>10}{'isabet':>9}{'basabas':>10}"
              f"{'A yari':>10}{'B yari':>10}")
        print("-" * 112)
        for ad in KOS:
            v = topla[ad]
            if len(v) < 100:
                continue
            k = [islem(bb, ii + 1, hedef, ufuk) for bb, ii, _ in v]
            a = oz(k, hedef)
            kA = oz([islem(bb, ii + 1, hedef, ufuk) for bb, ii, t in v if t < ORTA], hedef)
            kB = oz([islem(bb, ii + 1, hedef, ufuk) for bb, ii, t in v if t >= ORTA], hedef)
            if not a:
                continue
            im = " *" if a["ort"] > 0 else ""
            print(f"{ad:26}{a['n']:8d}{a['ort']:+10.2f}{a['isabet']:8.1f}%{a['basabas']:9.1f}%"
                  f"{(kA['ort'] if kA else 0):+10.2f}{(kB['ort'] if kB else 0):+10.2f}{im}")

    print("\n" + "=" * 112)
    print("HAM FORWARD GETİRİ (+24 saat, islemsiz) — sinyal sonrasi fiyat ne yapti?")
    print("=" * 112)
    print(f"{'sinyal':26}{'N':>8}{'medyan %':>11}{'ort %':>10}{'pozitif':>10}{'A yari':>10}{'B yari':>10}")
    print("-" * 112)
    for ad in KOS:
        v = [x for x, _ in fwd[ad]]
        if len(v) < 100:
            continue
        A = [x for x, t in fwd[ad] if t < ORTA]
        B = [x for x, t in fwd[ad] if t >= ORTA]
        print(f"{ad:26}{len(v):8d}{st.median(v):+11.2f}{st.mean(v):+10.2f}"
              f"{sum(1 for x in v if x > 0)/len(v)*100:9.0f}%"
              f"{(st.mean(A) if A else 0):+10.2f}{(st.mean(B) if B else 0):+10.2f}")


if __name__ == "__main__":
    main()
