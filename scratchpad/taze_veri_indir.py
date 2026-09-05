#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TAZE VERI INDIRICI — 1h mum + fonlama, 2026-08-20 -> bugun (2026-09-05)

KULLANICI ONAYI: "tamam yap. eldeki veriyi ezme ama"

🔴 EZME GUVENCESI — UC KATMAN:
  1. AYRI DIZINE yazar: taze_1h/ ve taze_funding/.
     klines_1h_uzun/ · funding_gecmis/ · perp_seri/ HIC ACILMAZ (okuma bile yok,
     yalniz sembol ADLARI icin klines_1h_uzun listelenir).
  2. Kendi dizinindeki dosyaya bile EZMEZ: var olani okur, zaman damgasina gore
     BIRLESTIRIR (perp_seri_indir.py:sembol_indir deseni — CLAUDE.md zorunlu kilar).
  3. Sonuc eskisinden KISAysa HATA firlatir ve dosyaya dokunmaz.

NAZIK HIZ: 0.9 sn/istek (~66/dk). Ders (2026-08-11): 215/dk hizla inen bir betik
  botun turlarini 4 dakikalik siniri astirip 3 SAAT oldurmustu. Ayrica her 25
  sembolde botun son turu denetlenir; gecikme varsa indirme YAVASLAR.

Bot dosyalarina yazim: YOK. Sadece iki YENI dizin olusur.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, time, datetime, urllib.request, urllib.error

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURA)
SEMBOL_KAYNAK = os.path.join(BURA, "klines_1h_uzun")     # YALNIZ listelenir
HEDEF_KLINE = os.path.join(BURA, "taze_1h")
HEDEF_FUND = os.path.join(BURA, "taze_funding")
FAPI = "https://fapi.binance.com"

BAS = "2026-08-20"          # klines_1h_uzun 08-25'te bitiyor -> 5 gun tampon
BEKLE = 0.9                 # ~66 istek/dk
BOT_ESIK_SN = 600           # botun son turu bundan eskiyse yavasla


def get(url, deneme=4):
    for k in range(deneme):
        try:
            r = urllib.request.Request(url, headers={"User-Agent": "kripto-arastirma/1.0"})
            with urllib.request.urlopen(r, timeout=25) as f:
                return json.loads(f.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 418):
                b = 10 * (k + 1) ** 2
                print("    hiz limiti (%d) -> %ds bekle" % (e.code, b), flush=True)
                time.sleep(b)
            elif e.code == 400:
                return []
            else:
                time.sleep(2 * (k + 1))
        except Exception:
            time.sleep(2 * (k + 1))
    return None


def bot_yasi():
    """Botun son turu kac saniye once bitti? Okunamazsa 0."""
    try:
        st = json.load(open(os.path.join(KOK, "testbot_state.json"), encoding="utf-8"))
        return (datetime.datetime.now() - datetime.datetime.strptime(
            st["son_cycle_ts"], "%Y-%m-%d %H:%M:%S")).total_seconds()
    except Exception:
        return 0


def guvenli_yaz(yol, yeni, zaman_alani):
    """🔴 EZMEZ. Var olani okur, damgaya gore birlestirir, KISALIRSA hata firlatir.
    -> (yazilan_kayit, eski_kayit)"""
    birlesik, eski_n = {}, 0
    if os.path.exists(yol):
        # 🔴 BOZUK DOSYAYI BOS SAYMA. Eskiden except -> birlesik={} idi; o yol
        #    bozuk bir dosyanin UZERINE yalnizca yeni veriyi yazardi = sessiz kayip.
        try:
            with open(yol, encoding="utf-8") as f:
                mevcut = json.load(f)
        except Exception as e:
            raise RuntimeError("OKUNAMADI, uzerine YAZILMADI: %s (%s)" % (yol, e))
        for x in mevcut:
            birlesik[int(x[zaman_alani])] = x
        eski_n = len(birlesik)
    for x in yeni:
        birlesik[int(x[zaman_alani])] = x
    out = [birlesik[k] for k in sorted(birlesik)]
    if len(out) < eski_n:
        raise RuntimeError("KISALMA: %s  %d -> %d (yazilmadi)" % (yol, eski_n, len(out)))
    gec = yol + ".tmp"
    with open(gec, "w", encoding="utf-8") as f:
        json.dump(out, f)
    os.replace(gec, yol)
    return len(out), eski_n


