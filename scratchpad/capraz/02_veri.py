#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CAPRAZ BORSA — VERI HAZIRLAMA (2026-09-05)

ON-KAYIT: ON_KAYIT_capraz_borsa.md, commit a0e52c5 — KOSUMDAN ONCE yazildi.

NE YAPAR: indirilen iki-borsa fonlamasini panele cevirir.
   cikti: scratchpad/capraz/panel.jsonl
   satir: {gun, sym, fark, f_bin, f_by, fwd24, rejim}

🔴 UC KRITIK NOKTA:

1) YEREL ARALIK NORMALIZASYONU (on-kayit bolum 2, karar 1)
   Fonlama araligi sembol ICINDE ZAMANLA DEGISIYOR — indirmede goruldu
   (0GUSDT bybit 4.977 kayit; 24 ayda 4 saatlik ust sinir 4.380).
   Global medyan bu yuzden YANLIS. Her kayit icin aralik, KOMSU kayitlarin
   medyanindan cikarilir ve {1,2,4,8} saate yapistirilir.
       gunluk_oran = ham_oran * 24 / aralik_saat
   Aksi halde `funding_gecmis` birim kirilmasiyla AYNI hata: iki farkli sey
   ayni adi tasir, join sessizce yanlis cikar.

2) SAAT HIZALAMASI — iki borsanin damgalari UTC ms. Ayni SAAT kovasina
   dusenler eslesir. klines de UTC -> ofset YOK.
   (radar_archive'daki UTC+3 sorunu buraya girmiyor; oraya hic bakilmiyor.)

3) ETIKET HAM — +24 saat ham fiyat getirisi. Mekanik YOK, stop YOK.
   CLAUDE.md asama sirasi: ham getiri -> mekanik -> portfoy.

REJIM: evren.btc_rejim() mantigi gun gun NEDENSEL yeniden uretilir.
   Fonksiyonlar scratchpad/rejim_gecis_sayim.py'den KOPYALANDI (import edilmiyor
   cunku o modul modul-duzeyinde print yapiyor). O betik "canli etiketle birebir
   uyustu" diye dogrulanmisti.
   🔴 radar_archive'in `rejim` ALANI KULLANILMAZ — 2026-07-22'de tanim degisti.

Salt-okuma + tek cikti dosyasi. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, datetime, statistics as stx
from collections import Counter

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURASI))
VERI = os.path.join(BURASI, "veri")
PANEL = os.path.join(BURASI, "panel.jsonl")
KL_UZUN = os.path.join(KOK, "scratchpad", "klines_1h_uzun")
KL_TAZE = os.path.join(KOK, "scratchpad", "taze_1h")

BAS_GUN = "2024-09-01"
SON_GUN = "2026-08-31"
UFUK_SAAT = 24                      # on-kayitta SABIT, tek ufuk
GECERLI_ARALIK = (1.0, 2.0, 4.0, 8.0)

OLU_BANT = 2.0
HISTEREZIS = 3


# --- rejim (kopya: scratchpad/rejim_gecis_sayim.py) -------------------------
def _gunluk(bars):
    g = {}
    for b in bars:
        t = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(b["t"]))
        g[t.date()] = float(b["c"])
    return [(datetime.datetime.combine(d, datetime.time()), c) for d, c in sorted(g.items())]


def _haftalik(gunler):
    h = {}
    for d, c in gunler:
        h[d.isocalendar()[:2]] = (d, c)
    return [v for k, v in sorted(h.items())]


