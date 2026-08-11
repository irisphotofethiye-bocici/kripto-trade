#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASGARI STOP TABANI: ELE mi, GENISLET mi? (2026-08-11)

BULGU (boyut_agirlik.py): canli kapinin karini YALNIZ genis stoplu islemler
tasiyor. Stop dilimlerine gore isabet: %10.3 / %20.1 / %33.3 / %56.2 —
monoton. Basabas orani stop/(10+stop) oldugundan dar stoplu dilim
matematiksel olarak KAYBEDIYOR (%10.3 isabet, %16 gerekiyordu).
Ustelik kaldirac tavani yuzunden bot en dar stoplu (degersiz) islemi
sermayenin 1.00 katiyla, en karli genis stoplu islemi 0.40 katiyla aliyor.

IKI COZUM VAR, hangisi dogru OLCULMELI:
  ELE      : stop_frac < taban ise girisi REDDET  (islem sayisi duser)
  GENISLET : stop'u tabana it, pozisyonu ona gore kucult (islem sayisi ayni)
GENISLET onemli cunku dar stoplu islemler "kotu kurulum" degil "gurultuye
cok yakin stop" olabilir; stop acilinca ayni kurulum kazanabilir.

KONTROL: taban=0 (bugunku canli hal) her tabloda ilk satirdir.
ON-KAYIT: taban secimi tablonun MAKSIMUMUNDAN degil, iki yarida da pozitif
kalan ve mekanik gerekcesi olan (basabas cizgisinin gectigi) yerden secilecek.
"""
import json, os, sys, statistics as stx, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yon_dogrula as yd
import yon_avi

PUMP, RISK_PCT, MARJIN_PCT, KALD_MAX = 20.0, 0.03, 0.10, 10
NBAR, MALIYET = 10, 0.09


def gecer_ab(o):
    return (o.get("funding") or 0) <= -0.05 and (o.get("oi24") or 0) >= 10


def gecer_ma50(o):
    px = 10 ** o["fiyat_log"] if o.get("fiyat_log") is not None else None
    return px is not None and px <= 0.07 and (o.get("ma50_mesafe") or -99) >= 3.72


def canli_kapi(o):
    return (gecer_ab(o) or gecer_ma50(o)) and (o.get("chg24") or 0) < PUMP


def islem_taban(b, gi, hedef_pct, ufuk, taban_pct):
    """yd.islem ile ayni SHORT mekanigi; stop tabandan dar cikarsa TABANA GENISLETILIR."""
    i = gi - 1
    if i < 200 or gi >= len(b):
        return None
    a = yd.atr(b, i)
    if not a or a <= 0:
        return None
    ref = b[gi]["o"]
    hi, _ = yd.swings2(b, i)
    res = min([x for x in hi if x > ref], default=None)
    ad = []
    if res is not None and (res - ref) <= 3 * a:
        ad.append(res + 0.25 * a)
    nb = max(x["h"] for x in b[max(0, i - NBAR + 1):i + 1])
    if nb > ref:
        ad.append(nb + 0.25 * a)
    ad.append(ref + 1.5 * a)
    gec = [s for s in ad if s > ref]
    stop = min(gec) if gec else ref + 1.5 * a
    sp = (stop - ref) / ref * 100
    if sp <= 0:
        return None
    if sp < taban_pct:                      # <-- TEK FARK: tabana genislet
        sp = taban_pct
        stop = ref * (1 + sp / 100)
    hedef = ref * (1 - hedef_pct / 100)
    son = min(gi + ufuk, len(b))
    if son - gi < 4:
        return None
    for j in range(gi, son):
        x = b[j]
        if x["h"] >= stop:
            return -sp - MALIYET, "STOP", sp
        if x["l"] <= hedef:
            return hedef_pct - MALIYET, "HEDEF", sp
    c = b[son - 1]["c"]
    return (ref - c) / ref * 100 - MALIYET, "SURE", sp


def boyut(sp):
    return min(RISK_PCT / (sp / 100.0), MARJIN_PCT * KALD_MAX)


def main():
    ge = yon_avi.yukle()
    bc, idxc = {}, {}
    for o in ge:
        s = o["sym"]
        if s not in bc:
            p = os.path.join(yd.CACHE, f"{s}.json")
            bc[s] = json.load(open(p)) if os.path.exists(p) else None
            if bc[s]:
                idxc[s] = {x["t"] // 3600000: i for i, x in enumerate(bc[s])}
        if not bc[s]:
            continue
        ms = int(datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M").astimezone().timestamp() * 1000)
        o["_b"], o["_gi"] = bc[s], idxc[s].get(ms // 3600000)
    sec = [o for o in ge if o.get("_gi") is not None and canli_kapi(o)]
    tsl = sorted(o["ts"] for o in ge)
    ORTA = tsl[len(tsl) // 2]

    print("=" * 112)
    print("ASGARI STOP TABANI — ELE vs GENISLET · canli boyutlandirmayla · hedef %10 / 72s")
    print("=" * 112)
    print(f"Canli kapi olay sayisi: {len(sec)}   ·   taban %0.0 satiri = BUGUNKU CANLI HAL\n")
    print(f"{'taban':10}{'|':2}{'ELE: N':>8}{'olay/gun':>10}{'net %':>8}{'A yari':>8}{'B yari':>8}"
          f"{'toplam':>9}{'|':3}{'GENISLET: N':>13}{'net %':>8}{'A yari':>8}{'B yari':>8}{'toplam':>9}")
    print("-" * 112)
    GUN = 46.0
    for taban in (0.0, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0):
        eV, gV = [], []
        for o in sec:
            r0 = yd.islem(o["_b"], o["_gi"] + 1, 10.0, 72, "SHORT")
            if r0 and r0[2] >= taban:
                eV.append((o["ts"], r0[0] * boyut(r0[2])))
            r1 = islem_taban(o["_b"], o["_gi"] + 1, 10.0, 72, taban)
            if r1:
                gV.append((o["ts"], r1[0] * boyut(r1[2])))
        if len(eV) < 60 or len(gV) < 60:
            continue
        def oz(v):
            A = [x[1] for x in v if x[0] < ORTA]; B = [x[1] for x in v if x[0] >= ORTA]
            return (stx.mean([x[1] for x in v]), stx.mean(A) if A else 0,
                    stx.mean(B) if B else 0, sum(x[1] for x in v))
        e = oz(eV); g = oz(gV)
        print(f"%{taban:<9.1f}{'|':2}{len(eV):8d}{len(eV)/GUN:10.1f}{e[0]:+8.2f}{e[1]:+8.2f}{e[2]:+8.2f}"
              f"{e[3]:+9.0f}{'|':3}{len(gV):13d}{g[0]:+8.2f}{g[1]:+8.2f}{g[2]:+8.2f}{g[3]:+9.0f}")
    print("-" * 112)
    print("  net % = olay basina SERMAYENIN yuzdesi (canli boyutlandirmayla)")
    print("  ELE = girisi reddet · GENISLET = stopu tabana it, pozisyonu kucult")

    print("\n" + "=" * 112)
    print("GENISLETILEN ISLEMLERIN KENDI KARNESI — sadece stop<%2.0 olan olaylar")
    print("=" * 112)
    print(f"{'':22}{'N':>6}{'isabet':>9}{'stop med':>10}{'net % (canli)':>15}{'toplam':>10}")
    print("-" * 112)
    dar = []
    for o in sec:
        r0 = yd.islem(o["_b"], o["_gi"] + 1, 10.0, 72, "SHORT")
        if r0 and r0[2] < 2.0:
            dar.append(o)
    for ad, taban in (("bugunku (taban yok)", 0.0), ("stop %2.0'a genisletilmis", 2.0),
                      ("stop %3.0'a genisletilmis", 3.0)):
        v = []
        for o in dar:
            r = islem_taban(o["_b"], o["_gi"] + 1, 10.0, 72, taban)
            if r:
                v.append(r)
        if not v:
            continue
        print(f"{ad:22}{len(v):6d}{sum(1 for x in v if x[1]=='HEDEF')/len(v)*100:8.1f}%"
              f"{stx.median([x[2] for x in v]):9.2f}%"
              f"{stx.mean([x[0]*boyut(x[2]) for x in v]):+15.2f}"
              f"{sum(x[0]*boyut(x[2]) for x in v):+10.0f}")


if __name__ == "__main__":
    main()
