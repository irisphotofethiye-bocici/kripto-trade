#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LIKIDASYON DENGESIZLIGI — LONG GIRISLERINDE

ON_KAYIT_likidasyon.md · commit 5cee2d9 — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

🔴 BIRINCIL metrik HAM getiri · chg24 MUMDAN · Spearman YOK · Apify YOK.
🔴 BELIRLEYICI SINAMA L4: katmanli etki ham etkinin >= %50'si olmali.
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

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURA))
VERI = os.path.join(BURA, "veri")
sys.path.insert(0, KOK)
sp = il.spec_from_file_location(
    "ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)
import olcucu  # noqa: E402

DILIM = 5
T_ESIK = 2.5              # IKI YONLU hipotezin bedeli (on-kayit bolum 4)
PENCERE_SA = 24
UFUK = 24
KORUMA = 0.50             # L4: katmanli etki ham etkinin >= %50'si
random.seed(20260907)


def liq_yukle():
    d = {}
    for fn in os.listdir(VERI):
        if not fn.endswith(".json"):
            continue
        try:
            h = json.load(open(os.path.join(VERI, fn)))
        except Exception:
            continue
        d[fn[:-5]] = sorted(((int(x["t"]), float(x.get("l") or 0), float(x.get("s") or 0))
                             for x in h), key=lambda z: z[0])
    return d


def pencere(seri, t_ms):
    """[t-24s, t) araligindaki long/short likidasyon toplami."""
    t = t_ms // 1000
    bas = t - PENCERE_SA * 3600
    lo = hi = 0.0
    n = 0
    for ts, l, s in seri:
        if ts >= t:
            break
        if ts >= bas:
            lo += l
            hi += s
            n += 1
    return lo, hi, n


def veri(mum, liq):
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
        if s not in liq:
            yok["liq verisi yok"] += 1
            continue
        t = ar.ts_ms(r["ts"])
        if s in son and (t - son[s]) < ar.COOLDOWN * 3_600_000:
            continue
        d, ix = mum[s]
        i0 = ix.get(t)
        if i0 is None or i0 < max(ar.YAPI_BAR, 25):
            continue
        lo, hi, nsaat = pencere(liq[s], t)
        if nsaat < 12:
            yok["liq penceresi eksik (<12 saat)"] += 1
            continue
        top = lo + hi
        if top <= 0:
            yok["pencerede likidasyon YOK"] += 1
            continue
        deng = (hi - lo) / top
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
        j = i0 + UFUK
        if j >= len(d):
            continue
        ham = (d[j]["c"] / p - 1) * 100.0
        c24 = d[i0 - 24]["c"]
        if not c24:
            continue
        chg24 = (p / c24 - 1) * 100.0
        sim = ar.simule(d, ix, t, p, stop, p * 1.10)
        if sim is None:
            continue
        son[s] = t
        R, hit = sim
        out.append({"gun": r["ts"][:10], "sym": s, "deng": deng, "top": top,
                    "ham": ham, "R": R, "hit": hit, "chg24": chg24,
                    "atr_pct": atr / p * 100.0, "stop_pct": sf})
    return out, yok


def dilimle(rows, alan, k=DILIM):
    v = sorted(rows, key=lambda x: x[alan])
    n = len(v)
    return [v[i * n // k:(i + 1) * n // k] for i in range(k)]


def gun_fark_t(rows, alan, ae, ue, metrik):
    g = collections.defaultdict(lambda: ([], []))
    for x in rows:
        if x[alan] <= ae:
            g[x["gun"]][0].append(x[metrik])
        elif x[alan] >= ue:
            g[x["gun"]][1].append(x[metrik])
    f = [stx.mean(a) - stx.mean(b) for a, b in g.values()
         if len(a) >= 2 and len(b) >= 2]
    if len(f) < 3:
        return 0.0, 0.0, len(f)
    m = stx.mean(f)
    se = stx.stdev(f) / math.sqrt(len(f))
    return m, ((m / se) if se > 0 else 0.0), len(f)


def kars(rows, alan, metrik="ham"):
    p = dilimle(rows, alan)
    alt, ust = p[0], p[-1]
    if len(alt) < 10 or len(ust) < 10:
        return None
    ae, ue = alt[-1][alan], ust[0][alan]
    ra = [x[metrik] for x in alt]
    ru = [x[metrik] for x in ust]
    fark = stx.mean(ra) - stx.mean(ru)
    _, t, ng = gun_fark_t(rows, alan, ae, ue, metrik)
    mde = 2.8 * math.sqrt(stx.variance(ra) / len(ra) + stx.variance(ru) / len(ru))
    return fark, t, mde, ng, stx.mean(ra), stx.mean(ru), len(ra), len(ru)


def katmanli(rows, alan, metrik="ham"):
    """chg24 katmanlari ICINDE ayni karsilastirma; katman farklarinin ortalamasi."""
    farklar, agirlik = [], []
    for kat in dilimle(rows, "chg24"):
        if len(kat) < 40:
            continue
        k = kars(kat, alan, metrik)
        if k is None:
            continue
        farklar.append(k[0])
        agirlik.append(len(kat))
    if not farklar:
        return None, 0
    top = sum(agirlik)
    return sum(f * w for f, w in zip(farklar, agirlik)) / top, len(farklar)


def main():
    print("=" * 106)
    print("LIKIDASYON DENGESIZLIGI — ON_KAYIT_likidasyon.md (5cee2d9)")
    print("dengesizlik = (short_liq - long_liq)/(short_liq + long_liq), giristen onceki 24s")
    print("🔴 birincil metrik HAM +24s getiri · chg24 MUMDAN · Apify YOK")
    print("=" * 106)
    liq = liq_yukle()
    print("likidasyon dosyasi: %d sembol" % len(liq))
    rows, yok = veri(ar.mumlar(), liq)
    for k, v in yok.most_common():
        print("   elenen: %-34s %d" % (k, v))
    gunler = sorted(set(x["gun"] for x in rows))
    ks = gunler[int(len(gunler) * ar.KESIF_PAY)]
    kesif = [x for x in rows if x["gun"] < ks]
    hold = [x for x in rows if x["gun"] >= ks]
    print("N=%d · gun=%d · KESIF %d · HOLDOUT %d" % (len(rows), len(gunler),
                                                     len(kesif), len(hold)))
    if len(rows) < 800:
        print("⚠️ N < 800 -> ON-KAYIT bolum 5: GUC YETERSIZ diye yazilacak")
    print()

    print("### 1) DILIM TABLOSU — dengesizlik (ek rapor)")
    for ad, p in (("KESIF", kesif), ("HOLDOUT", hold)):
        print("   --- %s (N=%d) ---" % (ad, len(p)))
        print("   %-16s %6s %9s %11s %10s %9s %9s %9s"
              % ("dengesizlik", "N", "ort deng", "HAM +24s", "ort R", "isabet%",
                 "ATR%", "stop%"))
        for q in dilimle(p, "deng"):
            if len(q) < 10:
                continue
            print("   %-16s %6d %+9.3f %+10.3f%% %+10.4f %8.1f%% %8.2f%% %8.2f%%"
                  % ("%+.2f..%+.2f" % (q[0]["deng"], q[-1]["deng"]), len(q),
                     stx.mean([x["deng"] for x in q]), stx.mean([x["ham"] for x in q]),
                     stx.mean([x["R"] for x in q]),
                     100.0 * sum(x["hit"] for x in q) / len(q),
                     stx.mean([x["atr_pct"] for x in q]),
                     stx.mean([x["stop_pct"] for x in q])))
        print()

    print("### 2) 🔴 BIRINCIL — en dusuk vs en yuksek dengesizlik dilimi (HAM)")
    kh = kars(hold, "deng")
    kk = kars(kesif, "deng")
    if kh is None or kk is None:
        print("   dilim doldurulamadi -> DURDU")
        return
    fh, th, mdeh, ngh, ah, uh, nah, nuh = kh
    fk = kk[0]
    print("   HOLDOUT  dusuk %+.4f%% (N=%d) · yuksek %+.4f%% (N=%d)" % (ah, nah, uh, nuh))
    print("            fark %+.4f%% · gun-kumeli t %+.2f (%d gun) · MDE %.4f"
          % (fh, th, ngh, mdeh))
    print("   KESIF    fark %+.4f%% (t %+.2f)" % (fk, kk[1]))
    print()

    print("### 3) 🔴 BELIRLEYICI — KARISTIRICI KONTROLU (L4)")
    kat_h, nkat = katmanli(hold, "deng")
    print("   HAM      holdout fark %+.4f%%" % fh)
    if kat_h is None:
        print("   KATMANLI hesaplanamadi (katman N yetersiz)")
        L4 = False
    else:
        oran = (kat_h / fh) if fh else 0.0
        print("   KATMANLI holdout fark %+.4f%%  (chg24'un %d katmani icinde)" % (kat_h, nkat))
        print("   koruma orani %.0f%%  (esik %%%.0f)" % (oran * 100, KORUMA * 100))
        L4 = (oran >= KORUMA)
        print("   -> %s" % ("KORUDU" if L4 else "🔴 KAYBETTI: FIYATIN KILIGI"))
    print()

    print("### 4) NEGATIF KONTROL (L5) — dengesizlik gun ici permute, AYNI HAT")
    for lst in (kesif, hold):
        g = collections.defaultdict(list)
        for i, x in enumerate(lst):
            g[x["gun"]].append(i)
        for _, idx in g.items():
            v = [lst[i]["deng"] for i in idx]
            random.shuffle(v)
            for i, val in zip(idx, v):
                lst[i]["sahte"] = val
    ks_ = kars(hold, "sahte")
    if ks_:
        print("   SAHTE holdout fark %+.4f%% · t %+.2f · MDE %.4f" % (ks_[0], ks_[1], ks_[2]))
        neg_bozuk = abs(ks_[1]) >= T_ESIK
    else:
        neg_bozuk = False
    print("   -> %s" % ("🔴 SAHTE DE ETKI URETTI" if neg_bozuk else "temiz"))
    print()

    print("### 5) EK — BUYUKLUK (emir defteri dersi tekrarlaniyor mu)")
    kb = kars(hold, "top")
    if kb:
        print("   toplam likidasyon USD: holdout fark %+.4f%% · t %+.2f · MDE %.4f"
              % (kb[0], kb[1], kb[2]))
        print("   (defter_usdt_20 BUYUKLUK olcup TAM SIFIR tasimisti)")
    print()

    print("### 6) EK — dengesizlik ile chg24 AYNI SEY MI (Spearman YOK)")
    dd = dilimle(hold, "deng")
    dc = dilimle(hold, "chg24")
    alt = len(set(id(x) for x in dd[0]) & set(id(x) for x in dc[0])) / max(1, len(dd[0]))
    ust = len(set(id(x) for x in dd[-1]) & set(id(x) for x in dc[-1])) / max(1, len(dd[-1]))
    print("   en dusuk dilim cakismasi %%%.1f · en yuksek %%%.1f  (rastgele %%20)"
          % (alt * 100, ust * 100))
    print()

    L = {
        "L1 kesif+holdout ayni isaret": (fk > 0) == (fh > 0),
        "L2 holdout |t| >= 2,5": abs(th) >= T_ESIK,
        "L3 |fark| > MDE": abs(fh) > mdeh,
        "L4 katmanli >= ham'in %50'si": L4,
        "L5 negatif kontrol temiz": not neg_bozuk,
    }
    print("=" * 106)
    print("HUKUM — ON_KAYIT bolum 8")
    print("=" * 106)
    for k, v in L.items():
        print("   %-34s %s" % (k, "GECTI" if v else "DUSTU"))
    print()
    if all(L.values()):
        print("   🔑 YON VAR — likidasyon dengesizligi fiyattan AYRI bilgi tasiyor.")
        print("   🔴 Kod OTOMATIK degismez (on-kayit bolum 11).")
    elif L["L1 kesif+holdout ayni isaret"] and L["L2 holdout |t| >= 2,5"] \
            and L["L3 |fark| > MDE"] and not L4:
        print("   🔴 FIYATIN KILIGI — etki var ama chg24 sabitlenince kayboluyor.")
    elif not L["L1 kesif+holdout ayni isaret"]:
        print("   YON YOK — isaret yarilar arasinda dondu.")
    else:
        print("   GOREMIYORUZ — isaret var, esik asilmadi.")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK · Apify cagrisi: YOK")


if __name__ == "__main__":
    main()
