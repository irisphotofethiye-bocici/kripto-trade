#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GOLGE LONG vs TESTBOT LONG — FARKIN AYRISTIRILMASI (boga bacagi).

1. tablo sunu gosterdi: golge LONG +2080 / testbot LONG -934, ama
   golge'nin 205 stopu toplam -411 (stop basi -2,00 $) iken
   testbot'un 59 stopu -1515 (stop basi -25,7 $).  12,8 KAT fark.
   -> ama o rakam KIRLI: 'sebep' son kaydinki, TP1 kari icinde.

Bu betik farki uc bilesene ayirir:
   (a) SECIM/ZAMANLAMA  -> saf fiyat hareketi (net/notional)
   (b) MEKANIK          -> stop genisligi + stop-olma orani  [CLAUDE.md ZORUNLU SINAMA]
   (c) BOYUT            -> marjin / notional / kaldirac
ve kuyruk yogunlasmasini olcer (kac pozisyon sonucu tasiyor).
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, datetime, collections, statistics as sx, math

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = "%Y-%m-%d %H:%M:%S"
BOGA = datetime.datetime(2026, 8, 19, 0, 0, 0)


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
    g = collections.defaultdict(list)
    for x in jl(dosya):
        g[x["id"]].append(x)
    out = []
    for i, v in g.items():
        v.sort(key=lambda z: z["ts"])
        ilk, son = v[0], v[-1]
        giris_ts = (datetime.datetime.strptime(ilk["ts"], F)
                    - datetime.timedelta(hours=(ilk.get("tutma_saat") or 0)))
        net = sum((t.get("sonuc_usdt") or 0) for t in v)
        gir = ilk.get("giris") or 0
        # SAF fiyat hareketi: son kaydin cikisi (mekanikten bagimsiz DEGIL ama
        # stop genisligini bu verir)
        son_cik = son.get("cikis") or 0
        hareket = 100.0 * (son_cik - gir) / gir if gir else None
        if son["yon"] == "SHORT" and hareket is not None:
            hareket = -hareket
        # TP1 alindi mi (ayri kayit)
        tp1 = any(t.get("kismi") for t in v)
        out.append({
            "id": i, "sym": son["sym"], "yon": son["yon"], "giris_ts": giris_ts,
            "gun": giris_ts.strftime("%m-%d"),
            "net": net, "marjin": ilk.get("marjin") or 0,
            "notional": ilk.get("notional") or 0, "kaldirac": ilk.get("kaldirac") or 0,
            "kaynak": son.get("kaynak") or "testbot", "sebep": son.get("sebep"),
            "tp1": tp1, "hareket": hareket, "tut": max((t.get("tutma_saat") or 0) for t in v),
            "chg24": ilk.get("chg24_giriste"), "skor": ilk.get("skor_giriste"),
            "kayit": len(v),
        })
    return out


def med(x):
    return sx.median(x) if x else float("nan")


G = [z for z in pozisyonlar("golge_islemler.jsonl")
     if z["giris_ts"] >= BOGA and z["yon"] == "LONG"]
T = [z for z in pozisyonlar("testbot_islemler.jsonl")
     if z["giris_ts"] >= BOGA and z["yon"] == "LONG"]

print("BOGA BACAGI LONG — FARKIN AYRISTIRILMASI   golge N=%d  testbot N=%d" % (len(G), len(T)))
print("=" * 104)

print("\n(b) MEKANIK — CLAUDE.md ZORUNLU SINAMASI: stop genisligi ve stop-olma orani esit mi?")
print("-" * 104)
print("   %-10s %8s %8s | %10s %10s %10s | %10s" %
      ("defter", "N", "stop%", "stop gen.med", "stop gen.ort", "TP1 orani", "med tutma"))
for ad, w in (("GOLGE", G), ("TESTBOT", T)):
    saf_stop = [z for z in w if z["sebep"] == "STOP" and not z["tp1"]]
    gen = [z["hareket"] for z in saf_stop if z["hareket"] is not None]
    print("   %-10s %8d %7.1f%% | %11.3f%% %11.3f%% | %9.1f%% | %8.1f sa"
          % (ad, len(w), 100.0 * sum(1 for z in w if z["sebep"] == "STOP") / len(w),
             med(gen), sum(gen) / len(gen) if gen else 0,
             100.0 * sum(1 for z in w if z["tp1"]) / len(w),
             med([z["tut"] for z in w])))
print("   NOT: 'stop gen.' = TP1 ALMAMIS saf stoplarin fiyat hareketi (LONG'da negatif).")

print("\n(a) SECIM/ZAMANLAMA — TP1 alan / almayan ayri  (net/notional = saf yuzde)")
print("-" * 104)
print("   %-10s %-14s %5s %10s %10s %10s" % ("defter", "grup", "N", "medyan%", "ort%", "toplam $"))
for ad, w in (("GOLGE", G), ("TESTBOT", T)):
    for gad, sec in (("TP1 ALDI", lambda z: z["tp1"]), ("TP1 YOK", lambda z: not z["tp1"])):
        v = [z for z in w if sec(z)]
        if not v:
            continue
        h = [100.0 * z["net"] / z["notional"] for z in v if z["notional"]]
        print("   %-10s %-14s %5d %9.3f%% %9.3f%% %+10.2f"
              % (ad, gad, len(v), med(h), sum(h) / len(h), sum(z["net"] for z in v)))

