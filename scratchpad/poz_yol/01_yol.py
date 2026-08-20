#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASAMA 1a — POZISYONUN FILM SERIDI.

SORU (kullanici, 2026-08-20): "botun actigi pozlarin her asamasini, hangi oranda
ne kadar dustugunu, o sirada hacim/funding gibi karar verilerindeki degisimleri
ve birbirlerine oranini incele."

BU BETIK YALNIZ *CANLI* ALANLARI KULLANIR (ortak.py'deki olcume gore):
   fiyat · pnl_pct · taker_15 · taker_60 · d_taker · hacim_15/60 · hacim_x ·
   islem_15 · ort_islem_usdt · chg24 · funding
OI ve long/short DONMUS geldigi icin buraya GIRMEZ — onlar 02_oi.py'de,
perp_seri indirmesi bitince.

HUKUM YAZMAZ. 80 pozisyon · 7 gun = az; bu asama HIPOTEZ URETIR.
SALT OKUMA.
"""
import os, sys, statistics as sx, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ortak                                                    # noqa: E402


def _ozet(v):
    if not v:
        return None
    return (len(v), sx.mean(v), sx.median(v))


def yol_olcumleri(p):
    """Tek pozisyonun yol istatistikleri. -> dict | None"""
    s = p["seri"]
    pnl = [g.get("pnl_pct") for g in s if g.get("pnl_pct") is not None]
    if len(pnl) < 5:
        return None
    son = p["sonuc"]
    tepe, dip = max(pnl), min(pnl)
    i_tepe = pnl.index(tepe)
    return {
        "id": p["id"], "sym": p["sym"], "yon": p["yon"],
        "sebep": son["sebep"], "net": son["net_usdt"],
        "rejim": son.get("rejim_giriste"), "chg24_g": son.get("chg24_giriste"),
        "tutma_saat": son.get("tutma_saat"),
        "tepe_pct": tepe, "dip_pct": dip, "son_pct": pnl[-1],
        # tepeye kacinci goruntude ulasildi (0-1 arasi: yolun neresinde)
        "tepe_konum": i_tepe / max(1, len(pnl) - 1),
        "geri_verilen": tepe - pnl[-1],
        "goruntu": len(pnl),
    }


def kesit(baslik, kayitlar, alan="net"):
    o = _ozet([k[alan] for k in kayitlar])
    if not o:
        print("  %-34s  —" % baslik)
        return
    kz = sum(1 for k in kayitlar if k["net"] > 0)
    print("  %-34s N=%-3d  toplam %+9.2f$  medyan %+7.2f  kazanan %d (%%%.0f)"
          % (baslik, o[0], sum(k["net"] for k in kayitlar),
             sx.median([k["net"] for k in kayitlar]), kz, 100 * kz / o[0]))


def main():
    poz = ortak.pozisyonlar(en_az_goruntu=10)
    olc = [z for z in (yol_olcumleri(p) for p in poz) if z]
    print("=" * 92)
    print("ASAMA 1a — POZISYON FILM SERIDI   ·   N=%d kapali pozisyon (>=10 anlik goruntu)" % len(olc))
    print("kaynak: pozisyon_izleme.jsonl (5 dk) · 2026-08-13 -> simdi")
    print("=" * 92)

    # ---------- 1) SONUCA GORE YOL ----------
    print("\n1) SONUCA GORE YOL — 'once ne kadar kara gecti, sonra ne oldu'")
    print("%-16s %4s %9s %9s %9s %9s %9s" % ("sebep", "N", "tepe%", "dip%", "son%", "geri ver", "tepe konum"))
    print("-" * 74)
    g = collections.defaultdict(list)
    for z in olc:
        g[z["sebep"]].append(z)
    for sebep in sorted(g, key=lambda k: -len(g[k])):
        v = g[sebep]
        print("%-16s %4d %+9.2f %+9.2f %+9.2f %9.2f %9.2f"
              % (sebep, len(v), sx.median([x["tepe_pct"] for x in v]),
                 sx.median([x["dip_pct"] for x in v]),
                 sx.median([x["son_pct"] for x in v]),
                 sx.median([x["geri_verilen"] for x in v]),
                 sx.median([x["tepe_konum"] for x in v])))

    # ---------- 2) STOP OLAN AMA KARA GECMISLER ----------
    print("\n2) STOPLA OLEN AMA ONCE KARA GECEN POZISYONLAR")
    print("   ('stop kazanan islemi oldurdu' olcusu — 2 yillik veride %15,1 idi)")
    stoplu = [z for z in olc if "STOP" in (z["sebep"] or "")]
    for esik in (0.5, 1.0, 2.0, 3.0):
        k = [z for z in stoplu if z["tepe_pct"] >= esik]
        print("   tepe >= %%%.1f once gorulmus : %3d / %3d  (%%%.0f)"
              % (esik, len(k), len(stoplu), 100 * len(k) / max(1, len(stoplu))))
    if stoplu:
        tk = [z["tepe_konum"] for z in stoplu if z["tepe_pct"] >= 1.0]
        if tk:
            print("   bunlarda tepe yolun %%%.0f'inde gorulmus (medyan)" % (100 * sx.median(tk)))

    # ---------- 3) REJIM x YON ----------
    print("\n3) REJIM x YON  (canli defter, izleme penceresi)")
    rg = collections.defaultdict(list)
    for z in olc:
        rg[(z["rejim"] or "?", z["yon"])].append(z)
    print("%-10s %-6s %4s %11s %9s %9s" % ("rejim", "yon", "N", "net $", "medyan", "kazanan"))
    print("-" * 56)
    for k in sorted(rg):
        v = rg[k]
        kz = sum(1 for x in v if x["net"] > 0)
        print("%-10s %-6s %4d %+11.2f %+9.2f %5d (%%%.0f)"
              % (k[0], k[1], len(v), sum(x["net"] for x in v),
                 sx.median([x["net"] for x in v]), kz, 100 * kz / len(v)))

    # ---------- 4) chg24 BANDI x YON ----------
    print("\n4) GIRISTEKI chg24 BANDI  (botun %20 pump kapisi bu eksende)")
    bant = [(-999, 0, "<0"), (0, 10, "0-10"), (10, 15, "10-15"),
            (15, 20, "15-20 (kapinin dibi)"), (20, 999, ">=20")]
    print("%-24s %-6s %4s %11s %9s" % ("bant", "yon", "N", "net $", "kazanan"))
    print("-" * 58)
    for lo, hi, ad in bant:
        for yon in ("SHORT", "LONG"):
            v = [z for z in olc if z["yon"] == yon and z["chg24_g"] is not None
                 and lo <= z["chg24_g"] < hi]
            if not v:
                continue
            kz = sum(1 for x in v if x["net"] > 0)
            print("%-24s %-6s %4d %+11.2f %5d (%%%.0f)"
                  % (ad, yon, len(v), sum(x["net"] for x in v), kz, 100 * kz / len(v)))

    # ---------- 5) KAR GERI VERME ----------
    print("\n5) KAR GERI VERME  (pnl-tepe-raporu N=17 idi, burada N=%d)" % len(olc))
    kara = [z for z in olc if z["tepe_pct"] > 0]
    print("   tepede artida olan pozisyon : %d / %d" % (len(kara), len(olc)))
    if kara:
        gv = [z["geri_verilen"] for z in kara]
        print("   geri verilen (puan) medyan  : %.2f  ·  ortalama %.2f" % (sx.median(gv), sx.mean(gv)))
        oran = [z["geri_verilen"] / z["tepe_pct"] for z in kara if z["tepe_pct"] > 0.1]
        if oran:
            print("   tepenin ne kadari geri verildi: medyan %%%.0f" % (100 * sx.median(oran)))
    print("\nbot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
