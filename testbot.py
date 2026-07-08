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
from nobetci import telegram_gonder, toast_gonder

HERE = os.path.dirname(os.path.abspath(__file__))
FAPI = "https://fapi.binance.com"
STATEF = os.path.join(HERE, "testbot_state.json")
ISLEMLERF = os.path.join(HERE, "testbot_islemler.jsonl")
EQUITYF = os.path.join(HERE, "testbot_equity.jsonl")
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
    json.dump(st, open(STATEF, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def _append_jsonl(path, obj):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


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
        return [{"t": int(k[0]), "h": float(k[2]), "l": float(k[3]), "c": float(k[4])} for k in d]
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


def karar_yon(rejim_ad, r, pillar, kucuk_float_esik_gecerli):
    """r: radar.analyze() ciktisi. pillar: radar.pillar_d() ciktisi (top_ls/glob_ls/taker/smart).
    Donus: None | ("LONG"|"SHORT", "ANINDA"|"ONAY_BEKLE", sebep)"""
    skor = r["score"]
    smart = pillar.get("smart")
    taker = pillar.get("taker")
    dusuk_float = kucuk_float_esik_gecerli
    esik_short = evren.esik("radar_short_skor", 45.0)
    esik_uzun = evren.esik("radar_alert_skor", 40.0) + 5  # LONG icin biraz daha siki temel esik

    # ortak guvenlik: dusuk-float + dip_yakit = yapisal neg-funding, dusen bicak (RE/FOGO)
    short_riskli_dip = bool(r.get("dip_yakit") and dusuk_float)

    # BLOW-OFF filtresi (2026-07-03 TLM -%60 stop sonrasi eklendi — MANTA dersinin ihlali).
    # TLM: 48s'te +%126 pump'in ICINDEYKEN "BASLIYOR+smart-LONG+taker-alim" (AYI-istisnasi) tetiklendi,
    # 36dk'da stop oldu. "BASLIYOR" sadece SON 1-3s ivmeye bakiyor, coinin zaten NE KADAR uzadigina bakmiyordu.
    # MANTA dersi: pump'in GEC safhasinda OI/smart-long gorunumu = tuzak (tepe/likidasyon riski), LONG teyidi DEGIL.
    chg24 = r.get("chg24", 0.0) or 0.0
    blowoff_esik = evren.esik("blowoff_chg24_pct", 40.0)
    asiri_yukselmis = chg24 >= blowoff_esik
    asiri_dusmus = chg24 <= -blowoff_esik

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
    )

    if rejim_ad == "AYI":
        if r["stage"] == "BASLIYOR" and smart == "LONG" and (taker or 0) >= 1.0:
            if asiri_yukselmis:
                return ("SHORT", "ONAY_BEKLE",
                        f"BLOW-OFF TUZAGI (24s {chg24:+.0f}%, MANTA deseni): smart-long+BASLIYOR = pump'in GEC "
                        f"safhasi, LONG DEGIL -> SHORT-tepki adayi, tepe/donus onayi bekle")
            if long_veto:
                return None  # dip-bicak/kapitulasyon/fiyat-dusuk-OI-artis -> AAVE istisnasi bile gecersiz
            return ("LONG", "ANINDA", "AYI-istisna: BASLIYOR+smart-LONG+taker-alim (AAVE deseni)")
        if skor >= esik_short and smart != "LONG" and not short_riskli_dip and r.get("pos", 0.5) >= 0.20:
            if asiri_dusmus and r.get("pos", 0.5) < 0.30:
                return None  # zaten cok dusmus + dipte -> dusen bicagi kovalama, SHORT girme (ders#4)
            return ("SHORT", "ONAY_BEKLE", f"AYI: skor={skor} short-aday, 1-cycle onay bekletme")
        return None
    if rejim_ad == "BOGA":
        if r["stage"] == "BASLIYOR" and smart == "SHORT" and (taker or 1) <= 1.0:
            if asiri_dusmus:
                return ("LONG", "ONAY_BEKLE",
                        f"KAPITULASYON TUZAGI (24s {chg24:+.0f}%): smart-short+BASLIYOR = dususun GEC safhasi, "
                        f"SHORT DEGIL -> LONG-tepki adayi, dip/donus onayi bekle")
            return ("SHORT", "ANINDA", "BOGA-istisna: BASLIYOR+smart-SHORT+taker-satis")
        if skor >= esik_short and smart != "SHORT" and r.get("pos", 0.5) <= 0.85:
            if asiri_yukselmis and r.get("pos", 0.5) > 0.70:
                return None  # zaten cok yukselmis + tepede -> kovalama, LONG girme
            if long_veto:
                return None  # BOGA'da da bicak dibine LONG acilmaz
            return ("LONG", "ONAY_BEKLE", f"BOGA: skor={skor} long-aday, 1-cycle onay bekletme")
        return None
    # NOTR: temkinli — sadece stage aktif + smart hizali
    if r["stage"] in ("BASLIYOR", "HAZIRLANIYOR") and skor >= esik_uzun:
        # taker>=1.0 sarti (2026-07-06): smart etiketi tek basina 3/3 kaybetti (RE/O/SLX);
        # AYI-istisnasiyla (AAVE deseni) ayni agresif-alici teyidi burada da aranir.
        if smart == "LONG" and not asiri_yukselmis and not long_veto and (taker or 0) >= 1.0:
            return ("LONG", "ANINDA", "NOTR: stage-aktif+smart-LONG+taker-alim")
        if smart == "SHORT" and not short_riskli_dip and not asiri_dusmus:
            return ("SHORT", "ANINDA", "NOTR: stage-aktif+smart-SHORT")
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
    }
    _append_jsonl(ISLEMLERF, kayit)
    st["cooldown"][pos["sym"]] = now_iso()
    msg = f"[TESTBOT] KAPANDI {pos['sym']} {pos['yon']} {sebep} PnL={pnl_net:+.2f}$ (R={kayit['r']})"
    telegram_gonder(msg)
    toast_gonder("TestBot kapandi", f"{pos['sym']} {pos['yon']} {sebep} {pnl_net:+.2f}$")
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
    }
    _append_jsonl(ISLEMLERF, kayit)
    st["cooldown"][pos["sym"]] = now_iso()
    msg = f"[TESTBOT] LIKIDASYON {pos['sym']} {pos['yon']} marjin kaybi ${pos['marjin']:.2f}"
    telegram_gonder(msg)
    toast_gonder("TestBot LIKIDASYON", f"{pos['sym']} {pos['yon']} -${pos['marjin']:.2f}")
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
    }
    _append_jsonl(ISLEMLERF, kayit)
    telegram_gonder(f"[TESTBOT] TP1 {pos['sym']} {pos['yon']} yari kapatildi PnL={pnl_net:+.2f}$ (stop girise cekildi)")


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
        bars = olcucu.fetch_klines(sym, "1h", 100)
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
                    if b["l"] <= pos["likidasyon"]:
                        pozisyon_liq(st, pos); kapandi = True; break
                    if b["l"] <= pos["stop"]:
                        pozisyon_kapat(st, pos, pos["stop"], "STOP"); kapandi = True; break
                    if not pos["tp1_alindi"] and b["h"] >= pos["tp1"]:
                        pozisyon_kismi_tp1(st, pos, pos["tp1"])
                    if pos["tp1_alindi"] and b["h"] >= pos["tp2"]:
                        pozisyon_kapat(st, pos, pos["tp2"], "TP2"); kapandi = True; break
                else:  # SHORT
                    if b["h"] >= pos["likidasyon"]:
                        pozisyon_liq(st, pos); kapandi = True; break
                    if b["h"] >= pos["stop"]:
                        pozisyon_kapat(st, pos, pos["stop"], "STOP"); kapandi = True; break
                    if not pos["tp1_alindi"] and b["l"] <= pos["tp1"]:
                        pozisyon_kismi_tp1(st, pos, pos["tp1"])
                    if pos["tp1_alindi"] and b["l"] <= pos["tp2"]:
                        pozisyon_kapat(st, pos, pos["tp2"], "TP2"); kapandi = True; break
            if kapandi:
                continue
            pos["son_1m_kontrol_ts"] = now_iso()
            funding_uygula(st, pos)
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


