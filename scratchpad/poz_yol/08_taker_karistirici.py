#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KARISTIRICI TESTI — taker_pay'in yon bilgisi FIYATIN GOLGESI mi?

07_hacim_yon.py'de cikan:
   hacim_x  : YUKARI ile ASAGI'yi AYIRMIYOR (BTC p=0,43 · ETH p=0,93)   -> yon YOK
   taker_pay: AYIRIYOR, iki enstrumanda AYNI isaret, p tabanda           -> ??
   d_fiyat  : DE AYIRIYOR ve cok daha buyuk  (BTC -0,078 · ETH -0,109)

SUPHE: pencere-ici fiyat yukselmisse taker alis payi da yuksektir (mekanik
bagimlilik). Ve 30 dk olceginde fiyat ORTALAMAYA DONUYOR -> yukselmis olan
sonra duser. O zaman "taker_pay yonu haber veriyor" cumlesi YANLIS olur;
olculen sey yalnizca FIYATIN KENDI GERI DONUSUDUR.

Bu proje bu hatayi IKI KEZ yasadi: agresor dengesi (2026-08-17) ve son-yeni-uc
(2026-08-19). Ikisi de kapilari gecti, karistirici sabitlenince coktu.

TEST: d_fiyat dilimlere bolunur. taker_pay HER DILIM ICINDE de ayiriyor mu?
   ayiriyorsa  -> bagimsiz bilgi
   ayirmiyorsa -> fiyatin golgesi, HUKUM YAZILMAZ

SALT OKUMA.
"""
import os, json, datetime, random, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
VERI = os.path.join(os.path.dirname(HERE), "major_5dk")
random.seed(53)
ATR_N, OLAY_BAR, KAT, ONCE, AYIRMA = 14, 6, 2.0, 12, 12


def yukle(s):
    with open(os.path.join(VERI, "%s.json" % s), encoding="utf-8") as f:
        return json.load(f)


def topla(sym):
    b = yukle(sym)
    atr, tr = [None] * len(b), []
    for i in range(1, len(b)):
        tr.append(max(b[i]["h"] - b[i]["l"], abs(b[i]["h"] - b[i - 1]["c"]),
                      abs(b[i]["l"] - b[i - 1]["c"])))
        if len(tr) >= ATR_N and b[i]["c"]:
            atr[i] = (sum(tr[-ATR_N:]) / ATR_N) / b[i]["c"] * 100
    yuk, asg = [], []
    i = 2 * ONCE + 1
    while i < len(b) - OLAY_BAR - 1:
        if atr[i] and atr[i] > 0 and b[i]["c"]:
            g = (b[i + OLAY_BAR]["c"] - b[i]["c"]) / b[i]["c"] * 100
            if abs(g) >= KAT * atr[i]:
                j = i - ONCE
                qv = sum(b[k]["qv"] for k in range(j + 1, i + 1))
                tqv = sum(b[k]["tqv"] for k in range(j + 1, i + 1))
                if qv > 0 and b[j]["c"]:
                    o = {"taker_pay": tqv / qv,
                         "d_fiyat": (b[i]["c"] - b[j]["c"]) / b[j]["c"] * 100,
                         "ay": datetime.datetime.fromtimestamp(b[i]["t"] / 1000).strftime("%Y-%m")}
                    (yuk if g > 0 else asg).append(o)
                i += AYIRMA
                continue
        i += 1
    return yuk, asg


BANT = [(-99, -0.30, "d_fiyat < -0,30%"), (-0.30, -0.10, "-0,30..-0,10"),
        (-0.10, 0.10, "-0,10..+0,10"), (0.10, 0.30, "+0,10..+0,30"),
        (0.30, 99, "> +0,30%")]

if __name__ == "__main__":
    print("KARISTIRICI: taker_pay'in yon ayrimi, d_fiyat sabitlenince duruyor mu?")
    for sym in ("BTC", "ETH"):
        yuk, asg = topla(sym)
        print("\n" + "=" * 78)
        print("%s   yukari %d · asagi %d" % (sym, len(yuk), len(asg)))
        print("=" * 78)
        ham = sx.median([z["taker_pay"] for z in yuk]) - sx.median([z["taker_pay"] for z in asg])
        print("HAM fark (yukari - asagi): %+.5f" % ham)
        print("\n%-18s %10s %10s %11s %12s" % ("d_fiyat bandi", "YUKARI", "ASAGI", "fark", "N (yuk/asg)"))
        print("-" * 66)
        isaretler = []
        for lo, hi, et in BANT:
            y = [z["taker_pay"] for z in yuk if lo <= z["d_fiyat"] < hi]
            s = [z["taker_pay"] for z in asg if lo <= z["d_fiyat"] < hi]
            if len(y) < 50 or len(s) < 50:
                print("%-18s %10s %10s %11s %12s" % (et, "-", "-", "-", "%d/%d" % (len(y), len(s))))
                continue
            f = sx.median(y) - sx.median(s)
            isaretler.append(f)
            print("%-18s %10.5f %10.5f %+11.5f %12s"
                  % (et, sx.median(y), sx.median(s), f, "%d/%d" % (len(y), len(s))))
        if isaretler:
            ayni = sum(1 for f in isaretler if f * ham > 0)
            kucuk = sx.median([abs(f) for f in isaretler])
            print("\n  HAM isaretle ayni yonde: %d/%d bant" % (ayni, len(isaretler)))
            print("  bant-ici medyan |fark| : %.5f   (ham |fark| %.5f)" % (kucuk, abs(ham)))
            print("  -> %s" % ("bagimsiz bilgi olabilir" if ayni == len(isaretler) and kucuk > abs(ham) * 0.5
                               else "FIYATIN GOLGESI -- bant icinde ayrim COKUYOR"))
    print("\nbot dosyalarina yazim: YOK")
