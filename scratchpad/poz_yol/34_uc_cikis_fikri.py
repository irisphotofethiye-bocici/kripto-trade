#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UC CIKIS FIKRI — botun kendi mantigindan turetilen cikis kurallari.

33_hala_alir_miydi.py: "artik giris adayi degil" cikisi RASTGELEDEN 0,93 puan
KOTU cikti. Sebep: giris kapisi bir KURULUM kapisi; pozisyon calisinca kurulum
bozuluyor -> "artik aday degil" cogu zaman "islem tuttu" demek.

BURADA UC AYRI FIKIR, hepsi bizim veriyle:
  1) VETO CIKISI    — blowoff / taker_soguma / long_veto tetiklenince cik
  2) TERS ADAY      — bot ayni coini TERS yonde almaya baslarsa cik
  3) SMART DONUSU   — smart_giriste ile anlik smart ayrisirsa cik

HER BIRINDE ZORUNLU KONTROL: ayni pozisyonlardan AYNI SAYIDA rastgele cikis.
(31_kesinlik.py'de kontrol yoktu ve tetikler sahte pozitif gorunmustu.)

⚠️ evren.para_rejim STUB (ag yok) · btc_pay=None -> kapi GEVSER yonde.
HUKUM YAZILMAZ. SALT OKUMA.
"""
import os, sys, statistics as sx, collections, random

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
PROJE = os.path.dirname(SCRATCH)
sys.path.insert(0, HERE)
sys.path.insert(0, PROJE)
import ortak                                                    # noqa: E402
import testbot                                                  # noqa: E402
import evren                                                    # noqa: E402

random.seed(29)
evren.para_rejim = lambda *a, **k: {"durum": "NOTR"}
testbot.telegram_gonder = lambda *a, **k: None
testbot.toast_gonder = lambda *a, **k: None
testbot._append_jsonl = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("DISKE YAZIM"))
testbot._save_state = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("DISKE YAZIM"))

TERS = {"LONG": "SHORT", "SHORT": "LONG"}


def karar_ve_veto(g, rejim):
    r = {"score": g.get("score"), "stage": g.get("stage"), "chg24": g.get("chg24"),
         "pos": g.get("pos"), "funding": g.get("funding"), "oi24": g.get("oi24"),
         "price": g.get("fiyat"), "ma50_mesafe": g.get("ma50_mesafe"),
         "dip_yakit": g.get("dip_yakit"), "smart": g.get("smart"), "taker": g.get("taker")}
    if r["score"] is None or r["stage"] is None:
        return None, []
    pillar = {"smart": g.get("smart"), "taker": g.get("taker")}
    veto = []
    try:
        k = testbot.karar_yon(rejim, r, pillar, False, veto_out=veto,
                              para_cikis=False, btc_pay=None, para_durgun=False)
    except Exception:
        return None, []
    return (k[0] if k else None), [v.get("kategori") for v in veto]


def hazirla():
    out = []
    for p in ortak.pozisyonlar(en_az_goruntu=12, zengin=False):
        s = p["seri"]
        pnl = [g.get("pnl_pct") for g in s]
        if any(x is None for x in pnl):
            continue
        son = p["sonuc"] or {}
        out.append({"sym": p["sym"], "yon": p["yon"], "seri": s, "pnl": pnl,
                    "rejim": son.get("rejim_giriste") or "NOTR",
                    "smart_g": son.get("smart_giriste"), "sonuc": son})
    return out


def dene(P, ad, bulucu):
    """bulucu(p, kararlar, vetolar) -> ilk cikis indeksi | None"""
    kural, rast = [], []
    bulunan = 0
    ilk = []
    for p in P:
        s, pnl = p["seri"], p["pnl"]
        kararlar, vetolar = [], []
        for g in s:
            k, v = karar_ve_veto(g, p["rejim"])
            kararlar.append(k)
            vetolar.append(v)
        i = bulucu(p, kararlar, vetolar)
        if i is None or i >= len(pnl) - 1 or i < 2:
            continue
        bulunan += 1
        ilk.append(i)
        kural.append(pnl[i] - pnl[-1])
        aday = list(range(2, len(pnl) - 1))
        rast.append(pnl[random.choice(aday)] - pnl[-1])
    if bulunan < 15:
        print("  %-24s N=%-3d  yetersiz" % (ad, bulunan))
        return
    mk, mr = sx.median(kural), sx.median(rast)
    print("  %-24s N=%-3d  ilk-bar medyan %3d (%3d dk)  kural %+7.3f  rastgele %+7.3f  FARK %+7.3f"
          % (ad, bulunan, sx.median(ilk), sx.median(ilk) * 5, mk, mr, mk - mr))


if __name__ == "__main__":
    P = hazirla()
    print("UC CIKIS FIKRI — %d pozisyon" % len(P))
    print("olculen: cikis anindaki PnL eksi pozisyonun GERCEK sonu (puan)")
    print("pozitif = cikmak iyiydi · FARK = kural eksi rastgele\n")

    print("FIKIR 1 — VETO CIKISI")
    for kat in ("blowoff", "taker_soguma", "long_veto"):
        dene(P, kat, lambda p, k, v, _k=kat: next(
            (i for i in range(2, len(v)) if _k in v[i]), None))
    dene(P, "herhangi bir veto", lambda p, k, v: next(
        (i for i in range(2, len(v)) if v[i]), None))

    print("\nFIKIR 2 — TERS ADAY (bot ayni coini TERS yonde alacak)")
    dene(P, "ters yonde aday", lambda p, k, v: next(
        (i for i in range(2, len(k)) if k[i] == TERS[p["yon"]]), None))
    dene(P, "ters aday 2 bar ust uste", lambda p, k, v: next(
        (i for i in range(3, len(k)) if k[i] == TERS[p["yon"]] and k[i - 1] == TERS[p["yon"]]), None))

    print("\nFIKIR 3 — SMART DONUSU")
    dene(P, "smart giristen ayristi", lambda p, k, v: next(
        (i for i in range(2, len(p["seri"]))
         if p["smart_g"] and p["seri"][i].get("smart")
         and p["seri"][i].get("smart") != p["smart_g"]), None))
    dene(P, "smart POZ YONUNE dondu", lambda p, k, v: next(
        (i for i in range(2, len(p["seri"]))
         if p["seri"][i].get("smart") == p["yon"]), None))
    dene(P, "smart POZUN TERSINE", lambda p, k, v: next(
        (i for i in range(2, len(p["seri"]))
         if p["seri"][i].get("smart") == TERS[p["yon"]]), None))

    print("\nKIYAS — 33_hala_alir_miydi.py: 'artik aday degil' FARK -0,928")
    print("HUKUM YAZILMADI. diske yazim: YOK (stub'li)")
