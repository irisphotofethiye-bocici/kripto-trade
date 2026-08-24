#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CIKIS TERSINE MUHENDISLIK — 5 dakikalik poz verisinden cikis kestirilebilir mi?

KULLANICI (2026-08-21): "pozlarin 5 dakikalik verisini kontrol edelim, burdan
cikis kestirilebilir mi diye. Her acidan bak, tersine muhendislikle ilerle."

VERI (yalnizca bizim):
   pozisyon_izleme.jsonl  5 dk · 78 alan · 109 pozisyon · 08-13 -> simdi
   perp_seri/             5 dk · OI · top_ls · glob_ls · taker (izleyici DONDURUYOR)

⚠️ CANLI/DONMUS AYRIMI (olculdu, ortak.py):
   CANLI  : pnl_pct · fiyat · taker_15/60 · d_taker · hacim_* · islem_15 · chg24
   DONMUS : oi3 · oi24 · top_ls · glob_ls · vol_x · pos   -> perp_seri'den alinir

DORT ACI:
  1) TEPE ANI      — tepede olan bar, ayni pozisyonun diger barlarindan ayrilir mi?
  2) TEPE SONRASI  — tepeden sonraki 1-3 barda erken uyari var mi?
  3) AYNI YASTA    — N. barda kazananla kaybeden ayrilyor mu? (ileriye bakma YOK)
  4) YENI UC       — son yeni uctan sonra pozisyon ne kadar yasiyor?

ILERIYE BAKMA YASAGI: her acida "t aninda elde olan" ile "t'den SONRA olan"
ayri tutulur. Tepe tanimi geriye donuktur; 1. ve 2. acilar bunu ACIKCA
"tespit edilebilir mi" sorusu olarak sorar, tahmin olarak degil.

HUKUM YAZILMAZ.
SALT OKUMA.
"""
import os, sys, json, collections, statistics as sx, random

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ortak                                                    # noqa: E402

random.seed(101)

CANLI = ["pnl_pct", "d_pnl_pct", "taker_15", "taker_60", "d_taker", "hacim_x",
         "hacim_15_usdt", "islem_15", "ort_islem_usdt", "chg24", "funding",
         "stopa_uzaklik_pct", "hedefe_uzaklik_pct"]
SERI = ["oi_s", "top_ls_s", "glob_ls_s", "taker_orani_s", "hacim_5m_s"]


def hazirla():
    poz = ortak.pozisyonlar(en_az_goruntu=12, zengin=True)
    out = []
    for p in poz:
        s = p["seri"]
        pnl = [g.get("pnl_pct") for g in s]
        if any(x is None for x in pnl) or len(pnl) < 12:
            continue
        tepe = max(pnl)
        it = pnl.index(tepe)
        out.append({"id": p["id"], "sym": p["sym"], "yon": p["yon"], "seri": s,
                    "pnl": pnl, "tepe": tepe, "i_tepe": it, "son": pnl[-1],
                    "sonuc": p["sonuc"]})
    return out


def _d(s, i, alan, geri=3):
    """alan'in son `geri` bardaki degisimi (yuzde). None guvenli."""
    if i - geri < 0:
        return None
    a, b = s[i - geri].get(alan), s[i].get(alan)
    if a is None or b is None or a == 0:
        return None
    return (b - a) / abs(a) * 100


