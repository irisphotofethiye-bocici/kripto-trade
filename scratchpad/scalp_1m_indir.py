#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SCALP ICIN 1 DAKIKALIK VERI — rejime esit bolunmus ornek (2026-08-12)

NEDEN BOYLE: kullanici hakli olarak "6 ay esit sinama olmaz, ayi sadece" dedi.
Son 6 ay 2026-02'den beri ayi/notr; boga 2024-09 -> 2025-01'de. Toplu 15dk indirmek
ya taraflı olur ya da 2 yil x 566 sembol = ~27.000 istek / ~7 saat.

COZUM: toplu veri yerine HER SINYALIN ETRAFINDAN 1 DAKIKALIK bar cek.
  - sinyal basina TEK istek (240 bar = 4 saat, limit 260 marjla)
  - ornek REJIME ESIT bolunur (BOGA / NOTR / AYI ayni sayida)
  - 1 dakikalik = MAKSIMUM cozunurluk -> "hedef mi stop mu once" sorusu TAM cevaplanir

Bu, 1 saatlik olcumdeki tek kapanmamis soruyu kapatir: orada bar icinde sira
bilinmedigi icin KOTUMSER varsayimla hep STOP sayilmisti (alt sinir).

Yeniden baslatilabilir. Hiz ~66 istek/dk (bot izlenir).
"""
import json, os, sys, time, random, datetime, urllib.request, urllib.error, bisect, collections

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURA)
KLINE = os.path.join(BURA, "klines_1h_uzun")
FUND = os.path.join(BURA, "funding_gecmis")
HEDEF_DIR = os.path.join(BURA, "scalp_1m")
FAPI = "https://fapi.binance.com"
BEKLE = 0.9
HER_HUCRE = 500                 # kapi x rejim basina ornek
UFUK_DK = 240                   # 4 saat
ISINMA, SEYRELT, MIN_VOL = 220, 24, 3_000_000
FUND_ESIK, PUMP, MA50_ESIK, UCUZ = -0.05, 20.0, 3.72, 0.07
random.seed(59)


def get(url, deneme=4):
    for k in range(deneme):
        try:
            r = urllib.request.Request(url, headers={"User-Agent": "kripto-arastirma/1.0"})
            with urllib.request.urlopen(r, timeout=25) as f:
                return json.loads(f.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 418):
                b = 10 * (k + 1) ** 2
                print(f"    hiz limiti ({e.code}) -> {b}s", flush=True)
                time.sleep(b)
            elif e.code == 400:
                return []
            else:
                time.sleep(2 * (k + 1))
        except Exception:
            time.sleep(2 * (k + 1))
    return None


def ma(v, n):
    out, s = [None] * len(v), 0.0
    for i, x in enumerate(v):
        s += x
        if i >= n:
            s -= v[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def btc_rejim():
    b = json.load(open(os.path.join(KLINE, "BTC.json"), encoding="utf-8"))
    c = [x["c"] for x in b]
    pen, out = 720, {}
    for i in range(pen, len(b)):
        g = (c[i] / c[i - pen] - 1) * 100
        out[b[i]["t"] // 3600000] = "BOGA" if g >= 15 else ("AYI" if g <= -15 else "NOTR")
    return out


def sinyalleri_bul(rej):
    kume = collections.defaultdict(list)
    dosyalar = sorted(f for f in os.listdir(KLINE) if f.endswith(".json"))
    for n, f in enumerate(dosyalar, 1):
        if f == "BTC.json":
            continue
        sym = f[:-5]
        try:
            b = json.load(open(os.path.join(KLINE, f), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ISINMA + 60:
            continue
        c = [x["c"] for x in b]
        qv = [x.get("qv", 0.0) for x in b]
        m50 = ma(c, 50)
        fy = os.path.join(FUND, sym + ".json")
        fr = json.load(open(fy, encoding="utf-8")) if os.path.exists(fy) else []
        ft = [x["t"] for x in fr]
        son = collections.defaultdict(lambda: -10 ** 9)
        for i in range(ISINMA, len(b) - 6):
            if c[i - 24] <= 0 or sum(qv[i - 23:i + 1]) < MIN_VOL:
                continue
            if (c[i] / c[i - 24] - 1) * 100 >= PUMP:
                continue
            r = rej.get(b[i]["t"] // 3600000)
            if not r:
                continue
            # giris = SONRAKI barin acilisi -> 1m verisi o barin basindan baslar
            giris_ms = b[i + 1]["t"]
            if fr:
                k = bisect.bisect_right(ft, b[i]["t"]) - 1
                if k >= 0 and fr[k]["r"] <= FUND_ESIK and i - son["A+B"] >= SEYRELT:
                    son["A+B"] = i
                    kume[("A+B", r)].append((sym, giris_ms))
            if m50[i] and c[i] <= UCUZ and (c[i] / m50[i] - 1) * 100 >= MA50_ESIK \
                    and i - son["MA50"] >= SEYRELT:
                son["MA50"] = i
                kume[("MA50", r)].append((sym, giris_ms))
        for _ in range(max(1, (len(b) - ISINMA) // 900)):
            i = random.randint(ISINMA, len(b) - 7)
            if sum(qv[i - 23:i + 1]) < MIN_VOL:
                continue
            r = rej.get(b[i]["t"] // 3600000)
            if r:
                kume[("KONTROL", r)].append((sym, b[i + 1]["t"]))
        if n % 150 == 0:
            print(f"  sinyal taramasi {n}/{len(dosyalar)} ...", flush=True)
    return kume


def bot_yasi():
    try:
        st = json.load(open(os.path.join(KOK, "testbot_state.json"), encoding="utf-8"))
        return (datetime.datetime.now()
                - datetime.datetime.strptime(st["son_cycle_ts"], "%Y-%m-%d %H:%M:%S")).total_seconds()
    except Exception:
        return 0


def main():
    os.makedirs(HEDEF_DIR, exist_ok=True)
    print("Rejim ve sinyaller hazirlaniyor...", flush=True)
    rej = btc_rejim()
    kume = sinyalleri_bul(rej)
    print("\nBULUNAN SINYALLER (kapi x rejim):", flush=True)
    secim = []
    for kapi in ("A+B", "MA50", "KONTROL"):
        for r in ("BOGA", "NOTR", "AYI"):
            v = kume.get((kapi, r), [])
            n = min(len(v), HER_HUCRE)
            orn = random.sample(v, n) if n else []
            print(f"  {kapi:8} {r:5} mevcut {len(v):6d} -> ornek {n:4d}", flush=True)
            for sym, ms in orn:
                secim.append({"kapi": kapi, "rejim": r, "sym": sym, "giris_ms": ms})
    print(f"\nTOPLAM {len(secim)} istek · ~{len(secim)*BEKLE/60:.0f} dk", flush=True)

    yol = os.path.join(HEDEF_DIR, "ornekler.json")
    tamam = {}
    if os.path.exists(yol):
        tamam = {f"{x['sym']}_{x['giris_ms']}": x for x in json.load(open(yol, encoding="utf-8"))}
        print(f"  ({len(tamam)} kayit zaten var, atlanacak)", flush=True)
    t0, ok = time.time(), 0
    for n, s in enumerate(secim, 1):
        anahtar = f"{s['sym']}_{s['giris_ms']}"
        if anahtar in tamam:
            continue
        d = get(f"{FAPI}/fapi/v1/klines?symbol={s['sym']}USDT&interval=1m"
                f"&startTime={s['giris_ms']}&limit={UFUK_DK + 20}")
        if d:
            s["bars"] = [{"t": int(x[0]), "o": float(x[1]), "h": float(x[2]),
                          "l": float(x[3]), "c": float(x[4])} for x in d]
            tamam[anahtar] = s
            ok += 1
        time.sleep(BEKLE)
        if n % 200 == 0:
            with open(yol, "w", encoding="utf-8") as f:
                json.dump(list(tamam.values()), f)
            gecen = (time.time() - t0) / 60
            print(f"[{n}/{len(secim)}] gecen {gecen:.0f}dk · kalan ~{gecen*(len(secim)-n)/max(n,1):.0f}dk"
                  f" · bot son tur {bot_yasi()/60:.1f}dk once", flush=True)
            if bot_yasi() > 900:
                print("    !! BOT GECIKIYOR — 60 sn duraklat", flush=True)
                time.sleep(60)
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(list(tamam.values()), f)
    print(f"\nBITTI — {ok} yeni · toplam {len(tamam)} · {(time.time()-t0)/60:.0f} dk", flush=True)


if __name__ == "__main__":
    main()
