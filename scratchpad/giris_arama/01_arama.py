#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GIRIS KAPISI ARAMASI — kesif + AYRIK HOLDOUT

ON_KAYIT_giris_arama.md · commit fd932ca — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

🔴 HOLDOUT ADAY SECILENE KADAR ACILMAZ. Betik once kesif tablosunu basar,
   adayi OTOMATIK secer, SONRA holdout'u okur. Tek gecis.

SALT-OKUNUR. Arsiv context'e yuklenmez. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, sys, math, random, collections, statistics as stx
import datetime as dt

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)
import olcucu, evren   # noqa: E402

ARSIV = os.path.join(KOK, "radar_archive.jsonl")
KDIR = os.path.join(KOK, "scratchpad", "fund_ls", "klines")

KAYMA = 3
SKOR_MIN = 30.0
COOLDOWN = 4.0
HEDEF_PCT = 10.0
ZAMAN_STOP = 48
MALIYET = 0.09
ASGARI_STOP = 2.0
NBAR = int(evren.esik("olcucu_nbar_stop", 10))
YAPI_BAR = 120
KESIF_PAY = 0.60
DILIM = 5
MIN_N_KESIF = 100
MIN_N_HOLDOUT = 60

SUREKLI = ["score", "comp", "vol_x", "oi24", "oi3", "funding", "pos",
           "last1", "last3", "logfiyat", "mcap", "float_oran",
           "btc_chg24", "btc_chg3", "rel3"]
KATEGORIK = {"stage": ["BASLIYOR", "HAZIRLANIYOR", "izle"],
             "dusuk_float": [True, False], "erken": [True, False],
             "ayrisma": [True, False], "dip_yakit": [True, False]}

random.seed(20260906)


def ts_ms(ts):
    d = dt.datetime.strptime(ts[:16], "%Y-%m-%d %H:%M")
    d = (d - dt.timedelta(hours=KAYMA)).replace(minute=0, second=0, microsecond=0)
    return int(d.replace(tzinfo=dt.UTC).timestamp() * 1000)


def gun_kumeli_t(ciftler):
    g = collections.defaultdict(list)
    for gun, f in ciftler:
        g[gun].append(f)
    v = [stx.mean(x) for x in g.values()]
    if len(v) < 3:
        return 0.0, 0.0, len(v)
    m = stx.mean(v)
    se = stx.stdev(v) / math.sqrt(len(v))
    return m, ((m / se) if se > 0 else 0.0), len(v)


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


def stop_hesapla(bars, ref):
    a = olcucu.atr(bars, period=14)
    if a <= 0:
        return None
    highs, lows = olcucu.swings(bars)
    _, sup = olcucu.nearest(ref, highs, lows)
    ad = []
    if sup is not None and (ref - sup) <= 3 * a:
        ad.append(sup - 0.25 * a)
    nl = min(b["l"] for b in bars[-NBAR:])
    if nl < ref:
        ad.append(nl - 0.25 * a)
    ad.append(ref - 1.5 * a)
    gec = [x for x in ad if x < ref]
    return max(gec) if gec else ref - 1.5 * a


def simule(d, ix, t0, giris, stop, hedef):
    i0 = ix.get(t0)
    if i0 is None:
        return None
    risk_pct = (giris - stop) / giris * 100.0
    if risk_pct <= 0:
        return None
    for j in range(i0 + 1, min(i0 + 1 + ZAMAN_STOP, len(d))):
        b = d[j]
        if b["l"] <= stop:
            return ((stop / giris - 1) * 100.0 - MALIYET) / risk_pct, 0
        if b["h"] >= hedef:
            return ((hedef / giris - 1) * 100.0 - MALIYET) / risk_pct, 1
    j = min(i0 + ZAMAN_STOP, len(d) - 1)
    if j <= i0:
        return None
    return ((d[j]["c"] / giris - 1) * 100.0 - MALIYET) / risk_pct, 0


def veri_kur(mum):
    rows = []
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
            s, p = r.get("sym"), r.get("price")
            if not s or not p or s not in mum:
                continue
            if (r.get("score") or 0) < SKOR_MIN:
                continue
            t = ts_ms(r["ts"])
            if s in son and (t - son[s]) < COOLDOWN * 3_600_000:
                continue
            d, ix = mum[s]
            i0 = ix.get(t)
            if i0 is None or i0 < YAPI_BAR:
                continue
            bars = d[i0 - YAPI_BAR:i0]
            stop = stop_hesapla(bars, p)
            if stop is None:
                continue
            sf = (p - stop) / p * 100.0
            if sf < ASGARI_STOP:
                continue
            sim = simule(d, ix, t, p, stop, p * (1 + HEDEF_PCT / 100.0))
            if sim is None:
                continue
            son[s] = t
            rec = {"sym": s, "gun": r["ts"][:10], "R": sim[0], "hit": sim[1],
                   "stop_pct": sf,
                   "logfiyat": math.log10(p) if p > 0 else None}
            # SUREKLI alanlar SAYISALA zorlanir; arsivde bazi kayitlarda
            # (ornek: mcap) METIN geliyor -> None'a duser, hucreden dislanir.
            for k in ("score", "comp", "vol_x", "oi24", "oi3", "funding", "pos",
                      "last1", "last3", "mcap", "float_oran",
                      "btc_chg24", "btc_chg3", "rel3"):
                try:
                    rec[k] = float(r.get(k)) if r.get(k) is not None else None
                except (TypeError, ValueError):
                    rec[k] = None
            for k in KATEGORIK:
                rec[k] = r.get(k)
            rows.append(rec)
    return rows


