#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HAREKET BITINCE TERS YON (SHORT) — HAM ILERI GETIRI.
On-kayit: ON_KAYIT_hareket_bitisi_short.md (commit d9cbdd7). Olcutler H1-H5 SABIT.

A = hareket-bitis bari (son M saatte yeni tepe yok)  -> SHORT
B = ayni olayda bitis OLMAYAN barlar (hala yeni tepe yapiyor), kova-eslesmeli
C = tetik barinin kendisi ("pump'i hemen shortla")

H3 BELIRLEYICI: gecen sure x kumulatif kazanc sabitlendiginde A>B ayakta mi.
Dusrse hukum OTOMATIK DUSER.
SALT OKUMA.
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
CHG24_ESIK, VOLX_ESIK = 0.10, 2.0
UFUK = 24            # H = 24 saat
TAKIP = 48           # bitis en fazla 48 saat icinde aranir
M_BIRINCIL = 6
M_LISTE = [3, 6, 12]
MALIYET = 0.1726 * 2
BAS = datetime.date(2024, 12, 23)
SON = datetime.date(2026, 8, 25)
random.seed(20260825)


def gun_of(ms):
    return (datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(ms))).date()


def gecen_b(g):
    return "1-6" if g <= 6 else ("7-12" if g <= 12 else ("13-24" if g <= 24 else "25-48"))


def kazanc_b(k):
    return ("<-5" if k < -5 else ("-5..0" if k < 0 else ("0..5" if k < 5
            else ("5..15" if k < 15 else ">15"))))


def tara(M):
    """Donus: armA, armC (satir listeleri) · kova toplaclari · olay getiri listeleri."""
    armA, armC = [], []
    kova = collections.defaultdict(lambda: [0, 0.0])          # (ay,gb,kb,arm) -> [n,sum]
    olay_ret = []
    surer = 0
    dosyalar = sorted(glob.glob(os.path.join(KL, "*.json")))
    for nn, p in enumerate(dosyalar):
        sym = os.path.basename(p)[:-5]
        try:
            with open(p, encoding="utf-8") as f:
                b = json.load(f)
        except Exception:
            continue
        if len(b) < 200:
            continue
        c = [float(x["c"]) for x in b]
        hi = [float(x["h"]) for x in b]
        lo = [float(x["l"]) for x in b]
        v = [float(x["v"]) for x in b]
        t = [x["t"] for x in b]
        i = 24
        ust = len(b) - (TAKIP + UFUK + 1)
        while i < ust:
            if c[i - 24] <= 0 or c[i] <= 0:
                i += 1
                continue
            chg = c[i] / c[i - 24] - 1.0
            vort = sum(v[i - 24:i]) / 24.0
            if not (chg >= CHG24_ESIK and vort > 0 and v[i] / vort >= VOLX_ESIK):
                i += 1
                continue
            g = gun_of(t[i])
            if not (BAS <= g <= SON):
                i += 24
                continue
            ay = g.strftime("%Y-%m")
            tr = [max(hi[k] - lo[k], abs(hi[k] - c[k - 1]), abs(lo[k] - c[k - 1]))
                  for k in range(max(1, i - 13), i + 1)]
            atr = 100.0 * (sum(tr) / len(tr)) / c[i]

            # C: tetik barinda SHORT
            armC.append(dict(ay=ay, ret=-100.0 * (c[i + UFUK] / c[i] - 1.0), atr=atr, sym=sym))

            # ileri yurut: kosan tepe + bitis tespiti
            hh = [hi[i]]
            for j in range(i + 1, i + TAKIP + 1):
                hh.append(max(hh[-1], hi[j]))
            bitis_idx = None
            rets = []
            for j in range(i + 1, i + TAKIP + 1):
                off = j - i
                ret = -100.0 * (c[j + UFUK] / c[j] - 1.0)
                kaz = 100.0 * (c[j] / c[i] - 1.0)
                # bitis kosulu: son M barda YENI TEPE YOK
                bitti = (off > M) and (hh[off] == hh[off - M])
                rets.append(ret)
                if bitti and bitis_idx is None:
                    bitis_idx = off
                    armA.append(dict(ay=ay, ret=ret, gecen=off, kaz=kaz, atr=atr,
                                     sym=sym, tepeden=100.0 * (c[j] / hh[off] - 1.0)))
                    kova[(ay, gecen_b(off), kazanc_b(kaz), "A")][0] += 1
                    kova[(ay, gecen_b(off), kazanc_b(kaz), "A")][1] += ret
                elif not bitti:
                    kova[(ay, gecen_b(off), kazanc_b(kaz), "B")][0] += 1
                    kova[(ay, gecen_b(off), kazanc_b(kaz), "B")][1] += ret
            if bitis_idx is None:
                surer += 1
            olay_ret.append(rets)
            i += 24
        if (nn + 1) % 150 == 0:
            print("   ... %d/%d sembol (olay %d)" % (nn + 1, len(dosyalar), len(armC)), flush=True)
    return armA, armC, kova, olay_ret, surer


