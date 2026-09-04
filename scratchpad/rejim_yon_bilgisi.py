#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REJIM ETIKETI YON BILGISI TASIYOR MU? — 2 yil, cok epizot.
On-kayit: ON_KAYIT_rejim_etiketi.md (commit 32b908f, KOSUMDAN ONCE). Olcutler SABIT.

Rejim serisi BTC 1h mumundan NEDENSEL uretilir (rejim_gecis_sayim.py deseni;
radar_archive.rejim KULLANILMAZ — tanimi 2026-07-22'de degisti).

🔴 BIRIM = GUN. Ayni gun 566 sembol bagimsiz degil -> her gun icin semboller
   arasi MEDYAN ileri getiri TEK gozlem.
🔴 EPIZOT KIRILIMI ZORUNLU (kullanici uyarisi): havuz hukmu tek basina yazilmaz.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, io, json, math, datetime, statistics, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KL = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
OLU_BANT = 2.0        # esikler.f10_olu_bant_pct
HISTEREZIS = 3        # esikler.f10_histerezis_gun


def gunluk_kapanis(sym):
    try:
        with open(os.path.join(KL, sym + ".json"), encoding="utf-8") as f:
            bars = json.load(f)
    except Exception:
        return None
    g = {}
    for b in bars:
        t = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(b["t"]))
        g[t.date()] = float(b["c"])
    return g


def dogrulanmis_seri():
    """🔴 KENDI YENIDEN URETIMIMI KULLANMIYORUM — DOGRULANMIS OLANI YUKLUYORUM.

    Ilk denemede kendi surumumu yazdim ve UYUSMADI (745 gun/AYI 133 vs
    dogrulanmis 611 gun/AYI 204). Uc gercek hata vardi:
      (a) SEZON isinma penceresi (>=21 hafta ve wc[-21:-1]) atlanmisti
      (b) HAVA'nin SMA'si gunun KENDISINI iceriyordu (dogrusu HARIC)
      (c) TEPKI_RALLISI (sezon AYI + hava BOGA) NOTR'a haritalanmisti;
          DOGRUSU AYI  <- en buyuk fark bundandi
    Ders: dogrulanmis kod YENIDEN YAZILMAZ, CAGRILIR.
    """
    yol = os.path.join(PROJE, "scratchpad", "rejim_gecis_sayim.py")
    kaynak = open(yol, encoding="utf-8").read()
    ns = {"__name__": "_rejim_kaynak", "__file__": yol}
    tut = _sys.stdout
    _sys.stdout = io.StringIO()          # betigin kendi ciktisini yut
    try:
        exec(compile(kaynak, yol, "exec"), ns)
    finally:
        _sys.stdout = tut
    S = ns["S"]                          # isinma zaten elenmis
    return {x["gun"].date(): {"rejim": x["rejim"], "sezon": x["sezon"],
                              "hava": x["hava"], "f10": x["f10"],
                              "btc": x["kapanis"]} for x in S}


BEKLENEN = {"gun": 611, "NOTR": 313, "AYI": 204, "BOGA": 94}


def seri_sinamasi(rej):
    """Dogrulanmis betigin RAPORLADIGI sayilarla birebir uyusmali."""
    say = collections.Counter(v["rejim"] for v in rej.values())
    hata = []
    if len(rej) != BEKLENEN["gun"]:
        hata.append("gun sayisi %d, beklenen %d" % (len(rej), BEKLENEN["gun"]))
    for k in ("NOTR", "AYI", "BOGA"):
        if say.get(k, 0) != BEKLENEN[k]:
            hata.append("%s %d, beklenen %d" % (k, say.get(k, 0), BEKLENEN[k]))
    if hata:
        print("SERI SINAMASI DUSTU — betik calismayi REDDEDIYOR:")
        for h in hata:
            print("   " + h)
        raise SystemExit(1)
    print("seri sinamasi: GECTI (%d gun · %s)" % (len(rej), dict(say)))


def t_iki(a, b):
    if len(a) < 3 or len(b) < 3:
        return None, None
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    se = math.sqrt(statistics.variance(a) / len(a) + statistics.variance(b) / len(b))
    return (ma - mb), ((ma - mb) / se if se else None)


