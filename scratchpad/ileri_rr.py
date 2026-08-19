#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ILERI R/R CIKIS ESIGI - 2 yillik sinav (2026-08-19)

ON-KAYIT: olcumler.md -> "ON-KAYIT - ILERI R/R CIKIS ESIGI" (commit 43833f3,
KOSTURULMADAN ONCE yazildi). Bu betik o on-kaydi UYGULAR; olcut metnini
degistirmez, esik taramaz.

HIPOTEZ: acik pozisyonun ileri R/R'si -- (hedefe kalan mesafe)/(stopa kalan
mesafe) -- ESIK'in altina dusunce kapatmak, sabit %10 hedefe gore net getiriyi
artirir.

ESIK = 1.0 (TEK deger, on-kayitli, tarama YASAK).
  Geometrik basabas: R/R<1 ise pozisyon kazanabileceginden fazlasini riske atar.

DIKKAT -- KURALIN YONU: R/R, fiyat HEDEFE yaklastikca DUSER (hedefe kalan azalir,
  stopa kalan buyur). Yani kural pozisyon KAZANIRKEN tetiklenir; bu bir KAR-ALMA
  kuralidir, zarar-kesme degil. Tetik noktasi stop ile hedefin tam ORTASI.

MEKANIK (kontrol ile BIREBIR ayni, tek fark ek cikis kosulu):
  giris   = tetigin ertesi 1h barinin acilisi
  stop    = botun A-varyanti (swing + NBAR + 1.5xATR, Wilder ATR14)
  hedef   = giris -%10 (SHORT)
  ufuk    = 72 saat
  maliyet = olcum_ortak.MALIYET (gidis-donus: taker+slipaj)
  fonlama = gercek funding gecmisi, giris-cikis arasi oranlarin toplami
  bar ici sira: STOP (fitil) -> HEDEF (fitil) -> R/R (KAPANIS)
                kontrolun cikislari ONCELIKLI; R/R yalniz onlar tetiklenmezse bakar

GIRIS KUMELERI (botun SABIT_HEDEF_KAPILARI ile ayni):
  A) funding bacagi : funding <= -0.05 %/8s   (A+B'nin olculebilir bacagi;
                      oi24 kline verisinde YOK, bu yuzden tek bacak)
  B) MA50+ucuz      : fiyat <= $0.07  VE  MA50 mesafesi >= %3.72

GECME OLCUTU (dordu de gerekli, on-kayitli):
  1. net getiri kontrolden YUKSEK
  2. IKI YARIDA DA yuksek (A ve B ayri ayri)
  3. t_kume > +2.0
  4. uc rejimin hicbirinde ters isaret yok