def ay_t(ciftler, esik_n=30):
    """ciftler: {ay: (listeA, listeC)} -> (ort fark, t, poz ay, toplam ay)"""
    d = []
    for ay, (a, cc) in sorted(ciftler.items()):
        if len(a) >= esik_n and len(cc) >= esik_n:
            d.append(sum(a) / len(a) - sum(cc) / len(cc))
    if len(d) < 2:
        return None, None, 0, len(d)
    m, sd = sum(d) / len(d), statistics.stdev(d)
    return m, (m / (sd / math.sqrt(len(d))) if sd else None), sum(1 for x in d if x > 0), len(d)


print("HAREKET BITINCE TERS YON (SHORT) — HAM +24s")
print("on-kayit ON_KAYIT_hareket_bitisi_short.md (d9cbdd7) · olcutler SABIT")
print("=" * 116)

SONUC = {}
for M in M_LISTE:
    etiket = "BIRINCIL" if M == M_BIRINCIL else "kesifsel"
    print("\n%s M = %d saat  (%s)" % ("=" * 30, M, etiket))
    armA, armC, kova, olay_ret, surer = tara(M)
    SONUC[M] = (armA, armC, kova, olay_ret, surer)
    print("   olay %d · A (bitis bulundu) %d · hala suruyor %d (%%%.1f)"
          % (len(armC), len(armA), surer, 100.0 * surer / max(1, len(armC))))
    a = [x["ret"] for x in armA]
    cc = [x["ret"] for x in armC]
    print("   %-26s N=%6d  ort %+7.3f%%  medyan %+7.3f%%  kazanan %%%2.0f  ATR med %5.2f%%"
          % ("A  hareket bitti", len(a), sum(a) / len(a), statistics.median(a),
             100.0 * sum(1 for x in a if x > 0) / len(a),
             statistics.median([x["atr"] for x in armA])))
    print("   %-26s N=%6d  ort %+7.3f%%  medyan %+7.3f%%  kazanan %%%2.0f  ATR med %5.2f%%"
          % ("C  tetikte short", len(cc), sum(cc) / len(cc), statistics.median(cc),
             100.0 * sum(1 for x in cc if x > 0) / len(cc),
             statistics.median([x["atr"] for x in armC])))

armA, armC, kova, olay_ret, surer = SONUC[M_BIRINCIL]
A = [x["ret"] for x in armA]
C = [x["ret"] for x in armC]

print("\n" + "=" * 116)
print("BIRINCIL ANALIZ (M = %d saat)" % M_BIRINCIL)
print("=" * 116)

print("\nH1 — A - C, ay-kumeli")
print("-" * 116)
ay_a = collections.defaultdict(list)
ay_c = collections.defaultdict(list)
for x in armA:
    ay_a[x["ay"]].append(x["ret"])
for x in armC:
    ay_c[x["ay"]].append(x["ret"])
