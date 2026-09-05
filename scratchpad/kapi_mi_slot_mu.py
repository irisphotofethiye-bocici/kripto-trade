#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KAPI MI SECIYOR, SLOT MU SANSLI? (2026-09-05)

ON-KAYIT: ON_KAYIT_kapi_mi_slot_mu.md, commit fc88daa — KOSTURULMADAN ONCE.

S1  alinan 44 vs alinmayan 127            -> SLOT SANSI
S2  kapili 171 vs eslesmis KAPISIZ kontrol -> KAPI SECIMI
🔴 Ikisinde de SLOT UYGULANMAZ (slot etkisi S1'in olctugu sey).

Mekanik ve karar fonksiyonu etiket_karsiolgu.py'den CAGRILIR. Salt-okunur.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import sys, json, os, math, statistics as stx, collections

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURA)
sys.path.insert(0, BURA)
sys.path.insert(0, KOK)
import etiket_karsiolgu as ek

ek.BAS = "2026-08-19"
ARSIV = os.path.join(KOK, "testbot_aday_arsiv.jsonl")


def veri():
    kl, fn, idx, atrs, ma_ft = {}, {}, {}, {}, {}
    for f in sorted(os.listdir(ek.ESKI_K)):
        if not f.endswith(".json"):
            continue
        sym = f[:-5]
        b = ek.birlestir(os.path.join(ek.ESKI_K, f), os.path.join(ek.YENI_K, f))
        if not b or len(b) < 300:
            continue
        kl[sym] = b
        fn[sym] = ek.birlestir(os.path.join(ek.ESKI_F, f), os.path.join(ek.YENI_F, f)) or []
        idx[sym] = {x["t"]: i for i, x in enumerate(b)}
        atrs[sym] = ek.ir.atr_serisi(b)
        ma_ft[sym] = [x["t"] for x in fn[sym]]
    return kl, fn, idx, atrs, ma_ft


