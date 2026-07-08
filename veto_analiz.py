#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VETO ANALIZ — veto_log.jsonl forward-return cozucusu (2026-07-08).
testbot'un reddettigi adaylar (long_veto / taker_soguma / blowoff) gercekten zarardan mi
KORUDU yoksa firsat mi KACIRDI (opportunity cost) sorusunu OLCUMLE yanitlar.

Ne yapar (arsiv_analiz.py forward-return deseni; SALT OKUR, aksiyon almaz):
  - Her veto olayi icin veto ANINDAN itibaren Binance 1h kline cek
  - "olurdu_yon" yonunde +4h/+24h: endpoint getiri + max-lehte + max-aleyhte (yol-bagimli)
  - Stop-proxy (--stop_pct, varsayilan 8%) yolu simule: aleyhte once mi stop'u vururdu?
    -> KORUDU (stop vururdu / horizon'da zarar) vs FIRSAT_KACTI (lehte kosardi)
  - Kategori bazinda topla

Deterministik, 0 token, anahtarsiz. Kullanim:
  python veto_analiz.py [--stop_pct 8] [--dedup_saat 12]

!!! OVERFITTING UYARILARI (cikti basinda da tekrarlanir) !!!
  1. OLCMEK != OVERFIT. Riski, az ornege gore esik degistirmekte. N<25-30 = izlenim, KANIT DEGIL.
  2. 1 hafta = TEK rejim. Boga-haftasinda "firsat baltaladi" gorunen filtre, ayida seni kurtaran olabilir.
  3. Endpoint kiraz-toplama: +24h'te +%20 biten bir LONG once -%12 dusup stop'u vurmus olabilir -> veto yine korudu.
     (Bu yuzden max-aleyhte + stop-sim raporlanir, sadece endpoint degil.)
  4. Stop-proxy sabit (%8); testbot'un gercek ATR-stop'u degisken -> siniflama YAKLASIKTIR, mutlak degil.
"""
import json, os, sys, argparse, datetime, time, statistics
import evren

HERE = os.path.dirname(os.path.abspath(__file__))
FAPI = "https://fapi.binance.com"
VETO_LOGF = os.path.join(HERE, "veto_log.jsonl")
KATEGORILER = ("long_veto", "taker_soguma", "blowoff")

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")


def ts_to_ms(ts):
    """veto_log ts YEREL saat ('%Y-%m-%d %H:%M:%S') -> UTC epoch ms (arsiv_analiz timezone dersi)."""
    dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").astimezone()
    return int(dt.timestamp() * 1000)


def klines_1h(sym, start_ms):
    try:
        d = evren.get(f"{FAPI}/fapi/v1/klines?symbol={sym}USDT&interval=1h&startTime={start_ms}&limit=48",
                      headers={"User-Agent": "veto_analiz/1.0"}, timeout=25)
    except Exception:
        return []
    return [{"t": int(k[0]), "o": float(k[1]), "h": float(k[2]), "l": float(k[3]), "c": float(k[4])} for k in d]


def olay_forward(olay, stop_pct):
    """Bir veto olayi icin forward-return + yol-bagimli stop-sim. Donus: dict veya None (veri yok)."""
    sym, yon = olay.get("sym"), olay.get("olurdu_yon")
    price0 = olay.get("price")
    ts = olay.get("ts")
    if not (sym and yon and ts):
        return None
    start_ms = ts_to_ms(ts)
    bars = klines_1h(sym, start_ms)
    if len(bars) < 4:
        return None
    if not price0:
        price0 = bars[0]["o"]
    isaret = 1 if yon == "LONG" else -1  # LONG: yukari=kar; SHORT: asagi=kar

    def yon_getiri(px):
        return (px - price0) / price0 * 100 * isaret

    # +4h / +24h endpoint (bar indeksi ~ saat)
    endp = {}
    for ufuk in (4, 24):
        if len(bars) > ufuk:
            endp[ufuk] = round(yon_getiri(bars[ufuk]["c"]), 2)
        else:
            endp[ufuk] = None

    # yol-bagimli: ilk 24 barda max-lehte, max-aleyhte + stop-proxy hangisi ONCE vurdu
    max_leh, max_aleh = 0.0, 0.0
    stop_vurdu, hedef_vurdu = False, False
    for b in bars[1:25]:
        # aleyhte en kotu (LONG icin low, SHORT icin high)
        aleh = yon_getiri(b["l"]) if yon == "LONG" else yon_getiri(b["h"])
        leh = yon_getiri(b["h"]) if yon == "LONG" else yon_getiri(b["l"])
        max_aleh = min(max_aleh, aleh)
        max_leh = max(max_leh, leh)
        if not stop_vurdu and not hedef_vurdu:
            if aleh <= -stop_pct:
                stop_vurdu = True
            elif leh >= stop_pct:  # simetrik hedef proxy (1R)
                hedef_vurdu = True

    # siniflama: stop once vurduysa VEYA 24h endpoint zararsa -> veto KORUDU; hedef once/lehte kosti -> FIRSAT_KACTI
    e24 = endp.get(24)
    if stop_vurdu:
        sinif = "KORUDU"
    elif hedef_vurdu:
        sinif = "FIRSAT_KACTI"
    elif e24 is not None and e24 < 0:
        sinif = "KORUDU"
    elif e24 is not None and e24 > 0:
        sinif = "FIRSAT_KACTI"
    else:
        sinif = "NOTR"
    return {"endp": endp, "max_leh": round(max_leh, 2), "max_aleh": round(max_aleh, 2),
            "stop_vurdu": stop_vurdu, "hedef_vurdu": hedef_vurdu, "sinif": sinif}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stop_pct", type=float, default=8.0, help="stop-proxy mesafesi (yaklasik; testbot ATR-stop degisken)")
    a = ap.parse_args()

    print("=" * 70)
    print("VETO ANALIZ — testbot reddettigi adaylar: KORUMA mi FIRSAT-MALIYETI mi?")
    print("!!! OVERFITTING UYARILARI (once BUNU oku, sonra tabloyu) !!!")
    print("  1. Olcmek != overfit; riski az ornege gore esik degistirmekte. N<25-30 = izlenim, KANIT DEGIL.")
    print("  2. 1 hafta = tek rejim. Boga'da 'firsat baltaladi' filtre, ayida kurtarici olabilir.")
    print("  3. Endpoint kiraz-toplama: +24h kar biten once stop'u vurmus olabilir -> max-aleyhte + stop-sim'e bak.")
    print(f"  4. Stop-proxy sabit (%{a.stop_pct:.0f}); gercek ATR-stop degisken -> siniflama YAKLASIK.")
    print("=" * 70)

    try:
        olaylar = [json.loads(l) for l in open(VETO_LOGF, encoding="utf-8").read().splitlines() if l.strip()]
    except FileNotFoundError:
        print("veto_log.jsonl henuz yok (testbot bir veto loglamamis). Olcum baslamak icin --cycle bekle.")
        return
    if not olaylar:
        print("veto_log.jsonl bos.")
        return

    print(f"\nToplam veto olayi: {len(olaylar)}")
    kat_sayim = {k: 0 for k in KATEGORILER}
    for o in olaylar:
        kat_sayim[o.get("kategori")] = kat_sayim.get(o.get("kategori"), 0) + 1
    print("Kategori dagilimi:", ", ".join(f"{k}={v}" for k, v in kat_sayim.items()))

    # her kategori icin forward-return topla
    for kat in KATEGORILER:
        alt = [o for o in olaylar if o.get("kategori") == kat]
        if not alt:
            continue
        print(f"\n--- {kat.upper()} (N={len(alt)}) ---")
        korudu, firsat, notr, veri_yok = 0, 0, 0, 0
        e24_list = []
        for o in alt:
            fw = olay_forward(o, a.stop_pct)
            if fw is None:
                veri_yok += 1
                continue
            if fw["sinif"] == "KORUDU":
                korudu += 1
            elif fw["sinif"] == "FIRSAT_KACTI":
                firsat += 1
            else:
                notr += 1
            if fw["endp"].get(24) is not None:
                e24_list.append(fw["endp"][24])
            time.sleep(0.1)  # rate-limit dostu
        deger = len(alt) - veri_yok
        print(f"  KORUDU (zarardan kacindi): {korudu}/{deger}")
        print(f"  FIRSAT_KACTI (opportunity cost): {firsat}/{deger}")
        print(f"  NOTR/belirsiz: {notr}/{deger} | veri-yok: {veri_yok}")
        if e24_list:
            med = statistics.median(e24_list)
            print(f"  +24h yon-getiri medyani (olurdu_yon'da): {med:+.1f}%  "
                  f"[{'FILTRE HAKLI (medyan negatif)' if med < 0 else 'FILTRE FIRSAT KACIRMIS OLABILIR (medyan pozitif)'}]")
        if deger < 25:
            print(f"  >>> N={deger} < 25: bu SADECE IZLENIM, karar icin YETERSIZ. Esik DEGISTIRME. <<<")

    print("\nNOT: Bu arac aksiyon ALMAZ. Filtre degisikligi icin 25-30 BAGIMSIZ olay + coklu rejim gerekir.")


if __name__ == "__main__":
    main()
