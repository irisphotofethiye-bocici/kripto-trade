#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KAR KILIDI SINAMASI — notrlong.py (2026-09-07)

Kullanicinin kurali: "100 usd poz, 20 usd kazaninca pozun %20'sini alsin,
%5 alta stop koysun."  ->  tetik +%20 ROI · alim %20 · stop +%15 ROI

🔴 DISKE YAZAN HER YOL STUB'LANIR (CLAUDE.md: 2026-08-15'te sahte fiyat
gercek stop esigine carpip deftere 7 SAHTE LIKIDASYON yazdirmisti).
Sonda "diske yazim: YOK" diye DOGRULANIR.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, sys, copy

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
import testbot          # noqa: E402
import notrlong         # noqa: E402

YAZIM = []              # STUB'a dusen cagrilar (yol ile birlikte)
HEDEF = []              # _append_jsonl'e verilen YOLLAR
# Gercek kanit: bot dosyalarinin boyutu DEGISMEMELI
IZLENEN = ["notrlong_islemler.jsonl", "notrlong_state.json", "notrlong_equity.jsonl",
           "testbot_islemler.jsonl", "testbot_state.json"]
GECTI = []
DUSTU = []


def sinama(ad, kosul, detay=""):
    (GECTI if kosul else DUSTU).append(ad)
    print("   %-58s %s %s" % (ad, "GECTI" if kosul else "🔴 DUSTU", detay))


# ---------------------------------------------------------------- STUB'LAR
def _stub(ad):
    def f(*a, **kw):
        YAZIM.append(ad)
        if ad == "_append_jsonl" and a:
            HEDEF.append(a[0])
        return None
    return f


def _boyutlar():
    d = {}
    for f in IZLENEN:
        y = os.path.join(KOK, f)
        d[f] = os.path.getsize(y) if os.path.exists(y) else -1
    return d


testbot._append_jsonl = _stub("_append_jsonl")
testbot._save_state = _stub("_save_state")
testbot.pozisyon_kapat = _stub("pozisyon_kapat")
testbot.pozisyon_liq = _stub("pozisyon_liq")
testbot.telegram_gonder = _stub("telegram_gonder")
testbot.toast_gonder = _stub("toast_gonder")
testbot._funding_dilim = lambda pos: 0.0
notrlong.ISLEMLERF = "<STUB>"


def poz(giris=100.0, k=5, marjin=100.0, stop=95.0, yon="LONG"):
    return {"id": 1, "sym": "TEST", "yon": yon, "giris": giris, "stop": stop,
            "kaldirac": k, "marjin": marjin, "miktar": marjin * k / giris,
            "tp1": 0.0, "tp2": giris * 1.10, "tp1_alindi": True,
            "cikis_modu": "sabit_hedef", "giris_ts": testbot.now_iso(),
            "likidasyon": giris * 0.5, "kaynak": "notrlong"}


BOYUT0 = _boyutlar()
print("=" * 96)
print("KAR KILIDI SINAMASI — notrlong.py")
print("=" * 96)

# --- 1) SEVIYE ARITMETIGI: kullanicinin 100 $ ornegi
print("\n### 1) SEVIYELER — '100 usd poz, 20 usd kazaninca, %5 alta stop'")
for k in (3, 5, 6, 7):
    t, s = notrlong.kilit_seviyeleri(100.0, k, "LONG")
    kar_t = (t / 100.0 - 1) * 100 * k          # tetikte ROI
    kar_s = (s / 100.0 - 1) * 100 * k          # stopta ROI
    print("   %dx  tetik %.4f (kar %+5.1f $)   stop %.4f (kar %+5.1f $)"
          % (k, t, kar_t, s, kar_s))
    sinama("%dx tetik = kar 20 $" % k, abs(kar_t - 20.0) < 1e-9)
    sinama("%dx stop  = kar 15 $ (KAR, zarar DEGIL)" % k, abs(kar_s - 15.0) < 1e-9 and kar_s > 0)

# --- 2) kilit_kur
print("\n### 2) kilit_kur — tp1 tetige cevrilir, kismi yol ACILIR")
p = poz()
sinama("baslangicta tp1_alindi True (kismi KAPALI)", p["tp1_alindi"] is True)
notrlong.kilit_kur(p)
sinama("tp1 = tetik fiyati (104.0)", abs(p["tp1"] - 104.0) < 1e-6, "tp1=%.4f" % p["tp1"])
sinama("tp1_alindi False -> kismi yol ACIK", p["tp1_alindi"] is False)
sinama("tp2 DEGISMEDI (%10 hedef)", abs(p["tp2"] - 110.0) < 1e-6)
onceki = dict(p)
notrlong.kilit_kur(p)
sinama("IDEMPOTENT: ikinci cagri degistirmez", p["tp1"] == onceki["tp1"])

# --- 3) _kilit_tp1 muhasebesi
print("\n### 3) _kilit_tp1 — %20 kapanir, marjin OLCEKLENIR, stop +15 $'a")
st = {"equity": 10000.0, "acik_pozisyonlar": []}
p = poz()
notrlong.kilit_kur(p)
m0, mik0 = p["marjin"], p["miktar"]
notrlong._kilit_tp1(st, p, p["tp1"])
sinama("miktar %20 azaldi", abs(p["miktar"] - mik0 * 0.8) < 1e-9,
       "%.4f -> %.4f" % (mik0, p["miktar"]))
