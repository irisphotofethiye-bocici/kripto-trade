#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACIK POZISYONLAR ICIN TABAN-ORAN TAHMINI

Kullanici: "su anda acik olan pozlar uzerinden bakip bir tahmin uret"

🔴 BU BIR KANAAT DEGIL. Yordam:
  1) Tarihsel populasyonda (radar_archive · score>=30 · LONG · A0) her giris icin
     stopa ve hedefe olan mesafe ATR CINSINDEN hesaplanir
  2) Bu iki mesafeye gore KOVALARA ayrilir; her kovada gercek sonuc dagilimi
     (STOP / HEDEF / ZAMAN) sayilir  -> AMPIRIK taban oran
  3) Acik pozisyonun SU ANKI mesafeleri ayni kovaya dusurulur, kovanin
     dagilimi tahmin olarak okunur

⚠️ YAKLASIKLIK ve ACIKCA YAZILIYOR: acik pozisyon "hayatta kalmis" bir
   pozisyondur; taban oran ise GIRIS anindan sayiyor. Yol Markov degil.
   Tahmin bu yuzden KABA — nokta tahmin degil, kova frekansi.

SALT-OKUNUR. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, sys, time, collections, statistics as stx, datetime as dt
import urllib.request
import importlib.util as il

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURA))
sys.path.insert(0, KOK)
sp = il.spec_from_file_location(
    "ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)
import olcucu  # noqa: E402

API = "https://fapi.binance.com/fapi/v1/klines"


def atr_canli(sym, n=120):
    """Son n saatlik 1s mumdan ATR14 ve son fiyat."""
    u = "%s?symbol=%sUSDT&interval=1h&limit=%d" % (API, sym, n)
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read().decode("utf-8"))
    except Exception:
        return None, None
    bars = [{"h": float(k[2]), "l": float(k[3]), "c": float(k[4])} for k in d]
    if len(bars) < 20:
        return None, None
    return olcucu.atr(bars, period=14), bars[-1]["c"]


def taban(mum):
    """Tarihsel kovalar: (stop_atr, hedef_atr) -> sonuc dagilimi."""
    kova = collections.defaultdict(lambda: collections.Counter())
    ham = collections.defaultdict(list)
    son = {}
    for line in io.open(os.path.join(KOK, "radar_archive.jsonl"),
                        encoding="utf-8", errors="ignore"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        s, p = r.get("sym"), r.get("price")
        if not s or not p or s not in mum or (r.get("score") or 0) < ar.SKOR_MIN:
            continue
        t = ar.ts_ms(r["ts"])
        if s in son and (t - son[s]) < ar.COOLDOWN * 3_600_000:
            continue
        d, ix = mum[s]
        i0 = ix.get(t)
        if i0 is None or i0 < ar.YAPI_BAR:
            continue
        bars = d[i0 - ar.YAPI_BAR:i0]
        stop = ar.stop_hesapla(bars, p)
        if stop is None:
            continue
        if (p - stop) / p * 100.0 < ar.ASGARI_STOP:
            continue
        atr = olcucu.atr(bars, period=14)
        if atr <= 0:
            continue
        son[s] = t
        hedef = p * 1.10
        s_atr = (p - stop) / atr
        h_atr = (hedef - p) / atr
        # gercek sonuc
        sonuc = None
        for j in range(i0 + 1, min(i0 + 1 + ar.ZAMAN_STOP, len(d))):
            b = d[j]
            if b["l"] <= stop:
                sonuc = "STOP"
                break
            if b["h"] >= hedef:
                sonuc = "HEDEF"
                break
        if sonuc is None:
            sonuc = "ZAMAN"
        k = (kutu(s_atr), kutu(h_atr))
        kova[k][sonuc] += 1
        ham[k].append(sonuc)
    return kova


def kutu(v):
    """ATR mesafesini kovaya dusur."""
    for u in (0.5, 1.0, 1.5, 2.0, 3.0, 5.0):
        if v <= u:
            return u
    return 99.0


def komsu_kovalar(k, kova, asgari=40):
    """Kova seyrekse komsulariyla birlestir."""
    say = collections.Counter()
    say.update(kova.get(k, {}))
    if sum(say.values()) >= asgari:
        return say, "tam"
    kutular = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 99.0]
    si, hi = kutular.index(k[0]), kutular.index(k[1])
    for ds in (-1, 0, 1):
        for dh in (-1, 0, 1):
            a, b = si + ds, hi + dh
            if 0 <= a < len(kutular) and 0 <= b < len(kutular):
                say.update(kova.get((kutular[a], kutular[b]), {}))
    return say, "komsulu"


