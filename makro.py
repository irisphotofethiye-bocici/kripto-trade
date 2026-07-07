#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAKRO — D3 deterministik cekirdek (2026-07-02, B-eksik #4 duzeltmesi).
Eskiden D3 tamamen web_search'e bagliydi (uydurma-riskli katman). Simdi:
  - DXY: stooq.com ucretsiz gunluk CSV (anahtarsiz) -> deger + 20g trend + SKILL esikleri (>105 risk-off, <100 risk-on)
  - FOMC/CPI: makro_takvim.json (sabit dosya, yilda 1 bakim) -> kalan gun + 48s VETO bayragi
  - ETF flow: farside.co.uk denenir; erisilemezse ACIKCA "web_search kullan" der (UYDURMAZ)
Kullanim: python makro.py
"""
import json, os, re, sys, datetime, urllib.request, statistics

HERE = os.path.dirname(os.path.abspath(__file__))

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")


def fetch(u, timeout=20):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (makro/1.0)"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def _sinyal(v):
    return "RISK-OFF (>105)" if v > 105 else ("RISK-ON (<100)" if v < 100 else "NOTR (100-105)")


def dxy():
    """DXY: Yahoo chart API birincil (DX-Y.NYB, ucretsiz JSON; dogrulandi 2026-07-02).
    Stooq eski birincildi ama JS proof-of-work korumasi ekledi (2026-07) -> yedek olarak durur."""
    try:
        d = json.loads(fetch("https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB?range=3mo&interval=1d"))
        res = d["chart"]["result"][0]
        closes = [c for c in res["indicators"]["quote"][0]["close"] if c is not None]
        if len(closes) >= 21:
            v, sma20 = closes[-1], statistics.mean(closes[-20:])
            tarih = datetime.datetime.fromtimestamp(res["timestamp"][-1]).strftime("%Y-%m-%d")
            return {"deger": round(v, 2), "sma20": round(sma20, 2),
                    "trend": "YUKARI" if v > sma20 else "ASAGI",
                    "sinyal": _sinyal(v), "kaynak": "yahoo:DX-Y.NYB", "tarih": tarih}
    except Exception:
        pass
    for sym in ("dx.f", "usd_i", "^dxy"):  # yedek: stooq (PoW yuzunden muhtemelen calismaz)
        try:
            rows = [r.split(",") for r in fetch(f"https://stooq.com/q/d/l/?s={sym}&i=d").strip().splitlines()[1:]]
            closes = [float(r[4]) for r in rows if len(r) >= 5 and r[4] not in ("", "N/D")]
            if len(closes) < 21:
                continue
            v, sma20 = closes[-1], statistics.mean(closes[-20:])
            return {"deger": round(v, 2), "sma20": round(sma20, 2),
                    "trend": "YUKARI" if v > sma20 else "ASAGI",
                    "sinyal": _sinyal(v), "kaynak": f"stooq:{sym}", "tarih": rows[-1][0]}
        except Exception:
            continue
    return {"hata": "DXY kaynagi erisilemedi -> web_search('DXY today')"}


def takvim():
    try:
        t = json.load(open(os.path.join(HERE, "makro_takvim.json"), encoding="utf-8"))
    except Exception:
        return {"hata": "makro_takvim.json yok/bozuk"}
    bugun = datetime.date.today()
    out = {}
    for ad in ("fomc", "cpi"):
        gelecek = [d for d in t.get(ad, []) if datetime.date.fromisoformat(d) >= bugun]
        if gelecek:
            kalan = (datetime.date.fromisoformat(gelecek[0]) - bugun).days
            out[ad] = {"sonraki": gelecek[0], "kalan_gun": kalan}
        else:
            out[ad] = {"sonraki": None, "uyari": "takvim tukendi -> makro_takvim.json guncelle"}
    fk = out.get("fomc", {}).get("kalan_gun")
    out["veto_fomc_48s"] = bool(fk is not None and fk <= 2)   # SKILL vetosu: FOMC 48s -> pozisyon %50 kucult
    ck = out.get("cpi", {}).get("kalan_gun")
    out["cpi_bu_hafta"] = bool(ck is not None and ck <= 7)
    return out


def etf():
    """Farside BTC ETF flow tablosu (kirilgan; Cloudflare engellerse DURUST sekilde web_search'e yonlendir)."""
    try:
        html = fetch("https://farside.co.uk/btc/")
        m = re.findall(r"Total[^<]*</t[dh]>\s*(?:<[^>]+>\s*)*([\-−\(\)0-9,\.]+)", html)
        if m:
            return {"toplam_son": m[-1], "kaynak": "farside.co.uk", "uyari": "parse kirilgan; supheliyse siteden teyit"}
        return {"hata": "tablo parse edilemedi -> web_search('bitcoin ETF flows this week')"}
    except Exception as e:
        return {"hata": f"farside erisilemedi ({str(e)[:60]}) -> web_search('bitcoin ETF flows this week')"}


def main():
    d, t, e = dxy(), takvim(), etf()
    riskler = []
    if d.get("sinyal", "").startswith("RISK-OFF"):
        riskler.append("DXY>105")
    if t.get("veto_fomc_48s"):
        riskler.append("FOMC<=48s (VETO: pozisyon %50 kucult)")
    if t.get("cpi_bu_hafta"):
        riskler.append("CPI bu hafta")
    out = {"dxy": d, "takvim": t, "etf_btc": e,
           "d3_bayraklar": riskler or ["deterministik risk bayragi yok"],
           "not": "D3 cekirdegi: DXY+takvim deterministik; ETF/jeopolitik/Fed-soylem icin web_search tamamlar. Veri yoksa UYDURMA."}
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
