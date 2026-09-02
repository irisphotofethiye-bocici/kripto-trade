#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D) kazanan vs kaybeden  E) sure/karda kalma  F) mcap kontrolu. SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import pickle, collections, statistics as stt, math, os

D = pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "uc_defter.pkl"), "rb"))
G = {"golge/pump": [p for p in D["golge"] if p["k"].get("kaynak") == "golge:pump_long_tezi"],
     "golge/RED": [p for p in D["golge"] if p["k"].get("kaynak") != "golge:pump_long_tezi"],
     "defter2": D["defter2"],
     "defter3/SHORT": [p for p in D["defter3"] if p["k"]["yon"] == "SHORT"],
     "defter3/LONG": [p for p in D["defter3"] if p["k"]["yon"] == "LONG"]}


def sayi(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def med(v):
    v = [x for x in v if x is not None]
    return stt.median(v) if v else float("nan")


print("=" * 100)
print("F) mcap ALANI — neden bos")
print("=" * 100)
ham = [p["ars"].get("mcap") for p in D["golge"][:400] if p.get("ars")]
print("  ornek degerler:", [x for x in ham[:6]])
print("  None olan:", sum(1 for x in ham if x is None), "/", len(ham))

print("")
print("=" * 100)
print("D) KAZANAN vs KAYBEDEN — giris aninda ne farkliydi (medyan)")
print("   ⚠️ TP1 KONTROL KATMANI (65043f6): TP1 SONUCtur, ayri satirda gosteriliyor")
print("=" * 100)
ALAN = [("vol_x", "hacim x"), ("oi24", "OI24 %"), ("oi3", "OI3 %"),
        ("funding", "funding"), ("score", "skor"), ("chg24", "chg24 %"),
        ("pos", "bant konum"), ("taker", "taker"), ("price", "fiyat $"),
        ("last3", "son3 %")]
for ad, P in G.items():
    kz = [p for p in P if p["pnl"] > 0 and p.get("ars")]
    kb = [p for p in P if p["pnl"] <= 0 and p.get("ars")]
    if len(kz) < 8 or len(kb) < 8:
        continue
    print("  --- %s   (kazanan %d · kaybeden %d) ---" % (ad, len(kz), len(kb)))
    for al, et in ALAN:
        a, b = med([sayi(p["ars"].get(al)) for p in kz]), med([sayi(p["ars"].get(al)) for p in kb])
        if a != a or b != b:
            continue
        fark = a - b
        im = "  <<<" if abs(fark) > 0.25 * max(abs(a), abs(b), 1e-9) else ""
        print("     %-12s kazanan %9.3f · kaybeden %9.3f · fark %+9.3f%s" % (et, a, b, fark, im))
    t1k = 100 * sum(1 for p in kz if p["tp1"]) / len(kz)
    t1b = 100 * sum(1 for p in kb if p["tp1"]) / len(kb)
    print("     %-12s kazanan %8.0f%% · kaybeden %8.0f%%   <- SONUC, sebep DEGIL"
          % ("TP1 orani", t1k, t1b))
    print("")

print("=" * 100)
print("E) SURE — tutma ve 'karda kalma' vekilleri")
print("=" * 100)
print("  %-16s %8s %8s %8s %9s %9s"
      % ("defter/kol", "medyan", "kazanan", "kaybeden", "TP1'e", "TP1 sonrasi"))
for ad, P in G.items():
    t = [float(p["k"].get("tutma_saat") or 0) for p in P]
    tk = [float(p["k"].get("tutma_saat") or 0) for p in P if p["pnl"] > 0]
    tb = [float(p["k"].get("tutma_saat") or 0) for p in P if p["pnl"] <= 0]
    tp1 = [float(p["k"].get("tutma_saat") or 0) for p in P if p["tp1"]]
    ntp = [float(p["k"].get("tutma_saat") or 0) for p in P if not p["tp1"]]
    print("  %-16s %7.1fs %7.1fs %7.1fs %8.1fs %8.1fs"
          % (ad, med(t), med(tk), med(tb), med(tp1), med(ntp)))
print("")
print("  NOT: 'karda kalma suresi' dogrudan olculemiyor — defter yalniz KAPANIS")
print("  kaydi tutuyor, pozisyon ici fiyat yolu YOK. TP1'e ulasma orani ve")
print("  kazanan-tutma bunun en yakin vekilleri.")

print("")
print("=" * 100)
print("G) HER KOL — kaybin YAPISI")
print("=" * 100)
for ad, P in G.items():
    v = sorted(p["pnl"] for p in P)
    top = sum(v)
    eksi = [x for x in v if x <= 0]
    print("  %-16s N=%3d  toplam %+8.0f · en kotu 5 %+8.0f (%%%.0f) · eksi %d/%d (%%%.0f)"
          % (ad, len(v), top, sum(v[:5]),
             100 * sum(v[:5]) / top if top else 0,
             len(eksi), len(v), 100 * len(eksi) / len(v)))
