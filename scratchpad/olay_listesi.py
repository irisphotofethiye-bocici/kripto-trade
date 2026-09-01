#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OLAY LISTESI — Binance resmi duyuru arsivinden olay kutugu cikarir.
On-kayit: ON_KAYIT_olay_kuyrugu.md (bu betikten ONCE commit edilir).

Kaynak: binance.com public CMS duyuru ucu (anahtarsiz). Her duyurunun
releaseDate'i DAKIKA kesinliginde -> olay t=0 makine kesinliginde.

Bu betik YALNIZ olay toplar ve SAYAR. Hicbir getiri hesaplamaz.
Cikti: scratchpad/olaylar.jsonl
SALT OKUMA (bot dosyalarina yazim YOK).

[TUZAK 2026-09-01] Bu dosya bir kez heredoc ile yazildi ve icindeki `\\b`
sinir imi gercek BACKSPACE karakterine (0x08) donustu. Kural hicbir zaman
eslesmedi; py_compile DE pyflakes DE temiz gecti — ikisi de duzenli ifadenin
ANLAMINA bakmaz. Ayni sinif: radar.HERE / ayna.time.
Cozum disiplin degil ARAC: asagidaki kural_sinamasi() her koszumda calisir ve
beklenen etiketi vermeyen bir kural varsa betik CALISMAYI REDDEDER.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, re, json, time, datetime, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJE not in _sys.path:
    _sys.path.insert(0, PROJE)
import evren

CIKTI = os.path.join(PROJE, "scratchpad", "olaylar.jsonl")
UA = {"User-Agent": "Mozilla/5.0"}
BASE = ("https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"
        "?type=1&catalogId=%d&pageNo=%d&pageSize=20")
# fiyat arsivimizin kapsadigi pencere (klines_1h_uzun ilk bar) — disi ISE ALINMAZ
PENCERE_BAS = datetime.datetime(2024, 8, 11)
KATALOG = {48: "listeleme", 161: "kaldirma"}

# --- baslik -> olay tipi (sira ONEMLI: ilk eslesen kazanir)
# AYRIM: birincil duyuru (yeni bilgi) vs ikincil takip ("Will Add ... on Earn").
# Takip duyurulari ayni bilgiyi tekrar eder; birincil olayin kuyruguna karisir.
TIP_KURAL = [
    ("perp_listeleme",  re.compile(r"futures will launch", re.I)),
    ("delisting",       re.compile(r"will delist|delisting of", re.I)),
    ("cift_kaldirma",   re.compile(r"removal of (spot|margin) trading pairs", re.I)),
    ("perp_kaldirma",   re.compile(r"settle and delist|futures will (delist|remove)", re.I)),
    ("launchpool",      re.compile(r"launchpool|hodler airdrop|megadrop|pre-market", re.I)),
    ("ikincil_ekleme",  re.compile(r"(will add|adds) .*on.*(earn|convert|buy crypto|margin)", re.I)),
    ("spot_listeleme",  re.compile(r"will list|introducing .* on binance", re.I)),
]
# kuyruk olcumune GIRECEK tipler (ikincil/idari olanlar disarida)
BIRINCIL = {"spot_listeleme", "launchpool", "delisting", "perp_listeleme"}

RE_PERP = re.compile(r"(?<![A-Z0-9])([A-Z0-9]{2,15})USDT(?![A-Z0-9])")
RE_PARANTEZ = re.compile(r"\(([A-Z0-9]{2,15})\)")
RE_DELIST = re.compile(r"(?:delist|delisting of)\s+([A-Z0-9, ]+?)\s+on(?![A-Za-z])", re.I)


def tip_bul(b):
    for ad, rx in TIP_KURAL:
        if rx.search(b):
            return ad
    return "diger"


def sembol_bul(b, tip):
    if tip == "delisting":
        m = RE_DELIST.search(b)
        if m:
            s = [x.strip() for x in m.group(1).split(",") if 1 < len(x.strip()) < 16]
            if s:
                return s
    s = RE_PERP.findall(b)
    if s:
        return list(dict.fromkeys(s))
    return list(dict.fromkeys(RE_PARANTEZ.findall(b)))


# --------------------------------------------------------------------------
# KURAL SINAMASI — duzenli ifade BOZULURSA betik calismayi reddeder.
# (py_compile/pyflakes bu sinifi goremez; bkz. dosya basligi)
# --------------------------------------------------------------------------
SINAMA = [
    ("Binance Futures Will Launch USDS-Margined MARSCOINUSDT Perpetual Contract",
     "perp_listeleme", ["MARSCOIN"]),
    ("Binance Will Delist ICX, SCRT, STORJ on 2026-09-03",
     "delisting", ["ICX", "SCRT", "STORJ"]),
    ("Notice of Removal of Spot Trading Pairs - 2026-08-21", "cift_kaldirma", None),
    ("Introducing OpenGradient (OPG) on Binance HODLer Airdrops", "launchpool", ["OPG"]),
    ("Binance Will Add Catizen (CATI) on Earn, Buy Crypto, Convert & Margin",
     "ikincil_ekleme", None),
    ("Binance Adds Dogs (DOGS) on Earn, Buy Crypto, Convert & Margin",
     "ikincil_ekleme", None),
    ("Binance Will List Aerodrome (AERO) with Seed Tag Applied",
     "spot_listeleme", ["AERO"]),
    ("Binance Will List Cow Protocol (COW) and Cetus Protocol (CETUS) with Seed Tag Applied",
     "spot_listeleme", ["COW", "CETUS"]),
    ("Notice on New Trading Pairs & Trading Bots Services on Binance Spot - 2024-08-16",
     "diger", None),
]


