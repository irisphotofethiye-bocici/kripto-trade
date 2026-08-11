#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIKIR 1 — "KAC OLU SINYALIMIZ ASLINDA CANLIYDI?" (2026-08-11)

GEREKCE: bugun ogrendik ki A-stopumuz 4 barlik GERCEK bir kenari oldurebiliyor
  (kanal stratejisi: stopsuz +0.112 t=+3.13 -> A-stopla +0.051 t=+1.57).
  Bu projede "negatif" diye kapatilmis HER SEY stoplu olculmustu.
  Yani bir kismi YANLIS NEGATIF olabilir.

BU BETIK: arsivdeki her hucreyi IKI kez olcer ve karsilastirir —
  HAM      : stop yok, hedef yok, maliyet yok   (sinyalde bilgi VAR MI?)
  MEKANIK  : A-stop + hedef + maliyet           (bizim sistemimiz onu koruyor mu?)
  BAYRAK   : ham iki yarida da POZITIF  AMA  mekanik NEGATIF  ->  YANLIS NEGATIF ADAYI

BILINEN HEDEF: yon_avi.py iki LONG hucresini ham olcumde POZITIF bulmustu
  (iki yarida da!) ve yon_dogrula.py mekanikte oldurmustu:
    "MA50 dusuk + fiyat YUKSEK"  rel24 +0.89  N=125  (A +0.72 / B +1.12)
    "fiyat YUKSEK + chg24 dusuk" rel24 +0.72  N=119  (A +0.47 / B +1.31)
  Bunlar tam olarak bugunku dersin tarif ettigi durum. Once onlar sinaniyor.

