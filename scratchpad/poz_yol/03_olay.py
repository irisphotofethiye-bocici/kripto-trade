#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASAMA 2 — OLAY CALISMASI: sert hareketten ONCE kimildayan degisken var mi?

⚠️ BU BETIK ON_KAYIT_olay.md'ye BIREBIR UYAR. Esikler orada sabitlendi ve
   sonuc gorulduKten sonra DEGISTIRILMEYECEK (CLAUDE.md).

TASARIMIN KALBI: olcum penceresi hareketi ICERMEZ.
   t0 = sert hareketin BASLADIGI bar
   olcum = [t0 - 60dk, t0]        <- hareket DISARIDA
   (ilk denemede pencere hareketi iceriyordu -> "hacim %145 artti" bulgusu
    ongoru degil, hareketin TARIFIYDI.)

SALT OKUMA. Yalniz scratchpad/perp_seri/ okur.
"""
import os, sys, json, random, statistics as sx, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
SERI = os.path.join(SCRATCH, "perp_seri")

random.seed(11)

# --- ON-KAYITTA SABITLENEN ESIKLER — DOKUNULMAZ ---
ATR_N = 14
OLAY_BAR = 6            # 30 dk
OLAY_KAT = 2.0          # >= 2,0 x ATR
ONCE_BAR = 12           # olcum penceresi 60 dk
AYIRMA_BAR = 12         # olaylar cakismasin + kontrol olaydan uzak olsun
ALFA = 0.01
KARSILASTIRMA = 16      # 8 degisken x 2 yon
P_ESIK = ALFA / KARSILASTIRMA
# 🔴 ARAC HATASI (kosum sirasinda yakalandi, olcut DEGISMEDI):
#   PERM=1000 ile ulasilabilen EN KUCUK p = 1/1001 = 0,000999.
#   On-kayittaki esik 0,000625 bunun ALTINDA -> hicbir degisken GECEMEZDI.
#   Esik degil ARAC duzeltildi: PERM 1000 -> 20000 (min p = 0,00005).
PERM = 20000


def _yukle(sym, uc):
    yol = os.path.join(SERI, "%s_%s.json" % (sym, uc))
    if not os.path.exists(yol):
        return {}
    try:
        with open(yol, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        return {}
    z = "t" if uc == "kline" else "timestamp"
    return {int(x[z]): x for x in d}


def _atr_pct(k, i, n=ATR_N):
    """i barina kadar n barlik ATR, FIYATA ORANLA yuzde."""
    if i < n:
        return None
    tr = []
    for j in range(i - n + 1, i + 1):
        onceki = k[j - 1]["c"] if j > 0 else k[j]["o"]
        tr.append(max(k[j]["h"] - k[j]["l"], abs(k[j]["h"] - onceki), abs(k[j]["l"] - onceki)))
    c = k[i]["c"]
    return (sum(tr) / n) / c * 100 if c else None


def _degisim(a, b):
    if a is None or b is None or a == 0:
        return None
    return (b - a) / abs(a) * 100


def pencere(kl, oi, top, glob, tak, ts, i0, i1):
    """[i0, i1] penceresindeki degisim/oran olcumleri (hareket DISARIDA)."""
    t0, t1 = ts[i0], ts[i1]
    o = {}
    d_fiyat = _degisim(kl[i0]["c"], kl[i1]["c"])
    o["d_fiyat"] = d_fiyat
    a, b = oi.get(t0), oi.get(t1)
    d_oi = _degisim(float(a["sumOpenInterest"]) if a else None,
                    float(b["sumOpenInterest"]) if b else None)
    o["d_oi"] = d_oi
    if d_oi is not None and d_fiyat is not None and abs(d_fiyat) > 0.05:
        o["oi_fiyat_orani"] = d_oi / d_fiyat
    for kaynak, ad in ((top, "top_ls"), (glob, "glob_ls")):
        a, b = kaynak.get(t0), kaynak.get(t1)
        o["d_" + ad] = _degisim(float(a["longShortRatio"]) if a else None,
                                float(b["longShortRatio"]) if b else None)
    tb, gb = top.get(t1), glob.get(t1)
    if tb and gb:
        o["top_eksi_glob"] = float(tb["longShortRatio"]) - float(gb["longShortRatio"])
    a, b = tak.get(t0), tak.get(t1)
    if b:
        o["taker_orani"] = float(b["buySellRatio"])
    o["d_taker_orani"] = _degisim(float(a["buySellRatio"]) if a else None,
                                  float(b["buySellRatio"]) if b else None)
    o["d_hacim"] = _degisim(kl[i0]["qv"], kl[i1]["qv"])
    return o


DEGISKEN = ["d_oi", "oi_fiyat_orani", "d_top_ls", "d_glob_ls",
            "top_eksi_glob", "d_taker_orani", "taker_orani", "d_hacim"]


def sembol_isle(sym):
    """-> (yukari_olaylar, asagi_olaylar, kontroller)  her biri [(gun, olcum)]"""
    kl_m = _yukle(sym, "kline")
    if len(kl_m) < 200:
        return [], [], []
    ts = sorted(kl_m)
    kl = [kl_m[t] for t in ts]
    oi, top, glob, tak = (_yukle(sym, u) for u in ("oi", "top_ls", "glob_ls", "taker"))
    yukari, asagi, olay_idx = [], [], []
    i = ONCE_BAR
    while i < len(kl) - OLAY_BAR - 1:
        atr = _atr_pct(kl, i)
        if not atr:
            i += 1
            continue
        get = (kl[i + OLAY_BAR]["c"] - kl[i]["c"]) / kl[i]["c"] * 100
        if abs(get) >= OLAY_KAT * atr:
            o = pencere(kl, oi, top, glob, tak, ts, i - ONCE_BAR, i)
            gun = datetime.datetime.fromtimestamp(ts[i] / 1000).strftime("%Y-%m-%d")
            (yukari if get > 0 else asagi).append((gun, o))
            olay_idx.append(i)
            i += AYIRMA_BAR                      # cakisma yok
        else:
            i += 1
    # KONTROL: olaylardan >= AYIRMA_BAR uzak rastgele barlar, olay sayisiyla eslesik
    yasak = set()
    for j in olay_idx:
        yasak.update(range(j - AYIRMA_BAR, j + AYIRMA_BAR + 1))
    aday = [j for j in range(ONCE_BAR, len(kl) - OLAY_BAR - 1) if j not in yasak]
    n = len(yukari) + len(asagi)
    kontrol = []
    if aday and n:
        for j in random.sample(aday, min(n, len(aday))):
            o = pencere(kl, oi, top, glob, tak, ts, j - ONCE_BAR, j)
            gun = datetime.datetime.fromtimestamp(ts[j] / 1000).strftime("%Y-%m-%d")
            kontrol.append((gun, o))
    return yukari, asagi, kontrol


def _med(v):
    return sx.median(v) if v else None


def permutasyon(olay_v, kont_v):
    """Etiketleri karistirip gercek medyan farkinin p degerini bulur."""
    hepsi = olay_v + kont_v
    n = len(olay_v)
    gercek = sx.median(olay_v) - sx.median(kont_v)
    ust = 0
    for _ in range(PERM):
        random.shuffle(hepsi)
        f = sx.median(hepsi[:n]) - sx.median(hepsi[n:])
        if abs(f) >= abs(gercek):
            ust += 1
    return gercek, (ust + 1) / (PERM + 1)


def degerlendir(ad, olay, kontrol):
    print("\n" + "=" * 96)
    print("%s   olay=%d  kontrol=%d" % (ad, len(olay), len(kontrol)))
    print("=" * 96)
    if len(olay) < 50 or len(kontrol) < 50:
        print("N yetersiz (>=50 gerekli) — hukum yazilmaz.")
        return
    gunler = sorted({g for g, _ in olay})
    orta = gunler[len(gunler) // 2]
    print("%-18s %10s %10s %10s %9s %8s %8s %s"
          % ("degisken", "OLAY", "KONTROL", "fark", "p", "yari-A", "yari-B", "gun%"))
    print("-" * 96)
    for d in DEGISKEN:
        ov = [o[d] for _, o in olay if o.get(d) is not None]
        kv = [o[d] for _, o in kontrol if o.get(d) is not None]
        if len(ov) < 50 or len(kv) < 50:
            print("%-18s %10s %10s %10s %9s" % (d, "-", "-", "-", "N az"))
            continue
        fark, p = permutasyon(list(ov), list(kv))
        # zaman yarilari
        yar = []
        for f in (lambda g: g <= orta, lambda g: g > orta):
            a = [o[d] for g, o in olay if f(g) and o.get(d) is not None]
            b = [o[d] for g, o in kontrol if f(g) and o.get(d) is not None]
            yar.append(_med(a) - _med(b) if len(a) >= 10 and len(b) >= 10 else None)
        # gun-kumeli isaret tutarliligi
        gk = collections.defaultdict(list)
        for g, o in olay:
            if o.get(d) is not None:
                gk[g].append(o[d])
        kk = collections.defaultdict(list)
        for g, o in kontrol:
            if o.get(d) is not None:
                kk[g].append(o[d])
        ortak_gun = [g for g in gk if g in kk and len(gk[g]) >= 3 and len(kk[g]) >= 3]
        ayni = sum(1 for g in ortak_gun
                   if (sx.median(gk[g]) - sx.median(kk[g])) * fark > 0)
        gun_pct = 100 * ayni / len(ortak_gun) if ortak_gun else 0
        gecti = (p < P_ESIK and yar[0] is not None and yar[1] is not None
                 and yar[0] * yar[1] > 0 and yar[0] * fark > 0 and gun_pct >= 60)
        print("%-18s %+10.3f %+10.3f %+10.3f %9.5f %+8.3f %+8.3f %5.0f%% %s"
              % (d, sx.median(ov), sx.median(kv), fark, p,
                 yar[0] if yar[0] is not None else float("nan"),
                 yar[1] if yar[1] is not None else float("nan"),
                 gun_pct, "<<< GECTI" if gecti else ""))
    print("\ngecme olcutu (on-kayit): p < %.6f (Bonferroni %d karsilastirma) VE"
          % (P_ESIK, KARSILASTIRMA))
    print("iki zaman yarisinda ayni isaret VE gun-tutarliligi >= %%60")


def karistirici_kontrolu(ad, olay, kontrol, degisken):
    """🔴 ZORUNLU KONTROL — CLAUDE.md: monotonluk/anlamlilik TEK BASINA YETMEZ.

    ASIL SUPHE: olay, t0 SONRASI fiyat hareketiyle secilyor. Fiyat 30 dk olceginde
    ortalamaya donuyorsa, [t0-60,t0] penceresinde YUKSELMIS bir sembol sonraki
    30 dk'da DUSER. Taker orani da o yukselisle birlikte artmistir. O zaman
    "taker orani dususu ONCEDEN haber veriyor" demek YANLIS olur — olculen sey
    yalnizca FIYATIN KENDI GERI DONUSUDUR.

    Bu proje bu hatayi IKI KEZ yasadi (agresor dengesi 2026-08-17, son-yeni-uc
    2026-08-19): ikisi de kapilari gecti, fiyat/kar sabitlenince cokup gitti.

    TEST: pencere-ICI fiyat degisimi dilimlere bolunur; ayrim HER DILIM ICINDE
    de duruyor mu? Durmuyorsa bulgu fiyatin golgesidir."""
    print("\n--- KARISTIRICI KONTROLU: pencere-ici d_fiyat sabitlenince (%s) ---" % ad)
    bant = [(-99, -1.0, "d_fiyat < -1%"), (-1.0, -0.3, "-1..-0,3%"),
            (-0.3, 0.3, "-0,3..+0,3%"), (0.3, 1.0, "+0,3..+1%"), (1.0, 99, "> +1%")]
    print("%-16s %-14s %9s %9s %9s %8s" % ("degisken", "d_fiyat bandi", "OLAY", "KONTROL", "fark", "N"))
    print("-" * 72)
    for d in degisken:
        isaretler = []
        for lo, hi, et in bant:
            ov = [o[d] for _, o in olay
                  if o.get(d) is not None and o.get("d_fiyat") is not None
                  and lo <= o["d_fiyat"] < hi]
            kv = [o[d] for _, o in kontrol
                  if o.get(d) is not None and o.get("d_fiyat") is not None
                  and lo <= o["d_fiyat"] < hi]
            if len(ov) < 30 or len(kv) < 30:
                continue
            f = sx.median(ov) - sx.median(kv)
            isaretler.append(f)
            print("%-16s %-14s %+9.3f %+9.3f %+9.3f %8s"
                  % (d, et, sx.median(ov), sx.median(kv), f, "%d/%d" % (len(ov), len(kv))))
        if isaretler:
            ayni = sum(1 for f in isaretler if f * isaretler[0] > 0)
            print("%-16s %-14s -> %d/%d bantta AYNI isaret %s" %
                  ("", "OZET", ayni, len(isaretler),
                   "(saglam)" if ayni == len(isaretler) else "🔴 ISARET DONUYOR"))
        print()


def main():
    syms = sorted({f.rsplit("_", 1)[0] for f in os.listdir(SERI) if f.endswith("_kline.json")})
    print("OLAY CALISMASI — %d sembol · 5 dk · olay = 30 dk'da >= %.1f x ATR"
          % (len(syms), OLAY_KAT))
    print("olcum penceresi [t0-%d dk, t0] — HAREKET DISARIDA" % (ONCE_BAR * 5))
    Y, A, K = [], [], []
    for i, s in enumerate(syms, 1):
        y, a, k = sembol_isle(s)
        Y += y
        A += a
        K += k
        if i % 20 == 0:
            print("  ... %d/%d sembol · olay %d" % (i, len(syms), len(Y) + len(A)))
            sys.stdout.flush()
    print("\ntoplam: yukari %d · asagi %d · kontrol %d" % (len(Y), len(A), len(K)))
    degerlendir("SERT YUKARI hareketten ONCE", Y, K)
    karistirici_kontrolu("YUKARI", Y, K, ["d_taker_orani", "taker_orani", "d_hacim", "oi_fiyat_orani"])
    degerlendir("SERT ASAGI hareketten ONCE", A, K)
    karistirici_kontrolu("ASAGI", A, K, ["d_taker_orani", "taker_orani", "d_hacim", "oi_fiyat_orani"])
    print("\nbot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
