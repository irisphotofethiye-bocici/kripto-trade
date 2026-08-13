#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ERKEN MUDAHALE OLCUMU (2026-08-13) — "ilk N dakikadaki durum sonucu haber veriyor mu?"

KULLANICI SORUSU: "pozun anlik durumunu gecmise bakip gorebiliriz artik; ne gibi
    durumlarda yukselmis veya dusmus, mudahale edilebilir mi diye".

DIKKAT — ILERI BAKMA TUZAGI: "kazananlar %91.7 sure artida kaldi" bulgusu pozisyonun
    TUM omrunden hesaplandi. Kazanan islem zaten kazandigi ICIN cogu zaman artidadir;
    bu bir tahmin degil, sonucun yeniden ifadesi. Karar verilebilir tek soru sudur:
    GIRISTEN SONRAKI ILK N DAKIKADA gorulen sey, sonucu ONCEDEN haber veriyor mu?

    Bu betik yalnizca ilk N dakikaya bakar. Kontrol noktasindan SONRAKI hicbir bilgi
    kullanilmaz.

OLCULEN
  1) Kontrol noktasindaki duruma gore sonuc dagilimi (haber verici mi?)
  2) "N dakikada artida degilse KAPAT" kuralinin 44 pozisyonda ne yapacagi
  3) Kural, kapanis maliyeti (%0.13) dahil kasaya ne katardi

