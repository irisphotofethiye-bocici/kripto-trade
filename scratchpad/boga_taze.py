#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOGA PENCERESI, TAZE VERIYLE — iki kapi birden (2026-09-05)

ON-KAYITLAR (ikisi de KOSUMDAN ONCE yazildi, olcutleri DEGISTIRILMEDI):
  A_funding  -> ON_KAYIT_boga_holdout.md  (commit 5144a45)  K1 isaret testi ...
  MA50+ucuz  -> ON_KAYIT_ma50_boga.md     (commit 42e6452)  K1..K4 kapi vs kontrol

VERI KAYNAGI DEGISTI (kullanici onayi: "tamam yap, eldeki veriyi ezme ama"):
  eski: perp_seri (151 sembol) + radar_archive (kapi + fonlama)
  yeni: klines_1h_uzun + taze_1h   ·   funding_gecmis + taze_funding
        -> BELLEKTE birlestirilir, HICBIR DOSYAYA YAZILMAZ
🔑 SONUC: radar_archive HIC KULLANILMIYOR -> onceki olcumu durduran
   dongu-damgasi hizalama kapisi ARTIK GECERSIZ. Olcutler aynen duruyor.

Mekanik ileri_rr'den CAGRILIR. Salt-okunur.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import sys, json, os, math, statistics as stx, collections, datetime as dt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olcum_ortak as oo
import ileri_rr as ir

BURA = os.path.dirname(os.path.abspath(__file__))
ESKI_K = os.path.join(BURA, "klines_1h_uzun")
YENI_K = os.path.join(BURA, "taze_1h")
ESKI_F = os.path.join(BURA, "funding_gecmis")
YENI_F = os.path.join(BURA, "taze_funding")
PERP = os.path.join(BURA, "perp_seri")

# --- ON-KAYITLI PARAMETRELER (degistirilmez) ---
FUND_ESIK, OI24_ESIK = -0.05, 10.0
UCUZ_FIYAT, MA50_MESAFE = 0.07, 3.72
PUMP, MIN_VOL = 20.0, 3_000_000
HEDEF_PCT, UFUK = 10.0, 72
ASGARI_STOP = 2.0
ISINMA, SOGUMA_SAAT = 220, 24
BOGA_BAS = "2026-08-21"
KOLLAR = [("A", None), ("1.5x", 1.5), ("2.5x", 2.5), ("4.0x", 4.0)]
VARYANT = ["1.5x", "2.5x", "4.0x"]
ADAY, KOMSU = "2.5x", "4.0x"


# ------------------------------------------------------------------ veri
def birlestir(eski_yol, yeni_yol):
    """BELLEKTE birlestirir. Hicbir dosyaya yazmaz. -> liste | None"""
    d = {}
    for yol in (eski_yol, yeni_yol):
        if not os.path.exists(yol):
            continue
        try:
            for x in json.load(open(yol, encoding="utf-8")):
                d[int(x["t"])] = x
        except Exception:
            continue
    return [d[k] for k in sorted(d)] if d else None


def yukle():
    kl, fn = {}, {}
    semboller = sorted(f[:-5] for f in os.listdir(ESKI_K) if f.endswith(".json"))
    for sym in semboller:
        b = birlestir(os.path.join(ESKI_K, sym + ".json"),
                      os.path.join(YENI_K, sym + ".json"))
        if not b or len(b) < ISINMA + UFUK + 50:
            continue
        kl[sym] = b
        f = birlestir(os.path.join(ESKI_F, sym + ".json"),
                      os.path.join(YENI_F, sym + ".json"))
        fn[sym] = f or []
    return kl, fn


def oi24_serisi():
    """perp_seri OI -> {sym: [(t_ms, oi24_pct)]}. A+B alt kumesi (K4) icin.
    Arsiv KULLANILMAZ; 24 saatlik OI degisimi 5dk seriden turetilir."""
    out = {}
    if not os.path.isdir(PERP):
        return out
    for f in os.listdir(PERP):
        if not f.endswith("_oi.json"):
            continue
        sym = f[:-8]
        try:
            j = json.load(open(os.path.join(PERP, f), encoding="utf-8"))
        except Exception:
            continue
        if len(j) < 300:
            continue
        ts = [int(x["timestamp"]) for x in j]
        vv = [float(x["sumOpenInterest"]) for x in j]
        seri = []
        for i in range(len(ts)):
            hedef = ts[i] - 86400000
            lo, hi, k = 0, i, None
            while lo <= hi:
                mid = (lo + hi) // 2
                if ts[mid] <= hedef:
                    k = mid
                    lo = mid + 1
                else:
                    hi = mid - 1
            if k is None or vv[k] <= 0 or ts[i] - ts[k] > 26 * 3600000:
                continue
            seri.append((ts[i], (vv[i] / vv[k] - 1) * 100))
        if seri:
            out[sym] = seri
    return out


