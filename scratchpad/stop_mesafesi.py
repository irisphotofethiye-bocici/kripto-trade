#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STOP MESAFESI — hakem raporunun 5. maddesi (2026-09-05)

ON-KAYIT: ON_KAYIT_stop_mesafesi.md, commit 409e514 — KOSTURULMADAN ONCE.
Bu betik o on-kaydi UYGULAR; olcut metnini degistirmez, ek kol/esik denemez.

SORU: A+B'nin (funding bacagi) stopu kapisina uymuyor mu? Genis stop kurtarir mi?

KOLLAR (dort, on-kayitli, gainer_stop.py'nin kumesi — yeni esik ICAT YOK):
  A     botun mevcut stopu (yapisal adaylardan girise en yakin, tavan 1.5xATR)
  1.5x  sabit 1.5 x ATR14      2.5x  sabit 2.5 x ATR14      4.0x  sabit 4.0 x ATR14
  Merdiven MONOTON: SHORT'ta A <= 1.5x <= 2.5x <= 4.0x  (sinama ile dogrulanir)

OLCU: R = net% / stop%  (BIRINCIL — bot risk-bazli boyutlandirir, R ~ dolar)
      net%                (ikincil, her zaman yazilir)
  YASAK: "stop genisligi ~ R" korelasyonu delil olarak raporlanmaz (ortak payda).

ESLESTIRME: asgari_stop %2.0 elemesi A kolunun stopuna gore -> dort kolda AYNI
  girisler -> eslesmis test. Her kolun KENDI elemesiyle akis ayrica sayilir
  (betimleyici, hukum tasimaz).

MEKANIK ileri_rr.py'den CAGRILIR (yeniden yazilmaz): atr_serisi / ma_serisi /
  stop_hesapla / fonlama_pct / btc_rejim. Hedef %10 · ufuk 72s · maliyet %0.13 ·
  fonlama DAHIL · giris tetigin ertesi barinin acilisi.

Salt-okunur. Bot dosyalarina yazim: YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import sys, json, os, math, bisect, random, statistics as stx, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olcum_ortak as oo
import ileri_rr as ir

BURA = os.path.dirname(os.path.abspath(__file__))
KLINE = ir.KLINE
FUND = ir.FUND

# --- ON-KAYITLI PARAMETRELER (degistirilmez) -------------------------------
HEDEF_PCT, UFUK = 10.0, 72
ISINMA, SEYRELT = ir.ISINMA, ir.SEYRELT
FUND_ESIK, PUMP, MIN_VOL = ir.FUND_ESIK, ir.PUMP, ir.MIN_VOL
UCUZ_FIYAT, MA50_MESAFE = ir.UCUZ_FIYAT, ir.MA50_MESAFE
ASGARI_STOP = 2.0
KOLLAR = [("A", None), ("1.5x", 1.5), ("2.5x", 2.5), ("4.0x", 4.0)]
VARYANT = ["1.5x", "2.5x", "4.0x"]          # A temeldir, varyant degil
PERM = 2000
random.seed(41)


# ------------------------------------------------------------------ sinama
def sinama():
    """Kosumdan ONCE dogrulanan sartlar. Duserse betik CALISMAYI REDDEDER."""
    hata = []

    # 1) Merdiven monotonlugu: A, tavani 1.5*ATR olan bir MINIMUM olmali.
    b = [{"t": i * 3600000, "o": 100.0, "h": 100.0 + (i % 7),
          "l": 100.0 - (i % 5), "c": 100.0 + (i % 3)} for i in range(300)]
    atrs = ir.atr_serisi(b)
    for si in (250, 260, 270, 280):
        ref, a = b[si + 1]["o"], atrs[si]
        sA = ir.stop_hesapla(b, si, ref, a)
        for ad, m in KOLLAR:
            if m is None:
                continue
            if sA > ref + m * a + 1e-9:
                hata.append("MERDIVEN BOZUK si=%d: A=%.6f > %s=%.6f" %
                            (si, sA, ad, ref + m * a))

    # 2) Maliyet birimi: yuzde olmali (0.13), oran (0.0013) DEGIL.
    if not (0.05 < oo.MALIYET < 1.0):
        hata.append("MALIYET birimi supheli: %r" % oo.MALIYET)

    # 3) Fonlama birimi: 'r' alani ZATEN yuzde olmali (bkz. olcumler.md birim
    #    kirilmasi vakasi). Medyan buyuklugu 0.5'in altinda kalmali.
    orn = []
    for fn in sorted(os.listdir(FUND))[:40]:
        if not fn.endswith(".json"):
            continue
        try:
            fr = json.load(open(os.path.join(FUND, fn), encoding="utf-8"))
        except Exception:
            continue
        orn += [abs(x["r"]) for x in fr[:200]]
    if orn:
        m = stx.median(orn)
        if m > 0.5:
            hata.append("FONLAMA birimi supheli: medyan |r| = %.4f (100 kat sisik?)" % m)
    else:
        hata.append("FONLAMA ornegi bos — birim dogrulanamadi")

    if hata:
        print("SINAMA DUSTU — betik calismayi REDDEDIYOR:")
        for h in hata:
            print("  - " + h)
        raise SystemExit(1)
    print("sinama: GECTI (merdiven monoton · maliyet %%%s · fonlama medyan |r|=%.4f)"
          % (oo.MALIYET, stx.median(orn)))


# ------------------------------------------------------------------ mekanik
def yol(b, gi, son, ref, stop, hedef):
    """SHORT tek islem. Bar ici sira: STOP(fitil) -> HEDEF(fitil).  -> (ham%, tip, j)"""
    sp = (stop - ref) / ref * 100
    hp = (ref - hedef) / ref * 100
    for j in range(gi, son):
        x = b[j]
        if x["h"] >= stop:
            return -sp, "STOP", j
        if x["l"] <= hedef:
            return hp, "HEDEF", j
    j = son - 1
    return (ref - b[j]["c"]) / ref * 100, "SURE", j


def tetik_isle(b, atrs, si, ft, fr, iki_r=False):
    """-> (kayit | None, akis_sp)  akis_sp = her kolun stop%'i (eleme sayimi icin)."""
    gi = si + 1
    if si < ISINMA or gi >= len(b) or not atrs[si]:
        return None, None
    ref = b[gi]["o"]
    a = atrs[si]
    if ref <= 0 or a <= 0:
        return None, None
    son = min(gi + UFUK, len(b))
    if son - gi < 4:
        return None, None

    stoplar, akis_sp = {}, {}
    for ad, m in KOLLAR:
        s = ir.stop_hesapla(b, si, ref, a) if m is None else ref + m * a
        sp = (s - ref) / ref * 100
        stoplar[ad] = (s, sp)
        akis_sp[ad] = sp

    spA = stoplar["A"][1]
    if spA <= 0 or spA < ASGARI_STOP:          # ESLESTIRME: eleme A'ya gore
        return None, akis_sp

    kayit = {"sym": None, "ts": b[gi]["t"], "gun": b[gi]["t"] // 86400000, "kol": {}}
    for ad, _ in KOLLAR:
        s, sp = stoplar[ad]
        if sp <= 0:
            return None, akis_sp
        hedef = (ref - 2.0 * (s - ref)) if iki_r else ref * (1 - HEDEF_PCT / 100)
        if hedef <= 0:
            return None, akis_sp
        ham, tip, j = yol(b, gi, son, ref, s, hedef)
        fon = ir.fonlama_pct(ft, fr, b[gi]["t"], b[j]["t"])
        net = ham - oo.MALIYET + fon
        kayit["kol"][ad] = {"net": net, "R": net / sp, "tip": tip,
                            "saat": j - gi, "sp": sp}
    return kayit, akis_sp


# ------------------------------------------------------------------ tarama
def tara(iki_r=False):
    rej = ir.btc_rejim()
    kume = {"A_funding": [], "B_ma50ucuz": []}
    akis = {"A_funding": collections.Counter(), "B_ma50ucuz": collections.Counter()}
    islenen = 0
    for fn in sorted(os.listdir(KLINE)):
        if not fn.endswith(".json"):
            continue
        sym = fn[:-5]
        try:
            b = json.load(open(os.path.join(KLINE, fn), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ISINMA + UFUK + 50:
            continue
        fpath = os.path.join(FUND, fn)
        fr = []
        if os.path.exists(fpath):
            try:
                fr = json.load(open(fpath, encoding="utf-8"))
            except Exception:
                fr = []
        ft = [x["t"] for x in fr]
        atrs = ir.atr_serisi(b)
        ma50 = ir.ma_serisi(b, 50)
        islenen += 1
        for i in range(ISINMA, len(b) - UFUK - 2, SEYRELT):
            x = b[i]
            if (x.get("qv") or 0) < MIN_VOL / 24:
                continue
            if i < 24:
                continue
            if (x["c"] / b[i - 24]["c"] - 1) * 100 >= PUMP:
                continue
            hedefler = []
            if ft:
                k = bisect.bisect_right(ft, x["t"]) - 1
                if k >= 0 and fr[k]["r"] <= FUND_ESIK:
                    hedefler.append("A_funding")
            if ma50[i] and ma50[i] > 0 and x["c"] <= UCUZ_FIYAT:
                if (x["c"] / ma50[i] - 1) * 100 >= MA50_MESAFE:
                    hedefler.append("B_ma50ucuz")
            if not hedefler:
                continue
            kayit, akis_sp = tetik_isle(b, atrs, i, ft, fr, iki_r)
            if akis_sp:
                for h in hedefler:
                    for ad, sp in akis_sp.items():
                        if sp >= ASGARI_STOP:
                            akis[h][ad] += 1
            if not kayit:
                continue
            kayit["sym"] = sym
            kayit["rejim"] = rej.get(b[i]["t"] // 3600000, "NOTR")
            for h in hedefler:
                kume[h].append(kayit)
    return kume, akis, islenen


# ------------------------------------------------------------------ istatistik
def gun_ort(kayitlar, fark_fn):
    """Gun -> o gunun ortalama eslesmis farki."""
    g = collections.defaultdict(list)
    for k in kayitlar:
        v = fark_fn(k)
        if v is not None:
            g[k["gun"]].append(v)
    return {d: sum(v) / len(v) for d, v in g.items()}


def t_ve_mde(gunler):
    """gunler: {gun: ort}  -> (ort, t, mde, n_gun)"""
    vals = list(gunler.values())
    n = len(vals)
    if n < 3:
        return None, None, None, n
    m = sum(vals) / n
    sd = stx.stdev(vals)
    se = sd / math.sqrt(n)
    return m, (m / se if se else None), (2.0 * se if se else None), n


def permutasyon(kayitlar, alan):
    """Isaret-cevirme (gun bazinda). -> {varyant: p}, ve gozlenen max|t|."""
    gunler = sorted({k["gun"] for k in kayitlar})
    gv = {}
    for v in VARYANT:
        gv[v] = gun_ort(kayitlar, lambda k, v=v: k["kol"][v][alan] - k["kol"]["A"][alan])
    goz = {}
    for v in VARYANT:
        _, t, _, _ = t_ve_mde(gv[v])
        goz[v] = abs(t) if t is not None else 0.0
    goz_max = max(goz.values()) if goz else 0.0

    asan = 0
    for _ in range(PERM):
        isaret = {d: (1 if random.random() < 0.5 else -1) for d in gunler}
        en = 0.0
        for v in VARYANT:
            vals = [isaret[d] * x for d, x in gv[v].items()]
            n = len(vals)
            if n < 3:
                continue
            m = sum(vals) / n
            sd = stx.stdev(vals)
            se = sd / math.sqrt(n)
            if se:
                en = max(en, abs(m / se))
        if en >= goz_max:
            asan += 1
    return goz, goz_max, (asan + 1) / (PERM + 1)


# ------------------------------------------------------------------ rapor
def kol_tablo(kayitlar, baslik):
    print("  %-6s %8s %9s %9s %8s %8s %7s" %
          ("kol", "stop%", "net%", "R", "stop-ol%", "hedef%", "saat"))
    for ad, _ in KOLLAR:
        sp = stx.mean([k["kol"][ad]["sp"] for k in kayitlar])
        nt = stx.mean([k["kol"][ad]["net"] for k in kayitlar])
        rr = stx.mean([k["kol"][ad]["R"] for k in kayitlar])
        so = sum(1 for k in kayitlar if k["kol"][ad]["tip"] == "STOP") / len(kayitlar) * 100
        hd = sum(1 for k in kayitlar if k["kol"][ad]["tip"] == "HEDEF") / len(kayitlar) * 100
        sa = stx.mean([k["kol"][ad]["saat"] for k in kayitlar])
        print("  %-6s %8.2f %+9.3f %+9.4f %8.1f %8.1f %7.1f" % (ad, sp, nt, rr, so, hd, sa))


def fark_tablo(kayitlar, alan, etiket):
    print("  eslesmis fark (kol - A), %s:" % etiket)
    print("  %-6s %10s %8s %8s %7s %s" % ("kol", "fark", "t_gun", "MDE", "gun", "gorulur mu"))
    out = {}
    for v in VARYANT:
        g = gun_ort(kayitlar, lambda k, v=v: k["kol"][v][alan] - k["kol"]["A"][alan])
        m, t, mde, n = t_ve_mde(g)
        out[v] = (m, t, mde, n)
        gor = "GORULUR" if (m is not None and mde is not None and abs(m) >= mde) else "goremiyoruz"
        print("  %-6s %+10.4f %+8.2f %8.4f %7d  %s" %
              (v, m, t if t is not None else 0, mde, n, gor))
    return out


def yari_kontrol(kayitlar, alan, v):
    ts = sorted(k["ts"] for k in kayitlar)
    orta = ts[len(ts) // 2]
    a = [k for k in kayitlar if k["ts"] < orta]
    b = [k for k in kayitlar if k["ts"] >= orta]
    r = []
    for yar in (a, b):
        if len(yar) < 20:
            r.append(None)
            continue
        g = gun_ort(yar, lambda k: k["kol"][v][alan] - k["kol"]["A"][alan])
        m, _, _, _ = t_ve_mde(g)
        r.append(m)
    return r


def rejim_kontrol(kayitlar, alan, v):
    out = {}
    for rj in ("BOGA", "NOTR", "AYI"):
        s = [k for k in kayitlar if k["rejim"] == rj]
        if len(s) < 20:
            out[rj] = None
            continue
        g = gun_ort(s, lambda k: k["kol"][v][alan] - k["kol"]["A"][alan])
        m, _, _, n = t_ve_mde(g)
        out[rj] = (m, len(s), n)
    return out


def main():
    print("=" * 78)
    print("STOP MESAFESI — A+B'nin FUNDING BACAGI (oi24 olculemez, bkz. on-kayit)")
    print("=" * 78)
    print("ON-KAYIT: ON_KAYIT_stop_mesafesi.md commit 409e514 — KOSMADAN once")
    print("Mekanik: ileri_rr'den CAGRILIR · hedef %%%s · %ss · maliyet %%%s · FONLAMA DAHIL"
          % (HEDEF_PCT, UFUK, oo.MALIYET))
    print("Eslestirme: asgari_stop %%%.1f, A koluna gore -> dort kolda AYNI girisler\n"
          % ASGARI_STOP)
    sinama()

    kume, akis, islenen = tara(iki_r=False)
    print("islenen sembol: %d\n" % islenen)

    sonuc = {}
    for ad in ("A_funding", "B_ma50ucuz"):
        ky = kume[ad]
        if len(ky) < 40:
            print("### %s — yetersiz N (%d)\n" % (ad, len(ky)))
            continue
        gun = len({k["gun"] for k in ky})
        sem = len({k["sym"] for k in ky})
        print("### %s   N=%d islem · %d gun · %d sembol" % (ad, len(ky), gun, sem))
        c = collections.Counter(k["sym"] for k in ky)
        print("    en sik 5 sembol payi: %.0f%%" %
              (sum(n for _, n in c.most_common(5)) / len(ky) * 100))
        kol_tablo(ky, ad)
        print()
        rr = fark_tablo(ky, "R", "BIRINCIL olcu R")
        print()
        nt = fark_tablo(ky, "net", "ikincil olcu net%")
        print()
        goz, gmax, p = permutasyon(ky, "R")
        print("  permutasyon (isaret-cevirme, gun bazinda, %d tur):" % PERM)
        print("    gozlenen |t|: %s" % "  ".join("%s=%.2f" % (v, goz[v]) for v in VARYANT))
        print("    max|t| = %.2f   ->   p = %.4f" % (gmax, p))
        print("  akis (her kol KENDI %%%.1f elemesiyle kac aday gecerdi — BETIMLEYICI):"
              % ASGARI_STOP)
        print("    " + "  ".join("%s=%d" % (a, akis[ad][a]) for a, _ in KOLLAR))
        print()
        sonuc[ad] = {"ky": ky, "R": rr, "net": nt, "p": p, "gmax": gmax}

    # ---- HUKUM (on-kayitli olcutler) ----
    print("=" * 78)
    print("HUKUM — ON_KAYIT_stop_mesafesi.md bolum 9")
    print("=" * 78)
    if "A_funding" not in sonuc:
        print("A_funding olculemedi -> hukum YOK")
        return
    s = sonuc["A_funding"]
    ky = s["ky"]
    aday = [(v, s["R"][v][0], s["R"][v][1]) for v in VARYANT
            if s["R"][v][0] is not None and s["R"][v][0] > 0
            and s["R"][v][1] is not None and s["R"][v][1] >= 2.0]
    K1 = bool(aday) and s["p"] <= 0.05
    print("K1  R farki > 0 · t_gun >= +2.0 · permutasyon p <= 0.05")
    if not aday:
        print("    -> DUSTU: hicbir varyant t>=+2.0 ile pozitif degil")
    else:
        print("    aday: %s   permutasyon p=%.4f -> %s"
              % (", ".join("%s (%+.4f, t=%+.2f)" % a for a in aday), s["p"],
                 "GECTI" if K1 else "DUSTU (permutasyon)"))
    if K1:
        v = max(aday, key=lambda a: a[2])[0]
        ya, yb = yari_kontrol(ky, "R", v)
        K2 = (ya is not None and yb is not None and ya > 0 and yb > 0)
        print("K2  iki yaride ayni isaret: %s / %s -> %s"
              % (("%+.4f" % ya) if ya is not None else "yok",
                 ("%+.4f" % yb) if yb is not None else "yok", "GECTI" if K2 else "DUSTU"))
        idx = VARYANT.index(v)
        koms = [VARYANT[j] for j in (idx - 1, idx + 1) if 0 <= j < len(VARYANT)]
        kv = [s["R"][c][0] for c in koms]
        K3 = any(x is not None and x > 0 for x in kv)
        print("K3  komsu hucre ayni isaret: %s -> %s"
              % (", ".join("%s=%+.4f" % (c, s["R"][c][0]) for c in koms),
                 "GECTI" if K3 else "DUSTU (yalitik hucre)"))
        rj = rejim_kontrol(ky, "R", v)
        isar = [x[0] for x in rj.values() if x is not None]
        K4 = bool(isar) and (all(x > 0 for x in isar) or all(x < 0 for x in isar))
        print("K4  rejimde ters isaret yok: %s -> %s"
              % (" · ".join("%s %s" % (k, ("%+.4f (N=%d)" % (x[0], x[1])) if x else "yetersiz")
                            for k, x in rj.items()), "GECTI" if K4 else "DUSTU"))
        print("\nSONUC: %s" % ("GECTI" if (K2 and K3 and K4) else
                               ("ZAYIF" if K2 else "DUSTU")))
    else:
        print("K2/K3/K4 uygulanmadi (K1 dustu)")
        print("\nSONUC: DUSTU")

    # ---- ASIMETRI (on-kayit bolum 10) ----
    print("\n" + "=" * 78)
    print("ASIMETRI SORUSU — iki kapinin genislik profili ayni mi?")
    print("=" * 78)
    if "B_ma50ucuz" in sonuc:
        for m in ("R", "net"):
            print("  %s farklari (kol - A):" % ("R" if m == "R" else "net%"))
            for v in VARYANT:
                a = sonuc["A_funding"][m][v][0]
                b = sonuc["B_ma50ucuz"][m][v][0]
                ayni = "AYNI yon" if (a is not None and b is not None and a * b > 0) else "AYRISIYOR"
                print("    %-6s A_funding %+9.4f   B_ma50ucuz %+9.4f   -> %s" % (v, a, b, ayni))
        print("\n  YORUM KURALI (on-kayitli): profiller niteliksel olarak AYNIYSA")
        print("  asimetri iddiasi (A+B %65 vs MA50+ucuz %0) DESTEKLENMEDI.")
    else:
        print("  B_ma50ucuz olculemedi.")

    # ---- IKINCIL: 2R hedef ----
    print("\n" + "=" * 78)
    print("IKINCIL (on-kayitli, BETIMLEYICI): hedef = 2 x risk — R olcegi korunur")
    print("=" * 78)
    k2, _, _ = tara(iki_r=True)
    for ad in ("A_funding", "B_ma50ucuz"):
        if len(k2.get(ad, [])) < 40:
            continue
        print("### %s   N=%d" % (ad, len(k2[ad])))
        kol_tablo(k2[ad], ad)
        fark_tablo(k2[ad], "R", "R")
        print()

    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
