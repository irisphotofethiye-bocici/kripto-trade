#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""POZISYON KOMPOZISYONUNUN TEMIZ AYRISTIRMASI — OLCUM

ON_KAYIT_komp_temiz.md · commit a89474a — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

🔴 TASARIM (on-kayit bolum 4) — bugunku iki hatanin duzeltmesi:
   (a) sembol-gun basina TEK gozlem, ortusmesiz +24s, DONEN saat
   (b) Fama-MacBeth: gun basina kesitsel rho, sonra gunler uzerinde t
   (c) etki tabani PERMUTASYONLA olculur (200 tekrar, %95 kuantil)

SALT-OKUNUR. Bot dosyalarina yazim YOK.
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
MDIR = os.path.join(KOK, "scratchpad", "komp_temiz", "metrics")
KDIR = os.path.join(KOK, "scratchpad", "klines_1h_uzun")

UFUKLAR = [4, 24, 72]
BIRINCIL = 24
G1_ESIK = 2.5              # on-kayit bolum 6
PERM = 200
BIRINCIL_DEG = ["komp_temiz", "buyukluk_egimi"]
DEGISKENLER = ["komp_temiz", "buyukluk_egimi", "count_top",
               "count_glob", "sum_top", "komp_kirli"]

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
        o = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            r[p[k]] = o
        i = j + 1
    return r


def spearman(x, y):
    if len(x) < 8:
        return None
    rx, ry = siralar(x), siralar(y)
    mx, my = stx.mean(rx), stx.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return (num / den) if den else None


def fm(gunluk):
    """Fama-MacBeth: gunluk rho'larin ortalamasi ve t'si."""
    v = [x for x in gunluk if x is not None]
    if len(v) < 10:
        return 0.0, 0.0, len(v)
    m = stx.mean(v)
    se = stx.stdev(v) / math.sqrt(len(v))
    return m, ((m / se) if se > 0 else 0.0), len(v)


# ------------------------------------------------------------------ veri
def mum_yukle(sym):
    p = os.path.join(KDIR, sym + ".json")
    if not os.path.exists(p):
        return None
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return None
    return {int(x["t"]): float(x["c"]) for x in d}


def veri_kur():
    """-> gunluk kesitler: {gun: [ {sym, deg..., ret4, ret24, ret72, last1}, ... ]}"""
    kesit = collections.defaultdict(list)
    syms = sorted(x[:-5] for x in os.listdir(MDIR) if x.endswith(".json"))
    gun_sira = {}
    eksik_mum = 0
    for sym in syms:
        mum = mum_yukle(sym)
        if not mum:
            eksik_mum += 1
            continue
        try:
            met = json.load(open(os.path.join(MDIR, sym + ".json"), encoding="utf-8"))
        except Exception:
            continue
        # gun -> {saat_ms: satir}
        gunluk = collections.defaultdict(dict)
        for row in met:
            ms = int(row[0])
            g = dt.datetime.fromtimestamp(ms / 1000, dt.UTC).date().isoformat()
            gunluk[g][ms] = row[1:]
        for g, saatler in gunluk.items():
            if g not in gun_sira:
                gun_sira[g] = len(gun_sira)
            # DONEN saat — SEYRELT faz-kilidi tuzagi (CLAUDE.md)
            hedef = gun_sira[g] % 24
            ms = None
            for k in sorted(saatler):
                if dt.datetime.fromtimestamp(k / 1000, dt.UTC).hour == hedef:
                    ms = k
                    break
            if ms is None:
                continue
            ct, sp, cg, tk, oiv = saatler[ms]
            p0 = mum.get(ms)
            if not p0 or not ct or not cg:
                continue
            r = {"sym": sym, "ms": ms,
                 "komp_temiz": ct - cg,
                 "buyukluk_egimi": sp / ct,
                 "count_top": ct, "count_glob": cg, "sum_top": sp,
                 "komp_kirli": sp - cg}
            onceki = mum.get(ms - 3_600_000)
            r["last1"] = ((p0 / onceki - 1) * 100.0) if onceki else None
            for h in UFUKLAR:
                c = mum.get(ms + h * 3_600_000)
                r["ret%d" % h] = ((c / p0 - 1.0) * 100.0) if c else None
            kesit[g].append(r)
    return kesit, len(syms), eksik_mum


