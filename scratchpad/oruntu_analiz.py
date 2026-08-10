#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ÖRÜNTÜ ANALİZİ (2026-08-10) — botun kazandigi islemlerin profili GENELLENEBILIR mi?

SORU (kullanici): "botun islem actigi ve KAR ETTIGI butun varsayimlari nasil sagladi,
hangi esik ve olcme birimi — detayli arastirip bir oruntu uret."

YONTEM:
  1. Botun 10 gercek isleminin giris-anindaki OLCU DEGERLERI cikarilir (skor, stage,
     pos, chg24, funding, oi24, vol_x, comp, rejim...).
  2. radar_archive.jsonl (46 gun, 121.620 kayit, 384 sembol) uzerinde AYNI olculer
     hesaplanir ve her olay botun GERCEK mekanigiyle ileri oynatilir.
  3. Kazananlarin degerleri POPULASYON icinde nereye dusuyor (yuzdelik) bakilir.
  4. O profil buyuk N'de de pozitif mi -> ORUNTU; degilse tek-vaka.

MEKANIK (projenin standart olcumu — OTOPSI-2/3 ile AYNI, karsilastirilabilir olsun):
  giris  = kaydin ERTESI 1h barinin acilisi (look-ahead yok)
  stop   = olcucu'nun A-varyanti: {yapisal sup/res ±0.25ATR, son 10 barin dibi/tepesi
           ±0.25ATR, 1.5×ATR fallback} icinden GIRISE EN YAKIN olan
  hedef  = 2×risk        · ufuk = 72 saat · FITIL bazli (kapanis degil)
  ayni barda hem stop hem hedef -> STOP (muhafazakar)
  maliyet= 0.04R (projenin standart round-trip tahmini)

