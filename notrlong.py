#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NOTR-LONG BOTU — TEK KOL (2026-09-06, kullanici karari).

ON-KAYIT: ON_KAYIT_notr_long_botu.md, commit 4927f3d — kurulmadan ONCE yazildi.
   🔴 BOLUM 11 [DEGISTI 2026-09-06]: skor kapisi KALDIRILDI, iki kol -> tek kol.
   Tasarim orada; burada YENIDEN YAZILMAZ, yalnizca UYGULANIR.

NE: Rejim etiketi ZORLA "NOTR" tutulur ve YALNIZ LONG acilir.
    Dayanak: 2026-09-05 karsi-olgu olcumu — 08-21..09-02 penceresinde gercek bot
    -1.719,78 $ iken "NOTR + yalniz LONG" kolu +967,45 $ yapiyordu ve
    YOGUNLASMA testinden sag cikan TEK olumlu sonuctu.

🔴 NEDEN TEK KOL (eski iki-kollu tasarim kaldirildi):
    "N1: skor kapisi YOK" ifadesi YANLISTI — skor zaten uc yerde is goruyor:
      (a) tara(): radar.analyze sonucu score >= 30 suzgeci
      (b) tara(): kisa liste SKORA GORE siralanip [:10] kirpiliyor
      (c) karar_yon: skor >= stage_esigi  (BASLIYOR 45 · HAZIRLANIYOR 40)
    Ve karar_yon zaten BASLIYOR icin >=45 istedigi icin, N2'nin >=45 kapisi
    yalnizca HAZIRLANIYOR dalinda [40,45) araligini kesiyordu.
    ARSIVDE OLCULDU (N=34.618): iki kol adaylarin yalniz %8,5'inde ayrisiyordu
    -> fark gurultuden ayirt edilemezdi.
    SKOR SORUSU KAYBOLMADI: defter her girisin `skor_giriste` alanini yaziyor,
    sonradan ayni defterde olculur (skor_gercek.py deseni).

🔴 KENDI TARAMASINI YAPAR — defter2/defter3'ten AYRILDIGI TEK YER.
    Sebep olculdu (2026-09-05): testbot.maks_pozisyon=0 olunca yeni_giris_ara
    aday taramasindan ONCE donuyor (testbot.py:1376) ve testbot_aday_arsiv.jsonl
    YAZILMIYOR. defter2/3 o arsivden besleniyor; bu bot beslenseydi HIC aday
    gormezdi. O yuzden evren/radar dogrudan cagrilir.
    ⚠️ testbot_aday_arsiv.jsonl'e YAZMAZ — 6 cozumleyici onu okuyor.

🔴 SABIT %10 HEDEF ELLE KURULUR.
    testbot.yeni_giris_ac sabit hedefi YALNIZ sebep "A+B"/"MA50+ucuz" ile
    baslarsa atiyor (testbot.py:1293). Bizim sebebimiz oyle olamaz — o alani 6
    cozumleyici okuyor. Cozum: pozisyon ACILDIKTAN SONRA kendi state'imizde
    duzeltilir. testbot'a dokunulmaz. Bu ayrica config'teki kismi_pay'i BYPASS
    eder (on-kayit: kismi kar KAPALI).

