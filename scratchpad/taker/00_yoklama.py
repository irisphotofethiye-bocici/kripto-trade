#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""taker kapisi — YAPILABILIRLIK YOKLAMASI (sonuc DEGIL).

Sorulan: hedef hucrede kac gozlem var, taker alani ne kadar dolu, ileri
fiyat kaynagi kapsiyor mu. Getiri HESAPLANMAZ — on-kayit henuz yazilmadi.
SALT-OKUNUR.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, sys, collections

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)

ARSIV = os.path.join(KOK, "radar_archive.jsonl")
KLINES = os.path.join(KOK, "scratchpad", "klines_1h_uzun")

n = 0
alan = collections.Counter()
hucre = []
gunler = collections.Counter()
semboller = collections.Counter()
ilk = son = None

with open(ARSIV, encoding="utf-8", errors="ignore") as f:
    for l in f:
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        n += 1
        ts = r.get("ts") or ""
        if ilk is None or ts < ilk:
            ilk = ts
        if son is None or ts > son:
            son = ts
        for k in ("taker", "smart", "stage", "score", "price", "chg24", "last1"):
            if r.get(k) is not None:
                alan[k] += 1
        st = r.get("stage")
        if st not in ("BASLIYOR", "HAZIRLANIYOR"):
            continue
        sk = r.get("score") or 0
        if sk < (40.0 if st == "HAZIRLANIYOR" else 45.0):
            continue
        if r.get("smart") != "LONG":
            continue
        hucre.append(r)
        gunler[ts[:10]] += 1
        semboller[r.get("sym")] += 1

print("=" * 84)
print("TAKER KAPISI — YAPILABILIRLIK YOKLAMASI  (getiri hesaplanmadi)")
print("=" * 84)
print("arsiv       : %d kayit  ·  %s -> %s" % (n, ilk, son))
print()
print("ALAN DOLULUGU (tum arsiv):")
for k in ("stage", "score", "price", "chg24", "last1", "smart", "taker"):
    print("   %-8s %8d  (%%%.1f)" % (k, alan[k], 100.0 * alan[k] / n))
print()
print("HEDEF HUCRE = stage aktif + skor esigi + smart LONG")
print("   N            : %d" % len(hucre))
print("   tekil gun    : %d" % len(gunler))
print("   tekil sembol : %d" % len(semboller))

tk = [r for r in hucre if r.get("taker") is not None]
print("   taker DOLU   : %d  (%%%.1f)" % (len(tk), 100.0 * len(tk) / max(1, len(hucre))))
if tk:
    ust = sum(1 for r in tk if r["taker"] >= 1.0)
    print("   taker >= 1.0 : %d   ·   < 1.0 : %d" % (ust, len(tk) - ust))
    print("   en yogun 5 gun: %s" % ", ".join("%s(%d)" % g for g in gunler.most_common(5)))

print()
print("ILERI FIYAT KAYNAGI:")
if os.path.isdir(KLINES):
    dosya = os.listdir(KLINES)
    print("   klines_1h_uzun: %d dosya" % len(dosya))
    if dosya:
        print("   ornek: %s" % dosya[0])
    var = sum(1 for s in semboller
              if any(x.startswith(str(s)) for x in dosya))
    print("   hucredeki %d sembolun %d'i icin dosya VAR" % (len(semboller), var))
else:
    print("   klines_1h_uzun YOK")
print()
print("Salt-okuma. Arsiv context'e yuklenmedi. Bot dosyalarina yazim: YOK")
