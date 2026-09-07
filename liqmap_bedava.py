#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LIQMAP — BEDAVA SURUM (Binance aggTrades'ten, Apify'siz)

NEDEN: apify_liq.py cagri basina ~0,01 USD odeyip CoinGlass'in haritasini
aliyor. py-liquidation-map (aoki-h-jp) reposu incelendi ve haritanin
formulu goruldu — sirri yok:

    ALICI agresor islem  ->  likidasyon SEVIYELERI  fiyat x 0,99 / 0,98 / 0,96 / 0,90
    SATICI agresor islem ->                         fiyat x 1,01 / 1,02 / 1,04 / 1,10
    (sirasiyla varsayilan 100x · 50x · 25x · 10x kaldirac)
    agirlik = islem hacmi (fiyat x miktar)

🔴 BU YUZDEN NE OLDUGUNU BILEREK KULLAN: harita, BUYUK ISLEMLERIN FIYAT
HISTOGRAMININ dort sabitle kaydirilmis halidir. Girdisi yalnizca `fiyat` ve
`hacim`. Gercek kaldirac, gercek pozisyon, OI KULLANILMAZ — varsayilir.
Yani bant-disi bir bilgi DEGILDIR (CLAUDE.md: "her sey tek banttan turuyor").
Olcum iddiasi YOKTUR; baglam katmanidir.

Veri: Binance fapi /aggTrades (ANAHTARSIZ, UCRETSIZ).
Yuk olculdu: ARKM 16 cagri · MINA 54 · ICP 89 · TIA 170 · WLD 195 · BTC 698.

Kullanim:
  python liqmap_bedava.py --symbol TIA
  python liqmap_bedava.py --symbol ICP --saat 12 --esik 50000
  python liqmap_bedava.py --symbol WLD --poz          # acik pozisyonla hizala

SALT-OKUNUR. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, time, argparse, collections
import urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
FAPI = "https://fapi.binance.com/fapi/v1"

# py-liquidation-map (aoki-h-jp) mapping.py:193-211 ile BIREBIR ayni katsayilar
KADEME = [("100x", 0.99, 1.01), ("50x", 0.98, 1.02),
          ("25x", 0.96, 1.04), ("10x", 0.90, 1.10)]


