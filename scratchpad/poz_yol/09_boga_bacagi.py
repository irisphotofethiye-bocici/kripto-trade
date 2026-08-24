#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BUGUNKU GIBI HAREKET — ayni patern daha once de olmus mu, fonlama ne yapmis?

KULLANICI: "bugunku gibi hareket oldugunda olctun mu ayni patern, o sirada
funding ne durumdaymis, ya olctugumuz digerleri ve spot hareketi neymis —
SADECE BIZIM VERIDE olc."

DURUSTLUK — bizim veride NE VAR, NE YOK:
  VAR : major_5dk BTC/ETH (perp 5dk, 2 yil) · funding_gecmis (8s, 2024-08 -> 2026-08-11)
        perp_seri (74 alt, 5dk, 29 gun) · radar_archive (29 alan, 06-24 -> simdi)
  YOK : SPOT fiyat serisi. Diskteki her sey FAPI = PERP. klines_cache'te
        yalniz 25 sembol GUNLUK spot var, bu olcume yetmez.
        -> "spot hareketi" bu veriyle OLCULEMEZ. Basis/premium da olculemez.
  BOSLUK: funding_gecmis 2026-08-11'de BITIYOR -> 19-21 Agustos hareketinin
        fonlamasi orada YOK. Onun icin radar_archive kullanilir (o gunu kapsiyor).

OLAY TANIMI: BTC 24 saatte >= %4 yukselis (19-20 Agu: %+5,8). Cakismasin diye
  bir olaydan sonra 48 saat atlanir.

SALT OKUMA.
"""
import os, json, datetime, statistics as sx, bisect

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
PROJE = os.path.dirname(SCRATCH)
BAR24 = 288          # 24 saat / 5 dk
ESIK = 4.0


def yukle(yol):
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def fonlama(sym):
    p = os.path.join(SCRATCH, "funding_gecmis", "%s.json" % sym)
    if not os.path.exists(p):
        return [], []
    d = yukle(p)
    return [x["t"] for x in d], [x["r"] for x in d]      # YUZDE / 8 saat


def fon_deger(ts, rs, t):
    i = bisect.bisect_right(ts, t) - 1
    return rs[i] if 0 <= i < len(rs) else None


def fon_ort(ts, rs, t0, t1):
    i, j = bisect.bisect_right(ts, t0), bisect.bisect_right(ts, t1)
    v = rs[i:j]
    return sx.mean(v) if v else None


def btc_boga_bacaklari():
    b = yukle(os.path.join(SCRATCH, "major_5dk", "BTC.json"))
    olay, i = [], BAR24
    while i < len(b) - BAR24:
        g = (b[i]["c"] - b[i - BAR24]["c"]) / b[i - BAR24]["c"] * 100
        if g >= ESIK:
            olay.append((b[i]["t"], g, i))
            i += BAR24 * 2                    # 48 saat atla
        else:
            i += 12                           # saatlik tarama
    return b, olay


if __name__ == "__main__":
    print("=" * 88)
    print("BUGUNKU GIBI HAREKET — BTC 24 saatte >= %%%.0f yukselis" % ESIK)
    print("=" * 88)
    b, olay = btc_boga_bacaklari()
    print("2 yilda %d bagimsiz olay bulundu" % len(olay))
    ts, rs = fonlama("BTC")
    ets, ers = fonlama("ETH")

    print("\n1) OLAY LISTESI + FONLAMA (BTC, %%/8 saat)")
    print("%-18s %8s %11s %11s %11s %11s" %
          ("tarih", "24s %", "fon ONCE", "fon SIRADA", "fon SONRA", "ETH fon ONCE"))
    print("-" * 76)
    satir = []
    for t, g, i in olay:
        d = datetime.datetime.fromtimestamp(t / 1000)
        f_once = fon_ort(ts, rs, t - 86400000, t - 43200000)      # -24s..-12s
        f_sira = fon_ort(ts, rs, t - 43200000, t)                 # -12s..0
        f_sonr = fon_ort(ts, rs, t, t + 86400000)                 # 0..+24s
        e_once = fon_ort(ets, ers, t - 86400000, t - 43200000)
        satir.append((d, g, f_once, f_sira, f_sonr, e_once))
        if f_once is None:
            print("%-18s %8.2f %11s   <- fonlama verisi YOK (08-11 sonrasi)"
                  % (d.strftime("%Y-%m-%d %H:%M"), g, "-"))
            continue
        print("%-18s %8.2f %11.4f %11.4f %11s %11.4f"
              % (d.strftime("%Y-%m-%d %H:%M"), g, f_once, f_sira,
                 "%.4f" % f_sonr if f_sonr is not None else "-", e_once if e_once is not None else float("nan")))

    v = [(a, c, e, f) for _, a, c, e, f in
         [(x[0], x[1], x[2], x[4], x[5]) for x in satir] if c is not None]
    if v:
        print("\n2) OZET — fonlama olay etrafinda")
        oncelar = [x[1] for x in v]
        sonralar = [x[2] for x in v if x[2] is not None]
        print("   fon ONCE  (24-12s) medyan %+.4f  ·  ortalama %+.4f  ·  N=%d"
              % (sx.median(oncelar), sx.mean(oncelar), len(oncelar)))
        if sonralar:
            print("   fon SONRA (0-24s) medyan %+.4f  ·  ortalama %+.4f  ·  N=%d"
                  % (sx.median(sonralar), sx.mean(sonralar), len(sonralar)))
        poz = sum(1 for x in oncelar if x > 0.01)
        print("   ONCE fonlama > %%0,01 (long kalabalik) olan olay: %d/%d" % (poz, len(oncelar)))
        neg = sum(1 for x in oncelar if x < 0)
        print("   ONCE fonlama NEGATIF (short kalabalik)  olan olay: %d/%d" % (neg, len(oncelar)))

    # KONTROL: rastgele gunlerin fonlamasi
    import random
    random.seed(67)
    if ts:
        kont = []
        for _ in range(500):
            t = random.randint(ts[0] + 86400000, ts[-1] - 86400000)
            x = fon_ort(ts, rs, t - 86400000, t - 43200000)
            if x is not None:
                kont.append(x)
        print("\n3) KONTROL — rastgele 500 an, ayni pencere")
        print("   fonlama medyan %+.4f  ·  ortalama %+.4f" % (sx.median(kont), sx.mean(kont)))
        if v:
            print("   OLAY oncesi medyan %+.4f  ->  fark %+.4f"
                  % (sx.median(oncelar), sx.median(oncelar) - sx.median(kont)))
    print("\nSPOT: bizim veride YOK — olculemedi.")
    print("bot dosyalarina yazim: YOK")
