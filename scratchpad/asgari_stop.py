#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASGARI STOP ESIGI 2,0 -> 3,0 — 2 yillik sinav (2026-08-19)

ON-KAYIT: olcumler.md -> "ON-KAYIT — ASGARI STOP ESIGI" (commit d5a6881,
KOSTURULMADAN ONCE yazildi). Bu betik o on-kaydi UYGULAR; olcut metnini
degistirmez, esik taramaz.

HIPOTEZ: yapisal stop'u %3'ten dar olan adayi REDDETMEK net getiriyi artirir.

DIKKAT — YAPI ileri_rr.py'den FARKLI:
  ileri_rr'de iki kol AYNI girisleri paylasip farkli cikiyordu (eslesmis).
  Burada kural kolu kontrolun ALT KUMESI: ayni mekanik, daha az giris.
  Bu yuzden tek gecis yeter — her islem stop genisligiyle etiketlenir,
  sonra iki kume karsilastirilir. Eslesmis test DEGIL, alt-kume testi.

ESIK = 3.0 (TEK deger, on-kayitli, tarama YASAK).
  Gozlem A=3,38 / B=5,60 diyordu; esik oraya KONULMADI (veriye uydurma
  olurdu). 3,0 her iki medyanin da ALTINDA -> yonu muhafazakar sinar.

MEKANIK (ileri_rr ile birebir ayni):
  giris = tetigin ertesi 1h barinin acilisi · stop = A-varyanti (Wilder ATR14)
  hedef = giris -%10 · ufuk 72s · maliyet olcum_ortak.MALIYET · FONLAMA DAHIL

GECME OLCUTU (dordu de gerekli + ek sart):
  1. islem basina net getiri kontrolden YUKSEK
  2. IKI YARIDA DA yuksek
  3. t_kume > +2.0
  4. uc rejimde ters isaret yok
  EK: islem sayisi %50'den fazla duserse -> KALDI (olcum hizi baglayici kisit)
