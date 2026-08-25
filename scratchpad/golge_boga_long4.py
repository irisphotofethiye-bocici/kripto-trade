#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZORUNLU SINAMALAR — 3. betigin bulgulari hukum tasiyabilir mi?

CLAUDE.md, 2026-08-20 ihlalinden sonra su sinamayi ZORUNLU kildi:
   "karsilastirdigin hucrelerde STOP GENISLIGI ve STOP-OLMA ORANI esit mi?
    ayrisiyorsa HAM GETIRI ZORUNLU; ayrismiyorsa mekanikli olcum yeter."

Ayrica H-C (1-cycle gecikme) GUN ile karisik mi diye bakilir: botun
'onay bekletmesiz' 10 girisi hep boga bacaginin EN IYI gunlerindeyse,
bulunan fark gecikmenin degil TARIHIN eseridir.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, re, datetime, collections, statistics as sx

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
        gir, cik, r = ilk.get("giris"), son.get("cikis"), son.get("r")
        tp1 = any(t.get("kismi") for t in v)
        # BASLANGIC stop genisligi: yalniz TP1 ALMAMIS saf STOP'ta turetilebilir
        # (hareket% / |r|). Iz-suren stop TP1'den sonra devreye girdigi icin
        # digerlerinde bu turetme GECERSIZ.
        sg = None
        if son["sebep"] == "STOP" and not tp1 and r and gir:
            sg = abs(100.0 * (cik - gir) / gir / r)
        m = VOLX.search(son.get("sebep_giris") or "")
        out.append(dict(sym=son["sym"], yon=son["yon"], gt=gt, gun=gt.strftime("%m-%d"),
                        net=net, notional=no, pct=(100.0 * net / no) if no else None,
                        kaynak=son.get("kaynak") or "testbot", sebep=son["sebep"],
                        kapi=son.get("sebep_giris") or "", skor=ilk.get("skor_giriste"),
                        chg24=ilk.get("chg24_giriste"), vol_x=float(m.group(1)) if m else None,
                        tp1=tp1, stop_gen=sg))
    return out


G = [z for z in poz("golge_islemler.jsonl") if z["gt"] >= BOGA and z["yon"] == "LONG"]
T = [z for z in poz("testbot_islemler.jsonl") if z["gt"] >= BOGA and z["yon"] == "LONG"]
GP = [z for z in G if "pump_long" in z["kaynak"]]


def mek(ad, w):
    if not w:
        print("   %-26s N=0" % ad)
        return
    sg = [z["stop_gen"] for z in w if z["stop_gen"] is not None]
    print("   %-26s N=%3d | stop genisligi med %6.2f%% (N=%2d) | stop-olma %%%2.0f | TP1 %%%2.0f | net/notional ort %+6.3f%%"
          % (ad, len(w), sx.median(sg) if sg else float("nan"), len(sg),
             100.0 * sum(1 for z in w if z["sebep"] == "STOP") / len(w),
             100.0 * sum(1 for z in w if z["tp1"]) / len(w),
             sum(z["pct"] for z in w if z["pct"] is not None) / len(w)))


print("ZORUNLU SINAMA 1 — HUCRELER OYNAKLIKTA AYRISIYOR MU?")
print("=" * 122)
print("\nH-A hucreleri (skor kapisi):")
mek("golge pump skor < 45", [z for z in GP if z["skor"] is not None and z["skor"] < 45])
mek("golge pump skor >= 45", [z for z in GP if z["skor"] is not None and z["skor"] >= 45])
mek("testbot LONG (skor>=45)", T)

print("\nH-B hucreleri (vol_x):")
for lo, hi in ((2.0, 3.0), (3.0, 5.0), (5.0, 10.0), (10.0, 1e9)):
    mek("vol_x %.0f-%s" % (lo, "%.0f" % hi if hi < 1e8 else "inf"),
        [z for z in GP if z["vol_x"] is not None and lo <= z["vol_x"] < hi])

print("\nH-B2 hucreleri (chg24):")
for lo, hi in ((10, 20), (20, 40), (40, 1e9)):
    mek("chg24 %d-%s%%" % (lo, "%d" % hi if hi < 1e8 else "inf"),
        [z for z in GP if z["chg24"] is not None and lo <= z["chg24"] < hi])

