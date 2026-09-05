#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EMIR DEFTERI GECMISI GERCEKTEN YOK MU? — YOKLAMA (2026-09-05)

Kullanici: "emir defterinde sinyal bulabilir miyiz?"

Proje kaydi: "emir defteri gecmisi YOK -> yalniz ileriye" (olcumler.md:1190).
Bu yoklama o hukmu DOGRUDAN sinar, cunku eger yanlissa cevap tamamen degisir:
geriye test edilebilir bir emir defteri sinyali, bu projede simdiye kadar
bulunamamis seyin ta kendisi olurdu.

Binance ARSIV SITESI (data.binance.vision) gunluk dosyalar yayinliyor olabilir:
   bookTicker : en iyi alis/satis + MIKTARLARI  -> en basit dengesizlik olcusu
   bookDepth  : yuzde seviyelerinde toplam derinlik anlik goruntuleri
   metrics    : bazi turev oranlari
Bunlar VARSA emir defteri dengesizligi 2 yil geriye olculebilir.

Salt-okunur. Indirme YOK — yalnizca varlik ve BOYUT kontrolu (HEAD).
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import urllib.request, urllib.error, datetime, xml.etree.ElementTree as ET

TABAN = "https://data.binance.vision"
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"


def var_mi(yol):
    """HEAD ile varlik + boyut. -> (var_mi, boyut_bayt)"""
    url = TABAN + "/" + yol.lstrip("/")
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return True, int(r.headers.get("Content-Length") or 0)
    except urllib.error.HTTPError as e:
        return False, e.code
    except Exception as e:
        return False, str(e)[:40]


def listele(onek, maks=20):
    """S3 listeleme — hangi veri turleri var?"""
    url = "%s?delimiter=/&prefix=%s" % (S3, onek)
    try:
        with urllib.request.urlopen(url, timeout=25) as r:
            kok = ET.fromstring(r.read())
    except Exception as e:
        return ["HATA: %s" % str(e)[:60]]
    ns = "{http://s3.amazonaws.com/doc/2006-03-01/}"
    out = [p.find(ns + "Prefix").text for p in kok.findall(ns + "CommonPrefixes")]
    return out[:maks]


def mb(b):
    return "%.1f MB" % (b / 1048576.0) if isinstance(b, int) else str(b)


def main():
    print("=" * 92)
    print("EMIR DEFTERI GECMISI GERCEKTEN YOK MU?")
    print("=" * 92)
    print("Proje kaydi: 'emir defteri gecmisi YOK -> yalniz ileriye'")
    print("Bu yoklama o hukmu dogrudan sinar. Indirme YOK, yalniz varlik+boyut.")
    print()

    print("### 1) USD-M FUTURES gunluk veri turleri")
    turler = listele("data/futures/um/daily/")
    for t in turler:
        print("   %s" % t)
    print()

    print("### 2) AYLIK veri turleri (daha buyuk pencere)")
    for t in listele("data/futures/um/monthly/"):
        print("   %s" % t)
    print()

    # gecmis bir gun sec (dun degil, kesin yayinlanmis olsun)
    gun = (datetime.datetime.utcnow() - datetime.timedelta(days=10)).strftime("%Y-%m-%d")
    ay = (datetime.datetime.utcnow() - datetime.timedelta(days=45)).strftime("%Y-%m")
    print("### 3) DOSYA VARLIGI ve BOYUTU  (ornek gun %s · ay %s)" % (gun, ay))
    print("   %-46s %-8s %s" % ("yol", "var mi", "boyut"))
    denemeler = [
        "data/futures/um/daily/bookTicker/BTCUSDT/BTCUSDT-bookTicker-%s.zip" % gun,
        "data/futures/um/daily/bookDepth/BTCUSDT/BTCUSDT-bookDepth-%s.zip" % gun,
        "data/futures/um/daily/metrics/BTCUSDT/BTCUSDT-metrics-%s.zip" % gun,
        "data/futures/um/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-%s.zip" % gun,
        "data/futures/um/monthly/bookTicker/BTCUSDT/BTCUSDT-bookTicker-%s.zip" % ay,
        "data/futures/um/monthly/bookDepth/BTCUSDT/BTCUSDT-bookDepth-%s.zip" % ay,
        "data/futures/um/monthly/metrics/BTCUSDT/BTCUSDT-metrics-%s.zip" % ay,
        # kucuk bir altcoin — boyut kiyasi icin
        "data/futures/um/daily/bookDepth/SOLUSDT/SOLUSDT-bookDepth-%s.zip" % gun,
        "data/futures/um/daily/bookTicker/SOLUSDT/SOLUSDT-bookTicker-%s.zip" % gun,
    ]
    bulunan = []
    for y in denemeler:
        ok, b = var_mi(y)
        kisa = y.replace("data/futures/um/", "")
        print("   %-46s %-8s %s" % (kisa[:46], "VAR" if ok else "yok", mb(b)))
        if ok:
            bulunan.append((y, b))
    print()

    print("### 4) GERIYE NE KADAR GIDIYOR? (bookDepth, BTCUSDT, aylik)")
    for geri in (2, 6, 12, 18, 24, 30):
        a = (datetime.datetime.utcnow() - datetime.timedelta(days=30 * geri)).strftime("%Y-%m")
        ok, b = var_mi("data/futures/um/monthly/bookDepth/BTCUSDT/BTCUSDT-bookDepth-%s.zip" % a)
        print("   %-8s (%2d ay once) : %-4s %s" % (a, geri, "VAR" if ok else "yok", mb(b)))
    print()

    print("=" * 92)
    if bulunan:
        print("🔑 SONUC: emir defteri gecmisi VAR. Proje kaydi ('yalniz ileriye')")
        print("   GUNCELLENMELI — geriye test MUMKUN.")
    else:
        print("SONUC: arsivde emir defteri dosyasi bulunamadi -> kayit dogru,")
        print("   yalniz ileriye kayit mumkun.")
    print()
    print("Indirme YOK · Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
