#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Boyut kiyaslanabilirligi + tepe sonrasi dilim + acik poz. SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections, datetime as dt, statistics as st

T0, TP = "2026-08-19 00:00:00", "2026-08-22 12:00:00"


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


print("=" * 96)
print("1) BOYUT KIYASLANABILIR MI — pencerede acilan pozisyonlar")
print("=" * 96)
D = {}
for ad, f in (("testbot", "testbot_islemler.jsonl"), ("golge", "golge_islemler.jsonl")):
    K = oku(f)
    G = gts(K)
    D[ad] = (K, G)
    m = [r for r in K if not r.get("kismi")
         and G[r["id"]].strftime("%Y-%m-%d %H:%M:%S") >= T0]
    mar = [float(r["marjin"]) for r in m]
    not_ = [float(r["notional"]) for r in m]
    kal = [float(r["kaldirac"]) for r in m]
    tut = [float(r.get("tutma_saat") or 0) for r in m]
    print("  %-8s N=%3d  marjin ort %7.1f medyan %7.1f | notional ort %8.1f | kaldirac medyan %.0f | tutma medyan %.1f sa"
          % (ad, len(m), st.mean(mar), st.median(mar), st.mean(not_), st.median(kal), st.median(tut)))

print("")
print("=" * 96)
print("2) TEPE SONRASI — golge 08-22'de zirve yapti, o gunden bu yana ne oldu")
print("=" * 96)


def dilim(ad, f, ef, sf, t_bas, t_son=None):
    K, G = D[ad]
    e = oku(ef)
    e0 = [r for r in e if r["ts"] < t_bas][-1]
    e1 = ([r for r in e if r["ts"] < t_son][-1] if t_son
          else {"equity": json.load(open(sf, encoding="utf-8"))["equity"], "ts": "simdi"})
    pen = {i for i, t in G.items()
           if t_bas <= t.strftime("%Y-%m-%d %H:%M:%S") and (t_son is None or t.strftime("%Y-%m-%d %H:%M:%S") < t_son)}
    pnl = collections.defaultdict(float)
    for r in K:
        if r["id"] in pen:
            pnl[r["id"]] += float(r.get("sonuc_usdt") or 0)
    kz = sum(1 for v in pnl.values() if v > 0)
    return (e1["equity"] - e0["equity"], e0["equity"], len(pnl), kz,
            100.0 * kz / max(len(pnl), 1))


for ad, ef, sf in (("testbot", "testbot_equity.jsonl", "testbot_state.json"),
                   ("golge", "golge_equity.jsonl", "golge_state.json")):
    a = dilim(ad, None, ef, sf, T0, TP)
    b = dilim(ad, None, ef, sf, TP, None)
    print("  %-8s  08-19..08-22 : %+9.2f (%%%+6.1f)  %3d poz  kazanma %%%.0f"
          % (ad, a[0], 100.0 * a[0] / a[1], a[2], a[4]))
    print("  %-8s  08-22..SIMDI : %+9.2f (%%%+6.1f)  %3d poz  kazanma %%%.0f"
          % ("", b[0], 100.0 * b[0] / b[1], b[2], b[4]))

print("")
print("=" * 96)
print("3) YUZDE — sermaye tabanlari farkli, oran olarak")
print("=" * 96)
for ad, ef, sf in (("testbot", "testbot_equity.jsonl", "testbot_state.json"),
                   ("golge", "golge_equity.jsonl", "golge_state.json")):
    e = oku(ef)
    e0 = [r for r in e if r["ts"] < T0][-1]["equity"]
    pen = [r["equity"] for r in e if r["ts"] >= T0]
    now = json.load(open(sf, encoding="utf-8"))["equity"]
    zirve = max(pen)
    print("  %-8s taban %8.2f  zirve %8.2f (%%%+.1f)  simdi %8.2f (%%%+.1f)  zirveden geri %%%.1f"
          % (ad, e0, zirve, 100.0 * (zirve - e0) / e0, now, 100.0 * (now - e0) / e0,
             100.0 * (zirve - now) / max(zirve - e0, 1e-9)))

print("")
print("=" * 96)
print("4) SU AN ACIK OLANLAR")
print("=" * 96)
for ad, sf in (("testbot", "testbot_state.json"), ("golge", "golge_state.json")):
    s = json.load(open(sf, encoding="utf-8"))
    print("  %-8s durum=%s" % (ad, s.get("durum")))
    for p in s.get("acik_pozisyonlar", []):
        print("     %-8s %-5s giris %s  marjin %.0f  kaynak %s"
              % (p.get("sym"), p.get("yon"), p.get("giris_ts"), p.get("marjin", 0),
                 p.get("kaynak", "-")))
