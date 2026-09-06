#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""funding + long/short birikmesi olcumu — ILERI FIYAT icin 1h mum indirici.

ON_KAYIT_funding_ls_birikme.md bolum 4 · commit 19bbb73 (KOSMADAN once yazildi)

🔴 EZMEZ. scratchpad/klines_1h_uzun/ dizinine DOKUNMAZ; taze mumlar
   scratchpad/taker/klines/ altina iner. Var olan dosya bulunursa
   ZAMAN DAMGASINA GORE BIRLESTIRILIR ve sonuc eskisinden KISAYSA
   HATA FIRLATIR (CLAUDE.md: 'yeniden indirme eskiyi silebilir').

Kaynak: fapi/v1/klines — KALICI sinif, ucretsiz, anahtarsiz.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, sys, time, random, collections

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)
import evren  # noqa: E402

ARSIV = os.path.join(KOK, "radar_archive.jsonl")
CIKTI = os.path.join(KOK, "scratchpad", "fund_ls", "klines")
FAPI = "https://fapi.binance.com"

# Hucre penceresi 2026-06-24 -> 2026-09-06. En uzun ufuk +48s.
# Guvenli aralik: 06-20 ... simdi.
BAS_MS = 1781913600000      # 2026-06-20 00:00 UTC
LIMIT = 1500


def hucre_sembolleri():
    """P1 = TUM arsiv. Suzgec YOK; fiyati olan her sembol.
    (taker olcumunde yalniz 121 hucre sembolu inmisti — burada 461.)"""
    syms = collections.Counter()
    with open(ARSIV, encoding="utf-8", errors="ignore") as f:
        for l in f:
            l = l.strip()
            if not l:
                continue
            try:
                r = json.loads(l)
            except Exception:
                continue
            if not r.get("price") or not r.get("sym"):
                continue
            syms[r.get("sym")] += 1
    return syms


def cek(sym, bas_ms):
    """Bir sembolun mumlarini bas_ms'ten simdiye kadar ceker."""
    out = []
    imlec = bas_ms
    while True:
        u = ("%s/fapi/v1/klines?symbol=%sUSDT&interval=1h&startTime=%d&limit=%d"
             % (FAPI, sym, imlec, LIMIT))
        d = evren.get(u)
        if not d:
            break
        for k in d:
            out.append({"t": int(k[0]), "c": float(k[4]),
                        "h": float(k[2]), "l": float(k[3])})
        if len(d) < LIMIT:
            break
        imlec = int(d[-1][0]) + 3_600_000
        time.sleep(random.uniform(0.10, 0.25))
    return out


def birlestir_yaz(sym, taze):
    """🔴 BIRLESTIRIR, EZMEZ. Sonuc eskisinden KISAysa hata firlatir."""
    yol = os.path.join(CIKTI, sym + ".json")
    eski = []
    if os.path.exists(yol):
        try:
            eski = json.load(open(yol, encoding="utf-8"))
        except Exception:
            eski = []
    harita = {int(x["t"]): x for x in eski}
    for x in taze:
        harita[int(x["t"])] = x
    yeni = [harita[k] for k in sorted(harita)]
    if len(yeni) < len(eski):
        raise RuntimeError("KISALDI %s: eski %d -> yeni %d" % (sym, len(eski), len(yeni)))
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(yeni, f)
    os.replace(tmp, yol)
    return len(eski), len(yeni)


def main():
    os.makedirs(CIKTI, exist_ok=True)
    syms = hucre_sembolleri()
    print("=" * 80)
    print("FUNDING + L/S OLCUMU — ileri fiyat mumlari (on-kayit 19bbb73)")
    print("=" * 80)
    print("arsiv sembolu       : %d" % len(syms))
    print("cikti dizini        : %s" % CIKTI)
    print("🔴 klines_1h_uzun'a DOKUNULMUYOR")
    print()

    ok = hata = 0
    for i, sym in enumerate(sorted(syms), 1):
        try:
            taze = cek(sym, BAS_MS)
            if not taze:
                print("  %3d/%3d %-10s VERI YOK" % (i, len(syms), sym))
                hata += 1
                continue
            e, y = birlestir_yaz(sym, taze)
            ok += 1
            if i % 20 == 0 or i == len(syms):
                print("  %3d/%3d %-10s %d bar (eski %d)" % (i, len(syms), sym, y, e))
        except Exception as ex:
            hata += 1
            print("  %3d/%3d %-10s HATA: %s" % (i, len(syms), sym, ex))
        time.sleep(random.uniform(0.08, 0.20))

    print()
    print("bitti: %d basarili · %d hata" % (ok, hata))
    print("Bot dosyalarina yazim: YOK · eski mum dizini degismedi")


if __name__ == "__main__":
    main()
