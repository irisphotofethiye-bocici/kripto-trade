#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACIK POZISYONLARIN MENZILI — 'tabloyu oynatir' ifadesini SAYIYA cevirir.
TP1 pozisyonun YARISINI kapatir (defter3.py:272). SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json

# esit zemin toplamlari (scratchpad/defter23_esit.py ciktisi)
BAZ = {"defter2": 438.45, "defter3": 20.53}
LONG_KOL = -597.47          # defter3 LONG kolu, 4 poz
LONG_N = 4


def pnl(p, fiyat, oran=1.0):
    m = p["miktar"] * oran
    d = (fiyat - p["giris"]) if p["yon"] == "LONG" else (p["giris"] - fiyat)
    return d * m


print("=" * 94)
print("ACIK POZISYONLAR — mumkun sonuclarin MENZILI")
print("=" * 94)
S = {}
for ad in ("defter2", "defter3"):
    st = json.load(open("%s_state.json" % ad, encoding="utf-8"))
    for p in st["acik_pozisyonlar"]:
        yari = p.get("tp1_alindi")
        kalan = 0.5 if yari else 1.0
        s_stop = pnl(p, p["stop"], kalan)
        # DUZELTME: TP2 yolu TP1 uzerinden gecer -> yari TP1de, yari TP2de kapanir
        s_tp2 = (pnl(p, p["tp2"], kalan) if yari
                 else pnl(p, p["tp1"], 0.5) + pnl(p, p["tp2"], 0.5))
        # TP1'e ulasip sonra stop'a donme (yari kar + yari stop) — yalniz TP1 alinmamissa
        s_tp1 = (pnl(p, p["tp1"], 0.5) + pnl(p, p["stop"], 0.5)) if not yari else None
        print("  %-8s %-8s %-5s  giris %.6f  stop %.6f  tp1 %.6f  tp2 %.6f  %s"
              % (ad, p["sym"], p["yon"], p["giris"], p["stop"], p["tp1"], p["tp2"],
                 "TP1 ALINDI (yari kapali)" if yari else "TP1 alinmadi"))
        print("       STOP olursa  %+8.2f   |   TP1+TP2 olursa  %+8.2f%s"
              % (s_stop, s_tp2,
                 "   |   TP1-sonra-STOP %+8.2f" % s_tp1 if s_tp1 is not None else ""))
        S[ad] = (min(s_stop, s_tp2), max(s_stop, s_tp2), p)

print("")
print("=" * 94)
print("1) ESIT ZEMIN TOPLAMI nereye gider  (08-25 16:12 -> simdi)")
print("=" * 94)
print("  %-9s %10s %12s %12s" % ("", "SIMDI", "EN KOTU", "EN IYI"))
for ad in ("defter2", "defter3"):
    lo, hi, _ = S[ad]
    print("  %-9s %+10.2f %+12.2f %+12.2f" % (ad, BAZ[ad], BAZ[ad] + lo, BAZ[ad] + hi))
d2lo, d2hi = BAZ["defter2"] + S["defter2"][0], BAZ["defter2"] + S["defter2"][1]
d3lo, d3hi = BAZ["defter3"] + S["defter3"][0], BAZ["defter3"] + S["defter3"][1]
print("")
print("  defter3 EN IYI (%+.2f)  vs  defter2 EN KOTU (%+.2f)  ->  %s"
      % (d3hi, d2lo,
         "SIRALAMA DEGISMEZ, defter2 onde kalir" if d3hi < d2lo else "SIRALAMA DONEBILIR"))

print("")
print("=" * 94)
print("2) ASIL OYNAYAN SEY — defter3'un LONG kolu")
print("=" * 94)
lo, hi, p = S["defter3"]
print("  simdi          : %2d poz  %+8.2f  kazanma %%0  (4'te 4 kaybetti)" % (LONG_N, LONG_KOL))
print("  VELVET STOP    : %2d poz  %+8.2f  kazanma %%0  -> '5'te 5 kaybetti'" % (LONG_N + 1, LONG_KOL + lo))
print("  VELVET TP2     : %2d poz  %+8.2f  kazanma %%%.0f -> '5'te 4 kaybetti'"
      % (LONG_N + 1, LONG_KOL + hi, 100.0 / (LONG_N + 1)))
print("")
print("  -> LONG kolunun TOPLAMI %+.2f ile %+.2f arasinda oynar (menzil %.2f $)"
      % (LONG_KOL + lo, LONG_KOL + hi, hi - lo))
print("  -> EN IYI durumda bile LONG kolu EKSIDE kalir: %+.2f" % (LONG_KOL + hi))
