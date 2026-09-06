#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""'900 dolarlik pozda 90 dolar kar al + stopu basabasa cek' — OLCUM (2026-09-06)

Kullanici fikri: marjinin %10'u kar olunca KISMI KAR al, kalanin stopunu
basabasa cek. Canli pozisyonlarda tetik: %2-3,33 FIYAT = 0,32-0,60 R.

KOLLAR (ayni girisler, hicbiri stopsuz):
   A0        mevcut: sabit %10 hedef, kismi YOK, stop sabit
   K(t,pay)  fiyat +t%%'e degince pay kadari KAPATILIR + stop = giris*(1+%0,20)
             kalan, +%10 hedefe ya da yeni stopa gider

Tetik ve paylar KOSUMDAN ONCE betiğe yazildi.
IKI YARI (kesif/holdout) AYRI raporlanir.

🟡 BETIMLEYICI. SALT-OKUNUR.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, sys, math, collections, statistics as stx
import importlib.util as il

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
sp = il.spec_from_file_location(
    "ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)

TETIK = [2.0, 3.0]            # % fiyat — kullanicinin 90$/900$ karsiligi
PAYLAR = [0.5, 1.0]           # kapatilan oran (1,0 = tamami)
BAB_PAY = 0.20                # basabasin "biraz ustu" %


def simule(d, ix, i0, g, stop0, tetik=None, pay=0.0):
    """-> net R (maliyet dahil). tetik None -> A0."""
    h = g * 1.10
    risk_pct = (g - stop0) / g * 100.0
    stop = stop0
    bab = g * (1 + BAB_PAY / 100.0)
    kalan = 1.0
    banka = 0.0                      # realize edilmis kar (yuzde-notional)
    for j in range(i0 + 1, min(i0 + 1 + ar.ZAMAN_STOP, len(d))):
        b = d[j]
        # once STOP (muhafazakar)
        if b["l"] <= stop:
            son = (stop / g - 1) * 100.0
            return (banka + kalan * son - ar.MALIYET) / risk_pct
        if b["h"] >= h:
            son = (h / g - 1) * 100.0
            return (banka + kalan * son - ar.MALIYET) / risk_pct
        if tetik is not None and kalan == 1.0 and b["h"] >= g * (1 + tetik / 100.0):
            banka += pay * tetik          # tetik seviyesinde kismi realize
            kalan -= pay
            stop = max(stop, bab)
            if kalan <= 1e-9:
                return (banka - ar.MALIYET) / risk_pct
    j = min(i0 + ar.ZAMAN_STOP, len(d) - 1)
    if j <= i0:
        return None
    son = (d[j]["c"] / g - 1) * 100.0
    return (banka + kalan * son - ar.MALIYET) / risk_pct


def main():
    mum = ar.mumlar()
    rows, son_t = [], {}
    for l in io.open(os.path.join(KOK, "radar_archive.jsonl"),
                     encoding="utf-8", errors="ignore"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        s, p = r.get("sym"), r.get("price")
        if not s or not p or s not in mum or (r.get("score") or 0) < ar.SKOR_MIN:
            continue
        t = ar.ts_ms(r["ts"])
        if s in son_t and (t - son_t[s]) < ar.COOLDOWN * 3_600_000:
            continue
        d, ix = mum[s]
        i0 = ix.get(t)
        if i0 is None or i0 < ar.YAPI_BAR:
            continue
        stop = ar.stop_hesapla(d[i0 - ar.YAPI_BAR:i0], p)
        if stop is None or (p - stop) / p * 100.0 < ar.ASGARI_STOP:
            continue
        son_t[s] = t
        a0 = simule(d, ix, i0, p, stop)
        if a0 is None:
            continue
        rec = {"gun": r["ts"][:10], "A0": a0}
        ok = True
        for tk in TETIK:
            for pay in PAYLAR:
                v = simule(d, ix, i0, p, stop, tk, pay)
                if v is None:
                    ok = False
                rec["K%.0f_%.0f" % (tk, pay * 100)] = v
        if ok:
            rows.append(rec)

    gunler = sorted(set(x["gun"] for x in rows))
    ks = gunler[int(len(gunler) * ar.KESIF_PAY)]
    parca = [("KESIF", [x for x in rows if x["gun"] < ks]),
             ("HOLDOUT", [x for x in rows if x["gun"] >= ks]),
             ("TUMU", rows)]
    kollar = ["K%.0f_%.0f" % (t, p * 100) for t in TETIK for p in PAYLAR]

    print("'90/900 dolar kar al + basabas' — N=%d giris · %d gun" % (len(rows), len(gunler)))
    print("kol adi: K<tetik%%>_<kapatilan pay%%>   (basabas payi %%%.2f)" % BAB_PAY)
    print()
    bas = "%-10s %10s" % ("pencere", "A0")
    for k in kollar:
        bas += " %10s" % k
    print(bas)
    for ad, p in parca:
        if not p:
            continue
        sat = "%-10s %+10.4f" % (ad, stx.mean([x["A0"] for x in p]))
        for k in kollar:
            sat += " %+10.4f" % stx.mean([x[k] for x in p])
        print(sat)
    print()
    print("ESLESMIS FARK (kol - A0), gun-kumeli t:")
    print("%-10s %-10s %11s %9s" % ("pencere", "kol", "fark R", "t"))
    for ad, p in parca:
        if len(p) < 50:
            continue
        for k in kollar:
            f = [x[k] - x["A0"] for x in p]
            g = collections.defaultdict(list)
            for x, v in zip(p, f):
                g[x["gun"]].append(v)
            gv = [stx.mean(v) for v in g.values()]
            m = stx.mean(gv)
            se = stx.stdev(gv) / math.sqrt(len(gv)) if len(gv) > 2 else 0
            print("%-10s %-10s %+11.4f %+9.2f" % (ad, k, stx.mean(f), (m / se if se else 0)))
        print()
    print("🟡 Betimleyici. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
