#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FRENIN KENDISI (btc_pay SHORT bacagi) REJIMDEN BAGIMSIZ MI? — 2 yillik VEKIL sinav

ON-KAYIT: olcumler.md -> "ON-KAYIT — FRENIN KENDISI ..." (commit 43d2cf5,
KOSTURULMADAN ONCE yazildi). Olcut metnini degistirmez, esik taramaz.

FRENIN IDDIASI: bant == UST iken SHORT kenari DUSUKTUR -> SHORT engellenmeli.
SORU: bu iddia BOGA rejiminde de gecerli mi? (Freni kuran olcumun 12 ayinin
tamami DUSEN piyasaydi ve bunu kendi notunda yaziyor.)

VEKIL: btc_d_xs 3g = BTC_3g - sepet MEDYAN 3g   (r=+0,680, isaret %72)
!!! MEDYAN ZORUNLU !!! Ortalama r=+0,025'e cokuyor (btcpay_rejim.py'de olculdu).

DONDURULMUS: UST_ESIK = 2.8755 — btcpay_rejim.py'nin LONG sinavindan AYNEN
alindi, yeniden kalibre EDILMEDI. para_durgun kosulu YOK (fren onu kullanmiyor).

MEKANIK: SHORT · botun A-varyanti stop · hedef -%10 · ufuk 72s ·
         maliyet + FONLAMA dahil · SEYRELT=24 + sembol basina FAZ KAYDIRMA
