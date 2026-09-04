#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pos<0.25 KENARI MEKANIKTEN SAG CIKIYOR MU? — Asama 2.
On-kayit: ON_KAYIT_pos_mekanik.md (commit 5338860, KOSUMDAN ONCE). Olcutler SABIT.

🔑 MEKANIK YENIDEN YAZILMAZ, CAGRILIR: seviyeler() ve oynat() fonksiyonlari
   stop_mu_sure_mu.py'den OLDUGU GIBI alinir (kopyalanmaz — kaynaktan exec).
   Modulde __main__ korumasi olmadigi icin yalniz `oynat` sonuna kadarki
   kisim calistirilir; analiz kismi kosmaz.

🔴 K3 (mekanik esitligi) ZORUNLU: pos<0.25 bant dibi demek, muhtemelen daha
   oynak -> daha genis stop. Ayrisiyorsa kiyas BOZUK ve oyle yazilir.
🔴 BIRIM = SEMBOL-GUN · gun-kumeli t.
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
MUM = os.path.join(PROJE, "scratchpad", "aday_pencere_1h")
KAYNAK = os.path.join(PROJE, "scratchpad", "stop_mu_sure_mu.py")
BAS = "2026-08-21"
SAAT_MS = 3600 * 1000


def mekanik_yukle():
    """seviyeler/oynat'i KAYNAKTAN al — kopyalama YOK, suruklenme YOK."""
    src = open(KAYNAK, encoding="utf-8").read()
    kes = src.index('return kar, j - i, "ZAMAN_STOP"')
    kes = src.index("\n", kes) + 1
    ns = {"__name__": "_mek", "__file__": KAYNAK}
    tut = _sys.stdout
    _sys.stdout = io.StringIO()
    try:
        exec(compile(src[:kes], KAYNAK, "exec"), ns)
    finally:
        _sys.stdout = tut
    for f in ("seviyeler", "oynat", "atr_wilder"):
        if f not in ns:
            raise SystemExit("MEKANIK YUKLENEMEDI: %s yok — betik REDDEDIYOR" % f)
    return ns


