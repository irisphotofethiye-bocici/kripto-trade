#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UC DEFTER + ADAY ARSIVI BIRLESTIRME. SALT OKUMA.
Pozisyonlar (sym, giris ani) ile arsive baglanir; eslesme orani RAPORLANIR."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections, datetime as dt, bisect, pickle, os

HERE = os.path.dirname(os.path.abspath(__file__))
TOL_SN = 900          # +-15 dk: aday arsivi tur basi yazilir (7,5 dk cadence)


def _ts(s):
    """Defter saniyeli, arsiv DAKIKA hassasiyetinde — ikisini de kabul et."""
    s = str(s).strip().replace("T", " ")
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return dt.datetime.strptime(s[:19 if len(f) > 16 else 16], f)
        except ValueError:
            pass
    raise ValueError("cozulemeyen ts: %r" % s)


def pozisyonlar(f):
    """id -> (pnl, kapanis kaydi, giris ani, TP1 aldi mi)"""
    K = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    g = {}
    for r in K:
        t = _ts(r["ts"]) - dt.timedelta(hours=float(r.get("tutma_saat") or 0))
        if r["id"] not in g or t < g[r["id"]]:
            g[r["id"]] = t
    pnl, meta, tp1, fnd = collections.defaultdict(float), {}, set(), collections.defaultdict(float)
    for r in K:
        pnl[r["id"]] += float(r.get("sonuc_usdt") or 0)
        if r.get("funding_usdt") is not None:
            fnd[r["id"]] += float(r["funding_usdt"])
        if r.get("sebep") == "TP1_KISMI":
            tp1.add(r["id"])
        if not r.get("kismi"):
            meta[r["id"]] = r
    return [{"pnl": pnl[i], "fnd": fnd.get(i, 0.0), "k": meta[i], "gts": g[i],
             "tp1": i in tp1} for i in meta]


# --- aday arsivi: sym -> sirali (ts, kayit) ---
print("aday arsivi okunuyor...", flush=True)
ARS = collections.defaultdict(list)
for l in open("testbot_aday_arsiv.jsonl", encoding="utf-8"):
    l = l.strip()
    if not l:
        continue
    d = json.loads(l)
    if d.get("sym") and d.get("ts"):
        try:
            t = _ts(d["ts"])          # ONCE cozumle: hata bos anahtar YARATMASIN
        except Exception:
            continue
        ARS[d["sym"]].append((t, d))
for s in ARS:
    ARS[s].sort(key=lambda x: x[0])
print("  %d sembol · %d kayit" % (len(ARS), sum(len(v) for v in ARS.values())))


def arsivden(sym, t):
    """t'ye en yakin arsiv kaydi (TOL_SN icinde)."""
    v = ARS.get(sym)
    if not v:
        return None
    i = bisect.bisect_left([x[0] for x in v], t)
    en, ed = None, None
    for j in (i - 1, i, i + 1):
        if 0 <= j < len(v):
            d = abs((v[j][0] - t).total_seconds())
            if ed is None or d < ed:
                en, ed = v[j][1], d
    return en if (ed is not None and ed <= TOL_SN) else None


OUT = {}
print("")
print("=" * 88)
print("ESLESME ORANI — pozisyon -> aday arsivi (+-%d dk)" % (TOL_SN // 60))
print("=" * 88)
for ad, f in (("golge", "golge_islemler.jsonl"),
              ("defter2", "defter2_islemler.jsonl"),
              ("defter3", "defter3_islemler.jsonl")):
    P = pozisyonlar(f)
    n = 0
    for p in P:
        a = arsivden(p["k"]["sym"], p["gts"])
        p["ars"] = a
        if a:
            n += 1
    OUT[ad] = P
    print("  %-8s %4d pozisyon · eslesen %4d (%%%.1f)" % (ad, len(P), n, 100 * n / len(P)))

pickle.dump(OUT, open(os.path.join(HERE, "uc_defter.pkl"), "wb"))
print("")
print("kaydedildi: scratchpad/uc_defter.pkl")