print("\n(c) BOYUT — kasanin hissettigi risk")
print("-" * 104)
for ad, w in (("GOLGE", G), ("TESTBOT", T)):
    st = json.load(open(os.path.join(PROJE, "%s_state.json"
                                     % ("golge" if ad == "GOLGE" else "testbot")), encoding="utf-8"))
    bb = st.get("baslangic_bakiye") or 0
    print("   %-10s medyan marjin %7.1f $  medyan notional %7.0f $  medyan kald %4.1f"
          " | baslangic bakiye %8.2f  equity %8.2f"
          % (ad, med([z["marjin"] for z in w]), med([z["notional"] for z in w]),
             med([z["kaldirac"] for z in w]), bb, st.get("equity") or 0))
    r = [100.0 * z["net"] / z["marjin"] for z in w if z["marjin"]]
    print("   %-10s marjin-basi getiri (ROI)  medyan %+7.2f%%  ort %+7.2f%%" % ("", med(r), sum(r) / len(r)))

print("\n(d) KUYRUK YOGUNLASMASI — sonucu kac pozisyon tasiyor")
print("-" * 104)
for ad, w in (("GOLGE", G), ("TESTBOT", T)):
    s = sorted(w, key=lambda z: -z["net"])
    top = sum(z["net"] for z in w)
    for k in (1, 3, 5, 9):
        if k <= len(s):
            print("   %-10s en iyi %2d pozisyon  %+9.2f   (toplam %+9.2f · geri kalan %+9.2f)"
                  % (ad, k, sum(z["net"] for z in s[:k]), top, top - sum(z["net"] for z in s[:k])))
    print()

print("(e) GUN-KUMELI FARK — 6 gun, kume SAYISI COK AZ (t guvenilmez, aynen raporlanir)")
print("-" * 104)
gun_g = collections.defaultdict(list)
gun_t = collections.defaultdict(list)
for z in G:
    if z["notional"]:
        gun_g[z["gun"]].append(100.0 * z["net"] / z["notional"])
for z in T:
    if z["notional"]:
        gun_t[z["gun"]].append(100.0 * z["net"] / z["notional"])
farklar = []
print("   %-8s %8s %10s | %8s %10s | %10s" % ("gun", "golge N", "golge ort%", "bot N", "bot ort%", "fark"))
for g_ in sorted(set(gun_g) | set(gun_t)):
    a = gun_g.get(g_, [])
    b = gun_t.get(g_, [])
    if a and b:
        d = sum(a) / len(a) - sum(b) / len(b)
        farklar.append(d)
        print("   %-8s %8d %9.3f%% | %8d %9.3f%% | %+9.3f" % (g_, len(a), sum(a) / len(a),
                                                              len(b), sum(b) / len(b), d))
    else:
        print("   %-8s %8d %9s | %8d %9s | %10s"
              % (g_, len(a), "%.3f%%" % (sum(a) / len(a)) if a else "-",
                 len(b), "%.3f%%" % (sum(b) / len(b)) if b else "-", "-"))
if len(farklar) >= 2:
    m = sum(farklar) / len(farklar)
    sd = sx.stdev(farklar)
    t = m / (sd / math.sqrt(len(farklar))) if sd else float("nan")
    print("   gun-kumeli fark ort %+.3f  sd %.3f  N_kume=%d  ->  t = %+.2f  (%d/%d gunde golge onde)"
          % (m, sd, len(farklar), t, sum(1 for x in farklar if x > 0), len(farklar)))

print("\n(f) AYNI SEMBOLDE ESLESME — ikisi de ayni gun ayni coini LONG'ladi mi?")
print("-" * 104)
gi = collections.defaultdict(list)
for z in G:
    gi[(z["sym"], z["gun"])].append(z)
es = []
for z in T:
    k = (z["sym"], z["gun"])
    if k in gi:
        for y in gi[k]:
            es.append((z, y))
print("   eslesen cift: %d" % len(es))
if es:
    dt = [100.0 * z["net"] / z["notional"] for z, y in es if z["notional"]]
    dg = [100.0 * y["net"] / y["notional"] for z, y in es if y["notional"]]
    print("   bot ort %+.3f%%   golge ort %+.3f%%   fark %+.3f puan"
          % (sum(dt) / len(dt), sum(dg) / len(dg), sum(dg) / len(dg) - sum(dt) / len(dt)))
    for z, y in sorted(es, key=lambda p: p[0]["giris_ts"])[:14]:
        print("      %-9s %s  bot %+8.2f $ (%+6.2f%%, %s)   golge %+8.2f $ (%+6.2f%%, %s)"
              % (z["sym"], z["giris_ts"].strftime("%m-%d %H:%M"),
                 z["net"], 100.0 * z["net"] / z["notional"] if z["notional"] else 0, z["sebep"],
                 y["net"], 100.0 * y["net"] / y["notional"] if y["notional"] else 0, y["sebep"]))

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
