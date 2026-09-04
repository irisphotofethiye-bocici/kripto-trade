#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOYUTLANDIRMA KARSI-OLGUSU — secim degil agirlik mi kaybettiriyor?
On-kayit: ON_KAYIT_boyutlandirma.md (commit 161271f, KOSUMDAN ONCE). Olcutler SABIT.

Karsi-olgu aritmetigi (kagit defter oldugu icin gecerli — boyut fiyat yolunu
etkilemez, dolayisiyla ret_i boyuttan BAGIMSIZ):
    gercek P&L = SUM( ret_i/100 * notional_i )
    esit   P&L = SUM( ret_i/100 * ortalama_notional )

🔴 TP1'E BAKILMAZ ve bakilmamalidir: TP1 sonucun parcasi, nedensel yolun
   UZERINDE. Ona kosullamak olculmek istenen kanali KAPATIR (asiri kontrol).
   Onceki geri cekilen bulgu BASKA bir iddiaydi (secim), bu muhasebedir.

CLAUDE.md: birim POZISYON (id ile birlestirme) · P&L toplarken `kismi` SUZULMEZ ·
net = sonuc_usdt + funding_usdt.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, math, random, datetime, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFTER = os.path.join(PROJE, "testbot_islemler.jsonl")
PERM = 10000
random.seed(20260904)


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


