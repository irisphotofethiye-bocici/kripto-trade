#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KAPI SETİ REPLAY (2026-08-10) — onerilen konfigurasyon, uygulanmadan ONCE tam olculur.

Kullanici: "elimizdeki gecmis veriyle bunlari bulabilirsin, niye bekleyelim."
Dogru. Onerilen kapi seti canliya alinmadan once 46 gunluk arsivde bastan sona kosulur.

KARSILASTIRILAN SETLER (hepsi SHORT tarafi, botun gercek mekanigi: A-stop, 2R, 72s, fitil):
  S0  BUGUNKU        : skor>=45 · pump<20 · pos>=0.20 · chg24>-40 · rr>=1.5
  S1  R/R KALKSIN    : ayni, rr kapisi YOK
  S2  A+B EKLENSIN   : S1 + funding<=-0.05 & oi24>=10
  S3  SADECE A+B     : yalniz funding<=-0.05 & oi24>=10  (skor/pump/pos kapilari YOK)
  S4  A+B + skor     : A+B + skor>=45
  S5  A+B + pump     : A+B + chg24<20   (pump kapisi korunsun mu?)
  S6  A+B + HAZIR    : A+B + stage=HAZIRLANIYOR
Her set icin: N · ort R · hedefe ulasan % · A yarisi · B yarisi · gunluk olay sayisi.
KONTROL: her setin DISINDA kalanlarin R'si.
"""
import json, os, statistics as st

BURA = os.path.dirname(os.path.abspath(__file__))
ol = [o for o in json.load(open(os.path.join(BURA, "oruntu_olaylar.json")))
      if o.get("R_short") is not None]
try:
    ek = {(o["ts"], o["sym"]): o for o in json.load(open(os.path.join(BURA, "kacan_olaylar.json")))}
    for o in ol:
        k = ek.get((o["ts"], o["sym"]))
        if k:
            o["rr_tp1"] = k.get("rr_tp1")
except Exception:
    pass
ol = [o for o in ol if o.get("rr_tp1") is not None]
tsl = sorted(o["ts"] for o in ol)
ORTA = tsl[len(tsl) // 2]
GUN = 46.0

sk = lambda o: (o.get("score") or 0)
fu = lambda o: (o.get("funding") or 0)
oi = lambda o: (o.get("oi24") or 0)
ch = lambda o: (o.get("chg24") or 0)
po = lambda o: (o.get("pos") or 0)
AB = lambda o: (fu(o) <= -0.05 and oi(o) >= 10)
TEMEL = lambda o: (sk(o) >= 45 and ch(o) < 20 and po(o) >= 0.20 and ch(o) > -40)

SETLER = [
    ("S0  BUGUNKU (rr>=1.5)", lambda o: TEMEL(o) and o["rr_tp1"] >= 1.5),
    ("S1  R/R kapisi KALKSIN", TEMEL),
    ("S2  S1 + A+B", lambda o: TEMEL(o) and AB(o)),
    ("S3  SADECE A+B", AB),
    ("S4  A+B + skor>=45", lambda o: AB(o) and sk(o) >= 45),
    ("S5  A+B + pump kapisi", lambda o: AB(o) and ch(o) < 20),
    ("S6  A+B + HAZIRLANIYOR", lambda o: AB(o) and o.get("stage") == "HAZIRLANIYOR"),
]


def oz(sec):
    rs = [o["R_short"] for o in sec]
    if not rs:
        return None
    return {"n": len(rs), "ort": st.mean(rs),
            "sh": st.pstdev(rs) / len(rs) ** 0.5 if len(rs) > 1 else 0,
            "hedef": sum(1 for r in rs if r > 1.5) / len(rs) * 100}


print("=" * 118)
print("KAPI SETİ REPLAY — 46 gun · 7119 olay · SHORT · botun gercek mekanigi")
print("=" * 118)
print(f"{'set':26}{'N':>6}{'gun/olay':>10}{'ort R':>9}{'±':>7}{'hedefe':>8}"
      f"{'A yari':>10}{'B yari':>10}{'kontrol':>10}")
print("-" * 118)
for ad, fn in SETLER:
    sec = [o for o in ol if fn(o)]
    dis = [o for o in ol if not fn(o)]
    a = oz(sec)
    if not a:
        print(f"{ad:26}  N=0")
        continue
    A = oz([o for o in sec if o["ts"] < ORTA])
    B = oz([o for o in sec if o["ts"] >= ORTA])
    K = oz(dis)
    print(f"{ad:26}{a['n']:6d}{a['n']/GUN:10.1f}{a['ort']:+9.3f}{a['sh']:7.3f}"
          f"{a['hedef']:7.0f}%{(A['ort'] if A else 0):+10.3f}{(B['ort'] if B else 0):+10.3f}"
          f"{K['ort']:+10.3f}")

print("\n" + "=" * 118)
print("KUMULATIF R — 46 gunde toplam kac R kazanilirdi (islem sayisi x ort R)")
print("=" * 118)
for ad, fn in SETLER:
    sec = [o for o in ol if fn(o)]
    if not sec:
        continue
    t = sum(o["R_short"] for o in sec)
    print(f"  {ad:26} toplam {t:+8.1f}R  ({len(sec)} islem, gunde {len(sec)/GUN:.1f})")

print("\n" + "=" * 118)
print("GERCEKCILIK KESINTISI — bot 2R'ye hic ulasmadi (10/10 stopla kapandi)")
print("=" * 118)
print("Gercek karnede kazananlar ort +0.62R aldi, teorik 2R degil.")
print("Asagida ayni setler, kazanclar 1.5R'de KIRPILARAK (botun kismi-kar tavani):")
print(f"{'set':26}{'N':>6}{'kirpilmis ort R':>18}{'A yari':>11}{'B yari':>11}")
print("-" * 118)
for ad, fn in SETLER:
    sec = [o for o in ol if fn(o)]
    if not sec:
        continue
    kirp = lambda o: min(o["R_short"], 1.5)
    v = [kirp(o) for o in sec]
    vA = [kirp(o) for o in sec if o["ts"] < ORTA]
    vB = [kirp(o) for o in sec if o["ts"] >= ORTA]
    print(f"{ad:26}{len(v):6d}{st.mean(v):+18.3f}"
          f"{(st.mean(vA) if vA else 0):+11.3f}{(st.mean(vB) if vB else 0):+11.3f}")
