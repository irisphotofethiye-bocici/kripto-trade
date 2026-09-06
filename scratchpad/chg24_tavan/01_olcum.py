#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""chg24 TAVANI — "belli bir yukselis yapana girmesin"

ON_KAYIT_chg24_tavan.md · commit 1f3f213 — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

🔴 ARSIVIN chg24 ALANI OKUNMAZ (on-kayit bolum 2) — MUMDAN uretilir.
🔴 BIRINCIL METRIK HAM GETIRI (on-kayit bolum 3) — R ikincil.
🔴 SPEARMAN YOK.
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
UFUK = 24                 # ham ileri getiri ufku (saat) — mekaniksiz
MERDIVEN = [5.0, 10.0, 15.0, 20.0]      # EK RAPOR, olcut DEGIL
random.seed(20260907)


def veri(mum):
    """radar_archive ANA kayitlari. chg24 MUMDAN uretilir (arsiv alani OKUNMAZ)."""
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
        if i0 is None or i0 < max(ar.YAPI_BAR, 25):
            continue
        # --- chg24 MUMDAN (on-kayit bolum 2)
        c24 = d[i0 - 24]["c"]
        if not c24:
            continue
        chg24 = (p / c24 - 1) * 100.0

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
        # --- BIRINCIL: HAM ileri getiri, mekaniksiz
        j = i0 + UFUK
        if j >= len(d):
            continue
        ham = (d[j]["c"] / p - 1) * 100.0
        # --- IKINCIL: A0 mekanigi
        sim = ar.simule(d, ix, t, p, stop, p * 1.10)
        if sim is None:
            continue
        son[s] = t
        R, hit = sim
        stop_oldu = 1 if R < 0 and not hit else 0
        out.append({"gun": r["ts"][:10], "sym": s, "chg24": chg24,
                    "ham": ham, "R": R, "hit": hit, "stop_pct": sf,
                    "atr_pct": atr / p * 100.0, "stop_oldu": stop_oldu,
                    "pos": r.get("pos")})
    return out


