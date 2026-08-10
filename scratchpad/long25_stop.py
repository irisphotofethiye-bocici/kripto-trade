#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LONG %2.5 — STOP TARAMASI (2026-08-10) — "longda stopu ayarlarsak 2.5 yasar mi?"

MANTIK: hedef %2.5 sabitken basabas = stop% / (2.5 + stop%).
  stop %0.50 -> basabas %16.7   |  stop %1.00 -> %28.6
  stop %1.50 -> %37.5           |  stop %2.50 -> %50.0
Yani stop DARALDIKCA basabas duser — ama isabet de duser (daha cok stop yenir).
SORU: bir yerde isabet basabasin USTUNE cikiyor mu?

TARAMA (11 stop varyanti, 3 ufuk):
  ATR katlari : 0.25 · 0.35 · 0.50 · 0.75 · 1.00 · 1.50 · 2.00
  sabit yuzde : %0.5 · %0.75 · %1.0 · %1.5
  ufuk        : 6 · 24 · 72 saat  (kucuk hedef hizli tutulur)
Ayrica en iyi bulunan varyant KOSUL kirilimiyla ve ZAMAN IKIYE BOLUNEREK dogrulanir.

DURUSTLUK NOTU: bu bir ESIK TARAMASIDIR — projede normalde yasak. Burada mesru,
cunku amac "en iyi esigi bulup koda koymak" DEGIL, "boyle bir esik VAR MI" sorusunu
cevaplamak. Bulunan en iyi hucre, zaman bolmesinde ayakta kalmazsa TARAMA ARTIGIDIR
ve oyle raporlanir. Hicbir sonuc dogrudan koda girmez.
"""
import json, os, statistics as st, datetime

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h")
NBAR, MALIYET = 10, 0.09
HEDEF = 2.5


def atr14(b, i):
    if i < 14:
        return None
    tr = []
    for j in range(i - 13, i + 1):
        p = b[j - 1]["c"]
        tr.append(max(b[j]["h"] - b[j]["l"], abs(b[j]["h"] - p), abs(p - b[j]["l"])))
    return st.mean(tr)


def oyna(b, gi, stop_tanim, ufuk, yon="LONG"):
    i = gi - 1
    if i < 30 or gi >= len(b):
        return None
    a = atr14(b, i)
    if not a or a <= 0:
        return None
    ref = b[gi]["o"]
    tip, deger = stop_tanim
    sp = (deger * a / ref * 100) if tip == "atr" else deger      # stop mesafesi %
    if sp <= 0:
        return None
    stop = ref * (1 - sp / 100) if yon == "LONG" else ref * (1 + sp / 100)
    hedef = ref * (1 + HEDEF / 100) if yon == "LONG" else ref * (1 - HEDEF / 100)
    son = min(gi + ufuk, len(b))
    if son - gi < 3:
        return None
    for j in range(gi, son):
        x = b[j]
        if yon == "LONG":
            if x["l"] <= stop:
                return -sp - MALIYET, "STOP", sp
            if x["h"] >= hedef:
                return HEDEF - MALIYET, "HEDEF", sp
        else:
            if x["h"] >= stop:
                return -sp - MALIYET, "STOP", sp
            if x["l"] <= hedef:
                return HEDEF - MALIYET, "HEDEF", sp
    c = b[son - 1]["c"]
    g = (c - ref) / ref * 100 if yon == "LONG" else (ref - c) / ref * 100
    return g - MALIYET, "SURE", sp


def oz(k):
    k = [x for x in k if x]
    if not k:
        return None
    g = [x[0] for x in k]
    sp = st.median([x[2] for x in k])
    return {"n": len(g), "ort": st.mean(g), "sh": st.pstdev(g) / len(g) ** 0.5 if len(g) > 1 else 0,
            "isabet": sum(1 for x in k if x[1] == "HEDEF") / len(g) * 100,
            "stop": sp, "basabas": sp / (HEDEF + sp) * 100}


def main():
    ol = json.load(open(os.path.join(BURA, "oruntu_olaylar.json")))
    bc, idxc, ge = {}, {}, []
    for o in ol:
        s = o["sym"]
        if s not in bc:
            p = os.path.join(CACHE, f"{s}.json")
            bc[s] = json.load(open(p)) if os.path.exists(p) else None
            if bc[s]:
                idxc[s] = {x["t"] // 3600000: i for i, x in enumerate(bc[s])}
        if not bc[s]:
            continue
        ms = int(datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M").astimezone().timestamp() * 1000)
        gi = idxc[s].get(ms // 3600000 + 1)
        if gi is not None:
            o["_b"], o["_gi"] = bc[s], gi
            ge.append(o)
    tsl = sorted(o["ts"] for o in ge)
    ORTA = tsl[len(tsl) // 2]
    print(f"LONG · hedef %{HEDEF} · {len(ge)} olay · 46 gun (tamami AYI/NOTR) · maliyet %{MALIYET}")
    print(f"basabas = stop% / ({HEDEF} + stop%)\n")

    STOPLAR = [("atr", 0.25), ("atr", 0.35), ("atr", 0.50), ("atr", 0.75), ("atr", 1.00),
               ("atr", 1.50), ("atr", 2.00), ("pct", 0.50), ("pct", 0.75), ("pct", 1.00),
               ("pct", 1.50)]
    print("=" * 104)
    print("STOP TARAMASI — isabet basabasi geciyor mu?")
    print("=" * 104)
    print(f"{'stop':>12}{'ufuk':>7}{'N':>7}{'stop med':>10}{'isabet':>9}{'basabas':>10}"
          f"{'FARK':>8}{'net %':>9}")
    print("-" * 104)
    en_iyi, en_deger = None, -99
    for tanim in STOPLAR:
        ad = f"{tanim[1]:.2f}xATR" if tanim[0] == "atr" else f"%{tanim[1]:.2f}"
        for uf in (6, 24, 72):
            a = oz([oyna(o["_b"], o["_gi"], tanim, uf) for o in ge])
            if not a:
                continue
            fark = a["isabet"] - a["basabas"]
            im = " *" if a["ort"] > 0 else ""
            print(f"{ad:>12}{uf:>6}s{a['n']:7d}{a['stop']:9.2f}%{a['isabet']:8.1f}%"
                  f"{a['basabas']:9.1f}%{fark:+8.1f}{a['ort']:+9.2f}{im}")
            if a["ort"] > en_deger:
                en_deger, en_iyi = a["ort"], (tanim, uf)
    print("-" * 104)
    print("  '*' = net pozitif · FARK = isabet - basabas (pozitifse hedef basabasi geciyor)")

    tanim, uf = en_iyi
    ad = f"{tanim[1]:.2f}xATR" if tanim[0] == "atr" else f"%{tanim[1]:.2f}"
    print(f"\n" + "=" * 104)
    print(f"EN IYI VARYANT: stop {ad} · ufuk {uf}s · net {en_deger:+.2f}%")
    print("=" * 104)
    A = oz([oyna(o["_b"], o["_gi"], tanim, uf) for o in ge if o["ts"] < ORTA])
    B = oz([oyna(o["_b"], o["_gi"], tanim, uf) for o in ge if o["ts"] >= ORTA])
    print(f"  ZAMAN BOLMESI:  A yarisi {A['ort']:+.2f}% (N={A['n']})   "
          f"B yarisi {B['ort']:+.2f}% (N={B['n']})")
    if not (A["ort"] > 0 and B["ort"] > 0):
        print("  >>> IKI YARIDA DA POZITIF DEGIL -> TARAMA ARTIGI, kullanilamaz. <<<")
    else:
        print("  >>> iki yarida da pozitif -> incelenmeye deger. <<<")

    print("\n  KOSUL KIRILIMI (ayni stop/ufuk):")
    KOS = [("TUM", lambda o: True),
           ("funding >= +0.05", lambda o: (o.get("funding") or 0) >= 0.05),
           ("funding >= +0.03", lambda o: (o.get("funding") or 0) >= 0.03),
           ("stage=HAZIRLANIYOR", lambda o: o.get("stage") == "HAZIRLANIYOR"),
           ("stage=BASLIYOR", lambda o: o.get("stage") == "BASLIYOR"),
           ("oi24 >= %10", lambda o: (o.get("oi24") or 0) >= 10),
           ("skor >= 45", lambda o: (o.get("score") or 0) >= 45),
           ("pos <= 0.25", lambda o: (o.get("pos") or 1) <= 0.25),
           ("vol_x >= 3", lambda o: (o.get("vol_x") or 0) >= 3),
           ("chg24 >= %10", lambda o: (o.get("chg24") or 0) >= 10)]
    print(f"  {'kosul':24}{'N':>7}{'isabet':>9}{'basabas':>10}{'net %':>9}{'A yari':>9}{'B yari':>9}")
    print("  " + "-" * 92)
    for kad, fn in KOS:
        alt = [o for o in ge if fn(o)]
        if len(alt) < 25:
            continue
        a = oz([oyna(o["_b"], o["_gi"], tanim, uf) for o in alt])
        aA = oz([oyna(o["_b"], o["_gi"], tanim, uf) for o in alt if o["ts"] < ORTA])
        aB = oz([oyna(o["_b"], o["_gi"], tanim, uf) for o in alt if o["ts"] >= ORTA])
        print(f"  {kad:24}{a['n']:7d}{a['isabet']:8.1f}%{a['basabas']:9.1f}%{a['ort']:+9.2f}"
              f"{(aA['ort'] if aA else 0):+9.2f}{(aB['ort'] if aB else 0):+9.2f}")

    print("\n" + "=" * 104)
    print("KARSILASTIRMA — ayni stop taramasi SHORT tarafinda (simetri)")
    print("=" * 104)
    print(f"{'stop':>12}{'ufuk':>7}{'isabet':>9}{'basabas':>10}{'net %':>9}")
    print("-" * 104)
    for tanim2 in (("atr", 0.35), ("atr", 0.75), ("atr", 1.50), ("pct", 1.00)):
        ad2 = f"{tanim2[1]:.2f}xATR" if tanim2[0] == "atr" else f"%{tanim2[1]:.2f}"
        for uf2 in (24, 72):
            a = oz([oyna(o["_b"], o["_gi"], tanim2, uf2, "SHORT") for o in ge])
            if a:
                print(f"{ad2:>12}{uf2:>6}s{a['isabet']:8.1f}%{a['basabas']:9.1f}%{a['ort']:+9.2f}")


if __name__ == "__main__":
    main()
