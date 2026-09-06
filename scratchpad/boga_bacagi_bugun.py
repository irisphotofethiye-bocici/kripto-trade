#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOGA BACAGI — BIZIM 14 GUNLUK BOGA PENCEREMIZ DOSYAYLA TUTUYOR MU? (2026-09-06)

KULLANICI: "elimizdeki 14 gunluk boga verisi burdakiyle tutuyor mu?"

🔴 ONCE TESPIT: ORTUSME YOK.
   boga_bacagi_islemler.json  ->  2019-07-23 .. 2026-07-13
   bizim pencere              ->  2026-08-22 .. 2026-09-04
   Ayni islemleri kiyaslamak MUMKUN DEGIL. Yapilabilecek tek sey: AYNI KURALI
   bosluk doneminde kosturup dosyanin donemleriyle yan yana koymak.

🟡 BETIMLEYICI — HUKUM DEGIL, KURAL CIKMAZ.
   Bu bir on-kayitli sinama degil; var olan bir olcumun TAZE VERIDE nasil
   gorundugunun betimlemesi. Buradan kural cikarilmaz.

KURAL boga_bacagi_test.py'den BIREBIR kopyalandi (parametre DEGISTIRILMEDI):
   Trend : kapanis > MA200 VE MA50 > MA200
   Tetik : gunun DUSUGU <= MA50 VE kapanis > MA50
   Giris : ERTESI gunun acilisi   ·  Stop: son 5 gun dip - 0,25 x ATR14
   Hedef : giris + 2 x (giris - stop)  ·  Sure: en fazla 30 gun
   Ayni gun stop+hedef -> STOP (muhafazakar)  ·  sembol basina tek pozisyon
   Maliyet: gidis-donus %0,09 + gunde %0,03 fonlama vekili

🔴 VERI: ayni kaynak (SPOT gunluk klines). Onbellek 2026-08-09'da bitiyordu;
   eksik kuyruk EZMEDEN birlestirildi (kullanicinin duran kurali).

⚠️ 30 GUNLUK TUTUS SINIRI: 2026-08-07'den sonra acilan pozisyonlar bugune
   kadar COZULEMEZ. COZULEN ve KIRPILAN ayri raporlanir — karistirmak
   sonucu yanli yapardi.

SALT-OKUNUR (onbellek disinda yazim yok).
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, time, urllib.request, statistics as st, collections

BURASI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURASI, "klines_cache")
ISLEMLER = os.path.join(BURASI, "boga_bacagi_islemler.json")
SPOT = "https://api.binance.com/api/v3/klines"

# --- boga_bacagi_test.py'den BIREBIR ---
MAKS_GUN = 30
MALIYET_SABIT = 0.0009          # gidis-donus taker
MALIYET_GUNLUK = 0.0003         # fonlama vekili
SEMBOLLER = ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT", "LINK", "LTC",
             "AVAX", "ATOM", "ALGO", "AAVE", "UNI", "FIL", "ICP", "NEAR", "ETC",
             "XLM", "VET", "TRX", "EOS", "THETA", "MANA"]

BOSLUK_BAS = "2026-07-14"       # dosyanin bittigi gunden SONRA
BIZIM_BAS, BIZIM_SON = "2026-08-22", "2026-09-04"


