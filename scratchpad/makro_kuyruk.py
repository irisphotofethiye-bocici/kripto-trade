#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MAKRO KUYRUK — takvimli makro olaydan D dakika sonra katilan ne kazanir?
On-kayit: ON_KAYIT_makro_kuyruk.md (bu betikten ONCE commit edildi). Olcutler SABIT.

Yon ILERIYE BAKMADAN atanir: ilk 5 dakikanin isareti (t0+5dk'da elde olan
bilgi); giris t0+D, D>=5dk. Sans kolu AYNI yon kuralini kullanir — yoksa
olculen sey haberin etkisi degil kisa vadeli momentumun kendisi olur.

Enstruman yalniz BTC (alt para eklemek ayni gunu tekrar saymak olurdu = sahte N).
Fiyat: fapi 5dk mum, scratchpad/makro_pencere/ (YENI dizin, mevcut arsivlere
DOKUNMAZ). SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, time, math, random, statistics, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJE not in _sys.path:
    _sys.path.insert(0, PROJE)
import evren

OLAYLAR = os.path.join(PROJE, "scratchpad", "makro_olaylar.json")
ONBELLEK = os.path.join(PROJE, "scratchpad", "makro_pencere")

CFG = json.load(open(os.path.join(PROJE, "kripto-config.json"), encoding="utf-8"))
MAL = CFG.get("maliyet", {})
MALIYET = 2.0 * (float(MAL.get("taker_fee_pct", 0.045)) + float(MAL.get("slippage_pct", 0.02)))
ESIK_KENAR = 0.57                      # on-kayitta SABIT (3 x %0,19)

M = 60 * 1000
SEMBOL = "BTC"
GECIKME = [5, 15, 30, 60, 120]
UFUK = [60, 240, 1440]
ONCE_GUN, SONRA_GUN = 7, 3
K_CEKILIS = 20
ASGARI_N = 10
BIRINCIL_D, BIRINCIL_H = 30, 240
random.seed(20260901)


def pencere_cek(t0):
    os.makedirs(ONBELLEK, exist_ok=True)
    yol = os.path.join(ONBELLEK, "%s_%d.json" % (SEMBOL, t0))
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
             "&startTime=%d&endTime=%d&limit=500" % (SEMBOL, imlec, bit))
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
        time.sleep(0.12)
        if len(k) < 500:
            break
    if len(bar) < 500:
        return None
    bar = sorted({b[0]: b for b in bar}.values(), key=lambda z: z[0])
    json.dump(bar, open(yol, "w"))
    return bar


def kapanis(bar, ix, ts):
    i = ix.get(ts - (ts % (5 * M)))
    return bar[i][1] if i is not None else None


def yol_olc(bar, ix, t0):
    """Yon ilk 5 dakikadan; sonra gecikme x ufuk izgarasi."""
    p_on = kapanis(bar, ix, t0 - 5 * M)
    p5 = kapanis(bar, ix, t0 + 5 * M)
    if not p_on or not p5 or p_on <= 0:
        return None
    ilk = (p5 - p_on) / p_on * 100.0
    yon = 1 if ilk > 0 else (-1 if ilk < 0 else 0)
    if yon == 0:
        return None
    out = {"ilk5": ilk, "yon": yon, "ileri": {}}
    for d in GECIKME:
        e = kapanis(bar, ix, t0 + d * M)
        if not e or e <= 0:
            continue
        for h in UFUK:
            x = kapanis(bar, ix, t0 + (d + h) * M)
            if x and x > 0:
                out["ileri"]["%d_%d" % (d, h)] = yon * (x - e) / e * 100.0 - MALIYET
    return out


def t_ist(v):
    if len(v) < 3:
        return None, None, None
    m, sd = sum(v) / len(v), statistics.stdev(v)
    se = sd / math.sqrt(len(v))
    return m, (m / se if se else None), (2.0 * se if se else None)


def esli(W, anah):
    out = []
    for s in W:
        if anah not in s["g"]["ileri"]:
            continue
        sv = [x["ileri"][anah] for x in s["sans"] if anah in x["ileri"]]
        if sv:
            out.append(s["g"]["ileri"][anah] - sum(sv) / len(sv))
    return out


