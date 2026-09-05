#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OBI — VERI HAZIRLAMA (2026-09-05)

ON-KAYIT: ON_KAYIT_obi.md, commit 0db685f — KOSUMDAN ONCE yazildi.

cikti: scratchpad/obi/panel.jsonl
satir: {gun, sym, obi1, obi2, obi5, r5, r30, r60, r240, r1440, onceki, rejim}

🔴 ILERI BAKIS KORUMASI — bu betigin en kritik yeri:
   OBI, H saatinin ORTALAMASI. Dolayisiyla ancak H'nin SONUNDA bilinir.
   O yuzden TUM ileri getiriler H'nin SONUNDAN baslar:
       t0 = (H+1) * 3600 sn   ->  5dk kovasi (H+1)*12
   'onceki' (son 1 saat getirisi, P4/P5 icin) da H'nin KENDISI uzerinde
   hesaplanir; H sonunda bilinir. Ikisi de mesru.

REJIM: evren.btc_rejim() gun gun NEDENSEL yeniden uretim.
   Fonksiyonlar scratchpad/rejim_gecis_sayim.py'den KOPYALANDI (o modul
   modul-duzeyinde print yapiyor, import edilemez).
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
OBI_DIR = os.path.join(BURASI, "obi")
FIY_DIR = os.path.join(BURASI, "fiyat")
PANEL = os.path.join(BURASI, "panel.jsonl")
KL_UZUN = os.path.join(KOK, "scratchpad", "klines_1h_uzun")
KL_TAZE = os.path.join(KOK, "scratchpad", "taze_1h")

# on-kayit bolum 4: ufuk merdiveni (DAKIKA)
UFUKLAR = (("r5", 5), ("r30", 30), ("r60", 60), ("r240", 240), ("r1440", 1440))
MIN_SAAT = 500          # G-b: sembol basina en az gozlem

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
        wc = [c for d, c in _haftalik(G[:i + 1])]
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


def btc_saatlik():
    out = {}
    for kok in (KL_UZUN, KL_TAZE):
        p = os.path.join(kok, "BTC.json")
        if not os.path.exists(p):
            continue
        for b in json.load(open(p, encoding="utf-8")):
            out[int(b["t"]) // 3600000] = float(b["c"])
    return out


def _sinama_ileri_bakis():
    """🔴 ZORUNLU: ufuk hesabi H'nin SONUNDAN mi basliyor?
    Bilinen fiyat serisiyle sinanir; duserse betik CALISMAYI REDDEDER."""
    # H saati = kova 100. H sonu = 101*3600 sn = 5dk kovasi 101*12 = 1212
    H = 100
    fiy = {}
    for k in range(1200, 1600):
        fiy[k] = 100.0
    fiy[1212] = 100.0          # t0  (H'nin SONU)
    fiy[1213] = 110.0          # +5 dk   -> %10
    fiy[1218] = 120.0          # +30 dk  -> %20
    fiy[1224] = 130.0          # +60 dk  -> %30
    r = ufuk_getirileri(fiy, H)
    bek = {"r5": 10.0, "r30": 20.0, "r60": 30.0}
    for k, v in bek.items():
        if r.get(k) is None or abs(r[k] - v) > 1e-9:
            raise RuntimeError("ILERI BAKIS SINAMASI DUSTU: %s -> %s (beklenen %s)"
                               % (k, r.get(k), v))
    # H'nin ICINDEKI fiyat degisimi ileri getiriye SIZMAMALI
    fiy2 = dict(fiy)
    fiy2[1205] = 999.0         # H'nin ortasi — hicbir ufku etkilememeli
    r2 = ufuk_getirileri(fiy2, H)
    if any(abs(r2[k] - r[k]) > 1e-9 for k in bek):
        raise RuntimeError("ILERI BAKIS SINAMASI DUSTU: H ici fiyat ufuklara sizdi")
    print("   ileri-bakis sinamasi: GECTI (t0 = H sonu · H ici sizinti yok)")


def ufuk_getirileri(fiy5, saat_kovasi):
    """H saatinin SONUNDAN baslayan ham ileri getiriler (%)."""
    t0 = (saat_kovasi + 1) * 12          # 5dk kovasi
    p0 = fiy5.get(t0)
    out = {}
    for ad, dk in UFUKLAR:
        p1 = fiy5.get(t0 + dk // 5)
        out[ad] = ((p1 / p0 - 1) * 100) if (p0 and p1) else None
    return out


def main():
    print("=" * 92)
    print("OBI — VERI HAZIRLAMA (on-kayit 0db685f)")
    print("=" * 92)
    print()
    print("### 0) ZORUNLU SINAMA")
    _sinama_ileri_bakis()
    print()

    btc = btc_saatlik()
    rej = rejim_serisi([{"t": k * 3600000, "c": v} for k, v in sorted(btc.items())])
    print("### 1) REJIM: %d gun  ·  %s" % (len(rej), dict(Counter(rej.values()))))
    print()

    dosyalar = sorted(f for f in os.listdir(OBI_DIR) if f.endswith(".json"))
    print("### 2) PANEL")
    print("   OBI dosyasi: %d" % len(dosyalar))

    n_sat = n_sym = dus_fiyat = dus_az = 0
    etiket_var = etiket_top = 0
    with open(PANEL, "w", encoding="utf-8") as cikti:
        for fn in dosyalar:
            sym = fn[:-5]
            fyol = os.path.join(FIY_DIR, fn)
            if not os.path.exists(fyol):
                dus_fiyat += 1
                continue
            obi = json.load(open(os.path.join(OBI_DIR, fn), encoding="utf-8"))
            fiy = dict((int(k), v) for k, v in
                       json.load(open(fyol, encoding="utf-8")).items())
            yazilan = 0
            for k_str, sev in obi.items():
                H = int(k_str)
                o1 = sev.get("1.0")
                if o1 is None:
                    continue
                r = ufuk_getirileri(fiy, H)
                etiket_top += 1
                if r["r60"] is None:
                    continue
                etiket_var += 1
                # onceki: H saatinin KENDI getirisi (H sonunda bilinir)
                pa, pb = fiy.get(H * 12), fiy.get((H + 1) * 12)
                onceki = ((pb / pa - 1) * 100) if (pa and pb) else None
                gun = (datetime.datetime(1970, 1, 1)
                       + datetime.timedelta(hours=H)).strftime("%Y-%m-%d")
                sat = {"gun": gun, "sym": sym, "saat": H,
                       "obi1": o1, "obi2": sev.get("2.0"), "obi5": sev.get("5.0"),
                       "onceki": onceki, "rejim": rej.get(gun, "?")}
                for ad, _ in UFUKLAR:
                    sat[ad] = r[ad]
                cikti.write(json.dumps(sat, ensure_ascii=False) + "\n")
                yazilan += 1
            if yazilan >= MIN_SAAT:
                n_sym += 1
                n_sat += yazilan
            elif yazilan:
                dus_az += 1

    print("   panel satiri (>=%d saatli sembollerden): %d" % (MIN_SAAT, n_sat))
    print("   gecerli sembol: %d · <%d saat dustu: %d · fiyat yok: %d"
          % (n_sym, MIN_SAAT, dus_az, dus_fiyat))
    print()
    print("### 3) G-e KAPISI — etiket kapsami")
    kap = (etiket_var / etiket_top * 100) if etiket_top else 0
    print("   +1s etiketi bulunan OBI saati: %d / %d = %%%.1f  -> %s"
          % (etiket_var, etiket_top, kap, "✅" if kap >= 90 else "🔴 DUSTU (>=%90)"))
    print()
    print("cikti: %s" % PANEL)
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