def main():
    print("=" * 104)
    print("ACIK POZISYONLAR — TABAN-ORAN TAHMINI  (%s)"
          % dt.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("🔴 Kanaat DEGIL: tarihsel kovalarin AMPIRIK sonuc dagilimi")
    print("=" * 104)

    kova = taban(ar.mumlar())
    toplam = sum(sum(v.values()) for v in kova.values())
    tum = collections.Counter()
    for v in kova.values():
        tum.update(v)
    print("\n### TABAN (tum populasyon, N=%d)" % toplam)
    for s in ("HEDEF", "STOP", "ZAMAN"):
        print("   %-6s %5d  %%%.1f" % (s, tum[s], 100.0 * tum[s] / toplam))

    st = json.load(io.open(os.path.join(KOK, "notrlong_state.json"), encoding="utf-8"))
    print("\n### ACIK POZISYONLAR")
    print("   %-7s %-4s %9s %9s %9s   %8s %8s %8s  %s"
          % ("sym", "kald", "stop ATR", "hedef ATR", "tetik ATR",
             "P(HEDEF)", "P(STOP)", "P(ZAMAN)", "kova"))
    tahminler = []
    for p in st.get("acik_pozisyonlar", []):
        sym = p["sym"]
        atr, px = atr_canli(sym)
        time.sleep(0.2)
        if not atr or not px:
            print("   %-7s mum/ATR alinamadi -> atlandi" % sym)
            continue
        s_atr = (px - p["stop"]) / atr
        h_atr = (p["tp2"] - px) / atr
        t_atr = ((p.get("kilit_tetik") or px) - px) / atr
        k = (kutu(s_atr), kutu(h_atr))
        say, tip = komsu_kovalar(k, kova)
        n = sum(say.values())
        if n == 0:
            print("   %-7s kova bos" % sym)
            continue
        ph = 100.0 * say["HEDEF"] / n
        ps = 100.0 * say["STOP"] / n
        pz = 100.0 * say["ZAMAN"] / n
        print("   %-7s %-4s %9.2f %9.2f %9.2f   %7.1f%% %7.1f%% %7.1f%%  %s N=%d"
              % (sym, "%dx" % p["kaldirac"], s_atr, h_atr, t_atr, ph, ps, pz, tip, n))
        tahminler.append({"sym": sym, "kaldirac": p["kaldirac"], "marjin": p["marjin"],
                          "giris": p["giris"], "anlik": px, "stop": p["stop"],
                          "hedef": p["tp2"], "kilit_tetik": p.get("kilit_tetik"),
                          "stop_atr": round(s_atr, 3), "hedef_atr": round(h_atr, 3),
                          "tetik_atr": round(t_atr, 3), "N_kova": n,
                          "P_hedef": round(ph, 1), "P_stop": round(ps, 1),
                          "P_zaman": round(pz, 1)})

    if tahminler:
        print("\n### PORTFOY BEKLENTISI (kova olasiliklariyla)")
        bek = 0.0
        for t in tahminler:
            k = t["kaldirac"]
            m = t["marjin"]
            kar_h = (t["hedef"] / t["anlik"] - 1) * k * m
            zar_s = (t["stop"] / t["anlik"] - 1) * k * m
            # ZAMAN kolu: taban populasyonun ZAMAN kolundaki ortalama ~0 kabul
            e = (t["P_hedef"] / 100 * kar_h) + (t["P_stop"] / 100 * zar_s)
            bek += e
            print("   %-7s hedefte %+8.2f \$ · stopta %+8.2f \$  ->  beklenen %+8.2f \$"
                  % (t["sym"], kar_h, zar_s, e))
        print("   %-7s %54s %+8.2f \$" % ("TOPLAM", "", bek))
        yol = os.path.join(BURA, "tahmin_%s.json" % dt.datetime.now().strftime("%Y%m%d_%H%M"))
        io.open(yol, "w", encoding="utf-8").write(json.dumps(
            {"ts": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "taban": dict(tum), "beklenen_usd": round(bek, 2),
             "pozisyonlar": tahminler}, ensure_ascii=False, indent=2))
        print("\n   tahmin KAYDEDILDI -> %s" % os.path.basename(yol))
        print("   (sonradan puanlanabilsin diye; bu projenin 'tahminler' disiplini)")
    print("\nSalt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
