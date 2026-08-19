#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KATILIM FILTRESI islem_x >= 1,0 — 2 yillik sinav (2026-08-19)

ON-KAYIT: olcumler.md -> "ON-KAYIT — KATILIM FILTRESI" (commit 0a73e29,
KOSTURULMADAN ONCE yazildi). Olcut metnini degistirmez, esik taramaz.

HIPOTEZ: giris aninda katilimi KENDI NORMALININ ALTINDA olan adayi
reddetmek net getiriyi artirir.

  islem_x = n(giris bari) / medyan(n, onceki 48 bar)      esik: >= 1,0

NEDEN GORELI: mutlak islem sayisi BUYUKLUK VEKILIDIR (buyuk coin = cok
islem). Sembolun kendi tabanina oranlanmali.

NEDEN 1,0: ayarlanmis esik degil TANIMSAL sinir. 1,5+ kendi ek sartimla
(>%50 eleme -> KALDI) dislanmis; 1,2 keyfi olurdu.

COZUNURLUK SINIRI: gozlem 15 dakikalik, bu veri SAATLIK -> VEKIL olcum.

Yapi: asgari_stop.py ile ayni — ALT-KUME testi (eslesmis degil).
"""
import json, os, sys, statistics as stx, collections, bisect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olcum_ortak as oo
import ileri_rr as ir
import asgari_stop as asg

ESIK_X = 1.0
GERI = 48                      # katilim tabani icin bakilan bar sayisi


def kostur():
    rej = ir.btc_rejim()
    kume = {"A_funding": [], "B_ma50ucuz": []}
    islenen = 0
    for fn in sorted(os.listdir(ir.KLINE)):
        if not fn.endswith(".json"):
            continue
        sym = fn[:-5]
        try:
            b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ir.ISINMA + ir.UFUK + 50:
            continue
        fp = os.path.join(ir.FUND, fn)
        fr = []
        if os.path.exists(fp):
            try:
                fr = json.load(open(fp, encoding="utf-8"))
            except Exception:
                fr = []
        ft = [x["t"] for x in fr]
        atrs = ir.atr_serisi(b)
        ma50 = ir.ma_serisi(b, 50)
        islenen += 1
        for i in range(ir.ISINMA, len(b) - ir.UFUK - 2, ir.SEYRELT):
            x = b[i]
            if (x.get("qv") or 0) < ir.MIN_VOL / 24 or i < GERI:
                continue
            if (x["c"] / b[i - 24]["c"] - 1) * 100 >= ir.PUMP:
                continue
            hedefler = []
            if ft:
                k = bisect.bisect_right(ft, x["t"]) - 1
                if k >= 0 and fr[k]["r"] * 100 <= ir.FUND_ESIK:
                    hedefler.append("A_funding")
            if ma50[i] and ma50[i] > 0 and x["c"] <= ir.UCUZ_FIYAT:
                if (x["c"] / ma50[i] - 1) * 100 >= ir.MA50_MESAFE:
                    hedefler.append("B_ma50ucuz")
            if not hedefler:
                continue
            t = asg.islem(b, atrs, i, ft, fr)
            if not t:
                continue
            gec = [b[j].get("n") or 0 for j in range(i - GERI, i)]
            m = stx.median(gec)
            if not m or not x.get("n"):
                continue                      # katilim olculemiyorsa olay disi
            t["islem_x"] = x["n"] / m
            t["sym"] = sym
            t["rejim"] = rej.get(b[i]["t"] // 3600000, "NOTR")
            for h in hedefler:
                kume[h].append(t)
    return kume, islenen


def rapor():
    print("KATILIM FILTRESI  islem_x >= %.1f  —  2 yillik sinav" % ESIK_X)
    print("=" * 78)
    print("ON-KAYIT: olcumler.md (commit 0a73e29, kosturulmadan ONCE)")
    print("islem_x = n(giris bari) / medyan(n, onceki %d bar)   [GORELI, boyuttan arinik]" % GERI)
    print("UYARI: gozlem 15 dk, bu veri SAATLIK -> VEKIL olcum")
    print("Mekanik: A-stop, hedef %10, 72s, maliyet + FONLAMA DAHIL\n")
    kume, islenen = kostur()
    print("islenen sembol: %d\n" % islenen)
    for ad, v in kume.items():
        if len(v) < 40:
            print("%s: N=%d — YETERSIZ\n" % (ad, len(v)))
            continue
        kon = v
        kur = [t for t in v if t["islem_x"] >= ESIK_X]
        ok = oo.ozet([t["net"] for t in kon], [t["sym"] for t in kon], asgari=30)
        ur = oo.ozet([t["net"] for t in kur], [t["sym"] for t in kur], asgari=30)
        if not ok or not ur:
            print("%s: ozet uretilemedi\n" % ad)
            continue
        dus = 100 * (1 - len(kur) / len(kon))
        print("--- %s %s" % (ad, "-" * max(0, 58 - len(ad))))
        print("  KONTROL (filtresiz)     : N=%6d  %+7.3f%%  t=%+5.2f  t_kume=%+5.2f"
              % (ok["n"], ok["ort"], ok["t"], ok.get("t_kume", 0)))
        print("  KURAL   (islem_x>=%.1f)  : N=%6d  %+7.3f%%  t=%+5.2f  t_kume=%+5.2f"
              % (ESIK_X, ur["n"], ur["ort"], ur["t"], ur.get("t_kume", 0)))
        print("  FARK (islem basina)     : %+7.3f%%   |   islem dususu: %%%.1f %s"
              % (ur["ort"] - ok["ort"], dus, "<-- EK SART IHLALI" if dus > 50 else ""))
        el = [t for t in v if t["islem_x"] < ESIK_X]
        if len(el) >= 30:
            oe = oo.ozet([t["net"] for t in el], [t["sym"] for t in el], asgari=30)
            if oe:
                print("  ELENEN dilim (x<%.1f)    : N=%6d  %+7.3f%%  t=%+5.2f   <-- atilanlar"
                      % (ESIK_X, oe["n"], oe["ort"], oe["t"]))
        srt = sorted(range(len(kon)), key=lambda z: kon[z]["ts"])
        yar = len(srt) // 2
        for etiket, idx in (("A yarisi", srt[:yar]), ("B yarisi", srt[yar:])):
            kk = [kon[z] for z in idx]
            uu = [t for t in kk if t["islem_x"] >= ESIK_X]
            a1 = oo.ozet([t["net"] for t in kk], [t["sym"] for t in kk], asgari=20)
            a2 = oo.ozet([t["net"] for t in uu], [t["sym"] for t in uu], asgari=20)
            if a1 and a2:
                print("    %s: kontrol %+6.3f%%  kural %+6.3f%%  fark %+6.3f%%  (N %d->%d)"
                      % (etiket, a1["ort"], a2["ort"], a2["ort"] - a1["ort"], a1["n"], a2["n"]))
        rg = collections.defaultdict(lambda: [[], []])
        for t in v:
            rg[t["rejim"]][0].append(t["net"])
            if t["islem_x"] >= ESIK_X:
                rg[t["rejim"]][1].append(t["net"])
        par = []
        for k, (a1, a2) in sorted(rg.items()):
            if len(a1) >= 20 and len(a2) >= 20:
                par.append("%s %+.3f%% (N=%d)" % (k, stx.mean(a2) - stx.mean(a1), len(a2)))
        print("    rejim farki: " + " | ".join(par))
        print()


if __name__ == "__main__":
    rapor()
