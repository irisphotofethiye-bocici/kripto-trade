#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STOP GENISLIGI ile GETIRI ARASINDA YON VAR MI?

ON_KAYIT_stop_genislik_yonu.md · commit 162246b — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

🔴 HOLDOUT bir kez okunur. Ikinci hipotez sokulmaz.
SALT-OKUNUR. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, sys, math, collections, statistics as stx

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)
import importlib.util as il
sp = il.spec_from_file_location(
    "ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)

DILIM = 5
T_ESIK = 2.0            # on-kayit bolum 5: TEK birincil karsilastirma


def siralar(v):
    n = len(v)
    p = sorted(range(n), key=lambda i: v[i])
    r = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and v[p[j + 1]] == v[p[i]]:
            j += 1
        o = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            r[p[k]] = o
        i = j + 1
    return r


def spearman(x, y):
    if len(x) < 10:
        return 0.0
    rx, ry = siralar(x), siralar(y)
    mx, my = stx.mean(rx), stx.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return (num / den) if den else 0.0


def gun_kumeli_t(rows, esik):
    """Medyan bolme: stop GENIS vs DAR, gunluk farklarin t'si."""
    g = collections.defaultdict(lambda: ([], []))
    for x in rows:
        (g[x["gun"]][0] if x["stop_pct"] >= esik else g[x["gun"]][1]).append(x["R"])
    f = [stx.mean(a) - stx.mean(b) for a, b in g.values()
         if len(a) >= 2 and len(b) >= 2]
    if len(f) < 3:
        return 0.0, 0.0, len(f)
    m = stx.mean(f)
    se = stx.stdev(f) / math.sqrt(len(f))
    return m, ((m / se) if se > 0 else 0.0), len(f)


def dilim_tablo(rows, ad):
    v = sorted(rows, key=lambda x: x["stop_pct"])
    n = len(v)
    print("   --- %s (N=%d) ---" % (ad, n))
    print("   %-16s %6s %10s %9s %9s %11s %11s %8s"
          % ("stop dilimi", "N", "ort stop%", "ort R", "isabet%", "basabas AMP",
             "basabas FRM", "zaman%"))
    for i in range(DILIM):
        p = v[i * n // DILIM:(i + 1) * n // DILIM]
        if len(p) < 10:
            continue
        R = [x["R"] for x in p]
        sp_ = stx.mean([x["stop_pct"] for x in p])
        hit = 100.0 * sum(x["hit"] for x in p) / len(p)
        # 🔴 AMPIRIK basabas: R>0 olan islemlerin ortalama kazanci ve
        #    R<=0 olanlarin ortalama kaybindan turetilir (zaman stopu DAHIL)
        kaz = [x["R"] for x in p if x["R"] > 0]
        kay = [x["R"] for x in p if x["R"] <= 0]
        if kaz and kay:
            amp = 100.0 * (-stx.mean(kay)) / (stx.mean(kaz) - stx.mean(kay))
        else:
            amp = float("nan")
        frm = 100.0 / (1.0 + 10.0 / sp_) if sp_ else float("nan")
        zaman = 100.0 * sum(1 for x in p if x["hit"] == 0 and x["R"] > -0.9) / len(p)
        print("   %-16s %6d %10.2f %+9.4f %8.1f%% %10.1f%% %10.1f%% %7.0f%%"
              % ("%.2f-%.2f" % (p[0]["stop_pct"], p[-1]["stop_pct"]),
                 len(p), sp_, stx.mean(R), hit, amp, frm, zaman))


def main():
    print("=" * 104)
    print("STOP GENISLIGI -> GETIRI · ON_KAYIT_stop_genislik_yonu.md (162246b)")
    print("🔴 Hipotez KOSUMDAN ONCE: rho(stop_pct, R) > 0 (genis stop daha iyi)")
    print("=" * 104)

    mum = ar.mumlar()
    rows = ar.veri_kur(mum)
    gunler = sorted(set(x["gun"] for x in rows))
    kes_son = gunler[int(len(gunler) * ar.KESIF_PAY)]
    kesif = [x for x in rows if x["gun"] < kes_son]
    hold = [x for x in rows if x["gun"] >= kes_son]
    print("toplam %d · KESIF %d (%s..%s) · HOLDOUT %d (%s..%s)"
          % (len(rows), len(kesif), gunler[0], kes_son, len(hold), kes_son, gunler[-1]))
    print()

    print("### 1) DILIM TABLOSU (ek rapor, olcut DEGIL)")
    dilim_tablo(kesif, "KESIF")
    print()
    dilim_tablo(hold, "HOLDOUT")
    print()
    print("   basabas AMP = ampirik (kazanan ort / kaybeden ort ile) — ZAMAN STOPU DAHIL")
    print("   basabas FRM = 1/(1+hedef/stop) formulu — YALNIZ ikili sonucta gecerli")
    print("   zaman%% = hedefe de stopa da degmeden kapanan islem orani")
    print()

    print("### 2) 🔴 BIRINCIL — HOLDOUT")
    x = [r["stop_pct"] for r in hold]
    y = [r["R"] for r in hold]
    rho_h = spearman(x, y)
    rho_k = spearman([r["stop_pct"] for r in kesif], [r["R"] for r in kesif])
    med = stx.median(x)
    m, t, ng = gun_kumeli_t(hold, med)
    genis = [r["R"] for r in hold if r["stop_pct"] >= med]
    dar = [r["R"] for r in hold if r["stop_pct"] < med]
    fark = stx.mean(genis) - stx.mean(dar)
    mde = 2.8 * math.sqrt(stx.variance(genis) / len(genis)
                          + stx.variance(dar) / len(dar))
    v = sorted(hold, key=lambda z: z["stop_pct"])
    ust = [z["R"] for z in v[4 * len(v) // 5:]]

    print("   rho(stop_pct, R)   KESIF %+.4f   HOLDOUT %+.4f" % (rho_k, rho_h))
    print("   medyan stop %.2f%% -> GENIS ort R %+.4f (N=%d) · DAR %+.4f (N=%d)"
          % (med, stx.mean(genis), len(genis), stx.mean(dar), len(dar)))
    print("   fark %+.4f R · gun-kumeli t %+.2f (%d gun) · MDE %.4f"
          % (fark, t, ng, mde))
    print("   en genis dilim ort R %+.4f (N=%d)" % (stx.mean(ust), len(ust)))
    print()

    P = {
        "P1 holdout rho > 0": rho_h > 0,
        "P2 gun-kumeli t >= %.1f" % T_ESIK: t >= T_ESIK,
        "P3 |fark| > MDE": abs(fark) > mde,
        "P4 kesif+holdout ayni isaret": (rho_k > 0) == (rho_h > 0),
        "P5 en genis dilim R > 0": stx.mean(ust) > 0,
    }
    print("=" * 104)
    print("HUKUM — ON_KAYIT bolum 5")
    print("=" * 104)
    for k, val in P.items():
        print("   %-32s %s" % (k, "GECTI" if val else "DUSTU"))
    print()
    if all(P.values()):
        print("   🔑 YON VAR — genis stop daha iyi.")
        print("   🔴 Bota KONMAZ: once portfoy simulasyonu (on-kayit bolum 8).")
        print("      ⚠️ Genis stop = KUCUK pozisyon -> slot/sermaye kullanimi degisir.")
    elif not (P["P1 holdout rho > 0"] and P["P2 gun-kumeli t >= %.1f" % T_ESIK]):
        print("   YON YOK — hipotez dustu.")
    else:
        print("   GOREMIYORUZ — isaret var ama MDE asilmadi (N/guc yetmedi).")
    print()
    print("   IKINCIL (hukum kurmaz) — ters yon, TAVAN kurali:")
    for esik in (3.0, 4.0, 5.0):
        ic = [r["R"] for r in hold if r["stop_pct"] <= esik]
        if len(ic) >= 30:
            print("      stop <= %%%.1f -> N=%4d  ort R %+.4f" % (esik, len(ic), stx.mean(ic)))
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
