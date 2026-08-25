#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KONTROL GRUBU + SANS OLCUMU — pump<45'in +%43,5'i gercek mi, beta mi?

CLAUDE.md: "Kontrol grubu zorunlu. 'Kural karli' yetmez; kontrolu gecmeli."
           "En iyi hucre secilmez."  "Sans olcumu."

Uc kontrol:
  K1  AYNI TETIK, DIGER SKOR BANDI     -> pump skor>=45 tek basina, ayni 8 slot
  K2  SANS       -> tum pump havuzundan RASTGELE ayni sayida poz cek, 2000 kez.
                    pump<45'in sonucu bu dagilimin neresinde?
  K3  BETA       -> ayni pencerede ayni sayida RASTGELE ZAMANDA acilmis LONG
                    (golge+bot tum LONG havuzu) — "boga bacaginda long olmak"
                    tek basina ne veriyor?
Ayrica gunluk equity yolu: sonuc tek gune mi yaslaniyor?
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, re, datetime, collections, bisect, random, statistics as sx

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = "%Y-%m-%d %H:%M:%S"
BOGA = datetime.datetime(2026, 8, 19, 0, 0, 0)
VOLX = re.compile(r"vol_x\s+([0-9.]+)x")
MAKS_POZ = 8
MAKS_DUSUS = 25.0
random.seed(20260825)


def jl(y):
    p = os.path.join(PROJE, y)
    out = []
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            for s in f:
                if s.strip():
                    try:
                        out.append(json.loads(s))
                    except Exception:
                        pass
    return out


def equity_serisi(y):
    p = sorted((datetime.datetime.strptime(x["ts"], F), x.get("equity") or 0)
               for x in jl(y) if x.get("ts"))
    return [a for a, b in p], [b for a, b in p]


def equity_at(zs, es, t):
    i = bisect.bisect_right(zs, t) - 1
    return es[i] if 0 <= i < len(es) else (es[0] if es else 10000.0)


def adaylar(dosya, eq_dosya):
    zs, es = equity_serisi(eq_dosya)
    g = collections.defaultdict(list)
    for x in jl(dosya):
        g[x["id"]].append(x)
    out = []
    for i, v in g.items():
        v.sort(key=lambda z: z["ts"])
        ilk, son = v[0], v[-1]
        gt = (datetime.datetime.strptime(ilk["ts"], F)
              - datetime.timedelta(hours=(ilk.get("tutma_saat") or 0)))
        kt = datetime.datetime.strptime(son["ts"], F)
        no = ilk.get("notional") or 0
        if not no or kt <= gt or gt < BOGA:
            continue
        net = sum((t.get("sonuc_usdt") or 0) for t in v)
        fon = [t.get("funding_usdt") for t in v if t.get("funding_usdt") is not None]
        eq = equity_at(zs, es, gt) or 10000.0
        m = VOLX.search(son.get("sebep_giris") or "")
        out.append(dict(sym=son["sym"], yon=son["yon"], gir=gt, kap=kt,
                        pct=100.0 * net / no, fon_frac=(sum(fon) / no) if fon else 0.0,
                        exp=no / eq, kaynak=son.get("kaynak") or "testbot",
                        skor=ilk.get("skor_giriste"), vol_x=float(m.group(1)) if m else None))
    return out


BOT = adaylar("testbot_islemler.jsonl", "testbot_equity.jsonl")
GOL = adaylar("golge_islemler.jsonl", "golge_equity.jsonl")
PUMP = [z for z in GOL if "pump_long" in z["kaynak"]]
LO = [z for z in PUMP if z["skor"] is not None and z["skor"] < 45]
HI = [z for z in PUMP if z["skor"] is not None and z["skor"] >= 45]
TUM_LONG = [z for z in GOL + BOT if z["yon"] == "LONG"]

zs_t, es_t = equity_serisi("testbot_equity.jsonl")
BAS = equity_at(zs_t, es_t, BOGA)


def sim(havuz, maks_poz=MAKS_POZ, fren=MAKS_DUSUS, yol=False):
    eq, tepe, dd = BAS, BAS, 0.0
    acik = []
    alinan = 0
    donmus = False
    gun_eq = {}
    for a in sorted(havuz, key=lambda z: z["gir"]):
        acik.sort(key=lambda z: z[0])
        while acik and acik[0][0] <= a["gir"]:
            kt, poz, no = acik.pop(0)
            eq += poz["pct"] / 100.0 * no + poz["fon_frac"] * no
            tepe = max(tepe, eq)
            dd = max(dd, 100.0 * (1 - eq / tepe))
            gun_eq[kt.strftime("%m-%d")] = eq
        if fren and 100.0 * (1 - eq / tepe) >= fren:
            donmus = True
        if donmus or len(acik) >= maks_poz or any(p[1]["sym"] == a["sym"] for p in acik):
            continue
        acik.append((a["kap"], a, a["exp"] * eq))
        alinan += 1
    for kt, poz, no in sorted(acik, key=lambda z: z[0]):
        eq += poz["pct"] / 100.0 * no + poz["fon_frac"] * no
        tepe = max(tepe, eq)
        dd = max(dd, 100.0 * (1 - eq / tepe))
        gun_eq[kt.strftime("%m-%d")] = eq
    return (eq, dd, alinan, gun_eq) if yol else (eq, dd, alinan)


