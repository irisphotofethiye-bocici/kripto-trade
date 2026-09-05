#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STOP MESAFESI, REJIME GORE — BOGA'da cevap degisiyor mu? (2026-09-05)

ON-KAYIT: ON_KAYIT_stop_rejim.md, commit 272f62e — KOSTURULMADAN ONCE.
Bu betik o on-kaydi UYGULAR; olcut metnini degistirmez, olcuyu degistirmez.

KULLANICI ITIRAZI: "2 yillik veri rejim ayi rejim" -> haklidir (BOGA %10,8).
"22 Agustos sonrasi" OLCULEMEZ (veri 08-25'te bitiyor, 72s ileri getiri gerek,
kullanici indirmeyi reddetti). Olculebilir hali: REJIM KIRILIMI.

MEKANIK/EVREN/KOLLAR: stop_mesafesi.py'den CAGRILIR, yeniden yazilmaz.
BIRINCIL OLCU YINE R (degistirilmedi — onceki koszumda net% gecmis, R gecmemisti).

Salt-okunur. Veri indirme YOK. Bot dosyalarina yazim: YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import sys, os, math, random, statistics as stx, collections, datetime as dt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stop_mesafesi as sm
import ileri_rr as ir

VARYANT = sm.VARYANT
KOLLAR = sm.KOLLAR
PERM = 2000
random.seed(41)

# ON-KAYIT bolum 3'te SABITLENEN uc buyuk BOGA blogu (K2 bunlara dayanir)
BLOKLAR = {"B1": ("2024-11-06", "2024-12-10"),
           "B2": ("2025-05-06", "2025-05-22"),
           "B3": ("2026-05-02", "2026-05-06")}
EPIZOT = ("2026-08-21", "2026-08-25")       # kullanicinin epizodu — BETIMLEYICI


def gun_no(s):
    d = dt.datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
    return int(d.timestamp()) // 86400


def blok_ata(k):
    g = k["gun"]
    for ad, (a, b) in BLOKLAR.items():
        if gun_no(a) <= g <= gun_no(b):
            return ad
    return None


def fark_satir(ky, alan, v):
    g = sm.gun_ort(ky, lambda k: k["kol"][v][alan] - k["kol"]["A"][alan])
    return sm.t_ve_mde(g)


def dilim_rapor(ky, baslik, alan="R"):
    gun = len({k["gun"] for k in ky})
    sem = len({k["sym"] for k in ky})
    print("  %-14s N=%-6d gun=%-4d sembol=%-4d" % (baslik, len(ky), gun, sem))
    if len(ky) < 40 or gun < 5:
        print("      -> yetersiz (N<40 ya da gun<5), hukum YOK")
        return None
    out = {}
    for v in VARYANT:
        m, t, mde, n = fark_satir(ky, alan, v)
        out[v] = (m, t, mde, n)
        gor = "GORULUR" if (m is not None and mde is not None and abs(m) >= mde) else "goremiyoruz"
        print("      %-6s fark %+9.4f  t_gun %+6.2f  MDE %7.4f  -> %s"
              % (v, m, t if t is not None else 0, mde, gor))
    return out


def permutasyon(ky, alan):
    return sm.permutasyon(ky, alan)


