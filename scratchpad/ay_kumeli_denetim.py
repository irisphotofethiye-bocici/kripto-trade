# -*- coding: utf-8 -*-
"""AY-KUMELI DENETIM — bugunku IKI btc_pay olcumunun TUM hucreleri.

POST-HOC, on-kayitta yoktu. Amac: "sadece hosuma gitmeyen sonucu elemek"
suclamasini imkansiz kilmak. Ayni kontrol AYNEN her hucreye uygulanir.

SORU: bu hucrelerdeki N (binlerce gozlem) BAGIMSIZ mi? Rejim epizotlari
takvimde kumelenir; ayni ay icindeki 900 gozlem 900 bagimsiz kanit degildir.
  - ay ay lift
  - baskin ay (lifte en cok agirlikli katki) atilinca ne kaliyor
  - bagimsiz birim AY alinirsa t
"""
import sys, os, collections, statistics as stx, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import btcpay_fren_rejim as F
import btcpay_rejim as bp


def ay(ts):
    return datetime.datetime.fromtimestamp(ts / 1000, datetime.timezone.utc).strftime("%Y-%m")


def denetle(baslik, hucre, pencere_ad, diger_ad):
    print("\n" + "=" * 76)
    print(baslik)
    print("=" * 76)
    for r in ("AYI", "NOTR", "BOGA"):
        p = hucre.get((r, pencere_ad), [])
        d = hucre.get((r, diger_ad), [])
        if len(p) < 40 or len(d) < 40:
            print("\n--- %s : N yetersiz" % r)
            continue
        ap, ad = collections.defaultdict(list), collections.defaultdict(list)
        for n, s, t in p:
            ap[ay(t)].append(n)
        for n, s, t in d:
            ad[ay(t)].append(n)
        ort = bp.iki_ornek([z[0] for z in p], [z[0] for z in d])
        ok = [k for k in set(ap) & set(ad) if len(ap[k]) >= 20 and len(ad[k]) >= 20]
        li = {k: stx.mean(ap[k]) - stx.mean(ad[k]) for k in ok}
        kat = {k: li[k] * len(ap[k]) for k in ok}
        print("\n--- %s   ham lift %+7.3f%%  (gozlem-t %+6.2f)  N=%d/%d"
              % (r, ort[0], ort[1], len(p), len(d)))
        if not ok:
            print("    ay kirilimi yapilamadi")
            continue
        print("    ayrik ay: %d   ay lifti: %s" % (len(ok), ", ".join(
            "%s %+.2f" % (k, li[k]) for k in sorted(ok))))
        v = list(li.values())
        poz = sum(1 for x in v if x > 0)
        print("    AY duzeyi -> ortalama %+7.3f · medyan %+7.3f · pozitif %d/%d"
              % (stx.mean(v), stx.median(v), poz, len(v)))
        if len(v) > 1:
            se = stx.stdev(v) / len(v) ** 0.5
            tk = stx.mean(v) / se if se else 0.0
            print("    AY-KUMELI t = %+6.2f %s" % (tk, "<-- GURULTU" if abs(tk) < 2 else "<-- ayakta"))
        bas = max(kat, key=lambda k: abs(kat[k]))
        qa = [n for k, vv in ap.items() if k != bas for n in vv]
        qb = [n for k, vv in ad.items() if k != bas for n in vv]
        if len(qa) >= 40 and len(qb) >= 40:
            f2, t2 = bp.iki_ornek(qa, qb)
            ayni = (f2 >= 0) == (ort[0] >= 0)
            print("    baskin ay %s (katki %+.0f) ATILINCA -> lift %+7.3f%%  t %+6.2f  isaret %s"
                  % (bas, kat[bas], f2, t2, "AYNI" if ayni else "DONDU"))


hs, _ = F.kostur()
denetle("1) SHORT bacagi (FRENIN KENDISI) — bugunku on-kayitli olcum", hs, "UST", "diger")
hl, _ = bp.kostur()
denetle("2) LONG bacagi — bugun olculdu, '21 Agustos BOGA HARIC' kararinin dayanagi",
        hl, "UST+durgun", "diger")