🔴 print() ICINDE EMOJI YOK — BILEREK.
    Windows konsolu cp1254; emoji ve varyasyon secicileri o kodlamada YOK ve
    cikti YONLENDIRILINCE UnicodeEncodeError ile betigi OLDURUR. (Olculdu
    2026-09-06: emoji/U+26A0/U+FE0F cokertiyor; orta nokta, em-dash ve Turkce
    harfler cp1254'te VAR, guvenli.) Yorumlarda emoji serbest — basilmiyor.

🔴 DOKUNULMAYANLAR: testbot.py · golge.py · ayna.py · benim.py · defter2/3 ·
    radar.py · evren.py · kripto-config.json. HICBIRI.
    Config'te DEGISIKLIK GEREKMEDI — asgari_stop_pct 2,0 · islem_risk_pct 1,5 ·
    kaldirac [3,10] · maks_dusus_pct 25 · zaman_stop 48s zaten on-kayitla birebir.

Kullanim:
    python notrlong.py --baslat     kasayi ILK KEZ olusturur
    python notrlong.py --tur        bir tur (yonet + tara + giris ara)
    python notrlong.py --durum      rapor
"""
import json, os, sys, time, random, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
LOGF = os.path.join(HERE, "notrlong_log.txt")

# 🔴 LOG KURULUMU PROJE MODULLERINDEN ONCE OLMAK ZORUNDA.
#    testbot.py:46 (ayrica radar.py:22, nobetci.py:26) "sys.stdout is None ise
#    devnull'a bagla" yapiyor. `import testbot` once kosarsa stdout ARTIK None
#    OLMAZ ve buradaki dal HIC CALISMAZ — olculdu (2026-09-06): log dosyasi
#    olusmadi, stdout 'nul' kaldi. O yuzden bu blok import'larin USTUNDE.
if sys.stdout is None:                      # pythonw ile kosarken
    try:
        if os.path.exists(LOGF) and os.path.getsize(LOGF) > 5_000_000:
            os.replace(LOGF, LOGF + ".1")   # basit donusum, tek yedek
    except Exception:
        pass
    try:
        sys.stdout = open(LOGF, "a", encoding="utf-8", buffering=1)
        sys.stderr = sys.stdout
    except Exception:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")

import testbot          # noqa: E402  (log kurulumu YUKARIDA olmak zorunda)
import evren            # noqa: E402
import radar            # noqa: E402
from nobetci import telegram_gonder as _tg   # noqa: E402

# --- ON-KAYIT bolum 3: BOTUN TANIMI. Burada SABIT, taranmaz. ---
MAKS_POZ = 8
SABIT_HEDEF_PCT = 10.0      # kismi kar KAPALI, iz-suren KAPALI
TEKRAR_SAAT = 4.0
REJIM_ZORLA = "NOTR"

STATEF = os.path.join(HERE, "notrlong_state.json")
ISLEMLERF = os.path.join(HERE, "notrlong_islemler.jsonl")
EQUITYF = os.path.join(HERE, "notrlong_equity.jsonl")
VETOF = os.path.join(HERE, "notrlong_veto.jsonl")
ELENENF = os.path.join(HERE, "notrlong_elenen.jsonl")

# --- ELENEN ADAY KAYDI (2026-09-06, kullanici karari) ----------------------
# [NEDEN] Kullanici sordu: "botun eledigi coinlere poz acsaydi ne olurdu?"
#   Cevap verilemedi cunku bot reddettiklerini KAYDETMIYORDU. testbot'ta bu isi
#   `golge` defteri yapiyor; bu botun karsiligi yoktu.
# [D/8 GUVENLIGI] Bu ekleme HANGI ISLEMIN ACILACAGINI DEGISTIRMEZ — yalnizca
#   yazar. Dolayisiyla olcum penceresini SIFIRLAMAZ. (Kullanici ayrica
#   "botu yeni kurduk, maliyeti yok" dedi.)
# [FAIL-SAFE] Yazim hatasi botu DURDURMAZ.
# ⚠️ SINIR: skor/smart basamaklari burada YENIDEN URETILIYOR cunku
#   karar_yon o dallarda adlandirilmis veto URETMEDEN None donuyor. testbot'un
#   mantigi degisirse bu kopya KAYABILIR ve log yanlis basamak yazabilir —
#   kayit yalnizca TESHIS icindir, hukum dayanagi degildir. 4-6. basamaklar
#   karar_yon'un GERCEK veto kategorilerinden gelir.


def _huni_basamagi(r, pillar, vlist):
    """Aday NOTR-LONG zincirinde NEREDE oldu. Yalnizca KAYIT icin.

    [DEGISTI 2026-09-06] stage ve taker KAPI DEGIL artik -> huni de oyle sayar.
    'izle' adaylari HAZIRLANIYOR esigiyle (radar_alert_skor) degerlendirilir,
    cunku kod da onlari oyle yeniden deniyor."""
    stage = r.get("stage")
    skor = r.get("score") or 0
    esik_hazir = evren.esik("radar_alert_skor", 40.0)
    # stage kapisi kalktigi icin 'izle' de HAZIRLANIYOR esigine tabi
    esik = esik_hazir if stage in ("HAZIRLANIYOR", "izle", None) else esik_hazir + 5
    if skor < esik:
        return "2_skor_dusuk"
    if pillar.get("smart") != "LONG":
        return "3_smart_degil"
    if vlist:
        return "4_" + str(vlist[0].get("kategori"))
    return "9_bilinmiyor"


def _elenen_yaz(r, pillar, kapi, detay=""):
    """Reddedilen adayi kaydet. FAIL-SAFE."""
    try:
        testbot._append_jsonl(ELENENF, {
            "ts": testbot.now_iso(), "sym": r.get("sym"), "kapi": kapi,
            "detay": (detay or "")[:120],
            "price": r.get("price"), "score": r.get("score"),
            "stage": r.get("stage"), "chg24": r.get("chg24"),
            "smart": pillar.get("smart"), "taker": pillar.get("taker"),
            "top_ls": pillar.get("top_ls"), "glob_ls": pillar.get("glob_ls"),
            "funding": r.get("funding"), "pos": r.get("pos"),
            "vol_x": r.get("vol_x"), "comp": r.get("comp"),
        })
    except Exception:
        pass


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
    golge.py duz json.dump kullaniyor ve defteri 2026-08-11'de 314 $ saptirmisti."""
    tmp = STATEF + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATEF)


