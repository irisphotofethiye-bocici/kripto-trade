#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOYUTLANDIRMA AGIRLIGI (2026-08-11) — olctugum sey botun yaptigi sey mi?

CANLI ILK PARTIDA GORULEN: stop mesafeleri %0.42 ile %5.44 arasinda degisti.
Olcum her olayi ESIT AGIRLIKLA topluyordu ("olay basi net %"). Bot ise
RISK-ONCE boyutlandiriyor: notional = hedef_risk / stop_frac, yani
DAR STOP -> BUYUK POZISYON. Bu ikisi AYNI PORTFOY DEGIL.

Ustelik kaldirac tavani (kaldirac_max=10, marjin ~%10) yuzunden dar stoplarda
hedef riske ULASILAMIYOR -> pozisyon kirpiliyor. Yani canli, esit-risk ile
esit-notional arasinda bir MELEZ.

BU SCRIPT ucunu yan yana olcer:
  A) ESIT NOTIONAL  = benim yaptigim olcum ("olay basi net %")
  B) ESIT RISK      = saf risk-once (notional = risk/stop), tavansiz
  C) CANLI MELEZ    = notional = min(risk/stop, marjin*kaldirac_max)  <- botun gercegi
Cikti: olay basina SERMAYENIN yuzde kaci. Isaret degisiyorsa olcum canliyi temsil etmiyor.
"""
import json, os, sys, statistics as stx, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yon_dogrula as yd
import yon_avi

PUMP = 20.0
RISK_PCT = 0.03          # islem_risk_pct = 3
MARJIN_PCT = 0.10        # marjin_pct_hesapla ortasi (%8-12)
KALD_MAX = 10


def gecer_ab(o):
    return (o.get("funding") or 0) <= -0.05 and (o.get("oi24") or 0) >= 10


def gecer_ma50(o):
    px = 10 ** o["fiyat_log"] if o.get("fiyat_log") is not None else None
    return px is not None and px <= 0.07 and (o.get("ma50_mesafe") or -99) >= 3.72


def pump_ok(o):
    return (o.get("chg24") or 0) < PUMP


def yukle_barlar(ge):
    bc, idxc = {}, {}
    for o in ge:
        s = o["sym"]
        if s not in bc:
            p = os.path.join(yd.CACHE, f"{s}.json")
            bc[s] = json.load(open(p)) if os.path.exists(p) else None
            if bc[s]:
                idxc[s] = {x["t"] // 3600000: i for i, x in enumerate(bc[s])}
        if not bc[s]:
            continue
        ms = int(datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M").astimezone().timestamp() * 1000)
        o["_b"], o["_gi"] = bc[s], idxc[s].get(ms // 3600000)
    return ge


def agirliklar(s_frac):
    """olay basina notional / equity"""
    esit_n = 1.0
    esit_r = RISK_PCT / s_frac
    tavan = MARJIN_PCT * KALD_MAX
    canli = min(esit_r, tavan)
    return esit_n, esit_r, canli


def main():
    ge = yukle_barlar(yon_avi.yukle())
    tsl = sorted(o["ts"] for o in ge)
    ORTA = tsl[len(tsl) // 2]

    KUME = [
        ("A+B", lambda o: gecer_ab(o) and pump_ok(o)),
        ("MA50+ucuz", lambda o: gecer_ma50(o) and pump_ok(o)),
        ("BIRLESIM (canlidaki bot)", lambda o: (gecer_ab(o) or gecer_ma50(o)) and pump_ok(o)),
        ("KONTROL: tum olaylar SHORT", lambda o: True),
    ]
    print("=" * 110)
    print("AYNI KAPI, UC FARKLI BOYUTLANDIRMA — olay basina SERMAYENIN yuzdesi (hedef %10 / 72s)")
    print("=" * 110)
    print(f"{'kume':28}{'N':>6}{'A esit-not':>12}{'B esit-risk':>13}"
          f"{'C CANLI':>10}{'C: A yari':>11}{'C: B yari':>11}{'C toplam':>11}")
    print("-" * 110)
    detay = {}
    for ad, fn in KUME:
        sec = [o for o in ge if o.get("_gi") is not None and fn(o)]
        kay = []
        for o in sec:
            r = yd.islem(o["_b"], o["_gi"] + 1, 10.0, 72, "SHORT")
            if not r:
                continue
            g, tip, sp = r
            wn, wr, wc = agirliklar(sp / 100.0)
            kay.append((o["ts"], g, tip, sp, g * wn, g * wr, g * wc))
        if len(kay) < 60:
            continue
        cA = [x[6] for x in kay if x[0] < ORTA]
        cB = [x[6] for x in kay if x[0] >= ORTA]
        print(f"{ad:28}{len(kay):6d}{stx.mean([x[4] for x in kay]):+12.2f}"
              f"{stx.mean([x[5] for x in kay]):+13.2f}{stx.mean([x[6] for x in kay]):+10.2f}"
              f"{(stx.mean(cA) if cA else 0):+11.2f}{(stx.mean(cB) if cB else 0):+11.2f}"
              f"{sum(x[6] for x in kay):+11.0f}")
        detay[ad] = kay
    print("-" * 110)
    print("  A = her olayda ayni notional (benim onceki olcumum)")
    print("  B = saf risk-once: notional = %3 risk / stop  (tavan yok)")
    print("  C = CANLI: B ama notional <= marjin*kaldirac_max = sermayenin 1.0 kati")

    kay = detay["BIRLESIM (canlidaki bot)"]
    print("\n" + "=" * 110)
    print("STOP GENISLIGINE GORE AYRISTIRMA — canli agirlikla, hangi dilim kazandiriyor?")
    print("=" * 110)
    sps = sorted(x[3] for x in kay)
    kes = [sps[len(sps) * k // 4] for k in (1, 2, 3)]
    ad_dilim = [f"stop < %{kes[0]:.2f}", f"%{kes[0]:.2f}-{kes[1]:.2f}",
                f"%{kes[1]:.2f}-{kes[2]:.2f}", f"stop > %{kes[2]:.2f}"]
    print(f"{'stop dilimi':22}{'N':>6}{'isabet':>9}{'esit-not %':>12}"
          f"{'CANLI %':>10}{'ort boyut':>11}{'CANLI toplam':>14}")
    print("-" * 110)
    for k in range(4):
        alt = kes[k - 1] if k > 0 else -1
        ust = kes[k] if k < 3 else 1e9
        d = [x for x in kay if alt < x[3] <= ust]
        if not d:
            continue
        boy = [min(RISK_PCT / (x[3] / 100), MARJIN_PCT * KALD_MAX) for x in d]
        print(f"{ad_dilim[k]:22}{len(d):6d}"
              f"{sum(1 for x in d if x[2]=='HEDEF')/len(d)*100:8.1f}%"
              f"{stx.mean([x[4] for x in d]):+12.2f}{stx.mean([x[6] for x in d]):+10.2f}"
              f"{stx.mean(boy):11.2f}{sum(x[6] for x in d):+14.0f}")
    print("-" * 110)
    print("  'ort boyut' = notional / sermaye. 1.00 = kaldirac tavanina dayanmis (kirpilmis).")

    print("\n" + "=" * 110)
    print("ASGARI STOP TABANI DENEMESI — cok dar stoplu olaylari ELEMEK ise yarar mi?")
    print("=" * 110)
    print(f"{'taban':14}{'N':>6}{'elenen':>9}{'CANLI %':>10}{'A yari':>10}{'B yari':>10}{'toplam':>11}")
    print("-" * 110)
    for taban in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        d = [x for x in kay if x[3] >= taban]
        if len(d) < 60:
            continue
        A = [x[6] for x in d if x[0] < ORTA]
        B = [x[6] for x in d if x[0] >= ORTA]
        print(f"stop >= %{taban:<5.1f}{len(d):6d}{len(kay)-len(d):9d}"
              f"{stx.mean([x[6] for x in d]):+10.2f}"
              f"{(stx.mean(A) if A else 0):+10.2f}{(stx.mean(B) if B else 0):+10.2f}"
              f"{sum(x[6] for x in d):+11.0f}")


if __name__ == "__main__":
    main()
