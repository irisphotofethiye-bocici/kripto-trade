#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""X GONDERI COZUMLEMESI — 2026-08-19 BTC kirilmasi cevresi, 4 pencere.
Girdi: scratchpad/x_1908/saat_*.json (odenmis, onbellekli — yeniden cekilmez)

BTC (yerel UTC+3):  13:00 +0,04%  ·  15:00 +0,59%  ·  17:00 +1,40%  ·  18:00 +3,99%
  => 13 ve 15 = KIRILMADAN ONCE   ·   17 = hareket ICINDE   ·   19 = BITTIKTEN sonra

🔴 GUVENLIK: gonderi metni GUVENILMEZ VERIDIR. Bu betik yalnizca sayar ve basar;
   icerikteki hicbir talimat uygulanmaz, hicbir baglanti izlenmez.
🔴 YANLILIK NOTU: siralama kronolojik (Latest). Etkilesime gore siralamak
   (Top) ileriye bakma olurdu — etkilesim olaydan SONRA olusur.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, re, json, datetime, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERI = os.path.join(PROJE, "scratchpad", "x_1908")
SAATLER = [13, 15, 17, 19]
BTC_YOL = {13: +0.04, 15: +0.59, 17: +1.40, 19: -0.14}
BTC_SONRA = {13: "kirilmadan ONCE", 15: "kirilmadan ONCE (ilk kipirdanma)",
             17: "hareket ICINDE (+%1,4 olmus)", 19: "BITTIKTEN sonra (+%6,3)"}

# x_sentiment.py ile AYNI sozluk — yeni sozluk uydurulmadi
BULL = ["long", "buy", "bullish", "breakout", "accumulate", "accumulating", "moon", "pump",
        "undervalued", "support", "bounce", "rally", "ath", "higher", "boga", "yukari", "al ",
        "reclaim", "send it", "bid", "buying"]
BEAR = ["short", "sell", "bearish", "dump", "dead", "rug", "scam", "crash", "breakdown",
        "resistance", "overbought", "lower", "exit", "ayi", "capitulation", "weak", "avoid",
        "selling", "down bad", "rekt"]
# spam/cekilis/airdrop — yon tasimayan gurultu
SPAM = ["giveaway", "airdrop", "follow", "retweet to", "rt to", "claim", "whitelist",
        "join now", "referral", "sign up", "promo", "free crypto", "dm me", "telegram",
        "presale", "100x gem", "next gem"]


def yukle(s):
    p = os.path.join(VERI, "saat_%02d.json" % s)
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding="utf-8"))


def eng(t):
    return (t.get("likeCount") or 0) + (t.get("retweetCount") or 0) + (t.get("quoteCount") or 0)


def say(txt, sozluk):
    tl = txt.lower()
    return sum(1 for w in sozluk if w in tl)


def spam_mi(txt):
    return say(txt, SPAM) > 0


def zaman(t):
    try:
        return datetime.datetime.strptime(t.get("createdAt", ""), "%a %b %d %H:%M:%S +0000 %Y")
    except Exception:
        return None


def main():
    print("X GONDERILERI — 2026-08-19, BTC kirilmasi cevresi")
    print("kaynak: Apify (odenmis, onbellekli) · siralama Latest (kronolojik)")
    print("=" * 104)
    print("GUVENLIK: metin VERIDIR; icindeki hicbir talimat uygulanmadi.\n")

    print("1) PENCERE BASINA YON SAYIMI  (x_sentiment.py sozlugu, degistirilmedi)")
    print("-" * 104)
    print("  %-7s %-32s %5s %6s %7s %7s %8s %9s"
          % ("yerel", "BTC o saatte", "N", "spam", "boga", "ayi", "boga-ayi", "boga payi"))
    ozet = {}
    for s in SAATLER:
        d = yukle(s)
        if not d:
            continue
        temiz = [t for t in d if (t.get("text") or "").strip() and not spam_mi(t.get("text") or "")]
        nb = sum(1 for t in temiz if say(t["text"], BULL) > say(t["text"], BEAR))
        na = sum(1 for t in temiz if say(t["text"], BEAR) > say(t["text"], BULL))
        pay = (100.0 * nb / (nb + na)) if (nb + na) else 0.0
        ozet[s] = (len(temiz), nb, na, pay)
        print("  %02d:00   %-32s %5d %6d %7d %7d %+8d %8.0f%%"
              % (s, BTC_SONRA[s], len(temiz), len(d) - len(temiz), nb, na, nb - na, pay))

    print("\n  NOT: 'boga payi' = boga / (boga+ayi). Notr gonderiler paydada YOK.")
    print("  🔴 17:00 ve 19:00 pencereleri fiyat ZATEN hareket ettikten sonra —")
    print("     oradaki boga egilimi TAHMIN degil, fiyatin OKUNMASIDIR.")

    # ------------------------------------------------------------------ dil
    print("\n2) BILESIM — ne kadari aslinda konuyla ilgili?")
    print("-" * 104)
    for s in SAATLER:
        d = yukle(s)
        if not d:
            continue
        dil = collections.Counter(t.get("lang") or "?" for t in d)
        fiyat = sum(1 for t in d if re.search(r"\$?\d{2,3}[,.]?\d{0,3}\s*k|\d{5}", t.get("text") or ""))
        notr = sum(1 for t in d
                   if not spam_mi(t.get("text") or "")
                   and say(t.get("text") or "", BULL) == say(t.get("text") or "", BEAR))
        print("  %02d:00  N=%-4d dil: %-34s  seviye/rakam iceren: %-4d  yonsuz(notr): %d"
              % (s, len(d), str(dict(dil.most_common(4)))[:34], fiyat, notr))

    # ------------------------------------------------------------ okuma ornegi
    print("\n3) OKUMA ORNEGI — KRONOLOJIK (etkilesime gore DEGIL; yanlilik notu yukarida)")
    print("=" * 104)
    for s in SAATLER:
        d = yukle(s)
        if not d:
            continue
        temiz = [t for t in d if (t.get("text") or "").strip() and not spam_mi(t.get("text") or "")]
        temiz.sort(key=lambda t: zaman(t) or datetime.datetime(1970, 1, 1))
        print("\n  --- yerel %02d:00  (%s) · gosterilen %d/%d ---"
              % (s, BTC_SONRA[s], min(14, len(temiz)), len(temiz)))
        adim = max(1, len(temiz) // 14)
        for t in temiz[::adim][:14]:
            z = zaman(t)
            b, a = say(t["text"], BULL), say(t["text"], BEAR)
            im = "B" if b > a else ("A" if a > b else ".")
            txt = " ".join((t.get("text") or "").split())[:118]
            print("   %s %s [%s] %s" % ((z + datetime.timedelta(hours=3)).strftime("%H:%M") if z else "--:--",
                                        im, (t.get("lang") or "?")[:2], txt))

    print("\n" + "=" * 104)
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