def kararlar_ve_kontrol(bp):
    """-> (kapili, kontrol)  her biri [(t_ms, sym)]  — LONG yonunde degerlendirilir."""
    kapili, kontrol = [], []
    damga_kapili = collections.defaultdict(list)
    damga_kontrol = collections.defaultdict(list)
    for line in open(ARSIV, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        ts = r.get("ts") or ""
        if ts[:10] < ek.BAS:
            continue
        if r.get("rejim") in (None, "BILINMIYOR"):
            continue
        pil = {"smart": r.get("smart"), "taker": r.get("taker"),
               "top_ls": r.get("top_ls"), "glob_ls": r.get("glob_ls")}
        try:
            k = ek.testbot.karar_yon("NOTR", r, pil, bool(r.get("dusuk_float")),
                                     None, False, bp.get(ts[:10]), False)
        except Exception:
            continue
        try:
            t = ek.utc_ms(ts)
        except Exception:
            continue
        if k and k[0] == "LONG":
            damga_kapili[ts].append((t, r.get("sym")))
        else:
            damga_kontrol[ts].append((t, r.get("sym")))
    # KONTROL: yalniz kapili karar URETILEN damgalardan (zaman eslesmesi TAM)
    for ts, lst in damga_kapili.items():
        kapili += lst
        kontrol += damga_kontrol.get(ts, [])
    kapili.sort()
    kontrol.sort()
    return kapili, kontrol


def islemler(liste, kl, fn, idx, atrs, ma_ft, tekil=True):
    """SLOT UYGULANMAZ. tekil=True -> ayni (sym,saat) bir kez."""
    gor = set()
    out = []
    for t, sym in liste:
        b = kl.get(sym)
        if not b:
            continue
        s = (t // 3600000) * 3600000
        if tekil:
            if (sym, s) in gor:
                continue
            gor.add((sym, s))
        si = idx[sym].get(s)
        if si is None:
            continue
        r = ek.islem(b, atrs[sym], si, ma_ft[sym], fn.get(sym) or [], "LONG")
        if not r:
            continue
        r["sym"] = sym
        r["gun"] = r["gir_ms"] // 86400000
        out.append(r)
    return out


def gun_ort(ps):
    g = collections.defaultdict(list)
    for p in ps:
        g[p["gun"]].append(p["net"])
    return [sum(v) / len(v) for v in g.values()]


def iki_ornek(a, b):
    ga, gb = gun_ort(a), gun_ort(b)
    if len(ga) < 3 or len(gb) < 3:
        return None, None, None
    ma, mb = sum(ga) / len(ga), sum(gb) / len(gb)
    se = math.sqrt(stx.variance(ga) / len(ga) + stx.variance(gb) / len(gb))
    return (ma - mb), ((ma - mb) / se if se else None), (2.0 * se if se else None)


def satir(ad, ps):
    if not ps:
        print("  %-24s (yok)" % ad)
        return
    g = gun_ort(ps)
    print("  %-24s N=%-4d gun=%-3d islem-ort %+7.3f%%  gun-ort %+7.3f%%  kazanan %%%.1f"
          % (ad, len(ps), len(g), stx.mean([p["net"] for p in ps]),
             sum(g) / len(g), sum(1 for p in ps if p["net"] > 0) / len(ps) * 100))


def main():
    print("=" * 96)
    print("KAPI MI SECIYOR, SLOT MU SANSLI?")
    print("=" * 96)
    print("ON-KAYIT: ON_KAYIT_kapi_mi_slot_mu.md commit fc88daa — KOSMADAN once")
    print("🔴 S1/S2'de SLOT UYGULANMAZ. Pencere %s -> 09-02\n" % ek.BAS)

    bp = ek.btc_pay_serisi()
    kl, fn, idx, atrs, ma_ft = veri()
    kapili, kontrol = kararlar_ve_kontrol(bp)
    print("kapili karar: %d · eslesmis kontrol adayi: %d" % (len(kapili), len(kontrol)))

    # --- alinan / alinmayan ayrimi: slot simulasyonunu KARAR listesinde kosturup isaretle
    kar3 = [(t, s, "LONG") for t, s in kapili]
    alinan_ps = ek.simule(kar3, kl, fn, idx, atrs, ma_ft)

    hepsi = islemler(kapili, kl, fn, idx, atrs, ma_ft)
    alinan, alinmayan = [], []
    for p in hepsi:
        # gir_ms bir sonraki bar; karar bari = gir_ms - 1 saat
        a = (p["sym"], p["gir_ms"])
        (alinan if a in {(q["sym"], q["gir_ms"]) for q in alinan_ps} else alinmayan).append(p)
    kont = islemler(kontrol, kl, fn, idx, atrs, ma_ft)

    print()
    print("### S1 — SLOT SANSI")
    satir("alinan (slot gecti)", alinan)
    satir("alinmayan", alinmayan)
    f1, t1, m1 = iki_ornek(alinan, alinmayan)
    if f1 is not None:
        print("  fark %+.3f%%  t_gun %+.2f  MDE %.3f  -> %s"
              % (f1, t1 or 0, m1, "GORULUR" if abs(f1) >= m1 else "goremiyoruz"))
    print()
    print("### S2 — KAPI SECIMI")
    satir("kapili (tumu)", hepsi)
    satir("eslesmis KONTROL", kont)
    f2, t2, m2 = iki_ornek(hepsi, kont)
    if f2 is not None:
        print("  fark %+.3f%%  t_gun %+.2f  MDE %.3f  -> %s"
              % (f2, t2 or 0, m2, "GORULUR" if abs(f2) >= m2 else "goremiyoruz"))

    print()
    print("=" * 96)
    print("HUKUM — ON_KAYIT_kapi_mi_slot_mu.md bolum 4")
    print("=" * 96)
    K1 = f2 is not None and f2 > 0 and t2 is not None and t2 >= 2.0
    print("K1  S2 fark > 0 ve t_gun >= +2,0 : %s  t=%s -> %s"
          % (("%+.3f%%" % f2) if f2 is not None else "yok",
             ("%.2f" % t2) if t2 is not None else "yok", "GECTI" if K1 else "DUSTU"))
    K2 = f1 is not None and m1 is not None and abs(f1) < m1
    print("K2  S1 fark MDE ALTINDA (slot sansi gosterilemedi): %s vs MDE %s -> %s"
          % (("%.3f" % abs(f1)) if f1 is not None else "yok",
             ("%.3f" % m1) if m1 is not None else "yok", "GECTI" if K2 else "DUSTU"))
    if kont:
        print("K3  kontrolun MUTLAK getirisi: islem-ort %+.3f%%  (betimleyici)"
              % stx.mean([p["net"] for p in kont]))
    print()
    if K1 and K2:
        print("HUKUM: 🟢 KAPILAR SECIYOR — karsi-olgu desteklenir, celiski cozulur.")
    elif K1 and not K2:
        print("HUKUM: ⚠️ KAPI SECIYOR AMA SLOT DA SANSLIYDI -> karsi-olgu SISIK.")
    elif (not K1) and K2:
        print("HUKUM: 🔴 KAPILAR SECMIYOR -> C'nin sonucu gurultu; NOTR MODELI ZAYIFLAR.")
    else:
        print("HUKUM: 🔴 HICBIRI ACIKLAMIYOR -> celiski COZULMEDI.")
    print("\n⚠️ K2 bir YOKLUK testidir: 'slot sansi YOK' degil 'GOSTERILEMEDI'.")
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
