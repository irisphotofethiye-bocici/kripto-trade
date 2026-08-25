#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CIKIS FIKIRLERI — SIZINTISIZ KIYAS KOLUYLA YENIDEN.

ONARILAN HATA (2026-08-21'de bulundu, 08-25'te duzeltiliyor):
   32/33/34'un "rastgele cikis" kolu soyleydi:
       aday = range(2, len(pnl) - 1)
       rast = pnl[random.choice(aday)] - pnl[-1]
   `len(pnl)` POZISYONUN OMRUDUR. Yani rastgele kol, pozisyonun kac bar
   yasayacagini BILEREK cikis secti: kisa omurluda erken, uzun omurluda gec.
   Gercek zamanda bu bilgi YOK. Kiyas olcutu sisirilmisti ve "dokuz cikis
   fikri de rastgeleyi yenemedi" hukmu bu bozuk olcute dayaniyordu.

SIZINTISIZ TASARIM
   1) SABIT UFUK H: her pozisyon H bara KIRPILIR. H'den once kapanan pozisyon
      ELENMEZ, kapanis degerinde SABITLENIR (hayatta-kalma yanliligi onlenir).
   2) BELLEKSIZ CIKIS: her barda p olasilikla cik (geometrik). Omur bilgisi
      kullanmaz, gercek zamanda uygulanabilir.
   3) ESLESMIS TUTMA: p, kuralin ORTALAMA cikis barina esitlenir. Boylece
      "erken cikan kazanir" yapayligi kolun lehine calismaz.
   4) SABIT BAR: ayrica butun pozisyonlarda AYNI j'de cikan kol (ongorusuz taban).

OLCU: cikis anindaki PnL eksi UFUK SONUNDAKI PnL (puan). Pozitif = cikmak iyiydi.
   Referans her iki kolda AYNI (pnl[H-1]) -> kiyas adil.

