#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TAKER KAPISI KALDIRILSA — KAC POZ, NE SONUC?

Kullanici (2026-09-06): "bu degisiklik ne kadar poz izin verir. eldeki veriyle
olc sadece botu kurduktan sonraki veriyle ve sonuc ne olurdu"

IKI KAYNAK, IKISI DE RAPORLANIR — cunku biri KESIN ama KUCUK, oteki BUYUK
ama YENIDEN KURULUM:

  A) notrlong_elenen.jsonl  — botun KENDI kaydi, kurulustan beri.
                              KESIN ama pencere ~3 saat -> N kucuk.
  B) radar_archive tabani   — 57 gunluk huni orani -> HIZ tahmini.

🔴 A'dan HIZ cikarilmaz (N cok kucuk). B'den SONUC cikarilmaz (mekanik yok).
   Her biri kendi sorusunu cevaplar.

SALT-OKUNUR. Bota dokunulmaz.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, sys, collections, time
import datetime as dt

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)
import evren  # noqa: E402

ELENEN = os.path.join(KOK, "notrlong_elenen.jsonl")
STATEF = os.path.join(KOK, "notrlong_state.json")
FAPI = "https://fapi.binance.com"

HEDEF_PCT = 10.0        # notrlong.py: SABIT_HEDEF_PCT
MALIYET_PCT = 0.09      # gidis-donus (taker fee + slipaj), olcumlerde kullanilan


def mum5(sym, bas_ms):
    """5 dakikalik mum — stop/hedef vurulmus mu diye bakmak icin."""
    try:
        d = evren.get("%s/fapi/v1/klines?symbol=%sUSDT&interval=5m&startTime=%d&limit=500"
                      % (FAPI, sym, bas_ms))
        return [{"t": int(k[0]), "h": float(k[2]), "l": float(k[3]), "c": float(k[4])}
                for k in (d or [])]
    except Exception:
        return []


def ts_ms(ts):
    """notrlong damgasi YEREL (UTC+3) — 02_olcum.py'de dogrulandi."""
    d = dt.datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S") - dt.timedelta(hours=3)
    return int(d.replace(tzinfo=dt.UTC).timestamp() * 1000)


def bolum(b):
    print()
    print("=" * 88)
    print(b)
    print("=" * 88)


