#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTBOT — 1 haftalık otonom SANAL (paper) vadeli işlem botu (2026-07-03).
Gerçek para KULLANMAZ, gerçek emir VERMEZ (sistemin "hiçbir ajan işlem yapmaz" ilkesi korunur —
bu kova defterden/gerçek pozisyonlardan TAMAMEN AYRI, sadece istatistik/kanıt üretir).

Amaç: $1000 sanal bakiye ile 7 gün, PC açıkken 5dk'da bir piyasayı tara, iki yönlü (LONG/SHORT)
vadeli pozisyon aç/yönet, gerçekçi maliyetlerle (fee+slippage+funding+likidasyon) kapat.
Sonunda: edge gerçekten var mı (win-rate, ort. R, maliyet payı) sorusuna VERİ ile cevap.

Yeniden kullanılan modüller: evren (evren/rejim/esik), radar (analyze/pillar_d/btc_ref),
olcucu (atr/measure — giriş/stop/TP deterministik), nobetci (telegram_gonder/toast_gonder).

Yön politikası (rejim-koşullu, arsiv_analiz.py 2026-07-02 bulgularından):
  AYI  : SHORT öncelik (skor>=45), 1-cycle onay bekletme (anında-giriş short -EV çıktı).
         LONG istisna: stage=BASLIYOR + smart=LONG + taker>=1.0 (anında, AAVE deseni).
  BOGA : simetrik ters (LONG öncelik+bekletme, SHORT istisna BASLIYOR+smart SHORT).
  NOTR : esik+5, SADECE stage aktif + smart hizali (temkinli).
Ortak filtreler: smart karsı yönse boyut yarıya; DUSUK_FLOAT+dip_yakit şortu atla (RE/FOGO dersi,
düşük-float+derin-neg-funding = yapısal, düşen bıçak — squeeze değil).

Kullanım:
  python testbot.py --cycle          (zamanlayıcı çağırır)
  python testbot.py --durum          (karne, salt-okunur)
  python testbot.py --reset          (yeni test haftası; ONAY ister)
  python testbot.py --dur / --devam
  python testbot.py --zorla SOL:long (debug: sahte giriş, doğrulama için)
