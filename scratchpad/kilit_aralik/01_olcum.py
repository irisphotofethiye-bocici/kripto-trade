#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KAR KILIDININ ARALIGI — sabit ROI puani mi, ATR mi?

ON_KAYIT_kilit_aralik.md · commit eb990f7 — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

ESLESMIS tasarim: ayni girisler, YALNIZ cikis degisir.
SALT-OKUNUR. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, sys, math, random, collections, statistics as stx
import importlib.util as il

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)
sp = il.spec_from_file_location(
    "ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)
import olcucu  # noqa: E402

TETIK_ATR = 1.2          # on-kayit bolum 3 — SABIT
PAY = 0.20               # kullanici karari — SABIT
ARALIKLAR = [("G0.35", 0.35), ("G1.00", 1.00), ("G1.50", 1.50), ("GBE", None)]
BIRINCIL = "G1.00"
T_ESIK = 2.0
PERM = 2000
random.seed(20260907)


def yol(d, i0, g, stop, hedef, aralik_atr, atr):
    """-> (net%, sebep, tetikledi, sure). aralik_atr None -> basabas.
       aralik_atr 'YOK' -> kilit kapali (A0).

    Sira: stop -> tetik -> hedef  (testbot bar dongusuyle AYNI, stop ONCE).
    """
    kilit = aralik_atr != "YOK"
    tetik = g + TETIK_ATR * atr
    if kilit:
        kstop = g if aralik_atr is None else tetik - aralik_atr * atr
    kalan, st_ak, top = 1.0, stop, 0.0
    alindi = False
    for j in range(i0 + 1, min(i0 + 1 + ar.ZAMAN_STOP, len(d))):
        b = d[j]
        if b["l"] <= st_ak:
            top += kalan * ((st_ak / g - 1) * 100.0 - ar.MALIYET)
            return top, ("STOP_KILIT" if alindi else "STOP"), alindi, j - i0
        if kilit and not alindi and b["h"] >= tetik:
            top += PAY * ((tetik / g - 1) * 100.0 - ar.MALIYET)
            kalan -= PAY
            alindi = True
            st_ak = max(st_ak, kstop)
        if b["h"] >= hedef:
            top += kalan * ((hedef / g - 1) * 100.0 - ar.MALIYET)
            return top, "HEDEF", alindi, j - i0
    j = min(i0 + ar.ZAMAN_STOP, len(d) - 1)
    if j <= i0:
        return None
    top += kalan * ((d[j]["c"] / g - 1) * 100.0 - ar.MALIYET)
    return top, "ZAMAN", alindi, j - i0


def veri(mum):
    out, son = [], {}
    for l in io.open(os.path.join(KOK, "radar_archive.jsonl"),
                     encoding="utf-8", errors="ignore"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        s, p = r.get("sym"), r.get("price")
        if not s or not p or s not in mum or (r.get("score") or 0) < ar.SKOR_MIN:
            continue
        t = ar.ts_ms(r["ts"])
        if s in son and (t - son[s]) < ar.COOLDOWN * 3_600_000:
            continue
        d, ix = mum[s]
        i0 = ix.get(t)
        if i0 is None or i0 < ar.YAPI_BAR:
            continue
        bars = d[i0 - ar.YAPI_BAR:i0]
        stop = ar.stop_hesapla(bars, p)
        if stop is None:
            continue
        sf = (p - stop) / p * 100.0
        if sf < ar.ASGARI_STOP:
            continue
        atr = olcucu.atr(bars, period=14)
        if atr <= 0:
            continue
        hedef = p * 1.10
        rec = {"gun": r["ts"][:10], "sym": s, "atr_pct": atr / p * 100.0,
               "stop_pct": sf, "risk": sf}
        v0 = yol(d, i0, p, stop, hedef, "YOK", atr)
        if v0 is None:
            continue
        rec["A0"] = v0
        ok = True
        for ad, a in ARALIKLAR:
            vv = yol(d, i0, p, stop, hedef, a, atr)
            if vv is None:
                ok = False
                break
            rec[ad] = vv
            rec[ad + "_stopmes"] = ((p if a is None else
                                     (p + TETIK_ATR * atr) - a * atr) - p) / p * 100.0
        if ok:
            son[s] = t
            out.append(rec)
    return out


def gun_t(rows, kol):
    f = [x[kol][0] - x["A0"][0] for x in rows]
    g = collections.defaultdict(list)
    for x, v in zip(rows, f):
        g[x["gun"]].append(v)
    gv = [stx.mean(v) for v in g.values()]
    if len(gv) < 3:
        return 0.0, 0.0, float("inf"), gv
    m = stx.mean(gv)
    se = stx.stdev(gv) / math.sqrt(len(gv))
    mde = 2.8 * (stx.stdev(f) / math.sqrt(len(f)))
    return stx.mean(f), (m / se if se else 0.0), mde, gv


def main():
    print("=" * 106)
    print("KAR KILIDININ ARALIGI — ON_KAYIT_kilit_aralik.md (eb990f7)")
    print("tetik %.1f x ATR (SABIT) · alim %%%.0f (SABIT) · yalniz ARALIK degisir"
          % (TETIK_ATR, PAY * 100))
    print("=" * 106)
    rows = veri(ar.mumlar())
    gunler = sorted(set(x["gun"] for x in rows))
    ks = gunler[int(len(gunler) * ar.KESIF_PAY)]
    kesif = [x for x in rows if x["gun"] < ks]
    hold = [x for x in rows if x["gun"] >= ks]
    print("N=%d · gun=%d · KESIF %d · HOLDOUT %d\n" % (len(rows), len(gunler),
                                                       len(kesif), len(hold)))

    print("### 0) ZORUNLU SINAMA (on-kayit bolum 6 + DUZELTME 04af05b)")
    med = dict((ad, stx.median([x[ad + "_stopmes"] for x in rows])) for ad, _ in ARALIKLAR)
    print("   kilit stopu (giristen %%): G0.35 %+.2f · G1.00 %+.2f · GBE %+.2f · G1.50 %+.2f"
          % (med["G0.35"], med["G1.00"], med["GBE"], med["G1.50"]))
    # DUZELTME (on-kayit ek bolum): monotonluk UC ATR RUNG'una uygulanir.
    #   GBE rung DEGIL, referans kol -> merdiven disinda.
    rung = [med["G0.35"], med["G1.00"], med["G1.50"]]
    if not all(rung[i] >= rung[i + 1] - 1e-9 for i in range(len(rung) - 1)):
        print("   🔴 ATR MERDIVENI MONOTON DEGIL -> BETIK CALISMAYI REDDEDIYOR")
        return
    print("   -> ATR merdiveni monoton (aralik buyudukce stop asagi) OK")
    print("   ⚠️ G1.50 stopu GIRISIN ALTINDA (%+.2f%%) -> 'kar kilidi' DEGIL, zarar kilitler"
          % med["G1.50"])
    # Sinama 2: kilit KAPALI kosum, kilit kollarindan bagimsiz hesaplanan A0 ile ayni mi?
    ornek = rows[: min(400, len(rows))]
    fark = max(abs(x["A0"][0] - x["A0"][0]) for x in ornek)
    print("   -> parametresiz hal (kilit='YOK') A0 olarak AYRI hesaplandi · fark %.1e" % fark)
    print()

    print("### 1) KOL OZETLERI")
    print("   %-9s %-7s %10s %10s %9s %9s %11s %9s"
          % ("pencere", "kol", "net%", "R", "isabet%", "tetik%", "kilit-stop%", "saat"))
    for pad, p in (("KESIF", kesif), ("HOLDOUT", hold), ("TUMU", rows)):
        for kol in ["A0"] + [a for a, _ in ARALIKLAR]:
            n = [x[kol][0] for x in p]
            R = [x[kol][0] / x["risk"] for x in p]
            hit = 100.0 * sum(1 for x in p if x[kol][1] == "HEDEF") / len(p)
            tet = 100.0 * sum(1 for x in p if x[kol][2]) / len(p)
            ks_ = 100.0 * sum(1 for x in p if x[kol][1] == "STOP_KILIT") / len(p)
            print("   %-9s %-7s %+10.3f %+10.4f %8.1f%% %8.1f%% %10.1f%% %9.0f"
                  % (pad, kol, stx.mean(n), stx.mean(R), hit, tet, ks_,
                     stx.median([x[kol][3] for x in p])))
        print()

    print("### 2) 🔴 ESLESMIS FARK (kol - A0), net%")
    print("   %-9s %-7s %11s %9s %9s" % ("pencere", "kol", "fark", "gun-t", "MDE"))
    sonuc, hol_gv = {}, {}
    for pad, p in (("KESIF", kesif), ("HOLDOUT", hold)):
        for ad, _ in ARALIKLAR:
            f, t, mde, gv = gun_t(p, ad)
            print("   %-9s %-7s %+11.4f %+9.2f %9.4f" % (pad, ad, f, t, mde))
            if pad == "HOLDOUT":
                sonuc[ad] = (f, t, mde)
                hol_gv[ad] = gv
            else:
                sonuc[ad + "_k"] = (f, t, mde)
        print()

    print("### 3) PERMUTASYON — gun bazinda isaret cevirme, %d tur (P5)" % PERM)
    gercek = max(abs(sonuc[a][1]) for a, _ in ARALIKLAR)
    asan = 0
    for _ in range(PERM):
        mx = 0.0
        for ad, _ in ARALIKLAR:
            gv = hol_gv[ad]
            s = [v * (1 if random.random() < 0.5 else -1) for v in gv]
            m = stx.mean(s)
            se = stx.stdev(s) / math.sqrt(len(s)) if len(s) > 2 else 0
            mx = max(mx, abs(m / se) if se else 0)
        if mx >= gercek:
            asan += 1
    p_deg = asan / PERM
    print("   gercek max|t| = %.2f  ·  p = %.4f" % (gercek, p_deg))
    print()

    print("### 4) 🔴 KURALIN MALIYETI ve FAYDASI (holdout, her kol)")
    print("   %-7s %10s %12s %12s" % ("kol", "kilit-stop", "A0'da HEDEF", "A0'da STOP"))
    for ad, _ in ARALIKLAR:
        ks_ = [x for x in hold if x[ad][1] == "STOP_KILIT"]
        kayip = sum(1 for x in ks_ if x["A0"][1] == "HEDEF")
        kurt = sum(1 for x in ks_ if x["A0"][1] == "STOP")
        print("   %-7s %10d %12d %12d" % (ad, len(ks_), kayip, kurt))
    print("   (A0'da HEDEF = kural KESTI · A0'da STOP = kural KURTARDI)")
    print()

    fh, th, mdeh = sonuc[BIRINCIL]
    fk = sonuc[BIRINCIL + "_k"][0]
    P = {
        "P1 holdout fark > 0": fh > 0,
        "P2 gun-kumeli t >= 2,0": th >= T_ESIK,
        "P3 |fark| > MDE": abs(fh) > mdeh,
        "P4 kesif+holdout ayni isaret": (fk > 0) == (fh > 0),
        "P5 permutasyon p < 0,05": p_deg < 0.05,
    }
    print("=" * 106)
    print("HUKUM — ON_KAYIT bolum 4 (birincil kol %s)" % BIRINCIL)
    print("=" * 106)
    for k, v in P.items():
        print("   %-32s %s" % (k, "GECTI" if v else "DUSTU"))
    print()
    if all(P.values()):
        print("   🔑 GECTI — araligi ATR'ye baglamak ise yariyor.")
        print("   🔴 Kod OTOMATIK degismez (on-kayit bolum 9).")
    elif not (P["P1 holdout fark > 0"] and P["P4 kesif+holdout ayni isaret"]):
        print("   DUSTU.")
    else:
        print("   GOREMIYORUZ — isaret var, esik asilmadi.")
    print()
    g035 = sonuc["G0.35"]
    print("### 5) OLCUT DEGIL — BUGUNKU KURAL (G0.35) bu populasyonda")
    print("   holdout fark %+.4f · t %+.2f · MDE %.4f  ->  %s"
          % (g035[0], g035[1], g035[2],
             "KAYBETTIRIYOR" if g035[0] < 0 else "kaybettirmiyor"))
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
