#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KANAL + StochRSI OLCUMU (2026-08-11) — on-kayit: fikir-defteri.md, commit 2bde27b

KISIT (kullanici): bota DOKUNULMAYACAK, sisteme EKLEME YAPILMAYACAK.
  Bu betik yalniz scratchpad/klines_1h onbelligini OKUR. testbot/radar/config/golge
  defterine hicbir sey yazmaz, hicbirini import etmez.

KAYNAK: kullanici bir X videosundan aldi; gonderi acilamadi (HTTP 402).
  Ancak KULLANICI INDIKATORU SOYLEDI: "price hadley ve stokastik rsi"
  -> PRICE HEADLEY ACCELERATION BANDS (TradingView yerlesik) + StochRSI.
  Belirsizlik kalkti; ASIL OLCUM bu bantla yapiliyor.

  DEGISIKLIK KAYDI: on-kayit (commit 2bde27b) indikator kimligi bilinmedigi icin
  Bollinger+Donchian yaziyordu. Kullanici kimligi bildirince ASIL bant Acceleration
  Bands olarak degistirildi. BU DEGISIKLIK HICBIR SONUC GORULMEDEN yapildi
  (betik o ana kadar hic kosturulmamisti) -> girdi duzeltmesi, bulguya gore ayar DEGIL.
  Bollinger ve Donchian DUYARLILIK KONTROLU olarak tabloda kaldi: sonuc bant
  ailesine ne kadar bagimli, gorunsun.

  DONCHIAN INCELIGI: bant SIMDIKI bari DISLAR (min(low[i-20:i])). Icerseydi
  "low[i] <= alt_bant" HER BARDA dogru olurdu (bar bandi kendisi tanimlar) -> dejenere.

ON-KAYITLI SABITLER (sonuc gorulmeden yazildi):
  giris    : sonraki barin acilisi b[gi]["o"]
  stop     : min(son 10 bar dibi, alt bant) - 0.25*ATR(14)
  hedef    : giristeki ust bant, DONDURULMUS (hareketli hedef dusen piyasada sahte kazanc uretir)
  ufuk     : BIRINCIL 12 bar (config maliyet.tutma_saat_tf["1h"]) · ikincil 48 (bilgi icin)
  maliyet  : %0.13 (taker 0.045x2 + slipaj 0.02x2)
  ayni bar : stop ve hedef birlikte gorulurse STOP (kotumser)
  seyreltme: ayni sembolde en az 24 bar ara
  isinma   : i >= 200

