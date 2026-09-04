#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NOTR'da SHORT — HAM ileri getiri (mekaniksiz). Asama 1, simetrik tamamlayici.
On-kayit: ON_KAYIT_notr_short_ham.md (commit 107b2e4, KOSUMDAN ONCE). Olcutler SABIT.

Yontem `boga_long_ham.py` ile BIREBIR ayni; tek fark rejim=NOTR, yon=SHORT.
Birincil hucre ONCEDEN atandi: A+B kolu, H=4 saat.
MA50 kolu BETIMLEYICI — besinci kez olculuyor, hukum TASIMAZ.

🔴 BIRIM = SEMBOL-GUN + GUN KUMELI t ZORUNLU (onceki olcumun dersi).
🔴 ZAMAN DILIMI SINAMASI: %90 altiysa betik REDDEDER.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, time, math, datetime, statistics, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJE not in _sys.path:
    _sys.path.insert(0, PROJE)
import evren

ARSIV = os.path.join(PROJE, "testbot_aday_arsiv.jsonl")
ONBELLEK = os.path.join(PROJE, "scratchpad", "aday_pencere_1h")
CFG = json.load(open(os.path.join(PROJE, "kripto-config.json"), encoding="utf-8"))
E = CFG.get("esikler", {})

AB_FUND = float(E.get("ab_funding_esik", -0.05))
AB_OI24 = float(E.get("ab_oi24_esik", 10.0))
UCUZ = float(E.get("ucuz_fiyat_esik", 0.07))
MA50_ESIK = float(E.get("ma50_mesafe_esik", 3.72))

YEREL_FARK = 3
SAAT_MS = 3600 * 1000
H_SAAT = [1, 4, 12, 24]
BIRINCIL_H = 4
BAS, BIT = "2026-08-03", "2026-09-05"
TZ_ASGARI = 0.90
YON = -1                      # SHORT