def yeni_giris_ac(st, sym, yon, r, pillar, sebep, zorla=False):
    skor = r["score"]
    smart_hiz = smart_hizali_mi(yon, pillar.get("smart"))
    kaldirac0 = kaldirac_hesapla(skor, smart_hiz)
    try:
        olc = olcucu.measure(sym, yon.lower(), "1h", 100, spot=False)
    except Exception:
        return False
    if olc.get("VETO_rr_net") and not zorla:
        return False  # edge kanitlanmamis giris -> mekanik veto (Olcucu ile ayni disiplin)
    giris_piyasa, stop, tp1_yapisal, tp2 = olc["giris"], olc["stop"], olc["tp1"], olc["tp2"]
    kaldirac = kaldirac_guvenlik_kirp(giris_piyasa, stop, yon, kaldirac0)
    if kaldirac is None:
        kaldirac = 2 if zorla else None
        if kaldirac is None:
            return False  # stop cok genis -> hicbir kaldiracta guvenli degil
    if not smart_hiz and pillar.get("smart") not in (None, "NOTR"):
        marjin_pct = marjin_pct_hesapla(skor) / 2  # smart karsi yonde -> boyut yarı
    else:
        marjin_pct = marjin_pct_hesapla(skor)
    marjin = st["equity"] * marjin_pct
    cst = _maliyet()
    giris_ef = maliyet_uygula_giris(giris_piyasa, yon, cst)
    notional = marjin * kaldirac
    miktar = notional / giris_ef
    risk_usdt = abs(giris_ef - stop) / giris_ef * notional
    maks_risk = st["equity"] * float(_c("islem_risk_pct", 5)) / 100.0
    if risk_usdt > maks_risk and risk_usdt > 0:
        kucult = maks_risk / risk_usdt
        marjin *= kucult; notional *= kucult; miktar *= kucult; risk_usdt = maks_risk
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
        "son_funding_kontrol_ts": now_iso(), "son_1m_kontrol_ts": now_iso(), "sebep_giris": sebep,
        # trailing stop icin (2026-07-03, "piyasa donunce de TP/SL bekliyor" geri bildirimi):
        "stop_orijinal": round(stop, 6), "atr_giriste": olc.get("atr14"),
        "en_iyi_fiyat": giris_ef, "trailing_aktif": False,
    }
    st["sonraki_id"] += 1
    st["acik_pozisyonlar"].append(pos)
    telegram_gonder(f"[TESTBOT] GIRIS {sym} {yon} {kaldirac}x marjin=${marjin:.2f} "
                     f"giris={giris_ef:.6g} stop={stop:.6g} tp1={tp1:.6g} skor={skor} — {sebep}")
    toast_gonder("TestBot GIRIS", f"{sym} {yon} {kaldirac}x skor={skor}")
    return True