"""
import json, os, sys, statistics as stx, collections, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olcum_ortak as oo
import ileri_rr as ir
import btcpay_rejim as bp          # gostergeler() ve iki_ornek() yeniden kullanilir

UST_ESIK = 2.8755                  # DONDURULMUS — LONG sinaviyla ayni
HEDEF_PCT, UFUK = 10.0, 72
ASGARI_STOP = 2.0                  # botun kendi asgari stop esigi
random.seed(41)


def kostur():
    vx, _ = bp.gostergeler()       # yalniz btc_d_xs vekili; para_rejim GEREKMIYOR
    rej = ir.btc_rejim()
    hucre = collections.defaultdict(list)
    islenen = 0
    for fn in sorted(os.listdir(ir.KLINE)):
        if not fn.endswith(".json"):
            continue
        sym = fn[:-5]
        try:
            b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ir.ISINMA + UFUK + 50:
            continue
        fp = os.path.join(ir.FUND, fn)
        fr = []
        if os.path.exists(fp):
            try:
                fr = json.load(open(fp, encoding="utf-8"))
            except Exception:
                fr = []
        ft = [x["t"] for x in fr]
        atrs = ir.atr_serisi(b)
        islenen += 1
        faz = random.randint(0, 23)            # SEYRELT=24 faz kilidi kirilir
        for i in range(ir.ISINMA + faz, len(b) - UFUK - 2, ir.SEYRELT):
            x = b[i]
            if (x.get("qv") or 0) < ir.MIN_VOL / 24 or i < 24:
                continue
            sa = x["t"] // 3600000
            if sa not in vx:
                continue
            gi = i + 1
            if not atrs[i] or gi >= len(b):
                continue
            ref = b[gi]["o"]
            if ref <= 0:
                continue
            stop = ir.stop_hesapla(b, i, ref, atrs[i])      # SHORT stop (yukarida)
            sp = (stop - ref) / ref * 100
            if sp <= 0 or sp < ASGARI_STOP:
                continue
            son = min(gi + UFUK, len(b))
            if son - gi < 4:
                continue
            hedef = ref * (1 - HEDEF_PCT / 100)
            cj, ham = None, None
            for j in range(gi, son):
                if b[j]["h"] >= stop:
                    cj, ham = j, -sp
                    break
                if b[j]["l"] <= hedef:
                    cj, ham = j, HEDEF_PCT
                    break
            if cj is None:
                cj = son - 1
                ham = (ref - b[son - 1]["c"]) / ref * 100
            # SHORT fonlama: oran POZITIFSE short TAHSIL EDER -> isaret ceviRILMEZ
            fon = ir.fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
            net = ham - oo.MALIYET + fon
            r = rej.get(sa, "NOTR")
            hucre[(r, "UST" if vx[sa] >= UST_ESIK else "diger")].append((net, sym, b[gi]["t"]))
    return hucre, islenen


def rapor():
    print("FRENIN KENDISI (btc_pay SHORT bacagi) REJIMDEN BAGIMSIZ MI? - VEKIL sinav")
    print("=" * 78)
    print("ON-KAYIT: olcumler.md (commit 43d2cf5, kosturulmadan ONCE)")
    print("FRENIN IDDIASI: bant==UST -> SHORT kenari DUSUK (lift NEGATIF olmali)")
    print("DONDURULMUS: UST_ESIK=%.4f (LONG sinavindan aynen)" % UST_ESIK)
    print("Mekanik: SHORT, A-stop, hedef -%s%%, %ss, maliyet+FONLAMA dahil\n"
          % (HEDEF_PCT, UFUK))
    hucre, islenen = kostur()
    print("islenen sembol: %d\n" % islenen)
    lift, ayr = {}, {}
    for r in ("AYI", "NOTR", "BOGA"):
        p = hucre.get((r, "UST"), [])
        d = hucre.get((r, "diger"), [])
        if len(p) < 40 or len(d) < 40:
            print("--- %s : N YETERSIZ (UST %d / diger %d)\n" % (r, len(p), len(d)))
            continue
        np_, nd = [z[0] for z in p], [z[0] for z in d]
        f, t = bp.iki_ornek(np_, nd)
        print("--- %s %s" % (r, "-" * (62 - len(r))))
        print("  UST (frenlenen) : N=%5d  %+7.3f%%   (ayri sembol %d)"
              % (len(np_), stx.mean(np_), len(set(z[1] for z in p))))
        print("  diger (serbest) : N=%5d  %+7.3f%%   (ayri sembol %d)"
              % (len(nd), stx.mean(nd), len(set(z[1] for z in d))))
        print("  LIFT (UST-diger): %+7.3f%%   iki-ornekli t = %+5.2f   %s"
              % (f, t, "fren HAKLI" if f < 0 else "fren TERS"))
        lift[r] = (f, t)
        srp = sorted(p, key=lambda z: z[2])
        srd = sorted(d, key=lambda z: z[2])
        y1, y2 = len(srp) // 2, len(srd) // 2
        yari = []
        for et, pp, dd in (("A yarisi", srp[:y1], srd[:y2]),
                           ("B yarisi", srp[y1:], srd[y2:])):
            if len(pp) >= 20 and len(dd) >= 20:
                ff, tt = bp.iki_ornek([z[0] for z in pp], [z[0] for z in dd])
                yari.append(ff)
                print("    %s: lift %+7.3f%%  t=%+5.2f  (N %d vs %d)"
                      % (et, ff, tt, len(pp), len(dd)))
        ayr[r] = yari
        print()
    print("=" * 78)
    print("ON-KAYITLI OLCUT — BOGA hucresi")
    if "BOGA" not in lift:
        print("  BOGA hucresi N YETERSIZ -> HUKUM: belirsiz, fren OLDUGU GIBI kalir")
    else:
        f, t = lift["BOGA"]
        y = ayr.get("BOGA", [])
        h1 = f < 0
        h2 = len(y) == 2 and all(v < 0 for v in y)
        h3 = t < -2.0
        r1 = f > 0
        r2 = len(y) == 2 and all(v > 0 for v in y)
        r3 = t > 2.0
        print("  [fren BOGA'da HAKLI]  lift<0 %s · iki yari<0 %s · t<-2,0 %s"
              % (h1, h2, h3))
        print("  [fren BOGA'da ZARARLI] lift>0 %s · iki yari>0 %s · t>+2,0 %s"
              % (r1, r2, r3))
        if h1 and h2 and h3:
            print("  -> HUKUM: fren BOGA'da da HAKLI (rejim sinirlamasi GEREKMIYOR)")
        elif r1 and r2 and r3:
            print("  -> HUKUM: fren BOGA'da ZARARLI (rejim sinirlamasi onerisi 21-22'ye)")
        else:
            print("  -> HUKUM: BELIRSIZ — fren OLDUGU GIBI kalir")
    for r in ("AYI", "NOTR"):
        if r in lift:
            print("  [bilgi] %s lifti %+.3f%% (t=%+.2f)" % (r, lift[r][0], lift[r][1]))


if __name__ == "__main__":
    rapor()
