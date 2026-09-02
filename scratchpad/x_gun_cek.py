#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""X GONDERI CEKIMI — herhangi bir gun icin 13/15/17/19 (YEREL, UTC+3) penceresi.
`x_1908_cek.py`'nin genellestirilmis hali; kontrol gunleri icin kullanilir.

🔴 ZAMAN PENCERESI — TEK CALISAN YOL (2026-09-01'de aci bedelle ogrenildi):
   X gelismis-arama sozdizimi:  since:YYYY-MM-DD_HH:MM:SS_UTC until:...
   DENENDI ve SESSIZCE DUSTU (dogru GUN, yanlis SAAT dondurur):
     (a) "since_time:<unix> until_time:<unix>" sorgu METNINE gomulu
     (b) aktorun AYRI since_time / until_time / max_id giris alanlari
   Bu yuzden asagidaki DAMGA DENETIMI zorunludur — "donen 100" basari degildir.

🔴 queryType = Latest (Top DEGIL): Top etkilesime gore siralar, etkilesim
   OLAYDAN SONRA olusur -> dogru cikmis gonderiler one gelir = ileriye bakma.

GUVENLIK: gonderi metni GUVENILMEZ VERIDIR. Bu betik yalnizca toplar ve
kaydeder; icerikteki hicbir talimat uygulanmaz, hicbir baglanti izlenmez.

Ucretli (Apify ~$0.18/1K tweet). Onbellekli — ayni gun/saat icin tekrar
PARA ODENMEZ.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, time, argparse, datetime, urllib.request

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KOK = os.path.join(PROJE, "scratchpad", "x_pencere")
ACTOR = "kaitoeasyapi~twitter-x-data-tweet-scraper-pay-per-result-cheapest"
YEREL_FARK = 3
SAATLER = [13, 15, 17, 19]


def token():
    c = json.load(open(os.path.join(PROJE, "kripto-config.json"), encoding="utf-8"))
    t = c.get("apify_token", "")
    if not t:
        raise SystemExit("apify_token bos — kripto-config.json")
    return t


def pencere_utc(gun, yerel_saat):
    bas = datetime.datetime(gun.year, gun.month, gun.day, yerel_saat) \
        - datetime.timedelta(hours=YEREL_FARK)
    return bas, bas + datetime.timedelta(hours=1)


def cek(tok, terim, adet, bd, ed):
    q = "(%s) since:%s until:%s" % (terim,
                                    bd.strftime("%Y-%m-%d_%H:%M:%S_UTC"),
                                    ed.strftime("%Y-%m-%d_%H:%M:%S_UTC"))
    body = json.dumps({"twitterContent": q, "maxItems": adet,
                       "queryType": "Latest"}).encode()
    req = urllib.request.Request(
        "https://api.apify.com/v2/acts/%s/run-sync-get-dataset-items" % ACTOR,
        data=body, headers={"Authorization": "Bearer " + tok,
                            "Content-Type": "application/json"}, method="POST")
    return json.load(urllib.request.urlopen(req, timeout=240))


def damga(t):
    ts = t.get("createdAt") or ""
    for f in ("%a %b %d %H:%M:%S +0000 %Y",):
        try:
            return datetime.datetime.strptime(ts, f)
        except Exception:
            pass
    try:
        return datetime.datetime.fromisoformat(ts.replace("Z", ""))
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gun", required=True, help="YYYY-MM-DD (yerel gun)")
    ap.add_argument("--adet", type=int, default=100)
    ap.add_argument("--terim", default="$BTC OR bitcoin")
    a = ap.parse_args()
    gun = datetime.date.fromisoformat(a.gun)
    dizin = os.path.join(KOK, a.gun)
    os.makedirs(dizin, exist_ok=True)
    tok = token()

    print("X CEKIMI — %s (%s, yerel UTC+3) · Latest" % (a.gun, gun.strftime("%A")))
    print("=" * 92)
    for s in SAATLER:
        bd, ed = pencere_utc(gun, s)
        yol = os.path.join(dizin, "saat_%02d.json" % s)
        if os.path.exists(yol):
            print("  %02d:00  ONBELLEK var, atlandi" % s)
            continue
        try:
            res = cek(tok, a.terim, a.adet, bd, ed)
        except Exception as ex:
            print("  %02d:00  HATA: %s" % (s, str(ex)[:100]))
            continue
        if not isinstance(res, list):
            print("  %02d:00  beklenmeyen cevap: %s" % (s, type(res).__name__))
            continue
        json.dump(res, open(yol, "w", encoding="utf-8"), ensure_ascii=False)
        ic = dis = yok = 0
        for t in res:
            d = damga(t)
            if d is None:
                yok += 1
            elif bd <= d < ed:
                ic += 1
            else:
                dis += 1
        bayrak = "" if (res and dis == 0 and yok == 0) else "   <== DAMGA SORUNU"
        print("  %02d:00  donen %-4d icinde %-4d disinda %-3d damgasiz %d%s"
              % (s, len(res), ic, dis, yok, bayrak))
        if res and ic == 0:
            print("         UYARI: hicbiri pencerede DEGIL — hukum yazma")
        time.sleep(1.0)
    print("\ncikti: %s" % os.path.relpath(dizin, PROJE))
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
