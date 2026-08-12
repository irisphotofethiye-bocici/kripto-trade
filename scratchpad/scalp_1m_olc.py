#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SCALP — 1 DAKIKALIK KESIN OLCUM (2026-08-12)

Onceki 1 saatlik olcum bar ICINDE sirayi bilemedigi icin KOTUMSER varsayimla
"ikisi de gorulduyse STOP" saymisti -> sonuc ALT SINIRDI (en iyi hucre -0.168).

Bu olcum 1 DAKIKALIK barlarla sirayi TAM gorur. Yani gercek cevap, alt sinir degil.

Ornek: 4.498 kayit · kapi x rejim basina ~500 (REJIME ESIT — kullanicinin
"6 ay esit sinama olmaz, ayi sadece" uyarisi uzerine boyle tasarlandi).
Giris = sinyal barinin SONRAKI barinin acilisi (botun kullandigi fiyat).
Salt-okunur.
"""
import json, os, sys, statistics as stx, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olcum_ortak as oo

BURA = os.path.dirname(os.path.abspath(__file__))
ORNEK = os.path.join(BURA, "scalp_1m", "ornekler.json")
UFUKLAR_DK = (15, 30, 60, 120, 240)


def sonuc(bars, hedef, stop, ufuk_dk):
    """SHORT. Dakika dakika: hedef mi stop mu ONCE? Ayni dakikada ikisi de -> STOP (kotumser,
    ama artik cok nadir cunku 1 dakikalik bar araligi kucuk)."""
    if not bars:
        return None
    ref = bars[0]["o"]
    if ref <= 0:
        return None
    h = ref * (1 - hedef / 100)
    s = ref * (1 + stop / 100)
    for x in bars[:ufuk_dk]:
        if x["h"] >= s:
            return "STOP"
        if x["l"] <= h:
            return "HEDEF"
    return "ZAMAN"


def mfe_mae(bars, ufuk_dk):
    if not bars:
        return None
    ref = bars[0]["o"]
    if ref <= 0:
        return None
    d = bars[:ufuk_dk]
    return ((ref - min(x["l"] for x in d)) / ref * 100,
            (max(x["h"] for x in d) - ref) / ref * 100)


def main():
    d = json.load(open(ORNEK, encoding="utf-8"))
    print("=" * 106)
    print("SCALP — 1 DAKIKALIK KESIN OLCUM (sira TAM biliniyor, alt sinir DEGIL)")
    print("=" * 106)
    print(f"Ornek {len(d)} · rejime esit bolunmus · maliyet %{oo.MALIYET}\n")

    kapi_list = ("A+B", "MA50", "KONTROL")
    print("### 1) MFE / MAE — ince cozunurluk (ilk kez 15 ve 30 dakika gorulebiliyor)")
    print(f"{'kapi':10}{'ufuk':>7}{'MFE med':>10}{'MAE med':>10}{'MFE/MAE':>10}"
          f"{'>= +%0.5':>10}{'>= +%1':>9}")
    print("-" * 106)
    for k in kapi_list:
        v = [x for x in d if x["kapi"] == k]
        for u in UFUKLAR_DK:
            r = [mfe_mae(x.get("bars"), u) for x in v]
            r = [z for z in r if z]
            if len(r) < 100:
                continue
            mfe = [z[0] for z in r]; mae = [z[1] for z in r]
            mm, ma_ = stx.median(mfe), stx.median(mae)
            print(f"{k:10}{u:>5}dk{mm:10.2f}{ma_:10.2f}{(mm/ma_ if ma_ else 0):10.2f}"
                  f"{sum(1 for z in mfe if z >= 0.5)/len(mfe)*100:9.0f}%"
                  f"{sum(1 for z in mfe if z >= 1.0)/len(mfe)*100:8.0f}%")
        print()

    print("=" * 106)
    print("### 2) ASIL TABLO — hedef stoptan ONCE mi? (KESIN sira, ilk 4 saat)")
    print("=" * 106)
    en_iyi = {}
    for k in kapi_list:
        v = [x for x in d if x["kapi"] == k]
        print(f"\n{k}   N={len(v)}")
        print(f"{'hedef':>7}{'stop':>7}{'hedef%':>9}{'stop%':>8}{'zaman%':>9}{'BEKLENTI':>11}")
        print("-" * 106)
        for hedef in (0.5, 1.0, 1.5, 2.0, 3.0):
            for stop in (0.5, 1.0, 1.5, 2.0):
                c = collections.Counter()
                for x in v:
                    r = sonuc(x.get("bars"), hedef, stop, 240)
                    if r:
                        c[r] += 1
                n = sum(c.values())
                if n < 100:
                    continue
                ph, ps = c["HEDEF"] / n, c["STOP"] / n
                bek = ph * (hedef - oo.MALIYET) - ps * (stop + oo.MALIYET)
                if bek > en_iyi.get(k, (-99,))[0]:
                    en_iyi[k] = (bek, hedef, stop, ph, ps)
                im = " *" if bek > 0 else ""
                print(f"{hedef:6.1f}%{stop:6.1f}%{ph*100:8.0f}%{ps*100:7.0f}%"
                      f"{c['ZAMAN']/n*100:8.0f}%{bek:+11.3f}{im}")

    print("\n" + "=" * 106)
    print("### 3) ALT SINIR vs GERCEK — 1 saatlik olcum ne kadar kotumserdi?")
    print("=" * 106)
    print(f"{'kapi':10}{'1 saatlik (alt sinir)':>24}{'1 dakikalik (gercek)':>24}{'fark':>10}")
    print("-" * 106)
    ALT = {"A+B": -0.168, "MA50": -0.199, "KONTROL": -0.094}
    for k in kapi_list:
        if k in en_iyi:
            b, h, s, ph, ps = en_iyi[k]
            print(f"{k:10}{ALT[k]:>24.3f}{b:>24.3f}{b-ALT[k]:>+10.3f}"
                  f"   (en iyi {h:.1f}/{s:.1f}, hedef %{ph*100:.0f} / stop %{ps*100:.0f})")

    print("\n" + "=" * 106)
    print("### 4) REJIME GORE — en iyi hucre her rejimde ne yapiyor?")
    print("=" * 106)
    print(f"{'kapi':10}{'rejim':7}{'N':>6}{'hedef%':>9}{'stop%':>8}{'BEKLENTI':>11}")
    print("-" * 106)
    for k in kapi_list:
        if k not in en_iyi:
            continue
        _, hedef, stop, _, _ = en_iyi[k]
        for r in ("BOGA", "NOTR", "AYI"):
            v = [x for x in d if x["kapi"] == k and x["rejim"] == r]
            c = collections.Counter()
            for x in v:
                z = sonuc(x.get("bars"), hedef, stop, 240)
                if z:
                    c[z] += 1
            n = sum(c.values())
            if n < 50:
                continue
            ph, ps = c["HEDEF"] / n, c["STOP"] / n
            bek = ph * (hedef - oo.MALIYET) - ps * (stop + oo.MALIYET)
            im = " *" if bek > 0 else ""
            print(f"{k:10}{r:7}{n:6d}{ph*100:8.0f}%{ps*100:7.0f}%{bek:+11.3f}{im}"
                  f"   (hedef {hedef:.1f} / stop {stop:.1f})")
        print()


if __name__ == "__main__":
    main()
