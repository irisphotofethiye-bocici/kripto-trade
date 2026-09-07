#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BINANCE forceOrder AKISI HALA OLU MU? (2026-09-07 yeniden olcum)

CLAUDE.md/durum kaydi: "2026-07-23: OLU — bolge-engelli, 0 olay".
O kayit 6 hafta once. Bu proje "sayi tekrarlanmaz, sayilir" diyor -> yeniden olculuyor.

Uc ayri sinama:
  1) TCP/TLS baglanti kuruluyor mu
  2) websocket handshake 101 donuyor mu
  3) N saniyede kac forceOrder olayi geliyor  (KIYAS: ayni anda Coinalyze ne diyor)

SALT-OKUNUR. Hicbir dosyaya yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, socket, ssl, base64, struct, time, datetime as dt
import urllib.request, urllib.parse

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOST = "fstream.binance.com"
PATH = "/ws/!forceOrder@arr"
import sys as _a
DINLE = int(_a.argv[1]) if len(_a.argv) > 1 else 90   # saniye


def cerceve_oku(s, buf):
    """Tek websocket cercevesi. -> (payload, kalan_buf) ya da (None, buf)."""
    while len(buf) < 2:
        d = s.recv(4096)
        if not d:
            return None, buf
        buf += d
    b1, b2 = buf[0], buf[1]
    ln = b2 & 0x7F
    i = 2
    if ln == 126:
        while len(buf) < 4:
            buf += s.recv(4096)
        ln = struct.unpack(">H", buf[2:4])[0]
        i = 4
    elif ln == 127:
        while len(buf) < 10:
            buf += s.recv(4096)
        ln = struct.unpack(">Q", buf[2:10])[0]
        i = 10
    while len(buf) < i + ln:
        d = s.recv(65536)
        if not d:
            return None, buf
        buf += d
    yuk = buf[i:i + ln]
    return (b1 & 0x0F, yuk), buf[i + ln:]


def main():
    print("=" * 92)
    print("BINANCE forceOrder — HALA OLU MU? (yeniden olcum %s)"
          % dt.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("kayit: 2026-07-23 'OLU, bolge-engelli, 0 olay' — tekrarlanmiyor, OLCULUYOR")
    print("=" * 92)

    print("\n### 1) TCP/TLS")
    t0 = time.time()
    try:
        ham = socket.create_connection((HOST, 443), timeout=15)
        s = ssl.create_default_context().wrap_socket(ham, server_hostname=HOST)
        print("   BAGLANDI  %s:443  (%.2f sn)" % (HOST, time.time() - t0))
    except Exception as e:
        print("   🔴 BAGLANAMADI: %s" % str(e)[:120])
        print("   -> bolge engeli TCP/TLS seviyesinde")
        return

    print("\n### 2) WEBSOCKET HANDSHAKE")
    anahtar = base64.b64encode(os.urandom(16)).decode()
    istek = ("GET %s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\n"
             "Connection: Upgrade\r\nSec-WebSocket-Key: %s\r\n"
             "Sec-WebSocket-Version: 13\r\nUser-Agent: Mozilla/5.0\r\n\r\n"
             % (PATH, HOST, anahtar))
    s.sendall(istek.encode())
    s.settimeout(15)
    yanit = b""
    try:
        while b"\r\n\r\n" not in yanit:
            d = s.recv(4096)
            if not d:
                break
            yanit += d
    except Exception as e:
        print("   🔴 yanit alinamadi: %s" % str(e)[:80])
        return
    ilk = yanit.split(b"\r\n")[0].decode("utf-8", "replace")
    print("   %s" % ilk)
    if b"101" not in yanit.split(b"\r\n")[0]:
        print("   🔴 HANDSHAKE REDDEDILDI -> akis kapali")
        print("   tam yanit: %s" % yanit[:300].decode("utf-8", "replace"))
        return
    print("   -> handshake OK, akis ACIK")

    print("\n### 3) %d SANIYE DINLE" % DINLE)
    buf = yanit.split(b"\r\n\r\n", 1)[1] if b"\r\n\r\n" in yanit else b""
    s.settimeout(5)
    bas = time.time()
    olay, sembol, uzun, kisa = 0, {}, 0.0, 0.0
    ping = 0
    while time.time() - bas < DINLE:
        try:
            r, buf = cerceve_oku(s, buf)
        except socket.timeout:
            continue
        except Exception:
            break
        if r is None:
            print("   akis kapandi")
            break
        op, yuk = r
        if op == 9:          # ping -> pong
            ping += 1
            s.sendall(b"\x8a" + bytes([len(yuk) | 0x80]) + b"\x00\x00\x00\x00" + yuk)
            continue
        if op != 1:
            continue
        try:
            m = json.loads(yuk.decode("utf-8"))
        except Exception:
            continue
        o = m.get("o") or {}
        if not o:
            continue
        olay += 1
        sym = o.get("s", "?")
        usd = float(o.get("ap") or o.get("p") or 0) * float(o.get("q") or 0)
        sembol[sym] = sembol.get(sym, 0.0) + usd
        if o.get("S") == "SELL":
            uzun += usd          # SELL emri = LONG likidasyonu
        else:
            kisa += usd
        if olay <= 5:
            print("      olay %d: %-12s %-4s %10.0f $  %s"
                  % (olay, sym, o.get("S"), usd,
                     dt.datetime.now().strftime("%H:%M:%S")))

    gecen = time.time() - bas
    print("\n   %d saniyede %d olay · ping %d" % (gecen, olay, ping))
    if olay:
        print("   LONG-liq %.0f $ · SHORT-liq %.0f $" % (uzun, kisa))
        top = sorted(sembol.items(), key=lambda z: -z[1])[:5]
        print("   en buyuk: %s" % ", ".join("%s %.0f$" % (k, v) for k, v in top))
    try:
        s.close()
    except Exception:
        pass

    print("\n### 4) KIYAS — ayni saatte Coinalyze ne diyor?")
    try:
        key = (json.load(io.open(os.path.join(KOK, "kripto-config.json"),
                                 encoding="utf-8")).get("coinalyze_api_key") or "").strip()
        simdi = int(time.time())
        u = ("https://api.coinalyze.net/v1/liquidation-history?"
             + urllib.parse.urlencode({"symbols": "BTCUSDT_PERP.A", "interval": "1hour",
                                       "convert_to_usd": "true",
                                       "from": simdi - 7200, "to": simdi}))
        rq = urllib.request.Request(u, headers={"api_key": key, "User-Agent": "x"})
        d = json.loads(urllib.request.urlopen(rq, timeout=25).read().decode())
        for x in (d[0].get("history") or [])[-2:]:
            print("      %s  BTC long-liq %.0f $ · short-liq %.0f $"
                  % (dt.datetime.fromtimestamp(x["t"], dt.timezone.utc).strftime("%H:%M UTC"),
                     x.get("l", 0), x.get("s", 0)))
        print("   -> Coinalyze BTC'de likidasyon GORUYOR mu, akis gormuyor mu: kiyas budur")
    except Exception as e:
        print("   kiyas alinamadi: %s" % str(e)[:80])

    print("\n" + "=" * 92)
    print("Hicbir dosyaya yazim: YOK")


if __name__ == "__main__":
    main()
