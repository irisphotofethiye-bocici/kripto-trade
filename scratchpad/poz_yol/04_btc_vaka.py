#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VAKA — 19 Agustos BTC/ETH sicramasi: ALTLARDA ONCEDEN iz var miydi?

KULLANICI (2026-08-21): "btc 19'unda 15:00'te yukselmeye basladi, yukselis
hareketinden 1 saat onceki pozlari ve kayitlari kontrol et; btc/eth sicrarken
poz datasini incele, hareketi orda ariyoruz. Gecmise bakiyoruz ama cektigimiz
veriyle YENI BIR ORNEKLEM yaratiyoruz."

OLCULEN OLAY YAPISI (15 dk mumdan, dogrulandi):
   15:30  BTC %+0,71  hacim 21,7 -> 538,1 M$  (25 KAT)   <- IZ: hacim patliyor, fiyat az
   17:45  BTC %+0,71 ... 18:15 %+2,52          <- KIRILMA, 2,25 saat SONRA
Yani 15:30 "haber", 17:45 "olay". Aradaki 2,25 saat karar penceresidir.

SORU: 14:30-15:30 (haberden ONCE) ve 16:45-17:45 (olaydan ONCE) pencerelerinde
      ALTLARIN OI/taker/hacim verisi, o gunun SIRADAN saatlerinden ayrilyor mu?

KONTROL: ayni sembollerin AYNI GUN diger saatleri (gun-ici kontrol -> sembol,
   rejim ve gunun kendisi sabit). CLAUDE.md: karistirici kontrolu zorunlu.

SALT OKUMA.
"""
import os, json, datetime, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
SERI = os.path.join(os.path.dirname(HERE), "perp_seri")
BAR = 12          # 60 dk = 12 x 5dk


def yukle(sym, uc):
    y = os.path.join(SERI, "%s_%s.json" % (sym, uc))
    if not os.path.exists(y):
        return {}
    try:
        d = json.load(open(y, encoding="utf-8"))
    except Exception:
        return {}
    z = "t" if uc == "kline" else "timestamp"
    return {int(x[z]): x for x in d}


def ms(dt):
    return int(dt.timestamp() * 1000)


def pencere_olc(sym, bit_dt):
    """[bit-60dk, bit] penceresinin olcumleri. -> dict | None"""
    kl = yukle(sym, "kline")
    if len(kl) < 50:
        return None
    t1 = ms(bit_dt)
    t0 = t1 - BAR * 300000
    if t0 not in kl or t1 not in kl:
        return None
    oi, tak = yukle(sym, "oi"), yukle(sym, "taker")
    o = {}
    a, b = kl[t0], kl[t1]
    o["d_fiyat"] = (b["c"] - a["c"]) / a["c"] * 100 if a["c"] else None
    # pencere hacmi / onceki 12 barin hacmi  -> hacim GENISLEMESI
    ic = [kl[t].get("qv", 0) for t in range(t0, t1 + 1, 300000) if t in kl]
    onc = [kl[t].get("qv", 0) for t in range(t0 - BAR * 300000, t0, 300000) if t in kl]
    if ic and onc and sum(onc) > 0:
        o["hacim_x"] = sum(ic) / sum(onc)
    # pencere ICI taker alis orani (tqv / qv) — kline'dan, kesintisiz
    tq = sum(kl[t].get("tqv", 0) for t in range(t0, t1 + 1, 300000) if t in kl)
    qv = sum(kl[t].get("qv", 0) for t in range(t0, t1 + 1, 300000) if t in kl)
    if qv > 0:
        o["taker_alis_pay"] = tq / qv
    if t0 in oi and t1 in oi:
        a2, b2 = float(oi[t0]["sumOpenInterest"]), float(oi[t1]["sumOpenInterest"])
        if a2:
            o["d_oi"] = (b2 - a2) / a2 * 100
    if t1 in tak:
        o["taker_orani"] = float(tak[t1]["buySellRatio"])
    return o


def ozet(ad, kayitlar, alanlar):
    print("\n%s   N=%d sembol" % (ad, len(kayitlar)))
    print("%-16s %10s %10s" % ("degisken", "medyan", "ortalama"))
    print("-" * 40)
    for a in alanlar:
        v = [k[a] for k in kayitlar if k.get(a) is not None]
        if len(v) < 5:
            print("%-16s %10s %10s" % (a, "-", "N az"))
            continue
        print("%-16s %+10.3f %+10.3f" % (a, sx.median(v), sx.mean(v)))


ALAN = ["d_fiyat", "hacim_x", "taker_alis_pay", "d_oi", "taker_orani"]

if __name__ == "__main__":
    syms = sorted({f.rsplit("_", 1)[0] for f in os.listdir(SERI) if f.endswith("_kline.json")})
    print("VAKA — 19 Agustos BTC sicramasi · %d sembol" % len(syms))

    G = datetime.date(2026, 8, 19)
    olaylar = [
        ("A) 14:30-15:30  IZ'den ONCE  (hacim patlamasindan once)", datetime.datetime(2026, 8, 19, 15, 30)),
        ("B) 15:30-16:30  IZ penceresi (hacim 25x, fiyat +0,71)",   datetime.datetime(2026, 8, 19, 16, 30)),
        ("C) 16:45-17:45  KIRILMA'dan ONCE",                        datetime.datetime(2026, 8, 19, 17, 45)),
        ("D) 17:45-18:45  KIRILMA penceresi",                       datetime.datetime(2026, 8, 19, 18, 45)),
    ]
    for ad, bit in olaylar:
        k = [z for z in (pencere_olc(s, bit) for s in syms) if z]
        ozet(ad, k, ALAN)

    # KONTROL: ayni gun, olaylardan uzak saatler
    print("\n" + "=" * 56)
    kontrol = []
    for saat in (2, 4, 6, 8, 10, 12, 22):
        bit = datetime.datetime(2026, 8, 19, saat, 0)
        kontrol += [z for z in (pencere_olc(s, bit) for s in syms) if z]
    ozet("KONTROL — ayni gun, olaydan uzak 7 saat", kontrol, ALAN)
    print("\nbot dosyalarina yazim: YOK")