"""
import json, os, sys, argparse, datetime, statistics, time, random

import evren
import radar
import olcucu
import makro
from nobetci import telegram_gonder, toast_gonder

HERE = os.path.dirname(os.path.abspath(__file__))
FAPI = "https://fapi.binance.com"
STATEF = os.path.join(HERE, "testbot_state.json")
ISLEMLERF = os.path.join(HERE, "testbot_islemler.jsonl")
EQUITYF = os.path.join(HERE, "testbot_equity.jsonl")
VETO_LOGF = os.path.join(HERE, "veto_log.jsonl")  # 2026-07-08: reddedilen adaylar (olcum; davranis degismez)
LOCKF = os.path.join(HERE, "testbot.lock")

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")


def _cfg():
    return evren.cfg().get("testbot", {})


def _c(ad, varsayilan):
    return _cfg().get(ad, varsayilan)


def _maliyet():
    try:
        return json.load(open(os.path.join(HERE, "kripto-config.json"), encoding="utf-8")).get("maliyet", {})
    except Exception:
        return {}


def now_iso():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def now_dt():
    return datetime.datetime.now()


def parse_iso(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


# ---------- kalıcı dosyalar ----------

def _load_state():
    try:
        return json.load(open(STATEF, encoding="utf-8"))
    except Exception:
        return None


def _save_state(st):
    """ATOMIK yazma (denetim ek bulgu, 2026-08-11).

    [ESKI] json.dump(st, open(STATEF,"w")) — dosyayi TRUNCATE edip yaziyordu.
    [RISK] "KriptoTestBot" zamanlanmis gorevinin ExecutionTimeLimit degeri PT4M idi:
      Windows, 4 dakikayi asan turu SURECI OLDURDUK kesiyor. Oldurme tam bu yazmanin
      ortasina denk gelirse testbot_state.json YARIM kalir -> acik pozisyonlar,
      equity ve zirve kaydi TAMAMEN kaybolur. 2026-08-11'de gorev 3 kez
      SCHED_S_TASK_TERMINATED (267014) dondu, yani senaryo teorik degil.
    [DUZELTME] Once .tmp'ye yaz, sonra os.replace ile ATOMIK degistir. Yazma yarida
      kesilse bile eski state saglam kalir.
    """
    gecici = STATEF + ".tmp"
    with open(gecici, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(gecici, STATEF)


def _append_jsonl(path, obj):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


# --- IKINCI HESAP DESTEGI (2026-08-05, kullanici karari) --------------------
# "benim" hesabi (benim.py) ayni kapatma/yonetme mantigini kullanir ama KENDI
# defterine yazar. Imzalari degistirmek yerine TEK yonlendirme noktasi:
# pozisyon_kapat / pozisyon_liq / pozisyon_kismi_tp1 artik _islem_defteri() yazar.
#
# _DEFTER None iken -> ISLEMLERF, yani BOTUN DAVRANISI BIREBIR AYNI.
# benim.py bunu gecici olarak degistirir ve finally ile GERI ALIR.
# NEDEN AYRI DEFTER: bu oturumdaki tum olcumler (skor otopsisi, stop otopsisi,
# rejim dogrulamasi, btc_pay katmani) botun KENDI kararlarinin karnesine dayaniyor.
# Elle acilan islemler ayni deftere karisirsa o olcumlerin hicbiri bir daha temiz
# yapilamaz ve karisan veri geriye donuk AYRILAMAZ.
_DEFTER = None


def _islem_defteri():
    return _DEFTER or ISLEMLERF


def yeni_state():
    bakiye = float(_c("baslangic_bakiye", 1000.0))
    return {
        "baslangic_ts": now_iso(),
        "baslangic_bakiye": bakiye,
        "equity": bakiye,
        "durum": "AKTIF",
        "acik_pozisyonlar": [],
        "sonraki_id": 1,
        "cooldown": {},       # sym -> kapanis_ts (yeniden-giris 4h kilit)
        "bekleyenler": {},    # sym -> {"yon","skor","ilk_gorulme_ts","cycle_sayaci"}
        "son_cycle_ts": None,
    }


# ---------- fiyat/kline yardımcıları ----------

def _get(u):
    return evren.get(u, headers={"User-Agent": "testbot/1.0"}, timeout=20)


def fiyat_fapi(sym):
    try:
        return float(_get(f"{FAPI}/fapi/v1/ticker/price?symbol={sym}USDT")["price"])
    except Exception:
        return None


def klines_since(sym, interval, start_ms, limit=500):
    try:
        d = _get(f"{FAPI}/fapi/v1/klines?symbol={sym}USDT&interval={interval}&startTime={start_ms}&limit={limit}")
        # [2026-08-13] v/q/n/tb/tq EKLENDI. Binance bu alanlari AYNI yanitta zaten
        # gonderiyordu, biz okumadan atiyorduk -> ek ag maliyeti YOK.
        #   v hacim(baz) · q hacim(USDT) · n islem sayisi
        #   tb taker ALIS hacmi(baz) · tq taker ALIS hacmi(USDT)
        # tq/q = dakika cozunurluklu AGRESOR baskisi. radar'in 'taker' alani 5 dakikada
        # bir noktasal olcum; fiyat donerken ilk kirilanin agresor dengesi olmasi
        # bekleniyor, o seri buradan cikiyor.
        return [{"t": int(k[0]), "o": float(k[1]), "h": float(k[2]), "l": float(k[3]),
                 "c": float(k[4]), "v": float(k[5]), "q": float(k[7]), "n": int(k[8]),
                 "tb": float(k[9]), "tq": float(k[10])} for k in d]
    except Exception:
        return []


def funding_events_since(sym, start_ms):
    try:
        d = _get(f"{FAPI}/fapi/v1/fundingRate?symbol={sym}USDT&startTime={start_ms}&limit=50")
        return [{"t": int(x["fundingTime"]), "rate": float(x["fundingRate"])} for x in d]
    except Exception:
        return []


def to_ms(iso_str):
    return int(parse_iso(iso_str).timestamp() * 1000)


# ---------- boyutlandırma ----------

def kaldirac_hesapla(skor, smart_hizali):
    """[2026-08-03: BOYUTLANDIRMADA ARTIK KULLANILMIYOR — SILINMEDI (Madde 9).
    Kaldirac skordan degil, risk hedefinden turetiliyor; gerekce yeni_giris_ac icindeki
    'RISK-ONCE BOYUTLANDIRMA ONARIMI' blogunda. Geri donulurse referans olarak duruyor.]"""
    k = 3 + (skor - 45) * 7 / 30.0
    if smart_hizali:
        k += 2
    kmin, kmax = float(_c("kaldirac_min", 3)), float(_c("kaldirac_max", 10))
    return int(round(max(kmin, min(kmax, k))))


def marjin_pct_hesapla(skor):
    return max(0.08, min(0.12, 0.08 + max(0.0, skor - 45) * 0.0015))


def likidasyon_fiyati(giris, yon, kaldirac):
    frac = 0.95 / kaldirac
    return giris * (1 - frac) if yon == "LONG" else giris * (1 + frac)


def kaldirac_guvenlik_kirp(giris, stop, yon, kaldirac):
    """Stop, likidasyondan ÖNCE tetiklenmeli (aksi halde bot kendi stopuna ulaşamadan silinir).
    risk_frac*1.3 < liq_frac(k) olacak sekilde kaldiraci kirp; guvenli deger yoksa None (atla)."""
    risk_frac = abs(giris - stop) / giris
    if risk_frac <= 0:
        return None
    kmax_guvenli = 0.95 / (risk_frac * 1.3)
    k = min(kaldirac, int(kmax_guvenli))
    return k if k >= 2 else None


# ---------- yön kararı ----------

def smart_hizali_mi(yon, smart):
    return smart == yon


def _veto_ekle(veto_out, kategori, detay, olurdu_yon):
    """karar_yon icindeki adlandirilmis veto noktalarinda cagrilir (2026-07-08 veto olcum katmani).
    veto_out None ise HICBIR SEY yapmaz -> eski cagirim davranisi birebir korunur (drift yok)."""
    if veto_out is not None:
        veto_out.append({"kategori": kategori, "detay": detay, "olurdu_yon": olurdu_yon})


def _veto_logla(st, sym, r, pillar, kategori, detay, olurdu_yon, rejim_ad):
    """Reddedilen adayi veto_log.jsonl'e yaz (radar_archive deseni + forward-return icin baglam).
    Dedup: ayni (sym,kategori) veto_log_cooldown_saat icinde tekrar yazilmaz (spam/cift-sayim onleme)."""
    cd = st.setdefault("veto_cooldown", {})
    anahtar = f"{sym}:{kategori}"
    cooldown_saat = evren.esik("veto_log_cooldown_saat", 12.0)
    son = cd.get(anahtar)
    if son:
        try:
            if (now_dt() - parse_iso(son)).total_seconds() / 3600 < cooldown_saat:
                return  # cooldown icinde -> ayni suregelen veto, tekrar yazma
        except Exception:
            pass
    kayit = {"ts": now_iso(), "sym": sym, "price": r.get("price"), "kategori": kategori,
             "detay": detay, "olurdu_yon": olurdu_yon, "skor": r.get("score"), "stage": r.get("stage"),
             "chg24": r.get("chg24"), "pos": r.get("pos"), "oi24": r.get("oi24"),
             "taker": pillar.get("taker"), "smart": pillar.get("smart"), "rejim": rejim_ad}
    _append_jsonl(VETO_LOGF, kayit)
    cd[anahtar] = now_iso()


ADAY_ARSIV = os.path.join(HERE, "testbot_aday_arsiv.jsonl")


def _aday_arsivle(aday_rows, rejim_ad, btc_chg3):
    """TESTBOT'UN KENDI ADAY EVRENINI arsivler (2026-08-04, kullanici karari).

    NEDEN: `radar_archive.jsonl` radar.py'nin evreni — gunluk hacmi 7-gun medyanina gore
    PATLAYAN coinler. testbot ise MUTLAK hacimde en buyukleri tarar. Bunlar farkli
    populasyonlar ve fark olculdu: 7 gercek islemin ikisi (GWEI skor 81.1, BLESS skor 72.3)
    islem gununde radar_archive'da HIC YOK. Yani en yuksek skorlu iki islem — biri en buyuk
    zarari veren — bugune kadarki her olcumun disinda kaldi.

    AYRI DOSYA, bilincli: radar_archive'a karistirilirsa o dosyanin anlami bozulur ve
    onunla yapilmis TUM eski olcumler geriye donuk gecersizlesir.

    DAVRANISA ETKISI YOK — yalnizca gorunurluk. Yazma hatasi dongüyu durdurmaz.
    Sema radar_archive.jsonl ile ayni tutuldu ki ayni cozumleme araclari calissin.
    """
    try:
        ts0 = now_iso()[:16].replace("T", " ")
        with open(ADAY_ARSIV, "a", encoding="utf-8") as af:
            for r in aday_rows:
                p = r.get("_pillar") or {}
                kayit = {"ts": ts0, "sym": r.get("sym"), "score": r.get("score"),
                         "stage": r.get("stage"), "price": r.get("price"),
                         "comp": r.get("comp"), "vol_x": r.get("vol_x"),
                         "oi24": r.get("oi24"), "oi3": r.get("oi3"),
                         "funding": r.get("funding"), "pos": r.get("pos"),
                         "last1": r.get("last1"), "last3": r.get("last3"),
                         "chg24": r.get("chg24"), "mcap": r.get("mcap"),
                         "dip_yakit": r.get("dip_yakit"), "ayrisma": r.get("ayrisma"),
                         "rel3": r.get("rel3"), "btc_chg3": btc_chg3, "rejim": rejim_ad,
                         "top_ls": p.get("top_ls"), "glob_ls": p.get("glob_ls"),
                         "taker": p.get("taker"), "smart": p.get("smart"),
                         "float_oran": r.get("_float_oran"), "dusuk_float": r.get("_dusuk_float"),
                         # 2026-08-11: MA50+ucuz kapisinin iki girdisi de arsive gecer ki
                         # kapinin karnesi geriye donuk cozumlenebilsin (fiyat zaten 'price').
                         "ma50_mesafe": r.get("ma50_mesafe"),
                         "karar": r.get("_karar"),
                         # 2026-08-10: karar_yon "SHORT/ANINDA" dese bile giris kapisi (rr_veto /
                         # kaldirac_guvenlik) oldurebiliyordu ve arsivde bu GORUNMUYORDU —
                         # panelde "SHORT/ANINDA" yaziyordu ama islem yoktu (KMNO 19 kez).
                         # Artik nihai akibet de burada: acildi mi, hangi kapida oldu.
                         "sonuc": r.get("_sonuc"), "red_kapi": r.get("_red_kapi"),
                         "kaynak": "testbot"}
                af.write(json.dumps(kayit, ensure_ascii=False) + "\n")
    except Exception:
        pass  # olcum katmani asla karar akisini durdurmaz


def karar_yon(rejim_ad, r, pillar, kucuk_float_esik_gecerli, veto_out=None, para_cikis=False,
              btc_pay=None, para_durgun=False):
    """BTC-PAY KATMANI SARMALAYICISI (2026-08-04, kullanici karari, Madde 9).

    Ic mantik (_karar_yon_ham) BIREBIR KORUNDU; bu sarmalayici yalnizca iki sey yapar:
      1) SHORT FRENI — BTC risk-varlik payi (stable haric) 3 gunde UST ceyrekteyse SHORT ACMAZ.
      2) btc_pay/para_durgun'u ic mantiga gecirir (AYI long penceresi icin).

    [OLCUM] 12 ay, 103 sembol, 37.271 gozlem, gercek holdout (kesif 8 ay / sakli 4 ay):
        BTC_D_XS 3g ALT ceyrek -> SHORT R +0.27 / +0.16   (temel +0.06 / +0.04)
        BTC_D_XS 3g UST ceyrek -> SHORT R -0.02 / -0.03   <-- frenlenen bant
        Kesif/sakli ayrimi +0.45 vs +0.46; saklida dilimler MUKEMMEL sirali (mono +1.00).
    [FREN LONG-NOTR] yalnizca SHORT'u kapatir, hicbir long ACMAZ.
    [FAIL-OPEN] btc_pay None (veri yok/bayat) ise fren DEVREYE GIRMEZ, eski davranis surer.
    [SINIR] Olcumun 12 ayinin tamami DUSEN piyasa; yukselen piyasada iliski donebilir.
    GERI ALMA: kripto-config.json -> esikler.btc_pay_short_freni: 0
    """
    karar = _karar_yon_ham(rejim_ad, r, pillar, kucuk_float_esik_gecerli, veto_out,
                           para_cikis, btc_pay, para_durgun)
    if (karar and karar[0] == "SHORT" and (btc_pay or {}).get("bant") == "UST"
            and evren.esik("btc_pay_short_freni", 1) >= 1):
        _veto_ekle(veto_out, "btc_pay_freni",
                   f"BTC risk-payi UST ceyrek ({btc_pay.get('degisim'):+.2f} puan/3g) "
                   f"-> SHORT frenlendi (olculdu: bu bantta SHORT R -0.02/-0.03)", "SHORT")
        return None
    return karar


def _karar_yon_ham(rejim_ad, r, pillar, kucuk_float_esik_gecerli, veto_out=None, para_cikis=False,
                   btc_pay=None, para_durgun=False):
    """r: radar.analyze() ciktisi. pillar: radar.pillar_d() ciktisi (top_ls/glob_ls/taker/smart).
    Donus: None | ("LONG"|"SHORT", "ANINDA"|"ONAY_BEKLE", sebep)
    veto_out: opsiyonel liste; verilirse adlandirilmis vetolar (long_veto/blowoff/taker_soguma)
    kaydedilir (SADECE olcum, karar cikttisini DEGISTIRMEZ).
    para_cikis: TOTAL mcap 7g <= -%2 (evren.para_rejim 'PARA CIKIYOR'). True ise long-veto'ya
    eklenir (2026-07-23 kullanici karari, Madde 9): kriptodan net cikis/risk-off'ta long kapali.
    LONG-KISITLAYICI — long ACMAZ (opener degil); SHORT/fade tarafina DOKUNMAZ."""
    skor = r["score"]
    smart = pillar.get("smart")
    taker = pillar.get("taker")
    dusuk_float = kucuk_float_esik_gecerli
    esik_short = evren.esik("radar_short_skor", 45.0)
    esik_uzun = evren.esik("radar_alert_skor", 40.0) + 5  # LONG icin biraz daha siki temel esik

    # ortak guvenlik: dusuk-float + dip_yakit = yapisal neg-funding, dusen bicak (RE/FOGO)
    short_riskli_dip = bool(r.get("dip_yakit") and dusuk_float)
    btc_pay_ust = ((btc_pay or {}).get("bant") == "UST")   # 2026-08-04: AYI long penceresi

    # BLOW-OFF filtresi (2026-07-03 TLM -%60 stop sonrasi eklendi — MANTA dersinin ihlali).
    # TLM: 48s'te +%126 pump'in ICINDEYKEN "BASLIYOR+smart-LONG+taker-alim" (AYI-istisnasi) tetiklendi,
    # 36dk'da stop oldu. "BASLIYOR" sadece SON 1-3s ivmeye bakiyor, coinin zaten NE KADAR uzadigina bakmiyordu.
    # MANTA dersi: pump'in GEC safhasinda OI/smart-long gorunumu = tuzak (tepe/likidasyon riski), LONG teyidi DEGIL.
    chg24 = r.get("chg24", 0.0) or 0.0
    blowoff_esik = evren.esik("blowoff_chg24_pct", 40.0)
    asiri_yukselmis = chg24 >= blowoff_esik
    asiri_dusmus = chg24 <= -blowoff_esik
    # PUMP KAPISI TUM SHORT DALLARINDA (2026-08-10, kullanici karari: "pumplamis coinleri
    # pumplamadan kesfetsin"). 2026-08-04'te ayni kanitla YALNIZ AYI-SHORT dali kapatilmisti;
    # kodun kendi notu "satir 317 NOTR-SHORT ve satir 285 BOGA-SHORT dallari dokunulmadi,
    # ayri karar ister" diyordu. Karar simdi verildi -> ayni esik her SHORT dalinda.
    # [KANIT] 362 sembol / 16.169 gozlem / 24sa izgara / ham fiyat: chg24 >%20 grubu IKI
    #   YARIDA DA negatif (A -0.18 / B -0.16, N=258). Mekanizma: pump -> ATR patlar -> stop
    #   medyani %0.97'den %8.57'ye genisler VE stop orani %65 -> %74 cikar (cifte ceza).
    pump_esik_short = evren.esik("ayi_short_chg24_max", 20.0)
    pumplamis = chg24 >= pump_esik_short

    # LONG kalite filtreleri (2026-07-06 — LONG karnesi 0W/4L: RE/O/SLX bicak-dibi girisleri).
    # SHORT'taki dip korumasinin simetrigi + CEO'nun "Fiyat DUSUYOR + OI ARTIYOR -> long girme" vetosunun koda tasinmasi.
    # SHORT dallarina DOKUNULMADI (4W/1L +$121 — calisan taraf).
    oi24 = r.get("oi24") or 0.0
    pos = r.get("pos", 0.5)
    oi_esik = evren.esik("oi_hizli_degisim_pct", 5.0)
    long_veto = (
        pos < 0.25                              # range dibi = dusen bicak (RE 0.11, SLX 0.06, EPIC 0.04)
        or asiri_dusmus                         # 24s'te -%40+ cakilmis (kapitulasyon ortasi)
        or (chg24 < 0 and oi24 >= oi_esik * 3)  # fiyat dusarken OI hizli artiyor = guclu dusus (SLX: -30.6% & OI+33%)
        or para_cikis                           # PARA CIKIYOR (2026-07-23): kriptodan net cikis 7g <= -%2 (risk-off) -> long kapali
    )
    # long_veto alt-tetik etiketi (olcum logu icin; karari etkilemez)
    if pos < 0.25:
        long_veto_detay = f"pos<0.25 (dip-bicak, pos={pos:.2f})"
    elif asiri_dusmus:
        long_veto_detay = f"asiri_dusmus (24s {chg24:+.0f}%)"
    elif chg24 < 0 and oi24 >= oi_esik * 3:
        long_veto_detay = f"fiyat-dusuk+OI-artis (chg24={chg24:+.1f}% oi24={oi24:+.0f}%)"
    elif para_cikis:
        long_veto_detay = "para-cikis (kriptodan net cikis 7g, risk-off)"
    else:
        long_veto_detay = ""

    # ================= A+B KAPISI (2026-08-10, KULLANICI KARARI, Madde 9) =================
    # [NE] funding <= -0.05 (%/8s)  VE  oi24 >= %10  ->  SHORT.
    #   Turkce: shortlar KALABALIK (derin negatif funding) ve pozisyon BIRIKIYOR.
    # [NEDEN BU] 46 gunluk radar arsivi (121.620 kayit / 384 sembol) botun GERCEK mekanigiyle
    #   ileri oynatildi (A-stop · 2R · 72s · fitil · maliyet 0.04R) -> 7.119 bagimsiz olay.
    #   Bulunan TEK pozitif hucre bu. Tek-degisken guclerinin ikisi de zaman ikiye bolununce
    #   ayakta: funding<=-0.05 -> +0.259 (A +0.250 / B +0.269, N=508)
    #           oi24>=10       -> +0.189 (A +0.151 / B +0.228, N=803)
    #   Kesisim: +0.375 (N=206, kontrol -0.037). Pump kapisiyla: +0.396 (N=201).
    #   SIMETRI KONTROLU: ayni kosullar LONG tarafinda -0.28..-0.34 -> yon TASIYORLAR.
    # [KAPI SETI REPLAY — uygulanmadan once, ayni arsivde]
    #   bugunku set (skor>=45 + rr>=1.5)  N=107  ort R +0.008  | kazanc 1.5R'de kirpilirsa -0.143
    #   A+B + pump kapisi                 N=201  ort R +0.396  | kirpilirsa +0.218 (A +0.127 / B +0.319)
    #   A+B + skor>=45                    N=134  ort R +0.338  <- SKOR EKLEMEK DUSURUYOR
    #   -> skor bu kapiya SART DEGIL. Zaten aday kisa listesi skora gore siralaniyor;
    #      skoru bir de kapi yapmak, oi24'un tasidigi bilgiyi ikinci kez sayip aday kisiyor.
    # [KORUNAN FILTRELER] pump kapisi (chg24 >= %20 -> acma) · dip-bicak (short_riskli_dip) ·
    #   asiri_dusmus · BTC-PAY short freni (sarmalayicida, holdout'lu olcum) — hicbiri gevsetilmedi.
    # [BOGA'DA KAPALI] olcumun 46 gununun tamami AYI/NOTR; boga hucresi YOK -> TAM_BOGA'da acilmaz.
    # [SINIR] Tek rejim · sabit 2R hedefle olculdu (bot 1.5R kismi + trailing ile cikiyor) ·
    #   slipaj yok sayildi · olaylar 15 sembolde kumeleniyor (bagimsizlik gorundugunden dusuk).
    # GERI ALMA: kripto-config.json -> esikler.ab_kapisi_acik: 0
    # [DENETIM DUZELTMESI 2026-08-11, Bulgu 5] Eskiden A+B ve MA50+ucuz AYRI iki blok idi ve
    #   A+B once gelip `return` ettigi icin IKISINI BIRDEN saglayan olaylar HEP "A+B" etiketiyle
    #   yaziliyordu. Olcum: 445 MA50 olayinin 61'i (%14) boyle kayboluyordu -> MA50 kapisinin
    #   karnesi eksik, atif yanlis. Simdi iki kapi ONCE degerlendirilir, sonra etiketlenir.
    #   Davranis (hangi islemin acildigi) DEGISMEDI; yalniz SEBEP etiketi duzeldi.
    #   Not: birlesik etiket "A+B+MA50:" ile baslar, yani SABIT_HEDEF_KAPILARI ("A+B", ...)
    #   startswith kontrolu aynen calisir -> sabit %10 hedef korunur.
    _ab_gecti = (evren.esik("ab_kapisi_acik", 1) >= 1
                 and (r.get("funding") is not None)
                 and r["funding"] <= evren.esik("ab_funding_esik", -0.05)
                 and (r.get("oi24") or 0) >= evren.esik("ab_oi24_esik", 10.0))
    _ma50_gecti = (evren.esik("ma50_kapisi_acik", 1) >= 1
                   and r.get("ma50_mesafe") is not None and r.get("price")
                   and r["price"] <= evren.esik("ucuz_fiyat_esik", 0.07)
                   and r["ma50_mesafe"] >= evren.esik("ma50_mesafe_esik", 3.72))
    if ((_ab_gecti or _ma50_gecti) and rejim_ad in ("AYI", "NOTR")
            and not short_riskli_dip and not asiri_dusmus):
        _hangi = ("A+B+MA50" if (_ab_gecti and _ma50_gecti)
                  else ("A+B" if _ab_gecti else "MA50+ucuz"))
        if pumplamis:
            _veto_ekle(veto_out, "blowoff",
                       f"{_hangi} pump-kapisi (24s {chg24:+.0f}% >= {pump_esik_short:.0f}%)", "SHORT")
            return None
        _parca = []
        if _ab_gecti:
            _parca.append(f"funding {r['funding']:.3f} (short kalabalik) + oi24 {oi24:+.0f}%")
        if _ma50_gecti:
            _parca.append(f"fiyat ${r['price']:.4f} (ucuz sinif) + MA50'nin "
                          f"%{r['ma50_mesafe']:.1f} ustunde")
        return ("SHORT", "ANINDA", f"{_hangi}: " + " | ".join(_parca)
                + " [A+B 2026-08-10 +0.396R N=201 · MA50 2026-08-11 +0.84% N=460]")

    # ================= MA50+UCUZ KAPISI (2026-08-11, KULLANICI KARARI, Madde 9) ===========
    # [NE] fiyat <= $0.07  VE  MA50 mesafesi >= %3.72  ->  SHORT.
    #   Turkce: UCUZ bir coin 50 saatlik ortalamasinin belirgin ustune cikmissa -> asagi.
    # [NEDEN] YON AVI (2026-08-10): stop/hedef olmadan, ham "rel24 = coin 24s - BTC 24s"
    #   uzerinden 6.790 olayda tarandi. Ayi piyasasinda her sey duser; asil yon olcusu
    #   PIYASADAN AYRISMA. Kararli (iki zaman yarisinda da ayni isaret) olculer:
    #     MA50 mesafesi -1.76 (A -1.70 / B -1.87)  <- en guclu tek olcu
    #     fiyat seviyesi (log10) +1.57 (A +2.18 / B +1.03)  <- ucuz coin BTC'nin ALTINDA
    #     radar skoru -1.55 · son 24s -1.44 · MA200 -1.43 · oi24 -0.91 · mcap -0.51
    #   RASTGELE CIKANLAR: gercek taker orani (-0.07) · sikisma (-0.17) · hacim kati (+0.03).
    # [OLCUM — botun gercek mekanigiyle, hedef %10 / 72s / A-stop / maliyet %0.09]
    #     bu kapi          N=460  net +0.84%  (A +0.99 / B +0.72)  isabet %29.8 / basabas %25.9
    #     A+B (mevcut)     N=197  net +2.14%  (A +2.38 / B +1.90)
    #     kesisim          N= 65  net +2.53%  (A +2.82 / B +1.94)  <- en guclu hucre
    #     KONTROL          N=6790 net -0.05%
    # [NEDEN EKLENDI] Ortusme analizi: yalniz-bu-kapi 407 olay x +0.55% = +226 EK katki.
    #   Birlesim 604 olay x +1.07% = +648 (A+B tek basina +422) -> toplam edge %54 artar.
    #   Bedeli: islem basi beklenti +2.14 -> +1.07. Bot 8 pozisyon kapasitesini zaten
    #   kullanamiyordu; olay sayisini 2,3 katina cikarmak olcum hizini da artirir.
    # [ESIKLER ICAT EDILMEDI] Ikisi de olcumun kendi dagiliminin ceyreginden:
    #   fiyat = %20'lik dilim ($0.07) · ma50_mesafe = %80'lik dilim (%3.72).
    # [KORUNANLAR] pump kapisi · dip-bicak · asiri_dusmus · BTC-PAY short freni ·
    #   kaldirac guvenlik kirpmasi. TAM_BOGA'da KAPALI (olcumde boga hucresi yok).
    # [SINIR] Fiyat seviyesi bir COIN-TIPI vekilidir (ucuz = genelde yuksek arz/yeni/
    #   spekulatif). Rejim degisince iliski DONEBILIR — bogada ucuz coinler one gecebilir.
    #   Ayrica ham fiyat esigi zamanla kayar; yeniden olculmeden yillarca birakilmamali.
    # GERI ALMA: kripto-config.json -> esikler.ma50_kapisi_acik: 0
    # (MA50+ucuz kapisi yukaridaki BIRLESIK blokta degerlendiriliyor — Bulgu 5 duzeltmesi)

    if rejim_ad == "AYI":
        if r["stage"] == "BASLIYOR" and smart == "LONG" and (taker or 0) >= 1.0:
            if asiri_yukselmis:
                # 2026-08-10: bu dal LONG'u SHORT'a CEVIRIYORDU — yani pump kapisinin tam
                # tersini yapiyordu (BLESS -$488'in sinifi). Ayni kanitla artik cevirmiyor,
                # sadece elemine ediyor: pump'in icine SHORT atmak da girmek de olculdu, ikisi de negatif.
                _veto_ekle(veto_out, "blowoff",
                           f"AYI blow-off (24s {chg24:+.0f}%): pump'in gec safhasi — LONG da SHORT da acilmaz", "LONG")
                return None
            if long_veto:
                _veto_ekle(veto_out, "long_veto", f"AYI-istisna: {long_veto_detay}", "LONG")
                return None  # dip-bicak/kapitulasyon/fiyat-dusuk-OI-artis -> AAVE istisnasi bile gecersiz
            return ("LONG", "ANINDA", "AYI-istisna: BASLIYOR+smart-LONG+taker-alim (AAVE deseni)")
        # --- BTC-PAY LONG PENCERESI (2026-08-04, KULLANICI KARARI, Madde 9) -----------
        # [ESKI DAVRANIS] AYI'da LONG yalnizca AAVE-istisnasindan (yukarida, BASLIYOR+
        #   smart-LONG+taker>=1.0) acilabiliyordu. Baska hicbir long yolu YOKTU.
        # [OLCUM] 12 ay / 103 sembol / 37.271 gozlem / GERCEK holdout (PARA_SONUC.md, CIKIS_SONUC.md):
        #   "BTC risk-varlik payi 3g UST ceyrek + para DURGUN" penceresinde
        #     LONG R = kesif +0.24 / sakli +0.16   (rastgele kontrol -0.07 / -0.04)
        #   Ayni olcumde KULLANICININ ilk onerdigi tetik (AYI + para GIRISI + coin yukari)
        #   calismadi: -0.06 / +0.04, rastgeleden ayirt edilemedi. BTC/ETH sarti da katki
        #   yapmadi (+0.01/+0.02). Yani acilan kapi, olcumun secdigi kapi.
        # [PENCERE COIN SECMEZ] T-B piyasa-seviyesi bir IZIN penceresidir; hangi coin
        #   sorusunu cevaplamaz. O yuzden coin-seviyesi TUM kalite filtreleri AYNEN gecerli:
        #   long_veto (pos<0.25 / asiri_dusmus / fiyat-dusuk+OI-artis / para_cikis) ·
        #   asiri_yukselmis (blowoff) · taker>=1.0. Hicbiri gevsetilmedi.
        # [SINIR] Olcumun 12 ayinin TAMAMI dusen piyasa. Yukselen piyasada iliski donebilir.
        # GERI ALMA: kripto-config.json -> esikler.btc_pay_ayi_long: 0
        if (btc_pay_ust and para_durgun and evren.esik("btc_pay_ayi_long", 1) >= 1
                and skor >= esik_uzun and smart != "SHORT" and r["stage"] != "izle"):
            if asiri_yukselmis:
                _veto_ekle(veto_out, "blowoff", f"AYI btc-pay-long tepe (24s {chg24:+.0f}%)", "LONG")
            elif long_veto:
                _veto_ekle(veto_out, "long_veto", f"AYI btc-pay-long: {long_veto_detay}", "LONG")
            elif (taker or 0) < 1.0:
                _veto_ekle(veto_out, "taker_soguma", f"AYI btc-pay-long taker<1.0 (taker={taker})", "LONG")
            else:
                return ("LONG", "ONAY_BEKLE",
                        f"AYI btc-pay penceresi: BTC risk-payi UST ceyrek + para durgun "
                        f"(skor={skor}) [2026-08-04, olculdu: +0.24/+0.16]")
        if skor >= esik_short and smart != "LONG" and not short_riskli_dip and r.get("pos", 0.5) >= 0.20:
            if asiri_dusmus and r.get("pos", 0.5) < 0.30:
                _veto_ekle(veto_out, "blowoff", f"AYI-SHORT dusen-bicak (24s {chg24:+.0f}%, pos={r.get('pos',0.5):.2f})", "SHORT")
                return None  # zaten cok dusmus + dipte -> dusen bicagi kovalama, SHORT girme (ders#4)
            # --- PUMP KAPISI (2026-08-04, KULLANICI KARARI, Madde 9) --------------------
            # [ESKI DAVRANIS] Bu dalda YALNIZ `asiri_dusmus` bakiliyordu; `asiri_yukselmis`
            #   HIC kontrol edilmiyordu. Tasarim pump'i bir SHORT FIRSATI sayiyordu
            #   (bkz. yukarida satir 265 blow-off redirect: LONG -> SHORT-tepki).
            #   BLESS 2026-08-02: skor 72.3, chg24 +%73, smart NOTR, pos 0.83 -> dogrudan SHORT,
            #   1.8 saatte stop, -$487.98 (tek islemde en buyuk zarar). Bot TASARLANDIGI GIBI calisti.
            # [OLCUM] 362 sembol / 16.169 gozlem / 24sa izgara / ham fiyat (skor ve radar filtresi
            #   KARISMADAN). SHORT, A-stop, 2R, 72sa, fitil tetikli. Sahte-kontrol gurultusu 0.01.
            #     chg24 %-10..0 -> R +0.05 | %0..10 -> +0.04 | %10..20 -> +0.07
            #     chg24 %20..35 -> R -0.14 | %35..50 -> -0.25 | %50..75 -> -0.14
            #   >%20 grubu IKI YARIDA DA negatif (A -0.18 / B -0.16, N=258) ve en kotu 3 kayit
            #   cikarilinca ayakta (-0.17 -> -0.16) => aykiri degerden gelmiyor.
            #   MEKANIZMA (cifte ceza): pump -> ATR patlar -> stop medyani %0.97'den %8.57'ye
            #   genisler VE buna ragmen stop orani %65 -> %74 cikar.
            # [DURUSTLUK NOTU] On-kayitli karar kurali (fark >=0.15 IKI yarida da) GECILEMEDI:
            #   B yarisinda fark +0.12. Takilma sebebi kalan grubun kendisinin de negatif olmasi
            #   (-0.04) -> FARK kuculdu, SEVIYE degil. Esik gevsetilmedi; kullanici "duzelt" dedi.
            # [ESIK] 40 (mevcut blowoff_chg24_pct) DEGIL 20 secildi: >%30'da B yarisi isaret
            #   donduruyor (A -0.37 / B +0.05, N kucuk) -> yuksek esikler daha AZ kanitli.
            # [KAPSAM] YALNIZ bu dal. Dokunulmayanlar (ayni kanit sinifi, AYRI karar ister):
            #   * satir 265 AYI blow-off redirect: pump'ta LONG'u SHORT'a CEVIRIYOR (ayni tuzak)
            #   * satir 317 NOTR-SHORT ve satir 285 BOGA-SHORT dallari
            #   Olcum rejim-kosullu DEGILDI; kanit bu dallar icin de gecerli ama kullanici karari
            #   AYI-SHORT icindi. Bunlar ayri oturumda teklif edilir.
            # GERI ALMA: kripto-config.json -> esikler.ayi_short_chg24_max: 999 (kapi etkisiz kalir)
            if pumplamis:
                _veto_ekle(veto_out, "blowoff",
                           f"AYI-SHORT pump-kapisi (24s {chg24:+.0f}% >= {pump_esik_short:.0f}%)", "SHORT")
                return None
            return ("SHORT", "ONAY_BEKLE", f"AYI: skor={skor} short-aday, 1-cycle onay bekletme")
        return None
    if rejim_ad == "BOGA":
        if r["stage"] == "BASLIYOR" and smart == "SHORT" and (taker or 1) <= 1.0:
            if asiri_dusmus:
                return ("LONG", "ONAY_BEKLE",
                        f"KAPITULASYON TUZAGI (24s {chg24:+.0f}%): smart-short+BASLIYOR = dususun GEC safhasi, "
                        f"SHORT DEGIL -> LONG-tepki adayi, dip/donus onayi bekle")
            if pumplamis:   # 2026-08-10: pump kapisi bu dala da (ayni kanit)
                _veto_ekle(veto_out, "blowoff",
                           f"BOGA-SHORT pump-kapisi (24s {chg24:+.0f}% >= {pump_esik_short:.0f}%)", "SHORT")
                return None
            return ("SHORT", "ANINDA", "BOGA-istisna: BASLIYOR+smart-SHORT+taker-satis")
        if skor >= esik_short and smart != "SHORT" and r.get("pos", 0.5) <= 0.85:
            if asiri_yukselmis and r.get("pos", 0.5) > 0.70:
                _veto_ekle(veto_out, "blowoff", f"BOGA-LONG tepe (24s {chg24:+.0f}%, pos={r.get('pos',0.5):.2f})", "LONG")
                return None  # zaten cok yukselmis + tepede -> kovalama, LONG girme
            if long_veto:
                _veto_ekle(veto_out, "long_veto", f"BOGA: {long_veto_detay}", "LONG")
                return None  # BOGA'da da bicak dibine LONG acilmaz
            return ("LONG", "ONAY_BEKLE", f"BOGA: skor={skor} long-aday, 1-cycle onay bekletme")
        return None
    # NOTR: temkinli — sadece stage aktif + smart hizali
    # 2026-08-10: HAZIRLANIYOR icin esik `radar_alert_skor`a (40) iner. Gerekce OTOPSI-3:
    # HAZIRLANIYOR skordan BAGIMSIZ ayirt ediyor — skor<45 bandinda bile +0.22R vs izle +0.01
    # (N=116). Yani bu hucrede yuksek skor sarti bilgi katmiyor, sadece aday sayisini kisiyor.
    # Yeni esik ICAT EDILMEDI: mevcut radar_alert_skor kullanildi. BASLIYOR esigi DEGISMEDI.
    esik_hazir = evren.esik("radar_alert_skor", 40.0)
    stage_esigi = esik_hazir if r["stage"] == "HAZIRLANIYOR" else esik_uzun
    if r["stage"] in ("BASLIYOR", "HAZIRLANIYOR") and skor >= stage_esigi:
        # taker>=1.0 sarti (2026-07-06): smart etiketi tek basina 3/3 kaybetti (RE/O/SLX);
        # AYI-istisnasiyla (AAVE deseni) ayni agresif-alici teyidi burada da aranir.
        # (2026-07-08) bilesik kosul alt-dallara ayrildi: karar cikttisi BIREBIR AYNI, sadece
        # hangi filtrenin blokladigi veto_out'a yazilir (olcum). Oncelik eski && sirasiyla ayni:
        # asiri_yukselmis -> long_veto -> taker<1.0.
        if smart == "LONG":
            if asiri_yukselmis:
                _veto_ekle(veto_out, "blowoff", f"NOTR-LONG asiri_yukselmis (24s {chg24:+.0f}%)", "LONG")
            elif long_veto:
                _veto_ekle(veto_out, "long_veto", f"NOTR: {long_veto_detay}", "LONG")
            elif (taker or 0) < 1.0:
                _veto_ekle(veto_out, "taker_soguma", f"NOTR-LONG taker<1.0 (taker={taker}, agresif-alici teyidi yok)", "LONG")
            else:
                # Faz 2 (2026-07-22, kullanici karari "belirsizde long kapali, fade acik"):
                # F10 BELIRSIZ/NOTR rejimde anomali-LONG artik ACILMAZ (temiz-aday olsa bile).
                # Gerekce: replay/erken-kusak — belirsizde anomali-long negatif; F1 trend-long
                # gelince yalniz TAM_BOGA'da acilir. AYI-AAVE-istisnasi (kullanici karari) KORUNDU;
                # NOTR-SHORT/fade tarafi acik (pump'lari fade'le yakala).
                #
                # --- ACILDI (2026-08-04, KULLANICI KARARI, Madde 9) --------------------------
                # [ESKI DAVRANIS] Yukaridaki Faz 2 kurali: bu noktaya gelen "temiz aday" bile
                #   yalnizca vetolanirdi. NOTR'de LONG donduren HICBIR kod yolu YOKTU.
                #   veto_log 2026-07-23..08-03: bu tam metinle 13 aday elendi.
                # [OLCUM] F10 etiketleri fiili getiriyle karsilastirildi (13.997 gozlem, 39 gun,
                #   nokta-zamanli rejim yeniden kurma; kalibrasyon canli btc_rejim() ile birebir):
                #     BELIRSIZ->NOTR  N=4662  LONG R -0.09 (A -0.40 / B +0.16)
                #                             SHORT R +0.17 (A +0.39 / B -0.01)
                #   Yani long'un YAPISAL olarak kapatildigi rejimde, son yarida kazanan taraf LONG.
                # [DURUSTLUK NOTU — bu degisiklik OLCUMLE GEREKCELENMEDI]
                #   On-kayitli kural (lehte yon, aleyhtekini IKI YARIDA DA >=0.15R gecmeli)
                #   BU ETIKETTE DE GECILEMEDI: A +0.79 / B -0.17. Isaret yariyi donduruyor.
                #   Bulgu TEK YARILIK. LONG karnesi hala 0W/4L (RE/O/SLX bicak-dibi girisleri).
                #   Kapi, olcum kanitiyla degil KULLANICI KARARIYLA aciliyor; bu boyle kayda gecti.
                # [KAPSAM] YALNIZ bu son "else" kolu acildi. Ustteki UC kalite filtresi AYNEN
                #   duruyor ve LONG'u kapatmaya devam ediyor:
                #     asiri_yukselmis (blowoff) · long_veto (pos<0.25 / asiri_dusmus /
                #     fiyat-dusuk+OI-artis / para_cikis) · taker < 1.0
                #   Bunlar olculmedi, dokunulmadi. AYI ve BOGA dallari da DEGISMEDI.
                # GERI ALMA: kripto-config.json -> esikler.notr_long_acik: 0
                if evren.esik("notr_long_acik", 0.0) >= 1:
                    return ("LONG", "ONAY_BEKLE",
                            f"NOTR-belirsiz: temiz-aday long (skor={skor}, smart-LONG, taker={taker}) "
                            f"[2026-08-04 kullanici karari; olcumle gerekcelenmedi]")
                _veto_ekle(veto_out, "long_veto", "NOTR-belirsiz: temiz-aday ama rejim-long kapali (fade acik)", "LONG")
        if smart == "SHORT" and not short_riskli_dip and not asiri_dusmus:
            if pumplamis:   # 2026-08-10: pump kapisi NOTR-SHORT dalina da (ayni kanit)
                _veto_ekle(veto_out, "blowoff",
                           f"NOTR-SHORT pump-kapisi (24s {chg24:+.0f}% >= {pump_esik_short:.0f}%)", "SHORT")
                return None
            return ("SHORT", "ANINDA", "NOTR: stage-aktif+smart-SHORT")

        # (fade dali asagida, stage blogunun DISINDA — gerekce orada)
    # --- SMART=NOTR IKI YONLU FADE DALI (2026-08-10, KULLANICI KARARI, Madde 9) --------
        # [ESKI DAVRANIS] NOTR rejimde YALNIZ smart=LONG veya smart=SHORT is gorurdu.
        #   smart=NOTR adayi HICBIR yol bulamiyordu — ve Pillar D okumalarinin cogunlugu NOTR
        #   (kapanan 10 islemin 6'sinda smart=NOTR). Yani rejim NOTR + smart NOTR = bot sagir.
        #   "Olcum bant genisligi" darbogazinin karar-tarafindaki yarisi buydu.
        # [YON NEREDEN GELIYOR] smart yoksa yonu RANGE KONUMU verir — sistemin kendi kimligi:
        #   momentum-takipcisi degil, ORTALAMAYA DONUS + rejim okuyucu (fikir defteri, ELENEN
        #   GIRIS FIKIRLERI ortak dersi). Ust banttan fade = SHORT, alt banttan tepki = LONG.
        # [DURUSTLUK] Bu dal OLCUMLE GEREKCELENMEDI — kullanici karari ("giris hem long hem
        #   short olsun, daha agresif bot"). notr_long_acik (2026-08-04) ile ayni sinifta ve
        #   ayni sekilde kayda geciyor. Kalite filtrelerinin HICBIRI gevsetilmedi: pump kapisi,
        #   long_veto, dip-bicak korumasi, taker teyidi aynen calisiyor.
        # [OLCUM] Bu dalin urettigi her giris golge defterde de izlenebilir; reddedilenler
        #   zaten orada aciliyor. Karne 'NOTR-fade' sebebiyle ayrilabilir.
        #
        # [STAGE SARTI YOK — TEZAT ONARIMI] Bu dal, ustteki `stage in (BASLIYOR,HAZIRLANIYOR)`
        #   blogunun DISINDA duruyor. Sebep bir CELISKI: fade = ortalamaya donus; ihtiyaci
        #   "hareket basliyor" degil UC NOKTA'dir. Ustteki blok ise fade girisi icin momentum
        #   sarti (BASLIYOR) ariyordu — ve OTOPSI-3 tam da BASLIYOR'un short icin EN KOTU hucre
        #   oldugunu olcmustu (-0.09R; izle +0.07R; HAZIRLANIYOR +0.19R). Yani bot, en iyi
        #   stratejisi icin en kotu olculmus on-sarti dayatiyordu. Havuzun %89'u 'izle' ve o
        #   hucre POZITIF olctu -> fade dali orada da calisir. Skor esigi radar_alert_skor (40).
        # [ETKI OLCULDU] scratchpad/etki_tahmini.py, 7 gun / 1152 tur / 6799 aday kaydi:
        #   A eski kural 97 karar (64'u pumplamis-coin SHORT'u = olculmus negatif sinif)
        #   B stage-sartli fade  72 karar  (pump kapisi 44 SHORT'u kesiyor, fade 18 ekliyor)
        #   C stage-sartsiz fade 111 karar (SHORT 53 / LONG 58 — gercekten iki yonlu)  <- SECILEN
    if (smart in (None, "NOTR") and evren.esik("notr_fade_acik", 1) >= 1
            and skor >= evren.esik("radar_alert_skor", 40.0)):
        pos_ust = evren.esik("notr_fade_pos_ust", 0.75)
        pos_alt = evren.esik("notr_fade_pos_alt", 0.40)
        if pos >= pos_ust and not short_riskli_dip and not asiri_dusmus:
            if pumplamis:
                _veto_ekle(veto_out, "blowoff",
                           f"NOTR-fade SHORT pump-kapisi (24s {chg24:+.0f}%)", "SHORT")
                return None
            return ("SHORT", "ONAY_BEKLE",
                    f"NOTR-fade: range ustu (pos={pos:.2f}>={pos_ust}), smart yok -> "
                    f"ortalamaya donus SHORT [2026-08-10 kullanici karari, olcumsuz]")
        if pos <= pos_alt:
            if asiri_yukselmis:
                _veto_ekle(veto_out, "blowoff", f"NOTR-fade LONG tepe (24s {chg24:+.0f}%)", "LONG")
            elif long_veto:
                _veto_ekle(veto_out, "long_veto", f"NOTR-fade: {long_veto_detay}", "LONG")
            elif (taker or 0) < 1.0:
                _veto_ekle(veto_out, "taker_soguma",
                           f"NOTR-fade LONG taker<1.0 (taker={taker}, agresif-alici teyidi yok)", "LONG")
            else:
                return ("LONG", "ONAY_BEKLE",
                        f"NOTR-fade: range alti (pos={pos:.2f}<={pos_alt}), taker={taker} -> "
                        f"ortalamaya donus LONG [2026-08-10 kullanici karari, olcumsuz]")
    return None


# ---------- açık pozisyon yönetimi ----------

def maliyet_uygula_giris(fiyat, yon, cst):
    slip = float(cst.get("slippage_pct", 0.02)) / 100.0
    return fiyat * (1 + slip) if yon == "LONG" else fiyat * (1 - slip)


def maliyet_uygula_cikis(fiyat, yon, cst):
    slip = float(cst.get("slippage_pct", 0.02)) / 100.0
    return fiyat * (1 - slip) if yon == "LONG" else fiyat * (1 + slip)


def pozisyon_kapat(st, pos, cikis_fiyat_piyasa, sebep):
    cst = _maliyet()
    taker = float(cst.get("taker_fee_pct", 0.045)) / 100.0
    cikis_ef = maliyet_uygula_cikis(cikis_fiyat_piyasa, pos["yon"], cst)
    miktar = pos["miktar"]
    notional_exit = miktar * cikis_ef
    yon_isaret = 1 if pos["yon"] == "LONG" else -1
    pnl_ham = (cikis_ef - pos["giris"]) * miktar * yon_isaret
    ucret = notional_exit * taker
    pnl_net = pnl_ham - ucret
    st["equity"] += pnl_net
    tutma_saat = (now_dt() - parse_iso(pos["giris_ts"])).total_seconds() / 3600
    r_katsayi = (pnl_net / pos["risk_usdt"]) if pos.get("risk_usdt") else None
    kayit = {
        "ts": now_iso(), "id": pos["id"], "sym": pos["sym"], "yon": pos["yon"],
        "giris": round(pos["giris"], 6), "cikis": round(cikis_ef, 6),
        "kaldirac": pos["kaldirac"], "marjin": round(pos["marjin"], 2),
        "notional": round(miktar * pos["giris"], 2), "sonuc_usdt": round(pnl_net, 2),
        "roi_pct": round(pnl_net / pos["marjin"] * 100, 1) if pos["marjin"] else None,
        "r": round(r_katsayi, 2) if r_katsayi is not None else None,
        "sebep": sebep, "tutma_saat": round(tutma_saat, 1),
        "skor_giriste": pos.get("skor_giriste"), "smart_giriste": pos.get("smart_giriste"),
        "chg24_giriste": pos.get("chg24_giriste"), "range_pos_giriste": pos.get("range_pos_giriste"),
        "stage_giriste": pos.get("stage_giriste"), "sebep_giris": pos.get("sebep_giris"),
        "rejim_giriste": pos.get("rejim_giriste", "BILINMIYOR"),
        # 2026-08-05: "elle" ise botun karnesinden DISLANIR (panel_sunucu suzuyor)
        "kaynak": pos.get("kaynak"), "stop_elle": pos.get("stop_elle"),
    }
    _append_jsonl(_islem_defteri(), kayit)
    st["cooldown"][pos["sym"]] = now_iso()
    msg = f"[TESTBOT] KAPANDI {pos['sym']} {pos['yon']} {sebep} PnL={pnl_net:+.2f}$ (R={kayit['r']})"
    telegram_gonder(msg, olay="kapanis")
    toast_gonder("TestBot kapandi", f"{pos['sym']} {pos['yon']} {sebep} {pnl_net:+.2f}$",
                 olay="kapanis")
    return kayit


def pozisyon_liq(st, pos):
    """Likidasyon: TÜM marjin gider (fee/slippage ihmal — anlık zorunlu kapanış)."""
    st["equity"] -= pos["marjin"]
    tutma_saat = (now_dt() - parse_iso(pos["giris_ts"])).total_seconds() / 3600
    kayit = {
        "ts": now_iso(), "id": pos["id"], "sym": pos["sym"], "yon": pos["yon"],
        "giris": round(pos["giris"], 6), "cikis": round(pos["likidasyon"], 6),
        "kaldirac": pos["kaldirac"], "marjin": round(pos["marjin"], 2),
        "notional": round(pos["miktar"] * pos["giris"], 2), "sonuc_usdt": round(-pos["marjin"], 2),
        "roi_pct": -100.0, "r": round(-pos["marjin"] / pos["risk_usdt"], 2) if pos.get("risk_usdt") else None,
        "sebep": "LIKIDASYON", "tutma_saat": round(tutma_saat, 1),
        "skor_giriste": pos.get("skor_giriste"), "smart_giriste": pos.get("smart_giriste"),
        "chg24_giriste": pos.get("chg24_giriste"), "range_pos_giriste": pos.get("range_pos_giriste"),
        "stage_giriste": pos.get("stage_giriste"), "sebep_giris": pos.get("sebep_giris"),
        "rejim_giriste": pos.get("rejim_giriste", "BILINMIYOR"),
        # 2026-08-05: "elle" ise botun karnesinden DISLANIR (panel_sunucu suzuyor)
        "kaynak": pos.get("kaynak"), "stop_elle": pos.get("stop_elle"),
    }
    _append_jsonl(_islem_defteri(), kayit)
    st["cooldown"][pos["sym"]] = now_iso()
    msg = f"[TESTBOT] LIKIDASYON {pos['sym']} {pos['yon']} marjin kaybi ${pos['marjin']:.2f}"
    telegram_gonder(msg, olay="likidasyon")
    toast_gonder("TestBot LIKIDASYON", f"{pos['sym']} {pos['yon']} -${pos['marjin']:.2f}",
                 olay="likidasyon")
    return kayit


def pozisyon_kismi_tp1(st, pos, cikis_fiyat_piyasa):
    cst = _maliyet()
    taker = float(cst.get("taker_fee_pct", 0.045)) / 100.0
    cikis_ef = maliyet_uygula_cikis(cikis_fiyat_piyasa, pos["yon"], cst)
    yari = pos["miktar"] / 2.0
    yon_isaret = 1 if pos["yon"] == "LONG" else -1
    pnl_ham = (cikis_ef - pos["giris"]) * yari * yon_isaret
    ucret = yari * cikis_ef * taker
    pnl_net = pnl_ham - ucret
    st["equity"] += pnl_net
    pos["miktar"] -= yari
    # [DENETIM DUZELTMESI 2026-08-11, Bulgu 4] Miktar yarilaniyordu ama pos["marjin"] AYNI
    #   kaliyordu. pozisyon_liq tam marjini siler (st["equity"] -= pos["marjin"]) -> TP1
    #   alinmis bir pozisyon likide olsa zarar ~2 KAT fazla yazilirdi. Henuz hic likidasyon
    #   olmadigi icin gerceklesmedi (0 vaka / 2 TP1), ama hata gercekti.
    #   NOT: risk_usdt BILEREK degistirilmiyor — R, GIRISTE hedeflenen riske gore olculur;
    #   kalan yarinin R'sinin ~yari cikmasi dogru muhasebedir.
    pos["marjin"] = round(pos["marjin"] / 2.0, 2)
    # [2026-08-11] Sabit-hedef pozisyonlarda stop BASABASA CEKILMEZ. Olculdu (577 olay):
    #   kismi sonrasi stop ayni kalirsa +0.274, basabasa cekilirse +0.261 — cekmek
    #   kalan yarinin nefes alanini oldurup hedefe varmadan susturuyor.
    #   Diger (klasik) cikis modlarinda eski davranis aynen korunur.
    if pos.get("cikis_modu") != "sabit_hedef":
        pos["stop"] = pos["giris"]  # breakeven'e cek
    pos["tp1_alindi"] = True
    # kismi realize kaydi (2026-07-06): TP1 karlari log disinda kaliyordu -> karne ~$59 kari gormuyordu.
    # kismi=true satirlari islem SAYILMAZ (win-rate/R disi) ama toplam PnL'e dahil edilir.
    tutma_saat = (now_dt() - parse_iso(pos["giris_ts"])).total_seconds() / 3600
    kayit = {
        "ts": now_iso(), "id": pos["id"], "sym": pos["sym"], "yon": pos["yon"],
        "giris": round(pos["giris"], 6), "cikis": round(cikis_ef, 6),
        "kaldirac": pos["kaldirac"], "marjin": round(pos["marjin"] / 2.0, 2),
        "notional": round(yari * pos["giris"], 2), "sonuc_usdt": round(pnl_net, 2),
        "roi_pct": round(pnl_net / (pos["marjin"] / 2.0) * 100, 1) if pos["marjin"] else None,
        "r": None, "sebep": "TP1_KISMI", "kismi": True, "tutma_saat": round(tutma_saat, 1),
        "skor_giriste": pos.get("skor_giriste"), "smart_giriste": pos.get("smart_giriste"),
        "chg24_giriste": pos.get("chg24_giriste"), "range_pos_giriste": pos.get("range_pos_giriste"),
        "stage_giriste": pos.get("stage_giriste"), "sebep_giris": pos.get("sebep_giris"),
        "rejim_giriste": pos.get("rejim_giriste", "BILINMIYOR"),
        # 2026-08-05: "elle" ise botun karnesinden DISLANIR (panel_sunucu suzuyor)
        "kaynak": pos.get("kaynak"), "stop_elle": pos.get("stop_elle"),
    }
    _append_jsonl(_islem_defteri(), kayit)
    telegram_gonder(f"[TESTBOT] TP1 {pos['sym']} {pos['yon']} yari kapatildi PnL={pnl_net:+.2f}$ (stop girise cekildi)",
                    olay="tp1")


def funding_uygula(st, pos):
    start_ms = to_ms(pos.get("son_funding_kontrol_ts", pos["giris_ts"]))
    olaylar = funding_events_since(pos["sym"], start_ms)
    if not olaylar:
        return
    notional = pos["miktar"] * pos["giris"]
    for e in olaylar:
        isaret = 1 if pos["yon"] == "LONG" else -1
        maliyet = notional * e["rate"] * isaret  # LONG + pozitif funding = oder (equity azalir)
        st["equity"] -= maliyet
        st["kumulatif_funding"] = st.get("kumulatif_funding", 0.0) - maliyet
    pos["son_funding_kontrol_ts"] = now_iso()


def atr_canli_al(sym):
    """Cycle basina 1 kez taze ATR14 (1h/100 mum) - trailing_guncelle'de 'momentum yavasladi mi' proxy'si.
    Ag hatasi veya bar'siz/0 ATR -> None (cagiran taraf atr_giriste'ye fallback eder, davranis bozulmaz)."""
    try:
        bars = olcucu.fetch_klines(sym, "1h", 100, kapali=True)  # denetim Bulgu 3
        a = olcucu.atr(bars)
        return a if a and a > 0 else None
    except Exception:
        return None


def trailing_guncelle(pos, bar):
    """ATR trailing stop + ratchet + breakeven taban (2026-07-04 — 'kar %80-90 gorup geri veriyor' geri bildirimi).
    Kar >= trailing_r_esik*risk'e ulasinca aktiflesir; sonra stop SADECE kar yonunde sikilir, hic gevsetilmez.
    Kar buyudukce ATR katsayisi kademeli daralir (2R'de trailing_atr_kat_2r, 3R'de trailing_atr_kat_3r) —
    boylece buyuk kar gorup sonra tamamen geri veren/zarara donen pozisyonlar (ZKP/THE/ARPA ornekleri) onlenir.
    trailing_aktif oldugu andan itibaren stop, fee+slippage payi dahil breakeven'in gerisine ASLA dusmez.
    Canli ATR (2026-07-04, 'dusus yavasladiginda stopu sikilastir' fikri): atr_basis = min(atr_giriste, atr_canli) —
    volatilite gercekten daraldiysa (yavaslama sinyali) stop daha siki takip eder; volatilite genislerse eski
    (daha dar) mesafede kalinir, ASLA gevsetilmez. atr_canli yoksa (ag hatasi) atr_giriste'ye fallback.
    Eski/ATR'siz pozisyonlarda (atr_giriste yok) sabit stop/TP davranisi aynen devam eder."""
    pos.setdefault("stop_orijinal", pos["stop"])
    pos.setdefault("atr_giriste", None)
    pos.setdefault("atr_canli", None)
    pos.setdefault("en_iyi_fiyat", pos["giris"])
    pos.setdefault("trailing_aktif", False)
    # 2026-08-10: A+B pozisyonlarinda trailing DEVRE DISI — olcum, sabit %10 hedefin
    # trailing'li cikisi %62 gectigini gosterdi (+2.01% vs +1.24%). Stop orijinal yerinde
    # kalir; kazanci kesen mekanizma kapatilir. Gerekce yeni_giris_ac'taki blokta.
    if pos.get("cikis_modu") == "sabit_hedef":
        return
    if not pos["atr_giriste"]:
        return
    atr_canli = pos.get("atr_canli")
    atr_basis = min(pos["atr_giriste"], atr_canli) if atr_canli else pos["atr_giriste"]
    r_esik = evren.esik("trailing_r_esik", 1.0)
    atr_kat_taban = evren.esik("trailing_atr_kat", 2.0)
    atr_kat_2r = evren.esik("trailing_atr_kat_2r", 1.5)
    atr_kat_3r = evren.esik("trailing_atr_kat_3r", 1.0)
    risk_birim = abs(pos["giris"] - pos["stop_orijinal"])
    if risk_birim <= 0:
        return
    breakeven_pay = 0.0015  # taker x2 + slippage payi
    if pos["yon"] == "LONG":
        pos["en_iyi_fiyat"] = max(pos["en_iyi_fiyat"], bar["h"])
        if not pos["trailing_aktif"] and pos["en_iyi_fiyat"] >= pos["giris"] + risk_birim * r_esik:
            pos["trailing_aktif"] = True
        if pos["trailing_aktif"]:
            r_kar = (pos["en_iyi_fiyat"] - pos["giris"]) / risk_birim
            atr_kat = atr_kat_3r if r_kar >= 3 else (atr_kat_2r if r_kar >= 2 else atr_kat_taban)
            yeni_stop = pos["en_iyi_fiyat"] - atr_kat * atr_basis
            taban = pos["giris"] * (1 + breakeven_pay)
            pos["stop"] = round(max(pos["stop"], yeni_stop, taban), 6)
    else:
        pos["en_iyi_fiyat"] = min(pos["en_iyi_fiyat"], bar["l"])
        if not pos["trailing_aktif"] and pos["en_iyi_fiyat"] <= pos["giris"] - risk_birim * r_esik:
            pos["trailing_aktif"] = True
        if pos["trailing_aktif"]:
            r_kar = (pos["giris"] - pos["en_iyi_fiyat"]) / risk_birim
            atr_kat = atr_kat_3r if r_kar >= 3 else (atr_kat_2r if r_kar >= 2 else atr_kat_taban)
            yeni_stop = pos["en_iyi_fiyat"] + atr_kat * atr_basis
            tavan = pos["giris"] * (1 - breakeven_pay)
            pos["stop"] = round(min(pos["stop"], yeni_stop, tavan), 6)


