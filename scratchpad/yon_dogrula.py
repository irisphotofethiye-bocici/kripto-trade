#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""YÖN SİNYALİ DOĞRULAMA (2026-08-10) — bulunan yön hücreleri ticaret mekaniğinde yaşıyor mu?

YON AVI SONUCU (ham ileri getiri, rel24 = coin - BTC, 6790 olay, taban -0.46%):
  Alti KARARLI yon olcusu (isaret iki yarida da ayni):
    MA50 mesafesi   ust dilim -2.10 / alt -0.35  -> yon gucu -1.76  (A -1.70 / B -1.87)
    taker alis payi ust -1.57 / alt +0.00        -> -1.57  (A -2.10 / B -1.23)
    radar skoru     ust -1.68 / alt -0.13        -> -1.55
    son 24 saat %   ust -2.16 / alt -0.72        -> -1.44
    MA200 mesafesi  ust -1.83 / alt -0.40        -> -1.43
    oi24            ust -1.68 / alt -0.77        -> -0.91
  Hepsi ayni yone bakiyor: YUKSEK deger -> BTC'nin ALTINDA performans (SHORT tarafi).

  LONG TARAFI (dusuk %20 kesisimleri) — ilk POZITIF hucreler:
    MA50 dusuk + fiyat YUKSEK        rel24 +0.89  N=125  (A +0.72 / B +1.12)  <- iki yarida da +
    fiyat YUKSEK + chg24 dusuk       rel24 +0.72  N=119  (A +0.47 / B +1.31)  <- iki yarida da +

  REFERANS: A+B kapisi rel24 -4.38% (taban -0.46) -> en guclu yon sinyali, farkla.

