#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FONLAMA ve LONG/SHORT BIRIKMESI YON TASIYOR MU?

ON_KAYIT_funding_ls_birikme.md · commit 19bbb73 — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

🔴 BU BIR TARAMADIR, KAPI KARARI DEGILDIR (on-kayit bolum 6).
SALT-OKUNUR. Arsiv context'e yuklenmez. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, math, random, collections, statistics as stx
import datetime as dt

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARSIV = os.path.join(KOK, "radar_archive.jsonl")
KDIR = os.path.join(KOK, "scratchpad", "fund_ls", "klines")

UFUKLAR = [1, 4, 12, 24, 48]
BIRINCIL = 24
TABAN = 0.020            # on-kayit bolum 6 · G1
DILIM = 5
KAYMA = 3                # radar_archive.ts YEREL (UTC+3) — 02_olcum.py'de dogrulandi
HIZA_UST_SINIR = 0.010   # medyan bagil hata bunun ustundeyse BETIK REDDEDER

DEGISKENLER = ["funding", "oi24", "oi3", "top_ls", "glob_ls", "komp"]
NEG_KONTROL = ["vol_x", "funding_karisik"]

random.seed(20260906)


# ------------------------------------------------------------------ istatistik
def siralar(v):
    n = len(v)
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


def spearman(x, y):
    if len(x) < 10:
        return 0.0
    rx, ry = siralar(x), siralar(y)
    mx, my = stx.mean(rx), stx.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return (num / den) if den else 0.0


def rho_mde(n):
    return 2.8 / math.sqrt(max(4, n - 3))


