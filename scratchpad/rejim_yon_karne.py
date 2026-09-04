#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REJIM x YON KARNESI — "iki rejim var, SHORT ayagi basariliydi" iddiasinin sinanmasi.

Kullanici notu (2026-09-04): 11-19 Agustos NOTR/AYI rejimiydi ve NOTR-SHORT'ta
bot buyuk oranda artida kaliyordu -> olcumde IKI REJIM var.

Bu betik iddiayi CANLI DEFTERDEN sinar. CLAUDE.md kurallari aynen:
  - birim POZISYON (id ile birlestirme)
  - P&L toplarken `kismi` SUZULMEZ
  - net = sonuc_usdt + funding_usdt
  - rejim = `rejim_giriste` (GIRIS anindaki rejim, cikis degil)
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, math, statistics, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFTER = os.path.join(PROJE, "testbot_islemler.jsonl")


def t_ist(v):
    if len(v) < 3:
        return (sum(v) / len(v) if v else 0.0), None, len(v)
    m, sd = sum(v) / len(v), statistics.stdev(v)
    se = sd / math.sqrt(len(v))
    return m, (m / se if se else None), len(v)


def main():
    ham = collections.defaultdict(list)
    for l in open(DEFTER, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r.get("id") is not None:
            ham[r["id"]].append(r)

    poz = []
    for i, v in ham.items():
        v.sort(key=lambda z: z["ts"])
        ilk, son = v[0], v[-1]
        no = ilk.get("notional") or 0
        if no <= 0:
            continue
        brut = sum((t.get("sonuc_usdt") or 0) for t in v)
        fl = [t.get("funding_usdt") for t in v if t.get("funding_usdt") is not None]
        net = brut + (sum(fl) if fl else 0.0)
        tut = max((t.get("tutma_saat") or 0) for t in v)
        poz.append({
            "id": i, "sym": son["sym"], "yon": son["yon"],
            "rejim": str(ilk.get("rejim_giriste") or "?"),
            "kapi": str(ilk.get("sebep_giris") or "?").split(":")[0].strip()[:14],
            "net": net, "ret": 100.0 * net / no,
            "gun": son["ts"][:10], "giris_gun": None,
            "sebep": son.get("sebep"), "tut": tut, "ts": son["ts"],
        })
    # giris gunu = kapanis - tutma
    import datetime
    for p in poz:
        try:
            k = datetime.datetime.strptime(p["ts"], "%Y-%m-%d %H:%M:%S")
            p["giris_gun"] = (k - datetime.timedelta(hours=p["tut"])).date().isoformat()
        except Exception:
            p["giris_gun"] = p["gun"]

    print("REJIM x YON KARNESI — canli defter, POZISYON bazinda")
    print("=" * 104)
    print("pozisyon %d · kapsam %s .. %s"
          % (len(poz), min(p["giris_gun"] for p in poz), max(p["giris_gun"] for p in poz)))

    # ---------------------------------------------------------------- rejim x yon
    print("\n1) REJIM (giriste) x YON")
    print("-" * 104)
    print("  %-14s %-6s %5s %10s %10s %9s %9s %8s"
          % ("rejim", "yon", "N", "NET $", "$/poz", "kazanan", "ort ret%", "poz-t"))
    g = collections.defaultdict(list)
    for p in poz:
        g[(p["rejim"], p["yon"])].append(p)
    for k in sorted(g, key=lambda z: (z[0], z[1])):
        w = g[k]
        m, t, n = t_ist([p["ret"] for p in w])
        print("  %-14s %-6s %5d %+9.2f %+9.2f %8.0f%% %+8.3f%% %8s"
              % (k[0], k[1], len(w), sum(p["net"] for p in w),
                 sum(p["net"] for p in w) / len(w),
                 100.0 * sum(1 for p in w if p["net"] > 0) / len(w), m,
                 ("%+.2f" % t) if t else "-"))

    # ---------------------------------------------------------------- rejim ozeti
    print("\n2) REJIM OZETI")
    print("-" * 104)
    print("  %-14s %5s %10s %10s %9s %8s %8s"
          % ("rejim", "N", "NET $", "$/poz", "kazanan", "SHORT%", "ilk gun"))
    gr = collections.defaultdict(list)
    for p in poz:
        gr[p["rejim"]].append(p)
    for k in sorted(gr, key=lambda z: -sum(p["net"] for p in gr[z])):
        w = gr[k]
        print("  %-14s %5d %+9.2f %+9.2f %8.0f%% %7.0f%% %8s"
              % (k, len(w), sum(p["net"] for p in w), sum(p["net"] for p in w) / len(w),
                 100.0 * sum(1 for p in w if p["net"] > 0) / len(w),
                 100.0 * sum(1 for p in w if p["yon"] == "SHORT") / len(w),
                 min(p["giris_gun"] for p in w)))

    # ---------------------------------------------------------------- yon ozeti
    print("\n3) YON OZETI — rejimden bagimsiz")
    print("-" * 104)
    print("  %-6s %5s %10s %10s %9s %9s %8s"
          % ("yon", "N", "NET $", "$/poz", "kazanan", "ort ret%", "poz-t"))
    for y in ("SHORT", "LONG"):
        w = [p for p in poz if p["yon"] == y]
        if not w:
            continue
        m, t, n = t_ist([p["ret"] for p in w])
        print("  %-6s %5d %+9.2f %+9.2f %8.0f%% %+8.3f%% %8s"
              % (y, len(w), sum(p["net"] for p in w), sum(p["net"] for p in w) / len(w),
                 100.0 * sum(1 for p in w if p["net"] > 0) / len(w), m,
                 ("%+.2f" % t) if t else "-"))

    # ---------------------------------------------------------------- zaman dilimi
    print("\n4) ZAMAN DILIMI — kullanicinin isaret ettigi 11-19 Agustos vs sonrasi")
    print("-" * 104)
    dilim = [("... 08-10", lambda d: d <= "2026-08-10"),
             ("08-11..08-19", lambda d: "2026-08-11" <= d <= "2026-08-19"),
             ("08-20..08-23", lambda d: "2026-08-20" <= d <= "2026-08-23"),
             ("08-24 ...", lambda d: d >= "2026-08-24")]
    print("  %-14s %5s %10s %9s %8s %9s %9s"
          % ("dilim", "N", "NET $", "kazanan", "SHORT%", "SHORT $", "LONG $"))
    for ad, f in dilim:
        w = [p for p in poz if f(p["giris_gun"])]
        if not w:
            continue
        s = [p for p in w if p["yon"] == "SHORT"]
        lo = [p for p in w if p["yon"] == "LONG"]
        print("  %-14s %5d %+9.2f %8.0f%% %7.0f%% %+8.2f %+8.2f"
              % (ad, len(w), sum(p["net"] for p in w),
                 100.0 * sum(1 for p in w if p["net"] > 0) / len(w),
                 100.0 * len(s) / len(w),
                 sum(p["net"] for p in s), sum(p["net"] for p in lo)))

    # -------------------------------------------------- NOTR-SHORT ayrintisi
    print("\n5) 🔑 NOTR-SHORT — kullanicinin iddiasinin tam yeri")
    print("-" * 104)
    w = [p for p in poz if p["rejim"].startswith("NOTR") and p["yon"] == "SHORT"]
    if w:
        m, t, n = t_ist([p["ret"] for p in w])
        kaz = sum(1 for p in w if p["net"] > 0)
        print("  N=%d · NET %+.2f · $/poz %+.2f · kazanan %%%.0f · ort ret %+.3f%% · poz-t %s"
              % (len(w), sum(p["net"] for p in w), sum(p["net"] for p in w) / len(w),
                 100.0 * kaz / len(w), m, ("%+.2f" % t) if t else "-"))
        print("  kapi kirilimi:")
        gk = collections.defaultdict(list)
        for p in w:
            gk[p["kapi"]].append(p)
        for k in sorted(gk, key=lambda z: -sum(p["net"] for p in gk[z])):
            ww = gk[k]
            print("    %-14s N=%3d  NET %+9.2f  kazanan %%%2.0f"
                  % (k, len(ww), sum(p["net"] for p in ww),
                     100.0 * sum(1 for p in ww if p["net"] > 0) / len(ww)))
        print("  gun dagilimi: %s .. %s"
              % (min(p["giris_gun"] for p in w), max(p["giris_gun"] for p in w)))
    else:
        print("  NOTR-SHORT pozisyonu yok")

    print("\n" + "=" * 104)
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
