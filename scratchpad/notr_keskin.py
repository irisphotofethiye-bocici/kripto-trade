# -*- coding: utf-8 -*-
"""NOTR hukmu KESKIN HAREKET anlarinda da gecerli mi? (2026-08-19)

BAGLAM: rejim etiketi BTC'nin 30 GUNLUK getirisine bakiyor (>=+15 BOGA).
Su an 30g +5,11% -> NOTR. Ama 3 gunluk +8,95%, 24 saatlik +6,41%.
Kullanici itirazi: "bir anda 70'e firladi, bu pek notr degil". HAKLI SORU.

YONTEM — esik SECILMEZ: NOTR gozlemleri, o andaki BTC 3 GUNLUK getirisine
gore UCE bolunur (terciles). Her dilimde frenin lifti ayri olculur.
Esik taramasi YOK, en iyi hucre secimi YOK — uc dilim de raporlanir.

ISTATISTIK: AY-KUMELI (bu aksam ogrenilen ders — piyasa-seviyesi sinyalde
bagimsiz birim sembol-saat degil TAKVIM DONEMI).
"""
import sys, os, json, collections, statistics as stx, datetime, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import btcpay_fren_rejim as F
import ileri_rr as ir


def btc_3g():
    """saat -> BTC'nin onceki 72 saatteki getirisi (%)."""
    b = json.load(open(os.path.join(ir.KLINE, "BTC.json"), encoding="utf-8"))
    c = {x["t"] // 3600000: x["c"] for x in b}
    ks = sorted(c)
    out = {}
    for i, k in enumerate(ks):
        if i >= 72 and c[ks[i - 72]] > 0:
            out[k] = (c[k] / c[ks[i - 72]] - 1) * 100
    return out


def ay(ts):
    return datetime.datetime.fromtimestamp(ts / 1000, datetime.timezone.utc).strftime("%Y-%m")


def kumeli(pa, da):
    """ay-kumeli lift + t. pa/da: liste[(net, sym, ts)]"""
    ap, ad = collections.defaultdict(list), collections.defaultdict(list)
    for n, s, t in pa:
        ap[ay(t)].append(n)
    for n, s, t in da:
        ad[ay(t)].append(n)
    ok = [k for k in set(ap) & set(ad) if len(ap[k]) >= 20 and len(ad[k]) >= 20]
    if len(ok) < 3:
        return None
    v = [stx.mean(ap[k]) - stx.mean(ad[k]) for k in ok]
    se = stx.stdev(v) / len(v) ** 0.5
    return (stx.mean(v), stx.mean(v) / se if se else 0.0, len(ok),
            sum(1 for x in v if x > 0))


b3 = btc_3g()
print("NOTR hukmu KESKIN HAREKET anlarinda da gecerli mi?")
print("=" * 76)
print("Bugunun konumu: BTC 30g +5,11%% (NOTR) · 3g +8,95%%")
print("Yontem: NOTR gozlemleri BTC 3g getirisine gore UCE bolunur (esik secilmez)")
print("Istatistik: AY-KUMELI\n")

for tohum in (41, 7):
    random.seed(tohum)
    h, _ = F.kostur()
    p = [z for z in h.get(("NOTR", "UST"), []) if z[2] // 3600000 in b3]
    d = [z for z in h.get(("NOTR", "diger"), []) if z[2] // 3600000 in b3]
    hep = sorted(b3[z[2] // 3600000] for z in p + d)
    k1, k2 = hep[len(hep) // 3], hep[2 * len(hep) // 3]
    print("--- tohum %d   dilim sinirlari: BTC 3g  %+.2f%%  ve  %+.2f%%" % (tohum, k1, k2))
    for ad_, lo, hi in (("DUSUK  (BTC 3g <%+.1f)" % k1, -1e9, k1),
                        ("ORTA", k1, k2),
                        ("YUKSEK (BTC 3g >%+.1f)" % k2, k2, 1e9)):
        pa = [z for z in p if lo <= b3[z[2] // 3600000] < hi]
        da = [z for z in d if lo <= b3[z[2] // 3600000] < hi]
        if len(pa) < 40 or len(da) < 40:
            print("    %-26s N yetersiz (%d/%d)" % (ad_, len(pa), len(da)))
            continue
        ham = stx.mean([z[0] for z in pa]) - stx.mean([z[0] for z in da])
        km = kumeli(pa, da)
        if km is None:
            print("    %-26s ham lift %+6.3f%%  (ay kirilimi yapilamadi)" % (ad_, ham))
            continue
        li, t, na, pz = km
        print("    %-26s N=%5d/%5d  ham %+6.3f%%  AY-KUMELI lift %+6.3f%% t=%+5.2f  (%d ay, %d/%d poz) %s"
              % (ad_, len(pa), len(da), ham, li, t, na, pz, na,
                 "" if abs(t) >= 2 else "<-- gurultu"))
    print()


# --- EK: BUGUN nerede duruyor? Ucte-bir dilimi bizi gercekten kapsiyor mu? ---
print("=" * 76)
print("BUGUN (+8,95%) BU DAGILIMIN NERESINDE?")
random.seed(41)
h, _ = F.kostur()
p = [z for z in h.get(("NOTR", "UST"), []) if z[2] // 3600000 in b3]
d = [z for z in h.get(("NOTR", "diger"), []) if z[2] // 3600000 in b3]
hep = sorted(b3[z[2] // 3600000] for z in p + d)
BUGUN = 8.95
alt = sum(1 for v in hep if v <= BUGUN)
print("  NOTR gozlemlerinin %%%.1f'i bugunkunden DUSUK bir BTC 3g getirisinde"
      % (100 * alt / len(hep)))
print("  dagilim: %%10 %+.2f · %%50 %+.2f · %%90 %+.2f · %%95 %+.2f · en yuksek %+.2f"
      % (hep[len(hep)//10], hep[len(hep)//2], hep[int(len(hep)*.9)],
         hep[int(len(hep)*.95)], hep[-1]))
print()
print("  UST DILIM (en yuksek %10) — bugunku duruma en yakin kume:")
esik = hep[int(len(hep) * .9)]
pa = [z for z in p if b3[z[2] // 3600000] >= esik]
da = [z for z in d if b3[z[2] // 3600000] >= esik]
if len(pa) < 40 or len(da) < 40:
    print("    N YETERSIZ (%d / %d) -> bu bolgede HUKUM YOK" % (len(pa), len(da)))
else:
    ham = stx.mean([z[0] for z in pa]) - stx.mean([z[0] for z in da])
    km = kumeli(pa, da)
    if km is None:
        print("    N=%d/%d ham lift %+.3f%% — ay kirilimi yapilamadi (yeterli ay yok)"
              % (len(pa), len(da), ham))
    else:
        li, t, na, pz = km
        print("    N=%d/%d  ham %+.3f%%  AY-KUMELI lift %+.3f%%  t=%+.2f  (%d ay, %d/%d poz) %s"
              % (len(pa), len(da), ham, li, t, na, pz, na,
                 "<-- gurultu" if abs(t) < 2 else ""))
