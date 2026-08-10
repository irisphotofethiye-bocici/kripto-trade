#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""YÜKSELENLERİN ORTAK ÖRÜNTÜSÜ (2026-08-10)

SORU (kullanici): "bizden BAGIMSIZ — bu coinler ortak olarak hangi sinyalleri verdi?
Ayni rejim, yukselmis; yukseldigi andaki TUM coinlerin arasindaki oruntuyu bul."

PARAMETRELER (kullanici secti):
  yukselis  : 24 saatte +%10 (ilk kez esigi astigi bar)
  an        : tetik barinin KENDISI
  evren     : TUM 570 USDT perp · yalniz fiyat/hacim (funding/OI yok)
  rejim     : 46 gunun tamami AYI/NOTR — tek rejim, ayrica ayrilmiyor

YONTEM:
  1. Her sembolde 24h getirinin ilk kez +%10'u astigi barlar bulunur (72 bar dedup).
  2. O barda, RADAR'IN SKORUNDAN BAGIMSIZ, ham OHLCV'den 24 olcu hesaplanir.
  3. KONTROL: her yukselis olayi icin AYNI sembolden, ayni donemde RASTGELE bir bar
     (eslesmis kontrol; sembol ve donem etkisini sabitler). Tohum sabit.
  4. Her olcu icin: yukselenlerin medyani vs kontrolun medyani + AYRIM GUCU
     (yukselenlerin kacta kaci kontrolun ust/alt ceyreginin disinda).
  5. En ayirici olculerin ES ZAMANLI olusma orani ("ortak olarak hangi sinyaller").

