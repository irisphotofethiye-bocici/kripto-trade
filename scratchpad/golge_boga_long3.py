#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GOLGE pump_long_tezi — farki UReten bileseni ayir.

Bulunan mekanizma (testbot.py:1500):
   tetik = chg24 >= %10  VE  vol_x >= 2.0
   skor kapisi YOK · onay bekleme YOK · smart/taker kapisi YOK · MAKS_ACIK=20 (bot 8)

Bot LONG'u ise: skor >= 45 + smart-LONG + taker + 1-CYCLE ONAY BEKLETME + maks 8 poz.

Aday aciklamalar (hepsi ayri olculur):
   H-A  SKOR KAPISI botun aleyhine  -> golge pump'larini skor<45 / >=45 diye bol
   H-B  VOL_X FILTRESI golge'nin lehine -> vol_x bandina gore ayir
   H-C  1-CYCLE GECIKME botun aleyhine  -> golge:onay_bekle (aninda) vs bot (bekleyip girdi)
   H-D  SADECE DAHA COK ATIS (20 slot vs 8) -> islem BASI beklenti esitse H-D gecerli

CLAUDE.md: bu betik HIPOTEZ URETIR, HUKUM YAZMAZ. On-kayit yok, 6 gun var.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, re, datetime, collections, statistics as sx, math

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = "%Y-%m-%d %H:%M:%S"
BOGA = datetime.datetime(2026, 8, 19, 0, 0, 0)
VOLX = re.compile(r"vol_x\s+([0-9.]+)x")


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


def poz(dosya):
    g = collections.defaultdict(list)
    for x in jl(dosya):
        g[x["id"]].append(x)
    out = []
    for i, v in g.items():
        v.sort(key=lambda z: z["ts"])
        ilk, son = v[0], v[-1]
        gt = (datetime.datetime.strptime(ilk["ts"], F)
              - datetime.timedelta(hours=(ilk.get("tutma_saat") or 0)))
        net = sum((t.get("sonuc_usdt") or 0) for t in v)
        no = ilk.get("notional") or 0
        m = VOLX.search(son.get("sebep_giris") or "")
        out.append(dict(id=i, sym=son["sym"], yon=son["yon"], gt=gt,
                        gun=gt.strftime("%m-%d"), net=net, notional=no,
                        pct=(100.0 * net / no) if no else None,
                        kaynak=son.get("kaynak") or "testbot", sebep=son["sebep"],
                        kapi=son.get("sebep_giris") or "",
                        skor=ilk.get("skor_giriste"), chg24=ilk.get("chg24_giriste"),
                        smart=ilk.get("smart_giriste"), pos=ilk.get("range_pos_giriste"),
                        vol_x=float(m.group(1)) if m else None,
                        tp1=any(t.get("kismi") for t in v)))
    return out


def satir(ad, w):
    if not w:
        print("   %-34s N=0" % ad)
        return
    p = [z["pct"] for z in w if z["pct"] is not None]
    kz = sum(1 for z in w if z["net"] > 0)
    tp1 = sum(1 for z in w if z["tp1"])
    print("   %-34s N=%3d  medyan %+6.3f%%  ort %+6.3f%%  toplam %+9.2f $  kazanan %%%2.0f  TP1 %%%2.0f"
          % (ad, len(w), sx.median(p), sum(p) / len(p), sum(z["net"] for z in w),
             100.0 * kz / len(w), 100.0 * tp1 / len(w)))


def gun_t(w):
    """gun-kumeli tek-orneklem t (kume=gun). 6 gun -> ZAYIF, aynen raporlanir."""
    g = collections.defaultdict(list)
    for z in w:
        if z["pct"] is not None:
            g[z["gun"]].append(z["pct"])
    o = [sum(v) / len(v) for v in g.values()]
    if len(o) < 2:
        return None
    sd = sx.stdev(o)
    return (sum(o) / len(o)) / (sd / math.sqrt(len(o))) if sd else None


G = [z for z in poz("golge_islemler.jsonl") if z["gt"] >= BOGA and z["yon"] == "LONG"]
T = [z for z in poz("testbot_islemler.jsonl") if z["gt"] >= BOGA and z["yon"] == "LONG"]
GP = [z for z in G if "pump_long" in z["kaynak"]]

print("BOGA BACAGI LONG — BILESEN AYRISTIRMASI")
print("golge N=%d (pump_long %d)  ·  testbot N=%d" % (len(G), len(GP), len(T)))
print("=" * 110)

