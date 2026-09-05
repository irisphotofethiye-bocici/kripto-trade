#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EMIR DEFTERI DENGESIZLIGI — PILOT (2026-09-05)

On-kayittan ONCE. Hukum YOK, olcum YOK.
🔴 ILERI GETIRIYE HIC DOKUNMAZ — tasarim kararlari etiketten habersiz kalsin diye.
   (Capraz borsa olcumunde ise yarayan disiplin.)

ALTI SORU — hepsi on-kayita SAYI koymak icin:
  1) bookDepth dosya basina indirme+ayristirma suresi
  2) Etiket icin 5 DAKIKALIK fiyat nereden gelecek? (ufuk merdiveni sart)
  3) Ozellik cikarimi calisiyor mu: saatlik OBI (±%1 · ±%2 · ±%5)
  4) Sembol kapsami: kac sembol tum pencerede var?
  5) OBI gercekten oynuyor mu, sembolden sembole degisiyor mu?
  6) Gercek KAPSAM onerisi (sembol x gun) — sure ve disk

Salt-okunur. Ham dosya SAKLANMAZ (akis halinde islenir).
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import urllib.request, zipfile, io, time, datetime, statistics as stx, os

ARSIV = "https://data.binance.vision/"
BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURASI))
KL = os.path.join(KOK, "scratchpad", "klines_1h_uzun")


def indir(yol, timeout=90):
    with urllib.request.urlopen(ARSIV + yol, timeout=timeout) as r:
        return r.read()


def var_mi(yol):
    try:
        r = urllib.request.urlopen(urllib.request.Request(ARSIV + yol, method="HEAD"), timeout=20)
        return int(r.headers.get("Content-Length") or 0)
    except Exception:
        return None


def bookdepth_yol(sym, gun):
    return "data/futures/um/daily/bookDepth/%s/%s-bookDepth-%s.zip" % (sym, sym, gun)


def saatlik_obi(ham):
    """bookDepth ham metni -> {saat_kovasi: {seviye: OBI}}

    OBI = (alis_notional - satis_notional) / (alis + satis)
    Anlik goruntu basina hesaplanir, sonra SAAT icinde ORTALAMA alinir.
    (Ortalama, tek anlik goruntuden daha az gurultulu; ve saat sonunda
     bilinen bilgiden olustugu icin ILERI BAKIS yok.)
    """
    anlik = {}
    for l in ham.splitlines()[1:]:
        p = l.split(",")
        if len(p) != 4:
            continue
        try:
            anlik.setdefault(p[0], {})[float(p[1])] = float(p[3])
        except ValueError:
            continue
    saat = {}
    for ts, sev in anlik.items():
        try:
            t = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        kova = int(t.replace(tzinfo=datetime.UTC).timestamp()) // 3600
        for lv in (1.0, 2.0, 5.0):
            b, a = sev.get(-lv), sev.get(lv)
            if b and a and (b + a) > 0:
                saat.setdefault(kova, {}).setdefault(lv, []).append((b - a) / (b + a))
    return dict((k, dict((lv, stx.mean(v)) for lv, v in d.items())) for k, d in saat.items())