BU SCRIPT: yon sinyali != kar. Ayni hucreler botun GERCEK mekanigiyle (A-stop, hedef,
fitil, maliyet %0.09) test edilir. Yon gucu stop genislemesini asiyorsa kar cikar.
"""
import json, os, statistics as st, datetime

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h")
NBAR, MALIYET = 10, 0.09


def atr(b, i, n=14):
    if i < n:
        return None
    tr = []
    for j in range(i - n + 1, i + 1):
        p = b[j - 1]["c"]
        tr.append(max(b[j]["h"] - b[j]["l"], abs(b[j]["h"] - p), abs(p - b[j]["l"])))
    return st.mean(tr)


def swings2(b, i, left=3, right=3, geri=100):
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


def islem(b, gi, hedef_pct, ufuk, yon):
    i = gi - 1
    if i < 200 or gi >= len(b):
        return None
    a = atr(b, i)
    if not a or a <= 0:
        return None
    ref = b[gi]["o"]
    hi, lo = swings2(b, i)
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
        hedef = ref * (1 + hedef_pct / 100)
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
        hedef = ref * (1 - hedef_pct / 100)
    sp = abs(ref - stop) / ref * 100
    if sp <= 0:
        return None
    son = min(gi + ufuk, len(b))
    if son - gi < 4:
        return None
    for j in range(gi, son):
        x = b[j]
        if yon == "LONG":
            if x["l"] <= stop:
                return -sp - MALIYET, "STOP", sp
            if x["h"] >= hedef:
                return hedef_pct - MALIYET, "HEDEF", sp
        else:
            if x["h"] >= stop:
                return -sp - MALIYET, "STOP", sp
            if x["l"] <= hedef:
                return hedef_pct - MALIYET, "HEDEF", sp
    c = b[son - 1]["c"]
    g = (c - ref) / ref * 100 if yon == "LONG" else (ref - c) / ref * 100
    return g - MALIYET, "SURE", sp


def oz(k, hedef):
    k = [x for x in k if x]
    if not k:
        return None
    g = [x[0] for x in k]
    sp = st.median([x[2] for x in k])
    return {"n": len(g), "ort": st.mean(g), "isabet": sum(1 for x in k if x[1] == "HEDEF") / len(g) * 100,
            "basabas": sp / (hedef + sp) * 100, "stop": sp}


def main():
    import yon_avi
    ge = yon_avi.yukle()
    tsl = sorted(o["ts"] for o in ge)
    ORTA = tsl[len(tsl) // 2]
    bc, idxc = {}, {}
    for o in ge:
        s = o["sym"]
        if s not in bc:
            p = os.path.join(CACHE, f"{s}.json")
            bc[s] = json.load(open(p)) if os.path.exists(p) else None
            if bc[s]:
                idxc[s] = {x["t"] // 3600000: i for i, x in enumerate(bc[s])}
        if not bc[s]:
            continue
        ms = int(datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M").astimezone().timestamp() * 1000)
        o["_b"], o["_gi"] = bc[s], idxc[s].get(ms // 3600000)

    def q(alan, p):
        v = sorted(o[alan] for o in ge if o.get(alan) is not None)
        return v[int(len(v) * p)]

    ma50_alt, fiyat_ust, chg24_alt = q("ma50_mesafe", 0.2), q("fiyat_log", 0.8), q("chg24", 0.2)
    ma50_ust, fiyat_alt = q("ma50_mesafe", 0.8), q("fiyat_log", 0.2)

    HUCRE = [
        ("LONG: MA50 dusuk + fiyat YUKSEK", "LONG",
         lambda o: o["ma50_mesafe"] <= ma50_alt and o["fiyat_log"] >= fiyat_ust),
        ("LONG: fiyat YUKSEK + chg24 dusuk", "LONG",
         lambda o: o["fiyat_log"] >= fiyat_ust and (o.get("chg24") or 0) <= chg24_alt),
        ("LONG: MA50 dusuk (tek)", "LONG", lambda o: o["ma50_mesafe"] <= ma50_alt),
        ("LONG: fiyat YUKSEK (tek)", "LONG", lambda o: o["fiyat_log"] >= fiyat_ust),
        ("SHORT: fiyat DUSUK (tek)", "SHORT", lambda o: o["fiyat_log"] <= fiyat_alt),
        ("SHORT: MA50 YUKSEK + fiyat DUSUK", "SHORT",
         lambda o: o["ma50_mesafe"] >= ma50_ust and o["fiyat_log"] <= fiyat_alt),
        ("SHORT: A+B (canlidaki kapi)", "SHORT",
         lambda o: (o.get("funding") or 0) <= -0.05 and (o.get("oi24") or 0) >= 10),
        ("SHORT: A+B + fiyat DUSUK", "SHORT",
         lambda o: (o.get("funding") or 0) <= -0.05 and (o.get("oi24") or 0) >= 10
         and o["fiyat_log"] <= fiyat_alt),
        ("KONTROL: tum olaylar LONG", "LONG", lambda o: True),
        ("KONTROL: tum olaylar SHORT", "SHORT", lambda o: True),
    ]
    print("=" * 116)
    print("YÖN HÜCRELERİ TİCARET MEKANİĞİNDE — botun A-stopu, maliyet %0.09")
    print("=" * 116)
    for hedef, ufuk in ((2.5, 24), (10.0, 72)):
        print(f"\n### hedef %{hedef} · ufuk {ufuk} saat")
        print(f"{'hucre':38}{'N':>6}{'net %':>9}{'isabet':>9}{'basabas':>10}"
              f"{'stop%':>8}{'A yari':>9}{'B yari':>9}")
        print("-" * 116)
        for ad, yon, fn in HUCRE:
            sec = [o for o in ge if o.get("_gi") is not None and fn(o)]
            if len(sec) < 60:
                continue
            k = [islem(o["_b"], o["_gi"] + 1, hedef, ufuk, yon) for o in sec]
            a = oz(k, hedef)
            A = oz([islem(o["_b"], o["_gi"] + 1, hedef, ufuk, yon) for o in sec if o["ts"] < ORTA], hedef)
            B = oz([islem(o["_b"], o["_gi"] + 1, hedef, ufuk, yon) for o in sec if o["ts"] >= ORTA], hedef)
            if not a:
                continue
            im = " *" if a["ort"] > 0 else ""
            print(f"{ad:38}{a['n']:6d}{a['ort']:+9.2f}{a['isabet']:8.1f}%{a['basabas']:9.1f}%"
                  f"{a['stop']:7.2f}%{(A['ort'] if A else 0):+9.2f}{(B['ort'] if B else 0):+9.2f}{im}")
    print("\n  '*' = net pozitif")


if __name__ == "__main__":
    main()