VERI: pozisyon_ozet.jsonl'deki 44 pozisyonun giris/cikis pencereleri + Binance 1m mumlar.
Yollar scratchpad/poz_yollari.json'a onbelleklenir (ikinci kosuda ag cagrisi yok).
Salt-okunur; bota ve defterlere dokunmaz.
"""
import json, os, sys, time, datetime, statistics as stx

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURA)
sys.path.insert(0, KOK)
import testbot

OZET = os.path.join(KOK, "pozisyon_ozet.jsonl")
ONBELLEK = os.path.join(BURA, "poz_yollari.json")
KONTROL_NOKTALARI = (15, 30, 60, 120)
MALIYET = 0.13          # tam tur islem maliyeti (%), olcum_ortak ile ayni

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def yollar_yukle(pozlar):
    try:
        onb = json.load(open(ONBELLEK, encoding="utf-8"))
    except Exception:
        onb = {}
    eksik = [p for p in pozlar if str(p["id"]) not in onb]
    if eksik:
        print(f"1 dakikalik yol cekiliyor: {len(eksik)} pozisyon...", flush=True)
        for p in eksik:
            try:
                bas = testbot.to_ms(p["giris_ts"])
                son = testbot.to_ms(p["sonuc_ts"])
                b, t = [], bas
                while t < son:
                    d = testbot.klines_since(p["sym"], "1m", t, limit=1000)
                    if not d:
                        break
                    d = [x for x in d if x["t"] <= son]
                    b += d
                    if len(d) < 900:
                        break
                    t = d[-1]["t"] + 60000
                    time.sleep(0.15)
                onb[str(p["id"])] = [[x["t"], x["o"], x["h"], x["l"], x["c"]] for x in b]
                time.sleep(0.15)
            except Exception as e:
                print(f"  {p['sym']}: {str(e)[:50]}")
        json.dump(onb, open(ONBELLEK, "w", encoding="utf-8"))
    return onb


def pnl_pct(giris, fiyat, yon):
    return (fiyat - giris) / giris * 100 * (1 if yon == "LONG" else -1)


def main():
    pozlar = [json.loads(l) for l in open(OZET, encoding="utf-8") if l.strip()]
    pozlar = [p for p in pozlar if p.get("sonuc_ts") and p.get("giris_ts")]
    onb = yollar_yukle(pozlar)
    # GERCEK notional: islem defterinden id ile. Kismi kar alinmis pozisyonlarda
    # kayitlar pozisyonu boler, o yuzden id basina TOPLANIR.
    notional = {}
    try:
        for l in open(testbot.ISLEMLERF, encoding="utf-8"):
            if not l.strip():
                continue
            r = json.loads(l)
            notional[r["id"]] = notional.get(r["id"], 0.0) + (r.get("notional") or 0.0)
    except Exception:
        pass

    print("\n" + "=" * 104)
    print("ERKEN MUDAHALE — ilk N dakikadaki durum sonucu HABER VERIYOR MU?")
    print("=" * 104)
    print(f"{len(pozlar)} kapanmis pozisyon · kontrol noktasindan SONRAKI bilgi KULLANILMADI\n")

    kayit = []
    for p in pozlar:
        yol = onb.get(str(p["id"])) or []
        if not yol:
            continue
        g, yon = p["giris"], p["yon"]
        satir = {"sym": p["sym"], "id": p["id"], "kapi": p.get("kapi"),
                 "sonuc": p.get("sonuc_usdt") or 0.0, "sebep": p.get("sonuc_sebep"),
                 "omur": len(yol), "notional": notional.get(p["id"])}
        for n in KONTROL_NOKTALARI:
            dilim = yol[:n]
            if len(dilim) < min(n, 5):
                satir[f"d{n}"] = None
                continue
            kap = pnl_pct(g, dilim[-1][4], yon)
            leh = [pnl_pct(g, (x[2] if yon == "LONG" else x[3]), yon) for x in dilim]
            satir[f"d{n}"] = round(kap, 3)
            satir[f"mfe{n}"] = round(max(leh), 3)
        kayit.append(satir)

    print("### 1) KONTROL NOKTASINDA ARTIDA MI? -> SONUC")
    print(f"{'nokta':10}{'durum':14}{'N':>5}{'kazanan':>9}{'ort sonuc $':>13}{'medyan $':>11}")
    print("-" * 104)
    for n in KONTROL_NOKTALARI:
        v = [k for k in kayit if k.get(f"d{n}") is not None]
        if len(v) < 10:
            continue
        for ad, sec in (("artida", [k for k in v if k[f"d{n}"] > 0]),
                        ("eksinde", [k for k in v if k[f"d{n}"] <= 0])):
            if not sec:
                continue
            kaz = [k for k in sec if k["sonuc"] > 0]
            print(f"{str(n)+' dk':10}{ad:14}{len(sec):5d}{len(kaz)/len(sec)*100:8.0f}%"
                  f"{stx.mean([k['sonuc'] for k in sec]):13.2f}"
                  f"{stx.median([k['sonuc'] for k in sec]):11.2f}")
        print("-" * 104)

    print("\n### 2) KURAL: 'N dakikada artida DEGILSE kapat' — 44 pozisyonda ne olurdu?")
    print("Dolar hesabi GERCEK notional ile: kontrol noktasindaki yuzde x pozisyonun notional'i.")
    print(f"{'kural':16}{'kapanan':>9}{'GERCEK $':>12}{'KURAL $':>12}{'FARK':>11}"
          f"{'kesilen zarar':>15}{'kacan kar':>12}")
    print("-" * 104)
    for n in KONTROL_NOKTALARI:
        v = [k for k in kayit if k.get(f"d{n}") is not None and k["omur"] > n and k.get("notional")]
        if len(v) < 10:
            continue
        gercek = kural = 0.0
        kesilen = kacan = 0.0
        mudahale = 0
        for k in v:
            gercek += k["sonuc"]
            if k[f"d{n}"] <= 0:                       # kural devreye girer
                mudahale += 1
                # kontrol noktasindaki fiyattan cikis; MALIYET zaten pozisyonun kendi
                # cikisinda da odenecekti, o yuzden EK maliyet yok (cikis erkene alindi)
                d = k[f"d{n}"] / 100.0 * k["notional"]
                kural += d
                fark = d - k["sonuc"]
                if fark > 0:
                    kesilen += fark
                else:
                    kacan += -fark
            else:
                kural += k["sonuc"]
        print(f"{str(n)+' dakika':16}{mudahale:9d}{gercek:12.2f}{kural:12.2f}"
              f"{kural-gercek:+11.2f}{kesilen:15.2f}{kacan:12.2f}")
    print("\n  'kesilen zarar' = erken cikisin ONLEDIGI kayip · 'kacan kar' = erken cikisin")
    print("  KAYBETTIRDIGI kar (o an eksideyken sonra donup kazanan islemler)")

    print("\n### 4) HABER VERICILIK — ilk N dakikadaki MFE sonucu ayiriyor mu?")
    print(f"{'nokta':10}{'MFE esigi':14}{'N':>5}{'kazanan':>9}{'ort sonuc $':>13}")
    print("-" * 104)
    for n in KONTROL_NOKTALARI:
        v = [k for k in kayit if k.get(f"mfe{n}") is not None]
        if len(v) < 10:
            continue
        for ad, sec in ((">= %1 gordu", [k for k in v if k[f"mfe{n}"] >= 1.0]),
                        ("< %1", [k for k in v if k[f"mfe{n}"] < 1.0])):
            if not sec:
                continue
            kaz = [k for k in sec if k["sonuc"] > 0]
            print(f"{str(n)+' dk':10}{ad:14}{len(sec):5d}{len(kaz)/len(sec)*100:8.0f}%"
                  f"{stx.mean([k['sonuc'] for k in sec]):13.2f}")
        print("-" * 104)


if __name__ == "__main__":
    main()
