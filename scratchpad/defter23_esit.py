#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESIT ZEMIN: sadece ORTUSEN pencerede ACILAN pozisyonlar. SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections, datetime as dt, statistics as stt

T0 = "2026-08-25 16:12:12"


def oku(a):
    return [json.loads(l) for l in open(a, encoding="utf-8") if l.strip()]


def gts(K):
    g = {}
    for r in K:
        t = dt.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S") \
            - dt.timedelta(hours=float(r.get("tutma_saat") or 0))
        if r["id"] not in g or t < g[r["id"]]:
            g[r["id"]] = t
    return g


print("=" * 94)
print("A) EQUITY FARKI NEDEN YANILTIYOR — defter2 ACIK POZISYON DEVRALDI")
print("=" * 94)
for ad, f, sf in (("defter2", "defter2_islemler.jsonl", "defter2_state.json"),
                  ("defter3", "defter3_islemler.jsonl", "defter3_state.json")):
    K = oku(f); G = gts(K)
    dev = {i for i, t in G.items()
           if t.strftime("%Y-%m-%d %H:%M:%S") < T0
           and max(r["ts"] for r in K if r["id"] == i) >= T0}
    p = sum(float(r.get("sonuc_usdt") or 0) for r in K if r["id"] in dev)
    print("  %-8s pencere basinda ACIK devralinan: %2d poz  ->  P&L %+8.2f" % (ad, len(dev), p))

print("")
print("=" * 94)
print("B) ESIT ZEMIN — YALNIZ pencerede ACILAN pozisyonlar")
print("=" * 94)
R = {}
for ad, f in (("defter2", "defter2_islemler.jsonl"), ("defter3", "defter3_islemler.jsonl")):
    K = oku(f); G = gts(K)
    pnl, fnd, meta = collections.defaultdict(float), collections.defaultdict(float), {}
    for r in K:
        if G[r["id"]].strftime("%Y-%m-%d %H:%M:%S") < T0:
            continue
        pnl[r["id"]] += float(r.get("sonuc_usdt") or 0)
        fnd[r["id"]] += float(r.get("funding_usdt") or 0)
        if not r.get("kismi"):
            meta[r["id"]] = r
    R[ad] = (pnl, meta)
    v = list(pnl.values())
    kz = sum(1 for x in v if x > 0)
    mar = [float(meta[i]["marjin"]) for i in meta]
    print("  %-8s %2d poz  P&L %+8.2f  fonlama %+6.2f  kazanma %%%.0f  medyan marjin %6.1f"
          % (ad, len(meta), sum(v), sum(fnd.values()), 100.0 * kz / max(len(v), 1),
             stt.median(mar)))
print("")
print("  -> FARK (D3 - D2): %+.2f $" % (sum(R["defter3"][0].values()) - sum(R["defter2"][0].values())))

print("")
print("=" * 94)
print("C) DEFTER3'UN KENDI ICINDE — LONG kolu SHORT kolunu ne kadar yiyor")
print("=" * 94)
pnl, meta = R["defter3"]
for y in ("SHORT", "LONG"):
    ids = [i for i, m in meta.items() if m["yon"] == y]
    v = [pnl[i] for i in ids]
    kz = sum(1 for x in v if x > 0)
    print("  %-6s %2d poz  P&L %+8.2f  kazanma %%%.0f" % (y, len(ids), sum(v), 100.0 * kz / max(len(v), 1)))
print("  -> LONG kolu olmasaydi defter3: %+.2f  (gercek: %+.2f)"
      % (sum(pnl[i] for i, m in meta.items() if m["yon"] == "SHORT"), sum(pnl.values())))

print("")
print("=" * 94)
print("D) REJIM — bu pencere gercekten BOGA mi (giristeki etiket)")
print("=" * 94)
for ad in ("defter2", "defter3"):
    pnl, meta = R[ad]
    c = collections.Counter(str(m.get("rejim_giriste")) for m in meta.values())
    print("  %-8s %s" % (ad, dict(c)))

print("")
print("=" * 94)
print("E) SURE — kac gunluk veriyle konusuyoruz")
print("=" * 94)
n = dt.datetime.now()
for ad, sf in (("defter2", "defter2_state.json"), ("defter3", "defter3_state.json")):
    b = json.load(open(sf, encoding="utf-8"))["baslangic_ts"]
    print("  %-8s omur %.1f gun" % (ad, (n - dt.datetime.strptime(b, "%Y-%m-%d %H:%M:%S")).total_seconds() / 86400))
print("  ortusen pencere: %.1f gun" % ((n - dt.datetime.strptime(T0, "%Y-%m-%d %H:%M:%S")).total_seconds() / 86400))
