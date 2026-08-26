#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""POZISYON VERI KUMESI. On-kayit: ON_KAYIT_pozisyon.md (e1097b5).
Botun KENDI pozisyonlari + giris anindaki aday fotografi + IKI etiket.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, datetime, collections, statistics

HERE  = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(os.path.dirname(HERE))
KL    = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
OFSET = -3
UFUK  = 24

SAYISAL = ["score", "price", "comp", "vol_x", "oi24", "oi3", "funding", "pos",
           "last1", "last3", "chg24", "rel3", "btc_chg3", "top_ls", "glob_ls",
           "taker", "ma50_mesafe", "kaldirac"]
KATEGORIK = ["stage", "rejim", "smart", "dip_yakit", "ayrisma", "dusuk_float", "yon"]

print("POZISYON VERI KUMESI — on-kayit e1097b5")
print("=" * 92)

# --- 1) pozisyonlar (id bazli, kismi kayitlar BIRLESTIRILIR) ---------------
R = [json.loads(l) for l in open(os.path.join(PROJE, "testbot_islemler.jsonl"),
                                 encoding="utf-8") if l.strip()]
grup = collections.defaultdict(list)
for r in R:
    if r.get("id") is not None:
        grup[r["id"]].append(r)
print("kayit %d  ->  POZISYON %d  (id bazli)" % (len(R), len(grup)))

poz = []
for i, rs in grup.items():
    kap = [x for x in rs if not x.get("kismi")]
    if not kap:
        continue
    k = kap[-1]
    try:
        t = datetime.datetime.strptime(k["ts"][:19], "%Y-%m-%d %H:%M:%S")
    except Exception:
        continue
    g = t - datetime.timedelta(hours=float(k.get("tutma_saat") or 0))
    poz.append(dict(id=i, sym=k["sym"], yon=k.get("yon"), giris=g,
                    gun=g.strftime("%Y-%m-%d"),
                    kaldirac=k.get("kaldirac"),
                    L2=sum(x.get("sonuc_usdt") or 0 for x in rs)))   # P&L: SUZGEC YOK
print("giris anina cevrilen: %d  ·  net toplam %+.2f $"
      % (len(poz), sum(p["L2"] for p in poz)))

# --- 2) aday arsivi fotografi ----------------------------------------------
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

es = 0
for p in poz:
    en, ed = None, 1e9
    for x in A.get(p["sym"], []):
        dd = abs((p["giris"] - x["_t"]).total_seconds())
        if dd < ed:
            ed, en = dd, x
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
print("aday arsiviyle eslesen: %d/%d  (%%%.1f)" % (es, len(poz), 100*es/len(poz)))

# --- 3) L1: ham +24s getiri, YONE GORE isaretli ----------------------------
gerek = collections.defaultdict(list)
for p in poz:
    gerek[p["sym"]].append(p)
n1 = 0
for sym, ps in gerek.items():
    # TAZE onbellek once (08-26'ya kadar), yoksa paylasilan uzun seri
    fp = os.path.join(HERE, "taze_mum", sym + ".json")
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
        saat = p["giris"].replace(minute=0, second=0, microsecond=0)
        j = idx.get(saat + datetime.timedelta(hours=OFSET))
        if j is None or j+1+UFUK >= len(c) or c[j+1] <= 0:
            continue
        ham = 100.0 * (c[j+1+UFUK] / c[j+1] - 1.0)
        p["L1"] = ham if p["yon"] == "LONG" else -ham      # YONE GORE ISARETLI
        n1 += 1
print("L1 (ham +24s, yone gore isaretli) hesaplanan: %d/%d" % (n1, len(poz)))

# L1 (ham getiri) OPSIYONEL: klines kapsamayabilir. L2 (gercek P&L) her
# kapanan pozisyonda VAR -> asil soru (T1/para) tam ornekle olculur.
kul = [p for p in poz if p.get("_es")]
for p in kul:
    p["giris"] = p["giris"].isoformat()
    p.pop("_es", None)
print("\nKULLANILABILIR: %d pozisyon" % len(kul))

TEST = sorted({p["gun"] for p in kul if p["gun"] >= "2026-08-19"})
say = collections.Counter(p["gun"] for p in kul)
print("test gunu %d: %s" % (len(TEST), TEST))
for g in TEST:
    alt = [p for p in kul if p["gun"] == g]
    ctx = [p for p in kul if p["gun"] < g]
    print("   %s  test=%-3d baglam=%-3d  net %+8.2f $  LONG %d/%d"
          % (g, len(alt), len(ctx), sum(x["L2"] for x in alt),
             sum(1 for x in alt if x["yon"] == "LONG"), len(alt)))

t = [p for p in kul if p["gun"] >= "2026-08-19"]
print("\nTEST TOPLAM: %d pozisyon · net %+.2f $ · kazanan %d (%%%.0f)"
      % (len(t), sum(x["L2"] for x in t), sum(1 for x in t if x["L2"] > 0),
         100*sum(1 for x in t if x["L2"] > 0)/len(t)))
l1 = [x["L1"] for x in t if x.get("L1") is not None]
print("L1 dolu %d/%d · ort %+.3f%%   ·   L2 ort %+.2f $"
      % (len(l1), len(t), statistics.mean(l1) if l1 else float("nan"),
         statistics.mean(x["L2"] for x in t)))
json.dump({"sayisal": SAYISAL, "kategorik": KATEGORIK, "test_gun": TEST,
           "satir": kul}, open(os.path.join(HERE, "poz_veri.json"), "w"))
print("\nYAZILDI -> scratchpad/tabfm/poz_veri.json")
