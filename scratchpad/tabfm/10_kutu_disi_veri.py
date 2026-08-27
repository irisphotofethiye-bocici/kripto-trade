#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KUTU DISI VERI KUMESI — radar TAM TARAMA. On-kayit e1b6457. SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, datetime, collections, statistics

HERE  = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(os.path.dirname(HERE))
KL    = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
OFSET, UFUK = -3, 2

# 18 alan — score YOK (on-kayit sarti), gizli-secilim alanlari YOK
SAYISAL = ["price", "comp", "vol_x", "pos", "last1", "last3", "rel3",
           "btc_chg3", "btc_chg24", "funding", "oi24", "oi3", "mcap", "float_oran"]
KATEGORIK = ["stage", "dip_yakit", "ayrisma", "dusuk_float", "rejim_yeni"]

print("KUTU DISI VERI — radar TAM TARAMA · skorsuz · ufuk +%ds" % UFUK)
print("=" * 96)


def rejim_serisi():
    """skor_tahmin_rejim.py:42 ile AYNI mantik, KOPYALANDI (import yan etkisi var)."""
    b = json.load(open(os.path.join(KL, "BTC.json"), encoding="utf-8"))
    g = {}
    for x in b:
        d = (datetime.datetime(1970,1,1)+datetime.timedelta(milliseconds=int(x["t"]))).date()
        g[d] = float(x["c"])
    G = sorted(g.items()); out = {}
    for i in range(len(G)):
        hafta = {}
        for d, c in G[:i+1]:
            hafta[d.isocalendar()[:2]] = (d, c)
        wc = [c for k, (d, c) in sorted(hafta.items())]
        if len(wc) < 21:
            continue
        wo = statistics.mean(wc[-21:-1])
        sezon = ("BOGA" if (wc[-1] > wo and wc[-1]-wc[-21] > 0)
                 else ("AYI" if (wc[-1] < wo and wc[-1]-wc[-21] < 0) else "NOTR"))
        cl = [c for d, c in G[max(0, i-59):i+1]]
        ham = []
        for j in range(20, len(cl)):
            sma = statistics.mean(cl[j-20:j])
            uz = (cl[j]-sma)/sma*100
            ham.append("NOTR" if abs(uz) < 2.0 else ("BOGA" if uz > 0 else "AYI"))
        hava = ham[0] if ham else "NOTR"
        for j in range(len(ham)):
            if j < 3:
                hava = ham[j]
            else:
                pen = ham[j-2:j+1]
                if all(x == pen[0] for x in pen):
                    hava = pen[0]
        if sezon == "AYI" and hava == "BOGA":    f10 = "TEPKI_RALLISI"
        elif sezon == "BOGA" and hava == "BOGA": f10 = "TAM_BOGA"
        elif sezon == "AYI" and hava == "AYI":   f10 = "DERIN_AYI"
        elif sezon == "BOGA" and hava == "AYI":  f10 = "BOGA_DUZELTME"
        else:                                    f10 = "BELIRSIZ"
        out[G[i][0].isoformat()] = ("BOGA" if f10 == "TAM_BOGA"
                                    else ("AYI" if f10 in ("TEPKI_RALLISI","DERIN_AYI")
                                          else "NOTR"))
    return out


def _sayi(ad, v):
    """mcap BICIMLENMIS METIN gelir ('$1082M') -> milyon USD float.
    Bulundu 2026-08-27: onceki doluluk kontrolu 'None degil' diye sayinca
    metinleri DOLU gordu ve float() sessizce None yazdi. DOLULUK != KULLANILABILIRLIK."""
    if v is None:
        return None
    if ad == "mcap" and isinstance(v, str):
        t = v.strip().replace("$", "").replace(",", "")
        kat = 1.0
        if t.endswith("B"):
            kat, t = 1000.0, t[:-1]
        elif t.endswith("M"):
            kat, t = 1.0, t[:-1]
        elif t.endswith("K"):
            kat, t = 0.001, t[:-1]
        return float(t) * kat            # birim: MILYON USD
    return float(v)


RJ = rejim_serisi()
print("rejim YENIDEN URETILDI: %d gun  %s"
      % (len(RJ), dict(collections.Counter(RJ.values()))))

# --- bosluk denetimi (CLAUDE.md: arsiv NOKTASAL) ---
bp = os.path.join(PROJE, "radar_bosluk.jsonl")
nb = sum(1 for l in open(bp, encoding="utf-8") if l.strip()) if os.path.exists(bp) else 0
print("radar_bosluk.jsonl kayit: %d" % nb)

