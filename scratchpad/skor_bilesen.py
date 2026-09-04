#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SKORUN BES BILESENI — hangisi bilgi tasiyor, skor yeniden kurulabilir mi?
On-kayit: ON_KAYIT_skor_bilesenleri.md (commit 81c95fb, KOSUMDAN ONCE). SABIT.

ASAMA A: 5 bilesen x 2 rejim + 2 ozel soru (O1 funding isareti, O2 squeeze_bonus)
ASAMA B: yeni skor ARANMAZ, mekanik kuralla TURETILIR
ASAMA C: A yarisinda SEC, B yarisinda OLC (K2 belirleyici)

🔑 seviyeler()/oynat() KAYNAKTAN cagrilir.
🔴 BIRIM = SEMBOL-GUN · gun-kumeli t.
SALT OKUMA — bu betik hicbir bot dosyasina yazmaz.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, io, json, math, datetime, statistics, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARSIV = os.path.join(PROJE, "testbot_aday_arsiv.jsonl")
MUM = os.path.join(PROJE, "scratchpad", "aday_pencere_1h")
KAYNAK = os.path.join(PROJE, "scratchpad", "stop_mu_sure_mu.py")
SAAT_MS = 3600 * 1000
BOGA_BAS = "2026-08-21"


def mekanik_yukle():
    src = open(KAYNAK, encoding="utf-8").read()
    k = src.index('return kar, j - i, "ZAMAN_STOP"')
    k = src.index("\n", k) + 1
    ns = {"__name__": "_mek", "__file__": KAYNAK}
    tut = _sys.stdout
    _sys.stdout = io.StringIO()
    try:
        exec(compile(src[:k], KAYNAK, "exec"), ns)
    finally:
        _sys.stdout = tut
    if "seviyeler" not in ns:
        raise SystemExit("MEKANIK YUKLENEMEDI")
    return ns


M = mekanik_yukle()
seviyeler, oynat = M["seviyeler"], M["oynat"]
MALIYET, ASGARI, YAPI = M["MALIYET"], M["ASGARI_STOP"], M["YAPI_BAR"]


def clamp(x):
    return max(0.0, min(1.0, x))