def tp1_efektif_hesapla(giris, stop_orijinal, tp1_yapisal, yon):
    """R-tabanli kismi kar hedefi (2026-07-04 — TP1 pratikte hic tetiklenmiyordu, 2.6-5.2R uzaktaydi).
    Yapisal TP1 ile kismi_kar_r*risk hedefinden HANGISI DAHA YAKINSA o kullanilir (erken kismi kar).
    Idempotent: pos['tp1'] zaten migrasyon gormusse tekrar cagrilmasi sonucu degistirmez."""
    risk_birim = abs(giris - stop_orijinal)
    if risk_birim <= 0:
        return tp1_yapisal
    kismi_kar_r = evren.esik("kismi_kar_r", 1.5)
    if yon == "LONG":
        tp_r = giris + kismi_kar_r * risk_birim
        return min(tp1_yapisal, tp_r)
    else:
        tp_r = giris - kismi_kar_r * risk_birim
        return max(tp1_yapisal, tp_r)


def yonet_acik_pozisyonlar(st):
    kalanlar = []
    zaman_stop_saat = float(_c("zaman_stop_saat", 48))
    for pos in st["acik_pozisyonlar"]:
        try:
            son_ts = pos.get("son_1m_kontrol_ts", pos["giris_ts"])
            if not pos["tp1_alindi"]:
                pos["tp1"] = round(tp1_efektif_hesapla(
                    pos["giris"], pos.get("stop_orijinal", pos["stop"]), pos["tp1"], pos["yon"]), 6)
            if pos.get("atr_giriste"):
                pos["atr_canli"] = atr_canli_al(pos["sym"])
            bars = klines_since(pos["sym"], "1m", to_ms(son_ts))
            kapandi = False
            for b in bars:
                trailing_guncelle(pos, b)
                if pos["yon"] == "LONG":
                    # BUG-FIX 2026-07-15 (Madde 8, 1000XEC vakasi): ayni bar stop+liq'i birden
                    # supurunce eski kod liq isliyordu — kaldirac_guvenlik_kirp'in "stop liq'ten
                    # ONCE tetiklenir" garantisiyle celiski. Liq artik SADECE bar liq altinda
                    # ACILDIYSA (stop'un kurtaramayacagi gercek gap); yoksa stop oncelikli,
                    # gap-acilis stoptan kotuyse acilistan dolar (gercekci kayma).
                    bar_acilis = b.get("o", b["c"])
                    if bar_acilis <= pos["likidasyon"]:
                        pozisyon_liq(st, pos); kapandi = True; break
                    if b["l"] <= pos["stop"]:
                        pozisyon_kapat(st, pos, min(pos["stop"], bar_acilis), "STOP"); kapandi = True; break
                    if not pos["tp1_alindi"] and b["h"] >= pos["tp1"]:
                        pozisyon_kismi_tp1(st, pos, pos["tp1"])
                    if pos["tp1_alindi"] and b["h"] >= pos["tp2"]:
                        pozisyon_kapat(st, pos, pos["tp2"], "TP2"); kapandi = True; break
                else:  # SHORT (ayni bug-fix, simetrik)
                    bar_acilis = b.get("o", b["c"])
                    if bar_acilis >= pos["likidasyon"]:
                        pozisyon_liq(st, pos); kapandi = True; break
                    if b["h"] >= pos["stop"]:
                        pozisyon_kapat(st, pos, max(pos["stop"], bar_acilis), "STOP"); kapandi = True; break
                    if not pos["tp1_alindi"] and b["l"] <= pos["tp1"]:
                        pozisyon_kismi_tp1(st, pos, pos["tp1"])
                    if pos["tp1_alindi"] and b["l"] <= pos["tp2"]:
                        pozisyon_kapat(st, pos, pos["tp2"], "TP2"); kapandi = True; break
            # [DENETIM DUZELTMESI 2026-08-11, Bulgu 9] funding_uygula ESKIDEN `if kapandi:
            #   continue`den SONRA geliyordu -> pozisyonun KAPANDIGI turda son periyodun
            #   fonlamasi hic alinmiyordu. Tek yonlu (hep lehte) sapma. Kucuk (toplam
            #   kumulatif funding -6$) ama sistematik. Artik kapanistan BAGIMSIZ uygulanir.
            funding_uygula(st, pos)
            if kapandi:
                continue
            pos["son_1m_kontrol_ts"] = now_iso()
            yas_saat = (now_dt() - parse_iso(pos["giris_ts"])).total_seconds() / 3600
            if yas_saat >= zaman_stop_saat:
                px = fiyat_fapi(pos["sym"])
                if px:
                    pozisyon_kapat(st, pos, px, "ZAMAN_STOP")
                    continue
            kalanlar.append(pos)
        except Exception:
            kalanlar.append(pos)  # ag hatasi -> pozisyonu KAYBETME, bir sonraki cycle tekrar dener
    st["acik_pozisyonlar"] = kalanlar