def _sessiz(*a, **kw):
    return None


def _defterde(fn, *a, **kw):
    """testbot fonksiyonunu BU deftere yonlendirerek + SESSIZ calistir.

    DORT takas, finally ile MUTLAKA geri alinir (defter2 deseni):
      _DEFTER        -> kapanan islemler bu deftere yazilsin
      telegram/toast -> bota ait olmayan hareket bot bildirimi gibi gitmesin
      VETO_LOGF      -> botun veto_log.jsonl'ine SIZMASIN (golge.py'de eksik koruma)

    ⚠️ testbot._aynala zaten "_DEFTER is not None -> aynalamaz" korumasi tasiyor,
       yani bu takas ayna sizintisini da kapatir (CLAUDE.md'de UC KEZ isiran sinif).
    """
    eski = (testbot._DEFTER, testbot.telegram_gonder,
            testbot.toast_gonder, testbot.VETO_LOGF)
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
def sabit_hedef_kur(st, yon):
    """Yeni acilan pozisyonu SABIT %10 HEDEF moduna cevirir.

    testbot.py:1293-1322'deki 'ab_hedef > 0 ve pay == 0' dalinin BIREBIR ayni
    alanlari yazilir. Yalnizca KENDI state'imize dokunur.

    Etkisi (testbot'un kendi kodundan):
      trailing_guncelle   -> cikis_modu=="sabit_hedef" ise ERKEN DONER (iz-suren KAPALI)
      tp1_efektif_hesapla -> bu modda ATLANIR
      tp1_alindi=True     -> kismi kar yolu KAPALI
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
    pos["tp1_alindi"] = True          # kismi kar KAPALI (config kismi_pay BYPASS)
    pos["tp1"] = pos["tp2"]
    pos["kaynak"] = "notrlong"
    return True


def fren_kontrol(st):
    """maks_dusus_pct — ON-KAYIT bolum 7: tetiklenirse DURUR."""
    esik = float(testbot._c("maks_dusus_pct", 25))
    if esik <= 0 or st["durum"] != "AKTIF":
        return
    st["zirve"] = max(st.get("zirve", st["baslangic_bakiye"]), st["equity"])
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
    -> (rows, pillars)"""
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


