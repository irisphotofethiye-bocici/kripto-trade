#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""YON KARISIMI — kapilar bogayi algiladi mi?  (kullanici sorusu)

Karistirici: 08-18'de LONG payi %100 gorunuyor AMA fren TUM SHORT adaylarini
kesmisti. "Kapi bogayi gordu" ile "fren shortu kesti" AYRILMALI.

UC KATMAN:
  1. HAM KAPI KARARI (veto ONCESI) — kapi mantiginin kendi yon egilimi
  2. VETO SONRASI                  — fren/blowoff/long_veto neyi kesti
  3. ACILAN POZISYON               — kapasite + giris kapilari neyi birakti

Ayrica: fren vetosu SIFIR olan gunler ayri (temiz karsilastirma),
aday havuzu degisti mi, ve SANS OLCUMU.

SALT OKUMA.
"""
import sys, os, json, collections, random, statistics as stx

HERE = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ortak                                    # noqa: E402

BAS = "2026-08-11"
SICRAMA_GUN = "2026-08-18"
random.seed(41)


def aday_oku():
    out = []
    with open(os.path.join(PROJE, "testbot_aday_arsiv.jsonl"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            x = json.loads(line)
            if x["ts"][:10] >= BAS:
                out.append(x)
    return out


def main():
    ad = aday_oku()
    print("YON KARISIMI — kapilar bogayi algiladi mi?")
    print("=" * 92)
    print("Aday kaydi: %d  (%s .. %s)" % (len(ad), ad[0]["ts"], ad[-1]["ts"]))

    # ---------- KATMAN 1: ham kapi karari ----------
    g = collections.defaultdict(lambda: collections.Counter())
    for x in ad:
        k = x.get("karar") or "yok"
        gun = x["ts"][:10]
        if k.startswith("LONG"):
            g[gun]["L"] += 1
        elif k.startswith("SHORT"):
            g[gun]["S"] += 1
        elif k == "VETO:btc_pay_freni":
            g[gun]["fren"] += 1
        elif k.startswith("VETO:long"):
            g[gun]["long_veto"] += 1
        elif k.startswith("VETO"):
            g[gun]["dv"] += 1
        g[gun]["hepsi"] += 1

    print("\n### KATMAN 1 — HAM KAPI KARARI (veto ONCESI)")
    print("%-12s %6s %6s %9s %8s %10s %8s %s"
          % ("gun", "LONG", "SHORT", "long pay", "fren", "long_veto", "aday", "not"))
    temiz = []
    for d in sorted(g):
        c = g[d]
        L, S = c["L"], c["S"]
        pay = 100 * L / max(1, L + S)
        nt = ""
        if c["fren"] > 0:
            nt = "<-- fren aktif, long payi SISIRILMIS"
        else:
            temiz.append((d, L, S, pay))
        print("%-12s %6d %6d     %%%3.0f %8d %10d %8d %s"
              % (d, L, S, pay, c["fren"], c["long_veto"], c["hepsi"], nt))

    # ---------- FREN-SIFIR gunlerde temiz karsilastirma ----------
    print("\n### FREN HIC CALISMAYAN GUNLER — tek adil karsilastirma")
    onc = [t for t in temiz if t[0] < SICRAMA_GUN]
    son = [t for t in temiz if t[0] >= SICRAMA_GUN]
    for adi, gg in (("sicrama ONCESI", onc), ("sicrama SONRASI", son)):
        if not gg:
            print("  %-16s gun yok" % adi)
            continue
        L = sum(t[1] for t in gg)
        S = sum(t[2] for t in gg)
        print("  %-16s %d gun · LONG %3d · SHORT %3d · long pay %%%.1f   (gunler: %s)"
              % (adi, len(gg), L, S, 100 * L / max(1, L + S), ", ".join(t[0][5:] for t in gg)))

    # ---------- KATMAN 3: acilan pozisyon ----------
    print("\n### KATMAN 3 — ACILAN POZISYON (giris gunune gore)")
    poz = ortak.poz_yukle()
    pg = collections.defaultdict(lambda: collections.Counter())
    for p in poz:
        pg[p["giris_ts"][:10]][p["yon"]] += 1
    for d in sorted(pg):
        c = pg[d]
        L, S = c["LONG"], c["SHORT"]
        print("  %-12s LONG %2d · SHORT %2d · long pay %%%3.0f%s"
              % (d, L, S, 100 * L / max(1, L + S),
                 "   <-- fren aktifti" if g[d]["fren"] > 0 else ""))

    # ---------- ADAY HAVUZU degisti mi ----------
    print("\n### ADAY HAVUZU — 'kapi mi degisti, piyasa mi?'")
    hv = collections.defaultdict(list)
    for x in ad:
        if x.get("chg24") is not None:
            hv[x["ts"][:10]].append(x["chg24"])
    print("%-12s %7s %11s %11s %11s"
          % ("gun", "aday", "chg24 med", "yukselen %", ">%10 yukselen"))
    for d in sorted(hv):
        v = hv[d]
        print("%-12s %7d %+10.2f %10.0f%% %10.0f%%"
              % (d, len(v), stx.median(v),
                 100 * sum(1 for z in v if z > 0) / len(v),
                 100 * sum(1 for z in v if z > 10) / len(v)))

    # ---------- SANS OLCUMU ----------
    print("\n### SANS OLCUMU — '%9 -> %24 sicramasi rastgele ne siklikla olur?'")
    print("Yontem: HER aday karari (LONG/SHORT) havuza atilir, gun etiketleri")
    print("1000 kez KARISTIRILIR, ayni 'son 2 gun vs oncesi' farki yeniden olculur.")
    kar = []
    for x in ad:
        k = x.get("karar") or ""
        if k.startswith("LONG"):
            kar.append((x["ts"][:10], 1))
        elif k.startswith("SHORT"):
            kar.append((x["ts"][:10], 0))
    # gercek fark: fren-sifir gunler uzerinde
    tg = {t[0] for t in temiz}
    ger_s = [z for z in kar if z[0] in tg and z[0] >= SICRAMA_GUN]
    ger_o = [z for z in kar if z[0] in tg and z[0] < SICRAMA_GUN]
    if not ger_s or not ger_o:
        print("  fren-sifir gunlerde iki donem birden yok -> olcum yapilamiyor")
        return
    f_ger = (100 * sum(z[1] for z in ger_s) / len(ger_s)
             - 100 * sum(z[1] for z in ger_o) / len(ger_o))
    havuz = ger_s + ger_o
    n_s = len(ger_s)
    sahte = []
    for _ in range(1000):
        random.shuffle(havuz)
        a, b = havuz[:n_s], havuz[n_s:]
        sahte.append(100 * sum(z[1] for z in a) / len(a)
                     - 100 * sum(z[1] for z in b) / len(b))
    ust = sum(1 for z in sahte if z >= f_ger)
    print("  GERCEK fark (long payi, sonrasi - oncesi): %+.1f puan" % f_ger)
    print("  karistirilmis 1000 turda ortalama %+.1f · sapma %.1f" % (stx.mean(sahte), stx.pstdev(sahte)))
    print("  bu kadar veya daha buyuk fark SANS ESERI: %d/1000  ->  p = %.3f" % (ust, ust / 1000))
    print("  %s" % ("-> SANS ILE ACIKLANAMIYOR (p<0.05)" if ust / 1000 < 0.05
                    else "-> SANSTAN AYIRT EDILEMIYOR"))
    print("\n  UYARI (pesinen yazildi): LONG kararlari gunde 0-18 arasi. N kucuktur;")
    print("  sonuc ne cikarsa ciksin ISARETTIR, kanit degil.")
    print("\nbot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