# ---------- yeni giriş arama ----------

def _cikar_havuzdan(pool_syms, st, cooldown_saat):
    acik = {p["sym"] for p in st["acik_pozisyonlar"]}
    now = now_dt()
    out = []
    for s in pool_syms:
        if s in acik:
            continue
        son_kapanis = st["cooldown"].get(s)
        if son_kapanis and (now - parse_iso(son_kapanis)).total_seconds() / 3600 < cooldown_saat:
            continue
        out.append(s)
    return out


def yeni_giris_ac(st, sym, yon, r, pillar, sebep, zorla=False, rejim_ad=None,
                  olc_override=None, kaynak=None, red_out=None):
    """olc_override / kaynak: 2026-08-05'te eklendi, IKISI DE None iken davranis BIREBIR AYNI.
    olc_override: {"stop":..,"tp1":..,"tp2":..} — kullanici panelden stop/hedef duzenlerse.
      GIRIS FIYATI ve RISK-ONCE BOYUTLANDIRMA aynen korunur (2026-08-03 onarimi bozulmaz);
      yalnizca seviyeler degisir, boyut yeni stop mesafesine gore YENIDEN hesaplanir.
    kaynak: pozisyona ve kapanan kayda yazilir ("elle"). Karne ayrimi bunun uzerinden.

    red_out: 2026-08-10 — bu fonksiyonun retleri SESSIZDI (rr_veto haric). Karar_yon "SHORT"
      dedigi halde islem acilmiyordu ve hicbir yerde sebebi yazmiyordu: 08-08'de KMNO 19 kez
      SHORT karari aldi, 19'u da burada oldu, panelde "SHORT/ANINDA" gorunuyordu.
      Liste verilirse red sebebi {"kapi","detay","yon","olc"} olarak eklenir. Verilmezse
      davranis BIREBIR AYNI (mevcut cagiranlar degismedi)."""
    def _red(kapi, detay, olc=None):
        if red_out is not None:
            red_out.append({"kapi": kapi, "detay": detay, "yon": yon, "olc": olc})
        return False

    skor = r["score"]
    smart_hiz = smart_hizali_mi(yon, pillar.get("smart"))
    try:
        olc = olcucu.measure(sym, yon.lower(), "1h", 100, spot=False)
    except Exception as e:
        return _red("olcum_hatasi", f"olcucu.measure patladi: {str(e)[:80]}")
    if olc_override:
        for a in ("stop", "tp1", "tp2"):
            if olc_override.get(a) is not None:
                olc[a] = float(olc_override[a])
    # ============ R/R KAPISI — TEZAT ONARIMI (2026-08-10, Madde 8) =========================
    # [TEZAT] Kapi `VETO_rr_net` idi: YAPISAL tp1 net R/R < 2.0 -> giris yok. AMA bot bu tp1'i
    #   KULLANMIYOR: tp1_efektif_hesapla, TP1'i min(yapisal_tp1, giris + kismi_kar_r*risk)'e
    #   CEKIYOR (kismi_kar_r=1.5, 2026-07-04'te "TP1 pratikte hic tetiklenmiyordu, 2.6-5.2R
    #   uzaktaydi" diye eklendi). Yani bot, ASLA ALMAYI PLANLAMADIGI 2R'lik hedefe gore islem
    #   REDDEDIYORDU. Kapinin test ettigi hedef ile botun gittigi hedef AYNI DEGILDI.
    # [KANIT] 2026-08-08: KMNO 19 kez SHORT karari aldi, 19'u da burada oldu (rr 0.19).
    #   03-10 Agustos: 21 SHORT karari, 0 giris. Bot 3 gun hic islem acmadi.
    # [ONARIM] Kapi artik botun FIILEN gittigi ilk hedefi test eder: yapisal tp1, kismi-kar
    #   hedefinden (kismi_kar_r) UZAK olmali. Yeni esik ICAT EDILMEDI — mevcut `kismi_kar_r`
    #   config degeri kullanildi (tek dogruluk kaynagi). tp2'nin net R/R'si de loglanir.
    # [BU BIR GEVSETME MI?] Sayisal olarak evet (2.0 -> 1.5) ama gerekce esik-arama degil
    #   TUTARLILIK: iki hedef arasindaki celiski giderildi. Etkisi golge defterde olculecek
    #   (reddedilenler orada aciliyor) — karar degil, olcum bekleyen bir onarim.
    # GERI ALMA: kripto-config.json -> esikler.rr_kapisi_r: 2.0
    # [2026-08-10 — KAPI ETKISIZLESTIRILDI, kullanici karari, Madde 9]
    #   Arsiv olcumu (7.119 olay): kapi kazananlarin %62.8'ini, kaybedenlerin %61.8'ini kesiyor
    #   — AYIRT ETMIYOR. Ustelik GECIRDIGI grup kestiginden KOTU (-0.053 vs -0.008).
    #   Izole: A+B kapisiz +0.375 | A+B + rr>=1.5 -0.004 | kapinin ATTIGI grup +0.542.
    #   Tum kapilar birlikte: rr ile N=77 +0.011 | rr'siz N=212 +0.151.
    #   MEKANIZMA: rr_tp1 = en yakin yapisal destege uzaklik / risk. YUKSEK rr = "asagida yakin
    #   destek YOK" = coin zaten kirip bosluga dusmus (uzamis) -> ortalamaya donus geri ziplatiyor.
    #   Bot "kosacak yer var" sanip "zaten kosmus"u seciyordu. rr bandi TERS: 3.0+ -> -0.109.
    #   Ek: rr<1.5 olaylarin %43'u yine de 2R'ye ulasiyor -> yapisal TP1, fiyatin duracagi yerin
    #   kotu bir tahmini; kapinin dayandigi varsayim da zayif.
    #   rr_kapisi_r <= 0 -> kapi TAMAMEN devre disi (negatif rr_net bile gecer; olcum boyle yapildi).
    #   GERI ALMA: rr_kapisi_r: 1.5 (ya da eski davranis icin 2.0).
    rr_esik = evren.esik("rr_kapisi_r", evren.esik("kismi_kar_r", 1.5))
    rr_net = olc.get("rr_tp1_net")
    if rr_esik > 0 and rr_net is not None and rr_net < rr_esik and not zorla:
        # 2026-07-10: bu ret onceden SESSIZDI ("bot neden girmedi" cevabinda kor nokta) -> olcum loguna eklendi
        _veto_logla(st, sym, r, pillar, "rr_veto",
                    f"NET R/R {rr_net} < {rr_esik} (tp2 net {olc.get('rr_tp2_net')})",
                    yon, rejim_ad or "BILINMIYOR")
        # edge kanitlanmamis giris -> mekanik veto (Olcucu ile ayni disiplin)
        return _red("rr_veto", f"NET R/R {rr_net} < {rr_esik}", olc)
    giris_piyasa, stop, tp1_yapisal, tp2 = olc["giris"], olc["stop"], olc["tp1"], olc["tp2"]
    cst = _maliyet()
    giris_ef = maliyet_uygula_giris(giris_piyasa, yon, cst)

    # ================= RISK-ONCE BOYUTLANDIRMA ONARIMI (2026-08-03, Madde 8) =================
    # [ESKI DAVRANIS — HATA]  marjin ve kaldirac YALNIZ SKORDAN belirleniyor, stop mesafesinden
    #   bagimsizdi; risk sonucta OLUSUYOR, sadece TAVANI kirpiliyordu:
    #       kaldirac0 = kaldirac_hesapla(skor, smart);  marjin = equity*marjin_pct(skor)
    #       notional  = marjin*kaldirac;  risk = stop_frac*notional;  if risk>%5: kucult
    #   Bu, sistemin kendi "risk-once boyutlandirma" tanimiyla CELISIYORDU.
    # [OLCULDU — 7 gercek islem, risk = sonuc_usdt/r ile turetildi]
    #   PROM stop%1.5 -> risk $70  | AKE %2.3 -> $115 | DEXE %7.2 -> $178 | BLESS %7.5 -> $483
    #   Yani dolar riski 7 KAT degisiyordu ve farki yaratan KONVIKSIYON DEGIL STOP MESAFESIYDI
    #   (genis stop -> BUYUK risk; gercek risk-oncede tam TERSI olmali). En buyuk kayip
    #   (BLESS -$487.98) en genis stoplu islemden geldi, en iyi kurulumdan degil.
    # [ONARIM]  Risk artik HEDEFLENIR:  notional = hedef_risk / stop_frac
    #   Kaldirac bir GIRDI degil, bu notional'a ulasmanin ARACI (risk-once tanimi budur).
    #   Konviksiyon HALA etkili: skor -> marjin_pct (%8-12) ile SERMAYE TAHSISI surur
    #   (kullanicinin 2026-07-03 kurulum karari "skora gore degisken boyut" KORUNDU).
    # [KORUNANLAR]  kaldirac_guvenlik_kirp (stop likidasyondan ONCE) · kaldirac_min/max ·
    #   %5 tavani (artik hedef; kemer-aski olarak da duruyor) · smart-karsi yarim boyut.
    # [DEGISEN INCELIK]  smart karsi yonde artik MARJIN degil HEDEF RISK yarilanir. Sebep:
    #   kaldirac serbest kalinca marjini yarilamak riski dusurmuyordu (kaldirac telafi ederdi).
    # [SINIR]  Cok dar stoplarda hedef riske kaldirac_max yuzunden ULASILAMAZ -> risk hedefin
    #   ALTINDA kalir. Bu guvenli yondur; asla hedefin USTUNE cikilmaz.
    stop_frac = abs(giris_ef - stop) / giris_ef if giris_ef else 0.0
    if stop_frac <= 0:
        return _red("stop_gecersiz", f"stop_frac={stop_frac} (giris={giris_ef} stop={stop})", olc)
    # --- ASGARI STOP TABANI (2026-08-11, Madde 10) --------------------------------------------
    # OLCUM (577 canli-kapi olayi, hedef %10/72s): stop dilimlerine gore isabet
    #   <%1.92 -> %10.3 (basabas ~%16) · %1.92-3.40 -> %20.1 · %3.40-5.51 -> %33.3 · >%5.51 -> %56.2
    #   Dar dilim basabasin ALTINDA -> net sifir uretiyor ama tam boyutla alinip ucret ve slot yiyor.
    # MEKANIZMA: dar A-stop = direnc hemen tepede -> islem gelismeden gurultuyle deliniyor.
    # STOPU GENISLETMEK ISE YARAMIYOR (olculdu): isabet %11.0->%13.6 ama basabas %12.1->%16.7;
    #   basabas isabetten hizli buyuyor -> "kovalama tuzagi"nin stop tarafindaki hali. O yuzden ELE.
    # ETKI: olay basina +%0.58 -> +%0.78, toplam kar ayni (+334 -> +330), islem %27 az.
    # ESIK GEREKCESI: %2.0 = isabetin basabasin ALTINDA kaldigi bolgenin siniri (tablonun
    #   maksimumu %2.5'ti, ONE-KAYIT geregi secilmedi -> gerekcesi "tabloya baktim" olurdu).
    # GERI ALMA: kripto-config.json -> testbot.asgari_stop_pct: 0
    asg = float(_c("asgari_stop_pct", 0))
    if asg > 0 and stop_frac * 100 < asg and not zorla:
        return _red("stop_cok_dar", f"stop %{stop_frac*100:.2f} < asgari %{asg:.1f}", olc)
    # ------------------------------------------------------------------------------------------
    # [DENETIM DUZELTMESI 2026-08-11, Bulgu 1] Boyut artik EFEKTIF equity'ye (gerceklesmis +
    #   acik P&L) gore. Eskiden yalniz gerceklesmis equity kullaniliyordu; acik zarar buyurken
    #   bot pozisyon boyutunu KUCULTMUYOR, ayni buyuklukte acmaya devam ediyordu.
    #   efektif_equity() cycle basinda hesaplanip state'e yazilir; burada agdan tekrar
    #   cekilmez. Yoksa (ilk cycle, --zorla, test) gerceklesmis equity'ye duser.
    baz_equity = float(st.get("efektif_equity") or st["equity"])
    hedef_risk = baz_equity * float(_c("islem_risk_pct", 5)) / 100.0
    if not smart_hiz and pillar.get("smart") not in (None, "NOTR"):
        hedef_risk /= 2.0                      # smart karsi yonde -> RISK yari
    marjin = baz_equity * marjin_pct_hesapla(skor)
    kmin, kmax = float(_c("kaldirac_min", 3)), float(_c("kaldirac_max", 10))
    kald_gerekli = ((hedef_risk / stop_frac) / marjin) if marjin > 0 else kmin
    kaldirac0 = int(round(max(kmin, min(kmax, kald_gerekli))))
    kaldirac = kaldirac_guvenlik_kirp(giris_piyasa, stop, yon, kaldirac0)
    if kaldirac is None:
        kaldirac = 2 if zorla else None
        if kaldirac is None:
            # stop cok genis -> hicbir kaldiracta guvenli degil (stop likidasyondan SONRA kalirdi)
            return _red("kaldirac_guvenlik", f"stop %{stop_frac*100:.1f} -> guvenli kaldirac yok", olc)
    notional = marjin * kaldirac
    miktar = notional / giris_ef
    risk_usdt = stop_frac * notional
    if risk_usdt > hedef_risk and risk_usdt > 0:   # hedefin USTUNE asla cikma
        kucult = hedef_risk / risk_usdt
        marjin *= kucult; notional *= kucult; miktar *= kucult; risk_usdt = hedef_risk
    # ==========================================================================================
    liq = likidasyon_fiyati(giris_ef, yon, kaldirac)
    taker = float(cst.get("taker_fee_pct", 0.045)) / 100.0
    st["equity"] -= notional * taker  # giris ucreti
    st["kumulatif_giris_ucret"] = st.get("kumulatif_giris_ucret", 0.0) + notional * taker
    tp1 = tp1_efektif_hesapla(giris_ef, stop, tp1_yapisal, yon)
    pos = {
        "id": st["sonraki_id"], "sym": sym, "yon": yon, "giris": round(giris_ef, 6),
        "giris_ts": now_iso(), "marjin": round(marjin, 2), "kaldirac": kaldirac,
        "miktar": miktar, "stop": round(stop, 6), "tp1": round(tp1, 6), "tp2": round(tp2, 6),
        "tp1_alindi": False, "likidasyon": round(liq, 6), "risk_usdt": round(risk_usdt, 2),
        "skor_giriste": skor, "smart_giriste": pillar.get("smart"),
        "chg24_giriste": r.get("chg24"), "range_pos_giriste": r.get("pos"), "stage_giriste": r.get("stage"),
        "rejim_giriste": rejim_ad or "BILINMIYOR",  # 2026-07-08: rejim x yon karne icin (hem-ayi-hem-boga olcumu)
        "son_funding_kontrol_ts": now_iso(), "son_1m_kontrol_ts": now_iso(), "sebep_giris": sebep,
        # trailing stop icin (2026-07-03, "piyasa donunce de TP/SL bekliyor" geri bildirimi):
        "stop_orijinal": round(stop, 6), "atr_giriste": olc.get("atr14"),
        "en_iyi_fiyat": giris_ef, "trailing_aktif": False,
    }
    if kaynak:                      # 2026-08-05: "elle" -> karne ayrimi bunun uzerinden
        pos["kaynak"] = kaynak

    # ---- A+B GIRISLERINE SABIT HEDEF (2026-08-10, KULLANICI KARARI, Madde 9) --------------
    # [NEDEN] A+B edge'i HEDEF BUYUDUKCE ARTIYOR — isabet, basabasi hedef buyudukce daha cok
    #   geciyor (N=206): %2.5 -> +0.47 | %5 -> +1.33 | %10 -> +2.19 | %15 isabet basabasin ALTINA.
    #   Ayni 206 giriste cikis kurallari karsilastirildi:
    #     MEVCUT (kismi %50 @1.5R + ATR trailing)  +1.24%  kazanan %66  (A +1.22 / B +1.25)
    #     sabit %10 hedef, trailing yok            +2.01%  kazanan %50  (A +1.95 / B +2.08)
    #   -> %62 daha fazla beklenti, iki yarida da ayni siralama. Bedeli: kazanma orani %66->%50.
    # [KURAL] Kotu giriste siki cikis KAYBI keser; iyi giriste siki cikis KAZANCI keser.
    #   Bu yuzden degisiklik GIRIS-KOSULLU: yalniz A+B pozisyonlari. Diger dallar (AYI-SHORT,
    #   smart-SHORT, AAVE-istisnasi...) mevcut kismi+trailing ile KALIR — onlarin girisi icin
    #   siki cikis hala en iyisiydi (10 gercek islemde olculmustu).
    # [NASIL] tp2 = giris ±%10 · tp1_alindi=True (kismi kar DEVRE DISI) · trailing DEVRE DISI
    #   (trailing_guncelle bu modda erken doner) · stop ORIJINAL A-stop'ta kalir ·
    #   48 saat zaman stopu AYNEN gecerli.
    # [SINIR] Olcum 1 SAATLIK mumla; bot 1 DAKIKALIK ile yonetiyor -> gercek MEVCUT biraz daha
    #   iyi olabilir. Funding maliyeti eklenmedi (uzun tutusta artar, MEVCUT lehine duzeltme).
    # GERI ALMA: kripto-config.json -> esikler.ab_sabit_hedef_pct: 0
    # 2026-08-11: MA50+ucuz kapisi da ayni muameleyi gorur — olcumu de %10 hedefle
    # yapildi (net +0.84%, A +0.99 / B +0.72). Kismi kar/trailing bu girislerde de kapali.
    SABIT_HEDEF_KAPILARI = ("A+B", "MA50+ucuz")
    ab_hedef = evren.esik("ab_sabit_hedef_pct", 10.0)
    if ab_hedef > 0 and str(sebep).startswith(SABIT_HEDEF_KAPILARI):
        pos["cikis_modu"] = "sabit_hedef"
        pos["tp2"] = round(giris_ef * (1 - ab_hedef / 100) if yon == "SHORT"
                           else giris_ef * (1 + ab_hedef / 100), 6)
        pos["sabit_hedef_pct"] = ab_hedef
        # --- KISMI KAR (2026-08-11, kullanici karari) -----------------------------------
        # [NE] Hedefin `kismi_pay` kadarina gelince pozisyonun YARISI satilir, kalan yari
        #   ayni stop ve ayni %10 hedefle devam eder. kismi_pay=0 -> kapali (eski davranis).
        # [OLCUM] 577 canli-kapi olayi, hedef %10/72s, Wilder ATR, maliyet %0.13.
        #   Sermaye getirisi (islem basi): kismi YOK +0.301 · %60 +0.280 · %40 +0.274 ·
        #   %50 +0.270 · %30 +0.205.  YANI KISMI KAR OLCUMDE KENARI KUCULTUYOR.
        #   Mekanizma: hedefe ULASMA orani DEGISMIYOR (%29.1 ikisinde de), ama kazanan
        #   islemde kazancin ~%30'u kesiliyor; kaybedende zarar kapaniyor. Bu kapida
        #   kazananlar kaybedenlerden buyuk oldugu icin takas zararina.
        # [YINE DE ACILDI] Kullanici karari: tek islem bazinda kar korumasi ve dalgalanma
        #   dusuklugu icin kenarin bir kismindan bilerek vazgecildi (%30'da ~%32'si).
        # [STOP] Kismi sonrasi stop BASABASA CEKILMEZ — olculdu: cekilirse +0.274 -> +0.261.
        #   pozisyon_kismi_tp1 bunu cikis_modu'na bakarak ayirt eder.
        # GERI ALMA: kripto-config.json -> esikler.kismi_pay: 0
        pay = evren.esik("kismi_pay", 0.0)
        if pay > 0:
            kismi_pct = ab_hedef * pay
            pos["tp1"] = round(giris_ef * (1 - kismi_pct / 100) if yon == "SHORT"
                               else giris_ef * (1 + kismi_pct / 100), 6)
            pos["tp1_alindi"] = False                # kismi kar yolu ACIK
            pos["kismi_pay"] = pay
        else:
            pos["tp1_alindi"] = True                 # kismi kar yolu kapali
            pos["tp1"] = pos["tp2"]
    if olc_override:
        pos["stop_elle"] = True
    st["sonraki_id"] += 1
    st["acik_pozisyonlar"].append(pos)
    _aynala(pos)
    telegram_gonder(f"[TESTBOT] GIRIS {sym} {yon} {kaldirac}x marjin=${marjin:.2f} "
                     f"giris={giris_ef:.6g} stop={stop:.6g} tp1={tp1:.6g} skor={skor} — {sebep}",
                    olay="giris")
    toast_gonder("TestBot GIRIS", f"{sym} {yon} {kaldirac}x skor={skor}", olay="giris")
    return True


