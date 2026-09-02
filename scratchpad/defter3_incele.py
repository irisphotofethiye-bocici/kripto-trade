#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEFTER3 DERIN INCELEME. SALT OKUMA.
Kontroller: gun-kumeli t · TP1 KONTROL KATMANI (65043f6) · eslesmis isim kiyasi."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections, math, datetime as dt, statistics as stt

T0 = "2026-08-25 16:12:12"


def oku(a):
    return [json.loads(l) for l in open(a, encoding="utf-8") if l.strip()]


def poz(f, t0=T0):
    """id -> pnl (kismi DAHIL, id ile birlestirilir) + kapanis kaydi."""
    K = oku(f)
    g = {}
    for r in K:
        t = dt.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S") \
            - dt.timedelta(hours=float(r.get("tutma_saat") or 0))
        if r["id"] not in g or t < g[r["id"]]:
            g[r["id"]] = t
    pnl, meta, tp1 = collections.defaultdict(float), {}, set()
    for r in K:
        if g[r["id"]].strftime("%Y-%m-%d %H:%M:%S") < t0:
            continue
        pnl[r["id"]] += float(r.get("sonuc_usdt") or 0)
        if r.get("sebep") == "TP1_KISMI":
            tp1.add(r["id"])
        if not r.get("kismi"):
            meta[r["id"]] = dict(r, _gun=g[r["id"]].strftime("%Y-%m-%d"))
    return {i: (pnl[i], meta[i], i in tp1) for i in meta}


def t_gun(kayit):
    """GUN-KUMELI t: her gunun toplami bir gozlem."""
    g = collections.defaultdict(float)
    for p, m, _ in kayit:
        g[m["_gun"]] += p
    v = list(g.values())
    if len(v) < 3:
        return None, None, len(v)
    sd = stt.stdev(v)
    m_ = stt.mean(v)
    return m_, (m_ / (sd / math.sqrt(len(v))) if sd > 0 else None), len(v)


D3 = poz("defter3_islemler.jsonl")
D2 = poz("defter2_islemler.jsonl")

print("=" * 100)
print("1) DEFTER3 — IKI KOL, GUN-KUMELI ISTATISTIK")
print("=" * 100)
kol = {"SHORT": [], "LONG": []}
for i, (p, m, t) in D3.items():
    kol[m["yon"]].append((p, m, t))
for y in ("SHORT", "LONG"):
    v = [x[0] for x in kol[y]]
    kz = sum(1 for x in v if x > 0)
    mm, tt, ng = t_gun(kol[y])
    print("  %-6s %3d poz  toplam %+9.2f  ort %+7.2f  kazanma %%%.0f"
          % (y, len(v), sum(v), stt.mean(v), 100 * kz / len(v)))
    print("         gun-kumeli: %d gun · gun ort %+8.2f · t=%s"
          % (ng, mm, ("%+.2f" % tt) if tt else "—"))

print("")
print("=" * 100)
print("2) 🔴 TP1 KONTROL KATMANI (65043f6 kurali) — TP1 sabitlenince kol farki KALIYOR mu")
print("=" * 100)
for tp in (True, False):
    print("  --- TP1 %s ---" % ("ALINDI" if tp else "ALINMADI"))
    for y in ("SHORT", "LONG"):
        s = [x for x in kol[y] if x[2] == tp]
        if not s:
            continue
        v = [x[0] for x in s]
        mm, tt, ng = t_gun(s)
        print("     %-6s %3d poz  toplam %+9.2f  ort %+7.2f  kazanma %%%.0f  gun-t %s"
              % (y, len(v), sum(v), stt.mean(v),
                 100 * sum(1 for x in v if x > 0) / len(v),
                 ("%+.2f" % tt) if tt else "—"))
    print("")
print("  TP1 ORANI:  SHORT %%%.0f  ·  LONG %%%.0f"
      % (100 * sum(1 for x in kol["SHORT"] if x[2]) / len(kol["SHORT"]),
         100 * sum(1 for x in kol["LONG"] if x[2]) / len(kol["LONG"])))

print("")
print("=" * 100)
print("3) LONG KAYBI YOGUN MU YAYGIN MI")
print("=" * 100)
lv = sorted(x[0] for x in kol["LONG"])
top = sum(lv)
print("  N=%d  toplam %+.2f  medyan %+.2f" % (len(lv), top, stt.median(lv)))
for k in (1, 3, 5):
    print("     en kotu %d pozisyon: %+9.2f  (toplamin %%%.0f'i)"
          % (k, sum(lv[:k]), 100 * sum(lv[:k]) / top))
print("  eksi kapanan: %d/%d" % (sum(1 for x in lv if x <= 0), len(lv)))

print("")
print("=" * 100)
print("4) ESLESMIS ISIM — ayni sembol, D2 SHORT vs D3 LONG (TEK YON FARKI)")
print("=" * 100)
s2 = {}
for i, (p, m, t) in D2.items():
    s2.setdefault((m["sym"], m["_gun"]), []).append((p, m))
n, fark = 0, 0.0
print("  %-10s %-6s %10s   %-6s %10s   %8s" % ("sym", "D2", "D2 P&L", "D3", "D3 P&L", "chg24"))
for i, (p3, m3, t3) in sorted(D3.items(), key=lambda x: x[1][1]["_gun"]):
    if m3["yon"] != "LONG":
        continue
    k = (m3["sym"], m3["_gun"])
    if k not in s2:
        continue
    p2, m2 = s2[k][0]
    if m2["yon"] == "LONG":
        continue
    n += 1
    fark += p3 - p2
    print("  %-10s %-6s %+10.2f   %-6s %+10.2f   %+8.1f"
          % (m3["sym"], m2["yon"], p2, m3["yon"], p3, float(m3.get("chg24_giriste") or 0)))
print("  -> %d eslesmis cift · D3(LONG) - D2(SHORT) toplam farki: %+.2f" % (n, fark))

print("")
print("=" * 100)
print("5) chg24 DERINLIGI — daha cok dusen daha mi kotu")
print("=" * 100)
b = collections.defaultdict(list)
for p, m, t in kol["LONG"]:
    c = float(m.get("chg24_giriste") or 0)
    k = "-5..0" if c > -5 else ("-10..-5" if c > -10 else ("-20..-10" if c > -20 else "<-20"))
    b[k].append(p)
for k in ("-5..0", "-10..-5", "-20..-10", "<-20"):
    if k in b:
        v = b[k]
        print("  chg24 %-9s %3d poz  toplam %+9.2f  ort %+7.2f  kazanma %%%.0f"
              % (k, len(v), sum(v), stt.mean(v), 100 * sum(1 for x in v if x > 0) / len(v)))

print("")
print("=" * 100)
print("6) ODEME GEOMETRISI — kol basina")
print("=" * 100)
for y in ("SHORT", "LONG"):
    v = [x[0] for x in kol[y]]
    kz = [x for x in v if x > 0]
    kb = [-x for x in v if x <= 0]
    if kz and kb:
        ak, az = stt.mean(kz), stt.mean(kb)
        print("  %-6s ort KAZANC %+7.2f · ort KAYIP -%6.2f · oran %.2f · kazanma %%%.1f · basabas gereken %%%.1f"
              % (y, ak, az, ak / az, 100 * len(kz) / len(v), 100 * az / (ak + az)))
