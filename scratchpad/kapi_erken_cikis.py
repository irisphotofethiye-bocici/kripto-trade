#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C KOLU — ERKEN CIKIS. On-kayit: ON_KAYIT_kapi_dengesi.md (bd327a6).

Soru: ilk 30 dakikadaki hangi kosul "bu pozisyon kesilmeli" diyor?
⚠️ Bu bir CIKIS SIKILASTIRMASIDIR; bu projede sikilastiran 28 varyantin 28'i de
   kalmistir. Prior kotu — on-kayitta yazili.

Karsi-olgu: kosulu saglayanlar 30. dakikada KESILSEYDI ne olurdu?
   kesilen getiri ~ o andaki pnl - cikis maliyeti     vs   gercek sonuc
Birim dogrulamasi kod icinde YAPILIR (pnl_pct hangi tabana gore).
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, collections, statistics, math

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = json.load(open(os.path.join(PROJE, "scratchpad", "poz_yol", "kapi_veri.json"),
                   encoding="utf-8"))
CFG = json.load(open(os.path.join(PROJE, "kripto-config.json"), encoding="utf-8"))
MAL = CFG.get("maliyet", {})
CIKIS_MAL = float(MAL.get("taker_fee_pct", 0.045)) + float(MAL.get("slippage_pct", 0.02))
KESIF = ("2026-08-04", "2026-08-16")
DOGRU = ("2026-08-17", "2026-08-30")

W = [r for r in V if r.get("e30_pnl") is not None and r.get("_kontrol_tutma_saat") is not None]
print("C KOLU — ERKEN CIKIS   (yalniz testbot, 5 dk izleme)")
print("on-kayit ON_KAYIT_kapi_dengesi.md (bd327a6) · olcut SABIT")
print("=" * 118)
print("pozisyon %d  ·  cikis maliyeti varsayimi %%%.3f" % (len(W), CIKIS_MAL))

# ---------------------------------------------------------------- birim dogrulamasi
print("\n0) BIRIM DOGRULAMASI — izlemenin pnl_pct'i defterin ret'iyle ayni tabanda mi?")
print("-" * 118)
kisa = [r for r in W if r["_kontrol_tutma_saat"] <= 0.7]
if len(kisa) >= 10:
    a = [r["e30_pnl"] for r in kisa]
    b = [r["ret"] for r in kisa]
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((x - mb) ** 2 for x in b))
    kor = sum((a[i] - ma) * (b[i] - mb) for i in range(len(a))) / (sa * sb) if sa * sb else 0
    egim = (sum((a[i] - ma) * (b[i] - mb) for i in range(len(a))) / (sa * sa)) if sa else 0
    print("   <=42 dk'da kapanan %d pozisyon: korelasyon %+.3f  ·  egim %.3f" % (len(kisa), kor, egim))
    print("   ort: izleme pnl %+.3f%%  ·  defter ret %+.3f%%" % (ma, mb))
    print("   -> %s" % ("AYNI taban (egim ~1)" if 0.7 <= egim <= 1.4
                        else "TABAN FARKLI (egim %.2f) — karsi-olgu bu katsayiyla olceklenir" % egim))
    OLCEK = 1.0 if 0.7 <= egim <= 1.4 else (egim if egim else 1.0)
else:
    OLCEK = 1.0
    print("   yeterli kisa pozisyon yok — olcek 1,0 varsayildi (SINIR)")


def gun_t(w, alan_fn, nmin=3):
    g = collections.defaultdict(list)
    for r in w:
        g[r["gun"]].append(alan_fn(r))
    d = [sum(v) / len(v) for k, v in sorted(g.items()) if len(v) >= nmin]
    if len(d) < 2:
        return None, None, len(d)
    m, sd = sum(d) / len(d), statistics.stdev(d)
    return m, (m / (sd / math.sqrt(len(d))) if sd else None), len(d)


