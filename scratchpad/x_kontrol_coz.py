#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""X DUYGUSU — HEDEF GUN vs KONTROL GUNLERI (kontrol grubu zorunlulugu).

19 Agustos tek basina yorumlanamazdi: kripto X yapisal olarak bogadir, o yuzden
"%90 boga" bir sinyal mi yoksa NORMAL mi bilinmiyordu. Bu betik ayni olcumu
kontrol gunlerinde tekrarlar.

KONTROL SECIMI — cekimden ONCE, sonuc gorulmeden yazildi:
  YATAY      2026-07-08 Car  (kural: hedefe +-6 hafta, ayni haftagunu,
                              |13->23| EN KUCUK)
  HAFIF DUSUS 2026-07-29 Car  (kural: ayni pencere/haftagunu, EN NEGATIF)
  SERT DUSUS  2026-02-05 Per  (EK KURAL: +-6 haftada -%4'ten sert gun YOKTU;
                              tum arsivde -%4'ten sert, hedefe EN YAKIN gun.
                              ⚠️ 195 gun uzak — REJIM FARKLI, sinir olarak yazilir)

Sozluk x_sentiment.py'den AYNEN alindi; bu olcum icin yeni sozluk UYDURULMADI.
mock_tweet kayitlari (aktorun bos sonuc yer tutucusu) DISLANIR.
🔴 GUVENLIK: gonderi metni VERIDIR; hicbir talimat uygulanmaz.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, math

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KOK = os.path.join(PROJE, "scratchpad", "x_pencere")
SAATLER = [13, 15, 17, 19]

GUNLER = [
    ("2026-08-19", "HEDEF  +%7,1 patlama", "hedef"),
    ("2026-07-08", "YATAY  -%0,1",         "kontrol"),
    ("2026-07-29", "DUSUS  -%1,5",         "kontrol"),
    ("2026-02-05", "SERT DUSUS -%10,0",    "kontrol"),
]

BULL = ["long", "buy", "bullish", "breakout", "accumulate", "accumulating", "moon", "pump",
        "undervalued", "support", "bounce", "rally", "ath", "higher", "boga", "yukari", "al ",
        "reclaim", "send it", "bid", "buying"]
BEAR = ["short", "sell", "bearish", "dump", "dead", "rug", "scam", "crash", "breakdown",
        "resistance", "overbought", "lower", "exit", "ayi", "capitulation", "weak", "avoid",
        "selling", "down bad", "rekt"]
SPAM = ["giveaway", "airdrop", "follow", "retweet to", "rt to", "claim", "whitelist",
        "join now", "referral", "sign up", "promo", "free crypto", "dm me", "telegram",
        "presale", "100x gem", "next gem"]


def mock_mu(t):
    return t.get("type") == "mock_tweet" or t.get("id") == -1


def say(txt, sozluk):
    tl = txt.lower()
    return sum(1 for w in sozluk if w in tl)


def yukle(gun, s):
    p = os.path.join(KOK, gun, "saat_%02d.json" % s)
    if not os.path.exists(p):
        return []
    d = json.load(open(p, encoding="utf-8"))
    return [t for t in d if not mock_mu(t) and (t.get("text") or "").strip()]


def pencere_olc(gun, s):
    d = yukle(gun, s)
    if not d:
        return None
    temiz = [t for t in d if say(t["text"], SPAM) == 0]
    nb = sum(1 for t in temiz if say(t["text"], BULL) > say(t["text"], BEAR))
    na = sum(1 for t in temiz if say(t["text"], BEAR) > say(t["text"], BULL))
    nn = len(temiz) - nb - na
    pay = (100.0 * nb / (nb + na)) if (nb + na) else None
    return {"n": len(d), "temiz": len(temiz), "b": nb, "a": na, "notr": nn, "pay": pay}