sinama("🔴 marjin AYNI ORANDA azaldi (liq cift-sayim korumasi)",
       abs(p["marjin"] - m0 * 0.8) < 0.01, "%.2f -> %.2f" % (m0, p["marjin"]))
sinama("stop = +15 $ karda (103.0)", abs(p["stop"] - 103.0) < 1e-6, "stop=%.4f" % p["stop"])
sinama("stop GIRISIN USTUNDE (kar kilitli)", p["stop"] > p["giris"])
kazanc = st["equity"] - 10000.0
sinama("equity ~ +4 $ arttI (20 $ karin %20'si)", 3.5 < kazanc < 4.2, "%+.3f $" % kazanc)
sinama("tp1_alindi True (bir daha tetiklenmez)", p["tp1_alindi"] is True)
sinama("kilit_alindi True", p.get("kilit_alindi") is True)

# --- 4) STOP GERI CEKILMEZ
print("\n### 4) stop yalniz LEHE oynar")
p2 = poz(stop=105.0)          # stop zaten tetigin de ustunde (yapay)
notrlong.kilit_kur(p2)
notrlong._kilit_tp1({"equity": 0.0}, p2, 104.0)
sinama("mevcut stop daha iyiyse GERI CEKILMEZ", abs(p2["stop"] - 105.0) < 1e-6,
       "stop=%.4f" % p2["stop"])

# --- 5) SIRA: ayni barda stop varsa STOP once (ileri-bakis yok)
print("\n### 5) testbot bar dongusu sirasi — stop ONCE")
kaynak = open(os.path.join(KOK, "testbot.py"), encoding="utf-8").read()
i_stop = kaynak.find('if b["l"] <= pos["stop"]:')
i_tp1 = kaynak.find('if not pos["tp1_alindi"] and b["h"] >= pos["tp1"]:')
sinama("LONG dalinda stop kontrolu tp1'den ONCE", 0 < i_stop < i_tp1,
       "stop@%d tp1@%d" % (i_stop, i_tp1))

# --- 6) KAPSAM SIZINTISI: takas geri aliniyor mu?
print("\n### 6) KAPSAM — diger defterler etkilenmemeli")
orij = testbot.pozisyon_kismi_tp1
notrlong._defterde(lambda: None)
sinama("_defterde SONRASI pozisyon_kismi_tp1 GERI ALINDI",
       testbot.pozisyon_kismi_tp1 is orij)
ic = {}


def _yakala():
    ic["fn"] = testbot.pozisyon_kismi_tp1
    ic["defter"] = testbot._DEFTER


notrlong._defterde(_yakala)
sinama("_defterde ICINDE bizim surumumuz aktif", ic["fn"] is notrlong._kilit_tp1)
sinama("_defterde ICINDE defter notrlong'unki", ic["defter"] == notrlong.ISLEMLERF)

# --- 7) KAPALI HALDE hicbir sey yapmaz
print("\n### 7) GERI ALMA — kilit_tetik_roi = 0")
_eski_esik = notrlong._kilit_esik
notrlong._kilit_esik = lambda ad, v: 0.0 if ad == "kilit_tetik_roi" else _eski_esik(ad, v)
t, s = notrlong.kilit_seviyeleri(100.0, 5, "LONG")
sinama("tetik_roi=0 -> seviye URETILMEZ", t is None and s is None)
p3 = poz()
sinama("tetik_roi=0 -> kilit_kur False doner", notrlong.kilit_kur(p3) is False)
sinama("tetik_roi=0 -> tp1_alindi True KALIR (kismi kapali)", p3["tp1_alindi"] is True)
notrlong._kilit_esik = _eski_esik

# --- 8) GERI DOLDURMA
print("\n### 8) kilit_geri_doldur — acik pozlara seviye ekler")
st2 = {"acik_pozisyonlar": [poz(), poz(giris=200.0, k=3, marjin=300.0, stop=190.0)]}
n = notrlong.kilit_geri_doldur(st2)
sinama("iki pozisyona da eklendi", n == 2, "n=%d" % n)
sinama("3x pozun tetigi 200 x (1+0.20/3)",
       abs(st2["acik_pozisyonlar"][1]["tp1"] - 200.0 * (1 + 0.20 / 3)) < 1e-4)
sinama("IDEMPOTENT: ikinci cagri 0 doner", notrlong.kilit_geri_doldur(st2) == 0)

# --- 9) DISKE YAZIM: gercek kanit dosya boyutu
print("\n### 9) DISKE YAZIM DOGRULAMASI")
sinama("_append_jsonl YALNIZ stub yoluna gitti (gercek defter yolu YOK)",
       bool(HEDEF) and all(h == "<STUB>" for h in HEDEF), "hedefler=%s" % sorted(set(HEDEF)))
BOYUT1 = _boyutlar()
degisen = [f for f in IZLENEN if BOYUT0[f] != BOYUT1[f]]
sinama("izlenen bot dosyalarinin BOYUTU degismedi", not degisen,
       "degisen=%s" % (degisen or "-"))

# --- SONUC
print("\n" + "=" * 96)
print("   GECTI %d · DUSTU %d" % (len(GECTI), len(DUSTU)))
if DUSTU:
    for d in DUSTU:
        print("      DUSTU: %s" % d)
print("   stub'a dusen cagrilar: %s   (hicbiri diske GITMEDI)" % sorted(set(YAZIM)))
print("   diske yazim: %s" % ("YOK" if not degisen else "VAR -> %s" % degisen))
print("=" * 96)
sys.exit(1 if (DUSTU or degisen) else 0)
