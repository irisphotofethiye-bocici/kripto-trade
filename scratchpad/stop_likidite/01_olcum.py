#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STOP LIKIDITE KUMESI ICINDEYSE DAHA COK YENIR MI?

ON_KAYIT_stop_likidite.md · commit 224162f — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

🔴 BIRINCIL metrik STOP OLMA ORANI · karsilastirma ATR KATMANLARI ICINDE.
🔴 Apify/ucretli cagri YOK — harita diskteki mumdan kurulur.
SALT-OKUNUR. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, sys, math, random, collections, statistics as stx
import importlib.util as il

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)
sp = il.spec_from_file_location(
    "ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)
import olcucu  # noqa: E402

# py-liquidation-map ile AYNI katsayilar (ARANMADI, repodan alindi)
ALICI = [0.99, 0.98, 0.96, 0.90]
SATICI = [1.01, 1.02, 1.04, 1.10]
KOVA_PCT = 0.25          # kova genisligi, giris fiyatinin yuzdesi
PENCERE = 24             # harita kac saatlik mumdan kurulacak
DILIM = 5
T_ESIK = 2.0
KORUMA = 0.50            # S5
random.seed(20260907)


def hacimli_mumlar():
    """HACIM tasiyan mum kaynagi — harita SADECE bunlardan kurulur.

    🔴 Boru hattinin kendi kaynagi (fund_ls/klines) yalniz c,h,l,t tasiyor;
    hacim/tbv YOK. Giris ve stop mantigi ORADA kaliyor (kardes olcumlerle
    populasyon eslessin diye); harita icin AYRI kaynak yukleniyor:
      klines_1h_uzun 2025-09-17..2026-08-25  +  taze_1h 2026-08-20..2026-09-05
    """
    out = {}
    for d in ("klines_1h_uzun", "taze_1h"):
        yol = os.path.join(KOK, "scratchpad", d)
        if not os.path.isdir(yol):
            continue
        for f in os.listdir(yol):
            if not f.endswith(".json"):
                continue
            try:
                b = json.load(open(os.path.join(yol, f), encoding="utf-8"))
            except Exception:
                continue
            sym = f[:-5]
            h = out.setdefault(sym, {})
            for x in b:
                h.setdefault(int(x["t"]), x)      # BIRLESTIR, ezme
    return dict((k, sorted(v.values(), key=lambda z: z["t"])) for k, v in out.items())


def pencere_al(seri, t_ms, n):
    """t_ms'den ONCEKI n saatlik mum (kapanmis)."""
    i = 0
    for j, x in enumerate(seri):
        if x["t"] >= t_ms:
            i = j
            break
    else:
        i = len(seri)
    return seri[max(0, i - n):i]


def harita_kur(bars, ref):
    """Saatlik mumlardan liqmap. -> {kova_ortasi: agirlik}"""
    kv = collections.defaultdict(float)
    adim = ref * KOVA_PCT / 100.0
    if adim <= 0:
        return kv
    for b in bars:
        p = (b["h"] + b["l"] + b["c"]) / 3.0
        v = b.get("v") or 0.0
        tbv = b.get("tbv") or 0.0
        alis = tbv * p                      # alici agresor, kote cinsinden
        satis = max(v - tbv, 0.0) * p       # satici agresor
        if alis > 0:
            for k in ALICI:
                kv[round(p * k / adim) * adim] += alis
        if satis > 0:
            for k in SATICI:
                kv[round(p * k / adim) * adim] += satis
    return kv


def yogunluk_p(kv, seviye, ref):
    """Seviyenin dustugu kovanin yogunlugu, TUM kovalara gore yuzdelik [0,1]."""
    if not kv:
        return None
    adim = ref * KOVA_PCT / 100.0
    anahtar = round(seviye / adim) * adim
    deger = kv.get(anahtar, 0.0)
    hepsi = sorted(kv.values())
    n = len(hepsi)
    # kacinin ALTINDA -> yuzdelik
    alt = sum(1 for x in hepsi if x < deger)
    esit = sum(1 for x in hepsi if x == deger)
    return (alt + esit / 2.0) / n


def veri(mum, hac):
    out, son = [], {}
    yok = collections.Counter()
    for line in io.open(os.path.join(KOK, "radar_archive.jsonl"),
                        encoding="utf-8", errors="ignore"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        s, p = r.get("sym"), r.get("price")
        if not s or not p or s not in mum or (r.get("score") or 0) < ar.SKOR_MIN:
            continue
        t = ar.ts_ms(r["ts"])
        if s in son and (t - son[s]) < ar.COOLDOWN * 3_600_000:
            continue
        d, ix = mum[s]
        i0 = ix.get(t)
        if i0 is None or i0 < max(ar.YAPI_BAR, PENCERE + 1):
            continue
        bars = d[i0 - ar.YAPI_BAR:i0]
        stop = ar.stop_hesapla(bars, p)
        if stop is None:
            continue
        sf = (p - stop) / p * 100.0
        if sf < ar.ASGARI_STOP:
            continue
        atr = olcucu.atr(bars, period=14)
        if atr <= 0:
            continue
        hs = hac.get(s)
        if not hs:
            yok["hacimli mum YOK (sembol)"] += 1
            continue
        pen = pencere_al(hs, t, PENCERE)
        if len(pen) < PENCERE or not any((b.get("tbv") or 0) > 0 for b in pen):
            yok["hacim penceresi eksik"] += 1
            continue
        kv = harita_kur(pen, p)
        sp_ = yogunluk_p(kv, stop, p)
        if sp_ is None:
            yok["harita bos"] += 1
            continue
        # sonuc
        hedef = p * 1.10
        sonuc = None
        for j in range(i0 + 1, min(i0 + 1 + ar.ZAMAN_STOP, len(d))):
            b = d[j]
            if b["l"] <= stop:
                sonuc = "STOP"
                break
            if b["h"] >= hedef:
                sonuc = "HEDEF"
                break
        if sonuc is None:
            sonuc = "ZAMAN"
        j24 = i0 + 24
        if j24 >= len(d):
            continue
        ham = (d[j24]["c"] / p - 1) * 100.0
        son[s] = t
        yukari = sum(v for k, v in kv.items() if k > p)
        asagi = sum(v for k, v in kv.items() if k < p)
        out.append({"gun": r["ts"][:10], "sym": s, "stop_p": sp_,
                    "stop_atr": (p - stop) / atr, "stop_pct": sf,
                    "atr_pct": atr / p * 100.0, "ham": ham,
                    "sonuc": sonuc, "stop_oldu": 1 if sonuc == "STOP" else 0,
                    "hedef_oldu": 1 if sonuc == "HEDEF" else 0,
                    "denge": (yukari - asagi) / (yukari + asagi) if (yukari + asagi) else 0.0})
    return out, yok


def dilimle(rows, alan, k=DILIM):
    v = sorted(rows, key=lambda x: x[alan])
    n = len(v)
    return [v[i * n // k:(i + 1) * n // k] for i in range(k)]


def gun_t(rows, alan, ae, ue, metrik):
    g = collections.defaultdict(lambda: ([], []))
    for x in rows:
        if x[alan] >= ue:
            g[x["gun"]][0].append(x[metrik])     # KUME ICI
        elif x[alan] <= ae:
            g[x["gun"]][1].append(x[metrik])     # BOS BOLGE
    f = [stx.mean(a) - stx.mean(b) for a, b in g.values()
         if len(a) >= 2 and len(b) >= 2]
    if len(f) < 3:
        return 0.0, 0.0, len(f)
    m = stx.mean(f)
    se = stx.stdev(f) / math.sqrt(len(f))
    return m, ((m / se) if se > 0 else 0.0), len(f)


def kars(rows, metrik="stop_oldu"):
    """kume ici - bos bolge. -> (fark, t, mde, ngun, ki, bo, nk, nb)"""
    p = dilimle(rows, "stop_p")
    bos, kume = p[0], p[-1]
    if len(bos) < 10 or len(kume) < 10:
        return None
    ae, ue = bos[-1]["stop_p"], kume[0]["stop_p"]
    rk = [x[metrik] for x in kume]
    rb = [x[metrik] for x in bos]
    fark = stx.mean(rk) - stx.mean(rb)
    _, t, ng = gun_t(rows, "stop_p", ae, ue, metrik)
    mde = 2.8 * math.sqrt(stx.variance(rk) / len(rk) + stx.variance(rb) / len(rb))
    return fark, t, mde, ng, stx.mean(rk), stx.mean(rb), len(rk), len(rb)


def katmanli(rows, metrik="stop_oldu"):
    """ATR katmanlari ICINDE ayni karsilastirma; agirlikli ortalama."""
    f, w = [], []
    for kat in dilimle(rows, "stop_atr"):
        if len(kat) < 40:
            continue
        k = kars(kat, metrik)
        if k is None:
            continue
        f.append(k[0])
        w.append(len(kat))
    if not f:
        return None, 0
    return sum(a * b for a, b in zip(f, w)) / sum(w), len(f)


def main():
    print("=" * 106)
    print("STOP LIKIDITE KUMESI ICINDE MI — ON_KAYIT_stop_likidite.md (224162f)")
    print("harita: klines_1h_uzun (hacim + tbv) · Apify YOK · birincil metrik STOP OLMA")
    print("=" * 106)
    hac = hacimli_mumlar()
    print("hacimli mum kaynagi: %d sembol (klines_1h_uzun + taze_1h)" % len(hac))
    rows, yok = veri(ar.mumlar(), hac)
    for k, v in yok.most_common():
        print("   elenen: %-26s %d" % (k, v))
    gunler = sorted(set(x["gun"] for x in rows))
    if len(gunler) < 6:
        print("🔴 gun sayisi %d -> olculemez, DURDU" % len(gunler))
        return
    ks = gunler[int(len(gunler) * ar.KESIF_PAY)]
    kesif = [x for x in rows if x["gun"] < ks]
    hold = [x for x in rows if x["gun"] >= ks]
    print("N=%d · gun=%d · KESIF %d · HOLDOUT %d\n" % (len(rows), len(gunler),
                                                       len(kesif), len(hold)))

    print("### 1) DILIM TABLOSU (ek rapor)")
    for ad, p in (("KESIF", kesif), ("HOLDOUT", hold)):
        print("   --- %s (N=%d) ---" % (ad, len(p)))
        print("   %-14s %6s %9s %9s %9s %11s %9s %9s"
              % ("stop_p", "N", "STOP%", "HEDEF%", "ham+24s", "stop ATR", "stop%", "ATR%"))
        for q in dilimle(p, "stop_p"):
            if len(q) < 10:
                continue
            print("   %-14s %6d %8.1f%% %8.1f%% %+8.3f%% %10.2f %8.2f%% %8.2f%%"
                  % ("%.2f-%.2f" % (q[0]["stop_p"], q[-1]["stop_p"]), len(q),
                     100.0 * sum(x["stop_oldu"] for x in q) / len(q),
                     100.0 * sum(x["hedef_oldu"] for x in q) / len(q),
                     stx.mean([x["ham"] for x in q]),
                     stx.mean([x["stop_atr"] for x in q]),
                     stx.mean([x["stop_pct"] for x in q]),
                     stx.mean([x["atr_pct"] for x in q])))
        print()

    kh = kars(hold)
    kk = kars(kesif)
    if kh is None or kk is None:
        print("dilim doldurulamadi -> DURDU")
        return
    fh, th, mdeh, ngh, ki, bo, nk, nb = kh
    print("### 2) 🔴 BIRINCIL — HAM (katmansiz), stop olma orani")
    print("   HOLDOUT  kume ici %.1f%% (N=%d) · bos bolge %.1f%% (N=%d)"
          % (ki * 100, nk, bo * 100, nb))
    print("            fark %+.4f (%.1f puan) · gun-t %+.2f (%d gun) · MDE %.4f"
          % (fh, fh * 100, th, ngh, mdeh))
    print("   KESIF    fark %+.4f (t %+.2f)" % (kk[0], kk[1]))
    print()

    print("### 3) 🔴 BELIRLEYICI — ATR KATMANLARI ICINDE (S5)")
    kat_h, nkat = katmanli(hold)
    if kat_h is None:
        print("   katman N yetersiz -> S5 DUSTU")
        S5 = False
        kat_h = 0.0
    else:
        oran = (kat_h / fh) if fh else 0.0
        print("   HAM      %+.4f" % fh)
        print("   KATMANLI %+.4f  (stop_atr'nin %d katmani icinde)" % (kat_h, nkat))
        print("   koruma orani %.0f%% (esik %%%.0f)" % (oran * 100, KORUMA * 100))
        S5 = (oran >= KORUMA)
        print("   -> %s" % ("KORUDU" if S5 else "🔴 KAYBETTI: STOP MESAFESININ KILIGI"))
    print()

    print("### 4) IKINCIL — ham +24s getiri (ayni bolme)")
    kg = kars(hold, "ham")
    if kg:
        print("   kume ici %+.3f%% · bos bolge %+.3f%% · fark %+.4f%% · t %+.2f"
              % (kg[4], kg[5], kg[0], kg[1]))
    print()

    print("### 5) NEGATIF KONTROL (S6) — stop_p gun ici permute")
    for lst in (kesif, hold):
        g = collections.defaultdict(list)
        for i, x in enumerate(lst):
            g[x["gun"]].append(i)
        for _, idx in g.items():
            v = [lst[i]["stop_p"] for i in idx]
            random.shuffle(v)
            for i, val in zip(idx, v):
                lst[i]["gercek_p"] = lst[i]["stop_p"]
                lst[i]["stop_p"] = val
    ks_ = kars(hold)
    neg = bool(ks_ and ks_[0] > 0 and ks_[1] >= T_ESIK)
    if ks_:
        print("   SAHTE fark %+.4f · t %+.2f -> %s"
              % (ks_[0], ks_[1], "🔴 SAHTE DE ETKI URETTI" if neg else "temiz"))
    for lst in (kesif, hold):
        for x in lst:
            x["stop_p"] = x.pop("gercek_p", x["stop_p"])
    print()

    print("### 6) EK — stop_p ile stop_pct AYNI SEY MI (Spearman YOK)")
    dp = dilimle(hold, "stop_p")
    ds = dilimle(hold, "stop_pct")
    a = len(set(id(x) for x in dp[0]) & set(id(x) for x in ds[0])) / max(1, len(dp[0]))
    b = len(set(id(x) for x in dp[-1]) & set(id(x) for x in ds[-1])) / max(1, len(dp[-1]))
    print("   alt dilim cakismasi %%%.1f · ust %%%.1f  (rastgele %%20)" % (a * 100, b * 100))
    print()

    S = {
        "S1 katmanli fark > 0": kat_h > 0,
        "S2 gun-kumeli t >= 2,0": th >= T_ESIK,
        "S3 |fark| > MDE": abs(fh) > mdeh,
        "S4 kesif+holdout ayni isaret": (kk[0] > 0) == (fh > 0),
        "S5 katmanli >= hamin %50si": S5,
        "S6 negatif kontrol temiz": not neg,
    }
    print("=" * 106)
    print("HUKUM — ON_KAYIT bolum 7")
    print("=" * 106)
    for k, v in S.items():
        print("   %-34s %s" % (k, "GECTI" if v else "DUSTU"))
    print()
    if all(S.values()):
        print("   🔑 YON VAR — kumedeki stop daha cok yeniyor.")
        print("   🔴 GIRIS KAPISI DEGIL, STOP YERLESTIRME kurali. Kod OTOMATIK degismez.")
    elif S["S2 gun-kumeli t >= 2,0"] and S["S3 |fark| > MDE"] and not S5:
        print("   🔴 STOP MESAFESININ KILIGI — etki var, ATR sabitlenince kayboluyor.")
    elif not (S["S1 katmanli fark > 0"] and S["S4 kesif+holdout ayni isaret"]):
        print("   YON YOK.")
    else:
        print("   GOREMIYORUZ — isaret var, esik asilmadi.")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK · ucretli cagri: YOK")


if __name__ == "__main__":
    main()
