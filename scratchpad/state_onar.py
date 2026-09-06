#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STATE ONARIMI — kapatilan pozisyonlari acik listesinden dusur (2026-09-06)

SEBEP: testbot.pozisyon_kapat KAYDI yazar ve equity'yi gunceller ama pozisyonu
   st["acik_pozisyonlar"]'dan SILMEZ — silme isini CAGIRAN yapiyor
   (yonet_acik_pozisyonlar 'kalanlar' listesi kurup atiyor, testbot.py:1092).
   defterleri_kapat.py bunu bilmiyordu: kayitlar yazildi, liste dolu kaldi.

RISK: liste dolu kalirsa zamanlanmis gorev ayni pozisyonu IKINCI KEZ kapatir
   = cift P&L. Gorevler bu yuzden ONCE devre disi birakildi; cift kapanis
   OLMADIGI dogrulandi.

BU BETIK: yalnizca ELLE_KAPAT_TEMIZ_SAYFA kaydi OLAN pozisyonlari listeden
   duser. Baska hicbir alana dokunmaz. equity'ye DOKUNMAZ (zaten islenmis).

Varsayilan KURU KOSUM. --uygula ile yazar.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, sys, argparse

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)

SEBEP = "ELLE_KAPAT_TEMIZ_SAYFA"
DEFTERLER = (("testbot", "testbot_state.json", "testbot_islemler.jsonl"),
             ("golge", "golge_state.json", "golge_islemler.jsonl"),
             ("ayna", "ayna_state.json", "ayna_islemler.jsonl"),
             ("defter2", "defter2_state.json", "defter2_islemler.jsonl"),
             ("defter3", "defter3_state.json", "defter3_islemler.jsonl"))


def yukle(p):
    try:
        with open(os.path.join(KOK, p), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def kaydet(p, st):
    yol = os.path.join(KOK, p)
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
    os.replace(tmp, yol)


def kapanan_idler(df):
    """ELLE_KAPAT kaydi olan id'ler."""
    out = set()
    p = os.path.join(KOK, df)
    if not os.path.exists(p):
        return out
    for l in open(p, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            k = json.loads(l)
        except Exception:
            continue
        if k.get("sebep") == SEBEP:
            out.add(k.get("id"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uygula", action="store_true")
    a = ap.parse_args()
    print("=" * 84)
    print("STATE ONARIMI — %s" % ("UYGULAMA" if a.uygula else "KURU KOSUM"))
    print("=" * 84)
    print()

    for ad, sf, df in DEFTERLER:
        st = yukle(sf)
        if not st:
            continue
        idler = kapanan_idler(df)
        ap_ = st.get("acik_pozisyonlar") or []
        dusecek = [p for p in ap_ if p.get("id") in idler]
        kalacak = [p for p in ap_ if p.get("id") not in idler]
        print("   %-9s acik=%d  ELLE_KAPAT kaydi olan=%d  ->  dusecek=%d kalacak=%d"
              % (ad, len(ap_), len(idler), len(dusecek), len(kalacak)))
        for p in dusecek:
            print("        id=%s %s %s" % (p.get("id"), p.get("sym"), p.get("yon")))
        for p in kalacak:
            print("        🔴 KALIYOR (kapanis kaydi YOK): id=%s %s"
                  % (p.get("id"), p.get("sym")))
        if a.uygula and dusecek:
            st["acik_pozisyonlar"] = kalacak
            kaydet(sf, st)
            print("        -> yazildi")
    print()

    if not a.uygula:
        print("KURU KOSUM — diske yazim YOK.")
        return

    print("### DOGRULAMA")
    kalan = 0
    for ad, sf, df in DEFTERLER:
        st = yukle(sf)
        if not st:
            continue
        n = len(st.get("acik_pozisyonlar") or [])
        kalan += n
        print("   %-9s durum=%-24s acik=%d equity=%.2f"
              % (ad, st.get("durum"), n, st.get("equity", 0)))
    b = yukle("benim_state.json")
    if b:
        print("   %-9s durum=%-24s acik=%d equity=%.2f"
              % ("benim", b.get("durum"), len(b.get("acik_pozisyonlar") or []),
                 b.get("equity", 0)))
    print()
    print("   KALAN ACIK POZISYON: %d  ->  %s"
          % (kalan, "TEMIZ SAYFA" if kalan == 0 else "🔴 HALA VAR"))


if __name__ == "__main__":
    main()
