#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""notrlong TESHIS — neden pozisyon acilmadi? (2026-09-06)

Ilk tur 0 pozisyon acti. Bu MESRU olabilir (NOTR+LONG'da vetolar tutuyor) ya da
HATA olabilir. Fark ancak aday aday bakinca anlasilir.

🔴 SALT-OKUNUR. Giris ACMAZ, state YAZMAZ, defter YAZMAZ.
   yeni_giris_ac hic cagrilmaz; yalniz karar_yon calistirilir.
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


def main():
    print("=" * 88)
    print("notrlong TESHIS — aday aday karar dokumu (SALT-OKUNUR)")
    print("=" * 88)
    print("rejim ZORLA: %s   ·   yalniz LONG   ·   N2 skor kapisi: %.0f"
          % (notrlong.REJIM_ZORLA, notrlong.SKOR_KAPISI))
    print()

    print("### 1) TARAMA")
    rows, pillars = notrlong.tara()
    print("   kisa listeye giren aday: %d" % len(rows))
    if not rows:
        print("   🔴 HIC ADAY YOK -> tarama tarafinda sorun var")
        return
    print()

    _pr = evren.para_rejim()
    try:
        evren.btc_pay_guncelle()
        bp = evren.btc_pay_akisi()
    except Exception:
        bp = None
    para_cikis = bool(_pr and _pr.get("rejim") == "PARA CIKIYOR")
    para_durgun = bool(_pr and _pr.get("rejim") == "PARA DURGUN")
    print("### 2) BAGLAM")
    print("   para rejimi : %s  (para_cikis=%s · para_durgun=%s)"
          % ((_pr or {}).get("rejim"), para_cikis, para_durgun))
    print("   btc_pay bant: %s" % ((bp or {}).get("bant")))
    print("   GERCEK rejim: %s   <- bot bunu ZORLA %s yapiyor"
          % (evren.btc_rejim().get("rejim") if hasattr(evren, "btc_rejim") else "?",
             notrlong.REJIM_ZORLA))
    print()

    print("### 3) ADAY ADAY KARAR")
    print("   %-14s %6s %8s %-16s %s" % ("sembol", "skor", "chg24", "KARAR", "veto / sebep"))
    sayac = collections.Counter()
    for r in rows:
        sym = r["sym"]
        pil = pillars.get(sym, {})
        vlist = []
        karar = testbot.karar_yon(notrlong.REJIM_ZORLA, r, pil, False,
                                  veto_out=vlist, para_cikis=para_cikis,
                                  btc_pay=bp, para_durgun=para_durgun)
        if not karar:
            kat = vlist[0]["kategori"] if vlist else "karar-yok"
            detay = (vlist[0].get("detay") or "")[:52] if vlist else ""
            sayac["VETO:" + kat] += 1
            print("   %-14s %6.1f %+8.1f %-16s %s" %
                  (sym, r.get("score") or 0, r.get("chg24") or 0, "-", "%s %s" % (kat, detay)))
            continue
        yon, mod, sebep = karar
        if yon != "LONG":
            sayac["SHORT (atildi)"] += 1
        else:
            sayac["LONG %s" % mod] += 1
            if (r.get("score") or 0) < notrlong.SKOR_KAPISI:
                sayac["  -> N2 skor kapisinda elenir"] += 1
        print("   %-14s %6.1f %+8.1f %-16s %s" %
              (sym, r.get("score") or 0, r.get("chg24") or 0,
               "%s/%s" % (yon, mod), (sebep or "")[:52]))
    print()

    print("### 4) OZET")
    for k, v in sorted(sayac.items(), key=lambda x: -x[1]):
        print("   %-34s %d" % (k, v))
    print()
    long_var = sum(v for k, v in sayac.items() if k.startswith("LONG"))
    if long_var == 0:
        print("   -> Bu turda LONG karari CIKMADI. Bot dogru calisiyor olabilir;")
        print("      vetolar 'AYNEN korunuyor' (on-kayit bolum 3). Birkac tur")
        print("      gozlemlemeden 'bozuk' denemez.")
    else:
        print("   -> LONG karari VAR. ONAY_BEKLE ise giris ERTESI turda olur")
        print("      (on-kayit: 'GIRIS: kararin ertesi turunda').")
    print()
    print("Giris ACILMADI · state YAZILMADI · defter YAZILMADI")


if __name__ == "__main__":
    main()
