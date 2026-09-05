#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MA50+UCUZ KAPISI, BOGA PENCERESINDE — hala calisiyor mu? (2026-09-05)

ON-KAYIT: ON_KAYIT_ma50_boga.md, commit 42e6452 — KOSTURULMADAN ONCE.
Bu betik o on-kaydi UYGULAR; olcut/esik degistirmez, esik TARAMAZ.

BIRINCIL SORU: kapi bu bogada hala kar eden SHORT'lar seciyor mu?
  (stop genisligi burada IKINCIL ve BETIMLEYICI — gecme olcutu YOK)

KAPI: fiyat <= $0,07 VE ma50_mesafe >= %3,72  -> ikisi de YALNIZCA MUMDAN.
  Arsive ihtiyac yok -> dongu-damgasi hizalama sorunu GECERSIZ.
  Arsiv yalniz FONLAMA MALIYETI icin; S2 sinamasi onu dogrular.

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

# --- ON-KAYITLI PARAMETRELER (config'ten, TARANMAZ) ---
UCUZ_FIYAT, MA50_MESAFE = 0.07, 3.72
PUMP, MIN_VOL = 20.0, 3_000_000
HEDEF_PCT, UFUK = 10.0, 72
ASGARI_STOP = 2.0
ISINMA, SOGUMA_SAAT = 220, 24
OFSET_SAAT = -3
BOGA_BAS = "2026-08-21"
KOLLAR = [("A", None), ("1.5x", 1.5), ("2.5x", 2.5), ("4.0x", 4.0)]
S2_ESIK = 0.005                      # fonlama orani dongu-ici kararlilik esigi