# ------------------------------------------------------------------ olcum
def gunluk_rho(kesit, alan, ufuk, gunler=None):
    out = []
    for g in sorted(kesit):
        if gunler is not None and g not in gunler:
            continue
        rows = [r for r in kesit[g]
                if r.get(alan) is not None and r.get("ret%d" % ufuk) is not None]
        if len(rows) < 8:
            continue
        out.append(spearman([r[alan] for r in rows],
                            [r["ret%d" % ufuk] for r in rows]))
    return out


def perm_null(kesit, alan, ufuk, tekrar=PERM):
    """Gun ICINDE semboller arasinda permutasyon -> null |FM ortalama rho|."""
    gunler = []
    for g in sorted(kesit):
        rows = [r for r in kesit[g]
                if r.get(alan) is not None and r.get("ret%d" % ufuk) is not None]
        if len(rows) >= 8:
            gunler.append(([r[alan] for r in rows],
                           [r["ret%d" % ufuk] for r in rows]))
    if len(gunler) < 10:
        return None
    dag = []
    for _ in range(tekrar):
        rr = []
        for x, y in gunler:
            xs = x[:]
            random.shuffle(xs)
            v = spearman(xs, y)
            if v is not None:
                rr.append(v)
        if rr:
            dag.append(abs(stx.mean(rr)))
    dag.sort()
    return dag[int(0.95 * len(dag))]


