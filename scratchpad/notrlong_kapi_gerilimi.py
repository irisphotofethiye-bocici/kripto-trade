#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SKOR KAPISI ile STAGE KAPISI CAKISIYOR MU? — arsivde olcum (2026-09-06)

KULLANICI: "botun poza girmesini engelleyen ne?"

Tek turluk huni teshisi sunu gosterdi: 10 adayin 8'i `stage=izle` diye olduu,
kalan 2'si skor esigine takildi. Ve EN YUKSEK SKORLULAR hep `izle` idi.

HIPOTEZ (bugunku skor olcumune baglaniyor): skor BUYUKLUK olcuyor — cok hareket
etmis coin yuksek skor alir, ama cok hareket etmis coin ARTIK "izle"dir
(kurulum gecmis). Yani skor kapisi ile stage kapisi TERS calisir ve kesisim
neredeyse BOS kalir.

Bu betik hipotezi TEK TUR yerine ARSIVDE olcer.
VERI: testbot_aday_arsiv.jsonl (botun KENDI aday evreni).
🔴 Arsiv context'e YUKLENMEZ — Python okur, yalniz ozet basar (CLAUDE.md).

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


def main():
    print("=" * 92)
    print("SKOR KAPISI ile STAGE KAPISI CAKISIYOR MU?")
    print("=" * 92)
    print("Veri: testbot_aday_arsiv.jsonl (ozet basilir, icerik context'e girmez)")
    print()

    n = 0
    stage_say = collections.Counter()
    skor_stage = collections.defaultdict(list)
    gecen = collections.Counter()
    smart_say = collections.Counter()
    ilk = son = None
    # kesisim sayaci
    a_stage = a_skor = a_ikisi = a_uc = 0

    with open(ARSIV, encoding="utf-8", errors="replace") as f:
        for l in f:
            l = l.strip()
            if not l:
                continue
            try:
                r = json.loads(l)
            except Exception:
                continue
            st = r.get("stage")
            sk = r.get("score")
            if st is None or sk is None:
                continue
            n += 1
            ts = r.get("ts")
            if ts:
                ilk = ts if ilk is None or ts < ilk else ilk
                son = ts if son is None or ts > son else son
            stage_say[st] += 1
            skor_stage[st].append(sk)
            smart = r.get("smart")
            esik = ESIK_HAZIR if st == "HAZIRLANIYOR" else ESIK_BASLIYOR
            k_stage = st in ("BASLIYOR", "HAZIRLANIYOR")
            k_skor = sk >= esik
            if k_stage:
                a_stage += 1
            if k_skor:
                a_skor += 1
            if k_stage and k_skor:
                a_ikisi += 1
                smart_say[smart or "-"] += 1
                if smart == "LONG":
                    a_uc += 1
                gecen[st] += 1

    if not n:
        print("arsiv bos ya da okunamadi")
        return

    print("### KAPSAM")
    print("   aday satiri: %d  ·  %s .. %s" % (n, ilk, son))
    print()

    print("### 1) STAGE DAGILIMI ve SKOR")
    print("   %-14s %9s %8s %10s %10s" % ("stage", "N", "pay", "skor ort", "skor medyan"))
    for st, k in stage_say.most_common():
        v = sorted(skor_stage[st])
        print("   %-14s %9d %7.1f%% %10.1f %10.1f"
              % (st, k, 100.0 * k / n, sum(v) / len(v), v[len(v) // 2]))
    print()
    print("   🔑 Skor ile stage TERS mi? (yuksek skor -> kurulum GECMIS mi)")
    if "izle" in skor_stage and "HAZIRLANIYOR" in skor_stage:
        i = skor_stage["izle"]
        h = skor_stage["HAZIRLANIYOR"]
        print("      izle ort %.1f  ·  HAZIRLANIYOR ort %.1f  ->  fark %+.1f"
              % (sum(i) / len(i), sum(h) / len(h), sum(i) / len(i) - sum(h) / len(h)))
    print()

    print("### 2) KAPILARIN KESISIMI — asil cevap")
    print("   %-40s %9s %8s" % ("kapi", "gecen", "oran"))
    print("   %-40s %9d %7.2f%%" % ("stage IN (BASLIYOR,HAZIRLANIYOR)", a_stage,
                                    100.0 * a_stage / n))
    print("   %-40s %9d %7.2f%%" % ("skor >= esik", a_skor, 100.0 * a_skor / n))
    print("   %-40s %9d %7.2f%%" % ("IKISI BIRDEN", a_ikisi, 100.0 * a_ikisi / n))
    print("   %-40s %9d %7.2f%%" % ("+ smart == LONG (ucu birden)", a_uc,
                                    100.0 * a_uc / n))
    print()
    bag = (a_ikisi / n) / ((a_stage / n) * (a_skor / n)) if a_stage and a_skor else 0
    print("   BAGIMSIZLIK ORANI: gozlenen_kesisim / (bagimsiz_beklenen) = %.2f" % bag)
    if bag < 0.7:
        print("   -> 🔴 KAPILAR BIRBIRINI KESIYOR. Bagimsiz olsalardi %.2f kat daha"
              % (1 / bag if bag else 0))
        print("      cok aday gecerdi. Skor ve stage AYNI ANDA saglanmasi ZOR.")
    elif bag > 1.3:
        print("   -> kapilar birbirini DESTEKLIYOR")
    else:
        print("   -> kapilar yaklasik BAGIMSIZ")
    print()

    print("### 3) IKISINI GECENLERDE smart DAGILIMI (3. kapi)")
    for s, k in smart_say.most_common():
        print("   %-10s %6d  %5.1f%%" % (s, k, 100.0 * k / max(1, a_ikisi)))
    print()

    print("### 4) SONUC — bir aday LONG'a ne kadar yakin?")
    print("   %d aday satirindan %d'i (%.3f%%) ilk UC kapiyi birden geciyor."
          % (n, a_uc, 100.0 * a_uc / n))
    print("   Kalan uc kapi (blowoff · long_veto · taker>=1.0) BUNDAN SONRA geliyor.")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
