#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BASI BULGUSU — ZORUNLU KARISTIRICI SINAMASI (2026-09-05)

🔴 NEDEN: basi = notional / defter_usdt_20.  Bot'ta notional ~ hedef_risk/stop_frac,
   yani DAR STOP -> BUYUK notional -> BUYUK basi.  Dar stop bu projede OLCULMUS
   bir kayip bolgesi.  Yani "kalin pozisyon kotu" bulgusu, "dar stop kotu"nun
   KILIGI olabilir.  CLAUDE.md bunu hukum yazmadan once kosmayi ZORUNLU kiliyor.

UC SINAMA:
  1) VARYANS AYRISTIRMASI — basi'yi notional mi DEFTER mi oynatiyor?
  2) STOP GENISLIGI ceyreklere gore ayrisiyor mu?
  3) STOP SABITLENINCE basi hala ayiriyor mu? (stratifiye)

BETIMLEYICI — hukum tasimaz, hukmun GECERLILIGINI sinar. Salt-okunur.
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


def izleme_stop():
    """id -> ILK izleme kaydindaki stop_mesafe_pct (giris ani)."""
    out = {}
    p = os.path.join(KOK, "pozisyon_izleme.jsonl")
    if not os.path.exists(p):
        return out
    for line in open(p, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        i, s = r.get("id"), r.get("stop_mesafe_pct")
        if i is None or s is None:
            continue
        ts = r.get("ts") or ""
        o = out.get(i)
        if o is None or ts < o[1]:
            out[i] = (s, ts)
    return dict((k, v[0]) for k, v in out.items())


def yukle(stopmap):
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
            kay.append({
                "defter": d, "id": i, "sym": ana.get("sym"),
                "gun": (ana.get("ts") or "")[:10],
                "basi": no / db, "ret": usd / no * 100.0,
                "notional": no, "defter_usdt": db,
                "stop": stopmap.get(i),
                "sebep": ana.get("sebep"), "yon": ana.get("yon"),
            })
    return kay


def ceyrekle(kay):
    s = sorted(kay, key=lambda x: x["basi"])
    n = len(s) // 4
    return [("Q1 (en INCE)", s[:n]), ("Q2", s[n:2 * n]),
            ("Q3", s[2 * n:3 * n]), ("Q4 (en KALIN)", s[3 * n:])]


def gunt(ust, alt):
    ga, gb = collections.defaultdict(list), collections.defaultdict(list)
    for p in ust:
        ga[p["gun"]].append(p["ret"])
    for p in alt:
        gb[p["gun"]].append(p["ret"])
    ortak = set(ga) & set(gb)
    f = [sum(ga[g]) / len(ga[g]) - sum(gb[g]) / len(gb[g]) for g in ortak]
    if len(f) < 3:
        return None, None, len(f)
    m = sum(f) / len(f)
    se = stx.stdev(f) / math.sqrt(len(f))
    return m, (m / se if se else None), len(f)


def main():
    print("=" * 96)
    print("BASI BULGUSU — ZORUNLU KARISTIRICI SINAMASI")
    print("=" * 96)
    print("🔴 basi = notional/defter · notional ~ risk/stop_frac -> DAR STOP = KALIN basi")
    print()

    sm = izleme_stop()
    kay = yukle(sm)
    ile = [p for p in kay if p["stop"] is not None]
    print("N = %d pozisyon (5 defter) · stop bilgisi olan: %d (%%%.0f)"
          % (len(kay), len(ile), len(ile) / len(kay) * 100 if kay else 0))
    print()

    cy = ceyrekle(kay)

    print("### 1) VARYANS AYRISTIRMASI — basi'yi NE oynatiyor?")
    print("   log(basi) = log(notional) - log(defter_usdt_20)")
    ln = [math.log(p["notional"]) for p in kay]
    ld = [math.log(p["defter_usdt"]) for p in kay]
    vn, vd = stx.variance(ln), stx.variance(ld)
    print("   var log(notional)       = %7.4f   <- karistiricinin girebilecegi yer" % vn)
    print("   var log(defter_usdt_20) = %7.4f   <- botun kontrolunde DEGIL (temiz)" % vd)
    print("   -> notional payi %%%.1f  ·  defter payi %%%.1f"
          % (vn / (vn + vd) * 100, vd / (vn + vd) * 100))
    b1 = stx.median([p["basi"] for p in cy[0][1]])
    b4 = stx.median([p["basi"] for p in cy[3][1]])
    n1 = stx.median([p["notional"] for p in cy[0][1]])
    n4 = stx.median([p["notional"] for p in cy[3][1]])
    print("   ceyrek Q1->Q4:  basi %.4f -> %.4f  (%.1f KAT)" % (b1, b4, b4 / b1))
    print("                   notional %.0f -> %.0f  (%.2f kat)" % (n1, n4, n4 / n1))
    print()

    print("### 2) SINAMA — ceyrekler STOP GENISLIGINDE ayrisiyor mu?")
    print("   %-15s %6s %10s %11s %12s %11s"
          % ("ceyrek", "N", "basi med", "stop% med", "notional med", "ret ort"))
    kats = []
    for ad, g in cy:
        st = [p["stop"] for p in g if p["stop"] is not None]
        kats.append(stx.median(st) if st else None)
        print("   %-15s %6d %10.4f %11s %12.0f %+10.3f%%"
              % (ad, len(g), stx.median([p["basi"] for p in g]),
                 ("%.2f" % stx.median(st)) if st else "yok",
                 stx.median([p["notional"] for p in g]),
                 stx.mean([p["ret"] for p in g])))
    if kats[0] and kats[3]:
        kat = kats[0] / kats[3]
        durum = "🔴 AYRISIYOR — karistirici GERCEK"
        if 0.77 <= kat <= 1.3:
            durum = "✅ ayrismiyor — karistirici zayif"
        print()
        print("   -> stop genisligi Q1/Q4 = %.2f kat   %s" % (kat, durum))
    print()

    print("### 3) BELIRLEYICI — STOP SABITLENINCE basi hala ayiriyor mu?")
    if len(ile) < 60:
        print("   stop bilgisi olan N=%d — yetersiz, sinama YAPILAMADI" % len(ile))
    else:
        ile.sort(key=lambda p: p["stop"])
        t3 = len(ile) // 3
        dilimler = (("dar stop", ile[:t3]), ("orta stop", ile[t3:2 * t3]),
                    ("genis stop", ile[2 * t3:]))
        print("   %-12s %6s %10s %11s %11s %9s %8s"
              % ("stop dilimi", "N", "stop med", "ust ort", "alt ort", "fark", "gun-t"))
        ayakta = 0
        for ad, g in dilimler:
            g2 = sorted(g, key=lambda p: p["basi"])
            h = len(g2) // 2
            alt, ust = g2[:h], g2[h:]
            if not alt or not ust:
                continue
            uo = stx.mean([p["ret"] for p in ust])
            ao = stx.mean([p["ret"] for p in alt])
            m, t, nk = gunt(ust, alt)
            if uo - ao < 0:
                ayakta += 1
            print("   %-12s %6d %10.2f %+10.3f%% %+10.3f%% %+8.3f %8s"
                  % (ad, len(g), stx.median([p["stop"] for p in g]), uo, ao, uo - ao,
                     ("%.2f" % t) if t else "yok"))
        sonuc = "🔴 basi kismen stop'un vekili"
        if ayakta == 3:
            sonuc = "✅ basi stop'un vekili DEGIL"
        print()
        print("   -> %d/3 stop diliminde isaret AYNI (negatif)   %s" % (ayakta, sonuc))
    print()

    print("### 4) SLIPAJ MEKANIZMA MI? (buyukluk kiyasi)")
    fark = stx.mean([p["ret"] for p in cy[0][1]]) - stx.mean([p["ret"] for p in cy[3][1]])
    print("   getiri farki (Q1-Q4) : %+.3f puan" % fark)
    print("   olculen slipaj farki :  ~0,044 puan  (0,0230 -> 0,0673)")
    print("   -> slipaj farkin ancak %%%.1f'ini aciklar  ->  MEKANIZMA DEGIL"
          % (0.044 / fark * 100))
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
