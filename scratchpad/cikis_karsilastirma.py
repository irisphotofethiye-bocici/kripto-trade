#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ÇIKIŞ KARŞILAŞTIRMASI (2026-08-10) — botun 10 gercek islemi, 3 farkli cikis kuraliyla.

BULGU (once): 10 pozisyonun 10'u da STOP ile kapandi, TP2'ye HIC ulasilmadi.
  Gerceklesen R: kazananlar ort +0.62 (0.01..1.65), kaybedenler ort -1.03.
  Yani kayiplar TAM, kazanclar KIRPIK -> basabas kazanma orani %62 gerekiyor, fiili %40.

SORU: kirpma nereden geliyor — GIRIS secimi mi, CIKIS mekanigi mi?
YONTEM: ayni girisler (gercek giris fiyati + gercek stop), uc cikis kurali:
  A) SAF 2R      : stop | 2R hedef | 48s zaman stopu   (trailing YOK, kismi YOK)
  B) SAF 1.5R    : stop | 1.5R hedef | 48s
  C) GERCEK      : defterdeki fiili sonuc (trailing + kismi TP1)
1 dakikalik mum YOK -> 1h fitil bazli; ayni gun ikisi de -> STOP (muhafazakar).
"""
import json, os, sys, collections, datetime, statistics as st

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "klines_1h")


def bars(sym):
    p = os.path.join(CACHE, f"{sym}.json")
    return json.load(open(p)) if os.path.exists(p) else None


def sim(b, giris_ms, giris, stop, yon, hedef_r, saat=48):
    risk = abs(giris - stop)
    hedef = giris + hedef_r * risk if yon == "LONG" else giris - hedef_r * risk
    i0 = next((i for i, x in enumerate(b) if x["t"] >= giris_ms), None)
    if i0 is None:
        return None
    for j in range(i0, min(i0 + saat, len(b))):
        x = b[j]
        if yon == "LONG":
            if x["l"] <= stop:
                return -1.0
            if x["h"] >= hedef:
                return hedef_r
        else:
            if x["h"] >= stop:
                return -1.0
            if x["l"] <= hedef:
                return hedef_r
    son = b[min(i0 + saat, len(b)) - 1]["c"]
    return (son - giris) / risk if yon == "LONG" else (giris - son) / risk


def main():
    isl = [json.loads(l) for l in open(os.path.join(HERE, "testbot_islemler.jsonl"),
                                       encoding="utf-8") if l.strip()]
    poz = collections.defaultdict(list)
    for t in isl:
        poz[t["id"]].append(t)

    print("=" * 82)
    print("ÇIKIŞ KARŞILAŞTIRMASI — ayni girisler, uc farkli cikis kurali")
    print("=" * 82)
    print(f"{'sym':8}{'yon':6}{'stop%':>7}{'SAF 2R':>9}{'SAF 1.5R':>10}{'GERCEK':>9}")
    A, B, C = [], [], []
    for i, ts in sorted(poz.items()):
        tam = [x for x in ts if not x.get("kismi")][0]
        a = ts[0]
        risk_usd = abs(tam["sonuc_usdt"] / tam["r"]) if tam.get("r") else None
        if not risk_usd or not a.get("notional"):
            continue
        stop_frac = risk_usd / a["notional"]
        giris = a["giris"]
        stop = giris * (1 + stop_frac) if a["yon"] == "SHORT" else giris * (1 - stop_frac)
        net = sum(x["sonuc_usdt"] for x in ts)
        gercek = net / risk_usd
        bb = bars(a["sym"])
        if not bb:
            print(f"{a['sym']:8}{a['yon']:6}{stop_frac*100:7.2f}   (mum verisi yok)")
            continue
        gms = int(datetime.datetime.strptime(tam["ts"], "%Y-%m-%d %H:%M:%S").astimezone().timestamp() * 1000) \
            - int((tam.get("tutma_saat") or 0) * 3600000)
        r2 = sim(bb, gms, giris, stop, a["yon"], 2.0)
        r15 = sim(bb, gms, giris, stop, a["yon"], 1.5)
        if r2 is None:
            continue
        A.append(r2); B.append(r15); C.append(gercek)
        print(f"{a['sym']:8}{a['yon']:6}{stop_frac*100:7.2f}{r2:9.2f}{r15:10.2f}{gercek:9.2f}")

    print("-" * 82)
    for ad, v in (("SAF 2R (trailing/kismi YOK)", A), ("SAF 1.5R", B), ("GERCEK (trailing+kismi)", C)):
        kaz = [x for x in v if x > 0]
        print(f"  {ad:32} ort R {st.mean(v):+.3f} | toplam {sum(v):+.2f}R | kazanma %{len(kaz)/len(v)*100:.0f}")
    print("\nNOT: 1h fitil bazli; bot 1dk mumla yonetiyor -> GERCEK sutunu daha hassas.")
    print("Ayni barda stop+hedef -> STOP sayildi (muhafazakar).")


if __name__ == "__main__":
    main()