def yaz(ad, r):
    eq, dd, al = r[0], r[1], r[2]
    print("   %-42s son equity %9.2f  (%+7.2f%%)  maks dd %5.1f%%  alinan %3d"
          % (ad, eq, 100.0 * (eq / BAS - 1), dd, al))


print("KONTROL GRUBU + SANS OLCUMU   (baslangic %.2f · maks_poz=%d)" % (BAS, MAKS_POZ))
print("havuz: pump toplam %d · skor<45 %d · skor>=45 %d · tum LONG (golge+bot) %d"
      % (len(PUMP), len(LO), len(HI), len(TUM_LONG)))
print("=" * 116)

print("\nK1 — AYNI TETIK, DIGER SKOR BANDI")
print("-" * 116)
yaz("pump  skor < 45   (ONERI)", sim(LO))
yaz("pump  skor >= 45  (kontrol)", sim(HI))
yaz("pump  tum bantlar", sim(PUMP))
yaz("bot LONG (mevcut kural)", sim([z for z in BOT if z["yon"] == "LONG"]))

print("\nK2 — SANS: tum pump havuzundan RASTGELE %d poz, 2000 cekilis" % len(LO))
print("-" * 116)
sonuclar = []
for _ in range(2000):
    sonuclar.append(sim(random.sample(PUMP, len(LO)))[0])
sonuclar.sort()
ger = sim(LO)[0]
ustunde = sum(1 for x in sonuclar if x >= ger)
print("   rastgele dagilim: medyan %9.2f  %%5 %9.2f  %%95 %9.2f"
      % (sx.median(sonuclar), sonuclar[int(0.05 * len(sonuclar))],
         sonuclar[int(0.95 * len(sonuclar))]))
print("   skor<45 gercek  : %9.2f   -> rastgeleden IYI olma yuzdesi %%%.1f  (p = %.4f)"
      % (ger, 100.0 * (1 - ustunde / len(sonuclar)), ustunde / len(sonuclar)))

print("\nK3 — BETA: ayni pencerede RASTGELE %d LONG (golge+bot tum LONG havuzu), 2000 cekilis" % len(LO))
print("-" * 116)
s3 = []
for _ in range(2000):
    s3.append(sim(random.sample(TUM_LONG, min(len(LO), len(TUM_LONG))))[0])
s3.sort()
ust3 = sum(1 for x in s3 if x >= ger)
print("   'boga bacaginda rastgele long' dagilimi: medyan %9.2f  %%5 %9.2f  %%95 %9.2f"
      % (sx.median(s3), s3[int(0.05 * len(s3))], s3[int(0.95 * len(s3))]))
print("   -> boga bacaginda RASTGELE long olmak bile %+.2f%% veriyor (medyan)"
      % (100.0 * (sx.median(s3) / BAS - 1)))
print("   skor<45 gercek %9.2f  -> p = %.4f" % (ger, ust3 / len(s3)))

print("\nGUNLUK EQUITY YOLU — sonuc tek gune mi yasliyor?")
print("-" * 116)
for ad, hav in (("pump skor<45", LO), ("pump skor>=45", HI), ("bot LONG", [z for z in BOT if z["yon"] == "LONG"])):
    _, _, _, ge = sim(hav, yol=True)
    print("   %-16s %s" % (ad, "  ".join("%s %8.0f" % (g, ge[g]) for g in sorted(ge))))

print("\nEK — skor esigi kaydirilirsa (esik SECIMI post-hoc mu?)")
print("-" * 116)
for esik in (30, 35, 40, 45, 50, 55, 60):
    w = [z for z in PUMP if z["skor"] is not None and z["skor"] < esik]
    if len(w) >= 15:
        eq, dd, al = sim(w)
        print("   skor < %-3d  N=%3d  son equity %9.2f  (%+7.2f%%)  maks dd %5.1f%%"
              % (esik, len(w), eq, 100.0 * (eq / BAS - 1), dd))

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
