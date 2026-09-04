#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SKORUN TERSI — dusuk skorlu adaylar alinsaydi ne olurdu?
On-kayit: ON_KAYIT_skor_tersi.md (commit c83e4a8, KOSUMDAN ONCE). Olcutler SABIT.

S1 (BIRINCIL) skor<45 vs skor>=45, HAM ve MEKANIKLI
S2 skorun poz ALMADAKI etkisi (esik vs taranan evren)
S3 skorun BOYUTLANDIRMADAKI etkisi — zaten olculdu, yalniz TEYIT

🔑 seviyeler()/oynat() KAYNAKTAN cagrilir, kopyalanmaz.
🔴 BIRIM = SEMBOL-GUN · gun-kumeli t · guc denetimi zorunlu.
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
ARSIV = os.path.join(PROJE, "testbot_aday_arsiv.jsonl")
DEFTER = os.path.join(PROJE, "testbot_islemler.jsonl")
MUM = os.path.join(PROJE, "scratchpad", "aday_pencere_1h")
KAYNAK = os.path.join(PROJE, "scratchpad", "stop_mu_sure_mu.py")
BAS = "2026-08-22"          # kullanicinin tarihi
SAAT_MS = 3600 * 1000
ESIK = 45.0


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
    if "seviyeler" not in ns or "oynat" not in ns:
        raise SystemExit("MEKANIK YUKLENEMEDI — betik REDDEDIYOR")
    return ns


M = mekanik_yukle()
seviyeler, oynat = M["seviyeler"], M["oynat"]
MALIYET, ASGARI, YAPI = M["MALIYET"], M["ASGARI_STOP"], M["YAPI_BAR"]


