#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A+B'nin FUNDING BACAGI — 2 yillik sinav (2026-08-12)
On-kayit: fikir-defteri.md, commit 80e8bfc (KOSTURULMADAN once)

SINANAN: funding <= -0.05 %/8s  ->  SHORT.
KISIT (on-kayitta yazili): OI gecmisi ~30 gun oldugu icin `oi24 >= %10` bacagi
2 yilda kurulamaz. Yani kapinin TAMAMI degil TASIYICI BACAGI sinaniyor.
Arsivde: funding tek basina +0.259R (N=508) · kesisim +0.375R (N=206).

Mekanik canlinin aynisi: A-stop · Wilder ATR · sabit %10 hedef · 72s · maliyet %0.13 ·
giris sonraki barin acilisi · pump kapisi · hacim tabani $3M/24s · seyreltme 24 bar.
Kontrol: REJIM-ESLESMIS rastgele barlar (yukselen piyasada her short farkli davranir).
Salt-okunur.
"""
import json, os, sys, random, statistics as stx, collections, datetime, bisect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olcum_ortak as oo

BURA = os.path.dirname(os.path.abspath(__file__))
KLINE = os.path.join(BURA, "klines_1h_uzun")
FUND = os.path.join(BURA, "funding_gecmis")
HEDEF_PCT, UFUK = 10.0, 72
STOP_NBAR, ATR_N = 10, 14
RISK_PCT, MARJIN_PCT, KALD_MAX = 0.015, 0.10, 10
ISINMA, SEYRELT = 220, 24
FUND_ESIK, PUMP, MIN_VOL = -0.05, 20.0, 3_000_000
random.seed(41)


def atr_serisi(b, n=ATR_N):
    out, tr = [None] * len(b), [None] * len(b)
    for i in range(1, len(b)):
        pc = b[i - 1]["c"]
        tr[i] = max(b[i]["h"] - b[i]["l"], abs(b[i]["h"] - pc), abs(pc - b[i]["l"]))
    if len(b) <= n:
        return out
    a = sum(tr[1:n + 1]) / n
    out[n] = a
    for i in range(n + 1, len(b)):
        a = (a * (n - 1) + tr[i]) / n
        out[i] = a
    return out


def stop_hesapla(b, si, ref, a):
    bas = max(3, si - 100)
    hi = []
    for j in range(bas, si - 2):
        w = b[j - 3:j + 4]
        if w and b[j]["h"] == max(x["h"] for x in w):
            hi.append(b[j]["h"])
    res = min([x for x in hi if x > ref], default=None)
    ad = []
    if res is not None and (res - ref) <= 3 * a:
        ad.append(res + 0.25 * a)
    nb = max(x["h"] for x in b[max(0, si - STOP_NBAR + 1):si + 1])
    if nb > ref:
        ad.append(nb + 0.25 * a)
    ad.append(ref + 1.5 * a)
    gec = [s for s in ad if s > ref]
    return min(gec) if gec else ref + 1.5 * a


def islem(b, atrs, si):
    gi = si + 1
    if si < ISINMA or gi >= len(b) or not atrs[si]:
        return None
    ref = b[gi]["o"]
    if ref <= 0:
        return None
    stop = stop_hesapla(b, si, ref, atrs[si])
    sp = (stop - ref) / ref * 100
    if sp <= 0:
        return None
    son = min(gi + UFUK, len(b))
    if son - gi < 4:
        return None
    hedef = ref * (1 - HEDEF_PCT / 100)
    for j in range(gi, son):
        x = b[j]
        if x["h"] >= stop:
            return -sp - oo.MALIYET, "STOP", sp
        if x["l"] <= hedef:
            return HEDEF_PCT - oo.MALIYET, "HEDEF", sp
    c = b[son - 1]["c"]
    return (ref - c) / ref * 100 - oo.MALIYET, "SURE", sp


def btc_rejim():
    b = json.load(open(os.path.join(KLINE, "BTC.json"), encoding="utf-8"))
    c = [x["c"] for x in b]
    pen, out = 720, {}
    for i in range(pen, len(b)):
        g = (c[i] / c[i - pen] - 1) * 100
        out[b[i]["t"] // 3600000] = "BOGA" if g >= 15 else ("AYI" if g <= -15 else "NOTR")
    return out


def main():
    rej = btc_rejim()
    dosyalar = sorted(f for f in os.listdir(KLINE) if f.endswith(".json"))
    sinyal, kontrol = [], []
    eksik = 0
    for n, f in enumerate(dosyalar, 1):
        if f == "BTC.json":
            continue
        sym = f[:-5]
        fy = os.path.join(FUND, sym + ".json")
        if not os.path.exists(fy):
            eksik += 1
            continue
        try:
            b = json.load(open(os.path.join(KLINE, f), encoding="utf-8"))
            fr = json.load(open(fy, encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ISINMA + 120 or not fr:
            continue
        ft = [x["t"] for x in fr]
        c = [x["c"] for x in b]
        qv = [x.get("qv", 0.0) for x in b]
        atrs = atr_serisi(b)
        son = -10 ** 9
        for i in range(ISINMA, len(b) - UFUK - 2):
            if not atrs[i] or c[i - 24] <= 0:
                continue
            if sum(qv[i - 23:i + 1]) < MIN_VOL:
                continue
            # o bara kadarki EN GUNCEL funding (ileriye bakma yok)
            k = bisect.bisect_right(ft, b[i]["t"]) - 1
            if k < 0:
                continue
            if fr[k]["r"] > FUND_ESIK:
                continue
            if (c[i] / c[i - 24] - 1) * 100 >= PUMP:
                continue
            if i - son < SEYRELT:
                continue
            son = i
            sinyal.append({"sym": sym, "b": b, "atrs": atrs, "i": i, "t": b[i]["t"],
                           "rej": rej.get(b[i]["t"] // 3600000), "f": fr[k]["r"]})
        # rejim-eslesmis kontrol
        for _ in range(max(2, (len(b) - ISINMA) // 400)):
            i = random.randint(ISINMA, len(b) - UFUK - 3)
            if not atrs[i] or sum(qv[i - 23:i + 1]) < MIN_VOL:
                continue
            kontrol.append({"sym": sym, "b": b, "atrs": atrs, "i": i, "t": b[i]["t"],
                            "rej": rej.get(b[i]["t"] // 3600000)})
        if n % 150 == 0:
            print(f"  {n}/{len(dosyalar)} ...", flush=True)

    if not sinyal:
        print("SINYAL YOK — funding verisi eksik olabilir"); return
    tl = sorted(o["t"] for o in sinyal)
    ORTA = tl[len(tl) // 2]

    print("\n" + "=" * 112)
    print("A+B'nin FUNDING BACAGI — 2 yillik sinav (funding <= -0.05 %/8s -> SHORT)")
    print("=" * 112)
    print(f"Sinyal {len(sinyal)} · {len(set(o['sym'] for o in sinyal))} ayri sembol · "
          f"kontrol {len(kontrol)} · funding dosyasi eksik {eksik} sembol")
    print(f"Mekanik: A-stop · Wilder ATR · hedef %{HEDEF_PCT} · {UFUK}s · maliyet %{oo.MALIYET}\n")

    def hesapla(sec):
        kay, sem = [], []
        for o in sec:
            r = islem(o["b"], o["atrs"], o["i"])
            if r:
                boy = min(RISK_PCT / (r[2] / 100.0), MARJIN_PCT * KALD_MAX)
                kay.append((r[0] * boy, r[1], r[2], o["t"])); sem.append(o["sym"])
        if len(kay) < 40:
            return None
        a = oo.ozet([k[0] for k in kay], sem, asgari=40)
        if a:
            a["isabet"] = sum(1 for k in kay if k[1] == "HEDEF") / len(kay) * 100
            a["stop"] = stx.median([k[2] for k in kay])
            a["A"] = stx.mean([k[0] for k in kay if k[3] < ORTA] or [0])
            a["B"] = stx.mean([k[0] for k in kay if k[3] >= ORTA] or [0])
        return a

    print(f"{'kume':28}{'N':>7}{'sermaye%':>11}{'t':>7}{'isabet':>8}{'stop~':>7}"
          f"{'A yari':>9}{'B yari':>9}{'sembol':>8}{'t_kume':>8}")
    print("-" * 112)
    s = hesapla(sinyal); k = hesapla(kontrol)
    for ad, a in (("FUNDING <= -0.05 (sinyal)", s), ("KONTROL rastgele", k)):
        if not a:
            continue
        print(f"{ad:28}{a['n']:7d}{a['ort']:+11.3f}{a['t']:+7.2f}{a['isabet']:7.1f}%"
              f"{a['stop']:6.2f}%{a['A']:+9.3f}{a['B']:+9.3f}{a['ayri_sembol']:8d}"
              f"{a.get('t_kume', 0):+8.2f}")
    if s and k:
        print("-" * 112)
        print(f"{'FARK (sinyal - kontrol)':28}{'':7}{s['ort']-k['ort']:+11.3f}")

    print("\n" + "=" * 112)
    print("REJIME GORE (rejim-eslesmis kontrolle)")
    print("=" * 112)
    print(f"{'rejim':10}{'N':>7}{'sinyal%':>11}{'t':>7}{'KONTROL%':>11}{'FARK':>9}{'isabet':>9}")
    print("-" * 112)
    for r in ("BOGA", "NOTR", "AYI"):
        a = hesapla([o for o in sinyal if o["rej"] == r])
        kk = hesapla([o for o in kontrol if o["rej"] == r])
        if not a or not kk:
            continue
        print(f"{r:10}{a['n']:7d}{a['ort']:+11.3f}{a['t']:+7.2f}{kk['ort']:+11.3f}"
              f"{a['ort']-kk['ort']:+9.3f}{a['isabet']:8.1f}%")

    print("\n" + "=" * 112)
    print("GECME OLCUTU (on-kayitli)")
    print("=" * 112)
    if s and k:
        c1 = s["ort"] > 0
        c2 = s["ort"] > k["ort"]
        c3 = s["A"] > 0 and s["B"] > 0
        rj = {}
        for r in ("BOGA", "AYI"):
            a = hesapla([o for o in sinyal if o["rej"] == r])
            rj[r] = (a["ort"] > 0) if a else None
        c4 = all(v is not False for v in rj.values())
        print(f"  1) net > 0                    : {'EVET' if c1 else 'HAYIR'}  ({s['ort']:+.3f})")
        print(f"  2) kontrolu yener             : {'EVET' if c2 else 'HAYIR'}  "
              f"(fark {s['ort']-k['ort']:+.3f})")
        print(f"  3) iki zaman yarisi da +      : {'EVET' if c3 else 'HAYIR'}  "
              f"(A {s['A']:+.3f} / B {s['B']:+.3f})")
        print(f"  4) BOGA ve AYI'da cokme yok   : {'EVET' if c4 else 'HAYIR'}  "
              f"(boga {rj.get('BOGA')} · ayi {rj.get('AYI')})")
        print(f"\n  ->  {'GECTI' if all((c1, c2, c3, c4)) else 'KALDI'}")
    print("\n  SINIR: oi24 bacagi yok (OI gecmisi ~30 gun). Bu, kapinin TAMAMI degil")
    print("  TASIYICI BACAGIDIR. Arsivde funding tek 0.259R, kesisim 0.375R idi.")


if __name__ == "__main__":
    main()
