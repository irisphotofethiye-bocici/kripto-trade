#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COINALYZE LIKIDASYON GECMISI — INDIRICI

Ucretsiz uc (40 cagri/dk, 10 sembol/istek). Apify KULLANILMIYOR.

🔴 CLAUDE.md: indirici BIRLESTIRIR, EZMEZ, sonuc kisalirsa HATA firlatir.
Bot dosyalarina ve arsiv/coinalyze_liq_log.jsonl'e yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, sys, time, datetime as dt
import urllib.request, urllib.parse, urllib.error

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURA))
VERI = os.path.join(BURA, "veri")
os.makedirs(VERI, exist_ok=True)
BASE = "https://api.coinalyze.net/v1"
GRUP = 10
BEKLE = 4.0          # olculdu: 1,8 sn 429 uretti (Retry-After 45 sn)
GUN = 90             # ucretsiz katman zaten ~67 gunde kesiyor


def _key():
    k = (json.load(io.open(os.path.join(KOK, "kripto-config.json"),
                           encoding="utf-8")).get("coinalyze_api_key") or "").strip()
    if not k:
        sys.exit("coinalyze_api_key BOS")
    return k


def get(path, params, deneme=0):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"api_key": _key(),
                                               "User-Agent": "kripto-liq/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.loads(r.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        if e.code == 429 and deneme < 5:
            # Retry-After ONDALIK gelebiliyor ("45.503") -> int() patliyordu
            try:
                bek = float(e.headers.get("Retry-After") or 5)
            except Exception:
                bek = 5.0
            print("      [429] %.0f sn bekleniyor" % bek)
            time.sleep(bek + 2)
            return get(path, params, deneme + 1)
        return None, "HTTP %d" % e.code
    except Exception as e:
        if deneme < 2:
            time.sleep(3)
            return get(path, params, deneme + 1)
        return None, str(e)[:100]


def kaydet(sym, yeni):
    """BIRLESTIR + KISALMA SINAMASI."""
    yol = os.path.join(VERI, "%s.json" % sym)
    var = {}
    if os.path.exists(yol):
        try:
            for x in json.load(open(yol)):
                var[x["t"]] = x
        except Exception:
            var = {}
    n0 = len(var)
    for x in yeni:
        var.setdefault(x["t"], x)
    birlesik = sorted(var.values(), key=lambda z: z["t"])
    if len(birlesik) < n0:
        raise RuntimeError("KISALDI: %s (%d -> %d)" % (sym, n0, len(birlesik)))
    if len(birlesik) == n0:
        return 0
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(birlesik, f, separators=(",", ":"))
    os.replace(tmp, yol)
    return len(birlesik) - n0


def main():
    sem = json.load(io.open(os.path.join(BURA, "semboller.json"), encoding="utf-8"))
    print("=" * 88)
    print("COINALYZE LIKIDASYON GECMISI — %d sembol · %d/istek · interval 1hour" % (len(sem), GRUP))
    print("BIRLESTIRIR, EZMEZ · kisalirsa HATA")
    print("=" * 88)
    frm = int((dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=GUN)).timestamp())
    to = int(time.time())
    ek = 0
    bulunan, bos, hata = 0, 0, 0
    for i in range(0, len(sem), GRUP):
        blok = sem[i:i + GRUP]
        gruplar = ",".join("%sUSDT_PERP.A" % s for s in blok)
        d, err = get("/liquidation-history",
                     {"symbols": gruplar, "interval": "1hour",
                      "convert_to_usd": "true", "from": frm, "to": to})
        if err:
            hata += len(blok)
            print("   [%3d/%3d] HATA %s" % (i + len(blok), len(sem), err))
            time.sleep(BEKLE)
            continue
        gelen = set()
        for seri in (d or []):
            s = seri.get("symbol", "").replace("USDT_PERP.A", "")
            h = seri.get("history") or []
            if not h:
                continue
            gelen.add(s)
            ek += kaydet(s, h)
            bulunan += 1
        bos += len(blok) - len(gelen)
        if (i // GRUP) % 8 == 0:
            print("   [%3d/%3d] bulunan %d · bos %d · hata %d · +%d kayit"
                  % (i + len(blok), len(sem), bulunan, bos, hata, ek))
        time.sleep(BEKLE)

    print()
    print("=" * 88)
    dosya = [x for x in os.listdir(VERI) if x.endswith(".json")]
    print("   sembol dosyasi %d · toplam yeni kayit %d" % (len(dosya), ek))
    print("   veri yok/hata : bos %d · hata %d" % (bos, hata))
    if dosya:
        ornek = json.load(open(os.path.join(VERI, dosya[0])))
        t0 = dt.datetime.fromtimestamp(ornek[0]["t"], dt.timezone.utc)
        t1 = dt.datetime.fromtimestamp(ornek[-1]["t"], dt.timezone.utc)
        print("   ornek %s: N=%d  %s .. %s"
              % (dosya[0][:-5], len(ornek), t0.strftime("%Y-%m-%d"), t1.strftime("%Y-%m-%d")))
    print("   kisalan dosya: YOK (kisalsaydi hata firlatilirdi)")
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
