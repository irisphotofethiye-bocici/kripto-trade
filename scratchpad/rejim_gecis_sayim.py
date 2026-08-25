#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REJIM SERISI YENIDEN URETIMI + GECIS SAYIMI (on-kayit ONCESI, tasarim icin).

Bu betik HENUZ SONUC OLCMEZ. Yalnizca:
  1) evren.btc_rejim()'i 2 yillik BTC 1h mumundan BIREBIR yeniden uretir
  2) DOGRULAMA: bugunku etiket botun canli etiketiyle ayni mi
  3) NOTR->BOGA gecislerini SAYAR (on-kayitta N ve olcut belirlemek icin)

Gecis SAYISI bir sonuc degil, ORNEKLEM BUYUKLUGUdur; on-kayittan once
bilinmesi gerekir (yoksa olcut uydurulmus olur).
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, datetime, statistics, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KL = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
OLU_BANT = 2.0      # esikler.f10_olu_bant_pct
HISTEREZIS = 3      # esikler.f10_histerezis_gun


def saatlik(sym):
    with open(os.path.join(KL, sym + ".json"), encoding="utf-8") as f:
        return json.load(f)


def gunluk(bars):
    """1h -> gunluk kapanis (UTC gun sonu). Donus: [(gun_datetime, kapanis)]"""
    g = {}
    for b in bars:
        t = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(b["t"]))
        g[t.date()] = float(b["c"])        # ayni gunun SON barinin kapanisi
    return [(datetime.datetime.combine(d, datetime.time()), c) for d, c in sorted(g.items())]


def haftalik(gunler):
    """gunluk -> haftalik kapanis (ISO hafta sonu)."""
    h = {}
    for d, c in gunler:
        h[d.isocalendar()[:2]] = (d, c)
    return [v for k, v in sorted(h.items())]


def rejim_serisi(bars):
    """evren.btc_rejim() mantigini gun gun yeniden uretir.
    Her gun icin YALNIZ o gune kadarki veri kullanilir (nedensel)."""
    G = gunluk(bars)
    out = []
    for i in range(len(G)):
        # --- SEZON: haftalik kapanis vs son 20 KAPALI hafta ort + egim
        H = haftalik(G[:i + 1])
        wc = [c for d, c in H]
        sezon = "?"
        if len(wc) >= 21:
            w_ort = statistics.mean(wc[-21:-1])
            w_egim = wc[-1] - wc[-21]
            if wc[-1] > w_ort and w_egim > 0:
                sezon = "BOGA"
            elif wc[-1] < w_ort and w_egim < 0:
                sezon = "AYI"
            else:
                sezon = "NOTR"
        # --- HAVA: gunluk SMA20 + olu bant + histerezis
        cl = [c for d, c in G[max(0, i - 59):i + 1]]      # evren limit=40 gun okur; 60 yeter
        ham = []
        for j in range(20, len(cl)):
            sma = statistics.mean(cl[j - 20:j])
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
        # --- capraz
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
        rejim = "BOGA" if f10 == "TAM_BOGA" else ("AYI" if f10 in ("TEPKI_RALLISI", "DERIN_AYI") else "NOTR")
        out.append(dict(gun=G[i][0], kapanis=G[i][1], sezon=sezon, hava=hava,
                        f10=f10, rejim=rejim))
    return out


bars = saatlik("BTC")
S = rejim_serisi(bars)
S = [x for x in S if x["sezon"] != "?"]        # ilk 21 hafta isinma

print("REJIM SERISI — 2 yillik BTC 1h mumundan yeniden uretildi")
print("pencere %s .. %s   (%d gun)"
      % (S[0]["gun"].strftime("%Y-%m-%d"), S[-1]["gun"].strftime("%Y-%m-%d"), len(S)))
print("=" * 100)

