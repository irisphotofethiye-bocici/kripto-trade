#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FREN RISKI (2026-08-11) — kenar kendini gostermeden -%25 freni tetiklenir mi?

SORU (kullanici): kapilar bu hizda calisirken es zamanli maruziyet sermayenin
2,2 katina cikti ve 9 saatte -%15,9 dusus olustu. Kenarin belli olmasi ~138 islem
(~11 gun) sururken, HALT freni ondan ONCE tetiklenirse bot durur ve kenar hic
gorunmez. Bu olasilik nedir, ve maruziyet tavani onu ne kadar dusurup
beklentiden ne goturur?

BU BIR PORTFOY SIMULASYONU — tek tek islem ortalamasi degil. Onemli fark:
  - 8 slot siniri: olaylarin hepsi alinamaz
  - 4 saat cooldown (sembol basina)
  - ES ZAMANLILIK: ayni gun icinde olaylar KUMELENIR (piyasa geneli hareket eder),
    bu yuzden kayiplar bagimsiz degil — ruin riskini asil bu yaratir.

BOOTSTRAP TASARIMI: 46 gunun GUN BLOKLARI yerine konarak yeniden ornekleniyor.
  Gun bloklu olmasi sart: bir olayin sonucunu tek basina karistirmak, ayni gun
  butun shortlarin birlikte kazanip birlikte kaybettigi gercegini yok ederdi
  (korelasyonu silmek ruin riskini SAHTE sekilde dusururdu).
  Her olayin kendi (stop%, sonuc%, sure) ucgeni BOZULMADAN tasiniyor.

ON-KAYIT: karsilastirilacak senaryolar ve karar olcutu ONCEDEN sabit:
  S0 bugunku hal · S1 stop tabani %2 · S2 maruziyet tavani 3x · S3 ikisi birden
  KARAR OLCUTU: 11 gun icinde HALT olasiligini yariya indirirken 46 gunluk
  medyan getiriden %25'ten fazla goturmeyen senaryo tercih edilir.
