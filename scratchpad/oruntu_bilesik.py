#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BİLEŞİK ÖRÜNTÜ TESTİ (2026-08-10) — tek-degisken tablolarindan cikan aday kosullarin kesisimi.

ON-KAYIT: asagidaki 4 kosul, tek-degisken tablolarinda (N buyuk, SH kucuk) POZITIF ciktigi
icin secildi — sonuca bakip esik aranmadi, mevcut config esikleri kullanildi:
    A) funding <= funding_derin_neg_pct (-0.05)      tek basina R +0.259 (N=508)
    B) oi24    >= 10                                 tek basina R +0.217/+0.122/+0.184
    C) score   >= radar_alert_skor (40)              monoton artan: +0.167/+0.205/+0.234
    D) stage   == HAZIRLANIYOR                       tek basina R +0.247 (N=114)
REDDEDILEN (tek-degiskende NEGATIF, kazananlarin profilinde olmasina ragmen):
    pos >= 0.85 (range tepesi) -> R -0.071 ; pos 0.7-0.85 -> -0.090
Kurallar: kesisimler ONCEDEN yazildi, her biri KONTROL ile ve ZAMAN IKIYE BOLUNEREK raporlanir.
N<25-30 hucre = izlenim.
"""
import json, os, statistics as st, itertools

BURA = os.path.dirname(os.path.abspath(__file__))
olaylar = json.load(open(os.path.join(BURA, "oruntu_olaylar.json")))
tsl = sorted(o["ts"] for o in olaylar)
ORTA = tsl[len(tsl) // 2]

K = {
    "A funding<=-0.05": lambda o: (o.get("funding") is not None and o["funding"] <= -0.05),
    "B oi24>=10":       lambda o: ((o.get("oi24") or 0) >= 10),
    "C skor>=40":       lambda o: ((o.get("score") or 0) >= 40),
    "D HAZIRLANIYOR":   lambda o: (o.get("stage") == "HAZIRLANIYOR"),
    "X pos>=0.85":      lambda o: ((o.get("pos") or 0) >= 0.85),
}


def ozet(sec, alan="R_short"):
    rs = [o[alan] for o in sec if o.get(alan) is not None]
    if not rs:
        return None
    return {"n": len(rs), "ort": st.mean(rs), "sh": st.pstdev(rs) / len(rs) ** 0.5 if len(rs) > 1 else 0,
            "poz": sum(1 for r in rs if r > 0) / len(rs) * 100}


def yaz(ad, sec, alan="R_short"):
    o = ozet(sec, alan)
    kontrol = ozet([x for x in olaylar if x not in sec], alan)
    a = ozet([x for x in sec if x["ts"] < ORTA], alan)
    b = ozet([x for x in sec if x["ts"] >= ORTA], alan)
    if not o:
        print(f"  {ad:36} N=0")
        return
    f = lambda d: (f"{d['ort']:+.3f}±{d['sh']:.3f}(N={d['n']})" if d else "  –  ")
    kstr = f"{kontrol['ort']:+.3f}" if kontrol else "  –  "
    print(f"  {ad:36} {f(o):26} kontrol {kstr}  |  A {f(a):22} B {f(b)}")


print("=" * 118)
print("BİLEŞİK ÖRÜNTÜ — SHORT (botun gercek stop/2R mekanigi, 46 gun, 7119 bagimsiz olay)")
print(f"Zaman bolme noktasi: {ORTA}")
print("=" * 118)
yaz("TUM OLAYLAR", olaylar)
print()
for ad, fn in K.items():
    yaz(ad + " (tek)", [o for o in olaylar if fn(o)])
print()
for r in (2, 3):
    for kombo in itertools.combinations([k for k in K if not k.startswith("X")], r):
        sec = [o for o in olaylar if all(K[k](o) for k in kombo)]
        if len(sec) >= 20:
            yaz(" + ".join(k.split()[0] for k in kombo) + f"  [{r}'li]", sec)
print()
print("--- KAZANANLARIN PROFILI (pos tepesi) — REDDEDILEN ---")
yaz("X pos>=0.85 (tek)", [o for o in olaylar if K["X pos>=0.85"](o)])
yaz("X + A", [o for o in olaylar if K["X pos>=0.85"](o) and K["A funding<=-0.05"](o)])
print()
print("--- AYNI KOSULLAR LONG TARAFINDA (simetri kontrolu) ---")
for ad in ("A funding<=-0.05", "B oi24>=10", "C skor>=40", "D HAZIRLANIYOR"):
    yaz(ad + " LONG", [o for o in olaylar if K[ad](o)], "R_long")
