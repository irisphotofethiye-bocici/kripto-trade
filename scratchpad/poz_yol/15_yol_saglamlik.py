#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""YOL BULGULARININ SAGLAMLIGI — yaslanmadan once sina.

Holdout dersini kendi bulgularima uyguluyorum: 12/13_holdout'ta DORT hukum de
'en iyi 3 sembol cikinca' testinde coktu. 01_yol.py'nin bulgulari (stopun
kazananlari kesmesi, kar geri verme) ayni teste tabi tutulmadan HUKUM OLMAZ.

SINANAN:
  1. "Stoplularin %68'i once >%1 kara gecmisti"
  2. "Kar geri verme: tepenin medyan %157'si"
  3. "TP2 tepe konumu 1,00 vs STOP 0,43"
Her biri icin: sembol yogunlasmasi · gun yogunlasmasi · zaman yarilari.

⚠️ FARK: bunlar GETIRI ortalamasi degil, DAGILIM ozellikleri. Yogunlasmaya
   getiri ortalamasi kadar duyarli olmalari beklenmez — ama SINANMADAN
   varsayilmaz.

SALT OKUMA.
"""
import os, sys, collections, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ortak                                                    # noqa: E402


def olc(p):
    s = p["seri"]
    pnl = [g.get("pnl_pct") for g in s if g.get("pnl_pct") is not None]
    if len(pnl) < 5:
        return None
    tepe = max(pnl)
    return {"sym": p["sym"], "sebep": p["sonuc"]["sebep"], "net": p["sonuc"]["net_usdt"],
            "tepe": tepe, "son": pnl[-1], "geri": tepe - pnl[-1],
            "konum": pnl.index(tepe) / max(1, len(pnl) - 1),
            "gun": s[0]["ts"][:10], "yon": p["yon"]}


def bolum(v, ad):
    stoplu = [x for x in v if "STOP" in (x["sebep"] or "")]
    kara = [x for x in v if x["tepe"] > 0]
    r = {}
    if stoplu:
        r["stop_kara_gecen"] = 100 * sum(1 for x in stoplu if x["tepe"] >= 1.0) / len(stoplu)
        r["stop_konum"] = sx.median([x["konum"] for x in stoplu])
    if kara:
        o = [x["geri"] / x["tepe"] for x in kara if x["tepe"] > 0.1]
        if o:
            r["geri_oran"] = 100 * sx.median(o)
    tp = [x for x in v if (x["sebep"] or "").startswith("TP2")]
    if tp:
        r["tp2_konum"] = sx.median([x["konum"] for x in tp])
    print("  %-34s N=%-4d  stop>%%1-kara %s  stop-konum %s  geri-veri %s  TP2-konum %s"
          % (ad, len(v),
             "%%%.0f" % r["stop_kara_gecen"] if "stop_kara_gecen" in r else "-",
             "%.2f" % r["stop_konum"] if "stop_konum" in r else "-",
             "%%%.0f" % r["geri_oran"] if "geri_oran" in r else "-",
             "%.2f" % r["tp2_konum"] if "tp2_konum" in r else "-"))
    return r


if __name__ == "__main__":
    poz = ortak.pozisyonlar(en_az_goruntu=10, zengin=False)
    v = [z for z in (olc(p) for p in poz) if z]
    print("=" * 104)
    print("YOL BULGULARI — YOGUNLASMA SINAVI   N=%d pozisyon" % len(v))
    print("=" * 104)
    tam = bolum(v, "TAM ORNEKLEM")

    # sembol yogunlasmasi
    g = collections.Counter(x["sym"] for x in v)
    en = [s for s, _ in g.most_common(3)]
    print("\n  en cok tekrar eden 3 sembol: %s" % ", ".join("%s(%d)" % (s, g[s]) for s in en))
    bolum([x for x in v if x["sym"] not in en], "3 sembol CIKINCA")

    # net'e gore en buyuk 3 katki
    kn = collections.defaultdict(float)
    for x in v:
        kn[x["sym"]] += x["net"]
    enk = [s for s, _ in sorted(kn.items(), key=lambda z: -abs(z[1]))[:3]]
    print("\n  net'e en cok katki: %s" % ", ".join("%s(%+.0f)" % (s, kn[s]) for s in enk))
    bolum([x for x in v if x["sym"] not in enk], "en buyuk 3 katki CIKINCA")

    # gun yogunlasmasi
    gd = collections.Counter(x["gun"] for x in v)
    eng = gd.most_common(1)[0][0]
    print("\n  en yogun gun: %s (%d pozisyon)" % (eng, gd[eng]))
    bolum([x for x in v if x["gun"] != eng], "en yogun gun CIKINCA")

    # zaman yarilari
    gunler = sorted({x["gun"] for x in v})
    orta = gunler[len(gunler) // 2]
    print("\n  zaman yarilari (bolen %s):" % orta)
    bolum([x for x in v if x["gun"] <= orta], "  A yarisi")
    bolum([x for x in v if x["gun"] > orta], "  B yarisi")

    # yon ayrimi
    print("\n  yon ayrimi:")
    bolum([x for x in v if x["yon"] == "SHORT"], "  SHORT")
    bolum([x for x in v if x["yon"] == "LONG"], "  LONG")

    print("\nbot dosyalarina yazim: YOK")
