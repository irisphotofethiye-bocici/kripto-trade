#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOGA LONG HAM — GUN KUMELI saglamlik denetimi (boga_long_ham.py EKI).

NEDEN: on-kayit birimi SEMBOL-GUN idi ve hukum ona gore verildi (K1 GECTI,
t=-2,06). Ama sembol-gunler ayni gun icinde BAGIMSIZ DEGIL: dusus gununde
butun altlar birlikte duser. Bu, t'yi sisirir.

Bu betik OLCUT DEGISTIRMEZ ve hukmu yeniden yazmaz. On-kayitli hukmun
NE KADAR SAGLAM oldugunu gosterir:
  - gun duzeyinde toplama (her gun = TEK gozlem)
  - gun bazinda dagilim (kac gun eksi, en kotu gunler ne kadar tasiyor)
  - en kotu gunler cikarilinca ne kaliyor

Onbellekten okur (scratchpad/aday_pencere_1h/), YENI ag cagrisi YAPMAZ.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, math, datetime, statistics, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARSIV = os.path.join(PROJE, "testbot_aday_arsiv.jsonl")
ONBELLEK = os.path.join(PROJE, "scratchpad", "aday_pencere_1h")
YEREL_FARK = 3
SAAT_MS = 3600 * 1000
SKOR_ESIK, POS_ESIK = 45.0, 0.85
H_SAAT = [1, 4, 12, 24]
BIRINCIL_H = 4


def utc_ts(s):
    d = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M") - datetime.timedelta(hours=YEREL_FARK)
    return int((d - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)


def t_ist(v):
    if len(v) < 3:
        return (sum(v) / len(v) if v else None), None, len(v), None
    m, sd = sum(v) / len(v), statistics.stdev(v)
    se = sd / math.sqrt(len(v))
    return m, (m / se if se else None), len(v), (2.0 * se if se else None)


def main():
    print("BOGA LONG HAM — GUN KUMELI SAGLAMLIK DENETIMI")
    print("olcut DEGISTIRILMEDI; on-kayitli hukum (sembol-gun, K1 GECTI t=-2,06)")
    print("ne kadar saglam, onu gosterir.")
    print("=" * 100)

    mum = {}
    for fn in os.listdir(ONBELLEK):
        if fn.endswith(".json"):
            try:
                b = json.load(open(os.path.join(ONBELLEK, fn)))
            except Exception:
                continue
            if b:
                mum[fn[:-5]] = (b, {x[0]: j for j, x in enumerate(b)})

    satir = []
    for l in open(ARSIV, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        if str(r.get("rejim") or "").upper().startswith("BOGA") and r.get("sym") and r.get("ts"):
            satir.append(r)

    def ret(r, h):
        m = mum.get(r["sym"])
        if not m:
            return None
        bar, ix = m
        t0 = utc_ts(r["ts"])
        a = ix.get(t0 - (t0 % SAAT_MS))
        b = ix.get(t0 - (t0 % SAAT_MS) + h * SAAT_MS)
        if a is None or b is None:
            return None
        e, x = bar[a][3], bar[b][3]
        return ((x - e) / e * 100.0) if e > 0 else None

    def kapi_mi(r):
        return ((r.get("score") or 0) >= SKOR_ESIK
                and str(r.get("smart")) != "SHORT"
                and (r.get("pos") is None or float(r.get("pos")) <= POS_ESIK))

    def topla(sec, h):
        """-> (sembol-gun listesi, gun->ortalama sozlugu)"""
        sg = collections.defaultdict(list)
        for r in satir:
            if not sec(r):
                continue
            v = ret(r, h)
            if v is not None:
                sg[(r["sym"], str(r["ts"])[:10])].append(v)
        sgo = {k: sum(v) / len(v) for k, v in sg.items()}
        gun = collections.defaultdict(list)
        for (s, g), v in sgo.items():
            gun[g].append(v)
        return list(sgo.values()), {g: sum(v) / len(v) for g, v in gun.items()}, \
            {g: len(v) for g, v in gun.items()}

    print("\n1) IKI BIRIM YAN YANA — ayni sayi, farkli bagimsizlik varsayimi")
    print("-" * 100)
    print("  %-8s %-9s %10s %8s %8s %10s %8s %8s"
          % ("kol", "ufuk", "sem-gun", "sg-t", "gun", "gun ort", "gun-t", "MDE(gun)"))
    for ad, sec in (("KAPI", kapi_mi), ("TABAN", lambda r: True)):
        for h in H_SAAT:
            sgv, gunort, gunn = topla(sec, h)
            if len(sgv) < 3:
                continue
            m1, t1, n1, _ = t_ist(sgv)
            gv = list(gunort.values())
            m2, t2, n2, mde2 = t_ist(gv)
            print("  %-8s %-9s %10d %8s %8d %+9.3f%% %8s %8s"
                  % (ad, "%d saat" % h, n1, ("%+.2f" % t1) if t1 else "-",
                     n2, m2, ("%+.2f" % t2) if t2 else "-",
                     ("%.3f" % mde2) if mde2 else "-"))

    # ------------------------------------------------ gun gun dokum (birincil)
    print("\n" + "=" * 100)
    print("2) GUN GUN — birincil hucre (KAPI, H=%d saat)" % BIRINCIL_H)
    print("-" * 100)
    sgv, gunort, gunn = topla(kapi_mi, BIRINCIL_H)
    _, _, _, _ = t_ist(sgv)
    print("  %-12s %8s %11s" % ("gun", "sem-gun", "ort %"))
    for g in sorted(gunort):
        print("  %-12s %8d %+10.3f%%" % (g, gunn[g], gunort[g]))
    gv = [gunort[g] for g in sorted(gunort)]
    eksi = sum(1 for x in gv if x < 0)
    print("  " + "-" * 34)
    print("  gun sayisi %d · EKSI gun %d (%%%.0f)" % (len(gv), eksi, 100.0 * eksi / len(gv)))

    # ------------------------------------------------ dayaniklilik
    print("\n" + "=" * 100)
    print("3) DAYANIKLILIK — en kotu gunler cikarilinca")
    print("-" * 100)
    s = sorted(gv)
    for k in (0, 1, 2, 3):
        kalan = s[k:]
        if len(kalan) < 3:
            continue
        m, t, n, _ = t_ist(kalan)
        print("  en kotu %d gun cikarildi -> gun %2d · ort %+.3f%% · gun-t %s"
              % (k, n, m, ("%+.2f" % t) if t else "-"))

    print("\n" + "=" * 100)
    print("YORUM KURALI (on-kayit degistirilmez):")
    print("  gun-t da <= -2,0 ise  -> hukum SAGLAM")
    print("  gun-t -1,0 .. -2,0    -> isaret ayni ama GUVEN ZAYIF, oyle yazilir")
    print("  gun-t > -1,0          -> hukum TEK BASINA TASIMAZ; sembol-gun t sismis")
    print("\nbot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
