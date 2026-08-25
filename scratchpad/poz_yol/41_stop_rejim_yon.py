#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STOPUN DEGERI REJIME MI, YONE MI BAGLI? — on-kayit ON_KAYIT_sure_rejim.md.

OLCUTLER ON-KAYITTA SABIT — burada TEKRAR EDILMEZ, hesaplanip basilir.

D = net(STOP YOK) - net(STOP %3)
   D > 0 -> stop ZARAR veriyor    D < 0 -> stop KORUYOR

Kesit TARAFSIZ: kapi suzgeci UYGULANMAZ (kapinin kendi yanliligi karismasin).
Likidasyon simule edilir (kaldirac 3 -> aleyhte ~%33,33).
Fonlama fonlama_oku ile (birim dogrulamasi zorunlu).

SALT OKUMA.
"""
# [2026-08-25] cp1254 TUZAGI — kalici kapatma.
#   Windows konsolu cp1254; print() icindeki emoji/varyasyon secici CIKTI
#   YONLENDIRILDIGINDE UnicodeEncodeError firlatiyor ve betik COKUYOR.
#   Bu sinif bu projede BES kez isirdi. Emoji ayiklamak yerine stdout
#   guvenli hale getirilir; hata sinifi disiplinle degil ARACLA kapanir.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, sys, json, datetime, collections, statistics as sx, math

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
sys.path.insert(0, SCRATCH)
import fonlama_oku as fo                                        # noqa: E402

KLINE = os.path.join(SCRATCH, "klines_1h_uzun")
ADIM, MIN_QV = 4, 125000
MALIYET = 0.1726
KALDIRAC = 3.0
LIQ = 100.0 / KALDIRAC          # %33,33 aleyhte -> likidasyon
STOPLAR = [3.0, 5.0]            # birincil %3
UFUKLAR = [4, 24, 72]           # saat; birincil 24
BIRINCIL_STOP, BIRINCIL_UFUK = 3.0, 24


def ms(s):
    return int(datetime.datetime.strptime(s, "%Y-%m-%d").timestamp() * 1000)


PENCERE = [
    ("ATH 24-09/12", ms("2024-09-15"), ms("2024-12-15"), "yukselen"),
    ("ATH 25-06/10", ms("2025-06-01"), ms("2025-10-15"), "yukselen"),
    ("TOPARLANMA 25-04", ms("2025-04-03"), ms("2025-05-15"), "yukselen"),
    ("DERIN-AYI 26-01", ms("2026-01-05"), ms("2026-03-20"), "dusen"),
    ("AYI 26-06/08", ms("2026-06-24"), ms("2026-08-19"), "dusen"),
]
MAKS_UFUK = max(UFUKLAR)


def oynat(b, i, ref, yon, ft, fr):
    """-> {(stop, ufuk): (net, tip)}  ·  stop None = STOP YOK."""
    n = len(b)
    son = min(i + MAKS_UFUK, n - 1)
    # aleyhte kumulatif en buyuk hareket (yuzde), bar bar
    aleyhte = []
    en = 0.0
    for j in range(i + 1, son + 1):
        x = b[j]
        a = ((x["h"] - ref) if yon == "SHORT" else (ref - x["l"])) / ref * 100
        en = max(en, a)
        aleyhte.append(en)
    if not aleyhte:
        return {}
    out = {}
    for stop in STOPLAR + [None]:
        esik = stop if stop is not None else LIQ
        # ilk asma bari (aleyhte monoton artan -> ilk gecis)
        vur = None
        for k, a in enumerate(aleyhte):
            if a >= esik:
                vur = k
                break
        for ufuk in UFUKLAR:
            sinir = min(ufuk, len(aleyhte)) - 1
            if sinir < 0:
                continue
            if vur is not None and vur <= sinir:
                ham, tip, cj = -esik, ("STOP" if stop is not None else "LIQ"), i + 1 + vur
            else:
                c = b[i + 1 + sinir]["c"]
                ham = ((ref - c) if yon == "SHORT" else (c - ref)) / ref * 100
                tip, cj = "SURE", i + 1 + sinir
            f = fo.dilim(ft, fr, b[i + 1]["t"], b[cj]["t"], yon)
            out[(stop, ufuk)] = (ham - MALIYET + f, tip)
    return out


def topla():
    kova = {ad: [] for ad, _, _, _ in PENCERE}
    dosya = sorted(f for f in os.listdir(KLINE) if f.endswith(".json"))
    for n, fn in enumerate(dosya, 1):
        sym = fn[:-5]
        if sym == "BTC":
            continue
        try:
            with open(os.path.join(KLINE, fn), encoding="utf-8") as f:
                b = json.load(f)
        except Exception:
            continue
        if len(b) < 100:
            continue
        try:
            ft, fr = fo.yukle(sym)
        except fo.BirimHatasi as e:
            print("  ATLANDI %s: %s" % (sym, e))
            continue
        for i in range(24, len(b) - MAKS_UFUK - 2, ADIM):
            x = b[i]
            if (x.get("qv") or 0) < MIN_QV:
                continue
            ad = None
            for a, t0, t1, _ in PENCERE:
                if t0 <= x["t"] < t1:
                    ad = a
                    break
            if ad is None:
                continue
            ref = b[i + 1]["o"]
            if ref <= 0:
                continue
            gun = datetime.datetime.fromtimestamp(x["t"] / 1000).strftime("%Y-%m-%d")
            r = {"sym": sym, "gun": gun}
            bos = False
            for yon in ("LONG", "SHORT"):
                res = oynat(b, i, ref, yon, ft, fr)
                if not res:
                    bos = True
                    break
                for (stop, ufuk), (net, tip) in res.items():
                    r["%s_%s_%d" % (yon, "N" if stop is None else int(stop), ufuk)] = net
                    if stop is None and ufuk == BIRINCIL_UFUK:
                        r["%s_liq" % yon] = 1 if tip == "LIQ" else 0
            if not bos:
                kova[ad].append(r)
        if n % 150 == 0:
            print("  ... %d/%d sembol" % (n, len(dosya)))
            sys.stdout.flush()
    return kova


def gun_t(v, alan_a, alan_b, cikar=()):
    """gun-kumeli ESLESMIS fark: ort(alan_a) - ort(alan_b) her gun."""
    g = collections.defaultdict(lambda: [[], []])
    for x in v:
        if x["sym"] in cikar:
            continue
        a, b2 = x.get(alan_a), x.get(alan_b)
        if isinstance(a, (int, float)) and isinstance(b2, (int, float)):
            g[x["gun"]][0].append(a)
            g[x["gun"]][1].append(b2)
    gunluk = [sx.mean(a) - sx.mean(b2) for a, b2 in g.values() if len(a) >= 5]
    if len(gunluk) < 8:
        return None, None, len(gunluk)
    m, sd = sx.mean(gunluk), sx.pstdev(gunluk)
    return m, (m / (sd / math.sqrt(len(gunluk))) if sd > 0 else None), len(gunluk)


def yogun3(v, alan_a, alan_b):
    kat = collections.defaultdict(float)
    for x in v:
        a, b2 = x.get(alan_a), x.get(alan_b)
        if isinstance(a, (int, float)) and isinstance(b2, (int, float)):
            kat[x["sym"]] += (a - b2)
    return {k for k, _ in sorted(kat.items(), key=lambda z: -abs(z[1]))[:3]}


if __name__ == "__main__":
    print("STOP: REJIM mi YON mu? — on-kayit ON_KAYIT_sure_rejim.md")
    print("D = net(STOP YOK) - net(STOP %%%.0f) · ufuk %dsa · maliyet %%%.4f · liq %%%.1f"
          % (BIRINCIL_STOP, BIRINCIL_UFUK, MALIYET, LIQ))
    kova = topla()

    hucre = {}
    print("\n" + "=" * 100)
    print("%-20s %-6s %9s %8s %7s %9s %8s %7s" %
          ("pencere", "yon", "D", "gun-t", "gun", "D(top3cik)", "liq%", "tur"))
    print("=" * 100)
    for ad, _, _, tur in PENCERE:
        v = kova[ad]
        if len(v) < 300:
            print("%-20s N=%d YETERSIZ" % (ad, len(v)))
            continue
        for yon in ("LONG", "SHORT"):
            a = "%s_N_%d" % (yon, BIRINCIL_UFUK)
            b2 = "%s_%d_%d" % (yon, int(BIRINCIL_STOP), BIRINCIL_UFUK)
            m, t, ng = gun_t(v, a, b2)
            if m is None:
                print("%-20s %-6s gun yetersiz (%d)" % (ad, yon, ng))
                continue
            m2, _, _ = gun_t(v, a, b2, cikar=yogun3(v, a, b2))
            liq = 100.0 * sx.mean(x.get("%s_liq" % yon, 0) for x in v)
            hucre[(ad, yon)] = (m, t, m2, liq, tur)
            print("%-20s %-6s %+9.3f %+8.2f %7d %+10.3f %7.1f %7s"
                  % (ad, yon, m, t if t is not None else float("nan"), ng,
                     m2 if m2 is not None else float("nan"), liq, tur))

    print("\n" + "=" * 100)
    print("OLCUT DEGERLENDIRMESI (ON_KAYIT_sure_rejim.md)")
    print("=" * 100)
    yuk = [(k, x) for k, x in hucre.items() if x[4] == "yukselen"]
    dus = [(k, x) for k, x in hucre.items() if x[4] == "dusen"]
    h1a = all(x[0] < 0 for _, x in yuk) and len(yuk) == 6
    h1b = all(x[0] > 0 for _, x in dus) and len(dus) == 4
    h1c = sum(1 for _, x in hucre.items() if x[1] is not None and abs(x[1]) >= 2.0)
    print("  H1a yukselen 6 hucrenin HEPSINDE D<0 : %d/6 negatif -> %s"
          % (sum(1 for _, x in yuk if x[0] < 0), "GECTI" if h1a else "DUSTU"))
    print("  H1b dusen 4 hucrenin HEPSINDE D>0    : %d/4 pozitif -> %s"
          % (sum(1 for _, x in dus if x[0] > 0), "GECTI" if h1b else "DUSTU"))
    print("  H1c |t|>=2,0 en az 6 hucrede         : %d/10 -> %s"
          % (h1c, "GECTI" if h1c >= 6 else "DUSTU"))
    H1 = h1a and h1b and h1c >= 6
    print("  --> H1 (REJIM aciklamasi) : %s" % ("GECTI" if H1 else "DUSTU"))
    lo = [x for k, x in hucre.items() if k[1] == "LONG"]
    sh = [x for k, x in hucre.items() if k[1] == "SHORT"]
    h2a = sum(1 for x in lo if x[0] < 0)
    h2b = sum(1 for x in sh if x[0] > 0)
    print("  H2a LONG'da D<0, >=4/5               : %d/%d -> %s"
          % (h2a, len(lo), "GECTI" if h2a >= 4 else "DUSTU"))
    print("  H2b SHORT'ta D>0, >=4/5              : %d/%d -> %s"
          % (h2b, len(sh), "GECTI" if h2b >= 4 else "DUSTU"))
    print("  H2c |t|>=2,0 en az 6 hucrede         : %d/10 -> %s"
          % (h1c, "GECTI" if h1c >= 6 else "DUSTU"))
    H2 = h2a >= 4 and h2b >= 4 and h1c >= 6
    print("  --> H2 (YON aciklamasi)   : %s" % ("GECTI" if H2 else "DUSTU"))
    dondu = sum(1 for _, x in hucre.items()
                if x[2] is not None and (x[0] > 0) != (x[2] > 0))
    print("\n  K1 yogunlasma: en iyi 3 sembol cikinca isaret DONEN hucre: %d -> %s"
          % (dondu, "GECTI" if dondu == 0 else "DUSTU"))
    bask = sum(1 for _, x in hucre.items() if x[3] > 25.0)
    print("  K3 likidasyon >%%25 olan hucre: %d (hukme sayilmaz)" % bask)
    print("\nKarar tablosu ON_KAYIT_sure_rejim.md'de. Bot dosyalarina yazim: YOK")
