# -*- coding: utf-8 -*-
"""KULLANICI ONERISI: coinleri DUSEN / STABIL / YUKSELEN diye ayir,
model bunlari birbirinden ayirabiliyor mu?
Yeni kosum YOK — 01_topla.py'nin ham ciktisi kullaniliyor.

AUC = "modelin skoru, gercekten yukselen coini gercekten dusen coinden
       daha yuksek siraliyor mu?"  %50 = hicbir ayirt etme yetenegi yok.
SALT OKUMA."""
import json, os, math, collections, statistics as sx

d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ham_sonuc.json")))

def auc(poz, neg):
    """Mann-Whitney: rastgele bir POZ, rastgele bir NEG'den yuksek skorlanma olasiligi."""
    if len(poz) < 20 or len(neg) < 20: return None, 0, 0
    hep = sorted([(s, 1) for s in poz] + [(s, 0) for s in neg])
    i, toplam = 0, 0.0
    while i < len(hep):
        j = i
        while j < len(hep) and hep[j][0] == hep[i][0]: j += 1
        ort_r = (i + j + 1) / 2.0                      # 1-tabanli ortalama rank (beraberlik)
        for k in range(i, j):
            if hep[k][1] == 1: toplam += ort_r
        i = j
    n1, n0 = len(poz), len(neg)
    return (toplam - n1*(n1+1)/2.0) / (n1*n0), n1, n0

for H in (4, 24):
    print("=" * 92)
    print("UFUK %d SAAT" % H)
    print("=" * 92)
    # modelin tahmin ettigi getiri (%) ve gerceklesen getiri (%)
    for x in d:
        x["tah"] = (x["p%d" % H] - x["son"]) / x["son"] * 100
        x["ger"] = (x["ger%d" % H] - x["son"]) / x["son"] * 100
        q = x["q%d" % H]
        x["gen"] = (q[9] - q[1]) / x["son"] * 100        # modelin ongordugu band genisligi

    ESIK = 2.0 if H == 24 else 1.0
    dusen  = [x for x in d if x["ger"] < -ESIK]
    stabil = [x for x in d if -ESIK <= x["ger"] <= ESIK]
    yuksel = [x for x in d if x["ger"] > ESIK]
    print("\nGRUPLAR (gerceklesen sonuca gore, esik +-%%%.0f):" % ESIK)
    for ad, g in (("DUSEN", dusen), ("STABIL", stabil), ("YUKSELEN", yuksel)):
        print("  %-9s N=%-5d   gercek ort %+6.2f%%   MODEL NE DEDI: %+6.3f%%   band %%%.2f"
              % (ad, len(g), sx.mean([z["ger"] for z in g]),
                 sx.mean([z["tah"] for z in g]), sx.mean([z["gen"] for z in g])))

    print("\nAYIRT ETME YETENEGI (AUC — %50 = hicbir yetenek yok):")
    a, n1, n0 = auc([x["tah"] for x in yuksel], [x["tah"] for x in dusen])
    print("  1) YUKSELEN vs DUSEN   ... skor = modelin YON tahmini")
    print("     AUC %%%.1f   (N %d vs %d)" % (100*a, n1, n0))

    hareket = dusen + yuksel
    a2, n1, n0 = auc([x["gen"] for x in hareket], [x["gen"] for x in stabil])
    print("  2) HAREKETLI vs STABIL ... skor = modelin ongordugu BAND GENISLIGI")
    print("     AUC %%%.1f   (N %d vs %d)" % (100*a2, n1, n0))

    a3, n1, n0 = auc([x["gen"] for x in yuksel], [x["gen"] for x in dusen])
    print("  3) YUKSELEN vs DUSEN   ... skor = BAND GENISLIGI (yon bilgisi tasiyor mu?)")
    print("     AUC %%%.1f   (N %d vs %d)" % (100*a3, n1, n0))

    # gun-kumeli guven araligi (1 numara icin)
    g = collections.defaultdict(lambda: ([], []))
    for x in yuksel: g[x["gun"]][0].append(x["tah"])
    for x in dusen:  g[x["gun"]][1].append(x["tah"])
    gunluk = []
    for k, (p, n) in g.items():
        v, _, _ = auc(p*3, n*3) if len(p) >= 7 and len(n) >= 7 else (None, 0, 0)
        if v is not None: gunluk.append(v)
    if len(gunluk) > 10:
        m = sx.mean(gunluk); se = sx.stdev(gunluk)/math.sqrt(len(gunluk))
        print("\n  gun-kumeli AUC (yon): %%%.1f +-%%%.1f   (gun N=%d)" % (100*m, 100*1.96*se, len(gunluk)))
    print()
