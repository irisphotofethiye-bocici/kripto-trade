#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""YÖN AVI (2026-08-10) — "yönü bulmaya çalışalım eldeki veriyle"

NEDEN YENI BIR OLCUM TASARIMI: bu oturumun bulgusu -> yon soylemeyen sinyal degersiz,
cunku stop mesafesi hareketle buyur ve fazladan isabeti yer. Ama stop/hedef mekanigi
YONU DE GIZLIYOR: bir olcu yon tasisa bile, oynakligi artiriyorsa stop yiyip negatif
gorunebilir. Bu yuzden burada STOP YOK, HEDEF YOK — sadece HAM ILERI GETIRI.

IKI GETIRI olculur:
  ham_fwd  : coinin kendi getirisi (+6s / +24s / +72s)
  rel_fwd  : coin getirisi - BTC getirisi (ayni pencere)
             ASIL YON OLCUSU BUDUR: ayi piyasasinda her sey duser; "daha az dusen"
             yon sinyali degildir. Yon = piyasadan AYRISMA.

YONTEM:
  - Her olcu 5 dilime (quintile) bolunur, dilim basina ortalama/medyan getiri.
  - YON GUCU = ust dilim getirisi - alt dilim getirisi (monoton mu?).
  - En guclu olculer ZAMAN IKIYE BOLUNEREK dogrulanir; ayakta kalmayan elenir.
  - Sonra ikili KESISIMLER (es zamanli sinyal) taranir.

VERI: radar_archive (384 sembol) — funding/OI/skor/stage burada var; tek yer.
      Fiyat/hacim olculeri 1h mumlardan eklenir.
