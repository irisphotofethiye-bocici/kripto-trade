#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OTOPSI-4 DOGRULAMA (2026-08-10) — "risk-once boyutlandirma onarimi" fiilen ne degistirdi?

ON-KAYIT (sonuca bakmadan yazildi):
  Hipotez: onarim sonrasi DOLAR RISKI stop mesafesinden BAGIMSIZLASIR.
  Olcut  : kapanan islemlerin turetilmis dolar riskinin ORANI (maks/min).
           Eski kodda 7x civari (fikir defteri OTOPSI-4). Onarilmis formulde
           beklenen: ~1.5x (yalnizca marjin_pct %8-12 bandindan ve kaldirac
           tavanindan gelen fark; stop mesafesi katkisi SIFIR).
  Yontem : gercek kapanan islemlerin KENDI girdileriyle (skor, stop mesafesi,
           o anki equity) iki formul de yeniden hesaplanir. Yeni fiyat/veri
           CEKILMEZ, eslik-arama YOK, tek varyant.

SINIR: equity izi islem defterinde yok -> her islem icin o anki equity,
       equity jsonl'inden islem kapanis ts'sine gore alinir (giris equity'sine
       en yakin kayit). Bu bir YAKLASIM; dolar riski oranini ~%5'ten fazla
       etkilemez cunku her iki formul de AYNI equity'yi kullanir.
"""
import json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # proje koku
sys.path.insert(0, HERE)
import testbot  # noqa: E402


def oku(ad):
    p = os.path.join(HERE, ad)
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def equity_o_an(eq, ts):
    """Kapanis ts'inden ONCEKI son equity kaydi (girisin equity'sine en yakin vekil)."""
    onceki = [e for e in eq if e["ts"] <= ts]
    return (onceki[-1] if onceki else eq[0])["equity"]


def _kirp(stop_frac, kald):
    """kaldirac_guvenlik_kirp — stop likidasyondan ONCE tetiklensin (iki formulde de var)."""
    return min(kald, int(0.95 / (stop_frac * 1.3)))


def eski_formul(equity, skor, stop_frac, smart_hiz, smart_karsi):
    """[HATA] marjin ve kaldirac YALNIZ skordan; risk sonucta olusur, sadece tavan kirpilir."""
    kald = _kirp(stop_frac, testbot.kaldirac_hesapla(skor, smart_hiz))
    if kald < 2:
        return None, None, None
    marjin = equity * testbot.marjin_pct_hesapla(skor)
    if smart_karsi:
        marjin /= 2.0            # eski kodda smart KARSI yonde MARJIN yarilaniyordu (NOTR haric)
    notional = marjin * kald
    risk = stop_frac * notional
    tavan = equity * 0.05
    if risk > tavan:
        notional *= tavan / risk
        risk = tavan
    return risk, kald, notional


def yeni_formul(equity, skor, stop_frac, smart_hiz, smart_karsi):
    """[ONARIM] notional = hedef_risk / stop_frac; kaldirac bir ARAC, girdi degil."""
    hedef = equity * 0.05
    if smart_karsi:
        hedef /= 2.0             # yeni kodda RISK yarilanir (NOTR haric)
    marjin = equity * testbot.marjin_pct_hesapla(skor)
    kald_gerekli = (hedef / stop_frac) / marjin
    kald = _kirp(stop_frac, int(round(max(3.0, min(10.0, kald_gerekli)))))
    if kald < 2:
        return None, None, None                    # bot bu islemi ACMAZDI
    notional = marjin * kald
    risk = stop_frac * notional
    if risk > hedef:
        notional *= hedef / risk
        risk = hedef
    return risk, kald, notional


def main():
    islemler = [t for t in oku("testbot_islemler.jsonl") if not t.get("kismi")]
    eq = oku("testbot_equity.jsonl")

    print("OTOPSI-4 DOGRULAMA — kapanan gercek islemler, iki formul yan yana")
    print(f"{'sym':8} {'skor':>5} {'stop%':>6} {'equity':>8} | "
          f"{'ESKI risk':>9} {'k':>3} | {'YENI risk':>9} {'k':>3} | {'risk%':>6}")
    print("-" * 78)
    eski_r, yeni_r = [], []
    for t in islemler:
        risk_gercek = abs(t["sonuc_usdt"] / t["r"]) if t.get("r") else None
        if not risk_gercek or not t.get("notional"):
            continue
        stop_frac = risk_gercek / t["notional"]
        skor = t.get("skor_giriste") or 50.0
        sm = t.get("smart_giriste")
        smart_hiz = (sm == t["yon"])
        smart_karsi = (sm not in (None, "NOTR")) and not smart_hiz
        e = equity_o_an(eq, t["ts"])
        er, ek, _ = eski_formul(e, skor, stop_frac, smart_hiz, smart_karsi)
        yr, yk, _ = yeni_formul(e, skor, stop_frac, smart_hiz, smart_karsi)
        if er:
            eski_r.append(er)
        if yr:
            yeni_r.append(yr)
        print(f"{t['sym']:8} {skor:5.1f} {stop_frac*100:6.2f} {e:8.0f} | " +
              (f"{er:9.0f} {ek:3d} | " if er else f"{'ACMAZDI':>9} {'-':>3} | ") +
              (f"{yr:9.0f} {yk:3d} | {yr/e*100:5.2f}%" if yr else f"{'ACMAZDI':>9} {'-':>3} |"))
    print("-" * 78)
    print(f"ESKI  dolar riski: min ${min(eski_r):.0f}  maks ${max(eski_r):.0f}  "
          f"-> ORAN {max(eski_r)/min(eski_r):.1f}x")
    print(f"YENI  dolar riski: min ${min(yeni_r):.0f}  maks ${max(yeni_r):.0f}  "
          f"-> ORAN {max(yeni_r)/min(yeni_r):.1f}x")
    print("\nNOT: 'risk%' = riskin o anki equity'ye orani. Hedef %5 (smart karsi yonde %2.5).")
    print("Hedefin ALTINDA kalan satirlar = kaldirac tavani/guvenlik kirpmasi (guvenli yon).")


if __name__ == "__main__":
    main()
