#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GAINER'A BİNME TESTİ (2026-08-10) — "gorseydik binebilir miydik?"

KAPSAMA OLCUMU SONUCU: 46 gunde 24h'te >%50 yukselen 117 sembolun yalniz 13'unu (%11)
radar hareketten ONCEKI 24 saatte kaydetmis; skor>=45 olan 6 (%5). Yani mevcut boru
hatti buyuk hareketleri GORMUYOR.

Bu script bir sonraki soruyu cevaplar: GORSEYDIK NE OLURDU?
Radar filtresi TAMAMEN devre disi — TUM 526 USDT perp taranir, radar'in evreni degil.

TETIK (sabit, sonuca bakilmadan secildi): 24 saatlik getiri ilk kez +%15'i astigi bar.
  Ayni sembolde 72 saat dedup (ayni hareketi tekrar saymamak icin).

VARYANTLAR (hepsi botun AYNI mekanigi: A-stop, 2R hedef, 72s ufuk, fitil, maliyet 0.04R):
  L0   LONG hemen (tetik barinin ertesi acilisi)          = "binmek"
  L6   LONG 6 saat sonra                                   = "geri cekilmeyi bekle"
  L12  LONG 12 saat sonra
  L24  LONG 24 saat sonra
  S0   SHORT hemen                                          = "fade" (botun bugunku isi)
  S6   SHORT 6 saat sonra                                   = botun ONAY_BEKLE'sinin genisi