"""
import json, os, sys, random, statistics as stx, datetime, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yon_dogrula as yd
import yon_avi

PUMP = 20.0
RISK_PCT, MARJIN_PCT, KALD_MAX = 0.03, 0.10, 10
SLOT, COOLDOWN_S, HALT = 8, 4.0, 0.25
NBAR, MALIYET = 10, 0.09
random.seed(7)


def gecer_ab(o):
    return (o.get("funding") or 0) <= -0.05 and (o.get("oi24") or 0) >= 10


def gecer_ma50(o):
    px = 10 ** o["fiyat_log"] if o.get("fiyat_log") is not None else None
    return px is not None and px <= 0.07 and (o.get("ma50_mesafe") or -99) >= 3.72


def canli_kapi(o):
    return (gecer_ab(o) or gecer_ma50(o)) and (o.get("chg24") or 0) < PUMP


def islem_sureli(b, gi, hedef_pct=10.0, ufuk=72):
    """SHORT; yd.islem ile ayni mekanik + SURE (kac saat sonra kapandi) doner."""
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
    hedef = ref * (1 - hedef_pct / 100)
    son = min(gi + ufuk, len(b))
    if son - gi < 4:
        return None
    for j in range(gi, son):
        x = b[j]
        if x["h"] >= stop:
            return -sp - MALIYET, sp, j - gi + 1
        if x["l"] <= hedef:
            return hedef_pct - MALIYET, sp, j - gi + 1
    c = b[son - 1]["c"]
    return (ref - c) / ref * 100 - MALIYET, sp, son - gi


def olaylari_hazirla():
    ge = yon_avi.yukle()
    bc, idxc = {}, {}
    out = []
    for o in ge:
        if not canli_kapi(o):
            continue
        s = o["sym"]
        if s not in bc:
            p = os.path.join(yd.CACHE, f"{s}.json")
            bc[s] = json.load(open(p)) if os.path.exists(p) else None
            if bc[s]:
                idxc[s] = {x["t"] // 3600000: i for i, x in enumerate(bc[s])}
        if not bc[s]:
            continue
        t = datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M")
        ms = int(t.astimezone().timestamp() * 1000)
        gi = idxc[s].get(ms // 3600000)
        if gi is None:
            continue
        r = islem_sureli(bc[s], gi + 1)
        if not r:
            continue
        g, sp, sure = r
        out.append({"gun": t.date(), "sa": t.hour + t.minute / 60.0,
                    "sym": s, "g": g, "sp": sp, "sure": sure})
    out.sort(key=lambda x: (x["gun"], x["sa"]))
    return out


def simule(gunler, taban, tavan, risk=RISK_PCT):
    """gunler: [[olay,...], ...] siralanmis gun bloklari. Doner: (bitis_carpani, halt_gun, min_dd)"""
    eq, zirve, acik, cool = 1.0, 1.0, [], {}
    saat0, halt_gun, min_dd = 0.0, None, 0.0
    for gi, gun in enumerate(gunler):
        for o in gun:
            simdi = saat0 + o["sa"]
            # once vadesi gelen pozisyonlari kapat (sira onemli: slot ve sermaye serbest kalir)
            kalan = []
            for p in acik:
                if p["kapanis"] <= simdi:
                    eq += p["notional"] * p["g"] / 100.0
                    zirve = max(zirve, eq)
                    min_dd = min(min_dd, eq / zirve - 1)
                    if halt_gun is None and eq / zirve - 1 <= -HALT:
                        halt_gun = gi + o["sa"] / 24.0
                else:
                    kalan.append(p)
            acik = kalan
            if halt_gun is not None:
                continue
            if o["sp"] < taban:
                continue
            if len(acik) >= SLOT:
                continue
            if cool.get(o["sym"], -99) > simdi - COOLDOWN_S:
                continue
            notional = min(risk / (o["sp"] / 100.0), MARJIN_PCT * KALD_MAX) * eq
            if tavan:
                bos = tavan * eq - sum(p["notional"] for p in acik)
                if bos <= 0:
                    continue
                notional = min(notional, bos)
            cool[o["sym"]] = simdi
            acik.append({"notional": notional, "g": o["g"], "kapanis": simdi + o["sure"]})
        saat0 += 24.0
    for p in acik:
        eq += p["notional"] * p["g"] / 100.0
    zirve = max(zirve, eq); min_dd = min(min_dd, eq / zirve - 1)
    return eq, halt_gun, min_dd


def main():
    ol = olaylari_hazirla()
    gun_map = collections.OrderedDict()
    for o in ol:
        gun_map.setdefault(o["gun"], []).append(o)
    bloklar = list(gun_map.values())
    N_GUN = len(bloklar)
    print("=" * 108)
    print("FREN RISKI — portfoy simulasyonu (8 slot · 4s cooldown · gun-bloklu bootstrap)")
    print("=" * 108)
    print(f"Olay: {len(ol)}  ·  gun: {N_GUN}  ·  gun basina ortalama {len(ol)/N_GUN:.1f} olay")
    print(f"HALT esigi: -%{HALT*100:.0f}  ·  kenarin belli olmasi ~11 gun\n")

    SEN = [("S0  bugunku hal (risk %3)", 0.0, None, 0.03),
           ("S1  stop tabani %2", 2.0, None, 0.03),
           ("S2  maruziyet tavani 3x", 0.0, 3.0, 0.03),
           ("S3  taban %2 + tavan 3x", 2.0, 3.0, 0.03),
           ("S4  taban %2 + tavan 2x", 2.0, 2.0, 0.03),
           ("S5  YALNIZ risk %3->%2", 0.0, None, 0.02),
           ("S6  YALNIZ risk %3->%1.5", 0.0, None, 0.015),
           ("S7  risk %2 + taban %2", 2.0, None, 0.02),
           ("S8  risk %2 + taban %2 + tavan 3x", 2.0, 3.0, 0.02),
           ("S9  risk %1.5 + taban %2", 2.0, None, 0.015)]

    print("### A) GERCEK SIRA (tek tarihsel yol, 46 gun)")
    print(f"{'senaryo':34}{'bitis carpani':>15}{'en dip dusus':>15}{'HALT':>10}")
    print("-" * 108)
    for ad, tb, tv, rk in SEN:
        eq, hg, dd = simule(bloklar, tb, tv, rk)
        print(f"{ad:34}{eq:15.2f}{dd*100:14.1f}%"
              f"{('gun ' + format(hg, '.1f')) if hg is not None else 'yok':>10}")

    NSIM = 2000
    print(f"\n### B) BOOTSTRAP — {NSIM} yol, gun bloklari yerine konarak orneklendi")
    print(f"{'senaryo':34}{'11g HALT':>10}{'46g HALT':>10}{'medyan 46g':>12}"
          f"{'alt %5':>9}{'ust %95':>9}{'medyan dip':>12}{'kayip yol':>11}")
    print("-" * 108)
    tab = {}
    for ad, tb, tv, rk in SEN:
        random.seed(7)
        son11, son46, carp, dip = 0, 0, [], []
        for _ in range(NSIM):
            g11 = [random.choice(bloklar) for _ in range(11)]
            e, h, d = simule(g11, tb, tv, rk)
            if h is not None:
                son11 += 1
            g46 = g11 + [random.choice(bloklar) for _ in range(35)]
            e, h, d = simule(g46, tb, tv, rk)
            if h is not None:
                son46 += 1
            carp.append(e); dip.append(d)
        carp.sort()
        tab[ad] = (son11 / NSIM, son46 / NSIM, stx.median(carp), stx.median(dip))
        print(f"{ad:34}{son11/NSIM*100:9.1f}%{son46/NSIM*100:9.1f}%{stx.median(carp):12.2f}"
              f"{carp[int(NSIM*0.05)]:9.2f}{carp[int(NSIM*0.95)]:9.2f}"
              f"{stx.median(dip)*100:11.1f}%{sum(1 for x in carp if x < 1)/NSIM*100:10.1f}%")
    print("-" * 108)
    print("  'bitis carpani' 1.00 = basabas · 2.00 = sermaye iki kati")
    print("  '11g HALT' = kenarin belli olmasi beklenen sureden ONCE freni tetikleme olasiligi")

    print("\n### C) KARAR OLCUTU (on-kayitli): 11g HALT'i YARIYA indir, medyandan %25'ten fazla goturme")
    b0 = tab["S0  bugunku hal (risk %3)"]
    for ad, tb, tv, rk in SEN[1:]:
        b = tab[ad]
        halt_dus = (1 - b[0] / b0[0]) * 100 if b0[0] else 0
        d_get = ((b[2] - 1) / (b0[2] - 1) - 1) * 100 if b0[2] > 1 else float("nan")
        gec = "GECER" if b[0] <= b0[0] / 2 and d_get >= -25 else "gecmez"
        print(f"  {ad:34} 11g HALT {halt_dus:+.0f}%  |  getiri {d_get:+.0f}%  ->  {gec}")


if __name__ == "__main__":
    main()
