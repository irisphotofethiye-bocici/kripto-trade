#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UC DEFTER KARSILASTIRMASI — golge · defter2 · defter3. SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import pickle, collections, statistics as stt, os

HERE = os.path.dirname(os.path.abspath(__file__))
D = pickle.load(open(os.path.join(HERE, "uc_defter.pkl"), "rb"))


def med(v):
    v = [x for x in v if x is not None]
    return stt.median(v) if v else float("nan")


def karne(P):
    v = [p["pnl"] for p in P]
    kz = [x for x in v if x > 0]
    kb = [-x for x in v if x <= 0]
    ak = stt.mean(kz) if kz else 0.0
    az = stt.mean(kb) if kb else 0.0
    return dict(n=len(v), top=sum(v), ort=stt.mean(v) if v else 0,
                orn=100 * len(kz) / len(v) if v else 0,
                ak=ak, az=az, oran=(ak / az) if az else float("nan"),
                bas=(100 * az / (ak + az)) if (ak + az) else float("nan"),
                tut=med([float(p["k"].get("tutma_saat") or 0) for p in P]),
                tp1=100 * sum(1 for p in P if p["tp1"]) / len(P) if v else 0,
                fnd=sum(p["fnd"] for p in P))


print("=" * 104)
print("A) UC DEFTER — TEMEL KARNE")
print("=" * 104)
print("  %-26s %5s %10s %8s %8s %9s %9s %6s %7s %7s"
      % ("defter / is", "poz", "P&L", "kazanma", "ort P&L", "ort KAZ", "ort KAY",
         "oran", "tutma", "TP1%"))
GRUP = collections.OrderedDict()
GRUP["golge — TUMU"] = D["golge"]
GRUP["  golge: pump_long_tezi"] = [p for p in D["golge"]
                                   if p["k"].get("kaynak") == "golge:pump_long_tezi"]
GRUP["  golge: REDDEDILENLER"] = [p for p in D["golge"]
                                  if p["k"].get("kaynak") != "golge:pump_long_tezi"]
GRUP["defter2 (yalniz SHORT)"] = D["defter2"]
GRUP["defter3 — TUMU"] = D["defter3"]
GRUP["  defter3: SHORT kolu"] = [p for p in D["defter3"] if p["k"]["yon"] == "SHORT"]
GRUP["  defter3: LONG kolu"] = [p for p in D["defter3"] if p["k"]["yon"] == "LONG"]
K = {}
for ad, P in GRUP.items():
    if not P:
        continue
    k = karne(P)
    K[ad] = k
    print("  %-26s %5d %+10.0f %7.0f%% %+8.1f %+9.1f %-9s %6.2f %6.1fs %6.0f%%"
          % (ad, k["n"], k["top"], k["orn"], k["ort"], k["ak"], "-%.1f" % k["az"],
             k["oran"], k["tut"], k["tp1"]))

print("")
print("  BASABAS ICIN GEREKEN KAZANMA ORANI vs GERCEK")
for ad in K:
    k = K[ad]
    print("     %-26s gereken %%%.1f · gercek %%%.1f · ACIK %+.1f puan"
          % (ad, k["bas"], k["orn"], k["orn"] - k["bas"]))

print("")
print("=" * 104)
print("B) GOLGE — KAPI KAPI (hangi kapinin reddettigi giris)")
print("=" * 104)
g = collections.defaultdict(list)
for p in D["golge"]:
    g[p["k"].get("kaynak", "?")].append(p)
print("  %-26s %5s %10s %8s %9s %6s %7s %7s"
      % ("kaynak", "poz", "P&L", "kazanma", "ort P&L", "oran", "tutma", "TP1%"))
for ad, P in sorted(g.items(), key=lambda x: karne(x[1])["top"]):
    k = karne(P)
    print("  %-26s %5d %+10.0f %7.0f%% %+9.1f %6.2f %6.1fs %6.0f%%"
          % (ad, k["n"], k["top"], k["orn"], k["ort"], k["oran"], k["tut"], k["tp1"]))

print("")
print("=" * 104)
print("C) GIRIS KOSULLARI — arsivden (MEDYAN degerler)")
print("=" * 104)
ALAN = [("price", "fiyat $"), ("funding", "funding %"), ("vol_x", "hacim x"),
        ("oi24", "OI 24s %"), ("oi3", "OI 3s %"), ("score", "skor"),
        ("chg24", "chg24 %"), ("mcap", "mcap M$"), ("taker", "taker"),
        ("last1", "son1 %"), ("last3", "son3 %"), ("pos", "bant konum")]


def _say(ad, v):
    if v is None:
        return None
    if ad == "mcap" and isinstance(v, str):
        t = v.strip().replace("$", "").replace(",", "")
        kat = 1.0
        if t.endswith("B"):   kat, t = 1000.0, t[:-1]
        elif t.endswith("M"): kat, t = 1.0, t[:-1]
        elif t.endswith("K"): kat, t = 0.001, t[:-1]
        try:
            return float(t) * kat
        except ValueError:
            return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


SEC = ["golge — TUMU", "  golge: pump_long_tezi", "  golge: REDDEDILENLER",
       "defter2 (yalniz SHORT)", "  defter3: SHORT kolu", "  defter3: LONG kolu"]
print("  %-14s" % "alan" + "".join("%12s" % a.split(":")[-1].strip()[:11] for a in SEC))
for al, et in ALAN:
    sat = "  %-14s" % et
    for ad in SEC:
        v = [_say(al, p["ars"].get(al)) for p in GRUP[ad] if p.get("ars")]
        m = med(v)
        sat += "%12s" % ("—" if m != m else ("%.3f" % m if abs(m) < 10 else "%.1f" % m))
    print(sat)
# derinlik defterden
for al, et in (("defter_usdt_20", "defter $20"), ("slipaj_pct", "slipaj %")):
    sat = "  %-14s" % et
    for ad in SEC:
        v = [p["k"].get("derinlik_giriste", {}).get(al) for p in GRUP[ad]
             if isinstance(p["k"].get("derinlik_giriste"), dict)]
        m = med([x for x in v if x is not None])
        sat += "%12s" % ("—" if m != m else ("%.3f" % m if abs(m) < 10 else "%.0f" % m))
    print(sat)
print("  %-14s" % "N (eslesen)" + "".join("%12d" % sum(1 for p in GRUP[a] if p.get("ars"))
                                          for a in SEC))
