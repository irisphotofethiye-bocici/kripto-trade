#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TAKER >= 1.0 KAPISI BILGI TASIYOR MU?

ON_KAYIT_taker_kapisi.md · commit 08c8876 — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

SALT-OKUNUR. Arsiv context'e yuklenmez. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, math, collections, statistics as stx
import datetime as dt

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARSIV = os.path.join(KOK, "radar_archive.jsonl")
KDIR = os.path.join(KOK, "scratchpad", "taker", "klines")

UFUKLAR = [1, 4, 12, 24, 48]
BIRINCIL = 24                 # on-kayit bolum 5
ESIK_TAKER = 1.0
ETKI_TABAN = 0.30             # on-kayit bolum 8 — puan
DILIM = 5                     # last1 besli dilim


# ---------------------------------------------------------------- yardimcilar
def welch(a, b):
    if len(a) < 2 or len(b) < 2:
        return 0.0, 0.0
    ma, mb = stx.mean(a), stx.mean(b)
    va, vb = stx.variance(a), stx.variance(b)
    se = math.sqrt(va / len(a) + vb / len(b))
    return (ma - mb), ((ma - mb) / se if se > 0 else 0.0)


def tek_t(v):
    """Bir dizinin ortalamasinin sifirdan farkinin t'si."""
    if len(v) < 2:
        return 0.0, 0.0
    m = stx.mean(v)
    s = stx.stdev(v)
    se = s / math.sqrt(len(v))
    return m, (m / se if se > 0 else 0.0)


def spearman(x, y):
    n = len(x)
    if n < 3:
        return 0.0
    def sira(v):
        p = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[p[j + 1]] == v[p[i]]:
                j += 1
            ort = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[p[k]] = ort
            i = j + 1
        return r
    rx, ry = sira(x), sira(y)
    mx, my = stx.mean(rx), stx.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else 0.0


def mde(a, b, guc_z=2.8):
    """Kabaca: 2.8 * SE (alfa .05 iki yonlu + guc .80)."""
    if len(a) < 2 or len(b) < 2:
        return float("inf")
    se = math.sqrt(stx.variance(a) / len(a) + stx.variance(b) / len(b))
    return guc_z * se


# ---------------------------------------------------------------- veri
def mumlar_yukle(semboller):
    out = {}
    for s in semboller:
        p = os.path.join(KDIR, str(s) + ".json")
        if not os.path.exists(p):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        out[s] = {int(x["t"]): float(x["c"]) for x in d}
    return out


def hucre_yukle():
    h = []
    with open(ARSIV, encoding="utf-8", errors="ignore") as f:
        for l in f:
            l = l.strip()
            if not l:
                continue
            try:
                r = json.loads(l)
            except Exception:
                continue
            st = r.get("stage")
            if st not in ("BASLIYOR", "HAZIRLANIYOR"):
                continue
            if (r.get("score") or 0) < (40.0 if st == "HAZIRLANIYOR" else 45.0):
                continue
            if r.get("smart") != "LONG":
                continue
            if r.get("taker") is None or not r.get("price"):
                continue
            h.append(r)
    return h


def ts_ms(ts, kayma_saat):
    """Arsiv damgasi -> UTC saat kovasi (ms). kayma_saat: yerel->UTC duzeltmesi."""
    try:
        d = dt.datetime.strptime(ts[:16], "%Y-%m-%d %H:%M")
    except Exception:
        return None
    d = d - dt.timedelta(hours=kayma_saat)
    d = d.replace(minute=0, second=0, microsecond=0)
    return int(d.replace(tzinfo=dt.UTC).timestamp() * 1000)


def hiza_dogrula(hucre, mum):
    """🔴 ZORUNLU: arsiv damgasi yerel mi UTC mi? Fiyati mumla esleyerek bul.
    Yanlis kayma tum ileri getiriyi kaydirir -> olcum sessizce coper."""
    print("### 0) ZAMAN DAMGASI HIZASI (zorunlu dogrulama)")
    en_iyi, en_iyi_k = None, None
    for k in (0, 3, -3, 1, -1, 2, -2):
        hata = []
        for r in hucre:
            m = mum.get(r["sym"])
            if not m:
                continue
            t = ts_ms(r["ts"], k)
            if t is None or t not in m:
                continue
            c = m[t]
            if c > 0:
                hata.append(abs(r["price"] / c - 1.0))
        if len(hata) < 50:
            continue
        med = stx.median(hata)
        print("   kayma %+d sa : N=%4d  medyan bagil hata %.5f" % (k, len(hata), med))
        if en_iyi is None or med < en_iyi:
            en_iyi, en_iyi_k = med, k
    print("   -> SECILEN kayma: %+d saat (medyan hata %.5f)" % (en_iyi_k, en_iyi))
    if en_iyi > 0.02:
        print("   🔴 UYARI: en iyi hizada bile medyan hata %2'nin ustunde.")
    print()
    return en_iyi_k


