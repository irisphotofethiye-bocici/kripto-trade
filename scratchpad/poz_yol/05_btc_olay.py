#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""YENI ORNEKLEM — BTC sert hareket ederken ALTLAR ne yapiyor?

KULLANICI: "btc veya eth sicrarken pozlarin datasini incele, hareketi orda
ariyoruz... cektigimiz veriyle YENI BIR ORNEKLEM yaratiyoruz."

19 Agustos TEK vakaydi. Burada ayni yapi 29 GUNUN TAMAMINA uygulanir:
her BTC sert hareketi bir OLAY, altlarin toplu davranisi olculur.

IKI AYRI SORU — karistirilmaz:
  ONCE  [t0-60dk, t0]  : altlar BTC'nin hareketini HABER VERIYOR mu? (ongoru)
  SONRA [t0, t0+60dk]  : altlar nasil TEPKI veriyor?                 (yapi)

OLAY (03_olay.py ile AYNI, on-kayittaki tanim): BTC'de 30 dk icinde >= 2,0 x ATR.
KONTROL: BTC'nin olay olmayan saatleri, olaydan >= 60 dk uzak.
KARISTIRICI: BTC'nin pencere-ICI kendi fiyat degisimi dilimlenir.

SALT OKUMA.
"""
import os, json, datetime, statistics as sx, random

HERE = os.path.dirname(os.path.abspath(__file__))
SERI = os.path.join(os.path.dirname(HERE), "perp_seri")
random.seed(23)
BAR, OLAY_BAR, ATR_N, KAT = 12, 6, 14, 2.0


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


def atr_pct(k, ts, i):
    if i < ATR_N:
        return None
    tr = []
    for j in range(i - ATR_N + 1, i + 1):
        o = k[ts[j - 1]]["c"]
        b = k[ts[j]]
        tr.append(max(b["h"] - b["l"], abs(b["h"] - o), abs(b["l"] - o)))
    c = k[ts[i]]["c"]
    return (sum(tr) / ATR_N) / c * 100 if c else None


def btc_olaylari():
    kl = yukle("BTC", "kline")
    ts = sorted(kl)
    olay, i = [], BAR
    while i < len(ts) - OLAY_BAR - 1:
        a = atr_pct(kl, ts, i)
        if not a:
            i += 1
            continue
        g = (kl[ts[i + OLAY_BAR]]["c"] - kl[ts[i]]["c"]) / kl[ts[i]]["c"] * 100
        if abs(g) >= KAT * a:
            olay.append((ts[i], g))
            i += BAR
        else:
            i += 1
    yasak = set()
    for t, _ in olay:
        yasak.update(range(ts.index(t) - BAR, ts.index(t) + BAR + 1))
    aday = [i for i in range(BAR, len(ts) - OLAY_BAR - 1) if i not in yasak]
    kontrol = [ts[i] for i in random.sample(aday, min(len(olay) * 2, len(aday)))]
    return olay, kontrol, kl, ts


def alt_kesit(syms, t_bit, ileri=False):
    """Bir ana ait ALTLARIN toplu olcumu. ileri=True -> [t, t+60dk]"""
    t0 = t_bit if ileri else t_bit - BAR * 300000
    t1 = t_bit + BAR * 300000 if ileri else t_bit
    dfi, hx, tap, doi = [], [], [], []
    for s in syms:
        kl = yukle(s, "kline")
        if t0 not in kl or t1 not in kl:
            continue
        a, b = kl[t0], kl[t1]
        if a["c"]:
            dfi.append((b["c"] - a["c"]) / a["c"] * 100)
        ic = [kl[t]["qv"] for t in range(t0, t1 + 1, 300000) if t in kl]
        onc = [kl[t]["qv"] for t in range(t0 - BAR * 300000, t0, 300000) if t in kl]
        if ic and onc and sum(onc) > 0:
            hx.append(sum(ic) / sum(onc))
        q = sum(kl[t]["qv"] for t in range(t0, t1 + 1, 300000) if t in kl)
        tq = sum(kl[t]["tqv"] for t in range(t0, t1 + 1, 300000) if t in kl)
        if q > 0:
            tap.append(tq / q)
        oi = yukle(s, "oi")
        if t0 in oi and t1 in oi:
            x, y = float(oi[t0]["sumOpenInterest"]), float(oi[t1]["sumOpenInterest"])
            if x:
                doi.append((y - x) / x * 100)
    if len(dfi) < 10:
        return None
    return {"alt_d_fiyat": sx.median(dfi), "alt_hacim_x": sx.median(hx) if hx else None,
            "alt_taker_pay": sx.median(tap) if tap else None,
            "alt_d_oi": sx.median(doi) if doi else None, "n": len(dfi)}


def tablo(ad, gruplar):
    print("\n%s" % ad)
    print("%-26s %5s %11s %11s %12s %10s" %
          ("grup", "N", "alt_d_fiyat", "alt_hacim_x", "alt_taker_pay", "alt_d_oi"))
    print("-" * 80)
    for g, v in gruplar:
        if not v:
            print("%-26s %5s" % (g, "-"))
            continue
        def m(a):
            x = [z[a] for z in v if z.get(a) is not None]
            return sx.median(x) if len(x) >= 3 else float("nan")
        print("%-26s %5d %+11.3f %11.3f %12.4f %+10.3f"
              % (g, len(v), m("alt_d_fiyat"), m("alt_hacim_x"), m("alt_taker_pay"), m("alt_d_oi")))


if __name__ == "__main__":
    syms = sorted({f.rsplit("_", 1)[0] for f in os.listdir(SERI)
                   if f.endswith("_kline.json")} - {"BTC", "ETH"})
    olay, kontrol, btckl, bts = btc_olaylari()
    yuk = [t for t, g in olay if g > 0]
    asg = [t for t, g in olay if g < 0]
    print("YENI ORNEKLEM — BTC olaylari · %d alt sembol" % len(syms))
    print("BTC 5dk seri: %d bar (%s -> %s)" %
          (len(bts), datetime.datetime.fromtimestamp(bts[0]/1000).strftime("%m-%d"),
           datetime.datetime.fromtimestamp(bts[-1]/1000).strftime("%m-%d")))
    print("olay: yukari %d · asagi %d · kontrol %d" % (len(yuk), len(asg), len(kontrol)))

    for ileri, baslik in ((False, "A) BTC HAREKETINDEN ONCEKI 60 DK — altlar haber veriyor mu?"),
                          (True,  "B) BTC HAREKETINDEN SONRAKI 60 DK — altlar nasil tepki veriyor?")):
        g = []
        for ad, lst in (("BTC YUKARI olayi", yuk), ("BTC ASAGI olayi", asg), ("KONTROL", kontrol)):
            v = [z for z in (alt_kesit(syms, t, ileri) for t in lst) if z]
            g.append((ad, v))
        tablo(baslik, g)

    # KARISTIRICI: BTC'nin KENDI pencere-ici hareketi sabitlenince
    print("\n--- KARISTIRICI: BTC'nin pencere-ICI (t-60,t) kendi degisimi sabitlenince ---")
    def btc_onceki(t):
        i = bts.index(t)
        a, b = btckl[bts[i - BAR]]["c"], btckl[t]["c"]
        return (b - a) / a * 100 if a else None
    bant = [(-99, -0.3, "BTC onceki < -0,3%"), (-0.3, 0.3, "-0,3..+0,3%"), (0.3, 99, "> +0,3%")]
    for lo, hi, et in bant:
        g = []
        for ad, lst in (("BTC YUKARI", yuk), ("BTC ASAGI", asg), ("KONTROL", kontrol)):
            v = []
            for t in lst:
                b = btc_onceki(t)
                if b is None or not (lo <= b < hi):
                    continue
                z = alt_kesit(syms, t, False)
                if z:
                    v.append(z)
            g.append((ad, v))
        tablo("   %s" % et, g)
    print("\nbot dosyalarina yazim: YOK")