def main():
    rec = []
    for l in open(ELENEN, encoding="utf-8"):
        l = l.strip()
        if l:
            try:
                rec.append(json.loads(l))
            except Exception:
                pass
    turlar = sorted(set(r["ts"][:16] for r in rec))
    saat = (ts_ms(rec[-1]["ts"]) - ts_ms(rec[0]["ts"])) / 3_600_000.0

    bolum("A) BOTUN KENDI KAYDI — kurulustan beri (KESIN, ama KUCUK)")
    print("   pencere : %s -> %s   (%.2f saat · %d tur)"
          % (rec[0]["ts"], rec[-1]["ts"], saat, len(turlar)))
    print()
    c = collections.Counter(r.get("kapi") for r in rec)
    for k, v in sorted(c.items()):
        print("      %-22s %4d" % (k, v))

    # Gercekte acilan
    st = json.load(open(STATEF, encoding="utf-8"))
    acik = st.get("acik_pozisyonlar", [])
    print()
    print("   GERCEKTE ACILAN: %d" % len(acik))
    for p in acik:
        print("      %-8s %-5s giris %.6f · stop %.6f · tp2 %.6f"
              % (p.get("sym"), p.get("yon"), p.get("giris") or 0,
                 p.get("stop") or 0, p.get("tp2") or 0))

    # Taker kapisi kalksa EKLENECEK olanlar
    tk = [r for r in rec if r.get("kapi") == "4_taker_soguma"]
    ek_sym = collections.OrderedDict()
    for r in tk:
        if r["sym"] not in ek_sym:
            ek_sym[r["sym"]] = r          # ILK gorulme = karar ani
    print()
    print("   TAKER KAPISI KALKSA EKLENECEK: %d kayit -> %d TEKIL pozisyon"
          % (len(tk), len(ek_sym)))
    for s, r in ek_sym.items():
        print("      %s %-8s skor %.1f · taker %s · fiyat %s"
              % (r["ts"][11:16], s, r.get("score") or 0, r.get("taker"), r.get("price")))

    if not ek_sym:
        print("      (bu pencerede yok)")

    # ---- SONUC: her ek aday icin mekanikli takip
    bolum("B) SONUC NE OLURDU — ek adaylarin yolu (5dk mum, gercek mekanik)")
    print("   Kural: ONAY_BEKLE -> bir sonraki turda giris · sabit %+.0f%% hedef"
          % HEDEF_PCT)
    print("          A-stop = botun kendi hesabi (elenen kaydinda YOK -> yaklasik)")
    print("          zaman stopu 48s (henuz dolmadi) · maliyet %%%.2f" % MALIYET_PCT)
    print()
    if not ek_sym:
        print("   ek aday yok")
    else:
        print("   %-8s %10s %10s %9s %9s %-16s" %
              ("sembol", "giris", "simdi", "ham %", "net %", "durum"))
        toplam = 0.0
        for s, r in ek_sym.items():
            g = r.get("price")
            if not g:
                continue
            bas = ts_ms(r["ts"])
            m = mum5(s, bas)
            time.sleep(0.15)
            if not m:
                print("   %-8s  mum alinamadi" % s)
                continue
            hedef = g * (1 + HEDEF_PCT / 100.0)
            en_yuksek = max(x["h"] for x in m)
            en_dusuk = min(x["l"] for x in m)
            son = m[-1]["c"]
            vurdu = "ACIK (hedef/stop vurulmadi)"
            cikis = son
            if en_yuksek >= hedef:
                vurdu = "HEDEF vuruldu (+%.0f%%)" % HEDEF_PCT
                cikis = hedef
            ham = (cikis / g - 1.0) * 100.0
            net = ham - MALIYET_PCT
            toplam += net
            print("   %-8s %10.6f %10.6f %+8.2f%% %+8.2f%% %-16s"
                  % (s, g, son, ham, net, vurdu))
            print("            pencere ici en yuksek %.6f (%+.2f%%) · en dusuk %.6f (%+.2f%%)"
                  % (en_yuksek, (en_yuksek / g - 1) * 100,
                     en_dusuk, (en_dusuk / g - 1) * 100))
        print()
        print("   EK ADAYLARIN TOPLAMI: %+.2f%% (islem basi %+.2f%%)"
              % (toplam, toplam / max(1, len(ek_sym))))

    # ---- gercekte acilanin durumu
    if acik:
        print()
        print("   KARSILASTIRMA — botun GERCEKTEN actigi pozisyon:")
        for p in acik:
            s, g = p.get("sym"), p.get("giris")
            m = mum5(s, ts_ms(rec[0]["ts"]))
            if m and g:
                son = m[-1]["c"]
                print("      %-8s giris %.6f -> simdi %.6f  (%+.2f%% ham)"
                      % (s, g, son, (son / g - 1) * 100))

    # ---- HIZ tahmini
    bolum("C) HIZ — 'ne kadar poz izin verir' (arsiv tabani, 57 gun)")
    print("   🔴 A penceresi %.1f saat. Ondan HIZ cikarilmaz." % saat)
    print("      Hiz tahmini 57 gunluk huni oranindan gelir:")
    print()
    print("      smart LONG  367  ->  taker>=1.0  161      (kapi ACIK)")
    print("      smart LONG  367  ->            367        (kapi KAPALI)")
    print("      carpan: 367/161 = %.2f" % (367.0 / 161.0))
    print()
    kars = 2.06                      # karsi-olgu C kolu: 33 poz / 16 gun
    print("      karsi-olgu C kolu hizi        : %.2f poz/gun" % kars)
    print("      taker kalkarsa (x%.2f)        : %.2f poz/gun" % (367.0 / 161.0, kars * 367.0 / 161.0))
    print("      N=80 icin gereken sure        : %.0f gun  (on-kayit penceresi 30)"
          % (80.0 / (kars * 367.0 / 161.0)))
    print()
    print("   ⚠️ Bu bir UST SINIR: carpan yalniz taker adimini kaldirir, ONAY_BEKLE")
    print("      kaybini, asgari_stop/rr kapisini ve slot cakismasini iceremez.")
    print("      Karsi-olgu da bunlari icermiyordu (kendi SINIR notu).")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
