#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PAHALI kolunun MUTLAK karliligi — SONUCA BAKTIKTAN SONRA sorulan soru.
🔴 BU BIR BULGU DEGILDIR. On-kayitli degildir. pahali_ayna.py'nin tablosunda
   goze carpan bir hucrenin sayisini uretir; kural adayi olmasi icin KENDI
   on-kaydi + holdout + coklu-karsilastirma denetimi gerekir.
Salt-okunur."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import sys, os, math, statistics as stx, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pahali_ayna as pa

kl, fn = pa.yukle()
kume, _ = pa.tara(kl, fn)

print("=" * 74)
print("POST-HOC — mutlak karlilik (BULGU DEGIL, on-kayitsiz)")
print("=" * 74)
print("%-8s %-6s %7s %6s %10s %8s %9s %s" %
      ("kol", "rejim", "N", "gun", "net%", "t_gun", "MDE", "gorulur mu"))
for ad in ("UCUZ", "PAHALI"):
    for rj in ("NOTR", "AYI", "BOGA"):
        ky = [k for k in kume[ad] if k["rejim"] == rj]
        if len(ky) < 40:
            continue
        g = pa.gun_ort(ky, lambda k: k["kol"]["A"]["net"])
        v = list(g.values())
        m = sum(v) / len(v)
        se = stx.stdev(v) / math.sqrt(len(v))
        t = m / se if se else 0
        mde = 2 * se
        print("%-8s %-6s %7d %6d %+10.4f %+8.2f %9.4f  %s" %
              (ad, rj, len(ky), len(v), m, t, mde,
               "GORULUR" if abs(m) >= mde else "goremiyoruz"))
print()
print("🔴 Coklu karsilastirma: bugun bu pencerede ONLARCA hucreye bakildi.")
print("   Buradan kural CIKMAZ. Kendi on-kaydi + holdout sart.")
print("Bot dosyalarina yazim: YOK")
