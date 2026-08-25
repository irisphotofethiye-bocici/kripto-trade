# -*- coding: utf-8 -*-
"""KOL A — botun GERCEK girisleri, farkli stop carpanlariyla yeniden oynatilir.
Ayni girisler, farkli cikis -> ESLESMIS test (CLAUDE.md: t iyi tanimli).
On-kayit: ON_KAYIT.md   SALT OKUMA, bota yazmaz."""
import json, os, bisect, datetime, statistics as sx

PROJE = r"c:\Users\alper\Desktop\kripto trade"
KL = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
FUND = os.path.join(PROJE, "scratchpad", "funding_gecmis")
CIK = os.path.join(PROJE, "scratchpad", "stop_carpani", "kol_a.json")
KLAR = (0.50, 0.75, 1.00, 1.25, 1.50, 2.00, 2.50, 3.00, 4.00, 6.00, 999.0)
HLAR = (2, 4, 8, 24)
HMAX = max(HLAR)
F = "%Y-%m-%d %H:%M:%S"

# --- girisler: pozisyon_izleme'den (atr_giriste YALNIZ burada var)
giris = {}
for l in open(os.path.join(PROJE, "pozisyon_izleme.jsonl"), encoding="utf-8"):
    try: r = json.loads(l)
    except Exception: continue
    i = r.get("id")
    if i is None or i in giris: continue
    g, a, y, gt = r.get("giris"), r.get("atr_giriste"), r.get("yon"), r.get("giris_ts")
    if not (g and a and y and gt) or a <= 0: continue
    try: ms = int(datetime.datetime.strptime(gt, F).timestamp()*1000)
    except Exception: continue
    giris[i] = {"id": i, "sym": r["sym"], "giris": g, "atr": a, "yon": y, "ts": ms,
                "kaldirac": r.get("kaldirac")}
print("benzersiz giris (atr_giriste dolu): %d" % len(giris))

sonuc, atlanan = [], 0
onbellek = {}
for z in giris.values():
    sym = z["sym"]
    if sym not in onbellek:
        y = os.path.join(KL, sym + ".json")
        onbellek[sym] = json.load(open(y, encoding="utf-8")) if os.path.exists(y) else None
        fy = os.path.join(FUND, sym + ".json")
        ft, fr = [], []
        if os.path.exists(fy):
            for x in json.load(open(fy, encoding="utf-8")):
                if "r" in x: ft.append(x["t"]); fr.append(x["r"])
        fk = [0.0]
        for r in fr: fk.append(fk[-1]+r)
        onbellek[sym+"|f"] = (ft, fk)
    b = onbellek[sym]
    if not b: atlanan += 1; continue
    ts = [x["t"] for x in b]
    i = bisect.bisect_right(ts, z["ts"])          # giris barindan SONRAKI bar (muhafazakar)
    if i < 1 or i+HMAX >= len(b): atlanan += 1; continue
    ft, fk = onbellek[sym+"|f"]
    g, a, yon = z["giris"], z["atr"], z["yon"]
    kayit = {"id": z["id"], "sym": sym, "yon": yon, "t": z["ts"],
             "gun": datetime.datetime.utcfromtimestamp(z["ts"]/1000).strftime("%Y-%m-%d"),
             "atrp": a/g*100, "r": {}}
    ters = 0.0
    for j in range(i, i+HMAX):
        t_ = (b[j]["h"]-g)/g*100 if yon == "SHORT" else (g-b[j]["l"])/g*100
        ters = max(ters, t_)
    kayit["ters"] = ters
    for k in KLAR:
        stop = g + k*a if yon == "SHORT" else g - k*a
        vur = None
        for j in range(i, i+HMAX):
            if (yon == "SHORT" and b[j]["h"] >= stop) or (yon == "LONG" and b[j]["l"] <= stop):
                vur = j; break
        for H in HLAR:
            son_i = i+H-1
            if vur is not None and vur <= son_i: cikis, cj = stop, vur
            else: cikis, cj = b[son_i]["c"], son_i
            r_ = (g-cikis)/g*100 if yon == "SHORT" else (cikis-g)/g*100
            if ft:
                i0 = bisect.bisect_right(ft, z["ts"]); i1 = bisect.bisect_right(ft, b[cj]["t"])
                fon = fk[i1]-fk[i0]
                r_ += fon if yon == "SHORT" else -fon
            kayit["r"]["%g|%d" % (k, H)] = r_
    sonuc.append(kayit)

json.dump({"olaylar": sonuc, "KLAR": KLAR, "HLAR": HLAR}, open(CIK, "w"))
print("oynatilan: %d   atlanan (mum/ileri veri yok): %d" % (len(sonuc), atlanan))
import collections
print("yon:", dict(collections.Counter(x["yon"] for x in sonuc)))
print("ATR/fiyat medyan: %%%.2f" % sx.median([x["atrp"] for x in sonuc]))
