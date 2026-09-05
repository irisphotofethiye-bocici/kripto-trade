#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OBI — INDIRICI (2026-09-05)

ON-KAYIT: ON_KAYIT_obi.md, commit 0db685f — KOSUMDAN ONCE yazildi.

IKI IS:
  A) bookDepth -> SAATLIK OBI (±%1 · ±%2 · ±%5)
     🔴 Ham dosya DISKE HIC YAZILMAZ — indirilir, ayristirilir, atilir.
        (21.600 dosya x 500 kB = 10 GB; saklamaya gerek yok.)
  B) 5m klines -> etiket fiyatlari (ufuk merdiveni icin ZORUNLU)
     Kalici uc fapi/v1/klines, 1500 bar/cagri.

PARALEL: sembol ICINDE gunler 8 is parcacigina dagitilir. Tek is parcacigiyla
   1,92 sn x 21.600 = 11,5 saat olurdu.
   ⚠️ data.binance.vision STATIK dosya sunucusu (S3), fapi'nin oran sinirlayicisi
      DEGIL. 8 baglanti mutedil. fapi'ye giden B kismi TEK is parcacigi + bekleme.

KESINTIYE DAYANIKLI: her sembol kendi dosyasina yazilir, tamamlanan atlanir.

EVREN ve PENCERE on-kayittan AYNEN gelir — burada degistirilmez.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import urllib.request, urllib.error, zipfile, io, os, json, time, random, datetime
import argparse, statistics as stx
from concurrent.futures import ThreadPoolExecutor

ARSIV = "https://data.binance.vision/"
FAPI = "https://fapi.binance.com/fapi/v1/klines"
BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURASI))
KL_UZUN = os.path.join(KOK, "scratchpad", "klines_1h_uzun")
OBI_DIR = os.path.join(BURASI, "obi")
FIY_DIR = os.path.join(BURASI, "fiyat")

# --- ON-KAYIT bolum 5: EVREN ve PENCERE. DEGISTIRILMEZ. ---
TOHUM = 20260905
N_SEMBOL = 120
BAS_GUN = datetime.date(2025, 9, 7)
SON_GUN = datetime.date(2026, 8, 31)
ADIM_GUN = 2
SEVIYELER = (1.0, 2.0, 5.0)
IS_PARCACIGI = 8


def gunler():
    out, g = [], BAS_GUN
    while g <= SON_GUN:
        out.append(g.strftime("%Y-%m-%d"))
        g += datetime.timedelta(days=ADIM_GUN)
    return out


def _ac(url, timeout=90, deneme=3):
    for i in range(deneme):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if i == deneme - 1:
                raise
            time.sleep(2 * (i + 1))
        except Exception:
            if i == deneme - 1:
                raise
            time.sleep(2 * (i + 1))
    return None


def bd_yol(sym, gun):
    return "data/futures/um/daily/bookDepth/%s/%s-bookDepth-%s.zip" % (sym, sym, gun)


