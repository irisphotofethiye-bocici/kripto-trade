#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KARSI-OLGU HAVUZU vs NOTRLONG HAVUZU — ayni mi? SALT OKUMA, DUZELTME YOK."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections

A, B = "2026-08-21", "2026-09-03"        # karsi-olgu penceresi (08-21..09-02)
BONUS = 8.0


def oku(f):
    out = []
    for l in open(f, encoding="utf-8", errors="replace"):
        l = l.strip()
        if not l:
            continue
        try:
            out.append(json.loads(l))
        except Exception:
            pass
    return out


ADAY = [d for d in oku("testbot_aday_arsiv.jsonl") if A <= str(d.get("ts", ""))[:10] < B]
RAD = [d for d in oku("radar_archive.jsonl") if A <= str(d.get("ts", ""))[:10] < B]

print("=" * 96)
print("1) HAM BUYUKLUK — pencere %s .. %s" % (A, B))
print("=" * 96)
print("  testbot_aday_arsiv (karsi-olgunun kullandigi) : %6d kayit · %4d tur · %3d sembol"
      % (len(ADAY), len({d["ts"] for d in ADAY}), len({d["sym"] for d in ADAY})))
print("  radar_archive      (notrlong'un taradigi)     : %6d kayit · %4d tur · %3d sembol"
      % (len(RAD), len({d["ts"] for d in RAD}), len({d["sym"] for d in RAD})))

# notrlong'un havuzunu YENIDEN URET: skor>=30 -> sirala -> ilk 10
tur = collections.defaultdict(list)
for d in RAD:
    if (d.get("score") or 0) >= 30:
        tur[d["ts"]].append(d)
NL = []
for ts, rows in tur.items():
    rows.sort(key=lambda x: -((x.get("score") or 0)
                              + (BONUS if x.get("stage") == "HAZIRLANIYOR" else 0.0)))
    NL.extend(rows[:10])
print("  notrlong havuzu (yeniden uretildi: skor>=30, ilk 10) : %6d kayit · %4d tur"
      % (len(NL), len(tur)))

print("")
print("=" * 96)
print("2) AYNI TUR + AYNI SEMBOL — ortusme")
print("=" * 96)
sa = {(d["ts"], d["sym"]) for d in ADAY}
sn = {(d["ts"], d["sym"]) for d in NL}
ort = sa & sn
print("  aday_arsiv cift : %6d" % len(sa))
print("  notrlong  cift  : %6d" % len(sn))
print("  ORTAK           : %6d" % len(ort))
print("    aday_arsiv'in %%%.1f'i notrlong havuzunda" % (100 * len(ort) / max(len(sa), 1)))
print("    notrlong'un   %%%.1f'i aday_arsiv'de" % (100 * len(ort) / max(len(sn), 1)))
print("  yalniz aday_arsiv'de : %6d" % len(sa - sn))
print("  yalniz notrlong'da   : %6d" % len(sn - sa))

print("")
print("=" * 96)
print("3) PROFIL KIYASI — iki havuz ayni seye mi benziyor")
print("=" * 96)


def profil(ad, X):
    st = collections.Counter(d.get("stage") for d in X)
    sk = sorted((d.get("score") or 0) for d in X)
    t = len(X)
    med = sk[t // 2] if t else 0
    ak = 100 * sum(v for k, v in st.items() if k in ("BASLIYOR", "HAZIRLANIYOR")) / max(t, 1)
    sm = collections.Counter(d.get("smart") for d in X)
    print("  %-34s N=%-6d medyan skor %5.1f · aktif stage %%%5.2f · smart LONG %%%.1f"
          % (ad, t, med, ak, 100 * sm.get("LONG", 0) / max(t, 1)))


profil("aday_arsiv (karsi-olgu)", ADAY)
profil("notrlong havuzu", NL)
profil("radar TAM tarama", RAD)

print("")
print("=" * 96)
print("4) 🔴 BELIRLEYICI — NOTR kapisini gecebilecek aday sayisi")
print("=" * 96)


def uygun(d):
    st, sk = d.get("stage"), (d.get("score") or 0)
    if st not in ("BASLIYOR", "HAZIRLANIYOR"):
        return False
    if sk < (40.0 if st == "HAZIRLANIYOR" else 45.0):
        return False
    return d.get("smart") == "LONG"


for ad, X, nt in (("aday_arsiv (karsi-olgu)", ADAY, len({d["ts"] for d in ADAY})),
                  ("notrlong havuzu", NL, len(tur))):
    u = [d for d in X if uygun(d)]
    print("  %-28s uygun aday %4d · tur %4d · TUR BASINA %.3f"
          % (ad, len(u), nt, len(u) / max(nt, 1)))

print("")
print("=" * 96)
print("5) aday_arsiv NE ZAMAN DURDU")
print("=" * 96)
tum = oku("testbot_aday_arsiv.jsonl")
ts = sorted(str(d.get("ts", "")) for d in tum if d.get("ts"))
print("  ilk kayit : %s" % ts[0])
print("  son kayit : %s" % ts[-1])
g = collections.Counter(t[:10] for t in ts)
print("  son 6 gun :", {k: g[k] for k in sorted(g)[-6:]})
