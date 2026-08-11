#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OYNAKLIGA OLCEKLI HEDEF — olcum (2026-08-12)
On-kayit: fikir-defteri.md, commit 60fb7e4 (KOSTURULMADAN once)

FIKIR: sabit "%10 dussun" yerine "bu coin'in kendi oynakliginin N kati kadar dussun",
ve hedef HER BARDA guncel ATR ile YENIDEN hesaplansin. Coin sakinlesirse hedef
yakinlasir; fiyat zaten oradaysa pozisyon kapanir ("oynaklik sondu").

NEDEN BAR-BAR SIMULASYON SART: hedef hareket ettigi icin onceden hesaplayip
"degdi mi" diye bakilamaz. Her barda ATR yeniden hesaplanmali. Aksi halde olcum
gercegi yansitmaz.

VERI: klines_1h_uzun (566 sembol, 2 yil, GERCEK BOGA + GERCEK AYI).
Esikler ve kapilar canlidakiyle ayni; ATR Wilder (olcum_ortak = canlinin olcucu.atr'i).
Salt-okunur.
"""
import json, os, sys, statistics as stx, collections, datetime, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olcum_ortak as oo

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h_uzun")
SABIT_HEDEF, UFUK = 10.0, 72
STOP_NBAR, STOP_ATR_PAY, ATR_N = 10, 0.25, 14
RISK_PCT, MARJIN_PCT, KALD_MAX = 0.015, 0.10, 10
ISINMA, SEYRELT = 220, 24
PUMP, CHG_ESIK, MA50_ESIK, UCUZ = 20.0, -3.662, 3.72, 0.07


# ---------------------------------------------------------------- gostergeler
def atr_serisi(b, n=ATR_N):
    """Wilder ATR, TUM seri (bar-bar simulasyon icin sart — her barda taze deger)."""
    out = [None] * len(b)
    tr = [None] * len(b)
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


def ma(v, n):
    out, s = [None] * len(v), 0.0
    for i, x in enumerate(v):
        s += x
        if i >= n:
            s -= v[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def swings_yuksek(b, i, left=3, right=3, geri=100):
    bas = max(left, i - geri)
    hi = []
    for j in range(bas, i - right + 1):
        w = b[j - left:j + right + 1]
        if w and b[j]["h"] == max(x["h"] for x in w):
            hi.append(b[j]["h"])
    return hi


def stop_hesapla(b, si, ref, a):
    """Botun A-stopu (SHORT)."""
    hi = swings_yuksek(b, si)
    res = min([x for x in hi if x > ref], default=None)
    ad = []
    if res is not None and (res - ref) <= 3 * a:
        ad.append(res + 0.25 * a)
    nb = max(x["h"] for x in b[max(0, si - STOP_NBAR + 1):si + 1])
    if nb > ref:
        ad.append(nb + STOP_ATR_PAY * a)
    ad.append(ref + 1.5 * a)
    gec = [s for s in ad if s > ref]
    return min(gec) if gec else ref + 1.5 * a


# ---------------------------------------------------------------- islem
def islem(b, atrs, si, mod, n=None, taban=None, tavan=None):
    """mod='sabit' -> %10 sabit hedef.  mod='oynak' -> hedef = n x ATR, HER BARDA taze.
    Doner: (net%, tip, stop%, medyan_hedef%)"""
    gi = si + 1
    i = si
    if i < ISINMA or gi >= len(b) or atrs[i] is None or atrs[i] <= 0:
        return None
    ref = b[gi]["o"]
    if ref <= 0:
        return None
    stop = stop_hesapla(b, i, ref, atrs[i])
    sp = (stop - ref) / ref * 100
    if sp <= 0:
        return None
    son = min(gi + UFUK, len(b))
    if son - gi < 4:
        return None
    hedefler = []
    for j in range(gi, son):
        x = b[j]
        # --- HEDEF: her barda yeniden (oynak modda)
        if mod == "sabit":
            hp = SABIT_HEDEF
        else:
            a = atrs[j - 1] if atrs[j - 1] else atrs[i]      # o ana kadarki KAPANMIS bar ATR'si
            hp = n * a / ref * 100
            if taban is not None:
                hp = max(hp, taban)
            if tavan is not None:
                hp = min(hp, tavan)
        hedefler.append(hp)
        hedef = ref * (1 - hp / 100)
        if x["h"] >= stop:
            return -sp - oo.MALIYET, "STOP", sp, stx.median(hedefler)
        # [DUZELTME 2026-08-12] Hedef daralip fiyat onu ZATEN gectiyse, canlida bot
        #   PIYASADAN kapatir — hedef fiyatindan degil. Onceki surum hedeften
        #   doldururken kazanci EKSIK yaziyordu (SHORT'ta hedef daha yuksek = daha kotu),
        #   yani olcum test edilen fikrin ALEYHINE capitiyordu.
        acilis = x.get("o", x["c"])
        if acilis <= hedef:                      # bar ACILISINDA zaten gecilmis
            g = (ref - acilis) / ref * 100
            return g - oo.MALIYET, "OYNAKLIK_SONDU", sp, stx.median(hedefler)
        if x["l"] <= hedef:                      # bar ICINDE hedefe dokundu
            g = hp
            return g - oo.MALIYET, "HEDEF", sp, stx.median(hedefler)
    c = b[son - 1]["c"]
    return (ref - c) / ref * 100 - oo.MALIYET, "SURE", sp, stx.median(hedefler)


# ---------------------------------------------------------------- olaylar
def btc_rejim():
    b = json.load(open(os.path.join(CACHE, "BTC.json"), encoding="utf-8"))
    c = [x["c"] for x in b]
    pen, out = 720, {}
    for i in range(pen, len(b)):
        g = (c[i] / c[i - pen] - 1) * 100
        out[b[i]["t"] // 3600000] = "BOGA" if g >= 15 else ("AYI" if g <= -15 else "NOTR")
    return out


def olaylari_topla(rej):
    """Canli iki kapinin (A+B yaklasigi + MA50+ucuz) tetiklendigi barlar.
    NOT: funding/OI 2 yillik veride YOK -> A+B tam kurulamaz. Bu yuzden MA50+ucuz
    kapisi kullanilir (fiyat + MA50, ikisi de mumdan turer) ve bu SINIR raporlanir."""
    olay = []
    dosyalar = sorted(f for f in os.listdir(CACHE) if f.endswith(".json"))
    for n, f in enumerate(dosyalar, 1):
        if f == "BTC.json":
            continue
        try:
            b = json.load(open(os.path.join(CACHE, f), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ISINMA + 120:
            continue
        sym = f[:-5]
        c = [x["c"] for x in b]
        qv = [x.get("qv", 0.0) for x in b]
        atrs = atr_serisi(b)
        m50 = ma(c, 50)
        son = -10 ** 9
        for i in range(ISINMA, len(b) - UFUK - 2):
            if m50[i] is None or atrs[i] is None or c[i - 24] <= 0:
                continue
            # [DUZELTME 2026-08-12] Canli bot yalniz min_vol_musd=3 ($3M/24s) uzeri
            #   likit havuzu tariyor. Filtresiz surum TUM sembolleri aliyordu ->
            #   medyan stop %1.1 cikti (canlida %3.4), yani BASKA bir populasyon
            #   olculuyordu. Hacim tabani eklendi ki kiyas adil olsun.
            if sum(qv[i - 23:i + 1]) < 3_000_000:
                continue
            px = c[i]
            if px > UCUZ:
                continue
            if (px / m50[i] - 1) * 100 < MA50_ESIK:
                continue
            if (px / c[i - 24] - 1) * 100 >= PUMP:        # pump kapisi
                continue
            if i - son < SEYRELT:
                continue
            son = i
            olay.append({"sym": sym, "b": b, "atrs": atrs, "i": i, "t": b[i]["t"],
                         "rej": rej.get(b[i]["t"] // 3600000)})
        if n % 150 == 0:
            print(f"  {n}/{len(dosyalar)} ...", flush=True)
    return olay


def oz(kayit, sem):
    if len(kayit) < 60:
        return None
    g = [x[0] for x in kayit]
    boy = [min(RISK_PCT / (x[2] / 100.0), MARJIN_PCT * KALD_MAX) for x in kayit]
    serm = [a * b for a, b in zip(g, boy)]
    o = oo.ozet(serm, sem, asgari=60)
    if o:
        o["fiyat_ort"] = stx.mean(g)
        o["isabet"] = sum(1 for x in kayit if x[1] == "HEDEF") / len(kayit) * 100
        o["sondu"] = sum(1 for x in kayit if x[1] == "OYNAKLIK_SONDU") / len(kayit) * 100
        o["hedef_med"] = stx.median([x[3] for x in kayit])
        o["stop_med"] = stx.median([x[2] for x in kayit])
    return o


def main():
    print("Rejim ve olaylar hazirlaniyor...", flush=True)
    rej = btc_rejim()
    olay = olaylari_topla(rej)
    tl = sorted(o["t"] for o in olay)
    ORTA = tl[len(tl) // 2]
    print(f"\nOlay: {len(olay)} · {len(set(o['sym'] for o in olay))} ayri sembol\n")

    print("=" * 116)
    print("OYNAKLIGA OLCEKLI HEDEF vs SABIT %10 — 2 yillik veri (boga + ayi)")
    print("=" * 116)
    print(f"maliyet %{oo.MALIYET} · Wilder ATR · ufuk {UFUK}s · hedef HER BARDA yeniden\n")

    def kos(mod, n=None, taban=None, tavan=None, suz=None):
        kay, sem = [], []
        for o in olay:
            if suz and not suz(o):
                continue
            r = islem(o["b"], o["atrs"], o["i"], mod, n, taban, tavan)
            if r:
                kay.append((r[0], r[1], r[2], r[3], o["t"])); sem.append(o["sym"])
        return oz([(k[0], k[1], k[2], k[3]) for k in kay], sem), kay

    print(f"{'kural':30}{'N':>6}{'sermaye%':>10}{'t':>7}{'isabet':>8}{'sondu':>8}"
          f"{'hedef~':>8}{'stop~':>7}{'A yari':>9}{'B yari':>9}{'sembol':>8}{'t_kume':>8}")
    print("-" * 116)
    SENARYO = [("SABIT %10 (bugunku)", "sabit", None, None, None)]
    for n in (2, 3, 4, 5, 6):
        SENARYO.append((f"oynak {n}xATR (frensiz)", "oynak", n, None, None))
    for n in (3, 4, 5):
        SENARYO.append((f"oynak {n}xATR taban%3 tavan%20", "oynak", n, 3.0, 20.0))
    sonuc = {}
    for ad, mod, n, tb, tv in SENARYO:
        a, kay = kos(mod, n, tb, tv)
        if not a:
            continue
        A = oz([(k[0], k[1], k[2], k[3]) for k in kay if k[4] < ORTA],
               [o for o, k in zip([x["sym"] for x in olay if True][:0] or [None]*len(kay), kay) if k[4] < ORTA] or None)
        # yarilar icin basit ortalama (sembol listesi olmadan)
        boy = lambda k: min(RISK_PCT / (k[2] / 100.0), MARJIN_PCT * KALD_MAX)
        va = [k[0] * boy(k) for k in kay if k[4] < ORTA]
        vb = [k[0] * boy(k) for k in kay if k[4] >= ORTA]
        sonuc[ad] = (a, kay)
        im = ""
        if ad != "SABIT %10 (bugunku)" and "SABIT %10 (bugunku)" in sonuc:
            im = " *" if a["ort"] > sonuc["SABIT %10 (bugunku)"][0]["ort"] else ""
        print(f"{ad:30}{(n or 0):6}{a['ort']:+10.3f}{a['t']:+7.2f}{a['isabet']:7.1f}%"
              f"{a['sondu']:7.1f}%{a['hedef_med']:7.1f}%{a['stop_med']:6.1f}%"
              f"{stx.mean(va):+9.3f}{stx.mean(vb):+9.3f}{a['ayri_sembol']:8d}"
              f"{a.get('t_kume', 0):+8.2f}{im}")
    print("-" * 116)
    print("  'sondu' = oynaklik dustugu icin hedef yakinlasip kapanan islem orani")
    print("  'hedef~' = medyan hedef yuzdesi · '*' = sabit %10'u yendi")

    print("\n" + "=" * 116)
    print("REJIME GORE — ilk kez boga/ayi ayrimi yapilabiliyor")
    print("=" * 116)
    print(f"{'kural':30}{'rejim':7}{'N':>6}{'sermaye%':>11}{'t':>7}{'isabet':>9}")
    print("-" * 116)
    for ad, mod, n, tb, tv in SENARYO:
        if ad != "SABIT %10 (bugunku)" and n not in (3, 4):
            continue
        for r in ("BOGA", "NOTR", "AYI"):
            a, _ = kos(mod, n, tb, tv, suz=lambda o, _r=r: o["rej"] == _r)
            if a:
                print(f"{ad:30}{r:7}{a['n']:6d}{a['ort']:+11.3f}{a['t']:+7.2f}{a['isabet']:8.1f}%")
        print()

    print("=" * 116)
    print("GECME OLCUTU: sabit %10'u yen · iki zaman yarisi + · BOGA ve AYI'da cokme")
    print("=" * 116)
    taban_s = sonuc.get("SABIT %10 (bugunku)")
    for ad, (a, kay) in sonuc.items():
        if ad == "SABIT %10 (bugunku)":
            continue
        boy = lambda k: min(RISK_PCT / (k[2] / 100.0), MARJIN_PCT * KALD_MAX)
        va = [k[0] * boy(k) for k in kay if k[4] < ORTA]
        vb = [k[0] * boy(k) for k in kay if k[4] >= ORTA]
        c1 = a["ort"] > taban_s[0]["ort"]
        c2 = stx.mean(va) > 0 and stx.mean(vb) > 0
        print(f"  {ad:30} yendi {'E' if c1 else 'H'} · iki yari + {'E' if c2 else 'H'}"
              f"  -> {'aday' if (c1 and c2) else 'KALDI'}")
    print("\n  SINIR: 2 yillik veride funding/OI yok -> A+B kapisi kurulamadi;")
    print("  olcum YALNIZ MA50+ucuz kapisinin olaylari uzerinde.")


if __name__ == "__main__":
    main()