def giris_ara(st, rows, pillars, baglam):
    """Karar + giris. -> acilan sayisi

    Rejim ZORLA 'NOTR'. YALNIZ LONG. Vetolar AYNEN (long_veto/blowoff/onay_bekle
    karar_yon'un icinde; asgari_stop ve rr kapisi yeni_giris_ac'in icinde).
    EK SKOR KAPISI YOK — on-kayit bolum 11."""
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
        pillar = pillars.get(sym, {})
        # KAPASITE elemesi — filtre degil, ama olculmesi gerekiyor: onceki bir
        # olcumde "ayni sembol zaten ACIK" gercek baglayici kisit cikmisti.
        if sym in acik:
            _elenen_yaz(r, pillar, "0_zaten_acik")
            continue
        if _tekrar_var_mi(st, sym):
            _elenen_yaz(r, pillar, "0_tekrar_bekleme", "%.1f saat" % TEKRAR_SAAT)
            continue

        vlist = []
        karar = testbot.karar_yon(REJIM_ZORLA, r, pillar, False, veto_out=vlist,
                                  para_cikis=baglam["para_cikis"],
                                  btc_pay=baglam["btc_pay"],
                                  para_durgun=baglam["para_durgun"])

        # --- TAKER KAPISI KALDIRILDI (2026-09-06, KULLANICI KARARI) ------------------
        # [NE] karar_yon YALNIZCA `taker_soguma` yuzunden None donduyse, ayni cagri
        #   pillar.taker = 1.0 ile TEKRARLANIR. Baska hicbir veto atlanmaz; vlist'te
        #   tek bir kayit ve kategorisi `taker_soguma` degilse bu dal CALISMAZ.
        # [NEDEN] ON_KAYIT_taker_kapisi.md (08c8876) · olcum 2b01efd:
        #   N=956 · 57 gun · 121 sembol. Bes olcutun BESI de dustu
        #   (ham fark -0,353 · last1-sabitlenmis -0,293 · gun-kumeli t -0,79 ·
        #    merdivende 1/5 · yogunlasma -0,807). Sabitleyicilerin BESI DE negatif.
        #   Kapinin KARARSIZLIGI da olculdu: karsi-olgu penceresinde taker>=1.0 kolu
        #   +1,01% iken onceki 40 gunde -4,41% -> ISARET DONUYOR.
        # [DURUSTLUK] Gorulen fark MDE'nin (2,57 puan) COK ALTINDA -> 'goremiyoruz',
        #   'zarari kanitlandi' DEGIL. Soylenebilen: +2,57 puandan buyuk bir YARAR YOK.
        # [BEDELI] Kapi adaylarin %56'sini kesiyordu (arsiv: smart-LONG 367 ->
        #   taker>=1.0 161) ve notrlong'da TERMINAL darbogazdi: stage+skor gecen
        #   6 adayin 6'si da burada oldu. Beklenen hiz 2,06 -> 4,70 poz/gun.
        # [KAPSAM] YALNIZ bu defter. testbot.py'ye DOKUNULMADI -> golge/ayna/
        #   defter2/defter3 ve NOTR-AYI botu AYNEN eski davranista.
        # GERI ALMA: asagidaki blogu sil (kapi kendiliginden geri gelir).
        if (not karar) and vlist and all(
                x.get("kategori") == "taker_soguma" for x in vlist):
            _tk = pillar.get("taker")
            vlist2 = []
            karar = testbot.karar_yon(REJIM_ZORLA, r, dict(pillar, taker=1.0), False,
                                      veto_out=vlist2,
                                      para_cikis=baglam["para_cikis"],
                                      btc_pay=baglam["btc_pay"],
                                      para_durgun=baglam["para_durgun"])
            if karar:
                karar = (karar[0], karar[1],
                         karar[2] + " [taker kapisi KALDIRILDI 2026-09-06; "
                                    "gercek taker=%s]" % _tk)
            else:
                vlist = vlist2 or vlist
        # ----------------------------------------------------------------------------

        # --- STAGE KAPISI KALDIRILDI (2026-09-06, KULLANICI KARARI) ------------------
        # [NE] karar_yon hala None ve adayin GERCEK stage'i "izle" ise, cagri
        #   stage="HAZIRLANIYOR" ve taker=1.0 ile TEKRARLANIR. Boylece NOTR-LONG
        #   dali acilir ve skor esigi radar_alert_skor (40) olur.
        #   🔴 KALITE FILTRELERI ACILMADI: asiri_yukselmis (blowoff) ve long_veto
        #   yamali cagrida da AYNEN calisir; yalniz stage ve taker on-sarti kalkar.
        # [NEDEN] Botun LONG yolu stage in (BASLIYOR, HAZIRLANIYOR) SART kosuyordu
        #   ama olculen sey bunun TERSI:
        #     giris aramasi (2026-09-06, kesif yarisi, A0 mekanigi, LONG):
        #       BASLIYOR     -0,4076 (N= 25)   <- bot BUNU sart kosuyordu
        #       HAZIRLANIYOR -0,3300 (N= 84)   <- ve BUNU
        #       izle         -0,1346 (N=897)   <- EN AZ KOTU, bot bunu ELIYORDU
        #     OTOPSI-3 (SHORT, 41 gun): BASLIYOR -0,09R (en kotu) · izle +0,07R ·
        #       HAZIRLANIYOR +0,19R
        #   Proje bu dersi BIR KEZ zaten uygulamisti: notr_fade dali stage sartindan
        #   CIKARILDI, gerekcesi "bot, en iyi stratejisi icin en kotu olculmus
        #   on-sarti dayatiyordu; havuzun %89'u izle" (testbot.py:700).
        # [ETKI — OLCULDU] radar_archive kisa listesi (N=57.570, pillar_d uygulanmis):
        #     MEVCUT  stage aktif + skor + smart LONG   956  (%1,66)
        #     STAGE KALKARSA  skor>=40 + smart LONG   5.945  (%10,33)
        #     -> 6,2 KAT aday
        # [DURUSTLUK] Ucu de NEGATIF olculdu (-0,13 .. -0,41). Bu degisiklik botu
        #   ISLEM ACAR hale getirir, KARLI hale getirmez. Olcum penceresi hakemdir.
        # [KAPSAM] YALNIZ bu defter. testbot.py'ye DOKUNULMADI.
        # GERI ALMA: asagidaki blogu sil.
        if (not karar) and r.get("stage") == "izle":
            vlist3 = []
            karar = testbot.karar_yon(REJIM_ZORLA,
                                      dict(r, stage="HAZIRLANIYOR"),
                                      dict(pillar, taker=1.0), False,
                                      veto_out=vlist3,
                                      para_cikis=baglam["para_cikis"],
                                      btc_pay=baglam["btc_pay"],
                                      para_durgun=baglam["para_durgun"])
            if karar:
                karar = (karar[0], karar[1],
                         karar[2] + " [stage kapisi KALDIRILDI 2026-09-06; "
                                    "gercek stage=izle]")
            else:
                vlist = vlist3 or vlist
        # ----------------------------------------------------------------------------

        if not karar:
            _elenen_yaz(r, pillar, _huni_basamagi(r, pillar, vlist),
                        (vlist[0].get("detay") if vlist else ""))
            bekleyenler.pop(sym, None)
            continue
        yon, mod, sebep = karar
        if yon != "LONG":                    # YALNIZ LONG — SHORT kararlari atilir
            _elenen_yaz(r, pillar, "5_short_karari", sebep)
            bekleyenler.pop(sym, None)
            continue

        sebep_tam = "NOTRLONG: rejim zorla NOTR + yalniz LONG | %s" % sebep

        def _ac(ek=""):
            red = []
            ok = _defterde(testbot.yeni_giris_ac, st, sym, "LONG", r, pillar,
                           sebep_tam + ek, zorla=False, rejim_ad=REJIM_ZORLA,
                           kaynak="notrlong", red_out=red)
            if ok:
                sabit_hedef_kur(st, "LONG")
                st.setdefault("son_giris", {})[sym] = testbot.now_iso()
                print("    ACILDI %s LONG (skor %s · chg24 %s · stage %s)"
                      % (sym, r.get("score"), r.get("chg24"), r.get("stage")))
            elif red:
                # Karar VERILDI ama giris kapisinda oldu (rr_veto / asgari_stop /
                # kaldirac_guvenlik...). Bunlar ayri bir sinif — kaydedilir.
                _elenen_yaz(r, pillar, "6_giris_" + str(red[0]["kapi"]),
                            red[0].get("detay", ""))
                print("    giris kapisi %s: %s" % (sym, red[0]["kapi"]))
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


