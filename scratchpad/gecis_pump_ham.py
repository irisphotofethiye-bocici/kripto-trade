#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GECIS x PUMP — HAM ILERI GETIRI.  On-kayit: ON_KAYIT_gecis_pump.md (commit 2e0c96f)

AsAMA 1 (HAM): stop YOK, hedef YOK, fonlama YOK.
Olcutler G1-G5 on-kayitta SABIT; burada yalniz hesaplanir.
SALT OKUMA — bot dosyalarina dokunmaz.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, glob, datetime, statistics, collections, math, random

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KL = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
CACHE = os.path.join(PROJE, "scratchpad", "poz_yol", "gecis_pump_tetikler.json")
OLU_BANT, HISTEREZIS = 2.0, 3
CHG24_ESIK, VOLX_ESIK = 0.10, 2.0
random.seed(20260825)


def gun_of(ms):
    return (datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(ms))).date()


# ---------------------------------------------------------------- rejim serisi
def rejim_serisi():
    with open(os.path.join(KL, "BTC.json"), encoding="utf-8") as f:
        bars = json.load(f)
    g = {}
    for b in bars:
        g[gun_of(b["t"])] = float(b["c"])
    G = sorted(g.items())
    out = []
    for i in range(len(G)):
        # [ONARIM 2026-08-25] ESKIDEN: hafta sozlugu TUM gunlerden BIR KEZ kuruluyordu,
        #   yani acik haftanin "kapanisi" o haftanin SON gunuydu -> ILERIYE BAKMA.
        #   Etiketi kaydiriyordu: 7 gecis 5'e dustu, 2025-05-06 -> 05-11 kaydi.
        #   Dogrusu: her gun icin haftalik seri YALNIZ o gune kadarki gunlerden kurulur
        #   (acik hafta = simdiye kadarki son kapanis), rejim_gecis_sayim.py ile ayni.
        hafta = {}
        for d, c in G[:i + 1]:
            hafta[d.isocalendar()[:2]] = (d, c)
        wc = [c for k, (d, c) in sorted(hafta.items())]
        sezon = "?"
        if len(wc) >= 21:
            w_ort = statistics.mean(wc[-21:-1])
            if wc[-1] > w_ort and wc[-1] - wc[-21] > 0:
                sezon = "BOGA"
            elif wc[-1] < w_ort and wc[-1] - wc[-21] < 0:
                sezon = "AYI"
            else:
                sezon = "NOTR"
        cl = [c for d, c in G[max(0, i - 59):i + 1]]
        ham = []
        for j in range(20, len(cl)):
            sma = statistics.mean(cl[j - 20:j])
            uz = (cl[j] - sma) / sma * 100
            ham.append("NOTR" if abs(uz) < OLU_BANT else ("BOGA" if uz > 0 else "AYI"))
        hava = ham[0] if ham else "NOTR"
        for j in range(len(ham)):
            if j < HISTEREZIS:
                hava = ham[j]
            else:
                pen = ham[j - HISTEREZIS + 1:j + 1]
                if all(x == pen[0] for x in pen):
                    hava = pen[0]
        if sezon == "AYI" and hava == "BOGA":
            f10 = "TEPKI_RALLISI"
        elif sezon == "BOGA" and hava == "BOGA":
            f10 = "TAM_BOGA"
        elif sezon == "AYI" and hava == "AYI":
            f10 = "DERIN_AYI"
        elif sezon == "BOGA" and hava == "AYI":
            f10 = "BOGA_DUZELTME"
        else:
            f10 = "BELIRSIZ"
        rej = "BOGA" if f10 == "TAM_BOGA" else ("AYI" if f10 in ("TEPKI_RALLISI", "DERIN_AYI") else "NOTR")
        if sezon != "?":
            out.append((G[i][0], rej))
    return out


REJ = rejim_serisi()
REJ_D = dict(REJ)
ILK, SON = REJ[0][0], REJ[-1][0]
GECIS = [REJ[i][0] for i in range(1, len(REJ))
         if REJ[i - 1][1] == "NOTR" and REJ[i][1] == "BOGA"]