def hucreler(rows, sahte=False):
    """-> [(ad, secici_fn)] · on-kayit bolum 5: yalniz UC dilimler + kategorik."""
    out = []
    alanlar = ["sahte"] if sahte else SUREKLI
    for a in alanlar:
        v = sorted(x[a] for x in rows if x.get(a) is not None)
        if len(v) < DILIM * 20:
            continue
        alt = v[len(v) // DILIM]
        ust = v[(DILIM - 1) * len(v) // DILIM]
        out.append(("%s <= %.4g (alt dilim)" % (a, alt),
                    (lambda k, e: (lambda x: x.get(k) is not None and x[k] <= e))(a, alt)))
        out.append(("%s >= %.4g (ust dilim)" % (a, ust),
                    (lambda k, e: (lambda x: x.get(k) is not None and x[k] >= e))(a, ust)))
    if not sahte:
        for a, duzeyler in KATEGORIK.items():
            for dz in duzeyler:
                out.append(("%s == %s" % (a, dz),
                            (lambda k, e: (lambda x: x.get(k) == e))(a, dz)))
    return out


def hucre_olc(rows, fn):
    ic = [x for x in rows if fn(x)]
    if not ic:
        return None
    R = [x["R"] for x in ic]
    hit = sum(x["hit"] for x in ic)
    sp = stx.median([x["stop_pct"] for x in ic])
    bb = 100.0 / (1 + HEDEF_PCT / sp) if sp > 0 else 100.0
    return {"N": len(ic), "ortR": stx.mean(R), "isabet": 100.0 * hit / len(ic),
            "stop_pct": sp, "basabas": bb, "ic": ic}


def main():
    print("=" * 100)
    print("GIRIS KAPISI ARAMASI — ON_KAYIT_giris_arama.md (fd932ca)")
    print("🔴 Holdout aday secilene kadar ACILMAZ.")
    print("=" * 100)
    mum = mumlar()
    rows = veri_kur(mum)
    if not rows:
        print("veri yok")
        return
    gunler = sorted(set(x["gun"] for x in rows))
    kes_son = gunler[int(len(gunler) * KESIF_PAY)]
    kesif = [x for x in rows if x["gun"] < kes_son]
    hold = [x for x in rows if x["gun"] >= kes_son]
    print("toplam giris %d · gun %d" % (len(rows), len(gunler)))
    print("KESIF   : %s .. %s   N=%d" % (gunler[0], kes_son, len(kesif)))
    print("HOLDOUT : %s .. %s   N=%d" % (kes_son, gunler[-1], len(hold)))
    print()

    tum = hucre_olc(rows, lambda x: True)
    tk = hucre_olc(kesif, lambda x: True)
    print("### 0) TABAN — hicbir kapi yokken")
    print("   tumu    N=%4d  ort R %+.4f  isabet %.1f%%  stop %%%.2f  basabas %.1f%%"
          % (tum["N"], tum["ortR"], tum["isabet"], tum["stop_pct"], tum["basabas"]))
    print("   kesif   N=%4d  ort R %+.4f  isabet %.1f%%" % (tk["N"], tk["ortR"], tk["isabet"]))
    print()

    hc = hucreler(kesif)
    print("### 1) KESIF TABLOSU — %d hucre arandi (on-kayit: 41 beklendi)" % len(hc))
    print("   %-34s %6s %10s %9s %9s %10s" %
          ("hucre", "N", "ort R", "isabet", "basabas", "isabet-bb"))
    sonuc = []
    for ad, fn in hc:
        o = hucre_olc(kesif, fn)
        if not o:
            continue
        uygun = o["N"] >= MIN_N_KESIF
        sonuc.append((ad, fn, o, uygun))
    for ad, fn, o, uygun in sorted(sonuc, key=lambda z: -z[2]["ortR"]):
        print("   %-34s %6d %+10.4f %8.1f%% %8.1f%% %+9.1f%s"
              % (ad, o["N"], o["ortR"], o["isabet"], o["basabas"],
                 o["isabet"] - o["basabas"], "" if uygun else "  (N<100, aday degil)"))
    print()

    # --- NEGATIF KONTROL: sahte degisken ayni boru hattindan
    for x in kesif:
        x["sahte"] = None
    g = collections.defaultdict(list)
    for i, x in enumerate(kesif):
        g[x["gun"]].append(i)
    kaynak = [x["score"] for x in kesif]
    for gun, idx in g.items():
        v = [kaynak[i] for i in idx]
        random.shuffle(v)
        for i, val in zip(idx, v):
            kesif[i]["sahte"] = val
    sahte_en = None
    for ad, fn in hucreler(kesif, sahte=True):
        o = hucre_olc(kesif, fn)
        if o and o["N"] >= MIN_N_KESIF and (sahte_en is None or o["ortR"] > sahte_en[1]["ortR"]):
            sahte_en = (ad, o)
    print("### 2) NEGATIF KONTROL — gun ici permute edilmis SAHTE degisken")
    if sahte_en:
        print("   sahtenin EN IYI hucresi: %-28s N=%d  ort R %+.4f"
              % (sahte_en[0], sahte_en[1]["N"], sahte_en[1]["ortR"]))
    else:
        print("   hesaplanamadi")
    print()

    # --- SECIM (otomatik, on-kayit bolum 6)
    adaylar = [(ad, fn, o) for ad, fn, o, u in sonuc if u]
    if not adaylar:
        print("N>=100 aday yok — arama biter")
        return
    adaylar.sort(key=lambda z: (-z[2]["ortR"], -z[2]["N"]))
    s_ad, s_fn, s_o = adaylar[0]
    print("### 3) 🔒 SECILEN ADAY (otomatik: en yuksek ort R, N>=%d)" % MIN_N_KESIF)
    print("   %s" % s_ad)
    print("   kesif: N=%d  ort R %+.4f  isabet %.1f%% (basabas %.1f%%)"
          % (s_o["N"], s_o["ortR"], s_o["isabet"], s_o["basabas"]))
    if sahte_en:
        print("   ⚠️ sahte degiskenin en iyisi %+.4f -> aday onun %.2f kati"
              % (sahte_en[1]["ortR"],
                 (s_o["ortR"] / sahte_en[1]["ortR"]) if sahte_en[1]["ortR"] else 0))
    print()

    # --- HOLDOUT (ILK KEZ ACILIYOR)
    print("=" * 100)
    print("### 4) 🔓 HOLDOUT — ilk kez aciliyor, TEK gecis")
    print("=" * 100)
    hi = hucre_olc(hold, s_fn)
    hd = hucre_olc(hold, lambda x: not s_fn(x))
    if not hi or not hd:
        print("   holdout'ta hesaplanamadi")
        return
    print("   hucre ICI   N=%4d  ort R %+.4f  isabet %.1f%%  stop %%%.2f  basabas %.1f%%"
          % (hi["N"], hi["ortR"], hi["isabet"], hi["stop_pct"], hi["basabas"]))
    print("   hucre DISI  N=%4d  ort R %+.4f  isabet %.1f%%"
          % (hd["N"], hd["ortR"], hd["isabet"]))
    fark = hi["ortR"] - hd["ortR"]
    gd = collections.defaultdict(lambda: ([], []))
    for x in hold:
        (gd[x["gun"]][0] if s_fn(x) else gd[x["gun"]][1]).append(x["R"])
    gfark = [(g, stx.mean(a) - stx.mean(b)) for g, (a, b) in gd.items()
             if len(a) >= 2 and len(b) >= 2]
    m, t, ng = gun_kumeli_t(gfark)
    tumR = [x["R"] for x in hi["ic"]]
    disR = [x["R"] for x in hd["ic"]]
    mde = 2.8 * math.sqrt(
        (stx.variance(tumR) / len(tumR) if len(tumR) > 1 else 0) +
        (stx.variance(disR) / len(disR) if len(disR) > 1 else 0))
    print()
    print("   fark (ici - disi)  %+.4f R   ·   gun-kumeli t %+.2f (%d gun)   ·   MDE %.4f"
          % (fark, t, ng, mde))
    print("   BUZULME: kesif %+.4f -> holdout %+.4f" % (s_o["ortR"], hi["ortR"]))
    print()
    H = {
        "H1 ort R > 0": hi["ortR"] > 0,
        "H2 gun-kumeli t >= 2,0": t >= 2.0,
        "H3 |fark| > MDE": abs(fark) > mde,
        "H4 isabet > basabas": hi["isabet"] > hi["basabas"],
        "H5 N >= %d" % MIN_N_HOLDOUT: hi["N"] >= MIN_N_HOLDOUT,
    }
    for k, v in H.items():
        print("   %-26s %s" % (k, "GECTI" if v else "DUSTU"))
    print()
    if all(H.values()):
        print("   🔑 KAPI BULUNDU (holdout'u gecti): %s" % s_ad)
        print("   🔴 Dogrudan bota KONMAZ — once portfoy simulasyonu (on-kayit bolum 11).")
    else:
        print("   BULUNAMADI — aday holdout'ta dustu.")
        print("   On-kayit bolum 9: ikinci aday holdout'a SOKULMAZ. Arama burada biter.")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
