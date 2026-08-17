# -*- coding: utf-8 -*-
"""HTTP keep-alive / baglanti havuzu — dogrulama testi (2026-08-17).

Sahte YEREL sunucu kullanir: GERCEK borsaya hicbir istek gitmez, disk yazimi yok.
On-kayittaki 5 gecme olcutunden 3/4/5'i burada sinanir (1 ve 2 canli turlarla).

Kritik: yalniz mekanizma degil, DORT URETIM CAGIRANI da sinanir — cunku carpma
alani genis (evren.get'i 8 dosya cagiriyor, biri ThreadingHTTPServer'li panel).
"""
import sys, os, json, time, threading, socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
import evren

hata = 0
def kontrol(ad, kosul, detay=""):
    global hata
    print(("  OK   " if kosul else "  HATA ") + ad + ("  " + detay if detay else ""))
    if not kosul:
        hata += 1

# ---- SAHTE SUNUCU --------------------------------------------------------------
BAGLANTI = []          # her yeni TCP baglantisi icin bir kayit
ISTEK = []
MOD = {"durum": 200, "retry_after": "0"}
KILIT = threading.Lock()

class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"      # keep-alive icin SART
    def setup(self):
        super().setup()
        with KILIT:
            BAGLANTI.append(id(self.connection))
    def log_message(self, *a):
        pass
    def do_GET(self):
        with KILIT:
            ISTEK.append(self.path)
            durum = MOD["durum"]
            if MOD.get("tek_seferlik"):
                MOD["durum"] = 200
                MOD.pop("tek_seferlik")
        if durum == 429:
            self.send_response(429)
            self.send_header("Retry-After", MOD["retry_after"])
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if durum >= 400:
            self.send_response(durum)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        # klines benzeri govde (olcucu/radar parse edebilsin)
        if "klines" in self.path:
            n = 120
            g = json.dumps([[i * 3600000, "10", "11", "9", "10.5", "100", 0, "1000",
                             50, "60", "600", "0"] for i in range(n)]).encode()
        elif "premiumIndex" in self.path:
            g = json.dumps({"lastFundingRate": "-0.0011"}).encode()
        elif "openInterestHist" in self.path:
            g = json.dumps([{"sumOpenInterest": str(100 + i)} for i in range(24)]).encode()
        elif "depth" in self.path:
            g = json.dumps({"bids": [["10.0", "1000"]], "asks": [["10.1", "1000"]]}).encode()
        elif "ticker/price" in self.path:
            g = json.dumps({"price": "10.0"}).encode()
        elif "futures/data/" in self.path:
            g = json.dumps([{"longShortRatio": "1.30", "buySellRatio": "1.05"}]).encode()
        else:
            g = json.dumps({"ok": True}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(g)))
        self.end_headers()
        self.wfile.write(g)

srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
PORT = srv.server_address[1]
KOKURL = f"http://127.0.0.1:{PORT}"
threading.Thread(target=srv.serve_forever, daemon=True).start()
time.sleep(0.2)

def sifirla():
    with KILIT:
        BAGLANTI.clear(); ISTEK.clear()
        MOD["durum"] = 200; MOD["retry_after"] = "0"; MOD.pop("tek_seferlik", None)
    evren._ban_until = 0.0

print("=" * 70)
print("Havuz aktif mi:", evren._HAVUZ is not None, "| urllib3", getattr(evren._urllib3, "__version__", "-"))

print()
print("1) BAGLANTI YENIDEN KULLANILIYOR MU (isin ozu)")
sifirla()
for i in range(12):
    evren.get(f"{KOKURL}/x?i={i}")
n_bag, n_ist = len(set(BAGLANTI)), len(ISTEK)
kontrol("12 istek yapildi", n_ist == 12, f"istek={n_ist}")
kontrol("baglanti sayisi 12'den AZ (havuz calisiyor)", n_bag < 12, f"baglanti={n_bag}")
kontrol("tek baglantiya dustu", n_bag <= 2, f"baglanti={n_bag}")

print()
print("2) 429 -> Retry-After bekle, BIR KEZ tekrar (semantik korundu)")
sifirla()
with KILIT:
    MOD["durum"] = 429; MOD["retry_after"] = "0"; MOD["tek_seferlik"] = True
t0 = time.time()
d = evren.get(f"{KOKURL}/y")
kontrol("429 sonrasi basarili donus", d == {"ok": True}, str(d))
kontrol("iki istek gitti (ilk 429 + tekrar)", len(ISTEK) == 2, f"istek={len(ISTEK)}")

print()
print("3) 418 -> sogutma penceresi baslar, sonraki cagri AG'A CIKMAZ")
sifirla()
with KILIT:
    MOD["durum"] = 418
try:
    evren.get(f"{KOKURL}/z")
    kontrol("418 istisna atti", False)
except Exception:
    kontrol("418 istisna atti", True)
kontrol("_ban_until kuruldu", evren._ban_until > time.time(), f"kalan={evren._ban_until-time.time():.0f}sn")
n_once = len(ISTEK)
try:
    evren.get(f"{KOKURL}/z2")
except Exception:
    pass
kontrol("pencere icinde YENI istek gitmedi", len(ISTEK) == n_once, f"{n_once} -> {len(ISTEK)}")
evren._ban_until = 0.0

print()
print("4) BAYAT SOCKET -> tek seferlik yeniden deneme")
sifirla()
evren.get(f"{KOKURL}/isin")          # havuza baglanti koy
srv.shutdown_request  # (noop) — asil test: sunucu baglantiyi kapatirsa
# sunucu tarafini kapatmayi taklit et: havuzdaki socket'i disaridan kapat
kapatildi = 0
try:
    havuz = evren._HAVUZ.connection_from_url(KOKURL)
    while True:
        c = havuz.pool.get_nowait()
        if c is not None:
            try:
                c.close(); kapatildi += 1
            except Exception:
                pass
        havuz.pool.put(c)
        break
