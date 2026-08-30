#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KAZANAN vs KAYBEDEN — ortak patern araması. KESIFSEL (hipotez uretir, HUKUM YAZMAZ).

Kullanici istegi 2026-08-30: "butun defterlerde kaybeden pozlarla kazanan pozlari
ayir ve ikisindeki ortak paterni ara".

🔴 DONGUSELLIK KURALI — bu betigin varlik sebebi:
   Pozisyonun GEC anina ait alanlar (mfe_pct · tepe_pnl_pct · arti_dakika · pnl_*)
   kazanani kazanan YAPAN seyin kendisidir. Onlarla ayirmak "kazananlar kazandi"
   demektir. Bu betik onlari AYRI bolumde ve DONGUSEL etiketiyle basar, karar
   ozelliklerinden ayirir.
   KARAR OZELLIKLERI = giris aninda bilinen + ilk 30 dakikada bilinen.

KAPSAM: 5 dakikalik izleme YALNIZ testbot'u kapsiyor (kaynak='canli').
   Diger defterler icin yalniz giris ani alanlari var.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, datetime, collections, statistics, math

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = "%Y-%m-%d %H:%M:%S"
DEFTERLER = [("testbot", "testbot_islemler.jsonl"), ("golge", "golge_islemler.jsonl"),
             ("ayna", "ayna_islemler.jsonl"), ("defter2", "defter2_islemler.jsonl"),
             ("defter3", "defter3_islemler.jsonl"), ("benim", "benim_islemler.jsonl")]


def pozisyonlar():
    out = []
    for ad, f in DEFTERLER:
        p = os.path.join(PROJE, f)
        if not os.path.exists(p):
            continue
        g = collections.defaultdict(list)
        for s in open(p, encoding="utf-8"):
            if not s.strip():
                continue
            try:
                x = json.loads(s)
            except Exception:
                continue
            g[x.get("id")].append(x)
        for i, v in g.items():
            v.sort(key=lambda z: z["ts"])
            ilk, son = v[0], v[-1]
            no = ilk.get("notional") or 0
            if no <= 0:
                continue
            net = sum((t.get("sonuc_usdt") or 0) for t in v)      # SUZGEC YOK
            fon = [t.get("funding_usdt") for t in v if t.get("funding_usdt") is not None]
            kap = datetime.datetime.strptime(son["ts"], F)
            tut = max((t.get("tutma_saat") or 0) for t in v)
            d = ilk.get("derinlik_giriste") or {}
            out.append(dict(
                defter=ad, id=i, sym=son["sym"], yon=son["yon"],
                giris_ts=kap - datetime.timedelta(hours=tut), kap_ts=kap,
                net=net + (sum(fon) if fon else 0.0), notional=no, tut=tut,
                ret=100.0 * (net + (sum(fon) if fon else 0.0)) / no,
                sebep=son.get("sebep"), kaldirac=ilk.get("kaldirac"),
                skor=ilk.get("skor_giriste"), chg24=ilk.get("chg24_giriste"),
                pos=ilk.get("range_pos_giriste"), smart=ilk.get("smart_giriste"),
                stage=ilk.get("stage_giriste"), rejim=ilk.get("rejim_giriste"),
                slipaj=d.get("slipaj_pct"),
                basi=(no / d["defter_usdt_20"]) if d.get("defter_usdt_20") else None,
                kismi=any(t.get("kismi") for t in v)))
    return out


P = pozisyonlar()
KAZ = [x for x in P if x["net"] > 0]
KAY = [x for x in P if x["net"] <= 0]

print("KAZANAN vs KAYBEDEN — ortak patern taramasi   [KESIFSEL · HUKUM YAZMAZ]")
print("=" * 118)
print("pozisyon %d  ·  KAZANAN %d (%%%.0f)  ·  KAYBEDEN %d"
      % (len(P), len(KAZ), 100.0 * len(KAZ) / len(P), len(KAY)))
print("  %-9s %6s %8s %8s | %10s %10s" % ("defter", "N", "kazanan", "%", "kaz ort ret", "kay ort ret"))
for ad, _ in DEFTERLER:
    w = [x for x in P if x["defter"] == ad]
    if not w:
        continue
    k = [x for x in w if x["net"] > 0]
    y = [x for x in w if x["net"] <= 0]
    print("  %-9s %6d %8d %7.0f%% | %+9.3f%% %+9.3f%%"
          % (ad, len(w), len(k), 100.0 * len(k) / len(w),
             sum(x["ret"] for x in k) / len(k) if k else 0,
             sum(x["ret"] for x in y) / len(y) if y else 0))


