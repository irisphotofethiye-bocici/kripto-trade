#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""notrlong: POZ ACMAMANIN SEBEBI HANGI KAPI? (2026-09-06)

Iki kaynak:
  A) notrlong_elenen.jsonl  -> botun KENDI kaydi (kesin, ama 2,5 saat)
  B) radar_archive.jsonl    -> TABAN ORAN (bekleme suresi tahmini icin)

NOTR rejimde LONG donduren KOD YOLU sayisi: testbot.py'de tam IKI tane
  (1) NOTR stage-aktif LONG  [:673]  -> stage in (BASLIYOR,HAZIRLANIYOR)
                                        + skor >= esik + smart==LONG
                                        + not blowoff + not long_veto + taker>=1.0
                                        + config notr_long_acik >= 1
  (2) NOTR-fade LONG         [:733]  -> config notr_fade_acik >= 1

MA50+ucuz kapisi [:485] SART OLARAK SHORT dondurur (LONG uretemez) ve
stage/skor SORMAZ -> zincirin ONUNDE calisir.

SALT-OKUNUR. Arsiv context'e YUKLENMEZ; Python okur, ozet basar.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, sys, collections

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
import evren  # noqa: E402

ELENEN = os.path.join(KOK, "notrlong_elenen.jsonl")
ARSIV = os.path.join(KOK, "radar_archive.jsonl")
BOT_BAS = "2026-09-06"
GUN_GERI = "2026-08-08"          # taban oran penceresi (~30 gun)
ESIK_HAZ = evren.esik("radar_alert_skor", 40.0)
ESIK_BAS = ESIK_HAZ + 5
HAVUZ = 10                        # bot her turda skora gore ilk 10'a bakiyor


def bolum(b):
    print()
    print("=" * 88)
    print(b)
    print("=" * 88)


def a_botun_kaydi():
    bolum("A) BOTUN KENDI KAYDI — notrlong_elenen.jsonl")
    if not os.path.exists(ELENEN):
        print("   kayit yok")
        return
    rec = []
    for l in open(ELENEN, encoding="utf-8"):
        l = l.strip()
        if l:
            try:
                rec.append(json.loads(l))
            except Exception:
                pass
    if not rec:
        print("   kayit yok")
        return
    turlar = sorted(set(r.get("ts", "")[:16] for r in rec))
    print("   pencere : %s -> %s  ·  %d tur  ·  %d kayit"
          % (rec[0].get("ts"), rec[-1].get("ts"), len(turlar), len(rec)))
    print()
    c = collections.Counter(r.get("kapi") for r in rec)
    print("   %-24s %6s %8s   %s" % ("KAPI", "N", "pay", "anlami"))
    ANLAM = {
        "1_stage_izle": "stage 'izle' -> LONG yolu hic acilmiyor",
        "2_skor_dusuk": "stage aktif AMA skor esigin altinda",
        "3_smart_degil": "stage+skor OK, smart LONG degil",
        "5_short_karari": "GECERLI karar cikti ama SHORT -> yalniz-LONG atti",
    }
    for k, v in c.most_common():
        print("   %-24s %6d %7.1f%%   %s"
              % (k, v, 100.0 * v / len(rec), ANLAM.get(k, "")))
    print()
    aktif = [r for r in rec if r.get("stage") in ("BASLIYOR", "HAZIRLANIYOR")]
    print("   🔑 stage AKTIF olan aday sayisi : %d / %d  (%%%.1f)"
          % (len(aktif), len(rec), 100.0 * len(aktif) / len(rec)))
    if aktif:
        c2 = collections.Counter(r.get("sym") for r in aktif)
        print("      tekil sembol: %s" % ", ".join("%s(%d)" % (s, n) for s, n in c2.most_common()))
        gecen = [r for r in aktif
                 if (r.get("score") or 0) >= (ESIK_HAZ if r.get("stage") == "HAZIRLANIYOR" else ESIK_BAS)]
        print("      skor kapisini gecen        : %d" % len(gecen))
    print()
    sh = [r for r in rec if r.get("kapi") == "5_short_karari"]
    if sh:
        kaynak = collections.Counter(
            ("MA50+ucuz" if "MA50" in str(r.get("detay")) else
             "A+B" if "A+B" in str(r.get("detay")) else "diger") for r in sh)
        print("   SHORT kararlari HANGI KAPIDAN geldi:")
        for k, v in kaynak.most_common():
            print("      %-14s %4d   (bu kapi TANIMI GEREGI SHORT dondurur)" % (k, v))