KIRILIM: hareketin buyuklugune gore (15-30 / 30-50 / 50-100 / 100+) ve zaman ikiye bolerek.
"""
import json, os, statistics as st, collections, datetime

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h")
UFUK, NBAR, MALIYET = 72, 10, 0.04
TETIK_PCT, DEDUP_BAR = 15.0, 72


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


def oyna(b, gi, yon):
    """Botun mekanigi. -> R (maliyet dusulmus) | None"""
    i = gi - 1
    if i < 30 or gi >= len(b):
        return None
    a = atr14(b, i)
    if not a or a <= 0:
        return None
    ref = b[gi]["o"]
    hi, lo = swings(b, i)
    res = min([x for x in hi if x > ref], default=None)
    sup = max([x for x in lo if x < ref], default=None)
    ad = []
    if yon == "LONG":
        if sup is not None and (ref - sup) <= 3 * a:
            ad.append(sup - 0.25 * a)
        nb = min(x["l"] for x in b[max(0, i - NBAR + 1):i + 1])
        if nb < ref:
            ad.append(nb - 0.25 * a)
        ad.append(ref - 1.5 * a)
        gec = [s for s in ad if s < ref]
        stop = max(gec) if gec else ref - 1.5 * a
        risk = ref - stop
        hedef = ref + 2 * risk
    else:
        if res is not None and (res - ref) <= 3 * a:
            ad.append(res + 0.25 * a)
        nb = max(x["h"] for x in b[max(0, i - NBAR + 1):i + 1])
        if nb > ref:
            ad.append(nb + 0.25 * a)
        ad.append(ref + 1.5 * a)
        gec = [s for s in ad if s > ref]
        stop = min(gec) if gec else ref + 1.5 * a
        risk = stop - ref
        hedef = ref - 2 * risk
    if risk <= 0:
        return None
    son = min(gi + UFUK, len(b))
    if son - gi < 6:
        return None
    for j in range(gi, son):
        x = b[j]
        if yon == "LONG":
            if x["l"] <= stop:
                return -1.0 - MALIYET
            if x["h"] >= hedef:
                return 2.0 - MALIYET
        else:
            if x["h"] >= stop:
                return -1.0 - MALIYET
            if x["l"] <= hedef:
                return 2.0 - MALIYET
    c = b[son - 1]["c"]
    ham = (c - ref) / risk if yon == "LONG" else (ref - c) / risk
    return ham - MALIYET


def oz(rs):
    rs = [r for r in rs if r is not None]
    if not rs:
        return None
    return {"n": len(rs), "ort": st.mean(rs),
            "sh": st.pstdev(rs) / len(rs) ** 0.5 if len(rs) > 1 else 0,
            "hedef": sum(1 for r in rs if r > 1.5) / len(rs) * 100}


def main():
    dosyalar = [f[:-5] for f in os.listdir(CACHE) if f.endswith(".json")]
    print(f"TUM EVREN: {len(dosyalar)} sembol (radar filtresi YOK)")
    olaylar = []
    for sym in dosyalar:
        try:
            b = json.load(open(os.path.join(CACHE, f"{sym}.json")))
        except Exception:
            continue
        if len(b) < 150:
            continue
        son_tetik = -999
        for i in range(24, len(b) - 30):
            if i - son_tetik < DEDUP_BAR:
                continue
            onceki = b[i - 24]["c"]
            if not onceki:
                continue
            r24 = (b[i]["c"] / onceki - 1) * 100
            if r24 < TETIK_PCT:
                continue
            son_tetik = i
            o = {"sym": sym, "i": i, "ts": b[i]["t"], "r24": r24}
            for ad, gecikme, yon in (("L0", 0, "LONG"), ("L6", 6, "LONG"), ("L12", 12, "LONG"),
                                     ("L24", 24, "LONG"), ("S0", 0, "SHORT"), ("S6", 6, "SHORT")):
                o[ad] = oyna(b, i + 1 + gecikme, yon)
            olaylar.append(o)
    print(f"TETIK: 24h getiri ilk kez >%{TETIK_PCT:.0f} (72 bar dedup) -> {len(olaylar)} olay\n")

    tsl = sorted(o["ts"] for o in olaylar)
    ORTA = tsl[len(tsl) // 2]
    VAR = [("L0", "LONG hemen (BIN)"), ("L6", "LONG +6s"), ("L12", "LONG +12s"),
           ("L24", "LONG +24s"), ("S0", "SHORT hemen (FADE)"), ("S6", "SHORT +6s")]

    print("=" * 104)
    print("1) TUM TETIKLER")
    print("=" * 104)
    print(f"{'varyant':22}{'N':>7}{'ort R':>10}{'hedefe %':>10}{'A yarisi':>11}{'B yarisi':>11}")
    print("-" * 104)
    for k, ad in VAR:
        a = oz([o[k] for o in olaylar])
        A = oz([o[k] for o in olaylar if o["ts"] < ORTA])
        B = oz([o[k] for o in olaylar if o["ts"] >= ORTA])
        if not a:
            continue
        print(f"{ad:22}{a['n']:7d}{a['ort']:+10.3f}{a['hedef']:9.0f}%"
              f"{(A['ort'] if A else 0):+11.3f}{(B['ort'] if B else 0):+11.3f}")

    print("\n" + "=" * 104)
    print("2) HAREKET BUYUKLUGUNE GORE")
    print("=" * 104)
    for a, b_ in ((15, 30), (30, 50), (50, 100), (100, 9999)):
        alt = [o for o in olaylar if a <= o["r24"] < b_]
        if len(alt) < 20:
            continue
        print(f"\n  24h hareketi %{a}-{b_ if b_ < 9999 else '+'} (N={len(alt)}):")
        for k, ad in VAR:
            x = oz([o[k] for o in alt])
            if x:
                print(f"     {ad:22} ort R {x['ort']:+.3f} ±{x['sh']:.3f}  hedefe %{x['hedef']:.0f}")

    print("\n" + "=" * 104)
    print("3) EN IYI VARYANTIN KARNESI (dolar cinsinden kaba tahmin)")
    print("=" * 104)
    en_iyi = max(VAR, key=lambda v: (oz([o[v[0]] for o in olaylar]) or {"ort": -9})["ort"])
    x = oz([o[en_iyi[0]] for o in olaylar])
    print(f"  En iyi varyant: {en_iyi[1]}  ort R {x['ort']:+.3f}  N={x['n']} / 46 gun")
    print(f"  Gunde {x['n']/46:.1f} tetik · islem basi %3 risk · 8 es zamanli pozisyon tavani")
    print(f"  Kaba beklenti: gunde {x['n']/46:.1f} x {x['ort']:+.3f}R x %3 = "
          f"%{x['n']/46*x['ort']*3:+.2f}/gun (tavansiz, kaba)")

    json.dump(olaylar, open(os.path.join(BURA, "gainer_olaylar.json"), "w"))
    print("\n-> scratchpad/gainer_olaylar.json")


if __name__ == "__main__":
    main()