def getiriler(hucre, mum, kayma):
    """Her kayda ufuk getirilerini ekler. Eksik ufuk None."""
    out = []
    for r in hucre:
        m = mum.get(r["sym"])
        if not m:
            continue
        t0 = ts_ms(r["ts"], kayma)
        if t0 is None or t0 not in m:
            continue
        p0 = m[t0]
        if not p0:
            continue
        rec = dict(r)
        rec["_gun"] = r["ts"][:10]
        for h in UFUKLAR:
            t1 = t0 + h * 3_600_000
            c = m.get(t1)
            rec["ret%d" % h] = ((c / p0 - 1.0) * 100.0) if c else None
        out.append(rec)
    return out


# ---------------------------------------------------------------- olcum
def kol_ayir(rows, alan, esik, ufuk):
    a = [r["ret%d" % ufuk] for r in rows
         if r.get(alan) is not None and r[alan] >= esik and r.get("ret%d" % ufuk) is not None]
    b = [r["ret%d" % ufuk] for r in rows
         if r.get(alan) is not None and r[alan] < esik and r.get("ret%d" % ufuk) is not None]
    return a, b


def dilim_ici_fark(rows, alan, esik, ufuk, sabit):
    """SABITLENMIS fark: `sabit` alaninin besli dilimi ICINDE bolme,
    dilim farklarinin N-agirlikli ortalamasi."""
    kul = [r for r in rows
           if r.get(alan) is not None and r.get(sabit) is not None
           and r.get("ret%d" % ufuk) is not None]
    if len(kul) < DILIM * 4:
        return None, 0, []
    kul.sort(key=lambda r: r[sabit])
    n = len(kul)
    parca = [kul[i * n // DILIM:(i + 1) * n // DILIM] for i in range(DILIM)]
    toplam_w = 0.0
    toplam = 0.0
    detay = []
    for i, p in enumerate(parca):
        a = [r["ret%d" % ufuk] for r in p if r[alan] >= esik]
        b = [r["ret%d" % ufuk] for r in p if r[alan] < esik]
        if len(a) < 3 or len(b) < 3:
            detay.append((i + 1, len(a), len(b), None))
            continue
        f = stx.mean(a) - stx.mean(b)
        w = min(len(a), len(b))
        toplam += f * w
        toplam_w += w
        detay.append((i + 1, len(a), len(b), f))
    if toplam_w == 0:
        return None, 0, detay
    return toplam / toplam_w, int(toplam_w), detay


def gun_kumeli(rows, alan, esik, ufuk):
    """Gunluk kol farklarinin t'si."""
    g = collections.defaultdict(lambda: ([], []))
    for r in rows:
        v = r.get("ret%d" % ufuk)
        if v is None or r.get(alan) is None:
            continue
        (g[r["_gun"]][0] if r[alan] >= esik else g[r["_gun"]][1]).append(v)
    farklar = []
    for gun, (a, b) in g.items():
        if len(a) >= 2 and len(b) >= 2:
            farklar.append(stx.mean(a) - stx.mean(b))
    return farklar


def main():
    print("=" * 92)
    print("TAKER >= 1.0 KAPISI — ON_KAYIT_taker_kapisi.md (commit 08c8876)")
    print("=" * 92)
    print()

    hucre = hucre_yukle()
    semboller = sorted(set(r["sym"] for r in hucre))
    mum = mumlar_yukle(semboller)
    print("hucre N=%d · sembol %d · mum dosyasi %d" % (len(hucre), len(semboller), len(mum)))
    print()

    kayma = hiza_dogrula(hucre, mum)
    rows = getiriler(hucre, mum, kayma)
    print("### 1) KAPSAM")
    print("   ileri getirisi hesaplanabilen kayit : %d / %d" % (len(rows), len(hucre)))
    for h in UFUKLAR:
        k = sum(1 for r in rows if r.get("ret%d" % h) is not None)
        print("      +%2ds : %d" % (h, k))
    gunler = sorted(set(r["_gun"] for r in rows))
    print("   tekil gun: %d  (%s .. %s)" % (len(gunler), gunler[0], gunler[-1]))
    print()

    # ---- oynaklik ayrismasi (on-kayit bolum 6)
    print("### 2) OYNAKLIK AYRISMASI (zorunlu sinama)")
    ust = [r for r in rows if r["taker"] >= ESIK_TAKER]
    alt = [r for r in rows if r["taker"] < ESIK_TAKER]
    print("   %-14s %6s %10s %10s %12s" % ("kol", "N", "vol_x med", "|last1| med", "ret24 sapma"))
    for ad, kol in (("taker>=1.0", ust), ("taker<1.0", alt)):
        vx = [r["vol_x"] for r in kol if r.get("vol_x") is not None]
        l1 = [abs(r["last1"]) for r in kol if r.get("last1") is not None]
        rr = [r["ret24"] for r in kol if r.get("ret24") is not None]
        print("   %-14s %6d %10.2f %10.2f %12.2f"
              % (ad, len(kol), stx.median(vx) if vx else 0,
                 stx.median(l1) if l1 else 0,
                 stx.stdev(rr) if len(rr) > 1 else 0))
    print()

    # ---- ufuk merdiveni (HAM)
    print("### 3) UFUK MERDIVENI — HAM fark (mekaniksiz)")
    print("   %-8s %7s %7s %11s %11s %10s %9s %9s"
          % ("ufuk", "N>=1", "N<1", "ort >=1.0", "ort <1.0", "FARK", "Welch t", "MDE"))
    isaretler = []
    ham = {}
    for h in UFUKLAR:
        a, b = kol_ayir(rows, "taker", ESIK_TAKER, h)
        f, t = welch(a, b)
        m = mde(a, b)
        ham[h] = (f, t, m, len(a), len(b))
        isaretler.append(1 if f > 0 else (-1 if f < 0 else 0))
        print("   +%-7d %7d %7d %+10.3f%% %+10.3f%% %+9.3f %9.2f %9.3f"
              % (h, len(a), len(b),
                 stx.mean(a) if a else 0, stx.mean(b) if b else 0, f, t, m))
    print()

    # ---- SABITLENMIS fark (on-kayit bolum 7 — K2)
    print("### 4) 🔴 KARISTIRICI KONTROLU — last1 SABITLENMIS (K2'nin kaynagi)")
    f2, w2, detay = dilim_ici_fark(rows, "taker", ESIK_TAKER, BIRINCIL, "last1")
    print("   birincil ufuk +%ds · sabitlenen: last1 (besli dilim)" % BIRINCIL)
    print("   %-8s %7s %7s %12s" % ("dilim", "N>=1", "N<1", "fark"))
    for i, na, nb, ff in detay:
        print("   %-8d %7d %7d %12s"
              % (i, na, nb, ("%+.3f" % ff) if ff is not None else "-"))
    print("   -> SABITLENMIS FARK: %s  (agirlik %d)"
          % (("%+.3f puan" % f2) if f2 is not None else "hesaplanamadi", w2))
    print("      HAM fark ayni ufukta: %+.3f puan" % ham[BIRINCIL][0])
    print()

    print("   ikincil sabitleyiciler (hukum kurmaz):")
    for sab in ("last3", "pos", "vol_x"):
        fx, wx, _ = dilim_ici_fark(rows, "taker", ESIK_TAKER, BIRINCIL, sab)
        print("      %-8s -> %s (agirlik %d)"
              % (sab, ("%+.3f puan" % fx) if fx is not None else "hesaplanamadi", wx))
    alt24 = [r for r in rows if r.get("chg24") is not None]
    if len(alt24) >= DILIM * 4:
        fx, wx, _ = dilim_ici_fark(alt24, "taker", ESIK_TAKER, BIRINCIL, "chg24")
        print("      %-8s -> %s (agirlik %d, alt kume N=%d)"
              % ("chg24", ("%+.3f puan" % fx) if fx is not None else "-", wx, len(alt24)))
    print()

    # ---- gun kumeli (K3)
    farklar = gun_kumeli(rows, "taker", ESIK_TAKER, BIRINCIL)
    m3, t3 = tek_t(farklar)
    print("### 5) GUN-KUMELI (K3)")
    print("   iki kolu da olan gun: %d · gunluk fark ortalamasi %+.3f · t = %+.2f"
          % (len(farklar), m3, t3))
    print()

    # ---- yogunlasma (K5)
    print("### 6) YOGUNLASMA (K5) — en iyi 2 gun cikarilinca")
    gun_kat = collections.defaultdict(list)
    for r in rows:
        if r.get("ret%d" % BIRINCIL) is not None:
            gun_kat[r["_gun"]].append(r)
    gun_fark = {}
    for gun, rr in gun_kat.items():
        a = [x["ret%d" % BIRINCIL] for x in rr if x["taker"] >= ESIK_TAKER]
        b = [x["ret%d" % BIRINCIL] for x in rr if x["taker"] < ESIK_TAKER]
        if len(a) >= 2 and len(b) >= 2:
            gun_fark[gun] = stx.mean(a) - stx.mean(b)
    kotu = sorted(gun_fark, key=lambda g: -gun_fark[g])[:2]
    kalan = [r for r in rows if r["_gun"] not in kotu]
    a5, b5 = kol_ayir(kalan, "taker", ESIK_TAKER, BIRINCIL)
    f5, t5 = welch(a5, b5)
    print("   cikarilan gunler: %s" % ", ".join("%s(%+.2f)" % (g, gun_fark[g]) for g in kotu))
    print("   kalan fark: %+.3f puan (t %+.2f, N %d/%d)" % (f5, t5, len(a5), len(b5)))
    print()

    # ---- sureklilik
    xs = [r["taker"] for r in rows if r.get("ret%d" % BIRINCIL) is not None]
    ys = [r["ret%d" % BIRINCIL] for r in rows if r.get("ret%d" % BIRINCIL) is not None]
    rho = spearman(xs, ys)
    print("### 7) SUREKLI (ikincil): Spearman rho(taker, ret%d) = %+.4f  N=%d"
          % (BIRINCIL, rho, len(xs)))
    print()

    # ---- negatif kontrol (on-kayit bolum 10)
    print("### 8) NEGATIF KONTROL — glob_ls ayni esikle")
    an, bn = kol_ayir(rows, "glob_ls", 1.0, BIRINCIL)
    fn, tn = welch(an, bn)
    fn2, wn2, _ = dilim_ici_fark(rows, "glob_ls", 1.0, BIRINCIL, "last1")
    print("   ham fark %+.3f puan (t %+.2f, N %d/%d)" % (fn, tn, len(an), len(bn)))
    print("   SABITLENMIS fark %s (agirlik %d)"
          % (("%+.3f puan" % fn2) if fn2 is not None else "-", wn2))
    if fn2 is not None and fn2 >= ETKI_TABAN:
        print("   🔴 NEGATIF KONTROL K2'YI GECTI -> duzenek supheli, hukum YAZILMAZ")
    else:
        print("   -> negatif kontrol K2'yi gecmedi (duzenek saglam)")
    print()

    # ---- HUKUM
    print("=" * 92)
    print("HUKUM — ON_KAYIT bolum 9 (olcutler kosumdan once sabitti)")
    print("=" * 92)
    k1 = ham[BIRINCIL][0] > 0
    k2 = (f2 is not None and f2 >= ETKI_TABAN)
    k3 = t3 >= 2.0
    ayni = sum(1 for s in isaretler if s > 0)
    k4 = ayni >= 3
    k5 = f5 > 0
    neg_ok = not (fn2 is not None and fn2 >= ETKI_TABAN)
    for ad, v, aciklama in (
            ("K1", k1, "ham fark > 0 (+%ds): %+.3f puan" % (BIRINCIL, ham[BIRINCIL][0])),
            ("K2", k2, "SABITLENMIS fark >= +%.2f: %s"
             % (ETKI_TABAN, ("%+.3f" % f2) if f2 is not None else "-")),
            ("K3", k3, "gun-kumeli t >= 2,0: %+.2f" % t3),
            ("K4", k4, "merdivende >=3 basamak ayni isaret: %d/5" % ayni),
            ("K5", k5, "en iyi 2 gun cikinca hala K1: %+.3f" % f5)):
        print("   %-4s %-8s %s" % (ad, "GECTI" if v else "DUSTU", aciklama))
    print()
    if not neg_ok:
        print("SONUC: HUKUM YAZILMAZ — negatif kontrol duzenegi curuttu.")
    elif not k2:
        print("SONUC: 🔴 KAPI BOS — K2 dustu. taker kapisi kaldirilabilir.")
    elif k1 and k2 and k3 and k4 and k5:
        print("SONUC: KAPI BILGI TASIYOR — kapi KALIR.")
    else:
        print("SONUC: BELIRSIZ — K1+K2 gecti ama biri dustu -> kapi KALIR (statuko).")
    print()
    print("MDE (+%ds) = %.3f puan · |fark| < MDE ise 'goremiyoruz', 'etki yok' DEGIL"
          % (BIRINCIL, ham[BIRINCIL][2]))
    print("Salt-okuma. Arsiv context'e yuklenmedi. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