def guncelle(sym):
    """Onbellegi oku, eksik kuyrugu indir, EZMEDEN birlestir."""
    yol = os.path.join(CACHE, "%sUSDT_1d.json" % sym)
    bars = []
    if os.path.exists(yol):
        try:
            bars = json.load(open(yol, encoding="utf-8"))
        except Exception as e:
            raise RuntimeError("OKUNAMADI, uzerine YAZILMADI: %s (%s)" % (yol, e))
    eski_n = len(bars)
    bas = (bars[-1]["t"] + 86400000) if bars else 1546300800000
    yeni = []
    while True:
        u = "%s?symbol=%sUSDT&interval=1d&startTime=%d&limit=1000" % (SPOT, sym, bas)
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                d = json.loads(r.read())
        except Exception:
            break
        if not d:
            break
        yeni += d
        if len(d) < 1000:
            break
        bas = d[-1][0] + 86400000
        time.sleep(0.12)
    for k in yeni:
        bars.append({"t": k[0],
                     "gun": time.strftime("%Y-%m-%d", time.gmtime(k[0] / 1000)),
                     "o": float(k[1]), "h": float(k[2]),
                     "l": float(k[3]), "c": float(k[4])})
    # damgaya gore tekillestir + sirala
    d2 = dict((b["t"], b) for b in bars)
    bars = [d2[t] for t in sorted(d2)]
    if len(bars) < eski_n:
        raise RuntimeError("KISALMA: %s %d -> %d (yazilmadi)" % (yol, eski_n, len(bars)))
    if len(bars) > eski_n:
        tmp = yol + ".tmp"
        json.dump(bars, open(tmp, "w", encoding="utf-8"))
        os.replace(tmp, yol)
    return bars, len(bars) - eski_n


def ma(v, i, n):
    return st.mean(v[i - n + 1:i + 1]) if i >= n - 1 else None


def atr14(bars, i):
    if i < 14:
        return None
    tr = [max(bars[j]["h"] - bars[j]["l"],
              abs(bars[j]["h"] - bars[j - 1]["c"]),
              abs(bars[j]["l"] - bars[j - 1]["c"])) for j in range(i - 13, i + 1)]
    return st.mean(tr)


def sinyaller(bars):
    cl = [b["c"] for b in bars]
    out, mesgul = [], -1
    for i in range(200, len(bars) - 1):
        if i <= mesgul:
            continue
        m50, m200 = ma(cl, i, 50), ma(cl, i, 200)
        if not m50 or not m200:
            continue
        if not (cl[i] > m200 and m50 > m200):
            continue
        if not (bars[i]["l"] <= m50 and cl[i] > m50):
            continue
        out.append(i + 1)
        mesgul = i + MAKS_GUN
    return out


def isle(bars, gi):
    """gi = giris bar indeksi. -> (r_brut, r_net, tut, cozuldu_mu)"""
    if gi >= len(bars):
        return None
    giris = bars[gi]["o"]
    a = atr14(bars, gi - 1)
    if not a:
        return None
    dip = min(b["l"] for b in bars[max(0, gi - 5):gi])
    stop = dip - 0.25 * a
    risk = giris - stop
    if risk <= 0:
        return None
    hedef = giris + 2 * risk
    for j in range(gi, min(gi + MAKS_GUN, len(bars))):
        tut = j - gi + 1
        if bars[j]["l"] <= stop:                      # ayni gun ikisi de -> STOP
            r = -1.0
            return r, r - (MALIYET_SABIT + MALIYET_GUNLUK * tut) / risk * giris, tut, True
        if bars[j]["h"] >= hedef:
            r = 2.0
            return r, r - (MALIYET_SABIT + MALIYET_GUNLUK * tut) / risk * giris, tut, True
    son = len(bars) - 1
    if son - gi + 1 < MAKS_GUN:                       # veri bitti, SURE DOLMADI
        tut = son - gi + 1
        r = (bars[son]["c"] - giris) / risk
        return r, r - (MALIYET_SABIT + MALIYET_GUNLUK * tut) / risk * giris, tut, False
    tut = MAKS_GUN
    j = min(gi + MAKS_GUN - 1, son)
    r = (bars[j]["c"] - giris) / risk
    return r, r - (MALIYET_SABIT + MALIYET_GUNLUK * tut) / risk * giris, tut, True


def ozet(ad, kayit):
    if not kayit:
        print("   %-24s (kayit yok)" % ad)
        return
    b = [k["r_brut"] for k in kayit]
    n = [k["r_net"] for k in kayit]
    kaz = sum(1 for x in n if x > 0)
    print("   %-24s N=%-4d brut %+7.3f  net %+7.3f  kazanan %%%-5.0f tut %.1f"
          % (ad, len(kayit), st.mean(b), st.mean(n), 100.0 * kaz / len(kayit),
             st.mean([k["tut"] for k in kayit])))


