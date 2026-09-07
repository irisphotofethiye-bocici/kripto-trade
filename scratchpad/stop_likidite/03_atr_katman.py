#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STOP-LIKIDITE ETKISI, ATR/FIYAT SABITLENINCE KALIYOR MU?

ON_KAYIT_stop_likidite_atr.md · commit 6f2c715 — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

Populasyon/harita/stop_p: 02_uzun.py'den AYNEN. Degisen tek sey KATMANLAMA.
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

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURA))
sys.path.insert(0, KOK)
sp1 = il.spec_from_file_location("o1", os.path.join(BURA, "01_olcum.py"))
o1 = il.module_from_spec(sp1)
sp1.loader.exec_module(o1)
sp2 = il.spec_from_file_location("o2", os.path.join(BURA, "02_uzun.py"))
o2 = il.module_from_spec(sp2)
sp2.loader.exec_module(o2)

TABAN = 0.0458        # 02_uzun.py ATR-mesafesi katmanli sonucu (+4,58 puan)
A2_ESIK = TABAN * 0.50
A5_ESIK = 0.030
T_ESIK = 2.5
DILIM = 5
MIN_HUCRE = 200
random.seed(20260907)


def dil(rows, alan, k=DILIM):
    v = sorted(rows, key=lambda x: x[alan])
    n = len(v)
    return [v[i * n // k:(i + 1) * n // k] for i in range(k)]


def katman_fark(rows, alan, metrik="stop_oldu"):
    """alan katmanlari ICINDE (kume ici - bos bolge), agirlikli ortalama."""
    f, w, at = [], [], 0
    for kat in dil(rows, alan):
        if len(kat) < MIN_HUCRE:
            at += 1
            continue
        k = o1.kars(kat, metrik)
        if k is None:
            at += 1
            continue
        f.append(k[0])
        w.append(len(kat))
    if not f:
        return None, 0, at
    return sum(a * b for a, b in zip(f, w)) / sum(w), len(f), at


def cift_katman(rows, metrik="stop_oldu"):
    f, w, at = [], [], 0
    for k1 in dil(rows, "atr_pct"):
        for k2 in dil(k1, "stop_atr"):
            if len(k2) < MIN_HUCRE:
                at += 1
                continue
            k = o1.kars(k2, metrik)
            if k is None:
                at += 1
                continue
            f.append(k[0])
            w.append(len(k2))
    if not f:
        return None, 0, at
    return sum(a * b for a, b in zip(f, w)) / sum(w), len(f), at


def kume_t(rows, anahtar):
    """anahtar bazinda (gun ya da sembol) kumelenmis fark ve t."""
    p = dil(rows, "stop_p")
    ae, ue = p[0][-1]["stop_p"], p[-1][0]["stop_p"]
    g = collections.defaultdict(lambda: ([], []))
    for x in rows:
        if x["stop_p"] >= ue:
            g[x[anahtar]][0].append(x["stop_oldu"])
        elif x["stop_p"] <= ae:
            g[x[anahtar]][1].append(x["stop_oldu"])
    v = [stx.mean(a) - stx.mean(b) for a, b in g.values()
         if len(a) >= 3 and len(b) >= 3]
    if len(v) < 5:
        return 0.0, 0.0, len(v)
    m = stx.mean(v)
    se = stx.stdev(v) / math.sqrt(len(v))
    return m, (m / se if se else 0.0), len(v)


def main():
    print("=" * 104)
    print("STOP-LIKIDITE, ATR/FIYAT SABITLENINCE — ON_KAYIT 6f2c715")
    print("taban (02_uzun ATR-mesafesi katmanli) = %+.2f puan · A2 esigi %+.2f puan"
          % (TABAN * 100, A2_ESIK * 100))
    print("=" * 104)
    rows, _ = o2.uret()
    gunler = sorted(set(x["gun"] for x in rows))
    ks = gunler[int(len(gunler) * o2.KESIF_PAY)]
    kesif = [x for x in rows if x["gun"] < ks]
    hold = [x for x in rows if x["gun"] >= ks]
    print("N=%s · KESIF %s · HOLDOUT %s\n"
          % ("{:,}".format(len(rows)), "{:,}".format(len(kesif)), "{:,}".format(len(hold))))

    print("### 0) ATR/fiyat GERCEKTEN ayrisyor mu (karistirici var mi)")
    print("   %-14s %8s %10s %11s %10s" % ("stop_p dilimi", "N", "ATR%", "stop ATR", "stop%"))
    for q in dil(hold, "stop_p"):
        print("   %-14s %8s %9.2f%% %10.2f %9.2f%%"
              % ("%.2f-%.2f" % (q[0]["stop_p"], q[-1]["stop_p"]), "{:,}".format(len(q)),
                 stx.mean([x["atr_pct"] for x in q]),
                 stx.mean([x["stop_atr"] for x in q]),
                 stx.mean([x["stop_pct"] for x in q])))
    print()

    print("### 1) 🔴 BIRINCIL — ATR/fiyat KATMANLARI ICINDE")
    fa, na, ata = katman_fark(hold, "atr_pct")
    fk, _, _ = katman_fark(kesif, "atr_pct")
    ham = o1.kars(hold)
    print("   HAM (katmansiz)     %+.4f (%.2f puan)" % (ham[0], ham[0] * 100))
    print("   ATR-MESAFESI katman %+.4f (%.2f puan)   <- 02_uzun'un tabani" % (TABAN, TABAN * 100))
    if fa is None:
        print("   🔴 ATR/fiyat katmani hesaplanamadi")
        return
    print("   ATR/FIYAT katman    %+.4f (%.2f puan)  · %d katman · %d atlandi"
          % (fa, fa * 100, na, ata))
    print("   KESIF ayni hesap    %+.4f (%.2f puan)" % (fk or 0, (fk or 0) * 100))
    print("   tabana gore koruma  %.0f%%   (A2 esigi %%50)" % (fa / TABAN * 100))
    print()

    print("### 2) IKINCIL-1 — CIFT KATMAN (ATR/fiyat x stop_atr, 5x5)")
    fc, nc, atc = cift_katman(hold)
    if fc is None:
        print("   hucre yetersiz")
        fc = 0.0
    else:
        print("   %+.4f (%.2f puan) · %d hucre kullanildi · %d atlandi (N<%d)"
              % (fc, fc * 100, nc, atc, MIN_HUCRE))
        print("   ATR/fiyat katmanina gore koruma %.0f%% (A6 esigi %%50)"
              % (fc / fa * 100 if fa else 0))
    print()

    print("### 3) IKINCIL-2 — KUMELEME (gun vs SEMBOL)")
    mg, tg, ng = kume_t(hold, "gun")
    msy, tsy, nsy = kume_t(hold, "sym")
    print("   GUN   -kumeli fark %+.4f · t %+.2f (%d gun)" % (mg, tg, ng))
    print("   SEMBOL-kumeli fark %+.4f · t %+.2f (%d sembol)" % (msy, tsy, nsy))
    print()

    A = {
        "A1 ATR/fiyat katmanli fark > 0": fa > 0,
        "A2 fark >= tabanin %50si (2,29 puan)": fa >= A2_ESIK,
        "A3 gun-kumeli t >= 2,5": tg >= T_ESIK,
        "A4 kesif+holdout ayni isaret": (fk or 0) > 0 and fa > 0,
        "A5 ekonomik taban >= 3,0 puan": fa >= A5_ESIK,
        "A6 cift katmanli >= ATR-katmanlinin %50si": bool(fa) and fc >= 0.5 * fa,
        "A7 sembol-kumeli t >= 2,5": tsy >= T_ESIK,
    }
    print("=" * 104)
    print("HUKUM — ON_KAYIT bolum 3")
    print("=" * 104)
    for k, v in A.items():
        print("   %-44s %s" % (k, "GECTI" if v else "DUSTU"))
    print()
    if all(A.values()):
        print("   🔑 KARISTIRICI KAPANDI — etki ATR/fiyat'tan BAGIMSIZ.")
        print("   🔴 SIRADA: tasinabilirlik (botun evreninde var mi). Kod DEGISMEZ.")
    elif not (A["A1 ATR/fiyat katmanli fark > 0"] and A["A4 kesif+holdout ayni isaret"]):
        print("   🔴 ATR'NIN KILIGI — bulgu COKTU.")
    elif not A["A2 fark >= tabanin %50si (2,29 puan)"]:
        print("   KISMEN ATR — etki ATR'nin bir parcasiymis, kural YAZILMAZ.")
    elif not A["A7 sembol-kumeli t >= 2,5"]:
        print("   SEMBOLE OZGU — etki birkac sembolden geliyor olabilir.")
    elif not A["A5 ekonomik taban >= 3,0 puan"]:
        print("   GORULUR AMA ZAYIF — ekonomik taban altinda, kural YAZILMAZ.")
    else:
        print("   KISMEN gecti — ayrintiya bak.")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