HUKUM YAZILMAZ. SALT OKUMA.
"""
# [2026-08-25] cp1254 TUZAGI — kalici kapatma.
#   Windows konsolu cp1254; print() icindeki emoji/varyasyon secici CIKTI
#   YONLENDIRILDIGINDE UnicodeEncodeError firlatiyor ve betik COKUYOR.
#   Bu sinif bu projede BES kez isirdi. Emoji ayiklamak yerine stdout
#   guvenli hale getirilir; hata sinifi disiplinle degil ARACLA kapanir.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, sys, random, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
PROJE = os.path.dirname(SCRATCH)
sys.path.insert(0, HERE)
sys.path.insert(0, PROJE)
import ortak                                                    # noqa: E402
import testbot                                                  # noqa: E402
import evren                                                    # noqa: E402

random.seed(4224)
evren.para_rejim = lambda *a, **k: {"durum": "NOTR"}
testbot.telegram_gonder = lambda *a, **k: None
testbot.toast_gonder = lambda *a, **k: None
testbot._append_jsonl = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("DISKE YAZIM"))
testbot._save_state = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("DISKE YAZIM"))

H = 48                # ufuk: 48 bar x 5 dk = 4 saat
TEKRAR = 200          # belleksiz kol icin tekrar sayisi (Monte Carlo)
TERS = {"LONG": "SHORT", "SHORT": "LONG"}


def doldur(pnl, h):
    """h bara kirp; kisa ise SON DEGERDE sabitle (kapali pozisyon ilerlemez)."""
    w = pnl[:h]
    if len(w) < h:
        w = w + [w[-1]] * (h - len(w))
    return w


def hazirla():
    out = []
    for p in ortak.pozisyonlar(en_az_goruntu=6, zengin=False):
        s = p["seri"]
        pnl = [g.get("pnl_pct") for g in s]
        if any(x is None for x in pnl) or len(pnl) < 6:
            continue
        son = p["sonuc"] or {}
        out.append({"sym": p["sym"], "yon": p["yon"], "seri": s,
                    "pnl": doldur(pnl, H), "ham_uzunluk": len(pnl),
                    "rejim": son.get("rejim_giriste") or "NOTR",
                    "smart_g": son.get("smart_giriste")})
    return out


def karar_ve_veto(g, rejim):
    r = {"score": g.get("score"), "stage": g.get("stage"), "chg24": g.get("chg24"),
         "pos": g.get("pos"), "funding": g.get("funding"), "oi24": g.get("oi24"),
         "price": g.get("fiyat"), "ma50_mesafe": g.get("ma50_mesafe"),
         "dip_yakit": g.get("dip_yakit"), "smart": g.get("smart"), "taker": g.get("taker")}
    if r["score"] is None or r["stage"] is None:
        return None, []
    veto = []
    try:
        k = testbot.karar_yon(rejim, r, {"smart": g.get("smart"), "taker": g.get("taker")},
                              False, veto_out=veto, para_cikis=False,
                              btc_pay=None, para_durgun=False)
    except Exception:
        return None, []
    return (k[0] if k else None), [v.get("kategori") for v in veto]


def belleksiz(pnl, p, rng):
    """Her barda p olasilikla cik. Omur bilgisi KULLANMAZ. -> cikis indeksi."""
    for i in range(2, H - 1):
        if rng.random() < p:
            return i
    return H - 2


def p_coz(hedef_bar):
    """Ortalama cikis bari ~hedef olacak p (kesilmis geometrik, kabaca)."""
    if hedef_bar <= 2:
        return 0.9
    return min(0.9, max(1e-4, 1.0 / max(1.0, hedef_bar - 2.0)))


def dene(P, ad, bulucu, kararlar_hepsi):
    kural, ilk = [], []
    havuz = []
    for idx, p in enumerate(P):
        i = bulucu(p, kararlar_hepsi[idx][0], kararlar_hepsi[idx][1])
        if i is None or i < 2 or i >= H - 1:
            continue
        kural.append(p["pnl"][i] - p["pnl"][H - 1])
        ilk.append(i)
        havuz.append(p)
    if len(kural) < 15:
        print("  %-26s N=%-3d  yetersiz" % (ad, len(kural)))
        return
    ort_bar = sx.mean(ilk)
    pp = p_coz(ort_bar)
    # BELLEKSIZ kol — ayni pozisyonlar, ayni ufuk, TEKRAR kez
    rng = random.Random(99)
    bk = []
    for _ in range(TEKRAR):
        v = [pz["pnl"][belleksiz(pz["pnl"], pp, rng)] - pz["pnl"][H - 1] for pz in havuz]
        bk.append(sx.median(v))
    # SABIT BAR kol — herkes ayni j'de (ongorusuz taban)
    j = int(round(ort_bar))
    sb = sx.median([pz["pnl"][j] - pz["pnl"][H - 1] for pz in havuz])
    mk = sx.median(kural)
    mb = sx.mean(bk)
    sd = sx.pstdev(bk) if len(bk) > 1 else 0.0
    z = (mk - mb) / sd if sd > 0 else float("nan")
    print("  %-26s N=%-3d bar%5.1f  kural %+7.3f  belleksiz %+7.3f (sd %.3f)  "
          "sabit-bar %+7.3f  FARK %+7.3f  z %+5.2f"
          % (ad, len(kural), ort_bar, mk, mb, sd, sb, mk - mb, z))


if __name__ == "__main__":
    P = hazirla()
    print("CIKIS FIKIRLERI — SIZINTISIZ KIYAS  (ufuk %d bar = %d dk)" % (H, H * 5))
    print("%d pozisyon · kapanmis olanlar kapanis degerinde SABITLENDI" % len(P))
    kisa = sum(1 for p in P if p["ham_uzunluk"] < H)
    print("%d pozisyon ufuktan KISA (dolduruldu) · %d tam" % (kisa, len(P) - kisa))
    print("olculen: cikis PnL eksi UFUK SONU PnL (puan) · pozitif = cikmak iyiydi")
    print("z = (kural - belleksiz) / belleksiz_sd   |z| >= 2 anlamli\n")

    kh = []
    for p in P:
        ks, vs = [], []
        for g in p["seri"][:H]:
            k, v = karar_ve_veto(g, p["rejim"])
            ks.append(k)
            vs.append(v)
        while len(ks) < H:
            ks.append(None)
            vs.append([])
        kh.append((ks, vs))

    print("FIKIR 1 — VETO CIKISI")
    for kat in ("blowoff", "taker_soguma", "long_veto"):
        dene(P, kat, lambda p, k, v, _k=kat: next(
            (i for i in range(2, len(v)) if _k in v[i]), None), kh)
    dene(P, "herhangi bir veto", lambda p, k, v: next(
        (i for i in range(2, len(v)) if v[i]), None), kh)

    print("\nFIKIR 2 — ARTIK ADAY DEGIL / TERS ADAY")
    dene(P, "artik bu yonde almazdi", lambda p, k, v: next(
        (i for i in range(2, len(k)) if k[i] != p["yon"]), None), kh)
    dene(P, "ters yonde aday", lambda p, k, v: next(
        (i for i in range(2, len(k)) if k[i] == TERS[p["yon"]]), None), kh)
    dene(P, "ters aday 2 bar ust uste", lambda p, k, v: next(
        (i for i in range(3, len(k)) if k[i] == TERS[p["yon"]] and k[i-1] == TERS[p["yon"]]), None), kh)

    print("\nFIKIR 3 — SMART DONUSU")
    dene(P, "smart giristen ayristi", lambda p, k, v: next(
        (i for i in range(2, min(H, len(p["seri"])))
         if p["smart_g"] and p["seri"][i].get("smart")
         and p["seri"][i].get("smart") != p["smart_g"]), None), kh)
    dene(P, "smart POZUN TERSINE", lambda p, k, v: next(
        (i for i in range(2, min(H, len(p["seri"])))
         if p["seri"][i].get("smart") == TERS[p["yon"]]), None), kh)

    print("\nESKI (SIZINTILI) OLCUT: rastgele bar, pozisyonun OMRU icinden secilirdi.")
    print("HUKUM YAZILMADI. diske yazim: YOK (stub'li)")
