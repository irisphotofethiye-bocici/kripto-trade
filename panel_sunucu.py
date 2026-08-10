#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PANEL SUNUCU — tam kontrol paneli. Sadece 127.0.0.1:8787 (dışarıya açık DEĞİL).

OKUMA
  GET /              -> panel.html
  GET /api/durum     -> equity, açık pozisyonlar (canlı fiyat+PnL), işlemler, karne
  GET /api/sistem    -> veto özeti, gerçek pozisyonlar, erken kuşak, sayaç, para akışı
  GET /api/mumlar    -> ?sym=SOL&interval=15m&limit=200 (Binance klines proxy)
  GET /api/ozet      -> düz Türkçe anlatı + madde listesi (kural tabanlı)      [2026-08-05]
  GET /api/kafa      -> botun kafası: aday arşivi, veto kırılımı, bekleyenler  [2026-08-05]
  GET /api/gecmis    -> drawdown, kırılımlar, R dağılımı, tur karşılaştırma    [2026-08-05]
  GET /api/piyasa    -> F10 rejim, para rejimi, BTC payı serisi, makro takvim  [2026-08-05]
  GET /api/defter    -> gerçek portföy: spot, tahminler, dersler, izleme       [2026-08-05]
  GET /api/gunluk    -> fikir-defteri.md zaman çizelgesi (salt okur)           [2026-08-05]
  GET /api/ayarlar   -> BEYAZ LİSTELİ ayarlar + panel işlem izi               [2026-08-05]

YAZMA (2026-08-05, kullanıcı kararı)
  POST /api/kontrol  -> {eylem: bot_durdur|bot_devam|bildirim_ac|bildirim_kapa|pozisyon_kapat}
  POST /api/ayar     -> {anahtar: "esikler.x", deger: n}  — AYAR_BEYAZ dışı REDDEDİLİR

GÜVENLİK: kripto-config.json gerçek API anahtarları ve Telegram token'ı içeriyor.
Bu dosya asla ham servis edilmez; yalnız AYAR_BEYAZ'daki anahtarlar okunur/yazılır.
Durum yazan her eylem testbot._kilit_al() ile kilit alır (bot ayrı süreçte --cycle koşuyor).
Panelden yapılan her değişiklik panel_islem_log.jsonl'e yazılır.

