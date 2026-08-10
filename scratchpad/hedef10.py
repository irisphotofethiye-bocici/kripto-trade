#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""%10 HEDEF ÖLÇÜMÜ (2026-08-10) — "long da ara, %10 kazanc hedefle, asamayi bul"

Kullanici: "long islemde acsin sadece short degil · long islem ara, gainers'da onemli olan bu ·
kazananlarin gosterdigi ozellikler hangi ASAMADA ortusuyor bunu bul · yuzde 10 kazanc hedefle,
ona gore olc · ayni anda ayni sinyalleri uretmesi onemli · pumplara bakalim"

NE DEGISTI: onceki tum olcumler 2R hedefliydi. Simdi hedef SABIT %10.
  Bu odeme profilini tamamen degistirir: stop medyani ~%1.4-4 -> %10 hedef 2.5-7R uzakta.
  Kazanma orani DUSER ama tek kazanc BUYUR. Basabas orani = stop% / (10 + stop%).
  Ornek: stop %2 ise basabas %16.7 · stop %5 ise %33.3.

MEKANIK: giris = kaydin ertesi 1h barinin acilisi · stop = botun A-varyanti ·
  hedef = giris ±%10 · ufuk 72 saat · fitil bazli · ayni barda ikisi de -> STOP ·
  maliyet %0.09 (gidis-donus taker) dusuldu.

CIKTI:
  1. LONG ve SHORT icin ASAMA (stage) kirilimi — "hangi asamada ortusuyor"
  2. Her kosulun LONG/SHORT net beklentisi (%) — es zamanli sinyal aramak icin
  3. Kosullarin KESISIMI (ayni anda uretilmesi) — asama x kosul matrisi
  4. PUMP OLAYLARI (tum evren 570 sembol, 1422 tetik) ayni %10 hedefle
