#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REJIM KAPISI — ALFA REJIME BAGLI MI?

ON_KAYIT_rejim_kapisi.md · commit ee67fb6 — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

🔴 LOOK-AHEAD YASAK: her kapi t-1 KAPANISIYLA hesaplanir.
SALT-OKUNUR. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, sys, math, collections, statistics as stx
import datetime as dt

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)
import importlib.util as il
sp = il.spec_from_file_location(
    "ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)

PYL = os.path.join(KOK, "piyasa_yapisi_log.jsonl")
T_ESIK = 2.5
MIN_GUN = 20
BAR_BTC = 0.88          # on-kayit bolum 1


def btc_gunluk():
    d = json.load(open(os.path.join(KOK, "scratchpad", "klines_1h_uzun", "BTC.json"),
                       encoding="utf-8"))
    g = {}
    for x in d:
        k = dt.datetime.fromtimestamp(x["t"] / 1000, dt.UTC).date().isoformat()
        g[k] = x["c"]
    gs = sorted(g)
    return gs, g


def kapilar(gs, g, btcd):
    """t gunu icin, t-1 KAPANISIYLA hesaplanir. -> {kapi: {gun: bool}}"""
    kap = collections.defaultdict(dict)
    kapanis = [g[k] for k in gs]
    for i in range(50, len(gs)):
        gun = gs[i]
        onceki = kapanis[:i]           # t-1'e kadar, t DAHIL DEGIL
        c = onceki[-1]
        sma20 = stx.mean(onceki[-20:])
        sma50 = stx.mean(onceki[-50:])
        mom7 = (onceki[-1] / onceki[-8] - 1) * 100 if len(onceki) >= 8 else 0.0
        rets = [(onceki[j] / onceki[j - 1] - 1) * 100 for j in range(len(onceki) - 20, len(onceki))]
        vol20 = stx.pstdev(rets) if len(rets) > 1 else 0.0
        kap["K1 btc>sma20"][gun] = c > sma20
        kap["K2 btc>sma50"][gun] = c > sma50
        kap["K3 btc_mom7>0"][gun] = mom7 > 0
        kap["_vol20"][gun] = vol20
    # K4: vol20 kendi medyaninin ALTINDA (medyan TUM pencereden — teshis amacli,
    #     nedensel degil; bu yuzden ayrica GENISLEYEN medyanla da hesaplanir)
    vv = sorted(kap["_vol20"].values())
    med = vv[len(vv) // 2] if vv else 0
    gecmis = []
    for gun in sorted(kap["_vol20"]):
        v = kap["_vol20"][gun]
        m = stx.median(gecmis) if len(gecmis) >= 20 else med
        kap["K4 btc_sakin"][gun] = v < m          # GENISLEYEN medyan -> nedensel
        gecmis.append(v)
    del kap["_vol20"]
    # K7: BOTUN KENDI dedektoru — evren.btc_rejim() nedensel yeniden uretimi
    #     (scratchpad/rejim_gecis_sayim.py:rejim_serisi, CLAUDE.md: canli
    #     etiketle birebir uyustugu dogrulanmis).
    #     🔴 radar_archive.rejim alani OKUNMAZ (2026-07-22 tanim degisikligi).
    #     Kapi t gunu icin t-1'in etiketiyle kurulur -> LOOK-AHEAD YOK.
    try:
        sp7 = il.spec_from_file_location(
            "rg", os.path.join(KOK, "scratchpad", "rejim_gecis_sayim.py"))
        rg = il.module_from_spec(sp7)
        sp7.loader.exec_module(rg)
        bars = json.load(open(os.path.join(KOK, "scratchpad", "klines_1h_uzun",
                                           "BTC.json"), encoding="utf-8"))
        seri = rg.rejim_serisi(bars)
        etiket = {x["gun"].date().isoformat(): x["f10"] for x in seri}
        eg = sorted(etiket)
        for i in range(1, len(eg)):
            kap["K7 bot_rejimi"][eg[i]] = etiket[eg[i - 1]] in ("TAM_BOGA", "TEPKI_RALLISI")
    except Exception as ex:
        print("   ⚠️ K7 hesaplanamadi: %s" % str(ex)[:120])
    # K5/K6: btc_d ve usdt_d 3 gunluk degisim (t-1 ve t-4 kayitlariyla)
    for ad, alan in (("K5 btcd_dusuyor", "btc_d"), ("K6 usdtd_dusuyor", "usdt_d")):
        seri = sorted(btcd.get(alan, {}).items())
        harita = dict(seri)
        gunl = [x[0] for x in seri]
        for i, gun in enumerate(gunl):
            if i < 4:
                continue
            onc, esk = harita[gunl[i - 1]], harita[gunl[i - 4]]
            kap[ad][gun] = (onc - esk) < 0
    return kap


def piyasa_yapisi():
    out = {"btc_d": {}, "usdt_d": {}}
    if not os.path.exists(PYL):
        return out
    for l in open(PYL, encoding="utf-8", errors="ignore"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        g = (r.get("ts") or "")[:10]
        for k in ("btc_d", "usdt_d"):
            if r.get(k) is not None:
                out[k][g] = r[k]        # gunun SON kaydi kalir
    return out


def regres(x, y):
    n = len(x)
    if n < 5:
        return 0.0, 0.0, 0.0
    mx, my = stx.mean(x), stx.mean(y)
    sxx = sum((a - mx) ** 2 for a in x)
    if sxx == 0:
        return my, 0.0, 0.0
    beta = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx
    alfa = my - beta * mx
    art = [b - (alfa + beta * a) for a, b in zip(x, y)]
    if n > 2:
        s = math.sqrt(sum(e * e for e in art) / (n - 2))
        se_a = s * math.sqrt(1.0 / n + mx * mx / sxx)
        t_a = alfa / se_a if se_a else 0.0
    else:
        t_a = 0.0
    return alfa, beta, t_a


def main():
    print("=" * 104)
    print("REJIM KAPISI — ON_KAYIT_rejim_kapisi.md (ee67fb6)")
    print("🔴 Bolum 1: alfa sabit kalirsa HICBIR kapi yetmez (bar %0,88/gun = BTC ort.nin 12,6 kati)")
    print("   -> olculen soru: ALFA rejime bagli mi? (R4 belirleyici)")
    print("=" * 104)

    mum = ar.mumlar()
    rows = ar.veri_kur(mum)
    gunR = collections.defaultdict(list)
    for x in rows:
        gunR[x["gun"]].append(x["R"])
    gunR = {g: stx.mean(v) for g, v in gunR.items() if len(v) >= 5}

    gs, g = btc_gunluk()
    btcret = {}
    for i in range(1, len(gs)):
        btcret[gs[i]] = (g[gs[i]] / g[gs[i - 1]] - 1) * 100
    kap = kapilar(gs, g, piyasa_yapisi())

    ortak = sorted(set(gunR) & set(btcret))
    print("bot gunu %d · BTC ile ortak %d gun (%s .. %s)"
          % (len(gunR), len(ortak), ortak[0], ortak[-1]))
    ax, ay = [btcret[d] for d in ortak], [gunR[d] for d in ortak]
    a0, b0, t0 = regres(ax, ay)
    print("TABAN (kapisiz): ort R %+.4f · ALFA %+.4f (t %+.2f) · BETA %+.4f"
          % (stx.mean(ay), a0, t0, b0))
    print()

    print("%-20s %5s %5s %9s %9s %10s %8s %8s %9s %8s"
          % ("kapi", "acik", "kapal", "R acik", "R kapali", "fark", "t", "MDE",
             "ALFA acik", "t_alfa"))
    sonuc = {}
    for ad in sorted(kap):
        h = kap[ad]
        ac = [d for d in ortak if h.get(d) is True]
        ka = [d for d in ortak if h.get(d) is False]
        if len(ac) < 3 or len(ka) < 3:
            print("%-20s  yetersiz (acik %d · kapali %d)" % (ad, len(ac), len(ka)))
            continue
        ra = [gunR[d] for d in ac]
        rk = [gunR[d] for d in ka]
        fark = stx.mean(ra) - stx.mean(rk)
        se = math.sqrt(stx.variance(ra) / len(ra) + stx.variance(rk) / len(rk))
        t = fark / se if se else 0.0
        mde = 2.8 * se
        alfa, beta, t_alfa = regres([btcret[d] for d in ac], ra)
        sonuc[ad] = {"ac": ac, "ka": ka, "Ra": stx.mean(ra), "Rk": stx.mean(rk),
                     "fark": fark, "t": t, "mde": mde, "alfa": alfa,
                     "beta": beta, "t_alfa": t_alfa,
                     "btc_ort": stx.mean([btcret[d] for d in ac])}
        print("%-20s %5d %5d %+9.4f %+9.4f %+10.4f %+8.2f %8.4f %+9.4f %+8.2f"
              % (ad, len(ac), len(ka), stx.mean(ra), stx.mean(rk), fark, t, mde,
                 alfa, t_alfa))
    print()

    print("### TESHIS (olcut degil) — kapi acikken ortalama BTC getirisi vs BAR %%%.2f" % BAR_BTC)
    for ad, s in sorted(sonuc.items()):
        print("   %-20s BTC ort %+7.3f%%   bar farki %+7.3f puan"
              % (ad, s["btc_ort"], s["btc_ort"] - BAR_BTC))
    print()

    print("=" * 104)
    print("HUKUM — ON_KAYIT bolum 5")
    print("=" * 104)
    print("   %-20s %-7s %-7s %-7s %-7s %-7s  %s"
          % ("kapi", "R1", "R2", "R3", "R4", "R5", "SONUC"))
    gecen = []
    for ad, s in sorted(sonuc.items()):
        R1 = s["Ra"] > 0
        R2 = s["t"] >= T_ESIK
        R3 = abs(s["fark"]) > s["mde"]
        R4 = s["alfa"] >= 0
        R5 = len(s["ac"]) >= MIN_GUN and len(s["ka"]) >= MIN_GUN
        hep = R1 and R2 and R3 and R4 and R5
        if hep:
            gecen.append(ad)
        son = ("🔑 ISE YARAR" if hep else
               ("BOS" if not (R1 and R4) else "GOREMIYORUZ"))
        print("   %-20s %-7s %-7s %-7s %-7s %-7s  %s"
              % (ad, "OK" if R1 else "-", "OK" if R2 else "-", "OK" if R3 else "-",
                 "OK" if R4 else "-", "OK" if R5 else "-", son))
    print()
    if gecen:
        print("   ISE YARAYAN: %s" % ", ".join(gecen))
        print("   🔴 Bota KONMAZ — once portfoy simulasyonu (on-kayit bolum 8).")
    else:
        print("   HICBIR KAPI GECMEDI.")
        pozitif_alfa = [a for a, s in sonuc.items() if s["alfa"] >= 0]
        print("   ALFA >= 0 olan kapi: %s" % (", ".join(pozitif_alfa) if pozitif_alfa else "YOK"))
        print("   -> Bolum 1'in aritmetigi BAGLAYICI hale gelir:")
        print("      kar BETADAN geliyor, SECIMDEN degil.")
    print()
    print("Salt-okuma. Look-ahead yok (kapilar t-1 kapanisiyla). Bota yazim: YOK")


if __name__ == "__main__":
    main()
