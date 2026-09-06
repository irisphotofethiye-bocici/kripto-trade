#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""notrlong HUNI TESHISI — LONG'u NEREDE kaybediyoruz? (2026-09-06)

KULLANICI: "botun poza girmesini engelleyen ne?"

Ilk teshis "10 adayin 7'si karar-yok" demisti ama NEDENINI soylemiyordu —
karar_yon adlandirilmis veto uretmeden None donuyor. Bu betik NOTR-LONG
zincirini ADIM ADIM yeniden yurutur ve her adayin HANGI BASAMAKTA oldugunu sayar.

ZINCIR (testbot._karar_yon_ham, NOTR dali, satir ~633):
   1) stage IN (BASLIYOR, HAZIRLANIYOR)
   2) skor >= stage_esigi   (HAZIRLANIYOR -> radar_alert_skor · BASLIYOR -> +5)
   3) smart == "LONG"
   4) NOT asiri_yukselmis
   5) NOT long_veto
   6) taker >= 1.0
   7) notr_long_acik >= 1
Yedisi de gecmezse LONG YOK.

🔴 SALT-OKUNUR. Giris ACMAZ, state/defter YAZMAZ.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, sys, collections

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)

import testbot, evren, notrlong

ADIMLAR = [
    "1 stage BASLIYOR/HAZIRLANIYOR",
    "2 skor >= esik",
    "3 smart == LONG",
    "4 asiri_yukselmis degil",
    "5 long_veto yok",
    "6 taker >= 1.0",
    "7 notr_long_acik",
]


def main():
    print("=" * 92)
    print("notrlong HUNI TESHISI — LONG'u NEREDE kaybediyoruz?")
    print("=" * 92)
    print()

    esik_uzun = evren.esik("radar_alert_skor", 40.0) + 5
    esik_hazir = evren.esik("radar_alert_skor", 40.0)
    nla = evren.esik("notr_long_acik", 0.0)
    print("### ESIKLER (config'ten)")
    print("   BASLIYOR skor esigi     : %.0f" % esik_uzun)
    print("   HAZIRLANIYOR skor esigi : %.0f" % esik_hazir)
    print("   notr_long_acik          : %.0f  %s" % (nla, "ACIK" if nla >= 1 else "🔴 KAPALI"))
    print()

    print("### TARAMA (botun gordugu ADAY LISTESI)")
    rows, pillars = notrlong.tara()
    print("   kisa listeye giren aday: %d" % len(rows))
    if not rows:
        print("   🔴 hic aday yok")
        return
    print()

    huni = collections.Counter()
    detay = []
    for r in rows:
        sym = r["sym"]
        pil = pillars.get(sym, {})
        smart = pil.get("smart")
        taker = pil.get("taker")
        stage = r.get("stage")
        skor = r.get("score") or 0
        chg24 = r.get("chg24") or 0
        stage_esigi = esik_hazir if stage == "HAZIRLANIYOR" else esik_uzun

        oldu = None
        if stage not in ("BASLIYOR", "HAZIRLANIYOR"):
            oldu = 0
        elif skor < stage_esigi:
            oldu = 1
        elif smart != "LONG":
            oldu = 2
        else:
            # 4-6 icin gercek karar_yon'u calistirip veto adini alalim
            v = []
            k = testbot.karar_yon("NOTR", r, pil, False, veto_out=v)
            if k and k[0] == "LONG":
                oldu = None
            else:
                kat = v[0]["kategori"] if v else "?"
                oldu = {"blowoff": 3, "long_veto": 4, "taker_soguma": 5}.get(kat, 6)
        huni[oldu if oldu is not None else "GECTI"] += 1
        detay.append((sym, stage, skor, smart, taker, chg24,
                      ADIMLAR[oldu] if oldu is not None else "GECTI -> LONG"))

    print("### ADAY ADAY — nerede oldu")
    print("   %-13s %-13s %6s %-7s %7s %7s  %s"
          % ("sembol", "stage", "skor", "smart", "taker", "chg24", "oldugu adim"))
    for sym, stage, skor, smart, taker, chg24, nerede in detay:
        print("   %-13s %-13s %6.1f %-7s %7s %+7.1f  %s"
              % (sym, stage, skor, smart or "-",
                 ("%.2f" % taker) if taker is not None else "-", chg24, nerede))
    print()

    print("### HUNI — kac aday hangi basamakta oldu")
    n = len(rows)
    kalan = n
    for i, ad in enumerate(ADIMLAR):
        olen = huni.get(i, 0)
        print("   %-32s giren %3d  olen %3d  kalan %3d" % (ad, kalan, olen, kalan - olen))
        kalan -= olen
    print("   %-32s %s%d" % ("LONG KARARI", " " * 22, huni.get("GECTI", 0)))
    print()

    print("### YORUM")
    if huni.get("GECTI", 0):
        print("   Bu turda LONG karari VAR — sorun akista degil, zamanlamada.")
    else:
        enb = max((i for i in range(len(ADIMLAR)) if huni.get(i, 0)),
                  key=lambda i: huni.get(i, 0), default=None)
        if enb is not None:
            print("   EN COK ELEYEN BASAMAK: %s  (%d/%d aday)"
                  % (ADIMLAR[enb], huni[enb], n))
        print("   ⚠️ TEK TUR = TEK ORNEK. Hukum icin birkac tur gerekir;")
        print("      bu betik her kosuldugunda o anki adaylara bakar.")
    print()
    print("Giris ACILMADI · state/defter YAZILMADI")


if __name__ == "__main__":
    main()
