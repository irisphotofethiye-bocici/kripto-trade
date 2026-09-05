#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FORMASYON — GUC HESABI (2026-09-06)

On-kayittan ONCE. 🔴 ETKIYE BAKMAZ — yalnizca:
   (a) kullanicinin istedigi pencerede kac OLAY var
   (b) gun-kumeli testin MDE'si ne  (etiketin VARYANSINDAN, etkiden DEGIL)
   (c) hucreler oynaklikta ayrisiyor mu (CLAUDE.md'nin zorunlu sinamasi)

Kullanici (2026-09-06): "bunu 2 yillik veriyle degil bizim 22 agustos sonrasi
verimizle test et." Gerekce daha once verilmisti: 2 yillik veri AYI agirlikli,
21 Agustos'tan beri rejim BOGA.

Bu betik o pencerenin GUCUNU olcer ki on-kayit gercekci bir esikle yazilsin.

Salt-okunur.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, math, datetime, statistics as stx, collections

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURASI))
KL_UZUN = os.path.join(KOK, "scratchpad", "klines_1h_uzun")
KL_TAZE = os.path.join(KOK, "scratchpad", "taze_1h")

BAS = "2026-08-22"
UFUK = 24          # saat


def barlar(sym):
    """uzun + taze birlestirilmis saatlik barlar. {saat_kovasi: bar}"""
    out = {}
    for kok in (KL_UZUN, KL_TAZE):
        p = os.path.join(kok, sym + ".json")
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            continue
        for b in d:
            out[int(b["t"]) // 3600000] = b
    return out


def sekil(b):
    """Bir barin sekil olculeri. Standart tanimlar, PARAMETRE TARAMASI YOK."""
    o, h, l, c = float(b["o"]), float(b["h"]), float(b["l"]), float(b["c"])
    aralik = h - l
    if aralik <= 0:
        return None
    govde = abs(c - o)
    ust = h - max(o, c)
    alt = min(o, c) - l
    return {"o": o, "h": h, "l": l, "c": c, "aralik": aralik,
            "govde": govde, "ust": ust, "alt": alt,
            "govde_oran": govde / aralik}


def formasyonlar(onceki, simdi):
    """-> {ad: +1 (boga) | -1 (ayi)}  · standart tanimlar"""
    s = sekil(simdi)
    if not s:
        return {}
    out = {}
    # 1) PIN BAR — fitil asimetrisi (BIRINCIL aday)
    if s["alt"] >= 2 * s["govde"] and s["ust"] <= s["govde"]:
        out["pin"] = +1
    elif s["ust"] >= 2 * s["govde"] and s["alt"] <= s["govde"]:
        out["pin"] = -1
    # 2) DOJI — kararsizlik
    if s["govde_oran"] <= 0.10:
        out["doji"] = 0
    # 3) YUTAN — iki barli donus
    p = sekil(onceki) if onceki else None
    if p:
        if (s["c"] > s["o"] and p["c"] < p["o"]
                and s["o"] <= p["c"] and s["c"] >= p["o"]):
            out["yutan"] = +1
        elif (s["c"] < s["o"] and p["c"] > p["o"]
                and s["o"] >= p["c"] and s["c"] <= p["o"]):
            out["yutan"] = -1
    return out


def main():
    print("=" * 92)
    print("FORMASYON — GUC HESABI (on-kayittan ONCE, ETKIYE BAKMAZ)")
    print("=" * 92)
    print("Pencere: %s -> bugun  (kullanici karari)" % BAS)
    print()

    semboller = sorted(set(
        [f[:-5] for f in os.listdir(KL_UZUN) if f.endswith(".json")]
        + [f[:-5] for f in os.listdir(KL_TAZE) if f.endswith(".json")]))
    bas_kova = int(datetime.datetime.strptime(BAS, "%Y-%m-%d")
                   .replace(tzinfo=datetime.UTC).timestamp()) // 3600

    say = collections.Counter()
    gun_olay = collections.defaultdict(collections.Counter)
    gun_getiri = collections.defaultdict(list)
    atr_ile = collections.defaultdict(list)     # formasyon -> ATR/fiyat listesi
    tum_atr = []
    n_bar = 0
    kapsam = 0

    for sym in semboller:
        b = barlar(sym)
        if not b:
            continue
        ks = sorted(k for k in b if k >= bas_kova)
        if len(ks) < 30:
            continue
        kapsam += 1
        for k in ks:
            if (k - 1) not in b or (k + UFUK) not in b:
                continue
            n_bar += 1
            gun = datetime.datetime.fromtimestamp(k * 3600, datetime.UTC).strftime("%Y-%m-%d")
            p0 = float(b[k]["c"])
            p1 = float(b[k + UFUK]["c"])
            if not p0:
                continue
            ret = (p1 / p0 - 1) * 100
            gun_getiri[gun].append(ret)
            # oynaklik vekili: son 14 barin ortalama TR / fiyat
            pen = [b[j] for j in range(k - 13, k + 1) if j in b]
            if len(pen) >= 10:
                tr = stx.mean([float(x["h"]) - float(x["l"]) for x in pen])
                vol = tr / p0 * 100
                tum_atr.append(vol)
            else:
                vol = None
            f = formasyonlar(b.get(k - 1), b[k])
            for ad, yon in f.items():
                say[(ad, yon)] += 1
                gun_olay[gun][ad] += 1
                if vol is not None:
                    atr_ile[ad].append(vol)

    print("### 1) KAPSAM")
    print("   sembol: %d  ·  olculebilir bar: %d" % (kapsam, n_bar))
    gunler = sorted(gun_getiri)
    print("   gun: %d  (%s .. %s)" % (len(gunler), gunler[0], gunler[-1]))
    print()

    print("### 2) OLAY SAYISI")
    print("   %-16s %10s %12s %12s" % ("formasyon", "N", "bar orani", "gun basina"))
    for (ad, yon), n in sorted(say.items()):
        etiket = "%s %s" % (ad, {1: "BOGA", -1: "AYI", 0: "notr"}[yon])
        print("   %-16s %10d %11.2f%% %12.0f"
              % (etiket, n, n / n_bar * 100, n / len(gunler)))
    print()

    print("### 3) 🔴 GUC — gun-kumeli MDE (etiketin VARYANSINDAN, etkiden DEGIL)")
    gunluk_ort = [stx.mean(v) for g, v in sorted(gun_getiri.items()) if len(v) > 20]
    n_gun = len(gunluk_ort)
    if n_gun >= 3:
        sd = stx.stdev(gunluk_ort)
        se = sd / math.sqrt(n_gun)
        print("   gun kumesi: %d" % n_gun)
        print("   gunluk ortalama getirinin std'si: %.3f puan" % sd)
        print("   tek kolun SE'si: %.3f  ->  MDE (t=2) ~ %.3f puan" % (se, 2 * se))
        print("   IKI kol farki icin SE ~ %.3f  ->  MDE ~ %.3f puan"
              % (se * math.sqrt(2), 2 * se * math.sqrt(2)))
        print()
        print("   KIYAS — bu projede olculmus etki buyuklukleri:")
        print("      A+B kapisi (kabul edilen kenar)          ~ +2,2 puan")
        print("      chg24 >40 LONG (guclu bulundu)           ~ +2,3 puan")
        print("      basis / capraz borsa (DUSTU)             ~ 0,0x puan")
        print("   -> MDE %.2f puan ise, %s"
              % (2 * se * math.sqrt(2),
                 "SADECE cok buyuk etkiler gorulur; kucuk-orta etki 'goremiyoruz' cikar"
                 if 2 * se * math.sqrt(2) > 1.0 else "orta etkiler de gorulebilir"))
    print()

    print("### 4) 🔴 ZORUNLU SINAMA — hucreler OYNAKLIKTA ayrisiyor mu?")
    print("   (CLAUDE.md: chg24 bandi bu tuzaga dustu, stop genisligi 3,3 kat degisiyordu)")
    if tum_atr:
        taban = stx.median(tum_atr)
        print("   %-16s %10s %14s %10s" % ("formasyon", "N", "oynaklik med", "taban kati"))
        print("   %-16s %10d %13.2f%% %10s" % ("TUM BARLAR", len(tum_atr), taban, "1,00"))
        for ad, v in sorted(atr_ile.items()):
            if len(v) < 30:
                continue
            m = stx.median(v)
            print("   %-16s %10d %13.2f%% %9.2fx" % (ad, len(v), m, m / taban))
        print("   -> 1,3 kattan sapan varsa HAM getiri zorunlu, mekanikli olcum yaniltir")
    print()

    print("### 5) GUN BASINA OLAY DAGILIMI (yogunlasma kontrolu)")
    for ad in sorted(set(a for a, _ in say)):
        v = [gun_olay[g].get(ad, 0) for g in gunler]
        if sum(v) == 0:
            continue
        print("   %-10s min %4d · medyan %4d · maks %4d  (en yogun gun toplamin %%%.0f'i)"
              % (ad, min(v), int(stx.median(v)), max(v), max(v) / sum(v) * 100))
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
