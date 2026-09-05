#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BASI: BOYUTLANDIRMA MI, COIN SECIMI MI? (2026-09-05)

🔴 ILK KOSUM (2026-08-30) BUNU ACIK BIRAKMISTI ve "bu hukum yazilmadan
   cozulmeli" demisti.  O gun eslesen sembol sayisi 6'ydi.  Bugun ornek
   1.056 -> 1.858 pozisyona cikti; ayrim simdi yapilabilir.

IKI RAKIP ACIKLAMA:
  (a) BOYUTLANDIRMA — ayni coinde bile, pozisyon defterin yaninda buyukse kotu
      -> kural: pozisyonu defter derinligine gore kirp
  (b) COIN SECIMI   — sig defterli coinlerde daha kotuyuz, boyut onemsiz
      -> kural: sig coine hic girme

YONTEM — sabit-etki ayristirmasi (within/between):
  ICERIDE (within) : her pozisyonun basi'si KENDI SEMBOLUNUN ortalamasindan sapma
                     -> yalniz (a)'yi tasir
  DISARIDA (between): sembol ortalamasi basi vs sembol ortalamasi getiri
                     -> yalniz (b)'yi tasir

BETIMLEYICI — hukum tasimaz. Salt-okunur.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, math, statistics as stx, collections

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFTERLER = ("testbot", "golge", "ayna", "defter2", "defter3")


def yukle():
    kay = []
    for d in DEFTERLER:
        p = os.path.join(KOK, "%s_islemler.jsonl" % d)
        if not os.path.exists(p):
            continue
        grup = collections.defaultdict(list)
        for line in open(p, encoding="utf-8", errors="replace"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            grup[r.get("id")].append(r)
        for i, ks in grup.items():
            ana = next((k for k in ks if not k.get("kismi")), ks[0])
            dr = ana.get("derinlik_giriste")
            if not dr:
                continue
            no = ana.get("notional") or 0.0
            db = dr.get("defter_usdt_20")
            if not no or not db:
                continue
            usd = sum(k.get("sonuc_usdt") or 0.0 for k in ks)
            kay.append({"sym": ana.get("sym"), "gun": (ana.get("ts") or "")[:10],
                        "lb": math.log(no / db), "ret": usd / no * 100.0,
                        "ldefter": math.log(db), "defter": d})
    return kay


def kor(xs, ys):
    if len(xs) < 8:
        return None, None
    mx, my = stx.mean(xs), stx.mean(ys)
    pay = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    px = math.sqrt(sum((a - mx) ** 2 for a in xs))
    py = math.sqrt(sum((b - my) ** 2 for b in ys))
    if not px or not py:
        return None, None
    r = pay / (px * py)
    n = len(xs)
    if abs(r) >= 0.9999:
        return r, None
    t = r * math.sqrt((n - 2) / (1 - r * r))
    return r, t


def main():
    print("=" * 96)
    print("BASI: BOYUTLANDIRMA MI (a), COIN SECIMI MI (b)?")
    print("=" * 96)
    print("🔴 2026-08-30 kosumu bu ayrimi ACIK birakmisti (o gun eslesen sembol=6)")
    print()

    kay = yukle()
    say = collections.Counter(p["sym"] for p in kay)
    print("N = %d pozisyon · %d tekil sembol" % (len(kay), len(say)))
    cok = [s for s, k in say.items() if k >= 4]
    print("en az 4 pozisyonu olan sembol: %d  (iceride sinama bunlarla yapilir)"
          % len(cok))
    print()

    # ---- DISARIDA: sembol ortalamalari ----
    print("### (b) DISARIDA — sembol ortalamasi basi  vs  sembol ortalamasi getiri")
    gs = collections.defaultdict(list)
    for p in kay:
        gs[p["sym"]].append(p)
    xs, ys, ws = [], [], []
    for s, g in gs.items():
        if len(g) < 4:
            continue
        xs.append(stx.mean([p["lb"] for p in g]))
        ys.append(stx.mean([p["ret"] for p in g]))
        ws.append(len(g))
    r, t = kor(xs, ys)
    print("   N sembol = %d" % len(xs))
    print("   r(sembol ort log-basi, sembol ort getiri) = %s   t = %s"
          % (("%+.3f" % r) if r is not None else "yok",
             ("%+.2f" % t) if t is not None else "yok"))
    print()

    # ---- ICERIDE: sembol icinde sapma ----
    print("### (a) ICERIDE — sembol ortalamasindan SAPMA (sembol sabitlendi)")
    dx, dy = [], []
    for s, g in gs.items():
        if len(g) < 4:
            continue
        mb = stx.mean([p["lb"] for p in g])
        mr = stx.mean([p["ret"] for p in g])
        for p in g:
            dx.append(p["lb"] - mb)
            dy.append(p["ret"] - mr)
    r2, t2 = kor(dx, dy)
    print("   N pozisyon = %d  (%d sembolden)" % (len(dx), len(xs)))
    print("   r(sapma log-basi, sapma getiri) = %s   t = %s"
          % (("%+.3f" % r2) if r2 is not None else "yok",
             ("%+.2f" % t2) if t2 is not None else "yok"))
    print()

    # ---- iceride ceyrek tablosu ----
    print("   iceride, SAPMA ceyreklerine gore ortalama sapma-getiri:")
    ikili = sorted(zip(dx, dy))
    n4 = len(ikili) // 4
    adlar = ("Q1 (sembol ortalamasindan INCE)", "Q2", "Q3",
             "Q4 (sembol ortalamasindan KALIN)")
    for k, ad in enumerate(adlar):
        dil = ikili[k * n4:(k + 1) * n4] if k < 3 else ikili[3 * n4:]
        print("      %-34s N=%-5d sapma-getiri ort %+7.3f puan"
              % (ad, len(dil), stx.mean([b for _, b in dil])))
    print()

    # ---- DEFTER DERINLIGI TEK BASINA (b'nin saf hali) ----
    print("### (b) SAF HALI — DEFTER DERINLIGI tek basina (boyut hic yok)")
    ds = sorted(kay, key=lambda p: p["ldefter"])
    m4 = len(ds) // 4
    print("   %-24s %6s %14s %12s" % ("ceyrek", "N", "defter $ med", "getiri ort"))
    for k, ad in enumerate(("Q1 (EN SIG defter)", "Q2", "Q3", "Q4 (EN DERIN defter)")):
        dil = ds[k * m4:(k + 1) * m4] if k < 3 else ds[3 * m4:]
        print("   %-24s %6d %14.0f %+11.3f%%"
              % (ad, len(dil), math.exp(stx.median([p["ldefter"] for p in dil])),
                 stx.mean([p["ret"] for p in dil])))
    print()

    print("=" * 96)
    print("YORUM ANAHTARI")
    print("=" * 96)
    print("  iceride GUCLU + disarida zayif  ->  (a) BOYUTLANDIRMA  -> pozisyonu kirp")
    print("  disarida GUCLU + iceride zayif  ->  (b) COIN SECIMI    -> sig coine girme")
    print("  ikisi de guclu                  ->  IKISI BIRDEN")
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
