#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EKSEN 1 / IS 1 — UZUN TUTMA: kenar ufukla buyuyor mu, maliyet sabit mi?

TEZ: islem basi maliyet (ucret+slipaj = 0,17) SABIT. Brut kenar ufukla ~sqrt(t)
buyurse, uzun tutma maliyet oranini dusurur. AMA fonlama ufukla DOGRUSAL buyur.
Hangisi kazanir? Hic olculmedi — 72 saat en uzun denenen ufuk.

SIRA (CLAUDE.md): HAM getiri once, mekanik sonra.
  1. HAM ileri getiri: 24s · 72s · 168s (1 hafta) · 336s (2 hafta) · 720s (1 ay)
  2. Ayni ufuklarda fonlama yuku
  3. Net = ham - 0,1726 (sabit) + fonlama

GIRIS KUMESI: botun kenar ureten kapisi (funding <= -0,05). SHORT.
ESIK TARAMASI YOK — ufuklar dogal zaman olcekleri.
"""
import json, os, sys, collections, random, statistics as stx, bisect, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ileri_rr as ir

UFUKLAR = [(24, "24s"), (72, "72s"), (168, "1 hafta"), (336, "2 hafta"), (720, "1 ay")]
MAL = 0.1726
random.seed(41)
K = collections.defaultdict(lambda: {"ham": [], "fon": [], "ts": []})

for fn in sorted(os.listdir(ir.KLINE)):
    if not fn.endswith(".json"): continue
    fp = os.path.join(ir.FUND, fn)
    if not os.path.exists(fp): continue
    try:
        fr = json.load(open(fp, encoding="utf-8"))
        b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
    except Exception: continue
    if not fr or len(b) < ir.ISINMA + 760: continue
    ft = [x["t"] for x in fr]
    faz = random.randint(0, 23)
    for i in range(ir.ISINMA + faz, len(b) - 740, ir.SEYRELT):
        x = b[i]
        if (x.get("qv") or 0) < ir.MIN_VOL/24 or i < 24: continue
        if (x["c"]/b[i-24]["c"]-1)*100 >= ir.PUMP: continue
        k = bisect.bisect_right(ft, x["t"]) - 1
        if k < 0 or fr[k]["r"]*100 > ir.FUND_ESIK: continue
        gi = i+1
        ref = b[gi]["o"]
        if ref <= 0: continue
        for h, ad in UFUKLAR:
            j = gi + h
            if j >= len(b): continue
            ham = (ref - b[j]["c"])/ref*100                 # SHORT ham getiri
            fon = ir.fonlama_pct(ft, fr, b[gi]["t"], b[j]["t"])
            d = K[ad]
            d["ham"].append(ham); d["fon"].append(fon); d["ts"].append(b[gi]["t"])

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

def kumeli(v, ts):
    a = collections.defaultdict(list)
    for z, t in zip(v, ts): a[ay(t)].append(z)
    ok = [m for m in a if len(a[m]) >= 20]
    if len(ok) < 3: return None
    ms = [stx.mean(a[m]) for m in ok]
    se = stx.stdev(ms)/len(ms)**0.5
    return stx.mean(ms), (stx.mean(ms)/se if se else 0), len(ok), sum(1 for z in ms if z > 0)

print("EKSEN 1 / IS 1 — UZUN TUTMA (SHORT, funding kapisi, 2 yil)")
print("=" * 104)
print("Sabit maliyet: %%%.4f/islem  ·  fonlama ufukla degisir\n" % MAL)
print("%-10s %8s %11s %11s %11s %11s %11s %9s"
      % ("ufuk", "N", "HAM", "fonlama", "NET", "ham ay-t", "net ay-t", "poz ay"))
onc = None
for h, ad in UFUKLAR:
    d = K[ad]
    n = len(d["ham"])
    if n < 200: continue
    net = [a - MAL + f for a, f in zip(d["ham"], d["fon"])]
    kh = kumeli(d["ham"], d["ts"]); kn = kumeli(net, d["ts"])
    print("%-10s %8d %+11.4f %+11.4f %+11.4f %+11.2f %+11.2f %6d/%-3d"
          % (ad, n, stx.mean(d["ham"]), stx.mean(d["fon"]), stx.mean(net),
             kh[1] if kh else 0, kn[1] if kn else 0, kn[3] if kn else 0, kn[2] if kn else 0))

print("\nOLCEKLEME — kenar ufukla nasil buyuyor?")
print("%-10s %11s %11s %13s %13s" % ("ufuk", "HAM", "sqrt(saat)", "HAM/sqrt(t)", "fonlama/saat"))
for h, ad in UFUKLAR:
    d = K[ad]
    if len(d["ham"]) < 200: continue
    hm = stx.mean(d["ham"])
    print("%-10s %+11.4f %11.2f %+13.4f %+13.5f"
          % (ad, hm, h**0.5, hm/(h**0.5), stx.mean(d["fon"])/h))
print("\nHAM/sqrt(t) SABIT ise kenar rastgele-yuruyus gibi olcekleniyor demektir.")
print("ARTIYORSA uzun tutma lehine, AZALIYORSA kenar erken bitiyor.")