GECME OLCUTU: net > 0  VE  kontrolu yenmek  VE  HER IKI zaman yarisinda pozitif.
BEKLENTI (on-kayitli): NEGATIF.
"""
import json, os, random, statistics as stx, datetime, collections

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h")

BANT_N, BANT_K = 20, 2.0
RSI_N, STOCH_N, K_N, D_N = 14, 14, 3, 3
ASIRI_SATIM, ASIRI_ALIM = 20.0, 80.0
ATR_N, STOP_NBAR, STOP_ATR_PAY = 14, 10, 0.25
MALIYET = 0.13
SEYRELT, ISINMA = 24, 200
UFUK_BIRINCIL, UFUK_IKINCIL = 12, 48
random.seed(11)


# ----------------------------------------------------------------- gostergeler
def wilder_rsi(c, n=RSI_N):
    out = [None] * len(c)
    if len(c) < n + 1:
        return out
    kaz = kay = 0.0
    for i in range(1, n + 1):
        d = c[i] - c[i - 1]
        kaz += max(d, 0.0); kay += max(-d, 0.0)
    ag, al = kaz / n, kay / n
    out[n] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(n + 1, len(c)):
        d = c[i] - c[i - 1]
        ag = (ag * (n - 1) + max(d, 0.0)) / n
        al = (al * (n - 1) + max(-d, 0.0)) / n
        out[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def stochrsi(r, n=STOCH_N, kn=K_N, dn=D_N):
    """ham -> %K = SMA(kn) -> %D = SMA(dn, %K).  RSI duz ise ham=0.5 (sifira bolme korumasi)."""
    ham = [None] * len(r)
    for i in range(len(r)):
        p = r[i - n + 1:i + 1]
        if i < n - 1 or any(x is None for x in p):
            continue
        lo, hi = min(p), max(p)
        ham[i] = 0.5 if hi <= lo else (r[i] - lo) / (hi - lo)
    def sma(src, m):
        o = [None] * len(src)
        for i in range(len(src)):
            p = src[i - m + 1:i + 1]
            if i < m - 1 or any(x is None for x in p):
                continue
            o[i] = sum(p) / m
        return o
    K = sma([None if x is None else x * 100 for x in ham], kn)
    return K, sma(K, dn)


def bollinger(c, n=BANT_N, k=BANT_K):
    ust, alt = [None] * len(c), [None] * len(c)
    s = s2 = 0.0
    for i, x in enumerate(c):
        s += x; s2 += x * x
        if i >= n:
            y = c[i - n]; s -= y; s2 -= y * y
        if i >= n - 1:
            m = s / n
            var = max(s2 / n - m * m, 0.0)
            sd = var ** 0.5
            ust[i], alt[i] = m + k * sd, m - k * sd
    return ust, alt


def acc_bands(b, n=BANT_N):
    """PRICE HEADLEY ACCELERATION BANDS — TradingView yerlesik surumu.
       upper = SMA(high * (1 + 4*(high-low)/(high+low)), n)
       lower = SMA(low  * (1 - 4*(high-low)/(high+low)), n)
    (TV kaynagi 2*((h-l)/((h+l)/2)) yazar; sadelesince 4*(h-l)/(h+l) ile ayni sey.)

    NOT — YAZARIN KENDI KULLANIMI TERSI: Headley bu bantlari KIRILIM icin tasarladi;
    fiyatin bant DISINDA art arda kapanmasini 'hizlanma' sinyali sayar. Videodaki
    kullanim (alt bantta AL) ortalamaya donustur, yani indikatorun tasarim amacinin
    tersi. Bu belirtiyi olcum yorumlarken hatirla; olcum yine tarif edildigi gibi yapilir.
    """
    ust, alt = [None] * len(b), [None] * len(b)
    uv, lv, su, sl = [], [], 0.0, 0.0
    for i, x in enumerate(b):
        h, l = x["h"], x["l"]
        hl = h + l
        f = 4.0 * (h - l) / hl if hl > 0 else 0.0
        uv.append(h * (1 + f)); lv.append(l * (1 - f))
        su += uv[i]; sl += lv[i]
        if i >= n:
            su -= uv[i - n]; sl -= lv[i - n]
        if i >= n - 1:
            ust[i], alt[i] = su / n, sl / n
    return ust, alt


def donchian(b, n=BANT_N):
    """SIMDIKI bari DISLAR — icerse dejenere olurdu (bkz. dosya basligi)."""
    ust, alt = [None] * len(b), [None] * len(b)
    for i in range(n, len(b)):
        p = b[i - n:i]
        ust[i] = max(x["h"] for x in p); alt[i] = min(x["l"] for x in p)
    return ust, alt


def atr_serisi(b, n=ATR_N):
    out = [None] * len(b)
    tr = [None] * len(b)
    for i in range(1, len(b)):
        pc = b[i - 1]["c"]
        tr[i] = max(b[i]["h"] - b[i]["l"], abs(b[i]["h"] - pc), abs(pc - b[i]["l"]))
    if len(b) <= n:
        return out
    a = sum(tr[1:n + 1]) / n
    out[n] = a
    for i in range(n + 1, len(b)):
        a = (a * (n - 1) + tr[i]) / n
        out[i] = a
    return out


def ma(c, n):
    out = [None] * len(c)
    s = 0.0
    for i, x in enumerate(c):
        s += x
        if i >= n:
            s -= c[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


# ----------------------------------------------------------------- islem
def islem(b, si, yon, alt, ust, atr, ufuk):
    """si = SINYAL bari. Giris si+1'in acilisi. Doner (net%, tip, stop%, hedef%)."""
    gi = si + 1
    if gi >= len(b) or atr is None or alt is None or ust is None:
        return None
    ref = b[gi]["o"]
    if ref <= 0:
        return None
    if yon == "LONG":
        dip = min(x["l"] for x in b[si - STOP_NBAR + 1:si + 1])
        stop = min(dip, alt) - STOP_ATR_PAY * atr
        hedef = ust
        if not (stop < ref < hedef):
            return None
    else:
        tepe = max(x["h"] for x in b[si - STOP_NBAR + 1:si + 1])
        stop = max(tepe, ust) + STOP_ATR_PAY * atr
        hedef = alt
        if not (hedef < ref < stop):
            return None
    sp = abs(ref - stop) / ref * 100
    hp = abs(hedef - ref) / ref * 100
    if sp <= 0 or hp <= 0:
        return None
    son = min(gi + ufuk, len(b))
    if son - gi < 2:
        return None
    for j in range(gi, son):
        x = b[j]
        if yon == "LONG":
            if x["l"] <= stop:
                return -sp - MALIYET, "STOP", sp, hp
            if x["h"] >= hedef:
                return hp - MALIYET, "HEDEF", sp, hp
        else:
            if x["h"] >= stop:
                return -sp - MALIYET, "STOP", sp, hp
            if x["l"] <= hedef:
                return hp - MALIYET, "HEDEF", sp, hp
    c = b[son - 1]["c"]
    g = (c - ref) / ref * 100 if yon == "LONG" else (ref - c) / ref * 100
    return g - MALIYET, "SURE", sp, hp


