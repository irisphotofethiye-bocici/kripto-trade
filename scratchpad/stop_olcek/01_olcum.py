#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STOP ve HEDEF OYNAKLIK OLCEGINE UYUYOR MU?

ON_KAYIT_stop_hedef_olcek.md · commit 838c4e5 — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

KOLLAR (ayni girisler, hicbiri STOPSUZ — CLAUDE.md deseni (b)):
   A0 mevcut   : olcucu uclu stop mantigi, ATR14 · sabit %10 hedef
   A1 taze ATR : ayni mantik, ATR3        · sabit %10 hedef
   A2 olcekli  : ATR14                    · hedef m x ATR14

SALT-OKUNUR. Arsiv context'e yuklenmez. Bot dosyalarina yazim YOK.
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
import testbot, olcucu, evren   # noqa: E402

ARSIV = os.path.join(KOK, "radar_archive.jsonl")
KDIR = os.path.join(KOK, "scratchpad", "fund_ls", "klines")

KAYMA = 3                 # radar_archive.ts YEREL (UTC+3) — dogrulandi
HEDEF_PCT = 10.0
ZAMAN_STOP = 48           # saat
MALIYET = 0.09            # % gidis-donus
ASGARI_STOP = 2.0         # kripto-config testbot.asgari_stop_pct
TEKRAR_SAAT = 4.0         # botun cooldown'u -> sahte tekrar onlenir
NBAR = int(evren.esik("olcucu_nbar_stop", 10))
YAPI_BAR = 120            # stop yapisi icin geriye bakilan bar


# ------------------------------------------------------------------ yardimcilar
def ts_ms(ts):
    d = dt.datetime.strptime(ts[:16], "%Y-%m-%d %H:%M")
    d = (d - dt.timedelta(hours=KAYMA)).replace(minute=0, second=0, microsecond=0)
    return int(d.replace(tzinfo=dt.UTC).timestamp() * 1000)


def gun_kumeli_t(ciftler):
    """ciftler: [(gun, fark), ...] -> gunluk ortalamalarin t'si"""
    g = collections.defaultdict(list)
    for gun, f in ciftler:
        g[gun].append(f)
    v = [stx.mean(x) for x in g.values()]
    if len(v) < 3:
        return 0.0, 0.0, len(v)
    m = stx.mean(v)
    se = stx.stdev(v) / math.sqrt(len(v))
    return m, ((m / se) if se > 0 else 0.0), len(v)


def mde_cift(farklar):
    if len(farklar) < 3:
        return float("inf")
    return 2.8 * stx.stdev(farklar) / math.sqrt(len(farklar))


# ------------------------------------------------------------------ veri
def mumlar():
    out = {}
    for f in os.listdir(KDIR):
        if not f.endswith(".json"):
            continue
        try:
            d = json.load(open(os.path.join(KDIR, f), encoding="utf-8"))
        except Exception:
            continue
        d.sort(key=lambda x: x["t"])
        out[f[:-5]] = (d, {int(x["t"]): i for i, x in enumerate(d)})
    return out


def girisler(mum):
    """radar_archive -> NOTR-LONG kararlari. IKI set: taker ACIK / KAPALI."""
    acik, kapali = [], []
    son = {}
    with open(ARSIV, encoding="utf-8", errors="ignore") as f:
        for l in f:
            l = l.strip()
            if not l:
                continue
            try:
                r = json.loads(l)
            except Exception:
                continue
            s = r.get("sym")
            if not s or s not in mum or not r.get("price"):
                continue
            if r.get("smart") is None or r.get("taker") is None:
                continue
            pil = {"top_ls": r.get("top_ls"), "glob_ls": r.get("glob_ls"),
                   "taker": r.get("taker"), "smart": r.get("smart")}
            v = []
            try:
                k = testbot.karar_yon("NOTR", r, pil, False, veto_out=v)
            except Exception:
                continue
            long_karar = bool(k and k[0] == "LONG")
            # taker KAPALI seti: karar LONG ya da tek engel taker_soguma
            taker_engeli = (not long_karar and v
                            and all(x.get("kategori") == "taker_soguma" for x in v))
            if not (long_karar or taker_engeli):
                continue
            t = ts_ms(r["ts"])
            if s in son and (t - son[s]) < TEKRAR_SAAT * 3_600_000:
                continue
            son[s] = t
            kayit = {"sym": s, "ts": r["ts"], "t": t, "price": r["price"],
                     "gun": r["ts"][:10], "chg24": r.get("chg24")}
            if long_karar:
                acik.append(kayit)
            kapali.append(kayit)
    return acik, kapali