ciftler = {ay: (ay_a.get(ay, []), ay_c.get(ay, [])) for ay in set(ay_a) | set(ay_c)}
m1, t1, poz1, n1 = ay_t(ciftler)
print("   havuzlanmis  A %+7.3f%%   C %+7.3f%%   fark %+7.3f puan"
      % (sum(A) / len(A), sum(C) / len(C), sum(A) / len(A) - sum(C) / len(C)))
print("   ay-kumeli    fark ort %+7.3f   t = %s   (%d/%d ay pozitif)"
      % (m1 or 0, "%+.2f" % t1 if t1 else "-", poz1, n1))
H1 = (m1 is not None and m1 >= 0.5 and t1 is not None and t1 >= 2.5)
print("   H1 (>=+0,5 VE t>=+2,5): %s" % ("GECTI" if H1 else "DUSTU"))

print("\nH2 — KUYRUK: SHORT getirisi < -%20 olan pay (devam felaketi)")
print("-" * 116)
ka = sum(1 for x in A if x < -20) / len(A)
kc = sum(1 for x in C if x < -20) / len(C)
print("   A %%%.2f   C %%%.2f   ->  A/C = %.3f  (esik <= 0,600)"
      % (100 * ka, 100 * kc, ka / kc if kc else float("inf")))
print("   jackpot (> +%%20): A %%%.2f  C %%%.2f"
      % (100 * sum(1 for x in A if x > 20) / len(A), 100 * sum(1 for x in C if x > 20) / len(C)))
H2 = (kc > 0 and ka / kc <= 0.60)
print("   H2: %s" % ("GECTI" if H2 else "DUSTU"))

print("\nH3 — BELIRLEYICI: gecen x kazanc SABITLENINCE A > B ayakta mi")
print("-" * 116)
kb_a = collections.defaultdict(lambda: [0, 0.0])
kb_b = collections.defaultdict(lambda: [0, 0.0])
for (ay, gb, kb, arm), (n, s) in kova.items():
    (kb_a if arm == "A" else kb_b)[(gb, kb)][0] += n
    (kb_a if arm == "A" else kb_b)[(gb, kb)][1] += s
print("   %-8s %-8s %8s %10s | %8s %10s | %9s" %
      ("gecen", "kazanc", "A N", "A ort", "B N", "B ort", "fark"))
ayakta, hucre, wsum, wn = 0, 0, 0.0, 0
for gb in ("1-6", "7-12", "13-24", "25-48"):
    for kb in ("<-5", "-5..0", "0..5", "5..15", ">15"):
        na, sa = kb_a.get((gb, kb), [0, 0.0])
        nb, sb = kb_b.get((gb, kb), [0, 0.0])
        if na >= 50 and nb >= 50:
            hucre += 1
            f = sa / na - sb / nb
            if f > 0:
                ayakta += 1
            wsum += na * f
            wn += na
            print("   %-8s %-8s %8d %+9.3f%% | %8d %+9.3f%% | %+8.3f" %
                  (gb, kb, na, sa / na, nb, sb / nb, f))
oran = ayakta / hucre if hucre else 0
print("   -> %d/%d kovada A onde (%%%.0f)   N-agirlikli A-B = %+.3f puan"
      % (ayakta, hucre, 100 * oran, wsum / wn if wn else 0))
# ay-kumeli, kova-duzeltilmis
ay_fark = collections.defaultdict(lambda: [0.0, 0])
ay_kova = collections.defaultdict(dict)
for (ay, gb, kb, arm), (n, s) in kova.items():
    ay_kova[ay].setdefault((gb, kb), {})[arm] = (n, s)
d3 = []
for ay, hh in sorted(ay_kova.items()):
    num, den = 0.0, 0
    for k, v in hh.items():
        if "A" in v and "B" in v and v["A"][0] >= 5 and v["B"][0] >= 20:
            na, sa = v["A"]
            nb, sb = v["B"]
            num += na * (sa / na - sb / nb)
            den += na
    if den >= 30:
        d3.append(num / den)