def obi_cikar(ham):
    """bookDepth ham metni -> {saat_kovasi: {seviye: OBI_ortalama}}

    OBI = (alis_notional - satis_notional) / (alis + satis), anlik goruntu basina;
    sonra SAAT icinde ortalama. Saat sonunda bilinen bilgi -> ILERI BAKIS YOK.
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
        for lv in SEVIYELER:
            b, a = sev.get(-lv), sev.get(lv)
            if b and a and (b + a) > 0:
                saat.setdefault(kova, {}).setdefault(lv, []).append((b - a) / (b + a))
    return dict((k, dict((str(lv), round(stx.mean(v), 6)) for lv, v in d.items()))
                for k, d in saat.items())


def _sinama():
    """🔴 G-a KAPISI: bilinen girdi -> beklenen OBI. Duserse betik CALISMAYI REDDEDER."""
    ham = "\n".join([
        "timestamp,percentage,depth,notional",
        # saat 0: alis 300, satis 100  -> OBI = +0,5
        "2026-01-01 00:00:00,-1.00,1,300", "2026-01-01 00:00:00,1.00,1,100",
        # saat 0 ikinci anlik goruntu: alis 100, satis 300 -> OBI = -0,5
        "2026-01-01 00:30:00,-1.00,1,100", "2026-01-01 00:30:00,1.00,1,300",
        # saat 1: alis 100, satis 100 -> OBI = 0
        "2026-01-01 01:00:00,-1.00,1,100", "2026-01-01 01:00:00,1.00,1,100",
        # saat 2: ±%5 seviyesi, alis 900 satis 100 -> OBI = +0,8
        "2026-01-01 02:00:00,-5.00,1,900", "2026-01-01 02:00:00,5.00,1,100",
    ])
    o = obi_cikar(ham)
    k0 = int(datetime.datetime(2026, 1, 1, 0, tzinfo=datetime.UTC).timestamp()) // 3600
    bek = [(k0, "1.0", 0.0), (k0 + 1, "1.0", 0.0), (k0 + 2, "5.0", 0.8)]
    for kova, lv, v in bek:
        g = o.get(kova, {}).get(lv)
        if g is None or abs(g - v) > 1e-9:
            raise RuntimeError("G-a SINAMASI DUSTU: kova %s seviye %s -> %s (beklenen %s)"
                               % (kova, lv, g, v))
    # saat 0'da IKI anlik goruntunun ortalamasi 0 olmali (+0,5 ve -0,5)
    if abs(o[k0]["1.0"]) > 1e-9:
        raise RuntimeError("G-a: saat ortalamasi yanlis")
    # ±%5 saat 2'de var ama ±%1 OLMAMALI (o satirlar yok)
    if "1.0" in o.get(k0 + 2, {}):
        raise RuntimeError("G-a: olmayan seviye uretildi")
    print("   G-a sinamasi: GECTI (isaret · saat ortalamasi · seviye ayrimi · olmayan seviye)")


# ---------------------------------------------------------------------------
def evren():
    """On-kayit bolum 5: ILK gunde bookDepth'i olan VE klines'ta bulunanlardan
    TOHUM=20260905 ile rastgele 120."""
    kl = set()
    if os.path.isdir(KL_UZUN):
        for f in os.listdir(KL_UZUN):
            if f.endswith(".json"):
                kl.add(f[:-5] + "USDT")
    ilk = BAS_GUN.strftime("%Y-%m-%d")
    aday = sorted(kl)
    print("   klines'ta sembol: %d — ilk gunde (%s) bookDepth kontrolu..." % (len(aday), ilk))

    def kontrol(s):
        try:
            r = urllib.request.urlopen(
                urllib.request.Request(ARSIV + bd_yol(s, ilk), method="HEAD"), timeout=20)
            return s if int(r.headers.get("Content-Length") or 0) > 0 else None
        except Exception:
            return None
    with ThreadPoolExecutor(max_workers=IS_PARCACIGI) as ex:
        var = [x for x in ex.map(kontrol, aday) if x]
    print("   ilk gunde bookDepth'i olan: %d" % len(var))
    rnd = random.Random(TOHUM)
    sec = sorted(rnd.sample(var, min(N_SEMBOL, len(var))))
    print("   TOHUM %d ile secilen: %d sembol" % (TOHUM, len(sec)))
    return sec


def sembol_obi(sym, gunl):
    """Bir sembolun tum gunlerini PARALEL indir, saatlik OBI'ye cevir, HAMI AT."""
    def bir_gun(g):
        try:
            ham_z = _ac(ARSIV + bd_yol(sym, g))
        except Exception:
            return {}
        if not ham_z:
            return {}
        try:
            z = zipfile.ZipFile(io.BytesIO(ham_z))
            return obi_cikar(z.read(z.namelist()[0]).decode("utf-8", "replace"))
        except Exception:
            return {}
        # ham_z burada kapsam disina cikar -> DISKE YAZILMADI
    out = {}
    with ThreadPoolExecutor(max_workers=IS_PARCACIGI) as ex:
        for d in ex.map(bir_gun, gunl):
            out.update(d)
    return out


