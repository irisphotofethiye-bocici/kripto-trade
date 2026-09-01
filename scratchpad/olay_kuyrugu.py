#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OLAY KUYRUGU — bir duyurudan N dakika sonra hala maliyeti asan kenar var mi?
On-kayit: ON_KAYIT_olay_kuyrugu.md (bu betikten ONCE commit edilir). Olcutler SABIT.

Soru: Grok -> bildirim -> analiz -> karar zinciri DAKIKALAR suruyor. O gecikmeden
sonra girilse ne kalir? Iki kiyas: (a) maliyet, (b) AYNI sembolde AYNI pencerede
eslestirilmis RASTGELE anlar (sans tabani) — olay basina ESLI fark.

Veri: Binance fapi 5 dakikalik mum. Olay penceresi basina indirilir ve
scratchpad/olay_pencere/ altinda onbelleklenir. YENI dizin — mevcut arsivlere
(perp_seri / klines_1h_uzun) DOKUNMAZ, ezme riski yok.

ADAY SECIMI: arsiv kapsami SART KOSULMAZ (fiyat zaten taze cekiliyor); sembolu
cozulmus her birincil duyuru denenir, dusenler tip tip RAPORLANIR. Boylece
"arsivde yok" yuzunden gereksiz orneklem kaybi olmaz.
SALT OKUMA (bot dosyalarina yazim YOK).
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, time, math, random, collections, statistics

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJE not in _sys.path:
    _sys.path.insert(0, PROJE)
import evren

OLAYLAR = os.path.join(PROJE, "scratchpad", "olaylar.jsonl")
ONBELLEK = os.path.join(PROJE, "scratchpad", "olay_pencere")

CFG = json.load(open(os.path.join(PROJE, "kripto-config.json"), encoding="utf-8"))
MAL = CFG.get("maliyet", {})
TEK_YON = float(MAL.get("taker_fee_pct", 0.045)) + float(MAL.get("slippage_pct", 0.02))
MALIYET = 2.0 * TEK_YON            # config turevi gidis-donus (~%0,13)
ESIK_MALIYET = 0.19                # on-kayitta SABIT (plandaki muhafazakar sayi)
ESIK_KENAR = 3.0 * ESIK_MALIYET    # kabul bari = %0,57

M = 60 * 1000
GECIKME = [5, 15, 30, 60, 120, 240]        # dakika
UFUK = [60, 240, 1440]                     # dakika (1sa / 4sa / 24sa)
ONCE_GUN, SONRA_GUN = 3, 2
K_CEKILIS = 20
ASGARI_N = 10
# --- BIRINCIL HUCRE (on-kayitta ONCEDEN atandi, tabloya bakilarak SECILMEDI)
BIRINCIL_GRUP, BIRINCIL_D, BIRINCIL_H = "olumlu_duyuru", 30, 240
YON = {"spot_listeleme": +1, "launchpool": +1, "perp_listeleme": +1, "delisting": -1}
GRUP = {"spot_listeleme": "olumlu_duyuru", "launchpool": "olumlu_duyuru",
        "perp_listeleme": "perp_listeleme", "delisting": "delisting"}
random.seed(20260901)


def pencere_cek(sym, t0):
    """5 dk mum [t0-3g, t0+2g]. Onbellekli. Donus: [[t, close], ...] artan."""
    os.makedirs(ONBELLEK, exist_ok=True)
    yol = os.path.join(ONBELLEK, "%s_%d.json" % (sym, t0))
    if os.path.exists(yol):
        try:
            d = json.load(open(yol))
            if d:
                return d
        except Exception:
            pass
    bas, bit = t0 - ONCE_GUN * 86400000, t0 + SONRA_GUN * 86400000
    bar, imlec = [], bas
    while imlec < bit:
        u = ("https://fapi.binance.com/fapi/v1/klines?symbol=%sUSDT&interval=5m"
             "&startTime=%d&endTime=%d&limit=500" % (sym, imlec, bit))
        try:
            k = evren.get(u)
        except Exception:
            return None
        if not k:
            break
        bar.extend([[int(b[0]), float(b[4])] for b in k])
        yeni = int(k[-1][0]) + 5 * M
        if yeni <= imlec:
            break
        imlec = yeni
        time.sleep(0.15)
        if len(k) < 500:
            break
    if len(bar) < 200:
        return None
    bar = sorted({b[0]: b for b in bar}.values(), key=lambda z: z[0])
    json.dump(bar, open(yol, "w"))
    return bar


