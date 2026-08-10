#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GIRIS SIMULASYONU (2026-08-10) — tur-3 kurallariyla kac ISLEM acilirdi?

etki_tahmini.py "kac KARAR cikardi" diyordu; bu script "kac ISLEM ACILIRDI"
sorusunu cevaplar. Fark buyuk: ayni sembol ardisik turlarda tekrar tekrar karar
uretir (KMNO 90 dakikada 19 kez) ama bu TEK giris firsatidir.

BOT MEKANIGI AYNEN SIMULE EDILIR:
  - ONAY_BEKLE: aday BIR SONRAKI turda da listede olmali (cycle_sayaci>=1).
    SHORT icin ek sart: onay aninda taker < short_onay_taker_max (1.05).
    6 tur boyunca listede kalmazsa iptal.
  - ANINDA: hemen acilir.
  - Acik pozisyon varken ayni sembole ikinci giris YOK.
  - Kapanistan sonra 4 saat cooldown (_cikar_havuzdan).
  - Ayni anda en fazla maks_pozisyon (yeni: 8, eski: 4).
  - Tutma suresi: gercek defterin ORTALAMASI kullanilir (asagida hesaplanir).

OLCULEMEYEN (durustce ayri raporlanir):
  - R/R KAPISI: giris aninda olcucu ile bakilir; arsivde o veri YOK. Bu yuzden
    sonuc "R/R kapisi oncesi giris firsati" sayisidir. Kapinin gecirme orani
    ayrica CANLI olcuulur (asagida) ve aralik olarak raporlanir.
  - HAZIRLANIYOR sira bonusu: kisa listeye GIRME sansini artirir; arsivde
    olmayan aday simule edilemez -> gercek sayi buradan BUYUK olur.