print("\nH-A  SKOR KAPISI — botun sarti skor>=45. Golge pump'larini ayni esikte bol.")
print("-" * 110)
satir("golge pump  skor < 45", [z for z in GP if z["skor"] is not None and z["skor"] < 45])
satir("golge pump  skor >= 45", [z for z in GP if z["skor"] is not None and z["skor"] >= 45])
satir("  (referans) TESTBOT LONG", T)
b = [z for z in GP if z["skor"] is not None]
if b:
    lo = [z["pct"] for z in b if z["skor"] < 45 and z["pct"] is not None]
    hi = [z["pct"] for z in b if z["skor"] >= 45 and z["pct"] is not None]
    if lo and hi:
        print("   -> skor<45 ort %+.3f%%  vs  skor>=45 ort %+.3f%%   fark %+.3f puan"
              % (sum(lo) / len(lo), sum(hi) / len(hi), sum(lo) / len(lo) - sum(hi) / len(hi)))
        print("   -> gun-kumeli t (skor<45 kolu) %s"
              % ("%.2f" % gun_t([z for z in b if z["skor"] < 45])
                 if gun_t([z for z in b if z["skor"] < 45]) else "-"))

print("\nH-B  VOL_X — golge'nin BOTTA OLMAYAN filtresi (vol_x >= 2.0 zorunlu)")
print("-" * 110)
v = [z for z in GP if z["vol_x"] is not None]
print("   vol_x ayrilabilen: %d/%d   medyan %.2fx" % (len(v), len(GP),
                                                      sx.median([z["vol_x"] for z in v]) if v else 0))
for lo, hi in ((2.0, 3.0), (3.0, 5.0), (5.0, 10.0), (10.0, 1e9)):
    satir("vol_x %.0f-%s x" % (lo, "%.0f" % hi if hi < 1e8 else "inf"),
          [z for z in v if lo <= z["vol_x"] < hi])

print("\nH-B2 CHG24 BANDI — pump ne kadar buyukse?")
print("-" * 110)
for lo, hi in ((10, 20), (20, 40), (40, 1e9)):
    satir("chg24 %d-%s%%" % (lo, "%d" % hi if hi < 1e8 else "inf"),
          [z for z in GP if z["chg24"] is not None and lo <= z["chg24"] < hi])

print("\nH-C  1-CYCLE GECIKME — golge:onay_bekle (aninda girdi) vs bot (bekleyip girdi)")
print("-" * 110)
satir("golge:onay_bekle (aninda)", [z for z in G if "onay_bekle" in z["kaynak"]])
satir("testbot 'onay bekletme' ile", [z for z in T if "onay bekletme" in z["kapi"]])
satir("testbot onay bekletmesiz", [z for z in T if "onay bekletme" not in z["kapi"]])

print("\nH-D  ATIS SAYISI — islem BASI beklenti mi, atis sayisi mi?")
print("-" * 110)
gp = [z["pct"] for z in GP if z["pct"] is not None]
tp = [z["pct"] for z in T if z["pct"] is not None]
print("   golge pump  islem basi ort %+.3f%%   N=%d   toplam %+9.2f $"
      % (sum(gp) / len(gp), len(gp), sum(z["net"] for z in GP)))
print("   testbot     islem basi ort %+.3f%%   N=%d   toplam %+9.2f $"
      % (sum(tp) / len(tp), len(tp), sum(z["net"] for z in T)))
print("   -> bot golge kadar ATIS yapsaydi (kendi beklentisiyle, N=%d): %+9.2f $"
      % (len(GP), sum(tp) / len(tp) / 100.0 * sx.median([z["notional"] for z in T]) * len(GP)))
print("   -> golge bot kadar ATIS yapsaydi (kendi beklentisiyle, N=%d): %+9.2f $"
      % (len(T), sum(gp) / len(gp) / 100.0 * sx.median([z["notional"] for z in GP]) * len(T)))
print("   gun-kumeli t: golge pump %s   testbot %s   (kume=6 gun, ZAYIF)"
      % ("%+.2f" % gun_t(GP) if gun_t(GP) else "-", "%+.2f" % gun_t(T) if gun_t(T) else "-"))

print("\nH-E  KUYRUK — pump tezi kuyrukla mi yasiyor?")
print("-" * 110)
s = sorted(GP, key=lambda z: -z["net"])
top = sum(z["net"] for z in GP)
for k in (1, 5, 10, 20):
    print("   golge pump  en iyi %2d  %+9.2f   geri kalan (%3d islem) %+9.2f"
          % (k, sum(z["net"] for z in s[:k]), len(s) - k, top - sum(z["net"] for z in s[:k])))
print("   -> pozitif islem %d / negatif %d"
      % (sum(1 for z in GP if z["net"] > 0), sum(1 for z in GP if z["net"] <= 0)))

print("\nH-F  AYNI SEMBOLDE TEKRAR — golge ayni coine birden fazla giriyor mu")
print("-" * 110)
c = collections.Counter(z["sym"] for z in GP)
print("   tekil sembol %d / %d giris   en cok girilen: %s"
      % (len(c), len(GP), ", ".join("%s x%d" % (k, n) for k, n in c.most_common(6))))
cok = [s_ for s_, n in c.items() if n >= 3]
satir("3+ kez girilen sembollerde", [z for z in GP if z["sym"] in cok])
satir("1-2 kez girilen sembollerde", [z for z in GP if z["sym"] not in cok])

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
