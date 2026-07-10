#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERKEN ANALIZ — erken-kusak (erken:true) forward-return cozucusu (2026-07-10).
"Hacim once, fiyat sonra" hipotezinin OLCUMU — kalici/tekrarlanabilir (ilk olcum inline yapilmisti).

Iki hipotez olculur:
  (1) TESPIT-ANI LONG: tespit aninda long girilseydi +4h/+24h ne olurdu?
      (Ilk olcum 2026-07-10, N=82: medyan -3.55%, kazanan %30 -> NEGATIF edge; skor>=40 daha kotu
       AMA +4h medyani +0.67 -> "pop-then-fade" sekli.)
  (2) POP-FADE SHORT: tespit+4h fiyatindan SHORT girilseydi +20h ne olurdu?
      (Pop-then-fade sekli dogruysa bu pozitif cikmali — arsiv_analiz'in yuksek-skor->short-edge
       bulgusuyla ayni yon.)

Deterministik, 0 token, SALT OKUR. Kullanim:
  python erken_analiz.py [--dedup_saat 24]

!!! OVERFIT UYARILARI !!!
  1. N<25-30 = izlenim, KANIT DEGIL. Karar matrisi (test-degerlendirme-programi.md K2) N>=30 ister.
  2. Olcum donemi tek-rejim agirlikliysa sonuc o rejime kosulludur.
  3. Endpoint kiraz-toplama: max-leh/aleh da raporlanir, sadece endpoint'e bakma.
  4. Pencereler ONCEDEN sabit (+4h/+24h, pop-fade +20h) — sonuca gore pencere secmek YASAK.
