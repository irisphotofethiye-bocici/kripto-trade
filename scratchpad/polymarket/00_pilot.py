#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""POLYMARKET 5dk BTC Up/Down — TEK KRITIK IDDIANIN PILOTU (2026-09-06)

Kullanici: github.com/Novals83/5min-btc-polymarket 'ise yarar bisi cikar mi'

STRATEJI: 5 dakikalik pencerenin ~3. dakikasinda BTC $70-100 hareket ettiyse,
o yonde 0,70 fiyattan al. BASABAS = %70 (ima edilen olasilik).

OLCULEN TEK SEY: P(pencere ayni tarafta kapanir | 3 dk gecti, |hareket| $70-100)
   > %70 mi?

🟡 PILOT — on-kayit YOK, hukum YOK. Yalnizca 'olcmeye deger mi' sorusu.
SALT-OKUNUR. Ucretsiz (data.binance.vision).
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import io, zipfile, urllib.request, collections, datetime as dt, math

KOK_URL = "https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/1m"
AYLAR = ["2026-06", "2026-07", "2026-08"]
ALT, UST = 70.0, 100.0
PENCERE = 5          # dakika
GECEN = 3            # kac dakika gecmisken bakiliyor (kapanisa 2 dk kala)


def ay_indir(ay):
    u = "%s/BTCUSDT-1m-%s.zip" % (KOK_URL, ay)
    ham = urllib.request.urlopen(u, timeout=120).read()
    z = zipfile.ZipFile(io.BytesIO(ham))
    out = []
    for l in z.read(z.namelist()[0]).decode("utf-8", "replace").splitlines():
        p = l.split(",")
        if len(p) < 5 or not p[0].isdigit():
            continue
        out.append((int(p[0]), float(p[1]), float(p[4])))   # t, open, close
    return out


def main():
    bar = []
    for ay in AYLAR:
        try:
            b = ay_indir(ay)
            bar += b
            print("   %s -> %d dakika bar" % (ay, len(b)))
        except Exception as e:
            print("   %s HATA: %s" % (ay, str(e)[:80]))
    bar.sort()
    print("toplam %d dakika bar" % len(bar))
    ix = {t: i for i, (t, o, c) in enumerate(bar)}

    # 5 dakikalik pencereler :00 :05 :10 ... hizali
    say = collections.Counter()
    kazanan = 0
    toplam = 0
    hareketler = []
    for i, (t, o, c) in enumerate(bar):
        d = dt.datetime.fromtimestamp(t / 1000, dt.UTC)
        if d.minute % PENCERE != 0:
            continue
        i3 = ix.get(t + (GECEN - 1) * 60_000)     # 3. dakikanin KAPANISI
        i5 = ix.get(t + (PENCERE - 1) * 60_000)   # 5. dakikanin KAPANISI
        if i3 is None or i5 is None:
            continue
        acilis = o
        p3 = bar[i3][2]
        p5 = bar[i5][2]
        hareket = p3 - acilis
        if not (ALT <= abs(hareket) <= UST):
            continue
        toplam += 1
        hareketler.append(abs(hareket))
        yon = 1 if hareket > 0 else -1
        son = 1 if (p5 - acilis) > 0 else (-1 if (p5 - acilis) < 0 else 0)
        if son == yon:
            kazanan += 1
            say["kazandi"] += 1
        elif son == 0:
            say["berabere"] += 1
        else:
            say["kaybetti"] += 1

    print()
    print("=" * 84)
    print("SONUC — P(ayni tarafta kapanir | 3dk gecti, hareket $%.0f-$%.0f)" % (ALT, UST))
    print("=" * 84)
    if not toplam:
        print("olay yok")
        return
    p = kazanan / toplam
    se = math.sqrt(p * (1 - p) / toplam)
    print("   olay sayisi        : %d" % toplam)
    print("   ayni tarafta kapandi: %d  ->  %%%.2f   (+-%.2f puan, 1 s.h.)"
          % (kazanan, 100 * p, 100 * se))
    print("   dagilim            : %s" % dict(say))
    print()
    print("   BASABAS (0,70 fiyat): %70,00")
    print("   FARK                : %+.2f puan   (%.1f standart hata)"
          % (100 * p - 70.0, (100 * p - 70.0) / (100 * se) if se else 0))
    print()
    print("   ⚠️ Bu HAM olasilik. Gercek islemde ayrica: spread (<=0,03 -> 0,70'te")
    print("      %%4,3 maliyet) · slipaj · Polymarket ucreti · 0,70'ten ALABILME.")
    print()
    print("🟡 PILOT — on-kayit yok, hukum yok. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
