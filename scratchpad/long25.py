#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LONG %2.5 HEDEF (2026-08-10) — "long hedefini notr-ayi sezonunda %2.5 yapsak"

MANTIK: ayi/notr rejimde yukari hareketler kucuk ve hizla geri veriliyor; %10 hedef
ulasilamiyor (30 hucrede de negatif cikti). Kucuk hedef -> yuksek isabet.
AMA odeme de kucuk: basabas = stop% / (hedef% + stop%).
  stop %1.5 & hedef %2.5 -> basabas %37.5
  stop %3.0 & hedef %2.5 -> basabas %54.5   <- stop hedeften genisse cok zor
Bu yuzden STOP GENISLIGI burada belirleyici; iki stop varyanti birlikte olculur.

OLCUM:
  hedef duyarliligi : %1.5 / %2.0 / %2.5 / %3.0 / %5.0 (kullanicinin onerisi %2.5 ANA)
  stop varyanti     : A (botun) · 0.75xATR (dar) · 1.5xATR
  ufuk              : 24 ve 72 saat (kucuk hedef hizli tutulur)
  kirilim           : asama · kosul · rejim (F10 etiketi arsivde 'rejim' alaninda YOK,
                      bu yuzden BTC gunluk SMA20 ile tarihsel etiket uretilir)