def oz(kayit):
    k = [x for x in kayit if x]
    if not k:
        return None
    g = [x[0] for x in k]
    return {"n": len(g), "ort": stx.mean(g), "med": stx.median(g),
            "isabet": sum(1 for x in k if x[1] == "HEDEF") / len(k) * 100,
            "stop": stx.median([x[2] for x in k]),
            "hedef": stx.median([x[3] for x in k]),
            "toplam": sum(g)}


# ----------------------------------------------------------------- toplama
def olaylari_topla():
    dosyalar = sorted(f[:-5] for f in os.listdir(CACHE) if f.endswith(".json"))
    kume = collections.defaultdict(list)
    for sym in dosyalar:
        try:
            b = json.load(open(os.path.join(CACHE, sym + ".json"), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ISINMA + 60:
            continue
        c = [x["c"] for x in b]
        au, aa = acc_bands(b)          # BIRINCIL: Price Headley Acceleration Bands
        bu, ba = bollinger(c)          # duyarlilik kontrolu
        du, da = donchian(b)           # duyarlilik kontrolu
        A = atr_serisi(b)
        K, D = stochrsi(wilder_rsi(c))
        m200 = ma(c, 200)
        son = collections.defaultdict(lambda: -10 ** 9)

        def ekle(ad, i, yon, alt, ust, ek=None):
            if i - son[ad] < SEYRELT:
                return
            r = islem(b, i, yon, alt, ust, A[i], UFUK_BIRINCIL)
            r2 = islem(b, i, yon, alt, ust, A[i], UFUK_IKINCIL)
            if not r:
                return
            son[ad] = i
            genislik = (ust - alt) / c[i] * 100 if (ust and alt and c[i]) else None
            kume[ad].append({"sym": sym, "i": i, "t": b[i]["t"], "r": r, "r2": r2,
                             "genislik": genislik, "trend": (m200[i] is not None and c[i] > m200[i]),
                             **(ek or {})})

        for i in range(ISINMA, len(b) - UFUK_IKINCIL - 2):
            if None in (K[i], D[i], K[i - 1], D[i - 1], A[i]):
                continue
            stoch_long = K[i - 1] < ASIRI_SATIM and K[i - 1] <= D[i - 1] and K[i] > D[i]
            stoch_short = K[i - 1] > ASIRI_ALIM and K[i - 1] >= D[i - 1] and K[i] < D[i]
            # --- BIRINCIL: Price Headley Acceleration Bands (videodaki indikator)
            if aa[i] is not None:
                acc_long = b[i]["l"] <= aa[i]
                acc_short = b[i]["h"] >= au[i]
                if acc_long and stoch_long:
                    ekle("ACC LONG  (bant+stoch)  <== ASIL", i, "LONG", aa[i], au[i])
                if acc_short and stoch_short:
                    ekle("ACC SHORT (bant+stoch)  <== ASIL", i, "SHORT", aa[i], au[i])
                if acc_long:
                    ekle("  ayristirma: yalniz BANT (long)", i, "LONG", aa[i], au[i])
                if stoch_long:
                    ekle("  ayristirma: yalniz STOCH (long)", i, "LONG", aa[i], au[i])
                # Headley'nin KENDI kullanimi: bant disinda kapanis = hizlanma/kirilim
                if b[i]["c"] > au[i] and b[i - 1]["c"] > au[i - 1]:
                    ekle("  yazarin kendi kullanimi: KIRILIM long", i, "LONG", aa[i], au[i])
            # --- duyarlilik: bant ailesi degisirse sonuc degisiyor mu?
            if ba[i] is not None:
                if b[i]["l"] <= ba[i] and stoch_long:
                    ekle("BOLL LONG (duyarlilik)", i, "LONG", ba[i], bu[i])
                if b[i]["h"] >= bu[i] and stoch_short:
                    ekle("BOLL SHORT (duyarlilik)", i, "SHORT", ba[i], bu[i])
            if da[i] is not None:
                if b[i]["l"] <= da[i] and stoch_long:
                    ekle("DONCH LONG (duyarlilik)", i, "LONG", da[i], du[i])
                if b[i]["h"] >= du[i] and stoch_short:
                    ekle("DONCH SHORT (duyarlilik)", i, "SHORT", da[i], du[i])
        # --- kontrol: rastgele barlar, ayni mekanik (Bollinger seviyeleriyle)
        # KONTROL: rastgele barlar, ayni mekanik, ASIL bantlarla (Acceleration Bands)
        for _ in range(max(2, (len(b) - ISINMA) // 120)):
            i = random.randint(ISINMA, len(b) - UFUK_IKINCIL - 3)
            if aa[i] is None or A[i] is None:
                continue
            for yon, ad in (("LONG", "KONTROL rastgele (long)"),
                            ("SHORT", "KONTROL rastgele (short)")):
                r = islem(b, i, yon, aa[i], au[i], A[i], UFUK_BIRINCIL)
                if not r:
                    continue
                kume[ad].append(
                    {"sym": sym, "i": i, "t": b[i]["t"], "r": r,
                     "r2": islem(b, i, yon, aa[i], au[i], A[i], UFUK_IKINCIL),
                     "genislik": (au[i] - aa[i]) / c[i] * 100,
                     "trend": (m200[i] is not None and c[i] > m200[i])})
    return kume


def main():
    kume = olaylari_topla()
    tum_t = sorted(o["t"] for v in kume.values() for o in v)
    ORTA = tum_t[len(tum_t) // 2]

    print("=" * 120)
    print("PRICE HEADLEY ACCELERATION BANDS + StochRSI — 1 saatlik · 570 sembol · ~60 gun · giris sonraki bar acilisi")
    print("=" * 120)
    print(f"Maliyet %{MALIYET} · ufuk BIRINCIL {UFUK_BIRINCIL} bar · hedef girisde DONDURULMUS "
          f"· seyreltme {SEYRELT} bar")
    print(f"ON-KAYIT: fikir-defteri.md, commit 2bde27b (kosturmadan ONCE)\n")
    print(f"{'kume':38}{'N':>6}{'net %':>9}{'isabet':>9}{'stop%':>8}{'hedef%':>9}"
          f"{'A yari':>9}{'B yari':>9}{'toplam':>10}")
    print("-" * 120)
    SIRA = ["ACC LONG  (bant+stoch)  <== ASIL", "ACC SHORT (bant+stoch)  <== ASIL",
            "  ayristirma: yalniz BANT (long)", "  ayristirma: yalniz STOCH (long)",
            "  yazarin kendi kullanimi: KIRILIM long",
            "BOLL LONG (duyarlilik)", "BOLL SHORT (duyarlilik)",
            "DONCH LONG (duyarlilik)", "DONCH SHORT (duyarlilik)",
            "KONTROL rastgele (long)", "KONTROL rastgele (short)"]
    sonuc = {}
    for ad in SIRA:
        v = kume.get(ad, [])
        if len(v) < 60:
            continue
        a = oz([o["r"] for o in v])
        A = oz([o["r"] for o in v if o["t"] < ORTA])
        B = oz([o["r"] for o in v if o["t"] >= ORTA])
        if not a:
            continue
        sonuc[ad] = (a, A, B)
        im = " *" if a["ort"] > 0 else ""
        print(f"{ad:38}{a['n']:6d}{a['ort']:+9.2f}{a['isabet']:8.1f}%{a['stop']:7.2f}%"
              f"{a['hedef']:8.2f}%{(A['ort'] if A else 0):+9.2f}{(B['ort'] if B else 0):+9.2f}"
              f"{a['toplam']:+10.0f}{im}")
    print("-" * 120)
    print("  '*' = net pozitif · 'stop%' ve 'hedef%' medyan")

    print("\n" + "=" * 120)
    print(f"IKINCIL UFUK ({UFUK_IKINCIL} bar) — yalniz bilgi, karar BIRINCILDEN verilir")
    print("=" * 120)
    print(f"{'kume':38}{'N':>6}{'net %':>9}{'isabet':>9}{'A yari':>9}{'B yari':>9}")
    print("-" * 120)
    for ad in SIRA:
        v = [o for o in kume.get(ad, []) if o.get("r2")]
        if len(v) < 60:
            continue
        a = oz([o["r2"] for o in v])
        A = oz([o["r2"] for o in v if o["t"] < ORTA])
        B = oz([o["r2"] for o in v if o["t"] >= ORTA])
        print(f"{ad:38}{a['n']:6d}{a['ort']:+9.2f}{a['isabet']:8.1f}%"
              f"{(A['ort'] if A else 0):+9.2f}{(B['ort'] if B else 0):+9.2f}")

    print("\n" + "=" * 120)
    print("FILTRELER — ana kumeler uzerinde (birincil ufuk)")
    print("=" * 120)
    for ad in ("ACC LONG  (bant+stoch)  <== ASIL", "ACC SHORT (bant+stoch)  <== ASIL"):
        v = kume.get(ad, [])
        if len(v) < 60:
            continue
        print(f"\n### {ad}   (filtresiz N={len(v)})")
        print(f"{'filtre':34}{'N':>6}{'net %':>9}{'isabet':>9}{'A yari':>9}{'B yari':>9}")
        print("-" * 120)
        alt_kume = [("trend filtresi: fiyat > MA200", [o for o in v if o["trend"]]),
                    ("trend filtresi: fiyat < MA200", [o for o in v if not o["trend"]])]
        gen = sorted(o["genislik"] for o in v if o["genislik"] is not None)
        for p, ad2 in ((0.25, "%25"), (0.50, "medyan"), (0.75, "%75")):
            esik = gen[int(len(gen) * p)]
            alt_kume.append((f"bant genisligi >= {esik:.2f}% ({ad2})",
                             [o for o in v if (o["genislik"] or 0) >= esik]))
        for ad2, s in alt_kume:
            if len(s) < 60:
                continue
            a = oz([o["r"] for o in s])
            A = oz([o["r"] for o in s if o["t"] < ORTA])
            B = oz([o["r"] for o in s if o["t"] >= ORTA])
            im = " *" if a["ort"] > 0 else ""
            print(f"{ad2:34}{a['n']:6d}{a['ort']:+9.2f}{a['isabet']:8.1f}%"
                  f"{(A['ort'] if A else 0):+9.2f}{(B['ort'] if B else 0):+9.2f}{im}")

    print("\n" + "=" * 120)
    print("GECME OLCUTU (on-kayitli): net>0  VE  kontrolu yenmek  VE  HER IKI yarida pozitif")
    print("=" * 120)
    for ad in ("ACC LONG  (bant+stoch)  <== ASIL", "ACC SHORT (bant+stoch)  <== ASIL",
               "BOLL LONG (duyarlilik)", "BOLL SHORT (duyarlilik)",
               "DONCH LONG (duyarlilik)", "DONCH SHORT (duyarlilik)"):
        if ad not in sonuc:
            continue
        a, A, B = sonuc[ad]
        kad = "KONTROL rastgele (long)" if "LONG" in ad else "KONTROL rastgele (short)"
        kon = sonuc.get(kad, (None,))[0]
        s1 = a["ort"] > 0
        s2 = kon is not None and a["ort"] > kon["ort"]
        s3 = A is not None and B is not None and A["ort"] > 0 and B["ort"] > 0
        print(f"  {ad:30} net>0 {'E' if s1 else 'H'} · kontrolu yener {'E' if s2 else 'H'} "
              f"· iki yari + {'E' if s3 else 'H'}   ->  {'GECTI' if (s1 and s2 and s3) else 'KALDI'}")


if __name__ == "__main__":
    main()