"""
import json, os, sys, argparse, datetime, time, statistics
import evren

HERE = os.path.dirname(os.path.abspath(__file__))
ARSIV = os.path.join(HERE, "radar_archive.jsonl")
FAPI = "https://fapi.binance.com"

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")


def bagimsiz_olaylar(dedup_saat):
    """erken:true satirlari -> sembol basina dedup_saat penceresinde 1 bagimsiz olay."""
    olaylar, gorulen = [], {}
    for line in open(ARSIV, encoding="utf-8"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("erken") is not True:
            continue
        try:
            ts = datetime.datetime.strptime(d["ts"], "%Y-%m-%d %H:%M")
        except Exception:
            continue
        son = gorulen.get(d["sym"])
        if son is None or (ts - son).total_seconds() >= dedup_saat * 3600:
            olaylar.append(d)
            gorulen[d["sym"]] = ts
    return olaylar


def klines_1h(sym, start_ms):
    try:
        return evren.get(f"{FAPI}/fapi/v1/klines?symbol={sym}USDT&interval=1h&startTime={start_ms}&limit=26",
                         headers={"User-Agent": "erken_analiz/1.0"}, timeout=25)
    except Exception:
        return []


def olay_hesapla(o):
    """Bir olay icin: tespit-ani LONG forward + pop-fade SHORT forward. None = veri yok."""
    dt = datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M").astimezone()
    bars = klines_1h(o["sym"], int(dt.timestamp() * 1000))
    if len(bars) < 25:
        return None
    p0 = float(bars[0][1])  # tespit-ani (ilk bar open)
    p4 = float(bars[4][4])  # +4h kapanis (pop-fade giris referansi)
    p24 = float(bars[24][4])
    if not p0 or not p4:
        return None
    long_r4 = (p4 - p0) / p0 * 100
    long_r24 = (p24 - p0) / p0 * 100
    long_leh = max((float(b[2]) - p0) / p0 * 100 for b in bars[1:25])
    long_aleh = min((float(b[3]) - p0) / p0 * 100 for b in bars[1:25])
    # pop-fade SHORT: giris = +4h kapanisi, yon SHORT, +20h sonra (bars[24]) cikis
    short_r20 = (p4 - p24) / p4 * 100  # dusus = pozitif getiri
    short_leh = max((p4 - float(b[3])) / p4 * 100 for b in bars[5:25])
    short_aleh = min((p4 - float(b[2])) / p4 * 100 for b in bars[5:25])
    return {"sym": o["sym"], "ts": o["ts"], "skor": o.get("score") or 0,
            "long_r4": long_r4, "long_r24": long_r24, "long_leh": long_leh, "long_aleh": long_aleh,
            "short_r20": short_r20, "short_leh": short_leh, "short_aleh": short_aleh}


def ozet(ad, grp, r_alan, leh_alan, aleh_alan, r4_alan=None):
    if not grp:
        print(f"  {ad}: N=0"); return
    r = [g[r_alan] for g in grp]
    poz = sum(1 for x in r if x > 0)
    satir = (f"  {ad}: N={len(grp)} | medyan={statistics.median(r):+.2f}% ort={statistics.mean(r):+.2f}% "
             f"| pozitif={poz}/{len(grp)} (%{poz/len(grp)*100:.0f})")
    if r4_alan:
        satir += f" | +4h medyan={statistics.median([g[r4_alan] for g in grp]):+.2f}%"
    print(satir)
    print(f"  {' '*len(ad)}  max-leh medyan={statistics.median([g[leh_alan] for g in grp]):+.1f}% "
          f"| max-aleh medyan={statistics.median([g[aleh_alan] for g in grp]):+.1f}%")
    if len(grp) < 25:
        print(f"  {' '*len(ad)}  >>> N<25: IZLENIM, kanit degil <<<")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dedup_saat", type=float, default=24.0)
    a = ap.parse_args()

    print("=" * 74)
    print(f"ERKEN ANALIZ — erken-kusak forward-return ({datetime.datetime.now():%Y-%m-%d %H:%M})")
    print("Uyari: N<25-30 = izlenim. Pencereler ON-SABIT (+4h/+24h, pop-fade +20h). Bu arac aksiyon ALMAZ.")
    print("=" * 74)

    olaylar = bagimsiz_olaylar(a.dedup_saat)
    simdi = datetime.datetime.now()
    olgun = [o for o in olaylar
             if (simdi - datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M")).total_seconds() >= 25 * 3600]
    print(f"\nBagimsiz olay ({a.dedup_saat:.0f}h dedup): {len(olaylar)} | forward penceresi dolmus: {len(olgun)}")

    sonuc = []
    for o in olgun:
        fw = olay_hesapla(o)
        if fw:
            sonuc.append(fw)
        time.sleep(0.11)
    print(f"Olculen (veri bulunan): {len(sonuc)}")
    if not sonuc:
        return

    print("\n--- HIPOTEZ 1: TESPIT-ANI LONG (+24h) ---")
    ozet("TUMU      ", sonuc, "long_r24", "long_leh", "long_aleh", r4_alan="long_r4")
    ozet("skor >= 40", [g for g in sonuc if g["skor"] >= 40], "long_r24", "long_leh", "long_aleh", r4_alan="long_r4")
    ozet("skor < 40 ", [g for g in sonuc if g["skor"] < 40], "long_r24", "long_leh", "long_aleh", r4_alan="long_r4")

    print("\n--- HIPOTEZ 2: POP-FADE SHORT (giris=+4h, cikis=+24h; dusus=pozitif) ---")
    ozet("TUMU      ", sonuc, "short_r20", "short_leh", "short_aleh")
    ozet("skor >= 40", [g for g in sonuc if g["skor"] >= 40], "short_r20", "short_leh", "short_aleh")

    s24 = sorted(sonuc, key=lambda g: -g["long_r24"])
    print(f"\nLONG en iyi 5 : {[(g['sym'], round(g['long_r24'],1)) for g in s24[:5]]}")
    print(f"LONG en kotu 5: {[(g['sym'], round(g['long_r24'],1)) for g in s24[-5:]]}")
    print("\nKarar cercevesi: test-degerlendirme-programi.md K2 (LONG medyan negatifse baglanmaz;"
          " skor>=40 medyan>=0 VEYA pop-fade SHORT medyan>=+2%, N>=30 sartiyla).")


if __name__ == "__main__":
    main()
