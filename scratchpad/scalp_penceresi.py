#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SCALP PENCERESI (2026-08-12) — "botun girdigi poza elle scalp binebilir miyim?"

KULLANICI SORUSU: bot bir poz aciyor; ben onu izleyip ARTIDAYKEN kisa vadeli elle
islem alabilir miyim? Yani botun 72 saatlik %10 hedefi degil, GIRISTEN SONRAKI ILK
SAATLERDE fiyat lehe ne kadar, ne siklikla gidiyor?

BU SORU HIC OLCULMEDI. Bugune kadarki her sey botun KENDI cikis kurallariyla
(A-stop, %10 hedef, 72s) olculdu. "MA50+ucuz negatif" demek "72 saatte %10 hedefle
tutulursa kaybettirir" demek — "ilk yarim saatte kara gecmez" DEMEK DEGIL.

CIKTI: elle scalp yapan biri icin ASIL SAYI — belirli bir hedef/stop ciftinde
kac girisin hedefi stoptan ONCE gordugu, ve maliyet sonrasi beklenti.

VERI SINIRI (acikca): elimizde 1 SAATLIK bar var. 15/30 dakikalik cozunurluk YOK.
Bar'in dusuk/yuksek degerleriyle "ilk 1 saatte lehe/aleyhe ne kadar gitti" hesaplanir,
ama bar ICINDE hangisinin once oldugu bilinmez -> IKISI de gorulduyse KOTUMSER
varsayimla STOP sayilir. Sonuc bu yuzden gercegin ALT SINIRIDIR.

