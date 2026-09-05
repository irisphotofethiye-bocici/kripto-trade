#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MA50 kapisi BOGA'da ACILSAYDI ne olurdu — pratik kestirim (2026-09-05)
Yeni hipotez YOK; boga_taze.py'nin ayni taramasindan slot/kasa kestirimi cikarir.
Salt-okunur."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import sys, os, statistics as stx
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boga_taze as bt

RISK_PCT, SLOT = 1.5, 8

kl, fn = bt.yukle()
oi = bt.oi24_serisi()
kume = bt.tara(kl, fn, oi)
km = kume["MA50"]
gun = sorted({k["gun"] for k in km})
n_gun = len(gun)

r_islem = stx.mean([k["kol"]["A"]["R"] for k in km])
g = bt.gun_ort(km, lambda k: k["kol"]["A"]["R"])
r_gun, t_gun, mde, _ = bt.t_mde(g)
saat = stx.mean([k["kol"]["A"]["saat"] for k in km])
aday_gun = len(km) / n_gun
slot_gun = SLOT / saat * 24

print("=" * 70)
print("MA50 KAPISI BOGA'DA ACILSAYDI — pratik kestirim")
print("=" * 70)
print("aday olay          : %d  (%d gun -> gunde %.0f)" % (len(km), n_gun, aday_gun))
print("ortalama tutma     : %.1f saat" % saat)
print("slot kapasitesi    : %d slot / %.1f saat -> gunde EN COK ~%.0f islem"
      % (SLOT, saat, slot_gun))
print("darbogaz           : %s" % ("SLOT (aday cok fazla)" if aday_gun > slot_gun else "ADAY"))
print()
print("islem basi R  : islem-ort %+.4f  |  gun-ort %+.4f (t %+.2f, MDE %.4f)"
      % (r_islem, r_gun, t_gun or 0, mde or 0))
print("her islem kasanin %%%.1f'ini riske atar -> islem basi beklenti:" % RISK_PCT)
print("   islem-ort ile : %%%+.3f kasa" % (RISK_PCT * r_islem))
print("   gun-ort ile   : %%%+.3f kasa" % (RISK_PCT * r_gun))
print()
gercek = min(aday_gun, slot_gun)
top = gercek * n_gun
print("%.0f islem/gun x %d gun = ~%.0f islem" % (gercek, n_gun, top))
print("   islem-ort ile : kasa %%%+.1f" % (top * RISK_PCT * r_islem))
print("   gun-ort ile   : kasa %%%+.1f" % (top * RISK_PCT * r_gun))
print()
print("UYARI: portfoy asamasi YOK (es zamanli maruziyet, dusus freni, LONG ile")
print("slot rekabeti modellenmedi). Bu bir BUYUKLUK MERTEBESI kestirimidir.")
print("Bot dosyalarina yazim: YOK")