def utc_ts(s):
    d = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M") - datetime.timedelta(hours=3)
    return int((d - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)


def sg_gun(w, alan):
    g = collections.defaultdict(list)
    for x in w:
        if x.get(alan) is not None:
            g[(x["sym"], x["_gun"])].append(x[alan])
    sgo = {k: sum(v) / len(v) for k, v in g.items()}
    gun = collections.defaultdict(list)
    for (s, d), v in sgo.items():
        gun[d].append(v)
    return sgo, [sum(v) / len(v) for v in gun.values()]


def ist(w, alan):
    sgo, gv = sg_gun(w, alan)
    if len(gv) < 3:
        return (sum(gv) / len(gv) if gv else None), None, len(sgo), len(gv)
    m = sum(gv) / len(gv)
    return m, None, len(sgo), len(gv)


def fark_t(a, b, alan):
    _, ga = sg_gun(a, alan)
    _, gb = sg_gun(b, alan)
    if len(ga) < 3 or len(gb) < 3:
        return None, None, None
    ma, mb = sum(ga) / len(ga), sum(gb) / len(gb)
    se = math.sqrt(statistics.variance(ga) / len(ga) + statistics.variance(gb) / len(gb))
    return (ma - mb), ((ma - mb) / se if se else None), (2.0 * se if se else None)


def main():
    print("SKORUN TERSI — dusuk skorlu adaylar alinsaydi ne olurdu?")
    print("on-kayit ON_KAYIT_skor_tersi.md (c83e4a8) · olcutler SABIT")
    print("=" * 108)
    print("pencere: %s'den itibaren (kullanicinin tarihi) · esik skor %.0f" % (BAS, ESIK))

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

    R, eleme = [], collections.Counter()
    for l in open(ARSIV, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        ts = str(r.get("ts") or "")
        if ts[:10] < BAS or not str(r.get("rejim") or "").upper().startswith("BOGA"):
            continue
        s = r.get("sym")
        if not s or s not in seri or r.get("score") is None:
            eleme["seri/skor yok"] += 1
            continue
        S = seri[s]
        t0 = utc_ts(ts)
        i = S["ix"].get(t0 - (t0 % SAAT_MS))
        if i is None or i < YAPI:
            eleme["gecmis yetersiz"] += 1
            continue
        ref = S["c"][i]
        j4 = S["ix"].get(t0 - (t0 % SAAT_MS) + 4 * SAAT_MS)
        r["ham4"] = ((S["c"][j4] - ref) / ref * 100.0) if j4 is not None else None
        sv = seviyeler(S["h"], S["l"], S["c"], i, "LONG")
        if sv:
            sl, tp1, tp2, risk, a = sv
            if abs(ref - sl) / ref * 100.0 >= ASGARI:
                kar, sure, seb = oynat(S["h"], S["l"], S["c"], i, "LONG", sl, tp1, tp2, risk, a)
                r["mek"] = kar - MALIYET
                r["stop_pct"] = abs(ref - sl) / ref * 100.0
                r["seb"] = seb
                r["sure"] = sure
        r["_gun"] = ts[:10]
        if r.get("ham4") is not None:
            R.append(r)
    print("\nolculen satir: %d · sembol %d · gun %d · eleme %s"
          % (len(R), len({x["sym"] for x in R}), len({x["_gun"] for x in R}), dict(eleme)))

    A = [x for x in R if x["score"] < ESIK]          # TERS kol (hic alinmadi)
    B = [x for x in R if x["score"] >= ESIK]         # botun kolu
    Am = [x for x in A if x.get("mek") is not None]
    Bm = [x for x in B if x.get("mek") is not None]
    print("  skor<45: %d satir (mekanikli %d) · skor>=45: %d satir (mekanikli %d)"
          % (len(A), len(Am), len(B), len(Bm)))

    # -------------------------------------------------- S1 BIRINCIL
    print("\n" + "=" * 108)
    print("S1) BIRINCIL — skor<45 (TERS) vs skor>=45 (botun kurali)")
    print("-" * 108)
    print("  %-12s %10s %12s %10s %12s" % ("kol", "sem-gun", "HAM 4sa %", "sem-gun", "MEKANIK %"))
    for ad, w, wm in (("skor<45", A, Am), ("skor>=45", B, Bm)):
        mh, _, nh, _ = ist(w, "ham4")
        mm, _, nm, _ = ist(wm, "mek")
        print("  %-12s %10d %+11.3f%% %10d %+11.3f%%" % (ad, nh, mh, nm, mm if mm else 0))
    fh, th, _ = fark_t(A, B, "ham4")
    fm, tm, mde = fark_t(Am, Bm, "mek")
    print("  " + "-" * 96)
    print("  %-12s %10s %+11.3f%% %10s %+11.3f%%" % ("FARK", "", fh, "", fm if fm else 0))
    print("  %-12s %10s %11s   %10s %11s"
          % ("gun-t", "", ("%+.2f" % th) if th else "-", "", ("%+.2f" % tm) if tm else "-"))

    # -------------------------------------------------- K4 mekanik esitligi
    print("\n  K4 — mekanik esitligi:")
    olc = {}
    for ad, w in (("skor<45", Am), ("skor>=45", Bm)):
        sw = sum(x["stop_pct"] for x in w) / len(w)
        so = 100.0 * sum(1 for x in w if str(x["seb"]).startswith("STOP")) / len(w)
        olc[ad] = (sw, so)
        print("    %-10s stop genisligi %.2f%% · stop-olma %.0f%% · medyan sure %.1f"
              % (ad, sw, so, statistics.median([x["sure"] for x in w])))
    o1 = olc["skor<45"][0] / olc["skor>=45"][0]
    o2 = olc["skor<45"][1] / olc["skor>=45"][1]
    k4 = (1 / 1.5) <= o1 <= 1.5 and (1 / 1.5) <= o2 <= 1.5
    print("    oran %.2fx / %.2fx -> K4 %s" % (o1, o2, "GECTI" if k4 else "DUSTU (kiyas BOZUK)"))

    # -------------------------------------------------- K3 bolunmus yari
    print("\n  K3 — bolunmus yari (mekanikli):")
    gunler = sorted({x["_gun"] for x in R})
    orta = gunler[len(gunler) // 2]
    yariler = []
    for et, sec in (("A", lambda x: x["_gun"] < orta), ("B", lambda x: x["_gun"] >= orta)):
        f, t, _ = fark_t([x for x in Am if sec(x)], [x for x in Bm if sec(x)], "mek")
        yariler.append(f if f else 0)
        print("    %s yari: fark %s · t %s"
              % (et, ("%+.3f%%" % f) if f is not None else "-", ("%+.2f" % t) if t else "-"))

    # -------------------------------------------------- HUKUM
    print("\n" + "=" * 108)
    print("BIRINCIL HUKUM")
    print("=" * 108)
    k1 = fm is not None and fm > 0 and tm is not None and tm >= 2.0
    k2 = fh is not None and fm is not None and (fh > 0) == (fm > 0)
    k3 = yariler[0] > 0 and yariler[1] > 0
    print("  K1  mekanikli fark>0 ve t>=+2,0 : %-6s (%.3f / %s)"
          % ("GECTI" if k1 else "DUSTU", fm if fm else 0, ("%+.2f" % tm) if tm else "-"))
    print("  K2  ham ve mekanik ayni isaret  : %-6s (ham %+.3f · mek %+.3f)"
          % ("GECTI" if k2 else "DUSTU", fh, fm if fm else 0))
    print("  K3  iki yarida da > 0           : %-6s (A %+.3f · B %+.3f)"
          % ("GECTI" if k3 else "DUSTU", yariler[0], yariler[1]))
    print("  K4  mekanik esitligi            : %-6s" % ("GECTI" if k4 else "DUSTU"))
    print()
    if k1 and k2 and k3 and k4:
        h = "GECTI — skorun TERSI daha iyi"
    elif k1 and k3:
        h = "ZAYIF"
    else:
        h = "DUSTU"
    print("  HUKUM: %s" % h)
    if mde:
        print("  GUC: MDE %.3f · |fark| %.3f -> %s"
              % (mde, abs(fm) if fm else 0,
                 "gorulebilir" if (fm and abs(fm) > mde) else "GOREMIYORUZ"))

    # -------------------------------------------------- skor bantlari
    print("\n" + "=" * 108)
    print("BETIMLEYICI — skor bantlari (esik mi, monotonluk mu?) HUKUM TASIMAZ")
    print("-" * 108)
    print("  %-14s %8s %10s %12s %12s" % ("bant", "satir", "sem-gun", "HAM 4sa %", "MEKANIK %"))
    bantlar = [(0, 35), (35, 40), (40, 45), (45, 50), (50, 60), (60, 200)]
    for lo, hi in bantlar:
        w = [x for x in R if lo <= x["score"] < hi]
        wm = [x for x in w if x.get("mek") is not None]
        if len(w) < 30:
            continue
        mh, _, nh, _ = ist(w, "ham4")
        mm, _, nm, _ = ist(wm, "mek") if wm else (None, None, 0, 0)
        print("  %-14s %8d %10d %+11.3f%% %+11.3f%%"
              % ("%d-%d" % (lo, hi), len(w), nh, mh, mm if mm else 0))

    # -------------------------------------------------- S2 poz alma etkisi
    print("\n" + "=" * 108)
    print("S2) SKORUN POZ ALMADAKI ETKISI — esik ne kadar aday kesiyor?")
    print("-" * 108)
    print("  taranan satir           : %d" % len(R))
    print("  skor >= 45 (alinabilir) : %d (%%%.0f)" % (len(B), 100.0 * len(B) / len(R)))
    print("  skor <  45 (kesiliyor)  : %d (%%%.0f)" % (len(A), 100.0 * len(A) / len(R)))
    mt, _, nt, _ = ist(R, "ham4")
    print("  taranan evrenin ham getirisi : %+.3f%%" % mt)
    print("  -> esigin kattigi deger      : %+.3f puan"
          % (ist(B, "ham4")[0] - mt))

    # -------------------------------------------------- S3 boyut teyidi
    print("\n" + "=" * 108)
    print("S3) SKORUN BOYUTLANDIRMADAKI ETKISI — TEYIT (zaten olculdu)")
    print("-" * 108)
    ham = collections.defaultdict(list)
    for l in open(DEFTER, encoding="utf-8"):
        l = l.strip()
        if l:
            try:
                r = json.loads(l)
            except Exception:
                continue
            if r.get("id") is not None:
                ham[r["id"]].append(r)
    poz = []
    for i, v in ham.items():
        v.sort(key=lambda z: z["ts"])
        ilk, son = v[0], v[-1]
        no = ilk.get("notional") or 0
        if no <= 0 or ilk.get("skor_giriste") is None:
            continue
        net = sum((t.get("sonuc_usdt") or 0) for t in v)
        fl = [t.get("funding_usdt") for t in v if t.get("funding_usdt") is not None]
        net += sum(fl) if fl else 0.0
        tut = max((t.get("tutma_saat") or 0) for t in v)
        gir = datetime.datetime.strptime(son["ts"], "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=tut)
        poz.append({"skor": ilk["skor_giriste"], "no": no, "net": net,
                    "ret": 100.0 * net / no, "gun": gir.date().isoformat()})
    P = [p for p in poz if p["gun"] >= BAS]
    print("  %s'den beri GERCEK pozisyon: %d" % (BAS, len(P)))
    if len(P) >= 20:
        sk = [p["skor"] for p in P]
        nn = [p["no"] for p in P]
        rr = [p["ret"] for p in P]

        def pear(x, y):
            n = len(x)
            mx, my = sum(x) / n, sum(y) / n
            sx = math.sqrt(sum((a - mx) ** 2 for a in x))
            sy = math.sqrt(sum((b - my) ** 2 for b in y))
            return sum((x[i] - mx) * (y[i] - my) for i in range(n)) / (sx * sy) if sx and sy else None
        print("  skor ~ notional : %+.3f   (kod: marjin_pct %%8-12'ye DOYUYOR)" % pear(sk, nn))
        print("  skor ~ getiri   : %+.3f" % pear(sk, rr))
        s = sorted(P, key=lambda p: p["skor"])
        d = len(s) // 3
        print("\n  gercek pozisyonlar, skor ucte birlerine gore:")
        print("  %-14s %5s %10s %11s %11s" % ("dilim", "N", "ort skor", "ort ret%", "net $"))
        for i2, ad in enumerate(("dusuk", "orta", "yuksek")):
            w = s[i2 * d:(i2 + 1) * d] if i2 < 2 else s[2 * d:]
            print("  %-14s %5d %10.1f %+10.3f%% %+10.2f"
                  % (ad, len(w), sum(p["skor"] for p in w) / len(w),
                     sum(p["ret"] for p in w) / len(w), sum(p["net"] for p in w)))

    print("\n" + "=" * 108)
    print("⚠️ K1 gecse bile 'esigi ters cevir' DEMEK DEGIL: skor<45 kolu HIC")
    print("   islem gormemis bir populasyon; portfoy asamasi + ikinci epizot gerekir.")
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