def aci1_tepe(P):
    """TEPE bari vs AYNI pozisyonun rastgele diger bari (pozisyon-ici kontrol)."""
    print("\n" + "=" * 100)
    print("ACI 1 — TEPE ANI: tepedeki bar, ayni pozisyonun diger barlarindan ayrilyor mu?")
    print("(pozisyon-ici kontrol: sembol · rejim · giris sabit)")
    print("=" * 100)
    tepe, kont = [], []
    for p in P:
        s, it = p["seri"], p["i_tepe"]
        if it < 4 or it > len(s) - 3:
            continue
        tepe.append((p, it))
        aday = [j for j in range(4, len(s) - 2) if abs(j - it) >= 3]
        if aday:
            kont.append((p, random.choice(aday)))
    if len(tepe) < 25:
        print("  N=%d yetersiz" % len(tepe))
        return
    print("  tepe orneklemi %d · kontrol %d" % (len(tepe), len(kont)))
    print("\n  %-20s %12s %12s %12s" % ("olcum", "TEPEDE", "KONTROL", "fark"))
    print("  " + "-" * 58)
    olcumler = [("d_taker (3 bar)", lambda p, i: _d(p["seri"], i, "taker_15")),
                ("hacim_x", lambda p, i: p["seri"][i].get("hacim_x")),
                ("d_hacim15 (3 bar)", lambda p, i: _d(p["seri"], i, "hacim_15_usdt")),
                ("d_islem15 (3 bar)", lambda p, i: _d(p["seri"], i, "islem_15")),
                ("ort_islem_usdt", lambda p, i: p["seri"][i].get("ort_islem_usdt")),
                ("taker_15 seviye", lambda p, i: p["seri"][i].get("taker_15")),
                ("d_OI (3 bar)", lambda p, i: _d(p["seri"], i, "oi_s")),
                ("d_top_ls (3 bar)", lambda p, i: _d(p["seri"], i, "top_ls_s")),
                ("taker_orani_s", lambda p, i: p["seri"][i].get("taker_orani_s")),
                ("d_pnl (son bar)", lambda p, i: p["seri"][i].get("d_pnl_pct"))]
    for ad, f in olcumler:
        a = [f(p, i) for p, i in tepe]
        b = [f(p, i) for p, i in kont]
        a = [x for x in a if x is not None]
        b = [x for x in b if x is not None]
        if len(a) < 15 or len(b) < 15:
            print("  %-20s %12s %12s %12s" % (ad, "-", "-", "N az"))
            continue
        print("  %-20s %+12.4f %+12.4f %+12.4f" % (ad, sx.median(a), sx.median(b),
                                                   sx.median(a) - sx.median(b)))


def aci2_tepe_sonrasi(P):
    print("\n" + "=" * 100)
    print("ACI 2 — TEPEDEN SONRAKI 1-3 BAR: erken uyari var mi?")
    print("=" * 100)
    for k in (1, 2, 3):
        satir = []
        for ad, alan in (("d_taker15", "taker_15"), ("d_hacim15", "hacim_15_usdt"),
                         ("d_OI", "oi_s"), ("d_top_ls", "top_ls_s")):
            v = []
            for p in P:
                s, it = p["seri"], p["i_tepe"]
                if it + k >= len(s) or it < 4:
                    continue
                a, b = s[it].get(alan), s[it + k].get(alan)
                if a is None or b is None or a == 0:
                    continue
                v.append((b - a) / abs(a) * 100)
            satir.append((ad, sx.median(v) if len(v) >= 15 else None, len(v)))
        print("  +%d bar (%2d dk): %s" % (k, k * 5,
              "  ".join("%s %s (N=%d)" % (a, "%+.3f" % m if m is not None else "-", n)
                        for a, m, n in satir)))
    # PNL dususu ne kadar hizli
    dus = []
    for p in P:
        s, it = p["seri"], p["i_tepe"]
        if it + 3 < len(s):
            dus.append(p["pnl"][it] - p["pnl"][it + 3])
    if dus:
        print("\n  tepeden 3 bar (15 dk) sonra PnL dususu: medyan %.3f puan" % sx.median(dus))