def yeni_giris_ara(st, rejim):
    maks_poz = int(_c("maks_pozisyon", 4))
    if len(st["acik_pozisyonlar"]) >= maks_poz:
        return
    min_vol = float(_c("min_vol_musd", 15))
    pool = evren.binance_pool("fapi", min_vol, None)[:40]
    chg24_harita = {s: chg for s, _, chg in pool}  # 24s % degisim -> blow-off filtresi icin (karar_yon)
    syms = _cikar_havuzdan([s for s, _, _ in pool], st, cooldown_saat=4)
    if not syms:
        return
    btc_chg3, _ = radar.btc_ref()
    cryptos_cache = None
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
    aday_rows.sort(key=lambda x: -x["score"])
    aday_rows = aday_rows[:10]  # Pillar D sadece kisa listeye (API bütçesi)

    bekleyenler = st.setdefault("bekleyenler", {})
    for sym in list(bekleyenler.keys()):
        if sym not in {r["sym"] for r in aday_rows}:
            bekleyenler[sym]["cycle_sayaci"] = bekleyenler[sym].get("cycle_sayaci", 0) + 1
            if bekleyenler[sym]["cycle_sayaci"] > 6:  # ~30dk gecti, aday soguladi -> iptal
                del bekleyenler[sym]

    for r in aday_rows:
        if len(st["acik_pozisyonlar"]) >= maks_poz:
            break
        sym = r["sym"]
        try:
            pillar = radar.pillar_d(sym)
        except Exception:
            pillar = {"top_ls": None, "glob_ls": None, "taker": None, "smart": None}

        dusuk_float = False
        if r.get("dip_yakit"):
            if cryptos_cache is None:
                cryptos_cache = evren.cg_universe()
            fo = (cryptos_cache.get(sym) or {}).get("float_oran")
            esik_fo = evren.esik("dusuk_float_oran", 0.25)
            dusuk_float = bool(fo is not None and fo < esik_fo)

        karar = karar_yon(rejim.get("rejim"), r, pillar, dusuk_float)
        if not karar:
            bekleyenler.pop(sym, None)
            continue
        yon, mod, sebep = karar

        if mod == "ANINDA":
            bekleyenler.pop(sym, None)
            yeni_giris_ac(st, sym, yon, r, pillar, sebep)
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
                yeni_giris_ac(st, sym, yon, r, pillar, sebep + " (onaylandi)")
        else:
            bekleyenler[sym] = {"yon": yon, "skor": r["score"], "ilk_gorulme_ts": now_iso(), "cycle_sayaci": 0}