def sembol_fiyat(sym, bas_ms, son_ms):
    """5m klines, kalici uctan. -> {5dk_kovasi: kapanis}"""
    out, bas = {}, bas_ms
    while bas < son_ms:
        u = "%s?symbol=%s&interval=5m&startTime=%d&endTime=%d&limit=1500" % (
            FAPI, sym, bas, son_ms)
        try:
            d = json.loads(_ac(u, timeout=40) or b"[]")
        except Exception:
            break
        if not d:
            break
        for b in d:
            out[int(b[0]) // 300000] = float(b[4])
        yeni = int(d[-1][0])
        if yeni <= bas:
            break
        bas = yeni + 1
        if len(d) < 1500:
            break
        time.sleep(random.uniform(0.05, 0.15))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="ilk N sembol (deneme)")
    ap.add_argument("--sadece", choices=("obi", "fiyat"), default=None)
    a = ap.parse_args()

    print("=" * 92)
    print("OBI INDIRICI — on-kayit 0db685f")
    print("=" * 92)
    print("### 0) G-a KAPISI")
    _sinama()
    print()

    os.makedirs(OBI_DIR, exist_ok=True)
    os.makedirs(FIY_DIR, exist_ok=True)
    gl = gunler()
    print("### 1) PENCERE ve EVREN")
    print("   gun: %d  (%s .. %s, %d gunde bir)" % (len(gl), gl[0], gl[-1], ADIM_GUN))
    ev_yol = os.path.join(BURASI, "evren.json")
    if os.path.exists(ev_yol):
        syms = json.load(open(ev_yol, encoding="utf-8"))
        print("   evren dosyadan okundu: %d sembol (TOHUM sabit)" % len(syms))
    else:
        syms = evren()
        json.dump(syms, open(ev_yol, "w", encoding="utf-8"))
    if a.limit:
        syms = syms[:a.limit]
    print("   islenecek: %d sembol · toplam %d dosya" % (len(syms), len(syms) * len(gl)))
    print()

    t0 = time.time()
    if a.sadece != "fiyat":
        print("### 2) bookDepth -> SAATLIK OBI  (ham dosya DISKE YAZILMAZ)")
        ok = atl = 0
        for i, s in enumerate(syms, 1):
            yol = os.path.join(OBI_DIR, "%s.json" % s)
            if os.path.exists(yol):
                atl += 1
                continue
            o = sembol_obi(s, gl)
            with open(yol + ".tmp", "w", encoding="utf-8") as f:
                json.dump(o, f)
            os.replace(yol + ".tmp", yol)
            ok += 1
            gecen = time.time() - t0
            kalan = (gecen / max(1, ok)) * (len(syms) - i) / 60
            print("   [%3d/%d] %-16s %5d saat kovasi  (kalan ~%.0f dk)"
                  % (i, len(syms), s, len(o), kalan))
        print("   -> yeni %d · atlandi %d · %.1f dk" % (ok, atl, (time.time() - t0) / 60))
        print()

    if a.sadece != "obi":
        print("### 3) 5m klines -> etiket fiyatlari")
        bas_ms = int(datetime.datetime.combine(
            BAS_GUN, datetime.time(), datetime.UTC).timestamp() * 1000)
        son_ms = int(datetime.datetime.combine(
            SON_GUN + datetime.timedelta(days=2), datetime.time(),
            datetime.UTC).timestamp() * 1000)
        t1, ok2, atl2 = time.time(), 0, 0
        for i, s in enumerate(syms, 1):
            yol = os.path.join(FIY_DIR, "%s.json" % s)
            if os.path.exists(yol):
                atl2 += 1
                continue
            f5 = sembol_fiyat(s, bas_ms, son_ms)
            with open(yol + ".tmp", "w", encoding="utf-8") as f:
                json.dump(f5, f)
            os.replace(yol + ".tmp", yol)
            ok2 += 1
            if i % 10 == 0 or i <= 2:
                gecen = time.time() - t1
                kalan = (gecen / max(1, ok2)) * (len(syms) - i) / 60
                print("   [%3d/%d] %-16s %6d bar  (kalan ~%.0f dk)"
                      % (i, len(syms), s, len(f5), kalan))
        print("   -> yeni %d · atlandi %d · %.1f dk" % (ok2, atl2, (time.time() - t1) / 60))

    print()
    print("Ham bookDepth diske YAZILMADI · Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
