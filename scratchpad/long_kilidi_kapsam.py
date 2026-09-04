#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LONG KILIDI — BOGA rejiminde SHORT istisnasi ne kadar dar?

testbot.karar_yon, rejim BOGA iken SHORT'u yalniz su kosulda aciyor:
    stage == "BASLIYOR"  VE  smart == "SHORT"  VE  taker <= 1.0
LONG dali ise cok daha genis: skor >= esik  VE  smart != "SHORT"  VE  pos <= 0.85

Bu betik aday arsivinden BOGA satirlarini sayar ve iki dalin KAPSAMINI kiyaslar.
Karar vermez, kural onermez — yalnizca "kilit" sozunun ne kadar gercek oldugunu olcer.

⚠️ `rejim` alani 2026-07-22'de tanim degistirdi (CLAUDE.md). Bu sayim yalnizca
   O TARIHTEN SONRAsina bakar, dolayisiyla kirilma etkilenmiyor.
🔴 Arsiv context'e YUKLENMEZ — burada toplanip yalniz ozet basilir.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARSIV = os.path.join(PROJE, "testbot_aday_arsiv.jsonl")
BASLANGIC = "2026-08-24"          # botun son SHORT'undan sonrasi
TANIM_DEGISIMI = "2026-07-22"     # rejim alaninin anlam kirilmasi


def main():
    print("LONG KILIDI — BOGA'da SHORT istisnasi ne kadar dar?")
    print("=" * 92)
    print("kaynak: testbot_aday_arsiv.jsonl (context'e YUKLENMEDI, burada toplandi)")
    print("pencere: %s'ten itibaren  ·  rejim tanim kirilmasi (%s) SONRASI"
          % (BASLANGIC, TANIM_DEGISIMI))

    n = 0
    rejim = collections.Counter()
    boga = []
    for l in open(ARSIV, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        ts = str(r.get("ts") or "")
        if ts[:10] < BASLANGIC:
            continue
        n += 1
        rj = str(r.get("rejim") or "?")
        rejim[rj] += 1
        if rj.upper().startswith("BOGA") or rj.upper().startswith("TAM_BOGA"):
            boga.append(r)

    print("\naday satiri (pencere ici): %d" % n)
    print("rejim dagilimi: %s" % dict(rejim.most_common(6)))
    if not boga:
        print("BOGA satiri yok — sayim yapilamadi")
        return

    print("\n" + "=" * 92)
    print("BOGA satiri: %d" % len(boga))
    print("-" * 92)

    def sayi(f):
        return sum(1 for r in boga if f(r))

    st = collections.Counter(str(r.get("stage")) for r in boga)
    sm = collections.Counter(str(r.get("smart")) for r in boga)
    print("  stage dagilimi : %s" % dict(st.most_common(6)))
    print("  smart dagilimi : %s" % dict(sm.most_common(6)))

    # --- SHORT istisnasinin uc sarti, TEK TEK ve BIRLIKTE
    c1 = lambda r: str(r.get("stage")) == "BASLIYOR"
    c2 = lambda r: str(r.get("smart")) == "SHORT"
    c3 = lambda r: (r.get("taker") is None) or (float(r.get("taker") or 1.0) <= 1.0)
    print("\n  SHORT ISTISNASI — uc sart:")
    print("    %-34s %6d  (%%%.1f)" % ("stage == BASLIYOR", sayi(c1), 100.0 * sayi(c1) / len(boga)))
    print("    %-34s %6d  (%%%.1f)" % ("smart == SHORT", sayi(c2), 100.0 * sayi(c2) / len(boga)))
    print("    %-34s %6d  (%%%.1f)" % ("taker <= 1.0", sayi(c3), 100.0 * sayi(c3) / len(boga)))
    ucu = sayi(lambda r: c1(r) and c2(r) and c3(r))
    ikisi = sayi(lambda r: c1(r) and c2(r))
    print("    %-34s %6d  (%%%.2f)" % ("BASLIYOR + smart-SHORT", ikisi, 100.0 * ikisi / len(boga)))
    print("    %-34s %6d  (%%%.2f)   <== SHORT ACILABILEN" % ("UCU BIRDEN", ucu, 100.0 * ucu / len(boga)))

    # --- LONG dalinin kapsami
    l1 = lambda r: (r.get("score") or 0) >= 45
    l2 = lambda r: str(r.get("smart")) != "SHORT"
    l3 = lambda r: (r.get("pos") is None) or (float(r.get("pos") or 0.5) <= 0.85)
    lo = sayi(lambda r: l1(r) and l2(r) and l3(r))
    print("\n  LONG DALI — uc sart (skor esigi 45 varsayildi, config'ten okunmadi):")
    print("    %-34s %6d  (%%%.1f)" % ("skor >= 45", sayi(l1), 100.0 * sayi(l1) / len(boga)))
    print("    %-34s %6d  (%%%.1f)" % ("smart != SHORT", sayi(l2), 100.0 * sayi(l2) / len(boga)))
    print("    %-34s %6d  (%%%.1f)" % ("pos <= 0.85", sayi(l3), 100.0 * sayi(l3) / len(boga)))
    print("    %-34s %6d  (%%%.2f)   <== LONG ACILABILEN" % ("UCU BIRDEN", lo, 100.0 * lo / len(boga)))

    print("\n" + "=" * 92)
    print("KAPSAM ORANI")
    print("-" * 92)
    if ucu:
        print("  LONG adayi / SHORT adayi = %.1f kat" % (lo / ucu))
    else:
        print("  SHORT acilabilen aday: SIFIR -> oran tanimsiz (kilit TAM)")
    print("  Yani BOGA rejiminde bot SHORT'u bir ISTISNA olarak tutuyor;")
    print("  istisna saglanmadigi surece acabildigi TEK yon LONG.")

    print("\n  ⚠️ Bu sayim KAPSAM olcer, KARLILIK degil. 'LONG kaybettiriyor'")
    print("     hukmu baska uc olcumden geliyor (hakem raporu s.4).")
    print("\nbot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
