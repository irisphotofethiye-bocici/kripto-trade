#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOGA'DA SECIM — bot neyi secti, ne secseydi kazanirdi?
On-kayit: ON_KAYIT_boga_secim.md (commit 2866b50, KOSUMDAN ONCE). Olcutler SABIT.

ASAMA A: huni (her asamada tutulan vs atilan) + vetolarin karnesi
ASAMA B: 24 alan x 2 kesim = 48 sinama, PERMUTASYONLA duzeltilmis
ASAMA C: ters soru (yukselenler neydi) — betimleyici, ayri hukum YOK

🔴 "En iyi hucre secilmez" kurali burada ARACLA uygulanir: 1.000 permutasyonda
   TUM tarama tekrarlanir ve EN BUYUK |t| kaydedilir; gercek en iyi o dagilima
   karsi olculur. Tek bir hucre TEK BASINA rapor edilmez.
🔴 BIRIM = SEMBOL-GUN · gun-kumeli t zorunlu.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, math, random, datetime, statistics, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARSIV = os.path.join(PROJE, "testbot_aday_arsiv.jsonl")
MUM = os.path.join(PROJE, "scratchpad", "aday_pencere_1h")
BAS = "2026-08-21"
YEREL_FARK = 3
SAAT_MS = 3600 * 1000
H_BIR, H_IKI = 4, 24
PERM = 1000
ESIK_FARK = 1.0
random.seed(20260904)

ALANLAR = ["ayrisma", "btc_chg3", "chg24", "comp", "dip_yakit", "dusuk_float",
           "float_oran", "funding", "glob_ls", "last1", "last3", "ma50_mesafe",
           "mcap", "oi24", "oi3", "pos", "price", "rel3", "score", "taker",
           "top_ls", "vol_x"]
KATEGORIK = ["smart", "stage"]