def _aynala(pos):
    """Acilan pozisyonu AYNA deftere kopyala (2026-08-12). FAIL-SAFE: ayna.py yoksa,
    coker veya yavaslarsa BOT ETKILENMEZ. Karar/veto mantigina HICBIR dokunus yok;
    bu cagri yalnizca 'ben bu pozisyonu erken kapatsaydim' sorusunu olculebilir kilar.
    Kopya BIREBIR olmali (fiyat/boyut/stop/TP yeniden hesaplanmaz) — yoksa iki defter
    ayni islemi degil, iki farkli islemi kiyaslar ve eslestirmenin gucu kaybolur.

    [HATA VE ONARIMI 2026-08-12] yeni_giris_ac BOTA OZEL DEGIL: golge.py ve benim.py
    de ayni fonksiyonu cagirir (defter yolunu _DEFTER ile gecici degistirerek). Kanca
    korumasiz konuldugu icin GOLGE girisleri de aynaya dustu — ayna, botun HIC acmadigi
    LONG'lari (pump_long_tezi) acmis gorundu (BLESS/BTW/BEAT/APR) ve equity'si sapti.
    KORUMA: _DEFTER None ise cagri GERCEK bota aittir; degilse baska bir defter
    (golge/benim/ayna) icin kosuyoruz demektir ve aynalamayiz."""
    if _DEFTER is not None:
        return False
    try:
        import ayna
        return ayna.aynala(pos)
    except Exception as e:
        print(f"[{now_iso()}] ayna kaydi atlandi (bot etkilenmedi): {str(e)[:90]}")
        return False