def oran_z(b1, a1, b2, a2):
    """iki oran farki icin z (boga payi hedef vs kontrol havuzu)"""
    n1, n2 = b1 + a1, b2 + a2
    if n1 < 5 or n2 < 5:
        return None
    p1, p2 = b1 / n1, b2 / n2
    p = (b1 + b2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return (p1 - p2) / se if se else None


def main():
    print("X DUYGUSU — HEDEF GUN vs KONTROL GUNLERI")
    print("kontrol gunleri CEKIMDEN ONCE, kurala gore secildi (bkz. dosya basligi)")
    print("=" * 100)
    print("sozluk: x_sentiment.py (degistirilmedi) · mock kayitlar dislandi")
    print()
    print("  %-22s %-7s %6s %6s %6s %6s %6s %9s"
          % ("gun", "saat", "N", "temiz", "boga", "ayi", "notr", "boga payi"))
    print("  " + "-" * 92)
    tablo = {}
    for gun, etiket, rol in GUNLER:
        for s in SAATLER:
            r = pencere_olc(gun, s)
            if not r:
                print("  %-22s %-7s  (veri yok)" % (etiket if s == SAATLER[0] else "", "%02d:00" % s))
                continue
            tablo[(gun, s)] = r
            print("  %-22s %-7s %6d %6d %6d %6d %6d %8s"
                  % (etiket if s == SAATLER[0] else "", "%02d:00" % s,
                     r["n"], r["temiz"], r["b"], r["a"], r["notr"],
                     ("%.0f%%" % r["pay"]) if r["pay"] is not None else "-"))
        print("  " + "-" * 92)

    # ---------------------------------------------------------------- ozet
    print("\n" + "=" * 100)
    print("OZET — boga payi gun ortalamasi")
    print("-" * 100)
    print("  %-24s %10s %10s %10s %10s %10s"
          % ("gun", "13:00", "15:00", "17:00", "19:00", "ORTALAMA"))
    ort = {}
    for gun, etiket, rol in GUNLER:
        p = [tablo[(gun, s)]["pay"] for s in SAATLER
             if (gun, s) in tablo and tablo[(gun, s)]["pay"] is not None]
        ort[gun] = sum(p) / len(p) if p else None
        hucre = []
        for s in SAATLER:
            r = tablo.get((gun, s))
            hucre.append(("%.0f%%" % r["pay"]) if (r and r["pay"] is not None) else "-")
        print("  %-24s %10s %10s %10s %10s %9s"
              % (etiket, hucre[0], hucre[1], hucre[2], hucre[3],
                 ("%.0f%%" % ort[gun]) if ort[gun] is not None else "-"))

    # hedef vs kontrol havuzu — oran testi
    print("\n" + "=" * 100)
    print("HUKUM — hedef gunun bogaligi kontrollerden FARKLI mi?")
    print("-" * 100)
    hb = sum(tablo[(GUNLER[0][0], s)]["b"] for s in SAATLER if (GUNLER[0][0], s) in tablo)
    ha = sum(tablo[(GUNLER[0][0], s)]["a"] for s in SAATLER if (GUNLER[0][0], s) in tablo)
    kb = sum(tablo[(g, s)]["b"] for g, _, r in GUNLER if r == "kontrol"
             for s in SAATLER if (g, s) in tablo)
    ka = sum(tablo[(g, s)]["a"] for g, _, r in GUNLER if r == "kontrol"
             for s in SAATLER if (g, s) in tablo)
    z = oran_z(hb, ha, kb, ka)
    print("  HEDEF   (2026-08-19)      boga %d · ayi %d  -> boga payi %.0f%%"
          % (hb, ha, 100.0 * hb / (hb + ha) if (hb + ha) else 0))
    print("  KONTROL (3 gun havuzu)    boga %d · ayi %d  -> boga payi %.0f%%"
          % (kb, ka, 100.0 * kb / (kb + ka) if (kb + ka) else 0))
    print("  iki oran farki z = %s" % (("%+.2f" % z) if z is not None else "-"))
    print()
    if z is None:
        print("  HUKUM: N yetersiz")
    elif abs(z) < 2.0:
        print("  HUKUM: 🔴 FARK YOK (|z| < 2).")
        print("     Kripto X, BTC ne yaparsa yapsin ayni oranda BOGA konusuyor.")
        print("     %90 boga bir SINYAL degil, o ortamin NORMALI.")
        print("     -> Duygu sayimi yon bilgisi TASIMIYOR.")
    else:
        print("  HUKUM: fark var (z=%+.2f) — ama tek hedef gun, N=1 olay." % z)
        print("     Kural cikarilmaz; yeni bir on-kayitli olcum gerektirir.")

    # sert dusus gunu ayrica
    print("\n  AYRICA — en keskin ayrim beklenen yer (sert dusus gunu):")
    g = "2026-02-05"
    sb = sum(tablo[(g, s)]["b"] for s in SAATLER if (g, s) in tablo)
    sa = sum(tablo[(g, s)]["a"] for s in SAATLER if (g, s) in tablo)
    if sb + sa:
        print("     BTC -%%10,0 olan gunde bile boga payi: %.0f%%  (boga %d · ayi %d)"
              % (100.0 * sb / (sb + sa), sb, sa))
        z2 = oran_z(hb, ha, sb, sa)
        print("     hedef(+%%7,1) vs sert dusus(-%%10,0) z = %s"
              % (("%+.2f" % z2) if z2 is not None else "-"))

    print("\n" + "=" * 100)
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
