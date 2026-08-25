# -*- coding: utf-8 -*-
"""OLAY SEVIYESI ORNEKLEME — YONTEM GOSTERIMI (hukum yazilmaz).

SORU: "7 gun yatay gitmis, sonra sicramis" durumu 2 yilda kac kere oldu?
   A) PIYASA-TAKVIM seviyesinde say  (kullanicinin baktigi bicim)
   B) SEMBOL-OLAY seviyesinde say    (onerilen bicim)
Ardindan B'nin uzerinde KONTROL GRUBU + GUN-KUMELI istatistik.

Esikler kalibre.py dagilimlarindan secildi (alt ~%30 dilim), sonuca BAKMADAN.
   SAKIN   : |7 gunluk getiri| <= %5   VE  168sa saatlik std <= %0.80
   SICRAMA : tek saatlik getiri >= +%5   (saatlerin %0,525'i)
SALT OKUMA.
"""
import json, glob, os, math, datetime, bisect

PROJE = r"c:\Users\alper\Desktop\kripto trade"
KL = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
ENDEKS = os.path.join(PROJE, "scratchpad", "poz_yol", "endeks_gunluk.json")

YATAY_ESIK = 5.0
STD_ESIK = 0.80
SICRAMA = 5.0
UFUKLAR = (4, 24, 72)
BEKLEME = 24          # ayni sembolde 24 bar icinde ikinci olay sayilmaz (ortusme)

# ---------------------------------------------------------------- A) PIYASA
print("=" * 78)
print("A) PIYASA-TAKVIM SEVIYESI  —  'butun piyasa yatay, sonra ralli'")
print("=" * 78)
end = json.load(open(ENDEKS, encoding="utf-8"))
end.sort(key=lambda x: x["gun"])
ag = [x.get("alt_get") or 0.0 for x in end]
gun = [x["gun"] for x in end]
piyasa_olay = []
for i in range(7, len(ag) - 3):
    onceki7 = sum(ag[i-7:i])
    sonraki3 = sum(ag[i:i+3])
    if abs(onceki7) <= YATAY_ESIK and sonraki3 >= 10.0:
        piyasa_olay.append((gun[i], onceki7, sonraki3))
print("gun sayisi taranan            : %d  (%s .. %s)" % (len(ag), gun[0], gun[-1]))
print("olcut: onceki 7 gun toplam |getiri| <= %%%.0f  VE  sonraki 3 gun >= +%%10" % YATAY_ESIK)
print()
print(">>> BULUNAN OLAY SAYISI : %d" % len(piyasa_olay))
for g, o, s in piyasa_olay:
    print("      %s   onceki7 %+6.2f%%   sonraki3 %+6.2f%%" % (g, o, s))
print()
print("    N=%d ile hicbir istatistik kurulamaz. Kullanicinin tespiti DOGRU." % len(piyasa_olay))

# ---------------------------------------------------------------- BTC rejim
btc_dd = {}
for ad in ("BTC.json", "BTCUSDT.json", "BTCDOM.json"):
    y = os.path.join(KL, ad)
    if os.path.exists(y) and ad.startswith("BTC.") or (os.path.exists(y) and ad == "BTCUSDT.json"):
        b = json.load(open(y, encoding="utf-8"))
        z = 0.0
        for x in b:
            z = max(z, x["h"])
            dd = (x["c"] - z) / z * 100 if z else 0.0
            btc_dd[x["t"]] = ("ATH_BOLGESI" if dd > -10 else
                              "DUZELTME" if dd > -30 else "DERIN_AYI")
        break
btc_ts = sorted(btc_dd)
def rejim(t):
    if not btc_ts:
        return "?"
    i = bisect.bisect_right(btc_ts, t) - 1
    return btc_dd[btc_ts[i]] if i >= 0 else "?"

# ---------------------------------------------------------------- B) SEMBOL-OLAY
print()
print("=" * 78)
print("B) SEMBOL-OLAY SEVIYESI  —  ayni durum, coin bazinda")
print("=" * 78)

olaylar, kontrol = [], []
tar_sembol = 0
tar_bar = 0
ham_olay = 0

for f in sorted(glob.glob(os.path.join(KL, "*.json"))):
    sym = os.path.basename(f)[:-5]
    try:
        b = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    if len(b) < 300:
        continue
    tar_sembol += 1
    tar_bar += len(b)
    c = [x["c"] for x in b]
    t = [x["t"] for x in b]
    n = len(c)
    r = [0.0] * n
    for i in range(1, n):
        r[i] = (c[i] / c[i-1] - 1) * 100 if c[i-1] > 0 else 0.0
    # 168 barlik kayan toplam / kare toplam
    s = sum(r[1:169]); s2 = sum(v * v for v in r[1:169])
    son_olay = -10**9
    for i in range(169, n - max(UFUKLAR)):
        if i > 169:
            cik = r[i-169]; gir = r[i-1]
            s += gir - cik; s2 += gir * gir - cik * cik
        if r[i] < SICRAMA or c[i] <= 0 or c[i-169] <= 0:
            continue
        ham_olay += 1
        if i - son_olay < BEKLEME:
            continue
        ort = s / 168.0
        var = max(s2 / 168.0 - ort * ort, 0.0)
        std = math.sqrt(var)
        g7 = (c[i-1] / c[i-169] - 1) * 100
        sakin = abs(g7) <= YATAY_ESIK and std <= STD_ESIK
        ileri = {}
        ok = True
        for h in UFUKLAR:
            if i + h >= n or c[i] <= 0:
                ok = False; break
            ileri["f%d" % h] = (c[i+h] / c[i] - 1) * 100
        if not ok:
            continue
        kayit = {"sym": sym, "t": t[i], "g7": g7, "std": std, "sic": r[i],
                 "rejim": rejim(t[i])}
        kayit.update(ileri)
        (olaylar if sakin else kontrol).append(kayit)
        son_olay = i

print("taranan sembol : %d" % tar_sembol)
print("taranan bar    : %s" % format(tar_bar, ","))
print("ham sicrama    : %s  (>= +%%%.0f, tek saat)" % (format(ham_olay, ","), SICRAMA))
print()
print(">>> OLAY  (sicrama + onu SAKIN)      : %s" % format(len(olaylar), ","))
print(">>> KONTROL (sicrama + onu sakin DEGIL): %s" % format(len(kontrol), ","))
print("    (ayni sembolde %d bar bekleme uygulandi — ortusen pencereler elendi)" % BEKLEME)

gunler = sorted(set(datetime.datetime.utcfromtimestamp(x["t"]/1000).strftime("%Y-%m-%d") for x in olaylar))
semboller = len(set(x["sym"] for x in olaylar))
print("    bagimsiz GUN sayisi : %d      farkli SEMBOL : %d" % (len(gunler), semboller))

json.dump({"olay": olaylar, "kontrol": kontrol},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "olaylar.json"), "w"))
print("\n(olaylar gecici klasore yazildi — proje dosyalarina DOKUNULMADI)")
