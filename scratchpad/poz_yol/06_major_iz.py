#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MAJOR IZ — "hacim patliyor, fiyat kimildamiyor" sonraki hareketi soyluyor mu?

⚠️ ON_KAYIT_major_iz.md'ye BIREBIR uyar. Esikler orada sabitlendi, DEGISTIRILMEZ.

H1 (oynaklik): iz -> sonraki MUTLAK hareket buyur mu?
H2 (yon)     : izin ICINDEKI taker alis payi, hareketin YONUNU soyler mi?

On-kayitta yazili beklenti: H1 gecer (neredeyse totolojik), H2 GECMEZ.
Degerli olan H1'dir: "bir hareket geliyor" bilgisi + rejim = hangi tarafta
DURMAMAK gerektigi.

SALT OKUMA.
"""
import os, json, datetime, random, statistics as sx, collections

HERE = os.path.dirname(os.path.abspath(__file__))
VERI = os.path.join(os.path.dirname(HERE), "major_5dk")
random.seed(31)

# --- ON-KAYIT ESIKLERI — DOKUNULMAZ ---
PENCERE = 3          # 15 dk
GERI = 24            # 2 saatlik taban
HACIM_KAT = 5.0
FIYAT_KAT = 0.5      # |getiri| <= 0,5 x ATR
ATR_N = 14
AYIRMA = 12          # 60 dk
UFUK = [12, 24, 48]  # +1s, +2s, +4s
PERM = 20000
P_ESIK = 0.01 / 12   # 12 karsilastirma


def yukle(sym):
    y = os.path.join(VERI, "%s.json" % sym)
    if not os.path.exists(y):
        return []
    with open(y, encoding="utf-8") as f:
        return json.load(f)


def atr_serisi(b):
    out = [None] * len(b)
    tr = []
    for i in range(1, len(b)):
        tr.append(max(b[i]["h"] - b[i]["l"], abs(b[i]["h"] - b[i - 1]["c"]),
                      abs(b[i]["l"] - b[i - 1]["c"])))
        if len(tr) >= ATR_N and b[i]["c"]:
            out[i] = (sum(tr[-ATR_N:]) / ATR_N) / b[i]["c"] * 100
    return out


def olcum(b, atr, i):
    """i = pencerenin SON bari. -> dict | None"""
    if i < GERI + PENCERE or atr[i] is None or atr[i] <= 0:
        return None
    j = i - PENCERE + 1
    qv = sum(b[k]["qv"] for k in range(j, i + 1))
    taban = sum(b[k]["qv"] for k in range(i - PENCERE - GERI + 1, j)) / GERI * PENCERE
    if taban <= 0 or not b[j - 1]["c"]:
        return None
    tqv = sum(b[k]["tqv"] for k in range(j, i + 1))
    d = datetime.datetime.fromtimestamp(b[i]["t"] / 1000)
    return {"i": i, "t": b[i]["t"], "hacim_x": qv / taban,
            "get": (b[i]["c"] - b[j - 1]["c"]) / b[j - 1]["c"] * 100,
            "atr": atr[i], "taker_pay": tqv / qv if qv > 0 else None,
            "saat": d.hour, "ay": d.strftime("%Y-%m")}


def ileri(b, i, n):
    if i + n >= len(b) or not b[i]["c"]:
        return None
    return (b[i + n]["c"] - b[i]["c"]) / b[i]["c"] * 100


def topla(sym):
    b = yukle(sym)
    if len(b) < 1000:
        return None
    atr = atr_serisi(b)
    iz, hepsi = [], []
    i = GERI + PENCERE
    while i < len(b) - max(UFUK) - 1:
        o = olcum(b, atr, i)
        if o:
            for n in UFUK:
                o["f%d" % n] = ileri(b, i, n)
            hepsi.append(o)
            if o["hacim_x"] >= HACIM_KAT and abs(o["get"]) <= FIYAT_KAT * o["atr"]:
                iz.append(o)
                i += AYIRMA
                continue
        i += 1
    yasak = set()
    for z in iz:
        yasak.update(range(z["i"] - AYIRMA, z["i"] + AYIRMA + 1))
    aday = [o for o in hepsi if o["i"] not in yasak]
    kontrol = random.sample(aday, min(len(iz) * 2, len(aday))) if (aday and iz) else []
    return {"sym": sym, "iz": iz, "kontrol": kontrol, "hepsi": hepsi, "bar": len(b)}


def perm_p(a, bb):
    h = list(a) + list(bb)
    n = len(a)
    g = sx.median(a) - sx.median(bb)
    ust = 0
    for _ in range(PERM):
        random.shuffle(h)
        if abs(sx.median(h[:n]) - sx.median(h[n:])) >= abs(g):
            ust += 1
    return g, (ust + 1) / (PERM + 1)


def ay_tutarlilik(iz, kont, alan, fn):
    ai, ak = collections.defaultdict(list), collections.defaultdict(list)
    for z in iz:
        if z.get(alan) is not None:
            ai[z["ay"]].append(fn(z[alan]))
    for z in kont:
        if z.get(alan) is not None:
            ak[z["ay"]].append(fn(z[alan]))
    ortak = [a for a in ai if a in ak and len(ai[a]) >= 3 and len(ak[a]) >= 5]
    if not ortak:
        return 0, 0
    farklar = [sx.median(ai[a]) - sx.median(ak[a]) for a in ortak]
    isaret = 1 if sx.median(farklar) > 0 else -1
    return sum(1 for f in farklar if f * isaret > 0), len(ortak)


def yarim_kontrol(iz, kont, alan, fn):
    """Iki zaman yarisinda ayni isaret mi? -> (yariA, yariB)"""
    aylar = sorted({z["ay"] for z in iz})
    if len(aylar) < 4:
        return None, None
    orta = aylar[len(aylar) // 2]
    out = []
    for f in (lambda a: a <= orta, lambda a: a > orta):
        a = [fn(z[alan]) for z in iz if f(z["ay"]) and z.get(alan) is not None]
        b = [fn(z[alan]) for z in kont if f(z["ay"]) and z.get(alan) is not None]
        out.append(sx.median(a) - sx.median(b) if len(a) >= 10 and len(b) >= 10 else None)
    return out[0], out[1]


def h1(d):
    print("\n" + "=" * 96)
    print("H1 — OYNAKLIK: iz sonrasi MUTLAK hareket buyuyor mu?   [%s]" % d["sym"])
    print("iz=%d · kontrol=%d · toplam pencere=%d" % (len(d["iz"]), len(d["kontrol"]), len(d["hepsi"])))
    print("=" * 96)
    if len(d["iz"]) < 30:
        print("iz sayisi yetersiz.")
        return {}
    print("%-8s %10s %10s %8s %11s %10s %9s %9s"
          % ("ufuk", "IZ |get|", "KONTROL", "oran", "p", "ay tutar.", "yari-A", "yari-B"))
    print("-" * 82)
    out = {}
    for n in UFUK:
        a = [abs(z["f%d" % n]) for z in d["iz"] if z.get("f%d" % n) is not None]
        b = [abs(z["f%d" % n]) for z in d["kontrol"] if z.get("f%d" % n) is not None]
        if len(a) < 30 or len(b) < 30:
            continue
        g, p = perm_p(a, b)
        ay, top = ay_tutarlilik(d["iz"], d["kontrol"], "f%d" % n, abs)
        ya, yb = yarim_kontrol(d["iz"], d["kontrol"], "f%d" % n, abs)
        out[n] = g
        print("%-8s %10.4f %10.4f %7.2fx %11.5f %6d/%-3d %+9.4f %+9.4f"
              % ("+%dsa" % (n // 12), sx.median(a), sx.median(b),
                 sx.median(a) / sx.median(b) if sx.median(b) else 0, p, ay, top,
                 ya if ya is not None else float("nan"),
                 yb if yb is not None else float("nan")))
    return out


def h2(d):
    print("\n" + "=" * 96)
    print("H2 — YON: izin ICINDEKI taker alis payi yonu soyluyor mu?   [%s]" % d["sym"])
    print("=" * 96)
    iz = [z for z in d["iz"] if z.get("taker_pay") is not None]
    if len(iz) < 60:
        print("iz sayisi yetersiz.")
        return {}
    med = sx.median([z["taker_pay"] for z in iz])
    ust = [z for z in iz if z["taker_pay"] > med]
    alt = [z for z in iz if z["taker_pay"] <= med]
    print("taker alis payi medyani %.4f · ust %d · alt %d" % (med, len(ust), len(alt)))
    print("%-8s %12s %12s %10s %11s %10s" % ("ufuk", "ust taker", "alt taker", "fark", "p", "ay tutar."))
    print("-" * 70)
    out = {}
    for n in UFUK:
        a = [z["f%d" % n] for z in ust if z.get("f%d" % n) is not None]
        b = [z["f%d" % n] for z in alt if z.get("f%d" % n) is not None]
        if len(a) < 25 or len(b) < 25:
            continue
        g, p = perm_p(a, b)
        ay, top = ay_tutarlilik(ust, alt, "f%d" % n, lambda x: x)
        out[n] = g
        print("%-8s %+12.4f %+12.4f %+10.4f %11.5f %6d/%-3d"
              % ("+%dsa" % (n // 12), sx.median(a), sx.median(b), g, p, ay, top))
    return out


def karistirici(d):
    print("\n--- KARISTIRICI KONTROLLERI [%s] ---" % d["sym"])
    iz, kont = d["iz"], d["kontrol"]
    if len(iz) < 30:
        return
    print("\n1) 'iz' DUZ YUKSEK HACIMDEN daha mi iyi? (on-kayitta ozel olarak istendi)")
    hy = [o for o in d["hepsi"] if o["hacim_x"] >= HACIM_KAT]
    hareketli = [o for o in hy if abs(o["get"]) > FIYAT_KAT * o["atr"]]
    print("   hacim_x >= %.0f olan pencere : %d" % (HACIM_KAT, len(hy)))
    print("      fiyat KIMILDAMAYAN (iz)  : %d" % len(iz))
    print("      fiyat KIMILDAYAN         : %d" % len(hareketli))
    a = [abs(o["f24"]) for o in iz if o.get("f24") is not None]
    b = [abs(o["f24"]) for o in hareketli if o.get("f24") is not None]
    c = [abs(o["f24"]) for o in kont if o.get("f24") is not None]
    if a and b and c:
        print("   +2sa |getiri| medyan: iz %.4f · hacimli-HAREKETLI %.4f · kontrol %.4f"
              % (sx.median(a), sx.median(b), sx.median(c)))
        print("   -> iz, hareketli hacimden %s"
              % ("DAHA IYI" if sx.median(a) > sx.median(b) else "DAHA KOTU / AYNI"))
    print("\n2) saat yogunlasmasi (yerel saat)")
    si = collections.Counter(z["saat"] for z in iz)
    sk = collections.Counter(z["saat"] for z in kont)
    en = si.most_common(4)
    print("   iz en yogun    : %s" % ", ".join("%02d:00(%d)" % (h, c2) for h, c2 in en))
    print("   kontrol ayni sa: %s" % ", ".join("%02d:00(%d)" % (h, sk.get(h, 0)) for h, _ in en))
    print("\n3) ATR dilimi icinde de ayiriyor mu? (+2sa |getiri|)")
    tum = sorted(o["atr"] for o in kont)
    if len(tum) > 10:
        q = [tum[int(len(tum) * x)] for x in (0.33, 0.66)]
        for lo, hi, et in ((0, q[0], "dusuk ATR"), (q[0], q[1], "orta ATR"), (q[1], 9e9, "yuksek ATR")):
            a = [abs(o["f24"]) for o in iz if lo <= o["atr"] < hi and o.get("f24") is not None]
            b = [abs(o["f24"]) for o in kont if lo <= o["atr"] < hi and o.get("f24") is not None]
            if len(a) >= 10 and len(b) >= 10:
                print("   %-12s iz %.4f · kontrol %.4f · oran %.2fx  (N %d/%d)"
                      % (et, sx.median(a), sx.median(b), sx.median(a) / sx.median(b), len(a), len(b)))


if __name__ == "__main__":
    H1, H2 = {}, {}
    for s in ("BTC", "ETH"):
        d = topla(s)
        if not d:
            print("%s verisi yok — once scratchpad/major_5dk_indir.py" % s)
            continue
        H1[s] = h1(d)
        H2[s] = h2(d)
        karistirici(d)
    print("\n" + "=" * 96)
    print("GECME OLCUTU (on-kayit): p < %.6f · BTC ve ETH AYNI isaret ·" % P_ESIK)
    print("ay tutarliligi >= %60 · iki zaman yarisi ayni isaret")
    if len(H1) == 2:
        for ad, H in (("H1", H1), ("H2", H2)):
            ayni = [n for n in UFUK
                    if H.get("BTC", {}).get(n) is not None
                    and H.get("ETH", {}).get(n) is not None
                    and H["BTC"][n] * H["ETH"][n] > 0]
            print("%s — BTC ve ETH ayni isaretli ufuk: %s" % (ad, ayni or "YOK"))
    print("bot dosyalarina yazim: YOK")
