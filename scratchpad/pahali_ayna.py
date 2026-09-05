#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UCUZ yerine PAHALI — fiyat seviyesinin isareti rejimle donuyor mu? (2026-09-05)

ON-KAYIT: ON_KAYIT_pahali_ayna.md, commit 5f213c2 — KOSTURULMADAN ONCE.
Bu betik o on-kaydi UYGULAR; esik TARAMAZ, olcut degistirmez.

BIRINCIL: 2 YILLIK BOGA dilimi (13 gunluk pencereye cok bakildi -> o TEYIT).
K1 BOGA'da PAHALI-UCUZ > 0, gun-kumeli t>=+2,0 · K2 taze pencerede ayni isaret ·
K3 MDE. K4 YOK (ongorulen gurultu olcut yapilmaz — bugunku ders).

Salt-okunur. Veri BELLEKTE birlestirilir, hicbir arsive yazilmaz.
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
ESKI_K, YENI_K = os.path.join(BURA, "klines_1h_uzun"), os.path.join(BURA, "taze_1h")
ESKI_F, YENI_F = os.path.join(BURA, "funding_gecmis"), os.path.join(BURA, "taze_funding")

# --- ON-KAYITTA SABITLENEN (bolum 2/4) — TARANMAZ ---
UCUZ_ESIK = 0.07            # mevcut kapi (config)
PAHALI_ESIK = 2.3610        # 2 yillik %80 dilim — on-kayitta sabitlendi
MA50_MESAFE = 3.72
PUMP, MIN_VOL = 20.0, 3_000_000
HEDEF_PCT, UFUK = 10.0, 72
ASGARI_STOP = 2.0
ISINMA, SOGUMA_SAAT = 220, 24
TAZE_BAS = "2026-08-21"
KOLLAR = [("A", None), ("2.5x", 2.5)]     # stop genisligi burada IKINCIL


def birlestir(a, b):
    d = {}
    for y in (a, b):
        if os.path.exists(y):
            try:
                for x in json.load(open(y, encoding="utf-8")):
                    d[int(x["t"])] = x
            except Exception:
                pass
    return [d[k] for k in sorted(d)] if d else None


def yukle():
    kl, fn = {}, {}
    for f in sorted(os.listdir(ESKI_K)):
        if not f.endswith(".json"):
            continue
        sym = f[:-5]
        b = birlestir(os.path.join(ESKI_K, f), os.path.join(YENI_K, f))
        if not b or len(b) < ISINMA + UFUK + 50:
            continue
        kl[sym] = b
        fn[sym] = birlestir(os.path.join(ESKI_F, f), os.path.join(YENI_F, f)) or []
    return kl, fn


def sinama():
    hata = []
    b = [{"t": i * 3600000, "o": 100.0, "h": 100.0 + (i % 7),
          "l": 100.0 - (i % 5), "c": 100.0 + (i % 3)} for i in range(300)]
    atrs = ir.atr_serisi(b)
    for si in (250, 270):
        ref, a = b[si + 1]["o"], atrs[si]
        sA = ir.stop_hesapla(b, si, ref, a)
        if sA > ref + 2.5 * a + 1e-9:
            hata.append("S1 MERDIVEN BOZUK si=%d" % si)
    if PAHALI_ESIK <= UCUZ_ESIK:
        hata.append("S2 AYNA ESIGI ANLAMSIZ: %.4f <= %.4f" % (PAHALI_ESIK, UCUZ_ESIK))
    if hata:
        print("SINAMA DUSTU — betik calismayi REDDEDIYOR:")
        for h in hata:
            print("  - " + h)
        raise SystemExit(1)
    print("  sinama: GECTI (merdiven · ayna esigi ucuzun ustunde)\n")


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


