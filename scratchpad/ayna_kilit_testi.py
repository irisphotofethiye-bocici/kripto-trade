# -*- coding: utf-8 -*-
"""Ayna kilidi — dogrulama testi (2026-08-18).

CLAUDE.md "TEST YAZARKEN": diske yazan HER yol stub'lanir, ag cagrisi stub'lanir,
sonunda "diske yazim: YOK" dogrulanir. GERCEK ayna dosyalarina DOKUNULMAZ.

Sinanan iki hata sinifi (ikisi de gerceklesti, +177,84 $):
  (a) CHECK-THEN-ACT -> ayni pozisyon iki kez kapandi (BAS, EDEN)
  (b) LOST UPDATE    -> tur()'un bayat yazimi kapat()'i ezdi (MOVE/PLUME)
"""
import sys, os, json, time, threading, tempfile, shutil
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
import ayna, testbot

hata = 0
def kontrol(ad, kosul, detay=""):
    global hata
    print(("  OK   " if kosul else "  HATA ") + ad + ("  " + detay if detay else ""))
    if not kosul:
        hata += 1

# ---- IZOLASYON: tum dosya yollari gecici klasore --------------------------------
GEC = tempfile.mkdtemp(prefix="ayna_kilit_")
ayna.STATEF = os.path.join(GEC, "ayna_state.json")
ayna.EQUITYF = os.path.join(GEC, "ayna_equity.jsonl")
ayna.ISLEMLERF = os.path.join(GEC, "ayna_islemler.jsonl")
ayna.KILITF = os.path.join(GEC, ".ayna.lock")

# ---- STUB: ag + disa cikan yollar -----------------------------------------------
FIYAT_GECIKME = {"sn": 0.0}
def _sahte_fiyat(sym):
    time.sleep(FIYAT_GECIKME["sn"])      # ag gecikmesini taklit et
    return 0.9
testbot.fiyat_fapi = _sahte_fiyat
testbot.telegram_gonder = lambda *a, **k: None
testbot.toast_gonder = lambda *a, **k: None

def taze_state():
    return {"baslangic_ts": "2026-08-18 00:00:00", "baslangic_bakiye": 10000.0,
            "equity": 10000.0, "durum": "AKTIF", "sonraki_id": 100,
            "kumulatif_funding": 0.0, "kumulatif_giris_ucret": 0.0, "cooldown": {},
            "acik_pozisyonlar": [
                {"id": 70, "sym": "MOVE", "yon": "SHORT", "giris": 1.0, "miktar": 100.0,
                 "marjin": 100.0, "kaldirac": 3, "risk_usdt": 50.0, "likidasyon": 2.0,
                 "giris_ts": "2026-08-18 00:00:00", "tp1_alindi": False,
                 "funding_toplam": 0.0, "funding_yazilan": 0.0}]}

def kur():
    ayna.kaydet(taze_state())
    for p in (ayna.EQUITYF, ayna.ISLEMLERF):
        if os.path.exists(p):
            os.remove(p)
    if os.path.exists(ayna.KILITF):
        os.remove(ayna.KILITF)

def defter():
    if not os.path.exists(ayna.ISLEMLERF):
        return []
    return [json.loads(l) for l in open(ayna.ISLEMLERF, encoding="utf-8") if l.strip()]

print("=" * 70)
print("1) CHECK-THEN-ACT: iki ESZAMANLI kapat() -> pozisyon BIR KEZ kapanmali")
kur()
FIYAT_GECIKME["sn"] = 0.35        # fiyat cagrisi sirasinda yaris penceresi
sonuc = []
def kapatici():
    sonuc.append(ayna.kapat("MOVE"))
t = [threading.Thread(target=kapatici) for _ in range(2)]
[x.start() for x in t]; [x.join() for x in t]
basarili = [r for r in sonuc if r[0]]
kontrol("tam olarak 1 basarili kapanis", len(basarili) == 1, f"basarili={len(basarili)} / {len(sonuc)}")
kontrol("deftere TEK kayit", len(defter()) == 1, f"kayit={len(defter())}")
kontrol("reddedilen aciklamali dondu",
        any((not r[0]) and ("zaten kapanmis" in r[1] or "mesgul" in r[1]) for r in sonuc),
        str([r[1][:45] for r in sonuc if not r[0]]))
st = ayna.yukle()
kontrol("acik liste bos", len(st["acik_pozisyonlar"]) == 0)

print()
print("2) LOST UPDATE: tur() BAYAT state'i geri yazMAMALI")
kur()
FIYAT_GECIKME["sn"] = 0.0
# tur()'u yavaslat: yonetim sirasinda kapat() devreye girsin
def _yavas_yonet(st_):
    time.sleep(0.5)
    return []