if len(d3) >= 2:
    m3, sd3 = sum(d3) / len(d3), statistics.stdev(d3)
    t3 = m3 / (sd3 / math.sqrt(len(d3))) if sd3 else None
else:
    m3, t3 = None, None
print("   ay-kumeli kova-duzeltilmis A-B: ort %+.3f  t = %s  (%d/%d ay pozitif)"
      % (m3 or 0, "%+.2f" % t3 if t3 else "-",
         sum(1 for x in d3 if x > 0), len(d3)))
H3 = (oran >= 0.60 and (wsum / wn if wn else 0) > 0 and t3 is not None and t3 >= 2.0)
print("   H3: %s" % ("GECTI" if H3 else "DUSTU  ->  HUKUM OTOMATIK DUSER"))

print("\nH4 — SANS: olay basina RASTGELE giris bari x 2000 cekilis")
print("-" * 116)
sahte = []
for _ in range(2000):
    s = [r[random.randrange(len(r))] for r in olay_ret if r]
    sahte.append(sum(s) / len(s))
sahte.sort()
gercek = sum(A) / len(A)
ust = sum(1 for x in sahte if x >= gercek)
p4 = ust / len(sahte)
print("   sahte dagilim: medyan %+7.3f  %%5 %+7.3f  %%95 %+7.3f"
      % (statistics.median(sahte), sahte[int(0.05 * len(sahte))], sahte[int(0.95 * len(sahte))]))
print("   gercek A ort %+7.3f  ->  p = %.4f" % (gercek, p4))
H4 = p4 <= 0.05
print("   H4: %s" % ("GECTI" if H4 else "DUSTU"))

print("\nH5 — MALIYET SONRASI (rapor; fonlama HARIC, SHORT lehine olurdu)")
print("-" * 116)
print("   A  brut %+7.3f%%  - maliyet %.3f  =  NET %+7.3f%%"
      % (gercek, MALIYET, gercek - MALIYET))
print("   C  brut %+7.3f%%  - maliyet %.3f  =  NET %+7.3f%%"
      % (sum(C) / len(C), MALIYET, sum(C) / len(C) - MALIYET))
H5 = (gercek - MALIYET) > 0
print("   H5: %s" % ("GECTI" if H5 else "DUSTU"))

print("\nEK — kesifsel M degerleri (Bonferroni |t| >= 3,0)")
print("-" * 116)
for M in M_LISTE:
    aA, aC, _, _, _ = SONUC[M]
    a = [x["ret"] for x in aA]
    cc = [x["ret"] for x in aC]
    ya = collections.defaultdict(list)
    yc = collections.defaultdict(list)
    for x in aA:
        ya[x["ay"]].append(x["ret"])
    for x in aC:
        yc[x["ay"]].append(x["ret"])
    mm, tt, pz, nn2 = ay_t({ay: (ya.get(ay, []), yc.get(ay, [])) for ay in set(ya) | set(yc)})
    print("   M=%-3d  A ort %+7.3f%% (N=%5d)  C ort %+7.3f%%  fark %+6.3f  t=%s  (%d/%d ay)"
          % (M, sum(a) / len(a), len(a), sum(cc) / len(cc), mm or 0,
             "%+.2f" % tt if tt else "-", pz, nn2))

print("\n" + "=" * 116)
print("HUKUM")
print("=" * 116)
print("   H1 %s · H2 %s · H3 %s · H4 %s · H5 %s"
      % (*("GECTI" if z else "DUSTU" for z in (H1, H2, H3, H4, H5)),))
if not H3:
    print("   -> DUSTU  (H3 belirleyici: sinyal 'gecen sure / kazanc'in vekili)")
elif H1 and H2 and H3 and H4:
    print("   -> GECTI")
elif H1 and H3 and H4:
    print("   -> ZAYIF GECTI (H2 dustu)")
else:
    print("   -> DUSTU")

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