def utc_ts(s):
    d = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M") - datetime.timedelta(hours=3)
    return int((d - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)


def sg_gun(w, alan):
    """-> (sembol-gun listesi, gun ortalamalari)"""
    g = collections.defaultdict(list)
    for x in w:
        if x.get(alan) is not None:
            g[(x["sym"], x["_gun"])].append(x[alan])
    sgo = {k: sum(v) / len(v) for k, v in g.items()}
    gun = collections.defaultdict(list)
    for (s, d), v in sgo.items():
        gun[d].append(v)
    return list(sgo.values()), [sum(v) / len(v) for v in gun.values()]


def ist(w, alan):
    sg, gv = sg_gun(w, alan)
    if len(gv) < 3:
        return (sum(gv) / len(gv) if gv else None), None, len(sg), len(gv), None
    m, sd = sum(gv) / len(gv), statistics.stdev(gv)
    se = sd / math.sqrt(len(gv))
    return m, (m / se if se else None), len(sg), len(gv), (2.0 * se if se else None)


def fark_t(a, b, alan):
    _, ga = sg_gun(a, alan)
    _, gb = sg_gun(b, alan)
    if len(ga) < 3 or len(gb) < 3:
        return None, None, None
    ma, mb = sum(ga) / len(ga), sum(gb) / len(gb)
    se = math.sqrt(statistics.variance(ga) / len(ga) + statistics.variance(gb) / len(gb))
    return (ma - mb), ((ma - mb) / se if se else None), (2.0 * se if se else None)


def main():
    M = mekanik_yukle()
    seviyeler, oynat = M["seviyeler"], M["oynat"]
    MALIYET = M["MALIYET"]
    ASGARI = M["ASGARI_STOP"]
    YAPI = M["YAPI_BAR"]
    ZS = M["ZAMAN_STOP"]

    print("pos<0.25 KENARI MEKANIKTEN SAG CIKIYOR MU? — Asama 2")
    print("on-kayit ON_KAYIT_pos_mekanik.md (5338860) · olcutler SABIT")
    print("=" * 108)
    print("mekanik KAYNAKTAN yuklendi: seviyeler/oynat · maliyet %%%.3f · asgari stop %%%.1f"
          % (MALIYET, ASGARI))
    print("YAPI_BAR %d · ZAMAN_STOP %d saat" % (YAPI, ZS))

    # ---------------------------------------------------------------- mumlar
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
        seri[fn[:-5]] = {"t": [x[0] for x in b], "h": [x[1] for x in b],
                         "l": [x[2] for x in b], "c": [x[3] for x in b],
                         "ix": {x[0]: j for j, x in enumerate(b)}}
    print("saatlik seri: %d sembol" % len(seri))

    # ---------------------------------------------------------------- arsiv
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
        if not s or s not in seri or r.get("pos") is None:
            eleme["seri_yok"] += 1
            continue
        S = seri[s]
        t0 = utc_ts(ts)
        i = S["ix"].get(t0 - (t0 % SAAT_MS))
        if i is None or i < YAPI:
            eleme["gecmis_yetersiz"] += 1
            continue
        sv = seviyeler(S["h"], S["l"], S["c"], i, "LONG")
        if not sv:
            eleme["seviye_yok"] += 1
            continue
        sl, tp1, tp2, risk, a = sv
        ref = S["c"][i]
        stop_pct = abs(ref - sl) / ref * 100.0
        if stop_pct < ASGARI:
            eleme["asgari_stop"] += 1
            continue
        kar, sure, sebep = oynat(S["h"], S["l"], S["c"], i, "LONG", sl, tp1, tp2, risk, a)
        kesik = (i + 1 + ZS) > len(S["c"])
        # ham 4 saat (kiyas icin)
        j4 = S["ix"].get(t0 - (t0 % SAAT_MS) + 4 * SAAT_MS)
        r["_gun"] = ts[:10]
        r["mek"] = kar - MALIYET
        r["ham4"] = ((S["c"][j4] - ref) / ref * 100.0) if j4 is not None else None
        r["stop_pct"] = stop_pct
        r["sure"] = sure
        r["sebep"] = sebep
        r["kesik"] = kesik
        R.append(r)

    print("olculen satir: %d · eleme: %s" % (len(R), dict(eleme)))
    if len(R) < 100:
        print("N yetersiz")
        return

    A = [x for x in R if x["pos"] < 0.25]
    B = [x for x in R if x["pos"] >= 0.25]

    # ------------------------------------------------- K3 MEKANIK ESITLIGI
    print("\n" + "=" * 108)
    print("1) 🔴 K3 — MEKANIK ESITLIGI (bu gecmezse kiyas BOZUK)")
    print("-" * 108)
    print("  %-14s %8s %11s %11s %10s %10s %9s"
          % ("kol", "satir", "stop gen.%", "stop olma%", "med sure", "TP1+%", "kesik%"))
    olc = {}
    for ad, w in (("pos<0.25", A), ("pos>=0.25", B)):
        sw = sum(x["stop_pct"] for x in w) / len(w)
        so = 100.0 * sum(1 for x in w if str(x["sebep"]).startswith("STOP")) / len(w)
        tp = 100.0 * sum(1 for x in w if x["sebep"] in ("TP2", "STOP_TP1SONRASI")) / len(w)
        ks = 100.0 * sum(1 for x in w if x["kesik"]) / len(w)
        olc[ad] = (sw, so)
        print("  %-14s %8d %10.2f%% %10.1f%% %9.1f %9.1f%% %8.1f%%"
              % (ad, len(w), sw, so, statistics.median([x["sure"] for x in w]), tp, ks))
    o1 = olc["pos<0.25"][0] / olc["pos>=0.25"][0]
    o2 = olc["pos<0.25"][1] / olc["pos>=0.25"][1] if olc["pos>=0.25"][1] else 0
    k3 = (1 / 1.5) <= o1 <= 1.5 and (1 / 1.5) <= o2 <= 1.5
    print("  oran: stop genisligi %.2fx · stop olma %.2fx  -> K3 %s"
          % (o1, o2, "GECTI" if k3 else "DUSTU (kiyas BOZUK, aynen yazilir)"))

    print("\n  cikis sebebi dagilimi:")
    for ad, w in (("pos<0.25", A), ("pos>=0.25", B)):
        c = collections.Counter(x["sebep"] for x in w)
        top = sum(c.values())
        print("    %-12s %s" % (ad, {k: "%.0f%%" % (100.0 * v / top) for k, v in c.most_common()}))

    # ------------------------------------------------- HAM vs MEKANIK
    print("\n" + "=" * 108)
    print("2) HAM vs MEKANIK — yan yana (CLAUDE.md zorunlulugu)")
    print("-" * 108)
    print("  %-14s %10s %11s %8s %10s %11s %8s"
          % ("kol", "sem-gun", "HAM 4sa %", "t", "sem-gun", "MEKANIK %", "t"))
    for ad, w in (("pos<0.25", A), ("pos>=0.25", B)):
        mh, th, nh, _, _ = ist(w, "ham4")
        mm, tm, nm, _, _ = ist(w, "mek")
        print("  %-14s %10d %+10.3f%% %8s %10d %+10.3f%% %8s"
              % (ad, nh, mh, ("%+.2f" % th) if th else "-",
                 nm, mm, ("%+.2f" % tm) if tm else "-"))
    fh, tfh, _ = fark_t(A, B, "ham4")
    fm, tfm, mde = fark_t(A, B, "mek")
    print("  " + "-" * 100)
    print("  %-14s %10s %+10.3f%% %8s %10s %+10.3f%% %8s"
          % ("FARK", "", fh, ("%+.2f" % tfh) if tfh else "-",
             "", fm, ("%+.2f" % tfm) if tfm else "-"))

    # ------------------------------------------------- BIRINCIL HUKUM
    print("\n" + "=" * 108)
    print("3) BIRINCIL HUKUM")
    print("=" * 108)
    print("  mekanikli fark : %+.3f%%  ·  gun-t %s  ·  MDE %s"
          % (fm, ("%+.2f" % tfm) if tfm else "-", ("%.3f" % mde) if mde else "-"))
    print("  ham fark       : %+.3f%%" % fh)
    pay = (fm / fh * 100.0) if fh else 0.0
    print("  korunan pay    : %%%.0f" % pay)
    k1 = fm > 0 and tfm is not None and tfm >= 2.0
    k2 = pay >= 50.0
    print()
    print("  K1  mekanikli fark>0 ve t>=+2,0 : %-6s" % ("GECTI" if k1 else "DUSTU"))
    print("  K2  korunan pay >= %%50          : %-6s" % ("GECTI" if k2 else "DUSTU"))
    print("  K3  mekanik esitligi            : %-6s" % ("GECTI" if k3 else "DUSTU"))
    print()
    if k1 and k2 and k3:
        h = "GECTI — kenar mekanikten SAG CIKIYOR"
    elif k1 and not k3:
        h = "ZAYIF — fark var ama kollar mekanikte AYRISIYOR, kiyas bozuk"
    elif k1:
        h = "ZAYIF — K1 gecti, kenarin buyuk kismi mekanikte yendi"
    else:
        h = "DUSTU — kenar mekanikten SAG CIKMIYOR"
    print("  HUKUM: %s" % h)
    if mde and abs(fm) < mde:
        print("  GUC: |fark| %.3f < MDE %.3f -> 'goremiyoruz'" % (abs(fm), mde))
    elif mde:
        print("  GUC: |fark| %.3f > MDE %.3f -> orneklem bu buyuklugu gorebiliyor" % (abs(fm), mde))

    print("\n" + "=" * 108)
    print("⚠️ Gecse bile bilesen KALDIRILMAZ: portfoy asamasi ve IKINCI BOGA")
    print("   epizodu gerekiyor. 13 gunluk tek epizot kapi degistirmez.")
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
