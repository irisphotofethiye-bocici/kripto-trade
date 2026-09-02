#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DUSEN BICAGI YAKALAMA — ayni sembole tekrar tekrar LONG. SALT OKUMA.
NOT: atr_giriste ve stop defterde YOK (0 kayit) — ATR kiyasi YAPILAMAZ."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections, datetime as dt, statistics as stt

T0 = "2026-08-25 16:12:12"


def poz(f):
    K = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    g = {}
    for r in K:
        t = dt.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S") \
            - dt.timedelta(hours=float(r.get("tutma_saat") or 0))
        if r["id"] not in g or t < g[r["id"]]:
            g[r["id"]] = t
    pnl, meta = collections.defaultdict(float), {}
    for r in K:
        if g[r["id"]].strftime("%Y-%m-%d %H:%M:%S") < T0:
            continue
        pnl[r["id"]] += float(r.get("sonuc_usdt") or 0)
        if not r.get("kismi"):
            meta[r["id"]] = dict(r, _gts=g[r["id"]])
    return [(pnl[i], meta[i]) for i in meta]


D3 = poz("defter3_islemler.jsonl")
L = sorted([x for x in D3 if x[1]["yon"] == "LONG"], key=lambda x: x[1]["_gts"])
S = [x for x in D3 if x[1]["yon"] == "SHORT"]

print("=" * 96)
print("1) TEKRAR GIRIS — ayni sembole kacinci kez")
print("=" * 96)
for ad, X in (("LONG", L), ("SHORT", sorted(S, key=lambda x: x[1]["_gts"]))):
    say = collections.Counter()
    grup = collections.defaultdict(lambda: [0, 0.0])
    for p, m in X:
        say[m["sym"]] += 1
        k = min(say[m["sym"]], 4)
        grup[k][0] += 1
        grup[k][1] += p
    print("  --- %s ---  tekil sembol %d / %d pozisyon" % (ad, len(say), len(X)))
    for k in sorted(grup):
        v = grup[k]
        et = "%d. giris" % k if k < 4 else "4+. giris"
        print("     %-10s %3d poz  toplam %+9.2f  ort %+7.2f" % (et, v[0], v[1], v[1] / v[0]))
    print("")

print("=" * 96)
print("2) LONG — SEMBOL BASINA (2+ giris olanlar)")
print("=" * 96)
sg = collections.defaultdict(list)
for p, m in L:
    sg[m["sym"]].append((p, m))
print("  %-10s %4s %11s %10s %10s  %s" % ("sym", "poz", "P&L", "ilk giris", "son giris", "fiyat yonu"))
tekrar_pnl = tek_pnl = 0.0
for s, v in sorted(sg.items(), key=lambda x: sum(p for p, _ in x[1])):
    tot = sum(p for p, _ in v)
    f0, f1 = float(v[0][1]["giris"]), float(v[-1][1]["giris"])
    if len(v) >= 2:
        tekrar_pnl += tot
        print("  %-10s %4d %+11.2f %10.6f %10.6f  %+6.1f%%"
              % (s, len(v), tot, f0, f1, 100 * (f1 - f0) / f0))
    else:
        tek_pnl += tot
print("")
print("  TEKRAR girilen semboller (2+): %+9.2f" % tekrar_pnl)
print("  TEK   girilen semboller      : %+9.2f" % tek_pnl)
print("  -> LONG kolunun kaybinin %%%.0f'i TEKRAR girislerden"
      % (100 * tekrar_pnl / (tekrar_pnl + tek_pnl)))

print("")
print("=" * 96)
print("3) TEKRAR GIRISLER FIYAT DUSERKEN Mi OLUYOR")
print("=" * 96)
dus = ayn = yuk = 0
dus_p = yuk_p = 0.0
for s, v in sg.items():
    for i in range(1, len(v)):
        onc, sim = float(v[i - 1][1]["giris"]), float(v[i][1]["giris"])
        d = 100 * (sim - onc) / onc
        if d < -1:
            dus += 1; dus_p += v[i][0]
        elif d > 1:
            yuk += 1; yuk_p += v[i][0]
        else:
            ayn += 1
print("  onceki girise gore YENI giris fiyati:")
print("     DAHA DUSUK (>%%1)  %3d giris   toplam %+9.2f" % (dus, dus_p))
print("     DAHA YUKSEK (>%%1) %3d giris   toplam %+9.2f" % (yuk, yuk_p))
print("     AYNI (+-%%1)       %3d giris" % ayn)

print("")
print("=" * 96)
print("4) STOP KAYBI — marjin yuzdesi olarak (ATR defterde YOK, bu vekil)")
print("=" * 96)
for ad, X in (("LONG", L), ("SHORT", S)):
    st = [(p, m) for p, m in X if m.get("sebep") == "STOP" and p < 0]
    if st:
        oran = [100 * p / float(m["marjin"]) for p, m in st]
        print("  %-6s STOP'la kapanan %3d poz · kayip/marjin medyan %%%.1f · ort %%%.1f"
              % (ad, len(st), stt.median(oran), stt.mean(oran)))
print("  ⚠️ atr_giriste ve stop alanlari DEFTERE YAZILMIYOR (0/256 kayit) —")
print("     stop GENISLIGI kiyasi bu veriyle YAPILAMAZ, yalniz gerceklesmis kayip gorulur.")
