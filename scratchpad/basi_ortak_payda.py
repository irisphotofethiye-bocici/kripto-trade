#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BASI BULGUSU ORTAK-PAYDA ESERI MI? — KESIN SINAMA (2026-09-05)

🔴 CLAUDE.md: "ORTAK PAYDALI ORAN SAHTE KORELASYON URETIR — iki kez isirdi.
   Boyutla ilgili bir iddia yazmadan once sor: bu buyuklugun paydasinda,
   karsilastirdigim degisken var mi? Varsa o korelasyon DAYANAK OLAMAZ.
   Guvenli olan tek sey boyuttan bagimsiz buyuklugun kendi TOPLAMI/ORTALAMASI."

TESPIT:
   basi = notional / defter      -> notional PAYDA'da degil PAY'da
   ret  = sonuc    / notional    -> notional PAYDA'da
   ORTAK DEGISKEN: notional.  Iliski mekanik olarak garanti.

VE: sembol icinde defterin katkisi r=+0,022 (SIFIR); etkinin TAMAMI notional'dan.
   Yani "emir defteri bulgusu" aslinda bir BOYUT bulgusu olabilir.

KESIN SINAMA — bot SABIT KESIRLI RISK kullanir (risk_usd ~ sabit).
   O yuzden risk-normalize buyukluk zaten DOLARDIR, ret% degil.
   Soru: notional / basi, DOLAR P&L'i ongoruyor mu?
     ongormuyorsa -> bulgu ESER, coker
     ongoruyorsa  -> bulgu GERCEK

BETIMLEYICI. Salt-okunur.
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
                        "basi": no / db, "notional": no, "defter": db,
                        "usd": usd, "ret": usd / no * 100.0, "defterad": d})
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
    return r, r * math.sqrt((n - 2) / (1 - r * r))


def gunt(v):
    g = collections.defaultdict(list)
    for gun, x in v:
        g[gun].append(x)
    d = [sum(a) / len(a) for a in g.values()]
    if len(d) < 3:
        return None, None, len(d)
    m = sum(d) / len(d)
    se = stx.stdev(d) / math.sqrt(len(d))
    return m, (m / se if se else None), len(d)


def ceyrek(kay, alan):
    s = sorted(kay, key=lambda x: x[alan])
    n = len(s) // 4
    return [s[:n], s[n:2 * n], s[2 * n:3 * n], s[3 * n:]]


def main():
    print("=" * 96)
    print("BASI BULGUSU ORTAK-PAYDA ESERI MI? — KESIN SINAMA")
    print("=" * 96)
    print("🔴 basi = notional/defter   (notional PAY'da)")
    print("   ret  = sonuc/notional    (notional PAYDA'da)   -> ORTAK: notional")
    print("   Sembol icinde defterin katkisi r=+0,022 -> etkinin TAMAMI notional")
    print()

    kay = yukle()
    print("N = %d pozisyon" % len(kay))
    print()

    print("### 1) AYNI CEYREKLER, IKI OLCU: ret%% (kirli) vs DOLAR (temiz)")
    print("   %-18s %6s %12s %13s %13s" %
          ("basi ceyregi", "N", "ret% ort", "DOLAR ort", "DOLAR toplam"))
    cy = ceyrek(kay, "basi")
    adlar = ("Q1 (en INCE)", "Q2", "Q3", "Q4 (en KALIN)")
    for ad, g in zip(adlar, cy):
        print("   %-18s %6d %+11.3f%% %+12.2f %+13.2f"
              % (ad, len(g), stx.mean([p["ret"] for p in g]),
                 stx.mean([p["usd"] for p in g]), sum(p["usd"] for p in g)))
    r1 = stx.mean([p["ret"] for p in cy[3]]) - stx.mean([p["ret"] for p in cy[0]])
    d1 = stx.mean([p["usd"] for p in cy[3]]) - stx.mean([p["usd"] for p in cy[0]])
    print()
    print("   Q4-Q1  ret%%  : %+.3f puan" % r1)
    print("   Q4-Q1  DOLAR : %+.2f $" % d1)
    if r1 * d1 <= 0:
        print("   -> 🔴 ISARET DONDU. ret%% ile dolar TERS. Ortak-payda eseri.")
    else:
        print("   -> ✅ Isaret ayni. Eser tek basina aciklamiyor.")
    print()

    print("### 2) GUN-KUMELI, dolar cinsinden (birincil ölçüt neydi: gun-kumeli t)")
    ust = [(p["gun"], p["usd"]) for p in cy[3]]
    alt = [(p["gun"], p["usd"]) for p in cy[0]]
    gu = collections.defaultdict(list)
    ga = collections.defaultdict(list)
    for g, x in ust:
        gu[g].append(x)
    for g, x in alt:
        ga[g].append(x)
    ortak = set(gu) & set(ga)
    f = [sum(gu[g]) / len(gu[g]) - sum(ga[g]) / len(ga[g]) for g in ortak]
    if len(f) >= 3:
        m = sum(f) / len(f)
        se = stx.stdev(f) / math.sqrt(len(f))
        print("   gun-eslesmis DOLAR farki (Q4-Q1) = %+.2f $   t = %+.2f   (%d gun)"
              % (m, m / se if se else 0, len(f)))
        print("   negatif gun sayisi: %d/%d" % (sum(1 for x in f if x < 0), len(f)))
    print()

    print("### 3) NOTIONAL TEK BASINA — tuzagin kendisi")
    print("   %-22s %6s %12s %13s" % ("notional ceyregi", "N", "ret% ort", "DOLAR ort"))
    cn = ceyrek(kay, "notional")
    for ad, g in zip(("Q1 (en KUCUK)", "Q2", "Q3", "Q4 (en BUYUK)"), cn):
        print("   %-22s %6d %+11.3f%% %+12.2f"
              % (ad, len(g), stx.mean([p["ret"] for p in g]),
                 stx.mean([p["usd"] for p in g])))
    rn, tn = kor([math.log(p["notional"]) for p in kay], [p["ret"] for p in kay])
    rd, td = kor([math.log(p["notional"]) for p in kay], [p["usd"] for p in kay])
    print()
    print("   r(log notional, ret%%)  = %+.3f  t=%+.2f   <- CLAUDE.md: eser, dayanak DEGIL"
          % (rn, tn))
    print("   r(log notional, DOLAR) = %+.3f  t=%+.2f   <- temiz olcu" % (rd, td))
    print()

    print("### 4) DEFTER DERINLIGI TEK BASINA, DOLAR ile (emir defterinin SAF sinavi)")
    print("   %-24s %6s %14s %12s %13s" %
          ("defter ceyregi", "N", "defter $ med", "DOLAR ort", "ret% ort"))
    cd = ceyrek(kay, "defter")
    for ad, g in zip(("Q1 (EN SIG)", "Q2", "Q3", "Q4 (EN DERIN)"), cd):
        print("   %-24s %6d %14.0f %+11.2f %+12.3f%%"
              % (ad, len(g), stx.median([p["defter"] for p in g]),
                 stx.mean([p["usd"] for p in g]), stx.mean([p["ret"] for p in g])))
    rr, tt = kor([math.log(p["defter"]) for p in kay], [p["usd"] for p in kay])
    print()
    print("   r(log defter, DOLAR) = %+.3f  t=%+.2f" % (rr, tt))
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
