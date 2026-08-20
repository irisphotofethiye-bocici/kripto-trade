#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEFTER-2 TESTI — sahte veriyle, DISKE YAZMADAN.

CLAUDE.md: "Sahte veriyle test ederken diske yazan HER yolu stub'la — 'guvenli
fiyat secmek' yetmez. Testin sonunda 'diske yazim: YOK' diye DOGRULA."

Stub'lananlar: _append_jsonl · _save_state · pozisyon_kapat · pozisyon_liq ·
pozisyon_kismi_tp1 · telegram_gonder · toast_gonder · defter2.kaydet
"""
import json, os, sys, datetime, tempfile

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
import testbot
import defter2

GECTI, KALDI = [], []


def kontrol(ad, sart, detay=""):
    (GECTI if sart else KALDI).append(ad)
    print("  %s %s%s" % ("[OK] " if sart else "[!!]", ad, ("  -> " + detay) if detay else ""))


# ---------- diske yazim izleme ----------
IZLENEN = ["testbot_state.json", "testbot_islemler.jsonl", "veto_log.jsonl",
           "testbot_aday_arsiv.jsonl", "testbot_equity.jsonl", "golge_state.json",
           "golge_islemler.jsonl", "benim_state.json", "ayna_state.json",
           "defter2_state.json", "defter2_islemler.jsonl", "defter2_veto.jsonl",
           "defter2_equity.jsonl", "kripto-config.json"]


def parmak():
    d = {}
    for f in IZLENEN:
        p = os.path.join(KOK, f)
        d[f] = (os.path.getmtime(p), os.path.getsize(p)) if os.path.exists(p) else None
    return d


ONCE = parmak()

# ---------- STUB'LAR ----------
yazim = []
testbot._append_jsonl = lambda yol, kayit: yazim.append(("append", yol))
testbot._save_state = lambda st: yazim.append(("state", "testbot_state.json"))
testbot.pozisyon_kapat = lambda *a, **k: yazim.append(("kapat", a[1].get("sym") if len(a) > 1 else "?"))
testbot.pozisyon_liq = lambda *a, **k: yazim.append(("liq", "?"))
testbot.pozisyon_kismi_tp1 = lambda *a, **k: yazim.append(("tp1", "?"))
testbot.telegram_gonder = lambda *a, **k: yazim.append(("tg", "?"))
testbot.toast_gonder = lambda *a, **k: yazim.append(("toast", "?"))
defter2.kaydet = lambda st: yazim.append(("d2state", "defter2_state.json"))

print("=" * 74)
print("DEFTER-2 TESTI (sahte veri, diske yazim YOK)")
print("=" * 74)

# ---------- 1) _defterde DORT seyi takas edip GERI ALIYOR mu ----------
print("\n1) _defterde takas ve GERI ALMA")
d0 = (testbot._DEFTER, testbot.telegram_gonder, testbot.toast_gonder, testbot.VETO_LOGF)
ic = {}


def _gozle():
    ic["defter"] = testbot._DEFTER
    ic["veto"] = testbot.VETO_LOGF
    ic["tg"] = testbot.telegram_gonder
    return "ok"


defter2._defterde(_gozle)
kontrol("iceride _DEFTER defter2'ye donuyor", ic["defter"] == defter2.ISLEMLERF, ic["defter"])
kontrol("iceride VETO_LOGF defter2'ye donuyor", ic["veto"] == defter2.VETOF, ic["veto"])
kontrol("iceride telegram susturuluyor", ic["tg"] is defter2._sessiz)
kontrol("SONRA _DEFTER geri alindi", testbot._DEFTER == d0[0])
kontrol("SONRA VETO_LOGF geri alindi", testbot.VETO_LOGF == d0[3])
kontrol("SONRA telegram geri alindi", testbot.telegram_gonder is d0[1])


# ---------- 2) HATA halinde de geri aliyor mu (finally) ----------
print("\n2) icerideki fonksiyon PATLARSA geri alma")
def _patla():
    raise RuntimeError("test")


try:
    defter2._defterde(_patla)
except RuntimeError:
    pass
kontrol("hata sonrasi _DEFTER geri alindi", testbot._DEFTER == d0[0])
kontrol("hata sonrasi VETO_LOGF geri alindi", testbot.VETO_LOGF == d0[3])

# ---------- 3) _veto_logla GERCEKTEN takas edilen yola yaziyor mu ----------
print("\n3) _veto_logla sizinti testi (golge.py'de EKSIK olan koruma)")
hedef = []
testbot._append_jsonl = lambda yol, kayit: hedef.append(yol)
sahte_st = {"veto_cooldown": {}}
defter2._defterde(testbot._veto_logla, sahte_st, "TEST", {"price": 1.0, "score": 50},
                  {"taker": 1.0, "smart": "NOTR"}, "rr_veto", "test", "SHORT", "NOTR")
kontrol("veto kaydi defter2_veto.jsonl'e gitti", hedef and hedef[-1] == defter2.VETOF,
        hedef[-1] if hedef else "yazim yok")
kontrol("botun veto_log.jsonl'ine YAZILMADI",
        all("veto_log.jsonl" not in y for y in hedef))
testbot._append_jsonl = lambda yol, kayit: yazim.append(("append", yol))

# ---------- 4) evren filtresi ----------
print("\n4) evren filtresi (olculen esikler)")
ORN = [
    ({"price": 0.50, "funding": 0.01, "chg24": 5.0}, True, "temiz aday"),
    ({"price": 0.05, "funding": 0.01, "chg24": 5.0}, False, "ucuz -> RED"),
    ({"price": 0.07, "funding": 0.01, "chg24": 5.0}, False, "tam esik ($0,07) -> RED"),
    ({"price": 0.50, "funding": -0.06, "chg24": 5.0}, False, "botun funding kapisi -> RED"),
    ({"price": 0.50, "funding": -0.05, "chg24": 5.0}, False, "tam esik (-0,05) -> RED"),
    ({"price": 0.50, "funding": 0.01, "chg24": 25.0}, False, "pump -> RED"),
    ({"price": 0.50, "funding": 0.01, "chg24": 20.0}, False, "tam esik (%20) -> RED"),
    ({"price": None, "funding": 0.01, "chg24": 5.0}, False, "fiyat yok -> RED"),
    ({"price": 0.50, "funding": None, "chg24": 5.0}, False, "funding yok -> RED"),
    ({"price": 0.50, "funding": 0.01, "chg24": None}, False, "chg24 yok -> RED"),
]
for x, bek, ad in ORN:
    kontrol("evren: %s" % ad, defter2.evrene_uyar(x)[0] == bek)

# ---------- 5) tekrar korumasi ----------
print("\n5) ayni sembole tekrar giris korumasi (%.1f saat)" % defter2.TEKRAR_SAAT)
simdi = testbot.now_dt()
st = {"son_giris": {"A": (simdi - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
                    "B": (simdi - datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")}}
kontrol("1 saat once girilen -> ENGELLI", defter2._tekrar_var_mi(st, "A") is True)
kontrol("9 saat once girilen -> serbest", defter2._tekrar_var_mi(st, "B") is False)
kontrol("hic girilmemis -> serbest", defter2._tekrar_var_mi(st, "C") is False)

# ---------- 6) taze aday okuma ----------
print("\n6) aday arsivi okuma (SALT OKUMA)")
gec = tempfile.mkdtemp(prefix="d2test_")
sahte = os.path.join(gec, "aday.jsonl")
t_taze = simdi.strftime("%Y-%m-%d %H:%M")
t_bayat = (simdi - datetime.timedelta(hours=3)).strftime("%Y-%m-%d %H:%M")
with open(sahte, "w", encoding="utf-8") as f:
    f.write("BOZUK-ILK-SATIR\n")
    for ts, sym in ((t_bayat, "ESKI"), (t_taze, "YENI1"), (t_taze, "YENI2")):
        f.write(json.dumps({"ts": ts, "sym": sym, "price": 1.0}) + "\n")
eski_yol = defter2.ADAY_ARSIV
defter2.ADAY_ARSIV = sahte
ad = defter2.taze_adaylar()
defter2.ADAY_ARSIV = eski_yol
syms = [x["sym"] for x in ad]
kontrol("taze adaylar okundu", set(syms) == {"YENI1", "YENI2"}, str(syms))
kontrol("BAYAT aday elendi", "ESKI" not in syms)

# ---------- 7) btc_pay fail-safe ----------
print("\n7) btc_pay fail-safe (veri yoksa GIRIS ARANMAZ)")
esk = defter2.btc_pay_ust_mu
defter2.btc_pay_ust_mu = lambda: None
st2 = {"acik_pozisyonlar": [], "son_giris": {}}
kontrol("btc_pay None -> 0 giris", defter2.giris_ara(st2) == 0)
defter2.btc_pay_ust_mu = lambda: True
kontrol("btc_pay UST -> 0 giris", defter2.giris_ara(st2) == 0)
defter2.btc_pay_ust_mu = esk

# ---------- 8) kasa yokken tur() hicbir sey yapmaz ----------
print("\n8) kasa yokken tur()")
esk_y = defter2.yukle
defter2.yukle = lambda: None
kontrol("kasa yok -> tur() False doner, dosya olusturmaz", defter2.tur() is False)
defter2.yukle = esk_y

# ---------- 9) DISKE YAZIM DOGRULAMASI ----------
print("\n9) DISKE YAZIM DOGRULAMASI")
SONRA = parmak()
degisen = [f for f in IZLENEN if ONCE[f] != SONRA[f]]
kontrol("bot/defter dosyalarina yazim: YOK", not degisen, str(degisen))
kontrol("stub'lanan yazim cagrilari yakalandi (gercek yazim degil)", True,
        "%d cagri" % len(yazim))

print("\n" + "=" * 74)
print("GECTI: %d   KALDI: %d" % (len(GECTI), len(KALDI)))
if KALDI:
    print("KALAN KONTROLLER: %s" % ", ".join(KALDI))
    sys.exit(1)
print("TUM KONTROLLER GECTI · diske yazim: YOK")
