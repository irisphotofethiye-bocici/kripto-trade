#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""notrlong'un ELEDIGI COINLER — poz acsaydi ne olurdu? (2026-09-06)

KULLANICI: "botun kurdugumuzdan beri eledigi coinlere bak. bunlara poz acsaydi
           simdi ne olurdu?"

🔴 ONCE DURUST TESPIT: BOT REDDETTIKLERINI KAYDETMIYOR.
   notrlong_log.txt yalniz tur basi/sonu satiri tasiyor; ACILDI / giris kapisi
   satiri SIFIR, notrlong_veto.jsonl hic olusmamis. Yani sorunun dogrudan
   cevabi BOTUN KENDI KAYITLARINDAN CIKARILAMAZ.
   (testbot'ta bu isi `golge` defteri yapiyordu — bu botta karsiligi YOK.)

BU BETIK NE YAPAR: radar_archive.jsonl'den (KriptoRadar, 15 dk'da bir, taze)
   botun kurulusundan beri gorulen adaylari alir, NOTR-LONG karar zincirini
   YENIDEN YURUTUR, elenenleri bulur ve o andan BUGUNE ileri getirilerini olcer.

🔴 UC SINIR — hukum yazmadan once okunmali:
   1) radar_archive RADAR'in taramasi; botun kendi havuzu (150 sembol, skora
      gore ilk 10) ILE AYNI DEGIL. Buradaki bir aday bota hic ulasmamis olabilir.
   2) Bot ~2 SAATTIR kosuyor. Ileri getiri ufku 2 saat — hicbir seye yetmez.
   3) Eleme "para kaybettirdi mi" sorusu MEKANIKSIZ olcumle cevaplanmaz;
      burada stop/hedef YOK, ham fiyat farki var.

🟡 BETIMLEYICI — hukum yok, kural cikmaz. SALT-OKUNUR.
   ⚠️ radar_archive context'e YUKLENMEZ; Python okur, ozet basar.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, sys, collections, urllib.request, statistics as stx

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)

import testbot, evren   # noqa: E402

ARSIV = os.path.join(KOK, "radar_archive.jsonl")
BOT_BAS = "2026-09-06 11:08"        # ilk notrlong turu
ESIK_HAZIR = evren.esik("radar_alert_skor", 40.0)
ESIK_BASLIYOR = ESIK_HAZIR + 5

ADIM = ["stage izle", "skor dusuk", "smart LONG degil",
        "blowoff", "long_veto", "taker<1.0", "diger"]


def fiyatlar():
    try:
        r = urllib.request.urlopen(
            "https://fapi.binance.com/fapi/v1/ticker/price", timeout=15).read()
        return dict((x["symbol"], float(x["price"])) for x in json.loads(r))
    except Exception:
        return {}


def son_kuyruk(bayt=40_000_000):
    """Arsivin son parcasini oku — dosya 109 MB, tamamini okumaya gerek yok."""
    b = os.path.getsize(ARSIV)
    with open(ARSIV, "rb") as f:
        f.seek(max(0, b - bayt))
        return f.read().decode("utf-8", "ignore").splitlines()[1:]


