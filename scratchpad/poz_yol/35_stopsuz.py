#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STOP YOK, SADECE SURE — celiskiyi coz.

CELISKI:
  32_rastgele_kontrol.py : rastgele barda cikmak +1,789 puan kazandiriyor
  28_cikis_taramasi.py   : 46 stop/hedef varyantinin hicbiri iki kumede arti degil
Rastgele cikis STOP'A UGRAMIYOR; izgara varyantlarinin HEPSINDE stop var.
Hipotez: kenari yiyen stop'un kendisi.

BU BETIK: ayni girisler, ayni 5 dk veri, UC KOL:
   A) SADECE SURE      (stop YOK, hedef YOK) — T saat sonra kapanista cik
   B) SURE + STOP      (ayni T, stop %X)
   C) SADECE STOP      (sure 72sa, stop %X)   -> botun mevcut yapisi

⚠️ STOPSUZ = LIKIDASYON RISKI. Kaldiracli pozisyonda aleyhte hareket
   ~1/kaldirac'i asinca pozisyon OLUR. Bu SIMULE EDILIR (defterdeki gercek
   kaldirac kullanilir), yoksa stopsuz kol sahte iyi gorunur.

OLCU: islem basi NET YUZDE (maliyet+fonlama dahil). Dolar/boyut sorusu
   ayri; yuzde karsilastirmasi boyutlandirmadan bagimsiz.

Iki rejim kumesi ayri (bolen 2026-08-19 18:15).
HUKUM YAZILMAZ. SALT OKUMA.
"""
import os, sys, json, datetime, collections, bisect, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
PROJE = os.path.dirname(SCRATCH)
SERI = os.path.join(SCRATCH, "perp_seri")
sys.path.insert(0, SCRATCH)
import olcum_ortak as oo                                        # noqa: E402

F = "%Y-%m-%d %H:%M:%S"
BOLEN = datetime.datetime(2026, 8, 19, 18, 15)
BAS = datetime.datetime(2026, 8, 11)
SURELER = [1, 2, 4, 8, 24, 72]          # saat
STOPLAR = [3.0, 5.0, 8.0, None]         # None = stop YOK


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
        out.append({"sym": v[0]["sym"], "yon": v[0]["yon"], "gir": gir,
                    "kald": v[-1].get("kaldirac") or 3,
                    "gercek": sum(t.get("sonuc_usdt") or 0 for t in v)})
    with open(os.path.join(PROJE, "testbot_state.json"), encoding="utf-8") as f:
        for p in json.load(f)["acik_pozisyonlar"]:
            out.append({"sym": p["sym"], "yon": p["yon"],
                        "gir": datetime.datetime.strptime(p["giris_ts"], F),
                        "kald": p.get("kaldirac") or 3, "gercek": None})
    return [p for p in out if p["gir"] >= BAS]


_M, _FO = {}, {}


def mum(sym):
    if sym not in _M:
        y = os.path.join(SERI, "%s_kline.json" % sym)
        try:
            with open(y, encoding="utf-8") as f:
                _M[sym] = sorted(json.load(f), key=lambda x: x["t"])
        except Exception:
            _M[sym] = []
    return _M[sym]


def fon(sym, t0, t1, yon):
    if sym not in _FO:
        y = os.path.join(SCRATCH, "funding_gecmis", "%s.json" % sym)
        try:
            with open(y, encoding="utf-8") as f:
                d = json.load(f)
            _FO[sym] = ([x["t"] for x in d], [x["r"] for x in d])
        except Exception:
            _FO[sym] = ([], [])
    ft, fr = _FO[sym]
    if not ft:
        return 0.0
    i, j = bisect.bisect_right(ft, t0), bisect.bisect_right(ft, t1)
    s = sum(fr[k] for k in range(i, j))
    return s if yon == "SHORT" else -s


def oynat(p, sure_sa, stop_pct):
    """-> (net_pct, tip) | None.  stop_pct None ise stop YOK (likidasyon var)."""
    b = mum(p["sym"])
    if len(b) < 10:
        return None
    t0 = int(p["gir"].timestamp() * 1000)
    ic = [x for x in b if x["t"] >= t0]
    if len(ic) < 3:
        return None
    ref = ic[0]["o"]
    if ref <= 0:
        return None
    yon = p["yon"]
    # LIKIDASYON esigi: aleyhte ~1/kaldirac (bakim marji ihmal, iyimser)
    liq = 100.0 / max(1, p["kald"])
    sp = None
    if stop_pct is not None:
        sp = ref * (1 + stop_pct / 100) if yon == "SHORT" else ref * (1 - stop_pct / 100)
    sinir = t0 + sure_sa * 3600000
    cj, tip, ham = ic[-1], "SURE", None
    for x in ic:
        if x["t"] > sinir:
            cj, tip = x, "SURE"
            ham = ((ref - x["o"]) if yon == "SHORT" else (x["o"] - ref)) / ref * 100
            break
        alh = ((x["h"] - ref) if yon == "SHORT" else (ref - x["l"])) / ref * 100
        if alh >= liq:
            cj, tip, ham = x, "LIQ", -liq
            break
        if sp is not None and ((x["h"] >= sp) if yon == "SHORT" else (x["l"] <= sp)):
            cj, tip, ham = x, "STOP", -stop_pct
            break
    if ham is None:
        ham = ((ref - cj["c"]) if yon == "SHORT" else (cj["c"] - ref)) / ref * 100
        tip = "SURE"
    return ham - oo.MALIYET + fon(p["sym"], t0, cj["t"], yon), tip


def tablo(poz, ad):
    print("\n" + "=" * 104)
    print("%s   N=%d" % (ad, len(poz)))
    print("=" * 104)
    print("islem basi NET YUZDE (maliyet+fonlama dahil) · parantez: stop%% / liq%%")
    bas = "%-8s" % "sure"
    for s in STOPLAR:
        bas += "%22s" % ("stop %%%.0f" % s if s else "STOP YOK")
    print(bas)
    print("-" * 96)
    for u in SURELER:
        sat = "%-8s" % ("%dsa" % u)
        for s in STOPLAR:
            r = [oynat(p, u, s) for p in poz]
            r = [x for x in r if x]
            if len(r) < len(poz) * 0.6:
                sat += "%22s" % "-"
                continue
            net = [x[0] for x in r]
            tip = collections.Counter(x[1] for x in r)
            sat += "%22s" % ("%+.3f (%d%%/%d%%)"
                             % (sx.mean(net),
                                round(100 * tip.get("STOP", 0) / len(r)),
                                round(100 * tip.get("LIQ", 0) / len(r))))
        print(sat)


if __name__ == "__main__":
    poz = pozisyonlar()
    a = [p for p in poz if p["gir"] < BOLEN]
    b = [p for p in poz if p["gir"] >= BOLEN]
    print("STOP YOK / SADECE SURE — celiski testi")
    print("likidasyon SIMULE EDILIYOR (gercek kaldirac, ~1/kald esigi)")
    tablo(a, "A) NOTR/AYI  08-11 .. 08-19 18:15")
    tablo(b, "B) BOGA      08-19 18:15 .. simdi")
    print("\nHUKUM YAZILMADI. bot dosyalarina yazim: YOK")
