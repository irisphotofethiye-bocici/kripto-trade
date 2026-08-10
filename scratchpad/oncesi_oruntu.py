#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HAREKET ÖNCESİ ÖRÜNTÜ (2026-08-10) — "yükselişten ÖNCE bir örüntü var mı?"

Onceki olcum tetik ANINDA bakti: tek ortak sinyal hacim patlamasi (4.3x, ayrim %81)
ama TAHMIN ETMIYOR (+24s medyan -2.62%, hacim arttikca kotulesiyor).
Bu script kalan tek yolu kapatir: hareketin BASLAMASINDAN ONCEKI pencere.

IKI AYRI SORU — ikisi de olculur, karistirilmaz:

  A) GERIYE BAKIS (recall): yukselenler, tetikten 1/3/6/12/24 saat ONCE
     kontrolden ayrisiyor mu? "Yukselenlerin oncesi farkli miydi?"

  B) ILERIYE BAKIS (precision): TUM barlar tarandi — bir ozellige sahip barlarin
     yuzde kaci sonraki 24 saatte +%10 tetigine yol acti? Taban oranla karsilastirilir.
     ASIL SORU BUDUR: A'da ayrisma olsa bile B'de taban orani gecmiyorsa
     sinyal KULLANILAMAZ (yukselenlerde sik ama HER YERDE sik demektir).

TETIK: 24h getiri ilk kez > %10 · evren: tum 570 perp, fiyat/hacim ·
46 gun, tek rejim (AYI/NOTR) · eslesmis kontrol (ayni sembol, ayni donem).
Zaman ikiye bolunerek dogrulanir; ayakta kalmayan TARAMA ARTIGIDIR.
"""
import json, os, random, statistics as st, collections

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h")
TETIK, DEDUP = 10.0, 72
GERI = (1, 3, 6, 12, 24)
random.seed(23)


def atr(b, i, n=14):
    if i < n:
        return None
    tr = []
    for j in range(i - n + 1, i + 1):
        p = b[j - 1]["c"]
        tr.append(max(b[j]["h"] - b[j]["l"], abs(b[j]["h"] - p), abs(p - b[j]["l"])))
    return st.mean(tr)


def olcu(b, i, qv, c):
    """Bar i'deki durum — hafif set (tum barlarda kosulacak)."""
    if i < 200 or i >= len(b):
        return None
    a = atr(b, i)
    px = c[i]
    if not a or a <= 0 or not px:
        return None
    a24 = atr(b, i - 24)
    med24 = st.median(qv[i - 23:i + 1]) or 1e-9
    med7g = st.median(qv[max(0, i - 167):i + 1]) or 1e-9
    hi20 = max(x["h"] for x in b[i - 19:i + 1]); lo20 = min(x["l"] for x in b[i - 19:i + 1])
    tr6 = st.mean([max(b[j]["h"] - b[j]["l"], abs(b[j]["h"] - b[j - 1]["c"]),
                       abs(b[j]["l"] - b[j - 1]["c"])) for j in range(i - 5, i + 1)])
    tbv = sum(x.get("tbv", 0.0) for x in b[i - 23:i + 1])
    q24 = sum(qv[i - 23:i + 1]) or 1e-9
    return {
        "hacim_kat_1h": qv[i] / med24,
        "hacim_kat_24h": (sum(qv[i - 23:i + 1]) / (sum(qv[i - 47:i - 23]) or 1e-9)),
        "hacim_kat_7g": med24 / med7g,
        "sikisma": tr6 / a,
        "atr_patlama": a / (a24 or a),
        "atr_pct": a / px * 100,
        "pos20": (px - lo20) / (hi20 - lo20) if hi20 > lo20 else 0.5,
        "chg_24h": (px / c[i - 24] - 1) * 100,
        "chg_6h": (px / c[i - 6] - 1) * 100,
        "taker_alis_pay": tbv / q24,
    }


ALAN = ["hacim_kat_1h", "hacim_kat_24h", "hacim_kat_7g", "sikisma", "atr_patlama",
        "atr_pct", "pos20", "chg_24h", "chg_6h", "taker_alis_pay"]


