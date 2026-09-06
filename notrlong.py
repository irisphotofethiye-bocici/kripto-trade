#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NOTR-LONG BOTU — iki kol (2026-09-06, kullanici karari).

ON-KAYIT: ON_KAYIT_notr_long_botu.md, commit 4927f3d — KURULMADAN ONCE yazildi.
Tasarim orada; burada YENIDEN YAZILMAZ, yalnizca UYGULANIR.

NE: Rejim etiketi ZORLA "NOTR" tutulur ve YALNIZ LONG acilir.
    Dayanak: 2026-09-05 karsi-olgu olcumu — 08-19..09-02 penceresinde gercek bot
    -4.630,48 $ iken "NOTR kalsa + yalniz LONG" kolu +1.162,78 $ yapiyordu
    (K1/K2/K3 gecti; bugune kadar YOGUNLASMA testini gecen TEK olumlu sonuc).

IKI KOL — tek degisken: SKOR KAPISI
    N1: skor kapisi YOK
    N2: skor kapisi VAR (score >= 45), baska her sey N1 ile BIREBIR AYNI
    Ikisi AYNI TURDA, AYNI adaylarla, AYNI mekanikle kosar -> N1-N2 farki
    dogrudan "skor kapisi ne katiyor"un cevabidir.

🔴 KENDI TARAMASINI YAPAR — defter2/defter3'ten AYRILDIGI TEK YER.
    Sebep olculdu (2026-09-05): testbot.maks_pozisyon=0 olunca yeni_giris_ara
    aday taramasindan ONCE donuyor (testbot.py:1376) ve testbot_aday_arsiv.jsonl
    YAZILMIYOR. defter2/3 o arsivden besleniyor; bu bot beslenseydi HIC aday
    gormezdi. O yuzden evren/radar dogrudan cagrilir.
    ⚠️ testbot_aday_arsiv.jsonl'e YAZMAZ — 6 cozumleyici onu okuyor
    (CLAUDE.md: "arsive yeni tip kayit KARISTIRILMAZ").

🔴 SABIT %10 HEDEF ELLE KURULUR.
    testbot.yeni_giris_ac sabit hedefi YALNIZ sebep "A+B"/"MA50+ucuz" ile
    baslarsa atiyor (testbot.py:1293). Bizim sebebimiz oyle olamaz — o alani 6
    cozumleyici okuyor, kirletmek kapi karnesini bozar. Cozum: pozisyon
    ACILDIKTAN SONRA kendi state'imizde duzeltilir. testbot'a dokunulmaz.

🔴 DOKUNULMAYANLAR: testbot.py · golge.py · ayna.py · benim.py · defter2/3 ·
    radar.py · evren.py · kripto-config.json · mevcut state/defterler ·
    mevcut zamanlanmis gorevler. HICBIRI.
    Config'te DEGISIKLIK GEREKMEDI — asgari_stop_pct 2,0 · islem_risk_pct 1,5 ·
    kaldirac [3,10] · maks_dusus_pct 25 · zaman_stop 48s zaten on-kayitla birebir.

