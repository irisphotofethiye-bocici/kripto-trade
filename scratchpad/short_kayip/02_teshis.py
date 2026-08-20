#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TESHIS — para nereye gitti? ARAMA YOK, yalniz tarif.

Iki yon (SHORT/LONG) x iki donem (sicrama oncesi/sonrasi) x iki taban.
SALT OKUMA.
"""
import sys, os, collections, datetime, statistics as stx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ortak                                    # noqa: E402


def mfe_mae(p):
    """Pozisyon acikken en iyi (MFE) ve en kotu (MAE) yuzde — 5dk mumdan.
    Pozisyon LEHINE isaretli: MFE pozitif = kara gecmisti."""
    g0, g1 = ortak.dt(p["giris_ts"]), ortak.dt(p["cikis_ts"])
    b = ortak.mumlar(p["sym"], g0 - datetime.timedelta(minutes=10),
                     g1 + datetime.timedelta(minutes=10))
    t0, t1 = int(g0.timestamp() * 1000), int(g1.timestamp() * 1000)
    ic = [x for x in b if t0 <= x["t"] <= t1]
    ref = p.get("giris_fiyat")
    if not ic or not ref:
        return None, None
    hi = max(x["h"] for x in ic)
    lo = min(x["l"] for x in ic)
    if p["yon"] == "SHORT":
        return (ref - lo) / ref * 100, (ref - hi) / ref * 100
    return (hi - ref) / ref * 100, (lo - ref) / ref * 100


def blok(baslik, poz):
    v = [p["pnl"] for p in poz]
    o = ortak.ozet(v)
    if not o:
        print("  %s: yok" % baslik)
        return
    sv = sorted(v, reverse=True)
    print("  %-22s N=%3d  toplam %+9.2f  ort %+7.2f  MEDYAN %+7.2f  kazanan %2d (%%%.0f)"
          % (baslik, o["n"], o["toplam"], o["ort"], o["medyan"], o["kazanan"], o["kazanma_pct"]))
    if o["n"] >= 6:
        print("  %-22s en iyi 3 cikinca %+9.2f  ·  en kotu 3 cikinca %+9.2f"
              % ("", sum(sv[3:]), sum(sv[:-3])))


def kostur(taban):
    poz = ortak.poz_yukle(taban)
    print("\n" + "=" * 88)
    print("TABAN: %s   (pozisyon %d)" % (taban, len(poz)))
    print("=" * 88)

    for yon in ("SHORT", "LONG"):
        g = [p for p in poz if p["yon"] == yon]
        print("\n### %s  (N=%d)" % (yon, len(g)))
        blok("TUMU", g)
        for dn, ad in (("oncesi", "sicrama ONCESI"), ("sonrasi", "sicrama SONRASI")):
            blok(ad, [p for p in g if p["donem"] == dn])

        print("\n  -- gun gun (giris gunu)")
        gun = collections.defaultdict(list)
        for p in g:
            gun[p["giris_ts"][:10]].append(p["pnl"])
        kum = 0.0
        for d in sorted(gun):
            kum += sum(gun[d])
            print("     %s  N=%2d  gun %+9.2f   kumulatif %+9.2f"
                  % (d, len(gun[d]), sum(gun[d]), kum))

        print("\n  -- KAPI kirilimi")
        kp = collections.defaultdict(list)
        for p in g:
            kp[p["kapi"]].append(p["pnl"])
        for k in sorted(kp, key=lambda z: sum(kp[z])):
            o = ortak.ozet(kp[k])
            print("     %-14s N=%3d  toplam %+9.2f  medyan %+7.2f  kazanan %%%.0f"
                  % (k, o["n"], o["toplam"], o["medyan"], o["kazanma_pct"]))

        print("\n  -- CIKIS tipi")
        ck = collections.defaultdict(list)
        for p in g:
            ck[p["sebep_cikis"] or "?"].append(p["pnl"])
        for k in sorted(ck, key=lambda z: sum(ck[z])):
            o = ortak.ozet(ck[k])
            print("     %-14s N=%3d  toplam %+9.2f  medyan %+7.2f"
                  % (k, o["n"], o["toplam"], o["medyan"]))

        print("\n  -- OLUM SURESI (tutma saati)")
        kov = [(0, 1, "<1 sa"), (1, 2, "1-2 sa"), (2, 4, "2-4 sa"),
               (4, 8, "4-8 sa"), (8, 24, "8-24 sa"), (24, 1e9, ">24 sa")]
        for a, b, ad in kov:
            v = [p["pnl"] for p in g if a <= (p["tutma_saat"] or 0) < b]
            if v:
                o = ortak.ozet(v)
                print("     %-8s N=%3d  toplam %+9.2f  medyan %+7.2f  kazanan %%%.0f"
                      % (ad, o["n"], o["toplam"], o["medyan"], o["kazanma_pct"]))

    # MFE/MAE — "artiya gecip geri mi verdi"
    print("\n### ARTIYA GECIP GERI VERDI MI?  (5dk mumdan MFE/MAE)")
    for yon in ("SHORT", "LONG"):
        for dn in ("oncesi", "sonrasi"):
            g = [p for p in poz if p["yon"] == yon and p["donem"] == dn]
            if len(g) < 3:
                continue
            mf, ma, gr = [], [], 0
            for p in g:
                a, b = mfe_mae(p)
                if a is None:
                    continue
                mf.append(a)
                ma.append(b)
                if a >= 2.0 and p["pnl"] < 0:
                    gr += 1
            if not mf:
                continue
            print("  %-5s %-8s N=%3d  MFE medyan %+6.2f%%  MAE medyan %+6.2f%%"
                  % (yon, dn, len(mf), stx.median(mf), stx.median(ma)))
            print("        %%2'den fazla artiya gecip ZARARLA kapanan: %d/%d (%%%.0f)"
                  % (gr, len(mf), 100 * gr / len(mf)))

    # fonlama — sinirli
    fv = [p for p in poz if p.get("d_funding_usdt") is not None]
    print("\n### FONLAMA — defterde olculu olan %d/%d pozisyon" % (len(fv), len(poz)))
    if fv:
        for yon in ("SHORT", "LONG"):
            g = [p["d_funding_usdt"] for p in fv if p["yon"] == yon]
            if g:
                print("  %-5s N=%2d  toplam %+8.2f  (pozitif = defter TAHSIL etti)"
                      % (yon, len(g), sum(g)))
    print("  UYARI: alan 2026-08-17'de eklendi; oncesi geri uretilemez.")


if __name__ == "__main__":
    for t in ("muhasebe_11agu", "hakem_12agu"):
        kostur(t)
    print("\nbot dosyalarina yazim: YOK")
