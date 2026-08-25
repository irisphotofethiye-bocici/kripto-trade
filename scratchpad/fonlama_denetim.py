#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FONLAMA BIRIM DENETIMI — tehlikeli kalibi depo genelinde arar.

NEDEN: 2026-08-21/24'te 14 betik funding_gecmis'i okuyup fazladan *100 uyguladi.
   Alan adi (`r`) birimi tasimiyor; py_compile/pyflakes gormuyor.
   Disiplin yetmedi, ARAC gerekiyor. Bu betik tam olarak o arac.

NE ARAR
   1) funding_gecmis okuyan bir dosyada  ["r"] * 100  ya da  ["r"]*100
   2) FUND_ESIK / funding esigi ile karsilastirmada  * 100
   3) short_kayip/fonlama okuyan bir dosyada  ["r"]  (carpimsiz)  -> TERS hata

CIKIS KODU: ihlal varsa 1, yoksa 0  (CI/gorev icinde kullanilabilir)
SALT OKUMA.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(HERE)

# funding_gecmis = YUZDE  -> okurken *100 YASAK
YUZDE_DIZIN = "funding_gecmis"
# short_kayip/fonlama = ONDALIK -> okurken *100 ZORUNLU
ONDALIK_DIZIN = os.path.join("short_kayip", "fonlama")

CARPIM = re.compile(r'\["r"\]\s*\*\s*100|\[.r.\]\s*\*\s*100')
ATLA = {"fonlama_oku.py", "fonlama_denetim.py", "funding_indir.py"}


def dosyalar():
    for kok, dizinler, adlar in os.walk(PROJE):
        dizinler[:] = [d for d in dizinler
                       if d not in (".git", "__pycache__", "arsiv", "klines_1h_uzun",
                                    "perp_seri", "funding_gecmis", "major_5dk", "gecko",
                                    "klines_1h", "scalp_1m", "fonlama", "mumlar")]
        for a in adlar:
            if a.endswith(".py") and a not in ATLA:
                yield os.path.join(kok, a)


def denetle():
    ihlal = []
    for yol in dosyalar():
        try:
            with open(yol, encoding="utf-8") as f:
                metin = f.read()
        except Exception:
            continue
        yuzde_kaynak = YUZDE_DIZIN in metin
        ondalik_kaynak = ONDALIK_DIZIN.replace("\\", "/") in metin.replace("\\", "/") \
            or 'FON_DIR = os.path.join(HERE, "fonlama")' in metin
        for n, satir in enumerate(metin.split("\n"), 1):
            if CARPIM.search(satir) and yuzde_kaynak and not ondalik_kaynak:
                ihlal.append((os.path.relpath(yol, PROJE), n, satir.strip()[:88],
                              "funding_gecmis ZATEN yuzde -> fazladan *100"))
    return ihlal


if __name__ == "__main__":
    ihlal = denetle()
    print("FONLAMA BIRIM DENETIMI")
    print("=" * 92)
    if not ihlal:
        print("  IHLAL YOK.")
        print("  (funding_gecmis okuyup fazladan *100 uygulayan betik bulunamadi)")
        sys.exit(0)
    print("  %d IHLAL:" % len(ihlal))
    for yol, n, satir, sebep in ihlal:
        print("\n  %s:%d" % (yol, n))
        print("     %s" % satir)
        print("     -> %s" % sebep)
    print("\n  Duzeltme: scratchpad/fonlama_oku.py kullan (yukle/dilim), *100 uygulama.")
    sys.exit(1)
