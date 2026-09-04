#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOGA'da LONG — HAM ileri getiri (mekaniksiz). Asama 1.
On-kayit: ON_KAYIT_boga_long_ham.md (commit 59b7a67, KOSUMDAN ONCE). Olcutler SABIT.

Soru: bot BOGA'da LONG'a kilitli ve kaybediyor. Yon mu yanlis, mekanik mi olduruyor?
Mekanik YOK: stop yok, hedef yok, maliyet yok. Yalniz ham fiyat yolu.

🔴 BIRIM = SEMBOL-GUN. Aday satiri 7,5 dakikada bir yaziliyor; satir saymak
   sahte N uretir. Her (sembol, gun) o gunun nitelenen satirlarinin ORTALAMASI
   olarak TEK gozlem sayilir.
🔴 ZAMAN DILIMI SINAMASI: arsiv ts YEREL (UTC+3), mumlar UTC. `price` eslenen
   barin [low,high] araliginda mi? Oran %90'in altindaysa betik REDDEDER.
🔴 Arsiv context'e YUKLENMEZ.
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

YEREL_FARK = 3                 # arsiv ts = UTC+3
H_SAAT = [1, 4, 12, 24]
BIRINCIL_H = 4
SKOR_ESIK = 45.0               # config: radar_short_skor
POS_ESIK = 0.85                # testbot.py:617 sabit
BAS, BIT = "2026-08-03", "2026-09-05"
SAAT_MS = 3600 * 1000
TZ_ASGARI = 0.90               # zaman dilimi sinamasi bariyeri


def utc_ts(yerel_str):
    d = datetime.datetime.strptime(yerel_str, "%Y-%m-%d %H:%M") \
        - datetime.timedelta(hours=YEREL_FARK)
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
    e = datetime.datetime(1970, 1, 1)
    bas = int((datetime.datetime.strptime(BAS, "%Y-%m-%d") - e).total_seconds() * 1000)
    bit = int((datetime.datetime.strptime(BIT, "%Y-%m-%d") - e).total_seconds() * 1000)
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
        # [t, open, high, low, close]
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
    """(ort, t, n, MDE@t=2)"""
    if len(v) < 3:
        return (sum(v) / len(v) if v else None), None, len(v), None
    m, sd = sum(v) / len(v), statistics.stdev(v)
    se = sd / math.sqrt(len(v))
    return m, (m / se if se else None), len(v), (2.0 * se if se else None)


def iki_ornek_t(a, b):
    if len(a) < 3 or len(b) < 3:
        return None, None
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    se = math.sqrt(va / len(a) + vb / len(b))
    return (ma - mb), ((ma - mb) / se if se else None)


