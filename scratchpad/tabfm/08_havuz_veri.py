#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BES DEFTERIN HAVUZU. On-kayit: ON_KAYIT_havuz.md (e1b30d8). SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, datetime, collections, statistics

HERE  = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(os.path.dirname(HERE))
KL    = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
TAZE  = os.path.join(HERE, "taze_mum")
OFSET, UFUK = -3, 24
DEFTER = ["testbot", "golge", "defter2", "defter3", "ayna"]   # ONCELIK SIRASI

SAYISAL = ["score", "price", "comp", "vol_x", "oi24", "oi3", "funding", "pos",
           "last1", "last3", "chg24", "rel3", "btc_chg3", "top_ls", "glob_ls",
           "taker", "ma50_mesafe", "kaldirac"]
KATEGORIK = ["stage", "rejim", "smart", "dip_yakit", "ayrisma", "dusuk_float", "yon"]
# 'kaynak' (hangi defter) OZELLIK DEGILDIR -> model "golge kotudur" ogrenirdi.
# Yalnizca ust-veri olarak tasinir (H5 icin).

print("HAVUZ VERI KUMESI — on-kayit e1b30d8")
print("=" * 92)

A = collections.defaultdict(list)
for line in open(os.path.join(PROJE, "testbot_aday_arsiv.jsonl"), encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    try:
        x = json.loads(line)
    except Exception:
        continue
    if x.get("sym") and x.get("ts"):
        try:
            x["_t"] = datetime.datetime.strptime(x["ts"][:16], "%Y-%m-%d %H:%M")
        except Exception:
            continue
        A[x["sym"]].append(x)


def defter_oku(ad):
    R = []
    p = os.path.join(PROJE, ad + "_islemler.jsonl")
    if not os.path.exists(p):
        return []
    for l in open(p, encoding="utf-8"):
        l = l.strip()
        if l:
            try:
                R.append(json.loads(l))
            except Exception:
                pass
    g = collections.defaultdict(list)
    for r in R:
        if r.get("id") is not None:
            g[r["id"]].append(r)
    out = []
    for i, rs in g.items():
        kap = [x for x in rs if not x.get("kismi")]
        if not kap:
            continue
        k = kap[-1]
        try:
            t = datetime.datetime.strptime(k["ts"][:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
        gt = t - datetime.timedelta(hours=float(k.get("tutma_saat") or 0))
        marj = k.get("marjin")
        if not marj:
            continue
        net = sum(x.get("sonuc_usdt") or 0 for x in rs)        # SUZGEC YOK
        sg = (k.get("sebep_giris") or "").lower()
        out.append(dict(defter=ad, sym=k.get("sym"), yon=k.get("yon"), giris=gt,
                        gun=gt.strftime("%Y-%m-%d"),
                        kaldirac=k.get("kaldirac"),
                        L2=100.0 * net / float(marj),          # POZISYON GETIRISI %
                        net_usdt=net,
                        pump=("pump" in sg),
                        ret=(not ("pump" in sg)) and ad == "golge"))
    return out


havuz, dup = {}, collections.Counter()
for ad in DEFTER:
    P = defter_oku(ad)
    yeni = 0
    for p in P:
        k = (p["sym"], p["yon"], p["giris"].strftime("%Y-%m-%d %H"))
        if k in havuz:
            dup[ad] += 1
            continue
        havuz[k] = p
        yeni += 1
    print("  %-9s %4d poz  ->  havuza YENI %4d  (cift %d)" % (ad, len(P), yeni, dup[ad]))
poz = list(havuz.values())
print("\nHAVUZ tekil giris: %d" % len(poz))

# --- ozellikler ---
es = 0
for p in poz:
    en, ed = None, 1e9
    for x in A.get(p["sym"], []):
        d = abs((p["giris"] - x["_t"]).total_seconds())
        if d < ed:
            ed, en = d, x
    if en is not None and ed <= 3600:
        es += 1
        for a in SAYISAL:
            if a == "kaldirac":
                continue
            v = en.get(a)
            try:
                p[a] = float(v) if v is not None else None
            except Exception:
                p[a] = None
        for a in KATEGORIK:
            if a == "yon":
                continue
            v = en.get(a)
            p[a] = None if v is None else str(v)
        p["_es"] = True
    else:
        p["_es"] = False
print("aday arsiviyle eslesen: %d/%d (%%%.1f)" % (es, len(poz), 100*es/len(poz)))

# --- L1: ham +24s, yone gore isaretli ---
ger = collections.defaultdict(list)
for p in poz:
    ger[p["sym"]].append(p)
n1 = 0
for sym, ps in ger.items():
    fp = os.path.join(TAZE, sym + ".json")
    if not os.path.exists(fp):
        fp = os.path.join(KL, sym + ".json")
    if not os.path.exists(fp):
        continue
    try:
        b = json.load(open(fp, encoding="utf-8"))
    except Exception:
        continue
    idx, c = {}, []
    for j, z in enumerate(b):
        idx[datetime.datetime(1970,1,1)+datetime.timedelta(milliseconds=int(z["t"]))] = j
        c.append(float(z["c"]))
    for p in ps:
        s = p["giris"].replace(minute=0, second=0, microsecond=0)
        j = idx.get(s + datetime.timedelta(hours=OFSET))
        if j is None or j+1+UFUK >= len(c) or c[j+1] <= 0:
            continue
        h = 100.0 * (c[j+1+UFUK] / c[j+1] - 1.0)
        p["L1"] = h if p["yon"] == "LONG" else -h
        n1 += 1
print("L1 hesaplanan: %d/%d" % (n1, len(poz)))

kul = [p for p in poz if p.get("_es")]
for p in kul:
    p["giris"] = p["giris"].isoformat()
    p.pop("_es", None)

say = collections.Counter(p["gun"] for p in kul)
TEST = []
for g in sorted(say):
    ctx = sum(1 for p in kul if p["gun"] < g)
    if say[g] >= 15 and ctx >= 60:
        TEST.append(g)
print("\nKULLANILABILIR %d pozisyon · %d gun" % (len(kul), len(say)))
print("TEST GUNU %d (>=15 giris VE baglam>=60):" % len(TEST))
for g in TEST:
    alt = [p for p in kul if p["gun"] == g]
    print("   %s  test=%-3d baglam=%-4d  getiri ort %+6.2f%%  LONG %d/%d  defter %s"
          % (g, len(alt), sum(1 for p in kul if p["gun"] < g),
             statistics.mean(p["L2"] for p in alt),
             sum(1 for p in alt if p["yon"] == "LONG"), len(alt),
             dict(collections.Counter(p["defter"] for p in alt))))

t = [p for p in kul if p["gun"] in TEST]
print("\nTEST TOPLAM: %d pozisyon · getiri ort %+.2f%% · kazanan %%%.0f"
      % (len(t), statistics.mean(p["L2"] for p in t),
         100*sum(1 for p in t if p["L2"] > 0)/len(t)))
print("   defter: %s" % dict(collections.Counter(p["defter"] for p in t)))
print("   gercek RET alt kumesi (H5): %d" % sum(1 for p in t if p["ret"]))
json.dump({"sayisal": SAYISAL, "kategorik": KATEGORIK, "test_gun": TEST,
           "satir": kul}, open(os.path.join(HERE, "havuz_veri.json"), "w"))
print("\nYAZILDI -> scratchpad/tabfm/havuz_veri.json")