def main():
    print("MAKRO KUYRUK — takvimli makro olaydan sonra kovalanabilir kenar var mi?")
    print("on-kayit ON_KAYIT_makro_kuyruk.md · olcutler SABIT")
    print("=" * 104)
    print("maliyet %%%.3f · kabul bari %%%.2f · birincil hucre D=%d dk H=%d dk (ONCEDEN atandi)"
          % (MALIYET, ESIK_KENAR, BIRINCIL_D, BIRINCIL_H))
    print("enstruman: %s · yon = ilk 5 dakikanin isareti (ileriye bakma YOK)" % SEMBOL)

    ol = json.load(open(OLAYLAR, encoding="utf-8"))
    print("\nolay: %d  %s" % (len(ol), dict(collections.Counter(o["tip"] for o in ol))))

    sonuc, dus = [], collections.Counter()
    for i, o in enumerate(ol):
        bar = pencere_cek(o["ts"])
        if not bar:
            dus["mum_yok"] += 1
            continue
        ix = {b[0]: j for j, b in enumerate(bar)}
        g = yol_olc(bar, ix, o["ts"])
        if not g:
            dus["yon_yok_veya_bar_yok"] += 1
            continue
        d0, d1 = o["ts"] - 2 * 3600000, o["ts"] + 26 * 3600000
        uygun = [b[0] for b in bar
                 if not (d0 <= b[0] <= d1)
                 and b[0] >= bar[0][0] + 10 * M
                 and b[0] <= bar[-1][0] - (max(GECIKME) + max(UFUK) + 10) * M]
        cek = random.sample(uygun, min(K_CEKILIS, len(uygun))) if uygun else []
        sans = [x for x in (yol_olc(bar, ix, t) for t in cek) if x]
        if len(sans) < 5:
            dus["sans_yetersiz"] += 1
            continue
        sonuc.append({"tip": o["tip"], "utc": o["utc"], "g": g, "sans": sans})
        if (i + 1) % 10 == 0:
            print("  ... %d/%d (olculen %d)" % (i + 1, len(ol), len(sonuc)))

    print("\nolculen: %d · eleme: %s" % (len(sonuc), dict(dus) or "-"))
    if len(sonuc) < ASGARI_N:
        print("N yetersiz — HUKUM VERILMEZ")
        return

    # ---------------------------------------------------- ilk tepki gercek mi
    print("\n" + "=" * 104)
    print("1) OLAYLAR GERCEKTEN OYNATIYOR MU? (ilk 5 dakikanin MUTLAK buyuklugu)")
    print("   Bu gecmezse olcumun oznesi yok demektir.")
    print("-" * 104)
    print("  %-16s %5s %14s %14s %10s" % ("grup", "N", "olay |ilk5|", "sans |ilk5|", "oran"))
    for grup in ["havuz", "fomc_karar", "fomc_tutanak"]:
        W = sonuc if grup == "havuz" else [s for s in sonuc if s["tip"] == grup]
        if len(W) < 3:
            continue
        go = sum(abs(s["g"]["ilk5"]) for s in W) / len(W)
        sv = [abs(x["ilk5"]) for s in W for x in s["sans"]]
        sa = sum(sv) / len(sv) if sv else 0
        print("  %-16s %5d %13.4f%% %13.4f%% %9.2fx"
              % (grup, len(W), go, sa, (go / sa) if sa else 0))
    yl = sum(1 for s in sonuc if s["g"]["yon"] > 0)
    print("\n  yon dagilimi: LONG %d · SHORT %d" % (yl, len(sonuc) - yl))

    # ---------------------------------------------------------------- izgara
    print("\n" + "=" * 104)
    print("2) IZGARA — ham kenar%% / esli farkin t'si (betimleyici, hukum tasimaz)")
    print("-" * 104)
    for grup in ["havuz", "fomc_karar", "fomc_tutanak"]:
        W = sonuc if grup == "havuz" else [s for s in sonuc if s["tip"] == grup]
        if len(W) < 5:
            continue
        print("\n  %s  (N=%d)" % (grup, len(W)))
        print("  %-10s|%s" % ("gecikme", "".join("%17s" % ("ufuk %dsa" % (h // 60)) for h in UFUK)))
        print("  " + "-" * 62)
        for d in GECIKME:
            satir = "  %-10s|" % ("%d dk" % d)
            for h in UFUK:
                anah = "%d_%d" % (d, h)
                ger = [s for s in W if anah in s["g"]["ileri"]]
                if len(ger) < 5:
                    satir += "%17s" % "-"
                    continue
                gm = sum(s["g"]["ileri"][anah] for s in ger) / len(ger)
                fk = esli(ger, anah)
                _, ft, _ = t_ist(fk) if len(fk) >= 3 else (None, None, None)
                satir += "%11.2f/%-5s" % (gm, ("t%+.1f" % ft) if ft else "t-")
            print(satir)

    # ------------------------------------------------------- mekanik esitligi
    anah = "%d_%d" % (BIRINCIL_D, BIRINCIL_H)
    print("\n" + "=" * 104)
    print("3) MEKANIK ESITLIGI — gercek ve sans kollari ayni oynaklikta mi?")
    print("-" * 104)
    W = [s for s in sonuc if anah in s["g"]["ileri"]]
    gv = [abs(s["g"]["ileri"][anah]) for s in W]
    sv = [abs(x["ileri"][anah]) for s in W for x in s["sans"] if anah in x["ileri"]]
    print("  gercek |ort| %.3f%%   ·   sans |ort| %.3f%%   ·   oran %.2fx"
          % (sum(gv) / len(gv), sum(sv) / len(sv), (sum(gv) / len(gv)) / (sum(sv) / len(sv))))

    # ------------------------------------------------------------ birincil
    print("\n" + "=" * 104)
    print("4) BIRINCIL HUCRE — on-kayitta ONCEDEN atandi")
    print("=" * 104)
    if len(W) < ASGARI_N:
        print("  N=%d < %d — HUKUM VERILMEZ" % (len(W), ASGARI_N))
        return
    ham = [s["g"]["ileri"][anah] for s in W]
    fk = esli(W, anah)
    hm, ht, _ = t_ist(ham)
    fm, ft, mde = t_ist(fk)
    print("  N=%d olay  (%s)" % (len(W), dict(collections.Counter(s["tip"] for s in W))))
    print("  ham kenar (maliyet dusulmus): %+.3f%%   (olay-t %s)" % (hm, ("%+.2f" % ht) if ht else "-"))
    print("  sans tabanina ESLI fark     : %+.3f%%   (olay-t %s)" % (fm, ("%+.2f" % ft) if ft else "-"))
    k1 = hm >= ESIK_KENAR
    k2 = (fm > 0) and (ft is not None and ft >= 2.0)
    print()
    print("  K1  ham kenar >= %%%.2f          : %-6s (%.3f)" % (ESIK_KENAR, "GECTI" if k1 else "DUSTU", hm))
    print("  K2  esli fark > 0 ve t >= 2     : %-6s (%.3f / %s)"
          % ("GECTI" if k2 else "DUSTU", fm, ("%+.2f" % ft) if ft else "-"))
    print()
    print("  HUKUM: %s" % ("GECTI — takvimli makro olay kovalanabilir" if (k1 and k2)
                           else "DUSTU — bu gecikmeden sonra kovalanabilir kenar YOK"))
    print()
    print("  GUC DENETIMI (on-kayitta zorunlu):")
    if mde:
        print("    asgari saptanabilir etki (t=2): %%%.3f  ·  kabul bari %%%.2f" % (mde, ESIK_KENAR))
        if mde > ESIK_KENAR:
            print("    -> ORNEKLEM YETERSIZ: 'DUSTU' = ETKI YOK DEGIL, 'GOREMIYORUZ'.")
        else:
            print("    -> orneklem bari saptayacak guctedir; DUSTU anlamlidir.")
    print("\n" + "=" * 104)
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
