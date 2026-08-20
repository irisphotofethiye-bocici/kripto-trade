# -*- coding: utf-8 -*-
"""IZ D-2 — `smart=NOTR` adaylari NEDEN bu kadar dusuyor?

D_smart bulgusu: 72 saatte NOTR -14,306% (7/7 gun negatif, gun-t -6,49),
LONG -1,837, SHORT +3,014. NOTR digerlerinden DRAMATIK ayriliyor.
Bot NOTR'u "iki yonlu fade" diye isliyor (testbot.py, smart=NOTR fade dali).

KONTROLLER:
  1. gun ici etiket karistirma (NOTR vs digerleri) — sans olcumu
  2. chg24 sabitlenince duruyor mu (NOTR adaylari zaten pumplamis olabilir)
  3. gun gun kirilim — tek gune mi dayaniyor
"""
import json, os, sys, collections, statistics as stx, datetime, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PROJE = os.path.dirname(os.path.dirname(HERE))
import ortak
random.seed(41)

ev = {}
with open(os.path.join(PROJE, "testbot_aday_arsiv.jsonl"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        x = json.loads(line)
        if x["ts"][:10] < "2026-08-11" or x.get("smart") is None: continue
        k = (x["sym"], x["ts"][:13])
        if k not in ev: ev[k] = x

kayit = []
for (sym, saat), x in ev.items():
    b = ortak.mumlar(sym)
    if not b: continue
    t0 = int(datetime.datetime.strptime(x["ts"], "%Y-%m-%d %H:%M").timestamp()*1000)
    ic = [z for z in b if z["t"] >= t0]
    if len(ic) < 12*72+1: continue
    ref = ic[0]["o"]
    if ref <= 0: continue
    kayit.append({"smart": x["smart"], "gun": x["ts"][:10], "sym": sym,
                  "chg24": x.get("chg24"), "r72": (ic[12*72]["c"]/ref-1)*100})
print("72 saatlik ufku TAM olan olay: %d\n" % len(kayit))

print("KONTROL 1 — gun gun kirilim (tek gune mi dayaniyor?)")
print("%-12s %8s %10s %8s %10s %8s %10s" % ("gun", "N_NOTR", "NOTR r72", "N_LONG", "LONG r72", "fark", "N_hepsi"))
g = collections.defaultdict(list)
for d in kayit: g[d["gun"]].append(d)
farklar = []
for gun in sorted(g):
    v = g[gun]
    n = [d["r72"] for d in v if d["smart"] == "NOTR"]
    l = [d["r72"] for d in v if d["smart"] == "LONG"]
    if len(n) < 5 or len(l) < 5:
        print("%-12s %8d %10s %8d %10s" % (gun, len(n), "-", len(l), "-")); continue
    f = stx.mean(n)-stx.mean(l); farklar.append(f)
    print("%-12s %8d %+10.2f %8d %+10.2f %+8.2f %10d" % (gun, len(n), stx.mean(n), len(l), stx.mean(l), f, len(v)))
if len(farklar) >= 3:
    se = stx.stdev(farklar)/len(farklar)**0.5
    print("\n   GUN-KUMELI fark (NOTR - LONG): %d gun · ort %+.2f · t=%+.2f · negatif %d/%d"
          % (len(farklar), stx.mean(farklar), stx.mean(farklar)/se if se else 0,
             sum(1 for x in farklar if x < 0), len(farklar)))

print("\nKONTROL 2 — chg24 SABITLENINCE duruyor mu?")
print("(NOTR adaylari zaten pumplamis olabilir; o zaman dusus etiketten degil pumptan)")
kov = [(-1e9,0,"dusen"),(0,10,"0-10%"),(10,25,"10-25%"),(25,1e9,">25%")]
print("%-10s %8s %10s %8s %10s %9s" % ("chg24", "N_NOTR", "NOTR r72", "N_LONG", "LONG r72", "fark"))
for lo, hi, ad in kov:
    n = [d["r72"] for d in kayit if d["smart"] == "NOTR" and d.get("chg24") is not None and lo <= d["chg24"] < hi]
    l = [d["r72"] for d in kayit if d["smart"] == "LONG" and d.get("chg24") is not None and lo <= d["chg24"] < hi]
    if len(n) < 10 or len(l) < 10:
        print("%-10s %8d %10s %8d %10s   N yetersiz" % (ad, len(n), "-", len(l), "-")); continue
    print("%-10s %8d %+10.2f %8d %+10.2f %+9.2f" % (ad, len(n), stx.mean(n), len(l), stx.mean(l), stx.mean(n)-stx.mean(l)))

print("\nKONTROL 3 — SANS OLCUMU (gun ici etiket karistirma, 2000 tur)")
gg = collections.defaultdict(list)
for d in kayit: gg[d["gun"]].append((d["smart"], d["r72"]))
ger_n = stx.mean([d["r72"] for d in kayit if d["smart"] == "NOTR"])
ger_d = stx.mean([d["r72"] for d in kayit if d["smart"] != "NOTR"])
gf = ger_n - ger_d
sahte = []
for _ in range(2000):
    A, B = [], []
    for gun, lst in gg.items():
        etk = [e for e, _n in lst]; nets = [n for _e, n in lst]
        random.shuffle(etk)
        for e, n in zip(etk, nets):
            (A if e == "NOTR" else B).append(n)
    if A and B: sahte.append(stx.mean(A)-stx.mean(B))
p = sum(1 for x in sahte if x <= gf)/len(sahte)
print("   NOTR %+.2f · diger %+.2f · FARK %+.2f" % (ger_n, ger_d, gf))
print("   sahte ort %+.2f (sd %.2f) · p = %.4f  -> %s"
      % (stx.mean(sahte), stx.pstdev(sahte), p,
         "SANSTAN FARKLI" if p < 0.05 else "SANSTAN AYIRT EDILEMIYOR"))
