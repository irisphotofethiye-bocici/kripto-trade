#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACIK POZISYONLAR ICIN LIQMAP — duzeltilmis cikarma

🔴 apify_liq.py'deki KUSUR: once KURESEL en buyuk 12 kume aliniyor, SONRA
fiyata gore ikiye bolunuyor. On ikisi de bir tarafta cikarsa oteki taraf
BOS gorunuyor ve "orada miknatis yok" sanIliyor. (ICP'de bugun oldu.)
DUZELTME: ustten AYRI 5, alttan AYRI 5.

UCRETLI: her sembol ~0,01 USD (Apify FREE, aylik tavan 5 USD).
Kullanici ONAYLADI: "liqmapi de kullan".
Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, sys, time, datetime as dt
import urllib.request, urllib.error

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURA))
ACTOR = "api_merge~coinglass-liquidation-heatmap"


def cfg():
    return json.load(io.open(os.path.join(KOK, "kripto-config.json"), encoding="utf-8"))


def liqmap(sym, tok, interval="24h"):
    body = json.dumps({"symbol": sym, "model": "model1", "interval": interval}).encode()
    req = urllib.request.Request(
        "https://api.apify.com/v2/acts/%s/run-sync-get-dataset-items" % ACTOR,
        data=body, headers={"Authorization": "Bearer " + tok,
                            "Content-Type": "application/json"}, method="POST")
    res = None
    for deneme in range(4):
        try:
            res = json.load(urllib.request.urlopen(req, timeout=180))
            break
        except Exception as e:
            if deneme == 3:
                return None, str(e)[:90]
            time.sleep(6 * (deneme + 1))
            req = urllib.request.Request(
                "https://api.apify.com/v2/acts/%s/run-sync-get-dataset-items" % ACTOR,
                data=body, headers={"Authorization": "Bearer " + tok,
                                    "Content-Type": "application/json"}, method="POST")
    if not (isinstance(res, list) and res and res[0].get("success")):
        return None, "veri gelmedi"
    o = res[0]
    y = o.get("y_axis", [])
    agg = [0.0] * len(y)
    for row in o.get("liquidation_leverage_data", []):
        try:
            yi = int(row[1])
            if 0 <= yi < len(y):
                agg[yi] += float(row[2] or 0)
        except Exception:
            pass
    return (y, agg), None


def main():
    tok = cfg().get("apify_token", "")
    if not tok:
        sys.exit("apify_token BOS")
    st = json.load(io.open(os.path.join(KOK, "notrlong_state.json"), encoding="utf-8"))
    poz = st.get("acik_pozisyonlar", [])
    if len(sys.argv) > 1:
        istek = set(sys.argv[1].split(","))
        poz = [x for x in poz if x["sym"] in istek]

    print("=" * 100)
    print("ACIK POZISYONLAR — LIQMAP (duzeltilmis cikarma)  %s"
          % dt.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("=" * 100)

    cikti, harcanan = [], 0.0
    for p in poz:
        sym = p["sym"]
        if not sym.isascii():
            print("\n--- %s: ASCII olmayan sembol, Apify aktoru desteklemez -> ATLANDI" % sym)
            continue
        d, err = liqmap(sym, tok)
        harcanan += 0.01
        if err:
            print("\n--- %-6s HATA: %s" % (sym, err))
            continue
        y, agg = d
        px = p.get("anlik") or 0
        # anlik fiyati Binance'ten
        try:
            u = "https://fapi.binance.com/fapi/v1/ticker/price?symbol=%sUSDT" % sym
            px = float(json.load(urllib.request.urlopen(
                urllib.request.Request(u, headers={"User-Agent": "x"}), timeout=15))["price"])
        except Exception:
            px = p["giris"]

        ust = sorted([(y[i], agg[i]) for i in range(len(y)) if y[i] > px and agg[i] > 0],
                     key=lambda t: -t[1])[:5]
        alt = sorted([(y[i], agg[i]) for i in range(len(y)) if y[i] < px and agg[i] > 0],
                     key=lambda t: -t[1])[:5]
        ust.sort(key=lambda t: t[0])
        alt.sort(key=lambda t: -t[0])

        print("\n--- %-6s %dx · anlik %.6f · giris %.6f ---" % (sym, p["kaldirac"], px, p["giris"]))
        print("    seviye        buyukluk $        fiyattan    poz. isaretleri")
        for f, b in reversed(ust):
            print("    %10.6f  %14s  %+9.2f%%    %s" % (f, "{:,.0f}".format(b), (f / px - 1) * 100,
                                                        isaret(f, p, px)))
        print("    %10.6f  %14s  %+9.2f%%    << ANLIK FIYAT" % (px, "-", 0.0))
        for f, b in alt:
            print("    %10.6f  %14s  %+9.2f%%    %s" % (f, "{:,.0f}".format(b), (f / px - 1) * 100,
                                                        isaret(f, p, px)))
        cikti.append({"sym": sym, "anlik": px, "ust": ust, "alt": alt,
                      "stop": p["stop"], "hedef": p["tp2"],
                      "kilit_tetik": p.get("kilit_tetik")})
        time.sleep(1)

    print("\n" + "=" * 100)
    print("harcanan: ~%.2f USD (%d cagri)" % (harcanan, len(cikti)))
    if cikti:
        yol = os.path.join(BURA, "liqmap_%s.json" % dt.datetime.now().strftime("%Y%m%d_%H%M"))
        io.open(yol, "w", encoding="utf-8").write(json.dumps(cikti, ensure_ascii=False, indent=2))
        print("kaydedildi -> %s" % os.path.basename(yol))
    print("Bot dosyalarina yazim: YOK")


def isaret(f, p, px):
    """Bu seviye pozisyonun hangi esigine yakin?"""
    ims = []
    for ad, v in (("STOP", p["stop"]), ("TETIK", p.get("kilit_tetik")), ("HEDEF", p["tp2"])):
        if v and abs(f / v - 1) < 0.01:
            ims.append("~%s" % ad)
    if p["stop"] < f < px:
        ims.append("stop ile fiyat ARASINDA")
    elif f < p["stop"]:
        ims.append("stopun ALTINDA")
    return " · ".join(ims) if ims else ""


if __name__ == "__main__":
    main()
