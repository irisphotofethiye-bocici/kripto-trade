#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CAPRAZ BORSA — OLCUM (2026-09-05)

ON-KAYIT: ON_KAYIT_capraz_borsa.md, commit a0e52c5 — KOSUMDAN ONCE yazildi.
Olcutler burada YENIDEN YAZILMAZ, on-kayittan AYNEN alinir:

   C1 🔴 gun-kumeli rho : |rho| >= 0,020 VE |t| >= 3,0 · isaret NEGATIF
   C2    dort zaman ceyregi        : >= 3/4 ayni isaret
   C3    rejim (BOGA/NOTR/AYI)     : >= 2/3 ayni isaret
   C4    eleme |spearman(fark,f_bin)| : < 0,50
   C5    binance fonlama uctebirlik : >= 2/3 ayni isaret
   GECTI = besi birden.

   C6 IKINCIL (onceden ilan, GECTI'ye SAYILMAZ): |fark| >= gunun %90'lik dilimi

GECERLILIK KAPISI (on-kayit bolum 5) — duserse olcum DURUR, olcut gevsetilmez.

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

MIN_SEMBOL_GUN = 10       # bir gunde kesitsel rho icin gereken en az sembol.
#   Mekanik zorunluluk (2 sembolle rho anlamsiz), ayar dugmesi DEGIL. Raporlanir.
RHO_TABAN = 0.020         # on-kayit C1 — basis olcumunden AYNEN alindi
T_TABAN = 3.0
ELEME_TAVAN = 0.50        # on-kayit C4


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


def gun_rho(satirlar, x_alan="fark", y_alan="fwd24"):
    """Gun ICINDE kesitsel rho, sonra gun-kumeli ortalama ve t.
    -> (rho_ort, t, n_gun, gunluk_rho_listesi)"""
    g = collections.defaultdict(list)
    for r in satirlar:
        g[r["gun"]].append(r)
    rhos = []
    for gun, v in g.items():
        # ayni sembolun ayni gunde birden cok fonlama damgasi olabilir -> sembol ort.
        s = collections.defaultdict(list)
        for r in v:
            s[r["sym"]].append(r)
        xs, ys = [], []
        for sym, rr in s.items():
            xs.append(stx.mean([q[x_alan] for q in rr]))
            ys.append(stx.mean([q[y_alan] for q in rr]))
        if len(xs) < MIN_SEMBOL_GUN:
            continue
        r_ = spearman(xs, ys)
        if r_ is not None:
            rhos.append((gun, r_))
    if len(rhos) < 3:
        return None, None, len(rhos), rhos
    v = [r for _, r in rhos]
    m = stx.mean(v)
    se = stx.stdev(v) / math.sqrt(len(v))
    return m, (m / se if se else None), len(rhos), rhos


def yaz(ad, m, t, n):
    print("   %-26s rho %s   t %s   gun %d"
          % (ad,
             ("%+.4f" % m) if m is not None else "  yok ",
             ("%+.2f" % t) if t is not None else " yok ", n))


def main():
    print("=" * 96)
    print("CAPRAZ BORSA — BINANCE - BYBIT FONLAMA FARKI")
    print("=" * 96)
    print("ON-KAYIT: ON_KAYIT_capraz_borsa.md commit a0e52c5 — KOSUMDAN ONCE")
    print("Hipotez: fark yuksek = Binance'te uzun taraf kalabalik -> rho NEGATIF")
    print()

    sat = []
    with open(PANEL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                sat.append(json.loads(line))
    semboller = collections.Counter(r["sym"] for r in sat)
    gunler = sorted(set(r["gun"] for r in sat))
    print("N gozlem = %d  ·  sembol = %d  ·  gun = %d  (%s .. %s)"
          % (len(sat), len(semboller), len(gunler), gunler[0], gunler[-1]))
    print()

    # ---------------- GECERLILIK KAPISI ------------------------------------
    print("### GECERLILIK KAPISI (on-kayit bolum 5)")
    kb = min(semboller.values()) if semboller else 0
    m0, t0, n0, _ = gun_rho(sat)
    kapi = {
        "K-a gunluk orana cevirme": ("02_veri.py sinamasi 4/4 gecti", True),
        "K-c sembol basina >=100 gozlem": ("en az %d" % kb, kb >= 100),
        "K-d gun kumesi >= 300": ("%d gun" % n0, n0 >= 300),
    }
    for ad, (detay, ok) in kapi.items():
        print("   %-34s %-22s %s" % (ad, detay, "✅" if ok else "🔴 DUSTU"))
    if not all(ok for _, ok in kapi.values()):
        print()
        print("🔴 GECERLILIK KAPISI DUSTU -> OLCUM DURDU. Olcut gevsetilmez.")
        return
    print()

    # ---------------- SAGLAMA: ayna testi ----------------------------------
    print("### SAGLAMA — ters yon (bybit - binance) isareti aynalamali")
    ters = [dict(r, fark=-r["fark"]) for r in sat]
    mt, tt, _, _ = gun_rho(ters)
    ok_ayna = (m0 is not None and mt is not None and abs(m0 + mt) < 1e-9)
    print("   duz  rho %+.4f   ·   ters rho %+.4f   ->  %s"
          % (m0, mt, "✅ aynaliyor" if ok_ayna else "🔴 BETIK HATALI"))
    if not ok_ayna:
        return
    print()

    # ---------------- C1 ---------------------------------------------------
    print("### C1 🔴 BIRINCIL — gun-kumeli rho")
    yaz("TUM PENCERE", m0, t0, n0)
    C1 = (m0 is not None and t0 is not None and m0 < 0
          and abs(m0) >= RHO_TABAN and abs(t0) >= T_TABAN)
    print("   esik: |rho| >= %.3f VE |t| >= %.1f VE isaret NEGATIF" % (RHO_TABAN, T_TABAN))
    print("   -> C1 %s" % ("GECTI" if C1 else "DUSTU"))
    if m0 is not None and abs(m0) < RHO_TABAN and t0 is not None and abs(t0) >= T_TABAN:
        print("   📌 basis ile AYNI DESEN: t buyuk, etki kucuk. Taban tam bunun icin vardi.")
    print()

    # ---------------- C2 ---------------------------------------------------
    print("### C2 — dort zaman ceyregi")
    q = len(gunler) // 4
    dilimler = [gunler[:q], gunler[q:2 * q], gunler[2 * q:3 * q], gunler[3 * q:]]
    isaretler = []
    for i, d in enumerate(dilimler, 1):
        ds = set(d)
        mm, tt2, nn, _ = gun_rho([r for r in sat if r["gun"] in ds])
        isaretler.append(0 if mm is None else (1 if mm > 0 else -1))
        yaz("C%d  %s..%s" % (i, d[0], d[-1]), mm, tt2, nn)
    hedef = -1 if (m0 or 0) < 0 else 1
    ayni = sum(1 for x in isaretler if x == hedef)
    C2 = ayni >= 3
    print("   -> %d/4 ayni isaret  ->  C2 %s" % (ayni, "GECTI" if C2 else "DUSTU"))
    print()

    # ---------------- C3 ---------------------------------------------------
    print("### C3 — rejim")
    r_is = []
    for rej in ("BOGA", "NOTR", "AYI"):
        alt = [r for r in sat if r["rejim"] == rej]
        mm, tt2, nn, _ = gun_rho(alt)
        r_is.append(0 if mm is None else (1 if mm > 0 else -1))
        yaz(rej, mm, tt2, nn)
    ayni3 = sum(1 for x in r_is if x == hedef)
    C3 = ayni3 >= 2
    print("   -> %d/3 ayni isaret  ->  C3 %s" % (ayni3, "GECTI" if C3 else "DUSTU"))
    print()

    # ---------------- C4 ---------------------------------------------------
    print("### C4 — ELEME: fark, Binance fonlamasinin kopyasi mi?")
    ornek = sat if len(sat) <= 200000 else sat[::max(1, len(sat) // 200000)]
    rel = spearman([r["f_bin"] for r in ornek], [r["fark"] for r in ornek])
    C4 = rel is not None and abs(rel) < ELEME_TAVAN
    print("   spearman(f_bin, fark) = %s   (tavan %.2f, N=%d)"
          % (("%+.3f" % rel) if rel is not None else "yok", ELEME_TAVAN, len(ornek)))
    print("   -> C4 %s" % ("GECTI" if C4 else "DUSTU"))
    print()

    # ---------------- C5 ---------------------------------------------------
    print("### C5 — Binance fonlamasi uctebirlikleri (karistirici)")
    sf = sorted(sat, key=lambda r: r["f_bin"])
    t3 = len(sf) // 3
    f_is = []
    for ad, alt in (("alt (dusuk fonlama)", sf[:t3]), ("orta", sf[t3:2 * t3]),
                    ("ust (yuksek fonlama)", sf[2 * t3:])):
        mm, tt2, nn, _ = gun_rho(alt)
        f_is.append(0 if mm is None else (1 if mm > 0 else -1))
        yaz(ad, mm, tt2, nn)
    ayni5 = sum(1 for x in f_is if x == hedef)
    C5 = ayni5 >= 2
    print("   -> %d/3 ayni isaret  ->  C5 %s" % (ayni5, "GECTI" if C5 else "DUSTU"))
    print()

    # ---------------- C6 IKINCIL ------------------------------------------
    print("### C6 IKINCIL (onceden ilan, GECTI'ye SAYILMAZ) — BUYUK FARK kuyrugu")
    gg = collections.defaultdict(list)
    for r in sat:
        gg[r["gun"]].append(abs(r["fark"]))
    esik = {}
    for gun, v in gg.items():
        v2 = sorted(v)
        esik[gun] = v2[int(len(v2) * 0.90)] if v2 else 0
    kuyruk = [r for r in sat if abs(r["fark"]) >= esik.get(r["gun"], 1e9)]
    mk, tk, nk, _ = gun_rho(kuyruk)
    yaz("|fark| >= gunun %90'i", mk, tk, nk)
    print("   N = %d (%.1f%% of %d)" % (len(kuyruk), 100.0 * len(kuyruk) / len(sat), len(sat)))
    print()

    # ---------------- EK RAPOR --------------------------------------------
    print("### EK RAPOR (hukum tasimaz)")
    ss = collections.defaultdict(list)
    for r in sat:
        ss[r["sym"]].append(r)
    kal, degisen = [], []
    for sym, v in ss.items():
        mf = stx.mean([q["fark"] for q in v])
        for q in v:
            kal.append(dict(q, fark=mf))
            degisen.append(dict(q, fark=q["fark"] - mf))
    mk1, tk1, nk1, _ = gun_rho(kal)
    mk2, tk2, nk2, _ = gun_rho(degisen)
    print("   farkin AYRISTIRMASI (bası olcumunde belirleyici olmustu):")
    yaz("  KALICI (sembol ort.)", mk1, tk1, nk1)
    yaz("  ZAMANLA DEGISEN", mk2, tk2, nk2)
    n_per = sorted(semboller.values())
    print("   sembol basina gozlem: min %d · medyan %d · maks %d"
          % (n_per[0], n_per[len(n_per) // 2], n_per[-1]))
    print()

    # ---------------- HUKUM ------------------------------------------------
    print("=" * 96)
    print("HUKUM — ON_KAYIT_capraz_borsa.md bolum 6")
    print("=" * 96)
    for ad, ok in (("C1", C1), ("C2", C2), ("C3", C3), ("C4", C4), ("C5", C5)):
        print("   %s %s" % (ad, "GECTI" if ok else "DUSTU"))
    hepsi = C1 and C2 and C3 and C4 and C5
    print()
    print("   SONUC: %s" % ("GECTI" if hepsi else "DUSTU"))
    print()
    print("   Coklu karsilastirma (on-kayitta ilan): 5 birincil + 1 ikincil")
    print("   + 4 zaman ceyregi + 3 rejim + 3 fonlama dilimi = 16 hucre")
    print("   ⚠️ Etiket HAM getiri; fonlama/ucret DAHIL DEGIL (gidis-donus %0,19).")
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
