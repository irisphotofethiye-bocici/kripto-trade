#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GOLGE LONG vs TESTBOT — BOGA BACAGINDA farki NE uretiyor?

SORU (kullanici, 2026-08-25): golge defterin LONG tarafi boga bacaginda bottan
daha basarili duruyor. Bu farki ne sagliyor?

CLAUDE.md disiplini:
  - P&L TOPLARKEN suzgec YOK -> id ile birlestir (TP1_KISMI kari kaybolmasin)
  - kazanma orani POZISYON basina
  - funding_usdt: dolar, dilim, id ile toplanir; None = BILINMIYOR
  - sonuc_usdt fonlamayi ICERMEZ
  - golge iki is birden yapiyor -> kaynak kirilimi ZORUNLU
  - dolar kiyasi BOYUT farkini gizler -> notional/marjin/kaldirac ayrica olculur
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, datetime, collections, statistics as sx

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = "%Y-%m-%d %H:%M:%S"
BOGA = datetime.datetime(2026, 8, 19, 0, 0, 0)   # BTC 64.694 -> 69.310 dikey bacak
SIMDI = datetime.datetime.now()


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


def pozisyonlar(dosya):
    """id ile birlestir -> pozisyon listesi.
    GIRIS ani defterde YOK; ilk kayit zaten kismi/kapanis kaydi.
    tutma_saat ile geriye hesaplanir."""
    g = collections.defaultdict(list)
    for x in jl(dosya):
        g[x["id"]].append(x)
    out = []
    for i, v in g.items():
        v.sort(key=lambda z: z["ts"])
        ilk, son = v[0], v[-1]
        t_ilk = datetime.datetime.strptime(ilk["ts"], F)
        giris_ts = t_ilk - datetime.timedelta(hours=(ilk.get("tutma_saat") or 0))
        net = sum((t.get("sonuc_usdt") or 0) for t in v)
        fon = [t.get("funding_usdt") for t in v if t.get("funding_usdt") is not None]
        out.append({
            "id": i, "sym": son["sym"], "yon": son["yon"],
            "giris_ts": giris_ts,
            "kapanis_ts": datetime.datetime.strptime(son["ts"], F),
            "net": net,
            "fon": sum(fon) if fon else None,
            "marjin": ilk.get("marjin") or 0,
            "notional": ilk.get("notional") or 0,
            "kaldirac": ilk.get("kaldirac") or 0,
            "kaynak": son.get("kaynak") or "testbot",
            "sebep": son.get("sebep"),
            "kapi": (son.get("sebep_giris") or "?"),
            "chg24": ilk.get("chg24_giriste"),
            "skor": ilk.get("skor_giriste"),
            "smart": ilk.get("smart_giriste"),
            "rejim": ilk.get("rejim_giriste"),
            "pos": ilk.get("range_pos_giriste"),
            "tut": max((t.get("tutma_saat") or 0) for t in v),
            "kismi_var": any(t.get("kismi") for t in v),
        })
    return out


def ozet(ad, w):
    if not w:
        print("   %-30s N=0" % ad)
        return
    kz = sum(1 for z in w if z["net"] > 0)
    top = sum(z["net"] for z in w)
    # boyuttan arindirilmis getiri: net / notional = fiyat hareketinin kendisi
    ham = [100.0 * z["net"] / z["notional"] for z in w if z["notional"]]
    fon = [z["fon"] for z in w if z["fon"] is not None]
    print("   %-30s N=%3d  toplam %+9.2f  kazanan %2d (%%%3.0f)  ort %+7.2f"
          % (ad, len(w), top, kz, 100.0 * kz / len(w), top / len(w)))
    print("   %-30s notional-basi  medyan %+6.3f%%  ort %+6.3f%%   medyan notional %7.0f $  kald %s"
          % ("", sx.median(ham) if ham else 0,
             (sum(ham) / len(ham)) if ham else 0,
             sx.median([z["notional"] for z in w]),
             "/".join(str(k) for k in sorted(set(z["kaldirac"] for z in w)))))
    if fon:
        print("   %-30s fonlama %+8.2f $  (%d/%d biliniyor)" % ("", sum(fon), len(fon), len(w)))


print("GOLGE LONG vs TESTBOT — BOGA BACAGI  (%s .. %s)"
      % (BOGA.strftime("%m-%d %H:%M"), SIMDI.strftime("%m-%d %H:%M")))
print("BTC: 08-18 64.694 -> 08-21 78.309 -> 08-25 78.741  (dikey bacak + plato)")
print("=" * 104)

G = pozisyonlar("golge_islemler.jsonl")
T = pozisyonlar("testbot_islemler.jsonl")

