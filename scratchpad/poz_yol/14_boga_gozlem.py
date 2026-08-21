#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASAMA A — BOGA REJIMI CANLI GOZLEM.

NEDEN ACIL: bot 2026-07-23'ten beri kosuyor ve 29 gunde BOGA rejimini HIC
gormedi (149 pozisyon: AYI 5 · NOTR 144 · BOGA 0). karar_yon'un BOGA dali
2026-08-21 03:46'da ILK KEZ calisti. Bu pencere kapanirsa bir daha ne zaman
gelecegi belli degil.

BU BETIK OLCMEZ, KAYDEDER. Hukum yazmaz — N cok kucuk. Tekrar tekrar
calistirilir, birikimi gosterir.

KIYAS: ayni sorulara NOTR rejimindeki cevap yan yana konur, boylece BOGA
dalinin NE FARK YARATTIGI gorulur.

SALT OKUMA.
"""
import os, json, collections, statistics as sx

PROJE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADAY = os.path.join(PROJE, "testbot_aday_arsiv.jsonl")
VETO = os.path.join(PROJE, "veto_log.jsonl")
ISLEM = os.path.join(PROJE, "testbot_islemler.jsonl")
STATE = os.path.join(PROJE, "testbot_state.json")


def satirlar(yol):
    out = []
    try:
        with open(yol, encoding="utf-8") as f:
            for s in f:
                if s.strip():
                    try:
                        out.append(json.loads(s))
                    except Exception:
                        pass
    except Exception:
        pass
    return out


def yon_of(karar):
    if not karar:
        return None
    if karar.startswith("LONG"):
        return "LONG"
    if karar.startswith("SHORT"):
        return "SHORT"
    return None


def karar_tablosu(kayitlar, ad):
    n = len(kayitlar)
    if not n:
        print("  %-12s kayit YOK" % ad)
        return
    y = collections.Counter(yon_of(x.get("karar")) for x in kayitlar)
    lg, sh = y.get("LONG", 0), y.get("SHORT", 0)
    karar_var = lg + sh
    veto = sum(1 for x in kayitlar if str(x.get("karar", "")).startswith("VETO"))
    print("  %-12s aday %6d · karar %5d (LONG %4d · SHORT %4d) · LONG payi %s · veto %d"
          % (ad, n, karar_var, lg, sh,
             "%%%.0f" % (100 * lg / karar_var) if karar_var else "-", veto))


def chg24_dagilim(kayitlar, ad):
    v = [x["chg24"] for x in kayitlar if x.get("chg24") is not None]
    if len(v) < 5:
        print("  %-22s N=%d yetersiz" % (ad, len(v)))
        return
    v.sort()
    print("  %-22s N=%4d · medyan %+6.1f%% · %%25 %+6.1f · %%75 %+6.1f · >=%%20 olan %d"
          % (ad, len(v), sx.median(v), v[len(v) // 4], v[3 * len(v) // 4],
             sum(1 for x in v if x >= 20)))


if __name__ == "__main__":
    aday = satirlar(ADAY)
    veto = satirlar(VETO)
    islem = satirlar(ISLEM)
    st = json.load(open(STATE, encoding="utf-8"))

    boga = [x for x in aday if x.get("rejim") == "BOGA"]
    notr = [x for x in aday if x.get("rejim") == "NOTR"]

    print("=" * 96)
    print("BOGA REJIMI CANLI GOZLEM")
    print("=" * 96)
    if not boga:
        print("Henuz BOGA kaydi yok.")
        raise SystemExit(0)
    print("BOGA penceresi : %s  ->  %s   (%d aday kaydi)"
          % (boga[0]["ts"], boga[-1]["ts"], len(boga)))
    print("NOTR karsilastirmasi: %d aday kaydi" % len(notr))

    print("\n1) KARAR DAGILIMI — BOGA dali NE FARK YARATIYOR")
    karar_tablosu(boga, "BOGA")
    karar_tablosu(notr, "NOTR")

    print("\n2) LONG KARARLARININ chg24 DAGILIMI")
    print("   (2 yillik olcumde tek canli LONG hucresi chg24>%40 idi;")
    print("    holdout'ta o da coktu -> burada sadece KAYIT tutuluyor)")
    chg24_dagilim([x for x in boga if yon_of(x.get("karar")) == "LONG"], "BOGA LONG kararlari")
    chg24_dagilim([x for x in notr if yon_of(x.get("karar")) == "LONG"], "NOTR LONG kararlari")
    chg24_dagilim([x for x in boga if yon_of(x.get("karar")) == "SHORT"], "BOGA SHORT kararlari")

    print("\n3) VETOLAR — BOGA penceresinde")
    bv = [x for x in veto if x.get("ts", "") >= boga[0]["ts"]]
    if bv:
        c = collections.Counter(x.get("kategori") for x in bv)
        for k, n in c.most_common():
            print("  %-16s %d" % (k, n))
        bl = [x for x in bv if x.get("kategori") == "blowoff"]
        if bl:
            print("  blowoff'un kestigi yon: %s"
                  % dict(collections.Counter(x.get("olurdu_yon") for x in bl)))
    else:
        print("  BOGA penceresinde veto kaydi YOK")

    print("\n4) BOGA'DA ACILAN POZISYONLAR")
    acik = [p for p in st["acik_pozisyonlar"] if p.get("rejim_giriste") == "BOGA"]
    g = collections.defaultdict(list)
    for x in islem:
        g[x["id"]].append(x)
    kapali = [v for v in g.values() if v[0].get("rejim_giriste") == "BOGA"]
    print("  ACIK  : %d" % len(acik))
    for p in acik:
        print("     %-9s %-5s giris %s · chg24@g %+.1f%% · smart %s"
              % (p["sym"], p["yon"], p["giris_ts"][5:16], p.get("chg24_giriste") or 0,
                 p.get("smart_giriste")))
    print("  KAPALI: %d" % len(kapali))
    for v in kapali:
        net = sum(t.get("sonuc_usdt") or 0 for t in v)
        print("     %-9s %-5s %+8.2f$ · %s · chg24@g %+.1f%%"
              % (v[0]["sym"], v[0]["yon"], net, v[-1]["sebep"], v[0].get("chg24_giriste") or 0))

    print("\n5) OMUR BOYU REJIM x YON KARNESI")
    tab = collections.defaultdict(lambda: [0, 0.0])
    for v in g.values():
        k = (v[0].get("rejim_giriste", "?"), v[0]["yon"])
        tab[k][0] += 1
        tab[k][1] += sum(t.get("sonuc_usdt") or 0 for t in v)
    print("  %-12s %-6s %5s %11s" % ("rejim", "yon", "N", "net $"))
    for k in sorted(tab):
        print("  %-12s %-6s %5d %+11.2f" % (k[0], k[1], tab[k][0], tab[k][1]))

    print("\nHUKUM YAZILMADI — N cok kucuk. Bu bir KAYITTIR.")
    print("bot dosyalarina yazim: YOK")