def main():
    print("REJIM ETIKETI YON BILGISI TASIYOR MU? — 2 yil, cok epizot")
    print("on-kayit ON_KAYIT_rejim_etiketi.md (32b908f) · olcutler SABIT")
    print("=" * 104)

    btc = gunluk_kapanis("BTC")
    if not btc:
        print("BTC mumu yok")
        return
    rej = dogrulanmis_seri()
    seri_sinamasi(rej)
    print("rejim serisi: %d gun · %s .. %s" % (len(rej), min(rej), max(rej)))

    # --- DOGRULAMA: son gunun etiketi
    son = max(rej)
    print("dogrulama — son gun %s: rejim %s (sezon %s · hava %s · BTC %.0f)"
          % (son, rej[son]["rejim"], rej[son]["sezon"], rej[son]["hava"], rej[son]["btc"]))

    # ------------------------------------------------------- alt evren getirisi
    semboller = [f[:-5] for f in os.listdir(KL) if f.endswith(".json")]
    print("\nalt evren: %d sembol okunuyor..." % len(semboller))
    gun_ret = collections.defaultdict(list)
    for s in semboller:
        if s == "BTC":
            continue
        g = gunluk_kapanis(s)
        if not g:
            continue
        gs = sorted(g.items())
        for i in range(len(gs) - 1):
            d0, c0 = gs[i]
            d1, c1 = gs[i + 1]
            if (d1 - d0).days != 1 or c0 <= 0:
                continue
            gun_ret[d0].append((c1 - c0) / c0 * 100.0)
    gunluk = {d: statistics.median(v) for d, v in gun_ret.items() if len(v) >= 30}
    print("  gunluk medyan getirisi olan gun: %d (asgari 30 sembol)" % len(gunluk))

    ortak = sorted(set(gunluk) & set(rej))
    print("  rejim ile ortak gun: %d" % len(ortak))

    kova = collections.defaultdict(list)
    for d in ortak:
        kova[rej[d]["rejim"]].append(gunluk[d])

    print("\n" + "=" * 104)
    print("1) REJIME GORE ALT EVREN GETIRISI (gun birimi, medyan sembol)")
    print("-" * 104)
    print("  %-8s %6s %12s %12s %10s" % ("rejim", "gun", "ort %", "medyan %", "arti gun"))
    for k in ("BOGA", "NOTR", "AYI"):
        v = kova.get(k, [])
        if len(v) < 3:
            continue
        print("  %-8s %6d %+11.3f%% %+11.3f%% %9.0f%%"
              % (k, len(v), sum(v) / len(v), statistics.median(v),
                 100.0 * sum(1 for x in v if x > 0) / len(v)))

    boga = kova.get("BOGA", [])
    diger = kova.get("NOTR", []) + kova.get("AYI", [])
    fark, t = t_iki(boga, diger)
    print("\n" + "=" * 104)
    print("2) BIRINCIL — K1/K2/K3")
    print("=" * 104)
    print("  BOGA ort           : %+.3f%%  (N=%d)" % (sum(boga) / len(boga), len(boga)))
    print("  NOTR+AYI ort       : %+.3f%%  (N=%d)" % (sum(diger) / len(diger), len(diger)))
    print("  fark               : %+.3f%%  ·  iki-orneklemli t %s"
          % (fark, ("%+.2f" % t) if t else "-"))
    k1 = fark > 0 and t is not None and t >= 2.0
    k2 = sum(boga) / len(boga) > 0
    k3 = sum(diger) / len(diger) < 0
    print()
    print("  K1  fark>0 ve t>=+2,0        : %-6s" % ("GECTI" if k1 else "DUSTU"))
    print("  K2  BOGA ort > 0 (LONG savunulur mu) : %-6s" % ("GECTI" if k2 else "DUSTU"))
    print("  K3  NOTR+AYI ort < 0 (SHORT savunulur mu): %-6s" % ("GECTI" if k3 else "DUSTU"))
    print("  -> HUKUM: %s" % ("GECTI" if k1 else ("KISMI" if (k2 and k3) else "DUSTU")))

    # ------------------------------------------------------- K4 belirleyici
    print("\n" + "=" * 104)
    print("3) 🔑 K4 BELIRLEYICI — etiket FIYATIN KILIGI mi?")
    print("   btc_chg24 ceyrekleri ICINDE BOGA farki kaliyor mu?")
    print("-" * 104)
    bg = sorted(btc.items())
    chg = {}
    for i in range(1, len(bg)):
        d0, c0 = bg[i - 1]
        d1, c1 = bg[i]
        if c0 > 0:
            chg[d1] = (c1 - c0) / c0 * 100.0
    ort3 = [d for d in ortak if d in chg]
    ort3.sort(key=lambda d: chg[d])
    q = len(ort3) // 4
    print("  %-16s %8s %10s %10s %10s %9s"
          % ("btc_chg24 ceyrek", "gun", "BOGA n", "BOGA %", "diger %", "fark"))
    farklar = []
    for i, ad in enumerate(("Q1 en dusuk", "Q2", "Q3", "Q4 en yuksek")):
        w = ort3[i * q:(i + 1) * q] if i < 3 else ort3[3 * q:]
        b = [gunluk[d] for d in w if rej[d]["rejim"] == "BOGA"]
        o = [gunluk[d] for d in w if rej[d]["rejim"] != "BOGA"]
        if len(b) < 3 or len(o) < 3:
            print("  %-16s %8d %10d  (N yetersiz)" % (ad, len(w), len(b)))
            continue
        f = sum(b) / len(b) - sum(o) / len(o)
        farklar.append(f)
        print("  %-16s %8d %10d %+9.3f%% %+9.3f%% %+8.3f%%"
              % (ad, len(w), len(b), sum(b) / len(b), sum(o) / len(o), f))
    if farklar:
        ic_ort = sum(farklar) / len(farklar)
        print("  " + "-" * 68)
        print("  ceyrek ICI ortalama fark : %+.3f%%   (havuz farki %+.3f%%)" % (ic_ort, fark))
        kalan = 100.0 * ic_ort / fark if fark else 0
        print("  havuz farkinin ceyrek icinde KALAN payi: %%%.0f" % kalan)
        k4 = kalan >= 50
        print("  -> K4: %s" % ("etiket EK BILGI tasiyor (fark ceyrek icinde duruyor)" if k4
                               else "🔴 etiket FIYATIN KILIGI (fark ceyrek icinde kayboluyor)"))

    # ------------------------------------------------------- epizotlar
    print("\n" + "=" * 104)
    print("4) 🔴 EPIZOT KIRILIMI — ZORUNLU (kullanici: '11-19'u baska rejim, unutma')")
    print("-" * 104)
    epi = []
    prev, bas, onceki = None, None, None
    for d in ortak:
        r = rej[d]["rejim"]
        if r != prev:
            if prev is not None:
                epi.append((prev, bas, onceki))
            prev, bas = r, d
        onceki = d
    if prev is not None:
        epi.append((prev, bas, onceki))
    print("  %-8s %-12s %-12s %5s %12s" % ("rejim", "baslangic", "bitis", "gun", "ort alt %"))
    boga_epi = []
    for r, a, b in epi:
        gg = [gunluk[d] for d in ortak if a <= d <= b]
        if len(gg) < 2:
            continue
        m = sum(gg) / len(gg)
        if r == "BOGA":
            boga_epi.append((a, m, len(gg)))
        yildiz = "   <== 11-19 dilimi" if (a <= datetime.date(2026, 8, 15) <= b) else ""
        yildiz += "   <== GUNCEL" if b >= max(ortak) - datetime.timedelta(days=1) else ""
        print("  %-8s %-12s %-12s %5d %+11.3f%%%s" % (r, a, b, len(gg), m, yildiz))

    if boga_epi:
        print("\n  BOGA epizotlari siralamasi (ort alt getiriye gore):")
        sb = sorted(boga_epi, key=lambda z: z[1])
        for j, (a, m, ng) in enumerate(sb):
            im = "   <== GUNCEL EPIZOT" if a >= datetime.date(2026, 8, 20) else ""
            print("    %d/%d  %s  %+7.3f%%  (%d gun)%s" % (j + 1, len(sb), a, m, ng, im))

    # ------------------------------------------------------- gecikme
    print("\n" + "=" * 104)
    print("5) GECIKME — betimleyici, N kucuk, HUKUM YOK")
    print("-" * 104)
    gec = []
    ds = sorted(rej)
    for i in range(1, len(ds)):
        if rej[ds[i]]["rejim"] == "BOGA" and rej[ds[i - 1]]["rejim"] != "BOGA":
            j = max(0, i - 7)
            c0, c1 = rej[ds[j]]["btc"], rej[ds[i]]["btc"]
            gec.append((ds[i], (c1 - c0) / c0 * 100.0))
    print("  NOTR->BOGA gecisleri · etiket donmeden ONCEKI 7 gunde BTC hareketi")
    for d, v in gec:
        print("    %s   BTC onceki 7 gun: %+7.2f%%" % (d, v))
    if gec:
        vv = [v for _, v in gec]
        print("  ortalama %+.2f%% · medyan %+.2f%% · N=%d"
              % (sum(vv) / len(vv), statistics.median(vv), len(vv)))

    print("\n" + "=" * 104)
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