def tara(kl, fn):
    rej = ir.btc_rejim()
    taze_bas = int(dt.datetime.strptime(TAZE_BAS, "%Y-%m-%d")
                   .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    en_son = max(b[-1]["t"] for b in kl.values())
    kesme = en_son - UFUK * 3600000
    kume = {"UCUZ": [], "PAHALI": []}
    son = {k: {} for k in kume}
    eleme = collections.Counter()
    for sym, b in kl.items():
        fr = fn.get(sym) or []
        ft = [x["t"] for x in fr]
        atrs = ir.atr_serisi(b)
        ma50 = ir.ma_serisi(b, 50)
        r_cache = {}
        for i in range(ISINMA, len(b)):
            x = b[i]
            if x["t"] > kesme:
                continue
            if (x.get("qv") or 0) < MIN_VOL / 24:
                continue
            if i < 24 or b[i - 24]["c"] <= 0:
                continue
            if (x["c"] / b[i - 24]["c"] - 1) * 100 >= PUMP:
                continue
            if not ma50[i] or ma50[i] <= 0:
                continue
            if (x["c"] / ma50[i] - 1) * 100 < MA50_MESAFE:
                continue
            hedefler = []
            if x["c"] <= UCUZ_ESIK:
                hedefler.append("UCUZ")
            elif x["c"] >= PAHALI_ESIK:
                hedefler.append("PAHALI")
            if not hedefler:
                continue
            for h in hedefler:
                s0 = son[h].get(sym)
                if s0 is not None and x["t"] - s0 < SOGUMA_SAAT * 3600000:
                    continue
                if i not in r_cache:
                    r_cache[i] = islem(b, atrs, i, ft, fr)
                    if r_cache[i] is None:
                        eleme[h + "_asgari_stop"] += 1
                r = r_cache[i]
                if not r:
                    break
                son[h][sym] = x["t"]
                kume[h].append({
                    "sym": sym, "t": b[i + 1]["t"], "gun": b[i + 1]["t"] // 86400000,
                    "rejim": rej.get(b[i]["t"] // 3600000, "NOTR"),
                    "taze": b[i + 1]["t"] >= taze_bas, "kol": r})
    return kume, eleme


def gun_ort(ky, fn_):
    g = collections.defaultdict(list)
    for k in ky:
        g[k["gun"]].append(fn_(k))
    return {d: sum(v) / len(v) for d, v in g.items()}


def iki_ornek(ga, gb):
    a, b = list(ga.values()), list(gb.values())
    if len(a) < 3 or len(b) < 3:
        return None, None, None
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    se = math.sqrt(stx.variance(a) / len(a) + stx.variance(b) / len(b))
    return (ma - mb), ((ma - mb) / se if se else None), (2.0 * se if se else None)


def satir(ad, ky):
    if not ky:
        print("  %-8s (bos)" % ad)
        return None
    m = stx.mean([k["kol"]["A"]["net"] for k in ky])
    print("  %-8s N=%-6d gun=%-4d sembol=%-4d  net%% %+7.3f  R %+8.4f  stop%% %5.2f  stop-ol %%%.0f"
          % (ad, len(ky), len({k["gun"] for k in ky}), len({k["sym"] for k in ky}), m,
             stx.mean([k["kol"]["A"]["R"] for k in ky]),
             stx.mean([k["kol"]["A"]["sp"] for k in ky]),
             sum(1 for k in ky if k["kol"]["A"]["tip"] == "STOP") / len(ky) * 100))
    return m


def main():
    print("=" * 78)
    print("UCUZ yerine PAHALI — fiyat seviyesinin isareti rejimle donuyor mu?")
    print("=" * 78)
    print("ON-KAYIT: ON_KAYIT_pahali_ayna.md commit 5f213c2 — KOSMADAN once")
    print("UCUZ  = fiyat <= $%.4f   ·   PAHALI = fiyat >= $%.4f (2 yil %%80 dilim)"
          % (UCUZ_ESIK, PAHALI_ESIK))
    print("ikisinde de ma50_mesafe >= %%%.2f · SHORT · A-stop · %%%d hedef · %ds\n"
          % (MA50_MESAFE, HEDEF_PCT, UFUK))
    sinama()

    kl, fn = yukle()
    print("sembol: %d" % len(kl))
    kume, eleme = tara(kl, fn)
    print("asgari_stop %%%.1f elemesi: %s\n" % (ASGARI_STOP, dict(eleme)))

    print("### TUM PENCERE (2 yil + taze)")
    for ad in ("UCUZ", "PAHALI"):
        satir(ad, kume[ad])
    print()

    print("### REJIME GORE (birincil hucre: BOGA)")
    ort = {}
    for rj in ("BOGA", "NOTR", "AYI"):
        print("  --- %s ---" % rj)
        ort[rj] = {}
        for ad in ("UCUZ", "PAHALI"):
            ky = [k for k in kume[ad] if k["rejim"] == rj]
            ort[rj][ad] = satir(ad, ky)
        gu = gun_ort([k for k in kume["UCUZ"] if k["rejim"] == rj], lambda k: k["kol"]["A"]["net"])
        gp = gun_ort([k for k in kume["PAHALI"] if k["rejim"] == rj], lambda k: k["kol"]["A"]["net"])
        f, t, mde = iki_ornek(gp, gu)
        if f is None:
            print("           PAHALI - UCUZ : yetersiz\n")
            ort[rj]["fark"] = None
            continue
        gor = "GORULUR" if abs(f) >= mde else "goremiyoruz"
        print("           PAHALI - UCUZ : %+8.4f   t_gun %+6.2f   MDE %7.4f  -> %s\n"
              % (f, t or 0, mde, gor))
        ort[rj]["fark"] = (f, t, mde)

    print("### TAZE PENCERE (%s ->) — DOGRULAMA, kesif degil" % TAZE_BAS)
    gu = gun_ort([k for k in kume["UCUZ"] if k["taze"]], lambda k: k["kol"]["A"]["net"])
    gp = gun_ort([k for k in kume["PAHALI"] if k["taze"]], lambda k: k["kol"]["A"]["net"])
    for ad in ("UCUZ", "PAHALI"):
        satir(ad, [k for k in kume[ad] if k["taze"]])
    ft, tt, mt = iki_ornek(gp, gu)
    if ft is not None:
        print("           PAHALI - UCUZ : %+8.4f   t_gun %+6.2f   MDE %7.4f"
              % (ft, tt or 0, mt))
    print()

    print("=" * 78)
    print("HUKUM — ON_KAYIT_pahali_ayna.md bolum 5")
    print("=" * 78)
    b = ort.get("BOGA", {}).get("fark")
    if not b:
        print("BOGA hucresi olculemedi -> HUKUM YOK")
        return
    f, t, mde = b
    K1 = f > 0 and t is not None and t >= 2.0
    print("K1  BOGA'da PAHALI - UCUZ > 0 · t_gun >= +2,0 : %+.4f  t %+.2f -> %s"
          % (f, t or 0, "GECTI" if K1 else "DUSTU"))
    K2 = ft is not None and ft * f > 0
    print("K2  taze pencerede AYNI isaret : %s -> %s"
          % (("%+.4f" % ft) if ft is not None else "yok", "GECTI" if K2 else "DUSTU"))
    K3 = abs(f) >= mde
    print("K3  guc |fark| >= MDE : %.4f vs %.4f -> %s"
          % (abs(f), mde, "GORULUR" if K3 else "GOREMIYORUZ"))
    dusen = [a for a, v in (("K1", K1), ("K2", K2), ("K3", K3)) if not v]
    print("\nSONUC: %s" % ("GECTI" if not dusen else "DUSTU (dusen: %s)" % ", ".join(dusen)))

    print("\n" + "=" * 78)
    print("YORUM KURALI (on-kayit bolum 5, OLCUT DEGIL)")
    print("=" * 78)
    isar = {rj: (ort[rj]["fark"][0] if ort[rj].get("fark") else None)
            for rj in ("BOGA", "NOTR", "AYI")}
    print("  PAHALI - UCUZ :  " + " · ".join(
        "%s %s" % (rj, ("%+.4f" % v) if v is not None else "yok") for rj, v in isar.items()))
    bo = isar.get("BOGA")
    dg = [v for rj, v in isar.items() if rj != "BOGA" and v is not None]
    if bo is None or not dg:
        print("  -> yorum yapilamiyor")
    elif bo > 0 and all(v < 0 for v in dg):
        print("  -> REJIM TERSLIGI GERCEK: bogada pahali, digerlerinde ucuz onde.")
        print("     config'in ongorusu ('bogada ucuz coinler one gecebilir') DOGRU.")
    elif bo > 0 and all(v > 0 for v in dg):
        print("  -> TERSLIK YOK: pahali HER REJIMDE onde -> kapi bastan ters tarafa")
        print("     kurulmus olabilir (ayri on-kayit ister).")
    else:
        print("  -> fiyat seviyesi bu rejimde belirgin bilgi tasimiyor.")

    print("\nMUTLAK KARLILIK (tahmin 3): BOGA'da iki kol da negatif mi?")
    for ad in ("UCUZ", "PAHALI"):
        v = ort["BOGA"].get(ad)
        print("   %-7s %s" % (ad, ("%+.3f%%" % v) if v is not None else "yok"))

    print("\nVeri BELLEKTE birlestirildi · arsive yazim: YOK · bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
