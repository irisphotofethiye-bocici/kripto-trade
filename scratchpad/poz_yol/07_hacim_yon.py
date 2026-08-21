#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BTC/ETH SERT HAREKETTEN ONCE HACIM — YUKARI ile ASAGI FARKLI MI?

KULLANICI (2026-08-21): "yani daha once btc yukari hareket ettiginde hacim
artmasi veya dusmesi oncu sinyal olmamis mi diyorsun"

06_major_iz.py BUNU OLCMEDI. O, "hacim patlar VE fiyat kimildamazsa" dar
tanimini sinadi. Burada dogrudan soru soruluyor:

   sert YUKARI hareketten onceki 60 dk'da hacim ne yapiyor?
   sert ASAGI  hareketten onceki 60 dk'da hacim ne yapiyor?
   ikisi BIRBIRINDEN ayrilyor mu?   <- yon bilgisi ancak buradan cikar

Ayrilmiyorsa hacim yalnizca "bir hareket geliyor" der, YONU soylemez.

Veri: major_5dk/{BTC,ETH}.json — 5 dk, 2 yil, 210.241 bar.
SALT OKUMA.
"""
import os, json, datetime, random, statistics as sx, collections

HERE = os.path.dirname(os.path.abspath(__file__))
VERI = os.path.join(os.path.dirname(HERE), "major_5dk")
random.seed(41)
ATR_N, OLAY_BAR, KAT, ONCE, AYIRMA = 14, 6, 2.0, 12, 12
PERM = 1500   # kesif kosusu: medyan farkina bakiyoruz, min p 0,00067


def yukle(s):
    with open(os.path.join(VERI, "%s.json" % s), encoding="utf-8") as f:
        return json.load(f)


def atr_serisi(b):
    out, tr = [None] * len(b), []
    for i in range(1, len(b)):
        tr.append(max(b[i]["h"] - b[i]["l"], abs(b[i]["h"] - b[i - 1]["c"]),
                      abs(b[i]["l"] - b[i - 1]["c"])))
        if len(tr) >= ATR_N and b[i]["c"]:
            out[i] = (sum(tr[-ATR_N:]) / ATR_N) / b[i]["c"] * 100
    return out


def once_olc(b, i):
    """[i-60dk, i] penceresi — HAREKET DISARIDA (hareket i'den SONRA)."""
    j = i - ONCE
    if j < ONCE + 1 or not b[j]["c"]:
        return None
    qv = sum(b[k]["qv"] for k in range(j + 1, i + 1))
    taban = sum(b[k]["qv"] for k in range(j - ONCE + 1, j + 1))
    tqv = sum(b[k]["tqv"] for k in range(j + 1, i + 1))
    o = {"hacim_x": qv / taban if taban > 0 else None,
         "d_fiyat": (b[i]["c"] - b[j]["c"]) / b[j]["c"] * 100,
         "taker_pay": tqv / qv if qv > 0 else None,
         "islem_x": (sum(b[k]["n"] for k in range(j + 1, i + 1)) /
                     max(1, sum(b[k]["n"] for k in range(j - ONCE + 1, j + 1)))),
         "ay": datetime.datetime.fromtimestamp(b[i]["t"] / 1000).strftime("%Y-%m")}
    # ortalama islem BUYUKLUGU degisimi: buyuk oyuncu izi
    n1 = sum(b[k]["n"] for k in range(j + 1, i + 1))
    n0 = sum(b[k]["n"] for k in range(j - ONCE + 1, j + 1))
    if n1 and n0 and taban > 0:
        o["islem_boyu_x"] = (qv / n1) / (taban / n0)
    return o


def topla(sym):
    b = yukle(sym)
    atr = atr_serisi(b)
    yuk, asg, olay_i = [], [], []
    i = 2 * ONCE + 1
    while i < len(b) - OLAY_BAR - 1:
        if atr[i] and atr[i] > 0 and b[i]["c"]:
            g = (b[i + OLAY_BAR]["c"] - b[i]["c"]) / b[i]["c"] * 100
            if abs(g) >= KAT * atr[i]:
                o = once_olc(b, i)
                if o:
                    o["olay_get"] = g
                    (yuk if g > 0 else asg).append(o)
                    olay_i.append(i)
                i += AYIRMA
                continue
        i += 1
    yasak = set()
    for j in olay_i:
        yasak.update(range(j - AYIRMA, j + AYIRMA + 1))
    aday = [k for k in range(2 * ONCE + 1, len(b) - OLAY_BAR - 1) if k not in yasak]
    kont = []
    for k in random.sample(aday, min(2 * (len(yuk) + len(asg)), len(aday))):
        o = once_olc(b, k)
        if o:
            kont.append(o)
    return yuk, asg, kont


def perm_p(a, bb):
    h = list(a) + list(bb)
    n = len(a)
    g = sx.median(a) - sx.median(bb)
    u = 0
    for _ in range(PERM):
        random.shuffle(h)
        if abs(sx.median(h[:n]) - sx.median(h[n:])) >= abs(g):
            u += 1
    return g, (u + 1) / (PERM + 1)


ALAN = ["hacim_x", "islem_x", "islem_boyu_x", "taker_pay", "d_fiyat"]


def rapor(sym, yuk, asg, kont):
    print("\n" + "=" * 88)
    print("%s   sert YUKARI %d · sert ASAGI %d · kontrol %d" % (sym, len(yuk), len(asg), len(kont)))
    print("hareketten ONCEKI 60 dk (hareket pencerenin DISINDA)")
    print("=" * 88)
    print("%-14s %10s %10s %10s %12s %11s" %
          ("degisken", "YUKARI", "ASAGI", "KONTROL", "YUK-ASG", "p(yuk/asg)"))
    print("-" * 74)
    for a in ALAN:
        y = [z[a] for z in yuk if z.get(a) is not None]
        s = [z[a] for z in asg if z.get(a) is not None]
        k = [z[a] for z in kont if z.get(a) is not None]
        if min(len(y), len(s), len(k)) < 30:
            continue
        g, p = perm_p(list(y), list(s))
        print("%-14s %10.4f %10.4f %10.4f %+12.4f %11.5f"
              % (a, sx.median(y), sx.median(s), sx.median(k), g, p))
    # olay VAR MI (yon degil) — hacim, hareketi haber veriyor mu
    print("\n  olay(yuk+asg) vs kontrol — 'bir hareket geliyor' bilgisi:")
    for a in ("hacim_x", "islem_x", "islem_boyu_x"):
        o = [z[a] for z in yuk + asg if z.get(a) is not None]
        k = [z[a] for z in kont if z.get(a) is not None]
        if min(len(o), len(k)) < 30:
            continue
        g, p = perm_p(list(o), list(k))
        ai, ak = collections.defaultdict(list), collections.defaultdict(list)
        for z in yuk + asg:
            if z.get(a) is not None:
                ai[z["ay"]].append(z[a])
        for z in kont:
            if z.get(a) is not None:
                ak[z["ay"]].append(z[a])
        ort = [m for m in ai if m in ak and len(ai[m]) >= 3 and len(ak[m]) >= 5]
        f = [sx.median(ai[m]) - sx.median(ak[m]) for m in ort]
        isr = 1 if (f and sx.median(f) > 0) else -1
        ay = sum(1 for x in f if x * isr > 0)
        print("    %-14s olay %.4f · kontrol %.4f · fark %+.4f · p %.5f · ay %d/%d"
              % (a, sx.median(o), sx.median(k), g, p, ay, len(ort)))


if __name__ == "__main__":
    print("SORU: sert hareketten ONCE hacim, YUKARI ile ASAGI'yi ayiriyor mu?")
    print("olay: 30 dk icinde >= %.1f x ATR · pencere [t-60dk, t]" % KAT)
    sonuc = {}
    for s in ("BTC", "ETH"):
        y, a, k = topla(s)
        sonuc[s] = (y, a, k)
        rapor(s, y, a, k)
    print("\n" + "=" * 88)
    print("YORUM KILAVUZU:")
    print("  YUK-ASG farki ~0 ve p buyuk  -> hacim YONU SOYLEMIYOR")
    print("  olay vs kontrol farki buyuk  -> hacim 'hareket geliyor' DIYOR")
    print("bot dosyalarina yazim: YOK")
