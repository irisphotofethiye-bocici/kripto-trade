#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""notrlong AKIS DENETIMI — "yolunda mi, ne zaman mudahale?" (2026-09-06)

KULLANICI: "bi sure daha izleyelim ve poz acmazsa mudahale ederiz."

Bu betik o karari SAYIYLA verdirir. Iki soru:
  1) Simdiye kadar 0 pozisyon acmis olmak ALARM MI, yoksa BEKLENEN mi?
  2) On-kaydin N>=80 esigine yetisiyor muyuz?

TABAN ORAN — karsi-olgu C kolu (olcumler.md, pencere 08-21 -> 09-02):
     136 karar -> 33 pozisyon / 12 gun  =  2,75 poz/gun
     tur basina: 33 / (12 x 192) = %1,43
  Bot 7,5 dk'da bir kosuyor -> gunde 192 tur.

🔴 SINIR: taban oran SENTETIK karsi-olgudan geliyor (arsiv satirlari uzerinde).
   Canli tarama ayni evreni gormeyebilir. Bu bir BEKLENTI, garanti degil.

SALT-OKUNUR.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, datetime

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TUR_DK = 7.5
TUR_GUN = 24 * 60 / TUR_DK                 # 192
C_POZ, C_GUN = 33, 12                      # karsi-olgu C kolu
TABAN_GUN = C_POZ / C_GUN                  # 2,75 poz/gun
TABAN_TUR = TABAN_GUN / TUR_GUN            # tur basina olasilik
PENCERE_GUN, PENCERE_N = 30, 80


def oku(p):
    try:
        with open(os.path.join(HERE, p), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def satirlar(p):
    try:
        with open(os.path.join(HERE, p), encoding="utf-8", errors="replace") as f:
            return [l for l in f if l.strip()]
    except Exception:
        return []


def main():
    print("=" * 84)
    print("notrlong AKIS DENETIMI")
    print("=" * 84)
    print("Taban oran (karsi-olgu C kolu): %.2f poz/gun · tur basina %%%.2f"
          % (TABAN_GUN, TABAN_TUR * 100))
    print("On-kayit hedefi: %d gunde kol basina %d KAPANMIS pozisyon = %.2f poz/gun"
          % (PENCERE_GUN, PENCERE_N, PENCERE_N / PENCERE_GUN))
    marj = TABAN_GUN / (PENCERE_N / PENCERE_GUN)
    print("   -> taban oran hedefin %.2f kati  %s"
          % (marj, "(RAHAT)" if marj > 1.3 else "(🔴 KIL PAYI — dusuk akis riski)"))
    print()

    st = oku("notrlong_state.json")
    if not st:
        print("bot baslatilmamis")
        return
    try:
        b = datetime.datetime.strptime((st.get("baslangic_ts") or "")[:19],
                                       "%Y-%m-%d %H:%M:%S")
    except Exception:
        print("baslangic damgasi okunamadi")
        return
    gecen_sa = (datetime.datetime.now() - b).total_seconds() / 3600.0
    tur = len(satirlar("notrlong_equity.jsonl"))

    print("### SIMDIYE KADAR")
    print("   gecen sure : %.2f saat  (%.3f gun)" % (gecen_sa, gecen_sa / 24))
    print("   kosan tur  : %d   (equity logu satiri)" % tur)
    kayit = satirlar("notrlong_islemler.jsonl")
    idler = set()
    for l in kayit:
        try:
            k = json.loads(l)
            if not k.get("kismi"):
                idler.add(k.get("id"))
        except Exception:
            pass
    print("   durum=%-6s acik=%d  kapanmis pozisyon=%d"
          % (st.get("durum"), len(st.get("acik_pozisyonlar") or []), len(idler)))
    print()

    print("### 1) 0 POZISYON ALARM MI?")
    print("   %-14s %14s %s" % ("kosan tur", "P(hic acmama)", "yorum"))
    for n in (tur, 20, 50, 100, int(TUR_GUN), int(2 * TUR_GUN), int(3 * TUR_GUN)):
        if n <= 0:
            continue
        p = (1 - TABAN_TUR) ** n
        if p > 0.5:
            yorum = "tamamen normal"
        elif p > 0.10:
            yorum = "hala normal"
        elif p > 0.01:
            yorum = "dikkat"
        else:
            yorum = "🔴 ALARM — mudahale gerekcesi"
        etik = "%d%s" % (n, "  <- SIMDI" if n == tur else
                         ("  (%.0f gun)" % (n / TUR_GUN) if n >= TUR_GUN else ""))
        print("   %-14s %13.1f%% %s" % (etik, p * 100, yorum))
    print()
    esik_tur = int(2 * TUR_GUN)
    print("   🔑 MUDAHALE ESIGI: %d tur (~2 gun) hic pozisyon acmazsa." % esik_tur)
    print("      O noktada 'hic acmama' olasiligi %%%.1f — yani gercek bir kanit."
          % ((1 - TABAN_TUR) ** esik_tur * 100))
    print("      Once bu esik BEKLENIR; erken mudahale gurultuye tepki olur.")
    print()

    print("### 2) N>=80 HEDEFINE YETISIR MI?")
    if tur > 0:
        hiz = len(idler) / max(gecen_sa / 24, 1e-9)
        tahmin = hiz * PENCERE_GUN
        print("   gozlenen hiz %.2f poz/gun -> 30 gunde ~%.0f  %s"
              % (hiz, tahmin,
                 "(yeterli veri yok)" if gecen_sa < 24 else
                 ("YETER" if tahmin >= PENCERE_N else "🔴 YETMEZ")))
        if gecen_sa < 24:
            print("   ⚠️ %.1f saat cok kisa — bu tahmin ANLAMSIZ. En az 1 gun gerek."
                  % gecen_sa)
    print()
    print("### 3) [DEGISTI 2026-09-06] SKOR KAPISI KALDIRILDI")
    print("   Eskiden burada 'N2 skor kapisi yuzunden 80'e ulasamaz' riski yaziliydi.")
    print("   Kapi kaldirilinca o risk KALKTI — tek kol TAM akista kosuyor.")
    print("   Kalan risk: taban oranin kendisi kil payi (%.2f vs %.2f poz/gun)."
          % (TABAN_GUN, PENCERE_N / PENCERE_GUN))
    print("   On-kayit bolum 7: 'N 30 gunde 80'e ulasmazsa -> OLCULEMEDI, UZATILMAZ.'")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
