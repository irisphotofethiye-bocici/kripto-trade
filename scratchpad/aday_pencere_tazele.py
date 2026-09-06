#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""aday_pencere_1h TAZELEME — son mumdan bugune 1s mum EKLER.

🔴 CLAUDE.md: "YENIDEN INDIRME ESKIYI SILEBILIR — indiriciler BIRLESTIRMELI,
EZMEMELI." Bu betik:
  (a) var olan dosyayi OKUR
  (b) zaman damgasina gore BIRLESTIRIR (mevcut kayit KORUNUR, yenisi eklenir)
  (c) sonuc eskisinden KISAysa HATA FIRLATIR ve o dosyayi YAZMAZ

Sema DEGISMEZ: [[ts_ms, high, low, close], ...]  (9 olcum betigi okuyor)
Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, sys, time, datetime as dt
import urllib.request, urllib.error

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIZIN = os.path.join(KOK, "scratchpad", "aday_pencere_1h")
API = "https://fapi.binance.com/fapi/v1/klines"
SAAT = 3_600_000


def klines(sym, bas_ms):
    out, cur = [], bas_ms
    simdi = int(time.time() * 1000)
    while cur < simdi:
        u = "%s?symbol=%sUSDT&interval=1h&startTime=%d&limit=1000" % (API, sym, cur)
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                return out, "sembol-yok"
            if e.code == 418:
                raise RuntimeError("418 IP BAN — DUR")
            if e.code == 429:
                time.sleep(5)
                continue
            return out, "http-%d" % e.code
        except Exception:
            return out, "ag-hatasi"
        if not d:
            break
        for k in d:
            # kapanmamis mumu ALMA (son mum acik olabilir)
            if int(k[6]) >= simdi:
                continue
            out.append([int(k[0]), float(k[2]), float(k[3]), float(k[4])])
        if len(d) < 1000:
            break
        cur = int(d[-1][0]) + SAAT
    return out, None


def f(ms):
    return dt.datetime.utcfromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M")


def main():
    dosyalar = sorted(x for x in os.listdir(DIZIN) if x.endswith(".json"))
    print("=" * 92)
    print("aday_pencere_1h TAZELEME — BIRLESTIRIR, EZMEZ")
    print("dosya: %d" % len(dosyalar))
    print("=" * 92)

    buyudu = aynikaldi = hata = 0
    kisalan = []
    ek_toplam = 0
    en_eski_son = None
    for i, fn in enumerate(dosyalar, 1):
        yol = os.path.join(DIZIN, fn)
        sym = fn[:-5]
        try:
            eski = json.load(open(yol))
        except Exception:
            hata += 1
            continue
        if not eski:
            hata += 1
            continue
        eski.sort(key=lambda z: z[0])
        n0 = len(eski)
        son_ts = eski[-1][0]
        if en_eski_son is None or son_ts < en_eski_son:
            en_eski_son = son_ts

        yeni, hata_s = klines(sym, son_ts + SAAT)
        if hata_s:
            hata += 1
            if i % 40 == 0:
                print("   [%3d/%d] %-10s %s" % (i, len(dosyalar), sym, hata_s))
            continue

        # --- BIRLESTIR: mevcut kayit KORUNUR
        harita = {x[0]: x for x in eski}
        for x in yeni:
            harita.setdefault(x[0], x)
        birlesik = sorted(harita.values(), key=lambda z: z[0])

        # --- (c) KISALMA SINAMASI
        if len(birlesik) < n0:
            kisalan.append((sym, n0, len(birlesik)))
            continue

        if len(birlesik) == n0:
            aynikaldi += 1
            continue

        tmp = yol + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(birlesik, fh, separators=(",", ":"))
        os.replace(tmp, yol)
        ek_toplam += len(birlesik) - n0
        buyudu += 1
        if i % 40 == 0:
            print("   [%3d/%d] %-10s %d -> %d" % (i, len(dosyalar), sym, n0, len(birlesik)))

    print()
    print("=" * 92)
    print("SONUC")
    print("=" * 92)
    print("   onceki en ESKI son-mum : %s" % f(en_eski_son) if en_eski_son else "")
    print("   buyuyen dosya : %d   (toplam +%d mum)" % (buyudu, ek_toplam))
    print("   ayni kalan    : %d" % aynikaldi)
    print("   hata/atlanan  : %d" % hata)
    if kisalan:
        print("   🔴 KISALAN (YAZILMADI): %d" % len(kisalan))
        for s, a, b in kisalan[:10]:
            print("      %-10s %d -> %d" % (s, a, b))
    else:
        print("   kisalan: YOK  ->  (c) sinamasi GECTI")
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