def kural_sinamasi():
    hata = []
    for baslik, bek_tip, bek_sem in SINAMA:
        t = tip_bul(baslik)
        if t != bek_tip:
            hata.append("TIP  beklenen=%-16s bulunan=%-16s | %s" % (bek_tip, t, baslik[:52]))
            continue
        if bek_sem is not None:
            s = sembol_bul(baslik, t)
            if s != bek_sem:
                hata.append("SEM  beklenen=%-16s bulunan=%-16s | %s"
                            % (",".join(bek_sem), ",".join(s), baslik[:52]))
    # duzenli ifadelerde kacis karakteri bozulmasi (0x08 vb.) dogrudan aranir
    for ad, rx in TIP_KURAL:
        if any(ord(c) < 32 for c in rx.pattern):
            hata.append("KACIS BOZUK (kontrol karakteri) kural=%s repr=%r" % (ad, rx.pattern))
    if hata:
        print("KURAL SINAMASI DUSTU — betik calismayi REDDEDIYOR:")
        for h in hata:
            print("   " + h)
        raise SystemExit(1)
    print("kural sinamasi: %d baslik GECTI" % len(SINAMA))


def cek(cid, sayfa, deneme=4):
    """429'a dayanikli sayfa cekimi (ustel geri cekilme)."""
    bekle = 1.5
    for i in range(deneme):
        try:
            d = evren.get(BASE % (cid, sayfa), UA)
            kat = d.get("data", {}).get("catalogs", [{}])[0]
            return kat.get("articles", []) or []
        except Exception as e:
            if i == deneme - 1:
                raise
            if "429" in str(e) or "418" in str(e):
                time.sleep(bekle)
                bekle *= 2.5
            else:
                time.sleep(1.0)
    return []


def main():
    kural_sinamasi()
    gorulen, olaylar = set(), []
    for cid, kad in KATALOG.items():
        bitti, basarisiz = False, 0
        for pg in range(1, 61):
            if bitti:
                break
            try:
                art = cek(cid, pg)
            except Exception as e:
                basarisiz += 1
                print("  catalog %d sayfa %d HATA: %s" % (cid, pg, str(e)[:52]))
                continue
            if not art:
                break
            for a in art:
                ts = a.get("releaseDate")
                bas = (a.get("title") or "").strip()
                if not ts or not bas:
                    continue
                dt = datetime.datetime.utcfromtimestamp(ts / 1000.0)
                if dt < PENCERE_BAS:
                    bitti = True
                    continue
                anahtar = (ts, bas)
                if anahtar in gorulen:
                    continue
                gorulen.add(anahtar)
                tip = tip_bul(bas)
                olaylar.append({"ts": ts, "utc": dt.strftime("%Y-%m-%d %H:%M"),
                                "tip": tip, "semboller": sembol_bul(bas, tip),
                                "katalog": kad, "baslik": bas,
                                "kaynak_id": a.get("code") or a.get("id")})
            time.sleep(0.8)
        print("  catalog %d (%s) tarandi · basarisiz sayfa: %d" % (cid, kad, basarisiz))
        if basarisiz:
            print("  UYARI: bu katalogda %d sayfa alinamadi — kapsam EKSIK, hukumde belirt"
                  % basarisiz)

    olaylar.sort(key=lambda z: z["ts"])

    # --- KUMELEME: ayni sembolde 48 saat icinde ONCEKI birincil duyuru varsa,
    #     bu duyurunun ileri getirisi oncekinin kuyruguyla KARISIR -> isaretle.
    son_gorulen = {}
    PENCERE_MS = 48 * 3600 * 1000
    for o in olaylar:
        ilk = True
        if o["tip"] in BIRINCIL:
            for sm in o["semboller"]:
                onceki = son_gorulen.get(sm)
                if onceki is not None and o["ts"] - onceki <= PENCERE_MS:
                    ilk = False
            for sm in o["semboller"]:
                son_gorulen[sm] = o["ts"]
        o["birincil"] = o["tip"] in BIRINCIL
        o["kume_ilk"] = bool(ilk)

    with open(CIKTI, "w", encoding="utf-8") as f:
        for o in olaylar:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")

    print()
    print("OLAY KUTUGU — %s" % os.path.relpath(CIKTI, PROJE))
    print("=" * 84)
    print("toplam duyuru (pencere ici): %d" % len(olaylar))
    if olaylar:
        print("kapsam: %s .. %s" % (olaylar[0]["utc"], olaylar[-1]["utc"]))
    print()
    print("  %-18s %6s %8s %8s %-4s %s" % ("olay tipi", "N", "sembollu", "kume_ilk", "birn", "ornek"))
    print("  " + "-" * 80)
    c = collections.Counter(o["tip"] for o in olaylar)
    for tip, n in c.most_common():
        ss = [o for o in olaylar if o["tip"] == tip]
        ns = sum(1 for o in ss if o["semboller"])
        ki = sum(1 for o in ss if o["kume_ilk"] and o["semboller"])
        print("  %-18s %6d %8d %8d %-4s %s"
              % (tip, n, ns, ki, "BIR" if tip in BIRINCIL else "", ss[-1]["baslik"][:30]))
    print()
    tekil = set()
    for o in olaylar:
        tekil.update(o["semboller"])
    print("tekil sembol adedi: %d" % len(tekil))
    print("sembolu COZULEMEYEN duyuru: %d" % sum(1 for o in olaylar if not o["semboller"]))
    print()
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