def utc_ts(s):
    d = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M") - datetime.timedelta(hours=YEREL_FARK)
    return int((d - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)


def mum_cek(sym):
    os.makedirs(ONBELLEK, exist_ok=True)
    yol = os.path.join(ONBELLEK, "%s.json" % sym)
    if os.path.exists(yol):
        try:
            d = json.load(open(yol))
            if d:
                return d
        except Exception:
            pass
    e0 = datetime.datetime(1970, 1, 1)
    bas = int((datetime.datetime.strptime(BAS, "%Y-%m-%d") - e0).total_seconds() * 1000)
    bit = int((datetime.datetime.strptime(BIT, "%Y-%m-%d") - e0).total_seconds() * 1000)
    bar, imlec = [], bas
    while imlec < bit:
        u = ("https://fapi.binance.com/fapi/v1/klines?symbol=%sUSDT&interval=1h"
             "&startTime=%d&endTime=%d&limit=500" % (sym, imlec, bit))
        try:
            k = evren.get(u)
        except Exception:
            return None
        if not k:
            break
        bar.extend([[int(b[0]), float(b[2]), float(b[3]), float(b[4])] for b in k])
        yeni = int(k[-1][0]) + SAAT_MS
        if yeni <= imlec:
            break
        imlec = yeni
        time.sleep(0.10)
        if len(k) < 500:
            break
    if len(bar) < 100:
        return None
    bar = sorted({b[0]: b for b in bar}.values(), key=lambda z: z[0])
    json.dump(bar, open(yol, "w"))
    return bar


def t_ist(v):
    if len(v) < 3:
        return (sum(v) / len(v) if v else None), None, len(v), None
    m, sd = sum(v) / len(v), statistics.stdev(v)
    se = sd / math.sqrt(len(v))
    return m, (m / se if se else None), len(v), (2.0 * se if se else None)


def iki_ornek_t(a, b):
    if len(a) < 3 or len(b) < 3:
        return None, None
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    se = math.sqrt(statistics.variance(a) / len(a) + statistics.variance(b) / len(b))
    return (ma - mb), ((ma - mb) / se if se else None)


def main():
    print("NOTR'da SHORT — HAM ileri getiri (mekaniksiz, Asama 1)")
    print("on-kayit ON_KAYIT_notr_short_ham.md (107b2e4) · olcutler SABIT")
    print("=" * 106)
    print("birincil: A+B kolu · H=%d saat · birim SEMBOL-GUN · yon SHORT" % BIRINCIL_H)
    print("esikler config'ten OKUNDU: funding<=%.2f · oi24>=%.1f · fiyat<=%.2f · ma50>=%.2f"
          % (AB_FUND, AB_OI24, UCUZ, MA50_ESIK))

    satir = []
    for l in open(ARSIV, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        if str(r.get("rejim") or "").upper().startswith("NOTR") and r.get("sym") and r.get("ts") \
                and r.get("price"):
            satir.append(r)
    print("\nNOTR aday satiri: %d · sembol %d"
          % (len(satir), len({r["sym"] for r in satir})))

    semboller = sorted({r["sym"] for r in satir})
    mum, yok = {}, []
    for i, s in enumerate(semboller):
        if (i + 1) % 50 == 0:
            print("  mum ... %d/%d" % (i + 1, len(semboller)))
        b = mum_cek(s)
        if b:
            mum[s] = (b, {x[0]: j for j, x in enumerate(b)})
        else:
            yok.append(s)
    print("  mum bulunan %d · bulunamayan %d" % (len(mum), len(yok)))

    ic = dis = 0
    for r in satir:
        m = mum.get(r["sym"])
        if not m:
            continue
        bar, ix = m
        t0 = utc_ts(r["ts"])
        j = ix.get(t0 - (t0 % SAAT_MS))
        if j is None:
            continue
        _, hi, lo, _ = bar[j]
        if lo <= float(r["price"]) <= hi:
            ic += 1
        else:
            dis += 1
    oran = ic / (ic + dis) if (ic + dis) else 0.0
    print("\nZAMAN DILIMI SINAMASI: icinde %d · disinda %d -> %%%.1f" % (ic, dis, 100 * oran))
    if oran < TZ_ASGARI:
        print("  %%%.0f ALTINDA — BETIK REDDEDIYOR." % (100 * TZ_ASGARI))
        raise SystemExit(1)
    print("  -> GECTI")

    def ret(r, h):
        m = mum.get(r["sym"])
        if not m:
            return None
        bar, ix = m
        t0 = utc_ts(r["ts"])
        a = ix.get(t0 - (t0 % SAAT_MS))
        b = ix.get(t0 - (t0 % SAAT_MS) + h * SAAT_MS)
        if a is None or b is None:
            return None
        e, x = bar[a][3], bar[b][3]
        return (YON * (x - e) / e * 100.0) if e > 0 else None

    def ab(r):
        return (r.get("funding") is not None and float(r["funding"]) <= AB_FUND
                and (r.get("oi24") or 0) >= AB_OI24)

    def ma50(r):
        return (r.get("ma50_mesafe") is not None and r.get("price")
                and float(r["price"]) <= UCUZ and float(r["ma50_mesafe"]) >= MA50_ESIK)

    KOL = [("A+B", ab), ("MA50", ma50), ("TABAN", lambda r: True)]

    def topla(sec, h):
        sg = collections.defaultdict(list)
        for r in satir:
            if not sec(r):
                continue
            v = ret(r, h)
            if v is not None:
                sg[(r["sym"], str(r["ts"])[:10])].append(v)
        sgo = {k: sum(v) / len(v) for k, v in sg.items()}
        gun = collections.defaultdict(list)
        for (s, g), v in sgo.items():
            gun[g].append(v)
        return sgo, {g: sum(v) / len(v) for g, v in gun.items()}, sum(len(v) for v in sg.values())

    print("\n" + "=" * 106)
    print("1) HAM SHORT GETIRISI — ufuk egrisi")
    print("-" * 106)
    print("  %-8s %-9s %7s %8s %10s %8s %7s %9s"
          % ("kol", "ufuk", "satir", "sem-gun", "ort %", "sg-t", "gun", "gun-t"))
    sakla = {}
    for ad, sec in KOL:
        for h in H_SAAT:
            sgo, gunort, nsat = topla(sec, h)
            v = list(sgo.values())
            if len(v) < 3:
                continue
            m, t, n, mde = t_ist(v)
            gv = list(gunort.values())
            _, gt, gn, _ = t_ist(gv)
            sakla[(ad, h)] = (sgo, v, gunort, mde)
            print("  %-8s %-9s %7d %8d %+9.3f%% %8s %7d %9s"
                  % (ad, "%d saat" % h, nsat, n, m, ("%+.2f" % t) if t else "-",
                     gn, ("%+.2f" % gt) if gt else "-"))

    print("\n" + "=" * 106)
    print("2) SAGLAMLIK")
    print("-" * 106)
    for ad, _ in KOL:
        if (ad, BIRINCIL_H) not in sakla:
            continue
        sgo, v, _, _ = sakla[(ad, BIRINCIL_H)]
        c = collections.Counter(k[0] for k in sgo)
        top = c.most_common(1)[0]
        print("  %-6s sembol %3d · en buyuk sembol payi %%%.1f (%s) · |getiri| ort %.3f%%"
              % (ad, len(c), 100.0 * top[1] / len(sgo), top[0],
                 sum(abs(x) for x in v) / len(v)))
    if ("A+B", BIRINCIL_H) in sakla and ("TABAN", BIRINCIL_H) in sakla:
        a = sakla[("A+B", BIRINCIL_H)][1]
        t_ = sakla[("TABAN", BIRINCIL_H)][1]
        ka = sum(abs(x) for x in a) / len(a)
        ta = sum(abs(x) for x in t_) / len(t_)
        r_ = ka / ta if ta else 0
        print("  oynaklik orani A+B/TABAN = %.2fx  %s"
              % (r_, "(1,5x asildi -> K2 ZAYIF)" if (r_ > 1.5 or r_ < 1 / 1.5) else "(esit sayilir)"))

    print("\n" + "=" * 106)
    print("3) BIRINCIL HUCRE — A+B · SHORT · H=%d saat (ONCEDEN atandi)" % BIRINCIL_H)
    print("=" * 106)
    if ("A+B", BIRINCIL_H) not in sakla:
        print("  A+B kolunda yeterli veri YOK — HUKUM VERILMEZ")
        return
    sgo, av, gunort, mde = sakla[("A+B", BIRINCIL_H)]
    tv = sakla[("TABAN", BIRINCIL_H)][1]
    m, t, n, _ = t_ist(av)
    gv = list(gunort.values())
    gm, gt, gn, gmde = t_ist(gv)
    mt, tt, nt, _ = t_ist(tv)
    fark, ft = iki_ornek_t(av, tv)
    print("  A+B   : ort %+.3f%% · sembol-gun %d · sg-t %s · MDE %s"
          % (m, n, ("%+.2f" % t) if t else "-", ("%.3f" % mde) if mde else "-"))
    print("          gun ort %+.3f%% · gun %d · gun-t %s" % (gm, gn, ("%+.2f" % gt) if gt else "-"))
    print("  TABAN : ort %+.3f%% · sembol-gun %d · t %s" % (mt, nt, ("%+.2f" % tt) if tt else "-"))
    print("  A+B - TABAN: %+.3f%% · iki-orneklemli t %s" % (fark, ("%+.2f" % ft) if ft else "-"))
    k1 = (m > 0) and (t is not None and t >= 2.0)
    k2 = (fark is not None and fark > 0) and (ft is not None and ft >= 2.0)
    print()
    print("  K1  ort>0 ve sg-t>=+2,0 : %-6s (%.3f / %s)"
          % ("GECTI" if k1 else "DUSTU", m, ("%+.2f" % t) if t else "-"))
    print("  K2  fark>0 ve t>=+2,0   : %-6s (%.3f / %s)"
          % ("GECTI" if k2 else "DUSTU", fark, ("%+.2f" % ft) if ft else "-"))
    print()
    print("  HUKUM: %s" % ("GECTI" if (k1 and k2) else ("ZAYIF (yalniz K1)" if k1 else "DUSTU")))
    if mde and abs(m) < mde:
        print("  GUC: |ort| MDE'nin ALTINDA -> sonuc 'goremiyoruz' anlamina gelir.")
    elif mde:
        print("  GUC: |ort| %.3f > MDE %.3f -> orneklem bu buyuklugu gorebiliyor." % (abs(m), mde))

    # dayaniklilik
    print("\n  DAYANIKLILIK (gun duzeyi, en iyi gunler cikarilinca):")
    s = sorted(gv, reverse=True)
    for k in (0, 1, 2, 3):
        kalan = s[k:]
        if len(kalan) < 3:
            continue
        mm, tt2, nn, _ = t_ist(kalan)
        print("    en iyi %d gun cikarildi -> gun %2d · ort %+.3f%% · gun-t %s"
              % (k, nn, mm, ("%+.2f" % tt2) if tt2 else "-"))

    print("\n" + "=" * 106)
    print("4) MA50 KOLU — BETIMLEYICI, HUKUM TASIMAZ (besinci olcum)")
    print("-" * 106)
    if ("MA50", BIRINCIL_H) in sakla:
        _, mv, mgun, _ = sakla[("MA50", BIRINCIL_H)]
        mm, mt2, mn, _ = t_ist(mv)
        _, mgt, mgn, _ = t_ist(list(mgun.values()))
        print("  ort %+.3f%% · sembol-gun %d · sg-t %s · gun-t %s"
              % (mm, mn, ("%+.2f" % mt2) if mt2 else "-", ("%+.2f" % mgt) if mgt else "-"))
        print("  -> onceki DORT olcumle tutarli mi? (hepsi negatifti)")
    else:
        print("  veri yok")

    print("\n" + "=" * 106)
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
