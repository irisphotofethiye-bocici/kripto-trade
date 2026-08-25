#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PORTFOY SIMULASYONU — pump_long(skor<45) BOTA eklenirse ne olur?

SORU (kullanici, 2026-08-25): "bunu bota eklersek nasil sonuc aliriz"

Golge ZATEN bu kuralin canli testi. Eksik olan sey kuralin kendisi degil,
BOTUN KISITLARI:
    golge:  MAKS_ACIK=20 · dusus freni YOK   · kendi kasasi · rakip giris yok
    bot:    maks_pozisyon=8 · maks_dusus_pct=25 · ayni slotlar icin YARISMA

Bu betik olayları botun kisitlariyla YENIDEN OYNATIR.

YONTEM
  - Her pozisyonun getirisi net/notional olarak SABIT alinir (fiyat yolu +
    mekanik; boyuttan bagimsiz). Fonlama ayni oranla olceklenir.
  - Boyut: exposure_frac = notional / (o defterin o andaki equity'si).
    Risk-once boyutlandirmayi korur; kasa buyudukce poz buyur.
  - Olay kuyrugu: ayni anda once CIKIS, sonra GIRIS. Slot doluysa aday DUSER
    (bot da boyle davranir). Ayni sembolde ikinci poz YOK.
  - Dusus freni: equity zirveden %25 geri cekilirse YENI GIRIS durur.

DOGRULAMA: S0 (bot oldugu gibi) gercek defteri YENIDEN URETMELI. Uretmiyorsa
sim yanlistir ve digerleri de okunmaz.

SALT OKUMA — bot dosyalarina, state'e, deftere DOKUNMAZ.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, re, datetime, collections, bisect

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = "%Y-%m-%d %H:%M:%S"
BOGA = datetime.datetime(2026, 8, 19, 0, 0, 0)
VOLX = re.compile(r"vol_x\s+([0-9.]+)x")

MAKS_POZ = 8           # kripto-config.json -> testbot.maks_pozisyon
MAKS_DUSUS = 25.0      # kripto-config.json -> testbot.maks_dusus_pct


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
    zs, es = [], []
    for x in jl(y):
        try:
            zs.append(datetime.datetime.strptime(x["ts"], F))
            es.append(x.get("equity") or 0)
        except Exception:
            pass
    p = sorted(zip(zs, es))
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
        if not no or kt <= gt:
            continue
        net = sum((t.get("sonuc_usdt") or 0) for t in v)
        fon = [t.get("funding_usdt") for t in v if t.get("funding_usdt") is not None]
        eq = equity_at(zs, es, gt) or 10000.0
        m = VOLX.search(son.get("sebep_giris") or "")
        out.append(dict(sym=son["sym"], yon=son["yon"], gir=gt, kap=kt,
                        pct=100.0 * net / no,
                        fon_frac=(sum(fon) / no) if fon else 0.0,
                        exp=no / eq,
                        kaynak=son.get("kaynak") or "testbot",
                        skor=ilk.get("skor_giriste"),
                        vol_x=float(m.group(1)) if m else None))
    return [z for z in out if z["gir"] >= BOGA]


BOT = adaylar("testbot_islemler.jsonl", "testbot_equity.jsonl")
GOL = adaylar("golge_islemler.jsonl", "golge_equity.jsonl")
PUMP = [z for z in GOL if "pump_long" in z["kaynak"]]
PUMP_LO = [z for z in PUMP if z["skor"] is not None and z["skor"] < 45]

zs_t, es_t = equity_serisi("testbot_equity.jsonl")
BAS_EQ = equity_at(zs_t, es_t, BOGA)


def sim(havuz, maks_poz=MAKS_POZ, fren=MAKS_DUSUS, bas=None):
    """Olay kuyrugu. Donus: (son_equity, tepe, maks_dusus%, alinan, slot_dusen,
       fren_dusen, kaynak_sayim)"""
    eq = bas if bas is not None else BAS_EQ
    tepe = eq
    maks_dd = 0.0
    acik = []          # (kapanis_ts, aday, notional)
    alinan, slot_red, fren_red, sym_red = 0, 0, 0, 0
    kaynak = collections.Counter()
    pnl_kaynak = collections.Counter()
    donmus = False
    for a in sorted(havuz, key=lambda z: z["gir"]):
        # once bu ana kadarki CIKISLARI isle
        acik.sort(key=lambda z: z[0])
        while acik and acik[0][0] <= a["gir"]:
            kt, poz, no = acik.pop(0)
            kar = poz["pct"] / 100.0 * no + poz["fon_frac"] * no
            eq += kar
            pnl_kaynak[poz["kaynak"]] += kar
            tepe = max(tepe, eq)
            maks_dd = max(maks_dd, 100.0 * (1 - eq / tepe) if tepe else 0)
        if fren and tepe and 100.0 * (1 - eq / tepe) >= fren:
            donmus = True
        if donmus:
            fren_red += 1
            continue
        if len(acik) >= maks_poz:
            slot_red += 1
            continue
        if any(p[1]["sym"] == a["sym"] for p in acik):
            sym_red += 1
            continue
        no = a["exp"] * eq
        acik.append((a["kap"], a, no))
        alinan += 1
        kaynak[a["kaynak"]] += 1
    for kt, poz, no in acik:
        kar = poz["pct"] / 100.0 * no + poz["fon_frac"] * no
        eq += kar
        pnl_kaynak[poz["kaynak"]] += kar
        tepe = max(tepe, eq)
        maks_dd = max(maks_dd, 100.0 * (1 - eq / tepe) if tepe else 0)
    return dict(eq=eq, tepe=tepe, dd=maks_dd, alinan=alinan, slot_red=slot_red,
                fren_red=fren_red, sym_red=sym_red, kaynak=kaynak, pnl=pnl_kaynak,
                donmus=donmus)


print("PORTFOY SIMULASYONU — pump_long(skor<45) bota eklenirse")
print("pencere %s .. son kapanis  ·  baslangic equity %.2f (testbot, 08-19)"
      % (BOGA.strftime("%m-%d %H:%M"), BAS_EQ))
print("kisitlar: maks_poz=%d · maks_dusus=%.0f%% · ayni sembolde tek poz" % (MAKS_POZ, MAKS_DUSUS))
print("=" * 116)

print("\nHAVUZ BOYUTLARI   bot %d (LONG %d/SHORT %d) · golge pump %d · pump skor<45 %d"
      % (len(BOT), sum(1 for z in BOT if z["yon"] == "LONG"),
         sum(1 for z in BOT if z["yon"] == "SHORT"), len(PUMP), len(PUMP_LO)))

BOT_SHORT = [z for z in BOT if z["yon"] == "SHORT"]
SENARYO = [
    ("S0  bot oldugu gibi            (DOGRULAMA)", BOT),
    ("S1  bot + pump<45              (eklenir)", BOT + PUMP_LO),
    ("S2  bot SHORT + pump<45        (LONG kapisi degisir)", BOT_SHORT + PUMP_LO),
    ("S3  yalniz pump<45             (bot girisi yok)", PUMP_LO),
    ("S4  bot + pump TUMU            (skor suzgeci YOK)", BOT + PUMP),
]

print("\n%-52s %10s %9s %8s %7s %7s %7s" %
      ("senaryo", "son equity", "getiri", "maks dd", "alinan", "slotta", "frende"))
print("-" * 116)
sonuc = {}
for ad, hav in SENARYO:
    r = sim(hav)
    sonuc[ad[:2]] = r
    print("%-52s %10.2f %+8.2f%% %7.1f%% %7d %7d %7d"
          % (ad, r["eq"], 100.0 * (r["eq"] / BAS_EQ - 1), r["dd"],
             r["alinan"], r["slot_red"], r["fren_red"]))

print("\nDOGRULAMA — S0 gercek defteri yeniden uretiyor mu?")
print("-" * 116)
gercek = sum(z["pct"] / 100.0 * z["exp"] * BAS_EQ for z in BOT)
print("   S0 sim sonucu           %+9.2f $" % (sonuc["S0"]["eq"] - BAS_EQ))
print("   gercek defter (boga)    %+9.2f $   <- testbot LONG -934.12 + SHORT -1624.02"
      % (-934.12 - 1624.02))
print("   S0'da slot yuzunden dusen aday: %d   (gercekte bot bu adaylari zaten gordu)"
      % sonuc["S0"]["slot_red"])
print("   NOT: tam esitlik BEKLENMEZ — sim sabit %.2f kasadan baslar ve boyutu"
      % BAS_EQ)
print("        yeniden olcekler; isaret ve buyukluk mertebesi tutmalidir.")

print("\nKAYNAK KIRILIMI — hangi senaryoda kim ne kazandirdi")
print("-" * 116)
for ad, _ in SENARYO:
    r = sonuc[ad[:2]]
    print("   %s" % ad)
    for k, v in sorted(r["pnl"].items(), key=lambda z: -z[1]):
        print("        %-26s alinan %3d   P&L %+9.2f" % (k, r["kaynak"].get(k, 0), v))

print("\nSLOT MALIYETI — golge 20 slotla kostu, bot 8 slotla kosar")
print("-" * 116)
for n in (4, 8, 12, 20, 999):
    r = sim(PUMP_LO, maks_poz=n)
    print("   maks_poz=%-4s son equity %9.2f  (%+7.2f%%)  alinan %3d/%d  slotta dusen %3d  maks dd %5.1f%%"
          % (n if n < 999 else "sinirsiz", r["eq"], 100.0 * (r["eq"] / BAS_EQ - 1),
             r["alinan"], len(PUMP_LO), r["slot_red"], r["dd"]))

print("\nFREN — %d%% dusus freni bu senaryolarda tetikledi mi" % MAKS_DUSUS)
print("-" * 116)
for ad, hav in SENARYO:
    r = sonuc[ad[:2]]
    print("   %-52s maks dusus %5.1f%%   fren %s"
          % (ad, r["dd"], "TETIKLEDI (%d aday dustu)" % r["fren_red"] if r["donmus"] else "tetiklemedi"))

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