Bağımlılık yok (stdlib http.server). Kullanım: python panel_sunucu.py [--port 8787]
"""
import json, os, sys, time, argparse, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import testbot
import evren

HERE = os.path.dirname(os.path.abspath(__file__))
FAPI = "https://fapi.binance.com"

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")

_mumlar_cache = {}  # (sym,interval,limit) -> (ts, data) — hizli ardisik grafik tiklamalarini yutar


def _rejim_yon_karne(tam):
    """Rejim x yon kirilimi (2026-07-08): AYI/NOTR/BOGA/BILINMIYOR her biri icin LONG/SHORT
    islem/kazanan/PnL. 'hem-ayi-hem-boga' hedefine ne kadar yakiniz sorusunun olcum tablosu."""
    out = {}
    for rj in ("AYI", "NOTR", "BOGA", "BILINMIYOR"):
        for yn in ("LONG", "SHORT"):
            grp = [t for t in tam if t.get("rejim_giriste", "BILINMIYOR") == rj and t["yon"] == yn]
            if grp:
                kz = sum(1 for t in grp if t["sonuc_usdt"] > 0)
                out[f"{rj}_{yn}"] = {"n": len(grp), "kazanan": kz,
                                     "pnl": round(sum(t["sonuc_usdt"] for t in grp), 2)}
    return out


def _durum_json():
    st = testbot._load_state()
    if st is None:
        return {"basladi": False}
    acik = []
    for p in st["acik_pozisyonlar"]:
        px = testbot.fiyat_fapi(p["sym"]) or p["giris"]
        yon_isaret = 1 if p["yon"] == "LONG" else -1
        pnl = (px - p["giris"]) * p["miktar"] * yon_isaret
        notional = p["miktar"] * p["giris"]
        acik.append({**p, "anlik_fiyat": px, "acik_pnl": round(pnl, 2), "notional": round(notional, 2)})
    kullanilan_marjin = round(sum(p["marjin"] for p in acik), 2)
    try:
        islemler = [json.loads(l) for l in open(testbot.ISLEMLERF, encoding="utf-8").read().splitlines() if l.strip()]
    except Exception:
        islemler = []
    try:
        equity_serisi = [json.loads(l) for l in open(testbot.EQUITYF, encoding="utf-8").read().splitlines() if l.strip()]
    except Exception:
        equity_serisi = []
    tam = [t for t in islemler if not t.get("kismi")]  # TP1_KISMI satirlari islem SAYILMAZ, PnL'e dahil
    kazanan = [t for t in tam if t["sonuc_usdt"] > 0]
    rler = [t["r"] for t in tam if t.get("r") is not None]
    return {
        "basladi": True, "durum": st["durum"], "baslangic_ts": st["baslangic_ts"],
        "baslangic_bakiye": st["baslangic_bakiye"], "equity": round(st["equity"], 2),
        "acik_pnl_toplam": round(sum(a["acik_pnl"] for a in acik), 2),
        "kullanilan_marjin": kullanilan_marjin,
        "serbest_bakiye": round(st["equity"] - kullanilan_marjin, 2),
        "toplam_notional": round(sum(a["notional"] for a in acik), 2),
        "acik_pozisyonlar": acik, "son_islemler": islemler[-200:],
        "equity_serisi": equity_serisi[-2000:],
        "karne": {
            "toplam_islem": len(tam), "kazanan": len(kazanan),
            "win_rate": round(len(kazanan) / len(tam) * 100, 1) if tam else None,
            "toplam_pnl": round(sum(t["sonuc_usdt"] for t in islemler), 2),
            "tp1_kismi_pnl": round(sum(t["sonuc_usdt"] for t in islemler if t.get("kismi")), 2),
            "ort_r": round(sum(rler) / len(rler), 2) if rler else None,
            # funding/giris-ucreti acik pozisyonlarda equity'yi degistirir ama islem-log'a hic yazilmaz
            # (2026-07-08, "equity+ ama PnL-" karisikligi dersi) -> ayri sayaclarla goruniyor.
            "kumulatif_funding": round(st.get("kumulatif_funding", 0.0), 2),
            "kumulatif_giris_ucret": round(st.get("kumulatif_giris_ucret", 0.0), 2),
            # rejim x yon kirilimi (2026-07-08, "hem-ayi-hem-boga" hedefi olcumu)
            "rejim_yon": _rejim_yon_karne(tam),
        },
    }


_sistem_cache = None  # (ts, data) — /api/sistem 60s TTL (veriler yavas degisir)

# 2026-08-05: btc_pay_freni EKLENDI. Eksikti -> bu kategori sayacta sessizce gorunmuyordu.
VETO_KATEGORILER = ("long_veto", "taker_soguma", "blowoff", "rr_veto", "btc_pay_freni")


def _veto_ozet(son_n=15):
    """veto_log.jsonl -> kategori sayaclari + son N kayit. Dosya yoksa bos (gitignore'da)."""
    sayac = {k: 0 for k in VETO_KATEGORILER}
    kayitlar = []
    try:
        for line in open(os.path.join(HERE, "veto_log.jsonl"), encoding="utf-8"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            k = d.get("kategori")
            if k in sayac:
                sayac[k] += 1
            kayitlar.append({a: d.get(a) for a in
                             ("ts", "sym", "price", "kategori", "detay", "olurdu_yon", "rejim", "skor")})
    except Exception:
        pass
    return {"sayac": sayac, "toplam": sum(sayac.values()), "son": kayitlar[-son_n:][::-1]}


def _gercek_pozlar():
    """kripto_portfoy.json aktif_futures -> canli fiyat + PnL% + stopa uzaklik. Panel'in gercek defteri."""
    out = []
    try:
        pf = json.load(open(os.path.join(HERE, "kripto_portfoy.json"), encoding="utf-8"))
        for p in pf.get("aktif_futures", []):
            if p.get("durum") != "acik":
                continue
            sym, giris, stop = p["sembol"], float(p["giris"]), float(p.get("stop") or 0)
            isaret = 1 if p.get("yon") == "LONG" else -1
            px = testbot.fiyat_fapi(sym)
            pnl_pct = pnl_usdt = stop_uzaklik = None
            if px:
                pnl_pct = round((px - giris) / giris * 100 * isaret, 2)
                pnl_usdt = round((px - giris) / giris * float(p.get("notional_usdt") or 0) * isaret, 2)
                if stop:
                    stop_uzaklik = round((px - stop) / px * 100 * isaret, 2)  # +% = stopa mesafe var
            out.append({"sym": sym, "yon": p.get("yon"), "giris": giris, "stop": stop,
                        "tp1": p.get("tp1"), "kaldirac": p.get("kaldirac"), "tarih": p.get("tarih"),
                        "marjin": p.get("marjin_usdt"), "risk_usdt": p.get("risk_usdt"),
                        "anlik": px, "pnl_pct": pnl_pct, "pnl_usdt": pnl_usdt,
                        "stop_uzaklik_pct": stop_uzaklik})
    except Exception:
        pass
    return out


def _erken_kusak(top_n=10):
    """radar_active.json erken_kusak -> skora gore ilk N (KAPI DEGIL, gozlem katmani)."""
    try:
        ra = json.load(open(os.path.join(HERE, "radar_active.json"), encoding="utf-8"))
        ek = sorted(ra.get("erken_kusak") or [], key=lambda s: -(s.get("score") or 0))
        return [{a: s.get(a) for a in ("sym", "score", "vol_x_gun", "chg24", "price", "taker", "smart", "stage")}
                for s in ek[:top_n]]
    except Exception:
        return []


def _sayac(st):
    """Test bitisine geri sayim + K1 equity on-izleme (SADECE gosterim — karar 21 Tem'de,
    kapanan-R ve rejim-hucre kriterleriyle BIRLIKTE; test-degerlendirme-programi.md K1)."""
    try:
        bas = time.mktime(time.strptime(st["baslangic_ts"], "%Y-%m-%d %H:%M:%S"))
        sure_gun = float(testbot._c("sure_gun", 7))
        bitis = bas + sure_gun * 86400
        kalan_sn = max(0, bitis - time.time())
        return {"bitis_ts": time.strftime("%Y-%m-%d %H:%M", time.localtime(bitis)),
                "kalan_gun": round(kalan_sn / 86400, 1), "sure_gun": sure_gun,
                "equity": round(st["equity"], 2), "baslangic_bakiye": st["baslangic_bakiye"],
                "k1_equity_ok": st["equity"] > st["baslangic_bakiye"]}
    except Exception:
        return None


def _para_akisi(geri=14):
    """TOTAL2/3 para-akisi gostergesi (2026-07-22, kullanici: 'baslibasina indikator, kapi degil').
    piyasa_yapisi_log'dan turetilir (total/btc_d/eth_d zaten var). Kripto+altlara para giriyor mu,
    BTC'ye mi kaciyor? Bota KAPI DEGIL — CEO/insan icin baglam + boga-donus erken teyidi."""
    try:
        lines = [json.loads(l) for l in open(os.path.join(HERE, "piyasa_yapisi_log.jsonl"),
                                             encoding="utf-8").read().splitlines() if l.strip()]
    except Exception:
        return None
    if len(lines) < 2:
        return None
    def t2(d): return d["total"] * (1 - d["btc_d"] / 100)
    def t3(d): return d["total"] * (1 - d["btc_d"] / 100 - d.get("eth_d", 0) / 100)
    def brd(d): return next((v for k, v in d.items() if k.startswith("breadth")), None)
    son = lines[-1]
    ilk = lines[-geri] if len(lines) >= geri else lines[0]
    def yuzde(a, b): return round((a - b) / b * 100, 1) if b else 0.0
    total_chg = yuzde(son["total"], ilk["total"])
    t2_chg = yuzde(t2(son), t2(ilk))
    t3_chg = yuzde(t3(son), t3(ilk))
    btcd_chg = round(son["btc_d"] - ilk["btc_d"], 2)
    breadth = brd(son)
    btcd = son["btc_d"]
    usdtd = son.get("usdt_d", 0)
    usdtd_chg = round(usdtd - ilk.get("usdt_d", usdtd), 2)  # dususu = para kenardan GIRIYOR
    # ALT-BOGA tetigi (kullanici tezi 2026-07-22): BTC.D 55 altina kirilim ASIL sinyal.
    # AMA tek basina yetmez -> BTC saglikli (SEZON!=AYI) olmali; yoksa BTC.D dususu risk-off
    # cokusu de olabilir (alt-katliam, boga degil). SEZON F10'dan (btc_rejim.sezon).
    try:
        sezon = evren.btc_rejim().get("sezon")
    except Exception:
        sezon = None
    alt_boga = (btcd < 55.0 and t3_chg > 0 and (breadth or 0) >= 50 and sezon != "AYI")
    # boga-donus erken teyidi (hipotez#3): TOTAL3 yukari + BTC.D asagi + USDT.D asagi (para
    # kenardan giriyor) + breadth>=50. USDT.D dususu = stablecoin'den coin'e aktif alim.
    donus_teyit = (t3_chg > 0 and btcd_chg < 0 and usdtd_chg < 0 and (breadth or 0) >= 50)
    # PARA-REJIM sentezi (2026-07-23): total-trendi × rotasyon -> tek etiket. Etiket mantigi
    # evren.para_rejim_etiket'te (testbot para-kapisi ile ORTAK kaynak; drift olmasin). Panelde
    # gosterge; testbot'ta 'PARA CIKIYOR' long-veto (kullanici karari 2026-07-23).
    para_rejim, para_rejim_not = evren.para_rejim_etiket(total_chg, btcd_chg, t3_chg)
    return {"ts": son.get("ts"), "total_t": round(son["total"] / 1e12, 3),
            "para_rejim": para_rejim, "para_rejim_not": para_rejim_not,
            "total_chg": total_chg, "total2_chg": t2_chg, "total3_chg": t3_chg,
            "btcd": round(btcd, 1), "btcd_chg": btcd_chg, "btcd_55_uzaklik": round(btcd - 55, 1),
            "usdtd": round(usdtd, 2), "usdtd_chg": usdtd_chg,
            "breadth": breadth, "sezon": sezon,
            "alt_yon": "GIRIYOR" if t3_chg > 0 else "CIKIYOR",
            "btc_yon": "BTC'ye kaciyor" if btcd_chg > 0 else "BTC'den altlara",
            "usdt_yon": "para KENARDAN giriyor" if usdtd_chg < 0 else ("para KENARA kaciyor" if usdtd_chg > 0 else "durgun"),
            "donus_teyit": donus_teyit, "alt_boga": alt_boga, "gun": geri // 2}


def _sistem_json(ttl=60.0):
    global _sistem_cache
    now = time.time()
    if _sistem_cache and now - _sistem_cache[0] < ttl:
        return _sistem_cache[1]
    st = testbot._load_state()
    out = {"veto": _veto_ozet(), "gercek_pozisyonlar": _gercek_pozlar(),
           "erken_kusak": _erken_kusak(), "sayac": _sayac(st) if st else None,
           "para_akisi": _para_akisi()}
    _sistem_cache = (now, out)
    return out


def _mumlar(sym, interval, limit, ttl=30.0):
    key = (sym.upper(), interval, limit)
    now = time.time()
    hit = _mumlar_cache.get(key)
    if hit and now - hit[0] < ttl:
        return hit[1]
    try:
        url = f"{FAPI}/fapi/v1/klines?symbol={sym.upper()}USDT&interval={interval}&limit={limit}"
        d = evren.get(url, headers={"User-Agent": "panel/1.0"}, timeout=15)
        out = [{"time": int(k[0]) // 1000, "open": float(k[1]), "high": float(k[2]),
                "low": float(k[3]), "close": float(k[4])} for k in d]
        _mumlar_cache[key] = (now, out)
        return out
    except Exception as e:
        return {"error": str(e)}


# ===========================================================================
# 2026-08-05 — TAM KONTROL PANELI KATMANI
# Tasarim notu: buradaki her sey SALT OKUR (yazma yalnizca /api/kontrol ve
# /api/ayar'da, beyaz liste + kilit + iz kaydi ile). Buyuk dosyalar (ozellikle
# radar_archive.jsonl ~52 MB) ASLA tam okunmaz -> _tail_jsonl kullanilir.
# ===========================================================================

ISLEM_LOGF = os.path.join(HERE, "panel_islem_log.jsonl")
_cache = {}   # ad -> (ts, veri)


def _tut(ad, ttl, uret):
    """Basit TTL onbellek — mevcut _sistem_cache kalibinin genellestirilmis hali."""
    now = time.time()
    hit = _cache.get(ad)
    if hit and now - hit[0] < ttl:
        return hit[1]
    veri = uret()
    _cache[ad] = (now, veri)
    return veri


def _tail_jsonl(path, n=500, maks_bayt=6_000_000):
    """Dosyanin SONUNDAN geriye en fazla n satir okur.
    radar_archive.jsonl 52 MB — tam okuma paneli kilitler, bu yuzden yasak."""
    try:
        boyut = os.path.getsize(path)
    except Exception:
        return []
    parca = min(boyut, maks_bayt)
    try:
        with open(path, "rb") as f:
            f.seek(boyut - parca)
            ham = f.read(parca)
    except Exception:
        return []
    satirlar = ham.split(b"\n")
    if parca < boyut and satirlar:
        satirlar = satirlar[1:]          # ilk satir yarim kalmis olabilir, at
    out = []
    for s in satirlar[-n:]:
        s = s.strip()
        if not s:
            continue
        try:
            out.append(json.loads(s.decode("utf-8")))
        except Exception:
            pass
    return out


def _oku_json(ad, varsayilan=None):
    try:
        return json.load(open(os.path.join(HERE, ad), encoding="utf-8"))
    except Exception:
        return varsayilan


def _ticker_haritasi():
    """TEK cagriyla tum perp ticker'lari (fiyat, 24s degisim, hacim, 24s yuksek/dusuk)."""
    def uret():
        h = {}
        try:
            for t in evren.raw_tickers("fapi") or []:
                s = t.get("symbol", "")
                if s.endswith("USDT"):
                    h[s[:-4]] = t
        except Exception:
            pass
        return h
    return _tut("tickerlar", 30.0, uret)


def _fiyat_haritasi():
    """TEK cagriyla tum semboller (21 spot pozisyon icin 21 ayri istek atmamak icin)."""
    def uret():
        h = {}
        for kaynak in ("fapi", "spot"):
            try:
                for t in evren.raw_tickers(kaynak) or []:
                    s = t.get("symbol", "")
                    if s.endswith("USDT"):
                        h.setdefault(s[:-4], float(t["lastPrice"]))
            except Exception:
                pass
        return h
    return _tut("fiyatlar", 30.0, uret)


# ---------------------------------------------------------------------------
# AYAR BEYAZ LISTESI — panelden degistirilebilecek TEK sey bu liste.
# kripto-config.json gercek API anahtarlari ve Telegram token'i iceriyor;
# bu dosya ASLA ham servis edilmez, yalnizca asagidaki anahtarlar okunur/yazilir.
# ---------------------------------------------------------------------------
AYAR_BEYAZ = {
    "testbot.islem_risk_pct": dict(ad="İşlem başına risk (%)", min=0.5, max=10, tip="sayi",
        aciklama="Her işlemde göze alınan para, bakiyenin yüzdesi olarak. Stop yenirse kaybedilecek tutar bu."),
    "testbot.maks_pozisyon": dict(ad="Aynı anda en fazla pozisyon", min=1, max=10, tip="sayi",
        aciklama="Bot aynı anda kaç işlem açık tutabilir."),
    "testbot.zaman_stop_saat": dict(ad="Zaman stopu (saat)", min=6, max=240, tip="sayi",
        aciklama="Bu kadar saat geçtiğinde hâlâ bir yere gitmeyen pozisyon kapatılır."),
    "testbot.kaldirac_max": dict(ad="En yüksek kaldıraç", min=2, max=20, tip="sayi",
        aciklama="Kaldıraç bir girdi değil sonuç; bu sadece tavanı."),
    "esikler.radar_short_skor": dict(ad="Short için skor eşiği", min=20, max=90, tip="sayi",
        aciklama="Bir coin bu skorun üstündeyse short adayı sayılır."),
    "esikler.radar_alert_skor": dict(ad="Alarm skor eşiği", min=20, max=90, tip="sayi",
        aciklama="Nöbetçinin bildirim ürettiği skor."),
    "esikler.blowoff_chg24_pct": dict(ad="Aşırı yükselmiş sayılma (%24s)", min=10, max=200, tip="sayi",
        aciklama="24 saatte bu kadar yükselen coin 'patlamış' sayılır."),
    "esikler.ayi_short_chg24_max": dict(ad="Pump kapısı (%24s)", min=5, max=999, tip="sayi",
        aciklama="Ayı rejiminde 24 saatte bundan çok yükselmiş coine short AÇILMAZ. 2026-08-04'te ölçülerek eklendi. 999 = kapalı."),
    "esikler.notr_long_acik": dict(ad="Belirsiz rejimde long", min=0, max=1, tip="anahtar",
        aciklama="Açıkken, rejim belirsizken de temiz long adayları açılabilir. 2026-08-04 kullanıcı kararı; ölçümle gerekçelenmedi."),
    "esikler.btc_pay_short_freni": dict(ad="BTC payı SHORT freni", min=0, max=1, tip="anahtar",
        aciklama="BTC son 3 günde altlara göre pay kazandıysa short açılmaz. Ölçüldü: o bantta short kaybettiriyor."),
    "esikler.btc_pay_ayi_long": dict(ad="BTC payı AYI long penceresi", min=0, max=1, tip="anahtar",
        aciklama="BTC pay kazanıyor + para durgunsa ayıda da long açılabilir. Ölçüldü: +0.24/+0.16."),
    "esikler.btcd_xs_ust": dict(ad="BTC payı üst eşik (puan)", min=0.05, max=2.0, tip="sayi",
        aciklama="365 günlük serinin üst çeyreği. Bunu aşan 3 günlük değişim 'ÜST bant'."),
    "esikler.btcd_xs_alt": dict(ad="BTC payı alt eşik (puan)", min=-2.0, max=-0.05, tip="sayi",
        aciklama="Alt çeyrek. Bunun altı 'ALT bant' — short'un en iyi çalıştığı bant."),
    "esikler.short_onay_taker_max": dict(ad="Short onayı taker tavanı", min=0.9, max=1.5, tip="sayi",
        aciklama="Onay anında agresif alıcı hâlâ baskınsa (bu değerin üstü) short açılmaz, beklenir."),
    "esikler.dusuk_float_oran": dict(ad="Düşük dolaşım sınırı", min=0.05, max=0.9, tip="sayi",
        aciklama="Dolaşımdaki arz / toplam arz bunun altındaysa coin 'düşük float' sayılır (kilit açılma riski)."),
}


def _ayarlar():
    """Beyaz listedeki ayarlarin GUNCEL degerleri + aciklamalari. Gizli alan OKUNMAZ."""
    cfg = _oku_json("kripto-config.json", {}) or {}
    out = []
    for anahtar, meta in AYAR_BEYAZ.items():
        blok, ad = anahtar.split(".", 1)
        deger = (cfg.get(blok) or {}).get(ad)
        out.append({"anahtar": anahtar, "deger": deger, **meta})
    return out


def _ayar_yaz(anahtar, deger):
    """Beyaz liste + aralik dogrulamasi + iz kaydi. -> (ok, mesaj)"""
    meta = AYAR_BEYAZ.get(anahtar)
    if not meta:
        return False, f"'{anahtar}' değiştirilebilir ayarlar listesinde yok (reddedildi)."
    try:
        deger = float(deger)
    except Exception:
        return False, "Değer sayı olmalı."
    if not (meta["min"] <= deger <= meta["max"]):
        return False, f"Değer {meta['min']} – {meta['max']} arasında olmalı (gelen: {deger})."
    if meta["tip"] == "anahtar":
        deger = int(round(deger))
    elif deger == int(deger):
        deger = int(deger)
    yol = os.path.join(HERE, "kripto-config.json")
    try:
        cfg = json.load(open(yol, encoding="utf-8"))
    except Exception as e:
        return False, f"Ayar dosyası okunamadı: {e}"
    blok, ad = anahtar.split(".", 1)
    eski = (cfg.get(blok) or {}).get(ad)
    if eski == deger:
        return True, "Değer zaten buydu, dokunulmadı."
    cfg.setdefault(blok, {})[ad] = deger
    try:
        with open(yol, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return False, f"Yazılamadı: {e}"
    _iz_yaz({"eylem": "ayar", "anahtar": anahtar, "eski": eski, "yeni": deger})
    evren._cfg_cache = None          # varsa onbellek temizle (yoksa zararsiz)
    return True, f"{meta['ad']}: {eski} → {deger}"


def _iz_yaz(kayit):
    """Panelden yapilan HER degisiklik buraya yazilir — 'ne zaman neyi degistirdim' defteri."""
    try:
        kayit = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), **kayit}
        with open(ISLEM_LOGF, "a", encoding="utf-8") as f:
            f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
    except Exception:
        pass


# ===========================================================================
# COIN SAYFASI (2026-08-05) — gosterge hesaplari + tek sembol verisi
# Gostergeler SUNUCUDA hesaplanir: RSI icin olcucu.rsi14 (tek dogruluk kaynagi),
# Bollinger burada (projede stdev hic kullanilmamisti).
# ===========================================================================
import statistics as _ist
import olcucu
import radar

TF_LISTE = ("1m", "5m", "15m", "1h", "4h", "1d", "1w")


def _sma(dizi, n):
    return [None if i < n-1 else round(_ist.mean(dizi[i-n+1:i+1]), 10)
            for i in range(len(dizi))]


def _bollinger(kapanislar, n=20, k=2.0):
    """-> (orta, ust, alt). Orta = SMA(n); bantlar +-k*standart sapma.
    Nufus std'si (pstdev) kullanilir — grafik kutuphanelerinin yaygin kabulu."""
    orta, ust, alt = [], [], []
    for i in range(len(kapanislar)):
        if i < n-1:
            orta.append(None); ust.append(None); alt.append(None); continue
        p = kapanislar[i-n+1:i+1]
        m = _ist.mean(p); s = _ist.pstdev(p)
        orta.append(round(m, 10)); ust.append(round(m+k*s, 10)); alt.append(round(m-k*s, 10))
    return orta, ust, alt


def _rsi_serisi(kapanislar, period=14):
    """Her bar icin RSI — olcucu.rsi14 ile AYNI hesap (o fonksiyon cagrilir)."""
    out = []
    for i in range(len(kapanislar)):
        out.append(olcucu.rsi14(kapanislar[:i+1], period) if i >= period else None)
    return out


def _ohlcv(sym, interval, limit, ttl=30.0):
    """HACIM DAHIL mum. Mevcut _mumlar hacmi atiyordu; o geriye-uyum icin duruyor."""
    def uret():
        url = (f"{FAPI}/fapi/v1/klines?symbol={sym.upper()}USDT"
               f"&interval={interval}&limit={limit}")
        d = evren.get(url, headers={"User-Agent": "panel/1.0"}, timeout=20)
        return [{"time": int(k[0])//1000, "open": float(k[1]), "high": float(k[2]),
                 "low": float(k[3]), "close": float(k[4]), "volume": float(k[5])} for k in d]
    return _tut(f"ohlcv:{sym}:{interval}:{limit}", ttl, uret)


def _pivotlar(bars, left=3, right=3):
    """olcucu.swings ile AYNI pivot tanimi; tek farki INDEKSI de dondurmesi.
    Kumeleme icin 'kacinci barda dokunuldu' bilgisi gerekiyor, swings onu atiyor."""
    out = []
    for i in range(left, len(bars) - right):
        win = bars[i-left:i+right+1]
        if bars[i]["h"] == max(b["h"] for b in win):
            out.append((i, bars[i]["h"]))
        if bars[i]["l"] == min(b["l"] for b in win):
            out.append((i, bars[i]["l"]))
    return out


def _kumele(noktalar, tol):
    """Birbirine tol'dan yakin pivotlari TEK seviyede birlestir.
    Zincirleme kaymayi onlemek icin mesafe kumenin ILK elemanina gore olculur.
    -> [{"fiyat", "dokunus", "son_idx"}]"""
    if not noktalar:
        return []
    gruplar, g = [], []
    for idx, px in sorted(noktalar, key=lambda t: t[1]):
        if g and px - g[0][1] > tol:
            gruplar.append(g); g = []
        g.append((idx, px))
    if g:
        gruplar.append(g)
    return [{"fiyat": _ist.mean([p for _, p in gr]), "dokunus": len(gr),
             "son_idx": max(i for i, _ in gr)} for gr in gruplar]


def _basamak(fiyat):
    """Kume ortalamasi 74.9366666667 gibi cikiyor; fiyatin buyuklugune gore
    anlamli basamaga yuvarlanir (5 anlamli hane)."""
    import math
    if not fiyat or fiyat <= 0:
        return 4
    return max(0, min(8, 5 - int(math.floor(math.log10(abs(fiyat)))) - 1))


def _seviyeler(mumlar, fiyat, adet=3):
    """Grafikte gosterilecek YAPISAL destek/direnc seviyeleri.

    2026-08-05 DUZELTME-1: onceden en YUKSEK 6 direnc / en DUSUK 6 destek
    donuyordu (uc noktalar): 1g grafikte fiyat 74 iken direncler 146-211,
    olcek oraya aciliyor ve mumlar okunmaz oluyordu. "En yakin"a cevrildi.

    2026-08-05 DUZELTME-2 (kullanici: "destek direnc dogru vermiyor"):
    "en yakin pivot" destek/direnc DEGIL. SOL 1s'te fiyat 74.47 iken donen
    3 direnc 74.50 / 74.51 / 74.55 idi — birbirinin ustunde, %0.04 uzakta,
    3-barlik mikro tepecikler. Gercek seviye = fiyatin DEFALARCA donduugu bolge.
    Artik pivotlar ATR tabanli bir bantla KUMELENIYOR; kume = seviye, kume
    buyuklugu = dokunus sayisi. Once fiyata yakin havuz alinir, icinden EN COK
    DOKUNULANLAR secilir. Fiyata yapisik (yarim bant icindeki) kumeler elenir.

    NOT: bu GORUNTULEME katmanidir. Botun stopu hala olcucu.nearest'in tek
    pivotunu kullanir — o degismedi, karsilastirilabilsin diye bot_* alanlarinda
    ayrica donuyor."""
    bars = [{"o": m["open"], "h": m["high"], "l": m["low"], "c": m["close"]} for m in mumlar]
    bos = {"direncler": [], "destekler": [], "en_yakin_direnc": None,
           "en_yakin_destek": None, "bot_direnc": None, "bot_destek": None, "bant": None}
    if len(bars) < 10 or not fiyat:
        return bos
    try:
        hi, lo = olcucu.swings(bars)
        bot_res, bot_sup = olcucu.nearest(fiyat, hi, lo)
        # Kume bandi: yariım ATR, ama en az fiyatin binde 1.5'i (cok sakin dilimlerde
        # ATR sifira yaklasip her pivot ayri seviye sayilmasin diye taban var).
        tol = max(olcucu.atr(bars) * 0.5, fiyat * 0.0015)
        n = len(bars)
        bs = _basamak(fiyat)
        kumeler = _kumele(_pivotlar(bars), tol)
        for k in kumeler:
            k["tazelik"] = round(k["son_idx"] / max(n - 1, 1), 3)
            k["guc"] = k["dokunus"] + k["tazelik"]      # dokunus baskin, tazelik esitlik bozar
            k["uzaklik_pct"] = round((k["fiyat"] / fiyat - 1) * 100, 2)
            k["fiyat"] = round(k["fiyat"], bs)
            k.pop("son_idx", None)

        def sec(liste):
            liste.sort(key=lambda k: abs(k["fiyat"] - fiyat))
            havuz = liste[:adet * 3]                                  # once yakinlik
            gucluler = sorted(havuz, key=lambda k: -k["guc"])[:adet]   # icinden en guclu
            return sorted(gucluler, key=lambda k: abs(k["fiyat"] - fiyat))

        ust = sec([k for k in kumeler if k["fiyat"] > fiyat + tol * 0.5])
        alt = sec([k for k in kumeler if k["fiyat"] < fiyat - tol * 0.5])
        return {"direncler": ust, "destekler": alt,
                "en_yakin_direnc": (ust[0]["fiyat"] if ust else None),
                "en_yakin_destek": (alt[0]["fiyat"] if alt else None),
                "bot_direnc": bot_res, "bot_destek": bot_sup,
                "bant": round(tol, bs)}
    except Exception:
        return bos


def _sembol_listesi():
    """Arama kutusu: botun tarayabildigi perp evreni (hisse/stable elenmis)."""
    def uret():
        try:
            kripto = evren.cg_universe()
            pool = evren.binance_pool("fapi", 0.0,
                                      cryptos=(set(kripto.keys()) if kripto else None))
        except Exception:
            return []
        return [{"sym": s, "hacim_musd": round(qv/1e6, 1), "chg24": round(chg, 2)}
                for s, qv, chg in pool]
    return _tut("semboller", 300.0, uret)


def _arsiv_gecmis(sym):
    """Bu sembolun gecmis radar/aday kayitlari. radar_archive.jsonl 52 MB —
    TAM BELLEGE ALINMAZ: satir satir akitilir, yalniz bu sembolun kayitlari tutulur."""
    sym = sym.upper()
    def uret():
        radar_k, aday_k = [], []
        try:
            with open(os.path.join(HERE, "radar_archive.jsonl"), encoding="utf-8") as f:
                for satir in f:
                    if f'"sym": "{sym}"' not in satir:      # ucuz on-eleme
                        continue
                    try:
                        d = json.loads(satir)
                    except Exception:
                        continue
                    if d.get("sym") == sym:
                        radar_k.append({a: d.get(a) for a in
                                        ("ts", "score", "stage", "price", "oi24", "funding", "pos")})
        except Exception:
            pass
        try:
            for d in _tail_jsonl(os.path.join(HERE, "testbot_aday_arsiv.jsonl"), n=4000):
                if d.get("sym") == sym:
                    aday_k.append({a: d.get(a) for a in ("ts", "score", "stage", "karar", "price")})
        except Exception:
            pass
        skorlar = [r["score"] for r in radar_k if r.get("score") is not None]
        return {"sym": sym, "radar": radar_k[-400:], "aday": aday_k[-200:],
                "radar_toplam": len(radar_k), "aday_toplam": len(aday_k),
                "skor_max": max(skorlar) if skorlar else None,
                "skor_ort": round(_ist.mean(skorlar), 1) if skorlar else None,
                "kez_45_ustu": len([s for s in skorlar if s >= 45]),
                "kez_60_ustu": len([s for s in skorlar if s >= 60])}
    return _tut(f"gecmis:{sym}", 600.0, uret)


def _coin(sym):
    """Tek coin: botun gordugu HER SEY + olcucu'nun iki yonlu olcumu + botun gorusu.
    SALT OKUR — hicbir state dosyasina dokunmaz."""
    sym = sym.upper().strip()
    gorus, r, pillar, rejim_ad = benim_modul().bot_gorusu(sym, "SHORT")
    if not r:
        return {"hata": f"{sym} için veri alınamadı (sembol yanlış veya çok yeni)."}
    olc = {}
    for yon in ("long", "short"):
        try:
            olc[yon] = olcucu.measure(sym, yon, "1h", 100, spot=False)
        except Exception as e:
            olc[yon] = {"hata": str(e)[:120]}
    cg = {}
    try:
        cg = (evren.cg_universe() or {}).get(sym) or {}
    except Exception:
        pass
    tk = _ticker_haritasi().get(sym) or {}
    def f(a):
        try:
            return float(tk[a])
        except Exception:
            return None
    piyasa = {"fiyat": f("lastPrice"), "chg24": f("priceChangePercent"),
              "hacim_musd": (f("quoteVolume")/1e6 if f("quoteVolume") else None),
              "yuksek24": f("highPrice"), "dusuk24": f("lowPrice"),
              "mcap": cg.get("mcap"), "dolasim": cg.get("circ"), "toplam_arz": cg.get("total"),
              "float_oran": cg.get("float_oran")}
    # ALT/BTC paritesi (2026-08-10): kullanicinin kendi teknigi — "USD'de yesil ama
    # BTC'ye karsi kirmizi" tuzagi. OLCUM katmani, hicbir kapiya baglanmadi.
    try:
        altbtc = _tut(f"altbtc:{sym}", 600.0, lambda: evren.alt_btc(sym))
    except Exception:
        altbtc = None
    st = testbot._load_state() or {}
    return {"sym": sym, "radar": r, "pillar": pillar, "olcucu": olc, "alt_btc": altbtc,
            "bot_gorusu": gorus, "rejim": rejim_ad, "piyasa": piyasa,
            "mcap": cg.get("mcap"), "float_oran": cg.get("float_oran"),
            "equity_bot": st.get("equity"),
            "equity_benim": (benim_modul().yukle() or {}).get("equity"),
            "islem_risk_pct": float(testbot._c("islem_risk_pct", 3)),
            "kaldirac_min": float(testbot._c("kaldirac_min", 3)),
            "kaldirac_max": float(testbot._c("kaldirac_max", 10)),
            # istemci stop kutusunu degistirdiginde boyutu AYNI formulle onizlesin diye:
            "marjin_pct": testbot.marjin_pct_hesapla(r.get("score") or 0)}


def benim_modul():
    """Tembel import — benim.py yoksa panel yine ayakta kalsin."""
    import benim
    return benim


def _benim():
    """'Ben' hesabinin durumu. Hesap hic acilmadiysa bos iskelet doner."""
    try:
        b = benim_modul()
    except Exception as e:
        return {"var": False, "hata": str(e)[:120]}
    st = b.yukle()
    if not st:
        return {"var": False}
    acik = []
    for p in st["acik_pozisyonlar"]:
        px = testbot.fiyat_fapi(p["sym"]) or p["giris"]
        yi = 1 if p["yon"] == "LONG" else -1
        acik.append({**p, "anlik_fiyat": px,
                     "acik_pnl": round((px-p["giris"])*p["miktar"]*yi, 2),
                     "notional": round(p["miktar"]*p["giris"], 2)})
    islemler = _tail_jsonl(b.ISLEMLERF, n=500)
    tam = [t for t in islemler if not t.get("kismi")]
    kz = [t for t in tam if t["sonuc_usdt"] > 0]
    rler = [t["r"] for t in tam if t.get("r") is not None]
    kullanilan = round(sum(p["marjin"] for p in acik), 2)
    return {"var": True, "durum": st["durum"], "baslangic_bakiye": st["baslangic_bakiye"],
            "equity": round(st["equity"], 2), "baslangic_ts": st.get("baslangic_ts"),
            "acik_pozisyonlar": acik, "kullanilan_marjin": kullanilan,
            "serbest_bakiye": round(st["equity"]-kullanilan, 2),
            "acik_pnl_toplam": round(sum(a["acik_pnl"] for a in acik), 2),
            "islemler": islemler[::-1],
            "equity_serisi": _tail_jsonl(b.EQUITYF, n=2000),
            "karne": {"toplam_islem": len(tam), "kazanan": len(kz),
                      "win_rate": round(len(kz)/len(tam)*100, 1) if tam else None,
                      "toplam_pnl": round(sum(t["sonuc_usdt"] for t in islemler), 2),
                      "ort_r": round(sum(rler)/len(rler), 2) if rler else None}}


def _karne_ozet(islemler):
    tam = [t for t in islemler if not t.get("kismi")]
    kz = [t for t in tam if t["sonuc_usdt"] > 0]
    rler = [t["r"] for t in tam if t.get("r") is not None]
    return {"n": len(tam), "kazanan": len(kz),
            "win_rate": round(len(kz)/len(tam)*100, 1) if tam else None,
            "pnl": round(sum(t["sonuc_usdt"] for t in islemler), 2),
            "ort_r": round(sum(rler)/len(rler), 2) if rler else None}


def _dusus(seri):
    zirve, maks = None, 0.0
    for e in seri:
        v = e.get("equity")
        if v is None:
            continue
        zirve = v if zirve is None else max(zirve, v)
        maks = min(maks, (v/zirve-1)*100 if zirve else 0.0)
    return round(maks, 2)


def _karsilastirma():
    """BOT vs BEN — iki defteri okur, HICBIR SEY YAZMAZ."""
    bot_i = _tail_jsonl(testbot.ISLEMLERF, n=2000)
    try:
        b = benim_modul()
        ben_i = _tail_jsonl(b.ISLEMLERF, n=2000)
        ben_eq = _tail_jsonl(b.EQUITYF, n=3000)
    except Exception:
        ben_i, ben_eq = [], []
    bot_eq = _tail_jsonl(testbot.EQUITYF, n=3000)

    # Bot ONAYLADIGINDA vs BOTA RAGMEN
    tam = [t for t in ben_i if not t.get("kismi")]
    onay = [t for t in tam if (t.get("bot_gorusu") or {}).get("ayni_yonde")]
    ragmen = [t for t in tam if not (t.get("bot_gorusu") or {}).get("ayni_yonde")]
    # NOT: kapanan kayitta bot_gorusu yoksa (eski/kismi) "bota ragmen" sayilir —
    # bu muhafazakar taraf: kendi lehimize saymiyoruz.

    return {
        "bot": {**_karne_ozet(bot_i), "maks_dusus": _dusus(bot_eq),
                "equity": (bot_eq[-1]["equity"] if bot_eq else None)},
        "ben": {**_karne_ozet(ben_i), "maks_dusus": _dusus(ben_eq),
                "equity": (ben_eq[-1]["equity"] if ben_eq else None)},
        "bot_onayladi": _karne_ozet(onay),
        "bota_ragmen": _karne_ozet(ragmen),
        "karsi_olgu_1": {"n": len(ragmen),
                         "toplam": round(sum(t["sonuc_usdt"] for t in ragmen), 2)},
        "karsi_olgu_2": {"bot_islem": len([t for t in bot_i if not t.get("kismi")]),
                         "benim_islem": len(tam)},
        "bot_equity_serisi": [{"ts": e.get("ts"), "equity": e.get("equity")} for e in bot_eq],
        "ben_equity_serisi": [{"ts": e.get("ts"), "equity": e.get("equity")} for e in ben_eq],
        "yeterli_mi": len(tam) >= 25,
    }


def _kontrol(eylem, arg=None):
    """Panelden bot mudahalesi. Durum yazan her eylem KILIT alir (bot ayri surecte
    --cycle kosuyor; ayni anda state yazilirsa yaris olur). -> (ok, mesaj)"""
    if eylem in ("bot_durdur", "bot_devam"):
        yeni = "DURAKLATILDI" if eylem == "bot_durdur" else "AKTIF"
        if not testbot._kilit_al(timeout_sn=30):
            return False, "Bot şu an bir tur koşuyor, kilit alınamadı. Birkaç saniye sonra dene."
        try:
            st = testbot._load_state()
            if st is None:
                return False, "Bot henüz başlamamış."
            eski = st["durum"]
            st["durum"] = yeni
            testbot._save_state(st)
        finally:
            testbot._kilit_birak()
        _iz_yaz({"eylem": eylem, "anahtar": "durum", "eski": eski, "yeni": yeni})
        return True, f"Bot durumu: {eski} → {yeni}"

    if eylem in ("bildirim_ac", "bildirim_kapa"):
        yol = os.path.join(HERE, "kripto-config.json")
        try:
            cfg = json.load(open(yol, encoding="utf-8"))
        except Exception as e:
            return False, f"Ayar dosyası okunamadı: {e}"
        eski = bool((cfg.get("bildirim") or {}).get("acik", True))
        yeni = (eylem == "bildirim_ac")
        cfg.setdefault("bildirim", {})["acik"] = yeni
        try:
            with open(yol, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception as e:
            return False, f"Yazılamadı: {e}"
        _iz_yaz({"eylem": eylem, "anahtar": "bildirim.acik", "eski": eski, "yeni": yeni})
        evren._cfg_cache = None
        return True, f"Bildirimler {'AÇIK' if yeni else 'KAPALI'}"

    if eylem == "pozisyon_kapat":
        if not arg:
            return False, "Hangi pozisyon? (sembol gerekli)"
        if not testbot._kilit_al(timeout_sn=30):
            return False, "Bot şu an bir tur koşuyor, kilit alınamadı. Birkaç saniye sonra dene."
        try:
            st = testbot._load_state()
            if st is None:
                return False, "Bot henüz başlamamış."
            pos = next((p for p in st["acik_pozisyonlar"] if p["sym"] == str(arg).upper()), None)
            if not pos:
                return False, f"{arg} adında açık pozisyon yok."
            px = testbot.fiyat_fapi(pos["sym"])
            if not px:
                return False, "Anlık fiyat alınamadı, kapatma yapılmadı."
            testbot.pozisyon_kapat(st, pos, px, "PANEL_MANUEL")
            testbot._save_state(st)
        finally:
            testbot._kilit_birak()
        _iz_yaz({"eylem": "pozisyon_kapat", "anahtar": str(arg).upper(), "eski": "acik", "yeni": "kapali"})
        return True, f"{str(arg).upper()} pozisyonu kapatıldı (sebep: PANEL_MANUEL)."

    return False, f"Bilinmeyen eylem: {eylem}"


# ---------------------------------------------------------------------------
# OKUMA UCLARI
# ---------------------------------------------------------------------------

def _kafa():
    """BOTUN KAFASI — 'ne gordu, ne karar verdi, neden girmedi'.
    Kaynak testbot_aday_arsiv.jsonl (botun KENDI evreni). radar_archive DEGIL:
    o radar'in hacim-patlamasi evreni, botun tarama havuzuyla ayni degil."""
    adaylar = _tail_jsonl(os.path.join(HERE, "testbot_aday_arsiv.jsonl"), n=600)
    karar_dagilim = {}
    for a in adaylar:
        k = a.get("karar") or "kayit-yok"
        karar_dagilim[k] = karar_dagilim.get(k, 0) + 1
    son_ts = adaylar[-1].get("ts") if adaylar else None
    son_tur = [a for a in adaylar if a.get("ts") == son_ts]

    vetolar = _tail_jsonl(os.path.join(HERE, "veto_log.jsonl"), n=200)
    veto_kirilim = {}
    for v in vetolar:
        k = v.get("kategori") or "?"
        d = veto_kirilim.setdefault(k, {"n": 0, "ornekler": []})
        d["n"] += 1
        if len(d["ornekler"]) < 3:
            d["ornekler"].append({"sym": v.get("sym"), "detay": v.get("detay"), "ts": v.get("ts")})

    st = testbot._load_state() or {}
    bekleyen = [{"sym": s, **(v if isinstance(v, dict) else {})}
                for s, v in (st.get("bekleyenler") or {}).items()]
    simdi = time.time()
    def _kalan(ts_str, saat):
        try:
            t = time.mktime(time.strptime(ts_str, "%Y-%m-%d %H:%M:%S"))
            return round(max(0.0, (t + saat * 3600 - simdi) / 3600), 1)
        except Exception:
            return None
    cooldown = [{"sym": s, "ts": t, "kalan_saat": _kalan(t, 4)}
                for s, t in (st.get("cooldown") or {}).items()]
    cooldown = [c for c in cooldown if (c["kalan_saat"] or 0) > 0]

    return {
        "son_tur_ts": son_ts,
        "son_tur_aday": len(son_tur),
        "aday_toplam": len(adaylar),
        "karar_dagilim": karar_dagilim,
        "adaylar": adaylar[-120:][::-1],
        "veto_kirilim": veto_kirilim,
        "veto_son": vetolar[-25:][::-1],
        "bekleyenler": bekleyen,
        "cooldown": cooldown,
        "acik_sayisi": len(st.get("acik_pozisyonlar") or []),
        "maks_pozisyon": testbot._c("maks_pozisyon", 4),
        # GOLGE DEFTER (2026-08-10): reddedilen girislerin sanal karnesi. Bu sayfanin adi
        # "Bot neden islem acmiyor?" — asil eksik cevap "peki acsaydi ne olurdu" idi.
        "golge": _golge_ozet(),
        # Sure: SURE_DOLDU'ya girince YENI GIRIS HIC olmaz; "bot girmiyor"un sessiz sebebi
        # bu olabilir, o yuzden sayfada gorunur.
        "sure": _sure_durumu(st),
    }


def _golge_ozet():
    """golge.py karnesi + acik golge pozisyon sayisi. Golge yoksa None (panel bozulmaz)."""
    try:
        import golge
        gst = golge.yukle()
        if not gst:
            return None
        return {"karne": golge.karne(), "acik": len(gst.get("acik_pozisyonlar") or []),
                "equity": round(gst.get("equity", 0), 2),
                "baslangic_bakiye": gst.get("baslangic_bakiye"),
                "baslangic_ts": gst.get("baslangic_ts")}
    except Exception:
        return None


def _sure_durumu(st):
    """Testin kac gunu doldu — SURE_DOLDU yeni girisi TAMAMEN kapatir."""
    try:
        gecen = (testbot.now_dt() - testbot.parse_iso(st["baslangic_ts"])).total_seconds() / 86400
        sure = float(testbot._c("sure_gun", 7))
        return {"gecen_gun": round(gecen, 1), "sure_gun": sure,
                "kalan_gun": round(max(0.0, sure - gecen), 1),
                "durum": st.get("durum")}
    except Exception:
        return None


def _gecmis():
    """Derinlestirilmis karne: drawdown, kirilimlar, R dagilimi, tur karsilastirma."""
    try:
        islemler = [json.loads(l) for l in open(testbot.ISLEMLERF, encoding="utf-8")
                    .read().splitlines() if l.strip()]
    except Exception:
        islemler = []
    tam = [t for t in islemler if not t.get("kismi")]

    eq = _tail_jsonl(testbot.EQUITYF, n=4000)
    dd, zirve, maks_dd = [], None, 0.0
    for e in eq:
        v = e.get("equity")
        if v is None:
            continue
        zirve = v if zirve is None else max(zirve, v)
        d = (v / zirve - 1) * 100 if zirve else 0.0
        maks_dd = min(maks_dd, d)
        dd.append({"ts": e.get("ts"), "dd": round(d, 2), "equity": round(v, 2)})

    def kir(alan):
        g = {}
        for t in tam:
            k = str(t.get(alan) or "?")
            d = g.setdefault(k, {"n": 0, "kazanan": 0, "pnl": 0.0, "r": []})
            d["n"] += 1
            d["kazanan"] += 1 if t["sonuc_usdt"] > 0 else 0
            d["pnl"] += t["sonuc_usdt"]
            if t.get("r") is not None:
                d["r"].append(t["r"])
        for k, d in g.items():
            d["pnl"] = round(d["pnl"], 2)
            d["ort_r"] = round(sum(d["r"]) / len(d["r"]), 2) if d["r"] else None
            d.pop("r")
        return g

    kovalar = [(-99, -1), (-1, -0.5), (-0.5, 0), (0, 0.5), (0.5, 1), (1, 2), (2, 99)]
    r_hist = []
    for lo, hi in kovalar:
        n = len([t for t in tam if t.get("r") is not None and lo <= t["r"] < hi])
        r_hist.append({"aralik": f"{lo:g} … {hi:g}", "n": n})

    sirali = sorted([t for t in tam], key=lambda t: t["sonuc_usdt"])
    turlar = []
    try:
        for f in sorted(os.listdir(os.path.join(HERE, "arsiv"))):
            if not (f.startswith("testbot_islemler.") and f.endswith(".jsonl")):
                continue
            rs = _tail_jsonl(os.path.join(HERE, "arsiv", f), n=2000)
            rs = [t for t in rs if not t.get("kismi")]
            if not rs:
                continue
            kz = len([t for t in rs if t["sonuc_usdt"] > 0])
            rr = [t["r"] for t in rs if t.get("r") is not None]
            turlar.append({"tur": f.split(".")[1], "n": len(rs), "kazanan": kz,
                           "win_rate": round(kz / len(rs) * 100, 1),
                           "pnl": round(sum(t["sonuc_usdt"] for t in rs), 2),
                           "ort_r": round(sum(rr) / len(rr), 2) if rr else None})
    except Exception:
        pass
    if tam:
        kz = len([t for t in tam if t["sonuc_usdt"] > 0])
        rr = [t["r"] for t in tam if t.get("r") is not None]
        turlar.append({"tur": "ŞU ANKİ", "n": len(tam), "kazanan": kz,
                       "win_rate": round(kz / len(tam) * 100, 1),
                       "pnl": round(sum(t["sonuc_usdt"] for t in tam), 2),
                       "ort_r": round(sum(rr) / len(rr), 2) if rr else None})

    return {
        "islemler": islemler[::-1],
        "drawdown": dd[-1500:], "maks_drawdown": round(maks_dd, 2),
        "kirilim_sembol": kir("sym"), "kirilim_sebep": kir("sebep"),
        "kirilim_rejim": kir("rejim_giriste"), "kirilim_yon": kir("yon"),
        "kirilim_stage": kir("stage_giriste"),
        "r_histogram": r_hist,
        "en_kotu": sirali[:3], "en_iyi": sirali[-3:][::-1],
        "turlar": turlar,
    }


def _piyasa():
    """Rejim + para + BTC payi + dominance serisi + makro takvim — tek yerde."""
    try:
        rejim = evren.btc_rejim()
    except Exception:
        rejim = {}
    try:
        para = evren.para_rejim()
    except Exception:
        para = None
    try:
        bp = evren.btc_pay_akisi()
    except Exception:
        bp = None
    bp_seri = [{"gun": r.get("gun"), "xs": r.get("btc_d_xs")}
               for r in _tail_jsonl(os.path.join(HERE, "btc_pay_log.jsonl"), n=400)]
    dom = _tail_jsonl(os.path.join(HERE, "piyasa_yapisi_log.jsonl"), n=200)
    dom_seri = [{a: d.get(a) for a in ("ts", "btc_d", "eth_d", "usdt_d", "stable_d", "total")}
                | {"breadth": next((v for k, v in d.items() if k.startswith("breadth")), None)}
                for d in dom]
    takvim = _oku_json("makro_takvim.json", {}) or {}
    bugun = time.strftime("%Y-%m-%d")
    yaklasan = []
    for tur in ("fomc", "cpi"):
        for g in (takvim.get(tur) or []):
            if str(g) >= bugun:
                yaklasan.append({"tur": tur.upper(), "gun": g})
    yaklasan.sort(key=lambda x: x["gun"])
    return {"rejim": rejim, "para": para, "btc_pay": bp, "btc_pay_seri": bp_seri,
            "dominance": dom_seri, "para_akisi": _para_akisi(), "makro": yaklasan[:6],
            "esikler": {"btcd_xs_ust": evren.esik("btcd_xs_ust", 0.287),
                        "btcd_xs_alt": evren.esik("btcd_xs_alt", -0.318)}}


def _defter():
    """GERCEK defter — senin paran. Fiyatlar TEK ticker cagrisindan (21 ayri istek atmadan)."""
    pf = _oku_json("kripto_portfoy.json", {}) or {}
    gc = _oku_json("kripto_gecmis.json", {}) or {}
    fh = _fiyat_haritasi()
    spot = []
    for p in (pf.get("spot_pozisyonlar") or []):
        sym = (p.get("sembol") or "").upper()
        px = fh.get(sym)
        spot.append({"sym": sym, "miktar": p.get("miktar"), "maliyet": p.get("maliyet_usdt"),
                     "pnl_pct_kayitli": p.get("pnl_pct"), "durum": p.get("durum"),
                     "not": p.get("not"), "anlik": px})
    kapanan = gc.get("kapanan_tahminler") or []
    isabet = None
    if kapanan:
        v = [t for t in kapanan if t.get("sonuc")]
        if v:
            tut = len([t for t in v if str(t.get("sonuc")).upper().startswith(("TUT", "ISABET", "DOGRU"))])
            isabet = {"n": len(v), "tutan": tut, "oran": round(tut / len(v) * 100, 1)}
    return {"spot": spot, "aktif_futures": _gercek_pozlar(),
            "tahminler": pf.get("tahminler") or [], "dersler": pf.get("dersler") or [],
            "izleme": pf.get("izleme_listesi") or [], "dca": pf.get("dca_plani") or {},
            "hipotezler": pf.get("izlenen_hipotezler") or [],
            "kapanan_tahminler": kapanan, "isabet": isabet,
            "kapatilan_futures": pf.get("kapatilan_futures") or []}


_DURUM_ETIKET = ("ÖLDÜ", "ÇÜRÜDÜ", "GERİ ALINDI", "KOŞULSUZ", "RAFTA", "KAPIYA BAĞLI",
                 "DOĞRULANDI", "GEREKÇELENDİ", "ELENDİ", "AYAKTA")


def _gunluk():
    """fikir-defteri.md -> zaman cizelgesi kartlari. SALT OKUR, dosyaya dokunulmaz."""
    try:
        satirlar = open(os.path.join(HERE, "fikir-defteri.md"), encoding="utf-8").read().splitlines()
    except Exception:
        return {"kartlar": []}
    import re
    kartlar, aktif = [], None
    tarih_re = re.compile(r"(20\d\d-\d\d-\d\d)")
    for i, s in enumerate(satirlar):
        if s.startswith("## ") or s.startswith("### "):
            if aktif:
                kartlar.append(aktif)
            baslik = s.lstrip("#").strip()
            t = tarih_re.search(baslik)
            aktif = {"seviye": 2 if s.startswith("## ") else 3, "baslik": baslik,
                     "tarih": t.group(1) if t else None, "satir": i + 1,
                     "durum": next((e for e in _DURUM_ETIKET if e in baslik.upper()), None),
                     "govde": []}
        elif aktif is not None and s.strip():
            if len(aktif["govde"]) < 6:
                aktif["govde"].append(s.strip())
            if not aktif["durum"]:
                aktif["durum"] = next((e for e in _DURUM_ETIKET if e in s.upper()), None)
            if not aktif["tarih"]:
                t = tarih_re.search(s)
                if t:
                    aktif["tarih"] = t.group(1)
    if aktif:
        kartlar.append(aktif)
    return {"kartlar": kartlar[::-1], "toplam": len(kartlar)}


def _ozet():
    """DUZ TURKCE anlati + madde listesi. KURAL TABANLI — ayni veriden hep ayni cumle.
    Uydurma yok: her cumle bir veri alanina bagli, veri yoksa cumle YAZILMAZ."""
    d = _durum_json()
    p = _tut("piyasa", 60.0, _piyasa)
    anlati, maddeler = [], []

    rj = p.get("rejim") or {}
    f10 = rj.get("f10")
    F10_TR = {"TAM_BOGA": "tam boğa", "TEPKI_RALLISI": "ayı içinde tepki rallisi",
              "DERIN_AYI": "derin ayı", "BOGA_DUZELTME": "boğa içinde düzeltme",
              "BELIRSIZ": "belirsiz"}
    if f10:
        anlati.append(f"Piyasa {rj.get('sezon','?').lower()} mevsiminde, kısa vadeli hava "
                      f"{rj.get('hava','?').lower()}. Birleşince: {F10_TR.get(f10, f10)}.")
        maddeler.append({"metin": f"Rejim: {F10_TR.get(f10, f10)}", "renk": "notr"})

    pa = p.get("para") or {}
    if pa.get("rejim"):
        anlati.append(f"Para tarafı: {pa['rejim'].lower()} — son 7 günde tüm kripto piyasası "
                      f"%{pa.get('total_chg', 0):+.1f} değişti.")
        maddeler.append({"metin": f"Para: {pa['rejim'].lower()} (7g %{pa.get('total_chg',0):+.1f})",
                         "renk": "kotu" if "CIKIYOR" in pa["rejim"] else "notr"})

    bp = p.get("btc_pay") or {}
    if bp.get("bant"):
        bant, deg = bp["bant"], bp.get("degisim", 0)
        if bant == "UST":
            anlati.append(f"BTC son 3 günde altcoinlere göre pay kazandı ({deg:+.2f} puan). "
                          f"Ölçümde bu bant short için kötü çıkmıştı, o yüzden bot şu anda "
                          f"SHORT AÇMIYOR.")
            maddeler.append({"metin": f"BTC payı: ÜST bant ({deg:+.2f}) → SHORT freni açık",
                             "renk": "uyari"})
        elif bant == "ALT":
            anlati.append(f"BTC son 3 günde altcoinlere göre pay kaybetti ({deg:+.2f} puan). "
                          f"Ölçümde short'un en iyi çalıştığı bant burası.")
            maddeler.append({"metin": f"BTC payı: ALT bant ({deg:+.2f}) → short için elverişli",
                             "renk": "iyi"})
        else:
            maddeler.append({"metin": f"BTC payı: orta bant ({deg:+.2f}) → özel bir şey yok",
                             "renk": "notr"})

    if not d.get("basladi"):
        anlati.append("Test botu henüz başlamamış.")
        return {"anlati": anlati, "maddeler": maddeler}

    acik = d.get("acik_pozisyonlar") or []
    if acik:
        kar = sum(1 for a in acik if a["acik_pnl"] > 0)
        anlati.append(f"Şu an {len(acik)} açık pozisyon var, {kar} tanesi kârda. "
                      f"Gerçekleşmemiş sonuç {d['acik_pnl_toplam']:+.2f}$.")
        maddeler.append({"metin": f"Açık pozisyon: {len(acik)} ({d['acik_pnl_toplam']:+.2f}$)",
                         "renk": "iyi" if d["acik_pnl_toplam"] > 0 else "kotu"})
    else:
        anlati.append("Şu an açık pozisyon yok.")
        maddeler.append({"metin": "Açık pozisyon: yok", "renk": "notr"})

    k = d.get("karne") or {}
    bas, eq = d.get("baslangic_bakiye") or 0, d.get("equity") or 0
    if bas:
        anlati.append(f"Bakiye {bas:,.0f}$'dan {eq:,.0f}$'a geldi (%{(eq/bas-1)*100:+.1f}). "
                      f"{k.get('toplam_islem',0)} kapanan işlemin {k.get('kazanan',0)} tanesi kazanmış.")
        maddeler.append({"metin": f"Bakiye: {eq:,.0f}$ (%{(eq/bas-1)*100:+.1f})",
                         "renk": "iyi" if eq >= bas else "kotu"})
    if k.get("win_rate") is not None:
        maddeler.append({"metin": f"Kazanma oranı %{k['win_rate']} · ortalama R {k.get('ort_r')}",
                         "renk": "iyi" if (k.get("ort_r") or 0) > 0 else "kotu"})
    if d.get("durum") and d["durum"] != "AKTIF":
        maddeler.append({"metin": f"DİKKAT: bot {d['durum']}", "renk": "kotu"})
    return {"anlati": anlati, "maddeler": maddeler}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # sessiz (konsolu kirletme)

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            try:
                html = open(os.path.join(HERE, "panel.html"), "rb").read()
            except Exception:
                html = b"<h1>panel.html bulunamadi</h1>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
        elif u.path == "/api/durum":
            self._json(_durum_json())
        elif u.path == "/api/sistem":
            self._json(_sistem_json())
        elif u.path == "/api/mumlar":
            q = urllib.parse.parse_qs(u.query)
            sym = (q.get("sym") or ["BTC"])[0]
            interval = (q.get("interval") or ["15m"])[0]
            limit = int((q.get("limit") or ["200"])[0])
            self._json(_mumlar(sym, interval, limit))
        elif u.path == "/api/ozet":
            self._json(_tut("ozet", 30.0, _ozet))
        elif u.path == "/api/kafa":
            self._json(_tut("kafa", 30.0, _kafa))
        elif u.path == "/api/gecmis":
            self._json(_tut("gecmis", 60.0, _gecmis))
        elif u.path == "/api/piyasa":
            self._json(_tut("piyasa", 60.0, _piyasa))
        elif u.path == "/api/defter":
            self._json(_tut("defter", 60.0, _defter))
        elif u.path == "/api/gunluk":
            self._json(_tut("gunluk", 300.0, _gunluk))
        elif u.path == "/api/semboller":
            self._json({"semboller": _sembol_listesi()})
        elif u.path == "/api/coin":
            q = urllib.parse.parse_qs(u.query)
            sym = (q.get("sym") or [""])[0].upper().strip()
            if not sym:
                return self._json({"hata": "sembol gerekli"}, 400)
            self._json(_tut(f"coin:{sym}", 60.0, lambda: _coin(sym)))
        elif u.path == "/api/coin_mum":
            q = urllib.parse.parse_qs(u.query)
            sym = (q.get("sym") or ["BTC"])[0].upper().strip()
            tf = (q.get("tf") or ["1h"])[0]
            if tf not in TF_LISTE:
                return self._json({"hata": "gecersiz zaman dilimi"}, 400)
            limit = max(60, min(500, int((q.get("limit") or ["300"])[0])))
            try:
                m = _ohlcv(sym, tf, limit)
            except Exception as e:
                return self._json({"hata": str(e)[:140]}, 502)
            if not m:
                return self._json({"hata": f"{sym} icin mum verisi yok"}, 404)
            kap = [x["close"] for x in m]
            bo, bu, ba = _bollinger(kap)
            self._json({"sym": sym, "tf": tf, "mumlar": m,
                        "bollinger": {"orta": bo, "ust": bu, "alt": ba},
                        "rsi": _rsi_serisi(kap), "ma50": _sma(kap, 50), "ma200": _sma(kap, 200),
                        "seviyeler": _seviyeler(m, kap[-1])})
        elif u.path == "/api/coin_gecmis":
            q = urllib.parse.parse_qs(u.query)
            sym = (q.get("sym") or [""])[0].upper().strip()
            self._json(_arsiv_gecmis(sym) if sym else {"hata": "sembol gerekli"})
        elif u.path == "/api/coin_guvenlik":
            q = urllib.parse.parse_qs(u.query)
            sym = (q.get("sym") or [""])[0].upper().strip()
            def guv():
                try:
                    import kucukcap
                    return kucukcap.rapor(sym, evren.cg_key())
                except Exception as e:
                    return {"hata": str(e)[:200]}
            self._json(_tut(f"guv:{sym}", 900.0, guv) if sym else {"hata": "sembol gerekli"})
        elif u.path == "/api/benim":
            self._json(_tut("benim", 30.0, _benim))
        elif u.path == "/api/karsilastirma":
            self._json(_tut("karsilastirma", 60.0, _karsilastirma))
        elif u.path == "/api/ayarlar":
            self._json({"ayarlar": _ayarlar(),
                        "bildirim_acik": bool((_oku_json("kripto-config.json", {}) or {})
                                              .get("bildirim", {}).get("acik", True)),
                        "iz": _tail_jsonl(ISLEM_LOGF, n=30)[::-1]})
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        """YAZMA uclari. Beyaz liste + aralik dogrulamasi + kilit + iz kaydi.
        Sunucu 127.0.0.1'e bagli; yine de her istek sunucu tarafinda dogrulanir."""
        u = urllib.parse.urlparse(self.path)
        try:
            n = int(self.headers.get("Content-Length") or 0)
            gelen = json.loads(self.rfile.read(n).decode("utf-8")) if n else {}
        except Exception:
            return self._json({"ok": False, "mesaj": "İstek okunamadı."}, 400)

        if u.path == "/api/ayar":
            ok, mesaj = _ayar_yaz(gelen.get("anahtar"), gelen.get("deger"))
            _cache.pop("ozet", None)
            return self._json({"ok": ok, "mesaj": mesaj}, 200 if ok else 400)

        if u.path == "/api/benim_islem":
            # SANAL islem — kilit + botun gorusu kaydedilir, ama ENGELLEMEZ (kullanici karari)
            if not testbot._kilit_al(timeout_sn=30):
                return self._json({"ok": False, "mesaj": "Bot şu an bir tur koşuyor, "
                                   "kilit alınamadı. Birkaç saniye sonra dene."}, 409)
            try:
                b = benim_modul()
                ok, mesaj, pos = b.giris_ac(
                    gelen.get("sym"), gelen.get("yon"), gelen.get("tez") or "",
                    gelen.get("stop"), gelen.get("tp1"), gelen.get("tp2"))
            except Exception as e:
                ok, mesaj, pos = False, f"Hata: {str(e)[:160]}", None
            finally:
                testbot._kilit_birak()
            if ok and pos:
                g = pos.get("bot_gorusu") or {}
                _iz_yaz({"eylem": "benim_islem", "anahtar": pos["sym"], "eski": None,
                         "yeni": f"{pos['yon']} {pos['kaldirac']}x risk=${pos['risk_usdt']}",
                         "bot_karari": g.get("karar"),
                         "atlanan_vetolar": [v.get("kategori") for v in (g.get("vetolar") or [])],
                         "tez": (gelen.get("tez") or "")[:200],
                         "stop_elle": bool(pos.get("stop_elle"))})
            for k in ("benim", "karsilastirma"):
                _cache.pop(k, None)
            return self._json({"ok": ok, "mesaj": mesaj, "pozisyon": pos}, 200 if ok else 400)

        if u.path == "/api/benim_kapat":
            if not testbot._kilit_al(timeout_sn=30):
                return self._json({"ok": False, "mesaj": "Bot tur koşuyor, kilit alınamadı."}, 409)
            try:
                ok, mesaj = benim_modul().kapat(gelen.get("sym"))
            except Exception as e:
                ok, mesaj = False, f"Hata: {str(e)[:160]}"
            finally:
                testbot._kilit_birak()
            if ok:
                _iz_yaz({"eylem": "benim_kapat", "anahtar": str(gelen.get("sym")).upper(),
                         "eski": "acik", "yeni": "kapali"})
            for k in ("benim", "karsilastirma"):
                _cache.pop(k, None)
            return self._json({"ok": ok, "mesaj": mesaj}, 200 if ok else 400)

        if u.path == "/api/kontrol":
            ok, mesaj = _kontrol(gelen.get("eylem"), gelen.get("arg"))
            for k in ("ozet", "kafa", "gecmis"):
                _cache.pop(k, None)
            global _sistem_cache
            _sistem_cache = None
            return self._json({"ok": ok, "mesaj": mesaj}, 200 if ok else 400)

        self._json({"error": "not found"}, 404)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8787)
    a = ap.parse_args()
    srv = HTTPServer(("127.0.0.1", a.port), Handler)
    print(f"Panel: http://127.0.0.1:{a.port}/  (Ctrl+C ile durdur)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
