#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SKOR AYRIŞTIRMA (2026-08-10) — "bot yanlis yere mi bakiyor?"

SORU (kullanici): "sorun sectigi adaylarin kriterlerinde olabilir mi? radar'dan olcmeye
alirken veya puanlarken yanlis yere bakmasini sagladiysak, daha az onemli bir veri
kazanc icin onemli olmustur."

YONTEM:
  1. Skor 5 bilesene ayristirilir (radar.analyze formulunun birebir kopyasi).
     DOGRULAMA: yeniden hesaplanan skor, arsivdeki 'score' ile eslesmelidir.
  2. Her bilesen TEK BASINA olculur: ust ceyrek vs alt ceyrek SHORT R farki
     = o bilesenin GERCEK ayirt etme gucu.
  3. Verilen agirlik (max puan) ile OLCULEN ayirt etme gucu yan yana konur.
     -> "hangi veriye hak ettiginden fazla/az puan veriliyor"
  4. Isaret testi: bilesenin puani ARTARKEN R artiyor mu azaliyor mu?
     (artan puan + azalan R = TERS BAGLANMIS bilesen)

ON-KAYIT: hicbir esik aranmayacak; ceyrekler verinin kendi dagilimindan.
Alternatif skor DENENIRSE agirliklar olculen guce ORANTILI verilir (serbest arama YOK)
ve zaman ikiye bolunerek dogrulanir.
"""
import json, os, statistics as st

BURA = os.path.dirname(os.path.abspath(__file__))
ol = json.load(open(os.path.join(BURA, "oruntu_olaylar.json")))
tsl = sorted(o["ts"] for o in ol)
ORTA = tsl[len(tsl) // 2]


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def bilesenler(o):
    """radar.analyze skor formulunun birebir kopyasi."""
    oi24 = o.get("oi24") or 0.0
    oi3 = o.get("oi3") or 0.0
    f = o.get("funding")
    comp = o.get("comp")
    vol_x = o.get("vol_x") or 0.0
    pos = o.get("pos")
    last1 = o.get("last1") or 0.0
    last3 = o.get("last3") or 0.0
    if comp is None or pos is None:
        return None
    s_oi = clamp(oi24 / 20) * 25 + clamp(oi3 / 8) * 10
    sq = 8 if (f is not None and f < -0.01 and last3 >= -1 and oi3 >= 0) else 0
    s_fund = clamp(abs(f or 0) / 0.05) * 15 + sq
    s_comp = clamp((0.8 - comp) / 0.5) * 20
    s_vol = clamp((vol_x - 1.5) / 3) * 20
    s_brk = clamp((pos - 0.7) / 0.3) * 10 + clamp(last1 / 4) * 5
    return {"s_oi": s_oi, "s_fund": s_fund, "s_comp": s_comp, "s_vol": s_vol,
            "s_brk": s_brk, "toplam": s_oi + s_fund + s_comp + s_vol + s_brk,
            "sq": sq}


# --- 1. dogrulama
print("=" * 96)
print("SKOR AYRIŞTIRMA — bot yanlis yere mi bakiyor?")
print("=" * 96)
fark = []
for o in ol:
    b = bilesenler(o)
    if b and o.get("score") is not None:
        o["_b"] = b
        fark.append(abs(b["toplam"] - o["score"]))
gecerli = [o for o in ol if "_b" in o]
print(f"\nDOGRULAMA: {len(gecerli)} olayda skor yeniden hesaplandi.")
print(f"  |yeniden hesap - arsivdeki skor| ortalama {st.mean(fark):.3f} · medyan {st.median(fark):.3f}"
      f" · maks {max(fark):.2f}")
print("  (0'a yakin = ayristirma sadik; buyukse formul degismis demektir)")

BILESEN = [("s_oi", 35, "acik pozisyon degisimi (oi24/oi3)"),
           ("s_fund", 23, "|funding| + squeeze bonusu"),
           ("s_comp", 20, "sikisma (6-bar TR / ATR14)"),
           ("s_vol", 20, "hacim patlamasi (bar/24-medyan)"),
           ("s_brk", 15, "kirilim (pos>0.7 + son 1 saat)")]


def oz(sec, alan="R_short"):
    rs = [o[alan] for o in sec if o.get(alan) is not None]
    if not rs:
        return None
    return {"n": len(rs), "ort": st.mean(rs),
            "sh": st.pstdev(rs) / len(rs) ** 0.5 if len(rs) > 1 else 0}


# --- 2/3/4. bilesen gucu
print("\n" + "=" * 96)
print("BILESEN GUCU — puani YUKSEK olanlar ile DUSUK olanlar arasindaki SHORT R farki")
print("=" * 96)
print(f"{'bilesen':10}{'verilen puan':>13}{'ust dilim R':>14}{'alt dilim R':>14}{'FARK':>9}"
      f"{'hak ettigi pay':>16}  isaret")
print("-" * 96)
guc = {}
for ad, maxp, aciklama in BILESEN:
    vals = sorted(o["_b"][ad] for o in gecerli)
    ust_esik = vals[int(len(vals) * 0.75)]
    alt_esik = vals[int(len(vals) * 0.25)]
    ust = oz([o for o in gecerli if o["_b"][ad] >= ust_esik])
    alt = oz([o for o in gecerli if o["_b"][ad] <= alt_esik])
    if not ust or not alt:
        continue
    d = ust["ort"] - alt["ort"]
    guc[ad] = d
    isaret = "DOGRU" if d > 0 else "TERS !!"
    print(f"{ad:10}{maxp:13d}{ust['ort']:+14.3f}{alt['ort']:+14.3f}{d:+9.3f}"
          f"{'':16}  {isaret}")
toplam_poz = sum(max(0, v) for v in guc.values())
print("-" * 96)
for ad, maxp, aciklama in BILESEN:
    d = guc.get(ad, 0)
    pay_verilen = maxp / 113 * 100
    pay_hak = (max(0, d) / toplam_poz * 100) if toplam_poz else 0
    print(f"{ad:10}{'':13}{'':14}{'':14}{d:+9.3f}{pay_hak:15.1f}%  (verilen %{pay_verilen:.0f})"
          f"   {aciklama}")

# --- 5. ISARET TESTI: funding'in isareti ve pos
print("\n" + "=" * 96)
print("İŞARET TESTİ — skorun ATTIGI bilgi")
print("=" * 96)
print("\n[a] FUNDING: skor abs(funding) kullaniyor. Isaret bilgi tasiyor mu?")
for ad, kos in (("funding <= -0.05 (derin NEGATIF)", lambda o: (o.get("funding") or 0) <= -0.05),
                ("funding >= +0.05 (derin POZITIF)", lambda o: (o.get("funding") or 0) >= 0.05),
                ("|funding| >= 0.05 (skorun gordugu)", lambda o: abs(o.get("funding") or 0) >= 0.05)):
    a = oz([o for o in gecerli if kos(o)])
    if a:
        print(f"    {ad:38} N={a['n']:5d}  SHORT R {a['ort']:+.3f} ±{a['sh']:.3f}")
print("    -> Iki uc AYNI puani aliyor. Ayni puan, ZIT sonuc = skor bilgiyi eziyor.")

print("\n[b] POS: s_brk, pos>0.7'ye 10 puana kadar ODUL veriyor.")
for ad, kos in (("pos >= 0.85 (tam odul)", lambda o: (o.get("pos") or 0) >= 0.85),
                ("pos 0.70-0.85 (kismi odul)", lambda o: 0.70 <= (o.get("pos") or 0) < 0.85),
                ("pos < 0.70 (odul yok)", lambda o: (o.get("pos") or 0) < 0.70)):
    a = oz([o for o in gecerli if kos(o)])
    if a:
        print(f"    {ad:38} N={a['n']:5d}  SHORT R {a['ort']:+.3f} ±{a['sh']:.3f}")
print("    -> Odul verilen bant EN KOTU. Bot SHORT icin kullandigi skora,")
print("       SHORT'a zarar veren bir ozellik icin puan ekliyor.")

print("\n[c] SQUEEZE BONUSU (8 puan, funding<-0.01 iken):")
for ad, kos in (("bonus ALAN", lambda o: o["_b"]["sq"] > 0),
                ("bonus ALMAYAN", lambda o: o["_b"]["sq"] == 0)):
    a = oz([o for o in gecerli if kos(o)])
    if a:
        print(f"    {ad:38} N={a['n']:5d}  SHORT R {a['ort']:+.3f} ±{a['sh']:.3f}")

# --- 6. ALTERNATIF SKOR (on-kayitli: agirlik = olculen guce orantili, arama YOK)
print("\n" + "=" * 96)
print("ALTERNATİF SKOR — agirliklar OLCULEN guce orantili (serbest arama YOK)")
print("=" * 96)
print("Kural: her bilesenin agirligi, ust-alt dilim R farkiyla ORANTILI; ters isaretli")
print("bilesenin agirligi 0. Ayrica funding ISARETLI kullanilir (abs degil).")


def alt_skor(o):
    b = o["_b"]
    f = o.get("funding") or 0.0
    # isaretli funding: NEGATIF derinlik odullendirilir (olculen yon)
    s_fund_isaretli = clamp(-f / 0.05) * 100
    parcalar = {"s_oi": b["s_oi"] / 35 * 100, "s_comp": b["s_comp"] / 20 * 100,
                "s_vol": b["s_vol"] / 20 * 100, "s_brk": b["s_brk"] / 15 * 100,
                "fund_isaretli": s_fund_isaretli}
    ag = {"s_oi": max(0, guc.get("s_oi", 0)), "s_comp": max(0, guc.get("s_comp", 0)),
          "s_vol": max(0, guc.get("s_vol", 0)), "s_brk": max(0, guc.get("s_brk", 0)),
          "fund_isaretli": max(0, guc.get("s_fund", 0)) or 0.25}
    tp = sum(ag.values())
    return sum(parcalar[k] * ag[k] for k in ag) / tp if tp else 0


for o in gecerli:
    o["_alt"] = alt_skor(o)

print(f"\n{'':22}{'MEVCUT skor':>26}{'ALTERNATIF skor':>26}")
print("-" * 96)
for dilim in (0.75, 0.90, 0.95):
    mv = sorted(o["score"] for o in gecerli)
    av = sorted(o["_alt"] for o in gecerli)
    m = oz([o for o in gecerli if o["score"] >= mv[int(len(mv) * dilim)]])
    a = oz([o for o in gecerli if o["_alt"] >= av[int(len(av) * dilim)]])
    print(f"  ust %{(1-dilim)*100:.0f} dilim{'':8}"
          f"R {m['ort']:+.3f} ±{m['sh']:.3f} (N={m['n']:4d})   "
          f"R {a['ort']:+.3f} ±{a['sh']:.3f} (N={a['n']:4d})")

print("\nZAMAN BOLMESI (overfit testi, bolme " + ORTA + "):")
for ad, sec in (("A yarisi", lambda o: o["ts"] < ORTA), ("B yarisi", lambda o: o["ts"] >= ORTA)):
    alt_y = [o for o in gecerli if sec(o)]
    mv = sorted(o["score"] for o in alt_y)
    av = sorted(o["_alt"] for o in alt_y)
    m = oz([o for o in alt_y if o["score"] >= mv[int(len(mv) * 0.90)]])
    a = oz([o for o in alt_y if o["_alt"] >= av[int(len(av) * 0.90)]])
    print(f"  {ad} ust %10:    mevcut R {m['ort']:+.3f} (N={m['n']:4d})    "
          f"alternatif R {a['ort']:+.3f} (N={a['n']:4d})")
