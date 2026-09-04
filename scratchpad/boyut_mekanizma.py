#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOYUT-KAYIP MEKANIZMASI — on-kayitli zincir KOPTU, dogru zincir aranıyor.
On-kayit: ON_KAYIT_boyutlandirma.md s.5, "M2 pozitif cikarsa zincir KOPAR ve
boyut-kayip iliskisinin BASKA bir aciklamasi aranir" — bu betik o aramadir.

Olculen (boyut_karsi_olgu.py):
  M1 notional~ret  -0,303 (t -6,15)   <- guclu negatif
  M2 skor~ret      +0,009              <- skor YORDAMIYOR
  M3 skor~notional -0,028              <- skor boyutu BELIRLEMIYOR (!)
  EK marjin~ret    -0,573 (t -13,54)   <- EN GUCLU

KOD OKUNDU (testbot.py:1237-1241):
    kald_gerekli = (hedef_risk / stop_frac) / marjin
    risk_usdt = stop_frac * notional
    if risk_usdt > hedef_risk: hepsi `hedef_risk/risk_usdt` ile KUCULTULUR
  => notional <= hedef_risk / stop_frac  ->  BOYUT, STOP MESAFESIYLE TERS ORANTILI.

ADAY MEKANIZMA: dar stop -> BUYUK pozisyon; dar stop -> daha sik vurulur.
🔴 Bu ADAY, sonucu gordukten SONRA olusturuldu — dogrulanmasi gerekir, ve
   dogrulansa bile kendi on-kaydini hak eder. Burada YALNIZ sinaniyor.

⚠️ stop_mesafe GIRIS aninda belirlenir (sonuc-oncesi) -> ona kosullamak
   TP1'deki gibi asiri kontrol DEGILDIR.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, math, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pearson(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return None
    return sum((x[i] - mx) * (y[i] - my) for i in range(n)) / (sx * sy)


def kor_t(r, n):
    if r is None or n < 4 or abs(r) >= 1:
        return None
    return r * math.sqrt((n - 2) / (1 - r * r))


def kismi(rxy, rxz, ryz):
    """r(x,y | z)"""
    if None in (rxy, rxz, ryz):
        return None
    d = math.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
    return (rxy - rxz * ryz) / d if d else None


