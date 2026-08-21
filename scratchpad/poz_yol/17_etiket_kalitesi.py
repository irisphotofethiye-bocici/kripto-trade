#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REJIM ETIKETI — KARIYLA DEGIL, KENDI IDDIASIYLA SINANIR.

KULLANICI (2026-08-21): "burda tekrar kosullar ayni olmayacak test ile ve
negatif sonuc cikaracak."

HAKLI. "Hangi etiket daha karli" sorusunun rejimden BAGIMSIZ cevabi yok:
yon kenarinin kendisi rejimle donuyor (16_rejim_kosullu.py), o yuzden iki
etiketi GETIRI uzerinden kiyaslamak yine karisim uretir, yine sifir cikar.

BU YUZDEN SORU DEGISTI:
   ESKI (tuzakli) : "izin=sezon mu, izin=sezon VE hava mi daha cok kazandirir?"
   YENI (temiz)   : "etiket, BOGA oldugunu ne kadar DOGRU ve ne kadar ZAMANINDA
                     soyluyor?"

Olculen sey SAYIM istatistigi (gecikme, kapsama, yanlis alarm) — ortalama getiri
DEGIL. Yogunlasma ve karisim sorunu buraya bulasmaz, cunku hicbir yerde
sembol-uzeri getiri ortalamasi alinmiyor.

GERCEK BOGA TANIMI (etiketten BAGIMSIZ, ileri getiriye dayali):
   bir gun "yukselis gunu"dur  <=>  BTC'nin SONRAKI 7 gunluk getirisi >= +%3
Bu tanim etiketi kullanmiyor -> dairesellik yok.

