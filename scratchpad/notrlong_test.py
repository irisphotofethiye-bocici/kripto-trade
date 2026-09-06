#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""notrlong.py GUVENLI TESTI (2026-09-06)

🔴 CLAUDE.md: "Sahte veriyle test ederken diske yazan HER yolu stub'la —
   'guvenli fiyat secmek' yetmez." 2026-08-15'te sahte mum fiyati gercek stop
   esigine carpti ve deftere 7 SAHTE LIKIDASYON yazildi.

Stub'lananlar: _append_jsonl · _save_state · pozisyon_kapat · pozisyon_liq ·
   pozisyon_kismi_tp1 · telegram_gonder · toast_gonder · notrlong.kaydet ·
   notrlong._tg · ag cagrilari (fiyat_fapi/olcucu.measure)

Testin sonunda "diske yazim: YOK" DOGRULANIR (dosya sistemi taranir).
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, sys, glob

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)

import testbot
import notrlong

HATA = []
YAZIM = []


def kontrol(ad, kosul, detay=""):
    print("   %-52s %s%s" % (ad, "✅" if kosul else "🔴 DUSTU",
                             ("  " + detay) if detay else ""))
    if not kosul:
        HATA.append(ad)


def _yakala(etiket):
    def f(*a, **kw):
        YAZIM.append((etiket, a[:1]))
        return None
    return f


def stubla():
    """Diske yazan / aga giden HER yolu kes."""
    testbot._append_jsonl = _yakala("_append_jsonl")
    testbot._save_state = _yakala("_save_state")
    testbot.pozisyon_kapat = _yakala("pozisyon_kapat")
    testbot.pozisyon_liq = _yakala("pozisyon_liq")
    testbot.pozisyon_kismi_tp1 = _yakala("pozisyon_kismi_tp1")
    testbot.telegram_gonder = _yakala("telegram")
    testbot.toast_gonder = _yakala("toast")
    testbot.fiyat_fapi = lambda s: 1.0
    notrlong.kaydet = _yakala("notrlong.kaydet")
    notrlong._tg = _yakala("notrlong._tg")