def rho_sabitlenmis(cift, sab):
    """`sab` degerinin BESLI dilimi ICINDE rho; dilimlerin N-agirlikli ortalamasi.
    cift: [(x, y, sabit), ...]"""
    if len(cift) < DILIM * 20:
        return None, 0
    c = sorted(cift, key=lambda t: t[2])
    n = len(c)
    top_w = 0.0
    top = 0.0
    for i in range(DILIM):
        p = c[i * n // DILIM:(i + 1) * n // DILIM]
        if len(p) < 20:
            continue
        r = spearman([t[0] for t in p], [t[1] for t in p])
        top += r * len(p)
        top_w += len(p)
    return ((top / top_w) if top_w else None), int(top_w)


def gun_kumeli_t(rows, alan, ufuk):
    """Degiskenin MEDYANINDAN bolme; gunluk kol farklarinin t'si."""
    v = [r[alan] for r in rows if r.get(alan) is not None
         and r.get("ret%d" % ufuk) is not None]
    if len(v) < 50:
        return 0.0, 0
    med = stx.median(v)
    g = collections.defaultdict(lambda: ([], []))
    for r in rows:
        y = r.get("ret%d" % ufuk)
        x = r.get(alan)
        if y is None or x is None:
            continue
        (g[r["_gun"]][0] if x >= med else g[r["_gun"]][1]).append(y)
    fark = [stx.mean(a) - stx.mean(b) for a, b in g.values()
            if len(a) >= 2 and len(b) >= 2]
    if len(fark) < 3:
        return 0.0, len(fark)
    m, s = stx.mean(fark), stx.stdev(fark)
    se = s / math.sqrt(len(fark))
    return ((m / se) if se > 0 else 0.0), len(fark)


# ------------------------------------------------------------------ veri
def mumlar_yukle():
    out = {}
    if not os.path.isdir(KDIR):
        return out
    for f in os.listdir(KDIR):
        if not f.endswith(".json"):
            continue
        try:
            d = json.load(open(os.path.join(KDIR, f), encoding="utf-8"))
        except Exception:
            continue
        out[f[:-5]] = {int(x["t"]): float(x["c"]) for x in d}
    return out


def ts_ms(ts):
    try:
        d = dt.datetime.strptime(ts[:16], "%Y-%m-%d %H:%M")
    except Exception:
        return None
    d = (d - dt.timedelta(hours=KAYMA)).replace(minute=0, second=0, microsecond=0)
    return int(d.replace(tzinfo=dt.UTC).timestamp() * 1000)


def arsiv_yukle(mum):
    """Akarak okur; context'e yuklemez. Ileri getirisi olan kayitlari dondurur."""
    rows = []
    hiza = []
    with open(ARSIV, encoding="utf-8", errors="ignore") as f:
        for l in f:
            l = l.strip()
            if not l:
                continue
            try:
                r = json.loads(l)
            except Exception:
                continue
            s, p0, ts = r.get("sym"), r.get("price"), r.get("ts")
            if not s or not p0 or not ts:
                continue
            m = mum.get(s)
            if not m:
                continue
            t0 = ts_ms(ts)
            if t0 is None or t0 not in m:
                continue
            c0 = m[t0]
            if not c0:
                continue
            hiza.append(abs(p0 / c0 - 1.0))
            rec = {"sym": s, "ts": ts, "_gun": ts[:10],
                   "stage": r.get("stage"), "score": r.get("score") or 0,
                   "smart": r.get("smart"), "last1": r.get("last1"),
                   "funding": r.get("funding"), "oi24": r.get("oi24"),
                   "oi3": r.get("oi3"), "top_ls": r.get("top_ls"),
                   "glob_ls": r.get("glob_ls"), "vol_x": r.get("vol_x")}
            tl, gl = rec["top_ls"], rec["glob_ls"]
            rec["komp"] = (tl - gl) if (tl is not None and gl is not None) else None
            for h in UFUKLAR:
                c = m.get(t0 + h * 3_600_000)
                rec["ret%d" % h] = ((c / p0 - 1.0) * 100.0) if c else None
            rows.append(rec)
    return rows, hiza


def karisik_ekle(rows):
    """Negatif kontrol 2: funding GUN ICINDE rastgele permute edilir."""
    g = collections.defaultdict(list)
    for i, r in enumerate(rows):
        if r.get("funding") is not None:
            g[r["_gun"]].append(i)
    for gun, idx in g.items():
        v = [rows[i]["funding"] for i in idx]
        random.shuffle(v)
        for i, x in zip(idx, v):
            rows[i]["funding_karisik"] = x


# ------------------------------------------------------------------ raporlama
def pop_ayir(rows):
    p2 = [r for r in rows
          if r["stage"] in ("BASLIYOR", "HAZIRLANIYOR")
          and r["score"] >= (40.0 if r["stage"] == "HAZIRLANIYOR" else 45.0)]
    p3 = [r for r in p2 if r["smart"] == "LONG"]
    return [("P1 TAM", rows), ("P2 GENIS", p2), ("P3 DAR", p3)]


def cift_al(rows, alan, ufuk, sab=None):
    out = []
    for r in rows:
        x, y = r.get(alan), r.get("ret%d" % ufuk)
        if x is None or y is None:
            continue
        if sab is not None:
            s = r.get(sab)
            if s is None:
                continue
            out.append((x, y, s))
        else:
            out.append((x, y))
    return out


def main():
    print("=" * 100)
    print("FONLAMA + LONG/SHORT BIRIKMESI — ON_KAYIT_funding_ls_birikme.md (19bbb73)")
    print("🔴 TARAMA. Gecen degisken bile BOTA EKLENMEZ; ayri on-kayitla mekanikli olculur.")
    print("=" * 100)

    mum = mumlar_yukle()
    print("mum dosyasi: %d sembol" % len(mum))
    rows, hiza = arsiv_yukle(mum)
    print("ileri getirisi hesaplanabilen kayit: %d" % len(rows))
    if not rows:
        print("veri yok")
        return

    med = stx.median(hiza)
    print()
    print("### 0) ZAMAN DAMGASI HIZASI (kayma %+d sa, on-kayit bolum 4)" % KAYMA)
    print("   medyan bagil hata: %.5f   (ust sinir %.3f)" % (med, HIZA_UST_SINIR))
    if med > HIZA_UST_SINIR:
        print("   🔴 HIZA DUSTU — betik CALISMAYI REDDEDIYOR (on-kayit bolum 4).")
        return
    print("   -> hiza dogrulandi")

    karisik_ekle(rows)
    poplar = pop_ayir(rows)
    print()
    print("### 1) POPULASYONLAR ve GUC")
    print("   %-10s %9s %7s %14s" % ("pop", "N", "gun", "gorulebilir rho"))
    for ad, p in poplar:
        g = len(set(r["_gun"] for r in p))
        print("   %-10s %9d %7d %14.4f" % (ad, len(p), g, rho_mde(len(p))))
    print()

    # ---------------- BIRINCIL: P1 · +24s · last1 sabitlenmis
    print("### 2) 🔴 BIRINCIL SONUC — P1 · +%ds · last1 SABITLENMIS (G1)" % BIRINCIL)
    print("   %-16s %9s %10s %10s %10s   %s"
          % ("degisken", "N", "ham rho", "SABIT rho", "MDE", "G1 (>=%.3f)" % TABAN))
    p1 = poplar[0][1]
    g1 = {}
    for d in DEGISKENLER + NEG_KONTROL:
        c3 = cift_al(p1, d, BIRINCIL, "last1")
        if len(c3) < DILIM * 20:
            print("   %-16s  yetersiz (N=%d)" % (d, len(c3)))
            continue
        ham = spearman([t[0] for t in c3], [t[1] for t in c3])
        sab, w = rho_sabitlenmis(c3, "last1")
        m = rho_mde(len(c3))
        gecti = (sab is not None and abs(sab) >= TABAN)
        g1[d] = (sab, ham, len(c3), m, gecti)
        et = "NEG-KONTROL" if d in NEG_KONTROL else ""
        print("   %-16s %9d %+10.4f %+10.4f %10.4f   %-6s %s"
              % (d, len(c3), ham, (sab if sab is not None else 0.0), m,
                 "GECTI" if gecti else "dustu", et))
    print()

    # ---------------- G2: iki yari
    print("### 3) KARARLILIK — iki zaman yarisi (G2)")
    ts = sorted(set(r["ts"] for r in p1))
    orta = ts[len(ts) // 2]
    A = [r for r in p1 if r["ts"] < orta]
    B = [r for r in p1 if r["ts"] >= orta]
    print("   A: %s .. %s (N=%d)  ·  B: %s .. %s (N=%d)"
          % (ts[0][:10], orta[:10], len(A), orta[:10], ts[-1][:10], len(B)))
    print("   %-16s %11s %11s   %s" % ("degisken", "A (sabit)", "B (sabit)", "G2"))
    g2 = {}
    for d in DEGISKENLER + NEG_KONTROL:
        ra, _ = rho_sabitlenmis(cift_al(A, d, BIRINCIL, "last1"), "last1")
        rb, _ = rho_sabitlenmis(cift_al(B, d, BIRINCIL, "last1"), "last1")
        if ra is None or rb is None:
            print("   %-16s  yetersiz" % d)
            continue
        ok = (ra > 0) == (rb > 0)
        g2[d] = ok
        print("   %-16s %+11.4f %+11.4f   %s" % (d, ra, rb, "AYNI" if ok else "DONDU"))
    print()

    # ---------------- G3: ufuk merdiveni
    print("### 4) UFUK MERDIVENI — P1, last1 sabitlenmis (G3)")
    bas = "   %-16s" % "degisken"
    for h in UFUKLAR:
        bas += "%10s" % ("+%ds" % h)
    print(bas + "   G3")
    g3 = {}
    for d in DEGISKENLER + NEG_KONTROL:
        sat = "   %-16s" % d
        isaret = []
        for h in UFUKLAR:
            r, _ = rho_sabitlenmis(cift_al(p1, d, h, "last1"), "last1")
            sat += ("%+10.4f" % r) if r is not None else "%10s" % "-"
            if r is not None:
                isaret.append(1 if r > 0 else -1)
        ana = g1.get(d, (0,))[0] or 0
        ayni = sum(1 for s in isaret if (s > 0) == (ana > 0))
        g3[d] = ayni >= 3
        print(sat + "   %d/5 %s" % (ayni, "OK" if ayni >= 3 else "-"))
    print()

    # ---------------- G4: gun kumeli
    print("### 5) GUN-KUMELI t — medyan bolme, P1, +%ds (G4)" % BIRINCIL)
    g4 = {}
    print("   %-16s %10s %8s   %s" % ("degisken", "t", "gun", "G4 (|t|>=2,0)"))
    for d in DEGISKENLER + NEG_KONTROL:
        t, ng = gun_kumeli_t(p1, d, BIRINCIL)
        g4[d] = abs(t) >= 2.0
        print("   %-16s %+10.2f %8d   %s" % (d, t, ng, "GECTI" if abs(t) >= 2.0 else "dustu"))
    print()

    # ---------------- karar-ilgili populasyonlar
    print("### 6) P2/P3 — karar ilgisi (hukum KURMAZ, MDE ustunde degilse 'goremiyoruz')")
    for ad, p in poplar[1:]:
        print("   --- %s (N=%d · MDE %.4f) ---" % (ad, len(p), rho_mde(len(p))))
        for d in DEGISKENLER:
            c3 = cift_al(p, d, BIRINCIL, "last1")
            if len(c3) < DILIM * 20:
                print("      %-16s yetersiz (N=%d)" % (d, len(c3)))
                continue
            sab, _ = rho_sabitlenmis(c3, "last1")
            m = rho_mde(len(c3))
            durum = ("GORULUR" if (sab is not None and abs(sab) >= m) else "goremiyoruz")
            print("      %-16s N=%5d  sabit rho %+8.4f  MDE %.4f  -> %s"
                  % (d, len(c3), sab if sab is not None else 0.0, m, durum))
    print()

    # ---------------- HUKUM
    print("=" * 100)
    print("HUKUM — ON_KAYIT bolum 6 (olcutler kosumdan once sabitti)")
    print("=" * 100)
    neg_bozuk = [d for d in NEG_KONTROL if g1.get(d, (None,))[0] is not None
                 and abs(g1[d][0]) >= TABAN]
    print("   NEGATIF KONTROLLER (cift yonlu, |rho| >= %.3f duser):" % TABAN)
    for d in NEG_KONTROL:
        v = g1.get(d)
        if v:
            print("      %-16s sabit rho %+8.4f -> %s"
                  % (d, v[0] or 0.0, "🔴 GECTI (kotu)" if abs(v[0] or 0) >= TABAN else "temiz"))
    if neg_bozuk:
        print()
        print("   🔴 G5 DUSTU — negatif kontrol(ler) esigi gecti: %s" % ", ".join(neg_bozuk))
        print("   HUKUM YAZILMAZ.")
        return
    print("   -> G5 gecti (duzenek saglam)")
    print()
    print("   %-16s %-8s %-8s %-8s %-8s   %s"
          % ("degisken", "G1", "G2", "G3", "G4", "SONUC"))
    gecen = []
    for d in DEGISKENLER:
        v = g1.get(d)
        if not v:
            continue
        a, b, c, e = v[4], g2.get(d, False), g3.get(d, False), g4.get(d, False)
        hep = a and b and c and e
        if hep:
            gecen.append(d)
        print("   %-16s %-8s %-8s %-8s %-8s   %s"
              % (d, "GECTI" if a else "dustu", "GECTI" if b else "dustu",
                 "GECTI" if c else "dustu", "GECTI" if e else "dustu",
                 "🔑 BILGI TASIYOR" if hep else ("BOS" if not a else "BELIRSIZ")))
    print()
    if gecen:
        print("   BILGI TASIYAN: %s" % ", ".join(gecen))
        print("   🔴 Bu bir KAPI DEGIL. Her biri AYRI on-kayitla, MEKANIKLE ve")
        print("      kontrol grubuyla yeniden olculmeden bota EKLENMEZ.")
        print("   ⚠️ funding/oi24 gectiyse: ikisi de A+B kapisinin bacagi ->")
        print("      hukum 'bilinen kenar iki yonlu', 'yeni sinyal' DEGIL.")
    else:
        print("   HICBIRI GECMEDI. P1'de MDE %.4f < taban %.3f oldugu icin bu"
              % (rho_mde(len(p1)), TABAN))
        print("   sonuc 'goremiyoruz' DEGIL, gercekten 'esigi asan etki YOK'tur.")
    print()
    print("Salt-okuma. Arsiv context'e yuklenmedi. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
