#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COINGECKO — TOTAL / USDT.D / BTC.D tarihsel serisi (365 gun).

KULLANICI ONAYI: 2026-08-21 "tamam cek ve bak".

NEDEN GEREKLI: kullanicinin onerdigi rejim gostergeleri (USDT.D, TOTAL) bizim
2 yillik perp verimizden KURULAMIYOR (stablecoin arzi ve tarihsel mcap yok).
piyasa_yapisi_log onlari tutuyor ama 2026-06-26'dan beri, 107 kayit.

UC SINIRI (olculdu):
  /global/market_cap_chart  -> HTTP 401, UCRETLI katman
  /coins/{id}/market_chart  -> demo anahtarla OK, AZAMI 365 GUN (366 -> 401)
Bu yuzden TOTAL, top-N coinin mcap'lerinin TOPLAMI olarak kurulur (top 100
kripto mcap'inin ~%95'ini kapsar; yaklasiklik RAPOR EDILIR).

Ucretli cagri YOK — demo anahtar, ucretsiz katman. Sinir: ~30 cagri/dk.
SALT scratchpad/gecko/ altina yazar.
"""
import os, sys, json, time, datetime, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(HERE)
CIKTI = os.path.join(HERE, "gecko")
os.makedirs(CIKTI, exist_ok=True)
B = "https://api.coingecko.com/api/v3"
GUN = 365
BEKLE = 2.6           # demo katman ~30 cagri/dk

with open(os.path.join(PROJE, "kripto-config.json"), encoding="utf-8") as f:
    KEY = json.load(f).get("coingecko_demo_key", "")


def cek(u, deneme=3):
    req = urllib.request.Request(u, headers={"x-cg-demo-api-key": KEY,
                                             "accept": "application/json"})
    for k in range(deneme):
        try:
            return json.load(urllib.request.urlopen(req, timeout=30))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(20 * (k + 1))
                continue
            return None
        except Exception:
            time.sleep(3)
    return None


def top_coinler(n=100):
    yol = os.path.join(CIKTI, "_top.json")
    if os.path.exists(yol):
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    out = []
    for sayfa in (1, 2):
        d = cek("%s/coins/markets?vs_currency=usd&order=market_cap_desc"
                "&per_page=100&page=%d" % (B, sayfa))
        if not d:
            break
        out += [{"id": x["id"], "sym": x["symbol"].upper(),
                 "mcap": x.get("market_cap") or 0} for x in d]
        time.sleep(BEKLE)
    out = out[:n]
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(out, f)
    return out


def mcap_gecmis(cid):
    yol = os.path.join(CIKTI, "%s.json" % cid)
    if os.path.exists(yol):
        try:
            with open(yol, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    d = cek("%s/coins/%s/market_chart?vs_currency=usd&days=%d&interval=daily"
            % (B, cid, GUN))
    if not d or "market_caps" not in d:
        return None
    out = {}
    for t, m in d["market_caps"]:
        out[datetime.datetime.fromtimestamp(t / 1000).strftime("%Y-%m-%d")] = m
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f)
    os.replace(tmp, yol)
    return out


if __name__ == "__main__":
    top = top_coinler(100)
    print("top %d coin alindi (kapsam: mcap toplaminin ~%%95'i)" % len(top))
    kapsam = sum(x["mcap"] for x in top)
    print("anlik toplam (top100): %.3f T$" % (kapsam / 1e12))
    n_yeni = 0
    for i, c in enumerate(top, 1):
        yol = os.path.join(CIKTI, "%s.json" % c["id"])
        vardi = os.path.exists(yol)
        d = mcap_gecmis(c["id"])
        if not vardi:
            n_yeni += 1
            time.sleep(BEKLE)
        print("  [%3d/%3d] %-22s %-6s %s"
              % (i, len(top), c["id"], c["sym"],
                 "%d gun" % len(d) if d else "ALINAMADI"))
        sys.stdout.flush()
    print("\nyeni indirilen: %d · dizin: %s" % (n_yeni, CIKTI))
    print("bot dosyalarina yazim: YOK")
