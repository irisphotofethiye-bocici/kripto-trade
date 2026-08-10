#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SKOR HOLDOUT (2026-08-10) — alternatif skorun DURUST testi.

skor_ayristirma.py'de alternatif skorun agirliklari TUM veriden turetildi (ornek-ici).
Bu, "iyi gorunmesi zorunlu" bir kurulumdur. Burada ayrim yapiliyor:

    Agirliklar YALNIZ A yarisindan turetilir  ->  YALNIZ B yarisinda test edilir
    Sonra tersi (B'den turet, A'da test).

Boylece test verisi agirliklari hic gormemis olur. Ek olarak KONTROL:
rastgele agirliklar ayni yordamla test edilir (tesaduf payi).

ON-KAYIT: tek varyant. Agirlik = ust ceyrek/alt ceyrek R farki (negatifse 0).
Funding ISARETLI (abs degil). Hicbir esik aranmayacak.
"""
import json, os, random, statistics as st

BURA = os.path.dirname(os.path.abspath(__file__))
ol = json.load(open(os.path.join(BURA, "oruntu_olaylar.json")))
tsl = sorted(o["ts"] for o in ol)
ORTA = tsl[len(tsl) // 2]
random.seed(7)


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def parcala(o):
    oi24 = o.get("oi24") or 0.0
    oi3 = o.get("oi3") or 0.0
    f = o.get("funding")
    comp = o.get("comp")
    vol_x = o.get("vol_x") or 0.0
    pos = o.get("pos")
    last1 = o.get("last1") or 0.0
    if comp is None or pos is None:
        return None
    return {
        "oi":   (clamp(oi24 / 20) * 25 + clamp(oi3 / 8) * 10) / 35 * 100,
        "fund": clamp(-(f or 0.0) / 0.05) * 100,      # ISARETLI: negatif derinlik odullenir
        "comp": clamp((0.8 - comp) / 0.5) * 100,
        "vol":  clamp((vol_x - 1.5) / 3) * 100,
        "brk":  (clamp((pos - 0.7) / 0.3) * 10 + clamp(last1 / 4) * 5) / 15 * 100,
    }


for o in ol:
    p = parcala(o)
    if p:
        o["_p"] = p
ge = [o for o in ol if "_p" in o and o.get("R_short") is not None]
A = [o for o in ge if o["ts"] < ORTA]
B = [o for o in ge if o["ts"] >= ORTA]
ANAHTAR = ["oi", "fund", "comp", "vol", "brk"]


def agirlik_turet(kume):
    ag = {}
    for k in ANAHTAR:
        v = sorted(o["_p"][k] for o in kume)
        ue, ae = v[int(len(v) * 0.75)], v[int(len(v) * 0.25)]
        ust = [o["R_short"] for o in kume if o["_p"][k] >= ue]
        alt = [o["R_short"] for o in kume if o["_p"][k] <= ae]
        ag[k] = max(0.0, st.mean(ust) - st.mean(alt)) if ust and alt else 0.0
    tp = sum(ag.values()) or 1.0
    return {k: v / tp for k, v in ag.items()}


def skorla(o, ag):
    return sum(o["_p"][k] * ag[k] for k in ANAHTAR)


def ust_dilim_R(kume, anahtar_fn, dilim=0.90):
    v = sorted(anahtar_fn(o) for o in kume)
    esik = v[int(len(v) * dilim)]
    rs = [o["R_short"] for o in kume if anahtar_fn(o) >= esik]
    return {"n": len(rs), "ort": st.mean(rs),
            "sh": st.pstdev(rs) / len(rs) ** 0.5 if len(rs) > 1 else 0}


print("=" * 92)
print("SKOR HOLDOUT — agirliklar bir yaridan, test oteki yarida")
print("=" * 92)
print(f"A yarisi: {len(A)} olay (-> {ORTA})   |   B yarisi: {len(B)} olay ({ORTA} ->)")

for ad_egit, egit, ad_test, test in (("A", A, "B", B), ("B", B, "A", A)):
    ag = agirlik_turet(egit)
    print(f"\n--- Agirliklar {ad_egit} yarisindan turetildi, {ad_test} yarisinda test edildi ---")
    print("    agirlik: " + " · ".join(f"{k} %{ag[k]*100:.0f}" for k in ANAHTAR))
    mevcut = ust_dilim_R(test, lambda o: o["score"])
    yeni = ust_dilim_R(test, lambda o: skorla(o, ag))
    # kontrol: rastgele agirliklar (10 deneme ortalamasi)
    rast = []
    for _ in range(10):
        ra = {k: random.random() for k in ANAHTAR}
        s = sum(ra.values())
        ra = {k: v / s for k, v in ra.items()}
        rast.append(ust_dilim_R(test, lambda o, ra=ra: skorla(o, ra))["ort"])
    print(f"    {ad_test} yarisi ust %10:")
    print(f"      MEVCUT skor       R {mevcut['ort']:+.3f} ±{mevcut['sh']:.3f}  (N={mevcut['n']})")
    print(f"      ALTERNATIF skor   R {yeni['ort']:+.3f} ±{yeni['sh']:.3f}  (N={yeni['n']})")
    print(f"      KONTROL (rastgele agirlik, 10 deneme ort) R {st.mean(rast):+.3f}"
          f"  [aralik {min(rast):+.3f} .. {max(rast):+.3f}]")

print("\n" + "=" * 92)
print("TEK DEGISIKLIK TESTI — sadece funding'i ISARETLI yapmak ne kazandirir?")
print("=" * 92)
print("Mevcut formulun TEK farkla kopyasi: abs(funding) yerine isaretli negatif derinlik.")


def mevcut_gibi(o, isaretli):
    p = o["_p"]
    f = o.get("funding") or 0.0
    fund = (clamp(-f / 0.05) * 100) if isaretli else (clamp(abs(f) / 0.05) * 100)
    return (p["oi"] * 35 + fund * 15 / 100 * 100 * 0.15 * 100 / 100 * 0 + fund * 0.15 * 100 / 100
            + p["comp"] * 0.20 + p["vol"] * 0.20 + p["brk"] * 0.15) if False else (
        p["oi"] / 100 * 35 + fund / 100 * 15 + p["comp"] / 100 * 20
        + p["vol"] / 100 * 20 + p["brk"] / 100 * 15)


for ad, isaretli in (("mevcut (abs funding)", False), ("tek degisiklik (isaretli funding)", True)):
    for yad, ykume in (("A", A), ("B", B)):
        r = ust_dilim_R(ykume, lambda o, i=isaretli: mevcut_gibi(o, i))
        print(f"  {ad:36} {yad} yarisi ust %10:  R {r['ort']:+.3f} ±{r['sh']:.3f} (N={r['n']})")
