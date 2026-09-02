#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MAKRO OLAY LISTESI — FOMC kararlari + FOMC tutanaklari, TAM damgali.

Kaynak: federalreserve.gov/monetarypolicy/fomccalendars.htm (2026-09-01'de cekildi).
Capraz dogrulama: 2026 FOMC karar tarihleri projedeki makro_takvim.json ile
BIREBIR uyustu -> kaynak dogru okundu.

Yayin saati: ikisi de 14:00 ET.
  ET = EDT (UTC-4) yaz · EST (UTC-5) kis. ABD yaz saati: Mart'in 2. Pazari ->
  Kasim'in 1. Pazari. Asagida ELDE hesaplanir (zoneinfo'ya bagimlilik yok).

Cikti: scratchpad/makro_olaylar.json
SALT OKUMA — hicbir bot dosyasina dokunmaz.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, datetime, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIKTI = os.path.join(PROJE, "scratchpad", "makro_olaylar.json")

# --- federalreserve.gov'dan cekildi (karar = toplantinin 2. gunu)
FOMC_KARAR = [
    "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12",
    "2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18",
    "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
    "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
    "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17",
    "2026-07-29", "2026-09-16", "2026-10-28", "2026-12-09",
]
# --- tutanak yayin tarihleri (ayni sayfa)
FOMC_TUTANAK = [
    "2024-02-21", "2024-04-10", "2024-05-22", "2024-07-03",
    "2024-08-21", "2024-10-09", "2024-11-26", "2025-01-08",
    "2025-02-19", "2025-04-09", "2025-05-28", "2025-07-09",
    "2025-08-20", "2025-10-08", "2025-11-19", "2025-12-30",
    "2026-02-18", "2026-04-08", "2026-05-20", "2026-07-08", "2026-08-19",
]
YAYIN_SAAT_ET = 14      # 14:00 ET

# fiyat arsivinin kapsadigi pencere
PENCERE_BAS = datetime.date(2024, 8, 11)
PENCERE_BIT = datetime.date(2026, 9, 1)


def nth_pazar(yil, ay, n):
    d = datetime.date(yil, ay, 1)
    d += datetime.timedelta(days=(6 - d.weekday()) % 7)      # ilk Pazar
    return d + datetime.timedelta(weeks=n - 1)


def edt_mi(d):
    """ABD yaz saati: Mart'in 2. Pazari .. Kasim'in 1. Pazari"""
    return nth_pazar(d.year, 3, 2) <= d < nth_pazar(d.year, 11, 1)


def utc_damga(gun_str):
    d = datetime.date.fromisoformat(gun_str)
    ofs = 4 if edt_mi(d) else 5                              # ET -> UTC farki
    return datetime.datetime(d.year, d.month, d.day, YAYIN_SAAT_ET) \
        + datetime.timedelta(hours=ofs)


def sinama():
    """DST hesabi dogru mu — bilinen iki nokta."""
    h = []
    # 2026-08-19 yaz -> EDT -> 14:00 ET = 18:00 UTC
    if utc_damga("2026-08-19") != datetime.datetime(2026, 8, 19, 18):
        h.append("yaz saati hatasi: 2026-08-19")
    # 2024-12-18 kis -> EST -> 14:00 ET = 19:00 UTC
    if utc_damga("2024-12-18") != datetime.datetime(2024, 12, 18, 19):
        h.append("kis saati hatasi: 2024-12-18")
    if h:
        print("DST SINAMASI DUSTU — betik calismayi REDDEDIYOR:")
        for x in h:
            print("   " + x)
        raise SystemExit(1)
    print("DST sinamasi: 2 nokta GECTI (yaz 18:00 UTC · kis 19:00 UTC)")


def main():
    sinama()
    olay = []
    for tip, liste in (("fomc_karar", FOMC_KARAR), ("fomc_tutanak", FOMC_TUTANAK)):
        for g in liste:
            d = datetime.date.fromisoformat(g)
            if not (PENCERE_BAS <= d <= PENCERE_BIT):
                continue
            u = utc_damga(g)
            olay.append({"tip": tip, "gun": g,
                         "utc": u.strftime("%Y-%m-%d %H:%M"),
                         "ts": int((u - datetime.datetime(1970, 1, 1)).total_seconds() * 1000),
                         "kaynak": "federalreserve.gov/monetarypolicy/fomccalendars.htm"})
    olay.sort(key=lambda z: z["ts"])
    json.dump(olay, open(CIKTI, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print()
    print("MAKRO OLAY LISTESI — %s" % os.path.relpath(CIKTI, PROJE))
    print("=" * 78)
    c = collections.Counter(o["tip"] for o in olay)
    for t, n in c.most_common():
        print("  %-16s %3d" % (t, n))
    print("  %-16s %3d" % ("TOPLAM", len(olay)))
    if olay:
        print("  kapsam: %s .. %s" % (olay[0]["utc"], olay[-1]["utc"]))
    print()
    print("  DISARIDA BIRAKILANLAR ve NEDENI:")
    print("   - CPI/PPI/NFP : bls.gov HTTP 403 verdi, 2024-2025 tarihleri")
    print("     DOGRULANAMADI. Tarih UYDURULMAZ -> kapsam disi.")
    print("   - Hazine geri-alim duyurulari: 19 Agustos'u ACIKLAYAN haber buydu,")
    print("     ama gecmis damgalari dogrulanabilir bicimde alinamadi.")
    print("   ⚠️ Yani bu olcum 19 Agustos MEKANIZMASINI dogrudan sinamiyor;")
    print("      titizlikle tarihlenebilen EN YAKIN makro olay sinifini sinar.")
    print()
    print("  ⚠️ 2026-08-19 bu listede VAR (FOMC tutanak gunu). Anekdotu")
    print("     inceledigim gun bu 33'ten biri — karistirici olarak yazildi.")
    print()
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