def rejim_serisi(bars):
    G = _gunluk(bars)
    out = []
    for i in range(len(G)):
        H = _haftalik(G[:i + 1])
        wc = [c for d, c in H]
        sezon = "?"
        if len(wc) >= 21:
            w_ort = stx.mean(wc[-21:-1])
            w_egim = wc[-1] - wc[-21]
            if wc[-1] > w_ort and w_egim > 0:
                sezon = "BOGA"
            elif wc[-1] < w_ort and w_egim < 0:
                sezon = "AYI"
            else:
                sezon = "NOTR"
        cl = [c for d, c in G[max(0, i - 59):i + 1]]
        ham = []
        for j in range(20, len(cl)):
            sma = stx.mean(cl[j - 20:j])
            uz = (cl[j] - sma) / sma * 100
            ham.append("NOTR" if abs(uz) < OLU_BANT else ("BOGA" if uz > 0 else "AYI"))
        hava = ham[0] if ham else "NOTR"
        for j in range(len(ham)):
            if j < HISTEREZIS:
                hava = ham[j]
            else:
                pen = ham[j - HISTEREZIS + 1:j + 1]
                if all(x == pen[0] for x in pen):
                    hava = pen[0]
        if sezon == "AYI" and hava == "BOGA":
            f10 = "TEPKI_RALLISI"
        elif sezon == "BOGA" and hava == "BOGA":
            f10 = "TAM_BOGA"
        elif sezon == "AYI" and hava == "AYI":
            f10 = "DERIN_AYI"
        elif sezon == "BOGA" and hava == "AYI":
            f10 = "BOGA_DUZELTME"
        else:
            f10 = "BELIRSIZ"
        out.append((G[i][0].strftime("%Y-%m-%d"),
                    "BOGA" if f10 == "TAM_BOGA"
                    else ("AYI" if f10 in ("TEPKI_RALLISI", "DERIN_AYI") else "NOTR")))
    return dict(out)


# --- yerel aralik ----------------------------------------------------------
def yerel_aralik(ts_sirali, pencere=10):
    """Her damga icin fonlama araligini SAAT olarak dondur.

    Komsu farklarin medyani alinir ve {1,2,4,8}'e YAPISTIRILIR. Boylece:
      - veri deliği (48 saatlik bosluk) araligi sismez
      - aralik ZAMANLA DEGISIRSE yakalanir (global medyan yakalayamaz)
    Yapisamayan (hicbir gecerli araliga yakin olmayan) kayit None doner ve DUSER.
    """
    n = len(ts_sirali)
    if n < 3:
        return [None] * n
    farklar = [(ts_sirali[i + 1] - ts_sirali[i]) / 3600000.0 for i in range(n - 1)]
    out = []
    for i in range(n):
        a = max(0, i - pencere)
        b = min(len(farklar), i + pencere)
        yerel = [f for f in farklar[a:b] if 0.5 <= f <= 25.0]
        if not yerel:
            out.append(None)
            continue
        m = stx.median(yerel)
        en_yakin = min(GECERLI_ARALIK, key=lambda v: abs(v - m))
        out.append(en_yakin if abs(en_yakin - m) <= en_yakin * 0.35 else None)
    return out


def _sinama():
    """🔴 ZORUNLU: bilinen girdi -> beklenen etiket. Duserse betik CALISMAYI REDDEDER."""
    s = 3600000
    # 8 saatlik duzenli seri
    ts = [i * 8 * s for i in range(30)]
    a = yerel_aralik(ts)
    if set(x for x in a if x) != {8.0}:
        raise RuntimeError("SINAMA DUSTU: duzenli 8s seri -> %s" % set(a))
    # 4 saatlik duzenli seri
    ts = [i * 4 * s for i in range(30)]
    a = yerel_aralik(ts)
    if set(x for x in a if x) != {4.0}:
        raise RuntimeError("SINAMA DUSTU: duzenli 4s seri -> %s" % set(a))
    # 8 saatlik seri ORTASINDA bir DELIK (48 saat) — delik araligi sismemeli
    ts = [i * 8 * s for i in range(15)] + [(14 * 8 + 48 + i * 8) * s for i in range(15)]
    a = yerel_aralik(ts)
    if set(x for x in a if x) != {8.0}:
        raise RuntimeError("SINAMA DUSTU: delikli 8s seri -> %s" % set(a))
    # ARALIK DEGISIMI: once 8s sonra 4s
    ts = [i * 8 * s for i in range(30)]
    t0 = ts[-1]
    ts += [t0 + (i + 1) * 4 * s for i in range(30)]
    a = yerel_aralik(ts)
    if not (a[2] == 8.0 and a[-3] == 4.0):
        raise RuntimeError("SINAMA DUSTU: aralik degisimi -> bas %s son %s" % (a[2], a[-3]))
    print("   sinama: 4/4 GECTI (duzenli 8s · duzenli 4s · delik · aralik degisimi)")