def aci3_ayni_yas(P):
    print("\n" + "=" * 100)
    print("ACI 3 — AYNI YASTA: N. barda kazananla kaybeden ayrilyor mu? (ileriye bakma YOK)")
    print("=" * 100)
    kaz = [p for p in P if p["sonuc"] and p["sonuc"]["net_usdt"] > 0]
    kay = [p for p in P if p["sonuc"] and p["sonuc"]["net_usdt"] <= 0]
    print("  kazanan %d · kaybeden %d" % (len(kaz), len(kay)))
    if len(kaz) < 15 or len(kay) < 15:
        print("  N yetersiz")
        return
    print("\n  %-6s %-18s %11s %11s %11s" % ("bar", "olcum", "KAZANAN", "KAYBEDEN", "fark"))
    print("  " + "-" * 62)
    for n in (6, 12, 24):
        for ad, f in (("pnl_pct", lambda s, i: s[i].get("pnl_pct")),
                      ("hacim_x", lambda s, i: s[i].get("hacim_x")),
                      ("taker_15", lambda s, i: s[i].get("taker_15")),
                      ("yeni uc yasi", None)):
            def al(grup):
                v = []
                for p in grup:
                    s = p["seri"]
                    if len(s) <= n:
                        continue
                    if ad == "yeni uc yasi":
                        en, son = p["pnl"][0], 0
                        for j in range(1, n + 1):
                            if p["pnl"][j] > en:
                                en, son = p["pnl"][j], j
                        v.append(n - son)
                    else:
                        x = f(s, n)
                        if x is not None:
                            v.append(x)
                return v
            a, b = al(kaz), al(kay)
            if len(a) < 10 or len(b) < 10:
                continue
            print("  %-6d %-18s %+11.4f %+11.4f %+11.4f"
                  % (n, ad, sx.median(a), sx.median(b), sx.median(a) - sx.median(b)))
        print()


def aci4_yeni_uc(P):
    print("=" * 100)
    print("ACI 4 — YENI UC: son yeni uctan sonra pozisyon ne kadar yasiyor?")
    print("=" * 100)
    for ad, grup in (("KAZANAN", [p for p in P if p["sonuc"] and p["sonuc"]["net_usdt"] > 0]),
                     ("KAYBEDEN", [p for p in P if p["sonuc"] and p["sonuc"]["net_usdt"] <= 0])):
        if len(grup) < 10:
            continue
        kalan = [len(p["seri"]) - 1 - p["i_tepe"] for p in grup]
        oran = [(len(p["seri"]) - 1 - p["i_tepe"]) / max(1, len(p["seri"]) - 1) for p in grup]
        geri = [p["tepe"] - p["son"] for p in grup]
        print("  %-9s N=%-3d  tepeden sonra medyan %4.0f bar (%3.0f dk) · yolun %%%2.0f'i · "
              "geri verilen %5.2f puan"
              % (ad, len(grup), sx.median(kalan), sx.median(kalan) * 5,
                 100 * sx.median(oran), sx.median(geri)))
    print("\n  'N barda yeni uc yoksa cik' kurali kac pozisyonu ERKEN keserdi?")
    print("  %-8s %14s %14s %14s" % ("N bar", "kazananda kes", "kaybedende kes", "ayrim"))
    for n in (3, 6, 12, 24):
        r = {}
        for ad, grup in (("kaz", [p for p in P if p["sonuc"] and p["sonuc"]["net_usdt"] > 0]),
                         ("kay", [p for p in P if p["sonuc"] and p["sonuc"]["net_usdt"] <= 0])):
            kes = 0
            for p in grup:
                en, son = p["pnl"][0], 0
                for j in range(1, len(p["pnl"])):
                    if p["pnl"][j] > en:
                        en, son = p["pnl"][j], j
                    elif j - son >= n:
                        kes += 1
                        break
            r[ad] = 100 * kes / len(grup) if grup else 0
        print("  %-8d %13.0f%% %13.0f%% %13.0f puan" % (n, r["kaz"], r["kay"], r["kay"] - r["kaz"]))


if __name__ == "__main__":
    P = hazirla()
    print("TERSINE MUHENDISLIK — %d pozisyon (>=12 anlik goruntu)" % len(P))
    kap = [p for p in P if p["sonuc"]]
    print("kapali: %d · acik: %d" % (len(kap), len(P) - len(kap)))
    aci1_tepe(P)
    aci2_tepe_sonrasi(P)
    aci3_ayni_yas(kap)
    aci4_yeni_uc(kap)
    print("\nHUKUM YAZILMADI. bot dosyalarina yazim: YOK")