def kapanis(bar, indeks, ts):
    """ts anini ICEREN 5dk barinin kapanisi (yoksa None)."""
    i = indeks.get(ts - (ts % (5 * M)))
    return bar[i][1] if i is not None else None


def yol_olc(bar, indeks, t0, yon):
    """Tek bir t0 icin: sizinti, gecikme basina kacan hareket ve ileri getiri."""
    p_on = kapanis(bar, indeks, t0 - 5 * M)          # duyurudan ONCEKI bar
    if not p_on or p_on <= 0:
        return None
    p_saat_once = kapanis(bar, indeks, t0 - 60 * M)
    out = {"p_on": p_on, "giris": {}, "ileri": {},
           "sizinti": (yon * (p_on - p_saat_once) / p_saat_once * 100.0)
           if (p_saat_once and p_saat_once > 0) else None}
    for d in GECIKME:
        e = kapanis(bar, indeks, t0 + d * M)
        if not e or e <= 0:
            continue
        out["giris"][d] = yon * (e - p_on) / p_on * 100.0     # girise kadar KACAN
        for h in UFUK:
            x = kapanis(bar, indeks, t0 + (d + h) * M)
            if x and x > 0:
                out["ileri"]["%d_%d" % (d, h)] = yon * (x - e) / e * 100.0 - MALIYET
    return out


def gun_ortalamalari(ciftler):
    g = collections.defaultdict(list)
    for gun, v in ciftler:
        g[gun].append(v)
    return [sum(v) / len(v) for _, v in sorted(g.items())]


def gun_t(ciftler):
    """ciftler: [(gun, deger)] -> (ort, t, gun_sayisi, MDE@t=2)"""
    d = gun_ortalamalari(ciftler)
    if len(d) < 3:
        return None, None, len(d), None
    m, sd = sum(d) / len(d), statistics.stdev(d)
    se = sd / math.sqrt(len(d))
    return m, (m / se if se else None), len(d), (2.0 * se if se else None)


def olay_t(vals):
    if len(vals) < 3:
        return None, None
    m, sd = sum(vals) / len(vals), statistics.stdev(vals)
    return m, (m / (sd / math.sqrt(len(vals))) if sd else None)


def esli_fark(W, anahtar):
    """Olay basina: gercek - kendi sans cekilislerinin ortalamasi. [(gun, fark)]"""
    out = []
    for s in W:
        if anahtar not in s["g"]["ileri"]:
            continue
        sv = [x["ileri"][anahtar] for x in s["sans"] if anahtar in x["ileri"]]
        if sv:
            out.append((s["gun"], s["g"]["ileri"][anahtar] - sum(sv) / len(sv)))
    return out


