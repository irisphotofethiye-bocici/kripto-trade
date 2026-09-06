#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESKI DEFTERLERI KAPAT — acik pozisyonlari ELLE kapatir (2026-09-06)

KULLANICI KARARI (2026-09-06): "acik tek poz kalmis zaten onu da kapat, diger
butun defterleri kapat, temiz bir sayfa olsun."

⚠️ DUZELTME KULLANICIYA BILDIRILDI: acik pozisyon 1 DEGIL 5 (uc ayri islem,
   bes kayit) — AZTEC testbot+ayna, VANA defter2+defter3, NEAR golge.

🔴 BU BIR ELLE MUDAHALEDIR ve olcum pencerelerini BITIRIR.
   CLAUDE.md: "olcum penceresi bes kararin hakemi — icine elle mudahale girerse
   hakem kalmaz." Kullanici bunu bilerek istedi; kapanis kayitlarina
   sebep="ELLE_KAPAT_TEMIZ_SAYFA" yaziliyor ki sonraki her cozumleme bu
   islemlerin DOGAL kapanmadigini gorebilsin.

Her defter KENDI dosyasina yazar (_DEFTER takasi). Cikis fiyati PIYASA.

Varsayilan KURU KOSUM. Gercekten kapatmak icin --uygula.
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

import testbot

SEBEP = "ELLE_KAPAT_TEMIZ_SAYFA"

# defter adi -> (state dosyasi, islem defteri, veto defteri)
DEFTERLER = {
    "testbot": ("testbot_state.json", "testbot_islemler.jsonl", "veto_log.jsonl"),
    "golge":   ("golge_state.json",   "golge_islemler.jsonl",   "golge_veto.jsonl"),
    "ayna":    ("ayna_state.json",    "ayna_islemler.jsonl",    "ayna_veto.jsonl"),
    "benim":   ("benim_state.json",   "benim_islemler.jsonl",   "benim_veto.jsonl"),
    "defter2": ("defter2_state.json", "defter2_islemler.jsonl", "defter2_veto.jsonl"),
    "defter3": ("defter3_state.json", "defter3_islemler.jsonl", "defter3_veto.jsonl"),
}


def _sessiz(*a, **kw):
    return None


def yukle(p):
    try:
        with open(os.path.join(KOK, p), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def kaydet(p, st):
    """ATOMIK — CLAUDE.md kurali (golge.py duz json.dump kullaniyor, 314 $ saptirmisti)."""
    yol = os.path.join(KOK, p)
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
    os.replace(tmp, yol)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uygula", action="store_true",
                    help="GERCEKTEN kapat (varsayilan: kuru kosum)")
    a = ap.parse_args()

    print("=" * 88)
    print("ESKI DEFTERLERI KAPAT  —  %s" % ("UYGULAMA" if a.uygula else "KURU KOSUM"))
    print("=" * 88)
    if not a.uygula:
        print("(hicbir sey yazilmayacak; gercek kapanis icin --uygula)")
    print()

    plan = []
    for ad, (sf, df, vf) in DEFTERLER.items():
        st = yukle(sf)
        if not st:
            continue
        for pos in list(st.get("acik_pozisyonlar") or []):
            plan.append((ad, sf, df, vf, st, pos))

    if not plan:
        print("Acik pozisyon YOK — kapatilacak bir sey yok.")
        return

    print("### KAPATILACAKLAR")
    print("   %-9s %-10s %-6s %10s %10s %11s %s"
          % ("defter", "sembol", "yon", "giris", "anlik", "PnL $", "durum"))
    fiyatlar = {}
    toplam = 0.0
    for ad, sf, df, vf, st, pos in plan:
        sym = pos["sym"]
        if sym not in fiyatlar:
            fiyatlar[sym] = testbot.fiyat_fapi(sym)
        px = fiyatlar[sym] or pos["giris"]
        yi = 1 if pos["yon"] == "LONG" else -1
        pnl = (px - pos["giris"]) * pos["miktar"] * yi
        toplam += pnl
        print("   %-9s %-10s %-6s %10.6g %10.6g %+11.2f %s"
              % (ad, sym, pos["yon"], pos["giris"], px, pnl, st.get("durum")))
    print()
    print("   toplam gerceklesecek P&L: %+.2f $   (fiyat kaynagi: fapi anlik)" % toplam)
    print("   sebep etiketi: %s" % SEBEP)
    print()

    if not a.uygula:
        print("KURU KOSUM — diske yazim YOK.")
        return

    print("### UYGULANIYOR")
    eski = (testbot._DEFTER, testbot.telegram_gonder,
            testbot.toast_gonder, testbot.VETO_LOGF)
    kapandi = 0
    try:
        for ad, sf, df, vf, st, pos in plan:
            px = fiyatlar.get(pos["sym"]) or pos["giris"]
            # testbot KENDISI icin _DEFTER None olmali (kendi ISLEMLERF'ine yazsin)
            testbot._DEFTER = None if ad == "testbot" else os.path.join(KOK, df)
            testbot.VETO_LOGF = os.path.join(KOK, vf)
            testbot.telegram_gonder = _sessiz
            testbot.toast_gonder = _sessiz
            try:
                testbot.pozisyon_kapat(st, pos, px, SEBEP)
                # 🔴 ONARIM (2026-09-06, ilk kosumda ISIRDI): pozisyon_kapat
                #    KAYDI yazar ve equity'yi gunceller ama pozisyonu
                #    st["acik_pozisyonlar"]'dan SILMEZ — silmeyi CAGIRAN yapar
                #    (yonet_acik_pozisyonlar 'kalanlar' listesi kurup atiyor,
                #    testbot.py:1092). Silinmezse zamanlanmis gorev ayni
                #    pozisyonu IKINCI KEZ kapatir = cift P&L.
                try:
                    st["acik_pozisyonlar"].remove(pos)
                except ValueError:
                    pass
                kapandi += 1
                print("   %-9s %-10s kapatildi @ %.6g (listeden dusuruldu)"
                      % (ad, pos["sym"], px))
            except Exception as e:
                print("   %-9s %-10s HATA: %s" % (ad, pos["sym"], str(e)[:70]))
    finally:
        (testbot._DEFTER, testbot.telegram_gonder,
         testbot.toast_gonder, testbot.VETO_LOGF) = eski

    # state'leri yaz (her defter bir kez)
    yazildi = set()
    for ad, sf, df, vf, st, pos in plan:
        if sf in yazildi:
            continue
        st["durum"] = "KAPANDI_TEMIZ_SAYFA"
        kaydet(sf, st)
        yazildi.add(sf)
        print("   state yazildi: %-22s durum=KAPANDI_TEMIZ_SAYFA acik=%d"
              % (sf, len(st.get("acik_pozisyonlar") or [])))

    print()
    print("### DOGRULAMA")
    kalan = 0
    for ad, (sf, df, vf) in DEFTERLER.items():
        st = yukle(sf)
        if not st:
            continue
        n = len(st.get("acik_pozisyonlar") or [])
        kalan += n
        print("   %-9s durum=%-22s acik=%d" % (ad, st.get("durum"), n))
    print()
    print("   kapatilan: %d  ·  KALAN ACIK: %d  ->  %s"
          % (kapandi, kalan, "TEMIZ" if kalan == 0 else "🔴 HALA ACIK VAR"))
    print()
    print("notrlong kasalarina DOKUNULMADI.")


if __name__ == "__main__":
    main()