SISTEME DOKUNULMAZ: yalniz scratchpad + salt-okunur onbellek.
"""
import json, os, sys, statistics as stx, datetime, itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yon_avi
import yon_dogrula as yd

MALIYET = 0.09          # projenin onceki olcumleriyle kiyaslanabilir kalsin
UFUKLAR = (1, 2, 4, 6, 12, 24, 48, 72)


def barlari_bagla(ge):
    bc, idxc = {}, {}
    for o in ge:
        s = o["sym"]
        if s not in bc:
            p = os.path.join(yd.CACHE, f"{s}.json")
            bc[s] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
            if bc[s]:
                idxc[s] = {x["t"] // 3600000: i for i, x in enumerate(bc[s])}
        if not bc[s]:
            continue
        ms = int(datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M")
                 .astimezone().timestamp() * 1000)
        o["_b"], o["_gi"] = bc[s], idxc[s].get(ms // 3600000)
    return [o for o in ge if o.get("_gi") is not None]


def ham_getiri(o, ufuk, yon):
    """STOP YOK · HEDEF YOK · MALIYET YOK. Giris sonraki barin acilisi."""
    b, gi = o["_b"], o["_gi"] + 1
    if gi + ufuk >= len(b):
        return None
    ref = b[gi]["o"]
    if ref <= 0:
        return None
    g = (b[gi + ufuk]["c"] / ref - 1) * 100
    return g if yon == "LONG" else -g


def stopsuz_net(o, ufuk, yon):
    g = ham_getiri(o, ufuk, yon)
    return None if g is None else g - MALIYET


def oz(v, asgari=60):
    """asgari: yarilarda 30'a duser — 60'ta kalirsa kucuk hucrelerin yarilari
    None doner ve tabloda 0.00 gorunup 'yari coktu' diye YANLIS okunur (2026-08-11 hatasi)."""
    v = [x for x in v if x is not None]
    if len(v) < asgari:
        return None
    sh = stx.pstdev(v) / len(v) ** 0.5 if len(v) > 1 else 0
    return {"n": len(v), "ort": stx.mean(v), "med": stx.median(v),
            "sh": sh, "t": stx.mean(v) / sh if sh else 0}


def mek(sec, yon, hedef, ufuk):
    r = [yd.islem(o["_b"], o["_gi"] + 1, hedef, ufuk, yon) for o in sec]
    r = [x[0] for x in r if x]
    return oz(r)


def main():
    ge = barlari_bagla(yon_avi.yukle())
    tsl = sorted(o["ts"] for o in ge)
    ORTA = tsl[len(tsl) // 2]
    print("=" * 116)
    print("FIKIR 1 — HAM vs MEKANIK: hangi 'olu' sinyal aslinda canliydi?")
    print("=" * 116)
    print(f"Olay: {len(ge)}  ·  maliyet %{MALIYET}  ·  HAM = stop/hedef/maliyet YOK\n")

    def q(alan, p):
        v = sorted(o[alan] for o in ge if o.get(alan) is not None)
        return v[int(len(v) * p)] if v else None

    ma50_alt, ma50_ust = q("ma50_mesafe", 0.2), q("ma50_mesafe", 0.8)
    fiyat_alt, fiyat_ust = q("fiyat_log", 0.2), q("fiyat_log", 0.8)
    chg_alt, chg_ust = q("chg24", 0.2), q("chg24", 0.8)
    skor_ust = q("score", 0.8)
    oi_ust = q("oi24", 0.8)

    HUCRE = [
        # --- yon_avi'nin HAM olcumde POZITIF bulup mekanikte olen LONG hucreleri
        ("LONG: MA50 dusuk + fiyat YUKSEK", "LONG",
         lambda o: o.get("ma50_mesafe") is not None and o["ma50_mesafe"] <= ma50_alt
         and o.get("fiyat_log") is not None and o["fiyat_log"] >= fiyat_ust),
        ("LONG: fiyat YUKSEK + chg24 dusuk", "LONG",
         lambda o: o.get("fiyat_log") is not None and o["fiyat_log"] >= fiyat_ust
         and (o.get("chg24") or 0) <= chg_alt),
        ("LONG: MA50 dusuk (tek)", "LONG",
         lambda o: o.get("ma50_mesafe") is not None and o["ma50_mesafe"] <= ma50_alt),
        ("LONG: fiyat YUKSEK (tek)", "LONG",
         lambda o: o.get("fiyat_log") is not None and o["fiyat_log"] >= fiyat_ust),
        ("LONG: chg24 dusuk (tek)", "LONG", lambda o: (o.get("chg24") or 0) <= chg_alt),
        ("LONG: funding pozitif >= 0.05", "LONG", lambda o: (o.get("funding") or 0) >= 0.05),
        # --- canlidaki kapilar (referans: ham olcumde ne kadar guclu?)
        ("SHORT: A+B (canli kapi)", "SHORT",
         lambda o: (o.get("funding") or 0) <= -0.05 and (o.get("oi24") or 0) >= 10),
        ("SHORT: MA50+ucuz (canli kapi)", "SHORT",
         lambda o: o.get("fiyat_log") is not None and 10 ** o["fiyat_log"] <= 0.07
         and (o.get("ma50_mesafe") or -99) >= 3.72),
        ("SHORT: skor YUKSEK", "SHORT", lambda o: (o.get("score") or 0) >= skor_ust),
        ("SHORT: chg24 YUKSEK (pump)", "SHORT", lambda o: (o.get("chg24") or 0) >= chg_ust),
        ("SHORT: oi24 YUKSEK", "SHORT", lambda o: (o.get("oi24") or 0) >= oi_ust),
        ("KONTROL: tum olaylar LONG", "LONG", lambda o: True),
        ("KONTROL: tum olaylar SHORT", "SHORT", lambda o: True),
    ]

    print("### 1) HAM ILERI GETIRI — hangi ufukta kenar var? (net, maliyet dusulmus)")
    print(f"{'hucre':36}{'N':>6}" + "".join(f"{u}s".rjust(9) for u in UFUKLAR))
    print("-" * 116)
    kayit = {}
    for ad, yon, fn in HUCRE:
        sec = [o for o in ge if fn(o)]
        if len(sec) < 60:
            continue
        sat, ic = f"{ad:36}{len(sec):6d}", {}
        for u in UFUKLAR:
            a = oz([stopsuz_net(o, u, yon) for o in sec])
            ic[u] = a
            sat += f"{a['ort']:+9.2f}" if a else "        -"
        kayit[ad] = (yon, fn, sec, ic)
        print(sat)
    print("-" * 116)
    print("  Sayilar: stopsuz, sabit-sureli cikis, maliyet dusulmus. En iyi ufuk = kenarin omru.")

    print("\n### 2) HAM (en iyi ufuk) vs MEKANIK (A-stop) — YANLIS NEGATIF taramasi")
    print(f"{'hucre':36}{'iyi ufuk':>9}{'HAM net':>9}{'t':>7}"
          f"{'A yari':>8}{'B yari':>8}{'MEKANIK':>9}{'BAYRAK':>22}")
    print("-" * 116)
    bayrakli = []
    for ad, (yon, fn, sec, ic) in kayit.items():
        gecerli = [(u, a) for u, a in ic.items() if a]
        if not gecerli:
            continue
        eu, ea = max(gecerli, key=lambda x: x[1]["ort"])
        A = oz([stopsuz_net(o, eu, yon) for o in sec if o["ts"] < ORTA], 30)
        B = oz([stopsuz_net(o, eu, yon) for o in sec if o["ts"] >= ORTA], 30)
        m = mek(sec, yon, 10.0, 72)
        iki_yari = A is not None and B is not None and A["ort"] > 0 and B["ort"] > 0
        yanlis_neg = (ea["ort"] > 0 and iki_yari and abs(ea["t"]) >= 2
                      and (m is None or m["ort"] <= 0))
        bayrak = "*** YANLIS NEGATIF ADAYI" if yanlis_neg else (
            "ham+ ama yarilar zayif" if ea["ort"] > 0 and not iki_yari else "")
        if yanlis_neg:
            bayrakli.append((ad, yon, sec, eu, ea))
        ay = f"{A['ort']:+8.2f}" if A else "     az "
        by = f"{B['ort']:+8.2f}" if B else "     az "
        print(f"{ad:36}{eu:>8}s{ea['ort']:+9.2f}{ea['t']:+7.2f}{ay}{by}"
              f"{(m['ort'] if m else 0):+9.2f}  {bayrak}")
    print("-" * 116)
    print("  BAYRAK sarti: ham net>0 VE |t|>=2 VE iki yari da + VE mekanik <=0")

    print("\n" + "=" * 116)
    if bayrakli:
        print(f"YANLIS NEGATIF ADAYLARI: {len(bayrakli)} — stop mesafesi taramasi")
        print("=" * 116)
        for ad, yon, sec, eu, ea in bayrakli:
            print(f"\n### {ad}   (yon {yon} · en iyi ufuk {eu}s · ham {ea['ort']:+.2f})")
            print(f"{'stop':16}{'N':>6}{'net %':>9}{'t':>7}{'A yari':>9}{'B yari':>9}")
            for carp in (None, 4.0, 3.0, 2.0):
                v = []
                for o in sec:
                    if carp is None:
                        v.append((o["ts"], stopsuz_net(o, eu, yon)))
                        continue
                    b, gi = o["_b"], o["_gi"] + 1
                    a = yd.atr(b, o["_gi"])
                    if gi + eu >= len(b) or not a:
                        continue
                    ref = b[gi]["o"]
                    stop = ref - carp * a if yon == "LONG" else ref + carp * a
                    vur = None
                    for j in range(gi, gi + eu):
                        if (yon == "LONG" and b[j]["l"] <= stop) or \
                           (yon == "SHORT" and b[j]["h"] >= stop):
                            vur = abs(stop - ref) / ref * 100
                            break
                    if vur is not None:
                        v.append((o["ts"], -vur - MALIYET))
                    else:
                        v.append((o["ts"], stopsuz_net(o, eu, yon)))
                a_ = oz([x[1] for x in v])
                A_ = oz([x[1] for x in v if x[0] < ORTA], 30)
                B_ = oz([x[1] for x in v if x[0] >= ORTA], 30)
                if not a_:
                    continue
                nm = "stop YOK" if carp is None else f"{carp:.0f} x ATR"
                print(f"{nm:16}{a_['n']:6d}{a_['ort']:+9.2f}{a_['t']:+7.2f}"
                      f"{(A_['ort'] if A_ else 0):+9.2f}{(B_['ort'] if B_ else 0):+9.2f}")
    else:
        print("YANLIS NEGATIF ADAYI YOK — arsivde stopun oldurdugu bir kenar bulunamadi.")
        print("=" * 116)


if __name__ == "__main__":
    main()
