#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KUYRUK RISKI — "ilk 30 coin ne kadar dusebilir?" (2026-09-05)

Kullanici iddiasi: buyuk coinlerin oynakligi dusuk, sifirlanmasi zor -> kaybi
  daha az olmali. BU BETIK O IDDIAYI OLCER.

🔴 IKI AYRI SORU, KARISTIRILMAZ:
  (a) TIPIK hareket  -> risk-bazli boyutlandirmada NOTR'dur: stop dar olunca
      pozisyon buyur, dolar riski SABIT kalir. Dusuk oynaklik kaybi AZALTMAZ.
  (b) KUYRUK          -> asil fark burada: -%50/-%90 gibi hareketler ve
      likidasyon riski. Boyutlandirma bunu normalize ETMEZ.

Olculen: her sembol-saat icin ONUMUZDEKI 72 SAATTE en kotu hareket
  (LONG icin en dusuk dip, SHORT icin en yuksek tepe), fiyat kovasina gore.
BETIMLEYICI. On-kayit yok, hukum yok. Salt-okunur.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import sys, json, os, statistics as stx, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ileri_rr as ir

BURA = os.path.dirname(os.path.abspath(__file__))
ESKI_K, YENI_K = os.path.join(BURA, "klines_1h_uzun"), os.path.join(BURA, "taze_1h")
UFUK, SEYRELT, ISINMA = 72, 24, 60
MIN_VOL = 3_000_000

KOVA = [(0.01, "< $0,01"), (0.07, "$0,01-0,07"), (1.0, "$0,07-1"),
        (10.0, "$1-10"), (100.0, "$10-100"), (float("inf"), ">= $100")]
SIRA = [k[1] for k in KOVA]


def birlestir(a, b):
    d = {}
    for y in (a, b):
        if os.path.exists(y):
            try:
                for x in json.load(open(y, encoding="utf-8")):
                    d[int(x["t"])] = x
            except Exception:
                pass
    return [d[k] for k in sorted(d)] if d else None


def kova(p):
    for esik, ad in KOVA:
        if p < esik:
            return ad
    return SIRA[-1]


def dilim(v, q):
    s = sorted(v)
    return s[min(int(len(s) * q), len(s) - 1)]


def main():
    print("=" * 84)
    print("KUYRUK RISKI — 'ilk 30 coin ne kadar dusebilir?'")
    print("=" * 84)
    print("🔴 Betimleyici. On-kayit yok, hukum yok.")
    print("Olcu: onumuzdeki %d saatte en kotu hareket (giristen).\n" % UFUK)

    asagi = collections.defaultdict(list)   # LONG'un aleyhine: en dusuk dip
    yukari = collections.defaultdict(list)  # SHORT'un aleyhine: en yuksek tepe
    atrp = collections.defaultdict(list)
    sem = collections.defaultdict(set)

    for f in sorted(os.listdir(ESKI_K)):
        if not f.endswith(".json"):
            continue
        sym = f[:-5]
        b = birlestir(os.path.join(ESKI_K, f), os.path.join(YENI_K, f))
        if not b or len(b) < ISINMA + UFUK + 50:
            continue
        atrs = ir.atr_serisi(b)
        for i in range(ISINMA, len(b) - UFUK - 1, SEYRELT):
            x = b[i]
            hac = sum(y.get("qv") or 0 for y in b[max(0, i - 23):i + 1])
            if hac < MIN_VOL:
                continue
            ref = b[i + 1]["o"]
            if ref <= 0:
                continue
            pen = b[i + 1:i + 1 + UFUK]
            if len(pen) < UFUK // 2:
                continue
            dip = min(y["l"] for y in pen)
            tepe = max(y["h"] for y in pen)
            k = kova(x["c"])
            asagi[k].append((dip / ref - 1) * 100)
            yukari[k].append((tepe / ref - 1) * 100)
            sem[k].add(sym)
            a = atrs[i]
            if a and a > 0:
                atrp[k].append(a / ref * 100)

    print("### LONG'UN ALEYHINE — 72 saatte EN DUSUK dip (giristen %%)")
    print("%-13s %9s %7s %8s %8s %8s %8s %9s %9s" %
          ("fiyat kovasi", "N", "sembol", "medyan", "%25", "%5", "%1", "<-%50 sik", "<-%30 sik"))
    for k in SIRA:
        v = asagi.get(k)
        if not v or len(v) < 200:
            continue
        print("%-13s %9d %7d %+8.2f %+8.2f %+8.2f %+8.2f %8.2f%% %8.2f%%" %
              (k, len(v), len(sem[k]), stx.median(v), dilim(v, 0.25), dilim(v, 0.05),
               dilim(v, 0.01),
               sum(1 for x in v if x <= -50) / len(v) * 100,
               sum(1 for x in v if x <= -30) / len(v) * 100))

    print("\n### SHORT'UN ALEYHINE — 72 saatte EN YUKSEK tepe (giristen %%)")
    print("%-13s %9s %8s %8s %8s %8s %9s %9s" %
          ("fiyat kovasi", "N", "medyan", "%75", "%95", "%99", "+%50 sik", "+%30 sik"))
    for k in SIRA:
        v = yukari.get(k)
        if not v or len(v) < 200:
            continue
        print("%-13s %9d %+8.2f %+8.2f %+8.2f %+8.2f %8.2f%% %8.2f%%" %
              (k, len(v), stx.median(v), dilim(v, 0.75), dilim(v, 0.95), dilim(v, 0.99),
               sum(1 for x in v if x >= 50) / len(v) * 100,
               sum(1 for x in v if x >= 30) / len(v) * 100))

    print("\n### OYNAKLIK ve KALDIRACLA LIKIDASYON MESAFESI")
    print("%-13s %10s %14s %s" % ("fiyat kovasi", "ATR/fiyat", "kald.3 liq ~%33", "72s'de asilma sikligi"))
    for k in SIRA:
        v = atrp.get(k)
        if not v or len(v) < 200:
            continue
        d = asagi[k]
        u = yukari[k]
        print("%-13s %9.2f%% %14s   LONG %5.2f%%  ·  SHORT %5.2f%%" %
              (k, stx.median(v), "-",
               sum(1 for x in d if x <= -33) / len(d) * 100,
               sum(1 for x in u if x >= 33) / len(u) * 100))

    print("\n🔑 YORUM ANAHTARI:")
    print("  'medyan/%25' = TIPIK hareket -> risk-bazli boyutta NOTR (stop dar,")
    print("                 pozisyon buyuk, dolar riski AYNI).")
    print("  '%1 / <-%50 / liq asilma' = KUYRUK -> boyutlandirma bunu normalize")
    print("                 ETMEZ; kaldiracla likidasyon buradan gelir.")
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
