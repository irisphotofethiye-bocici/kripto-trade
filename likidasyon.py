#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIKIDASYON — Binance forceOrder canli akisi (D2, UCRETSIZ; 2026-07-02, B-eksik #3).
Apify liq-map (ucretli, ~$0.01) HARITA (miknatis seviyeleri) icin kalir; bu script GERCEKLESEN
likidasyonlari toplar (kaskad/flush tespiti). wss://fstream.binance.com/ws/!forceOrder@arr
Saf stdlib websocket istemcisi (bagimlilik yok). --dk dakika dinler, likidasyon_log.jsonl'e ekler,
ozet basar (top semboller, LONG-liq vs SHORT-liq notional).
Kullanim: python likidasyon.py [--dk 10] [--min_usd 5000]
Yorum: LONG-liq baskin = dusus kaskadi (dip'e yakin kapitulasyon olabilir); SHORT-liq baskin = squeeze.
"""
import json, os, ssl, sys, socket, base64, struct, time, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
HOST = "fstream.binance.com"
PATH = "/ws/!forceOrder@arr"
LOGF = os.path.join(HERE, "likidasyon_log.jsonl")

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")


class Okuyucu:
    def __init__(self, sock, on=b""):
        self.s, self.buf = sock, on

    def oku(self, n):
        while len(self.buf) < n:
            c = self.s.recv(65536)
            if not c:
                raise ConnectionError("baglanti kapandi")
            self.buf += c
        out, self.buf = self.buf[:n], self.buf[n:]
        return out


def baglan(timeout=20):
    ctx = ssl.create_default_context()
    raw = socket.create_connection((HOST, 443), timeout=timeout)
    s = ctx.wrap_socket(raw, server_hostname=HOST)
    key = base64.b64encode(os.urandom(16)).decode()
    s.sendall((f"GET {PATH} HTTP/1.1\r\nHost: {HOST}\r\n"
               "Upgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
    buf = b""
    while b"\r\n\r\n" not in buf:
        c = s.recv(4096)
        if not c:
            raise ConnectionError("handshake kesildi")
        buf += c
    head, kalan = buf.split(b"\r\n\r\n", 1)
    if b" 101" not in head.split(b"\r\n")[0]:
        raise ConnectionError("upgrade reddedildi: " + head.split(b"\r\n")[0].decode(errors="replace"))
    return s, Okuyucu(s, kalan)


def cerceve_gonder(s, opcode, payload=b""):
    mask = os.urandom(4)  # istemci->sunucu MASKELI zorunlu (RFC6455)
    n = len(payload)
    h = bytes([0x80 | opcode])
    if n < 126:
        h += bytes([0x80 | n])
    elif n < 65536:
        h += bytes([0x80 | 126]) + struct.pack(">H", n)
    else:
        h += bytes([0x80 | 127]) + struct.pack(">Q", n)
    s.sendall(h + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))


def cerceve_oku(rd):
    b1, b2 = rd.oku(2)
    fin, opcode, ln = b1 & 0x80, b1 & 0x0F, b2 & 0x7F
    if ln == 126:
        ln = struct.unpack(">H", rd.oku(2))[0]
    elif ln == 127:
        ln = struct.unpack(">Q", rd.oku(8))[0]
    if b2 & 0x80:
        mask = rd.oku(4)
        data = bytes(x ^ mask[i % 4] for i, x in enumerate(rd.oku(ln)))
    else:
        data = rd.oku(ln)
    return fin, opcode, data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dk", type=float, default=10.0, help="dinleme suresi (dakika)")
    ap.add_argument("--min_usd", type=float, default=5000.0, help="log esigi (notional $)")
    a = ap.parse_args()
    try:
        s, rd = baglan()
    except Exception as e:
        print(json.dumps({"error": f"baglanti: {str(e)[:100]}"}, ensure_ascii=False)); sys.exit(1)
    s.settimeout(60)
    son = time.time() + a.dk * 60
    toplam = {}
    n_ev = 0
    parca, parca_op = b"", None
    print(f"=== LIKIDASYON dinleniyor ({a.dk:.0f} dk, esik ${a.min_usd:.0f}) ===")
    with open(LOGF, "a", encoding="utf-8") as fh:
        while time.time() < son:
            try:
                fin, op, data = cerceve_oku(rd)
            except socket.timeout:
                try:
                    cerceve_gonder(s, 0x9)  # keepalive ping (sakin piyasada olay seyrek)
                except Exception:
                    break
                continue
            except Exception:
                break
            if op == 0x9:
                cerceve_gonder(s, 0xA, data); continue   # ping -> pong
            if op == 0x8:
                break                                     # close
            if op in (0x1, 0x0):                          # text / continuation
                parca += data
                if op == 0x1:
                    parca_op = 0x1
                if not fin:
                    continue
                mesaj, parca, parca_op = parca, b"", None
                try:
                    ev = json.loads(mesaj)
                except Exception:
                    continue
                for e in (ev if isinstance(ev, list) else [ev]):
                    o = e.get("o") or {}
                    sym, side = o.get("s", ""), o.get("S", "")
                    try:
                        notional = float(o.get("q", 0)) * float(o.get("ap") or o.get("p") or 0)
                    except Exception:
                        continue
                    if not sym.endswith("USDT"):
                        continue
                    n_ev += 1
                    base = sym[:-4]
                    t = toplam.setdefault(base, {"long_liq": 0.0, "short_liq": 0.0})
                    # SELL emri = LONG pozisyon likide edildi; BUY = SHORT likide (squeeze)
                    t["long_liq" if side == "SELL" else "short_liq"] += notional
                    if notional >= a.min_usd:
                        fh.write(json.dumps({"ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                             "sym": base, "yon": ("LONG_LIQ" if side == "SELL" else "SHORT_LIQ"),
                                             "usd": round(notional), "fiyat": o.get("ap")},
                                            ensure_ascii=False) + "\n")
    try:
        s.close()
    except Exception:
        pass
    L = sum(v["long_liq"] for v in toplam.values())
    S = sum(v["short_liq"] for v in toplam.values())
    print(f"Olay: {n_ev} | LONG-liq ${L:,.0f} vs SHORT-liq ${S:,.0f} "
          f"-> {'DUSUS kaskadi agirlikli' if L > S * 1.5 else ('SQUEEZE agirlikli' if S > L * 1.5 else 'dengeli/sakin')}")
    for sym, v in sorted(toplam.items(), key=lambda kv: -(kv[1]['long_liq'] + kv[1]['short_liq']))[:10]:
        print(f"  {sym:8} long_liq=${v['long_liq']:,.0f}  short_liq=${v['short_liq']:,.0f}")
    print(f"(detay: {os.path.basename(LOGF)}; harita/miknatis seviyeleri icin apify_liq.py ayri)")


if __name__ == "__main__":
    main()
