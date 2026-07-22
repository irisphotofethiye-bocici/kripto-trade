#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PANEL SUNUCU — TestBot canlı dashboard (2026-07-03). Sadece 127.0.0.1:8787 (dışarıya açık DEĞİL).
GET /            -> panel.html
GET /api/durum   -> {state, acik_pozisyonlar(guncel fiyat+PnL), son_islemler, equity_serisi}
GET /api/mumlar?sym=SOL&interval=15m&limit=200 -> Binance public klines proxy (CORS icin)
GET /api/sistem  -> {veto, gercek_pozisyonlar, erken_kusak, sayac} — olcum katmanlari (60s cache, 2026-07-11)
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

VETO_KATEGORILER = ("long_veto", "taker_soguma", "blowoff", "rr_veto")


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
    return {"ts": son.get("ts"), "total_t": round(son["total"] / 1e12, 3),
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
        else:
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
