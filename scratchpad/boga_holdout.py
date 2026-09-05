#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOGA HOLDOUT — genis stop TAZE veride de tutuyor mu? (2026-09-05)

ON-KAYIT: ON_KAYIT_boga_holdout.md, commit 5144a45 — KOSTURULMADAN ONCE.
Bu betik o on-kaydi UYGULAR; olcut/olcu/kol degistirmez, esik taramaz.

KAYNAK: perp_seri 5dk klineler (1 saate toplanir) + radar_archive (kapi + fonlama).
  Bu, hipotezin dogdugu klines_1h_uzun'dan FARKLI bir kaynak ve 08-25..09-02
  hic gorulmedi -> GERCEK HOLDOUT.

BIRINCIL OLCUT K1 = GUN BAZINDA ISARET TESTI (tek yonlu binom).
  Ortalama farkin t'si RAPORLANIR ama olcut DEGILDIR (N yetersiz, on-kayit bolum 4).

ZORUNLU SINAMA: zaman ofseti kanitlanmadan kosulmaz (bkz. sinama()).
Salt-okunur. Veri indirme YOK. radar_archive context'e yuklenmez.
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
KOK = os.path.dirname(BURA)
PERP = os.path.join(BURA, "perp_seri")
ARSIV = os.path.join(KOK, "radar_archive.jsonl")

# --- ON-KAYITLI PARAMETRELER (degistirilmez) ---
FUND_ESIK, OI24_ESIK = -0.05, 10.0
HEDEF_PCT, UFUK = 10.0, 72
ASGARI_STOP = 2.0
ISINMA = 220
SOGUMA_SAAT = 24
OFSET_SAAT = -3
BOGA_BAS = "2026-08-21"
KOLLAR = [("A", None), ("1.5x", 1.5), ("2.5x", 2.5), ("4.0x", 4.0)]
ADAY = "2.5x"                 # 2 yillik BOGA'da en iyi olan — ARANMIYOR, SINANIYOR
KOMSU = "4.0x"


