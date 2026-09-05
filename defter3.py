#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEFTER-3 — AYNI EVREN, IKI YON (2026-08-25, kullanici karari).

NE: defter2 ile TAM AYNI evren, TAM AYNI cikis kurallari, TAM AYNI boyutlandirma.
    TEK FARK: yon. defter2 yalniz SHORT acar; bu defter chg24 isaretine gore
    SHORT ya da LONG acar.

        chg24 >= 0  ->  SHORT   (defter2 ile AYNI davranis)
        chg24 <  0  ->  LONG    (defter2 burada SHORT aciyor)

    Boylece bir ay sonra tek cikarma isi yeter:
        defter3 - defter2  =  YON eklemenin etkisi, baska hicbir sey degismedi
    Ve chg24<0 alt kumesinde ayni isimler uzerinde DOGRUDAN yon kiyasi olur
    (defter2 SHORT acmis, defter3 LONG acmis).

NEDEN: defter2 YALNIZ SHORT oldugu icin, boga haftasinda YAPISI GEREGI kaybeder.
    Olculdu (2026-08-20..25): BTC'nin alti gununun besinde yukseldi, toplam ~%16.
    defter2 -1.457 $. Bu kaybin sebebi AYRILAMIYOR:
        (a) evren kotu           (b) yon kisiti kotu
    Bu defter tam olarak o ayrimi yapar.

⚠️ LONG BU EVRENDE OLCULDU VE REDDEDILDI: "bes adimin hepsinde t < -4"
    (defter2.py basligi). Bu defter o "hayir"i ILERI ZAMANDA sinar.
    Neden yine de deger: defter2'nin KENDI dayanagi da geriye donuk olcumde
    zayifladi (8 gunluk holdout, uc sembol cikinca isaret dondu) ama ileri
    performansi testbot'un iki kati iyi cikti. Ayni belirsizlik LONG icin de
    gecerli. LONG kolunun KAYBETMESI BEKLENIYOR; "gercekten kotu" cevabi da
    tam bir cevaptir.

⚠️ BILINEN ASIMETRI: btc_pay UST filtresi SHORT icin olculmustu ve burada
    HER IKI yone de uygulaniyor. Bilincli: evren AYNI kalsin, tek degisken yon
    olsun diye. LONG kolunu bir miktar kisitlar; hukum yazarken not dusulur.

⚠️ FORMASYON YOK. "En iyi formasyon" olculmedi (2026-08-25 oturumu: yedi olcum,
    yedisi de olumsuz). Uydurulmus bir formasyon konsaydi sonuc uc bilinmeyenli
    olurdu (evren mi, yon mu, formasyon mu). Bu defter SADE tutuldu.

RISK: YOK. Ayri kasa, ayri dosyalar, sifir API cagrisi (aday arsivini okur).
    testbot'a da defter2'ye de DOKUNMAZ.

Kullanim:  python defter3.py --baslat     (kasayi ILK KEZ olusturur)
           python defter3.py --tur        (bir tur)
           python defter3.py --durum      (LONG/SHORT kirilimli rapor)
