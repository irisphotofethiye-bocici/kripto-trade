#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BASABAS STOPU KAZANANLARI OLDURUR MU? — TESHIS (2026-09-06)

Kullanici: 'bot belli bir kara gelince stopu basabasin biraz ustune koysak'

Kayitli olcum KISMI KAR SONRASI basabasi olcmustu (+0,274 -> +0,261).
Senin versiyonun KISMI KAR OLMADAN, sadece kar esiginde cekme. Farkli.

BU BETIK MEKANIK BIR OLGU OLCER, performans DEGIL:
   +%10 hedefe ULASAN islemlerin kaci, once +X%%'e cikip SONRA girise
   (basabas) geri dondu? Donenler basabas stopuyla OLDURULURDU.

🟡 BETIMLEYICI — on-kayit yok, hukum yok. SALT-OKUNUR.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, sys, collections, statistics as stx
import importlib.util as il

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
sp = il.spec_from_file_location(
    "ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)

TETIK = [1.0, 2.0, 3.0, 5.0]      # kar esigi %
PAY = 0.20                        # basabasin "biraz ustu" (%) — ucret payi


def main():
    mum = ar.mumlar()
    print("YOL ANALIZI — +%10 hedefe ulasan islemler once basabasa dondu mu?")
    print()
    kaz, kayb = [], []
    n = 0
    for x in ar.veri_kur(mum):
        n += 1
    # veri_kur R/hit veriyor ama YOLU vermiyor -> yeniden simule etmek gerek.
    # Bunun yerine: giris kayitlarini alip mumlarda yolu taraayalim.
    rows = []
    son = {}
    import json, io, math, datetime as dt
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
        if not s or not p or s not in mum:
            continue
        if (r.get("score") or 0) < ar.SKOR_MIN:
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
        sf = (p - stop) / p * 100.0
        if sf < ar.ASGARI_STOP:
            continue
        son[s] = t
        rows.append((d, ix, i0, p, stop, r["ts"][:10]))
    print("giris: %d" % len(rows))
    print()

    hedef_ulasan = 0
    olduren = collections.Counter()
    kurtaran = collections.Counter()
    for d, ix, i0, g, stop, gun in rows:
        h = g * 1.10
        # yolu tara
        yol = []
        sonuc = None
        for j in range(i0 + 1, min(i0 + 1 + ar.ZAMAN_STOP, len(d))):
            b = d[j]
            yol.append((b["h"], b["l"]))
            if b["l"] <= stop:
                sonuc = "STOP"
                break
            if b["h"] >= h:
                sonuc = "HEDEF"
                break
        if sonuc is None:
            sonuc = "ZAMAN"
        # her tetik icin: once +X%%'e cikip sonra girise dondu mu?
        for X in TETIK:
            tet = g * (1 + X / 100.0)
            bab = g * (1 + PAY / 100.0)
            tetiklendi = False
            oldu = False
            for hi, lo in yol:
                if not tetiklendi and hi >= tet:
                    tetiklendi = True
                    continue
                if tetiklendi and lo <= bab:
                    oldu = True
                    break
            if oldu:
                if sonuc == "HEDEF":
                    olduren[X] += 1
                else:
                    kurtaran[X] += 1
        if sonuc == "HEDEF":
            hedef_ulasan += 1

    print("hedefe (+%%10) ulasan islem: %d / %d  (%%%.1f)"
          % (hedef_ulasan, len(rows), 100.0 * hedef_ulasan / len(rows)))
    print()
    print("%-10s %28s %28s %14s" % ("tetik", "KAZANANI OLDURUR", "KAYBEDENI KURTARIR", "net etki"))
    for X in TETIK:
        o, k = olduren[X], kurtaran[X]
        # kaba net: oldurulen kazanan = -(10/stop_ort) R kayip, kurtarilan = +1R civari
        print("   +%-6.1f%% %10d islem (%%%.1f kazananin) %10d islem %18s"
              % (X, o, 100.0 * o / max(1, hedef_ulasan), k,
                 ("%d kazanan < %d kurtarilan" % (o, k)) if o < k
                 else ("%d kazanan > %d kurtarilan" % (o, k))))
    print()
    print("🔑 'oldurur' = hedefe ULASAN ama once +X%%'e cikip basabasa donen islem.")
    print("   Basabas stopu bunlari hedefe VARMADAN kapatirdi.")
    print("🟡 Betimleyici. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
