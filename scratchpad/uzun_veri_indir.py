#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIKIR 3 — UZUN GECMIS VERI (2026-08-11)

NEDEN: bugun cevaplayamadigimiz her soru ayni darbogaza cikti — 60 gunluk veri.
  "Bogada calisir mi?"          -> boga yok (BTC 60 gunde +%1.1)
  "Cokus sonrasi tekrar eder mi?" -> tek cokus var (19-25 Haziran)
  "Kapilar rejim donunce bozulur mu?" -> tek rejim var
Bu betik 2 yillik 1 saatlik mum indirir; uc soruyu birden acar.

GUVENLIK:
  - AYRI dizine yazar (klines_1h_uzun/). Mevcut klines_1h/ DOKUNULMAZ,
    boylece bugune kadarki tum olcumler yeniden uretilebilir kalir.
  - Bota/config'e/deftere hicbir sey yazmaz.
  - YENIDEN BASLATILABILIR: tamamlanmis sembolu atlar (kismi dosya .tmp'de tutulur).
  - Nazik hiz: istekler arasi bekleme + 429/418'de geri cekilme.
"""
import json, os, time, sys, urllib.request, urllib.error, datetime

BURA = os.path.dirname(os.path.abspath(__file__))
KAYNAK = os.path.join(BURA, "klines_1h")
HEDEF = os.path.join(BURA, "klines_1h_uzun")
FAPI = "https://fapi.binance.com"
GERI_GUN = 730                      # 2 yil
LIMIT = 1500
BEKLE = 0.28                        # ~215 istek/dk (limit 240'in altinda)


def get(url, deneme=5):
    for k in range(deneme):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "kripto-arastirma/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 418):
                bekle = 5 * (k + 1) ** 2
                print(f"    hiz limiti ({e.code}) -> {bekle}s bekle", flush=True)
                time.sleep(bekle)
            elif e.code == 400:
                return []           # sembol yok / vade disi
            else:
                time.sleep(2 * (k + 1))
        except Exception:
            time.sleep(2 * (k + 1))
    return None


def indir(sym, bas_ms, son_ms):
    out, t = [], bas_ms
    while t < son_ms:
        u = (f"{FAPI}/fapi/v1/klines?symbol={sym}USDT&interval=1h"
             f"&startTime={t}&limit={LIMIT}")
        d = get(u)
        if d is None:
            return None
        if not d:
            break
        for k in d:
            out.append({"t": int(k[0]), "o": float(k[1]), "h": float(k[2]),
                        "l": float(k[3]), "c": float(k[4]), "v": float(k[5]),
                        "qv": float(k[7]), "n": int(k[8]), "tbv": float(k[9])})
        yeni = int(d[-1][0]) + 3600000
        if yeni <= t:
            break
        t = yeni
        time.sleep(BEKLE)
        if len(d) < LIMIT:
            break
    return out


def main():
    os.makedirs(HEDEF, exist_ok=True)
    semboller = sorted(f[:-5] for f in os.listdir(KAYNAK) if f.endswith(".json"))
    son_ms = int(time.time() * 1000)
    bas_ms = son_ms - GERI_GUN * 86400000
    print(f"UZUN VERI INDIRME — {len(semboller)} sembol · {GERI_GUN} gun "
          f"({datetime.datetime.fromtimestamp(bas_ms/1000):%Y-%m-%d} ->)", flush=True)
    print(f"Hedef: {HEDEF}  (mevcut klines_1h/ DOKUNULMUYOR)\n", flush=True)
    t0 = time.time()
    ok = atlandi = hata = 0
    for n, sym in enumerate(semboller, 1):
        yol = os.path.join(HEDEF, sym + ".json")
        if os.path.exists(yol):
            atlandi += 1
            continue
        b = indir(sym, bas_ms, son_ms)
        if b is None:
            hata += 1
            print(f"[{n}/{len(semboller)}] {sym:12} HATA", flush=True)
            continue
        if len(b) < 200:
            with open(yol, "w", encoding="utf-8") as f:
                json.dump(b, f)
            atlandi += 1
            continue
        gecici = yol + ".tmp"
        with open(gecici, "w", encoding="utf-8") as f:
            json.dump(b, f)
        os.replace(gecici, yol)
        ok += 1
        if n % 20 == 0 or n <= 3:
            gecen = time.time() - t0
            kalan = (len(semboller) - n) * gecen / n if n else 0
            ilk = datetime.datetime.fromtimestamp(b[0]["t"] / 1000)
            print(f"[{n}/{len(semboller)}] {sym:12} {len(b):6d} bar  "
                  f"({ilk:%Y-%m-%d}'den)  ·  gecen {gecen/60:.0f}dk  "
                  f"kalan ~{kalan/60:.0f}dk", flush=True)
    print(f"\nBITTI — indirilen {ok} · atlanan/kisa {atlandi} · hata {hata} "
          f"· sure {(time.time()-t0)/60:.0f} dk", flush=True)


if __name__ == "__main__":
    main()
