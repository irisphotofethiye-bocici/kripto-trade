#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KAPI KARNESI — marjinal etki, IKI YONLU.
On-kayit: ON_KAYIT_kapi_dengesi.md (commit bd327a6). Olcutler SABIT.

A kolu: her aday kapi EKLENSE ne olur   (aday arsivi alanlari)
B kolu: her mevcut kapi KALDIRILSA ne olur   (golge dogal deneyi)

🔴 `_kontrol_` onekli alanlar YORDAYICI OLARAK KULLANILMAZ — yalniz Z1 kontrol
   katmani. Tarama fonksiyonu bu oneki tasiyanlari GORMEZ (kod duzeyinde koruma).
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, collections, statistics, math

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = json.load(open(os.path.join(PROJE, "scratchpad", "poz_yol", "kapi_veri.json"),
                   encoding="utf-8"))
KESIF = ("2026-08-04", "2026-08-16")
DOGRU = ("2026-08-17", "2026-08-30")

# on-kayit s.5 — A kolu, 13 alan
A_SAYISAL = ["a_vol_x", "a_oi3", "a_oi24", "a_rel3", "a_last1", "a_last3",
             "a_btc_chg3", "a_taker", "a_comp", "a_ma50_mesafe"]
A_BOOL = ["a_dip_yakit", "a_ayrisma", "a_dusuk_float"]
A_KAT = ["a_stage"]


def pencere(w, p):
    return [r for r in w if p[0] <= r["gun"] <= p[1] and r.get("a_score") is not None]


def gun_t(vals_by_gun, nmin=3):
    d = [sum(v) / len(v) for g, v in sorted(vals_by_gun.items()) if len(v) >= nmin]
    if len(d) < 2:
        return None, None, len(d)
    m, sd = sum(d) / len(d), statistics.stdev(d)
    return m, (m / (sd / math.sqrt(len(d))) if sd else None), len(d)


def blok_etkisi(hepsi, sec):
    """sec(r) True olanlar ENGELLENIR. Donus: olcum sozlugu."""
    blok = [r for r in hepsi if sec(r)]
    kal = [r for r in hepsi if not sec(r)]
    if not blok or not kal:
        return None
    gb = collections.defaultdict(list)
    for r in blok:
        gb[r["gun"]].append(r["ret"])
    m, t, nk = gun_t(gb)
    return dict(
        blok_n=len(blok), kal_n=len(kal),
        kalan_oran=100.0 * len(kal) / len(hepsi),
        blok_ret=sum(r["ret"] for r in blok) / len(blok),
        blok_dolar=sum(r["dolar"] for r in blok),
        kal_ret=sum(r["ret"] for r in kal) / len(kal),
        kal_dolar=sum(r["dolar"] for r in kal),
        d_ret=sum(r["ret"] for r in kal) / len(kal) - sum(r["ret"] for r in hepsi) / len(hepsi),
        d_dolar=-sum(r["dolar"] for r in blok),
        gun_t=t, gun_n=nk,
        tp1_blok=100.0 * sum(1 for r in blok if r["_kontrol_tp1"]) / len(blok),
        tp1_kal=100.0 * sum(1 for r in kal if r["_kontrol_tp1"]) / len(kal))