# ------------------------------------------------------------------ veri
def saatlik(bes_dk):
    """5 dakikalik barlari 1 SAATLIK bara toplar. o=ilk · h=maks · l=min · c=son."""
    grup = collections.OrderedDict()
    for x in bes_dk:
        s = (x["t"] // 3600000) * 3600000
        g = grup.get(s)
        if g is None:
            grup[s] = {"t": s, "o": x["o"], "h": x["h"], "l": x["l"], "c": x["c"],
                       "qv": x.get("qv") or 0.0, "n": 1}
        else:
            g["h"] = max(g["h"], x["h"])
            g["l"] = min(g["l"], x["l"])
            g["c"] = x["c"]
            g["qv"] += x.get("qv") or 0.0
            g["n"] += 1
    return [v for _, v in sorted(grup.items())]


def klineler_yukle():
    """-> (saatlik, bes_dk)  — 5dk seri SINAMA icin saklanir (last1 dogrulamasi)."""
    out, ham5 = {}, {}
    for f in os.listdir(PERP):
        if not f.endswith("_kline.json"):
            continue
        sym = f[:-11]
        try:
            j = json.load(open(os.path.join(PERP, f), encoding="utf-8"))
        except Exception:
            continue
        if not j:
            continue
        b = saatlik(j)
        if len(b) >= ISINMA + 10:
            out[sym] = b
            ham5[sym] = [(x["t"], x["c"]) for x in j]
    return out, ham5


def utc_ms(s):
    d = dt.datetime.strptime(s[:16], "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)
    return int((d + dt.timedelta(hours=OFSET_SAAT)).timestamp() * 1000)


def utc_ms_ofset(s, ofset):
    d = dt.datetime.strptime(s[:16], "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)
    return int((d + dt.timedelta(hours=ofset)).timestamp() * 1000)


def arsiv_oku(kl):
    """-> (tetikler, fonlama_serisi)
    tetik = {sym, t(UTC ms, bar basi), ab(bool)}
    fonlama_serisi = {sym: [(t_ms, oran), ...]}  (siralanmis)
    """
    ham = []
    fon = collections.defaultdict(list)
    last1 = []                                   # sinama icin (ts_str, sym, last1)
    with open(ARSIV, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            ts, sym = r.get("ts"), r.get("sym")
            if not ts or not sym or sym not in kl:
                continue
            fd = r.get("funding")
            if fd is None:
                continue
            try:
                t = utc_ms(ts)
            except Exception:
                continue
            fon[sym].append((t, fd))
            if len(last1) < 60000 and r.get("last1") is not None:
                last1.append((ts, sym, r["last1"]))
            if t < utc_ms(BOGA_BAS + " 00:00"):
                continue
            if fd <= FUND_ESIK:
                ab = (r.get("oi24") is not None and r["oi24"] >= OI24_ESIK)
                ham.append((t, sym, ab))
    for s in fon:
        fon[s].sort()
    return ham, fon, last1


# ------------------------------------------------------------------ sinama
def sinama(kl, ham5, last1):
    """Zaman ofseti KANITLANMADAN kosulmaz. Duserse SystemExit(1)."""
    hata = []
    # 1) merdiven monotonlugu (stop_mesafesi.sinama ile ayni ilke)
    b = [{"t": i * 3600000, "o": 100.0, "h": 100.0 + (i % 7),
          "l": 100.0 - (i % 5), "c": 100.0 + (i % 3)} for i in range(300)]
    atrs = ir.atr_serisi(b)
    for si in (250, 270):
        ref, a = b[si + 1]["o"], atrs[si]
        sA = ir.stop_hesapla(b, si, ref, a)
        for ad, m in KOLLAR:
            if m is not None and sA > ref + m * a + 1e-9:
                hata.append("MERDIVEN BOZUK si=%d kol=%s" % (si, ad))

    # 2) ZAMAN OFSETI — arsivin last1'i ile 5 DAKIKALIK izgarada hesaplanan
    #    gercek "anlik goruntu anindan geriye 60 dakika" getirisi.
    #    [DEGISTI 2026-09-05] Ilk surum SAATLIK bar kapanis getirisini kullaniyordu;
    #    arsiv anlik goruntusu saatin ORTASINDA alindigi icin bu yanlis buyuklugu
    #    olcuyordu (korelasyon 0,511). Esik 0,80 DEGISMEDI, sinama duzeltildi.
    print("  zaman ofseti sinamasi (arsiv last1 vs radar.py:117 tanimi (son saat kapanisindan bu yana)):")

    def kapanis(seri, hedef_ms, tolerans_ms=300000):
        """hedef_ms'e en yakin 5dk kapanisi (tolerans icinde) -> float | None"""
        lo, hi, en = 0, len(seri) - 1, None
        while lo <= hi:
            mid = (lo + hi) // 2
            if seri[mid][0] <= hedef_ms:
                en = seri[mid]
                lo = mid + 1
            else:
                hi = mid - 1
        if en is None or hedef_ms - en[0] > tolerans_ms:
            return None
        return en[1]

    en_iyi, skorlar = None, {}
    for ofs in (-4, -3, -2):
        cift = []
        for ts, sym, l1 in last1:
            seri = ham5.get(sym)
            if not seri:
                continue
            try:
                t = utc_ms_ofset(ts, ofs)
            except Exception:
                continue
            # radar.py:117 -> last1 = (canli fiyat - SON KAPANMIS saatlik barin
            # kapanisi) / o kapanis. Son kapanmis barin kapanisi = saat sinirindaki
            # fiyat = (H - 5dk) damgali 5dk barin kapanisi.  KAYAN 60dk DEGIL.
            H = (t // 3600000) * 3600000
            simdi = kapanis(seri, t)
            once = kapanis(seri, H - 300000)
            if simdi is None or once is None or once <= 0:
                continue
            cift.append((l1, (simdi / once - 1) * 100))
            if len(cift) >= 4000:
                break
        if len(cift) < 200:
            skorlar[ofs] = None
            print("    ofset %+d : yetersiz eslesme (%d)" % (ofs, len(cift)))
            continue
        xs = [c[0] for c in cift]
        ys = [c[1] for c in cift]
        mx, my = stx.mean(xs), stx.mean(ys)
        pay = sum((x - mx) * (y - my) for x, y in cift)
        px = math.sqrt(sum((x - mx) ** 2 for x in xs))
        py = math.sqrt(sum((y - my) ** 2 for y in ys))
        r = pay / (px * py) if px and py else 0.0
        skorlar[ofs] = r
        print("    ofset %+d : korelasyon %+.3f  (N=%d)" % (ofs, r, len(cift)))
        if en_iyi is None or r > skorlar[en_iyi]:
            en_iyi = ofs
    if en_iyi != OFSET_SAAT:
        hata.append("OFSET YANLIS: en iyi %s, kullanilan %s" % (en_iyi, OFSET_SAAT))
    elif skorlar.get(OFSET_SAAT) is None or skorlar[OFSET_SAAT] < 0.80:
        hata.append("OFSET KORELASYONU DUSUK: %.3f < 0.80" % (skorlar.get(OFSET_SAAT) or -1))

    if hata:
        print("\nSINAMA DUSTU — betik calismayi REDDEDIYOR:")
        for h in hata:
            print("  - " + h)
        raise SystemExit(1)
    print("  sinama: GECTI\n")


# ------------------------------------------------------------------ mekanik
def fonlama_maliyeti(seri, bas_ms, son_ms):
    """8 saatlik odeme anlarinda (00/08/16 UTC) arsivin gozledigi orani topla.
    SHORT icin katki = +oran (oran negatifse ODERSIN)."""
    if not seri:
        return 0.0
    top = 0.0
    adim = 8 * 3600000
    ilk = ((bas_ms // adim) + 1) * adim
    t = ilk
    while t <= son_ms:
        # o ana en yakin arsiv kaydi
        lo, hi, en = 0, len(seri) - 1, None
        while lo <= hi:
            mid = (lo + hi) // 2
            if seri[mid][0] <= t:
                en = seri[mid]
                lo = mid + 1
            else:
                hi = mid - 1
        if en is not None and abs(en[0] - t) <= 6 * 3600000:
            top += en[1]
        t += adim
    return top


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


def islem(b, si, seri):
    gi = si + 1
    if si < ISINMA or gi >= len(b):
        return None
    a = ir.atr_serisi(b[:si + 1])[si] if si < len(b) else None
    if not a or a <= 0:
        return None
    ref = b[gi]["o"]
    if ref <= 0:
        return None
    son = min(gi + UFUK, len(b))
    if son - gi < 4:
        return None
    sA = ir.stop_hesapla(b, si, ref, a)
    spA = (sA - ref) / ref * 100
    if spA <= 0 or spA < ASGARI_STOP:
        return None
    out = {}
    hedef = ref * (1 - HEDEF_PCT / 100)
    for ad, m in KOLLAR:
        s = sA if m is None else ref + m * a
        sp = (s - ref) / ref * 100
        if sp <= 0:
            return None
        ham, tip, j = yol(b, gi, son, ref, s, hedef)
        fon = fonlama_maliyeti(seri, b[gi]["t"], b[j]["t"])
        net = ham - oo.MALIYET + fon
        out[ad] = {"net": net, "R": net / sp, "tip": tip, "sp": sp, "saat": j - gi}
    return out


# ------------------------------------------------------------------ istatistik
def binom_ust(k, n, p=0.5):
    """P(X >= k) — tek yonlu."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def gun_farklari(kayitlar, kol, alan="R"):
    g = collections.defaultdict(list)
    for k in kayitlar:
        g[k["gun"]].append(k["kol"][kol][alan] - k["kol"]["A"][alan])
    return {d: sum(v) / len(v) for d, v in g.items()}


def t_mde(gunler):
    v = list(gunler.values())
    n = len(v)
    if n < 3:
        return None, None, None, n
    m = sum(v) / n
    se = stx.stdev(v) / math.sqrt(n)
    return m, (m / se if se else None), (2.0 * se if se else None), n


# ------------------------------------------------------------------ ana
def main():
    print("=" * 78)
    print("BOGA HOLDOUT — genis stop TAZE veride de tutuyor mu?")
    print("=" * 78)
    print("ON-KAYIT: ON_KAYIT_boga_holdout.md commit 5144a45 — KOSMADAN once")
    print("Kaynak: perp_seri 5dk -> 1sa  +  radar_archive (kapi + fonlama)")
    print("BIRINCIL OLCUT: GUN BAZINDA ISARET TESTI (tek yonlu binom)")
    print("Aday kol: %s (2 yillik BOGA'da en iyi) — ARANMIYOR, SINANIYOR\n" % ADAY)

    kl, ham5 = klineler_yukle()
    print("perp_seri kline (1sa'e toplanmis) sembol: %d" % len(kl))
    ham, fon, last1 = arsiv_oku(kl)
    print("arsiv tetigi (ham): %d · fonlama serisi olan sembol: %d\n" % (len(ham), len(fon)))

    sinama(kl, ham5, last1)

    # --- bagimsiz olaylar (24 saat soguma) ---
    ham.sort()
    son_olay, olaylar = {}, []
    for t, sym, ab in ham:
        s0 = son_olay.get(sym)
        if s0 is not None and t - s0 < SOGUMA_SAAT * 3600000:
            continue
        son_olay[sym] = t
        olaylar.append((t, sym, ab))

    kayit = []
    b_index = {}
    for t, sym, ab in olaylar:
        b = kl[sym]
        if sym not in b_index:
            b_index[sym] = {x["t"]: i for i, x in enumerate(b)}
        s = (t // 3600000) * 3600000
        si = b_index[sym].get(s)
        if si is None:
            continue
        r = islem(b, si, fon.get(sym, []))
        if not r:
            continue
        kayit.append({"sym": sym, "t": b[si + 1]["t"], "ab": ab,
                      "gun": b[si + 1]["t"] // 86400000, "kol": r})

    if not kayit:
        print("HIC ISLEM URETILEMEDI -> hukum YOK")
        return

    gun = sorted({k["gun"] for k in kayit})
    print("### A_funding · BOGA holdout")
    print("    N=%d islem · %d gun · %d sembol   (A+B alt kumesi N=%d)"
          % (len(kayit), len(gun), len({k["sym"] for k in kayit}),
             sum(1 for k in kayit if k["ab"])))
    print()
    print("  %-6s %8s %9s %9s %8s %8s %7s" %
          ("kol", "stop%", "net%", "R", "stop-ol%", "hedef%", "saat"))
    for ad, _ in KOLLAR:
        print("  %-6s %8.2f %+9.3f %+9.4f %8.1f %8.1f %7.1f" % (
            ad,
            stx.mean([k["kol"][ad]["sp"] for k in kayit]),
            stx.mean([k["kol"][ad]["net"] for k in kayit]),
            stx.mean([k["kol"][ad]["R"] for k in kayit]),
            sum(1 for k in kayit if k["kol"][ad]["tip"] == "STOP") / len(kayit) * 100,
            sum(1 for k in kayit if k["kol"][ad]["tip"] == "HEDEF") / len(kayit) * 100,
            stx.mean([k["kol"][ad]["saat"] for k in kayit])))
    print()

    print("  eslesmis fark (kol - A), olcu R:")
    print("  %-6s %10s %8s %8s %9s %s" % ("kol", "ort fark", "t_gun", "MDE", "poz gun", "binom p"))
    sonuc = {}
    for ad, m in KOLLAR:
        if m is None:
            continue
        g = gun_farklari(kayit, ad, "R")
        mo, t, mde, n = t_mde(g)
        poz = sum(1 for v in g.values() if v > 0)
        p = binom_ust(poz, n) if n >= 3 else None
        sonuc[ad] = {"ort": mo, "t": t, "mde": mde, "n": n, "poz": poz, "p": p}
        print("  %-6s %+10.4f %+8.2f %8.4f   %2d/%-2d   %.4f"
              % (ad, mo, t if t else 0, mde if mde else 0, poz, n, p if p else 1))
    print()

    print("  ikincil olcu net%:")
    for ad, m in KOLLAR:
        if m is None:
            continue
        g = gun_farklari(kayit, ad, "net")
        mo, t, mde, n = t_mde(g)
        poz = sum(1 for v in g.values() if v > 0)
        print("  %-6s %+10.4f  t %+6.2f  MDE %7.4f  poz gun %2d/%-2d"
              % (ad, mo, t if t else 0, mde if mde else 0, poz, n))
    print()

    # --- A+B alt kumesi (K4) ---
    ab = [k for k in kayit if k["ab"]]
    print("  TAM A+B KAPISI (funding <= %.2f VE oi24 >= %.0f) — N=%d:"
          % (FUND_ESIK, OI24_ESIK, len(ab)))
    ab_ort = None
    if len(ab) >= 10:
        g = gun_farklari(ab, ADAY, "R")
        ab_ort, abt, abmde, abn = t_mde(g)
        abpoz = sum(1 for v in g.values() if v > 0)
        print("    %s fark %+.4f  t %+.2f  MDE %.4f  poz gun %d/%d"
              % (ADAY, ab_ort, abt if abt else 0, abmde if abmde else 0, abpoz, abn))
    else:
        print("    N<10 -> sayi verilmez")
    print()

    # --- HUKUM ---
    print("=" * 78)
    print("HUKUM — ON_KAYIT_boga_holdout.md bolum 7")
    print("=" * 78)
    s = sonuc[ADAY]
    K1 = s["p"] is not None and s["p"] <= 0.05
    print("K1  gun bazinda isaret testi (tek yonlu binom p <= 0.05)")
    print("    %s: %d/%d gun pozitif  ->  p = %.4f  ->  %s"
          % (ADAY, s["poz"], s["n"], s["p"] if s["p"] else 1, "GECTI" if K1 else "DUSTU"))
    K2 = s["ort"] is not None and s["ort"] > 0
    print("K2  ortalama fark > 0: %+.4f -> %s" % (s["ort"], "GECTI" if K2 else "DUSTU"))
    k = sonuc[KOMSU]
    K3 = k["ort"] is not None and k["ort"] > 0
    print("K3  komsu kol %s > 0: %+.4f -> %s" % (KOMSU, k["ort"], "GECTI" if K3 else "DUSTU"))
    K4 = (ab_ort is None) or (ab_ort >= 0)
    print("K4  tam A+B alt kumesinde isaret ters DEGIL: %s -> %s"
          % (("%+.4f" % ab_ort) if ab_ort is not None else "N<10, degerlendirilmedi",
             "GECTI" if K4 else "DUSTU"))
    if K1 and K2 and K3 and K4:
        h = "GECTI"
    elif K2 and K3:
        h = "ZAYIF (K1 dustu — guc yetersizdi, on-kayit bolum 4)"
    else:
        h = "DUSTU"
    print("\nSONUC: %s" % h)
    print()
    print("MDE hatirlatmasi: ortalama farkin t'si OLCUT DEGILDIR (N=%d gun)." % s["n"])
    print("Veri indirme: YOK · Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