def _golge(sym, yon, r, pillar, kapi, detay="", rejim_ad=None):
    """Reddedilen girisi GOLGE deftere yaz (2026-08-10). FAIL-SAFE: golge.py yoksa,
    coker veya yavaslarsa BOT ETKILENMEZ — olcum katmani hicbir zaman karar
    katmanini durduramaz. Karar/veto mantigina HICBIR dokunus yok; bu cagri yalnizca
    'reddedilen giris ne yapardi' sorusunu olculebilir kilar."""
    try:
        import golge
        return golge.ac(sym, yon, r, pillar, kapi, detay, rejim_ad)
    except Exception as e:
        print(f"[{now_iso()}] golge kaydi atlandi (bot etkilenmedi): {str(e)[:90]}")
        return False


def yeni_giris_ara(st, rejim):
    maks_poz = int(_c("maks_pozisyon", 4))
    if len(st["acik_pozisyonlar"]) >= maks_poz:
        return
    # MAKRO GUVENLIK-KAPISI (2026-07-23, KURTİ/SISTEM.md odunc — olculmus edge DEGIL, RISK azaltir):
    # FOMC <=48s iken YENI GIRIS YOK (bilinen yuksek-etkili olaya fade girip squeeze yeme riski). Acik
    # pozlar ETKILENMEZ (cycle'da bu fonksiyon ONCESI yonet_acik_pozisyonlar kostu). SADECE makro.takvim()
    # = yerel dosya, NETWORK YOK, deterministik (DXY/ETF network'une girmez). Yon/skor DEGISTIRMEZ,
    # sadece "simdi acma". Hata -> fail-open (bot calisir; kapi kritik-altyapi degil). config: makro_kapi_aktif.
    if bool(_c("makro_kapi_aktif", True)):
        try:
            tk = makro.takvim()
            if tk.get("veto_fomc_48s"):
                fk = (tk.get("fomc") or {}).get("kalan_gun")
                print(f"[{now_iso()}] MAKRO-KAPI: FOMC {fk}g icinde -> yeni giris YOK (acik pozlar yonetiliyor)")
                return
        except Exception as e:
            print(f"[{now_iso()}] makro-kapi kontrol hatasi (giris devam, fail-open): {e}")
    min_vol = float(_c("min_vol_musd", 3))
    havuz_n = int(_c("tarama_havuz_n", 150))
    # KRIPTO-ONLY + genisletilmis evren (2026-07-23 kullanici karari, Madde 9). ESKIDEN:
    # binance_pool(..., None)[:40] -> cryptos=None tokenize-hisse (SKHY/SPCX/INTC/MSTR...) ELEMIYORDU
    # + kapak 40'ta. SIMDI: cg_universe ile kripto-only (hisse elenir) + kapak havuz_n + taban $3M
    # (dusuk-mcap kripto anomalilerini de tara; sanal para, slipaj kullanici karariyla goz ardi).
    # cg_universe basarisizsa kripto-only o cycle atlanir (degrade, nadir; hisse geri sizabilir).
    cryptos_cache = evren.cg_universe()
    pool = evren.binance_pool("fapi", min_vol,
                              cryptos=(set(cryptos_cache.keys()) if cryptos_cache else None))[:havuz_n]
    chg24_harita = {s: chg for s, _, chg in pool}  # 24s % degisim -> blow-off filtresi icin (karar_yon)
    syms = _cikar_havuzdan([s for s, _, _ in pool], st, cooldown_saat=4)
    if not syms:
        return
    btc_chg3, _ = radar.btc_ref()  # cryptos_cache yukarida cg_universe ile dolduruldu (kripto-only + float_oran)
    aday_rows = []
    for sym in syms:
        try:
            r = radar.analyze(sym, btc_chg3)
            if r and r["score"] >= 30:
                r["chg24"] = chg24_harita.get(sym, 0.0)
                aday_rows.append(r)
        except Exception:
            continue
        time.sleep(random.uniform(0.05, 0.15))  # rate-limit guvenlik payi (2026-07-08)
    # ---- PUMP-ONCESI ONCELIK (2026-08-10, kullanici karari: "pumplamis coinleri
    #      pumplamadan kesfetsin") ------------------------------------------------------
    # [KANIT — OTOPSI-3, 2026-08-03, 41 gun, fitil bazli yol testi, SHORT]
    #     BASLIYOR     (vol_x>2.5 & last1>2 & oi3>3)  N=69  ort R -0.09  <- amiral gemisi etiket
    #     izle                                        N=796 ort R +0.07
    #     HAZIRLANIYOR (comp<0.65 & |last3|<4 & oi24>8) N=162 ort R +0.19  <- EN IYI
    #   HAZIRLANIYOR = sikismis + fiyat YATAY + pozisyon birikiyor = tam olarak "pump ONCESI".
    #   Ve skordan BAGIMSIZ ayirt ediyor: skor<45 icinde bile +0.22 vs izle +0.01 (N=116).
    #   O olcum "aksiyon alinmadi" diye rafta duruyordu; kullanici karariyla artik SIRALAMAYA giriyor.
    # [NE DEGISTI] Yalnizca KISA LISTEYE GIRME SIRASI. Skorun kendisi, kapilar, karar mantigi
    #   DEGISMEDI — HAZIRLANIYOR adayi da tum vetolardan aynen gecmek zorunda. Onceden liste
    #   sirf skora gore diziliyordu; skor bir ACIK-POZISYON DEDEKTORU (skor otopsisi BULGU 1)
    #   oldugu icin en yuksek skorlular sistematik olarak zaten HAREKET ETMIS coinlerdi.
    # GERI ALMA: kripto-config.json -> esikler.hazirlaniyor_sira_bonus: 0
    sira_bonus = evren.esik("hazirlaniyor_sira_bonus", 8.0)
    aday_rows.sort(key=lambda x: -(x["score"] + (sira_bonus if x.get("stage") == "HAZIRLANIYOR" else 0.0)))
    aday_rows = aday_rows[:10]  # Pillar D sadece kisa listeye (API bütçesi)

    bekleyenler = st.setdefault("bekleyenler", {})
    for sym in list(bekleyenler.keys()):
        if sym not in {r["sym"] for r in aday_rows}:
            bekleyenler[sym]["cycle_sayaci"] = bekleyenler[sym].get("cycle_sayaci", 0) + 1
            if bekleyenler[sym]["cycle_sayaci"] > 6:  # ~30dk gecti, aday soguladi -> iptal
                del bekleyenler[sym]

    # Para-kapisi (2026-07-23 kullanici karari, Madde 9): TOTAL mcap 7g net cikista (risk-off,
    # <=-%2) long kapali. Dongu basina 1 kez (log okumasi); log yok/az -> None -> kapi KAPALI
    # (fail-open, mevcut davranis korunur). LONG-kisitlayici — SHORT/fade'e dokunmaz.
    _pr = evren.para_rejim()
    para_cikis = bool(_pr and _pr.get("rejim") == "PARA CIKIYOR")
    if para_cikis:
        print(f"[{now_iso()}] PARA-KAPISI aktif: PARA CIKIYOR (TOTAL 7g {_pr['total_chg']:+.1f}%) -> long-veto")

    # BTC-PAY katmani (2026-08-04): gunluk anlik goruntu tazelenir, sonra bant okunur.
    # guncelle() ayni gun icin ikinci kez cagrilirsa hicbir sey yapmaz (ucuz).
    evren.btc_pay_guncelle()
    btc_pay = evren.btc_pay_akisi()
    para_durgun = bool(_pr and _pr.get("rejim") == "PARA DURGUN")
    if btc_pay:
        print(f"[{now_iso()}] BTC-PAY: {btc_pay['degisim']:+.2f} puan/3g -> bant={btc_pay['bant']}"
              f"{'  (SHORT freni AKTIF)' if btc_pay['bant']=='UST' else ''}"
              f"{'  (AYI long penceresi ACIK)' if btc_pay['bant']=='UST' and para_durgun else ''}")

    for r in aday_rows:
        if len(st["acik_pozisyonlar"]) >= maks_poz:
            break
        sym = r["sym"]
        try:
            pillar = radar.pillar_d(sym)
        except Exception:
            pillar = {"top_ls": None, "glob_ls": None, "taker": None, "smart": None}
        r["_pillar"] = pillar          # aday arsivi icin (2026-08-04, olcum; karari etkilemez)

        dusuk_float = False
        if r.get("dip_yakit"):
            if cryptos_cache is None:
                cryptos_cache = evren.cg_universe()
            fo = (cryptos_cache.get(sym) or {}).get("float_oran")
            esik_fo = evren.esik("dusuk_float_oran", 0.25)
            dusuk_float = bool(fo is not None and fo < esik_fo)
            r["_float_oran"] = fo
        r["_dusuk_float"] = dusuk_float

        # --- GOLGE-LONG: "pump'a binme" tezi CANLI olcumu (2026-08-10, kullanici istegi) ----
        # Kullanici LONG istiyor; arsiv olcumu her hucrede negatif verdi (tum evren 570 sembol,
        # 3 tetik esigi, 5 giris zamanlamasi, 2 ufuk, %10 hedef -> hicbiri pozitif degil).
        # Cozum: tez GERCEK deftere DOKUNMADAN golgede canli test edilir. Bot bu satirdan
        # etkilenmez — golge ayri kasa, ayri dosya, hata durumunda sessizce atlanir.
        # Tetik: pump olusuyor (chg24 >= %10 ve hacim patlamasi) -> golgede LONG acilir.
        # GERI ALMA: kripto-config.json -> esikler.golge_long_pump: 0
        try:
            if (evren.esik("golge_long_pump", 1) >= 1
                    and (r.get("chg24") or 0) >= 10 and (r.get("vol_x") or 0) >= 2.0):
                _golge(sym, "LONG", r, pillar, "pump_long_tezi",
                       f"chg24 {r.get('chg24'):+.0f}% vol_x {r.get('vol_x'):.1f}x",
                       rejim.get("rejim"))
        except Exception:
            pass

        vlist = []
        karar = karar_yon(rejim.get("rejim"), r, pillar, dusuk_float, veto_out=vlist,
                          para_cikis=para_cikis, btc_pay=btc_pay, para_durgun=para_durgun)
        r["_karar"] = (f"{karar[0]}/{karar[1]}" if karar
                       else (f"VETO:{vlist[0]['kategori']}" if vlist else "karar-yok"))
        if not karar:
            for v in vlist:  # reddedilen aday -> olcum logu (davranis degismedi, sadece kaydediliyor)
                _veto_logla(st, sym, r, pillar, v["kategori"], v["detay"], v["olurdu_yon"], rejim.get("rejim"))
            if vlist and vlist[0].get("olurdu_yon"):   # ilk veto = karari kesen kapi
                _golge(sym, vlist[0]["olurdu_yon"], r, pillar, vlist[0]["kategori"],
                       vlist[0].get("detay", ""), rejim.get("rejim"))
            bekleyenler.pop(sym, None)
            continue
        yon, mod, sebep = karar

        if mod == "ANINDA":
            bekleyenler.pop(sym, None)
            red = []
            if yeni_giris_ac(st, sym, yon, r, pillar, sebep,
                             rejim_ad=rejim.get("rejim"), red_out=red):
                r["_sonuc"] = "ACILDI"
            else:
                # Karar VERILDI ama giris kapisinda oldu (rr_veto / kaldirac_guvenlik / ...).
                # 08-08 KMNO: 19 kez buraya dustu ve hicbir yerde gorunmedi.
                r["_sonuc"] = "GIRIS_KAPISI"
                if red:
                    r["_red_kapi"] = red[0]["kapi"]
                    print(f"[{now_iso()}] GIRIS-KAPISI {sym} {yon}: {red[0]['kapi']} — {red[0]['detay']}")
                    _golge(sym, yon, r, pillar, red[0]["kapi"], red[0]["detay"], rejim.get("rejim"))
            continue

        # ONAY_BEKLE: bu adayi ilk kez mi goruyoruz?
        onceki = bekleyenler.get(sym)
        if onceki and onceki.get("yon") == yon:
            onceki["cycle_sayaci"] = onceki.get("cycle_sayaci", 0) + 1
            # SHORT soguma teyidi (2026-07-06, VANRY -$53 / BIRB -$12 dersi): 1-cycle beklemek pump
            # ivmesinin kirildigini OLCMUYOR. Onay aninda taker hala alis baskin (>= esik) ise pump
            # suruyor demektir -> acma, bekletmeye devam (taker sogursa veya karar None olursa cozulur).
            # taker None (veri yok) ise engelleme (eski davranis korunur).
            taker_onay = pillar.get("taker")
            taker_esigi = evren.esik("short_onay_taker_max", 1.05)
            soguma_ok = (yon != "SHORT") or (taker_onay is None) or (taker_onay < taker_esigi)
            if onceki["cycle_sayaci"] >= 1 and soguma_ok:  # 1 tam cycle (5dk) gecti + ivme kirildi -> onayla
                del bekleyenler[sym]
                red = []
                if yeni_giris_ac(st, sym, yon, r, pillar, sebep + " (onaylandi)",
                                 rejim_ad=rejim.get("rejim"), red_out=red):
                    r["_sonuc"] = "ACILDI"
                elif red:
                    r["_sonuc"] = "GIRIS_KAPISI"
                    r["_red_kapi"] = red[0]["kapi"]
                    print(f"[{now_iso()}] GIRIS-KAPISI {sym} {yon}: {red[0]['kapi']} — {red[0]['detay']}")
                    _golge(sym, yon, r, pillar, red[0]["kapi"], red[0]["detay"], rejim.get("rejim"))
            elif onceki["cycle_sayaci"] >= 1 and not soguma_ok:  # onaya hazir ama taker sogumadi -> bekletiliyor (olcum)
                _veto_logla(st, sym, r, pillar, "taker_soguma",
                            f"SHORT onay bekletildi: taker={taker_onay} >= {taker_esigi} (pump ivmesi surer)", "SHORT", rejim.get("rejim"))
        else:
            bekleyenler[sym] = {"yon": yon, "skor": r["score"], "ilk_gorulme_ts": now_iso(), "cycle_sayaci": 0}
            # ONAY_BEKLE'nin kendisi de bir KAPI: son 7 gunde 33 aday burada bekledi, hicbiri
            # onaylanmadi (aday ilk-10'dan dusunce iptal). "Beklemek para kazandiriyor mu yoksa
            # firsati mi kaciriyor" sorusu ancak beklemeden girilen hali olculurse cevaplanir.
            _golge(sym, yon, r, pillar, "onay_bekle", sebep, rejim.get("rejim"))

    # Aday evreni arsivi (2026-08-04) — dongü BITTIKTEN sonra, tek yazim. maks_poz'da break
    # olduysa geri kalan adaylarda pillar/karar null kalir; bu bilincli ve durustce bos yazilir.
    _aday_arsivle(aday_rows, rejim.get("rejim"), btc_chg3)