def pozisyonlar():
    ham = collections.defaultdict(list)
    for l in open(DEFTER, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r.get("id") is not None:
            ham[r["id"]].append(r)
    out = []
    for i, v in ham.items():
        v.sort(key=lambda z: z["ts"])
        ilk, son = v[0], v[-1]
        no = ilk.get("notional") or 0
        if no <= 0:
            continue
        net = sum((t.get("sonuc_usdt") or 0) for t in v)
        fl = [t.get("funding_usdt") for t in v if t.get("funding_usdt") is not None]
        net += sum(fl) if fl else 0.0
        tut = max((t.get("tutma_saat") or 0) for t in v)
        try:
            kap = datetime.datetime.strptime(son["ts"], "%Y-%m-%d %H:%M:%S")
            gir = kap - datetime.timedelta(hours=tut)
        except Exception:
            gir = None
        out.append({
            "id": i, "sym": son["sym"], "yon": son["yon"],
            "notional": no, "marjin": ilk.get("marjin") or 0,
            "kaldirac": ilk.get("kaldirac") or 0,
            "skor": ilk.get("skor_giriste"),
            "rejim": str(ilk.get("rejim_giriste") or "?"),
            "kapi": str(ilk.get("sebep_giris") or "?").split(":")[0].strip()[:14],
            "net": net, "ret": 100.0 * net / no,
            "giris": gir, "tut": tut,
        })
    out.sort(key=lambda p: p["giris"] or datetime.datetime(1970, 1, 1))
    return out


def karsi_olgu(poz):
    """(gercek, esit, fark)"""
    if not poz:
        return 0.0, 0.0, 0.0
    g = sum(p["net"] for p in poz)
    ort_no = sum(p["notional"] for p in poz) / len(poz)
    e = sum(p["ret"] / 100.0 * ort_no for p in poz)
    return g, e, e - g


def main():
    poz = pozisyonlar()
    print("BOYUTLANDIRMA KARSI-OLGUSU")
    print("on-kayit ON_KAYIT_boyutlandirma.md (161271f) · olcutler SABIT")
    print("=" * 100)
    print("pozisyon %d · %s .. %s"
          % (len(poz),
             poz[0]["giris"].date() if poz[0]["giris"] else "?",
             poz[-1]["giris"].date() if poz[-1]["giris"] else "?"))
    print("🔴 TP1'e BAKILMADI (asiri kontrol olurdu — bkz. on-kayit s.2)")

    g, e, f = karsi_olgu(poz)
    ort_no = sum(p["notional"] for p in poz) / len(poz)
    print("\n" + "=" * 100)
    print("1) HAVUZ — karsi-olgu")
    print("-" * 100)
    print("  gercek P&L            : %+10.2f $" % g)
    print("  ESIT AGIRLIK P&L      : %+10.2f $   (her poz %.0f $ notional)" % (e, ort_no))
    print("  fark (esit - gercek)  : %+10.2f $" % f)
    print("  ortalama getiri       : %+10.3f %%" % (sum(p["ret"] for p in poz) / len(poz)))
    print("  NOT: havuzda pozitif cikmasi neredeyse GARANTI (on-kayit s.4) —")
    print("       hukum tasiyan sinama asagidaki BOLUNMUS YARI.")

    # ---------------------------------------------------------------- K1
    print("\n" + "=" * 100)
    print("2) K1 — BOLUNMUS YARI TEKRARI (birincil, hukum tasir)")
    print("-" * 100)
    yari = len(poz) // 2
    A, B = poz[:yari], poz[yari:]
    print("  %-6s %5s %-24s %11s %11s %11s"
          % ("yari", "N", "donem", "gercek $", "esit $", "fark $"))
    sonuc = {}
    for ad, w in (("A", A), ("B", B)):
        gg, ee, ff = karsi_olgu(w)
        sonuc[ad] = ff
        d0 = w[0]["giris"].date() if w[0]["giris"] else "?"
        d1 = w[-1]["giris"].date() if w[-1]["giris"] else "?"
        print("  %-6s %5d %-24s %+10.2f %+10.2f %+10.2f"
              % (ad, len(w), "%s .. %s" % (d0, d1), gg, ee, ff))
    k1 = sonuc["A"] > 0 and sonuc["B"] > 0
    print("  -> K1: %s  (A %+.2f · B %+.2f)"
          % ("GECTI" if k1 else "DUSTU", sonuc["A"], sonuc["B"]))

    # ---------------------------------------------------------------- K2
    print("\n" + "=" * 100)
    print("3) K2 — PERMUTASYON BOS HIPOTEZI (%d karistirma)" % PERM)
    print("   'herhangi bir agirliklandirma bu kadar kotu olur muydu?'")
    print("-" * 100)
    rets = [p["ret"] / 100.0 for p in poz]
    nos = [p["notional"] for p in poz]
    dagilim = []
    for _ in range(PERM):
        random.shuffle(nos)
        dagilim.append(sum(rets[i] * nos[i] for i in range(len(rets))))
    dagilim.sort()
    alt = sum(1 for x in dagilim if x <= g)
    yzd = 100.0 * alt / PERM
    q = lambda p: dagilim[min(PERM - 1, int(p * PERM))]
    print("  gercek P&L                   : %+10.2f $" % g)
    print("  karistirilmis dagilim  %%5    : %+10.2f $" % q(0.05))
    print("                        medyan : %+10.2f $" % q(0.50))
    print("                         %%95   : %+10.2f $" % q(0.95))
    print("  gercek degerin YUZDELIGI     : %%%.2f" % yzd)
    k2 = yzd <= 5.0
    print("  -> K2: %s  (esik: alt %%5)" % ("GECTI" if k2 else "DUSTU"))

    # ---------------------------------------------------------------- K3
    print("\n" + "=" * 100)
    print("4) K3 — UC DEGER DAYANIKLILIGI")
    print("-" * 100)
    print("  %-26s %5s %11s %11s %11s %8s"
          % ("kesit", "N", "gercek $", "esit $", "fark $", "A/B"))
    k3ok = True
    for ad, kes in (("tum", 0), ("en buyuk 5 notional atildi", 5), ("en buyuk 20 atildi", 20)):
        s = sorted(poz, key=lambda p: -p["notional"])[kes:]
        s.sort(key=lambda p: p["giris"] or datetime.datetime(1970, 1, 1))
        gg, ee, ff = karsi_olgu(s)
        y = len(s) // 2
        fa = karsi_olgu(s[:y])[2]
        fb = karsi_olgu(s[y:])[2]
        ok = fa > 0 and fb > 0
        if kes:
            k3ok = k3ok and ok
        print("  %-26s %5d %+10.2f %+10.2f %+10.2f %8s"
              % (ad, len(s), gg, ee, ff, "OK" if ok else "DUSTU"))
    print("  -> K3: %s" % ("GECTI" if k3ok else "DUSTU"))

    # ---------------------------------------------------------------- mekanizma
    print("\n" + "=" * 100)
    print("5) MEKANIZMA — zincir  skor -> boyut -> kayip  (on-kayit s.5)")
    print("-" * 100)
    r_ = [p["ret"] for p in poz]
    n_ = [p["notional"] for p in poz]
    sk = [(p["skor"], p["ret"], p["notional"]) for p in poz if p["skor"] is not None]
    print("  %-34s %9s %9s %6s" % ("olcum", "korelasyon", "t", "N"))
    m1 = pearson(n_, r_)
    print("  %-34s %+9.3f %9s %6d" % ("M1  notional ~ ret", m1,
                                      ("%+.2f" % kor_t(m1, len(r_))) if m1 else "-", len(r_)))
    if sk:
        a = [x[0] for x in sk]
        b = [x[1] for x in sk]
        c = [x[2] for x in sk]
        m2 = pearson(a, b)
        m3 = pearson(a, c)
        print("  %-34s %+9.3f %9s %6d" % ("M2  skor ~ ret", m2,
                                          ("%+.2f" % kor_t(m2, len(a))) if m2 else "-", len(a)))
        print("  %-34s %+9.3f %9s %6d" % ("M3  skor ~ notional", m3,
                                          ("%+.2f" % kor_t(m3, len(a))) if m3 else "-", len(a)))
        kl = [p["kaldirac"] for p in poz]
        m4 = pearson(kl, r_)
        print("  %-34s %+9.3f %9s %6d" % ("EK  kaldirac ~ ret", m4,
                                          ("%+.2f" % kor_t(m4, len(r_))) if m4 else "-", len(r_)))
        m5 = pearson([p["marjin"] for p in poz], r_)
        print("  %-34s %+9.3f %9s %6d" % ("EK  marjin ~ ret", m5,
                                          ("%+.2f" % kor_t(m5, len(r_))) if m5 else "-", len(r_)))
        print()
        zincir = (m1 is not None and m1 < 0) and (m3 is not None and m3 > 0) \
            and not (m2 is not None and m2 > 0)
        print("  ZINCIR KURULDU MU: %s" % ("EVET" if zincir else "HAYIR — KOPUK"))
        if not zincir and m2 is not None and m2 > 0:
            print("    (M2 POZITIF -> skor aslinda yorduyor; boyut-kayip iliskisinin")
            print("     baska aciklamasi aranmali: kaldirac, rejim, tutma suresi)")

    # ------------------------------------------------------- boyut dilimleri
    print("\n" + "=" * 100)
    print("6) BOYUT DILIMLERI — betimleyici")
    print("-" * 100)
    s = sorted(poz, key=lambda p: p["notional"])
    d = len(s) // 4
    print("  %-10s %5s %12s %11s %11s %9s"
          % ("dilim", "N", "ort notional", "ort ret%", "net $", "kazanan"))
    for i, ad in enumerate(("Q1 kucuk", "Q2", "Q3", "Q4 buyuk")):
        w = s[i * d:(i + 1) * d] if i < 3 else s[3 * d:]
        print("  %-10s %5d %11.0f $ %+10.3f%% %+10.2f %8.0f%%"
              % (ad, len(w), sum(p["notional"] for p in w) / len(w),
                 sum(p["ret"] for p in w) / len(w), sum(p["net"] for p in w),
                 100.0 * sum(1 for p in w if p["net"] > 0) / len(w)))

    # ------------------------------------------------------- rejim/kapi (betimleyici)
    print("\n" + "=" * 100)
    print("7) KIRILIMLAR — BETIMLEYICI, hukum tasimaz")
    print("-" * 100)
    for alan in ("rejim", "yon"):
        print("  --- %s ---" % alan)
        gr = collections.defaultdict(list)
        for p in poz:
            gr[p[alan]].append(p)
        for k in sorted(gr, key=lambda z: -len(gr[z])):
            gg, ee, ff = karsi_olgu(gr[k])
            print("    %-10s N=%3d  gercek %+9.2f  esit %+9.2f  fark %+9.2f"
                  % (k, len(gr[k]), gg, ee, ff))

    # ---------------------------------------------------------------- hukum
    print("\n" + "=" * 100)
    print("HUKUM")
    print("=" * 100)
    print("  K1 bolunmus yari : %s" % ("GECTI" if k1 else "DUSTU"))
    print("  K2 permutasyon   : %s" % ("GECTI" if k2 else "DUSTU"))
    print("  K3 uc deger      : %s" % ("GECTI" if k3ok else "DUSTU"))
    if k1 and k2 and k3ok:
        h = "GECTI — agirliklandirma sistematik olarak kotu"
    elif k1 and k2:
        h = "ZAYIF — K1+K2 gecti, uc degerlere dayanikli DEGIL"
    else:
        h = "DUSTU"
    print("  -> %s" % h)
    print()
    print("  ⚠️ GECSE BILE KURAL DEGIL (on-kayit s.6):")
    print("     karsi-olgu portfoy kisitlarini (8 slot · %25 fren · marjin tavani)")
    print("     YOK SAYIYOR. Sonraki asama portfoy simulasyonu, kod degisikligi DEGIL.")
    print("     Ayrica kagit defter varsayimi (boyut fiyati etkilemez) GERCEK PARADA gecersiz.")

    print("\n" + "=" * 100)
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