gb = [z for z in G if z["giris_ts"] >= BOGA]
tb = [z for z in T if z["giris_ts"] >= BOGA]

print("\n1) YON KIRILIMI — girisi boga bacaginda olan KAPANMIS pozisyonlar")
print("-" * 104)
for ad, w in (("GOLGE", gb), ("TESTBOT", tb)):
    print("  %s" % ad)
    for yon in ("LONG", "SHORT"):
        ozet(yon, [z for z in w if z["yon"] == yon])
    print()

print("2) GOLGE LONG — KAYNAK KIRILIMI (golge iki is birden yapiyor)")
print("-" * 104)
gl = [z for z in gb if z["yon"] == "LONG"]
for k in sorted(set(z["kaynak"] for z in gl)):
    ozet(k, [z for z in gl if z["kaynak"] == k])
print()

print("3) BOT LONG'a hangi kapidan girdi")
print("-" * 104)
tl = [z for z in tb if z["yon"] == "LONG"]
for k, n in collections.Counter(z["kapi"][:58] for z in tl).most_common():
    w = [z for z in tl if z["kapi"][:58] == k]
    print("   %-60s %2d  %+9.2f" % (k, n, sum(z["net"] for z in w)))
print()

print("4) SECIM FARKI — giris anindaki chg24  (bot pump >= %20'yi ENGELLIYOR)")
print("-" * 104)
for ad, w in (("GOLGE LONG (tum)", gl),
              ("GOLGE LONG pump_long_tezi", [z for z in gl if "pump_long" in z["kaynak"]]),
              ("TESTBOT LONG", tl)):
    c = [z["chg24"] for z in w if z["chg24"] is not None]
    if c:
        print("   %-28s N=%3d  chg24 medyan %+6.2f%%  min %+7.2f  maks %+7.2f   >=%%20: %d (%%%.0f)"
              % (ad, len(c), sx.median(c), min(c), max(c),
                 sum(1 for x in c if x >= 20),
                 100.0 * sum(1 for x in c if x >= 20) / len(c)))
print()

print("5) TUTMA SURESI ve CIKIS SEBEBI")
print("-" * 104)
for ad, w in (("GOLGE LONG", gl), ("TESTBOT LONG", tl)):
    if not w:
        continue
    print("   %-16s medyan tutma %5.1f sa   kismi kar alan %d/%d"
          % (ad, sx.median([z["tut"] for z in w]),
             sum(1 for z in w if z["kismi_var"]), len(w)))
    for s, n in collections.Counter(z["sebep"] for z in w).most_common():
        v = [z for z in w if z["sebep"] == s]
        print("        %-16s %2d  %+9.2f" % (s, n, sum(z["net"] for z in v)))
print()

print("6) BOT NE ZAMAN KOSTU — HALT penceresi kiyasi bozuyor mu")
print("-" * 104)
eq = jl("testbot_equity.jsonl")
gun = collections.defaultdict(int)
for x in eq:
    try:
        t = datetime.datetime.strptime(x["ts"], F)
    except Exception:
        continue
    if t >= BOGA:
        gun[t.strftime("%m-%d")] += 1
print("   testbot tur sayisi/gun (7,5 dk -> beklenen ~192):")
for g_ in sorted(gun):
    print("      %s : %3d tur" % (g_, gun[g_]))
gg = collections.defaultdict(int)
for z in gb:
    gg[z["giris_ts"].strftime("%m-%d")] += 1
tt = collections.defaultdict(int)
for z in tb:
    tt[z["giris_ts"].strftime("%m-%d")] += 1
print("   GIRIS sayisi/gun   golge / testbot:")
for g_ in sorted(set(gg) | set(tt)):
    print("      %s :  %2d / %2d" % (g_, gg.get(g_, 0), tt.get(g_, 0)))
print()

print("7) ACIK POZISYONLAR — realize kasa yaniltir (etkin kasa)")
print("-" * 104)
for ad, sf in (("golge", "golge_state.json"), ("testbot", "testbot_state.json")):
    p = os.path.join(PROJE, sf)
    if not os.path.exists(p):
        continue
    st = json.load(open(p, encoding="utf-8"))
    acik = st.get("acik_pozisyonlar") or []
    yon = collections.Counter(a.get("yon") for a in acik)
    print("   %-8s equity %9.2f  efektif %9.2f  acik %d (%dL/%dS)  durum %s"
          % (ad, st.get("equity") or 0, st.get("efektif_equity") or 0,
             len(acik), yon.get("LONG", 0), yon.get("SHORT", 0), st.get("durum")))

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