def utc_ts(s):
    d = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M") - datetime.timedelta(hours=YEREL_FARK)
    return int((d - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)


def t_iki(a, b):
    if len(a) < 5 or len(b) < 5:
        return None, None
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    se = math.sqrt(va / len(a) + vb / len(b))
    return (ma - mb), ((ma - mb) / se if se else None)


def gun_ort(kayit):
    """[(sym, gun, deger)] -> sembol-gun ortalamalari listesi"""
    g = collections.defaultdict(list)
    for s, d, v in kayit:
        g[(s, d)].append(v)
    return [sum(v) / len(v) for v in g.values()]


def main():
    print("BOGA'DA SECIM — bot neyi secti, ne secseydi kazanirdi?")
    print("on-kayit ON_KAYIT_boga_secim.md (2866b50) · olcutler SABIT")
    print("=" * 108)

    # ------------------------------------------------------------- mumlar
    mum = {}
    for fn in os.listdir(MUM):
        if not fn.endswith(".json"):
            continue
        try:
            b = json.load(open(os.path.join(MUM, fn)))
        except Exception:
            continue
        if b:
            mum[fn[:-5]] = (b, {x[0]: j for j, x in enumerate(b)})

    # ------------------------------------------------------------- arsiv
    R = []
    for l in open(ARSIV, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        ts = str(r.get("ts") or "")
        if ts[:10] < BAS or not str(r.get("rejim") or "").upper().startswith("BOGA"):
            continue
        s = r.get("sym")
        if not s or s not in mum:
            continue
        bar, ix = mum[s]
        t0 = utc_ts(ts)
        a = ix.get(t0 - (t0 % SAAT_MS))
        if a is None:
            continue
        e = bar[a][3]
        if e <= 0:
            continue
        for h, ad in ((H_BIR, "r4"), (H_IKI, "r24")):
            j = ix.get(t0 - (t0 % SAAT_MS) + h * SAAT_MS)
            r[ad] = ((bar[j][3] - e) / e * 100.0) if j is not None else None
        r["_gun"] = ts[:10]
        if r.get("r4") is not None:
            R.append(r)

    print("olculebilir BOGA satiri: %d · sembol %d · gun %d"
          % (len(R), len({x["sym"] for x in R}), len({x["_gun"] for x in R})))

    def sg(w, alan="r4"):
        return gun_ort([(x["sym"], x["_gun"], x[alan]) for x in w if x.get(alan) is not None])

    # ================================================== ASAMA A — HUNI
    print("\n" + "=" * 108)
    print("ASAMA A) HUNI — her asamada tutulan kumenin ham getirisi (H=%d saat)" % H_BIR)
    print("-" * 108)
    print("  %-34s %7s %9s %11s %11s" % ("asama", "satir", "sem-gun", "ort %", "medyan %"))

    def yaz(ad, w):
        v = sg(w)
        if len(v) < 5:
            print("  %-34s %7d %9d  (N yetersiz)" % (ad, len(w), len(v)))
            return None
        print("  %-34s %7d %9d %+10.3f%% %+10.3f%%"
              % (ad, len(w), len(v), sum(v) / len(v), statistics.median(v)))
        return v

    v_tum = yaz("1. taranan (hacim suzgeci sonrasi)", R)
    v_skor = yaz("2. skor >= 45", [x for x in R if (x.get("score") or 0) >= 45])
    kapi = [x for x in R if str(x.get("karar") or "").startswith("LONG")]
    v_kapi = yaz("3. kapiyi gecen (LONG karari)", kapi)
    veto_l = [x for x in R if str(x.get("karar") or "") == "VETO:long_veto"]
    veto_b = [x for x in R if str(x.get("karar") or "") == "VETO:blowoff"]
    yaz("   VETO:long_veto (ENGELLENEN)", veto_l)
    yaz("   VETO:blowoff (ENGELLENEN)", veto_b)

    print("\n  VETO KARNESI — engellenen dilim, kalanla kiyaslandiginda:")
    kalan = [x for x in R if str(x.get("karar") or "") not in ("VETO:long_veto", "VETO:blowoff")]
    for ad, w in (("long_veto", veto_l), ("blowoff", veto_b)):
        a, b = sg(w), sg(kalan)
        f, t = t_iki(a, b)
        if f is None:
            continue
        hk = "DOGRU calisiyor (kotuyu engelledi)" if f < 0 else "TERS calisiyor (IYIYI engelledi)"
        print("    %-12s engellenen %+7.3f%% · kalan %+7.3f%% · fark %+7.3f%% (t %s)  -> %s"
              % (ad, sum(a) / len(a), sum(b) / len(b), f, ("%+.2f" % t) if t else "-", hk))

    if v_tum and v_kapi:
        f, t = t_iki(v_kapi, v_tum)
        print("\n  KAPI KATKISI: kapiyi gecen - taranan = %+.3f%%  (t %s)"
              % (f, ("%+.2f" % t) if t else "-"))

    # ================================================== ASAMA B — TARAMA
    print("\n" + "=" * 108)
    print("ASAMA B) AYIRICI TARAMASI — 'her ihtimali hesapla'")
    print("-" * 108)

    def hucreler(W):
        """[(ad, ust_liste, alt_liste)] — 22 sayisal x 2 kesim + kategorikler"""
        out = []
        for a in ALANLAR:
            v = sorted(x[a] for x in W if isinstance(x.get(a), (int, float)))
            if len(v) < 80:
                continue
            for pay, et in ((0.25, "ceyrek"), (0.10, "ondalik")):
                lo = v[int(pay * len(v))]
                hi = v[int((1 - pay) * len(v))]
                if lo >= hi:
                    continue
                ust = [x for x in W if isinstance(x.get(a), (int, float)) and x[a] >= hi]
                alt = [x for x in W if isinstance(x.get(a), (int, float)) and x[a] <= lo]
                out.append(("%s (%s)" % (a, et), ust, alt))
        for a in KATEGORIK:
            lv = sorted({str(x.get(a)) for x in W if x.get(a) is not None})
            for k in lv:
                ust = [x for x in W if str(x.get(a)) == k]
                alt = [x for x in W if str(x.get(a)) != k]
                if len(ust) >= 40:
                    out.append(("%s == %s" % (a, k), ust, alt))
        return out

    HC = hucreler(R)
    print("  sinanan hucre: %d  (%d sayisal alan x 2 kesim + kategorikler)"
          % (len(HC), len(ALANLAR)))

    sonuc = []
    for ad, ust, alt in HC:
        a, b = sg(ust), sg(alt)
        f, t = t_iki(a, b)
        if t is not None:
            sonuc.append((abs(t), t, f, ad, len(a), len(b)))
    sonuc.sort(reverse=True)
    print("\n  EN GUCLU 10 HUCRE (ham — permutasyon esigi ASAGIDA, once ona bak):")
    print("  %-30s %9s %9s %8s %8s" % ("hucre", "fark %", "t", "ust n", "alt n"))
    for at, t, f, ad, na, nb in sonuc[:10]:
        print("  %-30s %+8.3f%% %+8.2f %8d %8d" % (ad[:30], f, t, na, nb))

    # --- permutasyon: TUM taramayi tekrarla, en buyuk |t|'yi kaydet
    print("\n  🔴 PERMUTASYON — sonuc etiketleri karistirilip TUM tarama tekrarlaniyor")
    print("     ('48 hucre arayinca sans eseri hangi t'yi bulurduk?')")
    tas = [x["r4"] for x in R]
    en_iyiler = []
    for p in range(PERM):
        random.shuffle(tas)
        for i, x in enumerate(R):
            x["_perm"] = tas[i]
        mx = 0.0
        for ad, ust, alt in HC:
            a = gun_ort([(x["sym"], x["_gun"], x["_perm"]) for x in ust])
            b = gun_ort([(x["sym"], x["_gun"], x["_perm"]) for x in alt])
            _, t = t_iki(a, b)
            if t is not None and abs(t) > mx:
                mx = abs(t)
        en_iyiler.append(mx)
        if (p + 1) % 200 == 0:
            print("     ... %d/%d" % (p + 1, PERM))
    en_iyiler.sort()
    q95 = en_iyiler[int(0.95 * PERM)]
    gercek = sonuc[0][0] if sonuc else 0.0
    ustte = sum(1 for x in en_iyiler if x >= gercek)
    print("\n     sans dagiliminin en buyuk |t|'si : medyan %.2f · %%95 %.2f · max %.2f"
          % (en_iyiler[PERM // 2], q95, en_iyiler[-1]))
    print("     GERCEK taramanin en iyi |t|'si   : %.2f  (%s)" % (gercek, sonuc[0][3] if sonuc else "-"))
    print("     gercek degerin yuzdeligi         : %%%.1f" % (100.0 * (PERM - ustte) / PERM))
    k1 = gercek >= q95
    print("     -> K1: %s" % ("GECTI (sans esigini asti)" if k1 else "DUSTU (sans esigi ASILMADI)"))

    # --- K2 bolunmus yari + K3 buyukluk
    print("\n  K2/K3 — en iyi aday, yarilarda ayakta mi ve fark yeterince buyuk mu?")
    if sonuc:
        _, t0v, f0, ad0, _, _ = sonuc[0]
        gunler = sorted({x["_gun"] for x in R})
        orta = gunler[len(gunler) // 2]
        for ad, ust, alt in HC:
            if ad != ad0:
                continue
            for et, sec in (("A yari", lambda x: x["_gun"] < orta), ("B yari", lambda x: x["_gun"] >= orta)):
                a = sg([x for x in ust if sec(x)])
                b = sg([x for x in alt if sec(x)])
                f, t = t_iki(a, b)
                print("    %-8s %-26s fark %s · t %s"
                      % (et, ad0[:26], ("%+.3f%%" % f) if f is not None else "-",
                         ("%+.2f" % t) if t else "-"))
        print("    K3 (|fark| >= %%%.1f): %s" % (ESIK_FARK, "GECTI" if abs(f0) >= ESIK_FARK else "DUSTU"))

    # ================================================== ASAMA C — TERS
    print("\n" + "=" * 108)
    print("ASAMA C) TERS SORU — yukselenler neydi? (betimleyici, AYRI HUKUM YOK)")
    print("-" * 108)
    g = collections.defaultdict(list)
    for x in R:
        g[(x["sym"], x["_gun"])].append(x)
    sgl = [(k, sum(y["r4"] for y in v) / len(v), v[0]) for k, v in g.items()]
    sgl.sort(key=lambda z: -z[1])
    n10 = max(5, len(sgl) // 10)
    ust, alt = sgl[:n10], sgl[-n10:]
    print("  en iyi %%10 (%d sembol-gun) vs en kotu %%10 — alan ortalamalari:" % n10)
    print("  %-14s %12s %12s %10s" % ("alan", "en iyi", "en kotu", "fark"))
    for a in ALANLAR:
        va = [z[2][a] for z in ust if isinstance(z[2].get(a), (int, float))]
        vb = [z[2][a] for z in alt if isinstance(z[2].get(a), (int, float))]
        if len(va) < 5 or len(vb) < 5:
            continue
        ma, mb = sum(va) / len(va), sum(vb) / len(vb)
        print("  %-14s %+11.3f %+11.3f %+9.3f" % (a, ma, mb, ma - mb))
    print("\n  ⚠️ Bu tablo SONUCA GORE secilmis kumelerin ozetidir — hukum TASIMAZ.")
    print("     Ayni sinama Asama B'de ONCEDEN, permutasyon duzeltmesiyle yapildi.")

    print("\n" + "=" * 108)
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