print("\n" + "=" * 122)
print("ZORUNLU SINAMA 2 — H-C (1-cycle gecikme) GUN ile karisik mi?")
print("=" * 122)
bekle = [z for z in T if "onay bekletme" in z["kapi"]]
hizli = [z for z in T if "onay bekletme" not in z["kapi"]]
gb = collections.Counter(z["gun"] for z in bekle)
gh = collections.Counter(z["gun"] for z in hizli)
print("   %-8s %10s %10s | %12s %12s" % ("gun", "bekleyen N", "hizli N", "bekleyen ort", "hizli ort"))
for g_ in sorted(set(gb) | set(gh)):
    a = [z["pct"] for z in bekle if z["gun"] == g_ and z["pct"] is not None]
    b = [z["pct"] for z in hizli if z["gun"] == g_ and z["pct"] is not None]
    print("   %-8s %10d %10d | %11s %12s"
          % (g_, gb.get(g_, 0), gh.get(g_, 0),
             "%+.3f%%" % (sum(a) / len(a)) if a else "-",
             "%+.3f%%" % (sum(b) / len(b)) if b else "-"))
print("   -> hizli girislerin gun dagilimi: %s" % dict(gh))
print("   NOT: 'hizli' = NOTR-belirsiz kapisi, 'bekleyen' = BOGA kapisi. Kapi ile gun")
print("        BIRLIKTE degisiyorsa gecikme etkisi AYRISTIRILAMAZ.")

print("\n" + "=" * 122)
print("ZORUNLU SINAMA 3 — GOLGE pump: skor<45 kolu GUN GUN tutarli mi?")
print("=" * 122)
lo = [z for z in GP if z["skor"] is not None and z["skor"] < 45]
hi = [z for z in GP if z["skor"] is not None and z["skor"] >= 45]
print("   %-8s %8s %11s | %8s %11s | %10s" % ("gun", "lo N", "lo ort", "hi N", "hi ort", "fark"))
ay = []
for g_ in sorted(set(z["gun"] for z in GP)):
    a = [z["pct"] for z in lo if z["gun"] == g_ and z["pct"] is not None]
    b = [z["pct"] for z in hi if z["gun"] == g_ and z["pct"] is not None]
    if a and b:
        d = sum(a) / len(a) - sum(b) / len(b)
        ay.append(d)
        print("   %-8s %8d %+10.3f%% | %8d %+10.3f%% | %+9.3f" %
              (g_, len(a), sum(a) / len(a), len(b), sum(b) / len(b), d))
    else:
        print("   %-8s %8d %11s | %8d %11s | %10s"
              % (g_, len(a), "%+.3f%%" % (sum(a) / len(a)) if a else "-",
                 len(b), "%+.3f%%" % (sum(b) / len(b)) if b else "-", "-"))
if ay:
    print("   -> %d/%d gunde skor<45 onde   ort fark %+.3f puan" %
          (sum(1 for x in ay if x > 0), len(ay), sum(ay) / len(ay)))

print("\n" + "=" * 122)
print("ZORUNLU SINAMA 4 — KUYRUK: en iyi 10 islem hangi hucrede?")
print("=" * 122)
s = sorted(GP, key=lambda z: -z["net"])[:10]
print("   %-9s %-12s %7s %7s %8s %10s %s" % ("sym", "gun", "skor", "vol_x", "chg24", "net $", "sebep"))
for z in s:
    print("   %-9s %-12s %7s %7s %8s %+10.2f %s"
          % (z["sym"], z["gt"].strftime("%m-%d %H:%M"),
             "%.1f" % z["skor"] if z["skor"] is not None else "-",
             "%.1f" % z["vol_x"] if z["vol_x"] else "-",
             "%+.1f" % z["chg24"] if z["chg24"] is not None else "-",
             z["net"], z["sebep"]))
print("   -> en iyi 10'un skor<45 olani: %d/10   gun dagilimi: %s"
      % (sum(1 for z in s if z["skor"] is not None and z["skor"] < 45),
         dict(collections.Counter(z["gun"] for z in s))))

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
