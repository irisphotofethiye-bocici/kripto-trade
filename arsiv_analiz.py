#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARSIV ANALIZ — radar_archive.jsonl forward-return cozucusu (2026-07-02, M7 duzeltmesi).
Hipotez testlerinin KALICI araci; eski scratchpad/short_test.py oturumla kaybolmustu.

Ne yapar:
  - Arsiv satirlarini Binance 1h kline ile birlestirir -> +1h/+3h/+6h/+24h forward return
  - Bagimsiz olay dedup (ayni sembol --dedup_saat penceresinde 1 olay; autocorrelation sismesini keser)
  - Skor-bucket (20-30 / 30-39 / 39-45 / 45+) x ufuk x yon (LONG ham / SHORT ham)
  - Stop'lu SHORT scalp simulasyonu (hipotez#1 metodolojisi: stop %, round-trip maliyet, 3h/6h cikis)
  - Rejim-kosullu ayrim (satirda 'rejim' varsa o; yoksa BTC gunluk SMA20'den tarihsel etiket)
  - Etiket analizi: dip_yakit / ayrisma / (varsa) smart-aligned

REGRESYON BEKLENTISI (ayi verisi 06-24..07-02, hipotez#1 bulgulari):
  45+ SHORT pozitif EV | AYRISMA negatif-edge | 39+ LONG scalp zayif/negatif.
Bu beklentiler tutmuyorsa once VERIYI sorgula (timezone/kline eslesmesi), sonra hipotezi.

Deterministik, 0 token, anahtarsiz. Kullanim:
  python arsiv_analiz.py [--dedup_saat 6] [--stop_pct 5] [--maliyet_pct 0.2] [--min_skor 20]
UYARI: bagimsiz N kucukken (<25-30) sonuclar KANIT degil, izlenimdir (small-N dersi: FOGO vs RE).
"""
import json, os, sys, time, argparse, datetime, urllib.request, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
FAPI = "https://fapi.binance.com"
ARSIV = os.path.join(HERE, "radar_archive.jsonl")
UFUKLAR = (1, 3, 6, 24)

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")


def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "arsiv/1.0"})
    return json.load(urllib.request.urlopen(req, timeout=25))


def ts_to_ms(ts):
    """Arsiv ts'i YEREL saattir ('%Y-%m-%d %H:%M') -> UTC epoch ms (timezone dersi: FOGO 04:00 vakasi)."""
    dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M").astimezone()
    return int(dt.timestamp() * 1000)


def klines_1h(sym, start_ms):
    d = get(f"{FAPI}/fapi/v1/klines?symbol={sym}USDT&interval=1h&startTime={start_ms}&limit=1500")
    return {int(k[0]): {"h": float(k[2]), "l": float(k[3]), "c": float(k[4])} for k in d}


def btc_gunluk_rejim():
    """Gun -> AYI/BOGA/NOTR haritasi (BTC 1d, SMA20 + egim; evren.btc_rejim ile ayni kural, tarihsel)."""
    try:
        d = get(f"{FAPI}/fapi/v1/klines?symbol=BTCUSDT&interval=1d&limit=90")
    except Exception:
        return {}
    days, closes = [], []
    for k in d:
        days.append(datetime.datetime.fromtimestamp(int(k[0]) / 1000).strftime("%Y-%m-%d"))
        closes.append(float(k[4]))
    rej = {}
    for i in range(len(closes)):
        if i < 20:
            continue
        sma = statistics.mean(closes[i-19:i+1])
        slope = closes[i] - closes[i-20]
        rej[days[i]] = "BOGA" if (closes[i] > sma and slope > 0) else ("AYI" if (closes[i] < sma and slope < 0) else "NOTR")
    return rej


def bucket(score):
    if score >= 45: return "45+"
    if score >= 39: return "39-45"
    if score >= 30: return "30-39"
    return "20-30"


def ozet(rets):
    """[(ret_long_pct)] -> (n, long_win%, long_avg, short_win%, short_avg)"""
    n = len(rets)
    if not n:
        return 0, None, None, None, None
    lw = sum(1 for r in rets if r > 0) / n * 100
    la = statistics.mean(rets)
    return n, round(lw), round(la, 2), round(100 - lw), round(-la, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dedup_saat", type=float, default=6.0)
    ap.add_argument("--stop_pct", type=float, default=5.0)
    ap.add_argument("--maliyet_pct", type=float, default=0.2, help="round-trip fee+slip (%)")
    ap.add_argument("--min_skor", type=float, default=20.0)
    a = ap.parse_args()

    rows = []
    for line in open(ARSIV, encoding="utf-8"):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("score", 0) >= a.min_skor or r.get("dip_yakit") or r.get("ayrisma"):
            rows.append(r)
    rows.sort(key=lambda r: r["ts"])
    print(f"=== ARSIV ANALIZ === ({len(rows)} aday satir, min_skor={a.min_skor})")
    if not rows:
        return

    # Bagimsiz olay dedup (sembol basina pencere)
    son, olaylar = {}, []
    dd_ms = a.dedup_saat * 3600 * 1000
    for r in rows:
        ms = ts_to_ms(r["ts"])
        if r["sym"] in son and ms - son[r["sym"]] < dd_ms:
            continue
        son[r["sym"]] = ms
        r["_ms"] = ms
        olaylar.append(r)
    print(f"Bagimsiz olay (dedup {a.dedup_saat}h): {len(olaylar)}  |  {rows[0]['ts']} -> {rows[-1]['ts']}")

    # Kline join (sembol basina tek cagri)
    kl, atla = {}, 0
    syms = sorted({r["sym"] for r in olaylar})
    start = min(r["_ms"] for r in olaylar) - 3600_000
    for s in syms:
        try:
            kl[s] = klines_1h(s, start)
        except Exception:
            kl[s] = {}
        time.sleep(0.05)

    rejim_map = btc_gunluk_rejim()
    for r in olaylar:
        bars = kl.get(r["sym"], {})
        bar0 = r["_ms"] - r["_ms"] % 3600_000
        if bar0 not in bars:
            r["_entry"] = None; atla += 1; continue
        r["_entry"] = bars[bar0]["c"]
        for h in UFUKLAR:
            b = bars.get(bar0 + h * 3600_000)
            r[f"_r{h}"] = round((b["c"] / r["_entry"] - 1) * 100, 3) if b else None
        # stop'lu SHORT sim (hipotez#1): stop asilirsa -stop; degilse 3h kapanista cik
        stop_px = r["_entry"] * (1 + a.stop_pct / 100)
        stopped = any((bars.get(bar0 + k * 3600_000) or {"h": 0})["h"] >= stop_px for k in (1, 2, 3))
        b3 = bars.get(bar0 + 3 * 3600_000)
        if b3:
            r["_short3"] = round((-a.stop_pct if stopped else (r["_entry"] - b3["c"]) / r["_entry"] * 100) - a.maliyet_pct, 3)
        else:
            r["_short3"] = None
        if not r.get("rejim"):
            r["rejim"] = rejim_map.get(r["ts"][:10], "?")
    if atla:
        print(f"(kline eslesmeyen {atla} olay atlandi — delist/veri yok)")

    def tablo(baslik, evs):
        print(f"\n## {baslik}")
        print(f"  {'bucket':7} {'n':>4} | " + " | ".join(f"+{h}h L-win/avg  S-win/avg" for h in (1, 3, 6)))
        for bk in ("45+", "39-45", "30-39", "20-30"):
            sub = [e for e in evs if bucket(e["score"]) == bk]
            if not sub:
                continue
            hucre = []
            for h in (1, 3, 6):
                rets = [e[f"_r{h}"] for e in sub if e.get(f"_r{h}") is not None]
                n, lw, la, sw, sa = ozet(rets)
                hucre.append(f"%{lw}/{la:+.1f}  %{sw}/{sa:+.1f}" if n else "-")
            print(f"  {bk:7} {len(sub):>4} | " + " | ".join(f"{c:22}" for c in hucre))
            # stop'lu short sim
            s3 = [e["_short3"] for e in sub if e.get("_short3") is not None]
            if s3:
                w = sum(1 for x in s3 if x > 0) / len(s3) * 100
                print(f"  {'':7} {'':>4}   SHORT-sim 3h (stop %{a.stop_pct:.0f}+maliyet): win %{w:.0f}, ort {statistics.mean(s3):+.2f}%, n={len(s3)}")

    evs = [e for e in olaylar if e.get("_entry")]
    tablo("TUM OLAYLAR (skor-bucket x ufuk; L=long ham, S=short ham)", evs)
    for rj in ("AYI", "NOTR", "BOGA"):
        sub = [e for e in evs if e.get("rejim") == rj]
        if sub:
            tablo(f"REJIM = {rj}", sub)

    def etiket(ad, sec):
        sub = [e for e in evs if sec(e)]
        if not sub:
            print(f"\n## {ad}: olay yok"); return
        print(f"\n## {ad} (n={len(sub)})")
        for h in (1, 3, 6, 24):
            rets = [e[f"_r{h}"] for e in sub if e.get(f"_r{h}") is not None]
            n, lw, la, sw, sa = ozet(rets)
            if n:
                print(f"  +{h}h: LONG win %{lw} ort {la:+.2f}% | SHORT win %{sw} ort {sa:+.2f}% (n={n})")

    etiket("DIP_YAKIT", lambda e: e.get("dip_yakit"))
    etiket("AYRISMA", lambda e: e.get("ayrisma"))
    etiket("45+ & funding<0 (en keskin short kumesi)", lambda e: e["score"] >= 45 and (e.get("funding") or 0) < 0)
    etiket("SMART-ALIGNED SHORT (smart=SHORT, yeni Pillar D verisi)", lambda e: e.get("smart") == "SHORT")
    etiket("SMART-ALIGNED LONG (smart=LONG)", lambda e: e.get("smart") == "LONG")

    print("\nREGRESYON KONTROL (hipotez#1, ayi verisi): 45+ SHORT pozitif mi? AYRISMA long negatif mi? 39+ LONG zayif mi?")
    print("UYARI: bagimsiz N<25-30 = izlenim, kanit degil. BOGA verisi girince yon-edge YENIDEN olculur (rejim tablosu).")


if __name__ == "__main__":
    main()