def kesme_etkisi(w, sec, ad):
    """sec(r) saglayanlar 30. dk'da KESILIR. Kazanc = kesik - gercek."""
    ks = [r for r in w if sec(r)]
    if len(ks) < 12:
        return None
    def kazanc(r):
        kesik = r["e30_pnl"] * OLCEK - CIKIS_MAL
        return kesik - r["ret"]
    m, t, nk = gun_t(ks, kazanc)
    return dict(ad=ad, n=len(ks), oran=100.0 * len(ks) / len(w),
                gercek=sum(r["ret"] for r in ks) / len(ks),
                kesik=sum(r["e30_pnl"] * OLCEK - CIKIS_MAL for r in ks) / len(ks),
                kazanc=sum(kazanc(r) for r in ks) / len(ks),
                dolar=sum((r["e30_pnl"] * OLCEK - CIKIS_MAL - r["ret"]) / 100.0 * r["notional"]
                          for r in ks),
                t=t, nk=nk,
                tp1=100.0 * sum(1 for r in ks if r["_kontrol_tp1"]) / len(ks))


KOSULLAR = [
    ("30dk pnl < 0", lambda r: r["e30_pnl"] < 0),
    ("30dk pnl < -0,5%", lambda r: r["e30_pnl"] < -0.5),
    ("30dk MAE < -1%", lambda r: r.get("e30_mae") is not None and r["e30_mae"] < -1),
    ("30dk MAE < -2%", lambda r: r.get("e30_mae") is not None and r["e30_mae"] < -2),
    ("30dk artida sure < %50", lambda r: r.get("e30_arti_oran") is not None and r["e30_arti_oran"] < 50),
    ("30dk artida sure < %25", lambda r: r.get("e30_arti_oran") is not None and r["e30_arti_oran"] < 25),
    ("ATR genisledi > 1,1x", lambda r: r.get("e30_atr_genis") is not None and r["e30_atr_genis"] > 1.1),
    ("ATR daraldi < 0,95x", lambda r: r.get("e30_atr_genis") is not None and r["e30_atr_genis"] < 0.95),
]

for pad, pen in (("KESIF", KESIF), ("DOGRULAMA", DOGRU)):
    P = [r for r in W if pen[0] <= r["gun"] <= pen[1]]
    print("\n%s %s..%s   N=%d  ·  gun %d" % (pad, pen[0], pen[1], len(P), len({r["gun"] for r in P})))
    print("-" * 118)
    if len(P) < 25:
        print("   N yetersiz — bu pencerede hukum verilmez")
        continue
    print("  %-24s %5s %7s %10s %10s %10s %11s %8s %8s" %
          ("kosul", "N", "pay", "gercek", "kesik", "kazanc", "dolar", "gun-t", "TP1%"))
    for ad, fn in KOSULLAR:
        e = kesme_etkisi(P, fn, ad)
        if not e:
            print("  %-24s  (N<12, atlandi)" % ad)
            continue
        print("  %-24s %5d %6.0f%% %+9.3f%% %+9.3f%% %+9.3f %+10.1f %8s %7.0f%%"
              % (e["ad"], e["n"], e["oran"], e["gercek"], e["kesik"], e["kazanc"],
                 e["dolar"], ("%+.2f" % e["t"]) if e["t"] else "-", e["tp1"]))

print("\n" + "=" * 118)
print("🔑 Z1 — TP1 KONTROL KATMANI (bugunku artefaktin oldugu yer)")
print("=" * 118)
print("Erken cikis kosullari TP1 ile guclu iliskiliyse, bulunan sey 'kesmek iyi' degil")
print("'zaten kaybedenleri kesmek iyi' olur — ve o dongusel.")
print("  %-24s %10s %10s %12s" % ("kosul", "TP1 alan%", "TP1 almayan%", "fark"))
for ad, fn in KOSULLAR:
    ks = [r for r in W if fn(r)]
    dg = [r for r in W if not fn(r)]
    if len(ks) < 12 or len(dg) < 12:
        continue
    a = 100.0 * sum(1 for r in ks if r["_kontrol_tp1"]) / len(ks)
    b = 100.0 * sum(1 for r in dg if r["_kontrol_tp1"]) / len(dg)
    print("  %-24s %9.0f%% %11.0f%% %+11.1f puan %s"
          % (ad, a, b, a - b, "  <== TP1 ile GUCLU iliskili" if abs(a - b) > 25 else ""))

print("\nbot dosyalarina yazim: YOK")
