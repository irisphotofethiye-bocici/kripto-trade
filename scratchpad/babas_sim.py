#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BASABAS STOPU — GERCEK R ETKISI (2026-09-06)

Kullanici fikri: kar +X%%'e ulasinca stop basabasin biraz ustune.
Kayitli olcum KISMI KAR SONRASI basabasi olcmustu; bu KISMI KARSIZ versiyon.

Kollar (AYNI girisler, hicbiri stopsuz — CLAUDE.md deseni (b)):
   A0   : mevcut (olcucu stop ATR14 · sabit %10 · 48s)
   B(X) : ayni, AMA fiyat +X%%'e degince stop = giris * (1 + %0,20)

Tetik degerleri KOSUMDAN ONCE betiğe yazildi: 1 · 2 · 3 · 5
IKI YARI (kesif/holdout) AYRI raporlanir -> kararliligi hemen gorunur.

🟡 BETIMLEYICI — hukum icin ayri on-kayit gerekir. SALT-OKUNUR.
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

TETIK = [1.0, 2.0, 3.0, 5.0]
PAY = 0.20


def simule(d, ix, i0, g, stop0, tetik=None):
    """tetik None -> A0. Degilse +tetik%%'te stop basabasin %0,20 ustune."""
    h = g * 1.10
    stop = stop0
    risk_pct = (g - stop0) / g * 100.0
    bab = g * (1 + PAY / 100.0)
    tetiklendi = False
    for j in range(i0 + 1, min(i0 + 1 + ar.ZAMAN_STOP, len(d))):
        b = d[j]
        if b["l"] <= stop:
            return ((stop / g - 1) * 100.0 - ar.MALIYET) / risk_pct
        if b["h"] >= h:
            return ((h / g - 1) * 100.0 - ar.MALIYET) / risk_pct
        if tetik is not None and not tetiklendi and b["h"] >= g * (1 + tetik / 100.0):
            tetiklendi = True
            stop = max(stop, bab)
    j = min(i0 + ar.ZAMAN_STOP, len(d) - 1)
    if j <= i0:
        return None
    return ((d[j]["c"] / g - 1) * 100.0 - ar.MALIYET) / risk_pct


def main():
    mum = ar.mumlar()
    rows, son = [], {}
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
        if s in son and (t - son[s]) < ar.COOLDOWN * 3_600_000:
            continue
        d, ix = mum[s]
        i0 = ix.get(t)
        if i0 is None or i0 < ar.YAPI_BAR:
            continue
        stop = ar.stop_hesapla(d[i0 - ar.YAPI_BAR:i0], p)
        if stop is None:
            continue
        if (p - stop) / p * 100.0 < ar.ASGARI_STOP:
            continue
        son[s] = t
        a0 = simule(d, ix, i0, p, stop)
        if a0 is None:
            continue
        rec = {"gun": r["ts"][:10], "A0": a0}
        for X in TETIK:
            rec["B%.0f" % X] = simule(d, ix, i0, p, stop, X)
        if any(rec["B%.0f" % X] is None for X in TETIK):
            continue
        rows.append(rec)

    gunler = sorted(set(x["gun"] for x in rows))
    ks = gunler[int(len(gunler) * ar.KESIF_PAY)]
    parca = [("KESIF", [x for x in rows if x["gun"] < ks]),
             ("HOLDOUT", [x for x in rows if x["gun"] >= ks]),
             ("TUMU", rows)]

    print("BASABAS STOPU — gercek R etkisi (N=%d giris · %d gun)" % (len(rows), len(gunler)))
    print()
    print("%-10s %10s %10s %10s %10s %10s" %
          ("pencere", "A0", "B+1%", "B+2%", "B+3%", "B+5%"))
    for ad, p in parca:
        if not p:
            continue
        sat = "%-10s %+10.4f" % (ad, stx.mean([x["A0"] for x in p]))
        for X in TETIK:
            sat += " %+10.4f" % stx.mean([x["B%.0f" % X] for x in p])
        print(sat)
    print()
    print("ESLESMIS FARK (B - A0), gun-kumeli t ile:")
    print("%-10s %-12s %11s %9s %9s" % ("pencere", "kol", "fark R", "t", "gun"))
    for ad, p in parca:
        if len(p) < 50:
            continue
        for X in TETIK:
            f = [x["B%.0f" % X] - x["A0"] for x in p]
            g = collections.defaultdict(list)
            for x, v in zip(p, f):
                g[x["gun"]].append(v)
            gv = [stx.mean(v) for v in g.values()]
            m = stx.mean(gv)
            se = stx.stdev(gv) / math.sqrt(len(gv)) if len(gv) > 2 else 0
            print("%-10s %-12s %+11.4f %+9.2f %9d"
                  % (ad, "B+%.0f%%" % X, stx.mean(f), (m / se if se else 0), len(gv)))
        print()
    print("🟡 Betimleyici. Hukum icin ayri on-kayit gerekir.")
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
