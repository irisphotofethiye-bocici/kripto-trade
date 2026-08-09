#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOGA BACAGI OLCUMU (2026-08-10) — F1 trend-pullback arketipi gercek bogalarda kazaniyor mu?

================================ ON-KAYIT ==================================
(Bu blok SONUCA BAKILMADAN yazildi. Tek varyant kosulur, esik taramasi YASAK.)

SORU: Fikir defteri F1 "kurulu trendde geri cekilme alimi" — sistemin TEK
  elenmemis long arketipi (breakout/beta/anomali-long olctuk, hepsi coktu).
  Gercek boga donemlerinde (2020-21, 2023-24) pozitif beklenti veriyor mu?

NEDEN SIMDI: kazanan-bot-arastirma-raporu §8 adim 1. Elimizde gercek boga
  verisi YOK (K6 bosluğu); tek dolduruş yolu gecmis bogalarda test.

HIPOTEZ (on-kayit): F1 boga donemlerinde net ort R > +0.20 verir ve ayni
  donemdeki KONTROL (rastgele giris) grubunu belirgin gecer. Ayi/notr
  donemlerde edge kaybolur ya da negatiflesir (rejim-kapisi gerekcesi).

KURAL (parametrelerin hepsi KONVANSIYONEL ve testten ONCE sabit):
  Trend  : gunluk kapanis > MA200  VE  MA50 > MA200
  Tetik  : gunun DUSUGU <= MA50 (geri cekilme dokunusu) VE kapanis > MA50 (geri alis)
  Giris  : ERTESI gunun acilisi (look-ahead yok)
  Stop   : son 5 gunun en dusugu - 0.25*ATR14   [F9 mantigi, 2026-07-22]
  Hedef  : giris + 2*(giris-stop)               [botun R/R>=2 kapisiyla ayni]
  Sure   : en fazla 30 gun, dolarsa kapanistan cik
  Ayni gun hem stop hem hedefe dokunulursa STOP kabul edilir (muhafazakar)
  Ayni sembolde ayni anda tek pozisyon

MALIYET: giris+cikis taker %0.045 (toplam %0.09) + perp long funding vekili
  %0.01/8s = gunde %0.03 (boga doneminde long ODER — muhafazakar varsayim).
  Brut ve net AYRI raporlanir.

KONTROL GRUBU: her gercek sinyal icin AYNI sembolde, sinyal gununden ±60 gun
  icinde RASTGELE bir gun (tohum sabit=42), ayni stop/hedef/sure mekanigi.
  Amac: "kural mi ise yariyor yoksa donem mi yukseliyordu" ayrimi.

DONEM AYRIMI (takvimsel, sabit — sonuca gore secilmedi):
  2020-21 BOGA : 2020-04-01 .. 2021-11-10
  2022    AYI  : 2021-11-11 .. 2022-12-31
  2023-24 BOGA : 2023-01-01 .. 2024-12-31
  2025-26 SON  : 2025-01-01 .. bugun
  Ayrica her giris BTC-tabanli F10 etiketi (evren.btc_rejim mantiginin
  tarihsel kopyasi) ile de kirilir: TAM_BOGA / TEPKI_RALLISI / ...

WALK-FORWARD NOTU (durustluk): kuralda UYDURULAN parametre YOK (MA50/MA200/
  ATR14/2R hepsi konvansiyonel ve onceden sabit) -> optimize edilecek bir sey
  olmadigi icin klasik walk-forward'in anlami kalmiyor; onun yerine TUM
  donemler ayri ayri raporlanir, yani her donem zaten ornek-disi. Parametre
  arama yapilmadigi icin overfit kanali kapali.

BILINEN SINIRLAR (rapora yazilir):
  1. HAYATTA KALMA YANLILIGI: evren bugun yasayan buyuk altlardan secildi;
     2021'de olup bugun olmeyenler yok -> long lehine YUKARI yanli.
  2. Spot klines kullanildi; funding vekil bir varsayim (gercek gecmis degil).
  3. Botun kapilari (radar skoru, Pillar D, taker orani) gecmiste YOK ->
     bu test SAF ARKETIPI olcer, botun seciciligini degil.
  4. Slipaj yok (buyuk-cap gunluk giris, ihmal edilebilir kabul edildi).