print("\n1) DOGRULAMA — bugunku etiket botunkiyle ayni mi")
print("-" * 100)
son = S[-1]
print("   yeniden uretim : %s  (f10=%s · sezon=%s · hava=%s · BTC %.0f)"
      % (son["rejim"], son["f10"], son["sezon"], son["hava"], son["kapanis"]))
ra = os.path.join(PROJE, "radar_active.json")
if os.path.exists(ra):
    d = json.load(open(ra, encoding="utf-8"))
    r = d.get("rejim")
    print("   botun canli etiketi: %s" % (json.dumps(r, ensure_ascii=False)[:200] if r else "yok"))
    print("   radar guncelleme   : %s" % d.get("guncelleme"))

print("\n2) REJIM DAGILIMI (2 yil)")
print("-" * 100)
for k, n in collections.Counter(x["rejim"] for x in S).most_common():
    print("   %-8s %4d gun  (%%%.1f)" % (k, n, 100.0 * n / len(S)))
print("   F10 kirilimi:")
for k, n in collections.Counter(x["f10"] for x in S).most_common():
    print("      %-16s %4d gun  (%%%.1f)" % (k, n, 100.0 * n / len(S)))

print("\n3) GECISLER — ORNEKLEM BUYUKLUGU (on-kayit icin)")
print("-" * 100)
gecis = collections.defaultdict(list)
for i in range(1, len(S)):
    a, b = S[i - 1]["rejim"], S[i]["rejim"]
    if a != b:
        gecis["%s->%s" % (a, b)].append(S[i])
for k in sorted(gecis, key=lambda z: -len(gecis[z])):
    print("   %-14s %3d kez" % (k, len(gecis[k])))

print("\n   NOTR->BOGA gecis tarihleri:")
nb = gecis.get("NOTR->BOGA", [])
for x in nb:
    print("      %s   BTC %8.0f" % (x["gun"].strftime("%Y-%m-%d"), x["kapanis"]))
print("   -> NOTR->BOGA gecis sayisi: %d" % len(nb))

print("\n   BOGA'ya TUM girisler (NOTR->BOGA + AYI->BOGA):")
tum_boga = sorted(gecis.get("NOTR->BOGA", []) + gecis.get("AYI->BOGA", []),
                  key=lambda z: z["gun"])
for x in tum_boga:
    print("      %s   BTC %8.0f   (onceki rejim %s)"
          % (x["gun"].strftime("%Y-%m-%d"), x["kapanis"],
             "NOTR" if x in gecis.get("NOTR->BOGA", []) else "AYI"))
print("   -> toplam %d giris" % len(tum_boga))

print("\n4) BOGA EPIZODLARININ UZUNLUGU (kac gun surdu)")
print("-" * 100)
i = 0
epiz = []
while i < len(S):
    if S[i]["rejim"] == "BOGA":
        j = i
        while j < len(S) and S[j]["rejim"] == "BOGA":
            j += 1
        epiz.append((S[i]["gun"], j - i, S[i]["kapanis"], S[j - 1]["kapanis"]))
        i = j
    else:
        i += 1
for g, n, c0, c1 in epiz:
    print("   %s  %3d gun   BTC %8.0f -> %8.0f  (%+.1f%%)"
          % (g.strftime("%Y-%m-%d"), n, c0, c1, 100.0 * (c1 / c0 - 1)))
print("   -> %d epizod, medyan uzunluk %s gun"
      % (len(epiz), statistics.median([n for g, n, a, b in epiz]) if epiz else "-"))

print("\n5) SON 30 GUN — gun gun (mevcut gecis nerede)")
print("-" * 100)
for x in S[-30:]:
    print("   %s  BTC %8.0f  sezon %-5s hava %-5s  %-14s -> %s"
          % (x["gun"].strftime("%m-%d"), x["kapanis"], x["sezon"], x["hava"], x["f10"], x["rejim"]))

print("\nSALT OKUMA — sonuc OLCULMEDI, yalnizca ornekelem tasarimi.")