def klines(sym, bas_ms, son_ms):
    out, t = [], bas_ms
    while t < son_ms:
        d = get("%s/fapi/v1/klines?symbol=%sUSDT&interval=1h&startTime=%d&limit=1500"
                % (FAPI, sym, t))
        if d is None:
            return None
        if not d:
            break
        for k in d:
            out.append({"t": int(k[0]), "o": float(k[1]), "h": float(k[2]),
                        "l": float(k[3]), "c": float(k[4]), "v": float(k[5]),
                        "qv": float(k[7]), "n": int(k[8]), "tbv": float(k[9])})
        yeni = int(d[-1][0]) + 3600000
        if yeni <= t or len(d) < 1500:
            break
        t = yeni
        time.sleep(BEKLE)
    return out


def funding(sym, bas_ms, son_ms):
    out, t = [], bas_ms
    while t < son_ms:
        d = get("%s/fapi/v1/fundingRate?symbol=%sUSDT&startTime=%d&limit=1000"
                % (FAPI, sym, t))
        if d is None:
            return None
        if not d:
            break
        # funding_indir.py ile AYNI birim: yuzde (%/8s)
        out += [{"t": int(x["fundingTime"]), "r": float(x["fundingRate"]) * 100} for x in d]
        yeni = int(d[-1]["fundingTime"]) + 1
        if yeni <= t or len(d) < 1000:
            break
        t = yeni
        time.sleep(BEKLE)
    return out


def main():
    for d in (HEDEF_KLINE, HEDEF_FUND):
        os.makedirs(d, exist_ok=True)
    semboller = sorted(f[:-5] for f in os.listdir(SEMBOL_KAYNAK) if f.endswith(".json"))
    bas_ms = int(datetime.datetime.strptime(BAS, "%Y-%m-%d")
                 .replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)
    son_ms = int(time.time() * 1000)

    print("=" * 74)
    print("TAZE VERI INDIRME — %d sembol · %s -> bugun" % (len(semboller), BAS))
    print("=" * 74)
    print("HEDEF (YENI): %s" % HEDEF_KLINE)
    print("HEDEF (YENI): %s" % HEDEF_FUND)
    print("🔴 DOKUNULMAYAN: klines_1h_uzun/ · funding_gecmis/ · perp_seri/")
    print("   (klines_1h_uzun yalnizca sembol ADLARI icin listelendi)")
    print("Hiz: %.1f sn/istek · bot denetimi her 25 sembolde\n" % BEKLE)

    t0 = time.time()
    ok = atla = hata = 0
    kisalma = []
    for i, sym in enumerate(semboller, 1):
        if i % 25 == 1:
            y = bot_yasi()
            if y > BOT_ESIK_SN:
                print("  [bot son turu %.0f sn once — 30 sn yavaslama]" % y, flush=True)
                time.sleep(30)
        yol_k = os.path.join(HEDEF_KLINE, sym + ".json")
        yol_f = os.path.join(HEDEF_FUND, sym + ".json")
        if os.path.exists(yol_k) and os.path.exists(yol_f):
            atla += 1
            continue
        try:
            k = klines(sym, bas_ms, son_ms)
            time.sleep(BEKLE)
            f = funding(sym, bas_ms, son_ms)
            time.sleep(BEKLE)
            if k is None or f is None:
                hata += 1
                continue
            if k:
                guvenli_yaz(yol_k, k, "t")
            if f:
                guvenli_yaz(yol_f, f, "t")
            ok += 1
        except RuntimeError as e:
            kisalma.append(str(e))
            hata += 1
        except Exception as e:
            hata += 1
            if hata <= 5:
                print("  %s: %s" % (sym, e), flush=True)
        if i % 50 == 0:
            gecen = time.time() - t0
            print("  %d/%d · ok %d · atlanan %d · hata %d · %.0f dk"
                  % (i, len(semboller), ok, atla, hata, gecen / 60), flush=True)

    print("\nBITTI — indirilen %d · atlanan %d · hata %d · %.1f dk"
          % (ok, atla, hata, (time.time() - t0) / 60))
    if kisalma:
        print("🔴 KISALMA ENGELLENDI (%d dosya yazilmadi):" % len(kisalma))
        for m in kisalma[:10]:
            print("   " + m)
    print("Bot dosyalarina yazim: YOK · mevcut arsivlere yazim: YOK")


if __name__ == "__main__":
    main()
