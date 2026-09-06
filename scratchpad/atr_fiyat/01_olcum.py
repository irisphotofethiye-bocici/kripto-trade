#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ATR/FIYAT — DOGRUDAN GIRIS FILTRESI OLARAK

ON_KAYIT_atr_fiyat.md · commit 8273a10 — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

🔴 SPEARMAN/KORELASYON HESAPLANMAZ (on-kayit bolum 2, ortak payda tuzagi).
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

DILIM = 5
T_ESIK = 2.0
random.seed(20260906)


def veri(mum):
    out, son = [], {}
    for l in io.open(os.path.join(KOK, "radar_archive.jsonl"),
                     encoding="utf-8", errors="ignore"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
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
        if i0 is None or i0 < ar.YAPI_BAR:
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
        sim = ar.simule(d, ix, t, p, stop, p * 1.10)
        if sim is None:
            continue
        son[s] = t
        R, hit = sim
        # net% : R x stop%  (geri cevrim)
        out.append({"gun": r["ts"][:10], "sym": s, "R": R, "hit": hit,
                    "atr_pct": atr / p * 100.0, "stop_pct": sf,
                    "net_pct": R * sf, "chg24": r.get("chg24")})
    return out


def dilimle(rows, alan):
    v = sorted(rows, key=lambda x: x[alan])
    n = len(v)
    return [v[i * n // DILIM:(i + 1) * n // DILIM] for i in range(DILIM)]


def gun_fark_t(rows, alan, alt_esik, ust_esik):
    """en dusuk dilim - en yuksek dilim, gunluk."""
    g = collections.defaultdict(lambda: ([], []))
    for x in rows:
        if x[alan] <= alt_esik:
            g[x["gun"]][0].append(x["R"])
        elif x[alan] >= ust_esik:
            g[x["gun"]][1].append(x["R"])
    f = [stx.mean(a) - stx.mean(b) for a, b in g.values()
         if len(a) >= 2 and len(b) >= 2]
    if len(f) < 3:
        return 0.0, 0.0, len(f)
    m = stx.mean(f)
    se = stx.stdev(f) / math.sqrt(len(f))
    return m, ((m / se) if se > 0 else 0.0), len(f)


def kars(rows, alan):
    """-> (fark, t, mde, ngun, alt_ort, ust_ort, n_alt, n_ust)"""
    p = dilimle(rows, alan)
    alt, ust = p[0], p[-1]
    ae, ue = alt[-1][alan], ust[0][alan]
    ra = [x["R"] for x in alt]
    ru = [x["R"] for x in ust]
    fark = stx.mean(ra) - stx.mean(ru)
    _, t, ng = gun_fark_t(rows, alan, ae, ue)
    mde = 2.8 * math.sqrt(stx.variance(ra) / len(ra) + stx.variance(ru) / len(ru))
    return fark, t, mde, ng, stx.mean(ra), stx.mean(ru), len(ra), len(ru)


def tablo(rows, alan, ad):
    print("   --- %s (N=%d) ---" % (ad, len(rows)))
    print("   %-16s %6s %9s %11s %10s %9s %12s %9s %7s"
          % ("dilim", "N", "ort ATR%", "ort R", "net%", "isabet%", "amp.basabas",
             "stop-ol%", "saat"))
    for i, p in enumerate(dilimle(rows, alan)):
        if len(p) < 10:
            continue
        R = [x["R"] for x in p]
        kaz = [v for v in R if v > 0]
        kay = [v for v in R if v <= 0]
        amp = (100.0 * (-stx.mean(kay)) / (stx.mean(kaz) - stx.mean(kay))
               if (kaz and kay) else float("nan"))
        print("   %-16s %6d %9.2f %+11.4f %+9.3f%% %8.1f%% %11.1f%% %8s %7s"
              % ("%.2f-%.2f" % (p[0][alan], p[-1][alan]), len(p),
                 stx.mean([x[alan] for x in p]), stx.mean(R),
                 stx.mean([x["net_pct"] for x in p]),
                 100.0 * sum(x["hit"] for x in p) / len(p), amp, "-", "-"))


def main():
    print("=" * 104)
    print("ATR/FIYAT — ON_KAYIT_atr_fiyat.md (8273a10)")
    print("🔴 Spearman/korelasyon HESAPLANMIYOR (ortak payda tuzagi).")
    print("=" * 104)
    rows = veri(ar.mumlar())
    gunler = sorted(set(x["gun"] for x in rows))
    ks = gunler[int(len(gunler) * ar.KESIF_PAY)]
    kesif = [x for x in rows if x["gun"] < ks]
    hold = [x for x in rows if x["gun"] >= ks]
    print("N=%d · KESIF %d · HOLDOUT %d" % (len(rows), len(kesif), len(hold)))
    print()

    # --- ATR ile stop_pct ne kadar ayni sey?
    ap = [x["atr_pct"] for x in rows]
    sp_ = [x["stop_pct"] for x in rows]
    oran = [b / a for a, b in zip(ap, sp_) if a > 0]
    print("### 0) ATR/fiyat ile stop_pct AYNI SEY MI?")
    print("   ATR%%  medyan %.2f · stop%% medyan %.2f" % (stx.median(ap), stx.median(sp_)))
    print("   stop/ATR orani: medyan %.2f · p25 %.2f · p75 %.2f"
          % (stx.median(oran), sorted(oran)[len(oran) // 4], sorted(oran)[3 * len(oran) // 4]))
    esit = 100.0 * sum(1 for o in oran if abs(o - 1.5) < 0.05) / len(oran)
    print("   stop = 1,5 x ATR olan (ATR yedegi baglamis) pay: %%%.1f" % esit)
    print()

    print("### 1) DILIM TABLOSU (ek rapor)")
    tablo(kesif, "atr_pct", "KESIF")
    print()
    tablo(hold, "atr_pct", "HOLDOUT")
    print()

    print("### 2) 🔴 BIRINCIL — en DUSUK ATR dilimi vs en YUKSEK (holdout)")
    fh, th, mdeh, ngh, ah, uh, nah, nuh = kars(hold, "atr_pct")
    fk, tk, _, _, ak, uk, _, _ = kars(kesif, "atr_pct")
    print("   HOLDOUT  dusuk %+.4f (N=%d) · yuksek %+.4f (N=%d)" % (ah, nah, uh, nuh))
    print("            fark %+.4f · gun-kumeli t %+.2f (%d gun) · MDE %.4f"
          % (fh, th, ngh, mdeh))
    print("   KESIF    dusuk %+.4f · yuksek %+.4f · fark %+.4f (t %+.2f)"
          % (ak, uk, fk, tk))
    print()

    # --- NEGATIF KONTROL: ATR gun ici permute, AYNI HAT
    for lst in (kesif, hold):
        g = collections.defaultdict(list)
        for i, x in enumerate(lst):
            g[x["gun"]].append(i)
        for gun, idx in g.items():
            v = [lst[i]["atr_pct"] for i in idx]
            random.shuffle(v)
            for i, val in zip(idx, v):
                lst[i]["sahte"] = val
    fs, ts, mdes, _, _, _, _, _ = kars(hold, "sahte")
    print("### 3) NEGATIF KONTROL — ATR gun ici permute, AYNI HAT")
    print("   SAHTE holdout fark %+.4f · t %+.2f · MDE %.4f" % (fs, ts, mdes))
    neg_bozuk = (fs > 0 and ts >= T_ESIK)
    print("   -> %s" % ("🔴 SAHTE DE ETKI URETTI, duzenek supheli" if neg_bozuk
                        else "temiz (sahte etki uretmedi)"))
    print()

    V = {
        "V1 holdout fark > 0": fh > 0,
        "V2 gun-kumeli t >= 2,0": th >= T_ESIK,
        "V3 |fark| > MDE": abs(fh) > mdeh,
        "V4 kesif+holdout ayni isaret": (fk > 0) == (fh > 0),
        "V5 negatif kontrol temiz": not neg_bozuk,
    }
    print("=" * 104)
    print("HUKUM — ON_KAYIT bolum 6")
    print("=" * 104)
    for k, val in V.items():
        print("   %-32s %s" % (k, "GECTI" if val else "DUSTU"))
    print()
    if all(V.values()):
        print("   🔑 YON VAR — sakin coin daha iyi.")
        print("   🔴 Bota KONMAZ: once portfoy simulasyonu (on-kayit bolum 10).")
        print("      ⚠️ Oynak coinleri elemek ISLEM SAYISINI AZALTIR.")
    elif not (V["V1 holdout fark > 0"] and V["V4 kesif+holdout ayni isaret"]):
        print("   YON YOK — hipotez dustu.")
    else:
        print("   GOREMIYORUZ — isaret var, MDE/esik asilmadi.")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
