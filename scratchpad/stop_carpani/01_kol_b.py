# -*- coding: utf-8 -*-
"""KOL B — olay seviyesi vekil girisler, ATR stop carpani taramasi.
On-kayit: scratchpad/stop_carpani/ON_KAYIT.md   SALT OKUMA, bota yazmaz.
Fonlama birimi: YUZDE/8sa (dogrulandi, medyan |r|=%0,0050). *100 UYGULANMAZ."""
import json, glob, os, bisect, datetime, statistics as sx

PROJE = r"c:\Users\alper\Desktop\kripto trade"
KL = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
FUND = os.path.join(PROJE, "scratchpad", "funding_gecmis")
CIK = os.path.join(PROJE, "scratchpad", "stop_carpani", "kol_b.json")

KLAR = (0.50, 0.75, 1.00, 1.25, 1.50, 2.00, 2.50, 3.00, 4.00, 6.00, 999.0)  # 999 = STOPSUZ
HLAR = (2, 4, 8, 24)
HMAX = max(HLAR)
PUMP = 20.0          # chg24 esigi
BEKLEME = 24

# --- fonlama birim iddiasi (CLAUDE.md kurali)
_ilk = json.load(open(os.path.join(FUND, os.listdir(FUND)[0]), encoding="utf-8"))
_med = sx.median([abs(x["r"]) for x in _ilk if "r" in x])
assert _med < 0.5, "FONLAMA BIRIM HATASI: medyan |r|=%.4f (yuzde bekleniyordu)" % _med

# --- BTC rejimi (16_rejim_kosullu ile ayni tanim)
rej_t, rej_v = [], []
if os.path.exists(os.path.join(KL, "BTC.json")):
    z = 0.0
    for x in json.load(open(os.path.join(KL, "BTC.json"), encoding="utf-8")):
        z = max(z, x["h"])
        dd = (x["c"]-z)/z*100 if z else 0.0
        rej_t.append(x["t"])
        rej_v.append("ATH_BOLGESI" if dd > -10 else "DUZELTME" if dd > -30 else "DERIN_AYI")
def rejim(t):
    i = bisect.bisect_right(rej_t, t)-1
    return rej_v[i] if i >= 0 else "?"

def atr_serisi(b, n=14):
    """Wilder ATR, olcucu.py:98 ile ayni."""
    out = [None]*len(b)
    tr = []
    for i in range(1, len(b)):
        x, pc = b[i], b[i-1]["c"]
        tr.append(max(x["h"]-x["l"], abs(x["h"]-pc), abs(x["l"]-pc)))
        if len(tr) == n:
            a = sum(tr)/n; out[i] = a
        elif len(tr) > n:
            a = (out[i-1]*(n-1) + tr[-1])/n; out[i] = a
    return out

olaylar = []
sembol = 0
for f in sorted(glob.glob(os.path.join(KL, "*.json"))):
    sym = os.path.basename(f)[:-5]
    try: b = json.load(open(f, encoding="utf-8"))
    except Exception: continue
    if len(b) < 200: continue
    sembol += 1
    # fonlama
    fy = os.path.join(FUND, sym + ".json")
    ft, fr = [], []
    if os.path.exists(fy):
        try:
            for x in json.load(open(fy, encoding="utf-8")):
                if "r" in x: ft.append(x["t"]); fr.append(x["r"])
        except Exception: pass
    fkum = [0.0]
    for r in fr: fkum.append(fkum[-1] + r)

    atr = atr_serisi(b)
    c = [x["c"] for x in b]
    son = -10**9
    for i in range(30, len(b)-HMAX-1):
        if atr[i] is None or c[i] <= 0 or c[i-24] <= 0: continue
        chg24 = (c[i]/c[i-24]-1)*100
        for yon, kosul in (("SHORT", chg24 >= PUMP), ("LONG", chg24 <= -PUMP)):
            if not kosul: continue
            if i - son < BEKLEME: continue
            son = i
            giris, a = c[i], atr[i]
            if a <= 0: continue
            kayit = {"sym": sym, "yon": yon, "t": b[i]["t"],
                     "gun": datetime.datetime.utcfromtimestamp(b[i]["t"]/1000).strftime("%Y-%m-%d"),
                     "rejim": rejim(b[i]["t"]), "chg24": chg24,
                     "atrp": a/giris*100, "r": {}}
            # azami ters hareket (likidasyon denetimi)
            ters = 0.0
            for j in range(i+1, i+HMAX+1):
                t_ = (b[j]["h"]-giris)/giris*100 if yon == "SHORT" else (giris-b[j]["l"])/giris*100
                ters = max(ters, t_)
            kayit["ters"] = ters
            for k in KLAR:
                stop = giris + k*a if yon == "SHORT" else giris - k*a
                vur = None
                for j in range(i+1, i+HMAX+1):
                    if (yon == "SHORT" and b[j]["h"] >= stop) or (yon == "LONG" and b[j]["l"] <= stop):
                        vur = j; break
                for H in HLAR:
                    if vur is not None and vur <= i+H:
                        cikis, cj = stop, vur
                    else:
                        cikis, cj = c[i+H], i+H
                    g = (giris-cikis)/giris*100 if yon == "SHORT" else (cikis-giris)/giris*100
                    # fonlama: giris ile cikis arasindaki oranlarin toplami (yuzde)
                    if ft:
                        i0 = bisect.bisect_right(ft, b[i]["t"]); i1 = bisect.bisect_right(ft, b[cj]["t"])
                        fon = fkum[i1]-fkum[i0]
                    else:
                        fon = 0.0
                    g += fon if yon == "SHORT" else -fon
                    kayit["r"]["%g|%d" % (k, H)] = g
                    if H == HLAR[-1]:
                        kayit.setdefault("stopta", {})["%g" % k] = 1 if (vur is not None and vur <= i+H) else 0
            olaylar.append(kayit)

json.dump({"olaylar": olaylar, "KLAR": KLAR, "HLAR": HLAR}, open(CIK, "w"))
print("sembol %d   OLAY %s" % (sembol, format(len(olaylar), ",")))
import collections
c2 = collections.Counter(x["yon"] for x in olaylar)
print("yon:", dict(c2))
print("gun:", len(set(x["gun"] for x in olaylar)), " sembol:", len(set(x["sym"] for x in olaylar)))
print("->", CIK)