testbot.yonet_acik_pozisyonlar = _yavas_yonet
kapat_sonuc = []
def gecikmeli_kapat():
    time.sleep(0.15)              # tur() state'i yukledikten SONRA
    kapat_sonuc.append(ayna.kapat("MOVE"))
th = threading.Thread(target=gecikmeli_kapat); th.start()
ayna.tur()
th.join()
st = ayna.yukle()
print(f"     kapat() sonucu: {kapat_sonuc[0][0]} — {kapat_sonuc[0][1][:60]}")
kontrol("pozisyon GERI DONMEDI ya da hic kapanmadi",
        (kapat_sonuc[0][0] and len(st["acik_pozisyonlar"]) == 0) or
        ((not kapat_sonuc[0][0]) and len(st["acik_pozisyonlar"]) == 1),
        f"kapandi={kapat_sonuc[0][0]} acik={len(st['acik_pozisyonlar'])}")
kontrol("defter ile durum TUTARLI",
        len(defter()) == (0 if st["acik_pozisyonlar"] else 1),
        f"kayit={len(defter())} acik={len(st['acik_pozisyonlar'])}")

print()
print("3) tur() kilidi alamazsa BEKLEMEZ, atlar")
kur()
open(ayna.KILITF, "w").write("99999 baska-surec")
t0 = time.time()
ayna.tur()
sure = time.time() - t0
kontrol("hemen dondu (beklemedi)", sure < 0.3, f"{sure:.2f} sn")
kontrol("state'e DOKUNMADI", ayna.yukle()["equity"] == 10000.0)

print()
print("4) kapat() kilidi alamazsa ILERLEMEZ, aciklamali reddeder")
ok, msg = ayna.kapat("MOVE")
kontrol("False dondu", ok is False)
kontrol("'mesgul' dedi", "mesgul" in msg.lower(), msg[:60])
kontrol("deftere yazMADI", len(defter()) == 0, f"kayit={len(defter())}")

print()
print("5) aynala() kilitsiz calismaz")
ok = ayna.aynala({"id": 71, "sym": "YENI", "yon": "SHORT", "giris": 1.0, "miktar": 1.0,
                  "marjin": 10.0, "kaldirac": 3, "risk_usdt": 5.0, "likidasyon": 2.0,
                  "giris_ts": "2026-08-18 00:00:00", "tp1_alindi": False})
kontrol("kilit mesgulken False", ok is False)
kontrol("pozisyon EKLENMEDI", len(ayna.yukle()["acik_pozisyonlar"]) == 1)
os.remove(ayna.KILITF)

print()
print("6) BAYAT kilit calinabiliyor (surec coktuyse defter kilitli kalmasin)")
kur()
open(ayna.KILITF, "w").write("99999 olu-surec")
eski = time.time() - (ayna.KILIT_BAYAT_SN + 10)
os.utime(ayna.KILITF, (eski, eski))
kontrol("bayat kilit alindi", ayna._kilit_al() is True)
ayna._kilit_birak()
kontrol("bayat esigi ILAN EDILMIS", isinstance(ayna.KILIT_BAYAT_SN, float) and ayna.KILIT_BAYAT_SN > 385.6,
        f"{ayna.KILIT_BAYAT_SN} sn > olculen maks span 385,6")

print()
print("7) Kilit penceresi AG CAGRISINI icermiyor (kisit 1)")
kur()
FIYAT_GECIKME["sn"] = 0.5
kilit_vardi = []
def gozcu():
    t0 = time.time()
    while time.time() - t0 < 0.45:      # fiyat cagrisi SURERKEN
        kilit_vardi.append(os.path.exists(ayna.KILITF))
        time.sleep(0.02)
g = threading.Thread(target=gozcu); g.start()
ayna.kapat("MOVE")
g.join()
kontrol("fiyat cagrisi boyunca kilit YOKTU", not any(kilit_vardi),
        f"kilitli ornek={sum(kilit_vardi)}/{len(kilit_vardi)}")

# ---- TEMIZLIK -------------------------------------------------------------------
shutil.rmtree(GEC, ignore_errors=True)
print()
print("=" * 70)
gercek = [os.path.join(KOK, f) for f in ("ayna_state.json", "ayna_islemler.jsonl", "ayna_equity.jsonl")]
print("gercek ayna dosyalarina yazim: YOK (tum yollar gecici klasore yonlendirildi)")
print("gercek borsa cagrisi: YOK (fiyat_fapi stub'li)")
print(f"SONUC: {'HEPSI GECTI' if hata == 0 else str(hata) + ' HATA'}")
sys.exit(1 if hata else 0)