EPIZOD_SON = {}
for d in GECIS:
    i = [k for k, (g, r) in enumerate(REJ) if g == d][0]
    j = i
    while j < len(REJ) and REJ[j][1] == "BOGA":
        j += 1
    EPIZOD_SON[d] = REJ[j - 1][0]


# ---------------------------------------------------------------- tetik tablosu
def tetikleri_uret():
    T = []
    dosyalar = sorted(glob.glob(os.path.join(KL, "*.json")))
    for n, p in enumerate(dosyalar):
        sym = os.path.basename(p)[:-5]
        try:
            with open(p, encoding="utf-8") as f:
                b = json.load(f)
        except Exception:
            continue
        if len(b) < 100:
            continue
        c = [float(x["c"]) for x in b]
        h_ = [float(x["h"]) for x in b]
        l_ = [float(x["l"]) for x in b]
        v = [float(x["v"]) for x in b]
        t = [x["t"] for x in b]
        i = 24
        while i < len(b) - 48:
            if c[i - 24] <= 0 or c[i] <= 0:
                i += 1
                continue
            chg = c[i] / c[i - 24] - 1.0
            vort = sum(v[i - 24:i]) / 24.0
            if chg >= CHG24_ESIK and vort > 0 and v[i] / vort >= VOLX_ESIK:
                g = gun_of(t[i])
                if ILK <= g <= SON:
                    tr = [max(h_[k] - l_[k], abs(h_[k] - c[k - 1]), abs(l_[k] - c[k - 1]))
                          for k in range(max(1, i - 13), i + 1)]
                    T.append(dict(sym=sym, gun=g.isoformat(),
                                  chg24=round(100.0 * chg, 3),
                                  vol_x=round(v[i] / vort, 3),
                                  f24=round(100.0 * (c[i + 24] / c[i] - 1.0), 4),
                                  f48=round(100.0 * (c[i + 48] / c[i] - 1.0), 4),
                                  atr=round(100.0 * (sum(tr) / len(tr)) / c[i], 4),
                                  rejim=REJ_D.get(g, "?")))
                i += 24          # tekillestirme: ayni sembolde 24 saat
                continue
            i += 1
        if (n + 1) % 100 == 0:
            print("   ... %d/%d sembol tarandi (tetik %d)" % (n + 1, len(dosyalar), len(T)),
                  flush=True)
    return T


if os.path.exists(CACHE):
    print("tetik tablosu onbellekten okunuyor: %s" % os.path.relpath(CACHE, PROJE))
    with open(CACHE, encoding="utf-8") as f:
        T = json.load(f)
else:
    print("tetik tablosu uretiliyor (567 sembol x 1h)...")
    T = tetikleri_uret()
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(T, f)
for x in T:
    x["_g"] = datetime.date.fromisoformat(x["gun"])

print("\nGECIS x PUMP — HAM ILERI GETIRI")
print("on-kayit ON_KAYIT_gecis_pump.md (2e0c96f) · olcutler SABIT")
print("=" * 112)
print("pencere %s .. %s   tetik toplam %d   sembol %d   gecis %d"
      % (ILK, SON, len(T), len(set(x["sym"] for x in T)), len(GECIS)))


def bant(x):
    for d in GECIS:
        fark = (x["_g"] - d).days
        if -3 <= fark < 0:
            return "ONCE", d
        if 0 <= fark < 3:
            return "T0", d
        if 3 <= fark < 7:
            return "T1", d
        if 7 <= fark and x["_g"] <= EPIZOD_SON[d]:
            return "T2", d
    return None, None


for x in T:
    x["bant"], x["gecis"] = bant(x)

# KONTROL: gecis i icin D_i oncesi 30 gunde, BOGA olmayan ve [D_i-3,D_i) disi
KONTROL = collections.defaultdict(list)
for d in GECIS:
    for x in T:
        f = (x["_g"] - d).days
        if -30 <= f < -3 and x["rejim"] != "BOGA":
            KONTROL[d].append(x)


def ozet(ad, w, alan="f24"):
    if not w:
        print("   %-12s N=0" % ad)
        return
    p = [x[alan] for x in w]
    print("   %-12s N=%5d   ham +24s: medyan %+7.3f%%  ort %+7.3f%%   pozitif %%%2.0f"
          "   ATR/fiyat med %5.2f%%"
          % (ad, len(w), statistics.median(p), sum(p) / len(p),
             100.0 * sum(1 for z in p if z > 0) / len(p),
             statistics.median([x["atr"] for x in w])))