def last1_sabit_rho(kesit, alan, ufuk):
    """Kesit ICINDE last1'e gore UCLU dilim; dilim rho'larinin ortalamasi."""
    out = []
    for g in sorted(kesit):
        rows = [r for r in kesit[g] if r.get(alan) is not None
                and r.get("ret%d" % ufuk) is not None and r.get("last1") is not None]
        if len(rows) < 24:
            continue
        rows.sort(key=lambda r: r["last1"])
        n = len(rows)
        vs = []
        for i in range(3):
            p = rows[i * n // 3:(i + 1) * n // 3]
            if len(p) < 8:
                continue
            v = spearman([r[alan] for r in p], [r["ret%d" % ufuk] for r in p])
            if v is not None:
                vs.append(v)
        if vs:
            out.append(stx.mean(vs))
    return out


def main():
    print("=" * 100)
    print("POZISYON KOMPOZISYONU — TEMIZ AYRISTIRMA · ON_KAYIT_komp_temiz.md (a89474a)")
    print("🔴 Gecse bile BOTA EKLENMEZ — once mekanikli ikinci olcum (on-kayit bolum 7).")
    print("=" * 100)

    kesit, ns, eksik = veri_kur()
    if not kesit:
        print("veri yok")
        return
    tg = sum(len(v) for v in kesit.values())
    print("sembol dosyasi %d (mumu eksik %d) · gun %d · sembol-gun %d"
          % (ns, eksik, len(kesit), tg))
    print("gun basina medyan sembol: %d"
          % stx.median([len(v) for v in kesit.values()]))
    g_ilk, g_son = min(kesit), max(kesit)
    print("pencere: %s .. %s" % (g_ilk, g_son))
    print()

    print("### 1) 🔴 BIRINCIL — Fama-MacBeth, +%ds (G1 esik |t| >= %.1f)"
          % (BIRINCIL, G1_ESIK))
    print("   %-18s %9s %11s %9s   %s"
          % ("degisken", "gun", "ort rho", "t", "G1"))
    fm_sonuc = {}
    for d in DEGISKENLER:
        gr = gunluk_rho(kesit, d, BIRINCIL)
        m, t, n = fm(gr)
        fm_sonuc[d] = (m, t, n)
        yildiz = " *" if d in BIRINCIL_DEG else ""
        print("   %-18s %9d %+11.5f %+9.2f   %-6s%s"
              % (d, n, m, t, "GECTI" if abs(t) >= G1_ESIK else "dustu", yildiz))
    print("   (* = birincil; digerleri KONTROL, hukum kurmaz)")
    print()

    print("### 2) PERMUTASYON NULL (G2) — gun ici sembol permutasyonu, %d tekrar" % PERM)
    print("   %-18s %13s %13s   %s" % ("degisken", "|gercek rho|", "null %95", "G2"))
    g2 = {}
    for d in DEGISKENLER:
        nl = perm_null(kesit, d, BIRINCIL)
        gercek = abs(fm_sonuc[d][0])
        ok = (nl is not None and gercek > nl)
        g2[d] = ok
        print("   %-18s %13.5f %13.5f   %s"
              % (d, gercek, nl if nl is not None else -1,
                 "GECTI" if ok else "dustu"))
    print()

    print("### 3) IKI YARI (G3)")
    gs = sorted(kesit)
    orta = gs[len(gs) // 2]
    A, B = set(gs[:len(gs) // 2]), set(gs[len(gs) // 2:])
    print("   A: %s..%s   B: %s..%s" % (gs[0], orta, orta, gs[-1]))
    print("   %-18s %11s %11s   %s" % ("degisken", "A rho", "B rho", "G3"))
    g3 = {}
    for d in DEGISKENLER:
        ma, _, _ = fm(gunluk_rho(kesit, d, BIRINCIL, A))
        mb, _, _ = fm(gunluk_rho(kesit, d, BIRINCIL, B))
        ok = (ma > 0) == (mb > 0)
        g3[d] = ok
        print("   %-18s %+11.5f %+11.5f   %s" % (d, ma, mb, "AYNI" if ok else "DONDU"))
    print()

    print("### 4) UFUK MERDIVENI (G4) — >=2 basamak ayni isaret")
    bas = "   %-18s" % "degisken"
    for h in UFUKLAR:
        bas += "%12s" % ("+%ds" % h)
    print(bas + "   G4")
    g4 = {}
    for d in DEGISKENLER:
        sat = "   %-18s" % d
        isr = []
        for h in UFUKLAR:
            m, _, _ = fm(gunluk_rho(kesit, d, h))
            sat += "%+12.5f" % m
            isr.append(1 if m > 0 else -1)
        ana = 1 if fm_sonuc[d][0] > 0 else -1
        ayni = sum(1 for s in isr if s == ana)
        g4[d] = ayni >= 2
        print(sat + "   %d/3 %s" % (ayni, "OK" if ayni >= 2 else "-"))
    print()

    print("### 5) last1 SABITLENMIS (G5) — kesit ici uclu dilim")
    print("   %-18s %11s %11s   %s" % ("degisken", "ham rho", "sabit rho", "G5"))
    g5 = {}
    for d in DEGISKENLER:
        sr = last1_sabit_rho(kesit, d, BIRINCIL)
        m, t, n = fm(sr)
        ham = fm_sonuc[d][0]
        ok = (n >= 10 and (m > 0) == (ham > 0))
        g5[d] = ok
        print("   %-18s %+11.5f %+11.5f   %s" % (d, ham, m, "KORUNDU" if ok else "DONDU"))
    print()

    print("=" * 100)
    print("HUKUM — ON_KAYIT bolum 6 (olcutler kosumdan once sabitti)")
    print("=" * 100)
    print("   %-18s %-7s %-7s %-7s %-7s %-7s   %s"
          % ("degisken", "G1", "G2", "G3", "G4", "G5", "SONUC"))
    gecen = []
    for d in DEGISKENLER:
        a = abs(fm_sonuc[d][1]) >= G1_ESIK
        b, c, e, f = g2[d], g3[d], g4[d], g5[d]
        hep = a and b and c and e and f
        if hep and d in BIRINCIL_DEG:
            gecen.append(d)
        sonuc = ("🔑 BILGI TASIYOR" if hep
                 else ("BOS" if not (a and b) else "BELIRSIZ (aday)"))
        if d not in BIRINCIL_DEG:
            sonuc += "  [kontrol]"
        print("   %-18s %-7s %-7s %-7s %-7s %-7s   %s"
              % (d, "OK" if a else "-", "OK" if b else "-", "OK" if c else "-",
                 "OK" if e else "-", "OK" if f else "-", sonuc))
    print()
    if gecen:
        print("   BIRINCIL GECEN: %s" % ", ".join(gecen))
        print("   🔴 BU BIR KAPI DEGIL. On-kayit bolum 7 baglayici:")
        print("      (1) botun kendi mekanigiyle (sabit %10 hedef · A-stop · 48s)")
        print("          IKINCI bir olcum yapilir;")
        print("      (2) ancak o da gecerse kapi onerisi + pencere sifirlama.")
    else:
        print("   HICBIR BIRINCIL DEGISKEN GECMEDI.")
        print("   -> bant-disi liste TAMAMEN kapanir (dort adayin dordu).")
    print()
    kirli = fm_sonuc.get("komp_kirli")
    temiz = fm_sonuc.get("komp_temiz")
    if kirli and temiz:
        print("   YINELEME KONTROLU — eski ELMA-ARMUT vs TEMIZ:")
        print("      komp_kirli (eski) rho %+.5f  t %+.2f" % (kirli[0], kirli[1]))
        print("      komp_temiz (yeni) rho %+.5f  t %+.2f" % (temiz[0], temiz[1]))
    print()
    print("Salt-okuma. klines_1h_uzun EZILMEDI. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
