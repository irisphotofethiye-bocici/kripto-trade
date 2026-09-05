#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OBI — OLCUM (2026-09-05)

ON-KAYIT: ON_KAYIT_obi.md, commit 0db685f — KOSUMDAN ONCE yazildi.
Olcutler burada YENIDEN YAZILMAZ, on-kayittan AYNEN alinir:

   BIRINCIL HUCRE: OBI ±%1 · ufuk +1 saat
   P1 🔴 |rho| >= 0,020 VE |t| >= 3,0     (IKI TARAFLI; isaret AYRICA raporlanir)
   P2    dort zaman ceyregi   >= 3/4 ayni isaret
   P3    rejim                >= 2/3 ayni isaret
   P4    eleme |spearman(OBI, onceki 1s getiri)| < 0,50
   P5    onceki getiri uctebirlikleri >= 2/3 ayni isaret
   GECTI = besi birden.

   IKINCIL (onceden ilan, GECTI'ye SAYILMAZ):
     ufuk merdiveni +5dk · +30dk · +4s · +24s     <- "yok" ile "bizim ufkumuzda yok"u AYIRIR
     seviye ±%2 · ±%5

Salt-okunur.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, math, statistics as stx, collections

BURASI = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.join(BURASI, "panel.jsonl")

MIN_SEMBOL_GUN = 40       # on-kayit G-d
MIN_GUN = 120             # on-kayit G-c
RHO_TABAN = 0.020         # on-kayit P1 — basis/capraz borsadan AYNEN
T_TABAN = 3.0
ELEME_TAVAN = 0.50        # on-kayit P4

UFUKLAR = (("r5", "+5 dk"), ("r30", "+30 dk"), ("r60", "+1 saat"),
           ("r240", "+4 saat"), ("r1440", "+24 saat"))


def spearman(xs, ys):
    n = len(xs)
    if n < 8:
        return None

    def sirala(v):
        idx = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(idx):
            j = i
            while j + 1 < len(idx) and v[idx[j + 1]] == v[idx[i]]:
                j += 1
            ort = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[idx[k]] = ort
            i = j + 1
        return r
    rx, ry = sirala(xs), sirala(ys)
    mx, my = stx.mean(rx), stx.mean(ry)
    pay = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    px = math.sqrt(sum((a - mx) ** 2 for a in rx))
    py = math.sqrt(sum((b - my) ** 2 for b in ry))
    return pay / (px * py) if px and py else None


def gun_rho(sat, x_alan="obi1", y_alan="r60"):
    """Gun ICINDE kesitsel rho (sembol ortalamalari uzerinden), sonra gun-kumeli t."""
    g = collections.defaultdict(list)
    for r in sat:
        if r.get(x_alan) is None or r.get(y_alan) is None:
            continue
        g[r["gun"]].append(r)
    rhos = []
    for gun, v in g.items():
        s = collections.defaultdict(lambda: [[], []])
        for r in v:
            s[r["sym"]][0].append(r[x_alan])
            s[r["sym"]][1].append(r[y_alan])
        if len(s) < MIN_SEMBOL_GUN:
            continue
        xs = [stx.mean(a) for a, _ in s.values()]
        ys = [stx.mean(b) for _, b in s.values()]
        r_ = spearman(xs, ys)
        if r_ is not None:
            rhos.append(r_)
    if len(rhos) < 3:
        return None, None, len(rhos)
    m = stx.mean(rhos)
    se = stx.stdev(rhos) / math.sqrt(len(rhos))
    return m, (m / se if se else None), len(rhos)


def yaz(ad, m, t, n, ek=""):
    print("   %-26s rho %s   t %s   gun %4d %s"
          % (ad, ("%+.4f" % m) if m is not None else "  yok ",
             ("%+.2f" % t) if t is not None else " yok ", n, ek))


def main():
    print("=" * 96)
    print("EMIR DEFTERI DENGESIZLIGI (OBI)")
    print("=" * 96)
    print("ON-KAYIT: ON_KAYIT_obi.md commit 0db685f — KOSUMDAN ONCE")
    print("Hipotez: alis tarafi kalin -> sonraki getiri yuksek  ->  rho > 0")
    print("BIRINCIL HUCRE: OBI ±%1 · ufuk +1 saat")
    print()

    sat = []
    with open(PANEL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                sat.append(json.loads(line))
    sym = collections.Counter(r["sym"] for r in sat)
    gunler = sorted(set(r["gun"] for r in sat))
    print("N gozlem = %d  ·  sembol = %d  ·  gun = %d  (%s .. %s)"
          % (len(sat), len(sym), len(gunler), gunler[0], gunler[-1]))
    print()

    # -------- GECERLILIK KAPISI --------
    print("### GECERLILIK KAPISI (on-kayit bolum 6)")
    m0, t0, n0 = gun_rho(sat)
    gs = collections.defaultdict(set)
    for r in sat:
        gs[r["gun"]].add(r["sym"])
    ort_sym = stx.median([len(v) for v in gs.values()]) if gs else 0
    kapi = [
        ("G-a OBI cikarim sinamasi", "01_indir.py'de gecti", True),
        ("G-b sembol basina >=500 saat", "en az %d" % min(sym.values()), min(sym.values()) >= 500),
        ("G-c gun kumesi >= %d" % MIN_GUN, "%d gun" % n0, n0 >= MIN_GUN),
        ("G-d gun basina >=%d sembol" % MIN_SEMBOL_GUN, "medyan %d" % ort_sym, ort_sym >= MIN_SEMBOL_GUN),
    ]
    for ad, detay, ok in kapi:
        print("   %-34s %-22s %s" % (ad, detay, "✅" if ok else "🔴 DUSTU"))
    if not all(ok for _, _, ok in kapi):
        print()
        print("🔴 GECERLILIK KAPISI DUSTU -> OLCUM DURDU. Olcut gevsetilmez.")
        return
    print()

    # -------- AYNA SAGLAMASI --------
    print("### SAGLAMA — -OBI rho'yu tam aynalamali")
    ters = [dict(r, obi1=(-r["obi1"] if r.get("obi1") is not None else None)) for r in sat]
    mt, _, _ = gun_rho(ters)
    ok_ayna = (m0 is not None and mt is not None and abs(m0 + mt) < 1e-9)
    print("   duz %+.4f  ·  ters %+.4f  ->  %s"
          % (m0, mt, "✅ aynaliyor" if ok_ayna else "🔴 BETIK HATALI"))
    if not ok_ayna:
        return
    print()

    # -------- P1 --------
    print("### P1 🔴 BIRINCIL — OBI ±%1 · +1 saat")
    yaz("TUM PENCERE", m0, t0, n0)
    P1 = (m0 is not None and t0 is not None
          and abs(m0) >= RHO_TABAN and abs(t0) >= T_TABAN)
    print("   esik: |rho| >= %.3f VE |t| >= %.1f   (IKI TARAFLI)" % (RHO_TABAN, T_TABAN))
    print("   olculen isaret: %s  (hipotez: POZITIF)"
          % ("POZITIF" if (m0 or 0) > 0 else "NEGATIF"))
    print("   -> P1 %s" % ("GECTI" if P1 else "DUSTU"))
    if m0 is not None and abs(m0) < RHO_TABAN and t0 is not None and abs(t0) >= T_TABAN:
        print("   📌 basis/capraz borsa ile AYNI DESEN: t buyuk, etki kucuk.")
    print()

    hedef = 1 if (m0 or 0) > 0 else -1

    # -------- P2 --------
    print("### P2 — dort zaman ceyregi")
    q = len(gunler) // 4
    dilim = [gunler[:q], gunler[q:2 * q], gunler[2 * q:3 * q], gunler[3 * q:]]
    isr = []
    for i, d in enumerate(dilim, 1):
        ds = set(d)
        mm, tt, nn = gun_rho([r for r in sat if r["gun"] in ds])
        isr.append(0 if mm is None else (1 if mm > 0 else -1))
        yaz("C%d  %s..%s" % (i, d[0], d[-1]), mm, tt, nn)
    a2 = sum(1 for x in isr if x == hedef)
    P2 = a2 >= 3
    print("   -> %d/4 ayni isaret  ->  P2 %s" % (a2, "GECTI" if P2 else "DUSTU"))
    print()

    # -------- P3 --------
    print("### P3 — rejim")
    isr3 = []
    for rj in ("BOGA", "NOTR", "AYI"):
        mm, tt, nn = gun_rho([r for r in sat if r["rejim"] == rj])
        isr3.append(0 if mm is None else (1 if mm > 0 else -1))
        yaz(rj, mm, tt, nn)
    a3 = sum(1 for x in isr3 if x == hedef)
    P3 = a3 >= 2
    print("   -> %d/3 ayni isaret  ->  P3 %s" % (a3, "GECTI" if P3 else "DUSTU"))
    print()

    # -------- P4 --------
    print("### P4 — ELEME: OBI, son 1 saatlik hareketin izi mi?")
    orn = [r for r in sat if r.get("onceki") is not None and r.get("obi1") is not None]
    if len(orn) > 200000:
        orn = orn[::max(1, len(orn) // 200000)]
    rel = spearman([r["onceki"] for r in orn], [r["obi1"] for r in orn])
    P4 = rel is not None and abs(rel) < ELEME_TAVAN
    print("   spearman(onceki 1s getiri, OBI) = %s  (tavan %.2f, N=%d)"
          % (("%+.3f" % rel) if rel is not None else "yok", ELEME_TAVAN, len(orn)))
    print("   -> P4 %s" % ("GECTI" if P4 else "DUSTU"))
    print()

    # -------- P5 --------
    print("### P5 — onceki getiri uctebirlikleri (karistirici)")
    sf = sorted([r for r in sat if r.get("onceki") is not None], key=lambda r: r["onceki"])
    t3 = len(sf) // 3
    isr5 = []
    for ad, alt in (("alt (dusen saat)", sf[:t3]), ("orta", sf[t3:2 * t3]),
                    ("ust (yukselen saat)", sf[2 * t3:])):
        mm, tt, nn = gun_rho(alt)
        isr5.append(0 if mm is None else (1 if mm > 0 else -1))
        yaz(ad, mm, tt, nn)
    a5 = sum(1 for x in isr5 if x == hedef)
    P5 = a5 >= 2
    print("   -> %d/3 ayni isaret  ->  P5 %s" % (a5, "GECTI" if P5 else "DUSTU"))
    print()

    # -------- IKINCIL: UFUK MERDIVENI --------
    print("### 🔑 UFUK MERDIVENI (ikincil, GECTI'ye SAYILMAZ)")
    print("   Isi hukum vermek DEGIL: 'sinyal yok' ile 'sinyal var ama BIZIM")
    print("   ufkumuzda degil' ayrimini yapmak.")
    merdiven = []
    for alan, ad in UFUKLAR:
        mm, tt, nn = gun_rho(sat, "obi1", alan)
        merdiven.append((ad, mm, tt))
        yaz(ad, mm, tt, nn, "<- BIRINCIL" if alan == "r60" else "")
    print()

    # -------- IKINCIL: SEVIYE --------
    print("### SEVIYE (ikincil) — +1 saat ufkunda")
    for alan, ad in (("obi1", "±%1 (BIRINCIL)"), ("obi2", "±%2"), ("obi5", "±%5")):
        mm, tt, nn = gun_rho(sat, alan, "r60")
        yaz(ad, mm, tt, nn)
    print()

    # -------- EK RAPOR --------
    print("### EK RAPOR (hukum tasimaz)")
    ss = collections.defaultdict(list)
    for r in sat:
        if r.get("obi1") is not None:
            ss[r["sym"]].append(r)
    kal, deg = [], []
    for s, v in ss.items():
        mo = stx.mean([q["obi1"] for q in v])
        for q in v:
            kal.append(dict(q, obi1=mo))
            deg.append(dict(q, obi1=q["obi1"] - mo))
    mk, tk, nk = gun_rho(kal)
    md, td, nd = gun_rho(deg)
    print("   OBI ayristirmasi:")
    yaz("  KALICI (sembol ort.)", mk, tk, nk)
    yaz("  ZAMANLA DEGISEN", md, td, nd)
    v1 = [r["obi1"] for r in sat if r.get("obi1") is not None]
    print("   OBI ±%%1 dagilimi: ort %+.4f · medyan %+.4f · std %.4f · poz oran %%%.1f"
          % (stx.mean(v1), stx.median(v1), stx.stdev(v1),
             100.0 * sum(1 for x in v1 if x > 0) / len(v1)))
    n_per = sorted(sym.values())
    print("   sembol basina saat: min %d · medyan %d · maks %d"
          % (n_per[0], n_per[len(n_per) // 2], n_per[-1]))
    print()

    # -------- HUKUM --------
    print("=" * 96)
    print("HUKUM — ON_KAYIT_obi.md bolum 7")
    print("=" * 96)
    for ad, ok in (("P1", P1), ("P2", P2), ("P3", P3), ("P4", P4), ("P5", P5)):
        print("   %s %s" % (ad, "GECTI" if ok else "DUSTU"))
    hepsi = P1 and P2 and P3 and P4 and P5
    print()
    print("   SONUC: %s" % ("GECTI" if hepsi else "DUSTU"))
    print()
    en_guclu = max((x for x in merdiven if x[1] is not None),
                   key=lambda x: abs(x[1]), default=None)
    if en_guclu:
        print("   MERDIVEN OKUMASI: en guclu basamak %s (rho %+.4f, t %+.2f)"
              % (en_guclu[0], en_guclu[1], en_guclu[2] or 0))
    print("   Coklu karsilastirma (on-kayitta ilan): 21 hucre")
    print("   ⚠️ Etiket HAM getiri; maliyet/slipaj DAHIL DEGIL.")
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
