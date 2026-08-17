# -*- coding: utf-8 -*-
"""Pozisyon basina fonlama kaydi — dogrulama testi (2026-08-17).

CLAUDE.md "TEST YAZARKEN" kurali: diske yazan HER yol stub'lanir ve sonunda
"diske yazim: YOK" diye dogrulanir. Ag cagrisi da stub'lanir (funding_events_since).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import testbot

# ---- STUB: diske yazan / disa cikan HER yol -------------------------------------
YAZIM = []
testbot._append_jsonl = lambda p, o: YAZIM.append(("jsonl", p, o))
testbot._save_state = lambda *a, **k: YAZIM.append(("state", a, k))
testbot.telegram_gonder = lambda *a, **k: None
testbot.toast_gonder = lambda *a, **k: None

# ---- STUB: ag ------------------------------------------------------------------
SAHTE_OLAYLAR = []
testbot.funding_events_since = lambda sym, ms: list(SAHTE_OLAYLAR)

KAYITLAR = []          # gercek defter yerine buraya
_orij_append = testbot._append_jsonl
def _yakala(p, o):
    KAYITLAR.append(o); YAZIM.append(("jsonl", p, o))
testbot._append_jsonl = _yakala

hata = 0
def kontrol(ad, kosul, detay=""):
    global hata
    print(("  OK   " if kosul else "  HATA ") + ad + ("  " + detay if detay else ""))
    if not kosul:
        hata += 1


def yeni_pos(pid=1, miktar=1000.0, giris=1.0, yon="SHORT"):
    return {"id": pid, "sym": "TEST", "yon": yon, "giris": giris, "miktar": miktar,
            "marjin": 100.0, "kaldirac": 3, "risk_usdt": 50.0, "likidasyon": 2.0,
            "giris_ts": testbot.now_iso(), "son_funding_kontrol_ts": testbot.now_iso(),
            "tp1_alindi": False, "cikis_modu": "sabit_hedef",
            "funding_toplam": 0.0, "funding_yazilan": 0.0}


print("=" * 66)
print("1) funding_uygula pozisyona biriktiriyor mu")
st = {"equity": 10000.0, "kumulatif_funding": 0.0, "cooldown": {}}
pos = yeni_pos()
SAHTE_OLAYLAR = [{"rate": -0.001}, {"rate": -0.0005}]   # SHORT + negatif oran = ODER
testbot.funding_uygula(st, pos)
# notional = 1000 * 1.0 = 1000. SHORT isaret=-1. maliyet = 1000*(-0.001)*(-1) = +1.0
# equity -= 1.0 ; funding_toplam -= 1.0  -> toplam -1.5
kontrol("pozisyon biriktirdi", abs(pos["funding_toplam"] - (-1.5)) < 1e-9,
        f"funding_toplam={pos['funding_toplam']}")
kontrol("defter geneliyle AYNI isaret",
        abs(pos["funding_toplam"] - st["kumulatif_funding"]) < 1e-9,
        f"kumulatif={st['kumulatif_funding']}")
kontrol("equity ayrica dustu", abs(st["equity"] - 9998.5) < 1e-9, f"equity={st['equity']}")

print()
print("2) _funding_dilim: ikinci cagri CIFT SAYMAMALI")
d1 = testbot._funding_dilim(pos)
d2 = testbot._funding_dilim(pos)
kontrol("ilk dilim tam tutar", abs(d1 - (-1.5)) < 1e-9, f"d1={d1}")
kontrol("ikinci dilim SIFIR", abs(d2) < 1e-9, f"d2={d2}")

print()
print("3) Degisiklik ONCESI pozisyon -> None (uydurma 0.0 degil)")
eski = yeni_pos(pid=2)
del eski["funding_toplam"]; del eski["funding_yazilan"]
kontrol("bilinmiyor = None", testbot._funding_dilim(eski) is None)

print()
print("4) Mesru sifir ile 'bilinmiyor' ayriliyor mu")
sifir = yeni_pos(pid=3)
kontrol("hic fonlama gormemis pozisyon 0.0 (None DEGIL)",
        testbot._funding_dilim(sifir) == 0.0)

print()
print("4b) ESKI pozisyon fonlama gorunce ANAHTAR YARATILMAMALI (yarim sayi tuzagi)")
st_eski = {"equity": 10000.0, "kumulatif_funding": 0.0, "cooldown": {}}
eski2 = yeni_pos(pid=6)
del eski2["funding_toplam"]; del eski2["funding_yazilan"]
SAHTE_OLAYLAR = [{"rate": -0.001}]
testbot.funding_uygula(st_eski, eski2)
kontrol("anahtar yaratilmadi", "funding_toplam" not in eski2)
kontrol("defter geneli YINE DE isliyor", abs(st_eski["kumulatif_funding"] - (-1.0)) < 1e-9,
        f"kumulatif={st_eski['kumulatif_funding']}")
kontrol("kayitta bilinmiyor kalir", testbot._funding_dilim(eski2) is None)

print()
print("5) KISMI + TAM kapanis: dilimlerin TOPLAMI = pozisyon fonlamasi")
st2 = {"equity": 10000.0, "kumulatif_funding": 0.0, "cooldown": {}}
pos2 = yeni_pos(pid=4)
SAHTE_OLAYLAR = [{"rate": -0.001}]
testbot.funding_uygula(st2, pos2)                 # -1.0
KAYITLAR.clear()
testbot.pozisyon_kismi_tp1(st2, pos2, 0.9)        # yari kapanir, kayit 1
SAHTE_OLAYLAR = [{"rate": -0.002}]
testbot.funding_uygula(st2, pos2)                 # kalan yari: notional 500 -> -1.0
testbot.pozisyon_kapat(st2, pos2, 0.9, "TP2")     # kayit 2
dilimler = [k.get("funding_usdt") for k in KAYITLAR]
toplam = sum(d for d in dilimler if d is not None)
kontrol("iki kayit yazildi", len(KAYITLAR) == 2, f"kayit={len(KAYITLAR)}")
kontrol("dilimler toplami = funding_toplam",
        abs(toplam - pos2["funding_toplam"]) < 1e-6,
        f"dilimler={dilimler} toplam={round(toplam,4)} beklenen={round(pos2['funding_toplam'],4)}")
kontrol("defter geneliyle mutabik",
        abs(toplam - st2["kumulatif_funding"]) < 1e-6,
        f"kumulatif={round(st2['kumulatif_funding'],4)}")

print()
print("6) alan adi funding_usdt olmali (funding = ORAN, cakisma)")
k_son = KAYITLAR[-1]
kontrol("funding alani var", "funding_usdt" in k_son, f"funding={k_son.get('funding_usdt')}")
kontrol("sonuc_usdt fonlamadan bagimsiz",
        k_son["sonuc_usdt"] != k_son.get("funding_usdt"))

print()
print("7) Likidasyon yolunda da alan var mi")
st3 = {"equity": 10000.0, "kumulatif_funding": 0.0, "cooldown": {}}
pos3 = yeni_pos(pid=5)
SAHTE_OLAYLAR = [{"rate": -0.001}]
testbot.funding_uygula(st3, pos3)
KAYITLAR.clear()
testbot.pozisyon_liq(st3, pos3)
kontrol("likidasyon kaydinda funding var",
        KAYITLAR and KAYITLAR[-1].get("funding_usdt") is not None,
        f"funding={KAYITLAR[-1].get('funding_usdt') if KAYITLAR else '-'}")

print()
print("=" * 66)
gercek_yazim = [y for y in YAZIM if y[0] == "state"]
print(f"diske yazim (state): {'YOK' if not gercek_yazim else 'VAR — ' + str(gercek_yazim)}")
print(f"defter yazimi stub'a gitti: {len(YAZIM)} cagri, gercek dosyaya 0")
print(f"SONUC: {'HEPSI GECTI' if hata == 0 else str(hata) + ' HATA'}")
sys.exit(1 if hata else 0)
