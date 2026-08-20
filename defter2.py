#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEFTER-2 — OLCULEN EVRENIN CANLI SINAVI (2026-08-20, kullanici karari).

NE: Botun HIC dokunmadigi bir aday evreninde, botun AYNI cikis kurallariyla
    sanal SHORT acan ikinci kasa. Amac tek bir soruyu cevaplamak:
        "Mevcut bot yanlis evrende mi avlaniyor?"

NEDEN AYRI DEFTER (mevcut bota EKLENEMEZ): olculdu — botun 117 gercek
    pozisyonunun %100'u bu yapilandirmadan gecemezdi. Sebep yapisal: botun iki
    giris kapisi TAM OLARAK bu evreni disliyor.
        A+B        -> funding <= -0,05   (dislanan sart)
        MA50+ucuz  -> fiyat  <= $0,07    (dislanan sart)
    Yani filtreleri mevcut bota eklemek onu HIC islem acmaz hale getirir.
    Karsilastirma ancak AYRI defterle ve KENDI evreniyle yapilabilir.

EVREN (hepsi 2 yillik veriyle, KONTROL GRUPLU olculdu — olcumler.md):
    fiyat  > $0,07        ucuz coinler ham getiride -0,28 (t=-2,14); slipaj orada
                          2,5 kat yuksek. Botun SHORT akisinin %91'i buranin altinda.
    funding > -0,05       botun cekirdek kapisi kontrolunden -0,54 KOTU (t=-4,96),
                          oynaklik karistiricisi YOK (ATR 1,73 vs 1,69).
    chg24  <  %20         pump engeli — botun ZATEN uyguladigi ve DOGRU olan kapi
                          (gecenler ham -2,18).
    btc_pay bant != UST   ham lift uc rejimde de ayni isaret (-4,12/-3,21/-1,48).
    YALNIZ SHORT          LONG bu evrende bes adimin hepsinde t < -4.

    Kademeli olcum (2 yil, ay ortalamasi): ham evren -0,1097 -> tam yigin +0,2340.
    Zaman bolunmesi: A yarisi +0,2376 · B yarisi +0,2814 (ikisi de arti).
    ⚠️ AMA ay-kumeli t = +1,33 — ANLAMLI DEGIL, ve ornekle-ici insadir.
    2 yilin tamami kullanildi; geriye kalan tek gecerli hakem ILERI ZAMANDIR.
    Bu defter O hakemdir.

AYNI CIKIS KURALLARI — bilincli: fark YALNIZ giris evreninden gelsin diye
    (benim.py/golge.py ile ayni ilke). Olculmus stop onarimi (ilk 6 saat x2,
    +0,057) BURAYA KONMADI; konsaydi fark iki kaynaktan gelir ve ayrilamazdi.

RISK: YOK. Ayri kasa, ayri dosyalar. testbot'un state'ine, defterine, veto
    loguna DOKUNMAZ. Kendi surecinde kosar; testbot.py'ye HICBIR degisiklik
    yapilmadi.

Kullanim:  python defter2.py --baslat     (kasayi ILK KEZ olusturur)
           python defter2.py --tur        (bir tur: yonet + yeni giris ara)
           python defter2.py --durum
