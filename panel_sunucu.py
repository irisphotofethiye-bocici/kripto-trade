#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PANEL SUNUCU — TestBot canlı dashboard (2026-07-03). Sadece 127.0.0.1:8787 (dışarıya açık DEĞİL).
GET /            -> panel.html
GET /api/durum   -> {state, acik_pozisyonlar(guncel fiyat+PnL), son_islemler, equity_serisi}
GET /api/mumlar?sym=SOL&interval=15m&limit=200 -> Binance public klines proxy (CORS icin)
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