except Exception:
    pass
d = evren.get(f"{KOKURL}/isin2")
kontrol("bayat socket sonrasi istek BASARILI", d == {"ok": True}, f"kapatilan={kapatildi}")

print()
print("4b) TIMEOUT'ta tekrar YOK (kuyruk 2x olmamali)")
sifirla()
import urllib3 as _u3
_orij = evren._havuz_iste
_sayac = {"n": 0}
def _takilan(u, bas, timeout):
    _sayac["n"] += 1
    raise _u3.exceptions.ReadTimeoutError(None, u, "read timeout")
evren._havuz_iste = _takilan
try:
    evren.get(f"{KOKURL}/timeout")
    kontrol("timeout istisna atti", False)
except Exception:
    kontrol("timeout istisna atti", True)
kontrol("TEK deneme yapildi (2 degil)", _sayac["n"] == 1, f"deneme={_sayac['n']}")
evren._havuz_iste = _orij

_sayac2 = {"n": 0}
def _bayat(u, bas, timeout):
    _sayac2["n"] += 1
    if _sayac2["n"] == 1:
        raise _u3.exceptions.ProtocolError("connection aborted")
    return 200, b'{"ok": true}', {}
evren._havuz_iste = _bayat
d = evren.get(f"{KOKURL}/bayat")
kontrol("baglanti hatasinda TEKRAR var", _sayac2["n"] == 2 and d == {"ok": True}, f"deneme={_sayac2['n']}")
evren._havuz_iste = _orij

print()
print("5) ESZAMANLI IS PARCACIGI (panel ThreadingHTTPServer senaryosu)")
sifirla()
sonuc, hatalar = [], []
def isci(k):
    try:
        for i in range(8):
            sonuc.append(evren.get(f"{KOKURL}/t{k}-{i}"))
    except Exception as e:
        hatalar.append(repr(e))
th = [threading.Thread(target=isci, args=(k,)) for k in range(10)]
[t.start() for t in th]; [t.join() for t in th]
kontrol("80 esszamanli cagri, HATA YOK", not hatalar, str(hatalar[:2]))
kontrol("hepsi dogru govde dondu", len(sonuc) == 80 and all(x == {"ok": True} for x in sonuc), f"n={len(sonuc)}")
kontrol("baglanti sayisi cagri sayisindan AZ", len(set(BAGLANTI)) < 80, f"baglanti={len(set(BAGLANTI))}")

print()
print("6) DORT URETIM CAGIRANI sahte sunucuyla")
import radar, testbot, olcucu
sifirla()
_r, _t, _o = radar.FAPI, testbot.FAPI, olcucu.FAPI
radar.FAPI = testbot.FAPI = olcucu.FAPI = KOKURL
try:
    a = radar.analyze("TEST", 0.0)
    kontrol("radar.analyze calisti", a is not None and "score" in a, f"score={a and a.get('score')}")
    p = radar.pillar_d("TEST")
    kontrol("radar.pillar_d 3 alan dondurdu", p and p.get("top_ls") == 1.3, str(p))
    k = olcucu.fetch_klines("TEST", "1h", 100)
    kontrol("olcucu.fetch_klines calisti", isinstance(k, list) and len(k) > 50, f"n={len(k) if k else 0}")
    px = testbot.fiyat_fapi("TEST")
    kontrol("testbot.fiyat_fapi calisti", px == 10.0, str(px))
    dd = testbot.defter_derinlik("TEST", "SHORT", 100.0)
    kontrol("testbot.defter_derinlik calisti", dd is not None and dd["en_iyi"] == 10.0, str(dd and dd["en_iyi"]))
    pn = evren.get(f"{KOKURL}/panel", headers={"User-Agent": "panel/1.0"}, timeout=15)
    kontrol("panel deseni (headers+timeout) calisti", pn == {"ok": True}, str(pn))
finally:
    radar.FAPI, testbot.FAPI, olcucu.FAPI = _r, _t, _o

print()
print("7) HIZ KIYASI — havuzlu vs havuzsuz (ayni sahte sunucu)")
sifirla()
N = 40
t0 = time.time()
for i in range(N):
    evren.get(f"{KOKURL}/h{i}")
sure_havuz = time.time() - t0
_hv = evren._HAVUZ
evren._HAVUZ = None                      # eski yola dus
sifirla()
t0 = time.time()
for i in range(N):
    evren.get(f"{KOKURL}/n{i}")
sure_duz = time.time() - t0
evren._HAVUZ = _hv
print(f"     havuzlu {sure_havuz*1000/N:6.2f} ms/cagri | havuzsuz {sure_duz*1000/N:6.2f} ms/cagri"
      f" | oran {sure_duz/max(sure_havuz,1e-9):.2f}x")
kontrol("havuzlu daha hizli", sure_havuz < sure_duz, f"{sure_havuz:.3f} < {sure_duz:.3f}")
print("     (yerel sunucu — gercek kazanc TLS el sikismasi olan uzak host'ta cok daha buyuk)")

srv.shutdown()
print()
print("=" * 70)
print("gercek borsaya istek: YOK (tum trafik 127.0.0.1)")
print("diske yazim: YOK")
print(f"SONUC: {'HEPSI GECTI' if hata == 0 else str(hata) + ' HATA'}")
sys.exit(1 if hata else 0)