"""
import json, os, statistics as st, datetime, itertools, collections

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h")


def yukle():
    ol = json.load(open(os.path.join(BURA, "oruntu_olaylar.json")))
    btc = json.load(open(os.path.join(CACHE, "BTC.json")))
    bidx = {x["t"] // 3600000: i for i, x in enumerate(btc)}
    bc, idxc, ge = {}, {}, []
    for o in ol:
        s = o["sym"]
        if s not in bc:
            p = os.path.join(CACHE, f"{s}.json")
            bc[s] = json.load(open(p)) if os.path.exists(p) else None
            if bc[s]:
                idxc[s] = {x["t"] // 3600000: i for i, x in enumerate(bc[s])}
        b = bc[s]
        if not b:
            continue
        ms = int(datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M").astimezone().timestamp() * 1000)
        sa = ms // 3600000
        i = idxc[s].get(sa)
        bi = bidx.get(sa)
        if i is None or bi is None or i < 200 or i + 72 >= len(b) or bi + 72 >= len(btc):
            continue
        c, px = [x["c"] for x in b], b[i]["c"]
        qv = [x.get("qv", 0.0) for x in b]
        if not px:
            continue
        med24 = st.median(qv[i - 23:i + 1]) or 1e-9
        # DUZELTME 2026-08-10: onceki surumde tbv(BASE) / qv(QUOTE) bolunuyordu ->
        # sonuc ~ taker_orani / fiyat olup FIYAT SEVIYESINE donusuyordu. Ikisi de base:
        tb = sum(x.get("tbv", 0.0) for x in b[i - 23:i + 1])
        v24 = sum(x.get("v", 0.0) for x in b[i - 23:i + 1]) or 1e-9
        hi20 = max(x["h"] for x in b[i - 19:i + 1]); lo20 = min(x["l"] for x in b[i - 19:i + 1])
        ma50 = st.mean(c[i - 49:i + 1]); ma200 = st.mean(c[i - 199:i + 1])
        for ufuk in (6, 24, 72):
            o[f"ham{ufuk}"] = (c[i + ufuk] / px - 1) * 100
            bp = btc[bi]["c"]
            o[f"rel{ufuk}"] = o[f"ham{ufuk}"] - ((btc[bi + ufuk]["c"] / bp - 1) * 100 if bp else 0)
        o["taker_orani"] = tb / v24 if v24 > 1e-9 else None   # DOGRU: 0..1
        o["fiyat_log"] = __import__("math").log10(px) if px > 0 else None  # AYRI olcu
        o["hacim_kat"] = qv[i] / med24
        o["ma50_mesafe"] = (px / ma50 - 1) * 100
        o["ma200_mesafe"] = (px / ma200 - 1) * 100
        o["pos20_h"] = (px - lo20) / (hi20 - lo20) if hi20 > lo20 else 0.5
        ge.append(o)
    return ge


ALAN = [
    ("funding", "funding (isaretli, %/8s)"),
    ("oi24", "acik pozisyon 24s %"),
    ("oi3", "acik pozisyon 3s %"),
    ("comp", "sikisma (TR/ATR)"),
    ("vol_x", "hacim kati (radar)"),
    ("hacim_kat", "hacim kati (1h mum)"),
    ("pos", "range konumu (radar)"),
    ("pos20_h", "range konumu (mum)"),
    ("last1", "son 1 saat %"),
    ("last3", "son 3 saat %"),
    ("chg24", "son 24 saat %"),
    ("score", "radar skoru"),
    ("rel3", "BTC'ye gore 3s"),
    ("btc_chg3", "BTC 3 saat %"),
    ("btc_chg24", "BTC 24 saat %"),
    ("taker_orani", "taker alis orani (DOGRU)"),
    ("fiyat_log", "fiyat seviyesi log10"),
    ("ma50_mesafe", "MA50 mesafesi %"),
    ("ma200_mesafe", "MA200 mesafesi %"),
    ("mcap", "piyasa degeri"),
]


def dilimle(ge, alan, n=5):
    v = sorted(o[alan] for o in ge if o.get(alan) is not None)
    if len(v) < 500:
        return None
    kes = [v[int(len(v) * k / n)] for k in range(1, n)]
    kova = [[] for _ in range(n)]
    for o in ge:
        x = o.get(alan)
        if x is None:
            continue
        k = 0
        while k < n - 1 and x >= kes[k]:
            k += 1
        kova[k].append(o)
    return kova, kes


def main():
    ge = yukle()
    tsl = sorted(o["ts"] for o in ge)
    ORTA = tsl[len(tsl) // 2]
    print("=" * 114)
    print("YÖN AVI — ham ileri getiri (stop/hedef YOK) · radar arşivi · 46 gün, tek rejim")
    print("=" * 114)
    print(f"Olay: {len(ge)}   ·   ASIL OLCU: rel24 = coin 24s getirisi - BTC 24s getirisi\n")
    print(f"  Taban: ham24 medyan {st.median([o['ham24'] for o in ge]):+.2f}%  ·  "
          f"rel24 medyan {st.median([o['rel24'] for o in ge]):+.2f}%")

    print("\n" + "=" * 114)
    print("1) TEK ÖLÇÜ — 5 dilim, üst dilim vs alt dilim (rel24 = BTC'ye göre 24 saat)")
    print("=" * 114)
    print(f"{'olcu':26}{'alt dilim':>11}{'2':>9}{'3':>9}{'4':>9}{'ust dilim':>11}"
          f"{'YON GUCU':>10}{'A yari':>9}{'B yari':>9}")
    print("-" * 114)
    guc = []
    for al, ad in ALAN:
        r = dilimle(ge, al)
        if not r:
            continue
        kova, kes = r
        if any(len(k) < 100 for k in kova):
            continue
        med = [st.median([o["rel24"] for o in k]) for k in kova]
        yg = med[-1] - med[0]
        A = [st.median([o["rel24"] for o in k if o["ts"] < ORTA] or [0]) for k in kova]
        B = [st.median([o["rel24"] for o in k if o["ts"] >= ORTA] or [0]) for k in kova]
        ygA, ygB = A[-1] - A[0], B[-1] - B[0]
        guc.append((abs(yg), al, ad, med, yg, ygA, ygB))
    guc.sort(reverse=True)
    for _, al, ad, med, yg, ygA, ygB in guc:
        kararli = "  OK" if (yg > 0) == (ygA > 0) == (ygB > 0) and min(abs(ygA), abs(ygB)) > abs(yg) * 0.3 else ""
        print(f"{ad:26}" + "".join(f"{m:+9.2f}" for m in med) +
              f"{yg:+10.2f}{ygA:+9.2f}{ygB:+9.2f}{kararli}")
    print("-" * 114)
    print("  YON GUCU = ust dilim medyani - alt dilim medyani (rel24, puan).")
    print("  'OK' = isaret her iki yarida da ayni VE her yarida gucun en az %30'u korunmus.")

    print("\n" + "=" * 114)
    print("2) EN GÜÇLÜ ÖLÇÜLERİN KESİŞİMİ — es zamanli yon sinyali")
    print("=" * 114)
    kararlilar = [(al, ad, yg) for _, al, ad, med, yg, ygA, ygB in guc
                  if (yg > 0) == (ygA > 0) == (ygB > 0) and min(abs(ygA), abs(ygB)) > abs(yg) * 0.3][:6]
    print("  Kararli olculer: " + ", ".join(ad for _, ad, _ in kararlilar))
    esik = {}
    for al, ad, yg in kararlilar:
        v = sorted(o[al] for o in ge if o.get(al) is not None)
        esik[al] = (v[int(len(v) * 0.2)], v[int(len(v) * 0.8)], yg)
    print(f"\n{'kombinasyon':44}{'N':>7}{'rel24 med':>11}{'ham24 med':>11}{'A yari':>9}{'B yari':>9}")
    print("-" * 114)

    def kos(o, al, yon):
        alt, ust, _ = esik[al]
        return (o.get(al) is not None) and (o[al] >= ust if yon > 0 else o[al] <= alt)

    tekli = []
    for al, ad, yg in kararlilar:
        yon = 1 if yg > 0 else -1
        sec = [o for o in ge if kos(o, al, yon)]
        tekli.append((al, ad, yon, sec))
        if len(sec) >= 100:
            A = [o["rel24"] for o in sec if o["ts"] < ORTA]
            B = [o["rel24"] for o in sec if o["ts"] >= ORTA]
            ok = "yuksek" if yon > 0 else "dusuk"
            print(f"{ad+' ('+ok+' %20)':44}{len(sec):7d}"
                  f"{st.median([o['rel24'] for o in sec]):+11.2f}"
                  f"{st.median([o['ham24'] for o in sec]):+11.2f}"
                  f"{(st.median(A) if A else 0):+9.2f}{(st.median(B) if B else 0):+9.2f}")
    print()
    for (a1, ad1, y1, s1), (a2, ad2, y2, s2) in itertools.combinations(tekli, 2):
        sec = [o for o in ge if kos(o, a1, y1) and kos(o, a2, y2)]
        if len(sec) < 60:
            continue
        A = [o["rel24"] for o in sec if o["ts"] < ORTA]
        B = [o["rel24"] for o in sec if o["ts"] >= ORTA]
        ad = f"{ad1.split('(')[0].strip()} + {ad2.split('(')[0].strip()}"
        print(f"{ad:44}{len(sec):7d}"
              f"{st.median([o['rel24'] for o in sec]):+11.2f}"
              f"{st.median([o['ham24'] for o in sec]):+11.2f}"
              f"{(st.median(A) if A else 0):+9.2f}{(st.median(B) if B else 0):+9.2f}")

    print("\n" + "=" * 114)
    print("3) A+B KAPISI aynı ölçüyle (referans — yönü söylediği iddia edilen kapı)")
    print("=" * 114)
    AB = [o for o in ge if (o.get("funding") or 0) <= -0.05 and (o.get("oi24") or 0) >= 10]
    for ad, sec in (("A+B (canlidaki kapi)", AB), ("TUM OLAYLAR", ge)):
        A = [o["rel24"] for o in sec if o["ts"] < ORTA]
        B = [o["rel24"] for o in sec if o["ts"] >= ORTA]
        print(f"  {ad:26} N={len(sec):5d}  rel24 medyan {st.median([o['rel24'] for o in sec]):+.2f}%  "
              f"ham24 medyan {st.median([o['ham24'] for o in sec]):+.2f}%  "
              f"(A {st.median(A):+.2f} / B {st.median(B):+.2f})")


if __name__ == "__main__":
    main()