def main():
    print("=" * 92)
    print("notrlong'un ELEDIGI COINLER — poz acsaydi ne olurdu?")
    print("=" * 92)
    print("🔴 Bot reddettiklerini KAYDETMIYOR. Bu yeniden kurulum, kayit degil.")
    print()

    fy = fiyatlar()
    if not fy:
        print("fiyat alinamadi")
        return

    gorulen = {}          # (sym) -> ilk gorulme kaydi (bot basladiktan sonra)
    n_satir = 0
    for l in son_kuyruk():
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        ts = r.get("ts") or ""
        if ts < BOT_BAS:
            continue
        n_satir += 1
        s = r.get("sym")
        if s and s not in gorulen:
            gorulen[s] = r

    print("### 1) KAPSAM")
    print("   bot baslangici : %s" % BOT_BAS)
    print("   arsiv satiri   : %d  ·  tekil sembol: %d" % (n_satir, len(gorulen)))
    if not gorulen:
        print("   kayit yok")
        return
    print()

    alinan, elenen = [], []
    for s, r in gorulen.items():
        pil = {"top_ls": r.get("top_ls"), "glob_ls": r.get("glob_ls"),
               "taker": r.get("taker"), "smart": r.get("smart")}
        stage, skor = r.get("stage"), r.get("score") or 0
        esik = ESIK_HAZIR if stage == "HAZIRLANIYOR" else ESIK_BASLIYOR
        nerede = None
        if stage not in ("BASLIYOR", "HAZIRLANIYOR"):
            nerede = 0
        elif skor < esik:
            nerede = 1
        elif r.get("smart") != "LONG":
            nerede = 2
        else:
            v = []
            k = testbot.karar_yon("NOTR", r, pil, False, veto_out=v)
            if k and k[0] == "LONG":
                nerede = None
            else:
                kat = v[0]["kategori"] if v else "?"
                nerede = {"blowoff": 3, "long_veto": 4, "taker_soguma": 5}.get(kat, 6)
        p0 = r.get("price")
        p1 = fy.get(s if s.endswith("USDT") else s + "USDT")
        ret = ((p1 / p0 - 1) * 100) if (p0 and p1) else None
        kay = {"sym": s, "ts": r.get("ts"), "stage": stage, "skor": skor,
               "smart": r.get("smart"), "ret": ret, "nerede": nerede}
        (alinan if nerede is None else elenen).append(kay)

    olculebilir = [k for k in elenen if k["ret"] is not None]
    print("### 2) SONUC")
    print("   LONG karari cikan (alinacakti) : %d" % len(alinan))
    print("   ELENEN                          : %d  (ileri getirisi olculebilen %d)"
          % (len(elenen), len(olculebilir)))
    print()

    if olculebilir:
        v = [k["ret"] for k in olculebilir]
        v.sort()
        print("### 3) ELENENLERE POZ ACSAYDIK (ham fiyat, LONG, stop/hedef YOK)")
        print("   ortalama %+.3f%%  ·  medyan %+.3f%%  ·  artida %d/%d (%%%.0f)"
              % (stx.mean(v), v[len(v) // 2],
                 sum(1 for x in v if x > 0), len(v),
                 100.0 * sum(1 for x in v if x > 0) / len(v)))
        print("   en kotu %+.2f%%  ·  en iyi %+.2f%%" % (v[0], v[-1]))
        print()
        print("   ELEME BASAMAGINA GORE:")
        g = collections.defaultdict(list)
        for k in olculebilir:
            g[k["nerede"]].append(k["ret"])
        print("   %-20s %6s %11s %10s" % ("basamak", "N", "ort getiri", "artida"))
        for i in sorted(g):
            vv = g[i]
            print("   %-20s %6d %+10.3f%% %8.0f%%"
                  % (ADIM[i], len(vv), stx.mean(vv),
                     100.0 * sum(1 for x in vv if x > 0) / len(vv)))
        print()
        print("   EN COK KAZANDIRAN 8 ELENEN:")
        print("   %-12s %-13s %6s %-7s %10s  %s"
              % ("sembol", "stage", "skor", "smart", "getiri", "elendigi yer"))
        for k in sorted(olculebilir, key=lambda x: -x["ret"])[:8]:
            print("   %-12s %-13s %6.1f %-7s %+9.2f%%  %s"
                  % (k["sym"], k["stage"], k["skor"], k["smart"] or "-",
                     k["ret"], ADIM[k["nerede"]]))
    print()

    if alinan:
        print("### 4) LONG KARARI CIKANLAR (bot bunlari almali/beklemeliydi)")
        for k in alinan:
            print("   %-12s %-13s skor %5.1f  getiri %s"
                  % (k["sym"], k["stage"], k["skor"],
                     ("%+.2f%%" % k["ret"]) if k["ret"] is not None else "-"))
        print()

    print("### 5) 🔴 BU SAYILAR NE DEGILDIR")
    print("   - radar_archive RADAR'in taramasi; botun havuzu (150 sembol, ilk 10)")
    print("     ile AYNI DEGIL. Buradaki bir aday bota hic ulasmamis olabilir.")
    print("   - Ufuk ~2 SAAT. Bu bir kenar olcumu DEGIL, anlik goruntudur.")
    print("   - Stop/hedef YOK. Bot bu pozisyonlari boyle tutmazdi.")
    print("   - Tek pencere, secilim yok ama N kucuk -> HUKUM CIKMAZ.")
    print()
    print("Salt-okuma. Arsiv context'e yuklenmedi. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
