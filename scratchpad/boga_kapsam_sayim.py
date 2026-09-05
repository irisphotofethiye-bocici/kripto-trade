#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOGA PENCERESI KAPSAM SAYIMI — guc girdisi (2026-09-05)

NE YAPAR: yalnizca TETIK ve KAPSAM sayar. Getiri/stop/hedef HESAPLAMAZ.
NEDEN: kullanici "21'inden bugune rejim boga, elimizde veri olmasi lazim" dedi
  ve HAKLI cikti. Onceki iki iddiam yanlisti:
    (1) "22 Agustos sonrasi olculemez"  -> perp_seri klineleri 09-05'e kadar VAR
    (2) "oi24 bacagi olculemez"         -> radar_archive'da oi24 ZATEN VAR
  Bu betik dogru rakami uretir; on-kayit ona gore yazilir.

ZAMAN: radar_archive ts YEREL (UTC+3), klineler UTC -> ofset -3 saat.
Salt-okunur. radar_archive context'e YUKLENMEZ, yalnizca ozet basilir.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, collections, datetime as dt

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURA)
PERP = os.path.join(BURA, "perp_seri")
ARSIV = os.path.join(KOK, "radar_archive.jsonl")
BOSLUK = os.path.join(KOK, "radar_bosluk.jsonl")

FUND_ESIK = -0.05
OI24_ESIK = 10.0
OFSET_SAAT = -3                 # yerel (UTC+3) -> UTC
BOGA_BAS = "2026-08-21"
SOGUMA_SAAT = 24                # ayni sembolde ust uste olaylari ele


def utc_ms(s):
    """'YYYY-MM-DD HH:MM' YEREL -> UTC ms"""
    d = dt.datetime.strptime(s[:16], "%Y-%m-%d %H:%M")
    d = d.replace(tzinfo=dt.timezone.utc) + dt.timedelta(hours=OFSET_SAAT)
    return int(d.timestamp() * 1000)


def gun(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d")


def main():
    # --- perp_seri kline kapsami ---
    kl = {}
    for f in os.listdir(PERP):
        if not f.endswith("_kline.json"):
            continue
        sym = f[:-11]
        try:
            j = json.load(open(os.path.join(PERP, f), encoding="utf-8"))
        except Exception:
            continue
        if j:
            kl[sym] = (j[0]["t"], j[-1]["t"], len(j))
    print("=" * 74)
    print("BOGA PENCERESI KAPSAM SAYIMI")
    print("=" * 74)
    print("perp_seri kline olan sembol: %d" % len(kl))
    if kl:
        sonlar = sorted(v[1] for v in kl.values())
        print("  kline son bar medyani: %s" % gun(sonlar[len(sonlar) // 2]))

    # --- radar_bosluk (kayip kare denetimi) ---
    bos = 0
    if os.path.exists(BOSLUK):
        with open(BOSLUK, encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.strip():
                    bos += 1
    print("radar_bosluk.jsonl satir: %d  (kayip kare kaydi)" % bos)

    bas_ms = utc_ms(BOGA_BAS + " 00:00")
    # ileri getiri icin son 72 saat kullanilamaz
    son_kl = max((v[1] for v in kl.values()), default=0)
    kesme = son_kl - 72 * 3600000

    print("\nBOGA penceresi: %s ->  (kline sonu %s, 72s ileri icin kesme %s)"
          % (BOGA_BAS, gun(son_kl), gun(kesme)))
    print()

    # --- arsiv taramasi ---
    son_olay = {}
    say = collections.Counter()
    gunler = {"A": set(), "AB": set()}
    semboller = {"A": set(), "AB": set()}
    ham = collections.Counter()
    with open(ARSIV, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            ts = r.get("ts")
            if not ts:
                continue
            try:
                t = utc_ms(ts)
            except Exception:
                continue
            if t < bas_ms:
                continue
            ham["boga_penceresi_kayit"] += 1
            sym = r.get("sym")
            if not sym:
                continue
            fund = r.get("funding")
            oi24 = r.get("oi24")
            if fund is None:
                continue
            ham["funding_dolu"] += 1
            a = fund <= FUND_ESIK
            ab = a and (oi24 is not None and oi24 >= OI24_ESIK)
            if not a:
                continue
            say["A_ham"] += 1
            if ab:
                say["AB_ham"] += 1
            if sym not in kl:
                say["A_kline_YOK"] += 1
                continue
            if t > kesme:
                say["A_ileri_getiri_YOK"] += 1
                continue
            # soguma: ayni sembolde 24 saat icinde ikinci olay sayilmaz
            son = son_olay.get(sym)
            if son is not None and t - son < SOGUMA_SAAT * 3600000:
                say["A_soguma_elendi"] += 1
                continue
            son_olay[sym] = t
            say["A_OLAY"] += 1
            gunler["A"].add(gun(t))
            semboller["A"].add(sym)
            if ab:
                say["AB_OLAY"] += 1
                gunler["AB"].add(gun(t))
                semboller["AB"].add(sym)

    print("BOGA penceresindeki arsiv kaydi     : %d" % ham["boga_penceresi_kayit"])
    print("  funding alani dolu                : %d" % ham["funding_dolu"])
    print()
    print("A  (funding <= %.2f) ham tetik      : %d" % (FUND_ESIK, say["A_ham"]))
    print("   kline'i olmayan sembol yuzunden  : -%d" % say["A_kline_YOK"])
    print("   72s ileri getirisi olmayan       : -%d" % say["A_ileri_getiri_YOK"])
    print("   soguma (%ds) ile elenen          : -%d" % (SOGUMA_SAAT, say["A_soguma_elendi"]))
    print("   >>> BAGIMSIZ OLAY                : %d   (%d gun · %d sembol)"
          % (say["A_OLAY"], len(gunler["A"]), len(semboller["A"])))
    print()
    print("A+B (funding <= %.2f VE oi24 >= %.0f) ham : %d" % (FUND_ESIK, OI24_ESIK, say["AB_ham"]))
    print("   >>> BAGIMSIZ OLAY                : %d   (%d gun · %d sembol)"
          % (say["AB_OLAY"], len(gunler["AB"]), len(semboller["AB"])))
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