def main():
    print("=" * 92)
    print("BOGA BACAGI — 14 GUNLUK PENCEREMIZ DOSYAYLA TUTUYOR MU?")
    print("=" * 92)
    print("🟡 BETIMLEYICI — hukum degil, kural cikmaz.")
    print()

    print("### 1) ORTUSME KONTROLU")
    d = json.load(open(ISLEMLER, encoding="utf-8"))
    gs = [x["gun"] for x in d]
    print("   dosya    : %s .. %s  (N=%d)" % (min(gs), max(gs), len(d)))
    print("   pencere  : %s .. %s" % (BIZIM_BAS, BIZIM_SON))
    print("   ORTUSME  : %d kayit  ->  %s"
          % (sum(1 for g in gs if BIZIM_BAS <= g <= BIZIM_SON), "YOK"))
    print()

    print("### 2) ONBELLEK GUNCELLEME (EZMEDEN birlestirilir)")
    veri, eklenen = {}, 0
    for s in SEMBOLLER:
        try:
            bars, ek = guncelle(s)
        except Exception as e:
            print("   %-6s HATA %s" % (s, str(e)[:60]))
            continue
        veri[s] = bars
        eklenen += ek
    son = max((b[-1]["gun"] for b in veri.values()), default="-")
    print("   sembol %d · eklenen yeni bar %d · en son gun %s"
          % (len(veri), eklenen, son))
    print()

    print("### 3) AYNI KURAL, BOSLUK DONEMINDE (%s -> bugun)" % BOSLUK_BAS)
    cozulen, kirpik, bizim = [], [], []
    for s, bars in veri.items():
        for gi in sinyaller(bars):
            if gi >= len(bars):
                continue
            gun = bars[gi]["gun"]
            if gun < BOSLUK_BAS:
                continue
            r = isle(bars, gi)
            if not r:
                continue
            kay = {"sym": s, "gun": gun, "r_brut": r[0], "r_net": r[1], "tut": r[2]}
            (cozulen if r[3] else kirpik).append(kay)
            if BIZIM_BAS <= gun <= BIZIM_SON:
                bizim.append(kay)
    ozet("bosluk COZULEN", cozulen)
    ozet("bosluk KIRPIK (sure dolmadi)", kirpik)
    print()
    print("   ⚠️ KIRPIK olanlar 30 gunu DOLDURAMADI (veri bitti). Ayri tutuldu;")
    print("      cozulenlerle karistirmak sonucu yanli yapardi.")
    print()

    print("### 4) BIZIM 14 GUNLUK PENCEREMIZ (%s .. %s)" % (BIZIM_BAS, BIZIM_SON))
    ozet("pencere ICI tetik", bizim)
    if bizim:
        for k in sorted(bizim, key=lambda x: x["gun"]):
            print("      %-6s %s  brut %+6.2f  net %+6.2f  tut %2d"
                  % (k["sym"], k["gun"], k["r_brut"], k["r_net"], k["tut"]))
    print()

    print("### 5) DOSYANIN DONEMLERIYLE YAN YANA")
    g = collections.defaultdict(list)
    for x in d:
        g[x["donem"]].append(x)
    for ad in ("2020-21 BOGA", "2023-24 BOGA", "2022 AYI", "2025-26 SON", "ONCESI"):
        if ad in g:
            ozet("[dosya] " + ad, g[ad])
    ozet("[TAZE] bosluk cozulen", cozulen)
    ozet("[TAZE] bizim 14 gun", bizim)
    print()

    print("### 6) OKUMA")
    if not bizim:
        print("   Bizim 14 gunluk pencerede F1 TETIGI HIC OLUSMADI.")
        print("   -> 'tutuyor mu' sorusu bu kural icin CEVAPSIZ: kiyaslanacak")
        print("      islem yok. Pencere kuralin ornekleme hizina gore COK KISA.")
    else:
        print("   Pencere ici N=%d — tek basina hicbir hukum tasimaz." % len(bizim))
    print()
    print("Yalniz onbellege yazildi (birlestirerek). Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
