# -*- coding: utf-8 -*-
"""TOHUM KARARLILIGI — faz kaydirma rastgele, hukumler buna dayaniyor mu?

KUSUR: btcpay_rejim.py / btcpay_fren_rejim.py sembol basina RASTGELE faz
kaydiriyor (SEYRELT=24 faz kilidini kirmak icin). random.seed modul
duzeyinde, yani ayni surecte iki olcum kosunca akislar farkli. Olculdu:
LONG/NOTR bu sabah +0,306 (t=+3,13), ayni kod bugun aksam +0,124 (t=+1,31).

SORU: AY-KUMELI hukumler tohuma duyarli mi? Uc tohumda tekrarlanir.
"""
import sys, os, random, collections, statistics as stx, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import btcpay_fren_rejim as F
import btcpay_rejim as bp


def ay(ts):
    return datetime.datetime.fromtimestamp(ts / 1000, datetime.timezone.utc).strftime("%Y-%m")


def ozet(hucre, pen, dig):
    out = {}
    for r in ("AYI", "NOTR", "BOGA"):
        p, d = hucre.get((r, pen), []), hucre.get((r, dig), [])
        if len(p) < 40 or len(d) < 40:
            out[r] = None
            continue
        ap, ad = collections.defaultdict(list), collections.defaultdict(list)
        for n, s, t in p:
            ap[ay(t)].append(n)
        for n, s, t in d:
            ad[ay(t)].append(n)
        ok = [k for k in set(ap) & set(ad) if len(ap[k]) >= 20 and len(ad[k]) >= 20]
        if len(ok) < 2:
            out[r] = None
            continue
        v = [stx.mean(ap[k]) - stx.mean(ad[k]) for k in ok]
        se = stx.stdev(v) / len(v) ** 0.5
        ham = stx.mean([z[0] for z in p]) - stx.mean([z[0] for z in d])
        out[r] = (ham, stx.mean(v) / se if se else 0.0, len(ok),
                  sum(1 for x in v if x > 0))
    return out


print("%-6s %-6s %-8s %10s %10s %8s %8s" %
      ("olcum", "rejim", "tohum", "ham lift", "AY-KUMELI t", "ay", "poz"))
print("-" * 66)
for tohum in (41, 7, 99):
    for ad_, mod, pen, dig in (("SHORT", F, "UST", "diger"),
                               ("LONG", bp, "UST+durgun", "diger")):
        random.seed(tohum)
        h, _ = mod.kostur()
        o = ozet(h, pen, dig)
        for r in ("AYI", "NOTR", "BOGA"):
            if o[r] is None:
                print("%-6s %-6s %-8d %10s %10s" % (ad_, r, tohum, "-", "N yetersiz"))
            else:
                ham, tk, na, pz = o[r]
                print("%-6s %-6s %-8d %+10.3f %+10.2f %8d %8s %s"
                      % (ad_, r, tohum, ham, tk, na, "%d/%d" % (pz, na),
                         "" if abs(tk) >= 2 else "<-- gurultu"))
    print("-" * 66)
