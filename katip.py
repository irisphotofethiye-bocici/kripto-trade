#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KATIP — tahmin defteri cozumleyici (Faz 8 cekirdegi, 2026-07-02; m9 duzeltmesi).
LLM YOK. Deftere YAZMAZ (CEO yazar) — sadece okur, anlik fiyatla karsilastirir, raporlar.

Ne yapar:
  1. ACIK tahminler + izleme_listesi (kripto_portfoy.json): anlik fiyat vs giris/stop/tp1
     -> yon-PnL, R (risk katsayisi), STOP_IHLAL / TP1_ULASTI / ACIK onerisi.
  2. KAPANMIS kayitlar (kripto_gecmis.json + portfoyde sonucu olanlar): hit-rate.
     Yapilandirilmis 'sonuc_durum' varsa onu sayar; eski serbest-metin 'sonuc' icin
     kaba siniflama (ISABET/YANLIS kelimeleri). Belirsizler ayri sayilir, UYDURULMAZ.
Kullanim: python katip.py
"""
import json, os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SPOT = "https://api.binance.com"
FAPI = "https://fapi.binance.com"

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")


def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "katip/1.0"})
    return json.load(urllib.request.urlopen(req, timeout=15))


def fiyat(sym):
    for u in (f"{SPOT}/api/v3/ticker/price?symbol={sym}USDT",
              f"{FAPI}/fapi/v1/ticker/price?symbol={sym}USDT"):
        try:
            return float(get(u)["price"])
        except Exception:
            continue
    return None


def f(x):
    try:
        return float(x)
    except Exception:
        return None


def acik_rapor(defter):
    print("## ACIK TAHMINLER")
    acik = [t for t in defter.get("tahminler", [])
            if t.get("sonuc_durum", "ACIK") == "ACIK" and not (t.get("sonuc") and "ISABET" in str(t.get("sonuc")).upper() and "izlemede" not in str(t.get("sonuc")).lower())]
    if not acik:
        print("  (yok)")
    for t in acik:
        sym, yon = t.get("token", "?"), (t.get("yon") or "?")[:1].upper()
        px = fiyat(sym)
        giris, stop, tp1 = f(t.get("giris")), f(t.get("stop")), f(t.get("tp1"))
        satir = f"  #{t.get('no','?')} {sym:8} yon={t.get('yon','?')}"
        if px is None or giris is None:
            print(satir + f" | fiyat/giris sayisal degil -> elle degerlendir (giris={t.get('giris')})")
            continue
        sgn = 1 if yon == "L" else (-1 if yon == "S" else 0)
        pnl = (px / giris - 1) * 100 * sgn
        satir += f" | giris={giris} anlik={px} yon-PnL={pnl:+.1f}%"
        if stop:
            risk = abs(giris - stop) / giris * 100
            if risk > 0:
                satir += f" | R={pnl/risk:+.2f}"
            ihlal = (px <= stop) if yon == "L" else (px >= stop)
            if ihlal:
                satir += " | !! STOP_IHLAL (sonuc_durum=YANLIS yazilmali)"
        if tp1:
            ulasti = (px >= tp1) if yon == "L" else (px <= tp1)
            if ulasti:
                satir += " | ** TP1_ULASTI (sonuc_durum=ISABET yazilmali)"
        print(satir)

    print("\n## IZLEME LISTESI (tetik bekleyenler)")
    for z in defter.get("izleme_listesi", []):
        sym = z.get("sembol", "?")
        px, eklemede = fiyat(sym), f(z.get("fiyat_eklemede"))
        if px and eklemede:
            print(f"  {sym:8} {z.get('yon','')[:28]:28} eklemede={eklemede} anlik={px} ({(px/eklemede-1)*100:+.1f}%)")
        else:
            print(f"  {sym:8} {z.get('yon','')[:28]:28} (fiyat alinamadi)")


def kapali_rapor(defter, gecmis):
    kayitlar = list(gecmis.get("kapanan_tahminler", []))
    kayitlar += [t for t in defter.get("tahminler", []) if t.get("sonuc_durum") in ("ISABET", "YANLIS", "KISMEN")]
    isabet = yanlis = kismen = belirsiz = 0
    rler = []
    for t in kayitlar:
        sd = t.get("sonuc_durum")
        if sd == "ISABET":
            isabet += 1
        elif sd == "YANLIS":
            yanlis += 1
        elif sd == "KISMEN":
            kismen += 1
        else:  # eski serbest-metin siniflama
            s = str(t.get("sonuc") or "").upper()
            if "ISABET" in s and "YANLIS" not in s:
                isabet += 1
            elif "YANLIS" in s and "ISABET" not in s:
                yanlis += 1
            elif "YON DOGRU" in s or ("ISABET" in s and "YANLIS" in s):
                kismen += 1
            else:
                belirsiz += 1
        gr = f(t.get("gerceklesen_r"))
        if gr is not None:
            rler.append(gr)
    n = isabet + yanlis + kismen
    print("\n## KAPANMIS TAHMIN KARNESI")
    print(f"  Toplam siniflanan: {n} (+{belirsiz} belirsiz/elle bak)")
    if n:
        print(f"  ISABET {isabet} | YANLIS {yanlis} | KISMEN {kismen} -> hit-rate %{isabet/n*100:.0f} (kismen haric)")
    if rler:
        print(f"  Ortalama gerceklesen R: {sum(rler)/len(rler):+.2f} (n={len(rler)})")
    else:
        print("  gerceklesen_r alani henuz dolmamis (sema v2 yeni kayitlarla dolacak)")
    print("  NOT: eski kayitlar serbest-metinden KABACA siniflandi; kesin karne v2 alanlariyla olusur.")


def main():
    defter = json.load(open(os.path.join(HERE, "kripto_portfoy.json"), encoding="utf-8"))
    try:
        gecmis = json.load(open(os.path.join(HERE, "kripto_gecmis.json"), encoding="utf-8"))
    except Exception:
        gecmis = {}
    print("=== KATIP (okur + raporlar; deftere yazmaz) ===")
    acik_rapor(defter)
    kapali_rapor(defter, gecmis)


if __name__ == "__main__":
    main()