def _get(url, deneme=0):
    try:
        r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(r, timeout=25) as x:
            return json.loads(x.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (429, 418) and deneme < 4:
            time.sleep(5 * (deneme + 1))
            return _get(url, deneme + 1)
        raise
    except Exception:
        if deneme < 3:
            time.sleep(2)
            return _get(url, deneme + 1)
        raise


def fiyat(sym):
    return float(_get("%s/ticker/price?symbol=%sUSDT" % (FAPI, sym))["price"])


def buyuk_islemler(sym, saat, esik_usd, ilerleme=True, pay=None):
    """Son `saat` saatteki islemler.

    esik_usd: mutlak USD esigi (repo 'gross_value' modu)
    pay     : verilirse EN BUYUK %pay islem alinir (repo 'portion' modu)
              -> sembolden sembole kendi kendine olceklenir
    -> ([(fiyat, notional, alici_agresor_mu)], cagri, secilen_esik)"""
    bit = int(time.time() * 1000)
    bas = bit - int(saat * 3600 * 1000)
    out = []
    cur = bas
    cagri = 0
    son_id = None
    while cur < bit:
        if son_id is None:
            u = "%s/aggTrades?symbol=%sUSDT&startTime=%d&endTime=%d&limit=1000" % (
                FAPI, sym, cur, min(cur + 3600000, bit))
        else:
            u = "%s/aggTrades?symbol=%sUSDT&fromId=%d&limit=1000" % (FAPI, sym, son_id + 1)
        d = _get(u)
        cagri += 1
        if not d:
            if son_id is None:
                cur += 3600000
                continue
            break
        for t in d:
            ts = int(t["T"])
            if ts > bit:
                break
            p = float(t["p"])
            n = p * float(t["q"])
            # m=True -> ALICI maker, yani agresor SATICI
            out.append((p, n, not bool(t["m"])))
        son_id = int(d[-1]["a"])
        cur = int(d[-1]["T"])
        if int(d[-1]["T"]) >= bit:
            break
        if ilerleme and cagri % 40 == 0:
            print("   ... %d cagri · %d islem" % (cagri, len(out)))
        time.sleep(0.06)
    if pay is not None and out:
        # 'portion' modu: en buyuk %pay islem -> esik VERIDEN gelir, secilmez
        boy = sorted((x[1] for x in out), reverse=True)
        k = max(1, int(len(boy) * pay / 100.0))
        esik_usd = boy[k - 1]
    secili = [x for x in out if x[1] >= esik_usd]
    return secili, cagri, esik_usd


def harita(islemler, px, kova_pct=0.25):
    """Likidasyon seviyelerini kovalayip hacimle agirlikla.
    -> {kova_ortasi: toplam_usd}"""
    kv = collections.defaultdict(float)
    adim = px * kova_pct / 100.0
    for p, n, alici in islemler:
        for _ad, asagi, yukari in KADEME:
            lvl = p * (asagi if alici else yukari)
            kv[round(lvl / adim) * adim] += n
    return kv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--saat", type=float, default=24.0)
    ap.add_argument("--esik", type=float, default=100000.0,
                    help="asgari islem buyuklugu USD (repo 'gross_value' modu)")
    ap.add_argument("--pay", type=float, default=None,
                    help="en buyuk %%pay islemi al (repo 'portion' modu). "
                         "Sembolden sembole kendi kendine olceklenir. Orn: --pay 1")
    ap.add_argument("--poz", action="store_true",
                    help="notrlong_state.json'daki acik pozisyonla hizala")
    ap.add_argument("--n", type=int, default=5)
    a = ap.parse_args()
    sym = a.symbol.upper()

    print("=" * 92)
    print("LIQMAP (BEDAVA) — %s · son %.0f saat · %s"
          % (sym, a.saat,
             ("en buyuk %%%.2f islem" % a.pay) if a.pay else
             ("esik %s $" % "{:,.0f}".format(a.esik))))
    print("kaynak: Binance aggTrades · formul: py-liquidation-map ile ayni")
    print("=" * 92)

    px = fiyat(sym)
    t0 = time.time()
    isl, cagri, esik_efektif = buyuk_islemler(sym, a.saat, a.esik, pay=a.pay)
    if not isl:
        print("   esigi gecen islem YOK — esigi dusur (--esik)")
        return
    alici = sum(1 for _, _, x in isl if x)
    print("   %d cagri · %.0f sn · secilen %d islem (alici agresor %d · satici %d)"
          % (cagri, time.time() - t0, len(isl), alici, len(isl) - alici))
    print("   efektif esik: %s $" % "{:,.0f}".format(esik_efektif))
    print("   anlik fiyat %.6f" % px)

    kv = harita(isl, px)
    ust = sorted([(k, v) for k, v in kv.items() if k > px], key=lambda z: -z[1])[:a.n]
    alt = sorted([(k, v) for k, v in kv.items() if k < px], key=lambda z: -z[1])[:a.n]
    ust.sort(key=lambda z: z[0])
    alt.sort(key=lambda z: -z[0])

    poz = None
    if a.poz:
        try:
            st = json.load(io.open(os.path.join(HERE, "notrlong_state.json"), encoding="utf-8"))
            poz = next((p for p in st.get("acik_pozisyonlar", []) if p["sym"] == sym), None)
        except Exception:
            poz = None
        if poz:
            print("   POZ: giris %.6f · stop %.6f · tetik %s · hedef %.6f"
                  % (poz["giris"], poz["stop"], poz.get("kilit_tetik"), poz["tp2"]))
        else:
            print("   (bu sembolde acik pozisyon yok)")

    print()
    print("   %12s %16s %11s   %s" % ("seviye", "buyukluk $", "fiyattan", "isaret"))
    for k, v in reversed(ust):
        print("   %12.6f %16s %+10.2f%%   %s" % (k, "{:,.0f}".format(v), (k / px - 1) * 100,
                                                 _im(k, poz, px)))
    print("   %12.6f %16s %+10.2f%%   << ANLIK" % (px, "-", 0.0))
    for k, v in alt:
        print("   %12.6f %16s %+10.2f%%   %s" % (k, "{:,.0f}".format(v), (k / px - 1) * 100,
                                                 _im(k, poz, px)))
    print()
    print("⚠️ Bu harita FIYAT + HACIM'in donusumudur; gercek kaldirac/pozisyon")
    print("   KULLANILMAZ, varsayilir. Olcum iddiasi yoktur — baglam katmanidir.")
    print("Maliyet: 0 USD · Bot dosyalarina yazim: YOK")


def _im(k, poz, px):
    if not poz:
        return ""
    im = []
    for ad, v in (("STOP", poz.get("stop")), ("TETIK", poz.get("kilit_tetik")),
                  ("HEDEF", poz.get("tp2")), ("GIRIS", poz.get("giris"))):
        if v and abs(k / v - 1) < 0.008:
            im.append("~" + ad)
    s = poz.get("stop")
    if s and s < k < px:
        im.append("stop ile fiyat ARASINDA")
    elif s and k < s:
        im.append("stopun altinda")
    return " · ".join(im)


if __name__ == "__main__":
    main()