# ---------- ana döngü ----------

def _tum_fiyatlar():
    """TEK cagrida butun perp fiyatlari. 2026-08-12: acik_pnl_toplam her pozisyon icin
    ayri ticker cagirir ve cycle icinde birkac kez calisir (fren + equity logu + panel).
    6 pozisyonda 12-18 gereksiz istek demekti; API basincini artiriyordu (11 Agustos'ta
    toplu indirme yuzunden turlar 4 dk siniri asip OLDURULMUSTU — az istek = az risk)."""
    try:
        d = _get(f"{FAPI}/fapi/v1/ticker/price")
        return {x["symbol"]: float(x["price"]) for x in d} if isinstance(d, list) else {}
    except Exception:
        return {}


def acik_pnl_toplam(st, fiyatlar=None):
    if not st["acik_pozisyonlar"]:
        return 0.0
    if fiyatlar is None:
        fiyatlar = _tum_fiyatlar()
    toplam = 0.0
    for pos in st["acik_pozisyonlar"]:
        px = fiyatlar.get(pos["sym"] + "USDT")
        if px is None:
            px = fiyat_fapi(pos["sym"])       # toplu cagri basarisizsa tek tek (fail-safe)
        if px is None:
            continue
        yon_isaret = 1 if pos["yon"] == "LONG" else -1
        toplam += (px - pos["giris"]) * pos["miktar"] * yon_isaret
    return toplam


def efektif_equity(st):
    """GERCEKLESMIS + ACIK P&L. Denetim Bulgu 1 (2026-08-11) duzeltmesi.

    st["equity"] yalnizca kapanmis islemleri toplar; acik pozisyonlar ne kadar zararda
    olursa olsun ona girmez. Fren ve boyutlandirma BU degeri kullanmali, yoksa koruma
    zarar KESINLESENE kadar kor kalir.

    Sonuc st["efektif_equity"]'e yazilir; ayni cycle icinde yeniden ag cagrisi yapilmasin
    diye yeni_giris_ac oradan okur (her giris denemesinde 8 pozisyon icin ticker cekmek
    cycle'i yavaslatirdi).
    """
    ef = st["equity"] + acik_pnl_toplam(st)
    st["efektif_equity"] = round(ef, 2)
    st["efektif_equity_ts"] = now_iso()
    return ef


