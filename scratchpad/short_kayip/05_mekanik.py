#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEKANIK DENEMELERI — "kapilari kapatmak cozum degil"

AYNI girisler, HICBIRI elenmeden, farkli mekanikle yeniden oynatilir.
5 dakikalik mum · maliyet + FONLAMA dahil.

⚠️ PLANDAN SAPMA (ve sebebi): plan "stop x0,75 / x1,25 ..." diyordu, bu botun
ORIJINAL stopunu gerektirir. Defter stop fiyatini SAKLAMIYOR (yalniz state
saklar, o da acik pozisyonlar icin). Geri kurma denendi
(stop%% = equity x %1,5 / notional): r=+0,61, medyan sapma 2,44 puan —
mekanik denemesi icin YETERSIZ. Bunun yerine MUTLAK IZGARA kullaniliyor:
"stop %X, hedef %Y olsaydi ne olurdu". Daha yorumlanabilir ve geri kurmaya
muhtac degil.

RISK SABIT TUTULUR: her denemede islem basina ayni dolar riske edilir
(75 $), yani notional = 75 / stop%%. Boylece dar ve genis stop ADIL kiyaslanir.

SALT OKUMA.
"""
import sys, os, datetime, statistics as stx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ortak                                    # noqa: E402

RISK_USD = 75.0
UFUK_SA = 72
STOPLAR = [2, 3, 4, 5, 6, 8]
HEDEFLER = [3, 5, 7, 10, 15]


def oynat(p, stop_pct, hedef_pct, gecikme_dk=0, sure_saat=None, yon=None):
    """Tek girisi verilen mekanikle oynatir. -> net yuzde | None"""
    yon = yon or p["yon"]
    g0 = ortak.dt(p["giris_ts"]) + datetime.timedelta(minutes=gecikme_dk)
    bit = g0 + datetime.timedelta(hours=UFUK_SA)
    b = ortak.mumlar(p["sym"], g0 - datetime.timedelta(minutes=15), bit)
    t0 = int(g0.timestamp() * 1000)
    ic = [x for x in b if x["t"] >= t0]
    if len(ic) < 3:
        return None
    ref = ic[0]["o"]
    if ref <= 0:
        return None
    if yon == "SHORT":
        sp, hp = ref * (1 + stop_pct / 100), ref * (1 - hedef_pct / 100)
    else:
        sp, hp = ref * (1 - stop_pct / 100), ref * (1 + hedef_pct / 100)
    sinir = int((g0 + datetime.timedelta(hours=sure_saat)).timestamp() * 1000) \
        if sure_saat else None
    ham, cj = None, ic[-1]
    for x in ic:
        if sinir and x["t"] >= sinir:
            cj = x
            ham = ((ref - x["o"]) if yon == "SHORT" else (x["o"] - ref)) / ref * 100
            break
        vur_stop = (x["h"] >= sp) if yon == "SHORT" else (x["l"] <= sp)
        vur_hed = (x["l"] <= hp) if yon == "SHORT" else (x["h"] >= hp)
        if vur_stop:                       # ayni mumda ikisi de olursa STOP once
            cj, ham = x, -stop_pct
            break
        if vur_hed:
            cj, ham = x, hedef_pct
            break
    if ham is None:
        ham = ((ref - cj["c"]) if yon == "SHORT" else (cj["c"] - ref)) / ref * 100
    fon = ortak.fonlama_pct(ortak.fonlama(p["sym"]), t0, cj["t"], yon)
    return ham - ortak.MALIYET_PCT + fon


def dolar(net_pct, stop_pct):
    """Risk SABIT: notional = RISK / stop%%  ->  dolar = net%% x notional / 100"""
    return net_pct * (RISK_USD / (stop_pct / 100)) / 100


def kume_kostur(poz, fn):
    v = [fn(p) for p in poz]
    v = [x for x in v if x is not None]
    return v


def izgara(baslik, poz):
    print("\n" + "=" * 96)
    print("%s   N=%d" % (baslik, len(poz)))
    print("GERCEK sonuc: %+.2f $" % sum(p["pnl"] for p in poz))
    print("=" * 96)
    print("STOP/HEDEF IZGARASI — risk her hucrede SABIT %.0f $/islem" % RISK_USD)
    print("(hucre = toplam $ · parantez: islem basina net %%)\n")
    print("%-8s" % "stop\\hed" + "".join("%16s" % ("%%%d" % h) for h in HEDEFLER))
    en = []
    for s in STOPLAR:
        satir = "%-8s" % ("%%%d" % s)
        for h in HEDEFLER:
            v = kume_kostur(poz, lambda p, s=s, h=h: oynat(p, s, h))
            if not v:
                satir += "%16s" % "-"
                continue
            d = sum(dolar(x, s) for x in v)
            en.append((d, s, h, stx.mean(v), len(v)))
            satir += "%16s" % ("%+.0f (%+.2f)" % (d, stx.mean(v)))
        print(satir)
    en.sort(reverse=True)
    print("\n  EN IYI 3 hucre:")
    for d, s, h, m, n in en[:3]:
        print("     stop %%%d · hedef %%%d  ->  %+9.2f $  (islem basi %+.3f%%, N=%d)"
              % (s, h, d, m, n))
    print("  EN KOTU 1: stop %%%d · hedef %%%d -> %+.2f $" % (en[-1][1], en[-1][2], en[-1][0]))
    # botun kendi mekanigine en yakin hucre
    yak = [x for x in en if x[1] == 3 and x[2] == 10]
    if yak:
        print("  BOTUN mekanigine yakin (stop %%3 · hedef %%10): %+.2f $" % yak[0][0])
    return en


def digerleri(baslik, poz):
    print("\n--- %s : FILTRE OLMAYAN diger degisiklikler" % baslik)
    tab = [("stop %3 hedef %10 (referans)", dict(stop_pct=3, hedef_pct=10))]
    for dk in (15, 30, 60):
        tab.append(("+%d dk GECIKMELI giris" % dk, dict(stop_pct=3, hedef_pct=10, gecikme_dk=dk)))
    for sa in (1, 2, 4, 8, 24):
        tab.append(("%d saatte kosulsuz KAPAT" % sa, dict(stop_pct=3, hedef_pct=10, sure_saat=sa)))
    tab.append(("YON CEVIRME (ters islem)", dict(stop_pct=3, hedef_pct=10,
                                                 yon="LONG" if poz[0]["yon"] == "SHORT" else "SHORT")))
    for ad, kw in tab:
        v = kume_kostur(poz, lambda p, kw=kw: oynat(p, **kw))
        if not v:
            print("   %-32s -" % ad)
            continue
        d = sum(dolar(x, kw["stop_pct"]) for x in v)
        kz = sum(1 for x in v if x > 0)
        print("   %-32s %+9.2f $   islem basi %+6.3f%%   kazanan %2d/%2d (%%%.0f)  N=%d"
              % (ad, d, stx.mean(v), kz, len(v), 100 * kz / len(v), len(v)))


if __name__ == "__main__":
    poz = ortak.poz_yukle("muhasebe_11agu")
    for yon in ("SHORT", "LONG"):
        g = [p for p in poz if p["yon"] == yon]
        for dn, ad in ((None, "TUM DONEM"), ("oncesi", "sicrama ONCESI"),
                       ("sonrasi", "sicrama SONRASI")):
            gg = g if dn is None else [p for p in g if p["donem"] == dn]
            if len(gg) < 5:
                print("\n%s — %s: N=%d, atlandi" % (yon, ad, len(gg)))
                continue
            izgara("%s — %s" % (yon, ad), gg)
            digerleri("%s — %s" % (yon, ad), gg)
    print("\nbot dosyalarina yazim: YOK")
