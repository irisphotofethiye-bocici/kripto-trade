#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEFTER IZOLASYON TESTI (2026-08-13)

NEDEN VAR: testbot.yeni_giris_ac / pozisyon_kapat BOTA OZEL DEGIL — golge.py, benim.py
ve ayna.py de ayni fonksiyonlari cagiriyor. Bu fonksiyonlarin YAN ETKILERI (Telegram
bildirimi, ayna kopyalama, defter yolu) cagiran kim olursa olsun tetikleniyor.

BU YUZDEN AYNI HATA IKI KEZ CIKTI:
  1) 2026-08-12: _aynala kancasi korumasizdi -> golge'nin LONG girisleri aynaya dustu.
  2) 2026-08-12: benim.py bildirimleri susturmuyordu -> kullanici panelden BTW acti,
     Telegram'a "[TESTBOT] GIRIS BTW" dustu ama pozisyon BOTTA YOKTU.

Ucuncusu olmasin diye bu test dort defterin izolasyonunu birden dogrular.
GERCEK DOSYALARA DOKUNMAZ — yan etkiler sahte fonksiyonlarla degistirilir.
"""
import os, sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
import testbot, golge, benim, ayna

hata = []


def esit(ad, a, b):
    ok = a == b
    print(f"  {'GECTI' if ok else 'KALDI'}  {ad:52} {a!r} {'==' if ok else '!='} {b!r}")
    if not ok:
        hata.append(ad)


def olcum(modul, ad):
    """modul._defterde(...) icinde yan etkiler ne yapiyor?"""
    izler = {"tg": [], "toast": [], "ayna": [], "defter": []}
    o_tg, o_toast = testbot.telegram_gonder, testbot.toast_gonder
    o_ayna = ayna.aynala
    testbot.telegram_gonder = lambda m, olay=None: izler["tg"].append(olay or "?")
    testbot.toast_gonder = lambda b, m, olay=None: izler["toast"].append(olay or "?")
    ayna.aynala = lambda pos: izler["ayna"].append(pos.get("sym")) or True

    def icerde():
        izler["defter"].append(testbot._islem_defteri())
        testbot.telegram_gonder("test", olay="giris")
        testbot.toast_gonder("t", "test", olay="giris")
        testbot._aynala({"sym": "TEST", "id": 99})
    try:
        modul._defterde(icerde)
    finally:
        testbot.telegram_gonder, testbot.toast_gonder = o_tg, o_toast
        ayna.aynala = o_ayna
    return izler


def main():
    print("DEFTER IZOLASYON TESTI — yan etkiler dogru deftere mi gidiyor?\n")
    print("1) BOT (dogrudan cagri) — bildirim GITMELI, ayna KOPYALAMALI")
    izler = {"tg": [], "ayna": []}
    o_tg, o_ayna = testbot.telegram_gonder, ayna.aynala
    testbot.telegram_gonder = lambda m, olay=None: izler["tg"].append(olay or "?")
    ayna.aynala = lambda pos: izler["ayna"].append(pos.get("sym")) or True
    try:
        testbot.telegram_gonder("test", olay="giris")
        testbot._aynala({"sym": "TEST", "id": 99})
        esit("bot: bildirim gonderiliyor", izler["tg"], ["giris"])
        esit("bot: ayna kopyaliyor", izler["ayna"], ["TEST"])
    finally:
        testbot.telegram_gonder, ayna.aynala = o_tg, o_ayna

    for modul, ad, defter in ((golge, "GOLGE", golge.ISLEMLERF),
                              (benim, "BENIM", benim.ISLEMLERF),
                              (ayna, "AYNA", ayna.ISLEMLERF)):
        print(f"\n2) {ad} — bildirim GITMEMELI, ayna KOPYALAMAMALI, defter KENDISI")
        iz = olcum(modul, ad)
        esit(f"{ad}: Telegram susturulmus", iz["tg"], [])
        esit(f"{ad}: toast susturulmus", iz["toast"], [])
        esit(f"{ad}: aynaya kopyalanmiyor", iz["ayna"], [])
        esit(f"{ad}: kendi defterine yaziyor",
             os.path.basename(iz["defter"][0]), os.path.basename(defter))

    print("\n3) GERI ALMA — cagrilar sonrasi bot normale donmus mu?")
    esit("defter yolu geri alindi", testbot._DEFTER, None)
    esit("telegram_gonder geri alindi", testbot.telegram_gonder.__name__ != "_sessiz", True)
    esit("toast_gonder geri alindi", testbot.toast_gonder.__name__ != "_sessiz", True)

    print(f"\n{'HEPSI GECTI' if not hata else 'KALAN: ' + ', '.join(hata)}")
    return 1 if hata else 0


if __name__ == "__main__":
    sys.exit(main())