"""
import json, os, sys, collections, datetime, statistics

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

ARSIV = os.path.join(HERE, "testbot_aday_arsiv.jsonl")
DEFTER = os.path.join(HERE, "testbot_islemler.jsonl")


def karar(r, yeni):
    """NOTR dali. Donus: (yon, mod, dal) | None.  yeni=False eski kural, True tur-3."""
    skor = r.get("score") or 0
    stage = r.get("stage")
    smart = r.get("smart")
    taker = r.get("taker")
    pos = r.get("pos", 0.5)
    chg24 = r.get("chg24") or 0.0
    oi24 = r.get("oi24") or 0.0
    short_riskli_dip = bool(r.get("dip_yakit") and r.get("dusuk_float"))

    asiri_yuk = chg24 >= 40.0
    asiri_dus = chg24 <= -40.0
    pumplamis = chg24 >= 20.0
    long_veto = (pos < 0.25 or asiri_dus or (chg24 < 0 and oi24 >= 15.0))
    stage_ok = stage in ("BASLIYOR", "HAZIRLANIYOR")
    esik = 40.0 if (yeni and stage == "HAZIRLANIYOR") else 45.0

    if stage_ok and skor >= esik:
        if smart == "LONG":
            if not (asiri_yuk or long_veto or (taker or 0) < 1.0):
                return ("LONG", "ONAY_BEKLE", "notr_long")
        if smart == "SHORT" and not short_riskli_dip and not asiri_dus:
            if not (yeni and pumplamis):
                return ("SHORT", "ANINDA", "smart-SHORT")
    if yeni and smart in (None, "NOTR") and skor >= 40.0:      # tur-3 fade dali (stage sartsiz)
        if pos >= 0.75 and not short_riskli_dip and not asiri_dus and not pumplamis:
            return ("SHORT", "ONAY_BEKLE", "NOTR-fade")
        if pos <= 0.40 and not asiri_yuk and not long_veto and (taker or 0) >= 1.0:
            return ("LONG", "ONAY_BEKLE", "NOTR-fade")
    return None


def simule(turlar, yeni, maks_poz, tutma_saat):
    acik = {}          # sym -> kapanis_zamani
    cooldown = {}      # sym -> cooldown bitisi
    bekleyen = {}      # sym -> {"yon","sayac"}
    girisler = []
    nedenler = collections.Counter()   # giris NEDEN olmadi
    for ts, adaylar in turlar:
        t = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M")
        for s, bitis in list(acik.items()):
            if t >= bitis:
                cooldown[s] = bitis + datetime.timedelta(hours=4)
                del acik[s]
        gorulen = {r["sym"] for r in adaylar}
        for s in list(bekleyen):
            if s not in gorulen:
                bekleyen[s]["sayac"] += 1
                if bekleyen[s]["sayac"] > 6:
                    del bekleyen[s]
        for r in adaylar:
            sym = r["sym"]
            k0 = karar(r, yeni)
            if len(acik) >= maks_poz:
                if k0: nedenler["maks_pozisyon dolu"] += 1
                break
            if sym in acik:
                if k0: nedenler["sembol zaten acik"] += 1
                continue
            if sym in cooldown and t < cooldown[sym]:
                if k0: nedenler["4s cooldown"] += 1
                continue
            k = k0
            if not k:
                bekleyen.pop(sym, None)
                continue
            yon, mod, dal = k
            if mod == "ANINDA":
                bekleyen.pop(sym, None)
                acik[sym] = t + datetime.timedelta(hours=tutma_saat)
                girisler.append({"ts": ts, "sym": sym, "yon": yon, "dal": dal})
                continue
            onceki = bekleyen.get(sym)
            if onceki and onceki["yon"] == yon:
                # SHORT onayinda taker sogumasi sarti (short_onay_taker_max=1.05)
                soguma_ok = (yon != "SHORT") or (r.get("taker") is None) or (r["taker"] < 1.05)
                if soguma_ok:
                    del bekleyen[sym]
                    acik[sym] = t + datetime.timedelta(hours=tutma_saat)
                    girisler.append({"ts": ts, "sym": sym, "yon": yon, "dal": dal})
                else:
                    nedenler["SHORT onayda taker sogumadi"] += 1
            else:
                bekleyen[sym] = {"yon": yon, "sayac": 0}
                nedenler["ONAY_BEKLE'ye alindi (ilk gorulme)"] += 1
    return girisler, nedenler


def main():
    rows = [json.loads(l) for l in open(ARSIV, encoding="utf-8") if l.strip()]
    gruplu = collections.OrderedDict()
    for r in rows:
        gruplu.setdefault(r["ts"], []).append(r)
    turlar = list(gruplu.items())
    ilk, son = turlar[0][0], turlar[-1][0]
    gun = (datetime.datetime.strptime(son, "%Y-%m-%d %H:%M")
           - datetime.datetime.strptime(ilk, "%Y-%m-%d %H:%M")).total_seconds() / 86400

    # gercek tutma suresi (defterden)
    try:
        isl = [json.loads(l) for l in open(DEFTER, encoding="utf-8") if l.strip()]
        tut = [t["tutma_saat"] for t in isl if not t.get("kismi") and t.get("tutma_saat")]
        tutma = statistics.median(tut) if tut else 6.0
    except Exception:
        tutma = 6.0

    print("=" * 74)
    print("GIRIS SIMULASYONU — tur-3 kurallariyla kac ISLEM acilirdi?")
    print("=" * 74)
    print(f"Pencere : {ilk}  ->  {son}   ({gun:.1f} gun, {len(turlar)} tur, {len(rows)} aday kaydi)")
    print(f"Tutma   : medyan {tutma:.1f} saat (gercek defterden)")
    print("UYARI   : aday arsivi 2026-08-04'te basladi -> 2 HAFTA VERISI YOK.")
    print()

    for ad, yeni, maks in (("ESKI kural (maks 4 pozisyon)", False, 4),
                           ("TUR-3 kurallari (maks 8 pozisyon)", True, 8)):
        g, nd = simule(turlar, yeni, maks, tutma)
        yon = collections.Counter(x["yon"] for x in g)
        dal = collections.Counter(x["dal"] for x in g)
        sym = collections.Counter(x["sym"] for x in g)
        print(f"--- {ad} ---")
        print(f"  GIRIS: {len(g)}  ({len(g)/gun:.1f}/gun · {len(g)/gun*14:.0f}/2 hafta)")
        print(f"  yon  : {dict(yon)}")
        print(f"  dal  : {dict(dal)}")
        print(f"  ayri sembol: {len(sym)} -> {', '.join(s for s, _ in sym.most_common(10))}")
        print("  GIRIS OLMAYAN karar-anlari (neden):")
        for k, v in nd.most_common():
            print(f"     {k:34} {v:5d}")
        print()

    print("NOT: Bu sayilar R/R KAPISI ONCESIDIR (arsivde olcucu verisi yok).")
    print("     Gercek acilan islem = bu sayi x R/R gecirme orani (ayrica olculuyor).")


if __name__ == "__main__":
    main()