def dilimle(rows, alan):
    v = sorted(rows, key=lambda x: x[alan])
    n = len(v)
    return [v[i * n // DILIM:(i + 1) * n // DILIM] for i in range(DILIM)]


def gun_fark_t(rows, alan, alt_esik, ust_esik, metrik):
    g = collections.defaultdict(lambda: ([], []))
    for x in rows:
        if x[alan] <= alt_esik:
            g[x["gun"]][0].append(x[metrik])
        elif x[alan] >= ust_esik:
            g[x["gun"]][1].append(x[metrik])
    f = [stx.mean(a) - stx.mean(b) for a, b in g.values()
         if len(a) >= 2 and len(b) >= 2]
    if len(f) < 3:
        return 0.0, 0.0, len(f)
    m = stx.mean(f)
    se = stx.stdev(f) / math.sqrt(len(f))
    return m, ((m / se) if se > 0 else 0.0), len(f)


def kars(rows, alan, metrik):
    """-> (fark, t, mde, ngun, alt_ort, ust_ort, n_alt, n_ust)"""
    p = dilimle(rows, alan)
    alt, ust = p[0], p[-1]
    ae, ue = alt[-1][alan], ust[0][alan]
    ra = [x[metrik] for x in alt]
    ru = [x[metrik] for x in ust]
    fark = stx.mean(ra) - stx.mean(ru)
    _, t, ng = gun_fark_t(rows, alan, ae, ue, metrik)
    mde = 2.8 * math.sqrt(stx.variance(ra) / len(ra) + stx.variance(ru) / len(ru))
    return fark, t, mde, ng, stx.mean(ra), stx.mean(ru), len(ra), len(ru)


def tablo(rows, ad):
    print("   --- %s (N=%d) ---" % (ad, len(rows)))
    print("   %-16s %6s %10s %11s %10s %9s %10s %10s"
          % ("chg24 dilimi", "N", "ort chg24", "HAM +24s", "ort R",
             "isabet%", "stop gen%", "stop-ol%"))
    for p in dilimle(rows, "chg24"):
        if len(p) < 10:
            continue
        print("   %-16s %6d %+10.2f %+10.3f%% %+10.4f %8.1f%% %9.2f%% %9.1f%%"
              % ("%+.1f..%+.1f" % (p[0]["chg24"], p[-1]["chg24"]), len(p),
                 stx.mean([x["chg24"] for x in p]),
                 stx.mean([x["ham"] for x in p]),
                 stx.mean([x["R"] for x in p]),
                 100.0 * sum(x["hit"] for x in p) / len(p),
                 stx.mean([x["stop_pct"] for x in p]),
                 100.0 * sum(x["stop_oldu"] for x in p) / len(p)))


def main():
    print("=" * 108)
    print("chg24 TAVANI — ON_KAYIT_chg24_tavan.md (1f3f213)")
    print("🔴 chg24 MUMDAN uretildi (arsiv alani OKUNMADI) · BIRINCIL metrik HAM getiri")
    print("=" * 108)
    rows = veri(ar.mumlar())
    gunler = sorted(set(x["gun"] for x in rows))
    ks = gunler[int(len(gunler) * ar.KESIF_PAY)]
    kesif = [x for x in rows if x["gun"] < ks]
    hold = [x for x in rows if x["gun"] >= ks]
    print("N=%d · gun=%d · KESIF %d · HOLDOUT %d\n" % (len(rows), len(gunler),
                                                       len(kesif), len(hold)))

    ch = sorted(x["chg24"] for x in rows)
    print("### 0) chg24 DAGILIMI — arsiv alaninin +-15 kirpmasi ASILDI MI?")
    print("   min %+.2f · p05 %+.2f · medyan %+.2f · p95 %+.2f · max %+.2f"
          % (ch[0], ch[len(ch) // 20], stx.median(ch), ch[19 * len(ch) // 20], ch[-1]))
    print("   |chg24| > 15 olan: %d (%%%.1f)   > 20: %d   > 40: %d"
          % (sum(1 for x in ch if abs(x) > 15), 100.0 * sum(1 for x in ch if abs(x) > 15) / len(ch),
             sum(1 for x in ch if x > 20), sum(1 for x in ch if x > 40)))
    print()

    print("### 1) DILIM TABLOSU (ek rapor) — BOLUM 3 AYRISMA SINAMASI da burada")
    tablo(kesif, "KESIF")
    print()
    tablo(hold, "HOLDOUT")
    print()

    print("### 2) 🔴 BIRINCIL — en DUSUK chg24 dilimi vs en YUKSEK, HAM getiri (holdout)")
    fh, th, mdeh, ngh, ah, uh, nah, nuh = kars(hold, "chg24", "ham")
    fk, tk, _, _, ak, uk, _, _ = kars(kesif, "chg24", "ham")
    print("   HOLDOUT  dusuk %+.4f%% (N=%d) · yuksek %+.4f%% (N=%d)" % (ah, nah, uh, nuh))
    print("            fark %+.4f%% · gun-kumeli t %+.2f (%d gun) · MDE %.4f"
          % (fh, th, ngh, mdeh))
    print("   KESIF    dusuk %+.4f%% · yuksek %+.4f%% · fark %+.4f%% (t %+.2f)"
          % (ak, uk, fk, tk))
    print()

    print("### 2b) IKINCIL — ayni karsilastirma R ile (HUKUM KURMAZ)")
    fr, tr, mder, _, ar_, ur_, _, _ = kars(hold, "chg24", "R")
    print("   HOLDOUT  dusuk %+.4f · yuksek %+.4f · fark %+.4f · t %+.2f · MDE %.4f"
          % (ar_, ur_, fr, tr, mder))
    print("   ⚠️ 'yon ayni, guven yalan' — stop varyansi kirar, t sisebilir.")
    print()

    # --- NEGATIF KONTROL
    for lst in (kesif, hold):
        g = collections.defaultdict(list)
        for i, x in enumerate(lst):
            g[x["gun"]].append(i)
        for gun, idx in g.items():
            v = [lst[i]["chg24"] for i in idx]
            random.shuffle(v)
            for i, val in zip(idx, v):
                lst[i]["sahte"] = val
    fs, ts, mdes, _, _, _, _, _ = kars(hold, "sahte", "ham")
    print("### 3) NEGATIF KONTROL — chg24 gun ici permute, AYNI HAT")
    print("   SAHTE holdout fark %+.4f%% · t %+.2f · MDE %.4f" % (fs, ts, mdes))
    neg_bozuk = (fs > 0 and ts >= T_ESIK)
    print("   -> %s" % ("🔴 SAHTE DE ETKI URETTI, duzenek supheli" if neg_bozuk
                        else "temiz (sahte etki uretmedi)"))
    print()

    print("### 4) 🔴 chg24 ile pos AYNI SEY MI? (Spearman YOK — dilim cakismasi)")
    hp = [x for x in hold if x.get("pos") is not None]
    if len(hp) >= 50:
        dc = dilimle(hp, "chg24")
        dp = dilimle(hp, "pos")
        alt_c = set(id(x) for x in dc[0])
        alt_p = set(id(x) for x in dp[0])
        ust_c = set(id(x) for x in dc[-1])
        ust_p = set(id(x) for x in dp[-1])
        print("   en DUSUK dilim cakismasi : %%%.1f" % (100.0 * len(alt_c & alt_p) / len(alt_c)))
        print("   en YUKSEK dilim cakismasi: %%%.1f" % (100.0 * len(ust_c & ust_p) / len(ust_c)))
        print("   (rastgele beklenti %20. Yuksekse bu olcum 'pos' aramasinin")
        print("    yeniden etiketlenmis halidir — giris_arama'da BULUNAMADI.)")
    else:
        print("   pos alani yetersiz (N=%d)" % len(hp))
    print()

    print("### 5) EK — TAVAN MERDIVENI (BILGI; OLCUT DEGIL)")
    print("   %-14s %8s %12s %12s" % ("kural", "N", "HAM +24s", "kalan taban"))
    taban = stx.mean([x["ham"] for x in hold])
    print("   %-14s %8d %+11.3f%% %12s" % ("tavan YOK", len(hold), taban, "-"))
    for m in MERDIVEN:
        kal = [x for x in hold if x["chg24"] < m]
        el = [x for x in hold if x["chg24"] >= m]
        if len(kal) < 30 or len(el) < 30:
            print("   %-14s %8d %12s %12s" % ("chg24 < %+.0f" % m, len(kal), "(N yetersiz)", ""))
            continue
        print("   %-14s %8d %+11.3f%% %+11.3f%%"
              % ("chg24 < %+.0f" % m, len(kal), stx.mean([x["ham"] for x in kal]),
                 stx.mean([x["ham"] for x in el])))
    print("   🔴 Buradan esik SECILMEZ (genis_stop'ta bu yordam kusurlu cikti).")
    print()

    C = {
        "C1 holdout fark > 0": fh > 0,
        "C2 gun-kumeli t >= 2,0": th >= T_ESIK,
        "C3 |fark| > MDE": abs(fh) > mdeh,
        "C4 kesif+holdout ayni isaret": (fk > 0) == (fh > 0),
        "C5 negatif kontrol temiz": not neg_bozuk,
    }
    print("=" * 108)
    print("HUKUM — ON_KAYIT bolum 7")
    print("=" * 108)
    for k, val in C.items():
        print("   %-32s %s" % (k, "GECTI" if val else "DUSTU"))
    print()
    if all(C.values()):
        print("   🔑 YON VAR — az kosmus coin daha iyi ham getiri veriyor.")
        print("   🔴 Bota KONMAZ: once mekanik, sonra portfoy (on-kayit bolum 11).")
        print("      ⚠️ Tavan ISLEM SAYISINI AZALTIR; notrlong penceresi 80 poz istiyor.")
    elif not (C["C1 holdout fark > 0"] and C["C4 kesif+holdout ayni isaret"]):
        print("   YON YOK — hipotez dustu.")
    else:
        print("   GOREMIYORUZ — isaret var, MDE/esik asilmadi.")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
