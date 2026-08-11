#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SISTEM DENETIMI — olcum tarafi bulgularinin SAYISALLASTIRILMASI (2026-08-11)

Bulgu 2: maliyet sabiti %0.09 (betikler) vs %0.13 (canli gercek)
Bulgu 3: sembol kumelenmesi hicbir ana olcumde raporlanmiyor
Bulgu 4: canli gostergeler KAPANMAMIS mumu iceriyor (vol_x carpitmasi)
Bulgu 7: A+B kapisi MA50+ucuz kapisini golgeliyor (erken return)

Salt-okunur. Bota/config'e/deftere yazmaz.
"""
import json, os, sys, statistics as stx, collections, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yon_avi
import yon_dogrula as yd

PUMP = 20.0


def ab(o):
    return (o.get("funding") or 0) <= -0.05 and (o.get("oi24") or 0) >= 10


def ma50(o):
    px = 10 ** o["fiyat_log"] if o.get("fiyat_log") is not None else None
    return px is not None and px <= 0.07 and (o.get("ma50_mesafe") or -99) >= 3.72


def pump_ok(o):
    return (o.get("chg24") or 0) < PUMP


def main():
    ge = yon_avi.yukle()
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
    ge = [o for o in ge if o.get("_gi") is not None]

    KUME = [("A+B (+pump)", lambda o: ab(o) and pump_ok(o)),
            ("MA50+ucuz (+pump)", lambda o: ma50(o) and pump_ok(o)),
            ("BIRLESIM (canli bot)", lambda o: (ab(o) or ma50(o)) and pump_ok(o))]

    # ---------------------------------------------------------------- Bulgu 2
    print("=" * 100)
    print("BULGU 2 — MALIYET: betikler %0.09, canli gercek %0.13")
    print("=" * 100)
    print("  canli: taker %0.045 x2 (giris+cikis) + kayma %0.02 x2 = %0.13")
    print(f"\n{'kume':26}{'N':>6}{'%0.09 ile':>12}{'%0.13 ile':>12}{'FARK':>9}{'toplam kayip':>15}")
    print("-" * 100)
    for ad, fn in KUME:
        sec = [o for o in ge if fn(o)]
        r = [yd.islem(o["_b"], o["_gi"] + 1, 10.0, 72, "SHORT") for o in sec]
        r = [x for x in r if x]
        if len(r) < 60:
            continue
        eski = stx.mean([x[0] for x in r])                 # yd.MALIYET = 0.09
        yeni = eski - 0.04                                  # +0.04 puan daha maliyet
        print(f"{ad:26}{len(r):6d}{eski:+12.2f}{yeni:+12.2f}{-0.04:+9.2f}"
              f"{-0.04*len(r):+15.1f}")
    print("-" * 100)
    print("  NOT: %0.04 sabit kaydirma — her islemde ayni. Isaret degistirmiyor ama")
    print("  BIRLESIM icin islem basi kenar %3.7 kuculur. gainer_* betikleri 0.04R")
    print("  varsayiyordu; stop %0.5 iken gercek maliyet 0.26R -> orada hata 6.5 KAT.")

    # ---------------------------------------------------------------- Bulgu 3
    print("\n" + "=" * 100)
    print("BULGU 3 — SEMBOL KUMELENMESI (hicbir ana olcumde raporlanmiyordu)")
    print("=" * 100)
    print(f"{'kume':26}{'N olay':>8}{'ayri sembol':>13}{'olay/sembol':>13}"
          f"{'en sik 5in payi':>17}")
    print("-" * 100)
    for ad, fn in KUME:
        sec = [o for o in ge if fn(o)]
        if len(sec) < 60:
            continue
        c = collections.Counter(o["sym"] for o in sec)
        ilk5 = sum(n for _, n in c.most_common(5))
        print(f"{ad:26}{len(sec):8d}{len(c):13d}{len(sec)/len(c):13.1f}"
              f"{ilk5/len(sec)*100:16.0f}%")
        print(f"{'':26}en sik: " + ", ".join(f"{s}({n})" for s, n in c.most_common(6)))
    print("-" * 100)
    print("  Efektif bagimsiz birim ~ ayri sembol sayisi. t-degeri N ile degil")
    print("  sembol sayisiyla olceklenmeli; aksi halde SISER.")

    # ---------------------------------------------------------------- Bulgu 7
    print("\n" + "=" * 100)
    print("BULGU 7 — A+B kapisi MA50+ucuz kapisini GOLGELIYOR (erken return)")
    print("=" * 100)
    sadece_ab = [o for o in ge if ab(o) and not ma50(o) and pump_ok(o)]
    sadece_ma = [o for o in ge if ma50(o) and not ab(o) and pump_ok(o)]
    ikisi = [o for o in ge if ab(o) and ma50(o) and pump_ok(o)]
    top = len(sadece_ab) + len(sadece_ma) + len(ikisi)
    print(f"  yalniz A+B          : {len(sadece_ab):5d}")
    print(f"  yalniz MA50+ucuz    : {len(sadece_ma):5d}")
    print(f"  IKISI BIRDEN        : {len(ikisi):5d}  <- canlida HEPSI 'A+B' etiketli yazilir")
    print(f"  toplam              : {top:5d}")
    print(f"\n  MA50 kapisinin gercek katkisi {len(sadece_ma) + len(ikisi)} olay,")
    print(f"  ama karnede yalniz {len(sadece_ma)} gorunur -> "
          f"%{len(ikisi)/max(len(sadece_ma)+len(ikisi),1)*100:.0f} eksik sayiliyor.")

    # ---------------------------------------------------------------- Bulgu 4
    print("\n" + "=" * 100)
    print("BULGU 4 — KAPANMAMIS MUM: vol_x turun hangi dakikada kostuguna bagli")
    print("=" * 100)
    print("  radar.vol_x = son barin quote hacmi / son 24 barin medyani")
    print("  Son bar HENUZ KAPANMADIYSA hacmi orantili eksiktir:")
    print("  dakika m'de gozlenen vol_x ~ (m/60) x gercek vol_x\n")
    ornek, dosyalar = [], sorted(f for f in os.listdir(yd.CACHE) if f.endswith(".json"))[:120]
    for f in dosyalar:
        try:
            b = json.load(open(os.path.join(yd.CACHE, f), encoding="utf-8"))
        except Exception:
            continue
        qv = [x.get("qv", 0.0) for x in b]
        for i in range(200, len(b) - 1, 37):
            med = stx.median(qv[i - 23:i + 1])
            if med > 0:
                ornek.append(qv[i] / med)
    ornek.sort()
    print(f"  Gercek (kapanmis bar) vol_x dagilimi, N={len(ornek)}:")
    for p in (0.5, 0.75, 0.9, 0.95, 0.99):
        print(f"    %{p*100:.0f} dilim: {ornek[int(len(ornek)*p)]:.2f}")
    print(f"\n  vol_x >= 2.0 esigini gecen olay orani, tur DAKIKASINA gore:")
    print(f"    {'dakika':>8}{'gecen %':>10}{'kayip':>10}")
    tam = sum(1 for x in ornek if x >= 2.0) / len(ornek) * 100
    for m in (5, 15, 30, 45, 59):
        gecen = sum(1 for x in ornek if x * (m / 60.0) >= 2.0) / len(ornek) * 100
        print(f"    {m:>8}{gecen:9.1f}%{gecen-tam:+10.1f}")
    print(f"    {'kapanmis':>8}{tam:9.1f}%{0:+10.1f}   <- backtestlerin gordugu")
    print("\n  Yani ayni coin, saat 05'te elenip 55'te gecebilir. Radar skoru ve")
    print("  golge LONG tezinin vol_x>=2 sarti bundan dogrudan etkilenir.")


if __name__ == "__main__":
    main()
