#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KALDIRACLI %10 HEDEF — olcum (2026-08-11)

SORU (kullanici): "hedefi kaldiracli %10 diye ayarlasak nasil olur?"
Yani: fiyat %10 hareket etsin diye degil, MARJINE gore %10 kar olunca cik.

ONCE ARITMETIK — sonucu bu belirliyor:
  ROI_marjin = fiyat_hareketi x kaldirac
  kaldiracli %10  ->  fiyat_hedefi = 10 / kaldirac

  Kaldirac bu botta SERBEST DEGIL, stop mesafesinden turer (risk-once boyutlandirma):
      notional  = hedef_risk / stop_frac
      kaldirac  = notional / marjin = (risk_pct/marjin_pct) / stop_frac
      risk_pct=%1.5, marjin_pct=%10 -> kaldirac = 0.15/stop_frac, [3,10] araliginda kirpilir

  Yerine koyunca:
      kar_$ = notional x fiyat_hedefi = notional x (10/kaldirac) = 0.10 x marjin
  YANI "kaldiracli %10" = HER ISLEMDE MARJININ %10'U KADAR SABIT DOLAR KAR.
  Marjin ~ sermayenin %10'u oldugundan -> islem basi hedef ~ sermayenin %1'i.
  Risk ise sermayenin %1.5'i. Yani odul/risk ~ 0.67:1 -> basabas isabet ~%60.

  Bugunku sabit %10 FIYAT hedefinde: medyan stop %3.4 -> odul/risk ~2.9:1, basabas ~%26.

