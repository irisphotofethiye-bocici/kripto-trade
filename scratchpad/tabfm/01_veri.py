#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TabFM olcumu ADIM 1 — veri kumesi kur. On-kayit: ON_KAYIT.md (43b0785).

Etiket HAM +24s getiri (mekanik YOK). Sizinti suzgeci on-kayitta SABIT.
SALT OKUMA — bota/deftere dokunmaz.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, datetime, collections, statistics

HERE  = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(os.path.dirname(HERE))
KL    = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
ARSIV = os.path.join(PROJE, "testbot_aday_arsiv.jsonl")
OFSET = -3          # radar ts YEREL (UTC+3) -> UTC. skor_tahmin.py ile AYNI
UFUK  = 24          # ON-KAYITTA SABIT

# --- on-kayitta yazili 23 alan ---------------------------------------------
SAYISAL = ["score", "price", "comp", "vol_x", "oi24", "oi3", "funding", "pos",
           "last1", "last3", "chg24", "rel3", "btc_chg3", "top_ls", "glob_ls",
           "taker", "ma50_mesafe"]
KATEGORIK = ["stage", "rejim", "smart", "dip_yakit", "ayrisma", "dusuk_float"]
# DISLANAN (on-kayit): karar, sonuc, red_kapi, kaynak, float_oran, mcap, ts, sym
DISLANAN = {"karar", "sonuc", "red_kapi", "kaynak", "float_oran", "mcap"}

print("TabFM VERI KUMESI — on-kayit ON_KAYIT.md (43b0785)")
print("=" * 96)

# ---------------------------------------------------------------- 1) arsiv
gorulen, n_satir, cift = {}, 0, 0
for s in open(ARSIV, encoding="utf-8"):
    s = s.strip()
    if not s:
        continue
    n_satir += 1
    try:
        x = json.loads(s)
    except Exception:
        continue
    ts, sym = x.get("ts"), x.get("sym")
    if not ts or not sym:
        continue
    try:
        t = datetime.datetime.strptime(ts[:16], "%Y-%m-%d %H:%M").replace(minute=0)
    except Exception:
        continue
    k = (sym, t)
    if k in gorulen:
        cift += 1
        continue                       # saatteki ILK anlik goruntu
    r = {"sym": sym, "yerel": t, "gun": t.strftime("%Y-%m-%d")}
    for a in SAYISAL:
        v = x.get(a)
        try:
            r[a] = float(v) if v is not None else None
        except Exception:
            r[a] = None
    for a in KATEGORIK:
        v = x.get(a)
        r[a] = None if v is None else str(v)
    gorulen[k] = r

print("arsiv satir %d  ->  (sembol,saat) tekil %d  (cift dusen %d)"
      % (n_satir, len(gorulen), cift))
gecen = set(SAYISAL) | set(KATEGORIK)
print("girdi alani %d  ·  dislanan %s" % (len(gecen), sorted(DISLANAN)))

# ---------------------------------------------------------------- 2) klines
gerek = collections.defaultdict(list)
for v in gorulen.values():
    gerek[v["sym"]].append(v)

satir, eksik_sym, eksik_bar = [], 0, 0
for n, (sym, kayit) in enumerate(sorted(gerek.items())):
    p = os.path.join(KL, sym + ".json")
    if not os.path.exists(p):
        eksik_sym += 1
        continue
    try:
        with open(p, encoding="utf-8") as f:
            b = json.load(f)
    except Exception:
        eksik_sym += 1
        continue
    idx, c, hi, lo = {}, [], [], []
    for i, z in enumerate(b):
        t = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(z["t"]))
        idx[t] = i
        c.append(float(z["c"])); hi.append(float(z["h"])); lo.append(float(z["l"]))
    for v in kayit:
        i = idx.get(v["yerel"] + datetime.timedelta(hours=OFSET))
        if i is None:
            eksik_bar += 1
            continue
        g = i + 1                       # GIRIS = bir SONRAKI saatin kapanisi
        if g < 15 or g + UFUK >= len(c) or c[g] <= 0:
            eksik_bar += 1
            continue
        tr = [max(hi[k] - lo[k], abs(hi[k] - c[k-1]), abs(lo[k] - c[k-1]))
              for k in range(g - 13, g + 1)]
        r = dict(v)
        r["atr"] = 100.0 * (sum(tr) / len(tr)) / c[g]
        r["y"]   = 100.0 * (c[g + UFUK] / c[g] - 1.0)    # HAM +24s getiri
        r.pop("yerel")
        satir.append(r)
    if (n + 1) % 100 == 0:
        print("   ... %d/%d sembol  (satir %d)" % (n + 1, len(gerek), len(satir)), flush=True)

print("\nkullanilabilir gozlem %d  ·  kline'i olmayan sembol %d  ·  bar eslesmeyen %d"
      % (len(satir), eksik_sym, eksik_bar))

GUN = sorted({r["gun"] for r in satir})
say = collections.Counter(r["gun"] for r in satir)
print("gun %d  (%s .. %s)" % (len(GUN), GUN[0], GUN[-1]))
print("\ngun basi satir:")
for g in GUN:
    print("   %s  %5d" % (g, say[g]))

y = [r["y"] for r in satir]
print("\netiket (ham +24s getiri %%): ort %+.3f  medyan %+.3f  std %.3f  min %+.1f  max %+.1f"
      % (statistics.mean(y), statistics.median(y), statistics.pstdev(y), min(y), max(y)))

# alan doluluk
print("\ngirdi alani doluluk:")
for a in SAYISAL + KATEGORIK:
    d = sum(1 for r in satir if r.get(a) is not None)
    print("   %-14s %6d  %%%5.1f" % (a, d, 100.0 * d / len(satir)))

out = os.path.join(HERE, "veri.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump({"sayisal": SAYISAL, "kategorik": KATEGORIK, "ufuk": UFUK,
               "gunler": GUN, "satir": satir}, f)
print("\nYAZILDI -> %s  (%.1f MB)" % (out, os.path.getsize(out) / 1048576))