print("\n1) BANT ORTALAMALARI (havuzlanmis — cikarim DEGIL, betimleme)")
print("-" * 112)
for b in ("ONCE", "T0", "T1", "T2"):
    ozet(b, [x for x in T if x["bant"] == b])
ozet("KONTROL", [z for d in GECIS for z in KONTROL[d]])
ozet("TUM tetik", T)


def t_paired(d):
    if len(d) < 2:
        return None, None
    m, sd = sum(d) / len(d), statistics.stdev(d)
    return m, (m / (sd / math.sqrt(len(d))) if sd else None)


print("\n2) G1/G2 — GECIS-KUMELI ESLESMIS FARK  (T0 - KONTROL, H=24s)  [BIRINCIL]")
print("-" * 112)
print("   %-12s %8s %11s | %8s %11s | %10s" % ("gecis", "T0 N", "T0 ort", "KON N", "KON ort", "fark"))
d1 = []
for d in GECIS:
    a = [x["f24"] for x in T if x["bant"] == "T0" and x["gecis"] == d]
    b = [x["f24"] for x in KONTROL[d]]
    if a and b:
        fark = sum(a) / len(a) - sum(b) / len(b)
        d1.append(fark)
        print("   %-12s %8d %+10.3f%% | %8d %+10.3f%% | %+9.3f" %
              (d, len(a), sum(a) / len(a), len(b), sum(b) / len(b), fark))
    else:
        print("   %-12s %8d %11s | %8d %11s | %10s" %
              (d, len(a), "-" if not a else "", len(b), "-" if not b else "", "VERI YOK"))
m1, t1 = t_paired(d1)
print("   " + "-" * 100)
print("   ESLESMIS FARK ort %+.3f puan   t = %s   (%d/%d gecis pozitif)"
      % (m1, "%+.2f" % t1 if t1 else "-", sum(1 for x in d1 if x > 0), len(d1)))
G1 = (m1 is not None and m1 >= 1.0 and t1 is not None and t1 >= 2.5)
G2 = sum(1 for x in d1 if x > 0) >= 5
print("   G1 (ort>=+1,0 VE t>=+2,5): %s" % ("GECTI" if G1 else "DUSTU"))
print("   G2 (>=5/7 pozitif)       : %s" % ("GECTI" if G2 else "DUSTU"))

print("\n3) G3 — CURUTME KAPISI: ONCE >= T0 mi (etiket gec mi kaliyor)")
print("-" * 112)
d3 = []
for d in GECIS:
    a = [x["f24"] for x in T if x["bant"] == "ONCE" and x["gecis"] == d]
    b = [x["f24"] for x in KONTROL[d]]
    if a and b:
        d3.append(sum(a) / len(a) - sum(b) / len(b))
m3, t3 = t_paired(d3)
print("   ONCE - KONTROL  ort %+.3f puan  t = %s  (%d/%d pozitif)"
      % (m3 if m3 else 0, "%+.2f" % t3 if t3 else "-",
         sum(1 for x in d3 if x > 0), len(d3)))
print("   T0   - KONTROL  ort %+.3f puan" % (m1 if m1 else 0))
G3_tetik = (m3 is not None and m1 is not None and m3 >= m1)
print("   G3: %s" % ("TETIKLEDI — kenar GECISTE degil, pump'in KENDISINDE" if G3_tetik
                     else "tetiklemedi (T0 > ONCE)"))

print("\n4) G4 — KARISTIRICI: chg24 x vol_x hucrelerinde ayakta mi")
print("-" * 112)


def cb(x):
    c = x["chg24"]
    return "10-20" if c < 20 else ("20-40" if c < 40 else "40+")


def vb(x):
    v = x["vol_x"]
    return "2-3" if v < 3 else ("3-5" if v < 5 else ("5-10" if v < 10 else "10+"))


t0all = [x for x in T if x["bant"] == "T0"]
konall = [z for d in GECIS for z in KONTROL[d]]
print("   %-8s %-8s %8s %11s | %8s %11s | %10s" %
      ("chg24", "vol_x", "T0 N", "T0 ort", "KON N", "KON ort", "fark"))