def _kilit_al(timeout_sn=240):
    """Ayni anda 2 cycle calismasin (2026-07-03 kaniti: manuel calistirma + zamanlayici cakisti,
    TLM kapanisi 2 KEZ loglandi — istatistikleri sisiriyordu). Kilit dosyasi timeout_sn'den eskiyse
    (onceki process muhtemelen coktu/takildi) yine de devam edilir (stale-lock kurtarma)."""
    if os.path.exists(LOCKF):
        try:
            yas = time.time() - os.path.getmtime(LOCKF)
        except Exception:
            yas = timeout_sn + 1
        if yas < timeout_sn:
            return False
    try:
        with open(LOCKF, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass
    return True


def _kilit_birak():
    try:
        os.remove(LOCKF)
    except Exception:
        pass


def cycle():
    if not _kilit_al():
        print(f"[{now_iso()}] baska bir instance calisiyor, bu cycle atlandi")
        return
    try:
        _cycle_ic()
    finally:
        _kilit_birak()


def _cycle_ic():
    st = _load_state()
    if st is None:
        st = yeni_state()
        _save_state(st)
        telegram_gonder(f"[TESTBOT] BASLADI — baslangic bakiye ${st['baslangic_bakiye']:.0f} sanal, sure {int(_c('sure_gun', 7))} gun")

    gun_gecti = (now_dt() - parse_iso(st["baslangic_ts"])).total_seconds() / 86400
    sure_gun = float(_c("sure_gun", 7))
    min_equity = float(_c("min_equity_dur", 50))

    # SURE SINIRI (2026-08-10 kullanici karari: "an itibari ile sure sinirli olmadan calissin")
    # sure_gun <= 0 -> SINIRSIZ. Eskiden 19 gundu ve 11 Agustos 19:07'de bot yeni giris aramayi
    # TAMAMEN birakacakti; bu "bot neden girmiyor"un yaklasan sessiz sebebiydi.
    if sure_gun > 0 and st["durum"] == "AKTIF" and gun_gecti >= sure_gun:
        st["durum"] = "SURE_DOLDU"
        telegram_gonder(f"[TESTBOT] SURE DOLDU ({sure_gun} gun) — yeni giris YOK, acik pozisyonlar dogal kapanisini bekliyor")
    if st["durum"] == "AKTIF" and st["equity"] <= min_equity:
        st["durum"] = "HALT_BAKIYE"
        telegram_gonder(f"[TESTBOT] BAKIYE BITTI (${st['equity']:.2f}) — islem DURDU")

    # DUSUS FRENI (2026-08-10) — sure sinirinin YERINE gecen koruma.
    # [NEDEN] Sure siniri yalnizca bir zaman-kapisi degil, ZORUNLU DEGERLENDIRME NOKTASIYDI
    #   (K1-K6 kapilari orada acilirdi). Sinirsiz calisan bot bu duraga hic ugramaz; yerine
    #   sonuca bagli bir durak gerekir. kazanan-bot-arastirma-raporu §8 madde 3 zaten bunu
    #   oneriyordu ("portfoy-dusus limiti") ve hic uygulanmamisti.
    # [NASIL] Equity zirveden maks_dusus_pct kadar geri cekilirse YENI GIRIS durur; acik
    #   pozisyonlar yonetilmeye DEVAM eder (yarim birakma yok). Insan `--devam` ile acar.
    # [NOT] min_equity_dur=50 ($10.000'de %99.5 kayip) pratikte hicbir zaman tetiklenmez;
    #   gercek koruma bu. 0 yazilirsa fren kapanir.
    # [DENETIM DUZELTMESI 2026-08-11, Bulgu 1 — YUKSEK] Fren ESKIDEN yalniz st["equity"]'ye
    #   bakiyordu; equity ise SADECE kapanmis islemleri toplar. acik_pnl_toplam() vardi ama
    #   yalnizca log ve --durum ciktisinda kullaniliyordu, hicbir KARAR dalinda degil.
    #   OLCUM (2026-08-11 canli): fren 8.401$ goruyordu, acik notional 21.889$ = sermayenin
    #   2,61 KATI. Acik pozisyonlar birlikte %10 aleyhe gitse gercek sermaye 6.212$'a (-%26)
    #   duserdi ama fren hala 8.401 gorup TETIKLENMEZDI.
    #   AYRICA fren, yonet_acik_pozisyonlar'dan ONCE calisiyordu -> bir tur GEC olcuyordu.
    # [DUZELTME] (a) pozisyonlar yonetildikten SONRA calisir, (b) EFEKTIF equity'ye bakar
    #   (gerceklesmis + acik P&L), (c) ayni efektif deger boyutlandirmada da kullanilir ki
    #   acik zarar buyurken pozisyon boyutu da kuculsun.
    yonet_acik_pozisyonlar(st)
    # Kapanislar HEMEN diske (2026-07-14 VELVET dersi, Madde 8 bug-fix): islem kaydi pozisyon_kapat
    # icinde aninda yaziliyor ama state cycle sonunda kaydediliyordu -> arada yeni_giris_ara'nin ag
    # hatasi cycle'i oldurunce ayni kapanis her cycle'da tekrar yazildi (VELVET 5x mukerrer kayit).
    _save_state(st)

    ef = efektif_equity(st)          # gerceklesmis + acik P&L; st["efektif_equity"]'e yazilir
    dusus_esik = float(_c("maks_dusus_pct", 25))
    if dusus_esik > 0 and st["durum"] == "AKTIF":
        zirve = max(float(st.get("zirve_equity") or st["baslangic_bakiye"]), ef)
        st["zirve_equity"] = round(zirve, 2)
        dusus = (ef / zirve - 1) * 100 if zirve else 0.0
        if dusus <= -dusus_esik:
            st["durum"] = "HALT_DUSUS"
            telegram_gonder(f"[TESTBOT] DUSUS FRENI: zirveden %{-dusus:.1f} geri cekildi "
                            f"(efektif ${ef:.2f} = gerceklesmis ${st['equity']:.2f} + acik "
                            f"${ef - st['equity']:+.2f}; esik %{dusus_esik:.0f}) — YENI GIRIS "
                            f"DURDU, acik pozlar yonetiliyor. 'python testbot.py --devam' ile ac.")

    if st["durum"] == "AKTIF":
        try:
            rejim = evren.btc_rejim()
            yeni_giris_ara(st, rejim)
        except Exception as e:
            print(f"[{now_iso()}] yeni_giris_ara hatasi (cycle devam, state korundu): {e}")

    st["son_cycle_ts"] = now_iso()
    _save_state(st)
    _append_jsonl(EQUITYF, {"ts": now_iso(), "equity": round(st["equity"], 2),
                            "acik_pnl": round((st.get("efektif_equity") or st["equity"]) - st["equity"], 2), "acik_sayisi": len(st["acik_pozisyonlar"]),
                            "durum": st["durum"]})
    print(f"[{now_iso()}] durum={st['durum']} equity=${st['equity']:.2f} acik={len(st['acik_pozisyonlar'])} "
          f"gun={gun_gecti:.1f}/{sure_gun}")

    # --- IKINCI HESAP ("ben") — 2026-08-05, kullanici karari -----------------
    # Kullanicinin panelden actigi SANAL pozisyonlar ayri kasada durur ama AYNI
    # kurallarla yonetilir (stop/TP1/iz-suren/zaman-stopu/fonlama) — boylece iki
    # sistem arasindaki fark yalnizca GIRIS KARARINDAN gelir, cikis kurallarindan degil.
    # Tembel import: benim.py yoksa veya coker ise BOT ETKILENMEZ (fail-safe).
    # Yeni giris ARAMAZ; girisler yalnizca panelden gelir (karar verici insan).
    try:
        import benim
        benim.tur()
    except Exception as e:
        print(f"[{now_iso()}] 'ben' hesabi turu atlandi (bot etkilenmedi): {e}")

    # --- GOLGE DEFTER — 2026-08-10, kullanici karari ------------------------
    # Botun REDDETTIGI girisler burada sanal olarak acildi; cikislari da BOTLA AYNI
    # kurallarla yonetilmeli ki fark yalnizca "kapi acti mi kapatti mi"dan gelsin.
    # Yeni giris ARAMAZ (girisler yalnizca yeni_giris_ara'daki red kancalarindan gelir).
    try:
        import golge
        golge.tur()
    except Exception as e:
        print(f"[{now_iso()}] golge turu atlandi (bot etkilenmedi): {e}")

    # --- AYNA DEFTERI — 2026-08-12, kullanici karari ------------------------
    # Botun ACTIGI girislerin BIREBIR kopyasi burada da acilir ve AYNI kurallarla
    # yonetilir; boylece kullanici dokunmadikca ayna botun aynisini yapar. Kullanici
    # panelden "kapatirdim" derse fark yalnizca O KARARDAN gelir (kontrol grubu bedava).
    # Yeni giris ARAMAZ (girisler yalnizca yeni_giris_ac icindeki _aynala kancasindan).
    try:
        import ayna
        ayna.tur()
    except Exception as e:
        print(f"[{now_iso()}] ayna turu atlandi (bot etkilenmedi): {e}")


# ---------- CLI yardımcıları ----------

def durum_yazdir():
    st = _load_state()
    if st is None:
        print("Bot henuz baslamadi (--cycle ile baslat)."); return
    print(f"=== TESTBOT DURUM ===")
    print(f"Durum: {st['durum']} | Baslangic: {st['baslangic_ts']} | Bakiye: ${st['baslangic_bakiye']:.0f} -> ${st['equity']:.2f}")
    acik_pnl = acik_pnl_toplam(st)
    print(f"Acik pozisyon: {len(st['acik_pozisyonlar'])} | Acik PnL (gerceklesmemis): {acik_pnl:+.2f}$")
    for p in st["acik_pozisyonlar"]:
        px = fiyat_fapi(p["sym"]) or p["giris"]
        yon_isaret = 1 if p["yon"] == "LONG" else -1
        pnl = (px - p["giris"]) * p["miktar"] * yon_isaret
        print(f"  {p['sym']:8} {p['yon']:5} {p['kaldirac']}x marjin=${p['marjin']:.2f} giris={p['giris']:.6g} "
              f"anlik={px:.6g} PnL={pnl:+.2f}$ stop={p['stop']:.6g} tp1={p['tp1']:.6g} liq={p['likidasyon']:.6g}")
    try:
        islemler = [json.loads(l) for l in open(ISLEMLERF, encoding="utf-8").read().splitlines() if l.strip()]
    except Exception:
        islemler = []
    if islemler:
        tam = [t for t in islemler if not t.get("kismi")]
        kismi = [t for t in islemler if t.get("kismi")]
        kazanan = [t for t in tam if t["sonuc_usdt"] > 0]
        rler = [t["r"] for t in tam if t.get("r") is not None]
        print(f"\nKapanan islem: {len(tam)} | Kazanan: {len(kazanan)} (%{len(kazanan)/len(tam)*100:.0f}) "
              f"| Toplam PnL (kismi dahil): {sum(t['sonuc_usdt'] for t in islemler):+.2f}$")
        if kismi:
            print(f"TP1 kismi realize: {sum(t['sonuc_usdt'] for t in kismi):+.2f}$ ({len(kismi)} adet)")
        # equity <-> islem-log mutabakati (2026-07-08, "equity + ama PnL -" karisikligi dersi):
        # funding/giris-ucreti acik pozisyonlarda equity'yi SESSIZCE degistirir, jsonl'e hic yazilmaz.
        kum_funding = st.get("kumulatif_funding", 0.0)
        kum_ucret = st.get("kumulatif_giris_ucret", 0.0)
        print(f"Funding (acik/kapanan poz., islem-log'unda YOK): {kum_funding:+.2f}$ | Giris ucretleri: {-kum_ucret:+.2f}$")
        print(f"Equity degisimi (gercek, hepsi dahil): {st['equity']-st['baslangic_bakiye']:+.2f}$"
              + (" (sayaclar 0'dan basladi, gecmis funding/ucret bu farka dahil DEGIL)"
                 if kum_funding == 0.0 and kum_ucret == 0.0 else ""))
        if rler:
            print(f"Ortalama R: {statistics.mean(rler):+.2f} | Toplam R: {sum(rler):+.2f}")
        # REJIM x YON kirilimi (2026-07-08, "hem-ayi-hem-boga" hedefi olcumu): hangi rejimde hangi
        # yon calisiyor? BILINMIYOR = rejim-etiketi eklenmeden ONCE acilan eski islemler.
        print("\n-- Rejim x Yon karnesi (hangi kosulda hangi yon?) --")
        rejimler = ["AYI", "NOTR", "BOGA", "BILINMIYOR"]
        for rj in rejimler:
            for yn in ("LONG", "SHORT"):
                grp = [t for t in tam if t.get("rejim_giriste", "BILINMIYOR") == rj and t["yon"] == yn]
                if grp:
                    kz = sum(1 for t in grp if t["sonuc_usdt"] > 0)
                    pnl = sum(t["sonuc_usdt"] for t in grp)
                    print(f"  {rj:10} {yn:5}: {len(grp)} islem, {kz}W (%{kz/len(grp)*100:.0f}), PnL={pnl:+.1f}$")
        print("  NOT: N kucukken (<25-30) kanit degil izlenimdir; gercek AYI verisi henuz yok (overfit'e dikkat).")
        for t in islemler[-10:]:
            print(f"  {t['ts']} {t['sym']:8} {t['yon']:5} {t['sebep']:10} PnL={t['sonuc_usdt']:+.2f}$ R={t.get('r')} [{t.get('rejim_giriste','?')}]")
    else:
        print("\nHenuz kapanan islem yok.")


def reset():
    # KILIT (2026-07-23 bug-fix, Madde 8): reset eskiden kilit ALMIYORDU -> reset aninda calisan bir
    # cycle eski state'i bellekte tutup reset'in ustune kaydediyordu (10k reset ezildi vakasi). Artik
    # reset de cycle kilidini alir; alamazsa (cycle calisyor) EZMEK yerine reddeder (kullanici retry/gorev-durdur).
    if not _kilit_al():
        print("REDDEDILDI: bir cycle su an calisiyor (kilit tutuluyor). Birkac saniye sonra tekrar dene "
              "VEYA once zamanlayici gorevini (KriptoTestBot) durdur, sonra reset yap.")
        return
    try:
        st = _load_state()
        if st and st["acik_pozisyonlar"]:
            print(f"UYARI: {len(st['acik_pozisyonlar'])} acik pozisyon var, reset onlari SILER (sanal — gercek para etkilenmez).")
        _save_state(yeni_state())
        print("Yeni test haftasi baslatildi (islem/equity gecmisi dosyalarda kalir, state sifirlandi).")
    finally:
        _kilit_birak()


def dur_devam(yeni_durum):
    st = _load_state()
    if st is None:
        print("Bot henuz baslamadi."); return
    # Dusus freninden donuluyorsa zirve SIFIRLANIR (2026-08-10). Yoksa fren kalici olurdu:
    # eski zirve duruyor -> bir sonraki cycle ayni dususu gorup yeniden HALT ederdi.
    # Bilincli: "gozden gecirdim, buradan devam" = yeni dusus penceresi baslasin.
    if yeni_durum == "AKTIF" and st.get("durum") == "HALT_DUSUS":
        st["zirve_equity"] = round(st["equity"], 2)
        print(f"Dusus freni sifirlandi: yeni zirve referansi ${st['equity']:.2f}")
    st["durum"] = yeni_durum
    _save_state(st)
    print(f"Durum -> {yeni_durum}")


def zorla_giris(spec):
    sym, yon = spec.upper().split(":")
    yon = "LONG" if yon.upper().startswith("L") else "SHORT"
    st = _load_state() or yeni_state()
    r = radar.analyze(sym)
    if not r:
        print("analyze basarisiz (sembol/veri sorunu)"); return
    pillar = radar.pillar_d(sym)
    rejim_ad = evren.btc_rejim().get("rejim")
    ok = yeni_giris_ac(st, sym, yon, r, pillar, "ZORLA (debug)", zorla=True, rejim_ad=rejim_ad)
    _save_state(st)
    print(f"zorla giris: {'basarili' if ok else 'reddedildi (VETO_rr_net veya kaldirac guvenlik)'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", action="store_true")
    ap.add_argument("--durum", action="store_true")
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--dur", action="store_true")
    ap.add_argument("--devam", action="store_true")
    ap.add_argument("--zorla", default=None, help="orn. SOL:long (debug)")
    a = ap.parse_args()
    if a.durum:
        durum_yazdir()
    elif a.reset:
        reset()
    elif a.dur:
        dur_devam("DURAKLATILDI")
    elif a.devam:
        dur_devam("AKTIF")
    elif a.zorla:
        zorla_giris(a.zorla)
    else:
        cycle()
