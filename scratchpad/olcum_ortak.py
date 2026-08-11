#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OLCUM ORTAK MODULU (2026-08-11) — denetim Bulgu 2, 7 ve kumelenme dersinin karsiligi.

NEDEN VAR: 2026-08-11 sistem denetimi uc tutarsizlik buldu:
  Bulgu 2  maliyet: 11 betik %0.09 kullaniyordu, canli gercek %0.13
           (taker %0.045 x2 + kayma %0.02 x2). Uc betikteki "0.04R" varsayimi
           ise ancak stop >= %3.25 iken dogru; stop %0.5'te gercek 0.26R -> 6.5 KAT hata.
  Bulgu 7  ATR: olcucu.py Wilder yumusatmasi kullaniyor, ~20 scratchpad betigi
           basit 14-bar ortalama. Medyan oran 1.015 ama vakalarin %39'unda fark >%10.
  Ders     Sembol kumelenmesi: 41 betikten yalniz 2'si hucre basina AYRI SEMBOL
           sayiyordu. N=113 gorunen bir hucre 8 sembolden geliyorsa t-degeri SISER
           (2026-08-11'de LONG hucresinde tam bu yasandi).

ESKI BETIKLER BILEREK DEGISTIRILMEDI: defterdeki sayilarin yeniden uretilebilir
kalmasi icin. Bu modul BUNDAN SONRAKI olcumler icindir; eski sonuclarin %0.04'luk
duzeltmesi defterde ayrica kayitli.

Kullanim:
    import olcum_ortak as oo
    a  = oo.atr(barlar, i)              # Wilder — canli botla AYNI
    m  = oo.MALIYET                     # %0.13 gidis-donus
    oz = oo.ozet(getiriler, semboller)  # n, ort, t VE ayri sembol sayisi
"""
import os, json, statistics as stx, collections

# --- canli botun gercekte odedigi (kripto-config.json -> maliyet) -----------------
TAKER_PCT = 0.045          # her bacakta
SLIPAJ_PCT = 0.02          # her bacakta (testbot.maliyet_uygula_giris/cikis)
MALIYET = round((TAKER_PCT + SLIPAJ_PCT) * 2, 4)      # = 0.13, gidis-donus


def maliyet_r(stop_pct):
    """Maliyetin R cinsinden karsiligi. SABIT DEGILDIR — stop mesafesine baglidir.
    Eski betiklerdeki sabit 0.04R varsayimi bu yuzden hatalidir."""
    return MALIYET / stop_pct if stop_pct and stop_pct > 0 else float("inf")


def atr(barlar, i=None, period=14):
    """WILDER ATR — olcucu.py:98 ile birebir ayni tanim.
    i verilirse barlar[:i+1] uzerinde hesaplar (backtest kullanimi)."""
    b = barlar if i is None else barlar[:i + 1]
    if len(b) < 2:
        return None
    trs = []
    for k in range(1, len(b)):
        h, l, pc = b[k]["h"], b[k]["l"], b[k - 1]["c"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    if not trs:
        return None
    if len(trs) < period:
        return stx.mean(trs)
    a = stx.mean(trs[:period])
    for tr in trs[period:]:
        a = (a * (period - 1) + tr) / period
    return a


def ozet(getiriler, semboller=None, asgari=40):
    """n · ortalama · standart hata · t  VE  ayri sembol sayisi.

    'semboller' verilirse kumelenme de raporlanir:
      ayri_sembol   : kac farkli sembolden geldi
      olay_sembol   : ortalama olay/sembol (1'e yakin = iyi, buyuk = kumelenmis)
      en_sik_5_pay  : en sik 5 sembolun toplam icindeki payi (%)
      t_kume        : sembol sayisina gore olceklenmis t (KABA ust sinir duzeltmesi;
                      bagimsiz birim sayisi N degil ~sembol sayisi ise t bu kadar kucur)
    """
    g = [x for x in getiriler if x is not None]
    if len(g) < asgari:
        return None
    sh = stx.pstdev(g) / len(g) ** 0.5 if len(g) > 1 else 0.0
    out = {"n": len(g), "ort": stx.mean(g), "med": stx.median(g), "sh": sh,
           "t": (stx.mean(g) / sh) if sh else 0.0}
    if semboller:
        c = collections.Counter(semboller)
        out["ayri_sembol"] = len(c)
        out["olay_sembol"] = len(semboller) / len(c) if c else 0.0
        out["en_sik_5_pay"] = sum(n for _, n in c.most_common(5)) / len(semboller) * 100
        out["en_sik"] = c.most_common(5)
        if len(c) > 1:
            out["t_kume"] = out["t"] * (len(c) / len(g)) ** 0.5
    return out


def satir(ad, o, genislik=30):
    """Tek satirlik rapor — sembol sutunu HER ZAMAN basilir."""
    if not o:
        return f"{ad:{genislik}}  (yetersiz N)"
    s = (f"{ad:{genislik}}{o['n']:6d}{o['ort']:+9.3f}{o['t']:+7.2f}")
    if "ayri_sembol" in o:
        s += (f"{o['ayri_sembol']:8d}{o['olay_sembol']:9.1f}"
              f"{o['en_sik_5_pay']:8.0f}%{o.get('t_kume', 0):+8.2f}")
    return s


BASLIK = (f"{'kume':30}{'N':>6}{'ort':>9}{'t':>7}"
          f"{'sembol':>8}{'olay/sem':>9}{'ilk5':>9}{'t_kume':>8}")


def basliksatiri(genislik=30):
    return BASLIK if genislik == 30 else (
        f"{'kume':{genislik}}{'N':>6}{'ort':>9}{'t':>7}"
        f"{'sembol':>8}{'olay/sem':>9}{'ilk5':>9}{'t_kume':>8}")


if __name__ == "__main__":
    print(f"MALIYET = %{MALIYET}  (taker {TAKER_PCT}x2 + kayma {SLIPAJ_PCT}x2)")
    print(f"  stop %0.5 -> maliyet {maliyet_r(0.5):.2f}R   "
          f"(eski betiklerin sabit varsayimi 0.04R -> {maliyet_r(0.5)/0.04:.1f} KAT hata)")
    print(f"  stop %3.25 -> maliyet {maliyet_r(3.25):.2f}R  (0.04R burada dogru)")
    print(f"  stop %8.0 -> maliyet {maliyet_r(8.0):.3f}R")
