#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-19 AGUSTOS PENCERESI — "elimizdeki en iyi bot oydu" tespitinin olcumu

Kullanici: "basarilidan kastim sectigi coinler bir sekilde buyuk oranda artida
  kaliyordu, elimizdeki en iyi bot oydu."

🔴 CLAUDE.md KURALLARI:
  - Pozisyon SAYARKEN  not kismi ; P&L TOPLARKEN id ile birlestir (suzgec YOK).
  - "acilip kapanan" ayrimi: pencere tabani secilirken girisi de o pencerede
    olan pozisyonlar sayilir (kayitli celiski uretmis bir ayrim).
  - 'r' kismi kari GORMEZ -> dolar ile ters isaret verebilir; ikisi de yazilir.
BETIMLEYICI. On-kayit yok, hukum yok. Salt-okunur.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, math, statistics as stx, collections

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFTER = os.path.join(KOK, "testbot_islemler.jsonl")

PENCERELER = [
    ("07-23..08-10  (S9 oncesi)", "2026-07-23", "2026-08-11"),
    ("08-11..08-19  <- KULLANICI", "2026-08-11", "2026-08-20"),
    ("08-20..08-20              ", "2026-08-20", "2026-08-21"),
    ("08-21..09-05  (BOGA)      ", "2026-08-21", "2026-09-06"),
]


def poz_birlestir():
    g = collections.defaultdict(list)
    for line in open(DEFTER, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        g[r.get("id")].append(r)
    out = []
    for i, ks in g.items():
        ana = next((k for k in ks if not k.get("kismi")), ks[0])
        out.append({
            "id": i, "sym": ana.get("sym"), "yon": ana.get("yon"),
            "ts": ana.get("ts") or "", "sebep": ana.get("sebep"),
            "usd": sum(k.get("sonuc_usdt") or 0.0 for k in ks),
            "r": ana.get("r"),
            "notional": ana.get("notional") or 0.0,
            "kismi_var": any(k.get("kismi") for k in ks),
            "kaynak": ana.get("sebep_giris") or "",
        })
    return out


def gun_t(ps):
    g = collections.defaultdict(list)
    for p in ps:
        g[p["ts"][:10]].append(p["usd"])
    v = [sum(x) / len(x) for x in g.values()]
    if len(v) < 3:
        return None, None, len(v), None
    m = sum(v) / len(v)
    se = stx.stdev(v) / math.sqrt(len(v))
    return m, (m / se if se else None), len(v), 2 * se


def main():
    poz = poz_birlestir()
    print("=" * 96)
    print("11-19 AGUSTOS — 'elimizdeki en iyi bot oydu' tespitinin olcumu")
    print("=" * 96)
    print("🔴 Betimleyici. On-kayit yok, hukum yok.\n")
    print("%-28s %5s %10s %9s %8s %8s %9s %8s %7s" %
          ("pencere", "N", "toplam $", "ort $", "kazanan", "R_med", "gun ort", "t_gun", "gun"))
    for ad, a, b in PENCERELER:
        ps = [p for p in poz if a <= p["ts"][:10] < b]
        if not ps:
            print("%-28s (yok)" % ad)
            continue
        usd = sum(p["usd"] for p in ps)
        kaz = sum(1 for p in ps if p["usd"] > 0) / len(ps) * 100
        rs = [p["r"] for p in ps if p["r"] is not None]
        m, t, ng, mde = gun_t(ps)
        print("%-28s %5d %+10.2f %+9.2f %7.1f%% %+8.2f %+9.2f %+8s %7d" %
              (ad, len(ps), usd, usd / len(ps), kaz,
               stx.median(rs) if rs else 0,
               m if m is not None else 0,
               ("%.2f" % t) if t is not None else "yok", ng))

    print("\n### 11-19 PENCERESI — AYRINTI")
    ps = [p for p in poz if "2026-08-11" <= p["ts"][:10] < "2026-08-20"]
    if not ps:
        print("  pozisyon yok")
        return
    print("  yon dagilimi : %s" % dict(collections.Counter(p["yon"] for p in ps)))
    print("  cikis sebebi : %s" % dict(collections.Counter(p["sebep"] for p in ps)))
    print("  kismi kar    : %d / %d pozisyonda" % (sum(1 for p in ps if p["kismi_var"]), len(ps)))
    for y in ("SHORT", "LONG"):
        s = [p for p in ps if p["yon"] == y]
        if not s:
            continue
        usd = sum(p["usd"] for p in s)
        print("  %-5s N=%-3d toplam %+9.2f $  ort %+7.2f  kazanan %%%.1f" %
              (y, len(s), usd, usd / len(s), sum(1 for p in s if p["usd"] > 0) / len(s) * 100))

    print("\n  GUNLUK:")
    g = collections.defaultdict(float)
    n = collections.Counter()
    for p in ps:
        g[p["ts"][:10]] += p["usd"]
        n[p["ts"][:10]] += 1
    for d in sorted(g):
        print("    %s  %3d islem  %+9.2f $" % (d, n[d], g[d]))
    art = sum(1 for v in g.values() if v > 0)
    print("  artida gun: %d / %d" % (art, len(g)))

    print("\n  YOGUNLASMA (tek gun/islem tasiyor mu):")
    top = sum(g.values())
    sr = sorted(g.values(), reverse=True)
    pr = sorted((p["usd"] for p in ps), reverse=True)
    if abs(top) > 1e-9:
        print("    en iyi 1 gun   %+9.2f $ -> toplamin %%%.0f'i" % (sr[0], sr[0] / top * 100))
        print("    en iyi 2 gun   %+9.2f $ -> toplamin %%%.0f'i" % (sum(sr[:2]), sum(sr[:2]) / top * 100))
        print("    en iyi 5 islem %+9.2f $ -> toplamin %%%.0f'i" % (sum(pr[:5]), sum(pr[:5]) / top * 100))
        print("    en iyi 2 gun HARIC: %+.2f $" % (top - sum(sr[:2])))

    print("\n  EN COK KAZANDIRAN 5 / KAYBETTIREN 5:")
    sp = sorted(ps, key=lambda p: -p["usd"])
    for p in sp[:5]:
        print("    + %-10s %-5s %+9.2f $  (%s)" % (p["sym"], p["yon"], p["usd"], p["sebep"]))
    for p in sp[-5:]:
        print("    - %-10s %-5s %+9.2f $  (%s)" % (p["sym"], p["yon"], p["usd"], p["sebep"]))

    print("\nBot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