def main():
    print("=" * 78)
    print("STOP MESAFESI, REJIME GORE — kullanici itirazi: 'veri ayi rejimi'")
    print("=" * 78)
    print("ON-KAYIT: ON_KAYIT_stop_rejim.md commit 272f62e — KOSMADAN once")
    print("BIRINCIL olcu: R (DEGISTIRILMEDI) · ikincil: net%")
    print("VERI INDIRME YOK — eldeki veri (kullanici talimati)\n")
    sm.sinama()

    # --- rejim gun dagilimi (BTC'den, arsiv alanindan DEGIL) ---
    rej = ir.btc_rejim()
    gunrej = {}
    for saat, r in rej.items():
        gunrej[saat // 24] = r
    c = collections.Counter(gunrej.values())
    print("rejim gun dagilimi: " + " · ".join("%s %d (%%%.1f)" % (k, v, v / len(gunrej) * 100)
                                              for k, v in sorted(c.items())))
    print()

    kume, _, islenen = sm.tara(iki_r=False)
    print("islenen sembol: %d\n" % islenen)

    for evren in ("A_funding", "B_ma50ucuz"):
        ky = kume[evren]
        birincil = (evren == "A_funding")
        print("=" * 78)
        print("### %s   (%s)" % (evren, "BIRINCIL" if birincil else "ikincil, hukum tasimaz"))
        print("=" * 78)
        pay = collections.Counter(k["rejim"] for k in ky)
        print("  islem dagilimi: " + " · ".join("%s %d (%%%.1f)" % (r, n, n / len(ky) * 100)
                                                for r, n in sorted(pay.items())))
        # tahmin 1 kontrolu: BOGA islem payi, BOGA gun payindan dusuk mu?
        gp = c.get("BOGA", 0) / len(gunrej) * 100
        ip = pay.get("BOGA", 0) / len(ky) * 100
        print("  BOGA: gun payi %%%.1f  vs  islem payi %%%.1f  -> tetik %s"
              % (gp, ip, "DAHA SEYREK" if ip < gp else "daha SIK"))
        print()

        print("  --- BIRINCIL olcu R, rejime gore eslesmis fark (kol - A) ---")
        rr = {}
        for r in ("BOGA", "NOTR", "AYI"):
            d = [k for k in ky if k["rejim"] == r]
            rr[r] = dilim_rapor(d, r, "R")
        print()
        print("  --- ikincil olcu net%, rejime gore ---")
        nn = {}
        for r in ("BOGA", "NOTR", "AYI"):
            d = [k for k in ky if k["rejim"] == r]
            nn[r] = dilim_rapor(d, r, "net")
        print()

        if not birincil:
            continue

        boga = [k for k in ky if k["rejim"] == "BOGA"]
        if len(boga) < 40:
            print("  BOGA dilimi yetersiz -> HUKUM YOK\n")
            continue

        goz, gmax, p = permutasyon(boga, "R")
        print("  permutasyon (BOGA, isaret-cevirme, gun bazinda, %d tur):" % PERM)
        print("    gozlenen |t|: %s" % "  ".join("%s=%.2f" % (v, goz[v]) for v in VARYANT))
        print("    max|t| = %.2f   ->   p = %.4f" % (gmax, p))
        print()

        # ---- blok kirilimi (K2 icin, bloklar ON-KAYITTA sabit) ----
        print("  BOGA bloklari (K2 — bloklar on-kayitta sabitlendi):")
        blok = collections.defaultdict(list)
        for k in boga:
            b = blok_ata(k)
            if b:
                blok[b].append(k)
        blok_fark = {}
        for b in ("B1", "B2", "B3"):
            d = blok[b]
            if len(d) < 15:
                print("    %s  N=%-4d -> yetersiz" % (b, len(d)))
                blok_fark[b] = None
                continue
            satir = []
            bf = {}
            for v in VARYANT:
                m, _, _, _ = fark_satir(d, "R", v)
                bf[v] = m
                satir.append("%s %+.4f" % (v, m if m is not None else 0))
            blok_fark[b] = bf
            print("    %s  N=%-4d  %s" % (b, len(d), "  ".join(satir)))

        # ---- kullanicinin epizodu (BETIMLEYICI) ----
        ea, eb = gun_no(EPIZOT[0]), gun_no(EPIZOT[1])
        ep = [k for k in boga if ea <= k["gun"] <= eb]
        print()
        print("  KULLANICININ EPIZODU %s..%s (BETIMLEYICI, hukum YOK):" % EPIZOT)
        if len(ep) < 10:
            print("    N=%d — cok kucuk, sayi bile verilmez." % len(ep))
        else:
            print("    N=%d · %d gun" % (len(ep), len({k["gun"] for k in ep})))
            for ad, _ in KOLLAR:
                print("      %-6s net%% %+7.3f   R %+8.4f   stop-ol %%%.0f"
                      % (ad, stx.mean([k["kol"][ad]["net"] for k in ep]),
                         stx.mean([k["kol"][ad]["R"] for k in ep]),
                         sum(1 for k in ep if k["kol"][ad]["tip"] == "STOP") / len(ep) * 100))
            print("    ^ 5 gun · gun-kumeli cikarim YAPILAMAZ. Yalnizca goruntu.")

        # ---- HUKUM ----
        print()
        print("=" * 78)
        print("HUKUM — ON_KAYIT_stop_rejim.md bolum 6")
        print("=" * 78)
        rb = rr["BOGA"]
        aday = [(v, rb[v][0], rb[v][1]) for v in VARYANT
                if rb and rb[v][0] is not None and rb[v][0] > 0
                and rb[v][1] is not None and rb[v][1] >= 2.0]
        K1 = bool(aday) and p <= 0.05
        print("K1  BOGA'da R farki > 0 · t_gun >= +2.0 · permutasyon p <= 0.05")
        if not aday:
            print("    -> DUSTU: hicbir varyant t>=+2.0 ile pozitif degil")
        else:
            print("    aday: %s  ·  p=%.4f -> %s"
                  % (", ".join("%s (%+.4f, t=%+.2f)" % a for a in aday), p,
                     "GECTI" if K1 else "DUSTU (permutasyon)"))

        if K1:
            v = max(aday, key=lambda a: a[2])[0]
            isar = [blok_fark[b][v] for b in ("B1", "B2", "B3")
                    if blok_fark.get(b) and blok_fark[b].get(v) is not None]
            K2 = sum(1 for x in isar if x > 0) >= 2
            print("K2  uc buyuk BOGA blogunun >=2'sinde ayni isaret: %s -> %s"
                  % (["%+.4f" % x for x in isar], "GECTI" if K2 else "DUSTU"))
            i = VARYANT.index(v)
            koms = [VARYANT[j] for j in (i - 1, i + 1) if 0 <= j < len(VARYANT)]
            K3 = any(rb[cc][0] is not None and rb[cc][0] > 0 for cc in koms)
            print("K3  komsu hucre ayni isaret: %s -> %s"
                  % (", ".join("%s=%+.4f" % (cc, rb[cc][0]) for cc in koms),
                     "GECTI" if K3 else "DUSTU"))
            nb = rr["NOTR"][v][0] if rr["NOTR"] else None
            K4 = (nb is not None and rb[v][0] - nb > 0)
            print("K4  (BOGA farki) - (NOTR farki) > 0: %+.4f - %+.4f = %+.4f -> %s"
                  % (rb[v][0], nb if nb is not None else 0,
                     (rb[v][0] - nb) if nb is not None else 0, "GECTI" if K4 else "DUSTU"))
            print("\nSONUC: %s" % ("GECTI" if (K2 and K3 and K4) else
                                   ("ZAYIF" if K2 else "DUSTU")))
        else:
            print("K2/K3/K4 uygulanmadi (K1 dustu)")
            # K4 yine de BILGI olarak yazilir — on-kaydin kalbi bu soru
            print()
            print("K4 sorusu yine de raporlanir (BILGI, hukum degil):")
            for v in VARYANT:
                b_ = rr["BOGA"][v][0] if rr["BOGA"] else None
                n_ = rr["NOTR"][v][0] if rr["NOTR"] else None
                if b_ is None or n_ is None:
                    continue
                ayni = "AYNI yon" if b_ * n_ > 0 else "AYRISIYOR"
                print("    %-6s BOGA %+9.4f  NOTR %+9.4f  fark %+9.4f  -> %s"
                      % (v, b_, n_, b_ - n_, ayni))
            print("\nSONUC: DUSTU")

    # ---- IKINCIL: 2R hedef, rejime gore (tahmin 4) ----
    print()
    print("=" * 78)
    print("IKINCIL (on-kayitli, BETIMLEYICI): hedef = 2 x risk, rejime gore")
    print("=" * 78)
    k2, _, _ = sm.tara(iki_r=True)
    for evren in ("A_funding",):
        ky = k2[evren]
        for r in ("BOGA", "NOTR", "AYI"):
            d = [k for k in ky if k["rejim"] == r]
            if len(d) < 40:
                print("  %s / %s: N=%d yetersiz" % (evren, r, len(d)))
                continue
            print("  %s / %s   N=%d" % (evren, r, len(d)))
            for ad, _ in KOLLAR:
                print("      %-6s R %+8.4f   hedef %%%.0f   stop-ol %%%.0f"
                      % (ad, stx.mean([k["kol"][ad]["R"] for k in d]),
                         sum(1 for k in d if k["kol"][ad]["tip"] == "HEDEF") / len(d) * 100,
                         sum(1 for k in d if k["kol"][ad]["tip"] == "STOP") / len(d) * 100))
    print()
    print("Veri indirme: YOK · Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