def kars(ad, anahtar, sayisal=True, sec=None):
    kz = [x[anahtar] for x in (sec or KAZ) if x.get(anahtar) is not None]
    ky = [x[anahtar] for x in KAY if x.get(anahtar) is not None]
    if sayisal:
        if len(kz) < 20 or len(ky) < 20:
            return
        mk, my = statistics.median(kz), statistics.median(ky)
        ok, oy = sum(kz) / len(kz), sum(ky) / len(ky)
        # etki buyuklugu (Cohen d benzeri, medyan farki / birlesik sapma)
        try:
            sd = statistics.pstdev(kz + ky)
            d = (ok - oy) / sd if sd else 0
        except Exception:
            d = 0
        print("   %-22s KAZ med %9.3f ort %9.3f (N=%4d) | KAY med %9.3f ort %9.3f (N=%4d) | d=%+.2f"
              % (ad, mk, ok, len(kz), my, oy, len(ky), d))
    else:
        ck = collections.Counter(kz)
        cy = collections.Counter(ky)
        anahtarlar = sorted(set(ck) | set(cy), key=lambda z: -(ck[z] + cy[z]))[:5]
        print("   %-22s %s" % (ad, "  ".join(
            "%s: KAZ%%%.0f/KAY%%%.0f" % (str(a)[:10], 100.0 * ck[a] / len(kz),
                                         100.0 * cy[a] / len(ky)) for a in anahtarlar)))


print("\n" + "=" * 118)
print("A) GIRIS ANI OZELLIKLERI — KARAR VERILEBILIR (tum defterler)")
print("=" * 118)
for ad, a in (("skor", "skor"), ("chg24 giriste", "chg24"), ("range_pos", "pos"),
              ("kaldirac", "kaldirac"), ("notional $", "notional"),
              ("poz/defter orani", "basi"), ("beklenen slipaj", "slipaj")):
    kars(ad, a)
print()
for ad, a in (("yon", "yon"), ("smart", "smart"), ("stage", "stage"),
              ("rejim", "rejim"), ("defter", "defter")):
    kars(ad, a, sayisal=False)

print("\n" + "=" * 118)
print("B) SONUC OZELLIKLERI — 🔴 DONGUSEL, karar icin KULLANILAMAZ (bilgi olsun diye)")
print("=" * 118)
for ad, a in (("tutma saati", "tut"), ("kismi kar alindi", "kismi")):
    kars(ad, a, sayisal=(a == "tut"))
print("   %-22s %s" % ("kapanis sebebi", "  ".join(
    "%s: KAZ%%%.0f/KAY%%%.0f" % (s, 100.0 * sum(1 for x in KAZ if x["sebep"] == s) / len(KAZ),
                                 100.0 * sum(1 for x in KAY if x["sebep"] == s) / len(KAY))
    for s in sorted({x["sebep"] for x in P}, key=lambda z: -sum(1 for x in P if x["sebep"] == z))[:5])))

# ---------------------------------------------------------------- 5 dk yol (testbot)
print("\n" + "=" * 118)
print("C) ILK 30 DAKIKA — KARAR VERILEBILIR (yalniz testbot, 5 dk izleme)")
print("=" * 118)
izl = collections.defaultdict(list)
for s in open(os.path.join(PROJE, "pozisyon_izleme.jsonl"), encoding="utf-8"):
    if not s.strip():
        continue
    try:
        x = json.loads(s)
    except Exception:
        continue
    if x.get("id") is not None:
        izl[x["id"]].append(x)
for i in izl:
    izl[i].sort(key=lambda z: z.get("ts") or "")

tb = {x["id"]: x for x in P if x["defter"] == "testbot"}
satir = []
for i, snaps in izl.items():
    p = tb.get(i)
    if not p:
        continue
    ilk = snaps[0]
    # ilk 30 dakikadaki kareler
    erken = [s for s in snaps if (s.get("yas_saat") or 0) <= 0.5]
    if not erken:
        erken = snaps[:1]
    son_e = erken[-1]
    ag = ilk.get("atr_giriste")
    ac = son_e.get("atr_canli")
    satir.append(dict(
        kazandi=p["net"] > 0, ret=p["ret"],
        ilk_pnl=ilk.get("pnl_pct"), e30_pnl=son_e.get("pnl_pct"),
        e30_mae=son_e.get("mae_pct"), e30_mfe=son_e.get("mfe_pct"),
        e30_arti=(100.0 * (son_e.get("arti_dakika") or 0) / (son_e.get("toplam_dakika") or 1)),
        stop_mes=ilk.get("stop_mesafe_pct"),
        stopa_uz=son_e.get("stopa_uzaklik_pct"),
        atr_genis=(ac / ag) if (ag and ac) else None,
        d_taker=son_e.get("d_taker"), taker15=son_e.get("taker_15"),
        hacim_x=son_e.get("hacim_x"), kum_taker=son_e.get("kum_taker_oran"),
        ma50=ilk.get("ma50_mesafe"), kare=len(erken)))