# ---------- ana döngü ----------

def acik_pnl_toplam(st):
    toplam = 0.0
    for pos in st["acik_pozisyonlar"]:
        px = fiyat_fapi(pos["sym"])
        if px is None:
            continue
        yon_isaret = 1 if pos["yon"] == "LONG" else -1
        toplam += (px - pos["giris"]) * pos["miktar"] * yon_isaret
    return toplam


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

    if st["durum"] == "AKTIF" and gun_gecti >= sure_gun:
        st["durum"] = "SURE_DOLDU"
        telegram_gonder(f"[TESTBOT] SURE DOLDU ({sure_gun} gun) — yeni giris YOK, acik pozisyonlar dogal kapanisini bekliyor")
    if st["durum"] == "AKTIF" and st["equity"] <= min_equity:
        st["durum"] = "HALT_BAKIYE"
        telegram_gonder(f"[TESTBOT] BAKIYE BITTI (${st['equity']:.2f}) — islem DURDU")

    yonet_acik_pozisyonlar(st)

    if st["durum"] == "AKTIF":
        rejim = evren.btc_rejim()
        yeni_giris_ara(st, rejim)

    st["son_cycle_ts"] = now_iso()
    _save_state(st)
    _append_jsonl(EQUITYF, {"ts": now_iso(), "equity": round(st["equity"], 2),
                            "acik_pnl": round(acik_pnl_toplam(st), 2), "acik_sayisi": len(st["acik_pozisyonlar"]),
                            "durum": st["durum"]})
    print(f"[{now_iso()}] durum={st['durum']} equity=${st['equity']:.2f} acik={len(st['acik_pozisyonlar'])} "
          f"gun={gun_gecti:.1f}/{sure_gun}")


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
        for t in islemler[-10:]:
            print(f"  {t['ts']} {t['sym']:8} {t['yon']:5} {t['sebep']:10} PnL={t['sonuc_usdt']:+.2f}$ R={t.get('r')}")
    else:
        print("\nHenuz kapanan islem yok.")


def reset():
    st = _load_state()
    if st and st["acik_pozisyonlar"]:
        print(f"UYARI: {len(st['acik_pozisyonlar'])} acik pozisyon var, reset onlari SILER (sanal — gercek para etkilenmez).");
    _save_state(yeni_state())
    print("Yeni test haftasi baslatildi (islem/equity gecmisi dosyalarda kalir, state sifirlandi).")


def dur_devam(yeni_durum):
    st = _load_state()
    if st is None:
        print("Bot henuz baslamadi."); return
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
    ok = yeni_giris_ac(st, sym, yon, r, pillar, "ZORLA (debug)", zorla=True)
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