# --- arsiv: saatlik tekillestirme ---
gor, ham = {}, 0
for l in open(os.path.join(PROJE, "radar_archive.jsonl"), encoding="utf-8"):
    l = l.strip()
    if not l:
        continue
    ham += 1
    try:
        x = json.loads(l)
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
    if k in gor:
        continue
    r = {"sym": sym, "yerel": t, "gun": t.strftime("%Y-%m-%d"),
         "skor_bot": float(x.get("score") or 0)}     # UST-VERI: ozellik DEGIL
    for a in SAYISAL:
        v = x.get(a)
        try:
            r[a] = _sayi(a, v)
        except Exception:
            r[a] = None
    for a in KATEGORIK:
        if a == "rejim_yeni":
            continue
        v = x.get(a)
        r[a] = None if v is None else str(v)
    r["rejim_yeni"] = RJ.get(r["gun"])
    gor[k] = r
print("ham satir %d  ->  (sembol,saat) tekil %d" % (ham, len(gor)))

# --- etiket: HAM +2s, ve ATR (D3 icin) ---
gerek = collections.defaultdict(list)
for r in gor.values():
    gerek[r["sym"]].append(r)
satir, eksik_s, eksik_b = [], 0, 0
for n, (sym, rs) in enumerate(sorted(gerek.items())):
    p = os.path.join(KL, sym + ".json")
    if not os.path.exists(p):
        eksik_s += 1
        continue
    try:
        b = json.load(open(p, encoding="utf-8"))
    except Exception:
        eksik_s += 1
        continue
    idx, c, hi, lo = {}, [], [], []
    for i, z in enumerate(b):
        idx[datetime.datetime(1970,1,1)+datetime.timedelta(milliseconds=int(z["t"]))] = i
        c.append(float(z["c"])); hi.append(float(z["h"])); lo.append(float(z["l"]))
    for r in rs:
        i = idx.get(r["yerel"] + datetime.timedelta(hours=OFSET))
        if i is None:
            eksik_b += 1
            continue
        g = i + 1
        if g < 15 or g + UFUK >= len(c) or c[g] <= 0:
            eksik_b += 1
            continue
        tr = [max(hi[k]-lo[k], abs(hi[k]-c[k-1]), abs(lo[k]-c[k-1]))
              for k in range(g-13, g+1)]
        r = dict(r)
        r["atr_pct"] = 100.0 * (sum(tr)/len(tr)) / c[g]      # D3 karistiricisi
        r["y"] = 100.0 * (c[g + UFUK] / c[g] - 1.0)          # HAM +2s
        r["saat"] = r["yerel"].strftime("%Y-%m-%d %H")
        r.pop("yerel")
        satir.append(r)
    if (n + 1) % 100 == 0:
        print("   ... %d/%d sembol (satir %d)" % (n+1, len(gerek), len(satir)), flush=True)

print("\nkullanilabilir %d  ·  klines'i yok %d sembol  ·  bar eslesmeyen %d"
      % (len(satir), eksik_s, eksik_b))

say = collections.Counter(r["gun"] for r in satir)
GUN = sorted(g for g in say if say[g] >= 100)
TEST = GUN[7:]
print("gun (>=100 gozlem) %d  ·  TEST GUNU %d  (%s .. %s)"
      % (len(GUN), len(TEST), TEST[0], TEST[-1]))
print("gun basi gozlem: medyan %d" % statistics.median(say[g] for g in GUN))
rj = collections.Counter(r["rejim_yeni"] for r in satir if r["gun"] in GUN)
print("rejim dagilimi (gozlem): %s" % dict(rj))
y = [r["y"] for r in satir]
print("etiket +%ds: ort %+.4f%% · medyan %+.4f%% · std %.3f" % (UFUK,
      statistics.mean(y), statistics.median(y), statistics.pstdev(y)))
print("skor (UST-VERI): medyan %.1f · %%10 %.1f · %%90 %.1f"
      % (statistics.median(r["skor_bot"] for r in satir),
         sorted(r["skor_bot"] for r in satir)[len(satir)//10],
         sorted(r["skor_bot"] for r in satir)[9*len(satir)//10]))
print("\ngirdi alani doluluk:")
for a in SAYISAL + KATEGORIK:
    d = sum(1 for r in satir if r.get(a) is not None)
    print("   %-14s %%%.1f" % (a, 100.0*d/len(satir)))

json.dump({"sayisal": SAYISAL, "kategorik": KATEGORIK, "ufuk": UFUK,
           "test_gun": TEST, "gun": GUN, "bosluk": nb, "satir": satir},
          open(os.path.join(HERE, "kutu_disi_veri.json"), "w"))
print("\nYAZILDI -> kutu_disi_veri.json (%.0f MB)"
      % (os.path.getsize(os.path.join(HERE, "kutu_disi_veri.json"))/1048576))
