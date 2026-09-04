#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LONG_VETO HAKLI MI? — dort alt-tetigin ayri ayri sinanmasi.
On-kayit: ON_KAYIT_long_veto.md (commit 76d1f08, KOSUMDAN ONCE). Olcutler SABIT.

Kural (testbot.py:430):
    long_veto = pos<0.25 or chg24<=-40 or (chg24<0 and oi24>=15) or para_cikis

TASARIM: vetolanan kume yalniz 65 sembol-gun — cok kucuk. Bunun yerine her
alt-tetik TUM BOGA populasyonunda sinanir: "kosulu saglayanlar saglamayanlardan
gercekten daha mi kotu?" Veto tam olarak bunu varsayiyor.

🔑 Permutasyon duzeltmesi YOK ve GEREKMIYOR: hucreler benim aramamla degil,
   URETIMDEKI KURALIN kendisiyle belirlendi (arama degil, denetim).
🔴 BIRIM = SEMBOL-GUN · gun-kumeli t zorunlu · guc denetimi (MDE) zorunlu.
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
MUM = os.path.join(PROJE, "scratchpad", "aday_pencere_1h")
BAS = "2026-08-21"
SAAT_MS = 3600 * 1000
BLOWOFF = 40.0          # esikler.blowoff_chg24_pct
OI_ESIK = 5.0 * 3       # esikler.oi_hizli_degisim_pct * 3