SINIR:
  - radar_archive'da smart/taker (Pillar D) YOK -> o iki kapi bu olcumde test edilemez.
  - 46 gunun tamami AYI/NOTR; BOGA hucresi yok.
  - Kazanan islem sayisi 4 (biri kârın %89'u) -> profil TEK VAKADAN turetilmis olabilir;
    bu yuzden asil is populasyon dogrulamasi.
"""
import json, os, sys, time, math, statistics as st, collections
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "klines_1h")
os.makedirs(CACHE, exist_ok=True)
FAPI = "https://fapi.binance.com"
ARSIV = os.path.join(HERE, "radar_archive.jsonl")

DEDUP_SAAT = 6
UFUK = 72
MALIYET_R = 0.04
NBAR = 10


# ---------------------------------------------------------------- veri
def klines(sym):
    yol = os.path.join(CACHE, f"{sym}.json")
    if os.path.exists(yol):
        try:
            return json.load(open(yol))
        except Exception:
            pass
    # arsiv 2026-06-24'te basliyor; ATR/swing icin ~200 bar geriye pay birakiyoruz
    out, bas = [], 1781222400000  # 2026-06-16
    while True:
        u = f"{FAPI}/fapi/v1/klines?symbol={sym}USDT&interval=1h&startTime={bas}&limit=1500"
        try:
            with urllib.request.urlopen(urllib.request.Request(
                    u, headers={"User-Agent": "oruntu/1.0"}), timeout=30) as rq:
                d = json.loads(rq.read())
        except Exception:
            break
        if not d:
            break
        out += d
        if len(d) < 1500:
            break
        bas = d[-1][0] + 3600000
        time.sleep(0.12)
    bars = [{"t": int(k[0]), "o": float(k[1]), "h": float(k[2]),
             "l": float(k[3]), "c": float(k[4])} for k in out]
    json.dump(bars, open(yol, "w"))
    time.sleep(0.08)
    return bars


def ts_ms(ts):
    import datetime
    return int(datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M").astimezone().timestamp() * 1000)


# ---------------------------------------------------------------- olcucu kopyasi
def atr14(bars, i):
    if i < 14:
        return None
    tr = []
    for j in range(i - 13, i + 1):
        p = bars[j - 1]["c"]
        tr.append(max(bars[j]["h"] - bars[j]["l"], abs(bars[j]["h"] - p), abs(p - bars[j]["l"])))
    return st.mean(tr)


def swings(bars, i, left=3, right=3, geri=100):
    """olcucu.swings ile ayni pivot tanimi, [i-geri, i] penceresinde."""
    bas = max(left, i - geri)
    hi, lo = [], []
    for j in range(bas, i - right + 1):
        w = bars[j - left:j + right + 1]
        if not w:
            continue
        if bars[j]["h"] == max(b["h"] for b in w):
            hi.append(bars[j]["h"])
        if bars[j]["l"] == min(b["l"] for b in w):
            lo.append(bars[j]["l"])
    return hi, lo


def kurulum(bars, gi, yon):
    """gi = giris bar indeksi. -> (giris, stop, hedef) | None. olcucu A-varyanti."""
    i = gi - 1
    a = atr14(bars, i)
    if a is None or a <= 0:
        return None
    ref = bars[gi]["o"]
    hi, lo = swings(bars, i)
    res = min([x for x in hi if x > ref], default=None)
    sup = max([x for x in lo if x < ref], default=None)
    adaylar = []
    if yon == "LONG":
        if sup is not None and (ref - sup) <= 3 * a:
            adaylar.append(sup - 0.25 * a)
        nb = min(b["l"] for b in bars[max(0, i - NBAR + 1):i + 1])
        if nb < ref:
            adaylar.append(nb - 0.25 * a)
        adaylar.append(ref - 1.5 * a)
        gecerli = [s for s in adaylar if s < ref]
        stop = max(gecerli) if gecerli else ref - 1.5 * a
        risk = ref - stop
        hedef = ref + 2 * risk
    else:
        if res is not None and (res - ref) <= 3 * a:
            adaylar.append(res + 0.25 * a)
        nb = max(b["h"] for b in bars[max(0, i - NBAR + 1):i + 1])
        if nb > ref:
            adaylar.append(nb + 0.25 * a)
        adaylar.append(ref + 1.5 * a)
        gecerli = [s for s in adaylar if s > ref]
        stop = min(gecerli) if gecerli else ref + 1.5 * a
        risk = stop - ref
        hedef = ref - 2 * risk
    if risk <= 0:
        return None
    return ref, stop, hedef, risk


def yol(bars, gi, yon):
    """R sonucu (maliyet dusulmus) | None."""
    k = kurulum(bars, gi, yon)
    if not k:
        return None
    ref, stop, hedef, risk = k
    son = min(gi + UFUK, len(bars))
    if son - gi < 6:
        return None
    for j in range(gi, son):
        b = bars[j]
        if yon == "LONG":
            if b["l"] <= stop:
                return -1.0 - MALIYET_R
            if b["h"] >= hedef:
                return 2.0 - MALIYET_R
        else:
            if b["h"] >= stop:
                return -1.0 - MALIYET_R
            if b["l"] <= hedef:
                return 2.0 - MALIYET_R
    c = bars[son - 1]["c"]
    ham = (c - ref) / risk if yon == "LONG" else (ref - c) / risk
    return ham - MALIYET_R


def chg24_hesap(bars, gi):
    if gi < 24:
        return None
    o = bars[gi - 24]["c"]
    return (bars[gi]["o"] / o - 1) * 100 if o else None


# ---------------------------------------------------------------- ana
def main():
    print("Arsiv okunuyor...")
    kayitlar = collections.defaultdict(list)
    with open(ARSIV, encoding="utf-8") as f:
        for l in f:
            if not l.strip():
                continue
            r = json.loads(l)
            kayitlar[r["sym"]].append(r)
    print(f"  {sum(len(v) for v in kayitlar.values())} kayit / {len(kayitlar)} sembol")

    olaylar = []
    semboller = sorted(kayitlar, key=lambda s: -len(kayitlar[s]))
    for n, sym in enumerate(semboller, 1):
        bars = klines(sym)
        if len(bars) < 200:
            continue
        idx = {b["t"] // 3600000: i for i, b in enumerate(bars)}
        son_olay = {}
        for r in sorted(kayitlar[sym], key=lambda x: x["ts"]):
            ms = ts_ms(r["ts"])
            saat = ms // 3600000
            if sym in son_olay and (saat - son_olay[sym]) < DEDUP_SAAT:
                continue
            gi = idx.get(saat + 1)     # kaydin ERTESI bari
            if gi is None or gi < 30:
                continue
            son_olay[sym] = saat
            rs = yol(bars, gi, "SHORT")
            rl = yol(bars, gi, "LONG")
            if rs is None and rl is None:
                continue
            olaylar.append({**r, "chg24": chg24_hesap(bars, gi), "R_short": rs, "R_long": rl})
        if n % 40 == 0:
            print(f"  {n}/{len(semboller)} sembol... olay={len(olaylar)}")

    print(f"\nTOPLAM BAGIMSIZ OLAY: {len(olaylar)}")
    json.dump(olaylar, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "oruntu_olaylar.json"), "w"))
    print("kaydedildi -> scratchpad/oruntu_olaylar.json")


if __name__ == "__main__":
    main()
