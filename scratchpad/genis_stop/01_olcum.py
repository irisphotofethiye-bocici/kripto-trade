#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COK GENIS STOPLU GIRISLER ELENMELI MI?

ON_KAYIT_genis_stop_eleme.md · commit 885695b — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

🔴 Esik YALNIZ kesifte secilir; holdout bir kez sinar.
SALT-OKUNUR. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, sys, math, random, collections, statistics as stx
import importlib.util as il

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)
sp = il.spec_from_file_location(
    "ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)

IZGARA = [5.0, 6.0, 7.0, 8.0, 9.0, 10.0]     # on-kayit bolum 3
MIN_N_KESIF = 60
MIN_N_HOLD = 40
T_ESIK = -2.0
random.seed(20260906)


def gun_kumeli_t(rows, X):
    g = collections.defaultdict(lambda: ([], []))
    for x in rows:
        (g[x["gun"]][0] if x["stop_pct"] > X else g[x["gun"]][1]).append(x["R"])
    f = [stx.mean(a) - stx.mean(b) for a, b in g.values()
         if len(a) >= 2 and len(b) >= 2]
    if len(f) < 3:
        return 0.0, 0.0, len(f)
    m = stx.mean(f)
    se = stx.stdev(f) / math.sqrt(len(f))
    return m, ((m / se) if se > 0 else 0.0), len(f)


def esik_sec(kesif, alan="stop_pct"):
    """On-kayit bolum 3: kosulu saglayan EN KUCUK X."""
    print("   %-8s %7s %11s   %s" % ("X", "N", "ort R", "kosul (R<0 ve N>=%d)" % MIN_N_KESIF))
    secilen = None
    for X in IZGARA:
        ic = [x["R"] for x in kesif if x[alan] > X]
        if not ic:
            continue
        ok = (stx.mean(ic) < 0 and len(ic) >= MIN_N_KESIF)
        print("   >%-7.1f %7d %+11.4f   %s" % (X, len(ic), stx.mean(ic),
                                               "SAGLIYOR" if ok else "-"))
        if ok and secilen is None:
            secilen = X
    return secilen


def hat(kesif, hold, alan, etiket):
    """Tam boru hatti: kesifte esik sec -> holdoutta sina. -> (X, sonuc dict)"""
    print("### %s — KESIF'te esik secimi" % etiket)
    X = esik_sec(kesif, alan)
    if X is None:
        print("   -> kosulu saglayan X YOK")
        print()
        return None, None
    print("   -> SECILEN X = %.1f" % X)
    print()
    ic = [x["R"] for x in hold if x[alan] > X]
    dis = [x["R"] for x in hold if x[alan] <= X]
    if len(ic) < 5 or len(dis) < 5:
        print("   holdout yetersiz")
        return X, None
    fark = stx.mean(ic) - stx.mean(dis)
    m, t, ng = gun_kumeli_t([dict(x, stop_pct=x[alan]) for x in hold], X)
    mde = 2.8 * math.sqrt(stx.variance(ic) / len(ic) + stx.variance(dis) / len(dis))
    tum = stx.mean([x["R"] for x in hold])
    return X, {"ic": stx.mean(ic), "n_ic": len(ic), "dis": stx.mean(dis),
               "n_dis": len(dis), "fark": fark, "t": t, "gun": ng,
               "mde": mde, "tum": tum}


def main():
    print("=" * 100)
    print("GENIS STOP ELEME — ON_KAYIT_genis_stop_eleme.md (885695b)")
    print("=" * 100)
    rows = ar.veri_kur(ar.mumlar())
    gunler = sorted(set(x["gun"] for x in rows))
    ks = gunler[int(len(gunler) * ar.KESIF_PAY)]
    kesif = [x for x in rows if x["gun"] < ks]
    hold = [x for x in rows if x["gun"] >= ks]
    print("N=%d · KESIF %d · HOLDOUT %d" % (len(rows), len(kesif), len(hold)))
    print()

    X, r = hat(kesif, hold, "stop_pct", "GERCEK stop_pct")
    if X is None or r is None:
        print("ADAY YOK — olcum burada biter.")
        return

    print("### 🔓 HOLDOUT — tek gecis (X = %.1f)" % X)
    print("   hucre ICI  (stop > %.1f)  N=%4d  ort R %+.4f" % (X, r["n_ic"], r["ic"]))
    print("   hucre DISI               N=%4d  ort R %+.4f" % (r["n_dis"], r["dis"]))
    print("   TUMU                     N=%4d  ort R %+.4f" % (len(hold), r["tum"]))
    print("   fark %+.4f R · gun-kumeli t %+.2f (%d gun) · MDE %.4f"
          % (r["fark"], r["t"], r["gun"], r["mde"]))
    print()

    # --- NEGATIF KONTROL: stop_pct gun ici permute, AYNI HAT
    print("### NEGATIF KONTROL — stop_pct gun ici permute, AYNI BORU HATTI")
    for lst in (kesif, hold):
        g = collections.defaultdict(list)
        for i, x in enumerate(lst):
            g[x["gun"]].append(i)
        for gun, idx in g.items():
            v = [lst[i]["stop_pct"] for i in idx]
            random.shuffle(v)
            for i, val in zip(idx, v):
                lst[i]["sahte"] = val
    Xs, rs = hat(kesif, hold, "sahte", "SAHTE stop_pct")
    neg_bozuk = False
    if Xs is not None and rs is not None:
        print("   SAHTE holdout: ici %+.4f (N=%d) · fark %+.4f · t %+.2f"
              % (rs["ic"], rs["n_ic"], rs["fark"], rs["t"]))
        neg_bozuk = (rs["ic"] < 0 and rs["t"] <= T_ESIK)
    else:
        print("   sahte degiskende aday cikmadi -> yordam kendi basina eleme URETMIYOR")
    print()

    print("=" * 100)
    print("HUKUM — ON_KAYIT bolum 5")
    print("=" * 100)
    kalan = [x["R"] for x in hold if x["stop_pct"] <= X]
    W = {
        "W1 hucre ort R < 0": r["ic"] < 0,
        "W2 gun-kumeli t <= -2,0": r["t"] <= T_ESIK,
        "W3 |fark| > MDE": abs(r["fark"]) > r["mde"],
        "W4 holdout N >= %d" % MIN_N_HOLD: r["n_ic"] >= MIN_N_HOLD,
        "W5 kalan > tumu": stx.mean(kalan) > r["tum"],
    }
    for k, v in W.items():
        print("   %-28s %s" % (k, "GECTI" if v else "DUSTU"))
    print()
    if neg_bozuk:
        print("   🔴 NEGATIF KONTROL de eleme buldu -> yordam supheli, HUKUM YAZILMAZ.")
    elif all(W.values()):
        print("   🔑 ELEME HAKLI — stop > %%%.1f girisleri iki yarida da negatif." % X)
        print("   🔴 Bota KONMAZ: once portfoy simulasyonu (on-kayit bolum 8).")
        print("      ⚠️ Eleme islem sayisini AZALTIR — pencere hizi kontrol edilmeli.")
    elif not (W["W1 hucre ort R < 0"] and W["W2 gun-kumeli t <= -2,0"]):
        print("   HAKLI DEGIL — hipotez dustu.")
    else:
        print("   GOREMIYORUZ — isaret var, MDE asilmadi.")
    print()
    print("   ⚠️ Gecse bile bu KAYIP ONLEME kuralidir, KENAR DEGIL (on-kayit bolum 7).")
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