K1 = [x for x in satir if x["kazandi"]]
K0 = [x for x in satir if not x["kazandi"]]
print("izlenen testbot pozisyonu %d  ·  kazanan %d  ·  kaybeden %d" % (len(satir), len(K1), len(K0)))


def kars2(ad, a):
    kz = [x[a] for x in K1 if x.get(a) is not None]
    ky = [x[a] for x in K0 if x.get(a) is not None]
    if len(kz) < 15 or len(ky) < 15:
        print("   %-24s N yetersiz (%d/%d)" % (ad, len(kz), len(ky)))
        return
    ok, oy = sum(kz) / len(kz), sum(ky) / len(ky)
    sd = statistics.pstdev(kz + ky)
    print("   %-24s KAZ med %8.3f ort %8.3f | KAY med %8.3f ort %8.3f | d=%+.2f"
          % (ad, statistics.median(kz), ok, statistics.median(ky), oy,
             (ok - oy) / sd if sd else 0))


print("\n   -- girisin ILK karesi (t=0) --")
for ad, a in (("ilk kare pnl%", "ilk_pnl"), ("giris stop mesafesi%", "stop_mes"),
              ("MA50 mesafesi", "ma50")):
    kars2(ad, a)
print("\n   -- ilk 30 DAKIKA sonunda --")
for ad, a in (("pnl%", "e30_pnl"), ("en kotu nokta (MAE)", "e30_mae"),
              ("en iyi nokta (MFE)", "e30_mfe"), ("artida gecen sure %", "e30_arti"),
              ("stopa uzaklik %", "stopa_uz"), ("ATR genislemesi (canli/giris)", "atr_genis"),
              ("d_taker", "d_taker"), ("taker_15", "taker15"),
              ("hacim_x", "hacim_x"), ("kumulatif taker orani", "kum_taker")):
    kars2(ad, a)

print("\n   -- ILK 30 DAKIKA AYIRICI MI? (esik taramasi) --")
for ad, a, ters in (("30dk pnl > 0", "e30_pnl", False),
                    ("30dk MAE > -%1", "e30_mae", True),
                    ("30dk artida %50+", "e30_arti", False)):
    w = [x for x in satir if x.get(a) is not None]
    if len(w) < 40:
        continue
    if a == "e30_pnl":
        us = [x for x in w if x[a] > 0]
        al = [x for x in w if x[a] <= 0]
    elif a == "e30_mae":
        us = [x for x in w if x[a] > -1]
        al = [x for x in w if x[a] <= -1]
    else:
        us = [x for x in w if x[a] >= 50]
        al = [x for x in w if x[a] < 50]
    if len(us) >= 15 and len(al) >= 15:
        print("   %-20s SAGLAYAN N=%3d kazanma %%%2.0f ort ret %+7.3f%%  |  SAGLAMAYAN N=%3d %%%2.0f %+7.3f%%"
              % (ad, len(us), 100.0 * sum(1 for x in us if x["kazandi"]) / len(us),
                 sum(x["ret"] for x in us) / len(us),
                 len(al), 100.0 * sum(1 for x in al if x["kazandi"]) / len(al),
                 sum(x["ret"] for x in al) / len(al)))

print("\n" + "=" * 118)
print("D) ATLANMIS ALANLAR — izlemede TOPLANIYOR ama hicbir olcumde KULLANILMADI")
print("=" * 118)
kullanilan = {"pnl_pct", "pnl_usd", "pnl_r", "mfe_pct", "mae_pct", "tepe_pnl_pct", "dip_pnl_pct",
              "arti_dakika", "eksi_dakika", "notr_dakika", "toplam_dakika", "chg24", "funding",
              "score", "taker_15", "taker_60", "d_taker", "hacim_15_usdt", "hacim_60_usdt",
              "oi3", "oi24", "top_ls", "glob_ls", "smart", "taker", "vol_x", "pos", "yas_saat",
              "sym", "yon", "id", "ts", "giris", "stop", "tp2", "fiyat", "kaynak", "notional",
              "marjin", "kaldirac", "miktar", "giris_ts", "stopa_uzaklik_pct", "hedefe_uzaklik_pct",
              "mcap", "stage", "kapi", "rel3", "ayrisma", "comp", "last1", "last3", "dip_yakit",
              "dusuk_float", "float_oran", "d_pnl_pct", "tepe_ts", "dip_ts", "btc_chg3"}
tum = set(izl[list(izl)[0]][0].keys()) if izl else set()
atlanan = sorted(tum - kullanilan)
for k in atlanan:
    ornek = [s.get(k) for i in list(izl)[:40] for s in izl[i][:1] if s.get(k) is not None]
    print("   %-24s dolu ornek: %s" % (k, str(ornek[:3])[:60] if ornek else "-"))
print("\n   (bu liste 'hic olculmedi' demektir, 'degerli' demek DEGIL)")
print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