🔴 print() ICINDE EMOJI YOK — BILEREK.
    Windows konsolu cp1254; emoji ve varyasyon secicileri o kodlamada YOK ve
    cikti YONLENDIRILINCE UnicodeEncodeError ile betigi OLDURUR. Bu bot
    zamanlanmis gorevle ve ciktisi bir dosyaya yonlendirilerek kosacak, yani
    tam o kosulda. (Olculdu 2026-09-06: emoji/U+26A0/U+FE0F cokertiyor;
    orta nokta, em-dash ve Turkce harfler cp1254'te VAR, guvenli.)
    Yorumlarda emoji serbest — onlar basilmiyor.

Kullanim:
    python notrlong.py --baslat     iki kasayi ILK KEZ olusturur
    python notrlong.py --tur        bir tur (yonet + tara + iki kola giris ara)
    python notrlong.py --durum      iki kolu yan yana raporlar
"""
import json, os, sys, time, random, argparse

import testbot
import evren
import radar
from nobetci import telegram_gonder as _tg

HERE = os.path.dirname(os.path.abspath(__file__))

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")

# --- ON-KAYIT bolum 3: BOTUN TANIMI. Burada SABIT, taranmaz. ---
MAKS_POZ = 8
SKOR_KAPISI = 45.0          # yalniz N2
SABIT_HEDEF_PCT = 10.0      # kismi kar KAPALI, iz-suren KAPALI
TEKRAR_SAAT = 4.0
REJIM_ZORLA = "NOTR"

KOLLAR = ("n1", "n2")


def _yol(kol, ek):
    return os.path.join(HERE, "notrlong_%s_%s" % (kol, ek))


def yeni_state():
    return {"baslangic_ts": testbot.now_iso(), "baslangic_bakiye": 10000.0,
            "equity": 10000.0, "durum": "AKTIF", "acik_pozisyonlar": [],
            "sonraki_id": 1, "cooldown": {}, "bekleyenler": {}, "veto_cooldown": {},
            "son_giris": {}, "son_cycle_ts": None}


def yukle(kol):
    try:
        with open(_yol(kol, "state.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def kaydet(kol, st):
    """ATOMIK yazim (.tmp + os.replace) — CLAUDE.md kurali.
    golge.py duz json.dump kullaniyor ve defteri 2026-08-11'de 314 $ saptirmisti."""
    yol = _yol(kol, "state.json")
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
    os.replace(tmp, yol)


def _sessiz(*a, **kw):
    return None


def _defterde(kol, fn, *a, **kw):
    """testbot fonksiyonunu BU kolun defterine yonlendirerek + SESSIZ calistir.

    DORT takas, finally ile MUTLAKA geri alinir (defter2 deseni):
      _DEFTER        -> kapanan islemler bu deftere yazilsin
      telegram/toast -> bota ait olmayan hareket bot bildirimi gibi gitmesin
      VETO_LOGF      -> botun veto_log.jsonl'ine SIZMASIN (golge.py'de eksik olan koruma)

    ⚠️ testbot._aynala zaten "_DEFTER is not None -> aynalamaz" korumasi tasiyor,
       yani bu takas ayna sizintisini da kapatir (CLAUDE.md'de UC KEZ isiran sinif).
    """
    eski = (testbot._DEFTER, testbot.telegram_gonder,
            testbot.toast_gonder, testbot.VETO_LOGF)
    testbot._DEFTER = _yol(kol, "islemler.jsonl")
    testbot.telegram_gonder = _sessiz
    testbot.toast_gonder = _sessiz
    testbot.VETO_LOGF = _yol(kol, "veto.jsonl")
    try:
        return fn(*a, **kw)
    finally:
        (testbot._DEFTER, testbot.telegram_gonder,
         testbot.toast_gonder, testbot.VETO_LOGF) = eski


# ---------------------------------------------------------------------------
def sabit_hedef_kur(st, yon):
    """Yeni acilan pozisyonu SABIT %10 HEDEF moduna cevirir.

    testbot.py:1293-1322'deki 'ab_hedef > 0 ve pay == 0' dalinin BIREBIR ayni
    alanlari yazilir. Neden burada: o dal yalniz sebep "A+B"/"MA50+ucuz" ile
    baslarsa calisiyor; bizim sebebimiz oyle olamaz (sebep alanini 6 cozumleyici
    okuyor). Yalnizca KENDI state'imize dokunur.

    Etkisi (testbot'un kendi kodundan):
      trailing_guncelle  -> cikis_modu=="sabit_hedef" ise ERKEN DONER (iz-suren KAPALI)
      tp1_efektif_hesapla-> bu modda ATLANIR
      tp1_alindi=True    -> kismi kar yolu KAPALI
    """
    if not st["acik_pozisyonlar"]:
        return False
    pos = st["acik_pozisyonlar"][-1]
    g = pos.get("giris")
    if not g:
        return False
    hedef = g * (1 + SABIT_HEDEF_PCT / 100.0) if yon == "LONG" \
        else g * (1 - SABIT_HEDEF_PCT / 100.0)
    pos["cikis_modu"] = "sabit_hedef"
    pos["sabit_hedef_pct"] = SABIT_HEDEF_PCT
    pos["tp2"] = round(hedef, 6)
    pos["tp1_alindi"] = True          # kismi kar KAPALI (config kismi_pay'i BYPASS edilir)
    pos["tp1"] = pos["tp2"]
    pos["kaynak"] = "notrlong"
    return True


def fren_kontrol(st):
    """maks_dusus_pct — ON-KAYIT bolum 7: tetiklenirse DURUR."""
    esik = float(testbot._c("maks_dusus_pct", 25))
    if esik <= 0 or st["durum"] != "AKTIF":
        return
    tepe = max(st.get("zirve", st["baslangic_bakiye"]), st["equity"])
    st["zirve"] = tepe
    if st["equity"] <= st["baslangic_bakiye"] * (1 - esik / 100.0):
        st["durum"] = "DURDU"
        msg = ("[NOTRLONG] *** DUSUS FRENI: equity %.2f $ (baslangic %.0f, -%%%.0f) "
               "-> YENI GIRIS YOK. On-kayit bolum 7: bu kol KAPATILIR."
               % (st["equity"], st["baslangic_bakiye"], esik))
        print(msg)
        try:
            _tg(msg)
        except Exception:
            pass


def _tekrar_var_mi(st, sym):
    son = st.get("son_giris", {}).get(sym)
    if not son:
        return False
    try:
        return (testbot.now_dt() - testbot.parse_iso(son)).total_seconds() / 3600 < TEKRAR_SAAT
    except Exception:
        return False


# ---------------------------------------------------------------------------
def tara():
    """KENDI aday taramasi. testbot.yeni_giris_ara'nin tarama kismiyla ayni,
    ama karar/giris kismi YOK ve aday arsivine YAZMAZ.
    -> [(r, pillar)] skor sirali kisa liste"""
    min_vol = float(testbot._c("min_vol_musd", 3))
    havuz_n = int(testbot._c("tarama_havuz_n", 150))
    cryptos = evren.cg_universe()
    pool = evren.binance_pool("fapi", min_vol,
                              cryptos=(set(cryptos.keys()) if cryptos else None))[:havuz_n]
    chg24_harita = {s: chg for s, _, chg in pool}
    syms = [s for s, _, _ in pool]
    if not syms:
        return [], {}
    btc_chg3, _ = radar.btc_ref()
    rows = []
    for sym in syms:
        try:
            r = radar.analyze(sym, btc_chg3)
            if r and r["score"] >= 30:
                r["chg24"] = chg24_harita.get(sym, 0.0)
                rows.append(r)
        except Exception:
            continue
        time.sleep(random.uniform(0.05, 0.15))      # rate-limit guvenlik payi

    # SIRALAMA: testbot ile AYNI (skor + HAZIRLANIYOR bonusu). Bir kapi DEGIL,
    # kapasite kuyrugudur; hukum yazilirken "skor sirasiyla alindi" notu dusulur.
    bonus = evren.esik("hazirlaniyor_sira_bonus", 8.0)
    rows.sort(key=lambda x: -(x["score"] + (bonus if x.get("stage") == "HAZIRLANIYOR" else 0.0)))
    rows = rows[:10]

    pillars = {}
    for r in rows:
        try:
            pillars[r["sym"]] = radar.pillar_d(r["sym"])
        except Exception:
            pillars[r["sym"]] = {"top_ls": None, "glob_ls": None,
                                 "taker": None, "smart": None}
    return rows, pillars


def giris_ara(kol, st, rows, pillars, baglam):
    """Bir kol icin karar + giris. -> acilan sayisi

    Rejim ZORLA 'NOTR'. YALNIZ LONG. Vetolar AYNEN (long_veto/blowoff/onay_bekle
    karar_yon'un icinde; asgari_stop ve rr kapisi yeni_giris_ac'in icinde)."""
    if st["durum"] != "AKTIF":
        return 0
    if len(st["acik_pozisyonlar"]) >= MAKS_POZ:
        return 0
    acik = {p["sym"] for p in st["acik_pozisyonlar"]}
    bekleyenler = st.setdefault("bekleyenler", {})
    gorulen = {r["sym"] for r in rows}
    for s in list(bekleyenler):
        if s not in gorulen:
            bekleyenler[s]["cycle_sayaci"] = bekleyenler[s].get("cycle_sayaci", 0) + 1
            if bekleyenler[s]["cycle_sayaci"] > 6:
                del bekleyenler[s]

    acilan = 0
    for r in rows:
        if len(st["acik_pozisyonlar"]) >= MAKS_POZ:
            break
        sym = r["sym"]
        if sym in acik or _tekrar_var_mi(st, sym):
            continue
        pillar = pillars.get(sym, {})

        vlist = []
        karar = testbot.karar_yon(REJIM_ZORLA, r, pillar, False, veto_out=vlist,
                                  para_cikis=baglam["para_cikis"],
                                  btc_pay=baglam["btc_pay"],
                                  para_durgun=baglam["para_durgun"])
        if not karar:
            bekleyenler.pop(sym, None)
            continue
        yon, mod, sebep = karar
        if yon != "LONG":                    # YALNIZ LONG — SHORT kararlari atilir
            bekleyenler.pop(sym, None)
            continue
        # --- TEK DEGISKEN: skor kapisi (yalniz N2) ---
        if kol == "n2" and (r.get("score") or 0) < SKOR_KAPISI:
            bekleyenler.pop(sym, None)
            continue

        sebep_tam = "NOTRLONG-%s: rejim zorla NOTR + yalniz LONG | %s" % (kol.upper(), sebep)

        def _ac(ek=""):
            red = []
            ok = _defterde(kol, testbot.yeni_giris_ac, st, sym, "LONG", r, pillar,
                           sebep_tam + ek, zorla=False, rejim_ad=REJIM_ZORLA,
                           kaynak="notrlong", red_out=red)
            if ok:
                sabit_hedef_kur(st, "LONG")
                st.setdefault("son_giris", {})[sym] = testbot.now_iso()
                print("[%s] ACILDI %s LONG (skor %s · chg24 %s)"
                      % (kol, sym, r.get("score"), r.get("chg24")))
            elif red:
                print("[%s] giris kapisi %s: %s" % (kol, sym, red[0]["kapi"]))
            return bool(ok)

        if mod == "ANINDA":
            bekleyenler.pop(sym, None)
            if _ac():
                acilan += 1
            continue

        # ONAY_BEKLE korunur (on-kayit bolum 3)
        onceki = bekleyenler.get(sym)
        if onceki and onceki.get("yon") == yon:
            onceki["cycle_sayaci"] = onceki.get("cycle_sayaci", 0) + 1
            if onceki["cycle_sayaci"] >= 1:
                del bekleyenler[sym]
                if _ac(" (onaylandi)"):
                    acilan += 1
        else:
            bekleyenler[sym] = {"yon": yon, "skor": r.get("score"),
                                "ilk_gorulme_ts": testbot.now_iso(), "cycle_sayaci": 0}
    return acilan


def equity_yaz(kol, st):
    try:
        testbot._append_jsonl(_yol(kol, "equity.jsonl"), {
            "ts": testbot.now_iso(), "equity": round(st["equity"], 2),
            "acik_pnl": round(testbot.acik_pnl_toplam(st), 2),
            "acik_sayisi": len(st["acik_pozisyonlar"]), "durum": st["durum"]})
    except Exception:
        pass


def _defter_kayitlari(kol):
    try:
        with open(_yol(kol, "islemler.jsonl"), encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]
    except Exception:
        return []


def kapanis_bildir(kol, yeni, st):
    """Bu turda deftere DUSEN kayitlari bildirir.
    ⚠️ CLAUDE.md: P&L TOPLARKEN kismi kayitlar DAHIL; POZISYON SAYARKEN haric."""
    if not yeni:
        return
    satir = []
    for k in yeni:
        satir.append("%s %s %+.2f$ (%s, %.1f sa)"
                     % ("YARIM" if k.get("kismi") else "KAPANDI", k.get("sym"),
                        k.get("sonuc_usdt") or 0.0, k.get("sebep"),
                        k.get("tutma_saat") or 0.0))
    tum = _defter_kayitlari(kol)
    toplam = sum(t.get("sonuc_usdt") or 0 for t in tum)
    kapanan = len({t.get("id") for t in tum if not t.get("kismi")})
    msg = ("[NOTRLONG-%s] " % kol.upper() + " | ".join(satir)
           + "\nkasa $%.2f | acik %d/%d | kapanan poz %d | defter toplami %+.2f$"
             " (fonlama HARIC; kasa farkina dahil)"
           % (st["equity"], len(st["acik_pozisyonlar"]), MAKS_POZ, kapanan, toplam))
    print(msg)
    try:
        _tg(msg)
    except Exception:
        pass


# ---------------------------------------------------------------------------
def tur():
    """Bir tur: her iki kolun acik pozisyonlarini yonet, SONRA tek tarama yapip
    iki kola da AYNI adaylari ver.

    ⚠️ SIRA ONEMLI: yonetim (cikislar) ONCE, giris arama SONRA — testbot ile ayni.
    Boylece MAKS_POZ dolu olsa bile cikislar isler."""
    durumlar = {}
    for kol in KOLLAR:
        st = yukle(kol)
        if not st:
            return False
        durumlar[kol] = st

    # 1) ACIK POZISYONLARI YONET (cikislar)
    yeni_kayitlar = {}
    for kol, st in durumlar.items():
        yeni_kayitlar[kol] = []
        if st["acik_pozisyonlar"]:
            n0 = len(_defter_kayitlari(kol))
            _defterde(kol, testbot.yonet_acik_pozisyonlar, st)
            yeni_kayitlar[kol] = _defter_kayitlari(kol)[n0:]
        fren_kontrol(st)

    # 2) TEK TARAMA — iki kol AYNI adaylari gorur (tek degisken skor kapisi kalsin)
    aktif = [k for k, s in durumlar.items()
             if s["durum"] == "AKTIF" and len(s["acik_pozisyonlar"]) < MAKS_POZ]
    if aktif:
        try:
            rows, pillars = tara()
        except Exception as e:
            print("[notrlong] tarama hatasi (tur atlandi): %s" % str(e)[:100])
            rows, pillars = [], {}
        if rows:
            _pr = evren.para_rejim()
            try:
                evren.btc_pay_guncelle()
                bp = evren.btc_pay_akisi()
            except Exception:
                bp = None
            baglam = {"para_cikis": bool(_pr and _pr.get("rejim") == "PARA CIKIYOR"),
                      "para_durgun": bool(_pr and _pr.get("rejim") == "PARA DURGUN"),
                      "btc_pay": bp}
            for kol in aktif:
                giris_ara(kol, durumlar[kol], rows, pillars, baglam)

    # 3) KAYDET + LOG + BILDIR
    for kol, st in durumlar.items():
        st["son_cycle_ts"] = testbot.now_iso()
        kaydet(kol, st)
        equity_yaz(kol, st)
        kapanis_bildir(kol, yeni_kayitlar[kol], st)
    return True


def _karne(kayitlar):
    """id ile birlestirilmis pozisyon karnesi.
    ⚠️ CLAUDE.md: 'suzgec saymak icindir, toplamak icin degil'."""
    poz = {}
    for t in kayitlar:
        poz.setdefault(t["id"], []).append(t)
    out = {}
    for i, v in poz.items():
        v.sort(key=lambda z: z.get("ts") or "")
        s = v[-1]
        out[i] = {"sym": s.get("sym"), "sebep": s.get("sebep"),
                  "net": sum(t.get("sonuc_usdt") or 0 for t in v),
                  "fon": sum(t["funding_usdt"] for t in v
                             if t.get("funding_usdt") is not None)}
    return out


def durum():
    print("=== NOTR-LONG BOTU (on-kayit 4927f3d) ===")
    print("Karar: rejim ZORLA %s · YALNIZ LONG · sabit %%%.0f hedef · kismi kar KAPALI"
          % (REJIM_ZORLA, SABIT_HEDEF_PCT))
    print("Kol farki: N1 skor kapisi YOK · N2 skor >= %.0f" % SKOR_KAPISI)
    print()
    print("  %-5s %-8s %10s %6s %6s %11s %9s %10s"
          % ("kol", "durum", "equity", "acik", "poz", "net $", "kazanan", "fonlama"))
    for kol in KOLLAR:
        st = yukle(kol)
        if not st:
            print("  %-5s (baslatilmadi)" % kol)
            continue
        poz = _karne(_defter_kayitlari(kol))
        v = list(poz.values())
        net = sum(p["net"] for p in v)
        kaz = (100.0 * sum(1 for p in v if p["net"] > 0) / len(v)) if v else 0
        fon = sum(p["fon"] for p in v)
        print("  %-5s %-8s %10.2f %6d %6d %+11.2f %8.0f%% %+10.2f"
              % (kol, st["durum"], st["equity"], len(st["acik_pozisyonlar"]),
                 len(v), net, kaz, fon))
    print()
    for kol in KOLLAR:
        st = yukle(kol)
        if not st or not st["acik_pozisyonlar"]:
            continue
        print("  --- %s acik pozisyonlar ---" % kol)
        for p in st["acik_pozisyonlar"]:
            px = testbot.fiyat_fapi(p["sym"]) or p["giris"]
            print("   %-10s %-5s %sx giris=%.6g anlik=%.6g PnL=%+.2f$ stop=%.6g hedef=%.6g"
                  % (p["sym"], p["yon"], p.get("kaldirac"), p["giris"], px,
                     (px - p["giris"]) * p["miktar"], p["stop"], p.get("tp2") or 0))
    print()
    print("UYARI: Pencere: 30 gun VE kol basina >=80 KAPANMIS pozisyon — IKISI BIRDEN")
    print("   dolmadan hukum YOK (on-kayit bolum 5).")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--baslat", action="store_true", help="iki kasayi ILK KEZ olustur")
    ap.add_argument("--tur", action="store_true")
    ap.add_argument("--durum", action="store_true")
    a = ap.parse_args()
    if a.baslat:
        for kol in KOLLAR:
            if yukle(kol):
                print("NOTRLONG-%s zaten var — atlandi (kasa SIFIRLANMADI)." % kol.upper())
            else:
                kaydet(kol, yeni_state())
                print("NOTRLONG-%s olusturuldu: %s" % (kol.upper(), _yol(kol, "state.json")))
    elif a.tur:
        print("tur tamam" if tur() else "kasa yok — once --baslat")
    else:
        durum()