def utc_ts(s):
    d = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M") - datetime.timedelta(hours=3)
    return int((d - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)


def sg_ort(w, alan):
    g = collections.defaultdict(list)
    for x in w:
        if x.get(alan) is not None:
            g[(x["sym"], x["_gun"])].append(x[alan])
    return [sum(v) / len(v) for v in g.values()], g


def gun_t(w, alan):
    """(ort, gun-kumeli t, sembol-gun N, gun N, MDE)"""
    _, g = sg_ort(w, alan)
    gun = collections.defaultdict(list)
    for (s, d), v in g.items():
        gun[d].append(sum(v) / len(v))
    d = [sum(v) / len(v) for v in gun.values()]
    sgn = len(g)
    if len(d) < 3:
        return (sum(d) / len(d) if d else None), None, sgn, len(d), None
    m, sd = sum(d) / len(d), statistics.stdev(d)
    se = sd / math.sqrt(len(d))
    return m, (m / se if se else None), sgn, len(d), (2.0 * se if se else None)


def iki_gun_t(a, b, alan):
    """iki kume arasi fark, GUN duzeyinde eslesmemis"""
    ma, _, na, ga, _ = gun_t(a, alan)
    mb, _, nb, gb, _ = gun_t(b, alan)
    if ma is None or mb is None:
        return None, None, None
    _, ga_ = sg_ort(a, alan)
    _, gb_ = sg_ort(b, alan)
    da = collections.defaultdict(list)
    db = collections.defaultdict(list)
    for (s, d), v in ga_.items():
        da[d].append(sum(v) / len(v))
    for (s, d), v in gb_.items():
        db[d].append(sum(v) / len(v))
    va = [sum(v) / len(v) for v in da.values()]
    vb = [sum(v) / len(v) for v in db.values()]
    if len(va) < 3 or len(vb) < 3:
        return (ma - mb), None, None
    se = math.sqrt(statistics.variance(va) / len(va) + statistics.variance(vb) / len(vb))
    return (ma - mb), ((ma - mb) / se if se else None), (2.0 * se if se else None)


def main():
    print("LONG_VETO HAKLI MI? — dort alt-tetik ayri ayri")
    print("on-kayit ON_KAYIT_long_veto.md (76d1f08) · olcutler SABIT")
    print("=" * 108)
    print("kural: pos<0.25 · chg24<=%.0f · (chg24<0 & oi24>=%.0f) · para_cikis"
          % (-BLOWOFF, OI_ESIK))

    mum = {}
    for fn in os.listdir(MUM):
        if fn.endswith(".json"):
            try:
                b = json.load(open(os.path.join(MUM, fn)))
            except Exception:
                continue
            if b:
                mum[fn[:-5]] = (b, {x[0]: j for j, x in enumerate(b)})

    R = []
    for l in open(ARSIV, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        ts = str(r.get("ts") or "")
        if ts[:10] < BAS or not str(r.get("rejim") or "").upper().startswith("BOGA"):
            continue
        s = r.get("sym")
        if not s or s not in mum:
            continue
        bar, ix = mum[s]
        t0 = utc_ts(ts)
        a = ix.get(t0 - (t0 % SAAT_MS))
        if a is None or bar[a][3] <= 0:
            continue
        e = bar[a][3]
        for h, ad in ((4, "r4"), (24, "r24")):
            j = ix.get(t0 - (t0 % SAAT_MS) + h * SAAT_MS)
            r[ad] = ((bar[j][3] - e) / e * 100.0) if j is not None else None
        if r.get("r4") is None:
            continue
        r["_gun"] = ts[:10]
        R.append(r)
    print("\nolculebilir BOGA satiri: %d · sembol %d · gun %d"
          % (len(R), len({x["sym"] for x in R}), len({x["_gun"] for x in R})))

    # ---------------------------------------------------- alt-tetik tanimlari
    def t1(x):
        return x.get("pos") is not None and x["pos"] < 0.25

    def t2(x):
        return (x.get("chg24") or 0) <= -BLOWOFF

    def t3(x):
        return (x.get("chg24") or 0) < 0 and (x.get("oi24") or 0) >= OI_ESIK

    TETIK = [("1 pos<0.25            (BIRINCIL)", t1),
             ("2 chg24<=-40          (ikincil)", t2),
             ("3 chg24<0 & oi24>=15  (ikincil)", t3)]

    for H in ("r4", "r24"):
        print("\n" + "=" * 108)
        print("UFUK %s — her alt-tetik: kosulu saglayan vs saglamayan" % ("4 saat" if H == "r4" else "24 saat"))
        print("-" * 108)
        print("  %-34s %6s %5s %11s %11s %10s %8s %9s"
              % ("alt-tetik", "sem-gun", "gun", "saglayan %", "digeri %", "fark", "gun-t", "MDE"))
        for ad, fn in TETIK:
            a = [x for x in R if fn(x)]
            b = [x for x in R if not fn(x)]
            ma, _, na, ga, _ = gun_t(a, H)
            mb, _, nb, gb, _ = gun_t(b, H)
            if ma is None or mb is None or na < 5:
                print("  %-34s %6s  (N yetersiz: %s)" % (ad, na, na))
                continue
            f, t, mde = iki_gun_t(a, b, H)
            print("  %-34s %6d %5d %+10.3f%% %+10.3f%% %+9.3f%% %8s %8s"
                  % (ad, na, ga, ma, mb, f,
                     ("%+.2f" % t) if t else "-", ("%.3f" % mde) if mde else "-"))

    # ---------------------------------------------------- BIRINCIL HUKUM
    print("\n" + "=" * 108)
    print("BIRINCIL HUKUM — alt-tetik 1 (pos<0.25), H=4 saat")
    print("=" * 108)
    a = [x for x in R if t1(x)]
    b = [x for x in R if not t1(x)]
    ma, _, na, ga, _ = gun_t(a, "r4")
    mb, _, nb, gb, _ = gun_t(b, "r4")
    f, t, mde = iki_gun_t(a, b, "r4")
    print("  pos<0.25   : %+.3f%%  (sembol-gun %d · gun %d)" % (ma, na, ga))
    print("  pos>=0.25  : %+.3f%%  (sembol-gun %d · gun %d)" % (mb, nb, gb))
    print("  fark       : %+.3f%%  ·  gun-t %s  ·  MDE %s"
          % (f, ("%+.2f" % t) if t else "-", ("%.3f" % mde) if mde else "-"))
    print()
    k1 = f < 0
    k2 = f > 0 and t is not None and t >= 2.0
    print("  K1  fark < 0 -> VETO HAKLI            : %s" % ("EVET" if k1 else "hayir"))
    print("  K2  fark > 0 ve t >= +2,0 -> HAKSIZ   : %s" % ("EVET" if k2 else "hayir"))
    print()
    if k2:
        print("  HUKUM: 🔴 VETO HAKSIZ — kestigi dilim ISTATISTIKSEL OLARAK daha iyi.")
    elif k1:
        print("  HUKUM: VETO HAKLI — kestigi dilim daha kotu. Dokunulmaz.")
    else:
        print("  HUKUM: VETO ETKISIZ — ne hakli ne haksiz (fark>0 ama t esigin altinda).")
        print("         Yani islem sayisini kisiyor, KALITE KATMIYOR.")
    if mde and abs(f) < mde:
        print("  GUC: |fark| %.3f < MDE %.3f -> 'etkisiz' DEGIL, 'GOREMIYORUZ'." % (abs(f), mde))
    elif mde:
        print("  GUC: |fark| %.3f > MDE %.3f -> orneklem bu buyuklugu gorebiliyor." % (abs(f), mde))

    # ---------------------------------------------------- vetolanan kumenin karnesi
    print("\n" + "=" * 108)
    print("EK 1) VETOLANAN KUMENIN KENDI KARNESI (kucuk N — betimleyici)")
    print("-" * 108)
    vet = [x for x in R if str(x.get("karar")) == "VETO:long_veto"]
    lng = [x for x in R if str(x.get("karar") or "").startswith("LONG")]
    for ad, w in (("VETOLANAN", vet), ("GECEN (LONG karari)", lng)):
        m, t, n, g, mde = gun_t(w, "r4")
        print("  %-22s sembol-gun %4d · gun %2d · ort %+7.3f%% · gun-t %s"
              % (ad, n, g, m if m is not None else 0, ("%+.2f" % t) if t else "-"))
    f2, t2v, mde2 = iki_gun_t(vet, lng, "r4")
    print("  fark (vetolanan - gecen): %+.3f%% · gun-t %s · MDE %s"
          % (f2, ("%+.2f" % t2v) if t2v else "-", ("%.3f" % mde2) if mde2 else "-"))

    # alt-tetik kirilimi (vetolanan icinde)
    print("\n  vetolanan kumenin alt-tetik kirilimi:")
    print("  %-24s %6s %5s %11s" % ("alt-tetik", "sem-gun", "gun", "ort %"))
    for ad, fn in TETIK:
        w = [x for x in vet if fn(x)]
        m, t, n, g, _ = gun_t(w, "r4")
        if n >= 3:
            print("  %-24s %6d %5d %+10.3f%%" % (ad.split("(")[0].strip(), n, g, m))
    art = [x for x in vet if not t1(x) and not t2(x) and not t3(x)]
    m, t, n, g, _ = gun_t(art, "r4")
    if n >= 3:
        print("  %-24s %6d %5d %+10.3f%%   (piyasa geneli — BETIMLEYICI)"
              % ("4 artik ~ para_cikis", n, g, m))

    # ---------------------------------------------------- karsi-olgu
    print("\n" + "=" * 108)
    print("EK 2) KARSI-OLGU — bilesen kaldirilsa LONG havuzu ne olurdu?")
    print("-" * 108)
    m0, _, n0, g0, _ = gun_t(lng, "r4")
    print("  bugunku LONG havuzu            : %+7.3f%%  (sembol-gun %d)" % (m0, n0))
    for ad, fn in TETIK:
        ek = [x for x in vet if fn(x)]
        yeni = lng + ek
        m1, _, n1, g1, _ = gun_t(yeni, "r4")
        print("  + %-28s : %+7.3f%%  (sembol-gun %d · %+.3f puan)"
              % (ad.split("(")[0].strip(), m1, n1, m1 - m0))
    yeni = lng + vet
    m1, _, n1, g1, _ = gun_t(yeni, "r4")
    print("  + TUM veto kaldirilsa          : %+7.3f%%  (sembol-gun %d · %+.3f puan)"
          % (m1, n1, m1 - m0))
    print("\n  ⚠️ Karsi-olgu HAM getiridir; mekanik (stop/hedef) ve portfoy (8 slot)")
    print("     kisitlari YOK SAYILIYOR. Kod degisikligi onerisi DEGILDIR.")

    print("\n" + "=" * 108)
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