"""
import json, os, sys, statistics as stx, collections, bisect, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olcum_ortak as oo

BURA = os.path.dirname(os.path.abspath(__file__))
KLINE = os.path.join(BURA, "klines_1h_uzun")
FUND = os.path.join(BURA, "funding_gecmis")

# --- ON-KAYITLI PARAMETRELER (degistirilmez) ---
ESIK_RR = 1.0
HEDEF_PCT, UFUK = 10.0, 72
STOP_NBAR, ISINMA, SEYRELT = 10, 220, 24
FUND_ESIK, PUMP, MIN_VOL = -0.05, 20.0, 3_000_000
ASGARI_STOP = 2.0
UCUZ_FIYAT, MA50_MESAFE = 0.07, 3.72
random.seed(41)


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


def ma_serisi(b, n=50):
    out = [None] * len(b)
    s = 0.0
    for i, x in enumerate(b):
        s += x["c"]
        if i >= n:
            s -= b[i - n]["c"]
        if i >= n - 1:
            out[i] = s / n
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
    i = bisect.bisect_right(ft, bas_ms)
    j = bisect.bisect_right(ft, son_ms)
    return sum(fr[k]["r"] for k in range(i, j))


def islem(b, atrs, si, ft, fr):
    """-> (kontrol, kural) | None.  AYNI giris, iki farkli cikis."""
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

    kontrol = kural = None
    for j in range(gi, son):
        x = b[j]
        if x["h"] >= stop:                      # 1) STOP (fitil)
            e = (j, "STOP", -sp)
            kontrol = kontrol or e
            kural = kural or e
            break
        if x["l"] <= hedef:                     # 2) HEDEF (fitil)
            e = (j, "HEDEF", HEDEF_PCT)
            kontrol = kontrol or e
            kural = kural or e
            break
        if kural is None:                       # 3) ILERI R/R (KAPANIS)
            c = x["c"]
            kalan_hedef = c - hedef              # SHORT: fiyat hedefin USTUNDE
            kalan_stop = stop - c                # SHORT: stop fiyatin USTUNDE
            if kalan_stop > 0 and kalan_hedef > 0:
                if (kalan_hedef / kalan_stop) < ESIK_RR:
                    kural = (j, "RR", (ref - c) / ref * 100)
    if kontrol is None:
        kontrol = (son - 1, "SURE", (ref - b[son - 1]["c"]) / ref * 100)
    if kural is None:
        kural = (son - 1, "SURE", (ref - b[son - 1]["c"]) / ref * 100)

    out = []
    for cj, tip, ham in (kontrol, kural):
        fon = fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
        out.append({"net": ham - oo.MALIYET + fon, "tip": tip, "sp": sp,
                    "saat": cj - gi, "ts": b[gi]["t"]})
    return out[0], out[1]


def btc_rejim():
    b = json.load(open(os.path.join(KLINE, "BTC.json"), encoding="utf-8"))
    c = [x["c"] for x in b]
    pen, out = 720, {}
    for i in range(pen, len(b)):
        g = (c[i] / c[i - pen] - 1) * 100
        out[b[i]["t"] // 3600000] = "BOGA" if g >= 15 else ("AYI" if g <= -15 else "NOTR")
    return out


def kosturr():
    rej = btc_rejim()
    kume = {"A_funding": {"k": [], "r": [], "s": [], "t": [], "g": []},
            "B_ma50ucuz": {"k": [], "r": [], "s": [], "t": [], "g": []}}
    islenen = 0
    for fn in sorted(os.listdir(KLINE)):
        if not fn.endswith(".json"):
            continue
        sym = fn[:-5]
        try:
            b = json.load(open(os.path.join(KLINE, fn), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ISINMA + UFUK + 50:
            continue
        fpath = os.path.join(FUND, fn)
        fr = []
        if os.path.exists(fpath):
            try:
                fr = json.load(open(fpath, encoding="utf-8"))
            except Exception:
                fr = []
        ft = [x["t"] for x in fr]
        atrs = atr_serisi(b)
        ma50 = ma_serisi(b, 50)
        islenen += 1
        for i in range(ISINMA, len(b) - UFUK - 2, SEYRELT):
            x = b[i]
            if (x.get("qv") or 0) < MIN_VOL / 24:
                continue
            if i < 24:
                continue
            if (x["c"] / b[i - 24]["c"] - 1) * 100 >= PUMP:   # pump kapisi
                continue
            hedefler = []
            if ft:
                k = bisect.bisect_right(ft, x["t"]) - 1
                if k >= 0 and fr[k]["r"] * 100 <= FUND_ESIK:
                    hedefler.append("A_funding")
            if ma50[i] and ma50[i] > 0 and x["c"] <= UCUZ_FIYAT:
                if (x["c"] / ma50[i] - 1) * 100 >= MA50_MESAFE:
                    hedefler.append("B_ma50ucuz")
            if not hedefler:
                continue
            r = islem(b, atrs, i, ft, fr)
            if not r:
                continue
            kon, kur = r
            rj = rej.get(b[i]["t"] // 3600000, "NOTR")
            for h in hedefler:
                d = kume[h]
                d["k"].append(kon["net"])
                d["r"].append(kur["net"])
                d["s"].append(sym)
                d["t"].append(b[i]["t"])
                d["g"].append((rj, kur["tip"]))
    return kume, islenen


def rapor():
    print("ILERI R/R CIKIS ESIGI - 2 yillik sinav")
    print("=" * 78)
    print("ON-KAYIT: olcumler.md (commit 43833f3, kosturulmadan ONCE)")
    print("ESIK = %s  (TEK deger, tarama YOK)" % ESIK_RR)
    print("Mekanik: A-stop, Wilder ATR, hedef %%%s, %ss, maliyet %%%s, FONLAMA DAHIL"
          % (HEDEF_PCT, UFUK, oo.MALIYET))
    print("Bar ici sira: STOP(fitil) -> HEDEF(fitil) -> R/R(kapanis)\n")
    kume, islenen = kosturr()
    print("islenen sembol: %d\n" % islenen)
    for ad, d in kume.items():
        n = len(d["k"])
        if n < 30:
            print("%s: N=%d - YETERSIZ\n" % (ad, n))
            continue
        ok = oo.ozet(d["k"], d["s"], asgari=30)
        ur = oo.ozet(d["r"], d["s"], asgari=30)
        if not ok or not ur:
            print("%s: ozet uretilemedi (N=%d)" % (ad, n))
            continue
        print("--- %s  (N=%d) %s" % (ad, n, "-" * max(0, 50 - len(ad))))
        print("  KONTROL (sabit %%10 hedef) : %+7.3f%%  t=%+5.2f  t_kume=%+5.2f"
              % (ok["ort"], ok["t"], ok.get("t_kume", 0)))
        print("  KURAL   (ileri R/R < %s) : %+7.3f%%  t=%+5.2f  t_kume=%+5.2f"
              % (ESIK_RR, ur["ort"], ur["t"], ur.get("t_kume", 0)))
        fark = [a - b for a, b in zip(d["r"], d["k"])]
        of = oo.ozet(fark, d["s"], asgari=30)
        print("  FARK (kural - kontrol)    : %+7.3f%%  t=%+5.2f  t_kume=%+5.2f   <-- OLCUT 1 ve 3"
              % (of["ort"], of["t"], of.get("t_kume", 0)))
        srt = sorted(range(n), key=lambda z: d["t"][z])
        yar = len(srt) // 2
        for etiket, idx in (("A yarisi", srt[:yar]), ("B yarisi", srt[yar:])):
            fa = [d["r"][z] - d["k"][z] for z in idx]
            sa = [d["s"][z] for z in idx]
            o = oo.ozet(fa, sa, asgari=10)
            if o:
                print("    %s: fark %+7.3f%%  t=%+5.2f  N=%d" % (etiket, o["ort"], o["t"], len(fa)))
            else:
                print("    %s: N=%d yetersiz" % (etiket, len(fa)))
        rg = collections.defaultdict(list)
        for z in range(n):
            rg[d["g"][z][0]].append(d["r"][z] - d["k"][z])
        print("    rejim: " + " | ".join("%s %+.3f%% (N=%d)" % (k, stx.mean(v), len(v))
                                          for k, v in sorted(rg.items())))
        print("    kural cikis tipleri: %s" % dict(collections.Counter(g[1] for g in d["g"])))
        print()


if __name__ == "__main__":
    rapor()
