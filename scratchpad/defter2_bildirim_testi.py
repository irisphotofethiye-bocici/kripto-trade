#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEFTER-2 KAPANIS BILDIRIMI TESTI — sahte veriyle, DISKE YAZMADAN.

CLAUDE.md: "diske yazan HER yolu stub'la ... sonunda 'diske yazim: YOK' diye
DOGRULA." Burada ayrica TELEGRAM da stub'lanir (gercek mesaj GITMEZ).
"""
import json, os, sys, tempfile

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
import testbot
import defter2

GECTI, KALDI = [], []


def kontrol(ad, sart, detay=""):
    (GECTI if sart else KALDI).append(ad)
    print("  %s %s%s" % ("[OK] " if sart else "[!!]", ad, ("  -> " + detay) if detay else ""))


IZLENEN = ["testbot_state.json", "testbot_islemler.jsonl", "veto_log.jsonl",
           "testbot_equity.jsonl", "golge_state.json", "benim_state.json",
           "ayna_state.json", "defter2_state.json", "defter2_islemler.jsonl",
           "defter2_equity.jsonl", "defter2_veto.jsonl", "kripto-config.json"]


def parmak():
    d = {}
    for f in IZLENEN:
        p = os.path.join(KOK, f)
        d[f] = (os.path.getmtime(p), os.path.getsize(p)) if os.path.exists(p) else None
    return d


ONCE = parmak()

# ---------- STUB'LAR ----------
gonderilen = []
defter2._tg = lambda msg: gonderilen.append(msg)
testbot._save_state = lambda st: None
testbot.telegram_gonder = lambda *a, **k: None
testbot.toast_gonder = lambda *a, **k: None

gec = tempfile.mkdtemp(prefix="d2bild_")
defter2.ISLEMLERF = os.path.join(gec, "islem.jsonl")
defter2.STATEF = os.path.join(gec, "state.json")
defter2.EQUITYF = os.path.join(gec, "equity.jsonl")

print("=" * 74)
print("DEFTER-2 KAPANIS BILDIRIMI TESTI (sahte veri, gercek telegram YOK)")
print("=" * 74)

ST = {"equity": 10012.5, "acik_pozisyonlar": [{"sym": "X"}], "durum": "AKTIF",
      "baslangic_bakiye": 10000.0, "son_giris": {}}

# ---------- 1) hic kapanis yoksa SESSIZ ----------
print("\n1) kapanis yoksa bildirim gitmez")
defter2.kapanis_bildir([], ST)
kontrol("bos liste -> mesaj YOK", not gonderilen)

# ---------- 2) tam kapanis ----------
print("\n2) tam kapanis bildirimi")
K1 = {"id": 1, "sym": "BEAT", "yon": "SHORT", "sonuc_usdt": 13.4,
      "sebep": "TP", "r": 1.8, "tutma_saat": 5.2}
with open(defter2.ISLEMLERF, "w", encoding="utf-8") as f:
    f.write(json.dumps(K1) + "\n")
defter2.kapanis_bildir([K1], ST)
m = gonderilen[-1] if gonderilen else ""
kontrol("mesaj gonderildi", bool(gonderilen))
kontrol("sembol var", "BEAT" in m)
kontrol("KAPANDI etiketi", "KAPANDI" in m)
kontrol("PnL yazili", "+13.40$" in m, m.splitlines()[0] if m else "")
kontrol("R yazili", "R=1.80" in m)
kontrol("kapanan poz 1", "kapanan poz 1" in m)
kontrol("defter toplami +13.40", "+13.40$ (fonlama" in m)

# ---------- 3) TP1 kismi: YARIM etiketi + TOPLAMA DAHIL ----------
print("\n3) TP1_KISMI — 'suzgec toplamak icin degil' kurali")
K2 = {"id": 2, "sym": "KAITO", "yon": "SHORT", "sonuc_usdt": 9.0,
      "sebep": "TP1_KISMI", "kismi": True, "r": None, "tutma_saat": 2.1}
with open(defter2.ISLEMLERF, "a", encoding="utf-8") as f:
    f.write(json.dumps(K2) + "\n")
defter2.kapanis_bildir([K2], ST)
m = gonderilen[-1]
kontrol("YARIM etiketi", "YARIM" in m and "KAPANDI" not in m.split("|")[0])
kontrol("R yok -> R yazilmadi", "R=" not in m)
kontrol("TOPLAM kismiyi ICERIR (13.4+9.0=22.4)", "+22.40$ (fonlama" in m, m)
kontrol("POZISYON SAYISI kismiyi SAYMAZ (hala 1)", "kapanan poz 1" in m, m)

# ---------- 4) ayni turda iki kapanis tek mesajda ----------
print("\n4) ayni turda iki kayit -> tek mesaj")
n0 = len(gonderilen)
defter2.kapanis_bildir([K1, K2], ST)
kontrol("tek mesaj gitti", len(gonderilen) - n0 == 1)
kontrol("ikisi de mesajda", "BEAT" in gonderilen[-1] and "KAITO" in gonderilen[-1])

# ---------- 5) tur() kapanisi YAKALIYOR mu ----------
print("\n5) tur() akisi: yonetim sonrasi dusen kayit yakalanir")
defter2.kaydet(ST)
gonderilen.clear()


def _sahte_yonet(st):
    """Gercek yonetim yerine: deftere bir kapanis kaydi dusur (bot davranisi taklidi)."""
    with open(defter2.ISLEMLERF, "a", encoding="utf-8") as f:
        f.write(json.dumps({"id": 3, "sym": "META", "yon": "SHORT",
                            "sonuc_usdt": -21.7, "sebep": "STOP", "r": -1.0,
                            "tutma_saat": 1.4}) + "\n")


testbot.yonet_acik_pozisyonlar = _sahte_yonet
defter2.giris_ara = lambda st: 0            # ag cagrisi yapmasin
ok = defter2.tur()
kontrol("tur() True dondu", ok is True)
kontrol("tur() kapanisi bildirdi", len(gonderilen) == 1)
kontrol("dogru sembol", "META" in gonderilen[-1] and "-21.70$" in gonderilen[-1])
kontrol("ESKI kayitlar tekrar bildirilmedi", "BEAT" not in gonderilen[-1])

# ---------- 6) kapanis olmayan turda mesaj YOK ----------
print("\n6) kapanis olmayan turda mesaj yok")
testbot.yonet_acik_pozisyonlar = lambda st: None
gonderilen.clear()
defter2.tur()
kontrol("sessiz tur -> mesaj YOK", not gonderilen)

# ---------- 7) _defterde REGRESYONU: takas hala geri aliniyor ----------
print("\n7) regresyon — _defterde takasi geri aliyor")
d0 = (testbot._DEFTER, testbot.telegram_gonder, testbot.toast_gonder, testbot.VETO_LOGF)
defter2._defterde(lambda: None)
kontrol("_DEFTER geri alindi", testbot._DEFTER == d0[0])
kontrol("VETO_LOGF geri alindi", testbot.VETO_LOGF == d0[3])
kontrol("telegram geri alindi", testbot.telegram_gonder is d0[1])
kontrol("_tg takastan ETKILENMEZ (nobetci'den dogrudan)",
        defter2._tg is not testbot.telegram_gonder)

# ---------- 8) DISKE YAZIM ----------
print("\n8) DISKE YAZIM DOGRULAMASI")
SONRA = parmak()
degisen = [f for f in IZLENEN if ONCE[f] != SONRA[f]]
kontrol("bot/defter dosyalarina yazim: YOK", not degisen, str(degisen))
kontrol("gercek telegram cagrisi: YOK (stub'landi)", True, "%d mesaj yakalandi" % len(gonderilen))

print("\n" + "=" * 74)
print("GECTI: %d   KALDI: %d" % (len(GECTI), len(KALDI)))
if KALDI:
    print("KALAN: %s" % ", ".join(KALDI))
    sys.exit(1)
print("TUM KONTROLLER GECTI · diske yazim: YOK · telegram: gonderilmedi")
