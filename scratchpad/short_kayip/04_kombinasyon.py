#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KOMBINASYON ARAMASI + SANS OLCUMU + GERCEK HOLDOUT

SORU (kullanici): "bu girisler hangi kombinasyonda zarar etmezdi?"

TEHLIKE: 27 alandan 77 kosul, 76.153 kural. N=103. Bu kadar cok kural
denenince EN IYISI SANS ESERI harika gorunur — GARANTI. O yuzden ayni
arama, sonuclari KARISTIRILMIS veride de kosturulur ve karsilastirilir.

CIKTI: gercek en iyi kural  VS  sahte en iyi kurallarin dagilimi.

SALT OKUMA.
"""
import sys, os, random, itertools, statistics as stx, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ortak                                    # noqa: E402
import kosul                                    # noqa: E402

MIN_N = 15          # bir kural en az bu kadar islem birakmali (aksi halde anlamsiz)
KARIS_2 = 1000      # 1-li + 2-li icin karistirma sayisi
KARIS_3 = 100       # 3-lu icin (cok daha pahali)
random.seed(41)


def kurallar(ks, mask, n, derece):
    """-> [(ad, idx_tuple)]  ·  MIN_N altini eler."""
    out = []
    if derece == 1:
        for i, (ad, _) in enumerate(ks):
            idx = tuple(j for j in range(n) if mask[i][j])
            if len(idx) >= MIN_N:
                out.append((ad, idx))
    elif derece == 2:
        for a, b in itertools.combinations(range(len(ks)), 2):
            ma, mb = mask[a], mask[b]
            idx = tuple(j for j in range(n) if ma[j] and mb[j])
            if len(idx) >= MIN_N:
                out.append((ks[a][0] + " & " + ks[b][0], idx))
    else:
        for a, b, c in itertools.combinations(range(len(ks)), 3):
            ma, mb, mc = mask[a], mask[b], mask[c]
            idx = tuple(j for j in range(n) if ma[j] and mb[j] and mc[j])
            if len(idx) >= MIN_N:
                out.append((ks[a][0] + " & " + ks[b][0] + " & " + ks[c][0], idx))
    return out


def degerlendir(kr, pnl):
    """-> (en_iyi_toplam, en_iyi_ad, sifir_ustu_kural_sayisi)"""
    en, ad, sif = None, None, 0
    for k, idx in kr:
        t = 0.0
        for j in idx:
            t += pnl[j]
        if t >= 0:
            sif += 1
        if en is None or t > en:
            en, ad = t, k
    return en, ad, sif


def sans(kr, pnl, tur):
    """Ayni aramayi KARISTIRILMIS P&L uzerinde tekrarlar."""
    v = list(pnl)
    eniyiler, sifirlar = [], []
    for _ in range(tur):
        random.shuffle(v)
        e, _a, s = degerlendir(kr, v)
        eniyiler.append(e)
        sifirlar.append(s)
    return eniyiler, sifirlar


def rapor_kume(baslik, poz, dereceler=(1, 2, 3)):
    n = len(poz)
    pnl = [p["pnl"] for p in poz]
    ks = kosul.kosullar(poz)
    mask = [[1 if f(x) else 0 for x in poz] for _, f in ks]
    print("\n" + "=" * 92)
    print("%s   N=%d   toplam %+.2f   kosul %d" % (baslik, n, sum(pnl), len(ks)))
    print("=" * 92)
    for d in dereceler:
        t0 = time.time()
        kr = kurallar(ks, mask, n, d)
        if not kr:
            print("\n--- %d'li kural: MIN_N=%d altinda hepsi elendi" % (d, MIN_N))
            continue
        en, ad, sif = degerlendir(kr, pnl)
        tur = KARIS_2 if d < 3 else KARIS_3
        se, ss = sans(kr, pnl, tur)
        ustte = sum(1 for x in se if x >= en)
        print("\n--- %d'li kural  (MIN_N>=%d gecen: %d · uretim %.1f sn)"
              % (d, MIN_N, len(kr), time.time() - t0))
        print("  GERCEK en iyi : %+9.2f   ->  %s" % (en, ad[:78]))
        print("  SAHTE en iyi  : ortalama %+9.2f · medyan %+9.2f · en yuksek %+9.2f  (%d karistirma)"
              % (stx.mean(se), stx.median(se), max(se), tur))
        print("  gercek >= sahte olma sayisi: %d/%d   ->  p = %.3f"
              % (ustte, tur, ustte / tur))
        print("  HUKUM: %s" % ("SANSTAN AYIRT EDILEMIYOR" if ustte / tur >= 0.05
                               else "sanstan farkli (p<0.05)"))
        print("  'zarar etmeyen' (toplam>=0) kural sayisi -> gercek %d · sahtede ortalama %.0f"
              % (sif, stx.mean(ss)))
        # en iyi 5
        srt = sorted(kr, key=lambda z: -sum(pnl[j] for j in z[1]))[:5]
        print("  en iyi 5:")
        for k, idx in srt:
            v = [pnl[j] for j in idx]
            print("     %+9.2f  N=%3d  medyan %+7.2f  kazanan %%%2.0f   %s"
                  % (sum(v), len(v), stx.median(v),
                     100 * sum(1 for x in v if x > 0) / len(v), k[:64]))
    return ks, mask


def holdout(poz):
    """Kural sicrama ONCESI aranir, SONRASI'nda sinanir."""
    o = [p for p in poz if p["donem"] == "oncesi"]
    s = [p for p in poz if p["donem"] == "sonrasi"]
    if len(o) < 20 or len(s) < 5:
        print("\nHOLDOUT: donem N yetersiz (%d / %d)" % (len(o), len(s)))
        return
    ks = kosul.kosullar(o)
    mo = [[1 if f(x) else 0 for x in o] for _, f in ks]
    po = [p["pnl"] for p in o]
    ps = [p["pnl"] for p in s]
    print("\n" + "=" * 92)
    print("GERCEK HOLDOUT — kural %d islemde ARANIR, %d islemde SINANIR" % (len(o), len(s)))
    print("=" * 92)
    print("UYARI (pesinen yazildi): test kumesi N=%d. Bu sayi neredeyse hicbir seyi"
          " dogrulayamaz." % len(s))
    for d in (1, 2):
        kr = kurallar(ks, mo, len(o), d)
        if not kr:
            continue
        srt = sorted(kr, key=lambda z: -sum(po[j] for j in z[1]))[:5]
        print("\n--- %d'li  (egitimde en iyi 5, sonra TESTTE ne yaptigi)" % d)
        for k, idx in srt:
            egit = sum(po[j] for j in idx)
            # ayni kurali test kumesinde uygula
            fn = [f for ad, f in ks if ad in k.split(" & ")]
            tidx = [i for i, p in enumerate(s) if all(g(p) for g in fn)]
            tt = sum(ps[i] for i in tidx)
            tum = sum(ps)
            print("     egitim %+9.2f (N=%3d)  ->  TEST %+9.2f (N=%2d)   [test tumu %+9.2f]  %s"
                  % (egit, len(idx), tt, len(tidx), tum, k[:52]))


if __name__ == "__main__":
    taban = sys.argv[1] if len(sys.argv) > 1 else "muhasebe_11agu"
    poz = ortak.poz_yukle(taban)
    print("TABAN: %s" % taban)
    sh = [p for p in poz if p["yon"] == "SHORT"]
    lo = [p for p in poz if p["yon"] == "LONG"]
    rapor_kume("SHORT — TUM DONEM", sh)
    rapor_kume("SHORT — sicrama ONCESI", [p for p in sh if p["donem"] == "oncesi"])
    holdout(sh)
    print("\n" + "=" * 92)
    print("LONG - N=%d  [!] KOMBINASYON ARAMASI BU N'DE ANLAMLI SONUC VEREMEZ." % len(lo))
    print("Yine de ayni yontemle kosturuluyor — amac kural bulmak DEGIL,")
    print("aramanin bu N'de ne kadar kolay yanilttigini GOSTERMEK.")
    print("=" * 92)
    rapor_kume("LONG — TUM DONEM", lo, dereceler=(1, 2))
    print("\nbot dosyalarina yazim: YOK")
