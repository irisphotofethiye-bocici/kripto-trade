# -*- coding: utf-8 -*-
"""Giris anindaki emir defteri derinligi — dogrulama testi (2026-08-17).

CLAUDE.md "TEST YAZARKEN": diske yazan HER yol stub'lanir, sonunda "diske yazim: YOK"
dogrulanir. Ag cagrisi (_get) da stub'lanir — GERCEK borsaya istek GITMEZ.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import testbot

YAZIM = []
testbot._append_jsonl = lambda p, o: YAZIM.append(("jsonl", p, o))
testbot._save_state = lambda *a, **k: YAZIM.append(("state", a, k))
testbot.telegram_gonder = lambda *a, **k: None
testbot.toast_gonder = lambda *a, **k: None

SAHTE_DEFTER = {}
CAGRI = []
def _sahte_get(u, *a, **k):
    CAGRI.append(u)
    if "/depth" in u:
        if SAHTE_DEFTER is None:
            raise RuntimeError("ag hatasi")
        return SAHTE_DEFTER
    raise RuntimeError("beklenmeyen uc nokta: " + u)
testbot._get = _sahte_get

hata = 0
def kontrol(ad, kosul, detay=""):
    global hata
    print(("  OK   " if kosul else "  HATA ") + ad + ("  " + detay if detay else ""))
    if not kosul:
        hata += 1

print("=" * 68)
print("1) SHORT bids tarafini yer, slipaj POZITIF (aleyhte)")
# bids: 100 usdt'lik satis -> ilk seviye 10.0 x 5 = 50 usdt, sonra 9.9 x 10 = 99
SAHTE_DEFTER = {"bids": [["10.0", "5"], ["9.9", "10"], ["9.8", "100"]],
                "asks": [["10.1", "5"], ["10.2", "10"]]}
d = testbot.defter_derinlik("TEST", "SHORT", 100.0)
# 50 usdt @10.0 -> 5 adet ; 50 usdt @9.9 -> 5.0505 adet ; toplam 10.0505 adet, 100 usdt
# vwap = 100/10.0505 = 9.9497 ; slipaj = (10 - 9.9497)/10 = %0.503
kontrol("en_iyi = ilk bid", d and d["en_iyi"] == 10.0, str(d and d["en_iyi"]))
kontrol("slipaj pozitif (aleyhte)", d and d["slipaj_pct"] > 0, str(d and d["slipaj_pct"]))
kontrol("slipaj ~%0.50", d and abs(d["slipaj_pct"] - 0.503) < 0.01, str(d and d["slipaj_pct"]))
kontrol("defter yetti", d and d["yetersiz"] is False)

print()
print("2) LONG asks tarafini yer (yon ayrimi)")
d = testbot.defter_derinlik("TEST", "LONG", 100.0)
kontrol("en_iyi = ilk ask", d and d["en_iyi"] == 10.1, str(d and d["en_iyi"]))
kontrol("slipaj pozitif", d and d["slipaj_pct"] > 0, str(d and d["slipaj_pct"]))

print()
print("3) DERIN defter -> slipaj ~0 (buyuk coin)")
SAHTE_DEFTER = {"bids": [["10.0", "100000"]], "asks": [["10.01", "100000"]]}
d = testbot.defter_derinlik("TEST", "SHORT", 500.0)
kontrol("slipaj ~0", d and abs(d["slipaj_pct"]) < 1e-6, str(d and d["slipaj_pct"]))

print()
print("4) SIG defter -> 'yetersiz' bayragi (slipaj ALT SINIR)")
SAHTE_DEFTER = {"bids": [["10.0", "1"]], "asks": [["10.1", "1"]]}
d = testbot.defter_derinlik("TEST", "SHORT", 100000.0)
kontrol("yetersiz=True", d and d["yetersiz"] is True)
kontrol("defter_usdt_20 kaydedildi", d and d["defter_usdt_20"] == 10.0, str(d and d["defter_usdt_20"]))

print()
print("5) HATA yollari -> None, giris ETKILENMEZ")
SAHTE_DEFTER = None
kontrol("ag hatasi -> None", testbot.defter_derinlik("TEST", "SHORT", 100.0) is None)
SAHTE_DEFTER = {"bids": [], "asks": []}
kontrol("bos defter -> None", testbot.defter_derinlik("TEST", "SHORT", 100.0) is None)
SAHTE_DEFTER = {}
kontrol("alan yok -> None", testbot.defter_derinlik("TEST", "SHORT", 100.0) is None)

print()
print("6) POZISYON BASINA TEK cagri (aday dongusune girmiyor)")
CAGRI.clear()
SAHTE_DEFTER = {"bids": [["10.0", "1000"]], "asks": [["10.1", "1000"]]}
testbot.defter_derinlik("TEST", "SHORT", 100.0)
kontrol("1 cagri", len(CAGRI) == 1, f"n={len(CAGRI)}")
kontrol("uc nokta /depth limit=20", "/fapi/v1/depth" in CAGRI[0] and "limit=20" in CAGRI[0], CAGRI[0])

print()
print("7) Kapanis kaydinda alan tasiniyor mu")
KAYIT = []
testbot._append_jsonl = lambda p, o: (KAYIT.append(o), YAZIM.append(("jsonl", p, o)))
st = {"equity": 10000.0, "kumulatif_funding": 0.0, "cooldown": {}}
pos = {"id": 1, "sym": "TEST", "yon": "SHORT", "giris": 1.0, "miktar": 100.0,
       "marjin": 100.0, "kaldirac": 3, "risk_usdt": 50.0, "likidasyon": 2.0,
       "giris_ts": testbot.now_iso(), "tp1_alindi": False, "cikis_modu": "sabit_hedef",
       "funding_toplam": 0.0, "funding_yazilan": 0.0,
       "derinlik_giriste": {"slipaj_pct": 0.42, "yetersiz": False}}
testbot.pozisyon_kapat(st, pos, 0.9, "TP2")
k = KAYIT[-1]
kontrol("derinlik_giriste kayitta", k.get("derinlik_giriste") is not None)
kontrol("slipaj degeri korundu", k["derinlik_giriste"]["slipaj_pct"] == 0.42)
kontrol("funding_usdt hala var", "funding_usdt" in k)

print()
print("8) Derinliksiz pozisyon (eski/olculemedi) -> None, cokme yok")
KAYIT.clear()
pos2 = dict(pos); pos2.pop("derinlik_giriste"); pos2["id"] = 2
pos2["funding_toplam"] = 0.0; pos2["funding_yazilan"] = 0.0
testbot.pozisyon_kapat(st, pos2, 0.9, "TP2")
kontrol("None yazildi", KAYIT[-1].get("derinlik_giriste") is None)

print()
print("=" * 68)
gercek = [y for y in YAZIM if y[0] == "state"]
print(f"diske yazim (state): {'YOK' if not gercek else 'VAR — ' + str(gercek)}")
print(f"gercek borsa cagrisi: YOK (_get stub'li, {len(CAGRI)} sahte cagri)")
print(f"SONUC: {'HEPSI GECTI' if hata == 0 else str(hata) + ' HATA'}")
sys.exit(1 if hata else 0)