def adaylar_uret(W):
    """on-kayitta sabit liste. Donus: [(ad, sec_fn)]"""
    out = []
    for alan in A_SAYISAL:
        v = sorted(r[alan] for r in W if r.get(alan) is not None)
        if len(v) < 60:
            continue
        q1, q3 = v[len(v) // 4], v[3 * len(v) // 4]
        out.append(("%s <= %.4g  (alt ceyrek)" % (alan[2:], q1),
                    lambda r, a=alan, q=q1: r.get(a) is not None and r[a] <= q))
        out.append(("%s >= %.4g  (ust ceyrek)" % (alan[2:], q3),
                    lambda r, a=alan, q=q3: r.get(a) is not None and r[a] >= q))
    for alan in A_BOOL:
        for hedef in (True, False):
            n = sum(1 for r in W if bool(r.get(alan)) == hedef and r.get(alan) is not None)
            if n >= 25:
                out.append(("%s == %s" % (alan[2:], hedef),
                            lambda r, a=alan, h=hedef: r.get(a) is not None and bool(r[a]) == h))
    for alan in A_KAT:
        for lv in sorted({str(r.get(alan)) for r in W if r.get(alan) is not None}):
            n = sum(1 for r in W if str(r.get(alan)) == lv)
            if n >= 25:
                out.append(("%s == %s" % (alan[2:], lv),
                            lambda r, a=alan, l=lv: str(r.get(a)) == l))
    return out


print("KAPI KARNESI — marjinal etki, IKI YONLU")
print("on-kayit ON_KAYIT_kapi_dengesi.md (bd327a6) · olcutler SABIT")
print("=" * 122)
K = pencere(V, KESIF)
D = pencere(V, DOGRU)
print("KESIF N=%d (%d gun · dolar %+.2f)   ·   DOGRULAMA N=%d (%d gun · dolar %+.2f)"
      % (len(K), len({r["gun"] for r in K}), sum(r["dolar"] for r in K),
         len(D), len({r["gun"] for r in D}), sum(r["dolar"] for r in D)))
print("⚠️ KESIF penceresi kucuk ve neredeyse hic zarar tasimiyor — on-kayitli tarihler")
print("   DEGISTIRILMEDI; gucun yetmemesi bir SONUCTUR ve aynen raporlanir.")

print("\n" + "=" * 122)
print("A KOLU — EKLENECEK kapilar (KESIF yarisi; esik: blok_ret<0 VE gun-t<=-1,5)")
print("=" * 122)
ADAY = adaylar_uret(K)
print("sinanan aday kosul: %d" % len(ADAY))
print("  %-34s %6s %7s %9s %9s %10s %8s %9s" %
      ("kosul (ENGELLENEN dilim)", "blokN", "kalan%", "blok ret", "blok $", "d_islem", "gun-t", "TP1 blok%"))
print("-" * 122)
gecen = []
for ad, fn in ADAY:
    e = blok_etkisi(K, fn)
    if not e:
        continue
    ok = (e["blok_ret"] < 0 and e["gun_t"] is not None and e["gun_t"] <= -1.5)
    if ok:
        gecen.append((ad, fn, e))
    print("  %-34s %6d %6.0f%% %+8.3f%% %+9.1f %+9.3f %8s %8.0f%% %s"
          % (ad[:34], e["blok_n"], e["kalan_oran"], e["blok_ret"], e["blok_dolar"],
             e["d_ret"], ("%+.2f" % e["gun_t"]) if e["gun_t"] else "-",
             e["tp1_blok"], "  <== HAK KAZANDI" if ok else ""))
print("-" * 122)
print("  -> yol egrisine hak kazanan: %d / %d" % (len(gecen), len(ADAY)))

print("\n" + "=" * 122)
print("B KOLU — KALDIRILACAK kapilar (golge dogal deneyi)")
print("=" * 122)
print("golge, botun REDDETTIKLERINI aciyor. Reddedilenler KARLIYSA kapi YANLIS.")
print("⚠️ N kucuk — on-kayitta sinir olarak yazildi. Kesif/dogrulama BOLUNEMEZ, tum pencere.")
print("  %-26s %6s %10s %10s %8s %9s %s" %
      ("kapi (golge kaynagi)", "N", "ort ret", "TOPLAM $", "kazanan", "gun-t", "hukum"))
print("-" * 122)
gol = [r for r in V if r["defter"] == "golge" and r.get("l_kaynak")]
kay = collections.Counter(r["l_kaynak"] for r in gol)
for k, n in kay.most_common():
    if n < 10:
        continue
    w = [r for r in gol if r["l_kaynak"] == k]
    gb = collections.defaultdict(list)
    for r in w:
        gb[r["gun"]].append(r["ret"])
    m, t, nk = gun_t(gb, nmin=2)
    ort = sum(r["ret"] for r in w) / len(w)
    tot = sum(r["dolar"] for r in w)
    hkm = ("KAPI YANLIS olabilir (reddedilenler KARLI)" if (ort > 0 and tot > 0)
           else "kapi dogru gorunuyor" if (ort < 0 and tot < 0) else "belirsiz (ret/dolar celisiyor)")
    print("  %-26s %6d %+9.3f%% %+9.1f %7.0f%% %8s  %s"
          % (k.replace("golge:", "")[:26], len(w), ort, tot,
             100.0 * sum(1 for r in w if r["_kontrol_kaz"]) / len(w),
             ("%+.2f" % t) if t else "-", hkm))

print("\n" + "=" * 122)
print("B KOLU EK — `skor >= 45` LONG kapisi (bugun TERS olculdu, dogrudan sinaniyor)")
print("=" * 122)
lo = [r for r in V if r["yon"] == "LONG" and r.get("a_score") is not None]
if lo:
    for ad, sec in (("skor >= 45 (kapinin ALDIKLARI)", lambda r: r["a_score"] >= 45),
                    ("skor <  45 (kapinin REDDETTIKLERI)", lambda r: r["a_score"] < 45)):
        w = [r for r in lo if sec(r)]
        if len(w) < 20:
            continue
        gb = collections.defaultdict(list)
        for r in w:
            gb[r["gun"]].append(r["ret"])
        m, t, nk = gun_t(gb)
        print("  %-36s N=%4d  ort %+7.3f%%  TOPLAM %+9.1f  kazanan %%%2.0f  gun-t %s"
              % (ad, len(w), sum(r["ret"] for r in w) / len(w), sum(r["dolar"] for r in w),
                 100.0 * sum(1 for r in w if r["_kontrol_kaz"]) / len(w),
                 ("%+.2f" % t) if t else "-"))

# hak kazananlari sonraki adima birak
CIK = os.path.join(PROJE, "scratchpad", "poz_yol", "kapi_hak_kazanan.json")
with open(CIK, "w", encoding="utf-8") as f:
    json.dump([ad for ad, _, _ in gecen], f, ensure_ascii=False)
print("\nhak kazanan kosul listesi yazildi: %s" % os.path.relpath(CIK, PROJE))
print("bot dosyalarina yazim: YOK")
