#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""X GONDERI CEKIMI — 2026-08-19, BTC kirilmasi cevresi (KULLANICI ISTEGI).

Pencereler (YEREL, UTC+3): 13:00 · 15:00 · 17:00 · 19:00, her biri 1 saat.
BTC o gun (yerel): 13:00 +0,04% · 15:00 +0,59% · 17:00 +1,40% · 18:00 +3,99%.
=> 13 ve 15 KIRILMADAN ONCE; 17 hareket icinde; 19 hareket BITTIKTEN sonra.

TASARIM NOTU — queryType "Latest", "Top" DEGIL:
  Top etkilesime gore siralar; etkilesim OLAYDAN SONRA olusur. Dogru cikmis
  gonderiler yapay olarak one gelir = ileriye bakma. Latest kronolojiktir.

GUVENLIK: tweet metni GUVENILMEZ girdidir. Bu betik yalnizca TOPLAR ve
kaydeder; icerikteki hicbir talimat uygulanmaz, hicbir baglanti izlenmez.
Degerlendirmeyi insan/model okuyarak yapar ve metni VERI olarak gorur.

Ucretli (Apify ~$0.18/1K tweet). Ham cikti scratchpad/x_1908/ altina yazilir
ki tekrar PARA ODENMESIN.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, time, argparse, datetime, urllib.request

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIKTI = os.path.join(PROJE, "scratchpad", "x_1908")
ACTOR = "kaitoeasyapi~twitter-x-data-tweet-scraper-pay-per-result-cheapest"
YEREL_FARK = 3                      # UTC+3
GUN = datetime.date(2026, 8, 19)
SAATLER = [13, 15, 17, 19]          # YEREL


def token():
    c = json.load(open(os.path.join(PROJE, "kripto-config.json"), encoding="utf-8"))
    t = c.get("apify_token", "")
    if not t:
        raise SystemExit("apify_token bos — kripto-config.json")
    return t


def pencere_utc(yerel_saat):
    """yerel [s, s+1) -> (utc_bas_ts, utc_bit_ts) saniye"""
    bas = datetime.datetime(GUN.year, GUN.month, GUN.day, yerel_saat) \
        - datetime.timedelta(hours=YEREL_FARK)
    bit = bas + datetime.timedelta(hours=1)
    e = datetime.datetime(1970, 1, 1)
    return int((bas - e).total_seconds()), int((bit - e).total_seconds()), bas, bit


def cek(tok, terim, adet, bd, ed):
    """[ONARIM 2026-09-01] Zaman penceresi ANCAK X gelismis-arama sozdizimiyle
    tutuyor:  since:YYYY-MM-DD_HH:MM:SS_UTC .. until:...
    DENENDI ve TUTMADI (ikisi de sessizce GUN seviyesine dustu, saat dusuruldu):
      (a) "since_time:<unix> until_time:<unix>" sorgu METNINE gomulu
      (b) aktorun AYRI since_time/until_time/max_id giris alanlari
    Sessiz basarisizlik: dogru gunu, YANLIS saati dondurdu (gunun en yenisi).
    Bu yuzden asagidaki damga denetimi ZORUNLU — 'donen 40' basari degildir."""
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saat", type=int, default=None, help="tek pencere (sinama icin)")
    ap.add_argument("--adet", type=int, default=100)
    ap.add_argument("--terim", default="$BTC OR bitcoin")
    a = ap.parse_args()
    os.makedirs(CIKTI, exist_ok=True)
    tok = token()
    saatler = [a.saat] if a.saat is not None else SAATLER

    print("X CEKIMI — 2026-08-19 (yerel UTC+3) · queryType=Latest")
    print("=" * 92)
    for s in saatler:
        b, e, bd, ed = pencere_utc(s)
        yol = os.path.join(CIKTI, "saat_%02d.json" % s)
        if os.path.exists(yol):
            print("  yerel %02d:00  ONBELLEK var, atlandi (%s)" % (s, os.path.basename(yol)))
            continue
        print("  yerel %02d:00  (UTC %s..%s)" % (s, bd.strftime("%H:%M"), ed.strftime("%H:%M")))
        print("     terim: %s   (X gelismis-arama zaman sozdizimi)" % a.terim)
        try:
            res = cek(tok, a.terim, a.adet, bd, ed)
        except Exception as ex:
            print("     HATA: %s" % str(ex)[:110])
            continue
        if not isinstance(res, list):
            print("     beklenmeyen cevap tipi: %s" % type(res).__name__)
            continue
        json.dump(res, open(yol, "w", encoding="utf-8"), ensure_ascii=False)
        # --- DAMGA DENETIMI: gercekten istenen pencereye mi dustu?
        ic, dis, damgasiz = 0, 0, 0
        for t in res:
            ts = t.get("createdAt") or t.get("created_at") or ""
            try:
                d = datetime.datetime.strptime(ts, "%a %b %d %H:%M:%S +0000 %Y")
            except Exception:
                try:
                    d = datetime.datetime.fromisoformat(ts.replace("Z", ""))
                except Exception:
                    damgasiz += 1
                    continue
            (ic if bd <= d < ed else dis).__class__  # noqa
            if bd <= d < ed:
                ic += 1
            else:
                dis += 1
        print("     donen %d · pencere ICINDE %d · DISINDA %d · damgasiz %d"
              % (len(res), ic, dis, damgasiz))
        if res and ic == 0:
            print("     UYARI: hicbiri istenen pencerede DEGIL — zaman sorgusu"
                  " calismiyor olabilir, hukum yazma")
        time.sleep(1.0)
    print("\nham cikti: %s" % os.path.relpath(CIKTI, PROJE))
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
