#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KACIRMA ANALIZ — gunun top-gainer'lari sistemin neresinden kacti? (2026-07-10)
"Binance gainers'i yakalayamiyoruz" sorusunu VERIYLE cevaplar: her gainer icin
radar arsivi + erken-kusak + veto_log + nobetci alarmlari eslestirilir.

Siniflar (oncelik sirasiyla):
  ALERTED     — nobetci alarmi GITTI (sistem insana kadar tasidi; kacirma degil, aksiyon konusu)
  VETOED      — testbot gordu ama kalite filtresi reddetti (veto_analiz forward-return olcuyor)
  SEEN_EARLY  — pump oncesi (chg24 < erken_chg24_max) arsivde gorundu ama alarm/eylem yok
  SEEN_LATE   — arsivde var ama sadece pump sonrasi/dusuk skorla
  MISSED      — hicbir kayitta yok (gercek kor nokta; genelde yeni-listing)

Deterministik, 0 token, SALT OKUR. Kullanim:
  python kacirma_analiz.py [--top 10] [--min_vol_musd 1] [--gun 3]

!!! OVERFIT UYARISI: tek gunun tablosu anekdottur. Sinyal/esik degisikligi icin haftalarca
birikmis tablo + hangi katmanin TEKRARLAYAN darbogaz oldugu kaniti gerekir. Bu arac aksiyon almaz.
"""
import json, os, sys, argparse, datetime
import evren

HERE = os.path.dirname(os.path.abspath(__file__))
ARSIV = os.path.join(HERE, "radar_archive.jsonl")
VETOF = os.path.join(HERE, "veto_log.jsonl")
ALARMF = os.path.join(HERE, "nobetci_alarm.log")

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")


def top_gainers(n, min_vol):
    rows = []
    cryptos = evren.cg_universe()  # kripto-only (2026-07-23 bug-fix): tokenize-hisse (GOOGL/TSLA/SMCI...) eleme
    for x in evren.raw_tickers("fapi"):
        s = x.get("symbol", "")
        if not s.endswith("USDT") or any(s.endswith(b) for b in evren.BAD):
            continue
        sym = s[:-4]
        if sym in evren.STABLES or sym in evren.GOLD:
            continue
        if cryptos and sym not in cryptos:
            continue
        try:
            chg = float(x["priceChangePercent"]); qv = float(x["quoteVolume"])
        except Exception:
            continue
        if qv >= min_vol * 1e6:
            rows.append((sym, chg, qv))
    rows.sort(key=lambda r: -r[1])
    return rows[:n]


def _jsonl_oku(path, tarih_min):
    out = []
    try:
        for line in open(path, encoding="utf-8"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("ts", "") >= tarih_min:
                out.append(d)
    except FileNotFoundError:
        pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--min_vol_musd", type=float, default=1.0)
    ap.add_argument("--gun", type=int, default=3, help="arsivde kac gun geriye bakilsin")
    a = ap.parse_args()

    tarih_min = (datetime.datetime.now() - datetime.timedelta(days=a.gun)).strftime("%Y-%m-%d")
    erken_chg_max = evren.esik("erken_chg24_max", 15.0)

    print("=" * 78)
    print(f"KACIRMA ANALIZ — bugunun top-{a.top} gainer'i sistemin neresinden kacti? ({datetime.datetime.now():%Y-%m-%d %H:%M})")
    print("UYARI: tek gun = anekdot. Esik/sinyal karari icin haftalarca birikim gerekir. Bu arac aksiyon ALMAZ.")
    print("=" * 78)

    gainers = top_gainers(a.top, a.min_vol_musd)
    if not gainers:
        print("gainer listesi cekilemedi (ag?)"); return

    arsiv = _jsonl_oku(ARSIV, tarih_min)
    vetolar = _jsonl_oku(VETOF, tarih_min)
    try:
        alarmlar = [json.loads(l) for l in open(ALARMF, encoding="utf-8").read().splitlines()
                    if l.strip() and l.strip().startswith("{")]
        alarmlar = [x for x in alarmlar if x.get("ts", "") >= tarih_min]
    except Exception:
        alarmlar = []

    sayim = {"ALERTED": 0, "VETOED": 0, "SEEN_EARLY": 0, "SEEN_LATE": 0, "MISSED": 0}
    for sym, chg, qv in gainers:
        a_kayit = [r for r in arsiv if r.get("sym") == sym]
        v_kayit = [v for v in vetolar if v.get("sym") == sym]
        al_kayit = [x for x in alarmlar if x.get("sym") == sym]
        erken_gorunum = [r for r in a_kayit if (r.get("chg24") is not None and r["chg24"] < erken_chg_max)]

        if al_kayit:
            sinif = "ALERTED"
            ilk = al_kayit[0]
            iz = f"nobetci {len(al_kayit)}x alarm, ilki {ilk.get('ts')}"
        elif v_kayit:
            sinif = "VETOED"
            ilk = v_kayit[0]
            iz = f"{ilk.get('kategori')} @ {ilk.get('ts')} ({str(ilk.get('detay'))[:50]})"
        elif erken_gorunum:
            sinif = "SEEN_EARLY"
            ilk = erken_gorunum[0]
            iz = f"arsiv {ilk.get('ts')} skor={ilk.get('score')} chg24={ilk.get('chg24')} erken={ilk.get('erken')}"
        elif a_kayit:
            sinif = "SEEN_LATE"
            ilk = a_kayit[0]
            iz = f"arsiv {ilk.get('ts')} skor={ilk.get('score')} stage={ilk.get('stage')}"
        else:
            sinif = "MISSED"
            iz = "hicbir kayitta yok (yeni listing? havuz disi?)"
        sayim[sinif] += 1
        print(f"{sym:10} +{chg:5.1f}% vol=${qv/1e6:7.1f}M  [{sinif:10}] {iz}")

    print("\n-- Katman ozeti --")
    for k, v in sayim.items():
        if v:
            print(f"  {k:10}: {v}/{len(gainers)}")
    print("\nOkuma rehberi: ALERTED=sistem tasidi (insan aksiyonu konusu) | VETOED=veto_analiz olcuyor |")
    print("SEEN_EARLY=tespit var kopru yok | SEEN_LATE=skor uretmedi | MISSED=gercek kor nokta.")
    print("TEKRARLAYAN darbogaz hangi katmandaysa iyilestirme ORAYA yapilir — sezgiyle sinyal eklenmez.")


if __name__ == "__main__":
    main()