# --- klines ----------------------------------------------------------------
def klines(sym_kisa):
    """uzun + taze BIRLESTIRILMIS saatlik kapanis. {saat_kovasi: kapanis}"""
    out = {}
    for kok in (KL_UZUN, KL_TAZE):
        p = os.path.join(kok, sym_kisa + ".json")
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            continue
        for b in d:
            out[int(b["t"]) // 3600000] = float(b["c"])
    return out


def main():
    print("=" * 92)
    print("CAPRAZ BORSA — VERI HAZIRLAMA (on-kayit a0e52c5)")
    print("=" * 92)
    print()
    print("### 0) YEREL ARALIK SINAMASI (zorunlu)")
    _sinama()
    print()

    btc = klines("BTC")
    if not btc:
        raise RuntimeError("BTC klines yok — rejim uretilemez")
    bars = [{"t": k * 3600000, "c": v} for k, v in sorted(btc.items())]
    rej = rejim_serisi(bars)
    print("### 1) REJIM: %d gun uretildi (%s .. %s)"
          % (len(rej), min(rej), max(rej)))
    print("   dagilim:", dict(Counter(rej.values())))
    print()

    dosyalar = sorted(f for f in os.listdir(VERI) if f.endswith(".json"))
    print("### 2) PANEL")
    print("   indirilmis sembol dosyasi: %d" % len(dosyalar))

    n_sat, n_sym, dusen_aralik, dusen_kapsam, dusen_fiyat = 0, 0, 0, 0, 0
    ozet_aralik = Counter()
    with open(PANEL, "w", encoding="utf-8") as cikti:
        for fn in dosyalar:
            sym = fn[:-5]
            try:
                with open(os.path.join(VERI, fn), encoding="utf-8") as f:
                    d = json.load(f)
            except Exception:
                continue
            kl = klines(sym.replace("USDT", ""))
            if not kl:
                dusen_fiyat += 1
                continue

            saatlik = {}
            for borsa in ("binance", "bybit"):
                ham = d.get(borsa) or {}
                if len(ham) < 20:
                    saatlik[borsa] = {}
                    continue
                ts = sorted(int(t) for t in ham)
                ar = yerel_aralik(ts)
                h = {}
                for t, a in zip(ts, ar):
                    if a is None:
                        dusen_aralik += 1
                        continue
                    ozet_aralik[(borsa, a)] += 1
                    h[t // 3600000] = float(ham[str(t)]) * 24.0 / a
                saatlik[borsa] = h

            ortak = sorted(set(saatlik.get("binance", {})) & set(saatlik.get("bybit", {})))
            yazilan = 0
            for saat in ortak:
                gun = datetime.datetime(1970, 1, 1) + datetime.timedelta(hours=saat)
                gs = gun.strftime("%Y-%m-%d")
                if gs < BAS_GUN or gs > SON_GUN:
                    continue
                p0 = kl.get(saat)
                p1 = kl.get(saat + UFUK_SAAT)
                if not p0 or not p1:
                    continue
                fb = saatlik["binance"][saat]
                fy = saatlik["bybit"][saat]
                cikti.write(json.dumps({
                    "gun": gs, "sym": sym,
                    "fark": round((fb - fy) * 100, 6),
                    "f_bin": round(fb * 100, 6), "f_by": round(fy * 100, 6),
                    "fwd24": round((p1 / p0 - 1) * 100, 6),
                    "rejim": rej.get(gs, "?"),
                }, ensure_ascii=False) + "\n")
                yazilan += 1
            if yazilan >= 100:                 # on-kayit K-c
                n_sym += 1
                n_sat += yazilan
            elif yazilan:
                dusen_kapsam += 1

    print("   panel satiri (>=100 gozlemli sembollerden): %d" % n_sat)
    print("   gecerli sembol: %d  ·  <100 gozlem dustu: %d  ·  fiyat yok: %d"
          % (n_sym, dusen_kapsam, dusen_fiyat))
    print("   aralik yapisamadi (dusen kayit): %d" % dusen_aralik)
    print()
    print("### 3) ARALIK DAGILIMI (birim kirilmasi kaniti)")
    for (borsa, a), k in sorted(ozet_aralik.items()):
        print("   %-9s %.0f saat : %d kayit" % (borsa, a, k))
    print()
    print("cikti: %s" % PANEL)
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
