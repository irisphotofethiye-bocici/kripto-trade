#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HEDEF R'YE BAGLANIRSA (m x stop) — sabit %10 yerine

ON_KAYIT_R_bagli_hedef.md · commit f309cd1 — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

m = 10 / medyan(stop_pct) — TURETILDI, ARANMADI.
SALT-OKUNUR. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, sys, math, collections, statistics as stx
import importlib.util as il

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)
sp = il.spec_from_file_location(
    "ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)

IZGARA = [2.0, 3.0, 4.0, 5.0]      # ek rapor — hukum kurmaz
T_ESIK = 2.0


def yol(d, ix, i0, g, stop, hedef):
    """-> (net R, isabet 0/1, sure saat, cikis 'STOP'/'HEDEF'/'ZAMAN')"""
    risk_pct = (g - stop) / g * 100.0
    if risk_pct <= 0:
        return None
    for j in range(i0 + 1, min(i0 + 1 + ar.ZAMAN_STOP, len(d))):
        b = d[j]
        if b["l"] <= stop:
            return (((stop / g - 1) * 100.0 - ar.MALIYET) / risk_pct, 0, j - i0, "STOP")
        if b["h"] >= hedef:
            return (((hedef / g - 1) * 100.0 - ar.MALIYET) / risk_pct, 1, j - i0, "HEDEF")
    j = min(i0 + ar.ZAMAN_STOP, len(d) - 1)
    if j <= i0:
        return None
    return (((d[j]["c"] / g - 1) * 100.0 - ar.MALIYET) / risk_pct, 0, j - i0, "ZAMAN")


def veri(mum):
    out, son = [], {}
    for l in io.open(os.path.join(KOK, "radar_archive.jsonl"),
                     encoding="utf-8", errors="ignore"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        s, p = r.get("sym"), r.get("price")
        if not s or not p or s not in mum or (r.get("score") or 0) < ar.SKOR_MIN:
            continue
        t = ar.ts_ms(r["ts"])
        if s in son and (t - son[s]) < ar.COOLDOWN * 3_600_000:
            continue
        d, ix = mum[s]
        i0 = ix.get(t)
        if i0 is None or i0 < ar.YAPI_BAR:
            continue
        stop = ar.stop_hesapla(d[i0 - ar.YAPI_BAR:i0], p)
        if stop is None:
            continue
        sf = (p - stop) / p * 100.0
        if sf < ar.ASGARI_STOP:
            continue
        son[s] = t
        out.append({"gun": r["ts"][:10], "d": d, "ix": ix, "i0": i0,
                    "g": p, "stop": stop, "sf": sf})
    return out


def ozet(rows, anahtar):
    R = [x[anahtar][0] for x in rows]
    hit = sum(x[anahtar][1] for x in rows)
    sure = [x[anahtar][2] for x in rows]
    zaman = sum(1 for x in rows if x[anahtar][3] == "ZAMAN")
    kaz = [v for v in R if v > 0]
    kay = [v for v in R if v <= 0]
    amp = (100.0 * (-stx.mean(kay)) / (stx.mean(kaz) - stx.mean(kay))
           if (kaz and kay) else float("nan"))
    return {"ortR": stx.mean(R), "isabet": 100.0 * hit / len(rows),
            "amp": amp, "sure": stx.median(sure),
            "zaman": 100.0 * zaman / len(rows)}


def fark_ist(rows, anahtar):
    f = [x[anahtar][0] - x["A0"][0] for x in rows]
    g = collections.defaultdict(list)
    for x, v in zip(rows, f):
        g[x["gun"]].append(v)
    gv = [stx.mean(v) for v in g.values()]
    m = stx.mean(gv)
    se = stx.stdev(gv) / math.sqrt(len(gv)) if len(gv) > 2 else 0
    mde = 2.8 * (stx.stdev(f) / math.sqrt(len(f))) if len(f) > 2 else float("inf")
    return stx.mean(f), (m / se if se else 0.0), mde, len(gv)


def main():
    print("=" * 100)
    print("HEDEF R'YE BAGLI (m x stop) — ON_KAYIT_R_bagli_hedef.md (f309cd1)")
    print("=" * 100)
    mum = ar.mumlar()
    rows = veri(mum)
    med = stx.median([x["sf"] for x in rows])
    M = 10.0 / med
    print("N=%d · medyan stop %.2f%% -> m = 10/%.2f = %.3f  (TURETILDI, ARANMADI)"
          % (len(rows), med, med, M))
    print()

    tam = []
    for x in rows:
        g, stop = x["g"], x["stop"]
        a0 = yol(x["d"], x["ix"], x["i0"], g, stop, g * 1.10)
        if a0 is None:
            continue
        x["A0"] = a0
        ok = True
        for m in [M] + IZGARA:
            h = g * (1 + m * (g - stop) / g)
            v = yol(x["d"], x["ix"], x["i0"], g, stop, h)
            if v is None:
                ok = False
                break
            x["R%.3f" % m] = v
        if ok:
            tam.append(x)
    rows = tam
    gunler = sorted(set(x["gun"] for x in rows))
    ks = gunler[int(len(gunler) * ar.KESIF_PAY)]
    kesif = [x for x in rows if x["gun"] < ks]
    hold = [x for x in rows if x["gun"] >= ks]
    print("simule edilen %d · KESIF %d · HOLDOUT %d" % (len(rows), len(kesif), len(hold)))
    print()

    ana = "R%.3f" % M
    print("### 1) KOL OZETLERI")
    print("   %-10s %-14s %10s %9s %12s %9s %8s"
          % ("pencere", "kol", "ort R", "isabet%", "amp.basabas", "sure(s)", "zaman%"))
    for ad, p in (("KESIF", kesif), ("HOLDOUT", hold), ("TUMU", rows)):
        for kol, et in (("A0", "A0 sabit %10"), (ana, "R(m=%.2f)" % M)):
            o = ozet(p, kol)
            print("   %-10s %-14s %+10.4f %8.1f%% %11.1f%% %9.0f %7.0f%%"
                  % (ad, et, o["ortR"], o["isabet"], o["amp"], o["sure"], o["zaman"]))
        print()

    print("### 2) 🔴 BIRINCIL — eslesmis fark R(m) - A0")
    print("   %-10s %11s %9s %9s %7s" % ("pencere", "fark R", "t", "MDE", "gun"))
    sonuc = {}
    for ad, p in (("KESIF", kesif), ("HOLDOUT", hold), ("TUMU", rows)):
        f, t, mde, ng = fark_ist(p, ana)
        sonuc[ad] = (f, t, mde)
        print("   %-10s %+11.4f %+9.2f %9.4f %7d" % (ad, f, t, mde, ng))
    print()

    print("### 3) EK — m izgarasi (HUKUM KURMAZ)")
    print("   %-8s %11s %11s %11s" % ("m", "KESIF fark", "HOLDOUT fark", "TUMU fark"))
    for m in IZGARA:
        k = "R%.3f" % m
        a = fark_ist(kesif, k)[0]
        b = fark_ist(hold, k)[0]
        c = fark_ist(rows, k)[0]
        print("   %-8.1f %+11.4f %+11.4f %+11.4f" % (m, a, b, c))
    print()

    print("### 4) 🔴 MEKANIZMA — stop dilimlerine gore fark (R(m) - A0)")
    v = sorted(hold, key=lambda z: z["sf"])
    n = len(v)
    print("   %-16s %6s %11s %11s %11s" % ("stop dilimi", "N", "A0 ort R", "R(m) ort R", "fark"))
    for i in range(5):
        p = v[i * n // 5:(i + 1) * n // 5]
        if len(p) < 10:
            continue
        a = stx.mean([x["A0"][0] for x in p])
        b = stx.mean([x[ana][0] for x in p])
        print("   %-16s %6d %+11.4f %+11.4f %+11.4f"
              % ("%.2f-%.2f" % (p[0]["sf"], p[-1]["sf"]), len(p), a, b, b - a))
    print()

    # --- HUKUM
    fh, th, mdeh = sonuc["HOLDOUT"]
    fk = sonuc["KESIF"][0]
    gd = collections.defaultdict(list)
    for x in hold:
        gd[x["gun"]].append(x[ana][0] - x["A0"][0])
    eniyi = sorted(gd, key=lambda g: -stx.mean(gd[g]))[:2]
    kalan = [x[ana][0] - x["A0"][0] for x in hold if x["gun"] not in eniyi]
    kalan = sorted(kalan)[:-5] if len(kalan) > 5 else kalan
    T = {
        "T1 holdout fark > 0": fh > 0,
        "T2 gun-kumeli t >= 2,0": th >= T_ESIK,
        "T3 |fark| > MDE": abs(fh) > mdeh,
        "T4 kesif+holdout ayni isaret": (fk > 0) == (fh > 0),
        "T5 yogunlasma": bool(kalan) and stx.mean(kalan) > 0,
    }
    print("=" * 100)
    print("HUKUM — ON_KAYIT bolum 7")
    print("=" * 100)
    for k, val in T.items():
        print("   %-32s %s" % (k, "GECTI" if val else "DUSTU"))
    print()
    if all(T.values()):
        print("   🔑 GECTI — hedefi R'ye baglamak ise yariyor.")
        print("   🔴 Bota KONMAZ: once portfoy simulasyonu (on-kayit bolum 10).")
        print("      ⚠️ Buyuk hedefler TUTMA SURESINI uzatir -> slot devri yavaslar.")
    elif not (T["T1 holdout fark > 0"] and T["T4 kesif+holdout ayni isaret"]):
        print("   DUSTU.")
    else:
        print("   GOREMIYORUZ — isaret var, MDE asilmadi.")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