def deger_at(seri, t, tolerans=2 * 3600000):
    if not seri:
        return None
    lo, hi, en = 0, len(seri) - 1, None
    while lo <= hi:
        mid = (lo + hi) // 2
        if seri[mid][0] <= t:
            en = seri[mid]
            lo = mid + 1
        else:
            hi = mid - 1
    if en is None or t - en[0] > tolerans:
        return None
    return en[1]


# ------------------------------------------------------------------ sinama
def sinama(kl, fn):
    hata = []
    b = [{"t": i * 3600000, "o": 100.0, "h": 100.0 + (i % 7),
          "l": 100.0 - (i % 5), "c": 100.0 + (i % 3)} for i in range(300)]
    atrs = ir.atr_serisi(b)
    for si in (250, 270):
        ref, a = b[si + 1]["o"], atrs[si]
        sA = ir.stop_hesapla(b, si, ref, a)
        for ad, m in KOLLAR:
            if m is not None and sA > ref + m * a + 1e-9:
                hata.append("S1 MERDIVEN BOZUK si=%d kol=%s" % (si, ad))

    # S2 — birlestirme SUREKLI mi? eski/yeni sinirinda delik olmamali
    sinir = int(dt.datetime.strptime("2026-08-25", "%Y-%m-%d")
                .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    delik = 0
    for sym, b2 in list(kl.items())[:120]:
        pen = [x["t"] for x in b2 if sinir - 86400000 <= x["t"] <= sinir + 86400000]
        if len(pen) < 40:
            delik += 1
    if delik > 12:
        hata.append("S2 BIRLESTIRME DELIKLI: %d/120 sembolde 08-25 civari eksik" % delik)
    else:
        print("  S2 birlestirme surekliligi: GECTI (%d/120 sembolde bosluk)" % delik)

    # S3 — fonlama birimi yuzde mi (funding_gecmis ile taze ayni birimde mi)
    orn = [abs(x["r"]) for s in list(fn)[:60] for x in (fn[s] or [])[-40:]]
    if orn:
        med = stx.median(orn)
        print("  S3 fonlama birimi: medyan |r| = %.4f" % med)
        if med > 0.5:
            hata.append("S3 FONLAMA BIRIMI SUPHELI: %.4f (100 kat sisik?)" % med)
    else:
        hata.append("S3 fonlama ornegi bos")

    if hata:
        print("\nSINAMA DUSTU — betik calismayi REDDEDIYOR:")
        for h in hata:
            print("  - " + h)
        raise SystemExit(1)
    print("  S1 merdiven: GECTI\n")


# ------------------------------------------------------------------ mekanik
def yol(b, gi, son, ref, stop, hedef):
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


def islem(b, atrs, si, ft, fr):
    gi = si + 1
    if si < ISINMA or gi >= len(b) or not atrs[si] or atrs[si] <= 0:
        return None
    ref, a = b[gi]["o"], atrs[si]
    if ref <= 0:
        return None
    son = min(gi + UFUK, len(b))
    if son - gi < 4:
        return None
    sA = ir.stop_hesapla(b, si, ref, a)
    spA = (sA - ref) / ref * 100
    if spA <= 0 or spA < ASGARI_STOP:
        return None
    hedef = ref * (1 - HEDEF_PCT / 100)
    out = {}
    for ad, m in KOLLAR:
        s = sA if m is None else ref + m * a
        sp = (s - ref) / ref * 100
        if sp <= 0:
            return None
        ham, tip, j = yol(b, gi, son, ref, s, hedef)
        f = ir.fonlama_pct(ft, fr, b[gi]["t"], b[j]["t"])
        net = ham - oo.MALIYET + f
        out[ad] = {"net": net, "R": net / sp, "tip": tip, "sp": sp, "saat": j - gi}
    return out


def tara(kl, fn, oi):
    bas = int(dt.datetime.strptime(BOGA_BAS, "%Y-%m-%d")
              .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    en_son = max(b[-1]["t"] for b in kl.values())
    kesme = en_son - UFUK * 3600000
    kume = {"A_funding": [], "MA50": [], "K_dar": [], "K_genis": []}
    son = {k: {} for k in kume}
    for sym, b in kl.items():
        fr = fn.get(sym) or []
        ft = [x["t"] for x in fr]
        atrs = ir.atr_serisi(b)
        ma50 = ir.ma_serisi(b, 50)
        oser = oi.get(sym)
        r_cache = {}
        for i in range(ISINMA, len(b)):
            x = b[i]
            if x["t"] < bas or x["t"] > kesme:
                continue
            if (x.get("qv") or 0) < MIN_VOL / 24:
                continue
            if i < 24 or b[i - 24]["c"] <= 0:
                continue
            if (x["c"] / b[i - 24]["c"] - 1) * 100 >= PUMP:
                continue
            hedefler = ["K_genis"]
            fd = None
            if ft:
                k = ir.bisect.bisect_right(ft, x["t"]) - 1
                if k >= 0:
                    fd = fr[k]["r"]
            if fd is not None and fd <= FUND_ESIK:
                hedefler.append("A_funding")
            ucuz = x["c"] <= UCUZ_FIYAT
            uzak = bool(ma50[i]) and ma50[i] > 0 and \
                (x["c"] / ma50[i] - 1) * 100 >= MA50_MESAFE
            if ucuz and uzak:
                hedefler.append("MA50")
            elif ucuz:
                hedefler.append("K_dar")
            for h in hedefler:
                s0 = son[h].get(sym)
                if s0 is not None and x["t"] - s0 < SOGUMA_SAAT * 3600000:
                    continue
                if i not in r_cache:
                    r_cache[i] = islem(b, atrs, i, ft, fr)
                r = r_cache[i]
                if not r:
                    break
                son[h][sym] = x["t"]
                o24 = deger_at(oser, x["t"]) if oser else None
                kume[h].append({"sym": sym, "t": b[i + 1]["t"],
                                "gun": b[i + 1]["t"] // 86400000, "kol": r,
                                "ab": (o24 is not None and o24 >= OI24_ESIK),
                                "oi_var": o24 is not None})
    return kume


# ------------------------------------------------------------------ istatistik
def gun_ort(ky, fn_):
    g = collections.defaultdict(list)
    for k in ky:
        v = fn_(k)
        if v is not None:
            g[k["gun"]].append(v)
    return {d: sum(v) / len(v) for d, v in g.items()}


def t_mde(g):
    v = list(g.values())
    n = len(v)
    if n < 3:
        return None, None, None, n
    m = sum(v) / n
    se = stx.stdev(v) / math.sqrt(n)
    return m, (m / se if se else None), (2.0 * se if se else None), n


def iki_ornek(ga, gb):
    a, b = list(ga.values()), list(gb.values())
    if len(a) < 3 or len(b) < 3:
        return None, None, None
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    se = math.sqrt(stx.variance(a) / len(a) + stx.variance(b) / len(b))
    return (ma - mb), ((ma - mb) / se if se else None), (2.0 * se if se else None)


def binom_ust(k, n, p=0.5):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def kol_tablo(ky):
    print("  %-6s %8s %9s %9s %8s %8s %7s" %
          ("kol", "stop%", "net%", "R", "stop-ol%", "hedef%", "saat"))
    for ad, _ in KOLLAR:
        print("  %-6s %8.2f %+9.3f %+9.4f %8.1f %8.1f %7.1f" % (
            ad,
            stx.mean([k["kol"][ad]["sp"] for k in ky]),
            stx.mean([k["kol"][ad]["net"] for k in ky]),
            stx.mean([k["kol"][ad]["R"] for k in ky]),
            sum(1 for k in ky if k["kol"][ad]["tip"] == "STOP") / len(ky) * 100,
            sum(1 for k in ky if k["kol"][ad]["tip"] == "HEDEF") / len(ky) * 100,
            stx.mean([k["kol"][ad]["saat"] for k in ky])))


def main():
    print("=" * 78)
    print("BOGA PENCERESI, TAZE VERIYLE — iki kapi birden")
    print("=" * 78)
    print("ON-KAYITLAR: boga_holdout 5144a45 · ma50_boga 42e6452 (ikisi de KOSMADAN once)")
    print("VERI: klines_1h_uzun + taze_1h · funding_gecmis + taze_funding (BELLEKTE)")
    print("🔑 radar_archive HIC KULLANILMIYOR -> hizalama kapisi GECERSIZ\n")

    kl, fn = yukle()
    en_son = max(b[-1]["t"] for b in kl.values())
    u = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
    print("sembol: %d · en gec bar: %s · 72s kesme: %s"
          % (len(kl), u(en_son), u(en_son - UFUK * 3600000)))
    sinama(kl, fn)
    oi = oi24_serisi()
    print("  oi24 serisi olan sembol (A+B alt kumesi icin): %d\n" % len(oi))

    kume = tara(kl, fn, oi)

    for ad in ("A_funding", "MA50", "K_dar", "K_genis"):
        ky = kume[ad]
        if not ky:
            continue
        print("### %s   N=%d · %d gun · %d sembol"
              % (ad, len(ky), len({k["gun"] for k in ky}), len({k["sym"] for k in ky})))
        kol_tablo(ky)
        print()

    # ---------------- A_funding: ON_KAYIT_boga_holdout olcutleri ----------------
    print("=" * 78)
    print("HUKUM 1 — A_funding · ON_KAYIT_boga_holdout.md bolum 7")
    print("=" * 78)
    ky = kume["A_funding"]
    if len(ky) < 40:
        print("N=%d yetersiz -> HUKUM YOK\n" % len(ky))
    else:
        s = {}
        print("  eslesmis fark (kol - A), olcu R:")
        print("  %-6s %10s %8s %8s %9s %9s" % ("kol", "ort", "t_gun", "MDE", "poz gun", "binom p"))
        for ad, m in KOLLAR:
            if m is None:
                continue
            g = gun_ort(ky, lambda k, v=ad: k["kol"][v]["R"] - k["kol"]["A"]["R"])
            mo, t, mde, n = t_mde(g)
            poz = sum(1 for v in g.values() if v > 0)
            p = binom_ust(poz, n) if n >= 3 else 1.0
            s[ad] = {"ort": mo, "t": t, "mde": mde, "n": n, "poz": poz, "p": p}
            print("  %-6s %+10.4f %+8.2f %8.4f   %2d/%-2d   %8.4f"
                  % (ad, mo, t or 0, mde or 0, poz, n, p))
        a = s[ADAY]
        K1 = a["p"] <= 0.05
        print("\nK1  gun bazinda isaret testi (tek yonlu binom p<=0.05)")
        print("    %s: %d/%d gun pozitif -> p=%.4f -> %s"
              % (ADAY, a["poz"], a["n"], a["p"], "GECTI" if K1 else "DUSTU"))
        K2 = a["ort"] is not None and a["ort"] > 0
        print("K2  ortalama fark > 0: %+.4f -> %s" % (a["ort"], "GECTI" if K2 else "DUSTU"))
        K3 = s[KOMSU]["ort"] is not None and s[KOMSU]["ort"] > 0
        print("K3  komsu %s > 0: %+.4f -> %s" % (KOMSU, s[KOMSU]["ort"], "GECTI" if K3 else "DUSTU"))
        ab = [k for k in ky if k["oi_var"] and k["ab"]]
        if len(ab) >= 10:
            g = gun_ort(ab, lambda k: k["kol"][ADAY]["R"] - k["kol"]["A"]["R"])
            abm, abt, _, abn = t_mde(g)
            K4 = abm is not None and abm >= 0
            print("K4  tam A+B (N=%d, %d gun) isaret ters DEGIL: %+.4f (t %+.2f) -> %s"
                  % (len(ab), abn, abm, abt or 0, "GECTI" if K4 else "DUSTU"))
        else:
            K4 = True
            print("K4  tam A+B: N=%d < 10 -> degerlendirilmedi (GECTI sayilir)" % len(ab))
        # ON-KAYIT bolum 7 METNI: GECTI = K1+K2+K3+K4 · ZAYIF = "K2+K3 var, K1 DUSTU"
        #   · aksi DUSTU.  [DUZELTME 2026-09-05] Ilk surum, K1 GECIP K4 dustugunde
        #   "ZAYIF (K1 dustu)" basiyordu: hem etiket yanlisti hem de on-kaydin
        #   ZAYIF tanimi bu bilesimi KAPSAMIYOR -> dogru kategori DUSTU.
        #   Hata LEHE yondeydi; kriter metni yorumlanmaz, harfiyen uygulanir (D/9).
        dusen = [ad for ad, v in (("K1", K1), ("K2", K2), ("K3", K3), ("K4", K4)) if not v]
        if not dusen:
            h = "GECTI"
        elif K2 and K3 and not K1:
            h = "ZAYIF (K1 dustu)"
        else:
            h = "DUSTU (dusen: %s)" % ", ".join(dusen)
        print("\nSONUC 1: %s\n" % h)

    # ---------------- MA50: ON_KAYIT_ma50_boga olcutleri ----------------
    print("=" * 78)
    print("HUKUM 2 — MA50+ucuz · ON_KAYIT_ma50_boga.md bolum 8")
    print("=" * 78)
    km, kd, kg = kume["MA50"], kume["K_dar"], kume["K_genis"]
    if len(km) < 40:
        print("N=%d yetersiz -> HUKUM YOK" % len(km))
    else:
        gk = gun_ort(km, lambda k: k["kol"]["A"]["net"])
        gd = gun_ort(kd, lambda k: k["kol"]["A"]["net"])
        gg = gun_ort(kg, lambda k: k["kol"]["A"]["net"])
        f1, t1, m1 = iki_ornek(gk, gd)
        K1 = f1 is not None and f1 > 0 and t1 is not None and t1 >= 2.0
        print("K1  kapi - K_dar (net%%): %+.4f  t %+.2f  MDE %.4f -> %s"
              % (f1, t1 or 0, m1 or 0, "GECTI" if K1 else "DUSTU"))
        mk, tk, _, nk = t_mde(gk)
        K2 = mk is not None and mk > 0
        # 🔴 IKI ORTALAMA AYRISABILIR: gun-ortalamasi gunleri esit tartar,
        #    islem-ortalamasi cok islemli gunleri agir tartar. ISARETLERI TERS
        #    cikarsa hukum kirilgandir -> IKISI DE basilir, gizlenmez.
        islem_ort = stx.mean([k["kol"]["A"]["net"] for k in km])
        print("K2  kapinin MUTLAK net%%: gun-ort %+.4f  t %+.2f  (%d gun) -> %s"
              % (mk, tk or 0, nk, "GECTI" if K2 else "DUSTU"))
        print("      islem-ort %+.4f   -> isaretler %s"
              % (islem_ort, "AYNI" if islem_ort * mk > 0 else "TERS (K2 KIRILGAN)"))
        f3, t3, _ = iki_ornek(gk, gg)
        K3 = f1 is not None and f3 is not None and f1 * f3 > 0
        print("K3  kapi - K_genis: %+.4f  t %+.2f -> %s" % (f3, t3 or 0, "GECTI" if K3 else "DUSTU"))
        K4 = f1 is not None and m1 is not None and abs(f1) >= m1
        print("K4  guc |fark| >= MDE: %.4f vs %.4f -> %s"
              % (abs(f1), m1, "GORULUR" if K4 else "GOREMIYORUZ"))
        h2 = ("GECTI" if (K1 and K2 and K3 and K4)
              else ("AYIRIYOR AMA KAZANDIRMIYOR" if (K1 and K3) else "DUSTU"))
        print("\nSONUC 2: %s" % h2)
        print("\n  MA50'de stop genisligi (BETIMLEYICI, olcut YOK):")
        for ad, m in KOLLAR:
            if m is None:
                continue
            g = gun_ort(km, lambda k, v=ad: k["kol"][v]["R"] - k["kol"]["A"]["R"])
            mo, t, mde, n = t_mde(g)
            print("    %-6s %+9.4f  t %+6.2f  MDE %7.4f" % (ad, mo, t or 0, mde or 0))

    print("\nVeri: BELLEKTE birlestirildi · hicbir arsive YAZILMADI")
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
