#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STOPSUZ / GENIS STOPLU 4-BAR CIKIS (2026-08-11) — KESIFSEL

HAM OLCUM (kanal_ham.py) sunu gosterdi: sinyalin 4 barlik ILERI GETIRISI
kontrolden ANLAMLI iyi (+0.208 ham, t=+3.84 · +0.121 rel, t=+2.31), ama
12 barda kayboluyor. Yani sinyal GERCEK ama KISA OMURLU ve KUCUK.

Onceki tum olcumlerde A-stop vardi (medyan %1.48). Bu, +%0.24'luk bir suruklenmeyi
stop-out'a cevirebilir. SORU: stopu kaldirinca / cok genisletince kenar hayatta kaliyor mu?

KONFIGURASYONLAR: stop yok · 3xATR · 2xATR · A-stop.  Cikis: 4. barin KAPANISI (hedef yok).
Kontrol: ayni rastgele barlar, ayni cikis.
"""
import json, os, random, statistics as stx, sys
sys.path.insert(0, ".")
import kanal_stoch as ks
random.seed(29)

def isle(b, i, ufuk, stop_tipi, atr):
    gi = i + 1
    if gi + ufuk >= len(b):
        return None
    ref = b[gi]["o"]
    if ref <= 0 or atr is None:
        return None
    stop = None
    if stop_tipi == "A":
        dip = min(x["l"] for x in b[i - ks.STOP_NBAR + 1:i + 1])
        stop = dip - ks.STOP_ATR_PAY * atr
    elif stop_tipi in ("2atr", "3atr"):
        stop = ref - (2.0 if stop_tipi == "2atr" else 3.0) * atr
    if stop is not None and stop >= ref:
        return None
    for j in range(gi, gi + ufuk):
        if stop is not None and b[j]["l"] <= stop:
            return (stop - ref) / ref * 100 - ks.MALIYET, "STOP"
    return (b[gi + ufuk - 1]["c"] - ref) / ref * 100 - ks.MALIYET, "SURE"

def oz(v):
    g = [x[0] for x in v if x]
    if len(g) < 40: return None
    sh = stx.pstdev(g) / len(g) ** 0.5
    return {"n": len(g), "ort": stx.mean(g), "sh": sh, "t": stx.mean(g)/sh if sh else 0,
            "stopla": sum(1 for x in v if x and x[1] == "STOP")/len(g)*100}

sinyal, kontrol = [], []
for f in sorted(os.listdir(ks.CACHE)):
    if not f.endswith(".json") or f == "BTC.json": continue
    try: b = json.load(open(os.path.join(ks.CACHE, f), encoding="utf-8"))
    except Exception: continue
    if len(b) < ks.ISINMA + 60: continue
    c = [x["c"] for x in b]
    _, aa = ks.acc_bands(b); A = ks.atr_serisi(b)
    K, D = ks.stochrsi(ks.wilder_rsi(c))
    son = -10**9
    for i in range(ks.ISINMA, len(b) - 30):
        if None in (K[i], D[i], K[i-1], D[i-1], aa[i], A[i]): continue
        if not (K[i-1] < ks.ASIRI_SATIM and K[i-1] <= D[i-1] and K[i] > D[i]): continue
        if b[i]["l"] > aa[i] or i - son < ks.SEYRELT: continue
        son = i
        sinyal.append((b, i, A[i], b[i]["t"]))
    for _ in range(max(2, (len(b) - ks.ISINMA)//150)):
        i = random.randint(ks.ISINMA, len(b) - 31)
        if A[i] is None: continue
        kontrol.append((b, i, A[i], b[i]["t"]))

tl = sorted(x[3] for x in sinyal); ORTA = tl[len(tl)//2]
print("=" * 104)
print("STOPSUZ / GENIS STOPLU 4-BAR CIKIS — hedef YOK, cikis 4. barin kapanisi")
print("=" * 104)
print(f"Sinyal {len(sinyal)} · kontrol {len(kontrol)} · maliyet %{ks.MALIYET}\n")
print(f"{'stop':16}{'N':>6}{'net %':>9}{'t':>7}{'stopa giden':>13}"
      f"{'KONTROL':>10}{'FARK':>8}{'fark t':>9}{'A yari':>9}{'B yari':>9}")
print("-" * 104)
for st, ad in ((None,"stop YOK"), ("3atr","3 x ATR"), ("2atr","2 x ATR"), ("A","A-stop (asil)")):
    sv = [isle(b,i,4,st,a) for b,i,a,_ in sinyal]
    kv = [isle(b,i,4,st,a) for b,i,a,_ in kontrol]
    A_ = oz([isle(b,i,4,st,a) for b,i,a,t in sinyal if t < ORTA])
    B_ = oz([isle(b,i,4,st,a) for b,i,a,t in sinyal if t >= ORTA])
    s, k = oz(sv), oz(kv)
    if not s or not k: continue
    fark = s["ort"] - k["ort"]; fsh = (s["sh"]**2 + k["sh"]**2)**0.5
    im = " *" if s["ort"] > 0 else ""
    print(f"{ad:16}{s['n']:6d}{s['ort']:+9.3f}{s['t']:+7.2f}{s['stopla']:12.1f}%"
          f"{k['ort']:+10.3f}{fark:+8.3f}{fark/fsh:+9.2f}"
          f"{(A_['ort'] if A_ else 0):+9.3f}{(B_['ort'] if B_ else 0):+9.3f}{im}")
print("-" * 104)
print("  '*' = net pozitif · 'fark' = sinyal - kontrol (ayni cikis kuraliyla)")
print("\nUFUK DUYARLILIGI (stop YOK):")
print(f"{'ufuk':>8}{'net %':>10}{'t':>8}{'KONTROL':>10}{'FARK':>9}{'fark t':>9}")
for uf in (2, 4, 6, 8, 12):
    s = oz([isle(b,i,uf,None,a) for b,i,a,_ in sinyal])
    k = oz([isle(b,i,uf,None,a) for b,i,a,_ in kontrol])
    if not s or not k: continue
    fark = s["ort"] - k["ort"]; fsh = (s["sh"]**2 + k["sh"]**2)**0.5
    print(f"{uf:>6} bar{s['ort']:+10.3f}{s['t']:+8.2f}{k['ort']:+10.3f}{fark:+9.3f}{fark/fsh:+9.2f}")
