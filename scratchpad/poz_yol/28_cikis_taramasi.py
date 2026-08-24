#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CIKIS TARAMASI — YALNIZ BIZIM VERI, iki rejim kumesi ayri.

KULLANICI (2026-08-21): "bu olcumu sadece bizim verilerle yap, 11-19 arasi ve
19'dan bugune, 2 kumeye ayir: biri notr-ayi obüru boga donemi."

GIRISLER  : botun KENDI actigi pozisyonlar (testbot_islemler + acik pozisyonlar)
FIYAT YOLU: scratchpad/perp_seri/ 5 dakikalik mumlar (kendi cektigimiz)
2 yillik Binance kline seti KULLANILMADI.

KUMELER (bolen: boga kirilmasi 2026-08-19 18:15):
   A) NOTR/AYI  2026-08-11 .. 08-19 18:15   111 pozisyon
   B) BOGA      2026-08-19 18:15 .. simdi    48 pozisyon

RISK SABIT: her varyantta islem basina ayni dolar riske edilir (75 $),
   notional = 75 / stop%. Boylece dar ve genis stop ADIL kiyaslanir.
   (05_mekanik.py'de ayni ilke kullanildi.)

MALIYET + FONLAMA dahil.

⚠️ BOTUN ORIJINAL STOPU DEFTERDE YOK -> mutlak izgara kullaniliyor
   ("stop %X olsaydi"). 05_mekanik.py'nin gerekcesiyle ayni.

HUKUM YAZILMAZ — sayi uretilir.
SALT OKUMA.
"""
import os, sys, json, datetime, collections, bisect

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
PROJE = os.path.dirname(SCRATCH)
SERI = os.path.join(SCRATCH, "perp_seri")
sys.path.insert(0, SCRATCH)
import olcum_ortak as oo                                        # noqa: E402

F = "%Y-%m-%d %H:%M:%S"
BOLEN = datetime.datetime(2026, 8, 19, 18, 15)
BAS = datetime.datetime(2026, 8, 11)
RISK = 75.0
UFUK_SA = 72
STOPLAR = [2, 3, 4, 5, 6, 8]
HEDEFLER = [3, 5, 7, 10, 15, None]


def pozisyonlar():
    g = collections.defaultdict(list)
    with open(os.path.join(PROJE, "testbot_islemler.jsonl"), encoding="utf-8") as f:
        for s in f:
            if s.strip():
                x = json.loads(s)
                g[x["id"]].append(x)
    out = []
    for i, v in g.items():
        v.sort(key=lambda z: z["ts"])
        tut = max(t.get("tutma_saat") or 0 for t in v)
        gir = datetime.datetime.strptime(v[-1]["ts"], F) - datetime.timedelta(hours=tut)
        out.append({"id": i, "sym": v[0]["sym"], "yon": v[0]["yon"], "gir": gir,
                    "gercek": sum(t.get("sonuc_usdt") or 0 for t in v)})
    with open(os.path.join(PROJE, "testbot_state.json"), encoding="utf-8") as f:
        for p in json.load(f)["acik_pozisyonlar"]:
            out.append({"id": p["id"], "sym": p["sym"], "yon": p["yon"],
                        "gir": datetime.datetime.strptime(p["giris_ts"], F), "gercek": None})
    return [p for p in out if p["gir"] >= BAS]


_ONB = {}


def mumlar(sym):
    if sym in _ONB:
        return _ONB[sym]
    y = os.path.join(SERI, "%s_kline.json" % sym)
    d = []
    if os.path.exists(y):
        try:
            with open(y, encoding="utf-8") as f:
                d = sorted(json.load(f), key=lambda x: x["t"])
        except Exception:
            d = []
    _ONB[sym] = d
    return d


_FON = {}


def fonlama(sym):
    if sym in _FON:
        return _FON[sym]
    y = os.path.join(SCRATCH, "funding_gecmis", "%s.json" % sym)
    d = []
    if os.path.exists(y):
        try:
            with open(y, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            d = []
    _FON[sym] = ([x["t"] for x in d], [x["r"] for x in d])
    return _FON[sym]


def fon_pct(sym, t0, t1, yon):
    ft, fr = fonlama(sym)
    if not ft:
        return 0.0
    i, j = bisect.bisect_right(ft, t0), bisect.bisect_right(ft, t1)
    s = sum(fr[k] for k in range(i, j))
    return s if yon == "SHORT" else -s


def oynat(p, stop_pct, hedef_pct=None, ufuk_sa=UFUK_SA, yol_bar=None):
    """-> net yuzde | None.  yol_bar: N barda yeni uc yoksa CIK (yol tabanli)."""
    b = mumlar(p["sym"])
    if len(b) < 20:
        return None
    t0 = int(p["gir"].timestamp() * 1000)
    ic = [x for x in b if x["t"] >= t0]
    if len(ic) < 4:
        return None
    ref = ic[0]["o"]
    if ref <= 0:
        return None
    yon = p["yon"]
    sp = ref * (1 + stop_pct / 100) if yon == "SHORT" else ref * (1 - stop_pct / 100)
    hp = None
    if hedef_pct:
        hp = ref * (1 - hedef_pct / 100) if yon == "SHORT" else ref * (1 + hedef_pct / 100)
    sinir = t0 + ufuk_sa * 3600000
    en_iyi = ref
    son_uc = 0
    cj, ham = ic[-1], None
    for n, x in enumerate(ic):
        if x["t"] > sinir:
            cj = x
            ham = ((ref - x["o"]) if yon == "SHORT" else (x["o"] - ref)) / ref * 100
            break
        vs = (x["h"] >= sp) if yon == "SHORT" else (x["l"] <= sp)
        vh = hp is not None and ((x["l"] <= hp) if yon == "SHORT" else (x["h"] >= hp))
        if vs:
            cj, ham = x, -stop_pct
            break
        if vh:
            cj, ham = x, hedef_pct
            break
        if yol_bar:
            yeni = (x["l"] < en_iyi) if yon == "SHORT" else (x["h"] > en_iyi)
            if yeni:
                en_iyi = x["l"] if yon == "SHORT" else x["h"]
                son_uc = n
            elif n - son_uc >= yol_bar:
                cj = x
                ham = ((ref - x["c"]) if yon == "SHORT" else (x["c"] - ref)) / ref * 100
                break
    if ham is None:
        ham = ((ref - cj["c"]) if yon == "SHORT" else (cj["c"] - ref)) / ref * 100
    return ham - oo.MALIYET + fon_pct(p["sym"], t0, cj["t"], yon)


def dolar(net_pct, stop_pct):
    return net_pct * (RISK / (stop_pct / 100)) / 100


def kume(poz, ad):
    print("\n" + "=" * 104)
    print("%s   N=%d pozisyon" % (ad, len(poz)))
    if poz and any(p["gercek"] is not None for p in poz):
        gk = [p["gercek"] for p in poz if p["gercek"] is not None]
        print("botun GERCEK sonucu (kapanmis %d): %+.2f $" % (len(gk), sum(gk)))
    print("=" * 104)
    print("IZGARA — risk her hucrede SABIT %.0f $/islem, ufuk %d saat" % (RISK, UFUK_SA))
    print("%-9s" % "stop\\hed" + "".join("%13s" % (("%%%d" % h) if h else "hedefsiz") for h in HEDEFLER))
    en = []
    for s in STOPLAR:
        sat = "%-9s" % ("%%%d" % s)
        for h in HEDEFLER:
            v = [oynat(p, s, h) for p in poz]
            v = [x for x in v if x is not None]
            if len(v) < len(poz) * 0.6:
                sat += "%13s" % "-"
                continue
            d = sum(dolar(x, s) for x in v)
            en.append((d, "stop%%%d/hedef %s" % (s, h or "yok"), len(v)))
            sat += "%13s" % ("%+.0f" % d)
        print(sat)
    print("\nUFUK taramasi (stop %3, hedef %10):")
    for u in (6, 12, 24, 48, 72):
        v = [oynat(p, 3, 10, u) for p in poz]
        v = [x for x in v if x is not None]
        if v:
            d = sum(dolar(x, 3) for x in v)
            en.append((d, "ufuk %dsa" % u, len(v)))
            print("   %2d saat: %+9.0f $   (N=%d)" % (u, d, len(v)))
    print("\nYOL TABANLI cikis (stop %3, hedefsiz) — N barda yeni uc yoksa CIK:")
    for yb in (3, 6, 12, 24, 48):
        v = [oynat(p, 3, None, UFUK_SA, yb) for p in poz]
        v = [x for x in v if x is not None]
        if v:
            d = sum(dolar(x, 3) for x in v)
            en.append((d, "yol %d bar (%d dk)" % (yb, yb * 5), len(v)))
            print("   %2d bar (%3d dk): %+9.0f $   (N=%d)" % (yb, yb * 5, d, len(v)))
    en.sort(reverse=True)
    print("\n  EN IYI 5:")
    for d, ad2, n in en[:5]:
        print("     %-26s %+9.0f $  (N=%d)" % (ad2, d, n))
    print("  EN KOTU 1: %-26s %+9.0f $" % (en[-1][1], en[-1][0]))
    return dict((a, d) for d, a, _ in en)


if __name__ == "__main__":
    poz = pozisyonlar()
    a = [p for p in poz if p["gir"] < BOLEN]
    b = [p for p in poz if p["gir"] >= BOLEN]
    print("BIZIM VERI — botun kendi girisleri, perp_seri 5 dk mumlariyla oynatildi")
    print("bolen: %s (boga kirilmasi)" % BOLEN)
    ra = kume(a, "A) NOTR / AYI   2026-08-11 .. 08-19 18:15")
    rb = kume(b, "B) BOGA         2026-08-19 18:15 .. simdi")
    print("\n" + "=" * 104)
    print("IKI KUMEDE DE EN IYI 8 VARYANT (siralama A'ya gore)")
    print("=" * 104)
    print("%-28s %14s %14s   %s" % ("varyant", "A (notr/ayi)", "B (boga)", "ikisi de arti?"))
    for k in sorted(ra, key=lambda z: -ra[z])[:8]:
        va, vb = ra[k], rb.get(k)
        print("%-28s %+14.0f %14s   %s"
              % (k, va, "%+.0f" % vb if vb is not None else "-",
                 "EVET" if (vb is not None and va > 0 and vb > 0) else "hayir"))
    print("\nHUKUM YAZILMADI. bot dosyalarina yazim: YOK")
