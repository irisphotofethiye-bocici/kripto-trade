#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HAM SINYAL TESTI (2026-08-11) — "sonuc bizim sistemimizden mi, sinyalden mi?"

KULLANICI SORUSU: sonuc olumsuz, ama BIZIM SISTEME gore. Hakli soru:
  onceki olcumlerde su bizim seceneklerimizdi -> A-stop · ust-bant hedefi ·
  maliyet %0.13 · 1 saatlik · sonraki bar acilisi. Sinyalin kendisi bunlardan
  bagimsiz olarak bilgi tasiyor mu?

BU OLCUM MEKANIKTEN ARINIK:
  STOP YOK · HEDEF YOK · MALIYET YOK · ZAMAN STOPU YOK.
  Yalniz: sinyalden sonra fiyat ne yapti?
  (Projede ayni desen `yon_avi.py`'de kullanildi — kasitli olarak ayni.)

UC OLCU:
  ham      : coinin kendi getirisi (+1/+4/+12/+24 bar)
  rel      : coin getirisi - BTC getirisi  <- ASIL YON OLCUSU
             (yatay piyasada her sey birlikte hareket eder; yon = AYRISMA)
  MFE/MAE  : sinyalden sonra gorulen EN IYI ve EN KOTU nokta
             -> "mukemmel cikis" senaryosu. Scalp icin kritik: fiyat bir ara
                %1 yukari gitse bile, once %2 asagi gittiyse scalp yasamaz.

KONTROL: ayni sembol/donemde rastgele barlar, ayni olculer.
KARAR:
  ham/rel kontrolden ANLAMLI iyiyse -> sinyalde bilgi VAR, sorun BIZIM mekanikte
  ham/rel kontrolle ayniysa         -> sinyalde bilgi YOK, mekanigin sucu degil
"""
import json, os, random, statistics as stx, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kanal_stoch as ks

UFUKLAR = (1, 4, 12, 24)
random.seed(29)


def olc(b, i, btc, bi, ufuk):
    """stop/hedef/maliyet YOK. Doner: ham%, rel%, MFE%, MAE%"""
    if i + ufuk >= len(b) or bi is None or bi + ufuk >= len(btc):
        return None
    ref = b[i]["c"]
    if ref <= 0:
        return None
    ham = (b[i + ufuk]["c"] / ref - 1) * 100
    bp = btc[bi]["c"]
    brel = (btc[bi + ufuk]["c"] / bp - 1) * 100 if bp else 0.0
    dilim = b[i + 1:i + ufuk + 1]
    mfe = (max(x["h"] for x in dilim) / ref - 1) * 100
    mae = (min(x["l"] for x in dilim) / ref - 1) * 100
    return ham, ham - brel, mfe, mae


def oz(v, k):
    g = [x[k] for x in v if x]
    if len(g) < 40:
        return None
    sh = stx.pstdev(g) / len(g) ** 0.5
    return {"n": len(g), "ort": stx.mean(g), "med": stx.median(g), "sh": sh,
            "t": stx.mean(g) / sh if sh else 0}


def main():
    btc = json.load(open(os.path.join(ks.CACHE, "BTC.json"), encoding="utf-8"))
    bidx = {x["t"] // 3600000: i for i, x in enumerate(btc)}
    sinyal, kontrol = [], []
    for f in sorted(os.listdir(ks.CACHE)):
        if not f.endswith(".json") or f == "BTC.json":
            continue
        try:
            b = json.load(open(os.path.join(ks.CACHE, f), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ks.ISINMA + 60:
            continue
        c = [x["c"] for x in b]
        _, aa = ks.acc_bands(b)
        K, D = ks.stochrsi(ks.wilder_rsi(c))
        son = -10 ** 9
        for i in range(ks.ISINMA, len(b) - max(UFUKLAR) - 2):
            if None in (K[i], D[i], K[i - 1], D[i - 1], aa[i]):
                continue
            if not (K[i - 1] < ks.ASIRI_SATIM and K[i - 1] <= D[i - 1] and K[i] > D[i]):
                continue
            if b[i]["l"] > aa[i] or i - son < ks.SEYRELT:
                continue
            son = i
            sinyal.append((b, i, bidx.get(b[i]["t"] // 3600000)))
        for _ in range(max(2, (len(b) - ks.ISINMA) // 150)):
            i = random.randint(ks.ISINMA, len(b) - max(UFUKLAR) - 3)
            kontrol.append((b, i, bidx.get(b[i]["t"] // 3600000)))

    print("=" * 104)
    print("HAM SINYAL — STOP YOK · HEDEF YOK · MALIYET YOK  (mekanikten arinik)")
    print("=" * 104)
    print(f"Sinyal: {len(sinyal)}  ·  kontrol: {len(kontrol)}\n")

    for ad, k in (("ham getiri (coinin kendisi)", 1), ("REL getiri (coin - BTC)", 2)):
        print(f"### {ad}")
        print(f"{'ufuk':>8}{'sinyal ort':>13}{'medyan':>10}{'t':>8}"
              f"{'KONTROL ort':>14}{'medyan':>10}{'FARK':>9}{'fark t':>9}")
        print("-" * 104)
        for uf in UFUKLAR:
            sv = [olc(b, i, btc, bi, uf) for b, i, bi in sinyal]
            kv = [olc(b, i, btc, bi, uf) for b, i, bi in kontrol]
            a, kk = oz(sv, k - 1 + 1 if False else k - 1), oz(kv, k - 1)
            if not a or not kk:
                continue
            fark = a["ort"] - kk["ort"]
            fsh = (a["sh"] ** 2 + kk["sh"] ** 2) ** 0.5
            print(f"{uf:>6} bar{a['ort']:+13.3f}{a['med']:+10.3f}{a['t']:+8.2f}"
                  f"{kk['ort']:+14.3f}{kk['med']:+10.3f}{fark:+9.3f}{fark/fsh:+9.2f}")
        print()

    print("### MFE / MAE — 'mukemmel cikis' ve 'en kotu an'")
    print(f"{'ufuk':>8}{'S: MFE':>10}{'S: MAE':>10}{'S: oran':>10}"
          f"{'K: MFE':>10}{'K: MAE':>10}{'K: oran':>10}")
    print("-" * 104)
    for uf in UFUKLAR:
        sv = [x for x in (olc(b, i, btc, bi, uf) for b, i, bi in sinyal) if x]
        kv = [x for x in (olc(b, i, btc, bi, uf) for b, i, bi in kontrol) if x]
        if len(sv) < 40 or len(kv) < 40:
            continue
        sm, sa = stx.median([x[2] for x in sv]), stx.median([x[3] for x in sv])
        km, ka = stx.median([x[2] for x in kv]), stx.median([x[3] for x in kv])
        print(f"{uf:>6} bar{sm:+10.2f}{sa:+10.2f}{abs(sm/sa) if sa else 0:>10.2f}"
              f"{km:+10.2f}{ka:+10.2f}{abs(km/ka) if ka else 0:>10.2f}")
    print("-" * 104)
    print("  MFE = en iyi nokta · MAE = en kotu nokta (medyan) · oran = MFE/|MAE|")
    print("  oran > 1 ise yukari alan asagi alandan buyuk; scalp icin gerekli sart.")

    print("\n" + "=" * 104)
    print("KARAR")
    print("=" * 104)
    sv = [olc(b, i, btc, bi, 4) for b, i, bi in sinyal]
    kv = [olc(b, i, btc, bi, 4) for b, i, bi in kontrol]
    a, kk = oz(sv, 1), oz(kv, 1)
    fark = a["ort"] - kk["ort"]
    fsh = (a["sh"] ** 2 + kk["sh"] ** 2) ** 0.5
    print(f"  4 bar REL getiri:  sinyal {a['ort']:+.3f}%  ·  kontrol {kk['ort']:+.3f}%  "
          f"·  fark {fark:+.3f}  (t={fark/fsh:+.2f})")
    if abs(fark / fsh) < 2:
        print("  -> Sinyal, rastgele bardan AYIRT EDILEMIYOR (|t| < 2).")
        print("     Yani olumsuz sonuc BIZIM MEKANIGIMIZDEN DEGIL: sinyalin kendisinde")
        print("     yon bilgisi yok. Stop/hedef/maliyet degistirmek bunu duzeltmez.")
    else:
        print("  -> Sinyal kontrolden ANLAMLI farkli. Sorun mekanikte olabilir;")
        print("     stop/hedef tasarimi yeniden dusunulmeli.")


if __name__ == "__main__":
    main()