def main():
    print("OLAY KUYRUGU — duyurudan sonra kovalanabilir kenar kaliyor mu?")
    print("on-kayit ON_KAYIT_olay_kuyrugu.md · olcutler SABIT")
    print("=" * 108)
    print("maliyet modeli: gidis-donus %%%.3f (config turevi)" % MALIYET)
    print("kabul bari    : %%%.2f  (= 3 x %%%.2f, on-kayitta sabitlendi)" % (ESIK_KENAR, ESIK_MALIYET))
    print("birincil hucre: grup=%s · gecikme=%d dk · ufuk=%d dk  (ONCEDEN atandi)"
          % (BIRINCIL_GRUP, BIRINCIL_D, BIRINCIL_H))

    ol = [json.loads(l) for l in open(OLAYLAR, encoding="utf-8")]
    aday = []
    for o in ol:
        if not o.get("birincil") or not o.get("kume_ilk") or o["tip"] not in YON:
            continue
        for s in o["semboller"]:
            aday.append({"sym": s, "ts": o["ts"], "tip": o["tip"],
                         "grup": GRUP[o["tip"]], "utc": o["utc"], "gun": o["utc"][:10]})
    print("\naday olay-sembol cifti: %d" % len(aday))
    print("  tip dagilimi: %s" % dict(collections.Counter(a["tip"] for a in aday)))

    sonuc = []
    dus = collections.defaultdict(collections.Counter)
    for i, a in enumerate(aday):
        if (i + 1) % 40 == 0:
            print("  ... %d/%d  (olculen %d)" % (i + 1, len(aday), len(sonuc)))
        bar = pencere_cek(a["sym"], a["ts"])
        if not bar:
            dus[a["tip"]]["mum_yok"] += 1
            continue
        indeks = {b[0]: j for j, b in enumerate(bar)}
        yon = YON[a["tip"]]
        g = yol_olc(bar, indeks, a["ts"], yon)
        if not g:
            dus[a["tip"]]["olay_oncesi_bar_yok"] += 1
            continue
        dis0, dis1 = a["ts"] - 2 * 3600000, a["ts"] + 26 * 3600000
        uygun = [b[0] for b in bar
                 if not (dis0 <= b[0] <= dis1)
                 and b[0] >= bar[0][0] + 70 * M
                 and b[0] <= bar[-1][0] - (max(GECIKME) + max(UFUK) + 10) * M]
        cek = random.sample(uygun, min(K_CEKILIS, len(uygun))) if uygun else []
        sans = [x for x in (yol_olc(bar, indeks, t, yon) for t in cek) if x]
        if len(sans) < 5:
            dus[a["tip"]]["sans_yetersiz"] += 1
            continue
        a2 = dict(a)
        a2["g"] = g
        a2["sans"] = sans
        sonuc.append(a2)

    # ------------------------------------------------------------------ eleme
    print("\n" + "=" * 108)
    print("0) ELEME DOKUMU — hangi tipte kac olay neden dustu")
    print("-" * 108)
    print("  %-18s %8s %10s %s" % ("tip", "aday", "OLCULEN", "dusme sebepleri"))
    for tip in sorted(set(list(dus.keys()) + [s["tip"] for s in sonuc])):
        n_ad = sum(1 for a in aday if a["tip"] == tip)
        n_ol = sum(1 for s in sonuc if s["tip"] == tip)
        print("  %-18s %8d %10d %s" % (tip, n_ad, n_ol, dict(dus[tip]) or "-"))
    print("\n  NOT: perp_listeleme yapisi geregi elenir — perp kendi listelenmesinden")
    print("       ONCE var olmadigi icin olay oncesi fiyat yoktur. Bu bir SONUCTUR.")
    print("\nolculen olay: %d" % len(sonuc))
    if not sonuc:
        print("olculebilir olay yok — HUKUM VERILEMEZ")
        return

    # ------------------------------------------------------------------ sizinti
    print("\n" + "=" * 108)
    print("1) SIZINTI KONTROLU — duyurudan ONCEKI 1 saatte hareket var mi?")
    print("   (buyukse haber onceden sizmis; t=0 tanimi KIRLI ve olcum yanlidir)")
    print("-" * 108)
    print("  %-18s %6s %14s %14s %10s" % ("grup/tip", "N", "ort sizinti", "medyan", "olay-t"))
    for tip in sorted({s["tip"] for s in sonuc}):
        w = [s["g"]["sizinti"] for s in sonuc if s["tip"] == tip and s["g"]["sizinti"] is not None]
        if len(w) < 3:
            continue
        m, t = olay_t(w)
        print("  %-18s %6d %+13.3f%% %+13.3f%% %9s"
              % (tip, len(w), m, statistics.median(w), ("%+.2f" % t) if t else "-"))

    # ------------------------------------------- kacan hareket + kalan kenar
    print("\n" + "=" * 108)
    print("2) KACAN HAREKET ve KALAN KENAR")
    print("   kacan = duyuru anindan girise kadarki hareket (bunu ALAMAYIZ)")
    print("   hucre = ham kenar%% / esli farkin gun-t'si (sans tabanina karsi)")
    print("-" * 108)
    kume = collections.defaultdict(list)
    for s in sonuc:
        kume[s["tip"]].append(s)
        if s["grup"] != s["tip"]:
            kume[s["grup"] + " (havuz)"].append(s)
    for tip in sorted(kume):
        W = kume[tip]
        if len(W) < 5:
            continue
        y = YON.get(W[0]["tip"], 1)
        print("\n  %s   (N=%d olay · %d gun · yon %s)"
              % (tip, len(W), len({s["gun"] for s in W}), "LONG" if y > 0 else "SHORT"))
        print("  %-9s %9s |%s" % ("gecikme", "kacan",
                                  "".join("%16s" % ("ufuk %dsa" % (h // 60)) for h in UFUK)))
        print("  " + "-" * 96)
        for d in GECIKME:
            kac = [s["g"]["giris"][d] for s in W if d in s["g"]["giris"]]
            if len(kac) < 3:
                continue
            satir = "  %-9s %+8.2f%% |" % ("%d dk" % d, sum(kac) / len(kac))
            for h in UFUK:
                anah = "%d_%d" % (d, h)
                ger = [s for s in W if anah in s["g"]["ileri"]]
                if len(ger) < 5:
                    satir += "%16s" % "-"
                    continue
                gm = sum(s["g"]["ileri"][anah] for s in ger) / len(ger)
                fk = esli_fark(ger, anah)
                ft = gun_t(fk)[1] if len(fk) >= 5 else None
                satir += "%10.2f/%-5s" % (gm, ("t%+.1f" % ft) if ft else "t-")
            print(satir)

    # ------------------------------------------------------------ mekanik esitligi
    anah = "%d_%d" % (BIRINCIL_D, BIRINCIL_H)
    print("\n" + "=" * 108)
    print("3) MEKANIK ESITLIGI — gercek ve sans kollari ayni oynaklikta mi?")
    print("   (CLAUDE.md 2026-08-20: kollar oynaklikta ayrisiyorsa kiyas bozulur)")
    print("-" * 108)
    print("  %-24s %8s %16s %16s" % ("grup", "N", "gercek |ort|", "sans |ort|"))
    for tip in sorted(kume):
        W = [s for s in kume[tip] if anah in s["g"]["ileri"]]
        if len(W) < 5:
            continue
        gv = [abs(s["g"]["ileri"][anah]) for s in W]
        sv = [abs(x["ileri"][anah]) for s in W for x in s["sans"] if anah in x["ileri"]]
        if not sv:
            continue
        print("  %-24s %8d %15.3f%% %15.3f%%"
              % (tip, len(W), sum(gv) / len(gv), sum(sv) / len(sv)))

    # ------------------------------------------------------------ birincil hüküm
    print("\n" + "=" * 108)
    print("4) BIRINCIL HUCRE — on-kayitta ONCEDEN atandi, tabloya bakilarak SECILMEDI")
    print("=" * 108)
    W = [s for s in sonuc if s["grup"] == BIRINCIL_GRUP and anah in s["g"]["ileri"]]
    if len(W) < ASGARI_N:
        print("  N=%d — on-kayittaki asgari %d'un altinda." % (len(W), ASGARI_N))
        print("  HUKUM VERILMEZ (guc yetersiz). Bu bir SONUCTUR ve aynen raporlanir.")
    else:
        ham = [s["g"]["ileri"][anah] for s in W]
        fk = esli_fark(W, anah)
        hm, ht = olay_t(ham)
        fm, ft, ng, mde = gun_t(fk)
        print("  N=%d olay · %d gun  (%s)"
              % (len(W), len({s["gun"] for s in W}),
                 dict(collections.Counter(s["tip"] for s in W))))
        print("  ham kenar (maliyet dusulmus): %+.3f%%   (olay-t %s)"
              % (hm, ("%+.2f" % ht) if ht else "-"))
        print("  sans tabanina ESLI fark     : %+.3f%%   (gun-t %s · %d gun)"
              % (fm, ("%+.2f" % ft) if ft else "-", ng))
        k1 = hm >= ESIK_KENAR
        k2 = (fm is not None and fm > 0) and (ft is not None and ft >= 2.0)
        print()
        print("  K1  ham kenar >= %%%.2f          : %-6s (%.3f)"
              % (ESIK_KENAR, "GECTI" if k1 else "DUSTU", hm))
        print("  K2  esli fark > 0 ve gun-t >= 2 : %-6s (%.3f / %s)"
              % ("GECTI" if k2 else "DUSTU", fm if fm is not None else 0.0,
                 ("%+.2f" % ft) if ft else "-"))
        print()
        print("  HUKUM: %s" % ("GECTI — bu olay tipi kovalanabilir"
                               if (k1 and k2) else
                               "DUSTU — bu gecikmeden sonra kovalanabilir kenar YOK"))
        # --- GUC: bir DUSTU sonucu 'etki yok' mu, 'goremiyoruz' mu?
        print()
        print("  GUC DENETIMI (on-kayitta zorunlu kilindi):")
        if mde:
            print("    asgari saptanabilir etki (t=2) : %%%.3f" % mde)
            print("    kabul bari                     : %%%.2f" % ESIK_KENAR)
            if mde > ESIK_KENAR:
                print("    -> ORNEKLEM YETERSIZ: bar kadar buyuk gercek bir etkiyi bile")
                print("       saptayamayiz. 'DUSTU' = ETKI YOK DEGIL, 'GOREMIYORUZ'.")
            else:
                print("    -> orneklem bari saptayacak guctedir; DUSTU anlamlidir.")
        else:
            print("    MDE hesaplanamadi (gun sayisi yetersiz)")

    print("\n" + "=" * 108)
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