Salt-okunur.
"""
import json, os, sys, random, statistics as stx, collections, bisect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olcum_ortak as oo

BURA = os.path.dirname(os.path.abspath(__file__))
KLINE = os.path.join(BURA, "klines_1h_uzun")
FUND = os.path.join(BURA, "funding_gecmis")
ISINMA, SEYRELT, MIN_VOL = 220, 24, 3_000_000
FUND_ESIK, PUMP, MA50_ESIK, UCUZ = -0.05, 20.0, 3.72, 0.07
UFUKLAR = (1, 2, 3, 4, 8, 24)
random.seed(53)


def ma(v, n):
    out, s = [None] * len(v), 0.0
    for i, x in enumerate(v):
        s += x
        if i >= n:
            s -= v[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def btc_rejim():
    b = json.load(open(os.path.join(KLINE, "BTC.json"), encoding="utf-8"))
    c = [x["c"] for x in b]
    pen, out = 720, {}
    for i in range(pen, len(b)):
        g = (c[i] / c[i - pen] - 1) * 100
        out[b[i]["t"] // 3600000] = "BOGA" if g >= 15 else ("AYI" if g <= -15 else "NOTR")
    return out


def mfe_mae(b, gi, ufuk):
    """SHORT icin: lehte = dusuk, aleyhte = yuksek. Yuzde olarak."""
    if gi + ufuk >= len(b):
        return None
    ref = b[gi]["o"]
    if ref <= 0:
        return None
    dilim = b[gi:gi + ufuk]
    mfe = (ref - min(x["l"] for x in dilim)) / ref * 100
    mae = (max(x["h"] for x in dilim) - ref) / ref * 100
    return mfe, mae


def hedef_once_mu(b, gi, hedef, stop, ufuk):
    """Hedef stoptan ONCE mi goruldu? Ayni barda ikisi de -> KOTUMSER: STOP.
    Doner 'HEDEF' / 'STOP' / 'ZAMAN'."""
    ref = b[gi]["o"]
    h = ref * (1 - hedef / 100)
    s = ref * (1 + stop / 100)
    for j in range(gi, min(gi + ufuk, len(b))):
        x = b[j]
        vurdu_s = x["h"] >= s
        vurdu_h = x["l"] <= h
        if vurdu_s:
            return "STOP"
        if vurdu_h:
            return "HEDEF"
    return "ZAMAN"


def olaylari_topla(rej):
    kume = {"A+B (funding)": [], "MA50+ucuz": [], "KONTROL": []}
    dosyalar = sorted(f for f in os.listdir(KLINE) if f.endswith(".json"))
    for n, f in enumerate(dosyalar, 1):
        if f == "BTC.json":
            continue
        sym = f[:-5]
        try:
            b = json.load(open(os.path.join(KLINE, f), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ISINMA + 60:
            continue
        c = [x["c"] for x in b]
        qv = [x.get("qv", 0.0) for x in b]
        m50 = ma(c, 50)
        fy = os.path.join(FUND, sym + ".json")
        fr = json.load(open(fy, encoding="utf-8")) if os.path.exists(fy) else []
        ft = [x["t"] for x in fr]
        son = collections.defaultdict(lambda: -10 ** 9)

        def ekle(ad, i):
            if i - son[ad] < SEYRELT or i + max(UFUKLAR) + 1 >= len(b):
                return
            son[ad] = i
            kume[ad].append({"sym": sym, "b": b, "gi": i + 1,
                             "t": b[i]["t"], "rej": rej.get(b[i]["t"] // 3600000)})

        for i in range(ISINMA, len(b) - max(UFUKLAR) - 2):
            if c[i - 24] <= 0 or sum(qv[i - 23:i + 1]) < MIN_VOL:
                continue
            if (c[i] / c[i - 24] - 1) * 100 >= PUMP:
                continue
            if fr:
                k = bisect.bisect_right(ft, b[i]["t"]) - 1
                if k >= 0 and fr[k]["r"] <= FUND_ESIK:
                    ekle("A+B (funding)", i)
            if m50[i] and c[i] <= UCUZ and (c[i] / m50[i] - 1) * 100 >= MA50_ESIK:
                ekle("MA50+ucuz", i)
        for _ in range(max(2, (len(b) - ISINMA) // 400)):
            i = random.randint(ISINMA, len(b) - max(UFUKLAR) - 3)
            if sum(qv[i - 23:i + 1]) >= MIN_VOL:
                kume["KONTROL"].append({"sym": sym, "b": b, "gi": i + 1,
                                        "t": b[i]["t"], "rej": rej.get(b[i]["t"] // 3600000)})
        if n % 150 == 0:
            print(f"  {n}/{len(dosyalar)} ...", flush=True)
    return kume


def main():
    print("Olaylar toplaniyor...", flush=True)
    rej = btc_rejim()
    kume = olaylari_topla(rej)

    print("\n" + "=" * 108)
    print("SCALP PENCERESI — botun girisinden sonra fiyat LEHE ne kadar gidiyor?")
    print("=" * 108)
    print("VERI SINIRI: 1 saatlik bar. 15/30 dk cozunurluk YOK; en kisa pencere 1 SAAT.")
    print("Ayni barda hem hedef hem stop -> KOTUMSER olarak STOP sayilir (alt sinir).\n")

    for ad in ("A+B (funding)", "MA50+ucuz", "KONTROL"):
        v = kume[ad]
        if len(v) < 100:
            continue
        print(f"### {ad}   N={len(v)} · {len(set(o['sym'] for o in v))} ayri sembol")
        print(f"{'ufuk':>8}{'MFE med':>10}{'MFE %75':>10}{'MAE med':>10}"
              f"{'MFE/MAE':>10}{'>= +%0.5':>10}{'>= +%1':>9}{'>= +%2':>9}")
        print("-" * 108)
        for u in UFUKLAR:
            r = [mfe_mae(o["b"], o["gi"], u) for o in v]
            r = [x for x in r if x]
            if len(r) < 100:
                continue
            mfe = sorted(x[0] for x in r)
            mae = sorted(x[1] for x in r)
            mm = stx.median(mfe); ma_ = stx.median(mae)
            print(f"{u:>6}s{mm:10.2f}{mfe[int(len(mfe)*0.75)]:10.2f}{ma_:10.2f}"
                  f"{(mm/ma_ if ma_ else 0):10.2f}"
                  f"{sum(1 for x in mfe if x >= 0.5)/len(mfe)*100:9.0f}%"
                  f"{sum(1 for x in mfe if x >= 1.0)/len(mfe)*100:8.0f}%"
                  f"{sum(1 for x in mfe if x >= 2.0)/len(mfe)*100:8.0f}%")
        print()

    print("=" * 108)
    print("ASIL TABLO — elle scalp: hedef stoptan ONCE gorulur mu? (ilk 4 saat)")
    print("=" * 108)
    print(f"maliyet %{oo.MALIYET} dahil · beklenti = P(hedef)x(hedef-maliyet) - P(stop)x(stop+maliyet)\n")
    for ad in ("A+B (funding)", "MA50+ucuz", "KONTROL"):
        v = kume[ad]
        if len(v) < 100:
            continue
        print(f"### {ad}")
        print(f"{'hedef':>7}{'stop':>7}{'hedef %':>10}{'stop %':>9}{'zaman %':>10}"
              f"{'BEKLENTI %':>12}{'sembol':>8}")
        print("-" * 108)
        for hedef in (0.5, 1.0, 1.5, 2.0):
            for stop in (0.5, 1.0, 1.5):
                sonuc = collections.Counter()
                sem = set()
                for o in v:
                    if o["gi"] + 4 >= len(o["b"]):
                        continue
                    sonuc[hedef_once_mu(o["b"], o["gi"], hedef, stop, 4)] += 1
                    sem.add(o["sym"])
                n = sum(sonuc.values())
                if n < 100:
                    continue
                ph = sonuc["HEDEF"] / n; ps = sonuc["STOP"] / n
                bek = ph * (hedef - oo.MALIYET) - ps * (stop + oo.MALIYET)
                im = " *" if bek > 0 else ""
                print(f"{hedef:6.1f}%{stop:6.1f}%{ph*100:9.0f}%{ps*100:8.0f}%"
                      f"{sonuc['ZAMAN']/n*100:9.0f}%{bek:+12.3f}{len(sem):8d}{im}")
        print()

    print("=" * 108)
    print("HIZLI TEPE = KAYBEDEN MI? (17 canli pozisyonda gorulen oruntu, 2 yilda sinaniyor)")
    print("=" * 108)
    for ad in ("A+B (funding)", "MA50+ucuz"):
        v = kume[ad]
        if len(v) < 100:
            continue
        erken, gec = [], []
        for o in v:
            b, gi = o["b"], o["gi"]
            if gi + 72 >= len(b):
                continue
            r4 = mfe_mae(b, gi, 4)
            r72 = mfe_mae(b, gi, 72)
            if not r4 or not r72:
                continue
            ref = b[gi]["o"]
            son72 = (ref - b[gi + 71]["c"]) / ref * 100
            (erken if r4[0] >= 1.0 else gec).append(son72)
        if len(erken) < 50 or len(gec) < 50:
            continue
        print(f"  {ad}")
        print(f"    ilk 4 saatte >= +%1 gorenler  : N={len(erken):5d}  72s sonu medyan {stx.median(erken):+.2f}%")
        print(f"    gormeyenler                   : N={len(gec):5d}  72s sonu medyan {stx.median(gec):+.2f}%")
        print()


if __name__ == "__main__":
    main()
