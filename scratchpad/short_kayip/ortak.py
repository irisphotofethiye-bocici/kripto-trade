#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ORTAK YARDIMCILAR — fiyat onbellegi + fonlama gecmisi + kucuk hesaplar.

SALT OKUMA (bot dosyalari). Yalniz scratchpad/short_kayip/ altina yazar.
"""
import json, os, sys, datetime, bisect, statistics as stx

HERE = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJE)
sys.path.insert(0, os.path.join(PROJE, "scratchpad"))
import evren                                    # noqa: E402

MUM_DIR = os.path.join(HERE, "mum5")
FON_DIR = os.path.join(HERE, "fonlama")
for d in (MUM_DIR, FON_DIR):
    os.makedirs(d, exist_ok=True)

# maliyet: gidis-donus taker + slipaj (olcum_ortak ile ayni ruh)
_c = json.load(open(os.path.join(PROJE, "kripto-config.json"), encoding="utf-8"))
_m = _c.get("maliyet", {})
MALIYET_PCT = 2 * (_m.get("taker_fee_pct", 0.045) + _m.get("slippage_pct", 0.02))


def _ms(dt):
    return int(dt.timestamp() * 1000)


# ONBELLEK SABIT PENCERE: her sembol icin TUM analiz penceresi bir kez cekilir
# ve bir daha daraltilmaz. (Onceki hali istenen araligi yaziyordu; her pozisyon
# farkli aralik isteyince onbellek surekli yeniden cekiliyor, rate-limit'e
# takilip BOS donuyordu. Sicrama sonrasi 12 pozisyon bu yuzden olculemedi.)
PENCERE_BAS = datetime.datetime(2026, 8, 10, 0, 0)


def mumlar(sym, bas_dt=None, bit_dt=None):
    """5 dakikalik mumlar (onbellekli, SABIT pencere). -> [{t,o,h,l,c}] · yoksa []"""
    yol = os.path.join(MUM_DIR, sym + ".json")
    if os.path.exists(yol):
        try:
            with open(yol, encoding="utf-8") as f:
                b = json.load(f)
            if b:
                return b
        except Exception:
            pass
    out, t0 = [], _ms(PENCERE_BAS)
    son = _ms(datetime.datetime.now())
    while t0 < son:
        try:
            d = evren.get("https://fapi.binance.com/fapi/v1/klines?symbol=%sUSDT"
                          "&interval=5m&startTime=%d&limit=1500" % (sym, t0), timeout=25)
        except Exception:
            break
        if not d:
            break
        out += [{"t": int(k[0]), "o": float(k[1]), "h": float(k[2]),
                 "l": float(k[3]), "c": float(k[4])} for k in d]
        yeni = int(d[-1][0]) + 300000
        if yeni <= t0:
            break
        t0 = yeni
        if len(d) < 1500:
            break
    if out:
        with open(yol, "w", encoding="utf-8") as f:
            json.dump(out, f)
    return out


def fonlama(sym):
    """Fonlama oran gecmisi (onbellekli). -> [{t, r}]"""
    yol = os.path.join(FON_DIR, sym + ".json")
    if os.path.exists(yol):
        try:
            with open(yol, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    try:
        d = evren.get("https://fapi.binance.com/fapi/v1/fundingRate?symbol=%sUSDT&limit=200"
                      % sym, timeout=25)
        out = [{"t": int(x["fundingTime"]), "r": float(x["fundingRate"])} for x in d]
    except Exception:
        out = []
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(out, f)
    return out


def fonlama_pct(fr, t0, t1, yon):
    """[t0,t1] arasindaki fonlama oranlarinin toplami, YUZDE, pozisyon lehine isaretli.
    SHORT: oran pozitifse short TAHSIL eder (+).  LONG: oran pozitifse LONG ODER (-)."""
    if not fr:
        return 0.0
    ts = [x["t"] for x in fr]
    i = bisect.bisect_right(ts, t0)
    j = bisect.bisect_right(ts, t1)
    s = sum(fr[k]["r"] for k in range(i, j)) * 100
    return s if yon == "SHORT" else -s


def dt(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def poz_yukle(taban="muhasebe_11agu"):
    with open(os.path.join(HERE, "pozisyonlar.json"), encoding="utf-8") as f:
        return json.load(f)[taban]


def ozet(v):
    """-> dict: n, toplam, ort, medyan, kazanan, kazanma_pct"""
    if not v:
        return None
    kz = sum(1 for x in v if x > 0)
    return {"n": len(v), "toplam": sum(v), "ort": stx.mean(v),
            "medyan": stx.median(v), "kazanan": kz, "kazanma_pct": 100 * kz / len(v)}