def main():
    print("BOGA'da LONG — HAM ileri getiri (mekaniksiz, Asama 1)")
    print("on-kayit ON_KAYIT_boga_long_ham.md (59b7a67) · olcutler SABIT")
    print("=" * 106)
    print("birim: SEMBOL-GUN  ·  birincil hucre: KAPI kolu, H=%d saat" % BIRINCIL_H)
    print("kapi: rejim=BOGA & score>=%.0f & smart!=SHORT & pos<=%.2f" % (SKOR_ESIK, POS_ESIK))

    # ------------------------------------------------------------- arsiv
    satir = []
    for l in open(ARSIV, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        if not str(r.get("rejim") or "").upper().startswith("BOGA"):
            continue
        ts = str(r.get("ts") or "")
        sym, px = r.get("sym"), r.get("price")
        if not ts or not sym or not px:
            continue
        satir.append(r)
    print("\nBOGA aday satiri: %d · sembol %d"
          % (len(satir), len({r["sym"] for r in satir})))

    # ------------------------------------------------------------- mumlar
    semboller = sorted({r["sym"] for r in satir})
    mum, yok = {}, []
    for i, s in enumerate(semboller):
        if (i + 1) % 40 == 0:
            print("  mum ... %d/%d" % (i + 1, len(semboller)))
        b = mum_cek(s)
        if b:
            mum[s] = (b, {x[0]: j for j, x in enumerate(b)})
        else:
            yok.append(s)
    print("  mum bulunan %d · bulunamayan %d %s"
          % (len(mum), len(yok), ("(%s...)" % ",".join(yok[:6])) if yok else ""))

    # ------------------------------------------- zaman dilimi sinamasi
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
    print("\nZAMAN DILIMI SINAMASI (UTC+3 -> UTC): price bar araliginda mi?")
    print("  icinde %d · disinda %d  ->  %%%.1f" % (ic, dis, 100 * oran))
    if oran < TZ_ASGARI:
        print("  🔴 %%%.0f bariyerinin ALTINDA — kaydirma yanlis. BETIK REDDEDIYOR." % (100 * TZ_ASGARI))
        raise SystemExit(1)
    print("  -> GECTI (kaydirma dogru)")

    # ------------------------------------------------------------- getiri
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
        return ((x - e) / e * 100.0) if e > 0 else None

    def kapi_mi(r):
        return ((r.get("score") or 0) >= SKOR_ESIK
                and str(r.get("smart")) != "SHORT"
                and (r.get("pos") is None or float(r.get("pos")) <= POS_ESIK))

    # sembol-gun toplama
    def sg_topla(sec, h):
        g = collections.defaultdict(list)
        for r in satir:
            if not sec(r):
                continue
            v = ret(r, h)
            if v is not None:
                g[(r["sym"], str(r["ts"])[:10])].append(v)
        return {k: sum(v) / len(v) for k, v in g.items()}, sum(len(v) for v in g.values())

    print("\n" + "=" * 106)
    print("1) HAM GETIRI — ufuk egrisi (birim SEMBOL-GUN)")
    print("-" * 106)
    print("  %-8s %-9s %7s %7s %10s %8s %9s %10s"
          % ("kol", "ufuk", "satir", "sem-gun", "ort %", "t", "MDE", "medyan %"))
    sakla = {}
    for ad, sec in (("KAPI", kapi_mi), ("TABAN", lambda r: True)):
        for h in H_SAAT:
            sg, nsat = sg_topla(sec, h)
            v = list(sg.values())
            if len(v) < 3:
                continue
            m, t, n, mde = t_ist(v)
            sakla[(ad, h)] = (sg, v, nsat)
            print("  %-8s %-9s %7d %7d %+9.3f%% %8s %8s %+9.3f%%"
                  % (ad, "%d saat" % h, nsat, n, m,
                     ("%+.2f" % t) if t else "-",
                     ("%.3f" % mde) if mde else "-", statistics.median(v)))

    # ---------------------------------------------------- yogunlasma + oynaklik
    print("\n" + "=" * 106)
    print("2) SAGLAMLIK — yogunlasma ve oynaklik esitligi")
    print("-" * 106)
    for ad in ("KAPI", "TABAN"):
        if (ad, BIRINCIL_H) not in sakla:
            continue
        sg, v, _ = sakla[(ad, BIRINCIL_H)]
        c = collections.Counter(k[0] for k in sg)
        top = c.most_common(1)[0] if c else ("-", 0)
        print("  %-6s sembol %3d · en buyuk sembolun payi %%%.1f (%s) · |getiri| ort %.3f%%"
              % (ad, len(c), 100.0 * top[1] / len(sg), top[0],
                 sum(abs(x) for x in v) / len(v)))
    if ("KAPI", BIRINCIL_H) in sakla and ("TABAN", BIRINCIL_H) in sakla:
        ka = sum(abs(x) for x in sakla[("KAPI", BIRINCIL_H)][1]) / len(sakla[("KAPI", BIRINCIL_H)][1])
        ta = sum(abs(x) for x in sakla[("TABAN", BIRINCIL_H)][1]) / len(sakla[("TABAN", BIRINCIL_H)][1])
        r_ = ka / ta if ta else 0
        print("  oynaklik orani KAPI/TABAN = %.2fx  %s"
              % (r_, "(1,5x asildi -> K2 hukmu ZAYIF)" if r_ > 1.5 or r_ < 1 / 1.5 else "(esit sayilir)"))

    # ------------------------------------------------------------- birincil
    print("\n" + "=" * 106)
    print("3) BIRINCIL HUCRE — on-kayitta ONCEDEN atandi")
    print("=" * 106)
    kg, kv, _ = sakla[("KAPI", BIRINCIL_H)]
    tg, tv, _ = sakla[("TABAN", BIRINCIL_H)]
    m, t, n, mde = t_ist(kv)
    print("  KAPI  H=%dsa : ort %+.3f%%  ·  sembol-gun %d  ·  t %s  ·  MDE %s"
          % (BIRINCIL_H, m, n, ("%+.2f" % t) if t else "-", ("%.3f" % mde) if mde else "-"))
    mt, tt, nt, _ = t_ist(tv)
    print("  TABAN H=%dsa : ort %+.3f%%  ·  sembol-gun %d  ·  t %s"
          % (BIRINCIL_H, mt, nt, ("%+.2f" % tt) if tt else "-"))
    fark, ft = iki_ornek_t(kv, tv)
    print("  KAPI - TABAN: %+.3f%%  ·  iki-orneklemli t %s"
          % (fark, ("%+.2f" % ft) if ft else "-"))
    k1 = (m < 0) and (t is not None and t <= -2.0)
    k2 = (fark is not None and fark < 0) and (ft is not None and ft <= -2.0)
    print()
    print("  K1  ort<0 ve t<=-2,0        : %-6s (%.3f / %s)"
          % ("GECTI" if k1 else "DUSTU", m, ("%+.2f" % t) if t else "-"))
    print("  K2  fark<0 ve t<=-2,0       : %-6s (%.3f / %s)"
          % ("GECTI" if k2 else "DUSTU", fark, ("%+.2f" % ft) if ft else "-"))
    print()
    print("  UC YOLLU HUKUM:")
    if k1:
        print("    -> YON YANLIS. Ham fiyatta da kaybediyor; mekanik tek suclu degil.")
        print("       LONG dali ve SHORT istisnasi gundeme gelir (yeni pencere ile).")
    elif mde and abs(m) < mde:
        print("    -> ORTALAMA ~0 (|ort| MDE'nin altinda). Yon NOTR.")
        print("       KAPIYA DOKUNULMAZ; sira STOP olcumune gecer.")
    elif m > 0:
        print("    -> YON DOGRU, ham getiri ARTI. Sorun kapida degil MEKANIKTE.")
        print("       Kapi KESINLIKLE degismez; stop/hedef olculur.")
    else:
        print("    -> ort<0 ama t esigi gecmedi. Isaret A yonunde, KANIT yok.")
        print("       Hukum: KANITLANAMADI (guc icin MDE'ye bak).")

    # ------------------------------------------------------------- ikincil
    print("\n" + "=" * 106)
    print("4) IKINCIL — betimleyici, HUKUM TASIMAZ (on-kayitta 3 adet sayildi)")
    print("-" * 106)
    print("  (2) taker ayrimi — SHORT istisnasini kesen sart tam olarak bu")
    for ad, sec in (("taker<=1,0", lambda r: (r.get("taker") is not None and float(r["taker"]) <= 1.0)),
                    ("taker >1,0", lambda r: (r.get("taker") is not None and float(r["taker"]) > 1.0))):
        sg, ns = sg_topla(sec, BIRINCIL_H)
        v = list(sg.values())
        if len(v) < 3:
            continue
        m2, t2, n2, _ = t_ist(v)
        print("    %-12s satir %6d · sem-gun %4d · ort %+.3f%% · t %s"
              % (ad, ns, n2, m2, ("%+.2f" % t2) if t2 else "-"))
    print("\n  (3) BASLIYOR + smart=SHORT alt kumesi (N'in kucuk oldugu BILINIYOR)")
    sg, ns = sg_topla(lambda r: str(r.get("stage")) == "BASLIYOR" and str(r.get("smart")) == "SHORT",
                      BIRINCIL_H)
    v = list(sg.values())
    if v:
        print("    satir %d · sembol-gun %d · ort %+.3f%% · sembol: %s"
              % (ns, len(v), sum(v) / len(v), sorted({k[0] for k in sg})))
        print("    -> LONG yonunde. SHORT yonu bunun TERSI olur.")
    else:
        print("    veri yok")

    print("\n" + "=" * 106)
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