Maliyet %0.09 gidis-donus.
"""
import json, os, statistics as st, datetime, collections

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h")
NBAR, MALIYET = 10, 0.09


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


def oyna(b, gi, yon, hedef_pct, stop_mod, ufuk):
    i = gi - 1
    if i < 30 or gi >= len(b):
        return None
    a = atr14(b, i)
    if not a or a <= 0:
        return None
    ref = b[gi]["o"]
    if stop_mod == "A":
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
    else:
        kat = float(stop_mod)
        stop = ref - kat * a if yon == "LONG" else ref + kat * a
    sp = abs(ref - stop) / ref * 100
    if sp <= 0:
        return None
    hedef = ref * (1 + hedef_pct / 100) if yon == "LONG" else ref * (1 - hedef_pct / 100)
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


def oz(k, hedef_pct):
    k = [x for x in k if x]
    if not k:
        return None
    g = [x[0] for x in k]
    sp = st.median([x[2] for x in k])
    return {"n": len(g), "ort": st.mean(g), "sh": st.pstdev(g) / len(g) ** 0.5 if len(g) > 1 else 0,
            "hedef": sum(1 for x in k if x[1] == "HEDEF") / len(g) * 100,
            "stop": sp, "basabas": sp / (hedef_pct + sp) * 100}


def main():
    ol = json.load(open(os.path.join(BURA, "oruntu_olaylar.json")))
    bc, idxc = {}, {}
    ge = []
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
        if gi is None:
            continue
        o["_b"], o["_gi"] = bc[s], gi
        ge.append(o)
    print(f"Olay: {len(ge)} · radar arsivi 46 gun (tamami AYI/NOTR) · maliyet %{MALIYET}\n")
    tsl = sorted(o["ts"] for o in ge)
    ORTA = tsl[len(tsl) // 2]

    print("=" * 108)
    print("1) HEDEF DUYARLILIGI — LONG (stop: botun A-varyanti, ufuk 72s)")
    print("=" * 108)
    print(f"{'hedef':>8}{'N':>7}{'net %':>10}{'isabet':>9}{'basabas':>10}{'stop med':>10}"
          f"{'A yari':>10}{'B yari':>10}")
    print("-" * 108)
    for h in (1.5, 2.0, 2.5, 3.0, 5.0, 10.0):
        k = [oyna(o["_b"], o["_gi"], "LONG", h, "A", 72) for o in ge]
        a = oz(k, h)
        kA = oz([oyna(o["_b"], o["_gi"], "LONG", h, "A", 72) for o in ge if o["ts"] < ORTA], h)
        kB = oz([oyna(o["_b"], o["_gi"], "LONG", h, "A", 72) for o in ge if o["ts"] >= ORTA], h)
        yildiz = "  <- onerilen" if h == 2.5 else ""
        print(f"%{h:>6.1f}{a['n']:7d}{a['ort']:+10.2f}{a['hedef']:8.1f}%{a['basabas']:9.1f}%"
              f"{a['stop']:9.2f}%{(kA['ort'] if kA else 0):+10.2f}{(kB['ort'] if kB else 0):+10.2f}{yildiz}")

    print("\n" + "=" * 108)
    print("2) STOP VARYANTI x UFUK — hedef %2.5 LONG")
    print("=" * 108)
    print(f"{'stop':>14}{'ufuk':>7}{'N':>7}{'net %':>10}{'isabet':>9}{'basabas':>10}{'stop med':>10}")
    print("-" * 108)
    for sm, sad in (("A", "A (botun)"), ("0.75", "0.75xATR"), ("1.5", "1.5xATR")):
        for uf in (24, 72):
            k = [oyna(o["_b"], o["_gi"], "LONG", 2.5, sm, uf) for o in ge]
            a = oz(k, 2.5)
            if a:
                print(f"{sad:>14}{uf:>6}s{a['n']:7d}{a['ort']:+10.2f}{a['hedef']:8.1f}%"
                      f"{a['basabas']:9.1f}%{a['stop']:9.2f}%")

    print("\n" + "=" * 108)
    print("3) EN IYI STOP ile ASAMA ve KOSUL KIRILIMI (hedef %2.5)")
    print("=" * 108)
    # en iyi stop varyantini sec (sadece raporlama icin; kural yapilmiyor)
    en = max((("A", 72), ("0.75", 72), ("1.5", 72), ("0.75", 24), ("A", 24), ("1.5", 24)),
             key=lambda sv: (oz([oyna(o["_b"], o["_gi"], "LONG", 2.5, sv[0], sv[1]) for o in ge], 2.5)
                             or {"ort": -9})["ort"])
    print(f"  (en iyi: stop={en[0]} · ufuk={en[1]}s)")
    KOS = [("TUM", lambda o: True),
           ("stage=HAZIRLANIYOR", lambda o: o.get("stage") == "HAZIRLANIYOR"),
           ("stage=BASLIYOR", lambda o: o.get("stage") == "BASLIYOR"),
           ("stage=izle", lambda o: o.get("stage") == "izle"),
           ("funding >= +0.05", lambda o: (o.get("funding") or 0) >= 0.05),
           ("funding <= -0.05", lambda o: (o.get("funding") or 0) <= -0.05),
           ("oi24 >= %10", lambda o: (o.get("oi24") or 0) >= 10),
           ("oi24 <= -%10", lambda o: (o.get("oi24") or 0) <= -10),
           ("skor >= 45", lambda o: (o.get("score") or 0) >= 45),
           ("pos <= 0.25 (dip)", lambda o: (o.get("pos") or 1) <= 0.25),
           ("pos >= 0.85 (tepe)", lambda o: (o.get("pos") or 0) >= 0.85),
           ("vol_x >= 3", lambda o: (o.get("vol_x") or 0) >= 3),
           ("comp < 0.65 (sikisik)", lambda o: (o.get("comp") or 9) < 0.65),
           ("chg24 <= -%10 (dusmus)", lambda o: (o.get("chg24") or 0) <= -10),
           ("chg24 >= %10 (pump)", lambda o: (o.get("chg24") or 0) >= 10)]
    print(f"{'kosul':26}{'N':>7}{'LONG net %':>12}{'isabet':>9}{'basabas':>10}{'A yari':>10}{'B yari':>10}")
    print("-" * 108)
    for ad, fn in KOS:
        alt = [o for o in ge if fn(o)]
        if len(alt) < 25:
            continue
        a = oz([oyna(o["_b"], o["_gi"], "LONG", 2.5, en[0], en[1]) for o in alt], 2.5)
        A = oz([oyna(o["_b"], o["_gi"], "LONG", 2.5, en[0], en[1]) for o in alt if o["ts"] < ORTA], 2.5)
        B = oz([oyna(o["_b"], o["_gi"], "LONG", 2.5, en[0], en[1]) for o in alt if o["ts"] >= ORTA], 2.5)
        print(f"{ad:26}{a['n']:7d}{a['ort']:+12.2f}{a['hedef']:8.1f}%{a['basabas']:9.1f}%"
              f"{(A['ort'] if A else 0):+10.2f}{(B['ort'] if B else 0):+10.2f}")

    print("\n" + "=" * 108)
    print("4) KARSILASTIRMA — ayni hedefle SHORT ne veriyor? (simetri)")
    print("=" * 108)
    for h in (2.5, 10.0):
        kL = oz([oyna(o["_b"], o["_gi"], "LONG", h, "A", 72) for o in ge], h)
        kS = oz([oyna(o["_b"], o["_gi"], "SHORT", h, "A", 72) for o in ge], h)
        print(f"  hedef %{h:<5} LONG {kL['ort']:+6.2f}% (isabet %{kL['hedef']:.1f})   "
              f"SHORT {kS['ort']:+6.2f}% (isabet %{kS['hedef']:.1f})")


if __name__ == "__main__":
    main()