"""
import json, os, sys, statistics as stx, collections, bisect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olcum_ortak as oo
import ileri_rr as ir          # atr_serisi / ma_serisi / stop_hesapla / fonlama_pct / btc_rejim

KONTROL_STOP = 2.0
KURAL_STOP = 3.0
HEDEF_PCT, UFUK = 10.0, 72


def islem(b, atrs, si, ft, fr):
    """-> dict | None.  TEK islem; stop genisligi (sp) ile etiketlenir."""
    gi = si + 1
    if si < ir.ISINMA or gi >= len(b) or not atrs[si]:
        return None
    ref = b[gi]["o"]
    if ref <= 0:
        return None
    stop = ir.stop_hesapla(b, si, ref, atrs[si])
    sp = (stop - ref) / ref * 100
    if sp <= 0 or sp < KONTROL_STOP:      # kontrol esigini gecemeyen ikisinde de yok
        return None
    son = min(gi + UFUK, len(b))
    if son - gi < 4:
        return None
    hedef = ref * (1 - HEDEF_PCT / 100)
    cj = tip = ham = None
    for j in range(gi, son):
        x = b[j]
        if x["h"] >= stop:
            cj, tip, ham = j, "STOP", -sp
            break
        if x["l"] <= hedef:
            cj, tip, ham = j, "HEDEF", HEDEF_PCT
            break
    if cj is None:
        cj, tip = son - 1, "SURE"
        ham = (ref - b[son - 1]["c"]) / ref * 100
    fon = ir.fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
    return {"net": ham - oo.MALIYET + fon, "tip": tip, "sp": sp, "ts": b[gi]["t"]}


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
        if len(b) < ir.ISINMA + UFUK + 50:
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
        for i in range(ir.ISINMA, len(b) - UFUK - 2, ir.SEYRELT):
            x = b[i]
            if (x.get("qv") or 0) < ir.MIN_VOL / 24 or i < 24:
                continue
            if (x["c"] / b[i - 24]["c"] - 1) * 100 >= ir.PUMP:
                continue
            hedefler = []
            if ft:
                k = bisect.bisect_right(ft, x["t"]) - 1
                if k >= 0 and fr[k]["r"] <= ir.FUND_ESIK:   # 2026-08-21: r ZATEN yuzde (funding_indir.py:67)
                    hedefler.append("A_funding")
            if ma50[i] and ma50[i] > 0 and x["c"] <= ir.UCUZ_FIYAT:
                if (x["c"] / ma50[i] - 1) * 100 >= ir.MA50_MESAFE:
                    hedefler.append("B_ma50ucuz")
            if not hedefler:
                continue
            t = islem(b, atrs, i, ft, fr)
            if not t:
                continue
            t["sym"] = sym
            t["rejim"] = rej.get(b[i]["t"] // 3600000, "NOTR")
            for h in hedefler:
                kume[h].append(t)
    return kume, islenen


def rapor():
    print("ASGARI STOP ESIGI %s -> %s  —  2 yillik sinav" % (KONTROL_STOP, KURAL_STOP))
    print("=" * 78)
    print("ON-KAYIT: olcumler.md (commit d5a6881, kosturulmadan ONCE)")
    print("Yapi: ALT-KUME testi (eslesmis degil) — kural kolu kontrolun alt kumesi")
    print("Mekanik: A-stop, Wilder ATR, hedef %%%s, %ss, maliyet %%%s, FONLAMA DAHIL\n"
          % (HEDEF_PCT, UFUK, oo.MALIYET))
    kume, islenen = kostur()
    print("islenen sembol: %d\n" % islenen)
    for ad, v in kume.items():
        if len(v) < 40:
            print("%s: N=%d — YETERSIZ\n" % (ad, len(v)))
            continue
        kon = v
        kur = [t for t in v if t["sp"] >= KURAL_STOP]
        ok = oo.ozet([t["net"] for t in kon], [t["sym"] for t in kon], asgari=30)
        ur = oo.ozet([t["net"] for t in kur], [t["sym"] for t in kur], asgari=30)
        if not ok or not ur:
            print("%s: ozet uretilemedi\n" % ad)
            continue
        dus = 100 * (1 - len(kur) / len(kon))
        print("--- %s %s" % (ad, "-" * max(0, 58 - len(ad))))
        print("  KONTROL (stop>=%.1f) : N=%6d  %+7.3f%%  t=%+5.2f  t_kume=%+5.2f  toplam %+9.1f"
              % (KONTROL_STOP, ok["n"], ok["ort"], ok["t"], ok.get("t_kume", 0), ok["ort"] * ok["n"]))
        print("  KURAL   (stop>=%.1f) : N=%6d  %+7.3f%%  t=%+5.2f  t_kume=%+5.2f  toplam %+9.1f"
              % (KURAL_STOP, ur["n"], ur["ort"], ur["t"], ur.get("t_kume", 0), ur["ort"] * ur["n"]))
        print("  FARK (islem basina)  : %+7.3f%%   |   islem sayisi dususu: %%%.1f %s"
              % (ur["ort"] - ok["ort"], dus, "<-- EK SART IHLALI (>%50)" if dus > 50 else ""))
        # elenen dilim: stop 2,0-3,0 arasi
        el = [t for t in v if t["sp"] < KURAL_STOP]
        if len(el) >= 30:
            oe = oo.ozet([t["net"] for t in el], [t["sym"] for t in el], asgari=30)
            if oe:
                print("  ELENEN dilim (%.1f-%.1f): N=%6d  %+7.3f%%  t=%+5.2f   <-- bunlar atiliyor"
                      % (KONTROL_STOP, KURAL_STOP, oe["n"], oe["ort"], oe["t"]))
        # olcut 2: iki yari
        srt = sorted(range(len(kon)), key=lambda z: kon[z]["ts"])
        yar = len(srt) // 2
        for etiket, idx in (("A yarisi", srt[:yar]), ("B yarisi", srt[yar:])):
            kk = [kon[z] for z in idx]
            uu = [t for t in kk if t["sp"] >= KURAL_STOP]
            a1 = oo.ozet([t["net"] for t in kk], [t["sym"] for t in kk], asgari=20)
            a2 = oo.ozet([t["net"] for t in uu], [t["sym"] for t in uu], asgari=20)
            if a1 and a2:
                print("    %s: kontrol %+6.3f%%  kural %+6.3f%%  fark %+6.3f%%  (N %d->%d)"
                      % (etiket, a1["ort"], a2["ort"], a2["ort"] - a1["ort"], a1["n"], a2["n"]))
        # olcut 4: rejim
        rg = collections.defaultdict(lambda: [[], []])
        for t in v:
            rg[t["rejim"]][0].append(t["net"])
            if t["sp"] >= KURAL_STOP:
                rg[t["rejim"]][1].append(t["net"])
        par = []
        for k, (a1, a2) in sorted(rg.items()):
            if len(a1) >= 20 and len(a2) >= 20:
                par.append("%s %+.3f%% (N=%d)" % (k, stx.mean(a2) - stx.mean(a1), len(a2)))
        print("    rejim farki: " + " | ".join(par))
        print()


if __name__ == "__main__":
    rapor()
