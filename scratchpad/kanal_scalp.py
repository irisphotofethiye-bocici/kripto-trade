#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SCALP VARYANTI + REJIM TESTI (2026-08-11)

KULLANICI SORUSU: "long icin kisa donem scalp olarak ayarlasak? genelde notr ve
bogada calistigi soyleniyor."

ON-KAYIT — BIRINCIL SCALP YAPILANDIRMASI (sweep'e BAKMADAN once secildi):
  hedef %1.0 · ufuk 4 bar · stop = A-stop (onceki olcumle kiyaslanabilir kalsin)
  Gerekce: 1 saatlik kriptoda %1 hedef + 4 saat gercek bir scalp; A-stop degismedi
  ki fark yalniz "scalp"ten gelsin.

REJIM — VERI NE DIYOR (olcumden ONCE bakildi, ve SONUCU BELIRLIYOR):
  BTC 2026-06-12 -> 2026-08-10: toplam +%1.1, tepeden dip -%13.4
  -> Bu pencere NOTR/YATAY. GERCEK BOGA YOK.
  SONUC: "bogada calisir" iddiasi BU VERIYLE TEST EDILEMEZ. Test edilmeyecek,
  edilmis gibi de yazilmayacak. Test edilebilen: NOTR ve BTC'nin yukselen alt donemleri.

  Rejim vekili = BTC'nin kendi MA500'u (saatlik, ~21 gun):
    BTC > MA500 -> "yukselen" (surenin %75'i)  ·  BTC < MA500 -> "dusen" (%25)
  Ikinci vekil: BTC son 24 saat degisimi (yatay/yukari/asagi).

⚠️ REJIM-ESLESMIS KONTROL SART:
  Yukselen bir piyasada HERHANGI bir long para kazanir. "Boga bucket'inda pozitif"
  demek strateji calisiyor demek DEGILDIR. Dogru kiyas: AYNI REJIMDEKI RASTGELE
  long'lar. Bu yuzden kontrol grubu da rejime gore bolunuyor.

GECME OLCUTU (on-kayitli, uclu):
  net > 0  VE  ayni rejimdeki rastgele kontrolu yenmek  VE  |t| >= 2
  VE her iki zaman yarisinda pozitif.
  Cok sayida hucreye bakiliyor -> |t| >= 2 sarti bu yuzden eklendi.

BEKLENTI (on-kayitli): NEGATIF. Sebep: maliyet %0.13, %1 hedefin %13'u; ve onceki
olcumde hedef yakinlastikca acik kapanmiyordu (bant x0.25'te bile -10.2 puan).
"""
import json, os, random, statistics as stx, collections, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kanal_stoch as ks

SCALP_HEDEF, SCALP_UFUK = 1.0, 4
random.seed(23)


def btc_rejim():
    b = json.load(open(os.path.join(ks.CACHE, "BTC.json"), encoding="utf-8"))
    c = [x["c"] for x in b]
    m500 = ks.ma(c, 500)
    out = {}
    for i, x in enumerate(b):
        if m500[i] is None or i < 24:
            continue
        d24 = (c[i] / c[i - 24] - 1) * 100
        out[x["t"] // 3600000] = {
            "ust": c[i] > m500[i],
            "d24": d24,
            "yon": "yukari" if d24 > 1.0 else ("asagi" if d24 < -1.0 else "yatay")}
    return out


def isle(b, si, hedef_pct, ufuk, stop_tipi, alt, atr):
    gi = si + 1
    if gi >= len(b) or None in (atr, alt):
        return None
    ref = b[gi]["o"]
    if ref <= 0:
        return None
    if stop_tipi == "A":
        dip = min(x["l"] for x in b[si - ks.STOP_NBAR + 1:si + 1])
        stop = min(dip, alt) - ks.STOP_ATR_PAY * atr
    elif stop_tipi == "0.5atr":
        stop = ref - 0.5 * atr
    else:                                    # sabit %
        stop = ref * (1 - float(stop_tipi) / 100)
    if stop >= ref:
        return None
    hedef = ref * (1 + hedef_pct / 100)
    sp = (ref - stop) / ref * 100
    son = min(gi + ufuk, len(b))
    if son - gi < 1:
        return None
    for j in range(gi, son):
        if b[j]["l"] <= stop:
            return -sp - ks.MALIYET, "STOP", sp
        if b[j]["h"] >= hedef:
            return hedef_pct - ks.MALIYET, "HEDEF", sp
    return (b[son - 1]["c"] - ref) / ref * 100 - ks.MALIYET, "SURE", sp


def oz(v):
    if len(v) < 40:
        return None
    g = [x[0] for x in v]
    sh = stx.pstdev(g) / len(g) ** 0.5 if len(g) > 1 else 0
    return {"n": len(g), "ort": stx.mean(g), "sh": sh, "t": (stx.mean(g) / sh) if sh else 0,
            "isabet": sum(1 for x in v if x[1] == "HEDEF") / len(v) * 100,
            "stop": stx.median([x[2] for x in v])}


def main():
    rej = btc_rejim()
    dosyalar = sorted(f[:-5] for f in os.listdir(ks.CACHE) if f.endswith(".json"))
    olay, kontrol = [], []
    for sym in dosyalar:
        if sym == "BTC":
            continue
        try:
            b = json.load(open(os.path.join(ks.CACHE, sym + ".json"), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ks.ISINMA + 60:
            continue
        c = [x["c"] for x in b]
        au, aa = ks.acc_bands(b)
        A = ks.atr_serisi(b)
        K, D = ks.stochrsi(ks.wilder_rsi(c))
        son = -10 ** 9
        for i in range(ks.ISINMA, len(b) - 60):
            r = rej.get(b[i]["t"] // 3600000)
            if r is None or None in (K[i], D[i], K[i - 1], D[i - 1], A[i], aa[i]):
                continue
            if not (K[i - 1] < ks.ASIRI_SATIM and K[i - 1] <= D[i - 1] and K[i] > D[i]):
                continue
            if b[i]["l"] > aa[i] or i - son < ks.SEYRELT:
                continue
            son = i
            olay.append({"b": b, "i": i, "t": b[i]["t"], "aa": aa[i], "au": au[i],
                         "atr": A[i], "rej": r})
        for _ in range(max(2, (len(b) - ks.ISINMA) // 150)):
            i = random.randint(ks.ISINMA, len(b) - 61)
            r = rej.get(b[i]["t"] // 3600000)
            if r is None or aa[i] is None or A[i] is None:
                continue
            kontrol.append({"b": b, "i": i, "t": b[i]["t"], "aa": aa[i], "au": au[i],
                            "atr": A[i], "rej": r})
    tl = sorted(o["t"] for o in olay)
    ORTA = tl[len(tl) // 2]

    print("=" * 112)
    print("SCALP LONG + REJIM — Price Headley Acc.Bands + StochRSI · 1 saatlik")
    print("=" * 112)
    print(f"Sinyal: {len(olay)}  ·  rejim-eslesmis kontrol: {len(kontrol)}")
    print(f"BIRINCIL SCALP (on-kayitli): hedef %{SCALP_HEDEF} · ufuk {SCALP_UFUK} bar · A-stop")
    print(f"Maliyet %{ks.MALIYET} = hedefin %{ks.MALIYET/SCALP_HEDEF*100:.0f}'i\n")

    def calis(sec, hedef=SCALP_HEDEF, ufuk=SCALP_UFUK, stop="A"):
        return [x for x in (isle(o["b"], o["i"], hedef, ufuk, stop, o["aa"], o["atr"])
                            for o in sec) if x]

    print("1) HEDEF x UFUK IZGARASI (A-stop) — KESIFSEL, on-kayitli degil")
    print("-" * 112)
    print(f"{'hedef':>8}" + "".join(f"{u:>2} bar".rjust(12) for u in (2, 4, 6, 12))
          + "      (her hucre: net% / isabet)")
    for hd in (0.5, 0.75, 1.0, 1.5, 2.0):
        sat = f"%{hd:<7.2f}"
        for uf in (2, 4, 6, 12):
            a = oz(calis(olay, hd, uf))
            sat += f"{a['ort']:+7.2f}/{a['isabet']:3.0f}%" if a else "        -   "
        print(sat)
    print("  basabas isabet = (stop+0.13)/((hedef-0.13)+(stop+0.13))")

    print("\n2) BIRINCIL SCALP — REJIME GORE (rejim-eslesmis kontrolle)")
    print("-" * 112)
    print(f"{'rejim':30}{'N':>6}{'net %':>9}{'t':>7}{'isabet':>8}"
          f"{'KONTROL':>10}{'fark':>8}{'A yari':>9}{'B yari':>9}")
    BOL = [("TUMU", lambda o: True),
           ("BTC > MA500 (yukselen)", lambda o: o["rej"]["ust"]),
           ("BTC < MA500 (dusen)", lambda o: not o["rej"]["ust"]),
           ("BTC 24s YATAY (notr)", lambda o: o["rej"]["yon"] == "yatay"),
           ("BTC 24s YUKARI", lambda o: o["rej"]["yon"] == "yukari"),
           ("BTC 24s ASAGI", lambda o: o["rej"]["yon"] == "asagi")]
    for ad, fn in BOL:
        s = [o for o in olay if fn(o)]
        a = oz(calis(s))
        k = oz(calis([o for o in kontrol if fn(o)]))
        if not a:
            continue
        A = oz(calis([o for o in s if o["t"] < ORTA]))
        B = oz(calis([o for o in s if o["t"] >= ORTA]))
        fark = a["ort"] - k["ort"] if k else float("nan")
        print(f"{ad:30}{a['n']:6d}{a['ort']:+9.2f}{a['t']:+7.2f}{a['isabet']:7.1f}%"
              f"{(k['ort'] if k else 0):+10.2f}{fark:+8.2f}"
              f"{(A['ort'] if A else 0):+9.2f}{(B['ort'] if B else 0):+9.2f}")

    print("\n3) STOP VARYANTLARI (birincil hedef/ufuk) — KESIFSEL")
    print("-" * 112)
    print(f"{'stop tipi':30}{'N':>6}{'stop%':>8}{'basabas':>10}{'isabet':>9}{'net %':>9}{'t':>7}")
    for st, ad in (("A", "A-stop (asil)"), ("0.5atr", "0.5 x ATR"),
                   ("0.5", "sabit %0.5"), ("1.0", "sabit %1.0")):
        v = calis(olay, stop=st)
        a = oz(v)
        if not a:
            continue
        bb = (a["stop"] + ks.MALIYET) / ((SCALP_HEDEF - ks.MALIYET) + a["stop"] + ks.MALIYET) * 100
        print(f"{ad:30}{a['n']:6d}{a['stop']:7.2f}%{bb:9.1f}%{a['isabet']:8.1f}%"
              f"{a['ort']:+9.2f}{a['t']:+7.2f}")

    print("\n" + "=" * 112)
    print("GECME OLCUTU: net>0 VE rejim-eslesmis kontrolu yenmek VE |t|>=2 VE iki yari +")
    print("=" * 112)
    for ad, fn in BOL:
        s = [o for o in olay if fn(o)]
        a = oz(calis(s))
        k = oz(calis([o for o in kontrol if fn(o)]))
        if not a or not k:
            continue
        A = oz(calis([o for o in s if o["t"] < ORTA]))
        B = oz(calis([o for o in s if o["t"] >= ORTA]))
        c1, c2 = a["ort"] > 0, a["ort"] > k["ort"]
        c3 = abs(a["t"]) >= 2
        c4 = A is not None and B is not None and A["ort"] > 0 and B["ort"] > 0
        print(f"  {ad:26} net>0 {'E' if c1 else 'H'} · kontrol {'E' if c2 else 'H'} · "
              f"|t|>=2 {'E' if c3 else 'H'} · iki yari {'E' if c4 else 'H'}  ->  "
              f"{'GECTI' if all((c1,c2,c3,c4)) else 'KALDI'}")
    print("\n  NOT: bu pencerede GERCEK BOGA YOK (BTC 60 gunde +%1.1).")
    print("  'Bogada calisir' iddiasi BU VERIYLE TEST EDILEMEDI.")


if __name__ == "__main__":
    main()