# ------------------------------------------------------------------ mekanik
def stop_hesapla(bars, ref, atr_period):
    """olcucu'nun KENDI uclu mantigi. Yalniz ATR periyodu degisir."""
    a = olcucu.atr(bars, period=atr_period)
    if a <= 0:
        return None, 0.0
    highs, lows = olcucu.swings(bars)
    _, sup = olcucu.nearest(ref, highs, lows)
    adaylar = []
    if sup is not None and (ref - sup) <= 3 * a:
        adaylar.append(sup - 0.25 * a)
    nbar_low = min(b["l"] for b in bars[-NBAR:])
    if nbar_low < ref:
        adaylar.append(nbar_low - 0.25 * a)
    adaylar.append(ref - 1.5 * a)
    gecerli = [x for x in adaylar if x < ref]
    return (max(gecerli) if gecerli else ref - 1.5 * a), a


def simule(d, ix, t0, giris, stop, hedef):
    """Fitil tetikli. Ayni barda ikisi de -> STOP (muhafazakar).
    -> (net_R, sebep, saat)"""
    i0 = ix.get(t0)
    if i0 is None:
        return None
    risk = giris - stop
    if risk <= 0:
        return None
    for j in range(i0 + 1, min(i0 + 1 + ZAMAN_STOP, len(d))):
        b = d[j]
        if b["l"] <= stop:
            ham = (stop / giris - 1) * 100.0
            return ((ham - MALIYET) / (risk / giris * 100.0), "STOP", j - i0)
        if b["h"] >= hedef:
            ham = (hedef / giris - 1) * 100.0
            return ((ham - MALIYET) / (risk / giris * 100.0), "HEDEF", j - i0)
    j = min(i0 + ZAMAN_STOP, len(d) - 1)
    if j <= i0:
        return None
    ham = (d[j]["c"] / giris - 1) * 100.0
    return ((ham - MALIYET) / (risk / giris * 100.0), "ZAMAN", j - i0)


def kol_kos(gir, mum, m_carpan):
    """Her giris icin uc kolu da hesaplar. A0'in asgari_stop'unu GECEN girisler
    tum kollarda kullanilir (eslesme korunur; on-kayit bolum 4)."""
    out = []
    a1_red = a1_ek = 0
    for g in gir:
        d, ix = mum[g["sym"]]
        i0 = ix.get(g["t"])
        if i0 is None or i0 < YAPI_BAR:
            continue
        bars = d[i0 - YAPI_BAR:i0]          # KAPANMIS barlar (karar barindan once)
        ref = g["price"]
        s14, a14 = stop_hesapla(bars, ref, 14)
        s3, a3 = stop_hesapla(bars, ref, 3)
        if s14 is None or s3 is None:
            continue
        sf14 = (ref - s14) / ref * 100.0
        sf3 = (ref - s3) / ref * 100.0
        if sf14 < ASGARI_STOP:               # A0'in giris kapisi -> eslesme tabani
            if sf3 >= ASGARI_STOP:
                a1_ek += 1
            continue
        if sf3 < ASGARI_STOP:
            a1_red += 1
        r0 = simule(d, ix, g["t"], ref, s14, ref * (1 + HEDEF_PCT / 100.0))
        r1 = simule(d, ix, g["t"], ref, s3, ref * (1 + HEDEF_PCT / 100.0))
        h2 = ref + m_carpan * a14
        r2 = simule(d, ix, g["t"], ref, s14, h2)
        if not (r0 and r1 and r2):
            continue
        out.append({"gun": g["gun"], "sym": g["sym"], "chg24": g.get("chg24"),
                    "sf14": sf14, "sf3": sf3, "atr14_pct": a14 / ref * 100.0,
                    "h2_pct": (h2 / ref - 1) * 100.0,
                    "A0": r0, "A1": r1, "A2": r2})
    return out, a1_red, a1_ek


