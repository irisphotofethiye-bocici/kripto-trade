#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A+B — FONLAMA MALIYETI DAHIL 2 yillik sinav (2026-08-13)
On-kayit: fikir-defteri.md, commit 437d0b7 (KOSTURULMADAN once)

NEDEN: canlida fonlama yayindan beri -189.05 $ cikti, su an gunde -100 $ akiyor
  (hesabin ~%1'i/gun). A+B'nin onceki 2 yillik olcumunde deftere "funding maliyeti
  eklenmedi" yazilmisti — o bosluk burada kapaniyor.

FONLAMA MUHASEBESI (canli funding_uygula ile AYNI isaret kurali):
  testbot: maliyet = notional * oran * isaret ; equity -= maliyet   (isaret: LONG +1)
  -> pozisyonun P&L katkisi (% olarak) = -(oran * isaret)
  -> SHORT icin (isaret=-1): katki = +oran. Oran NEGATIFSE ODERSIN.
  A+B kapisi oran <= -0.05 secip SHORT actigi icin bu HER ZAMAN bir MALIYET.

  Her 8 saatlik fonlama ani icin gercek TARIHSEL oran uygulanir (funding_gecmis).
  Yalnizca giris ile cikis ARASINDAKI anlar sayilir.

BASITLESTIRME (acikca): fonlama GIRIS notional'i uzerinden hesaplanir. Gercekte
  notional fiyatla birlikte degisir; SHORT kazanirken kuculur, yani gercek maliyet
  kazananlarda biraz DAHA AZ olur. Yani bu olcum fonlama yukunu HAFIF ABARTIR
  (muhafazakar yon — kapiyi haksiz yere kurtarmaz).

POPULASYON: canli asgari_stop_pct %2.0 uygulanir (2026-08-11 dersi).
MEKANIK canlinin aynisi: A-stop · Wilder ATR · %10 hedef · 72s · maliyet %0.13 ·
  giris sonraki barin acilisi · pump kapisi · hacim tabani $3M/24s · seyreltme 24 bar.
Kontrol: REJIM-ESLESMIS rastgele barlar (ayni fonlama muhasebesiyle).
Salt-okunur.
"""
import json, os, sys, statistics as stx, collections, bisect, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olcum_ortak as oo

BURA = os.path.dirname(os.path.abspath(__file__))
KLINE = os.path.join(BURA, "klines_1h_uzun")
FUND = os.path.join(BURA, "funding_gecmis")
HEDEF_PCT, UFUK = 10.0, 72
STOP_NBAR = 10
RISK_PCT, MARJIN_PCT, KALD_MAX = 0.015, 0.10, 10
ISINMA, SEYRELT = 220, 24
FUND_ESIK, PUMP, MIN_VOL = -0.05, 20.0, 3_000_000
ASGARI_STOP = 2.0
random_seed = 41


def atr_serisi(b, n=14):
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


def fonlama_pct(ft, fr, bas_ms, son_ms):
    """SHORT icin fonlama P&L katkisi (%): giris ile cikis ARASINDAKI anlarin oran
    toplami. Oran negatifse sonuc negatif = MALIYET."""
    i = bisect.bisect_right(ft, bas_ms)
    j = bisect.bisect_right(ft, son_ms)
    return sum(fr[k]["r"] for k in range(i, j)), (j - i)


def islem(b, atrs, si, ft, fr):
    gi = si + 1
    if si < ISINMA or gi >= len(b) or not atrs[si]:
        return None
    ref = b[gi]["o"]
    if ref <= 0:
        return None
    stop = stop_hesapla(b, si, ref, atrs[si])
    sp = (stop - ref) / ref * 100
    if sp <= 0 or sp < ASGARI_STOP:
        return None
    son = min(gi + UFUK, len(b))
    if son - gi < 4:
        return None
    hedef = ref * (1 - HEDEF_PCT / 100)
    cikis_j, tip, ham = None, None, None
    for j in range(gi, son):
        x = b[j]
        if x["h"] >= stop:
            cikis_j, tip, ham = j, "STOP", -sp
            break
        if x["l"] <= hedef:
            cikis_j, tip, ham = j, "HEDEF", HEDEF_PCT
            break
    if cikis_j is None:
        cikis_j, tip = son - 1, "SURE"
        ham = (ref - b[son - 1]["c"]) / ref * 100
    fon, adet = fonlama_pct(ft, fr, b[gi]["t"], b[cikis_j]["t"])
    saat = cikis_j - gi
    return {"ham": ham - oo.MALIYET, "fon": fon, "net": ham - oo.MALIYET + fon,
            "tip": tip, "sp": sp, "saat": saat, "fon_adet": adet}


def btc_rejim():
    b = json.load(open(os.path.join(KLINE, "BTC.json"), encoding="utf-8"))
    c = [x["c"] for x in b]
    pen, out = 720, {}
    for i in range(pen, len(b)):
        g = (c[i] / c[i - pen] - 1) * 100
        out[b[i]["t"] // 3600000] = "BOGA" if g >= 15 else ("AYI" if g <= -15 else "NOTR")
    return out


def main():
    import random
    random.seed(random_seed)
    rej = btc_rejim()
    dosyalar = sorted(f for f in os.listdir(KLINE) if f.endswith(".json"))
    sinyal, kontrol = [], []
    for n, f in enumerate(dosyalar, 1):
        if f == "BTC.json":
            continue
        sym = f[:-5]
        fy = os.path.join(FUND, sym + ".json")
        if not os.path.exists(fy):
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
            if not atrs[i] or c[i - 24] <= 0 or sum(qv[i - 23:i + 1]) < MIN_VOL:
                continue
            k = bisect.bisect_right(ft, b[i]["t"]) - 1
            if k < 0 or fr[k]["r"] > FUND_ESIK:
                continue
            if (c[i] / c[i - 24] - 1) * 100 >= PUMP or i - son < SEYRELT:
                continue
            son = i
            sinyal.append({"sym": sym, "b": b, "atrs": atrs, "i": i, "t": b[i]["t"],
                           "ft": ft, "fr": fr, "rej": rej.get(b[i]["t"] // 3600000),
                           "oran": fr[k]["r"]})
        for _ in range(max(2, (len(b) - ISINMA) // 400)):
            i = random.randint(ISINMA, len(b) - UFUK - 3)
            if atrs[i] and sum(qv[i - 23:i + 1]) >= MIN_VOL:
                kontrol.append({"sym": sym, "b": b, "atrs": atrs, "i": i, "t": b[i]["t"],
                                "ft": ft, "fr": fr, "rej": rej.get(b[i]["t"] // 3600000)})
        if n % 150 == 0:
            print(f"  {n}/{len(dosyalar)} ...", flush=True)

    if not sinyal:
        print("SINYAL YOK"); return
    tl = sorted(o["t"] for o in sinyal)
    ORTA = tl[len(tl) // 2]

    print("\n" + "=" * 116)
    print("A+B FUNDING BACAGI — FONLAMA MALIYETI DAHIL (2 yil)")
    print("=" * 116)
    print(f"Sinyal {len(sinyal)} · {len(set(o['sym'] for o in sinyal))} ayri sembol · "
          f"kontrol {len(kontrol)} · asgari stop %{ASGARI_STOP} uygulandi")
    print(f"Mekanik: A-stop · Wilder ATR · hedef %{HEDEF_PCT} · {UFUK}s · islem maliyeti %{oo.MALIYET}\n")

    def hesapla(sec, alan):
        kay, sem = [], []
        for o in sec:
            r = islem(o["b"], o["atrs"], o["i"], o["ft"], o["fr"])
            if r:
                boy = min(RISK_PCT / (r["sp"] / 100.0), MARJIN_PCT * KALD_MAX)
                kay.append((r[alan] * boy, r, o["t"])); sem.append(o["sym"])
        if len(kay) < 40:
            return None
        g = [k[0] for k in kay]
        n = len(g); k_ = len(set(sem))
        t = stx.mean(g) / (stx.stdev(g) / math.sqrt(n)) if n > 1 else 0
        return {"n": n, "ort": stx.mean(g), "sem": k_, "t": t,
                "t_kume": t * math.sqrt(k_ / n),
                "isabet": sum(1 for k in kay if k[1]["tip"] == "HEDEF") / n * 100,
                "saat": stx.median([k[1]["saat"] for k in kay]),
                "fon_ort": stx.mean([k[1]["fon"] for k in kay]),
                "fon_adet": stx.mean([k[1]["fon_adet"] for k in kay]),
                "A": stx.mean([k[0] for k in kay if k[2] < ORTA] or [0]),
                "B": stx.mean([k[0] for k in kay if k[2] >= ORTA] or [0])}

    print("### 1) FONLAMASIZ vs FONLAMALI")
    print(f"{'kume':30}{'N':>7}{'sermaye%':>11}{'t':>7}{'t_kume':>8}{'isabet':>8}"
          f"{'tutus~':>8}{'fonlama%':>10}{'A yari':>9}{'B yari':>9}")
    print("-" * 116)
    sonuc = {}
    for ad, sec, alan in (("SINYAL — fonlamasiz", sinyal, "ham"),
                          ("SINYAL — FONLAMALI", sinyal, "net"),
                          ("KONTROL — fonlamasiz", kontrol, "ham"),
                          ("KONTROL — FONLAMALI", kontrol, "net")):
        a = hesapla(sec, alan)
        if not a:
            continue
        sonuc[ad] = a
        print(f"{ad:30}{a['n']:7d}{a['ort']:+11.3f}{a['t']:+7.2f}{a['t_kume']:+8.2f}"
              f"{a['isabet']:7.1f}%{a['saat']:7.0f}s{a['fon_ort']:+10.3f}"
              f"{a['A']:+9.3f}{a['B']:+9.3f}")
    s0 = sonuc.get("SINYAL — fonlamasiz"); s1 = sonuc.get("SINYAL — FONLAMALI")
    k1 = sonuc.get("KONTROL — FONLAMALI")
    if s0 and s1:
        print("-" * 116)
        print(f"{'FONLAMANIN BEDELI':30}{'':7}{s1['ort']-s0['ort']:+11.3f}"
              f"   (kenarin %{abs(s1['ort']-s0['ort'])/abs(s0['ort'])*100:.0f}'i)")
    if s1 and k1:
        print(f"{'FARK (sinyal - kontrol)':30}{'':7}{s1['ort']-k1['ort']:+11.3f}")

    print("\n" + "=" * 116)
    print("### 2) REJIME GORE (fonlamali, rejim-eslesmis kontrolle)")
    print("=" * 116)
    print(f"{'rejim':10}{'N':>7}{'sinyal%':>11}{'t':>7}{'KONTROL%':>11}{'FARK':>9}{'fonlama%':>11}")
    print("-" * 116)
    rj = {}
    for r in ("BOGA", "NOTR", "AYI"):
        a = hesapla([o for o in sinyal if o["rej"] == r], "net")
        kk = hesapla([o for o in kontrol if o["rej"] == r], "net")
        if not a or not kk:
            continue
        rj[r] = a["ort"]
        print(f"{r:10}{a['n']:7d}{a['ort']:+11.3f}{a['t']:+7.2f}{kk['ort']:+11.3f}"
              f"{a['ort']-kk['ort']:+9.3f}{a['fon_ort']:+11.3f}")

    print("\n" + "=" * 116)
    print("### 3) TUTUS SURESINE GORE — fonlama uzun tutusta mi yiyor?")
    print("=" * 116)
    print(f"{'tutus':14}{'N':>7}{'fonlamasiz':>12}{'FONLAMALI':>12}{'fonlama%':>11}{'isabet':>9}")
    print("-" * 116)
    hepsi = []
    for o in sinyal:
        r = islem(o["b"], o["atrs"], o["i"], o["ft"], o["fr"])
        if r:
            boy = min(RISK_PCT / (r["sp"] / 100.0), MARJIN_PCT * KALD_MAX)
            hepsi.append((r, boy))
    for ad, alt, ust in (("0-8 saat", 0, 8), ("8-24 saat", 8, 24),
                         ("24-48 saat", 24, 48), ("48-72 saat", 48, 999)):
        v = [(r, b) for r, b in hepsi if alt <= r["saat"] < ust]
        if len(v) < 40:
            continue
        print(f"{ad:14}{len(v):7d}{stx.mean([r['ham']*b for r,b in v]):+12.3f}"
              f"{stx.mean([r['net']*b for r,b in v]):+12.3f}"
              f"{stx.mean([r['fon'] for r,_ in v]):+11.3f}"
              f"{sum(1 for r,_ in v if r['tip']=='HEDEF')/len(v)*100:8.1f}%")

    print("\n" + "=" * 116)
    print("### 4) GECME OLCUTU (on-kayitli)")
    print("=" * 116)
    if s1 and k1:
        c1 = s1["ort"] > 0
        c2 = s1["ort"] > k1["ort"]
        c3 = s1["A"] > 0 and s1["B"] > 0
        c4 = all(v > 0 for k, v in rj.items() if k in ("BOGA", "AYI"))
        print(f"  1) net > 0                   : {'EVET' if c1 else 'HAYIR'}  ({s1['ort']:+.3f})")
        print(f"  2) kontrolu yener            : {'EVET' if c2 else 'HAYIR'}  (fark {s1['ort']-k1['ort']:+.3f})")
        print(f"  3) iki zaman yarisi da +     : {'EVET' if c3 else 'HAYIR'}  (A {s1['A']:+.3f} / B {s1['B']:+.3f})")
        print(f"  4) BOGA ve AYI'da cokme yok  : {'EVET' if c4 else 'HAYIR'}  "
              f"({', '.join(f'{k} {v:+.3f}' for k, v in rj.items())})")
        print(f"  5) ayri sembol / t_kume      : {s1['sem']} · {s1['t_kume']:+.2f}")
        print(f"\n  ->  {'GECTI' if all((c1, c2, c3, c4)) else 'KALDI'}")


if __name__ == "__main__":
    main()