def main():
    # ---- pozisyonlar
    ham = collections.defaultdict(list)
    for l in open(os.path.join(PROJE, "testbot_islemler.jsonl"), encoding="utf-8"):
        l = l.strip()
        if l:
            try:
                r = json.loads(l)
            except Exception:
                continue
            if r.get("id") is not None:
                ham[r["id"]].append(r)
    poz = {}
    for i, v in ham.items():
        v.sort(key=lambda z: z["ts"])
        ilk, son = v[0], v[-1]
        no = ilk.get("notional") or 0
        if no <= 0:
            continue
        net = sum((t.get("sonuc_usdt") or 0) for t in v)
        fl = [t.get("funding_usdt") for t in v if t.get("funding_usdt") is not None]
        net += sum(fl) if fl else 0.0
        poz[i] = {"notional": no, "marjin": ilk.get("marjin") or 0,
                  "kaldirac": ilk.get("kaldirac") or 0, "net": net,
                  "ret": 100.0 * net / no, "sebep": son.get("sebep"),
                  "tut": max((t.get("tutma_saat") or 0) for t in v)}

    # ---- ilk izleme anindaki stop mesafesi
    ilk_izl = {}
    for l in open(os.path.join(PROJE, "pozisyon_izleme.jsonl"), encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        i = r.get("id")
        if i is None or r.get("stop_mesafe_pct") is None:
            continue
        t = r.get("ts") or ""
        if i not in ilk_izl or t < ilk_izl[i][0]:
            ilk_izl[i] = (t, abs(float(r["stop_mesafe_pct"])))

    W = [dict(poz[i], stop=ilk_izl[i][1]) for i in poz if i in ilk_izl and ilk_izl[i][1] > 0]
    print("BOYUT-KAYIP MEKANIZMASI — aday: 'boyut stop mesafesiyle ters orantili'")
    print("=" * 100)
    print("eslesen pozisyon: %d / %d  (izlemede stop_mesafe_pct olanlar)" % (len(W), len(poz)))
    if len(W) < 30:
        print("N yetersiz")
        return

    no = [p["notional"] for p in W]
    mj = [p["marjin"] for p in W]
    st = [p["stop"] for p in W]
    rt = [p["ret"] for p in W]
    n = len(W)

    print("\n1) ZINCIRIN HALKALARI")
    print("-" * 100)
    print("  %-40s %10s %9s" % ("olcum", "korelasyon", "t"))
    ciftler = [("stop mesafesi ~ notional  (kod: ters)", st, no),
               ("stop mesafesi ~ marjin", st, mj),
               ("stop mesafesi ~ ret", st, rt),
               ("notional ~ ret", no, rt),
               ("marjin ~ ret", mj, rt)]
    R = {}
    for ad, a, b in ciftler:
        r = pearson(a, b)
        R[ad] = r
        print("  %-40s %+10.3f %9s" % (ad, r, ("%+.2f" % kor_t(r, n)) if r else "-"))

    # log-donusum: iliski carpimsal (notional ~ 1/stop)
    lst = [math.log(x) for x in st]
    lno = [math.log(x) for x in no]
    rl = pearson(lst, lno)
    print("  %-40s %+10.3f %9s" % ("log(stop) ~ log(notional)", rl,
                                   ("%+.2f" % kor_t(rl, n)) if rl else "-"))
    print("     -> kod 'notional <= hedef_risk/stop_frac' diyor; tam ters orantida")
    print("        log-log korelasyonu -1'e yakin olmali.")

    print("\n2) 🔑 BELIRLEYICI SINAMA — stop mesafesi SABITLENINCE boyut hala ayiriyor mu?")
    print("-" * 100)
    r_no_ret = pearson(no, rt)
    r_no_st = pearson(no, st)
    r_st_ret = pearson(st, rt)
    k = kismi(r_no_ret, r_no_st, r_st_ret)
    print("  ham       notional~ret            : %+.3f  (t %s)"
          % (r_no_ret, ("%+.2f" % kor_t(r_no_ret, n)) if r_no_ret else "-"))
    print("  KISMI     notional~ret | stop     : %+.3f  (t %s)"
          % (k, ("%+.2f" % kor_t(k, n - 1)) if k else "-"))
    if k is not None and r_no_ret:
        print("  -> aciklanan pay: %%%.0f" % (100.0 * (1 - abs(k) / abs(r_no_ret))))
        if abs(k) < 0.5 * abs(r_no_ret):
            print("  -> MEKANIZMA BUYUK OLCUDE STOP MESAFESI. Boyut formulunun kendisi degil,")
            print("     boyutu belirleyen STOP GENISLIGI ayiriyor.")
        else:
            print("  -> stop mesafesi tek basina ACIKLAMIYOR; baska kanal var.")

    print("\n3) STOP MESAFESI DILIMLERI — betimleyici")
    print("-" * 100)
    s = sorted(W, key=lambda p: p["stop"])
    d = len(s) // 4
    print("  %-14s %5s %9s %12s %10s %11s %9s %8s"
          % ("dilim", "N", "stop%", "ort notional", "ort ret%", "net $", "kazanan", "STOP%"))
    for i, ad in enumerate(("Q1 en dar", "Q2", "Q3", "Q4 en genis")):
        w = s[i * d:(i + 1) * d] if i < 3 else s[3 * d:]
        stp = sum(1 for p in w if str(p["sebep"]).upper() == "STOP")
        print("  %-14s %5d %8.2f%% %11.0f $ %+9.3f%% %+10.2f %8.0f%% %7.0f%%"
              % (ad, len(w), sum(p["stop"] for p in w) / len(w),
                 sum(p["notional"] for p in w) / len(w),
                 sum(p["ret"] for p in w) / len(w), sum(p["net"] for p in w),
                 100.0 * sum(1 for p in w if p["net"] > 0) / len(w),
                 100.0 * stp / len(w)))

    print("\n4) 🔴 DOLAR RISKI SABIT MI? (risk-paritesi tasarimin AMACI)")
    print("-" * 100)
    print("  Tasarim: risk_usdt = stop_frac x notional <= hedef_risk -> her poz AYNI dolar riski")
    print("  %-14s %5s %14s %14s" % ("dilim", "N", "ort risk $", "ort |kayip| $"))
    for i, ad in enumerate(("Q1 en dar", "Q2", "Q3", "Q4 en genis")):
        w = s[i * d:(i + 1) * d] if i < 3 else s[3 * d:]
        risk = [p["stop"] / 100.0 * p["notional"] for p in w]
        kay = [abs(p["net"]) for p in w if p["net"] < 0]
        print("  %-14s %5d %13.2f $ %13.2f $"
              % (ad, len(w), sum(risk) / len(risk),
                 (sum(kay) / len(kay)) if kay else 0.0))
    print("  -> risk kolonu dilimler arasi SABITSE tasarim calisiyor demektir;")
    print("     ayrisiyorsa kirpma/kaldirac tavani devreye giriyor ve parite BOZULUYOR.")

    print("\n" + "=" * 100)
    print("⚠️ Bu bolum sonucu gordukten SONRA olusturulmus bir ADAYIN sinamasidir.")
    print("   Dogrulansa bile KURAL DEGIL — kendi on-kaydini ve portfoy asamasini hak eder.")
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