def kol_ozet(rows, ad):
    r = [x[ad][0] for x in rows]
    seb = collections.Counter(x[ad][1] for x in rows)
    sure = [x[ad][2] for x in rows]
    n = len(r)
    return {"N": n, "ortR": stx.mean(r), "toplamR": sum(r),
            "stop%": 100.0 * seb["STOP"] / n, "hedef%": 100.0 * seb["HEDEF"] / n,
            "zaman%": 100.0 * seb["ZAMAN"] / n, "sure": stx.median(sure)}


def kars(rows, kol, ad_set):
    """A0'a gore eslesmis fark + on-kayitin S1..S4'u."""
    farklar = [x[kol][0] - x["A0"][0] for x in rows]
    ciftler = [(x["gun"], f) for x, f in zip(rows, farklar)]
    m, t, ng = gun_kumeli_t(ciftler)
    md = mde_cift(farklar)
    ort = stx.mean(farklar)
    # S3 iki yari
    gs = sorted(set(x["gun"] for x in rows))
    orta = gs[len(gs) // 2]
    fa = [f for x, f in zip(rows, farklar) if x["gun"] < orta]
    fb = [f for x, f in zip(rows, farklar) if x["gun"] >= orta]
    s3 = bool(fa and fb and (stx.mean(fa) > 0) == (stx.mean(fb) > 0))
    # S4 yogunlasma
    gd = collections.defaultdict(list)
    for x, f in zip(rows, farklar):
        gd[x["gun"]].append(f)
    eniyi = sorted(gd, key=lambda k: -stx.mean(gd[k]))[:2]
    kalan = [f for x, f in zip(rows, farklar) if x["gun"] not in eniyi]
    kalan5 = sorted(kalan)[:-5] if len(kalan) > 5 else kalan
    s4 = bool(kalan5 and stx.mean(kalan5) > 0)
    return {"set": ad_set, "kol": kol, "N": len(farklar), "ort": ort,
            "gun_ort": m, "t": t, "gun": ng, "mde": md,
            "S1": t >= 2.5, "S2": abs(ort) > md, "S3": s3, "S4": s4,
            "yari_A": stx.mean(fa) if fa else 0, "yari_B": stx.mean(fb) if fb else 0,
            "kalan": stx.mean(kalan5) if kalan5 else 0}


def main():
    print("=" * 100)
    print("STOP/HEDEF OLCEK — ON_KAYIT_stop_hedef_olcek.md (838c4e5)")
    print("🔴 Gecse bile BOTA KONMAZ — once portfoy simulasyonu (on-kayit bolum 8).")
    print("=" * 100)
    mum = mumlar()
    print("mum: %d sembol" % len(mum))
    acik, kapali = girisler(mum)
    print("giris (taker ACIK) : %d   ·   (taker KAPALI) : %d" % (len(acik), len(kapali)))
    if not kapali:
        print("giris yok")
        return

    # m carpani: medyan ATR14/fiyat uzerinden, KOSUMDAN ONCE formulle sabit
    orn = []
    for g in kapali[:600]:
        d, ix = mum[g["sym"]]
        i0 = ix.get(g["t"])
        if i0 is None or i0 < YAPI_BAR:
            continue
        a = olcucu.atr(d[i0 - YAPI_BAR:i0], period=14)
        if a > 0:
            orn.append(a / g["price"] * 100.0)
    if not orn:
        print("ATR ornegi yok")
        return
    med_atr = stx.median(orn)
    m_carpan_pct = HEDEF_PCT / med_atr
    print("medyan ATR14/fiyat = %.3f%%  ->  m = %.2f  (medyan islemde hedef tam %%%.0f)"
          % (med_atr, m_carpan_pct, HEDEF_PCT))
    print()

    tum = {}
    for ad, gir in (("taker ACIK", acik), ("taker KAPALI", kapali)):
        rows, a1red, a1ek = kol_kos(gir, mum, m_carpan_pct)
        if not rows:
            print("### %s — simule edilebilir giris YOK" % ad)
            continue
        tum[ad] = rows
        print("### GIRIS SETI: %s   (N=%d · gun %d)"
              % (ad, len(rows), len(set(x["gun"] for x in rows))))
        print("   A1'in asgari_stop'u: %d giris REDDEDERDI · %d giris EKLERDI (eslesme icin A0 tabani kullanildi)"
              % (a1red, a1ek))
        print()
        print("   %-6s %6s %9s %10s %9s %9s %9s %9s"
              % ("kol", "N", "ort R", "toplam R", "stop %", "hedef %", "zaman %", "sure(s)"))
        for kol in ("A0", "A1", "A2"):
            o = kol_ozet(rows, kol)
            print("   %-6s %6d %+9.4f %+10.1f %8.1f%% %8.1f%% %8.1f%% %9.0f"
                  % (kol, o["N"], o["ortR"], o["toplamR"], o["stop%"],
                     o["hedef%"], o["zaman%"], o["sure"]))
        print()
        print("   TESHIS — stop mesafesi ve hedef (medyan):")
        print("      A0 stop %%%.2f · A1 stop %%%.2f · A2 hedef %%%.2f (A0/A1 hedef %%%.0f)"
              % (stx.median([x["sf14"] for x in rows]),
                 stx.median([x["sf3"] for x in rows]),
                 stx.median([x["h2_pct"] for x in rows]), HEDEF_PCT))
        print()

    print("=" * 100)
    print("HUKUM — ON_KAYIT bolum 5 (olcutler kosumdan once sabitti)")
    print("=" * 100)
    sonuc = {}
    for ad, rows in tum.items():
        for kol in ("A1", "A2"):
            k = kars(rows, kol, ad)
            sonuc[(ad, kol)] = k
            print("   %-13s %s  N=%d gun=%d" % (ad, kol, k["N"], k["gun"]))
            print("      eslesmis fark ort %+.4f R · gun-ort %+.4f · t %+.2f · MDE %.4f"
                  % (k["ort"], k["gun_ort"], k["t"], k["mde"]))
            print("      S1 t>=2,5 %-6s S2 |fark|>MDE %-6s S3 iki yari %-6s S4 yogunlasma %s"
                  % ("GECTI" if k["S1"] else "dustu", "GECTI" if k["S2"] else "dustu",
                     "GECTI" if k["S3"] else "dustu", "GECTI" if k["S4"] else "dustu"))
            print("      (yari A %+.4f · yari B %+.4f · en iyi 2 gun+5 islem cikinca %+.4f)"
                  % (k["yari_A"], k["yari_B"], k["kalan"]))
    print()
    for kol in ("A1", "A2"):
        ks = [v for (a, k), v in sonuc.items() if k == kol]
        if len(ks) < 2:
            continue
        s5 = (ks[0]["ort"] > 0) == (ks[1]["ort"] > 0)
        hep = all(x["S1"] and x["S2"] and x["S3"] and x["S4"] for x in ks) and s5
        print("   %s -> S5 (iki giris setinde ayni isaret): %s   SONUC: %s"
              % (kol, "GECTI" if s5 else "dustu",
                 "🔑 GECTI" if hep else
                 ("DUSTU" if not all(x["S1"] and x["S2"] for x in ks)
                  else "BELIRSIZ -> A0 KALIR")))
    print()
    print("   ⚠️ ORTAK PAYDA: R = net/risk. risk~R korelasyonu MEKANIKTIR ->")
    print("      raporlanmadi (on-kayit bolum 6).")
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