"""
import json, os, statistics as st, collections

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h")
UFUK, NBAR = 72, 10
MALIYET_PCT = 0.09          # gidis-donus taker
HEDEF_PCT = 10.0


def atr14(b, i):
    if i < 14:
        return None
    tr = []
    for j in range(i - 13, i + 1):
        p = b[j - 1]["c"]
        tr.append(max(b[j]["h"] - b[j]["l"], abs(b[j]["h"] - p), abs(p - b[j]["l"])))
    return st.mean(tr)


def swings(b, i, left=3, right=3, geri=100):
    bas = max(left, i - geri)
    hi, lo = [], []
    for j in range(bas, i - right + 1):
        w = b[j - left:j + right + 1]
        if not w:
            continue
        if b[j]["h"] == max(x["h"] for x in w):
            hi.append(b[j]["h"])
        if b[j]["l"] == min(x["l"] for x in w):
            lo.append(b[j]["l"])
    return hi, lo


def oyna10(b, gi, yon):
    """-> (net_getiri_pct, sonuc, stop_pct) | None.  sonuc: HEDEF / STOP / SURE"""
    i = gi - 1
    if i < 30 or gi >= len(b):
        return None
    a = atr14(b, i)
    if not a or a <= 0:
        return None
    ref = b[gi]["o"]
    hi, lo = swings(b, i)
    if yon == "LONG":
        sup = max([x for x in lo if x < ref], default=None)
        ad = []
        if sup is not None and (ref - sup) <= 3 * a:
            ad.append(sup - 0.25 * a)
        nb = min(x["l"] for x in b[max(0, i - NBAR + 1):i + 1])
        if nb < ref:
            ad.append(nb - 0.25 * a)
        ad.append(ref - 1.5 * a)
        gec = [s for s in ad if s < ref]
        stop = max(gec) if gec else ref - 1.5 * a
        hedef = ref * (1 + HEDEF_PCT / 100)
    else:
        res = min([x for x in hi if x > ref], default=None)
        ad = []
        if res is not None and (res - ref) <= 3 * a:
            ad.append(res + 0.25 * a)
        nb = max(x["h"] for x in b[max(0, i - NBAR + 1):i + 1])
        if nb > ref:
            ad.append(nb + 0.25 * a)
        ad.append(ref + 1.5 * a)
        gec = [s for s in ad if s > ref]
        stop = min(gec) if gec else ref + 1.5 * a
        hedef = ref * (1 - HEDEF_PCT / 100)
    stop_pct = abs(ref - stop) / ref * 100
    if stop_pct <= 0:
        return None
    son = min(gi + UFUK, len(b))
    if son - gi < 6:
        return None
    for j in range(gi, son):
        x = b[j]
        if yon == "LONG":
            if x["l"] <= stop:
                return -stop_pct - MALIYET_PCT, "STOP", stop_pct
            if x["h"] >= hedef:
                return HEDEF_PCT - MALIYET_PCT, "HEDEF", stop_pct
        else:
            if x["h"] >= stop:
                return -stop_pct - MALIYET_PCT, "STOP", stop_pct
            if x["l"] <= hedef:
                return HEDEF_PCT - MALIYET_PCT, "HEDEF", stop_pct
    c = b[son - 1]["c"]
    g = (c - ref) / ref * 100 if yon == "LONG" else (ref - c) / ref * 100
    return g - MALIYET_PCT, "SURE", stop_pct


def oz(kayitlar):
    if not kayitlar:
        return None
    g = [k[0] for k in kayitlar]
    hed = sum(1 for k in kayitlar if k[1] == "HEDEF")
    sp = st.median([k[2] for k in kayitlar])
    basabas = sp / (HEDEF_PCT + sp) * 100
    return {"n": len(g), "ort": st.mean(g), "sh": st.pstdev(g) / len(g) ** 0.5 if len(g) > 1 else 0,
            "hedef_pct": hed / len(g) * 100, "stop_med": sp, "basabas": basabas}


def yaz(ad, kL, kS, genis=30):
    L, S = oz(kL), oz(kS)
    if not L:
        print(f"  {ad:<{genis}} N=0")
        return
    print(f"  {ad:<{genis}} N={L['n']:5d} | LONG {L['ort']:+6.2f}% (hedef %{L['hedef_pct']:4.1f}, "
          f"basabas %{L['basabas']:4.1f}) | SHORT {S['ort']:+6.2f}% (hedef %{S['hedef_pct']:4.1f})")


def main():
    ol = json.load(open(os.path.join(BURA, "oruntu_olaylar.json")))
    import datetime
    bc, sonuc = {}, []
    for o in ol:
        sym = o["sym"]
        if sym not in bc:
            p = os.path.join(CACHE, f"{sym}.json")
            bc[sym] = json.load(open(p)) if os.path.exists(p) else None
        b = bc[sym]
        if not b:
            continue
        if "_idx" not in o:
            pass
        ms = int(datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M").astimezone().timestamp() * 1000)
        idx = bc.setdefault("_i_" + sym, {x["t"] // 3600000: i for i, x in enumerate(b)})
        gi = idx.get(ms // 3600000 + 1)
        if gi is None:
            continue
        L = oyna10(b, gi, "LONG")
        S = oyna10(b, gi, "SHORT")
        if L and S:
            o["L10"], o["S10"] = L, S
            sonuc.append(o)
    ge = sonuc
    print("=" * 112)
    print(f"%10 HEDEF ÖLÇÜMÜ — {len(ge)} olay · radar arşivi 46 gün · maliyet %{MALIYET_PCT} düşüldü")
    print("=" * 112)
    yaz("TÜM OLAYLAR", [o["L10"] for o in ge], [o["S10"] for o in ge])

    print("\n### AŞAMA (stage) KIRILIMI — 'hangi aşamada örtüşüyor'")
    for sg in ("BASLIYOR", "HAZIRLANIYOR", "izle"):
        alt = [o for o in ge if o.get("stage") == sg]
        yaz(sg, [o["L10"] for o in alt], [o["S10"] for o in alt])

    print("\n### TEK KOŞULLAR")
    KOS = [
        ("funding <= -0.05", lambda o: (o.get("funding") or 0) <= -0.05),
        ("funding >= +0.05", lambda o: (o.get("funding") or 0) >= 0.05),
        ("oi24 >= %10", lambda o: (o.get("oi24") or 0) >= 10),
        ("oi24 <= -%10", lambda o: (o.get("oi24") or 0) <= -10),
        ("oi3 >= %3", lambda o: (o.get("oi3") or 0) >= 3),
        ("skor >= 45", lambda o: (o.get("score") or 0) >= 45),
        ("vol_x >= 3", lambda o: (o.get("vol_x") or 0) >= 3),
        ("comp < 0.65 (sikisik)", lambda o: (o.get("comp") or 9) < 0.65),
        ("pos >= 0.85", lambda o: (o.get("pos") or 0) >= 0.85),
        ("pos <= 0.25", lambda o: (o.get("pos") or 1) <= 0.25),
        ("chg24 >= %20 (pumplamis)", lambda o: (o.get("chg24") or 0) >= 20),
        ("chg24 <= -%10", lambda o: (o.get("chg24") or 0) <= -10),
        ("last3 >= %4", lambda o: (o.get("last3") or 0) >= 4),
    ]
    for ad, fn in KOS:
        alt = [o for o in ge if fn(o)]
        if len(alt) >= 25:
            yaz(ad, [o["L10"] for o in alt], [o["S10"] for o in alt])

    print("\n### AŞAMA × KOŞUL — es zamanli sinyal (LONG net %)")
    print(f"  {'kosul':28}{'BASLIYOR':>22}{'HAZIRLANIYOR':>22}{'izle':>20}")
    print("  " + "-" * 90)
    for ad, fn in KOS:
        hucre = []
        for sg in ("BASLIYOR", "HAZIRLANIYOR", "izle"):
            alt = [o for o in ge if fn(o) and o.get("stage") == sg]
            x = oz([o["L10"] for o in alt])
            hucre.append(f"{x['ort']:+6.2f}% (N={x['n']:4d})" if x and x["n"] >= 10 else f"{'—':>15}")
        print(f"  {ad:28}{hucre[0]:>22}{hucre[1]:>22}{hucre[2]:>20}")

    json.dump([{k: v for k, v in o.items() if not k.startswith("_")} for o in ge],
              open(os.path.join(BURA, "hedef10_olaylar.json"), "w"))
    print("\n-> scratchpad/hedef10_olaylar.json")


if __name__ == "__main__":
    main()
