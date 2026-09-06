#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STOP MESAFESI — LONG POPULASYONUNDA

ON_KAYIT_stop_mesafesi_LONG.md · commit 883791a — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

Kollar dunku olcumden AYNEN: A · 1,5xATR · 2,5xATR · 4,0xATR
🔴 Merdiven monoton degilse betik CALISMAYI REDDEDER.
SALT-OKUNUR. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, sys, math, random, collections, statistics as stx
import importlib.util as il

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)
sp = il.spec_from_file_location(
    "ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)
import olcucu  # noqa: E402

KATLAR = [1.5, 2.5, 4.0]          # dunku olcumden AYNEN
BIRINCIL = 2.5
T_ESIK = 2.0
PERM = 2000
random.seed(20260906)


def yol(d, i0, g, stop):
    """-> (net R, net %, isabet, sure, cikis)"""
    h = g * 1.10
    risk = (g - stop) / g * 100.0
    if risk <= 0:
        return None
    for j in range(i0 + 1, min(i0 + 1 + ar.ZAMAN_STOP, len(d))):
        b = d[j]
        if b["l"] <= stop:
            n = (stop / g - 1) * 100.0 - ar.MALIYET
            return (n / risk, n, 0, j - i0, "STOP")
        if b["h"] >= h:
            n = (h / g - 1) * 100.0 - ar.MALIYET
            return (n / risk, n, 1, j - i0, "HEDEF")
    j = min(i0 + ar.ZAMAN_STOP, len(d) - 1)
    if j <= i0:
        return None
    n = (d[j]["c"] / g - 1) * 100.0 - ar.MALIYET
    return (n / risk, n, 0, j - i0, "ZAMAN")


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
        bars = d[i0 - ar.YAPI_BAR:i0]
        stopA = ar.stop_hesapla(bars, p)
        if stopA is None:
            continue
        if (p - stopA) / p * 100.0 < ar.ASGARI_STOP:
            continue          # A kolunun kapisi -> ESLESME TABANI
        atr = olcucu.atr(bars, period=14)
        if atr <= 0:
            continue
        son[s] = t
        rec = {"gun": r["ts"][:10], "sym": s, "g": p,
               "stopA_pct": (p - stopA) / p * 100.0}
        v = yol(d, i0, p, stopA)
        if v is None:
            continue
        rec["A"] = v
        rec["A_stop"] = (p - stopA) / p * 100.0
        ok = True
        for k in KATLAR:
            st = p - k * atr
            if st <= 0:
                ok = False
                break
            vv = yol(d, i0, p, st)
            if vv is None:
                ok = False
                break
            rec["K%.1f" % k] = vv
            rec["K%.1f_stop" % k] = (p - st) / p * 100.0
        if ok:
            out.append(rec)
    return out


def gun_t(rows, kol):
    f = [x[kol][0] - x["A"][0] for x in rows]
    g = collections.defaultdict(list)
    for x, v in zip(rows, f):
        g[x["gun"]].append(v)
    gv = [stx.mean(v) for v in g.values()]
    m = stx.mean(gv)
    se = stx.stdev(gv) / math.sqrt(len(gv)) if len(gv) > 2 else 0
    mde = 2.8 * (stx.stdev(f) / math.sqrt(len(f))) if len(f) > 2 else float("inf")
    return stx.mean(f), (m / se if se else 0.0), mde, gv


def main():
    print("=" * 100)
    print("STOP MESAFESI — LONG · ON_KAYIT_stop_mesafesi_LONG.md (883791a)")
    print("=" * 100)
    rows = veri(ar.mumlar())
    gunler = sorted(set(x["gun"] for x in rows))
    ks = gunler[int(len(gunler) * ar.KESIF_PAY)]
    kesif = [x for x in rows if x["gun"] < ks]
    hold = [x for x in rows if x["gun"] >= ks]
    print("N=%d · KESIF %d · HOLDOUT %d" % (len(rows), len(kesif), len(hold)))
    print()

    # --- ZORUNLU SINAMA: merdiven monoton mu?
    med = [stx.median([x["A_stop"] for x in rows])]
    for k in KATLAR:
        med.append(stx.median([x["K%.1f_stop" % k] for x in rows]))
    print("### 0) ZORUNLU SINAMA — merdiven monoton mu?")
    print("   A %.2f%% -> 1.5x %.2f%% -> 2.5x %.2f%% -> 4.0x %.2f%%"
          % tuple(med))
    if not all(med[i] <= med[i + 1] + 1e-9 for i in range(len(med) - 1)):
        print("   🔴 MONOTON DEGIL -> BETIK CALISMAYI REDDEDIYOR")
        return
    print("   -> monoton ✔")
    print()

    kollar = ["A"] + ["K%.1f" % k for k in KATLAR]
    ad = {"A": "A (mevcut)", "K1.5": "1.5x ATR", "K2.5": "2.5x ATR", "K4.0": "4.0x ATR"}

    print("### 1) KOL OZETLERI")
    print("   %-10s %-12s %9s %10s %9s %9s %9s %8s %8s"
          % ("pencere", "kol", "stop%", "ort R", "net%", "stop-ol%", "isabet%", "saat", "zaman%"))
    for pad, p in (("KESIF", kesif), ("HOLDOUT", hold), ("TUMU", rows)):
        for kol in kollar:
            R = [x[kol][0] for x in p]
            N = [x[kol][1] for x in p]
            st = 100.0 * sum(1 for x in p if x[kol][4] == "STOP") / len(p)
            hi = 100.0 * sum(x[kol][2] for x in p) / len(p)
            za = 100.0 * sum(1 for x in p if x[kol][4] == "ZAMAN") / len(p)
            sp_ = stx.median([x["A_stop" if kol == "A" else kol + "_stop"] for x in p])
            print("   %-10s %-12s %8.2f%% %+10.4f %+8.3f%% %8.1f%% %8.1f%% %8.0f %7.0f%%"
                  % (pad, ad[kol], sp_, stx.mean(R), stx.mean(N), st, hi,
                     stx.median([x[kol][3] for x in p]), za))
        print()

    print("### 2) 🔴 ESLESMIS FARK (kol - A)")
    print("   %-10s %-12s %11s %9s %9s   %s" % ("pencere", "kol", "fark R", "t", "MDE", "net% fark"))
    hol_gv = {}
    sonuc = {}
    for pad, p in (("KESIF", kesif), ("HOLDOUT", hold)):
        for kol in kollar[1:]:
            f, t, mde, gv = gun_t(p, kol)
            nf = stx.mean([x[kol][1] - x["A"][1] for x in p])
            print("   %-10s %-12s %+11.4f %+9.2f %9.4f   %+8.3f%%"
                  % (pad, ad[kol], f, t, mde, nf))
            if pad == "HOLDOUT":
                hol_gv[kol] = gv
                sonuc[kol] = (f, t, mde)
        print()

    # --- U5 PERMUTASYON: gun bazinda isaret cevirme, uc kolun max|t|
    print("### 3) PERMUTASYON (gun bazinda isaret cevirme, %d tur) — U5" % PERM)
    gercek_max = max(abs(sonuc[k][1]) for k in sonuc)
    asan = 0
    for _ in range(PERM):
        mx = 0.0
        for k, gv in hol_gv.items():
            s = [v * (1 if random.random() < 0.5 else -1) for v in gv]
            m = stx.mean(s)
            se = stx.stdev(s) / math.sqrt(len(s)) if len(s) > 2 else 0
            mx = max(mx, abs(m / se) if se else 0)
        if mx >= gercek_max:
            asan += 1
    p_deger = asan / PERM
    print("   gercek max|t| = %.2f  ·  p = %.4f" % (gercek_max, p_deger))
    print()

    # --- KARISTIRICI TESTI
    print("### 4) 🔴 KARISTIRICI TESTI — stop dilimlerine gore (2.5x - A), HOLDOUT")
    v = sorted(hold, key=lambda z: z["A_stop"])
    n = len(v)
    print("   %-16s %6s %11s %11s %11s" % ("A stop dilimi", "N", "A ort R", "2.5x ort R", "fark"))
    ayni = 0
    for i in range(5):
        pp = v[i * n // 5:(i + 1) * n // 5]
        if len(pp) < 10:
            continue
        a = stx.mean([x["A"][0] for x in pp])
        b = stx.mean([x["K2.5"][0] for x in pp])
        if b - a > 0:
            ayni += 1
        print("   %-16s %6d %+11.4f %+11.4f %+11.4f"
              % ("%.2f-%.2f" % (pp[0]["A_stop"], pp[-1]["A_stop"]), len(pp), a, b, b - a))
    print("   -> 5 dilimin %d'inde 2.5x DAHA IYI" % ayni)
    print()

    # --- HUKUM
    fh, th, mdeh = sonuc["K%.1f" % BIRINCIL]
    fk = gun_t(kesif, "K%.1f" % BIRINCIL)[0]
    U = {
        "U1 holdout fark > 0": fh > 0,
        "U2 gun-kumeli t >= 2,0": th >= T_ESIK,
        "U3 |fark| > MDE": abs(fh) > mdeh,
        "U4 kesif+holdout ayni isaret": (fk > 0) == (fh > 0),
        "U5 permutasyon p < 0,05": p_deger < 0.05,
    }
    print("=" * 100)
    print("HUKUM — ON_KAYIT bolum 6 (birincil kol %.1fx)" % BIRINCIL)
    print("=" * 100)
    for k, val in U.items():
        print("   %-32s %s" % (k, "GECTI" if val else "DUSTU"))
    print()
    if all(U.values()):
        print("   🔑 GECTI — LONG'da stopu genisletmek ise yariyor.")
        print("   🔴 Bota KONMAZ: once portfoy simulasyonu (on-kayit bolum 9).")
    elif not (U["U1 holdout fark > 0"] and U["U4 kesif+holdout ayni isaret"]):
        print("   DUSTU.")
    else:
        print("   GOREMIYORUZ — isaret var, esik asilmadi.")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