BU BETIK: iddiayi degil, SONUCU olcer. Canli iki kapinin 577 olayinda iki hedef
kuralini yan yana kosturur. Salt-okunur, bota dokunmaz.
"""
import json, os, sys, statistics as stx, datetime, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yon_avi
import yon_dogrula as yd
import olcum_ortak as oo

RISK_PCT, MARJIN_PCT = 0.015, 0.10
KALD_MIN, KALD_MAX = 3.0, 10.0
UFUK = 72


def kaldirac(stop_frac):
    """testbot.yeni_giris_ac ile ayni: notional=risk/stop, kaldirac=notional/marjin, kirpilir."""
    if stop_frac <= 0:
        return KALD_MIN
    k = (RISK_PCT / MARJIN_PCT) / stop_frac
    return max(KALD_MIN, min(KALD_MAX, k))


def islem(b, si, hedef_pct, yon, ufuk=UFUK):
    """yd.islem ile ayni mekanik; hedef DISARIDAN verilir. Wilder ATR (olcum_ortak)."""
    gi = si
    i = gi - 1
    if i < 200 or gi >= len(b):
        return None
    a = oo.atr(b, i)
    if not a or a <= 0:
        return None
    ref = b[gi]["o"]
    hi, lo = yd.swings2(b, i)
    if yon == "SHORT":
        res = min([x for x in hi if x > ref], default=None)
        ad = []
        if res is not None and (res - ref) <= 3 * a:
            ad.append(res + 0.25 * a)
        nb = max(x["h"] for x in b[max(0, i - 9):i + 1])
        if nb > ref:
            ad.append(nb + 0.25 * a)
        ad.append(ref + 1.5 * a)
        gec = [s for s in ad if s > ref]
        stop = min(gec) if gec else ref + 1.5 * a
        hedef = ref * (1 - hedef_pct / 100)
    else:
        return None
    sp = (stop - ref) / ref * 100
    if sp <= 0 or hedef_pct <= 0:
        return None
    son = min(gi + ufuk, len(b))
    if son - gi < 4:
        return None
    for j in range(gi, son):
        x = b[j]
        if x["h"] >= stop:
            return -sp - oo.MALIYET, "STOP", sp, hedef_pct
        if x["l"] <= hedef:
            return hedef_pct - oo.MALIYET, "HEDEF", sp, hedef_pct
    c = b[son - 1]["c"]
    return (ref - c) / ref * 100 - oo.MALIYET, "SURE", sp, hedef_pct


def main():
    ge = yon_avi.yukle()
    bc, idxc = {}, {}
    for o in ge:
        s = o["sym"]
        if s not in bc:
            p = os.path.join(yd.CACHE, f"{s}.json")
            bc[s] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
            if bc[s]:
                idxc[s] = {x["t"] // 3600000: i for i, x in enumerate(bc[s])}
        if not bc[s]:
            continue
        ms = int(datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M")
                 .astimezone().timestamp() * 1000)
        o["_b"], o["_gi"] = bc[s], idxc[s].get(ms // 3600000)

    def ab(o):
        return (o.get("funding") or 0) <= -0.05 and (o.get("oi24") or 0) >= 10

    def ma50(o):
        px = 10 ** o["fiyat_log"] if o.get("fiyat_log") is not None else None
        return px is not None and px <= 0.07 and (o.get("ma50_mesafe") or -99) >= 3.72

    sec = [o for o in ge if o.get("_gi") is not None
           and (ab(o) or ma50(o)) and (o.get("chg24") or 0) < 20]
    tsl = sorted(o["ts"] for o in sec)
    ORTA = tsl[len(tsl) // 2]

    print("=" * 108)
    print("KALDIRACLI %10 HEDEF vs BUGUNKU SABIT %10 FIYAT HEDEFI")
    print("=" * 108)
    print(f"Canli iki kapinin olaylari: N={len(sec)} · maliyet %{oo.MALIYET} · Wilder ATR · ufuk {UFUK}s\n")

    # --- once: kaldiracli %10 pratikte hangi fiyat hedefine denk geliyor?
    ornek = []
    for o in sec:
        r = islem(o["_b"], o["_gi"] + 1, 10.0, "SHORT")
        if r:
            ornek.append((r[2], kaldirac(r[2] / 100.0)))
    if ornek:
        sp = [x[0] for x in ornek]
        print("1) KALDIRACLI %10 NE DEMEK — stop mesafesine gore")
        print(f"{'stop dilimi':18}{'medyan stop':>13}{'kaldirac':>10}{'FIYAT hedefi':>14}{'odul/risk':>11}")
        print("-" * 108)
        q = sorted(sp)
        kes = [q[int(len(q) * p)] for p in (0.25, 0.5, 0.75)]
        for ad, s in (("dar  (%25 dilim)", kes[0]), ("orta (medyan)", kes[1]),
                      ("genis(%75 dilim)", kes[2])):
            k = kaldirac(s / 100.0)
            h = 10.0 / k
            print(f"{ad:18}{s:12.2f}%{k:10.1f}{h:13.2f}%{h/s:11.2f}")
        print("-" * 108)
        print("  Cikan sonuc: kaldiracli %10, HER ISLEMDE marjinin %10'u kadar SABIT dolar kar")
        print("  demektir (kar_$ = notional x 10/kaldirac = 0.10 x marjin). Odul/risk ~0.67:1.")

    # --- asil karsilastirma
    print("\n2) SONUC — iki kural yan yana")
    print(f"{'kural':34}{'N':>6}{'net %':>9}{'isabet':>9}{'basabas':>10}"
          f"{'A yari':>9}{'B yari':>9}{'toplam':>10}")
    print("-" * 108)
    KURAL = [("BUGUNKU: sabit %10 FIYAT", lambda spf: 10.0),
             ("kaldiracli %10 (= marjinin %10)", lambda spf: 10.0 / kaldirac(spf / 100.0)),
             ("kaldiracli %20", lambda spf: 20.0 / kaldirac(spf / 100.0)),
             ("kaldiracli %30", lambda spf: 30.0 / kaldirac(spf / 100.0)),
             ("kaldiracli %60 (~fiyat %10'a denk)", lambda spf: 60.0 / kaldirac(spf / 100.0))]
    for ad, hedef_fn in KURAL:
        kayit, sem = [], []
        for o in sec:
            on = islem(o["_b"], o["_gi"] + 1, 10.0, "SHORT")   # stop mesafesini ogren
            if not on:
                continue
            h = hedef_fn(on[2])
            r = islem(o["_b"], o["_gi"] + 1, h, "SHORT")
            if r:
                kayit.append((o["ts"], r)); sem.append(o["sym"])
        if len(kayit) < 60:
            continue
        g = [x[1][0] for x in kayit]
        isa = sum(1 for x in kayit if x[1][1] == "HEDEF") / len(kayit) * 100
        msp = stx.median([x[1][2] for x in kayit])
        mh = stx.median([x[1][3] for x in kayit])
        bb = (msp + oo.MALIYET) / ((mh - oo.MALIYET) + msp + oo.MALIYET) * 100
        A = [x[1][0] for x in kayit if x[0] < ORTA]
        B = [x[1][0] for x in kayit if x[0] >= ORTA]
        im = " *" if stx.mean(g) > 0 else ""
        print(f"{ad:34}{len(g):6d}{stx.mean(g):+9.2f}{isa:8.1f}%{bb:9.1f}%"
              f"{stx.mean(A):+9.2f}{stx.mean(B):+9.2f}{sum(g):+10.0f}{im}")
    print("-" * 108)
    print("  'net %' = FIYAT yuzdesi (kaldiracsiz). Kaldiracli karsiligi icin kaldiracla carp.")
    print("  basabas = (stop+maliyet)/((hedef-maliyet)+stop+maliyet), medyanlardan.")

    print("\n3) AYNI SEY SERMAYE GETIRISI OLARAK — kaldirac etkisi dahil")
    print(f"{'kural':34}{'islem basi sermaye %':>22}{'aciklama':>28}")
    print("-" * 108)
    for ad, hedef_fn in KURAL:
        kayit = []
        for o in sec:
            on = islem(o["_b"], o["_gi"] + 1, 10.0, "SHORT")
            if not on:
                continue
            h = hedef_fn(on[2])
            r = islem(o["_b"], o["_gi"] + 1, h, "SHORT")
            if r:
                k = kaldirac(r[2] / 100.0)
                boy = min(RISK_PCT / (r[2] / 100.0), MARJIN_PCT * KALD_MAX)
                kayit.append(r[0] * boy)
        if len(kayit) < 60:
            continue
        print(f"{ad:34}{stx.mean(kayit):+22.3f}")


if __name__ == "__main__":
    main()