def equity_yaz(st):
    try:
        testbot._append_jsonl(EQUITYF, {
            "ts": testbot.now_iso(), "equity": round(st["equity"], 2),
            "acik_pnl": round(testbot.acik_pnl_toplam(st), 2),
            "acik_sayisi": len(st["acik_pozisyonlar"]), "durum": st["durum"]})
    except Exception:
        pass


def _defter_kayitlari():
    try:
        with open(ISLEMLERF, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]
    except Exception:
        return []


def kapanis_bildir(yeni, st):
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
    tum = _defter_kayitlari()
    toplam = sum(t.get("sonuc_usdt") or 0 for t in tum)
    kapanan = len({t.get("id") for t in tum if not t.get("kismi")})
    msg = ("[NOTRLONG] " + " | ".join(satir)
           + "\nkasa $%.2f | acik %d/%d | kapanan poz %d/80 | defter toplami %+.2f$"
             " (fonlama HARIC; kasa farkina dahil)"
           % (st["equity"], len(st["acik_pozisyonlar"]), MAKS_POZ, kapanan, toplam))
    print(msg)
    try:
        _tg(msg)
    except Exception:
        pass


# ---------------------------------------------------------------------------
def tur():
    """Bir tur: acik pozisyonlari yonet, SONRA tara ve giris ara.
    ⚠️ SIRA ONEMLI: yonetim (cikislar) ONCE, giris arama SONRA — testbot ile ayni.
    Boylece MAKS_POZ dolu olsa bile cikislar isler."""
    t0 = time.time()
    print("--- tur %s ---" % testbot.now_iso())
    st = yukle()
    if not st:
        print("    kasa yok (once --baslat)")
        return False

    yeni_kayit = []
    if st["acik_pozisyonlar"]:
        n0 = len(_defter_kayitlari())
        _defterde(testbot.yonet_acik_pozisyonlar, st)
        yeni_kayit = _defter_kayitlari()[n0:]
    fren_kontrol(st)

    if st["durum"] == "AKTIF" and len(st["acik_pozisyonlar"]) < MAKS_POZ:
        try:
            rows, pillars = tara()
        except Exception as e:
            print("    tarama hatasi (tur atlandi): %s" % str(e)[:100])
            rows, pillars = [], {}
        if rows:
            _pr = evren.para_rejim()
            try:
                evren.btc_pay_guncelle()
                bp = evren.btc_pay_akisi()
            except Exception:
                bp = None
            giris_ara(st, rows, pillars, {
                "para_cikis": bool(_pr and _pr.get("rejim") == "PARA CIKIYOR"),
                "para_durgun": bool(_pr and _pr.get("rejim") == "PARA DURGUN"),
                "btc_pay": bp})

    st["son_cycle_ts"] = testbot.now_iso()
    kaydet(st)
    equity_yaz(st)
    kapanis_bildir(yeni_kayit, st)
    print("    tur bitti %.1f sn | acik=%d equity=%.2f"
          % (time.time() - t0, len(st["acik_pozisyonlar"]), st["equity"]))
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
                             if t.get("funding_usdt") is not None),
                  "skor": s.get("skor_giriste")}
    return out


