#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""POZISYON KOMPOZISYONU — SURE OLCUMU (2026-09-06)

Kullanici: "bu kac saatlik onu olc."

Tahmin YOK — gercek dosyalar indirilip SURE olculur, sonra olceklenir.
(CLAUDE.md: "uydurma sayi yok: her rakam ya dosyadan okunur ya olculur.")

OLCULEN: data.binance.vision daily/metrics — 11 kB/sembol/gun.
   Etiket icin indirme GEREKMEZ: klines_1h_uzun (2 yil, 567 sembol) elde.

Salt-okunur. Indirilen dosyalar diske YAZILMAZ (sure olcumu icin okunup atilir).
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import urllib.request, zipfile, io, time, datetime, os
import statistics as stx
from concurrent.futures import ThreadPoolExecutor

ARSIV = "https://data.binance.vision/"
KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KL = os.path.join(KOK, "scratchpad", "klines_1h_uzun")
IS_PARCACIGI = 8


def yol(sym, gun):
    return "data/futures/um/daily/metrics/%s/%s-metrics-%s.zip" % (sym, sym, gun)


def cek(sym, gun):
    """Indir + ayristir. Diske YAZMAZ. -> (satir_sayisi, bayt) ya da None."""
    try:
        ham = urllib.request.urlopen(ARSIV + yol(sym, gun), timeout=40).read()
        z = zipfile.ZipFile(io.BytesIO(ham))
        n = len(z.read(z.namelist()[0]).decode("utf-8", "replace").splitlines())
        return n, len(ham)
    except Exception:
        return None


def main():
    print("=" * 88)
    print("POZISYON KOMPOZISYONU — SURE OLCUMU")
    print("=" * 88)
    print("Tahmin yok; gercek dosya indirilip olculuyor.")
    print()

    semboller = sorted(f[:-5] + "USDT" for f in os.listdir(KL) if f.endswith(".json"))
    print("### 1) EVREN")
    print("   klines_1h_uzun'da sembol: %d  (etiket icin INDIRME GEREKMEZ)" % len(semboller))
    print()

    gun = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    print("### 2) TEK IS PARCACIGI — dosya basi sure (ornek gun %s)" % gun)
    sureler, boyutlar, satirlar = [], [], []
    for s in semboller[:10]:
        t0 = time.time()
        r = cek(s, gun)
        if r:
            sureler.append(time.time() - t0)
            satirlar.append(r[0])
            boyutlar.append(r[1])
    if not sureler:
        print("   dosya cekilemedi")
        return
    tek = stx.median(sureler)
    print("   N=%d · medyan %.3f sn · %.1f kB · %d satir/gun"
          % (len(sureler), tek, stx.median(boyutlar) / 1024, stx.median(satirlar)))
    print()

    print("### 3) %d IS PARCACIGI ILE — gercek hizlanma" % IS_PARCACIGI)
    hedef = [(s, gun) for s in semboller[10:74]]
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=IS_PARCACIGI) as ex:
        sonuc = list(ex.map(lambda x: cek(*x), hedef))
    gecen = time.time() - t0
    ok = sum(1 for x in sonuc if x)
    par = gecen / max(1, ok)
    print("   %d dosya · %.1f sn · dosya basi %.3f sn · hizlanma %.1fx"
          % (ok, gecen, par, tek / par if par else 0))
    print()

    print("### 4) OLCEKLEME — kac saat?")
    print("   %-38s %9s %10s %10s" % ("kapsam", "dosya", "sure", "boyut"))
    for ad, nsym, ngun, adim in (
            ("2 yil · 567 sembol · her gun", 567, 730, 1),
            ("2 yil · 567 sembol · 2 gunde bir", 567, 365, 1),
            ("2 yil · 300 sembol · her gun", 300, 730, 1),
            ("1 yil · 567 sembol · her gun", 567, 365, 1),
            ("2 yil · 150 sembol · her gun", 150, 730, 1)):
        d = nsym * ngun // adim
        print("   %-38s %9d %9.1f sa %9.1f GB"
              % (ad, d, d * par / 3600, d * stx.median(boyutlar) / 1e9))
    print()

    print("### 5) KIYAS — bugun yapilan indirmeler")
    print("   capraz borsa (bybit+binance fonlama) : 104,6 dk")
    print("   OBI (bookDepth 21.600 dosya)         : 145,1 dk")
    print()
    print("Indirilen dosyalar diske YAZILMADI · Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