ayakta = 0
hucre = 0
for c_ in ("10-20", "20-40", "40+"):
    for v_ in ("2-3", "3-5", "5-10", "10+"):
        a = [x["f24"] for x in t0all if cb(x) == c_ and vb(x) == v_]
        b = [x["f24"] for x in konall if cb(x) == c_ and vb(x) == v_]
        if len(a) >= 10 and len(b) >= 10:
            hucre += 1
            f = sum(a) / len(a) - sum(b) / len(b)
            if f > 0:
                ayakta += 1
            print("   %-8s %-8s %8d %+10.3f%% | %8d %+10.3f%% | %+9.3f" %
                  (c_, v_, len(a), sum(a) / len(a), len(b), sum(b) / len(b), f))
G4 = ayakta >= 3
print("   G4 (>=3 hucrede ayni isaret): %s   -> %d/%d hucre pozitif"
      % ("GECTI" if G4 else "DUSTU", ayakta, hucre))

print("\n5) G5 — SANS: 7 SAHTE gecis tarihi x 2000 cekilis")
print("-" * 112)
gunler = [g for g, r in REJ if ILK + datetime.timedelta(days=35) <= g <= SON - datetime.timedelta(days=10)]
gun_tetik = collections.defaultdict(list)
for x in T:
    gun_tetik[x["_g"]].append(x)


def istatistik(dizi_gecis):
    ds = []
    for d in dizi_gecis:
        a = [x["f24"] for k in range(0, 3)
             for x in gun_tetik.get(d + datetime.timedelta(days=k), [])]
        b = [x["f24"] for k in range(-30, -3)
             for x in gun_tetik.get(d + datetime.timedelta(days=k), [])
             if x["rejim"] != "BOGA"]
        if a and b:
            ds.append(sum(a) / len(a) - sum(b) / len(b))
    return sum(ds) / len(ds) if ds else None


sahte = []
for _ in range(2000):
    while True:
        pick = sorted(random.sample(gunler, len(GECIS)))
        if all((pick[i + 1] - pick[i]).days >= 14 for i in range(len(pick) - 1)):
            break
    s = istatistik(pick)
    if s is not None:
        sahte.append(s)
sahte.sort()
ust = sum(1 for x in sahte if x >= (m1 or 0))
p5 = ust / len(sahte)
print("   sahte dagilim: medyan %+.3f  %%5 %+.3f  %%95 %+.3f  (N=%d cekilis)"
      % (statistics.median(sahte), sahte[int(0.05 * len(sahte))],
         sahte[int(0.95 * len(sahte))], len(sahte)))
print("   gercek T0-KONTROL %+.3f  ->  p = %.4f" % (m1 or 0, p5))
G5 = p5 <= 0.05
print("   G5 (p<=0,05): %s" % ("GECTI" if G5 else "DUSTU"))

print("\n6) IKINCIL — H=48 saat (KESIFSEL, Bonferroni |t|>=4,0)")
print("-" * 112)
d48 = []
for d in GECIS:
    a = [x["f48"] for x in T if x["bant"] == "T0" and x["gecis"] == d]
    b = [x["f48"] for x in KONTROL[d]]
    if a and b:
        d48.append(sum(a) / len(a) - sum(b) / len(b))
m48, t48 = t_paired(d48)
print("   T0 - KONTROL (48s)  ort %+.3f puan  t = %s  (%d/%d pozitif)"
      % (m48 or 0, "%+.2f" % t48 if t48 else "-", sum(1 for x in d48 if x > 0), len(d48)))

print("\n" + "=" * 112)
print("HUKUM")
print("=" * 112)
print("   G1 %s · G2 %s · G3 %s · G4 %s · G5 %s"
      % ("GECTI" if G1 else "DUSTU", "GECTI" if G2 else "DUSTU",
         "TETIKLEDI" if G3_tetik else "temiz", "GECTI" if G4 else "DUSTU",
         "GECTI" if G5 else "DUSTU"))
if G1 and G2 and G4 and G5 and not G3_tetik:
    print("   -> GECTI")
elif G1 and G2:
    print("   -> ZAYIF GECTI (G4/G5 dustu)")
else:
    print("   -> DUSTU")

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
