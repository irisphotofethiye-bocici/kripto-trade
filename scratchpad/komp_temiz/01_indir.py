#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""POZISYON KOMPOZISYONU (TEMIZ) — metrics arsivi indirici.

ON_KAYIT_komp_temiz.md bolum 5 · commit a89474a (KOSMADAN once yazildi)

Kaynak: data.binance.vision daily/metrics — UCRETSIZ, anahtarsiz.
🔴 EZMEZ: her sembolun dosyasi okunur, SAATLIK satirlar zaman damgasina gore
   birlestirilir; sonuc eskisinden KISAysa hata firlatir (CLAUDE.md).
🔴 SURDURULEBILIR: zaten inmis sembol-gunler atlanir.

Cikti: scratchpad/komp_temiz/metrics/<SYM>.json
   [[ts_ms, count_top, sum_top, count_glob, taker, oi_value], ...]  saatlik
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, io, zipfile, urllib.request, urllib.error, threading, queue, time
import datetime as dt

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVREN = os.path.join(KOK, "scratchpad", "pozisyon_komp", "evren150.txt")
CIKTI = os.path.join(KOK, "scratchpad", "komp_temiz", "metrics")
KOK_URL = "https://data.binance.vision/data/futures/um/daily/metrics"

BAS = dt.date(2025, 9, 6)
SON = dt.date(2026, 8, 25)
IS_PARCACIK = 8

# metrics CSV sutun adlari (CLAUDE.md'de kayitli)
S_TOP_HESAP = "count_toptrader_long_short_ratio"
S_TOP_POZ = "sum_toptrader_long_short_ratio"
S_GLOB_HESAP = "count_long_short_ratio"
S_TAKER = "sum_taker_long_short_vol_ratio"
S_OI_DEG = "sum_open_interest_value"

kilit = threading.Lock()
sayac = {"ok": 0, "yok": 0, "hata": 0, "atlandi": 0}


def gunler():
    g = BAS
    out = []
    while g <= SON:
        out.append(g.isoformat())
        g += dt.timedelta(days=1)
    return out


def indir_gun(sym, gun):
    """Bir sembol-gun -> saatlik satirlar. Yoksa None."""
    u = "%s/%sUSDT/%sUSDT-metrics-%s.zip" % (KOK_URL, sym, sym, gun)
    try:
        ham = urllib.request.urlopen(u, timeout=60).read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    z = zipfile.ZipFile(io.BytesIO(ham))
    sat = z.read(z.namelist()[0]).decode("utf-8", "replace").splitlines()
    if len(sat) < 2:
        return None
    bas = [x.strip() for x in sat[0].split(",")]
    ix = {a: bas.index(a) for a in
          (S_TOP_HESAP, S_TOP_POZ, S_GLOB_HESAP, S_TAKER, S_OI_DEG)
          if a in bas}
    if len(ix) < 5:
        return None
    saatlik = {}
    for l in sat[1:]:
        p = l.split(",")
        if len(p) != len(bas):
            continue
        try:
            t = dt.datetime.strptime(p[0].strip(), "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
        # create_time = canli damga - 5 dk (CLAUDE.md) -> saat kovasi icin +5dk
        t = t + dt.timedelta(minutes=5)
        if t.minute != 0:
            continue                      # yalniz tam saat satirlari
        try:
            v = [float(p[ix[S_TOP_HESAP]]), float(p[ix[S_TOP_POZ]]),
                 float(p[ix[S_GLOB_HESAP]]), float(p[ix[S_TAKER]]),
                 float(p[ix[S_OI_DEG]])]
        except Exception:
            continue
        ms = int(t.replace(tzinfo=dt.UTC).timestamp() * 1000)
        saatlik[ms] = v
    return saatlik


def sembol_isle(sym, tum_gunler):
    yol = os.path.join(CIKTI, sym + ".json")
    eski = []
    if os.path.exists(yol):
        try:
            eski = json.load(open(yol, encoding="utf-8"))
        except Exception:
            eski = []
    harita = {int(x[0]): x[1:] for x in eski}
    var_gun = set(dt.datetime.fromtimestamp(k / 1000, dt.UTC).date().isoformat()
                  for k in harita)
    yeni_gun = [g for g in tum_gunler if g not in var_gun]
    if not yeni_gun:
        with kilit:
            sayac["atlandi"] += 1
        return
    bulundu = 0
    for g in yeni_gun:
        try:
            s = indir_gun(sym, g)
        except Exception:
            with kilit:
                sayac["hata"] += 1
            continue
        if not s:
            with kilit:
                sayac["yok"] += 1
            continue
        harita.update(s)
        bulundu += 1
    if not bulundu:
        return
    cikti = [[k] + harita[k] for k in sorted(harita)]
    if len(cikti) < len(eski):
        raise RuntimeError("KISALDI %s: %d -> %d" % (sym, len(eski), len(cikti)))
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cikti, f)
    os.replace(tmp, yol)
    with kilit:
        sayac["ok"] += bulundu


def main():
    os.makedirs(CIKTI, exist_ok=True)
    syms = [x.strip() for x in open(EVREN, encoding="utf-8") if x.strip()]
    gs = gunler()
    print("=" * 84)
    print("POZISYON KOMPOZISYONU (TEMIZ) — metrics indirici (on-kayit a89474a)")
    print("=" * 84)
    print("sembol : %d  ·  gun: %d  ·  toplam dosya: %d" % (len(syms), len(gs), len(syms) * len(gs)))
    print("cikti  : %s" % CIKTI)
    print("🔴 klines_1h_uzun'a DOKUNULMUYOR · surdurulebilir · birlestirir")
    print()

    q = queue.Queue()
    for s in syms:
        q.put(s)
    t0 = time.time()

    def isci():
        while True:
            try:
                s = q.get_nowait()
            except queue.Empty:
                return
            try:
                sembol_isle(s, gs)
            except Exception as ex:
                with kilit:
                    sayac["hata"] += 1
                print("   %s HATA: %s" % (s, ex))
            finally:
                q.task_done()
                kalan = q.qsize()
                if kalan % 10 == 0:
                    gecen = time.time() - t0
                    print("   kalan %3d sembol · %5.1f dk · ok %d / yok %d / hata %d"
                          % (kalan, gecen / 60.0, sayac["ok"], sayac["yok"], sayac["hata"]))

    isler = [threading.Thread(target=isci, daemon=True) for _ in range(IS_PARCACIK)]
    for t in isler:
        t.start()
    for t in isler:
        t.join()

    print()
    print("bitti: %.1f dk · sembol-gun ok %d · yok(404) %d · hata %d · atlanan sembol %d"
          % ((time.time() - t0) / 60.0, sayac["ok"], sayac["yok"],
             sayac["hata"], sayac["atlandi"]))
    n = len(os.listdir(CIKTI))
    print("dosya: %d sembol" % n)
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
