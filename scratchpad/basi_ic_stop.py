#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ICERIDEKI BASI ETKISI STOP'UN KILIGI MI? (2026-09-05)

🔴 SON KONTROL. Sembol icinde defter_usdt_20 ~ sabit, dolayisiyla
   basi sapmasi ~ NOTIONAL sapmasi.  Ve bot'ta notional ~ risk/stop_frac.
   Yani iceride olculen sey "dar stop"un kiligi OLABILIR.
   CLAUDE.md'nin ORTAK PAYDA tuzagi tam burada iki kez isirdi.

UC SORU:
  1) Sembol icinde basi sapmasi ~ stop sapmasi korelasyonu nedir?
  2) MEKANIK YON: dar stop -> kucuk |ret| bekleriz. Gozlenen yon hangisi?
  3) Stop SABITLENINCE sembol-ici etki ayakta mi?

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


def izleme_stop():
    out = {}
    p = os.path.join(KOK, "pozisyon_izleme.jsonl")
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


def yukle(sm):
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
            st = sm.get(i)
            if not no or not db or st is None:
                continue
            usd = sum(k.get("sonuc_usdt") or 0.0 for k in ks)
            kay.append({"sym": ana.get("sym"), "lb": math.log(no / db),
                        "ret": usd / no * 100.0, "lstop": math.log(st),
                        "sebep": ana.get("sebep")})
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


def sapmalar(kay, en_az=4):
    gs = collections.defaultdict(list)
    for p in kay:
        gs[p["sym"]].append(p)
    out = []
    for s, g in gs.items():
        if len(g) < en_az:
            continue
        mb = stx.mean([p["lb"] for p in g])
        mr = stx.mean([p["ret"] for p in g])
        ms = stx.mean([p["lstop"] for p in g])
        for p in g:
            out.append({"db": p["lb"] - mb, "dr": p["ret"] - mr,
                        "ds": p["lstop"] - ms, "sym": s, "sebep": p["sebep"]})
    return out


def main():
    print("=" * 96)
    print("ICERIDEKI BASI ETKISI STOP'UN KILIGI MI?")
    print("=" * 96)
    print("🔴 Sembol icinde defter ~ sabit -> basi sapmasi ~ NOTIONAL sapmasi")
    print("   ve notional ~ risk/stop_frac.  Ortak payda tuzagi tam burasi.")
    print()

    kay = yukle(izleme_stop())
    sp = sapmalar(kay)
    print("N = %d pozisyon (stop bilgisi olan) · sapma ornegi = %d" % (len(kay), len(sp)))
    print()

    print("### 1) Sembol ICINDE: basi sapmasi ~ stop sapmasi")
    r, t = kor([x["db"] for x in sp], [x["ds"] for x in sp])
    print("   r = %+.3f   t = %+.2f" % (r, t))
    print("   beklenen (mekanik): notional ~ 1/stop  ->  r NEGATIF olmali")
    if r < -0.5:
        print("   -> 🔴 GUCLU mekanik bag: basi buyuk olcude stop'un tersi")
    elif r < -0.2:
        print("   -> ⚠️ ORTA mekanik bag var")
    else:
        print("   -> ✅ ZAYIF bag: basi stop'tan bagimsiz oynuyor")
    print()

    print("### 2) MEKANIK YON — tuzak bizi hangi yone iterdi?")
    print("   Pozisyonlarin %%%.0f'i STOP ile kapaniyor."
          % (sum(1 for p in kay if p["sebep"] == "STOP") / len(kay) * 100))
    print("   STOP'ta ret ~ -stop_mesafe.  DAR stop -> KUCUK kayip -> ret DAHA IYI.")
    print("   Ve dar stop -> BUYUK notional -> KALIN basi.")
    print("   => Tuzak gercek olsaydi:  KALIN basi -> DAHA IYI getiri beklerdik.")
    r2, t2 = kor([x["db"] for x in sp], [x["dr"] for x in sp])
    print("   GOZLENEN: r(basi sapma, getiri sapma) = %+.3f  t = %+.2f" % (r2, t2))
    if r2 < 0:
        print("   -> ✅ Gozlenen yon TUZAGIN TERSI. Tuzak bu bulguyu URETEMEZ.")
    else:
        print("   -> 🔴 Gozlenen yon tuzakla AYNI. Ayirt edilemez.")
    print()

    print("### 3) STOP SABITLENINCE sembol-ici etki ayakta mi?")
    sp.sort(key=lambda x: x["ds"])
    t3 = len(sp) // 3
    dilim = (("dar sapma", sp[:t3]), ("orta", sp[t3:2 * t3]), ("genis sapma", sp[2 * t3:]))
    print("   %-14s %7s %12s %12s %10s %9s"
          % ("stop sapmasi", "N", "ust basi", "alt basi", "fark", "r_ici"))
    ayakta = 0
    for ad, g in dilim:
        g2 = sorted(g, key=lambda x: x["db"])
        h = len(g2) // 2
        alt, ust = g2[:h], g2[h:]
        uo, ao = stx.mean([x["dr"] for x in ust]), stx.mean([x["dr"] for x in alt])
        rr, tt = kor([x["db"] for x in g], [x["dr"] for x in g])
        if uo - ao < 0:
            ayakta += 1
        print("   %-14s %7d %+11.3f %+11.3f %+9.3f %8s"
              % (ad, len(g), uo, ao, uo - ao, ("%+.3f" % rr) if rr is not None else "yok"))
    print()
    sonuc = "🔴 kismen stop'un vekili"
    if ayakta == 3:
        sonuc = "✅ etki stop'tan BAGIMSIZ ayakta"
    print("   -> %d/3 dilimde isaret ayni   %s" % (ayakta, sonuc))
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
