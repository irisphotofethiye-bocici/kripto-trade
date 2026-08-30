#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ODEME GEOMETRISI — kazanma orani degil, kazanc/kayip BUYUKLUGU.
Pozisyon bazli: kayitlar id ile birlestirilir (CLAUDE.md). SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections, statistics as stt

DEF = (("testbot", "testbot_islemler.jsonl"),
       ("golge", "golge_islemler.jsonl"),
       ("defter2", "defter2_islemler.jsonl"),
       ("defter3", "defter3_islemler.jsonl"))


def poz(f):
    """id -> {pnl, tp1_var, son_sebep, marjin, risk}"""
    d = collections.defaultdict(lambda: {"pnl": 0.0, "tp1": False, "sebep": None,
                                         "marjin": None, "kayit": 0})
    for l in open(f, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        r = json.loads(l)
        p = d[r["id"]]
        p["pnl"] += float(r.get("sonuc_usdt") or 0)
        p["kayit"] += 1
        if r.get("sebep") == "TP1_KISMI":
            p["tp1"] = True
        if not r.get("kismi"):
            p["sebep"] = r.get("sebep")
            p["marjin"] = float(r.get("marjin") or 0) * 2 if r.get("kismi") else float(r.get("marjin") or 0)
    return {i: v for i, v in d.items() if v["sebep"]}      # yalniz KAPANMIS


print("=" * 100)
print("1) BEKLENTI AYRISTIRMASI — kazanma orani yeterli mi")
print("=" * 100)
print("  %-9s %5s %7s %11s %11s %8s %11s" %
      ("defter", "poz", "kazanma", "ort KAZANC", "ort KAYIP", "oran", "beklenti/poz"))
P = {}
for ad, f in DEF:
    p = poz(f)
    P[ad] = p
    v = [x["pnl"] for x in p.values()]
    k = [x for x in v if x > 0]
    z = [-x for x in v if x <= 0]
    if not k or not z:
        continue
    pw = len(k) / len(v)
    ak, az = stt.mean(k), stt.mean(z)
    bek = pw * ak - (1 - pw) * az
    print("  %-9s %5d  %5.1f%% %+11.2f %-11s %8.2f %+11.2f" %
          (ad, len(v), 100 * pw, ak, "-%.2f" % az, ak / az, bek))

print("")
print("  -> BASABAS icin gereken kazanma orani = kayip/(kazanc+kayip)")
for ad in P:
    v = [x["pnl"] for x in P[ad].values()]
    k = [x for x in v if x > 0]
    z = [-x for x in v if x <= 0]
    if not k or not z:
        continue
    ak, az = stt.mean(k), stt.mean(z)
    ger = az / (ak + az)
    var = len(k) / len(v)
    print("     %-9s gereken %%%.1f  ·  gercek %%%.1f  ·  ACIK %+.1f puan"
          % (ad, 100 * ger, 100 * var, 100 * (var - ger)))

print("")
print("=" * 100)
print("2) TP1 KISMI KAR — yarisini erken almak ne yapiyor")
print("=" * 100)
for ad in P:
    p = P[ad]
    grp = collections.defaultdict(list)
    for x in p.values():
        grp["TP1 ALDI" if x["tp1"] else "TP1 YOK"].append(x["pnl"])
    print("  --- %s ---" % ad)
    for g in ("TP1 ALDI", "TP1 YOK"):
        v = grp.get(g, [])
        if not v:
            continue
        kz = sum(1 for x in v if x > 0)
        print("     %-9s %4d poz  toplam %+9.2f  ort %+7.2f  kazanma %%%.0f"
              % (g, len(v), sum(v), stt.mean(v), 100 * kz / len(v)))
    # TP1 aldi AMA yine de eksi kapandi
    hain = [x["pnl"] for x in p.values() if x["tp1"] and x["pnl"] <= 0]
    tp1 = [x["pnl"] for x in p.values() if x["tp1"]]
    if tp1:
        print("     TP1 alip yine de EKSI kapanan: %d/%d (%%%.0f)  toplam %+9.2f"
              % (len(hain), len(tp1), 100 * len(hain) / len(tp1), sum(hain)))
    print("")

print("=" * 100)
print("3) KAPANIS SEBEBI — para nereden giriyor, nereden cikiyor")
print("=" * 100)
for ad in P:
    p = P[ad]
    g = collections.defaultdict(lambda: [0, 0.0])
    for x in p.values():
        g[x["sebep"]][0] += 1
        g[x["sebep"]][1] += x["pnl"]
    tot = sum(v[1] for v in g.values())
    print("  --- %s (toplam %+.2f) ---" % (ad, tot))
    for s, v in sorted(g.items(), key=lambda x: x[1][1]):
        print("     %-12s %4d poz (%%%4.1f)  %+9.2f   ort %+7.2f"
              % (s, v[0], 100 * v[0] / len(p), v[1], v[1] / v[0]))
    print("")