DURUSTLUK: bu bir KESIF taramasidir, kural uretmez. Bulunan her sey once zaman
ikiye bolunerek dogrulanir; ayakta kalmayan TARAMA ARTIGIDIR ve oyle raporlanir.
"""
import json, os, math, random, statistics as st, collections, datetime

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h")
TETIK, DEDUP = 10.0, 72
random.seed(11)


def ma(v, i, n):
    return st.mean(v[i - n + 1:i + 1]) if i >= n - 1 else None


def atr(b, i, n=14):
    if i < n:
        return None
    tr = []
    for j in range(i - n + 1, i + 1):
        p = b[j - 1]["c"]
        tr.append(max(b[j]["h"] - b[j]["l"], abs(b[j]["h"] - p), abs(p - b[j]["l"])))
    return st.mean(tr)


def olcu(b, i):
    """Bar i'deki durum — 24 olcu, hepsi ham OHLCV'den. Radar/skor KULLANILMAZ."""
    if i < 200 or i >= len(b):
        return None
    c = [x["c"] for x in b]
    px = b[i]["c"]
    a = atr(b, i)
    a24 = atr(b, i - 24)
    if not a or a <= 0 or not px:
        return None
    qv = [x.get("qv", 0.0) for x in b]
    tbv = [x.get("tbv", 0.0) for x in b]
    son24 = qv[i - 23:i + 1]
    onceki24 = qv[i - 47:i - 23]
    med7g = st.median(qv[max(0, i - 167):i + 1]) or 1e-9
    hi20 = max(x["h"] for x in b[i - 19:i + 1]); lo20 = min(x["l"] for x in b[i - 19:i + 1])
    hi168 = max(x["h"] for x in b[i - 167:i + 1]); lo168 = min(x["l"] for x in b[i - 167:i + 1])
    hi720 = max(x["h"] for x in b[max(0, i - 719):i + 1])
    m50, m200 = ma(c, i, 50), ma(c, i, 200)
    bar = b[i]
    govde = abs(bar["c"] - bar["o"])
    aralik = bar["h"] - bar["l"]
    yesil = 0
    for j in range(i, max(0, i - 12), -1):
        if b[j]["c"] > b[j]["o"]:
            yesil += 1
        else:
            break
    # taker alis orani (tbv = taker buy quote volume)
    tb24 = sum(tbv[i - 23:i + 1]); q24 = sum(son24) or 1e-9
    return {
        # --- hacim
        "hacim_kat_1h": qv[i] / (st.median(qv[i - 23:i + 1]) or 1e-9),
        "hacim_kat_24h": (sum(son24) / (sum(onceki24) or 1e-9)),
        "hacim_kat_7g": (st.median(son24) / med7g),
        "hacim_musd": st.median(son24) / 1e6,
        "islem_sayisi": st.median([x.get("n", 0) for x in b[i - 23:i + 1]]),
        "taker_alis_pay": tb24 / q24,
        # --- oynaklik
        "atr_pct": a / px * 100,
        "atr_patlama": a / (a24 or a),
        "sikisma": st.mean([max(b[j]["h"] - b[j]["l"],
                                abs(b[j]["h"] - b[j - 1]["c"]),
                                abs(b[j]["l"] - b[j - 1]["c"])) for j in range(i - 5, i + 1)]) / a,
        # --- fiyat yapisi
        "pos20": (px - lo20) / (hi20 - lo20) if hi20 > lo20 else 0.5,
        "pos168": (px - lo168) / (hi168 - lo168) if hi168 > lo168 else 0.5,
        "zirve30g_uzaklik": (px / hi720 - 1) * 100 if hi720 else 0,
        "dip7g_yukselis": (px / lo168 - 1) * 100 if lo168 else 0,
        "ma50_mesafe": (px / m50 - 1) * 100 if m50 else 0,
        "ma200_mesafe": (px / m200 - 1) * 100 if m200 else 0,
        # --- getiriler
        "chg_1h": (px / c[i - 1] - 1) * 100,
        "chg_6h": (px / c[i - 6] - 1) * 100,
        "chg_24h": (px / c[i - 24] - 1) * 100,
        "chg_72h": (px / c[i - 72] - 1) * 100,
        "chg_168h": (px / c[i - 168] - 1) * 100 if i >= 168 else 0,
        # --- mum yapisi
        "govde_orani": govde / aralik if aralik > 0 else 0,
        "ardisik_yesil": yesil,
        # --- zaman
        "utc_saat": datetime.datetime.utcfromtimestamp(b[i]["t"] / 1000).hour,
        "listelenme_bar": i,
    }


ALANLAR = ["hacim_kat_1h", "hacim_kat_24h", "hacim_kat_7g", "hacim_musd", "islem_sayisi",
           "taker_alis_pay", "atr_pct", "atr_patlama", "sikisma", "pos20", "pos168",
           "zirve30g_uzaklik", "dip7g_yukselis", "ma50_mesafe", "ma200_mesafe",
           "chg_1h", "chg_6h", "chg_24h", "chg_72h", "chg_168h",
           "govde_orani", "ardisik_yesil", "utc_saat", "listelenme_bar"]


def main():
    dosyalar = sorted(f[:-5] for f in os.listdir(CACHE) if f.endswith(".json"))
    yuk, kon = [], []
    atlanan = 0
    for sym in dosyalar:
        try:
            b = json.load(open(os.path.join(CACHE, f"{sym}.json")))
        except Exception:
            continue
        if len(b) < 300 or "qv" not in b[-1]:
            atlanan += 1
            continue
        son = -999
        tetikler = []
        for i in range(200, len(b) - 2):
            if i - son < DEDUP:
                continue
            onc = b[i - 24]["c"]
            if not onc or (b[i]["c"] / onc - 1) * 100 < TETIK:
                continue
            son = i
            tetikler.append(i)
        for i in tetikler:
            o = olcu(b, i)
            if not o:
                continue
            o["sym"], o["ts"] = sym, b[i]["t"]
            yuk.append(o)
            # eslesmis kontrol: ayni sembol, ayni donem, rastgele bar
            for _ in range(8):
                k = random.randint(200, len(b) - 3)
                if abs(k - i) < 72:
                    continue
                ok = olcu(b, k)
                if ok:
                    ok["sym"], ok["ts"] = sym, b[k]["t"]
                    kon.append(ok)
                    break
    print("=" * 106)
    print("YÜKSELENLERİN ORTAK ÖRÜNTÜSÜ — bizim göstergelerimizden BAĞIMSIZ")
    print("=" * 106)
    print(f"Tetik: 24h getiri ilk kez > %{TETIK:.0f} · an: tetik barinin kendisi · "
          f"{len(dosyalar)-atlanan} sembol (hacimsiz {atlanan} atlandi)")
    print(f"YUKSELEN olay: {len(yuk)}   ·   ESLESMIS KONTROL: {len(kon)}   ·   46 gun, tek rejim\n")

    tsl = sorted(o["ts"] for o in yuk)
    ORTA = tsl[len(tsl) // 2]

    def dilim(v, p):
        v = sorted(v)
        return v[min(len(v) - 1, int(len(v) * p))]

    print(f"{'olcu':20}{'YUKSELEN med':>14}{'KONTROL med':>13}{'oran':>8}"
          f"{'ust-ceyrek disi %':>19}{'A yari':>10}{'B yari':>10}")
    print("-" * 106)
    satirlar = []
    for al in ALANLAR:
        y = [o[al] for o in yuk if o.get(al) is not None]
        k = [o[al] for o in kon if o.get(al) is not None]
        if len(y) < 50 or len(k) < 50:
            continue
        my, mk = st.median(y), st.median(k)
        ust = dilim(k, 0.75)
        alt = dilim(k, 0.25)
        # ayrim: yukselenlerin kaci kontrolun ust ceyreginin USTUNDE (ya da alt ceyreginin ALTINDA)
        p_ust = sum(1 for x in y if x > ust) / len(y) * 100
        p_alt = sum(1 for x in y if x < alt) / len(y) * 100
        ayrim = max(p_ust, p_alt)
        yon = "yuksek" if p_ust >= p_alt else "dusuk"
        yA = [o[al] for o in yuk if o["ts"] < ORTA]
        yB = [o[al] for o in yuk if o["ts"] >= ORTA]
        pA = (sum(1 for x in yA if x > ust) / len(yA) * 100) if yon == "yuksek" else \
             (sum(1 for x in yA if x < alt) / len(yA) * 100)
        pB = (sum(1 for x in yB if x > ust) / len(yB) * 100) if yon == "yuksek" else \
             (sum(1 for x in yB if x < alt) / len(yB) * 100)
        oran = (my / mk) if mk not in (0,) else float("nan")
        satirlar.append((ayrim, al, my, mk, oran, yon, pA, pB))
    satirlar.sort(reverse=True)
    for ayrim, al, my, mk, oran, yon, pA, pB in satirlar:
        print(f"{al:20}{my:14.3f}{mk:13.3f}{oran:8.2f}"
              f"{ayrim:15.1f}% {yon:4}{pA:10.1f}{pB:10.1f}")
    print("-" * 106)
    print("  'ust-ceyrek disi %' = yukselenlerin yuzde kaci kontrolun ust (ya da alt) ceyreginin")
    print("  disinda. Rastgele olsaydi %25 cikardi. %25'ten ne kadar uzaksa o kadar ayirici.")
    print("  A/B = ayni oran, donem ikiye bolunmus (tarama artigi kontrolu).")

    json.dump({"yuk": [{k: v for k, v in o.items()} for o in yuk],
               "kon": [{k: v for k, v in o.items()} for o in kon]},
              open(os.path.join(BURA, "yukselen_olaylar.json"), "w"))
    print("\n-> scratchpad/yukselen_olaylar.json")


if __name__ == "__main__":
    main()
