#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""btc_pay LONG PENCERESI REJIMDEN BAGIMSIZ MI? - 2 yillik VEKIL sinav (2026-08-19)

ON-KAYIT: olcumler.md (commit a1b39d8, KOSTURULMADAN ONCE yazildi).
Olcut metnini degistirmez, parametre taramaz.

SORU: btc_pay'in LONG bacagi (UST + para durgun -> LONG R +0,24/+0,16, gercek
holdout) koda rejim_ad=="AYI" kolunun ICINE konmus (testbot.py:559). Olcumun
kendi tanimi ise piyasa seviyesinde: "T-B PIYASA-SEVIYESI bir IZIN penceresidir".
Kilit hakli mi?

VEKIL - dayanak dosyalar (PARA_SONUC.md, CIKIS_SONUC.md) KAYIP. Iki gosterge
2 yillik mumlardan yeniden kuruldu ve gercek loglarla dogrulandi:
  btc_d_xs 3g   = BTC_3g - sepet MEDYAN 3g            r=+0,680  isaret %72
  para_rejim 7g = 0,56*BTC_7g + 0,44*sepet MEDYAN 7g  r=+0,882  isaret %86

!!! MEDYAN ZORUNLU !!! Ortalama denendi ve sifira yakin fiyatli tokenlerde
patladi: r +0,680 -> +0,025, aykiri deger -38.275. Bu satiri degistirme.
"""
import json, os, sys, statistics as stx, collections, random, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olcum_ortak as oo
import ileri_rr as ir

# --- DONDURULMUS PARAMETRELER (getiriye bakilmadan kalibre edildi, on-kayitli) ---
UST_ESIK = 2.8755
DUR_ALT, DUR_UST = -2.8046, 2.3766
SEPET_N, MIN_BAR = 60, 8000
HEDEF_PCT, UFUK = 10.0, 72
random.seed(41)


def stop_long(b, si, ref, a):
    """LONG icin aynalanmis A-stop (katilim_filtresi LONG testiyle ayni)."""
    bas = max(3, si - 100)
    lo = []
    for j in range(bas, si - 2):
        w = b[j - 3:j + 4]
        if w and b[j]["l"] == min(x["l"] for x in w):
            lo.append(b[j]["l"])
    sup = max([x for x in lo if x < ref], default=None)
    ad = []
    if sup is not None and (ref - sup) <= 3 * a:
        ad.append(sup - 0.25 * a)
    nb = min(x["l"] for x in b[max(0, si - 10):si + 1])
    if nb < ref:
        ad.append(nb - 0.25 * a)
    ad.append(ref - 1.5 * a)
    gec = [s for s in ad if s < ref]
    return max(gec) if gec else ref - 1.5 * a


def gostergeler():
    """-> (vekil_xs, vekil_para): saat -> deger."""
    btc = json.load(open(os.path.join(ir.KLINE, "BTC.json"), encoding="utf-8"))
    bts = {x["t"] // 3600000: x["c"] for x in btc}
    hac = []
    for fn in sorted(os.listdir(ir.KLINE)):
        if not fn.endswith(".json") or fn == "BTC.json":
            continue
        try:
            b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < MIN_BAR:
            continue
        hac.append((stx.median([x.get("qv") or 0 for x in b[-500:]]), fn, b))
    hac.sort(reverse=True)
    ser = collections.defaultdict(dict)
    for _, fn, b in hac[:SEPET_N]:
        for x in b:
            if x["c"] > 0:
                ser[x["t"] // 3600000][fn] = x["c"]
    ortak = sorted(k for k in ser if len(ser[k]) >= 40 and k in bts)

    def kur(geri, agirlikli):
        out = {}
        for i, k in enumerate(ortak):
            if i < geri:
                continue
            k0 = ortak[i - geri]
            if k0 not in bts:
                continue
            bg = (bts[k] / bts[k0] - 1) * 100
            o = set(ser[k]) & set(ser[k0])
            if len(o) < 40:
                continue
            g = [(ser[k][s] / ser[k0][s] - 1) * 100 for s in o if ser[k0][s] > 0]
            if len(g) < 40:
                continue
            m = stx.median(g)                      # <-- MEDYAN, degistirme
            out[k] = (0.56 * bg + 0.44 * m) if agirlikli else (bg - m)
        return out

    return kur(72, False), kur(168, True)


def kostur():
    vx, vp = gostergeler()
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
        faz = random.randint(0, 23)        # FAZ KAYDIRMA - SEYRELT=24 faz kilidi
        for i in range(ir.ISINMA + faz, len(b) - UFUK - 2, ir.SEYRELT):
            x = b[i]
            if (x.get("qv") or 0) < ir.MIN_VOL / 24 or i < 24:
                continue
            sa = x["t"] // 3600000
            if sa not in vx or sa not in vp:
                continue
            gi = i + 1
            if not atrs[i] or gi >= len(b):
                continue
            ref = b[gi]["o"]
            if ref <= 0:
                continue
            stop = stop_long(b, i, ref, atrs[i])
            sp = (ref - stop) / ref * 100
            if sp <= 0 or sp < 2.0:
                continue
            son = min(gi + UFUK, len(b))
            if son - gi < 4:
                continue
            hedef = ref * (1 + HEDEF_PCT / 100)
            cj, ham = None, None
            for j in range(gi, son):
                if b[j]["l"] <= stop:
                    cj, ham = j, -sp
                    break
                if b[j]["h"] >= hedef:
                    cj, ham = j, HEDEF_PCT
                    break
            if cj is None:
                cj = son - 1
                ham = (b[son - 1]["c"] - ref) / ref * 100
            # LONG fonlama: oran POZITIFSE long ODER -> isaret ters cevrilir
            fon = -ir.fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
            net = ham - oo.MALIYET + fon
            pencere = (vx[sa] >= UST_ESIK) and (DUR_ALT <= vp[sa] <= DUR_UST)
            r = rej.get(sa, "NOTR")
            hucre[(r, "UST+durgun" if pencere else "diger")].append((net, sym, b[gi]["t"]))
    return hucre, islenen


def iki_ornek(a, b):
    """-> (fark, t). On-kayitta belirtilen IKI-ORNEKLEMLI istatistik."""
    ma, mb = stx.mean(a), stx.mean(b)
    sa = stx.pstdev(a) / len(a) ** 0.5 if len(a) > 1 else 0.0
    sb = stx.pstdev(b) / len(b) ** 0.5 if len(b) > 1 else 0.0
    s = math.sqrt(sa * sa + sb * sb)
    return ma - mb, ((ma - mb) / s if s else 0.0)


def rapor():
    print("btc_pay LONG PENCERESI REJIMDEN BAGIMSIZ MI? - 2 yillik VEKIL sinav")
    print("=" * 78)
    print("ON-KAYIT: olcumler.md (commit a1b39d8, kosturulmadan ONCE)")
    print("VEKIL: btc_d_xs r=+0,680 - para_rejim r=+0,882 (MEDYAN tabanli)")
    print("DONDURULMUS: UST_ESIK=%.4f  DUR=[%.4f , %.4f]" % (UST_ESIK, DUR_ALT, DUR_UST))
    print("Mekanik: LONG, aynalanmis A-stop, hedef +%s%%, %ss, maliyet+FONLAMA dahil\n"
          % (HEDEF_PCT, UFUK))
    hucre, islenen = kostur()
    print("islenen sembol: %d\n" % islenen)
    lift = {}
    for r in ("AYI", "NOTR", "BOGA"):
        p = hucre.get((r, "UST+durgun"), [])
        d = hucre.get((r, "diger"), [])
        if len(p) < 40 or len(d) < 40:
            print("--- %s : N YETERSIZ (pencere %d / diger %d)\n" % (r, len(p), len(d)))
            continue
        np_, nd = [z[0] for z in p], [z[0] for z in d]
        f, t = iki_ornek(np_, nd)
        print("--- %s %s" % (r, "-" * (62 - len(r))))
        print("  UST+durgun : N=%5d  %+7.3f%%   (ayri sembol %d)"
              % (len(np_), stx.mean(np_), len(set(z[1] for z in p))))
        print("  diger      : N=%5d  %+7.3f%%   (ayri sembol %d)"
              % (len(nd), stx.mean(nd), len(set(z[1] for z in d))))
        print("  LIFT       : %+7.3f%%   iki-ornekli t = %+5.2f" % (f, t))
        lift[r] = f
        srp = sorted(p, key=lambda z: z[2])
        srd = sorted(d, key=lambda z: z[2])
        y1, y2 = len(srp) // 2, len(srd) // 2
        for et, pp, dd in (("A yarisi", srp[:y1], srd[:y2]),
                           ("B yarisi", srp[y1:], srd[y2:])):
            if len(pp) >= 20 and len(dd) >= 20:
                ff, tt = iki_ornek([z[0] for z in pp], [z[0] for z in dd])
                print("    %s: lift %+7.3f%%  t=%+5.2f  (N %d vs %d)"
                      % (et, ff, tt, len(pp), len(dd)))
        print()
    if "AYI" in lift and "NOTR" in lift:
        ayni = (lift["AYI"] >= 0) == (lift["NOTR"] >= 0)
        print("OLCUT 4 -- AYI lifti %+.3f%%  ·  NOTR lifti %+.3f%%  ->  isaret %s"
              % (lift["AYI"], lift["NOTR"],
                 "AYNI" if ayni else "ZIT  (rejim kosulluluk DOGRULANIR, kilit HAKLI)"))


if __name__ == "__main__":
    rapor()