def main():
    dosyalar = sorted(f[:-5] for f in os.listdir(CACHE) if f.endswith(".json"))
    onceki = {g: [] for g in GERI}       # yukselenlerin g saat oncesi
    kontrol = {g: [] for g in GERI}
    # ileriye bakis icin: tum barlarin hafif olcusu + 24 saat icinde tetik var mi
    tum = []
    for sym in dosyalar:
        try:
            b = json.load(open(os.path.join(CACHE, f"{sym}.json")))
        except Exception:
            continue
        if len(b) < 400 or "qv" not in b[-1]:
            continue
        c = [x["c"] for x in b]
        qv = [x.get("qv", 0.0) for x in b]
        # tetikler
        son, tetikler = -999, []
        for i in range(200, len(b) - 2):
            if i - son < DEDUP:
                continue
            if not c[i - 24] or (c[i] / c[i - 24] - 1) * 100 < TETIK:
                continue
            son = i
            tetikler.append(i)
        tset = set(tetikler)
        # A) geriye bakis
        for i in tetikler:
            for g in GERI:
                o = olcu(b, i - g, qv, c)
                if o:
                    o["ts"] = b[i - g]["t"]
                    onceki[g].append(o)
            for g in GERI:
                for _ in range(6):
                    k = random.randint(200, len(b) - 30)
                    if abs(k - i) < 72:
                        continue
                    ok = olcu(b, k, qv, c)
                    if ok:
                        ok["ts"] = b[k]["t"]
                        kontrol[g].append(ok)
                        break
        # B) ileriye bakis — her 3 barda bir ornekle (hiz icin), sonraki 24 barda tetik var mi
        for i in range(200, len(b) - 30, 3):
            o = olcu(b, i, qv, c)
            if not o:
                continue
            o["tetik"] = any(j in tset for j in range(i + 1, i + 25))
            o["ts"] = b[i]["t"]
            tum.append(o)
    n_yuk = len(onceki[1])
    print("=" * 106)
    print("HAREKET ÖNCESİ ÖRÜNTÜ — yükselişten önce bir şey var mı?")
    print("=" * 106)
    print(f"Yukselis olayi: {n_yuk} · taranan bar: {len(tum)} · 46 gun, tek rejim\n")

    def dilim(v, p):
        v = sorted(v)
        return v[min(len(v) - 1, int(len(v) * p))]

    print("A) GERİYE BAKIŞ — yükselenlerin ÖNCESİ kontrolden ayrışıyor mu?")
    print("   (rastgele olsaydi %25 · deger = yukselenlerin kaci kontrolun ust ceyregi disinda)")
    print(f"\n{'olcu':18}" + "".join(f"{'-'+str(g)+'s':>10}" for g in GERI) + f"{'tetik ani':>11}")
    print("-" * 106)
    tetik_ani = {}
    for al in ALAN:
        hucre = []
        for g in GERI:
            y = [o[al] for o in onceki[g]]
            k = [o[al] for o in kontrol[g]]
            if len(y) < 50 or len(k) < 50:
                hucre.append("   –")
                continue
            ust, alt = dilim(k, 0.75), dilim(k, 0.25)
            p = max(sum(1 for x in y if x > ust) / len(y) * 100,
                    sum(1 for x in y if x < alt) / len(y) * 100)
            hucre.append(f"{p:.1f}")
        # tetik ani icin: g=0 hesapla
        print(f"{al:18}" + "".join(f"{h:>10}" for h in hucre))
    print("-" * 106)

    print("\nB) İLERİYE BAKIŞ — bu özelliğe sahip barların yüzde kaçı 24 saat içinde tetiğe yol açtı?")
    taban = sum(1 for o in tum if o["tetik"]) / len(tum) * 100
    tsl = sorted(o["ts"] for o in tum)
    ORTA = tsl[len(tsl) // 2]
    print(f"   TABAN ORAN: %{taban:.2f}  (rastgele bir bardan sonraki 24 saatte tetik olma olasiligi)")
    print(f"\n{'kosul':34}{'N':>9}{'tetik %':>10}{'KAT':>8}{'A yari':>9}{'B yari':>9}")
    print("-" * 106)
    KOS = [("hacim_kat_1h >= 3", lambda o: o["hacim_kat_1h"] >= 3),
           ("hacim_kat_1h >= 6", lambda o: o["hacim_kat_1h"] >= 6),
           ("hacim_kat_1h >= 10", lambda o: o["hacim_kat_1h"] >= 10),
           ("hacim_kat_24h >= 1.5", lambda o: o["hacim_kat_24h"] >= 1.5),
           ("hacim_kat_7g >= 1.5", lambda o: o["hacim_kat_7g"] >= 1.5),
           ("sikisma < 0.65 (sikisik)", lambda o: o["sikisma"] < 0.65),
           ("sikisma < 0.5", lambda o: o["sikisma"] < 0.5),
           ("atr_patlama >= 1.5", lambda o: o["atr_patlama"] >= 1.5),
           ("pos20 >= 0.85", lambda o: o["pos20"] >= 0.85),
           ("pos20 <= 0.15", lambda o: o["pos20"] <= 0.15),
           ("chg_24h 3..8 (usulca)", lambda o: 3 <= o["chg_24h"] < 8),
           ("chg_6h >= 3", lambda o: o["chg_6h"] >= 3),
           ("taker_alis_pay >= 4", lambda o: o["taker_alis_pay"] >= 4),
           ("hacim>=3 VE sikisma<0.65", lambda o: o["hacim_kat_1h"] >= 3 and o["sikisma"] < 0.65),
           ("hacim>=3 VE chg_6h>=3", lambda o: o["hacim_kat_1h"] >= 3 and o["chg_6h"] >= 3),
           ("hacim>=6 VE pos20>=0.85", lambda o: o["hacim_kat_1h"] >= 6 and o["pos20"] >= 0.85),
           ("hacim7g>=1.5 VE sikisma<0.65", lambda o: o["hacim_kat_7g"] >= 1.5 and o["sikisma"] < 0.65)]
    for ad, fn in KOS:
        alt = [o for o in tum if fn(o)]
        if len(alt) < 100:
            continue
        p = sum(1 for o in alt if o["tetik"]) / len(alt) * 100
        A = [o for o in alt if o["ts"] < ORTA]
        B = [o for o in alt if o["ts"] >= ORTA]
        pA = (sum(1 for o in A if o["tetik"]) / len(A) * 100) if A else 0
        pB = (sum(1 for o in B if o["tetik"]) / len(B) * 100) if B else 0
        print(f"{ad:34}{len(alt):9d}{p:9.2f}%{p/taban:8.2f}{pA:8.2f}%{pB:8.2f}%")
    print("-" * 106)
    print("  KAT = tetik orani / taban oran. 1.00 = hicbir bilgi. 2.00 = iki kat olasilik.")


if __name__ == "__main__":
    main()
