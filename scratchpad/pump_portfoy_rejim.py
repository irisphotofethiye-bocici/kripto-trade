#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REJIM DISI KONTROL — pump<45 boga BITINCE ne yapiyor?

Boga bacagi olcumu (+%43,5) tek rejim epizodu. Bot her rejimde kosar.
Golge 2026-08-10'dan beri kayitli -> BOGA ONCESI 9 gunluk NOTR pencere BEDAVA.

Pencereler (BTC gunluk kapanis, scratchpad/perp_seri/BTC_kline.json):
   NOTR/DUSUS  08-10 .. 08-18   63.939 -> 64.694   (yatay, dip 62.876)
   BOGA        08-19 .. 08-25   69.310 -> 78.741   (dikey + plato)

Ayni sim, ayni kisitlar, ayni skor esigi. Esik BOGA'da secildiyse ve NOTR'de
cokuyorsa "bota ekle" cevabi DEGISIR.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, re, datetime, collections, bisect

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = "%Y-%m-%d %H:%M:%S"
VOLX = re.compile(r"vol_x\s+([0-9.]+)x")
MAKS_POZ = 8
MAKS_DUSUS = 25.0

PENCERE = [("NOTR  08-10..08-18", datetime.datetime(2026, 8, 10), datetime.datetime(2026, 8, 19)),
           ("BOGA  08-19..08-25", datetime.datetime(2026, 8, 19), datetime.datetime(2026, 9, 1)),
           ("TUMU  08-10..08-25", datetime.datetime(2026, 8, 10), datetime.datetime(2026, 9, 1))]


def jl(y):
    p = os.path.join(PROJE, y)
    out = []
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            for s in f:
                if s.strip():
                    try:
                        out.append(json.loads(s))
                    except Exception:
                        pass
    return out


def equity_serisi(y):
    p = sorted((datetime.datetime.strptime(x["ts"], F), x.get("equity") or 0)
               for x in jl(y) if x.get("ts"))
    return [a for a, b in p], [b for a, b in p]


def equity_at(zs, es, t):
    i = bisect.bisect_right(zs, t) - 1
    return es[i] if 0 <= i < len(es) else (es[0] if es else 10000.0)


def adaylar(dosya, eq_dosya):
    zs, es = equity_serisi(eq_dosya)
    g = collections.defaultdict(list)
    for x in jl(dosya):
        g[x["id"]].append(x)
    out = []
    for i, v in g.items():
        v.sort(key=lambda z: z["ts"])
        ilk, son = v[0], v[-1]
        gt = (datetime.datetime.strptime(ilk["ts"], F)
              - datetime.timedelta(hours=(ilk.get("tutma_saat") or 0)))
        kt = datetime.datetime.strptime(son["ts"], F)
        no = ilk.get("notional") or 0
        if not no or kt <= gt:
            continue
        net = sum((t.get("sonuc_usdt") or 0) for t in v)
        fon = [t.get("funding_usdt") for t in v if t.get("funding_usdt") is not None]
        eq = equity_at(zs, es, gt) or 10000.0
        m = VOLX.search(son.get("sebep_giris") or "")
        out.append(dict(sym=son["sym"], yon=son["yon"], gir=gt, kap=kt,
                        pct=100.0 * net / no, fon_frac=(sum(fon) / no) if fon else 0.0,
                        exp=no / eq, kaynak=son.get("kaynak") or "testbot",
                        skor=ilk.get("skor_giriste"), chg24=ilk.get("chg24_giriste"),
                        vol_x=float(m.group(1)) if m else None))
    return out


BOT_ALL = adaylar("testbot_islemler.jsonl", "testbot_equity.jsonl")
GOL_ALL = adaylar("golge_islemler.jsonl", "golge_equity.jsonl")


def sim(havuz, bas, maks_poz=MAKS_POZ, fren=MAKS_DUSUS):
    eq, tepe, dd = bas, bas, 0.0
    acik = []
    alinan = 0
    donmus = False
    for a in sorted(havuz, key=lambda z: z["gir"]):
        acik.sort(key=lambda z: z[0])
        while acik and acik[0][0] <= a["gir"]:
            kt, poz, no = acik.pop(0)
            eq += poz["pct"] / 100.0 * no + poz["fon_frac"] * no
            tepe = max(tepe, eq)
            dd = max(dd, 100.0 * (1 - eq / tepe))
        if fren and 100.0 * (1 - eq / tepe) >= fren:
            donmus = True
        if donmus or len(acik) >= maks_poz or any(p[1]["sym"] == a["sym"] for p in acik):
            continue
        acik.append((a["kap"], a, a["exp"] * eq))
        alinan += 1
    for kt, poz, no in sorted(acik, key=lambda z: z[0]):
        eq += poz["pct"] / 100.0 * no + poz["fon_frac"] * no
        tepe = max(tepe, eq)
        dd = max(dd, 100.0 * (1 - eq / tepe))
    return eq, dd, alinan, donmus


