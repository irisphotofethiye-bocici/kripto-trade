#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASAMA 1b — OI · LONG/SHORT · TAKER: pozisyon boyunca ve STOPTAN ONCE.

SORU: "o sirada hacim, funding gibi olctugumuz karar verme verilerindeki
degisiklikleri ve BIRBIRLERINE ORANI seklinde arastir. Sert dusus yada cikis
yapmadan biraz once ongorebilir miyiz?"

VERI: scratchpad/perp_seri/ (5 dk, Binance futures/data, 29 gunluk pencere).
  ⚠️ izleyici'nin oi3/top_ls/glob_ls alanlari RADARDAN KOPYA (donmus) — kullanilmaz.

OLCULEN ORANLAR — hepsi ham degil, ORAN/DEGISIM:
  oi_degisim / fiyat_degisim   klasik okuma: fiyat dus + OI dus = tasfiye (saglikli)
                                             fiyat dus + OI art = yeni konumlanma
  top_ls - glob_ls             "akilli" ile "kalabalik" arasindaki fark
  taker_orani (buy/sell)       geri cekilmede alici hala agresif mi
  hacim_5m / pozisyon_ort      hareket hacimle mi geliyor

KONTROL ZORUNLU: stoptan onceki pencere, AYNI POZISYONUN kendi erken penceresiyle
  kiyaslanir (sembol/rejim/oynaklik karistiricilarini pozisyon-ici sabitler).

