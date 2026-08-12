#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FUNDING GECMISI INDIRICI (2026-08-12) — A+B'nin funding bacagini 2 yilda sinamak icin.

ISLETIM DERSI (2026-08-11): 2 yillik mum indirmesi ~215 istek/dk hizla kosmustu ve
botun turlarini 4 dakikalik siniri astirip 3 SAAT oldurmustu. Bu betik UCTE BIR hizla
(~66 istek/dk) gider ve her 50 sembolde botun son turunu kontrol edip gecikme varsa
kendini YAVASLATIR.

Yeniden baslatilabilir: tamamlanmis sembol atlanir.
"""
import json, os, sys, time, datetime, urllib.request, urllib.error

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURA)
KAYNAK = os.path.join(BURA, "klines_1h_uzun")
HEDEF = os.path.join(BURA, "funding_gecmis")
FAPI = "https://fapi.binance.com"
GERI_GUN = 730
BEKLE = 0.9                      # ~66 istek/dk (dun 215'ti ve bot olmustu)


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


def bot_saglikli_mi():
    """Bot son turunu ne kadar once bitirdi? Gecikme varsa indirmeyi yavaslat."""
    try:
        st = json.load(open(os.path.join(KOK, "testbot_state.json"), encoding="utf-8"))
        yas = (datetime.datetime.now()
               - datetime.datetime.strptime(st["son_cycle_ts"], "%Y-%m-%d %H:%M:%S")).total_seconds()
        return yas
    except Exception:
        return 0


def indir(sym, bas_ms, son_ms):
    out, t = [], bas_ms
    while t < son_ms:
        d = get(f"{FAPI}/fapi/v1/fundingRate?symbol={sym}USDT&startTime={t}&limit=1000")
        if d is None:
            return None
        if not d:
            break
        out += [{"t": int(x["fundingTime"]), "r": float(x["fundingRate"]) * 100} for x in d]
        yeni = int(d[-1]["fundingTime"]) + 1
        if yeni <= t:
            break
        t = yeni
        time.sleep(BEKLE)
        if len(d) < 1000:
            break
    return out


def main():
    os.makedirs(HEDEF, exist_ok=True)
    semboller = sorted(f[:-5] for f in os.listdir(KAYNAK) if f.endswith(".json"))
    son_ms = int(time.time() * 1000)
    bas_ms = son_ms - GERI_GUN * 86400000
    print(f"FUNDING INDIRME — {len(semboller)} sembol · {GERI_GUN} gun · ~66 istek/dk", flush=True)
    t0, ok, atlandi, hata = time.time(), 0, 0, 0
    for n, sym in enumerate(semboller, 1):
        yol = os.path.join(HEDEF, sym + ".json")
        if os.path.exists(yol):
            atlandi += 1
            continue
        d = indir(sym, bas_ms, son_ms)
        if d is None:
            hata += 1
            continue
        gec = yol + ".tmp"
        with open(gec, "w", encoding="utf-8") as f:
            json.dump(d, f)
        os.replace(gec, yol)
        ok += 1
        if n % 50 == 0:
            yas = bot_saglikli_mi()
            gecen = (time.time() - t0) / 60
            kalan = (len(semboller) - n) * gecen / max(n - atlandi, 1)
            print(f"[{n}/{len(semboller)}] {sym:12} {len(d):5d} kayit · gecen {gecen:.0f}dk "
                  f"· kalan ~{kalan:.0f}dk · bot son tur {yas/60:.1f}dk once", flush=True)
            if yas > 900:                      # bot 15 dk'dir tur atmadiysa
                print("    !! BOT GECIKIYOR — 60 sn duraklatiliyor", flush=True)
                time.sleep(60)
    print(f"\nBITTI — indirilen {ok} · atlanan {atlandi} · hata {hata} "
          f"· sure {(time.time()-t0)/60:.0f} dk", flush=True)


if __name__ == "__main__":
    main()