print("REJIM DISI KONTROL — ayni kural, boga ONCESI notr pencerede")
print("=" * 118)

for ad, t0, t1 in PENCERE:
    bot = [z for z in BOT_ALL if t0 <= z["gir"] < t1]
    gol = [z for z in GOL_ALL if t0 <= z["gir"] < t1]
    pump = [z for z in gol if "pump_long" in z["kaynak"]]
    lo = [z for z in pump if z["skor"] is not None and z["skor"] < 45]
    hi = [z for z in pump if z["skor"] is not None and z["skor"] >= 45]
    bot_long = [z for z in bot if z["yon"] == "LONG"]
    zs, es = equity_serisi("testbot_equity.jsonl")
    bas = equity_at(zs, es, t0)
    print("\n%s   baslangic equity %.2f   (havuz: pump %d · skor<45 %d · bot LONG %d)"
          % (ad, bas, len(pump), len(lo), len(bot_long)))
    print("-" * 118)
    for kol, hav in (("pump skor<45      (ONERI)", lo),
                     ("pump skor>=45     (kontrol)", hi),
                     ("pump tum bantlar", pump),
                     ("bot LONG          (mevcut kural)", bot_long),
                     ("bot TUMU          (LONG+SHORT)", bot)):
        if not hav:
            print("   %-34s havuz BOS" % kol)
            continue
        eq, dd, al, don = sim(hav, bas)
        print("   %-34s son equity %9.2f  (%+7.2f%%)  maks dd %5.1f%%  alinan %3d  fren %s"
              % (kol, eq, 100.0 * (eq / bas - 1), dd, al, "TETIKLEDI" if don else "-"))

print("\n" + "=" * 118)
print("ISLEM BASI GETIRI — rejime gore (portfoyden BAGIMSIZ, boyut etkisi yok)")
print("=" * 118)
print("   %-34s %8s %11s %11s %9s" % ("kol", "N", "medyan%", "ort%", "kazanan"))
for ad, t0, t1 in PENCERE[:2]:
    print("   --- %s" % ad)
    gol = [z for z in GOL_ALL if t0 <= z["gir"] < t1]
    bot = [z for z in BOT_ALL if t0 <= z["gir"] < t1]
    pump = [z for z in gol if "pump_long" in z["kaynak"]]
    for kol, hav in (("pump skor<45", [z for z in pump if z["skor"] is not None and z["skor"] < 45]),
                     ("pump skor>=45", [z for z in pump if z["skor"] is not None and z["skor"] >= 45]),
                     ("bot LONG", [z for z in bot if z["yon"] == "LONG"]),
                     ("bot SHORT", [z for z in bot if z["yon"] == "SHORT"])):
        if not hav:
            continue
        p = [z["pct"] for z in hav]
        import statistics as sx
        print("   %-34s %8d %+10.3f%% %+10.3f%% %8.0f%%"
              % (kol, len(p), sx.median(p), sum(p) / len(p),
                 100.0 * sum(1 for x in p if x > 0) / len(p)))

print("\n" + "=" * 118)
print("SKOR ESIGI — NOTR penceresinde de 40-50 platosu var mi (yoksa esik BOGA'ya uydurulmus)")
print("=" * 118)
for ad, t0, t1 in PENCERE[:2]:
    gol = [z for z in GOL_ALL if t0 <= z["gir"] < t1]
    pump = [z for z in gol if "pump_long" in z["kaynak"]]
    zs, es = equity_serisi("testbot_equity.jsonl")
    bas = equity_at(zs, es, t0)
    sat = []
    for esik in (35, 40, 45, 50, 55, 60):
        w = [z for z in pump if z["skor"] is not None and z["skor"] < esik]
        sat.append("<%d: %+6.1f%% (N=%d)" % (esik, 100.0 * (sim(w, bas)[0] / bas - 1), len(w))
                   if len(w) >= 10 else "<%d: N<10" % esik)
    print("   %-20s %s" % (ad, "   ".join(sat)))

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