SALT OKUMA.
"""
import os, json, datetime, statistics as sx, collections

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
KLINE = os.path.join(SCRATCH, "klines_1h_uzun")

ILERI_GUN = 7
ILERI_ESIK = 3.0
OLU_BANT = 2.0
HIST = 3


def gunluk_btc():
    with open(os.path.join(KLINE, "BTC.json"), encoding="utf-8") as f:
        b = json.load(f)
    g = collections.OrderedDict()
    for x in b:
        d = datetime.datetime.fromtimestamp(x["t"] / 1000).strftime("%Y-%m-%d")
        g[d] = x["c"]                       # gunun SON kapanisi
    return list(g.items())


def haftalik_sezon(gun, i):
    """Haftalik kapanis vs son 20 hafta ort + egim (evren.py mantigi, gunlukten)."""
    if i < 21 * 7:
        return "?"
    hafta = [gun[j][1] for j in range(i, max(-1, i - 21 * 7), -7)][::-1]
    if len(hafta) < 21:
        return "?"
    ort = sx.mean(hafta[-21:-1])
    egim = hafta[-1] - hafta[-21]
    if hafta[-1] > ort and egim > 0:
        return "BOGA"
    if hafta[-1] < ort and egim < 0:
        return "AYI"
    return "NOTR"


def etiketler(gun):
    """Her gun icin: sezon · ham hava · histerezisli hava · iki KURAL."""
    n = len(gun)
    ham = [None] * n
    for i in range(20, n):
        sma = sx.mean(x[1] for x in gun[i - 20:i])
        uz = (gun[i][1] - sma) / sma * 100
        ham[i] = "NOTR" if abs(uz) < OLU_BANT else ("BOGA" if uz > 0 else "AYI")
    hava = [None] * n
    son = None
    for i in range(n):
        if ham[i] is None:
            continue
        if i >= HIST and all(ham[j] == ham[i] for j in range(i - HIST + 1, i + 1)):
            son = ham[i]
        elif son is None:
            son = ham[i]
        hava[i] = son
    out = []
    for i in range(n):
        sez = haftalik_sezon(gun, i)
        h = hava[i]
        # MEVCUT KURAL: sezon VE hava ikisi de BOGA
        mevcut = "BOGA" if (sez == "BOGA" and h == "BOGA") else "DIGER"
        # ONERI: yalniz sezon
        oneri = "BOGA" if sez == "BOGA" else "DIGER"
        # UCUNCU: sezon BOGA ve HAM hava (histerezissiz) BOGA
        hamk = "BOGA" if (sez == "BOGA" and ham[i] == "BOGA") else "DIGER"
        out.append({"gun": gun[i][0], "fiyat": gun[i][1], "sezon": sez,
                    "hava": h, "ham": ham[i],
                    "MEVCUT": mevcut, "ONERI_sezon": oneri, "HAMHAVA": hamk})
    return out


def gercek(gun):
    """Etiketten BAGIMSIZ: sonraki 7 gun >= +%3 ise 'yukselis gunu'."""
    n = len(gun)
    out = [None] * n
    for i in range(n - ILERI_GUN):
        a, b = gun[i][1], gun[i + ILERI_GUN][1]
        out[i] = ((b - a) / a * 100) >= ILERI_ESIK
    return out


def kalite(et, gr, anahtar):
    tp = fp = fn = tn = 0
    for e, g in zip(et, gr):
        if g is None or e["sezon"] == "?":
            continue
        p = e[anahtar] == "BOGA"
        if p and g:
            tp += 1
        elif p and not g:
            fp += 1
        elif (not p) and g:
            fn += 1
        else:
            tn += 1
    top = tp + fp + fn + tn
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "n": top,
            "kesinlik": 100 * tp / (tp + fp) if tp + fp else 0,
            "kapsama": 100 * tp / (tp + fn) if tp + fn else 0,
            "acik_gun": 100 * (tp + fp) / top if top else 0}


def gecikme(et, gun, anahtar):
    """Her GERCEK yukselis epizodunun basindan etiketin acilmasina kac gun?"""
    fiy = [x[1] for x in gun]
    epi, i = [], 0
    while i < len(fiy) - ILERI_GUN:
        a, b = fiy[i], fiy[i + ILERI_GUN]
        if (b - a) / a * 100 >= ILERI_ESIK:
            epi.append(i)
            i += ILERI_GUN
        else:
            i += 1
    gec, kacan = [], 0
    for j in epi:
        bul = None
        for k in range(j, min(j + 21, len(et))):
            if et[k]["sezon"] != "?" and et[k][anahtar] == "BOGA":
                bul = k - j
                break
        if bul is None:
            kacan += 1
        else:
            gec.append(bul)
    return {"epizot": len(epi), "gecikme_medyan": sx.median(gec) if gec else None,
            "gecikme_ort": sx.mean(gec) if gec else None,
            "hemen": sum(1 for x in gec if x == 0), "kacirilan": kacan}


if __name__ == "__main__":
    gun = gunluk_btc()
    print("=" * 92)
    print("REJIM ETIKETI — TESPIT KALITESI (getiri DEGIL, sayim)")
    print("=" * 92)
    print("BTC gunluk: %d gun  %s -> %s" % (len(gun), gun[0][0], gun[-1][0]))
    print("GERCEK 'yukselis gunu' tanimi: sonraki %d gun >= +%%%.0f (etiketten BAGIMSIZ)"
          % (ILERI_GUN, ILERI_ESIK))
    et = etiketler(gun)
    gr = gercek(gun)
    ger_say = sum(1 for x in gr if x)
    print("gercek yukselis gunu: %d / %d (%%%.0f)"
          % (ger_say, sum(1 for x in gr if x is not None),
             100 * ger_say / max(1, sum(1 for x in gr if x is not None))))

    print("\n%-22s %8s %8s %9s %9s %9s" % ("kural", "kesinlik", "kapsama", "acik gun%", "yanlis+", "kacan"))
    print("-" * 72)
    for ad, k in (("MEVCUT (sezon VE hava)", "MEVCUT"),
                  ("ONERI (yalniz sezon)", "ONERI_sezon"),
                  ("sezon VE ham hava", "HAMHAVA")):
        q = kalite(et, gr, k)
        print("%-22s %7.1f%% %7.1f%% %8.1f%% %9d %9d" %
              (ad, q["kesinlik"], q["kapsama"], q["acik_gun"], q["fp"], q["fn"]))

    print("\n%-22s %8s %10s %10s %8s %9s" % ("kural", "epizot", "gecikme-med", "gecikme-ort", "hemen", "kacirilan"))
    print("-" * 72)
    for ad, k in (("MEVCUT (sezon VE hava)", "MEVCUT"),
                  ("ONERI (yalniz sezon)", "ONERI_sezon"),
                  ("sezon VE ham hava", "HAMHAVA")):
        d = gecikme(et, gun, k)
        print("%-22s %8d %10s %10s %8d %9d" %
              (ad, d["epizot"],
               "%.1f gun" % d["gecikme_medyan"] if d["gecikme_medyan"] is not None else "-",
               "%.1f gun" % d["gecikme_ort"] if d["gecikme_ort"] is not None else "-",
               d["hemen"], d["kacirilan"]))

    print("\n--- BUGUN ---")
    for e in et[-4:]:
        print("  %s  fiyat %8.0f  sezon %-5s hava %-5s ham %-5s | MEVCUT %-5s ONERI %-5s"
              % (e["gun"], e["fiyat"], e["sezon"], e["hava"], e["ham"], e["MEVCUT"], e["ONERI_sezon"]))
    print("\nbot dosyalarina yazim: YOK")