def main():
    print("=" * 84)
    print("notrlong.py GUVENLI TESTI")
    print("=" * 84)
    print()
    once = set(glob.glob(os.path.join(KOK, "*")))
    # Gercek turdan kalma dosyalar MESRU olabilir; onemli olan bu TESTIN
    # onlari BUYUTMEMESI. O yuzden boyutlar da not ediliyor.
    izlenen = (glob.glob(os.path.join(KOK, "notrlong_*")) +
               glob.glob(os.path.join(KOK, "*_islemler.jsonl")) +
               glob.glob(os.path.join(KOK, "*_state.json")) +
               [os.path.join(KOK, "veto_log.jsonl"),
                os.path.join(KOK, "testbot_aday_arsiv.jsonl")])
    boyut_once = dict((p, os.path.getsize(p)) for p in izlenen if os.path.exists(p))
    stubla()

    # ---------------------------------------------------------------
    print("### 1) _defterde — DORT takas yapiliyor ve GERI ALINIYOR mu?")
    d0 = (testbot._DEFTER, testbot.telegram_gonder,
          testbot.toast_gonder, testbot.VETO_LOGF)
    ic = {}

    def gozle():
        ic["defter"] = testbot._DEFTER
        ic["veto"] = testbot.VETO_LOGF
        ic["tg_sessiz"] = (testbot.telegram_gonder is notrlong._sessiz)
        return "ok"

    notrlong._defterde(gozle)
    kontrol("takas sirasinda _DEFTER notrlong defterine bakiyor",
            ic["defter"].endswith("notrlong_islemler.jsonl"))
    kontrol("takas sirasinda VETO_LOGF notrlong'a bakiyor",
            ic["veto"].endswith("notrlong_veto.jsonl"))
    kontrol("takas sirasinda telegram SUSTURULMUS", ic["tg_sessiz"])
    d1 = (testbot._DEFTER, testbot.telegram_gonder,
          testbot.toast_gonder, testbot.VETO_LOGF)
    kontrol("finally ile DORDU DE geri alindi", d0 == d1)

    def patla():
        raise RuntimeError("test")
    try:
        notrlong._defterde(patla)
    except RuntimeError:
        pass
    kontrol("HATA firlasa bile geri aliniyor",
            d0 == (testbot._DEFTER, testbot.telegram_gonder,
                   testbot.toast_gonder, testbot.VETO_LOGF))
    print()

    # ---------------------------------------------------------------
    print("### 2) sabit_hedef_kur — dogru alanlar, dogru degerler")
    st = notrlong.yeni_state()
    st["acik_pozisyonlar"].append({"sym": "X", "yon": "LONG", "giris": 100.0,
                                   "miktar": 1, "stop": 95.0, "tp1": 103.0,
                                   "tp2": 106.0, "tp1_alindi": False})
    notrlong.sabit_hedef_kur(st, "LONG")
    p = st["acik_pozisyonlar"][-1]
    kontrol("cikis_modu = sabit_hedef", p.get("cikis_modu") == "sabit_hedef")
    kontrol("tp2 = giris x 1,10 (LONG)", abs(p["tp2"] - 110.0) < 1e-9,
            "tp2=%.4f" % p["tp2"])
    kontrol("tp1_alindi = True (kismi kar KAPALI)", p.get("tp1_alindi") is True)
    kontrol("tp1 = tp2 (kismi kar yolu kapali)", p["tp1"] == p["tp2"])
    kontrol("kaynak = notrlong", p.get("kaynak") == "notrlong")
    # SHORT aynasi
    st2 = notrlong.yeni_state()
    st2["acik_pozisyonlar"].append({"sym": "Y", "yon": "SHORT", "giris": 100.0})
    notrlong.sabit_hedef_kur(st2, "SHORT")
    kontrol("SHORT aynasi tp2 = giris x 0,90",
            abs(st2["acik_pozisyonlar"][-1]["tp2"] - 90.0) < 1e-9)
    print()

    # ---------------------------------------------------------------
    print("### 3) fren_kontrol — %25 dususte DURUR, oncesinde DURMAZ")
    for eq, bek in ((7600.0, "AKTIF"), (7500.0, "DURDU"), (7000.0, "DURDU")):
        s = notrlong.yeni_state()
        s["equity"] = eq
        notrlong.fren_kontrol(s)
        kontrol("equity %.0f -> %s" % (eq, bek), s["durum"] == bek,
                "gercek=%s" % s["durum"])
    print()

    # ---------------------------------------------------------------
    print("### 4) REJIM ZORLANIYOR mu + YALNIZ LONG + SKOR KAPISI")
    gorulen_rejim = []
    kararlar = {}

    def sahte_karar_yon(rejim_ad, r, pillar, kf, veto_out=None, **kw):
        gorulen_rejim.append(rejim_ad)
        return kararlar.get(r["sym"])

    acilanlar = []

    def sahte_ac(st_, sym, yon, r, pillar, sebep, **kw):
        acilanlar.append((sym, yon, sebep))
        st_["acik_pozisyonlar"].append({"sym": sym, "yon": yon, "giris": 100.0})
        return True

    testbot.karar_yon = sahte_karar_yon
    testbot.yeni_giris_ac = sahte_ac

    rows = [{"sym": "AAA", "score": 60.0, "chg24": 5},
            {"sym": "BBB", "score": 40.0, "chg24": 5},     # skor kapisinin altinda
            {"sym": "CCC", "score": 70.0, "chg24": 5}]     # SHORT karari
    kararlar = {"AAA": ("LONG", "ANINDA", "test"),
                "BBB": ("LONG", "ANINDA", "test"),
                "CCC": ("SHORT", "ANINDA", "test")}
    pil = {s["sym"]: {} for s in rows}
    bag = {"para_cikis": False, "para_durgun": False, "btc_pay": None}

    s1 = notrlong.yeni_state()
    acilanlar.clear()
    notrlong.giris_ara(s1, rows, pil, bag)
    alinan = [x[0] for x in acilanlar]

    kontrol("karar_yon'a HER ZAMAN 'NOTR' gecildi",
            gorulen_rejim and all(x == "NOTR" for x in gorulen_rejim),
            "gorulen=%s" % sorted(set(gorulen_rejim)))
    kontrol("SHORT karari ATILDI (CCC alinmadi)", "CCC" not in alinan,
            "alinan=%s" % alinan)
    # [DEGISTI 2026-09-06] Eski iddia "N2 skor kapisi BBB'yi eler" idi.
    # Skor kapisi KALDIRILDI (on-kayit bolum 11) -> dogru iddia TERSI:
    # dusuk skorlu aday da ALINMALI, cunku EK kapi yok.
    kontrol("EK skor kapisi YOK -> BBB (skor 40) ALINDI", "BBB" in alinan,
            "alinan=%s" % alinan)
    kontrol("yuksek skorlu AAA da alindi", "AAA" in alinan)
    kontrol("SKOR_KAPISI sabiti koddan KALKTI",
            not hasattr(notrlong, "SKOR_KAPISI"))
    kontrol("KOLLAR sabiti koddan KALKTI", not hasattr(notrlong, "KOLLAR"))
    print()

    # ---------------------------------------------------------------
    print("### 5) FREN aktifken giris ARANMIYOR")
    s3 = notrlong.yeni_state()
    s3["durum"] = "DURDU"
    acilanlar.clear()
    n = notrlong.giris_ara(s3, rows, pil, bag)
    kontrol("durum=DURDU -> 0 giris", n == 0 and not acilanlar)

    print("### 6) MAKS_POZ dolu iken giris ARANMIYOR (cikislar etkilenmez)")
    s4 = notrlong.yeni_state()
    s4["acik_pozisyonlar"] = [{"sym": "Z%d" % i} for i in range(notrlong.MAKS_POZ)]
    acilanlar.clear()
    n = notrlong.giris_ara(s4, rows, pil, bag)
    kontrol("acik == MAKS_POZ -> 0 giris", n == 0 and not acilanlar)
    print()

    # ---------------------------------------------------------------
    print("### 7) 🔴 DISKE YAZIM KONTROLU")
    sonra = set(glob.glob(os.path.join(KOK, "*")))
    yeni_dosya = sonra - once
    kontrol("kok dizinde YENI DOSYA yok", not yeni_dosya,
            str(sorted(os.path.basename(x) for x in yeni_dosya)) if yeni_dosya else "")
    # NOT: gercek turdan kalma dosyalar MESRU; onemli olan bu TESTIN onlari
    # BUYUTMEMESI (yeni satir yazmamasi).
    buyuyen = []
    for p, b in boyut_once.items():
        if os.path.exists(p) and os.path.getsize(p) != b:
            buyuyen.append("%s %d->%d" % (os.path.basename(p), b, os.path.getsize(p)))
    kontrol("izlenen dosyalarin HICBIRI buyumedi (%d dosya)" % len(boyut_once),
            not buyuyen, "; ".join(buyuyen) if buyuyen else "")
    kontrol("BOTUN kendi defterlerine yazim YOK",
            not any("testbot_" in x or "veto_log" in x for x in buyuyen))
    kontrol("stub'lanan yazim yollari cagrilmadi ya da YAKALANDI",
            all(e[0] in ("_append_jsonl", "_save_state", "pozisyon_kapat",
                         "pozisyon_liq", "pozisyon_kismi_tp1", "telegram",
                         "toast", "notrlong.kaydet", "notrlong._tg")
                for e in YAZIM),
            "yakalanan=%s" % sorted(set(e[0] for e in YAZIM)))
    print()

    print("=" * 84)
    if HATA:
        print("🔴 %d TEST DUSTU: %s" % (len(HATA), ", ".join(HATA)))
        sys.exit(1)
    print("TUM TESTLER GECTI")
    print("diske yazim: YOK")


if __name__ == "__main__":
    main()