def utc_ts(s):
    d = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M") - datetime.timedelta(hours=3)
    return int((d - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)


def sg(w, alan):
    g = collections.defaultdict(list)
    for x in w:
        if x.get(alan) is not None:
            g[(x["sym"], x["_gun"])].append(x[alan])
    sgo = {k: sum(v) / len(v) for k, v in g.items()}
    gun = collections.defaultdict(list)
    for (s, d), v in sgo.items():
        gun[d].append(v)
    return sgo, [sum(v) / len(v) for v in gun.values()]


def fark_t(a, b, alan):
    _, ga = sg(a, alan)
    _, gb = sg(b, alan)
    if len(ga) < 3 or len(gb) < 3:
        return None, None, None
    ma, mb = sum(ga) / len(ga), sum(gb) / len(gb)
    se = math.sqrt(statistics.variance(ga) / len(ga) + statistics.variance(gb) / len(gb))
    return (ma - mb), ((ma - mb) / se if se else None), (2.0 * se if se else None)


# ---------------------------------------------------------------- terimler
def t_oi(r):
    return clamp((r.get("oi24") or 0) / 20) * 25 + clamp((r.get("oi3") or 0) / 8) * 10


def t_fund_abs(r):
    f = r.get("funding")
    return clamp(abs(f or 0) / 0.05) * 15


def t_fund_isaretli(r):
    """O1: isaretli — negatif funding NEGATIF puan"""
    f = r.get("funding")
    return clamp((f or 0) / 0.05) * 15 if (f or 0) > 0 else -clamp(abs(f or 0) / 0.05) * 15


def t_bonus(r):
    f, l3, oi3 = r.get("funding"), r.get("last3") or 0, r.get("oi3") or 0
    return 8.0 if (f is not None and f < -0.01 and l3 >= -1 and oi3 >= 0) else 0.0


def t_comp(r):
    c = r.get("comp")
    return clamp((0.8 - c) / 0.5) * 20 if c is not None else 0.0


def t_vol(r):
    return clamp(((r.get("vol_x") or 0) - 1.5) / 3) * 20


def t_brk(r):
    p = r.get("pos")
    return (clamp((p - 0.7) / 0.3) * 10 if p is not None else 0.0) + clamp((r.get("last1") or 0) / 4) * 5


TERIMLER = [("1 s_oi", t_oi), ("2 s_fund (abs)", t_fund_abs), ("3 s_comp", t_comp),
            ("4 s_vol", t_vol), ("5 s_brk", t_brk),
            ("O1 s_fund (ISARETLI)", t_fund_isaretli), ("O2 squeeze_bonus", t_bonus)]


def main():
    print("SKORUN BES BILESENI")
    print("on-kayit ON_KAYIT_skor_bilesenleri.md (81c95fb) · olcutler SABIT")
    print("=" * 110)

    seri = {}
    for fn in os.listdir(MUM):
        if not fn.endswith(".json"):
            continue
        try:
            b = json.load(open(os.path.join(MUM, fn)))
        except Exception:
            continue
        if len(b) < YAPI + 5:
            continue
        b.sort(key=lambda z: z[0])
        seri[fn[:-5]] = {"h": [x[1] for x in b], "l": [x[2] for x in b],
                         "c": [x[3] for x in b], "ix": {x[0]: j for j, x in enumerate(b)}}

    R = []
    for l in open(ARSIV, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        ts = str(r.get("ts") or "")
        s = r.get("sym")
        rej = str(r.get("rejim") or "").upper()
        if not s or s not in seri or r.get("score") is None:
            continue
        if not (rej.startswith("BOGA") or rej.startswith("NOTR")):
            continue
        S = seri[s]
        t0 = utc_ts(ts)
        i = S["ix"].get(t0 - (t0 % SAAT_MS))
        if i is None or i < YAPI:
            continue
        ref = S["c"][i]
        j4 = S["ix"].get(t0 - (t0 % SAAT_MS) + 4 * SAAT_MS)
        if j4 is None:
            continue
        r["ham4"] = (S["c"][j4] - ref) / ref * 100.0
        sv = seviyeler(S["h"], S["l"], S["c"], i, "LONG")
        if sv:
            sl, tp1, tp2, risk, a = sv
            if abs(ref - sl) / ref * 100.0 >= ASGARI:
                kar, _, _ = oynat(S["h"], S["l"], S["c"], i, "LONG", sl, tp1, tp2, risk, a)
                r["mek"] = kar - MALIYET
        r["_gun"] = ts[:10]
        r["_rej"] = "BOGA" if rej.startswith("BOGA") else "NOTR"
        R.append(r)

    B = [x for x in R if x["_rej"] == "BOGA"]
    N = [x for x in R if x["_rej"] == "NOTR"]
    print("satir %d  ·  BOGA %d (%d gun)  ·  NOTR %d (%d gun)"
          % (len(R), len(B), len({x['_gun'] for x in B}), len(N), len({x['_gun'] for x in N})))
    print("⚠️ Getiri LONG yonunde olculur. Bot NOTR'da cogunlukla SHORT acar ->")
    print("   NOTR kolunda POZITIF fark, SHORT icin KOTU demektir.")

    # ================================================== ASAMA A
    print("\n" + "=" * 110)
    print("ASAMA A) BILESEN TARAMASI — ust ceyrek - alt ceyrek (ham 4 saat, LONG)")
    print("-" * 110)
    print("  %-22s %-6s %8s %11s %8s %10s %9s"
          % ("terim", "rejim", "sem-gun", "fark %", "gun-t", "A yari t", "B yari t"))
    A_sonuc = {}
    for ad, fn in TERIMLER:
        for rad, W in (("BOGA", B), ("NOTR", N)):
            for x in W:
                x["_v"] = fn(x)
            v = sorted(x["_v"] for x in W)
            lo, hi = v[len(v) // 4], v[3 * len(v) // 4]
            if lo >= hi:
                print("  %-22s %-6s  (dagilim yok)" % (ad, rad))
                A_sonuc[(ad, rad)] = None
                continue
            ust = [x for x in W if x["_v"] >= hi]
            alt = [x for x in W if x["_v"] <= lo]
            f, t, _ = fark_t(ust, alt, "ham4")
            gunler = sorted({x["_gun"] for x in W})
            orta = gunler[len(gunler) // 2]
            fa, ta, _ = fark_t([x for x in ust if x["_gun"] < orta],
                               [x for x in alt if x["_gun"] < orta], "ham4")
            fb, tb, _ = fark_t([x for x in ust if x["_gun"] >= orta],
                               [x for x in alt if x["_gun"] >= orta], "ham4")
            n = len(sg(ust, "ham4")[0]) + len(sg(alt, "ham4")[0])
            A_sonuc[(ad, rad)] = (f, t, fa, fb)
            print("  %-22s %-6s %8d %+10.3f%% %8s %10s %9s"
                  % (ad, rad, n, f if f else 0, ("%+.2f" % t) if t else "-",
                     ("%+.2f" % ta) if ta else "-", ("%+.2f" % tb) if tb else "-"))

    # ================================================== ASAMA B
    print("\n" + "=" * 110)
    print("ASAMA B) YENI SKOR — ARANMAZ, on-kayittaki mekanik kuralla TURETILIR")
    print("-" * 110)
    print("  Kural: |gun-t| >= 2,0  VE  iki yarida ayni isaret  VE  rejimler arasi")
    print("         yon celiskisi YOK. Agirlik olculen farkla orantili.")
    secilen = []
    for ad, fn in TERIMLER:
        rb = A_sonuc.get((ad, "BOGA"))
        rn = A_sonuc.get((ad, "NOTR"))
        if not rb:
            continue
        f, t, fa, fb = rb
        if t is None or abs(t) < 2.0:
            print("    %-22s ELENDI: |t| %.2f < 2,0" % (ad, abs(t) if t else 0))
            continue
        if fa is None or fb is None or (fa > 0) != (fb > 0):
            print("    %-22s ELENDI: yarilar ZIT isaret (A %+.3f / B %+.3f)"
                  % (ad, fa if fa else 0, fb if fb else 0))
            continue
        if rn and rn[0] is not None and (rn[0] > 0) != (f > 0):
            print("    %-22s ELENDI: REJIMLER ARASI yon celiskisi (BOGA %+.3f / NOTR %+.3f)"
                  % (ad, f, rn[0]))
            continue
        secilen.append((ad, fn, f, t))
        print("    %-22s SECILDI  fark %+.3f%% · t %+.2f" % (ad, f, t))

    if not secilen:
        print("\n  🔴 HICBIR TERIM GECMEDI -> YENI SKOR KURULMAZ (on-kayit kural 4)")
        print("\n" + "=" * 110)
        print("HUKUM: DUSTU — bilesen ayari da skoru duzeltmiyor.")
        print("KOD DEGISMEZ. (on-kayit s.7)")
        print("\nbot dosyalarina yazim: YOK")
        return

    top = sum(abs(f) for _, _, f, _ in secilen)
    print("\n  YENI SKOR = " + " + ".join("%.0f x %s" % (100 * abs(f) / top, ad)
                                          for ad, _, f, _ in secilen))

    def yeni_skor(x):
        s = 0.0
        for ad, fn, f, _ in secilen:
            s += (100.0 * abs(f) / top) * (fn(x) / 100.0) * (1 if f > 0 else -1)
        return s

    # ================================================== ASAMA C
    print("\n" + "=" * 110)
    print("ASAMA C) DOGRULAMA — terimler A yarisinda secildi, hukum B yarisinda")
    print("-" * 110)
    gunler = sorted({x["_gun"] for x in B})
    orta = gunler[len(gunler) // 2]
    BB = [x for x in B if x["_gun"] >= orta]
    print("  B yarisi (dogrulama): %d satir · %d gun" % (len(BB), len({x['_gun'] for x in BB})))
    for x in BB:
        x["_yeni"] = yeni_skor(x)
    PAY = 0.36
    ys = sorted(x["_yeni"] for x in BB)
    es = sorted(x["score"] for x in BB)
    y_esik = ys[int((1 - PAY) * len(ys))]
    e_esik = es[int((1 - PAY) * len(es))]
    yeni_k = [x for x in BB if x["_yeni"] >= y_esik]
    eski_k = [x for x in BB if x["score"] >= e_esik]
    for alan, ad in (("ham4", "HAM"), ("mek", "MEKANIK")):
        my = sg(yeni_k, alan)[1]
        me = sg(eski_k, alan)[1]
        if len(my) < 3 or len(me) < 3:
            continue
        f, t, mde = fark_t(yeni_k, eski_k, alan)
        print("  %-8s yeni %+7.3f%% · eski %+7.3f%% · fark %+7.3f%% · t %s · MDE %s"
              % (ad, sum(my) / len(my), sum(me) / len(me), f,
                 ("%+.2f" % t) if t else "-", ("%.3f" % mde) if mde else "-"))
        if alan == "ham4":
            k1 = f > 0 and t is not None and t >= 2.0
            k1f, k1t, k1mde = f, t, mde
        else:
            k3 = f > 0
    k4 = abs(len(yeni_k) - len(eski_k)) / max(1, len(eski_k)) < 0.25
    print("  aday sayisi: yeni %d · eski %d -> K4 %s"
          % (len(yeni_k), len(eski_k), "GECTI" if k4 else "DUSTU (kisir kapi)"))

    print("\n" + "=" * 110)
    print("HUKUM")
    print("=" * 110)
    print("  K1 (B yarisinda ham fark>0, t>=+2,0) : %-6s (%.3f / %s)"
          % ("GECTI" if k1 else "DUSTU", k1f, ("%+.2f" % k1t) if k1t else "-"))
    print("  K2 (ayri yarida dogrulama)           : YAPILDI (terimler A, hukum B)")
    print("  K3 (mekanikli de > 0)                : %-6s" % ("GECTI" if k3 else "DUSTU"))
    print("  K4 (kisir kapi yok)                  : %-6s" % ("GECTI" if k4 else "DUSTU"))
    gec = k1 and k3 and k4
    print("\n  HUKUM: %s" % ("GECTI — skor degistirilir (on-kayit s.7)" if gec
                             else "DUSTU — KOD DEGISMEZ"))
    if k1mde and abs(k1f) < k1mde:
        print("  GUC: |fark| %.3f < MDE %.3f -> GOREMIYORUZ" % (abs(k1f), k1mde))
    print("\nbot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