def durum():
    st = yukle()
    if not st:
        print("NOTR-LONG: henuz baslatilmadi ('python notrlong.py --baslat').")
        return
    poz = _karne(_defter_kayitlari())
    v = list(poz.values())
    net = sum(p["net"] for p in v)
    print("=== NOTR-LONG BOTU (on-kayit 4927f3d, bolum 11 ile TEK KOL) ===")
    print("Karar: rejim ZORLA %s · YALNIZ LONG · sabit %%%.0f hedef · kismi kar KAPALI"
          % (REJIM_ZORLA, SABIT_HEDEF_PCT))
    print("EK SKOR KAPISI YOK (on-kayit bolum 11 — kullanici karari 2026-09-06)")
    print()
    print("Durum : %s | Bakiye: $%.0f -> $%.2f | Acik: %d/%d"
          % (st["durum"], st["baslangic_bakiye"], st["equity"],
             len(st["acik_pozisyonlar"]), MAKS_POZ))
    print("Kapanan pozisyon: %d / 80   ·   Toplam P&L: %+.2f$" % (len(v), net))
    if v:
        kaz = sum(1 for p in v if p["net"] > 0)
        print("Kazanan: %d (%%%.0f)  ·  Fonlama: %+.2f$"
              % (kaz, 100.0 * kaz / len(v), sum(p["fon"] for p in v)))
    print()
    for p in st["acik_pozisyonlar"]:
        px = testbot.fiyat_fapi(p["sym"]) or p["giris"]
        print("  %-10s %-5s %sx giris=%.6g anlik=%.6g PnL=%+.2f$ stop=%.6g hedef=%.6g"
              % (p["sym"], p["yon"], p.get("kaldirac"), p["giris"], px,
                 (px - p["giris"]) * p["miktar"], p["stop"], p.get("tp2") or 0))
    print()
    print("Pencere: 30 gun VE >=80 KAPANMIS pozisyon - IKISI BIRDEN dolmadan")
    print("hukum YOK (on-kayit bolum 5).")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--baslat", action="store_true", help="kasayi ILK KEZ olustur")
    ap.add_argument("--tur", action="store_true")
    ap.add_argument("--durum", action="store_true")
    a = ap.parse_args()
    if a.baslat:
        if yukle():
            print("NOTRLONG zaten var - atlandi (kasa SIFIRLANMADI).")
        else:
            kaydet(yeni_state())
            print("NOTRLONG olusturuldu: %s" % STATEF)
    elif a.tur:
        print("tur tamam" if tur() else "kasa yok - once --baslat")
    else:
        durum()