"""
import json, os, sys, argparse, datetime

import testbot
import evren
# Kapanis bildirimi icin GERCEK gonderici. testbot.telegram_gonder
# _defterde() icinde SUSTURULUYOR; buraya dogrudan alinir ki takastan
# etkilenmesin. Botun bildirim ayari DEGISTIRILMEDI.
from nobetci import telegram_gonder as _tg

HERE = os.path.dirname(os.path.abspath(__file__))
STATEF = os.path.join(HERE, "defter3_state.json")
ISLEMLERF = os.path.join(HERE, "defter3_islemler.jsonl")
EQUITYF = os.path.join(HERE, "defter3_equity.jsonl")
VETOF = os.path.join(HERE, "defter3_veto.jsonl")      # botun veto_log'una SIZMASIN
ADAY_ARSIV = os.path.join(HERE, "testbot_aday_arsiv.jsonl")

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")

# --- EVREN ESIKLERI: olcumden gelir, burada SABIT (tarama yapilmaz) ---
MIN_FIYAT = 0.07          # ustu alinir
MIN_FUNDING = -0.05       # ustu alinir (botun kapisinin TERSI)
MAKS_CHG24 = 20.0         # alti alinir (botun pump kapisiyla ayni)
UST_ESIK = 0.287          # btc_pay UST ceyregi — bu banttayken giris YOK

MAKS_POZ = 0              # [DEGISTI 2026-09-05] 8 -> 0, kullanici: 'yeni girisleri durdur'.
#   SIFIR = giris_ara() hemen doner; CIKISLAR ETKILENMEZ (tur(): yonet_acik_pozisyonlar
#   ONCE, giris_ara SONRA). Config'ten okunmuyor, o yuzden burada. GERI ALMA: 8 yap.
#   ESKI DEGER 8 — 'botun kendi limitiyle ayni (adil kiyas)' (D/9: silinmedi).
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
    """Taze adaylardan evrene uyanlari YON KURALIYLA ac. -> acilan sayisi."""
    if len(st["acik_pozisyonlar"]) >= MAKS_POZ:
        return 0
    ust = btc_pay_ust_mu()
    if ust is None:
        print("[defter3] btc_pay verisi yok -> giris aranmadi (fail-safe)")
        return 0
    if ust:
        print("[defter3] btc_pay UST bandi -> giris aranmadi")
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
        # YON KURALI — bu defterin TEK farki. Fiyat hareketi FADE edilir:
        #   chg24 >= 0 -> SHORT (defter2 ile ayni)   ·   chg24 < 0 -> LONG
        yon = "SHORT" if (x.get("chg24") or 0) >= 0 else "LONG"
        r = dict(x)                     # arsiv kaydi radar.analyze ciktisinin kendisidir
        pillar = {"top_ls": x.get("top_ls"), "glob_ls": x.get("glob_ls"),
                  "taker": x.get("taker"), "smart": x.get("smart")}
        red = []
        ok = _defterde(testbot.yeni_giris_ac, st, sym, yon, r, pillar,
                       "DEFTER3: defter2 evreni + IKI YON (chg24>=0 SHORT / chg24<0 LONG)",
                       zorla=False, rejim_ad=x.get("rejim"), kaynak="defter3", red_out=red)
        if ok:
            st.setdefault("son_giris", {})[sym] = testbot.now_iso()
            acilan += 1
            print("[defter3] ACILDI %s %s (chg24 %s · skor %s · fiyat %s · funding %s)"
                  % (sym, yon, x.get("chg24"), x.get("score"), x.get("price"), x.get("funding")))
            if len(st["acik_pozisyonlar"]) >= MAKS_POZ:
                break
        elif red:
            print("[defter3] giris kapisi %s: %s" % (sym, red[0]["kapi"]))
    return acilan


def equity_yaz(st):
    try:
        testbot._append_jsonl(EQUITYF, {
            "ts": testbot.now_iso(), "equity": round(st["equity"], 2),
            "acik_pnl": round(testbot.acik_pnl_toplam(st), 2),
            "acik_sayisi": len(st["acik_pozisyonlar"]), "durum": st["durum"]})
    except Exception:
        pass


# --- KAPANIS BILDIRIMI (kullanici istegi, 2026-08-20) ----------------------
# NEDEN BURADA VE _defterde DISINDA: takas sirasinda telegram susturuluyor
# (bota ait olmayan hareket "[TESTBOT] ..." diye gitmesin). Bildirim takas
# GERI ALINDIKTAN sonra, nobetci'den dogrudan alinan fonksiyonla gider.
#
# olay ETIKETI VERILMEZ: config'te "olaylar": ["giris"] var, yani "kapanis"
# etiketli cagrilar suzuluyor. nobetci._olay_izinli olaysiz cagrilari HER ZAMAN
# geciriyor -> boylece BOTUN bildirim ayarina dokunmadan bu defter bildirebiliyor.

def _defter_kayitlari():
    """defter3 islem defterinin tamami. Yoksa []. (salt okuma)"""
    try:
        with open(ISLEMLERF, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]
    except Exception:
        return []


def kapanis_bildir(yeni, st):
    """Bu turda deftere DUSEN kayitlari bildirir.

    TP1_KISMI de bildirilir — pozisyonun yarisinin gercekten kapanmasidir.
    TOPLAM hesabinda kismi kayitlar DAHIL EDILIR (CLAUDE.md: "suzgec saymak
    icindir, toplamak icin degil" — suzmek TP1'de realize edilen kari yok eder).
    POZISYON SAYISI ise kismi kayitlari HARIC tutar."""
    if not yeni:
        return
    satir = []
    for k in yeni:
        kismi = bool(k.get("kismi"))
        satir.append("%s %s %s %+.2f$ (%s%s, %.1f sa)"
                     % ("YARIM" if kismi else "KAPANDI", k.get("sym"), k.get("yon"),
                        k.get("sonuc_usdt") or 0.0, k.get("sebep"),
                        "" if k.get("r") is None else " R=%.2f" % k["r"],
                        k.get("tutma_saat") or 0.0))
    tum = _defter_kayitlari()
    toplam = sum(t.get("sonuc_usdt") or 0 for t in tum)
    kapanan = len({t.get("id") for t in tum if not t.get("kismi")})
    msg = ("[DEFTER-3] " + " | ".join(satir)
           + "\nkasa $%.2f | acik %d/%d | kapanan poz %d | defter toplami %+.2f$"
             " (fonlama HARIC; kasa farkina dahil)"
           % (st["equity"], len(st["acik_pozisyonlar"]), MAKS_POZ, kapanan, toplam))
    print(msg)
    try:
        _tg(msg)
    except Exception:
        pass


def tur():
    """Bir tur: acik pozisyonlari BOTLA AYNI kurallarla yonet, sonra yeni giris ara.
    Kasa yoksa HICBIR SEY yapmaz (dosya olusturmaz) — --baslat gerekir."""
    st = yukle()
    if not st:
        return False
    yeni_kayit = []
    if st["acik_pozisyonlar"]:
        n0 = len(_defter_kayitlari())
        _defterde(testbot.yonet_acik_pozisyonlar, st)
        yeni_kayit = _defter_kayitlari()[n0:]   # bu turda dusen kapanis/TP1 kayitlari
    giris_ara(st)
    st["son_cycle_ts"] = testbot.now_iso()
    kaydet(st)
    equity_yaz(st)
    kapanis_bildir(yeni_kayit, st)             # state YAZILDIKTAN sonra bildir
    return True


def _karne(islemler):
    """id ile birlestirilmis pozisyon karnesi.

    ⚠️ CLAUDE.md: 'suzgec saymak icindir, toplamak icin degil' — P&L TOPLARKEN
    kismi kayitlar DAHIL (yoksa TP1'de realize edilen kar kaybolur);
    pozisyon SAYARKEN kismi kayitlar haric (TP1 pozisyonu ikiye boluyor)."""
    poz = {}
    for t in islemler:
        poz.setdefault(t["id"], []).append(t)
    out = {}
    for i, v in poz.items():
        v.sort(key=lambda z: z["ts"])
        s_ = v[-1]
        out[i] = {"yon": s_.get("yon"), "sym": s_.get("sym"), "sebep": s_.get("sebep"),
                  "net": sum(t.get("sonuc_usdt") or 0 for t in v),
                  "fon": sum(t["funding_usdt"] for t in v if t.get("funding_usdt") is not None),
                  "tut": max(t.get("tutma_saat") or 0 for t in v)}
    return out


def _satir(ad, v):
    if not v:
        return "  %-7s %4s %11s %9s %8s %8s" % (ad, 0, "-", "-", "-", "-")
    net = sum(p["net"] for p in v)
    kaz = sum(1 for p in v if p["net"] > 0)
    stop = sum(1 for p in v if p["sebep"] == "STOP")
    fon = sum(p["fon"] for p in v)
    return ("  %-7s %4d %+11.2f %8.0f%% %7.0f%% %+8.2f"
            % (ad, len(v), net, 100.0*kaz/len(v), 100.0*stop/len(v), fon))


def durum():
    st = yukle()
    if not st:
        print("DEFTER-3: henuz baslatilmadi ('python defter3.py --baslat').")
        return
    try:
        with open(ISLEMLERF, encoding="utf-8") as f:
            islemler = [json.loads(l) for l in f if l.strip()]
    except Exception:
        islemler = []
    poz = _karne(islemler)
    print("=== DEFTER-3 (defter2 evreni + IKI YON, sanal) ===")
    print("Evren: fiyat>$%.2f · funding>%.2f · chg24<%.0f · btc_pay!=UST"
          % (MIN_FIYAT, MIN_FUNDING, MAKS_CHG24))
    print("Yon  : chg24>=0 -> SHORT   ·   chg24<0 -> LONG   (defter2: hepsi SHORT)")
    print("Durum: %s | Bakiye: $%.0f -> $%.2f | Acik: %d/%d"
          % (st["durum"], st["baslangic_bakiye"], st["equity"],
             len(st["acik_pozisyonlar"]), MAKS_POZ))
    for p in st["acik_pozisyonlar"]:
        px = testbot.fiyat_fapi(p["sym"]) or p["giris"]
        yi = 1 if p["yon"] == "LONG" else -1
        print("  %-8s %-5s %sx giris=%.6g anlik=%.6g PnL=%+.2f$ stop=%.6g"
              % (p["sym"], p["yon"], p["kaldirac"], p["giris"], px,
                 (px-p["giris"])*p["miktar"]*yi, p["stop"]))

    print()
    print("  %-7s %4s %11s %9s %8s %8s" % ("kol", "N", "net $", "kazanan", "stop", "fonlama"))
    v = list(poz.values())
    print(_satir("LONG", [p for p in v if p["yon"] == "LONG"]))
    print(_satir("SHORT", [p for p in v if p["yon"] == "SHORT"]))
    print(_satir("TOPLAM", v))
    print("  (fonlama: pozisyon LEHINE isaretli, dolar. 'net' fonlamayi ICERMEZ —"
          " CLAUDE.md: sonuc_usdt fonlamasiz.)")

    # --- defter2 ile yan yana ------------------------------------------------
    d2i = os.path.join(HERE, "defter2_islemler.jsonl")
    d2s = os.path.join(HERE, "defter2_state.json")
    if os.path.exists(d2i) and os.path.exists(d2s):
        try:
            with open(d2i, encoding="utf-8") as f:
                d2 = _karne([json.loads(l) for l in f if l.strip()])
            with open(d2s, encoding="utf-8") as f:
                s2 = json.load(f)
            print()
            print("  --- YAN YANA (ayni evren, tek fark YON) ---")
            print("  %-9s %4s %11s %9s %8s" % ("defter", "N", "net $", "kazanan", "equity"))
            for ad, pz, stx in (("defter3", poz, st), ("defter2", d2, s2)):
                vv = list(pz.values())
                net = sum(p["net"] for p in vv)
                kaz = 100.0*sum(1 for p in vv if p["net"] > 0)/len(vv) if vv else 0
                print("  %-9s %4d %+11.2f %8.0f%% %8.0f" % (ad, len(vv), net, kaz, stx.get("equity", 0)))
            print("  ⚠️ Iki defter AYNI GUN baslamadi; kiyas ancak ORTAK pencerede gecerli.")
        except Exception:
            pass

    print()
    print("Kapanan pozisyon: %d | Toplam P&L: %+.2f$"
          % (len(poz), sum(p["net"] for p in poz.values())))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--baslat", action="store_true", help="kasayi ILK KEZ olustur")
    ap.add_argument("--tur", action="store_true")
    ap.add_argument("--durum", action="store_true")
    a = ap.parse_args()
    if a.baslat:
        if yukle():
            print("DEFTER-3 zaten var — --baslat yok sayildi (kasa SIFIRLANMADI).")
        else:
            kaydet(yeni_state())
            print("DEFTER-3 olusturuldu: %s" % STATEF)
    elif a.tur:
        print("tur tamam" if tur() else "kasa yok — once --baslat")
    else:
        durum()