def b_taban_oran():
    bolum("B) TABAN ORAN — radar_archive, %s sonrasi" % GUN_GERI)
    if not os.path.exists(ARSIV):
        print("   arsiv yok")
        return
    turlar = collections.defaultdict(list)
    n = 0
    with open(ARSIV, encoding="utf-8", errors="ignore") as f:
        for l in f:
            l = l.strip()
            if not l:
                continue
            try:
                r = json.loads(l)
            except Exception:
                continue
            ts = r.get("ts") or ""
            if ts < GUN_GERI or ts >= BOT_BAS:
                continue
            n += 1
            turlar[ts[:16]].append(r)
    print("   kayit: %d  ·  tur: %d" % (n, len(turlar)))
    if not turlar:
        return

    adim = collections.Counter()
    tur_long = 0
    tur_ma50 = 0
    for t, rows in turlar.items():
        rows.sort(key=lambda x: -(x.get("score") or 0))
        havuz = rows[:HAVUZ]
        bu_tur_long = False
        bu_tur_ma50 = False
        for r in havuz:
            adim["0_aday"] += 1
            # ⚠️ radar_archive'da `ma50_mesafe` ALANI YOK -> MA50+ucuz kapisi
            #    arsivden YENIDEN URETILEMEZ. Yalniz fiyat kosulu sayilir ve bu
            #    bir UST SINIRDIR (kapinin ikinci sarti kontrol edilemiyor).
            p = r.get("price")
            if p and p <= 0.07:
                bu_tur_ma50 = True
            st = r.get("stage")
            if st not in ("BASLIYOR", "HAZIRLANIYOR"):
                continue
            adim["1_stage_aktif"] += 1
            sk = r.get("score") or 0
            if sk < (ESIK_HAZ if st == "HAZIRLANIYOR" else ESIK_BAS):
                continue
            adim["2_skor_ok"] += 1
            if r.get("smart") != "LONG":
                continue
            adim["3_smart_LONG"] += 1
            tk = r.get("taker")
            if (tk or 0) < 1.0:
                continue
            adim["4_taker_ok"] += 1
            bu_tur_long = True
        if bu_tur_long:
            tur_long += 1
        if bu_tur_ma50:
            tur_ma50 += 1

    print()
    print("   HUNI (her turda skora gore ilk %d aday):" % HAVUZ)
    tab = ["0_aday", "1_stage_aktif", "2_skor_ok", "3_smart_LONG", "4_taker_ok"]
    onc = None
    for k in tab:
        v = adim.get(k, 0)
        gec = ("%6.2f%%" % (100.0 * v / onc)) if onc else "     -"
        print("      %-16s %8d   bir onceki adimin %s" % (k, v, gec))
        onc = v if v else 1

    print()
    pay = 100.0 * tur_long / len(turlar)
    print("   🔑 LONG-adayi BULUNAN tur orani : %d/%d = %%%.1f" % (tur_long, len(turlar), pay))
    if pay > 0:
        print("      -> ortalama bekleme ~%.1f tur = ~%.1f saat (7,5 dk tur)"
              % (100.0 / pay, 100.0 / pay * 7.5 / 60.0))
    print("   ucuz-fiyat ($<=0.07) bulunan tur : %d/%d = %%%.1f   <- MA50+ucuz UST SINIRI"
          % (tur_ma50, len(turlar), 100.0 * tur_ma50 / len(turlar)))
    print("      (arsivde ma50_mesafe alani YOK -> kapinin kendisi yeniden uretilemiyor)")
    print()
    print("   ⚠️ SINIR: arsiv RADAR'in taramasi; botun 150-sembol havuzuyla birebir")
    print("      ayni degil. Sayi bir BUYUKLUK MERTEBESIDIR, kesin oran degil.")
    print("      Ayrica taker/smart alanlari arsivde eksik olabilir -> alt sinir.")


def c_hukum():
    bolum("C) HUKUM")
    print("   Kapali kapilar (config):")
    print("      notr_long_acik = %s   (1 = NOTR stage-aktif LONG ACIK)"
          % evren.esik("notr_long_acik", 0.0))
    print("      notr_fade_acik = %s   (0 = NOTR-fade LONG KAPALI, 2026-08-10 olcumle)"
          % evren.esik("notr_fade_acik", 1.0))
    print("      ma50_kapisi_acik = %s · ab_kapisi_acik = %s   (IKISI DE SHORT-ONLY)"
          % (evren.esik("ma50_kapisi_acik", 1), evren.esik("ab_kapisi_acik", 1)))
    print()
    print("   Bot dosyalarina yazim: YOK · arsiv context'e yuklenmedi.")


if __name__ == "__main__":
    a_botun_kaydi()
    b_taban_oran()
    c_hukum()