HUKUM YAZMAZ — N kucuk. Hipotez uretir.
SALT OKUMA.
"""
import os, sys, statistics as sx, collections, random

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ortak                                                    # noqa: E402

random.seed(7)
ONCE_DK = 30          # "sert hareketten biraz once" penceresi
ADIM_DK = 5


def _seri_degisim(seri, alan, i0, i1):
    """i0 -> i1 arasindaki YUZDE degisim. Deger yoksa None."""
    a = seri[i0].get(alan)
    b = seri[i1].get(alan)
    if a is None or b is None or a == 0:
        return None
    return (b - a) / abs(a) * 100


def pencere_olcumu(seri, i_son, n_adim):
    """[i_son-n_adim, i_son] penceresinde degiskenlerin degisimi ve oranlari."""
    i0 = max(0, i_son - n_adim)
    if i_son - i0 < 2:
        return None
    d_fiyat = _seri_degisim(seri, "fiyat", i0, i_son)
    d_oi = _seri_degisim(seri, "oi_s", i0, i_son)
    if d_fiyat is None:
        return None
    o = {"d_fiyat": d_fiyat, "d_oi": d_oi}
    # ORAN: OI degisimi / fiyat degisimi  (fiyat ~0 iken tanimsiz -> atla)
    if d_oi is not None and abs(d_fiyat) > 0.05:
        o["oi_fiyat_orani"] = d_oi / d_fiyat
    for a, ad in (("top_ls_s", "d_top_ls"), ("glob_ls_s", "d_glob_ls"),
                  ("taker_orani_s", "d_taker_orani"), ("hacim_5m_s", "d_hacim")):
        o[ad] = _seri_degisim(seri, a, i0, i_son)
    # SEVIYE farki: akilli - kalabalik
    t, g = seri[i_son].get("top_ls_s"), seri[i_son].get("glob_ls_s")
    if t is not None and g is not None:
        o["top_eksi_glob"] = t - g
    o["taker_orani"] = seri[i_son].get("taker_orani_s")
    o["taker_15"] = seri[i_son].get("taker_15")
    o["hacim_x"] = seri[i_son].get("hacim_x")
    return o


def _tablo(baslik, olay, kontrol, alanlar):
    print("\n%s" % baslik)
    print("%-18s %10s %10s %10s %8s" % ("degisken", "OLAY", "KONTROL", "fark", "N"))
    print("-" * 60)
    for a in alanlar:
        o = [x[a] for x in olay if x.get(a) is not None]
        k = [x[a] for x in kontrol if x.get(a) is not None]
        if len(o) < 5 or len(k) < 5:
            print("%-18s %10s %10s %10s %8s" % (a, "-", "-", "-", "N az"))
            continue
        mo, mk = sx.median(o), sx.median(k)
        print("%-18s %+10.3f %+10.3f %+10.3f %8s"
              % (a, mo, mk, mo - mk, "%d/%d" % (len(o), len(k))))


def main():
    poz = ortak.pozisyonlar(en_az_goruntu=12)
    kapsamli = [p for p in poz if sum(1 for g in p["seri"] if "oi_s" in g) >= 10]
    print("=" * 80)
    print("ASAMA 1b — OI · LONG/SHORT · TAKER")
    print("kapali pozisyon %d · OI serisi yeterli olan %d" % (len(poz), len(kapsamli)))
    print("=" * 80)
    if len(kapsamli) < 10:
        print("\nOI kapsami yetersiz — perp_seri indirmesi bitmemis olabilir.")
        print("kontrol: python scratchpad/perp_seri_indir.py --rapor")
        return

    n_adim = ONCE_DK // ADIM_DK

    # ---------- 1) POZISYON BOYUNCA ORTALAMA DEGISIM, SONUCA GORE ----------
    print("\n1) POZISYON BASINDAN SONUNA — sonuca gore")
    print("%-14s %4s %9s %9s %9s %9s" % ("sebep", "N", "d_fiyat%", "d_OI%", "OI/fiyat", "d_taker%"))
    print("-" * 60)
    g = collections.defaultdict(list)
    for p in kapsamli:
        s = p["seri"]
        o = pencere_olcumu(s, len(s) - 1, len(s) - 1)
        if o:
            g[p["sonuc"]["sebep"]].append(o)
    for sebep in sorted(g, key=lambda k: -len(g[k])):
        v = g[sebep]
        def med(a):
            x = [z[a] for z in v if z.get(a) is not None]
            return sx.median(x) if len(x) >= 3 else float("nan")
        print("%-14s %4d %+9.2f %+9.2f %+9.2f %+9.2f"
              % (sebep, len(v), med("d_fiyat"), med("d_oi"),
                 med("oi_fiyat_orani"), med("d_taker_orani")))

    # ---------- 2) STOPTAN ONCEKI 30 DK vs AYNI POZISYONUN ERKEN PENCERESI ----------
    print("\n2) STOPTAN ONCEKI %d DK  vs  AYNI POZISYONUN ERKEN PENCERESI" % ONCE_DK)
    print("   (kontrol pozisyon-ICI: sembol · rejim · oynaklik sabit)")
    olay, kontrol = [], []
    for p in kapsamli:
        if "STOP" not in (p["sonuc"]["sebep"] or ""):
            continue
        s = p["seri"]
        if len(s) < 2 * n_adim + 3:
            continue
        o = pencere_olcumu(s, len(s) - 1, n_adim)
        if o:
            olay.append(o)
        # kontrol: pozisyonun ERKEN yarisindan rastgele bir pencere
        i = random.randint(n_adim, max(n_adim, len(s) // 2))
        k = pencere_olcumu(s, i, n_adim)
        if k:
            kontrol.append(k)
    _tablo("   medyanlar:", olay, kontrol,
           ["d_fiyat", "d_oi", "oi_fiyat_orani", "d_top_ls", "d_glob_ls",
            "d_taker_orani", "d_hacim", "top_eksi_glob", "taker_orani", "hacim_x"])
    print("   NOT: 'fark' sutunu buyuk degilse ONCU YOK demektir; N=%d cok kucuk." % len(olay))

    # ---------- 3) TP2 ile BITENLERDE AYNI PENCERE ----------
    print("\n3) TP2 ile bitenlerde SON %d DK (kazanan taraf nasil gorunuyor)" % ONCE_DK)
    tp, tpk = [], []
    for p in kapsamli:
        if not (p["sonuc"]["sebep"] or "").startswith("TP2"):
            continue
        s = p["seri"]
        if len(s) < 2 * n_adim + 3:
            continue
        o = pencere_olcumu(s, len(s) - 1, n_adim)
        if o:
            tp.append(o)
        i = random.randint(n_adim, max(n_adim, len(s) // 2))
        k = pencere_olcumu(s, i, n_adim)
        if k:
            tpk.append(k)
    _tablo("   medyanlar:", tp, tpk,
           ["d_fiyat", "d_oi", "oi_fiyat_orani", "d_taker_orani", "d_hacim", "taker_orani"])

    print("\nbot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
