#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KAPI x FONLAMA KARNESI — canli defterden, POZISYON bazinda.

`olcumler.md` bunu "sirada bekleyen ILK is" diye isaretlemisti:
  "her kapi kazandigi R basina ne kadar fonlama oduyor?" — hic sorulmadi.
Bu MUHASEBEDIR, hipotez testi degil: tek soru, tek cevap.

CLAUDE.md kurallari AYNEN uygulanir:
  - Birim POZISYON: kayitlar `id` ile birlestirilir.
  - 🔴 SUZGEC SAYMAK ICIN, TOPLAMAK ICIN DEGIL: P&L toplanirken `kismi`
    SUZULMEZ (yoksa TP1'de realize edilen kar kaybolur).
  - `funding_usdt`: null = BILINMIYOR (2026-08-17 oncesi), 0.0 = mesru sifir.
    Fonlama kirilimi YALNIZ bilinen pozisyonlarda yapilir.
  - `sonuc_usdt` fonlamayi ICERMEZ -> net = sonuc + funding.
  - Kapi etiketi `sebep_giris`'in ilk ':' oncesi ( `kaynak` alani testbot
    defterinde HEP None — uydu defterlerde dolu).
SALT OKUMA — hicbir bot dosyasina yazmaz.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, collections, statistics

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFTER = os.path.join(PROJE, "testbot_islemler.jsonl")


