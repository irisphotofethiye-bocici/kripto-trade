#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""'30 GUNLUK SINIF' ARSIVDE 2+ YIL GERIYE VAR MI? — KANIT BETIGI (2026-09-05)

NEDEN: CLAUDE.md su an soyle diyor —
   "IKI SINIF VERI VAR: KALICI ve 30 GUNLUK. Ikinci sinif CEKILEMEZ, ancak
    ARSIVLENIR... o veri yalnizca o an kaydediyorsan vardir."
ve buna dayanarak 2026-08-24'te "58 sembolde OI/long-short/taker KALICI olarak
gitti" diye bir kayip kaydedildi.

Bu betik o hukmu sinar. Eger arsiv (data.binance.vision) ayni veriyi tasiyorsa:
   - kural YANLIS
   - kaydedilen kayip GERI ALINABILIR
   - 30-60 gunle sinirli tum perp_seri olcumleri 2 YILA genisletilebilir

YONTEM — belirleyici sinama:
   Ayni gun icin (a) arsiv metrics dosyasi (b) canli uc period=5m indirilir,
   damga kaymasi -10..+10 dk taranir ve BAGIL hata raporlanir.
   Bir kaymada bagil hata ~0 ise iki kaynak AYNI VERIDIR.

Salt-okunur. Ucretli cagri YOK. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import urllib.request, urllib.error, zipfile, io, json, datetime, statistics as stx

ARSIV = "https://data.binance.vision/"
FAPI = "https://fapi.binance.com/futures/data/"
BICIM = "%Y-%m-%d %H:%M:%S"

ALANLAR = (
    ("openInterestHist", "sumOpenInterest", "sum_open_interest"),
    ("topLongShortAccountRatio", "longShortRatio", "count_toptrader_long_short_ratio"),
    ("topLongShortPositionRatio", "longShortRatio", "sum_toptrader_long_short_ratio"),
    ("globalLongShortAccountRatio", "longShortRatio", "count_long_short_ratio"),
    ("takerlongshortRatio", "buySellRatio", "sum_taker_long_short_vol_ratio"),
)


def arsiv_metrics(sym, gun):
    y = "data/futures/um/daily/metrics/%s/%s-metrics-%s.zip" % (sym, sym, gun)
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(ARSIV + y, timeout=60).read()))
    sat = z.read(z.namelist()[0]).decode("utf-8", "replace").splitlines()
    bas = sat[0].split(",")
    out = {}
    for l in sat[1:]:
        p = l.split(",")
        if len(p) == len(bas):
            out[p[0]] = dict(zip(bas, p))
    return out


def canli(ep, alan, sym):
    u = "%s%s?symbol=%s&period=5m&limit=500" % (FAPI, ep, sym)
    d = json.loads(urllib.request.urlopen(u, timeout=25).read())
    return dict((int(x["timestamp"]), float(x[alan])) for x in d)


def ms(t):
    return int(datetime.datetime.strptime(t, BICIM).replace(tzinfo=datetime.UTC).timestamp() * 1000)


def var_mi(y):
    try:
        r = urllib.request.urlopen(urllib.request.Request(ARSIV + y, method="HEAD"), timeout=20)
        return int(r.headers.get("Content-Length") or 0)
    except Exception:
        return None


def main():
    print("=" * 92)
    print("'30 GUNLUK SINIF' ARSIVDE 2+ YIL GERIYE VAR MI?")
    print("=" * 92)
    print("CLAUDE.md su an: 'ikinci sinif CEKILEMEZ, ancak ARSIVLENIR'")
    print("Bu betik o hukmu sinar.")
    print()

    sym = "SOLUSDT"
    # canli 5m uc ~1,7 gun geriye gider -> ORTUSEN gun secilmeli
    dun = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    print("### 1) BELIRLEYICI SINAMA — arsiv(%s) vs canli uc, damga kaymasi taranir" % dun)
    try:
        ars = arsiv_metrics(sym, dun)
    except Exception as e:
        print("   arsiv okunamadi: %s" % str(e)[:70])
        return
    print("   arsiv kayit: %d  ·  adim: 5 dk" % len(ars))
    print()
    print("   %-34s %s" % ("alan", "kayma(dk):bagil_hata"))
    tam = 0
    for ep, alan, sut in ALANLAR:
        try:
            c = canli(ep, alan, sym)
        except Exception as e:
            print("   %-34s canli HATA %s" % (sut, str(e)[:30]))
            continue
        satir, en_iyi = [], None
        for kay in (-10, -5, 0, 5, 10):
            f, ref = [], []
            for t, d in ars.items():
                v = d.get(sut)
                if not v:
                    continue
                k = ms(t) + kay * 60000
                if k in c:
                    f.append(abs(c[k] - float(v)))
                    ref.append(abs(c[k]))
            if len(f) > 50:
                bg = max(f) / max(1e-9, stx.mean(ref))
                satir.append("%+d:%.0e" % (kay, bg))
                if en_iyi is None or bg < en_iyi:
                    en_iyi = bg
        if en_iyi is not None and en_iyi < 1e-3:
            tam += 1
        print("   %-34s %s" % (sut, "  ".join(satir)))
    print()
    print("   -> %d/%d alanda bir kaymada BAGIL HATA < 1e-3  =>  %s"
          % (tam, len(ALANLAR),
             "AYNI VERI" if tam >= 4 else "farkli/dogrulanamadi"))
    print()

    print("### 2) GERIYE NE KADAR GIDIYOR?")
    bugun = datetime.datetime.now(datetime.UTC)
    for geri in (30, 180, 365, 730, 1100):
        g = (bugun - datetime.timedelta(days=geri)).strftime("%Y-%m-%d")
        b = var_mi("data/futures/um/daily/metrics/%s/%s-metrics-%s.zip" % (sym, sym, g))
        print("   metrics   %s (%4d gun once): %s" % (g, geri, "VAR" if b else "yok"))
    for geri in (30, 365, 900):
        g = (bugun - datetime.timedelta(days=geri)).strftime("%Y-%m-%d")
        b = var_mi("data/futures/um/daily/bookDepth/%s/%s-bookDepth-%s.zip" % (sym, sym, g))
        print("   bookDepth %s (%4d gun once): %s" % (g, geri, "VAR" if b else "yok"))
    print()

    print("### 3) KAYDEDILEN KAYIP GERI ALINABILIR MI?")
    print("   CLAUDE.md: '58 sembolde 07-23..07-26 arasi OI/long-short/taker")
    print("              KALICI olarak gitti'")
    eksik = 0
    for g in ("2026-07-23", "2026-07-24", "2026-07-25", "2026-07-26"):
        b = var_mi("data/futures/um/daily/metrics/%s/%s-metrics-%s.zip" % (sym, sym, g))
        print("   %s : %s" % (g, "ARSIVDE VAR" if b else "yok"))
        if not b:
            eksik += 1
    print()
    print("   -> %s" % ("🔑 KAYIP GERI ALINABILIR — kural duzeltilmeli"
                        if eksik == 0 else "kismen"))
    print()
    print("Ucretli cagri: YOK · Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