# ------------------------------------------------------------------ veri
def saatlik(b5):
    g = collections.OrderedDict()
    for x in b5:
        s = (x["t"] // 3600000) * 3600000
        d = g.get(s)
        if d is None:
            g[s] = {"t": s, "o": x["o"], "h": x["h"], "l": x["l"], "c": x["c"],
                    "qv": x.get("qv") or 0.0}
        else:
            d["h"] = max(d["h"], x["h"])
            d["l"] = min(d["l"], x["l"])
            d["c"] = x["c"]
            d["qv"] += x.get("qv") or 0.0
    return [v for _, v in sorted(g.items())]


def yukle():
    kl, ham5 = {}, {}
    for f in sorted(os.listdir(PERP)):
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
            kl[sym] = b
            ham5[sym] = j
    return kl, ham5


def utc_ms(s):
    d = dt.datetime.strptime(s[:16], "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)
    return int((d + dt.timedelta(hours=OFSET_SAAT)).timestamp() * 1000)


def fonlama_serileri(kl):
    """{sym: [(t_ms, oran)]} + dongu-ici kararlilik orneklemi (S2)."""
    fon = collections.defaultdict(list)
    with open(ARSIV, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            ts, sym, fd = r.get("ts"), r.get("sym"), r.get("funding")
            if not ts or sym not in kl or fd is None:
                continue
            try:
                fon[sym].append((utc_ms(ts), fd))
            except Exception:
                continue
    for s in fon:
        fon[s].sort()
    return fon


# ------------------------------------------------------------------ sinama
def sinama(kl, ham5, fon):
    """S1 merdiven · S2 fonlama kararliligi · S3 toplama dogrulugu.
    S1/S3 duserse REDDEDER. S2 duserse fonlama HARIC kosar (on-kayit bolum 6)."""
    hata, fonlama_kullan = [], True

    # S1 — merdiven monotonlugu
    b = [{"t": i * 3600000, "o": 100.0, "h": 100.0 + (i % 7),
          "l": 100.0 - (i % 5), "c": 100.0 + (i % 3)} for i in range(300)]
    atrs = ir.atr_serisi(b)
    for si in (250, 270):
        ref, a = b[si + 1]["o"], atrs[si]
        sA = ir.stop_hesapla(b, si, ref, a)
        for ad, m in KOLLAR:
            if m is not None and sA > ref + m * a + 1e-9:
                hata.append("S1 MERDIVEN BOZUK si=%d kol=%s" % (si, ad))

    # S3 — 1 saate toplama dogrulugu (h/l uclari korunmali)
    ihlal = 0
    for sym in list(ham5)[:20]:
        j, b1 = ham5[sym], kl[sym]
        grup = collections.defaultdict(list)
        for x in j:
            grup[(x["t"] // 3600000) * 3600000].append(x)
        for bar in b1[-50:]:
            g = grup.get(bar["t"])
            if not g:
                continue
            if abs(bar["h"] - max(x["h"] for x in g)) > 1e-12:
                ihlal += 1
            if abs(bar["l"] - min(x["l"] for x in g)) > 1e-12:
                ihlal += 1
    if ihlal:
        hata.append("S3 TOPLAMA BOZUK: %d ihlal" % ihlal)
    else:
        print("  S3 toplama dogrulugu: GECTI (h/l uclari korunuyor)")

    # S2 — fonlama oraninin dongu-ici kararliligi
    dlt = []
    for sym, seri in list(fon.items()):
        for i in range(1, min(len(seri), 400)):
            if seri[i][0] - seri[i - 1][0] <= 15 * 60000:
                dlt.append(abs(seri[i][1] - seri[i - 1][1]))
        if len(dlt) > 40000:
            break
    if dlt:
        med = stx.median(dlt)
        print("  S2 fonlama dongu-ici |delta| medyani: %.6f  (esik %.4f)" % (med, S2_ESIK))
        if med > S2_ESIK:
            fonlama_kullan = False
            print("     -> S2 DUSTU: fonlama HARIC kosulacak (on-kayit bolum 6)")
        else:
            print("     -> S2 GECTI: damga bulanikligi fonlamayi bozmuyor")
    else:
        fonlama_kullan = False
        print("  S2 orneklem YOK -> fonlama HARIC")

    if hata:
        print("\nSINAMA DUSTU — betik calismayi REDDEDIYOR:")
        for h in hata:
            print("  - " + h)
        raise SystemExit(1)
    print("  S1 merdiven: GECTI\n")
    return fonlama_kullan


# ------------------------------------------------------------------ mekanik
def fonlama(seri, bas_ms, son_ms):
    if not seri:
        return 0.0
    top, adim = 0.0, 8 * 3600000
    t = ((bas_ms // adim) + 1) * adim
    while t <= son_ms:
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


def islem(b, atrs, si, seri, fon_kullan):
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
        f = fonlama(seri, b[gi]["t"], b[j]["t"]) if fon_kullan else 0.0
        net = ham - oo.MALIYET + f
        out[ad] = {"net": net, "R": net / sp, "tip": tip, "sp": sp,
                   "saat": j - gi, "fon": f}
    return out


# ------------------------------------------------------------------ tarama
def tara(kl, fon, fon_kullan):
    bas = int(dt.datetime.strptime(BOGA_BAS, "%Y-%m-%d")
              .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    en_son = max(b[-1]["t"] for b in kl.values())
    kesme = en_son - UFUK * 3600000
    kume = {"KAPI": [], "K_dar": [], "K_genis": []}
    son_olay = {k: {} for k in kume}
    for sym, b in kl.items():
        atrs = ir.atr_serisi(b)
        ma50 = ir.ma_serisi(b, 50)
        seri = fon.get(sym, [])
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
            ucuz = x["c"] <= UCUZ_FIYAT
            uzak = bool(ma50[i]) and ma50[i] > 0 and \
                (x["c"] / ma50[i] - 1) * 100 >= MA50_MESAFE
            hedefler = ["K_genis"]
            if ucuz and uzak:
                hedefler.append("KAPI")
            elif ucuz:
                hedefler.append("K_dar")
            r = None
            for h in hedefler:
                s0 = son_olay[h].get(sym)
                if s0 is not None and x["t"] - s0 < SOGUMA_SAAT * 3600000:
                    continue
                if r is None:
                    r = islem(b, atrs, i, seri, fon_kullan)
                    if not r:
                        break
                son_olay[h][sym] = x["t"]
                kume[h].append({"sym": sym, "t": b[i + 1]["t"],
                                "gun": b[i + 1]["t"] // 86400000, "kol": r})
    return kume


# ------------------------------------------------------------------ istatistik
def gun_ort(ky, fn):
    g = collections.defaultdict(list)
    for k in ky:
        v = fn(k)
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
    """Iki AYRIK grubun gun ortalamalari -> (fark, t, MDE)"""
    a, b = list(ga.values()), list(gb.values())
    if len(a) < 3 or len(b) < 3:
        return None, None, None
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    se = math.sqrt(stx.variance(a) / len(a) + stx.variance(b) / len(b))
    return (ma - mb), ((ma - mb) / se if se else None), (2.0 * se if se else None)


def tablo(ky, ad):
    gun = len({k["gun"] for k in ky})
    print("  %-9s N=%-5d gun=%-3d sembol=%-4d  net%% %+7.3f   R %+8.4f   stop-ol %%%.0f  hedef %%%.0f"
          % (ad, len(ky), gun, len({k["sym"] for k in ky}),
             stx.mean([k["kol"]["A"]["net"] for k in ky]),
             stx.mean([k["kol"]["A"]["R"] for k in ky]),
             sum(1 for k in ky if k["kol"]["A"]["tip"] == "STOP") / len(ky) * 100,
             sum(1 for k in ky if k["kol"]["A"]["tip"] == "HEDEF") / len(ky) * 100))


def main():
    print("=" * 78)
    print("MA50+UCUZ KAPISI, BOGA PENCERESINDE — hala calisiyor mu?")
    print("=" * 78)
    print("ON-KAYIT: ON_KAYIT_ma50_boga.md commit 42e6452 — KOSMADAN once")
    print("BIRINCIL: kapinin KENDISI (stop genisligi ikincil/betimleyici)")
    print("Olcu: net%% birincil · R ikincil · pencere %s ->\n" % BOGA_BAS)

    kl, ham5 = yukle()
    print("perp_seri sembol (1sa): %d" % len(kl))
    fon = fonlama_serileri(kl)
    print("fonlama serisi olan sembol: %d\n" % len(fon))
    fon_kullan = sinama(kl, ham5, fon)

    kume = tara(kl, fon, fon_kullan)
    print("### Kollar (botun mevcut A-stopu ile)")
    for ad in ("KAPI", "K_dar", "K_genis"):
        if kume[ad]:
            tablo(kume[ad], ad)
    print()
    if fon_kullan:
        print("  fonlama DAHIL (islem basi ort: %+.4f puan)"
              % stx.mean([k["kol"]["A"]["fon"] for k in kume["KAPI"]]))
    else:
        print("  ⚠ fonlama HARIC (S2 dustu)")
    print()

    if len(kume["KAPI"]) < 40:
        print("KAPI kolu yetersiz -> HUKUM YOK")
        return

    gk = gun_ort(kume["KAPI"], lambda k: k["kol"]["A"]["net"])
    gd = gun_ort(kume["K_dar"], lambda k: k["kol"]["A"]["net"])
    gg = gun_ort(kume["K_genis"], lambda k: k["kol"]["A"]["net"])

    print("=" * 78)
    print("HUKUM — ON_KAYIT_ma50_boga.md bolum 8")
    print("=" * 78)
    f1, t1, m1 = iki_ornek(gk, gd)
    K1 = (f1 is not None and f1 > 0 and t1 is not None and t1 >= 2.0)
    print("K1  kapi - K_dar (net%%): %+.4f   t_gun %+.2f   MDE %.4f  -> %s"
          % (f1, t1 if t1 else 0, m1 if m1 else 0, "GECTI" if K1 else "DUSTU"))
    mk, tk, mdk, nk = t_mde(gk)
    K2 = mk is not None and mk > 0
    print("K2  kapinin MUTLAK net%%: %+.4f   t_gun %+.2f   (%d gun) -> %s"
          % (mk, tk if tk else 0, nk, "GECTI" if K2 else "DUSTU"))
    f3, t3, m3 = iki_ornek(gk, gg)
    K3 = (f1 is not None and f3 is not None and f1 * f3 > 0)
    print("K3  kapi - K_genis (net%%): %+.4f   t_gun %+.2f  -> %s"
          % (f3, t3 if t3 else 0, "GECTI" if K3 else "DUSTU"))
    K4 = (f1 is not None and m1 is not None and abs(f1) >= m1)
    print("K4  guc |fark| >= MDE: %.4f vs %.4f -> %s"
          % (abs(f1), m1, "GORULUR" if K4 else "GOREMIYORUZ"))
    if K1 and K2 and K3 and K4:
        h = "GECTI"
    elif K1 and K3 and not K2:
        h = "AYIRIYOR AMA KAZANDIRMIYOR"
    else:
        h = "DUSTU"
    print("\nSONUC: %s" % h)

    print("\n" + "=" * 78)
    print("IKINCIL — R olcusu (ayni kollar)")
    print("=" * 78)
    rk = gun_ort(kume["KAPI"], lambda k: k["kol"]["A"]["R"])
    rd = gun_ort(kume["K_dar"], lambda k: k["kol"]["A"]["R"])
    fr, tr, mr = iki_ornek(rk, rd)
    mrk, trk, _, _ = t_mde(rk)
    print("  kapi mutlak R %+.4f (t %+.2f) · kapi-K_dar %+.4f (t %+.2f, MDE %.4f)"
          % (mrk, trk if trk else 0, fr, tr if tr else 0, mr if mr else 0))

    print("\n" + "=" * 78)
    print("IKINCIL/BETIMLEYICI — stop genisligi (GECME OLCUTU YOK)")
    print("=" * 78)
    ky = kume["KAPI"]
    print("  %-6s %8s %9s %9s %8s %8s" % ("kol", "stop%", "net%", "R", "stop-ol%", "hedef%"))
    for ad, _ in KOLLAR:
        print("  %-6s %8.2f %+9.3f %+9.4f %8.1f %8.1f" % (
            ad,
            stx.mean([k["kol"][ad]["sp"] for k in ky]),
            stx.mean([k["kol"][ad]["net"] for k in ky]),
            stx.mean([k["kol"][ad]["R"] for k in ky]),
            sum(1 for k in ky if k["kol"][ad]["tip"] == "STOP") / len(ky) * 100,
            sum(1 for k in ky if k["kol"][ad]["tip"] == "HEDEF") / len(ky) * 100))
    print("  eslesmis fark (kol - A), R:")
    for ad, m in KOLLAR:
        if m is None:
            continue
        g = gun_ort(ky, lambda k, v=ad: k["kol"][v]["R"] - k["kol"]["A"]["R"])
        mo, t, mde, n = t_mde(g)
        print("    %-6s %+9.4f  t %+6.2f  MDE %7.4f  (%d gun)"
              % (ad, mo, t if t else 0, mde if mde else 0, n))

    print("\nVeri indirme: YOK · Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