============================================================================
"""
import json, os, sys, time, random, statistics as st
import urllib.request

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "klines_cache")
os.makedirs(CACHE, exist_ok=True)

SPOT = "https://api.binance.com/api/v3/klines"

# --- evren: bugun yasayan, 2021'den once Binance spot'ta olan buyuk altlar (SABIT liste)
SEMBOLLER = ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT", "LINK", "LTC",
             "AVAX", "ATOM", "UNI", "XLM", "TRX", "ETC", "FIL", "NEAR", "ALGO", "VET",
             "AAVE", "EOS", "MATIC", "ICP", "HBAR"]

DONEMLER = [("2020-21 BOGA", "2020-04-01", "2021-11-10"),
            ("2022 AYI",     "2021-11-11", "2022-12-31"),
            ("2023-24 BOGA", "2023-01-01", "2024-12-31"),
            ("2025-26 SON",  "2025-01-01", "2030-01-01")]

TAKER = 0.00045          # tek yon
FUNDING_GUNLUK = 0.0003  # %0.01/8s vekili
MAKS_GUN = 30
random.seed(42)


def indir(sym):
    """1d klines, 2019-01-01'den bugune. Diske onbellek (tekrar kosuda ag yok)."""
    yol = os.path.join(CACHE, f"{sym}USDT_1d.json")
    if os.path.exists(yol):
        return json.load(open(yol))
    out, bas = [], 1546300800000  # 2019-01-01
    while True:
        u = f"{SPOT}?symbol={sym}USDT&interval=1d&startTime={bas}&limit=1000"
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                d = json.loads(r.read())
        except Exception as e:
            print(f"  !! {sym}: {e}")
            break
        if not d:
            break
        out += d
        if len(d) < 1000:
            break
        bas = d[-1][0] + 86400000
        time.sleep(0.15)
    bars = [{"t": k[0], "gun": time.strftime("%Y-%m-%d", time.gmtime(k[0] / 1000)),
             "o": float(k[1]), "h": float(k[2]), "l": float(k[3]), "c": float(k[4])}
            for k in out]
    if bars:
        json.dump(bars, open(yol, "w"))
    return bars


def ma(vals, i, n):
    return st.mean(vals[i - n + 1:i + 1]) if i >= n - 1 else None


def atr14(bars, i):
    if i < 14:
        return None
    tr = []
    for j in range(i - 13, i + 1):
        p = bars[j - 1]["c"]
        tr.append(max(bars[j]["h"] - bars[j]["l"], abs(bars[j]["h"] - p), abs(p - bars[j]["l"])))
    return st.mean(tr)


def isle(bars, gi):
    """gi = giris bar indeksi (ertesi gunun acilisi). -> (R_brut, R_net, gun) veya None"""
    tetik = gi - 1
    a = atr14(bars, tetik)
    if a is None:
        return None
    dip5 = min(b["l"] for b in bars[max(0, tetik - 4):tetik + 1])
    giris = bars[gi]["o"]
    stop = dip5 - 0.25 * a
    if stop >= giris:
        return None
    risk = giris - stop
    hedef = giris + 2 * risk
    for j in range(gi, min(gi + MAKS_GUN, len(bars))):
        if bars[j]["l"] <= stop:                      # ayni gun ikisi de -> STOP (muhafazakar)
            cikis, gun = stop, j - gi + 1
            break
        if bars[j]["h"] >= hedef:
            cikis, gun = hedef, j - gi + 1
            break
    else:
        son = min(gi + MAKS_GUN, len(bars)) - 1
        if son <= gi:
            return None
        cikis, gun = bars[son]["c"], son - gi + 1
    brut = (cikis - giris) / risk
    maliyet = (giris * 2 * TAKER + giris * FUNDING_GUNLUK * gun) / risk
    return brut, brut - maliyet, gun


def sinyaller(bars):
    """F1 tetikleri -> giris bar indeksleri (ayni anda tek pozisyon)."""
    cl = [b["c"] for b in bars]
    out, mesgul_bitis = [], -1
    for i in range(200, len(bars) - 1):
        if i <= mesgul_bitis:
            continue
        m50, m200 = ma(cl, i, 50), ma(cl, i, 200)
        if not m50 or not m200:
            continue
        if not (cl[i] > m200 and m50 > m200):
            continue
        if not (bars[i]["l"] <= m50 and cl[i] > m50):
            continue
        out.append(i + 1)
        mesgul_bitis = i + MAKS_GUN
    return out


def f10_etiket(btc, i):
    """evren.btc_rejim mantiginin TARIHSEL kopyasi (haftalik SEZON x gunluk HAVA)."""
    cl = [b["c"] for b in btc]
    if i < 200:
        return "?"
    hafta = [cl[j] for j in range(i, -1, -7)][::-1]      # i'den geriye 7 gunluk kapanislar
    if len(hafta) < 21:
        return "?"
    w_ort = st.mean(hafta[-21:-1])
    w_egim = hafta[-1] - hafta[-21]
    sezon = "BOGA" if (hafta[-1] > w_ort and w_egim > 0) else ("AYI" if (hafta[-1] < w_ort and w_egim < 0) else "NOTR")
    ham = []
    for j in range(i - 19, i + 1):
        sma = st.mean(cl[j - 20:j])
        uz = (cl[j] - sma) / sma * 100
        ham.append("NOTR" if abs(uz) < 2.0 else ("BOGA" if uz > 0 else "AYI"))
    hava = ham[0]
    for j in range(len(ham)):
        pen = ham[max(0, j - 2):j + 1]
        if len(pen) == 3 and all(x == pen[0] for x in pen):
            hava = pen[0]
    return {("AYI", "BOGA"): "TEPKI_RALLISI", ("BOGA", "BOGA"): "TAM_BOGA",
            ("AYI", "AYI"): "DERIN_AYI", ("BOGA", "AYI"): "BOGA_DUZELTME"}.get((sezon, hava), "BELIRSIZ")