def main():
    print("=" * 92)
    print("EMIR DEFTERI DENGESIZLIGI — PILOT (on-kayittan ONCE, hukum YOK)")
    print("=" * 92)
    print("🔴 Ileri getiriye DOKUNULMAZ.")
    print()

    gun = "2026-08-20"

    print("### 1) ETIKET ICIN 5 DAKIKALIK FIYAT — ufuk merdiveni sart, kaynak var mi?")
    for tur, yol in (
        ("arsiv 5m klines", "data/futures/um/daily/klines/SOLUSDT/5m/SOLUSDT-5m-%s.zip" % gun),
        ("arsiv 1m klines", "data/futures/um/daily/klines/SOLUSDT/1m/SOLUSDT-1m-%s.zip" % gun),
        ("arsiv 1h klines", "data/futures/um/daily/klines/SOLUSDT/1h/SOLUSDT-1h-%s.zip" % gun),
    ):
        b = var_mi(yol)
        print("   %-18s %s" % (tur, ("VAR %.0f kB" % (b / 1024)) if b else "yok"))
    print("   (elimizde 1h var: klines_1h_uzun. 5dk/30dk ufku icin 5m gerekiyor.)")
    print()

    print("### 2) SEMBOL KAPSAMI — bot evreninin ne kadari arsivde var?")
    kl = set()
    if os.path.isdir(KL):
        for f in os.listdir(KL):
            if f.endswith(".json"):
                kl.add(f[:-5] + "USDT")
    print("   klines_1h_uzun'da sembol: %d" % len(kl))
    ornek = sorted(kl)[:12]
    var, yok = 0, []
    t0 = time.time()
    for s in ornek:
        if var_mi(bookdepth_yol(s, gun)):
            var += 1
        else:
            yok.append(s)
    print("   ornek %d sembolun %d'inde bookDepth VAR  (%.1f sn)"
          % (len(ornek), var, time.time() - t0))
    if yok:
        print("   yok: %s" % ", ".join(yok[:6]))
    print()

    print("### 3) INDIRME + AYRISTIRMA SURESI (gercek olcum)")
    denek = [s for s in ornek if s not in yok][:5]
    sureler, boyutlar, ozellikler = [], [], {}
    for s in denek:
        t1 = time.time()
        try:
            ham_z = indir(bookdepth_yol(s, gun))
            z = zipfile.ZipFile(io.BytesIO(ham_z))
            ham = z.read(z.namelist()[0]).decode("utf-8", "replace")
            obi = saatlik_obi(ham)
        except Exception as e:
            print("   %-14s HATA %s" % (s, str(e)[:50]))
            continue
        dt = time.time() - t1
        sureler.append(dt)
        boyutlar.append(len(ham_z))
        ozellikler[s] = obi
        print("   %-14s %5.2f sn · %5.0f kB · %2d saat kovasi"
              % (s, dt, len(ham_z) / 1024, len(obi)))
    if sureler:
        print("   -> dosya basi medyan %.2f sn · %.0f kB"
              % (stx.median(sureler), stx.median(boyutlar) / 1024))
    print()

    print("### 4) OBI OYNUYOR MU ve SEMBOLDEN SEMBOLE DEGISIYOR MU?")
    print("   %-14s %10s %10s %10s %10s" % ("sembol", "±1% ort", "±1% std", "±2% ort", "±5% ort"))
    for s, obi in ozellikler.items():
        v1 = [d[1.0] for d in obi.values() if 1.0 in d]
        v2 = [d[2.0] for d in obi.values() if 2.0 in d]
        v5 = [d[5.0] for d in obi.values() if 5.0 in d]
        if not v1:
            continue
        print("   %-14s %+10.4f %10.4f %+10.4f %+10.4f"
              % (s, stx.mean(v1), stx.stdev(v1) if len(v1) > 1 else 0,
                 stx.mean(v2) if v2 else 0, stx.mean(v5) if v5 else 0))
    print()

    print("### 5) KESITSEL AYRISMA — ayni saatte semboller arasi yayilim")
    ortak = None
    for obi in ozellikler.values():
        k = set(obi)
        ortak = k if ortak is None else (ortak & k)
    if ortak and len(ozellikler) >= 3:
        yayilim = []
        for kova in sorted(ortak):
            v = [obi[kova][1.0] for obi in ozellikler.values() if 1.0 in obi.get(kova, {})]
            if len(v) >= 3:
                yayilim.append(max(v) - min(v))
        if yayilim:
            print("   ortak saat kovasi: %d  ·  kesitsel yayilim (±%%1) medyan %.4f"
                  % (len(ortak), stx.median(yayilim)))
            print("   -> %s" % ("✅ semboller AYRISIYOR, kesitsel siralama anlamli"
                                if stx.median(yayilim) > 0.05 else
                                "🔴 yayilim kucuk, kesitsel siralama zayif olabilir"))
    print()

    print("### 6) KAPSAM ONERISI (on-kayita yazilacak sayilar)")
    if sureler:
        sn = stx.median(sureler)
        for nsym, ngun in ((150, 180), (120, 180), (100, 240), (150, 120)):
            dosya = nsym * ngun
            print("   %3d sembol x %3d gun = %6d dosya -> ~%.1f saat  (ham SAKLANMAZ)"
                  % (nsym, ngun, dosya, dosya * sn / 3600))
    print()
    print("Ham dosya diske YAZILMADI · Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