"""
import json, os, sys, argparse, datetime

import testbot
import evren

HERE = os.path.dirname(os.path.abspath(__file__))
STATEF = os.path.join(HERE, "defter2_state.json")
ISLEMLERF = os.path.join(HERE, "defter2_islemler.jsonl")
EQUITYF = os.path.join(HERE, "defter2_equity.jsonl")
VETOF = os.path.join(HERE, "defter2_veto.jsonl")      # botun veto_log'una SIZMASIN
ADAY_ARSIV = os.path.join(HERE, "testbot_aday_arsiv.jsonl")

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")

# --- EVREN ESIKLERI: olcumden gelir, burada SABIT (tarama yapilmaz) ---
MIN_FIYAT = 0.07          # ustu alinir
MIN_FUNDING = -0.05       # ustu alinir (botun kapisinin TERSI)
MAKS_CHG24 = 20.0         # alti alinir (botun pump kapisiyla ayni)
UST_ESIK = 0.287          # btc_pay UST ceyregi — bu banttayken giris YOK

MAKS_POZ = 8              # botun kendi limitiyle ayni (adil kiyas)
TEKRAR_SAAT = 4.0         # ayni sembole bu kadar saat gecmeden tekrar girme
ADAY_TAZE_DK = 12.0       # aday arsivinden bu kadar dakikalik pencere okunur


# ---------------------------------------------------------------------------
def yeni_state():
    return {"baslangic_ts": testbot.now_iso(), "baslangic_bakiye": 10000.0,
            "equity": 10000.0, "durum": "AKTIF", "acik_pozisyonlar": [],
            "sonraki_id": 1, "cooldown": {}, "bekleyenler": {}, "veto_cooldown": {},
            "son_giris": {}, "son_cycle_ts": None}


def yukle():
    try:
        with open(STATEF, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def kaydet(st):
    """ATOMIK yazim (.tmp + os.replace) — CLAUDE.md kurali.
    benim.py/golge.py duz json.dump kullaniyor ve golge defteri 2026-08-11'de
    bu yuzden 314 $ sapmisti. Burada bastan dogru yapiliyor."""
    tmp = STATEF + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATEF)


def _sessiz(*a, **kw):
    """Bu defterin hareketleri '[TESTBOT] ...' bildirimi GONDERMEZ — bota ait degil."""
    return None


def _defterde(fn, *a, **kw):
    """testbot fonksiyonunu BU deftere yonlendirerek + SESSIZ calistir.

    DORT sey takas edilir, finally ile MUTLAKA geri alinir:
      _DEFTER         -> kapanan islemler bu deftere yazilsin
      telegram/toast  -> bota ait olmayan hareket bot bildirimi gibi gitmesin
      VETO_LOGF       -> 🔴 golge.py'de EKSIK OLAN KORUMA. _veto_logla modul
                         duzeyindeki VETO_LOGF'e KORUMASIZ yazar; golge canli-aday
                         kapilarinda zorla=False kullandigi icin rr_veto tetikleyip
                         BOTUN veto_log.jsonl'ine kayit dusurebiliyor. Bu defter
                         ayni hatayi yapmaz."""
    eski = (testbot._DEFTER, testbot.telegram_gonder, testbot.toast_gonder, testbot.VETO_LOGF)
    testbot._DEFTER = ISLEMLERF
    testbot.telegram_gonder = _sessiz
    testbot.toast_gonder = _sessiz
    testbot.VETO_LOGF = VETOF
    try:
        return fn(*a, **kw)
    finally:
        (testbot._DEFTER, testbot.telegram_gonder,
         testbot.toast_gonder, testbot.VETO_LOGF) = eski


# ---------------------------------------------------------------------------
def btc_pay_ust_mu():
    """btc_pay UST ceyreginde miyiz? Veri yoksa None -> FAIL-SAFE: giris ARANMAZ.
    (Botun fail-open'inin TERSI: burada emin olmadan girmeyiz.)"""
    try:
        bp = evren.btc_pay_akisi()
    except Exception:
        return None
    if not bp or bp.get("bant") is None:
        return None
    return bp["bant"] == "UST"


def taze_adaylar():
    """Aday arsivinin SON penceresini oku. -> [kayit]  (salt okuma)"""
    try:
        boyut = os.path.getsize(ADAY_ARSIV)
    except Exception:
        return []
    out = []
    with open(ADAY_ARSIV, "rb") as f:
        f.seek(max(0, boyut - 400000))          # son ~400 kB yeter, dosya buyuk
        ham = f.read().decode("utf-8", "ignore")
    sinir = testbot.now_dt() - datetime.timedelta(minutes=ADAY_TAZE_DK)
    for satir in ham.splitlines()[1:]:          # ilk satir kirpik olabilir
        satir = satir.strip()
        if not satir:
            continue
        try:
            x = json.loads(satir)
            t = datetime.datetime.strptime(x["ts"], "%Y-%m-%d %H:%M")
        except Exception:
            continue
        if t >= sinir:
            out.append(x)
    return out


def evrene_uyar(x):
    """Olculen evren. -> (uyar_mi, sebep)"""
    p = x.get("price")
    if p is None or p <= MIN_FIYAT:
        return False, "ucuz (<=$%.2f)" % MIN_FIYAT
    f = x.get("funding")
    if f is None or f <= MIN_FUNDING:
        return False, "funding <= %.2f (botun kapisi)" % MIN_FUNDING
    c = x.get("chg24")
    if c is None or c >= MAKS_CHG24:
        return False, "pump (chg24 >= %.0f)" % MAKS_CHG24
    return True, ""


def _tekrar_var_mi(st, sym):
    son = st.get("son_giris", {}).get(sym)
    if not son:
        return False
    try:
        return (testbot.now_dt() - testbot.parse_iso(son)).total_seconds()/3600 < TEKRAR_SAAT
    except Exception:
        return False


def giris_ara(st):
    """Taze adaylardan evrene uyanlari SHORT ac. -> acilan sayisi."""
    if len(st["acik_pozisyonlar"]) >= MAKS_POZ:
        return 0
    ust = btc_pay_ust_mu()
    if ust is None:
        print("[defter2] btc_pay verisi yok -> giris aranmadi (fail-safe)")
        return 0
    if ust:
        print("[defter2] btc_pay UST bandi -> giris aranmadi")
        return 0
    acik = {p["sym"] for p in st["acik_pozisyonlar"]}
    gorulen, acilan = set(), 0
    # SIRALAMA: skor azalan. Botun kendi siralamasi; kapasite (MAKS_POZ) yuzunden
    # bir sira SECMEK zorunlu. ⚠️ Skorun katki yaptigi OLCULMEDI — aksine A+B
    # notunda "skor eklemek DUSURUYOR" yaziyor (+0,396 -> +0,338). Bu yuzden
    # siralama bir KAPI DEGIL, yalnizca kapasite kuyrugudur ve hukum yazarken
    # "skor sirasiyla alindi" notu dusulmelidir.
    for x in sorted(taze_adaylar(), key=lambda z: -(z.get("score") or 0)):
        sym = x.get("sym")
        if not sym or sym in gorulen or sym in acik:
            continue
        gorulen.add(sym)
        uyar, _sb = evrene_uyar(x)
        if not uyar or _tekrar_var_mi(st, sym):
            continue
        r = dict(x)                     # arsiv kaydi radar.analyze ciktisinin kendisidir
        pillar = {"top_ls": x.get("top_ls"), "glob_ls": x.get("glob_ls"),
                  "taker": x.get("taker"), "smart": x.get("smart")}
        red = []
        ok = _defterde(testbot.yeni_giris_ac, st, sym, "SHORT", r, pillar,
                       "DEFTER2: olculen evren (fiyat>$%.2f · funding>%.2f · chg24<%.0f · btc_pay!=UST)"
                       % (MIN_FIYAT, MIN_FUNDING, MAKS_CHG24),
                       zorla=False, rejim_ad=x.get("rejim"), kaynak="defter2", red_out=red)
        if ok:
            st.setdefault("son_giris", {})[sym] = testbot.now_iso()
            acilan += 1
            print("[defter2] ACILDI %s SHORT (skor %s · fiyat %s · funding %s)"
                  % (sym, x.get("score"), x.get("price"), x.get("funding")))
            if len(st["acik_pozisyonlar"]) >= MAKS_POZ:
                break
        elif red:
            print("[defter2] giris kapisi %s: %s" % (sym, red[0]["kapi"]))
    return acilan


def equity_yaz(st):
    try:
        testbot._append_jsonl(EQUITYF, {
            "ts": testbot.now_iso(), "equity": round(st["equity"], 2),
            "acik_pnl": round(testbot.acik_pnl_toplam(st), 2),
            "acik_sayisi": len(st["acik_pozisyonlar"]), "durum": st["durum"]})
    except Exception:
        pass


def tur():
    """Bir tur: acik pozisyonlari BOTLA AYNI kurallarla yonet, sonra yeni giris ara.
    Kasa yoksa HICBIR SEY yapmaz (dosya olusturmaz) — --baslat gerekir."""
    st = yukle()
    if not st:
        return False
    if st["acik_pozisyonlar"]:
        _defterde(testbot.yonet_acik_pozisyonlar, st)
    giris_ara(st)
    st["son_cycle_ts"] = testbot.now_iso()
    kaydet(st)
    equity_yaz(st)
    return True


def durum():
    st = yukle()
    if not st:
        print("DEFTER-2: henuz baslatilmadi ('python defter2.py --baslat').")
        return
    try:
        with open(ISLEMLERF, encoding="utf-8") as f:
            islemler = [json.loads(l) for l in f if l.strip()]
    except Exception:
        islemler = []
    poz = {}
    for t in islemler:
        poz.setdefault(t["id"], []).append(t)
    toplam = sum(t.get("sonuc_usdt") or 0 for t in islemler)
    kz = sum(1 for v in poz.values() if sum(t.get("sonuc_usdt") or 0 for t in v) > 0)
    print("=== DEFTER-2 (olculen evren, sanal) ===")
    print("Evren: fiyat>$%.2f · funding>%.2f · chg24<%.0f · btc_pay!=UST · YALNIZ SHORT"
          % (MIN_FIYAT, MIN_FUNDING, MAKS_CHG24))
    print("Durum: %s | Bakiye: $%.0f -> $%.2f" % (st["durum"], st["baslangic_bakiye"], st["equity"]))
    print("Acik pozisyon: %d/%d" % (len(st["acik_pozisyonlar"]), MAKS_POZ))
    for p in st["acik_pozisyonlar"]:
        px = testbot.fiyat_fapi(p["sym"]) or p["giris"]
        yi = 1 if p["yon"] == "LONG" else -1
        print("  %-8s %-5s %sx giris=%.6g anlik=%.6g PnL=%+.2f$ stop=%.6g"
              % (p["sym"], p["yon"], p["kaldirac"], p["giris"], px,
                 (px-p["giris"])*p["miktar"]*yi, p["stop"]))
    print("Kapanan pozisyon: %d | Kazanan: %d | Toplam P&L: %+.2f$"
          % (len(poz), kz, toplam))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--baslat", action="store_true", help="kasayi ILK KEZ olustur")
    ap.add_argument("--tur", action="store_true")
    ap.add_argument("--durum", action="store_true")
    a = ap.parse_args()
    if a.baslat:
        if yukle():
            print("DEFTER-2 zaten var — --baslat yok sayildi (kasa SIFIRLANMADI).")
        else:
            kaydet(yeni_state())
            print("DEFTER-2 olusturuldu: %s" % STATEF)
    elif a.tur:
        print("tur tamam" if tur() else "kasa yok — once --baslat")
    else:
        durum()
