#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ARX ve TAO — KAR KILIDI UYGULANSAYDI NE OLURDU?

Kullanici: "tao ve arx da neler olurdu uygulansa"

Kural (2026-09-07, canlida):
    TETIK  fiyat = G x (1 + 0.20/k)
    ALIM   pozisyonun %20'si
    STOP   fiyat = G x (1 + 0.15/k)

Karsilastirma icin TIA da var — ayni bot, ayni gun, kilit TETIKLEDI.
SALT-OKUNUR. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, sys, datetime as dt
import importlib.util as il

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURA))
sys.path.insert(0, KOK)
sp = il.spec_from_file_location("olc", os.path.join(BURA, "01_olcum.py"))
olc = il.module_from_spec(sp)
sp.loader.exec_module(olc)

TETIK_ROI, STOP_ROI, PAY = 20.0, 15.0, 0.20
HEDEF_PCT = 10.0
# EK RAPOR — olcut DEGIL, yalniz "ne kadar yaklasti" sorusu icin
MERDIVEN = [5.0, 10.0, 15.0, 20.0]


def main():
    print("=" * 100)
    print("ARX ve TAO — KAR KILIDI UYGULANSAYDI")
    print("kural: tetik +%.0f%% ROI · alim %%%.0f · stop +%.0f%% ROI"
          % (TETIK_ROI, PAY * 100, STOP_ROI))
    print("=" * 100)

    kayit = []
    for l in io.open(os.path.join(KOK, "notrlong_islemler.jsonl"), encoding="utf-8"):
        l = l.strip()
        if l:
            kayit.append(json.loads(l))

    for r in kayit:
        if r.get("kismi") and r.get("sebep") != "KAR_KILIDI":
            continue
        sym, g, k = r["sym"], r["giris"], r["kaldirac"]
        yon = r["yon"]
        miktar = r["notional"] / g
        yi = 1 if yon == "LONG" else -1
        tetik = g * (1 + yi * TETIK_ROI / 100.0 / k)
        kstop = g * (1 + yi * STOP_ROI / 100.0 / k)
        hedef = g * (1 + yi * HEDEF_PCT / 100.0)

        kapanis_ms = olc.yerel_ms(r["ts"])
        giris_ms = kapanis_ms - int((r.get("tutma_saat") or 0) * 3600 * 1000)
        bars = olc.mum_getir(sym, giris_ms - 5 * 60000, kapanis_ms + 20 * 60000)
        if not bars:
            print("\n--- %-5s MUM YOK ---" % sym)
            continue

        en_iyi = max(b[1] for b in bars) if yon == "LONG" else min(b[2] for b in bars)
        mfe_roi = (en_iyi / g - 1) * 100.0 * k * yi
        t_iyi = [b[0] for b in bars if (b[1] if yon == "LONG" else b[2]) == en_iyi][0]

        print("\n--- %-5s  %s %dx  ·  gercek sonuc %+.2f $ (%s) ---"
              % (sym, yon, k, r["sonuc_usdt"], r["sebep"]))
        print("   giris %.6f · marjin %.2f · notional %.2f" % (g, r["marjin"], r["notional"]))
        print("   TETIK  %.6f  (fiyatta %+.2f%%)" % (tetik, (tetik / g - 1) * 100))
        print("   kilit stop %.6f  (fiyatta %+.2f%%  = +%.0f%% ROI = %+.2f $)"
              % (kstop, (kstop / g - 1) * 100, STOP_ROI, r["marjin"] * STOP_ROI / 100))
        print("   EN IYI %.6f (%+.2f%% fiyat = %+.1f%% ROI)  %s"
              % (en_iyi, (en_iyi / g - 1) * 100, mfe_roi, olc.ms_str(t_iyi)))

        if r.get("sebep") == "KAR_KILIDI":
            print("   -> BU POZISYONDA KILIT ZATEN TETIKLENDI (canli)")
            continue

        vardi = (en_iyi >= tetik) if yon == "LONG" else (en_iyi <= tetik)
        eksik_roi = TETIK_ROI - mfe_roi
        eksik_fiy = abs(tetik - en_iyi) / g * 100
        print("   TETIKLER MIYDI: %s" % ("EVET" if vardi else "HAYIR"))
        if not vardi:
            print("      eksik: %.1f puan ROI  ·  fiyatta %.2f%%" % (eksik_roi, eksik_fiy))

        olc.K["k"] = k
        # 🔴 Stop TURETME — 01_olcum.py ile AYNI dallanma olmak ZORUNDA.
        #   Ilk surumde 'cikis/(1-slipaj)' HER cikisa uygulanmisti; TP2 cikisinda
        #   bu HEDEFI stop sanar ve ilk barda "stop" tetikler. Sinama yakaladi
        #   (tutar dogru, SEBEP yanlis) ve yayimlamayi reddetti — guard calisti.
        if r["sebep"] == "STOP":
            stop = r["cikis"] / (1 - olc.SLIP) if yon == "LONG" else r["cikis"] / (1 + olc.SLIP)
        elif r.get("r"):
            net_pct = (r["cikis"] / g - 1) * 100.0 * yi
            risk_pct = net_pct / r["r"]
            if risk_pct <= 0:
                print("   stop turetilemedi -> atlandi")
                continue
            stop = g * (1 - yi * risk_pct / 100.0)
        else:
            print("   stop turetilemedi (r yok) -> atlandi")
            continue
        n0, s0, m0, _ = olc.yol_kos(bars, g, stop, hedef, miktar, yon, False)
        n1, s1, m1, o1 = olc.yol_kos(bars, g, stop, hedef, miktar, yon, True)
        print("   SINAMA: yeniden kurulan gercek %+.2f $ (%s) vs defter %+.2f $ (%s)"
              % (n0, s0, r["sonuc_usdt"], r["sebep"]))
        if s0 != r["sebep"] or abs(n0 - r["sonuc_usdt"]) > max(abs(r["sonuc_usdt"]) * 0.02, 0.5):
            print("      🔴 SINAMA DUSTU -> bu poz icin karsi-olgu YAZILMAZ")
            continue
        print("   KILITLI    %+.2f $ (%s)   ->  FARK %+.2f $" % (n1, s1, n1 - n0))

        # --- EK: hangi tetik seviyesi yakalardi (BILGI, esik SECIMI DEGIL)
        print("   ek — tetik seviyesi merdiveni (BILGI, kural DEGISMEZ):")
        for m in MERDIVEN:
            tt = g * (1 + yi * m / 100.0 / k)
            var = (en_iyi >= tt) if yon == "LONG" else (en_iyi <= tt)
            print("      tetik +%2.0f%% ROI -> fiyat %.6f  %s" % (m, tt, "VARDI" if var else "varmadi"))

    print()
    print("=" * 100)
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