def donem(gun):
    for ad, b, s in DONEMLER:
        if b <= gun <= s:
            return ad
    return "ONCESI"


def ozet(ad, kayitlar):
    if not kayitlar:
        print(f"  {ad:16} N=0")
        return
    net = [k["r_net"] for k in kayitlar]
    kaz = [x for x in net if x > 0]
    sh = (st.pstdev(net) / len(net) ** 0.5) if len(net) > 1 else 0.0   # ortalamanin standart hatasi
    print(f"  {ad:16} N={len(net):4d}  kazanma %{len(kaz)/len(net)*100:4.0f}  "
          f"ort R_net {st.mean(net):+.3f} ±{sh:.3f}  medyan {st.median(net):+.3f}  "
          f"toplam {sum(net):+7.1f}R  (brut {st.mean([k['r_brut'] for k in kayitlar]):+.3f})")


def main():
    print(__doc__.split("=" * 76)[1][:0] or "", end="")
    print("Veri indiriliyor / onbellekten okunuyor...")
    veri = {}
    for s in SEMBOLLER:
        b = indir(s)
        if len(b) > 300:
            veri[s] = b
        else:
            print(f"  atlandi: {s} (veri yok/yetersiz)")
    print(f"Evren: {len(veri)} sembol\n")

    btc = veri["BTC"]
    btc_idx = {b["gun"]: i for i, b in enumerate(btc)}
    f10_cache = {}

    gercek, kontrol = [], []
    for sym, bars in veri.items():
        gunler = [b["gun"] for b in bars]
        for gi in sinyaller(bars):
            r = isle(bars, gi)
            if not r:
                continue
            g = gunler[gi]
            bi = btc_idx.get(g)
            if bi is not None and bi not in f10_cache:
                f10_cache[bi] = f10_etiket(btc, bi)
            gercek.append({"sym": sym, "gun": g, "donem": donem(g),
                           "f10": f10_cache.get(bi, "?"),
                           "r_brut": r[0], "r_net": r[1], "tut": r[2]})
            # --- eslesmis KONTROL: ayni sembol, ±60 gun icinde rastgele bir gun
            for _ in range(6):
                ki = gi + random.randint(-60, 60)
                if 201 <= ki < len(bars) - 1:
                    kr = isle(bars, ki)
                    if kr:
                        kg = gunler[ki]
                        kbi = btc_idx.get(kg)
                        if kbi is not None and kbi not in f10_cache:
                            f10_cache[kbi] = f10_etiket(btc, kbi)
                        kontrol.append({"sym": sym, "gun": kg, "donem": donem(kg),
                                        "f10": f10_cache.get(kbi, "?"),
                                        "r_brut": kr[0], "r_net": kr[1], "tut": kr[2]})
                        break

    print(f"F1 GERCEK sinyal: {len(gercek)}   |   KONTROL (rastgele): {len(kontrol)}\n")
    print("=== DONEM KIRILIMI — F1 trend-pullback (net, maliyet dahil) ===")
    for ad, _, _ in DONEMLER:
        ozet(ad, [k for k in gercek if k["donem"] == ad])
    print("\n=== AYNI DONEMLER — KONTROL grubu (rastgele giris, ayni mekanik) ===")
    for ad, _, _ in DONEMLER:
        ozet(ad, [k for k in kontrol if k["donem"] == ad])

    print("\n=== F10 REJIM KIRILIMI (BTC tabanli, giris gunu etiketi) ===")
    for et in ("TAM_BOGA", "BOGA_DUZELTME", "TEPKI_RALLISI", "DERIN_AYI", "BELIRSIZ"):
        ozet("F1 " + et, [k for k in gercek if k["f10"] == et])
        ozet("   kontrol", [k for k in kontrol if k["f10"] == et])

    print("\n=== TOPLAM ===")
    ozet("F1 hepsi", gercek)
    ozet("KONTROL", kontrol)
    tut = [k["tut"] for k in gercek]
    print(f"\n  ort tutma: {st.mean(tut):.1f} gun | sembol basi ort sinyal: "
          f"{len(gercek)/len(veri):.1f}")

    json.dump(gercek, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "boga_bacagi_islemler.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
