#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ÖRÜNTÜ RAPORU (2026-08-10) — oruntu_analiz.py'nin urettigi olay setini cozumler.

CIKTI:
  1. Botun 10 gercek isleminin giris profili; kazanan/kaybeden ayrimi
  2. Her olcunun (skor/pos/chg24/funding/oi24/vol_x/comp/stage/dip_yakit) POPULASYON
     dagilimi + kazananlarin yuzdeligi -> "hangi esik gercekten ayirt ediyor"
  3. Tek-degisken R tablolari (SHORT ve LONG ayri)
  4. Kazanan profilinin BILESIK testi (kesisim) + kontrol
  5. ON-KAYITLI dogrulama: profil ikiye bolunmus veride (ilk yari / son yari) ayakta mi
"""
import json, os, sys, statistics as st, collections

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BURA = os.path.dirname(os.path.abspath(__file__))


def yukle():
    ol = json.load(open(os.path.join(BURA, "oruntu_olaylar.json")))
    isl = [json.loads(l) for l in open(os.path.join(HERE, "testbot_islemler.jsonl"),
                                       encoding="utf-8") if l.strip()]
    poz = collections.defaultdict(list)
    for t in isl:
        poz[t["id"]].append(t)
    islemler = []
    for i, ts in sorted(poz.items()):
        a = ts[0]
        islemler.append({"id": i, "sym": a["sym"], "yon": a["yon"], "ts": a["ts"],
                         "skor": a.get("skor_giriste"), "stage": a.get("stage_giriste"),
                         "smart": a.get("smart_giriste"), "chg24": a.get("chg24_giriste"),
                         "pos": a.get("range_pos_giriste"), "rejim": a.get("rejim_giriste"),
                         "net": sum(x["sonuc_usdt"] for x in ts)})
    return ol, islemler


def ozet(rs):
    rs = [r for r in rs if r is not None]
    if not rs:
        return None
    return {"n": len(rs), "ort": st.mean(rs), "medyan": st.median(rs),
            "poz": sum(1 for r in rs if r > 0) / len(rs) * 100,
            "sh": st.pstdev(rs) / len(rs) ** 0.5 if len(rs) > 1 else 0.0}


def satir(ad, o, genis=30):
    if not o:
        print(f"  {ad:<{genis}} N=0")
        return
    print(f"  {ad:<{genis}} N={o['n']:6d}  ort R {o['ort']:+.3f} ±{o['sh']:.3f}  "
          f"medyan {o['medyan']:+.3f}  poz %{o['poz']:.0f}")


def bantla(olaylar, alan, kenarlar, yonalan):
    print(f"\n### {alan.upper()} — {yonalan}")
    for a, b in zip(kenarlar, kenarlar[1:]):
        sec = [o[yonalan] for o in olaylar
               if o.get(alan) is not None and a <= o[alan] < b]
        satir(f"{a} .. {b}", ozet(sec))


def main():
    olaylar, islemler = yukle()
    print("=" * 88)
    print("ÖRÜNTÜ RAPORU — botun kazandigi islemlerin profili genellenebilir mi?")
    print("=" * 88)
    print(f"Olay seti: {len(olaylar)} bagimsiz olay (radar_archive 46 gun, 6s dedup)")
    ilk = min(o["ts"] for o in olaylar); son = max(o["ts"] for o in olaylar)
    print(f"Pencere  : {ilk} -> {son}")

    kaz = [t for t in islemler if t["net"] > 0]
    kay = [t for t in islemler if t["net"] <= 0]
    print(f"\nBOTUN GERCEK ISLEMLERI: {len(islemler)} pozisyon | kazanan {len(kaz)} | kaybeden {len(kay)}")
    print(f"{'sym':8}{'yon':6}{'skor':>6}{'pos':>6}{'chg24':>8}{'stage':>11}{'smart':>7}{'rejim':>7}{'NET$':>10}")
    for t in sorted(islemler, key=lambda x: -x["net"]):
        print(f"{t['sym']:8}{t['yon']:6}{t['skor']:6.1f}{t['pos']:6.2f}{t['chg24']:8.1f}"
              f"{str(t['stage']):>11}{str(t['smart']):>7}{str(t['rejim']):>7}{t['net']:+10.2f}")

    # --- kazananlarin yuzdeligi
    print("\n" + "=" * 88)
    print("1) KAZANANLARIN OLCU DEGERLERI POPULASYONDA NEREDE?")
    print("=" * 88)
    for alan in ("score", "pos", "chg24", "funding", "oi24", "vol_x", "comp"):
        pop = sorted(o[alan] for o in olaylar if o.get(alan) is not None)
        if not pop:
            continue
        ad = {"score": "skor", "pos": "pos", "chg24": "chg24"}.get(alan, alan)
        deger = {"score": "skor", "pos": "pos", "chg24": "chg24"}.get(alan)
        print(f"\n  {ad}: populasyon medyan {st.median(pop):.2f} | "
              f"%90 dilim {pop[int(len(pop)*0.9)]:.2f} | %99 {pop[int(len(pop)*0.99)]:.2f}")
        if deger:
            for t in sorted(islemler, key=lambda x: -x["net"]):
                v = t[deger]
                yuzde = sum(1 for x in pop if x < v) / len(pop) * 100
                print(f"     {t['sym']:7} {'KAZ' if t['net']>0 else 'kay'} {v:8.2f} -> populasyonun %{yuzde:.1f}'i altinda")

    # --- tek degisken R tablolari
    print("\n" + "=" * 88)
    print("2) TEK-DEGISKEN R TABLOLARI (botun gercek stop/2R mekanigiyle)")
    print("=" * 88)
    satir("TUM OLAYLAR — SHORT", ozet([o["R_short"] for o in olaylar]))
    satir("TUM OLAYLAR — LONG", ozet([o["R_long"] for o in olaylar]))

    bantla(olaylar, "pos", [0.0, 0.25, 0.50, 0.70, 0.85, 1.01], "R_short")
    bantla(olaylar, "pos", [0.0, 0.25, 0.50, 0.70, 0.85, 1.01], "R_long")
    bantla(olaylar, "score", [0, 30, 40, 45, 60, 80, 200], "R_short")
    bantla(olaylar, "chg24", [-100, -20, 0, 10, 20, 40, 1000], "R_short")
    bantla(olaylar, "funding", [-5, -0.05, -0.01, 0.01, 0.05, 5], "R_short")
    bantla(olaylar, "oi24", [-100, 0, 10, 25, 50, 1000], "R_short")

    print("\n### STAGE — SHORT / LONG")
    for sg in ("BASLIYOR", "HAZIRLANIYOR", "izle"):
        satir(f"{sg} SHORT", ozet([o["R_short"] for o in olaylar if o.get("stage") == sg]))
        satir(f"{sg} LONG ", ozet([o["R_long"] for o in olaylar if o.get("stage") == sg]))

    # --- bilesik profil
    print("\n" + "=" * 88)
    print("3) KAZANAN PROFILININ BILESIK TESTI")
    print("=" * 88)
    print("Kazananlarin ortak yani (4/4): pos >= 0.85 (range TEPESI) ve SHORT tarafi.")
    print("Kaybeden SHORT'larin en buyuk 3'u: BLESS chg24 +73 · GRVT#8 pos 0.74 · DEXE chg24 -25")
    print("-> ON-KAYITLI PROFIL:  yon=SHORT · pos>=0.85 · 0<chg24<40")
    prof = [o for o in olaylar if (o.get("pos") is not None and o["pos"] >= 0.85
                                   and o.get("chg24") is not None and 0 < o["chg24"] < 40)]
    satir("PROFIL (SHORT)", ozet([o["R_short"] for o in prof]))
    kontrol = [o for o in olaylar if o not in prof]
    satir("KONTROL — profil disi (SHORT)", ozet([o["R_short"] for o in kontrol]))
    print()
    for ek, kos in (("+ skor>=45", lambda o: (o.get("score") or 0) >= 45),
                    ("+ skor>=60", lambda o: (o.get("score") or 0) >= 60),
                    ("+ skor>=80", lambda o: (o.get("score") or 0) >= 80),
                    ("+ stage=BASLIYOR", lambda o: o.get("stage") == "BASLIYOR"),
                    ("+ stage=izle", lambda o: o.get("stage") == "izle"),
                    ("+ funding>0", lambda o: (o.get("funding") or 0) > 0),
                    ("+ dip_yakit yok", lambda o: not o.get("dip_yakit"))):
        satir(f"PROFIL {ek}", ozet([o["R_short"] for o in prof if kos(o)]))

    # --- zaman bolunmesi (on-kayitli dogrulama)
    print("\n" + "=" * 88)
    print("4) ZAMAN BOLUNMESI — profil iki yarida da ayakta mi? (overfit testi)")
    print("=" * 88)
    tsl = sorted(o["ts"] for o in olaylar)
    orta = tsl[len(tsl) // 2]
    print(f"  Bolme noktasi: {orta}")
    for ad, sec in (("A yarisi", lambda o: o["ts"] < orta), ("B yarisi", lambda o: o["ts"] >= orta)):
        satir(f"{ad} PROFIL", ozet([o["R_short"] for o in prof if sec(o)]))
        satir(f"{ad} kontrol", ozet([o["R_short"] for o in kontrol if sec(o)]))

    # grafik verisi (artifact icin)
    cikti = {"pos_short": [], "pos_long": [], "skor_short": [], "chg24_short": [],
             "stage": {}, "profil": {}, "islemler": islemler,
             "n_olay": len(olaylar), "pencere": [ilk, son]}
    for a, b in zip([0, .25, .5, .7, .85], [.25, .5, .7, .85, 1.01]):
        for yon, ad in (("R_short", "pos_short"), ("R_long", "pos_long")):
            o = ozet([x[yon] for x in olaylar if x.get("pos") is not None and a <= x["pos"] < b])
            if o:
                cikti[ad].append({"bant": f"{a}-{b}", **{k: round(v, 4) for k, v in o.items()}})
    for a, b in zip([0, 30, 40, 45, 60, 80], [30, 40, 45, 60, 80, 200]):
        o = ozet([x["R_short"] for x in olaylar if x.get("score") is not None and a <= x["score"] < b])
        if o:
            cikti["skor_short"].append({"bant": f"{a}-{b}", **{k: round(v, 4) for k, v in o.items()}})
    for a, b in zip([-100, -20, 0, 10, 20, 40], [-20, 0, 10, 20, 40, 1000]):
        o = ozet([x["R_short"] for x in olaylar if x.get("chg24") is not None and a <= x["chg24"] < b])
        if o:
            cikti["chg24_short"].append({"bant": f"{a}..{b}", **{k: round(v, 4) for k, v in o.items()}})
    for sg in ("BASLIYOR", "HAZIRLANIYOR", "izle"):
        cikti["stage"][sg] = {
            "short": {k: round(v, 4) for k, v in (ozet([o["R_short"] for o in olaylar if o.get("stage") == sg]) or {}).items()},
            "long": {k: round(v, 4) for k, v in (ozet([o["R_long"] for o in olaylar if o.get("stage") == sg]) or {}).items()}}
    cikti["profil"] = {"profil": {k: round(v, 4) for k, v in (ozet([o["R_short"] for o in prof]) or {}).items()},
                       "kontrol": {k: round(v, 4) for k, v in (ozet([o["R_short"] for o in kontrol]) or {}).items()},
                       "A": {k: round(v, 4) for k, v in (ozet([o["R_short"] for o in prof if o["ts"] < orta]) or {}).items()},
                       "B": {k: round(v, 4) for k, v in (ozet([o["R_short"] for o in prof if o["ts"] >= orta]) or {}).items()}}
    json.dump(cikti, open(os.path.join(BURA, "oruntu_grafik.json"), "w"), ensure_ascii=False, indent=1)
    print("\ngrafik verisi -> scratchpad/oruntu_grafik.json")


if __name__ == "__main__":
    main()
