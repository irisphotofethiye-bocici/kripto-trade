#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""N1'DE SKORUN ETKISI VAR MI? — on-kayit kusuru denetimi (2026-09-06)

KULLANICI: "n1 skor kapisi yok, skorun etkisi var mi?"

🔴 SORU HAKLI CIKTI. On-kayit "N1: skor kapisi YOK" diyor ama skor N1'de
   UC AYRI YERDE is goruyor:

   (a) notrlong.tara()  ->  radar.analyze sonucu `score >= 30` suzgeci
   (b) notrlong.tara()  ->  kisa liste SKORA GORE siralanip [:10] kirpiliyor
   (c) testbot.karar_yon ->  `skor >= stage_esigi`
            BASLIYOR      -> radar_alert_skor + 5 = 45
            HAZIRLANIYOR  -> radar_alert_skor     = 40

   Yani N1 skor-suz DEGIL; yalnizca EK bir kapi tasimiyor.

🔴 VE DAHA CIDDISI: N2'nin kapisi `score >= 45`. Ama (c) zaten BASLIYOR icin
   45 istiyor. Demek ki N2 kapisi BASLIYOR dalinda HICBIR SEY eklemiyor;
   yalnizca HAZIRLANIYOR dalinda skoru [40,45) araliginda olanlari kesiyor.

   => N1 - N2 farki YALNIZCA su populasyonu olcuyor:
        stage == HAZIRLANIYOR  VE  40 <= skor < 45
   Bu, "skor kapisi ne katiyor"dan cok daha DAR bir soru.

Bu betik o populasyonun BUYUKLUGUNU arsivde olcer: yeterince buyuk mu, yoksa
N1 ve N2 pratikte AYNI bot mu olacak?

VERI: testbot_aday_arsiv.jsonl — context'e YUKLENMEZ, ozet basilir.
SALT-OKUNUR.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, collections

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARSIV = os.path.join(KOK, "testbot_aday_arsiv.jsonl")

ESIK_HAZIR = 40.0
ESIK_BASLIYOR = 45.0
N2_KAPI = 45.0


def main():
    print("=" * 92)
    print("N1'DE SKORUN ETKISI VAR MI?  —  ve N1-N2 farki NEYI olcuyor?")
    print("=" * 92)
    print()

    print("### 1) SKOR N1'DE NEREDE IS GORUYOR (koddan)")
    print("   (a) tara(): radar.analyze sonucu  score >= 30 suzgeci")
    print("   (b) tara(): kisa liste SKORA GORE siralanip [:10] kirpiliyor")
    print("   (c) karar_yon: skor >= stage_esigi  (BASLIYOR 45 · HAZIRLANIYOR 40)")
    print("   -> N1 skor-suz DEGIL. On-kayittaki 'skor kapisi YOK' ifadesi EKSIK.")
    print()

    n = 0
    kova = collections.Counter()
    # N1'in gecirdigi vs N2'nin gecirdigi (ilk uc kapi seviyesinde)
    n1_gecen = n2_gecen = 0
    fark_pop = 0
    fark_ornek = []
    skor_dagilim = collections.Counter()

    with open(ARSIV, encoding="utf-8", errors="replace") as f:
        for l in f:
            l = l.strip()
            if not l:
                continue
            try:
                r = json.loads(l)
            except Exception:
                continue
            st, sk, sm = r.get("stage"), r.get("score"), r.get("smart")
            if st is None or sk is None:
                continue
            n += 1
            if st not in ("BASLIYOR", "HAZIRLANIYOR"):
                continue
            esik = ESIK_HAZIR if st == "HAZIRLANIYOR" else ESIK_BASLIYOR
            if sk < esik:
                continue
            if sm != "LONG":
                continue
            # buraya gelen = ilk UC kapiyi gecen aday (N1 icin)
            n1_gecen += 1
            kova[st] += 1
            skor_dagilim[int(sk // 5) * 5] += 1
            if sk >= N2_KAPI:
                n2_gecen += 1
            else:
                fark_pop += 1
                if len(fark_ornek) < 8:
                    fark_ornek.append((r.get("sym"), st, sk))

    print("### 2) ARSIVDE OLCUM (N=%d aday satiri)" % n)
    print("   ilk UC kapiyi gecen (N1):            %6d" % n1_gecen)
    print("   ayni + skor >= %.0f  (N2):            %6d" % (N2_KAPI, n2_gecen))
    print("   FARK (yalniz N1'in aldigi):          %6d   -> %%%.1f"
          % (fark_pop, 100.0 * fark_pop / max(1, n1_gecen)))
    print()
    print("   stage kirilimi (N1'in gecirdikleri):")
    for s, k in kova.most_common():
        print("      %-14s %6d" % (s, k))
    print()

    print("### 3) FARK POPULASYONU NE? (N1'de var, N2'de yok)")
    if fark_pop:
        print("   Tanim: stage == HAZIRLANIYOR  VE  %.0f <= skor < %.0f"
              % (ESIK_HAZIR, N2_KAPI))
        print("   Ornekler:")
        for sym, st, sk in fark_ornek:
            print("      %-12s %-13s skor %.1f" % (sym, st, sk))
    else:
        print("   🔴 FARK POPULASYONU BOS — N1 ve N2 AYNI adaylari gorur.")
    print()

    print("### 4) SKOR DAGILIMI — N1'in gecirdikleri")
    for k in sorted(skor_dagilim):
        bar = "#" * max(1, int(40.0 * skor_dagilim[k] / max(skor_dagilim.values())))
        print("   %3d-%3d  %5d  %s" % (k, k + 4, skor_dagilim[k], bar))
    print()

    print("### 5) HUKUM")
    oran = fark_pop / max(1, n1_gecen)
    print("   N1 ile N2 arasindaki aday farki: %%%.1f" % (100 * oran))
    if oran < 0.10:
        print("   🔴 CIDDI KUSUR: iki kol adaylarin %%%.0f'inde ayrisiyor."
              % (100 * oran))
        print("      N1-N2 karsilastirmasi 'skor kapisi ne katiyor'u OLCEMEZ;")
        print("      yalnizca cok dar bir alt kumeyi olcer. Kollar pratikte")
        print("      AYNI bot olacak ve fark GURULTUDEN ayirt edilemeyecek.")
    elif oran < 0.30:
        print("   ⚠️ ZAYIF: fark var ama dar. Gucu dusuk bir karsilastirma.")
    else:
        print("   ✅ Fark yeterince genis; karsilastirma anlamli.")
    print()
    print("Salt-okuma. Arsiv context'e yuklenmedi. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
