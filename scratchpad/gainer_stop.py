#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GAINER STOP TESTİ (2026-08-10) — "giris mi yanlis, STOP mu?"

ONCEKI SONUC: 570 sembol / 1422 tetik (24h getiri ilk kez >%15). Her varyant negatif —
LONG hemen -0.100R, SHORT hemen -0.084R. Yani "gorseydik binerdik" hipotezi tutmadi.

AMA BIR MEKANIZMA SUPHESI VAR: bir coin %15+ pump'ladiginda ATR patlar. Botun A-stopu
"girise EN YAKIN" adayi secer — patlamis oynaklikta bu stop, gunluk gurultunun icinde
kalir. Yani giris yonu dogru olsa bile stop once yenir.

TEST (on-kayitli, 4 SABIT stop genisligi, arama YOK):
  A     : botun mevcut A-varyanti (girise en yakin aday)
  1.5x  : sabit 1.5 x ATR14      (olcucunun fallback'i)
  2.5x  : sabit 2.5 x ATR14
  4.0x  : sabit 4.0 x ATR14
Hedef her zaman 2 x risk (yani stop genisledikce hedef de uzar — R olcegi korunur).
Ayrica MFE/MAE olculur: "fiyat lehimize ne kadar gitti, stopa ne kadar yaklasti."

BU AYRIMIN ANLAMI:
  Genis stop R'yi POZITIFE cevirirse -> giris dogru, STOP yanlis (aksiyon alinabilir).
  Genis stop da negatifse            -> giris yanlis, stop degistirmek kurtarmaz.
"""
import json, os, statistics as st

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h")
UFUK, NBAR, MALIYET = 72, 10, 0.04


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


def kur(b, gi, yon, mod):
    i = gi - 1
    a = atr14(b, i)
    if not a or a <= 0 or gi >= len(b):
        return None
    ref = b[gi]["o"]
    if mod != "A":
        kat = float(mod)
        stop = ref - kat * a if yon == "LONG" else ref + kat * a
    else:
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
    risk = abs(ref - stop)
    if risk <= 0:
        return None
    hedef = ref + 2 * risk if yon == "LONG" else ref - 2 * risk
    return ref, stop, hedef, risk, a


def oyna(b, gi, yon, mod):
    k = kur(b, gi, yon, mod)
    if not k:
        return None
    ref, stop, hedef, risk, a = k
    son = min(gi + UFUK, len(b))
    if son - gi < 6:
        return None
    mfe = mae = 0.0
    for j in range(gi, son):
        x = b[j]
        if yon == "LONG":
            mfe = max(mfe, (x["h"] - ref) / risk)
            mae = max(mae, (ref - x["l"]) / risk)
            if x["l"] <= stop:
                return -1.0 - MALIYET, mfe, mae, risk / ref * 100
            if x["h"] >= hedef:
                return 2.0 - MALIYET, mfe, mae, risk / ref * 100
        else:
            mfe = max(mfe, (ref - x["l"]) / risk)
            mae = max(mae, (x["h"] - ref) / risk)
            if x["h"] >= stop:
                return -1.0 - MALIYET, mfe, mae, risk / ref * 100
            if x["l"] <= hedef:
                return 2.0 - MALIYET, mfe, mae, risk / ref * 100
    c = b[son - 1]["c"]
    ham = (c - ref) / risk if yon == "LONG" else (ref - c) / risk
    return ham - MALIYET, mfe, mae, risk / ref * 100


def oz(rs):
    rs = [r for r in rs if r is not None]
    if not rs:
        return None
    return {"n": len(rs), "ort": st.mean(rs),
            "sh": st.pstdev(rs) / len(rs) ** 0.5 if len(rs) > 1 else 0,
            "hedef": sum(1 for r in rs if r > 1.5) / len(rs) * 100}


def main():
    olaylar = json.load(open(os.path.join(BURA, "gainer_olaylar.json")))
    print(f"Tetik olayi: {len(olaylar)}  (24h getiri ilk kez >%15, 570 sembol, 46 gun)\n")
    bcache = {}
    MODLAR = [("A", "A-stop (botun mevcut)"), ("1.5", "sabit 1.5x ATR"),
              ("2.5", "sabit 2.5x ATR"), ("4.0", "sabit 4.0x ATR")]
    sonuc = {(m, y): [] for m, _ in MODLAR for y in ("LONG", "SHORT")}
    mfe_l, mae_l, stopf = [], [], {m: [] for m, _ in MODLAR}
    for o in olaylar:
        sym = o["sym"]
        if sym not in bcache:
            try:
                bcache[sym] = json.load(open(os.path.join(CACHE, f"{sym}.json")))
            except Exception:
                bcache[sym] = None
        b = bcache[sym]
        if not b:
            continue
        gi = o["i"] + 1
        for m, _ in MODLAR:
            for y in ("LONG", "SHORT"):
                r = oyna(b, gi, y, m)
                if r:
                    sonuc[(m, y)].append(r[0])
                    if m == "A" and y == "LONG":
                        mfe_l.append(r[1]); mae_l.append(r[2])
                    if y == "LONG":
                        stopf[m].append(r[3])

    print("=" * 96)
    print("STOP GENISLIGI — pump'a giriste (hedef her zaman 2xrisk)")
    print("=" * 96)
    print(f"{'stop':26}{'stop mesafesi %':>17}{'LONG ort R':>13}{'SHORT ort R':>14}{'LONG hedefe %':>15}")
    print("-" * 96)
    for m, ad in MODLAR:
        L, S = oz(sonuc[(m, "LONG")]), oz(sonuc[(m, "SHORT")])
        sm = st.median(stopf[m]) if stopf[m] else 0
        print(f"{ad:26}{sm:16.2f}%{L['ort']:+13.3f}{S['ort']:+14.3f}{L['hedef']:14.0f}%")

    print("\n" + "=" * 96)
    print("YOL ANALIZI — A-stop / LONG (fiyat lehimize ne kadar gitti?)")
    print("=" * 96)
    print(f"  MFE (en fazla lehte gidis) : medyan {st.median(mfe_l):.2f}R · "
          f"ort {st.mean(mfe_l):.2f}R · %75 dilim {sorted(mfe_l)[int(len(mfe_l)*0.75)]:.2f}R")
    print(f"  MAE (en fazla aleyhte)     : medyan {st.median(mae_l):.2f}R · "
          f"ort {st.mean(mae_l):.2f}R")
    ge2 = sum(1 for x in mfe_l if x >= 2.0) / len(mfe_l) * 100
    ge1 = sum(1 for x in mfe_l if x >= 1.0) / len(mfe_l) * 100
    print(f"  MFE >= 2R olan olay: %{ge2:.0f}   ·   MFE >= 1R olan: %{ge1:.0f}")
    print("\n  OKUMA: MFE medyani 2R'nin ALTINDAysa fiyat zaten hedefe gitmiyor")
    print("         -> stop degil GIRIS sorunlu. Ustundeyse stop erken yiyor.")


if __name__ == "__main__":
    main()