def kapi(sg):
    return str(sg or "?").split(":")[0].strip()[:14]


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
        brut = sum((t.get("sonuc_usdt") or 0) for t in v)          # SUZGEC YOK
        fon_l = [t.get("funding_usdt") for t in v if t.get("funding_usdt") is not None]
        fon = sum(fon_l) if fon_l else None
        poz.append({
            "id": i, "sym": son["sym"], "yon": son["yon"],
            "kapi": kapi(ilk.get("sebep_giris")),
            "notional": no, "brut": brut, "fon": fon,
            "net": brut + (fon or 0.0),
            "sebep": son.get("sebep"), "tut": max((t.get("tutma_saat") or 0) for t in v),
            "tp1": any(t.get("kismi") for t in v),
            "kayit": len(v), "ts": son["ts"],
        })

    print("KAPI x FONLAMA KARNESI — canli defter, POZISYON bazinda")
    print("=" * 116)
    print("kayit %d -> POZISYON %d   (fark %d = TP1 kismi satirlari)"
          % (sum(len(v) for v in ham.values()), len(poz),
             sum(len(v) for v in ham.values()) - len(poz)))
    fb = [p for p in poz if p["fon"] is not None]
    print("fonlamasi BILINEN pozisyon: %d / %d   (oncesi null = bilinmiyor, sifir DEGIL)"
          % (len(fb), len(poz)))
    if poz:
        print("kapsam: %s .. %s" % (min(p["ts"] for p in poz), max(p["ts"] for p in poz)))

    # ------------------------------------------------------------- kapi karnesi
    print("\n" + "=" * 116)
    print("1) KAPI KARNESI — tum pozisyonlar (net = sonuc_usdt + funding_usdt)")
    print("-" * 116)
    print("  %-14s %5s %8s %11s %10s %8s %8s %8s %9s"
          % ("kapi", "N", "kazanan", "NET $", "$/poz", "TP1%", "stop%", "med saat", "med $"))
    grup = collections.defaultdict(list)
    for p in poz:
        grup[p["kapi"]].append(p)
    for k in sorted(grup, key=lambda z: -sum(p["net"] for p in grup[z])):
        w = grup[k]
        kaz = sum(1 for p in w if p["net"] > 0)
        stop = sum(1 for p in w if str(p["sebep"]).upper().startswith("STOP"))
        print("  %-14s %5d %7.0f%% %+10.2f %+9.2f %7.0f%% %7.0f%% %8.1f %+8.2f"
              % (k, len(w), 100.0 * kaz / len(w), sum(p["net"] for p in w),
                 sum(p["net"] for p in w) / len(w),
                 100.0 * sum(1 for p in w if p["tp1"]) / len(w),
                 100.0 * stop / len(w),
                 statistics.median([p["tut"] for p in w]),
                 statistics.median([p["net"] for p in w])))
    print("  " + "-" * 112)
    print("  %-14s %5d %7.0f%% %+10.2f %+9.2f"
          % ("TOPLAM", len(poz), 100.0 * sum(1 for p in poz if p["net"] > 0) / len(poz),
             sum(p["net"] for p in poz), sum(p["net"] for p in poz) / len(poz)))

    # ------------------------------------------------------------- fonlama
    print("\n" + "=" * 116)
    print("2) 🔴 KAPI x FONLAMA — asil soru: her kapi kazancinin ne kadarini fonlamaya odedi?")
    print("   (yalniz funding_usdt BILINEN pozisyonlar — 2026-08-17'den sonra acilanlar)")
    print("-" * 116)
    print("  %-14s %5s %11s %11s %11s %10s %11s"
          % ("kapi", "N", "brut $", "fonlama $", "NET $", "$/poz", "fonlama payi"))
    g2 = collections.defaultdict(list)
    for p in fb:
        g2[p["kapi"]].append(p)
    for k in sorted(g2, key=lambda z: -sum(p["net"] for p in g2[z])):
        w = g2[k]
        b = sum(p["brut"] for p in w)
        f = sum(p["fon"] for p in w)
        n = sum(p["net"] for p in w)
        pay = (100.0 * (-f) / b) if b > 0 else None
        print("  %-14s %5d %+10.2f %+10.2f %+10.2f %+9.2f %11s"
              % (k, len(w), b, f, n, n / len(w),
                 ("%.0f%%" % pay) if pay is not None else ("brut<=0" if b <= 0 else "-")))
    b = sum(p["brut"] for p in fb)
    f = sum(p["fon"] for p in fb)
    print("  " + "-" * 112)
    print("  %-14s %5d %+10.2f %+10.2f %+10.2f %+9.2f %11s"
          % ("TOPLAM", len(fb), b, f, b + f, (b + f) / len(fb) if fb else 0,
             ("%.0f%%" % (100.0 * (-f) / b)) if b > 0 else "brut<=0"))
    print()
    print("  NOT: 'fonlama payi' = odenen fonlama / BRUT kar. Brut <= 0 ise oransizdir")
    print("       (kapi zaten kaybediyorsa fonlamanin payi anlamli bir sayi vermez).")

    # ------------------------------------------------------------- yon x kapi
    print("\n" + "=" * 116)
    print("3) YON KIRILIMI — fonlama yonle isaret degistirir (SHORT oder, LONG tahsil eder)")
    print("-" * 116)
    print("  %-14s %-6s %5s %11s %11s %11s" % ("kapi", "yon", "N", "brut $", "fonlama $", "NET $"))
    for k in sorted(g2):
        for y in ("SHORT", "LONG"):
            w = [p for p in g2[k] if p["yon"] == y]
            if not w:
                continue
            print("  %-14s %-6s %5d %+10.2f %+10.2f %+10.2f"
                  % (k, y, len(w), sum(p["brut"] for p in w),
                     sum(p["fon"] for p in w), sum(p["net"] for p in w)))

    # ------------------------------------------------------------- mutabakat
    print("\n" + "=" * 116)
    print("4) MUTABAKAT — CLAUDE.md denklemi")
    print("-" * 116)
    st = os.path.join(PROJE, "testbot_state.json")
    if os.path.exists(st):
        s = json.load(open(st, encoding="utf-8"))
        eq = s.get("equity")
        kf = s.get("kumulatif_funding")
        ku = s.get("kumulatif_giris_ucret")
        print("  state equity                : %s" % eq)
        print("  state kumulatif_funding     : %s   (2026-07-23'ten beri KUMULATIF, pencereye ait DEGIL)" % kf)
        print("  state kumulatif_giris_ucret : %s" % ku)
        print("  defter brut P&L toplami     : %+.2f" % sum(p["brut"] for p in poz))
        print("  defter (bilinen) fonlama    : %+.2f" % sum(p["fon"] for p in fb))
        print("  acik pozisyon               : %d" % len(s.get("pozisyonlar") or []))
        print("  -> equity ACIK pozisyonlari da icerir; kapali-defter toplami ile")
        print("     birebir esitlik BEKLENMEZ. Tam mutabakat icin acik pozlarin")
        print("     unrealize'i ve kasa sifirlamasi eklenmeli.")
    else:
        print("  testbot_state.json bulunamadi")

    print("\n" + "=" * 116)
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
